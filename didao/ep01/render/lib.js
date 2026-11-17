// DIDAO — shared drawing library (2D flat cartoon, neon "Vice" city mood)
// Everything is deterministic: frame(t) always draws the same picture.
const W = 1920, H = 1080;

const C = {
  skin: '#d6a77a', skinSh: '#b98a60', hair: '#0e0e11', hairHi: '#26262c',
  sweater: '#1f2026', sweaterSh: '#16171b', pants: '#131317', shoe: '#c4c4c8', shoeSh: '#8d8d93',
  pink: '#ff2e88', cyan: '#19e3ff', orange: '#ff9a3c', yellow: '#ffd23f', purple: '#8a3cff',
  green: '#39ff8a', red: '#ff3b4a', white: '#ffffff', ink: '#0b0b10',
};
const FONT_T = '"Russo One", "Rubik", sans-serif';
const FONT = '"Rubik", sans-serif';

// ---------- math ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const smooth = k => { k = clamp(k); return k * k * (3 - 2 * k); };
const easeOut = k => 1 - Math.pow(1 - clamp(k), 3);
const easeIn = k => Math.pow(clamp(k), 3);
const easeOutBack = k => { k = clamp(k); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
function rng(seed) { let a = seed >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const fmt = n => Math.floor(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

// ---------- primitives ----------
function rr(ctx, x, y, w, h, r) { r = Math.min(r, w / 2, h / 2); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function fillRR(ctx, x, y, w, h, r, fill) { rr(ctx, x, y, w, h, r); ctx.fillStyle = fill; ctx.fill(); }
function circle(ctx, x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, Math.max(0.1, r), 0, Math.PI * 2); ctx.fillStyle = fill; ctx.fill(); }
function ellipse(ctx, x, y, rx, ry, fill, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.max(0.1, rx), Math.max(0.1, ry), rot, 0, Math.PI * 2); ctx.fillStyle = fill; ctx.fill(); }
function vgrad(ctx, y0, y1, stops) { const g = ctx.createLinearGradient(0, y0, 0, y1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }
function rgrad(ctx, x, y, r0, r1, stops) { const g = ctx.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([o, c]) => g.addColorStop(o, c)); return g; }
function glow(ctx, x, y, r, color, alpha = 1) { ctx.save(); ctx.globalAlpha = alpha; ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = rgrad(ctx, x, y, 0, r, [[0, color], [1, 'rgba(0,0,0,0)']]); ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore(); }

function text(ctx, s, x, y, o = {}) {
  ctx.save();
  ctx.font = `${o.weight || 700} ${o.size || 48}px ${o.font || FONT}`;
  ctx.textAlign = o.align || 'center'; ctx.textBaseline = o.base || 'middle';
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  if (o.spacing) ctx.letterSpacing = o.spacing + 'px';
  if (o.glow) { ctx.shadowColor = o.glow; ctx.shadowBlur = o.blur || 30; }
  if (o.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = o.strokeW || 10; ctx.strokeStyle = o.stroke; ctx.strokeText(s, x, y); }
  ctx.fillStyle = o.color || '#fff'; ctx.fillText(s, x, y);
  if (o.glow) { ctx.shadowBlur = (o.blur || 30) / 2; ctx.fillText(s, x, y); }
  ctx.restore();
}
function neonText(ctx, s, x, y, size, color, o = {}) {
  const flick = o.flicker === undefined ? 1 : o.flicker;
  text(ctx, s, x, y, { size, font: o.font || FONT_T, weight: 400, color: o.core || '#fff', glow: color, blur: size * 0.5, alpha: flick, align: o.align, spacing: o.spacing });
  ctx.save(); ctx.globalAlpha = 0.55 * flick; ctx.globalCompositeOperation = 'lighter';
  text(ctx, s, x, y, { size, font: o.font || FONT_T, weight: 400, color, glow: color, blur: size, align: o.align, spacing: o.spacing });
  ctx.restore();
}
function wrapLines(ctx, s, maxW) { const words = s.split(' '); const lines = []; let cur = ''; for (const w of words) { const t = cur ? cur + ' ' + w : w; if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; } if (cur) lines.push(cur); return lines; }

// ---------- offscreen cache ----------
const _cache = {};
function cached(key, w, h, draw) { if (!_cache[key]) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); _cache[key] = c; } return _cache[key]; }
let _layer = null;
function layer() { if (!_layer) { _layer = document.createElement('canvas'); _layer.width = W; _layer.height = H; } const l = _layer.getContext('2d'); l.setTransform(1, 0, 0, 1, 0, 0); l.globalAlpha = 1; l.globalCompositeOperation = 'source-over'; l.clearRect(0, 0, W, H); return l; }

// ---------- sky / environment ----------
function sunsetSky(ctx, w, h, horizon) {
  ctx.fillStyle = vgrad(ctx, 0, horizon, [[0, '#120a2e'], [0.35, '#3b1460'], [0.62, '#a12a72'], [0.82, '#ff5a6e'], [1, '#ffb35c']]);
  ctx.fillRect(0, 0, w, horizon + 2);
}
function nightSky(ctx, w, h, horizon, seed = 3) {
  ctx.fillStyle = vgrad(ctx, 0, horizon, [[0, '#04040f'], [0.6, '#130f33'], [1, '#3a1650']]);
  ctx.fillRect(0, 0, w, horizon + 2);
  const r = rng(seed); ctx.fillStyle = '#fff';
  for (let i = 0; i < 160; i++) { ctx.globalAlpha = 0.2 + r() * 0.6; ctx.fillRect(r() * w, r() * horizon * 0.7, 2, 2); }
  ctx.globalAlpha = 1;
}
function retroSun(ctx, x, y, r) {
  ctx.save();
  glow(ctx, x, y, r * 2.4, 'rgba(255,120,90,0.55)');
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.clip();
  ctx.fillStyle = vgrad(ctx, y - r, y + r, [[0, '#ffe36b'], [0.55, '#ff8a4c'], [1, '#ff2e88']]); ctx.fillRect(x - r, y - r, r * 2, r * 2);
  ctx.globalCompositeOperation = 'destination-out';
  for (let i = 0; i < 7; i++) { const yy = y + r * 0.1 + i * r * 0.14; ctx.fillRect(x - r, yy, r * 2, 3 + i * 2.2); }
  ctx.restore();
}
// procedural skyline drawn into cached canvas
function skylineCanvas(key, w, h, o) {
  return cached(key, w, h, (c) => {
    const r = rng(o.seed || 1); let x = -20;
    while (x < w) {
      const bw = o.minW + r() * (o.maxW - o.minW);
      const bh = o.minH + r() * (o.maxH - o.minH) * (r() < 0.15 ? 1.5 : 1);
      const top = h - bh;
      c.fillStyle = o.color; c.fillRect(x, top, bw, bh);
      if (r() < 0.3) { c.fillRect(x + bw * 0.3, top - bh * 0.08, bw * 0.4, bh * 0.08); if (r() < 0.5) c.fillRect(x + bw * 0.48, top - bh * 0.2, 3, bh * 0.12); }
      if (o.edge) { c.fillStyle = o.edge; c.fillRect(x, top, 3, bh); }
      if (o.windows) {
        const ww = o.win || 6, gap = ww * 2.2;
        for (let wy = top + 12; wy < h - 10; wy += gap * 1.2) for (let wx = x + 8; wx < x + bw - 10; wx += gap) {
          const p = r(); if (p < o.lit) { c.fillStyle = p < o.lit * 0.15 ? '#7ff3ff' : p < o.lit * 0.3 ? '#ff8ad0' : '#ffd98a'; c.globalAlpha = 0.55 + r() * 0.45; c.fillRect(wx, wy, ww, ww * 1.3); c.globalAlpha = 1; }
        }
      }
      x += bw + (r() < 0.3 ? 4 : 0);
    }
  });
}
function cityLayers(ctx, t, horizon, scroll = 0, night = false, seedBase = 10) {
  const far = skylineCanvas('far' + seedBase + night, 2600, 420, { seed: seedBase, minW: 60, maxW: 150, minH: 120, maxH: 330, color: night ? '#1a1238' : '#4a1d5e', windows: night, lit: 0.25, win: 4 });
  const mid = skylineCanvas('mid' + seedBase + night, 2600, 560, { seed: seedBase + 1, minW: 90, maxW: 220, minH: 180, maxH: 460, color: night ? '#0f0b22' : '#2a0f3c', edge: night ? '#2a1d55' : '#5a2468', windows: true, lit: night ? 0.45 : 0.22, win: 6 });
  ctx.drawImage(far, -((scroll * 0.3) % 600) - 200, horizon - 420);
  ctx.drawImage(mid, -((scroll * 0.6) % 600) - 200, horizon - 560 + 30);
}
function palm(ctx, x, y, h, o = {}) {
  const sway = o.sway || 0, lean = o.lean || 0.15, col = o.color || '#10071c';
  const tx = x + h * lean + sway * h * 0.04, ty = y - h;
  ctx.save(); ctx.fillStyle = col; ctx.strokeStyle = col;
  // trunk
  ctx.beginPath(); const n = 14;
  const pts = []; for (let i = 0; i <= n; i++) { const k = i / n; pts.push([lerp(x, tx, k) + Math.sin(k * Math.PI) * h * 0.06, lerp(y, ty, k)]); }
  ctx.moveTo(pts[0][0] - h * 0.035, pts[0][1]);
  pts.forEach(([px, py], i) => ctx.lineTo(px - lerp(h * 0.035, h * 0.018, i / n), py));
  for (let i = n; i >= 0; i--) ctx.lineTo(pts[i][0] + lerp(h * 0.035, h * 0.018, i / n), pts[i][1]);
  ctx.fill();
  // fronds
  const fr = [-2.6, -2.1, -1.6, -1.1, -0.6, -0.15, 0.3];
  fr.forEach((a0, i) => {
    const a = a0 + Math.sin(sway + i) * 0.06; const L = h * (0.42 + (i % 2) * 0.08);
    const ex = tx + Math.cos(a) * L, ey = ty + Math.sin(a) * L * 0.55 + L * 0.35;
    const mx = tx + Math.cos(a) * L * 0.5, my = ty + Math.sin(a) * L * 0.5 - L * 0.05;
    ctx.beginPath(); ctx.moveTo(tx, ty);
    ctx.quadraticCurveTo(mx, my - L * 0.12, ex, ey);
    ctx.quadraticCurveTo(mx, my + L * 0.1, tx, ty + 6);
    ctx.fill();
  });
  circle(ctx, tx, ty + 4, h * 0.035, col);
  ctx.restore();
}
function car(ctx, x, y, s, color = C.pink, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(o.flip ? -s : s, s);
  if (o.underglow) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; ellipse(ctx, 210, 6, 230, 22, o.underglow); ctx.restore(); }
  ellipse(ctx, 210, 4, 220, 14, 'rgba(0,0,0,0.45)');
  ctx.beginPath(); ctx.moveTo(0, -18); ctx.quadraticCurveTo(4, -50, 40, -56); ctx.lineTo(120, -62);
  ctx.quadraticCurveTo(160, -104, 230, -104); ctx.quadraticCurveTo(290, -100, 330, -62);
  ctx.lineTo(400, -50); ctx.quadraticCurveTo(428, -44, 426, -16); ctx.lineTo(420, -4); ctx.lineTo(6, -4); ctx.closePath();
  ctx.fillStyle = color; ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.18)'; ctx.fillRect(40, -54, 360, 6);
  ctx.beginPath(); ctx.moveTo(140, -64); ctx.quadraticCurveTo(170, -96, 230, -96); ctx.quadraticCurveTo(280, -94, 312, -64); ctx.closePath(); ctx.fillStyle = '#121626'; ctx.fill();
  ctx.fillStyle = 'rgba(140,220,255,0.35)'; ctx.beginPath(); ctx.moveTo(240, -94); ctx.lineTo(262, -94); ctx.lineTo(236, -66); ctx.lineTo(214, -66); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(220, -62, 3, 50);
  for (const wx of [92, 338]) { circle(ctx, wx, -6, 34, '#0a0a0e'); circle(ctx, wx, -6, 20, '#8a8a95'); circle(ctx, wx, -6, 8, '#2a2a30'); }
  fillRR(ctx, 404, -40, 20, 10, 4, '#fff6c8'); fillRR(ctx, 2, -42, 14, 10, 4, '#ff2340');
  if (o.lights) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; const g = ctx.createLinearGradient(420, 0, 900, 0); g.addColorStop(0, 'rgba(255,245,200,0.55)'); g.addColorStop(1, 'rgba(255,245,200,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(420, -40); ctx.lineTo(900, -110); ctx.lineTo(900, 40); ctx.lineTo(420, -30); ctx.fill(); glow(ctx, 6, -37, 40, 'rgba(255,30,60,0.8)'); ctx.restore(); }
  ctx.restore();
}
// generic background person (crowd)
function person(ctx, x, y, s, seed, o = {}) {
  const r = rng(seed); const shirts = ['#2f6fff', '#ff4f6d', '#2bb673', '#f4b23e', '#7a4cff', '#e8e8f0', '#1fc3c9', '#ff7a2f'];
  const skins = ['#f1c7a0', '#d6a77a', '#a8754f', '#7a5236', '#e7b48e'];
  const shirt = shirts[Math.floor(r() * shirts.length)], skin = skins[Math.floor(r() * skins.length)];
  const hairC = ['#1a120c', '#3b2414', '#0d0d0d', '#a0662a', '#d9c28a'][Math.floor(r() * 5)];
  const hh = 1 + (r() - 0.5) * 0.15, bob = o.bob || 0;
  ctx.save(); ctx.translate(x, y + bob); ctx.scale(s, s * hh);
  if (o.back) { /* seen from behind */ }
  fillRR(ctx, -26, -110, 22, 110, 8, '#20202a'); fillRR(ctx, 4, -110, 22, 110, 8, '#20202a');
  fillRR(ctx, -36, -210, 72, 112, 22, shirt);
  fillRR(ctx, -50, -200, 18, 90, 9, shirt); fillRR(ctx, 32, -200, 18, 90, 9, shirt);
  circle(ctx, -41, -106, 10, skin); circle(ctx, 41, -106, 10, skin);
  circle(ctx, 0, -250, 38, skin);
  ctx.fillStyle = hairC; ctx.beginPath(); ctx.arc(0, -256, 40, Math.PI * 1.02, Math.PI * 1.98); ctx.quadraticCurveTo(30, -246, 0, -250); ctx.quadraticCurveTo(-30, -246, -40, -252); ctx.fill();
  if (o.back) { circle(ctx, 0, -252, 39, hairC); }
  else { ellipse(ctx, -13, -246, 4.5, 7, '#111'); ellipse(ctx, 13, -246, 4.5, 7, '#111'); }
  if (o.box) { fillRR(ctx, -60, -190, 120, 100, 6, o.box); text(ctx, o.boxLabel || '', 0, -140, { size: 22, color: '#fff', font: FONT_T, weight: 400 }); }
  if (o.phone) { fillRR(ctx, 28, -200, 18, 30, 4, '#111'); ctx.save(); ctx.globalCompositeOperation = 'lighter'; fillRR(ctx, 30, -198, 14, 26, 3, 'rgba(120,220,255,0.8)'); ctx.restore(); }
  ctx.restore();
}

// ---------- THE HERO (one model for the whole series) ----------
// x,y = head centre, R = head radius.
// view: 'front' | '3q' | 'side' | 'back'.  expr: neutral|sad|surprised|smile|determined|worried|smug|bored
function heroHair(ctx, cx, cy, R, view, dir = 1) {
  ctx.fillStyle = C.hair;
  if (view === 'back') {
    ctx.beginPath(); const n = 22;
    for (let i = 0; i <= n; i++) { const a = Math.PI * 0.62 + (i / n) * Math.PI * 1.76; const rr_ = R * (i % 2 ? 1.13 : 1.05); ctx.lineTo(cx + Math.cos(a) * rr_, cy - R * 0.05 + Math.sin(a) * rr_); }
    // nape jag
    for (let i = 0; i <= 6; i++) { const k = i / 6; ctx.lineTo(cx + lerp(R * 0.45, -R * 0.45, k), cy + R * (0.78 + (i % 2) * 0.16)); }
    ctx.closePath(); ctx.fill();
    ctx.strokeStyle = C.hairHi; ctx.lineWidth = R * 0.05; ctx.lineCap = 'round';
    [[-0.4, -0.6, -0.1, -0.1], [0.3, -0.7, 0.15, 0], [0, -0.9, 0.05, -0.3]].forEach(([a, b, c, d]) => { ctx.beginPath(); ctx.moveTo(cx + a * R, cy + b * R); ctx.quadraticCurveTo(cx + (a + c) * R * 0.6, cy + (b + d) * R * 0.5, cx + c * R, cy + d * R); ctx.stroke(); });
    return;
  }
  if (view === 'side') {
    ctx.save(); ctx.translate(cx, cy); ctx.scale(dir, 1);
    ctx.beginPath(); const n = 18;
    for (let i = 0; i <= n; i++) { const a = Math.PI * 0.62 + (i / n) * Math.PI * 1.32; const rr_ = R * (i % 2 ? 1.13 : 1.04); ctx.lineTo(Math.cos(a) * rr_, -R * 0.06 + Math.sin(a) * rr_); }
    ctx.lineTo(R * 0.92, -R * 0.42); ctx.lineTo(R * 0.6, -R * 0.2); ctx.lineTo(R * 0.48, -R * 0.36); ctx.lineTo(R * 0.25, -R * 0.12); ctx.lineTo(R * 0.05, -R * 0.3);
    ctx.lineTo(-R * 0.15, R * 0.1); ctx.lineTo(-R * 0.42, R * 0.7); ctx.lineTo(-R * 0.7, R * 0.62); ctx.closePath(); ctx.fill();
    ctx.restore(); return;
  }
  const off = view === '3q' ? R * 0.16 * dir : 0;
  ctx.beginPath();
  const n = 20;
  for (let i = 0; i <= n; i++) {
    const a = Math.PI * 0.94 + (i / n) * Math.PI * 1.12;
    const jag = [1.14, 1.04, 1.18, 1.05, 1.12, 1.03, 1.2, 1.05, 1.13, 1.04][i % 10];
    ctx.lineTo(cx + Math.cos(a) * R * jag - off * 0.2, cy - R * 0.08 + Math.sin(a) * R * jag);
  }
  // fringe (right to left), spiky downward locks
  const fr = [[1.02, -0.06], [0.82, -0.3], [0.7, -0.06], [0.48, -0.32], [0.3, -0.14], [0.12, -0.34], [-0.1, -0.12], [-0.3, -0.33], [-0.48, -0.08], [-0.66, -0.3], [-0.82, 0.12], [-1.0, -0.1], [-1.1, 0.2]];
  fr.forEach(([fx, fy]) => ctx.lineTo(cx + fx * R + off, cy + fy * R));
  ctx.closePath(); ctx.fill();
  ctx.strokeStyle = C.hairHi; ctx.lineWidth = R * 0.045; ctx.lineCap = 'round';
  [[-0.5, -0.9, -0.2, -0.45], [0.2, -1.0, 0.45, -0.5], [0.65, -0.75, 0.75, -0.35]].forEach(([a, b, c, d]) => { ctx.beginPath(); ctx.moveTo(cx + a * R + off, cy + b * R); ctx.quadraticCurveTo(cx + (a + c) * 0.5 * R + off + R * 0.1, cy + (b + d) * 0.5 * R, cx + c * R + off, cy + d * R); ctx.stroke(); });
}
function heroFace(ctx, cx, cy, R, o) {
  const view = o.view, dir = o.dir || 1, ex = o.expr || 'neutral';
  const lookX = (o.lookX || 0) * R * 0.06, lookY = (o.lookY || 0) * R * 0.05;
  const fx = view === '3q' ? R * 0.2 * dir : 0;
  const sp = view === '3q' ? R * 0.24 : R * 0.27;
  const eyes = view === 'side' ? [[cx + R * 0.58 * dir, cy + R * 0.08]] : [[cx + fx - sp, cy + R * 0.1], [cx + fx + sp, cy + R * 0.1]];
  let ery = R * 0.15, erx = R * 0.1;
  if (ex === 'surprised') { ery *= 1.15; erx *= 1.1; }
  if (ex === 'smug' || ex === 'bored') ery *= 0.6;
  if (ex === 'smile') ery *= 0.9;
  const blink = o.blink ? 0.12 : 1;
  eyes.forEach(([x, y], i) => {
    if (ex === 'smile' && o.happyEyes) { ctx.strokeStyle = '#0b0b0e'; ctx.lineWidth = R * 0.06; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(x, y + R * 0.04, erx * 1.1, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); return; }
    ellipse(ctx, x + lookX, y + lookY + (ex === 'smug' || ex === 'bored' ? R * 0.04 : 0), erx, ery * blink, '#0b0b0e');
    if (blink === 1) circle(ctx, x + lookX + erx * 0.35, y + lookY - ery * 0.4, R * 0.028, 'rgba(255,255,255,0.9)');
    if ((ex === 'smug' || ex === 'bored') && blink === 1) { ctx.fillStyle = C.skin; ctx.fillRect(x - erx * 1.3, y - ery * 1.6, erx * 2.6, ery * 1.25); ctx.fillStyle = '#0b0b0e'; ctx.fillRect(x - erx * 1.2, y - ery * 0.38, erx * 2.4, R * 0.035); }
  });
  // brows
  ctx.strokeStyle = '#0b0b0e'; ctx.lineCap = 'round'; ctx.lineWidth = R * 0.075;
  const browY = { surprised: -0.27, sad: -0.15, worried: -0.17, determined: -0.1, smile: -0.17, neutral: -0.14, smug: -0.13, bored: -0.12 }[ex] ?? -0.14;
  const tilt = { sad: -0.08, worried: -0.09, determined: 0.09, smug: 0.03, surprised: -0.02 }[ex] || 0;
  eyes.forEach(([x, y], i) => {
    const side = view === 'side' ? 1 : (i === 0 ? -1 : 1);
    const inner = x - side * R * 0.13, outer = x + side * R * 0.13;
    ctx.beginPath(); ctx.moveTo(inner, cy + browY * R + tilt * R); ctx.lineTo(outer, cy + browY * R - tilt * R * 0.4); ctx.stroke();
  });
  // mouth
  const mx = view === 'side' ? cx + R * 0.62 * dir : cx + fx * 1.1, my = cy + R * 0.5;
  ctx.lineWidth = R * 0.05;
  const talk = o.talk || 0;
  if (ex === 'surprised') { ellipse(ctx, mx, my, R * 0.08, R * 0.11 + talk * R * 0.03, '#3a0d12'); ellipse(ctx, mx, my + R * 0.05, R * 0.05, R * 0.04, '#c4515e'); }
  else if (ex === 'smile') { ctx.beginPath(); ctx.moveTo(mx - R * 0.17, my - R * 0.04); ctx.quadraticCurveTo(mx, my + R * 0.22, mx + R * 0.17, my - R * 0.04); ctx.closePath(); ctx.fillStyle = '#3a0d12'; ctx.fill(); ctx.save(); ctx.clip(); ellipse(ctx, mx, my + R * 0.14, R * 0.09, R * 0.05, '#c4515e'); ctx.fillStyle = '#fff'; ctx.fillRect(mx - R * 0.17, my - R * 0.05, R * 0.34, R * 0.045); ctx.restore(); }
  else if (ex === 'sad') { ctx.beginPath(); ctx.arc(mx, my + R * 0.1, R * 0.11, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
  else if (ex === 'worried') { ctx.beginPath(); ctx.moveTo(mx - R * 0.12, my); ctx.quadraticCurveTo(mx - R * 0.06, my - R * 0.05, mx, my); ctx.quadraticCurveTo(mx + R * 0.06, my + R * 0.05, mx + R * 0.12, my); ctx.stroke(); ellipse(ctx, cx + fx - R * 0.6, cy - R * 0.05, R * 0.05, R * 0.08, 'rgba(150,200,255,0.85)'); }
  else if (ex === 'determined' || ex === 'smug') { ctx.beginPath(); ctx.moveTo(mx - R * 0.12, my + R * 0.02); ctx.quadraticCurveTo(mx + R * 0.02, my + R * 0.08, mx + R * 0.15, my - R * 0.04); ctx.stroke(); }
  else if (talk > 0.05) { ellipse(ctx, mx, my, R * 0.07, R * 0.03 + talk * R * 0.06, '#3a0d12'); }
}
function hero(ctx, o) {
  const { x, y, R } = o; const view = o.view || 'front', dir = o.dir || 1;
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha = o.alpha;
  const bob = o.bob || 0; const cy = y + bob;
  // ----- body -----
  if (o.body !== 'none') {
    const sw = view === 'side' ? R * 0.62 : R * 1.02, shY = cy + R * 1.02, botY = cy + R * 3.35;
    if (o.body === 'full') {
      // legs
      const legW = view === 'side' ? R * 0.55 : R * 0.6, gap = view === 'side' ? -R * 0.3 : R * 0.08;
      const lstep = o.walk ? Math.sin(o.walk) * R * 0.25 : 0;
      [[-1, lstep], [1, -lstep]].forEach(([s, st]) => {
        const lx = view === 'side' ? x - legW / 2 + st : x + s * (gap / 2 + legW / 2) - legW / 2;
        ctx.fillStyle = C.pants; ctx.beginPath(); ctx.moveTo(lx + 2, botY - R * 0.2); ctx.lineTo(lx + legW - 2, botY - R * 0.2); ctx.lineTo(lx + legW + R * 0.04, cy + R * 6.5); ctx.lineTo(lx - R * 0.04, cy + R * 6.5); ctx.fill();
        const shx = view === 'side' ? lx + legW * 0.5 + dir * R * 0.12 : lx + legW / 2;
        fillRR(ctx, shx - R * 0.42, cy + R * 6.42, R * 0.84, R * 0.3, R * 0.14, C.shoe);
        fillRR(ctx, shx - R * 0.42, cy + R * 6.62, R * 0.84, R * 0.1, R * 0.05, C.shoeSh);
      });
    }
    // torso
    ctx.fillStyle = C.sweater; ctx.beginPath();
    ctx.moveTo(x - sw * 0.6, shY); ctx.quadraticCurveTo(x - sw, shY, x - sw, shY + R * 0.4);
    ctx.lineTo(x - sw * 0.94, o.body === 'bust' ? cy + R * 6 : botY); ctx.lineTo(x + sw * 0.94, o.body === 'bust' ? cy + R * 6 : botY);
    ctx.lineTo(x + sw, shY + R * 0.4); ctx.quadraticCurveTo(x + sw, shY, x + sw * 0.6, shY); ctx.closePath(); ctx.fill();
    if (o.body !== 'bust' || o.hem) fillRR(ctx, x - sw * 0.94, botY - R * 0.18, sw * 1.88, R * 0.2, R * 0.08, C.sweaterSh);
    // sleeves + hands
    const arms = o.arms || 'down';
    if (view !== 'back' || arms === 'down') {
      const sides = view === 'side' ? [0] : [-1, 1];
      sides.forEach(s => {
        const ax = view === 'side' ? x + dir * R * 0.05 : x + s * (sw + R * 0.08);
        if (arms === 'down') {
          ctx.fillStyle = s === 0 ? C.sweaterSh : C.sweater; ctx.beginPath(); ctx.moveTo(ax - R * 0.22, shY + R * 0.2); ctx.lineTo(ax + R * 0.22, shY + R * 0.2); ctx.lineTo(ax + R * 0.25, cy + R * 3.25); ctx.lineTo(ax - R * 0.25, cy + R * 3.25); ctx.fill();
          ctx.strokeStyle = C.sweaterSh; ctx.lineWidth = R * 0.04; ctx.beginPath(); ctx.moveTo(ax - s * R * 0.2, shY + R * 0.5); ctx.lineTo(ax - s * R * 0.22, cy + R * 3.1); ctx.stroke();
          fillRR(ctx, ax - R * 0.25, cy + R * 3.1, R * 0.5, R * 0.16, R * 0.06, C.sweaterSh);
          circle(ctx, ax, cy + R * 3.5, R * 0.27, C.skin);
        } else if (arms === 'desk') {
          ctx.fillStyle = C.sweaterSh; ctx.beginPath(); ctx.moveTo(ax - R * 0.22, shY + R * 0.2); ctx.lineTo(ax + R * 0.22, shY + R * 0.2); ctx.lineTo(ax - s * R * 0.2 + R * 0.25, cy + R * 2.9); ctx.lineTo(ax - s * R * 0.2 - R * 0.25, cy + R * 2.9); ctx.fill();
          const hx = ax - s * R * 0.5 + (o.typing ? Math.sin(o.typing * (s > 0 ? 1.3 : 1.7)) * R * 0.06 : 0); const hy = cy + R * 2.85 + (o.typing ? Math.abs(Math.sin(o.typing * 2 + s)) * -R * 0.08 : 0);
          circle(ctx, hx, hy, R * 0.26, C.skin);
        } else if (arms === 'chin') {
          ctx.fillStyle = C.sweaterSh; ctx.beginPath(); ctx.moveTo(x + R * 0.9, shY + R * 1.8); ctx.lineTo(x + R * 0.4, cy + R * 1.1); ctx.lineTo(x + R * 0.1, cy + R * 1.2); ctx.lineTo(x + R * 0.5, shY + R * 2.0); ctx.fill();
        }
      });
    }
    // neck
    fillRR(ctx, x - R * 0.17 + (view === 'side' ? dir * R * 0.08 : 0), cy + R * 0.8, R * 0.34, R * 0.32, R * 0.05, C.skinSh);
    // collar
    ctx.fillStyle = C.sweaterSh; ctx.beginPath(); ctx.ellipse(x + (view === 'side' ? dir * R * 0.08 : 0), shY + R * 0.02, R * 0.3, R * 0.08, 0, 0, Math.PI); ctx.fill();
  }
  // ----- head -----
  const tilt = o.tilt || 0;
  ctx.save(); ctx.translate(x, cy); ctx.rotate(tilt); ctx.translate(-x, -cy);
  circle(ctx, x, cy, R, C.skin);
  if (view !== 'back') { ctx.save(); ctx.beginPath(); ctx.arc(x, cy, R, 0, Math.PI * 2); ctx.clip(); ellipse(ctx, x - dir * R * 0.15, cy + R * 0.95, R * 1.1, R * 0.35, 'rgba(120,70,40,0.18)'); ctx.restore(); }
  if (view === 'side') { // ear
    ellipse(ctx, x - dir * R * 0.12, cy + R * 0.12, R * 0.12, R * 0.17, C.skinSh);
  }
  if (view === '3q') ellipse(ctx, x - dir * R * 0.86, cy + R * 0.14, R * 0.1, R * 0.16, C.skinSh);
  heroHair(ctx, x, cy, R, view, dir);
  if (view !== 'back') heroFace(ctx, x, cy, R, { ...o, view, dir });
  if (o.blush) { ellipse(ctx, x - R * 0.45, cy + R * 0.35, R * 0.12, R * 0.06, 'rgba(255,90,90,0.35)'); ellipse(ctx, x + R * 0.45, cy + R * 0.35, R * 0.12, R * 0.06, 'rgba(255,90,90,0.35)'); }
  ctx.restore();
  ctx.restore();
}
// draw hero onto its own layer so we can light it with the scene (screen glow / rim light)
function litHero(ctx, o, light) {
  const l = layer(); hero(l, o);
  if (light) {
    l.globalCompositeOperation = 'source-atop';
    if (light.tint) { l.globalAlpha = light.tintA || 0.25; l.fillStyle = light.tint; l.fillRect(0, 0, W, H); l.globalAlpha = 1; }
    if (light.from) { const [lx, ly, lr, lc] = light.from; l.globalCompositeOperation = 'source-atop'; l.fillStyle = rgrad(l, lx, ly, 0, lr, [[0, lc], [1, 'rgba(0,0,0,0)']]); l.fillRect(0, 0, W, H); }
    if (light.shade) { l.globalAlpha = light.shade; l.fillStyle = '#05050c'; l.fillRect(0, 0, W, H); l.globalAlpha = 1; }
    l.globalCompositeOperation = 'source-over';
  }
  ctx.drawImage(_layer, 0, 0);
}

// ---------- props ----------
function crtMonitor(ctx, x, y, w, h, drawScreen, t = 0) {
  // beige old monitor, screen area x,y,w,h
  const b = w * 0.07;
  fillRR(ctx, x - b, y - b, w + b * 2, h + b * 2.6, b * 0.6, '#b9b29e');
  fillRR(ctx, x - b * 0.5, y - b * 0.5, w + b, h + b, b * 0.35, '#8c8676');
  fillRR(ctx, x + w * 0.35, y + h + b * 2.5, w * 0.3, b * 1.4, 4, '#a39c88');
  fillRR(ctx, x + w * 0.2, y + h + b * 3.6, w * 0.6, b * 0.6, 6, '#b9b29e');
  circle(ctx, x + w + b * 0.4, y + h + b * 1.25, b * 0.14, '#41ff7a');
  ctx.save(); rr(ctx, x, y, w, h, b * 0.25); ctx.clip(); ctx.translate(x, y);
  drawScreen(ctx, w, h);
  ctx.globalAlpha = 0.08; ctx.fillStyle = '#000'; for (let i = 0; i < h; i += 4) ctx.fillRect(0, i, w, 2);
  ctx.globalAlpha = 1; ctx.fillStyle = rgrad(ctx, w / 2, h / 2, Math.min(w, h) * 0.3, Math.max(w, h) * 0.75, [[0, 'rgba(255,255,255,0.04)'], [1, 'rgba(0,0,0,0.45)']]); ctx.fillRect(0, 0, w, h);
  ctx.restore();
}
function screenGlowOnRoom(ctx, x, y, r, color, a = 0.5) { glow(ctx, x, y, r, color, a); }
function scanlines(ctx, a = 0.06) { ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = '#000'; for (let i = 0; i < H; i += 4) ctx.fillRect(0, i, W, 2); ctx.restore(); }
function vignette(ctx, a = 0.55) { ctx.save(); ctx.fillStyle = rgrad(ctx, W / 2, H / 2, H * 0.35, W * 0.72, [[0, 'rgba(0,0,0,0)'], [1, `rgba(0,0,0,${a})`]]); ctx.fillRect(0, 0, W, H); ctx.restore(); }
function cursor(ctx, x, y, s = 1, click = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (click > 0) { ctx.strokeStyle = `rgba(255,255,255,${1 - click})`; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(0, 0, 10 + click * 40, 0, Math.PI * 2); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 34); ctx.lineTo(9, 26); ctx.lineTo(16, 40); ctx.lineTo(22, 37); ctx.lineTo(15, 23); ctx.lineTo(26, 23); ctx.closePath();
  ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = '#000'; ctx.lineWidth = 2.5; ctx.stroke(); ctx.restore();
}
function bulb(ctx, x, y, s, a = 1) {
  ctx.save(); ctx.globalAlpha = a; glow(ctx, x, y, 160 * s, 'rgba(255,220,90,0.8)');
  ctx.strokeStyle = 'rgba(255,230,120,0.9)'; ctx.lineWidth = 6 * s; ctx.lineCap = 'round';
  for (let i = 0; i < 8; i++) { const an = -Math.PI / 2 + (i - 3.5) * 0.38; ctx.beginPath(); ctx.moveTo(x + Math.cos(an) * 70 * s, y + Math.sin(an) * 70 * s); ctx.lineTo(x + Math.cos(an) * 100 * s, y + Math.sin(an) * 100 * s); ctx.stroke(); }
  circle(ctx, x, y, 48 * s, '#ffe680'); circle(ctx, x - 14 * s, y - 14 * s, 14 * s, '#fffbe0');
  fillRR(ctx, x - 22 * s, y + 40 * s, 44 * s, 30 * s, 6 * s, '#9aa0aa'); ctx.restore();
}

// "Vice" mini-scenes reused in thumbnails / screens
function viceSunsetScene(ctx, w, h, t = 0, o = {}) {
  ctx.save(); ctx.scale(w / 1920, h / 1080);
  sunsetSky(ctx, 1920, 1080, 760); retroSun(ctx, 960 + (o.sunX || 0), 640, 230);
  cityLayers(ctx, t, 790, t * 40, false, 10);
  ctx.fillStyle = vgrad(ctx, 760, 1080, [[0, '#3a1050'], [1, '#12061c']]); ctx.fillRect(0, 780, 1920, 300);
  ctx.globalAlpha = 0.5; ctx.fillStyle = '#ff7a8a'; for (let i = 0; i < 12; i++) ctx.fillRect(760 + Math.sin(i * 2 + t) * 30, 800 + i * 18, 400 - i * 25, 3); ctx.globalAlpha = 1;
  palm(ctx, 180, 1100, 620, { sway: t * 1.2, lean: 0.2 }); palm(ctx, 1720, 1100, 560, { sway: t * 1.2 + 1, lean: -0.25 }); palm(ctx, 1520, 1100, 420, { sway: t + 2, lean: -0.1 });
  if (!o.noCar) car(ctx, ((o.carX ?? 400) + t * 260) % 2400 - 400, 1030, 1.1, o.carColor || '#ff2e88', { lights: true });
  ctx.restore();
}
function viceNightStreet(ctx, w, h, t = 0, o = {}) {
  ctx.save(); ctx.scale(w / 1920, h / 1080);
  nightSky(ctx, 1920, 1080, 700, 8);
  cityLayers(ctx, t, 700, t * 30, true, 20);
  // storefront row
  const scroll = (o.scroll || 0);
  for (let i = -1; i < 8; i++) {
    const bx = i * 360 - (scroll % 360);
    ctx.fillStyle = i % 2 ? '#1c1033' : '#160c28'; ctx.fillRect(bx, 520, 352, 400);
    const cols = [C.pink, C.cyan, C.yellow, C.purple, C.orange];
    const col = cols[((i + Math.floor(scroll / 360)) % 5 + 5) % 5];
    fillRR(ctx, bx + 40, 560, 272, 60, 10, 'rgba(0,0,0,0.5)');
    neonText(ctx, ['MOTEL', 'BAR', 'DINER', 'CLUB', 'TATTOO'][((i + Math.floor(scroll / 360)) % 5 + 5) % 5], bx + 176, 592, 44, col, { flicker: 0.85 + 0.15 * Math.sin(t * 9 + i) });
    ctx.fillStyle = 'rgba(255,200,120,0.25)'; ctx.fillRect(bx + 40, 660, 272, 200);
  }
  ctx.fillStyle = '#0a0612'; ctx.fillRect(0, 900, 1920, 180);
  ctx.fillStyle = '#211533'; ctx.fillRect(0, 880, 1920, 24);
  ctx.globalAlpha = 0.35; ctx.fillStyle = C.pink; ctx.fillRect(0, 930, 1920, 4); ctx.globalAlpha = 1;
  for (let i = -1; i < 7; i++) palm(ctx, i * 420 - (scroll * 1.4 % 420) + 160, 905, 420, { sway: t * 1.5 + i, lean: 0.12, color: '#07030d' });
  ctx.restore();
}
function viceThumb(ctx, x, y, w, h, kind, t = 0) {
  ctx.save(); rr(ctx, x, y, w, h, 14); ctx.clip(); ctx.translate(x, y);
  if (kind === 'night') viceNightStreet(ctx, w, h, t, { scroll: t * 100 });
  else if (kind === 'car') { viceSunsetScene(ctx, w, h, t, { carX: 700, carColor: '#19e3ff' }); }
  else viceSunsetScene(ctx, w, h, t, { noCar: kind === 'sun2' });
  ctx.restore();
}
// generic platform UI (no real brand)
function playIcon(ctx, x, y, s, col = C.red) { fillRR(ctx, x - 30 * s, y - 21 * s, 60 * s, 42 * s, 12 * s, col); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(x - 9 * s, y - 11 * s); ctx.lineTo(x + 13 * s, y); ctx.lineTo(x - 9 * s, y + 11 * s); ctx.fill(); }
function notif(ctx, x, y, w, title, sub, col, a = 1, icon = 'bell') {
  ctx.save(); ctx.globalAlpha = a;
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 30; fillRR(ctx, x, y, w, 96, 22, 'rgba(24,22,36,0.95)'); ctx.shadowBlur = 0;
  circle(ctx, x + 50, y + 48, 28, col);
  if (icon === 'bell') { ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x + 50, y + 46, 12, Math.PI, 0); ctx.lineTo(x + 64, y + 56); ctx.lineTo(x + 36, y + 56); ctx.closePath(); ctx.fill(); circle(ctx, x + 50, y + 60, 4, '#fff'); }
  else if (icon === 'plus') text(ctx, '+', x + 50, y + 47, { size: 40, color: '#fff' });
  else if (icon === 'msg') { fillRR(ctx, x + 36, y + 36, 28, 20, 5, '#fff'); }
  else if (icon === 'up') { ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(x + 50, y + 32); ctx.lineTo(x + 64, y + 52); ctx.lineTo(x + 36, y + 52); ctx.fill(); ctx.fillRect(x + 45, y + 50, 10, 14); }
  text(ctx, title, x + 96, y + 34, { size: 28, align: 'left', color: '#fff', weight: 700 });
  text(ctx, sub, x + 96, y + 68, { size: 22, align: 'left', color: '#aab', weight: 400 });
  ctx.restore();
}
function particlesUp(ctx, t, n, seed, area, draw) { const r = rng(seed); for (let i = 0; i < n; i++) { const x0 = area[0] + r() * area[2], sp = 60 + r() * 120, ph = r() * 10, life = 2 + r() * 2; const k = ((t + ph) % life) / life; draw(x0 + Math.sin((t + ph) * 2) * 20, area[1] + area[3] - k * area[3] * (sp / 120), k, i); } }
function fireworks(ctx, t, seed, bursts) {
  const r = rng(seed);
  bursts.forEach(([t0, x, y, col]) => {
    const k = (t - t0); if (k < 0 || k > 2.2) return;
    if (k < 0.5) { const yy = lerp(1080, y, easeOut(k / 0.5)); circle(ctx, x, yy, 4, '#fff'); return; }
    const kk = (k - 0.5) / 1.7; ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 48; i++) { const a = (i / 48) * Math.PI * 2; const d = easeOut(kk) * 220; const px = x + Math.cos(a) * d, py = y + Math.sin(a) * d + kk * kk * 80; ctx.globalAlpha = 1 - kk; circle(ctx, px, py, 4.5 * (1 - kk) + 1, col); }
    glow(ctx, x, y, 300, col, (1 - kk) * 0.35); ctx.restore();
  });
}
