#!/usr/bin/env python3
"""Phase 4: job records for long /agy:notebook sweeps (200-page document sets).

Makes a sweep OBSERVABLE and RESUMABLE without a daemon: a tiny JSON job record under
`<OUTDIR>/.jobs/` tracks per-document status, derived from the manifest + which summary files
exist on disk. The incremental cache already lets a re-run resume (done docs are skipped); this
adds visibility + an ETA so `/agy:notebook-status` can report progress mid-flight.

Usage:
  python notebook_job.py init   <OUTDIR> [<objetivo>]   # create/refresh the job from _manifest.tsv
  python notebook_job.py sync    <OUTDIR>                # recompute statuses from files on disk
  python notebook_job.py status  <OUTDIR>                # print a progress report (+ ETA)

Pure stdlib. Status of a member: done (summary exists, non-empty, not a stub) | failed
(stub estado=no_procesado) | pending (missing/empty).
"""
import sys, os, json, time, re


def jobfile(outdir):
    d = os.path.join(outdir, ".jobs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "current.json")


def members(outdir):
    """(summary_relpath, mode) per member, expanding group pipe-lists."""
    mpath = os.path.join(outdir, "_manifest.tsv")
    out = []
    if not os.path.exists(mpath):
        return out
    for ln in open(mpath, encoding="utf-8"):
        c = ln.rstrip("\n").split("\t")
        if len(c) < 6:
            continue
        for s in c[4].split("|"):
            out.append((s, c[1]))
    return out


def member_status(outdir, summ):
    p = os.path.join(outdir, summ)
    if not (os.path.exists(p) and os.path.getsize(p) > 0):
        return "pending"
    head = open(p, encoding="utf-8", errors="ignore").read(200)
    return "failed" if "estado: no_procesado" in head else "done"


def load(outdir):
    f = jobfile(outdir)
    if os.path.exists(f):
        try:
            return json.load(open(f, encoding="utf-8"))
        except Exception:
            pass
    return {}


def save(outdir, job):
    json.dump(job, open(jobfile(outdir), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def recompute(outdir, job):
    docs = {}
    for summ, mode in members(outdir):
        docs[summ] = member_status(outdir, summ)
    job["docs"] = docs
    job["counts"] = {s: sum(1 for v in docs.values() if v == s) for s in ("done", "pending", "failed")}
    job["counts"]["total"] = len(docs)
    job["updated"] = time.time()
    return job


def main():
    if len(sys.argv) < 3:
        print("usage: notebook_job.py init|sync|status <OUTDIR> [objetivo]"); return
    cmd, outdir = sys.argv[1], sys.argv[2]
    job = load(outdir)

    if cmd == "init":
        if not job.get("created"):
            job["created"] = time.time()
        job["objetivo"] = sys.argv[3] if len(sys.argv) > 3 else job.get("objetivo", "")
        job["outdir"] = outdir
        recompute(outdir, job)
        save(outdir, job)
        c = job["counts"]
        print(f"JOB init total={c['total']} done={c['done']} pending={c['pending']} failed={c['failed']}")
        return

    if cmd == "sync":
        recompute(outdir, job)
        save(outdir, job)
        c = job["counts"]
        print(f"JOB sync done={c['done']} pending={c['pending']} failed={c['failed']} total={c['total']}")
        return

    if cmd == "status":
        if not job:
            print("NO_JOB: no sweep recorded for this folder"); return
        recompute(outdir, job); save(outdir, job)
        c = job["counts"]
        created = job.get("created", job.get("updated", time.time()))
        elapsed = max(1.0, time.time() - created)
        rate = c["done"] / elapsed if c["done"] else 0          # docs/sec
        eta = (c["pending"] / rate) if rate > 0 and c["pending"] else (None if not c["pending"] else float("inf"))
        pct = 100.0 * (c["done"] + c["failed"]) / c["total"] if c["total"] else 100.0
        print(f"NOTEBOOK SWEEP — {pct:.0f}% ({c['done']}/{c['total']} done, {c['failed']} failed, {c['pending']} pending)")
        print(f"  elapsed={int(elapsed)}s" + (f"  eta~{int(eta)}s" if eta not in (None, float('inf')) else ("  eta=?" if c['pending'] else "  COMPLETE")))
        if job.get("objetivo"):
            print(f"  objetivo: {job['objetivo']}")
        pend = [s for s, st in job.get("docs", {}).items() if st == "pending"]
        if pend:
            print(f"  pendientes (primeros 8 de {len(pend)}): " + ", ".join(re.sub(r'\.resumen\.md$', '', x) for x in pend[:8]))
            print("  -> re-run  /agy:notebook <folder> | <objetivo>  to resume (cached docs are skipped)")
        return

    print(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
