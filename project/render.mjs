// Renders project/render.html frame-by-frame with Playwright, pipes PNGs to ffmpeg.
// usage: node render.mjs --out out.mp4 [--from 0] [--to 105] [--fps 30] [--workers 4] [--lang ru] [--stills 1,2,3 --dir dir]
import { spawn, execSync } from 'child_process';
import { createRequire } from 'module';
const req = createRequire(import.meta.url);
let pw; try { pw = req('playwright'); } catch { pw = req(execSync('npm root -g').toString().trim() + '/playwright'); }
const { chromium } = pw;
import fs from 'fs'; import path from 'path'; import url from 'url';
const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, arr) => (x.startsWith('--') ? a.concat([[x.slice(2), arr[i + 1]]]) : a), []));
const here = path.dirname(url.fileURLToPath(import.meta.url));
const fps = +(args.fps || 30), from = +(args.from || 0), to = +(args.to || 105), workers = +(args.workers || 4), lang = args.lang || 'ru';
const page_url = 'file://' + path.join(here, 'render.html') + '?lang=' + lang + (args.thumb ? '&thumb=' + args.thumb : '');
const browser = await chromium.launch({ args: ['--disable-gpu-vsync'] });
async function newPage() { const p = await browser.newPage({ viewport: { width: 1920, height: 1080 } }); p.on('pageerror', e => console.error('PAGEERROR', e.message)); p.on('console', m => m.type() === 'error' && console.error('CONSOLE', m.text())); await p.goto(page_url); await p.evaluate(() => window.ready); return p; }
const grab = (p, t) => p.evaluate(t => { window.frame(t); return document.getElementById('c').toDataURL('image/png'); }, t);
if (args.stills) {
  const p = await newPage(); fs.mkdirSync(args.dir, { recursive: true });
  for (const t of args.stills.split(',').map(Number)) { const d = await grab(p, t); fs.writeFileSync(path.join(args.dir, `still_${t.toFixed(2)}.png`), Buffer.from(d.split(',')[1], 'base64')); }
  await browser.close(); process.exit(0);
}
const n = Math.round((to - from) * fps);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-tune', 'grain', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', args.out], { stdio: ['pipe', 'inherit', 'inherit'] });
const pages = await Promise.all(Array.from({ length: workers }, newPage));
const buf = new Map(); let next = 0, issued = 0; const t0 = Date.now();
async function flush() { while (buf.has(next)) { const b = buf.get(next); buf.delete(next); if (!ff.stdin.write(b)) await new Promise(r => ff.stdin.once('drain', r)); next++; if (next % 150 === 0) console.log(`frame ${next}/${n} ${((Date.now() - t0) / 1000).toFixed(0)}s`); } }
await Promise.all(pages.map(async p => {
  while (true) { const i = issued++; if (i >= n) break;
    while (i - next > 120) await new Promise(r => setTimeout(r, 20));
    const d = await grab(p, from + i / fps); buf.set(i, Buffer.from(d.split(',')[1], 'base64')); await flush(); }
}));
await flush(); ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close();
console.log('done', args.out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
