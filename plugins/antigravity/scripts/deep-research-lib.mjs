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
