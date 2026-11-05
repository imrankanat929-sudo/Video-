"""Синхронизация сцен с озвучкой: якорные фразы -> секунды по transcript.json."""
import json, re, subprocess
from functools import lru_cache
from .config import TRANSCRIPT, CUES, VOICE

def norm(s):
    s = s.lower().replace("ё", "е")
    return re.sub(r"[^\w]+", "", s)

def voice_duration():
    out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(VOICE)], capture_output=True, text=True).stdout
    return float(out.strip())

@lru_cache(None)
def load():
    cfg = json.load(open(CUES, encoding="utf-8"))
    words = []
    if TRANSCRIPT.exists():
        for seg in json.load(open(TRANSCRIPT, encoding="utf-8")):
            for w in seg["words"]:
                n = norm(w["w"])
                if n:
                    words.append((n, w["s"], w["e"]))
    cues, pos, report = {}, 0, []
    for name, phrase, at, fb in cfg["cues"]:
        toks = [norm(t) for t in phrase.split() if norm(t)]
        hit = None
        for i in range(pos, len(words) - len(toks) + 1):
            if all(words[i + k][0].startswith(toks[k]) or toks[k].startswith(words[i + k][0]) and len(words[i+k][0]) > 2
                   for k in range(len(toks))):
                hit = i
                break
        if hit is None:
            cues[name] = float(fb); report.append(f"{name:16s} {fb:7.2f}  (fallback!)")
        else:
            t = words[hit][1] if at == "start" else words[hit + len(toks) - 1][2]
            cues[name] = float(t); pos = hit + 1
            report.append(f"{name:16s} {t:7.2f}  '{phrase}'")
    vo = voice_duration()
    cues["vo_end"] = vo
    cues["END"] = vo + cfg.get("final_hold_seconds", 25.0)
    return cues, cfg, "\n".join(report)

def C():
    return load()[0]

if __name__ == "__main__":
    print(load()[2]); print("END", C()["END"])
