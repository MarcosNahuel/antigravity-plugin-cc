#!/usr/bin/env python3
"""Name a Graphify run's communities with Gemini via `agy` — OFF the host assistant's tokens.

Graphify 0.9 builds a code graph deterministically (tree-sitter AST, no LLM, no API key). The one
step that genuinely wants a language model is Step 5, naming each community: without it the report
reads "Community 0 / Community 1 / ...". Upstream fills that gap either from an API key backend
(`graphify label --backend gemini`) or by having the *host agent* name them — which on Claude Code
would spend Claude's tokens, exactly what this plugin exists to avoid.

So we hand the job to agy: ONE `agy --print` call per batch of communities, reading the analysis
sidecar Graphify already wrote and returning a `{cid: name}` map. We write that map to
`graphify-out/.graphify_labels.json`, which `graphify cluster-only` picks up on its next run.

Contract note (matters): `cluster-only` only trusts a saved label map when it covers EVERY current
community — a partial map is silently replaced by hub-derived names. So we label all of them or we
report failure and let the caller fall back to `--no-label`.

Usage:
  python graphify_label_agy.py <folder> [--timeout 300] [--batch 100]

Last line is machine-readable: `LABELED <n>` on success, `FAILED <reason>` otherwise.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH_RUNNER = os.path.join(HERE, "agy_scratch.py")
MAX_MEMBERS_SHOWN = 20          # per community, enough to name it without bloating the prompt


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def resolve_out_dir(folder):
    """Where Graphify actually wrote its sidecars. `GRAPHIFY_OUT` may be an absolute path (used by
    graphify_outdir.py to dodge Windows MAX_PATH) or a relative directory name next to the project."""
    override = (os.environ.get("GRAPHIFY_OUT") or "").strip()
    if override:
        return override if os.path.isabs(override) else os.path.join(folder, override)
    return os.path.join(folder, "graphify-out")


def node_labels(graph_path):
    """id -> human label, so the prompt shows `main()` instead of `notebook_db_main`."""
    try:
        graph = load_json(graph_path)
    except Exception:
        return {}
    out = {}
    for node in graph.get("nodes", []):
        if isinstance(node, dict) and node.get("id"):
            out[node["id"]] = node.get("label") or node["id"]
    return out


def build_prompt(batch, communities, labels, out_file):
    lines = [
        "You are naming the clusters of a code/document knowledge graph.",
        "",
        "For EACH community below, write a 2-5 word human-readable name describing what its members "
        "have in common (e.g. \"Auth token refresh\", \"Postgres migrations\", \"Invoice PDF export\"). "
        "Use the language the identifiers are written in. Do not invent members. Do not number them "
        "\"Community N\" — that is the placeholder you are replacing.",
        "",
    ]
    for cid in batch:
        members = communities[cid][:MAX_MEMBERS_SHOWN]
        shown = ", ".join(labels.get(m, m) for m in members)
        extra = len(communities[cid]) - len(members)
        if extra > 0:
            shown += f", (+{extra} more)"
        lines.append(f"- community {cid}: {shown}")
    lines += [
        "",
        "OUTPUT REQUIREMENT (CRITICAL): a single raw JSON object mapping each community id (as a "
        "string) to its name, and nothing else — no prose, no markdown fences. It must contain "
        f"exactly these {len(batch)} keys: {', '.join(json.dumps(str(c)) for c in batch)}.",
        f"Write that JSON with your write_file tool to this absolute path: {out_file}",
        "Do not print it to chat; the written file is your only deliverable.",
    ]
    return "\n".join(lines)


def run_batch(batch, communities, labels, timeout):
    """One agy call. Returns {cid_str: name} for this batch, or {} on failure."""
    tmpdir = tempfile.mkdtemp(prefix="graphify-labels-")
    out_file = os.path.join(tmpdir, "labels.json")
    prompt = build_prompt(batch, communities, labels, out_file)
    cmd = [sys.executable, SCRATCH_RUNNER, "--timeout", str(timeout),
           "--out", out_file, "--prompt", prompt]
    try:
        subprocess.run(cmd, input="", capture_output=True, text=True, encoding="utf-8",
                       errors="ignore", timeout=int(timeout) + 90, check=False)
    except Exception as exc:
        print(f"[labels] agy call failed: {exc}", file=sys.stderr)
        return {}

    if not os.path.isfile(out_file):
        return {}
    try:
        with open(out_file, encoding="utf-8") as fh:
            raw = fh.read().strip()
    finally:
        try:
            os.remove(out_file)
            os.rmdir(tmpdir)
        except OSError:
            pass
    if not raw:
        return {}
    # Tolerate a stray fence even though the prompt forbids one.
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    for cid, name in data.items():
        name = str(name).strip()
        # Reject the placeholder shape: upstream treats "Community N" as "no label" anyway.
        if name and not name.lower().startswith("community "):
            out[str(cid)] = name[:80]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--batch", type=int, default=100)
    args = ap.parse_args()

    out_dir = resolve_out_dir(os.path.abspath(args.folder))
    analysis_path = os.path.join(out_dir, ".graphify_analysis.json")
    if not os.path.isfile(analysis_path):
        print(f"FAILED no analysis sidecar at {analysis_path} (run `graphify extract` first)")
        return 1
    try:
        communities = load_json(analysis_path).get("communities") or {}
    except Exception as exc:
        print(f"FAILED unreadable analysis sidecar: {exc}")
        return 1
    if not communities:
        print("FAILED analysis sidecar has no communities")
        return 1

    labels = node_labels(os.path.join(out_dir, "graph.json"))
    cids = list(communities.keys())
    named = {}
    for start in range(0, len(cids), max(1, args.batch)):
        batch = cids[start:start + max(1, args.batch)]
        got = run_batch(batch, communities, labels, args.timeout)
        named.update({c: got[c] for c in map(str, batch) if c in got})
        print(f"[labels] batch {start // max(1, args.batch) + 1}: "
              f"{len(got)}/{len(batch)} named", file=sys.stderr)

    missing = [c for c in map(str, cids) if c not in named]
    if missing:
        # Partial maps are worse than none: cluster-only would drop ALL of them for hub names.
        print(f"FAILED agy named {len(named)}/{len(cids)} communities "
              f"(missing {', '.join(missing[:8])}{' ...' if len(missing) > 8 else ''})")
        return 1

    labels_path = os.path.join(out_dir, ".graphify_labels.json")
    with open(labels_path, "w", encoding="utf-8") as fh:
        json.dump(named, fh, ensure_ascii=False, indent=2)
    print(f"[labels] wrote {labels_path}", file=sys.stderr)
    print(f"LABELED {len(named)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
