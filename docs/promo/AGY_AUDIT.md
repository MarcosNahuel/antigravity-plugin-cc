# Audit Report: Antigravity Claude Code Plugin

This audit analyzes the stability, UX consistency, version alignment, and discoverability of the `antigravity` plugin (**v0.7.0**) bridging Claude Code to the Google Antigravity CLI (`agy` / Gemini 3.x).

---

# Executive Summary - Top 5 Actions

1. **Fix Command Count and List Mismatches (High Impact)**: Correct the command count across `README.md` (lines 3, 22), `.claude-plugin/plugin.json` (line 4), and `marketplace.json` (lines 9, 30) from "13" to "15", and explicitly list `/agy:transcribe` and `/agy:media` in all manifests.
2. **Synchronize `llms.txt` Command Listing & Model Info (High Impact)**: `llms.txt` (line 23) only lists 3 commands instead of 15 and contains stale claims about the `--model` flag (line 19) that contradict the updated version support (agy 1.0.5+).
3. **Update CITATION.cff Version Mismatch (Medium Impact)**: `CITATION.cff` (line 15) lists version `0.1.0` (released on 2026-05-23) instead of `0.7.0`.
4. **Fix the Missing `WRITE_FILE` in `review.md` (Medium Impact)**: `plugins/antigravity/commands/review.md` (line 45) passes an empty `WRITE_FILE:` header, relying on the subagent's internal fallback rather than following the standard explicit write-then-read discipline.
5. **Publish the `dev-to-article.md` and Submit to awesome-lists (Low Impact)**: The dev.to article (currently drafted as `published: false`) should be finalized and published to capture developer mindshare on the June 2026 Gemini CLI deprecation.

---

# Alta (High Impact)

### 1. Command Registry & Listing Discrepancies
There is a major disconnect between the actual commands implemented (15 commands) and how they are advertised in the metadata:
* **`README.md`**:
  * [README.md:3](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/README.md#L3) claims: *"A local NotebookLM — and 12 more commands"* (totaling 13).
  * [README.md:22](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/README.md#L22) claims: *"Thirteen slash commands"*.
  * However, the table in [README.md:100-116](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/README.md#L100-L116) correctly lists **15 commands** (including `/agy:transcribe` and `/agy:media`).
* **`plugin.json`**:
  * [plugin.json:4](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/plugins/antigravity/.claude-plugin/plugin.json#L4) claims: *"Thirteen slash commands"* but only lists 12 in the description block, entirely omitting `notebook-ask`, `transcribe`, and `media`.
* **`marketplace.json`**:
  * [marketplace.json:9](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/.claude-plugin/marketplace.json#L9) claims: *"Thirteen slash commands"*.
  * [marketplace.json:30](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/.claude-plugin/marketplace.json#L30) lists 13 commands, omitting `transcribe` and `media`.
* **`llms.txt`**:
  * [llms.txt:23](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/llms.txt#L23) claims: *"Three slash commands"* and only lists `/agy:research`, `/agy:rescue`, and `/agy:setup`. This is extremely outdated.

### 2. Stale Model Selection Claims in `llms.txt`
* [llms.txt:19](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/llms.txt#L19) and [llms.txt:33](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/llms.txt#L33) assert that the `agy` CLI 1.0.x does not expose a `--model` flag. This directly contradicts the updated information in the `CHANGELOG.md` ([CHANGELOG.md:192](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/CHANGELOG.md#L192)) and `README.md` ([README.md:126](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/README.md#L126)), which correctly note that `agy 1.0.5+` accepts the `--model` flag.

### 3. Scaling & Rate-Limit Vulnerability in `/agy:notebook`
* Although `/agy:notebook` implements a concurrency wave of up to 10 and a retry/backoff loop ([notebook.md:155-171](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/plugins/antigravity/commands/notebook.md#L155-L171)), large folders with dozens of scanned documents can still trigger severe rate-limiting (429) or exceed Claude's execution time constraints. A hard warning for directory sizes >30 files should be displayed before starting the sweep.

---

# Media (Medium Impact)

### 1. CITATION.cff Stale Metadata
* [CITATION.cff:15](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/CITATION.cff#L15) lists version `"0.1.0"` and [CITATION.cff:16](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/CITATION.cff#L16) lists date-released `"2026-05-23"`. Both must be bumped to `"0.7.0"` and `"2026-06-19"` to align with the current git tag `v0.7.0` and other package manifests.

### 2. Missing `WRITE_FILE` Target in `review.md`
* In [review.md:45](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/plugins/antigravity/commands/review.md#L45), the header block specifies:
  ```yaml
  WRITE_FILE:
  ```
  Leaving this empty means the command depends on the subagent (`agy-rescue.md`) generating a local temp file path internally. For consistency with the standard issue #76 workaround, the command should generate the path and explicitly define the `WRITE_FILE` destination in the header block.

### 3. Missing SEO Headings in README
* Key keywords like `notebooklm claude code`, `claude code plugin gemini`, and `audio transcription claude code` do not appear in any header tags inside `README.md`. While the keywords are present in the text, incorporating them into `#` or `##` headers would significantly improve GitHub search indexation.

---

# Baja (Low Impact)

### 1. `dev-to-article.md` Remains Unpublished
* The promotional article [dev-to-article.md](file:///C:/Users/malbornoz/OneDrive/GitHub/antigravity-plugin-cc/docs/promo/dev-to-article.md) is marked as `published: false` (line 3). Given that the Gemini CLI deprecation date has passed (June 18, 2026), this article should be published immediately with tags `#claudecode`, `#gemini`, `#opensource` to capture developers searching for alternatives.

### 2. Standardized Output Verification
* While `transcribe.md` and `media.md` correctly follow the `write_file` workaround due to gotcha (a), they rely entirely on the subagent to run Plan B transcript recovery. It is worth adding a reminder in the commands' user-facing text explaining that transcription audio files should be kept short to avoid timing out the subagent.
