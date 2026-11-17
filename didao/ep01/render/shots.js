// DIDAO — Episode 1 "ONE DAY BEFORE GTA 6" — shot list.
// start = position on the final timeline (seconds). Voice-over starts at 2.0s.
// Every shot is rendered as its own clip; the assembler cross-fades them (XF seconds overlap).
const XF = 0.4, TOTAL = 120.0;

function bgDark(ctx, c = '#07060d') { ctx.fillStyle = c; ctx.fillRect(0, 0, W, H); }
function cam(ctx, t, d, z0, z1, cx = W / 2, cy = H / 2, px = 0, py = 0) { const k = smooth(t / d); const z = lerp(z0, z1, k); ctx.translate(cx + px * k, cy + py * k); ctx.scale(z, z); ctx.translate(-cx, -cy); }

// ---------- room (shared set for all hero-at-home shots) ----------
function room(ctx, t, o = {}) {
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#1a1c2c'], [1, '#101120']]); ctx.fillRect(0, 0, W, H);
  // window with distant city
  const wx = o.winX ?? 1260, wy = 150, ww = 520, wh = 380;
  ctx.save(); rr(ctx, wx, wy, ww, wh, 8); ctx.clip();
  ctx.fillStyle = vgrad(ctx, wy, wy + wh, o.dawn ? [[0, lerp(0, 1, 0) ? '#000' : '#2b2f6a'], [1, '#ff9a6a']] : [[0, '#060714'], [1, '#2a1546']]);
  ctx.fillRect(wx, wy, ww, wh);
  if (o.dawn) { ctx.globalAlpha = o.dawn; ctx.fillStyle = vgrad(ctx, wy, wy + wh, [[0, '#4a5cae'], [1, '#ffb27a']]); ctx.fillRect(wx, wy, ww, wh); ctx.globalAlpha = 1; }
  const sk = skylineCanvas('roomsky', 900, 300, { seed: 77, minW: 30, maxW: 80, minH: 60, maxH: 240, color: '#0c0a1e', windows: true, lit: 0.5, win: 3 });
  ctx.drawImage(sk, wx - 120, wy + wh - 300);
  if (o.rain) { ctx.strokeStyle = 'rgba(170,190,255,0.35)'; ctx.lineWidth = 2; const r = rng(5); for (let i = 0; i < 70; i++) { const x = wx + r() * ww, sp = 500 + r() * 400, y = wy + ((r() * wh + t * sp) % wh); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 4, y + 22); ctx.stroke(); } }
  ctx.restore();
  ctx.strokeStyle = '#2c2f45'; ctx.lineWidth = 16; ctx.strokeRect(wx, wy, ww, wh); ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(wx + ww / 2, wy); ctx.lineTo(wx + ww / 2, wy + wh); ctx.moveTo(wx, wy + wh / 2); ctx.lineTo(wx + ww, wy + wh / 2); ctx.stroke();
  // poster (original art: palm + sun)
  ctx.save(); ctx.translate(o.posterX ?? 170, 150); ctx.rotate(-0.03); fillRR(ctx, 0, 0, 260, 360, 6, '#2b1440'); ctx.save(); rr(ctx, 12, 12, 236, 336, 4); ctx.clip(); ctx.translate(12, 12); viceSunsetScene(ctx, 236, 336, 0, { noCar: true }); ctx.restore(); text(ctx, 'VICE', 130, 300, { size: 54, font: FONT_T, weight: 400, color: '#fff', glow: C.pink, blur: 20 }); ctx.restore();
  // shelf
  fillRR(ctx, 120, 640, 380, 16, 4, '#2a2436');
  [[150, '#ff4f6d'], [185, '#2f6fff'], [215, '#f4b23e'], [250, '#2bb673']].forEach(([x, c], i) => fillRR(ctx, x, 560 + (i % 2) * 14, 28, 80 - (i % 2) * 14, 3, c));
  // floor + desk
  ctx.fillStyle = '#0c0d16'; ctx.fillRect(0, 860, W, 220);
  if (o.wallClock) o.wallClock(ctx);
}
function desk(ctx, y = 820) { fillRR(ctx, 260, y, 1400, 40, 8, '#4a3428'); ctx.fillStyle = '#3a281e'; ctx.fillRect(300, y + 40, 40, 260); ctx.fillRect(1580, y + 40, 40, 260); }
function keyboard(ctx, x, y, w, glowC) { fillRR(ctx, x, y, w, 46, 8, '#c9c2ad'); ctx.fillStyle = '#a49c87'; for (let r = 0; r < 3; r++) for (let i = 0; i < 14; i++) fillRR(ctx, x + 14 + i * (w - 28) / 14, y + 8 + r * 12, (w - 28) / 14 - 4, 9, 2, '#a49c87'); }

// ---------- screen contents ----------
function scrTrailer(ctx, w, h, t) { viceSunsetScene(ctx, w, h, t); fillRR(ctx, 20, h - 34, w - 40, 8, 4, 'rgba(255,255,255,0.3)'); fillRR(ctx, 20, h - 34, (w - 40) * (0.2 + t * 0.05), 8, 4, C.red); text(ctx, 'ТРЕЙЛЕР', 26, 30, { size: Math.max(18, h * 0.06), align: 'left', color: '#fff', weight: 800 }); }
function scrBrowserBase(ctx, w, h, title) { ctx.fillStyle = '#0f0f16'; ctx.fillRect(0, 0, w, h); ctx.fillStyle = '#1b1b26'; ctx.fillRect(0, 0, w, 70); [C.red, C.yellow, C.green].forEach((c, i) => circle(ctx, 34 + i * 30, 35, 9, c)); fillRR(ctx, 150, 16, w - 300, 38, 19, '#2a2a38'); text(ctx, title, 180, 36, { size: 20, align: 'left', color: '#99a', weight: 400 }); }
function videoCard(ctx, x, y, w, kind, title, views, t, hl = 0) {
  const h = w * 0.5625; if (hl) { ctx.save(); ctx.shadowColor = C.yellow; ctx.shadowBlur = 40 * hl; fillRR(ctx, x - 6, y - 6, w + 12, h + 12, 18, `rgba(255,210,63,${hl})`); ctx.restore(); }
  viceThumb(ctx, x, y, w, h, kind, t);
  ctx.save(); ctx.font = `800 ${Math.round(w * 0.075)}px ${FONT}`; ctx.textAlign = 'left'; ctx.lineJoin = 'round'; ctx.lineWidth = 8; ctx.strokeStyle = '#000'; const lines = wrapLines(ctx, title, w - 30); lines.slice(0, 2).forEach((l, i) => { ctx.strokeText(l, x + 16, y + 40 + i * w * 0.08); ctx.fillStyle = i ? C.yellow : '#fff'; ctx.fillText(l, x + 16, y + 40 + i * w * 0.08); }); ctx.restore();
  text(ctx, title, x, y + h + 30, { size: w * 0.055, align: 'left', color: '#fff', weight: 600 });
  text(ctx, views, x, y + h + 64, { size: w * 0.048, align: 'left', color: '#9aa0b4', weight: 400 });
}

const SHOTS = [
  // ===================== SCENE 1 — THE WHOLE WORLD IS WAITING =====================
  { id: 's01_city', start: 0.0, scene: 1, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.12, 1.0, W / 2, H / 2, -40, 0);
    sunsetSky(ctx, W, H, 760); retroSun(ctx, 960, 650, 240);
    cityLayers(ctx, t, 790, t * 25, false, 10);
    // billboard on tower
    ctx.fillStyle = '#1a0a26'; ctx.fillRect(1240, 300, 30, 220); ctx.fillRect(1460, 300, 30, 220);
    fillRR(ctx, 1150, 150, 430, 210, 10, '#12081c'); ctx.save(); rr(ctx, 1162, 162, 406, 186, 6); ctx.clip(); ctx.fillStyle = vgrad(ctx, 162, 348, [[0, '#ff2e88'], [1, '#7b2cff']]); ctx.fillRect(1162, 162, 406, 186); ctx.restore();
    neonText(ctx, 'GTA 6', 1365, 225, 84, C.yellow, { flicker: t < 0.6 ? (Math.sin(t * 60) > 0 ? 1 : 0.3) : 1 }); text(ctx, 'ВЫХОДИТ ЗАВТРА', 1365, 310, { size: 34, color: '#fff', weight: 800 });
    ctx.fillStyle = vgrad(ctx, 760, H, [[0, '#3a1050'], [1, '#0e0518']]); ctx.fillRect(0, 780, W, 300);
    ctx.fillStyle = '#0b0412'; ctx.fillRect(0, 930, W, 150); ctx.fillStyle = 'rgba(255,200,120,0.6)'; for (let i = 0; i < 20; i++) ctx.fillRect(((i * 130 - t * 300) % 2600 + 2600) % 2600 - 300, 1000, 60, 6);
    car(ctx, -500 + t * 520, 990, 1.0, C.pink, { lights: true }); car(ctx, 2300 - t * 420, 1060, 1.1, C.cyan, { lights: true, flip: true });
    palm(ctx, 120, 1100, 700, { sway: t * 1.3, lean: 0.22 }); palm(ctx, 1800, 1100, 620, { sway: t * 1.3 + 1, lean: -0.25 });
    ctx.restore();
    const a = smooth(seg(t, 0.2, 0.9)) * (1 - smooth(seg(t, 2.6, 3.4)));
    if (a > 0) { ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, W, H); neonText(ctx, 'DIDAO', W / 2, H / 2 - 40, 190, C.pink, { spacing: 20 }); text(ctx, 'ЭПИЗОД 1  ·  ЗА ДЕНЬ ДО GTA 6', W / 2, H / 2 + 100, { size: 44, color: '#fff', weight: 800, spacing: 6 }); ctx.restore(); }
  } },
  { id: 's02_countdown', start: 5.0, scene: 1, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.08);
    nightSky(ctx, W, H, H, 4); cityLayers(ctx, t, H + 40, t * 15, true, 30);
    ctx.fillStyle = 'rgba(5,3,15,0.55)'; ctx.fillRect(0, 0, W, H);
    const r = rng(9); ctx.save(); ctx.globalCompositeOperation = 'lighter'; for (let i = 0; i < 40; i++) { const c = [C.pink, C.cyan, C.orange, C.purple][i % 4]; glow(ctx, r() * W, r() * H, 30 + r() * 90, c, 0.25); } ctx.restore();
    ctx.restore();
    const secs = 59 - Math.floor(t); const hh = '23', mm = '59', ss = String(Math.max(0, secs)).padStart(2, '0');
    text(ctx, 'ДО ВЫХОДА GTA 6 ОСТАЛОСЬ', W / 2, 250, { size: 46, color: '#cfd3ff', weight: 700, spacing: 8, alpha: smooth(seg(t, 0, 0.5)) });
    const pulse = 1 + 0.03 * Math.exp(-((t % 1) * 6));
    ctx.save(); ctx.translate(W / 2, 450); ctx.scale(pulse, pulse);
    fillRR(ctx, -560, -130, 1120, 260, 36, 'rgba(10,8,22,0.85)'); ctx.strokeStyle = 'rgba(255,46,136,0.7)'; ctx.lineWidth = 4; rr(ctx, -560, -130, 1120, 260, 36); ctx.stroke();
    neonText(ctx, `${hh}:${mm}:${ss}`, 0, 8, 190, C.cyan, { font: '"Rubik", sans-serif' });
    ctx.restore();
    const k = easeOutBack(seg(t, 1.0, 1.6));
    if (t > 1.0) { ctx.save(); ctx.translate(W / 2, 790); ctx.scale(k, k); neonText(ctx, 'ONE DAY LEFT.', 0, 0, 170, C.pink, { flicker: t < 1.5 && Math.sin(t * 70) < 0 ? 0.4 : 1, spacing: 6 }); ctx.restore(); }
  } },
  { id: 's03_store', start: 10.0, scene: 1, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.05, 1.0, W / 2, H / 2, 60, 0);
    sunsetSky(ctx, W, H, 600); cityLayers(ctx, t, 620, 0, false, 40);
    // street
    ctx.fillStyle = '#2a1b3a'; ctx.fillRect(0, 880, W, 200); ctx.fillStyle = '#3a2a4c'; ctx.fillRect(0, 860, W, 30);
    // store facade
    fillRR(ctx, 120, 230, 1100, 660, 6, '#24163a'); ctx.fillStyle = '#1a0f2a'; ctx.fillRect(120, 230, 1100, 120);
    neonText(ctx, 'GAME ZONE', 670, 292, 92, C.cyan, { flicker: 0.9 + 0.1 * Math.sin(t * 13) });
    // shop windows
    fillRR(ctx, 170, 400, 560, 400, 10, 'rgba(255,190,120,0.25)'); fillRR(ctx, 800, 400, 160, 480, 6, '#140b20');
    ctx.save(); rr(ctx, 170, 400, 560, 400, 10); ctx.clip();
    viceThumb(ctx, 200, 420, 300, 220, 'sun', t); text(ctx, 'GTA 6', 350, 470, { size: 58, font: FONT_T, weight: 400, color: '#fff', stroke: '#000', strokeW: 8 }); text(ctx, 'ПРЕДЗАКАЗ', 350, 610, { size: 30, color: C.yellow, weight: 800, stroke: '#000', strokeW: 6 });
    [[520, 640, 170, 140, '#1f2a44', 'ИГРОВОЙ ПК'], [520, 470, 170, 160, '#2a2a33', 'КОНСОЛЬ'], [200, 670, 290, 120, '#3a1d4c', 'МОНИТОР 4K']].forEach(([x, y, w, h, c, l]) => { fillRR(ctx, x, y, w, h, 8, c); ctx.strokeStyle = C.cyan; ctx.lineWidth = 2; rr(ctx, x + 6, y + 6, w - 12, h - 12, 6); ctx.stroke(); text(ctx, l, x + w / 2, y + h / 2, { size: 24, color: '#fff', weight: 800 }); });
    ctx.restore();
    if (t > 3.6) { const k = easeOutBack(seg(t, 3.6, 4.0)); ctx.save(); ctx.translate(605, 545); ctx.rotate(-0.2); ctx.scale(k, k); fillRR(ctx, -120, -36, 240, 72, 10, C.red); text(ctx, 'РАСПРОДАНО', 0, 2, { size: 32, color: '#fff', weight: 900 }); ctx.restore(); }
    // queue
    for (let i = 0; i < 16; i++) { const x = 1010 + i * 92, bob = Math.sin(t * 3 + i) * 3; person(ctx, x, 950 + (i % 2) * 18, 0.95 - (i % 3) * 0.03, 100 + i, { bob, phone: i % 3 === 0, back: false }); }
    // customer leaving with a box
    const lx = 820 - t * 170; person(ctx, lx, 1010, 1.08, 7, { box: '#1f2a44', boxLabel: 'ПК', bob: Math.abs(Math.sin(t * 6)) * -8 });
    const lx2 = 920 - Math.max(0, t - 2) * 150; if (t > 2) person(ctx, lx2, 1030, 1.08, 13, { box: '#2a2a33', boxLabel: 'КОНСОЛЬ', bob: Math.abs(Math.sin(t * 6 + 1)) * -8 });
    palm(ctx, 1840, 1080, 560, { sway: t, lean: -0.2 });
    ctx.restore();
    text(ctx, 'ОЧЕРЕДЬ: 3 КВАРТАЛА', 1470, 160, { size: 40, color: '#fff', weight: 900, stroke: '#000', strokeW: 8, alpha: smooth(seg(t, 1, 1.4)) });
  } },
  { id: 's04_internet', start: 16.6, scene: 1, draw(ctx, t, d) {
    bgDark(ctx, '#0b0b14');
    ctx.save(); cam(ctx, t, d, 1.0, 1.1, W / 2, H / 2);
    const scroll = t * 90;
    const posts = [['ЗАВТРА ВЫХОДИТ GTA 6!!!', 'sun'], ['Я ВЗЯЛ ОТПУСК РАДИ GTA 6', 'night'], ['КУПИЛ НОВЫЙ ПК ЗА НОЧЬ', 'car'], ['ВСЕ СЕКРЕТЫ GTA 6', 'sun2'], ['GTA 6: ОБРАТНЫЙ ОТСЧЁТ', 'night'], ['ПРОВЕРЯЮ ГРАФИКУ GTA 6', 'sun'], ['ГДЕ КУПИТЬ GTA 6 ДЕШЕВЛЕ?', 'car'], ['СТРИМ ДО ПОЛУНОЧИ', 'night'], ['GTA 6 СЛОМАЕТ ИНТЕРНЕТ', 'sun2']];
    for (let i = 0; i < 12; i++) { const col = i % 3, row = Math.floor(i / 3); const x = 140 + col * 560, y = 200 + row * 420 - scroll; const p = posts[i % posts.length]; videoCard(ctx, x, y, 500, p[1], p[0], `${(1.1 + ((i * 37) % 90) / 10).toFixed(1)} млн просмотров · ${i + 1} ч назад`, t); }
    ctx.restore();
    // trending panel
    fillRR(ctx, 1460, 120, 400, 520, 24, 'rgba(18,18,30,0.94)'); text(ctx, 'В ТРЕНДАХ', 1500, 175, { size: 30, align: 'left', color: C.yellow, weight: 900 });
    ['#GTA6', '#ЗавтраGTA6', '#ViceCity', '#ОдинДень', '#GTA6Release'].forEach((s, i) => { text(ctx, `${i + 1}  ${s}`, 1500, 240 + i * 62, { size: 30, align: 'left', color: '#fff', weight: 700 }); text(ctx, `${fmt(4800000 / (i + 1) + t * 91234 / (i + 1))} публ.`, 1500, 270 + i * 62, { size: 18, align: 'left', color: '#8a8fa8', weight: 400 }); });
    // huge counter
    fillRR(ctx, 360, 690, 1200, 170, 30, 'rgba(255,46,136,0.92)');
    text(ctx, '#GTA6', 470, 775, { size: 64, color: '#fff', weight: 900, align: 'left' });
    text(ctx, fmt(48312904 + t * 412345) + ' публикаций', 1520, 775, { size: 58, color: '#fff', weight: 800, align: 'right' });
    for (let i = 0; i < 6; i++) { const t0 = 0.4 + i * 0.75; if (t > t0 && t < t0 + 2.2) { const k = t - t0; notif(ctx, 60 + (i % 2) * 40, 120 + (i % 4) * 120 - k * 30, 600, ['Новый пост о GTA 6', 'Тебя отметили в #GTA6', '1 892 новых видео', 'Новость: серверы готовы', 'Друг: «завтра всю ночь играем»', 'Магазин: остался 1 ПК'][i], 'только что', [C.pink, C.cyan, C.orange, C.purple, C.green, C.red][i], smooth(seg(k, 0, 0.25)) * (1 - smooth(seg(k, 1.8, 2.2)))); } }
    // "but there's one problem" — screen dims
    const dk = smooth(seg(t, d - 1.6, d)); if (dk > 0) { ctx.fillStyle = `rgba(0,0,0,${dk * 0.85})`; ctx.fillRect(0, 0, W, H); }
  } },

  // ===================== SCENE 2 — NO MONEY =====================
  { id: 's05_room', start: 23.2, scene: 2, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.12, 900, 560);
    room(ctx, t, { rain: true });
    desk(ctx);
    crtMonitor(ctx, 760, 430, 400, 300, (c, w, h) => scrTrailer(c, w, h, t + 3));
    glow(ctx, 960, 580, 700, 'rgba(255,90,140,0.25)');
    keyboard(ctx, 780, 790, 360);
    // hero from behind, sitting
    litHero(ctx, { x: 960, y: 690, R: 120, view: 'back', body: 'bust', arms: 'down', bob: Math.sin(t * 1.5) * 2 }, { from: [960, 480, 500, 'rgba(255,120,170,0.35)'] });
    // lamp
    ctx.fillStyle = '#2b2d3c'; ctx.fillRect(1430, 600, 14, 220); ellipse(ctx, 1437, 600, 70, 30, '#3a3c4e'); glow(ctx, 1437, 640, 240, 'rgba(255,190,110,0.25)');
    ctx.restore(); vignette(ctx, 0.6);
  } },
  { id: 's06_price', start: 27.0, scene: 2, draw(ctx, t, d) {
    bgDark(ctx, '#05050a');
    ctx.save(); cam(ctx, t, d, 1.0, 1.06, 960, 540);
    crtMonitor(ctx, 160, 70, 1600, 900, (c, w, h) => {
      scrBrowserBase(c, w, h, 'store.games / gta-6');
      viceThumb(c, 80, 130, 620, 700, 'sun', t);
      text(c, 'GTA 6', 390, 220, { size: 110, font: FONT_T, weight: 400, color: '#fff', stroke: '#000', strokeW: 10 });
      text(c, 'GTA 6 — Стандартное издание', 780, 200, { size: 54, align: 'left', color: '#fff', weight: 800 });
      text(c, 'Выход: ЗАВТРА, 00:00', 780, 270, { size: 34, align: 'left', color: '#9aa0b4', weight: 400 });
      text(c, '$69.99', 780, 420, { size: 160, align: 'left', color: C.yellow, weight: 900 });
      const hover = t > 1.1 ? 1 : 0; fillRR(c, 780, 540, 460, 120, 24, hover ? '#43ff8f' : C.green); text(c, 'КУПИТЬ', 1010, 600, { size: 56, color: '#05210f', weight: 900 });
      text(c, 'Твой баланс:  $0.00', 780, 730, { size: 40, align: 'left', color: '#ff8a95', weight: 700 });
      if (t > 1.9) { const sh = Math.sin(t * 60) * 18 * Math.exp(-(t - 1.9) * 5); const k = easeOutBack(seg(t, 1.9, 2.2)); c.save(); c.translate(w / 2 + sh, h / 2 + 40); c.scale(k, k); c.shadowColor = 'rgba(0,0,0,0.6)'; c.shadowBlur = 50; fillRR(c, -440, -150, 880, 300, 30, '#24151c'); c.shadowBlur = 0; c.strokeStyle = C.red; c.lineWidth = 6; rr(c, -440, -150, 880, 300, 30); c.stroke(); text(c, 'ОПЛАТА ОТКЛОНЕНА', 0, -50, { size: 64, color: C.red, weight: 900 }); text(c, 'Недостаточно средств', 0, 50, { size: 44, color: '#fff', weight: 600 }); c.restore(); }
      const cx = lerp(1500, 1010, easeOut(seg(t, 0.2, 1.2))), cy = lerp(820, 610, easeOut(seg(t, 0.2, 1.2)));
      cursor(c, cx, cy, 1.6, t > 1.7 && t < 2.3 ? (t - 1.7) / 0.6 : 0);
    });
    ctx.restore(); vignette(ctx, 0.5);
  } },
  { id: 's07_wallet', start: 30.6, scene: 2, draw(ctx, t, d) {
    // top-down desk, hero's hands open an empty wallet
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#4a3428'], [1, '#2e2018']]); ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 0.12; ctx.strokeStyle = '#000'; ctx.lineWidth = 3; for (let i = 0; i < 12; i++) { ctx.beginPath(); ctx.moveTo(0, i * 95 + 30); ctx.bezierCurveTo(600, i * 95 + 60, 1200, i * 95, W, i * 95 + 40); ctx.stroke(); } ctx.globalAlpha = 1;
    glow(ctx, 960, 200, 900, 'rgba(120,200,255,0.18)');
    ctx.save(); cam(ctx, t, d, 1.0, 1.1, 960, 560);
    const open = easeOut(seg(t, 0.2, 0.9));
    ctx.save(); ctx.translate(960, 560);
    fillRR(ctx, -380, -10, 760, 300, 30, '#5b3420'); ctx.strokeStyle = '#7a4a2e'; ctx.setLineDash([14, 10]); ctx.lineWidth = 5; rr(ctx, -360, 10, 720, 260, 24); ctx.stroke(); ctx.setLineDash([]);
    fillRR(ctx, -330, 30, 660, 180, 16, '#3a2014');
    ctx.save(); ctx.scale(1, lerp(1, -1, open)); fillRR(ctx, -380, -300, 760, 300, 30, '#6b3c24'); ctx.strokeStyle = '#8a5434'; ctx.setLineDash([14, 10]); ctx.lineWidth = 5; rr(ctx, -360, -280, 720, 260, 24); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
    // coins
    [[-120, 150, 1.0], [-40, 170, 0.8], [40, 140, 0.9], [110, 175, 0.7]].forEach(([x, y, s], i) => { const k = easeOut(seg(t, 0.9 + i * 0.12, 1.2 + i * 0.12)); if (k > 0) { circle(ctx, x, y - (1 - k) * 80, 34 * s, '#d9a93a'); circle(ctx, x, y - (1 - k) * 80, 26 * s, '#f2c14e'); } });
    ctx.restore();
    // moth flying out
    if (t > 0.8) { const k = t - 0.8; const mx = 960 + Math.sin(k * 3) * 90 + k * 120, my = 520 - k * 260; ctx.save(); ctx.translate(mx, my); const f = Math.sin(t * 40) * 0.6; ellipse(ctx, -18, 0, 26, 14 * Math.abs(Math.cos(f)) + 4, '#bdb6a6', -0.4); ellipse(ctx, 18, 0, 26, 14 * Math.abs(Math.cos(f)) + 4, '#bdb6a6', 0.4); ellipse(ctx, 0, 0, 7, 18, '#6d6658'); ctx.restore(); }
    // hands (same round hands as the hero)
    circle(ctx, 960 - 470, 640 + Math.sin(t * 2) * 4, 70, C.skin); circle(ctx, 960 + 470, 640 - Math.sin(t * 2) * 4, 70, C.skin);
    fillRR(ctx, 960 - 600, 600, 120, 500, 50, C.sweater); fillRR(ctx, 960 + 480, 600, 120, 500, 50, C.sweater);
    ctx.restore();
    const k = easeOutBack(seg(t, 1.3, 1.7)); if (t > 1.3) { ctx.save(); ctx.translate(960, 220); ctx.scale(k, k); text(ctx, '$3.27', 0, 0, { size: 150, color: '#fff', weight: 900, stroke: '#000', strokeW: 14 }); ctx.restore(); text(ctx, 'нужно $69.99', 960, 330, { size: 48, color: '#ff8a95', weight: 800, stroke: '#000', strokeW: 8, alpha: smooth(seg(t, 1.6, 1.9)) }); }
  } },
  { id: 's08_sad', start: 33.0, scene: 2, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.08, 960, 520);
    room(ctx, t, { rain: true, winX: 1180, posterX: 140 });
    litHero(ctx, { x: 960, y: 470, R: 230, view: 'front', expr: 'sad', body: 'bust', arms: 'down', bob: Math.sin(t * 1.2) * 3 + easeOut(seg(t, 0.4, 1.4)) * 18, tilt: -0.04, blink: (t > 1.6 && t < 1.72), lookY: 1 }, { tint: '#3a6cff', tintA: 0.07, from: [960, 1200, 900, 'rgba(110,180,255,0.18)'] });
    // desk edge in foreground with monitor glow
    ctx.fillStyle = '#2e2018'; ctx.fillRect(0, 990, W, 90); glow(ctx, 960, 1080, 700, 'rgba(120,190,255,0.35)');
    ctx.restore(); vignette(ctx, 0.7);
  } },

  // ===================== SCENE 3 — UNEXPECTED IDEA =====================
  { id: 's09_feed', start: 35.6, scene: 3, draw(ctx, t, d) {
    bgDark(ctx, '#05050a');
    ctx.save(); cam(ctx, t, d, 1.0, 1.35, 1180, 380);
    crtMonitor(ctx, 160, 70, 1600, 900, (c, w, h) => {
      scrBrowserBase(c, w, h, 'видео / поиск: GTA 6');
      const items = [['Я ПРОЖИЛ ДЕНЬ В GTA 6', 'sun', 5.1], ['ВСЁ, ЧТО ИЗВЕСТНО О GTA 6', 'night', 2.4], ['ТОП-10 МАШИН GTA 6', 'car', 3.8], ['GTA 6 ЗА 60 СЕКУНД', 'night', 1.9], ['ЧТО ЕСЛИ GTA 6 — РЕАЛЬНОСТЬ?', 'sun2', 7.3], ['ГОРОД GTA 6: ОБЗОР', 'car', 4.6]];
      items.forEach(([ti, k, v], i) => { const x = 60 + (i % 3) * 510, y = 110 + Math.floor(i / 3) * 400; videoCard(c, x, y, 470, k, ti, `${(v + t * 0.07 * (i + 1)).toFixed(1)} млн просмотров`, t, i === 4 ? smooth(seg(t, 0.8, 1.4)) : 0); });
    });
    ctx.restore();
    particlesUp(ctx, t, 18, 4, [200, 200, 1500, 800], (x, y, k) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * 0.9 * smooth(seg(t, 1.2, 2)); circle(ctx, x, y, 26, '#f2c14e'); text(ctx, '$', x, y + 2, { size: 30, color: '#8a5a00', weight: 900 }); ctx.restore(); });
    vignette(ctx, 0.5);
  } },
  { id: 's10_idea', start: 39.2, scene: 3, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.08, 1.0, 960, 540);
    room(ctx, t, { winX: 1250, posterX: 120 });
    const warm = smooth(seg(t, 0.6, 1.4)); if (warm) { ctx.fillStyle = `rgba(255,180,60,${warm * 0.18})`; ctx.fillRect(0, 0, W, H); }
    const ex = t < 0.6 ? 'neutral' : t < 1.7 ? 'surprised' : 'smile';
    litHero(ctx, { x: 900, y: 520, R: 210, view: '3q', dir: 1, expr: ex, body: 'bust', arms: 'down', bob: t > 0.6 && t < 0.9 ? -20 * Math.sin((t - 0.6) / 0.3 * Math.PI) : 0, lookX: 1 }, { from: [1500, 700, 900, 'rgba(120,200,255,0.25)'] });
    if (t > 0.6) bulb(ctx, 1260, 220, easeOutBack(seg(t, 0.6, 1.0)), 1);
    ctx.restore();
    text(ctx, 'А ЧТО, ЕСЛИ…', 700, 110, { size: 90, color: C.yellow, weight: 900, stroke: '#000', strokeW: 14, alpha: smooth(seg(t, 1.0, 1.3)) });
  } },
  { id: 's11_aistudio', start: 42.6, scene: 3, draw(ctx, t, d) {
    bgDark(ctx, '#07060f');
    ctx.save(); cam(ctx, t, d, 1.0, 1.05, 960, 540);
    crtMonitor(ctx, 160, 70, 1600, 900, (c, w, h) => {
      c.fillStyle = vgrad(c, 0, h, [[0, '#140b2e'], [1, '#08060f']]); c.fillRect(0, 0, w, h);
      text(c, 'DIDAO', 60, 64, { size: 46, font: FONT_T, weight: 400, align: 'left', color: '#fff', glow: C.purple, blur: 20 }); text(c, 'AI VIDEO STUDIO', 240, 66, { size: 26, align: 'left', color: '#b9a8ff', weight: 700, spacing: 4 });
      ['16:9', '1080p', '10 сек', 'Кино'].forEach((s, i) => { fillRR(c, w - 560 + i * 135, 38, 120, 50, 25, '#251a4a'); text(c, s, w - 500 + i * 135, 64, { size: 22, color: '#d8ccff', weight: 700 }); });
      text(c, 'Опиши видео:', 60, 160, { size: 30, align: 'left', color: '#9a8fd0', weight: 600 });
      fillRR(c, 60, 190, w - 120, 230, 24, '#1a1236'); c.strokeStyle = 'rgba(160,120,255,0.6)'; c.lineWidth = 3; rr(c, 60, 190, w - 120, 230, 24); c.stroke();
      const prompt = 'Огромный город в стиле Vice City ночью, неон, пальмы, спортивные машины, кинематографичный кадр';
      const n = Math.floor(clamp((t - 0.2) * 24, 0, prompt.length)); const typed = prompt.slice(0, n);
      c.font = `500 40px ${FONT}`; const lines = wrapLines(c, typed, w - 200); lines.forEach((l, i) => text(c, l, 100, 250 + i * 56, { size: 40, align: 'left', color: '#fff', weight: 500 }));
      if (Math.floor(t * 2) % 2 === 0 && t < 4.5) { const last = lines[lines.length - 1] || ''; c.font = `500 40px ${FONT}`; fillRR(c, 104 + c.measureText(last).width, 228 + (Math.max(1, lines.length) - 1) * 56, 4, 46, 2, '#fff'); }
      const press = t > 4.5 && t < 4.7 ? 0.95 : 1; c.save(); c.translate(w / 2, 500); c.scale(press, press); const bg = c.createLinearGradient(-300, 0, 300, 0); bg.addColorStop(0, C.purple); bg.addColorStop(1, C.pink); rr(c, -300, -50, 600, 100, 50); c.fillStyle = bg; c.fill(); text(c, 'СГЕНЕРИРОВАТЬ ✦', 0, 2, { size: 40, color: '#fff', weight: 900 }); c.restore();
      if (t > 4.6) { const p = seg(t, 4.6, 6.5); fillRR(c, 60, 590, w - 120, 18, 9, '#251a4a'); fillRR(c, 60, 590, (w - 120) * p, 18, 9, C.cyan); text(c, `Генерация… ${Math.floor(p * 100)}%`, 60, 640, { size: 26, align: 'left', color: '#9adfff', weight: 600 });
        for (let i = 0; i < 4; i++) { const k = seg(t, 4.8 + i * 0.35, 5.3 + i * 0.35); const x = 60 + i * 372, y = 680; fillRR(c, x, y, 350, 197, 14, '#1a1236'); if (k > 0) { c.save(); c.globalAlpha = k; viceThumb(c, x, y, 350, 197, ['night', 'car', 'sun', 'sun2'][i], t); c.restore(); } } }
      particlesUp(c, t, 30, 11, [0, 0, w, h], (x, y, k) => { c.save(); c.globalAlpha = Math.sin(k * Math.PI) * 0.6 * smooth(seg(t, 4.6, 5)); circle(c, x, y, 3, '#cbb8ff'); c.restore(); });
      cursor(c, lerp(w - 300, w / 2 + 120, easeOut(seg(t, 3.6, 4.4))), lerp(h - 120, 520, easeOut(seg(t, 3.6, 4.4))), 1.3, t > 4.5 && t < 5 ? (t - 4.5) / 0.5 : 0);
    });
    ctx.restore(); vignette(ctx, 0.45);
  } },

  // ===================== SCENE 4 — CREATING THE FIRST VIDEO =====================
  { id: 's12_vid1', start: 49.0, scene: 4, draw(ctx, t, d) {
    viceNightStreet(ctx, W, H, t, { scroll: t * 160 });
    car(ctx, 2000 - t * 380, 1050, 1.0, C.cyan, { flip: true, lights: true });
    aiFrame(ctx, t, d, 'AI ВИДЕО #1', 'Прогулка по Вайс-Сити');
  } },
  { id: 's13_vid2', start: 53.2, scene: 4, draw(ctx, t, d) {
    ctx.save(); const sh = Math.sin(t * 40) * 2;
    sunsetSky(ctx, W, H, 720); retroSun(ctx, 1300, 600, 220); cityLayers(ctx, t, 760, t * 300, false, 50);
    ctx.fillStyle = '#1a0c26'; ctx.fillRect(0, 760, W, 320); ctx.fillStyle = '#2a1636'; ctx.fillRect(0, 850, W, 160);
    ctx.fillStyle = 'rgba(255,220,140,0.85)'; for (let i = 0; i < 14; i++) ctx.fillRect(((i * 300 - t * 2400) % 4200 + 4200) % 4200 - 300, 925, 140, 10);
    for (let i = 0; i < 8; i++) palm(ctx, ((i * 520 - t * 1500) % 4160 + 4160) % 4160 - 400, 860, 480, { sway: t * 2 + i, lean: 0.1, color: '#14081f' });
    car(ctx, 640, 960 + sh, 1.55, C.pink, { lights: true, underglow: 'rgba(25,227,255,0.6)' });
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 3; const r = rng(3); for (let i = 0; i < 30; i++) { const y = 200 + r() * 860, x = ((r() * W - t * 3000) % W + W) % W; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 200 + r() * 200, y); ctx.stroke(); } ctx.restore();
    for (let i = 0; i < 6; i++) palm(ctx, ((i * 900 - t * 3800) % 5400 + 5400) % 5400 - 600, 1150, 900, { sway: i, lean: 0.05, color: '#05020a' });
    ctx.restore();
    text(ctx, `${Math.floor(180 + t * 20)} км/ч`, 1700, 980, { size: 64, color: C.cyan, weight: 900, align: 'right', glow: C.cyan, blur: 20 });
    aiFrame(ctx, t, d, 'AI ВИДЕО #2', 'Безумная поездка');
  } },
  { id: 's14_vid3', start: 56.5, scene: 4, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.1, 960, 600);
    sunsetSky(ctx, W, H, 700); retroSun(ctx, 520, 590, 200); cityLayers(ctx, t, 720, 0, false, 60);
    ctx.fillStyle = '#2b1838'; ctx.fillRect(0, 700, W, 380); ctx.fillStyle = '#3a2448'; ctx.fillRect(0, 700, W, 40);
    ctx.fillStyle = 'rgba(255,255,255,0.25)'; for (let i = 0; i < 8; i++) ctx.fillRect(i * 260 + 40, 900, 150, 8);
    palm(ctx, 260, 760, 520, { sway: t, lean: 0.15 }); palm(ctx, 1640, 760, 560, { sway: t + 1, lean: -0.2 });
    car(ctx, 1150, 880, 1.15, C.yellow, { flip: false });
    const ex = t < 1.4 ? 'surprised' : 'smile';
    litHero(ctx, { x: 820, y: 430, R: 70, view: t < 1.4 ? '3q' : 'front', dir: t < 0.7 ? -1 : 1, expr: ex, body: 'full', arms: 'down', blink: t > 3 && t < 3.1, bob: Math.sin(t * 3) * 2 }, { from: [400, 400, 900, 'rgba(255,140,90,0.35)'] });
    ctx.restore();
    // game HUD (original)
    ctx.save(); circle(ctx, 170, 900, 120, 'rgba(10,10,20,0.75)'); ctx.beginPath(); ctx.arc(170, 900, 120, 0, Math.PI * 2); ctx.clip(); ctx.strokeStyle = 'rgba(255,255,255,0.35)'; ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(60, 870 + t * 4); ctx.lineTo(300, 920 + t * 4); ctx.moveTo(150, 760); ctx.lineTo(200, 1040); ctx.stroke(); ctx.restore();
    ctx.save(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(170, 880); ctx.lineTo(184, 912); ctx.lineTo(156, 912); ctx.fill(); ctx.restore();
    fillRR(ctx, 70, 1035, 200, 14, 7, 'rgba(0,0,0,0.6)'); fillRR(ctx, 70, 1035, 160, 14, 7, C.green);
    text(ctx, '$3', 1860, 290, { size: 72, align: 'right', color: '#6dff9a', weight: 900, stroke: '#000', strokeW: 10 });
    for (let i = 0; i < 5; i++) text(ctx, '★', 1860 - i * 52, 215, { size: 50, align: 'right', color: i < 0 ? '#fff' : 'rgba(255,255,255,0.35)', stroke: '#000', strokeW: 6 });
    if (t > 1.2) { const k = smooth(seg(t, 1.2, 1.6)) * (1 - smooth(seg(t, 4.6, 5.2))); text(ctx, 'НОВАЯ ЖИЗНЬ', 960, 215, { size: 110, font: FONT_T, weight: 400, color: C.yellow, stroke: '#000', strokeW: 14, alpha: k }); text(ctx, 'Миссия: заработать на GTA 6', 960, 300, { size: 44, color: '#fff', weight: 700, stroke: '#000', strokeW: 8, alpha: k }); }
    aiFrame(ctx, t, d, 'AI ВИДЕО #3', 'Что если бы я оказался в GTA 6?');
  } },
  { id: 's15_edit', start: 62.6, scene: 4, draw(ctx, t, d) {
    bgDark(ctx, '#05050a');
    ctx.save(); cam(ctx, t, d, 1.0, 1.04);
    crtMonitor(ctx, 160, 70, 1600, 900, (c, w, h) => {
      c.fillStyle = '#121219'; c.fillRect(0, 0, w, h);
      // preview
      fillRR(c, 300, 30, 1000, 500, 10, '#000'); c.save(); rr(c, 300, 30, 1000, 500, 10); c.clip(); c.translate(300, 30); viceSunsetScene(c, 1000, 500, t * 2); c.restore();
      const title = 'WHAT IF YOU LIVED IN GTA 6?'; const n = Math.floor(clamp(t * 22, 0, title.length));
      text(c, title.slice(0, n), 800, 110, { size: 56, color: '#fff', weight: 900, stroke: '#000', strokeW: 10 });
      // timeline
      fillRR(c, 30, 560, w - 60, 320, 14, '#1b1b25');
      const tracks = [[C.purple, [[0, 300], [310, 260], [580, 380], [970, 420]]], [C.cyan, [[100, 500], [620, 380]]], ['#3fbf6f', [[0, 1390]]]];
      tracks.forEach(([col, cl], r) => cl.forEach(([x, wd]) => { fillRR(c, 80 + x, 590 + r * 90, wd - 6, 70, 8, col); if (r === 2) { c.fillStyle = 'rgba(0,0,0,0.35)'; for (let i = 0; i < wd; i += 6) { const a = 8 + Math.abs(Math.sin(i * 0.13) * Math.sin(i * 0.031)) * 26; c.fillRect(80 + x + i, 625 + r * 90 - a / 2 + 0, 3, a); } } }));
      ['ВИДЕО', 'ТЕКСТ', 'МУЗЫКА'].forEach((s, r) => text(c, s, 40, 625 + r * 90, { size: 18, align: 'left', color: '#888', weight: 700 }));
      const ph = 80 + ((t * 300) % 1390); c.fillStyle = C.red; c.fillRect(ph, 575, 4, 290);
      // upload dialog
      if (t > 1.9) { const k = easeOutBack(seg(t, 1.9, 2.2)); c.save(); c.translate(w / 2, h / 2); c.scale(k, k); c.shadowColor = '#000'; c.shadowBlur = 60; fillRR(c, -460, -170, 920, 340, 30, '#1d1d2b'); c.shadowBlur = 0;
        const p = seg(t, 2.2, 3.7); text(c, p < 1 ? 'Загрузка на канал DIDAO…' : 'Опубликовано!', 0, -90, { size: 46, color: p < 1 ? '#fff' : C.green, weight: 900 });
        fillRR(c, -380, -20, 760, 30, 15, '#2c2c3c'); fillRR(c, -380, -20, 760 * p, 30, 15, p < 1 ? C.red : C.green); text(c, `${Math.floor(p * 100)}%`, 0, 70, { size: 40, color: '#ccc', weight: 700 });
        if (p >= 1) { circle(c, 0, 125, 34, C.green); c.strokeStyle = '#fff'; c.lineWidth = 8; c.lineCap = 'round'; c.beginPath(); c.moveTo(-14, 125); c.lineTo(-3, 137); c.lineTo(17, 112); c.stroke(); }
        c.restore(); }
      cursor(c, t < 1.9 ? lerp(1200, 700, smooth(seg(t, 0.4, 1.6))) : 900, t < 1.9 ? lerp(700, 640, smooth(seg(t, 0.4, 1.6))) : 520, 1.3, t > 1.6 && t < 2 ? (t - 1.6) / 0.4 : 0);
    });
    ctx.restore(); vignette(ctx, 0.45);
  } },

  // ===================== SCENE 5 — FIRST RESULTS =====================
  { id: 's16_wait', start: 67.0, scene: 5, draw(ctx, t, d) {
    const hours = seg(t, 0.4, 4.4);
    ctx.save(); cam(ctx, t, d, 1.0, 1.06, 900, 560);
    room(ctx, t, { winX: 1280, dawn: hours * 0.85, wallClock: (c) => { const cx = 700, cy = 200; circle(c, cx, cy, 82, '#e8e2d0'); circle(c, cx, cy, 72, '#fbf7ea'); for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; c.fillStyle = '#333'; c.fillRect(cx + Math.cos(a) * 60 - 3, cy + Math.sin(a) * 60 - 3, 6, 6); } const hrs = 1 + hours * 6; const ha = (hrs / 12) * Math.PI * 2 - Math.PI / 2, ma = (hrs % 1) * Math.PI * 2 - Math.PI / 2; c.strokeStyle = '#222'; c.lineCap = 'round'; c.lineWidth = 8; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(ha) * 38, cy + Math.sin(ha) * 38); c.stroke(); c.lineWidth = 5; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(ma) * 58, cy + Math.sin(ma) * 58); c.stroke(); circle(c, cx, cy, 7, C.red); } });
    const jolt = t > 4.6 ? Math.exp(-(t - 4.6) * 5) * Math.sin((t - 4.6) * 30) * 10 : 0;
    litHero(ctx, { x: 640, y: 560 - (t > 4.6 ? 30 * Math.exp(-(t - 4.6) * 4) : 0), R: 110, view: 'side', dir: 1, expr: t < 4.6 ? 'bored' : 'surprised', body: 'bust', arms: t < 4.6 ? 'chin' : 'desk', bob: jolt, tilt: t < 4.6 ? 0.08 + Math.sin(t * 1.4) * 0.03 : 0 }, { from: [1100, 600, 700, 'rgba(120,190,255,0.3)'] });
    desk(ctx);
    const views = t < 4.6 ? Math.floor(3 + hours * 9) : 1000;
    crtMonitor(ctx, 960, 470, 420, 290, (c, w, h) => { c.fillStyle = '#101018'; c.fillRect(0, 0, w, h); viceThumb(c, 20, 20, 170, 96, 'sun', 0); text(c, 'WHAT IF YOU LIVED…', 205, 50, { size: 22, align: 'left', color: '#fff', weight: 800 }); text(c, 'Просмотры:', 30, 170, { size: 30, align: 'left', color: '#aab', weight: 600 }); text(c, fmt(views), 30, 235, { size: 70, align: 'left', color: t < 4.6 ? '#fff' : C.green, weight: 900 }); });
    glow(ctx, 1170, 610, 500, 'rgba(120,190,255,0.22)');
    keyboard(ctx, 980, 790, 360);
    ctx.restore();
    text(ctx, t < 4.6 ? `+${Math.floor(hours * 6)} ч` : '', 1700, 120, { size: 70, color: '#fff', weight: 900, stroke: '#000', strokeW: 10, align: 'right', alpha: smooth(seg(t, 0.4, 0.8)) });
    if (t > 4.6) { const k = easeOutBack(seg(t, 4.6, 4.9)); ctx.save(); ctx.translate(1240, 330); ctx.scale(k, k); notif(ctx, -300, -48, 600, '1 000 просмотров!', 'Твоё видео набирает обороты', C.red, 1, 'up'); ctx.restore(); }
    vignette(ctx, 0.55);
  } },
  { id: 's17_views', start: 72.6, scene: 5, draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#0c0a1c'], [1, '#170b26']]); ctx.fillRect(0, 0, W, H);
    // views keyframes synced to VO: "10 000" at t=1.3, "50 000" at t=3.3, then rocket
    const kf = [[0, 1000], [1.0, 1200], [1.5, 10000], [3.0, 12000], [3.5, 50000], [5.0, 61000], [d, 240000]];
    let v = 1000; for (let i = 0; i < kf.length - 1; i++) { const [t0, v0] = kf[i], [t1, v1] = kf[i + 1]; if (t >= t0 && t <= t1) v = lerp(v0, v1, i === kf.length - 2 ? easeIn(seg(t, t0, t1)) : easeOut(seg(t, t0, t1))); if (t > t1) v = v1; }
    ctx.save(); cam(ctx, t, d, 1.0, 1.05);
    fillRR(ctx, 80, 80, 1100, 920, 36, 'rgba(255,255,255,0.04)');
    viceThumb(ctx, 130, 130, 440, 248, 'sun', t); text(ctx, 'WHAT IF YOU LIVED', 600, 190, { size: 46, align: 'left', color: '#fff', weight: 900 }); text(ctx, 'IN GTA 6?', 600, 246, { size: 46, align: 'left', color: C.yellow, weight: 900 }); text(ctx, 'канал DIDAO · 1 видео', 600, 310, { size: 28, align: 'left', color: '#99a', weight: 500 });
    text(ctx, 'ПРОСМОТРЫ', 130, 460, { size: 34, align: 'left', color: '#99a', weight: 700, spacing: 4 });
    const pop = 1 + 0.08 * (Math.exp(-Math.max(0, t - 1.5) * 8) * (t > 1.5 ? 1 : 0) + Math.exp(-Math.max(0, t - 3.5) * 8) * (t > 3.5 ? 1 : 0));
    ctx.save(); ctx.translate(130, 590); ctx.scale(pop, pop); text(ctx, fmt(v), 0, 0, { size: 190, align: 'left', color: '#fff', weight: 900, glow: C.green, blur: 30 }); ctx.restore();
    // graph
    ctx.save(); ctx.translate(130, 950); ctx.strokeStyle = C.green; ctx.lineWidth = 8; ctx.lineJoin = 'round'; ctx.beginPath(); const N = 60; for (let i = 0; i <= N; i++) { const k = i / N; const tt = k * t; let vv = 1000; for (let j = 0; j < kf.length - 1; j++) { const [t0, v0] = kf[j], [t1, v1] = kf[j + 1]; if (tt >= t0 && tt <= t1) vv = lerp(v0, v1, seg(tt, t0, t1)); if (tt > t1) vv = v1; } const x = k * 1000 * Math.min(1, t / d * 1.2), y = -Math.pow(vv / 240000, 0.5) * 230; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); ctx.lineTo(1000 * Math.min(1, t / d * 1.2), 0); ctx.lineTo(0, 0); ctx.fillStyle = 'rgba(57,255,138,0.12)'; ctx.fill(); ctx.restore();
    // subs
    const subs = Math.floor(Math.pow(v / 240000, 0.9) * 4800);
    fillRR(ctx, 1230, 80, 610, 200, 36, 'rgba(255,46,136,0.95)'); text(ctx, 'ПОДПИСЧИКИ', 1270, 140, { size: 30, align: 'left', color: '#ffe0ee', weight: 800, spacing: 3 }); text(ctx, fmt(subs), 1270, 220, { size: 90, align: 'left', color: '#fff', weight: 900 });
    const comments = [['Лучшее видео про GTA 6', 'max_v'], ['Сделай вторую часть!!!', 'liza.play'], ['Как ты это сделал?', 'kirill_07'], ['Это лучше трейлера', 'neon_rider'], ['Жду новое видео', 'arthur'], ['ОГОНЬ', 'dimon']];
    comments.forEach(([s, u], i) => { const t0 = 0.7 + i * 0.9; if (t < t0) return; const k = easeOutBack(seg(t, t0, t0 + 0.35)); const y = 330 + i * 112; ctx.save(); ctx.translate(1230 + (1 - k) * 300, y); ctx.globalAlpha = clamp(k); fillRR(ctx, 0, 0, 610, 96, 22, 'rgba(255,255,255,0.08)'); circle(ctx, 48, 48, 28, [C.cyan, C.orange, C.purple, C.green, C.yellow, C.red][i]); text(ctx, '@' + u, 92, 32, { size: 22, align: 'left', color: '#9aa', weight: 600 }); text(ctx, s, 92, 66, { size: 30, align: 'left', color: '#fff', weight: 700 }); ctx.restore(); });
    ctx.restore();
    particlesUp(ctx, t, 26, 21, [100, 200, 1100, 800], (x, y, k, i) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * 0.8 * smooth(seg(t, 1.5, 2)); text(ctx, i % 2 ? '+1' : '♥', x, y, { size: 34, color: i % 2 ? C.green : C.pink, weight: 900 }); ctx.restore(); });
  } },
  { id: 's18_chance', start: 80.0, scene: 5, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.12, 960, 460);
    room(ctx, t, { winX: 1250, posterX: 120 });
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, W, H);
    // reflected graph behind
    ctx.save(); ctx.globalAlpha = 0.35; ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = C.green; ctx.lineWidth = 10; ctx.beginPath(); for (let i = 0; i <= 40; i++) { const k = i / 40; ctx.lineTo(200 + k * 1500, 900 - Math.pow(k, 2.2) * 700 - Math.sin(k * 20) * 20); } ctx.stroke(); ctx.restore();
    litHero(ctx, { x: 960, y: 470, R: 230, view: 'front', expr: t < 1.3 ? 'determined' : 'smile', body: 'bust', arms: 'down', lookX: 0, blink: t > 2.8 && t < 2.92 }, { tint: '#21ff9a', tintA: 0.03, from: [960, 1200, 900, 'rgba(90,255,170,0.16)'] });
    ctx.restore();
    particlesUp(ctx, t, 16, 31, [100, 100, 1700, 900], (x, y, k, i) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * 0.7; text(ctx, '+1 подписчик', x, y, { size: 26, color: C.green, weight: 700 }); ctx.restore(); });
    vignette(ctx, 0.6);
  } },

  // ===================== SCENE 6 — GTA 6 IS OUT =====================
  { id: 's19_midnight', start: 84.4, scene: 6, draw(ctx, t, d) {
    const T0 = 2.3; // 00:00:00
    ctx.save(); cam(ctx, t, d, 1.0, 1.06, 960, 700);
    nightSky(ctx, W, H, 820, 12); cityLayers(ctx, t, 860, 0, true, 70);
    ctx.fillStyle = '#05030b'; ctx.fillRect(0, 860, W, 220);
    fireworks(ctx, t, 1, [[T0, 400, 300, C.pink], [T0 + 0.25, 1500, 260, C.cyan], [T0 + 0.6, 960, 200, C.yellow], [T0 + 0.9, 700, 380, C.orange], [T0 + 1.2, 1300, 360, C.purple], [T0 + 1.5, 300, 220, C.green]]);
    ctx.restore();
    const rem = Math.max(0, Math.ceil(T0 - t)); const clock = t < T0 ? `23:59:${String(60 - rem).padStart(2, '0')}` : '00:00:00';
    neonText(ctx, clock, W / 2, t < T0 ? 480 : 200, t < T0 ? 220 : 90, t < T0 ? C.cyan : C.yellow, { font: '"Rubik", sans-serif' });
    const flash = t > T0 ? Math.exp(-(t - T0) * 5) : 0; if (flash > 0.01) { ctx.fillStyle = `rgba(255,255,255,${flash * 0.9})`; ctx.fillRect(0, 0, W, H); }
    if (t > T0) { const k = easeOutBack(seg(t, T0 + 0.05, T0 + 0.5)); ctx.save(); ctx.translate(W / 2, 520); ctx.scale(k, k); neonText(ctx, 'GTA VI', 0, -70, 200, C.pink); neonText(ctx, 'IS NOW AVAILABLE', 0, 110, 110, C.cyan, { spacing: 4 }); ctx.restore(); }
  } },
  { id: 's20_world', start: 89.0, scene: 6, draw(ctx, t, d) {
    ctx.fillStyle = '#07060e'; ctx.fillRect(0, 0, W, H);
    ctx.save(); cam(ctx, t, d, 1.15, 1.0, 960, 540);
    fillRR(ctx, 140, 60, 1640, 1100, 0, '#1b1530');
    const cols = 7, rows = 5; const r = rng(42);
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const x = 200 + i * 225, y = 110 + j * 190; const on = t > (i + j) * 0.12; const c = [C.cyan, C.pink, '#7cff9a', C.yellow, '#a98bff'][(i * 3 + j) % 5];
      fillRR(ctx, x, y, 180, 150, 8, on ? '#120c22' : '#0d0a18');
      if (on) { const fl = 0.7 + 0.3 * Math.sin(t * (6 + r() * 6) + i * j); ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = rgrad(ctx, x + 90, y + 60, 0, 140, [[0, c], [1, 'rgba(0,0,0,0)']]); ctx.globalAlpha = 0.45 * fl; ctx.fillRect(x, y, 180, 150); ctx.restore(); fillRR(ctx, x + 50, y + 30, 80, 48, 4, c); ctx.fillStyle = '#05040a'; ctx.beginPath(); ctx.arc(x + 70 + ((i + j) % 2) * 40, y + 128, 34, Math.PI, 0); ctx.fill(); circle(ctx, x + 70 + ((i + j) % 2) * 40, y + 100, 20, '#05040a'); }
      ctx.strokeStyle = '#2a2244'; ctx.lineWidth = 8; ctx.strokeRect(x, y, 180, 150);
    }
    ctx.restore();
    text(ctx, 'ВЕСЬ МИР ИГРАЕТ', 960, 70, { size: 80, color: '#fff', weight: 900, stroke: '#000', strokeW: 12, alpha: smooth(seg(t, 0.5, 0.9)) });
    vignette(ctx, 0.55);
  } },
  { id: 's21_notifs', start: 91.4, scene: 6, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.08, 960, 450);
    room(ctx, t, { winX: 1350 });
    // fireworks seen through window
    ctx.save(); rr(ctx, 1350, 150, 520, 380, 8); ctx.clip(); fireworks(ctx, t, 2, [[0, 1500, 260, C.pink], [0.7, 1700, 300, C.cyan], [1.5, 1560, 220, C.yellow], [2.2, 1760, 260, C.green]]); ctx.restore();
    desk(ctx);
    crtMonitor(ctx, 560, 230, 760, 520, (c, w, h) => { c.fillStyle = '#101018'; c.fillRect(0, 0, w, h); text(c, 'Уведомления', 30, 40, { size: 32, align: 'left', color: '#fff', weight: 800 });
      const list = [['+128 подписчиков', 'канал DIDAO растёт', C.pink, 'plus'], ['Новый комментарий', '«жду вторую серию!»', C.cyan, 'msg'], ['Видео в тренде #12', 'WHAT IF YOU LIVED IN GTA 6?', C.orange, 'up'], ['+1 000 просмотров', 'за последние 5 минут', C.green, 'up']];
      list.forEach(([a, b, col, ic], i) => { const t0 = 0.2 + i * 0.6; if (t < t0) return; const k = easeOut(seg(t, t0, t0 + 0.3)); notif(c, 20 + (1 - k) * 300, 80 + i * 108, w - 40, a, b, col, k, ic); }); });
    glow(ctx, 940, 490, 700, 'rgba(255,90,160,0.22)');
    litHero(ctx, { x: 820, y: 780, R: 150, view: 'back', body: 'bust', arms: 'down', tilt: Math.sin(t * 0.8) * 0.03 }, { from: [940, 500, 700, 'rgba(255,140,200,0.35)'] });
    ctx.restore(); vignette(ctx, 0.6);
  } },
  { id: 's22_channel', start: 94.8, scene: 6, draw(ctx, t, d) {
    const MSG = 4.3;
    ctx.save(); cam(ctx, t, d, 1.0, 1.05, 700, 520);
    room(ctx, t, { winX: 1300, posterX: 140 });
    ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fillRect(0, 0, W, H);
    litHero(ctx, { x: 560, y: 470, R: 220, view: '3q', dir: 1, expr: t < MSG + 0.1 ? 'smile' : 'surprised', body: 'bust', arms: 'down', lookX: 1, blink: t > 2.2 && t < 2.32 }, { from: [1300, 600, 1000, 'rgba(255,90,160,0.3)'] });
    ctx.restore();
    // channel panel (floating UI)
    const pa = easeOut(seg(t, 0.1, 0.6)); ctx.save(); ctx.globalAlpha = pa; ctx.translate((1 - pa) * 120, 0);
    fillRR(ctx, 1040, 140, 800, 680, 36, 'rgba(18,16,30,0.94)');
    circle(ctx, 1130, 230, 52, C.pink); text(ctx, 'D', 1130, 232, { size: 56, font: FONT_T, weight: 400, color: '#fff' });
    text(ctx, 'DIDAO', 1205, 210, { size: 46, align: 'left', color: '#fff', weight: 900 }); text(ctx, `${fmt(3418 + t * 210)} подписчиков`, 1205, 258, { size: 28, align: 'left', color: '#aab', weight: 500 });
    text(ctx, 'WHAT IF YOU LIVED IN GTA 6?', 1090, 340, { size: 30, align: 'left', color: '#fff', weight: 800 }); text(ctx, `${fmt(127004 + t * 9000)} просмотров`, 1090, 384, { size: 28, align: 'left', color: C.green, weight: 700 });
    // earnings vs goal
    const earned = 41.8 + t * 0.9;
    text(ctx, 'ЗАРАБОТАНО', 1090, 470, { size: 26, align: 'left', color: '#99a', weight: 800, spacing: 3 }); text(ctx, `$${earned.toFixed(2)}`, 1090, 540, { size: 84, align: 'left', color: C.yellow, weight: 900 });
    text(ctx, 'ЦЕЛЬ: GTA 6 — $69.99', 1090, 630, { size: 30, align: 'left', color: '#fff', weight: 800 });
    fillRR(ctx, 1090, 670, 700, 38, 19, '#2c2c3c'); fillRR(ctx, 1090, 670, 700 * Math.min(1, earned / 69.99), 38, 19, C.yellow); text(ctx, `${Math.floor(earned / 69.99 * 100)}%`, 1790, 750, { size: 32, align: 'right', color: C.yellow, weight: 900 });
    ctx.restore();
    if (t > MSG) { const k = easeOutBack(seg(t, MSG, MSG + 0.35)); const gl = t < MSG + 0.5 ? (Math.random() - 0.5) * 0 + Math.sin(t * 90) * 10 : 0; ctx.save(); ctx.fillStyle = `rgba(0,0,0,${0.5 * smooth(seg(t, MSG, MSG + 0.3))})`; ctx.fillRect(0, 0, W, H); ctx.translate(W / 2 + gl, H / 2 - 40); ctx.scale(k, k); ctx.shadowColor = C.pink; ctx.shadowBlur = 60; fillRR(ctx, -760, -150, 1520, 300, 30, '#140a1e'); ctx.shadowBlur = 0; ctx.strokeStyle = C.pink; ctx.lineWidth = 5; rr(ctx, -760, -150, 1520, 300, 30); ctx.stroke(); text(ctx, 'НОВОЕ СООБЩЕНИЕ · неизвестный отправитель', 0, -90, { size: 28, color: '#ff8ac0', weight: 700 }); text(ctx, 'YOUR NEXT VIDEO', 0, -10, { size: 84, color: '#fff', weight: 900 }); text(ctx, 'COULD CHANGE EVERYTHING.', 0, 80, { size: 84, color: C.pink, weight: 900 }); ctx.restore(); }
  } },
  { id: 's23_dark', start: 101.4, scene: 6, draw(ctx, t, d) {
    bgDark(ctx, '#030308');
    ctx.save(); cam(ctx, t, d, 1.0, 1.18, 960, 470);
    const flick = 0.85 + 0.15 * Math.sin(t * 23) * Math.sin(t * 7);
    crtMonitor(ctx, 560, 210, 800, 540, (c, w, h) => { c.fillStyle = '#0a0410'; c.fillRect(0, 0, w, h); text(c, 'YOUR NEXT VIDEO', w / 2, h / 2 - 50, { size: 66, color: '#fff', weight: 900, glow: C.pink, blur: 20, alpha: flick }); text(c, 'COULD CHANGE', w / 2, h / 2 + 30, { size: 66, color: C.pink, weight: 900, glow: C.pink, blur: 20, alpha: flick }); text(c, 'EVERYTHING.', w / 2, h / 2 + 110, { size: 66, color: C.pink, weight: 900, glow: C.pink, blur: 20, alpha: flick }); if (Math.floor(t * 2) % 2) c.fillRect(w / 2 + 230, h / 2 + 85, 30, 50); });
    glow(ctx, 960, 480, 900, 'rgba(255,46,136,0.25)', flick);
    litHero(ctx, { x: 960, y: 820, R: 170, view: 'back', body: 'bust', arms: 'down' }, { shade: 0.55, from: [960, 480, 700, 'rgba(255,60,150,0.35)'] });
    ctx.restore();
    vignette(ctx, 0.8);
    const fd = smooth(seg(t, d - 1.4, d - 0.2)); if (fd > 0) { ctx.fillStyle = `rgba(0,0,0,${fd})`; ctx.fillRect(0, 0, W, H); }
  } },
  { id: 's24_question', start: 107.6, scene: 6, draw(ctx, t, d) {
    bgDark(ctx, '#020205');
    ctx.save(); ctx.globalAlpha = 0.18 * smooth(seg(t, 0, 1.5)); const sk = skylineCanvas('qsky', 2600, 400, { seed: 90, minW: 50, maxW: 160, minH: 80, maxH: 360, color: '#140c26', windows: true, lit: 0.3, win: 4 }); ctx.drawImage(sk, -300 - t * 20, H - 400); ctx.restore();
    const words = ['Сможет', 'ли', 'он', 'заработать', 'достаточно', 'денег,', 'чтобы', 'наконец', 'купить', 'GTA 6?'];
    const lines = [words.slice(0, 5), words.slice(5)];
    ctx.font = `900 76px ${FONT}`;
    let wi = 0; lines.forEach((ln, li) => { const full = ln.join(' '); let x = W / 2 - ctx.measureText(full).width / 2; ln.forEach(w => { const t0 = 0.3 + wi * 0.22; const a = smooth(seg(t, t0, t0 + 0.3)); const isG = w.startsWith('GTA'); text(ctx, w, x, 430 + li * 110 - (1 - a) * 20, { size: 76, align: 'left', color: isG ? C.pink : '#fff', weight: 900, alpha: a, glow: isG ? C.pink : undefined, blur: 10 }); x += ctx.measureText(w + ' ').width; wi++; }); });
    text(ctx, 'Пиши свой ответ в комментариях', W / 2, 720, { size: 40, color: '#9aa0c0', weight: 500, alpha: smooth(seg(t, 3.4, 4.0)) });
  } },
  { id: 's25_endcard', start: 114.0, scene: 6, draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.05, 1.0);
    nightSky(ctx, W, H, 900, 21); cityLayers(ctx, t, 940, t * 20, true, 80); ctx.fillStyle = '#05030b'; ctx.fillRect(0, 930, W, 150);
    palm(ctx, 1840, 1080, 600, { sway: t, lean: -0.2, color: '#05030b' }); palm(ctx, 80, 1080, 520, { sway: t + 1, lean: 0.2, color: '#05030b' });
    ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, W, H);
    litHero(ctx, { x: 1450, y: 400, R: 80, view: 'front', expr: 'smug', body: 'full', arms: 'down', blink: t > 2.5 && t < 2.62 }, { from: [1000, 300, 900, 'rgba(255,60,150,0.3)'] });
    ctx.restore();
    const k = easeOutBack(seg(t, 0.2, 0.8)); ctx.save(); ctx.translate(700, 360); ctx.scale(k, k); neonText(ctx, 'DIDAO', 0, 0, 200, C.pink, { spacing: 20 }); ctx.restore();
    text(ctx, 'ЭПИЗОД 1 · ЗА ДЕНЬ ДО GTA 6', 700, 520, { size: 40, color: '#fff', weight: 800, spacing: 4, alpha: smooth(seg(t, 0.8, 1.2)) });
    text(ctx, 'ПРОДОЛЖЕНИЕ СЛЕДУЕТ…', 700, 640, { size: 64, color: C.yellow, weight: 900, stroke: '#000', strokeW: 10, alpha: smooth(seg(t, 1.4, 1.9)) });
    text(ctx, 'ЭПИЗОД 2 — СКОРО', 700, 740, { size: 44, color: C.cyan, weight: 800, glow: C.cyan, blur: 6, alpha: smooth(seg(t, 2.0, 2.5)) });
    const fo = smooth(seg(t, d - 1.2, d)); if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
  } },
];
// AI-generated-clip frame overlay used in scene 4
function aiFrame(ctx, t, d, tag, title) {
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 6; const m = 40, L = 70;
  [[m, m, 1, 1], [W - m, m, -1, 1], [m, H - m, 1, -1], [W - m, H - m, -1, -1]].forEach(([x, y, sx, sy]) => { ctx.beginPath(); ctx.moveTo(x, y + sy * L); ctx.lineTo(x, y); ctx.lineTo(x + sx * L, y); ctx.stroke(); });
  fillRR(ctx, 80, 80, 300, 64, 32, 'rgba(138,60,255,0.92)'); text(ctx, '✦ ' + tag, 230, 113, { size: 30, color: '#fff', weight: 900 });
  text(ctx, title, 400, 113, { size: 38, align: 'left', color: '#fff', weight: 800, stroke: '#000', strokeW: 8 });
  if (Math.floor(t * 2) % 2 === 0) circle(ctx, W - 130, 112, 14, C.red); text(ctx, 'REC', W - 105, 113, { size: 30, align: 'left', color: '#fff', weight: 800 });
  ctx.restore();
}
// ---------- COVER (YouTube thumbnail) ----------
function drawCover(ctx) {
  const t = 1.3;
  nightSky(ctx, W, H, 760, 33); cityLayers(ctx, t, 820, 200, true, 20);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; const r = rng(4); for (let i = 0; i < 26; i++) glow(ctx, r() * W, 300 + r() * 500, 40 + r() * 120, [C.pink, C.cyan, C.purple, C.orange][i % 4], 0.35); ctx.restore();
  neonText(ctx, 'MOTEL', 1640, 470, 70, C.cyan); neonText(ctx, 'VICE', 250, 430, 90, C.pink);
  ctx.fillStyle = '#0a0612'; ctx.fillRect(0, 820, W, 260);
  car(ctx, 1180, 900, 1.3, C.pink, { lights: true, underglow: 'rgba(25,227,255,0.7)' });
  palm(ctx, 1860, 1100, 820, { sway: 1, lean: -0.22, color: '#05020a' }); palm(ctx, 1080, 900, 520, { sway: 2, lean: 0.1, color: '#05020a' });
  // desk + monitor showing the vice world
  fillRR(ctx, -40, 900, 1120, 220, 10, '#3a281e');
  ctx.save(); ctx.translate(560, 470); ctx.rotate(-0.03); crtMonitor(ctx, 0, 0, 470, 330, (c, w, h) => viceSunsetScene(c, w, h, 2)); ctx.restore();
  glow(ctx, 790, 640, 600, 'rgba(255,140,90,0.45)');
  litHero(ctx, { x: 300, y: 560, R: 205, view: '3q', dir: 1, expr: 'surprised', body: 'bust', arms: 'down', lookX: 1 }, { from: [800, 620, 900, 'rgba(255,150,100,0.45)'] });
  vignette(ctx, 0.45);
  // headline
  ctx.save(); ctx.translate(1340, 210); ctx.rotate(-0.04);
  text(ctx, '1 DAY BEFORE', 0, 0, { size: 132, font: FONT_T, weight: 400, color: '#fff', stroke: '#000', strokeW: 26 });
  text(ctx, 'GTA 6', 40, 175, { size: 230, font: FONT_T, weight: 400, color: C.yellow, stroke: '#000', strokeW: 34 });
  ctx.restore();
  ctx.save(); ctx.translate(1530, 560); ctx.rotate(-0.06); fillRR(ctx, -170, -44, 340, 88, 14, C.red); text(ctx, 'НЕТ ДЕНЕГ', 0, 3, { size: 52, color: '#fff', weight: 900 }); ctx.restore();
  neonText(ctx, 'DIDAO', 150, 80, 64, C.pink, { align: 'left', spacing: 8 });
}

// timing helpers
for (let i = 0; i < SHOTS.length; i++) { const nx = i + 1 < SHOTS.length ? SHOTS[i + 1].start : TOTAL; SHOTS[i].dur = +(nx - SHOTS[i].start + (i + 1 < SHOTS.length ? XF : 0)).toFixed(3); }
function renderShot(id, t) { const s = SHOTS.find(s => s.id === id); const ctx = document.getElementById('c').getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.clearRect(0, 0, W, H); ctx.save(); s.draw(ctx, t, s.dur); ctx.restore(); }
function renderCover() { const ctx = document.getElementById('c').getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); ctx.save(); drawCover(ctx); ctx.restore(); }
