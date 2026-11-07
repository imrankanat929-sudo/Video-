// Episode 02 — cinematic 16:9 scenes ("What if water disappeared from the whole planet?").
// Same visual language and hero as episode 01 (art.js / scenes.js). Shot types are prefixed "c_".
'use strict';

const CP = {
  dawn1: '#1a2336', dawn2: '#4a5470', dawn3: '#c9a07a', haze: 'rgba(200,180,160,',
  mud: '#3e3227', mud2: '#2a2119', mudLit: '#5a4836', crack: '#1a140f',
  steel: '#4b525c', steel2: '#2c3138', rust: '#6b3b22', water: '#2d5f86', waterLit: '#7fb2d6',
};

// ---------- shared drawing helpers ----------
function skyGrad(ctx, y0, y1, stops) {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  stops.forEach(([k, c]) => g.addColorStop(k, c));
  ctx.fillStyle = g; ctx.fillRect(-2000, y0, 6000, y1 - y0);
}
function dawnSky(ctx, y0 = -600, y1 = 700, bright = 1) {
  skyGrad(ctx, y0, y1, [[0, '#0f1626'], [0.55, mix('#2a3550', '#3a4a6a', bright)], [0.85, mix('#5a5466', '#9a7c74', bright)], [1, mix('#7a6a66', '#d2a27e', bright)]]);
}
function crackField(ctx, x, y, w, h, seed, col = CP.crack, density = 1) {
  const r = mulberry32(seed);
  ctx.strokeStyle = col; ctx.lineCap = 'round';
  const n = Math.floor(w * h / 5000 * density);
  for (let i = 0; i < n; i++) {
    let px = x + r() * w, py = y + r() * h;
    const k = (py - y) / h;                       // perspective: thinner far away
    ctx.lineWidth = 1 + 2.5 * k;
    ctx.beginPath(); ctx.moveTo(px, py);
    for (let s = 0; s < 4; s++) { px += (r() - 0.5) * 90 * (0.4 + k); py += (r() - 0.5) * 22 * (0.4 + k); ctx.lineTo(px, py); }
    ctx.stroke();
  }
}
function mudPlane(ctx, x, y, w, h, seed, lit = 0.3) {
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, mix('#4a3d31', '#7a6550', lit)); g.addColorStop(1, mix(CP.mud2, '#4a3a2b', lit));
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
  crackField(ctx, x, y, w, h, seed);
}
function silhouettePerson(ctx, x, y, h, col = '#07090e', o = {}) {   // detailed-ish standing silhouette, feet at (x,y)
  ctx.save(); ctx.translate(x, y); const s = h / 170; ctx.scale(s * (o.flip ? -1 : 1), s);
  const sw = o.walk ? Math.sin(o.walk) : 0;
  ctx.fillStyle = col;
  ctx.beginPath(); ctx.moveTo(-8, 0); ctx.lineTo(-10 + sw * 10, -70); ctx.lineTo(0, -80); ctx.lineTo(10 - sw * 10, -70); ctx.lineTo(8, 0); ctx.lineTo(2, 0); ctx.lineTo(0, -60); ctx.lineTo(-2, 0); ctx.fill();
  rr(ctx, -20, -140, 40, 74, 14); ctx.fill();
  ctx.beginPath(); ctx.arc(0, -154, 14, 0, 7); ctx.fill();
  if (o.phone) { ctx.save(); ctx.translate(16, -150); ctx.rotate(-0.3); ctx.fillRect(-3, -12, 10, 18); ctx.restore(); ctx.lineWidth = 7; ctx.strokeStyle = col; ctx.beginPath(); ctx.moveTo(14, -130); ctx.lineTo(20, -150); ctx.stroke();
    if (o.flash) glow(ctx, 20, -156, 60, 'rgba(255,255,255,0.95)', o.flash); else if (o.screen) glow(ctx, 18, -150, 30, 'rgba(170,200,255,0.7)', o.screen); }
  if (o.bottle) { ctx.fillStyle = 'rgba(120,170,220,0.8)'; ctx.fillRect(-34, -110, 12, 30); }
  ctx.restore();
}
function windDust(ctx, T, cx, cy, w, h, amt = 1, seed = 0) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const r = mulberry32(seed + 50);
  for (let i = 0; i < 120 * amt; i++) {
    const sp = 300 + r() * 500, x = cx - w / 2 + ((r() * w + T * sp) % w), y = cy - h / 2 + r() * h + Math.sin(T * 2 + i) * 10;
    ctx.fillStyle = `rgba(210,180,140,${0.05 + r() * 0.12})`; ctx.fillRect(x, y, 2 + r() * 10, 1 + r() * 2);
  }
  ctx.restore();
}
function hazeBand(ctx, y, h, a = 0.3, col = '200,170,140') {
  const g = ctx.createLinearGradient(0, y - h, 0, y + h);
  g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(0.5, `rgba(${col},${a})`); g.addColorStop(1, `rgba(${col},0)`);
  ctx.fillStyle = g; ctx.fillRect(-2000, y - h, 6000, 2 * h);
}
function chromeTap(ctx, x, y, s, handleRot = 0, o = {}) {      // detailed chrome faucet; (x,y) = base on the counter
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const ch = (x0, x1) => { const g = ctx.createLinearGradient(x0, 0, x1, 0); g.addColorStop(0, '#3a4048'); g.addColorStop(0.3, '#c8d0da'); g.addColorStop(0.45, '#f4f7fa'); g.addColorStop(0.7, '#6d7681'); g.addColorStop(1, '#2a2f36'); return g; };
  // shadow on the wall/counter
  ctx.save(); ctx.filter = 'blur(10px)'; ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.beginPath(); ctx.ellipse(30, 4, 90, 14, 0, 0, 7); ctx.fill(); ctx.restore();
  ctx.fillStyle = ch(-60, 60); rr(ctx, -60, -26, 120, 30, 10); ctx.fill();                   // base
  ctx.fillStyle = ch(-24, 24); rr(ctx, -24, -260, 48, 240, 12); ctx.fill();                  // column
  // spout arc
  ctx.lineCap = 'round'; ctx.lineWidth = 38;
  const g = ctx.createLinearGradient(0, -330, 0, -250); g.addColorStop(0, '#f2f5f8'); g.addColorStop(0.5, '#9aa3ad'); g.addColorStop(1, '#2f353c');
  ctx.strokeStyle = g; ctx.beginPath(); ctx.moveTo(0, -240); ctx.bezierCurveTo(0, -360, 150, -360, 170, -260); ctx.stroke();
  ctx.fillStyle = '#20252b'; ctx.beginPath(); ctx.ellipse(170, -238, 17, 6, 0, 0, 7); ctx.fill();          // nozzle
  ctx.fillStyle = 'rgba(255,255,255,0.8)'; ctx.fillRect(-8, -250, 5, 200);                                 // specular
  // lever handle
  ctx.save(); ctx.translate(0, -262); ctx.rotate(handleRot);
  ctx.fillStyle = ch(-12, 12); rr(ctx, -12, -120, 24, 120, 10); ctx.fill();
  ctx.fillStyle = ch(-22, 22); rr(ctx, -22, -18, 44, 30, 10); ctx.fill();
  ctx.restore();
  if (o.light) glow(ctx, 40, -300, 220, 'rgba(255,230,200,0.25)', o.light);
  ctx.restore();
}
function glassCine(ctx, x, y, s, level = 0, T = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  if (level > 0) {
    ctx.save(); ctx.beginPath(); ctx.moveTo(-50, -100); ctx.lineTo(50, -100); ctx.lineTo(40, 90); ctx.lineTo(-40, 90); ctx.closePath(); ctx.clip();
    const top = lerp(90, -80, level);
    const g = ctx.createLinearGradient(0, top, 0, 90); g.addColorStop(0, 'rgba(150,200,240,0.75)'); g.addColorStop(1, 'rgba(40,90,140,0.85)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-60, top + Math.sin(T * 3) * 3);
    for (let i = -60; i <= 60; i += 8) ctx.lineTo(i, top + Math.sin(T * 3 + i * 0.06) * 3);
    ctx.lineTo(60, 100); ctx.lineTo(-60, 100); ctx.fill(); ctx.restore();
  }
  ctx.strokeStyle = 'rgba(220,235,250,0.55)'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.moveTo(-50, -100); ctx.lineTo(-40, 90); ctx.lineTo(40, 90); ctx.lineTo(50, -100); ctx.stroke();
  ctx.beginPath(); ctx.ellipse(0, -100, 50, 8, 0, 0, 7); ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(-36, -80, 6, 150);
  ctx.restore();
}
function handSil(ctx, x, y, s, rot = 0, col = '#120f10') {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.fillStyle = col;
  rr(ctx, -40, -30, 80, 70, 26); ctx.fill(); rr(ctx, -60, 30, 120, 240, 50); ctx.fill();
  ctx.restore();
}
function lightShaft(ctx, x0, y0, x1, y1, w0, w1, a = 0.12, col = '255,220,180') {
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  const g = ctx.createLinearGradient(x0, y0, x1, y1); g.addColorStop(0, `rgba(${col},${a})`); g.addColorStop(1, `rgba(${col},0)`);
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x0 - w0, y0); ctx.lineTo(x0 + w0, y0); ctx.lineTo(x1 + w1, y1); ctx.lineTo(x1 - w1, y1); ctx.fill();
  ctx.restore();
}

// ---------- scenes ----------
const CINE = {
  // 1. bedroom: alarm clock, the hero wakes up and sits on the bed
  c_wake(ctx, T, sh) {
    const cam = camOf(sh, T);
    const sit = sh.sitAt !== undefined ? ease.inOutSine(ramp(T, sh.sitAt, sh.sitAt + 1.4)) : 0;
    const ring = sh.alarm && T > sh.alarm[0] && T < sh.alarm[1];
    withCam(ctx, cam, 0.78, () => drawRoomBack(ctx, T, { morning: true }));
    withCam(ctx, cam, 0.78, () => lightShaft(ctx, 480, 360, 1100, 1100, 160, 420, 0.14));
    withCam(ctx, cam, 1, () => {
      // nightstand + alarm clock
      ctx.fillStyle = '#0c1018'; ctx.fillRect(1420, 700, 300, 400); ctx.fillStyle = 'rgba(150,170,210,0.08)'; ctx.fillRect(1420, 700, 300, 3);
      const j = ring ? shake(T, 3, 60, 2) : { x: 0, y: 0 };
      ctx.save(); ctx.translate(1570 + j.x, 650 + j.y); ctx.rotate(j.x * 0.01);
      ctx.fillStyle = '#05070b'; rr(ctx, -90, -50, 180, 100, 18); ctx.fill();
      text(ctx, '07:00', 0, 18, { font: font(700, 54, 'mono'), align: 'center', color: ring && Math.floor(T * 4) % 2 ? '#ff5a62' : '#c8323a' });
      ctx.restore();
      glow(ctx, 1570, 650, 260, 'rgba(200,50,58,0.5)', ring ? 0.9 : 0.4);
      // bed
      ctx.fillStyle = '#121826'; rr(ctx, 150, 760, 1250, 360, 24); ctx.fill();
      ctx.fillStyle = '#1b2233'; rr(ctx, 170, 700, 1220, 110, 30); ctx.fill();         // mattress
      ctx.fillStyle = '#2a3247'; rr(ctx, 200, 640, 300, 110, 50); ctx.fill();          // pillow
      // hero: pivot at hip, lying -> sitting up
      const a = lerp(-1.42, -0.12, sit);
      ctx.save(); ctx.beginPath(); ctx.rect(-500, -500, 3000, 1300); ctx.clip();
      ctx.translate(lerp(820, 760, sit), lerp(740, 760, sit)); ctx.rotate(a);
      drawHeroSide(ctx, T, 0, -420 * 0.95, 0.95, { rimCol: `rgba(210,180,150,${0.5 + 0.4 * sit})`, rimX: 6, rimY: 2, lean: 0 });
      ctx.restore();
      // blanket (slides down when he sits up)
      ctx.fillStyle = '#2b3550';
      ctx.beginPath(); ctx.moveTo(lerp(560, 700, sit), lerp(700, 770, sit)); ctx.quadraticCurveTo(900, lerp(640, 740, sit), 1390, lerp(690, 770, sit)); ctx.lineTo(1400, 860); ctx.lineTo(lerp(520, 680, sit), 860); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.3)'; ctx.lineWidth = 6; for (let i = 0; i < 4; i++) { ctx.beginPath(); ctx.moveTo(800 + i * 140, 760); ctx.quadraticCurveTo(840 + i * 140, 800, 820 + i * 140, 850); ctx.stroke(); }
      dust(ctx, T, 800, 600, 500, 0.9, 7);
    });
  },

  // 2. kitchen + chrome tap (wide -> close-up through camera keyframes)
  c_kitchen(ctx, T, sh) {
    const cam = camOf(sh, T);
    const open = sh.openAt !== undefined ? so(T, sh.openAt, sh.openAt + 0.35) : 0;
    let hard = 0; for (const t of [].concat(sh.hardAt || [])) if (T > t) hard = Math.min(1, hard + 0.5);
    const wig = sh.hardAt !== undefined && T > [].concat(sh.hardAt)[0] ? Math.abs(Math.sin((T - [].concat(sh.hardAt)[0]) * 5)) * 0.35 : 0;
    withCam(ctx, cam, 0.85, () => {
      skyGrad(ctx, -400, 1500, [[0, '#121a2a'], [1, '#0a0e17']]);
      // tiles
      ctx.strokeStyle = 'rgba(160,180,210,0.05)'; ctx.lineWidth = 2;
      for (let y = 200; y < 760; y += 64) { ctx.beginPath(); ctx.moveTo(-400, y); ctx.lineTo(2400, y); ctx.stroke(); }
      for (let x = -400; x < 2400; x += 64) { ctx.beginPath(); ctx.moveTo(x, 200); ctx.lineTo(x, 760); ctx.stroke(); }
      drawWindow(ctx, T, 1180, 120, 520, 470, {}); morningWash(ctx, 1180, 120, 520, 470, 0.8);
      ctx.fillStyle = '#0b0f17'; rr(ctx, 120, 150, 620, 230, 8); ctx.fill();            // cabinets
      ctx.fillStyle = 'rgba(150,170,210,0.06)'; ctx.fillRect(425, 150, 4, 230);
    });
    withCam(ctx, cam, 0.85, () => lightShaft(ctx, 1440, 360, 900, 1100, 200, 500, 0.12));
    withCam(ctx, cam, 1, () => {
      // counter
      const cg = ctx.createLinearGradient(0, 760, 0, 800); cg.addColorStop(0, '#2a3040'); cg.addColorStop(1, '#151a24');
      ctx.fillStyle = cg; ctx.fillRect(-400, 760, 2800, 40);
      ctx.fillStyle = '#0a0d14'; ctx.fillRect(-400, 800, 2800, 600);
      for (let x = -200; x < 2400; x += 330) { ctx.fillStyle = '#0d111a'; rr(ctx, x, 830, 300, 330, 8); ctx.fill(); ctx.fillStyle = 'rgba(160,180,210,0.12)'; ctx.fillRect(x + 140, 870, 20, 4); }
      // sink
      ctx.fillStyle = '#3a414c'; rr(ctx, 860, 750, 460, 24, 10); ctx.fill();
      ctx.fillStyle = '#12161d'; rr(ctx, 880, 752, 420, 12, 6); ctx.fill();
      chromeTap(ctx, 1000, 760, 0.6, -open * (1.0 + wig), { light: 0.6 });
      // empty nozzle: only silence — a little dust drifting in the light
      if (open > 0) { glow(ctx, 1102, 630, 60, 'rgba(255,240,210,0.25)', open); dust(ctx, T, 1102, 660, 70, 0.8 * open, 3); }
      // glass in hand under the spout
      glassCine(ctx, 1104, 705, 0.42, 0, T);
      handSil(ctx, 1140, 712, 0.42, 0.5);
      // hero side silhouette at the counter
      drawHeroSide(ctx, T, 640, 360, 1.15, { rimCol: 'rgba(220,190,160,0.75)', rimX: 7, rimY: 2, lean: 0.12 });
      ctx.fillStyle = '#0a0d14'; ctx.fillRect(-400, 800, 1100, 600);
    });
  },

  // 3. bathroom: mirror, sink tap, shower
  c_bath(ctx, T, sh) {
    const cam = camOf(sh, T);
    const tap = sh.tapAt !== undefined ? so(T, sh.tapAt, sh.tapAt + 0.35) : 0, sho = sh.showerAt !== undefined ? so(T, sh.showerAt, sh.showerAt + 0.35) : 0;
    const flick = 0.85 + 0.15 * (noise1(T * 8, 4) > 0.6 ? 0 : 1);
    withCam(ctx, cam, 0.9, () => {
      skyGrad(ctx, -400, 1500, [[0, '#14202a'], [1, '#0a1016']]);
      ctx.strokeStyle = 'rgba(160,200,210,0.06)'; ctx.lineWidth = 2;
      for (let y = -400; y < 1500; y += 80) { ctx.beginPath(); ctx.moveTo(-400, y); ctx.lineTo(2400, y); ctx.stroke(); }
      for (let x = -400; x < 2400; x += 80) { ctx.beginPath(); ctx.moveTo(x, -400); ctx.lineTo(x, 1500); ctx.stroke(); }
      glow(ctx, 700, 60, 700, 'rgba(200,230,240,0.35)', flick);                 // ceiling lamp
      // mirror with the hero's reflection
      ctx.fillStyle = '#0c1419'; rr(ctx, 450, 160, 520, 420, 12); ctx.fill();
      ctx.save(); rr(ctx, 460, 170, 500, 400, 8); ctx.clip();
      const mg = ctx.createLinearGradient(460, 170, 960, 570); mg.addColorStop(0, '#2a3a44'); mg.addColorStop(1, '#141c22'); ctx.fillStyle = mg; ctx.fillRect(460, 170, 500, 400);
      drawHeroBack(ctx, T, 720, 420, 0.75, { rimCol: 'rgba(170,200,210,0.5)', rimX: -4, rimY: -4 });
      ctx.fillStyle = 'rgba(255,255,255,0.06)'; ctx.beginPath(); ctx.moveTo(460, 170); ctx.lineTo(620, 170); ctx.lineTo(460, 400); ctx.fill();
      ctx.restore();
    });
    withCam(ctx, cam, 1, () => {
      // sink
      ctx.fillStyle = '#c9d2d8'; ctx.beginPath(); ctx.ellipse(710, 720, 280, 60, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#7d8a92'; ctx.beginPath(); ctx.ellipse(710, 716, 240, 42, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#20282e'; ctx.beginPath(); ctx.ellipse(710, 722, 18, 6, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#5d6a72'; ctx.fillRect(670, 780, 80, 400);
      chromeTap(ctx, 600, 680, 0.6, -tap * 1.0);
      // shower
      ctx.fillStyle = 'rgba(160,200,220,0.08)'; ctx.fillRect(1250, 0, 600, 1100); ctx.strokeStyle = 'rgba(200,230,240,0.25)'; ctx.lineWidth = 4; ctx.strokeRect(1250, -20, 600, 1120);
      const pipe = ctx.createLinearGradient(1700, 0, 1730, 0); pipe.addColorStop(0, '#3a4048'); pipe.addColorStop(0.5, '#e8eef2'); pipe.addColorStop(1, '#3a4048');
      ctx.fillStyle = pipe; ctx.fillRect(1700, 150, 28, 700); ctx.fillRect(1520, 150, 200, 24);
      ctx.save(); ctx.translate(1520, 190); ctx.rotate(sho ? Math.sin(T * 30) * 0.03 * (1 - ramp(T, sh.showerAt + 0.5, sh.showerAt + 1.0)) : 0);
      const hg = ctx.createLinearGradient(-110, 0, 110, 0); hg.addColorStop(0, '#4a525c'); hg.addColorStop(0.4, '#e8eef2'); hg.addColorStop(1, '#3a4048');
      ctx.fillStyle = hg; ctx.beginPath(); ctx.ellipse(0, 0, 110, 46, 0, Math.PI, 0); ctx.fill(); ctx.fillStyle = '#20262c'; ctx.fillRect(-110, 0, 220, 12);
      for (let i = -4; i <= 4; i++) circ(ctx, i * 22, 6, 3, '#0a0d10');
      ctx.restore();
      ctx.save(); ctx.translate(1714, 700); ctx.rotate(-sho * 1.4); ctx.fillStyle = pipe; rr(ctx, -10, -70, 20, 70, 8); ctx.fill(); ctx.restore();
    });
  },

  // 4. over-the-shoulder at the window, then the river (memory vs. today)
  c_river(ctx, T, sh) {
    const cam = camOf(sh, T);
    const dry = sh.dry ? 1 : 0, memory = sh.memory ? 1 : 0;
    const daylight = sh.daylight ?? 0.4;
    withCam(ctx, cam, 0.35, () => {
      dawnSky(ctx, -600, 560, daylight);
      if (sh.sunMove) { const k = ramp(T, sh.start, sh.end); glow(ctx, lerp(300, 1600, k), lerp(420, 120, k), 300, 'rgba(255,220,170,0.5)', 1); }
      else glow(ctx, 1450, 440, 360, 'rgba(255,200,150,0.45)', 1);
      if (sh.clouds) { const r = mulberry32(3); for (let i = 0; i < 8; i++) { ctx.fillStyle = 'rgba(60,60,80,0.35)'; ctx.beginPath(); ctx.ellipse(((r() * 3000 + T * sh.clouds) % 3200) - 600, 80 + r() * 260, 260, 40, 0, 0, 7); ctx.fill(); } }
    });
    withCam(ctx, cam, 0.55, () => {
      // far skyline
      const r = mulberry32(31); let x = -900;
      while (x < 2900) { const w = 60 + r() * 110, h = 80 + r() * 260; ctx.fillStyle = mix('#151b28', '#262a38', daylight); ctx.fillRect(x, 560 - h, w, h);
        for (let wy = 560 - h + 12; wy < 550; wy += 18) for (let wx = x + 6; wx < x + w - 8; wx += 14) if (r() < 0.08 * (1 - daylight)) { ctx.fillStyle = 'rgba(255,210,150,0.5)'; ctx.fillRect(wx, wy, 5, 7); }
        x += w + r() * 10; }
      hazeBand(ctx, 540, 80, 0.35);
    });
    withCam(ctx, cam, 0.75, () => {
      // far bank with trees
      ctx.fillStyle = '#121812'; ctx.fillRect(-900, 560, 3800, 50);
      const r = mulberry32(8); for (let x = -900; x < 2900; x += 40 + r() * 50) { ctx.fillStyle = '#0d130f'; ctx.beginPath(); ctx.ellipse(x, 560, 30 + r() * 30, 40 + r() * 40, 0, Math.PI, 0); ctx.fill(); }
      // bridge
      ctx.fillStyle = '#0b0e14'; ctx.fillRect(-900, 470, 3800, 16);
      for (let px = -800; px < 2900; px += 420) { ctx.fillRect(px, 486, 30, dry ? 220 : 140); ctx.beginPath(); ctx.moveTo(px - 200, 486); ctx.quadraticCurveTo(px + 15, 400, px + 230, 486); ctx.lineWidth = 6; ctx.strokeStyle = '#0b0e14'; ctx.stroke(); }
    });
    withCam(ctx, cam, 0.9, () => {
      if (!dry) {
        const g = ctx.createLinearGradient(0, 600, 0, 860); g.addColorStop(0, '#3a4c66'); g.addColorStop(1, '#1b2638');
        ctx.fillStyle = g; ctx.fillRect(-900, 600, 3800, 260);
        ctx.save(); ctx.globalCompositeOperation = 'lighter';
        for (let i = 0; i < 70; i++) { const r = mulberry32(i)(); const x = ((i * 97 + T * (20 + r * 30)) % 3600) - 900, y = 610 + (i * 37 % 240); ctx.fillStyle = `rgba(255,210,170,${0.05 + r * 0.12})`; ctx.fillRect(x, y, 40 + r * 80, 2); }
        ctx.restore();
        // boats
        [[300, 700, 1], [1250, 760, 1.3], [1900, 690, 0.8]].forEach(([bx, by, s], i) => {
          const x = bx + Math.sin(T * 0.3 + i) * 30, y = by + Math.sin(T * 1.5 + i) * 3;
          ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = '#080a0f';
          ctx.beginPath(); ctx.moveTo(-90, -10); ctx.lineTo(90, -10); ctx.lineTo(70, 18); ctx.lineTo(-70, 18); ctx.fill(); ctx.fillRect(-20, -40, 50, 30);
          glow(ctx, 0, -30, 40, 'rgba(255,210,150,0.6)', 0.6); ctx.restore();
        });
      } else {
        mudPlane(ctx, -900, 600, 3800, 260, 12, daylight);
        ctx.fillStyle = 'rgba(30,24,18,0.6)'; ctx.fillRect(-900, 600, 3800, 14);       // old water line
        // stranded boats, tilted
        [[300, 760, 1, -0.25], [1250, 800, 1.3, 0.3], [1900, 740, 0.8, -0.15]].forEach(([bx, by, s, rt]) => {
          ctx.save(); ctx.translate(bx, by); ctx.rotate(rt); ctx.scale(s, s);
          ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.beginPath(); ctx.ellipse(10, 24, 100, 12, 0, 0, 7); ctx.fill();
          ctx.fillStyle = '#0c0f15'; ctx.beginPath(); ctx.moveTo(-90, -10); ctx.lineTo(90, -10); ctx.lineTo(70, 18); ctx.lineTo(-70, 18); ctx.fill(); ctx.fillRect(-20, -40, 50, 30);
          ctx.restore();
        });
        if (sh.crowd) {
          const r = mulberry32(17);
          for (let i = 0; i < 40; i++) {
            const x = -500 + r() * 2900, y = 640 + r() * 200, hgt = 50 + (y - 640) * 0.45;
            const fl = sh.flashFrom !== undefined && T > sh.flashFrom && ((T * 1.7 + i * 0.37) % 3) < 0.06 ? 1 : 0;
            silhouettePerson(ctx, x, y, hgt, '#07080b', { phone: i % 3 === 0, flash: fl, screen: i % 3 === 0 ? 0.6 : 0, flip: i % 2 === 0 });
          }
        }
        windDust(ctx, T, 960, 720, 3400, 300, 1.2, 1);
      }
    });
    withCam(ctx, cam, 1.05, () => {
      // near promenade with railing + people walking (memory only)
      ctx.fillStyle = '#0b0d12'; ctx.fillRect(-900, 860, 3800, 400);
      ctx.fillStyle = '#05070a'; ctx.fillRect(-900, 846, 3800, 8);
      for (let x = -900; x < 2900; x += 60) ctx.fillRect(x, 800, 6, 50);
      ctx.fillRect(-900, 800, 3800, 6);
      for (let x = -800; x < 2900; x += 520) { ctx.fillRect(x, 640, 10, 220); glow(ctx, x + 5, 640, 120, 'rgba(255,200,140,0.5)', daylight < 0.5 ? 0.6 : 0.15); }
      if (sh.walkers) for (let i = 0; i < 6; i++) silhouettePerson(ctx, ((T * (40 + i * 6) + i * 520) % 3000) - 700, 900, 150, '#040507', { walk: T * 6 + i, flip: i % 2 });
    });
    if (sh.hero) withCam(ctx, cam, 1.25, () => drawHeroBack(ctx, T, 960, 860, 1.25, { rimCol: 'rgba(230,190,150,0.7)', rimX: 0, rimY: -6 }));
    if (memory) {   // soft memory look: warm, bright, blurred edges
      ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = 'rgba(120,90,60,0.18)'; ctx.fillRect(0, 0, W, H); ctx.restore();
      const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H); g.addColorStop(0, 'rgba(240,220,200,0)'); g.addColorStop(1, 'rgba(240,220,200,0.22)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    }
    if (sh.windowFrame) withCam(ctx, cam, 1.6, () => {
      const k = sh.frameOut !== undefined ? ease.inOutSine(ramp(T, sh.frameOut, sh.end)) : 0;
      ctx.fillStyle = '#05070a';
      const m = lerp(140, -400, k);
      ctx.fillRect(-1200, -1200, 4400, 1200 + m); ctx.fillRect(-1200, 1080 - m, 4400, 1500);
      ctx.fillRect(-1200, -1200, 1200 + m * 1.7, 4000); ctx.fillRect(1920 - m * 1.7, -1200, 2000, 4000);
      ctx.fillRect(950, -400, 20, 2000);
    });
  },

  // 5. park: dry fountain, empty lake, small holes (panorama with pan)
  c_park(ctx, T, sh) {
    const cam = camOf(sh, T);
    const f = sh.fountainAt !== undefined ? so(T, sh.fountainAt, sh.fountainAt + 0.6) : 1;
    withCam(ctx, cam, 0.4, () => { dawnSky(ctx, -600, 520, 0.7); glow(ctx, 2200, 380, 400, 'rgba(255,200,150,0.4)', 1); });
    withCam(ctx, cam, 0.6, () => { const r = mulberry32(44); for (let x = -900; x < 4200; x += 70 + r() * 90) { ctx.fillStyle = '#1a1f2b'; const h = 120 + r() * 240; ctx.fillRect(x, 520 - h, 60 + r() * 60, h); } hazeBand(ctx, 500, 70, 0.3); });
    withCam(ctx, cam, 1, () => {
      ctx.fillStyle = '#1c2219'; ctx.fillRect(-900, 520, 5200, 900);
      // paths
      ctx.fillStyle = '#3a352e'; ctx.beginPath(); ctx.moveTo(-900, 900); ctx.quadraticCurveTo(1500, 760, 4200, 900); ctx.lineTo(4200, 980); ctx.quadraticCurveTo(1500, 840, -900, 980); ctx.fill();
      // trees
      const r = mulberry32(5); for (let x = -800; x < 4200; x += 180 + r() * 160) { ctx.fillStyle = '#0d120d'; ctx.beginPath(); ctx.ellipse(x, 520, 70, 120, 0, 0, 7); ctx.fill(); ctx.fillRect(x - 6, 560, 12, 60); }
      // fountain (stone basin, statue) — dry
      ctx.save(); ctx.translate(400, 760);
      ctx.fillStyle = '#4a4a4c'; ctx.beginPath(); ctx.ellipse(0, 0, 300, 70, 0, 0, 7); ctx.fill();
      ctx.fillStyle = mix('#2d5f86', CP.mud, f); ctx.beginPath(); ctx.ellipse(0, -6, 260, 52, 0, 0, 7); ctx.fill();
      crackField(ctx, -220, -40, 440, 70, 9, `rgba(20,15,10,${f})`, 3);
      ctx.fillStyle = '#5a5a5c'; ctx.fillRect(-30, -260, 60, 260); ctx.beginPath(); ctx.ellipse(0, -260, 110, 26, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#3a3a3c'; ctx.beginPath(); ctx.ellipse(0, -360, 30, 60, 0, 0, 7); ctx.fill();
      if (f < 1) { ctx.strokeStyle = `rgba(160,200,230,${0.6 * (1 - f)})`; ctx.lineWidth = 6; for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(0, -380); ctx.quadraticCurveTo(-120 + i * 60, -480, -200 + i * 100, -260); ctx.stroke(); } }
      ctx.restore();
      // the lake: an empty pit
      const l = sh.lakeAt !== undefined ? sm(T, sh.lakeAt, sh.lakeAt + 1.2) : 1;
      ctx.save(); ctx.translate(1700, 820);
      ctx.fillStyle = '#15120e'; ctx.beginPath(); ctx.ellipse(0, 0, 640, 150, 0, 0, 7); ctx.fill();
      ctx.save(); ctx.beginPath(); ctx.ellipse(0, 0, 620, 140, 0, 0, 7); ctx.clip(); mudPlane(ctx, -640, -150, 1280, 300, 21, 0.4);
      ctx.fillStyle = `rgba(45,95,134,${0.9 * (1 - l)})`; ctx.beginPath(); ctx.ellipse(0, 10 * l, 620 * (1 - l * 0.7), 140 * (1 - l * 0.7), 0, 0, 7); ctx.fill(); ctx.restore();
      ctx.save(); ctx.translate(-200, 40); ctx.rotate(0.2); ctx.fillStyle = '#0a0c10'; ctx.beginPath(); ctx.moveTo(-70, -8); ctx.lineTo(70, -8); ctx.lineTo(50, 14); ctx.lineTo(-50, 14); ctx.fill(); ctx.restore();   // rowboat
      ctx.restore();
      // small ponds -> dry holes
      [[2900, 860], [3250, 930], [3600, 850]].forEach(([x, y], i) => {
        const k = sh.holesAt !== undefined ? sm(T, sh.holesAt + i * 0.3, sh.holesAt + i * 0.3 + 0.8) : 1;
        ctx.fillStyle = '#120f0b'; ctx.beginPath(); ctx.ellipse(x, y, 170, 40, 0, 0, 7); ctx.fill();
        ctx.fillStyle = `rgba(45,95,134,${1 - k})`; ctx.beginPath(); ctx.ellipse(x, y, 160 * (1 - k * 0.6), 34 * (1 - k * 0.6), 0, 0, 7); ctx.fill();
      });
      windDust(ctx, T, 1500, 800, 5000, 400, 1, 4);
      // leaves blowing
      const lr = mulberry32(2); for (let i = 0; i < 40; i++) { const x = ((lr() * 5000 + T * 260) % 5200) - 900, y = 700 + lr() * 300 + Math.sin(T * 3 + i) * 20; ctx.save(); ctx.translate(x, y); ctx.rotate(T * 4 + i); ctx.fillStyle = '#5a3a1e'; ctx.fillRect(-6, -3, 12, 6); ctx.restore(); }
    });
  },

  // 6. TV news in a dark room (push-in to full screen)
  c_tv(ctx, T, sh) {
    const cam = camOf(sh, T);
    const scr = tvScreen(T, sh);
    withCam(ctx, cam, 0.85, () => {
      skyGrad(ctx, -400, 1500, [[0, '#0b0f17'], [1, '#07090e']]);
      glow(ctx, 960, 420, 1100, 'rgba(110,150,220,0.35)', 0.9 + 0.1 * Math.sin(T * 9));
    });
    withCam(ctx, cam, 1, () => {
      ctx.fillStyle = '#030406'; rr(ctx, 520, 170, 880, 510, 10); ctx.fill();
      ctx.drawImage(scr, 540, 190, 840, 472);
      ctx.fillStyle = 'rgba(255,255,255,0.04)'; ctx.beginPath(); ctx.moveTo(540, 190); ctx.lineTo(900, 190); ctx.lineTo(540, 480); ctx.fill();
      ctx.fillStyle = '#05070a'; ctx.fillRect(560, 700, 800, 40);
      // sofa + hero from behind
      ctx.fillStyle = '#0c0f16'; rr(ctx, 300, 820, 1320, 400, 40); ctx.fill();
    });
    withCam(ctx, cam, 1.15, () => drawHeroBack(ctx, T, 960, 700, 1.05, { rimCol: 'rgba(140,175,235,0.85)', rimX: 0, rimY: -6 }));
  },

  // 7. Earth from orbit: water drains from the planet
  c_globe(ctx, T, sh) {
    const cam = camOf(sh, T);
    const items = sh.items || [];
    const dry = items.length ? ramp(T, items[0].at, items[items.length - 1].at + 0.8) : 0;
    withCam(ctx, cam, 0.3, () => { ctx.fillStyle = '#020306'; ctx.fillRect(-1000, -1000, 4000, 3000); const r = mulberry32(1); for (let i = 0; i < 300; i++) { ctx.fillStyle = `rgba(255,255,255,${r() * 0.7})`; ctx.fillRect(-800 + r() * 3600, -600 + r() * 2400, 2, 2); } });
    withCam(ctx, cam, 1, () => {
      const cx = 960, cy = 540, R = 400;
      glow(ctx, cx, cy, R * 1.35, `rgba(90,150,255,${0.45 * (1 - dry) + 0.1})`, 1);
      ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.clip();
      ctx.fillStyle = mix('#1d4f86', '#6b5640', dry); ctx.fillRect(cx - R, cy - R, 2 * R, 2 * R);
      const off = ((T - sh.start) * 16) % 1600;
      const r = mulberry32(6), land = [];
      for (let i = 0; i < 14; i++) land.push([r() * 1600, -300 + r() * 600, 60 + r() * 160, 40 + r() * 110, r() * 3]);
      for (const [x, y, rx, ry, rot] of land) for (const k of [0, 1600]) { ctx.fillStyle = mix('#3e5a32', '#7a6046', dry); ctx.beginPath(); ctx.ellipse(cx - 800 + x - off + k - 1600 * (x - off + k > 1600 ? 1 : 0), cy + y, rx, ry, rot, 0, 7); ctx.fill(); }
      if (dry > 0.2) crackField(ctx, cx - R, cy - R, 2 * R, 2 * R, 2, `rgba(40,28,18,${dry * 0.7})`, 0.6);
      // clouds
      ctx.fillStyle = 'rgba(255,255,255,0.25)'; for (let i = 0; i < 9; i++) { ctx.beginPath(); ctx.ellipse(cx - R + ((i * 230 + T * 25) % (2 * R + 200)) - 100, cy - 300 + i * 70, 120, 18, 0.2, 0, 7); ctx.fill(); }
      // terminator shading
      const sg = ctx.createLinearGradient(cx - R, cy - R, cx + R, cy + R); sg.addColorStop(0, 'rgba(0,0,0,0)'); sg.addColorStop(0.55, 'rgba(0,0,0,0.15)'); sg.addColorStop(1, 'rgba(0,0,0,0.85)');
      ctx.fillStyle = sg; ctx.fillRect(cx - R, cy - R, 2 * R, 2 * R);
      ctx.restore();
    });
    // lower-third labels
    items.forEach((it, i) => {
      const a = so(T, it.at - 0.05, it.at + 0.3); if (a <= 0) return;
      const x = 960 + (i - (items.length - 1) / 2) * 300;
      text(ctx, it.text, x, 990, { font: font(800, 44), align: 'center', color: PAL.white, ls: 8, alpha: a });
      ctx.fillStyle = PAL.red; ctx.globalAlpha = a; ctx.fillRect(x - 70 * so(T, it.at + 0.2, it.at + 0.6), 975, 140 * so(T, it.at + 0.2, it.at + 0.6), 4); ctx.globalAlpha = 1;
    });
  },

  // 8. dry ocean floor with a stranded ship and fish
  c_seabed(ctx, T, sh) {
    const cam = camOf(sh, T);
    withCam(ctx, cam, 0.35, () => { skyGrad(ctx, -600, 560, [[0, '#2a2420'], [0.7, '#8a6a50'], [1, '#d2a77a']]); glow(ctx, 600, 380, 300, 'rgba(255,220,170,0.6)', 1); });
    withCam(ctx, cam, 0.7, () => { ctx.fillStyle = '#6a5440'; ctx.beginPath(); ctx.moveTo(-900, 540); for (let x = -900; x < 3000; x += 200) ctx.lineTo(x, 520 + Math.sin(x * 0.01) * 20); ctx.lineTo(3000, 700); ctx.lineTo(-900, 700); ctx.fill(); hazeBand(ctx, 540, 90, 0.5); });
    withCam(ctx, cam, 1, () => {
      const g = ctx.createLinearGradient(0, 560, 0, 1200); g.addColorStop(0, '#7a6048'); g.addColorStop(1, '#3a2c20'); ctx.fillStyle = g; ctx.fillRect(-900, 560, 3800, 900);
      ctx.strokeStyle = 'rgba(40,30,20,0.4)'; ctx.lineWidth = 3; for (let y = 600; y < 1200; y += 34) { ctx.beginPath(); for (let x = -900; x < 2900; x += 40) ctx.lineTo(x, y + Math.sin(x * 0.015 + y * 0.1) * 6); ctx.stroke(); }
      // the ship (huge, tilted) + shadow
      ctx.save(); ctx.translate(1150, 640); ctx.rotate(0.12);
      ctx.save(); ctx.filter = 'blur(16px)'; ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.beginPath(); ctx.ellipse(120, 120, 760, 60, 0, 0, 7); ctx.fill(); ctx.restore();
      const hull = ctx.createLinearGradient(0, -80, 0, 110); hull.addColorStop(0, '#2c2f36'); hull.addColorStop(1, '#121418');
      ctx.fillStyle = hull; ctx.beginPath(); ctx.moveTo(-760, -80); ctx.lineTo(640, -80); ctx.lineTo(760, -190); ctx.lineTo(700, 110); ctx.lineTo(-700, 110); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#5a2420'; ctx.fillRect(-700, 60, 1400, 50);
      for (let i = 0; i < 6; i++) { ctx.fillStyle = ['#4a3a2a', '#2a3a4a', '#3a2a2a'][i % 3]; ctx.fillRect(-450 + i * 150, -180, 140, 100); ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(-450 + i * 150, -180, 140, 12); }
      ctx.fillStyle = '#c9c4ba'; ctx.fillRect(-700, -300, 220, 220); ctx.fillStyle = '#20242a'; for (let i = 0; i < 4; i++) ctx.fillRect(-680 + i * 52, -270, 34, 24);
      ctx.fillStyle = 'rgba(255,220,170,0.25)'; ctx.fillRect(-760, -80, 1400, 6);
      ctx.restore();
      // fish lying on the sand
      if (sh.fishAt !== undefined && T > sh.fishAt) [[300, 980, 1], [520, 1040, 0.8], [1700, 1000, 1.1], [1500, 1070, 0.7], [800, 1090, 0.9]].forEach(([x, y, s], i) => {
        const a = so(T, sh.fishAt + i * 0.15, sh.fishAt + i * 0.15 + 0.4), flap = Math.sin(T * 7 + i * 2) * 0.15 * (i % 2);
        ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.rotate(flap); ctx.scale(s, s);
        ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.beginPath(); ctx.ellipse(6, 18, 70, 10, 0, 0, 7); ctx.fill();
        const fg = ctx.createLinearGradient(0, -24, 0, 24); fg.addColorStop(0, '#9aa4ac'); fg.addColorStop(1, '#4a5258');
        ctx.fillStyle = fg; ctx.beginPath(); ctx.ellipse(0, 0, 64, 22, 0, 0, 7); ctx.fill(); ctx.beginPath(); ctx.moveTo(56, 0); ctx.lineTo(100, -26); ctx.lineTo(100, 26); ctx.fill();
        circ(ctx, -40, -4, 5, '#111'); ctx.restore();
      });
      windDust(ctx, T, 960, 800, 3600, 500, 1.4, 2);
    });
  },

  // 9. panic: crowds rush into a store, shelves empty out
  c_store(ctx, T, sh) {
    const cam = camOf(sh, T);
    const left = sh.grabFrom !== undefined ? 1 - ramp(T, sh.grabFrom, sh.emptyAt) : 1;
    const flick = noise1(T * 12, 2) > 0.75 ? 0.6 : 1;
    withCam(ctx, cam, 0.85, () => {
      skyGrad(ctx, -400, 1500, [[0, '#1a1f26'], [1, '#0c0f14']]);
      for (let i = 0; i < 3; i++) { ctx.fillStyle = `rgba(220,240,255,${0.7 * flick})`; ctx.fillRect(300 + i * 500, 60, 340, 12); glow(ctx, 470 + i * 500, 66, 420, 'rgba(200,230,255,0.3)', flick); }
    });
    withCam(ctx, cam, 1, () => {
      for (let row = 0; row < 4; row++) {
        const y = 250 + row * 190;
        ctx.fillStyle = '#2a2f38'; ctx.fillRect(160, y + 120, 1600, 18);
        for (let i = 0; i < 22; i++) {
          if ((row * 22 + i) / 88 > left) continue;
          const bx = 190 + i * 71;
          const bg = ctx.createLinearGradient(bx, 0, bx + 44, 0); bg.addColorStop(0, 'rgba(90,140,190,0.7)'); bg.addColorStop(0.4, 'rgba(180,215,240,0.85)'); bg.addColorStop(1, 'rgba(60,100,150,0.7)');
          ctx.fillStyle = bg; rr(ctx, bx, y + 20, 44, 100, 10); ctx.fill(); ctx.fillStyle = '#d8dde2'; ctx.fillRect(bx + 14, y + 4, 16, 18);
        }
        ctx.fillStyle = '#f2f2f2'; for (let i = 0; i < 6; i++) ctx.fillRect(200 + i * 270, y + 124, 40, 10);
      }
      ctx.fillStyle = '#1a1e25'; ctx.fillRect(140, 200, 24, 900); ctx.fillRect(1760, 200, 24, 900);
    });
    withCam(ctx, cam, 1.3, () => {   // rushing silhouettes in the foreground
      if (sh.grabFrom === undefined || T < sh.grabFrom - 1) return;
      for (let i = 0; i < 9; i++) { const sp = 300 + (i % 4) * 90, dir = i % 2 ? -1 : 1, x = dir > 0 ? ((T * sp + i * 400) % 2800) - 400 : 2400 - ((T * sp + i * 400) % 2800); silhouettePerson(ctx, x, 1180 + (i % 3) * 40, 520 + (i % 3) * 60, '#030305', { walk: T * 10 + i, flip: dir < 0, bottle: i % 3 === 0 }); }
    });
  },

  // 10. a single glass of water under a spotlight
  c_glass(ctx, T, sh) {
    const cam = camOf(sh, T);
    withCam(ctx, cam, 0.8, () => { ctx.fillStyle = '#050608'; ctx.fillRect(-500, -500, 3000, 2200); lightShaft(ctx, 960, -200, 960, 760, 120, 380, 0.16, '255,235,200'); });
    withCam(ctx, cam, 1, () => {
      const tg = ctx.createLinearGradient(0, 700, 0, 1100); tg.addColorStop(0, '#2a221c'); tg.addColorStop(1, '#0a0806'); ctx.fillStyle = tg; ctx.fillRect(-500, 700, 3000, 600);
      glow(ctx, 960, 760, 380, 'rgba(255,230,190,0.45)', 1);
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; for (let i = 0; i < 12; i++) { ctx.strokeStyle = `rgba(160,210,255,${0.06 + 0.04 * Math.sin(T * 2 + i)})`; ctx.lineWidth = 3; ctx.beginPath(); ctx.ellipse(1000 + Math.sin(T + i) * 10, 780, 60 + i * 10, 10 + i * 2, 0, 0, 7); ctx.stroke(); } ctx.restore();
      ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.beginPath(); ctx.ellipse(985, 772, 90, 12, 0, 0, 7); ctx.fill();
      glassCine(ctx, 960, 680, 0.95, 0.72, T);
      dust(ctx, T, 960, 400, 400, 1, 12);
    });
  },

  // 11. the metal door in the dry riverbed (approach, knocks, flashlight)
  c_door(ctx, T, sh) {
    const cam = camOf(sh, T);
    let kick = 0; for (const k of sh.knocks || []) if (T > k && T < k + 0.45) kick = Math.max(kick, 1 - (T - k) / 0.45);
    const ks = kick ? shake(T, 16 * kick, 40, 6) : { x: 0, y: 0 };
    const c2 = { ...cam, x: cam.x + ks.x, y: cam.y + ks.y };
    const dark = sh.dark !== undefined ? (sh.dark === true ? 1 : so(T, sh.dark, sh.dark + 1)) : 0;
    const open = sh.openAt !== undefined ? so(T, sh.openAt, sh.openAt + 1.2) : (sh.open ?? 0);
    withCam(ctx, c2, 0.35, () => { dawnSky(ctx, -600, 520, 0.8); glow(ctx, 1500, 380, 320, 'rgba(255,210,160,0.45)', 1); });
    withCam(ctx, c2, 0.6, () => { const r = mulberry32(31); let x = -900; while (x < 2900) { const w = 60 + r() * 110, h = 80 + r() * 260; ctx.fillStyle = '#20232c'; ctx.fillRect(x, 520 - h, w, h); x += w + r() * 10; } hazeBand(ctx, 500, 80, 0.4); });
    withCam(ctx, c2, 1, () => {
      mudPlane(ctx, -900, 500, 3800, 900, 5, 0.45);
      // concrete mound with the steel door
      ctx.save(); ctx.translate(960, 820);
      ctx.save(); ctx.filter = 'blur(14px)'; ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.beginPath(); ctx.ellipse(80, 40, 420, 50, 0, 0, 7); ctx.fill(); ctx.restore();
      const cg = ctx.createLinearGradient(-320, 0, 320, 0); cg.addColorStop(0, '#5a5852'); cg.addColorStop(0.5, '#7a776e'); cg.addColorStop(1, '#3a3934');
      ctx.fillStyle = cg; ctx.beginPath(); ctx.moveTo(-340, 40); ctx.lineTo(-260, -420); ctx.lineTo(260, -420); ctx.lineTo(340, 40); ctx.closePath(); ctx.fill();
      ctx.fillStyle = 'rgba(0,0,0,0.25)'; for (let i = 0; i < 6; i++) ctx.fillRect(-300 + i * 110, -400 + (i % 2) * 40, 60, 4);
      // dark opening
      ctx.fillStyle = '#020203'; rr(ctx, -170, -370, 340, 410, 6); ctx.fill();
      // flashlight beam inside the gap
      const fl = sh.flashAt !== undefined ? so(T, sh.flashAt, sh.flashAt + 0.15) : 0;
      if (fl > 0) { ctx.save(); rr(ctx, -170, -370, 340, 410, 6); ctx.clip(); ctx.globalCompositeOperation = 'lighter';
        const bg = ctx.createRadialGradient(150, -120, 10, 150, -120, 260); bg.addColorStop(0, `rgba(255,240,200,${0.5 * fl})`); bg.addColorStop(1, 'rgba(255,240,200,0)'); ctx.fillStyle = bg; ctx.fillRect(-170, -370, 340, 410);
        for (let i = 0; i < 40; i++) { const r = mulberry32(i)(); ctx.fillStyle = `rgba(255,240,210,${0.2 * fl * r})`; ctx.fillRect(60 + ((i * 37 + T * 20 * r) % 160), -300 + ((i * 53 + T * 15) % 360), 2, 2); }
        ctx.restore(); }
      // door leaf (swings: narrower = more open)
      const dw = 340 * (1 - open * 0.32);
      const dg = ctx.createLinearGradient(-170, 0, -170 + dw, 0); dg.addColorStop(0, '#3a4048'); dg.addColorStop(0.5, '#6a727c'); dg.addColorStop(1, '#2a2f36');
      ctx.fillStyle = dg; rr(ctx, -170, -370, dw, 410, 6); ctx.fill();
      ctx.fillStyle = 'rgba(107,59,34,0.55)'; ctx.beginPath(); ctx.ellipse(-90, 0, 90, 40, 0, Math.PI, 0); ctx.fill(); ctx.beginPath(); ctx.ellipse(-170 + dw - 30, -200, 22, 120, 0, 0, 7); ctx.fill();
      for (let i = 0; i < 7; i++) { circ(ctx, -150, -350 + i * 62, 6, '#1a1d22'); circ(ctx, -170 + dw - 20, -350 + i * 62, 6, '#1a1d22'); }
      ctx.strokeStyle = '#1a1d22'; ctx.lineWidth = 12; ctx.beginPath(); ctx.arc(-170 + dw * 0.5, -170, 54 * (1 - open * 0.3), 0, 7); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-170 + dw * 0.5, -224); ctx.lineTo(-170 + dw * 0.5, -116); ctx.moveTo(-170 + dw * 0.5 - 54, -170); ctx.lineTo(-170 + dw * 0.5 + 54, -170); ctx.stroke();
      ctx.fillStyle = 'rgba(255,220,180,0.25)'; ctx.fillRect(-170, -370, 4, 410);
      // dust falling after a knock
      if (kick > 0) for (let i = 0; i < 30; i++) { const r = mulberry32(i + Math.floor(T * 3))(); ctx.fillStyle = `rgba(200,170,130,${0.5 * kick})`; ctx.fillRect(-300 + r * 600, -420 + (1 - kick) * 300 + r * 80, 3, 3); }
      ctx.restore();
      windDust(ctx, T, 960, 820, 3400, 400, 1, 3);
    });
    if (sh.hero) withCam(ctx, c2, 1.3, () => drawHeroBack(ctx, T, 560, 900, 1.2, { rimCol: 'rgba(230,190,150,0.6)', rimX: 4, rimY: -6 }));
    if (dark > 0) { ctx.fillStyle = `rgba(3,4,8,${0.55 * dark})`; ctx.fillRect(0, 0, W, H); }
    if (sh.hand) {      // phone flashlight in the hand (foreground)
      const fl = sh.flashAt !== undefined ? so(T, sh.flashAt, sh.flashAt + 0.15) : 0;
      ctx.save(); ctx.translate(1500, 1000); ctx.rotate(-0.5);
      ctx.fillStyle = '#0a0809'; rr(ctx, -80, 40, 160, 400, 60); ctx.fill(); rr(ctx, -70, -20, 140, 110, 40); ctx.fill();
      ctx.fillStyle = '#05060a'; rr(ctx, -50, -170, 100, 190, 14); ctx.fill();
      if (fl) { circ(ctx, -20, -150, 8, '#fff8e0'); glow(ctx, -20, -150, 80, 'rgba(255,245,210,0.8)', fl); }
      ctx.restore();
      if (fl) lightShaft(ctx, 1460, 840, 1070, 640, 10, 140, 0.18 * fl, '255,240,200');
    }
    if (sh.textAt !== undefined && T > sh.textAt) {
      const a = so(T, sh.textAt, sh.textAt + 0.8);
      ctx.fillStyle = `rgba(0,0,0,${0.35 * a})`; ctx.fillRect(0, 0, W, H);
      (sh.lines || []).forEach((l, i) => text(ctx, l, 960, 470 + i * 90, { font: font(900, 66), align: 'center', color: i === (sh.lines.length - 1) ? '#e2343e' : PAL.white, ls: 4, alpha: a, shadow: 'rgba(0,0,0,0.9)', blur: 30 }));
    }
  },

  // 12. phone in hand: notifications / emergency alert (background: dry riverbed or room)
  c_phone(ctx, T, sh) {
    const cam = camOf(sh, T);
    const scr = phoneScreen(sh.screen, T);
    const sk = shake(T, sh.hand ?? 3, 1.2, 2);
    withCam(ctx, cam, 0.6, () => {
      if (sh.bg === 'riverbed') { dawnSky(ctx, -600, 520, 0.8); mudPlane(ctx, -900, 500, 3800, 900, 5, 0.35); ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(-900, -900, 3800, 3000); }
      else { ctx.fillStyle = '#05070b'; ctx.fillRect(-900, -900, 3800, 3000); ctx.drawImage(ART.wall, -200, -100); drawWindow(ctx, T, 1300, 60, 520, 460, {}); morningWash(ctx, 1300, 60, 520, 460, 0.7); ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(-900, -900, 3800, 3000); }
    });
    withCam(ctx, cam, 1, () => {
      const red = sh.red !== undefined && T > sh.red ? so(T, sh.red, sh.red + 0.5) : 0;
      glow(ctx, 960, 540, 900, red ? 'rgba(230,80,90,0.4)' : 'rgba(140,170,240,0.35)', onLevel(sh, T) * 0.9);
      const vib = pulseAt(T, sh.vibAt, 1.0) ? shake(T, 4, 60, 4) : { x: 0, y: 0 };
      drawPhone(ctx, 960 + sk.x * 3 + vib.x, 560 + sk.y * 3 + vib.y, 0.8, -0.03 + sk.r * 8, scr, { on: onLevel(sh, T) });
      ctx.fillStyle = '#0a0809'; const fx = 960 + sk.x * 3, fy = 560 + sk.y * 3;
      for (let i = 0; i < 3; i++) { rr(ctx, fx + 182, fy + 50 + i * 76, 56, 64, 28); ctx.fill(); }
      rr(ctx, fx - 240, fy + 130, 64, 170, 32); ctx.fill(); ctx.beginPath(); ctx.ellipse(fx, fy + 610, 340, 210, 0, 0, 7); ctx.fill();
    });
    withCam(ctx, cam, 1.3, () => ctx.drawImage(SPR.fgHero, -520, 200, 900, 1100));
  },
};
Object.assign(GEN, CINE);

// TV picture (offscreen)
function tvScreen(T, sh) {
  if (!SCR.tv) SCR.tv = makeCanvas(1280, 720);
  const g = SCR.tv.getContext('2d');
  const bg = g.createLinearGradient(0, 0, 1280, 720); bg.addColorStop(0, '#0c2a52'); bg.addColorStop(1, '#061226'); g.fillStyle = bg; g.fillRect(0, 0, 1280, 720);
  // world map panel
  g.fillStyle = 'rgba(30,70,130,0.6)'; rr(g, 620, 60, 620, 380, 14); g.fill();
  const blobs = [[700, 170, 60, 40], [790, 150, 40, 60], [900, 210, 90, 50], [1040, 280, 60, 40], [780, 320, 40, 60], [1120, 150, 50, 30], [980, 360, 50, 40]];
  blobs.forEach(([x, y, rx, ry]) => { g.fillStyle = '#3d6a4a'; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 7); g.fill(); });
  if (sh.worldAt !== undefined) blobs.forEach(([x, y], i) => { const k = ramp(T, sh.worldAt + i * 0.25, sh.worldAt + i * 0.25 + 0.3); if (k > 0) { g.fillStyle = '#e2343e'; g.beginPath(); g.arc(x, y, 12 * k, 0, 7); g.fill(); const p = (T * 1.2 + i * 0.3) % 1; g.strokeStyle = `rgba(226,52,62,${1 - p})`; g.lineWidth = 3; g.beginPath(); g.arc(x, y, 12 + p * 50, 0, 7); g.stroke(); } });
  // anchor (studio silhouette, softly lit)
  g.fillStyle = '#121a2a'; g.beginPath(); g.moveTo(120, 720); g.quadraticCurveTo(130, 470, 300, 440); g.quadraticCurveTo(470, 470, 480, 720); g.fill();
  g.fillStyle = '#e8e8ea'; g.beginPath(); g.moveTo(270, 450); g.lineTo(300, 540); g.lineTo(330, 450); g.fill();
  g.fillStyle = '#b88a6a'; g.beginPath(); g.ellipse(300, 360, 70, 86, 0, 0, 7); g.fill();
  g.fillStyle = '#2a1c16'; g.beginPath(); g.ellipse(300, 320, 80, 64, 0, Math.PI, 0); g.fill(); g.fillRect(222, 320, 26, 110); g.fillRect(352, 320, 26, 110);
  g.fillStyle = '#3a2420'; g.beginPath(); g.ellipse(300, 410, 18, 4 + Math.abs(Math.sin(T * 11)) * 6, 0, 0, 7); g.fill();
  // banner + ticker
  g.fillStyle = '#c8323a'; g.fillRect(0, 560, 1280, 80);
  g.font = font(900, 46); g.fillStyle = '#fff'; g.fillText(sh.banner || 'BREAKING NEWS', 40, 616);
  g.fillStyle = '#05080f'; g.fillRect(0, 640, 1280, 80);
  g.font = font(700, 34); g.fillStyle = '#f2f2f2'; const tk = sh.ticker || ''; const tw = g.measureText(tk).width + 80;
  const off = ((T - sh.start) * 140) % tw; for (let k = 0; k < 4; k++) g.fillText(tk, 1280 - off + (k - 1) * tw, 692);
  g.fillStyle = 'rgba(255,255,255,0.04)'; for (let y = 0; y < 720; y += 4) g.fillRect(0, y, 1280, 1);
  return SCR.tv;
}

// character reference sheet (1920x1080)
window.renderCharacterSheet = (title, notes) => {
  const ctx = MAIN.getContext('2d'), T = 1.0;
  ctx.save(); ctx.fillStyle = '#0a0d14'; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(150,170,210,0.08)'; for (let x = 0; x < W; x += 60) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  text(ctx, title, 80, 110, { font: font(900, 54), color: PAL.white, ls: 4 });
  // back view
  ctx.save(); ctx.beginPath(); ctx.rect(60, 180, 520, 700); ctx.clip(); glow(ctx, 320, 400, 400, 'rgba(110,145,215,0.4)', 1); drawHeroBack(ctx, T, 320, 430, 1.25, { rimCol: 'rgba(150,180,235,0.95)' }); ctx.restore();
  // side profile
  ctx.save(); ctx.beginPath(); ctx.rect(640, 180, 560, 700); ctx.clip(); glow(ctx, 1000, 400, 400, 'rgba(255,210,170,0.35)', 1); drawHeroSide(ctx, T, 880, 400, 1.3, { rimCol: 'rgba(230,200,170,0.95)', rimX: 7, rimY: 2, lean: 0.04 }); ctx.restore();
  // sitting at the desk (as in episode 01)
  ctx.save(); ctx.beginPath(); ctx.rect(1260, 180, 600, 700); ctx.clip(); ctx.translate(1260, 180); ctx.scale(0.62, 0.62); ctx.translate(-500, -80);
  roomWide(ctx, T, { x: 960, y: 540, z: 1 }, { phoneOn: 0.5 }); ctx.restore();
  ['BACK', 'PROFILE', 'IN SCENE'].forEach((l, i) => text(ctx, l, [320, 920, 1560][i], 930, { font: font(800, 28), align: 'center', color: PAL.mist, ls: 8 }));
  notes.forEach((n, i) => text(ctx, '• ' + n, 80, 990 + i * 34, { font: font(500, 24), color: '#b9c2d0' }));
  [['#06070a', 'HAIR'], ['#10141d', 'SWEATER'], ['#0d0e13', 'SKIN (SHADOW)'], ['#c8323a', 'ACCENT']].forEach(([c, l], i) => { ctx.fillStyle = c; rr(ctx, 1260 + i * 160, 960, 60, 60, 8); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.3)'; ctx.stroke(); text(ctx, l, 1290 + i * 160, 1045, { font: font(600, 16), align: 'center', color: PAL.mist }); });
  ctx.restore();
  return MAIN.toDataURL('image/png');
};

// cinematic 9:16 thumbnail
window.renderThumbCine = (l1, l2, alert) => {
  const T = 3;
  const b = BUF.getContext('2d');
  b.save(); b.fillStyle = '#000'; b.fillRect(0, 0, W, H);
  CINE.c_door(b, T, { start: 0, end: 10, open: 1, hero: true, cam: [[960, 600, 0.95], [960, 600, 0.95]] });
  b.restore();
  const cv = makeCanvas(1080, 1920), ctx = cv.getContext('2d');
  const sc = 1920 / 1080; ctx.drawImage(BUF, 540 - 960 * sc, 0, 1920 * sc, 1920);
  const g = ctx.createLinearGradient(0, 0, 0, 1920); g.addColorStop(0, 'rgba(4,5,9,0.95)'); g.addColorStop(0.3, 'rgba(4,5,9,0.2)'); g.addColorStop(0.75, 'rgba(4,5,9,0.3)'); g.addColorStop(1, 'rgba(4,5,9,0.95)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920);
  text(ctx, 'WHAT IF…?', 540, 140, { font: font(900, 44), align: 'center', color: PAL.mist, ls: 12 });
  const fit = (str, max, w = 980) => { let sz = max; ctx.font = font(900, sz); while (ctx.measureText(str).width > w && sz > 30) { sz -= 4; ctx.font = font(900, sz); } return sz; };
  const s1 = fit(l1, 170), s2 = fit(l2, 96);
  text(ctx, l1, 540, 300, { font: font(900, s1), align: 'center', color: '#fff', shadow: 'rgba(0,0,0,0.9)', blur: 40 });
  text(ctx, l2, 540, 300 + s2 + 30, { font: font(900, s2), align: 'center', color: '#e2343e', shadow: 'rgba(0,0,0,0.9)', blur: 40 });
  // alert card
  ctx.save(); ctx.translate(540, 1640); ctx.rotate(-0.03);
  ctx.fillStyle = 'rgba(20,22,30,0.92)'; rr(ctx, -440, -110, 880, 220, 36); ctx.fill(); ctx.strokeStyle = '#e2343e'; ctx.lineWidth = 5; ctx.stroke();
  ctx.fillStyle = '#e2343e'; rr(ctx, -400, -70, 90, 90, 22); ctx.fill(); text(ctx, '⚠', -355, 2, { font: font(800, 56), align: 'center', color: '#fff' });
  ctx.font = font(900, 46); const lines = wrap(ctx, alert, 640);
  lines.forEach((ln, i) => text(ctx, ln, -280, -18 + i * 56, { font: font(900, 46), color: '#fff' }));
  ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.1; for (let y = 0; y < 1920; y += 384) for (let x = 0; x < 1080; x += 384) ctx.drawImage(FX.grain[1], x, y); ctx.restore();
  return cv.toDataURL('image/png');
};
