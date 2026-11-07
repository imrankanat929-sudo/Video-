// Generic, data-driven shot types for the full episode. A shot in timeline.json:
// { "type": "desk", "start": 10, "end": 14, "cam": [[x,y,z],[x,y,z]], ...params }
// All times inside params are absolute video seconds.
'use strict';

const V = (sh, k, d) => (sh[k] !== undefined ? sh[k] : d);

// ---------- camera ----------
function camOf(sh, T) {
  const c = sh.cam || [[960, 540, 1], [960, 540, 1.08]];
  let cam;
  if (c.length && c[0].length === 4) {                       // keyframes [t,x,y,z]
    let i = 0; while (i < c.length - 2 && T > c[i + 1][0]) i++;
    const a = c[i], b = c[Math.min(i + 1, c.length - 1)];
    const k = b[0] > a[0] ? ease.inOutSine(clamp((T - a[0]) / (b[0] - a[0]))) : 1;
    cam = { x: lerp(a[1], b[1], k), y: lerp(a[2], b[2], k), z: lerp(a[3], b[3], k) };
  } else {
    const k = ease.inOutSine(clamp((T - sh.start) / (sh.end - sh.start)));
    cam = { x: lerp(c[0][0], c[1][0], k), y: lerp(c[0][1], c[1][1], k), z: lerp(c[0][2], c[1][2], k) };
  }
  if (sh.snap) {                                               // sharp zoom
    const k = ease.outExpo(ramp(T, sh.snap.at, sh.snap.at + (sh.snap.dur || 0.28)));
    cam = { x: lerp(cam.x, sh.snap.to[0], k), y: lerp(cam.y, sh.snap.to[1], k), z: lerp(cam.z, sh.snap.to[2], k) };
    if (T > sh.snap.at) { const s = shake(T, 7 * (1 - ramp(T, sh.snap.at, sh.snap.at + 0.8)), 25, 3); cam.x += s.x; cam.y += s.y; cam.r = s.r; }
  }
  if (sh.shake) { const s = shake(T, sh.shake, 1.6, 11); cam.x += s.x; cam.y += s.y; cam.r = (cam.r || 0) + s.r; }
  if (sh.jolt) {                                               // short camera jolt (answering a call etc.)
    for (const j of [].concat(sh.jolt)) if (T > j && T < j + 0.6) { const s = shake(T, 10 * (1 - (T - j) / 0.6), 30, 5); cam.x += s.x; cam.y += s.y; }
  }
  return cam;
}
const pulseAt = (T, list, len = 1.0) => [].concat(list || []).some(t => T > t && T < t + len);

// ---------- phone screens ----------
function stateAt(list, T) {
  let cur = list[0];
  for (const s of list) if (T >= (s.from ?? -1)) cur = s;
  return cur;
}
function phoneScreen(spec, T, cv) {
  const s = Array.isArray(spec) ? stateAt(spec, T) : spec;
  cv = cv || SCR.phone;
  let out;
  switch (s.kind) {
    case 'wallet': {
      const r = [].concat(s.refresh || []).find(t => T >= t && T <= t + 0.7);
      const flick = [].concat(s.refresh || []).some(t => T > t + 0.6 && T < t + 0.8);
      const amount = s.count !== undefined ? (10 * so(T, s.count, s.count + 0.9)).toFixed(8) : undefined;
      out = scrWallet(T, { refresh: r !== undefined ? ramp(T, r, r + 0.7) : -1, flick, amount, txRed: s.txRed !== undefined ? so(T, s.txRed, s.txRed + 0.4) : 0, dim: s.dimAt !== undefined ? so(T, s.dimAt, s.dimAt + 0.6) : 0, pulse: s.pulse ? 0.4 + 0.3 * Math.sin(T * 3) : 0 }, cv);
      break;
    }
    case 'lock': out = scrLock(T, { notifs: (s.notifs || []).map(n => ({ ...n, app: S(n.app), title: S(n.title), body: S(n.body), a: so(T, n.at, n.at + 0.35) })), flash: s.flash !== undefined ? 1 - so(T, s.flash, s.flash + 0.5) : 0 }); break;
    case 'chat': {
      out = scrChat(T, { msgs: (s.msgs || []).map(m => ({ text: S(m.key), a: so(T, m.at, m.at + 0.3), red: m.red })), typing: s.typing && T > s.typing[0] && T < s.typing[1] ? 1 : 0 });
      if (s.missed) { const a = so(T, s.missed[0], s.missed[0] + 0.35) * (1 - sm(T, s.missed[1], s.missed[1] + 0.4)); if (a > 0) notifCard(out.getContext('2d'), 100, a, { kind: 'call', app: S('missed'), title: S('hidden_num'), body: '02:49', red: true }); }
      break;
    }
    case 'profile': out = scrProfile(T, { p: ramp(T, s.from, s.from + 0.6) }); break;
    case 'news': out = scrNews(T, { stamp: s.stolen !== undefined ? so(T, s.stolen + 0.05, s.stolen + 0.3) : 0, scroll: s.scroll ? sm(T, s.scroll[0], s.scroll[1]) * (s.scrollBy || 200) : 0 }); break;
    case 'call': out = scrCall(T, { calling: s.calling !== undefined && T > s.calling }, cv); break;
    case 'incoming': out = scrIncoming(T, { mode: 'incoming', title: s.title }); break;
    case 'active': out = scrIncoming(T, { mode: 'active', title: s.title, from: s.since, voice: (s.voice || []).some(([a, b]) => T > a && T < b) ? 0.6 + 0.4 * Math.abs(noise1(T * 9)) : 0 }); break;
    case 'ended': out = scrIncoming(T, { mode: 'ended', title: s.title }); break;
    case 'splash': out = scrSplash(T); break;
    default: { const g = cv.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, PHONE.sw, PHONE.sh); out = cv; }
  }
  // quick brightness blink when the state changes
  if (Array.isArray(spec)) {
    const cur = stateAt(spec, T);
    if (cur.from !== undefined && T - cur.from < 0.18) { const g = out.getContext('2d'); g.fillStyle = `rgba(0,0,0,${0.8 * (1 - (T - cur.from) / 0.18)})`; g.fillRect(0, 0, PHONE.sw, PHONE.sh); }
  }
  return out;
}
function monScreen(m, T) {
  m = m || { kind: 'desktop' };
  switch (m.kind) {
    case 'graph': return monGraph(T, { reveal: m.reveal ? so(T, m.reveal[0], m.reveal[1]) : 1, focus: m.focus !== undefined ? so(T, m.focus, m.focus + 0.4) : 0 });
    case 'warning': return monWarning(T, { docs: m.docs !== undefined ? so(T, m.docs, m.docs + 1.2) : 1, warn: m.warn !== undefined ? so(T, m.warn, m.warn + 0.4) : 1, prog: m.prog ? ramp(T, m.prog[0], m.prog[1]) * 0.8 : 0.8 });
    case 'docs': return monDocs(T, { p: m.from !== undefined ? ramp(T, m.from, m.from + 2.4) : 1 });
    case 'mail': return monMail(T, m);
    case 'table': return monTable(T, m);
    default: return monDesktop(T, { redRow: m.redRow !== undefined && T > m.redRow });
  }
}
const onLevel = (sh, T) => {
  let on = sh.onAt !== undefined ? so(T, sh.onAt, sh.onAt + 0.25) : V(sh, 'on', 1);
  if (sh.offAt !== undefined) on *= 1 - sm(T, sh.offAt, sh.offAt + 0.5);
  return on;
};

// ---------- extra art ----------
function morningWash(ctx, x, y, w, h, a = 1) {
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = a;
  const g = ctx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, 'rgba(120,135,160,0.55)'); g.addColorStop(1, 'rgba(150,150,160,0.35)');
  ctx.fillStyle = g; ctx.fillRect(x, y, w, h); ctx.restore();
}
function lineReveal(ctx, path, p, color, width = 4) {
  ctx.save();
  ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.setLineDash([3000, 3000]); ctx.lineDashOffset = 3000 * (1 - p);
  ctx.stroke(path); ctx.restore();
}
const CAR = (() => { const p = new Path2D(); p.moveTo(-230, 40); p.lineTo(-230, 0); p.quadraticCurveTo(-220, -30, -170, -36); p.lineTo(-100, -44); p.quadraticCurveTo(-60, -100, 10, -104); p.lineTo(90, -100); p.quadraticCurveTo(140, -96, 180, -40); p.lineTo(220, -30); p.quadraticCurveTo(240, -20, 236, 40); p.closePath(); p.moveTo(-150, 40); p.arc(-150, 40, 38, 0, 7); p.moveTo(170, 40); p.arc(150, 40, 38, 0, 7); p.moveTo(-80, -44); p.lineTo(150, -44); return p; })();
const HOUSE = (() => { const p = new Path2D(); p.rect(-120, -220, 240, 300); p.moveTo(-170, 80); p.lineTo(170, 80); for (let r = 0; r < 5; r++) for (let c = 0; c < 3; c++) p.rect(-90 + c * 66, -190 + r * 52, 46, 32); return p; })();
const KEYS = (() => { const p = new Path2D(); p.arc(-60, -20, 60, 0, 7); p.moveTo(0, -20); p.lineTo(170, -20); p.lineTo(170, 20); p.moveTo(130, -20); p.lineTo(130, 10); return p; })();

// ---------- shot types ----------
const GEN = {
  room(ctx, T, sh) {
    const cam = camOf(sh, T);
    const vib = pulseAt(T, sh.vibAt, 1.0);
    let on = sh.phoneOnAt !== undefined ? so(T, sh.phoneOnAt, sh.phoneOnAt + 0.3) : V(sh, 'phoneOn', 0.5);
    if (sh.phoneOffAt !== undefined) on *= 1 - sm(T, sh.phoneOffAt, sh.phoneOffAt + 0.5);
    const j = vib ? shake(T, 3, 70, 1) : { x: 0, y: 0 };
    const red = sh.red !== undefined ? (sh.red === true ? 1 : so(T, sh.red, sh.red + 0.6)) : 0;
    roomWide(ctx, T, cam, {
      monitor: monScreen(sh.monitor, T), monTint: red ? `rgba(200,70,80,${0.35 * red})` : undefined, monLight: V(sh, 'monLight', 0.8),
      rimCol: red ? 'rgba(210,120,130,0.8)' : undefined,
      phoneOn: on * (vib ? 0.85 + 0.15 * Math.sin(T * 60) : 1), phoneX: 800 + j.x, phoneY: 716 + j.y,
      tilt: sh.tiltAt !== undefined ? V(sh, 'tilt', -0.08) * so(T, sh.tiltAt, sh.tiltAt + 0.8) : V(sh, 'tilt', 0),
      morning: sh.morning,
    });
    if (sh.title) {   // series title
      const ta = sm(T, sh.start + 0.6, sh.start + 1.4) * (1 - sm(T, sh.start + 3.4, sh.start + 4.2));
      text(ctx, S('series'), 90, 120, { font: font(900, 46), color: PAL.white, alpha: ta, ls: 8 });
      text(ctx, S('episode'), 92, 160, { font: font(600, 20), color: PAL.red, alpha: ta, ls: 6 });
    }
    if (sh.darkAt !== undefined) { ctx.fillStyle = `rgba(0,0,0,${sm(T, sh.darkAt, sh.darkAt + 0.35) * 0.92})`; ctx.fillRect(0, 0, W, H); }
    if (sh.caption) { const a = so(T, sh.caption.at, sh.caption.at + 0.4); text(ctx, S(sh.caption.key), W / 2, H / 2 + 30, { font: font(900, 84), align: 'center', color: PAL.red, alpha: a, ls: 6 + (1 - a) * 20 }); }
    if (sh.dim) { ctx.fillStyle = `rgba(0,0,0,${sh.dim})`; ctx.fillRect(0, 0, W, H); }
  },

  desk(ctx, T, sh) {
    const p = sh.phone || {};
    deskPhone(ctx, T, camOf(sh, T), phoneScreen(sh.screen, T), { px: p.px, py: p.py, s: p.s, rot: p.rot, on: onLevel(sh, T), vib: pulseAt(T, sh.vibAt, 1.0) ? 2.5 : 0, dark: V(sh, 'dark', 0.6), tint: sh.tint, spill: sh.spill });
    if (sh.dim) { ctx.fillStyle = `rgba(0,0,0,${sh.dim})`; ctx.fillRect(0, 0, W, H); }
  },

  held(ctx, T, sh) {
    const on = onLevel(sh, T);
    heldPhone(ctx, T, camOf(sh, T), phoneScreen(sh.screen, T), { shake: V(sh, 'hand', 3.5), on, fg: sh.fg });
    if (sh.redFlash !== undefined && T > sh.redFlash) { ctx.fillStyle = rgba(PAL.red, 0.18 * (1 - ramp(T, sh.redFlash, sh.redFlash + 0.6))); ctx.fillRect(0, 0, W, H); }
    if (sh.fadeOut) { ctx.fillStyle = `rgba(0,0,0,${sm(T, sh.fadeOut[0], sh.fadeOut[1]) * 0.85})`; ctx.fillRect(0, 0, W, H); }
  },

  monitor(ctx, T, sh) {
    const red = sh.redAt !== undefined ? so(T, sh.redAt, sh.redAt + 0.5) : 0;
    monitorClose(ctx, T, camOf(sh, T), monScreen(sh.monitor, T), { fg: V(sh, 'fg', true), tint: red ? `rgba(${110 + red * 90},${140 - red * 80},${210 - red * 140},0.4)` : undefined });
    ctx.fillStyle = `rgba(0,0,0,${0.06 * (noise1(T * 20) * 0.5 + 0.5)})`; ctx.fillRect(0, 0, W, H);
  },

  side(ctx, T, sh) {
    const cam = camOf(sh, T);
    const vib = pulseAt(T, sh.vibAt, 1.4);
    const v0 = [].concat(sh.vibAt || [sh.start])[0];
    const on = (sh.phoneOnAt !== undefined ? so(T, sh.phoneOnAt, sh.phoneOnAt + 0.2) : so(T, v0, v0 + 0.2)) * (vib ? 0.8 + 0.2 * Math.sin(T * 50) : 1);
    withCam(ctx, cam, 0.7, () => {
      ctx.drawImage(ART.wall, -240, -160);
      drawWindow(ctx, T, 160, 120, 700, 560, {});
      if (sh.morning) morningWash(ctx, 160, 120, 700, 560);
      ctx.fillStyle = `rgba(0,0,0,${sh.morning ? 0.1 : 0.25})`; ctx.fillRect(-300, -300, 2600, 1700);
    });
    const jx = vib ? shake(T, 3, 80, 5).x : 0;
    withCam(ctx, cam, 1, () => {
      ctx.fillStyle = '#0b0e15'; ctx.fillRect(-200, 740, 2400, 26);
      ctx.fillStyle = 'rgba(150,175,220,0.12)'; ctx.fillRect(-200, 740, 2400, 2);
      ctx.fillStyle = '#05060a'; rr(ctx, 1180 + jx, 728, 170, 14, 5); ctx.fill();
      ctx.fillStyle = `rgba(190,210,255,${on})`; ctx.fillRect(1186 + jx, 726, 158, 3);
      glow(ctx, 1265 + jx, 700, 520, 'rgba(150,180,255,0.6)', on);
      drawHeroSide(ctx, T, 760, 420 + so(T, v0 + 0.3, v0 + 1.5) * 18, 1.25, { rimCol: `rgba(150,180,240,${0.25 + on * 0.7})`, rimX: 6 * (0.3 + on), rimY: 3 });
      ctx.fillStyle = '#05060a'; ctx.fillRect(-200, 766, 2400, 600);
      dust(ctx, T, 1200, 600, 400, on * 0.8, 10);
    });
  },

  window(ctx, T, sh) {
    const cam = camOf(sh, T);
    withCam(ctx, cam, 0.6, () => {
      ctx.fillStyle = '#06080d'; ctx.fillRect(-400, -400, 2800, 1900);
      drawWindow(ctx, T, 260, 40, 1400, 1000, { fog: 1.3 });
      if (sh.morning) morningWash(ctx, 260, 40, 1400, 1000, 0.9);
      if (sh.bright) glow(ctx, 960, 900, 900, 'rgba(200,190,170,0.35)', so(T, sh.start, sh.end));
      if (sh.red) glow(ctx, 960, 540, 1100, 'rgba(200,50,58,0.4)', sh.red === true ? 0.8 : so(T, sh.red, sh.red + 1));
    });
    const ph = sh.phoneAt !== undefined ? so(T, sh.phoneAt, sh.phoneAt + 0.4) : V(sh, 'phone', 0.9);
    withCam(ctx, cam, 1, () => drawHeroSide(ctx, T, 900, 470, 1.55, { phone: ph > 0, phoneLight: ph, rimCol: `rgba(170,200,250,${0.35 + 0.6 * ph})`, rimX: 7, rimY: 4, lean: V(sh, 'lean', 0.1) }));
    withCam(ctx, cam, 1.3, () => ctx.drawImage(SPR.cable, -600, 900));
  },

  dream(ctx, T, sh) {
    const cam = camOf(sh, T);
    withCam(ctx, cam, 0.6, () => { ctx.fillStyle = '#070a11'; ctx.fillRect(-400, -400, 2800, 1900); ctx.drawImage(ART.city, -300, 380, 2600, 900); ctx.fillStyle = 'rgba(5,7,12,0.55)'; ctx.fillRect(-400, -400, 2800, 1900); });
    const items = [[CAR, 'dream_car', sh.carAt, 420], [HOUSE, 'dream_home', sh.homeAt, 960], [KEYS, 'dream_free', sh.freeAt, 1500]];
    withCam(ctx, cam, 1, () => {
      for (const [path, key, at, x] of items) {
        const p = so(T, at, at + 1.1);
        if (p <= 0) continue;
        ctx.save(); ctx.translate(x, 500); ctx.scale(1.2, 1.2);
        glow(ctx, 0, -40, 260, 'rgba(180,200,240,0.25)', p);
        lineReveal(ctx, path, p, 'rgba(217,221,228,0.9)', 4);
        ctx.restore();
        text(ctx, S(key), x, 760, { font: font(900, 52), align: 'center', color: PAL.white, alpha: so(T, at + 0.3, at + 0.8), ls: 6 });
      }
      dust(ctx, T, 960, 540, 900, 0.9, 30);
    });
  },

  title(ctx, T, sh) {
    const a = so(T, sh.at ?? sh.start, (sh.at ?? sh.start) + 0.4);
    const k = ramp(T, sh.start, sh.end);
    if (sh.style === 'countdown') {
      ctx.fillStyle = '#050608'; ctx.fillRect(0, 0, W, H);
      glow(ctx, W / 2, H / 2, 900, 'rgba(200,50,58,0.35)', 0.8);
      const left = 24 * 3600 - Math.max(0, Math.floor((T - sh.start - 0.5) * 3));   // ticking seconds
      const hh = String(Math.floor(left / 3600)).padStart(2, '0'), mm = String(Math.floor(left / 60) % 60).padStart(2, '0'), ss = String(left % 60).padStart(2, '0');
      const str = `${hh}:${mm}:${ss}`;
      const gl = T - sh.start < 0.25 ? 18 : (mulberry32(Math.floor(T * 30))() < 0.06 ? 8 : 0);
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      text(ctx, str, W / 2 - gl, 600, { font: font(800, 230, 'mono'), align: 'center', color: 'rgba(200,50,58,0.8)' });
      text(ctx, str, W / 2 + gl, 600, { font: font(800, 230, 'mono'), align: 'center', color: 'rgba(80,110,200,0.35)' });
      ctx.restore();
      text(ctx, S(sh.sub || 'h24_sub'), W / 2, 760, { font: font(800, 40), align: 'center', color: PAL.white, ls: 14, alpha: so(T, sh.start + 0.3, sh.start + 0.8) });
    } else {   // rewind
      withCam(ctx, { x: 960, y: 540, z: lerp(1.0, 1.06, k) }, 0.6, () => drawRoomBack(ctx, T - (T - sh.start) * 6, {}));
      ctx.fillStyle = 'rgba(3,4,8,0.72)'; ctx.fillRect(0, 0, W, H);
      const r = mulberry32(Math.floor(T * 30));
      for (let i = 0; i < 7; i++) { ctx.fillStyle = `rgba(200,210,230,${0.04 + r() * 0.08})`; ctx.fillRect(0, r() * H, W, 2 + r() * 10); }
      text(ctx, '◀◀', 120, 140, { font: font(800, 40, 'mono'), color: PAL.white, alpha: Math.floor(T * 3) % 2 ? 0.8 : 0.3 });
      const off = (1 - a) * 18;
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      text(ctx, S(sh.text), W / 2 - off, 560, { font: font(900, 96), align: 'center', color: 'rgba(200,50,58,0.7)', ls: 6, alpha: a });
      text(ctx, S(sh.text), W / 2 + off, 560, { font: font(900, 96), align: 'center', color: 'rgba(120,150,220,0.6)', ls: 6, alpha: a });
      ctx.restore();
      text(ctx, S(sh.text), W / 2, 560, { font: font(900, 96), align: 'center', color: PAL.white, ls: 6, alpha: a * 0.9 });
    }
  },

  option(ctx, T, sh) {
    const A = sh.side === 'A';
    const cam = camOf(sh, T);
    if (A) {
      deskPhone(ctx, T, cam, phoneScreen({ kind: 'wallet', pulse: 1 }, T), { px: 560, py: 560, s: 0.72, rot: -0.1, on: 1, dark: 0.7 });
      ctx.fillStyle = 'rgba(3,4,8,0.45)'; ctx.fillRect(960, 0, 960, H);
    } else {
      deskPhone(ctx, T, cam, phoneScreen({ kind: 'call', calling: sh.callingAt }, T), { px: 1380, py: 560, s: 0.72, rot: 0.08, on: 1, dark: 0.7, tint: 'rgba(255,140,150,0.45)' });
      ctx.fillStyle = 'rgba(3,4,8,0.45)'; ctx.fillRect(0, 0, 960, H);
      if (T > sh.callingAt) { const ph = Math.floor(T * 3) % 2; glow(ctx, ph ? 0 : W, H / 2, 900, ph ? 'rgba(200,50,58,0.5)' : 'rgba(70,100,200,0.45)', 0.35 * so(T, sh.callingAt, sh.callingAt + 0.5)); }
    }
    const lines = S(A ? 'optA' : 'optB').split(' ').reduce((a, w) => { if (a.length && (a[a.length - 1] + ' ' + w).length <= 12) a[a.length - 1] += ' ' + w; else a.push(w); return a; }, []);
    optionText(ctx, T, sh.at, S(A ? 'optA_label' : 'optB_label'), '', A ? 1000 : 120, 500, 'left', { lines, size: 92 });
    if (A && sh.millionAt !== undefined && T > sh.millionAt - 0.2) {
      const p = so(T, sh.millionAt - 0.2, sh.millionAt + 0.9);
      const s = '$' + String(Math.floor(lerp(0, 1000000, p))).replace(/\B(?=(\d{3})+(?!\d))/g, STR.thousands || ' ') + (p >= 1 ? '+' : '');
      text(ctx, s, 1004, 860, { font: font(800, 72), color: PAL.white, alpha: clamp(p * 3), shadow: 'rgba(200,215,255,0.35)', blur: 30 });
    }
    if (!A && sh.strikeAt !== undefined && T > sh.strikeAt - 0.3) {
      const a = so(T, sh.strikeAt - 0.3, sh.strikeAt + 0.2), st = so(T, sh.strikeAt + 0.3, sh.strikeAt + 1.0);
      text(ctx, '10 BTC  ≈ $1 000 000', 124, 860, { font: font(700, 48, 'mono'), color: PAL.mist, alpha: a * (1 - st * 0.5) });
      ctx.fillStyle = PAL.red; ctx.fillRect(118, 842, 640 * st, 5);
    }
  },

  split(ctx, T, sh) {
    const k = ramp(T, sh.start, sh.end);
    const wl = sh.walletAt !== undefined ? so(T, sh.walletAt, sh.walletAt + 0.4) : 1;
    const er = sh.emergencyAt !== undefined ? so(T, sh.emergencyAt, sh.emergencyAt + 0.4) : 1;
    const both = sh.walletAt === undefined;
    const open = sm(T, sh.start, sh.start + 0.65);
    [0, 1].forEach(side => {
      ctx.save(); ctx.beginPath(); side ? ctx.rect(W / 2 + 3, 0, W / 2, H) : ctx.rect(0, 0, W / 2 - 3, H); ctx.clip();
      ctx.translate(side ? W / 4 : -W / 4, 0);
      const cam = { x: side ? lerp(1450, 1430, k) : lerp(470, 490, k), y: 540, z: lerp(1.0, 1.08, k) * (2 - open) };
      const scr = side ? scrCall(T, { calling: sh.emergencyAt !== undefined && T > sh.emergencyAt }, SCR.phone2) : phoneScreen({ kind: 'wallet' }, T);
      deskPhone(ctx, T, cam, scr, { px: side ? 1440 : 480, py: 560, s: 0.68, rot: side ? 0.05 : -0.05, on: 1, dark: 0.7, tint: side ? 'rgba(255,140,150,0.45)' : undefined });
      const dim = both ? 0 : side ? wl * (1 - er) * 0.6 : er * 0.6;
      ctx.fillStyle = `rgba(0,0,0,${dim})`; ctx.fillRect(-W, 0, 3 * W, H);
      ctx.restore();
    });
    ctx.fillStyle = PAL.white; ctx.globalAlpha = 0.8; const lh = H * open; ctx.fillRect(W / 2 - 2, H / 2 - lh / 2, 4, lh); ctx.globalAlpha = 1;
    text(ctx, S('split_left'), W / 4, 1010, { font: font(800, 34), align: 'center', color: PAL.white, ls: 8, alpha: both ? 0.9 : 0.35 + wl * 0.65 * (1 - er * 0.5) });
    text(ctx, S('split_right'), W * 3 / 4, 1010, { font: font(800, 34), align: 'center', color: er && !both ? PAL.red : PAL.white, ls: 8, alpha: both ? 0.9 : 0.35 + er * 0.65 });
  },

  final(ctx, T, sh) {
    const Tb = Math.min(T, sh.freeze);
    const z = lerp(1.0, 1.06, ease.inOutSine(ramp(Tb, sh.start, sh.freeze)));
    [0, 1].forEach(side => {
      ctx.save(); ctx.beginPath(); side ? ctx.rect(W / 2 + 3, 0, W / 2, H) : ctx.rect(0, 0, W / 2 - 3, H); ctx.clip();
      ctx.translate(side ? W / 4 : -W / 4, 0);
      const scr = side ? scrCall(Tb, { calling: false }, SCR.phone2) : scrWallet(Tb, { refresh: -1 });
      deskPhone(ctx, Tb, { x: side ? 1440 : 480, y: 560, z }, scr, { px: side ? 1440 : 480, py: 560, s: 0.68, rot: side ? 0.05 : -0.05, on: 1, dark: 0.7, tint: side ? 'rgba(255,140,150,0.45)' : undefined });
      ctx.restore();
    });
    ctx.fillStyle = 'rgba(3,4,8,0.86)'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(217,221,228,0.2)'; ctx.fillRect(W / 2 - 1, 0, 2, H);
    const qa = so(T, sh.q, sh.q + 0.6);
    text(ctx, S('final_q'), W / 2, 260 - (1 - qa) * 30, { font: font(900, 104), align: 'center', color: PAL.white, alpha: qa, ls: 4 + (1 - qa) * 20, shadow: 'rgba(0,0,0,0.9)', blur: 30 });
    ctx.fillStyle = PAL.red; ctx.globalAlpha = qa; ctx.fillRect(W / 2 - 80 * qa, 310, 160 * qa, 5); ctx.globalAlpha = 1;
    text(ctx, S('final_a'), W / 2, 450, { font: font(800, 64), align: 'center', color: PAL.white, alpha: so(T, sh.a, sh.a + 0.5), ls: 3 });
    text(ctx, S('final_b'), W / 2, 560, { font: font(800, 64), align: 'center', color: PAL.white, alpha: so(T, sh.b, sh.b + 0.5), ls: 3 });
    text(ctx, S('final_c'), W / 2, 700, { font: font(600, 36), align: 'center', color: PAL.red, alpha: so(T, sh.c, sh.c + 0.6), ls: 8 });
    if (sh.d !== undefined) {
      const m = so(T, sh.d, sh.d + 0.5), s2 = so(T, sh.d2 ?? sh.d + 1.5, (sh.d2 ?? sh.d + 1.5) + 0.5);
      text(ctx, S('money'), W / 2 - 110, 870, { font: font(900, 56), align: 'right', color: PAL.white, alpha: m, ls: 6 });
      text(ctx, S('vs'), W / 2, 866, { font: font(700, 28), align: 'center', color: PAL.red, alpha: s2, ls: 6 });
      text(ctx, S('safety'), W / 2 + 110, 870, { font: font(900, 56), align: 'left', color: PAL.white, alpha: s2, ls: 6 });
    }
  },

  part2(ctx, T, sh) {
    // completely still frame: "the option with the most votes happens in part 2"
    const t0 = sh.start;
    withCam(ctx, { x: 960, y: 540, z: 1.08 }, 0.6, () => { ctx.fillStyle = '#06080d'; ctx.fillRect(-400, -400, 2800, 1900); drawWindow(ctx, t0, 260, 40, 1400, 1000, { fog: 1.3 }); });
    withCam(ctx, { x: 960, y: 540, z: 1.08 }, 1, () => drawHeroSide(ctx, t0, 1500, 560, 1.4, { phone: true, phoneLight: 0.6, rimCol: 'rgba(170,200,250,0.7)', rimX: 6, rimY: 3 }));
    ctx.fillStyle = 'rgba(3,4,8,0.7)'; ctx.fillRect(0, 0, W, H);
    const a = so(T, t0 + 0.1, t0 + 0.7), b = so(T, t0 + 0.5, t0 + 1.2), c = so(T, t0 + 1.0, t0 + 1.6);
    ctx.save(); ctx.globalAlpha = 0.12 * a; ctx.strokeStyle = PAL.white; ctx.lineWidth = 4;
    ctx.font = font(900, 760); ctx.textAlign = 'center'; ctx.strokeText('2', 1440, 900); ctx.restore();
    text(ctx, S('part2_top'), 140, 330, { font: font(800, 34), color: PAL.red, ls: 10, alpha: a });
    ctx.fillStyle = PAL.red; ctx.globalAlpha = a; ctx.fillRect(140, 356, 160, 4); ctx.globalAlpha = 1;
    text(ctx, S('part2_main'), 140, 470, { font: font(900, 60), color: PAL.white, ls: 2, alpha: b });
    text(ctx, S('part2_main2'), 140, 560, { font: font(900, 76), color: PAL.white, ls: 2, alpha: b });
    text(ctx, S('part2_tag'), 140, 720, { font: font(600, 34), color: PAL.mist, ls: 10, alpha: c });
  },
};
