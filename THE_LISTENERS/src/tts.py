"""Voice-over generation: Piper neural TTS (offline) + gTTS (female voices) + whisper conversion + character FX."""
import hashlib, os, subprocess, wave, io
import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICES = os.path.join(ROOT, 'assets', 'voices')
CACHE = os.path.join(ROOT, 'build', 'vo_cache')
SR = 48000
os.makedirs(CACHE, exist_ok=True)

_voices = {}


def piper_voice(name):
    from piper import PiperVoice
    if name not in _voices:
        _voices[name] = PiperVoice.load(os.path.join(VOICES, f'ru_{name}.onnx'))
    return _voices[name]


def piper_tts(text, voice, length=1.0, noise=0.6, noise_w=0.7):
    from piper import SynthesisConfig
    v = piper_voice(voice)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        v.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length, noise_scale=noise, noise_w_scale=noise_w))
    buf.seek(0)
    with wave.open(buf, 'rb') as wf:
        sr = wf.getframerate()
        x = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    return x, sr


def gtts_tts(text, slow=False):
    from gtts import gTTS
    os.environ.setdefault('REQUESTS_CA_BUNDLE', '/root/.ccr/ca-bundle.crt')
    p = os.path.join(CACHE, 'gtts_' + hashlib.md5((text + str(slow)).encode()).hexdigest() + '.mp3')
    if not os.path.exists(p):
        gTTS(text, lang='ru', slow=slow).save(p)
    return load_audio(p, 24000), 24000


def load_audio(path, sr=SR):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).copy()


def ffx(x, sr, filt, out_sr=SR):
    """run a mono float signal through an ffmpeg audio filter chain"""
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-af', filt,
                        '-f', 'f32le', '-ac', '1', '-ar', str(out_sr), '-'], input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def trim(x, thr=0.01, pad=0.04, sr=SR):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * sr))
    b = min(len(x), idx[-1] + int(pad * sr * 3))
    return x[a:b]


def whisperize(x, sr, keep=0.12, seed=0):
    """Turn voiced speech into a whisper: keep the smoothed spectral envelope (formants),
    replace the excitation by noise (cepstral liftering), add a little of the original for intelligibility."""
    n = 1024 if sr > 30000 else 512
    hop = n // 4
    f, tt, X = signal.stft(x, sr, nperseg=n, noverlap=n - hop, window='hann')
    mag = np.abs(X) + 1e-7
    logm = np.log(mag)
    cep = np.fft.irfft(logm, axis=0)
    L = int(sr / 1000 * 1.6)  # lifter ~1.6 ms quefrency -> removes pitch harmonics
    lif = np.zeros(cep.shape[0])
    lif[:L] = 1
    lif[-L + 1:] = 1
    env = np.exp(np.fft.rfft(cep * lif[:, None], axis=0).real)
    rng = np.random.RandomState(seed)
    ph = np.exp(1j * rng.uniform(-np.pi, np.pi, X.shape))
    # whisper spectral tilt: less low end, more breath around 2-6 kHz
    tilt = np.ones_like(f)
    tilt *= np.clip((f - 150) / 600, 0.08, 1.0)
    tilt *= 1 + 0.6 * np.exp(-((f - 3500) / 2200) ** 2)
    Y = env * ph * tilt[:, None]
    _, y = signal.istft(Y, sr, nperseg=n, noverlap=n - hop, window='hann')
    y = y[:len(x)]
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    # match energy envelope
    def rms_env(s):
        return np.sqrt(np.maximum(signal.convolve(s ** 2, np.ones(int(0.02 * sr)) / int(0.02 * sr), mode='same'), 0) + 1e-9)
    ex, ey = rms_env(x), rms_env(y)
    y = y * np.clip(ex / ey, 0, 8)
    b, a = signal.butter(2, 120 / (sr / 2), 'high')
    xo = signal.lfilter(b, a, x)
    return np.nan_to_num(y * (1 - keep) + xo * keep).astype(np.float32)


def norm_rms(x, target_db=-20.0):
    act = x[np.abs(x) > 0.02 * np.max(np.abs(x) + 1e-9)]
    if len(act) == 0:
        return x
    r = np.sqrt(np.mean(act ** 2))
    g = 10 ** (target_db / 20) / (r + 1e-9)
    y = x * g
    pk = np.max(np.abs(y))
    if pk > 0.97:
        y *= 0.97 / pk
    return y


PROFILE = {
    # narrator: low, slow, close-mic documentary
    'N': dict(src=('piper', 'ruslan', 1.14), pitch=0.9, whisper=False, fx='equalizer=f=140:t=q:w=1:g=3,equalizer=f=3200:t=q:w=1:g=1.5,acompressor=threshold=0.1:ratio=3:attack=5:release=120', db=-19),
    'W': dict(src=('piper', 'ruslan', 1.2), pitch=0.92, whisper=True, keep=0.10, fx='highpass=f=170,equalizer=f=5000:t=q:w=1:g=2,acompressor=threshold=0.08:ratio=4:attack=3:release=100', db=-20),
    'A': dict(src=('piper', 'denis', 1.08), pitch=1.06, whisper=True, keep=0.10, fx='highpass=f=140,acompressor=threshold=0.08:ratio=4:attack=3:release=100', db=-21),
    'AN': dict(src=('piper', 'denis', 1.05), pitch=1.06, whisper=False, fx='highpass=f=100,aecho=0.8:0.5:35:0.12', db=-21),
    'MIMA': dict(src=('piper', 'denis', 1.18), pitch=1.04, whisper=False, fx='vibrato=f=5.5:d=0.18,aphaser=in_gain=0.6:out_gain=0.8:delay=2.5:decay=0.5:speed=0.4,aecho=0.8:0.6:70|140:0.35|0.2,lowpass=f=5200', db=-21),
    'MOM': dict(src=('gtts', None, 0.92), pitch=0.98, whisper=False, fx='vibrato=f=4.5:d=0.10,aecho=0.8:0.55:60|120:0.3|0.18,lowpass=f=6000', db=-21),
    'TV': dict(src=('piper', 'dmitri', 1.0), pitch=1.0, whisper=False, fx='highpass=f=320,lowpass=f=3400,acrusher=bits=10:mix=0.25,acompressor=threshold=0.05:ratio=6', db=-22),
    'MIRA': dict(src=('gtts', None, 1.0), pitch=1.03, whisper=True, keep=0.12, fx='highpass=f=160,acompressor=threshold=0.08:ratio=4', db=-21),
    'VIK': dict(src=('piper', 'dmitri', 1.05), pitch=0.93, whisper=True, keep=0.12, fx='highpass=f=120,acompressor=threshold=0.08:ratio=4', db=-21),
    'MIMW': dict(src=('piper', 'denis', 1.35), pitch=1.0, whisper=True, keep=0.05, fx='highpass=f=200,vibrato=f=4:d=0.12,aecho=0.8:0.7:90|180:0.4|0.25', db=-23),
    'FRIEND': dict(src=('piper', 'denis', 1.05), pitch=1.12, whisper=False, fx='vibrato=f=5:d=0.12,aecho=0.8:0.7:150|300:0.35|0.2,highpass=f=220,lowpass=f=4200', db=-24),
    'VIKL': dict(src=('piper', 'dmitri', 1.0), pitch=0.93, whisper=False, fx='vibrato=f=4:d=0.08,aecho=0.8:0.7:180|360:0.35|0.2,highpass=f=200,lowpass=f=4500', db=-23),
    'MAN': dict(src=('piper', 'dmitri', 0.95), pitch=0.9, whisper=False, fx='highpass=f=180,aecho=0.8:0.7:160|320:0.35|0.18,acompressor=threshold=0.1:ratio=3', db=-21),
}


def say_text(text):
    """text adjustments for TTS pronunciation"""
    rep = {'N-0': 'эн-ноль', '«': '', '»': '', '—': ',', '...': '…'}
    for a, b in rep.items():
        text = text.replace(a, b)
    return text


def synth(spk, text):
    pr = PROFILE[spk]
    key = hashlib.md5(repr((spk, text, pr)).encode()).hexdigest()
    path = os.path.join(CACHE, f'{spk}_{key}.f32')
    if os.path.exists(path):
        return np.fromfile(path, np.float32)
    kind, voice, length = pr['src']
    st = say_text(text)
    if kind == 'piper':
        x, sr = piper_tts(st, voice, length)
    else:
        x, sr = gtts_tts(st)
        if length != 1.0:
            x = ffx(x, sr, f'atempo={length:.3f}', sr)
    x = x.astype(np.float32)
    # pitch (formant-preserving)
    if abs(pr['pitch'] - 1.0) > 1e-3:
        x = ffx(x, sr, f'rubberband=pitch={pr["pitch"]}:formant=preserved', sr)
    if pr['whisper']:
        x = whisperize(x, sr, pr.get('keep', 0.12), seed=len(text))
    y = ffx(x, sr, f'aresample={SR},' + pr['fx'], SR)
    y = trim(y, 0.004)
    y = norm_rms(y, pr['db'])
    # tiny fades
    f = int(0.01 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    y.astype(np.float32).tofile(path)
    return y


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    for spk in ['N', 'W', 'A', 'MIMA', 'MOM', 'TV', 'MIRA', 'VIK', 'MAN']:
        y = synth(spk, 'Если ты слышишь эту запись, говори тише. Они уже рядом.')
        print(spk, len(y) / SR)
