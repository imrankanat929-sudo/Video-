// Shared helpers + drawing primitives (flat 2D documentary style)
const { createCanvas, GlobalFonts, Path2D } = require('@napi-rs/canvas');
const path = require('path');
const FONTS = path.join(__dirname, '..', 'fonts');
GlobalFonts.registerFromPath(path.join(FONTS, 'Oswald-Bold.ttf'), 'OswaldBold');
GlobalFonts.registerFromPath(path.join(FONTS, 'Oswald-Medium.ttf'), 'OswaldMed');
GlobalFonts.registerFromPath(path.join(FONTS, 'PTSans-Regular.ttf'), 'PTSans');
GlobalFonts.registerFromPath(path.join(FONTS, 'PTSans-Bold.ttf'), 'PTSansBold');
GlobalFonts.registerFromPath(path.join(FONTS, 'PTSerif-Bold.ttf'), 'PTSerifBold');

const W = 1920, H = 1080;
function rng(seed) {
  let s = seed >>> 0;
  return () => { s = (s + 0x6D2B79F5) >>> 0; let t = s; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const ease = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const easeS = t => -(Math.cos(Math.PI * clamp(t)) - 1) / 2;
const easeOut = t => 1 - Math.pow(1 - clamp(t), 3);
function hex(h) { h = h.replace('#', ''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
function mix(a, b, t) { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => Math.round(lerp(v, B[i], clamp(t))).toString(16).padStart(2, '0')).join(''); }
function rgba(h, a) { const c = hex(h); return `rgba(${c[0]},${c[1]},${c[2]},${a})`; }
function canvas(w, h) { return createCanvas(Math.ceil(w), Math.ceil(h)); }

// smooth 1D value noise
function noise1(seed) {
  const r = rng(seed); const v = Array.from({ length: 512 }, r);
  return x => { const i = Math.floor(x), f = x - i; const a = v[((i % 512) + 512) % 512], b = v[(((i + 1) % 512) + 512) % 512]; const u = f * f * (3 - 2 * f); return a + (b - a) * u; };
}

function rrect(ctx, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
function ellipse(ctx, x, y, rx, ry, rot = 0) { ctx.beginPath(); ctx.ellipse(x, y, Math.abs(rx), Math.abs(ry), rot, 0, Math.PI * 2); }
function glow(ctx, x, y, r, col, a) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, rgba(col, a)); g.addColorStop(0.35, rgba(col, a * 0.45)); g.addColorStop(1, rgba(col, 0));
  ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
}
// volumetric beam: from apex (x,y) spreading to (x1,y1)-(x2,y2)
function beam(ctx, x, y, x1, y1, x2, y2, col, a) {
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let k = 0; k < 3; k++) {
    const sp = 1 + k * 0.12; const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const ax = mx + (x1 - mx) * sp, ay = my + (y1 - my) * sp, bx = mx + (x2 - mx) * sp, by = my + (y2 - my) * sp;
    const g = ctx.createLinearGradient(x, y, mx, my);
    g.addColorStop(0, rgba(col, a / (k + 1))); g.addColorStop(1, rgba(col, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(ax, ay); ctx.lineTo(bx, by); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

// ---------- soft cloud / fog textures ----------
function fogTexture(seed, w, h, col, n, rmin, rmax, amin, amax) {
  const c = canvas(w, h), x = c.getContext('2d'), r = rng(seed);
  for (let i = 0; i < n; i++) {
    const px = r() * w, py = h * (0.25 + r() * 0.5), rr = rmin + r() * (rmax - rmin);
    for (const off of [0, -w, w]) {
      const g = x.createRadialGradient(px + off, py, 0, px + off, py, rr);
      const a = amin + r() * (amax - amin);
      g.addColorStop(0, rgba(col, a)); g.addColorStop(1, rgba(col, 0));
      x.fillStyle = g; x.save(); x.translate(px + off, py); x.scale(1, 0.45); x.translate(-px - off, -py);
      x.fillRect(px + off - rr, py - rr, rr * 2, rr * 2); x.restore();
    }
  }
  return c;
}
// tile a horizontally-wrapping texture across the screen
function drawWrap(ctx, tex, offX, y, scaleY = 1, alpha = 1, sw = W) {
  ctx.save(); ctx.globalAlpha = alpha;
  const tw = tex.width; let ox = ((offX % tw) + tw) % tw;
  for (let x = -ox; x < sw; x += tw) ctx.drawImage(tex, x, y, tw, tex.height * scaleY);
  ctx.restore();
}

function skyGradient(ctx, w, h, stops) {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  stops.forEach(([o, c]) => g.addColorStop(o, c));
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
}

function cloudLayer(seed, w, h, cols) {
  const c = canvas(w, h), x = c.getContext('2d'), r = rng(seed);
  for (let i = 0; i < 70; i++) {
    const px = r() * w, py = h * (0.1 + r() * 0.75), rr = 120 + r() * 260;
    const col = cols[Math.floor(r() * cols.length)];
    for (const off of [0, -w, w]) {
      const g = x.createRadialGradient(px + off, py, 0, px + off, py, rr);
      g.addColorStop(0, rgba(col, 0.5)); g.addColorStop(0.6, rgba(col, 0.25)); g.addColorStop(1, rgba(col, 0));
      x.save(); x.translate(px + off, py); x.scale(1.6, 0.42); x.translate(-px - off, -py);
      x.fillStyle = g; x.fillRect(px + off - rr, py - rr, rr * 2, rr * 2); x.restore();
    }
  }
  return c;
}

// ---------- architecture ----------
// Timber-framed medieval house. Returns lit-window rects (for live lighting).
function house(ctx, x, by, w, h, o, r) {
  const fl = o.floors || 2, fh = h / fl, lights = [];
  const tim = o.timber, pl = o.plaster;
  for (let f = 0; f < fl; f++) {
    const ov = f * (o.jetty ?? 10), fx = x - ov, fw = w + ov * 2, fy = by - (f + 1) * fh - (f ? 0 : 0);
    ctx.fillStyle = pl; ctx.fillRect(fx, fy, fw, fh);
    // subtle shade gradient
    const g = ctx.createLinearGradient(fx, 0, fx + fw, 0); g.addColorStop(0, 'rgba(0,0,0,0.18)'); g.addColorStop(0.5, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.25)');
    ctx.fillStyle = g; ctx.fillRect(fx, fy, fw, fh);
    if (o.timbered !== false) {
      ctx.fillStyle = tim; const bt = Math.max(4, w * 0.035);
      ctx.fillRect(fx, fy, fw, bt); ctx.fillRect(fx, fy + fh - bt, fw, bt);
      const np = Math.max(2, Math.round(fw / 55));
      for (let i = 0; i <= np; i++) ctx.fillRect(fx + (fw - bt) * i / np, fy, bt, fh);
      ctx.strokeStyle = tim; ctx.lineWidth = bt * 0.8;
      for (let i = 0; i < np; i++) if ((i + f + o.seedOff) % 3 === 0) {
        const ax = fx + (fw - bt) * i / np + bt / 2, bx = fx + (fw - bt) * (i + 1) / np + bt / 2;
        ctx.beginPath(); ctx.moveTo(ax, fy + fh); ctx.lineTo(bx, fy); ctx.stroke();
      }
    }
    if (f > 0) { ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(fx + ov / 2, fy + fh, fw - ov, 7); }
    // windows
    const nw = Math.max(1, Math.round(fw / 90));
    for (let i = 0; i < nw; i++) {
      if (f === 0 && i === Math.floor(nw / 2) && o.door !== false) continue;
      const ww = Math.min(34, fw / nw * 0.42), wh = fh * 0.42;
      const wx = fx + fw * (i + 0.5) / nw - ww / 2, wy = fy + fh * 0.28;
      ctx.fillStyle = '#121216'; rrect(ctx, wx, wy, ww, wh, ww * 0.45); ctx.fill();
      ctx.fillStyle = tim; ctx.fillRect(wx - 3, wy + wh, ww + 6, 4);
      if (r() < (o.litChance ?? 0.35)) lights.push({ x: wx, y: wy, w: ww, h: wh, ph: r() * 10, off: r() });
      else if (r() < 0.5) { // shutters
        ctx.fillStyle = mix(tim, '#000000', 0.2); ctx.fillRect(wx - ww * 0.55, wy, ww * 0.5, wh); ctx.fillRect(wx + ww * 1.05, wy, ww * 0.5, wh);
      }
    }
    if (f === 0 && o.door !== false) {
      const dw = Math.min(46, fw * 0.25), dh = fh * 0.72, dx = fx + fw / 2 - dw / 2;
      ctx.fillStyle = mix(tim, '#000000', 0.25); ctx.beginPath(); ctx.moveTo(dx, by); ctx.lineTo(dx, by - dh + dw / 2);
      ctx.arc(dx + dw / 2, by - dh + dw / 2, dw / 2, Math.PI, 0); ctx.lineTo(dx + dw, by); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 2;
      for (let k = 1; k < 4; k++) { ctx.beginPath(); ctx.moveTo(dx + dw * k / 4, by); ctx.lineTo(dx + dw * k / 4, by - dh + 8); ctx.stroke(); }
      if (o.boarded) { ctx.fillStyle = '#5a4630'; ctx.save(); ctx.translate(dx + dw / 2, by - dh / 2); ctx.rotate(0.5); ctx.fillRect(-dw * 0.8, -5, dw * 1.6, 10); ctx.rotate(-1); ctx.fillRect(-dw * 0.8, -5, dw * 1.6, 10); ctx.restore(); }
    }
  }
  // roof (gable to street)
  const top = by - h, ovr = (fl - 1) * (o.jetty ?? 10) + 14, rh = o.roofH ?? w * 0.75;
  ctx.fillStyle = o.roof; ctx.beginPath(); ctx.moveTo(x - ovr, top + 2); ctx.lineTo(x + w / 2, top - rh); ctx.lineTo(x + w + ovr, top + 2); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,0.05)'; ctx.beginPath(); ctx.moveTo(x - ovr, top + 2); ctx.lineTo(x + w / 2, top - rh); ctx.lineTo(x + w / 2, top + 2); ctx.closePath(); ctx.fill();
  // gable plaster triangle w/ small window
  ctx.fillStyle = pl; ctx.beginPath(); ctx.moveTo(x - ovr + 22, top); ctx.lineTo(x + w / 2, top - rh + 26); ctx.lineTo(x + w + ovr - 22, top); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fill();
  if (o.timbered !== false) { ctx.fillStyle = tim; ctx.fillRect(x + w / 2 - 3, top - rh + 30, 6, rh - 30); }
  const gw = 16, gy = top - rh * 0.42;
  ctx.fillStyle = '#121216'; rrect(ctx, x + w / 2 - gw - 8, gy, gw, 26, 7); ctx.fill();
  if (r() < (o.litChance ?? 0.35) * 0.6) lights.push({ x: x + w / 2 - gw - 8, y: gy, w: gw, h: 26, ph: r() * 10, off: r() });
  // chimney
  if (o.chimney) { const cx = x + w * (0.65 + r() * 0.15); ctx.fillStyle = mix(o.roof, '#000000', 0.2); ctx.fillRect(cx, top - rh * 0.75, 22, rh * 0.5); lights.push({ chimney: true, x: cx + 11, y: top - rh * 0.75 }); }
  return lights;
}

function church(ctx, x, by, s, col, winCol) {
  ctx.save(); ctx.translate(x, by); ctx.scale(s, s); ctx.fillStyle = col;
  // nave
  ctx.fillRect(-260, -260, 360, 260);
  ctx.beginPath(); ctx.moveTo(-275, -258); ctx.lineTo(-80, -400); ctx.lineTo(115, -258); ctx.fill();
  // tower
  ctx.fillRect(90, -520, 130, 520);
  ctx.beginPath(); ctx.moveTo(78, -515); ctx.lineTo(155, -820); ctx.lineTo(232, -515); ctx.fill();
  for (const px of [90, 205]) { ctx.beginPath(); ctx.moveTo(px - 6, -515); ctx.lineTo(px + 7, -590); ctx.lineTo(px + 20, -515); ctx.fill(); }
  // windows
  ctx.fillStyle = winCol;
  for (let i = 0; i < 4; i++) { const wx = -230 + i * 80; ctx.beginPath(); ctx.moveTo(wx, -60); ctx.lineTo(wx, -170); ctx.quadraticCurveTo(wx + 15, -205, wx + 30, -170); ctx.lineTo(wx + 30, -60); ctx.fill(); }
  ctx.beginPath(); ctx.arc(-80, -310, 30, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.moveTo(140, -380); ctx.lineTo(140, -440); ctx.quadraticCurveTo(155, -470, 170, -440); ctx.lineTo(170, -380); ctx.fill();
  ctx.restore();
}

// distant skyline silhouette strip
function skyline(seed, w, h, col, base, opt = {}) {
  const c = canvas(w, h), x = c.getContext('2d'), r = rng(seed); x.fillStyle = col;
  let px = -20; const lights = [];
  while (px < w) {
    const bw = 50 + r() * 90, bh = (opt.minH ?? 60) + r() * (opt.varH ?? 120);
    x.fillRect(px, base - bh, bw, h - base + bh);
    const rh = bw * (0.5 + r() * 0.5);
    x.beginPath(); x.moveTo(px - 6, base - bh + 1); x.lineTo(px + bw / 2, base - bh - rh); x.lineTo(px + bw + 6, base - bh + 1); x.fill();
    if (r() < 0.3) x.fillRect(px + bw * 0.7, base - bh - rh * 0.8, 12, rh * 0.6);
    if (opt.lights && r() < 0.5) lights.push({ x: px + bw * (0.2 + r() * 0.6), y: base - bh * (0.3 + r() * 0.5), w: 7, h: 10, ph: r() * 10, off: r() });
    px += bw - 4;
  }
  if (opt.church) for (const cx of opt.church) church(x, cx, base + 10, opt.churchS ?? 0.8, col, col);
  return { c, lights };
}

// cobblestone street plane
function cobbles(ctx, x0, y0, w, h, seed, c1, c2) {
  const r = rng(seed);
  ctx.fillStyle = c1; ctx.fillRect(x0, y0, w, h);
  let y = y0 + 4, row = 0;
  while (y < y0 + h) {
    const sh = 6 + (y - y0) / h * 22, sw = sh * 1.8;
    let x = x0 - (row % 2) * sw / 2;
    while (x < x0 + w) {
      ctx.fillStyle = mix(c1, c2, 0.3 + r() * 0.7); rrect(ctx, x + 2, y, sw - 4, sh - 3, sh * 0.4); ctx.fill();
      x += sw;
    }
    y += sh; row++;
  }
}

// ---------- people ----------
const SKIN = '#c49a72';
function person(ctx, x, y, s, o, t = 0) {
  const d = o.dir ?? 1, side = o.dir !== 0;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const walking = o.walk != null; const p = o.walk || 0;
  const sw = walking ? Math.sin(p) : 0;
  const bob = walking ? -Math.abs(Math.cos(p)) * 5 : Math.sin(t * 1.3 + (o.ph || 0)) * 1.2;
  const skin = o.skin || SKIN, tun = o.tunic || '#2b2a2f', hose = o.hose || '#1d1d22', shoe = o.shoe || '#3b3530';
  const leg = (ang, col) => { ctx.save(); ctx.translate(0, -112 + bob); ctx.rotate(ang); ctx.fillStyle = col; rrect(ctx, -11, 0, 22, 110, 9); ctx.fill(); ctx.fillStyle = shoe; ellipse(ctx, side ? d * 8 : 0, 108, side ? 22 : 15, 9); ctx.fill(); ctx.restore(); };
  const arm = (ang, col, front) => { ctx.save(); ctx.translate(side ? 0 : (front ? 34 : -34), -268 + bob); ctx.rotate(ang); ctx.fillStyle = col; rrect(ctx, -11, -6, 22, 112, 10); ctx.fill(); ctx.fillStyle = skin; ellipse(ctx, 0, 110, 13, 13); ctx.fill(); ctx.restore(); };
  const tunDark = mix(tun, '#000000', 0.3);
  if (!o.dress) {
    if (side) { leg(-sw * 0.38, mix(hose, '#000000', 0.3)); leg(sw * 0.38, hose); }
    else { ctx.save(); ctx.translate(-14, 0); leg(0, hose); ctx.restore(); ctx.save(); ctx.translate(14, 0); leg(0, hose); ctx.restore(); }
  } else {
    ctx.fillStyle = shoe; ellipse(ctx, d * 10 + sw * 14, -4, 18, 8); ctx.fill();
  }
  const armBack = o.armBack ?? (side ? sw * 0.45 : 0.12);
  if (side) arm(armBack, tunDark, false); else arm(0.12, tun, false);
  // torso / tunic
  ctx.fillStyle = tun; const hem = o.dress ? -2 : (o.robe ? -18 : -96), tw = side ? 30 : 40, bw = o.dress || o.robe ? (side ? 52 + Math.abs(sw) * 10 : 62) : (side ? 40 : 50);
  ctx.beginPath(); ctx.moveTo(-tw, -282 + bob); ctx.quadraticCurveTo(0, -292 + bob, tw, -282 + bob);
  ctx.lineTo(bw, hem + bob); ctx.quadraticCurveTo(0, hem + 8 + bob, -bw, hem + bob); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.moveTo(side ? -d * tw : tw * 0.2, -282 + bob); ctx.lineTo(side ? -d * bw : bw * 0.3, hem + bob); ctx.lineTo(side ? -d * bw * 0.3 : bw, hem + bob); ctx.lineTo(side ? -d * tw * 0.2 : tw, -282 + bob); ctx.fill();
  if (o.belt) { ctx.fillStyle = o.belt; ctx.fillRect(-bw * 0.62, -175 + bob, bw * 1.24, 9); }
  if (o.apron) { ctx.fillStyle = o.apron; rrect(ctx, side ? d * 2 - 22 : -26, -190 + bob, 48, o.dress ? 170 : 90, 8); ctx.fill(); }
  // front arm
  const armF = o.armFront ?? (side ? -sw * 0.45 : -0.12);
  if (side) arm(armF, tun, true); else arm(-0.12, tun, true);
  // neck + head
  ctx.fillStyle = mix(skin, '#000000', 0.15); ctx.fillRect(-9, -300 + bob, 18, 22);
  const hy = -330 + bob, hr = 44;
  if (o.hood) { ctx.fillStyle = o.hood; ellipse(ctx, -d * (side ? 8 : 0), hy - 2, hr + 12, hr + 14); ctx.fill(); ctx.beginPath(); ctx.moveTo(-40, hy + 30); ctx.lineTo(40, hy + 30); ctx.lineTo(58, -270 + bob); ctx.lineTo(-58, -270 + bob); ctx.fill(); if (side) { ctx.beginPath(); ctx.moveTo(-d * 30, hy - 30); ctx.quadraticCurveTo(-d * 90, hy, -d * 70, hy + 90); ctx.lineTo(-d * 55, hy + 80); ctx.quadraticCurveTo(-d * 60, hy, -d * 20, hy - 40); ctx.fill(); } }
  if (o.veil) { ctx.fillStyle = o.veil; ellipse(ctx, -d * (side ? 6 : 0), hy - 4, hr + 8, hr + 10); ctx.fill(); ctx.beginPath(); ctx.moveTo(-hr - 8, hy); ctx.lineTo(hr + 8, hy); ctx.lineTo(hr + 16, -262 + bob); ctx.lineTo(-hr - 16, -262 + bob); ctx.fill(); }
  ctx.fillStyle = skin; ellipse(ctx, side ? d * 4 : 0, hy, hr, hr); ctx.fill();
  if (o.veil) { ctx.fillStyle = o.veil; ctx.beginPath(); ctx.arc(side ? d * 4 : 0, hy, hr + 2, Math.PI * 1.02, Math.PI * 1.98); ctx.quadraticCurveTo(side ? d * 4 : 0, hy - 18, -hr, hy - 6); ctx.fill(); }
  if (o.hood) { ctx.fillStyle = o.hood; ctx.beginPath(); ctx.arc(side ? d * 4 : 0, hy, hr + 3, Math.PI * 1.0, Math.PI * 2.0); ctx.quadraticCurveTo(side ? d * 4 : 0, hy - 14, -hr - 3, hy); ctx.fill(); ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.beginPath(); ctx.arc(side ? d * 4 : 0, hy, hr + 1, Math.PI * 1.05, Math.PI * 1.95); ctx.lineTo(side ? d * 4 : 0, hy - 18); ctx.fill(); }
  if (o.cap) { ctx.fillStyle = o.cap; ctx.beginPath(); ctx.arc(side ? d * 4 : 0, hy - 4, hr + 2, Math.PI * 1.08, Math.PI * 1.92); ctx.closePath(); ctx.fill(); ctx.fillRect(-hr + (side ? d * 4 : 0), hy - 22, hr * 2, 8); }
  if (o.hair === 'messy') messyHair(ctx, side ? d * 4 : 0, hy, hr, d, side, o.hairCol || '#121214');
  if (o.hair === 'short') { ctx.fillStyle = o.hairCol || '#2a2018'; ctx.beginPath(); ctx.arc(side ? d * 4 : 0, hy - 2, hr + 2, Math.PI * 1.05, Math.PI * 1.95); ctx.quadraticCurveTo(side ? d * 10 : 0, hy - 22, -hr, hy - 4); ctx.fill(); if (side) { ctx.beginPath(); ctx.ellipse(-d * 20, hy - 6, 26, 30, 0, 0, Math.PI * 2); ctx.fill(); } }
  if (o.mask) { ctx.fillStyle = o.mask; ctx.beginPath(); ctx.moveTo((side ? d * 4 : 0) - hr * 0.95, hy + 8); ctx.quadraticCurveTo(side ? d * (hr + 14) : 0, hy + 4, (side ? d * 4 : 0) + hr * 0.95, hy + 8); ctx.quadraticCurveTo(side ? d * 30 : 0, hy + 52, (side ? d * 4 : 0) - hr * 0.8, hy + 26); ctx.fill(); }
  face(ctx, side ? d * 4 : 0, hy, d, side, o.look || 0, o.brows || 'neutral', o.mouth, t, o.blink !== false);
  // held lantern
  if (o.lantern) {
    const lx = side ? d * 70 : 40, ly = -170 + bob;
    ctx.strokeStyle = '#1a1714'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(lx, ly - 30); ctx.lineTo(lx, ly - 14); ctx.stroke();
    ctx.fillStyle = '#2a241d'; ctx.fillRect(lx - 13, ly - 14, 26, 34); ctx.fillStyle = '#f0c46a'; ctx.fillRect(lx - 8, ly - 8, 16, 22);
    ctx.fillStyle = '#2a241d'; ctx.beginPath(); ctx.moveTo(lx - 15, ly - 14); ctx.lineTo(lx, ly - 26); ctx.lineTo(lx + 15, ly - 14); ctx.fill();
  }
  if (o.staff) { ctx.strokeStyle = '#3a2c1e'; ctx.lineWidth = 7; ctx.beginPath(); ctx.moveTo(d * 52 + sw * 20, -6); ctx.lineTo(d * 44, -220 + bob); ctx.stroke(); }
  ctx.restore();
  if (o.lantern) { const lx = x + (side ? d * 70 : 40) * s, ly = y + (-170) * s; return { lx, ly }; }
  return null;
}
function messyHair(ctx, cx0, hy, hr, d, side, col) {
  ctx.save(); ctx.translate(cx0, 0); if (side && d < 0) ctx.scale(-1, 1);
  ctx.fillStyle = col; const ox = side ? -6 : 0, cy = hy - 8, n = 15;
  ctx.beginPath();
  for (let i = 0; i <= n; i++) {
    const a = Math.PI * (0.93 + 1.14 * i / n), tip = i % 2 === 0;
    const rr = tip ? hr + 9 + ((i * 7) % 3) * 3 : hr + 3;
    const px = ox + Math.cos(a) * rr * 1.08, py = cy + Math.sin(a) * rr;
    if (!i) ctx.moveTo(px, py);
    else { const pa = Math.PI * (0.93 + 1.14 * (i - 0.6) / n); ctx.quadraticCurveTo(ox + Math.cos(pa) * (hr + 10) * 1.08, cy + Math.sin(pa) * (hr + 10), px, py); }
  }
  if (side) [[1.02, -18], [0.8, -27], [0.58, -20], [0.36, -29], [0.12, -22], [-0.2, -28], [-0.62, 4], [-0.98, 12]].forEach(([fx, fy]) => ctx.lineTo(fx * hr, hy + fy));
  else [[0.98, 4], [0.86, -20], [0.62, -30], [0.4, -22], [0.14, -31], [-0.12, -23], [-0.4, -31], [-0.66, -21], [-0.86, -27], [-1.02, 6]].forEach(([fx, fy]) => ctx.lineTo(fx * hr, hy + fy));
  ctx.closePath(); ctx.fill();
  ctx.restore();
}
function face(ctx, cx, hy, d, side, look, brows, mouth, t, blink) {
  const bl = blink && t > 0.5 && ((t * 0.31 + Math.abs(cx) * 0.013) % 1) < 0.035 ? 0.12 : 1;
  ctx.fillStyle = '#0d0d0f';
  const eyes = side ? [cx + d * 20 + look * 3] : [cx - 15 + look * 4, cx + 15 + look * 4];
  eyes.forEach(x => { ellipse(ctx, x, hy, 6.5, 10.5 * bl); ctx.fill(); });
  ctx.strokeStyle = '#0d0d0f'; ctx.lineWidth = 5; ctx.lineCap = 'round';
  const by = hy - 19;
  eyes.forEach((x, i) => {
    const inner = side ? -d : (i === 0 ? 1 : -1); // direction toward nose
    const lift = brows === 'worried' ? 5 : brows === 'sad' ? 7 : brows === 'angry' ? -6 : 0;
    ctx.beginPath(); ctx.moveTo(x - inner * 10, by + lift * 0.4); ctx.lineTo(x + inner * 9, by - lift); ctx.stroke();
  });
  ctx.lineWidth = 3.5;
  const mx = side ? cx + d * 18 : cx + look * 3;
  if (mouth === 'o') { ctx.fillStyle = '#2a1414'; ellipse(ctx, mx, hy + 24, 5, 7); ctx.fill(); }
  else if (mouth === 'flat') { ctx.beginPath(); ctx.moveTo(mx - 7, hy + 24); ctx.lineTo(mx + 7, hy + 24); ctx.stroke(); }
  else if (mouth === 'frown') { ctx.beginPath(); ctx.arc(mx, hy + 32, 8, Math.PI * 1.2, Math.PI * 1.8); ctx.stroke(); }
}

// Bactrian camel, side view, feet at (0,0)
function camel(ctx, x, y, s, d, p, col, packs) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * d, s);
  const dark = mix(col, '#000000', 0.3), bob = Math.sin(p * 2) * 3;
  const leg = (lx, ph, c) => { const a = Math.sin(p + ph) * 0.35; ctx.save(); ctx.translate(lx, -128 + bob); ctx.rotate(a); ctx.fillStyle = c; rrect(ctx, -8, 0, 16, 74, 6); ctx.fill(); ctx.translate(0, 70); ctx.rotate(-Math.max(0, a) * 1.2); rrect(ctx, -7, 0, 14, 58, 6); ctx.fill(); ellipse(ctx, 4, 58, 13, 6); ctx.fill(); ctx.restore(); };
  leg(-60, Math.PI, dark); leg(55, 0, dark);
  ctx.fillStyle = col; ellipse(ctx, 0, -160 + bob, 95, 48); ctx.fill();
  ellipse(ctx, -35, -205 + bob, 30, 34); ctx.fill(); ellipse(ctx, 32, -205 + bob, 30, 34); ctx.fill();
  // neck + head
  ctx.beginPath(); ctx.moveTo(70, -185 + bob); ctx.quadraticCurveTo(120, -160 + bob, 128, -230 + bob); ctx.lineTo(150, -250 + bob); ctx.lineTo(166, -236 + bob); ctx.quadraticCurveTo(150, -200 + bob, 140, -150 + bob); ctx.quadraticCurveTo(120, -125 + bob, 75, -135 + bob); ctx.fill();
  ellipse(ctx, 152, -246 + bob, 26, 15, 0.2); ctx.fill();
  ctx.fillStyle = '#0d0d0f'; ellipse(ctx, 156, -254 + bob, 3.5, 4.5); ctx.fill();
  ctx.fillStyle = dark; ellipse(ctx, 140, -262 + bob, 6, 9, -0.4); ctx.fill();
  leg(-48, 0, col); leg(68, Math.PI, col);
  if (packs) { packs.forEach((pc, i) => { ctx.fillStyle = pc; rrect(ctx, -70 + i * 48, -205 + bob, 44, 62, 10); ctx.fill(); ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.fillRect(-70 + i * 48, -180 + bob, 44, 6); }); }
  ctx.strokeStyle = dark; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-92, -165 + bob); ctx.quadraticCurveTo(-110, -130 + bob, -100, -110 + bob); ctx.stroke();
  ctx.restore();
}

// medieval cog ship; (x,y)= waterline center
function cog(ctx, x, y, s, d, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(Math.sin(t * 0.9 + (o.ph || 0)) * 0.025); ctx.scale(s * d, s);
  const hull = o.hull || '#3b2c20', dark = mix(hull, '#000000', 0.35);
  // mast + rigging
  ctx.strokeStyle = '#1e1813'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(0, -470); ctx.lineTo(-250, -60); ctx.moveTo(0, -470); ctx.lineTo(240, -70); ctx.moveTo(0, -470); ctx.lineTo(-120, -50); ctx.stroke();
  ctx.fillStyle = '#241c15'; ctx.fillRect(-7, -480, 14, 440);
  // sail
  const bil = 30 + Math.sin(t * 1.3) * 6;
  ctx.fillStyle = o.sail || '#b8ab8f'; ctx.beginPath(); ctx.moveTo(-120, -420); ctx.quadraticCurveTo(-4 + bil, -415, 120, -420); ctx.quadraticCurveTo(120 + bil, -280, 126, -150); ctx.quadraticCurveTo(0 + bil, -135, -126, -150); ctx.quadraticCurveTo(-120 + bil * 0.6, -280, -120, -420); ctx.fill();
  ctx.fillStyle = o.stripe || '#6e2a22'; ctx.globalAlpha = 0.85;
  for (const sx of [-60, 30]) { ctx.beginPath(); ctx.moveTo(sx, -418); ctx.lineTo(sx + 30, -418); ctx.quadraticCurveTo(sx + 30 + bil * 0.8, -280, sx + 32, -143); ctx.lineTo(sx + 2, -142); ctx.quadraticCurveTo(sx + bil * 0.8, -280, sx, -418); ctx.fill(); }
  ctx.globalAlpha = 1; ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.moveTo(-126, -150); ctx.quadraticCurveTo(0 + bil, -135, 126, -150); ctx.lineTo(120, -220); ctx.quadraticCurveTo(0, -200, -120, -220); ctx.fill();
  ctx.fillStyle = '#241c15'; ctx.fillRect(-130, -428, 260, 9);
  // pennant
  ctx.fillStyle = o.stripe || '#6e2a22'; ctx.beginPath(); ctx.moveTo(0, -480); ctx.quadraticCurveTo(40, -490 + Math.sin(t * 5) * 6, 80, -478 + Math.sin(t * 5 + 1) * 8); ctx.lineTo(0, -462); ctx.fill();
  // hull
  ctx.fillStyle = hull; ctx.beginPath(); ctx.moveTo(-260, -110); ctx.lineTo(250, -110); ctx.quadraticCurveTo(240, -20, 180, 10); ctx.lineTo(-190, 10); ctx.quadraticCurveTo(-250, -20, -260, -110); ctx.fill();
  // castles
  ctx.fillRect(-268, -170, 110, 62); ctx.fillRect(160, -160, 100, 52);
  ctx.fillStyle = dark; for (let i = 0; i < 4; i++) ctx.fillRect(-250 + i * 26, -170, 12, 14); for (let i = 0; i < 4; i++) ctx.fillRect(172 + i * 24, -160, 12, 14);
  ctx.strokeStyle = dark; ctx.lineWidth = 3; for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.moveTo(-250 + k * 8, -85 + k * 22); ctx.quadraticCurveTo(0, -80 + k * 22, 240 - k * 14, -85 + k * 22); ctx.stroke(); }
  ctx.restore();
  return { lx: x - d * 210 * s, ly: y - 190 * s };
}

function yurt(ctx, x, by, s, col) {
  ctx.save(); ctx.translate(x, by); ctx.scale(s, s);
  ctx.fillStyle = col; ctx.fillRect(-70, -70, 140, 70);
  ctx.beginPath(); ctx.moveTo(-76, -68); ctx.quadraticCurveTo(-60, -125, 0, -128); ctx.quadraticCurveTo(60, -125, 76, -68); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(-70, -70, 140, 8); ctx.fillRect(0, -70, 70, 70);
  ctx.strokeStyle = 'rgba(0,0,0,0.2)'; ctx.lineWidth = 3; for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.moveTo(i * 26, -126 + Math.abs(i) * 8); ctx.lineTo(i * 34, -70); ctx.stroke(); }
  ctx.fillStyle = '#3a2416'; ctx.fillRect(-15, -48, 30, 48);
  ctx.restore();
}

function mountains(seed, w, h, base, amp, col, snow) {
  const c = canvas(w, h), x = c.getContext('2d'), n = noise1(seed), n2 = noise1(seed + 7);
  const pts = []; for (let i = 0; i <= w; i += 6) { const v = n(i / 260) * 0.65 + n2(i / 70) * 0.25 + n(i / 25 + 50) * 0.1; pts.push([i, base - v * amp]); }
  x.fillStyle = col; x.beginPath(); x.moveTo(0, h); pts.forEach(p => x.lineTo(p[0], p[1])); x.lineTo(w, h); x.fill();
  // ridge shading: right-facing slopes darker
  x.save(); x.beginPath(); x.moveTo(0, h); pts.forEach(p => x.lineTo(p[0], p[1])); x.lineTo(w, h); x.clip();
  x.fillStyle = 'rgba(0,0,0,0.16)';
  const sm = pts.map((p, i) => { let a = 0, c = 0; for (let k = -12; k <= 12; k++) { const q = pts[i + k]; if (q) { a += q[1]; c++; } } return a / c; });
  for (let i = 1; i < pts.length - 1; i++) {
    if (sm[i] < sm[i - 1] && sm[i] <= sm[i + 1]) {
      let v = i + 1; while (v < pts.length - 1 && sm[v + 1] >= sm[v]) v++;
      if (v - i < 6) continue;
      x.beginPath(); x.moveTo(pts[i][0], pts[i][1]); for (let k = i + 1; k <= v; k++) x.lineTo(pts[k][0], pts[k][1]);
      const dy = pts[v][1] - pts[i][1]; x.lineTo(pts[i][0] + (pts[v][0] - pts[i][0]) * 0.3, pts[v][1] + dy * 1.2); x.closePath(); x.fill();
    }
  }
  if (snow) { x.fillStyle = snow; x.beginPath(); pts.forEach((p, i) => { const sy = base - amp * 0.55 + n2(i * 0.3) * 30; i ? x.lineTo(p[0], Math.min(p[1] + 40, sy)) : x.moveTo(p[0], Math.min(p[1] + 40, sy)); }); for (let i = pts.length - 1; i >= 0; i--) x.lineTo(pts[i][0], pts[i][1] - 2); x.fill(); }
  x.restore();
  const g = x.createLinearGradient(0, base - amp, 0, h); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.25)'); x.globalCompositeOperation = 'source-atop'; x.fillStyle = g; x.fillRect(0, 0, w, h);
  return c;
}

// screen-space dust motes
function dust(ctx, t, seed, n, col, a, area = [0, 0, W, H]) {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const bx = r(), by = r(), sp = 0.2 + r(), sz = 1 + r() * 2.6, ph = r() * 7;
    const x = area[0] + ((bx * area[2] + t * 14 * sp + Math.sin(t * 0.5 + ph) * 20) % area[2]);
    const y = area[1] + ((by * area[3] - t * 6 * sp + area[3] * 10) % area[3]);
    ctx.fillStyle = rgba(col, a * (0.5 + 0.5 * Math.sin(t * 1.7 + ph))); ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
  }
}
// rising smoke puffs from a point
function smoke(ctx, x, y, t, seed, col, a, scale = 1) {
  const r = rng(seed);
  for (let i = 0; i < 9; i++) {
    const life = ((t * 0.18 + i / 9 + r() * 0.05) % 1);
    const px = x + Math.sin(life * 4 + i) * 12 * scale + life * 70 * scale, py = y - life * 220 * scale, rr = (10 + life * 50) * scale;
    const g = ctx.createRadialGradient(px, py, 0, px, py, rr);
    g.addColorStop(0, rgba(col, a * (1 - life) * Math.min(1, life * 6))); g.addColorStop(1, rgba(col, 0));
    ctx.fillStyle = g; ctx.fillRect(px - rr, py - rr, rr * 2, rr * 2);
  }
}

function windowLights(ctx, lights, t, kill = () => 1, warm = '#e8b45a') {
  for (const L of lights) {
    if (L.chimney) continue;
    const k = kill(L); if (k <= 0) continue;
    const fl = 0.85 + 0.15 * Math.sin(t * 7 + L.ph) * Math.sin(t * 3.1 + L.ph * 2);
    ctx.fillStyle = rgba(warm, 0.9 * k * fl); rrect(ctx, L.x, L.y, L.w, L.h, L.w * 0.45); ctx.fill();
    ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, L.x + L.w / 2, L.y + L.h / 2, L.w * 3.2, warm, 0.22 * k * fl); ctx.restore();
  }
}

function vignette(strength = 0.75) {
  const c = canvas(W, H), x = c.getContext('2d');
  const g = x.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${strength})`);
  x.fillStyle = g; x.fillRect(0, 0, W, H); return c;
}

function textC(ctx, str, x, y, font, col, spacing = 0, align = 'center') {
  ctx.font = font; ctx.letterSpacing = spacing + 'px'; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.fillStyle = col; ctx.fillText(str, x, y); ctx.letterSpacing = '0px';
}

module.exports = { W, H, rng, clamp, lerp, prog, ease, easeS, easeOut, mix, rgba, hex, canvas, noise1, rrect, ellipse, glow, beam, fogTexture, drawWrap, skyGradient, cloudLayer, house, church, skyline, cobbles, person, camel, cog, yurt, mountains, dust, smoke, windowLights, vignette, textC, Path2D, SKIN };
