"""Client's recorded voice-over: load, align to the script (ASR word timestamps), cut and process clips."""
import os, json, re, difflib, hashlib
import numpy as np
import tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'voiceover_source', 'voice_ru.mp3')
WORDS = os.path.join(ROOT, 'assets', 'voiceover_source', 'voice_ru_words.json')
SR = tts.SR
_audio = None


def audio():
    global _audio
    if _audio is None:
        _audio = tts.load_audio(SRC, SR)
    return _audio


NUM = {'16': 'шестнадцать', '15': 'пятнадцать', '1': 'один', 'n0': 'эн0'}


def norm_tokens(text):
    t = text.lower().replace('ё', 'е').replace('n-0', 'n0').replace('—', ' ')
    toks = re.findall(r'[a-zа-я0-9]+', t)
    return [NUM.get(x, x) for x in toks]


def asr_words():
    segs = json.load(open(WORDS))
    out = []
    for s in segs:
        for a, b, w in s['w']:
            for tok in norm_tokens(w):
                out.append((tok, a, b))
    return out


def align(lines):
    """lines: list of texts (in spoken order). returns list of (start, end) in source seconds."""
    aw = asr_words()
    mine, owner = [], []
    for i, l in enumerate(lines):
        for tok in norm_tokens(l):
            mine.append(tok)
            owner.append(i)
    sm = difflib.SequenceMatcher(None, mine, [w[0] for w in aw], autojunk=False)
    m = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            m[a + k] = b + k
    res = []
    for i in range(len(lines)):
        idx = [m[j] for j in range(len(mine)) if owner[j] == i and j in m]
        if not idx:
            res.append(None)
            continue
        res.append((aw[min(idx)][1], aw[max(idx)][2]))
    return res


FX = {
    'N': None,
    'W': 'hush',
    'MIMA': 'vibrato=f=5.5:d=0.2,aphaser=in_gain=0.6:out_gain=0.8:delay=2.5:decay=0.5:speed=0.4,aecho=0.8:0.6:70|140:0.35|0.2,lowpass=f=5200',
    'MIMW': 'whisper',
    'HOOK': 'vibrato=f=6:d=0.25,aphaser=in_gain=0.6:out_gain=0.8:delay=3:decay=0.6:speed=0.5,aecho=0.8:0.7:90|180|360:0.4|0.25|0.15,lowpass=f=4800',
}
CACHE = os.path.join(ROOT, 'build', 'extvo_cache')
os.makedirs(CACHE, exist_ok=True)


_env = None


def envelope():
    """10 ms RMS envelope of the recording"""
    global _env
    if _env is None:
        a = audio()
        hop = SR // 100
        n = len(a) // hop
        _env = np.sqrt(np.mean(a[:n * hop].reshape(n, hop) ** 2, axis=1))
    return _env


def quietest(t0, t1):
    """time of the quietest 10 ms frame inside [t0, t1] (a clean cut point between words)"""
    env = envelope()
    a, b = max(0, int(t0 * 100)), min(len(env) - 1, int(t1 * 100))
    if b <= a:
        return (t0 + t1) / 2
    sm = np.convolve(env, np.ones(3) / 3, mode='same')
    return (a + int(np.argmin(sm[a:b + 1]))) / 100.0


def cut_spans(spans):
    """spans in source order -> non-overlapping [start, end] cut exactly in the pauses between lines"""
    out = []
    for i, (s, e) in enumerate(spans):
        if i == 0:
            a = max(0, s - 0.1)
        else:
            pe = spans[i - 1][1]
            a = quietest(min(pe, s) - 0.05, max(pe, s) + 0.05)
        if i == len(spans) - 1:
            b = e + 0.35
        else:
            ns = spans[i + 1][0]
            b = quietest(min(e, ns) - 0.05, max(e, ns) + 0.05)
        out.append((a, max(b, a + 0.2)))
    return out


def clip(spk, s, e):
    key = hashlib.md5(repr((spk, round(s, 3), round(e, 3), FX.get(spk), 4)).encode()).hexdigest()
    p = os.path.join(CACHE, key + '.f32')
    if os.path.exists(p):
        return np.fromfile(p, np.float32)
    a = audio()
    s0 = max(0, int(s * SR))
    e0 = min(len(a), int(e * SR))
    x = a[s0:e0].astype(np.float32).copy()
    fx = FX.get(spk)
    g_db = 0.0
    if fx == 'hush':
        # hushed: blend toward a whisper and bring it closer/quieter
        # hushed = simply softer and a touch warmer (no artificial whisper on the real voice)
        x = tts.ffx(x, SR, 'lowpass=f=9000', SR)
        g_db = -4.0
    elif fx == 'whisper':
        w = tts.whisperize(x, SR, keep=0.0, seed=int(s * 10))
        x = tts.ffx(w, SR, 'highpass=f=200,vibrato=f=4:d=0.12,aecho=0.8:0.7:90|180:0.4|0.25', SR)
        g_db = 5
    elif fx:
        x = tts.ffx(x, SR, fx, SR)
        g_db = 3
    x = x * 10 ** (g_db / 20)
    f = int(0.012 * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    x.astype(np.float32).tofile(p)
    return x
