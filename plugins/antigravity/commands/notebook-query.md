---
description: Query the notebook knowledge base (SQLite) built by /agy:notebook — precise, grounded, cited. Ask in natural language ("sumá los montos por concepto", "qué docs mencionan el DNI 20123456", "timeline del expediente") or pass raw SQL. Read-only. Use this when you need exact aggregates/lookups across a document corpus instead of re-reading prose.
argument-hint: "<folder> | <pregunta o SQL>"
context: fork
allowed-tools: Bash, Read
---

Run a precise, **read-only** query over the `notebook.db` that `/agy:notebook` compiled from a folder
of documents. Every answer is grounded in the documents and **cited** (each row carries its source
`numero_gde` / `basename`). There is **no `sqlite3` CLI** on this machine — all DB access is Python.

Raw user request:
$ARGUMENTS

## Phase 0 — Resolve the DB (ONE Bash call)

Split `$ARGUMENTS` on the first `|`: left = folder (or its notebook slug), right = the question/SQL.
Resolve `OUTDIR = docs/agy/notebook/<slug>` (same `slug()` rule the notebook uses: lowercase, non
-alnum→`-`). Confirm `notebook.db` exists; if missing, tell the user to run `/agy:notebook <folder> |
<objetivo>` first and stop. If the DB is older than the newest `*.facts.json`, rebuild it first:
`python "<plugin>/scripts/notebook_db.py" "$OUTDIR" "$OBJETIVO"`.

## Phase 1 — Two query modes

**A) Raw SQL** — if the text after `|` starts with `SELECT` or `WITH`, run it verbatim.

**B) Natural language** — write a `SELECT` against the schema below (use the recetas as templates),
then run it. Prefer the `v_*` views (they dedup + carry citations). For aggregates over money, sum
`monto_cents` and divide by 100.0 only for display.

ALWAYS execute via this read-only Python heredoc (never a `sqlite3` shell):

```bash
python - "$OUTDIR/notebook.db" "$SQL" <<'PY'
import sqlite3, sys, json
con = sqlite3.connect("file:%s?mode=ro" % sys.argv[1], uri=True); con.row_factory = sqlite3.Row
try:
    print(json.dumps([dict(r) for r in con.execute(sys.argv[2])], ensure_ascii=False, indent=2, default=str))
except Exception as e:
    print("SQL_ERROR: %s" % e)
PY
```

## Phase 1b — Hybrid semantic retrieval (only if the DB was built with `--semantic`)

If `meta` has an `embedder` row (i.e. `/agy:notebook … --semantic` ran and `sqlite-vec` is installed),
a fuzzy/conceptual question can use **hybrid retrieval**: FTS5 keyword ranking + vector KNN, fused
with Reciprocal Rank Fusion (RRF, k=60). The `vec0` KNN needs its `LIMIT` inside a CTE (not through a
JOIN). Use this to FIND the relevant documents, then answer with the structured queries above.

```bash
python - "$OUTDIR/notebook.db" "$PREGUNTA" <<'PY'
import sqlite3, sys, struct, re, hashlib, math, json
db, q = sys.argv[1], sys.argv[2]
con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); con.row_factory = sqlite3.Row
emb = con.execute("SELECT v FROM meta WHERE k='embedder'").fetchone()
if not emb:
    print("NO_SEMANTIC: build with /agy:notebook … --semantic first (FTS5 keyword search still works)"); raise SystemExit
import sqlite_vec
con.enable_load_extension(True); sqlite_vec.load(con)
dim = int(con.execute("SELECT v FROM meta WHERE k='embed_dim'").fetchone()[0])
# query vector: Gemini if a real key + 768-dim, else the lexical-hash fallback (matches the embedder)
def hash_embed(t, d):
    v=[0.0]*d
    for tok in re.findall(r"\w+", t.lower()): v[int(hashlib.md5(tok.encode()).hexdigest(),16)%d]+=1.0
    n=math.sqrt(sum(x*x for x in v)) or 1.0; return [x/n for x in v]
key=__import__('os').environ.get('GEMINI_API_KEY','')
if emb[0].startswith('gemini') and key and not key.startswith('$'):
    import urllib.request
    u=f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={key}"
    r=urllib.request.Request(u,data=json.dumps({"model":"models/text-embedding-004","content":{"parts":[{"text":q}]}}).encode(),headers={"Content-Type":"application/json"})
    qvec=json.load(urllib.request.urlopen(r,timeout=30))["embedding"]["values"]
else:
    qvec=hash_embed(q, dim)
qv=struct.pack("%df"%dim, *qvec)
fts=[r["doc_id"] for r in con.execute("SELECT c.doc_id FROM chunks_fts f JOIN chunks c ON c.id=f.rowid WHERE chunks_fts MATCH ? ORDER BY rank LIMIT 10",(re.sub(r'[^\w ]',' ',q),))]
vec=[r["doc_id"] for r in con.execute("WITH knn AS (SELECT chunk_id,distance FROM vec_chunks WHERE embedding MATCH ? ORDER BY distance LIMIT 10) SELECT c.doc_id FROM knn JOIN chunks c ON c.id=knn.chunk_id ORDER BY knn.distance",(qv,))]
s={}
for rl in (fts,vec):
    for rank,d in enumerate(dict.fromkeys(rl),1): s[d]=s.get(d,0)+1.0/(60+rank)
order=sorted(s,key=lambda d:-s[d])
docs=[dict(con.execute("SELECT id,numero_gde,tipo,basename,relevancia FROM documents WHERE id=?",(d,)).fetchone()) for d in order[:8]]
print(json.dumps(docs, ensure_ascii=False, indent=2))
PY
```

## Phase 2 — Present (grounded + cited)

Narrate the rows. **Cite every claim** by `numero_gde`/`basename`. For a SUM, list the contributing
rows so it's auditable. If a query returns 0 rows, say *"no aparece en el corpus"* (and note any
`estado='no_procesado'` docs as a coverage gap) — **never invent** a value.

## Schema (notebook.db, schema_ver=1)

```
documents(id, basename, nn, slug, doc_name, tipo, numero_gde, fecha, emisor, relevancia, estado, summary_md_path, cache_key)
chunks(id, doc_id→documents, ord, seccion, texto)          chunks_fts(texto)  -- FTS5, diacritic-folded
entities(id, doc_id→documents, clase, ent_key, valor, detalle, monto_cents, fecha_iso, quote)
        clase ∈ persona|monto|fecha|expediente|resolucion|escuela|organismo|ley
events(id, doc_id→documents, fecha_iso, hecho, monto_cents, quote)
relations(id, doc_id→documents, sujeto, predicado, objeto, quote)
citations(id, doc_id→documents, tabla, fila_id, cita)
views: v_personas(dni,nombre,n_docs,docs)  v_montos(concepto,n,total_cents,total)
       v_expedientes  v_resoluciones  v_escuelas  v_timeline(fecha_iso,hecho,monto_cents,numero_gde,basename,quote)
```

## Recetas (NL → SQL)

```sql
-- total de montos por concepto (auditable)
SELECT * FROM v_montos ORDER BY total_cents DESC;
-- gran total
SELECT printf('$%.2f', SUM(monto_cents)/100.0) total FROM entities WHERE clase='monto';
-- cada monto con su cita y documento fuente
SELECT e.valor importe, e.detalle concepto, e.quote cita, d.numero_gde, d.basename
  FROM entities e JOIN documents d ON d.id=e.doc_id WHERE e.clase='monto';
-- documentos que mencionan un DNI
SELECT d.numero_gde, d.tipo, e.valor FROM entities e JOIN documents d ON d.id=e.doc_id
  WHERE e.clase='persona' AND e.ent_key='20123456';
-- timeline del caso
SELECT fecha_iso, hecho, numero_gde FROM v_timeline;
-- búsqueda full-text (acentos plegados) con documento fuente
SELECT d.numero_gde, snippet(chunks_fts,0,'[',']','…',8) s
  FROM chunks_fts f JOIN chunks c ON c.id=f.rowid JOIN documents d ON d.id=c.doc_id
  WHERE chunks_fts MATCH 'zona AND antiguedad';
-- resoluciones / expedientes / escuelas
SELECT * FROM v_resoluciones;   SELECT * FROM v_expedientes;   SELECT * FROM v_escuelas;
-- cobertura: documentos no procesados (gaps)
SELECT nn, tipo, basename FROM documents WHERE estado='no_procesado';
```

## Notes
- Read-only (`mode=ro`): this command never writes. To refresh facts, re-run `/agy:notebook`.
- For grounded *prose* answers instead of structured rows, use `/agy:notebook-ask`.
