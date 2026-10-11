---
name: agy-ask
description: "Use Antigravity for ask. One-shot prompt to Antigravity (agy) — quick question, returns response verbatim. No file persistence to docs/."
---

# Antigravity: ask

Read [host integration](../../references/host-integration.md), then the shared
[ask workflow](../../commands/ask.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
