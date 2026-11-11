# Procedural score + ambience for "The Black Death", mixed under the voiceover.
import numpy as np, json, sys, wave
from scipy import signal
S = sys.argv[1]; LANG = sys.argv[2]
SR = 44100; DUR = 90.0; N = int(SR * DUR)
TL = json.load(open(f"{S}/timeline.json"))[LANG]
shot = {name: st for name, st in TL["shots"]}
names = [n for n, _ in TL["shots"]]
def shot_end(n):
    i = names.index(n); return TL["shots"][i + 1][1] if i + 1 < len(names) else DUR
EV = TL["ev"]
rng = np.random.default_rng(7)
T = np.arange(N) / SR

def bus(): return np.zeros((2, N))
music, amb = bus(), bus()

def add(b, x, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR);
    if i0 >= N: return
    x = x[: N - i0] if i0 >= 0 else x[-i0:]; i0 = max(0, i0)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    b[0, i0:i0 + len(x)] += x * gain * l * 1.414; b[1, i0:i0 + len(x)] += x * gain * r * 1.414

def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, f1, f2, o=2): return signal.sosfilt(signal.butter(o, [f1, f2], 'band', fs=SR, output='sos'), x)
def env(n, a, r, sus=None):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr: e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e
def saw(f, n, ph=0.0, nh=None):
    t = np.arange(n) / SR; nh = nh or max(1, min(24, int(6000 / f))); x = np.zeros(n)
    for k in range(1, nh + 1): x += np.sin(2 * np.pi * k * f * t + ph * k) / k
    return x
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def noise(n): return rng.standard_normal(n)

# ---------------- MUSIC ----------------
# chord pads (D minor), voiced warm & low
CH = {'Dm': [38, 50, 53, 57, 62], 'Bb': [34, 46, 53, 58, 62], 'Gm': [31, 43, 50, 55, 58], 'A': [33, 45, 52, 57, 61], 'F': [29, 41, 53, 57, 60], 'C': [36, 48, 52, 55, 60], 'Asus': [33, 45, 52, 57, 62]}
prog_list = []
b = [0, shot['window'], shot['asia'], shot['trade'], shot['europe'], shot['toll'], shot['after'], shot['final'], DUR]
plan = [['Dm', 'Bb'], ['Gm', 'Asus', 'A'], ['Dm', 'F', 'C'], ['Dm', 'Bb', 'Gm', 'A'], ['Dm', 'Bb', 'Gm', 'A'], ['Bb', 'A'], ['Dm', 'F', 'Gm'], ['Bb', 'F', 'A', 'Dm']]
for i, chs in enumerate(plan):
    seg = (b[i + 1] - b[i]) / len(chs)
    for j, c in enumerate(chs): prog_list.append((b[i] + j * seg, b[i] + (j + 1) * seg, c))
for (t0, t1, c) in prog_list:
    n = int((t1 - t0 + 2.5) * SR)
    for vi, m in enumerate(CH[c]):
        for det, pan in [(-0.004, -0.5), (0.004, 0.5), (0.0, 0.0)]:
            x = saw(note(m) * (1 + det), n, ph=rng.random() * 6)
            x = lp(x, 900 if vi > 0 else 400)
            vib = 1 + 0.15 * np.sin(2 * np.pi * (0.2 + rng.random() * 0.2) * np.arange(n) / SR + rng.random() * 6)
            add(music, x * env(n, 1.8, 2.4) * vib, t0 - 0.6, 0.018 * (1.4 if vi == 0 else 1.0), pan)
# low drone D1 throughout with swells
n = N; drone = lp(saw(note(26), n) + 0.6 * saw(note(33), n, ph=1.0), 260)
sw = 0.55 + 0.45 * np.sin(2 * np.pi * T / 17.0) ** 2
fade = np.clip(T / 4, 0, 1) * np.clip((DUR - 0.5 - T) / 3.5, 0, 1)
add(music, drone * sw * fade, 0, 0.05)
# ostinato pulse (low plucked D/A) from trade to toll
def pluck(f, dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 5)
    return lp(x, 1200)
t = shot['trade'] + 0.5; k = 0
while t < shot['after'] - 0.3:
    inten = min(1, (t - shot['trade']) / 12)
    f = note([38, 38, 45, 41][k % 4]) if t < shot['toll'] else note([38, 37, 38, 34][k % 4])
    add(music, pluck(f), t, 0.10 * (0.4 + 0.6 * inten), -0.2 if k % 2 else 0.2)
    t += 0.5; k += 1
# taiko-like low drum each 2s from europe to toll end
def boom(f0=55, f1=36, dur=2.4, nz=0.4):
    n = int(dur * SR); t = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    x += lp(noise(n), 300) * np.exp(-t * 25) * nz
    return x
t = shot['europe'] + 1.0
while t < shot['after']:
    add(music, boom(dur=1.6), t, 0.16); t += 2.0
# high string line (sad melody) in after + final
mel = [(0, 69, 3), (3, 67, 2), (5, 65, 3), (8, 64, 3)]
for t0, m, d in mel:
    n = int((d + 1.5) * SR); x = lp(saw(note(m), n) + saw(note(m) * 1.003, n, 1.0), 2200)
    vib = np.sin(2 * np.pi * 5 * np.arange(n) / SR) * 0.003
    add(music, x * env(n, 0.9, 1.4), shot['after'] + 0.8 + t0, 0.016, 0.15)

# ---------------- BELLS ----------------
BR = [(0.5, 1.0, 9), (1.0, 0.7, 6), (1.19, 0.45, 4.5), (1.5, 0.35, 3.5), (2.0, 0.5, 3), (2.51, 0.25, 2), (2.66, 0.2, 1.8), (3.01, 0.18, 1.5), (4.17, 0.12, 1.0), (5.43, 0.08, 0.7)]
def bell(f, dur=9.0, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for r, a, d in BR: x += a * (bright if r > 1.6 else 1) * np.sin(2 * np.pi * f * r * t + rng.random() * 6) * np.exp(-t / d * 1.2) * (1 + 0.04 * np.sin(2 * np.pi * 1.3 * t))
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x
add(amb, lp(bell(220, 8), 2500), 0.4, 0.05, 0.4)              # distant city bell
add(amb, lp(bell(220, 8), 2500), 3.4, 0.04, 0.4)
bd = EV.get('bd', None)
# "Black Death" moment: end of chunk B speech
b_end = TL["subs"][[s[2] for s in TL["subs"]].index(next(s[2] for s in TL["subs"] if 'Black Death' in s[2] or 'смертью' in s[2]))][1]
add(music, bell(146.8, 10, 0.8), b_end - 0.1, 0.075, 0.0)
add(music, boom(48, 30, 3.5, 0.6), b_end - 0.1, 0.25)
for k in range(3): add(amb, lp(bell(174.6, 7), 3000), shot['toll'] + 0.3 + k * 2.4, 0.05, -0.3)
add(music, bell(110, 12, 0.7), EV['title'], 0.10)
add(music, boom(52, 28, 4.5, 0.8), EV['title'], 0.35)
add(music, lp(bell(165, 8), 2000), shot['europe'] + 6.5, 0.035, 0.6)

# ---------------- AMBIENCE ----------------
def wind(n, base=400, var=300, rate=0.13, seed=0):
    r = np.random.default_rng(seed); x = r.standard_normal(n)
    out = np.zeros(n); blk = 4096; ph = r.random() * 6
    for i in range(0, n, blk):
        tt = (i / SR); fc = base + var * (0.5 + 0.5 * np.sin(2 * np.pi * rate * tt + ph) * np.sin(2 * np.pi * rate * 0.37 * tt))
        out[i:i + blk] = bp(x[i:i + blk], fc * 0.6, fc * 1.6, 1)
    g = 0.6 + 0.4 * np.sin(2 * np.pi * rate * 1.3 * np.arange(n) / SR + ph) ** 2
    return lp(out * g, 2500)
def region(t0, t1, fi=1.0, fo=1.0):
    n = int((t1 - t0) * SR); return n, env(n, fi, fo)
# wind across whole film, levels per shot
wl = {'city': 0.5, 'window': 0.25, 'asia': 0.8, 'trade': 0.35, 'europe': 0.4, 'toll': 0.25, 'after': 1.0, 'final': 0.7}
W1 = wind(N, seed=1); W2 = wind(N, 500, 350, 0.11, seed=2)
lev = np.zeros(N)
for nme, st in TL["shots"]: lev[int(st * SR):int(shot_end(nme) * SR)] = wl[nme]
lev = np.convolve(lev, np.ones(SR) / SR, 'same')
amb[0] += W1 * lev * 0.05; amb[1] += W2 * lev * 0.05
# city murmur (fades as streets empty)
n, e = region(0, shot['window'] + 0.8, 1.5, 4)
mur = np.zeros(n)
for k in range(6):
    am = np.clip(np.convolve(rng.standard_normal(n // 2000 + 2), np.ones(3) / 3, 'same'), 0, None)
    am = np.interp(np.arange(n), np.linspace(0, n, len(am)), am)
    mur += bp(noise(n), 250 + k * 90, 700 + k * 120) * am
add(amb, mur * e * np.linspace(1, 0.15, n), 0, 0.012)
# creaky cart wheel in city
def creak(dur=0.7, f=800, rate=55):
    n = int(dur * SR); t = np.arange(n) / SR; r = rate * (1 + 0.4 * np.sin(2 * np.pi * 1.5 * t))
    pulses = (np.sin(2 * np.pi * np.cumsum(r) / SR) > 0.97).astype(float)
    x = bp(pulses, f * 0.8, f * 1.4, 2) * env(n, 0.1, 0.25)
    return x / (np.abs(x).max() + 1e-9)
for k in range(5): add(amb, creak(0.6, 700 + k * 40), 2.0 + k * 1.9, 0.05, -0.4)
# footsteps
def step():
    n = int(0.12 * SR); t = np.arange(n) / SR; return lp(noise(n), 500) * np.exp(-t * 45)
t = 0.8
while t < shot['window']: add(amb, step(), t, 0.12, 0.5); t += 0.42
t = EV['europeCity'] + 0.3
while t < EV['europeDoc'] + 0.5: add(amb, step(), t, 0.16, -0.2); t += 0.75
# candle blow-out whoosh at end of window shot
n = int(0.8 * SR); add(amb, bp(noise(n), 400, 1800) * env(n, 0.05, 0.6), shot['asia'] - 1.3, 0.05)
# whooshes at shot changes / map reveals
def whoosh(d=1.4):
    n = int(d * SR); x = noise(n); out = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        p = i / n; fc = 300 + 1600 * np.sin(np.pi * p)
        out[i:i + blk] = bp(x[i:i + blk], fc * 0.7, fc * 1.4, 1)
    return out * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
for tt in [shot['asia'], EV['asiaMap'], EV['tradeMap'], shot['europe'], EV['europeCity'], shot['toll'], shot['final']]:
    add(amb, whoosh(), tt - 0.7, 0.05, rng.uniform(-0.3, 0.3))
# paper rustle on maps
def rustle(d=0.9):
    n = int(d * SR); x = hp(noise(n), 2500) * (np.abs(lp(noise(n), 30)) * 3); return x * env(n, 0.05, 0.4)
for tt in [EV['asiaMap'], EV['tradeMap'], shot['toll']]: add(amb, rustle(), tt + 0.1, 0.03)
# camel bells (asia)
def tink(f):
    n = int(0.6 * SR); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 7), (2.76, 0.5, 11), (5.4, 0.25, 16)])
t = shot['asia'] + 0.3
while t < EV['asiaMap'] + 0.5: add(amb, tink(rng.choice([1320, 1480, 1760])), t, 0.03, rng.uniform(-0.6, 0.2)); t += rng.uniform(0.35, 0.8)
# waves + gulls (port), gentle waves (night sea)
def waves(n, sl=6.0):
    t = np.arange(n) / SR; sw = 0.35 + 0.65 * np.sin(2 * np.pi * t / sl) ** 4
    return lp(noise(n), 700) * sw + hp(noise(n), 3000) * sw ** 3 * 0.25
n, e = region(shot['trade'] - 0.5, EV['tradeMap'] + 0.8); add(amb, waves(n) * e, shot['trade'] - 0.5, 0.06)
n, e = region(shot['europe'] - 0.5, EV['europeCity'] + 0.8); add(amb, waves(n, 8) * e, shot['europe'] - 0.5, 0.045)
def gull():
    n = int(0.42 * SR); t = np.arange(n) / SR; f = 1700 - 700 * (t / t[-1]) ** 0.7
    x = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in range(1, 5)); x = bp(x, 900, 4000) * np.sin(np.pi * t / t[-1]) ** 0.6
    return x
for k, tt in enumerate([0.8, 1.4, 2.6]): add(amb, gull(), shot['trade'] + tt, 0.035, 0.5 - k * 0.3)
# fire crackle (lighthouse)
n = int((EV['europeCity'] - shot['europe']) * SR); cr = (rng.random(n) > 0.9993).astype(float) * rng.random(n)
add(amb, hp(lp(cr, 6000), 800) * env(n, 1, 1), shot['europe'], 0.25, 0.6)
# heartbeat in toll
def heart():
    n = int(0.9 * SR); t = np.arange(n) / SR; x = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 18) + 0.7 * np.sin(2 * np.pi * 46 * (t - 0.28)) * np.exp(-np.clip(t - 0.28, 0, None) * 18) * (t > 0.28)
    return x
t = shot['toll'] + 0.2
while t < shot['after']: add(music, heart(), t, 0.22); t += 1.1
# crows + shutter creak (after)
def caw():
    n = int(0.32 * SR); t = np.arange(n) / SR; f = 520 - 120 * t / t[-1]
    x = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k ** 0.7 for k in range(1, 14))
    x = bp(x * (1 + 0.6 * noise(n)), 700, 2600); return x * np.sin(np.pi * t / t[-1]) ** 0.5
for tt, p in [(1.2, 0.5), (1.6, 0.5), (4.8, -0.4), (5.2, -0.4), (5.6, -0.4)]: add(amb, caw(), shot['after'] + tt, 0.06, p)
for k in range(4): add(amb, creak(1.0, 520, 30), shot['after'] + 2.4 + k * 3.4, 0.035, 0.3)
# birds at dawn (final)
def chirp():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 3200 + 900 * np.sin(2 * np.pi * 18 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1])
t = shot['final'] + 1
while t < EV['black'] - 1: add(amb, chirp(), t, 0.012, rng.uniform(-0.8, 0.8)); t += rng.uniform(0.2, 1.4)

# ---------------- REVERB ----------------
def reverb(x, sec=3.0, wet=0.35):
    n = int(sec * SR); t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = np.random.default_rng(ch + 10).standard_normal(n) * np.exp(-t * 3.2 / sec * 2.3); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
        out[ch] = signal.fftconvolve(x[ch], ir)[:x.shape[1]]
    return x * (1 - wet) + out * wet * 1.6
music = reverb(music, 3.5, 0.45); amb = reverb(amb, 2.2, 0.25)

# ---------------- VOICE + DUCKING ----------------
w = wave.open(f"{S}/{TL['vo']}.wav"); vsr = w.getframerate(); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = signal.resample_poly(v, SR, vsr)
voice = np.zeros(N)
for c0, c1, at in TL["chunks"]:
    seg = v[int(c0 * SR):int(c1 * SR)].copy(); f = int(0.03 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    i0 = int(at * SR); voice[i0:i0 + len(seg)] += seg[:N - i0]
voice = hp(voice, 70) ; voice /= np.abs(voice).max(); voice *= 0.89
venv = np.sqrt(np.convolve(voice ** 2, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same'))
venv = np.clip(venv / (np.percentile(venv[venv > 1e-3], 60) + 1e-9), 0, 1)
venv = np.convolve(venv, np.ones(int(0.4 * SR)) / int(0.4 * SR), 'same')
duck = 1 - 0.62 * np.clip(venv, 0, 1)
bed = (music * 1.0 + amb * 1.0) * duck
bed *= 0.48 / (np.percentile(np.abs(bed), 99.9) + 1e-9)
vo2 = np.vstack([voice, voice])
mix = bed + vo2
# master fade
fo = np.clip((DUR - T) / 0.6, 0, 1); mix *= fo
mix /= max(1.0, np.abs(mix).max() / 0.97)
def wr(path, x):
    x = np.clip(x, -1, 1); y = (x.T * 32767).astype(np.int16)
    with wave.open(path, 'wb') as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(y.tobytes())
wr(f"{S}/mix_{LANG}.wav", mix); wr(f"{S}/vo_timed_{LANG}.wav", vo2); wr(f"{S}/bed_{LANG}.wav", bed / max(1, np.abs(bed).max() / 0.97))
print("done", LANG, np.abs(mix).max())
