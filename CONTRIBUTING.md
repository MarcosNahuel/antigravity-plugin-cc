# Contributing

Thanks for considering a contribution! This plugin is intentionally small and dependency-free, so the bar for "is it a good fit?" is straightforward:

- It must be useful to a typical Claude Code user invoking `agy`.
- It must not introduce a runtime dependency (no Node.js, no Python, no compiled binaries beyond `agy` itself).
- It must work on Windows, macOS, and Linux.

## Quick start for development

1. Fork and clone this repo.
2. Edit files under `plugins/antigravity/`.
3. Test locally by pointing your Claude Code marketplace registry at your clone, or by symlinking `plugins/antigravity/` into `~/.claude/plugins/marketplaces/local/plugins/`.
4. Run `/agy:setup` to confirm nothing broke.
5. Open a PR.

## What we'd love help with

- New slash commands: `/agy:review`, `/agy:adversarial-research`, `/agy:fact-check`, `/agy:compare`.
- Output directory configurable via env var (`AGY_RESEARCH_DIR`).
- CI mode (machine-readable JSON output from `/agy:research`).
- Cost estimate per intensity in `/agy:setup`.
- More prompt templates in `agents/agy-rescue.md` — better prompts move the needle more than more code.

## What we'll likely say no to

- Adding a Node.js or Python companion runtime. The whole point of this plugin is that it's a thin Bash forwarder.
- Wrapping `agy` features that `agy` already exposes well (e.g., re-implementing `agy --conversation <id>` management).
- Hard dependencies on Windows-only or Unix-only tooling.

## Filing issues

Use the issue templates. For bugs, paste the output of `/agy:setup` and the exact command you ran.

## Code style

Markdown files use 2-space indentation in front-matter, no trailing whitespace, LF line endings (the `.gitattributes` file enforces this when added). JSON files use 2-space indentation and trailing newlines.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
