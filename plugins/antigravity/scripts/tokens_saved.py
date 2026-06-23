#!/usr/bin/env python3
"""Estimate how many of Claude's tokens a /agy:notebook sweep SAVED — the plugin's core value:
agy/Gemini read the whole corpus, but Claude only ever reads the small synthesis.

corpus      = tokens agy read so Claude didn't have to (extracted text of the text docs).
claude_reads = tokens Claude actually consumes (RESUMEN_MAESTRO.md + INDEX.md, else the per-doc summaries).
saved        = corpus − claude_reads ;  ratio = corpus / claude_reads.

Honest about scope: scanned/vision docs have no extracted text on disk, so their OCR'd content (which
agy ALSO read) is not counted here — the real saving is therefore HIGHER than reported. Uses tiktoken
if available, else ~chars/4. Pure stdlib otherwise.

Usage:  python tokens_saved.py <OUTDIR>
"""
import os, sys, glob


def toks(s: str) -> int:
    try:
        import tiktoken
        return len(tiktoken.get_encoding("cl100k_base").encode(s))
    except Exception:
        return max(1, len(s) // 4)


def _read(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""


def main():
    outdir = sys.argv[1]
    if not os.path.isdir(outdir):
        print("NO_OUTDIR"); return 1

    corpus = 0
    n_text = 0
    for f in glob.glob(os.path.join(outdir, "_text", "*.txt")):
        corpus += toks(_read(f)); n_text += 1

    summaries = [f for f in glob.glob(os.path.join(outdir, "*.resumen.md"))
                 if not os.path.basename(f).startswith("_grupo")]
    n_docs = len(summaries)
    n_vision = max(0, n_docs - n_text)

    claude = 0
    reads = []
    for name in ("RESUMEN_MAESTRO.md", "INDEX.md", "MASTER.md", "TIMELINE.md", "ENTIDADES.md"):
        p = os.path.join(outdir, name)
        if os.path.isfile(p):
            claude += toks(_read(p)); reads.append(name)
    if claude == 0:                      # no synthesis yet -> Claude would read the per-doc summaries
        for f in summaries:
            claude += toks(_read(f))
        reads = ["per-doc summaries"]

    saved = max(0, corpus - claude)
    ratio = (corpus / claude) if claude else 0.0
    note = (f"  (+{n_vision} scanned doc(s): agy also read their OCR'd text — not counted, so the real "
            "saving is higher)") if n_vision else ""
    print(f"TOKENS_SAVED corpus~{corpus} claude_reads~{claude} saved~{saved} ratio~{ratio:.1f}x "
          f"reads={reads}{note}")
    if ratio:
        print(f"  -> Reading this corpus directly would cost Claude ~{corpus:,} tokens; the synthesis "
              f"Claude reads is ~{claude:,} -> you saved ~{saved:,} tokens (~{ratio:.1f}x less).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
