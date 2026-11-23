// HUMAN MIND — Episode 02 — vertical 9:16 preview renderer.
// Usage: node render.js <startFrame> <endFrame> <out.mp4>    (renders video only)
//        node render.js --still <time|cover> <out.png>
const { createCanvas, GlobalFonts, Path2D } = require('@napi-rs/canvas');
const { spawn } = require('child_process');
const T = require('./timeline');
const { FPS, clamp, seg, TREE_X, REVEAL, CUTS } = T;

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
  [2.0, 330, -195, 2.45],
  [3.4, 20, -330, 1.0],
  [6.0, 90, -320, 1.05],
  [8.0, 110, -300, 1.12],
  [11.6, 210, -230, 1.6],
  [12.4, 240, -330, 1.22],
  [14.8, 240, -335, 1.2],
  [16.2, 200, -470, 0.88],
  [24.0, 200, -490, 0.8],
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
  const { phase = 0, walk = 0, lean = 0, tremble = 0, relax = 0, alpha = 1, color = '#ffffff', glowAmt = 1, lookUp = 0, reach = 0 } = o;
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
    const a = (sgn === 1 && reach > 0) ? lerp(aa, Math.PI / 2 * 0.95, reach) : aa * sgn;
    const ex = sgn * 30 + Math.sin(a) * 40, ey = shY + 10 + Math.cos(a) * 40;
    const ha = (sgn === 1 && reach > 0) ? lerp(a + 0.25 * walk, Math.PI / 2 * 1.05, reach) : a + 0.25 * walk;
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
  drawLamp(TREE_X + 330, 1, flick);
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
  const ghost = win(t, 19.0, 23.8, 0.5, 0.4) * (0.55 + 0.3 * Math.sin(t * 6));
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
    pill('ГЛАЗА', Math.max(150, ex - 10), ey - 90 * c.z - 40, 26, la * (1 - seg(t, 23.4, 23.8)), { inverted: true });
    pill('ОПЫТ', sx, sy - 175 * c.z, 26, seg(t, 18.6, 19.0) * (1 - seg(t, 23.4, 23.8)), { inverted: true });
  }

  // ---- texts ----
  // HOOK (0 - 4.5)
  pill('СМОТРИ ВНИМАТЕЛЬНО', W / 2, 235, 30, 1 - seg(t, 1.7, 2.0), { inverted: true });
  textBlock(['ТЫ ВИДИШЬ', 'ЧЕЛОВЕКА?'], W / 2, 370, { t, start: -0.8, end: 2.0, size: 124, stagger: 0.12 });
  textBlock(['ЕГО ТАМ', '*НЕТ.'], W / 2, 350, { t, start: 2.0, end: 4.7, size: 130, stagger: 0.16 });
  pill('ТВОЙ МОЗГ ДОРИСОВАЛ ЕГО САМ', W / 2, 640, 32, seg(t, 2.7, 3.1) * (1 - seg(t, 4.4, 4.7)));
  // captions
  textBlock(['Тёмная улица.', 'Впереди кто-то стоит.'], W / 2, 1540, { t, start: 4.8, end: 7.7, size: 58, font: 'InterBold', stagger: 0.06 });
  textBlock(['Сердце бьётся чаще.', 'Шаг. Ещё шаг…'], W / 2, 1540, { t, start: 7.9, end: 11.7, size: 58, font: 'InterBold', stagger: 0.12 });
  textBlock(['ЭТО ПРОСТО', '*ДЕРЕВО.'], W / 2, 330, { t, start: 12.2, end: 15.0, size: 112, stagger: 0.12 });
  textBlock(['Мозг не просто «видит».'], W / 2, 1600, { t, start: 15.3, end: 18.2, size: 56, font: 'InterBold', stagger: 0.07 });
  textBlock(['Он *ДОСТРАИВАЕТ картинку', 'по опыту и ожиданиям.'], W / 2, 1570, { t, start: 18.35, end: 23.9, size: 54, font: 'InterBold', stagger: 0.07 });

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
  ctx.globalAlpha = seg(t, 23.4, 23.9) * (1 - seg(t, 29.0, 29.4));
  ctx.beginPath(); ctx.moveTo(160, 1250); ctx.lineTo(380, 790); ctx.stroke(); ctx.restore();
  vignette(0.6);
  pill('ПАРЕЙДОЛИЯ', W / 2, 400, 36, seg(t, 25.9, 26.3) * (1 - seg(t, 29.0, 29.4)));
  textBlock(['Мозг ищет знакомое…'], W / 2, 1560, { t, start: 22.0, end: 24.8, size: 58, font: 'InterBold' });
  textBlock(['…даже в случайных', 'точках.'], W / 2, 1530, { t, start: 24.9, end: 29.4, size: 58, font: 'InterBold' });
}

// ---------- spotlight question ----------
function sceneQuestion(t) {
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
  const lt = t - 28;
  const z = 1 + ease(seg(t, 28, 39)) * 0.28;
  ctx.save(); ctx.translate(540, 1050); ctx.scale(z, z); ctx.translate(-540, -1050);
  // cone
  const on = seg(t, 28.15, 28.5);
  const cg = ctx.createLinearGradient(0, 0, 0, 1260);
  cg.addColorStop(0, `rgba(255,255,255,${0.02 * on})`); cg.addColorStop(1, `rgba(255,255,255,${0.2 * on})`);
  ctx.fillStyle = cg; ctx.beginPath(); ctx.moveTo(500, -100); ctx.lineTo(580, -100); ctx.lineTo(800, 1260); ctx.lineTo(280, 1260); ctx.closePath(); ctx.fill();
  const fg = ctx.createRadialGradient(540, 1262, 10, 540, 1262, 300);
  fg.addColorStop(0, `rgba(255,255,255,${0.35 * on})`); fg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = fg; ctx.save(); ctx.translate(540, 1262); ctx.scale(1, 0.18); ctx.beginPath(); ctx.arc(0, 0, 300, 0, 6.283); ctx.restore(); ctx.fill();
  drawMan(540, 1262, 1.1, { alpha: on, lookUp: seg(t, 31.5, 32.3) });
  ctx.restore();
  // dust in the beam
  for (let i = 0; i < 26; i++) {
    const pr = particles[i];
    const y = (pr.y * 0.65 + lt * pr.s * 2) % 1250;
    const xr = 540 + (pr.x / W - 0.5) * (80 + y * 0.42);
    ctx.fillStyle = `rgba(255,255,255,${pr.a * on})`; ctx.beginPath(); ctx.arc(xr, y, pr.r, 0, 6.283); ctx.fill();
  }
  textBlock(['ТЫ ВИДИШЬ', 'РЕАЛЬНОСТЬ?'], W / 2, 330, { t, start: 28.6, end: 38.9, size: 104, stagger: 0.14 });
  textBlock(['ИЛИ ТО, ЧТО', '*ОЖИДАЕШЬ?'], W / 2, 1520, { t, start: 32.3, end: 38.9, size: 92, stagger: 0.14 });
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
  textBlock(['Почему мозг видит', 'то, чего нет'], W / 2, 1170, { t, start: 35.5, end: 99, size: 50, font: 'InterSemi', glowA: 0.3 });
  pill('ПОЛНЫЙ ВЫПУСК НА КАНАЛЕ', W / 2, 1420, 28, seg(t, 36.0, 36.4), { inverted: true });
}

function fadeBlack(a) { if (a > 0) { ctx.fillStyle = `rgba(0,0,0,${clamp(a)})`; ctx.fillRect(0, 0, W, H); } }

// ---------- cloud that looks like a face (24 - 32) ----------
function sceneCloud(t) {
  background(t, 0.55);
  const lt = t - 24;
  // moon
  ctx.save(); const mg = ctx.createRadialGradient(860, 330, 10, 860, 330, 260);
  mg.addColorStop(0, 'rgba(255,255,255,0.35)'); mg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = mg; ctx.beginPath(); ctx.arc(860, 330, 260, 0, 6.283); ctx.fill();
  ctx.fillStyle = '#eee'; glow(40, 0.9); ctx.beginPath(); ctx.arc(860, 330, 46, 0, 6.283); ctx.fill(); noGlow(); ctx.restore();
  const cx = 560 - lt * 9, cy = 820;
  const z = 1 + lt * 0.015;
  ctx.save(); ctx.translate(cx, cy); ctx.scale(z, z);
  const puffs = [[-230, 40, 110], [-120, -40, 150], [30, -90, 170], [180, -30, 150], [270, 50, 110], [-60, 80, 140], [110, 90, 140], [-300, 110, 80], [330, 120, 80]];
  const fk = ease(seg(t, 26.3, 28.3)); // face emerges
  ctx.fillStyle = 'rgba(235,235,235,0.92)'; glow(50, 0.6);
  ctx.beginPath(); for (const [x, y, r] of puffs) { ctx.moveTo(x + r, y); ctx.arc(x, y, r * (1 + 0.02 * Math.sin(t * 0.8 + x)), 0, 6.283); } ctx.fill(); noGlow();
  // darker hollows = eyes + mouth
  ctx.fillStyle = `rgba(20,20,20,${0.55 * fk})`;
  ctx.beginPath(); ctx.ellipse(-80, -40, 34, 44 * fk + 4, 0.1, 0, 6.283); ctx.ellipse(110, -45, 34, 44 * fk + 4, -0.1, 0, 6.283); ctx.fill();
  ctx.beginPath(); ctx.ellipse(20, 95, 95 * fk + 10, 34 * fk + 4, 0, 0, Math.PI); ctx.fill();
  // dashed outline once the viewer "sees" it
  const ok = seg(t, 28.4, 29.0) * (1 - seg(t, 31.4, 31.8));
  if (ok > 0) {
    ctx.save(); ctx.globalAlpha = ok; ctx.strokeStyle = '#fff'; ctx.lineWidth = 4; ctx.setLineDash([12, 10]); ctx.lineDashOffset = -t * 30; glow(14, 0.9);
    ctx.beginPath(); ctx.ellipse(15, 10, 300, 240, 0, 0, 6.283); ctx.stroke(); ctx.restore();
  }
  ctx.restore();
  // observer
  const gy = 1390;
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.4)'; ctx.lineWidth = 3; ctx.setLineDash([24, 14]);
  ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke(); ctx.restore();
  drawMan(190, gy, 0.7, { lookUp: 1, alpha: seg(t, 24.2, 24.7), lean: -0.05 });
  vignette(0.55);
  textBlock(['Посмотри на облако.'], W / 2, 1560, { t, start: 24.5, end: 28.0, size: 58, font: 'InterBold' });
  textBlock(['Видишь лицо?'], W / 2, 1530, { t, start: 28.2, end: 31.8, size: 58, font: 'InterBold' });
  textBlock(['Его там тоже *нет.'], W / 2, 1620, { t, start: 29.4, end: 31.8, size: 58, font: 'InterBold' });
}

// ---------- objects that look like something else (40 - 61) ----------
function rope(k, lit) { // S-curve; k: 0 = snake, 1 = rope
  const pts = [];
  for (let i = 0; i <= 60; i++) { const u = i / 60; pts.push([-330 + u * 640, Math.sin(u * Math.PI * 2.2) * 55 * (1 - u * 0.3) - 6]); }
  const shade = Math.round(lerp(70, 235, lit));
  ctx.strokeStyle = `rgb(${shade},${shade},${shade})`; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  glow(lerp(10, 26, lit), lerp(0.2, 0.7, lit));
  ctx.lineWidth = lerp(30, 20, k);
  ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.stroke(); noGlow();
  const [hx, hy] = pts[pts.length - 1];
  if (k < 1) { // snake head + tongue
    ctx.save(); ctx.globalAlpha = 1 - k; ctx.fillStyle = `rgb(${shade},${shade},${shade})`;
    ctx.beginPath(); ctx.ellipse(hx + 20, hy - 4, 34, 22, -0.2, 0, 6.283); ctx.fill();
    ctx.fillStyle = '#fff'; glow(12, 1); ctx.beginPath(); ctx.arc(hx + 30, hy - 12, 4, 0, 6.283); ctx.fill(); noGlow();
    ctx.strokeStyle = '#bbb'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(hx + 52, hy - 6); ctx.lineTo(hx + 72, hy - 10); ctx.lineTo(hx + 80, hy - 18); ctx.moveTo(hx + 72, hy - 10); ctx.lineTo(hx + 82, hy - 4); ctx.stroke();
    ctx.restore();
  }
  if (k > 0) { // twist marks + frayed ends
    ctx.save(); ctx.globalAlpha = k; ctx.strokeStyle = '#2a2a2a'; ctx.lineWidth = 3;
    for (let i = 1; i < pts.length - 1; i += 2) { const [x, y] = pts[i]; ctx.beginPath(); ctx.moveTo(x - 5, y - 8); ctx.lineTo(x + 5, y + 8); ctx.stroke(); }
    ctx.strokeStyle = '#ddd'; ctx.lineWidth = 3;
    for (const [ex, ey, d] of [[pts[0][0], pts[0][1], -1], [hx, hy, 1]]) for (let j = -2; j <= 2; j++) { ctx.beginPath(); ctx.moveTo(ex, ey + j * 4); ctx.lineTo(ex + d * (16 + Math.abs(j) * 3), ey + j * 9); ctx.stroke(); }
    ctx.restore();
  }
}
function coat(k, lit) { // k: 0 = person standing in the dark, 1 = coat on a wall hook
  const shade = Math.round(lerp(55, 225, lit));
  const col = `rgb(${shade},${shade},${shade})`;
  ctx.fillStyle = col; glow(lerp(14, 26, lit), lerp(0.2, 0.6, lit));
  // hat
  ctx.beginPath(); ctx.ellipse(0, -400, 62, 13, 0, 0, 6.283); ctx.fill(); roundRect(-38, -460, 76, 62, 14); ctx.fill();
  // collar / "head" gap
  ctx.beginPath(); ctx.ellipse(0, -372, 30, 26, 0, 0, 6.283); ctx.fill();
  // coat body
  ctx.beginPath(); ctx.moveTo(-36, -350); ctx.quadraticCurveTo(-92, -345, -96, -300); ctx.lineTo(-104, -110); ctx.lineTo(104, -110); ctx.lineTo(96, -300); ctx.quadraticCurveTo(92, -345, 36, -350); ctx.closePath(); ctx.fill();
  // sleeves
  ctx.lineCap = 'round'; ctx.strokeStyle = col; ctx.lineWidth = 30;
  ctx.beginPath(); ctx.moveTo(-90, -310); ctx.lineTo(-104, -150); ctx.moveTo(90, -310); ctx.lineTo(104, -150); ctx.stroke();
  // "legs" in the dark (shadow) -> disappear when lit
  ctx.globalAlpha = 1 - k; ctx.lineWidth = 34;
  ctx.beginPath(); ctx.moveTo(-40, -110); ctx.lineTo(-44, 0); ctx.moveTo(40, -110); ctx.lineTo(44, 0); ctx.stroke(); ctx.globalAlpha = 1;
  noGlow();
  if (k > 0) { // buttons, hook, hanger
    ctx.save(); ctx.globalAlpha = k;
    ctx.fillStyle = '#333'; for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.arc(0, -320 + i * 52, 7, 0, 6.283); ctx.fill(); }
    ctx.strokeStyle = '#999'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(-22, -470); ctx.lineTo(22, -470); ctx.moveTo(0, -470); ctx.lineTo(0, -500); ctx.arc(-14, -500, 14, 0, Math.PI, true); ctx.stroke();
    ctx.fillStyle = '#888'; roundRect(-40, -478, 80, 16, 6); ctx.fill();
    ctx.restore();
  }
}
function socket(lit) {
  ctx.fillStyle = `rgb(${Math.round(lerp(150, 235, lit))},${Math.round(lerp(150, 235, lit))},${Math.round(lerp(150, 235, lit))})`;
  glow(30, 0.6); roundRect(-90, -90, 180, 180, 34); ctx.fill(); noGlow();
  ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 3; roundRect(-70, -70, 140, 140, 24); ctx.stroke();
  ctx.fillStyle = '#0a0a0a';
  roundRect(-38, -40, 14, 40, 6); ctx.fill(); roundRect(24, -40, 14, 40, 6); ctx.fill();
  ctx.beginPath(); ctx.ellipse(0, 42, 16, 12, 0, 0, 6.283); ctx.fill();
}
function sceneObject(t, idx) {
  const t0 = CUTS.objects[idx], lt = t - t0, rv = T.OBJ_REVEAL;
  const k = ease(seg(lt, rv, rv + 0.9));
  const lit = seg(lt, rv - 0.05, rv + 0.35);
  background(t, 0.45 + 0.4 * lit);
  // spotlight on the object after reveal
  const gy = 1300;
  const flash = (lt > rv && lt < rv + 0.45) ? (1 - (lt - rv) / 0.45) : 0;
  // camera: fake view = close + slightly tilted; real view = wider, level (perspective change)
  let zoom, ox, rot;
  if (idx === 2) { zoom = lerp(4.2, 1.0, ease(seg(lt, rv, rv + 1.3))) * (1 + lt * 0.01); ox = lerp(0, 120, k); rot = 0; }
  else { zoom = lerp(1.35 + lt * 0.03, 1.0, k); ox = lerp(80, 0, k); rot = lerp(-0.05, 0, k); }
  const objX = idx === 2 ? 640 : 600, objY = idx === 2 ? 820 : gy;
  ctx.save();
  ctx.translate(objX, objY - (idx === 2 ? 0 : 120)); ctx.rotate(rot); ctx.scale(zoom, zoom); ctx.translate(-objX + ox, -objY + (idx === 2 ? 0 : 120));
  // floor / wall
  ctx.strokeStyle = 'rgba(255,255,255,0.45)'; ctx.lineWidth = 3; ctx.setLineDash([24, 14]);
  ctx.beginPath(); ctx.moveTo(-600, gy); ctx.lineTo(W + 600, gy); ctx.stroke(); ctx.setLineDash([]);
  // light pool
  if (lit > 0) {
    const g = ctx.createRadialGradient(objX, objY - 100, 20, objX, objY - 100, 520);
    g.addColorStop(0, `rgba(255,255,255,${0.16 * lit})`); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(objX, objY - 100, 520, 0, 6.283); ctx.fill();
  }
  ctx.save(); ctx.translate(objX, objY);
  if (idx === 0) rope(k, lit);
  else if (idx === 1) { coat(k, lit); }
  else {
    socket(lit);
    // plug + cord visible after zoom-out
    ctx.globalAlpha = k; ctx.strokeStyle = '#cfcfcf'; ctx.lineWidth = 8; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-150, 160); ctx.bezierCurveTo(-200, 300, -320, 330, -330, gy - objY); ctx.stroke();
    ctx.fillStyle = '#ddd'; roundRect(-180, 110, 60, 60, 12); ctx.fill(); ctx.globalAlpha = 1;
  }
  ctx.restore();
  // observer (startled, then relaxed)
  const startle = seg(lt, 0.6, 1.0) * (1 - seg(lt, rv + 0.3, rv + 1.2));
  drawMan(idx === 2 ? 230 : 170, gy, 0.95, { lean: -0.12 * startle, tremble: startle > 0.2 ? t : 0, relax: seg(lt, rv + 0.4, rv + 1.2), alpha: seg(lt, 0.1, 0.5) });
  ctx.restore();
  vignette(0.6 - 0.2 * lit);
  if (flash > 0) { ctx.fillStyle = `rgba(255,255,255,${flash * 0.2})`; ctx.fillRect(0, 0, W, H); }
  const fakes = ['ЗМЕЯ?', 'КТО-ТО СТОИТ?', 'ЛИЦО?'];
  const reals = ['ВЕРЁВКА.', 'ПАЛЬТО.', 'РОЗЕТКА.'];
  textBlock([fakes[idx]], W / 2, 340, { t: lt, start: 0.4, end: rv, size: 112 });
  textBlock(['*' + reals[idx]], W / 2, 340, { t: lt, start: rv + 0.25, end: 7.1, size: 112 });
  const caps = [
    [['Первое впечатление…'], ['…бывает обманчивым.']],
    [['Мозг спешит', 'с выводом…'], ['…а детали', 'дорисовывает сам.']],
    [['Мозг ищет лица', 'повсюду.'], ['Даже на стене.']],
  ][idx];
  textBlock(caps[0], W / 2, 1530, { t: lt, start: 0.7, end: rv, size: 58, font: 'InterBold' });
  textBlock(caps[1], W / 2, 1530, { t: lt, start: rv + 0.6, end: 7.1, size: 58, font: 'InterBold' });
}

// ---------- psychological explanation (61 - 68.5) ----------
function sceneExplain(t) {
  background(t, 0.6);
  const lt = t - 61;
  const bx = 540, by = 760;
  const pulse = Math.max(0, Math.sin(lt * 3.2)) * seg(t, 64.6, 65.2);
  drawBrain(bx, by, 1.75, ease(seg(t, 61.2, 62.6)), pulse);
  const words = [['ОПЫТ', 250, 1130, 62.6], ['ОЖИДАНИЯ', 830, 1130, 63.4], ['ВОСПРИЯТИЕ', 540, 1330, 64.4]];
  for (const [w, x, y, ts] of words) {
    const k = seg(t, ts, ts + 0.6);
    signalLine(x, y - 40, bx + (x - bx) * 0.25, by + 170, ease(k), t);
    pill(w, x, y, 34, easeOut(k));
  }
  textBlock(['Ты видишь не только глазами.'], W / 2, 1560, { t, start: 61.5, end: 64.8, size: 52, font: 'InterBold' });
  textBlock(['Мозг смешивает сигнал', 'с тем, что уже *знает.'], W / 2, 1540, { t, start: 65.0, end: 68.4, size: 52, font: 'InterBold' });
  vignette(0.5);
}

// ---------- examining more carefully (68.5 - 75) ----------
function sceneExamine(t) {
  background(t, 0.55);
  const lt = t - 68.5;
  const gy = 1300;
  const z = 1.15 + lt * 0.02;
  ctx.save(); ctx.translate(540, 1100); ctx.scale(z, z); ctx.translate(-540, -1100);
  ctx.strokeStyle = 'rgba(255,255,255,0.45)'; ctx.lineWidth = 3; ctx.setLineDash([24, 14]);
  ctx.beginPath(); ctx.moveTo(-200, gy); ctx.lineTo(W + 200, gy); ctx.stroke(); ctx.setLineDash([]);
  // dark ambiguous object (the "snake")
  ctx.save(); ctx.translate(640, gy); rope(0, 0); ctx.restore();
  const reach = ease(seg(t, 68.9, 69.7));
  const mv = ease(seg(t, 69.8, 73.8));
  const mx = lerp(200, 640, mv);
  const fx = ((mx - 200) / 70) * Math.PI;
  const walking = (t > 69.8 && t < 73.8) ? 0.5 : 0;
  drawMan(mx, gy, 1.05, { lean: 0.12 * reach, reach, phase: fx, walk: walking, alpha: seg(t, 68.6, 69.0) });
  const hx = mx + 1.05 * 104, hy = gy - 1.05 * 152;
  const lx = hx + 95, ly = gy - 55;
  const r = 92 * seg(t, 69.4, 69.9);
  if (r > 1) {
    ctx.save(); ctx.beginPath(); ctx.arc(lx, ly, r, 0, 6.283); ctx.clip();
    ctx.fillStyle = '#151515'; ctx.fillRect(lx - r, ly - r, r * 2, r * 2);
    ctx.translate(640, gy); rope(1, 1); ctx.restore();
    ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 8; glow(22, 0.9);
    ctx.beginPath(); ctx.arc(lx, ly, r, 0, 6.283); ctx.stroke();
    ctx.lineWidth = 13; ctx.lineCap = 'round';
    const a = Math.atan2(hy - ly, hx - lx);
    ctx.beginPath(); ctx.moveTo(lx + Math.cos(a) * r, ly + Math.sin(a) * r); ctx.lineTo(hx, hy); ctx.stroke(); noGlow(); ctx.restore();
  }
  ctx.restore();
  vignette(0.55);
  textBlock(['Не спеши', 'с выводом.'], W / 2, 330, { t, start: 69.0, end: 74.8, size: 104 });
  textBlock(['Посмотри ещё раз —', 'внимательнее.'], W / 2, 1560, { t, start: 70.2, end: 74.8, size: 56, font: 'InterBold' });
}

function renderFrame(t) {
  ctx.save();
  ctx.globalAlpha = 1;
  const C = CUTS;
  if (t < C.cloud) sceneStreet(t);
  else if (t < C.dots) sceneCloud(t);
  else if (t < C.objects[0]) sceneDots(t - (C.dots - 21.5));
  else if (t < C.explain) sceneObject(t, t < C.objects[1] ? 0 : t < C.objects[2] ? 1 : 2);
  else if (t < C.examine) sceneExplain(t);
  else if (t < C.question) sceneExamine(t);
  else if (t < C.logo) sceneQuestion(t - (C.question - 28));
  else sceneLogo(t - (C.logo - 34.5));
  ctx.restore();
  const dips = [C.cloud, C.dots, ...C.objects, C.explain, C.examine, C.question, C.logo];
  let d = 0;
  for (const c of dips) d = Math.max(d, 1 - Math.abs(t - c) / 0.3);
  d = Math.max(d, seg(t, T.DURATION - 1.2, T.DURATION));
  fadeBlack(d);
}

// ---------- cover (thumbnail 9:16) ----------
function renderCover() {
  const t = 9.6;
  background(t, 0.7);
  const c = { x: 210, y: -250, z: 1.75 };
  drawGround(c);
  ctx.save(); applyCam(c);
  // strong backlight behind the figure
  const g = ctx.createRadialGradient(TREE_X, -240, 10, TREE_X, -240, 330);
  g.addColorStop(0, 'rgba(255,255,255,0.55)'); g.addColorStop(0.45, 'rgba(255,255,255,0.14)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(TREE_X, -240, 330, 0, 6.283); ctx.fill();
  drawFigure(TREE_X, 0, 1.1, 0, { lit: 0.0 });
  drawMan(40, 0, 1.1, { lean: -0.1, phase: 0.7, walk: 0.45 });
  ctx.restore();
  // ground fog
  const fg = ctx.createLinearGradient(0, 1150, 0, 1500);
  fg.addColorStop(0, 'rgba(255,255,255,0)'); fg.addColorStop(0.5, 'rgba(255,255,255,0.06)'); fg.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = fg; ctx.fillRect(0, 1150, W, 350);
  vignette(0.7);
  const [hx, hy] = toScreen(c, 46, -130);
  ctx.save(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 5; glow(18, 0.9);
  for (const [r, a] of [[85, 0.75], [140, 0.4], [195, 0.18]]) { ctx.globalAlpha = a; ctx.beginPath(); ctx.arc(hx, hy, r, 0, 6.283); ctx.stroke(); }
  noGlow(); ctx.restore();
  textBlock(['ТВОЙ МОЗГ', 'ТЕБЯ'], W / 2, 250, { t: 10, start: 0, end: 99, size: 150, stagger: 0 });
  textBlock(['*ОБМАНЫВАЕТ?'], W / 2, 580, { t: 10, start: 0, end: 99, size: 112, stagger: 0 });
  pill('HUMAN MIND · ЭПИЗОД 02', W / 2, 1760, 32, 1);
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
