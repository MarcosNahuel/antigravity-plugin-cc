import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
const root=new URL('../../../../',import.meta.url);
const plugin=new URL('plugins/antigravity/',root);
const json=async path=>JSON.parse(await readFile(path,'utf8'));

test('Claude, Codex, package and marketplace agree on release version',async()=>{
  const pkg=await json(new URL('package.json',root));
  const claude=await json(new URL('.claude-plugin/plugin.json',plugin));
  const codex=await json(new URL('.codex-plugin/plugin.json',plugin));
  const market=await json(new URL('.claude-plugin/marketplace.json',root));
  assert.equal(claude.name,codex.name);
  for(const version of [claude.version,codex.version,market.metadata.version,market.plugins[0].version])
    assert.equal(version,pkg.version);
  assert.equal(codex.skills,'./skills/');
});
test('every existing command has a current portable entry with valid references',async()=>{
  const commands=(await readdir(new URL('commands/',plugin))).filter(f=>f.endsWith('.md'));
  assert.ok(commands.length>=22);
  const seen=new Set();
  for(const command of commands){
    const skill=await readFile(new URL(`skills/agy-${command.slice(0,-3)}/SKILL.md`,plugin),'utf8');
    const name=skill.match(/^name: (.+)$/m)?.[1];
    assert.ok(name); assert.equal(seen.has(name),false); seen.add(name);
    assert.match(skill,/host-integration\.md/); assert.ok(skill.includes(`../../commands/${command}`));
    assert.doesNotMatch(skill,/^context: fork$/m);
    await readFile(new URL('references/host-integration.md',plugin),'utf8');
  }
  await promisify(execFile)(process.execPath,[fileURLToPath(new URL('bin/generate-codex-skills.mjs',root)),'--check']);
});
