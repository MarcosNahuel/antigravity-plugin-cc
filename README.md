# antigravity-plugin-cc

> Use Google **Antigravity CLI (`agy`)** as a subagent inside **Claude Code** — for deep web research, code rescue, and task delegation.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-7c3aed)](https://docs.claude.com/en/docs/claude-code/plugins)
[![Antigravity](https://img.shields.io/badge/Google-Antigravity-4285F4)](https://antigravity.google)

A minimal, dependency-free Claude Code plugin that lets you hand off work to Google's `agy` CLI (Gemini 3.x with **native web search** and agentic tools) — without leaving your Claude Code session.

The killer feature: **`/agy:research`** runs deep web research at three intensity levels and saves the report to `docs/agy/research/` automatically, with frontmatter and structured citations.

---

## Why this plugin

You're already in Claude Code. Claude is great at reasoning over your repo. But for **fresh information from the web with verifiable citations**, Gemini 3.x via Antigravity is hard to beat — it has Google Search wired into the model with grounding.

This plugin gives you a one-shot escape hatch: stay in Claude, type `/agy:research <topic>`, get a structured markdown report with real URLs, dropped right into your project as a file.

No Node.js companion runtime. No ACP protocol gymnastics. Just three slash commands and a thin subagent that shells out to `agy --print`.

---

## Slash commands

| Command | What it does |
|---|---|
| `/agy:research <topic> [--intensity low\|medium\|high]` | Deep web research. Saves to `docs/agy/research/YYYY-MM-DD-<slug>.md`. Default intensity: `medium`. |
| `/agy:rescue [--resume\|--fresh] [--model flash\|pro\|flash-lite] <task>` | Delegate a coding/debugging task to `agy` and return its output verbatim. |
| `/agy:setup` | Health-check: resolves the binary, reads version, runs a 30s ping. |

### Research intensity matrix

| Intensity | Default model | Timeout | Sources targeted | Output shape |
|---|---|---|---|---|
| `low` | `gemini-3.5-flash` | 3 min | 3–5 | TL;DR + sources |
| `medium` | `gemini-3.5-flash` | 8 min | 8–12 | Executive summary, findings, analysis, references |
| `high` | `gemini-3.5-pro` | 20 min | 15+ with triangulation | TL;DR, context, findings, comparisons, risks, evidence gaps, conclusion, references |

Use `--model flash`, `--model pro`, or `--model flash-lite` to override the per-intensity default.

---

## Install

### Prerequisites

1. **Claude Code** — `npm i -g @anthropic-ai/claude-code` ([docs](https://docs.claude.com/en/docs/claude-code/overview)).
2. **Antigravity CLI** — install once and log in:

   ```powershell
   # Windows (PowerShell)
   irm https://antigravity.google/cli/install.ps1 | iex
   ```

   ```bash
   # macOS / Linux
   curl -fsSL https://antigravity.google/cli/install.sh | bash
   ```

   Then run `agy` once in a fresh terminal to complete Google OAuth login.

### Add the plugin to Claude Code

From inside Claude Code:

```
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
```

Restart Claude Code, then verify:

```
/agy:setup
```

You should see the binary path, version, and a `pong` from a 30-second ping.

---

## Usage examples

### Quick fact check (low)

```
/agy:research n8n self-hosted telemetry env vars --intensity low
```

Returns a 3–5 bullet TL;DR with official-doc URLs, in under 3 minutes.

### Tech radar evaluation (medium)

```
/agy:research feature flags postgres vs redis tradeoffs 2026 --intensity medium
```

Executive summary, 8–12 sources triangulated, analysis section, numbered references with dates. Saved to `docs/agy/research/2026-05-23-feature-flags-postgres-vs-redis-tradeoffs-2026.md`.

### Strategic decision (high)

```
/agy:research modular erp architecture for mercadolibre sellers latam --intensity high
```

15+ sources, comparative tables, counterarguments, evidence gaps, confidence-rated conclusion. ~20 minutes.

### Code rescue

```
/agy:rescue debug why my drizzle migration drops the foreign key constraint on user_id
```

Hands the task to `agy` with `--dangerously-skip-permissions` so it can read and edit files. Returns agy's output verbatim.

---

## How it works

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

The subagent is a **thin forwarder** — no companion runtime, no ACP, no JavaScript. It picks the right prompt template per intensity, computes the timeout and model, captures stdout, writes the file, and returns.

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
├── LICENSE
└── README.md
```

---

## Comparison vs the `gemini` Claude Code plugin

| | [`abiswas97/gemini-plugin-cc`](https://github.com/abiswas97/gemini-plugin-cc) | This plugin |
|---|---|---|
| Underlying CLI | Gemini CLI (deprecated) | Antigravity CLI (`agy`) — official replacement |
| Runtime | Node.js companion script (~800 LoC) + ACP protocol | None — direct `agy --print` via Bash |
| Conversation persistence | Custom thread tracking | Native `agy --continue` |
| Web research | Generic delegation | First-class `/agy:research` with intensity levels |
| Output to file | No | Yes — `docs/agy/research/` by default |
| Code review commands | Yes (`/gemini:review`, `/gemini:adversarial-review`) | Not yet (v2 maybe) |

If you want sophisticated code review workflows, the `gemini` plugin is more mature. If you want **deep web research that drops a structured markdown file into your repo**, this is the simpler tool.

---

## Roadmap

- [ ] `/agy:review` and `/agy:adversarial-review` (parity with the gemini plugin)
- [ ] `/agy:adversarial-research` — high-intensity research with explicit red-team / steelman framing
- [ ] Configurable output directory (env var or repo-level config)
- [ ] CI mode (machine-readable JSON output)
- [ ] Cost estimate per intensity in the setup command

PRs welcome. Open an issue first if you're planning anything bigger than a typo.

---

## Author

Built by **Marcos Nahuel Albornoz** — co-founder & PM at [**TRAID**](https://traidai.com), an automation & AI agency for e-commerce in LATAM and the US.

Stack we use daily: Claude Code, Antigravity, n8n, Supabase, Next.js, LangGraph.

- GitHub: [@MarcosNahuel](https://github.com/MarcosNahuel)
- Email: contact@traidai.com

If this plugin saves you time, a ⭐ on the repo is the best way to say thanks.

---

## License

[MIT](LICENSE) — do whatever you want, no warranty.
