# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.1] - 2026-07-05

### Changed

- Routing/discoverability: sharpened `/agy:deep-research`'s description to lead with **when** to use it (decisions/designs where a single-shot answer isn't enough), and repositioned `/agy:research`'s description as the fast single-shot option that points to `/agy:deep-research` for deep, multi-round, fact-checked work. Removes the "deep web research" naming collision so Claude routes between the two correctly.

## [1.5.0] - 2026-07-05

### Added

- `/agy:deep-research [--depth L|H] [--background] [--yes] [--engines agy|mixed] <topic>` — deep
  research multi-agente sobre el motor de Workflows: agy browsea en paralelo por ángulo, Claude razona
  el análisis global y la convergencia entre rondas (depth `L`≤2 rondas / `H`≤4 rondas), red-team con
  agy sobre los claims centrales/de fuente única, gate de plan (salvo `--yes`/`--background`), y una
  recomendación aplicada grounded en memoria/repo local cuando el tema lo pide. Complementa (no
  reemplaza) `/agy:research`, que sigue siendo el single-shot rápido. `--engines mixed` queda aceptado
  pero hoy se comporta igual que `agy` (no hay un segundo motor de browsing wireado todavía).
- `deep-research-agy` Workflow (`scripts/deep-research-agy.js`) — orquesta las rondas, el red-team y
  la síntesis; `report.coverage` sale pre-poblado (determinístico) para que el comando renderice
  directo sin recalcular nada.
- `scripts/deep-research-lib.mjs` — fuente de verdad de los helpers puros (`normURL`, `corroborationOf`,
  `ingestRound`, `isConverged`, `computeCoverage`, `rankClaimsForRedTeam`, `applyRedTeam`,
  `renderReportMarkdown`) + tests (`node --test`), con un test de sync que garantiza que la copia
  inlined en el Workflow nunca diverge de la lib.
- `agy-rescue`: modos `deep-angle` y `redteam` para el browsing por ángulo y el desafío adversarial de
  claims.

## [1.4.2] — 2026-07-02

### Fixed — Windows path normalization for `ask`/`review`/`report-analyze` (thanks @headsvk)

- `TEMP_DIR`/`TEMP_FILE` in the `ask`, `review`, and `report-analyze` modes were built with a raw
  `mktemp -d -t ...` (POSIX-style path, e.g. `/tmp/agy-ask-xxx`). That path travels embedded inside
  the `--print` prompt text (a full sentence, not a bare CLI argument), so Git Bash's automatic
  MSYS2 argv path translation — which only rewrites arguments that are themselves a pure path, like
  `--add-dir /tmp/xxx` — never touches it. The native `agy.exe` then receives the literal POSIX
  string and cannot resolve it, surfacing as the known issue #76 / Windows-rename symptoms.
- Fix (PR #5): resolve `TEMP_DIR` via `cygpath -u` (POSIX form, for Bash) and `TEMP_FILE` via
  `cygpath -m` (mixed-mode form, e.g. `C:/Users/...` — forward slashes + drive letter, readable by
  both `agy.exe` and Bash tools like `test -f`/`cat`), with a no-op fallback to `${TMPDIR:-/tmp}` on
  Unix where `cygpath` doesn't exist. Applied to `ask`, `review`, `report-analyze`, and the
  `/agy:setup` ping self-test.
- Verified end-to-end on Windows + Git Bash: reproduced the old POSIX-path failure mode, confirmed
  the new mixed-mode path resolves correctly for both a native writer and Bash readers, and test-merged
  cleanly against v1.4.1 (no overlap with `agy_scratch.py`'s scratch-then-move, which only covers the
  `notebook*` modes).

## [1.4.1] — 2026-06-26

### Improved — agy notebook calls are faster (scratch-then-move), zero quality cost

- Investigation (60 session logs) found agy snapshots EVERY untracked file of any repo passed via
  `--add-dir` on every call, and sandboxes write_file to project paths (rejection→replan round-trips).
  New `scripts/agy_scratch.py` stages each call's read inputs in a fresh neutral scratch dir, runs
  `agy --add-dir <scratch>` ONLY (never the project), then **moves** outputs to their canonical paths.
  All four notebook modes (notebook / notebook-group / notebook-index / notebook-ask) now route
  through it. **0 untracked-file snapshots + 0 artifact rejections, repo-independent** (the prior
  gitignore band-aid only reached 10 snapshots and needed a clean repo).
- **Measured A/B**: 15s/20-snapshots/2-rejections → **9s/0/0**, with **byte-identical extracted facts**
  (same personas/orgs/relations). Zero quality cost: agy gets the identical prompt + input bytes and
  produces identical output; only the file's final location changes, after agy exits. Validated both
  the `--in` (single-file modes) and `--in-dir` (index/ask) paths end-to-end on a dirty repo.
- The inherent agy cost (the ~5s boot + Gemini's agentic generation, median 14 model round-trips/call)
  is NOT targeted — that's quality work, not waste. (A tested "do it in one step" directive made it
  slower and was rejected.)

## [1.4.0] — 2026-06-23

### Added — `/agy:notebook` reports the Claude tokens it saved

- After a sweep, `/agy:notebook` Phase 3 now estimates and shows **how many of Claude's tokens it
  saved** (`scripts/tokens_saved.py`, stdlib + optional tiktoken): `corpus` (tokens agy read) vs
  `claude_reads` (the synthesis Claude actually consumes: RESUMEN_MAESTRO + INDEX) → `saved` + a
  `~Nx less` ratio. Quantifies the plugin's core value (heavy reading runs in Gemini, off Claude's
  context). Honest scope: scanned docs' OCR'd text isn't counted, so the real saving is higher.
  Validated on a synthetic corpus (corpus~5060 vs reads~16 → ~316x).

## [1.3.0] — 2026-06-23

### Added — `/agy:setup` now reports the whole stack

- `/agy:setup` gains a Phase 0 stack check (`scripts/stack_check.py`, zero agy, stdlib): reports which
  capabilities are ready and how to fix what's missing — **agy CLI** (required), **PyMuPDF** (required
  for notebook PDFs), **sqlite-vec** (optional, `--semantic`), **ffmpeg** (optional, long media), and
  **graphify + agy-cli backend** (optional, `/agy:graph`). Prints `STACK n/5 present`. Also reusable
  by the `docs/SETUP_AGENT_STACK.md` bootstrap prompt. Validated (4/5 present, all required OK).
- Verified `/agy:notebook-graph`'s `graph.html` renders correctly in a browser (vis-network
  force-directed graph with colored entity/document nodes + relation edges).

## [1.2.1] — 2026-06-23

### Improved — agy now extracts relations (was always empty)

- The `notebook` / `notebook-group` extraction prompts now **actively instruct agy to extract
  subject–predicate–object relations** between entities ("X aprobó Y", "A contrató a B", "C reporta a
  D"). Investigation showed `relaciones` was empty in every real notebook.db, leaving the relational
  layer of the RAG and the knowledge graph unused. After the change, validated on a real agy run:
  **8 relations extracted** across 2 docs → `relations=8` in the DB → `/agy:notebook-graph` now adds
  those as explicit graph edges (richer graph + queryable relations). Additive only; no behavior break.

## [1.2.0] — 2026-06-23

### Added — `/agy:notebook-graph`: a graph view of the RAG, free + local

- **`/agy:notebook-graph <folder>`** turns a `notebook.db` into a knowledge GRAPH — a node-link
  `graph.json` + a self-contained interactive `graph.html` (vis-network) — with **zero agy calls and
  zero new deps** (pure stdlib). Investigation found agy almost never fills the explicit `relaciones`
  array (relations=0 in every real notebook.db), so this derives edges from **entity co-occurrence
  within documents** (the relational signal that needs no LLM) plus any explicit relations. Nodes =
  deduped entities (persona/organizacion/referencia) + documents; reports the hub entities.
- Validated on a real notebook.db: 6 nodes / 12 edges (co-occurrence + appears_in), correct hubs.
- Complements `/agy:notebook-query` (exact SQL) and `/agy:graph` (Graphify/Gemini, for code + Leiden).
- 21 slash commands.

## [1.1.0] — 2026-06-22

### Added — `/agy:graph`: knowledge graphs via Gemini, off Claude's tokens

- **`/agy:graph <folder>`** builds a knowledge GRAPH of a folder (code + docs) using
  [Graphify](https://github.com/safishamsi/graphify) (MIT) with a new **`agy-cli` backend** this
  plugin ships: **Gemini (via the Antigravity CLI `agy`) builds the graph** — tree-sitter ASTs +
  NetworkX + Leiden communities + an interactive `graph.html` — authenticated by the user's
  Antigravity/Google sign-in (no API key) and **off the host assistant's token budget**. Claude then
  reads the small `graph.json` / `GRAPH_REPORT.md` to reason. Complements `/agy:notebook` (graphs =
  relations/communities; notebook = multimodal docs + exact SQL).
- The integration ships inside the plugin and installs on first use (opt-in heavier deps): the
  `agy-cli` backend patch (`scripts/agy-cli-backend.patch`) + an idempotent installer
  (`scripts/graphify_agy_install.py`) that clones graphify, applies the patch and `pip install -e`s it.
  Validated end-to-end on a 4-doc corpus (18 nodes / 24 edges / 3 named communities, $0 Claude tokens).
- **`docs/SETUP_AGENT_STACK.md`** — a paste-into-Claude-Code bootstrap prompt that checks/installs the
  whole stack (agy, the plugin, PyMuPDF, optional sqlite-vec, graphify + agy-cli) and smoke-tests each.
- 20 slash commands.

## [1.0.0] — 2026-06-22

Stable 1.0 — repositioned as a **general-purpose NotebookLM replacement and capability pack for
Claude Code that saves tokens** (the heavy reading runs in Gemini via `agy`, not in Claude's context).

### Changed

- **General entity taxonomy for the notebook RAG.** The knowledge base now extracts a general,
  domain-agnostic set of entities — `persona | organizacion | monto | fecha | referencia` — instead
  of any domain-specific types. Views renamed accordingly (`v_personas, v_organizaciones, v_montos,
  v_referencias, v_fechas, v_timeline`); the document handle is `doc_ref`. The loader still accepts
  legacy fact keys, so existing `notebook.db`s rebuild cleanly. Re-validated end-to-end (build +
  all views + the audit) on the new taxonomy.
- **Docs, examples and marketing repositioned** to the general framing (research papers, contracts,
  meeting notes, RFPs, a book's chapters) — README, `llms.txt`, command/skill descriptions, design
  docs and promo. Described as a NotebookLM replacement + token-saver, not tied to any one industry.

### Added

- **`docs/semantic-rag-explainer.html`** — a self-contained visual page explaining the local RAG: what
  it is, how it saves tokens, and keyword (FTS5) vs semantic (vectors fused with RRF). Reusable for the
  project page.

## [0.11.0] — 2026-06-22

### Added — KB roadmap Phases 4 & 6 (all roadmap phases now complete)

- **Phase 4 — background sweeps + status.** `scripts/notebook_job.py` (init/sync/status) keeps a job
  record (`<OUTDIR>/.jobs/current.json`) tracking per-document progress; **`/agy:notebook-status
  <folder>`** reports % complete, done/pending/failed, elapsed + ETA, and which docs are pending.
  `/agy:notebook … --background` announces a resumable sweep. "Background" is cooperative — state is
  persisted every wave and the incremental cache resumes an interrupted run; no daemon. Validated on
  synthetic manifests (75% → 100% transitions, group pipe-list expansion, failed/pending detection).
- **Phase 6 — Neon export (opt-in).** `scripts/notebook_neon.py` emits idempotent Postgres SQL
  (utf-8 `nbkb_export.sql`, a dedicated `nbkb` schema keyed by notebook+basename) to run via the Neon
  MCP for cross-notebook querying. Chosen over auto-upsert into any application schema to avoid coupling;
  the local `notebook.db` already serves single-folder queries. Validated (idempotent DELETEs,
  balanced quoting, isolated schema).
- 19 slash commands. The opt-in grounding Stop-hook from Phase 5 stays deferred (loop-risk; the
  skill's citation contract covers most of its value).

## [0.10.0] — 2026-06-22

### Added — video vision + notebook contradiction audit (Phase 5)

- **`/agy:video <file|URL> [focus]`** — *watch* a video and return a structured **visual** breakdown
  (not just a transcript): a scene table with timestamps, on-screen text/OCR (slides, charts, UI,
  captions), and key visual moments. Gemini is natively multimodal in video; Claude Code is not. New
  `MODE: video` in the subagent; output to `docs/agy/video/`. Validated end-to-end on a real YouTube
  video (accurate scene + OCR + key-moment breakdown in ~19s).
- **`/agy:notebook-audit <folder>`** (KB roadmap Phase 5) — deterministic, read-only SQL audit over
  `notebook.db` that finds the contradictions that matter across a document corpus: the same
  concepto with conflicting amounts, the same person under two names, the same reference with different
  values, coverage gaps (`no_procesado` docs), and unparseable amounts → writes `CONTRADICCIONES.md`.
  `scripts/notebook_audit.py`, pure stdlib. Validated on crafted contradictions (all six checks fire
  correctly, DNI normalized across name/format variants).
- 18 slash commands.

## [0.9.0] — 2026-06-22

### Added — optional semantic layer for the notebook KB (`--semantic`, hybrid retrieval)

Phase 3 of the knowledge-base roadmap. Purely additive and opt-in — FTS5 keyword search stays the
always-on default with zero new deps.

- **`plugins/antigravity/scripts/notebook_embed.py`** — embeds every chunk into a `sqlite-vec` `vec0`
  table. Embeddings from **Gemini REST** (`text-embedding-004`, 768-dim, batched, pure stdlib
  `urllib`) when a real `GEMINI_API_KEY` is set; otherwise a stdlib **lexical-hash fallback** (256-dim,
  keyword-ish, clearly labeled) so it runs with zero key. Requires `pip install sqlite-vec` (the only
  new, opt-in dependency); prints `SEMANTIC_UNAVAILABLE` and no-ops if absent.
- **`/agy:notebook <folder> | <objetivo> --semantic`** runs the embed step in Phase 1.5 after the DB build.
- **`/agy:notebook-query`** gains a hybrid path: FTS5 keyword ranking + `vec0` vector KNN fused with
  **Reciprocal Rank Fusion** (RRF, k=60) to find relevant docs for fuzzy/conceptual questions, then
  answers with the structured cited queries. Validated end-to-end on a real `notebook.db`
  (sqlite-vec v0.1.9): vec0 KNN + RRF return the expected ranking.

## [0.8.0] — 2026-06-22

### Added — notebook becomes a queryable knowledge base (multi-agent designed + benchmarked)

`/agy:notebook` no longer just writes prose: the same agy pass now emits a structured
`NN-slug.facts.json` sidecar per document, and a pure-Python (stdlib `sqlite3`) loader compiles them
into a queryable **SQLite database** (`notebook.db`) so Claude Code does exact, grounded, cited work.

- **`plugins/antigravity/scripts/notebook_db.py`** — tolerant, idempotent loader → `documents ·
  chunks (+FTS5) · entities · events · relations · citations` + dedup views (`v_montos`,
  `v_personas`, `v_timeline`, …). Money is integer **cents** (no float drift); every fact row carries
  a `quote` + source document. A malformed/missing sidecar falls back to the `.md` frontmatter and is
  logged — the build never crashes.
- **`/agy:notebook-query <folder> | <pregunta|SQL>`** — read-only NL→SQL or raw SQL over the DB, with
  citations. There is no `sqlite3` CLI on Windows here, so all access is a Python heredoc.
- **`skills/notebook-kb/SKILL.md`** — teaches Claude when/how to use the DB (decision gate, query
  wrapper, citation contract, downstream liquidation/timeline workflows).
- **`schemas/notebook-facts.schema.json`** — JSON Schema for the sidecar (validation, adopted from the
  Gemini-plugin `schemas/` pattern). Tolerant last/largest-valid-JSON parsing adopted from the
  Codex-plugin discipline.
- Validated end-to-end on real agy 1.0.10 output: agy → `.facts.json` → `notebook.db` → cited SQL
  (montos by concepto with exact cents, DNI dedup incl. CUIL→DNI, FTS, timeline). Design +
  full roadmap (semantic vectors, background sweeps, grounding gate) in `docs/notebook-kb-design.md`.

## [0.7.2] — 2026-06-22

### Changed — `/agy:notebook` throughput at scale (multi-agent-designed + benchmarked)

- **Batch ALL text documents, not just one-page docs.** Phase 0 now greedily packs every
  uncached text doc into groups of **≤4 docs / ≤24 000 chars** and one `MODE: notebook-group` agy
  call summarizes the whole batch — writing **one summary file per member** (full per-doc
  frontmatter, so `notebook-index` keeps full granularity). The binding cost at scale is agy
  invocations-per-minute (≈10 RPM free tier), and batching cuts that count directly.
  - Measured: a 15-doc mixed folder dropped from **15 → 6 agy invocations** (~2.5×; ~4× on
    text-heavy corpora). One 4-doc batch call wrote 4 correct, independent summaries in **14.5 s**.
- **Vision/scanned docs stay strictly 1-per-call** (OCR is slow; multimodal batches blow the timeout).
- **Two dispatch queues** (text/group vs vision) so a slow OCR doc no longer head-of-line-blocks a
  wave of fast text batches. `RPM` is a documented constant (10 free / raise on Pro).
- Incremental cache now records one entry per member summary; group rows expand their pipe-lists in
  the manifest and the cache rewrite.

## [0.7.1] — 2026-06-22

### Fixed

- **`/agy:notebook` was ~4× slower than it should be.** When agy runs with its CWD inside the calling
  git project, agy 1.0.10 registers it as a cascade "project" and sandboxes every `write_file`
  artifact to `brain/<uuid>/`, then **rejects** the absolute summary path (`not a valid artifact
  path`). The model then replans and retries 3-5× per document — a single 1-page document took
  **43s and 5 model round-trips** instead of ~10s and 1 write. It also re-snapshotted the repo's
  untracked files on every invocation. Fix: the `notebook`, `notebook-index`, `notebook-ask` and
  `notebook-group` modes now run agy from a **neutral scratch CWD** (`mktemp -d`) and grant file
  access with repeatable `--add-dir` for the read/write directories instead of `--add-dir <CWD>`.
  Verified: clean CWD writes directly with **0 rejections in ~10s**. (Concurrency was never the
  bottleneck — the per-document retry loop was.)

## [0.7.0] — 2026-06-19

Audio & video — capabilities Claude Code does not have natively, offloaded to Gemini via `agy`.

### Added

- **`/agy:transcribe <audio|video|YouTube-URL> [focus]`** — faithful transcript + summary of an
  audio or video file (or a YouTube/remote URL), in the source language. Voice notes, meetings,
  calls, screencasts. Video/URLs get timestamps. Saves to `docs/agy/transcripts/`. Verified on a
  real WhatsApp `.ogg` voice note and a YouTube video (content + timestamps).
- **`/agy:media <file|URL> | <question>`** — multimodal Q&A over an audio/video/image (or URL):
  "what decisions were made?", "what happens at 2:30?", "what's the tone?" — grounded in what agy
  heard/saw, with time references. Saves to `docs/agy/media/`.
- New `agy-rescue` modes `transcribe` and `media`. 15 commands total.

## [0.6.9] — 2026-06-19

### Added

- **`/agy:notebook` groups one-page documents to save calls/quota.** When a folder has ≥3 single-page
  short one-page text documents, they are summarised together in a few
  `notebook-group` calls (batches of 8) instead of one call each — one combined summary lists each
  doc with its number, date and a one-line synthesis. Substantive and scanned documents are still
  summarised individually. New `agy-rescue` MODE: `notebook-group`.

### Notes

- **`/agy:notebook` prompt-via-stdin (roadmap #7) was evaluated and dropped.** `agy --print` requires
  the prompt as an argument and does not read it from stdin (a piped prompt with no arg exits 2), so
  there is no clean stdin path without breaking every mode's invocation. The write_file contract
  already keeps document *content* out of the process args; the prompt strings are not sensitive.

## [0.6.8] — 2026-06-19

### Fixed

- **`/agy:notebook` no longer chokes on a single very large scanned PDF.** A scanned (vision) PDF
  over ~20 pages is now split into 15-page sub-PDF chunks (`_chunks/`), each summarized in its own
  agy vision call — previously a 100+ page scan was sent as one call and timed out. Text-layer PDFs
  are unaffected (compact enough for a single call). Verified on a 184-page document → 13 chunks.

## [0.6.7] — 2026-06-19

NotebookLM corpus Q&A + two extra briefing artifacts.

### Added

- **`/agy:notebook-ask <folder> | <question>` — chat over a notebook corpus.** Answers a question
  from the per-document summaries built by `/agy:notebook` (never re-reading the originals), **with
  inline citations** to the source documents. Cheap (reads only the small `*.resumen.md`). Requires
  the corpus to exist; saves a Q&A trail under `docs/agy/notebook/<folder>/_respuestas/`.
- **`/agy:notebook` now also emits `TIMELINE.md` and `ENTIDADES.md`** alongside `INDEX.md` and
  `RESUMEN_MAESTRO.md`: a standalone chronological timeline, and extracted entities grouped as
  Personas, Organizaciones, Montos, Fechas and Referencias — each with
  the document where it appears. NotebookLM-style briefing artifacts, grounded only in the summaries.

## [0.6.6] — 2026-06-19

Model control + an incremental, model-routed `/agy:notebook`.

### Added

- **`/agy:model [alias|"label"]` — show or switch the agy model.** Writes the model label into
  `~/.gemini/antigravity-cli/settings.json` (the reliable lever — the `--model` CLI flag silently
  falls back to the default on an unknown id). No agy call, no reinstall; takes effect immediately.
  Stable aliases (`flash-low`, `pro`, `pro-high`, `sonnet`, `opus`, `gpt-oss`, …) in
  `config/model-map.json`; also accepts a full quoted label verbatim. Warns when agy ignores a label
  (wrong string for the account → verify against the TUI "Switch Model" list).
- **`/agy:notebook` — incremental cache.** Re-running the same folder + objective now only
  re-summarizes new or changed documents (cache key = size + mtime + objective hash, in
  `_cache.tsv`). Changing the objective invalidates the whole cache (summaries are objective-driven).
- **`/agy:notebook` — automatic model routing.** The per-document sweep runs on `Gemini 3.5 Flash
  (Low)` (fast/cheap), the final synthesis on `Gemini 3.1 Pro (Low)` (quality where it matters), and
  the user's original model is restored afterward. Best-effort: an unavailable label degrades to
  agy's default, harmlessly.

## [0.6.5] — 2026-06-19

`/agy:notebook` throughput + a model-selection note.

### Changed

- **`/agy:notebook` Phase 1 now fans out up to 10 documents per wave with rate-limit-aware retry**
  (was 3-4). agy is throttled per minute by the Antigravity account tier (~10 RPM free, higher on
  Pro/Ultra), so a wide wave is treated as best-effort: docs that come back without an output file
  are assumed rate-limited (429), not failed, and are re-dispatched in up to 2 retry rounds with a
  ~60s backoff (lets the per-minute quota reset) before being stubbed as `no_procesado`. This is the
  standard batch-LLM pattern (concurrency cap + backoff) rather than blind parallelism.

### Added

- **Model-selection note in `/agy:notebook`.** The per-document summaries don't need deep reasoning,
  so a low-effort model speeds up (and cheapens) the whole sweep. agy honors the model picked in its
  TUI (`agy` → "Switch Model"), which persists to `~/.gemini/antigravity-cli/settings.json`
  (`"model": "..."`) and applies to `--print` automatically — no per-call `--model` flag needed.
  `Gemini 3.5 Flash (Low)` is a good default for the sweep. (Note: agy's `--model <id>` flag silently
  falls back to the default when the id isn't in the account's known-model list, so the TUI selection
  is the reliable way to switch.)

## [0.6.4] — 2026-06-19

Adds a local NotebookLM and corrects the setup health-check's auth diagnosis.

### Added

- **`/agy:notebook <folder> | <objective>` — a local replacement for NotebookLM.** Sweeps every
  supported document in a folder (PDF with a text layer, scanned PDF, image, docx) and produces:
  one objective-driven Markdown **summary per document** (frontmatter: tipo, numero_gde, fecha,
  emisor, `relevancia` 0-100), a **`INDEX.md`** ranking the documents by relevance to the
  objective, and a cited **`RESUMEN_MAESTRO.md`** synthesis (answer-to-objective + timeline +
  conclusion). All heavy reading is offloaded to agy — the orchestrating agent only reads the two
  small final files. Output in `docs/agy/notebook/<folder>/`.
  - **Hybrid text/vision**: PDFs with a real text layer are pre-extracted and summarized as text
    (faster/cheaper); scanned PDFs and images go through agy's multimodal OCR. Decided per document.
  - **One document per agy call** (large multimodal batches time out), **3-4 concurrent** per
    batch; a document that fails/times out is recorded as `no_procesado` and the sweep continues.
  - New `agy-rescue` modes `notebook` (per-document summary) and `notebook-index` (index + master
    synthesis), following the existing write_file / issue-#76 discipline.

### Fixed

- **`/agy:setup` no longer raises a false "you must re-login" alarm.** The agy log emits
  `"You are not logged into Antigravity"`, `getting token source`, `FetchAvailableModels`,
  `loadCodeAssistResponse`, `userInfo` and `Skipping telemetry` lines from **secondary** auth
  scopes **even on a fully successful run** (verified 2026-06-19 — agy wrote its output file while
  emitting all of them). Setup now tests with a real `write_file` ping and treats those lines as
  non-fatal noise; it reports a genuine sign-in problem only when the output file is missing AND a
  real sign-in line appears, otherwise distinguishing timeout/task-size from auth.

## [0.6.3] — 2026-06-07

Patch release from a full end-to-end test pass of all 10 commands on agy 1.0.6. All commands verified working (research, report, ask, review, rescue, record, scrape, doc-to-md, design-review, setup — `review` correctly flagged two seeded bugs in a test diff). One real bug found and fixed.

### Fixed

- **Transcript recovery resolved the conversation id unreliably.** The v0.6.1/0.6.2 recovery (issue #76 Plan B) looked up the conversation id in `cache/last_conversations.json[cwd]` first — but that file is written with a delay and, on agy 1.0.6, frequently does NOT contain an entry for the invoking cwd at all, so an immediate post-exit recovery returned empty (the response was on disk the whole time). Recovery now resolves the id from the **cli log** (`Print mode: conversation=<cid>`, written immediately) first, then the most-recently-modified `brain/<cid>` dir, and only falls back to `last_conversations.json[cwd]` last. Verified: log-based recovery returns the response immediately where the cwd lookup returned empty.

### Notes

- No behavior change to any command's happy path — this only hardens the fallback that fires when `agy --print` drops stdout (still the common case on 1.0.6).

[0.6.3]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.6.3

## [0.6.2] — 2026-06-07

Reliability + distribution release: fixes the agy stdin-hang, makes the `/agy:report` infographics pipeline dependable, hardens research against forward-dating, and ships the plugin to npm. Driven by hands-on end-to-end testing on agy 1.0.6.

### Fixed

- **agy `--print` stdin-hang in subprocess/background contexts.** When stdin is inherited/open (the default for any subprocess, and always for background runs), `agy --print` blocks forever waiting on a TTY — the log file is created but stays empty and `--print-timeout` does NOT bound it. Confirmed on agy 1.0.6; matches reports from @dontcallmejames / @iwata-1116 on upstream issue #76. **Fix:** every `agy --print` invocation in the `agy-rescue` subagent now closes stdin with `< /dev/null` (PowerShell equivalent `$proc.StandardInput.Close()`), and the rule is documented prominently in the invocation contract. Without this, the v0.6.1 transcript recovery couldn't help — agy never ran.
- **`/agy:report` referenced images it never created (broken `<img>`).** agy's native `generate_image` is unreliable in headless mode (emits JPEG bytes under a `.png` name, or skips generation), and the assets path was inconsistent (`<WRITE_FILE>.assets` vs the `.assets` dir agy actually used). Standardized `ASSETS_DIR` (output with `.html` → `.assets`) and a deterministic slug, and added an **assets-existence check** after generation that verifies every `<img src>` resolves to a real file and reports any missing slugs instead of silently shipping broken images.
- **Research forward-dating / overstated specifics.** agy web research asserted unconfirmed hard facts (e.g. release dates, version numbers, parameter counts) unprompted. Added an anti-forward-dating rule to all three research intensity templates: never state dates/versions/specs unless a cited source supports them; never present unreleased items as shipped; mark the rest `[UNVERIFIED]`.

### Added

- **`/agy:report --images native|external|none`** — controls how `![generate: ...]` cues become images:
  - `native` (default): agy generates them (zero setup, flaky quality; missing ones now reported).
  - `external` (**recommended for brand-grade infographics**): pre-generate the PNGs with a dedicated image model — e.g. **Nano Banana 2** (`gemini_image_generation`, `gemini-3.1-flash-image-preview`) — into the assets dir using the slug convention; agy just references them. Deterministic, real PNGs, full brand control.
  - `none`: styled placeholder figures, never broken images.
- **npm distribution.** The plugin is now publishable to npm as [`antigravity-plugin-cc`](https://www.npmjs.com/package/antigravity-plugin-cc) with a `package.json` (files allowlist) and a `bin` helper — `npx antigravity-plugin-cc` prints the Claude Code install commands. The plugin is markdown+JSON with no runtime, so npm is a versioned discovery/mirror channel; the canonical install remains the git marketplace.

### Notes

- The intended document workflow is now first-class: **you write a clean source `.md` with `![generate: <description>]` cues, run `/agy:report` (with `--images external` for polished infographics), and agy turns it into a branded HTML document.**
- The upstream empty-stdout bug (#76) is still unfixed as of agy 1.0.6 — these remain wrapper-side mitigations, not a fix.
- Rendering tip: opening report HTML via `file://` can block local `<img>` loading; serve the folder with `python -m http.server` and open over `http://`.

[0.6.2]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.6.2

## [0.6.1] — 2026-06-06

Reliability release: full recovery path for the upstream empty-stdout bug (issue #76), driven by community findings on the upstream issue thread (confirmed through agy 1.0.5).

### Added

- **Transcript recovery (Plan B) for issue #76.** When `agy --print` exits 0 with empty stdout and no output file, the `agy-rescue` subagent now recovers the dropped response from the on-disk transcript — `cache/last_conversations.json[cwd]` → `brain/<cid>/.system_generated/logs/transcript.jsonl` → last `PLANNER_RESPONSE.content`. Confirmed by three independent reporters on the upstream thread. This makes `/agy:rescue` (which has no `write_file` instruction) usable in subprocess mode for the first time, and acts as a safety net for every other mode if the `write_file` workaround misses.
- **Headless auth-timeout detection (new agy 1.0.5 failure mode).** A distinct failure where silent auth times out before generation (`keyringAuth: timed out` → `Print mode: auth timed out`) — the model never runs, so nothing is recoverable. The subagent now detects this in the log and returns an actionable re-auth message instead of a silent empty result, and does NOT waste a retry on it.
- **Three-way failure-mode triage table** in the subagent (`text_drip length=N` → #76 recover; `rename … Access is denied` → #217 retry; `auth timed out` → re-auth) so the right recovery runs for each.

### Changed

- **`--print-timeout` documented as non-binding.** Community reports confirm agy runs past the stated `--print-timeout` (e.g. 15s requested, exited ~41s). The subagent now treats it as a hint and instructs setting the `Bash` tool's own timeout with headroom; it also warns that `high` research (`20m0s`) exceeds the `Bash` tool's 10m ceiling and should run in the background.

### Fixed

- **Corrected the stale `--model` claim.** Prior docs (since v0.1.1) stated `--model` does not exist in `agy` 1.0.x. That was true for 1.0.0/1.0.1 but **agy 1.0.5+ accepts `--model "<name>"`** (community-confirmed). The plugin still defaults to omitting `--model` for cross-version safety, but `SKILL.md` and the subagent no longer assert the flag is universally invalid.

### Notes

- Source for all of the above: the upstream issue thread [google-antigravity/antigravity-cli#76](https://github.com/google-antigravity/antigravity-cli/issues/76). The empty-stdout bug remains **unfixed upstream** as of agy 1.0.5 (2026-06-05); these are wrapper-side mitigations, not a fix.
- Transcript recovery keys by **cwd** and agy emits no stable run id, so it is fragile under concurrent agy runs from the same directory. Fine for normal one-call-at-a-time usage; not safe for parallel fan-out from the same cwd.

[0.6.1]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.6.1

## [0.6.0] — 2026-05-29

Feature release: branded HTML report generation via the TRAID Design System, two quick-use commands, and Windows reliability hardening.

### Added

- **`/agy:report <markdown> [--template <id>] [--output <path>]`** — generate a publication-grade, self-contained HTML report from a markdown source using the TRAID Design System catalog of 5 canonical templates (`traid-dark`, `traid-light`, `stripe-press`, `notion-docs`, `magazine`). Two-phase flow: agy analyzes the source and recommends 1–3 templates, you pick (or pass `--template` to skip analysis), then agy generates the final branded HTML — inlining Imagen-generated images for any `![generate: ...]` cues. Output to `docs/agy/reports/YYYY-MM-DD-<slug>.html`.
- **`/agy:ask <prompt>`** — one-shot quick prompt to agy; returns the response verbatim, no `docs/` persistence (uses the temp-file write-to-file workaround for issue #76).
- **`/agy:review [focus]`** — sends the current `git diff` to agy for code review with optional focus text.
- **TRAID Design System** — 5 canonical HTML templates with full palette / typography / component specs, embedded in the `report-analyze` catalog so agy can match content to the right template.

### Changed

- **`agy-rescue` subagent gained four new mode branches** (`ask`, `review`, `report-analyze`, `report-generate`) — now 10 modes total.
- **Windows rename bug (issue #217) hardening** — the output-file existence check now does a `sleep 2 && agy …` backoff retry (was an immediate retry that lost the same Defender scan race), and the pre-flight `.tmp` sweep gained a PowerShell fallback for non-Git-Bash shells. Root cause: Windows Defender real-time scan holds a handle on the freshly-written conversation `.tmp` at `MoveFileEx` time. Non-fatal for report/research flows (deliverable writes to a different path via `write_file` + `--add-dir`); the permanent fix is a Defender exclusion on the conversations dir.
- **Marketplace and plugin descriptions / keywords** updated to list ten commands and the design-system capability.

[0.6.0]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.6.0

## [0.3.1] — 2026-05-25

Hotfix release: plugin manifest schema fix.

### Fixed

- **`repository` field in `plugin.json` was an OBJECT, but Claude Code's plugin manifest schema requires it to be a STRING.** This caused Claude Code's plugin loader to reject the plugin with `Validation errors: repository: Invalid input: expected string, received object` and silently skip loading all seven slash commands, even though `/plugin install` appeared to succeed and the file structure was correct. The plugin had this bug from v0.1.0 onwards — present in every previous release — but only surfaced when a fresh Claude Code install attempted strict schema validation. Symptoms before the fix: `/plugin marketplace add` + `/plugin install` complete without errors, but `/antigravity:` never autocompletes any command.

### Notes

- The npm `package.json` convention is `repository: { type, url }`. The Claude Code plugin manifest convention is `repository: "<url-string>"`. Different schemas — don't reuse npm habits.
- If you were on any prior version (0.1.x, 0.2.0, 0.3.0) and the commands never showed up, this is why. Upgrade to 0.3.1 to fix.

[0.3.1]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.3.1

## [0.3.0] — 2026-05-25

Feature release: three new slash commands that exercise agy's lesser-known agentic capabilities — structured web scraping, multimodal document conversion, and visual/UX design review.

### Added

- **`/agy:scrape <url> [schema|description] [--json]`** — structured data extraction from a single URL. Pass the URL + optional comma-separated field names (e.g., `price, title, stock`) OR natural-language description (e.g., `extract product info`). Output to `docs/agy/scrapes/YYYY-MM-DD-<slug>.{md,json}`. Uses agy's `read_url` for static HTML and the browser subagent for JS-heavy SPAs. Saves time over hand-writing a scraper for one-off extractions; not a replacement for production scraping pipelines (use Playwright + n8n for that).
- **`/agy:doc-to-md <file> [focus instructions]`** — multimodal document → clean Markdown conversion. Accepts PDF, docx, image (PNG/JPG/WebP), and HTML. Preserves tables, lists, headings, code blocks. Inline images become described placeholders. Output to `docs/agy/converted/YYYY-MM-DD-<slug>.md`. Especially useful for ingesting RFPs, specs, or proposal PDFs that arrive from clients.
- **`/agy:design-review <url> [focus]`** — UX/visual audit of a URL. Captures desktop (1440×900) + mobile (375×667) screenshots and scores the page across 10 dimensions (hierarchy, typography, color, spacing, interactivity, brand, a11y, Nielsen heuristics, responsive behavior, competitive context). Ends with 3 strengths, 3 highest-leverage improvements, and an overall /10 score. Output to `docs/agy/design-reviews/YYYY-MM-DD-<slug>.md`. Validated on TRAID ERP login during development — output quality is on par with junior UX reviewer output.

### Changed

- **`agy-rescue` subagent gained three new mode branches** (`scrape`, `doc-to-md`, `design-review`) following the same write-to-file pattern as v0.2.0's `record` and `research` modes. The subagent description was updated to mention the new modes.
- **Timeouts tuned per mode:**
  - `scrape`: 5m (static) — 10m (JS-heavy SPA)
  - `doc-to-md`: 8m (small) — 15m (large >20 pages)
  - `design-review`: 12m (multi-viewport + multimodal analysis)
- **Marketplace and plugin descriptions** updated to list seven commands instead of four.
- **Keywords** expanded with `web-scraping`, `structured-extraction`, `pdf-to-markdown`, `docx-to-markdown`, `multimodal-conversion`, `design-review`, `ux-audit`, `visual-audit` for discoverability.

### Notes

- All three new commands use the same `--add-dir <CWD>` + `write_file` pattern from v0.2.0 to bypass upstream issue #76 (empty stdout in `--print` mode). No new workarounds needed.
- `/agy:scrape` is for ad-hoc extractions and exploration. For production scraping pipelines, use a deterministic stack (Playwright + n8n + Postgres).
- `/agy:doc-to-md` sends document contents to Google's Gemini servers. For data-residency-sensitive content (NDAs, internal contracts), prefer a Vertex AI ADC pipeline instead.
- `/agy:design-review` uses an isolated Chrome profile — no shared cookies. Login-protected pages must include credentials in the focus text (those credentials end up in the prompt/transcript).

[0.3.0]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.3.0

## [0.2.0] — 2026-05-25

Feature release: browser walkthrough recording + critical flag-order fix.

### Added

- **`/agy:record <url> [steps in natural language]`** — record a browser walkthrough of any URL using agy's browser subagent. Generates a `.webm` video, initial + final screenshots, and a markdown report describing what was observed. Output saved to `docs/agy/recordings/YYYY-MM-DD-<host-path-slug>.{webm,mp4,png,md}` (relative to the current project). Default exploratory walkthrough (load → screenshot → scroll → click prominent CTA → screenshot) when no steps are given; full natural-language control otherwise.
- **Automatic MP4 conversion via ffmpeg.** After recording, the subagent detects ffmpeg (`command -v ffmpeg` / `where ffmpeg`) and converts `.webm` → `.mp4` (H.264, CRF 23, audio stripped because recordings are silent). If ffmpeg is missing, the `.webm` is preserved and an install hint is appended to the report (no hard failure). Works on Windows (`winget install Gyan.FFmpeg`), macOS (`brew install ffmpeg`), and Linux (`apt install ffmpeg`).
- **`MODE: record` branch in the `agy-rescue` subagent.** Reuses the same forwarder, no new agent. Centralizes recording orchestration alongside `rescue` / `research` / `setup`.

### Fixed

- **Critical flag-order bug: `--print` must be the LAST flag before the prompt.** The Go flag parser treats `--print` as a value-taking flag and consumes the next token as its value. The v0.1.x contract documented `agy --print --dangerously-skip-permissions ...` which parses as `--print="--dangerously-skip-permissions"` — meaning agy treated the literal string `--dangerously-skip-permissions` as the user's prompt and responded to that instead of the intended task. The v0.2.0 contract reorders flags to `agy --dangerously-skip-permissions [--add-dir <CWD>] --print-timeout <T> [--continue] --print "<PROMPT>"` and documents this gotcha prominently in the subagent.
- **Workaround for upstream issue #76 (empty stdout in `--print` mode).** `agy` v1.0.x has a confirmed bug where, when stdout is not a TTY, the binary exits 0 but writes zero bytes to stdout even though the model generated a full response (confirmed via `text_drip.go` log entries showing `length=2504`+ characters streamed internally). The v0.2.0 subagent works around this by instructing agy *in the prompt itself* to write its output via `write_file` to a known path, then reading that file from the calling agent. stdout is now used only as a "did the process exit cleanly" signal.

### Changed

- **`--add-dir <CWD>` is now passed by default in `record` and `research` modes** so agy's `write_file` tool has permission to write into the calling project's directory (e.g., `docs/agy/research/`, `docs/agy/recordings/`). Without this flag, agy can only write to `~/.gemini/antigravity-cli/scratch/` and the output never lands in your repo.
- **Subagent description updated** to mention recording as one of its modes.
- **Marketplace and plugin descriptions** updated to list four commands instead of three.

### Notes

- Recordings have **no audio.** If narration is required, pair with a separate TTS pipeline (e.g., Google Chirp, ElevenLabs, or a Vertex AI skill) and mux with ffmpeg.
- agy uses an **isolated Chrome profile**. Cookies, sessions, and extensions from the user's main Chrome are not available. Demos that require login must include credentials in the steps (which then appear in the prompt and conversation transcript) or be recorded on public/demo URLs.
- The MP4 step uses `-an` to strip the empty audio track that some players (older Slack desktop, PowerPoint < 2019) refuse to play even when audio is silent.

[0.2.0]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.2.0

## [0.1.1] — 2026-05-24

Bugfix release.

### Fixed

- **Removed `--model` flag from `/agy:rescue` and `/agy:research`.** The `agy` CLI 1.0.x does not accept `--model` — passing it makes the binary exit with `flags provided but not defined: -model`. Earlier versions of this plugin documented and parsed this flag, which meant any user who tried `--model pro` or similar got an immediate hard failure. Model selection is now delegated entirely to `agy`'s internal default (Gemini 3.5 Flash for most cases).
- **Setup ping no longer enters tool-call loops.** `agy` defaults to an agentic mode that calls `ListDir`, `Search`, `ReadFile` even for trivial prompts. The previous `/agy:setup` ping was `"ping — reply with only the word 'pong'"`, which the model interpreted as license to explore the workspace, consume the entire `--print-timeout`, and return exit 0 with empty stdout — indistinguishable from "OAuth missing". v0.1.1 sends an explicit "do not use any tools, do not search, do not read files" instruction in the ping prompt.

### Changed

- **Health-check troubleshooting now distinguishes "tool-call timeout" from "OAuth missing".** Before, any silent failure was attributed to missing Google OAuth. The real root cause for many users is the agentic-loop timeout above. README FAQ and `commands/setup.md` now document both, with `~/.gemini/antigravity-cli/installation_id` as the diagnostic check for OAuth.
- **Removed the "Multi-model support" README section.** It documented model identifiers (`gemini-3.5-pro`, `claude-opus-4-6-thinking`, etc.) that are not selectable from the CLI in 1.0.x. The section will return when upstream `agy` exposes a model flag.

### Notes

- `agy` 1.0.x has model selection inside its interactive settings, not on the command line. If you need a specific model, change it via `agy` directly.
- This patch is non-breaking: the slash commands keep the same names. Anyone passing `--model X` will now get the model `agy` picks by default instead of a hard failure.

[0.1.1]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.1.1

## [0.1.0] — 2026-05-23

Initial public release.

### Added

- `/agy:research <topic> [--intensity low|medium|high]` — deep web research via Antigravity CLI (`agy`) with output saved to `docs/agy/research/YYYY-MM-DD-<slug>.md`. Three intensity tiers with different prompt templates, source counts, models, and timeouts.
- `/agy:rescue [--resume|--fresh] [--model <name>]` — delegate a coding/diagnosis task to `agy` and return its output verbatim.
- `/agy:setup` — health check for the `agy` binary and Google OAuth state.
- `agy-rescue` subagent — thin forwarder around `agy --print`. No companion runtime, no Node.js.
- `agy-prompting` internal skill — prompting tips for Gemini 3.x.
- Multi-model support: any model `agy` exposes (Gemini 3.5/3.1 Pro and Flash, Claude Sonnet 4.6 Thinking, Claude Opus 4.6 Thinking, GPT-OSS 120B) can be passed via `--model`.
- `llms.txt` for LLM-friendly discovery.
- `CITATION.cff` for academic and tool-citation use.
- `examples/sample-research-medium.md` showing what `/agy:research` output looks like before installing.

### Context

This plugin was released ahead of the **18 June 2026** Gemini CLI deprecation cutoff. Users of [`abiswas97/gemini-plugin-cc`](https://github.com/abiswas97/gemini-plugin-cc) (which depends on the deprecated `gemini-cli`) can use this as a migration target.

[0.1.0]: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/tag/v0.1.0

## Why this patch came so fast after 0.1.0

Both gotchas above were discovered the day after v0.1.0 shipped, while using the plugin against `agy.exe` v1.0.1 on Windows. They were not caught pre-release because the local development copy of the subagent had the same bugs and exhibited the same silent failure. See engram memory #657 in the source notes for the original diagnostic trail.
