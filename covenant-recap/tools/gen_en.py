exec(open("gen.py").read().split("# phrase timings")[0])  # helpers, KW lists
src = open("gen.py").read()
ns = {}
exec(src, ns)  # regenerates RU outputs (unchanged) and gives us SC/SH/write_ass/etc.
g = ns
KE = 1.025
segs = json.load(open("tr_en.json"))
phr = [{"start": s["words"][0][0]/KE, "end": s["words"][-1][1]/KE, "text": s["text"].strip(),
        "words": [[a/KE, b/KE, x.strip()] for a, b, x in s["words"]]} for s in segs]
ch = []
for p in phr:
    for c in g["chunk_words"](p["words"], 26):
        ch.append([c[0][0], c[-1][1], " ".join(x[2] for x in c)])
ch = g["fix_gaps"](ch)
g["srt"](ch, f"{OUT}/subtitles/covenant_en.srt")
SCE = [0.0, 5.8, 15.1, 22.9, 28.6, 37.6, 47.6, 54.9, 60.0]
SC_ru = g["SC"]
SC_en = [(SCE[i], SCE[i+1], n, r) for i, (_, _, n, r) in enumerate(SC_ru)]
def m(t, sc):
    a, b = SC_ru[sc-1][:2]; A, B = SC_en[sc-1][:2]
    return A + (t - a) * (B - A) / (b - a)
SH_en = [(round(m(s, sc), 2), round(m(e, sc), 2), sc, d) for s, e, sc, d in g["SH"]]
SH_en[-1] = (59.0, 60.0, 8, SH_en[-1][3]); SH_en[-2] = (SH_en[-2][0], 59.0, 8, SH_en[-2][3])
g["SC"][:] = SC_en; g["SH"][:] = SH_en
g["write_ass"]("en", ch, g["KW_EN"] + ["trapped", "lines,", "injured", "save", "abandon", "documents", "America",
               "decision", "evacuation", "enemies", "impossible", "lost", "Afghanistan", "keeps"], f"{OUT}/subtitles/covenant_en_styled.ass")
def f(t): mm, s = divmod(t, 60); return f"{int(mm):02}:{s:05.2f}"
open(f"{OUT}/vo_script_en.txt", "w").write("\n".join(f"[{f(p['start'])}] {p['text']}" for p in phr) + "\n")
json.dump({"scenes": SC_en, "shots": SH_en}, open("plan_en.json", "w"), ensure_ascii=False, indent=1)
for p in phr: print(f"{p['start']:5.2f}-{p['end']:5.2f} {p['text']}")
