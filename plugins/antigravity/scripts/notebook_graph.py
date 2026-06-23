#!/usr/bin/env python3
"""Export a notebook knowledge base (notebook.db) to a knowledge GRAPH — a node-link `graph.json`
plus a self-contained interactive `graph.html` — with NO agy calls and NO extra deps (stdlib only).

Why: agy rarely fills the explicit `relaciones` array, so the relational layer of the RAG sits empty.
This derives edges that don't need agy: **entity co-occurrence within a document** (the main signal)
plus any explicit relations that ARE present. Lets you SEE the document/entity network and reason
over it, complementing the SQL queries. Self-contained — does not require Graphify.

Usage:  python notebook_graph.py <OUTDIR>        # writes <OUTDIR>/graph.json and <OUTDIR>/graph.html

Nodes = deduped entities (persona | organizacion | referencia) + documents.
Edges = entity-co_mentioned-entity (weight = #docs they share) + explicit relations + entity-in-document.
"""
import os, sys, json, sqlite3, html
from itertools import combinations
from collections import defaultdict, Counter

ENTITY_CLASSES = ("persona", "organizacion", "referencia")
COLORS = {"persona": "#5896ff", "organizacion": "#46c88c", "referencia": "#ebc85a", "documento": "#9aa6bd"}
MAX_ENTS_PER_DOC = 25   # skip co-occurrence on docs with an entity explosion


def main():
    outdir = sys.argv[1]
    db = os.path.join(outdir, "notebook.db")
    if not os.path.exists(db):
        print("NO_DB: run /agy:notebook first"); return 1
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); con.row_factory = sqlite3.Row

    # deduped entity nodes: key = (clase, ent_key); label = most common valor; track docs it appears in
    label_votes = defaultdict(Counter)
    ent_docs = defaultdict(set)
    for r in con.execute(
            "SELECT clase, ent_key, valor, doc_id FROM entities WHERE clase IN (?,?,?) AND TRIM(ent_key)<>''",
            ENTITY_CLASSES):
        key = (r["clase"], r["ent_key"])
        if r["valor"]:
            label_votes[key][r["valor"]] += 1
        ent_docs[key].add(r["doc_id"])

    def nid(key):
        return f"{key[0]}:{key[1]}"

    nodes = []
    for key, docs in ent_docs.items():
        clase, _ = key
        label = label_votes[key].most_common(1)[0][0] if label_votes[key] else key[1]
        nodes.append({"id": nid(key), "label": label, "type": clase,
                      "n_docs": len(docs), "color": COLORS.get(clase, "#ccc")})

    # document nodes
    doc_label = {}
    for d in con.execute("SELECT id, doc_ref, basename, tipo FROM documents"):
        did = f"doc:{d['id']}"
        lab = d["doc_ref"] or d["basename"] or f"doc {d['id']}"
        doc_label[d["id"]] = (did, lab)
        nodes.append({"id": did, "label": lab, "type": "documento",
                      "n_docs": 1, "color": COLORS["documento"]})

    # edges
    links = []
    seen = set()

    def add(a, b, relation, weight=1):
        if a == b:
            return
        k = tuple(sorted((a, b))) + (relation,)
        if k in seen:
            return
        seen.add(k)
        links.append({"source": a, "target": b, "relation": relation, "weight": weight})

    # entity -> document membership
    for key, docs in ent_docs.items():
        for d in docs:
            if d in doc_label:
                add(nid(key), doc_label[d][0], "appears_in")

    # entity co-occurrence within a document (the relational signal that needs no agy)
    by_doc = defaultdict(list)
    for key, docs in ent_docs.items():
        for d in docs:
            by_doc[d].append(key)
    cooc = Counter()
    for d, keys in by_doc.items():
        if len(keys) > MAX_ENTS_PER_DOC:
            continue
        for a, b in combinations(sorted(set(keys)), 2):
            cooc[(a, b)] += 1
    for (a, b), w in cooc.items():
        add(nid(a), nid(b), "co_mentioned", w)

    # explicit relations, if any (string-match subject/object to known entity labels)
    lab2id = {}
    for n in nodes:
        lab2id.setdefault(n["label"].strip().lower(), n["id"])
    n_explicit = 0
    for r in con.execute("SELECT sujeto, predicado, objeto FROM relations"):
        s = lab2id.get((r["sujeto"] or "").strip().lower())
        o = lab2id.get((r["objeto"] or "").strip().lower())
        if s and o:
            add(s, o, (r["predicado"] or "rel")[:40], 1); n_explicit += 1

    graph = {"directed": False, "multigraph": False, "graph": {}, "nodes": nodes, "links": links}
    json.dump(graph, open(os.path.join(outdir, "graph.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    _write_html(outdir, nodes, links)

    deg = Counter()
    for l in links:
        deg[l["source"]] += 1; deg[l["target"]] += 1
    id2lab = {n["id"]: n["label"] for n in nodes}
    hubs = ", ".join(f"{id2lab.get(i, i)}({c})" for i, c in deg.most_common(5))
    print(f"GRAPH nodes={len(nodes)} edges={len(links)} (cooccur={len(cooc)}, explicit={n_explicit}) "
          f"hubs=[{hubs}] -> {os.path.join(outdir, 'graph.html')}")
    con.close()
    return 0


def _write_html(outdir, nodes, links):
    data = json.dumps({"nodes": nodes, "edges": [
        {"from": l["source"], "to": l["target"], "label": l["relation"], "value": l.get("weight", 1)}
        for l in links]}, ensure_ascii=False)
    doc = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>notebook graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>html,body{margin:0;height:100%;background:#0d111c;color:#e6eaf2;font:14px system-ui}
#net{height:88vh;border-bottom:1px solid #2a3346}#h{padding:10px 16px}
.lg span{display:inline-block;margin-right:14px}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:middle}</style>
</head><body>
<div id="h"><b>Notebook knowledge graph</b> — """ + str(len(nodes)) + """ nodes · """ + str(len(links)) + """ edges
<span class="lg" style="margin-left:14px">
<span><i class="dot" style="background:#5896ff"></i>persona</span>
<span><i class="dot" style="background:#46c88c"></i>organización</span>
<span><i class="dot" style="background:#ebc85a"></i>referencia</span>
<span><i class="dot" style="background:#9aa6bd"></i>documento</span></span></div>
<div id="net"></div>
<script>
const G=""" + data + """;
const nodes=new vis.DataSet(G.nodes.map(n=>({id:n.id,label:n.label,color:n.color,
  value:(n.n_docs||1),shape:n.type==='documento'?'box':'dot',font:{color:'#e6eaf2'}})));
const edges=new vis.DataSet(G.edges.map((e,i)=>({id:i,from:e.from,to:e.to,
  title:e.label,value:e.value})));
new vis.Network(document.getElementById('net'),{nodes,edges},{
  physics:{stabilization:true,barnesHut:{gravitationalConstant:-8000,springLength:120}},
  nodes:{scaling:{min:8,max:34}},edges:{smooth:false,color:{color:'#34406a',opacity:0.5}},
  interaction:{hover:true,tooltipDelay:120}});
</script></body></html>"""
    open(os.path.join(outdir, "graph.html"), "w", encoding="utf-8").write(doc)


if __name__ == "__main__":
    sys.exit(main())
