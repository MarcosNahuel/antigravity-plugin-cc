# Prompt para el repo de TRAID — construir la página del plugin Antigravity

> Copiá TODO lo que está debajo de la línea `=== PROMPT ===` y pegáselo al agente
> (Claude Code / el que uses) **dentro del repositorio del sitio traidagency.com**.
> Es autocontenido: trae el copy, los links, los assets y los criterios de aceptación.
>
> **Antes de pegar**, copiá estos 2 archivos a la carpeta de assets del sitio TRAID
> (o dejá que el agente use las URLs raw de GitHub que están más abajo):
> - `notebook-demo.gif`  (la demo animada)
> - `social-preview.png` (la card 1280×640 para Open Graph)
>
> Ambos están en este repo en `docs/promo/`. URLs raw (fallback si no querés copiarlos):
> - https://raw.githubusercontent.com/MarcosNahuel/antigravity-plugin-cc/main/docs/promo/notebook-demo.gif
> - https://raw.githubusercontent.com/MarcosNahuel/antigravity-plugin-cc/main/docs/promo/social-preview.png

---

=== PROMPT ===

Sos el desarrollador del sitio **traidagency.com** (marca TRAID). Tu tarea es crear una
**página de proyecto** para un producto open-source propio: un plugin de Claude Code llamado
**Antigravity Plugin** — "a local NotebookLM for Claude Code".

El objetivo de la página es doble: (1) **SEO / autoridad** — un backlink do-follow desde nuestro
dominio hacia el repo de GitHub para subir su ranking, y (2) **portfolio** — mostrar un proyecto
open-source de TRAID con un pitch claro y un demo visual.

## 1. Dónde y cómo

- Ruta sugerida: `/labs/antigravity` (o `/proyectos/antigravity` si esa es la convención del sitio).
  Revisá primero cómo están armadas las otras páginas/proyectos del repo y **seguí ese patrón
  exacto** (mismo layout, componentes, sistema de estilos, i18n si aplica). No inventes un stack nuevo.
- Agregá la página al índice de proyectos/labs y al sitemap si el sitio tiene uno.
- Idioma: igualá el del resto del sitio (si es ES, escribí en español; si es bilingüe, ambos).

## 2. Assets

- **Demo (hero):** `notebook-demo.gif` — colocalo como elemento principal arriba. Si lo copiaste a
  assets, referencialo localmente; si no, usá la URL raw:
  `https://raw.githubusercontent.com/MarcosNahuel/antigravity-plugin-cc/main/docs/promo/notebook-demo.gif`
  (preferí copiarlo local: más rápido y no depende de GitHub). Ancho ~760px, centrado, con `alt`
  descriptivo. Si el sitio soporta `loading="lazy"`, usalo.
- **Open Graph / Twitter card:** `social-preview.png` (1280×640) para las meta tags `og:image` y
  `twitter:image`.

## 3. SEO (importante — es el motivo #1 de la página)

- `<title>`: **Antigravity Plugin — a local NotebookLM for Claude Code | TRAID**
- `<meta name="description">` (~155 chars): *A Claude Code plugin that turns a folder of documents
  into a cited synthesis via Google's Antigravity CLI (Gemini 3.x). Open source, MIT.*
- Open Graph: `og:title`, `og:description`, `og:type=article`, `og:image=social-preview.png`,
  `og:url` = la URL canónica de esta página.
- Twitter: `twitter:card=summary_large_image`, `twitter:image`.
- **Canonical:** apuntá `<link rel="canonical">` a ESTA página de TRAID (somos el origen del contenido).
- **Todos los links al repo y al release deben ser do-follow** (sin `rel="nofollow"`). Este es el
  punto clave para el SEO del repo.
- Si el sitio usa JSON-LD, agregá un `SoftwareApplication` (o `CreativeWork`) con name, description,
  author (Marcos Nahuel Albornoz / TRAID), license MIT, codeRepository = el repo.
- Encabezados semánticos: un solo `<h1>` con el nombre + tagline; `<h2>` por sección.

## 4. Contenido de la página (usá EXACTAMENTE estos datos — no inventes features ni números)

**H1 / Hero**
> # Antigravity Plugin
> ### A local NotebookLM for Claude Code

**Pitch (1 párrafo, sin emojis, tono TRAID — claro y técnico, no marketinero):**
> Antigravity Plugin conecta Claude Code con la CLI oficial de Google Antigravity (`agy`, Gemini 3.x,
> multimodal). Con `/agy:notebook <carpeta> | <objetivo>` lee una carpeta entera de documentos
> —PDFs, escaneos, imágenes, docx— dentro de Gemini y devuelve un resumen por documento, un índice
> de relevancia, una síntesis maestra **con citas**, una línea de tiempo y una hoja de entidades.
> Después, `/agy:notebook-ask` responde preguntas sobre todo eso, también con citas. La lectura
> pesada ocurre en Gemini, así que casi no consume el contexto de Claude.

**Sección "Qué hace" (bullets — copialos tal cual):**
- **NotebookLM local** — `/agy:notebook` convierte una carpeta de documentos en INDEX + síntesis
  maestra citada + TIMELINE + ENTIDADES, sin meter los documentos crudos en el contexto de Claude.
- **Q&A con citas** — `/agy:notebook-ask <carpeta> | <pregunta>` responde sobre los resúmenes.
- **Audio y video** — `/agy:transcribe` (nota de voz, reunión, URL de YouTube → transcripción +
  resumen) y `/agy:media` ("¿qué se decidió en el minuto 2:30?"). Claude no puede oír/ver media; agy sí.
- **Investigación web con citas**, **grabación de walkthroughs de navegador**, **scraping
  estructurado**, **doc→markdown** y **design review** visual/UX.
- **MIT, sin runtime de Node.** Es el camino de migración desde el `gemini-cli` (deprecado el 18/06/2026).

**Sección "Instalación" (bloque de código, copiá literal):**
```
/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
/agy:setup
```
> Requiere la CLI `agy` instalada + inicio de sesión con Google.

**Sección "Por qué" (1-2 frases):**
> Construido en TRAID para no reventar el contexto de Claude Code con carpetas extensas de documentos
> larga: la lectura se delega a Gemini y solo vuelve la síntesis. Pensado para casos reales con
> cientos de páginas.

**CTAs / Links (do-follow):**
- Repositorio (GitHub): https://github.com/MarcosNahuel/antigravity-plugin-cc
- Último release: https://github.com/MarcosNahuel/antigravity-plugin-cc/releases/latest
- Autor: Marcos Nahuel Albornoz — https://github.com/MarcosNahuel

## 5. Reglas

- **No toques** ni rompas otras páginas, el layout global, ni la config de build/deploy.
- Reutilizá los componentes y tokens de diseño que ya existen en el repo.
- No agregues dependencias nuevas salvo que sea imprescindible (y avisá antes si lo fuera).
- No publiques/deploys vos: dejá los cambios en una rama nueva (`feat/antigravity-page`) y, si el
  flujo del repo lo usa, abrí un PR. Esperá mi revisión antes de mergear a producción.
- Datos fijos: nombre del producto = "Antigravity Plugin"; tagline = "a local NotebookLM for Claude
  Code"; licencia = MIT; autor = Marcos Nahuel Albornoz (TRAID).

## 6. Criterios de aceptación

- [ ] Página nueva en la ruta acordada, siguiendo el patrón de las páginas existentes.
- [ ] GIF demo visible arriba, con `alt`.
- [ ] Meta tags completas (title, description, OG, Twitter, canonical → esta página).
- [ ] Links al repo y al release **do-follow**.
- [ ] Enlazada desde el índice de proyectos/labs y agregada al sitemap.
- [ ] Build pasa sin errores; no se rompió ninguna otra página.
- [ ] Cambios en una rama nueva, sin deploy automático.

Empezá explorando el repo para entender el stack y el patrón de páginas; después construí. Cuando
termines, decime la ruta de la página, los archivos que tocaste y cómo levantar el preview local.

=== FIN DEL PROMPT ===
