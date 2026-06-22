#!/usr/bin/env python3
"""Compile a /agy:notebook folder's per-document `.facts.json` sidecars into one queryable
SQLite knowledge base (`notebook.db`). Pure stdlib (sqlite3 + re + json). No Node, no deps.

Usage:  python notebook_db.py <OUTDIR> [<OBJETIVO>]

OUTDIR is the notebook output folder (docs/agy/notebook/<slug>/) that holds `_manifest.tsv`,
the `NN-slug.resumen.md` summaries and their `NN-slug.facts.json` sidecars.

Tolerant + idempotent: a malformed/missing sidecar never crashes the build — it falls back to the
`.md` frontmatter and is logged to `_facts_errors.log`. Re-running only rebuilds changed docs
(cache_key = size:mtime:objhash, same key the sweep uses). Monetary values are integer cents.
"""
import sys, os, re, json, sqlite3, glob

SCHEMA_VER = 1

DDL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS documents(
  id INTEGER PRIMARY KEY,
  basename TEXT NOT NULL UNIQUE,          -- summary relpath stem: unique citation handle
  nn TEXT, slug TEXT, doc_name TEXT,
  source_abspath TEXT, tipo TEXT, doc_ref TEXT, fecha TEXT, emisor TEXT,
  relevancia INTEGER, estado TEXT DEFAULT 'ok',
  summary_md_path TEXT, facts_json_path TEXT, cache_key TEXT);
CREATE TABLE IF NOT EXISTS chunks(
  id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  ord INTEGER, seccion TEXT, texto TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS entities(
  id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  clase TEXT NOT NULL CHECK(clase IN ('persona','organizacion','monto','fecha','referencia')),
  ent_key TEXT NOT NULL, valor TEXT NOT NULL, detalle TEXT,
  monto_cents INTEGER, fecha_iso TEXT, quote TEXT);
CREATE INDEX IF NOT EXISTS ix_ent_clave ON entities(clase, ent_key);
CREATE INDEX IF NOT EXISTS ix_ent_doc ON entities(doc_id);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  fecha_iso TEXT NOT NULL, hecho TEXT NOT NULL, monto_cents INTEGER, quote TEXT);
CREATE INDEX IF NOT EXISTS ix_ev_fecha ON events(fecha_iso);
CREATE TABLE IF NOT EXISTS relations(
  id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  sujeto TEXT NOT NULL, predicado TEXT NOT NULL, objeto TEXT NOT NULL, quote TEXT);
CREATE TABLE IF NOT EXISTS citations(
  id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  tabla TEXT NOT NULL, fila_id INTEGER NOT NULL, cita TEXT NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
  texto, content='chunks', content_rowid='id', tokenize='unicode61 remove_diacritics 2');
"""

VIEWS = """
DROP VIEW IF EXISTS v_personas;
CREATE VIEW v_personas AS
  SELECT ent_key AS id, MIN(valor) AS nombre, COUNT(DISTINCT e.doc_id) AS n_docs,
         GROUP_CONCAT(DISTINCT d.doc_ref) AS docs
  FROM entities e JOIN documents d ON d.id=e.doc_id
  WHERE e.clase='persona' GROUP BY ent_key;
DROP VIEW IF EXISTS v_montos;
CREATE VIEW v_montos AS
  SELECT detalle AS concepto, COUNT(*) AS n, SUM(monto_cents) AS total_cents,
         printf('$%.2f', SUM(monto_cents)/100.0) AS total
  FROM entities WHERE clase='monto' AND monto_cents IS NOT NULL GROUP BY detalle;
DROP VIEW IF EXISTS v_organizaciones;
CREATE VIEW v_organizaciones AS
  SELECT ent_key AS org_key, MIN(valor) AS nombre, COUNT(DISTINCT doc_id) AS n_docs
  FROM entities WHERE clase='organizacion' GROUP BY ent_key;
DROP VIEW IF EXISTS v_referencias;
CREATE VIEW v_referencias AS
  SELECT ent_key AS ref_key, MIN(valor) AS valor, MIN(detalle) AS detalle, COUNT(DISTINCT doc_id) AS n_docs
  FROM entities WHERE clase='referencia' GROUP BY ent_key;
DROP VIEW IF EXISTS v_fechas;
CREATE VIEW v_fechas AS
  SELECT ev.fecha_iso, ev.hecho, d.doc_ref, d.basename
  FROM events ev JOIN documents d ON d.id=ev.doc_id WHERE ev.fecha_iso<>'' ORDER BY ev.fecha_iso;
DROP VIEW IF EXISTS v_timeline;
CREATE VIEW v_timeline AS
  SELECT ev.fecha_iso, ev.hecho, ev.monto_cents, d.doc_ref, d.basename, ev.quote
  FROM events ev JOIN documents d ON d.id=ev.doc_id ORDER BY ev.fecha_iso;
"""


def loads_tolerant(s):
    """Parse JSON; if malformed, return the largest balanced {...} object that parses."""
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s); s = re.sub(r"\n?```$", "", s)
    try:
        return json.loads(s)
    except Exception:
        pass
    best = None
    for st in (i for i, c in enumerate(s) if c == "{"):
        depth = 0
        for j in range(st, len(s)):
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
                if depth == 0:
                    cand = s[st:j + 1]
                    try:
                        o = json.loads(cand)
                        if best is None or len(cand) > best[1]:
                            best = (o, len(cand))
                    except Exception:
                        pass
                    break
    return best[0] if best else None


def to_cents(m):
    if isinstance(m, dict) and m.get("importe_cents") is not None:
        try:
            return int(m["importe_cents"])
        except Exception:
            pass
    raw = str(m.get("importe", "") if isinstance(m, dict) else m)
    s = re.sub(r"[^\d,.\-]", "", raw)
    if not s:
        return None
    if "," in s:                       # AR format: '.' thousands, ',' decimals
        s = s.replace(".", "").replace(",", ".")
    try:
        return int(round(float(s) * 100))
    except Exception:
        return None


def aslist(lst, strkey):
    """Coerce a facts array into a list of dicts (agy sometimes emits bare strings)."""
    out = []
    for x in (lst or []):
        if isinstance(x, dict):
            out.append(x)
        elif isinstance(x, str) and x.strip():
            out.append({strkey: x.strip()})
    return out


def as_int(x, default=0):
    if isinstance(x, bool):
        return default
    if isinstance(x, (int, float)):
        return int(x)
    m = re.search(r"-?\d+", str(x or ""))
    return int(m.group(0)) if m else default


def iso(x):
    x = (x or "").strip()
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", x)
    return m.group(0) if m else (x if re.match(r"^\d{4}-\d{2}-\d{2}$", x) else "")


def dni_key(p):
    d = re.sub(r"\D", "", str(p.get("dni") or p.get("cuil") or ""))
    if len(d) == 11:                   # CUIL -> middle DNI
        d = d[2:10]
    return d or (p.get("nombre", "").strip().lower())


def ex_key(n):
    return re.sub(r"\s+", "", str(n or "").upper())


def cue_key(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[:7] if d else (s or "").strip().lower()


def frontmatter(md_path):
    fm = {}
    try:
        t = open(md_path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return fm
    m = re.match(r"\s*---\s*\n(.*?)\n---", t, re.S)
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip()
    return fm


def manifest_members(outdir):
    """Yield (summary_relpath, cache_key) for every member, expanding group pipe-lists."""
    mpath = os.path.join(outdir, "_manifest.tsv")
    if not os.path.exists(mpath):
        return
    for ln in open(mpath, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if len(c) < 6:
            continue
        for s, k in zip(c[4].split("|"), c[5].split("|")):
            yield s, k


def main():
    outdir = sys.argv[1]
    objetivo = sys.argv[2] if len(sys.argv) > 2 else ""
    db = os.path.join(outdir, "notebook.db")
    errlog = open(os.path.join(outdir, "_facts_errors.log"), "w", encoding="utf-8")
    con = sqlite3.connect(db)
    con.executescript(DDL)
    cur = con.cursor()
    # existing cache_keys for incremental skip
    have = {r[0]: r[1] for r in cur.execute("SELECT basename, cache_key FROM documents")}

    n_doc = n_ent = n_ev = n_err = n_skip = 0
    for summ, key in manifest_members(outdir):
        basename = re.sub(r"\.resumen\.md$", "", summ)
        if have.get(basename) == key:                 # unchanged -> skip
            n_skip += 1
            continue
        md_path = os.path.join(outdir, summ)
        facts_path = os.path.join(outdir, re.sub(r"\.resumen\.md$", ".facts.json", summ))
        facts = None
        if os.path.exists(facts_path):
            try:
                facts = loads_tolerant(open(facts_path, encoding="utf-8", errors="ignore").read())
            except Exception:
                facts = None
        fm = frontmatter(md_path)
        estado = "no_procesado" if (fm.get("estado") == "no_procesado") else "ok"
        if facts is None:
            n_err += 1
            errlog.write(f"{summ}\t{'missing' if not os.path.exists(facts_path) else 'invalid_json'}\n")
            facts = {}                                  # fall back to frontmatter only
        # UPSERT by basename
        cur.execute("DELETE FROM documents WHERE basename=?", (basename,))
        cur.execute(
            "INSERT INTO documents(basename,nn,slug,doc_name,source_abspath,tipo,doc_ref,fecha,emisor,relevancia,estado,summary_md_path,facts_json_path,cache_key) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (basename, basename.split("-", 1)[0], basename, facts.get("doc") or fm.get("doc", ""),
             "", facts.get("tipo") or fm.get("tipo", ""), facts.get("doc_ref") or fm.get("doc_ref", ""),
             iso(facts.get("fecha") or fm.get("fecha", "")), facts.get("emisor") or fm.get("emisor", ""),
             as_int(facts.get("relevancia", fm.get("relevancia", 0))), estado, md_path, facts_path, key))
        did = cur.lastrowid
        n_doc += 1

        def cite(tabla, fila_id, q):
            cur.execute("INSERT INTO citations(doc_id,tabla,fila_id,cita) VALUES(?,?,?,?)",
                        (did, tabla, fila_id, q or ""))

        # chunks
        ordn = 0
        for sec, val in (("sintesis", facts.get("sintesis", "")),):
            if val:
                ordn += 1
                cur.execute("INSERT INTO chunks(doc_id,ord,seccion,texto) VALUES(?,?,?,?)", (did, ordn, sec, val))
        for dk in (facts.get("datos_clave") or []):
            ordn += 1
            cur.execute("INSERT INTO chunks(doc_id,ord,seccion,texto) VALUES(?,?,?,?)", (did, ordn, "datos_clave", str(dk)))
        # entities — general taxonomy: persona | organizacion | monto | fecha | referencia.
        # New facts keys (personas/organizaciones/montos/fechas/referencias) plus legacy aliases are merged.
        for p in aslist(facts.get("personas"), "nombre"):
            cur.execute("INSERT INTO entities(doc_id,clase,ent_key,valor,detalle,quote) VALUES(?,?,?,?,?,?)",
                        (did, "persona", dni_key(p), p.get("nombre", ""), p.get("rol", ""), p.get("quote", ""))); n_ent += 1; cite("entities", cur.lastrowid, p.get("quote", ""))
        for m in aslist(facts.get("montos"), "importe"):
            c = to_cents(m)
            cur.execute("INSERT INTO entities(doc_id,clase,ent_key,valor,detalle,monto_cents,fecha_iso,quote) VALUES(?,?,?,?,?,?,?,?)",
                        (did, "monto", str(c if c is not None else ""), m.get("importe", ""), m.get("concepto", ""), c, iso(m.get("fecha", "")), m.get("quote", ""))); n_ent += 1; cite("entities", cur.lastrowid, m.get("quote", ""))
        # organizations (new 'organizaciones' + legacy 'organismos'/'escuelas')
        for o in aslist(facts.get("organizaciones"), "nombre") + aslist(facts.get("organismos"), "nombre") + aslist(facts.get("escuelas"), "nombre"):
            nombre = o.get("nombre") or o.get("valor") or ""
            key = (o.get("id") or o.get("cue") or nombre)
            cur.execute("INSERT INTO entities(doc_id,clase,ent_key,valor,detalle,quote) VALUES(?,?,?,?,?,?)",
                        (did, "organizacion", cue_key(key), nombre, o.get("detalle") or o.get("cue", ""), o.get("quote", ""))); n_ent += 1
        # references: ids / document references / citations / standards (new 'referencias' + legacy)
        for r in (aslist(facts.get("referencias"), "valor") + aslist(facts.get("expedientes"), "numero")
                  + aslist(facts.get("resoluciones"), "numero") + aslist(facts.get("leyes"), "valor")):
            val = r.get("valor") or r.get("numero") or ""
            det = r.get("detalle") or r.get("caratula") or r.get("organismo") or ""
            cur.execute("INSERT INTO entities(doc_id,clase,ent_key,valor,detalle,fecha_iso,quote) VALUES(?,?,?,?,?,?,?)",
                        (did, "referencia", ex_key(val), val, det, iso(r.get("fecha", "")), r.get("quote", ""))); n_ent += 1
        # events
        for ev in aslist(facts.get("eventos"), "hecho") + [{"fecha": x.get("fecha"), "hecho": x.get("hecho"), "quote": x.get("quote")} for x in aslist(facts.get("fechas"), "hecho")]:
            fi = iso(ev.get("fecha", ""))
            if not fi or not (ev.get("hecho")):
                continue
            cur.execute("INSERT INTO events(doc_id,fecha_iso,hecho,monto_cents,quote) VALUES(?,?,?,?,?)",
                        (did, fi, ev.get("hecho", ""), ev.get("importe_cents"), ev.get("quote", ""))); n_ev += 1; cite("events", cur.lastrowid, ev.get("quote", ""))
        # relations
        for rel in aslist(facts.get("relaciones"), "objeto"):
            cur.execute("INSERT INTO relations(doc_id,sujeto,predicado,objeto,quote) VALUES(?,?,?,?,?)",
                        (did, rel.get("sujeto", ""), rel.get("predicado", ""), rel.get("objeto", ""), rel.get("quote", "")))

    # rebuild FTS + views + meta
    cur.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
    con.executescript(VIEWS)
    for k, v in (("schema_ver", str(SCHEMA_VER)), ("objetivo", objetivo),
                 ("outdir", outdir), ("n_docs", str(n_doc + n_skip))):
        cur.execute("INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))
    con.commit()
    errlog.close()
    con.close()
    print(f"BUILT db={db} docs={n_doc} skipped={n_skip} entities={n_ent} events={n_ev} errors={n_err}")


if __name__ == "__main__":
    main()
