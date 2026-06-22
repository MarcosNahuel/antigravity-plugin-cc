---
description: WATCH a video and return a structured VISUAL breakdown (not just a transcript) with Antigravity (agy / Gemini 3.x, natively multimodal in video). Scene-by-scene segments with timestamps, on-screen text/OCR (slides, charts, UI, captions), key visual events, and a summary. For screencasts, tutorials, presentations, demos, ads, inspections, security footage — things Claude Code can't see. Saves to docs/agy/video/.
argument-hint: "<video file | YouTube/URL> [focus]"
context: fork
allowed-tools: Bash, Read, Agent
---

Give Claude eyes on a video. `agy` (Gemini is natively multimodal in video) WATCHES the footage and
returns a structured, timestamped **visual** breakdown — what is shown, not just what is said. Use
this when the *picture* matters: screencasts, tutorials, slide decks, product demos, UI walkthroughs,
ads, site inspections. For a pure transcript use `/agy:transcribe`; for one targeted question use
`/agy:media`.

Raw user request:
$ARGUMENTS

## Phase 0 — Resolve source + kind (ONE Bash call)

Parse `$ARGUMENTS`: the first token that is a URL (`http(s)://`) OR an existing file (`test -f`) is the
**source**; the rest is an optional **focus**. If nothing resolves, ask once "¿Qué video analizo
(archivo o URL)?" and stop.

```bash
python - "$SOURCE" <<'PYEOF'
import sys, os, re
src = sys.argv[1].strip().strip('"')
low = src.lower()
if low.startswith("http"):
    kind = "url"; addir = ""
    base = re.sub(r"[^a-z0-9]+","-", re.sub(r"^https?://(www\.)?","",low)).strip("-")[:50] or "url"
else:
    kind = "file"; addir = os.path.dirname(os.path.abspath(src))
    base = re.sub(r"[^a-z0-9]+","-", os.path.splitext(os.path.basename(src))[0].lower()).strip("-")[:50] or "video"
out = os.path.join("docs","agy","video", f"{base}.md")
os.makedirs(os.path.dirname(out), exist_ok=True)
print(f"KIND={kind}\nADD_DIR={addir}\nWRITE_FILE={os.path.abspath(out)}\nSOURCE={src}")
PYEOF
```

## Phase 1 — Watch (ONE agy subagent)

Spawn ONE `antigravity:agy-rescue` subagent in **MODE: video**:

```
MODE: video
CWD: <absolute current working dir>
KIND: url|file
SOURCE: <file path or URL>
ADD_DIR: <dir of the source file, or empty for a URL>
FOCUS: <focus text or empty>
WRITE_FILE: <WRITE_FILE>
USER_TEXT:
(empty)
```

## Phase 2 — Present

Read ONLY `<WRITE_FILE>` and present: the summary first, then the scene table, then the saved path.
Don't re-process the video yourself.

## Notes
- Output is a **visual** breakdown: `## Resumen`, a `## Escenas` table (`| Tramo (mm:ss–mm:ss) | Qué se ve | Texto en pantalla / OCR | Audio (resumen) |`), `## Texto en pantalla` (all OCR'd slides/captions/UI), and `## Momentos clave`.
- Long videos (>~15 min) can hit the timeout — the subagent raises it for video; split with `ffmpeg` first if needed.
- agy `--print` writes nothing to stdout outside a TTY (issue #76); the breakdown is read from the file.
