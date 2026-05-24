# Antigravity Plugin for Claude Code

> **Deep web research, code rescue, and task delegation from Claude Code to Google Antigravity (`agy`) — the CLI that replaced `gemini-cli` in 2026.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-7c3aed)](https://docs.claude.com/en/docs/claude-code/plugins)
[![Antigravity CLI](https://img.shields.io/badge/Google-Antigravity%20CLI-4285F4)](https://antigravity.google)
[![Made with agy](https://img.shields.io/badge/Made%20with-agy-34a853)](https://github.com/MarcosNahuel/antigravity-plugin-cc)

**TL;DR** — Type `/agy:research <topic>` inside Claude Code. Get a structured markdown report grounded in real web search results from Gemini 3.x, saved to `docs/agy/research/`. No Node.js runtime. No MCP setup gymnastics. Three slash commands. ~7 files of plugin code.

[**Install**](#install) · [**Slash commands**](#slash-commands) · [**Examples**](#usage-examples) · [**FAQ**](#faq) · [**Compare to alternatives**](#compared-to-alternatives)

---

## What is this?

**A Claude Code plugin that lets you delegate work to Google Antigravity CLI (`agy`) without leaving Claude Code.**

- **Antigravity CLI** (`agy`) is Google's official agentic command-line assistant — the successor to `gemini-cli`, rewritten in Go for speed, with native web search grounding built into Gemini 3.x.
- **Claude Code** is Anthropic's CLI for AI-assisted software engineering.
- This plugin **bridges the two**: from inside Claude Code, you invoke `/agy:research`, `/agy:rescue`, or `/agy:setup` and the request gets handed to `agy --print` via a thin Bash forwarder.

The killer use case is **deep web research with citations** — Claude reasons over your repo, `agy` reasons over the live web. Each tool does what it's best at.

---

## When should I use this plugin?

| If you are… | This plugin helps because… |
|---|---|
| A Claude Code user who needs **fresh information from the web** with verifiable URLs | `/agy:research` returns a structured markdown report with cited sources, written to a file you can edit, review, and commit. |
| Already using `agy` from the terminal but **switching between two CLIs** breaks your flow | You stay in Claude Code for code work. `/agy:*` handles everything that needs `agy`. |
| Evaluating a new library, framework, or service and need a **Tech Radar–style report** | `/agy:research --intensity high` pulls 15+ primary sources (papers, official docs, repos), triangulates them, and emits a comparative analysis with confidence levels. |
| Building a **proposal, RFP response, or technical pitch** | `/agy:research --intensity medium` produces an 8–12 source executive summary you can paste into a doc with citations intact. |
| Migrating from the old `gemini-plugin-cc` (built on the deprecated `gemini-cli`) | This plugin uses the new `agy` CLI and has no Node.js companion runtime — drop-in replacement for research workflows. |

---

## Slash commands

| Command | What it does |
|---|---|
| `/agy:research <topic> [--intensity low\|medium\|high]` | **Deep web research.** Saves to `docs/agy/research/YYYY-MM-DD-<slug>.md`. Default: `medium`. |
| `/agy:rescue [--resume\|--fresh] [--model flash\|pro\|flash-lite] <task>` | **Delegate** a coding, debugging, or implementation task to `agy` and return its output verbatim. |
| `/agy:setup` | **Health check** — resolves the binary, reads version, runs a 30 s ping. |

### Research intensity matrix

| Intensity | Default Gemini model | Timeout | Source target | Output sections |
|---|---|---|---|---|
| `low` | `gemini-3.5-flash` | 3 min | 3–5 trusted sources | TL;DR · Sources |
| `medium` | `gemini-3.5-flash` | 8 min | 8–12 triangulated | Executive summary · Key findings · Analysis · References |
| `high` | `gemini-3.5-pro` | 20 min | 15+ primary sources | TL;DR · Context · Findings · Comparisons · Risks · Evidence gaps · Conclusion · References |

Override the model with `--model flash`, `--model pro`, or `--model flash-lite` at any intensity.

---

## Install

### 1. Prerequisites

You need both CLIs installed and authenticated:

**Claude Code** ([install guide](https://docs.claude.com/en/docs/claude-code/overview)):

```bash
npm install -g @anthropic-ai/claude-code
```

**Antigravity CLI** (`agy`):

```powershell
# Windows (PowerShell)
irm https://antigravity.google/cli/install.ps1 | iex
```

```bash
# macOS / Linux
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Then run `agy` once in a fresh shell to complete Google OAuth login. After that the CLI is good for non-interactive use via `--print`.

### 2. Add the plugin

From inside Claude Code:

```
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
```

### 3. Verify

```
/agy:setup
```

You should see the binary path, version, and a `pong` from a 30-second test ping.

---

## Usage examples

### Quick fact check — `low` intensity

```
/agy:research n8n self-hosted telemetry environment variables --intensity low
```

→ 3–5 bullet TL;DR with official-doc URLs, in under 3 minutes. Saved to `docs/agy/research/2026-05-23-n8n-self-hosted-telemetry-environment-variables.md`.

### Tech radar evaluation — `medium` intensity (default)

```
/agy:research feature flags postgres vs redis tradeoffs 2026
```

→ Executive summary · 8–12 triangulated sources · analysis · numbered references with dates.

### Strategic decision — `high` intensity

```
/agy:research modular ERP architecture for MercadoLibre sellers in Latam --intensity high
```

→ 15+ primary sources · comparative tables · counterarguments · evidence gaps · confidence-rated conclusion. ~20 minutes.

### Code rescue / task delegation

```
/agy:rescue debug why my drizzle migration drops the foreign key constraint on user_id
```

→ Hands the task to `agy` with `--dangerously-skip-permissions`. `agy` reads files, proposes edits, returns its output. You see it verbatim.

### Resume the previous `agy` conversation

```
/agy:rescue --resume apply the top fix you suggested
```

→ Equivalent to `agy --print --continue "apply the top fix you suggested"`. Useful for tight iteration loops.

---

## How it works under the hood

```
You → Claude Code → /agy:research <topic>
                        ↓
          antigravity:agy-rescue subagent
                        ↓
          Bash → agy --print --print-timeout <N> --model <M> "<wrapped-prompt>"
                        ↓
          stdout → Write → docs/agy/research/YYYY-MM-DD-<slug>.md
                        ↓
          path + TL;DR shown to you in Claude Code
```

The subagent is a **thin forwarder** — there is no companion runtime, no Agent Client Protocol (ACP) handling, no JavaScript. It picks the right prompt template per intensity, computes the timeout and model, shells out, captures stdout, writes the file, and returns.

This is intentionally simpler than [`abiswas97/gemini-plugin-cc`](https://github.com/abiswas97/gemini-plugin-cc) (~800 LoC of Node.js companion) because `agy --print` already handles the conversation lifecycle natively (`--continue`, `--conversation <id>`, `--print-timeout`).

---

## File layout

```
.
├── .claude-plugin/
│   └── marketplace.json            # marketplace manifest (root)
├── plugins/
│   └── antigravity/
│       ├── .claude-plugin/
│       │   └── plugin.json         # plugin manifest
│       ├── agents/
│       │   └── agy-rescue.md       # thin forwarder subagent
│       ├── commands/
│       │   ├── rescue.md           # /agy:rescue
│       │   ├── research.md         # /agy:research
│       │   └── setup.md            # /agy:setup
│       └── skills/
│           └── agy-prompting/
│               └── SKILL.md        # prompting tips for Gemini 3.x
├── llms.txt                        # LLM-friendly index (GEO)
├── CITATION.cff                    # citation metadata
├── LICENSE                         # MIT
└── README.md
```

---

## Compared to alternatives

| | This plugin | [`gemini-plugin-cc`](https://github.com/abiswas97/gemini-plugin-cc) | Claude's built-in `WebSearch` tool | Perplexity API |
|---|---|---|---|---|
| **CLI it wraps** | Antigravity (`agy`) — current | Gemini CLI — deprecated | None (native to Claude) | None (REST API) |
| **Runtime overhead** | None — direct Bash to `agy` | ~800 LoC Node.js companion | None | HTTP calls |
| **Web search engine** | Gemini 3.x with native grounding | Gemini 2.x via Gemini CLI | Brave (via Anthropic) | Perplexity Sonar |
| **Saves output to file** | ✅ `docs/agy/research/` by default | ❌ | ❌ | ❌ |
| **Intensity tiers** | ✅ low/medium/high | ❌ | ❌ | Some via model choice |
| **Code rescue / file edits** | ✅ via `/agy:rescue` | ✅ via `/gemini:rescue` | ❌ | ❌ |
| **Code review commands** | Not yet (roadmap) | ✅ `/gemini:review`, `/gemini:adversarial-review` | ❌ | ❌ |
| **Free tier** | Via Google's `agy` free quota | Via Gemini API free quota | Included in Claude Code | Paid |

**Rule of thumb:** Use Claude's `WebSearch` for quick lookups inside a Claude session. Use this plugin when you want **a saved, structured markdown report with citations** that lives in your repo and that you can iterate on.

---

## FAQ

### How is this different from just running `agy` in a separate terminal?

You don't lose your Claude Code context. The output of `/agy:research` lands as a file in your project — Claude can immediately read it, summarize it, or use it as input to the next step. Two terminals + copy-paste is not the same workflow.

### Does this require an API key?

No. `agy` uses your Google OAuth login (the same one you set up the first time you ran `agy` interactively). This plugin shells out to `agy --print` and inherits that auth.

### What models does it use?

Whatever `agy` exposes — at the time of writing, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, and `gemini-3.5-pro`. Defaults per intensity: `low`/`medium` → `flash`, `high` → `pro`. Override per call with `--model`.

### Where does the research output get saved?

`docs/agy/research/YYYY-MM-DD-<slug>.md`, relative to the directory where you ran the slash command. Each file gets a YAML frontmatter block with `title`, `intensity`, `model`, `created`, `sensitivity`, `source_tool`. You can commit these to your repo — they're plain markdown.

### Can I change the output directory?

Not via flag yet. It's on the roadmap. For now, edit `plugins/antigravity/commands/research.md` and change the `WRITE_FILE` path.

### Does it work on Windows?

Yes. The subagent resolves the `agy` binary in this order: `AGY_BIN` env var → `agy` on PATH → `${LOCALAPPDATA}/agy/bin/agy.exe`. Tested on Windows 11 with Claude Code.

### What if `/agy:setup` hangs?

The most likely cause is that `agy` has not completed Google OAuth yet. Open a regular terminal (not inside Claude Code) and run `agy` once — go through the browser login, then exit. After that, `agy --print` will run unattended.

### Does this plugin send my code anywhere?

For `/agy:rescue`, `agy` runs with `--dangerously-skip-permissions` so it can read and edit files in your repo. The data goes to Google's Gemini API per `agy`'s privacy policy — same as if you ran `agy` directly. For `/agy:research`, only the topic text and `agy`'s own web searches happen; your repo files are not sent.

### What's the difference between `/agy:research` and `/agy:rescue`?

`/agy:research` is **read-only**, web-focused, writes a markdown report to disk. `/agy:rescue` is **write-capable**, repo-focused, can edit your files. Different use cases, different prompts under the hood.

### Why not just use the official `agy mcp start` integration?

Two reasons:

1. The MCP integration exposes `agy` as a tool to Claude, but Claude decides when to call it. This plugin gives **you** explicit control via slash commands with structured prompts and intensity tiers.
2. The research-to-file workflow (`docs/agy/research/`) doesn't exist in the MCP setup. You'd build it yourself.

Both can coexist — they target different patterns.

### Can I use it without Claude Code (e.g., from Cursor, Windsurf, or another IDE)?

The plugin format is specific to Claude Code today. The prompt templates inside `plugins/antigravity/agents/agy-rescue.md` are reusable in any agent that can shell out to `agy --print`, though.

---

## Roadmap

- [ ] `/agy:review <files>` — code review of a path or diff
- [ ] `/agy:adversarial-review` — challenge-mode review (red-team approach, design tradeoffs, hidden assumptions)
- [ ] `/agy:adversarial-research <topic>` — research with explicit steelman + red-team framing
- [ ] `/agy:fact-check <claim>` — single-claim verification with citations
- [ ] `/agy:compare <A> vs <B>` — two-tool comparative report
- [ ] Configurable output directory (`AGY_RESEARCH_DIR` env var)
- [ ] CI mode (machine-readable JSON output)
- [ ] Cost estimate per intensity in the setup command
- [ ] `examples/` directory with real research outputs

PRs welcome. Open an issue first for anything bigger than a typo.

---

## Glossary

- **Antigravity CLI / `agy`** — Google's official agentic command-line assistant, written in Go, that replaced `gemini-cli` in 2026. Includes native web search grounding via Gemini 3.x. [Installer](https://antigravity.google/cli).
- **Claude Code** — Anthropic's official CLI for AI-assisted software engineering. Supports plugins, MCP servers, and subagents. [Docs](https://docs.claude.com/en/docs/claude-code/overview).
- **Claude Code plugin** — A folder with `.claude-plugin/plugin.json`, optional `commands/`, `agents/`, `skills/`, and `hooks/`. Installed via `/plugin install`. [Plugin docs](https://docs.claude.com/en/docs/claude-code/plugins).
- **Subagent** — A reusable agent definition in `agents/`. Can be invoked by Claude or by slash commands. This plugin uses a single `agy-rescue` subagent in three modes.
- **Slash command** — A custom `/<name>` shortcut defined in `commands/<name>.md`. This plugin ships `/agy:rescue`, `/agy:research`, `/agy:setup`.
- **`--dangerously-skip-permissions`** — `agy` flag that auto-approves all tool permission requests so it can run unattended. Required for `/agy:rescue` to be useful.
- **MCP** — Model Context Protocol. Standard for connecting LLM clients to tool servers. `agy mcp start` exposes `agy` as an MCP server; this plugin does NOT use that path and is independent of it.

---

## Cite this plugin

If this saved you work and you want to cite it (in a paper, blog post, talk), use:

```bibtex
@software{albornoz_antigravity_plugin_cc_2026,
  author = {Albornoz, Marcos Nahuel},
  title = {Antigravity Plugin for Claude Code},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/MarcosNahuel/antigravity-plugin-cc}
}
```

A machine-readable `CITATION.cff` is in the repo root.

---

## Author

Built by **Marcos Nahuel Albornoz** — co-founder & PM at [**TRAID**](https://traidai.com), an automation & AI agency for e-commerce in Latam and the US.

- GitHub: [@MarcosNahuel](https://github.com/MarcosNahuel)
- Email: [contact@traidai.com](mailto:contact@traidai.com)

If this plugin saves you time, a ⭐ on the repo is the best way to say thanks. Pull requests, issues, and feature ideas all welcome.

---

## License

[MIT](LICENSE) — do whatever you want, no warranty.

---

<sub>Keywords: claude code plugin, antigravity cli, agy cli, gemini 3.5, deep web research, llm research tool, agentic engineering, prompt engineering, claude code subagent, gemini grounding, claude code marketplace, research with citations, llm tool delegation, claude code anthropic.</sub>
