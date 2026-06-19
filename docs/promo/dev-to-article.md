---
title: "I built a local NotebookLM as a Claude Code plugin (on Google's new `agy` CLI)"
published: false
description: "How I turned a folder of documents into a grounded, cited, local NotebookLM — by bridging Claude Code to Google Antigravity's agy CLI. Plus the agy gotchas that cost me a day."
tags: claudecode, gemini, ai, opensource
canonical_url: https://github.com/MarcosNahuel/antigravity-plugin-cc
cover_image: ""
---

> **TL;DR** — `/agy:notebook <folder> | <objective>` reads a whole folder of documents (PDFs,
> scans, images, docx) with Gemini 3.x and produces a per-document summary, a relevance index, a
> cited master synthesis, a timeline and an entity sheet — then `/agy:notebook-ask` answers questions
> over them **with citations**. It runs locally, on your own Gemini account, and barely touches
> Claude's context. It's one of 13 commands in [`antigravity-plugin-cc`](https://github.com/MarcosNahuel/antigravity-plugin-cc).

## Why

I love [NotebookLM](https://notebooklm.google.com), but I kept hitting the same three walls:

1. **It's cloud.** I work with legal *expedientes* — files I can't upload to a third-party product.
2. **I already live in Claude Code.** Switching tools to "ask my documents" breaks the flow.
3. **Reading big document sets in Claude is expensive.** Forty 5–50-page PDFs blow through context.

What I wanted: point a command at a folder, get NotebookLM-style artifacts (summaries, an index, a
cited synthesis, Q&A) — **locally**, and **without** spending Claude tokens reading every page.

## The bridge: Claude Code × `agy`

Google announced at I/O 2026 that **Antigravity CLI (`agy`)** replaces the old `gemini-cli` (which
[stops serving requests on June 18, 2026](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)).
`agy` is a Go binary backed by Gemini 3.x with native multimodal vision. It's perfect for the
"read everything" half of the job — while Claude stays the orchestrator.

So the plugin is a **thin Bash forwarder**: a Claude Code slash command parses your request, fans
out work to a subagent, and the subagent calls `agy --print`. No Node runtime, no MCP server.

```
/agy:notebook  →  command (parse + orchestrate)
              →  agy-rescue subagent (one per document)
              →  agy --print  (Gemini 3.x reads the doc, writes a summary file)
```

## How `/agy:notebook` works

**Phase 0 — classify + cache.** For each file: PDFs with a real text layer are pre-extracted
(cheap, fed as text); scanned PDFs and images go through `agy`'s multimodal OCR. A content+objective
hash is stored so re-runs only re-summarize *changed* documents. Scanned PDFs over ~20 pages are
**split into 15-page sub-PDFs** — because (see gotchas) one `agy` call can't OCR hundreds of pages.

**Phase 1 — per-document summaries.** One `agy` call per document, fanned out ~10 at a time with
rate-limit backoff. Each writes a small `*.resumen.md` with frontmatter (`tipo`, `numero_gde`,
`fecha`, `relevancia` 0–100) and an objective-driven summary.

**Phase 2 — synthesis.** One `agy` call reads all the small summaries and writes `INDEX.md`
(relevance ranking), `RESUMEN_MAESTRO.md` (a synthesis that **cites each source document**),
`TIMELINE.md` and `ENTIDADES.md` (people / amounts / references / orgs, each with its source).

**Q&A.** `/agy:notebook-ask <folder> | <question>` answers from those summaries, with citations,
never re-reading the originals.

The trick that makes it cheap: **Claude never reads the documents.** `agy` does, writing to files;
Claude reads only the two small final artifacts.

```text
/agy:notebook  ./expediente | objective: parties, key dates, amounts, status
/agy:notebook-ask ./expediente | who opened the file and when?
→ "Opened by J. Doe on 2022-07-08." (cites PV-2022-04770554)
```

## The `agy` gotchas (that cost me a day)

If you build on `agy --print`, save yourself the pain:

1. **Empty stdout outside a TTY (issue #76).** Called from any subprocess, `agy --print` exits 0
   but writes *nothing* to stdout — even on success. **Fix:** tell `agy` to `write_file` its output
   to a path, and read the file. Never depend on stdout.
2. **Large multimodal inputs time out.** Hundreds of scanned pages in one call won't finish. **Fix:**
   one document per call; chunk big scans into page ranges.
3. **`"You are not logged into Antigravity"` is (mostly) noise.** It shows up from secondary auth
   scopes (model list, telemetry) *even on fully successful runs*. Don't send users to re-login over
   it. The real health check: did the `write_file` land?
4. **`--model` is unreliable.** An unknown id silently falls back to the default. The dependable
   lever is writing the exact label into `~/.gemini/antigravity-cli/settings.json` (which is what the
   TUI does). The plugin ships `/agy:model` to do exactly that, and routes Flash for the sweep / Pro
   for the synthesis automatically.
5. **Rate limits are per-minute.** ~10 RPM on free. A concurrency cap + 60s backoff beats blind
   parallelism.

## Try it

```bash
# 1) install agy (Google Antigravity CLI), sign in once
# 2) in Claude Code:
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
/agy:setup        # health check
/agy:notebook  ./my-docs | what are the key facts and dates?
```

13 commands total — also deep web research with citations, branded HTML reports, code review,
doc-to-markdown, browser recording, web scraping and UX audits. MIT, no runtime deps.

⭐ [github.com/MarcosNahuel/antigravity-plugin-cc](https://github.com/MarcosNahuel/antigravity-plugin-cc)

*What would you point a local NotebookLM at? I'd love to hear it in the comments.*
