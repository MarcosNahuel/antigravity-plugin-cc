# Bootstrap prompt — set up the full Antigravity agent stack on a machine

Paste everything below the `=== PROMPT ===` line into **Claude Code on the target machine** (your
notebook/laptop). It checks what's installed, installs only what's missing (idempotent, asks before
anything heavy), and verifies the whole stack works end-to-end. It will NOT do anything destructive.

The stack it sets up turns Claude Code into a much more capable agent by offloading heavy work to
Google's Antigravity CLI (`agy` / Gemini): read whole folders of documents (local RAG), build
knowledge **graphs**, transcribe audio/video, research the web — all off Claude's token budget.

---

=== PROMPT ===

You are setting up the **Antigravity agent stack** on THIS machine. Work step by step, **check before
installing** (everything is idempotent), explain what you do, and never run anything destructive. At
the end print a status table of every component. If a step needs me to act (sign-in, a GUI install),
stop and tell me exactly what to do.

## 1. agy CLI (Google Antigravity)
- Check: run `agy --version` (Windows: also try `~/AppData/Local/agy/bin/agy.exe --version`).
- If missing: tell me to install it from https://antigravity.google and run `agy` once to sign in
  (Google OAuth — no API key). Do NOT try to automate the sign-in.
- Verify auth with a tiny write-file ping (it must write a file): from a fresh temp dir, run
  `agy --dangerously-skip-permissions --add-dir <tmp> --print-timeout 60s --print "Write the text PONG to <tmp>/pong.txt with your write_file tool. That file is your only deliverable." < /dev/null`
  then check `<tmp>/pong.txt` exists. Ignore "not logged into Antigravity"/"FetchAvailableModels"
  lines in the output — those are NON-FATAL noise; the real health signal is the file on disk.

## 2. The antigravity plugin (this plugin)
- In Claude Code: `/plugin marketplace add MarcosNahuel/antigravity-plugin-cc` (or
  `/plugin marketplace update marcosnahuel-antigravity` if already added), then
  `/plugin install antigravity@marcosnahuel-antigravity` (or update it), then **restart Claude Code**.
  The plugin only loads after a restart — tell me to restart and re-run this prompt to continue if needed.
- Confirm with `/agy:setup`.

## 3. Python deps the plugin uses (check, install only what's missing)
- **PyMuPDF** (`python -c "import fitz"`) — required by `/agy:notebook` to read PDFs. If missing:
  `pip install pymupdf`.
- **sqlite-vec** (`python -c "import sqlite_vec"`) — OPTIONAL, only for `/agy:notebook --semantic`
  (vector search). If you want semantic search: `pip install sqlite-vec`. Skip otherwise.
- **ffmpeg** (`ffmpeg -version`) — OPTIONAL, only to split long audio/video for `/agy:transcribe`.
- (Real semantic embeddings also need a real `GEMINI_API_KEY`; without one, the fallback is keyword-ish.)

## 4. Graphify (knowledge graphs — built locally for free, named by Gemini)
- Run the plugin's installer (idempotent — installs `graphifyy` from PyPI, and migrates the old
  patched clone if this machine still has one):
  `python "<plugin>/plugins/antigravity/scripts/graphify_install.py"`
  (resolve `<plugin>` to where the plugin is installed; on a fresh marketplace install it's under
  `~/.claude/plugins/.../antigravity/`. If you can't find it, clone the repo
  `https://github.com/MarcosNahuel/antigravity-plugin-cc` and use that path.)
- It needs `pip` and prints `READY` when done (`READY_NO_AGY` = graphs work, community naming is off).
  `--check` reports status without installing.

## 5. End-to-end verification (do a real smoke test of each capability)
- **Notebook RAG**: make a tiny temp folder with 2 short `.txt`/`.pdf` docs, run
  `/agy:notebook <folder> | objetivo de prueba`, then `/agy:notebook-query <folder> | SELECT * FROM v_montos`.
  Confirm `notebook.db` was built and the query returns rows (or an empty result without error).
- **Graph**: run `/agy:graph <same folder>` and confirm `graphify-out/graph.json` + `GRAPH_REPORT.md`
  appear with a **non-zero** node count (a run that says "graph is empty" still exits 0 — that is a
  failure, not a result) and that the communities carry real names rather than "Community 0/1/2".
- **Media** (optional, if I give you a file): `/agy:transcribe <audio-or-youtube-url>`.

## 6. Report
Print a table: component · status (OK / MISSING / OPTIONAL-skipped) · how to fix if not OK. Then list
the capabilities now available (`/agy:notebook`, `/agy:notebook-query`, `/agy:graph`,
`/agy:transcribe`, `/agy:media`, `/agy:research`, …) and one example command for each. Keep my
documents local — nothing in this stack uploads them anywhere except my own Gemini account via agy.

=== FIN DEL PROMPT ===
