---
description: Check the progress of a /agy:notebook sweep (for long expedientes run with --background). Reports % complete, done/pending/failed counts, elapsed time and a rough ETA, and which documents are still pending — so you can resume. Read-only, no agy.
argument-hint: "<folder>"
context: fork
allowed-tools: Bash, Read
---

Report the status of a notebook sweep without re-running it. Useful for a long, `--background` sweep
over a 200-page expediente: the job record (`<OUTDIR>/.jobs/current.json`) tracks per-document
progress derived from the manifest + the summary files on disk.

Raw user request:
$ARGUMENTS

## Phase 0 — Resolve + report (ONE Bash call)

Resolve `OUTDIR = docs/agy/notebook/<slug>` from the folder argument (same `slug()` the notebook
uses). Then:

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/notebook_job.py" status "$OUTDIR"
```

It prints the progress line (`NOTEBOOK SWEEP — NN% (done/total …)`), elapsed/ETA, the objetivo, and
the first pending documents. If it prints `NO_JOB`, no sweep has been recorded — the user can just run
`/agy:notebook <folder> | <objetivo>` (the sweep is incremental, so it resumes automatically).

## Phase 1 — Present

Relay the progress. If documents are **pending**, tell the user to re-run `/agy:notebook <folder> |
<objetivo>` to resume — cached/done docs are skipped, so only the pending ones are processed. If
**failed > 0**, note those are `no_procesado` docs (timeout/rate-limit) that will retry on the next
run. If **COMPLETE**, point them to `/agy:notebook-query` / `/agy:notebook-audit`.

## Notes
- Read-only; it only reads the manifest + summary files and refreshes the job record's counts.
- "Background" here is cooperative: the sweep persists state every wave, so it is always safe to
  interrupt and resume — there is no daemon. ETA is a rough extrapolation from the average per-doc rate.
