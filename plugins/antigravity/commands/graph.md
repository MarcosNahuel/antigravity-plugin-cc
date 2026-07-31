---
description: Build a knowledge GRAPH of a folder (code + docs) with Graphify — tree-sitter ASTs + NetworkX + Leiden communities + an interactive graph.html. The code graph is built LOCALLY and costs zero tokens on any assistant; Gemini via agy only names the communities. Then Claude reads graph.json / GRAPH_REPORT.md to reason instead of re-reading the files. Complements /agy:notebook (graphs = relations/communities; notebook = multimodal docs + exact SQL). First run auto-installs graphify.
argument-hint: "<folder>"
context: fork
allowed-tools: Bash, Read
---

Turn a folder into a queryable **knowledge graph** using [Graphify](https://github.com/safishamsi/graphify).

Since Graphify 0.9 the code graph is **deterministic and local** — tree-sitter ASTs, no LLM, no API
key, no tokens on anyone's budget. The one step that wants a language model is naming the communities,
and this plugin hands that to **Gemini via `agy`** (one call), so the host assistant still spends
nothing. Claude then reads the small `graph.json` / `GRAPH_REPORT.md` to reason — no re-reading the
raw files.

Raw user request:
$ARGUMENTS

## Phase 0 — Ensure the stack (ONE Bash call)

Parse `$ARGUMENTS`: the leading existing-directory token is the **folder**. Then:

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/graphify_install.py"
```

- Last line `READY` → continue with everything below.
- `READY_NO_AGY` → continue, but **skip Phase 2** (communities keep hub-derived names). Mention that
  installing + signing into `agy` (https://antigravity.google) gets them named.
- `MISSING` / non-zero exit → relay the printed reason and stop.
- Also capture the `GRAPHIFY_CMD=` line — it is how to invoke Graphify on this machine (the console
  script, or `"<python>" -m graphify` when the Scripts dir is not on PATH). Use it verbatim below as
  `$GFY`.

## Phase 1 — Build the graph (local, free)

```bash
eval "$(python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/graphify_outdir.py" "<FOLDER>")"
$GFY extract "<FOLDER>" --code-only
```

- `graphify_outdir.py` is the **Windows MAX_PATH guard**: past ~140 characters of project path the
  AST cache filename crosses Windows' 260-char ceiling, and Graphify then prints "AST extraction
  failed" + "graph is empty" and still **exits 0**. For deep projects it emits an
  `export GRAPHIFY_OUT=...` line (relocating the outputs, and telling you where on stderr); for short
  paths and non-Windows it prints nothing, so the `eval` is a no-op. Keep the same environment for
  every later phase — the sidecars live wherever this pointed.
- Note the `found N code, M docs, P papers, Q images` line — you need `M+P+Q` in Phase 4.
- **Honest gate:** if the output says `graph is empty` or `0 nodes`, the run FAILED. Say so and stop;
  do not present an empty graph as a result. Exit code 0 does not mean success here.

## Phase 2 — Name the communities with Gemini (skip if `READY_NO_AGY`)

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/graphify_label_agy.py" "<FOLDER>"
```

- One `agy` call per 100 communities, off the host assistant's tokens. Last line `LABELED <n>` → good.
- `FAILED <reason>` → not fatal: re-run Phase 3 with `--no-label` so communities fall back to
  hub-derived names, and tell the user naming was skipped and why.

## Phase 3 — Report + interactive view

```bash
$GFY cluster-only "<FOLDER>"            # add --no-label if Phase 2 was skipped or FAILED
```

Outputs (in `$GRAPHIFY_OUT`, or `<FOLDER>/graphify-out/` when it is unset): `graph.json` (node-link),
`GRAPH_REPORT.md`, `graph.html` (interactive viz).

## Phase 4 — Docs, PDFs and images (only if Phase 1 found any)

`--code-only` indexes code and skips documents on purpose, because documents are the part that
genuinely needs a model. If `M+P+Q > 0`, tell the user those N files are NOT in the graph and offer:

1. **Gemini API key** (fastest, parallel): set `GEMINI_API_KEY`, then `$GFY extract "<FOLDER>" --backend gemini`.
2. **Native Antigravity route** (no key): `$GFY install --platform antigravity`, then drive the
   graphify workflow from inside `agy` — upstream ships first-class Antigravity support, so Gemini
   does the document pass under your Google sign-in.

Do not silently pretend the documents were indexed.

## Phase 5 — Present + reason

Read `GRAPH_REPORT.md` and present: the named **communities**, the **god nodes** (most-connected
entities), and the **surprising/inferred connections**. Point the user to `graph.html`. To answer a
specific question, prefer Graphify's own traversal over re-reading source:

```bash
$GFY query "<question>"        # BFS over graph.json, token-budgeted
$GFY explain "<node>"          # plain-language explanation of a node + neighbours
$GFY path "<A>" "<B>"          # shortest path between two concepts
```

## Notes
- **graphs vs RAG**: use `/agy:graph` for relations / multi-hop / community structure; use
  `/agy:notebook` + `/agy:notebook-query` for multimodal document reading and exact aggregates
  (amounts in integer cents, timelines). They complement each other.
- Re-runs are incremental (`$GFY update "<FOLDER>"` re-extracts only changed files).
- Plugin <= v1.5.1 instead cloned Graphify and applied a bundled `agy-cli` backend patch. Upstream's
  v8 rewrite moved those files, so the patch stopped applying and `/agy:graph` broke on every fresh
  install. It is gone: the graph no longer needs an LLM at all, so there is nothing left to patch.
