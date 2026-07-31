# Graphify × agy — knowledge graphs for free, community names by Gemini

[Graphify](https://github.com/safishamsi/graphify) (MIT) turns a folder of code + docs into a
queryable **knowledge graph** (tree-sitter ASTs + NetworkX + Leiden communities + an interactive
`graph.html`). This plugin drives it from `/agy:graph`.

## How it works now (plugin v1.6.0+)

**Graphify 0.9 extracts code structurally — no LLM, no API key, no tokens.** So the graph itself is
free on every assistant, and there is nothing to route through a model:

```bash
graphify extract <folder> --code-only   # tree-sitter AST, local, ~seconds
graphify cluster-only <folder>          # GRAPH_REPORT.md + graph.json + graph.html
```

The one step that genuinely wants a language model is **naming the communities** — otherwise the
report reads "Community 0 / Community 1 / …". Upstream fills that from an API-key backend, or by
letting the *host agent* do it, which on Claude Code would spend Claude's tokens. This plugin hands
it to **Gemini via `agy`** instead:

```bash
python plugins/antigravity/scripts/graphify_label_agy.py <folder>
```

One `agy --print` call per 100 communities, writing `graphify-out/.graphify_labels.json`, which
`graphify cluster-only` picks up on its next run. Division of labour: **Graphify builds the graph,
Gemini names it, Claude reads it.**

Documents (PDF, papers, images) still need a model to extract entities from prose. Two supported
routes, both off Claude: set `GEMINI_API_KEY` and run `graphify extract --backend gemini`, or use
upstream's native `graphify install --platform antigravity` and drive the workflow from inside agy.

## What changed, and why the old patch is gone

Plugin ≤ v1.5.1 shipped an `agy-cli-backend.patch`: it cloned Graphify, patched `llm.py` +
`__main__.py` to add an `agy-cli` LLM backend, and `pip install -e`'d the result. That earned its keep
in June 2026, when Graphify needed a model for *everything* and offered no Antigravity path.

Then upstream shipped the **v8 rewrite**: the default branch moved from `main` to `v8`, the files the
patch targeted moved with it, and — crucially — **code extraction stopped needing an LLM at all**.
Every *fresh* install after that cloned v8, failed `git apply`, and left `/agy:graph` dead. Existing
machines kept working only because their June clone was already on disk.

The lesson is worth keeping: **do not patch a third-party project's internals to add an integration
point.** A context diff against a fast-moving repo (Graphify ships multiple releases a day) is a
time-bomb, and the failure lands on users, not on the maintainer. The replacement depends only on the
official PyPI package plus a documented sidecar file.

## Windows gotcha — MAX_PATH (verified 2026-07-31)

Graphify caches each AST extraction at
`<out>/graphify-out/cache/ast/v<version>/<64-char-sha256>.<8-char>.tmp`, ~110 characters on top of the
project path. Cross Windows' 260-char ceiling and the write fails with ENOENT, Graphify prints
"AST extraction failed" then "graph is empty" — and **exits 0**. A silent empty graph, not an error.

Measured on Windows 11 + Python 3.13 + graphify 0.9.31:

| project path length | result |
|---|---|
| 259 chars | 57 nodes, 81 edges |
| 260 chars | 0 nodes, exit 0 |

`scripts/graphify_outdir.py` guards against it by relocating output for deep projects via the
`GRAPHIFY_OUT` env var upstream already honours.

## Validation (real run, 2026-07-31)

`/agy:graph` on a 2-file Python corpus, end to end on Windows:

| step | result |
|---|---|
| `graphify extract --code-only` | **21 nodes · 33 edges · 5 communities**, zero tokens, zero API keys |
| `graphify_label_agy.py` | `LABELED 5` — one agy call, zero Claude tokens |
| names produced by Gemini | "Notebook DB utilities and formatters", "AGY stack check and graphify integration", "Tolerant JSON parsing", … |
| `graphify cluster-only` | GRAPH_REPORT.md renders the Gemini names; `graph.html` + `graph.json` written |

`VALIDATION_GRAPH_REPORT.md` keeps the earlier (June 2026) document-corpus report from the patch era.
