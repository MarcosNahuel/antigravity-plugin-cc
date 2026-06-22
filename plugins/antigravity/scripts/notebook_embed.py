#!/usr/bin/env python3
"""Phase 3 (opt-in `--semantic`): add a vector layer to a notebook knowledge base.

Embeds every chunk in `notebook.db` and stores the vectors in a `sqlite-vec` `vec0` table so
`/agy:notebook-query` can do HYBRID retrieval (FTS5 keyword + vector semantic, fused with RRF).
FTS5 stays the always-on default; this is purely additive and opt-in.

Usage:  python notebook_embed.py <OUTDIR>

Dependencies (opt-in only): `pip install sqlite-vec`. Embeddings come from:
  1. Google Gemini REST (`text-embedding-004`, 768-dim) if a REAL `GEMINI_API_KEY` is in the env
     — recommended, true semantic search. Pure stdlib `urllib` (no SDK).
  2. else a stdlib LEXICAL-HASH fallback (256-dim) — works with zero deps/key but is keyword-ish,
     not truly semantic; prints a warning. Set GEMINI_API_KEY for real semantic quality.
"""
import sys, os, re, json, math, struct, hashlib, sqlite3, urllib.request

GEMINI_MODEL = "text-embedding-004"
GEMINI_DIM = 768
HASH_DIM = 256


def real_key():
    k = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    return k if (k and not k.startswith("$") and len(k) >= 20) else None


def hash_embed(text, dim=HASH_DIM):
    v = [0.0] * dim
    for tok in re.findall(r"\w+", (text or "").lower()):
        v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % dim] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def gemini_embed_batch(texts, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:batchEmbedContents?key={key}"
    reqs = [{"model": f"models/{GEMINI_MODEL}", "content": {"parts": [{"text": t[:8000] or " "}]}} for t in texts]
    body = json.dumps({"requests": reqs}).encode()
    r = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    out = json.load(urllib.request.urlopen(r, timeout=60))
    return [e["values"] for e in out["embeddings"]]


def packf(v):
    return struct.pack("%df" % len(v), *v)


def main():
    outdir = sys.argv[1]
    db = os.path.join(outdir, "notebook.db")
    if not os.path.exists(db):
        print("NO_DB: run /agy:notebook first"); return
    try:
        import sqlite_vec
    except ImportError:
        print("SEMANTIC_UNAVAILABLE: pip install sqlite-vec  (FTS5 keyword search still works without it)")
        return

    key = real_key()
    if key:
        embedder, dim = "gemini:text-embedding-004", GEMINI_DIM
    else:
        embedder, dim = "lexhash-256", HASH_DIM
        print("WARNING: no real GEMINI_API_KEY — using lexical-hash fallback (keyword-ish, NOT true "
              "semantic). Set GEMINI_API_KEY for real embeddings.")

    con = sqlite3.connect(db)
    con.enable_load_extension(True); sqlite_vec.load(con); con.enable_load_extension(False)
    cur = con.cursor()
    # (re)create the vec table at the right dim if missing or dim changed
    prev_dim = None
    row = cur.execute("SELECT v FROM meta WHERE k='embed_dim'").fetchone()
    if row:
        try: prev_dim = int(row[0])
        except Exception: prev_dim = None
    if prev_dim != dim:
        cur.execute("DROP TABLE IF EXISTS vec_chunks")
    cur.execute(f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks USING vec0(chunk_id INTEGER PRIMARY KEY, embedding float[{dim}])")
    cur.execute("DELETE FROM vec_chunks")

    rows = cur.execute("SELECT id, texto FROM chunks WHERE texto IS NOT NULL AND texto<>''").fetchall()
    n = 0
    if key:
        BATCH = 100
        for i in range(0, len(rows), BATCH):
            chunk = rows[i:i + BATCH]
            try:
                vecs = gemini_embed_batch([t for _, t in chunk], key)
            except Exception as e:
                print(f"EMBED_ERROR batch {i}: {str(e)[:140]} — falling back to lexhash for the rest")
                key = None; embedder, dim = "lexhash-256", HASH_DIM
                cur.execute("DROP TABLE IF EXISTS vec_chunks")
                cur.execute(f"CREATE VIRTUAL TABLE vec_chunks USING vec0(chunk_id INTEGER PRIMARY KEY, embedding float[{dim}])")
                rows = cur.execute("SELECT id, texto FROM chunks WHERE texto IS NOT NULL AND texto<>''").fetchall()
                n = 0
                break
            for (cid, _), v in zip(chunk, vecs):
                cur.execute("INSERT INTO vec_chunks(chunk_id,embedding) VALUES(?,?)", (cid, packf(v))); n += 1
    if not key:
        for cid, t in rows:
            cur.execute("INSERT INTO vec_chunks(chunk_id,embedding) VALUES(?,?)", (cid, packf(hash_embed(t)))); n += 1

    for k_, v_ in (("embedder", embedder), ("embed_dim", str(dim)), ("embedded_chunks", str(n))):
        cur.execute("INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k_, v_))
    con.commit(); con.close()
    print(f"EMBEDDED chunks={n} embedder={embedder} dim={dim} db={db}")


if __name__ == "__main__":
    main()
