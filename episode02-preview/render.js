// HUMAN MIND — Episode 02 — vertical 9:16 preview renderer.
// Usage: node render.js <startFrame> <endFrame> <out.mp4>    (renders video only)
//        node render.js --still <time|cover> <out.png>
const { createCanvas, GlobalFonts, Path2D } = require('@napi-rs/canvas');
const { spawn } = require('child_process');
const T = require('./timeline');
const { FPS, clamp, seg, TREE_X, REVEAL } = T;

const W = 1080, H = 1920;
const FONT_DIR = '/usr/share/fonts/opentype/inter/';
GlobalFonts.registerFromPath(FONT_DIR + 'Inter-Black.otf', 'InterBlack');
GlobalFonts.registerFromPath(FONT_DIR + 'Inter-Bold.otf', 'InterBold');
GlobalFonts.registerFromPath(FONT_DIR + 'Inter-SemiBold.otf', 'InterSemi');
GlobalFonts.registerFromPath(FONT_DIR + 'Inter-Medium.otf', 'InterMedium');

const canvas = createCanvas(W, H);
const ctx = canvas.getContext('2d');

// ---------- helpers ----------
const lerp = (a, b, k) => a + (b - a) * k;
const ease = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
const easeOut = (k) => 1 - Math.pow(1 - k, 3);
const easeBack = (k) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); };
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
const win = (t, a, b, fi = 0.35, fo = 0.35) => Math.min(seg(t, a, a + fi), 1 - seg(t, b - fo, b));

function glow(blur, alpha = 1) { ctx.shadowColor = `rgba(255,255,255,${alpha})`; ctx.shadowBlur = blur; }
function noGlow() { ctx.shadowBlur = 0; ctx.shadowColor = 'transparent'; }

// ---------- background ----------
const R = rng(7);
const particles = Array.from({ length: 70 }, () => ({ x: R() * W, y: R() * H, r: 0.8 + R() * 2.2, s: 4 + R() * 14, a: 0.15 + R() * 0.45, p: R() * 6.28 }));

function background(t, brightness = 1) {
  ctx.fillStyle = '#030303';
  ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W / 2, H * 0.45, 50, W / 2, H * 0.45, H * 0.75);
  g.addColorStop(0, `rgba(40,40,40,${0.9 * brightness})`);
  g.addColorStop(0.5, `rgba(16,16,16,${0.9 * brightness})`);
  g.addColorStop(1, 'rgba(0,0,0,1)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  // dot grid
  ctx.fillStyle = `rgba(255,255,255,${0.07 * brightness})`;
  for (let y = 24; y < H; y += 48) for (let x = 24; x < W; x += 48) ctx.fillRect(x, y, 2, 2);
  // particles
  for (const p of particles) {
    const y = (p.y - t * p.s + H * 10) % H;
    const x = p.x + Math.sin(t * 0.4 + p.p) * 12;
    ctx.fillStyle = `rgba(255,255,255,${p.a * brightness * (0.6 + 0.4 * Math.sin(t * 1.3 + p.p))})`;
    ctx.beginPath(); ctx.arc(x, y, p.r, 0, 6.283); ctx.fill();
  }
}

function vignette(strength) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.72);
  g.addColorStop(0, 'rgba(0,0,0,0)');
  g.addColorStop(1, `rgba(0,0,0,${strength})`);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
}

// ---------- camera ----------
// keys: [time, worldX, worldY, zoom] — world point (x,y) is placed at screen (W/2, H/2).
const CAM = [
  [0.0, 330, -190, 2.15],
  [2.35, 330, -195, 2.5],
  [3.7, 20, -330, 1.0],
  [6.0, 90, -320, 1.05],
  [8.0, 110, -300, 1.12],
  [11.6, 210, -230, 1.6],
  [12.4, 240, -330, 1.22],
  [14.8, 240, -335, 1.2],
  [16.2, 200, -470, 0.88],
  [21.5, 200, -480, 0.84],
];
function camAt(t) {
  for (let i = 0; i < CAM.length - 1; i++) {
    const [t0, x0, y0, z0] = CAM[i], [t1, x1, y1, z1] = CAM[i + 1];
    if (t <= t1) { const k = ease(seg(t, t0, t1)); return { x: lerp(x0, x1, k), y: lerp(y0, y1, k), z: lerp(z0, z1, k) }; }
  }
  const l = CAM[CAM.length - 1]; return { x: l[1], y: l[2], z: l[3] };
}
function applyCam(c) { ctx.translate(W / 2, H / 2); ctx.scale(c.z, c.z); ctx.translate(-c.x, -c.y); }
function toScreen(c, x, y) { return [(x - c.x) * c.z + W / 2, (y - c.y) * c.z + H / 2]; }

// ---------- stickman ----------
// x = feet center, y = ground. Height ≈ 235 * s.
function drawMan(x, y, s, o = {}) {
  const { phase = 0, walk = 0, lean = 0, tremble = 0, relax = 0, alpha = 1, color = '#ffffff', glowAmt = 1, lookUp = 0 } = o;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.translate(x, y);
  ctx.scale(s, s);
  const bob = -Math.abs(Math.sin(phase)) * 5 * walk + Math.sin(tremble * 61) * 1.6 * (tremble > 0 ? 1 : 0);
  ctx.translate(0, bob);
  ctx.strokeStyle = color; ctx.fillStyle = color;
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  glow(26 * glowAmt, 0.75);
  const hipY = -92, shY = -165 + relax * 4;
  // legs
  ctx.lineWidth = 17;
  const la = Math.sin(phase) * 0.46 * walk;
  for (const sgn of [1, -1]) {
    const a = la * sgn;
    const kx = Math.sin(a) * 46, ky = hipY + Math.cos(a) * 46;
    const fa = a - Math.max(0, -Math.sin(phase * sgn)) * 0.5 * walk;
    ctx.beginPath(); ctx.moveTo(0, hipY); ctx.lineTo(kx, ky); ctx.lineTo(kx + Math.sin(fa) * 46, ky + Math.cos(fa) * 46 - 0); ctx.stroke();
  }
  // torso (leans)
  ctx.save();
  ctx.rotate(lean);
  ctx.beginPath();
  ctx.moveTo(-26, hipY + 6);
  ctx.lineTo(-30, shY + 18);
  ctx.quadraticCurveTo(-30, shY - 4, -10, shY - 6);
  ctx.lineTo(10, shY - 6);
  ctx.quadraticCurveTo(30, shY - 4, 30, shY + 18);
  ctx.lineTo(26, hipY + 6);
  ctx.closePath(); ctx.fill();
  // arms
  ctx.lineWidth = 14;
  const aa = -Math.sin(phase) * 0.4 * walk;
  for (const sgn of [1, -1]) {
    const a = aa * sgn + (tremble > 0 ? 0.25 * sgn * 0 : 0);
    const ex = sgn * 30 + Math.sin(a) * 40, ey = shY + 10 + Math.cos(a) * 40;
    const ha = a + 0.25 * walk + (1 - relax) * 0;
    ctx.beginPath(); ctx.moveTo(sgn * 28, shY + 10); ctx.lineTo(ex, ey); ctx.lineTo(ex + Math.sin(ha) * 36, ey + Math.cos(ha) * 36); ctx.stroke();
  }
  // head
  ctx.beginPath(); ctx.arc(4 * lookUp, shY - 38 - lookUp * 3, 27, 0, 6.283); ctx.fill();
  ctx.restore();
  noGlow();
  ctx.restore();
}

// ---------- silhouette / tree (morph m: 0 = human figure, 1 = tree) ----------
function drawFigure(x, y, s, m, o = {}) {
  const { lit = 0, alpha = 1, dashed = false } = o;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.translate(x, y); ctx.scale(s, s);
  const shade = Math.round(lerp(58, 235, lit));
  const col = `rgb(${shade},${shade},${shade})`;
  ctx.fillStyle = col; ctx.strokeStyle = col;
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  glow(lerp(18, 34, lit), lerp(0.25, 0.7, lit));
  if (dashed) { ctx.fillStyle = 'rgba(0,0,0,0)'; ctx.setLineDash([10, 12]); }

  // trunk / body
  const topY = lerp(-175, -250, m);
  const baseW = lerp(26, 44, m), topW = lerp(30, 14, m);
  ctx.beginPath();
  ctx.moveTo(-baseW - m * 22, 0);
  ctx.quadraticCurveTo(-baseW * 0.6, -30, -topW * 0.8, topY * 0.55);
  ctx.lineTo(-topW, topY);
  ctx.lineTo(topW, topY);
  ctx.lineTo(topW * 0.8, topY * 0.55);
  ctx.quadraticCurveTo(baseW * 0.6, -30, baseW + m * 22, 0);
  ctx.closePath();
  if (!dashed) ctx.fill(); else { ctx.lineWidth = 4; ctx.stroke(); }
  // legs gap (human): dark notch fading out as it becomes a trunk
  if (!dashed && m < 1) {
    ctx.save(); ctx.globalAlpha = alpha * (1 - m);
    ctx.strokeStyle = '#050505'; noGlow(); ctx.lineWidth = 7;
    ctx.beginPath(); ctx.moveTo(0, 2); ctx.lineTo(0, -78); ctx.stroke(); ctx.restore();
    glow(lerp(18, 34, lit), lerp(0.25, 0.7, lit));
  }
  // shoulders (human) -> fade
  if (m < 1) {
    ctx.save(); ctx.globalAlpha = alpha * (1 - m);
    ctx.beginPath(); ctx.ellipse(0, -165, 36, 20, 0, 0, 6.283);
    if (!dashed) ctx.fill(); else { ctx.lineWidth = 4; ctx.stroke(); }
    ctx.restore();
  }
  // arms -> branches
  ctx.lineWidth = lerp(15, 11, m);
  const branches = [
    { y: -160, side: -1, a0: 0.12, a1: -0.95, l0: 120, l1: 150 },
    { y: -160, side: 1, a0: 0.12, a1: -0.85, l0: 120, l1: 165 },
    { y: -215, side: -1, a0: 0.0, a1: -0.55, l0: 0, l1: 110 },
    { y: -225, side: 1, a0: 0.0, a1: -0.45, l0: 0, l1: 95 },
  ];
  for (const b of branches) {
    const len = lerp(b.l0, b.l1, m); if (len < 2) continue;
    // angle measured from straight down (0) rotating outward; a1 negative = pointing up-out
    const ang = lerp(b.a0, b.a1 + Math.PI, ease(m));
    const sx = b.side * lerp(30, 8, m), sy = b.y;
    const ex = sx + b.side * Math.sin(ang) * len, ey = sy + Math.cos(ang) * len;
    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
    if (m > 0.3) { // twigs
      const k = seg(m, 0.3, 1);
      ctx.save(); ctx.lineWidth = 6;
      for (const tw of [0.55, 0.8]) {
        const px = lerp(sx, ex, tw), py = lerp(sy, ey, tw);
        ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px + b.side * 40 * k, py - 46 * k); ctx.stroke();
      }
      ctx.restore();
    }
  }
  // head -> canopy
  const blobs = [
    [0, -215, 27, 0, -330, 92],
    [0, -215, 0, -95, -300, 70],
    [0, -215, 0, 100, -295, 72],
    [0, -215, 0, -55, -400, 66],
    [0, -215, 0, 60, -405, 70],
    [0, -215, 0, 0, -455, 60],
    [0, -215, 0, -140, -365, 48],
    [0, -215, 0, 145, -360, 50],
  ];
  const mk = easeOut(m);
  ctx.beginPath();
  for (const [x0, y0, r0, x1, y1, r1] of blobs) {
    const r = lerp(r0, r1, mk); if (r < 1) continue;
    const cx = lerp(x0, x1, mk), cy = lerp(y0, y1, mk);
    ctx.moveTo(cx + r, cy); ctx.arc(cx, cy, r, 0, 6.283);
  }
  if (!dashed) {
    ctx.globalAlpha = alpha * lerp(1, 0.9, m);
    ctx.fill();
    // leaf texture when lit
    if (lit > 0.05 && m > 0.5) {
      noGlow(); ctx.globalAlpha = alpha * lit * 0.22;
      ctx.fillStyle = '#0a0a0a';
      const r2 = rng(99);
      for (let i = 0; i < 22; i++) {
        const a = r2() * 6.283, d = r2() * 120;
        const cx = Math.cos(a) * d * 1.3, cy = -360 + Math.sin(a) * d * 0.75;
        ctx.beginPath(); ctx.ellipse(cx, cy, 9, 5, a, 0, 6.283); ctx.fill();
      }
    }
  } else { ctx.lineWidth = 4; ctx.stroke(); }
  ctx.setLineDash([]);
  noGlow();
  ctx.restore();
}

// ---------- street props ----------
function drawLamp(x, on, flick) {
  ctx.save();
  ctx.strokeStyle = 'rgba(200,200,200,0.55)'; ctx.lineWidth = 7; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, -430); ctx.quadraticCurveTo(x, -470, x - 40, -470); ctx.lineTo(x - 70, -470); ctx.stroke();
  const a = on * flick;
  if (a > 0.01) {
    const g = ctx.createRadialGradient(x - 70, -460, 4, x - 70, -460, 140);
    g.addColorStop(0, `rgba(255,255,255,${0.9 * a})`); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x - 70, -460, 140, 0, 6.283); ctx.fill();
    // light cone
    const cg = ctx.createLinearGradient(0, -460, 0, 0);
    cg.addColorStop(0, `rgba(255,255,255,${0.16 * a})`); cg.addColorStop(1, `rgba(255,255,255,${0.03 * a})`);
    ctx.fillStyle = cg;
    ctx.beginPath(); ctx.moveTo(x - 90, -460); ctx.lineTo(x - 50, -460); ctx.lineTo(x + 200, 0); ctx.lineTo(x - 340, 0); ctx.closePath(); ctx.fill();
    ctx.fillStyle = `rgba(255,255,255,${a})`; glow(30, a);
    ctx.beginPath(); ctx.ellipse(x - 70, -462, 22, 8, 0, 0, 6.283); ctx.fill(); noGlow();
  } else {
    ctx.fillStyle = 'rgba(120,120,120,0.6)'; ctx.beginPath(); ctx.ellipse(x - 70, -462, 22, 8, 0, 0, 6.283); ctx.fill();
  }
  ctx.restore();
}

function drawGround(c) {
  const [, gy] = toScreen(c, 0, 0);
  if (gy > H + 10) return;
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.55)'; ctx.lineWidth = 3;
  ctx.setLineDash([26, 16]);
  ctx.lineDashOffset = c.x * c.z;
  ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
}

// ---------- brain ----------
function brainPath() {
  // stylised brain outline + folds, local coords ~ 360 x 260, centered at 0,0
  const p = [];
  const outline = new Path2D();
  const N = 90;
  for (let i = 0; i <= N; i++) {
    const a = (i / N) * Math.PI * 2;
    const r = 1 + 0.06 * Math.sin(a * 9) + 0.03 * Math.sin(a * 17 + 1);
    const x = Math.cos(a) * 180 * r;
    let y = Math.sin(a) * 125 * r;
    if (y > 0) y *= 0.85; // flatter bottom
    if (i === 0) outline.moveTo(x, y); else outline.lineTo(x, y);
  }
  outline.closePath();
  p.push(outline);
  const folds = new Path2D();
  folds.moveTo(0, -120); folds.bezierCurveTo(-20, -60, 20, -20, 0, 40); folds.bezierCurveTo(-15, 70, 10, 90, 0, 105);
  folds.moveTo(-150, -30); folds.bezierCurveTo(-110, -70, -80, -10, -40, -50);
  folds.moveTo(-140, 40); folds.bezierCurveTo(-100, 0, -70, 60, -30, 30);
  folds.moveTo(150, -30); folds.bezierCurveTo(110, -70, 80, -10, 40, -50);
  folds.moveTo(140, 40); folds.bezierCurveTo(100, 0, 70, 60, 30, 30);
  folds.moveTo(-90, -100); folds.bezierCurveTo(-70, -70, -50, -100, -30, -80);
  folds.moveTo(90, -100); folds.bezierCurveTo(70, -70, 50, -100, 30, -80);
  p.push(folds);
  return p;
}
const BRAIN = brainPath();
function drawBrain(x, y, s, reveal, pulse = 0, alpha = 1) {
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.translate(x, y); ctx.scale(s * (1 + pulse * 0.03), s * (1 + pulse * 0.03));
  ctx.strokeStyle = '#fff'; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  glow(22 + pulse * 20, 0.9);
  ctx.lineWidth = 6;
  ctx.setLineDash([1400 * reveal, 3000]);
  ctx.stroke(BRAIN[0]);
  ctx.lineWidth = 5;
  ctx.setLineDash([1000 * seg(reveal, 0.3, 1), 3000]);
  ctx.stroke(BRAIN[1]);
  ctx.setLineDash([]);
  // inner soft fill
  ctx.globalAlpha = alpha * 0.08 * reveal; ctx.fillStyle = '#fff'; ctx.fill(BRAIN[0]);
  noGlow(); ctx.restore();
}

// ---------- signal line with travelling pulses ----------
function signalLine(x0, y0, x1, y1, k, t, alpha = 1) {
  if (k <= 0) return;
  const ex = lerp(x0, x1, k), ey = lerp(y0, y1, k);
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.lineWidth = 3; ctx.setLineDash([10, 10]); ctx.lineDashOffset = -t * 60;
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(ex, ey); ctx.stroke(); ctx.setLineDash([]);
  glow(18, 1); ctx.fillStyle = '#fff';
  for (let i = 0; i < 2; i++) {
    const u = ((t * 0.7 + i * 0.5) % 1) * k;
    ctx.beginPath(); ctx.arc(lerp(x0, x1, u), lerp(y0, y1, u), 7, 0, 6.283); ctx.fill();
  }
  ctx.beginPath(); ctx.arc(x0, y0, 6, 0, 6.283); ctx.fill();
  noGlow(); ctx.restore();
}

// ---------- text ----------
function spaced(text, sp) { return text; }
function textBlock(lines, cx, y, o = {}) {
  const { size = 92, font = 'InterBlack', t = 0, start = 0, end = 99, lh = 1.08, stagger = 0.07, color = '#fff', glowA = 0.55, tracking = 0 } = o;
  const vis = win(t, start, end, 0.3, 0.3);
  if (vis <= 0) return;
  ctx.save();
  ctx.font = `${size}px ${font}`;
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
  ctx.letterSpacing = `${tracking}px`;
  let wi = 0;
  lines.forEach((line, li) => {
    const words = line.split(' ');
    const widths = words.map((w) => ctx.measureText(w.replace(/[*]/g, '')).width);
    const spaceW = ctx.measureText(' ').width;
    const total = widths.reduce((a, b) => a + b, 0) + spaceW * (words.length - 1);
    let x = cx - total / 2;
    const ly = y + li * size * lh;
    words.forEach((w, i) => {
      const k = easeOut(seg(t, start + wi * stagger, start + wi * stagger + 0.35));
      const out = 1 - seg(t, end - 0.3, end);
      const a = k * out;
      if (a > 0) {
        const hl = w.startsWith('*');
        const word = w.replace(/[*]/g, '');
        ctx.globalAlpha = a;
        const dy = (1 - k) * 26;
        if (hl) {
          // white pill highlight (HUMAN MIND style)
          const pw = widths[i] + size * 0.4, ph = size * 1.08;
          ctx.fillStyle = '#fff'; glow(30, 0.8);
          roundRect(x - size * 0.2, ly - ph / 2 + dy, pw, ph, ph * 0.28); ctx.fill(); noGlow();
          ctx.fillStyle = '#050505'; ctx.fillText(word, x, ly + dy + size * 0.04);
        } else {
          ctx.fillStyle = color; glow(24, glowA);
          ctx.fillText(word, x, ly + dy + size * 0.04); noGlow();
        }
      }
      x += widths[i] + spaceW + (w.startsWith('*') ? size * 0.25 : 0);
      wi++;
    });
  });
  ctx.restore();
}
function roundRect(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function pill(text, cx, cy, size, alpha, o = {}) {
  if (alpha <= 0) return;
  const { inverted = false, tracking = 6 } = o;
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.font = `${size}px InterSemi`; ctx.letterSpacing = `${tracking}px`;
  const w = ctx.measureText(text).width + size * 1.6, h = size * 2.1;
  roundRect(cx - w / 2, cy - h / 2, w, h, h / 2);
  if (inverted) { ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 2.5; ctx.stroke(); ctx.fillStyle = '#fff'; }
  else { glow(28, 0.8); ctx.fillStyle = '#fff'; ctx.fill(); noGlow(); ctx.fillStyle = '#060606'; }
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, cx + tracking / 2, cy + size * 0.05);
  ctx.restore();
}

// ---------- scenes ----------
function streetWorld(t, c, opt = {}) {
  const f = Math.round(t * FPS);
  const x = T.charX[Math.min(f, T.FRAMES)];
  const walk = T.walkAmt[Math.min(f, T.FRAMES)];
  const phase = ((x - T.START_X) / T.STRIDE) * Math.PI;
  const m = ease(seg(t, REVEAL.start, REVEAL.end));
  // lamp switching on with flicker right at reveal
  let flick = 0;
  if (t > REVEAL.start - 0.15) {
    const u = t - (REVEAL.start - 0.15);
    flick = u > 0.55 ? 1 : (Math.sin(u * 90) > 0.2 ? 0.9 : 0.15);
  }
  const lit = seg(t, REVEAL.start, REVEAL.start + 0.6);

  ctx.save(); applyCam(c);
  // far streetlamps (off, atmosphere)
  ctx.save(); ctx.globalAlpha = 0.35; drawLamp(-700, 0, 0); ctx.restore();
  drawLamp(TREE_X + 250, 1, flick);
  // silhouette / tree
  drawFigure(TREE_X, 0, 1.12, m, { lit });
  // brain's guess overlay
  if (opt.ghost > 0) drawFigure(TREE_X, 0, 1.12, 0, { dashed: true, alpha: opt.ghost, lit: 1 });
  // character
  const nervous = seg(t, 6.1, 6.6) * (1 - seg(t, 12.3, 13.2));
  const relax = seg(t, 12.6, 13.4);
  drawMan(x, 0, 1, { phase, walk, lean: -0.06 * nervous + 0.02 * relax, tremble: nervous > 0.01 ? t : 0, relax, lookUp: opt.lookUp || 0 });
  // heartbeat rings
  for (const hb of T.heartbeats) {
    const u = (t - hb) / 0.7;
    if (u > 0 && u < 1) {
      ctx.save(); ctx.strokeStyle = `rgba(255,255,255,${(1 - u) * 0.85})`; ctx.lineWidth = 4 * (1 - u) + 1; glow(18, 0.8);
      ctx.beginPath(); ctx.arc(x + 6, -130, 20 + u * 90, 0, 6.283); ctx.stroke(); noGlow(); ctx.restore();
    }
  }
  // relief "breath"
  const br = seg(t, 13.0, 14.2);
  if (br > 0 && br < 1) {
    ctx.save(); ctx.strokeStyle = `rgba(255,255,255,${Math.sin(br * Math.PI) * 0.7})`; ctx.lineWidth = 4; ctx.lineCap = 'round';
    for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(x + 46 + br * 40, -205 + (i - 1) * 16, 10 + i * 4, -0.7, 0.7); ctx.stroke(); }
    ctx.restore();
  }
  ctx.restore();
  return { x, m };
}

// heartbeat intensity at time t (for screen pulse)
function beatPulse(t) {
  let v = 0;
  for (const hb of T.heartbeats) { const u = t - hb; if (u >= 0 && u < 0.35) v = Math.max(v, 1 - u / 0.35); }
  return v;
}

function sceneStreet(t) {
  const c = camAt(t);
  // reveal "camera hit": tiny shake
  const shake = (t > REVEAL.start && t < REVEAL.start + 0.35) ? (1 - (t - REVEAL.start) / 0.35) * 6 : 0;
  c.x += Math.sin(t * 97) * shake; c.y += Math.cos(t * 83) * shake;
  const bp = beatPulse(t);
  background(t, 0.75 + 0.25 * seg(t, REVEAL.start, REVEAL.start + 0.5));
  drawGround(c);
  const ghost = win(t, 18.4, 21.6, 0.5, 0.4) * (0.55 + 0.3 * Math.sin(t * 6));
  const { x } = streetWorld(t, c, { ghost, lookUp: seg(t, 15.2, 15.8) });
  vignette(0.55 + bp * 0.3 + (1 - seg(t, 0, 2.3)) * 0.15);

  // brain section (15 - 21.5)
  if (t > 15.0) {
    const bx = 200, by = -820;
    const [sx, sy] = toScreen(c, bx, by);
    const rv = ease(seg(t, 15.2, 16.6));
    const pulse = Math.max(0, Math.sin((t - 16.6) * 4)) * seg(t, 16.6, 17);
    drawBrain(sx, sy, c.z * 0.95, rv, pulse, 1);
    const [ex, ey] = toScreen(c, x + 14, -205);
    const [tx, ty] = toScreen(c, TREE_X, -330);
    const k1 = ease(seg(t, 16.4, 17.2)), k2 = ease(seg(t, 17.0, 17.8));
    signalLine(ex, ey, sx - 70 * c.z, sy + 90 * c.z, k1, t);
    signalLine(tx, ty, sx + 70 * c.z, sy + 90 * c.z, k2, t + 0.3);
    // small labels
    const la = seg(t, 17.6, 18.0);
    pill('ГЛАЗА', Math.max(150, ex - 10), ey - 90 * c.z - 40, 26, la * (1 - seg(t, 21.0, 21.4)), { inverted: true });
    pill('ОПЫТ', sx, sy - 175 * c.z, 26, seg(t, 18.6, 19.0) * (1 - seg(t, 21.0, 21.4)), { inverted: true });
  }

  // ---- texts ----
  // HOOK (0 - 4.5)
  textBlock(['КТО СТОИТ', 'В ТЕМНОТЕ?'], W / 2, 360, { t, start: -0.8, end: 2.35, size: 116, stagger: 0.12 });
  textBlock(['ТАМ', '*НИКОГО', 'НЕТ.'], W / 2, 330, { t, start: 2.45, end: 4.7, size: 116, stagger: 0.14 });
  pill('НО ТВОЙ МОЗГ ВИДИТ ЧЕЛОВЕКА', W / 2, 700, 30, seg(t, 3.0, 3.4) * (1 - seg(t, 4.4, 4.7)));
  // captions
  textBlock(['Тёмная улица.', 'Впереди кто-то стоит.'], W / 2, 1540, { t, start: 4.8, end: 7.7, size: 58, font: 'InterBold', stagger: 0.06 });
  textBlock(['Сердце бьётся чаще.', 'Шаг. Ещё шаг…'], W / 2, 1540, { t, start: 7.9, end: 11.7, size: 58, font: 'InterBold', stagger: 0.12 });
  textBlock(['ЭТО ПРОСТО', '*ДЕРЕВО.'], W / 2, 330, { t, start: 12.2, end: 15.0, size: 112, stagger: 0.12 });
  textBlock(['Мозг не просто «видит».'], W / 2, 1600, { t, start: 15.3, end: 18.2, size: 56, font: 'InterBold', stagger: 0.07 });
  textBlock(['Он *ДОСТРАИВАЕТ картинку', 'по опыту и ожиданиям.'], W / 2, 1570, { t, start: 18.35, end: 21.4, size: 54, font: 'InterBold', stagger: 0.07 });

  // flash on reveal
  const fl = (t > REVEAL.start && t < REVEAL.start + 0.5) ? (1 - (t - REVEAL.start) / 0.5) : 0;
  if (fl > 0) { ctx.fillStyle = `rgba(255,255,255,${fl * 0.22})`; ctx.fillRect(0, 0, W, H); }
}

// ---------- dots → face ----------
const DOTS = (() => {
  const r = rng(2024);
  const face = [];
  const cx = 540, cy = 860;
  for (let i = 0; i < 7; i++) { const a = (i / 7) * 6.283; face.push({ x: cx - 150 + Math.cos(a) * 46, y: cy - 90 + Math.sin(a) * 46, g: 'eyeL', i }); }
  for (let i = 0; i < 7; i++) { const a = (i / 7) * 6.283; face.push({ x: cx + 150 + Math.cos(a) * 46, y: cy - 90 + Math.sin(a) * 46, g: 'eyeR', i }); }
  for (let i = 0; i < 4; i++) face.push({ x: cx + (i === 3 ? -22 : 0), y: cy - 20 + i * 38 - (i === 3 ? 10 : 0), g: 'nose', i });
  for (let i = 0; i < 9; i++) { const u = i / 8; face.push({ x: cx - 190 + u * 380, y: cy + 170 + Math.sin(u * Math.PI) * 70, g: 'mouth', i }); }
  const rand = [];
  while (rand.length < 85) {
    const p = { x: 70 + r() * 940, y: 430 + r() * 900 };
    if (face.every((q) => Math.hypot(q.x - p.x, q.y - p.y) > 55) && rand.every((q) => Math.hypot(q.x - p.x, q.y - p.y) > 45)) rand.push(p);
  }
  const all = [...face.map((p) => ({ ...p, face: true })), ...rand.map((p) => ({ ...p, face: false }))];
  all.forEach((p) => { p.d = r(); p.jx = (r() - 0.5) * 30; p.jy = (r() - 0.5) * 30; });
  return all;
})();

function sceneDots(t) {
  background(t, 0.6);
  const lt = t - 21.5;
  const zoom = 1 + lt * 0.012;
  ctx.save(); ctx.translate(540, 900); ctx.scale(zoom, zoom); ctx.translate(-540, -900);
  const groups = { eyeL: [23.6, 24.3, true], eyeR: [24.0, 24.7, true], nose: [24.5, 25.0, false], mouth: [24.9, 25.8, false] };
  const dimRand = seg(t, 25.4, 26.2);
  const faceGlow = seg(t, 25.6, 26.3);
  // connecting lines
  ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  for (const [g, [a, b, closed]] of Object.entries(groups)) {
    const pts = DOTS.filter((p) => p.g === g);
    const k = seg(t, a, b); if (k <= 0) continue;
    const n = closed ? pts.length : pts.length - 1;
    ctx.lineWidth = 4 + faceGlow * 2; glow(16 + faceGlow * 20, 0.9);
    ctx.beginPath(); ctx.moveTo(pts[0].x, pts[0].y);
    const segs = k * n;
    for (let i = 1; i <= Math.ceil(segs); i++) {
      const p0 = pts[(i - 1) % pts.length], p1 = pts[i % pts.length];
      const u = Math.min(1, segs - (i - 1));
      ctx.lineTo(lerp(p0.x, p1.x, u), lerp(p0.y, p1.y, u));
    }
    ctx.stroke();
  }
  noGlow(); ctx.restore();
  // dots
  for (const p of DOTS) {
    const appear = easeBack(seg(t, 21.8 + p.d * 1.4, 22.2 + p.d * 1.4));
    if (appear <= 0) continue;
    let a = 1, r = 7;
    if (!p.face) { a = 1 - dimRand * 0.8; }
    else { r = 7 + faceGlow * 3; }
    const settle = p.face ? 1 - seg(t, 22.8, 23.6) : 1;
    ctx.globalAlpha = a; ctx.fillStyle = '#fff'; glow(p.face ? 14 + faceGlow * 16 : 10, 0.8);
    ctx.beginPath(); ctx.arc(p.x + p.jx * settle * 0, p.y, r * appear, 0, 6.283); ctx.fill();
  }
  ctx.globalAlpha = 1; noGlow();
  ctx.restore();
  // little observer
  drawMan(150, 1395, 0.62, { lookUp: 1, alpha: seg(t, 21.9, 22.4) });
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.45)'; ctx.lineWidth = 2; ctx.setLineDash([6, 10]);
  ctx.globalAlpha = seg(t, 23.4, 23.9) * (1 - seg(t, 27.4, 27.8));
  ctx.beginPath(); ctx.moveTo(160, 1250); ctx.lineTo(380, 790); ctx.stroke(); ctx.restore();
  vignette(0.6);
  pill('ПАРЕЙДОЛИЯ', W / 2, 400, 36, seg(t, 25.9, 26.3) * (1 - seg(t, 27.5, 27.9)));
  textBlock(['Мозг ищет знакомое…'], W / 2, 1560, { t, start: 22.0, end: 24.8, size: 58, font: 'InterBold' });
  textBlock(['…даже в случайных', 'точках.'], W / 2, 1530, { t, start: 24.9, end: 27.9, size: 58, font: 'InterBold' });
}

// ---------- spotlight question ----------
function sceneQuestion(t) {
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const lt = t - 28;
  const z = 1 + ease(seg(t, 28, 34.5)) * 0.22;
  ctx.save(); ctx.translate(540, 1050); ctx.scale(z, z); ctx.translate(-540, -1050);
  // cone
  const on = seg(t, 28.15, 28.5);
  const cg = ctx.createLinearGradient(0, 0, 0, 1260);
  cg.addColorStop(0, `rgba(255,255,255,${0.02 * on})`); cg.addColorStop(1, `rgba(255,255,255,${0.2 * on})`);
  ctx.fillStyle = cg; ctx.beginPath(); ctx.moveTo(500, -100); ctx.lineTo(580, -100); ctx.lineTo(800, 1260); ctx.lineTo(280, 1260); ctx.closePath(); ctx.fill();
  const fg = ctx.createRadialGradient(540, 1262, 10, 540, 1262, 300);
  fg.addColorStop(0, `rgba(255,255,255,${0.35 * on})`); fg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = fg; ctx.save(); ctx.translate(540, 1262); ctx.scale(1, 0.18); ctx.beginPath(); ctx.arc(0, 0, 300, 0, 6.283); ctx.restore(); ctx.fill();
  drawMan(540, 1262, 1.1, { alpha: on, lookUp: seg(t, 30.5, 31.3) });
  ctx.restore();
  // dust in the beam
  for (let i = 0; i < 26; i++) {
    const pr = particles[i];
    const y = (pr.y * 0.65 + lt * pr.s * 2) % 1250;
    const xr = 540 + (pr.x / W - 0.5) * (80 + y * 0.42);
    ctx.fillStyle = `rgba(255,255,255,${pr.a * on})`; ctx.beginPath(); ctx.arc(xr, y, pr.r, 0, 6.283); ctx.fill();
  }
  textBlock(['ТЫ ВИДИШЬ', 'РЕАЛЬНОСТЬ?'], W / 2, 330, { t, start: 28.6, end: 34.4, size: 104, stagger: 0.14 });
  textBlock(['ИЛИ ТО, ЧТО', '*ОЖИДАЕШЬ?'], W / 2, 1520, { t, start: 31.3, end: 34.4, size: 92, stagger: 0.14 });
}

// ---------- end card ----------
function sceneLogo(t) {
  background(t, 0.5);
  const k = easeOut(seg(t, 34.6, 35.4));
  ctx.save();
  ctx.globalAlpha = k;
  ctx.font = '120px InterBlack'; ctx.letterSpacing = '18px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillStyle = '#fff'; glow(40, 0.9);
  ctx.fillText('HUMAN', W / 2 + 9, 830 + (1 - k) * 30);
  ctx.fillText('MIND', W / 2 + 9, 960 + (1 - k) * 30);
  noGlow(); ctx.restore();
  // drawing line
  const lk = ease(seg(t, 35.0, 35.8));
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 3; glow(14, 0.8);
  ctx.beginPath(); ctx.moveTo(540 - 260 * lk, 1060); ctx.lineTo(540 + 260 * lk, 1060); ctx.stroke(); noGlow(); ctx.restore();
  pill('ЭПИЗОД 02', W / 2, 690, 30, seg(t, 35.2, 35.6));
  textBlock(['Почему мозг видит', 'то, чего нет'], W / 2, 1170, { t, start: 35.5, end: 40, size: 50, font: 'InterSemi', glowA: 0.3 });
  pill('ПОЛНЫЙ ВЫПУСК НА КАНАЛЕ', W / 2, 1420, 28, seg(t, 36.0, 36.4), { inverted: true });
}

function fadeBlack(a) { if (a > 0) { ctx.fillStyle = `rgba(0,0,0,${clamp(a)})`; ctx.fillRect(0, 0, W, H); } }

function renderFrame(t) {
  ctx.save();
  ctx.globalAlpha = 1;
  if (t < 21.5) sceneStreet(t);
  else if (t < 28) sceneDots(t);
  else if (t < 34.5) sceneQuestion(t);
  else sceneLogo(t);
  ctx.restore();
  // dip-to-black transitions
  const dips = [21.5, 28, 34.5];
  let d = 0;
  for (const c of dips) d = Math.max(d, 1 - Math.abs(t - c) / 0.3);
  d = Math.max(d, seg(t, 37.3, 38));
  fadeBlack(d);
  // film grain-ish subtle noise lines
}

// ---------- cover (thumbnail 9:16) ----------
function renderCover() {
  const t = 9.6;
  background(t, 0.8);
  const c = { x: 250, y: -420, z: 1.55 };
  drawGround(c);
  ctx.save(); applyCam(c);
  // moon-ish glow behind figure
  const g = ctx.createRadialGradient(TREE_X, -220, 10, TREE_X, -220, 380);
  g.addColorStop(0, 'rgba(255,255,255,0.22)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(TREE_X, -220, 380, 0, 6.283); ctx.fill();
  drawFigure(TREE_X, 0, 1.2, 0.0, { lit: 0.12 });
  drawMan(130, 0, 1.15, { lean: -0.06, phase: 0.6, walk: 0.3 });
  ctx.restore();
  vignette(0.6);
  // heartbeat ring
  const [hx, hy] = toScreen(c, 140, -150);
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 4; glow(16, 0.8);
  for (const r of [70, 115]) { ctx.globalAlpha = r === 70 ? 0.7 : 0.35; ctx.beginPath(); ctx.arc(hx, hy, r, 0, 6.283); ctx.stroke(); }
  noGlow(); ctx.restore();
  textBlock(['ТВОЙ МОЗГ', 'ТЕБЯ', '*ОБМАНЫВАЕТ?'], W / 2, 300, { t: 10, start: 0, end: 99, size: 124, stagger: 0 });
  pill('HUMAN MIND · ЭПИЗОД 02', W / 2, 1700, 30, 1);
}

// ---------- main ----------
const args = process.argv.slice(2);
if (args[0] === '--still') {
  const fs = require('fs');
  if (args[1] === 'cover') renderCover(); else renderFrame(parseFloat(args[1]));
  fs.writeFileSync(args[2], canvas.toBuffer('image/png'));
} else {
  const [a, b, out] = [parseInt(args[0]), parseInt(args[1]), args[2]];
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  (async () => {
    for (let f = a; f < b; f++) {
      renderFrame(f / FPS);
      const buf = Buffer.from(ctx.getImageData(0, 0, W, H).data.buffer);
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
  })();
}
