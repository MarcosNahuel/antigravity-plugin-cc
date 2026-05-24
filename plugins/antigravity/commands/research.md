---
description: Run deep web research with Antigravity (agy) at chosen intensity. Saves output to docs/agy/research/ automatically.
argument-hint: "[--intensity low|medium|high] [--model flash|pro|flash-lite] <topic>"
context: fork
allowed-tools: Bash, Write
---

Route this to the `antigravity:agy-rescue` subagent in MODE: research.

Raw user request:
$ARGUMENTS

Routing rules:

- Parse `--intensity <low|medium|high>` from the user text. Default to `medium` if missing or invalid.
- Parse `--model <flash|pro|flash-lite>` from the user text if present (overrides the intensity default).
- Default model per intensity (if `--model` not given):
  - `low` → `gemini-3.5-flash`
  - `medium` → `gemini-3.5-flash`
  - `high` → `gemini-3.5-pro`
- Strip the routing flags from the user text. What remains IS the topic. Trim whitespace.
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
MODEL: <resolved model>
RESUME: false
WRITE_FILE: docs/agy/research/<date>-<slug>.md
USER_TEXT:
<topic>
```

Operating rules:

- The subagent wraps the topic in the intensity template, invokes agy with the right timeout (`low=3m`, `medium=8m`, `high=20m`), writes the result to `WRITE_FILE`, and returns:
  1. The saved file path.
  2. The first ~30 lines of agy's output (TL;DR / Executive summary).
- Present that to the user as-is. Do not paraphrase.
- If the user did not provide a topic, ask once: "What topic would you like to research?"
- If agy reports it is missing or unauthenticated, tell the user to run `/agy:setup`.
