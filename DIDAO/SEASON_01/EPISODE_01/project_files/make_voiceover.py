"""Cut the client's recorded voiceover (RU + EN) into per-line WAVs.

Input : ../voiceover/source/DIDAO_EP01_VO_{RU,EN}_ORIGINAL.mp3 and their transcriptions
        ../voiceover/source/transcript_{ru,en}.json (faster-whisper, word timestamps).
Output: ../voiceover/{ru,en}/VO_{LANG}_{clip:02d}_{n}.wav  + vo_timing.json (with a fit check).
Lines are cut in the pauses between sentences, never inside a word; no speed change is applied.
"""
import json
import os
import sys
import wave

import numpy as np
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script_ep01 import CLIPS, VO_SOURCE, GAP  # noqa: E402

EP = os.path.join(HERE, '..')
SR = 48000


def load(lang):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(EP, VO_SOURCE[lang]), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def seg_bounds(segs, i):
    """Cut points: halfway into the pauses around segment i."""
    s, e = segs[i]['start'], segs[i]['end']
    prev_e = segs[i - 1]['end'] if i > 0 else 0.0
    next_s = segs[i + 1]['start'] if i + 1 < len(segs) else e + 0.6
    a = max(prev_e + (s - prev_e) * 0.5, s - 0.12) if i > 0 else 0.0
    b = min(e + (next_s - e) * 0.5, e + 0.20) if next_s > e else e + 0.02
    return a, b


def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    report = {}
    for lang in ('ru', 'en'):
        audio = load(lang)
        segs = json.load(open(os.path.join(EP, 'voiceover', 'source', f'transcript_{lang}.json')))
        os.makedirs(os.path.join(EP, 'voiceover', lang), exist_ok=True)
        for f in os.listdir(os.path.join(EP, 'voiceover', lang)):
            os.remove(os.path.join(EP, 'voiceover', lang, f))
        for c in CLIPS:
            for n, (st, src, text) in enumerate(c['vo'][lang], 1):
                if isinstance(src, tuple):
                    a, b = src
                else:
                    idx = src if isinstance(src, list) else [src]
                    a, b = seg_bounds(segs, idx[0])[0], seg_bounds(segs, idx[-1])[1]
                x = audio[int(a * SR):int(b * SR)].copy()
                f = int(0.012 * SR)
                x[:f] *= np.linspace(0, 1, f)
                x[-f:] *= np.linspace(1, 0, f)
                name = f"VO_{lang.upper()}_{c['id']:02d}_{n}.wav"
                write(os.path.join(EP, 'voiceover', lang, name), x)
                report[name] = dict(clip=c['name'], text=text, src=[round(a, 2), round(b, 2)], dur=round(len(x) / SR, 2))
    json.dump(report, open(os.path.join(EP, 'voiceover', 'vo_timing.json'), 'w'), ensure_ascii=False, indent=1)
    # fit: place lines exactly like assemble.py; extend a clip only if the narration needs it
    fitted = {}
    for c in CLIPS:
        need = 0.0
        for lang in ('ru', 'en'):
            prev = -GAP
            for n, (st, src, text) in enumerate(c['vo'][lang], 1):
                d = report[f"VO_{lang.upper()}_{c['id']:02d}_{n}.wav"]['dur']
                start = max(st if st is not None else 0.0, prev + GAP)
                prev = start + d
            need = max(need, prev + 0.35 if c['vo'][lang] else 0.0)
        fitted[c['id']] = round(max(c['dur'], need), 1)
    # CLIP_01A narration may run on into CLIP_01B (one continuous camera move)
    over = fitted[1] - CLIPS[0]['dur']
    if over > 0:
        fitted[1] = CLIPS[0]['dur']
        fitted[2] = round(max(CLIPS[1]['dur'], over + 0.4), 1)
    json.dump(fitted, open(os.path.join(HERE, 'clip_durations.json'), 'w'), indent=1)
    for c in CLIPS:
        flag = '' if fitted[c['id']] == c['dur'] else f'  (planned {c["dur"]})'
        print(f"{c['name']:30s} {fitted[c['id']]:5.1f}s{flag}")
    print('TOTAL', round(sum(fitted.values()), 1), 's')


if __name__ == '__main__':
    main()
