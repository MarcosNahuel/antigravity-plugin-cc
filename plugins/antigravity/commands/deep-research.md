---
description: Deep, multi-source, fact-checked web research with agy — reach for it when a decision or design depends on getting it right and a single-shot answer is not enough (architecture / tool / vendor choices, thorough landscape scans, anything you will act on). Builds an evidence matrix + a plan you approve, then agy browses each angle one at a time (sequential — see Notes) while Claude reasons convergence across adaptive rounds (--depth L<=2 / H<=4), runs an agy red-team pass, and returns a cited report with evidence/inference/assumption tags + an applied recommendation. Heavier and slower than /agy:research (single-shot) — use it when depth and correctness matter more than speed.
argument-hint: "[--depth L|H] [--background] [--yes] [--engines agy|mixed] <topic>"
context: fork
allowed-tools: Bash, Write, Read, Workflow
---

Deep research command. Does **not** replace `/agy:research` (that one is a fast single-shot lookup) —
this one drives a multi-round loop through the `deep-research-agy` Workflow: agy browses several
angles **one at a time** per round (never in parallel — see Notes), Claude judges coverage and
convergence between rounds, a red-team pass challenges the central/single-source claims, and only then
does synthesis produce the final report.

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
  capataz/brain, or this repo's own architecture): si el tema pide aplicar los hallazgos a un
  diseño/proyecto local conocido Y tenés herramientas de memoria o búsqueda local disponibles (p.ej.
  engram, grep del repo), usalas para traer contexto y completar `appliedRecommendation.groundedContext`
  — este es el único campo que el workflow deja deliberadamente vacío, ya que no tiene acceso a memoria
  o archivos locales. Si no hay ninguna herramienta de ese tipo disponible, o el tema es investigación
  general sin nada local contra qué anclar, saltá este sub-paso y dejá `groundedContext` tal como lo
  devolvió el workflow (vacío).
- **Render** — do not hand-roll the markdown format. Call `renderReportMarkdown(report, meta)` from
  `deep-research-lib.mjs`, the single source of truth (also what the workflow's own tests check
  against). Write `{ report, meta }` to `<DEEP_DIR>/_render.json`, then run it through the
  `render-report.mjs` CLI in one Bash call:

  ```bash
  node "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/render-report.mjs" "<DEEP_DIR>/_render.json" > "<WRITE_FILE>"
  ```

  where `meta = { title: <topic>, depth: <L|H>, rounds: <result.rounds>, converged: <result.converged>, date: <DATE> }`.
  `render-report.mjs` imports the lib with a relative specifier (`./deep-research-lib.mjs`), which is
  drive-letter-safe on Windows — an absolute `C:\...`/`C:/...` path used directly as an ESM import
  specifier makes Node throw `ERR_UNSUPPORTED_ESM_URL_SCHEME` (it reads the drive letter as a URL
  scheme), so never inline the lib path into a `node -e` one-liner.
- Dump `{ findings: report.findings, coverage: report.coverage, rounds, converged }` to
  `<DEEP_DIR>/ledger.json` for audit/debugging.

## Step 6 — Return

Return the report path (`WRITE_FILE`) plus the first ~30 lines of the rendered file (TL;DR +
Cobertura sections). Present verbatim — do not paraphrase or re-summarize the findings yourself.

## Notes

- `--engines mixed` is a no-op today (agy is the only browsing engine wired in) — don't advertise it
  as multi-engine research until a second engine actually exists.
- Depth `H` is expensive: up to 4 rounds × up to 6 angles, plus a 10-claim red-team pass, each agy call
  taking several minutes — and now run **sequentially**, so `H` wall-clock is roughly the sum of every
  angle/red-team call, not the slowest one. Default to `L` unless the topic genuinely needs multi-round
  convergence.
- This command never talks to `agy` directly — every agy call happens inside the Workflow, one
  `antigravity:agy-rescue` subagent invocation per angle/red-team target, **one at a time, never via
  `parallel()`** (see below). If `agy` breaks mid-run, the affected angle calls come back `failed` and
  the coverage report degrades gracefully (fewer angles completed, noted in
  `coverage.failedAngleLabels`) rather than crashing the whole run.
- **Angles and red-team targets run sequentially, not in parallel, by design.** `agy --print` spins up
  a full local language-server per invocation; two or more running at once starve each other for
  CPU/IO and neither completes (measured 2026-07-05 for batch repo cartography and again 2026-08-15
  for this workflow's own fan-out — a "single-pass" retry still died at 0 bytes after 1h40m while
  another concurrent `agy` call was running). Do not reintroduce `parallel()` around
  `agentType:'antigravity:agy-rescue'` calls without re-verifying agy can actually sustain 2+
  concurrent invocations on the target machine.
- If `agy` is missing/unauthenticated, Step 1's preflight catches it before any Workflow round starts
  — route the user to `/agy:setup` there rather than discovering it mid-loop.
