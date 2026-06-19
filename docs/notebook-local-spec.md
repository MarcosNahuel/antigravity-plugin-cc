# Spec — `/agy:notebook`: NotebookLM local sobre una carpeta de documentos

**Fecha:** 2026-06-19 · **Autor:** Marcos Nahuel Albornoz

## Objetivo

Reemplazar NotebookLM por un flujo **local** con agy (Gemini multimodal). Dada una
**carpeta de documentos** y un **objetivo** en lenguaje natural, agy recorre cada
documento (PDF con texto, PDF escaneado, imagen, docx), produce un **resumen `.md`
por documento** orientado al objetivo, y luego un **`INDEX.md`** (relevancia) y un
**`RESUMEN_MAESTRO.md`** (síntesis con citas).

Meta de diseño: **minimizar tokens de Claude Code** — agy hace toda la lectura
pesada; Claude orquesta y solo lee los dos archivos finales (chicos).

## No-objetivos (YAGNI)

- Sin modo chat/Q&A interactivo (one-shot).
- Sin audio overview, sin mapa mental, sin embeddings/vector store.
- Sin re-uso de conversiones previas de `doc-to-md` (el resumen es orientado al
  objetivo, no una conversión fiel).

## Uso

```
/agy:notebook <carpeta> | <objetivo>
```
- Separador `|` entre carpeta y objetivo. Si no hay `|`, todo lo que no resuelva a
  carpeta existente es el objetivo.
- Ej: `/agy:notebook ".../Documentos-EX-2022-04770549..." | fechas de reclamo de zona por grupo y montos`

## Arquitectura

Comando `commands/notebook.md` (context: principal — orquesta) + nuevo **MODE: notebook**
en `agents/agy-rescue.md` (un fork por documento, como `doc-to-md`).

### Fase 0 — listado (comando, 1 Bash)
- Resolver carpeta a ruta absoluta. Listar archivos soportados: `.pdf .docx .doc
  .png .jpg .jpeg .webp .gif`. Ordenar por nombre.
- `OUTDIR = docs/agy/notebook/<slug-carpeta>/`. `mkdir -p`.
- Si no hay archivos soportados → avisar y parar.

### Fase 1 — barrido por documento (1 fork agy por doc)
Por cada documento, detectar texto vs escaneado (**híbrido**):
- Extraer texto con un helper rápido (pdftotext/pymupdf). Si el texto útil supera un
  umbral (p.ej. ≥200 chars/página promedio) → **modo texto**: pasar el texto a agy.
- Si no (escaneado / poco texto) → **modo visión**: agy lee el archivo con visión/OCR.

agy escribe (con `write_file`, por issue #76) `OUTDIR/<NN>-<slug>.resumen.md`:
```
---
doc: <nombre archivo>
tipo: <NO|IF|PV|RS|ACTO|EXDIG|...>
numero_gde: <...>
fecha: <YYYY-MM-DD o "ilegible">
emisor: <área/persona>
relevancia: <0-100>
---
## Síntesis (orientada al objetivo)
<2-6 frases enfocadas en el objetivo>
## Datos clave
- <fechas, montos, resoluciones, personas — citables>
## Por qué es (ir)relevante para el objetivo
<1-2 frases>
```
- **Robustez**: si un doc falla o timeoutea, escribir un stub con `relevancia: 0` y
  `estado: no_procesado` y seguir. Nunca abortar el barrido completo.
- **Concurrencia**: tandas chicas (p.ej. 3-4 forks a la vez) para no saturar agy.

### Fase 2 — índice + síntesis (1 fork agy sobre los resúmenes)
Entrada: todos los `*.resumen.md` (chicos). agy escribe:
- `OUTDIR/INDEX.md`: tabla de todos los docs ordenada por `relevancia` desc
  (doc · tipo · fecha · relevancia · 1 línea), con sección **TOP** (los más
  relevantes al objetivo) destacada arriba.
- `OUTDIR/RESUMEN_MAESTRO.md`: síntesis del caso orientada al objetivo, **con citas**
  al `numero_gde`/nombre de cada doc (ej. "según IF-2026-02429965…"), un **timeline**
  de hitos y una **conclusión** que responde directamente al objetivo.

### Fase 3 — reporte (comando)
Claude lee SOLO `INDEX.md` + `RESUMEN_MAESTRO.md` y los presenta. No lee los docs
originales ni los resúmenes por-doc.

## Salida
```
docs/agy/notebook/<slug-carpeta>/
├── INDEX.md
├── RESUMEN_MAESTRO.md
└── NN-<slug>.resumen.md   (uno por documento)
```

## Cambios al plugin
1. `commands/notebook.md` — nuevo comando (parseo carpeta|objetivo, listado, dispatch).
2. `agents/agy-rescue.md` — nuevo `MODE: notebook` (per-doc) y `MODE: notebook-index`
   (síntesis). Reusa las reglas de invocación de agy (skip-permissions, write_file,
   print-timeout, add-dir).
3. `agents/agy-rescue.md` — **portar el fix de `MODE: setup`** (el "not logged into
   Antigravity" es warning NO fatal; test real = `write_file`). Ya corregido en cache.
4. Registrar el comando en `plugin.json`/marketplace si aplica; bump de versión + CHANGELOG.

## Riesgos / decisiones
- agy `--print` no vuelca stdout (issue #76) → **siempre** `write_file` + leer archivo.
- Lotes grandes timeoutean → **1 documento por llamada** agy.
- Warnings de auth secundaria son ruido → no tratarlos como falla.
