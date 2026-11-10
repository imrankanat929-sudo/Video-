// Usage:
//   node render.mjs frames <out.mp4> <startFrame> <endFrame>   -> encoded video segment
//   node render.mjs stills <outDir> <t1,t2,...>                 -> PNG stills for preview
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const [mode, out, a, b] = process.argv.slice(2);
const FPS = 30;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const errors = [];
page.on('pageerror', e => errors.push(e.message));
await page.goto('file://' + path.join(dir, 'index.html'));
await page.waitForFunction(() => window.ready === true);
await page.evaluate(() => document.fonts.ready);

if (mode === 'stills') {
  fs.mkdirSync(out, { recursive: true });
  for (const t of a.split(',').map(Number)) {
    await page.evaluate(t => renderFrame(t), t);
    await page.screenshot({ path: path.join(out, `t${t.toFixed(2).padStart(6, '0')}.png`) });
  }
} else {
  const start = +a, end = +b;
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'fast', '-crf', '14', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = start; f < end; f++) {
    await page.evaluate(t => renderFrame(t), f / FPS);
    const jpg = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`${path.basename(out)} frame ${f}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
if (errors.length) console.error('PAGE ERRORS:', errors.slice(0, 5));
await browser.close();
