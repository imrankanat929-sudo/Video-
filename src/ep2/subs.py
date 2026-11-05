"""Субтитры 9:16: крупный шрифт, над интерфейсом TikTok/Shorts. Скрываются, когда тот же текст уже на экране."""
from ..config import OUT, BUILD, W, H, LANG
from ..cues import C
from .. import subtitles as SUB


def build():
    c = C()
    OUT.mkdir(parents=True, exist_ok=True); BUILD.mkdir(parents=True, exist_ok=True)
    L = SUB.lines()
    with open(OUT / "subtitles.srt", "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(L, 1):
            f.write(f"{i}\n{SUB.ts_srt(a)} --> {SUB.ts_srt(b)}\n" + "\n".join(SUB.wrap(t, 30)) + "\n\n")
    hide = [(c["three"] + 1.0, c["stop"]), (c["wrong"] - 0.1, c["head_up"]), (c["two_opts"] - 0.1, 1e9)]
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: {0 if LANG == "en" else 2}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Inter ExtraBold,66,&H00F4F6FA,&H000000FF,&H00000000,&H9A000000,0,0,0,0,100,100,0,0,1,4.2,1.6,2,80,80,520,204
"""
    with open(BUILD / "subtitles.ass", "w", encoding="utf-8") as f:
        f.write(head + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a, b, t in L:
            if any(x <= a + 0.1 < y for x, y in hide):
                continue
            f.write(f"Dialogue: 0,{SUB.ts_ass(a)},{SUB.ts_ass(b)},Main,,0,0,0,,{{\\fad(90,90)}}" +
                    "\\N".join(SUB.wrap(t, 26 if LANG == "en" else 24)) + "\n")
    return OUT / "subtitles.srt", BUILD / "subtitles.ass"


if __name__ == "__main__":
    print(build())
