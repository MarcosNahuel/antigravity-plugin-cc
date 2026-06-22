#!/usr/bin/env python3
"""Phase 5: adversarial consistency audit over a notebook knowledge base.

Pure stdlib SQL over `notebook.db` — finds the kinds of contradictions that matter for legal /
administrative work and writes `CONTRADICCIONES.md`. No agy, no deps, read-only.

Usage:  python notebook_audit.py <OUTDIR>

Checks:
  A) same concepto (monto.detalle) with conflicting amounts across documents
  B) same DNI under two or more different names (entity-dedup conflict)
  C) same expediente number under two or more different captions/values
  D) coverage gaps — documents that failed processing (estado='no_procesado')
  E) data quality — montos whose amount could not be parsed to cents
  F) resoluciones referenced with conflicting organismo/fecha
"""
import sys, os, sqlite3

def main():
    outdir = sys.argv[1]
    db = os.path.join(outdir, "notebook.db")
    if not os.path.exists(db):
        print("NO_DB: run /agy:notebook first"); return
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True); con.row_factory = sqlite3.Row
    out = ["# Contradicciones y revisiones — notebook KB", ""]
    total = 0

    def section(title, sql, fmt):
        nonlocal total
        rows = list(con.execute(sql))
        out.append(f"## {title} — {len(rows)}")
        if rows:
            total += len(rows)
            for r in rows:
                out.append("- " + fmt(r))
        else:
            out.append("- (sin hallazgos)")
        out.append("")

    section("A) Mismo concepto con montos en conflicto",
        """SELECT detalle AS concepto, COUNT(DISTINCT monto_cents) nd,
                  GROUP_CONCAT(DISTINCT printf('$%.2f', monto_cents/100.0)) montos,
                  GROUP_CONCAT(DISTINCT (SELECT numero_gde FROM documents d WHERE d.id=e.doc_id)) docs
           FROM entities e WHERE clase='monto' AND monto_cents IS NOT NULL AND TRIM(detalle)<>''
           GROUP BY LOWER(detalle) HAVING nd>1""",
        lambda r: f"**{r['concepto']}**: {r['montos']}  (docs: {r['docs']})")

    section("B) Mismo DNI bajo nombres distintos",
        """SELECT ent_key AS dni, GROUP_CONCAT(DISTINCT valor) nombres, COUNT(DISTINCT valor) n
           FROM entities WHERE clase='persona' AND LENGTH(ent_key)>=7
           GROUP BY ent_key HAVING n>1""",
        lambda r: f"DNI {r['dni']}: {r['nombres']}")

    section("C) Mismo expediente con valores distintos",
        """SELECT ent_key, GROUP_CONCAT(DISTINCT valor) vals, COUNT(DISTINCT valor) n
           FROM entities WHERE clase='expediente' AND TRIM(ent_key)<>''
           GROUP BY ent_key HAVING n>1""",
        lambda r: f"{r['ent_key']}: {r['vals']}")

    section("D) Documentos sin procesar (gaps de cobertura)",
        "SELECT nn, tipo, basename FROM documents WHERE estado='no_procesado' ORDER BY nn",
        lambda r: f"[{r['nn']}] {r['tipo']} — {r['basename']}")

    section("E) Montos sin importe parseable (revisar OCR)",
        """SELECT (SELECT numero_gde FROM documents d WHERE d.id=e.doc_id) doc, valor, quote
           FROM entities e WHERE clase='monto' AND monto_cents IS NULL""",
        lambda r: f"{r['doc']}: '{r['valor']}'  ({r['quote'] or ''})")

    section("F) Resoluciones con organismo/fecha en conflicto",
        """SELECT valor AS resol, COUNT(DISTINCT detalle||'|'||COALESCE(fecha_iso,'')) n,
                  GROUP_CONCAT(DISTINCT detalle) organismos, GROUP_CONCAT(DISTINCT fecha_iso) fechas
           FROM entities WHERE clase='resolucion' AND TRIM(valor)<>''
           GROUP BY valor HAVING n>1""",
        lambda r: f"{r['resol']}: organismos=[{r['organismos']}] fechas=[{r['fechas']}]")

    out.insert(2, f"**{total} hallazgos** para revisar. Cada uno cita su documento; verificá contra el original antes de actuar.\n")
    con.close()
    path = os.path.join(outdir, "CONTRADICCIONES.md")
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"AUDIT findings={total} report={path}")


if __name__ == "__main__":
    main()
