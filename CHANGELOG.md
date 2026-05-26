# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
