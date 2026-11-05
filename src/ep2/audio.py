"""Звук «За мной кто-то идёт»: отдельные слои (атмосфера, шаги героя, шаги преследователя, ветер и дождь,
вибрация, уведомления, музыка, акценты) + сведение с озвучкой. Всё привязано к меткам озвучки.
Слои также сохраняются отдельными WAV в build/ep2/stems/."""
import subprocess
import numpy as np
from scipy.io import wavfile
from ..config import SR, BUILD
from ..cues import C
from ..audio import (T, filt, noise, env, expdec, Bus, reverb, tone, drone, pad, pulse, cluster, piano, heartbeat,
                     boom, rumble, whoosh, vibrate, static, siren, footstep, breath, knock, drip, click, riser, murmur,
                     load_voice, follower, mixs, N, tinnitus, rng)

c = C()


def rain_bed(sec):
    n = noise(sec)
    y = filt(n, "band", [900, 9000]) * 0.5
    drops = (rng.random(len(n)) < 0.003) * rng.standard_normal(len(n)) * 4
    y += filt(drops, "band", [2000, 9000])
    return y


def wind(sec):
    t = T(sec)
    y = filt(noise(sec), "low", 300, 2)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t) * np.sin(2 * np.pi * 0.031 * t + 1)
    return y * lfo


def city_hum(sec):
    return filt(noise(sec), "low", 140, 3) * 1.2 + 0.15 * np.sin(2 * np.pi * 50 * T(sec))


def wet_step(heavy=False):
    s = footstep() * (1.4 if heavy else 1.0)
    sp = filt(noise(0.09), "band", [1500, 6000]) * expdec(0.09, 0.025) * 0.5
    s[:len(sp)] += sp
    if heavy:
        s = mixs(s, boom(0.2, 55, 0.05, 0) * 0.7)
    return s


def ding():
    return sum(piano(f, 1.0) for f in (1567.98, 2093.0)) * 0.45


def car_pass(sec=3.5):
    n = noise(sec)
    t = T(sec)
    g = np.exp(-((t - sec / 2) / (sec / 5)) ** 2)
    return filt(n, "band", [60, 1500]) * g + filt(n, "high", 3000) * g * 0.2  # шины по мокрому


def door_slam():
    s = boom(2.0, 60, 0.3, 0.2) * 1.4
    m = sum(np.sin(2 * np.pi * f * T(1.0)) * expdec(1.0, 0.18) for f in (220, 510, 1130)) * 0.2
    s[:len(m)] += m
    return reverb(s, 2.5, 0.8, 0.45)


def sting(sec=2.5, f=70):
    return mixs(reverb(boom(sec, f * 0.6, 0.6, 0.6), 2.5, 1.0, 0.45), whoosh(0.35, 400, 7000) * 0.6)


def build():
    out = BUILD
    out.mkdir(parents=True, exist_ok=True)
    END = c["END"]
    L = {k: Bus() for k in ("ambience", "steps_hero", "steps_follower", "wind_rain", "vibration", "notifications",
                            "music", "accents")}
    A1, C2, E2, A2, C3, E3 = 55.0, 65.41, 82.41, 110.0, 130.81, 164.81
    ext = [(0, c["window"]), (c["window"], c["coinc"]), (c["coinc"], c["flashback"]), (c["steps"], END)]

    # 1) атмосфера ночного города и 4) ветер + дождь — весь фильм (во воспоминании тише)
    L["ambience"].add(0, city_hum(END) * env(int(END * SR), 2, 4), 0.25)
    L["wind_rain"].add(0, rain_bed(END) * env(int(END * SR), 1.5, 4), 0.10)
    L["wind_rain"].add(0, wind(END) * env(int(END * SR), 2, 4), 0.35)
    mem0, mem1 = c["flashback"], c["steps"]
    for k in ("ambience", "wind_rain"):
        g = np.ones(N)
        g[int(mem0 * SR):int(mem1 * SR)] = 0.35
        g = filt(g, "low", 2)
        L[k].L *= g; L[k].R *= g
    # в переулке — эхо и реже машины; на главной улице — гул машин
    L["ambience"].add(c["main_st"], filt(noise(END - c["main_st"]), "band", [60, 700]) * env(int((END - c["main_st"]) * SR), 2, 3), 0.25)
    for tt in (c["bus"] + 0.8, c["headlights"] - 0.6, c["main_st"] + 3, c["call"] + 1, c["head_up"] + 2):
        L["ambience"].add(tt, car_pass(), 0.5, rng.uniform(-0.6, 0.6))

    # 2) шаги героя и 3) шаги преследователя
    def steps(bus, a, b, rate=2.0, heavy=False, gain=0.4, pan=0.0, echo=False, start=0.0):
        t = a + start
        while t < b:
            s = wet_step(heavy)
            if echo:
                s = reverb(s, 1.2, 0.5, 0.55)
            bus.add(t, s, gain * rng.uniform(0.85, 1.1), pan + rng.uniform(-0.1, 0.1))
            t += 1.0 / rate
    hero_walk = [(0.6, c["window"] - 0.5, 2.0), (c["coinc"], c["phone_out"], 2.0), (c["familiar"], c["nightmare"], 2.0),
                 (c["steps"], c["speed"], 2.0), (c["speed"], c["shop"] - 0.6, 3.0), (c["decide"], c["steps_back"], 2.0),
                 (c["dark_alley"], c["phone_a"], 2.0), (c["hey"], c["faster"], 2.2), (c["faster"], c["stop"] - 0.2, 3.0),
                 (c["seize"], c["main_st"] + 2.4, 3.4)]
    for a, b, r in hero_walk:
        steps(L["steps_hero"], a, b, r, gain=0.35, echo=a > c["decide"] - 1 and a < c["main_st"])
    foll = [(c["same_man"] - 0.5, c["window"] - 0.5, 1.8), (c["approach"], c["phone_out"], 1.9), (c["steps"], c["speed"], 1.8),
            (c["he_speed"], c["shop"] - 0.3, 2.9), (c["steps_back"], c["followed"] + 1.5, 1.8),
            (c["hey"], c["faster"], 2.1), (c["faster"], c["stop"], 2.9), (c["step_fwd"], c["step_fwd"] + 0.4, 2.0)]
    for a, b, r in foll:
        steps(L["steps_follower"], a, b, r, heavy=True, gain=0.22, pan=-0.2, echo=True, start=0.25)
    L["steps_follower"].add(c["finally"] + 0.6, reverb(wet_step(True) * 2, 1.5, 0.6, 0.5), 0.6)  # тяжёлый шаг вперёд

    # 5) вибрация и 6) уведомления
    for tt in (c["vibr"], c["another"] - 0.3):
        L["vibration"].add(tt, vibrate(1.3), 0.7)
    for k in range(3):
        L["notifications"].add(c["missed"] + k * 0.8, ding(), 0.22)
    L["notifications"].add(c["unknown"], ding(), 0.3)
    L["notifications"].add(c["another"] + 0.4, ding(), 0.3)
    L["notifications"].add(c["photo"] - 0.1, tone(2400, 0.08, harm=(1,)) * env(int(0.08 * SR), 0.002, 0.03), 0.12)
    L["notifications"].add(c["photo2"] - 0.1, tone(2400, 0.08, harm=(1,)) * env(int(0.08 * SR), 0.002, 0.03), 0.12)
    for k, d in enumerate((1, 1, 2)):
        L["notifications"].add(c["call"] + 1.0 + k * 0.35, tone(700 + 120 * d, 0.1, harm=(1, 0.3)) *
                               env(int(0.1 * SR), 0.002, 0.04), 0.1)

    # 7) музыка: низкий тревожный фон → нарастание
    M = L["music"]
    seg = lambda a, b: int((b - a) * SR)
    M.add(0, drone(A1, c["flashback"] + 0.5, 260) * env(seg(0, c["flashback"] + 0.5), 2, 1.5), 0.35)
    M.add(c["he_too"], pulse(A1, c["flashback"] - c["he_too"], 1.0) * env(seg(c["he_too"], c["flashback"]), 1.5, 1.5), 0.18)
    M.add(c["reflection"], cluster(c["coinc"] - c["reflection"]), 0.06)
    # воспоминание: спокойная музыка, постепенно тревожная
    mm = c["steps"] - mem0
    M.add(mem0, pad([A2, C3, E3], mm, 1400), 0.16)
    t = mem0 + 0.8
    notes = [440, 523.25, 659.25, 587.33, 523.25, 493.88, 440, 415.3]
    k = 0
    while t < c["steps"] - 1:
        M.add(t, reverb(piano(notes[k % len(notes)] / 2, 3), 2.5, 1.2, 0.5), 0.09)
        t += 2.1; k += 1
    M.add(c["familiar"], cluster(c["steps"] - c["familiar"]), 0.05)
    # настоящее: нарастающая тревога
    M.add(c["steps"], drone(A1, c["dont"] - c["steps"] + 0.6, 300) * env(seg(c["steps"], c["dont"] + 0.6), 2, 0.05), 0.33)
    M.add(c["speed"], pulse(A1, c["dont"] - c["speed"], 1.6) * env(seg(c["speed"], c["dont"]), 1, 0.05), 0.2)
    M.add(c["dark_alley"], cluster(c["dont"] - c["dark_alley"]) * env(seg(c["dark_alley"], c["dont"]), 3, 0.05), 0.07)
    M.add(c["heart"], heartbeat(c["dont"] - c["heart"], 108) * env(seg(c["heart"], c["dont"]), 0.5, 0.05), 0.5)
    M.add(c["faster"], riser(c["dont"] - c["faster"]), 0.25)
    # после «Беги» — короткая музыкальная пауза до «ты резко остановился»
    M.add(c["stop"], drone(A1 * 0.944, c["movement"] - c["stop"], 220) * env(seg(c["stop"], c["movement"]), 0.5, 0.1), 0.3)
    M.add(c["stop"], heartbeat(c["close"] - c["stop"], 96), 0.45)
    # фото: музыка почти бесшумная
    gph = np.ones(N)
    gph[int(c["photo"] * SR):int(c["movement"] * SR)] = 0.25
    # второй человек: внезапная тишина до громкого звука
    gph[int(c["movement"] * SR):int(c["loud"] * SR)] = 0.0
    M.add(c["seize"], pulse(A1, c["main_st"] - c["seize"] + 1, 3.0) * env(seg(c["seize"], c["main_st"] + 1), 0.3, 1.5), 0.25)
    M.add(c["seize"], riser(c["main_st"] - c["seize"]), 0.3)
    M.add(c["main_st"], drone(A1, c["two_opts"] - c["main_st"], 280) * env(seg(c["main_st"], c["two_opts"]), 2, 0.2), 0.28)
    M.add(c["wrong"], cluster(c["two_opts"] - c["wrong"]) * env(seg(c["wrong"], c["two_opts"]), 0.5, 0.2), 0.08)
    M.add(c["understood"], riser(c["two_opts"] - c["understood"]), 0.35)
    M.add(c["understood"], heartbeat(c["two_opts"] - c["understood"], 120), 0.45)
    fs = END - c["two_opts"]
    M.add(c["two_opts"] + 0.9, drone(A1, fs - 0.9, 220) * env(seg(0, fs - 0.9), 2, 3), 0.3)
    M.add(c["two_opts"] + 0.9, pad([A2, C3, E3 * 1.0595], fs - 0.9, 900) * env(seg(0, fs - 0.9), 3, 3), 0.1)

    # 8) акценты
    X = L["accents"]
    for key, g in (("same_man", 0.5), ("tall", 0.7), ("his_phone", 0.5), ("sure", 0.6), ("followed", 0.6), ("hey", 0.7),
                   ("dont", 0.8), ("photo", 0.4), ("someone", 0.7), ("wrong", 0.8)):
        X.add(c[key] - 0.05, sting(), g)
    X.add(c["looks"] + 0.3, reverb(boom(3, 32, 1.0), 3, 1.2, 0.5), 0.7)
    X.add(c["close"] - 0.02, mixs(reverb(boom(4, 30, 1.2, 0.6), 3.5, 1.4, 0.5) * 1.3, whoosh(0.4, 300, 8000)), 1.3)
    X.add(c["loud"], reverb(knock(), 2, 0.8, 0.4), 0.9)
    X.add(c["door"] - 0.1, door_slam(), 1.2)
    X.add(c["two_opts"], reverb(boom(4, 30, 1.4, 0.4), 3.5, 1.5, 0.5), 1.1)
    X.add(END - 3.2, mixs(tinnitus(3.0) * 0.5, filt(noise(3.0), "band", [300, 1200]) * env(int(3 * SR), 2.5, 0.3) * 0.3), 0.5)

    # ---------------- сведение
    voice = load_voice()
    voice = filt(voice, "high", 70)
    voice /= np.abs(voice).max() + 1e-9
    ve = follower(voice)
    duck = 1 - 0.6 * filt(np.clip(ve * 3, 0, 1), "low", 3)
    # музыкальная пауза после текста «НЕ ОБОРАЧИВАЙСЯ. БЕГИ»
    gp = np.ones(N)
    gp[int((c["dont"] + 0.6) * SR):int(c["stop"] * SR)] = 0
    gp = filt(gp, "low", 6) * filt(gph, "low", 4)
    gains = {"ambience": 1.0, "steps_hero": 1.0, "steps_follower": 1.0, "wind_rain": 1.0, "vibration": 1.0,
             "notifications": 1.0, "music": 1.0, "accents": 1.0}
    mix = np.zeros((N, 2))
    stems = out / "stems"
    stems.mkdir(exist_ok=True)
    for k, bus in L.items():
        st = bus.st() * gains[k]
        if k == "music":
            st = st * (duck * gp)[:, None]
        elif k in ("ambience", "wind_rain"):
            st = st * (0.55 + 0.45 * duck)[:, None]
        mix += st
        e = int(END * SR)
        wavfile.write(stems / f"{k}.wav", SR, (np.clip(st[:e] * 0.5, -1, 1) * 32767).astype(np.int16))
    mix = mix * 0.5 + np.stack([voice, voice], 1) * 0.85
    e = int(END * SR)
    nf = int(2.5 * SR)
    mix[e - nf:e] *= np.linspace(1, 0, nf)[:, None]
    mix = mix[:e]
    mix /= np.abs(mix).max() + 1e-9
    mix *= 0.89
    raw = out / "mix_raw.wav"
    wavfile.write(raw, SR, (mix * 32767).astype(np.int16))
    dst = out / "mix.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=12", "-ar", str(SR),
                    str(dst)], check=True)
    return dst


if __name__ == "__main__":
    print(build())
