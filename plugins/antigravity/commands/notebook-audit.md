---
description: Adversarial consistency audit over the notebook knowledge base — finds contradictions in a document corpus: the same category with conflicting amounts, the same person under two names, the same reference with different values, coverage gaps (unprocessed docs), unparseable amounts. Pure SQL, read-only. Writes CONTRADICCIONES.md.
argument-hint: "<folder>"
context: fork
allowed-tools: Bash, Read
---

Run a deterministic, read-only **consistency audit** over the `notebook.db` that `/agy:notebook`
built. It surfaces the conflicts you must resolve before trusting a total or building a liquidation —
each one cited to its source document. No agy, no model — just SQL over the structured facts.

Raw user request:
$ARGUMENTS

## Phase 0 — Resolve + run (ONE Bash call)

Resolve `OUTDIR = docs/agy/notebook/<slug>` from the folder argument (same `slug()` the notebook
uses). If `notebook.db` is missing, tell the user to run `/agy:notebook <folder> | <objetivo>` first
and stop. Otherwise run the audit:

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/notebook_audit.py" "$OUTDIR"
```

It prints `AUDIT findings=N report=…/CONTRADICCIONES.md` and writes the report. Checks:
- **A** same concepto with conflicting `monto_cents` across documents,
- **B** same person id under two or more different names,
- **C** same reference under two or more different values,
- **D** documents that failed processing (`estado='no_procesado'`) — coverage gaps,
- **E** amounts that couldn't be parsed to cents (OCR review),
- **F** same organization under two or more different names.

## Phase 1 — Present

Read `<OUTDIR>/CONTRADICCIONES.md` and present it. Lead with the count and the highest-stakes
findings (A and B — money and identity conflicts). For each, name the documents involved and advise
verifying against the original before acting. If `findings=0`, say the corpus is internally
consistent on these checks (note it does not prove correctness, only the absence of these conflicts).

## Notes
- Read-only; never writes to the DB. Re-run after a fresh `/agy:notebook` to re-audit.
- This is a *consistency* check (contradictions within the corpus), not a *grounding* check — pair it
  with `/agy:notebook-query` to verify a specific figure against its source.
