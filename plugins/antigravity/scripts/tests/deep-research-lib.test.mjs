import { test } from 'node:test'
import assert from 'node:assert/strict'
import { normURL, domainOf, distinctDomains, corroborationOf, ingestRound } from '../deep-research-lib.mjs'

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
