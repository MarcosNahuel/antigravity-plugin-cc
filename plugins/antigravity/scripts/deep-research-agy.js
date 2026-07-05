export const meta = { name: 'deep-research-agy',
  description: 'Deep research multi-agente: agy browsea, Claude razona; rondas adaptativas L<=2/H<=4, red-team, síntesis.',
  phases: [{ title:'Round 1' },{ title:'Round 2+' },{ title:'Red-team' },{ title:'Synthesize' }] }

// ─── INLINED from deep-research-lib.mjs — keep in sync (deep-research-wf-sync.test.mjs) ───
function normURL(u) {
  try {
    const p = new URL(u)
    return (p.hostname.replace(/^www\./, '') + p.pathname.replace(/\/+$/, '')).toLowerCase()
  } catch { return String(u).trim().toLowerCase() }
}

function domainOf(u) {
  try { return new URL(u).hostname.replace(/^www\./, '').toLowerCase() }
  catch { return String(u).trim().toLowerCase() }
}

function distinctDomains(sources) {
  const set = new Set()
  for (const s of sources || []) set.add(domainOf(s))
  return set.size
}

function corroborationOf(finding) {
  return distinctDomains(finding.sources) >= 2 ? 'independent' : 'single-source'
}

function initialConfidence(sourceQuality) {
  if (sourceQuality === 'primary') return 'high'
  if (sourceQuality === 'secondary') return 'medium'
  return 'low'
}

function ingestRound(roundResults, state, round) {
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

function isConverged({ coverage, matrix, lastRoundChangedMaterially, openCriticalThreads }) {
  const critical = (matrix || []).filter(m => m.recommendationChanging)
  const allAnswered = critical.every(m => {
    const c = (coverage || []).find(x => x.matrixId === m.id)
    return c && c.status === 'answered' && c.corroboration === 'independent'
  })
  return allAnswered && !lastRoundChangedMaterially && (openCriticalThreads || 0) === 0
}

function computeCoverage(state, angles) {
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
function rankClaimsForRedTeam(findings, limit) {
  return [...findings]
    .filter(f => f.importance === 'central' || f.corroboration === 'single-source')
    .sort((a, b) =>
      (_impRank[a.importance] - _impRank[b.importance]) ||
      ((a.corroboration === 'single-source' ? 0 : 1) - (b.corroboration === 'single-source' ? 0 : 1)))
    .slice(0, limit)
}

function applyRedTeam(findings, verdicts) {
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
// ─── END INLINED ───

const ANGLE_SCHEMA = { type:'object', required:['angle','status','findings','threads'], properties:{
  angle:{type:'string'}, status:{enum:['ok','partial','failed']}, rawArtifactPath:{type:'string'},
  findings:{type:'array', items:{ type:'object', required:['claim','evidence','sources','sourceQuality','importance'], properties:{
    claim:{type:'string'}, evidence:{type:'string'}, sources:{type:'array', items:{type:'string'}},
    sourceQuality:{enum:['primary','secondary','blog','forum','unreliable']},
    importance:{enum:['central','supporting','tangential']}, recency:{type:'string'} }}},
  threads:{type:'array', items:{ type:'object', required:['thread','class'], properties:{
    thread:{type:'string'}, class:{enum:['decision-critical','contradiction-risk','recency-risk','nice-to-have']} }}} } }
const GLOBAL_SCHEMA = { type:'object', required:['coverage','preConclusions','gaps','nextFocus','converged','answered'], properties:{
  coverage:{type:'array', items:{ type:'object', required:['matrixId','status','corroboration','confidence'], properties:{
    matrixId:{type:'string'}, status:{enum:['answered','partial','open']},
    corroboration:{enum:['independent','single-source','conflicting']}, confidence:{enum:['high','medium','low']} }}},
  preConclusions:{type:'array', items:{ type:'object', required:['statement','confidence'], properties:{
    statement:{type:'string'}, confidence:{enum:['high','medium','low']}, basis:{type:'string'} }}},
  gaps:{type:'array', items:{ type:'object', required:['question','recommendationChanging'], properties:{
    question:{type:'string'}, matrixId:{type:['string','null']}, whyItMatters:{type:'string'}, recommendationChanging:{type:'boolean'} }}},
  nextFocus:{type:'array', items:{ type:'object', required:['label','query'], properties:{
    label:{type:'string'}, query:{type:'string'}, targetsGap:{type:'string'} }}},
  converged:{type:'boolean'}, convergenceRationale:{type:'string'},
  lastRoundChangedMaterially:{type:'boolean'}, openCriticalThreads:{type:'number'}, answered:{type:'number'} } }
const REDTEAM_SCHEMA = { type:'object', required:['claim','refuted','verdict'], properties:{
  claim:{type:'string'}, refuted:{type:'boolean'}, refutingEvidence:{type:'string'},
  refutingSource:{type:['string','null']}, recencyOk:{type:'boolean'},
  verdict:{enum:['hold','downgrade','kill']}, newConfidence:{enum:['high','medium','low']} } }
const REPORT_SCHEMA = { type:'object', required:['tldr','findings','conclusion','references'], properties:{
  tldr:{type:'array', items:{type:'string'}}, context:{type:'string'},
  findings:{type:'array', items:{ type:'object', required:['statement','type','confidence','sources'], properties:{
    statement:{type:'string'}, type:{enum:['evidence','inference','assumption']},
    confidence:{enum:['high','medium','low']}, sources:{type:'array', items:{type:'string'}}, caveats:{type:'string'} }}},
  comparisons:{type:'string'}, risksCounterarguments:{type:'array', items:{type:'string'}},
  appliedRecommendation:{type:'object', properties:{ applies:{type:'boolean'}, recommendation:{type:'string'},
    rationale:{type:'string'}, groundedContext:{type:'string'} }},
  evidenceGaps:{type:'array', items:{type:'string'}},
  coverage:{type:'object'}, conclusion:{type:'object', required:['recommendation','overallConfidence'], properties:{
    recommendation:{type:'string'}, overallConfidence:{enum:['high','medium','low']} }},
  references:{type:'array', items:{ type:'object', required:['n','title','url'], properties:{
    n:{type:'number'}, title:{type:'string'}, url:{type:'string'}, type:{type:'string'}, date:{type:'string'} }}} } }

// The engine may deliver `args` as a JSON string; parse defensively so the
// command (or a manual invocation) can pass either an object or a string.
const _args = typeof args === 'string' ? JSON.parse(args) : (args || {})
const { question, matrix, angles, depth, engines, deepDir, date, title } = _args
const MAX_ROUNDS = depth === 'H' ? 4 : 2
const RT_TARGETS = depth === 'H' ? 10 : 5
const ANGLE_TIMEOUT = depth === 'H' ? '4m0s' : '3m0s'

const anglePrompt = (f, round, i) =>
  `MODE: deep-angle\nROUND: ${round}\nWRITE_FILE: ${deepDir}/r${round}-${i}-${slug(f.label)}.md\n` +
  `QUESTION: ${question}\nQUERY: ${f.query}\nTIMEOUT: ${ANGLE_TIMEOUT}\nUSER_TEXT:\n${f.query}`
const redTeamPrompt = (c, i) =>
  `MODE: redteam\nWRITE_FILE: ${deepDir}/redteam-${i}.md\nQUESTION: ${question}\nCLAIM: ${c.claim}\nUSER_TEXT:\n${c.claim}`
function slug(s){ return String(s).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40) }

const state = { findings: [], seenKeys: new Set(), failedAngles: [] }
let focus = angles, converged = false, round = 0, lastAnalysis = null
const attemptedAngles = []

while (round < MAX_ROUNDS && !converged) {
  round++
  const ph = round === 1 ? 'Round 1' : 'Round 2+'
  attemptedAngles.push(...focus)
  const results = (await parallel(focus.map((f, i) => () =>
    agent(anglePrompt(f, round, i), { label:`r${round}:${f.label}`, phase:ph, schema:ANGLE_SCHEMA, agentType:'antigravity:agy-rescue' })
  ))).filter(Boolean)
  const novel = ingestRound(results, state, round)
  log(`R${round}: +${novel} findings (${state.findings.length} total, ${state.failedAngles.length} failed angles)`)
  const analysis = await agent(
    `Global research analysis, round ${round}.\n\nQuestion: ${question}\n\nEvidence matrix (JSON):\n${JSON.stringify(matrix)}\n\n` +
    `Accumulated findings (JSON):\n${JSON.stringify(state.findings)}\n\n` +
    `Task: for each matrix row give coverage {matrixId,status,corroboration,confidence}. corroboration=independent needs >=2 distinct domains. ` +
    `List pre-conclusions with confidence. List ranked gaps (recommendationChanging flag). If NOT converged, propose nextFocus (label+query) targeting the top recommendation-changing gaps and any decision-critical/contradiction/recency threads. ` +
    `Set converged=true only if every recommendation-changing row is answered+independent, this round changed nothing material, and no critical threads remain. Report lastRoundChangedMaterially and openCriticalThreads.`,
    { label:`global:r${round}`, phase:ph, schema:GLOBAL_SCHEMA })
  if (!analysis) { log('deep-research: global analysis returned null — ending round loop with accumulated findings'); break }
  lastAnalysis = analysis
  converged = analysis.converged === true || isConverged({ coverage:analysis.coverage, matrix, lastRoundChangedMaterially:analysis.lastRoundChangedMaterially, openCriticalThreads:analysis.openCriticalThreads })
  focus = (analysis.nextFocus || [])
  log(`R${round}: ${analysis.answered}/${matrix.length} answered; converged=${converged}; nextFocus=${focus.length}`)
  if (!focus.length) break
}

// Red-team (agy)
phase('Red-team')
const targets = rankClaimsForRedTeam(state.findings, RT_TARGETS)
const verdicts = (await parallel(targets.map((c, i) => () =>
  agent(redTeamPrompt(c, i), { label:`rt:${c.id}`, phase:'Red-team', schema:REDTEAM_SCHEMA, agentType:'antigravity:agy-rescue' })
))).filter(Boolean)
const survivors = applyRedTeam(state.findings, verdicts)

// Synthesis (Claude)
phase('Synthesize')
const coverage = computeCoverage({ findings:survivors, failedAngles:state.failedAngles }, attemptedAngles)
if (lastAnalysis && lastAnalysis.gaps) coverage.unresolvedCriticalGaps = lastAnalysis.gaps.filter(g => g.recommendationChanging).map(g => g.question)
let report = await agent(
  `Synthesize the final research report.\n\nQuestion: ${question}\n\nMatrix:\n${JSON.stringify(matrix)}\n\n` +
  `Verified findings (JSON):\n${JSON.stringify(survivors)}\n\nCoverage:\n${JSON.stringify(coverage)}\n\n` +
  `Produce REPORT_SCHEMA. Tag each finding evidence|inference|assumption. If the question asks to apply findings to a specific design, set appliedRecommendation.applies=true and write a concrete recommendation (leave groundedContext empty — the caller fills local context). Map references [n] to real URLs from the findings' sources.`,
  { label:'synthesize', phase:'Synthesize', schema: REPORT_SCHEMA })
if (!report) {
  report = {
    tldr: [], context: '',
    findings: survivors.map(f => ({ statement: f.claim, type: 'evidence', confidence: f.confidence, sources: f.sources, caveats: f.evidence || '' })),
    risksCounterarguments: [], appliedRecommendation: { applies: false, recommendation: '', groundedContext: '' },
    evidenceGaps: [], conclusion: { recommendation: '(La síntesis falló; informe degradado desde los findings verificados.)', overallConfidence: 'low' }, references: [],
  }
}
report.coverage = coverage
return { report, coverage, rounds: round, converged }
