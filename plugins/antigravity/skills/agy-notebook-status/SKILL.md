---
name: agy-notebook-status
description: "Use Antigravity for notebook-status. Check the progress of a /agy:notebook sweep (for long document sets run with --background). Reports % complete, done/pending/failed counts, elapsed time and a rough ETA, and which "
---

# Antigravity: notebook-status

Read [host integration](../../references/host-integration.md), then the shared
[notebook-status workflow](../../commands/notebook-status.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
