---
name: agy-transcribe
description: "Use Antigravity for transcribe. Transcribe and summarize an AUDIO or VIDEO file (or a YouTube/remote URL) with Antigravity (agy / Gemini 3.x multimodal) — something Claude can't do natively. Voice notes, meetings"
---

# Antigravity: transcribe

Read [host integration](../../references/host-integration.md), then the shared
[transcribe workflow](../../commands/transcribe.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
