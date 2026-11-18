"""Tighten the ElevenLabs voice-over: every pause longer than MAXGAP between words is shortened
to MAXGAP by cutting the middle of the silence (speech itself untouched).
Writes vo_<lang>_tight.wav and vo_<lang>_map.json (original time -> new time) used for picture/subtitle sync."""
import json, os, sys, subprocess, numpy as np, soundfile as sf
here = os.path.dirname(os.path.abspath(__file__)); lang = sys.argv[1]; MAXGAP = 0.30; SR = 44100
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(here, '..', 'assets', f'voiceover_{lang}.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.float32).copy()
words = [(w['s'], w['e']) for s in json.load(open(os.path.join(here, f'vo_{lang}_transcript.json'))) for w in s['words']]
cuts = []  # (start, end) of removed audio, original seconds
for (s0, e0), (s1, e1) in zip(words, words[1:]):
    gap = s1 - e0
    if gap > MAXGAP + 0.05:
        mid = (e0 + s1) / 2; rem = gap - MAXGAP; cuts.append((mid - rem / 2, mid + rem / 2))
parts, last = [], 0
fade = int(0.01 * SR)
for c0, c1 in cuts:
    seg = a[int(last * SR): int(c0 * SR)].copy()
    if len(seg) > 2 * fade: seg[-fade:] *= np.linspace(1, 0, fade); seg[:fade] *= np.linspace(0, 1, fade) if last else 1
    parts.append(seg); last = c1
parts.append(a[int(last * SR):]); out = np.concatenate(parts)
nz = np.where(np.abs(out) > 0.01)[0]; out = out[: nz[-1] + int(0.4 * SR)]
sf.write(os.path.join(here, f'vo_{lang}_tight.wav'), out, SR)
json.dump({'cuts': cuts}, open(os.path.join(here, f'vo_{lang}_map.json'), 'w'))
print(lang, 'removed', round(sum(c1 - c0 for c0, c1 in cuts), 2), 's ->', round(len(out) / SR, 2), 's')
