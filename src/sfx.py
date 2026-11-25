"""Procedural sound design synced to the animation cues. Usage: python sfx.py LANG"""
import json
import math
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

from hm_scenes import END, Cues, block_times, flip_times
from hm_core import clamp

SR = 48000
rng = np.random.default_rng(11)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tl(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR)).astype(np.float32)


def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x).astype(np.float32)


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.where(t < a, t / max(a, 1e-4), np.exp(-(t - a) / d)).astype(np.float32)


def footstep(g=1.0):
    n = noise(0.18)
    x = filt(n, "low", 700) * env_ad(len(n), 0.004, 0.035) * 0.9
    t = tl(0.18)
    x += np.sin(2 * np.pi * 75 * t) * np.exp(-t / 0.05) * 0.6
    x += filt(n, "band", [2000, 5000]) * env_ad(len(n), 0.002, 0.012) * 0.25
    return x * 0.32 * g


def page(d=0.32, g=1.0):
    n = noise(d)
    t = tl(d)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    x = filt(n, "band", [900, 6500]) * e
    crack = (rng.random(len(n)) < 0.004) * rng.standard_normal(len(n))
    x += filt(crack.astype(np.float32), "high", 2500) * 0.8 * e
    return x * 0.16 * g


def pencil(d, g=1.0):
    n = noise(d)
    t = tl(d)
    strokes = np.abs(np.sin(2 * np.pi * 6.5 * t + 1.3 * np.sin(2 * np.pi * 1.7 * t))) ** 3
    x = filt(n, "band", [2500, 8000]) * strokes
    fade = np.minimum(1, np.minimum(t / 0.05, (d - t) / 0.08))
    return x * fade * 0.10 * g


def whoosh(d=0.9, g=1.0):
    n = noise(d)
    t = tl(d)
    u = t / d
    e = np.sin(np.pi * u) ** 2
    lo = filt(n, "band", [180, 900])
    hi = filt(n, "band", [900, 4000])
    mix = np.sin(np.pi * u)  # brighter in the middle
    return (lo * (1 - mix * 0.6) + hi * mix * 0.5) * e * 0.14 * g


def chime(f=880, d=1.6, g=1.0):
    t = tl(d)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (d * dd))
            for m, a, dd in ((1, 1, 0.45), (2.01, 0.35, 0.25), (3.98, 0.15, 0.12)))
    x *= np.minimum(1, t / 0.004)
    return x.astype(np.float32) * 0.07 * g


def tick(f=1200, g=1.0):
    t = tl(0.16)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.035) + 0.4 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / 0.01)
    return (x * np.minimum(1, t / 0.002)).astype(np.float32) * 0.07 * g


def clock_tick(hi=True):
    n = noise(0.05)
    x = filt(n, "band", [2500, 6000] if hi else [1200, 3000]) * env_ad(len(n), 0.0005, 0.006)
    return x * 0.18


def thud(g=1.0):
    t = tl(0.3)
    x = np.sin(2 * np.pi * 58 * t) * np.exp(-t / 0.06) + filt(noise(0.3), "low", 400) * np.exp(-t / 0.03) * 0.5
    return x.astype(np.float32) * 0.25 * g


def swish(g=1.0):
    d = 0.35
    n = noise(d)
    t = tl(d)
    return filt(n, "band", [300, 2200]) * np.sin(np.pi * t / d) ** 2 * 0.10 * g


def boom(g=1.0, d=4.0):
    t = tl(d)
    f = 48 * np.exp(-t / 3) + 30
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 1.2) * np.minimum(1, t / 0.01)
    x += filt(noise(d), "low", 250) * np.exp(-t / 0.5) * 0.4
    return x.astype(np.float32) * 0.35 * g


def riser(d=2.2, g=1.0):
    t = tl(d)
    u = t / d
    f = 180 + 420 * u ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * 0.3 + filt(noise(d), "band", [600, 3500]) * u * 0.5
    return (x * u ** 2 * np.minimum(1, (1 - u) / 0.05 + 0.0)).astype(np.float32) * 0.10 * g


def shimmer(d=1.4, g=1.0):
    out = np.zeros(int(d * SR), np.float32)
    for f in (1318.5, 1760, 2217.5, 2637):
        c = chime(f, d * 0.8, 0.5)
        off = int(rng.random() * 0.25 * SR)
        out[off:off + len(c)] += c[:len(out) - off]
    return out * g


def drone(d):
    t = tl(d)
    x = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t + 1) + 0.25 * np.sin(2 * np.pi * 110.3 * t))
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)
    x += filt(noise(d), "low", 300) * 0.25
    e = np.minimum(1, t / 3.0) * np.minimum(1, (d - t) / 4.0)
    return (x * e).astype(np.float32) * 0.05


def build(lang):
    with open(os.path.join(ROOT, "build", f"cues_{lang}.json"), encoding="utf-8") as f:
        C = Cues(json.load(f), lang)
    S, E, SC = C.S, C.E, C.SC
    out = np.zeros(int((END + 6) * SR), np.float32)

    def put(x, t, g=1.0):
        i = int(t * SR)
        if i < 0:
            x = x[-i:]
            i = 0
        n = min(len(x), len(out) - i)
        out[i:i + n] += x[:n] * g

    # scene 1 — atmosphere, dreams, the choice
    put(drone(16), 0.0)
    d2 = E[1] - S[1]
    for i, f in enumerate((659.3, 784, 987.8, 1318.5)):
        put(chime(f, 1.8, 0.8), S[1] + d2 * (0.05 + 0.25 * i))
    t2 = S[2]
    put(footstep(0.6), t2 + 1.45)
    for n in range(1, 9):
        put(footstep(0.85 * (1 - n / 10)), t2 + 1.95 + n / 1.55)
    put(footstep(1.0), t2 + 1.4 + 0.85)
    put(footstep(1.15), t2 + 3.1)
    put(chime(392, 3.0, 1.2), t2 + 2.9)
    put(chime(587.3, 3.0, 0.6), t2 + 3.0)
    # transitions
    for c in C.cuts:
        put(whoosh(0.9, 0.9), c - 0.5)
    # scene 2 — thinking, Monday circled, weeks flipping by
    d4 = E[3] - S[3]
    for i in range(3):
        put(tick(700 + i * 150, 0.6), S[3] + 0.4 + i * 0.15)
    put(pencil(0.75, 1.3), S[3] + d4 * 0.86)
    for i, ft in enumerate(flip_times(C)):
        put(page(0.3 if i < 8 else 0.2, 1.0 if i < 8 else 0.7), ft - 0.05)
    for k in range(3):
        put(chime(523.3, 1.4, 0.5), S[5] + (E[5] - S[5]) * (0.12 + 0.28 * k))
    # scene 3
    sh = C.shots3
    bt = block_times(S[6] + 2.3, E[6] - 0.2, S[6] + 0.35)
    for i, tb in enumerate(bt):
        put(tick(880 * 2 ** (min(i, 24) / 24), 1.3 if i == 0 else 0.75 / (1 + i * 0.03)), tb)
    for i in range(14):
        put(thud(0.35), sh[1] + 0.05 * i + 0.4)
    put(page(0.5, 1.2), sh[2] + 0.1)
    for tt in (0.5, 1.6):
        put(page(0.35, 1.0), sh[2] + tt)
    k = 0
    tt = sh[3] + 0.1
    while tt < sh[4] - 0.1:
        put(clock_tick(k % 2 == 0), tt)
        tt += 0.5
        k += 1
    tt = sh[4] + 0.3
    while tt < sh[5]:
        put(swish(0.9), tt + 0.1)
        put(swish(0.6), tt + 0.85)
        tt += 1.5
    put(page(0.6, 1.0), sh[5] + 0.05)
    tc = S[12] + (E[12] - S[12]) * 0.62
    put(pencil(max(0.3, tc - 0.15 - (sh[6] + 0.25)), 1.0), sh[6] + 0.25)
    put(pencil(0.45, 1.3), tc)
    put(chime(1046.5, 2.0, 1.1), tc + 0.35)
    # scene 4 — steps of every day
    a0, b0 = SC[3], SC[4]
    N = 44
    t0, D = a0 + 0.4, (b0 - 0.7) - (a0 + 0.4)
    for k in range(N):
        tk = t0 + D * (k / N) ** 0.62
        rate = 1 + k / 8
        put(tick(660 * 2 ** ((k % 12) / 24 + k / 60), 0.9 / rate ** 0.6), tk)
        if k % 2 == 0:
            put(footstep(0.5 / rate ** 0.5), tk + 0.3)
    put(riser(2.4, 1.0), S[15] - 0.6)
    # scene 5 — mirror memories, confidence
    d18 = E[17] - S[17]
    for f in (0.0, 0.26, 0.52, 0.78):
        put(shimmer(1.4, 0.7), S[17] + d18 * f)
    put(riser(2.0, 0.8), S[18] - 0.3)
    put(chime(392, 3.5, 1.0), S[18] + 1.7)
    # scene 6 — the top, the question, the logo
    for n in range(3):
        put(footstep(0.8), SC[5] + 0.2 + (n + 1) * 0.66)
    put(boom(0.6, 4.0), S[20] - 0.1)
    put(boom(0.9, 5.0), C.vo_end + 3.3)
    put(shimmer(2.5, 0.6), C.vo_end + 3.4)
    out = out[:int(END * SR)]
    sf.write(os.path.join(ROOT, "build", f"sfx_{lang}.wav"), out, SR, subtype="FLOAT")
    print(lang, "sfx peak", float(np.abs(out).max()))


if __name__ == "__main__":
    build(sys.argv[1])
