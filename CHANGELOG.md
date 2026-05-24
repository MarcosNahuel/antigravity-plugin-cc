# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
