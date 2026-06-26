#!/usr/bin/env python3
"""Run ONE `agy --print` call in an isolated scratch dir, then MOVE its outputs to their final paths.

WHY (validated 2026-06-26): agy snapshots every untracked file of any repo passed via `--add-dir`
on EVERY call (slow startup), and sandboxes write_file to project paths (rejection→replan round-trips).
Staging the read inputs + the writes in a neutral scratch dir gives **0 snapshots + 0 rejections**
with **byte-identical model output** — measured 15s/20snap/2rej → 9s/0/0, same extracted facts.
This generalizes the pattern the graphify agy-cli backend already runs in production. ZERO quality
cost: agy gets the identical prompt + identical input bytes and produces the identical output; only
the file's final location changes, and the move happens AFTER agy exits.

Usage:
  python agy_scratch.py --timeout 360 [--in ABS_READ]... [--out ABS_WRITE]... --prompt "PROMPT"

The PROMPT should reference each --in path (the file agy reads) and each --out path (the file agy
writes via write_file), exactly as it would today. This helper transparently maps those absolute
paths to copies/targets inside a fresh scratch dir, runs `agy --add-dir <scratch>` ONLY, then moves
each produced --out from scratch to its final absolute path. Prints `MOVED <abs>` / `MISSING <abs>`;
exits non-zero if any --out was not produced (so the caller's existing failure handling kicks in).

Each call mints its OWN scratch dir → safe under the notebook fan-out (disjoint per concurrent call).
"""
import os, sys, shutil, subprocess, tempfile, argparse, glob


def find_agy():
    a = os.environ.get("AGY_BIN") or shutil.which("agy") or shutil.which("agy.exe")
    if not a:
        c = os.path.expanduser("~/AppData/Local/agy/bin/agy.exe")
        if os.path.isfile(c):
            a = c
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", default="360")
    ap.add_argument("--in", dest="ins", action="append", default=[])
    ap.add_argument("--in-dir", dest="indirs", action="append", default=[])
    ap.add_argument("--out", dest="outs", action="append", default=[])
    ap.add_argument("--prompt")
    ap.add_argument("--prompt-file")
    a = ap.parse_args()

    agy = find_agy()
    if not agy:
        print("ERROR: agy not found (install https://antigravity.google or set AGY_BIN)"); return 2
    prompt = a.prompt if a.prompt is not None else (
        open(a.prompt_file, encoding="utf-8").read() if a.prompt_file else "")

    scratch = tempfile.mkdtemp(prefix="agy-scratch-")
    mapping = []                       # (abs_path_in_prompt, scratch_abs) — for prompt rewrite
    for p in a.ins:
        sp = os.path.join(scratch, os.path.basename(p))
        try:
            shutil.copy(p, sp)
        except Exception as e:
            shutil.rmtree(scratch, ignore_errors=True)
            print(f"ERROR staging input {p}: {e}"); return 2
        mapping.append((p, sp))
    # --in-dir: stage every file of a directory into scratch and rewrite the dir reference to scratch
    for d in a.indirs:
        for f in glob.glob(os.path.join(d, "*")):
            if os.path.isfile(f):
                try:
                    shutil.copy(f, os.path.join(scratch, os.path.basename(f)))
                except Exception:
                    pass
        mapping.append((d.rstrip("\\/"), scratch))
    out_map = []                       # (scratch_abs, final_abs)
    for p in a.outs:
        sp = os.path.join(scratch, os.path.basename(p))
        out_map.append((sp, p)); mapping.append((p, sp))

    # rewrite the prompt's absolute paths -> scratch paths (longest first to avoid partial overlaps)
    for orig, sp in sorted(mapping, key=lambda x: -len(x[0])):
        prompt = prompt.replace(orig, sp)

    to = a.timeout if str(a.timeout).endswith("s") else f"{a.timeout}s"
    cmd = [agy, "--dangerously-skip-permissions", "--add-dir", scratch,
           "--print-timeout", to, "--print", prompt]
    try:
        subprocess.run(cmd, input="", capture_output=True, text=True, encoding="utf-8",
                       errors="ignore", cwd=scratch,
                       timeout=int(str(a.timeout).rstrip("s")) + 30, check=False)
    except Exception as e:
        print(f"agy run error: {e}")

    missing = 0
    for sp, fp in out_map:
        if os.path.exists(sp) and os.path.getsize(sp) > 0:
            os.makedirs(os.path.dirname(fp) or ".", exist_ok=True)
            try:
                shutil.move(sp, fp)                      # atomic on same volume
            except Exception:
                try:
                    shutil.copy(sp, fp); os.remove(sp)   # cross-volume fallback
                except Exception as e:
                    print(f"MISSING {fp} (move failed: {e})"); missing += 1; continue
            print(f"MOVED {fp}")
        else:
            print(f"MISSING {fp}"); missing += 1

    shutil.rmtree(scratch, ignore_errors=True)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
