// Episode 2 compositor: shots, crossfades, chapter bar (reference style), subtitles.
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const main = cv.getContext('2d');
const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
const bufCtx = buf.getContext('2d');
initNoise();

function drawShot(sh, t, ctx) {
  c = ctx; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.fillStyle = '#000'; c.fillRect(0, 0, W, H);
  CUR = sh; c.save(); sh.draw(t - sh.t0, t); c.restore();
}

function chapterBar(t) {
  c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  if (t > 80.2) return;
  let idx = 0; CHAPTERS.forEach((ch, i) => { if (t >= ch[0]) idx = i; });
  const ch = CHAPTERS[idx];
  const [hh, mm] = ch[2].split(':').map(Number); const m2 = mm + Math.floor((t - ch[0]) / 3);
  const tm = `${String(hh).padStart(2, '0')}:${String(m2 % 60).padStart(2, '0')}`;
  rr(60, 44, 178, 58, 29, 'rgba(232,50,60,.95)'); circ(92, 73, 9, Math.floor(t * 2) % 2 ? '#fff' : 'rgba(255,255,255,.4)');
  txt(tm, 168, 74, 34, '#fff', { w: 800, f: 'DejaVu Sans Mono' });
  const n = CHAPTERS.length, gap = 52, x0 = W / 2 - (n - 1) * gap / 2;
  for (let i = 0; i < n; i++) {
    const on = i <= idx;
    circ(x0 + i * gap, 70, 18, on ? RED : 'rgba(255,255,255,.25)');
    txt(String(i + 1), x0 + i * gap, 71, 20, on ? '#fff' : 'rgba(255,255,255,.7)', { w: 900 });
  }
  txt(ch[1], W / 2, 112, 20, 'rgba(255,255,255,.85)', { w: 800, ls: 3 });
}

function wrap(s, max = 30) {
  if (s.length <= max) return [s];
  const w = s.split(' '); let best = 1, bd = 1e9;
  for (let i = 1; i < w.length; i++) { const a = w.slice(0, i).join(' ').length, b = w.slice(i).join(' ').length; const d = Math.abs(a - b); if (d < bd) { bd = d; best = i; } }
  return [w.slice(0, best).join(' '), w.slice(best).join(' ')];
}
const HL = /2005|2010|2000-Х|WINDOWS|XP|MP3|COUNTER|ИНТЕРНЕТ|КЛУБ/;
function richLine(s, y, size) {
  c.font = `900 ${size}px Inter`; c.letterSpacing = '0px';
  const toks = s.split(' '); const sp = c.measureText(' ').width * 1.6; const ws = toks.map(k => c.measureText(k).width);
  let x = W / 2 - (ws.reduce((a, b) => a + b, 0) + sp * (toks.length - 1)) / 2;
  toks.forEach((k, i) => { txt(k, x, y, size, HL.test(k) ? YEL : '#ffffff', { w: 900, a: 'left', stroke: '#0d1230', sw: 13 }); x += ws[i] + sp; });
}
function subs(t) {
  c = main; c.setTransform(1, 0, 0, 1, 0, 0);
  const s = SUBS.find(x => t >= x[0] && t < x[1]); if (!s) return;
  const p = cl((t - s[0]) / 0.15);
  c.globalAlpha = p * cl((s[1] - t) / 0.1);
  const lines = wrap(s[2].toUpperCase());
  const sc = lerp(0.85, 1, eo(p));
  c.save(); c.translate(W / 2, H - 120); c.scale(sc, sc); c.translate(-W / 2, -(H - 120));
  lines.forEach((l, i) => richLine(l, H - 100 - (lines.length - 1 - i) * 70, 56));
  c.restore(); c.globalAlpha = 1;
}

window.renderFrame = function (t) {
  let i = S.findIndex(s => t >= s.t0 && t < s.t1); if (i < 0) i = S.length - 1;
  const sh = S[i];
  drawShot(sh, t, main);
  const nx = S[i + 1];
  if (nx && t > sh.t1 - nx.fade) {
    drawShot(nx, t, bufCtx);
    c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = eio((t - (sh.t1 - nx.fade)) / nx.fade); c.drawImage(buf, 0, 0); c.globalAlpha = 1;
  }
  chapterBar(t);
  subs(t);
  return true;
};

window.renderCover = function () {
  c = main; c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1;
  const t = 20.0;
  if (VERT) {
    c.save(); c.translate(540, 1150); c.scale(1.75, 1.75); c.translate(-880, -560);
    room05(t, 'day', { screen: scrDesktop, pcOn: true });
    alpha(0.35, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(820, 500, 20, 600, [[0, 'rgba(120,170,255,.6)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
    c.restore();
    c.fillStyle = grad(0, 0, 0, 900, [[0, 'rgba(13,18,48,.96)'], [0.75, 'rgba(13,18,48,.7)'], [1, 'rgba(13,18,48,0)']]); c.fillRect(0, 0, W, 900);
    person({ x: 470, y: 1990, s: 1.45, expr: 'shock', look: [16, 4], sweat: true, hl: [-190, -560], hr: [230, -330] });
    c.fillStyle = rgrad(840, 1420, 10, 330, [[0, 'rgba(255,201,58,.55)'], [1, 'rgba(255,201,58,0)']]); c.fillRect(450, 1000, 800, 900);
    push(840, 1420, 0.18); phone05(0, 0, 0.95, t, 'ring'); pop();
    for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(840, 1420, 250 + i * 40, -0.9, -0.3); c.strokeStyle = YEL; c.lineWidth = 8; c.stroke(); }
    const tl = (s, x, y, size, col) => { txt(s, x + 8, y + 10, size, RED, { w: 900 }); txt(s, x, y, size, col, { w: 900, stroke: '#0d1230', sw: size * 0.13 }); };
    tl('ТЫ ПРОСНУЛСЯ', 540, 260, 118, '#ffffff');
    tl('В 2005', 540, 470, 230, YEL);
    tl('ГОДУ', 540, 690, 230, YEL);
    return true;
  }
  c.save(); c.translate(1080, 640); c.scale(1.55, 1.55); c.translate(-900, -560);
  room05(t, 'day', { screen: scrDesktop, pcOn: true });
  alpha(0.35, () => { c.globalCompositeOperation = 'lighter'; c.fillStyle = rgrad(820, 500, 20, 600, [[0, 'rgba(120,170,255,.6)'], [1, 'rgba(0,0,0,0)']]); c.fillRect(-600, -400, 3200, 2000); });
  c.restore();
  c.fillStyle = grad(0, 0, 0, 560, [[0, 'rgba(13,18,48,.95)'], [0.7, 'rgba(13,18,48,.7)'], [1, 'rgba(13,18,48,0)']]); c.fillRect(0, 0, W, 560);
  person({ x: 760, y: 1240, s: 1.3, expr: 'shock', look: [16, 4], sweat: true, hl: [-190, -540], hr: [230, -330] });
  c.fillStyle = rgrad(1330, 760, 10, 330, [[0, 'rgba(255,201,58,.55)'], [1, 'rgba(255,201,58,0)']]); c.fillRect(900, 350, 900, 800);
  push(1330, 760, 0.18); phone05(0, 0, 0.95, t, 'ring'); pop();
  for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(1330, 760, 250 + i * 40, -0.9, -0.3); c.strokeStyle = YEL; c.lineWidth = 8; c.stroke(); }
  const title = (s, x, y, size, col) => { txt(s, x + 8, y + 10, size, RED, { w: 900 }); txt(s, x, y, size, col, { w: 900, stroke: '#0d1230', sw: size * 0.13 }); };
  title('ТЫ ПРОСНУЛСЯ', 960, 140, 150, '#ffffff');
  title('В 2005 ГОДУ', 960, 320, 190, YEL);
  return true;
};
window.ready = true;
