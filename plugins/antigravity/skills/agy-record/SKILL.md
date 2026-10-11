---
name: agy-record
description: "Use Antigravity for record. Record a browser walkthrough of a URL using Antigravity (agy). Generates .webm video, screenshots, and a report. Auto-converts to MP4 if ffmpeg is available."
---

# Antigravity: record

Read [host integration](../../references/host-integration.md), then the shared
[record workflow](../../commands/record.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
