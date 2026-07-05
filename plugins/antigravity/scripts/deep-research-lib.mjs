// Pure, node-testable helpers for /agy:deep-research.
// SINGLE SOURCE OF TRUTH — these functions are inlined verbatim into
// deep-research-agy.js (guarded by deep-research-wf-sync.test.mjs).
// Keep dependency-free and side-effect-free.

export function normURL(u) {
  try {
    const p = new URL(u)
    return (p.hostname.replace(/^www\./, '') + p.pathname.replace(/\/+$/, '')).toLowerCase()
  } catch { return String(u).trim().toLowerCase() }
}

export function domainOf(u) {
  try { return new URL(u).hostname.replace(/^www\./, '').toLowerCase() }
  catch { return String(u).trim().toLowerCase() }
}

export function distinctDomains(sources) {
  const set = new Set()
  for (const s of sources || []) set.add(domainOf(s))
  return set.size
}

export function corroborationOf(finding) {
  return distinctDomains(finding.sources) >= 2 ? 'independent' : 'single-source'
}

function initialConfidence(sourceQuality) {
  if (sourceQuality === 'primary') return 'high'
  if (sourceQuality === 'secondary') return 'medium'
  return 'low'
}

export function ingestRound(roundResults, state, round) {
  let novel = 0
  for (const res of roundResults || []) {
    if (!res || res.status === 'failed') { if (res && res.angle) state.failedAngles.push(res.angle); continue }
    for (const f of res.findings || []) {
      const primary = (f.sources && f.sources[0]) || ''
      const key = normURL(primary) + '::' + String(f.claim || '').slice(0, 60).toLowerCase()
      if (state.seenKeys.has(key)) continue
      state.seenKeys.add(key)
      const finding = {
        id: 'f' + state.findings.length, claim: f.claim, evidence: f.evidence || '',
        sources: f.sources || [], sourceQuality: f.sourceQuality || 'unreliable',
        importance: f.importance || 'supporting', recency: f.recency || 'unknown',
        angle: res.angle, round, confidence: initialConfidence(f.sourceQuality), corroboration: null, redteam: null,
      }
      finding.corroboration = corroborationOf(finding)
      state.findings.push(finding)
      novel++
    }
  }
  return novel
}

export function isConverged({ coverage, matrix, lastRoundChangedMaterially, openCriticalThreads }) {
  const critical = (matrix || []).filter(m => m.recommendationChanging)
  const allAnswered = critical.every(m => {
    const c = (coverage || []).find(x => x.matrixId === m.id)
    return c && c.status === 'answered' && c.corroboration === 'independent'
  })
  return allAnswered && !lastRoundChangedMaterially && (openCriticalThreads || 0) === 0
}

export function computeCoverage(state, angles) {
  const allSources = state.findings.flatMap(f => f.sources || [])
  const domains = new Set(allSources.map(domainOf))
  const penalties = []
  for (const f of state.findings) {
    if (f.importance === 'central' && f.corroboration === 'single-source') {
      penalties.push('Claim central de fuente única: "' + String(f.claim).slice(0, 60) + '"')
    }
  }
  return {
    anglesCompleted: (angles ? angles.length : 0) - state.failedAngles.length,
    anglesFailed: state.failedAngles.length,
    failedAngleLabels: [...state.failedAngles],
    sourceCount: new Set(allSources.map(normURL)).size,
    distinctDomains: domains.size,
    unresolvedCriticalGaps: [],
    confidencePenalties: penalties,
  }
}

const _impRank = { central: 0, supporting: 1, tangential: 2 }
export function rankClaimsForRedTeam(findings, limit) {
  return [...findings]
    .filter(f => f.importance === 'central' || f.corroboration === 'single-source')
    .sort((a, b) =>
      (_impRank[a.importance] - _impRank[b.importance]) ||
      ((a.corroboration === 'single-source' ? 0 : 1) - (b.corroboration === 'single-source' ? 0 : 1)))
    .slice(0, limit)
}

export function applyRedTeam(findings, verdicts) {
  const byClaim = new Map()
  for (const v of verdicts || []) if (v && v.claim) byClaim.set(v.claim, v)
  const result = []
  for (const f of findings) {
    const v = byClaim.get(f.claim)
    // Skip killed findings (do not add to result)
    if (v && v.verdict === 'kill') continue
    // Create new finding object (shallow copy) — never mutate input
    const newFinding = { ...f }
    // Add redteam field if verdict exists
    if (v) {
      newFinding.redteam = { verdict: v.verdict, refutingSource: v.refutingSource || null, evidence: v.refutingEvidence || '' }
      // Downgrade confidence if downgrade verdict
      if (v.verdict === 'downgrade') {
        newFinding.confidence = v.newConfidence || 'low'
      }
    }
    result.push(newFinding)
  }
  return result
}

export function renderReportMarkdown(report, meta) {
  const L = []
  L.push([
    '---', `title: "${meta.title}"`, 'type: research', 'source_tool: agy-deep-research',
    `depth: ${meta.depth}`, `rounds: ${meta.rounds}`, `converged: ${meta.converged}`,
    `created: ${meta.date}`, 'sensitivity: internal', '---', '',
  ].join('\n'))
  L.push(`# ${meta.title}\n`)
  if (report.tldr && report.tldr.length) { L.push('## TL;DR'); for (const b of report.tldr) L.push(`- ${b}`); L.push('') }
  if (report.context) { L.push('## Contexto'); L.push(report.context + '\n') }
  if (report.findings && report.findings.length) {
    L.push('## Findings')
    const TAG = { evidence:'EVIDENCIA', inference:'INFERENCIA', assumption:'SUPUESTO' }
    for (const f of report.findings) {
      const refs = (f.sources || []).map(s => `[${s}](${s})`).join(', ')
      L.push(`- **[${TAG[f.type] || f.type} · ${f.confidence}]** ${f.statement}${f.caveats ? ` _(${f.caveats})_` : ''}${refs ? ` — ${refs}` : ''}`)
    }
    L.push('')
  }
  if (report.comparisons) { L.push('## Comparaciones'); L.push(report.comparisons + '\n') }
  if (report.risksCounterarguments && report.risksCounterarguments.length) {
    L.push('## Riesgos y contraargumentos'); for (const r of report.risksCounterarguments) L.push(`- ${r}`); L.push('')
  }
  const a = report.appliedRecommendation
  if (a && a.applies) {
    L.push('## Recomendación aplicada'); L.push(a.recommendation + '\n')
    if (a.rationale) L.push(`**Por qué:** ${a.rationale}\n`)
    if (a.groundedContext) L.push(`**Contexto local:** ${a.groundedContext}\n`)
  }
  if (report.evidenceGaps && report.evidenceGaps.length) {
    L.push('## Evidence gaps'); for (const g of report.evidenceGaps) L.push(`- ${g}`); L.push('')
  }
  const c = report.coverage || {}
  L.push('## Cobertura y confianza')
  L.push(`- Ángulos completados: ${c.anglesCompleted ?? '?'} · caídos: ${c.anglesFailed ?? 0}${(c.failedAngleLabels && c.failedAngleLabels.length) ? ` (${c.failedAngleLabels.join(', ')})` : ''}`)
  L.push(`- Fuentes: ${c.sourceCount ?? '?'} · dominios distintos: ${c.distinctDomains ?? '?'}`)
  if (c.unresolvedCriticalGaps && c.unresolvedCriticalGaps.length) { L.push('- Gaps críticos sin resolver:'); for (const g of c.unresolvedCriticalGaps) L.push(`  - ${g}`) }
  if (c.confidencePenalties && c.confidencePenalties.length) { L.push('- Penalizaciones de confianza:'); for (const p of c.confidencePenalties) L.push(`  - ${p}`) }
  L.push('')
  if (report.conclusion) { L.push('## Conclusión'); L.push(`${report.conclusion.recommendation}\n`); L.push(`**Confianza global:** ${report.conclusion.overallConfidence}\n`) }
  if (report.references && report.references.length) {
    L.push('## Referencias'); for (const r of report.references) L.push(`${r.n}. [${r.title}](${r.url}) — ${r.type || ''}${r.date ? ', ' + r.date : ''}`); L.push('')
  }
  return L.join('\n')
}
