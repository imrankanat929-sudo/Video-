"""Build SRT + ASS subtitles for one language. usage: python3 subs.py ru|en"""
import sys, json
lang = sys.argv[1]
tm = json.load(open(f'timing_{lang}_full.json'))
MAXC = 44

def split(a, b, s):
    if len(s) <= MAXC:
        return [(a, b, s)]
    mid = len(s) / 2
    cands = [i for i, ch in enumerate(s) if ch in ',.:;—?!' and 8 < i < len(s) - 8]
    if not cands:
        cands = [i for i, ch in enumerate(s) if ch == ' ']
    i = min(cands, key=lambda i: abs(i - mid))
    s1, s2 = s[:i + 1].strip(), s[i + 1:].strip()
    tb = a + (b - a) * len(s1) / (len(s1) + len(s2))
    return split(a, tb, s1) + split(tb, b, s2)

out = []
for a, b, s in tm['subs']:
    out += split(a, b + 0.25, s)
# no overlaps
for i in range(len(out) - 1):
    if out[i][1] > out[i + 1][0]:
        out[i] = (out[i][0], out[i + 1][0] - 0.02, out[i][2])

def ts(t, sep=','):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', sep)

with open(f'../{lang.upper()}_VERSION/subtitles_{lang}.srt', 'w') as f:
    for i, (a, b, s) in enumerate(out):
        f.write(f'{i+1}\n{ts(a)} --> {ts(b)}\n{s}\n\n')

def ats(t):
    return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'

with open(f'subtitles_{lang}.ass', 'w') as f:
    f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Roboto Condensed,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,390,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
    for a, b, s in out:
        f.write(f'Dialogue: 0,{ats(a)},{ats(b)},Main,,0,0,0,,{{\\fad(120,120)}}{s}\n')
print(len(out), 'subtitle lines')
