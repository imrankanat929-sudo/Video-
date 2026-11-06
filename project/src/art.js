// Procedural illustrations: room, window & fog, desk, monitor, phone, hero.
'use strict';

const ART = {};

function initArt() {
  // --- fog sprites (pre-blurred) ---
  ART.fog = [];
  for (let k = 0; k < 3; k++) {
    const c = makeCanvas(1400, 420), g = c.getContext('2d'), r = mulberry32(300 + k);
    g.filter = 'blur(38px)';
    for (let i = 0; i < 26; i++) {
      g.fillStyle = `rgba(150,170,200,${0.05 + r() * 0.08})`;
      g.beginPath();
      g.ellipse(100 + r() * 1200, 140 + r() * 160, 90 + r() * 220, 40 + r() * 70, 0, 0, 7);
      g.fill();
    }
    ART.fog.push(c);
  }
  // --- distant city skyline for the window ---
  {
    const c = makeCanvas(1600, 700), g = c.getContext('2d'), r = mulberry32(42);
    let x = 0;
    while (x < 1600) {
      const w = 60 + r() * 140, h = 120 + r() * 380;
      g.fillStyle = `rgb(${16 + r() * 8},${22 + r() * 8},${34 + r() * 10})`;
      g.fillRect(x, 700 - h, w, h);
      for (let wy = 700 - h + 14; wy < 690; wy += 22) for (let wx = x + 8; wx < x + w - 10; wx += 18) {
        if (r() < 0.07) { g.fillStyle = `rgba(${200 + r() * 40},${180 + r() * 40},${140 + r() * 40},${0.25 + r() * 0.4})`; g.fillRect(wx, wy, 7, 9); }
      }
      x += w + r() * 20;
    }
    g.filter = 'blur(3px)';
    g.drawImage(c, 0, 0);
    ART.city = c;
  }
  // --- dark wood desk texture (top-down) ---
  {
    const c = makeCanvas(2600, 1700), g = c.getContext('2d'), r = mulberry32(9);
    g.fillStyle = '#0d1018'; g.fillRect(0, 0, 2600, 1700);
    for (let i = 0; i < 260; i++) {
      const y = r() * 1700;
      g.strokeStyle = `rgba(${40 + r() * 30},${44 + r() * 30},${56 + r() * 30},${0.05 + r() * 0.09})`;
      g.lineWidth = 1 + r() * 4;
      g.beginPath(); g.moveTo(0, y);
      for (let x = 0; x <= 2600; x += 100) g.lineTo(x, y + Math.sin(x * 0.003 + i) * 12 + (r() - 0.5) * 3);
      g.stroke();
    }
    // plank seams
    g.strokeStyle = 'rgba(0,0,0,0.6)'; g.lineWidth = 3;
    for (let y = 280; y < 1700; y += 420) { g.beginPath(); g.moveTo(0, y); g.lineTo(2600, y + 6); g.stroke(); }
    // mug ring + scratches
    g.strokeStyle = 'rgba(120,130,150,0.06)'; g.lineWidth = 6;
    g.beginPath(); g.arc(1980, 420, 95, 0.3, 5.6); g.stroke();
    for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(150,160,180,${r() * 0.05})`; g.lineWidth = 1; const x = r() * 2600, y = r() * 1700; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 120, y + (r() - 0.5) * 30); g.stroke(); }
    ART.desk = c;
  }
  // --- wall texture ---
  {
    const c = makeCanvas(2400, 1400), g = c.getContext('2d'), r = mulberry32(5);
    const gr = g.createLinearGradient(0, 0, 0, 1400);
    gr.addColorStop(0, '#0a0e17'); gr.addColorStop(1, '#101624');
    g.fillStyle = gr; g.fillRect(0, 0, 2400, 1400);
    for (let i = 0; i < 1400; i++) { g.fillStyle = `rgba(255,255,255,${r() * 0.012})`; g.fillRect(r() * 2400, r() * 1400, 1 + r() * 3, 20 + r() * 120); }
    ART.wall = c;
  }
  ART.hair = buildHair();
}

// ---------- window with night fog ----------
function drawWindow(ctx, t, x, y, w, h, o = {}) {
  ctx.save();
  rr(ctx, x, y, w, h, 4); ctx.clip();
  const sky = ctx.createLinearGradient(0, y, 0, y + h);
  sky.addColorStop(0, '#0e1726'); sky.addColorStop(0.7, '#1b2638'); sky.addColorStop(1, '#222d40');
  ctx.fillStyle = sky; ctx.fillRect(x, y, w, h);
  // moon haze
  glow(ctx, x + w * 0.72, y + h * 0.2, w * 0.5, 'rgba(150,170,205,0.35)', 0.6);
  // city (slow drift for depth)
  ctx.globalAlpha = 0.9;
  ctx.drawImage(ART.city, x - 200 + Math.sin(t * 0.05) * 6, y + h - 520, 1600 * (w / 900), 700 * (w / 900) * 0.75);
  ctx.globalAlpha = 1;
  // fog layers drifting
  for (let k = 0; k < 3; k++) {
    const sp = 8 + k * 6, fw = ART.fog[k].width;
    const ox = ((t * sp + k * 400) % fw);
    const fy = y + h * (0.25 + k * 0.22);
    ctx.globalAlpha = 0.85 * (o.fog ?? 1);
    ctx.drawImage(ART.fog[k], x - ox, fy - 200, fw, 420);
    ctx.drawImage(ART.fog[k], x - ox + fw, fy - 200, fw, 420);
  }
  ctx.globalAlpha = 1;
  // faint rain
  const r = mulberry32(Math.floor(t * 24));
  ctx.strokeStyle = 'rgba(170,190,220,0.08)'; ctx.lineWidth = 1;
  for (let i = 0; i < 40; i++) { const rx = x + r() * w, ry = y + r() * h; ctx.beginPath(); ctx.moveTo(rx, ry); ctx.lineTo(rx - 4, ry + 30); ctx.stroke(); }
  // glass reflection
  const gl = ctx.createLinearGradient(x, y, x + w, y + h);
  gl.addColorStop(0, 'rgba(255,255,255,0.04)'); gl.addColorStop(0.5, 'rgba(255,255,255,0)'); gl.addColorStop(0.55, 'rgba(255,255,255,0.03)'); gl.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = gl; ctx.fillRect(x, y, w, h);
  ctx.restore();
  // frame
  ctx.save();
  ctx.strokeStyle = '#06080d'; ctx.lineWidth = 22;
  rr(ctx, x, y, w, h, 4); ctx.stroke();
  ctx.lineWidth = 14;
  ctx.beginPath(); ctx.moveTo(x + w / 2, y); ctx.lineTo(x + w / 2, y + h); ctx.moveTo(x, y + h * 0.42); ctx.lineTo(x + w, y + h * 0.42); ctx.stroke();
  // sill
  ctx.fillStyle = '#0b0f17'; ctx.fillRect(x - 40, y + h + 8, w + 80, 22);
  ctx.fillStyle = 'rgba(140,160,200,0.12)'; ctx.fillRect(x - 40, y + h + 8, w + 80, 2);
  ctx.restore();
}

function drawCurtain(ctx, t, x, y, w, h) {
  ctx.save();
  for (let i = 0; i < 7; i++) {
    const fx = x + (i / 7) * w, sway = Math.sin(t * 0.6 + i) * 3;
    const g = ctx.createLinearGradient(fx, 0, fx + w / 7, 0);
    g.addColorStop(0, '#07090f'); g.addColorStop(0.5, '#111827'); g.addColorStop(1, '#07090f');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(fx, y); ctx.lineTo(fx + w / 7 + 2, y);
    ctx.quadraticCurveTo(fx + w / 7 + sway, y + h * 0.5, fx + w / 7 + sway * 2 + 2, y + h);
    ctx.lineTo(fx + sway * 2, y + h);
    ctx.quadraticCurveTo(fx + sway, y + h * 0.5, fx, y);
    ctx.fill();
  }
  ctx.restore();
}

// ---------- monitor ----------
function drawMonitor(ctx, x, y, w, h, screen, o = {}) {
  ctx.save();
  // stand
  ctx.fillStyle = '#07090e';
  ctx.beginPath(); ctx.moveTo(x + w / 2 - 30, y + h); ctx.lineTo(x + w / 2 + 30, y + h); ctx.lineTo(x + w / 2 + 40, y + h + 60); ctx.lineTo(x + w / 2 - 40, y + h + 60); ctx.fill();
  ctx.fillRect(x + w / 2 - 110, y + h + 56, 220, 12);
  // bezel
  ctx.fillStyle = '#05070b'; rr(ctx, x - 14, y - 14, w + 28, h + 28, 10); ctx.fill();
  ctx.strokeStyle = 'rgba(140,160,200,0.15)'; ctx.lineWidth = 2; ctx.stroke();
  // screen
  ctx.save(); rr(ctx, x, y, w, h, 3); ctx.clip();
  if (screen) ctx.drawImage(screen, x, y, w, h); else { ctx.fillStyle = '#0b1220'; ctx.fillRect(x, y, w, h); }
  ctx.fillStyle = `rgba(0,0,0,${1 - (o.bright ?? 1)})`; ctx.fillRect(x, y, w, h);
  // scanline sheen
  const sh = ctx.createLinearGradient(x, y, x + w, y + h);
  sh.addColorStop(0, 'rgba(255,255,255,0.05)'); sh.addColorStop(0.4, 'rgba(255,255,255,0)');
  ctx.fillStyle = sh; ctx.fillRect(x, y, w, h);
  ctx.restore();
  ctx.restore();
}

// ---------- phone (frontal) ----------
const PHONE = { w: 600, h: 1240, sw: 556, sh: 1196 };
function drawPhone(ctx, cx, cy, s, rot, screen, o = {}) {
  ctx.save();
  ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(s, s);
  const w = PHONE.w, h = PHONE.h;
  // contact shadow
  ctx.save(); ctx.filter = 'blur(30px)'; ctx.fillStyle = 'rgba(0,0,0,0.75)'; rr(ctx, -w / 2 + 20, -h / 2 + 40, w, h, 90); ctx.fill(); ctx.restore();
  // body
  const bg = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2);
  bg.addColorStop(0, '#1a1f2a'); bg.addColorStop(0.5, '#0a0c11'); bg.addColorStop(1, '#151a24');
  ctx.fillStyle = bg; rr(ctx, -w / 2, -h / 2, w, h, 86); ctx.fill();
  ctx.strokeStyle = 'rgba(170,185,210,0.25)'; ctx.lineWidth = 3; ctx.stroke();
  // screen
  const sw = PHONE.sw, sh = PHONE.sh;
  ctx.save(); rr(ctx, -sw / 2, -sh / 2, sw, sh, 66); ctx.clip();
  if (screen && (o.on ?? 1) > 0) {
    ctx.globalAlpha = o.on ?? 1;
    ctx.drawImage(screen, -sw / 2, -sh / 2, sw, sh);
    ctx.globalAlpha = 1;
  } else { ctx.fillStyle = '#020305'; ctx.fillRect(-sw / 2, -sh / 2, sw, sh); }
  // glass reflection
  const gl = ctx.createLinearGradient(-sw / 2, -sh / 2, sw / 2, sh / 2);
  gl.addColorStop(0, 'rgba(255,255,255,0.07)'); gl.addColorStop(0.35, 'rgba(255,255,255,0)'); gl.addColorStop(0.36, 'rgba(255,255,255,0.025)'); gl.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = gl; ctx.fillRect(-sw / 2, -sh / 2, sw, sh);
  ctx.restore();
  // camera pill
  ctx.fillStyle = '#000'; rr(ctx, -70, -sh / 2 + 22, 140, 38, 19); ctx.fill();
  ctx.restore();
}
// screen light spill on the surface under a phone
function phoneSpill(ctx, cx, cy, r, a, tint = 'rgba(160,190,255,0.55)') {
  glow(ctx, cx, cy, r, tint, a);
}

// ---------- desk top (top-down) ----------
function drawDeskTop(ctx, t, o = {}) {
  ctx.drawImage(ART.desk, -340, -310);
  // props: keyboard corner, pen, sticky note, cable
  ctx.save();
  // keyboard (top right)
  ctx.translate(1650, 120); ctx.rotate(-0.08);
  ctx.fillStyle = '#080a0f'; rr(ctx, 0, 0, 900, 300, 18); ctx.fill();
  ctx.strokeStyle = 'rgba(140,160,200,0.12)'; ctx.lineWidth = 2; ctx.stroke();
  for (let ry = 0; ry < 5; ry++) for (let kx = 0; kx < 14; kx++) {
    ctx.fillStyle = '#10141c'; rr(ctx, 22 + kx * 62, 24 + ry * 54, 52, 44, 7); ctx.fill();
    ctx.fillStyle = 'rgba(160,180,220,0.06)'; ctx.fillRect(26 + kx * 62, 26 + ry * 54, 44, 2);
  }
  ctx.restore();
  // sticky note
  ctx.save(); ctx.translate(250, 760); ctx.rotate(0.12);
  ctx.fillStyle = '#4d5462'; ctx.fillRect(0, 0, 220, 220);
  ctx.strokeStyle = 'rgba(10,12,18,0.6)'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(24, 60); ctx.lineTo(180, 56); ctx.moveTo(24, 100); ctx.lineTo(150, 102); ctx.moveTo(24, 140); ctx.lineTo(170, 136); ctx.stroke();
  ctx.restore();
  // pen
  ctx.save(); ctx.translate(1500, 900); ctx.rotate(-0.6);
  ctx.fillStyle = '#0a0c12'; rr(ctx, 0, 0, 360, 22, 11); ctx.fill();
  ctx.fillStyle = PAL.redDim; ctx.fillRect(300, 0, 60, 22);
  ctx.restore();
  // cable
  ctx.strokeStyle = '#050608'; ctx.lineWidth = 16; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(960, -300); ctx.bezierCurveTo(1100, 0, 820, 120, 980, 180); ctx.stroke();
}

// ---------- hero ----------
function buildHair() {
  // messy clumps around the head contour (head centre 0,0; r ~ 60)
  const r = mulberry32(2024), s = [];
  for (let i = 0; i < 34; i++) {
    const a = -Math.PI - 0.5 + (i / 33) * (Math.PI + 1.0) + (r() - 0.5) * 0.12;   // left side → top → right side
    s.push({ a, len: 14 + r() * 26, w: 26 + r() * 22, side: (r() - 0.5) * 0.9, ph: r() * 6 });
  }
  for (let i = 0; i < 5; i++) s.push({ a: Math.PI / 2 + (i - 2) * 0.32, len: 10 + r() * 10, w: 24 + r() * 10, side: (r() - 0.5) * 0.4, ph: r() * 6, nape: 1 });
  return s;
}
function drawHairStrands(ctx, t, rx, ry, col, wind = 0, profile = false, noMass = false) {
  ctx.fillStyle = col;
  // main mass
  if (!noMass) { ctx.beginPath(); ctx.ellipse(0, -10, rx + 7, ry + 2, 0, 0, 7); ctx.fill(); }
  for (const h of ART.hair) {
    const sway = Math.sin(t * 1.1 + h.ph) * 0.03 * (1 + wind);
    const ca = Math.cos(h.a), sa = Math.sin(h.a);
    if (profile && (h.nape || (ca > 0.35 && sa > -0.55))) continue;   // keep the face clear in profile
    const bx = ca * (rx + 2), by = sa * (ry - 2) - 10;
    // direction: outward + a little gravity + sideways flick
    let dx = ca + h.side * -sa + sway, dy = sa * 0.8 + 0.35 + h.side * ca;
    if (h.nape) { dx = ca * 0.4 + h.side; dy = 1; }
    const n = Math.hypot(dx, dy); dx /= n; dy /= n;
    const tx = bx + dx * h.len, ty = by + dy * h.len;
    const px = -sa * h.w / 2, py = ca * h.w / 2;
    ctx.beginPath();
    ctx.moveTo(bx - px - dx * 12, by - py - dy * 12);
    ctx.quadraticCurveTo(bx - px * 0.4 + dx * h.len * 0.6, by - py * 0.4 + dy * h.len * 0.6, tx, ty);
    ctx.quadraticCurveTo(bx + px * 0.6 + dx * h.len * 0.4, by + py * 0.6 + dy * h.len * 0.4, bx + px - dx * 12, by + py - dy * 12);
    ctx.closePath(); ctx.fill();
  }
}
function heroBackPath() {
  const p = new Path2D();
  p.moveTo(-34, 48);
  p.bezierCurveTo(-60, 80, -120, 92, -160, 112);
  p.bezierCurveTo(-196, 132, -206, 190, -210, 260);
  p.lineTo(-222, 640); p.lineTo(222, 640); p.lineTo(210, 260);
  p.bezierCurveTo(206, 190, 196, 132, 160, 112);
  p.bezierCurveTo(120, 92, 60, 80, 34, 48);
  p.closePath();
  return p;
}
// hero seen from behind, sitting. (x,y) = head centre.
// o.rim: light dir {x,y} in px and colour; o.breath; o.tilt
function drawHeroBack(ctx, t, x, y, s, o = {}) {
  const breath = Math.sin(t * 1.6) * 0.008;
  const rimCol = o.rimCol || 'rgba(150,180,235,0.9)';
  const rx = o.rimX ?? 6, ry = o.rimY ?? -5;
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  // chair back
  ctx.save();
  ctx.fillStyle = '#06070b';
  rr(ctx, -170, 170, 340, 520, 40); ctx.fill();
  ctx.strokeStyle = 'rgba(120,140,180,0.15)'; ctx.lineWidth = 3; ctx.stroke();
  ctx.restore();
  // torso
  const torso = heroBackPath();
  ctx.save();
  ctx.scale(1, 1 + breath);
  ctx.fillStyle = rimCol; ctx.fill(torso);
  ctx.save(); ctx.clip(torso); ctx.translate(-rx * 1.6, -ry * 1.6); ctx.fillStyle = '#10141d'; ctx.fill(torso); ctx.restore();
  // sweater knit texture & folds
  ctx.save(); ctx.clip(torso);
  ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 3;
  for (let i = -6; i <= 6; i++) { ctx.beginPath(); ctx.moveTo(i * 32, 120); ctx.quadraticCurveTo(i * 34 + 8, 380, i * 36, 640); ctx.stroke(); }
  ctx.strokeStyle = 'rgba(160,180,220,0.05)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(-150, 260); ctx.quadraticCurveTo(-40, 300, 40, 250); ctx.stroke();
  // collar rib
  ctx.fillStyle = '#0b0e15'; ctx.beginPath(); ctx.ellipse(0, 58, 52, 20, 0, 0, 7); ctx.fill();
  ctx.restore();
  ctx.restore();
  // neck
  ctx.fillStyle = '#0c0d12'; rr(ctx, -26, 20, 52, 50, 16); ctx.fill();
  // head
  ctx.save(); ctx.rotate(o.tilt || 0);
  ctx.fillStyle = rimCol;
  ctx.beginPath(); ctx.ellipse(0, -5, 57, 66, 0, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.ellipse(-58, 8, 10, 18, 0, 0, 7); ctx.ellipse(58, 8, 10, 18, 0, 0, 7); ctx.fill();
  ctx.translate(-rx, -ry);
  ctx.fillStyle = '#0d0e13';
  ctx.beginPath(); ctx.ellipse(0, -5, 57, 66, 0, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.ellipse(-58, 8, 10, 18, 0, 0, 7); ctx.ellipse(58, 8, 10, 18, 0, 0, 7); ctx.fill();
  ctx.translate(rx, ry);
  // hair mass + strands (rim then dark)
  ctx.save(); ctx.translate(rx * 0.6, ry * 0.6);
  drawHairStrands(ctx, t, 57, 62, rimCol);
  ctx.restore();
  drawHairStrands(ctx, t, 57, 62, '#06070a');
  ctx.restore();
  ctx.restore();
}

// profile silhouette, facing right. (x,y)=head centre. holding phone in front of face.
function heroSidePath() {
  const p = new Path2D();
  p.moveTo(-20, -80);
  p.bezierCurveTo(30, -86, 66, -60, 74, -28);    // forehead
  p.lineTo(84, -10);                              // brow
  p.lineTo(100, 16);                              // nose tip
  p.lineTo(86, 24);
  p.lineTo(90, 36); p.lineTo(84, 42); p.lineTo(86, 50);   // lips
  p.bezierCurveTo(84, 66, 72, 74, 50, 78);        // chin
  p.bezierCurveTo(40, 82, 34, 96, 36, 120);       // neck front
  p.bezierCurveTo(60, 150, 110, 170, 140, 200);   // chest/shoulder front
  p.lineTo(170, 700); p.lineTo(-200, 700);
  p.bezierCurveTo(-200, 400, -170, 200, -110, 160);  // back
  p.bezierCurveTo(-70, 130, -48, 110, -46, 80);   // nape
  p.bezierCurveTo(-82, 50, -90, -30, -60, -66);   // back of head
  p.closePath();
  return p;
}
function heroArmPath() {
  const p = new Path2D();
  p.moveTo(40, 190);
  p.bezierCurveTo(70, 300, 100, 360, 150, 360);
  p.bezierCurveTo(200, 360, 226, 300, 236, 240);   // forearm up to hand
  p.lineTo(262, 232); p.lineTo(250, 300);
  p.bezierCurveTo(240, 400, 170, 430, 120, 420);
  p.bezierCurveTo(60, 410, 10, 330, -10, 220);
  p.closePath();
  return p;
}
function drawHeroSide(ctx, t, x, y, s, o = {}) {
  const rimCol = o.rimCol || 'rgba(160,190,240,0.95)';
  const lx = o.rimX ?? 7, ly = o.rimY ?? 2;
  const body = heroSidePath(), arm = heroArmPath();
  ctx.save();
  ctx.translate(x, y); ctx.scale(s * (o.flip ? -1 : 1), s);
  ctx.rotate(Math.sin(t * 0.8) * 0.004 + (o.lean ?? 0.1));
  // rim pass
  for (const [path, base] of [[body, '#07080c']]) {
    ctx.fillStyle = rimCol; ctx.fill(path);
    ctx.save(); ctx.clip(path); ctx.translate(-lx, -ly); ctx.fillStyle = base; ctx.fill(path); ctx.restore();
  }
  // hair
  ctx.save(); ctx.translate(-12 + lx * 0.7, -ly * 0.3);
  drawHairStrands(ctx, t, 60, 62, rimCol, 0.5, true, true);
  ctx.restore();
  ctx.save(); ctx.translate(-12, 0);
  drawHairStrands(ctx, t, 60, 62, '#05060a', 0.5, true);
  ctx.restore();
  // fringe over forehead
  ctx.fillStyle = '#05060a';
  ctx.beginPath(); ctx.moveTo(20, -78); ctx.quadraticCurveTo(70, -70, 84, -26); ctx.lineTo(60, -40); ctx.lineTo(66, -16); ctx.lineTo(40, -44); ctx.closePath(); ctx.fill();
  // phone in hand
  if (o.phone) {
    glow(ctx, 190, 190, 300, 'rgba(150,185,255,0.55)', o.phoneLight ?? 0.8);
  }
  ctx.restore();
}

// ---------- full room (wide shot, from behind) ----------
// layers drawn with parallax by the scene; screens are canvases.
function drawRoomBack(ctx, t, o = {}) {
  ctx.drawImage(ART.wall, -240, -160);
  drawWindow(ctx, t, 200, 110, 560, 500, o);
  drawCurtain(ctx, t, 90, 70, 150, 640);
  // cold window light on wall
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const wl = ctx.createLinearGradient(200, 600, 700, 1000);
  wl.addColorStop(0, 'rgba(90,110,150,0.10)'); wl.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = wl;
  ctx.beginPath(); ctx.moveTo(200, 620); ctx.lineTo(760, 620); ctx.lineTo(1000, 1080); ctx.lineTo(260, 1080); ctx.fill();
  ctx.restore();
  // poster
  ctx.save(); ctx.translate(1660, 170);
  ctx.fillStyle = '#0c111b'; ctx.fillRect(0, 0, 220, 300);
  ctx.strokeStyle = 'rgba(150,170,210,0.08)'; ctx.lineWidth = 2; ctx.strokeRect(0, 0, 220, 300);
  ctx.strokeStyle = 'rgba(200,50,58,0.25)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(110, 130, 60, 0, 7); ctx.stroke();
  ctx.fillStyle = 'rgba(150,170,210,0.12)'; ctx.fillRect(30, 230, 160, 8); ctx.fillRect(30, 250, 110, 8);
  ctx.restore();
  // shelf with books
  ctx.save(); ctx.translate(870, 180);
  ctx.fillStyle = '#080b12'; ctx.fillRect(0, 120, 300, 12);
  const r = mulberry32(8); let bx = 10;
  while (bx < 280) { const bw = 14 + r() * 18, bh = 70 + r() * 45; ctx.fillStyle = `rgb(${12 + r() * 10},${16 + r() * 10},${26 + r() * 12})`; ctx.fillRect(bx, 120 - bh, bw, bh); bx += bw + 2; }
  ctx.restore();
}
function drawRoomDesk(ctx, t, o = {}) {
  // desk surface
  ctx.save();
  const top = ctx.createLinearGradient(0, 650, 0, 780);
  top.addColorStop(0, '#0e121b'); top.addColorStop(1, '#151b27');
  ctx.fillStyle = top;
  ctx.beginPath(); ctx.moveTo(470, 660); ctx.lineTo(2100, 660); ctx.lineTo(2100, 790); ctx.lineTo(360, 790); ctx.fill();
  ctx.fillStyle = '#07090e'; ctx.fillRect(360, 790, 1800, 400);
  ctx.fillStyle = 'rgba(150,175,220,0.10)'; ctx.fillRect(360, 789, 1800, 2);
  ctx.restore();
  // lamp (off)
  ctx.save(); ctx.fillStyle = '#07090e'; ctx.strokeStyle = '#07090e'; ctx.lineWidth = 10;
  ctx.beginPath(); ctx.ellipse(560, 676, 60, 12, 0, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.moveTo(560, 676); ctx.lineTo(600, 470); ctx.lineTo(700, 430); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(670, 400); ctx.lineTo(760, 440); ctx.lineTo(720, 490); ctx.closePath(); ctx.fill();
  ctx.restore();
  // monitor + its light
  drawMonitor(ctx, 1040, 290, 560, 330, o.monitor, { bright: o.monBright ?? 1 });
  // keyboard
  ctx.fillStyle = '#090b11';
  ctx.beginPath(); ctx.moveTo(1120, 690); ctx.lineTo(1520, 690); ctx.lineTo(1540, 730); ctx.lineTo(1100, 730); ctx.fill();
  // phone lying on desk
  ctx.save(); ctx.translate(o.phoneX ?? 800, o.phoneY ?? 716);
  ctx.transform(1, 0, -0.5, 0.42, 0, 0); ctx.rotate(-0.2);
  ctx.fillStyle = '#05060a'; rr(ctx, -42, -86, 84, 172, 12); ctx.fill();
  const on = o.phoneOn ?? 0;
  if (on > 0) { ctx.fillStyle = `rgba(170,200,255,${0.75 * on})`; rr(ctx, -36, -80, 72, 160, 9); ctx.fill(); }
  ctx.restore();
  if ((o.phoneOn ?? 0) > 0) glow(ctx, o.phoneX ?? 800, (o.phoneY ?? 716) - 10, 260, 'rgba(140,175,255,0.55)', o.phoneOn);
}
function monitorLight(ctx, a = 1, tint = 'rgba(110,145,215,0.45)') {
  glow(ctx, 1320, 470, 820, tint, a);
}
