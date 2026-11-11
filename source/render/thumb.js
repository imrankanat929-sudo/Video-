// Thumbnail 1920x1080: plague doctor silhouette over a foggy medieval city
const L = require('./lib');
const SH = require('./shots');
const fs = require('fs');
const { W, H, glow, rgba, textC } = L;
SH.build(); const A = SH.A;

function doctor(ctx, x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const blk = '#0b0a0b';
  const parts = []; let body = null; const np = () => { body = new L.Path2D(); parts.push(body); };
  np();
  // coat
  body.moveTo(-115, -610); body.quadraticCurveTo(0, -640, 115, -610); body.quadraticCurveTo(170, -300, 230, 0); body.quadraticCurveTo(0, 25, -250, 0); body.quadraticCurveTo(-170, -300, -115, -610); body.closePath();
  // cape
  np();
  body.moveTo(-60, -650); body.quadraticCurveTo(-200, -600, -190, -420); body.quadraticCurveTo(0, -380, 185, -420); body.quadraticCurveTo(200, -600, 60, -650); body.closePath();
  // hood/head
  np();
  body.arc(0, -700, 78, 0, Math.PI * 2); body.closePath();
  // beak
  np();
  body.moveTo(-30, -745); body.quadraticCurveTo(-190, -735, -285, -590); body.quadraticCurveTo(-180, -645, -30, -655); body.closePath();
  // hat brim + crown
  np();
  body.ellipse(0, -772, 200, 34, -0.06, 0, Math.PI * 2); body.closePath();
  np(); body.moveTo(-88, -775); body.lineTo(-80, -905); body.quadraticCurveTo(0, -925, 80, -905); body.lineTo(88, -775); body.closePath();
  // arm + glove holding cane
  np();
  body.moveTo(-100, -560); body.quadraticCurveTo(-190, -470, -170, -330); body.lineTo(-120, -320); body.quadraticCurveTo(-130, -450, -60, -520); body.closePath();
  np(); body.arc(-150, -320, 30, 0, Math.PI * 2); body.closePath();
  // silhouette rendered offscreen, then glowed as one shape
  const sil = L.canvas(W, H), sx = sil.getContext('2d');
  sx.setTransform(ctx.getTransform()); sx.fillStyle = blk; parts.forEach(p => sx.fill(p));
  sx.strokeStyle = blk; sx.lineWidth = 14; sx.lineCap = 'round'; sx.beginPath(); sx.moveTo(-205, 10); sx.lineTo(-140, -470); sx.stroke(); sx.beginPath(); sx.arc(-138, -478, 16, 0, 7); sx.fill();
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.shadowColor = 'rgba(230,120,50,0.9)'; ctx.shadowBlur = 80; ctx.drawImage(sil, 0, 0);
  ctx.shadowColor = 'rgba(255,190,120,0.95)'; ctx.shadowBlur = 12; ctx.drawImage(sil, 0, 0);
  ctx.shadowBlur = 0; ctx.drawImage(sil, 0, 0); ctx.restore();
  // cane
  // subtle details: beak seam, hat band, coat folds
  ctx.strokeStyle = 'rgba(120,90,60,0.35)'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.moveTo(-40, -700); ctx.quadraticCurveTo(-170, -690, -270, -600); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-86, -790); ctx.lineTo(86, -790); ctx.stroke();
  ctx.strokeStyle = 'rgba(90,70,50,0.25)'; [[-40, -400, -70, -10], [40, -400, 70, -10], [110, -380, 170, -10]].forEach(([a, b, c, d]) => { ctx.beginPath(); ctx.moveTo(a, b); ctx.lineTo(c, d); ctx.stroke(); });
  // glass eye glowing
  ctx.save(); ctx.globalCompositeOperation = 'screen'; glow(ctx, -40, -712, 70, '#ff9a40', 0.8); ctx.restore();
  ctx.fillStyle = '#f2b060'; ctx.beginPath(); ctx.arc(-40, -712, 17, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff0c8'; ctx.beginPath(); ctx.arc(-45, -717, 6, 0, 7); ctx.fill();
  ctx.strokeStyle = '#1a1410'; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(-40, -712, 19, 0, 7); ctx.stroke();
  ctx.restore();
}

function thumb(lang) {
  const c = L.canvas(W, H), x = c.getContext('2d');
  L.skyGradient(x, W, H, [[0, '#0e0f13'], [0.45, '#2a1f1c'], [0.7, '#5a2c1e'], [1, '#2a1a16']]);
  // big blood moon / glow behind doctor
  glow(x, 960, 330, 900, '#d0602a', 0.55);
  x.fillStyle = '#e7c3a0'; x.beginPath(); x.arc(960, 330, 175, 0, 7); x.fill();
  x.save(); x.globalCompositeOperation = 'multiply'; glow(x, 920, 300, 175, '#a04020', 0.5); x.restore();
  L.drawWrap(x, A.clouds, 400, -120, 1, 0.75);
  // city layers
  x.save(); x.globalAlpha = 1; x.drawImage(A.dusk.far.c, -400, 180); x.restore();
  x.save(); x.globalCompositeOperation = 'multiply'; const mg = x.createLinearGradient(0, 300, 0, 800); mg.addColorStop(0, 'rgba(120,50,30,0)'); mg.addColorStop(1, 'rgba(120,50,30,0.7)'); x.fillStyle = mg; x.fillRect(0, 300, W, 800); x.restore();
  L.drawWrap(x, A.fogDark, 200, 560, 1, 0.7);
  x.drawImage(A.dusk.mid.c, -500, 300);
  x.save(); x.translate(-500, 300); L.windowLights(x, A.dusk.mid.lights, 1); x.restore();
  L.drawWrap(x, A.fog, 900, 640, 1.1, 0.75);
  // crows
  const r = L.rng(4); x.strokeStyle = '#0c0b0c'; x.lineCap = 'round';
  for (let i = 0; i < 9; i++) { const bx = 250 + r() * 1450, by = 120 + r() * 320, sc = 0.8 + r() * 1.2; if (Math.abs(bx - 960) < 260 && by < 420) continue; x.lineWidth = 5 * sc; x.beginPath(); x.moveTo(bx - 22 * sc, by - 8 * sc); x.quadraticCurveTo(bx - 8 * sc, by - 12 * sc, bx, by); x.quadraticCurveTo(bx + 8 * sc, by - 12 * sc, bx + 22 * sc, by - 6 * sc); x.stroke(); }
  // doctor
  doctor(x, 990, 1240, 1.13);
  // ground fog over feet
  const g = x.createLinearGradient(0, 760, 0, H); g.addColorStop(0, 'rgba(10,8,8,0)'); g.addColorStop(1, 'rgba(10,8,8,0.92)'); x.fillStyle = g; x.fillRect(0, 760, W, 320);
  // vignette
  x.drawImage(A.vig, 0, 0); x.drawImage(A.vig, 0, 0);
  // title
  const title = lang === 'ru' ? 'ЧЁРНАЯ СМЕРТЬ' : 'THE BLACK DEATH';
  const sub = lang === 'ru' ? 'Эпидемия, изменившая мир' : 'The plague that changed the world';
  x.save(); x.font = '230px OswaldBold'; x.letterSpacing = '8px';
  let tw = x.measureText(title).width; const fs_ = tw > 1780 ? Math.floor(230 * 1780 / tw) : 230;
  x.font = `${fs_}px OswaldBold`; x.textAlign = 'center'; x.textBaseline = 'alphabetic';
  x.shadowColor = 'rgba(0,0,0,0.95)'; x.shadowBlur = 40; x.shadowOffsetY = 8;
  x.lineWidth = 14; x.strokeStyle = '#0a0808'; x.strokeText(title, W / 2, 900);
  x.fillStyle = '#f3e8d2'; x.fillText(title, W / 2, 900); x.restore();
  // subtitle band
  x.save(); x.font = '60px PTSerifBold'; const sw = x.measureText(sub).width + 90;
  x.fillStyle = '#8e1f16'; x.fillRect(W / 2 - sw / 2, 940, sw, 92);
  x.fillStyle = 'rgba(0,0,0,0.25)'; x.fillRect(W / 2 - sw / 2, 1024, sw, 8);
  x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillStyle = '#f6ecd8'; x.fillText(sub, W / 2, 987); x.restore();
  return c;
}
const out = process.argv[2];
for (const lang of ['ru', 'en']) {
  const c = thumb(lang);
  fs.writeFileSync(`${out}/thumbnail_${lang}.png`, c.encodeSync('png'));
  fs.writeFileSync(`${out}/thumbnail_${lang}.jpg`, c.encodeSync('jpeg', 92));
}
