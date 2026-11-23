// Shared timeline for HUMAN MIND — Episode 02 vertical preview (9:16).
// Used by both the frame renderer and the audio builder so picture and sound stay in sync.
const FPS = 30;
const DURATION = 38; // seconds
const FRAMES = Math.round(FPS * DURATION);

const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const seg = (t, a, b) => clamp((t - a) / (b - a));

// Character walking: speed in world px/s.
function speedAt(t) {
  if (t < 6) return 92 * (1 - seg(t, 5.2, 6) ** 2 * 1) ;
  if (t < 8) return 0;
  if (t < 11.6) return 32 * seg(t, 8, 8.4) * (1 - seg(t, 11.0, 11.6));
  return 0;
}

const START_X = -540;
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
  let t = 6.25;
  let interval = 0.95;
  while (t < 11.9) {
    heartbeats.push(t);
    interval = Math.max(0.52, interval * 0.93);
    t += interval;
  }
}

const TREE_X = 330;
const REVEAL = { start: 11.95, end: 13.0 }; // silhouette -> tree morph, lamp switches on

// Scene boundaries (for whooshes / impacts in the audio).
const CUTS = {
  hookPullBack: 2.35,
  reveal: REVEAL.start,
  brain: 15.0,
  dots: 21.5,
  question: 28.0,
  question2: 31.3,
  logo: 34.5,
};

module.exports = { FPS, DURATION, FRAMES, clamp, seg, charX, walkAmt, footsteps, heartbeats, TREE_X, REVEAL, CUTS, STRIDE, START_X };
