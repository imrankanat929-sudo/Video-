"""Music + sound-effects bed synthesized with numpy (no voice).
Kept quiet (peaks around -9 dBFS) so the voice-over sits on top."""
import math
import wave
import numpy as np

SR = 44100


def _t(n):
    return np.arange(n) / SR


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / np.sqrt(1 + (f / hi) ** 4)) * (1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4))
    return np.fft.irfft(X, len(x))


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def add(self, t0, sig, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if i >= self.n:
            return
        sig = sig[: self.n - i]
        gl = gain * math.cos((pan + 1) * math.pi / 4)
        gr = gain * math.sin((pan + 1) * math.pi / 4)
        self.L[i:i + len(sig)] += sig * gl
        self.R[i:i + len(sig)] += sig * gr


rng = np.random.default_rng(3)


def tick(vol=1.0):
    n = int(0.05 * SR)
    t = _t(n)
    s = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 180) + rng.normal(0, 0.3, n) * np.exp(-t * 400)
    return s * vol


def ding(freq=1318.5, dur=0.9):
    n = int(dur * SR)
    t = _t(n)
    s = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.01 * t)) * np.exp(-t * 6)
    return s * env(n, 0.002, 0.05)


def buzz(dur=0.28):
    n = int(dur * SR)
    t = _t(n)
    s = np.sign(np.sin(2 * np.pi * 165 * t)) * 0.5 + np.sin(2 * np.pi * 82 * t)
    s *= 0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)
    return lowpass(s, 900) * env(n, 0.01, 0.04)


def whoosh(dur=0.7, up=True):
    n = int(dur * SR)
    t = _t(n)
    s = bandpass(rng.normal(0, 1, n), 300, 3000)
    shape = np.sin(np.pi * t / dur) ** 2
    return s * shape * 0.6


def boom(dur=3.0, f=48):
    n = int(dur * SR)
    t = _t(n)
    pitch = f * (1 + 1.5 * np.exp(-t * 8))
    ph = 2 * np.pi * np.cumsum(pitch) / SR
    s = np.sin(ph) * np.exp(-t * 1.6) + lowpass(rng.normal(0, 1, n), 400) * np.exp(-t * 5) * 0.8
    return s * env(n, 0.003, 0.4)


def bell(dur=5.0, f=196.0):
    n = int(dur * SR)
    t = _t(n)
    partials = [(1, 1), (2.0, 0.6), (2.4, 0.4), (3.0, 0.3), (4.2, 0.2), (5.4, 0.12)]
    s = sum(a * np.sin(2 * np.pi * f * p * t) * np.exp(-t * (0.6 + p * 0.3)) for p, a in partials)
    return s * env(n, 0.004, 0.5) / 2


def heartbeat():
    n = int(0.5 * SR)
    t = _t(n)
    one = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 18)
    s = one.copy()
    k = int(0.18 * SR)
    s[k:] += one[: n - k] * 0.7
    return s


def creak(dur):
    n = int(dur * SR)
    t = _t(n)
    f = 260 + 120 * np.sin(2 * np.pi * 0.35 * t) + 40 * np.sin(2 * np.pi * 2.1 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    grains = (np.sin(2 * np.pi * 14 * t) > 0.2).astype(float) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t))
    s = bandpass(saw, 300, 2200) * grains
    return s * env(n, 0.3, 0.8)


def pad(dur, notes, vol=1.0, bright=900):
    n = int(dur * SR)
    t = _t(n)
    s = np.zeros(n)
    for i, f in enumerate(notes):
        for det in (-0.6, 0.6):
            ph = 2 * np.pi * (f + det) * t + i
            saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
            s += saw
    s = lowpass(s / (len(notes) * 2), bright)
    return s * vol


def render(path, ep):
    dur = ep.DURATION
    m = Mix(dur)
    n = m.n
    t = _t(n)

    # 1) low drone over everything + wind
    drone = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 82.4 * t) * 0.3
             + np.sin(2 * np.pi * 110.3 * t) * 0.2) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t))
    wind = lowpass(rng.normal(0, 1, n), 350) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t + 1))
    wind /= np.abs(wind).max() + 1e-9
    m.add(0, drone, 0.10)
    m.add(0, wind, 0.06, -0.2)
    m.add(0, wind[::-1].copy(), 0.06, 0.2)

    # 2) "frozen time" shimmer during the first scene
    sh_n = int(22.5 * SR)
    st = _t(sh_n)
    shimmer = sum(np.sin(2 * np.pi * f * st) for f in (1760, 2217, 2637)) / 3
    shimmer *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * st)) * env(sh_n, 1.5, 2.5)
    m.add(0, shimmer, 0.02)

    # 3) music: each scene builds to its end, then drops
    scenes = [(0.0, 22.3, [110, 130.8, 164.8]),          # Am
              (22.3, 50.2, [98, 123.5, 146.8]),         # G-ish / tension
              (50.2, 69.1, [87.3, 110, 130.8]),         # F
              (69.1, 91.8, [82.4, 103.8, 123.5]),       # E (dominant, tension)
              (91.8, ep.BLACK_T, [110, 130.8, 155.6])]  # Am(b5) darker
    for a, b, notes in scenes:
        d = b - a
        nn = int(d * SR)
        e = np.linspace(0.25, 1.0, nn) ** 2 * env(nn, 1.0, 0.25)
        m.add(a, pad(d, notes, 1.0, 500 + 900 * (a / dur)) * e, 0.16)
        # soft pulse in the second half of tense scenes
        if a >= 50:
            k = a + d * 0.45
            while k < b - 0.3:
                m.add(k, heartbeat(), 0.22)
                k += 0.86 if a < 91 else 0.78

    # 4) whooshes on cuts
    for a, b, fn in ep.SHOTS[1:]:
        m.add(a - 0.35, whoosh(0.7), 0.10, rng.uniform(-0.4, 0.4))

    # 5) wall clock tries to tick but never moves
    k = 29.5
    while k < 36.6:
        m.add(k, tick(0.9), 0.25)
        k += 1.0

    # 6) all phones light up + chorus of notifications
    m.add(ep.LIGHT_T - 0.05, whoosh(0.5), 0.2)
    for i in range(14):
        m.add(ep.LIGHT_T + rng.uniform(0, 0.7), ding(rng.choice([1046.5, 1318.5, 1568, 1760])), 0.06,
              rng.uniform(-0.9, 0.9))
    m.add(ep.BUZZ_T, buzz(), 0.35)
    m.add(ep.BUZZ_T + 0.4, buzz(), 0.35)

    # 7) messages
    m.add(ep.MSG1_T, ding(987.8, 1.4), 0.22)
    m.add(ep.MSG1_T, boom(1.5, 70), 0.25)
    m.add(ep.MSG2_T, ding(932.3, 1.4), 0.22)
    m.add(ep.MSG2_T, boom(2.0, 55), 0.35)
    gl = bandpass(rng.normal(0, 1, int(0.4 * SR)), 1500, 6000) * env(int(0.4 * SR), 0.0, 0.2)
    m.add(ep.MSG2_T, gl, 0.12)

    # 8) clock tower starts: bell + fast ticking
    m.add(ep.TOWER_T, bell(6.0, 130.8), 0.35)
    m.add(ep.TOWER_T, boom(2.0, 45), 0.25)
    k = ep.TOWER_T + 0.5
    while k < 86.3:
        m.add(k, tick(1.0), 0.22, 0.1)
        k += 0.5

    # 9) the door opens by itself
    m.add(ep.DOOR_T0, creak(ep.DOOR_T1 - ep.DOOR_T0), 0.18, 0.15)
    m.add(ep.DOOR_T1 - 0.2, boom(1.5, 60), 0.15)

    # 10) final accent and darkness
    m.add(ep.BLACK_T, boom(3.2, 42), 0.6)
    fade_i = int(ep.BLACK_T * SR)
    fade = np.ones(n)
    fade[fade_i:] = np.exp(-np.arange(n - fade_i) / SR * 6)
    bed_L = m.L * fade
    bed_R = m.R * fade
    # re-add the boom tail unfaded
    tail = boom(3.2, 42) * 0.6
    end = min(n, fade_i + len(tail))
    bed_L[fade_i:end] = bed_L[fade_i:end] * 0 + tail[: end - fade_i] * 0.707
    bed_R[fade_i:end] = bed_R[fade_i:end] * 0 + tail[: end - fade_i] * 0.707
    # fades in/out and normalization (peak -9 dBFS)
    ramp = int(0.3 * SR)
    for ch in (bed_L, bed_R):
        ch[:ramp] *= np.linspace(0, 1, ramp)
        ch[-ramp:] *= np.linspace(1, 0, ramp)
    peak = max(np.abs(bed_L).max(), np.abs(bed_R).max())
    g = 10 ** (-9 / 20) / peak
    st = np.stack([bed_L * g, bed_R * g], 1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path
