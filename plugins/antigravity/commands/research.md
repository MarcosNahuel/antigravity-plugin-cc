---
description: Run deep web research with Antigravity (agy) at chosen intensity. Saves output to docs/agy/research/ automatically.
argument-hint: "[--background] [--intensity low|medium|high] <topic>"
context: fork
allowed-tools: Bash, Write
---

Route this to the `antigravity:agy-rescue` subagent in MODE: research.

Raw user request:
$ARGUMENTS

Routing rules:

- If the request contains `--background`, invoke the subagent with `run_in_background: true`. Research at `high` intensity can take 15–20min — background is the sensible default for that case but only when the user explicitly opted in. Strip the flag from the topic.
- Parse `--intensity <low|medium|high>` from the user text. Default to `medium` if missing or invalid.
- Strip the routing flags (`--background`, `--intensity`) from the user text. What remains IS the topic. Trim whitespace.
- Build a slug from the topic: lowercase, replace non-alphanumeric with `-`, collapse repeated `-`, trim to 60 chars.
- Compute today's date in `YYYY-MM-DD` (ISO, local time).
- Compute `WRITE_FILE` = `docs/agy/research/<YYYY-MM-DD>-<slug>.md` (relative to the current working directory).
- Before invoking the subagent, ensure the directory exists with one `Bash` call:

```bash
mkdir -p docs/agy/research
```

Pass this header block to the subagent followed by the topic:

```
MODE: research
INTENSITY: <low|medium|high>
MODEL:
RESUME: false
WRITE_FILE: docs/agy/research/<date>-<slug>.md
USER_TEXT:
<topic>
```

> **Note**: `agy` CLI 1.0.x does not accept a `--model` flag. Model selection is internal to the CLI. Intensity now controls the timeout and the prompt template only.

Operating rules:

- The subagent wraps the topic in the intensity template, invokes agy with the right timeout (`low=3m`, `medium=8m`, `high=20m`), writes the result to `WRITE_FILE`, and returns:
  1. The saved file path.
  2. The first ~30 lines of agy's output (TL;DR / Executive summary).
- Present that to the user as-is. Do not paraphrase.
- If the user did not provide a topic, ask once: "What topic would you like to research?"
- If agy reports it is missing or unauthenticated, tell the user to run `/agy:setup`.
