"""Build the English voice-over: one TTS clip per Russian segment, placed at the same start time.
usage: python tts_en.py kokoro.onnx voices.bin out.wav"""
import sys, json, os, subprocess
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
import subs

SR = 24000
DUR = 123.17
TEXTS = [t.replace(' / ', ' ').replace('/', ' ').replace('"', '') for t in subs.SEGMENTS_EN_TEXT]
RU = subs.SEGMENTS  # ru timing (run with VIDEO_LANG=ru)
k = Kokoro(sys.argv[1], sys.argv[2])
out = np.zeros(int(DUR * SR) + SR)
timing = []
prev_end = 0.0
for i, (txt, (a, b, _)) in enumerate(zip(TEXTS, RU)):
    s, sr = k.create(txt, voice='am_michael', speed=1.0, lang='en-us')
    # trim silence
    idx = np.where(np.abs(s) > 0.01)[0]
    s = s[max(0, idx[0] - 200): idx[-1] + 600]
    start = max(a, prev_end + 0.08)
    nxt = RU[i + 1][0] if i + 1 < len(RU) else DUR - 0.3
    slot = nxt - start - 0.06
    dur = len(s) / sr
    if dur > slot and slot > 0.3:
        tempo = min(dur / slot, 1.3)
        p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-',
                            '-filter:a', f'atempo={tempo:.3f}', '-f', 'f32le', '-'], input=s.astype(np.float32).tobytes(),
                           capture_output=True)
        s = np.frombuffer(p.stdout, dtype=np.float32)
        dur = len(s) / sr
    i0 = int(start * SR)
    out[i0:i0 + len(s)] += s
    timing.append((round(start, 3), round(start + dur, 3)))
    prev_end = start + dur
    print(f"{start:7.2f} {start + dur:7.2f} slot_end={nxt:7.2f} {txt}")
out = out[:int(DUR * SR)]
out /= np.abs(out).max() / 0.95
sf.write(sys.argv[3], out, SR)
json.dump(timing, open(os.path.join(os.path.dirname(__file__), '..', 'assets', 'voice_en_timing.json'), 'w'))
