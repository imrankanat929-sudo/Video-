// usage: node render.js <lang> <f0> <f1> <out.mp4|dir-for-png> [png]
const L = require('./lib');
const SH = require('./shots');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const { W, H, clamp, prog } = L;
const [lang, f0s, f1s, out, mode] = process.argv.slice(2);
const TL = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'timeline.json')))[lang];
const FPS = 30, DUR = 90;
SH.build();
const A = SH.A;
const shots = TL.shots.map(([name, st], i) => ({ name, st, en: i + 1 < TL.shots.length ? TL.shots[i + 1][1] : DUR }));
const TRANS = { asia: 'black' };

const main = L.canvas(W, H), ctx = main.getContext('2d');
const tmp = L.canvas(W, H), tctx = tmp.getContext('2d');

function drawShot(c, s, t) {
  const ev = {}; for (const k in TL.ev) ev[k] = TL.ev[k] - s.st;
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.fillStyle = '#000'; c.fillRect(0, 0, W, H);
  SH.shots[s.name](c, t - s.st, s.en - s.st, ev, lang);
  c.restore();
}

function wrap(c, text, maxW) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const tst = cur ? cur + ' ' + w : w; if (c.measureText(tst).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tst; }
  if (cur) lines.push(cur);
  if (lines.length === 2 && lines[1].split(' ').length === 1) { // avoid orphan
    const a = lines[0].split(' '); lines[1] = a.pop() + ' ' + lines[1]; lines[0] = a.join(' ');
  }
  return lines;
}
function subtitles(c, t) {
  const s = TL.subs.find(x => t >= x[0] && t < x[1]); if (!s) return;
  const a = clamp(prog(t, s[0], s[0] + 0.15)) * (1 - prog(t, s[1] - 0.12, s[1]));
  c.save(); c.globalAlpha = a; c.font = '44px PTSansBold'; c.letterSpacing = '0px';
  const lines = wrap(c, s[2], 1500), lh = 56, y0 = 1000 - (lines.length - 1) * lh;
  const wmax = Math.max(...lines.map(l => c.measureText(l).width));
  c.fillStyle = 'rgba(8,7,6,0.55)'; L.rrect(c, W / 2 - wmax / 2 - 26, y0 - 38, wmax + 52, lines.length * lh + 20, 10); c.fill();
  c.textAlign = 'center'; c.textBaseline = 'middle';
  lines.forEach((l, i) => { c.fillStyle = 'rgba(0,0,0,0.6)'; c.fillText(l, W / 2 + 2, y0 + i * lh + 2); c.fillStyle = '#f2ebdd'; c.fillText(l, W / 2, y0 + i * lh); });
  c.restore();
}

function frame(t) {
  let i = shots.findIndex(s => t >= s.st && t < s.en); if (i < 0) i = shots.length - 1;
  const s = shots[i], td = TRANS[s.name] === 'black' ? 1.0 : 0.8;
  if (i > 0 && t - s.st < td && TRANS[s.name] !== 'black') {
    drawShot(ctx, shots[i - 1], t); drawShot(tctx, s, t);
    ctx.save(); ctx.globalAlpha = L.easeS((t - s.st) / td); ctx.drawImage(tmp, 0, 0); ctx.restore();
  } else {
    drawShot(ctx, s, t);
    if (TRANS[s.name] === 'black' && t - s.st < td) { ctx.fillStyle = `rgba(0,0,0,${1 - L.easeS((t - s.st) / td)})`; ctx.fillRect(0, 0, W, H); }
  }
  ctx.save();
  ctx.drawImage(A.vig, 0, 0);
  // subtle warm grade + flicker
  ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = 'rgba(120,90,50,0.18)'; ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = 'source-over';
  const fl = 0.025 * (Math.sin(t * 23) * Math.sin(t * 7.7)); if (fl > 0) { ctx.fillStyle = `rgba(0,0,0,${fl})`; ctx.fillRect(0, 0, W, H); }
  ctx.restore();
  subtitles(ctx, t);
  const fin = 1 - prog(t, 0, 0.8); if (fin > 0) { ctx.fillStyle = `rgba(0,0,0,${fin})`; ctx.fillRect(0, 0, W, H); }
}

(async () => {
  const f0 = +f0s, f1 = +f1s;
  if (mode === 'png') {
    if (f0s.includes(',')) { for (const ts of f0s.split(',')) { const tt = +ts; frame(tt); fs.writeFileSync(path.join(out, `${lang}_${tt.toFixed(1)}.png`), main.encodeSync('png')); } return; }
    for (let f = f0; f < f1; f++) { frame(f / FPS); fs.writeFileSync(path.join(out, `${lang}_${(f / FPS).toFixed(1)}.png`), main.encodeSync('png')); }
    return;
  }
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-tune', 'animation', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    frame(f / FPS);
    const buf = ctx.getImageData(0, 0, W, H).data;
    if (!ff.stdin.write(Buffer.from(buf.buffer, buf.byteOffset, buf.byteLength))) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.error(`${lang} ${f}/${f1} ${((Date.now() - t0) / (f - f0 + 1)).toFixed(0)}ms/f`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
})();
