---
name: agy-model
description: "Use Antigravity for model. Show or set the agy (Antigravity / Gemini) model by writing ~/.gemini/antigravity-cli/settings.json — the reliable way to switch models (the unreliable --model flag silently falls "
---

# Antigravity: model

Read [host integration](../../references/host-integration.md), then the shared
[model workflow](../../commands/model.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
