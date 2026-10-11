---
name: agy-notebook-graph
description: "Use Antigravity for notebook-graph. Turn a notebook knowledge base into a knowledge GRAPH — a node-link graph.json + a self-contained interactive graph.html — with NO agy calls and NO extra deps. Derives edges from e"
---

# Antigravity: notebook-graph

Read [host integration](../../references/host-integration.md), then the shared
[notebook-graph workflow](../../commands/notebook-graph.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
