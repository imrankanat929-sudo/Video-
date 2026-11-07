// Screen UIs rendered into offscreen canvases (phone 556x1196, monitor 1600x900).
'use strict';

let STR = {};                 // filled from config/strings.<lang>.json
const SCR = {};
function initUI() {
  SCR.phone = makeCanvas(PHONE.sw, PHONE.sh);
  SCR.phone2 = makeCanvas(PHONE.sw, PHONE.sh);
  SCR.mon = makeCanvas(1600, 900);
}
const S = k => STR[k] ?? k;

function statusBar(g, dark = true) {
  text(g, S('clock'), 60, 64, { font: font(600, 26), color: PAL.white });
  g.fillStyle = PAL.white;
  for (let i = 0; i < 4; i++) g.fillRect(410 + i * 9, 56 - i * 5, 6, 8 + i * 5);
  rr(g, 456, 42, 46, 22, 6); g.strokeStyle = PAL.white; g.lineWidth = 2; g.stroke(); g.fillRect(460, 46, 22, 14);
}
function appIcon(g, x, y, r, kind) {
  g.save();
  g.fillStyle = kind === 'msg' ? '#1d2a42' : kind === 'call' ? PAL.red : '#202833';
  rr(g, x - r, y - r, r * 2, r * 2, r * 0.45); g.fill();
  const glyph = kind === 'msg' ? '✉' : kind === 'call' ? '✆' : '₿';
  text(g, glyph, x, y + r * 0.38, { font: font(700, r * 1.1), align: 'center', color: PAL.white });
  g.restore();
}
function wallpaper(g, t) {
  const gr = g.createLinearGradient(0, 0, 0, PHONE.sh);
  gr.addColorStop(0, '#101a2c'); gr.addColorStop(1, '#05070c');
  g.fillStyle = gr; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  g.save(); g.globalAlpha = 0.5;
  g.strokeStyle = 'rgba(120,150,200,0.12)'; g.lineWidth = 2;
  for (let i = 0; i < 6; i++) { g.beginPath(); g.arc(278, 1300, 300 + i * 90 + Math.sin(t * 0.4 + i) * 8, Math.PI, 0); g.stroke(); }
  g.restore();
}
function notifCard(g, y, a, n, scale = 1) {
  if (a <= 0) return;
  g.save();
  g.globalAlpha = a;
  g.translate(0, (1 - ease.out(a)) * -40);
  const h = n.big ? 230 : 150;
  g.fillStyle = 'rgba(30,38,54,0.92)'; rr(g, 26, y, 504, h, 32); g.fill();
  g.strokeStyle = n.red ? rgba(PAL.red, 0.7) : 'rgba(200,215,240,0.12)'; g.lineWidth = 2; g.stroke();
  appIcon(g, 82, y + 56, 28, n.kind);
  text(g, n.app, 128, y + 50, { font: font(600, 22), color: PAL.mist, ls: 1 });
  text(g, n.time || S('now'), 500, y + 50, { font: font(500, 20), color: PAL.grey, align: 'right' });
  text(g, n.title, 128, y + 86, { font: font(700, 27), color: PAL.white });
  g.font = font(500, n.big ? 30 : 24);
  const lines = wrap(g, n.body, 380);
  lines.forEach((l, i) => text(g, l, 128, y + (n.big ? 130 : 120) + i * (n.big ? 40 : 30), { font: font(n.big ? 600 : 500, n.big ? 30 : 24), color: n.big ? PAL.white : '#b9c2d0' }));
  g.restore();
}

// --- lock screen with notifications ---
// s.notifs: [{...card, a}], s.bigClock
function scrLock(t, s = {}) {
  const g = SCR.phone.getContext('2d');
  wallpaper(g, t);
  statusBar(g);
  text(g, S('date'), 278, 190, { font: font(500, 28), align: 'center', color: PAL.mist });
  text(g, S('clock'), 278, 330, { font: font(300, 150), align: 'center', color: PAL.white, ls: -4 });
  let y = 420;
  for (const n of s.notifs || []) { notifCard(g, y, n.a, n); y += (n.big ? 250 : 170) * clamp(n.a * 2); }
  g.fillStyle = 'rgba(220,225,235,0.6)'; rr(g, 188, 1160, 180, 8, 4); g.fill();
  if (s.flash) { g.fillStyle = `rgba(255,255,255,${s.flash * 0.25})`; g.fillRect(0, 0, PHONE.sw, PHONE.sh); }
  return SCR.phone;
}

// --- crypto wallet ---
// s.refresh: 0..1 spinner phase or -1, s.dim 0..1 (greyed), s.hist (show history 0..1), s.pulse
function scrWallet(t, s = {}, cv = SCR.phone) {
  const g = cv.getContext('2d');
  g.fillStyle = '#080b12'; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  text(g, S('wallet_title'), 278, 140, { font: font(700, 30), align: 'center' });
  // refresh spinner
  let off = 0;
  if (s.refresh >= 0 && s.refresh <= 1) {
    off = Math.sin(s.refresh * Math.PI) * 70;
    g.save(); g.globalAlpha = Math.sin(s.refresh * Math.PI);
    g.translate(278, 190 + off * 0.4); g.rotate(s.refresh * 12);
    g.strokeStyle = PAL.mist; g.lineWidth = 5; g.lineCap = 'round';
    g.beginPath(); g.arc(0, 0, 20, 0, 4.5); g.stroke(); g.restore();
  }
  g.save(); g.translate(0, off);
  // balance card
  const cg = g.createLinearGradient(30, 220, 526, 520);
  cg.addColorStop(0, '#18233a'); cg.addColorStop(1, '#0d131f');
  g.fillStyle = cg; rr(g, 30, 220, 496, 330, 36); g.fill();
  g.strokeStyle = 'rgba(180,200,240,0.12)'; g.lineWidth = 2; g.stroke();
  text(g, S('balance'), 70, 290, { font: font(600, 22), color: PAL.mist, ls: 3 });
  const flick = s.flick ? (Math.floor(t * 30) % 2 ? 0.35 : 1) : 1;
  text(g, s.amount || '10.00000000', 70, 390, { font: font(800, 62), color: PAL.white, alpha: flick, ls: -2 });
  text(g, 'BTC', 70, 440, { font: font(700, 30), color: PAL.mist, alpha: flick });
  text(g, s.usd || S('usd'), 70, 505, { font: font(500, 28), color: '#8f9bb0', alpha: flick });
  if (s.pulse) { g.strokeStyle = rgba(PAL.white, s.pulse * 0.6); g.lineWidth = 4; rr(g, 30, 220, 496, 330, 36); g.stroke(); }
  // action buttons
  [[S('send'), 140], [S('receive'), 416]].forEach(([l, x]) => {
    g.fillStyle = '#141b28'; rr(g, x - 110, 580, 220, 80, 24); g.fill();
    text(g, l, x, 630, { font: font(600, 24), align: 'center', color: '#c3cbd8' });
  });
  // history
  const ha = s.hist ?? 1;
  g.globalAlpha = ha;
  text(g, S('history'), 40, 730, { font: font(700, 28) });
  g.fillStyle = '#111724'; rr(g, 30, 760, 496, 150, 26); g.fill();
  if (s.txRed) { g.strokeStyle = rgba(PAL.red, s.txRed); g.lineWidth = 3; rr(g, 30, 760, 496, 150, 26); g.stroke(); }
  g.fillStyle = '#1d2638'; g.beginPath(); g.arc(90, 835, 32, 0, 7); g.fill();
  text(g, '↓', 90, 848, { font: font(700, 34), align: 'center', color: PAL.white });
  text(g, S('received'), 140, 818, { font: font(600, 26) });
  text(g, S('from_addr'), 140, 858, { font: font(500, 20, 'mono'), color: s.txRed ? PAL.red : '#8f9bb0' });
  text(g, '+10.0000', 506, 818, { font: font(700, 24), align: 'right', color: PAL.white });
  text(g, S('tx_time'), 506, 858, { font: font(500, 20), align: 'right', color: '#6f7a8c' });
  text(g, S('no_other_tx'), 278, 980, { font: font(500, 22), align: 'center', color: '#4f596a' });
  g.restore();
  g.globalAlpha = 1;
  if (s.dim) { g.fillStyle = `rgba(8,10,16,${s.dim * 0.7})`; g.fillRect(0, 0, PHONE.sw, PHONE.sh); }
  return cv;
}

// --- news article about the theft ---
function scrNews(t, s = {}) {
  const g = SCR.phone.getContext('2d');
  g.fillStyle = '#0b0e14'; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  g.fillStyle = '#151a24'; rr(g, 30, 96, 496, 56, 28); g.fill();
  text(g, S('news_url'), 278, 133, { font: font(500, 20), align: 'center', color: '#7d889a' });
  const sc = s.scroll || 0;
  g.save(); g.translate(0, -sc);
  g.fillStyle = PAL.red; rr(g, 40, 190, 150, 40, 8); g.fill();
  text(g, S('breaking'), 115, 219, { font: font(800, 20), align: 'center', color: '#fff', ls: 2 });
  g.font = font(800, 44);
  wrap(g, S('news_head'), 470).forEach((l, i) => text(g, l, 40, 300 + i * 54, { font: font(800, 44), color: PAL.white }));
  text(g, S('news_meta'), 40, 520, { font: font(500, 20), color: '#6f7a8c' });
  // schematic image: chain of blocks
  g.fillStyle = '#121826'; rr(g, 40, 550, 476, 260, 20); g.fill();
  for (let i = 0; i < 5; i++) {
    const bx = 70 + i * 90, by = 650 + Math.sin(i * 1.7) * 40;
    if (i) { g.strokeStyle = i === 4 ? PAL.red : '#3b475c'; g.lineWidth = 3; g.beginPath(); g.moveTo(bx - 60, 650 + Math.sin((i - 1) * 1.7) * 40); g.lineTo(bx, by); g.stroke(); }
    g.fillStyle = i === 4 ? PAL.red : '#46536a'; rr(g, bx - 22, by - 22, 44, 44, 8); g.fill();
  }
  g.font = font(500, 24);
  wrap(g, S('news_body'), 476).forEach((l, i) => text(g, l, 40, 860 + i * 36, { font: font(500, 24), color: '#a7b0bf' }));
  for (let i = 0; i < 6; i++) { g.fillStyle = '#1a202c'; rr(g, 40, 1010 + i * 30 + (wrap(g, S('news_body'), 476).length - 3) * 36, 476 - (i % 3) * 60, 14, 7); g.fill(); }
  g.restore();
  if (s.stamp) {
    g.save(); g.globalAlpha = s.stamp; g.translate(278, 420); g.rotate(-0.14); g.scale(1 + (1 - s.stamp) * 0.6, 1 + (1 - s.stamp) * 0.6);
    g.strokeStyle = PAL.red; g.lineWidth = 7; rr(g, -210, -60, 420, 120, 12); g.stroke();
    text(g, S('stolen'), 0, 24, { font: font(900, 64), align: 'center', color: PAL.red, ls: 6 });
    g.restore();
  }
  return SCR.phone;
}

// --- messenger chat ---
// s.msgs: [{text, a, red}], s.typing 0..1, s.title
function avatarEmpty(g, x, y, r) {
  g.fillStyle = '#2a3242'; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill();
  g.fillStyle = '#4a5468';
  g.beginPath(); g.arc(x, y - r * 0.18, r * 0.34, 0, 7); g.fill();
  g.beginPath(); g.ellipse(x, y + r * 0.62, r * 0.6, r * 0.42, 0, Math.PI, 0); g.fill();
}
function scrChat(t, s = {}) {
  const g = SCR.phone.getContext('2d');
  g.fillStyle = '#070a10'; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  g.fillStyle = '#0e131c'; g.fillRect(0, 86, PHONE.sw, 110);
  text(g, '‹', 34, 160, { font: font(400, 60), color: PAL.mist });
  avatarEmpty(g, 110, 141, 34);
  text(g, S('unknown'), 162, 136, { font: font(700, 28) });
  text(g, S('last_seen'), 162, 170, { font: font(500, 20), color: '#6f7a8c' });
  let y = 260;
  text(g, S('chat_today'), 278, y, { font: font(600, 18), align: 'center', color: '#4f596a', ls: 2 });
  y += 40;
  for (const m of s.msgs || []) {
    if (m.a <= 0) continue;
    g.save(); g.globalAlpha = clamp(m.a * 1.5); g.translate(0, (1 - ease.out(clamp(m.a))) * 30);
    g.font = font(500, 30);
    const lines = wrap(g, m.text, 360);
    const bw = Math.max(...lines.map(l => g.measureText(l).width)) + 56, bh = lines.length * 40 + 44;
    g.fillStyle = m.red ? '#3a1418' : '#1a2131'; rr(g, 30, y, bw, bh, 28); g.fill();
    if (m.red) { g.strokeStyle = rgba(PAL.red, 0.6); g.lineWidth = 2; g.stroke(); }
    lines.forEach((l, i) => text(g, l, 58, y + 52 + i * 40, { font: font(500, 30), color: PAL.white }));
    text(g, m.time || S('msg_time'), 30 + bw - 18, y + bh - 12, { font: font(500, 15), color: '#6f7a8c', align: 'right' });
    g.restore();
    y += (bh + 22) * clamp(m.a * 2);
  }
  if (s.typing > 0) {
    g.save(); g.globalAlpha = s.typing;
    g.fillStyle = '#1a2131'; rr(g, 30, y, 120, 60, 30); g.fill();
    for (let i = 0; i < 3; i++) { g.fillStyle = `rgba(200,210,230,${0.3 + 0.5 * (Math.sin(t * 8 - i) * 0.5 + 0.5)})`; g.beginPath(); g.arc(66 + i * 24, y + 30, 7, 0, 7); g.fill(); }
    g.restore();
  }
  // input bar
  g.fillStyle = '#0e131c'; g.fillRect(0, 1090, PHONE.sw, 106);
  g.fillStyle = '#161c28'; rr(g, 30, 1110, 420, 56, 28); g.fill();
  text(g, S('input_ph'), 60, 1146, { font: font(500, 22), color: '#4f596a' });
  return SCR.phone;
}
function scrProfile(t, s = {}) {
  const g = SCR.phone.getContext('2d');
  g.fillStyle = '#070a10'; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  avatarEmpty(g, 278, 330, 120);
  text(g, S('unknown'), 278, 520, { font: font(700, 40), align: 'center' });
  text(g, S('no_name'), 278, 565, { font: font(500, 22), align: 'center', color: '#6f7a8c' });
  const rows = [S('p_phone'), S('p_bio'), S('p_common'), S('p_created')];
  rows.forEach((r, i) => {
    const a = clamp(((s.p ?? 1) * 5) - i);
    g.save(); g.globalAlpha = a;
    g.fillStyle = '#10151f'; rr(g, 40, 630 + i * 110, 476, 90, 22); g.fill();
    const [k, v] = r.split('|');
    text(g, k, 70, 668 + i * 110, { font: font(500, 18), color: '#6f7a8c' });
    text(g, v, 70, 700 + i * 110, { font: font(600, 24), color: '#9aa4b5' });
    g.restore();
  });
  return SCR.phone;
}

// --- emergency call ---
function scrCall(t, s = {}, cv = SCR.phone) {
  const g = cv.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, PHONE.sh);
  gr.addColorStop(0, '#16101a'); gr.addColorStop(1, '#07080d');
  g.fillStyle = gr; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  text(g, S('emergency'), 278, 220, { font: font(600, 26), align: 'center', color: '#e7a0a4', ls: 3 });
  text(g, S('emergency_num'), 278, 380, { font: font(300, 150), align: 'center', color: PAL.white });
  const st = s.calling ? S('calling') + '.'.repeat(1 + Math.floor(t * 2) % 3) : S('call_ready');
  text(g, st, 278, 450, { font: font(500, 28), align: 'center', color: PAL.mist });
  // pulse rings
  if (s.calling) for (let i = 0; i < 3; i++) {
    const p = ((t * 0.6 + i / 3) % 1);
    g.strokeStyle = rgba(PAL.red, (1 - p) * 0.5); g.lineWidth = 3;
    g.beginPath(); g.arc(278, 980, 70 + p * 120, 0, 7); g.stroke();
  }
  const keys = [S('k_mute'), S('k_pad'), S('k_speaker')];
  keys.forEach((k, i) => {
    g.fillStyle = 'rgba(255,255,255,0.07)'; g.beginPath(); g.arc(118 + i * 160, 700, 56, 0, 7); g.fill();
    text(g, k, 118 + i * 160, 800, { font: font(500, 18), align: 'center', color: '#8f9bb0' });
  });
  g.fillStyle = s.calling ? PAL.red : '#2f8f5b';
  g.beginPath(); g.arc(278, 980, 70, 0, 7); g.fill();
  text(g, '✆', 278, 1004, { font: font(700, 64), align: 'center', color: '#fff' });
  return cv;
}

// ---------- monitor screens ----------
function monDesktop(t, s = {}) {
  const g = SCR.mon.getContext('2d');
  g.fillStyle = '#0a1120'; g.fillRect(0, 0, 1600, 900);
  g.fillStyle = '#0f182a'; g.fillRect(0, 0, 1600, 54);
  for (let i = 0; i < 4; i++) { g.fillStyle = i ? '#141e33' : '#1d2a44'; rr(g, 20 + i * 250, 10, 236, 40, 8); g.fill(); }
  // chat window on screen
  g.fillStyle = '#0d1526'; rr(g, 60, 100, 760, 760, 14); g.fill();
  for (let i = 0; i < 9; i++) { g.fillStyle = i % 3 ? '#16223a' : '#1d2b48'; rr(g, 90 + (i % 2) * 220, 140 + i * 76, 420 - (i % 3) * 80, 52, 14); g.fill(); }
  // explorer-like table
  g.fillStyle = '#0d1526'; rr(g, 860, 100, 680, 760, 14); g.fill();
  for (let i = 0; i < 16; i++) { g.fillStyle = i === 7 && s.redRow ? rgba(PAL.red, 0.5) : i % 2 ? '#111b2f' : '#0f182a'; g.fillRect(880, 140 + i * 44, 640, 38); }
  // cursor blink
  if (Math.floor(t * 2) % 2) { g.fillStyle = '#c8d6f0'; g.fillRect(120 + ((t * 30) % 300), 820, 3, 26); }
  return SCR.mon;
}

// transaction graph. s.focus 0..1 (highlight), s.reveal 0..1 (edges drawn)
const GRAPH = (() => {
  const r = mulberry32(31), nodes = [];
  nodes.push({ x: 180, y: 450, lbl: 'EXCHANGE', hot: 1 });
  const cols = [420, 680, 940, 1200];
  cols.forEach((cx, ci) => { const n = ci === 3 ? 3 : 4 + (ci % 2); for (let i = 0; i < n; i++) nodes.push({ x: cx + (r() - 0.5) * 60, y: 140 + (i + 0.5) * (640 / n) + (r() - 0.5) * 40, c: ci + 1 }); });
  nodes.push({ x: 1440, y: 470, lbl: 'YOU', you: 1 });
  const edges = [];
  for (const a of nodes) for (const b of nodes) if (b.c === (a.c || 0) + 1 && r() < 0.55) edges.push([a, b]);
  nodes.filter(n => n.c === 1).forEach(n => edges.push([nodes[0], n]));
  const last = nodes.filter(n => n.c === 4);
  edges.push([last[1], nodes[nodes.length - 1]]);
  // ensure path to "you" chain flagged
  const path = [nodes[0]];
  for (let c = 1; c <= 4; c++) path.push(nodes.filter(n => n.c === c)[c === 4 ? 1 : 1]);
  path.push(nodes[nodes.length - 1]);
  for (let i = 0; i < path.length - 1; i++) edges.push([path[i], path[i + 1], 1]);
  nodes.forEach((n, i) => { n.addr = n.addr || 'bc1q' + Math.floor(r() * 1e8).toString(36) + '…' + Math.floor(r() * 4e4).toString(36); });
  nodes[nodes.length - 1].addr = 'bc1q…7f3k';
  return { nodes, edges, path };
})();
function monGraph(t, s = {}) {
  const g = SCR.mon.getContext('2d');
  g.fillStyle = '#070b14'; g.fillRect(0, 0, 1600, 900);
  g.strokeStyle = 'rgba(80,110,160,0.08)'; g.lineWidth = 1;
  for (let x = 0; x < 1600; x += 40) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 900); g.stroke(); }
  for (let y = 0; y < 900; y += 40) { g.beginPath(); g.moveTo(0, y); g.lineTo(1600, y); g.stroke(); }
  text(g, S('graph_title'), 40, 60, { font: font(700, 26, 'mono'), color: '#7d8fb0', ls: 2 });
  const rev = s.reveal ?? 1, foc = s.focus ?? 0;
  GRAPH.edges.forEach(([a, b, hot], i) => {
    const k = clamp(rev * 1.6 - (a.x / 1600));
    if (k <= 0) return;
    const red = hot && foc > 0;
    g.strokeStyle = red ? rgba(PAL.red, 0.4 + foc * 0.6) : `rgba(110,140,190,${0.25 * (1 - foc * 0.5)})`;
    g.lineWidth = red ? 2 + foc * 3 : 1.5;
    g.beginPath(); g.moveTo(a.x, a.y); g.lineTo(lerp(a.x, b.x, k), lerp(a.y, b.y, k)); g.stroke();
    // moving packets
    if (k >= 1) { const p = (t * 0.5 + i * 0.13) % 1; g.fillStyle = red ? PAL.red : 'rgba(170,200,255,0.6)'; g.beginPath(); g.arc(lerp(a.x, b.x, p), lerp(a.y, b.y, p), red ? 4 : 2.5, 0, 7); g.fill(); }
  });
  GRAPH.nodes.forEach(n => {
    const k = clamp(rev * 1.6 - (n.x / 1600) + 0.1);
    if (k <= 0) return;
    const onPath = GRAPH.path.includes(n);
    g.globalAlpha = k * (foc && !onPath ? 1 - foc * 0.5 : 1);
    const r = n.lbl ? 26 : 14;
    g.fillStyle = (onPath && foc) || n.hot ? PAL.red : '#2c3a52';
    if (n.you) g.fillStyle = foc ? PAL.red : PAL.white;
    g.beginPath(); g.arc(n.x, n.y, r, 0, 7); g.fill();
    if (n.you && foc) { g.strokeStyle = rgba(PAL.red, 0.5 + 0.5 * Math.sin(t * 6)); g.lineWidth = 3; g.beginPath(); g.arc(n.x, n.y, r + 14 + Math.sin(t * 6) * 4, 0, 7); g.stroke(); }
    text(g, n.lbl ? S(n.you ? 'g_you' : 'g_exchange') : n.addr, n.x, n.y + r + 26, { font: font(n.lbl ? 700 : 500, n.lbl ? 20 : 14, 'mono'), align: 'center', color: n.lbl ? PAL.white : '#62708a' });
    if (n.you) text(g, n.addr, n.x, n.y + r + 50, { font: font(500, 16, 'mono'), align: 'center', color: foc ? PAL.red : '#8f9bb0' });
    g.globalAlpha = 1;
  });
  if (foc > 0) {
    g.save(); g.globalAlpha = clamp(foc * 2 - 1);
    g.fillStyle = rgba(PAL.red, 0.15); rr(g, 1180, 640, 380, 110, 12); g.fill();
    g.strokeStyle = PAL.red; g.lineWidth = 2; g.stroke();
    text(g, S('g_match'), 1370, 685, { font: font(800, 24, 'mono'), align: 'center', color: PAL.red, ls: 2 });
    text(g, S('g_match2'), 1370, 722, { font: font(500, 18, 'mono'), align: 'center', color: '#e5a5a9' });
    g.restore();
  }
  return SCR.mon;
}

// transaction verification warning + documents
function monWarning(t, s = {}) {
  const g = SCR.mon.getContext('2d');
  monDesktop(t, { redRow: true });
  g.fillStyle = 'rgba(4,6,10,0.6)'; g.fillRect(0, 0, 1600, 900);
  // documents (schematic)
  const docs = s.docs ?? 1;
  for (let i = 0; i < 3; i++) {
    const a = clamp(docs * 3 - i);
    if (a <= 0) continue;
    g.save(); g.globalAlpha = a; g.translate(140 + i * 90, 160 + i * 50); g.rotate(-0.06 + i * 0.04);
    g.fillStyle = '#c9ced8'; g.fillRect(0, 0, 380, 500);
    g.fillStyle = '#3b4252'; g.fillRect(30, 40, 200, 18);
    for (let l = 0; l < 12; l++) { g.fillStyle = l === 5 ? PAL.red : '#8a909c'; g.fillRect(30, 90 + l * 30, 320 - (l * 37 % 120), 9); }
    g.fillStyle = '#8a909c'; g.fillRect(30, 450, 120, 2);
    g.restore();
  }
  // warning dialog
  const wa = s.warn ?? 1;
  if (wa > 0) {
    g.save(); g.globalAlpha = wa; g.translate(0, (1 - wa) * 30);
    g.fillStyle = '#101624'; rr(g, 720, 220, 760, 460, 18); g.fill();
    g.strokeStyle = PAL.red; g.lineWidth = 3; g.stroke();
    g.fillStyle = PAL.red; rr(g, 720, 220, 760, 70, 18); g.fill(); g.fillRect(720, 260, 760, 30);
    text(g, S('w_title'), 760, 268, { font: font(800, 28), color: '#fff', ls: 2 });
    g.font = font(500, 26);
    wrap(g, S('w_body'), 680).forEach((l, i) => text(g, l, 760, 350 + i * 38, { font: font(500, 26), color: '#c3cbd8' }));
    text(g, S('w_id'), 760, 520, { font: font(500, 20, 'mono'), color: '#7d889a' });
    // progress bar
    g.fillStyle = '#1a2233'; rr(g, 760, 570, 680, 18, 9); g.fill();
    g.fillStyle = PAL.red; rr(g, 760, 570, 680 * clamp(s.prog ?? 0.5), 18, 9); g.fill();
    text(g, S('w_status'), 760, 630, { font: font(600, 20), color: '#e5a5a9' });
    g.restore();
  }
  return SCR.mon;
}

// --- incoming / active / ended call ---
function scrIncoming(t, s = {}) {
  const g = SCR.phone.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, PHONE.sh);
  gr.addColorStop(0, '#121826'); gr.addColorStop(1, '#05070c');
  g.fillStyle = gr; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  const mode = s.mode || 'incoming';
  avatarEmpty(g, 278, 330, 90);
  if (mode === 'incoming') {
    for (let i = 0; i < 3; i++) { const p = (t * 0.7 + i / 3) % 1; g.strokeStyle = `rgba(200,215,240,${(1 - p) * 0.35})`; g.lineWidth = 3; g.beginPath(); g.arc(278, 330, 95 + p * 110, 0, 7); g.stroke(); }
  }
  text(g, s.title ? S(s.title) : S('hidden_num'), 278, 500, { font: font(700, 40), align: 'center' });
  const sub = mode === 'incoming' ? S('incoming') : mode === 'ended' ? S('call_ended') : timer(t - (s.from || t));
  text(g, sub, 278, 550, { font: font(500, 26), align: 'center', color: mode === 'ended' ? '#e5a5a9' : PAL.mist });
  if (mode === 'active') {
    // voice waveform: flat line during silence, moving when the voice speaks
    const amp = s.voice || 0;
    g.strokeStyle = amp > 0.05 ? PAL.white : '#3b475c'; g.lineWidth = 4; g.beginPath();
    for (let x = 0; x <= 400; x += 6) { const y = 690 + Math.sin(x * 0.09 + t * 14) * Math.sin(x * 0.013 + t * 3) * 50 * amp * (0.6 + 0.4 * noise1(x * 0.05 + t * 6)); x ? g.lineTo(78 + x, y) : g.moveTo(78 + x, y); }
    g.stroke();
    [S('k_mute'), S('k_pad'), S('k_speaker')].forEach((k, i) => { g.fillStyle = 'rgba(255,255,255,0.07)'; g.beginPath(); g.arc(118 + i * 160, 830, 56, 0, 7); g.fill(); text(g, k, 118 + i * 160, 925, { font: font(500, 18), align: 'center', color: '#8f9bb0' }); });
    g.fillStyle = PAL.red; g.beginPath(); g.arc(278, 1040, 64, 0, 7); g.fill();
    text(g, '✆', 278, 1062, { font: font(700, 58), align: 'center', color: '#fff' });
  } else if (mode === 'incoming') {
    g.fillStyle = PAL.red; g.beginPath(); g.arc(140, 1010, 64, 0, 7); g.fill();
    text(g, '✆', 140, 1032, { font: font(700, 58), align: 'center', color: '#fff' });
    const bob = Math.sin(t * 7) * 8;
    g.fillStyle = '#2f8f5b'; g.beginPath(); g.arc(416, 1010 + bob, 64, 0, 7); g.fill();
    text(g, '✆', 416, 1032 + bob, { font: font(700, 58), align: 'center', color: '#fff' });
    text(g, S('decline'), 140, 1110, { font: font(500, 20), align: 'center', color: '#8f9bb0' });
    text(g, S('accept'), 416, 1110, { font: font(500, 20), align: 'center', color: '#8f9bb0' });
  }
  return SCR.phone;
}
function timer(sec) { sec = Math.max(0, Math.floor(sec)); return `00:${String(sec).padStart(2, '0')}`; }

function scrSplash(t, s = {}) {
  const g = SCR.phone.getContext('2d');
  g.fillStyle = '#080b12'; g.fillRect(0, 0, PHONE.sw, PHONE.sh);
  statusBar(g);
  appIcon(g, 278, 520, 70, 'btc');
  text(g, S('wallet_title'), 278, 650, { font: font(700, 30), align: 'center' });
  g.save(); g.translate(278, 780); g.rotate(t * 8); g.strokeStyle = PAL.mist; g.lineWidth = 5; g.lineCap = 'round';
  g.beginPath(); g.arc(0, 0, 24, 0, 4.4); g.stroke(); g.restore();
  return SCR.phone;
}

// saved chat screenshots on the monitor
function monDocs(t, s = {}) {
  const g = SCR.mon.getContext('2d');
  monDesktop(t, {});
  g.fillStyle = 'rgba(4,6,10,0.65)'; g.fillRect(0, 0, 1600, 900);
  const lines = [S('m_lucky'), S('m_dont'), S('m_keep2'), S('m_know')];
  for (let i = 0; i < 4; i++) {
    const a = clamp((s.p ?? 1) * 4.5 - i);
    if (a <= 0) continue;
    g.save(); g.globalAlpha = a; g.translate(120 + i * 360, 170 + (i % 2) * 40 + (1 - ease.out(a)) * 40);
    g.fillStyle = '#0b0f17'; rr(g, 0, 0, 320, 560, 22); g.fill();
    g.strokeStyle = 'rgba(200,215,240,0.25)'; g.lineWidth = 2; g.stroke();
    avatarEmpty(g, 46, 46, 22);
    text(g, S('unknown'), 80, 54, { font: font(700, 20) });
    g.font = font(500, 20);
    const ls = wrap(g, lines[i], 230);
    g.fillStyle = i ? '#3a1418' : '#1a2131'; rr(g, 20, 110, 270, ls.length * 30 + 30, 18); g.fill();
    ls.forEach((l, k) => text(g, l, 36, 142 + k * 30, { font: font(500, 20), color: PAL.white }));
    text(g, S('screenshot') + ' ' + (i + 1) + '.png', 160, 530, { font: font(500, 16, 'mono'), align: 'center', color: '#7d889a' });
    g.restore();
  }
  // folder label
  g.fillStyle = '#16203a'; rr(g, 120, 790, 560, 60, 12); g.fill();
  text(g, '▣  ' + S('folder'), 150, 830, { font: font(600, 24, 'mono'), color: '#c3cbd8' });
  return SCR.mon;
}

// --- monitor: new mail with an attached file ---
function monMail(t, s = {}) {
  const g = SCR.mon.getContext('2d');
  monDesktop(t, {});
  g.fillStyle = 'rgba(4,6,10,0.45)'; g.fillRect(0, 0, 1600, 900);
  const a = s.at !== undefined ? clamp((t - s.at) / 0.35) : 1;
  if (a > 0) {
    g.save(); g.globalAlpha = a; g.translate((1 - ease.out(a)) * 300, 0);
    g.fillStyle = '#121a2c'; rr(g, 980, 80, 560, 190, 18); g.fill(); g.strokeStyle = '#3d7bff'; g.lineWidth = 3; g.stroke();
    text(g, '✉  ' + S(s.title || 'Новый файл'), 1010, 135, { font: font(800, 30), color: '#fff' });
    text(g, S(s.from || 'Отправитель: неизвестен'), 1010, 180, { font: font(500, 22), color: '#8f9bb0' });
    g.fillStyle = '#1d2a44'; rr(g, 1010, 200, 500, 50, 10); g.fill();
    text(g, '▤  ' + (s.file || 'transactions_list.xlsx'), 1030, 235, { font: font(600, 22, 'mono'), color: '#c8d6f0' });
    g.restore();
  }
  // opened file preview
  const o = s.openAt !== undefined ? clamp((t - s.openAt) / 0.4) : 0;
  if (o > 0) {
    g.save(); g.globalAlpha = o; g.fillStyle = '#e9edf3'; rr(g, 200, 160, 760, 640, 10); g.fill();
    g.fillStyle = '#2f8f5b'; g.fillRect(200, 160, 760, 50); text(g, s.file || 'transactions_list.xlsx', 220, 195, { font: font(700, 22, 'mono'), color: '#fff' });
    for (let r = 0; r < 12; r++) { g.fillStyle = r % 2 ? '#dfe4ec' : '#eef1f6'; g.fillRect(220, 230 + r * 44, 720, 40); for (let c = 0; c < 4; c++) { g.fillStyle = '#9aa4b2'; g.fillRect(232 + c * 180, 246 + r * 44, 120 - (r * 13 + c * 7) % 50, 8); } }
    g.restore();
  }
  return SCR.mon;
}
// --- monitor: transaction table (spreadsheet) ---
function monTable(t, s = {}) {
  const g = SCR.mon.getContext('2d');
  g.fillStyle = '#eef1f6'; g.fillRect(0, 0, 1600, 900);
  g.fillStyle = '#2f8f5b'; g.fillRect(0, 0, 1600, 60); text(g, s.file || 'transactions_list.xlsx', 30, 40, { font: font(700, 26, 'mono'), color: '#fff' });
  const H = s.head || ['ДАТА', 'ОТКУДА', 'КУДА', 'СУММА'];
  const cols = [40, 300, 760, 1220];
  g.fillStyle = '#d5dbe4'; g.fillRect(0, 60, 1600, 56);
  H.forEach((h, i) => text(g, h, cols[i], 98, { font: font(800, 24), color: '#2a3140', ls: 2 }));
  const r = mulberry32(77), rows = [];
  const addr = () => 'bc1q' + Math.floor(r() * 1e8).toString(36) + '…' + Math.floor(r() * 4e4).toString(36);
  for (let i = 0; i < 11; i++) rows.push([`0${1 + (i % 9)}.11 0${i % 10}:${10 + i * 4}`, addr(), addr(), (r() * 3 + 0.2).toFixed(4) + ' BTC']);
  rows[6] = ['06.11 02:46', addr(), s.you || 'bc1q…9x2m', '10.0000 BTC'];
  rows[8] = ['07.11 08:12', addr(), s.you || 'bc1q…9x2m', '20.0000 BTC'];
  const scroll = s.scroll ? clamp((t - s.scroll[0]) / (s.scroll[1] - s.scroll[0])) * 160 : 0;
  g.save(); g.beginPath(); g.rect(0, 116, 1600, 784); g.clip(); g.translate(0, -ease.inOutSine(clamp(scroll / 160)) * 160);
  rows.forEach((row, i) => {
    const y = 116 + i * 62;
    g.fillStyle = i % 2 ? '#e3e8ef' : '#f4f6f9'; g.fillRect(0, y, 1600, 62);
    const youHi = (i === 6 || i === 8) && s.youAt !== undefined && t > s.youAt;
    if (youHi) { g.fillStyle = 'rgba(255,210,63,0.55)'; g.fillRect(0, y, 1600, 62); }
    row.forEach((c, k) => {
      let col = '#3a4252';
      if (k === 2 && youHi) col = '#111';
      if (k === 3 && i === 8 && s.amountAt !== undefined && t > s.amountAt) col = '#c8323a';
      text(g, c, cols[k], y + 40, { font: font(k === 3 && i === 8 && s.amountAt !== undefined && t > s.amountAt ? 900 : 500, k === 3 && i === 8 && t > (s.amountAt ?? 1e9) ? 30 : 24, 'mono'), color: col });
    });
  });
  // the final line
  const y = 116 + rows.length * 62;
  const la = s.lastAt !== undefined ? clamp((t - s.lastAt) / 0.4) : 0;
  g.fillStyle = la ? `rgba(200,50,58,${0.15 + 0.75 * la})` : '#f4f6f9'; g.fillRect(0, y, 1600, 76);
  text(g, s.last || '→ СЛЕДУЮЩИЙ АДРЕС: АДРЕС СЛЕДОВАТЕЛЯ', 40, y + 50, { font: font(900, 32, 'mono'), color: la ? '#fff' : '#9aa4b2' });
  g.restore();
  return SCR.mon;
}
