// Episode 2 (2005): hero look from the model sheet + 2005-era props.
Object.assign(HERO, { skin: '#d8a87e', hair: 'messy', hairCol: '#131116', top: 'plain', c1: '#2a2b31', c2: '#3a3b42', c3: '#3a3b42', pants: '#1e1f25', acid: false, shoes: '#d6d5d0', shoe2: '#a9a8a3' });
OUTFITS.splice(0, OUTFITS.length,
  { top: 'hoodie', c1: '#c8323c', c2: '#ffffff', c3: '#000', pants: '#3b5a8a', acid: false, logo: '' },
  { top: 'hoodie', c1: '#3a4a6a', c2: '#f2c230', c3: '#000', pants: '#2a2a30', acid: false, logo: '' },
  { top: 'track', c1: '#1d2a6b', c2: '#f2f2f2', c3: '#f2f2f2', pants: '#2a2a30', acid: false },
  { top: 'tshirt', c1: '#f2c230', c2: '#c8323c', c3: '#000', pants: '#4a6a9a', acid: false },
  { top: 'jacket', c1: '#2b2b2f', c2: '#000', c3: '#000', pants: '#4a6a9a', acid: false },
  { top: 'hoodie', c1: '#7a8a9a', c2: '#fff', c3: '#000', pants: '#2b3f66', acid: false, logo: '' },
  { top: 'tshirt', c1: '#e05a8a', c2: '#fff', c3: '#000', pants: '#4a6a9a', acid: false },
  { top: 'coat', c1: '#5a4a3a', c2: '#000', c3: '#000', pants: '#2a2a2a', acid: false },
  { top: 'jacket', c1: '#6a3a2a', c2: '#000', c3: '#000', pants: '#2a2a30', acid: false },
);
HAIRS.splice(0, HAIRS.length, ['short', '#3a2a1e'], ['cap', '#1d1d24'], ['long', '#6a3a1a'], ['short', '#16131a'], ['pony', '#c9a25a'], ['short', '#8a5a2a'], ['long', '#1a1214'], ['cap', '#c8323c'], ['short', '#4a3020']);

const NAVY = '#17203f', NAVY2 = '#1e2a50', NAVY3 = '#26355f', YEL = '#ffc93a', RED = '#e8323c';

// ---------- room ----------
function cityWindow(x, y, w, h, t, mode) {
  const sky = { dawn: ['#f2a65a', '#ffd98a'], day: ['#7fb2e0', '#d6ecf7'], evening: ['#2a2458', '#d8607a'], night: ['#0b1028', '#18244a'] }[mode];
  c.fillStyle = grad(0, y, 0, y + h, [[0, sky[0]], [1, sky[1]]]); c.fillRect(x, y, w, h);
  if (mode === 'dawn') circ(x + w * 0.7, y + h * 0.62, 34, '#fff1b0');
  if (mode === 'night') { circ(x + w * 0.75, y + h * 0.2, 22, '#f4f0d0'); for (let i = 0; i < 8; i++) circ(x + hash(i) * w, y + hash(i + 9) * h * 0.4, 2, '#fff'); }
  const dark = mode === 'night' || mode === 'evening';
  const r = rng(5);
  for (let i = 0; i < 6; i++) {
    const bw = 50 + r() * 50, bh = 100 + r() * 180, bx = x + i * w / 6 - 10;
    rect(bx, y + h - bh, bw, bh, dark ? '#141a36' : '#2a3560');
    for (let yy = y + h - bh + 12; yy < y + h - 10; yy += 22) for (let xx = bx + 8; xx < bx + bw - 10; xx += 16) if (hash(xx * 3 + yy) < (dark ? 0.45 : 0.25)) rect(xx, yy, 8, 10, YEL);
  }
  rect(x - 8, y - 8, w + 16, 12, '#cfd6e0'); rect(x - 8, y + h - 4, w + 16, 12, '#cfd6e0'); rect(x - 8, y - 8, 12, h + 16, '#cfd6e0'); rect(x + w - 4, y - 8, 12, h + 16, '#cfd6e0'); rect(x + w / 2 - 5, y, 10, h, '#cfd6e0');
  rect(x - 30, y + h + 6, w + 60, 18, '#b8c0cc');
  // blinds
  alpha(0.85, () => { for (let i = 0; i < 4; i++) rect(x, y + i * 14, w, 9, '#d7dde6'); });
}
function calendar2(x, y, s, front, back, flip, t = 0) {
  push(x, y, 0, s);
  rect(-150, -10, 300, 26, '#3a3a48'); circ(0, -18, 8, '#888');
  const page = (yr, col) => {
    rect(-140, 10, 280, 380, '#f4f1ea'); rect(-140, 10, 280, 92, col);
    txt(yr, 0, 58, 66, '#ffffff', { w: 900 }); txt('ЯНВАРЬ', 0, 128, 30, '#22222a', { w: 800 });
    ['П', 'В', 'С', 'Ч', 'П', 'С', 'В'].forEach((dd, i) => txt(dd, -105 + i * 35, 165, 17, i > 4 ? RED : '#555', { w: 700 }));
    for (let i = 0; i < 31; i++) { const cc = (i + 5) % 7, row = Math.floor((i + 5) / 7); txt(String(i + 1), -105 + cc * 35, 200 + row * 34, 19, cc > 4 ? RED : '#333', { w: 600 }); }
  };
  page(back || front, back ? '#2a7a4a' : '#2b5da8');
  if (back && flip > 0) {
    const sc = Math.cos(flip * Math.PI);
    c.save(); c.translate(0, 10); c.scale(1, sc); c.translate(0, -10);
    if (sc > 0) page(front, '#2b5da8'); else rect(-140, 10, 280, 380, '#d8d4ca');
    c.restore(); alpha(Math.sin(flip * Math.PI) * 0.4, () => rect(-140, 10, 280, 380, '#000'));
  } else if (back) page(front, '#2b5da8');
  pop();
}
function crtMonitor(x, y, s, screen, t, on = true) {
  // (x,y) = bottom centre of the stand
  push(x, y, 0, s);
  poly([-70, 0, 70, 0, 50, -30, -50, -30], '#c9c1ad'); rect(-30, -50, 60, 22, '#bdb5a0');
  rr(-170, -300, 340, 260, 18, '#ddd5c2'); rr(-150, -110, 300, 60, 8, '#cfc7b3');
  rr(-150, -282, 300, 210, 14, '#2a2a30');
  c.save(); c.beginPath(); c.roundRect(-138, -272, 276, 190, 12); c.clip();
  rect(-138, -272, 276, 190, '#0a0d14');
  if (on && screen) { push(-138, -272); screen(276, 190, t); pop(); }
  c.fillStyle = 'rgba(255,255,255,.07)'; c.beginPath(); c.ellipse(-60, -230, 120, 40, -0.3, 0, TAU); c.fill();
  for (let yy = -272; yy < -82; yy += 4) rect(-138, yy, 276, 1, 'rgba(0,0,0,.15)');
  c.restore();
  circ(130, -60, 7, on ? '#4ade6a' : '#555'); rect(-130, -64, 50, 8, '#bdb5a0');
  pop();
}
function tower(x, y, s, t, on, press = 0) {
  // (x,y) = bottom left
  push(x, y, 0, s);
  rr(0, -260, 100, 260, 8, '#ddd5c2'); rr(8, -248, 84, 34, 4, '#cfc7b3'); rect(14, -238, 72, 10, '#b5ad98');
  rr(8, -206, 84, 30, 4, '#cfc7b3'); rect(14, -194, 72, 6, '#b5ad98');
  circ(50, -130, 16 - press * 3, '#bdb5a0'); circ(50, -130, 11 - press * 3, press > 0.5 ? '#a9a18c' : '#cfc7b3');
  circ(30, -96, 5, on ? '#4ade6a' : '#666'); circ(70, -96, 5, on && Math.sin(t * 23) > 0.2 ? '#f2a03a' : '#666');
  for (let i = 0; i < 8; i++) rect(16, -70 + i * 7, 68, 3, '#c4bca8');
  pop();
}
function keyboard(x, y, s, t, typing = 0) {
  push(x, y, 0, s);
  rr(-200, -26, 400, 52, 8, '#d6cebb');
  for (let r = 0; r < 4; r++) for (let k = 0; k < 15; k++) { const pressed = typing && hash(Math.floor(t * 12) * 7 + r * 15 + k) < 0.06; rr(-190 + k * 25.5, -20 + r * 11, 22, 9, 2, pressed ? '#a69e8a' : '#ece6d6'); }
  pop();
}
function mouse(x, y, s, click = 0) { push(x, y, 0, s); ell(0, 0, 22, 32, '#ece6d6'); line(0, -30, 0, -6, '#b5ad98', 2); if (click) ell(-9, -18, 9, 12, '#c8bfa9'); pop(); line(x, y - 30 * s, x - 10 * s, y - 80 * s, '#999', 2); }
function cd(x, y, r, rot, t) {
  push(x, y, rot);
  c.fillStyle = c.createConicGradient ? (() => { const g = c.createConicGradient(t * 2, 0, 0); ['#dfe6f0', '#f6c6e6', '#c6e6f6', '#f6f0c6', '#dfe6f0'].forEach((col, i) => g.addColorStop(i / 4, col)); return g; })() : '#dde';
  c.beginPath(); c.arc(0, 0, r, 0, TAU); c.fill(); circ(0, 0, r * 0.32, '#aab'); circ(0, 0, r * 0.14, '#000');
  c.beginPath(); c.arc(0, 0, r * 0.75, -0.6, 0.2); c.strokeStyle = 'rgba(255,255,255,.7)'; c.lineWidth = r * 0.06; c.stroke();
  pop();
}
function jewelCase(x, y, w, col, label, rot = 0) { push(x, y, rot); rr(-w / 2, -w * 0.45, w, w * 0.9, 4, 'rgba(200,215,230,.6)'); rect(-w / 2 + 6, -w * 0.45 + 6, w - 12, w * 0.9 - 12, col); txt(label, 0, 0, w * 0.16, '#fff', { w: 900 }); pop(); }
function phone05(x, y, s, t, scr = 'home', rot = 0, pressKey = -1) {
  push(x, y, rot, s);
  rr(-80, -230, 160, 460, 60, '#2a3a5a'); rr(-72, -222, 144, 444, 54, '#3d5280');
  rr(-58, -190, 116, 120, 10, '#121620');
  c.save(); c.beginPath(); c.rect(-52, -184, 104, 108); c.clip();
  c.fillStyle = grad(0, -184, 0, -76, [[0, '#7ec8f0'], [1, '#2a6ab0']]); c.fillRect(-52, -184, 104, 108);
  for (let i = 0; i < 4; i++) rect(-46 + i * 7, -170 - i * 4, 5, 6 + i * 4, '#fff');
  rr(30, -176, 16, 9, 2, null, '#fff', 2);
  if (scr === 'home') { txt('07:15', 0, -138, 26, '#fff', { w: 900, f: 'DejaVu Sans Mono' }); txt('ПТ 14.01', 0, -112, 13, '#fff', { w: 700 }); txt('Меню', -26, -86, 11, '#fff', { w: 700 }); txt('Имена', 26, -86, 11, '#fff', { w: 700 }); }
  if (scr === 'ring') { txt('♪ МЕЛОДИЯ', 0, -150, 14, '#fff', { w: 900 }); for (let i = 0; i < 9; i++) { const hgt = 6 + Math.abs(Math.sin(t * 9 + i)) * 26; rect(-44 + i * 10, -86 - hgt, 7, hgt, YEL); } }
  if (scr === 'menu') { const icons = ['✉', '☎', '♫', '⚙', '◷', '★']; icons.forEach((ic, i) => { const sel = Math.floor(t * 2) % 6 === i; if (sel) rr(-48 + (i % 3) * 34, -176 + Math.floor(i / 3) * 44, 30, 38, 4, YEL); txt(ic, -33 + (i % 3) * 34, -157 + Math.floor(i / 3) * 44, 20, sel ? '#123' : '#fff', { w: 400, f: 'DejaVu Sans' }); }); }
  c.restore();
  rr(-60, -50, 120, 40, 18, '#2a3a5a'); circ(0, -30, 13, '#9aa8c0');
  const labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'];
  labels.forEach((L, i) => { const kx = -48 + (i % 3) * 48, ky = 20 + Math.floor(i / 3) * 44; rr(kx - 20, ky - 16, 40, 32, 12, pressKey === i ? YEL : '#c9d3e6'); txt(L, kx, ky, 18, '#1a2340', { w: 800 }); });
  pop();
}
function mp3(x, y, s, t, playing) {
  push(x, y, 0, s);
  rr(-80, -150, 160, 300, 26, '#eef0f4'); rr(-60, -128, 120, 90, 8, '#1a2a3a');
  c.save(); c.beginPath(); c.rect(-56, -124, 112, 82); c.clip(); rect(-56, -124, 112, 82, '#9fd0f0');
  txt('MP3', -30, -110, 13, '#123', { w: 900 }); txt(playing ? '▶ 03' : '■ 03', 30, -110, 12, '#123', { w: 800, f: 'DejaVu Sans' });
  txt('ЛЮБИМАЯ ПЕСНЯ', 0 - ((t * 30) % 60) + 20, -88, 11, '#123', { w: 800 });
  rect(-46, -62, 92, 6, '#5a8ab0'); rect(-46, -62, 92 * ((t * 0.05) % 1), 6, '#123');
  c.restore();
  circ(0, 40, 62, '#d6dae2'); circ(0, 40, 24, '#eef0f4');
  txt('▶‖', 0, 92, 16, '#556', { w: 800, f: 'DejaVu Sans' }); txt('◀◀', -42, 42, 13, '#556', { w: 800, f: 'DejaVu Sans' }); txt('▶▶', 42, 42, 13, '#556', { w: 800, f: 'DejaVu Sans' }); txt('MENU', 0, -8, 11, '#556', { w: 800 });
  rect(-10, 150, 20, 14, '#ccc');
  pop();
}
function earbudWire(x1, y1, x2, y2, col = '#f2f2f2') { c.beginPath(); c.moveTo(x1, y1); c.bezierCurveTo(x1, y1 + 160, x2, y2 + 200, x2, y2); c.strokeStyle = col; c.lineWidth = 4; c.stroke(); }
function digicam(x, y, s, flash) {
  push(x, y, 0, s); rr(-60, -40, 120, 80, 10, '#c9ccd4'); circ(16, 0, 28, '#2a2d36'); circ(16, 0, 16, '#4a5a7a'); circ(22, -6, 5, '#aac'); rect(-50, -32, 24, 14, flash ? '#fff' : '#eaeaea'); rect(-40, -48, 26, 10, '#999'); pop();
  if (flash) alpha(flash, () => { c.fillStyle = rgrad(x - 38 * s, y - 25 * s, 2, 260 * s, [[0, 'rgba(255,255,255,1)'], [1, 'rgba(255,255,255,0)']]); c.fillRect(x - 300 * s, y - 300 * s, 600 * s, 600 * s); });
}
function flipPhone(x, y, s, col = '#9aa4b8') { push(x, y, 0, s); rr(-28, -60, 56, 60, 10, col); rr(-22, -54, 44, 40, 4, '#7ec8f0'); rr(-28, 0, 56, 64, 10, shade(col, -0.15)); for (let i = 0; i < 9; i++) rr(-20 + (i % 3) * 14, 10 + Math.floor(i / 3) * 14, 10, 9, 2, '#dde'); pop(); }

// ---------- computer screens ----------
function scrBios(w, h, t) { rect(0, 0, w, h, '#000'); const lines = ['BIOS v6.00PG', 'CPU: 2400 MHz', 'Память: 512 MB  OK', 'HDD: 80 GB', 'Загрузка...']; lines.forEach((l, i) => { if (t * 6 > i) txt(l, 10, 18 + i * 20, 13, '#c8c8c8', { w: 700, f: 'DejaVu Sans Mono', a: 'left' }); }); }
function scrXPBoot(w, h, t) {
  rect(0, 0, w, h, '#000');
  const lg = 0.4 + 0.6 * cl(t * 2);
  alpha(lg, () => {
    [[-1, -1, '#f25022'], [1, -1, '#7fba00'], [-1, 1, '#00a4ef'], [1, 1, '#ffb900']].forEach(([a, b, col]) => { push(w / 2 - 34 + a * 11, h * 0.38 + b * 11, -0.12); rr(-10, -10, 20, 20, 3, col); pop(); });
    txt('Windows', w / 2 + 18, h * 0.38 - 4, 22, '#fff', { w: 700, f: 'DejaVu Sans', a: 'left' }); txt('XP', w / 2 + 100, h * 0.38 - 12, 12, '#f25022', { w: 900, a: 'left' });
  });
  rr(w / 2 - 50, h * 0.66, 100, 12, 6, null, '#888', 2);
  c.save(); c.beginPath(); c.roundRect(w / 2 - 48, h * 0.66 + 2, 96, 8, 4); c.clip(); const px = ((t * 70) % 130) - 30; for (let i = 0; i < 3; i++) rr(w / 2 - 48 + px + i * 10, h * 0.66 + 2, 8, 8, 2, '#3a7af2'); c.restore();
}
function xpDesktop(w, h, t) {
  c.fillStyle = grad(0, 0, 0, h, [[0, '#3a7ae0'], [0.55, '#a8d4f6'], [1, '#a8d4f6']]); c.fillRect(0, 0, w, h);
  for (let i = 0; i < 3; i++) alpha(0.85, () => ell(w * (0.25 + i * 0.3), h * 0.25 + Math.sin(i) * 10, 30, 10, '#fff'));
  c.beginPath(); c.moveTo(0, h * 0.7); c.quadraticCurveTo(w * 0.4, h * 0.45, w, h * 0.68); c.lineTo(w, h); c.lineTo(0, h); c.closePath(); c.fillStyle = '#4caa2a'; c.fill();
  [['Мой компьютер', 18], ['Корзина', 58], ['Игры', 98]].forEach(([n, yy]) => { rr(10, yy, 18, 16, 3, '#e8f0ff'); txt(n, 36, yy + 9, 8, '#fff', { w: 700, a: 'left' }); });
  rect(0, h - 16, w, 16, '#245edb'); rr(0, h - 16, 52, 16, [0, 8, 8, 0], '#3c9a3c'); txt('пуск', 26, h - 8, 9, '#fff', { w: 900 });
  rect(w - 40, h - 16, 40, 16, '#1290e8'); txt('07:21', w - 20, h - 8, 7, '#fff', { w: 700 });
}
function scrDesktop(w, h, t) { xpDesktop(w, h, t); }
function scrDialup(w, h, t) {
  xpDesktop(w, h, t);
  rr(w * 0.18, h * 0.2, w * 0.64, h * 0.5, 4, '#ece9d8'); rect(w * 0.18, h * 0.2, w * 0.64, 16, '#0a58d8'); txt('Подключение к Интернету', w * 0.2, h * 0.2 + 8, 8, '#fff', { w: 700, a: 'left' });
  txt('Набор номера...', w / 2, h * 0.36, 10, '#222', { w: 700 });
  const dots = ((Math.floor(t * 3) % 4) + 4) % 4; txt('●'.repeat(dots) + '○'.repeat(3 - dots), w / 2, h * 0.47, 12, '#0a58d8', { w: 400, f: 'DejaVu Sans' });
  rr(w * 0.3, h * 0.56, w * 0.4, 10, 2, '#fff', '#888', 1); rect(w * 0.3 + 1, h * 0.56 + 1, (w * 0.4 - 2) * ((t * 0.18) % 1), 8, '#3cba3c');
  // hourglass
  push(w * 0.62, h * 0.82, t * 2); poly([-6, -9, 6, -9, 0, 0], '#fff'); poly([-6, 9, 6, 9, 0, 0], '#fff'); pop();
}
function scrShooter(w, h, t) {
  c.fillStyle = grad(0, 0, 0, h, [[0, '#d9b98a'], [1, '#f2dfb6']]); c.fillRect(0, 0, w, h * 0.55);
  rect(0, h * 0.55, w, h * 0.45, '#b8925a');
  rect(0, h * 0.2, w * 0.25, h * 0.4, '#c9a46a'); rect(w * 0.75, h * 0.15, w * 0.25, h * 0.45, '#a8844e'); rect(w * 0.08, h * 0.25, w * 0.08, h * 0.12, '#1a1a1a');
  [[0.3, 0.45, 0.14], [0.44, 0.48, 0.1], [0.62, 0.42, 0.16]].forEach(([a, b, sz]) => { rect(w * a, h * b, w * sz, w * sz, '#8a6a34'); line(w * a, h * b, w * (a + sz), h * b + w * sz, '#6a4a20', 2); line(w * (a + sz), h * b, w * a, h * b + w * sz, '#6a4a20', 2); });
  const ex = w * (0.5 + Math.sin(t * 1.3) * 0.18);
  alpha(Math.sin(t * 1.3 + 1) > -0.6 ? 1 : 0, () => { rect(ex - 5, h * 0.37, 10, 22, '#2a2a20'); circ(ex, h * 0.35, 5, '#2a2a20'); });
  const shot = Math.sin(t * 9) > 0.7;
  poly([w * 0.62, h, w * 0.7, h * 0.72, w * 0.8, h * 0.7, w * 0.86, h], '#2a2a2a'); rect(w * 0.69, h * 0.66, w * 0.05, h * 0.08, '#3a3a3a');
  if (shot) circ(w * 0.71, h * 0.66, 12, '#ffd66a');
  line(w / 2 - 10, h / 2, w / 2 - 3, h / 2, '#3f3', 2); line(w / 2 + 3, h / 2, w / 2 + 10, h / 2, '#3f3', 2); line(w / 2, h / 2 - 10, w / 2, h / 2 - 3, '#3f3', 2); line(w / 2, h / 2 + 3, w / 2, h / 2 + 10, '#3f3', 2);
  txt('✚ 100', 8, h - 10, 11, '#ffd23a', { w: 900, a: 'left', f: 'DejaVu Sans' }); txt('30 | 90', w - 8, h - 10, 11, '#ffd23a', { w: 900, a: 'right' });
}
function scrBrowser(w, h, t) {
  rect(0, 0, w, h, '#ece9d8'); rect(0, 0, w, 14, '#0a58d8'); txt('Интернет — портал', 6, 7, 8, '#fff', { w: 700, a: 'left' });
  rr(30, 18, w - 40, 12, 2, '#fff', '#888', 1); txt('http://www.', 34, 24, 7, '#333', { w: 600, a: 'left' });
  rect(4, 34, w - 8, h - 50, '#fff');
  const loaded = cl((t % 4) / 3);
  rect(10, 40, w - 20, 22, '#e8323c'); txt('ПОРТАЛ 2005', w / 2, 51, 11, '#fff', { w: 900 });
  for (let i = 0; i < 6; i++) if (loaded > i / 6) rect(10, 70 + i * 16, (w - 20) * (0.5 + hash(i) * 0.5), 7, '#c9cfdc');
  if (loaded > 0.5) rect(w * 0.6, 70, w * 0.32, 60, '#7ab0e0');
  rect(0, h - 14, w, 14, '#245edb');
}
function scrChat(w, h, t) {
  xpDesktop(w, h, t);
  rr(w * 0.3, h * 0.08, w * 0.62, h * 0.78, 4, '#f4f6fa'); rect(w * 0.3, h * 0.08, w * 0.62, 14, '#3a9a3a'); txt('✿ Чат с другом', w * 0.32, h * 0.08 + 7, 8, '#fff', { w: 700, a: 'left', f: 'DejaVu Sans' });
  const msgs = [['Друг:', 'го в клуб?'], ['Я:', 'уже тут :)'], ['Друг:', 'ок, сажусь рядом'], ['Я:', ':D']];
  msgs.forEach((m, i) => { if (t * 1.5 > i) { txt(m[0], w * 0.33, h * 0.08 + 26 + i * 22, 8, i % 2 ? '#c8323c' : '#2a5ac8', { w: 900, a: 'left' }); txt(m[1], w * 0.33, h * 0.08 + 36 + i * 22, 9, '#222', { w: 600, a: 'left' }); } });
}
function scrTV05(w, h, t) {
  c.fillStyle = grad(0, 0, w, h, [[0, '#2a1a6a'], [1, '#e8323c']]); c.fillRect(0, 0, w, h);
  for (let i = 0; i < 6; i++) { const a = t * 0.7 + i; alpha(0.2, () => poly([w / 2, h * 0.6, w / 2 + Math.cos(a) * w, h * 0.6 + Math.sin(a) * w, w / 2 + Math.cos(a + 0.25) * w, h * 0.6 + Math.sin(a + 0.25) * w], YEL)); }
  const bx = w / 2 + Math.sin(t * 2) * w * 0.15; ell(bx, h * 0.68, w * 0.08, h * 0.2, '#111'); circ(bx, h * 0.42, w * 0.06, '#e7b48c'); ell(bx, h * 0.37, w * 0.07, h * 0.06, '#2a1a12');
  rect(0, h * 0.82, w, h * 0.18, 'rgba(0,0,0,.5)'); txt('ЛЮБИМАЯ ПЕРЕДАЧА', w / 2, h * 0.91, h * 0.08, YEL, { w: 900 });
}
function tv2005(x, y, w, screen, t, on) {
  const h = w * 0.78;
  push(x, y);
  rr(0, 0, w, h, w * 0.05, '#b9bec8'); rr(w * 0.02, h * 0.03, w * 0.96, h * 0.8, w * 0.04, '#2a2d36');
  const sx = w * 0.06, sy = h * 0.07, sw = w * 0.88, sh = h * 0.72;
  c.save(); c.beginPath(); c.roundRect(sx, sy, sw, sh, w * 0.05); c.clip(); rect(sx, sy, sw, sh, '#0d1018');
  if (on && screen) { push(sx, sy); screen(sw, sh, t); pop(); }
  c.fillStyle = 'rgba(255,255,255,.07)'; c.beginPath(); c.ellipse(sx + sw * 0.3, sy + sh * 0.2, sw * 0.3, sh * 0.12, -0.2, 0, TAU); c.fill();
  c.restore();
  txt('SILVER', w / 2, h * 0.9, w * 0.035, '#555', { w: 900 }); circ(w * 0.9, h * 0.9, w * 0.015, on ? '#e8323c' : '#555');
  pop();
}
function laptop10(x, y, s, t) { push(x, y, 0, s); poly([-260, 0, 260, 0, 300, 40, -300, 40], '#2a2a30'); rr(-240, -330, 480, 320, 14, '#18181c'); c.fillStyle = grad(0, -310, 0, -30, [[0, '#2a7ae0'], [1, '#8a3ac8']]); c.fillRect(-222, -312, 444, 284); for (let i = 0; i < 4; i++) rr(-200 + i * 110, -100, 90, 50, 8, 'rgba(255,255,255,.25)'); txt('2010', 0, -200, 70, '#fff', { w: 900 }); pop(); }
function smart10(x, y, s, t) { push(x, y, 0, s); rr(-90, -180, 180, 360, 26, '#111'); rr(-78, -150, 156, 290, 6, '#1a3a7a'); for (let i = 0; i < 12; i++) rr(-66 + (i % 4) * 38, -136 + Math.floor(i / 4) * 44, 28, 28, 7, ['#e8323c', YEL, '#3ac85a', '#3a8af2'][i % 4]); circ(0, 160, 10, '#333'); pop(); }

// ---------- cars & street ----------
function car05(x, y, s, col, t, dir = 1, kind = 0) {
  push(x, y + Math.sin(t * 20) * 1.2, 0, s * dir, s);
  c.beginPath();
  if (kind === 0) { c.moveTo(-250, -40); c.lineTo(-250, -95); c.quadraticCurveTo(-240, -115, -150, -118); c.quadraticCurveTo(-100, -185, 0, -185); c.quadraticCurveTo(100, -185, 150, -118); c.quadraticCurveTo(245, -112, 252, -80); c.lineTo(252, -40); }
  else { c.moveTo(-210, -40); c.lineTo(-210, -150); c.quadraticCurveTo(-200, -190, -120, -192); c.lineTo(60, -190); c.quadraticCurveTo(150, -150, 215, -100); c.lineTo(215, -40); }
  c.closePath(); c.fillStyle = col; c.fill();
  if (kind === 0) { poly([-130, -122, -10, -175, -10, -122], '#9cc6e6'); poly([5, -175, 70, -170, 130, -122, 5, -122], '#9cc6e6'); }
  else { poly([-190, -150, -110, -180, -110, -125, -190, -125], '#9cc6e6'); poly([-95, -180, 50, -180, 120, -125, -95, -125], '#9cc6e6'); }
  rect(-250, -80, 500, 6, shade(col, -0.2)); ell(235, -88, 14, 9, '#fff6c0'); ell(-240, -88, 10, 9, RED);
  [-150, 150].forEach(wx => { circ(wx * (kind ? 0.85 : 1), -35, 40, '#16161a'); circ(wx * (kind ? 0.85 : 1), -35, 20, '#c8ccd4'); push(wx * (kind ? 0.85 : 1), -35, t * 8); for (let k = 0; k < 5; k++) { push(0, 0, k * TAU / 5); rect(-2, -18, 4, 14, '#888'); pop(); } pop(); });
  pop();
}
function shop05(x, y, w, h, sign, col, t, items) {
  rect(x, y - h, w, h, '#2a3560'); rect(x, y - h, w, 70, col); txt(sign, x + w / 2, y - h + 35, 32, '#fff', { w: 900 });
  rr(x + 20, y - h + 90, w - 40, h - 110, 4, '#9fc6e0'); alpha(0.25, () => rect(x + 20, y - h + 90, (w - 40) * 0.3, h - 110, '#fff'));
  if (items) items(x + 20, y - h + 90, w - 40, h - 110);
  rect(x + w / 2 - 40, y - 140, 80, 140, '#1a2240');
}
function billboard(x, y, w, h, t, draw) { line(x + w * 0.3, y, x + w * 0.3, y + 400, '#333', 14); line(x + w * 0.7, y, x + w * 0.7, y + 400, '#333', 14); rr(x, y - h, w, h, 6, '#fff'); push(x + 8, y - h + 8); draw(w - 16, h - 16, t); pop(); }
function cityDay(t) {
  c.fillStyle = grad(0, -400, 0, 800, [[0, '#4a7ac8'], [1, '#ffd98a']]); c.fillRect(-1500, -1500, 5000, 4000);
  circ(1650, 160, 60, '#fff1b0');
  for (let i = 0; i < 8; i++) { const bx = -500 + i * 430, bh = 360 + (i % 3) * 140; rect(bx, 760 - bh, 380, bh, i % 2 ? NAVY2 : NAVY3); for (let r = 0; r < bh / 60 - 1; r++) for (let k = 0; k < 6; k++) rect(bx + 24 + k * 58, 760 - bh + 26 + r * 60, 30, 34, hash(i * 99 + r * 7 + k) < 0.25 ? YEL : '#3a4a78'); }
}
function club(t) {
  c.fillStyle = grad(0, -400, 0, 900, [[0, '#0d1230'], [1, '#1c2350']]); c.fillRect(-1500, -1500, 5000, 4000);
  rect(-600, 780, 3400, 700, '#151a36');
  for (let i = 0; i < 12; i++) line(-600 + i * 300, 780, 960 + (i - 6) * 900, 1500, 'rgba(255,255,255,.05)', 3);
  rr(660, 60, 600, 110, 20, null, '#ff3a8a', 8); txt('КОМПЬЮТЕРНЫЙ КЛУБ', 960, 115, 46, '#ff7ab0', { w: 900 });
  alpha(0.3 + 0.1 * Math.sin(t * 9), () => { c.fillStyle = rgrad(960, 115, 10, 500, [[0, 'rgba(255,58,138,.5)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(300, -200, 1300, 700); });
  rr(80, 200, 300, 200, 10, '#232c5a'); txt('ЧАС — 30 руб.', 230, 260, 32, YEL, { w: 900 }); txt('НОЧЬ — 150', 230, 320, 32, '#fff', { w: 900 });
}
function station(x, y, s, t, screen, kidIdx, kidOpts = {}) {
  push(x, y, 0, s);
  rect(-240, -10, 480, 30, '#3a2f52'); rect(-230, 20, 20, 160, '#2a2240'); rect(210, 20, 20, 160, '#2a2240');
  crtMonitor(0, -10, 0.95, screen, t, true);
  alpha(0.35, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(0, -150, 10, 360, [[0, 'rgba(120,170,255,.6)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-400, -500, 800, 800); });
  keyboard(0, 12, 0.6, t, 1);
  if (kidIdx !== undefined && kidIdx !== null) { const o = Object.assign({ x: 0, y: 330, s: 0.78, view: 'back', sit: true, tilt: Math.sin(t * 3 + kidIdx) * 0.04, headphones: true, hl: [-90, -230], hr: [90, -230] }, kidIdx >= 0 ? (() => { const hr = HAIRS[(kidIdx * 5 + 2) % HAIRS.length]; return Object.assign({ hair: hr[0], hairCol: hr[1], skin: SKINS[kidIdx % 4] }, OUTFITS[kidIdx % OUTFITS.length]); })() : {}, kidOpts); person(o); }
  pop();
}
