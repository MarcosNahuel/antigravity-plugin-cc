---
name: notebook-kb
description: Use the notebook knowledge base (the local SQLite RAG /agy:notebook builds from a folder of documents) to do precise, grounded, cited work — total amounts by category, find every doc that mentions a person/organization, build a timeline, export a table — instead of re-reading prose and burning Claude's context. Trigger on "sum the amounts", "which docs mention X", "build a timeline", "who/what/when across these documents", or any aggregate/lookup over an analyzed corpus.
user-invocable: true
---

# notebook-kb — work against the local document RAG

`/agy:notebook <folder> | <objective>` analyzes a folder of documents and compiles a **queryable
SQLite database** `docs/agy/notebook/<slug>/notebook.db`: `documents, chunks (+FTS5 / optional
vectors), entities, events, relations, citations`. Every fact row carries a `quote` and a source
document. This skill is how you USE that DB to do real work — deterministically, with citations, and
without pulling the documents back into Claude's context.

## Decision gate — when to use the DB

- **Use the DB** (`/agy:notebook-query`) for **structured / aggregate / grounding** work: totals of
  amounts by category, "which documents mention <person/org/term>", timelines, entity rosters,
  exporting a table, verifying a figure against its source. SQL is exact and auditable; prose is not.
- **Use `/agy:notebook-ask`** for an open-ended **prose** answer grounded in the summaries.
- **Build/refresh first** if needed: if `notebook.db` is missing → run `/agy:notebook <folder> |
  <objective>`. If it's older than the newest `*.facts.json` → rebuild (Phase 1.5):
  `python "<plugin>/scripts/notebook_db.py" "<OUTDIR>" "<objective>"` (~1s, pure Python).

## How to query (there is NO sqlite3 CLI — always Python, read-only)

```bash
python - "<OUTDIR>/notebook.db" "<SQL>" <<'PY'
import sqlite3, sys, json
con = sqlite3.connect("file:%s?mode=ro" % sys.argv[1], uri=True); con.row_factory = sqlite3.Row
try: print(json.dumps([dict(r) for r in con.execute(sys.argv[2])], ensure_ascii=False, indent=2, default=str))
except Exception as e: print("SQL_ERROR: %s" % e)
PY
```

Prefer the `v_*` views (they dedup by `ent_key` and keep citations). The schema + a recetas cookbook
live in the `/agy:notebook-query` command file — reuse those queries. Entity taxonomy:
`persona | organizacion | monto | fecha | referencia`.

## Citation contract (non-negotiable for trustworthy answers)

- **Every claim cites** its source: `doc_ref` (or `basename`) of the document the row came from.
- **A SUM lists its contributing rows** so the total is auditable line by line. Monetary math is in
  integer `monto_cents`; divide by 100 only to display (no float drift).
- **0 rows → say "does not appear in the corpus"**, and surface coverage gaps:
  `SELECT nn,tipo,basename FROM documents WHERE estado='no_procesado'`. **Never invent** a name,
  amount, date or reference — if it isn't a row in the DB, it isn't a fact.

## Downstream workflows (turn the DB into deliverables)

- **Entity roster** → `SELECT * FROM v_personas` / `v_organizaciones` / `v_referencias`.
- **Timeline** → `SELECT * FROM v_timeline` → a chronological briefing.
- **Export a table** → query amounts by category (or any view), emit a small CSV/JSON, and hand it to
  whatever downstream tool or report consumes it — instead of transcribing figures from hundreds of
  pages by hand. Cross-check a computed total against the DB's `v_montos` total before presenting.
- **Contradiction check** → `/agy:notebook-audit <folder>` flags the same category with conflicting
  amounts, the same person/org under two names, the same reference with different values, and gaps.

## Semantic search (opt-in)

By default retrieval is **FTS5 keyword** (always on, zero deps). For fuzzy/conceptual questions add a
vector layer: build with `/agy:notebook <folder> | <objective> --semantic` (needs `pip install
sqlite-vec`; real embeddings need a `GEMINI_API_KEY`, else a keyword-ish lexical fallback). Then
`/agy:notebook-query` fuses keyword + vector ranking with RRF. Without it, keyword + structured SQL
already answer most aggregate/lookup work.

## Long sweeps & cross-session

- **Long document sets** — run `/agy:notebook <folder> | <objective> --background` and check progress
  with `/agy:notebook-status <folder>` (% done, ETA, pending docs). The sweep persists state every
  wave, so it's resumable: re-run `/agy:notebook` and cached docs are skipped. No daemon.
- **Cross-folder in Neon (opt-in)** — to query MANY notebooks together, export one KB to Postgres SQL
  with `scripts/notebook_neon.py <OUTDIR> <notebook_name>` (writes `nbkb_export.sql`, an isolated
  `nbkb` schema), then run it via the Neon MCP (`mcp__neon__run_sql`). Only worth it for cross-folder
  aggregation; the local `notebook.db` already answers single-folder questions.

## Reliability notes

- The DB is **disposable** (gitignored) and always rebuildable from the `.facts.json` sidecars; the
  `.md` summaries remain the human source of truth.
- The loader is **tolerant**: malformed/missing sidecars fall back to the `.md` frontmatter and are
  logged to `_facts_errors.log` — the document is still queryable by `tipo/fecha/doc_ref`.
