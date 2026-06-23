#!/usr/bin/env python3
"""Report the status of the Antigravity agent stack on this machine — what's installed, what's
missing, and how to get each piece. Zero agy calls, stdlib only. Used by `/agy:setup` and the
bootstrap prompt (docs/SETUP_AGENT_STACK.md).

Usage:  python stack_check.py
"""
import os, sys, shutil, importlib.util

HOME = os.path.expanduser("~")


def find_agy():
    agy = os.environ.get("AGY_BIN") or shutil.which("agy") or shutil.which("agy.exe")
    if not agy:
        cand = os.path.join(HOME, "AppData", "Local", "agy", "bin", "agy.exe")
        if os.path.isfile(cand):
            agy = cand
    return agy


def has_module(name):
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def graphify_agy_ready():
    """graphify importable AND aware of the agy-cli backend."""
    if not has_module("graphify"):
        return False
    try:
        import graphify.llm as L  # noqa
        return "agy-cli" in L.BACKENDS
    except Exception:
        return False


def main():
    rows = []
    # component, ok, requirement, purpose, how-to-fix
    agy = find_agy()
    rows.append(("agy CLI", bool(agy), "required",
                 "the Gemini engine behind every /agy:* command",
                 "install https://antigravity.google + run `agy` once to sign in" if not agy else (agy or "")))

    rows.append(("PyMuPDF (fitz)", has_module("fitz"), "required for /agy:notebook PDFs",
                 "read/extract PDF text in the notebook RAG",
                 "pip install pymupdf"))

    rows.append(("sqlite-vec", has_module("sqlite_vec"), "optional",
                 "vector layer for /agy:notebook --semantic (hybrid search)",
                 "pip install sqlite-vec  (also needs a real GEMINI_API_KEY for true embeddings)"))

    ff = shutil.which("ffmpeg")
    rows.append(("ffmpeg", bool(ff), "optional",
                 "split long audio/video for /agy:transcribe",
                 "install ffmpeg (https://ffmpeg.org) and put it on PATH"))

    gready = graphify_agy_ready()
    rows.append(("graphify + agy-cli", gready, "optional (for /agy:graph)",
                 "knowledge graphs built by Gemini via agy (off Claude's tokens)",
                 "run scripts/graphify_agy_install.py (clones graphify + applies the agy-cli backend)"))

    # render
    width = max(len(r[0]) for r in rows)
    print("Antigravity agent stack:")
    n_req_missing = 0
    for name, ok, req, purpose, fix in rows:
        mark = "OK   " if ok else ("MISS " if "required" in req else "skip ")
        if not ok and "required" in req:
            n_req_missing += 1
        print(f"  [{mark}] {name.ljust(width)}  {req}")
        print(f"          {purpose}")
        if not ok:
            print(f"          -> {fix}")
    print()
    capdone = sum(1 for r in rows if r[1])
    print(f"STACK {capdone}/{len(rows)} present" + (f" - {n_req_missing} REQUIRED missing" if n_req_missing else " - all required OK"))
    return 0 if n_req_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
