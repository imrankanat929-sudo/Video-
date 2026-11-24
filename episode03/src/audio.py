"""Mix voiceover + music + synthesized sound design for one language.
usage: python3 audio.py <lang>   -> build/mix_<lang>.wav
"""
import json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from script import DURATION, SUPPLIED_OFFSET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
N = int(DURATION * SR)
rng = np.random.default_rng(5)


def load(path, mono=True):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1" if mono else "2", "-ar", str(SR),
                                   "-f", "f32le", "-"])
    a = np.frombuffer(raw, np.float32).copy()
    return a if mono else a.reshape(-1, 2)


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(clip))
    if i < 0:
        clip = clip[-i:]; i = 0; j = min(len(buf), len(clip))
    buf[i:j] += clip[:j - i] * gain


def rms_db(x):
    x = x[np.abs(x) > 1e-4]
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def lowpass(x, fc):
    # one-pole, applied twice
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); z = 0.0
    for _ in range(2):
        for i in range(len(x)):
            z = (1 - a) * x[i] + a * z; y[i] = z
        x = y.copy()
    return y


def lp_fast(x, fc):
    """FFT brick-ish lowpass with soft roll-off (fast for long signals)."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def hp_fast(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


# ------------------------------------------------------------- sound design

def footstep(gain=1.0):
    n = int(0.25 * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    thump = lp_fast(noise, 380) * env(n, 0.002, 0.035) * 3.0
    scuff = hp_fast(noise, 2500) * env(n, 0.001, 0.012) * 0.25
    return (thump + scuff) * gain


def tick(hi=True):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    f = 3200 if hi else 2500
    s = np.sin(2 * np.pi * f * t) * env(n, 0.0005, 0.006) + hp_fast(rng.standard_normal(n).astype(np.float32), 4000) * env(n, 0.0002, 0.003) * 0.4
    return s.astype(np.float32)


def whoosh(dur=1.2, rev=False, fc0=300, fc1=3000):
    n = int(dur * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    # sweep by crossfading lowpassed versions
    a = lp_fast(noise, fc0); b = lp_fast(noise, fc1)
    u = np.linspace(0, 1, n)
    e = np.sin(np.pi * u) ** 2
    s = (a * (1 - u) + b * u) * e
    return (s[::-1] if rev else s).astype(np.float32)


def boom(dur=3.0, f=48):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = f * (1 + 0.6 * np.exp(-t * 8))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) * env(n, 0.01, 0.9)
    s += lp_fast(rng.standard_normal(n).astype(np.float32), 200) * env(n, 0.005, 0.25) * 0.6
    return s.astype(np.float32)


def chime(f=880, dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t) + 0.15 * np.sin(2 * np.pi * f * 3.0 * t))
    return (s * env(n, 0.004, 0.55)).astype(np.float32)


def riser(dur=3.8):
    n = int(dur * SR); u = np.linspace(0, 1, n)
    noise = rng.standard_normal(n).astype(np.float32)
    s = lp_fast(noise, 400) * (1 - u) + lp_fast(noise, 5000) * u
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(110 + 330 * u ** 2) / SR) * 0.25
    return ((s * 0.8 + tone) * u ** 2.2).astype(np.float32)


def glitch_burst(dur=0.34):
    n = int(dur * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n).astype(np.float32)
    s = np.round(s * 3) / 3  # crunchy
    gate = (np.sin(2 * np.pi * 38 * t) > 0).astype(np.float32)
    tape = np.sin(2 * np.pi * np.cumsum(900 * (1 - t / dur) + 60) / SR)
    return ((hp_fast(s, 1500) * gate * 0.35 + tape * 0.3) * env(n, 0.003, 0.2)).astype(np.float32)


def drone(n):
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 55.4 * t) * 0.5
         + np.sin(2 * np.pi * 82.4 * t + 1) * 0.35 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t))
         + np.sin(2 * np.pi * 164.8 * t) * 0.08 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t)))
    air = lp_fast(rng.standard_normal(n).astype(np.float32), 900) * 0.5
    return (s + air).astype(np.float32)


def echo(x, delay=0.21, fb=0.32, taps=4):
    y = x.copy()
    for k in range(1, taps + 1):
        d = int(delay * k * SR)
        y[d:] += x[:-d] * (fb ** k)
    return y


def step_times(t0, t1, phase=0.0, period=0.55):
    out = []; k = np.ceil((t0 - phase) / period)
    while phase + k * period < t1 - 0.05:
        out.append(phase + k * period); k += 1
    return out


# ------------------------------------------------------------- main

def main(lang):
    timing = json.load(open(os.path.join(ROOT, "assets", f"vo_{lang}", "timing.json")))
    # ---------------- voice
    vo = np.zeros(N, np.float32)
    target = -20.0
    if lang == "ru":
        sup = load(os.path.join(ROOT, "assets", "ru_supplied_narration.mp3"))
        g = 10 ** ((target - rms_db(sup)) / 20)
        place(vo, sup, SUPPLIED_OFFSET, g)
    for line in timing:
        if line.get("supplied"): continue
        clip = load(os.path.join(ROOT, "assets", f"vo_{lang}", f"{line['id']}.wav"))
        g = 10 ** ((target - rms_db(clip)) / 20)
        place(vo, clip, line["start"], g)

    # ---------------- sfx
    sfx = np.zeros(N, np.float32)
    # footsteps (hero + friend), street echo
    steps = np.zeros(N, np.float32)
    for t in step_times(0.05, 4.4, 0.0):
        place(steps, footstep(), t, 0.55)
    for t in step_times(0.05, 4.9, 0.27):
        place(steps, footstep(), t, 0.38)
    for t in step_times(26.1, 32.2, 0.0):
        place(steps, footstep(), t, 0.55)
    for t in step_times(26.3, 31.4, 0.27):
        place(steps, footstep(), t, 0.38 * max(0.0, 1 - (t - 29.6) / 1.8) if t > 29.6 else 0.38)
    sfx += echo(steps, 0.19, 0.3, 3)
    # replay: the same steps cannot repeat (hero stands), but the ticking does
    for t0, t1 in ((10.7, 16.0), (16.5, 21.5), (73.0, 86.0), (88.9, 92.6)):
        k = 0; t = t0
        while t < t1:
            place(sfx, tick(k % 2 == 0), t, 0.10); t += 0.5; k += 1
    # glitch + short silence
    place(sfx, glitch_burst(), 16.05, 0.5)
    place(sfx, whoosh(0.5, rev=True, fc0=200, fc1=5000), 15.6, 0.35)
    place(sfx, glitch_burst(0.25), 88.65, 0.3)
    # transitions
    for t, d, gn in ((21.0, 1.4, 0.22), (35.0, 1.6, 0.2), (56.3, 1.3, 0.2), (72.1, 1.4, 0.2), (86.4, 1.6, 0.2), (92.4, 1.8, 0.18)):
        place(sfx, whoosh(d), t, gn)
    place(sfx, riser(3.6), 45.0, 0.22)
    for t, gn in ((22.3, 0.35), (41.25, 0.55), (48.55, 0.6), (65.7, 0.35), (94.9, 0.5), (100.3, 0.35)):
        place(sfx, boom(), t, gn)
    # memories / items / links
    b1 = next(l for l in timing if l["id"] == "b1")["words"][-4:]
    for i, w in enumerate(b1):
        place(sfx, whoosh(0.9, fc0=500, fc1=4000), w["s"] - 0.35, 0.12)
        place(sfx, chime([659, 784, 880, 988][i]), w["s"] + 0.75, 0.09)
    for i in range(4):
        place(sfx, chime([523, 587, 659, 784][i], 1.8), 35.6 + i * 0.9, 0.06)
    for j in range(3):
        place(sfx, chime(1046 + j * 130, 1.2), 62.2 + j * 0.45, 0.06)
    place(sfx, chime(784, 3.0), 62.7, 0.08)
    for k in range(12):
        place(sfx, chime(600 + (k * 137) % 500, 1.6), 73.2 + k * 0.85, 0.035)
    # bubble pops
    for t in (0.7, 7.9):
        place(sfx, chime(1318, 0.4), t, 0.05)
    sfx = echo(sfx, 0.27, 0.22, 3)

    # drone bed with envelope (silence dip during the repeat)
    d = drone(N)
    tt = np.arange(N) / SR
    denv = np.interp(tt, [0, 2, 15.9, 16.05, 16.45, 17.5, 47, 49, 72, 86, 92, 100, 104],
                         [0.0, 0.10, 0.10, 0.0, 0.0, 0.10, 0.12, 0.08, 0.08, 0.10, 0.11, 0.08, 0.0])
    sfx += d * denv

    # ---------------- music
    mus = load(os.path.join(ROOT, "assets", "music_lovibe_a_good_man_with_a_broken_heart.mp3"), mono=False)
    mus = mus[:N] if len(mus) >= N else np.pad(mus, ((0, N - len(mus)), (0, 0)))
    menv = np.interp(tt, [0, 1.2, 15.9, 16.05, 16.4, 17.6, 99.5, 104.0],
                         [0.0, 1.0, 1.0, 0.06, 0.06, 1.0, 1.0, 0.0])
    # duck under voice (smoothed voice envelope)
    vabs = np.abs(vo)
    win = int(0.25 * SR)
    venv = np.convolve(vabs, np.ones(win) / win, mode="same")
    venv = venv / (venv.max() + 1e-9)
    duck = 1 - 0.45 * np.clip(venv * 6, 0, 1)
    # smooth duck
    duck = np.convolve(duck, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
    mus_gain = 10 ** ((-27 - rms_db(mus.mean(axis=1))) / 20)
    mus = mus * (mus_gain * menv * duck)[:, None]

    # ---------------- final stereo mix
    mix = np.zeros((N, 2), np.float32)
    mix += vo[:, None]
    mix += mus
    mix[:, 0] += sfx * 0.9; mix[:, 1] += sfx * 0.9
    # slight stereo width on sfx echoes
    out = os.path.join(ROOT, "build"); os.makedirs(out, exist_ok=True)
    raw = os.path.join(out, f"premix_{lang}.f32")
    mix.astype(np.float32).tofile(raw)
    dst = os.path.join(out, f"mix_{lang}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", str(SR), dst], check=True)
    os.remove(raw)
    print("mix ok", dst)


if __name__ == "__main__":
    for lang in sys.argv[1:] or ["en", "ru"]:
        main(lang)
