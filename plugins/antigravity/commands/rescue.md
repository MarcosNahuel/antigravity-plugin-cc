---
description: Delegate a coding, debugging or implementation task to the Antigravity CLI (agy) subagent
argument-hint: "[--resume|--fresh] [--model flash|pro|flash-lite] <what agy should do>"
context: fork
allowed-tools: Bash, Write
---

Route this request to the `antigravity:agy-rescue` subagent in MODE: rescue.

Raw user request:
$ARGUMENTS

Routing rules:

- If the request includes `--resume`, set `RESUME: true` in the header you pass to the subagent.
- If the request includes `--fresh`, set `RESUME: false`.
- If neither flag is present and the user phrasing sounds like a follow-up ("continue", "keep going", "resume", "apply the first fix"), set `RESUME: true`. Otherwise `RESUME: false`.
- `--model flash` → `MODEL: gemini-3.5-flash`
- `--model pro` → `MODEL: gemini-3.5-pro`
- `--model flash-lite` → `MODEL: gemini-3.5-flash-lite`
- Otherwise `MODEL:` (empty — let agy choose).
- Strip the routing flags (`--resume`, `--fresh`, `--model X`) from the user text before forwarding.

Pass this header block to the subagent followed by the cleaned user text:

```
MODE: rescue
INTENSITY:
MODEL: <model or empty>
RESUME: <true|false>
WRITE_FILE:
USER_TEXT:
<cleaned user request>
```

Operating rules:

- The subagent is a thin forwarder. It returns agy's stdout verbatim.
- Return that stdout to the user as-is. Do not add commentary before or after.
- If agy reports it is missing or unauthenticated, tell the user to run `/agy:setup`.
