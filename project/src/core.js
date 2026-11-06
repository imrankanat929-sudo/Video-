// Core engine: canvas, math helpers, camera, post-processing, timeline.
'use strict';

let W = 1920, H = 1080;
const PAL = {
  black: '#05060a',
  night: '#0a0f1a',
  navy: '#0f1a2c',
  navy2: '#16243b',
  steel: '#2a3547',
  grey: '#5b6575',
  mist: '#9aa6b8',
  white: '#d9dde4',
  red: '#c8323a',
  redDim: '#6e1a20',
  screen: '#bcd3ff',
};

// ---------- math ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ramp = (t, a, b) => clamp((t - a) / (b - a));
const ease = {
  inOut: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  out: t => 1 - Math.pow(1 - t, 3),
  in: t => t * t * t,
  outExpo: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inOutSine: t => -(Math.cos(Math.PI * t) - 1) / 2,
  outBack: t => { const c = 1.4; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
};
const sm = (t, a, b) => ease.inOut(ramp(t, a, b));        // smooth ramp
const so = (t, a, b) => ease.out(ramp(t, a, b));          // ease-out ramp

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
// smooth 1D value noise, deterministic
function noise1(x, seed = 0) {
  const h = n => { const s = Math.sin(n * 127.1 + seed * 311.7) * 43758.5453; return s - Math.floor(s); };
  const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
  return lerp(h(i), h(i + 1), u) * 2 - 1;
}

// ---------- canvas helpers ----------
function makeCanvas(w, h) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  return c;
}
function rr(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
function glow(ctx, x, y, r, color, alpha = 1) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, color);
  g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.globalCompositeOperation = 'lighter';
  ctx.fillStyle = g;
  ctx.fillRect(x - r, y - r, r * 2, r * 2);
  ctx.restore();
}
function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
function font(weight, size, fam = 'Inter') {
  return `${weight} ${size}px ${fam === 'mono' ? '"JetBrains Mono"' : '"Inter"'}`;
}
function text(ctx, s, x, y, opt = {}) {
  ctx.save();
  ctx.font = opt.font || font(500, 32);
  ctx.fillStyle = opt.color || PAL.white;
  ctx.textAlign = opt.align || 'left';
  ctx.textBaseline = opt.base || 'alphabetic';
  if (opt.ls !== undefined) ctx.letterSpacing = opt.ls + 'px';
  if (opt.alpha !== undefined) ctx.globalAlpha *= opt.alpha;
  if (opt.shadow) { ctx.shadowColor = opt.shadow; ctx.shadowBlur = opt.blur || 20; }
  ctx.fillText(s, x, y);
  ctx.restore();
}
// wrap text into lines that fit maxW
function wrap(ctx, s, maxW) {
  const words = s.split(' '); const lines = []; let cur = '';
  for (const w of words) {
    const tst = cur ? cur + ' ' + w : w;
    if (ctx.measureText(tst).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tst;
  }
  if (cur) lines.push(cur);
  return lines;
}

// ---------- camera ----------
// cam = {x, y, z, r}; world is authored in 1920x1080 at z=1 centred on (960,540).
// depth d: 1 = focal plane, <1 farther (moves less), >1 nearer (moves more).
function withCam(ctx, cam, d, fn) {
  ctx.save();
  const z = 1 + (cam.z - 1) * d;
  ctx.translate(W / 2, H / 2);
  if (cam.r) ctx.rotate(cam.r * d);
  ctx.scale(z, z);
  ctx.translate(-(960 + (cam.x - 960) * d), -(540 + (cam.y - 540) * d));
  fn();
  ctx.restore();
}
function shake(t, amp, speed = 9, seed = 1) {
  return { x: noise1(t * speed, seed) * amp, y: noise1(t * speed, seed + 7) * amp, r: noise1(t * speed * 0.7, seed + 3) * amp * 0.0006 };
}
function camLerp(a, b, k) {
  return { x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k), z: lerp(a.z, b.z, k), r: lerp(a.r || 0, b.r || 0, k) };
}

// ---------- post FX ----------
const FX = { grain: [], vignette: null, dust: [] };
function initFX() {
  for (let k = 0; k < 8; k++) {
    const c = makeCanvas(384, 384), g = c.getContext('2d');
    const id = g.createImageData(384, 384), r = mulberry32(1000 + k);
    for (let i = 0; i < id.data.length; i += 4) {
      const v = 128 + (r() + r() + r() - 1.5) * 120;
      id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255;
    }
    g.putImageData(id, 0, 0);
    FX.grain.push(c);
  }
  const v = makeCanvas(W, H), g = v.getContext('2d');
  const gr = g.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  gr.addColorStop(0, 'rgba(0,0,0,0)');
  gr.addColorStop(0.6, 'rgba(0,0,0,0.35)');
  gr.addColorStop(1, 'rgba(0,0,0,0.92)');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  FX.vignette = v;
  const r = mulberry32(77);
  for (let i = 0; i < 90; i++) FX.dust.push({ x: r() * W, y: r() * H, s: 0.6 + r() * 2.2, v: 4 + r() * 14, ph: r() * 6.28, a: 0.15 + r() * 0.5 });
}
function postFX(ctx, t, frame, opts = {}) {
  // vignette
  ctx.save(); if (opts.flat) ctx.globalAlpha = 0.45; ctx.drawImage(FX.vignette, 0, 0); ctx.restore();
  // film grain (changes every frame)
  const tile = FX.grain[frame % FX.grain.length];
  const r = mulberry32(frame * 13 + 5);
  const ox = -Math.floor(r() * 384), oy = -Math.floor(r() * 384);
  ctx.save();
  ctx.globalCompositeOperation = 'overlay';
  ctx.globalAlpha = opts.grain ?? 0.16;
  for (let y = oy; y < H; y += 384) for (let x = ox; x < W; x += 384) ctx.drawImage(tile, x, y);
  ctx.restore();
  // subtle exposure flicker
  const fl = 0.025 * (noise1(t * 11, 9) * 0.5 + 0.5);
  ctx.fillStyle = `rgba(0,0,0,${fl})`;
  ctx.fillRect(0, 0, W, H);
  // rare film specks
  if (r() < 0.12) {
    ctx.fillStyle = `rgba(220,225,235,${0.08 + r() * 0.1})`;
    ctx.beginPath(); ctx.arc(r() * W, r() * H, 0.8 + r() * 1.8, 0, 7); ctx.fill();
  }
}
// floating dust in a light cone
function dust(ctx, t, cx, cy, rad, alpha = 1, seed = 0) {
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < FX.dust.length; i++) {
    const d = FX.dust[(i + seed) % FX.dust.length];
    const x = cx + ((d.x + Math.sin(t * 0.3 + d.ph) * 40 + t * d.v * 0.6) % (rad * 2)) - rad;
    const y = cy + ((d.y - t * d.v + 4000) % (rad * 2)) - rad;
    const dd = Math.hypot(x - cx, y - cy) / rad;
    if (dd > 1) continue;
    const a = d.a * alpha * (1 - dd) * (0.6 + 0.4 * Math.sin(t * 2 + d.ph));
    ctx.fillStyle = `rgba(200,215,240,${a})`;
    ctx.beginPath(); ctx.arc(x, y, d.s, 0, 7); ctx.fill();
  }
  ctx.restore();
}
