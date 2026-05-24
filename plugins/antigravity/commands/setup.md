---
description: Check whether the Antigravity CLI (agy) is installed, on PATH, and responding to a ping
argument-hint: ""
allowed-tools: Bash
---

Route this to the `antigravity:agy-rescue` subagent in MODE: setup.

Pass this header block to the subagent:

```
MODE: setup
INTENSITY:
MODEL:
RESUME: false
WRITE_FILE:
USER_TEXT:
```

The subagent will:

1. Resolve the `agy` binary (PATH, then `AGY_BIN`, then per-OS fallback paths).
2. Try `agy changelog` to read the current version.
3. Run a 30s ping: a minimal `--print` call expecting "pong" back.
4. Report binary path, version, and ping status.

Output rules:

- Present the final setup output to the user as-is.
- If the binary is missing, tell the user to install Antigravity:

  - **Windows (PowerShell):** `irm https://antigravity.google/cli/install.ps1 | iex`
  - **macOS / Linux (bash):** `curl -fsSL https://antigravity.google/cli/install.sh | bash`

  After install, restart the shell so the binary lands on PATH.

- If the binary exists but ping times out, suggest the user run `agy` once interactively to complete Google OAuth login.
