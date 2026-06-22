# Notebook Knowledge Base — design (multi-agent researched, 2026-06-22)

> Upgrade `/agy:notebook` from "a pile of markdown summaries" into a **specialized, queryable
> SQLite database** that Claude Code does *work* against — grounded, cited, deterministic.
> No Node runtime; agy extracts, Python stdlib (`sqlite3` + `re` + `json`) compiles & queries.

## Vision

The same single agy pass that writes `NN-slug.resumen.md` (human layer) ALSO emits a strict
`NN-slug.facts.json` sidecar (machine layer). A pure-Python loader compiles every sidecar into one
`notebook.db` per notebook folder: `documents / chunks / entities / events / relations / citations`
+ an FTS5 index. Every fact row carries `doc_id + quote + cita`, so amounts, DNIs, expedientes,
fechas, resoluciones, escuelas become exact SQL rows traceable to a document. For DGE expedientes:
*"sumá los montos del EX-…", "qué docs mencionan el DNI …", "timeline del caso", "armá la
liquidación desde el notebook"* become deterministic queries (monto math in integer **cents**, no
float drift) that feed the existing `gen_liquidacion_*.py` generators — instead of manual
transcription from hundreds of fojas.

Properties: **incremental** (sidecars share the `size:mtime:objhash` cache key), **offline-first**
(FTS5 + regex always-on; vectors opt-in), **zero-regression** (the `.md` and `notebook-ask` are
untouched; the DB is an additive, disposable, gitignored derivative).

## Architecture (first slice = Phases 1–2)

**File layout** (per notebook folder under `docs/agy/notebook/<slug>/`):
```
NN-slug.resumen.md     (unchanged — human layer)
NN-slug.facts.json     (NEW — machine layer, source of truth for the DB)
notebook.db            (NEW — compiled SQLite KB; gitignored, disposable)
_facts_errors.log      (NEW — quarantined bad/missing sidecars)
```

**SQLite schema** (`schema_ver=1`): `documents, chunks, entities, events, relations, citations` +
`chunks_fts` (FTS5, `unicode61 remove_diacritics 2` for es-AR) + dedup-at-query views
(`v_personas, v_montos, v_expedientes, v_resoluciones, v_escuelas, v_timeline`). Full DDL lives in
`plugins/antigravity/scripts/notebook_db.py`. Monetary values are **`monto_cents INTEGER`**.

**Build pipeline** — `notebook.md` Phase 2.5 (after the sweep): one Bash→Python call to
`notebook_db.py "$OUTDIR" "$OBJETIVO"`. Tolerant + idempotent: parse each sidecar (extract the
last/largest valid JSON if malformed); on missing/invalid → fall back to `.md` frontmatter + log;
UPSERT-by-doc (DELETE+insert, cascade wipes stale child rows); skip docs whose `cache_key` is
unchanged; rebuild FTS; write `meta`. **Never crashes the build.**

**Query interface** — `/agy:notebook-query <folder> | <pregunta-o-SQL>`. Read-only
(`mode=ro&uri=True`) via a Python heredoc (there is **no `sqlite3` CLI** on this box — all DB access
is Python). Raw `SELECT/WITH` runs directly; a natural-language question → Claude writes SQL against
the shipped SCHEMA + recetas cookbook, runs it, narrates rows **with citations**.

**Skill** — `skills/notebook-kb/SKILL.md` (user-invocable): decision gate (build only for
structured/aggregate/grounding tasks), the query wrapper, the recetas library, the **citation
contract** (every claim cites `numero_gde + summary_md_path`; SUMs list contributing rows; 0 rows →
"no aparece en el corpus", never invent), and downstream workflows (entity roster / timeline /
seed-liquidation that `gen_liquidacion_*.py` consume).

## Integrations adopted

- **Gemini plugin** (`abiswas97/gemini-plugin-cc`): `schemas/` JSON-Schema validation of the sidecar
  (highest-leverage import); thin-MD-over-real-`scripts/` runtime split; `--resume/--fresh` ≡ the
  incremental manifest; structured error envelopes (`_facts_errors.log`). Background jobs +
  grounding-gate Stop-hook → deferred (Phases 4–5).
- **Codex plugin** (`openai/codex-plugin-cc`): the `--output-schema` + **tolerant parser** discipline
  (per-doc try/parse, extract last/largest valid JSON, never abort the sweep); prompt-block library
  (ocr_grounding, entity_normalization, citation_rules) folded into the `agy-prompting` skill;
  read-only-by-default. Unix-socket app-server → not ported (no Node; agy is one-shot `--print`).

## Roadmap

| Phase | Deliverable | Effort | Status |
|---|---|---|---|
| **1** | Structured `.facts.json` sidecars + `notebook_db.py` loader + Phase 2.5 wiring + DDL | M | ✅ v0.8.0 |
| **2** | `/agy:notebook-query` + `skills/notebook-kb/SKILL.md` | M | ✅ v0.8.0 |
| 3 | Opt-in `--semantic`: sqlite-vec + Gemini embeddings, hybrid FTS5+vector (RRF) | L | ✅ v0.9.0 |
| 4 | `--background` sweeps + `/agy:notebook-status` job records (200-page expedientes) | M | ✅ v0.11.0 |
| 5 | `/agy:notebook-audit` → CONTRADICCIONES.md (grounding Stop-hook deferred) | L | ✅ v0.10.0 |
| 6 | (opt-in) Neon export of the KB to a dedicated `nbkb` schema for cross-expediente SQL | S | ✅ v0.11.0 |

> **All roadmap phases implemented (2026-06-22).** Phase 4 = `scripts/notebook_job.py` (init/sync/status)
> + `/agy:notebook-status`; cooperative "background" (state persisted every wave, resumable via the
> incremental cache — no daemon). Phase 6 = `scripts/notebook_neon.py` emits idempotent Postgres SQL
> (`nbkb` schema, keyed by notebook+basename) to run via the Neon MCP; chosen over auto-upsert into
> `dge_acuerdos` to avoid coupling — the local `notebook.db` already serves single-expediente queries,
> so Neon is only for cross-folder aggregation. The opt-in grounding Stop-hook from Phase 5 stays
> deferred (loop-risk; the citation contract in the skill covers most of its value).

## Key risks & mitigations

- **agy JSON flakiness** → tolerant loader + last/largest-valid-JSON extraction + `.md` fallback; DB always buildable.
- **Monto float drift** → `monto_cents INTEGER` everywhere; divide by 100 only for display.
- **Silent coverage gaps** → keep `no_procesado` document rows with empty facts so queries report coverage honestly (legal defensibility).
- **Hallucinated facts in a liquidation** → every row carries `quote + cita`; SUMs auditable row-by-row; opt-in grounding gate later.
- **No `sqlite3` CLI** (verified) → all access via Python heredoc, hard rule in command + skill.
