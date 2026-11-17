// Usage: node render.mjs shots [id,id,...]   -> output/shots/<id>.mp4 (each shot its own clip)
//        node render.mjs stills [t]          -> output/stills/<id>.png (mid-frame previews)
//        node render.mjs cover               -> output/cover.png
import { createRequire } from 'module'; import { spawn } from 'child_process'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url); const { chromium } = require('playwright');
const here = path.dirname(fileURLToPath(import.meta.url)); const out = path.join(here, '..', 'output');
const FPS = 30; const mode = process.argv[2] || 'stills'; const only = process.argv[3] ? process.argv[3].split(',') : null;
const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--disable-web-security'] });
async function newPage() { const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } }); await p.goto('file://' + path.join(here, 'index.html')); await p.evaluate(() => window.ready); return p; }
const shots = (await (await newPage()).evaluate(() => SHOTS.map(s => ({ id: s.id, dur: s.dur, start: s.start })))).filter(s => !only || only.includes(s.id));
if (mode === 'cover') { const p = await newPage(); await p.evaluate(() => renderCover()); const d = await p.evaluate(() => grabPng()); fs.writeFileSync(path.join(out, 'cover.png'), Buffer.from(d.split(',')[1], 'base64')); }
else if (mode === 'stills') { fs.mkdirSync(path.join(out, 'stills'), { recursive: true }); const p = await newPage(); const fr = process.argv[4] ? parseFloat(process.argv[4]) : 0.6;
  for (const s of shots) { const t = s.dur * fr; await p.evaluate(([id, t]) => renderShot(id, t), [s.id, t]); const d = await p.evaluate(() => grab(0.85)); fs.writeFileSync(path.join(out, 'stills', `${s.id}.jpg`), Buffer.from(d.split(',')[1], 'base64')); } }
else if (mode === 'shots') { fs.mkdirSync(path.join(out, 'shots'), { recursive: true });
  const queue = [...shots]; const t0 = Date.now();
  async function worker() { const p = await newPage(); while (queue.length) { const s = queue.shift(); const n = Math.round(s.dur * FPS); const file = path.join(out, 'shots', `${s.id}.mp4`);
      const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-frames:v', String(n), '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), file], { stdio: ['pipe', 'inherit', 'inherit'] });
      for (let f = 0; f < n; f++) { const d = await p.evaluate(([id, t]) => { renderShot(id, t); return grab(0.93); }, [s.id, f / FPS]); if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r)); }
      ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log(`${s.id}  ${n} frames  (${((Date.now() - t0) / 1000).toFixed(0)}s)`); } }
  await Promise.all([worker(), worker(), worker()]); }
await browser.close();
