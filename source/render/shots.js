// All shots of "The Black Death"
const L = require('./lib');
const M = require('./map');
const { W, H, rng, clamp, lerp, prog, ease, easeS, easeOut, mix, rgba, glow, beam, canvas, textC } = L;

// ---------------- static asset builders ----------------
function buildStreet(seed, o) {
  const c = canvas(2700, 1500), x = c.getContext('2d'), r = rng(seed);
  const base = 1150; let px = -40; const lights = [], chim = [], doors = [];
  const plasters = o.plasters, roofs = o.roofs; let i = 0;
  while (px < 2700) {
    const w = 170 + r() * 110, h = 300 + r() * 190, fl = h > 420 ? 3 : 2;
    const ls = L.house(x, px, base, w, h, { plaster: plasters[i % plasters.length], timber: o.timber, roof: roofs[i % roofs.length], floors: fl, chimney: r() < 0.6, seedOff: i, litChance: o.lit, boarded: o.boarded && r() < 0.5, jetty: 10 }, r);
    ls.forEach(l => l.chimney ? chim.push(l) : lights.push(l));
    doors.push({ x: px + w / 2, y: base });
    px += w + 34 + r() * 26; i++;
  }
  // gaps between houses get dark alley fill behind? draw ground
  L.cobbles(x, 0, base, 2700, 350, seed + 5, o.ground[0], o.ground[1]);
  const g = x.createLinearGradient(0, base, 0, base + 120); g.addColorStop(0, 'rgba(0,0,0,0.5)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(0, base, 2700, 120);
  if (o.extras) o.extras(x, base, r);
  return { c, lights, chim, base };
}
function behindStreetFill(ctx, col) { ctx.fillStyle = col; }

const PAL_DUSK = {
  sky: [[0, '#16181e'], [0.45, '#2a2a2f'], [0.75, '#4a4440'], [1, '#6b5a47']],
  far: '#3a3838', mid: '#2a292b', plasters: ['#5c5447', '#4f4b45', '#625647', '#57514a'], roofs: ['#2c2522', '#33302f', '#3a2c24'], timber: '#251b14', ground: ['#1e1d1b', '#3a3631'],
};
const PAL_DAWN = {
  sky: [[0, '#1d1f27'], [0.45, '#3b3a3e'], [0.75, '#7a6250'], [1, '#c39462']],
  far: '#4a4644', mid: '#33302f', plasters: ['#6a5f50', '#5b564e', '#6e604e', '#625b52'], roofs: ['#342b26', '#3a3634', '#40322a'], timber: '#2a1f17', ground: ['#24221f', '#45403a'],
};

let A = null;
function build() {
  if (A) return A; A = {};
  A.vig = L.vignette(0.8);
  A.fog = L.fogTexture(11, 2400, 520, '#9a958c', 60, 120, 320, 0.05, 0.16);
  A.fogDark = L.fogTexture(12, 2400, 520, '#6f6a62', 50, 140, 340, 0.06, 0.18);
  A.clouds = L.cloudLayer(13, 2600, 700, ['#3c3b3e', '#2a2a2e', '#4a4644']);
  A.cloudsDawn = L.cloudLayer(14, 2600, 700, ['#5a4c44', '#3a3638', '#7a5e48']);
  for (const [key, pal, seed] of [['dusk', PAL_DUSK, 100], ['dawn', PAL_DAWN, 100]]) {
    const sky = canvas(W, 1500), sx = sky.getContext('2d'); L.skyGradient(sx, W, 1500, pal.sky);
    if (key === 'dusk') { L.glow(sx, 1450, 260, 260, '#c8c0a8', 0.35); sx.fillStyle = '#d8d0b8'; sx.beginPath(); sx.arc(1450, 260, 46, 0, 7); sx.fill(); }
    else { L.glow(sx, 760, 1150, 900, '#e0a060', 0.45); }
    const far = L.skyline(seed + 1, 2700, 760, pal.far, 640, { church: [1500], churchS: 0.95, minH: 80, varH: 120 });
    const mid = L.skyline(seed + 2, 2700, 760, pal.mid, 660, { lights: true, minH: 120, varH: 160, church: [520], churchS: 0.7 });
    const street = buildStreet(seed + 3, { plasters: pal.plasters, roofs: pal.roofs, timber: pal.timber, ground: pal.ground, lit: key === 'dusk' ? 0.38 : 0.08 });
    A[key] = { sky, far, mid, street };
  }
  // Europe 1348 market street (colder)
  A.market = buildStreet(310, {
    plasters: ['#4e4c48', '#57524a', '#4a4743', '#5a5248'], roofs: ['#2a2828', '#302a26'], timber: '#221a14', ground: ['#1c1c1c', '#36332f'], lit: 0.3,
    extras: (x, base, r) => { for (let i = 0; i < 4; i++) stall(x, 260 + i * 560, base + 70, r, true); }
  });
  // abandoned street
  A.empty = buildStreet(520, {
    plasters: ['#4a4741', '#514b43', '#47443f'], roofs: ['#282524', '#2e2824'], timber: '#1f1812', ground: ['#1b1a19', '#33302c'], lit: 0.03, boarded: true,
    extras: (x, base, r) => {
      for (let i = 0; i < 2; i++) stall(x, 700 + i * 1100, base + 70, r, true, true);
      // weeds
      for (let i = 0; i < 160; i++) { const wx = r() * 2700, wy = base + 10 + r() * 30; x.strokeStyle = r() < 0.5 ? '#2e3326' : '#3a3a2a'; x.lineWidth = 2; x.beginPath(); x.moveTo(wx, wy); x.lineTo(wx + (r() - 0.5) * 14, wy - 10 - r() * 22); x.stroke(); }
    }
  });
  A.emptyMid = L.skyline(530, 2700, 760, '#2a2829', 660, { minH: 120, varH: 160, church: [1900], churchS: 0.8 });
  A.emptyFar = L.skyline(531, 2700, 760, '#3a3736', 640, { minH: 80, varH: 120 });
  // central asia
  A.asiaSky = canvas(W, 1100); { const x = A.asiaSky.getContext('2d'); L.skyGradient(x, W, 1100, [[0, '#23252e'], [0.4, '#4a4648'], [0.62, '#8a6c56'], [0.72, '#b88a5c'], [1, '#6a5446']]); L.glow(x, 420, 420, 560, '#f0b070', 0.5); x.fillStyle = 'rgba(250,210,150,0.9)'; x.beginPath(); x.arc(420, 430, 34, 0, 7); x.fill(); }
  A.mtFar = L.mountains(61, 2800, 900, 600, 330, '#5d5d68', '#a29fa6');
  A.mtMid = L.mountains(62, 2800, 900, 660, 230, '#47464f', '#7c7a82');
  A.hills = L.mountains(63, 3000, 900, 760, 90, '#3a322a', null);
  // port of Kaffa
  A.portSky = canvas(W, 1100); { const x = A.portSky.getContext('2d'); L.skyGradient(x, W, 1100, [[0, '#1d1e24'], [0.45, '#3a3836'], [0.68, '#7a6048'], [1, '#3a3a3c']]); L.glow(x, 1500, 640, 600, '#e0a060', 0.3); }
  A.crimea = L.mountains(71, 2800, 900, 640, 170, '#3c3a3c', null);
  A.night = canvas(W, 1100); { const x = A.night.getContext('2d'); L.skyGradient(x, W, 1100, [[0, '#0f1116'], [0.5, '#1e2128'], [0.7, '#33363c'], [1, '#1a1c20']]); L.glow(x, 520, 260, 300, '#c8ccd0', 0.3); x.fillStyle = '#d6d8d2'; x.beginPath(); x.arc(520, 260, 40, 0, 7); x.fill(); const r = rng(5); for (let i = 0; i < 120; i++) { x.fillStyle = `rgba(220,220,210,${0.15 + r() * 0.4})`; x.fillRect(r() * W, r() * 560, 2, 2); } }
  A.sicily = L.mountains(81, 2800, 900, 650, 200, '#202228', null);
  // interior wall texture
  A.wall = canvas(W, H); { const x = A.wall.getContext('2d'), r = rng(9); x.fillStyle = '#231c17'; x.fillRect(0, 0, W, H); for (let i = 0; i < 40; i++) { x.fillStyle = `rgba(${r() < 0.5 ? '0,0,0' : '90,70,50'},${0.05 + r() * 0.08})`; x.fillRect(r() * W, r() * H, 80 + r() * 300, 20 + r() * 80); } x.fillStyle = '#16110d'; [[0, 120, W, 34], [0, 880, W, 40]].forEach(b => x.fillRect(...b)); for (let i = 0; i < 6; i++) x.fillRect(i * 360 + 40, 0, 30, H); }
  return A;
}

// market stall (closed); (x,y) = front-left ground
function stall(ctx, x, y, r, closed, broken) {
  const w = 300, h = 170;
  ctx.fillStyle = '#2e2218'; ctx.fillRect(x, y - h, 12, h); ctx.fillRect(x + w - 12, y - h, 12, h);
  ctx.fillStyle = '#3a2b1f'; ctx.fillRect(x, y - 70, w, 70);
  ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 3; for (let k = 1; k < 7; k++) { ctx.beginPath(); ctx.moveTo(x + k * w / 7, y - 70); ctx.lineTo(x + k * w / 7, y); ctx.stroke(); }
  // awning (sagging, faded)
  ctx.fillStyle = broken ? '#4a3a2e' : '#5a3a2c'; ctx.beginPath(); ctx.moveTo(x - 20, y - h); ctx.lineTo(x + w + 20, y - h); ctx.lineTo(x + w + 30, y - h + 50); ctx.quadraticCurveTo(x + w / 2, y - h + (broken ? 90 : 66), x - 30, y - h + 50); ctx.closePath(); ctx.fill();
  ctx.fillStyle = 'rgba(200,180,140,0.12)'; for (let k = 0; k < 5; k += 2) { ctx.beginPath(); ctx.moveTo(x - 20 + k * (w + 40) / 5, y - h); ctx.lineTo(x - 20 + (k + 1) * (w + 40) / 5, y - h); ctx.lineTo(x - 26 + (k + 1) * (w + 40) / 5, y - h + 56); ctx.lineTo(x - 26 + k * (w + 40) / 5, y - h + 56); ctx.fill(); }
  if (closed) { ctx.fillStyle = '#2a1f17'; ctx.fillRect(x + 12, y - h + 50, w - 24, 50); ctx.strokeStyle = 'rgba(0,0,0,0.3)'; for (let k = 1; k < 6; k++) { ctx.beginPath(); ctx.moveTo(x + 12, y - h + 50 + k * 8); ctx.lineTo(x + w - 12, y - h + 50 + k * 8); ctx.stroke(); } }
  // crates / baskets / barrels
  ctx.fillStyle = '#35281d'; ctx.fillRect(x + w + 30, y - 60, 70, 60); ctx.strokeStyle = '#1e160f'; ctx.lineWidth = 4; ctx.strokeRect(x + w + 30, y - 60, 70, 60); ctx.beginPath(); ctx.moveTo(x + w + 30, y - 60); ctx.lineTo(x + w + 100, y); ctx.stroke();
  ctx.fillStyle = '#3f3122'; L.ellipse(ctx, x - 40, y - 34, 30, 34); ctx.fill(); ctx.fillStyle = '#2a2018'; ctx.fillRect(x - 70, y - 44, 60, 6); ctx.fillRect(x - 70, y - 22, 60, 6);
  if (broken) { ctx.fillStyle = '#3a2b1f'; ctx.save(); ctx.translate(x + w / 2, y - 10); ctx.rotate(0.3); ctx.fillRect(-60, -6, 120, 12); ctx.restore(); }
}

// ---------------- shot helpers ----------------
function camZoom(ctx, z, cx = W / 2, cy = H / 2) { ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy); }
function label(ctx, t, inAt, outAt, l1, l2) {
  const a = clamp(prog(t, inAt, inAt + 0.8)) * (1 - prog(t, outAt - 0.6, outAt));
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a; const x0 = 90, y0 = 96, slide = (1 - easeOut(prog(t, inAt, inAt + 1))) * -20;
  ctx.fillStyle = '#b2453a'; ctx.fillRect(x0 + slide, y0 - 28, 6, l2 ? 84 : 46);
  textC(ctx, l1, x0 + 22 + slide, y0 - 6, '38px OswaldBold', '#ece2cf', 5, 'left');
  if (l2) textC(ctx, l2, x0 + 22 + slide, y0 + 36, '28px PTSans', 'rgba(236,226,207,0.75)', 2, 'left');
  ctx.restore();
}
function flock(ctx, t, x0, y0, n, seed, sc = 1, vx = 60) {
  const r = rng(seed); ctx.strokeStyle = '#141416'; ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const ox = r() * 260, oy = r() * 120, ph = r() * 6, s = (0.6 + r() * 0.5) * sc;
    const x = x0 + ox + t * vx, y = y0 + oy + Math.sin(t * 0.8 + ph) * 10, f = Math.sin(t * 9 + ph) * 8 * s;
    ctx.lineWidth = 3 * s; ctx.beginPath(); ctx.moveTo(x - 14 * s, y - f); ctx.quadraticCurveTo(x - 6 * s, y - 6 * s, x, y); ctx.quadraticCurveTo(x + 6 * s, y - 6 * s, x + 14 * s, y - f); ctx.stroke();
  }
}
function crow(ctx, x, y, s, t, ph, d = 1) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s * d, s); ctx.fillStyle = '#0e0e10';
  const peck = Math.max(0, Math.sin(t * 1.3 + ph)) > 0.92 ? 0.5 : 0;
  L.ellipse(ctx, 0, -22, 26, 16, -0.2); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-20, -18); ctx.lineTo(-48, -6); ctx.lineTo(-22, -28); ctx.fill();
  ctx.save(); ctx.translate(18, -34); ctx.rotate(peck); L.ellipse(ctx, 6, 0, 12, 11); ctx.fill(); ctx.beginPath(); ctx.moveTo(14, -4); ctx.lineTo(32, 2); ctx.lineTo(14, 4); ctx.fill(); ctx.restore();
  ctx.strokeStyle = '#0e0e10'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-4, -8); ctx.lineTo(-6, 6); ctx.moveTo(6, -8); ctx.lineTo(6, 6); ctx.stroke();
  ctx.restore();
}
function candle(ctx, x, y, s, t, life = 1) {
  ctx.fillStyle = '#d8ccb0'; ctx.fillRect(x - 9 * s, y - 60 * s, 18 * s, 60 * s);
  ctx.fillStyle = '#3a2c20'; L.ellipse(ctx, x, y, 26 * s, 7 * s); ctx.fill();
  if (life <= 0) return;
  const fl = 1 + Math.sin(t * 17) * 0.06 + Math.sin(t * 7.3) * 0.08;
  ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, x, y - 75 * s, 420 * s * life, '#f0a850', 0.35 * life * fl); glow(ctx, x, y - 75 * s, 90 * s * life, '#ffd890', 0.6 * life); ctx.restore();
  ctx.fillStyle = '#ffd890'; L.ellipse(ctx, x + Math.sin(t * 9) * 1.5 * s, y - 76 * s, 7 * s * life, 15 * s * life * fl); ctx.fill();
  ctx.fillStyle = '#fff4d6'; L.ellipse(ctx, x, y - 72 * s, 3 * s * life, 7 * s * life); ctx.fill();
}
function seaBand(ctx, y0, y1, c0, c1, t, seed, hl = '#c8b090', ha = 0.25, sx = 0) {
  const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, c0); g.addColorStop(1, c1); ctx.fillStyle = g; ctx.fillRect(0, y0, W, y1 - y0);
  const r = rng(seed); ctx.strokeStyle = rgba(hl, ha); ctx.lineCap = 'round';
  for (let i = 0; i < 140; i++) {
    const yy = y0 + Math.pow(r(), 1.6) * (y1 - y0), k = (yy - y0) / (y1 - y0), len = 20 + k * 90 * r();
    const xx = ((r() * W * 1.4 + t * (8 + k * 20) + sx * (0.3 + k)) % (W * 1.4)) - W * 0.2;
    ctx.lineWidth = 1.5 + k * 3; ctx.globalAlpha = 0.4 + 0.6 * Math.abs(Math.sin(t * 1.2 + i)); ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx + len, yy); ctx.stroke();
  }
  ctx.globalAlpha = 1;
}

// ---------------- SHOTS ----------------
// city: c=0 rooftops -> c=1 street.  tod 'dusk'|'dawn'
function cityView(ctx, t, c, z, pan, key, o = {}) {
  const S = A[key];
  ctx.save(); camZoom(ctx, z);
  ctx.drawImage(S.sky, 0, lerp(0, -260, c));
  L.drawWrap(ctx, key === 'dusk' ? A.clouds : A.cloudsDawn, t * 12 + pan * 0.1, lerp(-60, -240, c), 1, 0.9);
  if (o.birds) flock(ctx, t, -200 + o.birds, lerp(260, 120, c), 9, 4, 0.9, 70);
  const fy = lerp(220, 60, c); ctx.drawImage(S.far.c, -200 - pan * 0.25, fy);
  L.drawWrap(ctx, A.fogDark, t * 10, fy + 380, 1, key === 'dusk' ? 0.55 : 0.45);
  const my = lerp(340, 40, c); ctx.drawImage(S.mid.c, -300 - pan * 0.5, my);
  ctx.save(); ctx.translate(-300 - pan * 0.5, my); L.windowLights(ctx, S.mid.lights, t, L => o.kill ? o.kill(L) : 1); ctx.restore();
  L.drawWrap(ctx, A.fog, t * 16 + 300, my + 420, 1, 0.45);
  const sy = lerp(300, -390, c), sx = -260 - pan;
  ctx.save(); ctx.translate(sx, sy);
  ctx.drawImage(S.street.c, 0, 0);
  S.street.chim.forEach((ch, i) => L.smoke(ctx, ch.x, ch.y, t + i * 3, i, key === 'dusk' ? '#6a6660' : '#8a8078', 0.35, 1));
  L.windowLights(ctx, S.street.lights, t, L => o.kill ? o.kill(L) : 1);
  if (o.street) o.street(ctx, S.street.base);
  ctx.restore();
  L.drawWrap(ctx, A.fog, t * 26, sy + 1000, 1.2, lerp(0.15, 0.55, c));
  ctx.restore();
}

function shotCity(ctx, t, D) {
  const c = easeS(prog(t, 0.6, D - 1.2));
  const kill = Lt => (Lt.off < 0.3 ? 1 - prog(t, 5 + Lt.off * 20, 5.4 + Lt.off * 20) : 1);
  cityView(ctx, t, c, lerp(1.12, 1.0, easeS(t / D)), t * 14, 'dusk', {
    kill, street: (x, base) => {
      // woman hurrying left, man with handcart right, boy in doorway
      const wx = 2050 - t * 85; L.person(x, wx, base + 140, 0.62, { dir: -1, walk: t * 6.5, dress: true, tunic: '#4a3028', veil: '#7a7266', brows: 'worried', apron: '#5a5246' }, t);
      const mx = 260 + t * 60; cart(x, mx + 120, base + 175, 0.62, t * 3); L.person(x, mx, base + 175, 0.65, { dir: 1, walk: t * 5, tunic: '#4a3a2a', hose: '#2a2420', hood: '#3a3028', belt: '#1e1610', armFront: -0.9, brows: 'worried' }, t);
      const bx = 1290; L.person(x, bx, base + 110, 0.55, { dir: 0, hair: 'messy', tunic: '#26262c', brows: 'worried', look: Math.sin(t * 0.7) }, t);
      // lantern on wall
      x.save(); x.globalCompositeOperation = 'screen'; glow(x, 1180, base - 210, 120, '#e8a850', 0.4 + Math.sin(t * 6) * 0.04); x.restore();
    }
  });
}
function cart(ctx, x, y, s, rot) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = '#3a2a1c'; ctx.fillRect(-20, -120, 230, 60); ctx.fillStyle = '#2a1e14'; ctx.fillRect(-120, -88, 110, 10);
  ctx.fillStyle = '#5a4a36'; L.ellipse(ctx, 40, -138, 40, 26); ctx.fill(); L.ellipse(ctx, 110, -140, 44, 30); ctx.fill(); ctx.fillStyle = '#4a3c2c'; L.ellipse(ctx, 170, -134, 34, 22); ctx.fill();
  ctx.strokeStyle = '#1e160f'; ctx.lineWidth = 9; ctx.beginPath(); ctx.arc(95, -46, 46, 0, 7); ctx.stroke();
  ctx.lineWidth = 5; for (let k = 0; k < 4; k++) { const a = rot + k * Math.PI / 4; ctx.beginPath(); ctx.moveTo(95 - Math.cos(a) * 46, -46 - Math.sin(a) * 46); ctx.lineTo(95 + Math.cos(a) * 46, -46 + Math.sin(a) * 46); ctx.stroke(); }
  ctx.restore();
}

function shotWindow(ctx, t, D) {
  const z = lerp(1.0, 1.14, easeS(t / D));
  ctx.save(); camZoom(ctx, z, 1250, 520);
  // outside view
  ctx.save(); ctx.beginPath(); ctx.rect(1040, 170, 640, 620); ctx.clip();
  ctx.drawImage(A.dusk.sky, 0, -180); ctx.save(); ctx.translate(1040, 0); ctx.scale(0.6, 0.6);
  ctx.drawImage(A.dusk.far.c, -300, 520); ctx.drawImage(A.dusk.mid.c, -800, 560);
  ctx.translate(-800, 560); const lights = A.dusk.mid.lights;
  L.windowLights(ctx, lights, t, Lt => 1 - prog(t, 1 + Lt.off * (D - 3), 1.3 + Lt.off * (D - 3))); ctx.restore();
  L.drawWrap(ctx, A.fog, t * 20, 520, 0.8, 0.6);
  ctx.restore();
  // wall with window hole
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.rect(1040, 170, 640, 620); ctx.clip('evenodd'); ctx.drawImage(A.wall, 0, 0); ctx.restore();
  // frame + mullions
  ctx.fillStyle = '#1a130e'; ctx.fillRect(1020, 150, 680, 24); ctx.fillRect(1020, 786, 680, 30); ctx.fillRect(1020, 150, 24, 660); ctx.fillRect(1676, 150, 24, 660); ctx.fillRect(1350, 170, 18, 620); ctx.fillRect(1040, 460, 640, 16);
  // open shutter
  ctx.fillStyle = '#2b2018'; ctx.beginPath(); ctx.moveTo(1700, 160); ctx.lineTo(1860, 120); ctx.lineTo(1860, 860); ctx.lineTo(1700, 810); ctx.fill();
  // shelf + pots + herbs on left
  ctx.fillStyle = '#1a130e'; ctx.fillRect(120, 380, 520, 18);
  [[170, 60, '#4a3a2c'], [260, 80, '#3a3028'], [360, 50, '#5a4636'], [470, 70, '#3c3430']].forEach(([px, ph, pc]) => { ctx.fillStyle = pc; L.ellipse(ctx, px, 380 - ph / 2, 34, ph / 2); ctx.fill(); });
  for (let i = 0; i < 4; i++) { ctx.strokeStyle = '#2a3220'; ctx.lineWidth = 3; const hx = 200 + i * 110; ctx.beginPath(); ctx.moveTo(hx, 140); ctx.lineTo(hx, 200); ctx.stroke(); ctx.fillStyle = '#2f3524'; L.ellipse(ctx, hx, 230, 22, 40); ctx.fill(); }
  // candle on sill
  const life = 1 - prog(t, D - 1.4, D - 0.7);
  candle(ctx, 1150, 786, 1.1, t, life);
  if (life < 1) L.smoke(ctx, 1150, 700, t * 2, 3, '#8a8a8a', 0.4 * (1 - life), 0.5);
  // boy
  const look = Math.sin(t * 0.5) * 0.5;
  L.person(ctx, 820, 1360, 2.25, { dir: 1, hair: 'messy', tunic: '#232328', brows: 'worried', look: 0.5 + look, mouth: t > D - 3 ? 'frown' : null, armFront: -0.2, armBack: 0.1 }, t);
  // warm light on boy & room
  ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, 1150, 700, 900, '#c07a3a', 0.18 * life); ctx.restore();
  // dark falloff
  const g = ctx.createRadialGradient(1100, 600, 200, 1100, 600, 1300); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${0.75 + (1 - life) * 0.2})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  ctx.restore();
  if (life < 1) { ctx.fillStyle = `rgba(0,0,0,${(1 - life) * 0.75})`; ctx.fillRect(0, 0, W, H); }
}

function shotAsia(ctx, t, D, ev, lang) {
  const mapAt = ev.asiaMap;
  if (t < mapAt + 0.8) {
    ctx.save(); const pan = t * 22, z = lerp(1.06, 1.0, t / mapAt);
    camZoom(ctx, z);
    ctx.drawImage(A.asiaSky, 0, -20);
    ctx.drawImage(A.mtFar, -300 - pan * 0.15, 40);
    ctx.drawImage(A.mtMid, -200 - pan * 0.3, 60);
    L.drawWrap(ctx, A.fog, t * 8, 520, 0.8, 0.35);
    // lake
    const g = ctx.createLinearGradient(0, 700, 0, 800); g.addColorStop(0, '#9a7c62'); g.addColorStop(1, '#4a4448'); ctx.fillStyle = g; ctx.fillRect(0, 700, W, 100);
    const r = rng(7); ctx.strokeStyle = 'rgba(240,200,150,0.35)'; ctx.lineWidth = 2; for (let i = 0; i < 60; i++) { const yy = 705 + r() * 90, xx = (r() * W + t * 6) % W; ctx.globalAlpha = 0.3 + 0.7 * Math.abs(Math.sin(t + i)); ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx + 20 + r() * 50, yy); ctx.stroke(); } ctx.globalAlpha = 1;
    // sun reflection
    ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, 420 - pan * 0.15, 730, 220, '#f0b070', 0.35); ctx.restore();
    // settlement on near shore
    ctx.save(); ctx.translate(-pan * 0.55, 0);
    ctx.fillStyle = '#3e352c'; ctx.fillRect(-100, 790, 3000, 40);
    for (let i = 0; i < 7; i++) { const yx = 900 + i * 120 + (i % 2) * 30; L.yurt(ctx, yx, 820, 0.55 + (i % 3) * 0.08, i % 2 ? '#7a7062' : '#8a7f6e'); if (i % 3 === 0) L.smoke(ctx, yx, 750, t + i, i, '#8a8278', 0.35, 0.6); }
    for (let i = 0; i < 4; i++) { const hx = 1800 + i * 150; ctx.fillStyle = '#5a4a3a'; ctx.fillRect(hx, 760, 110, 62); ctx.fillStyle = '#4a3c2e'; ctx.fillRect(hx - 6, 754, 122, 10); ctx.fillStyle = '#1a1410'; ctx.fillRect(hx + 40, 784, 22, 38); }
    ctx.restore();
    ctx.drawImage(A.hills, -300 - pan * 0.8, 120);
    // caravan walking west (left)
    ctx.save(); ctx.translate(-pan * 1.0, 0);
    const base = 925, cx0 = 1500 - t * 55;
    const packs = [['#6e3a2a', '#7a6a3a'], ['#3a4a5a', '#6e3a2a'], ['#7a6a3a', '#4a3a2a']];
    for (let i = 0; i < 3; i++) { const x = cx0 + i * 330; L.camel(ctx, x, base, 1.0, -1, t * 3.2 + i, '#7a6048', packs[i]); }
    L.person(ctx, cx0 - 190, base + 6, 0.72, { dir: -1, walk: t * 4.5, tunic: '#5a4030', hose: '#2a2018', cap: '#8a7a60', belt: '#2a1e14', staff: true, brows: 'neutral' }, t);
    L.person(ctx, cx0 + 900, base + 6, 0.7, { dir: -1, walk: t * 4.5 + 1, tunic: '#3a4048', hose: '#2a2420', hood: '#5a4a3a', belt: '#2a1e14', brows: 'neutral' }, t);
    ctx.restore();
    // ground fg
    const gg = ctx.createLinearGradient(0, 920, 0, H); gg.addColorStop(0, '#2c241c'); gg.addColorStop(1, '#16120e'); ctx.fillStyle = gg; ctx.fillRect(0, 920, W, 200);
    // sun rays + dust
    beam(ctx, 420, 430, 1400, 1100, 1900, 700, '#f0b070', 0.10);
    beam(ctx, 420, 430, 900, 1100, 1300, 1100, '#f0b070', 0.07);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; L.dust(ctx, t, 21, 70, '#f0c890', 0.5); ctx.restore();
    ctx.restore();
    label(ctx, t, 0.6, mapAt + 0.6, lang === 'ru' ? 'ЦЕНТРАЛЬНАЯ АЗИЯ' : 'CENTRAL ASIA', lang === 'ru' ? 'Озеро Иссык-Куль · ок. 1338 г.' : 'Lake Issyk-Kul · c. 1338');
  }
  if (t > mapAt) {
    const a = prog(t, mapAt, mapAt + 0.8);
    const tmp = ctx; tmp.save(); tmp.globalAlpha = a;
    const u = easeS(prog(t, mapAt, mapAt + 3.6));
    const [ix, iy] = M.P('issyk');
    const cam = { x: lerp(M.MW * 0.52, ix - 330, u), y: lerp(M.MH * 0.5, iy + 40, u), z: lerp(0.62, 1.45, u) };
    M.drawMap(tmp, cam, t, {
      lang, overlay: (c, iz) => {
        const pu = prog(t, mapAt + 1.2, mapAt + 2.4), pulse = 0.5 + 0.5 * Math.sin(t * 3);
        // Central Asia highlight
        c.save(); c.globalAlpha = pu; const [cx, cy] = M.proj(68, 42);
        const g = c.createRadialGradient(cx, cy, 0, cx, cy, 520); g.addColorStop(0, `rgba(150,30,20,${0.35 + pulse * 0.1})`); g.addColorStop(1, 'rgba(150,30,20,0)'); c.fillStyle = g; c.save(); c.clip(M.landPath); c.fillRect(cx - 600, cy - 600, 1200, 1200); c.restore();
        textC(c, lang === 'ru' ? 'ЦЕНТРАЛЬНАЯ АЗИЯ' : 'CENTRAL ASIA', cx - 40, cy - 190, `${40 * iz * 1.3}px PTSerifBold`, 'rgba(60,14,8,0.85)', 10 * iz);
        c.restore();
        const pr = prog(t, mapAt + 1.8, mapAt + 2.6);
        for (let k = 0; k < 3; k++) { const ph = ((t * 0.6 + k / 3) % 1); c.strokeStyle = `rgba(150,25,15,${(1 - ph) * 0.8 * pr})`; c.lineWidth = 3 * iz; c.beginPath(); c.arc(ix, iy, 10 + ph * 90, 0, 7); c.stroke(); }
        if (pr > 0) M.cityDot(c, 'issyk', iz, lang, pr, { red: true, fs: 30 });
        if (pr > 0) textC(c, '1338–1339', ix + 22 * iz * 1.4, iy + 34 * iz * 1.4, `${24 * iz * 1.3}px PTSerifBold`, `rgba(60,14,8,${0.85 * pr})`, 2, 'left');
      }
    });
    tmp.restore();
  }
}

function shotTrade(ctx, t, D, ev, lang) {
  const mapAt = ev.tradeMap, inf = ev.infect, pl = ev.plague;
  if (t < mapAt + 0.8) {
    ctx.save(); const pan = t * 30; camZoom(ctx, lerp(1.0, 1.08, t / mapAt));
    ctx.drawImage(A.portSky, 0, 0);
    L.drawWrap(ctx, A.clouds, t * 10, -100, 1, 0.6);
    ctx.drawImage(A.crimea, -400 - pan * 0.2, 60);
    // fortress walls of Kaffa on hill
    ctx.save(); ctx.translate(-pan * 0.25, 0); ctx.fillStyle = '#2e2c2e';
    ctx.fillRect(200, 600, 900, 110); for (let i = 0; i < 30; i++) ctx.fillRect(200 + i * 30, 588, 18, 14);
    [180, 460, 760, 1080].forEach(tx => { ctx.fillRect(tx, 530, 70, 180); for (let k = 0; k < 3; k++) ctx.fillRect(tx - 4 + k * 28, 516, 18, 16); });
    ctx.fillRect(1240, 560, 90, 150); ctx.beginPath(); ctx.moveTo(1230, 562); ctx.lineTo(1285, 470); ctx.lineTo(1340, 562); ctx.fill();
    ctx.restore();
    L.drawWrap(ctx, A.fog, t * 12, 470, 0.8, 0.4);
    seaBand(ctx, 700, H, '#4a4a4a', '#1c1e22', t, 3, '#d0a070', 0.18, pan);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, 1500 - pan * 0.2, 720, 300, '#e0a060', 0.25); ctx.restore();
    // ships
    L.cog(ctx, 600 - pan * 0.4, 760, 0.35, 1, t, { ph: 1 });
    L.cog(ctx, 1650 - pan * 0.5, 800, 0.5, -1, t, { ph: 2, stripe: '#2a3a5a' });
    const big = L.cog(ctx, 1250 - pan * 0.8, 960, 1.05, -1, t, { ph: 0 });
    // quay foreground
    ctx.save(); ctx.translate(-pan * 1.1, 0);
    ctx.fillStyle = '#2a2622'; ctx.fillRect(-200, 930, 1300, 200); ctx.fillStyle = '#3a3530'; ctx.fillRect(-200, 920, 1300, 18);
    ctx.strokeStyle = 'rgba(0,0,0,0.35)'; ctx.lineWidth = 3; for (let i = 0; i < 20; i++) { ctx.beginPath(); ctx.moveTo(-200 + i * 70, 938); ctx.lineTo(-200 + i * 70, H); ctx.stroke(); }
    [[60, '#3f3122'], [140, '#35281d'], [240, '#3f3122']].forEach(([bx, bc]) => { ctx.fillStyle = bc; L.ellipse(ctx, bx, 880, 34, 42); ctx.fill(); ctx.fillStyle = '#22180f'; ctx.fillRect(bx - 34, 862, 68, 6); ctx.fillRect(bx - 34, 892, 68, 6); });
    ctx.fillStyle = '#5a4a36'; for (let i = 0; i < 5; i++) { L.ellipse(ctx, 360 + (i % 3) * 52, 900 - Math.floor(i / 3) * 34, 30, 22); ctx.fill(); }
    // crane
    ctx.strokeStyle = '#1e1813'; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(700, 930); ctx.lineTo(700, 520); ctx.lineTo(980, 600); ctx.stroke(); ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(960, 600); ctx.lineTo(960, 700 + Math.sin(t) * 20); ctx.stroke(); ctx.fillStyle = '#4a3a2a'; ctx.fillRect(935, 700 + Math.sin(t) * 20, 50, 40);
    // porters
    for (let i = 0; i < 3; i++) { const px = ((150 + i * 260 + t * 70) % 900) - 50; L.person(ctx, px, 1000, 0.58, { dir: 1, walk: t * 5 + i, tunic: ['#5a4030', '#4a4a3a', '#3a3040'][i], hose: '#2a2018', cap: i === 1 ? '#7a6a50' : null, hair: i !== 1 ? 'short' : null, belt: '#2a1e14', armFront: -2.6, armBack: -2.5, brows: 'neutral' }, t); ctx.fillStyle = '#6a5a42'; L.ellipse(ctx, px + 4, 1000 - 0.58 * 408, 44, 22); ctx.fill(); ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.fillRect(px - 30, 1000 - 0.58 * 408 - 3, 66, 6); }
    ctx.restore();
    flock(ctx, t, 300, 260, 5, 9, 1.1, 50);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; L.dust(ctx, t, 31, 40, '#f0c890', 0.35); ctx.restore();
    ctx.restore();
    label(ctx, t, 0.4, mapAt + 0.6, lang === 'ru' ? 'КАФФА · ЧЁРНОЕ МОРЕ' : 'KAFFA · BLACK SEA', lang === 'ru' ? 'Торговый порт Генуи' : 'A Genoese trading port');
  }
  if (t > mapAt) {
    const a = prog(t, mapAt, mapAt + 0.8);
    ctx.save(); ctx.globalAlpha = a;
    const u = prog(t, mapAt + 0.2, inf + 0.6);          // route drawing progress
    const v = prog(t, inf, D + 0.6);                     // infection progress
    const k = easeS(prog(t, mapAt, D + 0.6));
    const [ix, iy] = M.P('issyk'), [mx, my] = M.P('messina');
    const cam = { x: lerp(ix - 350, mx + 500, k), y: lerp(iy - 60, my - 120, k), z: lerp(0.95, 0.72, k) };
    M.drawMap(ctx, cam, t, {
      lang, overlay: (c, iz) => {
        for (const rt of M.ROUTES) {
          const f = prog(u, rt.t0, rt.t1); if (f <= 0) continue;
          c.save(); c.setLineDash([16 * 1.2, 11 * 1.2]); c.strokeStyle = 'rgba(40,26,12,0.85)'; c.lineWidth = 4 * iz * 1.1; M.partial(c, rt.geo, f); c.stroke(); c.restore();
        }
        for (const rt of M.ROUTES) {
          const f = prog(v, rt.t0, rt.t1); if (f <= 0) continue;
          c.save(); c.lineCap = 'round'; c.strokeStyle = 'rgba(160,20,10,0.25)'; c.lineWidth = 22 * iz; M.partial(c, rt.geo, f); c.stroke();
          c.strokeStyle = 'rgba(170,30,15,0.9)'; c.lineWidth = 6 * iz; const e = M.partial(c, rt.geo, f); c.stroke(); c.restore();
          if (f < 1) { c.save(); c.globalCompositeOperation = 'screen'; glow(c, e[0], e[1], 60 * iz * 1.5, '#ff5030', 0.7); c.restore(); }
        }
        const cities = [['issyk', 0], ['samarkand', 0.12], ['sarai', 0.38], ['kaffa', 0.52], ['const', 0.62], ['messina', 0.8], ['genoa', 0.9], ['venice', 0.95], ['marseille', 0.97], ['alex', 0.85]];
        cities.forEach(([key, at]) => { const ap = prog(u, at - 0.02, at + 0.06); if (ap > 0) M.cityDot(c, key, iz, lang, ap, { red: prog(v, at, at + 0.05) > 0.5, fs: key === 'kaffa' ? 34 : 28 }); });
        // plague pulse on Kaffa
        const pp = prog(t, pl - 0.2, pl + 0.6); if (pp > 0) { const [kx, ky] = M.P('kaffa'); for (let q = 0; q < 3; q++) { const ph = ((t * 0.7 + q / 3) % 1); c.strokeStyle = `rgba(170,25,15,${(1 - ph) * 0.8 * pp})`; c.lineWidth = 3 * iz; c.beginPath(); c.arc(kx, ky, 12 + ph * 110, 0, 7); c.stroke(); } }
      }
    });
    // red flash at "it was the plague"
    const fl = prog(t, pl - 0.1, pl + 0.3) * (1 - prog(t, pl + 0.3, pl + 1.6)); if (fl > 0) { ctx.fillStyle = `rgba(120,10,5,${fl * 0.25})`; ctx.fillRect(0, 0, W, H); }
    ctx.restore();
  }
}

function shotEurope(ctx, t, D, ev, lang) {
  const cityAt = ev.europeCity, docAt = ev.europeDoc;
  if (t < cityAt + 0.8) {
    // 1347 - ship arriving at Messina at night
    ctx.save(); camZoom(ctx, lerp(1.0, 1.1, t / cityAt), 1200, 700);
    ctx.drawImage(A.night, 0, 0);
    L.drawWrap(ctx, A.clouds, t * 14, -120, 1, 0.5);
    ctx.drawImage(A.sicily, -300 - t * 6, 40);
    // harbor town silhouette w/ few lights
    ctx.save(); ctx.translate(900, 560); ctx.scale(0.5, 0.5); ctx.drawImage(A.dusk.mid.c, 0, 0, 2700, 760); ctx.restore();
    L.drawWrap(ctx, A.fogDark, t * 16, 520, 0.8, 0.6);
    seaBand(ctx, 690, H, '#2a2d33', '#0e1014', t, 8, '#c8ccd0', 0.18, 0);
    // moon reflection
    ctx.save(); ctx.globalCompositeOperation = 'screen'; for (let i = 0; i < 18; i++) { ctx.fillStyle = `rgba(210,214,210,${0.25 - i * 0.012})`; const yy = 700 + i * 20; ctx.fillRect(520 - 40 + Math.sin(t * 2 + i) * 18, yy, 80 - i * 2, 4); } ctx.restore();
    // lighthouse
    ctx.fillStyle = '#18191d'; ctx.beginPath(); ctx.moveTo(1640, 700); ctx.lineTo(1660, 430); ctx.lineTo(1720, 430); ctx.lineTo(1740, 700); ctx.fill(); ctx.fillRect(1650, 410, 80, 24);
    const fl = 0.85 + 0.15 * Math.sin(t * 8) * Math.sin(t * 3);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, 1690, 395, 260, '#f0a040', 0.5 * fl); ctx.restore(); ctx.fillStyle = '#ffc870'; L.ellipse(ctx, 1690, 395, 14, 20 * fl); ctx.fill();
    // ship approaching from left
    const sp = easeOut(prog(t, 0, cityAt + 1));
    const lx = L.cog(ctx, lerp(200, 980, sp), lerp(800, 870, sp), lerp(0.45, 0.85, sp), 1, t, { ph: 0.5, hull: '#2a2018', sail: '#6a665e', stripe: '#3a1a16' });
    ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, lx.lx, lx.ly, 140, '#f0b060', 0.5); ctx.restore();
    L.drawWrap(ctx, A.fog, t * 30, 820, 0.8, 0.35);
    ctx.restore();
    label(ctx, t, 0.5, cityAt + 0.6, lang === 'ru' ? '1347 · МЕССИНА' : '1347 · MESSINA', lang === 'ru' ? 'Сицилия, Средиземноморье' : 'Sicily, the Mediterranean');
  }
  if (t > cityAt && t < docAt + 0.8) {
    const a = prog(t, cityAt, cityAt + 0.8), lt = t - cityAt, dd = docAt - cityAt;
    ctx.save(); ctx.globalAlpha = a;
    ctx.drawImage(A.dusk.sky, 0, -380);
    const z = lerp(1.0, 1.08, lt / dd); camZoom(ctx, z);
    ctx.drawImage(A.dusk.far.c, -200 - lt * 4, -120);
    ctx.drawImage(A.dusk.mid.c, -300 - lt * 8, -150);
    ctx.save(); ctx.translate(-400 - lt * 22, -420);
    ctx.drawImage(A.market.c, 0, 0);
    // residents peeking from windows
    A.market.lights.slice(0, 40).forEach((w, i) => {
      if (i % 4 !== 1 || w.w < 30) return;
      ctx.save(); ctx.beginPath(); ctx.rect(w.x, w.y, w.w, w.h); ctx.clip();
      ctx.fillStyle = '#d0a060'; ctx.fillRect(w.x, w.y, w.w, w.h);
      L.person(ctx, w.x + w.w / 2, w.y + w.h + 150 * 0.35, 0.35, { dir: 0, hair: i % 3 ? 'short' : null, veil: i % 3 ? null : '#7a7266', tunic: '#3a3028', brows: 'worried', look: Math.sin(lt + i) }, lt + i);
      ctx.restore();
    });
    L.windowLights(ctx, A.market.lights.filter((w, i) => !(i % 4 === 1 && w.w >= 30 && i < 40)), lt);
    // physician w/ lantern walking right, woman w/ child hurrying left
    const base = A.market.base, px = 700 + lt * 70;
    const lan = L.person(ctx, px, base + 200, 0.8, { dir: 1, walk: lt * 4, tunic: '#3a2622', robe: true, hood: '#2a1c18', mask: '#9a8c74', lantern: true, brows: 'worried', armFront: -0.75 }, lt);
    const wx = 2200 - lt * 120;
    L.person(ctx, wx, base + 150, 0.66, { dir: -1, walk: lt * 7, dress: true, tunic: '#3a3a44', veil: '#6a645a', brows: 'worried' }, lt);
    L.person(ctx, wx + 70, base + 150, 0.42, { dir: -1, walk: lt * 7 + 1, tunic: '#5a4030', hair: 'short', brows: 'worried' }, lt);
    if (lan) { ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, lan.lx, lan.ly, 300, '#f0b060', 0.35); ctx.restore(); beam(ctx, lan.lx, lan.ly, lan.lx + 520, lan.ly + 220, lan.lx + 280, lan.ly + 330, '#f0c070', 0.16); }
    ctx.restore();
    L.drawWrap(ctx, A.fog, lt * 30, 760, 1.1, 0.5);
    ctx.restore();
    label(ctx, lt, 0.4, dd + 0.6, lang === 'ru' ? '1348 · ЕВРОПА' : '1348 · EUROPE', lang === 'ru' ? 'Рынки закрываются, улицы пустеют' : 'Markets close, streets empty');
  }
  if (t > docAt) {
    const a = prog(t, docAt, docAt + 0.8), lt = t - docAt;
    ctx.save(); ctx.globalAlpha = a; ctx.drawImage(A.wall, 0, 0);
    camZoom(ctx, lerp(1.0, 1.12, lt / (D - docAt)), 900, 560);
    // desk
    ctx.fillStyle = '#2e2218'; ctx.fillRect(0, 760, W, 330); ctx.fillStyle = '#3a2b1f'; ctx.fillRect(0, 750, W, 20);
    // books, mortar, herbs, flasks
    [['#4a2a22', 140, 90], ['#2a3a3a', 150, 70], ['#5a4a2a', 130, 60]].forEach(([bc, bw, bh], i) => { ctx.fillStyle = bc; ctx.fillRect(1300, 750 - (i + 1) * 46, bw + i * 10, 42); ctx.fillStyle = 'rgba(220,200,160,0.25)'; ctx.fillRect(1300, 750 - (i + 1) * 46 + 4, 8, 34); });
    ctx.fillStyle = '#4a4440'; ctx.beginPath(); ctx.moveTo(1560, 750); ctx.lineTo(1540, 690); ctx.lineTo(1660, 690); ctx.lineTo(1640, 750); ctx.fill(); ctx.strokeStyle = '#2a2420'; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(1600, 700); ctx.lineTo(1660, 620); ctx.stroke();
    for (let i = 0; i < 3; i++) { ctx.fillStyle = ['#3a4a3a', '#4a3a2a', '#3a3a4a'][i]; L.ellipse(ctx, 1760 + i * 60, 720, 22, 28); ctx.fill(); ctx.fillRect(1752 + i * 60, 680, 16, 20); }
    for (let i = 0; i < 5; i++) { const hx = 1150 + i * 140; ctx.strokeStyle = '#2a3220'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(hx, 150); ctx.lineTo(hx, 200 + Math.sin(lt + i) * 3); ctx.stroke(); ctx.fillStyle = '#2f3524'; L.ellipse(ctx, hx, 240, 24, 46); ctx.fill(); }
    // parchment w/ notes
    ctx.fillStyle = '#8a7a5a'; ctx.save(); ctx.translate(500, 800); ctx.rotate(-0.05); ctx.fillRect(0, 0, 360, 120); ctx.strokeStyle = 'rgba(40,30,20,0.6)'; ctx.lineWidth = 3; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(30, 22 + i * 20); ctx.lineTo(320 - (i % 2) * 60, 22 + i * 20); ctx.stroke(); } ctx.restore();
    candle(ctx, 1150, 750, 1.2, t, 1);
    // physician seated (draw body cut by desk) holding up a flask
    const raise = easeS(prog(lt, 0.3, 1.6)) * (1 - easeS(prog(lt, D - docAt - 1.6, D - docAt - 0.6)) * 0.6);
    L.person(ctx, 760, 1220, 1.9, { dir: 1, tunic: '#4a2a24', robe: true, hood: '#2e1e1a', brows: 'worried', look: 1 - raise * 0.5, armFront: lerp(-0.9, -2.3, raise), mouth: lt > (D - docAt) * 0.6 ? 'frown' : null }, t);
    // flask in hand
    const ang = lerp(-0.9, -2.3, raise), hx = 760 + Math.sin(-ang) * 110 * 1.9 + 0, hy = 1220 + (-268 + Math.cos(ang) * 110) * 1.9;
    ctx.fillStyle = 'rgba(200,190,120,0.55)'; L.ellipse(ctx, hx + 18, hy - 30, 34, 40); ctx.fill(); ctx.strokeStyle = 'rgba(230,220,190,0.7)'; ctx.lineWidth = 3; ctx.stroke(); ctx.fillStyle = 'rgba(200,190,120,0.55)'; ctx.fillRect(hx + 8, hy - 92, 20, 34);
    ctx.fillStyle = '#2e2218'; ctx.fillRect(0, 790, 980, 300);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, 1150, 660, 1000, '#c07a3a', 0.22); ctx.restore();
    const g = ctx.createRadialGradient(1000, 560, 250, 1000, 560, 1250); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.8)'); ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    ctx.restore();
  }
}

function shotToll(ctx, t, D, ev, lang) {
  const u = prog(t, 0.2, D - 0.6);
  const [mx, my] = M.proj(14, 48);
  const cam = { x: mx + lerp(-80, 120, u), y: my, z: lerp(1.0, 0.86, easeS(u)) };
  const seeds = [['messina', 0, 340], ['const', 0, 300], ['alex', 0.05, 260], ['marseille', 0.12, 380], ['genoa', 0.12, 320], ['venice', 0.15, 340], ['florence', 0.2, 260], ['paris', 0.38, 440], ['london', 0.55, 380], ['bergen', 0.75, 340], ['novgorod', 0.88, 420], ['baghdad', 0.2, 300]];
  M.drawMap(ctx, cam, t, {
    lang, overlay: (c, iz) => {
      c.save(); c.clip(M.landPath);
      for (const [k, at, R] of seeds) {
        const f = easeOut(prog(u, at, at + 0.45)); if (f <= 0) continue;
        const [x, y] = M.P(k), rr = R * f * 1.25;
        const g = c.createRadialGradient(x, y, 0, x, y, rr); g.addColorStop(0, 'rgba(24,8,6,0.78)'); g.addColorStop(0.7, 'rgba(60,10,6,0.55)'); g.addColorStop(1, 'rgba(110,20,10,0)');
        c.fillStyle = g; c.fillRect(x - rr, y - rr, rr * 2, rr * 2);
      }
      c.restore();
      ['messina', 'genoa', 'venice', 'marseille', 'paris', 'london', 'const', 'florence'].forEach((k, i) => M.cityDot(c, k, iz, lang, prog(u, i * 0.06, i * 0.06 + 0.1), { red: true, fs: 24 }));
    }
  });
  // year counter
  const yr = 1347 + Math.min(4, Math.floor(u * 4.6));
  ctx.save(); textC(ctx, String(yr), 110, 120, '84px OswaldBold', '#ece2cf', 4, 'left'); ctx.restore();
  ctx.fillStyle = '#b2453a'; ctx.fillRect(110, 175, 180 * Math.min(1, u * 1.15), 5);
  // stats
  const sa = prog(t, 1.6, 2.4);
  if (sa > 0) {
    ctx.save(); ctx.globalAlpha = sa; ctx.fillStyle = 'rgba(14,10,8,0.72)'; L.rrect(ctx, 1290, 90, 540, 300, 12); ctx.fill();
    ctx.fillStyle = '#b2453a'; ctx.fillRect(1290, 90, 8, 300);
    textC(ctx, lang === 'ru' ? '25–50 МЛН' : '25–50 MILLION', 1330, 175, '78px OswaldBold', '#ece2cf', 2, 'left');
    textC(ctx, lang === 'ru' ? 'погибших только в Европе' : 'dead in Europe alone', 1332, 245, '32px PTSans', 'rgba(236,226,207,0.8)', 1, 'left');
    ctx.globalAlpha = sa * prog(t, 3.0, 3.8);
    textC(ctx, lang === 'ru' ? '≈ 30–50 % населения' : '≈ 30–50% of the population', 1332, 320, '34px PTSansBold', '#d06a5a', 1, 'left');
    ctx.restore();
  }
}

function shotAfter(ctx, t, D, ev, lang) {
  const z = lerp(1.04, 1.12, easeS(t / D)), pan = t * 18;
  const dawn = easeS(prog(t, D - 5, D + 1));
  ctx.save(); camZoom(ctx, z);
  ctx.drawImage(A.dusk.sky, 0, -380); ctx.save(); ctx.globalAlpha = dawn; ctx.drawImage(A.dawn.sky, 0, -380); ctx.restore();
  L.drawWrap(ctx, A.clouds, t * 18, -200, 1, 0.8);
  ctx.drawImage(A.emptyFar.c, -200 - pan * 0.2, -120);
  ctx.drawImage(A.emptyMid.c, -300 - pan * 0.4, -150);
  L.drawWrap(ctx, A.fogDark, t * 14, 260, 1, 0.5);
  ctx.save(); ctx.translate(-500 - pan, -420);
  ctx.drawImage(A.empty.c, 0, 0);
  L.windowLights(ctx, A.empty.lights, t);
  const base = A.empty.base;
  // swinging broken shutter
  const sw = Math.sin(t * 1.8) * 0.25 + 0.15; ctx.save(); ctx.translate(1430, base - 250); ctx.rotate(sw); ctx.fillStyle = '#2a2018'; ctx.fillRect(0, 0, 18, 80); ctx.restore();
  // abandoned cart with broken wheel
  ctx.save(); ctx.translate(1180, base + 190); ctx.rotate(0.12); cart(ctx, 0, 0, 0.75, 0.4); ctx.restore();
  // crows on ridge + ground
  crow(ctx, 1640, base + 160, 1.1, t, 0); crow(ctx, 1760, base + 175, 0.95, t, 2, -1);
  ctx.restore();
  // crows on rooftops in mid layer
  [[520, 465], [880, 380]].forEach(([cx, cy], i) => crow(ctx, cx - pan * 0.4 - 300 + 300, cy, 0.8, t, i * 3));
  // wind-blown leaves/dust
  const r = rng(77); for (let i = 0; i < 40; i++) { const sp = 200 + r() * 300, x = W + 100 - ((t * sp + r() * 2400) % (W + 300)), y = 600 + r() * 420 + Math.sin(t * 3 + i) * 20; ctx.fillStyle = r() < 0.5 ? '#3a3024' : '#4a3a28'; ctx.save(); ctx.translate(x, y); ctx.rotate(t * 4 + i); ctx.fillRect(-6, -2, 12, 4); ctx.restore(); }
  L.drawWrap(ctx, A.fog, t * 40, 650, 1.2, 0.55);
  // dawn light
  if (dawn > 0) { beam(ctx, 1500, -100, 600, 1100, 1100, 1100, '#e0a060', 0.18 * dawn); beam(ctx, 1700, -100, 1200, 1100, 1600, 1100, '#e0a060', 0.12 * dawn); }
  ctx.restore();
}

function shotFinal(ctx, t, D, ev, lang) {
  const titleAt = ev.title, endAt = ev.black;
  const c = 1 - easeS(prog(t, 0, titleAt + 0.6));
  if (t < endAt + 0.2) {
    cityView(ctx, t + 40, c, lerp(1.0, 1.1, easeS(t / D)), (t + 20) * 10, 'dawn', { birds: t * 40 + 300 });
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.6; beam(ctx, 760, 800, -200, -200, 500, -200, '#e0a060', 0.12); ctx.restore();
    // title
    const ta = prog(t, titleAt, titleAt + 1.2) * (1 - prog(t, endAt - 0.6, endAt));
    if (ta > 0) {
      ctx.save(); ctx.fillStyle = `rgba(8,6,5,${0.45 * ta})`; ctx.fillRect(0, 0, W, H);
      ctx.globalAlpha = ta; const sp = lerp(48, 22, easeOut(prog(t, titleAt, titleAt + 2.5)));
      textC(ctx, lang === 'ru' ? '1346 — 1353' : '1346 — 1353', W / 2, 360, '36px OswaldMed', 'rgba(236,226,207,0.8)', 12);
      ctx.shadowColor = 'rgba(0,0,0,0.8)'; ctx.shadowBlur = 30;
      textC(ctx, lang === 'ru' ? 'ЧЁРНАЯ СМЕРТЬ' : 'THE BLACK DEATH', W / 2, 520, '190px OswaldBold', '#efe4cf', sp);
      ctx.shadowBlur = 0; const lw = 520 * easeOut(prog(t, titleAt + 0.4, titleAt + 1.8));
      ctx.fillStyle = '#b2453a'; ctx.fillRect(W / 2 - lw / 2, 652, lw, 6);
      ctx.restore();
    }
  }
  const bk = prog(t, endAt - 0.6, endAt);
  if (bk > 0) { ctx.fillStyle = `rgba(0,0,0,${bk})`; ctx.fillRect(0, 0, W, H); }
  const fa = prog(t, endAt + 0.4, endAt + 1.4) * (1 - prog(t, D - 1.1, D - 0.2));
  if (fa > 0) { ctx.save(); ctx.globalAlpha = fa; textC(ctx, lang === 'ru' ? 'Эпидемия, изменившая историю человечества' : 'The pandemic that changed human history', W / 2, H / 2, '58px PTSerifBold', '#e6dac4', 2); ctx.restore(); }
}

module.exports = { build, shots: { city: shotCity, window: shotWindow, asia: shotAsia, trade: shotTrade, europe: shotEurope, toll: shotToll, after: shotAfter, final: shotFinal }, get A() { return A; }, stall, crow, cart, candle, seaBand, label };
