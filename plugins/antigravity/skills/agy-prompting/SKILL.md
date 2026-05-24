---
name: agy-prompting
description: Internal helper — how to tighten a user request into a sharp prompt for the Antigravity CLI (agy / Gemini 3.x with native web search and agentic tools)
user-invocable: false
---

# Prompting agy (Gemini 3.x via Antigravity CLI)

Use this skill ONLY inside the `antigravity:agy-rescue` subagent when shaping the text you pass to `agy --print`. Do not use it to do independent reasoning, file inspection, or research yourself.

## What agy is good at

- Native web search with citation grounding (real URLs, not hallucinated).
- Long-context reasoning over multiple sources.
- Following structured-output instructions (markdown tables, JSON, frontmatter).
- Tool calling for code generation and file edits when run with `--dangerously-skip-permissions`.

## What agy is worse at than Claude

- Following complex multi-turn workflow rules. Keep the prompt single-shot and self-contained.
- Inferring implicit context — if a constraint matters, write it down.
- Localized linguistic nuance — explicitly ask for the target dialect ("Spanish (Argentina)", "Brazilian Portuguese", etc.) when the output language matters.

## Prompt shape that works

```
<TASK in one sentence>.

Rules:
- <constraint 1>
- <constraint 2>
- ...

Output format:
<exact markdown / json schema you want>

<DATA / TOPIC>:
<the actual content>
```

Keep the rules to <= 8 bullets. More than that and Gemini starts dropping the tail.

## Things to ALWAYS include

- Output language when relevant.
- Whether citations are required and the citation format ([N] style works best).
- The exact output structure with markdown headers.
- An anti-hallucination clause ("if you could not find a solid source, say so explicitly" / "mark weak claims as [WEAK EVIDENCE]").

## Things to AVOID

- Multi-step "first do X, then do Y, then call me back" instructions. agy in `--print` mode is single-shot; chain steps from the caller side instead.
- Demanding more than ~20 sources unless the user asked for it — quality drops fast past that.
- Free-form "be creative" — for research, structure is what makes the output usable.
- Mixing rescue work (code edits) and research (web search) in the same call. Pick one.

## Routing flags reminder

These are CALLER-SIDE controls, never include them in the agy prompt text:

- `--print` — non-interactive
- `--dangerously-skip-permissions` — auto-approve tool use
- `--print-timeout 20m0s` — high-intensity research needs long timeouts
- `--model gemini-3.5-pro` / `gemini-3.5-flash` / `gemini-3.5-flash-lite`
- `--continue` — resume the most recent agy conversation
- `--conversation <id>` — resume a specific past conversation

## When in doubt

Default to the templates baked into `agy-rescue.md` for research mode. Only deviate when the user explicitly asks for a different shape.
