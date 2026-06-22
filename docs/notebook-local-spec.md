# Spec — `/agy:notebook`: local NotebookLM over a folder of documents

**Fecha:** 2026-06-19 · **Autor:** Marcos Nahuel Albornoz

## Objetivo

Replace NotebookLM with a **local** flow inside Claude Code, powered by agy (Gemini
multimodal). The **Antigravity Plugin** offloads the heavy work Claude Code shouldn't
burn its context on. Given a **folder of documents** and an **objective** in natural
language, agy sweeps each document (text PDF, scanned PDF, image, docx), produces a
**per-document `.md` summary** oriented to the objective, and then an **`INDEX.md`**
(relevance) and a **`RESUMEN_MAESTRO.md`** (synthesis with citations).

Design goal: **minimize Claude Code tokens** — agy does all the heavy reading; Claude
orchestrates and only reads the two small final files. Claude Code stays lean and you
save tokens.

## No-objetivos (YAGNI)

- No interactive chat/Q&A mode (one-shot).
- No audio overview, no mind map, no embeddings/vector store.
- No reuse of prior `doc-to-md` conversions (the summary is oriented to the
  objective, not a faithful conversion).

## Uso

```
/agy:notebook <carpeta> | <objetivo>
```
- Separator `|` between folder and objective. If there is no `|`, anything that does
  not resolve to an existing folder is the objective.
- Ej: `/agy:notebook ".../research-papers-rag" | summarize each paper's method and open questions`

## Arquitectura

Command `commands/notebook.md` (context: principal — orchestrates) + new **MODE: notebook**
in `agents/agy-rescue.md` (one fork per document, like `doc-to-md`).

### Fase 0 — listado (comando, 1 Bash)
- Resolve folder to an absolute path. List supported files: `.pdf .docx .doc
  .png .jpg .jpeg .webp .gif`. Sort by name.
- `OUTDIR = docs/agy/notebook/<slug-carpeta>/`. `mkdir -p`.
- If there are no supported files → warn and stop.

### Fase 1 — barrido por documento (1 fork agy por doc)
For each document, detect text vs scanned (**hybrid**):
- Extract text with a fast helper (pdftotext/pymupdf). If the useful text exceeds a
  threshold (e.g. ≥200 chars/page average) → **text mode**: pass the text to agy.
- Otherwise (scanned / little text) → **vision mode**: agy reads the file with vision/OCR.

agy writes (with `write_file`, per issue #76) `OUTDIR/<NN>-<slug>.resumen.md`:
```
---
doc: <file name>
tipo: <paper|contract|meeting-notes|memo|report|...>
referencia: <doc id / citation, if any>
fecha: <YYYY-MM-DD or "ilegible">
emisor: <author / organization>
relevancia: <0-100>
---
## Síntesis (orientada al objetivo)
<2-6 sentences focused on the objective>
## Datos clave
- <fechas, montos, organizaciones, personas, referencias — citable>
## Por qué es (ir)relevante para el objetivo
<1-2 sentences>
```
- **Robustez**: if a doc fails or times out, write a stub with `relevancia: 0` and
  `estado: no_procesado` and continue. Never abort the whole sweep.
- **Concurrencia**: small batches (e.g. 3-4 forks at a time) so agy is not saturated.

### Fase 2 — índice + síntesis (1 fork agy sobre los resúmenes)
Input: all the `*.resumen.md` (small). agy writes:
- `OUTDIR/INDEX.md`: table of all docs sorted by `relevancia` desc
  (doc · tipo · fecha · relevancia · 1 line), with a **TOP** section (the most
  relevant to the objective) highlighted at the top.
- `OUTDIR/RESUMEN_MAESTRO.md`: synthesis of the corpus oriented to the objective, **with citations**
  to each doc's `referencia`/name (e.g. "according to the Acme Corp MSA…"), a **timeline**
  of milestones, and a **conclusion** that directly answers the objective.

### Fase 3 — reporte (comando)
Claude reads ONLY `INDEX.md` + `RESUMEN_MAESTRO.md` and presents them. It does not read the
original docs or the per-doc summaries.

## Salida
```
docs/agy/notebook/<slug-carpeta>/
├── INDEX.md
├── RESUMEN_MAESTRO.md
└── NN-<slug>.resumen.md   (one per document)
```

## Cambios al plugin
1. `commands/notebook.md` — new command (parse folder|objective, list, dispatch).
2. `agents/agy-rescue.md` — new `MODE: notebook` (per-doc) and `MODE: notebook-index`
   (synthesis). Reuses the agy invocation rules (skip-permissions, write_file,
   print-timeout, add-dir).
3. `agents/agy-rescue.md` — **port the `MODE: setup` fix** (the "not logged into
   Antigravity" message is a NON-fatal warning; the real test = `write_file`). Already fixed in cache.
4. Register the command in `plugin.json`/marketplace if applicable; version bump + CHANGELOG.

## Riesgos / decisiones
- agy `--print` does not flush stdout (issue #76) → **always** `write_file` + read the file.
- Large batches time out → **1 document per call** to agy.
- Secondary auth warnings are noise → do not treat them as a failure.
