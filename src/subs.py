"""Build SRT subtitles (deliverables) and styled ASS captions (burned into the MP4s)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline  # noqa: E402

OUT = os.path.join(timeline.ROOT, 'output')
BUILD = os.path.join(timeline.ROOT, 'build')

CHAPTER_LABELS = {
    'ru': [(0.0, 'ТРОПА'), (24.6, 'ВСТРЕЧА'), (49.6, 'ПРАВИЛА'), (76.0, 'ВЫПАД'), (107.4, 'ФИНАЛ')],
    'en': [(0.0, 'THE TRAIL'), (24.6, 'ENCOUNTER'), (49.6, 'THE RULES'), (76.0, 'THE CHARGE'), (107.4, 'FINAL')],
}
END_TEXT = {
    'ru': ('ТЫ БЫ СМОГ\\N{\\c&H00D4FF&}СОХРАНИТЬ\\NСПОКОЙСТВИЕ?', 'НАПИШИ СВОЙ ОТВЕТ В КОММЕНТАРИЯХ'),
    'en': ('COULD YOU\\N{\\c&H00D4FF&}STAY CALM?', 'WRITE YOUR ANSWER IN THE COMMENTS'),
}


def tokens_with_times(g):
    """Align proof-read text tokens to whisper word timings (by index, proportional when counts differ)."""
    toks = g['text'].split()
    ws = g['words']
    n, m = len(toks), len(ws)
    out = []
    for i, tk in enumerate(toks):
        j = min(m - 1, int(round(i * (m - 1) / max(1, n - 1)))) if n != m else i
        out.append((tk, ws[j][1], ws[j][2]))
    # make monotonic
    for i in range(1, len(out)):
        if out[i][1] < out[i - 1][1]:
            out[i] = (out[i][0], out[i - 1][1], max(out[i][2], out[i - 1][1]))
    return out


def fmt_srt(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def fmt_ass(t):
    cs = int(round(t * 100))
    return f'{cs // 360000:d}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}'


def balance(txt, max_line=38):
    if len(txt) <= max_line:
        return txt
    words = txt.split()
    best, bi = 1e9, 1
    for i in range(1, len(words)):
        l1, l2 = ' '.join(words[:i]), ' '.join(words[i:])
        score = max(len(l1), len(l2)) + (0 if re.search(r'[,.?!:—]$', words[i - 1]) else 4)
        if score < best:
            best, bi = score, i
    return ' '.join(words[:bi]) + '\n' + ' '.join(words[bi:])


def build_cues(lang, max_line=38):
    cues = []
    for g in timeline.placed(lang):
        toks = tokens_with_times(g)
        cur = []
        for i, (tk, s, e) in enumerate(toks):
            cand = ' '.join([x[0] for x in cur] + [tk])
            if cur and len(cand) > max_line * 2 - 4:
                cues.append(cur)
                cur = []
            cur.append((tk, s, e))
            last = i == len(toks) - 1
            L = len(' '.join(x[0] for x in cur))
            if not last and (re.search(r'[.?!]$', tk) and L > 24 or re.search(r'[,]$', tk) and L > 40):
                cues.append(cur)
                cur = []
        if cur:
            cues.append(cur)
    out = []
    for c in cues:
        out.append([c[0][1], c[-1][2] + 0.3, balance(' '.join(x[0] for x in c), max_line)])
    for i in range(len(out) - 1):
        out[i][1] = min(out[i][1], out[i + 1][0] - 0.04)
    for c in out:
        c[1] = max(c[1], c[0] + 0.8)
    return out


def write_srt(lang):
    cues = build_cues(lang)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f'bear_subtitles_{lang}.srt')
    with open(path, 'w', encoding='utf-8') as f:
        for i, (s, e, txt) in enumerate(cues, 1):
            f.write(f'{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{txt}\n\n')
    return path, cues


ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display Black,82,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,1,0,1,7,3,5,40,40,0,1
Style: Tag,Inter Display Black,38,&H00FFFFFF,&H00FFFFFF,&H003539E5,&H003539E5,-1,0,0,0,100,100,2,0,3,10,0,5,40,40,0,1
Style: Chap,Inter Display Black,28,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,3,0,1,3,0,5,40,40,0,1
Style: End,Inter Display Black,104,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,1,0,1,8,4,5,60,60,0,1
Style: EndSub,Inter Display Black,40,&H00FFFFFF,&H00FFFFFF,&H003539E5,&H003539E5,-1,0,0,0,100,100,2,0,3,14,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

CAP_Y = 1505
TAG_Y = 1405


def caption_chunks(g, lang, max_chars=17, max_words=3):
    toks = tokens_with_times(g)
    chunks, cur = [], []
    for tk, s, e in toks:
        cand = ' '.join([x[0] for x in cur] + [tk])
        if cur and (len(cand) > max_chars or len(cur) >= max_words or re.search(r'[.?!,:—]$', cur[-1][0])):
            chunks.append(cur)
            cur = []
        cur.append((tk, s, e))
    if cur:
        chunks.append(cur)
    return chunks


def hl(word, lang):
    w = word.lower()
    return any(w.startswith(k) or k in w for k in timeline.HILITE[lang]) if len(w) > 2 else False


def write_ass(lang):
    P = timeline.placed(lang)
    ev = []
    for gi, g in enumerate(P):
        if g['id'] == 'final':
            continue  # the end card shows the question in large type
        chunks = caption_chunks(g, lang)
        g_end = P[gi + 1]['dst_start'] - 0.05 if gi + 1 < len(P) else 120
        # tag pill for the group
        tag_end = min(g_end, chunks[-1][-1][2] + 0.35)
        ev.append(('1', g['dst_start'], tag_end, 'Tag',
                   f"{{\\pos(540,{TAG_Y})\\fad(120,120)\\t(0,140,\\fscx100\\fscy100)\\fscx70\\fscy70}}{g['tag']}"))
        for ci, ch in enumerate(chunks):
            s = ch[0][1] - 0.05
            e = chunks[ci + 1][0][1] - 0.06 if ci + 1 < len(chunks) else min(g_end, ch[-1][2] + 0.35)
            words = []
            for tk, ws, we in ch:
                t = tk.upper()
                if hl(tk, lang):
                    words.append(f'{{\\c&H00D4FF&}}{t}{{\\c&HFFFFFF&}}')
                else:
                    words.append(t)
            txt = ' '.join(words)
            ev.append(('2', s, e, 'Cap', f"{{\\pos(540,{CAP_Y})\\fscx82\\fscy82\\t(0,110,\\fscx104\\fscy104)\\t(110,190,\\fscx100\\fscy100)}}{txt}"))
    # chapter labels under the progress dots
    labels = CHAPTER_LABELS[lang]
    for i, (t0, lab) in enumerate(labels):
        t1 = labels[i + 1][0] if i + 1 < len(labels) else 120
        ev.append(('3', t0 + 0.05, t1, 'Chap', f"{{\\pos(540,168)\\fad(200,150)}}{lab}"))
    # end card
    big, small = END_TEXT[lang]
    ev.append(('4', 109.0, 120.0, 'End', f"{{\\pos(540,820)\\fad(350,0)\\fscx70\\fscy70\\t(0,320,\\fscx104\\fscy104)\\t(320,460,\\fscx100\\fscy100)}}{big}"))
    ev.append(('4', 110.2, 120.0, 'EndSub', f"{{\\pos(540,1140)\\fad(300,0)}}{small}"))
    path = os.path.join(BUILD, f'captions_{lang}.ass')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(ASS_HEAD)
        for layer, s, e, st, txt in ev:
            f.write(f'Dialogue: {layer},{fmt_ass(max(0, s))},{fmt_ass(e)},{st},,0,0,0,,{txt}\n')
    return path


if __name__ == '__main__':
    for lang in ('ru', 'en'):
        p, cues = write_srt(lang)
        a = write_ass(lang)
        print(p, len(cues), 'cues;', a)
        for g in timeline.placed(lang):
            nt, nw = len(g['text'].split()), len(g['words'])
            if nt != nw:
                print('  token mismatch', lang, g['id'], nt, nw)
