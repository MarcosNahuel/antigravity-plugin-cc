---
description: Deep research multi-agent research with agy (agy browses in parallel per angle, Claude reasons the evidence matrix and convergence) — adaptive rounds (L<=2 / H<=4), plan gate, red-team pass, and a grounded applied recommendation. Complements /agy:research (fast single-shot).
argument-hint: "[--depth L|H] [--background] [--yes] [--engines agy|mixed] <topic>"
context: fork
allowed-tools: Bash, Write, Read, Workflow, mcp__plugin_engram_engram__mem_search
---

Deep research command. Does **not** replace `/agy:research` (that one is a fast single-shot lookup) —
this one drives a multi-round loop through the `deep-research-agy` Workflow: agy browses several
angles in parallel per round, Claude judges coverage and convergence between rounds, a red-team pass
challenges the central/single-source claims, and only then does synthesis produce the final report.

Raw user request:
$ARGUMENTS

## Step 1 — Parse + preflight (ONE Bash call)

- `--depth L|H` (default `L`). `H` runs up to 4 rounds instead of 2, red-teams up to 10 claims instead
  of 5, and allows longer per-angle timeouts (4m vs 3m) — reserve it for topics that need real
  convergence (contradictory sources, a recommendation that must survive red-teaming), not quick
  lookups.
- `--background` runs the Workflow with `run_in_background: true` and **implies `--yes`** (you can't
  approve a plan you won't be watching).
- `--yes` skips the plan gate (Step 3) and goes straight to Step 4.
- `--engines agy|mixed` (default `agy`). **`mixed` is currently accepted but behaves identically to
  `agy`** — there is no second browsing engine wired in yet. If the user asks what `mixed` does, say
  this plainly; don't imply real engine diversity that doesn't exist.
- Strip all flags above from `$ARGUMENTS`; what remains, trimmed, is `<topic>`. If empty, ask once:
  "What should I deep-research?" and stop.
- Build `SLUG` from `<topic>` (lowercase, non-alphanumeric → `-`, collapse repeats, trim to 60 chars)
  and `DATE` = today, ISO `YYYY-MM-DD`.
- `WRITE_FILE` = absolute path to `docs/agy/research/<DATE>-<SLUG>.md`.
  `DEEP_DIR` = absolute path to `docs/agy/research/.deep/<DATE>-<SLUG>`.
- One Bash call does the preflight + scaffolding together — agy presence check, then both `mkdir -p`:

  ```bash
  mkdir -p "docs/agy/research/.deep/<DATE>-<SLUG>"
  command -v agy >/dev/null 2>&1 && agy --version || echo "AGY_MISSING"
  ```

  If the output is `AGY_MISSING`, tell the user to run `/agy:setup` first and **stop** — don't launch
  a multi-round Workflow (several minutes, several agy calls) against a broken/missing `agy`.

## Step 2 — Evidence matrix + angles (Claude reasons, no tool calls)

Decompose `<topic>` yourself into:

1. **Evidence matrix** — rows of
   `{ id, question, evidenceType, sourceQualityBar, recencyRequirement, contradictionCheck, recommendationChanging }`.
   `recommendationChanging: true` marks rows whose answer could flip the conclusion — those are the
   ones convergence and the red-team pass weigh most heavily.
2. **Angles** — `{ label, query, rationale, targetsMatrixIds }`. 3-4 angles at depth `L`, 5-6 at depth
   `H`. Every angle must target at least one matrix row; every `recommendationChanging` row should be
   targeted by at least one angle.

## Step 3 — Plan gate (skip on `--yes` / `--background`)

Show the user the matrix + angles (a compact table is fine) and wait for an explicit go-ahead or
edits. Apply any requested edits and re-show if they were non-trivial. Only proceed to Step 4 once the
user is on board. With `--yes` or `--background`, skip this step entirely.

## Step 4 — Launch the Workflow

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/deep-research-agy.js",
  args: {
    question: <topic>,
    matrix: <matrix from Step 2>,
    angles: <angles from Step 2>,
    depth: "L" | "H",
    engines: "agy" | "mixed",
    deepDir: <DEEP_DIR, absolute>,
    date: <DATE>,
    title: <topic>
  },
  run_in_background: <true if --background, else false>
})
```

`args` is passed as a JSON **object** (the workflow parses it defensively either way, but always pass
an object here). `deepDir` and `title` must be final, absolute/resolved values — never placeholders.

- **If `--background`**: tell the user it's running and mention `DEEP_DIR` (partial per-angle
  transcripts land there as the rounds progress), then stop — do not block waiting for it. Steps 5-6
  only run once you have the Workflow's result in hand (a follow-up turn, or the user checking back).
- **If not background**: await the result — `{ report, coverage, rounds, converged }`. `report`
  already conforms to the report schema and `report.coverage` is pre-populated (deterministic,
  code-computed inside the workflow) — do not recompute or second-guess it.

## Step 5 — Grounding + render (Claude, after the Workflow returns)

- **Grounding** (only when the topic asks to apply the findings to a known local design — e.g.
  capataz/brain, or this repo's own architecture): `mem_search` for relevant prior decisions, then
  `Read` the relevant spec/repo files. Fill `report.appliedRecommendation.groundedContext` with what
  you find — this is the one field the workflow deliberately leaves empty, since it has no access to
  local memory or files. If the topic is general research with nothing local to ground against, skip
  this substep and leave `groundedContext` exactly as the workflow returned it.
- **Render** — do not hand-roll the markdown format. Call `renderReportMarkdown(report, meta)` from
  `deep-research-lib.mjs`, the single source of truth (also what the workflow's own tests check
  against). Write `{ report, meta }` to a temp JSON file, then run it through Node in one Bash call:

  ```bash
  LIB_PATH="${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/deep-research-lib.mjs"
  node --input-type=module -e "
    import { renderReportMarkdown } from '$LIB_PATH';
    import { readFileSync } from 'node:fs';
    const j = JSON.parse(readFileSync(process.argv[1], 'utf8'));
    process.stdout.write(renderReportMarkdown(j.report, j.meta));
  " "<TEMP_JSON>" > "<WRITE_FILE>"
  ```

  where `meta = { title: <topic>, depth: <L|H>, rounds: <result.rounds>, converged: <result.converged>, date: <DATE> }`.
  (If `LIB_PATH` ever fails to resolve as an ESM import specifier — e.g. a backslash-heavy Windows
  path — fall back to a `file://` URL built from the same absolute path.)
- Dump `{ findings: report.findings, coverage: report.coverage, rounds, converged }` to
  `<DEEP_DIR>/ledger.json` for audit/debugging.

## Step 6 — Return

Return the report path (`WRITE_FILE`) plus the first ~30 lines of the rendered file (TL;DR +
Cobertura sections). Present verbatim — do not paraphrase or re-summarize the findings yourself.

## Notes

- `--engines mixed` is a no-op today (agy is the only browsing engine wired in) — don't advertise it
  as multi-engine research until a second engine actually exists.
- Depth `H` is expensive: up to 4 rounds × up to 6 angles, plus a 10-claim red-team pass, each agy call
  taking several minutes. Default to `L` unless the topic genuinely needs multi-round convergence.
- This command never talks to `agy` directly — every agy call happens inside the Workflow, one
  `antigravity:agy-rescue` subagent invocation per angle/red-team target. If `agy` breaks mid-run, the
  affected angle calls come back `failed` and the coverage report degrades gracefully (fewer angles
  completed, noted in `coverage.failedAngleLabels`) rather than crashing the whole run.
- If `agy` is missing/unauthenticated, Step 1's preflight catches it before any Workflow round starts
  — route the user to `/agy:setup` there rather than discovering it mid-loop.
