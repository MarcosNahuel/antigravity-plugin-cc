---
name: notebook-kb
description: Use the notebook knowledge base (the SQLite DB /agy:notebook builds from a folder of documents) to do precise, grounded, cited work — total amounts, find every doc mentioning a DNI/expediente, build a timeline, seed a liquidation — instead of re-reading prose. Trigger when the user asks "cuánto suma", "qué expedientes/DNI", "timeline del caso", "armá la liquidación desde el notebook", or any aggregate/lookup over an analyzed document corpus.
user-invocable: true
---

# notebook-kb — work against the document knowledge base

`/agy:notebook <folder> | <objetivo>` analyzes a folder of documents and (v0.8+) compiles a
**queryable SQLite database** `docs/agy/notebook/<slug>/notebook.db`: `documents, chunks (+FTS5),
entities, events, relations, citations`. Every fact row carries a `quote` and a source document.
This skill is how you USE that DB to do real work — deterministically and with citations.

## Decision gate — when to use the DB

- **Use the DB** (`/agy:notebook-query`) for **structured / aggregate / grounding** work: totals of
  montos, "which docs mention DNI X / expediente Y", timelines, rosters, building a liquidation seed,
  verifying a figure with its source. SQL is exact and auditable; prose is not.
- **Use `/agy:notebook-ask`** for an open-ended **prose** answer grounded in the summaries.
- **Build/refresh first** if needed: if `notebook.db` is missing → run `/agy:notebook <folder> |
  <objetivo>`. If it's older than the newest `*.facts.json` → rebuild (Phase 1.5):
  `python "<plugin>/scripts/notebook_db.py" "<OUTDIR>" "<objetivo>"` (~1s, pure Python).

## How to query (there is NO sqlite3 CLI — always Python, read-only)

```bash
python - "<OUTDIR>/notebook.db" "<SQL>" <<'PY'
import sqlite3, sys, json
con = sqlite3.connect("file:%s?mode=ro" % sys.argv[1], uri=True); con.row_factory = sqlite3.Row
try: print(json.dumps([dict(r) for r in con.execute(sys.argv[2])], ensure_ascii=False, indent=2, default=str))
except Exception as e: print("SQL_ERROR: %s" % e)
PY
```

Prefer the `v_*` views (they dedup by `ent_key` and keep citations). Schema + a recetas cookbook are
in the `/agy:notebook-query` command file — reuse those queries.

## Citation contract (non-negotiable for legal/administrative work)

- **Every claim cites** its source: `numero_gde` (or `basename`) of the document the row came from.
- **A SUM lists its contributing rows** so the total is auditable line by line. Monetary math is in
  integer `monto_cents`; divide by 100 only to display.
- **0 rows → say "no aparece en el corpus"**, and surface coverage gaps:
  `SELECT nn,tipo,basename FROM documents WHERE estado='no_procesado'`. **Never invent** a DNI, monto,
  fecha or expediente — if it isn't a row in the DB, it isn't a fact.

## Downstream workflows (turn the DB into deliverables)

- **Entity roster** → `SELECT * FROM v_personas` / `v_escuelas` / `v_expedientes`.
- **Case timeline** → `SELECT * FROM v_timeline` → a chronological briefing.
- **Seed a liquidation** → pull montos by concepto + the actor's DNI + the relevant resolución/EX from
  the DB, emit a small CSV/JSON, and feed it to the existing `liquidaciones_zona/casos/gen_liquidacion_*.py`
  / costeo generators — instead of transcribing figures from hundreds of fojas by hand. Cross-check the
  DB total against the generator's computed total before presenting.
- **Contradiction check (manual until /agy:notebook-audit ships)** → look for the same `concepto` with
  conflicting `monto_cents`, or a resolución cited but absent, or one DNI under two `nombre`s.

## Reliability notes

- The DB is **disposable** (gitignored) and always rebuildable from the `.facts.json` sidecars; the
  `.md` summaries remain the human source of truth.
- The loader is **tolerant**: malformed/missing sidecars fall back to the `.md` frontmatter and are
  logged to `_facts_errors.log` — the document is still queryable by `tipo/fecha/numero_gde`.
