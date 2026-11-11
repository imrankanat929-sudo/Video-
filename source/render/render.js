// usage: node render.js <lang> <f0> <f1> <out.mp4|dir-for-png> [png|vert|vpng]
//   vert / vpng = 9:16 (1080x1920) version
const L = require('./lib');
const SH = require('./shots');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const { W, H, clamp, prog, lerp, easeS } = L;
const [lang, f0s, f1s, out, mode] = process.argv.slice(2);
const VERT = mode === 'vert' || mode === 'vpng', PNG = mode === 'png' || mode === 'vpng';
const OW = VERT ? 1080 : W, OH = VERT ? 1920 : H, SC = OH / H;
const TL = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'timeline.json')))[lang];
const FPS = 30, DUR = 90;
SH.build(); SH.setV(VERT);
const A = SH.A;
const shots = TL.shots.map(([name, st], i) => ({ name, st, en: i + 1 < TL.shots.length ? TL.shots[i + 1][1] : DUR }));
const TRANS = { asia: 'black' };

const main = L.canvas(OW, OH), ctx = main.getContext('2d');
const tmp = L.canvas(OW, OH), tctx = tmp.getContext('2d');
let vig = A.vig;
if (VERT) { vig = L.canvas(OW, OH); const x = vig.getContext('2d'); const g = x.createRadialGradient(OW / 2, OH / 2, OW * 0.45, OW / 2, OH / 2, OH * 0.62); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.75)'); x.fillStyle = g; x.fillRect(0, 0, OW, OH); }

// horizontal focus point (in 16:9 coordinates) for the 9:16 crop of each shot
function cropX(name, lt, ev) {
  switch (name) {
    case 'window': return 900;
    case 'asia': { const m = ev.asiaMap; return lt < m ? lerp(1380, 1000, lt / m) : lerp(1000, 960, easeS(prog(lt, m, m + 0.8))); }
    case 'trade': { const m = ev.tradeMap; return lt < m ? lerp(1100, 1040, lt / m) : lerp(1040, 960, easeS(prog(lt, m, m + 0.8))); }
    case 'europe': {
      const c = ev.europeCity, d = ev.europeDoc;
      if (lt < c) return lerp(520, 1000, easeS(prog(lt, 0, c)));
      if (lt < d) return lerp(1000, 430 + 48 * (lt - c), easeS(prog(lt, c, c + 0.8)));
      return lerp(430 + 48 * (d - c), 950, easeS(prog(lt, d, d + 0.8)));
    }
    case 'after': return 1000;
    default: return 960;
  }
}

function drawShot(c, s, t) {
  const ev = {}; for (const k in TL.ev) ev[k] = TL.ev[k] - s.st;
  c.save();
  if (VERT) c.setTransform(SC, 0, 0, SC, OW / 2 - cropX(s.name, t - s.st, ev) * SC, 0); else c.setTransform(1, 0, 0, 1, 0, 0);
  c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.fillStyle = '#000'; c.fillRect(-W, 0, W * 3, H);
  SH.shots[s.name](c, t - s.st, s.en - s.st, ev, lang);
  c.restore();
}

function wrap(c, text, maxW) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const tst = cur ? cur + ' ' + w : w; if (c.measureText(tst).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tst; }
  if (cur) lines.push(cur);
  if (lines.length >= 2 && lines[lines.length - 1].split(' ').length === 1) { const a = lines[lines.length - 2].split(' '); if (a.length > 1) { lines[lines.length - 1] = a.pop() + ' ' + lines[lines.length - 1]; lines[lines.length - 2] = a.join(' '); } }
  return lines;
}
function subtitles(c, t) {
  const s = TL.subs.find(x => t >= x[0] && t < x[1]); if (!s) return;
  const a = clamp(prog(t, s[0], s[0] + 0.15)) * (1 - prog(t, s[1] - 0.12, s[1]));
  const fsz = VERT ? 52 : 44, lh = VERT ? 68 : 56, maxW = VERT ? 920 : 1500, yb = VERT ? 1500 : 1000;
  c.save(); c.globalAlpha = a; c.font = `${fsz}px PTSansBold`; c.letterSpacing = '0px';
  const lines = wrap(c, s[2], maxW), y0 = yb - (lines.length - 1) * lh;
  const wmax = Math.max(...lines.map(l => c.measureText(l).width));
  c.fillStyle = 'rgba(8,7,6,0.55)'; L.rrect(c, OW / 2 - wmax / 2 - 26, y0 - lh * 0.68, wmax + 52, lines.length * lh + 20, 10); c.fill();
  c.textAlign = 'center'; c.textBaseline = 'middle';
  lines.forEach((l, i) => { c.fillStyle = 'rgba(0,0,0,0.6)'; c.fillText(l, OW / 2 + 2, y0 + i * lh + 2); c.fillStyle = '#f2ebdd'; c.fillText(l, OW / 2, y0 + i * lh); });
  c.restore();
}

function frame(t) {
  SH.OV.length = 0;
  let i = shots.findIndex(s => t >= s.st && t < s.en); if (i < 0) i = shots.length - 1;
  const s = shots[i], td = TRANS[s.name] === 'black' ? 1.0 : 0.8;
  if (i > 0 && t - s.st < td && TRANS[s.name] !== 'black') {
    const a = L.easeS((t - s.st) / td);
    SH.setOVA(1 - a); drawShot(ctx, shots[i - 1], t); SH.setOVA(a); drawShot(tctx, s, t);
    ctx.save(); ctx.globalAlpha = a; ctx.drawImage(tmp, 0, 0); ctx.restore();
  } else {
    SH.setOVA(1); drawShot(ctx, s, t);
    if (TRANS[s.name] === 'black' && t - s.st < td) { ctx.fillStyle = `rgba(0,0,0,${1 - L.easeS((t - s.st) / td)})`; ctx.fillRect(0, 0, OW, OH); }
  }
  ctx.save();
  ctx.drawImage(vig, 0, 0);
  ctx.globalCompositeOperation = 'soft-light'; ctx.fillStyle = 'rgba(120,90,50,0.18)'; ctx.fillRect(0, 0, OW, OH);
  ctx.globalCompositeOperation = 'source-over';
  const fl = 0.025 * (Math.sin(t * 23) * Math.sin(t * 7.7)); if (fl > 0) { ctx.fillStyle = `rgba(0,0,0,${fl})`; ctx.fillRect(0, 0, OW, OH); }
  ctx.restore();
  for (const f of SH.OV) f(ctx);
  subtitles(ctx, t);
  const fin = 1 - prog(t, 0, 0.8); if (fin > 0) { ctx.fillStyle = `rgba(0,0,0,${fin})`; ctx.fillRect(0, 0, OW, OH); }
}

(async () => {
  const f0 = +f0s, f1 = +f1s;
  if (PNG) {
    if (f0s.includes(',')) { for (const ts of f0s.split(',')) { const tt = +ts; frame(tt); fs.writeFileSync(path.join(out, `${VERT ? 'v' : ''}${lang}_${tt.toFixed(1)}.png`), main.encodeSync('png')); } return; }
    for (let f = f0; f < f1; f++) { frame(f / FPS); fs.writeFileSync(path.join(out, `${lang}_${(f / FPS).toFixed(1)}.png`), main.encodeSync('png')); }
    return;
  }
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${OW}x${OH}`, '-r', String(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-tune', 'animation', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    frame(f / FPS);
    const buf = ctx.getImageData(0, 0, OW, OH).data;
    if (!ff.stdin.write(Buffer.from(buf.buffer, buf.byteOffset, buf.byteLength))) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 150 === 0) console.error(`${lang} ${f}/${f1} ${((Date.now() - t0) / (f - f0 + 1)).toFixed(0)}ms/f`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
})();
