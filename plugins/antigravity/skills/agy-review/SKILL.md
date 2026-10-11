---
name: agy-review
description: "Use Antigravity for review. Send the current git diff to Antigravity (agy) for code review. Optional focus text to steer the review."
---

# Antigravity: review

Read [host integration](../../references/host-integration.md), then the shared
[review workflow](../../commands/review.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
