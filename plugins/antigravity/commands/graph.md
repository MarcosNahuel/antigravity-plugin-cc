---
description: Build a knowledge GRAPH of a folder (code + docs) with Graphify, powered by Gemini via the Antigravity CLI (agy) — so the graph is built OFF Claude's tokens. Tree-sitter ASTs + NetworkX + Leiden communities + an interactive graph.html. Then Claude reads graph.json / GRAPH_REPORT.md to reason. Complements /agy:notebook (graphs = relations/communities; notebook = multimodal docs + exact SQL). First run auto-installs graphify (opt-in deps).
argument-hint: "<folder>"
context: fork
allowed-tools: Bash, Read
---

Turn a folder into a queryable **knowledge graph** using [Graphify](https://github.com/safishamsi/graphify),
with the **`agy-cli` backend** this plugin ships: **Gemini (via `agy`) builds the graph**, billed to
your Antigravity/Google sign-in and **off the host assistant's token budget**. Claude then reads the
small `graph.json` / `GRAPH_REPORT.md` to reason — no re-reading the raw files.

Raw user request:
$ARGUMENTS

## Phase 0 — Ensure the stack (ONE Bash call)

Parse `$ARGUMENTS`: the leading existing-directory token is the **folder**. Then make sure graphify +
the agy-cli backend are installed (idempotent; first run clones + patches + `pip install -e`s
graphify — opt-in heavier deps: networkx, tree-sitter):

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/graphify_agy_install.py"
```

- Prints `READY` → continue. `READY_BUT_AGY_MISSING` → tell the user to install/sign-in `agy`
  (https://antigravity.google) and stop. `MISSING`/error → relay it and stop.
- If `git` or `pip` is unavailable, surface that and stop.

## Phase 1 — Build the graph (Gemini via agy)

Run from a neutral CWD with `AGY_BIN` exported (so the subprocess finds agy). Extract, then cluster +
report:

```bash
export AGY_BIN="${AGY_BIN:-$(command -v agy || echo "$HOME/AppData/Local/agy/bin/agy.exe")}"
cd "$(mktemp -d)"
graphify extract "<FOLDER>" --backend agy-cli
graphify cluster-only "<FOLDER>" --backend agy-cli
```

- The graph is built by Gemini; the printed `tokens … est. cost (~agy-cli): $0.0000` confirms it cost
  **zero Claude tokens**.
- Big folders make many serial agy calls (rate-limited ~10 RPM on free tiers) — warn the user if the
  folder is large; `GRAPHIFY_AGY_CLI_PARALLEL=1` opts into concurrency on a high-RPM plan.
- Outputs land in `<FOLDER>/graphify-out/`: `graph.json` (node-link), `GRAPH_REPORT.md`,
  `graph.html` (interactive viz).

## Phase 2 — Present + reason

Read `<FOLDER>/graphify-out/GRAPH_REPORT.md` and present: the named **communities**, the **god nodes**
(most-connected entities), and the **surprising/inferred connections**. Point the user to
`graph.html` for the interactive view. To answer a specific question, query `graph.json` directly
(it's small) instead of re-reading the source files — e.g. with a short Python snippet over its
`nodes` / `links`.

## Notes
- **graphs vs RAG**: use `/agy:graph` for relations / multi-hop / community structure; use
  `/agy:notebook` + `/agy:notebook-query` for multimodal document reading and exact aggregates
  (amounts in integer cents, timelines). They complement each other.
- The agy-cli backend + install live in `plugins/antigravity/scripts/` (patch + installer). It's an
  upstreamable change to Graphify (it already has a `claude-cli` CLI backend).
