"""Cue sheet per language (seconds in the voice-over file, taken from word-level alignment)."""
import json
import os

VO_OFF = 0.5          # voice starts 0.5 s into the film
END_HOLD = 6.0        # question card after the voice ends

CUES = {
    "ru": dict(intro=0.0, evening=4.44, door_notice=6.46, never_before=10.18, blue_light=13.10, open_door=15.76,
               same_room=19.66, same_items=21.36, steps=25.88, noise=27.88, distort=30.30, flash_fall=32.48,
               eyes_open=35.52, leave_room=38.34, photos=41.54, objects=43.40, parents=46.26, parents_look=49.82,
               run_out=54.00, city=55.30, numbers=59.48, buildings=61.06, phone_photos=64.22, missing=67.00,
               message=69.30, read=73.96, msg_text=76.20, voice=79.98, turn=82.72, double_stand=84.26,
               same_hair=88.74, says=92.24, double_line=95.06, realize=99.08, maybe1=100.78, maybe2=103.84,
               real_one=107.32, important=109.34, end_vo=114.34),
    "en": dict(intro=0.0, evening=3.58, door_notice=5.82, never_before=9.32, blue_light=12.02, open_door=14.58,
               same_room=17.58, same_items=19.78, steps=24.94, noise=26.82, distort=29.44, flash_fall=31.98,
               eyes_open=35.06, leave_room=37.94, photos=41.34, objects=43.38, parents=45.92, parents_look=49.02,
               run_out=52.02, city=53.46, numbers=56.52, buildings=57.86, phone_photos=61.20, missing=63.66,
               message=66.20, read=70.60, msg_text=72.16, voice=75.06, turn=77.66, double_stand=79.58,
               same_hair=83.12, says=85.98, double_line=88.78, realize=92.00, maybe1=93.84, maybe2=96.62,
               real_one=99.60, important=101.76, end_vo=105.32),
}

QUESTION = {
    "ru": "Ты бы вернулся в свой мир или остался здесь?",
    "en": "Would you return to your world or stay here?",
}
TITLE = {
    "ru": ("А ЧТО, ЕСЛИ ТЫ ПОПАДЁШЬ", "В ПАРАЛЛЕЛЬНУЮ ВСЕЛЕННУЮ?"),
    "en": ("WHAT IF YOU ENTERED", "A PARALLEL UNIVERSE?"),
}

FIX = {
    "ru": [("споддвери", "из-под двери"), ("произносит.", "произносит:"),
           ("Не пытайся", "«Не пытайся"), ("есть ты.", "есть ты»."), ("Ты наконец-то", "«Ты наконец-то"),
           ("отправитель, твой", "отправитель — твой"), ("очередь вернуться домой.", "очередь вернуться домой»."),
           ("попытался бы вернуться домой.", "попытался бы вернуться домой?")],
    "en": [("and says,", "and says:"), ("Don't try", "“Don't try"), ("a you here.", "a you here.”"),
           ("You're finally", "“You're finally"), ("go home.", "go home.”"), ("read,", "read:"),
           ("realize,", "realize:")],
}


def cues(lang):
    return {k: v + VO_OFF for k, v in CUES[lang].items()}


def duration(lang):
    return CUES[lang]["end_vo"] + VO_OFF + END_HOLD


def subtitles(lang, max_chars=44):
    """chunk whisper words into short on-screen captions -> [(start, end, text, style)]"""
    here = os.path.dirname(os.path.abspath(__file__))
    segs = json.load(open(os.path.join(here, "..", "data", f"{lang}.json")))
    cq = cues(lang)
    out = []

    def emit(ws):
        out.append([ws[0]["s"] + VO_OFF, ws[-1]["e"] + VO_OFF, "".join(x["w"] for x in ws).strip()])

    def split(ws):
        txt = "".join(x["w"] for x in ws).strip()
        if len(txt) <= max_chars or len(ws) < 3:
            emit(ws)
            return
        # best break: near the middle, prefer after punctuation
        best, bi = 1e9, 1
        acc = 0
        for i in range(1, len(ws)):
            acc += len(ws[i - 1]["w"])
            score = abs(acc - len(txt) / 2)
            if ws[i - 1]["w"].strip().endswith((",", ".", "—", ":")):
                score -= 8
            if score < best:
                best, bi = score, i
        split(ws[:bi])
        split(ws[bi:])

    for s in segs:
        split(s["words"])
    # timing: hold each caption until the next one (max +0.6 s)
    res = []
    for i, (a, b, txt) in enumerate(out):
        nb = out[i + 1][0] if i + 1 < len(out) else b + 1.0
        e = min(nb - 0.02, b + 0.6)
        if lang == "ru" and "вернуться домой" in txt and a > cq["double_line"] - 1 and a < cq["realize"]:
            pass
        for o, n in FIX[lang]:
            if o in txt:
                txt = txt.replace(o, n)
        style = "quote" if (cq["msg_text"] - 0.3 <= a < cq["voice"] - 0.3) or (cq["double_line"] - 0.3 <= a < cq["realize"] - 0.3) else "normal"
        res.append((a, e, txt.strip(), style))
    return res


def srt(lang, path):
    def ts(x):
        h = int(x // 3600)
        m = int(x % 3600 // 60)
        s = x % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    subs = subtitles(lang)
    lines = []
    for i, (a, b, txt, _) in enumerate(subs, 1):
        lines += [str(i), f"{ts(a)} --> {ts(b)}", txt, ""]
    d = duration(lang)
    lines += [str(len(subs) + 1), f"{ts(d - END_HOLD + 0.6)} --> {ts(d - 0.2)}", QUESTION[lang], ""]
    open(path, "w", encoding="utf-8").write("\n".join(lines))
