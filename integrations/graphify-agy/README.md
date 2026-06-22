# Graphify × agy — build knowledge graphs with Gemini, off Claude's tokens

[Graphify](https://github.com/safishamsi/graphify) (MIT) turns a folder of code + docs into a
queryable **knowledge graph** (Tree-sitter ASTs + NetworkX + Leiden communities + an interactive
`graph.html`). Out of the box its `claude-cli` backend builds the graph using **Claude Code's own
tokens**; its `gemini` backend needs a `GEMINI_API_KEY`.

This integration adds an **`agy-cli` backend** so Graphify builds the graph through the **Google
Antigravity CLI (`agy`)** — i.e. **Gemini generates the graph**, billed to your Antigravity/Google
sign-in (no API key), and **off the host assistant's (Claude's) token budget**. Then Claude reads the
small `graph.json` / `GRAPH_REPORT.md` when it reasons — cheap.

> The division of labour: **Gemini (via agy) builds the graph; Claude reads it.** Pairs with this
> plugin's `/agy:notebook` (multimodal document RAG + exact SQL) — Graphify for the graph, notebook
> for structured facts.

## What the patch does (`agy-cli-backend.patch`)

Adds, to graphify's `llm.py` + `__main__.py`, a new `agy-cli` backend that mirrors the existing
`claude-cli` one:
- subprocesses `agy --print` from a **neutral temp CWD** (avoids agy's project artifact-sandbox bug),
- writes the (possibly huge) prompt to a file agy reads (agy takes the prompt as an argv, which blows
  the OS command-line limit on big chunks), and has agy **write its JSON answer to a file** (agy's
  `--print` writes nothing to stdout outside a TTY — upstream issue #76),
- runs **serial by default** (`GRAPHIFY_AGY_CLI_PARALLEL=1` to opt in) to respect agy's rate limit,
- exempts `agy-cli` from the API-key preflight (auth is the user's agy sign-in, like `claude-cli`).

## Install

```bash
git clone https://github.com/safishamsi/graphify
cd graphify
git apply /path/to/integrations/graphify-agy/agy-cli-backend.patch
pip install -e .          # or: uv pip install -e .
# agy must be installed + signed in (https://antigravity.google); set AGY_BIN if not on PATH
```

## Use

```bash
graphify extract ./my-folder --backend agy-cli       # Gemini-via-agy builds the graph
graphify cluster-only ./my-folder --backend agy-cli  # name communities + GRAPH_REPORT.md + graph.html
```

Output (in `./my-folder/graphify-out/`): `graph.json` (node-link), `GRAPH_REPORT.md` (communities,
god-nodes, surprising links), `graph.html` (interactive viz). Claude reads those to reason.

Env knobs: `AGY_BIN` (path to agy), `GRAPHIFY_AGY_CLI_PARALLEL=1` (allow concurrent agy calls — only
on a high-RPM plan).

## Validation (real run, 2026-06-22)

Ran on a 4-document test "expediente" (markdown notes with people/orgs/amounts/dates/contract refs):

| | |
|---|---|
| `graphify extract … --backend agy-cli` | **18 nodes · 24 edges · 3 communities** |
| Token cost on Claude | **$0 / 0 tokens** (built entirely by Gemini via agy) |
| Entities captured | Acme Corp, Jane Smith, Globex SA, Proyecto Phoenix, Carlos Ruiz, Contrato CT-2026-008 ✓ |
| Relations | Acme→Jane, Jane→Globex, Carlos→CT-2026-008, cross-doc entity links ✓ |
| `cluster-only` | named communities ("Proyecto Phoenix Collaboration", "Globex SA Personnel", …) + `GRAPH_REPORT.md` + `graph.html` ✓ |

See `VALIDATION_GRAPH_REPORT.md` for the actual report agy/Gemini produced.

## Notes & limits

- **Rate limit**: graphify makes one LLM call per chunk; on agy's free ~10 RPM a big repo is slow
  (serial). On a Pro/Ultra plan it's fine. For very large code corpora, `--backend gemini` (API key)
  parallelises better.
- **agy model** is set via `~/.gemini/antigravity-cli/settings.json` (not a flag); use a fast Flash
  model for the sweep. (`GRAPHIFY_AGY_MODEL` is reserved for a future settings.json switch.)
- This is a **clean, upstreamable patch** (graphify already has a `claude-cli` CLI backend) — it could
  be sent as a PR to graphify so no fork is needed long-term.
- Amounts/dates as exact rows are better served by this plugin's `/agy:notebook-query` (integer-cent
  SQL); Graphify focuses on the entity/relation graph. Use both.
