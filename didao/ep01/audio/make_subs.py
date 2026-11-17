"""Build subtitles (SRT) from the voice-over word timings. VO is placed at +2.0 s in the film."""
import json, os, re
OFF = 2.0; here = os.path.dirname(os.path.abspath(__file__))
FIX = {'немощного': 'ни мощного', 'станусь': 'останусь', 'заработанок': 'заработанных', '«Искусственного': 'искусственного', 'интеллекта»': 'интеллекта', 'немощного компьютера,': 'ни мощного компьютера,'}
words = []
for s in json.load(open(os.path.join(here, 'vo_transcript.json'))):
    for w in s['words']:
        t = w['w'].strip().replace('«', '').replace('»', ''); base = re.sub(r'[,.?!»]+$', '', t); tail = t[len(base):]
        if base in FIX: t = FIX[base] + tail.replace('»', '')
        if t.startswith('-') and words: words[-1][0] += t; words[-1][2] = w['e'] + OFF; continue
        words.append([t, w['s'] + OFF, w['e'] + OFF])
cues, cur = [], []
for i, w in enumerate(words):
    cur.append(w); txt = ' '.join(x[0] for x in cur)
    nxt_gap = words[i + 1][1] - w[2] if i + 1 < len(words) else 9
    if (txt[-1] in '.?!' and len(txt) > 18) or len(txt) > 58 or nxt_gap > 0.45 or (txt[-1] == ',' and len(txt) > 34):
        cues.append(cur); cur = []
if cur: cues.append(cur)
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h:02}:{m:02}:{s:06.3f}'.replace('.', ',')
out = []; out_prev_end = ['.']
for i, c in enumerate(cues):
    txt = ' '.join(x[0] for x in c)
    if i == 0 or out_prev_end[0] in '.?!': txt = txt[0].upper() + txt[1:]
    out_prev_end[0] = txt[-1]
    if len(txt) > 40:  # balance into 2 lines
        ws = txt.split(' '); best = min(range(1, len(ws)), key=lambda k: abs(len(' '.join(ws[:k])) - len(' '.join(ws[k:])))); txt = ' '.join(ws[:best]) + '\n' + ' '.join(ws[best:])
    end = min(c[-1][2] + 0.35, cues[i + 1][0][1] - 0.05) if i + 1 < len(cues) else c[-1][2] + 0.6
    out.append(f'{i + 1}\n{ts(c[0][1])} --> {ts(end)}\n{txt}\n')
open(os.path.join(here, '..', 'output', 'DIDAO_E01_subtitles_ru.srt'), 'w').write('\n'.join(out)); print(len(out), 'cues')
