---
description: Turn a notebook knowledge base into a knowledge GRAPH — a node-link graph.json + a self-contained interactive graph.html — with NO agy calls and NO extra deps. Derives edges from entity co-occurrence within documents (works even though agy rarely emits explicit relations) plus any explicit relations. See who/what connects to what, and the hub entities. Complements /agy:notebook-query (exact SQL) and /agy:graph (Graphify, for code).
argument-hint: "<folder>"
context: fork
allowed-tools: Bash, Read
---

Build a graph view of the `notebook.db` that `/agy:notebook` compiled — instantly, locally, free.
agy rarely fills the explicit `relaciones` array, so this derives edges from **entity co-occurrence
within each document** (the relational signal that needs no LLM) plus any explicit relations present.

Raw user request:
$ARGUMENTS

## Phase 0 — Build the graph (ONE Bash call)

Resolve `OUTDIR = docs/agy/notebook/<slug>` from the folder (same `slug()` the notebook uses). If
`notebook.db` is missing, tell the user to run `/agy:notebook <folder> | <objetivo>` first. Then:

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/notebook_graph.py" "$OUTDIR"
```

It prints `GRAPH nodes=N edges=M (cooccur=…, explicit=…) hubs=[…]` and writes `<OUTDIR>/graph.json`
(node-link) + `<OUTDIR>/graph.html` (self-contained interactive viz, vis-network from CDN).

## Phase 1 — Present + reason

- Report the node/edge counts and the **hub entities** (most connected — your central people / orgs /
  references). Point the user to `graph.html` for the interactive view.
- Nodes are deduped entities (`persona | organizacion | referencia`) + document nodes; edges are
  `appears_in` (entity→document), `co_mentioned` (entities sharing a document, weighted by # docs),
  and any explicit relations.
- To answer a question, read `graph.json` directly (small) — e.g. neighbours of an entity, shortest
  path between two, or the densest cluster — instead of re-reading the source documents.

## Notes
- **Zero agy calls, zero new deps** — pure stdlib over the existing `notebook.db`. Re-run after a
  fresh `/agy:notebook` to refresh.
- **vs `/agy:graph`**: this graphs the *document/entity* network from your notebook RAG (free, local);
  `/agy:graph` uses Graphify (Gemini via agy) for richer graphs incl. **code** (tree-sitter ASTs) and
  Leiden communities. Use this for a quick document graph, `/agy:graph` for code or deep graphs.
- For exact aggregates (amounts, timelines) use `/agy:notebook-query`.
