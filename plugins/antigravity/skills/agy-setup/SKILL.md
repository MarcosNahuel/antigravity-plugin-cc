---
name: agy-setup
description: "Use Antigravity for setup. Check whether the Antigravity CLI (agy) is installed, on PATH, and responding to a ping"
---

# Antigravity: setup

Read [host integration](../../references/host-integration.md), then the shared
[setup workflow](../../commands/setup.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
