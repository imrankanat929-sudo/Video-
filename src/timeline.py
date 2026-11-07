"""Strings, scene cues (anchored to voice-over words) and subtitle chunks."""
import json
import re

STR = {
    "ru": dict(
        t1="ЧТО, ЕСЛИ АСТЕРОИД", t2="УПАДЁТ ЧЕРЕЗ", t3="7 ДНЕЙ?",
        date="суббота, 7 ноября", alert="ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ", now="сейчас",
        alert_body="Обнаружен крупный астероид на курсе столкновения с Землёй. Следите за официальными сообщениями.",
        earth="ЗЕМЛЯ", obj="ОБЪЕКТ 2026 XR7", prob="ВЕРОЯТНОСТЬ УДАРА", dia="ДИАМЕТР", km="КМ", track="СОПРОВОЖДЕНИЕ ЦЕЛИ",
        chat="Друзья", online="в сети",
        fake_msgs=["Опять какой-то фейк", "Это же нейросеть нарисовала", "Не верю. Завтра опровергнут", "Вы новости видели?!"],
        fake="ФЕЙК?", live="ПРЯМОЙ ЭФИР", breaking="СРОЧНО",
        confirm="ПРАВИТЕЛЬСТВА ПОДТВЕРЖДАЮТ УГРОЗУ",
        ticker="АСТЕРОИД ДВИЖЕТСЯ К ЗЕМЛЕ   •   ДО СТОЛКНОВЕНИЯ 7 ДНЕЙ   •   КОСМИЧЕСКИЕ АГЕНТСТВА ПОДТВЕРЖДАЮТ ДАННЫЕ   •   ",
        days7="7 ДНЕЙ", hours7="7 ЧАСОВ", until="ДО СТОЛКНОВЕНИЯ", day="ДЕНЬ",
        left=lambda n: f"ОСТАЛОСЬ {n} {'ДЕНЬ' if n == 1 else 'ДНЯ' if 2 <= n <= 4 else 'ДНЕЙ'}" if n else "ПОСЛЕДНИЙ ДЕНЬ",
        traj="РАСЧЁТ ТРАЕКТОРИИ", oos="ТОВАР ЗАКОНЧИЛСЯ", dep="ВЫЛЕТ",
        stat=["ОТМЕНЁН", "ПОСАДКА", "ЗАДЕРЖАН", "МЕСТ НЕТ"],
        cities=["СИДНЕЙ", "ТОКИО", "КЕЙПТАУН", "САНТЬЯГО", "ОКЛЕНД", "ДУБАЙ", "ВЕЛЛИНГТОН", "ЛИМА"],
        forecast="ПРОГНОЗ", zone="ЗОНА ПОРАЖЕНИЯ", calm="СОХРАНЯЙТЕ СПОКОЙСТВИЕ",
        mom="Мама", calling="вызов…", friend="Макс",
        msg_out="Привет. Давно не общались… Как ты?", msg_in="Брат… я как раз хотел тебе написать",
        mission="МИССИЯ «ЩИТ»", inprog="ИДЁТ ОПЕРАЦИЯ", elapsed="ПРОШЛО",
        failed1="МИССИЯ", failed2="ПРОВАЛЕНА",
        size="РАЗМЕР", site="МЕСТО ПАДЕНИЯ", aft="ПОСЛЕДСТВИЯ",
        together="ВМЕСТЕ?", apart="ИЛИ ПОРОЗНЬ?",
        fin1="ЧТО БЫ ТЫ СДЕЛАЛ", fin2="ПЕРВЫМ ДЕЛОМ?", cta="Напиши в комментариях",
    ),
    "en": dict(
        t1="WHAT IF AN ASTEROID", t2="HITS EARTH IN", t3="7 DAYS?",
        date="Saturday, November 7", alert="EMERGENCY ALERT", now="now",
        alert_body="A large asteroid has been detected on a collision course with Earth. Follow official updates.",
        earth="EARTH", obj="OBJECT 2026 XR7", prob="IMPACT PROBABILITY", dia="DIAMETER", km="KM", track="TARGET TRACKING",
        chat="Friends", online="online",
        fake_msgs=["Another fake story lol", "That's obviously AI generated", "Not buying it. They'll deny it tomorrow", "Did you guys see the news?!"],
        fake="FAKE?", live="LIVE", breaking="BREAKING",
        confirm="GOVERNMENTS CONFIRM THE THREAT",
        ticker="ASTEROID HEADING FOR EARTH   •   IMPACT EXPECTED IN 7 DAYS   •   SPACE AGENCIES CONFIRM THE DATA   •   ",
        days7="7 DAYS", hours7="7 HOURS", until="UNTIL IMPACT", day="DAY",
        left=lambda n: f"{n} {'DAY' if n == 1 else 'DAYS'} LEFT" if n else "THE LAST DAY",
        traj="TRAJECTORY ANALYSIS", oos="OUT OF STOCK", dep="DEPARTURES",
        stat=["CANCELLED", "BOARDING", "DELAYED", "FULL"],
        cities=["SYDNEY", "TOKYO", "CAPE TOWN", "SANTIAGO", "AUCKLAND", "DUBAI", "WELLINGTON", "LIMA"],
        forecast="FORECAST", zone="IMPACT ZONE", calm="REMAIN CALM",
        mom="Mom", calling="calling…", friend="Max",
        msg_out="Hey. It's been years… How are you?", msg_in="Man… I was just about to text you",
        mission="MISSION SHIELD", inprog="OPERATION IN PROGRESS", elapsed="ELAPSED",
        failed1="MISSION", failed2="FAILED",
        size="SIZE", site="IMPACT SITE", aft="AFTERMATH",
        together="TOGETHER?", apart="OR APART?",
        fin1="WHAT WOULD YOU", fin2="DO FIRST?", cta="Tell me in the comments",
    ),
}

# (scene, arg, ru phrase, en phrase). Start = first word of phrase.
CUES = [
    ("hook", None, None, None),
    ("phone_wake", None, "представь", "imagine"),
    ("radar", None, "учёные обнаружили", "scientists have"),
    ("fake", None, "сначала никто", "at first"),
    ("confirm", None, "но через", "but a few"),
    ("asteroid_close", None, "астероид действительно", "the asteroid is real"),
    ("day", 1, "день 1", "day one"),
    ("mission", None, "по всему", "emergency meetings"),
    ("tv_wall", None, "новости показывают", "every news"),
    ("store", None, "люди массово", "people rush"),
    ("airport", None, "а аэропорты", "airports"),
    ("day", 3, "день 3", "day three"),
    ("size", None, "появляется новая", "new information"),
    ("earth_zone", None, "даже если", "even if"),
    ("sirens", None, "правительства призывают", "governments tell"),
    ("calls", None, "кто-то возвращается", "some people return"),
    ("rooftop", None, "а кто-то просто", "and some simply"),
    ("day", 5, "день 5", "day five"),
    ("launch", None, "учёные запускают", "scientists launch"),
    ("watch", None, "весь мир", "the entire world"),
    ("failed", None, "и, наконец", "then the announcement"),
    ("day", 7, "день 7", "day seven"),
    ("quiet", None, "до столкновения", "only a few"),
    ("family", None, "многие люди", "many people"),
    ("bright", None, "в небе", "a bright"),
    ("entry", None, "и вот", "and then the moment"),
    ("flash", None, "небо озаряется", "the sky fills"),
    ("destruction", None, "земля содрогается", "the ground shakes"),
    ("earth_dust", None, "но что будет", "but what happens"),
    ("rebuild", None, "некоторые регионы", "some regions"),
    ("q_mark", None, "но есть один", "but there is one"),
    ("unite", None, "если бы", "if humanity"),
    ("divide", None, "или страх", "or would fear"),
    ("twist", None, "а теперь", "now imagine"),
    ("final", None, "что бы ты", "what would you"),
]

# named events: (key, ru phrase, en phrase, which word of phrase)
EVENTS = [
    ("see", "и видишь", "and seeing", 1),
    ("days", "ровно через 7 дней", "in exactly seven days", 2),
    ("friends", "кто-то звонит", "others call", 0),
    ("mfail", "миссия не", "the mission failed", 0),
    ("sz", "от размера", "asteroid's size", 1),
    ("site", "местопадения", "where it hits", 0),
    ("aft", "и последствий", "and the effects", 1),
    ("hours", "всего 7 часов", "just seven hours", 1),
    ("impact", "земля содрогается", "the ground shakes", 0),
    ("flash", "небо озаряется", "the sky fills", 0),
    ("dot", "в небе", "a bright", 0),
    ("notify", "и видишь", "and seeing", 1),
    ("launch", "учёные запускают", "scientists launch", 1),
]

FIX = {"местопадения": "места падения", "допадение": "до падения", "Ученые": "Учёные", "еще": "ещё"}


def norm(w):
    return re.sub(r"[^\wё-]", "", w.lower().replace("ё", "е"))


def find(words, phrase, after=0.0, idx=0):
    toks = [norm(x) for x in phrase.split()]
    nw = [norm(w[0]) for w in words]
    for i in range(len(words)):
        if words[i][1] < after - 0.01:
            continue
        if nw[i:i + len(toks)] == toks:
            return words[i + idx][1]
    raise KeyError(phrase)


def build(lang, words_path, duration):
    words = []
    for w in json.load(open(words_path)):
        w0 = w[0].strip()
        if words and w0.startswith("-"):
            pw = words[-1]
            words[-1] = (pw[0] + w0, pw[1], w[2])
        else:
            words.append((w0, w[1], w[2]))
    li = 2 if lang == "ru" else 3
    starts, t = [], 0.0
    for c in CUES:
        if c[li] is None:
            starts.append(0.0)
            continue
        t = find(words, c[li], t) - 0.12
        starts.append(t)
    end = duration + 1.6
    scenes = []
    for i, c in enumerate(CUES):
        e = starts[i + 1] if i + 1 < len(CUES) else end
        scenes.append(dict(name=c[0], arg=c[1], start=starts[i], end=e))
    evs = {}
    for key, ru, en, k in EVENTS:
        evs[key] = find(words, ru if lang == "ru" else en, 0, k)
    return scenes, evs, words, end


def chunks(words, lang, max_chars=17, max_words=3):
    """Group words into short subtitle chunks."""
    out, cur = [], []
    for (w, s, e) in words:
        core = w.strip(",.?!")
        if core in FIX:
            w = w.replace(core, FIX[core])
        cur_len = sum(len(x[0]) + 1 for x in cur)
        if cur and (cur_len + len(w) > max_chars or len(cur) >= max_words or s - cur[-1][2] > 0.35):
            out.append(cur)
            cur = []
        cur.append((w, s, e))
        if w[-1] in ".?!,":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    # don't leave short words (и, а, the, a…) dangling at the end of a chunk
    for i in range(len(out) - 1):
        c = out[i]
        if len(c) > 1 and len(c[-1][0]) <= 3 and c[-1][0][-1] not in ".?!,":
            out[i + 1].insert(0, c.pop())
    # merge lonely one-word chunks into the previous one when it fits
    merged = []
    for c in out:
        if merged and len(c) == 1 and sum(len(x[0]) + 1 for x in merged[-1]) + len(c[0][0]) <= 20 and c[0][1] - merged[-1][-1][2] < 0.3 and merged[-1][-1][0][-1] not in ".?!":
            merged[-1].extend(c)
        else:
            merged.append(c)
    out = merged
    res = []
    for i, c in enumerate(out):
        st, en = c[0][1], c[-1][2]
        nxt = out[i + 1][0][1] if i + 1 < len(out) else en + 0.5
        en = min(nxt, en + 0.35)
        res.append(dict(start=st, end=en, words=[(w.strip(",.").upper() if True else w, s, e) for (w, s, e) in c]))
    return res
