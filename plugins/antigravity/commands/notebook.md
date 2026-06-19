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

## Phase 1 — Per-document summaries (fan out agy, with rate-limit-aware retry)

Fan out one `antigravity:agy-rescue` subagent in **MODE: notebook** per document. Pass:

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

**Concurrency — up to 10 per wave, with rate-limit backoff.** Each subagent runs its own `agy`
process. agy is rate-limited per minute (RPM) by the Antigravity account tier — roughly ~10 RPM on
the free tier, higher on Pro/Ultra. So fire a wave of **up to 10 Agent calls in one message**, but
treat a wide wave as "best effort": if the account is throttled, some calls come back with **no
output file** (HTTP 429) — that is **rate-limiting, not a per-document failure**. Do NOT stub those
immediately. This mirrors how batch LLM pipelines work (a concurrency cap + retry/backoff, not
blind parallelism). On a Pro/Ultra tier the retries below rarely fire; on free they smooth over the
~10 RPM ceiling.

**Drive it as retry rounds** (don't trust the subagents' self-reports; trust the files on disk):

1. **Round 1** — spawn waves of up to 10 until every manifest doc has been dispatched once.
2. **Check** (ONE Bash call): for every `summary_relpath`, test the file exists AND is non-empty
   (`test -s`). Collect the `missing` list.
3. **Retry rounds (up to 2)** — if `missing` is non-empty, **wait ~60s** (one `sleep 60` — lets the
   per-minute quota reset), then re-dispatch only the `missing` docs in waves of up to 10, and
   re-check. Repeat at most twice.
4. **Stub the rest** — only after the retry rounds, for any doc still missing/empty write a stub
   yourself (`Write`) to its `WRITE_FILE`:
   ```
   ---
   doc: <basename>
   estado: no_procesado
   relevancia: 0
   ---
   No se pudo procesar tras reintentos (timeout o rate-limit de agy). Reintentar con /agy:notebook.
   ```

> The per-minute ceiling is the real limiter, not local CPU — pushing concurrency far past ~10 just
> produces more 429s, not more throughput. 10-per-wave + the 60s backoff between retry rounds is the
> sweet spot on the free tier. (A paid Antigravity tier with higher RPM could raise the wave size.)

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
- 1 document per agy call (large multimodal batches time out), up to 10 calls per wave (see Phase 1).
- **Speed tip — pick a low-effort model.** These per-document summaries don't need deep reasoning,
  so a faster model makes the whole sweep cheaper and quicker. agy uses whatever model is selected
  in its TUI (run `agy`, "Switch Model"), which persists in `~/.gemini/antigravity-cli/settings.json`
  (`"model": "..."`) and is honored by `--print`. **`Gemini 3.5 Flash (Low)`** is a good default for
  the sweep; bump to a Pro/High model only if a corpus needs deeper synthesis. No per-call `--model`
  flag is needed — the persisted selection applies automatically.
- The `_text/` and `_manifest.tsv` are intermediate artifacts; they can be deleted after.
