"""Procedural score + SFX, mixed under the voice-over.  usage: python audio.py voice.mp3 out.wav"""
import sys
import subprocess
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
DUR = 123.2
N = int(SR * DUR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR


def env_curve(points):
    xs, ys = zip(*points)
    return np.interp(t_all, xs, ys)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def bp(x, f0, f1):
    return sosfilt(butter(2, [f0, f1], 'band', fs=SR, output='sos'), x)


def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * gain


def tone(f, d, decay=6.0, attack=0.005, kind='sine'):
    t = np.arange(int(d * SR)) / SR
    if kind == 'sine':
        s = np.sin(2 * np.pi * f * t)
    else:
        s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)
    e = np.minimum(1, t / attack) * np.exp(-decay * t)
    return s * e


def reverb(x, secs=2.5, mix=0.35):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.0 / secs * 2)
    ir = lp(ir, 5000)
    wet = fftconvolve(x, ir)[:len(x)]
    wet /= (np.abs(wet).max() + 1e-9)
    return x * (1 - mix) + wet * mix * np.abs(x).max()


# ---------------------------------------------------------------- music bed
def music():
    m = np.zeros(N)
    inten = env_curve([(0, 0.35), (8, 0.45), (20, 0.5), (24, 0.6), (34, 0.85), (40, 0.9), (54, 0.8), (62, 0.7),
                       (73, 0.85), (95, 1.0), (108, 1.15), (111.38, 1.2), (111.4, 0), (DUR, 0)])
    # drone: A minor-ish low cluster with slow beating
    for f, a in ((55, 0.5), (55.4, 0.4), (82.4, 0.3), (110, 0.18), (130.8, 0.12), (164.8, 0.07)):
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t_all + f)
        m += a * np.sin(2 * np.pi * f * t_all + 0.3 * np.sin(2 * np.pi * 0.2 * t_all)) * lfo
    # airy noise pad
    air = lp(hp(rng.standard_normal(N), 300), 1800) * 0.08
    m += air * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t_all))
    # rising tension string (detuned saws, filtered) from 21s on, and again in the climax
    rise = env_curve([(0, 0), (21, 0), (34, 0.5), (39.5, 0.8), (44, 0.4), (54, 0.2), (73, 0.4), (95, 0.8), (111.38, 1.1),
                      (111.4, 0), (DUR, 0)])
    saw = np.zeros(N)
    for f in (220, 220 * 1.006, 261.6 * 1.003, 311.1):   # A, C, Eb -> dissonant
        ph_ = (f * t_all) % 1.0
        saw += 2 * ph_ - 1
    saw = lp(saw, 900) * 0.12
    m += saw * rise
    # sparse piano-like notes in the opening (minor)
    notes = [440, 523.3, 392, 349.2, 329.6, 440, 293.7, 329.6]
    for k, st in enumerate(np.arange(0.6, 21, 2.4)):
        n = tone(notes[k % len(notes)], 2.5, decay=2.2, kind='rich') * 0.22
        add(m, st, n)
    for k, st in enumerate(np.arange(54.6, 72, 2.9)):
        n = tone(notes[(k * 3) % len(notes)] * 0.5, 3.0, decay=1.6, kind='rich') * 0.2
        add(m, st, n)
    # pulse (heartbeat-ish) during panic and the climax
    pulse = np.zeros(N)
    def beats(t0, t1, bpm, g):
        for st in np.arange(t0, t1, 60 / bpm):
            add(pulse, st, tone(52, 0.35, decay=12) * g)
            add(pulse, st + 0.18, tone(48, 0.3, decay=14) * g * 0.6)
    beats(29.5, 39.6, 72, 0.9)
    beats(39.6, 54.0, 110, 0.7)
    beats(87.4, 101.4, 84, 0.9)
    beats(104.5, 107.9, 96, 0.8)
    m += pulse
    m *= inten
    m = reverb(m, 3.0, 0.3)
    m[int(111.4 * SR):] = 0  # sharp silence for the finale
    return m


# ---------------------------------------------------------------- sfx
def layer(*parts):
    n = max(int(o * SR) + len(x) for x, o in parts)
    out = np.zeros(n)
    for x, o in parts:
        i = int(o * SR); out[i:i + len(x)] += x
    return out


def ping(pitch=1.0, g=1.0):
    s = layer((tone(1318 * pitch, 0.5, 9) * 0.6, 0), (tone(1760 * pitch, 0.45, 9) * 0.5, 0.07))
    return s * g


def buzz(d, g=1.0):
    t = np.arange(int(d * SR)) / SR
    am = (np.sin(2 * np.pi * 7 * t) > -0.2).astype(float)
    s = (np.sin(2 * np.pi * 150 * t) + 0.5 * np.sign(np.sin(2 * np.pi * 150 * t))) * am
    s = lp(s, 700) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.03)
    return s * 0.35 * g


def whoosh(d, f0=300, f1=3000, g=1.0, rev=False):
    n = int(d * SR)
    x = rng.standard_normal(n)
    t = np.arange(n) / SR
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        k = i / n
        fc = f0 + (f1 - f0) * (k if not rev else 1 - k)
        out[i:i + seg] = bp(x[max(0, i - 2048):i + seg], max(30, fc * 0.7), min(SR / 2 - 100, fc * 1.3))[-len(out[i:i + seg]):]
    e = np.sin(np.pi * t / d) ** 2
    if rev:
        e = (t / d) ** 2.5
    return out * e * g


def boom(d=3.5, f0=70, f1=28, g=1.0):
    t = np.arange(int(d * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 3)
    ph_ = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph_) * np.exp(-t * 1.1)
    s += lp(rng.standard_normal(len(t)), 200) * np.exp(-t * 4) * 0.6
    return s * g


def click(g=1.0):
    t = np.arange(int(0.05 * SR)) / SR
    return rng.standard_normal(len(t)) * np.exp(-t * 200) * g


def glitch(d, g=1.0):
    n = int(d * SR)
    s = np.zeros(n)
    i = 0
    while i < n:
        L = int(rng.uniform(0.01, 0.05) * SR)
        f = rng.uniform(200, 3000)
        tt = np.arange(L) / SR
        s[i:i + L] = (np.sign(np.sin(2 * np.pi * f * tt)) * rng.uniform(0.2, 1))[:len(s[i:i + L])]
        i += L + int(rng.uniform(0, 0.02) * SR)
    return lp(s, 6000) * 0.25 * g


def ring(d):
    t = np.arange(int(d * SR)) / SR
    s = (np.sin(2 * np.pi * 425 * t)) * ((t % 1.0) < 0.6)
    return s * 0.25


def sfx():
    s = np.zeros(N)
    add(s, 0.15, boom(2.0, 120, 40, 0.5))
    add(s, 0.1, whoosh(0.8, 2000, 300, 0.5, rev=False))
    for nt in (3.2, 4.1, 4.6, 5.0, 5.6, 6.4, 7.0, 7.5):
        add(s, nt, buzz(0.35, 0.6))
    add(s, 8.6, whoosh(0.5, 400, 2000, 0.3))
    times = [10.35, 10.85, 11.35, 11.8, 12.2, 12.55, 12.85, 13.1, 13.35, 13.55, 13.75, 13.95]
    for k, nt in enumerate(times):
        add(s, nt, ping(1.0 + 0.03 * (k % 3), 0.55))
    add(s, 14.36, ping(0.84, 0.8))
    add(s, 21.1, whoosh(0.6, 300, 1200, 0.2))
    add(s, 33.7, boom(1.5, 100, 40, 0.7))          # freeze hit
    add(s, 33.7, whoosh(0.4, 3000, 400, 0.4))
    add(s, 39.4, whoosh(0.6, 300, 2500, 0.5))
    for k in range(2):
        add(s, 44.8 + k * 0.0, ring(1.1))
    add(s, 53.7, tone(480, 0.25, 4) * 0.3)
    add(s, 53.95, tone(480, 0.25, 4) * 0.3)
    add(s, 54.7, whoosh(0.6, 800, 4000, 0.35))    # page flip
    for k in range(4):
        add(s, 57.8 + k * 0.75, whoosh(1.0, 3000, 600, 0.35, rev=True))
        add(s, 58.55 + k * 0.75, tone(1975 + k * 120, 1.2, 3) * 0.07)
    for k in range(8):
        add(s, 62.55 + k * 0.2, glitch(0.12, 0.6))
    add(s, 64.45, whoosh(1.8, 4000, 500, 0.35))
    add(s, 67.4, glitch(0.9, 1.0))
    add(s, 70.0, whoosh(2.5, 200, 800, 0.3, rev=True))
    add(s, 71.0, whoosh(1.0, 300, 1500, 0.3))
    add(s, 73.1, buzz(1.7, 1.0))
    add(s, 75.0, buzz(0.9, 1.0))
    add(s, 75.2, ping(0.7, 0.6))
    add(s, 77.42, ping(0.5, 0.8))
    add(s, 77.42, boom(2.0, 90, 35, 0.5))
    add(s, 80.0, boom(1.6, 110, 40, 0.8))
    add(s, 80.0, whoosh(0.35, 3500, 500, 0.4))
    add(s, 84.86, ping(0.5, 0.8))
    add(s, 84.86, glitch(0.45, 0.9))
    add(s, 89.6, click(0.8))
    add(s, 89.6, whoosh(0.4, 500, 3000, 0.3))
    add(s, 91.5, boom(1.8, 120, 40, 0.9))
    add(s, 95.2, whoosh(5.5, 200, 1600, 0.35, rev=True))  # creepy riser under the smile
    t = np.arange(int(6.2 * SR)) / SR
    riser = np.sin(2 * np.pi * (300 + 25 * t) * t) * np.sin(2 * np.pi * (307 + 27 * t) * t) * (t / 6.2) ** 2 * 0.18
    add(s, 95.3, riser)
    add(s, 97.6, boom(1.2, 90, 40, 0.5))
    add(s, 99.3, glitch(0.4, 0.8))
    add(s, 101.54, click(1.2))
    add(s, 101.54, boom(1.2, 60, 25, 0.8))
    add(s, 104.5, layer((tone(880, 1.0, 3) * 0.12, 0), (tone(1318, 0.9, 3) * 0.1, 0.12)))
    add(s, 107.94, boom(3.6, 65, 22, 1.6))           # deep low sound
    add(s, 107.94, whoosh(0.5, 3000, 300, 0.4))
    s[int(111.4 * SR):] = 0
    return reverb(s, 1.6, 0.18)


def main():
    voice_path, out = sys.argv[1], sys.argv[2]
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', voice_path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    v = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768
    voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
    voice /= np.abs(voice).max() + 1e-9
    m = music(); m /= np.abs(m).max() + 1e-9
    s = sfx(); s /= np.abs(s).max() + 1e-9
    # duck music under the voice
    venv = lp(np.abs(voice), 4)
    venv /= venv.max() + 1e-9
    duck = 1 - 0.45 * np.clip(venv * 3, 0, 1)
    mix_ = voice * 0.95 + m * 0.24 * duck + s * 0.42
    mix_ /= np.abs(mix_).max() / 0.95
    fade = np.ones(N); fade[-int(0.4 * SR):] = np.linspace(1, 0, int(0.4 * SR))
    mix_ *= fade
    st = np.stack([mix_, mix_], 1)
    from scipy.io import wavfile
    wavfile.write(out, SR, (st * 32767).astype(np.int16))
    print("audio ok", out)


if __name__ == '__main__':
    main()
