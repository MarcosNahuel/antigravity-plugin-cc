#!/usr/bin/env node
// Render a deep-research report object to markdown via the shared lib.
// Usage: node render-report.mjs <path-to-json>   where json = { report, meta }
import { readFileSync } from 'node:fs'
import { renderReportMarkdown } from './deep-research-lib.mjs'

const jsonPath = process.argv[2]
if (!jsonPath) { console.error('usage: render-report.mjs <report-json-path>'); process.exit(1) }
const { report, meta } = JSON.parse(readFileSync(jsonPath, 'utf8'))
process.stdout.write(renderReportMarkdown(report, meta))
