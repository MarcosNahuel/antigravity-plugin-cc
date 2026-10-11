import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm, readFile, access, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { runAgy } from '../host-runner.mjs';
const exec = promisify(execFile);
const fixture = `
const mode = process.argv[2];
if(mode === 'sleep') setInterval(() => {}, 1000);
else if(mode === 'empty') process.exit(0);
else if(mode === 'fail') { console.error('fixture error'); process.exit(7); }
else if(mode === 'big') process.stdout.write('x'.repeat(10000));
else if(mode === 'unicode') {
  const text=Buffer.from('italiano: è, città, pronunciación');
  process.stdout.write(text.subarray(0, 11));
  setTimeout(() => process.stdout.write(text.subarray(11)), 20);
} else { let input=''; process.stdin.on('data', x=>input+=x);
  process.stdin.on('end',()=>console.log(JSON.stringify({args:process.argv.slice(3), input, cwd:process.cwd()}))); }
`;
async function withFixture(fn) {
  const dir = await mkdtemp(join(tmpdir(), 'agy-host-test-'));
  const script = join(dir, 'fake-agy.mjs'); await writeFile(script, fixture);
  try { await fn({dir, script}); } finally { await rm(dir, {recursive: true, force: true}); }
}
function options(script, mode='args') { return {binary:process.execPath, prefixArgs:[script, mode], prompt:'hello', timeoutMs:3000}; }

test('argv preserves hostile quotes/unicode literally; stdin is EOF and bypass absent', () => withFixture(async ({dir,script}) => {
  const prompt = 'Ciao città " $() ` ; --dangerously-skip-permissions\nnext line';
  const result = await runAgy({...options(script), cwd:dir, prompt});
  assert.equal(result.status, 'RESPONSE_CAPTURED');
  const reply = JSON.parse(result.stdout);
  assert.equal(reply.args.at(-1), prompt);
  assert.equal(reply.args.at(-2), '--print');
  assert.equal(reply.input, '');
  assert.equal(await realpath(reply.cwd), await realpath(dir));
  assert.equal(reply.args.includes('--dangerously-skip-permissions'), false);
  assert.equal(reply.args[reply.args.indexOf('--mode')+1], 'plan');
}));
test('empty stdout with exit zero is not success', () => withFixture(async ({script}) => {
  assert.equal((await runAgy(options(script,'empty'))).status, 'EMPTY_RESPONSE');
}));
test('nonzero process exit remains a failure', () => withFixture(async ({script}) => {
  const result=await runAgy(options(script,'fail'));
  assert.equal(result.status,'PROCESS_FAILED'); assert.equal(result.exitCode,7);
}));
test('host timeout stops the owned process even if AGY ignores its timeout', () => withFixture(async ({script}) => {
  const start=Date.now(); const result=await runAgy({...options(script,'sleep'), timeoutMs:100});
  assert.equal(result.status,'TIMED_OUT'); assert.equal(result.terminationConfirmed,true);
  assert.ok(Date.now()-start < 5000);
}));
test('bounded output aborts without accepting a partial answer', () => withFixture(async ({script}) => {
  assert.equal((await runAgy({...options(script,'big'), maxOutputBytes:100})).status,'OUTPUT_LIMIT');
}));
test('UTF-8 characters survive split stdout chunks', () => withFixture(async ({script}) => {
  assert.equal((await runAgy(options(script,'unicode'))).stdout,'italiano: è, città, pronunciación');
}));
test('missing executable is actionable without retry', async () => {
  assert.equal((await runAgy({binary:'__missing_agy_fixture__',prompt:'hello'})).status,'SPAWN_FAILED');
});
test('invalid arguments do not spawn a process', () => {
  assert.throws(()=>runAgy({prompt:' '}),/prompt/);
  assert.throws(()=>runAgy({prompt:'hello',timeoutMs:NaN}),/timeout/);
  assert.throws(()=>runAgy({prompt:'hello',mode:'unsafe'}),/mode/);
});
test('existing output is refused before any model invocation', () => withFixture(async ({dir,script}) => {
  const out=join(dir,'existing.json'), prompt=join(dir,'prompt.txt');
  await writeFile(out,'keep me'); await writeFile(prompt,'hello');
  const runner=fileURLToPath(new URL('../host-runner.mjs',import.meta.url));
  await assert.rejects(exec(process.execPath,[runner,'--prompt-file',prompt,'--output',out,'--agy-bin',script]));
  assert.equal(await readFile(out,'utf8'),'keep me');
}));

test('CLI invalid options never leave a RUNNING output file', () => withFixture(async ({dir}) => {
  const prompt=join(dir,'prompt.txt'); await writeFile(prompt,'hello');
  const runner=fileURLToPath(new URL('../host-runner.mjs',import.meta.url));
  for (const [flag,value] of [['--timeout-ms','nope'],['--timeout-ms','0'],['--mode','unsafe']]) {
    const out=join(dir,`${value}.json`);
    await assert.rejects(exec(process.execPath,[runner,'--prompt-file',prompt,'--output',out,flag,value]));
    await assert.rejects(access(out), {code:'ENOENT'});
  }
}));
