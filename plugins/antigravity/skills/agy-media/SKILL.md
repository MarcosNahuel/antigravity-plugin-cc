---
name: agy-media
description: "Use Antigravity for media. Ask a question about an AUDIO, VIDEO or IMAGE file (or a YouTube/remote URL) with Antigravity (agy / Gemini 3.x multimodal). Beyond transcription — \"what decisions were made in thi"
---

# Antigravity: media

Read [host integration](../../references/host-integration.md), then the shared
[media workflow](../../commands/media.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
