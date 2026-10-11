---
name: agy-notebook
description: "Use Antigravity for notebook. Local NotebookLM over a FOLDER of documents using Antigravity (agy). Sweeps each document (PDF with text, scanned PDF, image, docx) into an objective-driven Markdown summary, then "
---

# Antigravity: notebook

Read [host integration](../../references/host-integration.md), then the shared
[notebook workflow](../../commands/notebook.md). Follow that workflow using the current
host's tools and the host integration contract. On Codex execute routing directly;
on Claude the existing slash command and subagent remain available.

Use the actual loaded plugin root for scripts and references. Do not require
Claude-only Agent/Workflow APIs, assume authentication, bypass permissions, or
claim success from installation alone. Keep the user's current scope.
