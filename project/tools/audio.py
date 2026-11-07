"""Procedural soundtrack: music bed + SFX, mixed with the voice-over.

usage: python3 tools/audio.py ru
writes assets/audio/music_<lang>.wav, sfx_<lang>.wav, mix_<lang>.wav
All timings come from config/timeline.<lang>.json (audio.events / audio.music).
"""
import json, subprocess, sys, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = sys.argv[1] if len(sys.argv) > 1 else 'ru'
TL = json.load(open(os.path.join(ROOT, 'config', f'timeline.{LANG}.json')))
SR = 48000
DUR = TL['duration']
N = int(DUR * SR)
rng = np.random.default_rng(7)

def db(x): return 10 ** (x / 20)
def t_(d): return np.arange(int(d * SR)) / SR
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def noise(d): return rng.standard_normal(int(d * SR))

def reverb_ir(d=2.6, decay=3.2):
    n = noise(d) * np.exp(-decay * t_(d))
    return lp(n, 5000) / np.sqrt(np.sum(n ** 2))
IR = reverb_ir()
def verb(x, wet=0.3):
    return x * (1 - wet) + signal.fftconvolve(x, IR)[:len(x)] * wet * 3

def place(buf, x, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x * gain

# ---------------- SFX ----------------
def sfx_vibrate(n=2):
    out = np.zeros(int((n * 0.58 + 0.2) * SR))
    for k in range(n):
        d = 0.38; tt = t_(d)
        f = 155 + 6 * np.sin(2 * np.pi * 9 * tt)
        buzz = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR)
        rattle = bp(noise(d), 300, 2500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 155 * tt)))
        env = np.minimum(1, tt / 0.01) * np.minimum(1, (d - tt) / 0.02)
        place(out, lp(buzz * 0.6 + rattle * 0.35, 1800) * env, k * 0.58)
    return out * 0.5

def sfx_hit():
    d = 3.2; tt = t_(d)
    f = 38 + 60 * np.exp(-tt * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.4)
    thump = lp(noise(d), 900) * np.exp(-tt * 22) * 0.8
    sub = np.sin(2 * np.pi * 31 * tt) * np.exp(-tt * 0.9) * 0.6
    x = body + thump + sub
    x = verb(x, 0.35)
    return np.tanh(x * 1.4) * 0.9

def sfx_ping():
    out = np.zeros(int(1.6 * SR))
    for k, f in enumerate([1318.5, 1760.0]):
        tt = t_(1.2)
        tone = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * f * 2 * tt)) * np.exp(-tt * 9) * np.minimum(1, tt / 0.004)
        place(out, tone, k * 0.09)
    return verb(out, 0.25) * 0.35

def sfx_click():
    tt = t_(0.06)
    x = hp(noise(0.06), 2500) * np.exp(-tt * 140) * 0.6 + np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 120) * 0.3
    return x * 0.5

def sfx_refresh():
    d = 0.5; tt = t_(d)
    sw = bp(noise(d), 800, 5000) * np.sin(np.pi * tt / d) ** 2 * 0.12
    out = np.zeros(int(0.8 * SR)); place(out, sw, 0); place(out, sfx_click(), 0.62)
    return out

def sfx_whoosh():
    d = 0.7; tt = t_(d)
    n = noise(d)
    # rising band via chunked filtering
    out = np.zeros_like(n); seg = int(0.035 * SR)
    for i in range(0, len(n), seg):
        k = i / len(n); lo = 200 + 2500 * k ** 2
        out[i:i + seg] = bp(n[max(0, i - seg):i + seg], lo, lo * 2.5)[-len(n[i:i + seg]):]
    env = (tt / d) ** 2.2 * np.minimum(1, (d - tt) / 0.03)
    return out * env * 0.9

def sfx_alarm():
    out = np.zeros(int(1.6 * SR))
    for k in range(3):
        tt = t_(0.16)
        x = (np.sin(2 * np.pi * 622 * tt) + np.sin(2 * np.pi * 659 * tt)) * np.minimum(1, tt / 0.005) * np.minimum(1, (0.16 - tt) / 0.02)
        place(out, x, k * 0.24)
    return verb(lp(out, 3000), 0.3) * 0.12

def sfx_shimmer():
    d = 3.0; tt = t_(d); x = np.zeros_like(tt)
    for f in [1174.7, 1568, 1760, 2349.3, 2637]:
        x += np.sin(2 * np.pi * f * tt + rng.random() * 6) * np.exp(-tt * (1.2 + rng.random()))
    return verb(x * np.minimum(1, tt / 0.05), 0.5) * 0.05

def sfx_keyboard(dur=3.0):
    out = np.zeros(int((dur + 0.2) * SR)); t = 0.0
    while t < dur:
        tt = t_(0.05)
        k = bp(noise(0.05), 900, 5000) * np.exp(-tt * (90 + rng.random() * 60)) * (0.5 + rng.random() * 0.5)
        k += lp(noise(0.05), 400) * np.exp(-tt * 60) * 0.4
        place(out, k, t)
        t += 0.06 + rng.random() * 0.16 + (0.35 if rng.random() < 0.08 else 0)
    return out * 0.28

def sfx_ringback(dur=4.9):
    out = np.zeros(int(dur * SR)); t = 0.2
    while t < dur - 0.2:
        tt = t_(0.9)
        place(out, np.sin(2 * np.pi * 425 * tt) * np.minimum(1, tt / 0.01) * np.minimum(1, (0.9 - tt) / 0.01), t)
        t += 3.0
    return bp(out, 300, 3400) * 0.05

def sfx_tick():
    d = 1.2; tt = t_(d)
    x = np.sin(2 * np.pi * (70 + 40 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 6) + lp(noise(d), 1500) * np.exp(-tt * 40) * 0.3
    return verb(x, 0.3) * 0.45

def roomtone(start, until):
    d = until - start
    brown = np.cumsum(noise(d)); brown = hp(brown, 20); brown /= np.max(np.abs(brown)) + 1e-9
    room = lp(brown, 250) * 0.5
    hum = (np.sin(2 * np.pi * 100 * t_(d)) * 0.02 + np.sin(2 * np.pi * 200 * t_(d)) * 0.008)
    rain = bp(noise(d), 2500, 7000) * 0.012 * (1 + 0.3 * np.sin(2 * np.pi * 0.13 * t_(d)))
    x = (room + hum + rain) * 0.09
    fade = np.minimum(1, t_(d) / 1.0) * np.minimum(1, (d - t_(d)) / 1.5)
    return x * fade

def sfx_rewind():
    d = 1.6; tt = t_(d)
    f = 300 + 2200 * (tt / d) ** 1.5
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + bp(noise(d), 1500, 6000) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * tt))
    return x * np.minimum(1, tt / 0.05) * np.minimum(1, (d - tt) / 0.2) * 0.6

def sfx_ringtone(dur=3.4):
    out = np.zeros(int(dur * SR)); t = 0.0
    mel = [659.3, 784, 987.8, 784]
    while t < dur - 0.2:
        for k, f in enumerate(mel):
            tt = t_(0.16)
            place(out, (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 10), t + k * 0.17)
        t += 1.4
    return verb(lp(out, 4000), 0.2) * 0.22

def sfx_clock(dur=2.0):
    out = np.zeros(int(dur * SR)); t = 0.0
    while t < dur:
        tt = t_(0.05); place(out, bp(noise(0.05), 2000, 6000) * np.exp(-tt * 200) * 0.7, t); t += 1 / 3
    return out * 0.4

def sfx_hangup():
    out = np.zeros(int(2.2 * SR))
    for k in range(3):
        tt = t_(0.35); place(out, np.sin(2 * np.pi * 425 * tt) * np.minimum(1, tt / 0.01) * np.minimum(1, (0.35 - tt) / 0.01), 0.2 + k * 0.7)
    return bp(out, 300, 3400) * 0.06

def sfx_knock():
    d = 0.9; tt = t_(d)
    x = np.sin(2 * np.pi * (95 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) + bp(noise(d), 300, 2500) * np.exp(-tt * 40) * 0.6
    x += np.sin(2 * np.pi * 410 * tt) * np.exp(-tt * 14) * 0.25        # metallic ring
    return verb(x, 0.4) * 0.9

def sfx_squeak():
    d = 0.5; tt = t_(d); f = 900 + 500 * tt / d
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * tt)) * np.sin(np.pi * tt / d) * 0.12
    return x + hp(noise(d), 3000) * np.sin(np.pi * tt / d) * 0.04

def sfx_flow(dur=6.0):
    tt = t_(dur); x = bp(noise(dur), 300, 3000) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * tt)) * 0.25
    x += bp(noise(dur), 2000, 6000) * 0.05
    return x * np.minimum(1, tt / 0.8) * np.minimum(1, (dur - tt) / 0.8)

def sfx_drain():
    d = 2.2; tt = t_(d); n = noise(d); out = np.zeros_like(n); seg = int(0.04 * SR)
    for i in range(0, len(n), seg):
        k = i / len(n); f = 1600 - 1300 * k
        out[i:i + seg] = bp(n[max(0, i - seg):i + seg], f * 0.7, f * 1.4)[-len(n[i:i + seg]):]
    gurgle = np.sin(2 * np.pi * (180 - 100 * tt / d) * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7 * tt))) * 0.15
    return (out * 0.5 + gurgle) * np.sin(np.pi * tt / d)

def sfx_shutter():
    out = np.zeros(int(0.3 * SR)); place(out, sfx_click() * 1.5, 0); place(out, hp(noise(0.05), 2000) * np.exp(-t_(0.05) * 80) * 0.4, 0.07)
    return out

def sfx_jingle():
    out = np.zeros(int(2.0 * SR))
    for k, f in enumerate([523.3, 659.3, 784.0, 1046.5]):
        tt = t_(0.9); place(out, (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 4), k * 0.12)
    return verb(out, 0.3) * 0.18

def sfx_crowd(dur=6.0):
    tt = t_(dur); x = np.zeros_like(tt)
    for i in range(6):
        x += bp(noise(dur), 250 + i * 80, 900 + i * 120) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.8 + rng.random() * 2) * tt + rng.random() * 6)) ** 2
    return x * 0.06 * np.minimum(1, tt / 1.0) * np.minimum(1, (dur - tt) / 1.0)

def sfx_alert():
    d = 1.6; tt = t_(d)
    x = (np.sin(2 * np.pi * 853 * tt) + np.sin(2 * np.pi * 960 * tt)) * 0.5 * (np.sin(2 * np.pi * 2.5 * tt) > 0)
    return lp(x, 3000) * np.minimum(1, tt / 0.02) * np.minimum(1, (d - tt) / 0.05) * 0.1

SFX = {'knock': lambda e: sfx_knock(), 'squeak': lambda e: sfx_squeak(), 'flow': lambda e: sfx_flow(e.get('dur', 6)),
       'drain': lambda e: sfx_drain(), 'shutter': lambda e: sfx_shutter(), 'jingle': lambda e: sfx_jingle(),
       'crowd': lambda e: sfx_crowd(e.get('dur', 6)), 'alert': lambda e: sfx_alert(),
       'rewind': lambda e: sfx_rewind(), 'ringtone': lambda e: sfx_ringtone(e.get('dur', 3.4)),
       'clock': lambda e: sfx_clock(e.get('dur', 2.0)), 'hangup': lambda e: sfx_hangup(),
       'vibrate': lambda e: sfx_vibrate(e.get('n', 2)), 'hit': lambda e: sfx_hit(), 'ping': lambda e: sfx_ping(),
       'click': lambda e: sfx_click(), 'ui': lambda e: sfx_click() * 0.7 + 0, 'refresh': lambda e: sfx_refresh(),
       'whoosh': lambda e: sfx_whoosh(), 'alarm': lambda e: sfx_alarm(), 'shimmer': lambda e: sfx_shimmer(),
       'keyboard': lambda e: sfx_keyboard(e.get('dur', 3)), 'ringback': lambda e: sfx_ringback(e.get('dur', 4.9)),
       'tick': lambda e: sfx_tick()}

def build_sfx():
    buf = np.zeros(N)
    for e in TL['audio']['events']:
        if e['type'] == 'roomtone':
            rt = roomtone(e['t'], min(e['until'], TL['cues']['camera_freeze']))
            # one-beat dip into silence before the last message
            tt = e['t'] + np.arange(len(rt)) / SR
            s0, s1 = TL['cues']['silence_start'], TL['cues']['keep_msg']
            dip = 1 - 0.85 * np.clip(np.minimum((tt - s0) / 0.3, (s1 - tt) / 0.05), 0, 1)
            place(buf, rt * dip, e['t'])
        else:
            place(buf, SFX[e['type']](e), e['t'], db(e.get('gain', 0)))
    return buf

# ---------------- music ----------------
NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)
CHORDS = [  # (start, end, midi notes)
    (0.0, 13.2, [38, 45, 53]),          # Dm
    (12.6, 22.6, [38, 46, 52, 57]),     # tension (D, Bb, E, A)
    (22.6, 29.4, [38, 45, 52, 53]),     # Dm add9
    (28.8, 40.6, [34, 41, 50, 53]),     # Bb
    (40.0, 47.4, [31, 38, 46, 50]),     # Gm
    (46.6, 57.4, [33, 40, 49, 52]),     # A (unresolved)
    (56.8, 68.0, [38, 45, 50, 53]),     # Dm
]
def pad(notes, d):
    tt = t_(d); x = np.zeros_like(tt)
    for n in notes:
        f = NOTE(n)
        for det in (-0.12, 0.0, 0.11):
            ph = 2 * np.pi * f * (1 + det / 100 * 6) * tt + rng.random() * 6
            saw = sum(np.sin(ph * h) / h for h in range(1, 9))
            x += saw * (1.0 if n < 45 else 0.6)
    x = lp(x, 650, 4)
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * tt + rng.random() * 6)
    fade = np.minimum(1, tt / 0.9) * np.minimum(1, (d - tt) / 0.9)
    return x * swell * fade / (len(notes) * 3)

def heartbeat(start, end, bpm=68):
    out = np.zeros(int((end - start + 1) * SR)); t = 0.0; period = 60 / bpm
    while t < end - start:
        for off, a in ((0, 1.0), (0.22, 0.7)):
            tt = t_(0.5)
            place(out, np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 10) * a, t + off)
        t += period
    return out

def build_music():
    buf = np.zeros(N)
    A = TL['audio']
    for s, e, notes in A.get('chords', CHORDS):
        place(buf, pad(notes, e - max(s, 0)), max(s, 0))
    # eerie high tone through the threat sections
    for st, d in A.get('eerie', [[12.8, 10.0]]):
        tt = t_(d)
        place(buf, np.sin(2 * np.pi * NOTE(86) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * tt)) * np.sin(np.pi * tt / d) ** 2 * 0.05, st)
    for s, e, bpm in A.get('heart', [[9.8, 22.2, 68], [34.7, 40.1, 76], [48.9, 56.8, 60]]):
        place(buf, heartbeat(s, e, bpm) * 0.45, s)
    # automation
    pts = TL['audio']['music']
    ts = np.array([p['t'] for p in pts]); lv = np.array([p['level'] for p in pts])
    env = np.interp(np.arange(N) / SR, ts, lv)
    env = lp(env, 8)  # smooth steps a little
    return buf * np.clip(env, 0, 1)

# ---------------- mix ----------------
def load_voice():
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(ROOT, TL['voice']), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    buf = np.zeros(N); place(buf, v, TL['voiceOffset'])
    return buf

def norm(x, peak_db=-1.0):
    return x / (np.max(np.abs(x)) + 1e-9) * db(peak_db)

def write(name, x):
    st = np.stack([x, x], axis=1) if x.ndim == 1 else x
    wavfile.write(os.path.join(ROOT, 'assets', 'audio', name), SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))

if __name__ == '__main__':
    voice = load_voice()
    music = norm(build_music(), -6) * db(TL['audio']['musicGainDb'] + 6)
    sfx = build_sfx()
    # duck music under the voice (up to -5 dB)
    venv = lp(np.abs(voice), 6); venv = venv / (venv.max() + 1e-9)
    duck = 1 - 0.45 * np.clip(venv * 4, 0, 1)
    tt = np.arange(N) / SR
    tail = np.clip((TL['cues']['camera_freeze'] + 1.0 - tt) / 0.8, 0, 1)   # everything but the voice dies out
    mix = voice * db(TL['audio']['voiceGainDb']) + (music * duck + sfx * db(-8)) * tail
    # true silence after the hard cut
    mix *= np.clip((TL['cues']['hard_black'] - tt) / 0.05, 0, 1)
    peak = np.max(np.abs(mix))
    if peak > db(-1): mix *= db(-1) / peak
    write(f'music_{LANG}.wav', music)
    write(f'sfx_{LANG}.wav', sfx * db(-8))
    write(f'mix_{LANG}.wav', mix)
    print('ok, peak', 20 * np.log10(np.max(np.abs(mix))))
