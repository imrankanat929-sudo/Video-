"""HUMAN MIND 01 — audio: music edit + synthesized SFX + voiceover mix.
usage: python3 audio_mix.py OUTDIR [--vo assets/voiceover_ru.mp3]
Writes OUTDIR/{music_edit,sfx,voiceover,mix}.wav (48 kHz). Timings match render.html."""
import sys, os, subprocess, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
VO_FILE = sys.argv[sys.argv.index('--vo') + 1] if '--vo' in sys.argv else os.path.join(HERE, 'assets/voiceover_ru.mp3')
SR = 48000
END = 105.0
N = int(END * SR)
VO = 3.7
DROP = 3.4
MUSIC_DROP = 10.48          # beat drop inside the music file
FREEZE = 60.45
v = lambda x: x + VO
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def load(path, ch=2):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def save(path, x):
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', str(x.shape[1]), '-ar', str(SR), '-i', '-',
                    '-c:a', 'pcm_s24le', path], input=x.tobytes(), check=True)


def lp(x, f, order=4):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x, axis=0)


def hp(x, f, order=4):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)


def ramp(t, a, b):
    return np.clip((t - a) / (b - a), 0, 1)


tt = np.arange(N) / SR

# ---------------------------------------------------------------- voiceover
vo_raw = load(VO_FILE, 1)[:, 0]
vo_raw = hp(vo_raw, 75)
# gentle compression (static curve on a smoothed envelope)
envv = np.sqrt(lp(vo_raw ** 2, 12, 2).clip(1e-10))
gain = np.where(envv > .08, (envv / .08) ** (-.35), 1.0)
vo_c = vo_raw * gain
vo_c /= np.max(np.abs(vo_c)) + 1e-9
vo = np.zeros(N)
s0 = int(VO * SR)
n = min(len(vo_c), N - s0)
vo[s0:s0 + n] = vo_c[:n] * .9

# ---------------------------------------------------------------- music
mus = load(os.path.join(HERE, 'assets/music_lovibe.mp3'), 2)
off = MUSIC_DROP - DROP                          # video t -> music time t+off
m = np.zeros((N, 2))
idx = (tt + off) * SR
valid = idx < len(mus) - 1
m[valid] = mus[idx[valid].astype(int)]

# tape-stop on FREEZE: playback rate slides 1 -> 0, short silence, then the track resumes in place
ts0, ts1, resume = FREEZE - .05, FREEZE + .55, 61.6
i0, i1 = int(ts0 * SR), int(ts1 * SR)
k = np.arange(i1 - i0) / (i1 - i0)
rate = (1 - k) ** 1.6
pos = (ts0 + off) * SR + np.cumsum(rate)
m[i0:i1] = mus[pos.astype(int)] * (1 - k[:, None] ** 3)
m[i1:int(resume * SR)] = 0
# System 2 (slow thinking): calmer, darker, more space — crossfade dry -> low-passed
m_lp = lp(m, 650, 2)
ir_t = np.arange(int(1.8 * SR)) / SR
ir = rng.standard_normal((len(ir_t), 2)) * np.exp(-ir_t / .45)[:, None]
ir = lp(ir, 3000, 2); ir /= np.sqrt((ir ** 2).sum(0))
m_rev = np.stack([fftconvolve(m_lp[:, c], ir[:, c])[:N] for c in range(2)], 1)
slow = ramp(tt, resume, resume + 1.5) * (1 - ramp(tt, 82.2, 83.6))
m = m * (1 - slow[:, None]) + (m_lp * .75 + m_rev * .35) * slow[:, None] * .9
# fade in under the hook (intro is ambient), fade out at the end
m *= (np.clip(.45 + .55 * ramp(tt, 0, DROP), 0, 1) * (1 - ramp(tt, 100.5, END - .2)))[:, None]
# sidechain duck under the voice
vo_env = np.sqrt(lp(vo ** 2, 6, 2).clip(0))
duck_amt = np.clip(vo_env / .05, 0, 1)
duck_amt = lp(duck_amt, 2.5, 1)
base = .23 * (1 + 1.0 * (1 - ramp(tt, 2.8, 3.6)))  # louder in the hook
m *= (base * (1 - .45 * duck_amt))[:, None]

# ---------------------------------------------------------------- SFX
sfx = np.zeros((N, 2))


def add(x, t, g=1.0, pan=0.0):
    if x.ndim == 1: x = np.stack([x * (1 - max(0, pan)), x * (1 + min(0, pan))], 1)
    a = int(t * SR); b = min(N, a + len(x))
    if a >= N or b <= a: return
    sfx[a:b] += x[:b - a] * g


def env_exp(d, decay, attack=.002):
    t = np.arange(int(d * SR)) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay), t


def boom(d=2.2, f0=70, f1=32, decay=.55):
    e, t = env_exp(d, decay, .004)
    f = f1 + (f0 - f1) * np.exp(-t / .25)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * e
    nz = lp(rng.standard_normal(len(t)), 900) * np.exp(-t / .07) * .8
    return np.tanh((sub + nz) * 1.6) * .9


def whoosh(d=.9, up=True, lo=300, hi=5000):
    t = np.arange(int(d * SR)) / SR
    nz = rng.standard_normal(len(t))
    out = np.zeros(len(t)); seg = 1024
    for i in range(0, len(t), seg):
        k = i / len(t); k = k if up else 1 - k
        fc = lo * (hi / lo) ** k
        out[i:i + seg] = bp(nz[max(0, i - 2048):i + seg], fc * .7, min(fc * 1.4, SR / 2 - 100))[-len(nz[i:i + seg]):]
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** (1.5 if up else 2)
    if up: shape = (t / d) ** 2.2 * np.exp(-(np.maximum(0, t - d * .9)) / .05)
    return out * shape * 1.4


def blip(f=900, d=.09, g=.5, f2=None):
    e, t = env_exp(d, d / 3, .002)
    ff = f if f2 is None else f + (f2 - f) * t / d
    return np.sin(2 * np.pi * np.cumsum(np.ones_like(t) * ff) / SR) * e * g


def tick(g=.5):
    e, t = env_exp(.04, .006, .0005)
    return hp(rng.standard_normal(len(t)), 2500) * e * g


def bell(f=660, d=2.2, g=.3):
    e, t = env_exp(d, .6, .004)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * r * .8) for r, a in [(1, 1), (2.01, .35), (3.03, .15), (4.2, .07)])
    return x * e * g


def crack(g=1.0):
    e, t = env_exp(1.4, .09, .0005)
    nz = hp(rng.standard_normal(len(t)), 1200) * np.exp(-t / .05)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / .35) * a for f, a in [(523, .3), (1187, .25), (1873, .2), (2741, .12)])
    b = np.zeros(len(t)); bb = boom(1.0, 120, 50, .15); b[:len(bb)] = bb
    return (nz * 1.2 + ring * .7 + b * .6) * g


def glitch_blips(d, g=.25, rate=28):
    t = np.arange(int(d * SR)) / SR
    out = np.zeros(len(t))
    for i in range(int(d * rate)):
        a = int(rng.uniform(0, d - .03) * SR); L = int(rng.uniform(.008, .03) * SR)
        f = rng.choice([800, 1200, 1600, 2400, 3200])
        out[a:a + L] += np.sign(np.sin(2 * np.pi * f * np.arange(L) / SR)) * .5 * (rng.random() + .3)
    return lp(out, 7000) * g


def riser(d=2.0):
    t = np.arange(int(d * SR)) / SR
    k = t / d
    nz = whoosh(d, True, 400, 9000) * .8
    f = 120 * (8 ** k)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * .25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * .12
    return (nz + tone) * k ** 2.5


def heartbeat(g=.9):
    a = boom(.5, 60, 40, .09)
    b = np.zeros(int(.75 * SR)); b[:len(a)] += a; b[int(.22 * SR):int(.22 * SR) + len(a)] += a * .7
    return b * g


def shimmer(d=6.0, base=220, g=.25):
    t = np.arange(int(d * SR)) / SR
    e = np.minimum(1, t / 1.2) * np.exp(-np.maximum(0, t - 1.2) / 1.8)
    x = np.zeros((len(t), 2))
    for i, (r, a) in enumerate([(1, 1), (1.5, .6), (2, .5), (3, .3), (4, .2), (5.04, .12)]):
        for c in range(2):
            x[:, c] += a * np.sin(2 * np.pi * base * r * (1 + (c - .5) * .003 * i) * t + i)
    return x * e[:, None] * g


# --- beat grid (for the rhythmic pulses in System 1) ---
mono = mus.mean(1)
onset = np.maximum(0, np.diff(np.sqrt(lp(hp(mono, 40), 160, 2) ** 2 + 1e-9)))
best = (0, 60 / 92.3)
for P in np.linspace(.640, .660, 81):
    beats = (MUSIC_DROP + np.arange(120) * P) * SR
    sc = onset[beats[beats < len(onset)].astype(int)].sum()
    if sc > best[0]: best = (sc, P)
BEAT = best[1]
print('beat period', round(BEAT, 4))
beats_v = DROP + np.arange(200) * BEAT

# --- hook ---
add(boom(2.0, 90, 30, .5), .15, .9)
add(glitch_blips(.7, .22), .15, 1, -.3)
e, t = env_exp(1.0, .18)
add(hp(rng.standard_normal(len(t)), 3000) * e * (rng.random(len(t)) > .985) * 2.5, .15, .5, .3)   # electric crackle
add(glitch_blips(.55, .14), .3, 1, .2)
add(glitch_blips(.6, .14), 1.3, 1, -.2)
add(heartbeat(.7), 1.0)
add(riser(2.0), DROP - 2.0, .55)
add(blip(500, .25, .25, 900), 2.35)                  # "?" pops
add(boom(3.0, 80, 28, .8), DROP, 1.0)                # the drop
add(whoosh(1.2, False, 200, 6000), DROP, .45)
# --- scene 1 ---
for i, at in enumerate([4.8, 5.25, 5.7, 6.15, 6.6]):
    add(blip(700 + i * 120, .12, .35, 1100 + i * 120), at, 1, [-.4, .4, .3, -.6, .6][i])
add(blip(1200, .15, .2), v(4.3), 1, -.3)
add(whoosh(.5, True, 600, 4000), v(5.6), .25)        # door
for i in range(10):
    add(blip(1500, .05, .12) if i % 2 == 0 else blip(1700, .05, .12), v(6.7) + i * .12, 1, .4)   # phone ring
for i in range(5):
    add(whoosh(.18, True, 2000, 9000), v(9.5) + i * .12, .12)
    add(tick(.45), v(12.05) + i * .1, 1, [-.4, .4, .3, -.6, .6][i])
    add(blip(1800, .07, .18), v(12.05) + i * .1)
add(whoosh(.8, False, 200, 3000), v(13.2), .35)
add(boom(1.0, 90, 50, .12), v(14.2), .35)            # book lands
add(whoosh(.6, True, 500, 5000), v(20.6), .3)
add(whoosh(1.0, True, 300, 9000), v(23.3), .55)      # zoom into the orb
add(boom(1.5, 80, 40, .3), v(24.35), .45)
# --- system 1: rhythmic pulses ---
for b in beats_v:
    if v(24.4) <= b < v(28.0) or v(36.0) <= b < v(39.0):
        add(tick(.3), b); add(blip(220, .12, .2), b)
        add(tick(.15), b + BEAT / 2, 1, .3)
add(whoosh(.7, False, 300, 6000), v(28.0), .35)
add(tick(.6), v(29.5)); add(tick(.5), v(29.56))       # face brackets
add(bell(880, 1.2, .18), v(30.42)); add(bell(1320, 1.2, .14), v(30.6))
add(crack(.85), v(33.02), 1, -.5)                     # the sudden sound
add(blip(900, .12, .35, 1500), v(33.3))
add(whoosh(.8, True, 300, 8000), v(35.4), .45)
add(boom(1.2, 70, 40, .2), v(35.9), .35)
# --- the problem ---
add(glitch_blips(.9, .3, 40), v(39.0), 1)
add(boom(1.8, 60, 30, .4), v(39.0), .7)
add(whoosh(.7, True, 400, 7000), v(41.15), .4)
add(blip(1400, .2, .3, 700), v(41.75))
add(whoosh(.6, False, 300, 4000), 48.1, .3)
for i in range(3):
    add(blip(2093, .25, .14) + blip(3136, .25, .08), v(47.6) + i * .35, 1, .2 * i)
add(blip(880, .2, .25, 1320), v(49.9))               # "!" impression
add(blip(1500, .12, .2), v(50.9))
add(glitch_blips(.5, .3, 40), v(53.58)); add(boom(1.6, 55, 28, .4), v(53.58), .5)
# --- freeze / system 2 ---
add(boom(2.5, 45, 25, .9), FREEZE, .5)
add(shimmer(7.0, 110, .12), 61.6)
add(bell(330, 4.0, .16), v(60.06))
for i in range(3):
    add(bell(660 * [1, 1.25, 1.5][i], 2.5, .12), v(69.9) + i * 1.0, 1, [-.3, 0, .3][i])
add(blip(500, .4, .12, 300), v(66.92))
add(whoosh(1.2, True, 200, 2500), v(75.6), .2)
add(bell(990, 2.0, .1), v(75.8))
# --- final ---
add(whoosh(1.4, False, 150, 3000), 82.2, .35)
add(boom(2.0, 60, 30, .5), 82.4, .35)
add(bell(523, 2.5, .10), v(83.54), 1, .4)
add(bell(392, 2.5, .10), v(85.46), 1, -.4)
add(heartbeat(.8), v(91.18)); add(heartbeat(.6), v(91.18) + 1.0)
add(boom(4.0, 50, 25, 1.2), v(93.4), .85)
add(shimmer(8.0, 165, .2), v(93.4))
add(bell(1320, 3.0, .08), v(94.9))
add(shimmer(5.0, 220, .14), 101.0)

# ---------------------------------------------------------------- mix
vo2 = np.stack([vo, vo], 1)
mix = m + sfx * .55 + vo2 * 1.0
mix *= (1 - ramp(tt, END - .4, END))[:, None]
save(os.path.join(OUT, 'voiceover.wav'), vo2)
save(os.path.join(OUT, 'music_edit.wav'), m)
save(os.path.join(OUT, 'sfx.wav'), sfx * .55)
save(os.path.join(OUT, 'mix_raw.wav'), mix / (np.max(np.abs(mix)) + 1e-9) * .9)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(OUT, 'mix_raw.wav'), '-af',
                'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), '-c:a', 'pcm_s24le', os.path.join(OUT, 'mix.wav')], check=True)
os.remove(os.path.join(OUT, 'mix_raw.wav'))
print('ok')
