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
