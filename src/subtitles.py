"""Отдельный слой субтитров: out/subtitles.srt (все реплики) и build/subtitles.ass (стилизованный, для вшивания)."""
import json
from .config import TRANSCRIPT, CUES, OUT, BUILD, W, H
from .cues import C


def lines():
    cfg = json.load(open(CUES, encoding="utf-8"))
    fixes = cfg.get("subtitle_fixes", {})
    out = []
    for s in json.load(open(TRANSCRIPT, encoding="utf-8")):
        txt = s["text"].strip()
        for a, b in fixes.items():
            txt = txt.replace(a, b)
        out.append([s["start"], s["end"], txt])
    # подрезаем «хвосты», чтобы строки не перекрывались, и даём минимум 1.0 c на чтение
    for i, l in enumerate(out):
        nxt = out[i + 1][0] if i + 1 < len(out) else l[1] + 2
        l[1] = min(max(l[1] + 0.25, l[0] + 1.0), nxt - 0.02)
    return out


def wrap(txt, n=48):
    if len(txt) <= n:
        return [txt]
    words, best = txt.split(), None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        sc = max(len(a), len(b))
        if best is None or sc < best[0]:
            best = (sc, [a, b])
    return best[1]


def ts_srt(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ts_ass(t):
    cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build():
    c = C()
    OUT.mkdir(exist_ok=True); BUILD.mkdir(exist_ok=True)
    L = lines()
    with open(OUT / "subtitles.srt", "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(L, 1):
            f.write(f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n" + "\n".join(wrap(t)) + "\n\n")
    radio = [(c["broadcast1"] - 0.1, c["silence"] - 0.1), (c["broadcast2"] - 0.1, c["broadcast2_end"] + 0.2)]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Inter SemiBold,50,&H00EEF2F5,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,0.5,0,1,2.6,1.2,2,160,160,62,204
Style: Radio,Inter SemiBold,50,&H0090D8FF,&H000000FF,&H00000000,&H96000000,0,1,0,0,100,100,0.5,0,1,2.6,1.2,2,160,160,62,204

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(BUILD / "subtitles.ass", "w", encoding="utf-8") as f:
        f.write(head)
        for a, b, t in L:
            if a >= c["final"] - 0.1:  # на финальном экране текст вариантов уже на экране
                continue
            st = "Radio" if any(x <= a + 0.2 < y for x, y in radio) else "Main"
            f.write(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},{st},,0,0,0,,{{\\fad(120,120)}}" + "\\N".join(wrap(t)) + "\n")
    return OUT / "subtitles.srt", BUILD / "subtitles.ass"


if __name__ == "__main__":
    print(build())
