---
title: "I built a local NotebookLM (and a multi-agent research loop) as a Claude Code plugin, on Google's new `agy` CLI"
published: false
description: "How I turned a folder of documents into a grounded, cited, local NotebookLM, and later a multi-agent deep-research loop, by bridging Claude Code to Google Antigravity's agy CLI. Plus the agy/Windows gotchas that cost real hours."
tags: claudecode, gemini, ai, opensource
canonical_url: https://github.com/MarcosNahuel/antigravity-plugin-cc
cover_image: ""
---

> **Note before you read this as a launch post: it isn't one.** This is a build log — what the
> problem was, how the bridge works, and the specific bugs that cost real time. The project is
> **alpha/experimental**, MIT-licensed, and **not affiliated with or endorsed by Google or
> Anthropic** — it just talks to their publicly documented CLIs, with your own credentials.

> **TL;DR** — `/agy:notebook <folder> | <objective>` reads a whole folder of documents (PDFs,
> scans, images, docx) with Gemini 3.x and produces a per-document summary, a relevance index, a
> cited master synthesis, a timeline and an entity sheet — then `/agy:notebook-ask` answers questions
> over them **with citations**. `/agy:deep-research <topic>` runs the same "let Gemini do the heavy
> lifting" idea on the open web: a multi-agent loop with a plan gate, parallel browsing per angle,
> a red-team pass, and a report that's explicit about what it didn't manage to cover. Both run
> locally, on your own Gemini account, and barely touch Claude's context. They're two of 22
> commands in [`antigravity-plugin-cc`](https://github.com/MarcosNahuel/antigravity-plugin-cc).

## Why

I love [NotebookLM](https://notebooklm.google.com), but I kept hitting the same three walls:

1. **It's cloud.** I work with documents I can't upload to a third-party product — contracts, an RFP, unreleased research.
2. **I already live in Claude Code.** Switching tools to "ask my documents" breaks the flow.
3. **Reading big document sets in Claude is expensive.** Forty 5–50-page PDFs blow through context.

What I wanted: point a command at a folder, get NotebookLM-style artifacts (summaries, an index, a
cited synthesis, Q&A) — **locally**, and **without** spending Claude tokens reading every page.

## The bridge: Claude Code × `agy`

Google announced at I/O 2026 that **Antigravity CLI (`agy`)** replaces the old `gemini-cli` (which
[stops serving requests on June 18, 2026](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)).
`agy` is a Go binary backed by Gemini 3.x with native multimodal vision. It's perfect for the
"read everything" half of the job — Claude stays lean as the orchestrator, and you save tokens.

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
rate-limit backoff. Each writes a small `*.resumen.md` with frontmatter (`tipo`, `referencia`,
`fecha`, `relevancia` 0–100) and an objective-driven summary.

**Phase 2 — synthesis.** One `agy` call reads all the small summaries and writes `INDEX.md`
(relevance ranking), `RESUMEN_MAESTRO.md` (a synthesis that **cites each source document**),
`TIMELINE.md` and `ENTIDADES.md` (personas / organizaciones / montos / fechas / referencias, each with its source).

**Q&A.** `/agy:notebook-ask <folder> | <question>` answers from those summaries, with citations,
never re-reading the originals.

The trick that makes it cheap: **Claude never reads the documents.** `agy` does, writing to files;
Claude reads only the two small final artifacts.

```text
/agy:notebook  ./research-papers | objective: open questions, key findings, who funded what
/agy:notebook-ask ./research-papers | which docs mention "Acme Corp"?
→ "Three: the 2024 RFP, the Q3 partnership memo, and the diligence report." (each cited)
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
6. **Windows argument translation only rewrites bare paths (community-reported, thanks @headsvk).**
   Git Bash auto-translates POSIX-looking arguments into Windows paths via MSYS2's argv rewriting —
   but only when the argument *is* a path by itself, like `--add-dir /tmp/xxx`. A temp path embedded
   inside a full prompt **sentence** passed to `agy --print` never gets touched, so `agy.exe`
   receives a literal `/tmp/...` string it can't resolve — which looks exactly like the issue #76
   symptom above, but isn't. The actual fix: resolve the path through `cygpath -u` (for Bash) and
   `cygpath -m` (mixed-mode, readable by both the native binary and Bash tools) before it goes
   anywhere near the prompt text, with a no-op fallback on real Unix where `cygpath` doesn't exist.

## Multi-agent deep research: `/agy:deep-research`

The notebook command above offloads *reading* to Gemini. The newest command, `/agy:deep-research`,
offloads *web research* the same way — but the interesting part isn't the offloading, it's making
the result trustworthy instead of "an LLM skimmed some pages and wrote a summary."

The loop:

1. **Evidence matrix, not just a topic.** Claude decomposes the question into rows —
   `{ question, evidenceType, sourceQualityBar, recommendationChanging }` — before any browsing
   happens. `recommendationChanging: true` marks the rows whose answer could flip the final
   conclusion; those get weighed harder later.
2. **A plan you approve.** The matrix plus 3-6 research angles are shown before anything runs
   (skippable with `--yes`/`--background` once you trust the shape of the plan).
3. **Parallel browsing per angle, judged for convergence.** `agy` browses each angle concurrently;
   Claude reads the round's findings and decides whether another round would actually change the
   answer (`--depth L` caps at 2 rounds, `H` at 4) — instead of running a fixed number of passes
   regardless of whether they're adding anything.
4. **A red-team pass.** A separate `agy` call specifically attacks the claims that are
   single-source or load-bearing for the recommendation, before synthesis ever sees them.
5. **Honest coverage, by design.** The final report doesn't present everything with the same
   confidence. It states which angles completed and which were dropped, which
   `recommendationChanging` questions are still open, and which claims got downgraded to
   "single-source" after the red-team pass — a structured admission of what the research *didn't*
   manage to close, not just what it found. Overstating coverage is a design decision to avoid, not
   an accident to catch later.

`report.coverage` comes out pre-computed and deterministic, so the command renders the final
markdown straight from it — no re-scoring, no LLM re-grading its own homework at write time.

## Try it

```bash
# 1) install agy (Google Antigravity CLI), sign in once
# 2) in Claude Code:
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
/agy:setup        # health check
/agy:notebook  ./my-docs | what are the key facts and dates?
```

22 commands total — also audio/video transcription, media Q&A, single-shot web research, branded
HTML reports, code review, doc-to-markdown, browser recording, web scraping and UX audits. MIT, no
runtime deps, alpha, not affiliated with Google or Anthropic.

[github.com/MarcosNahuel/antigravity-plugin-cc](https://github.com/MarcosNahuel/antigravity-plugin-cc)

*What would you point a local NotebookLM at, or what would you want a research loop to red-team
before you trusted it? I'd love to hear it in the comments.*

---

I'm Nahuel, an AI engineer and co-founder at [TRAID](https://traidagency.com), where we build
automation and AI systems for e-commerce in LATAM/USA — this plugin is a side project, not a TRAID
product, but the same "don't overstate what the system actually did" instinct runs through both.
