"""DIDAO S01E01 - procedural sound design + score (no external samples, fully reproducible).

Writes:
  ../sound_effects/SFX_EP01_FULL.wav       (all effects + ambience, episode timeline)
  ../sound_effects/sfx_*.wav               (individual one-shots for reuse)
  ../music/MUSIC_EP01_FULL.wav             (tension score, episode timeline)
  ../music/music_cue_sheet.txt
"""
import os
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script_ep01 import CLIPS  # noqa: E402

SR = 48000
rng = np.random.default_rng(11)
OFF = {}
acc = 0.0
for c in CLIPS:
    OFF[c['id']] = acc
    acc += c['dur']
TOTAL = acc
N = int(TOTAL * SR) + SR


def T(cid, t):
    return OFF[cid] + t


def write_wav(path, x, stereo=True):
    x = np.clip(x, -1, 1)
    if x.ndim == 1 and stereo:
        x = np.stack([x, x], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2 if x.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def bp(x, f1, f2, order=2):
    return sosfilt(butter(order, [f1, f2], 'band', fs=SR, output='sos'), x)


def env_adsr(n, a=0.005, d=0.1, s=0.0, r=0.1):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1.0)
    e *= np.where(t < a, 1, np.exp(-(t - a) / max(d, 1e-4)) * (1 - s) + s)
    return e


def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(x), 0] += x * gain * l * 1.414
    buf[i:i + len(x), 1] += x * gain * r * 1.414


def noise(sec):
    return rng.standard_normal(int(round(sec * SR)))


# ---------------------------------------------------------------- one-shots
def sfx_footstep_leaves(heavy=False):
    n = noise(0.35 if heavy else 0.22)
    crunch = bp(n, 1500, 6000) * env_adsr(len(n), 0.004, 0.05)
    grit = bp(noise(len(n) / SR), 400, 2500) * env_adsr(len(n), 0.01, 0.08) * 0.6
    thump = np.sin(2 * np.pi * (55 if heavy else 90) * np.arange(len(n)) / SR) * env_adsr(len(n), 0.003, 0.09 if heavy else 0.04)
    x = crunch * 0.5 + grit + thump * (1.6 if heavy else 0.5)
    if heavy:  # twig snap
        k = int(0.03 * SR)
        x[k:k + 800] += hp(noise(800 / SR), 2500) * np.exp(-np.arange(800) / 120) * 1.2
    return x / np.max(np.abs(x))


def sfx_fire_crackle(sec):
    n = int(sec * SR)
    base = lp(noise(sec), 900) * 0.25 + bp(noise(sec), 200, 600) * 0.15
    base *= 0.7 + 0.3 * lp(np.abs(noise(sec)), 3)
    pops = np.zeros(n)
    for _ in range(int(sec * 9)):
        i = rng.integers(0, n - 2000)
        L = rng.integers(200, 1500)
        pops[i:i + L] += hp(noise(L / SR), 1200) * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(0.3, 1.0)
    return base + pops * 0.6


def sfx_wind(sec, strength=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(sec * SR)
    x = r.standard_normal(n)
    mod = lp(r.standard_normal(n), 0.4)
    mod = (mod - mod.min()) / (np.ptp(mod) + 1e-9)
    low = lp(x, 350) * (0.4 + 0.8 * mod)
    hiss = bp(r.standard_normal(n), 1500, 5000) * 0.05 * (0.2 + mod)
    return (low + hiss) * strength


def sfx_click():
    n = int(0.05 * SR)
    x = hp(noise(0.05), 2000) * np.exp(-np.arange(n) / 120)
    x[:200] += np.sin(2 * np.pi * 1800 * np.arange(200) / SR) * 0.6
    return x / np.max(np.abs(x))


def sfx_match():
    n = int(1.2 * SR)
    strike = bp(noise(0.18), 2000, 9000) * env_adsr(int(0.18 * SR), 0.005, 0.06)
    flare = lp(noise(1.2), 2500) * env_adsr(n, 0.02, 0.4, 0.15, 0.3) * 0.5
    x = flare
    x[:len(strike)] += strike
    return x / np.max(np.abs(x))


def sfx_zipper(sec=1.1):
    n = int(sec * SR)
    t = np.arange(n) / SR
    rate = 38 + 20 * t
    ticks = (np.sin(2 * np.pi * np.cumsum(rate) / SR) > 0.85).astype(float)
    x = bp(noise(sec), 1500, 7000) * (0.3 + ticks) * np.minimum(1, t / 0.05) * np.minimum(1, (sec - t) / 0.1)
    return x / np.max(np.abs(x))


def sfx_glitch(sec=0.7):
    n = int(sec * SR)
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * (60 + 900 * rng.random()) * t)) * 0.3
    gate = (lp(noise(sec), 30) > 0).astype(float)
    x = (x + hp(noise(sec), 3000) * 0.6) * gate
    x += np.sin(2 * np.pi * 45 * t) * 0.7
    return x * np.minimum(1, (sec - t) / 0.08)


def sfx_vibrate(sec=0.6):
    t = np.arange(int(sec * SR)) / SR
    x = np.sign(np.sin(2 * np.pi * 165 * t)) * 0.4 + np.sin(2 * np.pi * 82 * t) * 0.5
    x = lp(x, 900) * np.minimum(1, t / 0.02) * np.minimum(1, (sec - t) / 0.03)
    return x


def sfx_hit(sec=3.5, f=38):
    t = np.arange(int(sec * SR)) / SR
    sub = np.sin(2 * np.pi * f * t * (1 - 0.15 * t / sec)) * np.exp(-t / 1.3)
    body = lp(noise(sec), 400) * np.exp(-t / 0.5) * 0.8
    metal = sum(np.sin(2 * np.pi * fr * t) * np.exp(-t / 0.9) for fr in (311, 466, 622, 740)) * 0.08
    air = hp(noise(sec), 4000) * np.exp(-t / 0.08) * 0.5
    x = sub * 1.2 + body + metal + air
    return x / np.max(np.abs(x))


def sfx_heartbeat():
    t = np.arange(int(0.6 * SR)) / SR
    b1 = np.sin(2 * np.pi * 50 * t) * np.exp(-t / 0.06)
    b2 = np.roll(b1, int(0.22 * SR)) * 0.7
    return lp(b1 + b2, 200)


def sfx_whoosh(sec=1.0):
    t = np.arange(int(sec * SR)) / SR
    x = bp(noise(sec), 300, 3000) * np.sin(np.pi * t / sec) ** 2
    return x / np.max(np.abs(x))


def sfx_riser(sec=3.0):
    t = np.arange(int(sec * SR)) / SR
    f = 80 + 600 * (t / sec) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + bp(noise(sec), 1000, 6000) * 0.4 * (t / sec) ** 2
    return x * (t / sec) ** 1.5


# ---------------------------------------------------------------- SFX timeline
# clip ids: 1 01A, 2 01B, 3 02, 4 03A, 5 03B, 6 04, 7 05, 8 06, 9 07A, 10 07B, 11 08, 12 09, 13 10, 14 11, 15 12, 16 13, 17 14
HIT = T(17, 7.4)          # final musical hit; 0.6 s of silence follows, then the end card


def build_sfx():
    buf = np.zeros((N, 2))
    wind = sfx_wind(TOTAL + 1, 0.9)
    wenv = np.ones(len(wind))

    def ramp(t0, t1, v0, v1):
        a, b = int(t0 * SR), int(t1 * SR)
        wenv[a:b] = np.linspace(v0, v1, b - a)
    ramp(T(7, 0), T(7, 3.5), 1.0, 0.25)            # the forest goes silent at midnight
    wenv[int(T(7, 3.5) * SR):int(T(8, 9.5) * SR)] = 0.25
    ramp(T(8, 9.5), T(9, 1.0), 0.25, 0.9)
    wenv[int(HIT * SR):] = 0.0
    wb = wind * wenv
    buf[:len(wb), 0] += wb * 0.16
    buf[:len(wb), 1] += np.roll(wb, 3000) * 0.16
    for t in (2.0, 9.5, T(3, 4), T(4, 6), T(8, 6.0), T(9, 5), T(12, 2), T(12, 8), T(13, 1.5), T(16, 0.5)):
        place(buf, bp(noise(1.6), 2000, 8000) * np.sin(np.linspace(0, np.pi, int(1.6 * SR))) ** 2, t, 0.05, pan=rng.uniform(-0.7, 0.7))
    for t, p in ((4.0, -0.6), (T(3, 4.5), 0.5)):
        tt = np.arange(int(0.9 * SR)) / SR
        owl = np.sin(2 * np.pi * (380 - 40 * tt) * tt) * (np.sin(np.pi * np.clip(tt / 0.35, 0, 1)) * (tt < 0.35) + np.sin(np.pi * np.clip((tt - 0.45) / 0.4, 0, 1)) * (tt > 0.45))
        place(buf, lp(owl, 900), t, 0.05, pan=p)
    fs = [sfx_footstep_leaves() for _ in range(6)]
    walk_end = OFF[3] - 0.3
    for k, off in enumerate((0.0, 0.21, 0.4)):
        t = 0.3 + off
        while t < walk_end:
            dist = 1.0 - 0.6 * (1 - t / walk_end)
            place(buf, fs[(k * 3 + int(t * 7)) % 6], t, 0.10 * dist + 0.02, pan=(-0.3, 0.0, 0.3)[k])
            t += 0.58
    # campsite
    for t in np.arange(0.4, 5.8, 1.31):
        tk = int(0.12 * SR)
        knock = (np.sin(2 * np.pi * 220 * np.arange(tk) / SR) + lp(noise(0.12), 2000)) * np.exp(-np.arange(tk) / 500)
        place(buf, knock, T(3, t), 0.08, pan=-0.4)
    place(buf, sfx_match(), T(3, 2.9), 0.35, pan=0.1)
    fire_len = OFF[7] - T(3, 3.5)
    fc = sfx_fire_crackle(fire_len)
    fenv = np.minimum(1, np.arange(len(fc)) / (2.5 * SR)) * np.minimum(1, (len(fc) - np.arange(len(fc))) / (1.0 * SR))
    place(buf, fc * fenv, T(3, 3.5), 0.22)
    place(buf, sfx_whoosh(1.2), T(3, 3.6), 0.12)
    # first sighting
    place(buf, sfx_riser(2.0), T(4, 3.6), 0.10)
    place(buf, sfx_hit(2.5, 42), OFF[5], 0.35)
    # flashlight + disappearance
    place(buf, sfx_click(), T(6, 1.25), 0.4, pan=0.2)
    place(buf, sfx_glitch(0.65), T(6, 4.0), 0.28)
    place(buf, sfx_whoosh(0.8), T(6, 4.5), 0.12)
    # midnight
    for t in np.arange(0.2, 6, 3.0):
        br = lp(noise(1.2), 900) * np.sin(np.linspace(0, np.pi, int(1.2 * SR))) ** 2
        place(buf, br, T(7, t), 0.05)
    place(buf, sfx_footstep_leaves(heavy=True), T(7, 4.6), 0.25, pan=0.6)       # the "strange sound"
    # footsteps: three, silence, three more
    for i, t in enumerate((2.0, 2.8, 3.6, 7.9, 8.6, 9.3)):
        place(buf, sfx_footstep_leaves(heavy=True), T(8, t), 0.75, pan=0.45 - (i % 3) * 0.3)
    hb = sfx_heartbeat()
    t = 2.2
    while t < 10.0:
        place(buf, hb, T(8, t), 0.32)
        t += 0.80 - 0.02 * (t - 2)
    for t in (3.0, 8.0):
        place(buf, bp(noise(1.0), 300, 2500) * np.sin(np.linspace(0, np.pi, SR)) ** 3, T(8, t), 0.08)
    # second sighting
    place(buf, sfx_zipper(1.2), T(9, 0.0), 0.25)
    place(buf, sfx_hit(3.0, 36), T(9, 1.6), 0.30)
    t = 0.0
    while t < OFF[11] - OFF[9]:
        place(buf, hb, T(9, t), 0.28)
        t += 0.62
    place(buf, sfx_riser(2.0), T(10, 0.6), 0.10)
    place(buf, sfx_hit(2.5, 33), T(10, 2.6), 0.32)               # "it has no face"
    # wake + exit + disappearance
    for t in (0.1, 0.5, 0.9):
        place(buf, bp(noise(0.35), 1500, 6000) * np.sin(np.linspace(0, np.pi, int(0.35 * SR))), T(11, t), 0.08)
    for t in (1.55, 2.65):
        place(buf, bp(noise(0.9), 200, 3000) * np.sin(np.linspace(0, np.pi, int(0.9 * SR))), T(11, t), 0.12)
    place(buf, sfx_zipper(0.8), T(11, 3.8), 0.18, pan=0.4)
    for k, t in enumerate(np.arange(4.0, 7.0, 0.5)):
        place(buf, fs[k % 6], T(11, t), 0.18, pan=0.3)
    place(buf, sfx_click(), T(11, 5.7), 0.35, pan=-0.1)
    place(buf, sfx_click(), T(11, 6.05), 0.3, pan=0.3)
    place(buf, sfx_glitch(0.6), T(11, 6.1), 0.28)
    # morning
    for k in range(7):
        tt = np.arange(int(0.25 * SR)) / SR
        chirp = np.sin(2 * np.pi * (2600 + 900 * np.sin(2 * np.pi * 6 * tt)) * tt) * np.sin(np.pi * tt / 0.25)
        place(buf, chirp, T(12, 0.5 + k * 0.9), 0.02, pan=rng.uniform(-0.8, 0.8))
    for k, t in enumerate(np.arange(6.9, 10.5, 0.9)):
        place(buf, fs[k % 6], T(12, t), 0.10, pan=rng.uniform(-0.4, 0.4))
    for k, t in enumerate(np.arange(0.1, 3.0, 0.56)):
        place(buf, fs[k % 6], T(13, t), 0.16, pan=0.2)
    place(buf, sfx_hit(2.5, 48), T(13, 3.4), 0.28)
    # phone
    place(buf, sfx_vibrate(0.6), T(14, 1.5), 0.45)
    place(buf, sfx_vibrate(0.6), T(14, 2.35), 0.45)
    tt = np.arange(int(0.5 * SR)) / SR
    ping = (np.sin(2 * np.pi * 988 * tt) * (tt < 0.12) + np.sin(2 * np.pi * 1318 * tt) * (tt >= 0.12)) * np.exp(-tt / 0.25)
    place(buf, ping, T(14, 2.9), 0.10)
    # reveal
    place(buf, sfx_hit(2.5, 40), T(15, 3.0), 0.32)
    t = T(15, 3.0)
    while t < OFF[17]:
        place(buf, hb, t, 0.22)
        t += 0.7
    # the fourth: breathy whisper bed
    place(buf, bp(noise(2.2), 1500, 6000) * np.sin(np.linspace(0, np.pi, int(2.2 * SR))), T(16, 2.1), 0.03)
    # empty tent: whip, riser, HIT, silence, low tail under the end card
    place(buf, sfx_whoosh(0.8), T(17, 0.05), 0.25)
    place(buf, sfx_riser(3.0), HIT - 3.0, 0.18)
    place(buf, sfx_hit(1.2, 34)[: int(0.6 * SR)] * np.linspace(1, 0, int(0.6 * SR)) ** 0.5, HIT, 0.8)
    place(buf, sfx_glitch(0.6), HIT, 0.2)
    tail = lp(noise(1.8), 120) * np.sin(np.linspace(0, np.pi, int(1.8 * SR)))
    place(buf, tail, HIT + 1.2, 0.25)
    a, b = int((HIT + 0.6) * SR), int((HIT + 1.2) * SR)
    buf[a:b] *= np.linspace(1, 0, b - a)[:, None] ** 8
    return buf


# ---------------------------------------------------------------- music
def build_music():
    t = np.arange(N) / SR
    out = np.zeros((N, 2))
    pts = [(0, 0.15), (OFF[3], 0.2), (OFF[4], 0.25), (OFF[5], 0.55), (OFF[7], 0.35), (OFF[8], 0.6), (OFF[9], 0.75), (OFF[10], 0.85),
           (OFF[11], 0.7), (OFF[12], 0.35), (OFF[13], 0.45), (T(13, 3.4), 0.6), (OFF[14], 0.65), (OFF[15], 0.8), (OFF[16], 0.6),
           (OFF[17], 0.8), (HIT, 1.0), (HIT + 0.01, 0.0), (TOTAL + 1, 0.0)]
    xs, ys = zip(*pts)
    ten = np.interp(t, xs, ys)
    # drone: D1/D2 + A2 detuned saws, low-passed, cutoff rises with tension
    def saw(f):
        ph = (f * t) % 1.0
        return 2 * ph - 1
    drone = sum(saw(f) for f in (36.71, 36.95, 73.42, 73.0, 110.0, 109.6)) / 6
    lo = lp(drone, 220)
    hi = lp(drone, 900) - lp(drone, 300)
    pad = lo * 0.9 + hi * ten * 0.8
    # dissonant high cluster (Eb against D) fading in with tension
    cl = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.13 * t * (i + 1)) * 2) for i, f in enumerate((587.3, 622.3, 880.0, 932.3))) / 4
    cl = lp(cl, 2000) * np.clip(ten - 0.45, 0, 1) * 0.35
    # slow pulse (sub thump) when tension high
    beat_rate = 0.8 + ten * 1.0
    phase = np.cumsum(beat_rate) / SR
    pulse = np.sin(2 * np.pi * 45 * t) * np.exp(-((phase % 1.0)) * 9) * np.clip(ten - 0.5, 0, 1) * 1.2
    # piano-like sparse motif in clip 1-2 (D minor), very soft
    motif = np.zeros(N)
    notes = [(1.0, 293.7), (2.4, 349.2), (3.8, 440.0), (5.2, 415.3), (8.0, 293.7), (9.4, 277.2), (11.5, 293.7), (13.0, 349.2),
             (T(3, 1.0), 311.1), (T(12, 1.0), 293.7), (T(12, 3.0), 277.2), (T(12, 5.5), 261.6)]
    for st, f in notes:
        n = int(3.0 * SR)
        tt = np.arange(n) / SR
        tone = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) + 0.15 * np.sin(2 * np.pi * 3 * f * tt)) * np.exp(-tt / 0.9)
        i = int(st * SR)
        motif[i:i + n] += tone[: N - i] * 0.25
    motif = lp(motif, 2500)
    mono = pad * 0.5 * (0.5 + ten) + cl + pulse + motif
    stereo_spread = lp(rng.standard_normal(N), 0.2) * 0.0
    out[:, 0] = mono + 0.15 * np.roll(cl, 900)
    out[:, 1] = mono + 0.15 * np.roll(cl, -900)
    # fade in/out + hard silence after the final hit
    out *= np.clip(t / 2.0, 0, 1)[:, None]
    out[int(HIT * SR):] *= 0
    out /= np.max(np.abs(out)) + 1e-9
    return out * 0.8


if __name__ == '__main__':
    sfx_dir = os.path.join(HERE, '..', 'sound_effects')
    mus_dir = os.path.join(HERE, '..', 'music')
    os.makedirs(sfx_dir, exist_ok=True)
    os.makedirs(mus_dir, exist_ok=True)
    for name, x in (('footstep_leaves', sfx_footstep_leaves()), ('footstep_heavy_outside', sfx_footstep_leaves(True)),
                    ('fire_crackle_10s', sfx_fire_crackle(10) * 0.5), ('wind_10s', sfx_wind(10) * 0.4),
                    ('flashlight_click', sfx_click() * 0.6), ('match_strike', sfx_match() * 0.6), ('tent_zipper', sfx_zipper() * 0.6),
                    ('glitch_disappear', sfx_glitch() * 0.6), ('phone_vibrate', sfx_vibrate() * 0.8), ('impact_hit', sfx_hit() * 0.8),
                    ('heartbeat', sfx_heartbeat() * 0.8), ('riser', sfx_riser() * 0.8)):
        write_wav(os.path.join(sfx_dir, f'sfx_{name}.wav'), x / (np.max(np.abs(x)) + 1e-9) * 0.8)
    sfx = build_sfx()
    sfx /= max(1.0, np.max(np.abs(sfx)))
    write_wav(os.path.join(sfx_dir, 'SFX_EP01_FULL.wav'), sfx)
    mus = build_music()
    write_wav(os.path.join(mus_dir, 'MUSIC_EP01_FULL.wav'), mus)
    with open(os.path.join(mus_dir, 'music_cue_sheet.txt'), 'w') as f:
        f.write('DIDAO S01E01 - score cue sheet (procedural, original)\n')
        for c in CLIPS:
            f.write(f"{OFF[c['id']]:7.2f}s  {c['name']}\n")
        f.write(f'Key: D minor drone; tension rises through the night, drops for the morning, climbs to the final hit at {HIT:.1f}s\n'
                '(CLIP_14 7.4 s), then 0.6 s of hard silence before the black end card.\n')
    print('audio done, total', TOTAL)
