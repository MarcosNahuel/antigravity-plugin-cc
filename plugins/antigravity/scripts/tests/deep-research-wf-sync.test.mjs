import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const dir = dirname(fileURLToPath(import.meta.url))
const lib = readFileSync(join(dir, '../deep-research-lib.mjs'), 'utf8')
const wf = readFileSync(join(dir, '../deep-research-agy.js'), 'utf8')

// Cada función de la lib debe existir inlineada (sin `export`) en el workflow.
const FNS = ['normURL','domainOf','distinctDomains','corroborationOf','ingestRound','isConverged','computeCoverage','rankClaimsForRedTeam','applyRedTeam']

test('workflow inlines every lib helper', () => {
  for (const fn of FNS) {
    assert.ok(new RegExp(`function ${fn}\\b`).test(wf), `workflow missing inlined ${fn}`)
    assert.ok(new RegExp(`export function ${fn}\\b`).test(lib), `lib missing exported ${fn}`)
  }
})

test('workflow has no import/require (self-contained)', () => {
  assert.ok(!/\bimport\s|\brequire\(/.test(wf.replace(/^export const meta[\s\S]*?\n/,'')), 'workflow must be self-contained')
})
