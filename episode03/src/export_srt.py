"""Write output/subtitles_<lang>.srt from the same chunks burned into the video."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import render

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

for lang in sys.argv[1:] or ["en", "ru"]:
    timing = render.load_timing(lang)
    subs = render.build_subs(timing, lang)
    d3 = next(l for l in timing if l["id"] == "d3")  # final question shown as title; still in SRT
    subs.append(dict(s=d3["words"][0]["s"] - 0.05, e=d3["words"][-1]["e"] + 1.2, words=[(d3["text"], False)]))
    with open(os.path.join(render.ROOT, "output", f"subtitles_{lang}.srt"), "w") as f:
        for i, c in enumerate(subs, 1):
            f.write(f"{i}\n{ts(max(0, c['s']))} --> {ts(c['e'])}\n{' '.join(w for w, k in c['words'])}\n\n")
    print("srt", lang, len(subs))
