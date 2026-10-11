---
name: agy-video
description: "Use Antigravity for video. WATCH a video and return a structured VISUAL breakdown (not just a transcript) with Antigravity (agy / Gemini 3.x, natively multimodal in video). Scene-by-scene segments with times"
---

# Antigravity: video

Read [host integration](../../references/host-integration.md), then the shared
[video workflow](../../commands/video.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
