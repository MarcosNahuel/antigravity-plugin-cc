---
name: agy-notebook-ask
description: "Use Antigravity for notebook-ask. Ask a question over a notebook corpus you already built with /agy:notebook. agy answers from the per-document summaries (docs/agy/notebook/<folder>/*.resumen.md) with citations — t"
---

# Antigravity: notebook-ask

Read [host integration](../../references/host-integration.md), then the shared
[notebook-ask workflow](../../commands/notebook-ask.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
