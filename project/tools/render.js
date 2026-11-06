// Render the video: node tools/render.js [lang] [workers] [fromSec] [toSec]
// Frames are drawn in headless Chromium and piped as JPEG into ffmpeg; segments are joined and muxed with the mix.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const serve = require('./server');
const ROOT = path.resolve(__dirname, '..');
const lang = process.argv[2] || 'ru', workers = +process.argv[3] || 3;
const TL = JSON.parse(fs.readFileSync(path.join(ROOT, `config/timeline.${lang}.json`)));
const from = Math.round((+process.argv[4] || 0) * TL.fps);
const to = Math.round((+process.argv[5] || TL.duration) * TL.fps);
const TMP = path.join(ROOT, '..', 'output', `.tmp_${lang}`);
fs.mkdirSync(TMP, { recursive: true });

async function worker(srv, idx, f0, f1) {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('[err]', e.message));
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html?render=1&lang=${lang}`);
  await p.evaluate(() => window.bootDone);
  const out = path.join(TMP, `seg_${String(idx).padStart(2, '0')}.mp4`);
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(TL.fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-tune', 'grain', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    const url = await p.evaluate(f => { window.renderFrame(f); return window.grabFrame(0.95); }, f);
    const buf = Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.log(`w${idx} ${f - f0}/${f1 - f0} ${((Date.now() - t0) / Math.max(1, f - f0)).toFixed(0)}ms/f`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  return out;
}
(async () => {
  const srv = await serve();
  const n = to - from, step = Math.ceil(n / workers), jobs = [];
  for (let i = 0; i < workers; i++) { const a = from + i * step, z = Math.min(to, a + step); if (a < z) jobs.push(worker(srv, i, a, z)); }
  const segs = await Promise.all(jobs);
  srv.close();
  const list = path.join(TMP, 'list.txt');
  fs.writeFileSync(list, segs.map(s => `file '${s}'`).join('\n'));
  const final = path.join(ROOT, '..', 'output', from === 0 && to === Math.round(TL.duration * TL.fps) ? `WhatIf_EP01_${lang}.mp4` : `preview_${lang}_${from}_${to}.mp4`);
  execFileSync('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list,
    '-ss', String(from / TL.fps), '-t', String(n / TL.fps), '-i', path.join(ROOT, `assets/audio/mix_${lang}.wav`),
    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', '-shortest', final], { stdio: 'inherit' });
  console.log('done', final);
})();
