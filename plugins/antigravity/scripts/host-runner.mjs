#!/usr/bin/env node
// Optional, dependency-free runner for hosts without Claude's Bash/fork tools.
import { spawn } from 'node:child_process';
import { readFile, open } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

export function runAgy({ binary = process.env.AGY_BIN || 'agy', prefixArgs = [], prompt,
  cwd = process.cwd(), timeoutMs = 60000, mode = 'plan', maxOutputBytes = 4 * 1024 * 1024 }) {
  if (!prompt?.trim()) throw new Error('A non-empty prompt is required');
  if (!Number.isFinite(timeoutMs) || timeoutMs < 1) throw new Error('Invalid timeout');
  if (!['plan', 'accept-edits'].includes(mode)) throw new Error('Invalid mode');
  const args = [...prefixArgs, '--mode', mode, '--disable-slash-commands', '--output-format', 'json',
    '--print-timeout', `${Math.ceil(timeoutMs / 1000)}s`, '--print', prompt];
  return new Promise((fulfill) => {
    const child = spawn(binary, args, { cwd, shell: false, windowsHide: true,
      detached: process.platform !== 'win32', stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '', stderr = '', size = 0, reason, settled = false, stopDeadline;
    const finish = (code, signal, error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      clearTimeout(stopDeadline);
      const status = reason || (error ? 'SPAWN_FAILED' : code !== 0 ? 'PROCESS_FAILED'
        : stdout.trim() ? 'RESPONSE_CAPTURED' : 'EMPTY_RESPONSE');
      fulfill({ status, exitCode: code, signal, stdout, stderr, error: error?.message,
        pid: child.pid, mode, timeoutMs, terminationConfirmed: reason !== 'STOP_UNCONFIRMED' });
    };
    const stop = () => {
      if (!child.pid) return;
      stopDeadline ||= setTimeout(() => {
        reason = 'STOP_UNCONFIRMED';
        finish(null, null);
        child.stdout.destroy(); child.stderr.destroy(); child.unref();
      }, 10000);
      if (process.platform === 'win32') {
        // Only the process tree launched by this invocation; never kill by image name.
        const killer = spawn('taskkill.exe', ['/PID', String(child.pid), '/T', '/F'],
          { shell: false, windowsHide: true, stdio: 'ignore' });
        killer.on('error', () => child.kill());
      } else {
        try { process.kill(-child.pid, 'SIGKILL'); } catch { child.kill('SIGKILL'); }
      }
    };
    const timer = setTimeout(() => { reason = 'TIMED_OUT'; stop(); }, timeoutMs);
    child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
    child.stdout.on('data', chunk => {
      size += Buffer.byteLength(chunk);
      if (size > maxOutputBytes) { reason ||= 'OUTPUT_LIMIT'; stop(); return; }
      stdout += chunk;
    });
    child.stderr.on('data', chunk => {
      size += Buffer.byteLength(chunk);
      if (size > maxOutputBytes) { reason ||= 'OUTPUT_LIMIT'; stop(); return; }
      stderr += chunk;
    });
    child.once('error', error => finish(null, null, error));
    child.once('close', (code, signal) => finish(code, signal));
  });
}

async function main(argv) {
  if (argv.includes('--help')) {
    console.log('host-runner.mjs --prompt-file FILE [--cwd DIR] [--timeout-ms N] [--mode plan|accept-edits] [--output FILE] [--agy-bin FILE]\nDefault mode: plan. No permission bypass or automatic retries. Output files must be new.');
    return;
  }
  const options = {};
  const allowed = new Set(['--prompt-file', '--cwd', '--timeout-ms', '--mode', '--output', '--agy-bin']);
  for (let i = 0; i < argv.length; i += 2) {
    if (!allowed.has(argv[i]) || !argv[i + 1] || options[argv[i]]) throw new Error('Invalid arguments');
    options[argv[i]] = argv[i + 1];
  }
  if (!options['--prompt-file']) throw new Error('--prompt-file is required');
  const prompt = await readFile(options['--prompt-file'], 'utf8');
  const timeoutMs = Number(options['--timeout-ms'] || 60000);
  const mode = options['--mode'] || 'plan';
  if (!prompt.trim()) throw new Error('A non-empty prompt is required');
  if (!Number.isFinite(timeoutMs) || timeoutMs < 1) throw new Error('Invalid timeout');
  if (!['plan', 'accept-edits'].includes(mode)) throw new Error('Invalid mode');
  // Reserve the destination before starting a model call: an existing result must not trigger a retry.
  const output = options['--output'] ? await open(options['--output'], 'wx', 0o600) : null;
  try {
  if (output) await output.writeFile('{"status":"RUNNING"}\n');
  const result = await runAgy({ prompt,
    cwd: options['--cwd'] ? resolve(options['--cwd']) : process.cwd(),
    binary: options['--agy-bin'] || process.env.AGY_BIN || 'agy',
    timeoutMs, mode });
  const json = JSON.stringify(result, null, 2) + '\n';
  if (output) { await output.truncate(0); await output.write(json, 0, 'utf8'); }
  else process.stdout.write(json);
  process.exitCode = result.status === 'RESPONSE_CAPTURED' ? 0 : 1;
  } finally { await output?.close(); }
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).catch(error => { console.error(error.message); process.exitCode = 1; });
}
