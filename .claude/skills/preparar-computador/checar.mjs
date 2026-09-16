#!/usr/bin/env node
// Diagnóstico somente leitura do computador para editar vídeo com IA.
// Uso: node checar.mjs   (rode na raiz da pasta do kit)
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const win = process.platform === 'win32';
const run = (cmd, args) => {
  // npm é um .cmd no Windows e só roda via shell; o resto roda direto (o shell estragaria as aspas do python -c)
  const r = spawnSync(cmd, args, {encoding: 'utf8', shell: win && cmd === 'npm'});
  if (r.error || r.status !== 0) return null;
  return (r.stdout || r.stderr || '').trim().split('\n')[0];
};

const venvPy = win ? path.join('.venv', 'Scripts', 'python.exe') : path.join('.venv', 'bin', 'python');
// No Windows, "python3" costuma ser o atalho da Microsoft Store, que não é Python:
// só vale o comando que consegue executar código de verdade.
const candidatos = win ? ['python', 'py', 'python3'] : ['python3', 'python'];
const python = fs.existsSync(venvPy) ? venvPy
  : candidatos.find(p => run(p, ['-c', 'import sys; print(sys.executable)'])) || null;
const pyMod = mod => python && run(python, ['-c', `import ${mod}; print(${mod}.__version__)`]);

const itens = [
  ['Node.js', run('node', ['--version']), true],
  ['npm', run('npm', ['--version']), true],
  ['FFmpeg', run('ffmpeg', ['-version']), true],
  ['ffprobe', run('ffprobe', ['-version']), true],
  ['Python', python && run(python, ['--version']), true],
  ['  ambiente .venv', fs.existsSync(venvPy) ? 'sim' : null, false],
  ['  faster-whisper', pyMod('faster_whisper'), true],
  ['  NumPy (som)', pyMod('numpy'), false],
  ['GPU NVIDIA', run('nvidia-smi', ['--query-gpu=name', '--format=csv,noheader']), false],
];

console.log(`Sistema: ${os.type()} ${os.release()} (${process.arch})\n`);
let faltam = 0;
for (const [nome, versao, obrigatorio] of itens) {
  const marca = (versao ? 'OK' : obrigatorio ? 'FALTA' : 'opcional').padEnd(9);
  if (!versao && obrigatorio) faltam++;
  console.log(`${marca}${nome.padEnd(18)} ${versao || ''}`);
}

console.log('\nSkills instaladas nesta pasta:');
for (const base of ['.claude/skills', '.agents/skills']) {
  const nomes = fs.existsSync(base) ? fs.readdirSync(base).filter(n => fs.existsSync(path.join(base, n, 'SKILL.md'))) : [];
  console.log(`  ${base.padEnd(16)} ${nomes.length ? nomes.join(', ') : '(nenhuma)'}`);
}
const todas = ['.claude/skills', '.agents/skills'].flatMap(b => fs.existsSync(b) ? fs.readdirSync(b) : []);
if (!todas.some(n => /hyperframes|remotion/i.test(n))) {
  console.log('\n  Nenhuma skill de motor (HyperFrames/Remotion) encontrada: veja o passo 3 do SKILL.md.');
  console.log('  Se ela instalou com outro nome, confira a lista acima.');
}

console.log(faltam ? `\n${faltam} item(ns) obrigatório(s) faltando.` : '\nTudo o que é obrigatório está instalado.');
