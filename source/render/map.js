// Historical parchment map with animated routes
const L = require('./lib');
const { W, H, rgba, mix, rng, glow, clamp, prog, ease, textC } = L;
const topo = require('topojson-client');
const land50 = require('world-atlas/land-50m.json');

const LON0 = -14, LON1 = 84, LAT0 = 20, LAT1 = 64, K = 40, CL = Math.cos(42 * Math.PI / 180);
const MW = (LON1 - LON0) * K * CL, MH = (LAT1 - LAT0) * K;
const proj = (lon, lat) => [(lon - LON0) * K * CL, (LAT1 - lat) * K];

const landPath = new L.Path2D();
(function build() {
  const fc = topo.feature(land50, land50.objects.land);
  const geoms = fc.features ? fc.features.map(f => f.geometry) : [fc.geometry];
  for (const g of geoms) {
    const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
    for (const poly of polys) {
      const outer = poly[0];
      if (!outer.some(([lo, la]) => lo > LON0 - 25 && lo < LON1 + 25 && la > LAT0 - 15 && la < LAT1 + 15)) continue;
      for (const ring of poly) {
        ring.forEach(([lo, la], i) => { const [x, y] = proj(lo, la); i ? landPath.lineTo(x, y) : landPath.moveTo(x, y); });
        landPath.closePath();
      }
    }
  }
})();

const CITIES = {
  issyk: { ll: [77.3, 42.4], ru: 'Иссык-Куль', en: 'Lake Issyk-Kul' },
  samarkand: { ll: [66.97, 39.65], ru: 'Самарканд', en: 'Samarkand' },
  urgench: { ll: [60.6, 42.3], ru: 'Ургенч', en: 'Urgench' },
  sarai: { ll: [47.0, 47.1], ru: 'Сарай', en: 'Sarai' },
  tana: { ll: [39.4, 47.1], ru: 'Тана', en: 'Tana' },
  kaffa: { ll: [35.38, 45.03], ru: 'Каффа', en: 'Kaffa' },
  const: { ll: [28.98, 41.01], ru: 'Константинополь', en: 'Constantinople' },
  messina: { ll: [15.55, 38.19], ru: 'Мессина', en: 'Messina' },
  genoa: { ll: [8.93, 44.41], ru: 'Генуя', en: 'Genoa' },
  venice: { ll: [12.33, 45.44], ru: 'Венеция', en: 'Venice' },
  marseille: { ll: [5.37, 43.3], ru: 'Марсель', en: 'Marseille' },
  alex: { ll: [29.9, 31.2], ru: 'Александрия', en: 'Alexandria' },
  paris: { ll: [2.35, 48.86], ru: 'Париж', en: 'Paris' },
  london: { ll: [-0.13, 51.5], ru: 'Лондон', en: 'London' },
  florence: { ll: [11.25, 43.77], ru: 'Флоренция', en: 'Florence' },
  bergen: { ll: [5.32, 60.39], ru: 'Берген', en: 'Bergen' },
  novgorod: { ll: [31.27, 58.52], ru: 'Новгород', en: 'Novgorod' },
  baghdad: { ll: [44.4, 33.3], ru: 'Багдад', en: 'Baghdad' },
};
const P = k => proj(...CITIES[k].ll);
// trade routes (land caravan then sea)
const ROUTES = [
  { pts: ['issyk', 'samarkand', 'urgench', 'sarai', 'tana', 'kaffa'], t0: 0, t1: 0.55, land: true, via: [null, null, [[55, 46.9]]] },
  { pts: ['kaffa', 'const', 'messina', 'genoa'], t0: 0.5, t1: 0.9, via: [[[31.5, 43.6]], [[23, 37.4], [19, 37.6]], [[12, 40.5], [9.8, 42.8]]] },
  { pts: ['const', 'alex'], t0: 0.62, t1: 0.85, via: [[[26.2, 39.9], [26.6, 36.6]]] },
  { pts: ['messina', 'marseille'], t0: 0.78, t1: 0.98, via: [[[11, 38.4], [7.2, 41.2]]] },
  { pts: ['messina', 'venice'], t0: 0.78, t1: 0.98, via: [[[17.2, 38.5], [19.1, 40.3], [15.6, 43.1]]] },
];
function routePoints(rt) {
  const out = [];
  rt.pts.forEach((k, i) => { out.push(P(k)); if (rt.via && rt.via[i] && i < rt.pts.length - 1) rt.via[i].forEach(ll => out.push(proj(...ll))); });
  // smooth by Catmull-Rom sampling
  const s = []; for (let i = 0; i < out.length - 1; i++) {
    const p0 = out[Math.max(0, i - 1)], p1 = out[i], p2 = out[i + 1], p3 = out[Math.min(out.length - 1, i + 2)];
    for (let j = 0; j < 16; j++) { const t = j / 16, t2 = t * t, t3 = t2 * t;
      s.push([0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
        0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)]); }
  }
  s.push(out[out.length - 1]);
  let len = 0; const cum = [0]; for (let i = 1; i < s.length; i++) { len += Math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1]); cum.push(len); }
  return { s, cum, len };
}
ROUTES.forEach(r => r.geo = routePoints(r));
function partial(ctx, geo, f) {
  const target = geo.len * clamp(f); ctx.beginPath(); ctx.moveTo(...geo.s[0]); let end = geo.s[0];
  for (let i = 1; i < geo.s.length; i++) {
    if (geo.cum[i] <= target) { ctx.lineTo(...geo.s[i]); end = geo.s[i]; }
    else { const a = (target - geo.cum[i - 1]) / (geo.cum[i] - geo.cum[i - 1]); end = [geo.s[i - 1][0] + (geo.s[i][0] - geo.s[i - 1][0]) * a, geo.s[i - 1][1] + (geo.s[i][1] - geo.s[i - 1][1]) * a]; ctx.lineTo(...end); break; }
  }
  return end;
}

// parchment texture (static)
const PAD = 600;
const parch = (() => {
  const c = L.canvas(MW + PAD * 2, MH + PAD * 2), x = c.getContext('2d'), r = rng(42);
  x.fillStyle = '#7d6a4c'; x.fillRect(0, 0, c.width, c.height);
  for (let i = 0; i < 260; i++) { const px = r() * c.width, py = r() * c.height, rr = 40 + r() * 260; const g = x.createRadialGradient(px, py, 0, px, py, rr); const dark = r() < 0.55; g.addColorStop(0, dark ? 'rgba(40,28,14,0.10)' : 'rgba(220,190,140,0.08)'); g.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g; x.fillRect(px - rr, py - rr, rr * 2, rr * 2); }
  for (let i = 0; i < 9000; i++) { x.fillStyle = r() < 0.5 ? 'rgba(30,20,10,0.08)' : 'rgba(230,210,170,0.06)'; x.fillRect(r() * c.width, r() * c.height, 1 + r() * 2, 1 + r() * 2); }
  return c;
})();

// draw map; cam = {x,y,z} map coords of screen center + zoom
function drawMap(ctx, cam, t, o = {}) {
  ctx.save();
  ctx.fillStyle = '#2a2219'; ctx.fillRect(0, 0, W, H);
  ctx.translate(W / 2, H / 2); ctx.scale(cam.z, cam.z); ctx.translate(-cam.x, -cam.y);
  const iz = 1 / cam.z;
  ctx.drawImage(parch, -PAD, -PAD);
  // sea tint
  ctx.fillStyle = 'rgba(40,46,44,0.28)'; ctx.fillRect(-PAD, -PAD, MW + PAD * 2, MH + PAD * 2);
  // graticule
  ctx.strokeStyle = 'rgba(40,28,16,0.18)'; ctx.lineWidth = 1.2 * iz;
  for (let lo = -10; lo <= 80; lo += 10) { ctx.beginPath(); ctx.moveTo(...proj(lo, LAT0 - 10)); ctx.lineTo(...proj(lo, LAT1 + 10)); ctx.stroke(); }
  for (let la = 20; la <= 70; la += 10) { ctx.beginPath(); ctx.moveTo(...proj(LON0 - 20, la)); ctx.lineTo(...proj(LON1 + 20, la)); ctx.stroke(); }
  // coastal hatching (sea side), then land
  ctx.strokeStyle = 'rgba(35,25,14,0.16)'; ctx.lineWidth = 18; ctx.stroke(landPath);
  ctx.strokeStyle = 'rgba(35,25,14,0.12)'; ctx.lineWidth = 34; ctx.stroke(landPath);
  ctx.fillStyle = '#a58d63'; ctx.fill(landPath);
  ctx.save(); ctx.clip(landPath); ctx.globalAlpha = 0.55; ctx.drawImage(parch, -PAD, -PAD); ctx.restore();
  // Issyk-Kul lake (too small for dataset)
  const [ix, iy] = P('issyk'); ctx.fillStyle = '#6a6555'; L.ellipse(ctx, ix, iy, 34, 11, -0.08); ctx.fill(); ctx.strokeStyle = 'rgba(35,25,14,0.7)'; ctx.lineWidth = 2; ctx.stroke();
  // mountains glyphs for Tian Shan / Caucasus / Alps
  const mtn = (lo, la, n) => { const [mx, my] = proj(lo, la); ctx.strokeStyle = 'rgba(45,32,18,0.55)'; ctx.lineWidth = 2.2; for (let i = 0; i < n; i++) { const x = mx + (i - n / 2) * 26 + (i % 2) * 6, y = my + (i % 2) * 14; ctx.beginPath(); ctx.moveTo(x - 14, y + 10); ctx.lineTo(x, y - 12); ctx.lineTo(x + 14, y + 10); ctx.stroke(); } };
  mtn(76, 44.4, 6); mtn(72, 40.6, 5); mtn(44, 42.8, 5); mtn(10, 46.3, 4); mtn(1, 42.7, 3);
  ctx.strokeStyle = 'rgba(30,20,10,0.85)'; ctx.lineWidth = 2.2 * Math.max(0.6, iz); ctx.stroke(landPath);
  // sea labels
  const lang = o.lang || 'ru';
  const seaLab = lang === 'ru' ? [['Чёрное море', 34, 43.2], ['Средиземное море', 18, 34.2], ['Каспийское море', 50.5, 41.5]] : [['Black Sea', 34, 43.2], ['Mediterranean Sea', 18, 34.2], ['Caspian Sea', 50.5, 41.5]];
  ctx.save(); ctx.font = 'italic 26px PTSerifBold'; ctx.fillStyle = 'rgba(50,38,22,0.55)'; ctx.textAlign = 'center'; ctx.letterSpacing = '3px';
  seaLab.forEach(([s, lo, la]) => { const [x, y] = proj(lo, la); ctx.fillText(s, x, y); }); ctx.restore();
  const reg = lang === 'ru' ? [['ЕВРОПА', 14, 52], ['АЗИЯ', 66, 52.5], ['АФРИКА', 18, 26]] : [['EUROPE', 14, 52], ['ASIA', 66, 52.5], ['AFRICA', 18, 26]];
  reg.forEach(([s, lo, la]) => { const [x, y] = proj(lo, la); textC(ctx, s, x, y, '44px PTSerifBold', 'rgba(50,38,22,0.38)', 18); });
  if (o.overlay) o.overlay(ctx, iz);
  ctx.restore();
  // map vignette / candle-light falloff
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H * 1.0); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(10,6,2,0.8)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

function cityDot(ctx, key, iz, lang, a = 1, opts = {}) {
  const [x, y] = P(key); ctx.save(); ctx.globalAlpha = a;
  ctx.fillStyle = opts.red ? '#7a1a12' : '#2b1d10'; ctx.beginPath(); ctx.arc(x, y, 7 * iz * 1.4, 0, 7); ctx.fill();
  ctx.strokeStyle = 'rgba(230,210,170,0.8)'; ctx.lineWidth = 2 * iz; ctx.stroke();
  const fs = (opts.fs || 30) * iz * 1.25; ctx.font = `${fs}px PTSerifBold`; ctx.textAlign = opts.align || 'left'; ctx.textBaseline = 'middle';
  const dx = (opts.dx ?? 16) * iz * 1.4, dy = (opts.dy ?? -18) * iz * 1.4;
  ctx.lineWidth = 6 * iz; ctx.strokeStyle = 'rgba(165,141,99,0.85)'; ctx.strokeText(CITIES[key][lang], x + dx, y + dy);
  ctx.fillStyle = '#24180c'; ctx.fillText(CITIES[key][lang], x + dx, y + dy); ctx.restore();
}

module.exports = { proj, P, MW, MH, landPath, drawMap, ROUTES, partial, cityDot, CITIES };
