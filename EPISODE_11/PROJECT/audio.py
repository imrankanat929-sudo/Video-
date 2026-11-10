"""Procedural score + sound design + final mix for one language.
usage: python3 audio.py ru|en <voice_file> <murmurs.npy>"""
import sys, json, subprocess, random
import numpy as np
from scipy import signal
import soundfile as sf
from scenes import build_timeline

SR = 48000
lang, voice_path, mur_path = sys.argv[1], sys.argv[2], sys.argv[3]
tm = json.load(open(f'timing_{lang}_full.json'))
S, E = tm['S'], tm['E']
shots, END = build_timeline(S, E)
N = int(END * SR) + SR
rng = np.random.default_rng(7)
T = {s['f'].__name__: (s['a'], s['b'], s['k']) for s in shots}


def st(name):
    return T[name][0]


def en(name):
    return T[name][1]


music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def add(buf, x, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or len(x) == 0:
        return
    if i < 0:
        x = x[-i:]
        i = 0
    x = x[:N - i]
    if x.ndim == 1:
        l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        buf[i:i + len(x), 0] += x * gain * l * 1.41
        buf[i:i + len(x), 1] += x * gain * r * 1.41
    else:
        buf[i:i + len(x)] += x * gain


def env(n, att, rel):
    e = np.ones(n)
    a, r = min(n, int(att * SR)), min(n, int(rel * SR))
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2))
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, x, axis=0)


def bp(x, f1, f2):
    b, a = signal.butter(2, [f1 / (SR / 2), f2 / (SR / 2)], 'band')
    return signal.lfilter(b, a, x, axis=0)


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


def pad_voice(freq, dur, bright=0.5):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for h, amp in [(1, 1.0), (2, 0.35 * bright), (3, 0.18 * bright), (4, 0.08 * bright)]:
        for det in (-0.0018, 0.0018):
            x += amp * np.sin(2 * np.pi * freq * h * (1 + det) * t + rng.uniform(0, 6))
    x *= 1 + 0.15 * np.sin(2 * np.pi * 0.2 * t + rng.uniform(0, 6))
    return x * env(len(t), dur * 0.35, dur * 0.4)


def chord_pad(buf, t0, t1, chords, seg=4.0, gain=0.05, bright=0.5, oct_=0):
    t, k = t0, 0
    while t < t1:
        dur = min(seg + 1.5, t1 - t + 1.5)
        for m in chords[k % len(chords)]:
            add(buf, pad_voice(mtof(m + oct_), dur, bright), t, gain, pan=rng.uniform(-0.5, 0.5))
        t += seg
        k += 1


def pluck(freq, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t) + 0.1 * np.sin(6 * np.pi * freq * t))
    return x * np.exp(-t * 3.2) * env(len(t), 0.004, 0.05)


def arps(buf, t0, t1, chords, seg=4.0, step=0.5, prob=0.55, gain=0.05, octave=24):
    t = t0
    while t < t1:
        k = int((t - t0) / seg)
        ch = chords[k % len(chords)]
        if rng.random() < prob:
            add(buf, pluck(mtof(rng.choice(ch) + octave)), t, gain, pan=rng.uniform(-0.6, 0.6))
        t += step


def noise(n):
    return rng.standard_normal(n)


def brown(n):
    x = np.cumsum(noise(n))
    x = hp(x, 20)
    return x / (np.abs(x).max() + 1e-9)


def whoosh(dur=1.2, up=True):
    n = int(dur * SR)
    x = noise(n)
    out = np.zeros(n)
    segs = 24
    for i in range(segs):
        a, b = i * n // segs, (i + 1) * n // segs
        f = (i / segs) if up else 1 - i / segs
        fc = 300 + 5000 * f ** 2
        out[a:b] = lp(x[a:b], fc)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e * 0.6


def boom(dur=2.5, f0=60, f1=32):
    t = np.arange(int(dur * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 4)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 1.8) * env(len(t), 0.005, 0.3)


def blip(f=900):
    t = np.arange(int(0.18 * SR)) / SR
    return np.sin(2 * np.pi * (f + 600 * t / 0.18) * t) * np.exp(-t * 22) * 0.6


def shimmer(dur=2.5, base=1200):
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)
    for k, m in enumerate([0, 7, 12, 19, 24]):
        f = base * 2 ** (m / 12) * (1 + 0.06 * t / dur)
        x += np.sin(2 * np.pi * f * t + k) * (0.6 + 0.4 * np.sin(2 * np.pi * (5 + k) * t))
    return x / 5 * env(len(t), dur * 0.4, dur * 0.5)


def heartbeat(t0, t1, bpm=72, gain=0.7):
    t = t0
    while t < t1:
        for off, g in ((0, 1.0), (0.22, 0.7)):
            add(sfx, boom(0.35, 70, 45) * g, t + off, gain)
        t += 60 / bpm


def tick():
    t = np.arange(int(0.04 * SR)) / SR
    return hp(noise(len(t)), 3000) * np.exp(-t * 120) * 0.5


# ---------------------------------------------------------------- murmurs
mur = np.load(mur_path)  # (k, n) at 24 kHz


def murmur_clip():
    a = mur[rng.integers(len(mur))]
    a = a[np.abs(a) > 1e-4] if np.any(np.abs(a) > 1e-4) else a
    a = a[::-1]  # reversed -> language-neutral, eerie
    rate = rng.uniform(0.82, 1.15)
    n = int(len(a) * 2 * rate)
    a = signal.resample(a, n)
    a = bp(a, 250, 3000)
    return a / (np.abs(a).max() + 1e-9)


def murmurs(t0, t1, d0, d1, gain=0.12):
    """d = clips started per second, ramping d0 -> d1"""
    t = t0
    while t < t1:
        f = (t - t0) / max(0.01, t1 - t0)
        d = d0 + (d1 - d0) * f
        if d <= 0:
            t += 0.1
            continue
        clip = murmur_clip()
        clip *= env(len(clip), 0.15, 0.3)
        add(sfx, clip, t, gain * rng.uniform(0.6, 1.0), pan=rng.uniform(-0.9, 0.9))
        t += rng.exponential(1.0 / d)


# ================================================================ SCORE
day1, day3, day5, day7 = st('sh_school_ext'), st('sh_tv'), st('sh_world'), st('sh_wake')
Am, F, C, G, Dm, Ee = [57, 60, 64, 71], [53, 57, 60, 64], [48, 55, 60, 64], [47, 55, 59, 62], [50, 57, 60, 65], [52, 56, 59, 64]
# A: mysterious opening
chord_pad(music, 0, day1, [Am, F, C, G], gain=0.045, bright=0.4)
arps(music, 0.5, day1, [Am, F, C, G], gain=0.045)
add(music, pad_voice(mtof(33), day1 + 1, 0.2), 0, 0.08)
# B: school, darker, tension rises
chord_pad(music, day1, st('sh_freeze'), [Am, Dm, Am, Ee], gain=0.045, bright=0.6)
arps(music, day1, st('sh_freeze'), [Am, Dm, Am, Ee], step=0.25, prob=0.35, gain=0.035)
t10 = st('sh_class_front') + T['sh_class_front'][2]['t10']
add(music, whoosh(en('sh_class_front') - t10 + 0.3) * 0.8, t10, 0.5)
# freeze: drone + heartbeat
fz0, fz1 = st('sh_freeze'), en('sh_freeze')
add(music, pad_voice(mtof(81), fz1 - fz0 + 1, 0.1), fz0, 0.03)
add(music, pad_voice(mtof(33), fz1 - fz0 + 1, 0.3), fz0, 0.09)
heartbeat(fz0 + 0.2, fz1, gain=0.55)
# C/D: day 3 + day 5 - anxious pulse, then stronger
for (t0, t1, bpm, g) in ((day3, day5, 100, 0.07), (day5, day7, 112, 0.09)):
    beat = 60 / bpm / 2
    t, k = t0, 0
    roots = [33, 33, 29, 28]
    while t < t1:
        r = roots[int((t - t0) / (beat * 16)) % 4]
        nn = int(beat * 0.9 * SR)
        tt = np.arange(nn) / SR
        x = np.sin(2 * np.pi * mtof(r) * tt) + 0.4 * np.sin(2 * np.pi * mtof(r + 12) * tt)
        x = lp(np.tanh(2 * x), 400) * np.exp(-tt * 6)
        add(music, x, t, g * (0.6 + 0.4 * (t - t0) / (t1 - t0)) * (1.0 if k % 2 == 0 else 0.7))
        if k % 2 == 1:
            add(music, tick() * 0.8, t, g * 0.8, pan=0.3)
        t += beat
        k += 1
    chord_pad(music, t0, t1, [Am, F, Dm, Ee], gain=0.04, bright=0.7)
riser = whoosh(4.0, up=True)
add(music, riser, day7 - 4.0, 0.35)
add(music, pad_voice(mtof(45), day7 - day5, 0.8) * np.linspace(0.2, 1.2, int((day7 - day5) * SR)), day5, 0.04)
# hard stop at day 7 -> silence (cut everything after)
cut = int(day7 * SR)
music[cut:] = 0
# E: soft return, warm, very quiet
q0 = st('sh_quiet_street') + 0.8
fr = st('sh_friend_close')
chord_pad(music, q0, fr - 0.5, [C, G, Am, F], gain=0.03, bright=0.3)
arps(music, q0 + 1, fr - 1, [C, G, Am, F], step=0.75, prob=0.4, gain=0.03)
# F: friend's voice -> reverse swell, low boom, eerie shimmer, low drone to the end
sw = whoosh(1.5, up=True)
add(sfx, sw, fr - 1.4, 0.45)
add(sfx, boom(3.5, 55, 28), fr + 0.05, 0.9)
add(music, shimmer(en('sh_friend_close') - fr + 1.5, 900), fr, 0.05)
add(music, pad_voice(mtof(33), END - fr + 1, 0.4) * np.linspace(1, 0, int((END - fr + 1) * SR)), fr, 0.11)
add(music, pad_voice(mtof(40), END - fr + 1, 0.4) * np.linspace(1, 0, int((END - fr + 1) * SR)), fr, 0.07)
chord_pad(music, st('sh_final_close'), END - 2, [Am, F, Am, Ee], gain=0.03, bright=0.3)
vo_end = E[-1]
add(sfx, boom(3, 50, 30), vo_end + 1.6, 0.6)
add(sfx, pluck(mtof(81), 3.0), vo_end + 1.6, 0.08)
add(sfx, pluck(mtof(76), 3.0), vo_end + 1.75, 0.06)

# ================================================================ SFX
# ambience: city (street shots), room tone elsewhere
for name in ('sh_title', 'sh_street_intro', 'sh_street_walk', 'sh_ears', 'sh_avoid', 'sh_world', 'sh_crowd_lonely',
             'sh_quiet_street', 'sh_school_ext'):
    a, b, _ = T[name]
    n = int((b - a + 0.6) * SR)
    amb = lp(brown(n), 600) * 0.5 + lp(noise(n), 1500) * 0.02
    g = 0.18 if name != 'sh_quiet_street' else 0.08
    add(sfx, amb * env(n, 0.3, 0.3), a, g, pan=rng.uniform(-0.2, 0.2))
    if name in ('sh_title', 'sh_street_walk', 'sh_avoid'):
        add(sfx, whoosh(2.4) * 0.5, a + 0.6, 0.12, pan=-0.6)  # passing car
# slow-mo + first ability
a, b, k = T['sh_street_intro']
slow = a + k['slow']
add(sfx, whoosh(1.4, up=False), slow - 0.4, 0.3)
add(sfx, shimmer(2.6, 1400), slow, 0.07)
add(sfx, boom(2.0, 80, 40), slow, 0.25)
murmurs(slow + 0.2, b + 0.3, 2, 4, 0.06)
add(sfx, shimmer(1.6, 1800), st('sh_eyes'), 0.06)
# kitchen: birds + mug + first thoughts (bubble blips)
a, b, _ = T['sh_kitchen']
for i in range(8):
    tt = np.arange(int(0.12 * SR)) / SR
    f = rng.uniform(2800, 4200)
    ch = np.sin(2 * np.pi * (f + 900 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.exp(-tt * 25)
    add(sfx, ch, a + rng.uniform(0, b - a), 0.04, pan=-0.7)
add(sfx, blip(800), a + 1.1, 0.15)
add(sfx, shimmer(1.2, 1600), a + 1.05, 0.05)
add(sfx, blip(1000), a + 1.6, 0.12)
murmurs(a + 1.2, b, 1, 2, 0.06)
# street: thoughts increase
a, b, _ = T['sh_street_walk']
murmurs(a, b, 1.5, 9, 0.07)
for i in range(10):
    add(sfx, blip(rng.uniform(700, 1200)), a + rng.uniform(0, b - a), 0.07, pan=rng.uniform(-0.6, 0.6))
# ears: overwhelm + muffled
a, b, _ = T['sh_ears']
murmurs(a, b, 14, 18, 0.10)
add(sfx, shimmer(b - a + 0.5, 700) * 0.8, a, 0.06)
add(sfx, boom(1.5, 90, 50), a, 0.3)
# day cards: whoosh + hit
for name in ('sh_school_ext', 'sh_tv', 'sh_world', 'sh_wake'):
    a = st(name)
    add(sfx, whoosh(0.9), a - 0.6, 0.28)
    add(sfx, boom(2.2, 65, 35), a + 0.05, 0.55 if name != 'sh_wake' else 0.2)
# school: clock ticks + murmurs
a = st('sh_class_board')
b = st('sh_freeze')
t = a
while t < b:
    add(sfx, tick(), t, 0.25, pan=0.5)
    t += 1.0
murmurs(st('sh_class_front'), t10, 1.5, 3, 0.07)
murmurs(t10, b, 6, 16, 0.09)
# freeze: everything stops, the girl's thought
add(sfx, whoosh(0.8, up=False), b - 0.3, 0.3)
t12 = b + T['sh_freeze'][2]['t12']
add(sfx, shimmer(2.5, 600), t12, 0.06)
# day 3: TV news murmur + sting
a, b, _ = T['sh_tv']
tvn = bp(noise(int((b - a) * SR)), 300, 3000) * 0.03
add(sfx, tvn, a, 0.5)
murmurs(a + 0.3, b, 3, 4, 0.05)
for m, g in ((69, 1), (76, 0.7), (81, 0.6), (88, 0.4)):
    add(sfx, pluck(mtof(m), 1.5), a + 2.0, 0.05 * g)
murmurs(st('sh_avoid'), en('sh_feed'), 2, 4, 0.05)
for i in range(6):
    add(sfx, blip(1300), st('sh_feed') + 0.3 + i * 0.5, 0.05)
murmurs(st('sh_world'), en('sh_hero_close'), 4, 10, 0.07)
# day 7 silence -> only a faint room tone, then birds on the quiet street
a = day7
n = int((st('sh_quiet_street') - a + 1) * SR)
add(sfx, lp(noise(n), 300) * 0.02 * env(n, 1.0, 0.5), a, 1.0)
a, b, _ = T['sh_quiet_street']
for i in range(10):
    tt = np.arange(int(0.12 * SR)) / SR
    f = rng.uniform(2800, 4200)
    ch = np.sin(2 * np.pi * (f + 900 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.exp(-tt * 25)
    add(sfx, ch, a + 1 + rng.uniform(0, b - a), 0.035, pan=rng.uniform(-0.8, 0.8))
for name in ('sh_meet',):
    a, b, _ = T[name]
    for i in range(5):
        tt = np.arange(int(0.12 * SR)) / SR
        f = rng.uniform(2800, 4200)
        ch = np.sin(2 * np.pi * (f + 900 * np.sin(2 * np.pi * 18 * tt)) * tt) * np.exp(-tt * 25)
        add(sfx, ch, a + rng.uniform(0, b - a), 0.03, pan=rng.uniform(-0.8, 0.8))

# ================================================================ reverb + mix
ir_n = int(2.6 * SR)
ir_t = np.arange(ir_n) / SR
ir = np.stack([noise(ir_n), noise(ir_n)], 1) * np.exp(-ir_t * 2.6)[:, None]
ir = lp(ir, 5000)
ir /= np.sqrt((ir ** 2).sum(0))


def verb(x, wet):
    y = np.stack([signal.fftconvolve(x[:, i], ir[:, i])[:len(x)] for i in range(2)], 1)
    return x * (1 - wet) + y * wet * 1.2


music = verb(music, 0.45)
sfx_dry = sfx.copy()
sfx = verb(sfx, 0.25)

# voice
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', voice_path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                     capture_output=True).stdout
voice = np.frombuffer(raw, np.float32).astype(np.float64)
voice = voice / (np.abs(voice).max() + 1e-9) * 0.85
vbuf = np.zeros(N)
vbuf[:min(N, len(voice))] = voice[:N]
# ducking: lower music/sfx while the narrator speaks
e = np.sqrt(np.abs(lp(vbuf ** 2, 8)))
e = np.convolve(e, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
duck = 1 - 0.55 * np.clip(e / 0.05, 0, 1)
music *= duck[:, None]
sfx *= (0.5 + 0.5 * duck)[:, None]

mix = np.stack([vbuf, vbuf], 1) + music + sfx
mix = np.tanh(mix * 1.1) / 1.1
mix = mix[:int(END * SR)]
fade = int(1.2 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
music = music[:len(mix)]
sfx = sfx[:len(mix)]
sf.write(f'mix_{lang}.wav', mix.astype(np.float32), SR)
for arr, out in ((music, f'../AUDIO/music/music_bed_{lang}.mp3'), (sfx, f'../AUDIO/sound_effects/sfx_track_{lang}.mp3')):
    sf.write('_tmp.wav', arr.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '_tmp.wav', '-b:a', '192k', out])
import os; os.remove('_tmp.wav')
print('done', len(mix) / SR)
