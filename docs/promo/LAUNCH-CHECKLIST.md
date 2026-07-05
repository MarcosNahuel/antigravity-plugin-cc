# Launch checklist — antigravity-plugin-cc v1.5.1

Sequenced per the research playbook (`CONOCIMIENTO-NAHUEL/docs/agy/research/2026-07-05-promocion-plugin-marca-personal.md`):
**hygiene → passive distribution → active launch**, in that order. Each phase earns the credibility
that makes the next one land. Do not skip ahead to Phase 2 with an empty Phase 1.

Guiding rules for every step below:
- Technical education first, promotion never leads. TRAID gets mentioned once, softly, at the end
  — never in a headline or opening line.
- No superlatives, no star-begging, no unedited AI-sounding copy.
- Every public post carries: **alpha/experimental**, **not affiliated with/endorsed by Google or
  Anthropic**, and BYOK (your own Google login / API key — nothing scraped or proxied).
- Stars are not the goal. Track: comments that ask real questions, forks, and any DM/email that
  mentions wanting implementation help — that's the actual signal for the credibility-wedge offer.

---

## ⚠️ Open flag before Phase 2 — resolve first

- [ ] **ToS/AUP gap is not resolved.** The research explicitly flags that Anthropic's and Google's
      exact terms on wrapping `--print`/headless CLIs — and whether there's real enforcement
      precedent against BYOK wrappers like this one — were **not independently verified**
      (`[UNVERIFIED]` in the source research). The plugin already does the safe thing architecturally
      (BYOK, no token scraping/proxying, no vendor names in the product name), which is the
      practical mitigation. But before actively driving traffic (Show HN / Reddit / PH), do a quick
      re-read of the current Anthropic Consumer/Commercial Terms and Google's terms for Antigravity
      CLI to confirm nothing changed. This is a flag to close, not a blocker that's been resolved —
      don't skip it because Phase 0/1 already shipped the disclaimer.

---

## Phase 0 — Repo hygiene (mostly done)

- [x] README rewritten as a landing page: value prop above the fold, demo GIF, one-command
      quickstart, alpha badge, non-affiliation disclaimer, `/agy:deep-research` featured.
- [x] `SUPPORT.md` — "side project, best-effort, no SLA" + commercial-support line to TRAID.
- [x] `SECURITY.md` present.
- [x] Version bumped to **1.5.1**, `CHANGELOG.md` current, command count consistent at **22**
      everywhere (README, `plugin.json`, `marketplace.json`).
- [x] BYOK stated explicitly (own Google login / API key, nothing scraped or proxied).
- [ ] Spot-check `CITATION.cff` version/date match the current tag (flagged stale at v0.1.0 in a
      prior audit — confirm it now says 1.5.1 before any launch post links to it).
- [ ] Confirm GitHub repo **Topics** are set (Settings → Topics): `claude-code-plugin`, `agy`,
      `gemini`, `notebooklm`, `deep-research`, `document-analysis` — cheap SEO/discoverability, do
      it once.

## Phase 1 — Passive distribution (do before any active launch post)

Do these in any order; none require timing coordination with each other.

- [ ] **Own marketplace** — already live at `MarcosNahuel/antigravity-plugin-cc`
      (`marcosnahuel-antigravity`). Nothing to do, just don't forget it's the install path every
      draft below points to.
- [ ] **awesome-claude-code submission** — use `docs/promo/awesome-claude-code-submission.md`.
      Submit via their **web form** (`hesreallyhim/awesome-claude-code` issue template
      `recommend-resource.yml`) — **not** the `gh` CLI, their CONTRIBUTING explicitly bans
      programmatic submissions and auto-closes them.
- [ ] **Secondary plugin-list PR** — `ccplugins/awesome-claude-code-plugins` or similar, one-line
      marketplace entry (see bottom of `awesome-claude-code-submission.md`).
- [ ] **Directory PRs** — `docs/promo/directory-submissions.md` has ready entries for the
      Antigravity/Gemini ecosystem lists and MCP-adjacent directories. One PR per list, don't batch.
- [ ] **MCP Registry / MCP.directory** — check whether this project is a fit (it's a Claude Code
      plugin, not an MCP server — confirm before submitting; don't force a category mismatch).

## Phase 2 — Active launch (48-72h window, sequenced, not simultaneous)

Do not post the same link to more than one platform on the same day — cross-posting the identical
GitHub link across communities in a tight window reads as spam to Reddit's filters and to human
readers on both sides.

- [ ] **Day 1 — Show HN.** Use `docs/promo/show-hn.md`. Post from a personal HN account. No
      waitlist/signup wall. Timing is a trade-off (see the file's note) — pick a slot you can
      actually defend with fast replies for 2-3 hours, don't over-optimize the exact hour.
      Post the first-author comment immediately after submitting.
- [ ] **Day 2 — X thread + LinkedIn post.** Use `docs/promo/social-posts.md`. X thread in English
      (deep-research architecture + the Windows path gotcha). LinkedIn post in Spanish (link goes
      in the **first comment**, not the post body — external links in the body suppress reach).
- [ ] **Day 3 — Reddit, one sub.** Use `docs/promo/reddit.md`. Post **r/LocalLLaMA** first (best
      fit for the local-first angle); post **r/ClaudeAI** on a *different* day, not the same day —
      space them out. Confirm the posting account has enough karma/age first (see the file's
      warm-up note) or the link gets auto-filtered before a human ever sees it.
- [ ] **dev.to article.** Use `docs/promo/dev-to-article.md`. Flip `published: true` in the
      frontmatter when pasting it in. Good to publish alongside Day 2 or Day 3 — it's reference
      material other posts can link to, not a launch event itself.
- [ ] **Product Hunt — only after the above have produced some organic stars/traffic.** Maker
      self-launch at 12:01 AM PT. **DST/timezone note:** 12:01 AM PT is currently **UTC-7** (US
      Pacific Daylight Time, roughly Mar-Nov) or **UTC-8** in Pacific Standard Time (roughly
      Nov-Mar) — double-check which one applies on the actual launch date, since Argentina (UTC-3,
      no DST) doesn't shift and the gap between the two changes by an hour depending on the season.
      Plan to be awake and answering comments for 12-16h after posting.
- [ ] **WhatsApp share** (`docs/promo/whatsapp.txt`) — send to peers/community whenever feels
      natural, not tied to the Show HN/PH timing. It's value-first, not a launch broadcast.

## After the launch window

- [ ] Write the honest post-mortem (numbers, what worked, what flopped) — this is the actual
      credibility wedge per the research, more than the launch itself. Candidate home: a dev.to
      follow-up or a LinkedIn post once there's something real to report.
- [ ] Track Fork-to-Star ratio and any inbound message that mentions wanting help implementing this
      (or similar local-AI/agentic tooling) for their own stack — that's the qualified-lead signal,
      not the star count.
- [ ] Re-check `SUPPORT.md`'s "best-effort" framing is holding up under whatever issue volume shows
      up; triage once a week, don't let it become unpaid on-call.
