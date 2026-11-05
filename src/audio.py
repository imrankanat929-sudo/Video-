"""Звук: синтез SFX и музыки кодом + сведение с озвучкой ElevenLabs.
Все события привязаны к меткам озвучки (cues) — смена озвучки автоматически сдвигает звук."""
import subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
from .config import SR, VOICE, BUILD
from .cues import C

c = C()
rng = np.random.default_rng(1)
N = int(c["END"] * SR) + SR


def T(sec):
    return np.arange(int(sec * SR)) / SR


def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output="sos")


def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def env(n, a=0.01, r=0.1, sus=None):
    """Огибающая длины n: атака a, спад r (сек)."""
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def expdec(sec, tau):
    t = T(sec)
    return np.exp(-t / tau)


class Bus:
    def __init__(self):
        self.L = np.zeros(N)
        self.R = np.zeros(N)

    def add(self, t, sig, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N or len(sig) == 0:
            return
        if i < 0:
            sig = sig[-i:]; i = 0
        n = min(len(sig), N - i)
        gl, gr = gain * np.sqrt(0.5 * (1 - pan)), gain * np.sqrt(0.5 * (1 + pan))
        self.L[i:i + n] += sig[:n] * gl
        self.R[i:i + n] += sig[:n] * gr

    def st(self):
        return np.stack([self.L, self.R], 1)


def reverb(x, sec=2.5, decay=0.6, wet=0.35):
    ir = noise(sec) * np.exp(-T(sec) / decay)
    ir = filt(ir, "low", 5000)
    ir /= np.sqrt((ir ** 2).sum())
    y = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - wet) + y * wet


# ------------------------------------------------------------------ instruments
def tone(f, sec, harm=(1, 0.5, 0.33, 0.25), vib=0.0, detune=0.0):
    t = T(sec)
    ph = 2 * np.pi * f * t + (vib * np.sin(2 * np.pi * 5 * t) if vib else 0)
    y = sum(a * np.sin(ph * (k + 1)) for k, a in enumerate(harm))
    if detune:
        y += sum(a * np.sin(ph * (k + 1) * (1 + detune)) for k, a in enumerate(harm))
    return y


def drone(f, sec, bright=600, lfo=0.07):
    t = T(sec)
    y = tone(f, sec, harm=(1, 0.6, 0.4, 0.3, 0.2, 0.15), detune=0.004) + 0.6 * tone(f * 1.5, sec, harm=(1, 0.4), detune=-0.003)
    y = filt(y, "low", bright)
    y *= 0.7 + 0.3 * np.sin(2 * np.pi * lfo * t)
    return y / (np.abs(y).max() + 1e-9) * env(len(y), 2.0, 2.0)


def pad(freqs, sec, cut=1200):
    y = sum(tone(f, sec, harm=(1, 0.3, 0.15), detune=0.003, vib=0.002) for f in freqs)
    y = filt(y, "low", cut)
    return y / (np.abs(y).max() + 1e-9) * env(len(y), 2.5, 2.5)


def pulse(f, sec, rate=2.0):
    t = T(sec)
    y = filt(tone(f, sec, harm=(1, 0.7, 0.5, 0.4, 0.3)), "low", 900)
    gate = (np.sin(2 * np.pi * rate * t) > 0.2).astype(float)
    gate = filt(gate, "low", 30)
    return y * gate / (np.abs(y).max() + 1e-9)


def cluster(sec):
    y = sum(tone(f, sec, harm=(1, 0.2), vib=0.004) for f in (880, 932.3, 987.8, 1046.5))
    return filt(y, "band", [500, 3000]) / 4 * env(int(sec * SR), 3.0, 1.5)


def piano(f, sec=4.0):
    t = T(sec)
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.2 + k * 0.8)) for k, a in
            zip((1, 2, 3, 4), (1, 0.4, 0.2, 0.1)))
    return y * env(len(y), 0.004, 0.3)


def heartbeat(sec, bpm=62):
    out = np.zeros(int(sec * SR))
    per = 60 / bpm
    k = 0.0
    while k < sec - 0.5:
        for dt, g in ((0, 1.0), (0.28, 0.7)):
            th = boom(0.4, 48, 0.08) * g
            i = int((k + dt) * SR)
            out[i:i + len(th)] += th[:len(out) - i]
        k += per
    return out


# ------------------------------------------------------------------ SFX
def boom(sec, f=40, tau=0.6, sweep=0.5):
    t = T(sec)
    fr = f * (1 + sweep * np.exp(-t * 6))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / tau)
    y += filt(noise(sec), "low", 180) * np.exp(-t / (tau * 0.6)) * 0.6
    return y


def rumble(sec, tau=2.5):
    y = filt(noise(sec), "low", 90, 4) * 3 + boom(sec, 32, tau, 0.3)
    return y * env(int(sec * SR), 0.15, sec * 0.5)


def whoosh(sec, f0=200, f1=3000):
    n = noise(sec)
    out = np.zeros_like(n)
    seg = int(0.05 * SR)
    for i in range(0, len(n), seg):
        fr = f0 + (f1 - f0) * (i / len(n)) ** 2
        out[i:i + seg] = filt(n[i:i + seg + 200], "band", [fr * 0.7, min(fr * 1.4, 20000)])[:len(out[i:i + seg])]
    return out * env(len(n), sec * 0.8, 0.05)


def vibrate(sec=1.3):
    t = T(sec)
    y = np.sin(2 * np.pi * 160 * t) * (1 + 0.5 * np.sign(np.sin(2 * np.pi * 320 * t)))
    gate = ((t % 0.45) < 0.3).astype(float)
    return filt(y * filt(gate, "low", 60), "band", [80, 2000]) * 0.5


def eas_alert(sec=2.6):
    t = T(sec)
    y = np.sin(2 * np.pi * 853 * t) + np.sin(2 * np.pi * 960 * t)
    return y * 0.5 * env(len(y), 0.02, 0.1)


def phone_ding():
    return sum(piano(f, 1.2) for f in (1318.5, 1760)) * 0.5


def static(sec, k=1.0):
    n = noise(sec)
    crackle = (rng.random(len(n)) < 0.002) * rng.standard_normal(len(n)) * 6
    return filt(n * 0.5 + crackle, "band", [800, 7000]) * k


def crackle_elec(sec):
    n = np.zeros(int(sec * SR))
    for _ in range(int(sec * 6)):
        i = rng.integers(0, len(n) - 4000)
        L = rng.integers(200, 3000)
        n[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4))
    return filt(n, "high", 1500)


def siren(sec, f0=600, f1=1100, period=4.0):
    t = T(sec)
    fr = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(2 * np.pi * t / period))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(fr) / SR)
    return filt(y, "band", [300, 3000])


def city_amb(sec):
    y = filt(noise(sec), "low", 400) * 0.6
    t0 = 0.0
    while t0 < sec - 4:  # проезжающие машины
        d = rng.uniform(3, 6)
        car = filt(noise(d), "band", [80, 900]) * np.sin(np.pi * T(d) / d) ** 2
        i = int(t0 * SR)
        y[i:i + len(car)] += car * rng.uniform(0.4, 1.0)
        t0 += rng.uniform(1.5, 4)
    return y


def footstep():
    s = filt(noise(0.12), "band", [80, 1200]) * expdec(0.12, 0.03)
    return s + boom(0.12, 70, 0.03, 0) * 0.5


def breath(sec, rate=0.55):
    t = T(sec)
    y = filt(noise(sec), "band", [400, 2500])
    g = np.clip(np.sin(2 * np.pi * rate * t), 0, 1) ** 2
    return y * filt(g, "low", 8) * 0.6


def door_slam():
    s = boom(2.5, 55, 0.35, 0.2) * 1.5
    clank = sum(np.sin(2 * np.pi * f * T(1.5)) * expdec(1.5, 0.3) for f in (310, 627, 1180, 1730)) * 0.25
    s[:len(clank)] += clank
    return reverb(s, 3.0, 0.9, 0.5)


def knock():
    s = boom(0.8, 75, 0.12, 0.4) * 1.4
    s += filt(noise(0.8), "band", [200, 2500]) * expdec(0.8, 0.02) * 0.8
    m = sum(np.sin(2 * np.pi * f * T(0.8)) * expdec(0.8, 0.15) for f in (180, 410, 905)) * 0.25
    return reverb(s + m, 2.5, 0.8, 0.45)


def drip():
    f = rng.uniform(900, 1600)
    t = T(0.25)
    return np.sin(2 * np.pi * (f + 1500 * np.exp(-t * 40)) * t) * np.exp(-t * 30)


def mixs(*sigs):
    n = max(len(x) for x in sigs)
    out = np.zeros(n)
    for x in sigs:
        out[:len(x)] += x
    return out


def click():
    return filt(noise(0.03), "high", 1500) * expdec(0.03, 0.004) * 2


def creak(sec):
    t = T(sec)
    f = 140 + 60 * np.sin(2 * np.pi * 0.4 * t) + 30 * np.sin(2 * np.pi * 3.1 * t)
    ph = np.cumsum(f) / SR
    pulses = (np.sin(2 * np.pi * ph) > 0.97).astype(float)
    y = filt(pulses, "band", [300, 3000]) * 3 + filt(np.sign(np.sin(2 * np.pi * ph)), "band", [200, 1600]) * 0.15
    return reverb(y * env(len(y), 0.3, 0.4), 2.0, 0.7, 0.4)


def tinnitus(sec):
    t = T(sec)
    return np.sin(2 * np.pi * 4200 * t) * np.exp(-t / (sec * 0.45)) * env(len(t), 0.05, 0.3)


def riser(sec):
    t = T(sec)
    f = 30 + 30 * (t / sec) ** 2
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    y += filt(noise(sec), "low", 200) * 0.3
    return y * (t / sec) ** 1.6


def murmur(sec):
    y = filt(noise(sec), "band", [200, 900])
    g = filt((rng.random(int(sec * 20)) < 0.4).astype(float).repeat(SR // 20)[:int(sec * SR)], "low", 6)
    return y * np.pad(g, (0, max(0, int(sec * SR) - len(g)))) * 0.5


# ------------------------------------------------------------------ voice
def load_voice():
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(VOICE), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).astype(np.float64)
    out = np.zeros(N)
    out[:len(v)] = v[:N]
    return out


def radio_fx(v, spans):
    """Голос из старого громкоговорителя: полоса 300–3400 Гц, перегруз, шум."""
    r = filt(v, "band", [320, 3200], 3)
    r = np.tanh(r * 4) / 2.5 + static(len(v) / SR, 0.006)
    r = reverb(r, 1.2, 0.35, 0.3)
    m = np.zeros(len(v))
    for a, b in spans:
        m[int(a * SR):int(b * SR)] = 1
    m = filt(m, "low", 20)
    return v * (1 - m) + r * m * 1.1


def follower(x, att=0.03, rel=0.4):
    e = np.abs(x)
    e = filt(e, "low", 15)
    return np.clip(e / (np.percentile(e, 99) + 1e-9), 0, 1)


# ------------------------------------------------------------------ build
def build():
    BUILD.mkdir(exist_ok=True)
    mus, amb, sfx = Bus(), Bus(), Bus()
    END = c["END"]
    A1, E2, A2, C3, E3 = 55.0, 82.41, 110.0, 130.81, 164.81

    # ---- 0 HOOK
    mus.add(0.0, drone(A1, c["day"] + 0.5, 300), 0.5)
    sfx.add(0.3, reverb(boom(4, 36, 1.4), 3, 1.0, 0.4), 0.9)
    mus.add(1.0, cluster(9.0), 0.08)
    amb.add(0.0, filt(noise(11), "low", 120) * env(int(11 * SR), 1, 1.5), 0.25)  # ветер
    sfx.add(7.0, riser(3.4), 0.35)
    sfx.add(10.45, reverb(boom(2, 42, 0.5), 2, 0.8, 0.4), 0.5)

    # ---- 1 ОБЫЧНЫЙ ДЕНЬ
    d0, em = c["day"], c["emergency"]
    amb.add(d0, city_amb(c["flash"] - d0 + 0.3) * env(int((c["flash"] - d0 + 0.3) * SR), 1.5, 0.1), 0.35, -0.2)
    mus.add(d0, pad([A2, C3, E3], em - d0 + 2), 0.20)
    sfx.add(c["phone_vibrate"] + 0.1, vibrate(), 0.6)
    sfx.add(c["notif"] - 0.2, vibrate(), 0.6)
    sfx.add(c["notif"], eas_alert(2.6), 0.22)
    sfx.add(c["opened"] + 0.3, click(), 0.4)
    # музыка резко напрягается на «чрезвычайной ситуации»
    sfx.add(em - 0.05, reverb(boom(2.5, 45, 0.6), 2.5, 0.9, 0.4), 0.7)
    tl = c["flash"] - em
    mus.add(em, pulse(A1, tl, 2.6) * env(int(tl * SR), 0.05, 0.05), 0.42)
    mus.add(em, cluster(tl + 0.2), 0.16)
    mus.add(em, drone(A1 * 1.0595, tl, 400) * 0.6, 0.35)  # полутон — тревога
    sfx.add(c["flash_scene"] - 1.0, riser(c["flash"] - c["flash_scene"] + 1.0), 0.3)

    # ---- 2 ВСПЫШКА: низкий гул, глухой удар, короткая тишина
    fl = c["flash"]
    sfx.add(fl - 0.15, whoosh(0.4, 400, 8000), 0.5)
    sfx.add(fl, filt(noise(4), "low", 60, 4) * env(int(4 * SR), 0.05, 3.5), 1.4)  # низкий гул
    sfx.add(fl + 0.05, tinnitus(4.0), 0.07)
    sfx.add(fl + 0.6, reverb(boom(3, 30, 0.9, 0.2), 3, 1.0, 0.5), 0.6)  # глухой удар
    # (тишина ~fl+1.5..rumble: музыки нет)
    mus.add(fl + 3.0, drone(A1, c["rumble"] - fl - 2.5, 220) * 0.8, 0.25)

    # ---- 3 ПОСЛЕДСТВИЯ
    r0 = c["rumble"]
    sfx.add(r0, rumble(7.0, 2.8), 1.5)
    sfx.add(c["glass"], filt(noise(2.5), "band", [2000, 8000]) * (np.sin(2 * np.pi * 23 * T(2.5)) > 0) *
            env(int(2.5 * SR), 0.05, 1.5), 0.25)  # дрожание стёкол
    sfx.add(c["glass"] + 0.3, crackle_elec(c["leave"] - c["glass"]), 0.10)
    sfx.add(c["signal_lost"], static(0.6), 0.35)
    for k in range(3):
        sfx.add(c["called"] + 0.4 + k * 0.5, tone(425, 0.3, harm=(1,)) * env(int(0.3 * SR), 0.01, 0.02), 0.08)
    sfx.add(c["called"] + 2.4, tone(425, 1.0, harm=(1,)) * ((T(1.0) % 0.35) < 0.18), 0.07)
    sfx.add(c["tv"], static(c["leave"] - c["tv"] + 0.4), 0.18)
    amb.add(c["rumble"] + 3, siren(c["phone2"] - r0 - 3, 500, 900, 5.0) * env(int((c["phone2"] - r0 - 3) * SR), 4, 2),
            0.05, 0.5)
    a0 = c["rumble"] + 3
    mus.add(a0, drone(A1, c["inside"] - a0, 350), 0.33)
    mus.add(c["leave"], pulse(A1, c["building"] - c["leave"], 1.6) * env(int((c["building"] - c["leave"]) * SR), 2, 2),
            0.22)

    # ---- 4 ПОИСК УКРЫТИЯ
    sfx.add(c["flashlight"] + 0.6, click(), 0.6)
    t = c["leave"] + 1.0
    while t < c["street"] - 0.4:  # шаги
        sfx.add(t, reverb(footstep(), 0.8, 0.3, 0.3), 0.35, rng.uniform(-0.2, 0.2))
        t += 0.5 if t < c["stairs"] else 0.42
    amb.add(c["leave"], breath(c["street"] - c["leave"], 0.6), 0.12)
    amb.add(c["leave"], siren(c["building"] - c["leave"], 400, 700, 6) * 0.5, 0.03, -0.5)  # отдалённая тревога
    amb.add(c["street"], murmur(c["phone2"] - c["street"]) * env(int((c["phone2"] - c["street"]) * SR), 1, 1), 0.25)
    amb.add(c["street"], siren(c["phone2"] - c["street"], 650, 1250, 3.0), 0.06, 0.3)
    sfx.add(c["phone2"] + 0.2, vibrate(), 0.6)
    sfx.add(c["msg_screen"], phone_ding(), 0.25)
    sfx.add(c["door_close"] - 0.15, door_slam(), 1.3)

    # ---- 5 ВНУТРИ: вентиляция, капли, тихие голоса; музыка тише
    i0 = c["inside"]
    vent = filt(noise(END - i0), "low", 180) * 0.8 + 0.3 * np.sin(2 * np.pi * 50 * T(END - i0))
    vent *= env(len(vent), 1.5, 2)
    amb.add(i0, vent, 0.10)
    t = i0 + 1
    while t < c["final"]:
        sfx.add(t, reverb(drip(), 1.5, 0.6, 0.5), 0.07, rng.uniform(-0.6, 0.6))
        t += rng.uniform(1.5, 4.5)
    amb.add(i0, murmur(c["lights_out"] - i0), 0.12)
    mus.add(i0, drone(A1, c["silence"] - i0 + 0.5, 250) * env(int((c["silence"] - i0 + 0.5) * SR), 1, 0.4), 0.18)
    sfx.add(c["lights_out"], mixs(reverb(boom(1.0, 60, 0.15), 1.5, 0.6, 0.4), click()), 0.6)
    sfx.add(c["emergency_light"], filt(np.sign(np.sin(2 * np.pi * 100 * T(c["silence"] - c["emergency_light"]))),
                                       "band", [100, 1200]), 0.012)
    amb.add(c["emergency_light"] + 2, murmur(4) * 0.6, 0.1)

    # ---- 6 НЕИЗВЕСТНОСТЬ
    for k in range(int(c["radio"] - c["clock"]) + 1):
        sfx.add(c["clock"] + k, click() * 0.5, 0.2)
    sfx.add(c["radio"] - 0.6, static(0.6) * env(int(0.6 * SR), 0.3, 0.1), 0.25)
    sfx.add(c["radio"] + 0.3, mixs(click(), filt(boom(0.3, 120, 0.05), "high", 80)), 0.8)
    sfx.add(c["radio"] + 0.3, static(c["broadcast2_end"] - c["radio"]), 0.04)
    mus.add(c["clock"], cluster(c["silence"] - c["clock"]) * env(int((c["silence"] - c["clock"]) * SR), 1, 0.05), 0.07)

    # ---- 7 СТРАННОЕ СООБЩЕНИЕ: музыка полностью исчезает
    # (с silence до man_door музыка не звучит)

    # ---- 8 ШЕСТОЙ ЧЕЛОВЕК / выбор
    m0 = c["man_door"]
    mus.add(m0, drone(A1, c["phone3"] - m0, 200) * env(int((c["phone3"] - m0) * SR), 3, 0.3), 0.25)
    mus.add(c["mall"], pad([A2, C3, E3 * 1.0595], c["choice_now"] - c["mall"], 900), 0.10)
    ch0 = c["choice_now"]
    kn = [c["corridor_look"] + 0.4 + k * 0.8 for k in range(3)]
    mus.add(ch0, heartbeat(kn[0] - ch0) * env(int((kn[0] - ch0) * SR), 1, 0.2), 0.5)
    amb.add(ch0, filt(noise(kn[0] - ch0), "low", 70, 4) * env(int((kn[0] - ch0) * SR), 2, 0.3), 0.6)  # низкий гул
    for k in kn:
        sfx.add(k, knock(), 1.2)
    # пауза ровно в секунду после третьего удара — тишина

    # ---- 9 ФИНАЛ: скрип, нарастающий бас, резкая тишина
    he = c["handle_end"]
    sfx.add(c["phone3"] + 0.1, vibrate(), 0.5)
    sfx.add(c["phone3"] + 1.0, riser(he - c["phone3"] - 1.0), 0.75)
    for k in range(int(c["handle"] - c["time_limited"]) + 1):
        sfx.add(c["time_limited"] + k, click(), 0.25)
    hm = c["handle_move"]
    sfx.add(hm - 0.5, creak(he - hm + 0.6) * env(int((he - hm + 0.6) * SR), 0.2, 0.05), 0.5)
    # резкая тишина на he: глушим всё ниже

    # ---- 10 ВЫБОР
    f0 = c["final"]
    sfx.add(f0, reverb(boom(4, 34, 1.2), 3.5, 1.2, 0.5), 0.9)
    fs = END - f0
    mus.add(f0 + 0.5, pad([A2, C3, E3], fs - 0.5, 800) * env(int((fs - 0.5) * SR), 3, 5), 0.18)
    mus.add(f0 + 0.5, drone(A1, fs - 0.5, 200) * env(int((fs - 0.5) * SR), 3, 5), 0.18)
    notes = [440, 523.25, 493.88, 329.63, 440, 392, 349.23, 329.63]
    t = f0 + 3
    k = 0
    while t < END - 5:
        mus.add(t, reverb(piano(notes[k % len(notes)] / 2, 4), 3, 1.5, 0.5), 0.10, rng.uniform(-0.3, 0.3))
        t += 2.6; k += 1
    sfx.add(c["optA"], reverb(boom(1.5, 60, 0.3), 2, 0.8, 0.4), 0.4)
    sfx.add(c["optB"], reverb(boom(1.5, 60, 0.3), 2, 0.8, 0.4), 0.4)

    # ------------------------------------------------ сведение
    voice = load_voice()
    voice = radio_fx(voice, [(c["broadcast1"] - 0.05, c["silence"] - 0.05),
                             (c["broadcast2"] - 0.05, c["broadcast2_end"] + 0.15)])
    voice = filt(voice, "high", 70)
    voice /= np.abs(voice).max() + 1e-9
    ve = follower(voice)
    duck = 1 - 0.55 * filt(np.clip(ve * 3, 0, 1), "low", 3)

    M = mus.st() * duck[:, None]
    A = amb.st() * (0.5 + 0.5 * duck[:, None])
    X = sfx.st()
    # тишина: после 3-го удара (1 c) и на конце ручки (до финала)
    gate = np.ones(N)
    def mute(a, b, fade=0.02):
        i0, i1 = int(a * SR), int(b * SR)
        gate[i0:i1] = 0
        nf = int(fade * SR)
        gate[max(0, i0 - nf):i0] = np.minimum(gate[max(0, i0 - nf):i0], np.linspace(1, 0, i0 - max(0, i0 - nf)))
    mute(kn[2] + 0.55, kn[2] + 1.0, 0.25)
    mute(he, f0 - 0.02, 0.01)
    # после вспышки — короткая тишина музыки и эмбиента
    mg = np.ones(N)
    i0, i1 = int((fl + 0.1) * SR), int((fl + 3.0) * SR)
    mg[i0:i1] = 0.0
    mg = filt(mg, "low", 4)
    M *= mg[:, None]
    A *= mg[:, None]
    # «Нас осталось шестеро» в ТЗ -> здесь: «заставило всех замолчать» — музыка полностью исчезает
    sg = np.ones(N)
    sg[int(c["silence"] * SR):int(c["man_door"] * SR)] = 0
    sg = filt(sg, "low", 3)
    M *= sg[:, None]

    bed = (M + A + X) * gate[:, None]
    mix = bed * 0.5 + np.stack([voice, voice], 1) * 0.85
    # фейд в конце
    nf = int(4 * SR)
    end_i = int(END * SR)
    mix[end_i - nf:end_i] *= np.linspace(1, 0, nf)[:, None]
    mix = mix[:end_i]
    mix /= np.abs(mix).max() + 1e-9
    mix *= 0.89
    raw = BUILD / "mix_raw.wav"
    wavfile.write(raw, SR, (mix * 32767).astype(np.int16))
    out = BUILD / "mix.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", "loudnorm=I=-15:TP=-1.5:LRA=14",
                    "-ar", str(SR), str(out)], check=True)
    return out


if __name__ == "__main__":
    print(build())
