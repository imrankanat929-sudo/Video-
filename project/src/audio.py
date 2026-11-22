"""Original cinematic score + sound design + voiceover mix.

The score is an original composition in the spirit of a tense, driving
"ticking-clock" film score (staccato string ostinato, low drones, impacts).
Every section starts exactly on a scene cut from timeline.py, so the downbeats,
impacts and drops land on the words.

usage: python audio.py            -> out/audio/{music,sfx,voiceover,mix}.wav
       MUSIC_FILE=track.mp3 python audio.py   -> use your own licensed track
"""
import os
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

from timeline import T, SFX, DURATION, VO_OFFSET, FINAL_TEXT, LOGO

SR = 48000
N = int(DURATION * SR)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "audio")
rng = np.random.default_rng(11)

BPM = 112.0
BEAT = 60.0 / BPM
S16 = BEAT / 4


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def env_adsr(n, a=0.005, d=0.05, s=0.6, r=0.05):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(1, min(na, n))
    e[:na] = np.linspace(0, 1, na)
    if na + nd < n:
        e[na:na + nd] = np.linspace(1, s, nd)
    nr = min(nr, n)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def additive(freq, n, rolloff=1.2, odd=False, vib=0.0, vib_rate=5.5, maxh=40):
    t = tt(n)
    ph = 2 * np.pi * freq * t
    if vib:
        ph += vib * np.sin(2 * np.pi * vib_rate * t) * freq / vib_rate
    out = np.zeros(n)
    for h in range(1, maxh + 1):
        if freq * h > 12000:
            break
        if odd and h % 2 == 0:
            continue
        out += np.sin(ph * h + h * 0.7) / h ** rolloff
    return out


class Bus:
    def __init__(self):
        self.L = np.zeros(N + SR * 4)
        self.R = np.zeros(N + SR * 4)

    def add(self, t0, sig, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        n = min(len(sig), len(self.L) - i)
        if n <= 0:
            return
        gl = gain * np.cos((pan + 1) * np.pi / 4) * 1.414
        gr = gain * np.sin((pan + 1) * np.pi / 4) * 1.414
        self.L[i:i + n] += sig[:n] * gl
        self.R[i:i + n] += sig[:n] * gr

    def out(self):
        return np.stack([self.L[:N], self.R[:N]], 1)


# ---------------------------------------------------------- instruments -----
def violin(m, dur, vel=1.0):
    n = int((dur + 0.08) * SR)
    s = additive(mtof(m), n, 1.15, vib=0.004, vib_rate=6.0, maxh=30)
    s += 0.15 * rng.standard_normal(n) * np.exp(-tt(n) * 60)  # bow scrape
    return s * env_adsr(n, 0.006, dur * 0.5, 0.35, 0.07) * vel * 0.22


def cello(m, dur, vel=1.0):
    n = int((dur + 0.15) * SR)
    s = additive(mtof(m), n, 1.3, vib=0.003, maxh=30)
    return s * env_adsr(n, 0.012, dur * 0.6, 0.5, 0.12) * vel * 0.32


def pad(ms, dur, vel=1.0, att=1.2, rel=1.5, bright=2.0):
    n = int((dur + rel) * SR)
    s = np.zeros(n)
    for m in ms:
        for det in (-0.07, 0.0, 0.08):
            s += additive(mtof(m + det), n, bright, maxh=12)
    e = env_adsr(n, att, 0.1, 1.0, rel)
    return s * e * vel * 0.06


def piano(m, vel=1.0, dur=3.0):
    n = int(dur * SR)
    t = tt(n)
    f = mtof(m)
    s = np.zeros(n)
    for h, (amp, dec) in enumerate(((1, 2.2), (0.45, 3.5), (0.25, 5), (0.12, 7), (0.06, 9)), 1):
        s += amp * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h * h)) * np.exp(-t * dec)
    s *= np.minimum(1, t / 0.004)
    return s * vel * 0.28


def synth_pluck(m, dur, vel=1.0):
    n = int((dur + 0.2) * SR)
    t = tt(n)
    s = additive(mtof(m), n, 1.8, odd=True, maxh=15) * np.exp(-t * 9)
    return s * np.minimum(1, t / 0.003) * vel * 0.25


def sub(m, dur, vel=1.0):
    n = int((dur + 0.1) * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * mtof(m) * t) + 0.25 * np.sin(4 * np.pi * mtof(m) * t)
    return s * env_adsr(n, 0.01, 0.1, 0.8, 0.08) * vel * 0.45


def thump(vel=1.0):
    n = int(0.35 * SR)
    t = tt(n)
    f = 60 * np.exp(-t * 8) + 38
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    return s * vel * 0.9


def tick(vel=1.0, hi=True):
    n = int(0.03 * SR)
    t = tt(n)
    s = rng.standard_normal(n) * np.exp(-t * 400)
    s = sosfilt(butter(2, 3500 if hi else 1800, "hp", fs=SR, output="sos"), s)
    s += 0.5 * np.sin(2 * np.pi * (4200 if hi else 2600) * t) * np.exp(-t * 300)
    return s * vel * 0.35


def lowpass(x, fc, order=2):
    return sosfilt(butter(order, fc, "lp", fs=SR, output="sos"), x)


# ---------------------------------------------------------------- harmony ---
CH = {  # chord tones (MIDI)
    "Dm": [50, 57, 62, 65, 69], "Bb": [46, 53, 58, 62, 65], "Gm": [43, 50, 55, 58, 62],
    "A": [45, 52, 57, 61, 64], "F": [41, 48, 53, 57, 60], "C": [48, 55, 60, 64, 67],
    "D": [50, 57, 62, 66, 69], "Gmadd9": [43, 50, 55, 57, 58],
}
OST = [0, 2, 3, 2, 4, 3, 2, 3, 0, 2, 3, 4, 3, 2, 3, 2]  # index into upper tones


def ostinato(bus, t0, t1, prog, vel0, vel1, octave=12, pan=0.0, step=S16, accent=True):
    """Staccato string arpeggio on a chord progression (1 chord per bar)."""
    bar = BEAT * 4
    t, i = t0, 0
    while t < t1 - 0.01:
        b = int((t - t0) / bar)
        ch = CH[prog[b % len(prog)]]
        upper = [m + octave for m in ch[1:]] + [ch[2] + octave + 12]
        m = upper[OST[i % 16] % len(upper)]
        k = (t - t0) / max(0.01, t1 - t0)
        v = vel0 + (vel1 - vel0) * k
        if accent and i % 4 == 0:
            v *= 1.25
        bus.add(t, violin(m, step * 0.85, v), 1.0, pan + (0.25 if i % 2 else -0.25))
        t += step
        i += 1


def bass_line(bus, t0, t1, prog, vel, step=BEAT / 2, inst=cello):
    bar = BEAT * 4
    t = t0
    while t < t1 - 0.01:
        b = int((t - t0) / bar)
        ch = CH[prog[b % len(prog)]]
        bus.add(t, inst(ch[0] - 12 if inst is sub else ch[0], step * 0.9, vel), 1.0, 0)
        t += step


def pads(bus, t0, t1, prog, vel, bars_per=1, att=0.8, bright=2.2):
    bar = BEAT * 4 * bars_per
    t, b = t0, 0
    while t < t1 - 0.05:
        d = min(bar, t1 - t)
        ch = CH[prog[b % len(prog)]]
        bus.add(t, pad(ch[:4], d, vel, att=att, rel=1.2, bright=bright), 1.0, 0)
        t += bar
        b += 1


def drone(bus, t0, t1, m, vel):
    n = int((t1 - t0) * SR)
    t = tt(n)
    s = additive(mtof(m), n, 2.2, maxh=10) + 0.6 * np.sin(2 * np.pi * mtof(m - 12) * t)
    e = np.minimum(1, t / 1.0) * np.minimum(1, (t[-1] - t) / 0.6 + 0.001)
    s *= e * (0.85 + 0.15 * np.sin(2 * np.pi * 0.2 * t))
    bus.add(t0, s * vel * 0.18)


def clock(bus, t0, t1, step, vel, hi=True):
    t, i = t0, 0
    while t < t1 - 0.005:
        bus.add(t, tick(vel * (1.0 if i % 2 == 0 else 0.6), hi), 1.0, 0.3 if i % 2 else -0.3)
        t += step
        i += 1


def compose():
    mus = Bus()
    # S0 hook ------------------------------------------------------------
    drone(mus, 0.0, T["ty_mozhesh"] + 0.6, 38, 1.0)
    pads(mus, 0.3, T["ty_mozhesh"], ["Dm"], 0.6, bars_per=4, att=2.0)
    hb = 0.35
    while hb < T["podumay"]:
        mus.add(hb, thump(0.9))
        mus.add(hb + 0.24, thump(0.6))
        hb += 1.05
    clock(mus, T["podumay"] - 0.05, T["ty_mozhesh"], BEAT / 2, 0.8)
    # S1 judgment: ostinato builds --------------------------------------
    a, b = T["ty_mozhesh"], T["pochemu2"]
    prog1 = ["Dm", "Bb", "Gm", "A"]
    ostinato(mus, a, b - 0.05, prog1, 0.35, 1.0)
    pads(mus, a, b, prog1, 0.7)
    bass_line(mus, a + 4 * BEAT * 2, b - 0.05, prog1, 0.9)
    clock(mus, a, b - 0.05, BEAT, 0.6)
    bass_line(mus, a + 4 * BEAT * 4, b - 0.05, prog1, 0.6, BEAT, sub)
    # S2 "why?" -- silence except the boom + low tail ----------------------
    drone(mus, b, T["delo"] + 1.0, 38, 0.7)
    # S3 society ---------------------------------------------------------
    a, b = T["delo"], T["kogda"]
    prog3 = ["Dm", "F", "C", "Gm"]
    pads(mus, a, b, prog3, 1.0, att=1.2, bright=2.4)
    bass_line(mus, a, b - 0.05, prog3, 0.7, BEAT)
    ostinato(mus, a + 4 * BEAT, T["poetomu"], prog3, 0.25, 0.75, step=BEAT / 2,
             accent=False)
    ostinato(mus, T["poetomu"], b - 0.05, prog3, 0.5, 0.85)
    bass_line(mus, T["poetomu"], b - 0.05, prog3, 0.6, BEAT / 2, sub)
    # S4 brain: electronic ------------------------------------------------
    a, b = T["kogda"], T["i_postepenno"]
    prog4 = ["Dm", "Dm", "Bb", "A"]
    t, i = a, 0
    arp = [62, 65, 69, 72, 76, 72, 69, 65]
    while t < b - 0.05:
        m = arp[i % 8] + (1 if (t > T["otvergayut"] and i % 8 == 3) else 0)
        mus.add(t, synth_pluck(m, S16, 0.7 + 0.3 * (i % 4 == 0)), 1.0, np.sin(i * 0.7) * 0.6)
        t += S16
        i += 1
    bass_line(mus, a, b - 0.05, prog4, 0.9, BEAT / 2, sub)
    pads(mus, a, b, prog4, 0.6, att=0.5, bright=2.8)
    n = int((b - T["otvergayut"]) * SR)
    tr = tt(n)
    trem = (np.sin(2 * np.pi * mtof(75) * tr) + np.sin(2 * np.pi * mtof(74) * tr)) * \
        (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tr)) * np.minimum(1, tr / 1.5)
    mus.add(T["otvergayut"], trem * 0.05, 1.0, 0.2)
    # S5 trap: full ostinato + clock -------------------------------------
    a, b = T["i_postepenno"], T["vot_chto_vazhno"]
    prog5 = ["Dm", "Bb", "Gm", "A"]
    clock(mus, a, b - 0.05, BEAT / 2, 0.9)
    ostinato(mus, T["lovushka"], b - 0.05, prog5, 0.7, 1.15)
    ostinato(mus, T["a_potomu"], b - 0.05, prog5, 0.4, 0.8, octave=24, pan=0.1)
    bass_line(mus, T["lovushka"], b - 0.05, prog5, 1.0)
    bass_line(mus, T["lovushka"], b - 0.05, prog5, 0.8, BEAT, sub)
    pads(mus, a, b, prog5, 0.8, att=0.6)
    drone(mus, a, T["lovushka"] + 0.5, 38, 0.9)
    # S6 realization: calm ----------------------------------------------
    a, b = T["vot_chto_vazhno"], T["a_teper"]
    pads(mus, a + 0.2, b, ["Dm", "Bb", "F", "C"], 0.8, att=2.0, bright=2.8)
    melody = [(0.0, 69), (1.0, 65), (2.0, 62), (4.3, 70), (5.3, 65), (6.3, 62),
              (8.6, 69), (9.6, 65), (10.6, 60), (12.9, 69), (13.9, 67), (14.9, 66)]
    for (dt, m) in melody:
        if a + 0.4 + dt < b:
            mus.add(a + 0.4 + dt, piano(m, 0.8), 1.0, -0.2)
            mus.add(a + 0.4 + dt, piano(m - 24, 0.35), 1.0, 0.2)
    ostinato(mus, T["i_inogda"], T["zabyvaem"], ["Dm", "Bb"], 0.15, 0.35,
             step=BEAT / 2, accent=False)
    # S7 outro build (major lift) ----------------------------------------
    a, b = T["a_teper"], FINAL_TEXT
    prog7 = ["Bb", "F", "Dm", "C"]
    ostinato(mus, a, b - 0.12, prog7, 0.35, 1.0)
    pads(mus, a, b, prog7, 0.9, att=0.8)
    bass_line(mus, a + 4 * BEAT, b - 0.12, prog7, 0.8)
    clock(mus, a + 4 * BEAT * 2, b - 0.12, BEAT / 2, 0.5)
    # S8 final chord + logo ------------------------------------------------
    mus.add(FINAL_TEXT, pad([50, 57, 62, 64, 69], 7.5, 1.4, att=0.05, rel=3.0), 1.0)
    drone(mus, FINAL_TEXT, DURATION, 38, 0.9)
    for i, m in enumerate((62, 69, 74, 76)):
        mus.add(LOGO + 0.1 + i * 0.32, piano(m, 0.7, 4.0), 1.0, -0.3 + 0.2 * i)
    return mus.out()


# ---------------------------------------------------------------- sfx -------
def sfx_boom(g):
    n = int(2.6 * SR)
    t = tt(n)
    f = 70 * np.exp(-t * 3) + 28
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    nz = lowpass(rng.standard_normal(n), 900) * np.exp(-t * 7) * 0.6
    cl = rng.standard_normal(n) * np.exp(-t * 120) * 0.4
    return (s + nz + cl) * g * 0.9


def sfx_click(g):
    n = int(0.08 * SR)
    t = tt(n)
    s = np.sin(2 * np.pi * 1650 * t) * np.exp(-t * 70) + 0.5 * np.sin(2 * np.pi * 3300 * t) * np.exp(-t * 120)
    return s * g * 0.22


def sfx_ding(g):
    n = int(2.0 * SR)
    t = tt(n)
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
            for f, a, d in ((1174.7, 1, 2.5), (2349.3, 0.4, 4), (3520, 0.15, 6)))
    return s * np.minimum(1, t / 0.002) * g * 0.16


def sweep_noise(dur, f0, f1, shape):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    fc = np.geomspace(f0, f1, n)
    y = np.zeros(n)
    z1 = z2 = 0.0
    a_all = np.exp(-2 * np.pi * fc / SR)
    for i in range(n):  # 2-pole time-varying lowpass
        a = a_all[i]
        z1 = (1 - a) * x[i] + a * z1
        z2 = (1 - a) * z1 + a * z2
        y[i] = z2
    y /= np.max(np.abs(y)) + 1e-9
    return y * shape(np.linspace(0, 1, n))


def sfx_whoosh(g, dur=0.7):
    s = sweep_noise(dur, 400, 5000, lambda u: np.sin(np.pi * u) ** 2)
    s2 = sweep_noise(dur, 300, 3000, lambda u: np.sin(np.pi * u) ** 3)
    return np.stack([s, s2], 0) * g * 0.35


def sfx_riser(g, dur):
    n = int(dur * SR)
    t = tt(n)
    u = t / dur
    s = sweep_noise(dur, 200, 8000, lambda u: u ** 2.2) * 0.5
    f = 110 * 2 ** (u * 2)
    s += np.sin(2 * np.pi * np.cumsum(f) / SR) * u ** 2 * 0.25
    return s * g * 0.5


def sfx_swell(g, dur):
    return pad([62, 66, 69, 74], dur * 0.6, 1.0, att=dur * 0.6, rel=dur * 0.4, bright=2.5) * g * 2.0


def build_sfx():
    bus = Bus()
    for kind, t0, g in SFX:
        if kind == "boom":
            bus.add(t0 - 0.01, sfx_boom(g))
        elif kind == "click":
            bus.add(t0, sfx_click(g), 1.0, rng.uniform(-0.4, 0.4))
        elif kind == "ding":
            bus.add(t0, sfx_ding(g), 1.0, 0.0)
        elif kind == "tick":
            bus.add(t0, tick(g * 2))
        elif kind == "whoosh":
            w = sfx_whoosh(g)
            bus.add(t0 - 0.35, w[0], 1.0, -0.5)
            bus.add(t0 - 0.35, w[1], 1.0, 0.5)
        elif kind == "riser":
            bus.add(t0, sfx_riser(1.0, g))
        elif kind == "swell":
            bus.add(t0, sfx_swell(1.0, g))
    return bus.out()


# ------------------------------------------------------------------ mix -----
def reverb(x, secs=2.4, wet=0.25):
    n = int(secs * SR)
    t = tt(n)
    out = np.zeros_like(x)
    for c in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 6.9 / secs)
        ir = lowpass(ir, 6000)
        ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, c] = fftconvolve(x[:, c], ir)[: len(x)]
    return x * (1 - wet) + out * wet * 1.6


def load(path, start):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le",
                          "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    out = np.zeros((N, 2))
    i = int(start * SR)
    n = min(len(a), N - i)
    out[i:i + n] = a[:n]
    return out


def envelope(x, attack=0.03, release=0.35):
    m = np.abs(x).max(1)
    m = lowpass(m, 20)
    m = np.maximum(m, 0)
    out = np.zeros_like(m)
    aa, ar = np.exp(-1 / (attack * SR)), np.exp(-1 / (release * SR))
    # vectorised-ish peak follower on a decimated signal
    dec = 48
    md = m[::dec]
    od = np.zeros_like(md)
    aa, ar = aa ** dec, ar ** dec
    v = 0.0
    for i, s in enumerate(md):
        v = aa * v + (1 - aa) * s if s > v else ar * v + (1 - ar) * s
        od[i] = v
    out = np.interp(np.arange(len(m)), np.arange(len(md)) * dec, od)
    return out


def write(path, x):
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2",
                    "-ar", str(SR), "-i", "-", "-c:a", "pcm_s24le", path],
                   input=x.tobytes(), check=True)


def db(x):
    return 10 ** (x / 20)


def main():
    os.makedirs(OUT, exist_ok=True)
    vo = load(os.path.join(ROOT, "assets", "voiceover_ru.mp3"), VO_OFFSET)
    vo = vo / (np.abs(vo).max() + 1e-9) * db(-3)
    ext = os.environ.get("MUSIC_FILE")
    if ext:
        music = load(ext, 0.0)
        music = music / (np.abs(music).max() + 1e-9) * db(-6)
    else:
        music = compose()
        music = reverb(music, 2.6, 0.32)
        music = music / (np.abs(music).max() + 1e-9) * db(-4)
    sfx = reverb(build_sfx(), 1.8, 0.22)
    sfx = sfx / (np.abs(sfx).max() + 1e-9) * db(-4)
    # duck music + sfx under the narrator
    env = envelope(vo)
    env = env / (np.percentile(env[env > 1e-4], 95) + 1e-9)
    duck = 1 - 0.55 * np.clip(env, 0, 1)
    mix = vo * 1.0 + music * db(-6) * duck[:, None] + sfx * db(-9) * (1 - 0.3 * np.clip(env, 0, 1))[:, None]
    # final fade
    fade = np.ones(N)
    k = int(1.2 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    mix *= fade[:, None]
    write(os.path.join(OUT, "voiceover.wav"), vo)
    write(os.path.join(OUT, "music.wav"), music * fade[:, None])
    write(os.path.join(OUT, "sfx.wav"), sfx * fade[:, None])
    write(os.path.join(OUT, "mix_raw.wav"), mix / max(1, np.abs(mix).max() / db(-1)))
    print("ok")


if __name__ == "__main__":
    main()
