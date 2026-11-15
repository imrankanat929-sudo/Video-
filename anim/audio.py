"""Original score + sound design, synthesised from scratch and timed to the cue sheet.

python -m anim.audio <lang>  ->  build/music_<lang>.wav, build/sfx_<lang>.wav, build/mix_<lang>.wav
"""
import os
import sys
import wave
import numpy as np
from scipy import signal
from .timing import cues, duration, VO_OFF

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.RandomState(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def bp(x, f0, f1, order=2):
    sos = signal.butter(order, [f0, f1], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)


def saw(f, t, ph=0.0):
    return 2 * ((f * t + ph) % 1.0) - 1


def env_adsr(n, a, d, s, r, total):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(na, 1)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr > 0 and n > nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def stereo(x, pan=0.0):
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l, x * r], 1)


def make_ir(dur=2.8, decay=2.2, bright=6000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = rng.randn(n, 2) * np.exp(-t * decay)[:, None]
    ir = lp(ir, bright)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.abs(ir).sum(0).max() * 6


IR = make_ir()
IR_BIG = make_ir(5.0, 1.1, 4000)


def reverb(x, wet=0.35, ir=None):
    ir = IR if ir is None else ir
    y = np.stack([signal.fftconvolve(x[:, i], ir[:, i])[: len(x)] for i in range(2)], 1)
    return x * (1 - wet) + y * wet


class Track:
    def __init__(self, dur):
        self.buf = np.zeros((int(dur * SR) + SR * 6, 2))

    def add(self, t0, x, gain=1.0, pan=0.0):
        if x.ndim == 1:
            x = stereo(x, pan)
        i = int(t0 * SR)
        if i < 0:
            x = x[-i:]
            i = 0
        j = min(len(self.buf), i + len(x))
        if j > i:
            self.buf[i:j] += x[: j - i] * gain


# ---------------------------------------------------------------- instruments
def pad(freqs, d, bright=1200, detune=0.15, attack=1.5, release=2.0, lfo=0.15):
    t = tt(d)
    x = np.zeros((len(t), 2))
    for f in freqs:
        for k, dt in enumerate((-detune, 0, detune)):
            ff = f * 2 ** (dt / 12)
            ph = rng.rand()
            v = saw(ff, t, ph)
            x += stereo(v, (k - 1) * 0.6) / len(freqs) / 3
    cut = bright * (1 + 0.35 * np.sin(2 * np.pi * lfo * t))
    # block-wise moving filter
    y = np.zeros_like(x)
    blk = SR // 10
    zi = None
    for i in range(0, len(t), blk):
        sos = signal.butter(2, min(cut[i], SR * 0.45), "low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2, 2))
        seg, zi = signal.sosfilt(sos, x[i:i + blk], axis=0, zi=zi)
        y[i:i + blk] = seg
    e = env_adsr(len(t), attack, 0.1, 1.0, release, d)
    return y * e[:, None]


def drone(f, d, amp=1.0):
    t = tt(d)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.003 * t) + 0.3 * np.sin(2 * np.pi * f * 1.5 * t))
    x *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t)
    e = env_adsr(len(t), 2.0, 0.1, 1.0, 2.0, d)
    return stereo(x * e * amp * 0.4)


def pluck(f, d=1.2, bright=3000):
    t = tt(d)
    x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 8)) * np.exp(-t * 3.5)
    x += 0.2 * saw(f, t) * np.exp(-t * 12)
    return lp(x, bright)


def tick(hi=True):
    t = tt(0.06)
    x = rng.randn(len(t)) * np.exp(-t * 180)
    x = bp(x, 2500 if hi else 1600, 6000)
    x += np.sin(2 * np.pi * (3200 if hi else 2400) * t) * np.exp(-t * 120) * 0.5
    return x * 0.6


def boom(d=3.0, f0=70, f1=28, noise=0.8):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 1.4) * 1.2
    n = lp(rng.randn(len(t)), 1800) * np.exp(-t * 6) * noise
    x = x + n
    return np.tanh(x * 1.5) * 0.8


def riser(d, f0=200, f1=2400, noise=1.0):
    t = tt(d)
    k = (t / d) ** 2
    f = f0 + (f1 - f0) * k
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.5 * np.sign(np.sin(ph * 1.005))) * 0.25
    n = rng.randn(len(t))
    out = np.zeros(len(t))
    blk = SR // 20
    for i in range(0, len(t), blk):
        fc = 300 + 7000 * k[i]
        out[i:i + blk] = bp(n[i:i + blk + 0], fc * 0.7, min(fc * 1.3, SR * 0.45), 1)
    wob = 1 + 0.5 * np.sin(2 * np.pi * (2 + 14 * k) * t)
    return (tone + out * noise * 0.6) * k * wob


def whoosh(d=1.2, up=True):
    t = tt(d)
    k = np.sin(np.pi * t / d) ** 2
    n = rng.randn(len(t))
    out = np.zeros(len(t))
    blk = SR // 40
    for i in range(0, len(t), blk):
        u = i / len(t)
        fc = 400 + 4000 * (u if up else 1 - u)
        out[i:i + blk] = bp(n[i:i + blk], fc * 0.6, fc * 1.4, 1)
    return out * k


def creak(d=1.4):
    t = tt(d)
    f = 90 + 60 * np.sin(2 * np.pi * 0.6 * t) + 25 * rng.randn(len(t)).cumsum() / SR * 30
    ph = 2 * np.pi * np.cumsum(np.clip(f, 40, 300)) / SR
    pulses = (np.sin(ph) > 0.92).astype(float)
    x = bp(pulses + 0.05 * rng.randn(len(t)), 300, 3000)
    return x * np.sin(np.pi * t / d) * 1.5


def step(soft=1.0):
    t = tt(0.18)
    x = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 30) + lp(rng.randn(len(t)), 900) * np.exp(-t * 40) * 0.6
    return x * soft


def heartbeat():
    t = tt(0.5)
    one = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 18)
    x = one.copy()
    o = int(0.22 * SR)
    x[o:] += one[: len(x) - o] * 0.7
    return x


def chime():
    t = tt(1.4)
    x = (np.sin(2 * np.pi * midi(88) * t) * np.exp(-t * 4) +
         np.sin(2 * np.pi * midi(95) * np.maximum(t - 0.12, 0)) * np.exp(-np.maximum(t - 0.12, 0) * 4) * (t > 0.12))
    return x * 0.5


def glitch_sfx(d=0.35):
    t = tt(d)
    sq = np.sign(np.sin(2 * np.pi * (300 + 2000 * rng.rand()) * t))
    gate = (np.sin(2 * np.pi * 37 * t) > 0).astype(float)
    return hp(sq * gate * 0.25 + rng.randn(len(t)) * 0.2 * gate, 400) * np.exp(-t * 4)


def wind(d, amp=1.0):
    n = rng.randn(int(d * SR), 2)
    x = lp(hp(n, 150), 900)
    t = tt(d)
    x *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.037 * t))[:, None]
    e = env_adsr(len(t), 2, 0.1, 1, 2, d)
    return x * e[:, None] * amp


def tinnitus(d):
    t = tt(d)
    return np.sin(2 * np.pi * 7400 * t) * np.exp(-t * 0.9) * 0.05


def city_ambience(d):
    t = tt(d)
    rum = lp(rng.randn(len(t), 2), 120) * 2.0
    out = rum
    for k in range(int(d / 4)):
        s = rng.rand() * d
        dd = 3.0
        i = int(s * SR)
        tw = tt(dd)
        car = lp(rng.randn(len(tw)), 500 + 300 * rng.rand()) * np.sin(np.pi * tw / dd) ** 2
        pan = np.linspace(-0.8, 0.8, len(tw)) * (1 if rng.rand() > 0.5 else -1)
        st = np.stack([car * np.cos((pan + 1) * np.pi / 4), car * np.sin((pan + 1) * np.pi / 4)], 1)
        j = min(len(out), i + len(st))
        out[i:j] += st[: j - i] * 0.6
    return out


# ---------------------------------------------------------------- score
def build(lang):
    C = cues(lang)
    D = duration(lang)
    mus = Track(D)
    sfx = Track(D)

    # ---- 1. ordinary evening (warm): A minor pad, drone, clock
    a_end = C["noise"]
    mus.add(0.0, drone(55, a_end + 1.0, 0.8))
    chords1 = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 57, 60]]  # Am F G Am/E
    seg = 4.0
    tpos, k = 0.3, 0
    while tpos < C["open_door"]:
        mus.add(tpos, pad([midi(n) for n in chords1[k % 4]], seg + 1.5, bright=900, attack=1.2, release=1.5), 0.32)
        tpos += seg
        k += 1
    for s in np.arange(0.5, C["open_door"], 1.0):
        sfx.add(s, tick(int(s) % 2 == 0), 0.7, pan=-0.3)
    # footsteps in the hallway
    stop_t = C["door_notice"] + 1.4
    for s in np.arange(0.6, stop_t, 0.48):
        sfx.add(s, step(0.5), 0.8, pan=0.1)
    # mysterious arpeggio once the door is noticed
    arp = [76, 79, 83, 88, 83, 79]
    s = C["door_notice"] + 0.8
    i = 0
    while s < C["noise"]:
        f = midi(arp[i % 6] + (12 if s > C["open_door"] else 0))
        mus.add(s, pluck(f, 1.0, 5000), 0.12 + 0.08 * min(1, (s - C["door_notice"]) / 8), pan=0.5 * np.sin(i))
        s += 0.3
        i += 1
    # low hum near the door
    mus.add(C["blue_light"], drone(36.7, C["noise"] - C["blue_light"] + 1.5, 1.2), 0.9)
    # door opening: electronic shimmer + creak + whoosh
    sfx.add(C["open_door"] + 1.0, creak(1.6), 0.5, pan=0.4)
    sfx.add(C["open_door"] + 1.2, whoosh(2.4), 0.6)
    mus.add(C["open_door"] + 1.0, pad([midi(n) for n in (69, 76, 81, 88)], C["noise"] - C["open_door"] + 1.0,
                                      bright=4000, attack=2.5, release=1.0, lfo=0.4), 0.30)
    # synth rising through the copy room
    mus.add(C["same_room"], pad([midi(n) for n in (45, 52, 57)], C["noise"] - C["same_room"] + 0.5,
                                bright=500, attack=3, release=0.6), 0.35)
    for s in np.arange(C["steps"] + 0.25, C["noise"] - 0.2, 0.55):
        sfx.add(s, step(0.35), 0.35)

    # ---- 2. the transition
    sfx.add(C["noise"], boom(2.5, 90, 35, 0.6), 0.75)
    sfx.add(C["noise"], riser(C["flash_fall"] - C["noise"] + 0.2, 120, 2600), 0.55)
    mus.add(C["noise"], riser(C["flash_fall"] - C["noise"], 55, 440, noise=0.2), 0.35)
    sfx.add(C["flash_fall"], boom(4.5, 120, 24, 1.0), 1.1)
    sfx.add(C["flash_fall"] - 0.15, whoosh(0.5, up=True), 0.8)
    sfx.add(C["flash_fall"] + 0.5, tinnitus(3.5), 1.0)
    sfx.add(C["flash_fall"] + 0.42, step(1.4), 0.9)  # body hits the floor

    # ---- 3. the other world: cold sci-fi ambient in D minor
    b0 = C["eyes_open"] - 0.8
    b1 = C["message"] + 0.2
    mus.add(b0, drone(36.7, C["double_line"] - b0, 1.0), 0.8)
    chords2 = [[50, 53, 57, 64], [46, 50, 53, 60], [43, 50, 55, 58], [45, 49, 52, 57]]  # Dm9 Bb G-ish A
    s, k = b0, 0
    while s < b1:
        mus.add(s, pad([midi(n) for n in chords2[k % 4]], 5.5, bright=1100, detune=0.25, attack=2.0, release=2.0, lfo=0.2), 0.30)
        s += 4.5
        k += 1
    sfx.add(b0, wind(C["voice"] - b0 + 2, 0.5), 0.6)
    # echo pings
    for s in np.arange(b0 + 1.0, b1, 3.1):
        p = pluck(midi(81 + int(rng.rand() * 3) * 2), 1.8, 2500)
        mus.add(s, p, 0.08, pan=rng.rand() - 0.5)
        mus.add(s + 0.375, p, 0.04, pan=rng.rand() - 0.5)
        mus.add(s + 0.75, p, 0.02, pan=rng.rand() - 0.5)
    # heartbeat when the photos are wrong, then at the parents
    for s in np.arange(C["photos"], C["parents"], 1.0):
        sfx.add(s, heartbeat(), 0.5)
    # tension pulse from the city on
    for s in np.arange(C["run_out"], C["message"], 0.25):
        tq = np.arange(int(0.2 * SR)) / SR
        b = np.sin(2 * np.pi * 36.7 * tq) * np.exp(-tq * 14)
        mus.add(s, b, 0.35 if int((s - C["run_out"]) / 0.25) % 4 == 0 else 0.18)
    for s in np.arange(C["run_out"], C["city"] + 0.4, 0.3):
        sfx.add(s, step(0.6), 0.4)
    sfx.add(C["run_out"], city_ambience(C["message"] - C["run_out"] + 1), 0.25)
    sfx.add(C["numbers"] + 0.45, glitch_sfx(0.5), 0.5)

    # ---- 4. the message: music pauses
    sfx.add(C["message"] + 0.15, chime(), 0.55)
    sfx.add(C["read"] + 0.1, chime() * 0.5, 0.35)
    for s in np.arange(C["message"] + 1.2, C["voice"], 0.9):
        sfx.add(s, heartbeat(), 0.6)
    mus.add(C["message"] + 0.5, drone(27.5, C["voice"] - C["message"] + 0.5, 0.8), 0.6)

    # ---- 5. the double
    sfx.add(C["voice"], boom(3.0, 60, 30, 0.3), 0.7)
    sfx.add(C["voice"] - 0.6, whoosh(0.7), 0.4)
    sil0 = C["double_line"] - 0.6
    mus.add(C["voice"], pad([midi(n) for n in (38, 45, 50, 53)], sil0 - C["voice"], bright=700, attack=3, release=0.05), 0.4)
    # accelerating bass pulses
    s = C["voice"] + 1.0
    gap = 0.9
    while s < sil0:
        tq = np.arange(int(0.25 * SR)) / SR
        b = np.tanh(2 * np.sin(2 * np.pi * 41.2 * tq)) * np.exp(-tq * 10)
        mus.add(s, b, 0.6)
        s += gap
        gap = max(0.22, gap * 0.93)
    sfx.add(C["turn"], whoosh(1.6, up=False), 0.35)
    sfx.add(C["double_stand"], boom(3.5, 55, 26, 0.2), 0.8)
    mus.add(C["double_stand"], riser(sil0 - C["double_stand"], 80, 900, noise=0.15), 0.25)
    # hard silence, then a deep hit under his line
    sfx.add(C["double_line"], boom(4.0, 48, 22, 0.15), 0.9)
    mus.add(C["double_line"], drone(30.9, C["realize"] - C["double_line"] + 0.5, 1.0), 0.6)

    # ---- 6. the end
    sfx.add(C["realize"], boom(5.0, 80, 24, 0.7), 1.0)
    end = D
    mus.add(C["realize"], pad([midi(n) for n in (38, 45, 50, 53, 57, 64)], end - C["realize"] + 0.5,
                              bright=1600, detune=0.2, attack=0.05, release=4.5, lfo=0.1), 0.42)
    mus.add(C["realize"], drone(36.7, end - C["realize"], 1.0), 0.7)
    mel = [(0, 69), (2.0, 72), (4.0, 76), (6.5, 74), (9.0, 72), (11.0, 69)]
    for o, n in mel:
        if C["realize"] + o < C["end_vo"]:
            mus.add(C["realize"] + o, pluck(midi(n), 3.0, 2200), 0.16, pan=-0.2)
    s = C["real_one"]
    while s < C["important"]:
        sfx.add(s, glitch_sfx(0.12), 0.35)
        s += 0.42
    sfx.add(C["end_vo"], boom(5.0, 70, 22, 0.4), 0.8)
    mus.add(C["end_vo"], pluck(midi(57), 4.0, 1500), 0.3)
    mus.add(C["end_vo"], pluck(midi(64), 4.0, 1500), 0.2)

    n = int(D * SR)
    music = reverb(mus.buf, 0.40, IR_BIG)[:n]
    effects = reverb(sfx.buf, 0.22)[:n]
    # hard silence before his line + fade at the very end
    i0, i1 = int(sil0 * SR), int((C["double_line"]) * SR)
    fo = int(0.08 * SR)
    for x in (music, effects):
        x[i0:i0 + fo] *= np.linspace(1, 0, fo)[:, None]
        x[i0 + fo:i1] = 0.0
    fade = np.ones(n)
    k0 = int((D - 2.5) * SR)
    fade[k0:] = np.linspace(1, 0, n - k0) ** 1.5
    music *= fade[:, None]
    effects *= fade[:, None]
    return music, effects


def read_voice(lang, n):
    w = wave.open(os.path.join(ROOT, "build", f"voice_{lang}.wav"))
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    assert w.getframerate() == SR
    v = np.zeros(n)
    o = int(VO_OFF * SR)
    m = min(n - o, len(a))
    v[o:o + m] = a[:m]
    return v


def ducking(v):
    e = np.abs(v)
    e = signal.lfilter([1 - np.exp(-1 / (0.05 * SR))], [1, -np.exp(-1 / (0.05 * SR))], e)
    g = 1 - 0.55 * np.clip(e / (np.percentile(e, 90) + 1e-9), 0, 1)
    # slow release
    g = signal.lfilter([1 - np.exp(-1 / (0.25 * SR))], [1, -np.exp(-1 / (0.25 * SR))], g - 1) + 1
    return g


def write(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    w = wave.open(path, "w")
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
    w.close()


def norm(x, peak):
    m = np.abs(x).max()
    return x / m * peak if m > 0 else x


def main(lang):
    music, effects = build(lang)
    n = len(music)
    v = read_voice(lang, n)
    music = norm(music, 0.5)
    effects = norm(effects, 0.7)
    g = ducking(v)
    vs = np.stack([v, v], 1) * 1.0
    mix = vs * 1.15 + music * 0.85 * g[:, None] + effects * 0.8 * (0.6 + 0.4 * g[:, None])
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    b = os.path.join(ROOT, "build")
    write(os.path.join(b, f"music_{lang}.wav"), music)
    write(os.path.join(b, f"sfx_{lang}.wav"), effects)
    write(os.path.join(b, f"mix_{lang}.wav"), norm(mix, 0.95))
    print("ok", lang, n / SR)


if __name__ == "__main__":
    main(sys.argv[1])
