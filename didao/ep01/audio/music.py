"""DIDAO Ep.1 — procedural original score + sound effects (numpy only).
Writes music.wav and sfx.wav (44.1 kHz stereo, 120 s) next to this file.
Timeline matches render/shots.js (final-video seconds)."""
import numpy as np, wave, os
SR = 44100; DUR = 120.0; N = int(SR * DUR)
rs = np.random.default_rng(7)
here = os.path.dirname(os.path.abspath(__file__))

def tt(d): return np.arange(int(d * SR)) / SR
def hz(n): return 440.0 * 2 ** ((n - 69) / 12)            # midi -> Hz
def note(name):
    names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    return names[name[:-1]] + 12 * (int(name[-1]) + 1)
def saw(f, t): return 2 * ((f * t) % 1.0) - 1
def lp(x, fc):  # brick-ish FFT low-pass with soft knee
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def env(n, a=0.01, r=0.2, s=1.0):
    e = np.ones(n) * s; na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, s, na)[:n] if na <= n else np.linspace(0, s, n)[:]
    if nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e
class Track:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def add(s, x, t0, gain=1.0, pan=0.0):
        i = int(t0 * SR); x = x[: max(0, N - i)]
        if i < 0: x = x[-i:]; i = 0
        s.L[i:i + len(x)] += x * gain * np.sqrt((1 - pan) / 2) * 1.414
        s.R[i:i + len(x)] += x * gain * np.sqrt((1 + pan) / 2) * 1.414
music, sfx = Track(), Track()

# ---------------- instruments ----------------
def pad(notes, d, cutoff=1400, a=0.8, r=1.0):
    t = tt(d); x = np.zeros(len(t))
    for n in notes:
        f = hz(n)
        for det in (-0.12, 0, 0.12): x += saw(f * 2 ** (det / 12), t + rs.random())
    x = lp(x / (3 * len(notes)), cutoff); return x * env(len(t), a, r)
def piano(n, d=2.5, vel=1.0):
    t = tt(d); f = hz(n)
    x = sum(np.sin(2 * np.pi * f * k * t) * (0.6 ** k) * np.exp(-t * (2.2 + k * 1.3)) for k in range(1, 6))
    return x * env(len(t), 0.003, 0.3) * vel * 0.6
def pluck(n, d=0.35, bright=3000):
    t = tt(d); x = (saw(hz(n), t) + 0.5 * saw(hz(n) * 1.005, t)) * np.exp(-t * 9)
    return lp(x, bright) * env(len(t), 0.002, 0.05) * 0.5
def bass(n, d=0.24):
    t = tt(d); x = saw(hz(n), t) + np.sin(2 * np.pi * hz(n) * t)
    return lp(x, 500) * env(len(t), 0.005, 0.06) * 0.6
def kick(d=0.45):
    t = tt(d); f = 45 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) * 1.0
def boom(d=2.5):
    t = tt(d); f = 32 + 80 * np.exp(-t * 9); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 1.8) + lp(rs.standard_normal(len(t)), 400) * 0.25 * np.exp(-t * 3)) * 1.2
def snare(d=0.25):
    t = tt(d); return (hp(rs.standard_normal(len(t)), 1500) * 0.5 + np.sin(2 * np.pi * 190 * t) * 0.5) * np.exp(-t * 18)
def hat(d=0.06):
    t = tt(d); return hp(rs.standard_normal(len(t)), 7000) * np.exp(-t * 60) * 0.35
def taiko(d=0.8):
    t = tt(d); f = 70 + 60 * np.exp(-t * 20); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + lp(rs.standard_normal(len(t)), 900) * 0.4) * np.exp(-t * 6)
def riser(d, f0=200, f1=4000):
    t = tt(d); x = hp(lp(rs.standard_normal(len(t)), f1), f0) * np.linspace(0, 1, len(t)) ** 2
    sw = np.sin(2 * np.pi * np.cumsum(np.geomspace(f0, f1, len(t))) / SR) * 0.15 * np.linspace(0, 1, len(t)) ** 3
    return x * 0.5 + sw
def whoosh(d=0.7):
    t = tt(d); x = rs.standard_normal(len(t)); X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    x = np.fft.irfft(X * np.exp(-((np.log(f + 1) - np.log(1500)) ** 2)), len(x)); e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return x * e * 2.0
def bell(n, d=1.6):
    t = tt(d); f = hz(n)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 3) * 0.5
def ping(hi=88, d=0.5): return bell(hi, d) * 0.8 + bell(hi + 7, d) * 0.4
def click(d=0.03): t = tt(d); return hp(rs.standard_normal(len(t)), 3000) * np.exp(-t * 250) * 0.8
def key(d=0.05): t = tt(d); return (hp(rs.standard_normal(len(t)), 2000) * 0.6 + np.sin(2 * np.pi * 1800 * t) * 0.2) * np.exp(-t * 120)
def tick(d=0.04): t = tt(d); return (np.sin(2 * np.pi * 3200 * t) + hp(rs.standard_normal(len(t)), 4000) * 0.5) * np.exp(-t * 150) * 0.6
def noise_bed(d, lo, hi): return hp(lp(rs.standard_normal(int(d * SR)), hi), lo)
def heartbeat(): return np.concatenate([kick(0.18) * 0.9, np.zeros(int(0.08 * SR)), kick(0.25) * 0.6])
def beep(f=1000, d=0.18): t = tt(d); return np.sign(np.sin(2 * np.pi * f * t)) * 0.25 * env(len(t), 0.005, 0.02)

def chords_pad(track, t0, t1, prog, bar, cutoff=1400, gain=0.5, octave_up=False):
    t = t0; i = 0
    while t < t1 - 0.05:
        d = min(bar, t1 - t) + 0.8; track.add(pad(prog[i % len(prog)], d, cutoff, a=0.25, r=0.8), t, gain, pan=0.0); t += bar; i += 1

# ================= A: 0 – 23.2  the world is waiting (D minor, 90 bpm) =================
BAR = 60 / 90 * 4; beat = BAR / 4
progA = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 48, 57, 60], [48, 55, 60, 64]]  # Dm Bb F C
chords_pad(music, 0, 23.0, progA, BAR, 1100, 0.55)
for b in range(int(23.0 / beat)):
    t = b * beat
    if t >= 4.6 and b % 2 == 0: music.add(taiko(), t, 0.55)
    if t >= 10 and b % 4 == 3: music.add(snare(0.4), t, 0.35)
    if t >= 10: music.add(hat(), t + beat / 2, 0.25, pan=0.3)
    if t >= 4.6: music.add(bass(progA[int(t // BAR) % 4][0] - 12, beat * 0.9), t, 0.5)
for i, n in enumerate([62, 65, 69, 72, 69, 65] * 6):  # ostinato
    t = 5.0 + i * beat / 2
    if t < 22.6: music.add(pluck(n, 0.3, 2400), t, 0.18, pan=-0.3 if i % 2 else 0.3)
music.add(boom(), 0.0, 0.6); music.add(boom(), 5.0, 0.7); music.add(bell(74, 3), 6.0, 0.3)
music.add(riser(3.0), 20.2, 0.35)
for s in range(5): sfx.add(tick(), 5.0 + s + 0.02, 0.5)                      # countdown ticks
sfx.add(noise_bed(6.6, 200, 2000) * env(int(6.6 * SR), 1.0, 1.5), 10.0, 0.06)  # crowd murmur
for i in range(6): sfx.add(ping(91, 0.4), 17.0 + i * 0.75, 0.18, pan=-0.4)     # social notifications
sfx.add(whoosh(0.8), 4.7, 0.25); sfx.add(whoosh(0.8), 9.7, 0.25); sfx.add(whoosh(0.8), 16.3, 0.25)

# ================= B: 23.2 – 42.6  no money (sad piano, A minor, 70 bpm) =================
BARB = 60 / 70 * 4; progB = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
t = 23.2; i = 0
while t < 42.4:
    ch = progB[i % 4]; music.add(pad([c - 12 for c in ch], BARB + 0.8, 700, a=0.6, r=0.8), t, 0.28)
    arp = [ch[0] - 12, ch[1], ch[2], ch[1] + 12, ch[2], ch[1]]
    for k, n in enumerate(arp + arp[:2]):
        tk = t + k * BARB / 8
        if tk < 42.5: music.add(piano(n, 2.0, 0.9 if k == 0 else 0.6), tk, 0.45, pan=(k % 3 - 1) * 0.25)
    t += BARB; i += 1
sfx.add(noise_bed(12.4, 800, 9000) * env(int(12.4 * SR), 1.0, 1.5), 23.2, 0.035)   # rain
sfx.add(click(), 28.75, 0.6); sfx.add(beep(220, 0.35), 28.95, 0.35); sfx.add(beep(180, 0.4), 29.3, 0.3)  # declined
sfx.add(noise_bed(0.5, 300, 3000) * env(int(0.5 * SR), 0.05, 0.3), 30.8, 0.2)   # wallet
for k in range(4): sfx.add(bell(96 - k, 0.5) * 0.6, 31.5 + k * 0.12, 0.25)    # coins
music.add(riser(3.4, 400, 6000), 39.2, 0.15)
sfx.add(bell(84, 2.5), 39.8, 0.55); sfx.add(bell(91, 2.5), 39.85, 0.35)       # idea!

# ================= C: 42.6 – 67  creating (electronic, 120 bpm, A minor) =================
bt = 0.5; progC = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
t = 42.6; b = 0
while t < 66.9:
    ch = progC[(b // 8) % 4]
    if t >= 49.0: music.add(kick(), t, 0.75)
    if t >= 49.0 and b % 2 == 1: music.add(snare(), t, 0.3)
    music.add(hat(), t + bt / 2, 0.3, pan=0.25)
    for h in (0, 1): music.add(bass(ch[0] - 24, bt / 2 * 0.9), t + h * bt / 2, 0.55 if t >= 49 else 0.3)
    for q in range(4):
        n = [ch[0], ch[1], ch[2], ch[1] + 12][(b * 4 + q) % 4] + 12
        music.add(pluck(n, 0.25, 2600 if t < 49 else 4500), t + q * bt / 4, 0.14, pan=(-0.4 if q % 2 else 0.4))
    if b % 8 == 0: music.add(pad(ch, 4.4, 1600, a=0.3), t, 0.22)
    t += bt; b += 1
rk = np.random.default_rng(3)
for i in range(70):  # typing the prompt
    sfx.add(key(), 42.85 + i * 0.058 + rk.random() * 0.02, 0.35 + rk.random() * 0.2, pan=rk.random() - 0.5)
sfx.add(click(), 47.1, 0.6); sfx.add(riser(1.8, 600, 8000), 47.2, 0.25)
for i in range(10): sfx.add(bell(96 + (i % 5) * 2, 0.4), 47.5 + i * 0.16, 0.08, pan=(i % 3 - 1) * 0.5)
for tt_ in (49.0, 53.2, 56.5, 62.6): sfx.add(whoosh(0.7), tt_ - 0.35, 0.35)
eng = tt(3.3); sfx.add(lp(saw(55 + 40 * eng / 3.3, eng) + saw(82 + 50 * eng / 3.3, eng) * 0.5, 900) * env(len(eng), 0.2, 0.5), 53.2, 0.18)  # engine
for i in range(30): sfx.add(key(), 62.7 + i * 0.05, 0.25)                         # typing title
for c in (64.2, 64.35): sfx.add(click(), c, 0.6)
sfx.add(bell(84, 1.2), 66.35, 0.4); sfx.add(bell(88, 1.2), 66.5, 0.4); sfx.add(bell(91, 1.5), 66.65, 0.4)   # published

# ================= D: 67 – 84.4  first results =================
music.add(pad([57, 60, 64, 69], 5.8, 900, a=0.5, r=1.0), 67.0, 0.3)
for i in range(int(5.0 / 0.12)): sfx.add(tick(), 67.4 + i * 0.12, 0.25)          # time-lapse clock
sfx.add(ping(88, 0.8), 71.6, 0.6)
music.add(riser(1.0, 500, 9000), 71.6, 0.3)
bt = 60 / 128; progD = [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]]   # C G Am F
t = 72.6; b = 0
while t < 84.3:
    ch = progD[(b // 4) % 4]; filt = 6000 if t < 80 else 1500 + (t - 80) * 600
    music.add(kick(), t, 0.8)
    if b % 2 == 1: music.add(snare(), t, 0.35)
    music.add(hat(), t + bt / 2, 0.3, pan=-0.25); music.add(hat(), t + bt * 0.25, 0.15, pan=0.25)
    music.add(bass(ch[0] - 12, bt * 0.45), t, 0.55); music.add(bass(ch[0] - 12, bt * 0.45), t + bt / 2, 0.45)
    for q in range(2): music.add(pluck(ch[(b * 2 + q) % 3] + 24, 0.3, filt), t + q * bt / 2, 0.16, pan=(q - 0.5))
    if b % 4 == 0: music.add(pad([c + 12 for c in ch], bt * 4 + 0.5, 2500, a=0.05), t, 0.22)
    t += bt; b += 1
for tp in (74.1, 76.1): sfx.add(ping(93, 0.7), tp, 0.55); sfx.add(boom(1.0) * 0.4, tp, 0.5)
for i in range(6): sfx.add(ping(86 + i % 3 * 2, 0.4), 73.3 + i * 0.9, 0.3, pan=0.5)   # comments pop
music.add(riser(3.0, 300, 7000), 81.4, 0.3)

# ================= E: 84.4 – 120  release + cliffhanger =================
T0 = 86.7
for k, tb in enumerate((84.7, 85.7)): sfx.add(beep(880, 0.15), tb, 0.5)
sfx.add(beep(1760, 0.5), T0, 0.5)
music.add(boom(3.5), T0, 1.0); sfx.add(whoosh(1.2), T0 - 0.6, 0.5)
sfx.add(riser(0.6, 800, 9000)[::-1], T0, 0.3)
for fw in (0, 0.25, 0.6, 0.9, 1.2, 1.5): sfx.add(noise_bed(0.6, 300, 4000) * np.exp(-tt(0.6) * 6), T0 + fw + 0.5, 0.25, pan=rs.random() - 0.5)  # firework pops
BARE = 60 / 90 * 4; beat = BARE / 4; progE = [[50, 57, 62, 66], [45, 52, 57, 61], [47, 54, 59, 62], [43, 50, 55, 59]]  # D A Bm G
t = T0; b = 0
while t < 101.3:
    ch = progE[int((t - T0) // BARE) % 4]
    if b % 4 == 0: music.add(pad(ch, BARE + 0.8, 2200, a=0.1), t, 0.5)
    if t < 94.8 or b % 2 == 0: music.add(taiko(), t, 0.6 if b % 2 == 0 else 0.35)
    if b % 4 == 2: music.add(snare(0.4), t, 0.35)
    music.add(bass(ch[0] - 12, beat * 0.9), t, 0.5)
    music.add(pluck(ch[(b % 3) + 1] + 12, 0.4, 3500), t + beat / 2, 0.14, pan=0.3 if b % 2 else -0.3)
    t += beat; b += 1
for i, tp in enumerate((91.6, 92.2, 92.8, 93.4)): sfx.add(ping(88 + i * 2, 0.5), tp, 0.4, pan=0.3)
# 99.1 — mysterious message: glitch hit
g = tt(0.6); sfx.add(np.sign(np.sin(2 * np.pi * 70 * g)) * np.exp(-g * 6) * 0.4 + hp(rs.standard_normal(len(g)), 2000) * np.exp(-g * 10) * 0.5, 99.1, 0.55)
music.add(boom(3.0), 99.1, 0.6)
# dark suspense 101.4 – 114
dr = tt(13.0); drone = lp(saw(hz(38), dr) + saw(hz(38) * 1.006, dr) + saw(hz(45), dr) * 0.6 + saw(hz(39), dr) * 0.3, 380)
music.add(drone * env(len(dr), 1.5, 3.0) * 0.35, 101.0, 0.6)
for i in range(9): music.add(heartbeat(), 101.6 + i * 0.95, 0.45)
for i, n in enumerate([69, 68, 67, 64, 69, 72, 71]): music.add(piano(n, 3.0, 0.7), 107.8 + i * 0.85, 0.35, pan=(i % 3 - 1) * 0.3)
# end card
music.add(boom(3.0), 114.0, 0.8); sfx.add(whoosh(0.8), 113.6, 0.35)
music.add(pad([50, 57, 62, 66, 69], 6.0, 2500, a=0.05, r=3.0), 114.0, 0.55)
music.add(bell(86, 4), 114.0, 0.3)

# ---------------- reverb + master ----------------
def reverb(x, secs=2.2, wet=0.25):
    ir = rs.standard_normal(int(secs * SR)) * np.exp(-np.linspace(0, 7, int(secs * SR))); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    n = len(x) + len(ir); nf = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[: len(x)]
    return x * (1 - wet) + y * wet * 3
def write(path, tr, wet):
    L, R = reverb(tr.L, wet=wet), reverb(tr.R, wet=wet)
    fade = np.ones(N); fade[-int(2.5 * SR):] = np.linspace(1, 0, int(2.5 * SR)) ** 2
    st = np.stack([L * fade, R * fade], 1); st = np.tanh(st / (np.abs(st).max() * 0.9) * 1.2) * 0.89
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
write(os.path.join(here, 'music.wav'), music, 0.22)
write(os.path.join(here, 'sfx.wav'), sfx, 0.12)
print('ok')
