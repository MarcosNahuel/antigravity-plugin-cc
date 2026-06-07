#!/usr/bin/env node
/**
 * antigravity-plugin-cc — npm presence / install helper.
 *
 * This package IS a Claude Code plugin (markdown + JSON, no runtime). Claude
 * Code installs plugins from a marketplace (a git repo), not from npm, so this
 * CLI does not "install" anything — it prints the exact commands to add the
 * plugin to Claude Code, and gives `npx` users a useful pointer.
 */

'use strict';

const pkg = require('../package.json');
const isPostinstall = process.argv.includes('--postinstall');

const REPO = 'MarcosNahuel/antigravity-plugin-cc';
const MARKETPLACE = 'marcosnahuel-antigravity';

if (isPostinstall) {
  // Keep postinstall output to a single quiet line; never fail the install.
  console.log(
    `\nantigravity-plugin-cc@${pkg.version} fetched. This is a Claude Code plugin.\n` +
    `Install it into Claude Code with:\n` +
    `  /plugin marketplace add ${REPO}\n` +
    `  /plugin install antigravity@${MARKETPLACE}\n` +
    `Run \`npx ${pkg.name}\` for details.\n`
  );
  process.exit(0);
}

console.log(`
antigravity-plugin-cc  v${pkg.version}
${'-'.repeat(40)}
A Claude Code plugin that wraps Google's Antigravity CLI (agy / Gemini 3.x).
It is NOT a standalone CLI — install it into Claude Code:

  1) Add the marketplace:
       /plugin marketplace add ${REPO}

  2) Install the plugin:
       /plugin install antigravity@${MARKETPLACE}

Then use the slash commands inside Claude Code:
  /agy:research <topic> [--intensity low|medium|high]
  /agy:report <markdown> [--template <id>] [--images native|external|none]
  /agy:ask · /agy:review · /agy:rescue · /agy:scrape
  /agy:doc-to-md · /agy:design-review · /agy:record · /agy:setup

Prerequisite: the Antigravity CLI (agy) on PATH — https://antigravity.google/cli

Docs & issues: https://github.com/${REPO}
`);
process.exit(0);
