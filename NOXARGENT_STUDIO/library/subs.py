"""Распознавание озвучки (faster-whisper, пословно) и субтитры (.srt + .ass для вшивания).

Стиль: Montserrat SemiBold, белые, тонкая тёмная обводка, снизу по центру, макс. 2 строки, без караоке.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

LINE = 42  # символов в строке


def transcribe(audio, out_json, model="medium"):
    out_json = Path(out_json)
    if out_json.exists():
        return json.loads(out_json.read_text(encoding="utf-8"))
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(audio), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(a, language="ru", vad_filter=True, word_timestamps=True)
    js = [dict(start=s.start, end=s.end, text=s.text.strip(), words=[(w.start, w.end, w.word) for w in s.words]) for s in segs]
    out_json.write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    return js


def words(segments):
    return [(a, b, w.strip()) for s in segments for (a, b, w) in s["words"]]


def word_time(segments, prefix, after=0.0, end=False):
    """Время начала (или конца) первого слова, начинающегося с prefix, после момента after."""
    p = prefix.lower()
    for a, b, w in words(segments):
        if a >= after and w.lower().strip("«»\".,!?:;—-").startswith(p):
            return b if end else a
    raise KeyError(f"слово «{prefix}» после {after:.1f} с не найдено")


def phrase_gap(segments, t):
    """Ближайшая пауза между фразами к моменту t (середина паузы)."""
    best = None
    for s1, s2 in zip(segments, segments[1:]):
        m = (s1["end"] + s2["start"]) / 2
        if best is None or abs(m - t) < abs(best - t):
            best = m
    return best


def events(segments, fixes=None, max_chars=LINE * 2):
    """Субтитры по пословным таймкодам: фраза до 2 строк, разрез по концу предложения."""
    fixes = fixes or {}
    out, cur, cs, ce = [], [], None, None
    for a, b, w in words(segments):
        if cs is None:
            cs = a
        if cur and len(" ".join(cur + [w])) > max_chars:
            out.append([cs, ce, " ".join(cur)])
            cur, cs = [], a
        cur.append(w)
        ce = b
        if w.endswith((".", "?", "!", "»", "…")) and len(" ".join(cur)) > 18:
            out.append([cs, ce, " ".join(cur)])
            cur, cs = [], None
    if cur:
        out.append([cs, ce, " ".join(cur)])
    for e in out:
        e[2] = e[2].replace(" -то", "-то").replace(" -нибудь", "-нибудь").replace(" -либо", "-либо")
        for k, v in fixes.items():
            e[2] = e[2].replace(k, v)
        e[1] = max(e[1] + 0.25, e[0] + 1.0)  # минимум 1 с на экране
    for a, b in zip(out, out[1:]):
        a[1] = min(a[1], b[0] - 0.02)
    return out


def two_lines(text, n=LINE):
    if len(text) <= n:
        return [text]
    words_ = text.split()
    best, bi = None, 1
    for i in range(1, len(words_)):
        l1, l2 = " ".join(words_[:i]), " ".join(words_[i:])
        score = max(len(l1), len(l2))
        if best is None or score < best:
            best, bi = score, i
    return [" ".join(words_[:bi]), " ".join(words_[bi:])]


def _ts(t, ass=False):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    if ass:
        return f"{h}:{m:02d}:{s:05.2f}"
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"


def write_srt(evts, path):
    with open(path, "w", encoding="utf-8") as fh:
        for i, (a, b, txt) in enumerate(evts, 1):
            fh.write(f"{i}\n{_ts(a)} --> {_ts(b)}\n" + "\n".join(two_lines(txt)) + "\n\n")


def write_ass(evts, path, res=(1920, 1080), size=46, margin_v=56, line=LINE, outline=1.6, margin_lr=120):
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {res[0]}\nPlayResY: {res[1]}\nWrapStyle: 2\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"Style: Sub,Montserrat SemiBold,{size},&H00FFFFFF,&H000000FF,&H00141414,&H00000000,0,0,0,0,100,100,0,0,1,{outline},0,2,{margin_lr},{margin_lr},{margin_v},1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(head)
        for a, b, txt in evts:
            body = "\\N".join(two_lines(txt, line))
            fh.write(f"Dialogue: 0,{_ts(a, True)},{_ts(b, True)},Sub,,0,0,0,,{body}\n")
