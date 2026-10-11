---
name: agy-rescue
description: "Use Antigravity for rescue. Delegate a coding, debugging or implementation task to the Antigravity CLI (agy) subagent"
---

# Antigravity: rescue

Read [host integration](../../references/host-integration.md), then the shared
[rescue workflow](../../commands/rescue.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
