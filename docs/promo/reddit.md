# Reddit drafts (ready to paste)

> **Ground rules before posting anywhere (per the research, don't skip):**
> - **Disclose upfront that you're the creator.** "I built this" in the first sentence, not buried.
>   Transparency is what separates a war-story post from astroturfing.
> - **Value before the link.** Lead with the problem and how it's solved; the repo link comes after
>   the reader already got something out of the post, not before.
> - **Account warm-up matters.** Big subs auto-filter external links from accounts with low comment
>   karma or under ~30 days old. If the posting account is new or low-karma, spend a couple weeks
>   commenting genuinely in the target subs first — there's no way around this, it's an algorithmic
>   gate, not a suggestion.
> - **One post, one sub, one day.** Don't drop the same GitHub link across multiple subreddits in the
>   same day/week — that pattern trips Reddit's cross-posting spam filter platform-wide (silent
>   shadowban, not a visible rejection). Space them out and let each post stand on its own.
> - **Never ask for upvotes** anywhere (here, X, Discord) — that's vote manipulation and risks a
>   domain-wide ban, not just a post removal.
> - **Format as a war story / case study**, not a launch announcement. "Here's a problem I had and
>   how I solved it" reads very differently from "check out my new product."
> - r/LocalLLaMA is receptive to local/open tooling — lead with the local-first angle. r/ClaudeAI sees
>   a lot of "I built a wrapper" posts; be specific about what's actually new (`/agy:deep-research`)
>   rather than re-pitching the whole plugin.
> - Both drafts carry the alpha/non-affiliation framing already — keep it in if anyone asks.

---

## r/LocalLLaMA

**Title:**
```
I built a local, no-cloud NotebookLM alternative — folder of docs in, cited synthesis out (Claude Code plugin, Gemini via Google's agy CLI)
```

**Body:**
```
I'm the author — figured this sub would appreciate the local-first angle more than most.

I use NotebookLM a lot but kept hitting the same wall: I have documents I can't upload to a
third-party product — contracts, an RFP, unreleased research. And even when I could, dumping
forty PDFs into an LLM's context to ask questions about them is slow and expensive.

So I built a Claude Code plugin that does the NotebookLM workflow locally, using Google's new
Antigravity CLI (`agy`, Gemini 3.x) as the reading engine, on your own account — nothing gets
uploaded to a product, nothing gets proxied or scraped.

Point it at a folder:

- one objective-driven summary per document (handles PDFs, scanned images, docx — hybrid text
  extraction + multimodal OCR for scans)
- a relevance index ranked against your objective
- a cited master synthesis (every claim traces back to a source document)
- a timeline and an entity sheet (people, orgs, amounts, dates)

Then ask follow-up questions and get answers **with citations**, without re-reading the originals.

The part that made this worth building instead of just using NotebookLM: the heavy reading
happens entirely in Gemini via agy, and only the small final synthesis comes back to Claude — so
a 200-page folder costs almost nothing in Claude's own context. There's also a SQLite-backed mode
(`/agy:notebook-query`) that turns the same corpus into a queryable DB with FTS5, so you can ask
"sum the amounts by category" and get a deterministic answer instead of an LLM doing arithmetic.

It also does audio/video transcription and Q&A ("what was decided at 2:30?") — things Claude Code
has no native way to do, since it can't hear or watch.

MIT license, alpha/experimental (it's built on a CLI Google shipped a couple months ago and could
change under me), no Node runtime — it's a thin Bash forwarder. Not affiliated with Google or
Anthropic. Repo: https://github.com/MarcosNahuel/antigravity-plugin-cc

Genuinely curious if others here have hit the same "can't upload it, don't want to pay Claude
context for it" problem and how you've solved it.
```

---

## r/ClaudeAI

**Title:**
```
Added multi-agent deep research to my Claude Code plugin — agy browses in parallel, Claude red-teams the claims before writing the report
```

**Body:**
```
I'm the author of antigravity-plugin-cc (a Claude Code plugin that bridges to Google's agy CLI /
Gemini 3.x) — wanted to share the newest piece, `/agy:deep-research`, since the architecture might
be useful to anyone building research or fact-checking workflows on top of Claude Code.

The problem with single-shot "web research" commands: they read a handful of pages and write
whatever they found, with no signal on how thorough the pass actually was. `/agy:deep-research`
tries to fix that:

1. Claude decomposes the question into an evidence matrix (which sub-questions matter, which ones
   could flip the final recommendation if the answer changed) and a set of research angles.
2. You approve the plan (or edit it) before anything runs.
3. agy browses each angle in parallel, one round at a time. Claude judges convergence between
   rounds instead of just running a fixed number of passes.
4. A red-team pass — also run through agy — specifically attacks single-source claims and
   anything load-bearing for the final recommendation.
5. The report is generated with an explicit coverage section: which angles completed, which got
   dropped, which critical questions are still open, and which claims got downgraded because they
   only had one source. It's designed to under-claim rather than present partial research as
   complete.

It complements the existing `/agy:research` (still there, still the fast single-shot option) —
Claude now routes between the two based on whether you're doing a quick lookup or something you're
going to act on.

The plugin also has a local-NotebookLM mode (folder of docs → cited synthesis, keeps the heavy
reading out of Claude's context) and audio/video transcription, if that's useful to anyone. 22
commands total, MIT, alpha, no Node runtime. Not affiliated with Anthropic or Google.

https://github.com/MarcosNahuel/antigravity-plugin-cc

Happy to talk through the convergence/red-team logic if anyone's building something similar —
that part took a few iterations to get right.
```
