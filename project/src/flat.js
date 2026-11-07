// Flat vector style for the vertical (9:16) Shorts version.
// Shot types are prefixed "f_" and configured in config/timeline.ru_v.json.
'use strict';

const FP = {
  bg: '#0e1424', bg2: '#151d33', grid: 'rgba(120,150,210,0.06)',
  wall: '#18213a', wall2: '#1d2844', floor: '#0f1528', moon: '#efe9d6',
  yellow: '#ffd23f', red: '#e8343f', green: '#35c46a', blue: '#3d7bff', white: '#ffffff',
  skin: '#f0bd92', skin2: '#d99d70', hair: '#14151b', hood: '#7a2433', hood2: '#5c1a27', hood3: '#9a3142',
  desk: '#2a3352', desk2: '#222a45', screen: '#9ec2ff',
};

// ---------- helpers ----------
function fcam(ctx, cam, d, fn) {           // camera centred on (540, 960) for the vertical frame
  ctx.save();
  const z = 1 + (cam.z - 1) * d;
  ctx.translate(W / 2, H / 2);
  if (cam.r) ctx.rotate(cam.r * d);
  ctx.scale(z, z);
  ctx.translate(-(W / 2 + (cam.x - W / 2) * d), -(H / 2 + (cam.y - H / 2) * d));
  fn();
  ctx.restore();
}
function fcamOf(sh, T) {
  const c = sh.cam || [[540, 960, 1], [540, 960, 1.06]];
  let cam;
  if (c[0].length === 4) {
    let i = 0; while (i < c.length - 2 && T > c[i + 1][0]) i++;
    const a = c[i], b = c[Math.min(i + 1, c.length - 1)];
    const k = b[0] > a[0] ? ease.inOutSine(clamp((T - a[0]) / (b[0] - a[0]))) : 1;
    cam = { x: lerp(a[1], b[1], k), y: lerp(a[2], b[2], k), z: lerp(a[3], b[3], k) };
  } else {
    const k = ease.inOutSine(clamp((T - sh.start) / (sh.end - sh.start)));
    cam = { x: lerp(c[0][0], c[1][0], k), y: lerp(c[0][1], c[1][1], k), z: lerp(c[0][2], c[1][2], k) };
  }
  if (sh.snap) {
    const k = ease.outExpo(ramp(T, sh.snap.at, sh.snap.at + 0.25));
    cam = { x: lerp(cam.x, sh.snap.to[0], k), y: lerp(cam.y, sh.snap.to[1], k), z: lerp(cam.z, sh.snap.to[2], k) };
    if (T > sh.snap.at) { const s = shake(T, 9 * (1 - ramp(T, sh.snap.at, sh.snap.at + 0.7)), 25, 3); cam.x += s.x; cam.y += s.y; }
  }
  if (sh.shake) { const s = shake(T, sh.shake, 2.2, 11); cam.x += s.x; cam.y += s.y; cam.r = s.r * 2; }
  for (const j of [].concat(sh.jolt || [])) if (T > j && T < j + 0.5) { const s = shake(T, 12 * (1 - (T - j) / 0.5), 30, 5); cam.x += s.x; cam.y += s.y; }
  return cam;
}
function fbg(ctx, col = FP.bg, glowCol) {
  ctx.fillStyle = col; ctx.fillRect(-600, -600, W + 1200, H + 1200);
  ctx.strokeStyle = FP.grid; ctx.lineWidth = 2;
  for (let x = -600; x < W + 600; x += 60) { ctx.beginPath(); ctx.moveTo(x, -600); ctx.lineTo(x, H + 600); ctx.stroke(); }
  for (let y = -600; y < H + 600; y += 60) { ctx.beginPath(); ctx.moveTo(-600, y); ctx.lineTo(W + 600, y); ctx.stroke(); }
  if (glowCol) glow(ctx, W / 2, H * 0.42, 900, glowCol, 1);
}
function circ(ctx, x, y, r, col) { ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); }
function ell(ctx, x, y, rx, ry, col, rot = 0) { ctx.fillStyle = col; ctx.beginPath(); ctx.ellipse(x, y, rx, ry, rot, 0, 7); ctx.fill(); }
function ftext(ctx, s, x, y, size, col = FP.white, o = {}) {
  if (!(size > 0.5)) return;
  ctx.save();
  ctx.font = font(o.w || 900, size); ctx.textAlign = o.align || 'center'; ctx.textBaseline = 'alphabetic';
  if (o.ls) ctx.letterSpacing = o.ls + 'px';
  if (o.alpha !== undefined) ctx.globalAlpha *= o.alpha;
  if (o.maxW) { const w = ctx.measureText(s).width; if (w > o.maxW) { ctx.translate(x, y); ctx.scale(o.maxW / w, o.maxW / w); ctx.translate(-x, -y); } }
  if (o.stroke !== false) { ctx.lineJoin = 'round'; ctx.lineWidth = size * 0.16; ctx.strokeStyle = 'rgba(0,0,0,0.9)'; ctx.strokeText(s, x, y); }
  ctx.fillStyle = col; ctx.fillText(s, x, y);
  ctx.restore();
}
function tagBox(ctx, s, x, y, col, o = {}) {
  ctx.save();
  ctx.font = font(900, o.size || 34); if (o.ls !== 0) ctx.letterSpacing = '1px';
  const w = ctx.measureText(s).width + 36, h = (o.size || 34) + 22;
  ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(o.scale || 1, o.scale || 1);
  ctx.fillStyle = col; rr(ctx, -w / 2, -h / 2, w, h, 8); ctx.fill();
  if (o.border) { ctx.strokeStyle = o.border; ctx.lineWidth = 4; ctx.stroke(); }
  ctx.fillStyle = o.color || (col === FP.yellow ? '#111' : '#fff');
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(s, 0, 3);
  ctx.restore();
}
function redX(ctx, x, y, r, p = 1, lw = 18) {
  ctx.save(); ctx.strokeStyle = FP.red; ctx.lineWidth = lw; ctx.lineCap = 'round';
  const a = clamp(p * 2), b = clamp(p * 2 - 1);
  ctx.beginPath(); ctx.moveTo(x - r, y - r); ctx.lineTo(x - r + 2 * r * a, y - r + 2 * r * a); ctx.stroke();
  if (b > 0) { ctx.beginPath(); ctx.moveTo(x + r, y - r); ctx.lineTo(x + r - 2 * r * b, y - r + 2 * r * b); ctx.stroke(); }
  ctx.restore();
}
const blinkK = (T, seed = 0) => { const p = (T + seed * 1.7) % 3.4; return p < 0.12 ? 0.12 : 1; };

// ---------- character ----------
function hairFront(ctx, s) {
  // messy black hair, front view, head radius ~170
  ctx.fillStyle = FP.hair;
  ctx.beginPath();
  ctx.moveTo(-176, 20);
  const spikes = [[-190, -60], [-215, -120], [-175, -140], [-200, -200], [-140, -200], [-150, -262], [-80, -228], [-60, -290], [0, -236], [40, -296], [80, -232], [150, -270], [140, -200], [210, -210], [180, -140], [222, -110], [186, -60]];
  for (const [x, y] of spikes) ctx.lineTo(x, y);
  ctx.lineTo(176, 20);
  // fringe with jagged edge
  const fr = [[160, -40], [120, -70], [96, -30], [60, -84], [24, -40], [-14, -92], [-48, -46], [-90, -96], [-112, -44], [-150, -82], [-168, -20]];
  for (const [x, y] of fr) ctx.lineTo(x, y);
  ctx.closePath(); ctx.fill();
}
// expr: neutral | shock | worry | happy | rich | skeptic | scared | determined
function heroFace(ctx, T, x, y, s, expr = 'neutral', o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (o.tilt) ctx.rotate(o.tilt);
  // hoodie bust
  if (o.body !== false) {
    ctx.fillStyle = FP.hood2; rr(ctx, -150, 120, 300, 200, 60); ctx.fill();            // hood behind neck
    ctx.fillStyle = FP.hood;
    ctx.beginPath(); ctx.moveTo(-300, 900); ctx.quadraticCurveTo(-300, 250, -120, 220); ctx.lineTo(120, 220); ctx.quadraticCurveTo(300, 250, 300, 900); ctx.closePath(); ctx.fill();
    ctx.fillStyle = FP.hood3; ctx.beginPath(); ctx.moveTo(-120, 220); ctx.quadraticCurveTo(0, 330, 120, 220); ctx.lineTo(90, 210); ctx.quadraticCurveTo(0, 290, -90, 210); ctx.fill();
    ctx.strokeStyle = '#f2f2f2'; ctx.lineWidth = 9; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-40, 270); ctx.lineTo(-48, 400); ctx.moveTo(40, 270); ctx.lineTo(48, 400); ctx.stroke();
    ctx.fillStyle = FP.skin2; rr(ctx, -55, 120, 110, 120, 30); ctx.fill();
  }
  // ears + head
  circ(ctx, -168, 20, 38, FP.skin2); circ(ctx, 168, 20, 38, FP.skin2);
  ell(ctx, 0, 0, 168, 182, FP.skin);
  ctx.fillStyle = 'rgba(160,90,60,0.12)'; ctx.beginPath(); ctx.ellipse(40, 20, 130, 160, 0, -1.2, 1.4); ctx.fill();
  // eyes
  const big = expr === 'shock' || expr === 'scared' ? 1.25 : 1;
  const bl = blinkK(T, o.seed || 0);
  const lx = (o.lookX || 0) * 14, ly = (o.lookY || 0) * 12;
  for (const sx of [-1, 1]) {
    const ex = sx * 64, ey = 16;
    ell(ctx, ex, ey, 46 * big, 54 * big * bl, '#fff');
    if (bl > 0.5) {
      if (expr === 'rich') { ftext(ctx, '$', ex + lx, ey + 26, 76, '#2ea85b', { stroke: false }); }
      else {
        const pr = expr === 'scared' ? 13 : expr === 'shock' ? 17 : 21;
        circ(ctx, ex + lx, ey + 6 + ly, pr, '#16161c');
        circ(ctx, ex + lx + 6, ey - 2 + ly, pr * 0.35, '#fff');
      }
    }
  }
  // brows
  ctx.strokeStyle = FP.hair; ctx.lineWidth = 16; ctx.lineCap = 'round';
  const brows = { neutral: [-48, -48, 0], shock: [-82, -82, 0], scared: [-74, -74, 0.25], worry: [-60, -60, 0.32], happy: [-60, -60, -0.15], rich: [-64, -64, -0.2], skeptic: [-70, -46, 0], determined: [-44, -44, -0.35] }[expr] || [-48, -48, 0];
  for (const sx of [-1, 1]) {
    const by = sx < 0 ? brows[0] : brows[1], tilt = brows[2] * sx;
    ctx.save(); ctx.translate(sx * 64, by); ctx.rotate(tilt); ctx.beginPath(); ctx.moveTo(-34, 0); ctx.lineTo(34, 0); ctx.stroke(); ctx.restore();
  }
  // nose
  ctx.strokeStyle = FP.skin2; ctx.lineWidth = 9; ctx.beginPath(); ctx.moveTo(6, 52); ctx.quadraticCurveTo(22, 82, 0, 88); ctx.stroke();
  // mouth
  const talk = o.talk ? Math.abs(Math.sin(T * 14)) : 0;
  ctx.fillStyle = '#5b1a1f'; ctx.strokeStyle = '#5b1a1f'; ctx.lineWidth = 9;
  if (expr === 'shock' || expr === 'scared') { ell(ctx, 0, 128, 30, 40 + talk * 6, '#5b1a1f'); ell(ctx, 0, 150, 18, 10, '#e2646b'); }
  else if (expr === 'happy' || expr === 'rich') { ctx.beginPath(); ctx.moveTo(-58, 112); ctx.quadraticCurveTo(0, 196, 58, 112); ctx.closePath(); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillRect(-40, 112, 80, 14); }
  else if (expr === 'worry') { ctx.beginPath(); ctx.moveTo(-46, 132); ctx.quadraticCurveTo(-23, 116, 0, 132); ctx.quadraticCurveTo(23, 148, 46, 130); ctx.stroke(); }
  else if (expr === 'skeptic') { ctx.beginPath(); ctx.moveTo(-40, 136); ctx.lineTo(44, 122); ctx.stroke(); }
  else if (expr === 'determined') { ctx.beginPath(); ctx.moveTo(-44, 130); ctx.lineTo(44, 130); ctx.stroke(); }
  else { ctx.beginPath(); ctx.moveTo(-34, 126 - talk * 4); ctx.quadraticCurveTo(0, 140 + talk * 16, 34, 126 - talk * 4); ctx.stroke(); }
  hairFront(ctx, s);
  // sweat drop
  if (o.sweat || expr === 'scared' || expr === 'worry') {
    const sy = -70 + ((T * 40) % 120);
    ctx.fillStyle = '#7fd0ff';
    ctx.beginPath(); ctx.moveTo(176, sy - 40); ctx.quadraticCurveTo(206, sy + 6, 176, sy + 14); ctx.quadraticCurveTo(146, sy + 6, 176, sy - 40); ctx.fill();
    circ(ctx, 172, sy + 2, 6, 'rgba(255,255,255,0.7)');
  }
  // light from a phone below
  if (o.phoneLight) { ctx.save(); ctx.globalCompositeOperation = 'source-atop'; ctx.restore(); glow(ctx, 0, 260, 420, 'rgba(150,190,255,0.35)', o.phoneLight); }
  ctx.restore();
}

// side view head (facing right). (0,0) = head centre, r ~ 90
function headSide(ctx, T, expr = 'neutral', o = {}) {
  circ(ctx, -10, 10, 30, FP.skin2);                                             // ear
  ell(ctx, 0, 0, 92, 98, FP.skin);
  ctx.fillStyle = FP.skin; ctx.beginPath(); ctx.moveTo(84, -6); ctx.quadraticCurveTo(122, 22, 88, 34); ctx.fill();   // nose
  const big = expr === 'shock' || expr === 'scared' ? 1.25 : 1, bl = blinkK(T, 2);
  ell(ctx, 52, -6, 20 * big, 26 * big * bl, '#fff');
  if (bl > 0.5) circ(ctx, 58 + (o.lookX || 0) * 6, -2 + (o.lookY || 0) * 6, 10, '#16161c');
  ctx.strokeStyle = FP.hair; ctx.lineWidth = 9; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(34, expr === 'shock' ? -50 : -38); ctx.lineTo(72, expr === 'worry' ? -46 : expr === 'shock' ? -50 : -38); ctx.stroke();
  ctx.strokeStyle = '#5b1a1f'; ctx.lineWidth = 7;
  if (expr === 'shock' || expr === 'scared') ell(ctx, 70, 58, 12, 16, '#5b1a1f');
  else if (o.talk && Math.sin(T * 14) > 0) ell(ctx, 70, 58, 12, 9, '#5b1a1f');
  else { ctx.beginPath(); ctx.moveTo(56, 58); ctx.lineTo(80, 56); ctx.stroke(); }
  // hair (side)
  ctx.fillStyle = FP.hair; ctx.beginPath();
  const pts = [[70, -60], [80, -100], [40, -96], [36, -138], [0, -112], [-30, -150], [-50, -108], [-100, -120], [-90, -70], [-130, -60], [-100, -20], [-118, 20], [-84, 30], [-80, 60], [-60, 36], [-30, 0], [-10, -40], [30, -50], [44, -30]];
  ctx.moveTo(pts[0][0], pts[0][1]); for (const [x, y] of pts) ctx.lineTo(x, y); ctx.closePath(); ctx.fill();
}
// sitting at a desk, side view facing right. (x,y) = hip on the chair
function heroSit(ctx, T, x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const br = Math.sin(T * 1.8) * 3;
  // chair
  ctx.fillStyle = '#2c3550'; rr(ctx, -150, -330, 40, 360, 14); ctx.fill(); rr(ctx, -150, 0, 230, 34, 12); ctx.fill();
  ctx.fillRect(-40, 34, 20, 170); rr(ctx, -120, 200, 180, 16, 8); ctx.fill();
  // legs
  ctx.fillStyle = '#232b44'; rr(ctx, -60, -40, 260, 70, 34); ctx.fill(); rr(ctx, 150, -30, 64, 240, 30); ctx.fill();
  ctx.fillStyle = '#e9e9ee'; rr(ctx, 150, 190, 110, 40, 18); ctx.fill();
  // torso
  ctx.fillStyle = FP.hood; ctx.beginPath(); ctx.moveTo(-90, 10); ctx.quadraticCurveTo(-110, -230 + br, -40, -300 + br); ctx.lineTo(60, -300 + br); ctx.quadraticCurveTo(110, -200, 70, 10); ctx.closePath(); ctx.fill();
  ctx.fillStyle = FP.hood2; ctx.beginPath(); ctx.ellipse(-50, -300 + br, 60, 40, -0.3, 0, 7); ctx.fill();     // hood
  // head
  ctx.save(); ctx.translate(20, -380 + br); ctx.rotate(o.headTilt || 0); headSide(ctx, T, o.expr, o); ctx.restore();
  // arm
  ctx.fillStyle = FP.hood3;
  if (o.phone) {                 // holding phone in front of face
    ctx.beginPath(); ctx.moveTo(0, -250 + br); ctx.quadraticCurveTo(60, -120, 150, -170); ctx.lineTo(170, -230); ctx.lineTo(150, -250); ctx.quadraticCurveTo(80, -170, 30, -260 + br); ctx.fill();
    ctx.save(); ctx.translate(178, -270); ctx.rotate(-0.35); ctx.fillStyle = '#0a0c12'; rr(ctx, -16, -60, 32, 110, 8); ctx.fill(); ctx.restore();
    circ(ctx, 166, -224, 22, FP.skin);
    glow(ctx, 140, -300, 260, 'rgba(150,190,255,0.6)', o.phoneLight ?? 0.8);
  } else {                       // forearm on the desk
    ctx.beginPath(); ctx.moveTo(-10, -250 + br); ctx.quadraticCurveTo(30, -140, 120, -120); ctx.lineTo(280, -120); ctx.lineTo(280, -84); ctx.lineTo(110, -84); ctx.quadraticCurveTo(-10, -100, -40, -230 + br); ctx.fill();
    circ(ctx, 286, -102, 22, FP.skin);
  }
  ctx.restore();
}
// back view bust (standing / looking at a window). (x,y) = head centre
function heroBackFlat(ctx, T, x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = FP.hood; ctx.beginPath(); ctx.moveTo(-320, 900); ctx.quadraticCurveTo(-320, 230, -120, 200); ctx.lineTo(120, 200); ctx.quadraticCurveTo(320, 230, 320, 900); ctx.closePath(); ctx.fill();
  ctx.fillStyle = FP.hood2; ctx.beginPath(); ctx.ellipse(0, 210, 170, 90, 0, 0, Math.PI); ctx.fill();
  ctx.fillStyle = FP.hood3; ctx.fillRect(-4, 300, 8, 600);
  circ(ctx, -168, 10, 36, FP.skin2); circ(ctx, 168, 10, 36, FP.skin2);
  ell(ctx, 0, 0, 165, 178, FP.hair);
  ctx.save(); ctx.scale(1, -1); ctx.translate(0, 60); hairFront(ctx, 1); ctx.restore();
  ctx.fillStyle = FP.hair; ctx.beginPath(); ctx.moveTo(-160, -10);
  for (const [px, py] of [[-200, -90], [-150, -120], [-190, -190], [-110, -200], [-120, -260], [-40, -220], [-10, -290], [40, -220], [110, -270], [110, -200], [190, -200], [160, -120], [210, -90], [160, -10]]) ctx.lineTo(px, py);
  ctx.closePath(); ctx.fill();
  if (o.rim) { ctx.strokeStyle = o.rim; ctx.lineWidth = 6; ctx.beginPath(); ctx.ellipse(0, 0, 167, 180, 0, -2.6, -0.5); ctx.stroke(); }
  if (o.phoneLight) glow(ctx, 0, 180, 380, 'rgba(150,190,255,0.5)', o.phoneLight);
  ctx.restore();
}
// standing side view with phone at the ear. (x,y) = head centre
function heroCall(ctx, T, x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = FP.hood; ctx.beginPath(); ctx.moveTo(-240, 900); ctx.quadraticCurveTo(-230, 200, -60, 150); ctx.lineTo(70, 150); ctx.quadraticCurveTo(210, 220, 200, 900); ctx.closePath(); ctx.fill();
  ctx.fillStyle = FP.hood2; ctx.beginPath(); ctx.ellipse(-80, 150, 110, 60, -0.3, 0, 7); ctx.fill();
  ctx.save(); ctx.scale(1.6, 1.6); headSide(ctx, T, o.expr, o); ctx.restore();
  // arm up to the ear with the phone
  ctx.fillStyle = FP.hood3; ctx.beginPath(); ctx.moveTo(40, 260); ctx.quadraticCurveTo(170, 220, 120, 60); ctx.lineTo(70, 70); ctx.quadraticCurveTo(110, 200, 0, 220); ctx.fill();
  ctx.save(); ctx.translate(30, 20); ctx.rotate(-0.4); ctx.fillStyle = '#0a0c12'; rr(ctx, -26, -110, 52, 170, 12); ctx.fill();
  if (o.glow) { ctx.fillStyle = `rgba(160,200,255,${o.glow})`; rr(ctx, -18, -100, 36, 150, 8); ctx.fill(); }
  ctx.restore();
  circ(ctx, 92, 70, 34, FP.skin);
  if (o.waves) for (let i = 0; i < 3; i++) { const p = (T * 1.2 + i / 3) % 1; ctx.strokeStyle = `rgba(255,210,63,${(1 - p) * 0.9})`; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(30, -10, 90 + p * 140, -2.4, -1.2); ctx.stroke(); }
  ctx.restore();
}

// ---------- environment ----------
function flatWindow(ctx, T, x, y, w, h, o = {}) {
  ctx.save(); rr(ctx, x, y, w, h, 10); ctx.clip();
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  if (o.morning) { g.addColorStop(0, '#6f8fc4'); g.addColorStop(1, '#f2b88a'); } else { g.addColorStop(0, '#0b1222'); g.addColorStop(1, '#1d2a4a'); }
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  if (o.morning) circ(ctx, x + w * 0.7, y + h * 0.62, w * 0.12, '#ffe2a6');
  else {
    circ(ctx, x + w * 0.72, y + h * 0.18, w * 0.09, FP.moon);
    const r = mulberry32(5); for (let i = 0; i < 30; i++) { ctx.fillStyle = `rgba(255,255,255,${0.3 + 0.5 * Math.abs(Math.sin(T * 2 + i))})`; ctx.fillRect(x + r() * w, y + r() * h * 0.5, 4, 4); }
  }
  // city blocks with lit windows
  const r = mulberry32(12); let bx = x - 20;
  while (bx < x + w) {
    const bw = 70 + r() * 90, bh = h * (0.25 + r() * 0.35);
    ctx.fillStyle = o.morning ? '#4a5a80' : '#121a30'; ctx.fillRect(bx, y + h - bh, bw, bh);
    for (let wy = y + h - bh + 16; wy < y + h - 10; wy += 34) for (let wx = bx + 12; wx < bx + bw - 18; wx += 28) {
      if (r() < (o.morning ? 0.1 : 0.35)) { ctx.fillStyle = FP.yellow; ctx.fillRect(wx, wy, 14, 18); }
    }
    bx += bw + 6;
  }
  // fog bands
  if (!o.morning) for (let k = 0; k < 3; k++) { ctx.fillStyle = 'rgba(160,180,220,0.08)'; const fy = y + h * (0.55 + k * 0.12) + Math.sin(T * 0.5 + k) * 8; rr(ctx, x - 100 + ((T * 20 * (k + 1)) % 200), fy, w + 200, 40, 20); ctx.fill(); }
  // eyes in the dark
  if (o.eyes) {
    const a = o.eyes, r2 = mulberry32(77);
    for (let i = 0; i < 3; i++) {
      const ex = x + w * (0.2 + r2() * 0.6), ey = y + h * (0.55 + r2() * 0.3);
      if ((T * 0.7 + i * 0.37) % 2 < 0.12) continue;      // blink
      ell(ctx, ex - 16, ey, 9, 6, `rgba(232,52,63,${a})`); ell(ctx, ex + 16, ey, 9, 6, `rgba(232,52,63,${a})`);
      glow(ctx, ex, ey, 60, 'rgba(232,52,63,0.5)', a);
    }
  }
  ctx.restore();
  ctx.strokeStyle = '#0a0f1c'; ctx.lineWidth = 22; rr(ctx, x, y, w, h, 10); ctx.stroke();
  ctx.lineWidth = 14; ctx.beginPath(); ctx.moveTo(x + w / 2, y); ctx.lineTo(x + w / 2, y + h); ctx.moveTo(x, y + h * 0.45); ctx.lineTo(x + w, y + h * 0.45); ctx.stroke();
  ctx.fillStyle = '#0a0f1c'; ctx.fillRect(x - 30, y + h, w + 60, 26);
}
function flatMonitor(ctx, x, y, w, h, screen, col = FP.screen) {
  ctx.fillStyle = '#0a0f1c'; rr(ctx, x - 18, y - 18, w + 36, h + 36, 14); ctx.fill();
  ctx.fillRect(x + w / 2 - 18, y + h + 18, 36, 60); rr(ctx, x + w / 2 - 90, y + h + 70, 180, 18, 8); ctx.fill();
  if (screen) { ctx.save(); rr(ctx, x, y, w, h, 4); ctx.clip(); ctx.drawImage(screen, x, y, w, h); ctx.restore(); }
  else { ctx.fillStyle = col; ctx.fillRect(x, y, w, h); }
}
// vertical bedroom. o: morning, red, phoneOn, vib, pose, expr
function flatRoom(ctx, T, cam, o = {}) {
  fcam(ctx, cam, 0.85, () => {
    ctx.fillStyle = o.morning ? '#25335a' : FP.wall; ctx.fillRect(-400, -400, W + 800, 1700);
    ctx.fillStyle = FP.wall2; for (let x = -400; x < W + 400; x += 120) ctx.fillRect(x, -400, 4, 1700);
    flatWindow(ctx, T, 90, 330, 470, 560, { morning: o.morning, eyes: o.eyes });
    // poster + shelf
    ctx.fillStyle = '#26305a'; rr(ctx, 720, 330, 200, 270, 8); ctx.fill(); circ(ctx, 820, 440, 60, FP.red); ftext(ctx, '?', 820, 470, 90, FP.white, { stroke: false });
  });
  fcam(ctx, cam, 1, () => {
    ctx.fillStyle = FP.floor; ctx.fillRect(-400, 1290, W + 800, 900);
    // desk
    ctx.fillStyle = FP.desk; rr(ctx, 560, 1080, 700, 40, 8); ctx.fill();
    ctx.fillStyle = FP.desk2; ctx.fillRect(600, 1120, 30, 360); ctx.fillRect(1010, 1120, 30, 360);
    // monitor glow + monitor
    const mcol = o.red ? 'rgba(232,52,63,0.45)' : 'rgba(110,160,255,0.4)';
    glow(ctx, 840, 920, 520, mcol, 0.9);
    flatMonitor(ctx, 690, 800, 330, 200, o.monitor);
    // phone on desk
    const on = o.phoneOn ?? 0, j = o.vib ? shake(T, 4, 70, 1).x : 0;
    if (!o.phoneInHand) {
      ctx.fillStyle = '#0a0c12'; rr(ctx, 600 + j, 1064, 90, 18, 6); ctx.fill();
      if (on > 0) { ctx.fillStyle = `rgba(170,210,255,${on})`; rr(ctx, 606 + j, 1062, 78, 6, 3); ctx.fill(); glow(ctx, 645 + j, 1050, 220, 'rgba(150,190,255,0.7)', on); }
      if (o.vib) { ctx.strokeStyle = FP.yellow; ctx.lineWidth = 6; for (const sx of [-1, 1]) { ctx.beginPath(); ctx.moveTo(645 + sx * 70, 1040); ctx.lineTo(645 + sx * 90, 1020); ctx.moveTo(645 + sx * 66, 1060); ctx.lineTo(645 + sx * 96, 1056); ctx.stroke(); } }
    }
    heroSit(ctx, T, 330, 1270, 1.05, { expr: o.expr || 'neutral', phone: o.phoneInHand, phoneLight: on, headTilt: o.headTilt, lookX: o.lookX, lookY: o.lookY });
  });
}

// ---------- shot types ----------
const FLAT = {
  f_room(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const vib = pulseAt(T, sh.vibAt, 1.0);
    let on = sh.phoneOnAt !== undefined ? so(T, sh.phoneOnAt, sh.phoneOnAt + 0.3) : V(sh, 'phoneOn', 0.4);
    if (sh.phoneOffAt !== undefined) on *= 1 - sm(T, sh.phoneOffAt, sh.phoneOffAt + 0.4);
    const inHand = sh.handAt !== undefined && T > sh.handAt;
    const expr = sh.exprAt && T > sh.exprAt[0] ? sh.exprAt[1] : sh.expr;
    flatRoom(ctx, T, cam, { morning: sh.morning, red: sh.red, phoneOn: on, vib, phoneInHand: inHand, expr, eyes: sh.eyes, monitor: monScreen(sh.monitor, T), headTilt: sh.headTilt, lookX: sh.lookX });
    if (sh.dim) { ctx.fillStyle = `rgba(0,0,0,${sh.dim})`; ctx.fillRect(0, 0, W, H); }
  },

  f_phone(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => fbg(ctx, sh.bg || FP.bg, sh.red && T > sh.red ? 'rgba(232,52,63,0.35)' : 'rgba(80,130,255,0.25)'));
    const vib = pulseAt(T, sh.vibAt, 1.0) ? shake(T, 4, 60, 4) : { x: 0, y: 0, r: 0 };
    fcam(ctx, cam, 1, () => {
      const scr = phoneScreen(sh.screen, T);
      drawPhone(ctx, 540 + vib.x, 780 + vib.y, 0.9, (sh.rot ?? -0.03) + vib.r * 10, scr, { on: onLevel(sh, T) });
      // thumbs
      circ(ctx, 540 - 290, 1010, 46, FP.skin); circ(ctx, 540 + 290, 980, 46, FP.skin);
      ctx.fillStyle = FP.hood3; rr(ctx, 160, 1240, 760, 400, 120); ctx.fill();
      if (sh.stampAt !== undefined && T > sh.stampAt) {
        const p = ease.outBack(ramp(T, sh.stampAt, sh.stampAt + 0.3));
        tagBox(ctx, S('stolen'), 540, 560, FP.red, { size: 76, rot: -0.12, scale: 2 - p });
      }
    });
    if (sh.redFlash !== undefined && T > sh.redFlash) { ctx.fillStyle = rgba(FP.red, 0.3 * (1 - ramp(T, sh.redFlash, sh.redFlash + 0.5))); ctx.fillRect(0, 0, W, H); }
    // reaction face in the corner
    if (sh.face) {
      const f = [].concat(sh.faceAt || []); let expr = sh.face;
      for (const [t, e] of (sh.faceSeq || [])) if (T > t) expr = e;
      const pop = f.length ? ease.outBack(ramp(T, f[0], f[0] + 0.35)) : 1;
      heroFace(ctx, T, 210, 1880 - 260 * pop, 0.62, expr, { lookX: 0.6, lookY: -0.6, sweat: sh.sweat });
    }
    if (sh.fadeOut) { ctx.fillStyle = `rgba(0,0,0,${sm(T, sh.fadeOut[0], sh.fadeOut[1]) * 0.85})`; ctx.fillRect(0, 0, W, H); }
    if (sh.shotAt !== undefined && T > sh.shotAt) { ctx.fillStyle = `rgba(255,255,255,${0.8 * (1 - ramp(T, sh.shotAt, sh.shotAt + 0.4))})`; ctx.fillRect(0, 0, W, H); }
  },

  f_face(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const red = sh.red !== undefined ? (sh.red === true ? 1 : so(T, sh.red, sh.red + 0.5)) : 0;
    fcam(ctx, cam, 0.7, () => fbg(ctx, sh.bg || FP.bg, red ? `rgba(232,52,63,${0.45 * red})` : sh.glow || 'rgba(80,130,255,0.25)'));
    let expr = sh.expr; for (const [t, e] of (sh.exprSeq || [])) if (T > t) expr = e;
    fcam(ctx, cam, 1, () => {
      if (sh.coins) {                                     // falling coins
        const r = mulberry32(3);
        for (let i = 0; i < 26; i++) { const x = r() * W, sp = 300 + r() * 300, y = ((T - sh.start) * sp + r() * 2000) % 2300 - 200; ell(ctx, x, y, 34, 34 * Math.abs(Math.cos(T * 3 + i)), FP.yellow); ftext(ctx, '₿', x, y + 14, 36, '#c9971a', { stroke: false }); }
      }
      heroFace(ctx, T, 540, 900, 1.6, expr, { lookX: sh.lookX || 0, lookY: sh.lookY || 0, sweat: sh.sweat, phoneLight: sh.phoneLight, talk: sh.talk, seed: 1 });
      if (sh.thought && typeof thoughtBubble === 'function') thoughtBubble(ctx, T, 800, 420, 190, sh.thought, ease.outBack(ramp(T, sh.thoughtAt ?? sh.start, (sh.thoughtAt ?? sh.start) + 0.35)));
      if (sh.question) { const p = ease.outBack(ramp(T, sh.question, sh.question + 0.3)); ftext(ctx, '?', 900, 560, 220 * p, FP.red); ftext(ctx, '?', 190, 470, 150 * p, FP.yellow); }
    });
    if (sh.darkAt !== undefined) { ctx.fillStyle = `rgba(0,0,0,${sm(T, sh.darkAt, sh.darkAt + 0.3) * 0.9})`; ctx.fillRect(0, 0, W, H); }
    if (sh.caption) { const p = ease.outBack(ramp(T, sh.caption.at, sh.caption.at + 0.35)); tagBox(ctx, sh.caption.text, 540, 820, FP.red, { size: 64, rot: -0.06, scale: p }); }
  },

  f_window(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.7, () => {
      ctx.fillStyle = sh.morning ? '#25335a' : FP.wall; ctx.fillRect(-400, -400, W + 800, H + 800);
      flatWindow(ctx, T, 110, 260, 860, 1000, { morning: sh.morning, eyes: sh.eyes ? so(T, sh.eyes, sh.eyes + 1) : 0 });
    });
    fcam(ctx, cam, 1, () => heroBackFlat(ctx, T, 540, 1200, 0.95, { rim: sh.morning ? null : 'rgba(170,200,255,0.5)', phoneLight: sh.phoneAt !== undefined ? so(T, sh.phoneAt, sh.phoneAt + 0.4) : V(sh, 'phone', 0.6) }));
    if (sh.red) { ctx.fillStyle = rgba(FP.red, 0.12 * so(T, sh.red, sh.red + 1)); ctx.fillRect(0, 0, W, H); }
  },

  f_dream(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.7, () => fbg(ctx, '#121a33', 'rgba(255,210,63,0.18)'));
    const items = [['car', 'dream_car', sh.carAt, 470], ['house', sh.homeKey || 'dream_home', sh.homeAt, 860], ['keys', sh.freeKey || 'dream_free', sh.freeAt, 1230]];
    fcam(ctx, cam, 1, () => {
      for (const [kind, key, at, y] of items) {
        if (at === undefined || T < at) continue;
        const p = ease.outBack(ramp(T, at, at + 0.4));
        ctx.save(); ctx.translate(kind === 'house' ? 330 : kind === 'car' ? 700 : 380, y); ctx.scale(p, p);
        if (kind === 'car') {
          ctx.fillStyle = FP.red; rr(ctx, -200, -40, 400, 90, 30); ctx.fill(); rr(ctx, -110, -110, 220, 90, 34); ctx.fill();
          ctx.fillStyle = '#9fd0ff'; rr(ctx, -90, -94, 84, 56, 12); ctx.fill(); rr(ctx, 6, -94, 84, 56, 12); ctx.fill();
          circ(ctx, -120, 56, 40, '#111'); circ(ctx, 120, 56, 40, '#111'); circ(ctx, -120, 56, 16, '#999'); circ(ctx, 120, 56, 16, '#999');
          circ(ctx, 196, 0, 12, FP.yellow);
        } else if (kind === 'house') {
          ctx.fillStyle = '#3a4a7a'; ctx.fillRect(-120, -200, 240, 330);
          for (let rr_ = 0; rr_ < 5; rr_++) for (let c = 0; c < 3; c++) { ctx.fillStyle = (rr_ + c) % 3 ? FP.yellow : '#1d2440'; ctx.fillRect(-92 + c * 66, -176 + rr_ * 58, 46, 38); }
        } else {
          ctx.strokeStyle = FP.yellow; ctx.lineWidth = 24; ctx.beginPath(); ctx.arc(-80, 0, 56, 0, 7); ctx.stroke();
          ctx.fillStyle = FP.yellow; ctx.fillRect(-24, -12, 230, 24); ctx.fillRect(150, 0, 22, 50); ctx.fillRect(190, 0, 22, 36);
        }
        ctx.restore();
        tagBox(ctx, S(key), kind === 'house' ? 760 : kind === 'car' ? 330 : 780, y, FP.yellow, { size: 44, rot: kind === 'house' ? 0.05 : -0.05, scale: p });
      }
    });
  },

  f_graph(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => fbg(ctx));
    const rev = sh.reveal ? so(T, sh.reveal[0], sh.reveal[1]) : 1;
    const foc = sh.focus !== undefined ? so(T, sh.focus, sh.focus + 0.4) : 0;
    fcam(ctx, cam, 1, () => {
      const N = 9, pts = [];
      for (let i = 0; i < N; i++) pts.push([170 + i * 95, 1420 - i * 125]);
      // side branches (grey)
      ctx.lineWidth = 6;
      pts.forEach(([x, y], i) => {
        const k = clamp(rev * N * 1.2 - i); if (k <= 0) return;
        ctx.strokeStyle = 'rgba(150,170,210,0.35)'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 140 * k, y + 90 * k); ctx.stroke();
        ctx.fillStyle = '#4a5677'; rr(ctx, x + 140 * k - 22, y + 90 * k - 22, 44, 44, 6); ctx.fill();
      });
      // main chain
      for (let i = 1; i < N; i++) {
        const k = clamp(rev * N * 1.2 - i); if (k <= 0) continue;
        const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
        ctx.strokeStyle = foc ? FP.red : 'rgba(200,215,240,0.6)'; ctx.lineWidth = foc ? 10 : 6;
        if (foc) ctx.setLineDash([22, 16]); ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(lerp(x0, x1, k), lerp(y0, y1, k)); ctx.stroke(); ctx.setLineDash([]);
      }
      pts.forEach(([x, y], i) => {
        const k = clamp(rev * N * 1.2 - i + 0.5); if (k <= 0) return;
        const end = i === N - 1, start = i === 0;
        ctx.save(); ctx.translate(x, y); ctx.scale(ease.outBack(k), ease.outBack(k));
        ctx.fillStyle = start ? FP.red : end ? (foc ? FP.red : FP.yellow) : FP.yellow; rr(ctx, -34, -34, 68, 68, 10); ctx.fill();
        ctx.restore();
        if (start) tagBox(ctx, S('g_exchange'), x + 20, y + 90, FP.red, { size: 30 });
        if (end) {
          tagBox(ctx, S('g_you'), x - 60, y - 90, foc ? FP.red : FP.yellow, { size: 34 });
          if (foc) { ctx.strokeStyle = FP.red; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(x, y, 70 + Math.sin(T * 6) * 8, 0, 7); ctx.stroke(); }
        }
        if (!start && !end && i % 3 === 1) ftext(ctx, '?', x + 58, y - 20, 60, FP.white, { alpha: k });
      });
      if (sh.crossAt !== undefined) [2, 5].forEach((i, n) => redX(ctx, pts[i][0], pts[i][1], 50, ramp(T, sh.crossAt + n * 0.25, sh.crossAt + n * 0.25 + 0.3), 16));
    });
  },

  f_monitor(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const red = sh.redAt !== undefined ? so(T, sh.redAt, sh.redAt + 0.4) : 0;
    fcam(ctx, cam, 0.8, () => fbg(ctx, FP.wall, red ? 'rgba(232,52,63,0.4)' : 'rgba(110,160,255,0.35)'));
    fcam(ctx, cam, 1, () => {
      flatMonitor(ctx, 40, 520, 1000, 562, monScreen(sh.monitor, T));
      ctx.fillStyle = FP.desk; ctx.fillRect(-400, 1180, W + 800, 40);
    });
    fcam(ctx, cam, 1.15, () => heroBackFlat(ctx, T, 540, 1560, 0.95, { rim: red ? 'rgba(255,120,130,0.7)' : 'rgba(170,200,255,0.6)' }));
  },

  f_call(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.7, () => { ctx.fillStyle = FP.wall; ctx.fillRect(-400, -400, W + 800, H + 800); flatWindow(ctx, T, 560, 300, 420, 520, { eyes: sh.eyes ? 0.8 : 0 }); });
    const speaking = (sh.voice || []).some(([a, b]) => T > a && T < b);
    fcam(ctx, cam, 1, () => heroCall(ctx, T, 400, 900, 1.0, { expr: speaking ? 'scared' : T > (sh.answerAt ?? 1e9) ? 'worry' : 'neutral', waves: T < (sh.answerAt ?? 1e9), glow: 0.6 }));
    // speech bubbles
    for (const b of sh.bubbles || []) {
      if (T < b.at || T > b.to) continue;
      const p = ease.outBack(ramp(T, b.at, b.at + 0.3));
      ctx.save(); ctx.translate(560, 420); ctx.scale(p, p);
      ctx.font = font(800, 46); const lines = wrap(ctx, b.text, 680);
      const bw = Math.max(...lines.map(l => ctx.measureText(l).width)) + 70, bh = lines.length * 58 + 50;
      ctx.fillStyle = b.red ? '#2a0f14' : '#0d1222'; ctx.strokeStyle = b.red ? FP.red : FP.white; ctx.lineWidth = 6;
      rr(ctx, -bw / 2, -bh / 2, bw, bh, 26); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-bw / 2 + 60, bh / 2); ctx.lineTo(-bw / 2 + 30, bh / 2 + 60); ctx.lineTo(-bw / 2 + 120, bh / 2); ctx.fill();
      lines.forEach((l, i) => ftext(ctx, l, 0, -bh / 2 + 70 + i * 58, 46, b.red ? '#ffb3b8' : FP.white, { stroke: false }));
      ctx.restore();
    }
  },

  f_big(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => fbg(ctx, FP.bg, sh.col === 'red' ? 'rgba(232,52,63,0.3)' : 'rgba(255,210,63,0.18)'));
    const at = sh.at ?? sh.start, p = ease.outBack(ramp(T, at, at + 0.4)), q = so(T, at + 0.25, at + 0.6);
    const col = sh.col === 'red' ? FP.red : sh.col === 'yellow' ? FP.yellow : FP.red;
    fcam(ctx, cam, 1, () => {
      ctx.save(); ctx.translate(540, 470); ctx.scale(p, p);
      circ(ctx, 0, 0, 150, col);
      ftext(ctx, sh.sym, 0, sh.sym.length > 1 ? 52 : 62, sh.sym.length > 1 ? 150 : 180, col === FP.yellow ? '#111' : FP.white, { stroke: false });
      ctx.restore();
      ftext(ctx, sh.label, 540, 690, 50, FP.yellow, { alpha: q, ls: 4 });
      ctx.save(); ctx.globalAlpha = q;
      ctx.font = font(900, 56); const bw = Math.min(1000, ctx.measureText(sh.box).width + 80);
      ctx.fillStyle = '#0b0f1c'; rr(ctx, 540 - bw / 2, 730, bw, 100, 14); ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.stroke();
      ctx.restore();
      ftext(ctx, sh.box, 540, 800, 56, FP.white, { alpha: q, maxW: 940, stroke: false });
      // illustration
      if (sh.ill === 'wallet' || sh.ill === 'call') {
        const scr = sh.ill === 'wallet' ? phoneScreen({ kind: 'wallet', pulse: 1 }, T) : phoneScreen({ kind: 'call', calling: sh.callingAt }, T);
        drawPhone(ctx, 540, 1170, 0.4, sh.ill === 'wallet' ? -0.08 : 0.08, scr, { on: 1 });
      } else if (sh.ill === 'file' || sh.ill === 'search') {
        ctx.save(); ctx.translate(540, 1150);
        if (sh.ill === 'file') {
          ctx.fillStyle = '#e9edf3'; rr(ctx, -150, -190, 300, 380, 18); ctx.fill(); ctx.fillStyle = '#2f8f5b'; rr(ctx, -150, -190, 300, 60, 18); ctx.fill();
          for (let i = 0; i < 6; i++) { ctx.fillStyle = i === 4 ? FP.red : '#9aa4b2'; ctx.fillRect(-120, -100 + i * 46, 240 - (i * 37) % 90, 16); }
          ctx.fillStyle = FP.blue; circ(ctx, 160, 140, 80, FP.blue); ftext(ctx, '👮', 160, 168, 80, '#fff', { stroke: false });
        } else {
          ctx.rotate(-0.3); ctx.strokeStyle = '#e9edf3'; ctx.lineWidth = 34; ctx.beginPath(); ctx.arc(0, -40, 130, 0, 7); ctx.stroke();
          ctx.fillStyle = 'rgba(160,200,255,0.25)'; ctx.beginPath(); ctx.arc(0, -40, 115, 0, 7); ctx.fill();
          ctx.fillStyle = '#e9edf3'; rr(ctx, -28, 90, 56, 200, 24); ctx.fill(); ftext(ctx, '?', 0, 10, 140, FP.yellow);
        }
        ctx.restore();
      } else if (sh.ill === 'countdown') {
        const left = 24 * 3600 - Math.max(0, Math.floor((T - at - 0.4) * 3));
        const str = `${String(Math.floor(left / 3600)).padStart(2, '0')}:${String(Math.floor(left / 60) % 60).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`;
        ctx.fillStyle = FP.red; rr(ctx, 230, 990, 620, 150, 30); ctx.fill();
        ftext(ctx, str, 540, 1100, 100, FP.white, { stroke: false, w: 800 });
      }
    });
    if (sh.millionAt !== undefined && T > sh.millionAt - 0.2) {
      const m = so(T, sh.millionAt - 0.2, sh.millionAt + 0.9);
      tagBox(ctx, '$' + String(Math.floor(lerp(0, 1000000, m))).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + (m >= 1 ? '+' : ''), 540, 1080, FP.green, { size: 64, rot: -0.05 });
    }
    if (sh.strikeAt !== undefined && T > sh.strikeAt - 0.3) {
      const a = so(T, sh.strikeAt - 0.3, sh.strikeAt), st = so(T, sh.strikeAt + 0.2, sh.strikeAt + 0.8);
      tagBox(ctx, '10 BTC', 540, 1080, FP.yellow, { size: 64, rot: 0.05, scale: a });
      redX(ctx, 540, 1080, 90, st, 20);
    }
  },

  f_rewind(ctx, T, sh) {
    fbg(ctx, '#121a33', 'rgba(255,210,63,0.15)');
    const p = ease.outBack(ramp(T, sh.start, sh.start + 0.4));
    ctx.save(); ctx.translate(540, 700); ctx.scale(p, p);
    circ(ctx, 0, 0, 230, FP.white); circ(ctx, 0, 0, 205, '#1d2440');
    for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; ctx.fillStyle = FP.white; ctx.fillRect(Math.cos(a) * 170 - 8, Math.sin(a) * 170 - 8, 16, 16); }
    const a = (sh.forward ? 1 : -1) * (T - sh.start) * 9;
    ctx.strokeStyle = FP.yellow; ctx.lineWidth = 16; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * 150, Math.sin(a) * 150); ctx.stroke();
    ctx.strokeStyle = FP.red; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a / 12) * 100, Math.sin(a / 12) * 100); ctx.stroke();
    circ(ctx, 0, 0, 18, FP.yellow);
    ctx.restore();
    ftext(ctx, sh.forward ? '▶▶' : '◀◀', 540, 1080, 90, FP.yellow, { alpha: Math.floor(T * 3) % 2 ? 1 : 0.4 });
  },

  f_split(ctx, T, sh) {
    const open = sm(T, sh.start, sh.start + 0.5);
    [0, 1].forEach(i => {
      ctx.save(); ctx.beginPath(); ctx.rect(0, i ? H / 2 + 4 : 0, W, H / 2 - 4); ctx.clip();
      ctx.translate(0, (i ? 1 : -1) * (1 - open) * 300);
      fbg(ctx, i ? '#1d1220' : FP.bg, i ? 'rgba(232,52,63,0.3)' : 'rgba(255,210,63,0.2)');
      const scr = i ? scrCall(T, { calling: false }, SCR.phone2) : phoneScreen({ kind: 'wallet' }, T);
      drawPhone(ctx, 540, i ? H * 0.75 : H * 0.25 + 120, 0.55, i ? 0.06 : -0.06, scr, { on: 1 });
      ctx.restore();
    });
    ctx.fillStyle = FP.white; ctx.fillRect(0, H / 2 - 4, W * open, 8);
    circ(ctx, 540, H / 2, 70 * open, FP.white); ftext(ctx, S('vs'), 540, H / 2 + 14, 40, '#111', { stroke: false, alpha: open });
    tagBox(ctx, 'A', 960, 330, FP.yellow, { size: 64 }); tagBox(ctx, 'B', 960, H / 2 + 120, FP.red, { size: 64 });
  },

  f_final(ctx, T, sh) {
    if (!sh.noBg) {
    fbg(ctx, FP.bg, 'rgba(255,210,63,0.12)');
    const q = ease.outBack(ramp(T, sh.q, sh.q + 0.4));
    ftext(ctx, sh.qText || S('final_q'), 540, 470, 86 * q, FP.white, { maxW: 980 });
    ftext(ctx, sh.q2Text || S('money_or_safety'), 540, 560, 46, FP.yellow, { alpha: so(T, sh.q + 0.3, sh.q + 0.7), maxW: 980 });
    const row = (t, letter, label, y, col) => {
      const p = ease.outBack(ramp(T, t, t + 0.35)); if (p <= 0) return;
      ctx.save(); ctx.translate(540, y); ctx.scale(p, p);
      ctx.fillStyle = '#0b0f1c'; rr(ctx, -440, -70, 880, 140, 24); ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 6; ctx.stroke();
      circ(ctx, -360, 0, 50, col); ftext(ctx, letter, -360, 22, 64, col === FP.yellow ? '#111' : '#fff', { stroke: false });
      ftext(ctx, label, 60, 18, 50, FP.white, { stroke: false, maxW: 700 });
      ctx.restore();
    };
    row(sh.a, 'A', sh.aText || S('final_a_short'), 740, FP.yellow);
    row(sh.b, 'B', sh.bText || S('final_b_short'), 910, FP.red);
    ftext(ctx, sh.cText || S('final_c_short'), 540, 1080, 42, FP.white, { alpha: so(T, sh.c, sh.c + 0.4), maxW: 980 });
    }
    // subscribe + part 2
    if (sh.sub !== undefined && T > sh.sub) {
      const p = ease.outBack(ramp(T, sh.sub, sh.sub + 0.35)), done = T > sh.sub + 1.4;
      ctx.save(); ctx.translate(540, 1240); ctx.scale(p * (T > sh.sub + 1.25 && T < sh.sub + 1.45 ? 0.92 : 1), p);
      ctx.fillStyle = done ? '#3a3f4f' : FP.red; rr(ctx, -260, -60, 520, 120, 60); ctx.fill();
      ftext(ctx, done ? S('subscribed') : S('subscribe'), 0, 18, 48, FP.white, { stroke: false });
      ctx.restore();
      if (T > sh.sub + 0.8 && T < sh.sub + 1.5) { const k = ramp(T, sh.sub + 0.8, sh.sub + 1.3); circ(ctx, lerp(900, 640, k), lerp(1500, 1260, k), 30, 'rgba(255,255,255,0.85)'); }
      if (done) { const b = ease.outBack(ramp(T, sh.sub + 1.4, sh.sub + 1.8)); ctx.save(); ctx.translate(860, 1240); ctx.scale(b, b); ctx.rotate(Math.sin(T * 12) * 0.2 * (1 - ramp(T, sh.sub + 1.8, sh.sub + 2.6))); circ(ctx, 0, 0, 60, FP.yellow); ftext(ctx, '🔔', 0, 20, 56, '#111', { stroke: false }); ctx.restore(); }
    }
    if (sh.part2 !== undefined && T > sh.part2) {
      const p = so(T, sh.part2, sh.part2 + 0.5);
      tagBox(ctx, sh.p2badge || S('part2_badge'), 540, 1420, FP.yellow, { size: 46, scale: ease.outBack(ramp(T, sh.part2, sh.part2 + 0.4)) });
      ftext(ctx, sh.p2l1 || S('part2_line1'), 540, 1530, 38, FP.white, { alpha: p, maxW: 980 });
      ftext(ctx, sh.p2l2 ?? S('part2_line2'), 540, 1585, 38, FP.white, { alpha: p, maxW: 980 });
    }
  },
};

// ---------- overlay: progress dots, clock pill, tag, karaoke subtitles ----------
let SUBS = null;
function buildSubs() {
  const words = [];
  for (const seg of TL.transcript || []) for (const w of seg.words) words.push({ w: w.w.trim(), s: w.s + TL.voiceOffset, e: w.e + TL.voiceOffset });
  // merge split tokens like "крипто" + "-кошелёк"
  for (let i = words.length - 1; i > 0; i--) if (/^[-—]?-/.test(words[i].w) && words[i].w.length > 1 && words[i].w !== '—') { words[i - 1].w += words[i].w; words[i - 1].e = words[i].e; words.splice(i, 1); }
  const chunks = []; let cur = [];
  const flush = () => { if (cur.length) chunks.push(cur); cur = []; };
  for (const w of words) {
    if (w.w === '—') { if (cur.length) cur[cur.length - 1].w += ' —'; continue; }
    const len = cur.reduce((a, x) => a + x.w.length + 1, 0);
    if (cur.length >= 3 || len + w.w.length > 18) flush();
    cur.push(w);
    if (/[.,?!:]$/.test(w.w)) flush();
  }
  flush();
  chunks.forEach((c, i) => { c.start = c[0].s; c.end = i < chunks.length - 1 ? Math.min(chunks[i + 1][0].s, c[c.length - 1].e + 0.9) : c[c.length - 1].e + 1.0; });
  SUBS = chunks;
}
const HL_Y = /^(10|24|биткоин|деньг|миллион|украд|полици|кошел|неизвестн|звон|сообщени|правд|разбогат|подар|машин|квартир|финанс|новост|риск|безопасн|комментар|выбер|тишин|ч(е|ё)рт)/i;
const HL_R = /^(не|никто|ничего|мы|знаем|украли|страшное|опасн)$/i;
function drawSubs(ctx, T) {
  if (!SUBS) buildSubs();
  const c = SUBS.find(c => T >= c.start && T < c.end);
  if (!c) return;
  const y = 1500, size = 74;
  ctx.save(); ctx.font = font(900, size);
  const parts = c.map(w => ({ ...w, txt: w.w.toUpperCase().replace(/[«»"]/g, '') }));
  const space = ctx.measureText(' ').width;
  let total = parts.reduce((a, p) => a + ctx.measureText(p.txt).width, 0) + space * (parts.length - 1);
  const sc = Math.min(1, 1000 / total);
  let x = 540 - total * sc / 2;
  for (const p of parts) {
    const w = ctx.measureText(p.txt).width * sc;
    if (T >= p.s - 0.03) {
      const k = ease.outBack(ramp(T, p.s - 0.03, p.s + 0.12));
      const clean = p.txt.replace(/[.,?!:—]/g, '').toLowerCase();
      const hr = TL.overlay && TL.overlay.hlRed ? new RegExp(TL.overlay.hlRed, 'i') : HL_R, hy = TL.overlay && TL.overlay.hlYellow ? new RegExp(TL.overlay.hlYellow, 'i') : HL_Y;
      const col = hr.test(clean) ? FP.red : hy.test(clean) ? FP.yellow : FP.white;
      ctx.save(); ctx.translate(x + w / 2, y); ctx.scale(sc * (0.7 + 0.3 * k), sc * (0.7 + 0.3 * k));
      ctx.textAlign = 'center'; ctx.lineJoin = 'round'; ctx.lineWidth = 16; ctx.strokeStyle = '#000';
      ctx.strokeText(p.txt, 0, 0); ctx.fillStyle = col; ctx.fillText(p.txt, 0, 0);
      ctx.restore();
    }
    x += w + space * sc;
  }
  ctx.restore();
}
function flatOverlay(ctx, T, sh) {
  const O = TL.overlay || {};
  // soft dark band behind the subtitles
  const g = ctx.createLinearGradient(0, 1280, 0, 1700); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.5, 'rgba(0,0,0,0.35)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 1280, W, 420);
  // progress dots
  if (sh.dots !== false && O.stages) {
    let st = 0; O.stages.forEach((s, i) => { if (T >= s.t) st = i + 1; });
    for (let i = 0; i < O.stages.length; i++) {
      const x = 540 + (i - (O.stages.length - 1) / 2) * 92, y = 150;
      const done = i + 1 <= st, curr = i + 1 === st;
      const pop = curr ? 1 + 0.12 * ease.outBack(clamp(1 - (T - O.stages[i].t) / 0.4)) : 1;
      circ(ctx, x, y, 30 * pop, done ? FP.red : 'rgba(0,0,0,0.35)');
      ftext(ctx, String(i + 1), x, y + 13, 36, FP.white, { stroke: false, alpha: done ? 1 : 0.7 });
    }
    if (st > 0) ftext(ctx, O.stages[st - 1].name, 540, 240, 34, FP.white, { ls: 3 });
  }
  // clock pill
  if (sh.clock) {
    const s = STR[sh.clock] || sh.clock;
    ctx.save(); ctx.font = font(800, 38, 'mono'); const w = ctx.measureText(s).width + 70;
    ctx.fillStyle = sh.clock === 'countdown_clock' ? FP.red : FP.red; rr(ctx, 50, 110, w, 64, 32); ctx.fill();
    circ(ctx, 84, 142, 14, '#fff'); ctx.fillStyle = FP.red; ctx.fillRect(82, 132, 4, 12);
    ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.fillText(s, 108, 145); ctx.restore();
  }
  // shot tag above the subtitles
  if (sh.tag) {
    const p = ease.outBack(ramp(T, sh.tag.at ?? sh.start, (sh.tag.at ?? sh.start) + 0.3));
    const col = { yellow: FP.yellow, red: FP.red, blue: FP.blue, green: FP.green }[sh.tag.color || 'yellow'];
    tagBox(ctx, sh.tag.text, 540, 1385, col, { size: 36, scale: p, rot: sh.tag.rot || 0 });
  }
  if (sh.subs !== false) drawSubs(ctx, T);
  if (T >= TL.cues.hard_black) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
}

// vertical thumbnail in the flat style
window.renderThumbFlat = () => {
  const ctx = MAIN.getContext('2d'), T = 2.0;
  STR.clock = STR.clock_night;
  ctx.save();
  fbg(ctx, FP.bg, 'rgba(232,52,63,0.35)');
  glow(ctx, 640, 1000, 700, 'rgba(120,170,255,0.35)', 1);
  const scr = scrWallet(T, { refresh: -1, pulse: 0.8 });
  drawPhone(ctx, 660, 1020, 0.72, 0.1, scr, { on: 1 });
  tagBox(ctx, S('stolen'), 660, 860, FP.red, { size: 90, rot: -0.12 });
  ftext(ctx, S('thumb_1'), 540, 300, 230, FP.white);
  ftext(ctx, S('thumb_2'), 540, 470, 150, FP.yellow, { maxW: 1000 });
  heroFace(ctx, T, 270, 1520, 1.0, 'shock', { lookX: 0.8, lookY: -0.5, sweat: true, seed: 0.5 });
  tagBox(ctx, S('thumb_tag'), 790, 1640, FP.red, { size: 54, rot: -0.06 });
  ftext(ctx, '?', 960, 700, 200, FP.red);
  ctx.restore();
  return MAIN.toDataURL('image/png');
};
