"""Synthesizes the 90s soundtrack (music + sound effects) and mixes it with the narration.

Usage: python3 audio.py <voice.mp3> <out.wav>
"""
import subprocess
import sys

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 90.0
N = int(SR * DUR)
rng = np.random.default_rng(7)


def tt(d):
    return np.arange(int(d * SR)) / SR


def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output='sos')
    return sosfilt(sos, x)


def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def plus(*xs):
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[: len(x)] += x
    return out


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


# ---------------- music ----------------
def music():
    out = np.zeros(N + SR)
    beat = 60 / 84
    bar = beat * 4
    chords = [([50, 53, 57, 60, 64], 38), ([46, 50, 53, 57, 60], 34), ([53, 57, 60, 64], 41), ([48, 52, 55, 62], 36)]
    nbars = int(DUR / bar) + 2
    for b in range(nbars):
        notes, root = chords[b % 4]
        t0 = b * bar
        # pad
        d = bar + 0.8
        t = tt(d)
        e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
        pad = np.zeros_like(t)
        for m in notes:
            f = mtof(m)
            for det in (-0.12, 0.12):
                ff = f * 2 ** (det / 12)
                pad += 2 * ((ff * t) % 1) - 1
        pad = filt(pad, 'low', 1100) * e / len(notes)
        add(out, t0, pad, 0.22)
        # bass
        for k, off in enumerate((0, 2, 2.5)):
            bt = tt(beat * 1.4)
            f = mtof(root)
            s = (np.sin(2 * np.pi * f * bt) + 0.3 * np.sin(4 * np.pi * f * bt)) * env_ad(len(bt), 0.01, 0.45)
            add(out, t0 + off * beat, s, 0.35)
        # e-piano arpeggio (FM)
        pat = [0, 2, 1, 3, 2, 1, 3, 2]
        for k in range(8):
            m = notes[pat[k] % len(notes)] + 12
            f = mtof(m)
            nt = tt(1.2)
            idx = 1.8 * np.exp(-nt * 7)
            s = np.sin(2 * np.pi * f * nt + idx * np.sin(2 * np.pi * f * nt)) * env_ad(len(nt), 0.004, 0.5)
            add(out, t0 + k * beat / 2, s, 0.12 if k % 2 else 0.16)
        # drums from bar 1
        if b >= 1:
            for k in range(4):
                if k in (0, 2):
                    kt = tt(0.35)
                    f = 50 + 90 * np.exp(-kt * 30)
                    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 9)
                    add(out, t0 + k * beat, s, 0.55)
                if k in (1, 3):
                    st = tt(0.25)
                    s = filt(rng.standard_normal(len(st)), 'band', [900, 5000]) * np.exp(-st * 18) + 0.4 * np.sin(2 * np.pi * 190 * st) * np.exp(-st * 25)
                    add(out, t0 + k * beat, s, 0.22)
            for k in range(8):
                ht = tt(0.06)
                s = filt(rng.standard_normal(len(ht)), 'high', 7000) * np.exp(-ht * 70)
                add(out, t0 + k * beat / 2, s, 0.09 if k % 2 else 0.05)
    out = out[:N]
    out = filt(out, 'low', 6500)
    # tape wow & flutter
    t = np.arange(N) / SR
    warp = t + 0.0018 * np.sin(2 * np.pi * 0.55 * t) + 0.0003 * np.sin(2 * np.pi * 6.0 * t)
    out = np.interp(warp * SR, np.arange(N), out)
    return out / np.max(np.abs(out))


# ---------------- sound effects ----------------
def bell_strikes(dur, rate, partials, decay=0.03):
    s = np.zeros(int(dur * SR) + SR // 4)
    n = int(dur * rate)
    for i in range(n):
        st = tt(0.12)
        hit = sum(np.sin(2 * np.pi * p * st) / (k + 1) for k, p in enumerate(partials)) * np.exp(-st / decay)
        add(s, i / rate, hit, 1.0 if i % 2 else 0.8)
    return s


def noise(d):
    return rng.standard_normal(int(d * SR))


def click(gain=1.0, f=2500, d=0.03):
    st = tt(d)
    return (filt(noise(d), 'band', [f * 0.5, min(f * 2, 18000)]) * np.exp(-st * 200) + 0.5 * np.sin(2 * np.pi * f / 3 * st) * np.exp(-st * 120)) * gain


def thump(f=80, d=0.25):
    st = tt(d)
    fr = f + f * np.exp(-st * 25)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-st * 14) + 0.2 * filt(noise(d), 'low', 600) * np.exp(-st * 30)


def chirp_bird(d=0.12):
    st = tt(d)
    f = 3200 + 1600 * np.sin(np.pi * st / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * st / d)


def car_pass(d=3.0, f0=70):
    st = tt(d)
    e = np.exp(-((st - d / 2) / (d / 5)) ** 2)
    f = f0 * (1.08 - 0.16 * (st / d))
    eng = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    tyre = filt(noise(d), 'band', [300, 2500])
    return (eng * 0.6 + tyre * 0.6) * e


def sfx():
    s = np.zeros(N + SR * 2)
    # room tone & tape hiss everywhere
    add(s, 0, filt(noise(DUR), 'high', 3000), 0.006)
    # 1: alarm clock
    add(s, 0.25, bell_strikes(2.15, 24, [2350, 3480, 5210]), 0.16)
    add(s, 2.42, click(1.0, 1800), 0.25)
    # ticking clock close-up
    for k in range(4):
        add(s, 9.4 + k * 0.5, click(1.0, 4000, 0.02), 0.12)
    # TV close-up: static then test tone
    add(s, 10.7, filt(noise(0.6), 'band', [500, 9000]) * np.linspace(1, 0.3, int(0.6 * SR)), 0.08)
    add(s, 11.3, np.sin(2 * np.pi * 1000 * tt(1.5)) * np.minimum(1, tt(1.5) / 0.05), 0.02)
    add(s, 10.7, np.sin(2 * np.pi * 9800 * tt(2.1)), 0.004)
    # footsteps
    def steps(t0, t1, period, g=0.18):
        t = t0
        while t < t1:
            add(s, t, plus(thump(110, 0.12), 0.3 * click(1, 1200, 0.03)), g)
            t += period
    steps(12.95, 14.85, np.pi / 9)
    steps(18.5, 20.1, np.pi / 9)
    # kettle hiss + soft whistle
    k = tt(4.6)
    add(s, 18.45, filt(noise(4.6), 'band', [2000, 6000]) * np.minimum(1, k / 1.0), 0.02)
    w = tt(1.3)
    add(s, 21.8, np.sin(2 * np.pi * (2100 + 30 * np.sin(2 * np.pi * 6 * w)) * w) * np.minimum(1, w / 0.4) * np.minimum(1, (1.3 - w) / 0.2), 0.03)
    # door creak and slam
    d = tt(0.9)
    add(s, 25.9, np.sign(np.sin(2 * np.pi * np.cumsum(180 + 120 * d) / SR)) * filt(noise(0.9), 'low', 3000) * np.sin(np.pi * d / 0.9), 0.05)
    add(s, 27.55, thump(60, 0.4), 0.35)
    # street ambience
    amb = filt(noise(12.8), 'low', 400)
    amb = amb / np.max(np.abs(amb))
    add(s, 25.85, amb * np.minimum(1, tt(12.8) / 0.6) * np.minimum(1, (12.8 - tt(12.8)) / 0.4), 0.12)
    for bt in (26.4, 26.7, 27.9, 31.2, 33.7, 34.1, 36.8, 37.3):
        add(s, bt, chirp_bird(0.1), 0.03)
    for ct, f0, g in ((27.2, 70, 0.3), (28.6, 85, 0.3), (29.6, 60, 0.4), (31.4, 75, 0.2), (34.2, 80, 0.2), (36.0, 70, 0.18)):
        add(s, ct, car_pass(2.6, f0), g)
    h = tt(0.45)
    add(s, 30.1, (np.sign(np.sin(2 * np.pi * 350 * h)) + np.sign(np.sin(2 * np.pi * 440 * h))) * np.minimum(1, (0.45 - h) / 0.05), 0.025)
    # crowd murmur
    m = filt(noise(5.0), 'band', [250, 1200])
    mod = 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 3.1 * tt(5.0))) * np.abs(np.sin(2 * np.pi * 1.7 * tt(5.0) + 1))
    add(s, 30.6, m * mod * np.minimum(1, tt(5.0) / 0.5) * np.minimum(1, (5.0 - tt(5.0)) / 0.5), 0.05)
    # rotary dial: wind (ratchet) and return clicks
    for cyc in range(2):
        c0 = 38.62 + cyc * 1.3
        for i in range(6):
            add(s, c0 + 0.05 + i * 0.09, click(1, 3000, 0.015), 0.1)
        for i in range(7):
            add(s, c0 + 0.6 + i * 0.07, click(1, 1500, 0.02), 0.16)
    # ringback tones (phone line, band-limited)
    for rt in (41.6, 42.5, 43.4):
        r = tt(0.7)
        tone = np.sin(2 * np.pi * 425 * r) * np.minimum(1, r / 0.02) * np.minimum(1, (0.7 - r) / 0.02)
        add(s, rt, filt(tone, 'band', [300, 3400]), 0.07)
    # shop: abacus clicks and register bell
    for i in range(6):
        add(s, 45.3 + i * 0.11, click(1, 1800, 0.02), 0.12)
    add(s, 46.5, bell_strikes(0.05, 20, [2600, 3900, 5200], 0.35), 0.14)
    # walkman
    add(s, 49.1, plus(click(1, 2200, 0.04), click(0.6, 900, 0.03)), 0.35)
    add(s, 50.75, filt(noise(0.15), 'band', [600, 4000]) * np.exp(-tt(0.15) * 20), 0.15)
    add(s, 51.0, plus(click(1, 1600, 0.05), thump(150, 0.08)), 0.4)
    add(s, 51.55, click(1, 1100, 0.05), 0.3)
    mt = tt(6.8)
    add(s, 51.6, np.sin(2 * np.pi * (118 + 2 * np.sin(2 * np.pi * 7 * mt)) * mt) * np.minimum(1, mt / 0.2), 0.006)
    # yard: birds, bike bell, freewheel, ball kicks, swing creak
    for bt in np.arange(58.6, 66.0, 0.85):
        add(s, bt + rng.random() * 0.3, chirp_bird(0.09), 0.025)
    add(s, 61.9, bell_strikes(0.12, 16, [3100, 4300], 0.12), 0.12)
    for i in range(int(2.2 / 0.045)):
        add(s, 61.7 + i * 0.045, click(1, 5000, 0.008), 0.03)
    for kt in (64.17, 65.0, 65.83):
        add(s, kt, thump(140, 0.15), 0.3)
    # evening crickets
    for i in range(int(3.0 / 0.4)):
        cr = tt(0.12)
        add(s, 66.2 + i * 0.4, np.sin(2 * np.pi * 4700 * cr) * (np.sin(2 * np.pi * 45 * cr) > 0) * np.sin(np.pi * cr / 0.12), 0.02)
    # TV on
    add(s, 69.35, plus(click(1, 900, 0.06), thump(90, 0.15)), 0.4)
    add(s, 69.4, filt(noise(0.6), 'band', [400, 9000]) * np.linspace(1, 0.2, int(0.6 * SR)), 0.12)
    add(s, 69.4, np.sin(2 * np.pi * 10200 * tt(7.3)) * np.minimum(1, tt(7.3) / 0.1), 0.004)
    # clock ticks speeding up
    t = 76.8
    gap = 0.25
    while t < 78.25:
        add(s, t, click(1, 3800, 0.02), 0.13)
        t += gap
        gap = max(0.03, gap * 0.85)
    # alarm again
    add(s, 78.35, bell_strikes(0.8, 24, [2350, 3480, 5210]), 0.12)
    # page flip whoosh
    pf = tt(0.6)
    add(s, 81.0, filt(noise(0.6), 'band', [800, 6000]) * np.sin(np.pi * pf / 0.6) ** 2, 0.12)
    # title impact
    add(s, 84.0, thump(45, 1.6), 0.5)
    add(s, 84.0, filt(noise(1.2), 'low', 1500) * np.exp(-tt(1.2) * 4), 0.15)
    # tape stop
    ts = tt(0.6)
    add(s, 89.4, np.sin(2 * np.pi * np.cumsum(300 * (1 - ts / 0.6)) / SR) * (1 - ts / 0.6), 0.08)
    # VHS glitch bursts (match the picture)
    for gt, a in [(0.05, 1), (18.45, 0.8), (25.85, 0.8), (38.62, 0.7), (45.0, 0.6), (48.1, 0.6), (58.35, 0.8), (66.15, 0.8), (76.75, 1), (78.3, 0.9), (81.1, 1.4), (84.0, 1.2), (89.7, 1.2)]:
        g = tt(0.3)
        burst = filt(noise(0.3), 'band', [300, 8000]) * np.exp(-((g - 0.15) / 0.08) ** 2)
        burst += 0.4 * np.sin(2 * np.pi * 60 * g) * np.exp(-((g - 0.15) / 0.08) ** 2)
        add(s, max(0, gt - 0.15), burst, 0.06 * a)
    return s[:N]


def music_gain():
    t = np.arange(N) / SR
    g = np.full(N, 0.13)
    def seg(a, b, v, fade=0.4):
        nonlocal g
        w = np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)
        g = g * (1 - w) + v * w
    seg(0, 3.0, 0.05)        # alarm takes over first
    seg(23.0, 25.9, 0.0, 0.2)  # radio has its own version
    seg(51.5, 58.3, 0.26)    # cassette plays
    seg(84.0, 90.5, 0.24)
    g[t > 89.4] *= np.clip(1 - (t[t > 89.4] - 89.4) / 0.5, 0, 1)
    return g


def main():
    voice_path, out_path = sys.argv[1], sys.argv[2]
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', voice_path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    voice = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    v = np.zeros(N)
    v[: min(N, len(voice))] = voice[:N]
    v = v / np.max(np.abs(v)) * 0.85

    mus = music()
    radio = filt(mus, 'band', [400, 3000], 4)
    r = np.zeros(N)
    a, b = int(23.0 * SR), int(25.9 * SR)
    seg = radio[a:b] + 0.15 * filt(rng.standard_normal(b - a), 'band', [1000, 6000]) * np.exp(-np.arange(b - a) / SR / 0.3)
    fade = np.minimum(1, np.arange(b - a) / (0.2 * SR)) * np.minimum(1, (b - a - np.arange(b - a)) / (0.2 * SR))
    r[a:b] = seg * fade * 0.2

    # duck music slightly under speech
    env = np.convolve(np.abs(v), np.ones(4410) / 4410, mode='same')
    duck = 1 - 0.35 * np.clip(env / 0.08, 0, 1)
    mix = v + mus * music_gain() * duck + r + sfx()
    mix = filt(mix, 'high', 40)
    mix = filt(mix, 'low', 14000)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / np.max(np.abs(mix)) * 0.95
    st = np.stack([mix, mix], axis=1)
    pcm = (st * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', out_path], input=pcm.tobytes(), check=True)


if __name__ == '__main__':
    main()
