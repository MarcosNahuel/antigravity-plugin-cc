import { test } from 'node:test'
import assert from 'node:assert/strict'
import { normURL, domainOf, distinctDomains, corroborationOf, ingestRound, isConverged, computeCoverage, rankClaimsForRedTeam, applyRedTeam } from '../deep-research-lib.mjs'

test('normURL strips www, scheme, trailing slash, lowercases', () => {
  assert.equal(normURL('https://WWW.Example.com/Path/'), 'example.com/path')
  assert.equal(normURL('http://example.com'), 'example.com')
  assert.equal(normURL('not a url'), 'not a url')
})

test('domainOf + distinctDomains', () => {
  assert.equal(domainOf('https://www.a.com/x'), 'a.com')
  assert.equal(distinctDomains(['https://a.com/1','https://www.a.com/2','https://b.org']), 2)
})

test('corroborationOf: 2+ domains = independent, else single-source', () => {
  assert.equal(corroborationOf({ sources:['https://a.com','https://b.com'] }), 'independent')
  assert.equal(corroborationOf({ sources:['https://a.com/1','https://a.com/2'] }), 'single-source')
})

test('ingestRound: assigns ids, dedups by source+claim, records failed angles', () => {
  const state = { findings: [], seenKeys: new Set(), failedAngles: [] }
  const results = [
    { angle:'A', status:'ok', findings:[{ claim:'X is true', evidence:'q', sources:['https://a.com'], sourceQuality:'primary', importance:'central' }] },
    { angle:'B', status:'failed', findings:[] },
    { angle:'C', status:'ok', findings:[{ claim:'X is true', evidence:'q2', sources:['https://a.com'], sourceQuality:'blog', importance:'supporting' }] }, // dup of A
  ]
  const novel = ingestRound(results, state, 1)
  assert.equal(novel, 1)
  assert.equal(state.findings.length, 1)
  assert.equal(state.findings[0].id, 'f0')
  assert.equal(state.findings[0].corroboration, 'single-source')
  assert.deepEqual(state.failedAngles, ['B'])
})

test('isConverged: needs all recommendation-changing rows answered+independent, stable, no open threads', () => {
  const matrix = [{ id:'m1', recommendationChanging:true }, { id:'m2', recommendationChanging:false }]
  const good = [{ matrixId:'m1', status:'answered', corroboration:'independent', confidence:'high' }]
  assert.equal(isConverged({ coverage:good, matrix, lastRoundChangedMaterially:false, openCriticalThreads:0 }), true)
  // single-source m1 → not converged
  assert.equal(isConverged({ coverage:[{ matrixId:'m1', status:'answered', corroboration:'single-source', confidence:'high' }], matrix, lastRoundChangedMaterially:false, openCriticalThreads:0 }), false)
  // last round changed something → not converged
  assert.equal(isConverged({ coverage:good, matrix, lastRoundChangedMaterially:true, openCriticalThreads:0 }), false)
  // open critical thread → not converged
  assert.equal(isConverged({ coverage:good, matrix, lastRoundChangedMaterially:false, openCriticalThreads:2 }), false)
})

test('computeCoverage aggregates sources/domains + flags central single-source', () => {
  const state = { failedAngles:['B'], findings:[
    { claim:'c1', sources:['https://a.com','https://b.com'], importance:'central', corroboration:'independent' },
    { claim:'c2', sources:['https://a.com/2'], importance:'central', corroboration:'single-source' },
  ] }
  const cov = computeCoverage(state, [{label:'A'},{label:'B'},{label:'C'}])
  assert.equal(cov.anglesFailed, 1)
  assert.equal(cov.anglesCompleted, 2)
  assert.equal(cov.distinctDomains, 2)
  assert.equal(cov.confidencePenalties.length, 1)
})

test('rankClaimsForRedTeam picks central or single-source, capped', () => {
  const findings = [
    { claim:'c1', importance:'central', corroboration:'independent' },
    { claim:'c2', importance:'tangential', corroboration:'single-source' },
    { claim:'c3', importance:'supporting', corroboration:'independent' }, // excluded
  ]
  const picked = rankClaimsForRedTeam(findings, 10).map(f => f.claim)
  assert.deepEqual(picked.sort(), ['c1','c2'])
})

test('applyRedTeam kills and downgrades (pure: no input mutation)', () => {
  const findings = [
    { id:'f0', claim:'c1', confidence:'high', redteam: null },
    { id:'f1', claim:'c2', confidence:'high', redteam: null },
  ]
  // Save original state for purity verification
  const origF0Confidence = findings[0].confidence
  const origF1Confidence = findings[1].confidence
  const origF0Redteam = findings[0].redteam
  const origF1Redteam = findings[1].redteam

  const alive = applyRedTeam(findings, [
    { claim:'c1', verdict:'kill' },
    { claim:'c2', verdict:'downgrade', newConfidence:'low' },
  ])

  // Verify output correctness
  assert.equal(alive.length, 1)
  assert.equal(alive[0].claim, 'c2')
  assert.equal(alive[0].confidence, 'low')
  assert.equal(alive[0].redteam.verdict, 'downgrade')

  // Verify input was NOT mutated (purity)
  assert.equal(findings[0].confidence, origF0Confidence, 'f0 confidence should not be mutated')
  assert.equal(findings[1].confidence, origF1Confidence, 'f1 confidence should not be mutated')
  assert.equal(findings[0].redteam, origF0Redteam, 'f0 redteam should not be mutated')
  assert.equal(findings[1].redteam, origF1Redteam, 'f1 redteam should not be mutated')
  assert.equal(findings[0].killed, undefined, 'f0 should not have killed property')
  assert.equal(findings[1].killed, undefined, 'f1 should not have killed property')
})
