# antigravity-plugin-cc — Estado, aprendizajes y roadmap de mejoras

> Documento de handoff (2026-06-19). Resume el estado actual del plugin, los hechos
> técnicos duros de `agy`, lo ya aplicado, los plugins similares encontrados y el
> roadmap de mejoras concretas. Pensado para continuar las mejoras en otra sesión.

---

## 1. Estado actual — v0.6.5

Plugin de Claude Code que envuelve el CLI **`agy`** (Google Antigravity / Gemini 3.x)
vía un *thin Bash forwarder*. **11 comandos**:

| Comando | Qué hace |
|---|---|
| `/agy:notebook <carpeta> \| <objetivo>` | **NotebookLM local** — barre una carpeta → resumen por doc (orientado a objetivo) + `INDEX.md` (relevancia) + `RESUMEN_MAESTRO.md` (con citas). Híbrido texto/visión. **Nuevo en v0.6.4-0.6.5.** |
| `/agy:report <md>` | Markdown → HTML branded (TRAID Design System, 5 templates) |
| `/agy:ask <prompt>` | One-shot prompt |
| `/agy:review [focus]` | Code review del git diff |
| `/agy:research <tema>` | Web research profundo con citas |
| `/agy:rescue <task>` | Delegar tarea de código/diagnóstico |
| `/agy:record <url>` | Grabar walkthrough de navegador (.webm) |
| `/agy:scrape <url>` | Extracción estructurada de una URL |
| `/agy:doc-to-md <file>` | PDF/docx/imagen → markdown fiel |
| `/agy:design-review <url>` | Auditoría UX/visual (10 dimensiones) |
| `/agy:setup` | Health check |

**Arquitectura**: `commands/<x>.md` (parseo/orquestación) → subagente `agents/agy-rescue.md`
(modos) → `agy --print`. Cada modo escribe a un `WRITE_FILE` (por issue #76) y verifica el archivo.

---

## 2. Hechos técnicos de `agy` (gotchas — costaron descubrirlos)

1. **Issue #76 — stdout vacío fuera de TTY.** `agy --print` NO escribe a stdout cuando no es
   TTY (siempre, al llamarlo de un subproceso), aunque genere bien. → **Siempre usar `write_file`
   a un path y leer el archivo.** stdout vacío ≠ falla. (El plugin ya tiene recovery por
   `transcript.jsonl` como plan B.)
2. **Lotes grandes timeoutean.** Pasar muchas páginas/imágenes en una sola llamada agota el
   `--print-timeout`. → **1 documento por llamada agy.**
3. **"You are not logged into Antigravity" es ruido NO fatal… excepto para modelos/plan.**
   Aparece en scopes secundarios (`loadCodeAssist`, `FetchAvailableModels`, `ListExperiments`,
   `userInfo`, telemetría) **incluso en runs exitosos** (agy escribió el archivo con esos errores
   en el log). NO bloquea la generación. **PERO** sí bloquea ver la lista de modelos y reconocer el
   plan (Pro). Si SOLO esos endpoints fallan → re-loguear `agy` interactivo arregla el scope.
4. **Selección de modelo:** el flag `--model <id>` es **poco fiable** — si el id no está en la
   lista conocida de la cuenta, agy **cae al default en silencio** (probados `gemini-3.1-flash-lite`,
   `gemini-3.1-flash`, etc. → todos caen a "Gemini 3.5 Flash (Medium)"). La forma **confiable**:
   el TUI `agy` → "Switch Model" persiste en `~/.gemini/antigravity-cli/settings.json`
   (`"model": "Gemini 3.5 Flash (Low)"`) y `--print` lo respeta. El "(Low/Medium/High)" es el nivel
   de *thinking effort*; no hay flag CLI para eso, viene en la variante del modelo.
5. **Modelos disponibles (cuenta Pro del owner):** Flash 3.5 (Low/Medium/High), **3.1 Pro (Low/High)**,
   Claude Sonnet/Opus 4.6 (Thinking), GPT-OSS 120B. **NO hay flash-lite.** Para barridos masivos
   conviene **Flash 3.5 (Low)** (rápido/barato). El tier gratuito da solo Flash/Flash-Lite con ~10 RPM.
6. **Rate limit:** ~10 RPM en gratuito; más alto en Pro/Ultra. 250K TPM. (Google recortó quotas
   gratuitas 50-80% en dic-2025.)
7. **Windows rename bug (#217):** mitigado con pre-flight `.tmp` sweep + retry on output-file miss.

---

## 3. Mejoras ya aplicadas (esta sesión, v0.6.4-0.6.5)

- **`/agy:notebook`** completo (NotebookLM local): híbrido texto/visión, frontmatter con relevancia,
  índice + síntesis con citas. Probado sobre un expediente real de **48 documentos** (46 texto + 2
  visión escaneado/docx) → generó todo OK.
- **Fix `/agy:setup`**: ya no da falsa alarma de "re-login" por el ruido de auth secundaria; testea
  con `write_file` y distingue timeout/tamaño vs login real.
- **Concurrencia notebook**: hasta **10 docs/wave + reintento con backoff 60s** (patrón batch-LLM:
  cap de concurrencia + backoff, no paralelismo ciego).

---

## 4. Plugins similares (competencia / ideas a robar)

| Plugin | Qué hace distinto / a robar |
|---|---|
| **davdittrich/delegate-agy** (el más parecido) | **Routing por tipo→modelo** (`search`→Flash, `code/analysis/review/implement`→Pro) con **restricciones de tools por modo**. **`config/model-map.json`** con aliases (`pro`, `flash`) → ids reales (aísla del churn de nombres). **Prompt por stdin** (no por CLI arg → no se expone en `ps`). **gemini CLI shim** (reemplazo drop-in). Output JSON opcional. Timeouts por tipo. |
| **sakibsadmanshajib / m-ghalib — gemini-plugin-cc** | Gemini CLI vía **ACP (Agent-Client Protocol, JSON-RPC sobre stdio)** en vez de `--print`. Reviews adversariales. |
| **sickn33/antigravity-awesome-skills** | Librería de 1500+ skills agénticas instalables (Claude Code, Cursor, Codex, Gemini, Antigravity). Modelo de distribución/installer. |
| **badrisnarayanan/antigravity-claude-proxy** | Proxy que expone los modelos Claude/Gemini de Antigravity como API para usarlos en otros clientes. |

Fuentes: búsqueda web 2026-06-19 (delegate-agy README, geminicli.com/extensions, etc.).

---

## 5. Roadmap de mejoras propuestas (priorizado)

### Alta prioridad — ✅ HECHO en v0.6.6 (2026-06-19)
1. **Comando `/agy:model [nombre]`** — listar y **setear el modelo escribiendo `settings.json`**
   (`"model": "..."`). Es la forma confiable (el TUI hace exactamente eso; `--model` no sirve).
   Sin nombre → muestra el actual + opciones conocidas. Resuelve el dolor #4 sin abrir el TUI.
2. **`config/model-map.json` con aliases** (robar de delegate-agy): `flash-low`, `pro`, `flash`, etc.
   → labels reales ("Gemini 3.5 Flash (Low)"). Que `/agy:model flash-low` y la doc usen alias estables.
3. **notebook — caché incremental**: hashear cada documento (mtime+size o sha) y **saltar los que ya
   tienen `.resumen.md` actualizado**. Re-correr un expediente solo procesa lo nuevo/cambiado.
   (Hoy re-procesa todo.) Gran ahorro de tiempo/quota en expedientes grandes.
4. **notebook — routing por tipo de doc**: resúmenes por-doc con **Flash (Low)**; la síntesis final
   (`notebook-index`) con **3.1 Pro (Low)** (más calidad donde importa). Robar el patrón de delegate-agy.

### Media
5. **notebook — modo Q&A sobre el corpus** (`/agy:notebook-ask <carpeta> <pregunta>`): responder
   preguntas citando los `.resumen.md` (el chat de NotebookLM). Ya tenemos los resúmenes como índice.
6. **notebook — agrupar docs chicos**: las providencias (PV) de 1 página son ruido; agruparlas en
   una sola llamada "providencias de trámite" reduce llamadas y quota.
7. **Prompt por stdin** (robar de delegate-agy): pasar el prompt por stdin, no como arg de `--print`,
   por seguridad (no aparece en `ps`/logs del sistema).
8. **notebook — salida adicional**: `TIMELINE.md` y/o `ENTIDADES.md` (personas/montos/expedientes)
   como artefactos extra (estilo "briefing doc" de NotebookLM).

### Baja / explorar
9. **Audio overview** (estilo NotebookLM podcast) si agy/Gemini expone TTS.
10. **ACP en vez de `--print`** (como gemini-plugin-cc) — evita issue #76 de raíz, pero es refactor grande.
11. **JSON output** opcional en los comandos que devuelven datos estructurados (scrape/notebook index).

---

## 6. Notas operativas

- **Versionado**: bump en `plugins/antigravity/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
  (2 lugares) y `package.json`; entrada en `CHANGELOG.md`; tag `vX.Y.Z`. Mantener las 3 versiones sincronizadas.
- **Validar JSON** antes de pushear (un JSON roto rompe el plugin).
- **Update del plugin instalado**: en Claude Code `/plugin` → update `marcosnahuel-antigravity` →
  **reiniciar Claude Code** (se carga al iniciar sesión). El cambio de **modelo** (settings.json) NO
  requiere reinstalar — aplica al toque.
- **Repo**: `github.com/MarcosNahuel/antigravity-plugin-cc`, marketplace `marcosnahuel-antigravity`.
- Último estado pusheado: **v0.6.5** (commit del 2026-06-19).
