// Synthesises the sound-design layer (footsteps, heartbeat, whooshes, reveal, impacts)
// from the shared timeline and writes a 48 kHz stereo WAV.  Usage: node audio.js out.wav
const fs = require('fs');
const T = require('./timeline');
const SR = 48000;
const N = Math.ceil(T.DURATION * SR);
const L = new Float32Array(N), Rr = new Float32Array(N);
let seed = 12345; const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;

function add(t0, len, fn, gain = 1, pan = 0) {
  const s0 = Math.floor(t0 * SR), n = Math.floor(len * SR);
  const gl = gain * Math.min(1, 1 - pan), gr = gain * Math.min(1, 1 + pan);
  for (let i = 0; i < n && s0 + i < N; i++) { if (s0 + i < 0) continue; const v = fn(i / SR, i); L[s0 + i] += v * gl; Rr[s0 + i] += v * gr; }
}
// one-pole lowpass noise generator
function lpNoise(cut) { let y = 0; const a = Math.exp(-2 * Math.PI * cut / SR); return () => (y = (1 - a) * rnd() + a * y); }

// footsteps: soft low-passed thumps
for (const f of T.footsteps) {
  const nz = lpNoise(900);
  add(f.t, 0.14, (t) => (nz() * 3 + Math.sin(2 * Math.PI * 90 * t) * 0.6) * Math.exp(-t * 38) * (t < 0.004 ? t / 0.004 : 1), 0.22 * f.v, Math.sin(f.t * 3) * 0.2);
}
// heartbeat: lub-dub low sine thumps with pitch drop
function thump(t0, g) {
  add(t0, 0.35, (t) => { const fq = 62 - 20 * t; return Math.sin(2 * Math.PI * fq * t) * Math.exp(-t * 14) * Math.min(1, t / 0.006); }, g);
}
T.heartbeats.forEach((hb, i) => { const g = 0.55 + 0.35 * (i / T.heartbeats.length); thump(hb, g); thump(hb + 0.17, g * 0.65); });

// whoosh: band-swept noise
function whoosh(t0, len, g, rev = false) {
  const nz = lpNoise(1);
  let y1 = 0, y2 = 0;
  add(t0, len, (t) => {
    const u = t / len; const k = rev ? 1 - u : u;
    const fc = 300 + 3500 * Math.sin(Math.PI * k) ** 2;
    const a = Math.exp(-2 * Math.PI * fc / SR);
    y1 = (1 - a) * rnd() + a * y1; y2 = (1 - a) * y1 + a * y2;
    return (y1 - y2) * 6 * Math.sin(Math.PI * u) ** 2;
  }, g);
}
whoosh(T.CUTS.hookPullBack - 0.2, 1.1, 0.35);
whoosh(T.CUTS.brain - 0.1, 0.9, 0.25);
whoosh(T.CUTS.dots - 0.45, 0.9, 0.3);
whoosh(T.CUTS.question - 0.45, 0.9, 0.3);
whoosh(T.CUTS.logo - 0.45, 0.9, 0.3);

// sub impact
function impact(t0, g) {
  const nz = lpNoise(400);
  add(t0, 2.2, (t) => (Math.sin(2 * Math.PI * (48 - 10 * t) * t) * 0.9 + nz() * 1.5) * Math.exp(-t * 2.6) * Math.min(1, t / 0.01), g);
}
impact(0.0, 0.45);          // cold open hit under the hook text
impact(T.CUTS.question, 0.4);
impact(T.CUTS.logo + 0.1, 0.45);

// reveal: lamp click + bright soft shimmer chord (relief)
add(T.REVEAL.start - 0.15, 0.05, (t) => rnd() * Math.exp(-t * 120), 0.35);
for (const [fq, d] of [[523.25, 0], [659.25, 0.06], [783.99, 0.12], [1046.5, 0.18]]) {
  add(T.REVEAL.start + d, 3.0, (t) => Math.sin(2 * Math.PI * fq * t) * Math.exp(-t * 1.4) * Math.min(1, t / 0.03), 0.06, fq > 700 ? 0.3 : -0.3);
}
// brain: soft electronic blips as the signal lines draw
[16.5, 17.1, 17.7, 18.6].forEach((t0, i) => add(t0, 0.25, (t) => Math.sin(2 * Math.PI * (880 + i * 220) * t) * Math.exp(-t * 18), 0.07, i % 2 ? 0.4 : -0.4));
// dots popping: tiny ticks
for (let i = 0; i < 30; i++) add(21.85 + (i / 30) * 1.6, 0.04, (t) => Math.sin(2 * Math.PI * 2400 * t) * Math.exp(-t * 160), 0.05, rnd() * 0.6);
// face completes: low swell
add(25.4, 2.5, (t) => Math.sin(2 * Math.PI * 110 * t) * Math.sin(Math.PI * t / 2.5) ** 2 * 0.5 + Math.sin(2 * Math.PI * 164.8 * t) * Math.sin(Math.PI * t / 2.5) ** 2 * 0.3, 0.12);
// tension drone during the approach (rises, cut at reveal)
add(6.0, T.REVEAL.start - 6.0, (t) => { const len = T.REVEAL.start - 6; const env = (t / len) ** 1.5 * Math.min(1, (len - t) / 0.05); return (Math.sin(2 * Math.PI * 55 * t) + 0.5 * Math.sin(2 * Math.PI * 82.4 * t + Math.sin(t * 3))) * env; }, 0.12);

// write wav (16-bit)
let peak = 0; for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(Rr[i]));
const norm = peak > 0.95 ? 0.95 / peak : 1;
const buf = Buffer.alloc(44 + N * 4);
buf.write('RIFF', 0); buf.writeUInt32LE(36 + N * 4, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(N * 4, 40);
for (let i = 0; i < N; i++) { buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i] * norm)) * 32767), 44 + i * 4); buf.writeInt16LE(Math.round(Math.max(-1, Math.min(1, Rr[i] * norm)) * 32767), 46 + i * 4); }
fs.writeFileSync(process.argv[2] || 'sfx.wav', buf);
console.log('sfx peak', peak.toFixed(2), 'norm', norm.toFixed(2));
