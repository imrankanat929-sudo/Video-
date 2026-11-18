// Episode 2 — "GTA 6 IS FINALLY HERE!" / «GTA 6 УЖЕ ВЫШЛА!» — vertical 1080×1920, RU + EN.
// Same hero (lib.js hero()), same art library as episode 1. Shot starts come from timing.js (VO-synced per language).
const LANG = (new URLSearchParams(location.search).get('lang')) || 'en';
const TM = TIMING[LANG]; const XF = 0.25;
const L = {
  en: { ch: 'My Channel', subs: 'subscribers', views: 'views', viewsCap: 'VIEWS', live: 'LIVE', watching: 'watching', news: 'BREAKING NEWS', waiting: 'WAITING', online: 'ONLINE',
    usa: 'USA', europe: 'EUROPE', asia: 'ASIA', aus: 'AUSTRALIA', loading: 'LOADING GTA 6', explode: 'THE INTERNET IS EXPLODING',
    chat: ['W CITY', 'THE CARS!!!', 'graphics omg', 'GO TO THE BEACH', 'first!!', 'LET HIM COOK', 'is that a secret?', '10/10', 'drive faster', 'insane'],
    viewers: 'viewers', tabs: ['Stream #1', 'Stream #2', 'Stream #3'], hours: '+5 HRS', newVids: 'new GTA 6 videos today', vidTitles: ['GTA 6 FIRST HOUR', 'I FOUND A SECRET', 'GTA 6 MAX SPEED', 'BEACH AT NIGHT', 'GTA 6 FAILS', 'SECRET ENDING?'],
    watchSub: '', createSub: '', mystery: 'AI VIDEO STUDIO', describe: 'Describe your video:', prompt: 'GTA 6 style Vice City, 10 crazy moments, sports car jump, neon night, cinematic', generate: 'GENERATE ✦', generating: 'Generating…',
    v1: 'AI VIDEO #1', v2: 'AI VIDEO #2', v3: 'AI VIDEO #3', t2: 'A giant dinosaur in Vice City?', t3: 'What if the whole city vanished?',
    uploading: 'Uploading…', published: 'Published!', almost: 'views', them: 'THEM: watching streams', me: 'ME: building my channel', earned: 'EARNED', goal: 'GOAL: GTA 6', almostThere: 'almost there!',
    problem: 'NEW PROBLEM', watchingYou: 'is watching your video', newMsg: 'NEW MESSAGE', from: 'from', typing: 'typing…', open: 'TAP TO OPEN',
    q: ['Can he become', 'bigger than the', 'streamers he was', 'watching yesterday?'], tbc: 'TO BE CONTINUED…', ep3: 'EPISODE 3 — COMING SOON', comments: ['how is this AI??', 'part 2 NOW', 'better than streams', 'subscribed!', 'the dinosaur lmao'],
    cover: ['GTA 6', 'IS HERE!'] },
  ru: { ch: 'Мой канал', subs: 'подписчиков', views: 'просмотров', viewsCap: 'ПРОСМОТРЫ', live: 'LIVE', watching: 'смотрят', news: 'СРОЧНЫЕ НОВОСТИ', waiting: 'ЖДУТ', online: 'ОНЛАЙН',
    usa: 'США', europe: 'ЕВРОПА', asia: 'АЗИЯ', aus: 'АВСТРАЛИЯ', loading: 'ЗАГРУЗКА GTA 6', explode: 'ИНТЕРНЕТ ВЗРЫВАЕТСЯ',
    chat: ['ГОРОД ТОП', 'МАШИНЫ!!!', 'графика жесть', 'НА ПЛЯЖ', 'первый!!', 'ДАВАЙ ЕЩЁ', 'это секрет?', '10/10', 'газуй', 'безумие'],
    viewers: 'зрителей', tabs: ['Стрим #1', 'Стрим #2', 'Стрим #3'], hours: '+5 Ч', newVids: 'новых видео о GTA 6 за день', vidTitles: ['ПЕРВЫЙ ЧАС В GTA 6', 'НАШЁЛ СЕКРЕТ', 'МАКС. СКОРОСТЬ', 'ПЛЯЖ НОЧЬЮ', 'ФЕЙЛЫ GTA 6', 'СЕКРЕТНАЯ КОНЦОВКА?'],
    watchSub: 'смотреть, как играют другие', createSub: 'создавать свои видео', mystery: 'AI VIDEO STUDIO', describe: 'Опиши видео:', prompt: 'Vice City в стиле GTA 6, 10 безумных моментов, прыжок спорткара, неон, ночь, кино', generate: 'СОЗДАТЬ ✦', generating: 'Генерация…',
    v1: 'AI ВИДЕО #1', v2: 'AI ВИДЕО #2', v3: 'AI ВИДЕО #3', t2: 'Огромный динозавр в Vice City?', t3: 'Что если весь город исчезнет?',
    uploading: 'Загрузка…', published: 'Опубликовано!', almost: 'просмотров', them: 'ОНИ: смотрят стримы', me: 'Я: строю свой канал', earned: 'ЗАРАБОТАНО', goal: 'ЦЕЛЬ: GTA 6', almostThere: 'почти!',
    problem: 'НОВАЯ ПРОБЛЕМА', watchingYou: 'смотрит твоё видео', newMsg: 'НОВОЕ СООБЩЕНИЕ', from: 'от', typing: 'печатает…', open: 'НАЖМИ, ЧТОБЫ ОТКРЫТЬ',
    q: ['Сможет ли он стать', 'популярнее блогеров,', 'за которыми ещё', 'вчера наблюдал?'], tbc: 'ПРОДОЛЖЕНИЕ СЛЕДУЕТ…', ep3: 'ЭПИЗОД 3 — СКОРО', comments: ['как это сделано AI??', 'вторую часть!', 'лучше стримов', 'подписался!', 'динозавр ахах'],
    cover: ['GTA 6', 'ВЫШЛА!'] },
}[LANG];
const num = n => LANG === 'ru' ? fmt(n) : fmtEn(n);
const kfmt = n => n >= 1e6 ? (n / 1e6).toFixed(1) + (LANG === 'ru' ? ' млн' : 'M') : n >= 1e3 ? Math.round(n / 1e3) + (LANG === 'ru' ? ' тыс.' : 'K') : String(Math.round(n));
const STREAMER = 'NeonKing';

function bgDark(ctx, c = '#07060d') { ctx.fillStyle = c; ctx.fillRect(0, 0, W, H); }
function cam(ctx, t, d, z0, z1, cx = W / 2, cy = H / 2) { const k = smooth(t / d); const z = lerp(z0, z1, k); ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy); }
function shake(ctx, t, amp, t0 = 0, decay = 6) { if (t < t0) return; const k = Math.exp(-(t - t0) * decay) * amp; ctx.translate(Math.sin(t * 71) * k, Math.cos(t * 53) * k); }
function sceneFill(ctx, fn, t, focusX = 0.5, o) { const sh = H, sw = sh * 16 / 9; ctx.save(); ctx.translate(-(sw - W) * focusX, 0); fn(ctx, sw, sh, t, o); ctx.restore(); }
function lines(ctx, arr, x, y, gap, o) { arr.forEach((s, i) => text(ctx, s, x, y + i * gap, o)); }
function pop(t, t0, d = 0.3) { return easeOutBack(seg(t, t0, t0 + d)); }
function liveBadge(ctx, x, y, s = 1) { fillRR(ctx, x, y, 96 * s, 40 * s, 8 * s, C.red); circle(ctx, x + 20 * s, y + 20 * s, 7 * s, '#fff'); text(ctx, L.live, x + 58 * s, y + 21 * s, { size: 24 * s, color: '#fff', weight: 900 }); }

// modern blogger room (episode 2 upgrade: LED strip) — the "mysterious" CRT from episode 1 stays
function roomV(ctx, t, o = {}) {
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#191a2e'], [1, '#0e0f1e']]); ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = vgrad(ctx, 0, 260, [[0, 'rgba(160,60,255,0.45)'], [1, 'rgba(160,60,255,0)']]); ctx.fillRect(0, 0, W, 260); ctx.restore();
  fillRR(ctx, 0, 0, W, 12, 0, '#c77dff');
  const wx = 600, wy = 300, ww = 400, wh = 520;
  ctx.save(); rr(ctx, wx, wy, ww, wh, 8); ctx.clip();
  ctx.fillStyle = vgrad(ctx, wy, wy + wh, o.day ? [[0, '#6a8cff'], [1, '#ffc38a']] : [[0, '#060714'], [1, '#2a1546']]); ctx.fillRect(wx, wy, ww, wh);
  if (o.dusk !== undefined) { ctx.globalAlpha = o.dusk; ctx.fillStyle = vgrad(ctx, wy, wy + wh, [[0, '#060714'], [1, '#2a1546']]); ctx.fillRect(wx, wy, ww, wh); ctx.globalAlpha = 1; }
  ctx.drawImage(skylineCanvas('roomskyV', 700, 380, { seed: 78, minW: 30, maxW: 80, minH: 80, maxH: 330, color: '#0c0a1e', windows: true, lit: 0.5, win: 3 }), wx - 120, wy + wh - 380);
  ctx.restore();
  ctx.strokeStyle = '#2c2f45'; ctx.lineWidth = 16; ctx.strokeRect(wx, wy, ww, wh); ctx.lineWidth = 8; ctx.beginPath(); ctx.moveTo(wx + ww / 2, wy); ctx.lineTo(wx + ww / 2, wy + wh); ctx.moveTo(wx, wy + wh / 2); ctx.lineTo(wx + ww, wy + wh / 2); ctx.stroke();
  ctx.save(); ctx.translate(90, 330); ctx.rotate(-0.03); fillRR(ctx, 0, 0, 240, 330, 6, '#2b1440'); ctx.save(); rr(ctx, 12, 12, 216, 306, 4); ctx.clip(); ctx.translate(12, 12); viceSunsetScene(ctx, 216, 306, 0, { noCar: true }); ctx.restore(); text(ctx, 'VICE', 120, 275, { size: 50, font: FONT_T, weight: 400, color: '#fff', glow: C.pink, blur: 20 }); ctx.restore();
  fillRR(ctx, 80, 790, 320, 16, 4, '#2a2436');
  [[110, '#ff4f6d'], [145, '#2f6fff'], [175, '#f4b23e'], [210, '#2bb673']].forEach(([x, c], i) => fillRR(ctx, x, 710 + (i % 2) * 14, 28, 80 - (i % 2) * 14, 3, c));
  ctx.fillStyle = '#0c0d16'; ctx.fillRect(0, 1560, W, 360);
  if (o.wallClock) o.wallClock(ctx);
}
function deskV(ctx, y = 1300) { fillRR(ctx, 30, y, 1020, 40, 8, '#4a3428'); ctx.fillStyle = '#3a281e'; ctx.fillRect(70, y + 40, 40, 600); ctx.fillRect(970, y + 40, 40, 600); ctx.save(); ctx.globalCompositeOperation = 'lighter'; fillRR(ctx, 30, y + 36, 1020, 6, 3, 'rgba(199,125,255,0.8)'); ctx.restore(); }
function browserBar(c, w, title) { c.fillStyle = '#0f0f16'; c.fillRect(0, 0, w, 4000); c.fillStyle = '#1b1b26'; c.fillRect(0, 0, w, 70); [C.red, C.yellow, C.green].forEach((col, i) => circle(c, 34 + i * 30, 35, 9, col)); fillRR(c, 140, 16, w - 180, 38, 19, '#2a2a38'); text(c, title, 165, 36, { size: 20, align: 'left', color: '#99a', weight: 400 }); }
function card(ctx, x, y, w, kind, title, sub, t, hl = 0) {
  const h = w * 0.5625;
  if (hl) { ctx.save(); ctx.shadowColor = C.yellow; ctx.shadowBlur = 40 * hl; fillRR(ctx, x - 6, y - 6, w + 12, h + 12, 18, `rgba(255,210,63,${hl})`); ctx.restore(); }
  viceThumb(ctx, x, y, w, h, kind, t);
  ctx.save(); ctx.font = `800 ${Math.round(w * 0.085)}px ${FONT}`; ctx.textAlign = 'left'; ctx.lineJoin = 'round'; ctx.lineWidth = 8; ctx.strokeStyle = '#000';
  wrapLines(ctx, title, w - 30).slice(0, 2).forEach((l, i) => { ctx.strokeText(l, x + 16, y + 44 + i * w * 0.09); ctx.fillStyle = i ? C.yellow : '#fff'; ctx.fillText(l, x + 16, y + 44 + i * w * 0.09); }); ctx.restore();
  if (sub) text(ctx, sub, x, y + h + 32, { size: Math.max(20, w * 0.055), align: 'left', color: '#c9cde0', weight: 700 });
}
function aiFrameV(ctx, t, tag, title) {
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 6; const m = 40, Lc = 70;
  [[m, 150, 1, 1], [W - m, 150, -1, 1], [m, H - 260, 1, -1], [W - m, H - 260, -1, -1]].forEach(([x, y, sx, sy]) => { ctx.beginPath(); ctx.moveTo(x, y + sy * Lc); ctx.lineTo(x, y); ctx.lineTo(x + sx * Lc, y); ctx.stroke(); });
  fillRR(ctx, 80, 190, 300, 66, 33, 'rgba(138,60,255,0.92)'); text(ctx, '✦ ' + tag, 230, 224, { size: 32, color: '#fff', weight: 900 });
  if (Math.floor(t * 2) % 2 === 0) circle(ctx, W - 160, 223, 14, C.red); text(ctx, 'REC', W - 135, 224, { size: 30, align: 'left', color: '#fff', weight: 800 });
  ctx.font = `900 64px ${FONT}`; wrapLines(ctx, title, W - 140).forEach((l, i) => text(ctx, l, W / 2, 340 + i * 76, { size: 64, color: '#fff', weight: 900, stroke: '#000', strokeW: 12 }));
  ctx.restore();
}
// streamer face-cam (generic person, headset)
function streamerCam(ctx, x, y, w, h, seed, t, o = {}) {
  ctx.save(); rr(ctx, x, y, w, h, 16); ctx.clip();
  const r = rng(seed); const bg = ['#2a1146', '#10264a', '#3a1230', '#123a33'][seed % 4];
  ctx.fillStyle = vgrad(ctx, y, y + h, [[0, bg], [1, '#08060f']]); ctx.fillRect(x, y, w, h);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; glow(ctx, x + w * 0.8, y + h * 0.2, w * 0.6, [C.pink, C.cyan, C.purple, C.green][seed % 4], 0.4); ctx.restore();
  const s = h / 330; person(ctx, x + w / 2, y + h + 90 * s, 1.25 * s, seed, { bob: Math.sin(t * 5 + seed) * 4 * s });
  // headset
  ctx.strokeStyle = '#111'; ctx.lineWidth = 10 * s; ctx.beginPath(); ctx.arc(x + w / 2, y + h + 90 * s - 312 * s * 1.25, 52 * s, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();
  if (o.shades) { fillRR(ctx, x + w / 2 - 44 * s, y + h + 90 * s - 312 * s * 1.25 + 6 * s, 88 * s, 22 * s, 8 * s, '#050505'); }
  ctx.restore();
  liveBadge(ctx, x + 14, y + 14, Math.min(1, w / 400));
  if (o.viewers) { fillRR(ctx, x + 14 + 104 * Math.min(1, w / 400), y + 14, 170 * Math.min(1, w / 400), 40 * Math.min(1, w / 400), 8, 'rgba(0,0,0,0.6)'); text(ctx, '● ' + kfmt(o.viewers), x + 14 + 189 * Math.min(1, w / 400), y + 35 * Math.min(1, w / 400) - 0, { size: 24 * Math.min(1, w / 400), color: '#fff', weight: 800 }); }
  if (o.name) text(ctx, o.name, x + w - 16, y + h - 26, { size: 28 * Math.min(1, w / 400), align: 'right', color: '#fff', weight: 900, stroke: '#000', strokeW: 6 });
}
function chatColumn(ctx, x, y, w, h, t, speed = 2.5, seed = 1) {
  ctx.save(); rr(ctx, x, y, w, h, 16); ctx.clip(); ctx.fillStyle = 'rgba(12,10,22,0.92)'; ctx.fillRect(x, y, w, h);
  const r = rng(seed); const names = ['max_v', 'liza', 'kirill07', 'neo', 'arthur', 'dimon', 'vice_fan', 'zzz', 'turbo', 'kate'];
  const N = 40, lh = 52; const off = (t * speed * lh) % lh, base = Math.floor(t * speed);
  for (let i = 0; i < Math.ceil(h / lh) + 1; i++) { const k = base + i; const rr_ = rng(seed * 100 + k); const nm = names[Math.floor(rr_() * names.length)], msg = L.chat[Math.floor(rr_() * L.chat.length)]; const yy = y + h - 30 - i * lh + off;
    text(ctx, nm + ':', x + 18, yy, { size: 26, align: 'left', color: [C.cyan, C.pink, C.yellow, C.green, '#c79bff'][k % 5], weight: 800 }); ctx.font = `800 26px ${FONT}`; text(ctx, msg, x + 26 + ctx.measureText(nm + ':').width, yy, { size: 26, align: 'left', color: '#fff', weight: 600 }); }
  ctx.restore();
}
function dino(ctx, x, y, s, t) {
  // original cartoon dinosaur (flat style)
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const step = Math.sin(t * 4), g = '#3fae5a', gd = '#2c8a44';
  fillRR(ctx, -120 + step * 20, -260, 80, 260, 30, gd); fillRR(ctx, 40 - step * 20, -260, 80, 260, 30, g);
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(-160, -360); ctx.quadraticCurveTo(-520, -300, -720, -420 + Math.sin(t * 3) * 30); ctx.quadraticCurveTo(-480, -220, -140, -220); ctx.fill();
  ellipse(ctx, 0, -380, 230, 190, g);
  ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(80, -500); ctx.quadraticCurveTo(150, -700, 230, -760); ctx.lineTo(330, -690); ctx.quadraticCurveTo(220, -560, 200, -420); ctx.fill();
  const jaw = 0.15 + Math.max(0, Math.sin(t * 2.2)) * 0.35;
  fillRR(ctx, 150, -900, 380, 190, 70, g);
  ctx.save(); ctx.translate(220, -730); ctx.rotate(jaw); fillRR(ctx, 0, -10, 300, 90, 40, gd); ctx.fillStyle = '#fff'; for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(40 + i * 42, -10); ctx.lineTo(60 + i * 42, -40); ctx.lineTo(80 + i * 42, -10); ctx.fill(); } ctx.restore();
  ctx.fillStyle = '#fff'; for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(260 + i * 42, -712); ctx.lineTo(280 + i * 42, -680); ctx.lineTo(300 + i * 42, -712); ctx.fill(); }
  circle(ctx, 330, -840, 30, '#fff'); circle(ctx, 340, -838, 16, '#111');
  ctx.strokeStyle = '#111'; ctx.lineWidth = 14; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(290, -880); ctx.lineTo(380, -860); ctx.stroke();
  fillRR(ctx, 150, -470, 120, 34, 17, gd); fillRR(ctx, 150, -400, 100, 30, 15, gd);
  for (let i = 0; i < 6; i++) { ctx.fillStyle = '#2a7a3c'; ctx.beginPath(); ctx.moveTo(-200 + i * 80, -560 + Math.abs(i - 2.5) * 20); ctx.lineTo(-160 + i * 80, -620 + Math.abs(i - 2.5) * 20); ctx.lineTo(-120 + i * 80, -560 + Math.abs(i - 2.5) * 20); ctx.fill(); }
  ctx.restore();
}
function streamerAvatar(ctx, x, y, r, t) { circle(ctx, x, y, r + 8, C.yellow); ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.clip(); ctx.fillStyle = '#3a1050'; ctx.fillRect(x - r, y - r, r * 2, r * 2); person(ctx, x, y + r * 2.25, r / 110, 11, { bob: 0 }); fillRR(ctx, x - r * 0.42, y - r * 0.12, r * 0.84, r * 0.2, r * 0.08, '#050505'); ctx.restore();
  // crown
  ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.moveTo(x - r * 0.5, y - r * 0.95); ctx.lineTo(x - r * 0.5, y - r * 1.35); ctx.lineTo(x - r * 0.25, y - r * 1.15); ctx.lineTo(x, y - r * 1.45); ctx.lineTo(x + r * 0.25, y - r * 1.15); ctx.lineTo(x + r * 0.5, y - r * 1.35); ctx.lineTo(x + r * 0.5, y - r * 0.95); ctx.fill(); }
function verified(ctx, x, y, s = 1) { circle(ctx, x, y, 18 * s, '#3ea6ff'); ctx.strokeStyle = '#fff'; ctx.lineWidth = 5 * s; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x - 8 * s, y); ctx.lineTo(x - 2 * s, y + 7 * s); ctx.lineTo(x + 9 * s, y - 7 * s); ctx.stroke(); }

const SHOTS = [
  // ===================== SCENE 1 — GTA 6 IS OUT (hook) =====================
  { id: 'a1_hook', draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#ff2e88'], [0.5, '#7b2cff'], [1, '#12063a']]); ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(W / 2, 900); for (let i = 0; i < 18; i++) { ctx.rotate(Math.PI / 9 + t * 0.02); ctx.fillStyle = 'rgba(255,255,255,0.06)'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(1400, -120); ctx.lineTo(1400, 120); ctx.fill(); } ctx.restore();
    ctx.save(); const z = lerp(1.18, 1.0, easeOut(seg(t, 0, 0.35))); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2); shake(ctx, t, 18, 0, 8);
    // phone
    fillRR(ctx, 150, 170, 780, 1580, 90, '#0a0a10'); fillRR(ctx, 172, 192, 736, 1536, 72, '#0f0f18');
    ctx.save(); rr(ctx, 172, 192, 736, 1536, 72); ctx.clip();
    fillRR(ctx, 440, 210, 200, 40, 20, '#000');
    text(ctx, '9:41', 240, 240, { size: 30, color: '#fff', weight: 700, align: 'left' });
    fillRR(ctx, 200, 300, 680, 70, 16, C.red); text(ctx, L.news, 540, 336, { size: 40, color: '#fff', weight: 900, spacing: 4 });
    viceThumb(ctx, 200, 400, 680, 470, 'car', t + 1); liveBadge(ctx, 220, 420, 1.2);
    text(ctx, 'GTA 6 IS', 540, 990, { size: 120, color: '#fff', weight: 900 });
    text(ctx, 'FINALLY', 540, 1120, { size: 120, color: C.yellow, weight: 900 });
    text(ctx, 'HERE!', 540, 1250, { size: 140, color: C.pink, weight: 900, glow: C.pink, blur: 12 });
    for (let i = 0; i < 3; i++) { const t0 = 0.5 + i * 0.45; if (t > t0) { const k = pop(t, t0); ctx.save(); ctx.translate(540, 1420 + i * 100); ctx.scale(k, k); fillRR(ctx, -320, -40, 640, 80, 20, 'rgba(255,255,255,0.1)'); text(ctx, ['🔥 12.4M', '▶ 3.1M LIVE', '♥ 48M'][i].replace('🔥 ', '★ '), 0, 2, { size: 40, color: '#fff', weight: 800 }); ctx.restore(); } }
    ctx.restore(); ctx.restore();
    const fl = Math.exp(-t * 7); if (fl > 0.02) { ctx.fillStyle = `rgba(255,255,255,${fl})`; ctx.fillRect(0, 0, W, H); }
  } },
  { id: 'a2_world', draw(ctx, t, d) {
    bgDark(ctx, '#05061a'); nightSky(ctx, W, H, H, 61);
    ctx.save(); cam(ctx, t, d, 1.0, 1.06);
    text(ctx, 'GTA 6', 540, 230, { size: 110, font: FONT_T, weight: 400, color: C.yellow, glow: C.orange, blur: 20 });
    const rows = [[L.usa, '23:58', 0], [L.europe, '05:58', 0], [L.asia, '12:58', 0], [L.aus, '15:58', 1]];
    rows.forEach(([n, tm, on], i) => { const k = pop(t, 0.1 + i * 0.18); const y = 420 + i * 290; ctx.save(); ctx.translate(540, y + 110); ctx.scale(k, k); ctx.translate(-540, -(y + 110));
      fillRR(ctx, 80, y, 920, 220, 34, on ? 'rgba(57,255,138,0.16)' : 'rgba(255,255,255,0.06)'); if (on) { ctx.save(); ctx.shadowColor = C.green; ctx.shadowBlur = 50; ctx.strokeStyle = C.green; ctx.lineWidth = 6; rr(ctx, 80, y, 920, 220, 34); ctx.stroke(); ctx.restore(); }
      text(ctx, n, 130, y + 80, { size: 64, align: 'left', color: '#fff', weight: 900 }); text(ctx, tm, 130, y + 160, { size: 40, align: 'left', color: '#99a', weight: 600 });
      fillRR(ctx, 640, y + 70, 320, 84, 42, on ? C.green : '#2b2b3d'); text(ctx, on ? L.online : L.waiting, 800, y + 113, { size: 40, color: on ? '#04210f' : '#aab', weight: 900 });
      if (!on) { ctx.strokeStyle = '#aab'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(590, y + 112, 22, 0, Math.PI * 2); ctx.stroke(); ctx.beginPath(); ctx.moveTo(590, y + 112); ctx.lineTo(590 + Math.cos(t * 6) * 15, y + 112 + Math.sin(t * 6) * 15); ctx.stroke(); }
      ctx.restore(); });
    ctx.restore();
  } },
  { id: 'a3_australia', draw(ctx, t, d) {
    ctx.fillStyle = '#07060e'; ctx.fillRect(0, 0, W, H);
    ctx.save(); cam(ctx, t, d, 1.12, 1.0);
    fillRR(ctx, 40, 360, 1000, 1700, 0, '#1b1530');
    const r = rng(7);
    for (let j = 0; j < 7; j++) for (let i = 0; i < 4; i++) { const x = 80 + i * 240, y = 400 + j * 200; const on = t > (i + j) * 0.08; const c = [C.cyan, C.pink, '#7cff9a', C.yellow, '#a98bff'][(i * 3 + j) % 5];
      fillRR(ctx, x, y, 200, 160, 8, '#120c22');
      if (on) { ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.5; ctx.fillStyle = rgrad(ctx, x + 100, y + 60, 0, 150, [[0, c], [1, 'rgba(0,0,0,0)']]); ctx.fillRect(x, y, 200, 160); ctx.restore(); fillRR(ctx, x + 40, y + 26, 120, 64, 4, c); const p = clamp((t - (i + j) * 0.08) * 1.2); fillRR(ctx, x + 50, y + 70, 100 * p, 8, 4, '#fff'); const px = x + 75 + ((i + j) % 2) * 50; ctx.fillStyle = '#05040a'; ctx.beginPath(); ctx.arc(px, y + 138, 36, Math.PI, 0); ctx.fill(); circle(ctx, px, y + 106, 21, '#05040a'); }
      ctx.strokeStyle = '#2a2244'; ctx.lineWidth = 8; ctx.strokeRect(x, y, 200, 160); }
    ctx.restore();
    ctx.fillStyle = 'rgba(7,6,14,0.9)'; ctx.fillRect(0, 0, W, 340);
    const k = pop(t, 0.05, 0.35); ctx.save(); ctx.translate(540, 180); ctx.scale(k, k); ctx.rotate(-0.03); fillRR(ctx, -500, -130, 1000, 260, 30, C.green); lines(ctx, ['AUSTRALIA PLAYERS', 'ARE ONLINE!'], 0, -48, 100, { size: 82, color: '#03200e', weight: 900 }); ctx.restore();
  } },
  { id: 'a4_internet', draw(ctx, t, d) {
    bgDark(ctx, '#0b0b14'); ctx.save(); shake(ctx, t, 12, 0, 3);
    ctx.save(); cam(ctx, t, d, 1.0, 1.1);
    for (let i = 0; i < 14; i++) { const t0 = i * 0.12; if (t < t0) continue; const k = pop(t, t0, 0.25); const r = rng(i + 3); const x = 60 + r() * 600, y = 160 + i * 115; ctx.save(); ctx.translate(x + 240, y + 48); ctx.rotate((r() - 0.5) * 0.12); ctx.scale(k, k); ctx.translate(-x - 240, -y - 48);
      notif(ctx, x, y, 480 + r() * 80, ['#GTA6', 'GTA 6', 'Vice City', 'LIVE', '#GTA6'][i % 5] + ' · ' + kfmt(1e5 + r() * 9e6), [L.watching, L.views, L.subs][i % 3], [C.pink, C.cyan, C.orange, C.purple, C.green, C.red][i % 6], 1, ['bell', 'plus', 'up', 'msg'][i % 4]); ctx.restore(); }
    ctx.restore();
    const k = pop(t, 0.3, 0.35); ctx.save(); ctx.translate(540, 1000); ctx.scale(k, k); ctx.rotate(-0.05); ctx.font = `900 96px ${FONT}`; const ls = wrapLines(ctx, L.explode, 900); ls.forEach((l, i) => text(ctx, l, 0, (i - (ls.length - 1) / 2) * 110, { size: 96, color: C.yellow, weight: 900, stroke: '#000', strokeW: 16 })); ctx.restore();
    ctx.restore();
  } },
  // ===================== SCENE 2 — EVERYONE WATCHES STREAMS =====================
  { id: 'b1_live', draw(ctx, t, d) {
    bgDark(ctx, '#0a0814');
    const tiles = [[40, 160, 'ViceQueen'], [550, 160, 'TurboMax'], [40, 780, 'PixelRaider'], [550, 780, STREAMER]];
    tiles.forEach(([x, y, n], i) => { const k = easeOut(seg(t, i * 0.15, i * 0.15 + 0.3)); ctx.save(); ctx.globalAlpha = k; ctx.translate((1 - k) * (i % 2 ? 300 : -300), 0); streamerCam(ctx, x, y, 490, 580, 20 + i, t, { viewers: [182e3, 96e3, 240e3, 1.2e6][i] + t * 3000, name: n, shades: i === 3 }); ctx.restore(); });
    text(ctx, 'GTA 6', 540, 1500, { size: 150, font: FONT_T, weight: 400, color: '#fff', glow: C.red, blur: 20 });
    liveBadge(ctx, 400, 1610, 2.9);
  } },
  { id: 'b2_stream', draw(ctx, t, d) {
    bgDark(ctx, '#05050a');
    ctx.save(); rr(ctx, 0, 120, W, 900, 0); ctx.clip(); sceneFill(ctx, viceNightStreet, t, 0.5, { scroll: t * 220 }); car(ctx, 140, 980, 1.25, C.pink, { lights: true, underglow: 'rgba(25,227,255,0.6)' }); ctx.restore();
    liveBadge(ctx, 30, 150, 1.3); text(ctx, `● ${kfmt(1.2e6 + t * 8000)}`, 180, 177, { size: 34, align: 'left', color: '#fff', weight: 900, stroke: '#000', strokeW: 6 });
    streamerCam(ctx, 700, 700, 340, 280, 23, t, { shades: true });
    chatColumn(ctx, 30, 1040, 1020, 720, t, 4, 3);
    text(ctx, STREAMER, 540, 80, { size: 52, color: '#fff', weight: 900 }); verified(ctx, 540 + 150, 80, 1.1);
  } },
  { id: 'b3_millions', draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#2a0838'], [1, '#07040f']]); ctx.fillRect(0, 0, W, H);
    for (let i = 0; i < 26; i++) { const r = rng(i + 50); const y = 150 + r() * 1650, sp = 300 + r() * 500; const x = W - ((t * sp + r() * 2000) % (W + 700)); fillRR(ctx, x, y, 460, 64, 20, 'rgba(255,255,255,0.07)'); text(ctx, L.chat[i % L.chat.length], x + 24, y + 33, { size: 30, align: 'left', color: 'rgba(255,255,255,0.65)', weight: 700 }); }
    ctx.save(); cam(ctx, t, d, 0.95, 1.08);
    liveBadge(ctx, 300, 640, 5);
    const v = 2.1e6 + t * 7.4e5; text(ctx, num(v), 540, 1000, { size: 150, color: '#fff', weight: 900, glow: C.red, blur: 30 }); text(ctx, L.viewers.toUpperCase(), 540, 1130, { size: 64, color: '#ffb3c6', weight: 900, spacing: 6 });
    ctx.restore();
    particlesUp(ctx, t, 30, 5, [60, 800, 960, 1000], (x, y, k, i) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI); text(ctx, '♥', x, y, { size: 50 + (i % 3) * 14, color: [C.pink, C.red, C.purple][i % 3] }); ctx.restore(); });
  } },
  // ===================== SCENE 2b — THE HERO WATCHES =====================
  { id: 'c1_open', draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.1, 540, 1000);
    roomV(ctx, t);
    litHero(ctx, { x: 250, y: 1080, R: 125, view: 'side', dir: 1, expr: 'neutral', body: 'bust', arms: 'desk', typing: t * 8, blink: t > 1 && t < 1.1 }, { from: [720, 1090, 600, 'rgba(255,100,130,0.3)'] });
    deskV(ctx);
    crtMonitor(ctx, 470, 920, 500, 340, (c, w, h) => { c.fillStyle = '#0f0f16'; c.fillRect(0, 0, w, h); playIcon(c, w / 2, h / 2 - 20, 2.2 * easeOutBack(seg(t, 0.2, 0.6))); fillRR(c, 60, h - 60, (w - 120) * seg(t, 0.4, 1.4), 10, 5, C.red); });
    glow(ctx, 720, 1090, 500, 'rgba(255,60,90,0.25)');
    ctx.restore(); vignette(ctx, 0.5);
  } },
  { id: 'c2_streams', draw(ctx, t, d) {
    bgDark(ctx, '#05050a'); const s2 = TM.extra.stream2 - TM.starts.c2_streams, s3 = TM.extra.stream3 - TM.starts.c2_streams;
    ctx.save(); cam(ctx, t, d, 1.0, 1.05, 540, 900);
    crtMonitor(ctx, 70, 230, 940, 1280, (c, w, h) => {
      browserBar(c, w, 'video / live / gta 6');
      [[0, 0], [s2, 1], [s3, 2]].forEach(([t0, i]) => { if (t < t0 - 0.05) return; const k = easeOutBack(seg(t, t0, t0 + 0.3)); const y = 100 + i * 390; c.save(); c.translate(w / 2, y + 180); c.scale(k, k); c.translate(-w / 2, -(y + 180)); streamerCam(c, 40, y, w - 80, 360, 30 + i, t, { viewers: [3.4e5, 1.1e6, 7.8e5][i], name: ['ViceQueen', STREAMER, 'TurboMax'][i], shades: i === 1 }); c.restore(); });
    });
    ctx.restore();
    const n = t >= s3 ? 3 : t >= s2 ? 2 : 1; const pk = t >= s3 ? t - s3 : t >= s2 ? t - s2 : t;
    ctx.save(); ctx.translate(900, 200); const k = 1 + 0.3 * Math.exp(-pk * 8); ctx.scale(k, k); circle(ctx, 0, 0, 90, C.red); text(ctx, String(n), 0, 6, { size: 120, color: '#fff', weight: 900 }); ctx.restore();
  } },
  { id: 'c3_hours', draw(ctx, t, d) {
    const hrs = seg(t, 0.2, d - 0.3);
    ctx.save(); cam(ctx, t, d, 1.0, 1.06, 540, 1100);
    roomV(ctx, t, { day: true, dusk: hrs, wallClock: (c) => { const cx = 470, cy = 470; circle(c, cx, cy, 90, '#e8e2d0'); circle(c, cx, cy, 80, '#fbf7ea'); const hh = 2 + hrs * 5; const ha = hh / 12 * Math.PI * 2 - Math.PI / 2, ma = (hh % 1) * Math.PI * 2 - Math.PI / 2; c.strokeStyle = '#222'; c.lineCap = 'round'; c.lineWidth = 9; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(ha) * 42, cy + Math.sin(ha) * 42); c.stroke(); c.lineWidth = 5; c.beginPath(); c.moveTo(cx, cy); c.lineTo(cx + Math.cos(ma) * 64, cy + Math.sin(ma) * 64); c.stroke(); circle(c, cx, cy, 8, C.red); } });
    litHero(ctx, { x: 270, y: 1110, R: 125, view: 'side', dir: 1, expr: 'bored', body: 'bust', arms: 'chin', tilt: 0.1 + Math.sin(t * 1.4) * 0.04 }, { from: [800, 1100, 700, 'rgba(255,90,140,0.3)'] });
    deskV(ctx);
    crtMonitor(ctx, 560, 960, 400, 290, (c, w, h) => { streamerCam(c, 0, 0, w, h, 31 + Math.floor(t * 1.2) % 3, t, { name: STREAMER }); });
    // snacks
    ellipse(ctx, 460, 1296, 70, 20, '#c43b3b'); for (let i = 0; i < 7; i++) circle(ctx, 420 + i * 13, 1282 - (i % 2) * 8, 12, '#f2c14e');
    ctx.restore();
    text(ctx, L.hours, 540, 200, { size: 120, color: '#fff', weight: 900, stroke: '#000', strokeW: 14, alpha: smooth(seg(t, 0.2, 0.5)) });
    vignette(ctx, 0.5);
  } },
  { id: 'c4_notice', draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.25, 540, 820);
    roomV(ctx, t);
    ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(0, 0, W, H);
    litHero(ctx, { x: 540, y: 880, R: 270, view: 'front', expr: t < 0.5 ? 'bored' : 'surprised', body: 'bust', arms: 'down', lookX: 0.6 }, { from: [540, 1900, 1000, 'rgba(120,200,255,0.2)'] });
    ctx.restore();
    if (t > 0.5) { const k = pop(t, 0.5); ctx.save(); ctx.translate(880, 360); ctx.scale(k, k); ctx.rotate(0.15); text(ctx, '!', 0, 0, { size: 260, color: C.yellow, weight: 900, stroke: '#000', strokeW: 16 }); ctx.restore(); }
    vignette(ctx, 0.6);
  } },
  { id: 'c5_thousands', draw(ctx, t, d) {
    bgDark(ctx, '#0b0b14');
    ctx.save(); cam(ctx, t, d, 1.15, 0.95);
    const kinds = ['sun', 'night', 'car', 'sun2'];
    for (let i = 0; i < 24; i++) { const col = i % 3, row = Math.floor(i / 3); const t0 = i * 0.06; if (t < t0) continue; const k = easeOutBack(seg(t, t0, t0 + 0.25)); const x = 50 + col * 335, y = 140 + row * 225; ctx.save(); ctx.translate(x + 155, y + 90); ctx.scale(k, k); ctx.translate(-x - 155, -y - 90); viceThumb(ctx, x, y, 310, 174, kinds[i % 4], t + i); fillRR(ctx, x + 10, y + 10, 76, 36, 8, C.red); text(ctx, 'NEW', x + 48, y + 29, { size: 22, color: '#fff', weight: 900 }); ctx.restore(); }
    ctx.restore();
    fillRR(ctx, 60, 1430, 960, 240, 40, 'rgba(10,8,20,0.92)'); text(ctx, '+' + num(Math.floor(lerp(1200, 12400, easeOut(seg(t, 0, d))))), 540, 1520, { size: 120, color: C.cyan, weight: 900, glow: C.cyan, blur: 14 }); text(ctx, L.newVids, 540, 1625, { size: 44, color: '#fff', weight: 700 });
  } },
  { id: 'c6_millions', draw(ctx, t, d) {
    bgDark(ctx, '#0b0b14');
    ctx.save(); cam(ctx, t, d, 1.0, 1.08);
    const vals = [4.2e6, 7.8e6, 2.9e6]; const ks = ['sun', 'car', 'night'];
    vals.forEach((v, i) => { const k = pop(t, i * 0.2); const y = 170 + i * 560; ctx.save(); ctx.translate(540, y + 240); ctx.scale(k, k); ctx.translate(-540, -(y + 240)); card(ctx, 90, y, 900, ks[i], L.vidTitles[i * 2], '', t, i === 1 ? 0.8 : 0); fillRR(ctx, 520, y + 380, 460, 110, 30, 'rgba(0,0,0,0.75)'); text(ctx, kfmt(v * (0.6 + 0.4 * easeOut(seg(t, 0, d)))) + ' ' + (LANG === 'ru' ? '' : ''), 750, y + 435, { size: 76, color: C.yellow, weight: 900 }); ctx.restore(); });
    ctx.restore();
    particlesUp(ctx, t, 18, 4, [60, 200, 960, 1500], (x, y, k) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * 0.9; circle(ctx, x, y, 32, '#f2c14e'); text(ctx, '$', x, y + 2, { size: 36, color: '#8a5a00', weight: 900 }); ctx.restore(); });
  } },
  // ===================== SCENE 3 — THE CHOICE =====================
  { id: 'd1_question', draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#1d0b33'], [1, '#07040f']]); ctx.fillRect(0, 0, W, H);
    ctx.save(); cam(ctx, t, d, 1.05, 1.15, 540, 900);
    litHero(ctx, { x: 540, y: 950, R: 260, view: '3q', dir: -1, expr: 'neutral', body: 'bust', arms: 'down', lookX: -1, lookY: -1, tilt: -0.06 }, { from: [200, 300, 900, 'rgba(160,90,255,0.35)'] });
    ctx.restore();
    for (let i = 0; i < 3; i++) { const t0 = 0.1 + i * 0.3; if (t < t0) continue; const k = pop(t, t0); ctx.save(); ctx.translate([220, 840, 560][i], [360, 300, 180][i] - (t - t0) * 20); ctx.scale(k, k); text(ctx, '?', 0, 0, { size: [150, 120, 190][i], color: [C.cyan, C.pink, C.yellow][i], weight: 900, stroke: '#000', strokeW: 12 }); ctx.restore(); }
  } },
  { id: 'd2_choice', draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#0d0a1e'], [1, '#05030c']]); ctx.fillRect(0, 0, W, H);
    const k1 = pop(t, 0.05), k2 = pop(t, 0.35), kOr = pop(t, 0.2);
    ctx.save(); ctx.translate(540, 560); ctx.scale(k1, k1); fillRR(ctx, -460, -190, 920, 380, 40, '#232233'); ctx.strokeStyle = '#555'; ctx.lineWidth = 5; rr(ctx, -460, -190, 920, 380, 40); ctx.stroke(); playIcon(ctx, 0, -100, 1.5, '#555'); lines(ctx, ['WATCH OTHER', 'PEOPLE PLAY'], 0, 10, 86, { size: 78, color: '#bbbcc8', weight: 900 }); if (L.watchSub) text(ctx, L.watchSub, 0, 150, { size: 34, color: '#8889a0', weight: 600 }); ctx.restore();
    ctx.save(); ctx.translate(540, 900); ctx.scale(kOr, kOr); text(ctx, 'OR', 0, 0, { size: 110, color: '#fff', weight: 900 }); ctx.restore();
    const glowA = 0.6 + 0.4 * Math.sin(t * 8);
    ctx.save(); ctx.translate(540, 1250); ctx.scale(k2, k2); ctx.shadowColor = C.pink; ctx.shadowBlur = 60 * glowA; const g = ctx.createLinearGradient(-460, 0, 460, 0); g.addColorStop(0, C.purple); g.addColorStop(1, C.pink); rr(ctx, -460, -190, 920, 380, 40); ctx.fillStyle = g; ctx.fill(); ctx.shadowBlur = 0; text(ctx, '✦', 0, -110, { size: 80, color: '#fff' }); lines(ctx, ['CREATE YOUR', 'OWN VIDEOS'], 0, 10, 86, { size: 78, color: '#fff', weight: 900 }); if (L.createSub) text(ctx, L.createSub, 0, 150, { size: 34, color: '#ffe0f0', weight: 600 }); ctx.restore();
    const cy = 900 + Math.sin(t * 3) * 330; cursor(ctx, 760 + Math.sin(t * 2) * 30, cy, 2.2);
  } },
  { id: 'd3_decide', draw(ctx, t, d) {
    bgDark(ctx, '#05050a');
    // streams closing
    const cls = easeIn(seg(t, 0.35, 0.9));
    ctx.save(); cam(ctx, t, d, 1.0, 1.05, 540, 900);
    crtMonitor(ctx, 70, 230, 940, 1280, (c, w, h) => {
      c.fillStyle = vgrad(c, 0, h, [[0, '#140b2e'], [1, '#08060f']]); c.fillRect(0, 0, w, h);
      if (cls < 1) [0, 1, 2].forEach(i => { c.save(); const y = 100 + i * 390; c.globalAlpha = 1 - cls; c.translate(w / 2, y + 180); c.scale(1 - cls * 0.8, 1 - cls * 0.8); c.rotate(cls * (i - 1) * 0.4); c.translate(-w / 2, -(y + 180)); streamerCam(c, 40, y, w - 80, 360, 30 + i, t); c.save(); c.translate(w - 90, y + 40); circle(c, 0, 0, 30, C.red); text(c, '×', 0, 2, { size: 50, color: '#fff', weight: 900 }); c.restore(); c.restore(); });
      if (t > 0.9) { const k = pop(t, 0.9); c.save(); c.translate(w / 2, h / 2); c.scale(k, k); const g = c.createLinearGradient(-380, 0, 380, 0); g.addColorStop(0, C.purple); g.addColorStop(1, C.pink); rr(c, -380, -150, 760, 300, 36); c.fillStyle = g; c.fill(); lines(c, ['CREATE YOUR', 'OWN VIDEOS'], 0, -38, 80, { size: 72, color: '#fff', weight: 900 }); c.restore(); }
      cursor(c, w / 2 + 90, h / 2 + 40, 1.8, t > 0.2 && t < 0.7 ? (t - 0.2) / 0.5 : 0);
    });
    ctx.restore();
    if (t > 0.9) { ctx.save(); ctx.globalAlpha = smooth(seg(t, 0.9, 1.2)); litHero(ctx, { x: 200, y: 1660, R: 150, view: '3q', dir: 1, expr: 'determined', body: 'bust', arms: 'down' }, { from: [700, 900, 900, 'rgba(255,90,200,0.35)'] }); ctx.restore(); }
    const fl = t > 0.2 ? Math.exp(-(t - 0.2) * 10) : 0; if (fl > 0.02) { ctx.fillStyle = `rgba(255,255,255,${fl * 0.6})`; ctx.fillRect(0, 0, W, H); }
  } },
  // ===================== SCENE 4 — CREATING =====================
  { id: 'e1_computer', draw(ctx, t, d) {
    bgDark(ctx, '#05040b');
    ctx.save(); cam(ctx, t, d, 1.0, 1.35, 540, 960);
    roomV(ctx, t); ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, W, H); deskV(ctx);
    const pulse = 0.7 + 0.3 * Math.sin(t * 5);
    crtMonitor(ctx, 290, 900, 500, 360, (c, w, h) => { c.fillStyle = '#12052a'; c.fillRect(0, 0, w, h); c.save(); c.globalCompositeOperation = 'lighter'; glow(c, w / 2, h / 2, 300, `rgba(170,90,255,${pulse})`); c.restore(); text(c, '✦', w / 2, h / 2 - 50, { size: 110, color: '#fff', glow: C.purple, blur: 30 }); text(c, L.mystery, w / 2, h / 2 + 80, { size: 40, font: FONT_T, weight: 400, color: '#fff', glow: C.purple, blur: 20 }); });
    glow(ctx, 540, 1080, 800, `rgba(150,70,255,${0.35 * pulse})`);
    particlesUp(ctx, t, 40, 9, [200, 600, 680, 800], (x, y, k) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI); ctx.globalCompositeOperation = 'lighter'; circle(ctx, x, y, 5, '#d8b8ff'); ctx.restore(); });
    litHero(ctx, { x: 540, y: 1560, R: 160, view: 'back', body: 'bust', arms: 'down' }, { shade: 0.3, from: [540, 1080, 700, 'rgba(170,100,255,0.45)'] });
    ctx.restore(); vignette(ctx, 0.7);
  } },
  { id: 'e2_program', draw(ctx, t, d) {
    bgDark(ctx, '#07060f');
    ctx.save(); cam(ctx, t, d, 1.0, 1.05, 540, 900);
    crtMonitor(ctx, 70, 230, 940, 1280, (c, w, h) => {
      c.fillStyle = vgrad(c, 0, h, [[0, '#140b2e'], [1, '#08060f']]); c.fillRect(0, 0, w, h);
      text(c, 'AI VIDEO STUDIO', 40, 64, { size: 44, font: FONT_T, weight: 400, align: 'left', color: '#fff', glow: C.purple, blur: 20 });
      text(c, L.describe, 40, 160, { size: 34, align: 'left', color: '#9a8fd0', weight: 600 });
      fillRR(c, 40, 190, w - 80, 380, 24, '#1a1236'); c.strokeStyle = 'rgba(160,120,255,0.6)'; c.lineWidth = 3; rr(c, 40, 190, w - 80, 380, 24); c.stroke();
      const typed = L.prompt.slice(0, Math.floor(clamp(t * 42, 0, L.prompt.length)));
      c.font = `600 48px ${FONT}`; const ls = wrapLines(c, typed, w - 160); ls.forEach((l, i) => text(c, l, 75, 255 + i * 64, { size: 48, align: 'left', color: '#fff', weight: 600 }));
      const press = t > d - 0.6 ? 0.94 : 1; c.save(); c.translate(w / 2, 690); c.scale(press, press); const bg = c.createLinearGradient(-330, 0, 330, 0); bg.addColorStop(0, C.purple); bg.addColorStop(1, C.pink); rr(c, -330, -60, 660, 120, 60); c.fillStyle = bg; c.fill(); text(c, L.generate, 0, 2, { size: 54, color: '#fff', weight: 900 }); c.restore();
      for (let i = 0; i < 4; i++) { const k = seg(t, 0.6 + i * 0.3, 1.0 + i * 0.3); const x = 40 + (i % 2) * 440, y = 800 + Math.floor(i / 2) * 230; fillRR(c, x, y, 420, 210, 14, '#1a1236'); if (k > 0) { c.save(); c.globalAlpha = k; viceThumb(c, x, y, 420, 210, ['car', 'night', 'sun', 'sun2'][i], t); c.restore(); } else text(c, L.generating, x + 210, y + 105, { size: 28, color: '#9a8fd0', weight: 600 }); }
    });
    ctx.restore(); vignette(ctx, 0.45);
  } },
  { id: 'e3_vid1', draw(ctx, t, d) {
    // "10 CRAZY THINGS IN GTA 6" — car jump over the palms
    sunsetSky(ctx, W, H, 1250); retroSun(ctx, 540, 1100, 280); cityLayers(ctx, t, 1300, t * 120, false, 12);
    ctx.fillStyle = '#1a0c26'; ctx.fillRect(0, 1300, W, 620);
    ctx.fillStyle = '#3a2448'; ctx.beginPath(); ctx.moveTo(-50, 1500); ctx.lineTo(380, 1500); ctx.lineTo(520, 1380); ctx.lineTo(520, 1500); ctx.lineTo(-50, 1500); ctx.fill();
    for (let i = 0; i < 4; i++) palm(ctx, 600 + i * 130, 1520, 380 + (i % 2) * 60, { sway: t * 2 + i, color: '#14081f' });
    const jt = (t % 2.2) / 2.2; const cx = lerp(-300, 1300, jt), cy = 1470 - Math.sin(clamp((jt - 0.25) / 0.6) * Math.PI) * 650;
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(-0.25 + jt * 0.4); car(ctx, -210, 0, 1.0, C.cyan, { lights: true }); ctx.restore();
    ctx.save(); ctx.translate(880, 820); ctx.rotate(0.12); circle(ctx, 0, 0, 110, C.yellow); text(ctx, '#' + (10 - Math.floor(t / 1.1) % 10), 0, 8, { size: 96, color: '#1a0c26', weight: 900 }); ctx.restore();
    aiFrameV(ctx, t, L.v1, '10 CRAZY THINGS IN GTA 6');
  } },
  { id: 'e4_dino', draw(ctx, t, d) {
    ctx.save(); shake(ctx, (t % 0.9), 16, 0, 9);
    sceneFill(ctx, viceNightStreet, t, 0.5, { scroll: 40 });
    dino(ctx, 380, 1830, 0.95, t);
    car(ctx, 1200 - t * 900, 1880, 0.8, C.yellow, { flip: true, lights: true });
    ctx.restore();
    aiFrameV(ctx, t, L.v2, L.t2);
  } },
  { id: 'e5_vanish', draw(ctx, t, d) {
    nightSky(ctx, W, H, 1500, 14);
    const sk = skylineCanvas('vanishSky', 1080, 900, { seed: 31, minW: 80, maxW: 200, minH: 300, maxH: 820, color: '#1a1238', edge: '#2a1d55', windows: true, lit: 0.5, win: 7 });
    const k = seg(t, 0.4, d - 0.4);
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, 1500 - 0); ctx.clip();
    const cut = 600 + (1 - k) * 0; ctx.drawImage(sk, 0, 600);
    // dissolve: pixel squares fly up from the top down
    const front = lerp(600, 1520, k);
    ctx.globalCompositeOperation = 'destination-out'; ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, front - 40);
    ctx.globalCompositeOperation = 'source-over';
    const r = rng(8); for (let i = 0; i < 260; i++) { const x = r() * W, y0 = 600 + r() * 900; if (y0 > front) continue; const age = (front - y0) / 300; const y = y0 - age * 200 - r() * 50; ctx.globalAlpha = Math.max(0, 1 - age); ctx.fillStyle = [C.cyan, C.pink, '#ffd98a', '#7ff3ff'][i % 4]; ctx.fillRect(x, y, 14, 14); }
    ctx.restore(); ctx.globalAlpha = 1;
    ctx.fillStyle = '#0a0612'; ctx.fillRect(0, 1500, W, 420);
    aiFrameV(ctx, t, L.v3, L.t3);
  } },
  // ===================== SCENE 5 — PUBLISHING =====================
  { id: 'f1_upload', draw(ctx, t, d) {
    bgDark(ctx, '#05050a');
    ctx.save(); cam(ctx, t, d, 1.0, 1.04, 540, 900);
    crtMonitor(ctx, 70, 230, 940, 1280, (c, w, h) => {
      c.fillStyle = '#121219'; c.fillRect(0, 0, w, h);
      fillRR(c, 30, 30, w - 60, (w - 60) * 0.5625, 10, '#000'); viceThumb(c, 30, 30, w - 60, (w - 60) * 0.5625, 'car', t * 2);
      const title = '10 CRAZY THINGS IN GTA 6'; const n = Math.floor(clamp(t * 26, 0, title.length));
      c.font = `900 64px ${FONT}`; wrapLines(c, title.slice(0, n), w - 140).forEach((l, i) => text(c, l, w / 2, 120 + i * 76, { size: 64, color: i ? C.yellow : '#fff', weight: 900, stroke: '#000', strokeW: 12 }));
      fillRR(c, 20, 560, w - 40, 300, 14, '#1b1b25');
      [[C.purple, [[0, 180], [190, 200], [400, 170], [580, 200]]], [C.cyan, [[60, 300], [380, 260]]], ['#3fbf6f', [[0, 780]]]].forEach(([col, cl], r) => cl.forEach(([x, wd]) => fillRR(c, 60 + x, 590 + r * 85, wd - 6, 70, 8, col)));
      c.fillStyle = C.red; c.fillRect(60 + ((t * 300) % 780), 570, 5, 280);
      const p = seg(t, 0.8, d - 0.3); c.save(); c.translate(w / 2, 1030); fillRR(c, -420, -130, 840, 260, 30, '#1d1d2b'); text(c, p < 1 ? L.uploading : L.published, 0, -60, { size: 52, color: p < 1 ? '#fff' : C.green, weight: 900 }); fillRR(c, -360, 20, 720, 36, 18, '#2c2c3c'); fillRR(c, -360, 20, 720 * p, 36, 18, p < 1 ? C.red : C.green); text(c, `${Math.floor(p * 100)}%`, 0, 95, { size: 40, color: '#ccc', weight: 700 }); c.restore();
    });
    ctx.restore(); vignette(ctx, 0.45);
  } },
  { id: 'f2_nobody', draw(ctx, t, d) {
    ctx.save(); cam(ctx, t, d, 1.0, 1.06, 540, 1100);
    roomV(ctx, t);
    litHero(ctx, { x: 270, y: 1090, R: 125, view: 'side', dir: 1, expr: 'worried', body: 'bust', arms: 'chin', tilt: 0.05 }, { from: [800, 1100, 700, 'rgba(120,190,255,0.3)'] });
    deskV(ctx);
    const v = Math.floor(lerp(0, 100, easeIn(seg(t, 0.2, d - 0.2))));
    crtMonitor(ctx, 560, 960, 400, 290, (c, w, h) => { c.fillStyle = '#101018'; c.fillRect(0, 0, w, h); viceThumb(c, 20, 20, 150, 84, 'car', 0); text(c, '10 CRAZY…', 185, 45, { size: 26, align: 'left', color: '#fff', weight: 900 }); text(c, L.viewsCap, 25, 160, { size: 30, align: 'left', color: '#aab', weight: 700 }); text(c, String(v), 25, 225, { size: 76, align: 'left', color: '#fff', weight: 900 }); });
    ctx.restore();
    text(ctx, String(v), 540, 300, { size: 220, color: '#fff', weight: 900, stroke: '#000', strokeW: 16 }); text(ctx, L.views, 540, 440, { size: 64, color: '#aab', weight: 800, stroke: '#000', strokeW: 8 });
    vignette(ctx, 0.55);
  } },
  { id: 'f3_gaining', draw(ctx, t, d) {
    bgDark(ctx, '#0b0b14');
    ctx.save(); cam(ctx, t, d, 1.0, 1.1, 540, 700);
    const ks = ['car', 'night', 'sun'], ttl = ['10 CRAZY THINGS IN GTA 6', L.t2, L.t3];
    ttl.forEach((ti, i) => { const y = 140 + i * 560; const hl = i === 0 ? smooth(seg(t, 0.4, 1.0)) : 0; ctx.save(); if (i) ctx.globalAlpha = lerp(1, 0.45, smooth(seg(t, 0.4, 1))); card(ctx, 90, y, 900, ks[i], ti, '', t, hl); ctx.restore();
      if (i === 0 && t > 0.6) { const k = pop(t, 0.6); ctx.save(); ctx.translate(880, y + 410); ctx.scale(k, k); circle(ctx, 0, 0, 80, C.green); ctx.fillStyle = '#04210f'; ctx.beginPath(); ctx.moveTo(0, -46); ctx.lineTo(40, 6); ctx.lineTo(-40, 6); ctx.fill(); ctx.fillRect(-14, 0, 28, 40); ctx.restore(); } });
    ctx.restore();
  } },
  { id: 'f4_counter', draw(ctx, t, d) {
    const t10 = TM.extra.v10k - TM.starts.f4_counter, t100 = TM.extra.v100k - TM.starts.f4_counter;
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#0c0a1c'], [1, '#170b26']]); ctx.fillRect(0, 0, W, H);
    const v = t < t10 - 0.3 ? lerp(800, 1000, easeOut(seg(t, 0, 0.3))) : t < t100 - 0.3 ? lerp(1000, 10000, easeOut(seg(t, t10 - 0.3, t10))) : lerp(10000, 100000, easeOut(seg(t, t100 - 0.3, t100))) + Math.max(0, t - t100) * 4000;
    ctx.save(); shake(ctx, t, 14, t10, 8); shake(ctx, t, 22, t100, 7);
    viceThumb(ctx, 70, 150, 940, 528, 'car', t); text(ctx, '10 CRAZY THINGS', 110, 230, { size: 70, align: 'left', color: '#fff', weight: 900, stroke: '#000', strokeW: 12 }); text(ctx, 'IN GTA 6', 110, 315, { size: 70, align: 'left', color: C.yellow, weight: 900, stroke: '#000', strokeW: 12 });
    text(ctx, L.viewsCap, 540, 780, { size: 48, color: '#99a', weight: 800, spacing: 6 });
    const pk = 1 + 0.12 * ((t > t10 ? Math.exp(-(t - t10) * 8) : 0) + (t > t100 ? Math.exp(-(t - t100) * 8) : 0));
    ctx.save(); ctx.translate(540, 940); ctx.scale(pk, pk); text(ctx, num(v), 0, 0, { size: 200, color: '#fff', weight: 900, glow: C.green, blur: 30 }); ctx.restore();
    ctx.save(); ctx.translate(90, 1330); ctx.strokeStyle = C.green; ctx.lineWidth = 10; ctx.beginPath(); for (let i = 0; i <= 50; i++) { const k = i / 50; ctx.lineTo(k * 900, -Math.pow(k, 3) * 260 * Math.min(1, v / 100000 + 0.1)); } ctx.stroke(); ctx.restore();
    ctx.restore();
    if (t > t100) { const k = pop(t, t100 + 0.05, 0.35); ctx.save(); ctx.translate(540, 1560); ctx.rotate(-0.04); ctx.scale(k, k); ctx.shadowColor = C.red; ctx.shadowBlur = 50; fillRR(ctx, -480, -110, 960, 220, 30, C.red); ctx.shadowBlur = 0; text(ctx, '▲ YOUR VIDEO', 0, -38, { size: 72, color: '#fff', weight: 900 }); text(ctx, 'IS TRENDING!', 0, 50, { size: 72, color: C.yellow, weight: 900 }); ctx.restore(); }
    particlesUp(ctx, t, 26, 21, [60, 700, 960, 900], (x, y, k, i) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * 0.8; text(ctx, i % 2 ? '+1' : '♥', x, y, { size: 44, color: i % 2 ? C.green : C.pink, weight: 900 }); ctx.restore(); });
  } },
  // ===================== SCENE 6 — NEW GOAL =====================
  { id: 'g1_shock', draw(ctx, t, d) {
    ctx.save(); shake(ctx, t, 20, 0, 5); cam(ctx, t, d, 1.15, 1.0, 540, 800);
    roomV(ctx, t); ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(0, 0, W, H);
    litHero(ctx, { x: 540, y: 880, R: 280, view: 'front', expr: 'surprised', body: 'bust', arms: 'down', bob: -10 * Math.abs(Math.sin(t * 9)) * Math.exp(-t * 2) }, { from: [540, 1900, 1000, 'rgba(90,255,170,0.22)'] });
    ctx.restore();
    L.comments.forEach((s, i) => { const t0 = 0.15 + i * 0.25; if (t < t0) return; const k = pop(t, t0, 0.25); const x = i % 2 ? 560 : 60, y = 1380 + Math.floor(i / 2) * 120; if (y > 1760) return; ctx.save(); ctx.translate(x + 230, y + 45); ctx.scale(k, k); ctx.translate(-x - 230, -y - 45); fillRR(ctx, x, y, 460, 92, 22, 'rgba(18,16,30,0.92)'); circle(ctx, x + 44, y + 46, 26, [C.cyan, C.orange, C.purple, C.green, C.yellow][i]); text(ctx, s, x + 84, y + 47, { size: 30, align: 'left', color: '#fff', weight: 700 }); ctx.restore(); });
    particlesUp(ctx, t, 16, 31, [60, 200, 960, 1000], (x, y, k) => { ctx.save(); ctx.globalAlpha = Math.sin(k * Math.PI) * 0.8; text(ctx, '+1', x, y, { size: 44, color: C.green, weight: 900 }); ctx.restore(); });
  } },
  { id: 'g2_others', draw(ctx, t, d) {
    bgDark(ctx, '#07060e');
    // top: crowd of viewers (backs) watching a stream
    ctx.save(); rr(ctx, 0, 0, W, 930, 0); ctx.clip(); ctx.fillStyle = '#120c22'; ctx.fillRect(0, 0, W, 930);
    streamerCam(ctx, 190, 150, 700, 420, 33, t, { viewers: 2.4e6, name: STREAMER, shades: true });
    glow(ctx, 540, 360, 700, 'rgba(255,60,120,0.25)');
    for (let i = 0; i < 7; i++) person(ctx, 60 + i * 160, 1100 + (i % 2) * 30, 1.3, 70 + i, { back: true, bob: Math.sin(t * 2 + i) * 3 });
    ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(0, 0, W, 930);
    ctx.restore();
    fillRR(ctx, 40, 40, 620, 70, 20, 'rgba(0,0,0,0.7)'); text(ctx, L.them, 60, 76, { size: 38, align: 'left', color: '#bbb', weight: 800 });
    ctx.fillStyle = C.pink; ctx.fillRect(0, 928, W, 8);
    // bottom: hero building his channel
    ctx.save(); rr(ctx, 0, 936, W, 984, 0); ctx.clip(); ctx.translate(0, 936 - 560); roomV(ctx, t); deskV(ctx, 1500);
    crtMonitor(ctx, 520, 1180, 440, 300, (c, w, h) => { c.fillStyle = '#101018'; c.fillRect(0, 0, w, h); text(c, L.ch, 30, 50, { size: 34, align: 'left', color: '#fff', weight: 900 }); text(c, num(1800 + t * 900), 30, 150, { size: 80, align: 'left', color: C.green, weight: 900 }); text(c, L.subs, 30, 215, { size: 30, align: 'left', color: '#aab', weight: 600 }); });
    litHero(ctx, { x: 270, y: 1290, R: 125, view: 'side', dir: 1, expr: 'determined', body: 'bust', arms: 'desk', typing: t * 9 }, { from: [740, 1300, 600, 'rgba(90,255,170,0.3)'] });
    ctx.restore();
    fillRR(ctx, 40, 970, 620, 70, 20, 'rgba(0,0,0,0.7)'); text(ctx, L.me, 60, 1006, { size: 38, align: 'left', color: C.green, weight: 900 });
  } },
  { id: 'g3_channel', draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#0c0a1c'], [1, '#170b26']]); ctx.fillRect(0, 0, W, H);
    ctx.save(); cam(ctx, t, d, 1.0, 1.05);
    circle(ctx, 200, 260, 90, C.pink); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(176, 222); ctx.lineTo(240, 260); ctx.lineTo(176, 298); ctx.fill();
    text(ctx, L.ch, 320, 230, { size: 70, align: 'left', color: '#fff', weight: 900 }); text(ctx, `${num(12400 + t * 2600)} ${L.subs}`, 320, 305, { size: 40, align: 'left', color: '#aab', weight: 600 });
    [['10 CRAZY THINGS IN GTA 6', 'car', 412000], [L.t2, 'night', 96000], [L.t3, 'sun', 41000]].forEach(([ti, k, v], i) => { const y = 430 + i * 230; const kk = pop(t, i * 0.12); ctx.save(); ctx.translate(540, y + 100); ctx.scale(kk, kk); ctx.translate(-540, -(y + 100)); fillRR(ctx, 60, y, 960, 200, 26, 'rgba(255,255,255,0.06)'); viceThumb(ctx, 80, y + 20, 280, 160, k, t); ctx.font = `800 36px ${FONT}`; wrapLines(ctx, ti, 600).slice(0, 2).forEach((l, j) => text(ctx, l, 390, y + 60 + j * 44, { size: 36, align: 'left', color: '#fff', weight: 800 })); text(ctx, `${num(v + t * v * 0.1)} ${L.views}`, 390, y + 160, { size: 32, align: 'left', color: C.green, weight: 700 }); ctx.restore(); });
    const earned = 61.4 + t * 1.2; const p = Math.min(0.99, earned / 69.99);
    fillRR(ctx, 60, 1150, 960, 300, 30, 'rgba(18,16,30,0.95)');
    text(ctx, L.earned, 110, 1220, { size: 36, align: 'left', color: '#99a', weight: 800 }); text(ctx, `$${earned.toFixed(2)}`, 970, 1220, { size: 90, align: 'right', color: C.yellow, weight: 900 });
    text(ctx, `${L.goal} — $69.99`, 110, 1320, { size: 38, align: 'left', color: '#fff', weight: 800 });
    fillRR(ctx, 110, 1360, 860, 44, 22, '#2c2c3c'); fillRR(ctx, 110, 1360, 860 * p, 44, 22, C.yellow);
    ctx.restore();
  } },
  // ===================== ENDING — THE MESSAGE =====================
  { id: 'h1_problem', draw(ctx, t, d) {
    bgDark(ctx, '#080205');
    ctx.save(); cam(ctx, t, d, 1.0, 1.12, 540, 850);
    litHero(ctx, { x: 540, y: 900, R: 270, view: 'front', expr: 'worried', body: 'bust', arms: 'down', blink: t > 0.9 && t < 1.0 }, { tint: '#ff2040', tintA: 0.12, shade: 0.25, from: [540, 1900, 1100, 'rgba(255,40,60,0.35)'] });
    ctx.restore();
    const gl = Math.sin(t * 50) > 0.7 ? 14 : 0;
    text(ctx, L.problem, 540 + gl, 260, { size: 100, color: C.red, weight: 900, glow: C.red, blur: 16, alpha: smooth(seg(t, 0.1, 0.4)) });
    vignette(ctx, 0.8);
  } },
  { id: 'h2_streamer', draw(ctx, t, d) {
    ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#1a0820'], [1, '#05030a']]); ctx.fillRect(0, 0, W, H);
    ctx.save(); cam(ctx, t, d, 1.05, 1.0);
    const k = pop(t, 0.05, 0.4); ctx.save(); ctx.translate(540, 760); ctx.scale(k, k); ctx.translate(-540, -760);
    fillRR(ctx, 70, 300, 940, 900, 40, 'rgba(25,20,40,0.95)'); ctx.save(); ctx.shadowColor = C.yellow; ctx.shadowBlur = 40; ctx.strokeStyle = C.yellow; ctx.lineWidth = 4; rr(ctx, 70, 300, 940, 900, 40); ctx.stroke(); ctx.restore();
    streamerAvatar(ctx, 540, 560, 170, t);
    text(ctx, STREAMER, 520, 830, { size: 84, color: '#fff', weight: 900 }); verified(ctx, 520 + 230, 828, 1.6);
    text(ctx, `${LANG === 'ru' ? '4,8 млн' : '4.8M'} ${L.subs}`, 540, 910, { size: 44, color: '#aab', weight: 600 });
    fillRR(ctx, 130, 980, 820, 160, 26, 'rgba(255,255,255,0.06)'); viceThumb(ctx, 150, 995, 230, 130, 'car', t); ctx.save(); ctx.globalCompositeOperation = 'lighter'; circle(ctx, 265, 1060, 30 + 6 * Math.sin(t * 6), 'rgba(255,60,90,0.6)'); ctx.restore();
    ctx.font = `800 34px ${FONT}`; wrapLines(ctx, L.watchingYou, 520).forEach((l, i) => text(ctx, l, 410, 1040 + i * 44, { size: 34, align: 'left', color: C.yellow, weight: 800 }));
    ctx.restore(); ctx.restore();
    // eye icon
    ctx.save(); ctx.translate(540, 1420); const bl = Math.abs(Math.sin(t * 2)) > 0.97 ? 0.1 : 1; ellipse(ctx, 0, 0, 150, 80 * bl, '#fff'); circle(ctx, 0, 0, 52 * bl, '#111'); circle(ctx, 18, -18, 14 * bl, '#fff'); ctx.restore();
  } },
  { id: 'h3_message', draw(ctx, t, d) {
    bgDark(ctx, '#030308');
    const z = lerp(1.0, 2.2, easeIn(seg(t, d - 1.4, d)));
    ctx.save(); ctx.translate(540, 980); ctx.scale(z, z); ctx.translate(-540, -980);
    roomV(ctx, t); ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 0, W, H); deskV(ctx, 1380);
    crtMonitor(ctx, 110, 700, 860, 600, (c, w, h) => { c.fillStyle = '#0a0612'; c.fillRect(0, 0, w, h);
      const k = pop(t, 0.2, 0.35); c.save(); c.translate(w / 2, h / 2); c.scale(k, k); fillRR(c, -380, -220, 760, 440, 34, '#1d1430'); c.strokeStyle = C.yellow; c.lineWidth = 4; rr(c, -380, -220, 760, 440, 34); c.stroke();
        text(c, L.newMsg, 0, -160, { size: 40, color: C.yellow, weight: 900 }); streamerAvatar(c, -250, -30, 70, t); text(c, STREAMER, -150, -50, { size: 48, align: 'left', color: '#fff', weight: 900 }); verified(c, -150 + 250, -52, 1);
        fillRR(c, -170, 0, 300, 60, 30, '#2c2440'); for (let i = 0; i < 3; i++) circle(c, -120 + i * 40, 30, 10 * (0.6 + 0.4 * Math.abs(Math.sin(t * 5 + i))), '#fff');
        fillRR(c, -300, 110, 600, 80, 40, C.pink); text(c, L.open, 0, 151, { size: 32, color: '#fff', weight: 900 }); c.restore(); });
    glow(ctx, 540, 1000, 800, 'rgba(255,210,63,0.18)');
    litHero(ctx, { x: 540, y: 1430, R: 180, view: 'back', body: 'bust', arms: 'down' }, { shade: 0.5, from: [540, 1000, 700, 'rgba(255,210,100,0.35)'] });
    ctx.restore();
    vignette(ctx, 0.8);
    const fd = smooth(seg(t, d - 0.5, d)); if (fd > 0) { ctx.fillStyle = `rgba(0,0,0,${fd})`; ctx.fillRect(0, 0, W, H); }
  } },
  { id: 'h4_end', draw(ctx, t, d) {
    bgDark(ctx, '#020205');
    ctx.save(); ctx.globalAlpha = 0.2; ctx.drawImage(skylineCanvas('qskyV2', 2600, 500, { seed: 90, minW: 50, maxW: 160, minH: 100, maxH: 460, color: '#140c26', windows: true, lit: 0.3, win: 4 }), -300 - t * 20, H - 500); ctx.restore();
    // last frame of the message stays as a ghost
    ctx.save(); ctx.globalAlpha = 0.25 * (1 - smooth(seg(t, 0, 1))); streamerAvatar(ctx, 540, 360, 120, t); ctx.restore();
    ctx.font = `900 84px ${FONT}`; L.q.forEach((l, i) => { const a = smooth(seg(t, 0.2 + i * 0.25, 0.5 + i * 0.25)); text(ctx, l, 540, 640 + i * 110 - (1 - a) * 20, { size: 84, color: i === 3 ? C.pink : '#fff', weight: 900, alpha: a }); });
    text(ctx, L.tbc, 540, 1250, { size: 60, color: C.yellow, weight: 900, alpha: smooth(seg(t, 1.6, 2.0)) });
    text(ctx, L.ep3, 540, 1340, { size: 44, color: C.cyan, weight: 800, alpha: smooth(seg(t, 2.0, 2.4)) });
    const fo = smooth(seg(t, d - 0.6, d)); if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
  } },
];
// ---------- cover ----------
function drawCover(ctx) {
  ctx.fillStyle = vgrad(ctx, 0, H, [[0, '#2a0a48'], [1, '#0a0614']]); ctx.fillRect(0, 0, W, H);
  cityLayers(ctx, 1, 1350, 300, true, 20);
  const r = rng(4); for (let i = 0; i < 26; i++) glow(ctx, r() * W, 700 + r() * 700, 40 + r() * 140, [C.pink, C.cyan, C.purple, C.orange][i % 4], 0.4);
  // side stream tiles + stats
  ctx.save(); ctx.translate(40, 800); ctx.rotate(-0.06); streamerCam(ctx, 0, 0, 330, 250, 21, 1, { viewers: 1.2e6 }); ctx.restore();
  ctx.save(); ctx.translate(720, 760); ctx.rotate(0.06); fillRR(ctx, 0, 0, 330, 250, 20, 'rgba(10,8,20,0.92)'); text(ctx, '▲ ' + kfmt(100000), 165, 90, { size: 64, color: C.green, weight: 900 }); ctx.strokeStyle = C.green; ctx.lineWidth = 8; ctx.beginPath(); for (let i = 0; i <= 20; i++) { const k = i / 20; ctx.lineTo(30 + k * 270, 220 - Math.pow(k, 3) * 90); } ctx.stroke(); ctx.restore();
  ctx.fillStyle = '#0a0612'; ctx.fillRect(0, 1640, W, 280); fillRR(ctx, -40, 1640, 1160, 300, 10, '#3a281e');
  ctx.save(); ctx.translate(540, 1170); ctx.rotate(-0.03); crtMonitor(ctx, 0, 0, 460, 330, (c, w, h) => viceSunsetScene(c, w, h, 2)); ctx.restore();
  glow(ctx, 770, 1330, 600, 'rgba(255,140,90,0.5)');
  litHero(ctx, { x: 290, y: 1300, R: 225, view: '3q', dir: 1, expr: 'surprised', body: 'bust', arms: 'down', lookX: 1 }, { from: [800, 1350, 900, 'rgba(255,150,100,0.45)'] });
  vignette(ctx, 0.4);
  ctx.save(); ctx.translate(540, 300); ctx.rotate(-0.04);
  text(ctx, L.cover[0], 0, 0, { size: 300, font: FONT_T, weight: 400, color: C.yellow, stroke: '#000', strokeW: 40 });
  text(ctx, L.cover[1], 0, 260, { size: LANG === 'ru' ? 190 : 170, font: FONT_T, weight: 400, color: '#fff', stroke: '#000', strokeW: 32 });
  ctx.restore();
  liveBadge(ctx, 380, 590, 3.3);
}
// durations from per-language timing
for (let i = 0; i < SHOTS.length; i++) { SHOTS[i].start = TM.starts[SHOTS[i].id]; }
for (let i = 0; i < SHOTS.length; i++) { const nx = i + 1 < SHOTS.length ? SHOTS[i + 1].start : TM.total; SHOTS[i].dur = +(nx - SHOTS[i].start + (i + 1 < SHOTS.length ? XF : 0)).toFixed(3); }
function renderShot(id, t) { const s = SHOTS.find(s => s.id === id); const ctx = document.getElementById('c').getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.clearRect(0, 0, W, H); ctx.save(); s.draw(ctx, t, s.dur); ctx.restore(); }
function renderCover() { const ctx = document.getElementById('c').getContext('2d'); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, W, H); ctx.save(); drawCover(ctx); ctx.restore(); }
