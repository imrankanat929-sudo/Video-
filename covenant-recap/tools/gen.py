import json, re
OUT = "/home/user/Video-/covenant-recap"
K = 1.08  # VO tempo factor (63.9s -> 60s)
segs = json.load(open("tr.json"))

EN = [
    "An American soldier is stranded deep in enemy territory.",
    "His unit is wiped out, and he is badly wounded.",
    "But the most incredible part: he will be saved by a man he barely knows.",
    "John Kinley serves in Afghanistan alongside his interpreter, Ahmed.",
    "During a dangerous operation, their unit is ambushed.",
    "John and Ahmed are the only survivors.",
    "Ahmed refuses to leave him, and for days carries the wounded soldier across the mountains,",
    "until he finally reaches an American base.",
    "John returns home, but learns that Ahmed and his family are still in danger.",
    "The visas they were promised never came through.",
    "So John decides to go back to Afghanistan and save his friend.",
    "Together with Ahmed's family, they try to reach the extraction point.",
    "The enemy closes in, and there seems to be no way out.",
    "Just when hope is almost gone, help arrives.",
    "John keeps his promise and saves the man who once saved him.",
]
KW_RU = ["вражеской", "территории", "уничтожен", "тяжело", "ранен", "невероятное", "спасёт", "Джон", "Кинли",
         "Ахмедом", "Ахмед", "Ахмеда", "засаду", "единственным", "выжившим", "не бросает", "горы", "базы",
         "опасности", "документы", "Америку", "вернуться", "друга", "эвакуации", "окружают", "безвыходной",
         "помощь", "обещание", "спас"]
KW_EN = ["enemy", "territory", "wiped", "wounded", "incredible", "saved", "John", "Kinley", "Ahmed",
         "Ahmed's", "ambushed", "only", "survivors", "refuses", "mountains", "base", "danger", "visas",
         "back", "friend", "extraction", "closes", "way", "out", "help", "arrives", "promise", "saves"]

def ts(t, sep=","):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"
def ass_t(t):
    cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

# phrase timings on the 60s scale
phr = []
for i, s in enumerate(segs):
    w = [[a / K, b / K, x.strip()] for a, b, x in s["words"]]
    phr.append({"start": w[0][0], "end": w[-1][1], "words": w, "ru": s["text"].strip(), "en": EN[i]})

def chunk_words(words, maxc=24):
    out, cur = [], []
    for wd in words:
        txt = " ".join(x[2] for x in cur + [wd])
        if cur and (len(txt) > maxc or cur[-1][2].endswith(".")):
            out.append(cur); cur = []
        cur.append(wd)
    if cur: out.append(cur)
    for i in range(len(out) - 1):  # move dangling short words (а, и, в...) to the next line
        while len(out[i]) > 1 and (len(out[i][-1][2]) <= 2 or out[i][-1][2].lower() in ("and","the","his","but","who","that","with")) and out[i][-1][2].isalpha():
            out[i + 1].insert(0, out[i].pop())
    # don't leave a lone short word (e.g. "в", "и") hanging at a chunk end
    return out

ru_chunks = []
for p in phr:
    for c in chunk_words(p["words"]):
        ru_chunks.append([c[0][0], c[-1][1], " ".join(x[2] for x in c)])
# EN chunks: spread words of the phrase evenly across its time slot
en_chunks = []
for p in phr:
    ws = p["en"].split(); n = len(ws); d = p["end"] - p["start"]
    fake = [[p["start"] + d * i / n, p["start"] + d * (i + 1) / n, ws[i]] for i in range(n)]
    for c in chunk_words(fake, 26):
        en_chunks.append([c[0][0], c[-1][1], " ".join(x[2] for x in c)])

def fix_gaps(ch):
    for i in range(len(ch) - 1):  # hold caption until next one if the gap is short
        if ch[i + 1][0] - ch[i][1] < 0.35: ch[i][1] = ch[i + 1][0]
        else: ch[i][1] += 0.2
    ch[-1][1] = min(ch[-1][1] + 0.3, 59.0)
    return ch
ru_chunks = fix_gaps(ru_chunks); en_chunks = fix_gaps(en_chunks)

def srt(ch, path):
    with open(path, "w") as f:
        for i, (a, b, t) in enumerate(ch, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
        f.write(f"{len(ch)+1}\n{ts(59.0)} --> {ts(60.0)}\nA PROMISE IS A PROMISE.\n\n")
srt(ru_chunks, f"{OUT}/subtitles/covenant_ru.srt")
srt(en_chunks, f"{OUT}/subtitles/covenant_en.srt")

def hl(text, kws):
    out = []
    for w in text.split():
        core = re.sub(r"[^\w'’-]", "", w)
        out.append("{\\c&H00D7FF&}" + w + "{\\c&HFFFFFF&}" if (core in kws or w in kws) else w)
    return " ".join(out)

# Scenes (60s scale), aligned to VO pauses
SC = [
    (0.0, 5.75, "THE LAST SURVIVOR", "Опасность"),
    (5.75, 14.8, "JOHN AND AHMED", "Знакомство"),
    (14.8, 21.5, "THE AMBUSH", "Засада"),
    (21.5, 29.2, "AHMED SAVES HIM", "Спасение"),
    (29.2, 38.3, "THE PROMISE", "Возвращение"),
    (38.3, 46.9, "BACK TO AFGHANISTAN", "Обещание"),
    (46.9, 53.7, "THE EXTRACTION", "Финал"),
    (53.7, 60.0, "THE COVENANT", "Концовка"),
]
# Shots: (start, end, scene#, description RU)
SH = [
    (0.0, 1.6, 1, "Экстрим-крупный план: глаза Джона, пыль, кровь на виске. Удар баса + звон в ушах"),
    (1.6, 3.0, 1, "Общий план: разрушенный горный склон, дым после боя"),
    (3.0, 4.3, 1, "Брошенное снаряжение отряда (без тел и крови)"),
    (4.3, 5.75, 1, "Джон лежит без сил, медленный наезд (zoom 100→110%)"),
    (5.75, 7.4, 2, "Тень фигуры над Джоном (лицо ещё не видно)"),
    (7.4, 10.4, 2, "РАСКРЫТИЕ: крупный план Ахмеда на слове «спасёт». Музыкальный удар"),
    (10.4, 12.3, 2, "Флэшбэк: база, Джон знакомится с новым переводчиком"),
    (12.3, 14.8, 2, "Джон и Ахмед вместе на выезде / блокпосту, панорама"),
    (14.8, 16.4, 3, "Отряд выдвигается к цели в горах, тревожная тишина"),
    (16.4, 17.9, 3, "Засада: вспышки, бойцы в укрытиях (быстрый монтаж 0.5–1 с)"),
    (17.9, 19.8, 3, "Джон ранен — падение, без крупного плана раны"),
    (19.8, 21.5, 3, "Ахмед среди хаоса, бросается к Джону"),
    (21.5, 23.8, 4, "Ахмед везёт Джона через горную тропу, широкий план с хребтом"),
    (23.8, 25.8, 4, "Крупно: лицо Ахмеда — пот, усталость, решимость"),
    (25.8, 27.6, 4, "Укрытие от преследователей, смена дня и ночи"),
    (27.6, 29.2, 4, "Американские военные замечают их — спасение"),
    (29.2, 31.4, 5, "Джон дома с семьёй, тёплые тона, медленная панорама"),
    (31.4, 34.9, 5, "Ахмед с семьёй скрывается, холодные тона"),
    (34.9, 36.6, 5, "Деталь: документы / отказ, музыка драматичнее"),
    (36.6, 38.3, 5, "Джон на телефоне, бессилие перед системой"),
    (38.3, 39.4, 6, "Джон принимает решение — крупный план взгляда"),
    (39.4, 41.1, 6, "Прилёт в Афганистан, общий план"),
    (41.1, 42.9, 6, "Встреча Джона и Ахмеда — ключевой эмоциональный кадр"),
    (42.9, 44.8, 6, "Жена и ребёнок Ахмеда"),
    (44.8, 46.9, 6, "Группа в пути к месту эвакуации"),
    (46.9, 48.6, 7, "Противники приближаются со всех сторон, быстрые планы ~1 с"),
    (48.6, 50.4, 7, "Герои в обороне, выхода нет, музыка нарастает"),
    (50.4, 52.4, 7, "Джон и Ахмед переглядываются, надежда гаснет"),
    (52.4, 53.7, 7, "Прибытие помощи с воздуха — кульминация, мощный звуковой удар"),
    (53.7, 56.0, 8, "Эвакуация: семья Ахмеда в безопасности"),
    (56.0, 59.0, 8, "Финальный кадр: Джон и Ахмед вместе, медленный отъезд камеры, музыка затихает"),
    (59.0, 60.0, 8, "Затемнение. Титр: A PROMISE IS A PROMISE."),
]
json.dump({"scenes": SC, "shots": SH, "phrases": [{k: p[k] for k in ("start", "end", "ru", "en")} for p in phr]},
          open("plan.json", "w"), ensure_ascii=False, indent=1)

def write_ass(lang, chunks, kws, path):
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,80,80,560,1
Style: Scene,DejaVu Sans,58,&H0000D7FF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,4,0,1,4,0,8,60,60,190,1
Style: Shot,DejaVu Sans,42,&H00E6F0F5,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,5,110,110,0,1
Style: Tag,DejaVu Sans,34,&H0090B4C8,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,8,60,60,110,1
Style: Final,DejaVu Serif,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,6,0,1,3,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for i, (a, b, n_, ru) in enumerate(SC, 1):
        ev.append(f"Dialogue: 1,{ass_t(a)},{ass_t(b)},Tag,,0,0,0,,АНИМАТИК · СЦЕНА {i}/8 · {ass_t(a)[2:7]}–{ass_t(b)[2:7]}")
        ev.append(f"Dialogue: 1,{ass_t(a)},{ass_t(b)},Scene,,0,0,0,,{{\\fad(200,150)}}{n_}")
    for k, (a, b, s, d) in enumerate(SH, 1):
        if b <= 59.0:
            ev.append(f"Dialogue: 1,{ass_t(a)},{ass_t(b)},Shot,,0,0,0,,{{\\pos(540,820)\\fad(120,120)}}КАДР {k}\\N\\N{d}")
    for a, b, t in chunks:
        ev.append(f"Dialogue: 2,{ass_t(a)},{ass_t(b)},Sub,,0,0,0,,{{\\fad(60,60)}}{hl(t, kws)}")
    ev.append(f"Dialogue: 3,{ass_t(58.95)},{ass_t(60.0)},Final,,0,0,0,,{{\\fad(300,0)}}A PROMISE\\NIS A PROMISE.")
    open(path, "w").write(hdr + "\n".join(ev) + "\n")

write_ass("ru", ru_chunks, KW_RU, f"{OUT}/subtitles/covenant_ru_styled.ass")
write_ass("en", en_chunks, KW_EN, f"{OUT}/subtitles/covenant_en_styled.ass")
for p in phr: print(f"{p['start']:5.2f}-{p['end']:5.2f} {p['ru']}")
print(len(ru_chunks), len(en_chunks))
