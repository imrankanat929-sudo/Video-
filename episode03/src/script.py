"""HUMAN MIND — Episode 03: Why does deja vu happen?
Narration, on-screen text and timing shared by the renderer and the audio mixer.
Each VO line has a planned start (seconds). Actual starts are resolved after TTS
so lines never overlap (see tts.py -> assets/vo_<lang>/timing.json).
"""

DURATION = 104.0
FPS = 30

VOICES = {
    "en": dict(voice="en-US-AndrewNeural", rate="-10%", pitch="-6Hz"),
    "ru": dict(voice="en-US-AndrewMultilingualNeural", rate="+0%", pitch="-10Hz"),
}

# The Russian narration for 0:00–0:49 is the supplied recording
# (assets/ru_supplied_narration.mp3), placed at SUPPLIED_OFFSET. Its segments
# (whisper timings) define the timeline of the first half; the English lines are
# translations placed on the same beats. ru=None means "taken from the supplied file".
SUPPLIED_OFFSET = 0.25
SUPPLIED_FIX = {"дожавю.": "дежавю.", "мозде": "мозге", "что -то": "что-то"}

# (id, planned_start, latest_end, en, ru)
VO = [
    # SCENE 1 — the street / something feels familiar
    ("a1", 0.25, 5.6, "You're walking down the street, talking with a friend… and suddenly you notice something strange.", None),
    ("a2", 5.95, 10.3, "You've seen this street before. You've heard these exact words.", None),
    ("a3", 10.71, 16.3, "You even remember how you're about to turn your head… and what will happen a few seconds from now.", None),
    ("a4", 16.67, 21.8, "And the strangest part — everything happens exactly the way you imagined.", None),
    ("a5", 22.15, 25.9, "But wait. You've never been on this street before.", None),
    # SCENE 2 — the loop
    ("a6", 26.25, 32.4, "This conversation is happening for the first time. And there's no way you could know what comes next.", None),
    ("a7", 32.63, 35.0, "So where does this feeling come from?", None),
    ("a8", 35.23, 40.9, "Why does an ordinary moment suddenly feel like a memory from the past?", None),
    # SCENE 3 — what is deja vu
    ("a9", 41.29, 43.9, "This is called déjà vu.", None),
    ("a10", 44.21, 49.6, "And what happens in your brain in those seconds is far more interesting than it seems.", None),
    # SCENE 4 — the memory connection
    ("b1", 50.4, 56.2, "Your brain constantly stores fragments of experience: shapes, faces, places, sounds.",
                       "Мозг постоянно хранит фрагменты опыта: формы, лица, места, звуки."),
    ("b2", 56.6, 60.6, "When a new place resembles an old one — its layout, its light —",
                       "Когда новое место похоже на старое — планировкой, светом, —"),
    ("b3", 60.8, 65.4, "the brain may signal “familiar”… without retrieving the memory itself.",
                       "мозг может сказать «знакомо»… не находя само воспоминание."),
    ("b4", 65.8, 68.4, "Familiarity is not recollection.",
                       "Знакомость — ещё не воспоминание."),
    ("b5", 68.7, 72.2, "The moment feels known… but you can't say where from.",
                       "Момент кажется знакомым… но ты не знаешь откуда."),
    # SCENE 5 — what science knows
    ("c1", 73.0, 79.4, "Scientists have several explanations — memory, attention, and how the brain checks what it recognizes.",
                       "У учёных есть несколько объяснений: память, внимание, работа узнавания."),
    ("c2", 79.8, 84.0, "But the exact mechanism… is still being studied.",
                       "Но точный механизм… всё ещё изучается."),
    # SCENE 6 — final question
    ("d1", 87.4, 91.0, "So the next time a moment feels like a replay… pause.",
                       "Когда момент снова покажется повтором… остановись."),
    ("d2", 91.2, 94.8, "Your mind may be recognizing something it can't quite remember.",
                       "Возможно, разум узнаёт то, чего не помнит."),
    ("d3", 95.4, 99.2, "Have you ever experienced déjà vu?",
                       "А ты когда-нибудь испытывал дежавю?"),
]

# On-screen text
TEXT = {
    "en": {
        "q1": "HAVE I BEEN HERE BEFORE?",
        "dv": "DÉJÀ VU",
        "fam": "A FEELING OF FAMILIARITY",
        "neq": ("FAMILIARITY", "≠", "RECOLLECTION"),
        "mech": "THE EXACT MECHANISM IS STILL BEING STUDIED",
        "final": "HAVE YOU EVER EXPERIENCED DÉJÀ VU?",
        "brand": "HUMAN MIND",
        "ep": "EPISODE 03",
        "room_a": "MEMORY", "room_b": "NOW",
        "brain_tag": "MEMORY",
        "repeat": "REPLAY",
    },
    "ru": {
        "q1": "Я УЖЕ БЫЛ ЗДЕСЬ?",
        "dv": "ДЕЖАВЮ",
        "fam": "ОЩУЩЕНИЕ ЗНАКОМОСТИ",
        "neq": ("ЗНАКОМОСТЬ", "≠", "ВОСПОМИНАНИЕ"),
        "mech": "ТОЧНЫЙ МЕХАНИЗМ ЕЩЁ ИЗУЧАЕТСЯ",
        "final": "А ВЫ КОГДА-НИБУДЬ ИСПЫТЫВАЛИ ДЕЖАВЮ?",
        "brand": "HUMAN MIND",
        "ep": "ЭПИЗОД 03",
        "room_a": "ПАМЯТЬ", "room_b": "СЕЙЧАС",
        "brain_tag": "ПАМЯТЬ",
        "repeat": "ПОВТОР",
    },
}

# Subtitle keyword highlighting (lower-case prefixes)
KEYWORDS = {
    "en": ["déjà", "vu", "familiar", "memory", "recollection"],
    "ru": ["дежавю", "знаком", "воспомин", "памят"],
}
