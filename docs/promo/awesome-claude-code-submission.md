# awesome-claude-code submission (ready to paste)

> ⚠️ **hesreallyhim/awesome-claude-code requires a HUMAN submission via the github.com web form.**
> Their template states submissions via `gh` CLI / programmatic means violate the Code of Conduct and
> are auto-closed. So **do not** open it with the CLI — paste the fields below into the web form.
>
> **Form:** https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml
> (Repo must be ≥1 week old — fine. Be ready to confirm you've reviewed the list.)

Lead with the **differentiated flagship** (the local NotebookLM), not "15 commands" — their guidance
prefers focused resources over general-purpose marketplaces.

---

## Field-by-field

- **Display Name:** `Antigravity Plugin — local NotebookLM for Claude Code`
- **Category:** `Agent Skills` *(their note: plugins are currently lumped under Agent Skills)*
- **Sub-Category:** `General`
- **Primary Link:** `https://github.com/MarcosNahuel/antigravity-plugin-cc`
- **Secondary Link:** `https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/latest`
- **Author Name:** `Marcos Nahuel Albornoz`
- **Author Link:** `https://github.com/MarcosNahuel`
- **License:** `MIT`

- **Description:**
  > A **local NotebookLM** for Claude Code. `/agy:notebook <folder> | <objective>` reads a whole folder
  > of documents (PDFs, scans, images, docx) via Google Antigravity's `agy` CLI (Gemini 3.x, multimodal)
  > and writes a per-document summary, a relevance index, a **cited** master synthesis, a timeline and an
  > entity sheet — then `/agy:notebook-ask` answers questions over them with citations. All the document
  > reading happens in Gemini, so it barely touches Claude's context. Also transcribes audio/video
  > (`/agy:transcribe`, `/agy:media`) — things Claude Code can't do natively. The `agy` bridge and a
  > migration path off the deprecated `gemini-cli`. MIT, no Node runtime.

- **Install:**
  ```
  /plugin marketplace add MarcosNahuel/antigravity-plugin-cc
  /plugin install antigravity@marcosnahuel-antigravity
  /agy:setup
  ```
  (Requires the Google Antigravity `agy` CLI installed + a Google sign-in.)

- **Uninstall:**
  ```
  /plugin uninstall antigravity@marcosnahuel-antigravity
  /plugin marketplace remove marcosnahuel-antigravity
  ```

### Required disclosures (their template asks for these explicitly)

- **Network requests beyond the Anthropic API:** Yes. The plugin forwards prompts to the local `agy`
  CLI, which calls **Google Antigravity / Gemini** endpoints (`*.googleapis.com`) under the user's own
  Google account. The plugin itself makes no other network calls.
- **`--dangerously-skip-permissions`:** Used **internally** when the plugin invokes `agy --print` so the
  unattended subprocess can auto-approve `agy`'s own tool prompts (write_file, etc.). It does **not**
  pass `--dangerously-skip-permissions` to Claude Code, and does not bypass Claude's permissions.
- **No auto-update / no `npx @latest`.** Updates are explicit via `/plugin` + a tagged release.
- **Demo:** see the README "Flagship: a local NotebookLM" section and the
  [`docs/promo/dev-to-article.md`](dev-to-article.md) walkthrough (cited Q&A example included).

---

## Secondary target (optional, PR-friendly)

`ccplugins/awesome-claude-code-plugins` (plugin-specific list / marketplace aggregator, ~850★) accepts
contributions for "your own marketplace". A PR adding the marketplace line is appropriate:

```
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
```
with the one-liner: *"agy/Gemini bridge for Claude Code — a local NotebookLM, audio/video transcription,
web research, branded reports. 15 commands."* Check their `CONTRIBUTING` for the exact file to edit.
