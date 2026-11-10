// Drawing library: helpers, characters, 90s props.
const W = 1920, H = 1080;
let c; // active 2D context

const cl = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => cl((t - a) / (b - a));
const eio = t => (t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
const eo = t => 1 - Math.pow(1 - t, 3);
const ei = t => t * t * t;
const TAU = Math.PI * 2;

function rng(seed) {
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const hash = (n) => { const r = rng(n * 9301 + 49297); r(); return r(); };

// ---------- primitives ----------
function rect(x, y, w, h, col) { c.fillStyle = col; c.fillRect(x, y, w, h); }
function rr(x, y, w, h, r, col, sc, sw) { c.beginPath(); c.roundRect(x, y, w, h, r); if (col) { c.fillStyle = col; c.fill(); } if (sc) { c.strokeStyle = sc; c.lineWidth = sw || 4; c.stroke(); } }
function circ(x, y, r, col) { c.beginPath(); c.arc(x, y, Math.max(0, r), 0, TAU); c.fillStyle = col; c.fill(); }
function ell(x, y, rx, ry, col, rot = 0) { c.beginPath(); c.ellipse(x, y, Math.max(0, rx), Math.max(0, ry), rot, 0, TAU); c.fillStyle = col; c.fill(); }
function poly(p, col) { c.beginPath(); c.moveTo(p[0], p[1]); for (let i = 2; i < p.length; i += 2) c.lineTo(p[i], p[i + 1]); c.closePath(); c.fillStyle = col; c.fill(); }
function line(x1, y1, x2, y2, col, w = 4, cap = 'round') { c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.strokeStyle = col; c.lineWidth = w; c.lineCap = cap; c.stroke(); }
function pline(p, col, w = 4) { c.beginPath(); c.moveTo(p[0], p[1]); for (let i = 2; i < p.length; i += 2) c.lineTo(p[i], p[i + 1]); c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.lineJoin = 'round'; c.stroke(); }
function txt(s, x, y, size, col, opt = {}) {
  c.font = `${opt.w || 900} ${size}px ${opt.f || 'Inter'}`; c.textAlign = opt.a || 'center'; c.textBaseline = opt.b || 'middle';
  if (opt.ls) c.letterSpacing = opt.ls + 'px'; else c.letterSpacing = '0px';
  if (opt.stroke) { c.lineJoin = 'round'; c.strokeStyle = opt.stroke; c.lineWidth = opt.sw || size * 0.16; c.strokeText(s, x, y); }
  c.fillStyle = col; c.fillText(s, x, y);
}
function grad(x0, y0, x1, y1, stops) { const g = c.createLinearGradient(x0, y0, x1, y1); stops.forEach(([o, col]) => g.addColorStop(o, col)); return g; }
function rgrad(x, y, r0, r1, stops) { const g = c.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([o, col]) => g.addColorStop(o, col)); return g; }
function push(x = 0, y = 0, rot = 0, sx = 1, sy = sx) { c.save(); c.translate(x, y); if (rot) c.rotate(rot); if (sx !== 1 || sy !== 1) c.scale(sx, sy); }
function pop() { c.restore(); }
function alpha(a, fn) { c.save(); c.globalAlpha *= a; fn(); c.restore(); }

// ---------- noise textures ----------
const NOISE = [];
function initNoise() {
  for (let k = 0; k < 6; k++) {
    const cv = document.createElement('canvas'); cv.width = 240; cv.height = 180;
    const x = cv.getContext('2d'); const im = x.createImageData(240, 180); const r = rng(k + 7);
    for (let i = 0; i < im.data.length; i += 4) { const v = r() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    x.putImageData(im, 0, 0); NOISE.push(cv);
  }
}
function staticFill(x, y, w, h, t, a = 1) { c.save(); c.globalAlpha *= a; c.imageSmoothingEnabled = false; c.drawImage(NOISE[Math.floor(t * 30) % NOISE.length], x, y, w, h); c.restore(); }

// ---------- IK limbs ----------
function ik(ax, ay, bx, by, l1, l2, bend) {
  let dx = bx - ax, dy = by - ay, d = Math.hypot(dx, dy); const m = l1 + l2 - 0.5;
  if (d > m) { bx = ax + dx / d * m; by = ay + dy / d * m; d = m; }
  if (d < 1) d = 1;
  const a = Math.atan2(dy, dx); const ca = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d);
  const g = a + bend * Math.acos(cl(ca, -1, 1));
  return [ax + Math.cos(g) * l1, ay + Math.sin(g) * l1, bx, by];
}
function limb(ax, ay, bx, by, l1, l2, bend, w, col) {
  const k = ik(ax, ay, bx, by, l1, l2, bend);
  c.beginPath(); c.moveTo(ax, ay); c.lineTo(k[0], k[1]); c.lineTo(k[2], k[3]);
  c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.lineJoin = 'round'; c.stroke();
  return k;
}

// ---------- characters ----------
const HERO = { skin: '#d9a57a', hair: 'messy', hairCol: '#16131a', top: 'sweater', c1: '#2d5b6b', c2: '#e3a83c', c3: '#a3333f', pants: '#86a3c6', acid: true, shoes: '#ece7dc', shoe2: '#3a63a8' };
const shade = (hex, f) => { const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255; const k = f < 0 ? 0 : 255, p = Math.abs(f); r = Math.round(r + (k - r) * p); g = Math.round(g + (k - g) * p); b = Math.round(b + (k - b) * p); return `rgb(${r},${g},${b})`; };

function blinkAt(t, seed = 0) { const p = (t + seed * 1.7) % 3.4; return p < 0.12 ? Math.sin(p / 0.12 * Math.PI) : 0; }

function hairPath(style, hx, hy, r, view) {
  c.beginPath();
  if (view === 'front' && style === 'messy') {
    const sp = [[168, 1.0], [182, 1.2], [194, 1.05], [207, 1.3], [220, 1.1], [233, 1.33], [246, 1.12], [259, 1.36], [272, 1.14], [286, 1.34], [299, 1.12], [312, 1.3], [325, 1.08], [338, 1.24], [351, 1.04], [8, 1.0]];
    sp.forEach(([a, f], i) => { const A = a * Math.PI / 180; const x = hx + Math.cos(A) * r * f, y = hy + Math.sin(A) * r * f; i ? c.lineTo(x, y) : c.moveTo(x, y); });
    const bang = [[96, 18], [82, -30], [64, -18], [48, -50], [28, -26], [8, -56], [-14, -28], [-34, -54], [-54, -24], [-74, -44], [-90, -10], [-100, 22]];
    bang.forEach(([x, y]) => c.lineTo(hx + x * r / 100, hy + y * r / 100));
  } else if (view === 'front' && style === 'short') {
    const sp = [[175, 1.0], [195, 1.1], [215, 1.14], [240, 1.16], [265, 1.17], [290, 1.16], [315, 1.14], [340, 1.1], [365, 1.0]];
    sp.forEach(([a, f], i) => { const A = a * Math.PI / 180; const x = hx + Math.cos(A) * r * f, y = hy + Math.sin(A) * r * f; i ? c.lineTo(x, y) : c.moveTo(x, y); });
    [[90, -20], [40, -48], [0, -42], [-40, -50], [-90, -20], [-100, 0]].forEach(([x, y]) => c.lineTo(hx + x * r / 100, hy + y * r / 100));
  } else if (view === 'front' && (style === 'pony' || style === 'long')) {
    c.moveTo(hx - r * 1.05, hy + (style === 'long' ? r * 1.1 : r * 0.2));
    c.bezierCurveTo(hx - r * 1.25, hy - r * 1.3, hx + r * 1.25, hy - r * 1.3, hx + r * 1.05, hy + (style === 'long' ? r * 1.1 : r * 0.2));
    c.lineTo(hx + r * 0.85, hy + r * 0.1); c.quadraticCurveTo(hx + r * 0.5, hy - r * 0.6, hx, hy - r * 0.5); c.quadraticCurveTo(hx - r * 0.5, hy - r * 0.6, hx - r * 0.85, hy + r * 0.1);
  } else if (view === 'front' && style === 'perm') {
    for (let i = 0; i < 14; i++) { const A = Math.PI * (0.95 + i / 13 * 1.1); c.moveTo(hx + Math.cos(A) * r * 1.0 + 38, hy + Math.sin(A) * r * 0.95); c.arc(hx + Math.cos(A) * r * 1.0, hy + Math.sin(A) * r * 0.95, 38, 0, TAU); }
    c.moveTo(hx + r, hy - r * 0.2); c.ellipse(hx, hy - r * 0.35, r * 1.0, r * 0.6, 0, 0, TAU);
  } else if (view === 'front' && style === 'cap') {
    c.moveTo(hx - r * 1.02, hy - r * 0.05); c.bezierCurveTo(hx - r * 1.1, hy - r * 1.25, hx + r * 1.1, hy - r * 1.25, hx + r * 1.02, hy - r * 0.05); c.lineTo(hx + r * 0.9, hy - r * 0.3); c.lineTo(hx - r * 0.9, hy - r * 0.3);
  } else if (view === 'side') {
    const sp = [[318, 1.05], [300, 1.28], [288, 1.12], [272, 1.34], [258, 1.12], [242, 1.32], [228, 1.1], [212, 1.3], [198, 1.08], [184, 1.22], [170, 1.04], [156, 1.12], [140, 0.98]];
    if (style !== 'messy') sp.forEach(s => s[1] = 1 + (s[1] - 1) * 0.35);
    sp.forEach(([a, f], i) => { const A = a * Math.PI / 180; const x = hx + Math.cos(A) * r * f, y = hy + Math.sin(A) * r * f; i ? c.lineTo(x, y) : c.moveTo(x, y); });
    [[-50, 40], [-10, 12], [20, -30], [52, -42], [72, -34]].forEach(([x, y]) => c.lineTo(hx + x * r / 100, hy + y * r / 100));
  } else { // back
    for (let i = 0; i <= 18; i++) { const A = Math.PI * (0.85 + i / 18 * 1.3); const f = i % 2 ? 1.28 : 1.06; const x = hx + Math.cos(A) * r * f, y = hy + Math.sin(A) * r * f; i ? c.lineTo(x, y) : c.moveTo(x, y); }
    c.lineTo(hx + r * 0.95, hy + r * 0.55); c.lineTo(hx + r * 0.4, hy + r * 0.85); c.lineTo(hx, hy + r * 0.7); c.lineTo(hx - r * 0.4, hy + r * 0.88); c.lineTo(hx - r * 0.95, hy + r * 0.55);
    if (style !== 'messy') { c.closePath(); }
  }
  c.closePath();
}

function torsoPath(view, top) {
  c.beginPath();
  const long = top === 'coat' ? 150 : 0;
  if (view === 'side') c.roundRect(-62, -385, 124, 200 + long, [40, 40, 12, 12]);
  else c.roundRect(-97, -385, 194, 200 + long, [46, 46, 14, 14]);
}

function drawTop(d, view) {
  const top = d.top;
  torsoPath(view, top); c.fillStyle = d.c1; c.fill();
  c.save(); torsoPath(view, top); c.clip();
  const x0 = view === 'side' ? -62 : -97, w = view === 'side' ? 124 : 194;
  if (top === 'sweater') {
    rect(x0, -330, w, 46, d.c3);
    c.beginPath(); for (let x = x0 - 20; x < x0 + w + 20; x += 24) { c.moveTo(x, -296); c.lineTo(x + 12, -318); c.lineTo(x + 24, -296); } c.strokeStyle = d.c2; c.lineWidth = 8; c.lineJoin = 'miter'; c.stroke();
    rect(x0, -340, w, 7, d.c2); rect(x0, -281, w, 7, d.c2);
    rect(x0, -208, w, 24, shade(d.c1, -0.25));
    for (let x = x0; x < x0 + w; x += 10) rect(x, -208, 3, 24, shade(d.c1, -0.4));
  } else if (top === 'track') {
    rect(x0, -300, w, 30, d.c2); rect(x0, -262, w, 10, d.c3);
    if (view !== 'side' && view !== 'back') line(0, -380, 0, -190, shade(d.c1, -0.4), 4);
    rect(x0, -204, w, 20, shade(d.c1, -0.3));
  } else if (top === 'jacket') {
    if (view === 'front') { poly([-40, -385, 0, -300, 40, -385, 60, -385, 8, -250, -8, -250, -60, -385], shade(d.c1, -0.3)); line(0, -300, 0, -190, shade(d.c1, -0.45), 4); }
    rect(x0, -205, w, 20, shade(d.c1, -0.3));
  } else if (top === 'coat') {
    if (view === 'front') { line(0, -360, 0, -40, shade(d.c1, -0.35), 4); [-320, -260, -200, -140].forEach(y => circ(14, y, 6, shade(d.c1, -0.5))); }
  } else if (top === 'tshirt') {
    txt('★', 0, -300, 60, d.c2);
  }
  c.restore();
  if (view === 'front') { c.beginPath(); c.ellipse(0, -385, 30, 13, 0, 0, Math.PI); c.fillStyle = shade(d.c1, -0.3); c.fill(); }
}

function drawFaceFront(d, hx, hy) {
  const lx = d.look[0], ly = d.look[1];
  const ex = 34, ey = hy + 8;
  let erx = 11, ery = 17;
  if (d.expr === 'surprised' || d.expr === 'shock') { erx = 13; ery = 21; }
  const blink = d.blink;
  const brow = (side) => {
    let inner = -16, outer = -20;
    if (d.expr === 'worried' || d.expr === 'shock') { inner = -30; outer = -14; }
    if (d.expr === 'surprised') { inner = -30; outer = -30; }
    if (d.expr === 'happy' || d.expr === 'smile') { inner = -22; outer = -24; }
    if (d.expr === 'sleepy') { inner = -12; outer = -12; }
    line(hx + side * 16, hy + inner - 8, hx + side * 52, hy + outer - 8, '#1b1418', 10);
  };
  brow(-1); brow(1);
  const closed = d.expr === 'closed' || d.expr === 'happy' || d.expr === 'yawn';
  [-1, 1].forEach(s => {
    const x = hx + s * ex + lx, y = ey + ly;
    if (closed || blink > 0.85) {
      c.beginPath(); if (d.expr === 'happy') c.arc(x, y + 6, 12, Math.PI * 1.1, Math.PI * 1.9); else c.arc(x, y - 4, 12, Math.PI * 0.15, Math.PI * 0.85);
      c.strokeStyle = '#1b1418'; c.lineWidth = 6; c.lineCap = 'round'; c.stroke();
    } else {
      ell(x, y, erx, ery * (1 - blink), '#141016');
      if (blink < 0.3) circ(x + 4, y - 6, 3.6, 'rgba(255,255,255,.85)');
      if (d.expr === 'sleepy') { rect(x - 16, y - 24, 32, 22, d.skin); line(x - 14, y - 2, x + 14, y - 2, '#1b1418', 5); }
    }
  });
  const my = hy + 52;
  if (d.expr === 'surprised' || d.expr === 'shock') { ell(hx, my, 12, 16 + d.mouthOpen * 6, '#3a1418'); ell(hx, my + 7, 7, 5, '#b8505a'); }
  else if (d.expr === 'yawn') { ell(hx, my, 18, 24, '#3a1418'); ell(hx, my + 10, 11, 7, '#b8505a'); }
  else if (d.expr === 'smile' || d.expr === 'happy') { c.beginPath(); c.arc(hx, my - 10, 22, Math.PI * 0.2, Math.PI * 0.8); c.strokeStyle = '#3a1418'; c.lineWidth = 6; c.lineCap = 'round'; c.stroke(); }
  else if (d.expr === 'worried') { pline([hx - 14, my + 3, hx - 5, my - 3, hx + 5, my + 3, hx + 14, my - 2], '#3a1418', 5); }
  else if (d.mouthOpen > 0.05) { ell(hx, my, 9, 3 + d.mouthOpen * 9, '#3a1418'); }
  else line(hx - 9, my, hx + 9, my, '#3a1418', 5);
  if (d.sweat) { c.beginPath(); c.moveTo(hx + 86, hy - 30); c.quadraticCurveTo(hx + 98, hy - 6, hx + 86, hy - 4); c.quadraticCurveTo(hx + 76, hy - 6, hx + 86, hy - 30); c.fillStyle = '#7ec3ea'; c.fill(); }
}

function person(o) {
  const d = Object.assign({ x: 0, y: 0, s: 1, view: 'front', dir: 1, expr: 'neutral', look: [0, 0], blink: 0, bob: 0, headphones: false, sit: false, mouthOpen: 0, walk: null, tilt: 0, hl: null, hr: null, fl: null, fr: null, hideLegs: false, sweat: false }, HERO, o);
  const v = d.view;
  c.save(); c.translate(d.x, d.y); c.scale(d.s * (v === 'side' ? d.dir : 1), d.s);
  const R = 100, hy = -495;
  const skinS = shade(d.skin, -0.18);
  let fl = d.fl, fr = d.fr, hl = d.hl, hr = d.hr, bob = d.bob;
  if (d.walk !== null) {
    const p = d.walk;
    bob += -Math.abs(Math.sin(p)) * 10;
    if (v === 'side') {
      const a1 = Math.sin(p) * 0.5, a2 = -a1;
      fl = fl || [Math.sin(a1) * 180, -14 - Math.max(0, Math.cos(p)) * 16 - bob];
      fr = fr || [Math.sin(a2) * 180, -14 - Math.max(0, -Math.cos(p)) * 16 - bob];
      hl = hl || [-Math.sin(a1) * 130, -200 + bob * 0];
      hr = hr || [-Math.sin(a2) * 130, -200];
    } else {
      fl = fl || [-34, -14 - Math.max(0, Math.sin(p)) * 26 - bob];
      fr = fr || [34, -14 - Math.max(0, -Math.sin(p)) * 26 - bob];
      hl = hl || [-108 + Math.sin(p) * 10, -190 - Math.max(0, -Math.sin(p)) * 25];
      hr = hr || [108 - Math.sin(p) * 10, -190 - Math.max(0, Math.sin(p)) * 25];
    }
  }
  const sitDrop = d.sit ? 70 : 0;
  if (v === 'side') { fl = fl || [8, -14]; fr = fr || [-8, -14]; hl = hl || [-10, -192]; hr = hr || [16, -190]; }
  else { fl = fl || [-36, -14]; fr = fr || [36, -14]; hl = hl || [-112, -188 + sitDrop]; hr = hr || [112, -188 + sitDrop]; }
  const pantsS = shade(d.pants, -0.25);
  // legs
  if (!d.hideLegs) {
    if (v === 'side') {
      const hip = [0, -195 + bob + sitDrop];
      limb(hip[0], hip[1], fr[0], fr[1], 98, 98, -1, 58, pantsS);
      shoeSide(fr[0], fr[1], d, true);
      limb(hip[0], hip[1], fl[0], fl[1], 98, 98, -1, 58, d.pants);
      shoeSide(fl[0], fl[1], d, false);
    } else if (d.sit) {
      [-1, 1].forEach(s => {
        const f = s < 0 ? fl : fr;
        rr(s * 38 - 34, -152 + bob, 68, 60, 26, d.pants);
        line(s * 38, -112 + bob, f[0], f[1] - 10, d.pants, 56);
        if (v === 'front') shoeFront(f[0], f[1], d);
      });
    } else {
      [-1, 1].forEach(s => {
        const f = s < 0 ? fl : fr;
        const k = limb(s * 36, -195 + bob, f[0], f[1], 98, 98, s < 0 ? 1 : -1, 60, d.pants);
        if (d.acid) { c.globalAlpha = 0.45; line(s * 36 - 8, -180 + bob, (k[0] + s * 36) / 2 - 8, (k[1] - 195 + bob) / 2 + 20, '#d6e2ef', 14); line(k[0] - 6, k[1] + 10, f[0] - 6, f[1] - 40, '#c9d8ea', 10); c.globalAlpha = 1; }
        if (v === 'front') shoeFront(f[0], f[1], d); else shoeFront(f[0], f[1], d, true);
      });
    }
  }
  c.translate(0, bob + sitDrop);
  hl = [hl[0], hl[1] - bob - sitDrop]; hr = [hr[0], hr[1] - bob - sitDrop];
  // back arm (side view)
  const sleeve = d.top === 'tshirt' ? d.skin : d.c1;
  if (v === 'side') { const k = limb(0, -362, hl[0], hl[1], 100, 95, 1, 44, shade(sleeve, -0.25)); circ(k[2], k[3], 22, skinS); }
  drawTop(d, v);
  // neck + head
  rect(-16, -410, 32, 30, skinS);
  c.save(); c.translate(0, -395); c.rotate(d.tilt); c.translate(0, 395);
  if (v === 'front') {
    if (d.hair === 'pony') { ell(0, hy - 120, 34, 44, d.hairCol); }
    if (d.hair === 'long') { rr(-108, hy - 40, 216, 170, 40, d.hairCol); }
    ell(0, hy, R * 1.02, R * 0.98, d.skin);
    hairPath(d.hair, 0, hy, R, 'front'); c.fillStyle = d.hairCol; c.fill();
    if (d.hair === 'cap') { ell(0, hy - 52, 70, 14, shade(d.hairCol, -0.3)); }
    drawFaceFront(d, 0, hy);
  } else if (v === 'side') {
    ell(6, hy, R * 0.96, R * 0.98, d.skin);
    ell(-10, hy + 10, 14, 20, skinS);
    hairPath(d.hair, 6, hy, R, 'side'); c.fillStyle = d.hairCol; c.fill();
    const ex = 58 + d.look[0], ey = hy + 6 + d.look[1];
    if (d.expr === 'closed' || d.expr === 'happy' || d.blink > 0.85) { c.beginPath(); c.arc(ex, ey - 4, 10, Math.PI * 0.15, Math.PI * 0.85); c.strokeStyle = '#1b1418'; c.lineWidth = 6; c.stroke(); }
    else { ell(ex, ey, 10, (d.expr === 'surprised' ? 19 : 16) * (1 - d.blink), '#141016'); circ(ex + 3, ey - 6, 3, 'rgba(255,255,255,.8)'); }
    line(40, hy - 30, 74, hy - 32 - (d.expr === 'surprised' ? 8 : 0), '#1b1418', 9);
    if (d.expr === 'smile' || d.expr === 'happy') { c.beginPath(); c.arc(76, hy + 40, 14, Math.PI * 0.2, Math.PI * 0.75); c.strokeStyle = '#3a1418'; c.lineWidth = 5; c.stroke(); }
    else if (d.expr === 'surprised') ell(84, hy + 50, 7, 10, '#3a1418');
    else line(74, hy + 50, 88, hy + 49, '#3a1418', 5);
  } else {
    ell(0, hy, R * 1.02, R * 0.98, d.skin);
    hairPath(d.hair, 0, hy, R, 'back'); c.fillStyle = d.hairCol; c.fill();
  }
  if (d.headphones) {
    c.beginPath(); c.arc(0, hy + 6, 120, Math.PI * 1.06, Math.PI * 1.94); c.strokeStyle = '#3b3b40'; c.lineWidth = 12; c.stroke();
    if (v === 'side') { ell(-4, hy + 4, 26, 36, '#e8862a'); ell(-4, hy + 4, 14, 22, '#c96a18'); }
    else { ell(-110, hy + 6, 22, 36, '#e8862a'); ell(110, hy + 6, 22, 36, '#e8862a'); }
  }
  c.restore();
  // front arms
  if (v === 'side') { const k = limb(0, -362, hr[0], hr[1], 100, 95, 1, 44, sleeve); trackStripe(d, 0, -362, k); circ(k[2], k[3], 23, d.skin); }
  else {
    const kl = limb(-86, -362, hl[0], hl[1], 100, 95, 1, 44, sleeve); trackStripe(d, -86, -362, kl);
    const kr = limb(86, -362, hr[0], hr[1], 100, 95, -1, 44, sleeve); trackStripe(d, 86, -362, kr);
    if (d.top === 'sweater') { [kl, kr].forEach(k => { const a = Math.atan2(k[3] - k[1], k[2] - k[0]); line(k[2] - Math.cos(a) * 30, k[3] - Math.sin(a) * 30, k[2] - Math.cos(a) * 22, k[3] - Math.sin(a) * 22, shade(d.c1, -0.3), 44, 'butt'); }); }
    circ(kl[2], kl[3], 23, d.skin); circ(kr[2], kr[3], 23, d.skin);
  }
  c.restore();
}
function trackStripe(d, ax, ay, k) { if (d.top !== 'track') return; c.save(); c.beginPath(); c.moveTo(ax, ay); c.lineTo(k[0], k[1]); c.lineTo(k[2], k[3]); c.strokeStyle = d.c2; c.lineWidth = 8; c.lineCap = 'round'; c.lineJoin = 'round'; c.stroke(); c.restore(); }
function shoeFront(x, y, d) { ell(x, y - 4, 40, 19, d.shoes); rect(x - 38, y + 4, 76, 7, '#9a958c'); line(x - 20, y - 10, x + 14, y - 14, d.shoe2, 5); }
function shoeSide(x, y, d, back) { const col = back ? shade(d.shoes, -0.2) : d.shoes; rr(x - 26, y - 22, 74, 30, 14, col); rect(x - 26, y + 2, 74, 7, '#9a958c'); line(x - 8, y - 10, x + 28, y - 14, d.shoe2, 5); }

// palette of 90s outfits for extras
const OUTFITS = [
  { top: 'track', c1: '#1d2a6b', c2: '#f2f2f2', c3: '#d23a3a', pants: '#1d2a6b', acid: false },
  { top: 'jacket', c1: '#3b2a22', c2: '#000', c3: '#000', pants: '#2b2f3a', acid: false },
  { top: 'track', c1: '#7a2c8f', c2: '#29b6b0', c3: '#f2d33b', pants: '#2d2d2d', acid: false },
  { top: 'sweater', c1: '#8c3a3a', c2: '#f1d38a', c3: '#2c4f7c', pants: '#86a3c6', acid: true },
  { top: 'coat', c1: '#6b5a48', c2: '#000', c3: '#000', pants: '#3a3a3a', acid: false },
  { top: 'track', c1: '#16805f', c2: '#fff', c3: '#f2d33b', pants: '#16805f', acid: false },
  { top: 'tshirt', c1: '#e05a8a', c2: '#ffe14d', c3: '#000', pants: '#86a3c6', acid: true },
  { top: 'coat', c1: '#9a3b4a', c2: '#000', c3: '#000', pants: '#3a3a3a', acid: false },
  { top: 'jacket', c1: '#2b2b2f', c2: '#000', c3: '#000', pants: '#86a3c6', acid: true },
];
const HAIRS = [['short', '#3a2a1e'], ['cap', '#c23b3b'], ['perm', '#8a4a22'], ['short', '#16131a'], ['pony', '#c9a25a'], ['perm', '#4a2a1a'], ['short', '#6b4a2a'], ['long', '#2a1a12'], ['cap', '#2b54a8']];
const SKINS = ['#d9a57a', '#e8bd96', '#c98f66', '#f0c9a4'];
function extra(i, o) { const r = rng(i * 31 + 5); const of = OUTFITS[i % OUTFITS.length]; const hr = HAIRS[(i * 5 + 2) % HAIRS.length]; return person(Object.assign({ hair: hr[0], hairCol: hr[1], skin: SKINS[i % 4], shoes: ['#2b2b2b', '#ece7dc', '#5a3a2a'][i % 3], shoe2: '#888' }, of, o)); }

// ---------- props ----------
function crtTV(x, y, w, screen, t, on = true) {
  const h = w * 0.82;
  push(x, y);
  line(w * 0.35, 0, w * 0.12, -h * 0.5, '#2a2a2a', 6); line(w * 0.45, 0, w * 0.75, -h * 0.55, '#2a2a2a', 6); circ(w * 0.12, -h * 0.5, 7, '#555'); circ(w * 0.75, -h * 0.55, 7, '#555');
  ell(w * 0.4, 0, w * 0.14, h * 0.06, '#2b2b2b');
  rr(0, 0, w, h, w * 0.06, '#6b4227'); rr(w * 0.03, h * 0.04, w * 0.94, h * 0.92, w * 0.05, '#7c4e2f');
  rr(w * 0.78, h * 0.08, w * 0.17, h * 0.84, 10, '#3a2b22');
  for (let i = 0; i < 3; i++) { circ(w * 0.865, h * (0.22 + i * 0.2), w * 0.035, '#1e1e1e'); line(w * 0.865, h * (0.22 + i * 0.2), w * 0.865 + Math.cos(i + t * 0) * w * 0.03, h * (0.22 + i * 0.2) - w * 0.02, '#888', 3); }
  for (let i = 0; i < 6; i++) rect(w * 0.81, h * (0.78 + i * 0.022), w * 0.11, 3, '#222');
  const sx = w * 0.07, sy = h * 0.09, sw = w * 0.67, sh = h * 0.8;
  rr(sx - 10, sy - 10, sw + 20, sh + 20, w * 0.07, '#1a1a1a');
  c.save(); c.beginPath(); c.roundRect(sx, sy, sw, sh, w * 0.06); c.clip();
  rect(sx, sy, sw, sh, '#14181a');
  if (on && screen) { push(sx, sy); screen(sw, sh, t); pop(); }
  c.fillStyle = rgrad(sx + sw * 0.5, sy + sh * 0.5, sw * 0.2, sw * 0.75, [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,.6)']]); c.fillRect(sx, sy, sw, sh);
  c.fillStyle = 'rgba(255,255,255,.08)'; c.beginPath(); c.ellipse(sx + sw * 0.3, sy + sh * 0.25, sw * 0.3, sh * 0.15, -0.3, 0, TAU); c.fill();
  for (let yy = sy; yy < sy + sh; yy += 6) rect(sx, yy, sw, 2, 'rgba(0,0,0,.18)');
  c.restore();
  pop();
}
function scrTest(w, h, t) {
  const cols = ['#c0c0c0', '#c0c000', '#00c0c0', '#00c000', '#c000c0', '#c00000', '#0000c0'];
  cols.forEach((col, i) => rect(i * w / 7, 0, w / 7 + 1, h * 0.7, col));
  rect(0, h * 0.7, w, h * 0.3, '#111'); for (let i = 0; i < 6; i++) rect(i * w / 6, h * 0.75, w / 12, h * 0.2, i % 2 ? '#fff' : '#333');
  c.beginPath(); c.arc(w / 2, h / 2, h * 0.38, 0, TAU); c.strokeStyle = '#fff'; c.lineWidth = 5; c.stroke();
  line(w / 2, h * 0.12, w / 2, h * 0.88, '#fff', 3); line(w * 0.2, h / 2, w * 0.8, h / 2, '#fff', 3);
  staticFill(0, 0, w, h, t, 0.12);
}
function scrStatic(w, h, t) { staticFill(0, 0, w, h, t, 1); }
function scrShow(w, h, t) {
  c.fillStyle = grad(0, 0, 0, h, [[0, '#2a3f8f'], [1, '#d24a7a']]); c.fillRect(0, 0, w, h);
  for (let i = 0; i < 8; i++) { const a = t * 0.8 + i * TAU / 8; poly([w / 2, h * 0.55, w / 2 + Math.cos(a) * w, h * 0.55 + Math.sin(a) * w, w / 2 + Math.cos(a + 0.2) * w, h * 0.55 + Math.sin(a + 0.2) * w], 'rgba(255,230,120,.15)'); }
  const bx = w / 2 + Math.sin(t * 2.2) * w * 0.12;
  ell(bx, h * 0.62, w * 0.09, h * 0.22, '#1a1a2a'); circ(bx, h * 0.33, w * 0.07, '#e7b48c'); ell(bx, h * 0.27, w * 0.085, h * 0.08, '#2a1a12');
  line(bx - w * 0.08, h * 0.5, bx - w * 0.16, h * 0.32 + Math.sin(t * 6) * 10, '#1a1a2a', w * 0.04);
  rect(0, h * 0.82, w, h * 0.18, 'rgba(0,0,0,.5)'); txt('ВЕЧЕРНЯЯ ПРОГРАММА', w / 2, h * 0.91, h * 0.08, '#ffe14d', { w: 800 });
  staticFill(0, 0, w, h, t, 0.08);
}

function alarmClock(x, y, s, t, ring, hours) {
  push(x, y, ring ? Math.sin(t * 70) * 0.06 : 0, s);
  line(-55, 60, -75, 95, '#333', 10); line(55, 60, 75, 95, '#333', 10);
  [-1, 1].forEach(k => { push(k * 62, -88, k * 0.5); c.beginPath(); c.arc(0, 0, 40, Math.PI, 0); c.closePath(); c.fillStyle = '#c9c4bb'; c.fill(); rect(-44, -2, 88, 8, '#8d877d'); pop(); });
  line(0, -100, 0, -125, '#777', 8); ell(ring ? Math.sin(t * 90) * 30 : 0, -128, 14, 8, '#999');
  circ(0, 0, 100, '#c43d33'); circ(0, 0, 84, '#f3ead6');
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; line(Math.cos(a) * 70, Math.sin(a) * 70, Math.cos(a) * 78, Math.sin(a) * 78, '#333', i % 3 ? 3 : 6); }
  txt('12', 0, -54, 18, '#333', { w: 700, f: 'DejaVu Serif' });
  const hh = hours !== undefined ? hours : 7 + 3 / 60 + t / 3600, mm = (hh % 1) * 60;
  line(0, 0, Math.cos(hh / 12 * TAU - Math.PI / 2) * 40, Math.sin(hh / 12 * TAU - Math.PI / 2) * 40, '#222', 8);
  line(0, 0, Math.cos(mm / 60 * TAU - Math.PI / 2) * 62, Math.sin(mm / 60 * TAU - Math.PI / 2) * 62, '#222', 5);
  const sa = (hours !== undefined ? hh * 3600 : Math.floor(t)) / 60 * TAU - Math.PI / 2; line(0, 0, Math.cos(sa) * 68, Math.sin(sa) * 68, '#c43d33', 2);
  circ(0, 0, 6, '#222');
  c.fillStyle = 'rgba(255,255,255,.18)'; c.beginPath(); c.ellipse(-30, -35, 40, 22, -0.6, 0, TAU); c.fill();
  pop();
}

function calendar(x, y, s, year, flip, month = 'ЯНВАРЬ', t = 0) {
  push(x, y, 0, s);
  rect(-150, -10, 300, 26, '#7a3a2a'); circ(0, -18, 8, '#444');
  const page = (yr, col) => {
    rect(-140, 10, 280, 380, '#f6efe0');
    rect(-140, 10, 280, 92, col);
    txt(yr, 0, 58, 64, '#fff8e8', { w: 900 });
    txt(month, 0, 128, 30, '#2a2a2a', { w: 800 });
    const days = ['П', 'В', 'С', 'Ч', 'П', 'С', 'В'];
    days.forEach((dd, i) => txt(dd, -105 + i * 35, 165, 17, i > 4 ? '#c43d33' : '#555', { w: 700 }));
    for (let i = 0; i < 31; i++) { const col2 = (i + 6) % 7, row = Math.floor((i + 6) / 7); txt(String(i + 1), -105 + col2 * 35, 200 + row * 34, 19, col2 > 4 ? '#c43d33' : '#333', { w: 600 }); }
  };
  page(year === '1995' ? '2005' : year, '#2b5d8a');
  if (flip !== undefined && flip > 0) {
    const sc = Math.cos(flip * Math.PI);
    c.save(); c.translate(0, 10); c.scale(1, sc); c.translate(0, -10);
    if (sc > 0) page('1995', '#b23a2e'); else { rect(-140, 10, 280, 380, '#e2d8c4'); }
    c.restore();
    alpha(Math.sin(flip * Math.PI) * 0.4, () => rect(-140, 10, 280, 380, '#000'));
  } else if (year === '1995') page('1995', '#b23a2e');
  // red circle around 14
  if (year === '1995' && !(flip > 0)) { c.beginPath(); c.ellipse(-105 + 5 * 35, 200 + 2 * 34, 22, 18, 0, 0, TAU); c.strokeStyle = 'rgba(200,30,30,.8)'; c.lineWidth = 4; c.stroke(); }
  pop();
}

function rotaryPhone(x, y, s, dial, lifted) {
  push(x, y, 0, s);
  poly([-150, 60, 150, 60, 110, -70, -110, -70], '#c63a2e'); rr(-155, 50, 310, 26, 10, '#8f2a22');
  circ(0, 0, 92, '#e8ddc8'); circ(0, 0, 88, '#d9cbb0');
  push(0, 0, dial);
  for (let i = 0; i < 10; i++) { const a = -Math.PI * 0.35 - i * 0.48; circ(Math.cos(a) * 62, Math.sin(a) * 62, 17, '#2a2a2a'); }
  pop();
  for (let i = 0; i < 10; i++) { const a = -Math.PI * 0.35 - i * 0.48; txt(String((i + 1) % 10), Math.cos(a) * 62, Math.sin(a) * 62, 18, '#e8ddc8', { w: 800 }); }
  circ(0, 0, 30, '#f6efe0'); line(68, 30, 88, 50, '#aaa', 6);
  if (!lifted) { rr(-175, -125, 350, 50, 25, '#b0352a'); ell(-150, -95, 46, 32, '#b0352a'); ell(150, -95, 46, 32, '#b0352a'); rect(-30, -78, 60, 12, '#8f2a22'); }
  pop();
}
function coil(x1, y1, x2, y2, col, n = 18, r = 12) {
  c.beginPath(); for (let i = 0; i <= n * 10; i++) { const p = i / (n * 10); const x = lerp(x1, x2, p), yy = lerp(y1, y2, p) + Math.sin(p * Math.PI) * 60; const a = p * n * TAU; const px = x + Math.cos(a) * r, py = yy + Math.sin(a) * r * 0.7; i ? c.lineTo(px, py) : c.moveTo(px, py); }
  c.strokeStyle = col; c.lineWidth = 5; c.stroke();
}
function handset(x, y, s, rot, col = '#b0352a') { push(x, y, rot, s); rr(-26, -110, 52, 220, 26, col); ell(0, -112, 40, 30, col); ell(0, 112, 40, 30, col); pop(); }

function cassette(x, y, s, t, spin = 1, label = 'MIX 95') {
  push(x, y, 0, s);
  rr(-200, -125, 400, 250, 14, '#2b2b30'); rr(-180, -105, 360, 150, 8, '#f2ead6');
  rect(-180, -105, 360, 32, '#e05a3a'); rect(-180, -73, 360, 10, '#f2b53a');
  txt(label, -60, -24, 26, '#333', { w: 800, f: 'DejaVu Sans' }); txt('C-90', 120, -24, 20, '#333', { w: 700 });
  rr(-110, -10, 220, 56, 26, '#1a1a1a'); rr(-100, -2, 200, 40, 20, '#5a4030');
  [-60, 60].forEach((cx, i) => { circ(cx, 18, 24, '#e8e8e8'); push(cx, 18, t * spin * (i ? 3.1 : 3.4)); for (let k = 0; k < 6; k++) { push(0, 0, k * TAU / 6); rect(-3, -18, 6, 9, '#333'); pop(); } circ(0, 0, 8, '#333'); pop(); });
  poly([-150, 125, 150, 125, 125, 75, -125, 75], '#3a3a40'); [-80, -30, 30, 80].forEach(xx => circ(xx, 100, 8, '#1a1a1a'));
  pop();
}
function walkman(x, y, s, t, lid = 0, cas = false, playing = false) {
  push(x, y, 0, s);
  rr(-230, -160, 460, 320, 26, '#c9ccd2'); rr(-230, -160, 460, 40, [26, 26, 0, 0], '#a9adb5');
  ['◀◀', '▶', '▶▶', '■', '⏏'].forEach((b, i) => { rr(-215 + i * 88, -205 + (playing && i === 1 ? 10 : 0), 76, 50, 8, i === 1 ? '#e05a3a' : '#5a5e66'); txt(b, -177 + i * 88, -180 + (playing && i === 1 ? 10 : 0), 22, '#fff', { w: 700, f: 'DejaVu Sans' }); });
  rr(-200, -110, 400, 250, 18, '#1d1f24');
  if (cas) { c.save(); c.beginPath(); c.roundRect(-195, -105, 390, 240, 16); c.clip(); cassette(0, 15, 0.95, t, playing ? 1 : 0); c.restore(); }
  push(0, -110); c.scale(1, 1 - lid * 1.6); alpha(0.55, () => rr(-200, 0, 400, 250, 18, '#7d8a99')); rr(-200, 0, 400, 250, 18, null, '#9aa3ad', 6); if (lid < 0.5) txt('STEREO CASSETTE PLAYER', 0, 220, 20, '#e8e8e8', { w: 700 }); pop();
  txt('AUTO REVERSE', 120, -138, 16, '#333', { w: 800 });
  pop();
}

function radio(x, y, s, t) {
  push(x, y, 0, s);
  rr(-260, -150, 520, 300, 30, '#7a4a2a'); rr(-240, -130, 300, 260, 16, '#c9b38a');
  for (let yy = -115; yy < 120; yy += 12) rect(-232, yy, 284, 5, '#8a7350');
  const pulse = 1 + Math.sin(t * 12) * 0.03;
  push(-90, 0, 0, pulse); c.beginPath(); c.arc(0, 0, 95, 0, TAU); c.strokeStyle = 'rgba(60,40,20,.35)'; c.lineWidth = 6; c.stroke(); pop();
  rr(80, -120, 160, 110, 10, '#f1e6c8'); for (let i = 0; i < 8; i++) line(92 + i * 19, -60, 92 + i * 19, -48, '#555', 2);
  txt('УКВ', 160, -100, 16, '#555', { w: 800 }); txt('66 · 70 · 74', 160, -78, 13, '#555', { w: 600 });
  const nx = 100 + (Math.sin(t * 0.9) * 0.5 + 0.5) * 120; line(nx, -112, nx, -18, '#c4302a', 4);
  circ(115, 55, 36, '#3a2a1e'); circ(205, 55, 36, '#3a2a1e'); line(115, 55, 115 + Math.cos(t) * 28, 55 + Math.sin(t) * 28, '#ccc', 4); line(205, 55, 205, 25, '#ccc', 4);
  line(200, -150, 330, -330, '#999', 5); circ(330, -330, 7, '#aaa');
  pop();
}
function notes(x, y, t, n = 6, spread = 300, col = '#ffe7a0') {
  for (let i = 0; i < n; i++) { const p = (t * 0.45 + i / n) % 1; const xx = x + Math.sin(p * 6 + i) * 40 + (hash(i) - 0.5) * spread; const yy = y - p * 320; alpha(Math.sin(p * Math.PI), () => { push(xx, yy, Math.sin(t * 3 + i) * 0.3); txt(i % 2 ? '♪' : '♫', 0, 0, 64, col, { w: 400, f: 'DejaVu Sans' }); pop(); }); }
}
function kettle(x, y, s, t) {
  push(x, y, 0, s);
  c.beginPath(); c.moveTo(-110, 0); c.quadraticCurveTo(-125, -150, -60, -170); c.lineTo(60, -170); c.quadraticCurveTo(125, -150, 110, 0); c.closePath(); c.fillStyle = '#e9e4da'; c.fill();
  rect(-110, -16, 220, 16, '#c43d33'); ell(0, -172, 62, 14, '#c43d33'); circ(0, -192, 14, '#222');
  pline([-70, -170, -60, -245, 60, -245, 70, -170], '#222', 10);
  poly([100, -60, 200, -150, 214, -138, 112, -30], '#e9e4da');
  [[-40, -80, '#c43d33'], [10, -100, '#e0a43a'], [40, -60, '#c43d33']].forEach(([fx, fy, col]) => { for (let k = 0; k < 5; k++) circ(fx + Math.cos(k * 1.26) * 12, fy + Math.sin(k * 1.26) * 12, 8, col); circ(fx, fy, 6, '#3a7a3a'); });
  for (let i = 0; i < 9; i++) { const p = (t * 0.6 + i / 9) % 1; alpha((1 - p) * 0.5, () => circ(214 + p * 60 + Math.sin(p * 8 + i) * 20, -150 - p * 260, 18 + p * 40, '#ffffff')); }
  pop();
}
function teaGlass(x, y, s, t) {
  push(x, y, 0, s);
  rr(-42, -110, 84, 110, 6, 'rgba(160,70,20,.85)'); rr(-42, -126, 84, 20, 4, 'rgba(255,255,255,.35)');
  rr(-50, -70, 100, 74, 8, '#b8a36a'); for (let i = 0; i < 5; i++) rect(-44 + i * 20, -62, 8, 58, '#8d7a44');
  pline([50, -60, 80, -55, 80, -15, 50, -10], '#b8a36a', 10);
  line(20, -110, 46, -170, '#ccc', 5);
  for (let i = 0; i < 4; i++) { const p = (t * 0.5 + i / 4) % 1; alpha((1 - p) * 0.35, () => circ(Math.sin(p * 7 + i) * 15, -130 - p * 120, 10 + p * 18, '#fff')); }
  pop();
}
function newspaper(x, y, s, rot) {
  push(x, y, rot, s);
  rect(-260, -170, 520, 340, '#e6e0d0'); rect(-260, -170, 520, 340, 'rgba(0,0,0,0)');
  txt('НОВОСТИ ДНЯ', 0, -128, 52, '#1a1a1a', { w: 900, f: 'DejaVu Serif' });
  line(-240, -96, 240, -96, '#333', 3); txt('№ 14 · 14 ЯНВАРЯ 1995 г. · ЦЕНА 300 руб.', 0, -82, 14, '#333', { w: 600 });
  txt('В ГОРОДЕ ОТКРЫЛСЯ НОВЫЙ РЫНОК', -40, -50, 20, '#222', { w: 900 });
  rect(-240, -32, 200, 140, '#a9a395'); circ(-140, 20, 36, '#7f796c'); rect(-180, 50, 80, 50, '#7f796c');
  for (let i = 0; i < 9; i++) rect(-20, -30 + i * 16, 250, 6, '#9e9789');
  for (let i = 0; i < 3; i++) rect(-240, 120 + i * 14, 470, 6, '#9e9789');
  pop();
}

function car(x, y, s, col, t, dir = 1, kind = 0) {
  push(x, y, 0, s * dir, s);
  const wob = Math.sin(t * 20) * 1.5;
  c.translate(0, wob);
  if (kind === 1) { // hatch / old compact
    c.beginPath(); c.moveTo(-200, -40); c.lineTo(-200, -100); c.lineTo(-120, -110); c.lineTo(-80, -175); c.lineTo(110, -175); c.lineTo(170, -110); c.lineTo(215, -100); c.lineTo(215, -40); c.closePath(); c.fillStyle = col; c.fill();
    poly([-68, -165, 40, -165, 40, -115, -105, -115], '#a9c4d6'); poly([52, -165, 102, -165, 150, -115, 52, -115], '#a9c4d6');
  } else { // boxy sedan
    c.beginPath(); c.moveTo(-250, -40); c.lineTo(-250, -105); c.lineTo(-130, -112); c.lineTo(-85, -180); c.lineTo(95, -180); c.lineTo(145, -112); c.lineTo(250, -105); c.lineTo(250, -40); c.closePath(); c.fillStyle = col; c.fill();
    poly([-74, -170, 2, -170, 2, -118, -112, -118], '#a9c4d6'); poly([14, -170, 88, -170, 128, -118, 14, -118], '#a9c4d6');
  }
  rect(-250, -75, 500, 8, shade(col, -0.25)); rect(240, -98, 14, 18, '#ffe9a0'); rect(-254, -98, 12, 18, '#d33');
  rr(-262, -48, 524, 14, 6, '#bdbdbd');
  [-150, 150].forEach(wx => { circ(wx, -30, 42, '#1b1b1b'); circ(wx, -30, 22, '#c9c9c9'); push(wx, -30, t * 8); line(-18, 0, 18, 0, '#777', 4); line(0, -18, 0, 18, '#777', 4); pop(); });
  pop();
}
function bus(x, y, s, t, dir = 1) {
  push(x, y, 0, s * dir, s);
  rr(-380, -290, 760, 260, 30, '#e3b23c'); rect(-380, -150, 760, 26, '#c43d33');
  for (let i = 0; i < 6; i++) rr(-350 + i * 115, -265, 100, 90, 8, '#a9c4d6');
  [-250, 250].forEach(wx => { circ(wx, -30, 46, '#1b1b1b'); circ(wx, -30, 22, '#888'); });
  pop();
}
function bike(x, y, s, t, col = '#2a7ac4', speed = 8) {
  push(x, y, 0, s);
  [-120, 120].forEach(wx => { c.beginPath(); c.arc(wx, -70, 70, 0, TAU); c.strokeStyle = '#1b1b1b'; c.lineWidth = 10; c.stroke(); push(wx, -70, t * speed); for (let k = 0; k < 8; k++) line(0, 0, Math.cos(k * TAU / 8) * 64, Math.sin(k * TAU / 8) * 64, '#aaa', 2); pop(); circ(wx, -70, 7, '#666'); });
  pline([-120, -70, -20, -70, 50, -160, -50, -160, -20, -70], col, 12); line(50, -160, 120, -70, col, 12); line(-50, -160, -60, -185, col, 10); rr(-90, -195, 70, 16, 8, '#222');
  line(50, -160, 60, -205, '#555', 8); line(40, -205, 85, -205, '#222', 10);
  circ(-20, -70, 16, '#555');
  pop();
}
function rider(x, y, s, t, i, speed = 8, expr = 'smile') {
  const crank = t * speed;
  const pedal = (ph) => [-20 + Math.cos(crank + ph) * 34, -70 + Math.sin(crank + ph) * 34];
  push(x, y, 0, s);
  bike(0, 0, 1, t, ['#2a7ac4', '#c43d33', '#3a9a5a'][i % 3], speed);
  const pa = pedal(0), pb = pedal(Math.PI);
  // seat at (-55,-195)
  const o = { x: -55, y: -195 + 195, view: 'side', dir: 1, s: 1, expr, hideLegs: true, hl: [60 - 55 + 55, -205 + 195], hr: [80 + 0, -200 + 195] };
  // legs drawn manually
  const P = i === -1 ? HERO : Object.assign({}, HERO, OUTFITS[i % OUTFITS.length]);
  c.save(); c.translate(-55, 0);
  const pants = P.pants;
  limb(0, -195, pb[0] + 55, pb[1], 98, 98, -1, 50, shade(pants, -0.25));
  limb(0, -195, pa[0] + 55, pa[1], 98, 98, -1, 50, pants);
  c.restore();
  push(-55, -150, 0.25); const extraO = i === -1 ? {} : (() => { const hr = HAIRS[(i * 5 + 2) % HAIRS.length]; return Object.assign({ hair: hr[0], hairCol: hr[1], skin: SKINS[i % 4] }, OUTFITS[i % OUTFITS.length]); })();
  person(Object.assign({ x: 0, y: 195 - 195 + 195 - 45, view: 'side', dir: 1, expr, hideLegs: true, hl: [100, -330], hr: [118, -322], blink: blinkAt(t, i) }, extraO));
  pop();
  pop();
}

function panel(x, y, w, h, col, t, litFn, seed = 1) {
  rect(x, y - h, w, h, col);
  const cols = Math.floor(w / 70), rows = Math.floor(h / 80);
  for (let r = 0; r < rows; r++) for (let k = 0; k < cols; k++) {
    const wx = x + 22 + k * (w - 30) / cols, wy = y - h + 26 + r * (h - 20) / rows;
    const lit = litFn ? litFn(r, k) : false;
    rect(wx, wy, 34, 42, lit ? '#ffd27a' : '#5d6f7f');
    if (!lit) rect(wx, wy, 34, 10, 'rgba(255,255,255,.12)');
    if ((r + k * 3 + seed) % 7 === 0) rect(wx - 6, wy + 34, 46, 18, shade(col, -0.15));
  }
  for (let r = 1; r < rows; r++) rect(x, y - h + r * (h - 20) / rows + 12, w, 2, 'rgba(0,0,0,.08)');
}
function kiosk(x, y, w, h, sign, col, t) {
  rect(x, y - h, w, h, col); rect(x - 10, y - h - 50, w + 20, 54, shade(col, -0.25)); txt(sign, x + w / 2, y - h - 23, 30, '#fff3c4', { w: 900 });
  rect(x + 14, y - h + 16, w - 28, h * 0.5, '#bcd2dd');
  for (let i = 0; i < 6; i++) rect(x + 24 + i * (w - 48) / 6, y - h + 30 + (i % 2) * 30, (w - 60) / 7, 40, ['#e05a3a', '#f2d33b', '#3a9ad9', '#7ad93a', '#d93a9a', '#fff'][i]);
  rect(x + 14, y - h + 16, w - 28, 4, 'rgba(255,255,255,.4)');
  rect(x + w / 2 - 30, y - h * 0.38, 60, 30, '#333');
}
function stall(x, y, w, cols, goods, t, seed) {
  for (let i = 0; i < w / 50; i++) rect(x + i * 50, y - 300, 50, 70, cols[i % 2]);
  for (let i = 0; i < w / 50; i++) { c.beginPath(); c.arc(x + i * 50 + 25, y - 230, 25, 0, Math.PI); c.fillStyle = cols[i % 2]; c.fill(); }
  line(x + 6, y - 300, x + 6, y, '#555', 8); line(x + w - 6, y - 300, x + w - 6, y, '#555', 8);
  rect(x, y - 110, w, 110, '#8a6a46'); rect(x, y - 110, w, 12, '#6a4a2a');
  const r = rng(seed);
  for (let i = 0; i < w / 34; i++) for (let j = 0; j < 2; j++) circ(x + 20 + i * 34 + j * 14, y - 124 - j * 22, 18, goods[Math.floor(r() * goods.length)]);
}
function tree(x, y, s, col = '#3f7a3a', t = 0) {
  push(x, y, 0, s); rect(-14, -160, 28, 160, '#6b4a2e');
  const sw = Math.sin(t * 1.5 + x) * 4;
  [[0, -240, 110], [-70, -200, 80], [70, -200, 80], [0, -320, 80]].forEach(([a, b, r]) => circ(a + sw, b, r, col));
  [[-30, -270, 40], [40, -240, 35]].forEach(([a, b, r]) => circ(a + sw, b, r, shade(col, 0.12)));
  pop();
}
function bench(x, y, s) { push(x, y, 0, s); rect(-150, -70, 300, 16, '#6b8a3a'); rect(-150, -100, 300, 14, '#6b8a3a'); rect(-150, -126, 300, 14, '#6b8a3a'); rect(-140, -70, 14, 70, '#444'); rect(126, -70, 14, 70, '#444'); pop(); }

function sky(top, bot) { c.fillStyle = grad(0, -300, 0, 900, [[0, top], [1, bot]]); c.fillRect(-1500, -1500, 5000, 4000); }

// ---------- camera ----------
function cam(p, a, b, shake = 1, t = 0) {
  const cx = lerp(a[0], b[0], p), cy = lerp(a[1], b[1], p), z = lerp(a[2], b[2], p), rot = lerp(a[3] || 0, b[3] || 0, p);
  const sx = (Math.sin(t * 1.3) + Math.sin(t * 2.7) * 0.5) * 4 * shake, sy = (Math.cos(t * 1.1) + Math.sin(t * 3.1) * 0.5) * 3 * shake;
  c.translate(W / 2, H / 2); c.rotate(rot + Math.sin(t * 0.9) * 0.002 * shake); c.scale(z, z); c.translate(-cx + sx, -cy + sy);
}
