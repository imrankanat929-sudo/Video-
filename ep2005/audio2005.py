"""Soundtrack for episode 2 (2005): 2000s-style original music, SFX, narration mix.

Usage: python3 audio2005.py <voice.mp3> <out_dir>
Writes mix.wav, music.wav and sfx.wav into out_dir.
"""
import importlib.util
import os
import subprocess
import sys

import numpy as np

spec = importlib.util.spec_from_file_location('base', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'audio.py'))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
SR, DUR, N = base.SR, base.DUR, base.N
tt, filt, add, plus, env_ad, mtof, noise, click, thump, bell_strikes, chirp_bird, car_pass = (
    base.tt, base.filt, base.add, base.plus, base.env_ad, base.mtof, base.noise, base.click, base.thump, base.bell_strikes, base.chirp_bird, base.car_pass)
rng = np.random.default_rng(11)


def music():
    out = np.zeros(N + SR)
    beat = 60 / 100
    bar = beat * 4
    chords = [([57, 60, 64, 69], 45), ([53, 57, 60, 65], 41), ([48, 52, 55, 60], 36), ([55, 59, 62, 67], 43)]
    for b in range(int(DUR / bar) + 2):
        notes, root = chords[b % 4]
        t0 = b * bar
        d = bar + 0.5
        t = tt(d)
        pad = sum(np.sin(2 * np.pi * mtof(m) * t) + 0.5 * np.sin(4 * np.pi * mtof(m) * t + 0.3) for m in notes) / len(notes)
        pump = 0.55 + 0.45 * np.clip((t % beat) / (beat * 0.6), 0, 1)
        add(out, t0, pad * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.5) * pump, 0.16)
        for k in range(8):
            bt = tt(beat / 2)
            s = (2 * ((mtof(root) * bt) % 1) - 1)
            s = base.filt(s, 'low', 600) * env_ad(len(bt), 0.005, 0.18)
            add(out, t0 + k * beat / 2, s, 0.4)
        pat = [0, 2, 1, 3, 2, 3, 1, 2, 0, 2, 1, 3, 2, 3, 1, 3]
        for k in range(16):
            m = notes[pat[k] % len(notes)] + 12
            nt = tt(0.3)
            s = (2 * ((mtof(m) * nt) % 1) - 1) + 0.6 * (2 * ((mtof(m) * 1.005 * nt) % 1) - 1)
            s = base.filt(s, 'low', 3500) * env_ad(len(nt), 0.002, 0.09)
            add(out, t0 + k * beat / 4, s, 0.09 if k % 2 else 0.12)
        if b >= 1:
            for k in range(4):
                kt = tt(0.3)
                f = 48 + 110 * np.exp(-kt * 35)
                add(out, t0 + k * beat, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 10), 0.5)
                if k in (1, 3):
                    ct = tt(0.2)
                    add(out, t0 + k * beat, filt(noise(0.2), 'band', [1000, 6000]) * np.exp(-ct * 22), 0.24)
                ht = tt(0.12)
                add(out, t0 + k * beat + beat / 2, filt(noise(0.12), 'high', 7000) * np.exp(-ht * 25), 0.07)
    out = filt(out[:N], 'low', 9000)
    return out / np.max(np.abs(out))


def tone(f, d, g=1.0):
    t = tt(d)
    return np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.01) * g


def dtmf(key, d=0.1):
    rows = {1: 697, 2: 697, 3: 697, 4: 770, 5: 770, 6: 770, 7: 852, 8: 852, 9: 852, 0: 941}
    cols = {1: 1209, 2: 1336, 3: 1477, 4: 1209, 5: 1336, 6: 1477, 7: 1209, 8: 1336, 9: 1477, 0: 1336}
    return tone(rows[key], d, 0.5) + tone(cols[key], d, 0.5)


def ringtone(dur):
    melody = [76, 74, 66, 68, 73, 71, 62, 64, 71, 69, 61, 64, 69]
    out = np.zeros(int(dur * SR) + SR)
    step = 0.14
    for i in range(int(dur / step)):
        m = melody[i % len(melody)]
        t = tt(step * 0.9)
        s = np.sign(np.sin(2 * np.pi * mtof(m) * t)) * np.minimum(1, (step * 0.9 - t) / 0.01)
        add(out, i * step, s, 1)
    return filt(out[: int(dur * SR)], 'low', 5000)


def sfx():
    s = np.zeros(N + SR * 2)
    add(s, 0, filt(noise(DUR), 'low', 300), 0.004)
    add(s, 0.2, bell_strikes(2.1, 24, [2350, 3480, 5210]), 0.15)
    add(s, 2.32, click(1.0, 1800), 0.25)
    for pt in (4.35, 12.3, 75.45):
        add(s, pt, plus(thump(70, 0.5), 0.3 * filt(noise(0.3), 'band', [2000, 8000]) * np.exp(-tt(0.3) * 12)), 0.3)
    cdw = tt(1.2)
    add(s, 8.7, filt(noise(1.2), 'band', [1500, 4000]) * np.sin(np.pi * cdw / 1.2) + 0.4 * np.sin(2 * np.pi * (300 + 400 * cdw) * cdw) * np.sin(np.pi * cdw / 1.2), 0.04)
    vb = tt(0.8)
    add(s, 10.25, np.sign(np.sin(2 * np.pi * 150 * vb)) * (np.sin(2 * np.pi * 4 * vb) > 0), 0.03)
    add(s, 10.3, ringtone(1.1), 0.05)
    t = 14.4
    while t < 15.75:
        add(s, t, plus(thump(110, 0.12), 0.3 * click(1, 1200, 0.03)), 0.18); t += np.pi / 9
    add(s, 16.55, plus(click(1, 1500, 0.05), thump(160, 0.08)), 0.45)
    fan = tt(9.2)
    add(s, 16.6, (filt(noise(9.2), 'low', 900) + 0.3 * np.sin(2 * np.pi * 120 * fan)) * np.minimum(1, fan / 0.8), 0.025)
    for i in range(14):
        add(s, 16.8 + rng.random() * 2.6, click(1, 3500, 0.015), 0.08)
    add(s, 17.65, tone(1000, 0.2), 0.06)
    for k, m in enumerate([64, 71, 76, 78, 83]):
        ct = tt(2.4)
        add(s, 19.6 + k * 0.12, (np.sin(2 * np.pi * mtof(m) * ct) + 0.3 * np.sin(4 * np.pi * mtof(m) * ct)) * np.minimum(1, ct / 0.05) * np.exp(-ct * 1.4), 0.05)
    for k, key in enumerate([8, 0, 0, 5, 5, 5, 1]):
        add(s, 21.9 + k * 0.11, dtmf(key, 0.08), 0.05)
    md = tt(1.0)
    hand = np.where((md * 7).astype(int) % 2 == 0, np.sin(2 * np.pi * 1200 * md), np.sin(2 * np.pi * 2100 * md)) + 0.8 * filt(noise(1.0), 'band', [800, 3500])
    add(s, 22.75, hand * np.minimum(1, md / 0.05) * np.minimum(1, (1.0 - md) / 0.1), 0.035)
    t = 23.8
    while t < 25.7:
        add(s, t, click(1, 2800, 0.02), 0.09); t += 0.08 + rng.random() * 0.06
    for mt in (24.2, 24.9, 25.4):
        add(s, mt, click(1, 4000, 0.015), 0.12)
    for k, key in enumerate([4, 1, 7, 5]):
        add(s, 31.6 + k * 0.25, dtmf(key, 0.12), 0.05)
    add(s, 32.2, ringtone(1.6), 0.05)
    add(s, 35.6, click(1, 2200, 0.03), 0.2)
    add(s, 38.0, click(1, 3000, 0.02), 0.2)
    add(s, 40.15, tone(1400, 0.12), 0.04); add(s, 40.3, tone(1400, 0.12), 0.04); add(s, 40.5, plus(click(1, 900, 0.05), thump(80, 0.2)), 0.3)
    amb = filt(noise(9.2), 'low', 450)
    amb = amb / np.max(np.abs(amb))
    add(s, 40.15, amb * np.minimum(1, tt(9.2) / 0.5) * np.minimum(1, (9.2 - tt(9.2)) / 0.5), 0.12)
    for bt in (40.8, 41.4, 45.3, 46.6):
        add(s, bt, chirp_bird(0.1), 0.025)
    for ct, f0, g in ((41.8, 90, 0.3), (42.6, 75, 0.35), (43.4, 95, 0.3), (44.2, 80, 0.25), (46.0, 85, 0.2)):
        add(s, ct, car_pass(2.4, f0), g)
    for ft in (47.0, 48.1, 49.2):
        add(s, ft - 0.5, tone(3000, 0.45) * np.linspace(0.2, 1, int(0.45 * SR)), 0.008)
        add(s, ft, plus(click(1, 2000, 0.03), click(0.7, 800, 0.04)), 0.25)
    add(s, 48.3, ringtone(0.9), 0.02)
    for i in range(10):
        add(s, 49.6 + i * 0.33, plus(thump(110, 0.12), 0.3 * click(1, 1200, 0.03)), 0.1)
    club = filt(noise(7.4), 'band', [250, 1100])
    mod = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 2.3 * tt(7.4))) * np.abs(np.sin(2 * np.pi * 1.1 * tt(7.4)))
    add(s, 52.95, club * mod * np.minimum(1, tt(7.4) / 0.4), 0.03)
    t = 52.95
    while t < 60.3:
        add(s, t, click(1, 2600 + rng.random() * 1500, 0.015), 0.05); t += 0.04 + rng.random() * 0.08
    for i in range(18):
        gt = 52.95 + rng.random() * 7.2
        add(s, gt, filt(noise(0.12), 'low', 1500) * np.exp(-tt(0.12) * 30), 0.06)
    for mt in (59.22, 59.88, 60.2):
        add(s, mt, plus(tone(880, 0.07), np.pad(tone(1320, 0.09), (int(0.07 * SR), 0))), 0.04)
    for i in range(int(2.0 / 0.4)):
        cr = tt(0.12)
        add(s, 60.4 + i * 0.4, np.sin(2 * np.pi * 4700 * cr) * (np.sin(2 * np.pi * 45 * cr) > 0) * np.sin(np.pi * cr / 0.12), 0.02)
    add(s, 62.65, plus(click(1, 900, 0.06), thump(90, 0.15)), 0.4)
    add(s, 62.7, filt(noise(0.45), 'band', [400, 9000]) * np.linspace(1, 0.2, int(0.45 * SR)), 0.1)
    add(s, 71.1, click(1, 1500, 0.04), 0.3)
    t, gap = 72.5, 0.25
    while t < 74.45:
        add(s, t, click(1, 3800, 0.02), 0.13); t += gap; gap = max(0.03, gap * 0.86)
    pf = tt(0.6)
    add(s, 74.75, filt(noise(0.6), 'band', [800, 6000]) * np.sin(np.pi * pf / 0.6) ** 2, 0.12)
    sw = tt(0.8)
    add(s, 77.4, filt(noise(0.8), 'band', [500, 7000]) * np.sin(np.pi * sw / 0.8) ** 2, 0.08)
    for k, m in enumerate([72, 76, 79, 84]):
        add(s, 77.9 + k * 0.08, tone(mtof(m), 0.4) * np.exp(-tt(0.4) * 6), 0.04)
    add(s, 80.3, thump(45, 1.6), 0.5)
    add(s, 80.3, filt(noise(1.2), 'low', 1500) * np.exp(-tt(1.2) * 4), 0.12)
    return s[:N]


def music_gain():
    t = np.arange(N) / SR
    g = np.full(N, 0.12)
    def seg(a, b, v, fade=0.4):
        nonlocal g
        w = np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)
        g = g * (1 - w) + v * w
    seg(0, 2.5, 0.04)
    seg(16.4, 21.8, 0.07)
    seg(37.6, 40.15, 0.3)
    seg(62.4, 71.0, 0.08)
    seg(80.2, 90.6, 0.3)
    g[t > 89.0] *= np.clip(1 - (t[t > 89.0] - 89.0) / 1.0, 0, 1)
    return g


def save(path, x):
    pcm = (np.stack([x, x], axis=1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', path], input=pcm.tobytes(), check=True)


def main():
    voice_path, out_dir = sys.argv[1], sys.argv[2]
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', voice_path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    voice = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    v = np.zeros(N)
    v[: min(N, len(voice))] = voice[:N]
    v = v / np.max(np.abs(v)) * 0.85
    mus = music() * music_gain()
    fx = sfx()
    env = np.convolve(np.abs(v), np.ones(4410) / 4410, mode='same')
    duck = 1 - 0.35 * np.clip(env / 0.08, 0, 1)
    mix = v + mus * duck + fx
    mix = filt(mix, 'high', 40)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    peak = np.max(np.abs(mix))
    save(os.path.join(out_dir, 'mix.wav'), mix / peak * 0.95)
    save(os.path.join(out_dir, 'music.wav'), mus / np.max(np.abs(mus)) * 0.9)
    save(os.path.join(out_dir, 'sfx.wav'), fx / np.max(np.abs(fx)) * 0.9)


if __name__ == '__main__':
    main()
