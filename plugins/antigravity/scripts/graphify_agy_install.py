#!/usr/bin/env python3
"""Install (or just check) Graphify with the `agy-cli` backend, so `/agy:graph` can build
knowledge graphs through Gemini (via the Antigravity CLI `agy`) — off Claude's tokens.

Idempotent + cross-platform. Clones Graphify (MIT) to ~/.antigravity-graphify/graphify, applies
the bundled `agy-cli-backend.patch`, and `pip install -e`s it. Re-running is a no-op once installed.

Usage:
  python graphify_agy_install.py            # install if missing, else verify
  python graphify_agy_install.py --check    # report status only, never install
"""
import os, sys, subprocess, shutil

HOME = os.path.expanduser("~")
TARGET = os.path.join(HOME, ".antigravity-graphify", "graphify")
PATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agy-cli-backend.patch")
GRAPHIFY_REPO = "https://github.com/safishamsi/graphify"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", **kw)


def find_agy():
    agy = os.environ.get("AGY_BIN") or shutil.which("agy") or shutil.which("agy.exe")
    if not agy:
        cand = os.path.join(HOME, "AppData", "Local", "agy", "bin", "agy.exe")
        if os.path.isfile(cand):
            agy = cand
    return agy


def graphify_has_agy_backend():
    """graphify importable AND aware of the agy-cli backend?"""
    p = run([sys.executable, "-c",
             "import graphify.llm as L,sys; sys.exit(0 if 'agy-cli' in L.BACKENDS else 3)"])
    return p.returncode == 0


def main():
    check_only = "--check" in sys.argv
    agy = find_agy()
    print(f"[stack] agy CLI: {'OK' if agy else 'MISSING — install from https://antigravity.google, run `agy` once to sign in'}")

    if graphify_has_agy_backend():
        print("[stack] graphify + agy-cli backend: OK (ready)")
        print("READY" if agy else "READY_BUT_AGY_MISSING")
        return 0 if agy else 1

    print("[stack] graphify + agy-cli backend: NOT installed")
    if check_only:
        print("MISSING")
        return 1

    if not os.path.isfile(PATCH):
        print(f"[stack] ERROR: bundled patch not found at {PATCH}")
        return 2
    if shutil.which("git") is None:
        print("[stack] ERROR: git is required to install graphify")
        return 2

    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    if not os.path.isdir(os.path.join(TARGET, ".git")):
        print(f"[stack] cloning graphify -> {TARGET} ...")
        r = run(["git", "clone", "--depth", "1", GRAPHIFY_REPO, TARGET])
        if r.returncode != 0:
            print("[stack] clone failed:", (r.stderr or "")[-400:])
            return 2

    llm_path = os.path.join(TARGET, "graphify", "llm.py")
    already = os.path.isfile(llm_path) and ("agy-cli" in open(llm_path, encoding="utf-8", errors="ignore").read())
    if not already:
        chk = run(["git", "-C", TARGET, "apply", "--check", PATCH])
        if chk.returncode == 0:
            run(["git", "-C", TARGET, "apply", PATCH])
            print("[stack] patch applied")
        else:
            print("[stack] patch apply failed:", (chk.stderr or "")[-400:])
            return 2
    else:
        print("[stack] patch already present")

    print("[stack] pip install -e graphify (deps: networkx, tree-sitter, ...) — this can take a minute ...")
    r = run([sys.executable, "-m", "pip", "install", "-e", TARGET, "-q"])
    if r.returncode != 0:
        print("[stack] pip install failed:", (r.stderr or "")[-500:])
        return 2

    if graphify_has_agy_backend():
        print("[stack] INSTALLED OK — graphify + agy-cli backend ready")
        print("READY" if agy else "READY_BUT_AGY_MISSING")
        return 0 if agy else 1
    print("[stack] install finished but verification failed")
    return 2


if __name__ == "__main__":
    sys.exit(main())
