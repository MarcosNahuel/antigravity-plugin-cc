# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
