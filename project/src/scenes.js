// Shot list. Each shot: draw(ctx, T, lt, d) — T absolute time, lt local time, d duration.
'use strict';

let TL = null;                         // timeline config
const C = k => TL.cues[k];             // cue time
const SPR = {};

function initScenes() {
  // blurred foreground sprites for parallax depth
  SPR.fgHero = makeCanvas(900, 1100);
  {
    const tmp = makeCanvas(900, 1100), g = tmp.getContext('2d');
    drawHeroBack(g, 0, 450, 260, 1.25, { rimCol: 'rgba(110,135,180,0.6)' });
    const s = SPR.fgHero.getContext('2d'); s.filter = 'blur(10px)'; s.drawImage(tmp, 0, 0);
  }
  SPR.cable = makeCanvas(2200, 500);
  {
    const g = SPR.cable.getContext('2d'); g.filter = 'blur(14px)';
    g.strokeStyle = '#020305'; g.lineWidth = 70; g.lineCap = 'round';
    g.beginPath(); g.moveTo(-100, 420); g.bezierCurveTo(500, 200, 900, 520, 1500, 300); g.bezierCurveTo(1800, 200, 2000, 350, 2300, 260); g.stroke();
  }
}

// ---------- reusable compositions ----------
function roomWide(ctx, T, cam, o = {}) {
  const mon = o.monitor || monDesktop(T, o.monState || {});
  withCam(ctx, cam, 0.78, () => drawRoomBack(ctx, T, o));
  if (o.morning) { ctx.fillStyle = 'rgba(120,135,160,0.06)'; ctx.fillRect(0, 0, W, H); }
  withCam(ctx, cam, 0.78, () => monitorLight(ctx, (o.monLight ?? 0.8), o.monTint));
  withCam(ctx, cam, 1, () => {
    drawRoomDesk(ctx, T, { monitor: mon, phoneOn: o.phoneOn ?? 0, phoneX: o.phoneX, phoneY: o.phoneY, monBright: o.monBright });
    dust(ctx, T, 1300, 470, 420, 0.8);
  });
  if (o.hero !== false) withCam(ctx, cam, 1.08, () => drawHeroBack(ctx, T, o.heroX ?? 1190, o.heroY ?? 505, 1, { rimCol: o.rimCol || 'rgba(140,170,230,0.85)', rimX: 6, rimY: -6, tilt: o.tilt || 0 }));
  // foreground: blurred bed corner for depth
  withCam(ctx, cam, 1.35, () => {
    ctx.save(); ctx.filter = 'blur(12px)'; ctx.fillStyle = '#030406';
    ctx.beginPath(); ctx.moveTo(-200, 860); ctx.quadraticCurveTo(200, 820, 420, 900); ctx.lineTo(520, 1300); ctx.lineTo(-200, 1300); ctx.fill();
    ctx.restore();
  });
}
// top-down desk with a phone lying on it
function deskPhone(ctx, T, cam, screen, o = {}) {
  const px = o.px ?? 960, py = o.py ?? 540, s = o.s ?? 0.78, rot = o.rot ?? -0.06;
  const vib = o.vib ? shake(T, o.vib, 60, 4) : { x: 0, y: 0, r: 0 };
  withCam(ctx, cam, 0.97, () => {
    drawDeskTop(ctx, T);
    ctx.fillStyle = `rgba(2,3,6,${o.dark ?? 0.55})`; ctx.fillRect(-400, -400, 2800, 1900);
    phoneSpill(ctx, px, py, 1000 * s, (o.on ?? 1) * (o.spill ?? 0.55), o.tint);
  });
  withCam(ctx, cam, 1, () => {
    drawPhone(ctx, px + vib.x, py + vib.y, s, rot + vib.r * 20, screen, { on: o.on ?? 1 });
    if (o.on) dust(ctx, T, px, py, 500, 0.4, 20);
  });
  withCam(ctx, cam, 1.4, () => { ctx.globalAlpha = 0.95; ctx.drawImage(SPR.cable, -300, 760); ctx.globalAlpha = 1; });
}
// phone held in hand, frontal, with over-shoulder hair at the edge
function heldPhone(ctx, T, cam, screen, o = {}) {
  const sh = shake(T, o.shake ?? 4, 1.2, 2);
  withCam(ctx, cam, 0.7, () => {
    ctx.fillStyle = '#05070b'; ctx.fillRect(-400, -400, 2800, 1900);
    ctx.drawImage(ART.wall, -200, -100);
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(-400, -400, 2800, 1900);
    drawWindow(ctx, T, 1300, 60, 520, 460, {});
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(1200, 0, 800, 700);
  });
  withCam(ctx, cam, 1, () => {
    glow(ctx, 960, 540, 900, 'rgba(140,170,240,0.35)', (o.on ?? 1) * 0.9);
    drawPhone(ctx, 960 + sh.x * 3, 560 + sh.y * 3, o.s ?? 0.8, -0.03 + sh.r * 8, screen, { on: o.on ?? 1 });
    // fingers (silhouette) on the sides
    ctx.fillStyle = '#07080c';
    const fx = 960 + sh.x * 3, fy = 560 + sh.y * 3, s = o.s ?? 0.8;
    for (let i = 0; i < 3; i++) { rr(ctx, fx + 228 * s, fy + (60 + i * 95) * s, 70 * s, 80 * s, 34 * s); ctx.fill(); }
    rr(ctx, fx - 300 * s, fy + 160 * s, 80 * s, 210 * s, 40 * s); ctx.fill();
    ctx.beginPath(); ctx.ellipse(fx, fy + 760 * s, 420 * s, 260 * s, 0, 0, 7); ctx.fill();
  });
  if (o.fg !== false) withCam(ctx, cam, 1.3, () => ctx.drawImage(SPR.fgHero, -520, 200, 900, 1100));
}
function monitorClose(ctx, T, cam, screen, o = {}) {
  withCam(ctx, cam, 0.9, () => {
    ctx.drawImage(ART.wall, -240, -160);
    glow(ctx, 960, 540, 1300, o.tint || 'rgba(110,140,210,0.4)', 0.9);
  });
  withCam(ctx, cam, 1, () => {
    drawMonitor(ctx, 160, 90, 1600, 900, screen, {});
    dust(ctx, T, 960, 540, 700, 0.7, 40);
  });
  if (o.fg !== false) withCam(ctx, cam, 1.3, () => ctx.drawImage(SPR.fgHero, -380, 330, 900, 1100));
}
// big typographic option card
function optionText(ctx, T, t0, label, main, x, y, align = 'left', o = {}) {
  const a = so(T, t0, t0 + 0.5), b = so(T, t0 + 0.15, t0 + 0.9);
  ctx.save();
  ctx.globalAlpha = a;
  text(ctx, label, x, y - 92 + (1 - a) * 20, { font: font(800, 34), color: PAL.red, align, ls: 10 });
  const lw = 160 * a;
  ctx.fillStyle = PAL.red;
  ctx.fillRect(align === 'left' ? x : x - lw, y - 70, lw, 4);
  ctx.restore();
  ctx.save();
  ctx.font = font(900, o.size || 92);
  const lines = o.lines || [main];
  lines.forEach((l, i) => {
    const k = so(T, t0 + 0.15 + i * 0.12, t0 + 0.9 + i * 0.12);
    ctx.save();
    ctx.beginPath(); ctx.rect(-5000, y - 90 + i * 104, 10000, 110); ctx.clip();
    text(ctx, l, x, y + i * 104 + (1 - k) * 110, { font: font(900, o.size || 92), color: PAL.white, align, ls: 2 + (1 - k) * 12, shadow: 'rgba(0,0,0,0.8)', blur: 30 });
    ctx.restore();
  });
  ctx.restore();
}

// ---------- shots ----------
const SHOTS = {
  s01_room(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = camLerp({ x: 990, y: 540, z: 1.0 }, { x: 900, y: 600, z: 1.28 }, k);
    const on = so(T, C('phone_vibrate_1'), C('phone_vibrate_1') + 0.3);
    const vibing = T > C('phone_vibrate_1') && T < C('phone_vibrate_1') + 0.9;
    const vib = vibing ? shake(T, 3, 70, 1) : { x: 0, y: 0 };
    roomWide(ctx, T, cam, { phoneOn: on * (vibing ? 0.85 + 0.15 * Math.sin(T * 60) : 1), phoneX: 800 + vib.x, phoneY: 716 + vib.y, tilt: -0.08 * so(T, C('phone_vibrate_1') + 0.2, C('phone_vibrate_1') + 1.0) });
    // series title
    const ta = sm(T, 0.6, 1.4) * (1 - sm(T, 3.0, 3.8));
    text(ctx, S('series'), 90, 120, { font: font(900, 46), color: PAL.white, alpha: ta, ls: 8 });
    text(ctx, S('episode'), 92, 160, { font: font(600, 20), color: PAL.red, alpha: ta, ls: 6 });
  },

  s02_notify(ctx, T, lt, d) {
    const z = lerp(1.55, 1.9, ease.inOutSine(lt / d));
    const cam = { x: 950, y: lerp(500, 470, lt / d), z };
    const a = so(T, C('btc_word'), C('btc_word') + 0.35);
    const scr = scrLock(T, { notifs: [{ kind: 'btc', app: S('wallet_app'), title: S('n_recv_title'), body: S('n_recv_body'), a, big: true }], flash: 1 - so(T, C('btc_word'), C('btc_word') + 0.5) });
    deskPhone(ctx, T, cam, scr, { on: 1, vib: T < 4.8 ? 2.5 : 0, spill: 0.6 + 0.3 * (1 - a) });
  },

  s03_wallet(ctx, T, lt, d) {
    // state 1: balance close-up, refresh x2; state 2: pan down to history
    const r1 = ramp(T, C('refresh_1'), C('refresh_1') + 0.7), r2 = ramp(T, C('refresh_2'), C('refresh_2') + 0.7);
    const refresh = (T >= C('refresh_1') && T <= C('refresh_1') + 0.7) ? r1 : (T >= C('refresh_2') && T <= C('refresh_2') + 0.7) ? r2 : -1;
    const flick = (T > C('refresh_1') + 0.6 && T < C('refresh_1') + 0.8) || (T > C('refresh_2') + 0.6 && T < C('refresh_2') + 0.8);
    const scr = scrWallet(T, { refresh, flick, pulse: so(T, C('refresh_2') + 0.7, C('refresh_2') + 0.8) * (1 - so(T, C('refresh_2') + 0.8, C('refresh_2') + 1.2)), txRed: 0 });
    const pan = sm(T, 8.0, 9.3);
    const cam = { x: lerp(930, 990, lt / d), y: lerp(330, 640, pan), z: lerp(1.75, 1.55, pan) };
    deskPhone(ctx, T, cam, scr, { on: 1 });
  },

  s04_news(ctx, T, lt, d) {
    const st = C('stolen_word');
    const snap = ease.outExpo(ramp(T, st, st + 0.28));
    const scr = scrNews(T, { stamp: so(T, st + 0.05, st + 0.3) });
    const sh = T > st ? shake(T, 6 * (1 - ramp(T, st, st + 0.8)), 25, 3) : { x: 0, y: 0, r: 0 };
    const cam = { x: lerp(960, 960, snap) + sh.x, y: lerp(lerp(560, 470, ramp(T, 9.85, st)), 380, snap) + sh.y, z: lerp(lerp(1.15, 1.35, ramp(T, 9.85, st)), 2.0, snap), r: sh.r };
    heldPhone(ctx, T, cam, scr, { shake: 3 });
    // red pulse + darkening at the end of the shot ("these coins were not a gift")
    if (T > st) { ctx.fillStyle = rgba(PAL.red, 0.18 * (1 - ramp(T, st, st + 0.6))); ctx.fillRect(0, 0, W, H); }
    ctx.fillStyle = `rgba(0,0,0,${sm(T, d + 9.85 - 0.4, d + 9.85) * 0.9})`; ctx.fillRect(0, 0, W, H);
  },

  s05_graph(ctx, T, lt, d) {
    const foc = so(T, C('graph_match'), C('graph_match') + 0.4);
    const scr = monGraph(T, { reveal: so(T, 12.85, 13.6), focus: foc });
    const k = ease.inOutSine(lt / d);
    const sh = shake(T, 1.5, 2, 8);
    const cam = { x: lerp(620, 1300, k) + sh.x, y: lerp(520, 600, k) + sh.y, z: lerp(1.35, 1.9, sm(T, C('graph_match'), 14.4)) };
    monitorClose(ctx, T, cam, scr, { fg: false, tint: foc ? 'rgba(200,60,70,0.25)' : undefined });
  },

  s06_sender(ctx, T, lt, d) {
    const po = C('profile_open');
    const slide = sm(T, po, po + 0.35);
    // two screens side by side inside the phone: chat -> profile
    const chat = scrChat(T, { msgs: [{ text: S('m_lucky'), a: so(T, C('lucky_msg'), C('lucky_msg') + 0.3) }] });
    const tmp = SCR.phone2.getContext('2d');
    tmp.drawImage(chat, -slide * PHONE.sw, 0);
    const prof = scrProfile(T, { p: ramp(T, po + 0.2, po + 0.7) });
    tmp.drawImage(prof, (1 - slide) * PHONE.sw, 0);
    const k = ease.inOutSine(lt / d);
    const still = T > po + 0.7;                                  // short pause after empty profile
    const cam = { x: 960, y: lerp(480, 430, k), z: lerp(1.25, 1.45, k) };
    heldPhone(ctx, T, cam, SCR.phone2, { shake: still ? 0.6 : 3 });
  },

  s07_dark(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = { x: lerp(900, 980, k), y: lerp(540, 520, k), z: lerp(1.0, 1.18, k) };
    const v = C('vibrate_2'), vib = T > v && T < v + 1.4;
    const on = so(T, v, v + 0.2) * (vib ? 0.8 + 0.2 * Math.sin(T * 50) : 1);
    withCam(ctx, cam, 0.7, () => {
      ctx.drawImage(ART.wall, -240, -160);
      drawWindow(ctx, T, 160, 120, 700, 560, {});
      ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(-300, -300, 2600, 1700);
    });
    const jx = vib ? shake(T, 3, 80, 5).x : 0;
    withCam(ctx, cam, 1, () => {
      // desk (side view)
      ctx.fillStyle = '#0b0e15'; ctx.fillRect(-200, 740, 2400, 26);
      ctx.fillStyle = '#05060a'; ctx.fillRect(-200, 766, 2400, 600);
      ctx.fillStyle = 'rgba(150,175,220,0.12)'; ctx.fillRect(-200, 740, 2400, 2);
      // phone flat on desk
      ctx.fillStyle = '#05060a'; rr(ctx, 1180 + jx, 728, 170, 14, 5); ctx.fill();
      ctx.fillStyle = `rgba(190,210,255,${on})`; ctx.fillRect(1186 + jx, 726, 158, 3);
      glow(ctx, 1265 + jx, 700, 520, 'rgba(150,180,255,0.6)', on);
      // light pooled on desk surface
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = on * 0.5;
      const pg = ctx.createRadialGradient(1265, 742, 0, 1265, 742, 420); pg.addColorStop(0, 'rgba(150,180,255,0.6)'); pg.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = pg; ctx.fillRect(800, 735, 900, 30); ctx.restore();
      drawHeroSide(ctx, T, 760, 420 + so(T, v + 0.3, v + 1.5) * 18, 1.25, { rimCol: `rgba(150,180,240,${0.25 + on * 0.7})`, rimX: 6 * (0.3 + on), rimY: 3 });
      ctx.fillStyle = '#05060a'; ctx.fillRect(-200, 766, 2400, 600);       // desk front occludes torso
      dust(ctx, T, 1200, 600, 400, on * 0.8, 10);
    });
  },

  s08_threats(ctx, T, lt, d) {
    const msgs = [
      { text: S('m_lucky'), a: 1 },
      { text: S('m_dont'), a: so(T, C('new_msg'), C('new_msg') + 0.3), red: true },
      { text: S('m_know'), a: so(T, 19.8, 20.1), red: true },
      { text: S('m_chance'), a: so(T, C('chance_msg'), C('chance_msg') + 0.3), red: true },
    ];
    const scr = scrChat(T, { msgs, typing: (T > 20.15 && T < C('chance_msg')) ? 1 : 0 });
    // missed call banner sliding over the chat
    const g = scr.getContext('2d');
    const ba = so(T, 19.0, 19.35) * (1 - sm(T, 20.3, 20.7));
    if (ba > 0) notifCard(g, 100, ba, { kind: 'call', app: S('missed'), title: S('hidden_num'), body: '02:49', red: true });
    const fade = sm(T, C('silence_start') - 0.4, C('silence_start') + 0.4);   // screen fades out
    const k = ease.inOutSine(lt / d);
    const cam = { x: 960, y: lerp(560, 620, k), z: lerp(1.35, 1.6, k) };
    heldPhone(ctx, T, cam, scr, { shake: 4, on: 1 - fade * 0.9 });
    ctx.fillStyle = `rgba(0,0,0,${fade * 0.7})`; ctx.fillRect(0, 0, W, H);
  },

  s09_lastmsg(ctx, T, lt, d) {
    const km = C('keep_msg');
    const a = so(T, km, km + 0.35);
    const scr = scrLock(T, { notifs: [{ kind: 'msg', app: S('msg_app'), title: S('unknown'), body: S('m_keep'), a, big: true, red: true }], flash: 1 - so(T, km, km + 0.6) });
    const k = ease.inOutSine(lt / d);
    const cam = { x: 960, y: lerp(560, 360, k), z: lerp(1.0, 1.75, k) };
    deskPhone(ctx, T, cam, scr, { on: so(T, 22.85, 22.95), vib: T < 23.3 ? 2 : 0, dark: 0.7, spill: 0.7 });
  },

  s10_window(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = { x: lerp(980, 1020, k), y: 520, z: lerp(1.05, 1.17, k) };
    withCam(ctx, cam, 0.6, () => {
      ctx.fillStyle = '#06080d'; ctx.fillRect(-400, -400, 2800, 1900);
      drawWindow(ctx, T, 260, 40, 1400, 1000, { fog: 1.3 });
    });
    withCam(ctx, cam, 1, () => {
      drawHeroSide(ctx, T, 900, 470, 1.55, { phone: true, phoneLight: 0.9, rimCol: 'rgba(170,200,250,0.95)', rimX: 7, rimY: 4 });
    });
    withCam(ctx, cam, 1.3, () => { ctx.drawImage(SPR.cable, -600, 900); });
  },

  s11_two(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = { x: 960, y: lerp(560, 500, k), z: lerp(0.95, 1.12, k) };
    deskPhone(ctx, T, cam, scrWallet(T, { refresh: -1 }), { on: 1, dark: 0.65 });
  },

  s12_optA(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = { x: lerp(980, 1010, k), y: 540, z: lerp(1.0, 1.08, k) };
    const scr = scrWallet(T, { refresh: -1, pulse: 0.4 + 0.3 * Math.sin(T * 3) });
    deskPhone(ctx, T, cam, scr, { px: 560, py: 560, s: 0.72, rot: -0.1, on: 1, dark: 0.7 });
    ctx.fillStyle = 'rgba(3,4,8,0.45)'; ctx.fillRect(960, 0, 960, H);
    optionText(ctx, T, C('optA'), S('optA_label'), '', 1000, 500, 'left', { lines: S('optA').split(' ').reduce((a, w) => { if (a.length && (a[a.length - 1] + ' ' + w).length <= 12) a[a.length - 1] += ' ' + w; else a.push(w); return a; }, []), size: 92 });
    // "millionaire" counter
    const m = C('millionaire');
    if (T > m - 0.2) {
      const p = so(T, m - 0.2, m + 0.9);
      const val = Math.floor(lerp(0, 1000000, p));
      const s = '$' + String(val).replace(/\B(?=(\d{3})+(?!\d))/g, STR.thousands || ' ') + (p >= 1 ? '+' : '');
      text(ctx, s, 1004, 860, { font: font(800, 72), color: PAL.white, alpha: clamp(p * 3), shadow: 'rgba(200,215,255,0.35)', blur: 30 });
    }
  },

  s13_invest(ctx, T, lt, d) {
    const iv = C('investigation');
    if (T < 38.6) {
      const scr = monWarning(T, { docs: so(T, iv, iv + 1.2), warn: so(T, 36.2, 36.6), prog: ramp(T, 36.4, 39.5) * 0.8 });
      const k = ease.inOutSine(ramp(T, 34.65, 38.6));
      const cam = { x: lerp(560, 1260, k), y: lerp(560, 470, k), z: lerp(1.25, 1.45, k) };
      const red = so(T, 36.2, 36.6);
      monitorClose(ctx, T, cam, scr, { tint: red ? `rgba(${110 + red * 90},${140 - red * 80},${210 - red * 140},0.4)` : undefined });
      // typing flicker on monitor light
      ctx.fillStyle = `rgba(0,0,0,${0.06 * (noise1(T * 20) * 0.5 + 0.5)})`; ctx.fillRect(0, 0, W, H);
    } else {
      // wide: hero has put the phone down on the desk
      const k = ease.inOutSine(ramp(T, 38.6, 40.25));
      const cam = camLerp({ x: 1000, y: 560, z: 1.12 }, { x: 960, y: 580, z: 1.2 }, k);
      const put = so(T, 38.6, 39.3);
      roomWide(ctx, T, cam, { monitor: monWarning(T, { warn: 1, docs: 1, prog: 0.8 }), monTint: 'rgba(200,70,80,0.35)', rimCol: 'rgba(210,120,130,0.8)', phoneOn: 0.9 - put * 0.4, phoneX: lerp(950, 800, put), phoneY: lerp(660, 716, put) });
    }
  },

  s14_optB(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = { x: lerp(940, 910, k), y: 540, z: lerp(1.0, 1.08, k) };
    const calling = T > C('police_word');
    deskPhone(ctx, T, cam, scrCall(T, { calling }), { px: 1380, py: 560, s: 0.72, rot: 0.08, on: 1, dark: 0.7, tint: 'rgba(255,140,150,0.45)' });
    ctx.fillStyle = 'rgba(3,4,8,0.45)'; ctx.fillRect(0, 0, 960, H);
    // police light flicker at the edges while calling
    if (calling) {
      const ph = Math.floor(T * 3) % 2;
      glow(ctx, ph ? 0 : W, H / 2, 900, ph ? 'rgba(200,50,58,0.5)' : 'rgba(70,100,200,0.45)', 0.35 * so(T, C('police_word'), C('police_word') + 0.5));
    }
    optionText(ctx, T, C('optB'), S('optB_label'), '', 120, 500, 'left', { lines: S('optB').split(' ').reduce((a, w) => { if (a.length && (a[a.length - 1] + ' ' + w).length <= 12) a[a.length - 1] += ' ' + w; else a.push(w); return a; }, []), size: 92 });
    // "give up the chance to get rich": 10 BTC crossed out
    const rf = C('refuse_word');
    if (T > rf - 0.3) {
      const a = so(T, rf - 0.3, rf + 0.2), st = so(T, rf + 0.3, rf + 1.0);
      text(ctx, '10 BTC  ≈ $1 000 000', 124, 860, { font: font(700, 48, 'mono'), color: PAL.mist, alpha: a * (1 - st * 0.5) });
      ctx.fillStyle = PAL.red; ctx.fillRect(118, 842, 640 * st, 5);
    }
  },

  s15_desk(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = { x: lerp(1000, 960, k), y: lerp(600, 540, k), z: lerp(0.9, 1.1, k) };
    const on = so(T, 47.4, 47.9);
    deskPhone(ctx, T, cam, scrWallet(T, { refresh: -1 }), { on, dark: 0.75 });
  },

  s16_split(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const wl = so(T, C('wallet_word'), C('wallet_word') + 0.4), er = so(T, C('emergency_word'), C('emergency_word') + 0.4);
    const leftHi = wl * (1 - er), rightHi = er;
    const open = sm(T, 48.95, 49.6);
    const half = (side) => {
      ctx.save();
      ctx.beginPath(); side ? ctx.rect(W / 2 + 3, 0, W / 2, H) : ctx.rect(0, 0, W / 2 - 3, H); ctx.clip();
      ctx.translate(side ? W / 4 : -W / 4, 0);
      const cam = { x: side ? lerp(1450, 1430, k) : lerp(470, 490, k), y: 540, z: lerp(1.0, 1.08, k) * (2 - open) };
      const scr = side ? scrCall(T, { calling: T > C('emergency_word') }, SCR.phone2) : scrWallet(T, { refresh: -1 });
      deskPhone(ctx, T, cam, scr, { px: side ? 1440 : 480, py: 560, s: 0.68, rot: side ? 0.05 : -0.05, on: 1, dark: 0.7, tint: side ? 'rgba(255,140,150,0.45)' : undefined });
      const dim = side ? leftHi * 0.6 : rightHi * 0.6;
      ctx.fillStyle = `rgba(0,0,0,${dim})`; ctx.fillRect(0, 0, W, H);
      ctx.restore();
    };
    half(0); half(1);
    // divider grows from the centre
    ctx.fillStyle = PAL.white; ctx.globalAlpha = 0.8;
    const lh = H * open; ctx.fillRect(W / 2 - 2, H / 2 - lh / 2, 4, lh); ctx.globalAlpha = 1;
    text(ctx, S('split_left'), W / 4, 1010, { font: font(800, 34), align: 'center', color: PAL.white, ls: 8, alpha: 0.35 + wl * 0.65 * (1 - er * 0.5) });
    text(ctx, S('split_right'), W * 3 / 4, 1010, { font: font(800, 34), align: 'center', color: er ? PAL.red : PAL.white, ls: 8, alpha: 0.35 + er * 0.65 });
  },

  s17_decide(ctx, T, lt, d) {
    const k = ease.inOutSine(lt / d);
    const cam = camLerp({ x: 1100, y: 560, z: 1.25 }, { x: 1160, y: 540, z: 1.55 }, k);
    roomWide(ctx, T, cam, { monitor: monWarning(T, { warn: 1, docs: 1, prog: 0.8 }), monTint: 'rgba(200,70,80,0.3)', monLight: 0.6, phoneOn: 0.9, rimCol: 'rgba(200,140,160,0.75)', tilt: -0.1 });
    ctx.fillStyle = `rgba(0,0,0,${0.2 + k * 0.3})`; ctx.fillRect(0, 0, W, H);
  },

  s18_final(ctx, T, lt, d) {
    // background: dim split view, slow zoom, then fully still from camera_freeze
    const zt = Math.min(T, C('camera_freeze'));
    const k = ease.inOutSine(ramp(zt, 57.0, C('camera_freeze')));
    const z = lerp(1.0, 1.06, k);
    const Tb = Math.min(T, C('camera_freeze'));              // freeze background motion too
    [0, 1].forEach(side => {
      ctx.save(); ctx.beginPath(); side ? ctx.rect(W / 2 + 3, 0, W / 2, H) : ctx.rect(0, 0, W / 2 - 3, H); ctx.clip();
      ctx.translate(side ? W / 4 : -W / 4, 0);
      const scr = side ? scrCall(Tb, { calling: false }, SCR.phone2) : scrWallet(Tb, { refresh: -1 });
      deskPhone(ctx, Tb, { x: side ? 1440 : 480, y: 560, z }, scr, { px: side ? 1440 : 480, py: 560, s: 0.68, rot: side ? 0.05 : -0.05, on: 1, dark: 0.7, tint: side ? 'rgba(255,140,150,0.45)' : undefined });
      ctx.restore();
    });
    ctx.fillStyle = 'rgba(3,4,8,0.84)'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = 'rgba(217,221,228,0.25)'; ctx.fillRect(W / 2 - 1, 0, 2, H);
    const q = C('final_q');
    const qa = so(T, q, q + 0.6);
    text(ctx, S('final_q'), W / 2, 330 - (1 - qa) * 30, { font: font(900, 104), align: 'center', color: PAL.white, alpha: qa, ls: 4 + (1 - qa) * 20, shadow: 'rgba(0,0,0,0.9)', blur: 30 });
    ctx.fillStyle = PAL.red; ctx.globalAlpha = qa; ctx.fillRect(W / 2 - 80 * qa, 380, 160 * qa, 5); ctx.globalAlpha = 1;
    const fa = so(T, C('final_a'), C('final_a') + 0.5), fb = so(T, C('final_b'), C('final_b') + 0.5), fc = so(T, C('final_c'), C('final_c') + 0.6);
    text(ctx, S('final_a'), W / 2, 540, { font: font(800, 64), align: 'center', color: PAL.white, alpha: fa, ls: 3 });
    text(ctx, S('final_b'), W / 2, 650, { font: font(800, 64), align: 'center', color: PAL.white, alpha: fb, ls: 3 });
    text(ctx, S('final_c'), W / 2, 850, { font: font(600, 36), align: 'center', color: PAL.red, alpha: fc, ls: 8 });
    if (T >= C('hard_black')) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
  },
};
