# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.8] — 2026-06-19

### Fixed

- **`/agy:notebook` no longer chokes on a single very large scanned PDF.** A scanned (vision) PDF
  over ~20 pages is now split into 15-page sub-PDF chunks (`_chunks/`), each summarized in its own
  agy vision call — previously a 100+ page scan was sent as one call and timed out. Text-layer PDFs
  are unaffected (compact enough for a single call). Verified on a 184-page expediente → 13 chunks.

## [0.6.7] — 2026-06-19

NotebookLM corpus Q&A + two extra briefing artifacts.

### Added

- **`/agy:notebook-ask <folder> | <question>` — chat over a notebook corpus.** Answers a question
  from the per-document summaries built by `/agy:notebook` (never re-reading the originals), **with
  inline citations** to the source documents. Cheap (reads only the small `*.resumen.md`). Requires
  the corpus to exist; saves a Q&A trail under `docs/agy/notebook/<folder>/_respuestas/`.
- **`/agy:notebook` now also emits `TIMELINE.md` and `ENTIDADES.md`** alongside `INDEX.md` and
  `RESUMEN_MAESTRO.md`: a standalone chronological timeline, and extracted entities grouped as
  Personas (with DNI/CUIL), Montos, Expedientes/resoluciones, and Escuelas/organismos — each with
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
