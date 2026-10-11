#!/usr/bin/env node
// Development-only export. commands/*.md remains the single workflow source.
import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../plugins/antigravity');
const check = process.argv.includes('--check');
let failed = false;
for (const file of (await readdir(resolve(root, 'commands'))).filter(f => f.endsWith('.md')).sort()) {
  const command = file.slice(0, -3);
  const source = await readFile(resolve(root, 'commands', file), 'utf8');
  const match = source.match(/^description:\s*(.+)$/m);
  if (!match) throw new Error(`Missing command description: ${file}`);
  const description = `Use Antigravity for ${command}. ${match[1].slice(0, 180)}`;
  const content = `---\nname: agy-${command}\ndescription: ${JSON.stringify(description)}\n---\n\n# Antigravity: ${command}\n\nRead [host integration](../../references/host-integration.md), then the shared\n[${command} workflow](../../commands/${file}). Follow that workflow using the current\nhost's tools and the host integration contract. On Codex execute routing directly;\non Claude the existing slash command and subagent remain available.\n\nUse the actual loaded plugin root for scripts and references. Do not require\nClaude-only Agent/Workflow APIs, assume authentication, bypass permissions, or\nclaim success from installation alone. Keep the user's current scope.\n`;
  const path = resolve(root, 'skills', `agy-${command}`, 'SKILL.md');
  if (check) {
    let actual; try { actual = await readFile(path, 'utf8'); } catch {}
    if (actual !== content) { console.error(`Outdated export: ${command}`); failed = true; }
  } else {
    await mkdir(dirname(path), { recursive: true }); await writeFile(path, content);
  }
}
if (failed) process.exitCode = 1;
