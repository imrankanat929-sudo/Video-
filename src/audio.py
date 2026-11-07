"""Synthesised score + sound design, mixed under the voice-over.

usage: python audio.py LANG WORDS.json VOICE.mp3 OUT.wav
"""
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import timeline as TL  # noqa

SR = 44100
RNG = np.random.default_rng(0)


def n(t):
    return int(t * SR)


def lowpass(x, fc, order=1.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** (2 * order)) ** 0.5
    return np.fft.irfft(X, len(x)).astype(np.float32)


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= np.exp(-((np.log(np.maximum(f, 1)) - np.log(np.sqrt(lo * hi))) / np.log(hi / lo) * 1.6) ** 2)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def noise(d):
    return RNG.normal(0, 1, n(d)).astype(np.float32)


def env(d, a=0.01, r=0.3, curve=1.0):
    N = n(d)
    t = np.arange(N) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.clip(1 - (t - (d - r)) / r, 0, 1) ** curve
    return e.astype(np.float32)


def expdecay(d, tau):
    t = np.arange(n(d)) / SR
    return np.exp(-t / tau).astype(np.float32)


def sine(f, d, ph=0):
    t = np.arange(n(d)) / SR
    if callable(f):
        return np.sin(2 * np.pi * np.cumsum(f(t)) / SR + ph).astype(np.float32)
    return np.sin(2 * np.pi * f * t + ph).astype(np.float32)


def saw(f, d):
    t = np.arange(n(d)) / SR
    return (2 * ((f * t) % 1) - 1).astype(np.float32)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


class Track:
    def __init__(self, dur):
        self.L = np.zeros(n(dur) + SR, np.float32)
        self.R = np.zeros_like(self.L)

    def add(self, t, x, gain=1.0, pan=0.0):
        i = n(t)
        if i >= len(self.L):
            return
        x = x[: len(self.L) - i] * gain
        self.L[i:i + len(x)] += x * np.sqrt((1 - pan) / 2) * 1.414
        self.R[i:i + len(x)] += x * np.sqrt((1 + pan) / 2) * 1.414


# ------------------------------------------------------------ instruments
def pad(notes, d, bright=900):
    out = np.zeros(n(d), np.float32)
    for m in notes:
        f = mtof(m)
        for det in (-0.12, 0.0, 0.11):
            out += saw(f * 2 ** (det / 12), d) * 0.2
    out = lowpass(out, bright, 2)
    return out * env(d, 1.2, 1.5) / max(1, len(notes))


def sub_pulse(d=0.6, f0=55):
    return sine(lambda t: f0 * (1 + 1.5 * np.exp(-t * 30)), d) * expdecay(d, 0.18)


def heartbeat():
    a = sub_pulse(0.35, 48)
    b = sub_pulse(0.45, 44) * 0.8
    out = np.zeros(n(0.7), np.float32)
    out[: len(a)] += a
    out[n(0.22): n(0.22) + len(b)] += b
    return lowpass(out, 200)


def pluck(m, d=2.5):
    f = mtof(m)
    x = (sine(f, d) + 0.4 * sine(2 * f, d) * expdecay(d, 0.3) + 0.15 * sine(3 * f, d) * expdecay(d, 0.15))
    return x * expdecay(d, 0.7) * env(d, 0.005, 0.3)


def tick():
    x = bandpass(noise(0.05), 2500, 6000) * expdecay(0.05, 0.006)
    return x * 3


def whoosh(d=0.8, up=True):
    x = noise(d)
    t = np.arange(len(x)) / SR
    k = t / d
    e = np.sin(np.pi * np.clip(k, 0, 1)) ** 2
    out = bandpass(x, 300, 3000) * e
    return out * 0.6


def boom(d=4.0, f0=60, f1=25, tau=1.2, nz=0.6, cutoff=400):
    s = sine(lambda t: f1 + (f0 - f1) * np.exp(-t * 3), d) * expdecay(d, tau)
    r = lowpass(noise(d), cutoff, 2) * expdecay(d, tau * 0.7) * nz * 4
    hit = bandpass(noise(0.3), 80, 2000) * expdecay(0.3, 0.05)
    out = s + r
    out[: len(hit)] += hit * 0.8
    return out


def ping():
    a = sine(1318.5, 0.25) * expdecay(0.25, 0.08)
    b = sine(1760, 0.5) * expdecay(0.5, 0.15)
    out = np.zeros(n(0.7), np.float32)
    out[: len(a)] += a
    out[n(0.12): n(0.12) + len(b)] += b
    return out * 0.5


def buzz(d=0.45):
    t = np.arange(n(d)) / SR
    x = np.sign(np.sin(2 * np.pi * 160 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    return lowpass(x.astype(np.float32), 400) * env(d, 0.02, 0.05) * 0.5


def alert_tone(d=1.2):
    return (sine(853, d) + sine(960, d)) * env(d, 0.02, 0.05) * 0.25


def ring(d=1.6):
    x = (sine(440, d) + sine(480, d)) * 0.25
    t = np.arange(len(x)) / SR
    return x * ((t % 0.5) < 0.4) * env(d, 0.02, 0.05)


def siren(d):
    f = lambda t: 900 + 350 * np.sin(2 * np.pi * t / 2.6)
    x = sine(f, d) + 0.3 * sine(lambda t: 2 * (900 + 350 * np.sin(2 * np.pi * t / 2.6)), d)
    return lowpass(x, 2500) * env(d, 0.8, 1.0) * 0.18


def crowd(d):
    x = bandpass(noise(d), 250, 1800)
    t = np.arange(len(x)) / SR
    am = 0.6 + 0.4 * np.sin(2 * np.pi * t * 1.7) * np.sin(2 * np.pi * t * 0.43)
    return x * am * env(d, 0.6, 0.8) * 0.5


def rumble(d, cutoff=150):
    return lowpass(noise(d), cutoff, 2) * 6


def riser(d):
    x = bandpass(noise(d), 400, 6000)
    t = np.arange(len(x)) / SR
    e = (t / d) ** 2.5
    tone = sine(lambda tt: 80 + 900 * (tt / d) ** 2, d) * 0.4
    return (x * 0.7 + tone) * e


def news_sting():
    d = 2.5
    chord = sum(saw(mtof(m), d) for m in (50, 57, 62, 65)) * 0.2
    chord = lowpass(chord, 1800) * expdecay(d, 0.5)
    return chord + boom(d, 90, 40, 0.4, 0.3) * 0.7


def stab():
    d = 3.0
    ch = sum(saw(mtof(m), d) for m in (38, 44, 50, 51)) * 0.25
    return lowpass(ch, 1200) * expdecay(d, 0.8) + boom(d, 70, 30, 0.8, 0.4)


def glitch_noise(d=0.4):
    x = noise(d)
    t = np.arange(len(x)) / SR
    gate = (np.sin(2 * np.pi * 37 * t) > 0) * 1.0
    return bandpass(x, 1000, 8000) * gate * 0.35 + np.sign(sine(110, d)) * 0.1 * gate


def tinnitus(d):
    return sine(3800, d) * env(d, 0.05, d * 0.8) * 0.06


# ------------------------------------------------------------ score
def build(lang, words_path, voice_path, out_wav):
    proc = subprocess.run(["ffmpeg", "-v", "error", "-i", voice_path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    voice = np.frombuffer(proc.stdout, np.float32)
    vdur = len(voice) / SR
    scenes, evs, _, end = TL.build(lang, words_path, vdur)
    st = {}
    for s in scenes:
        key = s["name"] if s["name"] != "day" else f"day{s['arg']}"
        st[key] = (s["start"], s["end"])
    M = Track(end)  # music
    X = Track(end)  # sfx

    # --- music sections
    prog_tense = [[38, 45, 50, 53], [34, 41, 46, 50], [31, 38, 43, 46], [33, 40, 45, 49]]  # Dm Bb Gm A
    prog_sad = [[38, 45, 50, 53, 57], [34, 41, 50, 53], [29, 36, 45, 48], [36, 43, 48, 52]]  # Dm Bb F C

    def lay_pads(t0, t1, prog, clen, gain, bright):
        t, i = t0, 0
        while t < t1 - 0.5:
            d = min(clen + 1.5, t1 - t + 1.0)
            M.add(t, pad(prog[i % len(prog)], d, bright), gain)
            t += clen
            i += 1

    flash_t = evs["flash"]
    impact_t = evs["impact"]
    twist_t = st["twist"][0]
    final_t = st["final"][0]

    # intro: drone + low pad
    lay_pads(0, st["day1"][0], prog_tense[:1] * 2 + prog_tense[1:2], 4.0, 0.9, 500)
    M.add(0, sine(36.7, st["day1"][0] + 1) * env(st["day1"][0] + 1, 1, 1.5) * 0.25)
    # days 1-5: tension pads + pulse that speeds up
    lay_pads(st["day1"][0], st["day7"][0], prog_tense, 4.0, 1.0, 800)
    t = st["day1"][0]
    while t < st["day7"][0] - 0.3:
        prog = (t - st["day1"][0]) / (st["day7"][0] - st["day1"][0])
        M.add(t, sub_pulse(), 0.55 + 0.3 * prog)
        t += 1.0 - 0.35 * prog
    # day 7: sparse plucks over soft pad
    lay_pads(st["day7"][0], flash_t - 0.3, prog_sad, 4.0, 0.7, 600)
    mel = [74, 72, 69, 70, 69, 65, 67, 69]
    t, i = st["day7"][0] + 0.6, 0
    while t < evs["dot"] - 0.2:
        M.add(t, pluck(mel[i % len(mel)]), 0.35, pan=0.2 * ((i % 2) * 2 - 1))
        t += 1.5
        i += 1
    # heartbeat from bright dot to flash
    t = evs["dot"]
    while t < flash_t - 0.6:
        M.add(t, heartbeat(), 0.9)
        t += 0.85
    M.add(st["entry"][0] - 0.5, riser(flash_t - st["entry"][0] + 0.2), 0.5)
    # silence at flash, then aftermath pad until the twist
    lay_pads(impact_t + 2.5, twist_t - 0.1, prog_sad, 5.0, 0.8, 700)
    t, i = st["q_mark"][0], 0
    while t < twist_t - 1.0:
        M.add(t, pluck(mel[(i + 3) % len(mel)] - 12), 0.3)
        t += 2.0
        i += 1
    # twist: 0.9 s of silence, then low drone + ticking clock
    tw = twist_t + 0.9
    dd = end - tw
    M.add(tw, sine(36.7, dd) * env(dd, 1.5, 1.2) * 0.35)
    M.add(tw, pad([26, 33, 38], dd, 300), 0.8)
    t = tw
    while t < end - 0.5:
        X.add(t, tick(), 0.5)
        t += 1.0

    # --- sfx
    X.add(evs["notify"] - 0.05, buzz(), 0.6)
    X.add(evs["notify"], ping(), 0.7)
    X.add(evs["notify"] + 1.2, alert_tone(), 0.35)
    X.add(0.0, whoosh(1.2), 0.5)
    X.add(st["radar"][0], whoosh(0.6), 0.35)
    X.add(st["fake"][0] + 0.3, ping() * 0.5, 0.3)
    X.add(st["fake"][0] + 1.5, ping() * 0.5, 0.3)
    X.add(st["confirm"][0], news_sting(), 0.55)
    X.add(evs["days"] - 0.1, boom(3, 70, 30, 0.7, 0.4), 0.35)
    t = evs["days"]
    while t < st["day1"][0] - 0.2:
        X.add(t, tick(), 0.5)
        t += 0.5
    for k in (1, 3, 5, 7):
        s0 = st[f"day{k}"][0]
        X.add(s0 - 0.35, whoosh(0.5), 0.6)
        X.add(s0, boom(2.5, 80, 35, 0.4, 0.3), 0.32)
    X.add(st["tv_wall"][0], bandpass(noise(st["tv_wall"][1] - st["tv_wall"][0]), 500, 4000) * 0.08)
    for key in ("store", "airport"):
        a, b = st[key]
        X.add(a, crowd(b - a + 0.4), 0.35)
    X.add(st["size"][0] + 0.3, riser(3.0), 0.25)
    a, b = st["sirens"]
    X.add(a - 0.2, siren(b - a + 0.6), 0.9, pan=-0.3)
    X.add(a, crowd(b - a), 0.3)
    a = st["calls"][0]
    X.add(a + 0.2, ring(1.6), 0.35)
    X.add(a + 2.4, ring(1.6), 0.35)
    X.add(evs["friends"] + 0.3, ping() * 0.5, 0.3)
    X.add(evs["friends"] + 2.3, ping() * 0.5, 0.3)
    a, b = st["launch"]
    r = rumble(b - a + 1.5) * env(b - a + 1.5, 0.8, 1.2)
    X.add(a, r, 0.18)
    X.add(evs["mfail"] - 1.2, boom(2.0, 120, 50, 0.3, 0.6, 1200), 0.4)
    X.add(evs["mfail"], stab(), 0.38)
    a, b = st["quiet"]
    t = a
    while t < b:
        X.add(t, tick(), 0.45)
        t += 1.0
    X.add(st["family"][0], whoosh(1.0), 0.2)
    a, b = st["entry"]
    X.add(a, lowpass(noise(b - a + 0.5), 900, 1) * env(b - a + 0.5, b - a, 0.1, 1) * 1.4, 0.6)
    X.add(flash_t, tinnitus(impact_t - flash_t + 0.4), 1.0)
    X.add(impact_t, boom(9.0, 55, 22, 2.6, 1.0, 300), 0.55)
    X.add(impact_t, rumble(st["destruction"][1] - impact_t + 2) * env(st["destruction"][1] - impact_t + 2, 0.05, 2.5) * 0.8, 0.2)
    X.add(impact_t + 0.05, bandpass(noise(4), 1500, 7000) * expdecay(4, 1.0), 0.12)
    X.add(st["earth_dust"][0], whoosh(1.2), 0.25)
    X.add(st["q_mark"][0], boom(3, 60, 30, 0.8, 0.2), 0.35)
    X.add(st["divide"][0], boom(3, 70, 30, 0.8, 0.5, 600) * 0.6, 0.4)
    X.add(evs["hours"] - 0.3, glitch_noise(0.4), 0.7)
    X.add(evs["hours"] - 0.05, stab(), 0.4)
    X.add(final_t, boom(4, 60, 25, 1.4, 0.3), 0.35)
    t = evs["hours"] + 0.4
    while t < end - 0.8:
        X.add(t, heartbeat(), 0.45)
        t += 0.9

    # --- mix: duck music under voice
    N = len(M.L)
    v = np.zeros(N, np.float32)
    v[: len(voice)] = voice
    e = np.abs(v)
    k = int(SR * 0.25)
    e = np.convolve(e, np.ones(k, np.float32) / k, mode="same")
    e = e / (e.max() + 1e-6)
    duck = 1 - 0.45 * np.clip(e * 4, 0, 1)
    mg, xg, vg = 0.16, 0.45, 1.0
    L = v * vg + (M.L * duck) * mg + X.L * xg
    R = v * vg + (M.R * duck) * mg + X.R * xg
    st_ = np.stack([L, R], 1)
    st_ = np.tanh(st_ * 1.0) * 0.98
    pcm = (np.clip(st_, -1, 1) * 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("audio", out_wav, round(N / SR, 2), "s")


if __name__ == "__main__":
    build(*sys.argv[1:5])
