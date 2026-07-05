# Show HN draft (ready to paste)

> **Rules before posting (Y Combinator guidelines — don't skip):**
> - Post from your **personal** HN account, not a corporate/brand one.
> - No waitlist, no signup wall, no email gate — the thing has to be usable the moment someone clicks.
> - Title stays neutral: `Show HN: <what it is>` — no adjectives, no "revolutionary", no emoji.
> - The first comment should be **substantive, not polished marketing copy**. Per the research,
>   an over-produced first comment can read as promotional and hurt more than a slightly rough one.
>   Leave the hedges and trade-offs in; don't sand them off.
> - Timing is a trade-off, not a formula: weekday daytime (US) gets more traffic but more competition;
>   quieter windows (weekend, early US morning) mean less competition but a smaller ceiling. Pick a
>   time you can actually sit at the keyboard for 2-3 hours after posting — replying fast in the first
>   hour matters more than the exact slot.
> - Be around to answer comments for the first few hours. Don't cross-post the same link to Reddit the
>   same day — let each community find it on its own terms.
> - This project is **alpha/experimental** and **not affiliated with Google or Anthropic** — say so
>   plainly if anyone asks; don't let the thread imply endorsement.

---

## Title

```
Show HN: A local NotebookLM for Claude Code, built on Google's Antigravity CLI
```

(Alternative if the above reads too close to a product name: `Show HN: I wrapped Google's new agy CLI into a local, cited NotebookLM for Claude Code`)

## Body (submission text)

```
I kept needing to ask questions over folders of PDFs and scans — contracts, RFPs, research
papers — without uploading them anywhere. This is a Claude Code plugin that bridges to Google's
Antigravity CLI (agy, Gemini 3.x) to do that locally: point it at a folder and it writes a
per-document summary, a relevance index, and a cited synthesis, then answers follow-up questions
with citations back to the source doc. It also does multi-agent deep web research (an evidence
matrix + a plan you approve, agy browsing each angle in parallel, a red-team pass on the shakiest
claims, then a cited report), plus audio/video transcription and a few other things Claude Code
can't do natively. MIT, alpha, no Node runtime, not affiliated with Google or Anthropic.

https://github.com/MarcosNahuel/antigravity-plugin-cc
```

## First comment (post immediately after submitting, from the author account)

```
Author here. A few notes on why this exists and how it's built, since "wraps another company's
CLI" always raises fair questions.

Why: I don't want to upload contracts, RFPs, or unreleased research to a third-party product to
ask questions about them, and reading forty 40-page PDFs inside Claude Code eats the context
window fast. Google shipped Antigravity CLI (agy) at I/O 2026 as the successor to gemini-cli —
it's a Go binary, natively multimodal, and does the heavy document reading well. So the plugin is
a thin Bash forwarder: a Claude Code slash command parses the request, fans it out to a subagent,
and the subagent shells out to `agy --print`. No Node runtime, no MCP server, no daemon.

Two gotchas cost me real time and are worth naming in case anyone else hits them:

1. `agy --print`, called from a non-interactive subprocess, exits 0 and writes literally nothing
   to stdout — even on success (this is a known upstream issue, #76 in their tracker). The fix is
   to never trust stdout: tell agy to `write_file` its output to a path, and read the file instead.
2. On Windows, Git Bash auto-translates POSIX-looking arguments into Windows paths (MSYS2's argv
   translation) — but only when the argument IS a path by itself, like `--add-dir /tmp/xxx`. A
   temp path embedded inside a full prompt *sentence* passed to `--print` never gets translated,
   so agy.exe receives a literal `/tmp/...` string it can't resolve. Took a community bug report
   to catch it (thanks @headsvk) — the fix is running the path through `cygpath -u`/`cygpath -m`
   before it goes anywhere near the prompt text.

The most interesting part architecturally is the deep-research command
(`/agy:deep-research`): it builds an evidence matrix from the question, gets your sign-off on a
research plan, then runs agy browsing each angle in parallel while Claude judges convergence
across rounds and runs a red-team pass on single-source or conclusion-flipping claims before
writing the report. The report is deliberately honest about its own coverage — it lists which
angles it dropped and which critical questions it couldn't close, instead of presenting
everything with the same confidence. I'd rather it under-claim than read like it solved something
it didn't.

Trade-offs, plainly: this is a wrapper around someone else's CLI that Google could change or
deprecate without notice (the whole reason this exists is that they just deprecated the previous
one). It requires the user's own Google/Gemini login — nothing is scraped or proxied. It's alpha:
I wouldn't point it at anything business-critical yet, and I say so in the repo. It's not
affiliated with or endorsed by Google or Anthropic — "Antigravity" and "Claude" are their marks,
this just talks to their public CLIs.

Happy to go into more detail on any part of this — the rate-limit handling, the OCR page-chunking
for large scanned PDFs, or the convergence logic in the research loop.
```
