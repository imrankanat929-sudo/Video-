"""DIDAO S01E01 "THE LAST NIGHT" - master script / timing sheet.

Every clip: id, file name, duration (s), and narration lines.
Each VO line: (start offset inside the clip in seconds, RU text, EN text).
Durations were fitted to the longer of the two languages + breathing room,
so the same picture works for both versions.
"""

SERIES = "DIDAO"
SEASON_TITLE_EN = "THE FOREST HAS NO EXIT"
SEASON_TITLE_RU = "ЛЕС БЕЗ ВЫХОДА"
EP_TITLE_EN = "Episode 1: The Last Night"
EP_TITLE_RU = "Серия 1: Последняя ночь"

CLIPS = [
    dict(id=1, name="CLIP_01_JOURNEY", dur=11.5, vo=[
        (1.6, "Нас было трое. Одни выходные. Лес, в котором никто не ночевал уже много лет.",
              "There were three of us. One weekend. A forest nobody had camped in for years."),
        (8.5, "Мы думали, это просто страшилка.",
              "We thought it was just a story."),
    ]),
    dict(id=2, name="CLIP_02_CAMPSITE", dur=10.0, vo=[
        (1.0, "К ночи у нас были палатка, костёр…",
              "By nightfall, we had a tent, a fire…"),
        (5.2, "и странное чувство, что мы здесь не одни.",
              "and the strange feeling that we weren't alone."),
    ]),
    dict(id=3, name="CLIP_03_FIRST_SIGHTING", dur=10.0, vo=[
        (0.8, "Лена заметила его первой.",
              "Lena saw it first."),
        (4.2, "Что-то высокое. Между деревьями.",
              "Something tall. Between the trees."),
        (7.6, "Оно не двигалось.",
              "It wasn't moving."),
    ]),
    dict(id=4, name="CLIP_04_DISAPPEARANCE", dur=9.5, vo=[
        (0.6, "Я направил на него фонарик…",
              "I pointed my flashlight at it…"),
        (4.0, "и он исчез.",
              "and it was gone."),
        (6.4, "Макс сказал, что это просто дерево.",
              "Max said it was just a tree."),
    ]),
    dict(id=5, name="CLIP_05_MIDNIGHT", dur=9.0, vo=[
        (1.2, "Около полуночи я проснулся.",
              "Around midnight, I woke up."),
        (4.4, "Костёр погас. Лес стал абсолютно тихим.",
              "The fire was out. The forest had gone completely silent."),
    ]),
    dict(id=6, name="CLIP_06_FOOTSTEPS", dur=11.0, vo=[
        (5.4, "Шаги. Три медленных шага. Прямо у палатки.",
              "Footsteps. Three slow steps. Right outside the tent."),
    ]),
    dict(id=7, name="CLIP_07_SECOND_SIGHTING", dur=10.0, vo=[
        (2.6, "Он стоял ближе. Намного ближе.",
              "It was closer now. Much closer."),
        (6.4, "И смотрел прямо на нашу палатку.",
              "And it was watching our tent."),
    ]),
    dict(id=8, name="CLIP_08_DISAPPEARANCE_AGAIN", dur=10.0, vo=[
        (0.5, "Я разбудил остальных.",
              "I woke the others."),
        (4.6, "Но когда мы выбежали наружу… там никого не было.",
              "But by the time we got outside… there was no one there."),
    ]),
    dict(id=9, name="CLIP_09_MISSING_PATH", dur=10.0, vo=[
        (1.0, "Утром мы собрались уходить.",
              "In the morning, we packed up to leave."),
        (4.4, "Но тропинки, по которой мы пришли… больше не было.",
              "But the path we came in on… was gone."),
    ]),
    dict(id=10, name="CLIP_10_WARNING", dur=9.0, vo=[
        (0.6, "А потом я увидел надпись на дереве.",
              "Then I saw the words carved into a tree."),
        (5.6, "«Не оглядывайтесь».",
              "Do not look back."),
    ]),
    dict(id=11, name="CLIP_11_PHONE_MESSAGE", dur=9.0, vo=[
        (0.5, "Связи не было уже много часов.",
              "We'd had no signal for hours."),
        (3.4, "Но телефон завибрировал.",
              "But my phone buzzed."),
        (6.6, "Одно новое сообщение.",
              "One new message."),
    ]),
    dict(id=12, name="CLIP_12_FINAL_REVEAL", dur=12.0, vo=[
        (0.6, "Я поднял голову…",
              "I looked up…"),
        (5.0, "Он был не один.",
              "It wasn't alone."),
    ]),
]

# On-screen text translations for subtitles (diegetic English text stays English in picture).
ONSCREEN = {
    10: (5.6, 8.6, "НЕ ОГЛЯДЫВАЙТЕСЬ", "DO NOT LOOK BACK"),
    11: (6.0, 8.8, "Я ВИЖУ ВАС ВСЕХ.", "I CAN SEE YOU ALL."),
}
