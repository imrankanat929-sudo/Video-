"""Original score + sound design + voice-over mix. All music/SFX are synthesised here (no third-party samples).
usage: python3 audio.py  -> build/mix_ru.wav, build/mix_en.wav, build/music.wav, build/sfx.wav"""
import os
import subprocess
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline  # noqa: E402

SR = 48000
DUR = 120.0
N = int(SR * DUR)
BUILD = os.path.join(timeline.ROOT, 'build')
rng = np.random.default_rng(1234)
t_all = np.arange(N) / SR


# ------------------------------------------------------------------------------------------------
# DSP helpers
# ------------------------------------------------------------------------------------------------
def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'low', fs=SR, output='sos'), x, axis=0)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'high', fs=SR, output='sos'), x, axis=0)


def bp(x, f1, f2, order=2):
    return signal.sosfilt(signal.butter(order, [f1, f2], 'band', fs=SR, output='sos'), x, axis=0)


def env_curve(points, n=N):
    """piecewise-linear envelope from [(t, v), ...]"""
    ts = np.array([p[0] for p in points]) * SR
    vs = np.array([p[1] for p in points])
    return np.interp(np.arange(n), ts, vs)


def adsr(n, a=0.005, d=0.1, s=0.0, r=0.2, sus_len=0.0):
    a_n, d_n, s_n, r_n = int(a * SR), int(d * SR), int(sus_len * SR), int(r * SR)
    e = np.concatenate([np.linspace(0, 1, max(a_n, 1)), np.linspace(1, s, max(d_n, 1)), np.full(s_n, s), np.linspace(s, 0, max(r_n, 1))])
    if len(e) < n:
        e = np.concatenate([e, np.zeros(n - len(e))])
    return e[:n]


def saw(freq, n, detune=0.0, phase=None):
    f = freq * (1 + detune)
    ph = (np.arange(n) * f / SR + (rng.random() if phase is None else phase)) % 1.0
    return 2 * ph - 1


def place(buf, x, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= len(buf) or i0 + len(x) <= 0:
        return
    if i0 < 0:
        x = x[-i0:]
        i0 = 0
    x = x[:len(buf) - i0]
    if x.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        buf[i0:i0 + len(x), 0] += x * gain * l * 1.414
        buf[i0:i0 + len(x), 1] += x * gain * r * 1.414
    else:
        buf[i0:i0 + len(x)] += x * gain


def reverb_ir(seconds=2.8, decay=3.2, bright=6000):
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], 1) * np.exp(-tt * decay)[:, None]
    ir = lp(ir, bright)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0)).max() * 0.5


IR = reverb_ir()


def reverb(x, wet=0.3, ir=IR):
    y = np.stack([signal.fftconvolve(x[:, k], ir[:, k])[:len(x)] for k in range(2)], 1)
    return x * (1 - wet * 0.3) + y * wet


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------------------------------------
# MUSIC
# ------------------------------------------------------------------------------------------------
def intensity_curve():
    # follows the brief: calm -> rising -> peak 76-92 -> near silence 92.2-95.4 -> soft -> atmospheric end
    return env_curve([(0, 0.0), (0.4, 0.42), (14, 0.45), (17.3, 0.5), (20, 0.58), (36, 0.62), (40, 0.68), (49, 0.7), (60, 0.76), (69.7, 0.82),
                      (75.5, 0.9), (76.0, 1.0), (92.0, 1.0), (92.3, 0.12), (95.4, 0.12), (95.7, 0.45), (102, 0.4), (103, 0.42),
                      (107, 0.45), (109, 0.55), (117, 0.5), (120, 0.0)])


def drone():
    x = np.zeros(N)
    for m, g in ((26, 1.0), (38, 0.6), (45, 0.25)):
        for dt in (-0.004, 0.0, 0.0035):
            x += saw(midi(m), N, dt) * g
    x = lp(x, 180, 4)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t_all)
    x *= lfo
    # sub sine
    x += 0.8 * np.sin(2 * np.pi * midi(26) * t_all) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t_all))
    return x / np.abs(x).max()


def pad_chords(seq, t0, t1, octave_gain=1.0, cutoff=1400, attack=1.2):
    """seq: list of (start, [midi notes]) inside [t0,t1]. Detuned saw ensemble, slow attack (strings)."""
    out = np.zeros((N, 2))
    for k, (s, notes) in enumerate(seq):
        e = seq[k + 1][0] if k + 1 < len(seq) else t1
        n = int((e - s + 1.5) * SR)
        x = np.zeros((n, 2))
        for m in notes:
            for dt, pan in ((-0.006, -0.6), (0.0, 0.0), (0.005, 0.6)):
                v = saw(midi(m), n, dt)
                x[:, 0] += v * (1 - pan) * 0.5
                x[:, 1] += v * (1 + pan) * 0.5
        x = lp(x, cutoff, 2)
        envl = adsr(n, a=attack, d=0.5, s=0.85, r=1.4, sus_len=max(0, e - s - attack - 0.5))
        out_seg = x * envl[:, None]
        place(out, out_seg, s, octave_gain / len(notes))
    return out


def tremolo_strings(t0, t1, notes, rate=11.0, gain=1.0, cutoff=4500):
    n = int((t1 - t0) * SR)
    tt = np.arange(n) / SR
    x = np.zeros((n, 2))
    for i, m in enumerate(notes):
        for dt, pan in ((-0.004, -0.5), (0.004, 0.5)):
            v = saw(midi(m), n, dt)
            x[:, 0] += v * (1 - pan) * 0.5
            x[:, 1] += v * (1 + pan) * 0.5
    x = lp(x, cutoff)
    trem = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * rate * tt)) * 0.6 + 0.2 * np.sin(2 * np.pi * rate * tt)
    envl = np.clip(np.minimum(tt / 1.5, (t1 - t0 - tt) / 0.4), 0, 1)
    out = np.zeros((N, 2))
    place(out, x * (trem * envl)[:, None], t0, gain / len(notes))
    return out


def boom(f0=55, dur=3.5, noise=0.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f0 * (1 + 1.8 * np.exp(-tt * 18))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-tt * 1.4)
    nz = lp(rng.standard_normal(n), 900) * np.exp(-tt * 9) * noise
    x = x + nz
    return x / np.abs(x).max()


def tom(f0=90, dur=0.8):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt * 30))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    x += bp(rng.standard_normal(n), 150, 1200) * np.exp(-tt * 40) * 0.4
    return x / np.abs(x).max()


def tick(dur=0.06):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 3500) * np.exp(-tt * 90)
    return x / np.abs(x).max()


def ostinato_note(m, dur=0.22):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = (saw(midi(m), n, -0.003) + saw(midi(m), n, 0.003)) * 0.5
    x = lp(x, 900)
    x *= np.exp(-tt * 9) * np.minimum(tt / 0.004, 1)
    return x


def riser(dur=3.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    # sweeping band-pass via blocks
    blocks = 30
    for b in range(blocks):
        a0, a1 = b * n // blocks, (b + 1) * n // blocks
        fc = 300 * (2 ** (b / blocks * 4.5))
        seg = bp(x[max(0, a0 - 2000):a1], fc * 0.7, min(fc * 1.4, 20000))[-(a1 - a0):]
        out[a0:a1] = seg
    out *= (tt / dur) ** 2.2
    return out / np.abs(out).max()


def music():
    I = intensity_curve()
    mus = np.zeros((N, 2))
    d = drone()
    mus += np.stack([d, d], 1) * 0.55
    # calm opening: soft high pad (Dm add9), airy
    calm = pad_chords([(0.0, [62, 65, 69, 76]), (6.0, [58, 62, 65, 72]), (11.0, [60, 64, 67, 74])], 0, 17.3, cutoff=2600, attack=2.5)
    mus += calm * env_curve([(0, 0), (2, 0.45), (15.5, 0.45), (17.4, 0.0)])[:, None]
    # tension strings 17.3 -> 92
    seq = []
    prog = [[50, 53, 57], [50, 53, 58], [46, 50, 53], [49, 52, 57, 58]]
    t = 17.3
    k = 0
    while t < 92:
        seq.append((t, prog[k % 4]))
        t += 4.0 if t < 60 else 3.0
        k += 1
    mus += pad_chords(seq, 17.3, 92.2, cutoff=1200, attack=1.0) * env_curve([(17.3, 0), (20, 0.5), (40, 0.65), (76, 0.85), (92.0, 0.9), (92.25, 0)])[:, None]
    # high dissonant tremolo at peak
    mus += tremolo_strings(60.0, 76.0, [74, 75], rate=9, gain=0.22)
    mus += tremolo_strings(76.0, 92.2, [74, 75, 81], rate=13, gain=0.38)
    # ostinato pulse with accelerating tempo (bpm 64 -> 128)
    tt = 40.0
    beat = 0
    while tt < 92.1:
        bpm = np.interp(tt, [40, 60, 76, 92], [64, 84, 120, 132])
        step = 60.0 / bpm / 2
        m = 38 if beat % 4 != 3 else 37
        g = np.interp(tt, [40, 50, 76, 92], [0.1, 0.25, 0.5, 0.6])
        place(mus, ostinato_note(m), tt, g * (1.25 if beat % 2 == 0 else 0.8))
        if tt > 49 and beat % 2 == 0:
            place(mus, tick(), tt, np.interp(tt, [49, 76, 92], [0.03, 0.08, 0.12]), pan=0.4 if beat % 4 == 0 else -0.4)
        tt += step
        beat += 1
    # war drums at peak
    tt = 76.0
    beat = 0
    while tt < 92.0:
        bpm = 120 if tt < 84 else 132
        if beat % 4 in (0, 3) or (tt > 84 and beat % 2 == 0):
            place(mus, tom(70 if beat % 4 == 0 else 95), tt, 0.55, pan=-0.2 if beat % 2 else 0.2)
        tt += 60 / bpm / 2
        beat += 1
    # bass hits
    for th, g in ((17.42, 0.9), (19.9, 1.0), (24.6, 0.7), (36.6, 0.75), (49.6, 0.7), (62.4, 0.6), (69.7, 0.85), (76.0, 1.0),
                  (78.6, 0.8), (81.3, 0.75), (82.4, 1.0), (89.9, 0.8), (95.6, 0.85), (109.0, 0.7)):
        place(mus, boom(52 if g > 0.8 else 60), th, g * 0.9)
    # risers
    for t0, dur, g in ((14.3, 3.0, 0.12), (73.0, 3.0, 0.3), (106.0, 3.0, 0.12)):
        place(mus, riser(dur), t0, g, pan=0.0)
    # relief / ending pad
    end = pad_chords([(102.4, [53, 57, 60, 64]), (106.0, [50, 53, 57, 64]), (110.0, [46, 50, 53, 57]), (114.0, [50, 53, 57, 62])], 102.4, 120, cutoff=1800, attack=2.0)
    mus += end * env_curve([(102.4, 0), (103.5, 0.55), (116, 0.5), (120, 0)])[:, None]
    # high suspense note at end
    mus += tremolo_strings(110.0, 119.5, [81], rate=6, gain=0.08, cutoff=3000)
    mus = mus * I[:, None]
    # near silence: only a whisper of drone
    mus = reverb(mus, 0.35)
    mus = hp(mus, 28)
    return mus


# ------------------------------------------------------------------------------------------------
# SOUND EFFECTS
# ------------------------------------------------------------------------------------------------
def birds_track(t0, t1, density=0.9, gain=0.12):
    out = np.zeros((N, 2))
    tt = t0
    r = np.random.default_rng(7)
    while tt < t1:
        nchirp = r.integers(2, 6)
        f0 = r.uniform(2500, 5200)
        pan = r.uniform(-0.8, 0.8)
        for k in range(nchirp):
            dur = r.uniform(0.05, 0.14)
            n = int(dur * SR)
            ts = np.arange(n) / SR
            f = f0 * (1 + r.uniform(-0.25, 0.35) * ts / dur) + 300 * np.sin(2 * np.pi * r.uniform(20, 45) * ts)
            x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * ts / dur) ** 2
            place(out, x, tt + k * r.uniform(0.09, 0.2), gain * r.uniform(0.4, 1.0), pan)
        tt += r.exponential(1.0 / density)
    return out


def wind_track():
    x = rng.standard_normal((N, 2))
    x = lp(x, 500, 2)
    x = hp(x, 60)
    m = np.convolve(np.abs(rng.standard_normal(N // 4800 + 2)), np.ones(4) / 4, 'same')
    gust = np.interp(np.arange(N), np.arange(len(m)) * 4800, m)
    lvl = env_curve([(0, 0.6), (20, 0.7), (50, 0.9), (76, 1.1), (92, 1.1), (95.6, 0.8), (102.4, 0.6), (120, 0.5)])
    x = x * (0.5 + 0.6 * gust / gust.max())[:, None] * lvl[:, None]
    return x / np.abs(x).max() * 0.18


def rustle(dur=0.5, bright=4000):
    n = int(dur * SR)
    ts = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 1500, bright)
    grains = (rng.random(n) < 0.004).astype(float)
    grains = np.convolve(grains, np.exp(-np.arange(400) / 60), 'same')
    x = x * (0.3 + grains) * np.sin(np.pi * ts / dur)
    return x / (np.abs(x).max() + 1e-9)


def footstep(heavy=False):
    if heavy:
        n = int(0.45 * SR)
        ts = np.arange(n) / SR
        thump = np.sin(2 * np.pi * (55 + 40 * np.exp(-ts * 30)) * ts) * np.exp(-ts * 11)
        crunch = bp(rng.standard_normal(n), 400, 3000) * np.exp(-ts * 22) * 0.45
        x = thump + crunch
    else:
        n = int(0.22 * SR)
        ts = np.arange(n) / SR
        crunch = bp(rng.standard_normal(n), 900, 5500) * np.exp(-ts * 28)
        gr = (rng.random(n) < 0.01).astype(float)
        crunch *= 0.6 + np.convolve(gr, np.exp(-np.arange(200) / 30), 'same')
        thump = np.sin(2 * np.pi * 110 * ts) * np.exp(-ts * 40) * 0.5
        x = crunch + thump
    return x / np.abs(x).max()


def branch_crack():
    n = int(0.9 * SR)
    ts = np.arange(n) / SR
    x = np.zeros(n)
    r = np.random.default_rng(3)
    for k in range(9):
        t0 = 0.0 if k == 0 else r.uniform(0.0, 0.12)
        i = int(t0 * SR)
        L = int(0.03 * SR)
        click = hp(r.standard_normal(L), 1200) * np.exp(-np.arange(L) / SR * (90 if k else 50))
        x[i:i + L] += click * (1.0 if k == 0 else r.uniform(0.2, 0.6))
    x += np.sin(2 * np.pi * 180 * ts) * np.exp(-ts * 25) * 0.4
    return x / np.abs(x).max()


def heartbeat(bpm, t0, t1, gain=0.5, out=None):
    out = np.zeros((N, 2)) if out is None else out
    tt = t0
    while tt < t1:
        for off, g in ((0.0, 1.0), (0.24, 0.7)):
            n = int(0.25 * SR)
            ts = np.arange(n) / SR
            x = np.sin(2 * np.pi * (48 + 20 * np.exp(-ts * 40)) * ts) * np.exp(-ts * 16)
            place(out, x, tt + off, gain * g)
        tt += 60.0 / bpm(tt) if callable(bpm) else 60.0 / bpm
    return out


def bear_rumble(dur=2.5, f0=70, growl=0.5):
    """low natural breathy rumble (no fantasy roar)"""
    n = int(dur * SR)
    ts = np.arange(n) / SR
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 23 * ts + 3 * np.sin(2 * np.pi * 1.7 * ts))
    x = bp(rng.standard_normal(n), f0, f0 * 6) * am * growl
    x += np.sin(2 * np.pi * f0 * ts) * 0.4
    envl = np.sin(np.pi * np.clip(ts / dur, 0, 1)) ** 1.5
    x = x * envl
    return x / np.abs(x).max()


def huff(dur=0.5, bright=2500):
    n = int(dur * SR)
    ts = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 200, bright) * np.exp(-ts * 6) * np.minimum(ts / 0.02, 1)
    x += bp(rng.standard_normal(n), 60, 300) * np.exp(-ts * 8) * 0.8
    return x / np.abs(x).max()


def sniff(dur=0.12):
    n = int(dur * SR)
    ts = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 1800, 6000) * np.sin(np.pi * ts / dur)
    return x / np.abs(x).max()


def whoosh(dur=0.5):
    n = int(dur * SR)
    ts = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    blocks = 12
    for b in range(blocks):
        a0, a1 = b * n // blocks, (b + 1) * n // blocks
        fc = 400 + 2600 * np.sin(np.pi * b / blocks)
        out[a0:a1] = bp(x[max(0, a0 - 1000):a1], fc * 0.6, fc * 1.6)[-(a1 - a0):]
    out *= np.sin(np.pi * ts / dur) ** 2
    return out / np.abs(out).max()


def skid(dur=0.9):
    n = int(dur * SR)
    ts = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 300, 3500) * np.exp(-ts * 3.5)
    gr = (rng.random(n) < 0.02).astype(float)
    x *= 0.5 + np.convolve(gr, np.exp(-np.arange(200) / 25), 'same')
    return x / np.abs(x).max()


def steps(out, t0, t1, rate, heavy=False, gain=0.3, pan=0.0, fade=None):
    tt = t0
    k = 0
    while tt < t1:
        g = gain if fade is None else gain * np.interp(tt, [t0, t1], fade)
        place(out, footstep(heavy), tt + rng.uniform(-0.015, 0.015), g * (1.0 if k % 2 == 0 else 0.85), pan + (0.08 if k % 2 else -0.08))
        tt += 1.0 / rate
        k += 1


def sfx():
    out = np.zeros((N, 2))
    out += birds_track(0, 17.3, density=1.4, gain=0.10)
    out += birds_track(101.5, 120, density=0.8, gain=0.08)
    out += wind_track()
    # hero footsteps while walking (rate ~1.85 steps/s)
    steps(out, 0.6, 9.4, 1.85, gain=0.06, fade=[0.15, 0.6])
    steps(out, 9.4, 12.0, 1.85, gain=0.22)
    steps(out, 12.0, 14.7, 1.7, gain=0.26)
    steps(out, 14.7, 17.3, 1.85, gain=0.10, pan=0.3)
    steps(out, 62.8, 68.2, 0.75, gain=0.16)   # slow steps backward
    # crack
    place(out, branch_crack(), 17.47, 0.9)
    place(out, rustle(1.2), 17.5, 0.25, 0.3)
    # whoosh (whip pan)
    place(out, whoosh(0.45), 19.72, 0.35)
    # bear presence low sound
    place(out, bear_rumble(3.5, 55, 0.35), 20.2, 0.35, 0.3)
    place(out, rustle(1.5, 2500), 20.4, 0.18, 0.4)
    # sniffing
    for k in range(7):
        place(out, sniff(), 32.2 + k * 0.32 + (0.15 if k > 3 else 0), 0.22)
    place(out, huff(0.6), 34.4, 0.3)
    # standing paws shift
    place(out, rustle(0.6, 3000), 35.2, 0.25)
    # heartbeat
    heartbeat(lambda tt: np.interp(tt, [36.6, 49], [72, 84]), 36.6, 49.2, 0.55, out)
    heartbeat(lambda tt: np.interp(tt, [72.9, 76], [100, 118]), 72.9, 76.0, 0.6, out)
    heartbeat(lambda tt: np.interp(tt, [92.2, 95.6], [118, 96]), 92.2, 95.8, 0.75, out)
    heartbeat(lambda tt: 70, 102.4, 105.0, 0.18, out)
    # bear steps
    steps(out, 49.7, 51.0, 1.25, heavy=True, gain=0.4)
    steps(out, 55.4, 56.6, 1.25, heavy=True, gain=0.55)
    place(out, huff(0.7), 68.6, 0.4)
    place(out, huff(0.7), 69.2, 0.3)
    steps(out, 69.8, 72.9, 2.4, heavy=True, gain=0.45)
    steps(out, 76.0, 77.6, 4.0, heavy=True, gain=0.6, pan=-0.2)
    steps(out, 78.6, 81.3, 4.2, heavy=True, gain=0.7)
    steps(out, 81.3, 82.35, 4.2, heavy=True, gain=0.7)
    place(out, skid(0.9), 82.0, 0.5)
    place(out, huff(0.8), 82.5, 0.55)
    place(out, bear_rumble(1.8, 65, 0.5), 82.6, 0.3)
    steps(out, 86.8, 89.9, 1.4, heavy=True, gain=0.35, pan=0.2)
    place(out, huff(0.6), 88.2, 0.3)
    steps(out, 89.9, 91.1, 4.0, heavy=True, gain=0.6)
    place(out, skid(0.6), 90.9, 0.35)
    # standoff breaths (near silence)
    for k in range(4):
        place(out, huff(0.9, 1800), 92.5 + k * 0.85, 0.22)
    # leaving
    steps(out, 96.0, 97.4, 1.0, heavy=True, gain=0.3)
    steps(out, 97.6, 102.4, 1.3, heavy=True, gain=0.35, fade=[1.0, 0.05])
    place(out, rustle(2.0, 2500), 99.5, 0.15, 0.4)
    # relief exhale
    place(out, huff(1.4, 4000), 103.0, 0.12)
    # random leaf rustles
    r = np.random.default_rng(9)
    for tt in np.arange(1, 118, 2.3):
        place(out, rustle(r.uniform(0.3, 0.9)), tt + r.uniform(0, 1.5), r.uniform(0.03, 0.07), r.uniform(-0.8, 0.8))
    out = reverb(out, 0.18)
    return out


# ------------------------------------------------------------------------------------------------
# VOICE
# ------------------------------------------------------------------------------------------------
def load_audio(path):
    b = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(b, np.float32).astype(np.float64)


def voice(lang):
    src = load_audio(os.path.join(timeline.ROOT, 'assets', f'vo_{lang}.mp3'))
    P = timeline.placed(lang)
    out = np.zeros(N)
    for k, g in enumerate(P):
        nxt_src = P[k + 1]['src_start'] if k + 1 < len(P) else len(src) / SR
        a = max(0.0, g['src_start'] - 0.10)
        prev_src_end = P[k - 1]['src_end'] if k > 0 else 0.0
        a = max(a, (prev_src_end + g['src_start']) / 2 if k > 0 else 0.0)
        b = min(nxt_src - 0.06, g['src_end'] + 0.45)
        seg = src[int(a * SR):int(b * SR)].copy()
        f = int(0.012 * SR)
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f * 3:] *= np.linspace(1, 0, f * 3)
        dst = a + g['off']
        i = int(dst * SR)
        out[i:i + len(seg)] += seg[:max(0, N - i)]
    # gentle presence EQ + normalise
    out = out + 0.25 * bp(out, 2500, 6000)
    out = hp(out, 70)
    out = out / (np.abs(out).max() + 1e-9) * 0.9
    return out


def duck_env(v, depth=0.6):
    e = np.abs(v)
    # attack 30ms / release 350ms envelope follower via filtering
    e = signal.sosfilt(signal.butter(1, 6, 'low', fs=SR, output='sos'), e)
    e = e / (e.max() + 1e-9)
    e = np.clip(e * 6, 0, 1)
    # smooth release
    e = np.maximum.accumulate(e[::-1].reshape(-1)[::-1]) if False else e
    e = signal.sosfilt(signal.butter(1, 2.5, 'low', fs=SR, output='sos'), e)
    e = np.clip(e / (e.max() + 1e-9) * 1.6, 0, 1)
    return 1 - depth * e


def compress(x, thr_db=-30.0, ratio=2.2, win=0.3):
    m = (x ** 2).mean(1)
    k = int(win * SR)
    e = np.sqrt(signal.fftconvolve(m, np.ones(k) / k, 'same').clip(1e-12))
    e_db = 20 * np.log10(e)
    over = np.maximum(e_db - thr_db, 0)
    g = 10 ** (-(over - over / ratio) / 20)
    return x * g[:, None]


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype('<i2')
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    os.makedirs(BUILD, exist_ok=True)
    print('music...')
    mus = music()
    mus = mus / np.abs(mus).max()
    mus = compress(mus, -26, 2.5)
    mus = mus / np.sqrt((mus ** 2).mean()) * 10 ** (-20 / 20)  # programme RMS -20 dBFS
    print('sfx...')
    fx = sfx()
    fx = fx / np.abs(fx).max()
    write_wav(os.path.join(BUILD, 'music.wav'), mus * 0.5)
    write_wav(os.path.join(BUILD, 'sfx.wav'), fx * 0.55)
    for lang in ('ru', 'en'):
        print('mix', lang)
        v = voice(lang)
        dk = duck_env(v, 0.5)
        dk_fx = duck_env(v, 0.35)
        mix = mus * 0.8 * dk[:, None] + fx * 0.55 * dk_fx[:, None] + np.stack([v, v], 1) * 0.95
        mix = mix / np.abs(mix).max() * 0.95
        write_wav(os.path.join(BUILD, f'mix_{lang}.wav'), mix)
        write_wav(os.path.join(BUILD, f'vo_{lang}_placed.wav'), np.stack([v, v], 1))


if __name__ == '__main__':
    main()
