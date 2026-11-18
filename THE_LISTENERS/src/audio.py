"""Original procedural music, ambience and sound effects for THE LISTENERS (numpy synthesis)."""
import numpy as np
from scipy import signal

SR = 48000


def T(d):
    return np.arange(int(d * SR)) / SR


def rng(seed):
    return np.random.RandomState(seed % (2 ** 31))


def white(n, seed=0):
    return rng(seed).randn(n).astype(np.float32)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band')
    return signal.lfilter(b, a, x).astype(np.float32)


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'low')
    return signal.lfilter(b, a, x).astype(np.float32)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'high')
    return signal.lfilter(b, a, x).astype(np.float32)


def pink(n, seed=0):
    w = np.fft.rfft(white(n, seed))
    f = np.arange(len(w)) + 1
    return np.fft.irfft(w / np.sqrt(f), n).astype(np.float32) * 8


def brown(n, seed=0):
    x = np.cumsum(white(n, seed)) / 300
    return hp(x, 15).astype(np.float32)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


def adsr(n, a=0.01, r=0.1):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return (x / m * peak).astype(np.float32)


_IR = {}


def reverb(x, size=2.0, wet=0.3, seed=1, damp=4000):
    key = (size, seed, damp)
    if key not in _IR:
        n = int(size * SR)
        ir = white(n, seed) * env_exp(n, size / 6)
        ir = lp(ir, damp)
        ir[0] = 0
        _IR[key] = ir / np.sqrt(np.sum(ir ** 2))
    y = signal.fftconvolve(x, _IR[key])[:len(x) + int(size * SR)]
    out = np.zeros(len(y), np.float32)
    out[:len(x)] += x * (1 - wet)
    out += y * wet * 0.5
    return out.astype(np.float32)


def place(buf, x, at):
    a = int(at * SR)
    if a >= len(buf):
        return
    if a < 0:
        x = x[-a:]
        a = 0
    b = min(len(buf), a + len(x))
    buf[a:b] += x[:b - a]


def sine(f, d, ph=0.0):
    t = T(d)
    if callable(f):
        return np.sin(2 * np.pi * np.cumsum(f(t)) / SR + ph).astype(np.float32)
    return np.sin(2 * np.pi * f * t + ph).astype(np.float32)


def saw(f, t, nh=12):
    y = np.zeros_like(t)
    for k in range(1, nh + 1):
        if f * k > SR / 2 - 1000:
            break
        y += np.sin(2 * np.pi * f * k * t) / k
    return y.astype(np.float32)


# ============================================================ SFX

def sfx_boom(d=4.0, seed=1):
    t = T(d)
    f = 55 * np.exp(-t * 0.9) + 26
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(len(t), 1.1)
    x += lp(white(len(t), seed), 200) * env_exp(len(t), 0.25) * 2
    return norm(reverb(x, 3.0, 0.35), 0.95)


def sfx_hit(d=3.0, seed=2):
    t = T(d)
    x = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-t * 6) + 35) / SR) * env_exp(len(t), 0.5)
    x += bp(white(len(t), seed), 200, 5000) * env_exp(len(t), 0.06) * 1.2
    x += np.sin(2 * np.pi * 1180 * t) * 0.15 * env_exp(len(t), 0.8) + np.sin(2 * np.pi * 1253 * t) * 0.12 * env_exp(len(t), 0.9)
    return norm(reverb(x, 3.5, 0.4), 0.95)


def sfx_stinger(d=3.5, seed=3):
    t = T(d)
    swell = np.clip(t / 0.25, 0, 1) * env_exp(len(t), 1.0)
    x = np.zeros_like(t)
    for i, f in enumerate((880, 932, 988, 1046, 1480, 1568)):
        vib = 1 + 0.004 * np.sin(2 * np.pi * (5 + i) * t)
        x += saw(f, t * vib, 6) * (0.6 if f < 1200 else 0.35)
    x = bp(x, 400, 7000) * swell
    x += sfx_hit(d, seed)[:len(t)] * 0.6
    return norm(reverb(x, 3.0, 0.45), 0.9)


def sfx_riser(d=5.0, seed=4):
    t = T(d)
    k = t / d
    n = white(len(t), seed)
    out = np.zeros_like(t)
    # sweep band by blocks
    blk = 2400
    for i in range(0, len(t), blk):
        f0 = 200 + 3000 * (i / len(t)) ** 2
        seg = bp(n[i:i + blk + 2000], f0, f0 * 2.2)[:blk]
        out[i:i + len(seg)] = seg
    out *= k ** 2
    out += np.sin(2 * np.pi * np.cumsum(60 + 300 * k ** 3) / SR) * 0.3 * k ** 2
    return norm(reverb(out, 2.0, 0.3), 0.8)


def sfx_tape_click(d=0.3, seed=5):
    x = np.zeros(int(d * SR), np.float32)
    x[:400] = bp(white(400, seed), 800, 6000) * np.linspace(1, 0, 400)
    x[2400:2700] += bp(white(300, seed + 1), 300, 3000) * np.linspace(0.6, 0, 300)
    return norm(x, 0.7)


def bed_tape_hiss(d, seed=6):
    x = hp(pink(int(d * SR), seed), 1500) * 0.2
    x += lp(brown(int(d * SR), seed + 1), 120) * 0.5
    return x.astype(np.float32)


def knock_one(seed, strength=1.0, pitch=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 110 * pitch * t) * env_exp(n, 0.06)
    x += bp(white(n, seed), 250 * pitch, 1800 * pitch) * env_exp(n, 0.02) * 1.5
    return (x * strength).astype(np.float32)


def sfx_knock(d=2.4, seed=7, n=3, strength=1.0, gapt=0.42):
    buf = np.zeros(int(d * SR), np.float32)
    for i in range(n):
        place(buf, knock_one(seed + i, strength * (0.9 + 0.1 * (i % 2))), 0.05 + i * gapt)
    return norm(reverb(buf, 0.8, 0.25), 0.9 * strength)


def sfx_knock_soft(d=2.0, seed=8):
    return sfx_knock(d, seed, 2, 0.55, 0.55)


def sfx_glass_tap(d=2.0, seed=9):
    buf = np.zeros(int(d * SR), np.float32)
    for i in range(3):
        place(buf, knock_one(seed + i, 0.7, 4.0), 0.1 + i * 0.5)
    return norm(reverb(buf, 0.6, 0.2), 0.6)


def sfx_creak(d=1.8, seed=10, base=180):
    t = T(d)
    r = rng(seed)
    jitter = np.interp(t, np.linspace(0, d, 30), r.uniform(-1, 1, 30))
    f = base + 120 * np.sin(np.pi * t / d) + 40 * jitter
    ph = np.cumsum(f) / SR
    x = (2 * (ph % 1) - 1)
    x *= (0.5 + 0.5 * (r.rand(len(t)) > 0.3))
    x = bp(x.astype(np.float32), 300, 2500) * np.sin(np.pi * t / d) ** 0.5
    return norm(reverb(x, 1.0, 0.3), 0.7)


def sfx_static(d=3.0, seed=11):
    n = int(d * SR)
    x = bp(white(n, seed), 600, 5000) * 0.5
    r = rng(seed)
    for i in range(int(d * 25)):
        a = r.randint(0, n - 200)
        x[a:a + 120] += r.uniform(-1, 1) * 2
    x *= adsr(n, 0.02, 0.3)
    return norm(x, 0.6)


def sfx_eas(d=2.5, seed=0):
    t = T(d)
    x = (np.sin(2 * np.pi * 853 * t) + np.sin(2 * np.pi * 960 * t)) * 0.5 * adsr(len(t), 0.02, 0.1)
    return norm(lp(x.astype(np.float32), 4000), 0.5)


def sfx_tv_on(d=1.0, seed=12):
    t = T(d)
    x = np.sin(2 * np.pi * 15000 * t) * 0.08 * env_exp(len(t), 0.5)
    x += bp(white(len(t), seed), 200, 4000) * env_exp(len(t), 0.05)
    x[:300] += white(300, seed + 1) * 1.5
    return norm(x, 0.6)


def sfx_beep(f=1000, d=0.15, n=1, gapt=0.2, decay=None):
    buf = np.zeros(int((n * gapt + d + 0.5) * SR), np.float32)
    for i in range(n):
        ff = f[i] if isinstance(f, (list, tuple)) else f
        x = sine(ff, d) * adsr(int(d * SR), 0.005, 0.03)
        place(buf, x, i * gapt)
    return norm(reverb(buf, 0.4, 0.15), 0.5)


def porcelain(d=2.5, seed=13, density=1.0):
    """Signature creature sound: tiny ceramic clicks, a thin glassy ring and a dry hiss."""
    n = int(d * SR)
    buf = np.zeros(n, np.float32)
    r = rng(seed)
    nclick = int(14 * d * density)
    for i in range(nclick):
        at = r.uniform(0, d - 0.1)
        f = r.uniform(2500, 6500)
        m = int(0.03 * SR)
        tt = np.arange(m) / SR
        ping = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.004)
        ping += np.sin(2 * np.pi * f * 1.51 * tt) * np.exp(-tt / 0.003) * 0.5
        place(buf, (ping * r.uniform(0.3, 1.0)).astype(np.float32), at)
    t = T(d)
    ring = np.sin(2 * np.pi * np.cumsum(5200 + 300 * np.sin(2 * np.pi * 0.7 * t)) / SR) * 0.035 * np.sin(np.pi * t / d)
    hiss = bp(white(n, seed + 3), 3000, 9000) * 0.06 * np.sin(np.pi * t / d) ** 2
    x = buf + ring + hiss
    return norm(reverb(x.astype(np.float32), 1.4, 0.35), 0.6)


def sfx_creature_step(d=0.8, seed=14):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 70 * t) * env_exp(n, 0.05) * 0.8
    x += bp(white(n, seed), 1500, 7000) * env_exp(n, 0.01) * 0.4
    x += porcelain(d, seed, 0.3)[:n] * 0.4
    return norm(reverb(x.astype(np.float32), 1.0, 0.25), 0.6)


def sfx_creature_rush(d=1.6, seed=15):
    t = T(d)
    p = porcelain(d, seed, 4.0)[:len(t)] * (t / d) ** 1.5
    wh = bp(white(len(t), seed + 1), 300, 3000) * (t / d) ** 3
    x = p + wh * 0.6
    return norm(x, 0.85)


def sfx_heartbeat(d=8.0, seed=16, bpm=78):
    buf = np.zeros(int(d * SR), np.float32)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    beat = (np.sin(2 * np.pi * 50 * t) * env_exp(n, 0.06)).astype(np.float32)
    k = 0
    tt = 0.0
    while tt < d - 0.5:
        place(buf, beat, tt)
        place(buf, beat * 0.6, tt + 0.28)
        tt += 60 / (bpm + k * 2)
        k += 1
    return norm(lp(buf, 200), 0.9)


def footstep(seed, soft=False, forest=False):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 90 * t) * env_exp(n, 0.03) * (0.4 if soft else 0.8)
    if forest:
        x += bp(white(n, seed), 1000, 6000) * env_exp(n, 0.05) * 0.8
    else:
        x += bp(white(n, seed), 400, 3000) * env_exp(n, 0.015) * (0.3 if soft else 0.7)
    return x.astype(np.float32)


def sfx_steps(d=6.0, seed=17, interval=0.55, soft=False, forest=False):
    buf = np.zeros(int(d * SR), np.float32)
    tt, i = 0.05, 0
    while tt < d - 0.3:
        place(buf, footstep(seed + i, soft, forest) * (0.8 + 0.2 * (i % 2)), tt)
        tt += interval * (1 + 0.05 * np.sin(i))
        i += 1
    return norm(reverb(buf, 0.9, 0.2), 0.5)


def bed_music_loud(d, seed=18, muffle=1400):
    """Loud party track from a neighbour's speaker (heard through the courtyard)."""
    t = T(d)
    bpm = 124
    beat = 60 / bpm
    buf = np.zeros(len(t), np.float32)
    kick_n = int(0.3 * SR)
    kt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-kt * 25) + 45) / SR) * env_exp(kick_n, 0.12)
    hat = hp(white(int(0.05 * SR), seed), 6000) * env_exp(int(0.05 * SR), 0.01)
    i = 0
    while i * beat < d:
        place(buf, kick.astype(np.float32), i * beat)
        place(buf, hat * 0.3, i * beat + beat / 2)
        i += 1
    bass_notes = [55, 55, 65.4, 49]
    bass = np.zeros_like(t)
    for j in range(int(d / beat) + 1):
        f = bass_notes[(j // 4) % 4]
        a, b = int(j * beat * SR + beat * SR / 2), int((j + 1) * beat * SR)
        b = min(b, len(t))
        if a < len(t):
            tt = t[a:b] - t[a]
            bass[a:b] = saw(f, tt, 6) * np.exp(-tt * 6)
    chord = np.zeros_like(t)
    for j in range(int(d / (beat * 2)) + 1):
        base = [220, 261.6, 196, 246.9][(j // 2) % 4]
        a = int(j * beat * 2 * SR)
        b = min(len(t), a + int(0.25 * SR))
        if a < len(t):
            tt = t[a:b] - t[a]
            chord[a:b] = (saw(base, tt, 5) + saw(base * 1.26, tt, 5) + saw(base * 1.5, tt, 5)) * np.exp(-tt * 8) * 0.3
    x = buf + bass * 0.5 + chord
    x = lp(x, muffle)
    return norm(reverb(x, 1.5, 0.35)[:len(t)], 0.8)


def bed_headphones(d, seed=19):
    x = bed_music_loud(d, seed, 9000)
    return norm(hp(x, 1800) * adsr(len(x), 0.05, 0.5), 0.35)


def babble(d, seed=20, lo=300, hi=3000):
    t = T(d)
    r = rng(seed)
    xp = np.arange(0, d + 0.3, 0.18)
    syl = np.interp(t, xp, np.clip(r.randn(len(xp)) * 0.6 + 0.6, 0, 1.5))
    x = bp(pink(len(t), seed), lo, hi) * lp(syl.astype(np.float32), 8)
    vow = np.sin(2 * np.pi * np.cumsum(140 + 30 * np.sin(2 * np.pi * 0.5 * t)) / SR)
    x += vow * 0.15 * lp(syl.astype(np.float32), 8)
    return x.astype(np.float32)


def bed_tv_show(d, seed=21):
    x = babble(d, seed) + bed_music_loud(d, seed, 2500) * 0.15
    return norm(reverb(x, 0.8, 0.3)[:int(d * SR)], 0.4)


def bed_tv_far(d, seed=22):
    return norm(lp(babble(d, seed), 1200), 0.2)


def sfx_glass(d=2.5, seed=23):
    n = int(d * SR)
    x = hp(white(n, seed), 2000) * env_exp(n, 0.15)
    r = rng(seed)
    for i in range(18):
        place(x, (np.sin(2 * np.pi * r.uniform(3000, 8000) * T(0.2)) * env_exp(int(0.2 * SR), 0.04) * r.uniform(0.2, 0.6)).astype(np.float32), r.uniform(0.02, 1.2))
    return norm(reverb(x, 1.2, 0.3), 0.6)


def sfx_window_open(d=1.2, seed=24):
    n = int(d * SR)
    x = bp(white(n, seed), 400, 3000) * np.sin(np.pi * np.arange(n) / n) * 0.5
    x[-3000:] += knock_one(seed, 0.5, 2.0)[:3000]
    return norm(x, 0.5)


def sfx_window_slam(d=1.5, seed=25):
    n = int(d * SR)
    x = np.zeros(n, np.float32)
    place(x, knock_one(seed, 1.0, 1.4) * 2, 0.05)
    place(x, hp(white(int(0.3 * SR), seed), 3000) * env_exp(int(0.3 * SR), 0.05), 0.05)
    return norm(reverb(x, 1.0, 0.3), 0.85)


def sfx_rustle(d=1.5, seed=26, lo=1500, hi=8000):
    n = int(d * SR)
    r = rng(seed)
    am = np.interp(np.arange(n), np.linspace(0, n, 20), np.abs(r.randn(20)))
    return norm(bp(white(n, seed), lo, hi) * am.astype(np.float32) * np.sin(np.pi * np.arange(n) / n), 0.3)


def sfx_pen(d=3.0, seed=27):
    n = int(d * SR)
    r = rng(seed)
    am = (np.interp(np.arange(n), np.linspace(0, n, int(d * 12)), r.rand(int(d * 12))) > 0.35).astype(np.float32)
    am = lp(am, 30)
    return norm(bp(white(n, seed), 2500, 9000) * am * adsr(n, 0.05, 0.3), 0.25)


def sfx_stamp(d=1.0, seed=28):
    x = np.zeros(int(d * SR), np.float32)
    place(x, knock_one(seed, 1.0, 0.8), 0.02)
    return norm(reverb(x, 0.5, 0.2), 0.6)


def sfx_typewriter(d=3.0, seed=29):
    buf = np.zeros(int(d * SR), np.float32)
    r = rng(seed)
    tt = 0.0
    while tt < d - 0.2:
        place(buf, hp(white(600, int(tt * 100)), 1500) * env_exp(600, 0.002), tt)
        tt += r.uniform(0.08, 0.2)
    return norm(buf, 0.35)


def sfx_lock(d=0.8, seed=30):
    x = np.zeros(int(d * SR), np.float32)
    for i, at in enumerate((0.05, 0.22)):
        place(x, (np.sin(2 * np.pi * 2800 * T(0.05)) * env_exp(int(0.05 * SR), 0.008)).astype(np.float32), at)
        place(x, hp(white(800, seed + i), 2000) * env_exp(800, 0.003), at)
    return norm(reverb(x, 0.5, 0.2), 0.5)


def sfx_bubble(d=3.0, seed=31):
    buf = np.zeros(int(d * SR), np.float32)
    r = rng(seed)
    for i in range(14):
        f0 = r.uniform(300, 900)
        dd = 0.08
        b = sine(lambda tt: f0 + 2000 * tt, dd) * env_exp(int(dd * SR), 0.02)
        place(buf, b * r.uniform(0.2, 0.6), r.uniform(0, d - 0.2))
    return norm(reverb(buf, 1.0, 0.3), 0.3)


def sfx_climb(d=5.0, seed=32):
    n = int(d * SR)
    buf = np.zeros(n, np.float32)
    r = rng(seed)
    tt = 0.1
    while tt < d - 0.5:
        sc_n = int(0.25 * SR)
        s = bp(white(sc_n, int(tt * 77)), 800, 4000) * np.sin(np.pi * np.arange(sc_n) / sc_n)
        place(buf, s * 0.5, tt)
        tt += r.uniform(0.5, 0.9)
    buf += porcelain(d, seed, 0.6)[:n] * 0.6
    return norm(reverb(buf, 1.0, 0.3), 0.55)


def sfx_shelf_crash(d=3.0, seed=33):
    n = int(d * SR)
    x = bp(white(n, seed), 200, 8000) * env_exp(n, 0.25)
    r = rng(seed)
    for i in range(10):
        place(x, (np.sin(2 * np.pi * r.uniform(600, 2500) * T(0.4)) * env_exp(int(0.4 * SR), 0.08) * 0.4).astype(np.float32), r.uniform(0.1, 2.0))
    return norm(reverb(x, 1.2, 0.3), 0.8)


def bed_vent_tick(d, seed=34):
    buf = np.zeros(int(d * SR), np.float32)
    tt = 0.0
    i = 0
    while tt < d - 0.1:
        g = 0.3 + 0.7 * (tt / d)
        place(buf, (np.sin(2 * np.pi * 3300 * T(0.03)) * env_exp(int(0.03 * SR), 0.004) * g).astype(np.float32), tt)
        place(buf, hp(white(500, i), 1500) * env_exp(500, 0.002) * g * 0.6, tt)
        tt += 0.62 - 0.25 * (tt / d)
        i += 1
    return norm(reverb(lp(buf, 6000), 0.5, 0.4), 0.5)


def sfx_vent_crash(d=2.0, seed=35):
    n = int(d * SR)
    x = bp(white(n, seed), 500, 6000) * env_exp(n, 0.2)
    for i, f in enumerate((420, 655, 980, 1530)):
        x += np.sin(2 * np.pi * f * T(d)) * env_exp(n, 0.4) * 0.15
    return norm(reverb(lp(x, 3000), 1.5, 0.4), 0.4)


def sfx_branch(d=1.0, seed=36):
    x = np.zeros(int(d * SR), np.float32)
    place(x, bp(white(2000, seed), 800, 7000) * env_exp(2000, 0.004), 0.02)
    place(x, bp(white(1500, seed + 1), 600, 5000) * env_exp(1500, 0.004) * 0.6, 0.09)
    return norm(reverb(x, 1.5, 0.4), 0.6)


def engine(d, seed=37, f=38, away=False):
    t = T(d)
    ff = f * (1 - 0.3 * (t / d) if away else 1) + 2 * np.sin(2 * np.pi * 0.3 * t)
    ph = 2 * np.pi * np.cumsum(ff) / SR
    x = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.2 * np.sin(5 * ph)
    x += lp(brown(len(t), seed), 300) * 2
    x = lp(x.astype(np.float32), 500)
    if away:
        x *= np.exp(-t / (d * 0.35))
    return norm(x, 0.6)


def sfx_bus_door(d=1.5, seed=38):
    n = int(d * SR)
    x = hp(white(n, seed), 2500) * env_exp(n, 0.3) * 0.5
    place(x, knock_one(seed, 1.0, 0.9) * 1.5, 0.5)
    return norm(reverb(x, 1.0, 0.3), 0.6)


def bed_wheels(d, seed=39):
    n = int(d * SR)
    buf = np.zeros(n, np.float32)
    tt = 0.0
    i = 0
    while tt < d - 0.05:
        place(buf, bp(white(400, i + seed), 700, 5000) * env_exp(400, 0.002) * (0.6 + 0.4 * (i % 3 == 0)), tt)
        tt += 0.055
        i += 1
    buf += lp(brown(n, seed), 400) * 0.3
    return norm(reverb(buf, 1.5, 0.35)[:n] * adsr(n, 0.1, 1.0), 0.6)


def bed_crowd(d, seed=40):
    n = int(d * SR)
    buf = np.zeros(n, np.float32)
    for k in range(5):
        buf += porcelain(d, seed + k, 1.5)[:n] * 0.4
    buf += bp(pink(n, seed), 200, 1500) * 0.15
    return norm(buf * adsr(n, 1.0, 1.0), 0.6)


def sfx_scratch(d=3.0, seed=41):
    n = int(d * SR)
    buf = np.zeros(n, np.float32)
    for i in range(4):
        m = int(0.5 * SR)
        s = bp(white(m, seed + i), 1500, 6000) * np.sin(np.pi * np.arange(m) / m) ** 2
        place(buf, s * 0.6, 0.2 + i * 0.65)
    return norm(reverb(buf, 0.8, 0.2), 0.5)


def sfx_birds(d=6.0, seed=42):
    buf = np.zeros(int(d * SR), np.float32)
    r = rng(seed)
    for i in range(7):
        f0 = r.uniform(2500, 4500)
        dd = r.uniform(0.08, 0.18)
        ch = sine(lambda tt: f0 + 2500 * np.sin(np.pi * tt / dd), dd) * np.sin(np.pi * np.arange(int(dd * SR)) / int(dd * SR))
        place(buf, ch * r.uniform(0.2, 0.5), r.uniform(0, d - 0.3))
    return norm(reverb(buf, 2.0, 0.5), 0.25)


def sfx_drip(d=4.0, seed=43):
    buf = np.zeros(int(d * SR), np.float32)
    for i, at in enumerate((0.2, 1.5, 2.9)):
        dd = 0.1
        place(buf, sine(lambda tt: 900 + 1800 * tt / dd, dd) * env_exp(int(dd * SR), 0.02), at)
    return norm(reverb(buf, 2.5, 0.55), 0.4)


def sfx_tap(d=0.2, seed=44):
    x = np.zeros(int(d * SR), np.float32)
    place(x, hp(white(300, seed), 2000) * env_exp(300, 0.002), 0.01)
    return norm(x, 0.25)


SFX = {
    'boom': sfx_boom, 'hit': sfx_hit, 'stinger': sfx_stinger, 'riser': sfx_riser, 'tape_click': sfx_tape_click,
    'knock': sfx_knock, 'knock_soft': sfx_knock_soft, 'glass_tap': sfx_glass_tap,
    'door_creak': lambda: sfx_creak(1.8, 10, 160), 'gate_creak': lambda: sfx_creak(2.8, 11, 120),
    'static': sfx_static, 'eas_tone': sfx_eas, 'tv_on': sfx_tv_on,
    'low_batt': lambda: sfx_beep([1320, 990], 0.12, 2, 0.16), 'error_beep': lambda: sfx_beep([660, 440], 0.12, 2, 0.16),
    'dial_beep': lambda: sfx_beep(425, 0.8, 1), 'tap': sfx_tap,
    'porcelain': porcelain, 'creature_step': sfx_creature_step, 'creature_rush': sfx_creature_rush,
    'heartbeat': sfx_heartbeat, 'footsteps': lambda: sfx_steps(6, 17, 0.55), 'footsteps_soft': lambda: sfx_steps(6, 18, 0.75, True),
    'footsteps_forest': lambda: sfx_steps(8, 19, 0.6, True, True), 'run': lambda: sfx_steps(4, 20, 0.28),
    'glass': sfx_glass, 'window_open': sfx_window_open, 'window_slam': sfx_window_slam,
    'sheets': lambda: sfx_rustle(1.5, 26, 800, 6000), 'paper': lambda: sfx_rustle(1.2, 27, 1500, 9000),
    'pen_write': sfx_pen, 'stamp': sfx_stamp, 'typewriter': sfx_typewriter, 'lock': sfx_lock, 'bubble': sfx_bubble,
    'climb': sfx_climb, 'shelf_crash': sfx_shelf_crash, 'vent_crash': sfx_vent_crash, 'branch': sfx_branch,
    'engine_far': lambda: engine(7, 37, 32) * 0.5, 'engine_away': lambda: engine(8, 38, 42, True), 'door_slam_bus': sfx_bus_door,
    'scratch': sfx_scratch, 'birds': sfx_birds, 'drip': sfx_drip, 'pa_echo': lambda: np.zeros(10, np.float32),
}

BEDS = {
    'tape_hiss': bed_tape_hiss, 'music_loud': bed_music_loud, 'headphones': bed_headphones, 'tv_show': bed_tv_show,
    'tv_far': bed_tv_far, 'vent_tick': bed_vent_tick, 'wheels': bed_wheels, 'crowd_shuffle': bed_crowd,
    'radio_static': lambda d, seed=0: norm(sfx_static(d, 77) * 0.6 + bp(white(int(d * SR), 78), 1000, 3000) * 0.05, 0.4),
    'engine_idle': lambda d, seed=0: engine(d, 39, 36) * 0.6,
}

# ============================================================ AMBIENCE (absolute-time generators)


def amb(kind, t0, d, seed=0):
    n = int(d * SR)
    t = t0 + np.arange(n) / SR
    s = int(t0 * 10) + seed
    z = np.zeros(n, np.float32)
    if kind == 'none':
        return z
    wind = lambda g, lo=150, hi=900: bp(pink(n, s), lo, hi) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t) * np.sin(2 * np.pi * 0.031 * t + 1)) * g
    hum = lambda f, g: (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)) * g
    if kind == 'city_dawn':
        z = wind(0.5) + lp(brown(n, s + 1), 120) * 0.4
    elif kind == 'city_night':
        z = wind(0.55) + lp(brown(n, s + 1), 100) * 0.5 + hum(100, 0.006)
    elif kind in ('room_dawn', 'room_night'):
        z = lp(brown(n, s), 200) * 0.25 + hum(50, 0.01)
        if kind == 'room_night':
            # clock ticking
            tick = (np.sin(2 * np.pi * 2600 * np.arange(int(0.02 * SR)) / SR) * env_exp(int(0.02 * SR), 0.003)).astype(np.float32)
            for k in np.arange(np.ceil(t0), t0 + d, 1.0):
                place(z, tick * 0.05, k - t0)
    elif kind == 'drone_room':
        z = hum(41, 0.05) + lp(brown(n, s), 150) * 0.3
    elif kind == 'store':
        z = hum(100, 0.02) + hp(white(n, s), 7000) * 0.004 + lp(brown(n, s), 200) * 0.2
    elif kind == 'hospital':
        z = hum(100, 0.015) + bp(pink(n, s), 200, 1200) * 0.12 + lp(brown(n, s), 200) * 0.2
    elif kind == 'stairs':
        z = wind(0.35, 100, 600) + lp(brown(n, s), 150) * 0.3
    elif kind == 'subway':
        z = wind(0.6, 60, 400) + lp(brown(n, s), 80) * 0.6
    elif kind == 'forest':
        z = wind(0.45, 300, 2500)
        cr = np.zeros(n, np.float32)
        for k in np.arange(np.ceil(t0 * 2) / 2, t0 + d, 0.5):
            m = int(0.12 * SR)
            ch = np.sin(2 * np.pi * 4200 * np.arange(m) / SR) * (np.sin(2 * np.pi * 60 * np.arange(m) / SR) > 0)
            place(cr, (ch * np.hanning(m) * 0.02).astype(np.float32), k - t0)
        z = z + cr
    elif kind == 'convoy':
        z = wind(0.45) + engine(d, s, 34) * 0.12
    elif kind == 'car_inside':
        z = lp(brown(n, s), 150) * 0.35 + hum(60, 0.004)
    elif kind == 'lab_hum':
        z = hum(50, 0.03) + bp(pink(n, s), 300, 2000) * 0.03 + lp(brown(n, s), 120) * 0.2
    elif kind == 'wind':
        z = wind(0.6)
    return z.astype(np.float32) * 0.5


# ============================================================ MUSIC (absolute time => continuous)

NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)


def pad(t, freqs, g, cutoff=900, seed=0):
    y = np.zeros_like(t)
    for i, f in enumerate(freqs):
        for det in (-0.12, 0.0, 0.11):
            ff = f * (1 + det / 100 * 3)
            y += saw(ff, t, 8) * 0.33
    y = lp(y.astype(np.float32), cutoff)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t + seed)
    return (y * lfo * g).astype(np.float32)


def plinks(t0, d, notes, every, g, seed=0, decay=1.6):
    n = int(d * SR)
    buf = np.zeros(n + int(4 * SR), np.float32)
    k0 = int(np.floor(t0 / every))
    k1 = int(np.ceil((t0 + d) / every))
    for k in range(k0 - 2, k1 + 1):
        r = rng(k * 7 + seed)
        if r.rand() < 0.25:
            continue
        f = NOTE(notes[r.randint(len(notes))])
        at = k * every + r.uniform(0, every * 0.3) - t0
        m = int(4 * SR)
        tt = np.arange(m) / SR
        x = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3) + 0.1 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 6)) * np.exp(-tt / decay) * np.clip(tt / 0.005, 0, 1)
        a = int(at * SR)
        if a + m <= 0 or a >= len(buf):
            continue
        if a < 0:
            x = x[-a:]
            a = 0
        b = min(len(buf), a + len(x))
        buf[a:b] += x[:b - a] * g * r.uniform(0.6, 1.0)
    return buf[:n]


def music(cue, t0, d):
    n = int(d * SR)
    t = t0 + np.arange(n) / SR
    z = np.zeros(n, np.float32)
    D2, F2, A2 = NOTE(38), NOTE(41), NOTE(45)
    if cue == 'calm':
        z = pad(t, [NOTE(50), NOTE(53), NOTE(57)], 0.05, 700) + pad(t, [D2], 0.05, 300)
        z += plinks(t0, d, [62, 65, 69, 72, 74, 77], 2.6, 0.06, 1)
    elif cue == 'doc':
        z = pad(t, [NOTE(50), NOTE(57)], 0.05, 600) + np.sin(2 * np.pi * D2 / 2 * t) * 0.06
        pulse = (np.sin(2 * np.pi * 1.0 * t) > 0.995).astype(np.float32)
        z += lp(pulse, 2000) * 0.5
        z += plinks(t0, d, [74, 77, 81], 3.3, 0.04, 2)
    elif cue == 'tense':
        z = np.sin(2 * np.pi * D2 / 2 * t) * 0.1 + np.sin(2 * np.pi * A2 / 2 * t) * 0.05
        trem = 0.5 + 0.5 * np.sin(2 * np.pi * 6.5 * t)
        z += pad(t, [NOTE(74), NOTE(75)], 0.018, 3500) * trem
        beat = np.zeros(n, np.float32)
        for k in np.arange(np.ceil(t0 / 1.6) * 1.6, t0 + d, 1.6):
            m = int(0.6 * SR)
            tt = np.arange(m) / SR
            place(beat, (np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.15) * 0.35).astype(np.float32), k - t0)
        z += beat
    elif cue in ('dread', 'title', 'end'):
        z = (np.sin(2 * np.pi * 36.7 * t) * 0.14 + np.sin(2 * np.pi * 55 * t) * 0.06 + np.sin(2 * np.pi * 55.6 * t) * 0.06)
        sw = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
        for f in (1245, 1318.5, 1760.7, 2093):
            z += np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.2 * t) * 3) * 0.006 * sw
        z += pad(t, [NOTE(38), NOTE(39)], 0.03, 400)
    elif cue == 'action':
        z = np.sin(2 * np.pi * D2 / 2 * t) * 0.12
        beat = 60 / 132
        buf = np.zeros(n + SR, np.float32)
        for k in np.arange(np.ceil(t0 / (beat / 2)) * (beat / 2), t0 + d, beat / 2):
            m = int(0.4 * SR)
            tt = np.arange(m) / SR
            idx = int(round(k / (beat / 2)))
            if idx % 4 in (0, 3):
                hit = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 18) + 48) / SR) * np.exp(-tt / 0.18) * 0.5
                place(buf, hit.astype(np.float32), k - t0)
            st = saw(D2 if (idx // 8) % 2 == 0 else NOTE(39), tt[:int(0.12 * SR)], 10) * np.exp(-tt[:int(0.12 * SR)] / 0.05) * 0.12
            place(buf, lp(st.astype(np.float32), 1200), k - t0)
        z += buf[:n]
        z += pad(t, [NOTE(74), NOTE(75), NOTE(80)], 0.012, 4000)
    elif cue == 'silence':
        z = np.sin(2 * np.pi * 36.7 * t) * 0.05 + lp(brown(n, int(t0)), 60) * 0.1
    elif cue == 'sad':
        z = pad(t, [NOTE(50), NOTE(53), NOTE(57)], 0.035, 600)
        z += plinks(t0, d, [62, 65, 69, 70, 74], 1.9, 0.08, 5, 2.4)
    elif cue == 'hope':
        z = pad(t, [NOTE(50), NOTE(54), NOTE(57), NOTE(62)], 0.04, 1200)
        z += plinks(t0, d, [62, 66, 69, 74, 78], 2.2, 0.05, 6)
    return z.astype(np.float32)
