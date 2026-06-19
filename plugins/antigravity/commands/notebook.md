---
description: Local NotebookLM over a FOLDER of documents using Antigravity (agy). Sweeps each document (PDF with text, scanned PDF, image, docx) into an objective-driven Markdown summary, then builds a relevance INDEX and a cited master summary. Offloads all heavy reading to agy. Saves to docs/agy/notebook/.
argument-hint: "<folder> | <objective>"
context: fork
allowed-tools: Bash, Read, Write, Agent
---

Local replacement for NotebookLM. Given a **folder of documents** and an **objective**,
agy reads every document and produces one objective-driven summary per document, plus a
relevance `INDEX.md` and a cited `RESUMEN_MAESTRO.md`. The point is to **keep Claude's
context cheap**: agy does all the document reading; you only read the two small final files.

Raw user request:
$ARGUMENTS

## Phase 0 — Parse + list + classify (ONE Bash call)

Parse `$ARGUMENTS`: split on the first `|`. Left side = folder, right side = objective.
If there is no `|`, the longest leading token that resolves to an existing directory is the
folder and the rest is the objective. If the folder is missing, ask once: "¿Qué carpeta querés
analizar?" and stop.

Run ONE Bash call (a Python helper) that:
1. Resolves the folder to an absolute path; lists supported files (`.pdf .docx .doc .png .jpg
   .jpeg .webp .gif`) sorted by name.
2. Computes `SLUG` = lowercased folder basename, non-alphanumeric → `-`, collapsed, trimmed to 60.
3. `OUTDIR = docs/agy/notebook/<SLUG>/`; `mkdir -p`. Also `mkdir -p "$OUTDIR/_text"`.
4. **Hybrid classify** each file: for PDFs, extract text with PyMuPDF (`fitz`). If the document
   has a real text layer (≥ ~200 non-space chars per page on average) → mode `text`, and write the
   extracted text to `"$OUTDIR/_text/NN-<slug>.txt"`. Otherwise (scanned / little text) → mode
   `vision`. `.docx/.doc` → `text` if extractable else `vision`. Images → always `vision`.
5. Write a manifest `"$OUTDIR/_manifest.tsv"` with one line per doc:
   `NN<TAB>mode<TAB>source_abspath<TAB>text_path_or_dash<TAB>summary_relpath`
   where `summary_relpath = NN-<slug>.resumen.md`.
6. Print the manifest and the counts (N docs, X text / Y vision).

If the manifest is empty → tell the user there are no supported documents and stop.

```bash
python - "$FOLDER_ABS" "$OUTDIR" <<'PY'
import sys, os, re, glob
import fitz  # PyMuPDF
folder, outdir = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(outdir, "_text"), exist_ok=True)
exts = (".pdf",".docx",".doc",".png",".jpg",".jpeg",".webp",".gif")
files = sorted(f for f in glob.glob(os.path.join(folder,"*")) if f.lower().endswith(exts))
def slug(s):
    s = re.sub(r"[^a-z0-9]+","-", os.path.splitext(os.path.basename(s))[0].lower()).strip("-")
    return s[:60] or "doc"
rows=[]
for i,f in enumerate(files,1):
    nn=f"{i:03d}"; sl=slug(f); mode="vision"; tpath="-"
    if f.lower().endswith(".pdf"):
        try:
            d=fitz.open(f); txt="\n".join(p.get_text() for p in d)
            if d.page_count and len(txt.strip())/d.page_count >= 200:
                mode="text"; tpath=os.path.join(outdir,"_text",f"{nn}-{sl}.txt")
                open(tpath,"w",encoding="utf-8").write(txt)
            d.close()
        except Exception: mode="vision"
    rows.append((nn,mode,os.path.abspath(f),tpath,f"{nn}-{sl}.resumen.md"))
with open(os.path.join(outdir,"_manifest.tsv"),"w",encoding="utf-8") as m:
    for r in rows: m.write("\t".join(r)+"\n")
nt=sum(1 for r in rows if r[1]=="text"); nv=len(rows)-nt
print(f"DOCS={len(rows)} TEXT={nt} VISION={nv} OUTDIR={outdir}")
for r in rows: print("\t".join(r))
PY
```

## Phase 1 — Per-document summaries (fan out agy)

For each manifest row, spawn an `antigravity:agy-rescue` subagent in **MODE: notebook**, in
**batches of 3-4 concurrent** (one message with multiple Agent calls per batch). Pass:

```
MODE: notebook
CWD: <absolute current working dir>
OBJETIVO: <objective>
INPUT_MODE: text|vision
SOURCE_FILE: <source_abspath>          # the original doc (vision reads this)
TEXT_FILE: <text_path or empty>        # extracted text (text mode reads this)
WRITE_FILE: <OUTDIR>/<summary_relpath>
USER_TEXT:
(empty)
```

If a subagent reports failure/timeout for a doc, do NOT abort. Write a stub yourself
(`Write`) to that doc's `WRITE_FILE`:
```
---
doc: <basename>
estado: no_procesado
relevancia: 0
---
No se pudo procesar (timeout o error de agy). Reintentar con /agy:notebook sobre este doc.
```
and continue with the rest.

## Phase 2 — Index + master synthesis (ONE agy subagent)

After all summaries exist, spawn ONE `antigravity:agy-rescue` subagent in **MODE: notebook-index**:

```
MODE: notebook-index
CWD: <absolute current working dir>
OBJETIVO: <objective>
SUMMARIES_DIR: <OUTDIR>               # contains the *.resumen.md files
INDEX_FILE: <OUTDIR>/INDEX.md
MASTER_FILE: <OUTDIR>/RESUMEN_MAESTRO.md
USER_TEXT:
(empty)
```

## Phase 3 — Report

Read ONLY `<OUTDIR>/INDEX.md` and `<OUTDIR>/RESUMEN_MAESTRO.md` (they are small) and present:
1. The objective and the doc counts (total / text / vision / no_procesado).
2. The TOP relevant documents from `INDEX.md`.
3. The master summary's conclusion.
4. The path to `<OUTDIR>` for the full per-document summaries.

Do NOT read the original documents or the per-document summaries yourself — that's the whole
point (agy already did the reading). Only the two final files.

## Notes
- agy `--print` writes nothing to stdout outside a TTY (issue #76) — every agy call writes to a
  file; the subagent verifies the file exists. This command never relies on agy stdout.
- 1 document per agy call (large multimodal batches time out).
- The `_text/` and `_manifest.tsv` are intermediate artifacts; they can be deleted after.
