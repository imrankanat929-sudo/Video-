// Frame renderer: picks the active shot, applies transitions and post FX.
'use strict';

let MAIN = null, BUF = null, READY = false;

async function boot(lang = 'ru') {
  TL = await (await fetch(`config/timeline.${lang}.json`)).json();
  STR = await (await fetch(TL.strings)).json();
  await document.fonts.load('900 40px "Inter"'); for (const w of [500, 700, 800]) await document.fonts.load(`${w} 40px "JetBrains Mono"`);
  for (const w of [300, 500, 600, 700, 800]) await document.fonts.load(`${w} 40px "Inter"`);
  MAIN = document.getElementById('c');
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
  if (s.type) GEN[s.type](ctx, T, s); else SHOTS[s.id](ctx, T, T - s.start, s.end - s.start);
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
  if (T < TL.cues.hard_black) postFX(ctx, T, frame);
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
