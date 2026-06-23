---
description: Check whether the Antigravity CLI (agy) is installed, on PATH, and responding to a ping
argument-hint: ""
allowed-tools: Bash
---

## Phase 0 — Stack check (ONE Bash call, no agy)

First report the whole agent stack — what's installed, what's missing, how to fix each — so the user
knows which `/agy:*` capabilities are ready:

```bash
python "${CLAUDE_PLUGIN_ROOT:-$PWD}/plugins/antigravity/scripts/stack_check.py"
```

It checks: **agy CLI** (required), **PyMuPDF/fitz** (required for `/agy:notebook` PDFs), **sqlite-vec**
(optional — `/agy:notebook --semantic`), **ffmpeg** (optional — long media for `/agy:transcribe`), and
**graphify + agy-cli backend** (optional — `/agy:graph`). Present the table and the fix line for
anything missing. Prints `STACK n/5 present`.

## Phase 1 — agy health ping

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

- If the binary exists but ping times out (empty stdout + exit 0), the symptom is ambiguous in agy 1.0.x:
  1. **Tool-call loop** (most common in v0.1.1+): the model entered an agentic loop and consumed the timeout before flushing. Re-run with a higher `--print-timeout` or a stricter "do not use tools" prompt.
  2. **OAuth missing**: verify with `ls ~/.gemini/antigravity-cli/installation_id`. If absent or empty, run `agy` once interactively in a regular terminal to complete the Google OAuth login.
