// Shots: timed to the narration. Each draw(lt, t) gets shot-local time and global time.

// ---------- environments ----------
function wallpaper(x0, y0, x1, y1, base, motif, line2) {
  rect(x0, y0, x1 - x0, y1 - y0, base);
  for (let x = x0; x < x1; x += 90) {
    rect(x, y0, 4, y1 - y0, line2);
    for (let y = y0 + 45, k = 0; y < y1; y += 95, k++) { const xx = x + 45 + (k % 2 ? 0 : 0); poly([xx, y - 16, xx + 12, y, xx, y + 16, xx - 12, y], motif); circ(xx, y + 48, 4, motif); }
  }
}
function carpet(x, y, w, h) {
  rr(x, y, w, h, 6, '#7d1f24'); rr(x + 18, y + 18, w - 36, h - 36, 4, '#a3343a');
  for (let i = 0; i < w / 40; i++) { poly([x + 20 + i * 40, y + 30, x + 40 + i * 40, y + 12, x + 60 + i * 40, y + 30, x + 40 + i * 40, y + 48], '#e0b04a'); poly([x + 20 + i * 40, y + h - 30, x + 40 + i * 40, y + h - 48, x + 60 + i * 40, y + h - 30, x + 40 + i * 40, y + h - 12], '#e0b04a'); }
  rr(x + 60, y + 70, w - 120, h - 140, 4, '#5e1a2a');
  const cx = x + w / 2, cy = y + h / 2;
  poly([cx, cy - 150, cx + 210, cy, cx, cy + 150, cx - 210, cy], '#c9543a'); poly([cx, cy - 100, cx + 140, cy, cx, cy + 100, cx - 140, cy], '#1f3a5a'); poly([cx, cy - 50, cx + 70, cy, cx, cy + 50, cx - 70, cy], '#e0b04a');
  [[x + 120, y + 120], [x + w - 120, y + 120], [x + 120, y + h - 120], [x + w - 120, y + h - 120]].forEach(([a, b]) => { poly([a, b - 40, a + 50, b, a, b + 40, a - 50, b], '#c9543a'); circ(a, b, 14, '#e0b04a'); });
  for (let i = 0; i < w / 14; i++) { line(x + 8 + i * 14, y + h, x + 8 + i * 14, y + h + 16, '#d9c8a0', 3); }
}
function bookshelf(x, y, w, h) {
  rect(x, y, w, h, '#5a3a22');
  const r = rng(3);
  for (let s = 0; s < 4; s++) { const sy = y + 20 + s * (h - 40) / 4; rect(x + 12, sy, w - 24, (h - 40) / 4 - 14, '#3a2414'); let bx = x + 16; while (bx < x + w - 40) { const bw = 16 + r() * 18, bh = (h - 40) / 4 - 30 - r() * 20; rect(bx, sy + (h - 40) / 4 - 14 - bh, bw, bh, ['#8a2a2a', '#2a4a7a', '#7a6a2a', '#2a6a4a', '#d9c8a0'][Math.floor(r() * 5)]); bx += bw + 3; } }
}

function room(t, mode = 'morning', opts = {}) {
  const dark = mode === 'evening' || mode === 'night';
  wallpaper(-600, -400, 2600, 760, '#d6c29a', '#b89a6a', '#cbb58a');
  rect(-600, 740, 3200, 24, '#8a6440');
  // floor
  rect(-600, 760, 3200, 700, '#8d5f38'); for (let i = 0; i < 30; i++) rect(-600, 790 + i * 34, 3200, 3, '#6f4a2a');
  rr(150, 860, 1500, 260, 6, '#6b2a2e'); rr(175, 880, 1450, 220, 4, '#8a3a36');
  // window
  const skyTop = { morning: '#f3c27a', morning2: '#cfe2f2', evening: '#2a2450', night: '#0d1430' }[mode];
  const skyBot = { morning: '#fbe3b0', morning2: '#f4f6f2', evening: '#c0587a', night: '#1d2a50' }[mode];
  c.fillStyle = grad(0, 160, 0, 560, [[0, skyTop], [1, skyBot]]); c.fillRect(100, 160, 320, 400);
  panel(110, 560, 140, 260, dark ? '#3a3f55' : '#9aa3ab', t, dark ? (r, k) => (r * 3 + k) % 4 === 0 : null);
  panel(280, 560, 150, 200, dark ? '#353a50' : '#a8a198', t, dark ? (r, k) => (r + k) % 3 === 0 : null, 4);
  if (mode === 'night') circ(330, 230, 26, '#f4f0d0');
  rect(92, 152, 336, 14, '#f0ece2'); rect(92, 552, 336, 14, '#f0ece2'); rect(92, 152, 14, 414, '#f0ece2'); rect(414, 152, 14, 414, '#f0ece2'); rect(254, 152, 12, 414, '#f0ece2');
  rect(70, 560, 380, 22, '#e9e3d6');
  alpha(0.55, () => { c.fillStyle = '#f7f2e6'; for (let i = 0; i < 9; i++) { const sw = Math.sin(t * 1.2 + i) * 6; c.fillRect(60 + i * 10 + sw, 130, 8, 460); c.fillRect(380 + i * 10 - sw, 130, 8, 460); } });
  rect(40, 120, 440, 16, '#7a5a3a');
  // calendar
  calendar(535, 250, 0.42, opts.year || '1995', opts.flip, 'ЯНВАРЬ', t);
  // nightstand + clock
  rect(440, 690, 140, 110, '#6b4227'); rect(432, 680, 156, 16, '#7c4e2f'); circ(510, 740, 6, '#d9b36a');
  alarmClock(510, 630, 0.42, t, !!opts.ring, opts.hours);
  // carpet + bed
  carpet(640, 170, 640, 430);
  bedBack();
  // TV
  rect(1380, 660, 320, 140, '#6b4227'); rect(1370, 650, 340, 16, '#7c4e2f'); rect(1400, 690, 120, 90, '#4a2c18'); rect(1560, 690, 120, 90, '#4a2c18');
  crtTV(1405, 432, 280, opts.tv || null, t, !!opts.tv);
  bookshelf(1760, 200, 300, 600);
  // ceiling lamp
  line(960, -400, 960, 40, '#333', 4); c.beginPath(); c.moveTo(900, 90); c.lineTo(1020, 90); c.lineTo(990, 40); c.lineTo(930, 40); c.closePath(); c.fillStyle = '#d98a3a'; c.fill();
}
function bedBack() {
  rr(600, 520, 44, 300, 10, '#5a3420'); rr(1300, 600, 40, 220, 10, '#5a3420');
  rect(640, 640, 660, 130, '#efe8da');
  rect(640, 760, 660, 40, '#6b4227');
}
function pillow() { ell(712, 640, 82, 36, '#f6f2ea'); ell(712, 632, 70, 22, '#ffffff'); }
function blanket(x0 = 770, top = 630, x1 = 1300) {
  c.beginPath(); c.moveTo(x0, 780); c.lineTo(x0, top + 20); c.quadraticCurveTo(x0 + 40, top - 20, x0 + 140, top - 10); c.quadraticCurveTo((x0 + x1) / 2, top + 10, x1, top + 10); c.lineTo(x1 + 10, 790); c.closePath();
  c.fillStyle = '#c4703a'; c.fill();
  c.save(); c.clip(); for (let x = x0; x < x1 + 40; x += 60) rect(x, top - 40, 14, 400, 'rgba(120,40,30,.35)'); for (let y = top - 40; y < 800; y += 60) rect(x0, y, x1 - x0 + 40, 14, 'rgba(255,220,150,.25)'); c.restore();
}
function sunbeam(t, a = 1) {
  alpha(0.22 * a, () => { c.fillStyle = grad(250, 160, 700, 900, [[0, '#fff2c0'], [1, 'rgba(255,230,160,0)']]); c.beginPath(); c.moveTo(100, 160); c.lineTo(420, 160); c.lineTo(1100, 1100); c.lineTo(450, 1100); c.closePath(); c.fill(); });
  for (let i = 0; i < 26; i++) { const r = rng(i + 40); const x = 300 + r() * 600 + Math.sin(t * 0.4 + i) * 30, y = 300 + r() * 600 + Math.cos(t * 0.3 + i * 2) * 30; alpha(0.5 * a * (0.5 + 0.5 * Math.sin(t * 2 + i)), () => circ(x, y, 2 + r() * 2.5, '#fff6d0')); }
}
function heroLying(t, expr, blink) {
  push(712 + 250, 615, -Math.PI / 2);
  person({ s: 0.5, expr, blink, hideLegs: true, hl: [-70, -260], hr: [70, -260] });
  pop();
  blanket(800, 600);
}
function heroSitBed(t, o) {
  person(Object.assign({ x: 960, y: 770, s: 0.82, hideLegs: true }, o));
  blanket(640, 640, 1300);
}

function kitchen(t) {
  rect(-600, -400, 3200, 820, '#b8c7a3');
  for (let y = 420; y < 780; y += 46) for (let x = -600; x < 2600; x += 46) { rect(x, y, 44, 44, ((x + y) / 46) % 7 === 0 ? '#9cc0d6' : '#eef1ef'); }
  rect(-600, 410, 3200, 12, '#7a9a7a');
  rect(-600, 780, 3200, 700, '#a5764a'); for (let x = -600; x < 2600; x += 90) for (let y = 780; y < 1300; y += 90) if (((x + y) / 90) % 2 === 0) rect(x, y, 90, 90, '#8d6038');
  // window
  c.fillStyle = grad(0, 120, 0, 440, [[0, '#a9cbe6'], [1, '#f2e2c0']]); c.fillRect(760, 120, 360, 320);
  panel(780, 440, 140, 220, '#9aa3ab', t); tree(1030, 460, 0.6, '#5a8a3a', t);
  [[752, 112, 376, 12], [752, 432, 376, 12], [752, 112, 12, 332], [1116, 112, 12, 332], [934, 112, 10, 332]].forEach(a => rect(...a, '#f0ece2'));
  rect(730, 440, 420, 24, '#e9e3d6');
  alpha(0.85, () => { c.fillStyle = '#f2d6a0'; c.fillRect(740, 100, 110, 200); c.fillRect(1030, 100, 110, 200); });
  rect(720, 90, 440, 14, '#7a5a3a');
  // fridge
  rr(1560, 240, 270, 560, 50, '#f1eee6'); rect(1560, 470, 270, 6, '#cfcac0'); rr(1580, 300, 16, 120, 8, '#b9b9b9'); rr(1580, 500, 16, 120, 8, '#b9b9b9'); rr(1660, 270, 110, 30, 6, '#c9b06a'); circ(1720, 380, 14, '#e05a3a'); rect(1700, 540, 40, 30, '#3a8ad9');
  // stove
  rect(1250, 620, 280, 180, '#ecebe6'); rect(1240, 610, 300, 18, '#d6d4cc'); rr(1280, 660, 220, 110, 6, '#3a3a3a'); for (let i = 0; i < 4; i++) circ(1290 + i * 30, 640, 8, '#222');
  // table
  rect(260, 640, 560, 160, '#c94a3a'); c.save(); c.beginPath(); c.rect(260, 600, 560, 200); c.clip(); for (let x = 260; x < 820; x += 40) rect(x, 600, 20, 200, 'rgba(255,255,255,.45)'); for (let y = 600; y < 800; y += 40) rect(260, y, 560, 20, 'rgba(255,255,255,.35)'); c.restore();
  rect(240, 600, 600, 50, '#d65a48'); rect(300, 800, 20, 100, '#5a3420'); rect(760, 800, 20, 100, '#5a3420');
  // lamp
  line(540, -400, 540, 160, '#333', 4); c.beginPath(); c.moveTo(450, 240); c.quadraticCurveTo(540, 120, 630, 240); c.closePath(); c.fillStyle = '#e38a2a'; c.fill();
  alpha(0.18, () => { c.fillStyle = '#ffd890'; c.beginPath(); c.moveTo(450, 240); c.lineTo(630, 240); c.lineTo(860, 640); c.lineTo(220, 640); c.closePath(); c.fill(); });
}

function streetBG(t, camX = 0, light = 'day') {
  sky(light === 'day' ? '#9ec6e4' : '#f0b070', light === 'day' ? '#f4e2c2' : '#f6d6a0');
  circ(1600, 160, 60, '#fff3c8');
  for (let i = 0; i < 7; i++) panel(-500 + i * 520, 760, 440, 380 + (i % 3) * 120, ['#b6b0a6', '#a9b2b8', '#c2b49e'][i % 3], t, null, i);
  for (let i = 0; i < 6; i++) tree(-300 + i * 560, 780, 0.9, '#4f8a3a', t);
  // wires
  c.beginPath(); c.moveTo(-600, 120); c.quadraticCurveTo(900, 200, 2600, 120); c.moveTo(-600, 150); c.quadraticCurveTo(900, 230, 2600, 150); c.strokeStyle = '#333'; c.lineWidth = 3; c.stroke();
}
function road(y0 = 820) {
  rect(-600, 760, 3400, 60, '#b3aca0'); rect(-600, y0, 3400, 200, '#55524e'); for (let x = -600; x < 2800; x += 160) rect(x, y0 + 95, 80, 10, '#e8e2d0'); rect(-600, y0 + 200, 3400, 300, '#b3aca0'); rect(-600, y0, 3400, 8, '#888');
}
function yardBG(t, eve = 0) {
  sky(eve ? '#e9a26a' : '#9ec6e4', eve ? '#f7d9a0' : '#f4e6c8');
  circ(eve ? 1500 : 1650, eve ? 420 : 150, eve ? 90 : 60, eve ? '#ffd27a' : '#fff3c8');
  for (let i = 0; i < 5; i++) panel(-500 + i * 700, 720, 620, 520 + (i % 2) * 80, ['#b6b0a6', '#a9b2b8', '#c2b49e'][i % 3], t, null, i + 3);
  rect(-600, 700, 3400, 800, '#7f9a54'); rect(-600, 700, 3400, 20, '#6a8444');
  for (let i = 0; i < 7; i++) tree(-400 + i * 480, 730, 0.8, i % 2 ? '#4f8a3a' : '#5d9a40', t);
  rr(-200, 860, 2600, 130, 40, '#c9b48a');
}
function climbArc(x, y) { for (let i = 0; i < 6; i++) { c.beginPath(); c.arc(x, y, 230 - i * 0, Math.PI, 0); } c.beginPath(); for (let k = 0; k < 7; k++) { const a = Math.PI + k * Math.PI / 6; c.moveTo(x + Math.cos(a) * 230, y + Math.sin(a) * 230); c.lineTo(x + Math.cos(a) * 230, y + Math.sin(a) * 230 + 0); } c.strokeStyle = '#d23a3a'; c.lineWidth = 10; [230, 170, 110].forEach(r => { c.beginPath(); c.arc(x, y, r, Math.PI, 0); c.strokeStyle = ['#d23a3a', '#f2b23a', '#2a7ac4'][r % 3 === 0 ? 0 : r === 170 ? 1 : 2]; c.stroke(); }); for (let k = 0; k <= 8; k++) { const a = Math.PI + k * Math.PI / 8; line(x + Math.cos(a) * 110, y + Math.sin(a) * 110, x + Math.cos(a) * 230, y + Math.sin(a) * 230, '#666', 6); } }
function swing(x, y, ang, kid) {
  line(x - 160, y - 330, x - 120, y, '#555', 10); line(x + 160, y - 330, x + 120, y, '#555', 10); line(x - 180, y - 330, x + 180, y - 330, '#d23a3a', 14);
  push(x, y - 330, ang); line(-40, 0, -40, 260, '#333', 4); line(40, 0, 40, 260, '#333', 4); rr(-60, 255, 120, 16, 4, '#8a5a2a'); if (kid) kid(); pop();
}

function shop(t) {
  rect(-600, -400, 3200, 900, '#e6dcc0'); rect(-600, 500, 3200, 1000, '#9a8a70');
  rr(560, 40, 800, 90, 10, '#2a5d8a'); txt('ПРОДУКТЫ', 960, 86, 64, '#f6efe0', { w: 900, ls: 8 });
  for (let s = 0; s < 4; s++) {
    const y = 200 + s * 120; rect(80, y + 92, 1760, 12, '#7a5a3a');
    for (let i = 0; i < 22; i++) {
      const x = 110 + i * 78;
      if (s === 0) { rr(x, y + 10, 56, 82, 10, 'rgba(160,200,140,.7)'); ell(x + 28, y + 60, 20, 18, '#4a7a2a'); rect(x + 4, y + 4, 48, 12, '#c9b06a'); }
      else if (s === 1) { rr(x, y + 30, 54, 62, 4, ['#c43d33', '#e3b23c', '#3a7ac4'][i % 3]); rect(x, y + 50, 54, 18, '#f6efe0'); }
      else if (s === 2) { poly([x, y + 92, x + 60, y + 92, x + 30, y + 22], i % 2 ? '#f2f2f2' : '#3a8ad9'); rect(x + 6, y + 70, 48, 8, '#3a8ad9'); }
      else { ell(x + 30, y + 70, 36, 22, '#c98a4a'); for (let k = 0; k < 3; k++) line(x + 12 + k * 14, y + 56, x + 18 + k * 14, y + 84, '#a96a2a', 3); }
    }
  }
  // counter
  rect(-600, 700, 3200, 400, '#6b4a30'); rect(-600, 640, 3200, 70, 'rgba(200,225,235,.65)'); rect(-600, 630, 3200, 14, '#ddd');
  for (let i = 0; i < 12; i++) { ell(160 + i * 150, 690, 60, 18, i % 2 ? '#c96a5a' : '#e8c86a'); }
}

// ---------- shots ----------
const S = [];
function shot(t0, t1, draw, o = {}) { S.push(Object.assign({ t0, t1, draw, fade: 0.3 }, o)); }

// 1a  bed, alarm
shot(0, 3.0, (lt, t) => {
  cam(eio(prog(lt, 0, 3.2)), [960, 560, 1.05], [800, 600, 1.35], 1, t);
  room(t, 'morning', { ring: lt < 2.4 }); pillow();
  heroLying(t, lt < 2.2 ? 'closed' : 'sleepy', 0);
  sunbeam(t);
  if (lt < 2.4) alpha(0.9, () => { for (let i = 0; i < 3; i++) { const p = (lt * 2 + i / 3) % 1; c.beginPath(); c.arc(510, 610, 40 + p * 90, -2.4, -0.7); c.strokeStyle = `rgba(255,80,60,${1 - p})`; c.lineWidth = 6; c.stroke(); } });
}, { v: { x: (p) => lerp(720, 800, p) } });
// 1b  sits up, realises
shot(3.0, 6.2, (lt, t) => {
  cam(eio(prog(lt, 0, 3.2)), [960, 470, 1.5], [960, 400, 2.1], 1, t);
  room(t, 'morning'); pillow();
  const up = eo(prog(lt, 0, 0.7));
  const yawn = lt < 1.2;
  const arm = Math.sin(prog(lt, 0.1, 1.3) * Math.PI);
  heroSitBed(t, { y: 770 + (1 - up) * 160, expr: yawn ? 'yawn' : (lt > 0.8 ? 'surprised' : 'neutral'), blink: lt > 1.5 ? blinkAt(lt) : 0, hl: [-112 - arm * 40, -188 - arm * 300], hr: [112 + arm * 40, -188 - arm * 300], look: lt > 2 ? [Math.sin(lt * 2) * 6, 0] : [0, 0] });
  sunbeam(t, 0.7);
});
// 1c  POV pan over room
shot(6.2, 9.3, (lt, t) => {
  const p = eio(prog(lt, 0, 3.1));
  cam(p, [380, 420, 1.55], [1500, 430, 1.55], 2, t);
  room(t, 'morning'); pillow(); blanket(640, 640, 1300);
  sunbeam(t, 0.8);
  alpha(0.25 * (1 - prog(lt, 0, 0.5)), () => rect(-600, -400, 3200, 2000, '#000'));
});
// 1d  alarm clock close
shot(9.3, 10.7, (lt, t) => {
  cam(eo(prog(lt, 0, 1.6)), [960, 520, 1.0, -0.03], [960, 540, 1.18, 0.02], 1, t);
  wallpaper(-600, -400, 2600, 820, '#d6c29a', '#b89a6a', '#cbb58a');
  alpha(0.5, () => rect(-600, -400, 3200, 1300, '#e9d6ae'));
  rect(-600, 760, 3200, 500, '#7c4e2f'); rect(-600, 760, 3200, 20, '#8f5d39');
  alarmClock(960, 520, 2.2, t, false);
  sunbeam(t, 0.5);
});
// 1e  CRT TV close
shot(10.7, 12.85, (lt, t) => {
  cam(eio(prog(lt, 0, 2.2)), [960, 520, 1.45], [960, 540, 1.05], 1, t);
  wallpaper(-600, -400, 2600, 820, '#d6c29a', '#b89a6a', '#cbb58a');
  rect(-600, 820, 3200, 500, '#7c4e2f'); rect(-600, 810, 3200, 24, '#8f5d39');
  crtTV(560, 120, 800, lt < 0.6 ? scrStatic : scrTest, t, true);
});
// 1f  walks to calendar
shot(12.85, 14.9, (lt, t) => {
  const hx = lerp(1250, 760, eio(prog(lt, 0, 2.1)));
  cam(0, [hx - 60, 520, 1.25], [hx - 60, 520, 1.25], 1, t);
  room(t, 'morning'); pillow(); blanket(640, 640, 1300);
  person({ x: hx, y: 960, s: 0.66, view: 'side', dir: -1, walk: lt < 2.0 ? lt * 9 : null, blink: blinkAt(lt) });
  sunbeam(t, 0.8);
});
// 1g  calendar 1995 close
shot(14.9, 18.45, (lt, t) => {
  cam(eio(prog(lt, 0, 3.5)), [960, 600, 1.0], [960, 470, 1.45], 1, t);
  wallpaper(-600, -400, 2600, 1400, '#d6c29a', '#b89a6a', '#cbb58a');
  calendar(960, 300, 1.9, '1995', undefined, 'ЯНВАРЬ', t);
  const hand = eo(prog(lt, 1.0, 1.8));
  if (lt > 0.9) { line(1500, 1300, lerp(1500, 1180, hand), lerp(1300, 820, hand), HERO.c1, 90); circ(lerp(1500, 1180, hand), lerp(1300, 820, hand), 48, HERO.skin); }
  alpha(0.6 * prog(lt, 1.1, 1.4) * (1 - prog(lt, 3.2, 3.5)), () => { c.beginPath(); c.ellipse(960, 410, 270, 90, 0, 0, TAU); c.strokeStyle = '#e8322a'; c.lineWidth = 10; c.stroke(); });
  sunbeam(t, 0.4);
}, { fade: 0.15 });

// 2a  kitchen wide
shot(18.45, 20.3, (lt, t) => {
  cam(eio(prog(lt, 0, 2)), [1100, 520, 1.12], [960, 540, 1.0], 1, t);
  kitchen(t);
  newspaper(420, 625, 0.32, -0.08); teaGlass(700, 640, 0.6, t);
  kettle(1330, 625, 0.5, t); radio(1050, 400, 0.28, t);
  person({ x: lerp(1700, 1000, eo(prog(lt, 0, 1.8))), y: 980, s: 0.68, view: 'side', dir: -1, walk: lt < 1.7 ? lt * 9 : null, look: [6, 0] });
});
// 2b  newspaper close
shot(20.3, 21.85, (lt, t) => {
  cam(eio(prog(lt, 0, 1.6)), [880, 520, 1.15, -0.04], [1000, 540, 1.3, 0], 1, t);
  rect(-600, -400, 3200, 2000, '#c94a3a'); for (let x = -600; x < 2600; x += 120) rect(x, -400, 60, 2000, 'rgba(255,255,255,.4)'); for (let y = -400; y < 1600; y += 120) rect(-600, y, 3200, 60, 'rgba(255,255,255,.3)');
  newspaper(860, 560, 1.75, -0.06);
  teaGlass(1560, 900, 2.0, t);
});
// 2c  kettle on gas
shot(21.85, 23.0, (lt, t) => {
  cam(eo(prog(lt, 0, 1.2)), [960, 540, 1.05], [980, 520, 1.2], 1, t);
  for (let y = -400; y < 1400; y += 92) for (let x = -600; x < 2600; x += 92) rect(x, y, 88, 88, '#eef1ef');
  rect(-600, 800, 3200, 500, '#ecebe6'); rect(-600, 790, 3200, 24, '#d6d4cc');
  for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; const fl = 1 + Math.sin(t * 30 + i) * 0.15; poly([960 + Math.cos(a) * 110, 820, 960 + Math.cos(a) * 125, 820 - 40 * fl, 960 + Math.cos(a + 0.2) * 115, 820], '#5a8aff'); }
  ell(960, 815, 180, 20, '#333');
  kettle(960, 800, 2.4, t);
});
// 2d  radio
shot(23.0, 25.85, (lt, t) => {
  cam(eio(prog(lt, 0, 2.9)), [960, 560, 1.0], [900, 520, 1.25], 1, t);
  c.fillStyle = grad(0, 0, 0, 760, [[0, '#a9cbe6'], [1, '#f2e2c0']]); c.fillRect(-600, -400, 3200, 1200);
  panel(-200, 800, 600, 900, '#9aa3ab', t); panel(1500, 800, 500, 700, '#b6b0a6', t);
  rect(-600, 760, 3200, 600, '#e9e3d6'); rect(-600, 740, 3200, 30, '#f2eee4');
  rr(1350, 600, 160, 170, 10, '#c4703a'); circ(1430, 520, 80, '#4f8a3a'); circ(1380, 470, 50, '#5d9a40');
  radio(900, 600, 1.3, t);
  notes(900, 380, t, 7, 600);
});

// 3a  out of the entrance
shot(25.85, 28.0, (lt, t) => {
  cam(eio(prog(lt, 0, 2.2)), [960, 560, 1.1], [960, 600, 1.2], 1, t);
  sky('#9ec6e4', '#f4e2c2');
  rect(200, -400, 1520, 1200, '#b9b2a6'); for (let x = 200; x < 1720; x += 80) for (let y = -400; y < 800; y += 60) rect(x, y, 78, 58, ((x / 80 + y / 60) % 2) ? '#c2bcb0' : '#b3ac9f');
  rect(700, 240, 520, 40, '#8a8378'); poly([680, 240, 1240, 240, 1210, 200, 710, 200], '#9a9388');
  rect(780, 280, 360, 520, '#2a2422');
  const open = eo(prog(lt, 0, 0.6)) * (1 - eio(prog(lt, 1.6, 2.1)));
  const hp = eo(prog(lt, 0.2, 2.1));
  person({ x: 960, y: lerp(800, 1180, hp), s: lerp(0.62, 1.05, hp), walk: lt * 8, blink: blinkAt(lt), look: [Math.sin(lt * 2) * 8, 0] });
  push(780, 280); c.scale(1 - open * 0.85, 1); rect(0, 0, 360, 520, '#7a4a2a'); rect(20, 20, 320, 480, '#8a5a34'); circ(320, 270, 12, '#ccc'); pop();
  txt('ПОДЪЕЗД 3', 960, 160, 34, '#2a2a2a', { w: 800 });
  bench(360, 860, 1.3); extra(2, { x: 300, y: 860, s: 0.55, sit: true, top: 'coat', c1: '#6b5a48', hair: 'perm', hairCol: '#9a9a9a', expr: 'neutral', blink: blinkAt(lt, 2) }); extra(7, { x: 450, y: 860, s: 0.55, sit: true, hair: 'perm', hairCol: '#c9b08a', blink: blinkAt(lt, 5), look: [8, 0] });
  bench(1560, 860, 1.3);
});
// 3b  street: cars and kiosks
shot(28.0, 30.6, (lt, t) => {
  cam(eio(prog(lt, 0, 2.6)), [800, 560, 1.05], [1150, 560, 1.05], 1, t);
  streetBG(t); road(820);
  kiosk(-200, 760, 300, 260, 'ГАЗЕТЫ', '#2a7ac4', t); kiosk(160, 760, 340, 280, 'ПРОДУКТЫ', '#c43d33', t); kiosk(1300, 760, 320, 270, 'ЦВЕТЫ', '#3a9a5a', t); kiosk(1680, 760, 340, 270, 'КАССЕТЫ', '#7a2c8f', t);
  for (let i = 0; i < 4; i++) extra(i + 3, { x: ((i * 520 + t * 90) % 2600) - 300, y: 790, s: 0.4, view: 'side', dir: 1, walk: t * 8 + i, blink: blinkAt(t, i) });
  car(((t * 420) % 3400) - 700, 900, 0.85, '#e8e2d0', t, 1, 0);
  car(2600 - ((t * 380 + 1200) % 3400), 1000, 0.95, '#a8323a', t, -1, 1);
  car(((t * 300 + 1600) % 3400) - 700, 900, 0.85, '#5a8ac4', t, 1, 1);
  bus(2700 - ((t * 260 + 400) % 3600), 1010, 0.75, t, -1);
});
// 3c  market
shot(30.6, 33.0, (lt, t) => {
  cam(eio(prog(lt, 0, 2.4)), [1150, 540, 1.1], [800, 540, 1.1], 1, t);
  streetBG(t); rect(-600, 760, 3400, 600, '#a59d8f');
  const goods = [['#e04a3a', '#f2b23a', '#7ad93a'], ['#f2d33b', '#e8862a'], ['#7a2c8f', '#c43d33', '#3a9a5a']];
  stall(-300, 860, 480, ['#c43d33', '#f6efe0'], goods[0], t, 1); stall(300, 860, 460, ['#2a7ac4', '#f6efe0'], goods[1], t, 2); stall(880, 860, 500, ['#3a9a5a', '#f6efe0'], goods[2], t, 3);
  // clothes stall
  stall(1500, 860, 520, ['#e3b23c', '#c43d33'], ['#555'], t, 4);
  for (let i = 0; i < 5; i++) { const x = 1540 + i * 100, sw = Math.sin(t * 2 + i) * 0.05; push(x, 600, sw); rr(-40, 0, 80, 120, 10, OUTFITS[i].c1); rect(-40, 40, 80, 12, OUTFITS[i].c2); pop(); }
  [80, 520, 1110].forEach((x, i) => extra(i + 1, { x, y: 760, s: 0.42, blink: blinkAt(t, i), look: [Math.sin(t + i) * 8, 0] }));
  for (let i = 0; i < 7; i++) { const dir = i % 2 ? 1 : -1; const x = dir > 0 ? ((t * 150 + i * 400) % 2800) - 400 : 2400 - ((t * 150 + i * 400) % 2800); extra(i + 4, { x, y: 1060 + (i % 3) * 20, s: 0.62, view: 'side', dir, walk: t * 8 + i * 1.3, blink: blinkAt(t, i) }); }
});
// 3d  hurrying crowd, nobody on phones
shot(33.0, 35.6, (lt, t) => {
  cam(eio(prog(lt, 0, 2.6)), [960, 560, 1.15], [960, 540, 1.0], 1, t);
  streetBG(t); road(820);
  rect(140, 470, 150, 300, '#c43d33'); rect(150, 480, 130, 180, '#bcd2dd'); txt('ТАКСОФОН', 215, 455, 22, '#fff', { w: 900, stroke: '#c43d33', sw: 26 }); rect(185, 560, 60, 80, '#555');
  for (let i = 0; i < 9; i++) { const dir = i % 2 ? 1 : -1; const sp = 220 + (i % 3) * 40; const x = dir > 0 ? ((t * sp + i * 330) % 2800) - 400 : 2400 - ((t * sp + i * 330) % 2800); const row = i % 3; extra(i, { x, y: 860 + row * 90, s: 0.5 + row * 0.1, view: 'side', dir, walk: t * 10 + i, blink: blinkAt(t, i), look: [4, 0] }); }
});
// 3e  hero shrugs: no smartphones yet
shot(35.6, 38.62, (lt, t) => {
  cam(eio(prog(lt, 0, 3)), [960, 600, 1.5], [960, 580, 1.8], 1, t);
  streetBG(t); road(820);
  for (let i = 0; i < 4; i++) { const dir = i % 2 ? 1 : -1; const x = dir > 0 ? ((t * 200 + i * 600) % 2800) - 400 : 2400 - ((t * 200 + i * 600) % 2800); extra(i + 2, { x, y: 900, s: 0.5, view: 'side', dir, walk: t * 9 + i }); }
  const pat = lt < 1.4 ? Math.abs(Math.sin(lt * 9)) : 0;
  const shrug = eo(prog(lt, 1.4, 1.8));
  person({ x: 960, y: 1060, s: 0.95, expr: lt < 1.4 ? 'worried' : 'smile', blink: blinkAt(lt), hl: [-100 - shrug * 80, -210 + pat * 20 - shrug * 120], hr: [100 + shrug * 80, -210 + pat * 20 - shrug * 120], look: lt < 1.4 ? [0, 10] : [0, 0], tilt: shrug * 0.08 });
  if (lt > 1.6) alpha(prog(lt, 1.6, 1.9), () => { push(1250, 320, Math.sin(t * 3) * 0.1); rr(-60, -100, 120, 200, 20, '#222'); rr(-50, -86, 100, 160, 8, '#5a6f8a'); line(-80, 110, 80, -110, '#e8322a', 14); line(-80, -110, 80, 110, '#e8322a', 14); pop(); });
}, { v: { k: 1.0, x: 1000 } });

// 4a  rotary phone dial
shot(38.62, 41.2, (lt, t) => {
  cam(eio(prog(lt, 0, 2.6)), [960, 560, 1.0], [960, 520, 1.2], 1, t);
  wallpaper(-600, -400, 2600, 760, '#c9b48a', '#a68a5a', '#bea67a');
  rect(-600, 760, 3200, 600, '#6b4227'); ell(960, 800, 520, 70, '#f6f2ea'); for (let i = 0; i < 24; i++) circ(960 + Math.cos(i / 24 * TAU) * 520, 800 + Math.sin(i / 24 * TAU) * 70, 16, '#f6f2ea');
  const cyc = (lt % 1.3) / 1.3; const dial = cyc < 0.45 ? -eio(cyc / 0.45) * 2.6 : -2.6 * (1 - prog(cyc, 0.45, 0.85));
  rotaryPhone(960, 700, 2.2, dial, false);
  const fa = -Math.PI * 0.35 - 2 * 0.48 + dial; const fx = 960 + Math.cos(fa) * 62 * 2.2, fy = 700 + Math.sin(fa) * 62 * 2.2;
  if (cyc < 0.47) { line(fx + 300, fy + 520, fx + 40, fy + 60, HERO.c1, 80); circ(fx + 30, fy + 40, 36, HERO.skin); line(fx + 22, fy + 30, fx, fy, HERO.skin, 22); }
});
// 4b  waiting with handset
shot(41.2, 45.0, (lt, t) => {
  cam(eio(prog(lt, 0, 3.8)), [1000, 600, 1.3], [940, 580, 1.55], 1, t);
  wallpaper(-600, -400, 2600, 820, '#c9b48a', '#a68a5a', '#bea67a');
  rect(-600, 820, 3200, 600, '#6b4227');
  rect(1240, 700, 300, 30, '#7c4e2f'); rect(1260, 730, 30, 300, '#5a3420'); rect(1490, 730, 30, 300, '#5a3420');
  rotaryPhone(1390, 640, 0.75, 0, true);
  const P = { x: 860, y: 1120, s: 1.0, expr: lt < 1.6 ? 'neutral' : (lt < 3 ? 'worried' : 'smile'), blink: blinkAt(lt), hr: [70, -455], hl: [-110, -190], look: [lt > 1.6 && lt < 3 ? 6 : 0, lt > 1.6 && lt < 3 ? -8 : 0] };
  coil(860 + 110, 1120 - 400, 1390 - 40, 640 - 30, '#b0352a', 22, 12);
  person(P);
  handset(860 + 95, 1120 - 480, 0.55, 0.25);
  circ(860 + 70, 1120 - 455, 23, HERO.skin);
  if (lt > 0.4 && lt < 3.2) { const n = Math.floor((lt - 0.4) / 0.9); for (let i = 0; i <= Math.min(n, 2); i++) alpha(0.9, () => txt('ДУ-У-У', 1280 + i * 40, 260 + i * 70, 40, '#2a2a2a', { w: 900, stroke: '#f6efe0', sw: 10 })); }
  if (lt > 3.0) alpha(prog(lt, 3.0, 3.3), () => { push(1300, 300); ell(0, 0, 150, 110, '#fff'); circ(-150, 110, 24, '#fff'); circ(-185, 145, 12, '#fff'); person({ x: 0, y: 120, s: 0.3, ...OUTFITS[0], hair: 'short', hairCol: '#3a2a1e', expr: 'smile' }); pop(); });
}, { v: { k: 1.0, x: 1060 } });
// 4c  shop
shot(45.0, 48.1, (lt, t) => {
  cam(eio(prog(lt, 0, 3.1)), [960, 520, 1.05], [1050, 520, 1.25], 1, t);
  shop(t);
  // cashier behind counter
  person({ x: 1300, y: 900, s: 0.8, hair: 'perm', hairCol: '#9a3a1a', skin: '#e8bd96', top: 'coat', c1: '#f2f2f2', expr: 'smile', blink: blinkAt(lt, 3), hr: [lerp(110, -150, eo(prog(lt, 1.4, 2.0))), lerp(-190, -260, eo(prog(lt, 1.4, 2.0)))] });
  rect(-600, 700, 3200, 400, '#6b4a30'); rect(-600, 640, 3200, 70, 'rgba(200,225,235,.5)'); rect(-600, 630, 3200, 14, '#ddd');
  // abacus
  push(1550, 620); rr(-110, -90, 220, 100, 6, '#8a5a2a'); for (let r = 0; r < 5; r++) { line(-100, -76 + r * 18, 100, -76 + r * 18, '#444', 2); for (let k = 0; k < 8; k++) ell(-90 + k * 14 + (k > 3 ? 60 : 0), -76 + r * 18, 7, 7, k % 2 ? '#222' : '#c9a25a'); } pop();
  // cassette rack
  push(380, 620); rect(-120, -150, 240, 150, '#333'); for (let i = 0; i < 6; i++) rr(-110 + (i % 3) * 75, -140 + Math.floor(i / 3) * 70, 66, 60, 4, ['#e05a3a', '#3a8ad9', '#f2b53a', '#7ad93a', '#d93a9a', '#fff'][i]); pop();
  const cp = eo(prog(lt, 1.4, 2.0));
  cassette(lerp(1300, 1100, cp), lerp(560, 600, cp), 0.32, t, 0);
  person({ x: 750, y: 1200, s: 1.0, view: 'side', dir: 1, expr: lt > 1.8 ? 'smile' : 'neutral', blink: blinkAt(lt), hr: [lerp(30, 230, eo(prog(lt, 1.7, 2.2))), lerp(-200, -330, eo(prog(lt, 1.7, 2.2)))] });
}, { v: { k: 1.0, x: 1000 } });

// 5a  walkman, lid opens
shot(48.1, 50.25, (lt, t) => {
  cam(eio(prog(lt, 0, 2.1)), [960, 560, 1.0], [960, 540, 1.2], 1, t);
  rect(-600, -400, 3200, 2000, '#3a2a4a'); c.fillStyle = rgrad(960, 500, 50, 900, [[0, 'rgba(255,190,120,.5)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000);
  const rise = eo(prog(lt, 0, 0.7));
  push(0, (1 - rise) * 500);
  walkman(960, 560, 1.4, t, eio(prog(lt, 1.0, 1.6)), false);
  [-1, 1].forEach(s => { line(960 + s * 420, 1300, 960 + s * 330, 760, HERO.c1, 110); circ(960 + s * 330, 740, 55, HERO.skin); });
  pop();
});
// 5b  cassette in, lid closes
shot(50.25, 51.7, (lt, t) => {
  cam(0, [960, 520, 1.25], [960, 520, 1.25], 1.5, t);
  rect(-600, -400, 3200, 2000, '#3a2a4a'); c.fillStyle = rgrad(960, 500, 50, 900, [[0, 'rgba(255,190,120,.5)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000);
  const ins = eio(prog(lt, 0, 0.6)); const close = eio(prog(lt, 0.7, 1.0));
  walkman(960, 560, 1.4, t, 1 - close, ins > 0.98, false);
  if (ins < 0.99) { cassette(960, lerp(-80, 581, ins), 1.33, t, 0); line(960 + 300, lerp(-300, 360, ins), 960 + 200, lerp(-160, 520, ins), HERO.c1, 100); circ(960 + 190, lerp(-160, 520, ins), 50, HERO.skin); }
  if (lt > 1.0 && lt < 1.25) alpha(1 - prog(lt, 1.0, 1.25), () => txt('ЩЁЛК!', 1380, 260, 90, '#ffe14d', { w: 900, stroke: '#2a2a2a', sw: 16 }));
}, { fade: 0.15 });
// 5c  headphones on
shot(51.7, 53.6, (lt, t) => {
  cam(eio(prog(lt, 0, 1.9)), [960, 520, 1.55], [960, 470, 1.85], 1, t);
  room(t, 'morning'); sunbeam(t, 0.6);
  const up = eio(prog(lt, 0, 0.6));
  const on = lt > 0.55;
  person({ x: 960, y: 1080, s: 0.95, expr: on ? (lt > 0.9 ? 'happy' : 'smile') : 'neutral', blink: on ? 0 : blinkAt(lt), headphones: on, hl: on ? [-108, -188] : [-130, lerp(-300, -470, up)], hr: on ? [108, -188] : [130, lerp(-300, -470, up)], tilt: on ? Math.sin(t * 7.2) * 0.04 : 0 });
  if (!on) { const y = 1080 + lerp(-300, -470, up) * 0.95; c.beginPath(); c.arc(960, y + 30, 125, Math.PI * 1.05, Math.PI * 1.95); c.strokeStyle = '#3b3b40'; c.lineWidth = 12; c.stroke(); ell(842, y + 40, 21, 34, '#e8862a'); ell(1078, y + 40, 21, 34, '#e8862a'); }
  if (on) notes(960, 300, t, 6, 700);
});
// 5d  reels close-up
shot(53.6, 56.0, (lt, t) => {
  cam(eio(prog(lt, 0, 2.4)), [960, 540, 1.6, -0.05], [960, 560, 2.1, 0.04], 1, t);
  rect(-600, -400, 3200, 2000, '#1d1f24');
  cassette(960, 540, 2.2, t, 1);
  alpha(0.25 + 0.1 * Math.sin(t * 8), () => { c.fillStyle = rgrad(960, 540, 10, 700, [[0, '#ff9a5a'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
  notes(960, 700, t, 8, 900);
});
// 5e  walking with music
shot(56.0, 58.35, (lt, t) => {
  cam(0, [960, 520, 1.3], [960, 520, 1.3], 1, t);
  push(-((t * 260) % 560), 0); streetBG(t); pop();
  rect(-600, 760, 3400, 600, '#b3aca0'); for (let x = -600; x < 2800; x += 140) rect(x - (t * 520) % 140, 760, 4, 600, '#9a9386');
  person({ x: 960, y: 1080, s: 0.8, view: 'side', dir: 1, walk: t * 10, headphones: true, expr: 'happy', tilt: Math.sin(t * 7.2) * 0.04 });
  notes(1000, 380, t, 6, 600);
});

// 6a  yard, friends
shot(58.35, 61.6, (lt, t) => {
  cam(eio(prog(lt, 0, 3.2)), [900, 540, 1.05], [1050, 560, 1.15], 1, t);
  yardBG(t); climbArc(1500, 860); bench(500, 900, 1.2);
  const wave = (k) => [110 + Math.sin(t * 9 + k) * 30, -470];
  extra(0, { x: 1150, y: 980, s: 0.62, expr: 'smile', blink: blinkAt(t, 1), hr: lt > 0.8 ? wave(0) : undefined });
  extra(2, { x: 1350, y: 990, s: 0.6, hair: 'cap', hairCol: '#c23b3b', expr: 'happy', hr: lt > 1.0 ? wave(1) : undefined });
  extra(4, { x: 1540, y: 985, s: 0.58, hair: 'pony', hairCol: '#c9a25a', top: 'tshirt', c1: '#e05a8a', expr: 'smile', blink: blinkAt(t, 3) });
  person({ x: lerp(250, 900, eo(prog(lt, 0, 2.4))), y: 1000, s: 0.64, view: 'side', dir: 1, walk: lt < 2.3 ? lt * 9 : null, expr: 'smile', hr: lt > 2.4 ? [120, -470 + Math.sin(t * 9) * 20] : undefined });
}, { v: { k: 1.05, x: (p) => lerp(800, 1250, p) } });
// 6b  bikes
shot(61.6, 63.9, (lt, t) => {
  const bx = lerp(200, 1500, prog(lt, 0, 2.3));
  cam(0, [bx + 300, 560, 1.0], [bx + 300, 560, 1.0], 1.5, t);
  yardBG(t); tree(400, 900, 1.1, '#4f8a3a', t); tree(1800, 900, 1.0, '#5d9a40', t);
  rider(bx + 500, 960, 0.75, t, 2, 9, 'happy');
  rider(bx + 120, 990, 0.8, t, -1, 9, 'happy');
  rider(bx - 320, 1000, 0.78, t, 0, 9, 'smile');
});
// 6c  together, sunset
shot(63.9, 66.15, (lt, t) => {
  cam(eio(prog(lt, 0, 2.3)), [960, 520, 1.12], [960, 540, 1.0], 1, t);
  yardBG(t, 1);
  swing(1450, 950, Math.sin(t * 2.4) * 0.45, () => extra(4, { x: 0, y: 330, s: 0.42, sit: true, hair: 'pony', hairCol: '#c9a25a', top: 'tshirt', c1: '#e05a8a', expr: 'happy', hl: [-40, -470], hr: [40, -470] }));
  const kick = (t * 1.2) % 1;
  const bx = lerp(620, 1080, Math.min(1, kick * 1.6)), by = 960 - Math.sin(Math.min(1, kick * 1.6) * Math.PI) * 220;
  extra(0, { x: 520, y: 990, s: 0.6, view: 'side', dir: 1, expr: 'happy', fr: kick < 0.15 ? [120, -60] : undefined });
  extra(2, { x: 1180, y: 990, s: 0.6, view: 'side', dir: -1, hair: 'cap', hairCol: '#c23b3b', expr: 'happy', walk: t * 6 });
  circ(bx, by, 26, '#f6efe0'); c.beginPath(); c.arc(bx, by, 26, 0, TAU); c.strokeStyle = '#222'; c.lineWidth = 3; c.stroke(); poly([bx - 8, by - 6, bx + 8, by - 6, bx + 10, by + 8, bx, by + 14, bx - 10, by + 8], '#222');
  person({ x: 860, y: 1010, s: 0.66, expr: 'happy', hl: [-150, -460 + Math.sin(t * 8) * 20], hr: [150, -460 + Math.cos(t * 8) * 20] });
  alpha(0.18, () => rect(-600, -400, 3200, 2000, '#ff8a3a'));
});

// 7a  evening outside
shot(66.15, 69.1, (lt, t) => {
  cam(eio(prog(lt, 0, 3)), [960, 520, 1.0], [960, 560, 1.15], 1, t);
  sky('#2a2458', '#e07a5a');
  for (let i = 0; i < 12; i++) { const r = rng(i + 90); circ(r() * 1920, r() * 300, 2, `rgba(255,255,255,${0.4 + 0.4 * Math.sin(t * 3 + i)})`); }
  const lp = prog(lt, 0, 2.6);
  panel(150, 900, 1620, 820, '#5a5e70', t, (r, k) => hash(r * 31 + k * 7) < lp * 0.75);
  rect(-600, 900, 3200, 600, '#3a3c44'); rect(860, 760, 200, 140, '#2a2422'); rect(820, 740, 280, 24, '#55586a');
  alpha(0.9 * prog(lt, 0.3, 0.6), () => { c.fillStyle = rgrad(960, 735, 5, 260, [[0, 'rgba(255,200,110,.7)'], [1, 'rgba(255,200,110,0)']]); c.fillRect(600, 600, 720, 500); });
  [300, 1620].forEach(x => { line(x, 1000, x, 640, '#333', 10); line(x, 640, x + 60, 630, '#333', 8); const on = prog(lt, 0.4, 0.5); alpha(on, () => { c.fillStyle = rgrad(x + 60, 645, 5, 260, [[0, 'rgba(255,170,80,.8)'], [1, 'rgba(255,170,80,0)']]); c.fillRect(x - 300, 400, 720, 700); }); ell(x + 60, 645, 22, 10, on > 0.5 ? '#ffc070' : '#666'); });
  person({ x: lerp(300, 900, eo(prog(lt, 0, 2.8))), y: 1000, s: 0.35, view: 'side', dir: 1, walk: lt * 9 });
});
// 7b  TV turns on, seen from behind
shot(69.1, 73.3, (lt, t) => {
  cam(eio(prog(lt, 0, 4.2)), [1300, 560, 1.2], [1450, 540, 1.55], 1, t);
  const tvf = lt < 0.25 ? null : (lt < 0.9 ? scrStatic : scrShow);
  room(t, 'evening', { tv: tvf });
  alpha(0.62, () => rect(-600, -400, 3200, 2000, '#0a0c22'));
  if (tvf) { const fl = 0.75 + 0.25 * Math.sin(t * 13) * Math.sin(t * 7); alpha(fl, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(1545, 540, 20, 800, [[0, 'rgba(120,160,255,.55)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); }); crtTV(1405, 432, 280, tvf, t, true); }
  person({ x: 1250, y: 1120, s: 0.9, view: 'back', sit: true, tilt: Math.sin(t * 0.5) * 0.03 });
});
// 7c  face lit by TV
shot(73.3, 76.75, (lt, t) => {
  cam(eio(prog(lt, 0, 3.4)), [960, 640, 1.6], [960, 610, 1.95], 1, t);
  room(t, 'evening'); alpha(0.7, () => rect(-600, -400, 3200, 2000, '#0a0c22'));
  person({ x: 960, y: 1080, s: 0.95, expr: lt < 2.4 ? 'smile' : 'sleepy', blink: blinkAt(lt), look: [10, 0] });
  const fl = 0.6 + 0.4 * Math.sin(t * 11) * Math.sin(t * 5.3);
  alpha(0.35 * fl, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(1500, 500, 30, 900, [[0, '#7aa0ff'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
});
// 7d  night, time races
shot(76.75, 78.3, (lt, t) => {
  cam(eio(prog(lt, 0, 1.6)), [960, 540, 1.0], [960, 540, 1.3, 0.05], 2, t);
  const p = prog(lt, 0, 1.5);
  rect(-600, -400, 3200, 2000, p < 0.5 ? '#141a3a' : '#e8c890');
  alpha(Math.abs(Math.sin(p * Math.PI)), () => rect(-600, -400, 3200, 2000, '#3a2a5a'));
  alarmClock(960, 560, 2.3, t, false, 22 + p * 9);
  for (let i = 0; i < 10; i++) { const a = i / 10 * TAU + t; line(960 + Math.cos(a) * 320, 560 + Math.sin(a) * 320, 960 + Math.cos(a) * 520, 560 + Math.sin(a) * 520, 'rgba(255,255,255,.25)', 6); }
}, { fade: 0.15 });
// 7e  wakes up again
shot(78.3, 80.4, (lt, t) => {
  cam(eio(prog(lt, 0, 2.1)), [960, 480, 1.5], [960, 420, 2.0], 1, t);
  room(t, 'morning2'); pillow();
  const up = eo(prog(lt, 0, 0.5));
  heroSitBed(t, { y: 770 + (1 - up) * 160, expr: lt < 0.5 ? 'closed' : 'surprised', blink: lt > 1 ? blinkAt(lt) : 0, sweat: lt > 0.8, look: [Math.sin(lt * 3) * 8, 0] });
  sunbeam(t, 0.5);
});
// 7f  calendar flips to 2005
shot(80.4, 84.0, (lt, t) => {
  cam(eio(prog(lt, 0, 3.6)), [960, 560, 1.0], [960, 430, 1.4], 1, t);
  wallpaper(-600, -400, 2600, 1400, '#d6c29a', '#b89a6a', '#cbb58a');
  const f = eio(prog(lt, 0.7, 1.5));
  calendar(960, 300, 1.9, '1995', f > 0 ? f : undefined, 'ЯНВАРЬ', t);
  if (lt > 1.5) alpha(prog(lt, 1.5, 1.8), () => { c.beginPath(); c.ellipse(960, 410, 270, 90, 0, 0, TAU); c.strokeStyle = '#e8322a'; c.lineWidth = 10; c.stroke(); });
}, { fade: 0.2 });
// 7g  final card
shot(84.0, 90.5, (lt, t) => {
  c.fillStyle = grad(0, 0, 0, H, [[0, '#0d1030'], [1, '#2a1238']]); c.fillRect(0, 0, W, H);
  if (!VERT) for (let i = 0; i < 14; i++) { const a = i / 14 * TAU + t * 0.08; alpha(0.06, () => poly([960, 470, 960 + Math.cos(a) * 2400, 470 + Math.sin(a) * 2400, 960 + Math.cos(a + 0.12) * 2400, 470 + Math.sin(a + 0.12) * 2400], '#ffd27a')); }
  const a1 = eo(prog(lt, 0.1, 0.6)), a2 = eo(prog(lt, 0.5, 1.0));
  if (VERT) {
    for (let i = 0; i < 14; i++) { const a = i / 14 * TAU + t * 0.08; alpha(0.06, () => poly([540, 700, 540 + Math.cos(a) * 2400, 700 + Math.sin(a) * 2400, 540 + Math.cos(a + 0.12) * 2400, 700 + Math.sin(a + 0.12) * 2400], '#ffd27a')); }
    push(540, 360, 0, lerp(1.3, 1, a1)); alpha(a1, () => { txt('СЛЕДУЮЩАЯ', 0, 0, 104, '#f6efe0', { w: 900, ls: 2 }); txt('ОСТАНОВКА —', 0, 120, 104, '#f6efe0', { w: 900, ls: 2 }); }); pop();
    push(540, 900, 0, lerp(1.6, 1, a2) * (1 + Math.sin(t * 3) * 0.01));
    alpha(a2, () => { [['2005', -110, 300], ['ГОД', 170, 220]].forEach(([s2, y, sz]) => { txt(s2, -8, y, sz, 'rgba(255,40,80,.7)', { w: 900 }); txt(s2, 8, y, sz, 'rgba(40,200,255,.7)', { w: 900 }); txt(s2, 0, y, sz, '#ffe14d', { w: 900 }); }); });
    pop();
    alpha(prog(lt, 1.2, 1.6), () => { person({ x: 790, y: 1920, s: 0.6, expr: 'surprised', blink: blinkAt(lt), look: [-10, -6] }); person({ x: 290, y: 1920, s: 0.6, expr: 'smile', headphones: true, blink: blinkAt(lt, 2) }); });
    alpha(prog(lt, 5.4, 6.0), () => rect(0, 0, W, H, '#000'));
    return;
  }
  push(960, 330, 0, lerp(1.3, 1, a1)); alpha(a1, () => txt('СЛЕДУЮЩАЯ ОСТАНОВКА —', 0, 0, 92, '#f6efe0', { w: 900, ls: 2 })); pop();
  push(960, 520, 0, lerp(1.6, 1, a2) * (1 + Math.sin(t * 3) * 0.01));
  alpha(a2, () => { txt('2005 ГОД', -8, 0, 230, 'rgba(255,40,80,.7)', { w: 900 }); txt('2005 ГОД', 8, 0, 230, 'rgba(40,200,255,.7)', { w: 900 }); txt('2005 ГОД', 0, 0, 230, '#ffe14d', { w: 900 }); });
  pop();
  alpha(prog(lt, 1.2, 1.6), () => { person({ x: 1640, y: 1080, s: 0.55, expr: 'surprised', blink: blinkAt(lt), look: [-10, -6] }); person({ x: 280, y: 1080, s: 0.55, view: 'front', expr: 'smile', headphones: true, blink: blinkAt(lt, 2) }); });
  alpha(prog(lt, 5.4, 6.0), () => rect(0, 0, W, H, '#000'));
}, { noCam: true });

// scene changes get a VHS glitch
const GLITCH = [[0.05, 1], [18.45, 0.8], [25.85, 0.8], [38.62, 0.7], [45.0, 0.6], [48.1, 0.6], [58.35, 0.8], [66.15, 0.8], [76.75, 1], [78.3, 0.9], [81.1, 1.4], [84.0, 1.2], [89.7, 1.2]];
const OSD = [[0, '14.01.1995', '07:03'], [18.45, '14.01.1995', '07:25'], [25.85, '14.01.1995', '10:40'], [38.62, '14.01.1995', '12:15'], [45, '14.01.1995', '12:40'], [48.1, '14.01.1995', '13:05'], [58.35, '14.01.1995', '16:30'], [66.15, '14.01.1995', '20:45'], [76.75, '14.01.1995', '23:59'], [78.3, '14.01.2005', '07:03']];
