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

// Functions whose BODIES must stay byte-identical between the lib (source of
// truth) and the inlined block in the workflow. Includes `initialConfidence`,
// which is inlined too but not exported from the lib (so it's excluded from
// the export-presence check above).
const BODY_FNS = [...FNS, 'initialConfidence']

// Extracts the full source of `function <name>(...) { ... }` from `src`,
// starting at the `function` keyword (so a leading `export ` — present only
// on the lib side — is stripped automatically) and ending at the matching
// closing brace of the body. Uses paren-depth counting to skip past the
// parameter list (which may itself contain `{ ... }` destructuring, e.g.
// `isConverged({ coverage, matrix, ... })`) before brace-depth counting the
// body itself.
function extractFn(src, name) {
  const sigRe = new RegExp(`(?:export\\s+)?function\\s+${name}\\s*\\(`)
  const m = sigRe.exec(src)
  if (!m) return null
  const fnStart = src.indexOf('function', m.index)
  const parenStart = m.index + m[0].length - 1 // index of the opening '(' of the params
  let depth = 0
  let j = parenStart
  for (; j < src.length; j++) {
    if (src[j] === '(') depth++
    else if (src[j] === ')') { depth--; if (depth === 0) break }
  }
  if (depth !== 0) return null // unbalanced parens — malformed source
  const braceStart = src.indexOf('{', j + 1)
  if (braceStart === -1) return null
  let bd = 0
  let end = -1
  for (let k = braceStart; k < src.length; k++) {
    if (src[k] === '{') bd++
    else if (src[k] === '}') { bd--; if (bd === 0) { end = k; break } }
  }
  if (end === -1) return null // unbalanced braces — malformed source
  return src.slice(fnStart, end + 1)
}

test('workflow inlines every lib helper', () => {
  for (const fn of FNS) {
    assert.ok(new RegExp(`function ${fn}\\b`).test(wf), `workflow missing inlined ${fn}`)
    assert.ok(new RegExp(`export function ${fn}\\b`).test(lib), `lib missing exported ${fn}`)
  }
})

test('inlined workflow helper BODIES are byte-identical to the lib source (drift guard)', () => {
  for (const fn of BODY_FNS) {
    const libFn = extractFn(lib, fn)
    const wfFn = extractFn(wf, fn)
    assert.ok(libFn, `could not extract ${fn} from deep-research-lib.mjs — check the extractor or the source`)
    assert.ok(wfFn, `could not extract ${fn} from deep-research-agy.js — check the extractor or the inlined block`)
    assert.equal(wfFn, libFn, `${fn} has drifted between deep-research-lib.mjs (source of truth) and the inlined copy in deep-research-agy.js`)
  }
})

test('workflow has no import/require (self-contained)', () => {
  assert.ok(!/\bimport\s|\brequire\(/.test(wf.replace(/^export const meta[\s\S]*?\n/,'')), 'workflow must be self-contained')
})
