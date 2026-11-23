// Shared timeline for HUMAN MIND — Episode 02 vertical preview (9:16).
// Used by both the frame renderer and the audio builder so picture and sound stay in sync.
const FPS = 30;
const DURATION = 102; // seconds — voiceover (95.4 s) + end card
const FRAMES = Math.round(FPS * DURATION);

const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const seg = (t, a, b) => clamp((t - a) / (b - a));

// Character walking: speed in world px/s.
function speedAt(t) {
  // synced to the voiceover: "Ты останавливаешься" 5.1 s, "стоит подойти ближе?" 11.8 s
  if (t < 5.1) return 92 * (1 - seg(t, 4.4, 5.1) ** 2);
  if (t < 11.8) return 0;
  if (t < 14.0) return 32 * seg(t, 11.8, 12.2) * (1 - seg(t, 13.5, 14.0));
  return 0;
}

const START_X = -460;
const STRIDE = 70; // world px per half-cycle (one footstep)

// Precompute per-frame character x and walk phase, plus footstep times.
const charX = new Float64Array(FRAMES + 1);
const walkAmt = new Float64Array(FRAMES + 1);
const footsteps = [];
{
  let x = START_X;
  let lastStep = 0;
  for (let f = 0; f <= FRAMES; f++) {
    const t = f / FPS;
    charX[f] = x;
    walkAmt[f] = clamp(speedAt(t) / 40);
    const step = Math.floor((x - START_X) / STRIDE);
    if (step > lastStep) {
      footsteps.push({ t, v: clamp(speedAt(t) / 92, 0.35, 1) });
      lastStep = step;
    }
    x += speedAt(t) / FPS;
  }
}

// Heartbeats: start once he notices the figure, accelerate, stop at the reveal.
const heartbeats = [];
{
  let t = 6.9; // "Сердце начинает биться быстрее"
  let interval = 0.95;
  while (t < 14.1) {
    heartbeats.push(t);
    interval = Math.max(0.52, interval * 0.93);
    t += interval;
  }
}

const TREE_X = 330;
const REVEAL = { start: 14.2, end: 15.2 }; // "Это всего лишь дерево" // silhouette -> tree morph, lamp switches on

// Scene boundaries (for whooshes / impacts in the audio).
const CUTS = {
  hookPullBack: 2.0,
  reveal: REVEAL.start,
  brain: 17.0,                // "твой мозг уже успел убедить тебя"
  explain: 23.4,              // "Почему так происходит?"
  cloud: 43.5,                // "Представь облако, похожее на лицо"
  dots: 46.7,                 // "Или случайное совпадение…"
  objects: [57.8, 64.8, 71.8],// Kahneman / fast thinking; each 7 s, reveal at +3.6 s
  examine: 78.8,              // "В следующий раз… остановись"
  question: 89.3,             // "Ты действительно видишь реальность?"
  logo: 97.0,
};
const OBJ_REVEAL = 3.6;

module.exports = { OBJ_REVEAL, FPS, DURATION, FRAMES, clamp, seg, charX, walkAmt, footsteps, heartbeats, TREE_X, REVEAL, CUTS, STRIDE, START_X };
