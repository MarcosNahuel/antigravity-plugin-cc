#!/usr/bin/env python3
"""Decide where Graphify should write `graphify-out/` for a given folder — Windows MAX_PATH guard.

Graphify caches every AST extraction at

    <out>/graphify-out/cache/ast/v<version>/<64-char-sha256>.<8-char-suffix>.tmp

which adds ~110 characters on top of the project path. Windows' legacy MAX_PATH is 260, and when the
total crosses it the write fails with ENOENT, Graphify prints "AST extraction failed" and then
"graph is empty", and **exits 0** — a silent empty graph rather than an error.

Measured on Windows 11 + Python 3.13 + graphify 0.9.31 (2026-07-31):
    project path 259 chars -> 57 nodes, 81 edges   (OK)
    project path 260 chars ->  0 nodes             (silent failure)

Upstream honours an absolute `GRAPHIFY_OUT`, so the fix is to relocate the output for deep projects.
The location is derived from the project path, so the incremental cache still hits across runs.

Output is meant to be `eval`'d by the caller, and is EMPTY when no redirect is needed — deliberately,
because upstream reads `os.environ.get("GRAPHIFY_OUT", "graphify-out")`: exporting an empty string
would not fall back to the default, it would point the output at the project root.

Usage:
  eval "$(python graphify_outdir.py <folder>)"     # sets + exports GRAPHIFY_OUT only if required
"""
import hashlib
import os
import re
import sys

# Longest project path that still leaves room for the cache suffix, with margin.
MAX_PROJECT_PATH = 140


def short_out_dir(folder):
    """Stable per-project location outside the deep tree."""
    digest = hashlib.sha1(folder.encode("utf-8", "ignore")).hexdigest()[:8]
    slug = re.sub(r"[^A-Za-z0-9_-]+", "-", os.path.basename(folder.rstrip("\\/")))[:24] or "graph"
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return os.path.join(base, "graphify-out", f"{slug}-{digest}")
    return os.path.join(os.path.expanduser("~"), ".graphify", "out", f"{slug}-{digest}")


def main():
    if len(sys.argv) < 2:
        print("usage: graphify_outdir.py <folder>", file=sys.stderr)
        return 2
    folder = os.path.abspath(sys.argv[1])

    # Only Windows has the 260-char ceiling; POSIX limits are per-component and far higher.
    if os.name != "nt" or len(folder) <= MAX_PROJECT_PATH:
        return 0                      # print nothing: keep graphify's own default

    out = short_out_dir(folder)
    os.makedirs(out, exist_ok=True)
    print(f"[outdir] project path is {len(folder)} chars - redirecting output to dodge MAX_PATH",
          file=sys.stderr)
    print(f"[outdir] graph outputs -> {out}", file=sys.stderr)
    print(f'export GRAPHIFY_OUT="{out}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
