"""Shared procedural synth (instruments, Track, reverb, write) extracted from episode 1. Set SYNTH_DUR before import."""
import numpy as np, wave, os
SR = 44100; DUR = float(os.environ.get("SYNTH_DUR", "120")); N = int(SR * DUR)
rs = np.random.default_rng(7)
here = os.path.dirname(os.path.abspath(__file__))

def tt(d): return np.arange(int(d * SR)) / SR
def hz(n): return 440.0 * 2 ** ((n - 69) / 12)            # midi -> Hz
def note(name):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    return names[name[:-1]] + 12 * (int(name[-1]) + 1)
def saw(f, t): return 2 * ((f * t) % 1.0) - 1
def lp(x, fc):  # brick-ish FFT low-pass with soft knee
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def env(n, a=0.01, r=0.2, s=1.0):
    e = np.ones(n) * s; na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, s, na)[:n] if na <= n else np.linspace(0, s, n)[:]
    if nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e
class Track:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def add(s, x, t0, gain=1.0, pan=0.0):
        i = int(t0 * SR); x = x[: max(0, N - i)]
        if i < 0: x = x[-i:]; i = 0
        s.L[i:i + len(x)] += x * gain * np.sqrt((1 - pan) / 2) * 1.414
        s.R[i:i + len(x)] += x * gain * np.sqrt((1 + pan) / 2) * 1.414

# ---------------- instruments ----------------
def pad(notes, d, cutoff=1400, a=0.8, r=1.0):
    t = tt(d); x = np.zeros(len(t))
    for n in notes:
        f = hz(n)
        for det in (-0.12, 0, 0.12): x += saw(f * 2 ** (det / 12), t + rs.random())
    x = lp(x / (3 * len(notes)), cutoff); return x * env(len(t), a, r)
def piano(n, d=2.5, vel=1.0):
    t = tt(d); f = hz(n)
    x = sum(np.sin(2 * np.pi * f * k * t) * (0.6 ** k) * np.exp(-t * (2.2 + k * 1.3)) for k in range(1, 6))
    return x * env(len(t), 0.003, 0.3) * vel * 0.6
def pluck(n, d=0.35, bright=3000):
    t = tt(d); x = (saw(hz(n), t) + 0.5 * saw(hz(n) * 1.005, t)) * np.exp(-t * 9)
    return lp(x, bright) * env(len(t), 0.002, 0.05) * 0.5
def bass(n, d=0.24):
    t = tt(d); x = saw(hz(n), t) + np.sin(2 * np.pi * hz(n) * t)
    return lp(x, 500) * env(len(t), 0.005, 0.06) * 0.6
def kick(d=0.45):
    t = tt(d); f = 45 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) * 1.0
def boom(d=2.5):
    t = tt(d); f = 32 + 80 * np.exp(-t * 9); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 1.8) + lp(rs.standard_normal(len(t)), 400) * 0.25 * np.exp(-t * 3)) * 1.2
def snare(d=0.25):
    t = tt(d); return (hp(rs.standard_normal(len(t)), 1500) * 0.5 + np.sin(2 * np.pi * 190 * t) * 0.5) * np.exp(-t * 18)
def hat(d=0.06):
    t = tt(d); return hp(rs.standard_normal(len(t)), 7000) * np.exp(-t * 60) * 0.35
def taiko(d=0.8):
    t = tt(d); f = 70 + 60 * np.exp(-t * 20); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + lp(rs.standard_normal(len(t)), 900) * 0.4) * np.exp(-t * 6)
def riser(d, f0=200, f1=4000):
    t = tt(d); x = hp(lp(rs.standard_normal(len(t)), f1), f0) * np.linspace(0, 1, len(t)) ** 2
    sw = np.sin(2 * np.pi * np.cumsum(np.geomspace(f0, f1, len(t))) / SR) * 0.15 * np.linspace(0, 1, len(t)) ** 3
    return x * 0.5 + sw
def whoosh(d=0.7):
    t = tt(d); x = rs.standard_normal(len(t)); X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    x = np.fft.irfft(X * np.exp(-((np.log(f + 1) - np.log(1500)) ** 2)), len(x)); e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return x * e * 2.0
def bell(n, d=1.6):
    t = tt(d); f = hz(n)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 3) * 0.5
def ping(hi=88, d=0.5): return bell(hi, d) * 0.8 + bell(hi + 7, d) * 0.4
def click(d=0.03): t = tt(d); return hp(rs.standard_normal(len(t)), 3000) * np.exp(-t * 250) * 0.8
def key(d=0.05): t = tt(d); return (hp(rs.standard_normal(len(t)), 2000) * 0.6 + np.sin(2 * np.pi * 1800 * t) * 0.2) * np.exp(-t * 120)
def tick(d=0.04): t = tt(d); return (np.sin(2 * np.pi * 3200 * t) + hp(rs.standard_normal(len(t)), 4000) * 0.5) * np.exp(-t * 150) * 0.6
def noise_bed(d, lo, hi): return hp(lp(rs.standard_normal(int(d * SR)), hi), lo)
def heartbeat(): return np.concatenate([kick(0.18) * 0.9, np.zeros(int(0.08 * SR)), kick(0.25) * 0.6])
def beep(f=1000, d=0.18): t = tt(d); return np.sign(np.sin(2 * np.pi * f * t)) * 0.25 * env(len(t), 0.005, 0.02)

def chords_pad(track, t0, t1, prog, bar, cutoff=1400, gain=0.5, octave_up=False):
    t = t0; i = 0
    while t < t1 - 0.05:
        d = min(bar, t1 - t) + 0.8; track.add(pad(prog[i % len(prog)], d, cutoff, a=0.25, r=0.8), t, gain, pan=0.0); t += bar; i += 1

# ---------------- reverb + master ----------------
def reverb(x, secs=2.2, wet=0.25):
    ir = rs.standard_normal(int(secs * SR)) * np.exp(-np.linspace(0, 7, int(secs * SR))); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    n = len(x) + len(ir); nf = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[: len(x)]
    return x * (1 - wet) + y * wet * 3
def write(path, tr, wet):
    L, R = reverb(tr.L, wet=wet), reverb(tr.R, wet=wet)
    fade = np.ones(N); fade[-int(1.0 * SR):] = np.linspace(1, 0, int(1.0 * SR)) ** 2
    st = np.stack([L * fade, R * fade], 1); st = np.tanh(st / (np.abs(st).max() * 0.9) * 1.2) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
