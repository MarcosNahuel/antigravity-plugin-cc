# Graph Report - C:\Users\MALBOR~1\AppData\Local\Temp\expediente_test  (2026-06-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 18 nodes · 24 edges · 3 communities
- Extraction: 50% EXTRACTED · 50% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Proyecto Phoenix Collaboration|Proyecto Phoenix Collaboration]]
- [[_COMMUNITY_Globex SA Personnel|Globex SA Personnel]]
- [[_COMMUNITY_Contract CT-2026-008 Administration|Contract CT-2026-008 Administration]]

## God Nodes (most connected - your core abstractions)
1. `Jane Smith` - 4 edges
2. `Jane Smith` - 4 edges
3. `Acme Corp` - 3 edges
4. `Globex SA` - 3 edges
5. `Jane Smith` - 3 edges
6. `Contrato CT-2026-008` - 3 edges
7. `Globex SA` - 3 edges
8. `Acme Corp` - 3 edges
9. `Proyecto Phoenix` - 3 edges
10. `Jane Smith` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Jane Smith` --semantically_similar_to--> `Jane Smith`  [INFERRED] [semantically similar]
  01-acta-kickoff.md → 02-contrato-globex.md
- `Globex SA` --semantically_similar_to--> `Globex SA`  [INFERRED] [semantically similar]
  02-contrato-globex.md → 03-minuta-revision.md
- `Jane Smith` --semantically_similar_to--> `Jane Smith`  [INFERRED] [semantically similar]
  03-minuta-revision.md → 04-nota-cierre.md
- `Proyecto Phoenix` --semantically_similar_to--> `Proyecto Phoenix`  [INFERRED] [semantically similar]
  01-acta-kickoff.md → 04-nota-cierre.md
- `Acme Corp` --semantically_similar_to--> `Acme Corp`  [INFERRED] [semantically similar]
  01-acta-kickoff.md → 02-contrato-globex.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Jane Smith CTO Role** — 01_acta_kickoff_jane_smith, 02_contrato_globex_jane_smith, 03_minuta_revision_jane_smith, 04_nota_cierre_jane_smith [INFERRED 0.90]
- **Globex Contract Lifecycle** — 02_contrato_globex_contrato_ct_2026_008, 03_minuta_revision_contrato_ct_2026_008, 02_contrato_globex_carlos_ruiz, 03_minuta_revision_carlos_ruiz [INFERRED 0.90]
- **Proyecto Phoenix Lifecycle** — 01_acta_kickoff_proyecto_phoenix, 04_nota_cierre_proyecto_phoenix, 01_acta_kickoff_acme_corp, 04_nota_cierre_acme_corp [INFERRED 0.90]

## Communities (3 total, 0 thin omitted)

### Community 0 - "Proyecto Phoenix Collaboration"
Cohesion: 0.28
Nodes (9): Acme Corp, Globex SA, Jane Smith, Proyecto Phoenix, Acme Corp, Globex SA, Acme Corp, Acme Corp (+1 more)

### Community 1 - "Globex SA Personnel"
Cohesion: 0.40
Nodes (5): Carlos Ruiz, Carlos Ruiz, Globex SA, Globex SA, Jane Smith

### Community 2 - "Contract CT-2026-008 Administration"
Cohesion: 0.67
Nodes (4): Contrato CT-2026-008, Jane Smith, Contrato CT-2026-008, Jane Smith

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Jane Smith` connect `Contract CT-2026-008 Administration` to `Proyecto Phoenix Collaboration`, `Globex SA Personnel`?**
  _High betweenness centrality (0.214) - this node is a cross-community bridge._
- **Why does `Jane Smith` connect `Proyecto Phoenix Collaboration` to `Contract CT-2026-008 Administration`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **Why does `Jane Smith` connect `Contract CT-2026-008 Administration` to `Proyecto Phoenix Collaboration`?**
  _High betweenness centrality (0.173) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Jane Smith` (e.g. with `Jane Smith` and `Jane Smith`) actually correct?**
  _`Jane Smith` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Acme Corp` (e.g. with `Acme Corp` and `Acme Corp`) actually correct?**
  _`Acme Corp` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Globex SA` (e.g. with `Globex SA` and `Globex SA`) actually correct?**
  _`Globex SA` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Jane Smith` (e.g. with `Jane Smith` and `Jane Smith`) actually correct?**
  _`Jane Smith` has 2 INFERRED edges - model-reasoned connections that need verification._