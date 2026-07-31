#!/usr/bin/env python3
"""Install (or just check) Graphify — the upstream PyPI package `graphifyy` — so `/agy:graph` works.

Since Graphify 0.9 (the upstream "v8" rewrite) **code is extracted structurally with tree-sitter
ASTs — no LLM, no API key**. Building the knowledge graph of a repo therefore costs zero tokens on
any assistant, and this installer only has to track the official package: no clone of upstream, no
source patch, nothing that can drift.

History (why this file changed shape in v1.6.0): plugin <= v1.5.1 cloned upstream HEAD into
`~/.antigravity-graphify/graphify` and applied a bundled `agy-cli-backend.patch` that taught Graphify
an `agy-cli` LLM backend. Upstream then shipped the v8 rewrite (default branch `main` -> `v8`, files
moved, LLM made optional for code), so on any *fresh* machine the clone pulled v8, the patch no
longer applied, and `/agy:graph` was dead on arrival. That patch is gone. This script also MIGRATES a
machine still carrying the old patched editable install.

Usage:
  python graphify_install.py            # install/upgrade if needed, else verify
  python graphify_install.py --check    # report status only, never install

Machine-readable last lines:
  GRAPHIFY_CMD=<how to invoke the CLI>   (only when ready)
  READY | READY_NO_AGY | MISSING
"""
import os
import re
import shutil
import subprocess
import sys

# Floor = the version this plugin was verified end-to-end against. Anything newer is fine.
MIN_VERSION = (0, 9, 31)
LEGACY_DIR = os.path.join(os.path.expanduser("~"), ".antigravity-graphify")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="ignore", **kw)


def find_agy():
    """agy is OPTIONAL for /agy:graph (code graphs are local + free); it is used to name
    communities and to read docs/PDFs/images, which are the only steps that need an LLM."""
    agy = os.environ.get("AGY_BIN") or shutil.which("agy") or shutil.which("agy.exe")
    if not agy:
        cand = os.path.join(os.path.expanduser("~"), "AppData", "Local", "agy", "bin", "agy.exe")
        if os.path.isfile(cand):
            agy = cand
    return agy


def version_tuple(text):
    """'0.9.31' -> (0, 9, 31). Non-numeric segments degrade to 0 rather than raising."""
    out = []
    for seg in str(text).strip().split("."):
        digits = ""
        for ch in seg:
            if ch.isdigit():
                digits += ch
            else:
                break
        out.append(int(digits) if digits else 0)
    return tuple(out[:3]) or (0,)


def installed_version():
    """Version of `graphifyy` importable by THIS interpreter, or None."""
    p = run([sys.executable, "-c",
             "from importlib.metadata import version; print(version('graphifyy'))"])
    if p.returncode != 0:
        return None
    m = re.search(r"\d+(?:\.\d+)*", p.stdout or "")
    return m.group(0) if m else None


def module_path():
    p = run([sys.executable, "-c", "import graphify, sys; sys.stdout.write(graphify.__file__)"])
    return (p.stdout or "").strip() if p.returncode == 0 else ""


def is_legacy_install():
    """True when graphify resolves to the old patched clone this plugin used to create."""
    path = module_path()
    if not path:
        return False
    try:
        return os.path.commonpath([os.path.abspath(path), LEGACY_DIR]) == LEGACY_DIR
    except ValueError:      # different drives on Windows -> definitely not the legacy dir
        return False


def graphify_cmd():
    """How the shell should invoke Graphify. Prefer the console script; fall back to `-m graphify`
    for installs whose Scripts/bin dir is not on PATH (common on Windows + pip --user)."""
    exe = shutil.which("graphify") or shutil.which("graphify.exe")
    if exe:
        return exe
    return f'"{sys.executable}" -m graphify'


def pip_install():
    """Install/upgrade graphifyy from PyPI. Returns (ok, detail)."""
    attempts = [
        [sys.executable, "-m", "pip", "install", "-U", "-q", "graphifyy"],
        # PEP 668 "externally managed" interpreters (Debian/Ubuntu system Python, Homebrew)
        [sys.executable, "-m", "pip", "install", "-U", "-q", "--user", "graphifyy"],
    ]
    last = ""
    for cmd in attempts:
        r = run(cmd)
        if r.returncode == 0:
            return True, ""
        last = (r.stderr or r.stdout or "").strip()[-500:]
    if shutil.which("uv"):
        r = run(["uv", "tool", "install", "--upgrade", "graphifyy"])
        if r.returncode == 0:
            return True, ""
        last = (r.stderr or r.stdout or "").strip()[-500:]
    return False, last


def main():
    check_only = "--check" in sys.argv
    agy = find_agy()
    # Plain concatenation, not a multi-line f-string expression: those only parse on 3.12+.
    agy_note = "OK" if agy else "missing (optional - only needed to name communities / read docs)"
    print("[stack] agy CLI: " + agy_note)

    ver = installed_version()
    legacy = is_legacy_install()
    if legacy:
        print(f"[stack] graphify: LEGACY patched clone detected ({module_path()})")
    elif ver:
        print(f"[stack] graphify: {ver} installed")
    else:
        print("[stack] graphify: not installed")

    ok = bool(ver) and not legacy and version_tuple(ver) >= MIN_VERSION
    if ok:
        print(f"[stack] graphify {ver} >= {'.'.join(map(str, MIN_VERSION))}: OK (ready)")
        print(f"GRAPHIFY_CMD={graphify_cmd()}")
        print("READY" if agy else "READY_NO_AGY")
        return 0

    if check_only:
        print("MISSING")
        return 1

    if legacy:
        # The old editable install shadows the PyPI wheel — remove it first, otherwise
        # `import graphify` keeps resolving to the unpatchable v0.8 clone.
        print("[stack] migrating: uninstalling the old patched editable install ...")
        r = run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", "graphifyy"])
        if r.returncode != 0:
            print("[stack] uninstall failed:", (r.stderr or "").strip()[-400:])
            print("MISSING")
            return 2
        print(f"[stack] done. The old clone at {LEGACY_DIR} is now unused - safe to delete by hand.")

    print("[stack] installing graphifyy from PyPI (deps: tree-sitter, networkx, ...) - a minute ...")
    good, detail = pip_install()
    if not good:
        print("[stack] install failed:", detail)
        print("MISSING")
        return 2

    ver = installed_version()
    if not ver or version_tuple(ver) < MIN_VERSION:
        print(f"[stack] install finished but version check failed (got {ver!r}, "
              f"need >= {'.'.join(map(str, MIN_VERSION))})")
        print("MISSING")
        return 2

    print(f"[stack] INSTALLED OK - graphify {ver}")
    print(f"GRAPHIFY_CMD={graphify_cmd()}")
    print("READY" if agy else "READY_NO_AGY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
