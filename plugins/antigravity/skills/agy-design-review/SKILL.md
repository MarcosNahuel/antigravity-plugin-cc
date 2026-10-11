---
name: agy-design-review
description: "Use Antigravity for design-review. Run a UX/visual design audit of a URL using Antigravity (agy). Captures desktop + mobile screenshots, scores 10 dimensions (hierarchy, typography, color, spacing, a11y, etc.), benc"
---

# Antigravity: design-review

Read [host integration](../../references/host-integration.md), then the shared
[design-review workflow](../../commands/design-review.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
