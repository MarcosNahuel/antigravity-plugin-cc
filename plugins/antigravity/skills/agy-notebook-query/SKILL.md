---
name: agy-notebook-query
description: "Use Antigravity for notebook-query. Query the notebook knowledge base (SQLite) built by /agy:notebook — precise, grounded, cited. Ask in natural language (\"sum the amounts by category\", \"which docs mention 'Acme Corp"
---

# Antigravity: notebook-query

Read [host integration](../../references/host-integration.md), then the shared
[notebook-query workflow](../../commands/notebook-query.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
