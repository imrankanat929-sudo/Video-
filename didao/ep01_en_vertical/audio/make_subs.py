"""English subtitles for the vertical cut, from the TTS word timings (short Shorts-style captions)."""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
words = []
for s in json.load(open(os.path.join(here, 'vo_en_transcript.json'))):
    for w in s['words']:
        t = w['w'].strip()
        if t[:1] in ',.' and words: words[-1][0] += t; words[-1][2] = w['e']; continue
        words.append([t, w['s'], w['e']])
cues, cur = [], []
for i, w in enumerate(words):
    cur.append(w); txt = ' '.join(x[0] for x in cur)
    gap = words[i + 1][1] - w[2] if i + 1 < len(words) else 9
    if txt[-1] in '.?!' or len(txt) > 34 or gap > 0.4 or (txt[-1] == ',' and len(txt) > 14): cues.append(cur); cur = []
if cur: cues.append(cur)
def ts(x): return f'{int(x // 3600):02}:{int(x % 3600 // 60):02}:{x % 60:06.3f}'.replace('.', ',')
out = []
for i, c in enumerate(cues):
    txt = ' '.join(x[0] for x in c)
    if len(txt) > 20:
        ws = txt.split(' '); b = min(range(1, len(ws)), key=lambda k: abs(len(' '.join(ws[:k])) - len(' '.join(ws[k:])))); txt = ' '.join(ws[:b]) + '\n' + ' '.join(ws[b:])
    end = min(c[-1][2] + 0.3, cues[i + 1][0][1] - 0.04) if i + 1 < len(cues) else c[-1][2] + 0.6
    out.append(f'{i + 1}\n{ts(c[0][1])} --> {ts(end)}\n{txt}\n')
open(os.path.join(here, '..', 'output', 'ONE_DAY_BEFORE_GTA6_EN_subtitles.srt'), 'w').write('\n'.join(out)); print(len(out), 'cues')
