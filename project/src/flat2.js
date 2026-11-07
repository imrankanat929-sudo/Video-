// Episode 02 — "What if water disappeared": extra flat scenes (vertical 9:16).
'use strict';

const WP = { water: '#3fa9f5', water2: '#8fd3ff', mud: '#7a5a3c', mud2: '#5e4630', sand: '#c9a26b', sand2: '#a8834f', grass: '#2f5a4a', grass2: '#24483b', metal: '#7d8796', metal2: '#5a6372', sky1: '#6f8fc4', sky2: '#f2b88a' };

function mix(c1, c2, k) {
  const a = parseInt(c1.slice(1), 16), b = parseInt(c2.slice(1), 16);
  const r = Math.round(lerp(a >> 16, b >> 16, k)), g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, k)), bl = Math.round(lerp(a & 255, b & 255, k));
  return `rgb(${r},${g},${bl})`;
}
function morningSky(ctx, y0 = -400, y1 = 900) {
  const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, WP.sky1); g.addColorStop(1, WP.sky2);
  ctx.fillStyle = g; ctx.fillRect(-500, y0, W + 1000, y1 - y0);
}
function cracks(ctx, x, y, w, h, seed = 1, col = WP.mud2) {
  const r = mulberry32(seed); ctx.strokeStyle = col; ctx.lineWidth = 4; ctx.lineCap = 'round';
  for (let i = 0; i < Math.floor(w * h / 9000); i++) {
    let px = x + r() * w, py = y + r() * h; ctx.beginPath(); ctx.moveTo(px, py);
    for (let k = 0; k < 3; k++) { px += (r() - 0.5) * 80; py += (r() - 0.5) * 30; ctx.lineTo(px, py); }
    ctx.stroke();
  }
}
function person(ctx, x, y, s, col, o = {}) {      // tiny flat bystander
  ctx.save(); ctx.translate(x, y); ctx.scale(s * (o.flip ? -1 : 1), s);
  const step = o.walk ? Math.sin(o.walk) * 14 : 0;
  ctx.fillStyle = '#20263a'; rr(ctx, -18 + step, 40, 16, 70, 8); ctx.fill(); rr(ctx, 2 - step, 40, 16, 70, 8); ctx.fill();
  ctx.fillStyle = col; rr(ctx, -28, -50, 56, 100, 20); ctx.fill();
  circ(ctx, 0, -78, 26, o.skin || FP.skin);
  ctx.fillStyle = o.hair || '#2a1d14'; ctx.beginPath(); ctx.arc(0, -84, 27, Math.PI, 0); ctx.fill();
  if (o.phone) { ctx.fillStyle = '#111'; rr(ctx, 18, -70, 16, 28, 4); ctx.fill(); ctx.fillStyle = FP.skin; circ(ctx, 26, -40, 9, FP.skin); if (o.flash) glow(ctx, 26, -60, 90, 'rgba(255,255,255,0.9)', o.flash); }
  if (o.bottle) { ctx.fillStyle = WP.water; rr(ctx, -46, -30, 22, 50, 6); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillRect(-40, -38, 10, 8); }
  ctx.restore();
}
// side bust reaching forward (holding a glass). (x,y)=head centre
function heroReach(ctx, T, x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = FP.hood; ctx.beginPath(); ctx.moveTo(-240, 900); ctx.quadraticCurveTo(-230, 200, -60, 150); ctx.lineTo(70, 150); ctx.quadraticCurveTo(210, 220, 200, 900); ctx.closePath(); ctx.fill();
  ctx.fillStyle = FP.hood2; ctx.beginPath(); ctx.ellipse(-80, 150, 110, 60, -0.3, 0, 7); ctx.fill();
  ctx.save(); ctx.scale(1.6, 1.6); headSide(ctx, T, o.expr, o); ctx.restore();
  const ax = o.ax ?? 420, ay = o.ay ?? 330;
  ctx.strokeStyle = FP.hood3; ctx.lineWidth = 70; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(40, 260); ctx.quadraticCurveTo(ax * 0.5, ay + 60, ax - 40, ay); ctx.stroke();
  circ(ctx, ax - 10, ay, 36, FP.skin);
  ctx.restore();
}
function glass(ctx, x, y, s, level = 0, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (level > 0) {
    ctx.save(); ctx.beginPath(); ctx.moveTo(-60, -110); ctx.lineTo(60, -110); ctx.lineTo(48, 100); ctx.lineTo(-48, 100); ctx.closePath(); ctx.clip();
    const top = lerp(100, -90, level);
    ctx.fillStyle = WP.water; ctx.beginPath(); ctx.moveTo(-80, top + Math.sin(t * 4) * 5);
    for (let i = -80; i <= 80; i += 10) ctx.lineTo(i, top + Math.sin(t * 4 + i * 0.05) * 5);
    ctx.lineTo(80, 120); ctx.lineTo(-80, 120); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(-36, top + 10, 12, 120);
    ctx.restore();
  }
  ctx.strokeStyle = 'rgba(220,240,255,0.95)'; ctx.lineWidth = 8; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.moveTo(-60, -110); ctx.lineTo(-48, 100); ctx.lineTo(48, 100); ctx.lineTo(60, -110); ctx.stroke();
  ctx.fillStyle = 'rgba(200,230,255,0.12)'; ctx.fill();
  ctx.restore();
}
function tapShape(ctx, x, y, s, handleRot = 0, col = '#c9d2de') {   // (x,y) = base on the counter
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = col; rr(ctx, -26, -260, 52, 260, 18); ctx.fill();                       // pipe
  ctx.beginPath(); ctx.moveTo(-26, -240); ctx.quadraticCurveTo(-20, -330, 90, -320); ctx.lineTo(160, -320); ctx.lineTo(160, -270); ctx.lineTo(100, -272); ctx.quadraticCurveTo(26, -276, 26, -230); ctx.closePath(); ctx.fill();   // spout
  ctx.fillStyle = '#9aa6b6'; rr(ctx, 120, -290, 44, 30, 8); ctx.fill();
  ctx.save(); ctx.translate(0, -300); ctx.rotate(handleRot);
  ctx.fillStyle = FP.red; rr(ctx, -16, -150, 32, 150, 14); ctx.fill(); circ(ctx, 0, -150, 26, FP.red);
  ctx.restore();
  circ(ctx, 0, -300, 34, '#aeb8c6');
  ctx.restore();
}
function thoughtBubble(ctx, T, x, y, r, kind, p = 1) {
  if (p <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(p, p);
  circ(ctx, -r * 0.9, r * 1.1, r * 0.14, '#fff'); circ(ctx, -r * 0.6, r * 0.8, r * 0.22, '#fff');
  ctx.fillStyle = '#fff'; ctx.beginPath();
  for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; ctx.moveTo(Math.cos(a) * r * 0.7 + r * 0.32, Math.sin(a) * r * 0.5); ctx.arc(Math.cos(a) * r * 0.7, Math.sin(a) * r * 0.5, r * 0.36, 0, 7); }
  ctx.fill(); ell(ctx, 0, 0, r * 0.85, r * 0.62, '#fff');
  if (kind === 'glass') glass(ctx, 0, 6, r / 260, 0.75, T);
  else if (kind === 'dam') { ctx.fillStyle = '#8a95a8'; ctx.fillRect(-r * 0.5, -r * 0.25, r, r * 0.5); ctx.strokeStyle = FP.red; ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(-r * 0.1, -r * 0.25); ctx.lineTo(r * 0.05, 0); ctx.lineTo(-r * 0.05, r * 0.25); ctx.stroke(); }
  else ftext(ctx, kind || '?', 0, r * 0.25, r * 0.7, FP.red, { stroke: false });
  ctx.restore();
}

// ---------- scenes ----------
Object.assign(FLAT, {
  f_kitchen(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const open = sh.openAt !== undefined ? so(T, sh.openAt, sh.openAt + 0.4) : 0;
    fcam(ctx, cam, 0.8, () => {
      ctx.fillStyle = '#2b3a63'; ctx.fillRect(-500, -500, W + 1000, H + 1000);
      ctx.strokeStyle = 'rgba(255,255,255,0.06)'; ctx.lineWidth = 4;
      for (let y = 300; y < 1100; y += 90) { ctx.beginPath(); ctx.moveTo(-500, y); ctx.lineTo(W + 500, y); ctx.stroke(); }
      for (let x = -500; x < W + 500; x += 90) { ctx.beginPath(); ctx.moveTo(x, 300); ctx.lineTo(x, 1100); ctx.stroke(); }
      flatWindow(ctx, T, 620, 330, 360, 400, { morning: true });
      ctx.fillStyle = '#3d4b7d'; rr(ctx, 40, 320, 300, 200, 12); ctx.fill(); ctx.fillStyle = '#33406b'; ctx.fillRect(186, 320, 6, 200);
    });
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = '#46557f'; ctx.fillRect(-500, 1100, W + 1000, 50);
      ctx.fillStyle = '#26304f'; ctx.fillRect(-500, 1150, W + 1000, 900);
      ctx.fillStyle = '#1f2843'; for (let x = -100; x < W + 200; x += 260) rr(ctx, x, 1190, 230, 300, 14), ctx.fill();
      ctx.fillStyle = '#9aa6b6'; rr(ctx, 380, 1080, 420, 40, 14); ctx.fill();         // sink rim
      tapShape(ctx, 560, 1090, 0.9, -open * 1.2);
      if (sh.nothingAt !== undefined && T > sh.nothingAt) {
        const q = ease.outBack(ramp(T, sh.nothingAt, sh.nothingAt + 0.3));
        ftext(ctx, '?', 760, 700, 170 * q, FP.red);
        for (let i = 0; i < 4; i++) { const k = ((T - sh.nothingAt) * 0.8 + i * 0.25) % 1; circ(ctx, 700 + Math.sin(i * 3) * 20, 820 + k * 120, 8 * (1 - k), 'rgba(220,230,240,0.5)'); }
      }
      glass(ctx, 705, 930, 0.7, 0, T);
      heroReach(ctx, T, 230, 760, 0.95, { expr: sh.nothingAt !== undefined && T > sh.nothingAt ? 'skeptic' : 'neutral', ax: 520, ay: 200, lookX: 1 });
    });
  },

  f_tap(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => fbg(ctx, '#22305a', 'rgba(140,190,255,0.25)'));
    const hard = sh.hardAt !== undefined ? ramp(T, sh.hardAt, sh.hardAt + 0.3) : 0;
    const rot = -0.4 - Math.abs(Math.sin((T - sh.start) * (2 + hard * 6))) * (0.6 + hard * 0.9);
    const sk = hard ? shake(T, 6 * hard, 30, 2) : { x: 0, y: 0 };
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = '#9aa6b6'; ctx.fillRect(-500, 1220, W + 1000, 60);
      tapShape(ctx, 420 + sk.x, 1230 + sk.y, 2.1, rot);
      // hand on the handle
      ctx.save(); ctx.translate(420 + sk.x, 1230 - 630 + sk.y); ctx.rotate(rot); circ(ctx, 0, -300, 64, FP.skin); ctx.restore();
      if (sh.xAt !== undefined) redX(ctx, 820, 640, 110, ramp(T, sh.xAt, sh.xAt + 0.35), 26);
      if (hard) for (let i = 0; i < 3; i++) { ctx.strokeStyle = FP.yellow; ctx.lineWidth = 10; ctx.beginPath(); ctx.arc(420, 600, 300 + i * 40, -1.9 - i * 0.1, -1.3 - i * 0.1); ctx.stroke(); }
    });
  },

  f_bath(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const tap = sh.tapAt !== undefined ? so(T, sh.tapAt, sh.tapAt + 0.4) : 0, sho = sh.showerAt !== undefined ? so(T, sh.showerAt, sh.showerAt + 0.4) : 0;
    fcam(ctx, cam, 0.85, () => {
      ctx.fillStyle = '#d7e3ef'; ctx.fillRect(-500, -500, W + 1000, H + 1000);
      ctx.strokeStyle = '#b8c7d8'; ctx.lineWidth = 4;
      for (let y = -500; y < H; y += 80) { ctx.beginPath(); ctx.moveTo(-500, y); ctx.lineTo(W + 500, y); ctx.stroke(); }
      for (let x = -500; x < W + 500; x += 80) { ctx.beginPath(); ctx.moveTo(x, -500); ctx.lineTo(x, H); ctx.stroke(); }
      // mirror
      ctx.fillStyle = '#9fb7cf'; rr(ctx, 120, 330, 360, 420, 30); ctx.fill(); ctx.fillStyle = 'rgba(255,255,255,0.4)'; ctx.fillRect(170, 360, 30, 300);
    });
    fcam(ctx, cam, 1, () => {
      // sink
      ctx.fillStyle = '#ffffff'; rr(ctx, 100, 880, 400, 110, 40); ctx.fill(); ctx.fillStyle = '#cfd9e4'; ctx.fillRect(250, 990, 100, 300);
      tapShape(ctx, 290, 890, 0.55, -tap * 1.2);
      // shower
      ctx.fillStyle = '#9aa6b6'; ctx.fillRect(840, 300, 26, 900); rr(ctx, 700, 300, 170, 26, 12); ctx.fill();
      ctx.save(); ctx.translate(700, 340); ctx.rotate(sho ? Math.sin(T * 30) * 0.05 * (1 - ramp(T, sh.showerAt + 0.6, sh.showerAt + 1.2)) : 0);
      ctx.fillStyle = '#c9d2de'; ctx.beginPath(); ctx.ellipse(0, 0, 90, 40, 0, Math.PI, 0); ctx.fill(); ctx.fillStyle = '#7d8796'; ctx.fillRect(-90, 0, 180, 10); ctx.restore();
      ctx.fillStyle = 'rgba(61,123,255,0.5)'; ctx.fillRect(600, 300, 14, 1000);
      ctx.fillStyle = 'rgba(160,200,255,0.35)'; ctx.beginPath(); ctx.moveTo(614, 300); ctx.quadraticCurveTo(660, 800, 614, 1300); ctx.lineTo(560, 1300); ctx.quadraticCurveTo(600, 800, 560, 300); ctx.fill();
      ctx.fillStyle = '#e7edf4'; ctx.fillRect(560, 1240, 520, 90);
      if (sh.showerAt !== undefined && T > sh.showerAt + 0.5) ftext(ctx, '?', 760, 560, 150 * ease.outBack(ramp(T, sh.showerAt + 0.5, sh.showerAt + 0.8)), FP.red);
      if (sh.xAt !== undefined) { redX(ctx, 360, 860, 80, ramp(T, sh.xAt, sh.xAt + 0.3), 20); redX(ctx, 700, 420, 90, ramp(T, sh.xAt + 0.15, sh.xAt + 0.45), 20); }
    });
    heroFace(ctx, T, 220, 1880 - 260, 0.62, sh.xAt !== undefined && T > sh.xAt ? 'shock' : 'worry', { lookX: 0.7, lookY: -0.6 });
    if (sh.caption && T > sh.caption.at) tagBox(ctx, sh.caption.text, 540, 1180, FP.red, { size: 58, rot: -0.05, scale: ease.outBack(ramp(T, sh.caption.at, sh.caption.at + 0.3)) });
  },

  f_river(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const dry = sh.dry === true ? 1 : sh.dryAt !== undefined ? sm(T, sh.dryAt, sh.dryAt + 1.6) : 0;
    fcam(ctx, cam, 0.6, () => {
      morningSky(ctx, -400, 860);
      circ(ctx, 820, 420, 70, '#ffe2a6');
      const r = mulberry32(21); let bx = -300;
      while (bx < W + 300) { const bw = 80 + r() * 100, bh = 120 + r() * 220; ctx.fillStyle = '#4a5a80'; ctx.fillRect(bx, 860 - bh, bw, bh); bx += bw + 10; }
    });
    fcam(ctx, cam, 0.85, () => {
      ctx.fillStyle = WP.grass; ctx.fillRect(-500, 820, W + 1000, 80);
      for (let x = -400; x < W + 400; x += 140) { circ(ctx, x, 800, 50, '#2a4f42'); ctx.fillStyle = '#3b2a1f'; ctx.fillRect(x - 6, 820, 12, 40); }
    });
    fcam(ctx, cam, 1, () => {
      // river bed
      ctx.fillStyle = WP.mud; ctx.fillRect(-500, 900, W + 1000, 320);
      cracks(ctx, -400, 920, W + 800, 280, 4);
      if (dry < 1) {
        const top = lerp(900, 1120, dry), a = 1 - dry * 0.9;
        ctx.fillStyle = `rgba(63,169,245,${a})`; ctx.fillRect(-500, top, W + 1000, 1220 - top - dry * 60);
        ctx.strokeStyle = `rgba(200,235,255,${0.8 * a})`; ctx.lineWidth = 6;
        for (let i = 0; i < 14; i++) { const wx = ((i * 170 + T * 90) % (W + 400)) - 200, wy = top + 30 + (i % 4) * 60; ctx.beginPath(); ctx.moveTo(wx, wy); ctx.quadraticCurveTo(wx + 30, wy - 12, wx + 60, wy); ctx.stroke(); }
      }
      // boats: float, then lie tilted on the mud
      const boats = [[220, 1000, '#e8343f'], [760, 1080, '#ffd23f']];
      if (sh.boatsAt !== undefined || sh.dry) boats.forEach(([bx0, by, col], i) => {
        const p = sh.dry ? 1 : ease.outBack(ramp(T, sh.boatsAt + i * 0.2, sh.boatsAt + i * 0.2 + 0.4)); if (p <= 0) return;
        const x = bx0 + (1 - dry) * Math.sin(T * 0.4 + i) * 40, y = by + dry * 50 + (1 - dry) * Math.sin(T * 2 + i) * 6;
        ctx.save(); ctx.translate(x, y); ctx.rotate(dry * (i ? 0.35 : -0.3)); ctx.scale(p, p);
        ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(-110, -20); ctx.lineTo(110, -20); ctx.lineTo(80, 30); ctx.lineTo(-80, 30); ctx.fill();
        ctx.fillStyle = '#fff'; ctx.fillRect(-10, -120, 8, 100); ctx.beginPath(); ctx.moveTo(-2, -120); ctx.lineTo(70, -40); ctx.lineTo(-2, -40); ctx.fill();
        ctx.restore();
      });
      // near bank + walkers / crowd
      ctx.fillStyle = WP.grass2; ctx.fillRect(-500, 1220, W + 1000, 900);
      ctx.fillStyle = '#5a6372'; ctx.fillRect(-500, 1220, W + 1000, 14);
      if (sh.peopleAt !== undefined && T > sh.peopleAt) {
        const a = so(T, sh.peopleAt, sh.peopleAt + 0.4);
        ctx.globalAlpha = a;
        [['#3d7bff', 0], ['#35c46a', 1], ['#ffd23f', 2]].forEach(([c, i]) => person(ctx, ((T * 50 + i * 360) % (W + 200)) - 100, 1290 + i * 6, 0.9, c, { walk: T * 8 + i }));
        ctx.globalAlpha = 1;
      }
      if (sh.crowd) {
        const r = mulberry32(9);
        for (let i = 0; i < 9; i++) {
          const x = 80 + i * 115 + r() * 30, y = 1060 + r() * 120, ph = sh.flash !== undefined && (Math.floor((T + i * 0.37) * 1.3) % 4 === 0) && T > sh.flash;
          person(ctx, x, y, 0.75 + r() * 0.2, ['#3d7bff', '#e8343f', '#35c46a', '#ffd23f', '#a46bff'][i % 5], { phone: i % 2 === 0, flash: ph ? 0.9 : 0, flip: i % 3 === 0 });
        }
      }
    });
  },

  f_city(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.7, () => { morningSky(ctx, -400, 700); ctx.fillStyle = '#4a5a80'; for (let x = -300; x < W + 300; x += 130) ctx.fillRect(x, 500 - (x * 7 % 160), 110, 300); });
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = '#3e6b55'; ctx.fillRect(-500, 700, W + 1000, 1500);
      ctx.fillStyle = '#c8b48a'; ctx.beginPath(); ctx.moveTo(480, 700); ctx.lineTo(600, 700); ctx.lineTo(760, 1900); ctx.lineTo(320, 1900); ctx.fill();
      for (const [x, y] of [[90, 760], [990, 780], [120, 1250], [980, 1300]]) { circ(ctx, x, y, 70, '#2a4f42'); }
      // fountain
      const f = sh.fountainAt !== undefined ? ramp(T, sh.fountainAt, sh.fountainAt + 0.3) : 0;
      ctx.fillStyle = '#b8c2cf'; ctx.beginPath(); ctx.ellipse(280, 860, 170, 50, 0, 0, 7); ctx.fill(); ctx.fillStyle = WP.mud2; ctx.beginPath(); ctx.ellipse(280, 856, 140, 36, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#b8c2cf'; ctx.fillRect(266, 720, 28, 140); ctx.beginPath(); ctx.ellipse(280, 720, 60, 18, 0, 0, 7); ctx.fill();
      redX(ctx, 280, 790, 80, f, 18);
      // lake → empty pit
      const l = sh.lakeAt !== undefined ? sm(T, sh.lakeAt, sh.lakeAt + 1.0) : 0;
      ell(ctx, 780, 1010, 230, 90, WP.mud); cracks(ctx, 600, 960, 360, 100, 7);
      ell(ctx, 780, 1010, 230 * (1 - l), 90 * (1 - l), WP.water);
      if (sh.lakeAt !== undefined) redX(ctx, 780, 1010, 80, ramp(T, sh.lakeAt + 0.6, sh.lakeAt + 0.9), 18);
      // small ponds → holes
      [[200, 1150], [430, 1230], [860, 1210]].forEach(([x, y], i) => {
        const k = sh.holesAt !== undefined ? sm(T, sh.holesAt + i * 0.25, sh.holesAt + i * 0.25 + 0.6) : 0;
        ell(ctx, x, y, 90, 34, '#3a2a1c'); ell(ctx, x, y, 90 * (1 - k), 34 * (1 - k), WP.water);
      });
      // benches
      ctx.fillStyle = '#6b4a30'; rr(ctx, 520, 1120, 140, 20, 6); ctx.fill(); ctx.fillRect(530, 1140, 10, 30); ctx.fillRect(640, 1140, 10, 30);
    });
  },

  f_tv(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => { ctx.fillStyle = '#26304f'; ctx.fillRect(-500, -500, W + 1000, H + 1000); glow(ctx, 540, 720, 800, 'rgba(120,170,255,0.35)', 1); });
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = '#0a0f1c'; rr(ctx, 60, 400, 960, 600, 20); ctx.fill();
      ctx.save(); rr(ctx, 84, 424, 912, 552, 8); ctx.clip();
      ctx.fillStyle = '#183a6b'; ctx.fillRect(84, 424, 912, 552);
      // world map
      ctx.fillStyle = '#204d8a'; rr(ctx, 520, 450, 450, 300, 14); ctx.fill();
      const blobs = [[600, 540, 50, 34], [690, 520, 36, 50], [780, 560, 70, 40], [880, 620, 40, 30], [660, 650, 30, 40], [900, 520, 34, 24]];
      blobs.forEach(([x, y, rx, ry]) => ell(ctx, x, y, rx, ry, '#4caf7a'));
      if (sh.worldAt !== undefined) blobs.forEach(([x, y], i) => { const k = ramp(T, sh.worldAt + i * 0.2, sh.worldAt + i * 0.2 + 0.3); if (k > 0) { circ(ctx, x, y, 14 * ease.outBack(k), FP.red); ctx.strokeStyle = rgba(FP.red, (1 - ((T * 1.2 + i * 0.3) % 1)) * 0.8); ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(x, y, 14 + ((T * 1.2 + i * 0.3) % 1) * 40, 0, 7); ctx.stroke(); } });
      // anchor
      ctx.fillStyle = '#2c3550'; rr(ctx, 160, 760, 300, 260, 60); ctx.fill();
      ctx.fillStyle = '#f2f2f2'; ctx.beginPath(); ctx.moveTo(280, 760); ctx.lineTo(310, 840); ctx.lineTo(340, 760); ctx.fill();
      circ(ctx, 310, 650, 90, '#d9a27a');
      ctx.fillStyle = '#4a2f22'; ctx.beginPath(); ctx.arc(310, 640, 96, Math.PI * 1.02, Math.PI * 1.98); ctx.lineTo(400, 720); ctx.lineTo(380, 640); ctx.lineTo(240, 640); ctx.lineTo(220, 720); ctx.closePath(); ctx.fill();
      circ(ctx, 280, 660, 9, '#16161c'); circ(ctx, 340, 660, 9, '#16161c');
      ell(ctx, 310, 705, 18, 6 + Math.abs(Math.sin(T * 12)) * 8, '#5b1a1f');
      // banner + ticker
      ctx.fillStyle = FP.red; ctx.fillRect(84, 860, 912, 64);
      ftext(ctx, sh.banner || 'BREAKING NEWS', 110, 905, 40, '#fff', { align: 'left', stroke: false });
      ctx.fillStyle = '#0b0f1c'; ctx.fillRect(84, 924, 912, 52);
      ctx.save(); ctx.font = font(800, 30); ctx.fillStyle = FP.yellow; const tw = ctx.measureText(sh.ticker || '').width + 120;
      const off = ((T - sh.start) * 160) % tw; for (let k = 0; k < 3; k++) ctx.fillText(sh.ticker || '', 1000 - off + k * tw - tw, 962); ctx.restore();
      ctx.restore();
      ctx.fillStyle = '#0a0f1c'; ctx.fillRect(500, 1000, 80, 60); rr(ctx, 380, 1050, 320, 22, 10); ctx.fill();
    });
    if (sh.faceAt !== undefined) heroFace(ctx, T, 860, 1880 - 260 * ease.outBack(ramp(T, sh.faceAt, sh.faceAt + 0.35)), 0.62, sh.faceExpr || 'shock', { lookX: -0.7, lookY: -0.6 });
  },

  f_globe(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => fbg(ctx, '#0b1122', 'rgba(120,170,255,0.25)'));
    const items = sh.items || [];
    const done = items.filter(i => T > i.at).length, dry = items.length ? ramp(T, items[0].at, items[items.length - 1].at + 0.6) : 0;
    fcam(ctx, cam, 1, () => {
      const cx = 540, cy = 720, R = 320;
      ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.clip();
      ctx.fillStyle = mix('#2f8fe0', '#c9a26b', dry); ctx.fillRect(cx - R, cy - R, 2 * R, 2 * R);
      const off = ((T - sh.start) * 40) % 700;
      const land = [[-200, -120, 120, 90], [-40, 40, 90, 140], [160, -60, 150, 100], [320, 120, 90, 70], [480, -150, 110, 80], [620, 60, 130, 120]];
      for (const [x, y, rx, ry] of land) for (const k of [0, -700]) ell(ctx, cx + x - off - k - 200, cy + y, rx, ry, mix('#4caf7a', '#8a6a4a', dry));
      if (dry > 0.3) cracks(ctx, cx - R, cy - R, 2 * R, 2 * R, 3, `rgba(94,70,48,${dry})`);
      ctx.restore();
      ctx.strokeStyle = 'rgba(255,255,255,0.25)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.stroke();
      glow(ctx, cx, cy, R * 1.4, `rgba(80,160,255,${0.3 * (1 - dry)})`, 1);
      // labels with crosses
      items.forEach((it, i) => {
        const x = 300 + (i % 2) * 480, y = 1140 + Math.floor(i / 2) * 110, p = ease.outBack(ramp(T, it.at - 0.1, it.at + 0.2));
        if (p <= 0) return;
        tagBox(ctx, it.text, x, y, i === items.length - 1 ? FP.red : FP.blue, { size: 46, scale: p });
        redX(ctx, x, y, 44, ramp(T, it.at + 0.25, it.at + 0.5), 12);
      });
    });
  },

  f_seabed(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.6, () => { const g = ctx.createLinearGradient(0, -400, 0, 900); g.addColorStop(0, '#c98b5a'); g.addColorStop(1, '#f0d29a'); ctx.fillStyle = g; ctx.fillRect(-500, -400, W + 1000, 1400); circ(ctx, 300, 420, 80, '#fff1c9'); });
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = WP.sand; ctx.beginPath(); ctx.moveTo(-500, 860); ctx.quadraticCurveTo(540, 780, W + 500, 880); ctx.lineTo(W + 500, 2200); ctx.lineTo(-500, 2200); ctx.fill();
      ctx.strokeStyle = WP.sand2; ctx.lineWidth = 6; for (let y = 950; y < 1900; y += 70) { ctx.beginPath(); ctx.moveTo(-500, y); for (let x = -500; x < W + 500; x += 60) ctx.lineTo(x, y + Math.sin(x * 0.02 + y) * 10); ctx.stroke(); }
      // ship
      ctx.save(); ctx.translate(600, 900); ctx.rotate(0.16);
      ctx.fillStyle = '#2a3352'; ctx.beginPath(); ctx.moveTo(-420, -60); ctx.lineTo(380, -60); ctx.lineTo(460, -150); ctx.lineTo(420, 60); ctx.lineTo(-380, 60); ctx.closePath(); ctx.fill();
      ctx.fillStyle = FP.red; ctx.fillRect(-380, 20, 780, 40);
      ctx.fillStyle = '#f2f2f2'; ctx.fillRect(-300, -180, 260, 120); ctx.fillRect(-260, -260, 160, 80);
      ctx.fillStyle = '#1d2440'; for (let i = 0; i < 5; i++) ctx.fillRect(-285 + i * 48, -150, 28, 26);
      ctx.fillStyle = FP.yellow; ctx.fillRect(0, -130, 90, 70); ctx.fillStyle = '#3d7bff'; ctx.fillRect(100, -130, 90, 70); ctx.fillStyle = FP.green; ctx.fillRect(200, -130, 90, 70);
      ctx.restore();
      // fish flopping
      if (sh.fishAt !== undefined && T > sh.fishAt) [[250, 1180, '#ff8a3d'], [520, 1250, '#3d7bff'], [820, 1170, '#ffd23f']].forEach(([x, y, c], i) => {
        const p = ease.outBack(ramp(T, sh.fishAt + i * 0.2, sh.fishAt + i * 0.2 + 0.3)); const hop = Math.abs(Math.sin(T * 6 + i * 2)) * 40;
        ctx.save(); ctx.translate(x, y - hop); ctx.rotate(Math.sin(T * 6 + i * 2) * 0.5); ctx.scale(p, p);
        ell(ctx, 0, 0, 70, 36, c); ctx.fillStyle = c; ctx.beginPath(); ctx.moveTo(60, 0); ctx.lineTo(110, -34); ctx.lineTo(110, 34); ctx.fill();
        circ(ctx, -36, -8, 12, '#fff'); circ(ctx, -36, -6, 6, '#111');
        ctx.restore();
        ctx.fillStyle = '#7fd0ff'; ctx.beginPath(); ctx.moveTo(x - 40, y - 90 - hop); ctx.quadraticCurveTo(x - 24, y - 60 - hop, x - 40, y - 54 - hop); ctx.quadraticCurveTo(x - 56, y - 60 - hop, x - 40, y - 90 - hop); ctx.fill();
      });
      // seaweed drooping + starfish
      ctx.strokeStyle = '#4c7a3a'; ctx.lineWidth = 14; ctx.lineCap = 'round';
      for (const x of [120, 960]) { ctx.beginPath(); ctx.moveTo(x, 1320); ctx.quadraticCurveTo(x + 60, 1260, x + 120, 1320); ctx.stroke(); }
      ctx.fillStyle = '#e07a5f'; ctx.beginPath(); for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2 - Math.PI / 2, r = i % 2 ? 22 : 50; ctx.lineTo(900 + Math.cos(a) * r, 1300 + Math.sin(a) * r); } ctx.fill();
    });
  },

  f_store(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const left = sh.grabFrom !== undefined ? 1 - ramp(T, sh.grabFrom, sh.emptyAt) : 1;
    fcam(ctx, cam, 0.85, () => { ctx.fillStyle = '#e7ecf3'; ctx.fillRect(-500, -500, W + 1000, H + 1000); ctx.fillStyle = '#c9d2de'; ctx.fillRect(-500, 1250, W + 1000, 900); });
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = FP.red; ctx.fillRect(80, 330, 920, 80); ftext(ctx, sh.sign || 'WATER', 540, 390, 54, '#fff', { stroke: false });
      for (let row = 0; row < 3; row++) {
        const y = 560 + row * 230;
        ctx.fillStyle = '#9aa6b6'; ctx.fillRect(80, y + 120, 920, 22);
        for (let i = 0; i < 9; i++) {
          const idx = row * 9 + i; if (idx / 27 > left) continue;
          ctx.fillStyle = WP.water; rr(ctx, 110 + i * 100, y, 64, 120, 14); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillRect(130 + i * 100, y - 20, 24, 22); ctx.fillStyle = 'rgba(255,255,255,0.5)'; ctx.fillRect(122 + i * 100, y + 40, 40, 24);
        }
      }
      ctx.fillStyle = '#9aa6b6'; ctx.fillRect(70, 470, 20, 820); ctx.fillRect(990, 470, 20, 820);
      if (sh.grabFrom !== undefined && T > sh.grabFrom - 0.5) {
        const cols = ['#3d7bff', '#35c46a', '#ffd23f', '#a46bff', '#e8343f', '#ff8a3d'];
        for (let i = 0; i < 6; i++) { const sp = 260 + i * 40, x = ((T - sh.grabFrom) * sp + i * 220) % 1400 - 200; person(ctx, i % 2 ? W - x : x, 1360 + (i % 3) * 30, 1.5, cols[i], { walk: T * 12 + i, bottle: true, flip: i % 2 === 1 }); }
      }
      if (sh.emptyAt !== undefined && T > sh.emptyAt) tagBox(ctx, sh.emptyText || 'SOLD OUT', 540, 900, FP.red, { size: 90, rot: -0.1, scale: ease.outBack(ramp(T, sh.emptyAt, sh.emptyAt + 0.3)) });
    });
  },

  f_glass(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    fcam(ctx, cam, 0.8, () => { fbg(ctx, '#0b1122'); glow(ctx, 540, 760, 650, 'rgba(255,230,150,0.35)', 1); });
    fcam(ctx, cam, 1, () => {
      ctx.fillStyle = 'rgba(255,240,190,0.1)'; ctx.beginPath(); ctx.moveTo(440, 0); ctx.lineTo(640, 0); ctx.lineTo(900, 1100); ctx.lineTo(180, 1100); ctx.fill();
      ctx.fillStyle = '#7a2433'; ell(ctx, 540, 1080, 260, 50, '#7a2433'); ctx.fillRect(280, 1080, 520, 140); ell(ctx, 540, 1220, 260, 50, '#5c1a27');
      glass(ctx, 540, 900, 1.4, 0.7, T);
      for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + T * 0.6, r = 260 + Math.sin(T * 3 + i) * 20, s = 16 + 8 * Math.sin(T * 5 + i); ctx.save(); ctx.translate(540 + Math.cos(a) * r, 860 + Math.sin(a) * r * 0.7); ctx.rotate(Math.PI / 4); ctx.fillStyle = FP.yellow; ctx.fillRect(-s / 2, -s / 2, s, s); ctx.restore(); }
      if (sh.priceAt !== undefined && T > sh.priceAt) tagBox(ctx, sh.price || 'PRICELESS', 760, 640, FP.yellow, { size: 56, rot: 0.12 + Math.sin(T * 2) * 0.04, scale: ease.outBack(ramp(T, sh.priceAt, sh.priceAt + 0.3)) });
    });
    if (sh.face) heroFace(ctx, T, 210, 1880 - 260, 0.62, sh.face, { lookX: 0.7, lookY: -0.6 });
  },

  f_door(ctx, T, sh) {
    const cam = fcamOf(sh, T);
    const dark = sh.dark !== undefined ? (sh.dark === true ? 1 : so(T, sh.dark, sh.dark + 0.8)) : 0;
    const appear = sh.doorAt !== undefined ? ease.outBack(ramp(T, sh.doorAt, sh.doorAt + 0.4)) : 1;
    const open = sh.openAt !== undefined ? so(T, sh.openAt, sh.openAt + 0.8) * 0.28 : (sh.open || 0);
    let kick = 0; for (const k of sh.knocks || []) if (T > k && T < k + 0.35) kick = 1 - (T - k) / 0.35;
    const ks = kick ? shake(T, 14 * kick, 40, 6) : { x: 0, y: 0 };
    fcam(ctx, { ...cam, x: cam.x + ks.x, y: cam.y + ks.y }, 0.6, () => { morningSky(ctx, -400, 760); ctx.fillStyle = '#4a5a80'; for (let x = -300; x < W + 300; x += 120) ctx.fillRect(x, 560 - (x * 5 % 140), 100, 240); });
    fcam(ctx, { ...cam, x: cam.x + ks.x, y: cam.y + ks.y }, 1, () => {
      ctx.fillStyle = WP.grass2; ctx.fillRect(-500, 700, W + 1000, 120);
      ctx.fillStyle = WP.mud; ctx.fillRect(-500, 800, W + 1000, 1400); cracks(ctx, -400, 820, W + 800, 1100, 11);
      // concrete frame + door
      ctx.save(); ctx.translate(540, 1240); ctx.scale(appear, appear);
      ctx.fillStyle = '#8f98a6'; rr(ctx, -250, -700, 500, 720, 20); ctx.fill();
      ctx.fillStyle = '#05060a'; rr(ctx, -200, -650, 400, 650, 8); ctx.fill();
      if (sh.eyesAt !== undefined && T > sh.eyesAt && open > 0) {
        const bl = (T % 2.6) < 0.12 ? 0.15 : 1, a = so(T, sh.eyesAt, sh.eyesAt + 0.5);
        const ex = 120 + 40 * (open / 0.28);
        ell(ctx, ex - 22, -380, 12, 8 * bl, `rgba(232,52,63,${a})`); ell(ctx, ex + 22, -380, 12, 8 * bl, `rgba(232,52,63,${a})`);
        glow(ctx, ex, -380, 80, 'rgba(232,52,63,0.6)', a);
      }
      const dw = 400 * (1 - open);
      ctx.fillStyle = WP.metal; rr(ctx, -200, -650, dw, 650, 8); ctx.fill();
      ctx.fillStyle = WP.metal2; ctx.fillRect(-200 + dw - 12, -650, 12, 650);
      for (let i = 0; i < 6; i++) { circ(ctx, -170, -610 + i * 115, 9, WP.metal2); circ(ctx, -200 + dw - 34, -610 + i * 115, 9, WP.metal2); }
      ctx.strokeStyle = WP.metal2; ctx.lineWidth = 14; ctx.beginPath(); ctx.arc(-200 + dw * 0.5, -330, 70 * (1 - open), 0, 7); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-200 + dw * 0.5 - 70 * (1 - open), -330); ctx.lineTo(-200 + dw * 0.5 + 70 * (1 - open), -330); ctx.stroke();
      ctx.fillStyle = FP.yellow; ctx.fillRect(-250, -720, 500, 26); ctx.fillStyle = '#111'; for (let i = 0; i < 10; i++) ctx.fillRect(-250 + i * 52, -720, 24, 26);
      ctx.restore();
      // knock texts
      (sh.knocks || []).forEach((k, i) => { if (T > k) { const p = ease.outBack(ramp(T, k, k + 0.2)); tagBox(ctx, sh.knockText || 'KNOCK', [280, 800, 540][i % 3], [560, 640, 470][i % 3], FP.yellow, { size: 56, rot: [-0.2, 0.18, -0.05][i % 3], scale: p }); } });
    });
    // darkness + flashlight
    if (dark > 0) {
      ctx.fillStyle = `rgba(3,5,12,${0.82 * dark})`; ctx.fillRect(0, 0, W, H);
      const fl = sh.flashAt !== undefined ? so(T, sh.flashAt, sh.flashAt + 0.15) : 0;
      if (fl > 0) {
        ctx.save(); ctx.globalCompositeOperation = 'lighter';
        const g = ctx.createLinearGradient(900, 1700, 640, 900); g.addColorStop(0, `rgba(255,240,180,${0.55 * fl})`); g.addColorStop(1, `rgba(255,240,180,${0.1 * fl})`);
        ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(880, 1640); ctx.lineTo(940, 1660); ctx.lineTo(820, 800); ctx.lineTo(500, 820); ctx.fill();
        ctx.restore();
        glow(ctx, 680, 880, 220, 'rgba(255,240,180,0.6)', fl);
      }
    }
    if (sh.hand) {
      ctx.save(); ctx.translate(900, 1720); ctx.rotate(-0.4);
      ctx.fillStyle = FP.hood3; rr(ctx, -70, 40, 140, 400, 60); ctx.fill(); circ(ctx, 0, 30, 60, FP.skin);
      ctx.fillStyle = '#0a0c12'; rr(ctx, -40, -110, 80, 150, 14); ctx.fill();
      if (sh.flashAt !== undefined && T > sh.flashAt) circ(ctx, 0, -96, 10, '#fff8d0');
      ctx.restore();
    }
    if (sh.questions !== undefined) [[200, 560, 160, FP.yellow], [880, 500, 200, FP.red], [760, 1150, 130, FP.white]].forEach(([x, y, s, c], i) => { const p = ease.outBack(ramp(T, sh.questions + i * 0.4, sh.questions + i * 0.4 + 0.3)); if (p > 0) ftext(ctx, '?', x, y, s * p, c); });
  },

  f_end(ctx, T, sh) {
    fbg(ctx, '#0b1122', 'rgba(232,52,63,0.18)');
    ctx.fillStyle = WP.mud2; ctx.beginPath(); ctx.moveTo(0, 1500); ctx.quadraticCurveTo(540, 1380, W, 1500); ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.fill();
    cracks(ctx, 0, 1520, W, 380, 5, '#3e2e20');
    const q = ease.outBack(ramp(T, sh.q, sh.q + 0.4));
    ftext(ctx, sh.line1, 540, 470, 92 * q, FP.white, { maxW: 980 });
    ftext(ctx, sh.line2, 540, 580, 92 * q, FP.yellow, { maxW: 980 });
    if (sh.ask !== undefined && T > sh.ask) { const p = so(T, sh.ask, sh.ask + 0.4); ftext(ctx, sh.askText, 540, 720, 46, FP.white, { alpha: p, maxW: 980 }); ftext(ctx, sh.askText2, 540, 780, 40, FP.red, { alpha: p, maxW: 980 }); }
    FLAT.f_final(ctx, T, { ...sh, q: 1e9, a: 1e9, b: 1e9, c: 1e9, noBg: true });
  },
});

// emergency alert icon for lock-screen notifications
const _appIcon = appIcon;
appIcon = function (g, x, y, r, kind) {
  if (kind !== 'alert') return _appIcon(g, x, y, r, kind);
  g.fillStyle = FP.red; rr(g, x - r, y - r, r * 2, r * 2, r * 0.45); g.fill();
  text(g, '⚠', x, y + r * 0.4, { font: font(800, r * 1.1), align: 'center', color: '#fff' });
};

// EP02 thumbnail (9:16)
window.renderThumbEp02 = () => {
  const ctx = MAIN.getContext('2d'), T = 5;
  ctx.save();
  FLAT.f_door(ctx, T, { start: 0, end: 10, open: 0.3, eyesAt: 0, cam: [[540, 1000, 1.05], [540, 1000, 1.05]] });
  // tilted boat on the dry riverbed
  ctx.save(); ctx.translate(860, 1420); ctx.rotate(0.3);
  ctx.fillStyle = FP.yellow; ctx.beginPath(); ctx.moveTo(-130, -24); ctx.lineTo(130, -24); ctx.lineTo(96, 36); ctx.lineTo(-96, 36); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.fillRect(-10, -150, 10, 126); ctx.beginPath(); ctx.moveTo(0, -150); ctx.lineTo(84, -50); ctx.lineTo(0, -50); ctx.fill();
  ctx.restore();
  const g = ctx.createLinearGradient(0, 0, 0, 640); g.addColorStop(0, 'rgba(8,10,20,0.85)'); g.addColorStop(1, 'rgba(8,10,20,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, 640);
  ftext(ctx, S('thumb2_1'), 540, 260, 210, FP.white, { maxW: 1000 });
  ftext(ctx, S('thumb2_2'), 540, 440, 150, FP.yellow, { maxW: 1000 });
  heroFace(ctx, T, 250, 1640, 0.95, 'scared', { lookX: 0.9, lookY: -0.6, sweat: true, seed: 0.5 });
  tagBox(ctx, S('thumb2_tag'), 770, 1180, FP.red, { size: 58, rot: -0.07 });
  ftext(ctx, '?', 960, 700, 190, FP.red);
  ctx.restore();
  return MAIN.toDataURL('image/png');
};
