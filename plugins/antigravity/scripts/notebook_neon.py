#!/usr/bin/env python3
"""Phase 6 (opt-in, speculative): export a local notebook.db to Postgres/Neon SQL for
CROSS-expediente, cross-session querying.

The local `notebook.db` already answers everything for ONE folder. This exporter is only worth it
when you want to query MANY expedientes together in Neon. It emits idempotent SQL into a dedicated
`nbkb` schema (it does NOT touch `dge_acuerdos`), keyed by (notebook, basename) so re-exports upsert
cleanly. Run the generated file via the Neon MCP (`mcp__neon__run_sql` / `run_sql_transaction`) — this
script never connects anywhere itself (no creds, no coupling).

Usage:  python notebook_neon.py <OUTDIR> [<notebook_name>]   # writes <OUTDIR>/nbkb_export.sql (utf-8)
"""
import sys, os, sqlite3


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


DDL = """CREATE SCHEMA IF NOT EXISTS nbkb;
CREATE TABLE IF NOT EXISTS nbkb.documents(
  notebook text, basename text, tipo text, numero_gde text, fecha text, emisor text,
  relevancia int, estado text, objetivo text, PRIMARY KEY(notebook, basename));
CREATE TABLE IF NOT EXISTS nbkb.entities(
  notebook text, basename text, clase text, ent_key text, valor text, detalle text,
  monto_cents bigint, fecha_iso text, quote text);
CREATE TABLE IF NOT EXISTS nbkb.events(
  notebook text, basename text, fecha_iso text, hecho text, monto_cents bigint, quote text);
CREATE INDEX IF NOT EXISTS ix_nbkb_ent ON nbkb.entities(clase, ent_key);
CREATE INDEX IF NOT EXISTS ix_nbkb_ev ON nbkb.events(fecha_iso);
"""


def main():
    outdir = sys.argv[1]
    nb = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(os.path.normpath(outdir))
    db = os.path.join(outdir, "notebook.db")
    if not os.path.exists(db):
        print("-- NO_DB: run /agy:notebook first"); return
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); con.row_factory = sqlite3.Row
    objetivo = ""
    r = con.execute("SELECT v FROM meta WHERE k='objetivo'").fetchone()
    if r:
        objetivo = r["v"]
    lines = [DDL]
    # fresh-load this notebook's rows (idempotent: clear then insert)
    lines.append(f"DELETE FROM nbkb.documents WHERE notebook={q(nb)};")
    lines.append(f"DELETE FROM nbkb.entities  WHERE notebook={q(nb)};")
    lines.append(f"DELETE FROM nbkb.events    WHERE notebook={q(nb)};")
    for d in con.execute("SELECT basename,tipo,numero_gde,fecha,emisor,relevancia,estado FROM documents"):
        lines.append("INSERT INTO nbkb.documents(notebook,basename,tipo,numero_gde,fecha,emisor,relevancia,estado,objetivo) VALUES("
                     + ",".join([q(nb), q(d["basename"]), q(d["tipo"]), q(d["numero_gde"]), q(d["fecha"]),
                                 q(d["emisor"]), q(d["relevancia"]), q(d["estado"]), q(objetivo)]) + ");")
    for e in con.execute("""SELECT d.basename b,e.clase,e.ent_key,e.valor,e.detalle,e.monto_cents,e.fecha_iso,e.quote
                            FROM entities e JOIN documents d ON d.id=e.doc_id"""):
        lines.append("INSERT INTO nbkb.entities(notebook,basename,clase,ent_key,valor,detalle,monto_cents,fecha_iso,quote) VALUES("
                     + ",".join([q(nb), q(e["b"]), q(e["clase"]), q(e["ent_key"]), q(e["valor"]),
                                 q(e["detalle"]), q(e["monto_cents"]), q(e["fecha_iso"]), q(e["quote"])]) + ");")
    for v in con.execute("""SELECT d.basename b,ev.fecha_iso,ev.hecho,ev.monto_cents,ev.quote
                            FROM events ev JOIN documents d ON d.id=ev.doc_id"""):
        lines.append("INSERT INTO nbkb.events(notebook,basename,fecha_iso,hecho,monto_cents,quote) VALUES("
                     + ",".join([q(nb), q(v["b"]), q(v["fecha_iso"]), q(v["hecho"]), q(v["monto_cents"]), q(v["quote"])]) + ");")
    con.close()
    n_ins = sum(1 for l in lines if l.startswith("INSERT"))
    path = os.path.join(outdir, "nbkb_export.sql")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"EXPORTED notebook={nb} inserts={n_ins} sql={path}")
    print("Run it in Neon via the MCP: mcp__neon__run_sql (or run_sql_transaction). Schema: nbkb (does not touch dge_acuerdos).")


if __name__ == "__main__":
    main()
