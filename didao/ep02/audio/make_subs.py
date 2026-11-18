"""Big Shorts-style subtitles from VO word timings, remapped through the pause-tightening cuts."""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__)); lang = sys.argv[1]
TM = json.load(open(os.path.join(here, 'timing.json')))[lang]; LEAD = TM['lead']
cuts = json.load(open(os.path.join(here, f'vo_{lang}_map.json')))['cuts']
def m(t):
    r = t
    for c0, c1 in cuts:
        if t >= c1: r -= c1 - c0
        elif t > c0: r -= t - c0
    return r + LEAD
FIX = {'игре.': 'игры.', 'произойдет,': 'произойдёт,', 'ещё': 'ещё'}
words = []
for s in json.load(open(os.path.join(here, f'vo_{lang}_transcript.json'))):
    for w in s['words']:
        t = w['w'].strip()
        if (t[:1] in ',.-') and words: words[-1][0] += t; words[-1][2] = m(w['e']); continue
        words.append([FIX.get(t, t), m(w['s']), m(w['e'])])
if lang == 'ru' and words[-1][0].endswith('.'): words[-1][0] = words[-1][0][:-1] + '?'
cues, cur = [], []
for i, w in enumerate(words):
    cur.append(w); txt = ' '.join(x[0] for x in cur)
    gap = words[i + 1][1] - w[2] if i + 1 < len(words) else 9
    if txt[-1] in '.?!' or len(txt) > 28 or gap > 0.25 or (txt[-1] in ',—' and len(txt) > 12): cues.append(cur); cur = []
if cur: cues.append(cur)
def ts(x): return f'{int(x // 3600):02}:{int(x % 3600 // 60):02}:{x % 60:06.3f}'.replace('.', ',')
out = []
for i, c in enumerate(cues):
    txt = ' '.join(x[0] for x in c)
    if len(txt) > 17:
        ws = txt.split(' '); b = min(range(1, len(ws)), key=lambda k: abs(len(' '.join(ws[:k])) - len(' '.join(ws[k:])))); txt = ' '.join(ws[:b]) + '\n' + ' '.join(ws[b:])
    end = min(c[-1][2] + 0.25, cues[i + 1][0][1] - 0.03) if i + 1 < len(cues) else c[-1][2] + 0.5
    out.append(f'{i + 1}\n{ts(c[0][1])} --> {ts(end)}\n{txt}\n')
name = {'ru': 'GTA6_VYSHLA_RU', 'en': 'GTA6_IS_HERE_EN'}[lang]
open(os.path.join(here, '..', f'output_{lang}', f'{name}_subtitles.srt'), 'w').write('\n'.join(out)); print(lang, len(out), 'cues')
