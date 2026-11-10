// Frame compositor: shot selection, crossfades, VHS overlays, OSD, subtitles.
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const main = cv.getContext('2d');
const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
const bufCtx = buf.getContext('2d');
initNoise();

function drawShot(sh, t, ctx) {
  c = ctx; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.fillStyle = '#000'; c.fillRect(0, 0, W, H);
  CUR = sh; c.save(); sh.draw(t - sh.t0, t); c.restore();
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
  if (t < 3.2 && Math.floor(t * 2) % 2 === 0) txt('▶ PLAY', VERT ? 60 : 90, 90, 48, '#f2f2f2', font);
  if (t > 89.3) txt('■ STOP', VERT ? 60 : 90, 90, 48, '#f2f2f2', font);
  if (t < 84) {
    let cur = OSD[0]; OSD.forEach(o => { if (t >= o[0]) cur = o; });
    const [hh, mm] = cur[2].split(':').map(Number); const sec = Math.floor(t - cur[0]); const m2 = mm + Math.floor(sec / 60);
    const tm = `${String(hh).padStart(2, '0')}:${String(m2).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
    txt(cur[1], W - (VERT ? 60 : 90), 76, 40, '#f2f2f2', Object.assign({}, font, { a: 'right' }));
    txt(tm, W - (VERT ? 60 : 90), 126, 40, '#f2f2f2', Object.assign({}, font, { a: 'right' }));
  }
  txt('SP', VERT ? 60 : 90, H - 150, 34, 'rgba(242,242,242,.8)', font);
}

function wrap(s, max = 32) {
  if (s.length <= max) return [s];
  const w = s.split(' '); let best = 1, bd = 1e9;
  for (let i = 1; i < w.length; i++) { const a = w.slice(0, i).join(' ').length, b = w.slice(i).join(' ').length; const d = Math.abs(a - b); if (d < bd) { bd = d; best = i; } }
  return [w.slice(0, best).join(' '), w.slice(best).join(' ')];
}
function wrapW(s, maxw, size) {
  c.font = `800 ${size}px Inter`; const sp = c.measureText(' ').width * 1.9;
  const out = []; let cur = '';
  s.split(' ').forEach(w => { const cand = cur ? cur + ' ' + w : w; const wd = cand.split(' ').reduce((a, k) => a + c.measureText(k).width, 0) + sp * (cand.split(' ').length - 1); if (wd > maxw && cur) { out.push(cur); cur = w; } else cur = cand; });
  if (cur) out.push(cur); return out;
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
  const lines = VERT ? wrapW(s[2], 900, 64) : wrap(s[2]); const size = VERT ? 64 : 54;
  const base = VERT ? H * 0.74 : H - 95, lh = VERT ? 80 : 66;
  lines.forEach((l, i) => richLine(l, base - (lines.length - 1 - i) * lh, size));
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

// Cover / thumbnail image for the video.
window.renderCover = function () {
  c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  const t = 4.0;
  c.save();
  if (VERT) { c.translate(540, 1425); c.scale(2.17, 2.17); c.translate(-960, -560); }
  else { c.translate(1380, 600); c.scale(1.45, 1.45); c.translate(-960, -520); }
  room(t, 'morning'); pillow();
  heroSitBed(t, { expr: 'shock', sweat: true, look: [-6, -4], hl: [-170, -560], hr: [170, -560] });
  sunbeam(t, 0.8);
  c.restore();
  // dark gradient behind the title
  if (VERT) { c.fillStyle = grad(0, 0, 0, 900, [[0, 'rgba(10,8,30,.92)'], [0.75, 'rgba(10,8,30,.55)'], [1, 'rgba(10,8,30,0)']]); c.fillRect(0, 0, W, 900); }
  else { c.fillStyle = grad(0, 0, 1100, 0, [[0, 'rgba(10,8,30,.92)'], [0.7, 'rgba(10,8,30,.6)'], [1, 'rgba(10,8,30,0)']]); c.fillRect(0, 0, 1100, H); }
  const title = (s, x, y, size, col, a = 'center') => { txt(s, x - 7, y, size, 'rgba(255,40,80,.75)', { w: 900, a }); txt(s, x + 7, y, size, 'rgba(40,200,255,.75)', { w: 900, a }); txt(s, x, y, size, col, { w: 900, a, stroke: '#14102a', sw: size * 0.12 }); };
  if (VERT) {
    title('ТЫ ПРОСНУЛСЯ', 540, 300, 118, '#f6efe0');
    title('В 90-Х', 540, 470, 230, '#ffe14d');
    rr(250, 600, 580, 92, 46, '#e8322a'); txt('1995 ГОД', 540, 648, 60, '#fff', { w: 900, ls: 4 });
    push(170, 1500, -0.12); calendar(0, 0, 0.7, '1995', undefined, 'ЯНВАРЬ', t); pop();
  } else {
    title('ТЫ ПРОСНУЛСЯ', 90, 300, 120, '#f6efe0', 'left');
    title('В 90-Х', 90, 500, 250, '#ffe14d', 'left');
    rr(90, 660, 420, 90, 45, '#e8322a'); txt('1995 ГОД', 300, 707, 58, '#fff', { w: 900, ls: 4 });
    calendar(1780, 260, 0.62, '1995', undefined, 'ЯНВАРЬ', t);
  }
  vhs(9.93);
  c = main; c.setTransform(1, 0, 0, 1, 0, 0);
  const font = { w: 700, f: 'DejaVu Sans Mono', a: 'left', stroke: 'rgba(0,0,0,.6)', sw: 6 };
  txt('▶ PLAY', VERT ? 60 : 90, VERT ? 90 : 90, 48, '#f2f2f2', font);
  txt('14.01.1995', W - (VERT ? 60 : 90), VERT ? 76 : 76, 40, '#f2f2f2', Object.assign({}, font, { a: 'right' }));
  return true;
};
