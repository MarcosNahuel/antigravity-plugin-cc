# Directory & list submissions — ready-to-paste entries

Reusable copy for getting `antigravity-plugin-cc` listed where people look for Claude Code plugins.
Pick a target, copy its entry, open a PR (fork → add line → PR).

## Canonical metadata (reuse anywhere)

- **Name:** Antigravity Plugin for Claude Code (`antigravity` / marketplace `marcosnahuel-antigravity`)
- **Repo:** https://github.com/MarcosNahuel/antigravity-plugin-cc
- **License:** MIT · **Runtime:** none (thin Bash forwarder over the `agy` CLI)
- **One-liner:** Bridge Claude Code to Google Antigravity (`agy` / Gemini 3.x) — a **local NotebookLM**, deep web research with citations, branded HTML reports, code review and more. 13 commands.
- **Install:** `/plugin marketplace add MarcosNahuel/antigravity-plugin-cc` → `/plugin install antigravity@marcosnahuel-antigravity`
- **Tags:** claude-code, claude-code-plugin, antigravity, agy, gemini, notebooklm, deep-research, document-analysis

---

## 1) awesome-claude-code (the main list)

Repo: `hesreallyhim/awesome-claude-code` (search "awesome-claude-code" on GitHub for the current
canonical list; there are a few). These lists usually take a one-line entry under a section like
**Plugins** or **Tooling / Integrations**.

**Entry (markdown list item):**

```markdown
- [antigravity-plugin-cc](https://github.com/MarcosNahuel/antigravity-plugin-cc) — Bridges Claude Code to Google Antigravity (`agy` / Gemini 3.x). A **local NotebookLM** (`/agy:notebook`: folder → per-doc summaries + relevance index + cited synthesis + Q&A), deep web research with citations, branded HTML reports, git-diff code review, doc-to-markdown, browser recording and UX audits. No Node runtime; MIT.
```

**How:** fork the repo → add the line in the right section (keep alphabetical if the list is) →
follow its `CONTRIBUTING`/entry format (some use a script/JSON, some a table) → open a PR.

## 2) Claude Code plugin marketplaces / community catalogs

Several community "marketplace of marketplaces" repos aggregate `marketplace.json` sources. Submit
the marketplace, not just the plugin:

```markdown
- **marcosnahuel-antigravity** (`MarcosNahuel/antigravity-plugin-cc`) — `agy`/Gemini bridge: local NotebookLM, research, reports, code review. `/plugin marketplace add MarcosNahuel/antigravity-plugin-cc`
```

## 3) Antigravity / Gemini ecosystem lists

`agy`-focused collections (e.g. `sickn33/antigravity-awesome-skills` and similar "awesome-antigravity"
/ "awesome-gemini-cli" lists). Entry:

```markdown
- [antigravity-plugin-cc](https://github.com/MarcosNahuel/antigravity-plugin-cc) — Use `agy` from inside Claude Code: 13 slash commands incl. a local NotebookLM over a folder of documents, deep web research, and branded HTML reports. Full issue-#76 handling + Windows mitigations.
```

> Note: geminicli.com/extensions lists **gemini-cli** extensions specifically; this is a *Claude Code*
> plugin wrapping `agy`, so it may not fit there. Better fit: Claude Code + Antigravity lists.

## 4) Product directories (optional)

- **Product Hunt** — title "Antigravity Plugin for Claude Code", tagline "A local NotebookLM (and
  more) for Claude Code, powered by Gemini's agy CLI". First comment = the "Why" from the blog post.
- **AlternativeTo** — list under NotebookLM alternatives (self-hosted / local, open-source).

## Submission checklist

- [ ] README is current (13 commands, hero section) — done.
- [ ] `CHANGELOG.md` reflects the latest tag.
- [ ] A short demo (GIF or the cited-Q&A snippet) in the README.
- [ ] Repo has topics/keywords set on GitHub (Settings → Topics): `claude-code-plugin`, `agy`,
      `gemini`, `notebooklm`, `document-analysis`.
- [ ] One PR per list; link them here as you go.
