// Frame renderer: picks the active shot, applies transitions and post FX.
'use strict';

let MAIN = null, BUF = null, READY = false;

async function boot(lang = 'ru') {
  TL = await (await fetch(`config/timeline.${lang}.json`)).json();
  STR = await (await fetch(TL.strings)).json();
  if (TL.transcriptFile) TL.transcript = await (await fetch(TL.transcriptFile)).json();
  await document.fonts.load('900 40px "Inter"'); for (const w of [500, 700, 800]) await document.fonts.load(`${w} 40px "JetBrains Mono"`);
  for (const w of [300, 500, 600, 700, 800]) await document.fonts.load(`${w} 40px "Inter"`);
  W = TL.width || 1920; H = TL.height || 1080;
  MAIN = document.getElementById('c'); MAIN.width = W; MAIN.height = H;
  BUF = makeCanvas(W, H);
  initFX(); initArt(); initUI(); initScenes();
  READY = true;
}

function shotAt(T) {
  const s = TL.shots;
  for (let i = s.length - 1; i >= 0; i--) if (T >= s[i].start) return i;
  return 0;
}
function drawShot(ctx, i, T) {
  const s = TL.shots[i];
  STR.clock = STR[s.clock || 'clock_night'] || STR.clock;
  ctx.save();
  ctx.fillStyle = PAL.black; ctx.fillRect(0, 0, W, H);
  if (s.type && FLAT[s.type]) FLAT[s.type](ctx, T, s); else if (s.type) GEN[s.type](ctx, T, s); else SHOTS[s.id](ctx, T, T - s.start, s.end - s.start);
  ctx.restore();
}
function renderAt(T, frame) {
  const ctx = MAIN.getContext('2d');
  const i = shotAt(T), s = TL.shots[i];
  const lt = T - s.start, dur = s.inDur || 0;
  drawShot(ctx, i, T);
  if (lt < dur && i > 0) {
    const k = ease.inOutSine(lt / dur);
    if (s.in === 'fade') {
      const b = BUF.getContext('2d');
      drawShot(b, i - 1, T);
      ctx.save(); ctx.globalAlpha = 1 - k; ctx.drawImage(BUF, 0, 0); ctx.restore();
    } else if (s.in === 'black') {
      ctx.fillStyle = `rgba(0,0,0,${1 - k})`; ctx.fillRect(0, 0, W, H);
    } else if (s.in === 'flash') {
      ctx.fillStyle = `rgba(225,230,240,${(1 - k) * 0.55})`; ctx.fillRect(0, 0, W, H);
    }
  } else if (i === 0 && lt < dur) {
    ctx.fillStyle = `rgba(0,0,0,${1 - ease.inOutSine(lt / dur)})`; ctx.fillRect(0, 0, W, H);
  }
  if (TL.flat && T < TL.cues.hard_black) flatOverlay(ctx, T, TL.shots[i]);
  if (T < TL.cues.hard_black) postFX(ctx, T, frame, { grain: TL.flat ? 0.07 : 0.16, flat: TL.flat });
  else { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H); }
}
window.renderFrame = (frame) => { renderAt(frame / TL.fps, frame); return true; };
window.grabFrame = (q = 0.94) => MAIN.toDataURL('image/jpeg', q);

// Separate background plates (no hero, no UI) for the asset folder.
const PLATES = {
  room_wide(ctx) { roomWide(ctx, 10, { x: 960, y: 540, z: 1 }, { hero: false, phoneOn: 0.6 }); },
  room_wide_red(ctx) { roomWide(ctx, 10, { x: 960, y: 540, z: 1 }, { hero: false, monitor: monWarning(10, { warn: 1, docs: 1, prog: 0.8 }), monTint: 'rgba(200,70,80,0.35)', phoneOn: 0.6 }); },
  window_fog(ctx) { withCam(ctx, { x: 960, y: 540, z: 1 }, 1, () => { ctx.fillStyle = '#06080d'; ctx.fillRect(0, 0, W, H); drawWindow(ctx, 10, 260, 40, 1400, 1000, { fog: 1.3 }); }); },
  dark_side(ctx) { SHOTS.s07_dark(ctx, 16.4, 0, 2.6); },
  desk_top(ctx) { withCam(ctx, { x: 960, y: 540, z: 1 }, 1, () => { drawDeskTop(ctx, 10); ctx.fillStyle = 'rgba(2,3,6,0.4)'; ctx.fillRect(-400, -400, 2800, 1900); }); },
  monitor_wall(ctx) { withCam(ctx, { x: 960, y: 540, z: 1 }, 1, () => { ctx.drawImage(ART.wall, -240, -160); glow(ctx, 960, 540, 1300, 'rgba(110,140,210,0.4)', 0.9); drawMonitor(ctx, 160, 90, 1600, 900, monDesktop(10), {}); }); },
};
window.renderPlate = (name) => {
  const ctx = MAIN.getContext('2d');
  ctx.save(); ctx.fillStyle = PAL.black; ctx.fillRect(0, 0, W, H); PLATES[name](ctx); ctx.restore();
  ctx.drawImage(FX.vignette, 0, 0);
  return MAIN.toDataURL('image/png');
};
window.plateNames = () => Object.keys(PLATES);

// YouTube thumbnail (1920x1080, export also as 1280x720)
window.renderThumb = () => {
  const ctx = MAIN.getContext('2d'), T = 30;
  STR.clock = STR.clock_night;
  ctx.save();
  ctx.fillStyle = '#05060a'; ctx.fillRect(0, 0, W, H);
  // background: room, hero from behind lit red by the monitor
  roomWide(ctx, T, { x: 1060, y: 560, z: 1.25 }, { monitor: monWarning(T, { warn: 1, docs: 1, prog: 0.8 }), monTint: 'rgba(220,60,70,0.55)', monLight: 1.1, rimCol: 'rgba(235,110,120,0.95)', phoneOn: 0, tilt: -0.08 });
  ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, W, H);
  const g = ctx.createLinearGradient(0, 0, W * 0.65, 0); g.addColorStop(0, 'rgba(3,4,8,0.95)'); g.addColorStop(1, 'rgba(3,4,8,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // phone with balance + stamp
  const scr = scrWallet(T, { refresh: -1, pulse: 0.8 });
  const sg = scr.getContext('2d');
  sg.save(); sg.translate(278, 420); sg.rotate(-0.16);
  sg.strokeStyle = PAL.red; sg.lineWidth = 9; rr(sg, -230, -66, 460, 132, 14); sg.stroke();
  text(sg, S('stolen'), 0, 28, { font: font(900, 74), align: 'center', color: PAL.red, ls: 6 });
  sg.restore();
  glow(ctx, 1500, 560, 700, 'rgba(160,190,255,0.5)', 0.9);
  drawPhone(ctx, 1500, 600, 0.78, 0.1, scr, { on: 1 });
  // headline
  text(ctx, 'WHAT IF…?', 110, 170, { font: font(900, 44), color: PAL.mist, ls: 10 });
  text(ctx, S('thumb_1'), 100, 430, { font: font(900, 250), color: '#ffffff', ls: -4, shadow: 'rgba(0,0,0,0.9)', blur: 40 });
  text(ctx, S('thumb_2'), 108, 620, { font: font(900, 150), color: '#e2343e', ls: 2, shadow: 'rgba(0,0,0,0.9)', blur: 40 });
  text(ctx, S('thumb_3'), 112, 760, { font: font(800, 64), color: '#ffffff', ls: 4, shadow: 'rgba(0,0,0,0.9)', blur: 30 });
  // A / B chips
  [['A', S('thumb_a')], ['B', S('thumb_b')]].forEach(([k, l], i) => {
    const y = 860 + i * 0; const x = 112 + i * 470;
    ctx.fillStyle = i ? 'rgba(200,50,58,0.95)' : 'rgba(217,221,228,0.95)'; rr(ctx, x, y, 440, 110, 18); ctx.fill();
    text(ctx, k + ' — ' + l, x + 220, y + 74, { font: font(900, 46), align: 'center', color: i ? '#fff' : '#0a0c12', ls: 2 });
  });
  ctx.restore();
  postFX(ctx, T, 3, { grain: 0.08 });
  return MAIN.toDataURL('image/png');
};

// Vertical 9:16 thumbnail (1080x1920)
window.renderThumbV = () => {
  const T = 30; STR.clock = STR.clock_night;
  const bg = BUF.getContext('2d');
  bg.save(); bg.fillStyle = '#05060a'; bg.fillRect(0, 0, W, H);
  roomWide(bg, T, { x: 1150, y: 560, z: 1.35 }, { monitor: monWarning(T, { warn: 1, docs: 1, prog: 0.8 }), monTint: 'rgba(220,60,70,0.55)', monLight: 1.1, rimCol: 'rgba(235,110,120,0.95)', phoneOn: 0, tilt: -0.08 });
  bg.restore();
  const cv = makeCanvas(1080, 1920), ctx = cv.getContext('2d');
  // background scaled to full height, centred on the hero
  const sc = 1920 / H;
  ctx.drawImage(BUF, 540 - 960 * sc, 0, W * sc, 1920);
  const g = ctx.createLinearGradient(0, 0, 0, 1920);
  g.addColorStop(0, 'rgba(3,4,8,0.92)'); g.addColorStop(0.38, 'rgba(3,4,8,0.35)'); g.addColorStop(0.7, 'rgba(3,4,8,0.55)'); g.addColorStop(1, 'rgba(3,4,8,0.95)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1080, 1920);
  // phone with stamp
  const scr = scrWallet(T, { refresh: -1, pulse: 0.8 }), sg = scr.getContext('2d');
  sg.save(); sg.translate(278, 420); sg.rotate(-0.16);
  sg.strokeStyle = PAL.red; sg.lineWidth = 9; rr(sg, -230, -66, 460, 132, 14); sg.stroke();
  text(sg, S('stolen'), 0, 28, { font: font(900, 74), align: 'center', color: PAL.red, ls: 6 });
  sg.restore();
  glow(ctx, 540, 1180, 650, 'rgba(160,190,255,0.5)', 0.9);
  drawPhone(ctx, 560, 1180, 0.6, 0.07, scr, { on: 1 });
  // text
  text(ctx, 'WHAT IF…?', 540, 150, { font: font(900, 46), align: 'center', color: PAL.mist, ls: 12 });
  text(ctx, S('thumb_1'), 540, 400, { font: font(900, 240), align: 'center', color: '#fff', ls: -4, shadow: 'rgba(0,0,0,0.9)', blur: 40 });
  text(ctx, S('thumb_2'), 540, 570, { font: font(900, 150), align: 'center', color: '#e2343e', ls: 2, shadow: 'rgba(0,0,0,0.9)', blur: 40 });
  text(ctx, S('thumb_3'), 540, 1640, { font: font(900, 70), align: 'center', color: '#fff', ls: 3, shadow: 'rgba(0,0,0,0.9)', blur: 30 });
  [['A', S('thumb_a')], ['B', S('thumb_b')]].forEach(([k, l], i) => {
    const x = 60 + i * 500, y = 1700;
    ctx.fillStyle = i ? 'rgba(200,50,58,0.95)' : 'rgba(217,221,228,0.95)'; rr(ctx, x, y, 460, 120, 20); ctx.fill();
    text(ctx, k + ' — ' + l, x + 230, y + 80, { font: font(900, 48), align: 'center', color: i ? '#fff' : '#0a0c12', ls: 2 });
  });
  // grain + vignette
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = 0.08;
  for (let y = 0; y < 1920; y += 384) for (let x = 0; x < 1080; x += 384) ctx.drawImage(FX.grain[2], x, y);
  ctx.restore();
  return cv.toDataURL('image/png');
};
