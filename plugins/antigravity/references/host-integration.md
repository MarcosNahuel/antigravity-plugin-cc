# Antigravity on Codex and Claude Code

The command markdown is the shared workflow specification. Claude keeps its original
slash commands and `agy-rescue` subagent. Codex uses the `agy-*` skills because its
Claude-command importer cannot export commands that require `context: fork`.

## Resolve paths and host tools

Resolve the plugin root from this loaded skill's location: two parents above its
directory. Do not assume the user's workspace contains `plugins/antigravity`, and
do not search the entire disk. Resolve AGY from `AGY_BIN`, PATH, then the documented
OS fallback in `agents/agy-rescue.md`. Use the host's native file and shell tools;
Claude's `Bash`, `Write`, `Read`, `Agent`, and `Workflow` names are not Codex APIs.

Read the referenced command body, replacing `$ARGUMENTS` with the current request.
On Codex, perform its routing in the current session. `context: fork` and “route
to agy-rescue” describe Claude dispatch; do not require that subagent to exist.
Read the needed mode template in `agents/agy-rescue.md` as prompt data, adapting
the invocation to this contract. Do not run legacy shell snippets unchanged.

## Invocation

The optional `scripts/host-runner.mjs` needs Node 18+ and no npm dependencies. It
passes an argv array without a shell, closes stdin, bounds output, enforces a host
timeout, and stops only the process tree it started. It does not pass a permission
bypass flag, change global AGY settings, retry, or resume somebody else's run.

Write a UTF-8 prompt file in the current workspace, then use native argv quoting:

```text
node <plugin-root>/scripts/host-runner.mjs --prompt-file <absolute-prompt-file> --cwd <workspace> --timeout-ms 60000 --output <new-private-result.json>
```

The default is `--mode plan`. Select `--mode accept-edits` only for edits already
authorized in that workspace. The runner returns a private diagnostic envelope;
its `stdout` contains AGY's JSON response. The host reads the actual response and
writes requested deliverables with its own file tools. Do not add a `write_file`
instruction for plan-mode output. For optional scripts that still use the older
scratch helper, its permission bypass is not implied by this adapter: use native
scoped execution or report that the mode cannot run under the current policy.

If Node is unavailable, use native process APIs with argument arrays, closed
stdin, a bounded timeout and JSON output, or report the missing optional helper.
Never build a shell command by interpolating the user's prompt. Python helpers
and report/Workflow tooling remain optional requirements of their specific modes.

`RESPONSE_CAPTURED` means only exit 0 and non-empty output. Check that the JSON
contains an answer and that the requested artifact exists before claiming a task
succeeded. `EMPTY_RESPONSE`, `PROCESS_FAILED`, `SPAWN_FAILED`, `TIMED_OUT`, and
`OUTPUT_LIMIT` are failures, not empty successes. `STOP_UNCONFIRMED` includes the
owned PID: report it and do not retry or claim the process stopped. Auth or tool
permission failures need native login/action; never bypass them or recover a
response by reading the latest unrelated conversation. Keep diagnostics private.

## Deep research without Workflow

Codex executes the same bounded algorithm with its own reasoning and tools:

1. Parse depth L/H, topic and the command's supported options. Reuse already
   authorized scope; `--engines mixed` still is not a second implemented engine.
2. Build the evidence matrix and angles using the command specification.
3. Present the plan when authorization is missing; an already approved plan or
   explicit `--yes` does not need another approval.
4. Run each AGY angle sequentially. Save each response under this run's directory;
   tag failed angles and keep evidence separate from inference and assumptions.
5. Apply coverage/convergence rules from `scripts/deep-research-lib.mjs`. Depth L
   allows at most 2 rounds; H at most 4. Stop when converged or at that limit.
6. Red-team the central/single-source claims, opening primary source pages. Never
   assert a URL resolves or a quote is supported from the duplicate-URL check.
7. Synthesize the command's report with citations, uncertainties and next actions;
   use `scripts/verify_citations.py` when Python is available, stating its limits.
8. Render with the optional renderer only when available and requested. Missing
   Workflow/renderer does not justify claiming an HTML report was produced.

Do not simulate a successful Workflow call. Background work is only possible
when the user asked for it and the host supports a tracked, resumable job.

## Setup

Read-only setup first checks AGY version/help with native tools. Optional Python
`scripts/stack_check.py` inventories extra mode dependencies. A live health prompt
is a separate inference call; perform it only within the user's authorized scope.
Installation/visibility does not establish authentication or model execution.
