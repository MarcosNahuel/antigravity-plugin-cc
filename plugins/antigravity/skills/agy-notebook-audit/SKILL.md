---
name: agy-notebook-audit
description: "Use Antigravity for notebook-audit. Adversarial consistency audit over the notebook knowledge base — finds contradictions in a document corpus: the same category with conflicting amounts, the same person under two na"
---

# Antigravity: notebook-audit

Read [host integration](../../references/host-integration.md), then the shared
[notebook-audit workflow](../../commands/notebook-audit.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
