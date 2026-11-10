// Frame compositor: shot selection, crossfades, VHS overlays, OSD, subtitles.
const cv = document.getElementById('c');
const main = cv.getContext('2d');
const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
const bufCtx = buf.getContext('2d');
initNoise();

function drawShot(sh, t, ctx) {
  c = ctx; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.fillStyle = '#000'; c.fillRect(0, 0, W, H);
  c.save(); sh.draw(t - sh.t0, t); c.restore();
}

function glitchAt(t) {
  let g = 0; GLITCH.forEach(([gt, a]) => { g += a * Math.exp(-Math.pow((t - gt) / 0.13, 2)); });
  const f = Math.floor(t * 30); if (hash(f * 3 + 1) < 0.012) g += 0.25;
  return g;
}

function vhs(t) {
  const f = Math.floor(t * 30); const r = rng(f * 7 + 3);
  const g = glitchAt(t);
  c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  if (g > 0.03) {
    const n = 3 + Math.floor(g * 12);
    for (let i = 0; i < n; i++) { const y = r() * H, h = 6 + r() * 70 * g, dx = (r() - 0.5) * 180 * g; c.drawImage(cv, 0, y, W, h, dx, y, W, h); }
    for (let i = 0; i < 1 + g * 3; i++) { const y = r() * H; staticFill(0, y, W, 20 + r() * 90 * g, t + i, Math.min(0.7, g * 0.6)); }
    alpha(Math.min(0.35, g * 0.25), () => { rect(0, r() * H, W, 8 + r() * 30, r() < 0.5 ? '#ff2a8a' : '#2affe0'); });
    if (g > 0.8) { const dy = (r() - 0.5) * 40 * g; c.drawImage(cv, 0, 0, W, H, 0, dy, W, H); }
  }
  // tracking line rolling down
  const ty = ((t * 70) % (H + 600)) - 300;
  staticFill(0, ty, W, 5, t, 0.12);
  // head-switching noise at bottom
  c.drawImage(cv, 0, H - 16, W, 16, 12 + r() * 16, H - 16, W, 16); staticFill(0, H - 12, W, 12, t, 0.35);
  // scanlines
  alpha(0.08, () => { c.fillStyle = '#000'; for (let y = 0; y < H; y += 4) c.fillRect(0, y, W, 2); });
}

function osd(t) {
  c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  const font = { w: 700, f: 'DejaVu Sans Mono', a: 'left', stroke: 'rgba(0,0,0,.6)', sw: 6 };
  if (t < 3.2 && Math.floor(t * 2) % 2 === 0) txt('▶ PLAY', 90, 90, 48, '#f2f2f2', font);
  if (t > 89.3) txt('■ STOP', 90, 90, 48, '#f2f2f2', font);
  if (t < 84) {
    let cur = OSD[0]; OSD.forEach(o => { if (t >= o[0]) cur = o; });
    const [hh, mm] = cur[2].split(':').map(Number); const sec = Math.floor(t - cur[0]); const m2 = mm + Math.floor(sec / 60);
    const tm = `${String(hh).padStart(2, '0')}:${String(m2).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
    txt(cur[1], W - 90, 76, 40, '#f2f2f2', Object.assign({}, font, { a: 'right' }));
    txt(tm, W - 90, 126, 40, '#f2f2f2', Object.assign({}, font, { a: 'right' }));
  }
  txt('SP', 90, H - 150, 34, 'rgba(242,242,242,.8)', font);
}

function wrap(s, max = 32) {
  if (s.length <= max) return [s];
  const w = s.split(' '); let best = 1, bd = 1e9;
  for (let i = 1; i < w.length; i++) { const a = w.slice(0, i).join(' ').length, b = w.slice(i).join(' ').length; const d = Math.abs(a - b); if (d < bd) { bd = d; best = i; } }
  return [w.slice(0, best).join(' '), w.slice(best).join(' ')];
}
function richLine(s, y, size) {
  c.font = `800 ${size}px Inter`; c.letterSpacing = '0px';
  const toks = s.split(' '); const sp = c.measureText(' ').width * 1.9; const ws = toks.map(k => c.measureText(k).width);
  let x = W / 2 - (ws.reduce((a, b) => a + b, 0) + sp * (toks.length - 1)) / 2;
  toks.forEach((k, i) => { const hl = /1995|2005|90-х/.test(k); txt(k, x, y, size, hl ? '#ffd23a' : '#ffffff', { w: 800, a: 'left', stroke: '#000', sw: 11 }); x += ws[i] + sp; });
}
function subs(t) {
  c = main; c.setTransform(1, 0, 0, 1, 0, 0);
  const s = SUBS.find(x => t >= x[0] && t < x[1]); if (!s) return;
  const a = cl((t - s[0]) / 0.12) * cl((s[1] - t) / 0.1);
  c.globalAlpha = a;
  const lines = wrap(s[2]); const size = 54;
  lines.forEach((l, i) => richLine(l, H - 95 - (lines.length - 1 - i) * 66, size));
  c.globalAlpha = 1;
}

window.renderFrame = function (t) {
  let i = S.findIndex(s => t >= s.t0 && t < s.t1); if (i < 0) i = S.length - 1;
  const sh = S[i];
  drawShot(sh, t, main);
  const nx = S[i + 1];
  if (nx && t > sh.t1 - nx.fade) {
    drawShot(nx, t, bufCtx);
    c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = eio((t - (sh.t1 - nx.fade)) / nx.fade); c.drawImage(buf, 0, 0); c.globalAlpha = 1;
  }
  vhs(t);
  subs(t);
  osd(t);
  return true;
};
window.ready = true;
