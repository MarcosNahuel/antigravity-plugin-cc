# Directory & list submissions — ready-to-paste entries

Reusable copy for getting `antigravity-plugin-cc` listed where people look for Claude Code plugins.
Pick a target, copy its entry, open a PR (fork → add line → PR).

## Canonical metadata (reuse anywhere)

- **Name:** Antigravity Plugin for Claude Code (`antigravity` / marketplace `marcosnahuel-antigravity`)
- **Repo:** https://github.com/MarcosNahuel/antigravity-plugin-cc
- **License:** MIT · **Runtime:** none (thin Bash forwarder over the `agy` CLI)
- **One-liner:** Bridge Claude Code to Google Antigravity (`agy` / Gemini 3.x) — a **local NotebookLM**, multi-agent deep research (`/agy:deep-research`), branded HTML reports, code review and more. 22 commands.
- **Install:** `/plugin marketplace add MarcosNahuel/antigravity-plugin-cc` → `/plugin install antigravity@marcosnahuel-antigravity`
- **Tags:** claude-code, claude-code-plugin, antigravity, agy, gemini, notebooklm, deep-research, document-analysis
- **Status:** alpha/experimental · not affiliated with or endorsed by Google or Anthropic

---

## 1) awesome-claude-code (the main list)

Repo: `hesreallyhim/awesome-claude-code` (search "awesome-claude-code" on GitHub for the current
canonical list; there are a few). These lists usually take a one-line entry under a section like
**Plugins** or **Tooling / Integrations**.

**Entry (markdown list item):**

```markdown
- [antigravity-plugin-cc](https://github.com/MarcosNahuel/antigravity-plugin-cc) — Bridges Claude Code to Google Antigravity (`agy` / Gemini 3.x). A **local NotebookLM** (`/agy:notebook`: folder → per-doc summaries + relevance index + cited synthesis + Q&A), multi-agent deep research with a red-team pass (`/agy:deep-research`), branded HTML reports, git-diff code review, doc-to-markdown, browser recording and UX audits. 22 commands, no Node runtime, MIT, alpha, not affiliated with Google or Anthropic.
```

**How:** fork the repo → add the line in the right section (keep alphabetical if the list is) →
follow its `CONTRIBUTING`/entry format (some use a script/JSON, some a table) → open a PR.

## 2) Claude Code plugin marketplaces / community catalogs

Several community "marketplace of marketplaces" repos aggregate `marketplace.json` sources. Submit
the marketplace, not just the plugin:

```markdown
- **marcosnahuel-antigravity** (`MarcosNahuel/antigravity-plugin-cc`) — `agy`/Gemini bridge: local NotebookLM, multi-agent deep research, reports, code review. 22 commands. `/plugin marketplace add MarcosNahuel/antigravity-plugin-cc`
```

## 3) Antigravity / Gemini ecosystem lists

`agy`-focused collections (e.g. `sickn33/antigravity-awesome-skills` and similar "awesome-antigravity"
/ "awesome-gemini-cli" lists). Entry:

```markdown
- [antigravity-plugin-cc](https://github.com/MarcosNahuel/antigravity-plugin-cc) — Use `agy` from inside Claude Code: 22 slash commands incl. a local NotebookLM over a folder of documents, multi-agent deep research, and branded HTML reports. Full issue-#76 handling + Windows mitigations.
```

> Note: geminicli.com/extensions lists **gemini-cli** extensions specifically; this is a *Claude Code*
> plugin wrapping `agy`, so it may not fit there. Better fit: Claude Code + Antigravity lists.

## 4) Product directories (later phase — see LAUNCH-CHECKLIST.md, not day 1)

- **Product Hunt** — title "Antigravity Plugin for Claude Code", tagline "A local NotebookLM and
  multi-agent deep research for Claude Code, powered by Gemini's agy CLI". First comment = the
  "Why" from the dev.to post. Maker self-launch (12:01 AM PT), only after Show HN/Reddit have given
  the repo some organic stars — cold-launching PH with zero prior traction rarely clears the
  front page.
- **AlternativeTo** — list under NotebookLM alternatives (self-hosted / local, open-source).

## Submission checklist

- [ ] README is current (22 commands, hero section, alpha badge, non-affiliation disclaimer) — done.
- [ ] `CHANGELOG.md` reflects the latest tag (v1.5.1) — done.
- [ ] A short demo (GIF or the cited-Q&A snippet) in the README — done (`docs/promo/notebook-demo.gif`).
- [ ] Repo has topics/keywords set on GitHub (Settings → Topics): `claude-code-plugin`, `agy`,
      `gemini`, `notebooklm`, `deep-research`, `document-analysis`.
- [ ] One PR per list; link them here as you go.
