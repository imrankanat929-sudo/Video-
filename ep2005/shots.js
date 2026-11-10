// Episode 2 — «Ты проснулся в 2005 году». Shots timed to the narration.

function room05(t, mode = 'dawn', o = {}) {
  rect(-600, -400, 3200, 1160, NAVY);
  for (let x = -600; x < 2600; x += 160) rect(x, -400, 6, 1160, NAVY2);
  rect(-600, 740, 3200, 22, '#2f3a66');
  rect(-600, 760, 3200, 800, '#2a2346'); for (let i = 0; i < 20; i++) rect(-600, 790 + i * 36, 3200, 3, '#231d3c');
  ell(1000, 900, 700, 90, '#7a2a3e'); ell(1000, 900, 600, 70, '#8f3348');
  cityWindow(120, 150, 380, 390, t, mode);
  calendar2(600, 205, 0.42, '2005', o.back, o.flip, t);
  // shelf with CDs + camera
  rect(690, 270, 300, 14, '#4b3f6b'); for (let i = 0; i < 7; i++) rect(700 + i * 16, 200, 12, 70, ['#e8323c', YEL, '#3a8af2', '#fff', '#3ac85a', '#e8323c', '#888'][i]); digicam(930, 245, 0.45, 0);
  // poster
  rr(1500, 170, 240, 300, 6, '#3a1f5a'); circ(1620, 290, 70, YEL); poly([1620, 230, 1640, 280, 1690, 285, 1650, 315, 1665, 365, 1620, 335, 1575, 365, 1590, 315, 1550, 285, 1600, 280], RED); txt('РОК-ФЕСТ', 1620, 420, 34, '#fff', { w: 900 }); txt('2005', 1620, 452, 22, YEL, { w: 900 });
  // desk
  rect(575, 700, 22, 100, '#2f2748'); rect(1080, 700, 150, 100, '#3d3358'); rect(1095, 720, 120, 30, '#4b3f6b'); rect(1095, 760, 120, 30, '#4b3f6b');
  rect(560, 640, 670, 52, '#5a4c80'); rect(560, 690, 670, 14, '#3d3358');
  // CD stack
  for (let i = 0; i < 5; i++) rr(600, 628 - i * 12, 90, 11, 2, ['#9ab', '#e8323c', '#3a8af2', YEL, '#9ab'][i]);
  cd(645, 566, 36, t * (o.cdSpin || 0), t);
  crtMonitor(820, 646, 0.95, o.screen, t, !!o.screen);
  tower(1095, 646, 1.0, t, !!o.pcOn, o.press || 0);
  keyboard(820, 668, 0.55, t, o.typing ? 1 : 0); mouse(985, 668, 0.5, 0);
  push(1045, 668, -Math.PI / 2); phone05(0, 0, 0.14, t, 'home'); pop();
  // nightstand + clock + bed
  rect(1260, 690, 100, 110, '#3d3358'); rect(1252, 680, 116, 14, '#4b3f6b');
  alarmClock(1308, 628, 0.36, t, !!o.ring, o.hours);
  rr(1370, 520, 44, 290, 10, '#3d3358');
  rect(1410, 640, 640, 120, '#e9e6ef'); rect(1410, 760, 640, 40, '#3d3358');
}
function pillow05() { ell(1470, 640, 78, 34, '#f4f2f8'); ell(1470, 632, 64, 20, '#ffffff'); }
function blanket05(x0 = 1530, top = 615) {
  c.beginPath(); c.moveTo(x0, 780); c.lineTo(x0, top + 20); c.quadraticCurveTo(x0 + 40, top - 20, x0 + 140, top - 8); c.quadraticCurveTo(x0 + 300, top + 10, 2060, top + 12); c.lineTo(2060, 790); c.closePath();
  c.fillStyle = RED; c.fill(); c.save(); c.clip(); for (let x = x0; x < 2100; x += 70) rect(x, top - 40, 16, 400, 'rgba(120,10,30,.35)'); c.restore();
}
function heroLying05(expr) { push(1470 + 250, 610, -Math.PI / 2); person({ s: 0.5, expr, hideLegs: true, hl: [-70, -260], hr: [70, -260] }); pop(); blanket05(); }
function light(mode, t, a = 1) {
  if (mode === 'dawn') {
    alpha(0.2 * a, () => { c.fillStyle = grad(300, 150, 700, 900, [[0, '#ffd98a'], [1, 'rgba(255,217,138,0)']]); c.beginPath(); c.moveTo(120, 150); c.lineTo(500, 150); c.lineTo(1150, 1100); c.lineTo(450, 1100); c.closePath(); c.fill(); });
    for (let i = 0; i < 22; i++) { const r = rng(i + 40); alpha(0.45 * a * (0.5 + 0.5 * Math.sin(t * 2 + i)), () => circ(300 + r() * 650 + Math.sin(t * 0.4 + i) * 30, 300 + r() * 600, 2 + r() * 2, '#ffe9b0')); }
  }
  if (mode === 'evening') alpha(0.5 * a, () => rect(-600, -400, 3200, 2000, '#05071a'));
  if (mode === 'night') alpha(0.68 * a, () => rect(-600, -400, 3200, 2000, '#03040f'));
}
function popText(s, x, y, size, lt, col = YEL, sub) {
  if (VERT) size *= 0.7;
  const p = eo(prog(lt, 0, 0.35)); if (p <= 0) return;
  push(x, y, Math.sin(lt * 3) * 0.015, lerp(1.6, 1, p) * (1 + Math.sin(lt * 4) * 0.01));
  alpha(p, () => { txt(s, 6, 8, size, RED, { w: 900 }); txt(s, 0, 0, size, col, { w: 900, stroke: '#0d1230', sw: size * 0.14 }); if (sub) { rr(-c.measureText(sub).width / 2 - 20, -size * 0.95, 0, 0, 0); const tw = sub.length * size * 0.18 + 30; rr(-tw / 2, -size * 0.98, tw, size * 0.32, 8, '#2a6ae8'); txt(sub, 0, -size * 0.82, size * 0.2, '#fff', { w: 900 }); } });
  pop();
}
function monitorClose(screen, t, lt, z0 = 1.0, z1 = 1.12) {
  cam(eio(prog(lt, 0, 4)), [960, 560, z0], [960, 540, z1], 1, t);
  rect(-600, -400, 3200, 2000, NAVY);
  for (let x = -600; x < 2600; x += 160) rect(x, -400, 6, 2000, NAVY2);
  rect(-600, 900, 3200, 600, '#5a4c80');
  crtMonitor(960, 940, 3.0, screen, t, true);
  alpha(0.35, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(960, 480, 30, 1100, [[0, 'rgba(110,160,255,.4)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
}

const S = [];
function shot(t0, t1, draw, o = {}) { S.push(Object.assign({ t0, t1, draw, fade: 0.3 }, o)); }

// ===== SCENE 1 — ПРОБУЖДЕНИЕ =====
shot(0, 2.9, (lt, t) => {
  cam(eio(prog(lt, 0, 3)), [1300, 560, 1.15], [1400, 590, 1.45], 1, t);
  room05(t, 'dawn', { ring: lt < 2.3 }); pillow05(); heroLying05(lt < 2.0 ? 'closed' : 'sleepy');
  light('dawn', t);
  if (lt < 2.3) for (let i = 0; i < 3; i++) { const p = (lt * 2 + i / 3) % 1; c.beginPath(); c.arc(1308, 600, 30 + p * 80, -2.4, -0.7); c.strokeStyle = `rgba(255,201,58,${1 - p})`; c.lineWidth = 6; c.stroke(); }
});
shot(2.9, 4.3, (lt, t) => {
  cam(eio(prog(lt, 0, 1.4)), [1500, 430, 1.9], [1480, 410, 2.2], 1, t);
  room05(t, 'dawn'); pillow05();
  const up = eo(prog(lt, 0, 0.5));
  person({ x: 1540, y: 760 + (1 - up) * 160, s: 0.8, hideLegs: true, expr: lt > 0.6 ? 'surprised' : 'sleepy', look: [-14, -4], tilt: -0.08 * up });
  blanket05(1410, 640);
  light('dawn', t, 0.7);
});
shot(4.3, 5.85, (lt, t) => {
  cam(eio(prog(lt, 0, 1.6)), [960, 560, 1.0], [960, 500, 1.2], 1, t);
  rect(-600, -400, 3200, 2000, NAVY); for (let x = -600; x < 2600; x += 160) rect(x, -400, 6, 2000, NAVY2);
  calendar2(VERT ? 960 : 640, 210, 1.9, '2005', null, 0, t);
  popText('2005 ГОД', VERT ? 960 : 1320, VERT ? 70 : 560, 130, lt - 0.1, YEL);
}, { fade: 0.15 });
shot(5.85, 8.7, (lt, t) => {
  cam(eio(prog(lt, 0, 2.9)), [1300, 470, 1.6], [760, 480, 1.6], 2, t);
  room05(t, 'dawn'); pillow05(); blanket05(1410, 640); light('dawn', t, 0.8);
});
shot(8.7, 9.95, (lt, t) => {
  cam(eo(prog(lt, 0, 1.3)), [960, 540, 1.0, -0.03], [960, 540, 1.12, 0.02], 1, t);
  rect(-600, -400, 3200, 2000, '#5a4c80');
  [['#e8323c', 'ГОНКИ'], ['#2a6ae8', 'СТРАТЕГИЯ'], [YEL, 'ШУТЕР'], ['#3ac85a', 'КВЕСТ']].forEach(([col, l], i) => jewelCase(560 + i * 270, 760 + (i % 2) * 30, 230, col, l, -0.1 + i * 0.07));
  cd(960, 420, 260, t * 1.5, t);
  popText('ДИСКИ С ИГРАМИ', 960, 215, 70, lt - 0.2, '#fff');
});
shot(9.95, 11.45, (lt, t) => {
  cam(eo(prog(lt, 0, 1.5)), [960, 560, 1.05], [960, 540, 1.2], 1, t);
  rect(-600, -400, 3200, 2000, '#5a4c80');
  const vib = lt > 0.3 && lt < 1.1 ? Math.sin(t * 80) * 0.03 : 0;
  phone05(960, 560, 1.7, t, lt > 0.3 ? 'ring' : 'home', vib);
  if (lt > 0.3 && lt < 1.1) [-1, 1].forEach(sd => { for (let i = 0; i < 2; i++) line(960 + sd * (190 + i * 30), 300, 960 + sd * (190 + i * 30), 420, YEL, 6); });
});
shot(11.45, 14.35, (lt, t) => {
  cam(eio(prog(lt, 0, 2.9)), [960, 500, 1.35], [960, 470, 1.6], 1, t);
  room05(t, 'dawn');
  person({ x: 960, y: 1020, s: 0.95, expr: 'smile', blink: blinkAt(lt), hl: [-170 - Math.sin(lt * 3) * 10, -520], hr: [170 + Math.sin(lt * 3) * 10, -520] });
  light('dawn', t, 0.8);
  popText('2005 ГОД', 960, 340, 120, lt - 0.9, YEL, 'ДОБРО ПОЖАЛОВАТЬ');
});

// ===== SCENE 2 — КОМПЬЮТЕР =====
shot(14.35, 15.8, (lt, t) => {
  const hx = lerp(1400, 1040, eio(prog(lt, 0, 1.4)));
  cam(0, [hx - 120, 520, 1.3], [hx - 120, 520, 1.3], 1, t);
  room05(t, 'day'); pillow05(); blanket05(1410, 640);
  person({ x: hx, y: 990, s: 0.7, view: 'side', dir: -1, walk: lt < 1.35 ? lt * 9 : null, blink: blinkAt(lt) });
});
shot(15.8, 17.6, (lt, t) => {
  cam(eo(prog(lt, 0, 1.8)), [960, 560, 1.0], [960, 540, 1.15], 1, t);
  rect(-600, -400, 3200, 2000, NAVY);
  rect(-600, 940, 3200, 500, '#5a4c80');
  const press = lt > 0.7 && lt < 1.0 ? 1 : 0;
  tower(760, 960, 3.0, t, lt > 0.95, press);
  const hp = eo(prog(lt, 0.2, 0.75));
  line(1500, 1300, lerp(1500, 940, hp), lerp(1300, 620, hp), HERO.c1, 120); circ(lerp(1500, 940, hp), lerp(1300, 620, hp), 56, HERO.skin);
  line(lerp(1500, 940, hp) - 30, lerp(1300, 620, hp) - 30, lerp(1500, 940, hp) - 70 + press * 6, lerp(1300, 620, hp) - 58 + press * 6, HERO.skin, 30);
  if (lt > 0.95) popText('ВКЛ', 1450, 300, 90, lt - 0.95, '#4ade6a');
});
shot(17.6, 19.5, (lt, t) => monitorClose(lt < 0.9 ? (w, h) => scrBios(w, h, lt) : (w, h) => scrXPBoot(w, h, lt - 0.9), t, lt));
shot(19.5, 21.8, (lt, t) => { monitorClose(lt < 0.8 ? (w, h) => scrXPBoot(w, h, lt + 1) : scrDesktop, t, lt, 1.12, 1.0); if (lt > 0.85) popText('WINDOWS XP', 960, 240, 90, lt - 0.85, '#fff'); });
shot(21.8, 23.75, (lt, t) => monitorClose((w, h) => scrDialup(w, h, lt), t, lt, 1.05, 1.3));
shot(23.75, 25.75, (lt, t) => {
  cam(eio(prog(lt, 0, 2)), [960, 600, 1.0], [960, 560, 1.15], 1, t);
  rect(-600, -400, 3200, 2000, NAVY); for (let x = -600; x < 2600; x += 160) rect(x, -400, 6, 2000, NAVY2);
  rect(-600, 760, 3200, 700, '#5a4c80');
  keyboard(860, 860, 2.2, t, 1);
  const tap = Math.floor(t * 6) % 2;
  [-1, 1].forEach(sd => { line(860 + sd * 260, 1300, 860 + sd * 200, 900, HERO.c1, 110); circ(860 + sd * 200, 880 - (sd > 0 ? tap : 1 - tap) * 14, 52, HERO.skin); });
  mouse(1480, 880, 2.0, Math.floor(t * 3) % 2);
  push(1480, 140); rr(-170, -60, 340, 120, 20, '#fff'); txt('ЖДЁМ...', -40, 0, 46, '#1a2340', { w: 900 }); push(110, 0, t * 3); poly([-14, -20, 14, -20, 0, 0], NAVY); poly([-14, 20, 14, 20, 0, 0], NAVY); pop(); pop();
});

// ===== SCENE 3 — ТЕЛЕФОН И МУЗЫКА =====
shot(25.75, 28.2, (lt, t) => {
  cam(eio(prog(lt, 0, 2.4)), [960, 520, 1.4], [960, 470, 1.7], 1, t);
  room05(t, 'day');
  const up = eo(prog(lt, 0.3, 1.0));
  person({ x: 960, y: 1030, s: 0.95, expr: lt > 1 ? 'smile' : 'neutral', blink: blinkAt(lt), look: [0, 10], hr: [lerp(110, 50, up), lerp(-190, -330, up)] });
  const px = 960 + lerp(110, 50, up) * 0.95, py = 1030 + lerp(-190, -330, up) * 0.95;
  phone05(px, py - 50, 0.32, t, 'home'); circ(px, py, 22, HERO.skin);
});
shot(28.2, 30.3, (lt, t) => {
  cam(eo(prog(lt, 0, 2)), [960, 560, 1.0], [960, 540, 1.15], 1, t);
  rect(-600, -400, 3200, 2000, NAVY3);
  phone05(VERT ? 800 : 760, 560, VERT ? 1.3 : 1.75, t, 'home', -0.08);
  push(VERT ? 1180 : 1380, VERT ? 420 : 470); if (VERT) c.scale(0.7, 0.7); alpha(eo(prog(lt, 0.3, 0.6)), () => { rr(-110, -200, 220, 400, 30, '#111'); rr(-96, -180, 192, 350, 8, '#2a4a8a'); line(-160, -230, 160, 230, RED, 22); line(160, -230, -160, 230, RED, 22); }); pop();
  popText('НИКАКИХ СЕНСОРОВ', VERT ? 960 : 1380, VERT ? 60 : 770, 54, lt - 0.6, '#fff');
});
shot(30.3, 33.85, (lt, t) => {
  cam(eio(prog(lt, 0, 3.5)), [960, 560, 1.1, 0.03], [960, 480, 1.35, -0.02], 1, t);
  rect(-600, -400, 3200, 2000, NAVY3);
  const key = lt > 1.3 && lt < 2.4 ? [4, 1, 7, 5][Math.floor(lt * 4) % 4] : -1;
  phone05(960, 600, 1.75, t, lt < 1.3 ? 'menu' : 'ring', 0, key);
  if (lt > 1.4) notes(960, 300, t, 6, 600, YEL);
});
shot(33.85, 35.55, (lt, t) => {
  cam(eio(prog(lt, 0, 1.7)), [960, 470, 1.6], [960, 440, 1.8], 1, t);
  room05(t, 'day');
  person({ x: 900, y: 1040, s: 0.95, expr: 'smile', look: [10, -10], blink: blinkAt(lt), hr: [60, -470], tilt: 0.06 });
  alpha(eo(prog(lt, 0.2, 0.5)), () => { push(1250, 300); ell(0, 0, 150, 110, '#fff'); circ(-150, 110, 22, '#fff'); circ(-185, 145, 11, '#fff'); txt('♫ ?', 0, 0, 90, NAVY, { w: 900, f: 'DejaVu Sans' }); pop(); });
}, { v: { x: 1050 } });
shot(35.55, 37.3, (lt, t) => {
  cam(eo(prog(lt, 0, 1.7)), [960, 560, 1.0], [960, 540, 1.15], 1, t);
  rect(-600, -400, 3200, 2000, '#2a6ae8'); for (let i = 0; i < 16; i++) { const a = i / 16 * TAU + t * 0.2; alpha(0.12, () => poly([960, 540, 960 + Math.cos(a) * 2400, 540 + Math.sin(a) * 2400, 960 + Math.cos(a + 0.15) * 2400, 540 + Math.sin(a + 0.15) * 2400], '#fff')); }
  const rise = eo(prog(lt, 0, 0.6));
  mp3(960, 560 + (1 - rise) * 600, 2.2, t, lt > 1.0);
  earbudWire(960, 560 + 340 + (1 - rise) * 600, 1500, 1300);
  popText('MP3-ПЛЕЕР', 960, 215, 80, lt - 0.5, YEL);
});
shot(37.3, 40.15, (lt, t) => {
  cam(eio(prog(lt, 0, 2.8)), [960, 470, 1.55], [960, 430, 1.85], 1, t);
  rect(-600, -400, 3200, 2000, NAVY); for (let i = 0; i < 10; i++) circ(200 + i * 180, 200 + Math.sin(t * 2 + i) * 60, 40 + (i % 3) * 20, `rgba(255,201,58,${0.08 + 0.05 * Math.sin(t * 3 + i)})`);
  const on = lt > 0.45;
  person({ x: 960, y: 1040, s: 0.95, expr: on ? 'happy' : 'smile', tilt: on ? Math.sin(t * 8.4) * 0.05 : 0, hl: on ? [-110, -190] : [-120, -470], hr: on ? [110, -190] : [120, -470] });
  const hx = 960, hy = 1040 - 495 * 0.95;
  [-1, 1].forEach(sd => { circ(hx + sd * 96, hy + 30, 14, '#f2f2f2'); c.beginPath(); c.moveTo(hx + sd * 96, hy + 40); c.quadraticCurveTo(hx + sd * 60, hy + 200, hx, hy + 330); c.strokeStyle = '#f2f2f2'; c.lineWidth = 4; c.stroke(); });
  if (on) notes(960, 330, t, 7, 800, YEL);
});

// ===== SCENE 4 — УЛИЦА =====
shot(40.15, 42.15, (lt, t) => {
  cam(eio(prog(lt, 0, 2)), [960, 560, 1.1], [960, 600, 1.2], 1, t);
  cityDay(t);
  rect(200, -400, 1520, 1200, '#3a4570'); for (let y = -400; y < 800; y += 70) rect(200, y, 1520, 3, '#2f3a62');
  rect(700, 240, 520, 36, '#26305a'); rect(780, 276, 360, 524, '#10162e');
  rr(1170, 420, 60, 110, 6, '#c9ccd4'); for (let i = 0; i < 9; i++) rr(1180 + (i % 3) * 16, 450 + Math.floor(i / 3) * 18, 12, 12, 2, '#888'); rect(1180, 428, 40, 14, '#4ade6a');
  const open = eo(prog(lt, 0, 0.5)) * (1 - eio(prog(lt, 1.5, 1.95)));
  const hp = eo(prog(lt, 0.15, 1.95));
  person({ x: 960, y: lerp(800, 1180, hp), s: lerp(0.62, 1.05, hp), walk: lt * 8, expr: 'smile', blink: blinkAt(lt) });
  const hy = lerp(800, 1180, hp) - 495 * lerp(0.62, 1.05, hp);
  push(780, 276); c.scale(1 - open * 0.85, 1); rect(0, 0, 360, 524, '#5a6488'); rect(20, 20, 320, 484, '#6a7498'); circ(320, 270, 12, '#ccc'); pop();
  txt('ПОДЪЕЗД 2', 960, 180, 34, '#fff', { w: 800 });
});
shot(42.15, 44.7, (lt, t) => {
  cam(eio(prog(lt, 0, 2.5)), [800, 560, 1.05], [1150, 560, 1.05], 1, t);
  cityDay(t);
  rect(-600, 760, 3400, 60, '#8a8fa0'); rect(-600, 820, 3400, 200, '#3a3d4a'); for (let x = -600; x < 2800; x += 160) rect(x, 915, 80, 10, '#e8e2d0'); rect(-600, 1020, 3400, 300, '#8a8fa0');
  car05(((t * 430) % 3400) - 700, 905, 0.85, '#c9ccd4', t, 1, 0);
  car05(2600 - ((t * 380 + 1200) % 3400), 1005, 0.95, '#2a5ac8', t, -1, 1);
  car05(((t * 300 + 1600) % 3400) - 700, 905, 0.85, '#1a1a20', t, 1, 0);
  car05(2600 - ((t * 350 + 300) % 3400), 1005, 0.95, YEL, t, -1, 0);
  popText('СЕРЕДИНА 2000-Х', 960 + lerp(-160, 190, eio(prog(lt, 0, 2.5))), 250, 70, lt - 0.9, '#fff');
});
shot(44.7, 47.0, (lt, t) => {
  cam(eio(prog(lt, 0, 2.3)), [1100, 520, 1.1], [820, 520, 1.1], 1, t);
  cityDay(t); rect(-600, 760, 3400, 600, '#8a8fa0');
  shop05(-100, 760, 520, 420, 'САЛОН СВЯЗИ', RED, t, (x, y, w, h) => { for (let i = 0; i < 4; i++) phone05(x + 70 + i * 110, y + h / 2, 0.28, t, 'home'); });
  shop05(480, 760, 520, 420, 'DVD ПРОКАТ', '#2a6ae8', t, (x, y, w, h) => { for (let i = 0; i < 6; i++) rr(x + 20 + i * 76, y + 40, 60, 90, 4, [YEL, RED, '#3ac85a', '#fff', '#8a3ac8', '#2a6ae8'][i]); });
  shop05(1060, 760, 520, 420, 'ФОТО ЗА 1 ЧАС', '#3ac85a', t, (x, y, w, h) => { digicam(x + 120, y + 120, 1.2, 0); digicam(x + 340, y + 140, 1.0, 0); });
  billboard(1660, 300, 560, 300, t, (w, h) => { c.fillStyle = grad(0, 0, w, 0, [[0, YEL], [1, '#ff8a3a']]); c.fillRect(0, 0, w, h); txt('НОВЫЙ ТАРИФ!', w / 2, 60, 46, RED, { w: 900 }); txt('SMS — 1 рубль', w / 2, 130, 40, NAVY, { w: 900 }); phone05(w - 70, h - 90, 0.3, t, 'home'); });
  for (let i = 0; i < 5; i++) { const dir = i % 2 ? 1 : -1; const x = dir > 0 ? ((t * 160 + i * 500) % 2800) - 400 : 2400 - ((t * 160 + i * 500) % 2800); extra(i, { x, y: 1060, s: 0.6, view: 'side', dir, walk: t * 8 + i, blink: blinkAt(t, i) }); }
});
shot(47.0, 49.35, (lt, t) => {
  cam(eio(prog(lt, 0, 2.3)), [960, 560, 1.25], [960, 540, 1.1], 1, t);
  cityDay(t); rect(-600, 760, 3400, 600, '#8a8fa0');
  // tourist with camera
  extra(7, { x: 560, y: 1060, s: 0.8, hr: [60, -420], hl: [-60, -420], expr: 'smile' });
  const fl = (lt % 1.1) < 0.12 ? 1 - (lt % 1.1) / 0.12 : 0;
  digicam(560, 1060 - 0.8 * 440, 0.9, fl);
  // teens with flip phones
  extra(0, { x: 1150, y: 1060, s: 0.75, hair: 'short', hairCol: '#3a2a1e', expr: 'smile', look: [0, 12], hr: [40, -330] }); flipPhone(1150 + 30, 1060 - 0.75 * 360, 0.9);
  extra(2, { x: 1450, y: 1060, s: 0.75, hair: 'long', hairCol: '#6a3a1a', expr: 'happy', hr: [60, -470], blink: blinkAt(t, 2) }); flipPhone(1450 + 45, 1060 - 0.75 * 500, 0.8, '#e05a8a');
  person({ x: 900, y: 1080, s: 0.9, expr: 'surprised', look: [Math.sin(t * 2) * 10, 0], blink: blinkAt(lt), headphones: false });
});

// ===== SCENE 5 — КОМПЬЮТЕРНЫЙ КЛУБ =====
shot(49.35, 52.95, (lt, t) => {
  cam(eio(prog(lt, 0, 3.6)), [960, 540, 1.05], [1100, 540, 1.15], 1, t);
  c.fillStyle = grad(0, -400, 0, 800, [[0, '#2a2458'], [1, '#ff9a6a']]); c.fillRect(-1500, -1500, 5000, 4000);
  rect(-600, 760, 3400, 600, '#5a5a78');
  rect(900, 100, 900, 700, '#232c5a'); rr(960, 140, 780, 110, 16, null, '#ff3a8a', 8); txt('КОМПЬЮТЕРНЫЙ КЛУБ', 1350, 195, 48, '#ff7ab0', { w: 900 });
  rect(1240, 400, 220, 360, '#10162e'); alpha(0.4, () => rect(1240, 400, 220, 360, '#3a8af2'));
  extra(0, { x: 560, y: 1000, s: 0.68, view: 'side', dir: 1, expr: 'happy', blink: blinkAt(t, 1) });
  extra(1, { x: 780, y: 1000, s: 0.68, hair: 'cap', hairCol: '#1d1d24', expr: 'smile', blink: blinkAt(t, 3) });
  const point = eo(prog(lt, 1.6, 2.0));
  person({ x: 300, y: 1000, s: 0.7, view: 'side', dir: 1, expr: 'smile', hr: [lerp(20, 190, point), lerp(-200, -420, point)], blink: blinkAt(lt) });
}, { v: { x: 560 } });
shot(52.95, 55.05, (lt, t) => {
  cam(eio(prog(lt, 0, 2.1)), [700, 560, 1.0], [1200, 560, 1.0], 1, t);
  club(t);
  for (let i = 0; i < 5; i++) station(200 + i * 480, 640, 0.7, t, [scrShooter, scrBrowser, scrShooter, scrChat, scrShooter][i], i, { s: 0.78 });
  for (let i = 0; i < 4; i++) station(440 + i * 480, 960, 1.0, t, [scrShooter, scrChat, scrShooter, scrBrowser][i], i + 5);
});
shot(55.05, 56.95, (lt, t) => { monitorClose(scrShooter, t, lt, 1.0, 1.15); popText('COUNTER-STRIKE', 960, 240, 64, lt - 0.6, YEL); });
shot(56.95, 58.55, (lt, t) => { monitorClose((w, h) => scrBrowser(w, h, lt * 2), t, lt, 1.15, 1.0); popText('ИНТЕРНЕТ', 960, 240, 64, lt - 0.3, '#fff'); });
shot(58.55, 60.35, (lt, t) => {
  cam(eio(prog(lt, 0, 1.8)), [960, 520, 1.2], [960, 500, 1.35], 1, t);
  club(t);
  station(600, 700, 1.0, t, scrShooter, 1);
  station(1320, 700, 1.0, t, (w, h) => scrChat(w, h, lt), -1, { headphones: false, tilt: Math.sin(t * 2) * 0.03, hl: [-60, -260], hr: [lerp(60, 70, Math.floor(t * 4) % 2), -250] });
  if (lt > 0.6) alpha(prog(lt, 0.6, 0.9), () => { push(960, 420); rr(-210, -60, 420, 120, 30, '#fff'); txt('ХА-ХА! :D', 0, 0, 56, RED, { w: 900 }); pop(); });
}, { v: { k: 0.95, x: 960 } });

// ===== SCENE 6 — ВЕЧЕР =====
shot(60.35, 62.3, (lt, t) => {
  cam(eio(prog(lt, 0, 2)), [960, 520, 1.0], [960, 560, 1.12], 1, t);
  c.fillStyle = grad(0, -400, 0, 800, [[0, '#15123a'], [1, '#d8607a']]); c.fillRect(-1500, -1500, 5000, 4000);
  const lp = prog(lt, 0, 1.8);
  rect(150, 80, 1620, 820, '#1e2448'); for (let r = 0; r < 10; r++) for (let k = 0; k < 20; k++) rect(185 + k * 79, 110 + r * 76, 36, 44, hash(r * 31 + k * 7) < lp * 0.7 ? YEL : '#2a3360');
  rect(-600, 900, 3200, 600, '#22243a'); rect(860, 760, 200, 140, '#10162e');
  [300, 1620].forEach(x => { line(x, 1000, x, 640, '#333', 10); line(x, 640, x + 60, 630, '#333', 8); alpha(0.9, () => { c.fillStyle = rgrad(x + 60, 645, 5, 260, [[0, 'rgba(255,201,58,.6)'], [1, 'rgba(255,201,58,0)']]); c.fillRect(x - 300, 400, 720, 700); }); });
  person({ x: lerp(300, 900, eo(prog(lt, 0, 1.9))), y: 1000, s: 0.36, view: 'side', dir: 1, walk: lt * 9 });
});
shot(62.3, 65.85, (lt, t) => {
  cam(eio(prog(lt, 0, 3.5)), [900, 560, 1.15], [760, 560, 1.35], 1, t);
  rect(-600, -400, 3200, 1160, NAVY); for (let x = -600; x < 2600; x += 160) rect(x, -400, 6, 1160, NAVY2);
  rect(-600, 760, 3200, 800, '#2a2346');
  cityWindow(1450, 160, 330, 340, t, 'evening');
  rect(260, 640, 520, 160, '#3d3358'); rect(250, 630, 540, 18, '#4b3f6b'); rr(330, 670, 380, 40, 6, '#1d1d24'); txt('DVD', 380, 690, 18, '#888', { w: 900 }); circ(680, 690, 5, '#4ade6a');
  const on = lt > 0.35;
  tv2005(300, 300, 440, lt < 0.8 ? (w, h, tt) => staticFill(0, 0, w, h, tt, 1) : scrTV05, t, on);
  rr(1000, 700, 640, 120, 30, '#5a2a4a'); rr(1000, 620, 640, 100, 30, '#6a3358');
  light('evening', t, prog(lt, 0, 3.5));
  if (on) { const fl = 0.7 + 0.3 * Math.sin(t * 13) * Math.sin(t * 7); alpha(fl, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(520, 470, 20, 900, [[0, 'rgba(120,150,255,.5)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); }); tv2005(300, 300, 440, lt < 0.8 ? (w, h, tt) => staticFill(0, 0, w, h, tt, 1) : scrTV05, t, on); }
  person({ x: 1250, y: 860, s: 0.72, view: 'side', dir: -1, sit: true, fl: [110, -14], fr: [95, -14], expr: 'smile', blink: blinkAt(lt), hr: lt < 0.4 ? [140, -300] : [60, -150] });
  if (lt < 0.5) { push(1250 - 0.72 * 140, 860 - 0.72 * 230 + 70 * 0.72); rr(-14, -30, 28, 60, 8, '#222'); circ(0, -18, 5, RED); pop(); }
}, { v: { k: 0.9, x: 770 } });
shot(65.85, 68.55, (lt, t) => {
  cam(eio(prog(lt, 0, 2.7)), [960, 600, 1.55], [960, 580, 1.85], 1, t);
  rect(-600, -400, 3200, 2000, '#0d1230');
  person({ x: 960, y: 1080, s: 0.95, expr: 'neutral', look: [-12, 0], blink: blinkAt(lt) });
  const fl = 0.6 + 0.4 * Math.sin(t * 11) * Math.sin(t * 5.3);
  alpha(0.4 * fl, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(300, 500, 30, 900, [[0, '#7aa0ff'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
});
shot(68.55, 71.05, (lt, t) => {
  cam(eio(prog(lt, 0, 2.5)), [1300, 450, 1.5], [1400, 380, 1.75], 1, t);
  room05(t, 'night'); pillow05();
  light('night', t);
  alpha(0.5, () => { c.fillStyle = rgrad(310, 240, 10, 500, [[0, 'rgba(200,210,255,.4)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
  person({ x: 1540, y: 760, s: 0.8, hideLegs: true, expr: lt > 1.4 ? 'smile' : 'neutral', look: [-16, -10], blink: blinkAt(lt) });
  blanket05(1410, 640);
  for (let i = 0; i < 6; i++) alpha(0.5 + 0.5 * Math.sin(t * 3 + i), () => txt('✦', 1250 + i * 70, 200 + Math.sin(i) * 60, 30, YEL, { w: 400, f: 'DejaVu Sans' }));
});

// ===== SCENE 7 — 2010 =====
shot(71.05, 72.45, (lt, t) => {
  cam(eio(prog(lt, 0, 1.4)), [1450, 560, 1.6], [1450, 590, 1.9], 1, t);
  room05(t, 'night'); pillow05(); heroLying05('closed'); light('night', t, 1.1);
  for (let i = 0; i < 3; i++) { const p = (lt * 0.6 + i / 3) % 1; alpha(1 - p, () => txt('z', 1500 + p * 120, 520 - p * 160, 40 + p * 30, YEL, { w: 900 })); }
});
shot(72.45, 74.55, (lt, t) => {
  cam(eio(prog(lt, 0, 2)), [960, 540, 1.0], [960, 540, 1.25, 0.05], 2, t);
  const p = prog(lt, 0, 2);
  rect(-600, -400, 3200, 2000, p < 0.5 ? '#0d1230' : '#2a6ae8');
  alpha(Math.abs(Math.sin(p * Math.PI)), () => rect(-600, -400, 3200, 2000, '#3a2a6a'));
  alarmClock(960, 560, 2.3, t, false, 23 + p * 8);
  for (let i = 0; i < 10; i++) { const a = i / 10 * TAU + t; line(960 + Math.cos(a) * 320, 560 + Math.sin(a) * 320, 960 + Math.cos(a) * 520, 560 + Math.sin(a) * 520, 'rgba(255,201,58,.35)', 6); }
}, { fade: 0.15 });
shot(74.55, 77.35, (lt, t) => {
  cam(eio(prog(lt, 0, 2.8)), [960, 560, 1.0], [960, 500, 1.2], 1, t);
  rect(-600, -400, 3200, 2000, NAVY); for (let x = -600; x < 2600; x += 160) rect(x, -400, 6, 2000, NAVY2);
  const f = eio(prog(lt, 0.2, 0.9));
  calendar2(VERT ? 960 : 640, 210, 1.9, '2005', '2010', f, t);
  if (lt > 0.9) popText('2010 ГОД', VERT ? 960 : 1320, VERT ? 70 : 560, 120, lt - 0.9, YEL);
}, { fade: 0.2 });
shot(77.35, 80.2, (lt, t) => {
  cam(eio(prog(lt, 0, 2.9)), [960, 560, 1.0], [960, 540, 1.1], 1, t);
  rect(-600, -400, 3200, 2000, NAVY); for (let i = 0; i < 16; i++) { const a = i / 16 * TAU + t * 0.15; alpha(0.07, () => poly([960, 500, 960 + Math.cos(a) * 2400, 500 + Math.sin(a) * 2400, 960 + Math.cos(a + 0.15) * 2400, 500 + Math.sin(a + 0.15) * 2400], YEL)); }
  const a1 = eo(prog(lt, 0.1, 0.6)), a2 = eo(prog(lt, 0.4, 0.9));
  alpha(a1, () => laptop10(540, 640 + (1 - a1) * 300, 1.0, t));
  alpha(a2, () => smart10(1400, 560 + (1 - a2) * 300, 1.25, t));
  person({ x: 960, y: 1180, s: 0.9, expr: 'surprised', look: [Math.sin(t * 2.5) * 14, -6], blink: blinkAt(lt), sweat: true });
}, { v: { k: 0.9 } });
shot(80.2, 90.5, (lt, t) => {
  c.fillStyle = grad(0, 0, 0, H, [[0, '#0d1230'], [1, '#2a1550']]); c.fillRect(0, 0, W, H);
  if (VERT) {
    for (let i = 0; i < 14; i++) { const a = i / 14 * TAU + t * 0.08; alpha(0.06, () => poly([540, 760, 540 + Math.cos(a) * 2400, 760 + Math.sin(a) * 2400, 540 + Math.cos(a + 0.12) * 2400, 760 + Math.sin(a + 0.12) * 2400], YEL)); }
    const b1 = eo(prog(lt, 0.1, 0.6)), b2 = eo(prog(lt, 0.5, 1.0));
    push(540, 360, 0, lerp(1.3, 1, b1)); alpha(b1, () => { txt('СЛЕДУЮЩАЯ', 0, 0, 104, '#fff', { w: 900 }); txt('ОСТАНОВКА —', 0, 120, 104, '#fff', { w: 900 }); }); pop();
    push(540, 820, 0, lerp(1.6, 1, b2) * (1 + Math.sin(t * 3) * 0.01));
    alpha(b2, () => { [['2010', -110, 300], ['ГОД', 170, 230]].forEach(([s2, y, sz]) => { txt(s2, 10, y + 12, sz, RED, { w: 900 }); txt(s2, 0, y, sz, YEL, { w: 900, stroke: '#0d1230', sw: sz * 0.11 }); }); });
    pop();
    alpha(prog(lt, 1.2, 1.6), () => { laptop10(250, 1880, 0.5, t); smart10(860, 1820, 0.6, t); person({ x: 540, y: 2050, s: 0.7, expr: 'surprised', blink: blinkAt(lt), look: [Math.sin(t * 2) * 12, -6] }); });
    alpha(prog(lt, 9.6, 10.2), () => rect(0, 0, W, H, '#000'));
    return;
  }
  if (!VERT) for (let i = 0; i < 14; i++) { const a = i / 14 * TAU + t * 0.08; alpha(0.06, () => poly([960, 470, 960 + Math.cos(a) * 2400, 470 + Math.sin(a) * 2400, 960 + Math.cos(a + 0.12) * 2400, 470 + Math.sin(a + 0.12) * 2400], YEL)); }
  const a1 = eo(prog(lt, 0.1, 0.6)), a2 = eo(prog(lt, 0.5, 1.0));
  push(960, 300, 0, lerp(1.3, 1, a1)); alpha(a1, () => txt('СЛЕДУЮЩАЯ ОСТАНОВКА —', 0, 0, 92, '#fff', { w: 900, ls: 2 })); pop();
  push(960, 500, 0, lerp(1.6, 1, a2) * (1 + Math.sin(t * 3) * 0.01));
  alpha(a2, () => { txt('2010 ГОД', 10, 12, 230, RED, { w: 900 }); txt('2010 ГОД', 0, 0, 230, YEL, { w: 900, stroke: '#0d1230', sw: 26 }); });
  pop();
  alpha(prog(lt, 1.2, 1.6), () => { laptop10(330, 1010, 0.6, t); smart10(1620, 930, 0.75, t); person({ x: 960, y: 1180, s: 0.62, expr: 'surprised', blink: blinkAt(lt), look: [Math.sin(t * 2) * 12, -6] }); });
  alpha(prog(lt, 9.6, 10.2), () => rect(0, 0, W, H, '#000'));
}, { noCam: true });

const CHAPTERS = [[0, 'КОМНАТА', '07:03'], [14.35, 'КОМПЬЮТЕР', '07:20'], [25.75, 'ТЕЛЕФОН', '08:10'], [40.15, 'УЛИЦА', '11:30'], [49.35, 'КЛУБ', '14:15'], [60.35, 'ВЕЧЕР', '20:40'], [71.05, '2010', '23:30']];
