---
name: agy-scrape
description: "Use Antigravity for scrape. Scrape structured data from a single URL using Antigravity (agy). Returns markdown table or JSON. Saves to docs/agy/scrapes/."
---

# Antigravity: scrape

Read [host integration](../../references/host-integration.md), then the shared
[scrape workflow](../../commands/scrape.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
