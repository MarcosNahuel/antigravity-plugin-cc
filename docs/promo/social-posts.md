# Social posts — antigravity-plugin-cc (ready to paste)

Repo: https://github.com/MarcosNahuel/antigravity-plugin-cc

> Reddit drafts moved to [`reddit.md`](reddit.md). Show HN moved to [`show-hn.md`](show-hn.md).
> This file is X/Twitter (English, technical, build-in-public) + LinkedIn (Spanish, thought
> leadership for the LATAM AI community). Value/insight first in both; the repo link and any TRAID
> mention come after, never in the opening line. No superlatives, no star-begging, no "check out my
> new tool" framing.

---

## X / Twitter — thread (English, build-in-public)

Lead with the deep-research demo (the newest, most technically interesting piece) and one
hard-won gotcha, not a feature list. Post as a thread from a personal account; no vote/RT asks.

**1/**
```
Spent the last stretch building a multi-agent deep-research loop into a Claude Code plugin.

The part I actually care about: it's honest when it didn't finish. Coverage, dropped angles, and
open questions ship in the report — not just findings.

Thread on how it works 🧵
```

**2/**
```
The loop, roughly:

1. Claude builds an evidence matrix from your question (which sub-answers could flip the
   conclusion) + a research plan you approve
2. agy (Gemini 3.x) browses each angle in parallel
3. Claude judges convergence between rounds — not a fixed pass count
4. a red-team pass attacks single-source claims before synthesis
```

**3/**
```
The report shows what it didn't manage to close: dropped angles, still-open critical questions,
claims downgraded to "single-source" after red-teaming.

Overstating coverage was a design decision to avoid, not a bug to catch later.
```

**4/**
```
One gotcha that cost real hours, in case it saves someone else's: on Windows, Git Bash
auto-translates POSIX paths passed as bare CLI args — but NOT paths embedded inside a full prompt
sentence. Looked identical to a totally different upstream bug for a day.

Fix: run it through cygpath before it touches the prompt text.
```

**5/**
```
It also has a local-NotebookLM mode — point it at a folder of PDFs/scans, get a cited synthesis,
without the documents leaving your machine or filling Claude's context.

22 commands total. MIT. Alpha. Not affiliated with Google or Anthropic.
```

**6/**
```
Install (inside Claude Code):

/plugin marketplace add MarcosNahuel/antigravity-plugin-cc
/plugin install antigravity@marcosnahuel-antigravity
/agy:setup

Repo + how it's built 👇
https://github.com/MarcosNahuel/antigravity-plugin-cc
```

---

## LinkedIn (español, liderazgo técnico — comunidad IA LATAM)

Formato recomendado por la investigación para esta audiencia: gancho con dato concreto en las
primeras 40-50 palabras, cuerpo con la decisión de arquitectura (no el pitch del producto), **link
al repo en el primer comentario, no en el cuerpo del post** (el enlace externo en el cuerpo baja el
alcance). Mención a TRAID al final, un renglón, sin venta.

**Post:**
```
Un detalle de arquitectura que me costó bastante decidir bien: cuándo un sistema de research con
IA debería admitir que no terminó, en vez de entregar todo con la misma confianza.

Le agregué a un plugin que armé para Claude Code un loop de investigación multi-agente: arma una
matriz de evidencia de la pregunta, un agente navega la web por ángulos en paralelo, otro agente
juzga si conviene una ronda más o si ya convergió, y un paso final de red-team ataca justo los
datos que dependen de una sola fuente.

Lo que más me importa no es que investigue rápido — es que el reporte final diga con qué ángulos
se quedó cortos, qué preguntas críticas siguen abiertas y qué afirmaciones bajaron de confianza
después del red-team. Que un sistema de IA sea honesto sobre su propia cobertura me parece más
valioso que uno que suene seguro de todo.

Es open source (MIT), todavía alpha, y no tiene nada que ver con Google ni Anthropic más que
hablar con sus CLIs públicas con tus propias credenciales — lo cuento como aprendizaje de
ingeniería, no como lanzamiento de producto.

Si a alguien de la comunidad de IA en LATAM le sirve la arquitectura del loop (matriz de
evidencia, convergencia entre rondas, red-team), lo charlamos en los comentarios.

Este es un proyecto personal — en el día a día lidero ingeniería en TRAID, donde armamos sistemas
de automatización e IA para e-commerce en LATAM y USA. Distinto contexto, misma obsesión: que el
sistema no diga que hizo más de lo que realmente hizo.
```

**Primer comentario (con el link, no en el cuerpo):**
```
Repo con el detalle técnico completo: https://github.com/MarcosNahuel/antigravity-plugin-cc
```
