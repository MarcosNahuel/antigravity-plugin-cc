# Social posts — antigravity-plugin-cc (ready to paste)

Repo: https://github.com/MarcosNahuel/antigravity-plugin-cc

> Tip: post the Reddit one to **r/ClaudeAI** and **r/ClaudeCode**. Post the X thread
> tagging **@AnthropicAI** and using **#ClaudeCode**. Attach the demo GIF
> (`docs/promo/notebook-demo.gif`) to both — it roughly doubles click-through.

---

## Reddit — r/ClaudeAI / r/ClaudeCode

**Title:** I built a local NotebookLM for Claude Code (offloads document reading to Gemini so it barely touches Claude's context)

**Body:**

I kept blowing up Claude Code's context window dumping PDFs and scans into it, so I built a plugin that hands the heavy reading to Google's Antigravity CLI (`agy`, Gemini 3.x — natively multimodal) and only brings back the synthesis.

`/agy:notebook <folder> | <objective>` sweeps a whole folder of documents — PDFs, scanned images, docx — and writes:

- a per-document summary
- a relevance index (what matters for your objective)
- a **cited** master synthesis
- a timeline + an entity sheet

Then `/agy:notebook-ask <folder> | <question>` answers follow-ups over those summaries **with citations**. Claude never ingests the raw documents, so a 200-page folder costs almost nothing in Claude tokens.

It also does stuff Claude Code can't do natively:
- `/agy:transcribe` — audio/video → faithful transcript + summary (voice notes, meetings, YouTube URLs)
- `/agy:media` — ask questions about an audio/video/image ("what was decided at 2:30?")
- plus deep web research with citations, browser-walkthrough recording, web scraping, doc→markdown, and design review.

MIT, no Node runtime. Install:

```
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
/agy:setup
```

(Needs the `agy` CLI + a Google sign-in.) Repo: https://github.com/MarcosNahuel/antigravity-plugin-cc — feedback welcome, especially on the notebook synthesis quality.

---

## X / Twitter — thread (tag @AnthropicAI, #ClaudeCode)

**1/**
I built a local NotebookLM for @AnthropicAI Claude Code.

`/agy:notebook <folder> | <objective>` reads a whole folder of PDFs/scans/docx in Gemini and returns a cited synthesis — so Claude's context stays clean.

Open source, MIT 👇 #ClaudeCode

**2/**
What it writes per run:
• per-document summaries
• a relevance index for your objective
• a CITED master synthesis
• a timeline + entity sheet

Then `/agy:notebook-ask` answers follow-ups with citations. A 200-page folder ≈ 0 Claude tokens.

**3/**
It also does what Claude Code can't natively:
• /agy:transcribe — audio/video → transcript (voice notes, meetings, YouTube)
• /agy:media — "what was decided at 2:30?"
• deep web research, browser recording, web scraping, doc→markdown, design review

**4/**
Install:

/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
/agy:setup

No Node runtime. Bridges to Google's `agy` CLI (Gemini 3.x).

Repo + demo 👇
https://github.com/MarcosNahuel/antigravity-plugin-cc

---

## LinkedIn (optional, more formal)

I just open-sourced **Antigravity Plugin** — a *local NotebookLM* for Claude Code.

It bridges Claude Code to Google's Antigravity CLI (Gemini 3.x, multimodal): point `/agy:notebook` at a folder of documents and it returns per-document summaries, a relevance index, a cited master synthesis, a timeline and an entity sheet — keeping the heavy document reading off Claude's own context. It also transcribes audio/video, does web research, records browser walkthroughs, and reviews designs.

MIT, no Node runtime. https://github.com/MarcosNahuel/antigravity-plugin-cc
