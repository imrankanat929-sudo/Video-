"""Voice-over groups placed on the 120 s timeline so that every line lands on its matching scene.
Each group = list of whisper segment indices per language + anchor time (seconds in the final video).
Texts are proof-read (whisper typos fixed)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (id, ru_segments, en_segments, anchor, tag_ru, tag_en)
GROUPS = [
    ('hook',     [0],      [0],            0.45, 'ЛЕС',               'FOREST'),
    ('intro',    [1, 2],   [1, 2],         3.55, 'ПРОГУЛКА',          'A WALK'),
    ('trail',    [3, 4],   [3, 4],         11.0, 'ТРОПА',             'THE TRAIL'),
    ('crack',    [5],      [5],            17.5, 'ХРУСТ',             'SNAP'),
    ('see',      [6],      [6],            19.75, 'БУРЫЙ МЕДВЕДЬ',    'BROWN BEAR'),
    ('stands',   [7],      [7],            24.75, 'ДИСТАНЦИЯ',        'DISTANCE'),
    ('freeze',   [8],      [8, 9],         27.6, 'ТЫ ЗАМИРАЕШЬ',      'YOU FREEZE'),
    ('sniff',    [9],      [10],           32.0, 'ЗАПАХ',             'SCENT'),
    ('what',     [10],     [11, 12, 13, 14], 37.0, 'ЧТО ДЕЛАТЬ?',     'WHAT TO DO?'),
    ('main',     [11],     [15, 16],       43.3, 'ГЛАВНОЕ',           'KEY RULE'),
    ('advice1',  [12, 13], [17, 18],       50.3, 'НЕ ПРИБЛИЖАЙСЯ',    "DON'T APPROACH"),
    ('voice',    [14],     [19],           56.0, 'СПОКОЙНЫЙ ГОЛОС',   'CALM VOICE'),
    ('distance', [15, 16], [20, 21, 22],   62.4, 'ДИСТАНЦИЯ',         'DISTANCE'),
    ('faster',   [17],     [23],           69.6, 'ОН БЛИЖЕ',          'CLOSER'),
    ('serious',  [18],     [24],           72.8, 'ОПАСНОСТЬ',         'DANGER'),
    ('bluff',    [19, 20], [25, 26],       77.6, 'ЛОЖНЫЙ ВЫПАД',      'BLUFF CHARGE'),
    ('species',  [21, 22], [27, 28],       84.5, 'ВАЖНО',             'REMEMBER'),
    ('experts',  [23, 24], [29, 30],       89.9, 'СПЕЦИАЛИСТЫ',       'EXPERTS'),
    ('stops',    [25, 26], [31, 32],       95.6, 'ОН УХОДИТ',         'IT LEAVES'),
    ('reflect',  [27, 28], [33, 34],       102.4, 'ПОЗАДИ',           'BEHIND YOU'),
    ('question', [29],     [35],           107.6, 'ВОПРОС',           'QUESTION'),
    ('final',    [30, 31], [36, 37],       109.0, 'А ТЫ?',            'AND YOU?'),
]

# proof-read texts per group (subtitle text)
TEXT = {
    'ru': {
        'hook': 'А что, если на тебя напал медведь в лесу?',
        'intro': 'Представь, ты отправился в лес на прогулку. Вокруг красивые деревья, свежий воздух и полная тишина.',
        'trail': 'Ты идёшь по тропинке, слушаешь музыку и даже не подозреваешь, что за тобой кто-то наблюдает.',
        'crack': 'Вдруг впереди ломается ветка.',
        'see': 'Ты поворачиваешь голову и видишь огромного бурого медведя.',
        'stands': 'Он стоит всего в нескольких десятках метров.',
        'freeze': 'Ты замираешь. Медведь тоже замечает тебя.',
        'sniff': 'Он поднимает голову и начинает принюхиваться.',
        'what': 'Что делать? Бежать? Кричать? Попытаться спрятаться?',
        'main': 'Самое главное — не паниковать и не пытаться убежать.',
        'advice1': 'Не приближайся к медведю. Не делай резких движений и не пытайся его кормить.',
        'voice': 'Если медведь заметил тебя, говори спокойным голосом.',
        'distance': 'Если он не проявляет агрессии, медленно увеличивай расстояние, не перекрывая ему путь.',
        'faster': 'Но вдруг медведь начинает приближаться быстрее.',
        'serious': 'Ты понимаешь, что ситуация становится серьёзной.',
        'bluff': 'Некоторые медведи могут совершать ложные выпады, поэтому не каждый бросок означает настоящую атаку.',
        'species': 'Важно понимать: поведение зависит от вида медведя и обстоятельств встречи.',
        'experts': 'При реальном контакте нужно следовать рекомендациям местных специалистов по дикой природе.',
        'stops': 'Наконец медведь останавливается, разворачивается и исчезает между деревьями.',
        'reflect': 'Ты стоишь и понимаешь, насколько близко оказался к настоящей опасности.',
        'question': 'А теперь вопрос.',
        'final': 'Если бы ты встретил медведя в лесу, смог бы сохранить спокойствие?',
    },
    'en': {
        'hook': 'What if a bear attacked you in the forest?',
        'intro': "Imagine you're going for a walk in the forest. Beautiful trees, fresh air, and complete silence.",
        'trail': "You're walking along a trail, listening to music, without realizing that something is watching you.",
        'crack': 'Suddenly, a branch snaps.',
        'see': 'You turn your head and see an enormous brown bear.',
        'stands': "It's standing just a short distance away.",
        'freeze': 'You freeze. The bear notices you too.',
        'sniff': 'It raises its head and starts sniffing the air.',
        'what': 'What should you do? Run? Scream? Try to hide?',
        'main': 'The most important thing is not to panic or try to run away.',
        'advice1': "Don't approach the bear, make sudden movements, or try to feed it.",
        'voice': 'If the bear has noticed you, speak in a calm voice.',
        'distance': "If it isn't acting aggressively, slowly increase the distance without blocking its escape route.",
        'faster': 'But suddenly, the bear starts moving closer.',
        'serious': 'You realize the situation is becoming serious.',
        'bluff': 'Some bears make bluff charges, so not every sudden movement means an actual attack.',
        'species': "Remember, the right response depends on the bear's species and the circumstances.",
        'experts': 'In a real encounter, follow the guidance of local wildlife experts.',
        'stops': 'Finally, the bear stops, turns around, and disappears between the trees.',
        'reflect': 'You stand there, realizing just how close you came to real danger.',
        'question': "Now here's the question.",
        'final': 'If you encountered a bear in the forest, would you be able to stay calm?',
    },
}

# word-level highlight (yellow) keywords, lower-case stems
HILITE = {
    'ru': ['медвед', 'лес', 'ветк', 'замира', 'паник', 'убежа', 'бежать', 'кричать', 'спрятат', 'кормить', 'спокойн',
           'расстояни', 'быстрее', 'серьёзн', 'серьезн', 'ложн', 'атак', 'специалист', 'исчезает', 'опасност', 'спокойстви', 'наблюдает', 'принюх', 'тишина'],
    'en': ['bear', 'forest', 'branch', 'freeze', 'panic', 'run', 'scream', 'hide', 'feed', 'calm', 'distance', 'closer',
           'serious', 'bluff', 'attack', 'experts', 'disappears', 'danger', 'watching', 'sniffing', 'silence'],
}


# measured onset corrections (whisper merged segment boundaries): first word starts later than reported
ONSET_FIX = {('ru', 'stops'): 0.5, ('en', 'sniff'): 0.45, ('en', 'serious'): 0.18}


def load_words(lang):
    return json.load(open(os.path.join(ROOT, 'build', f'words_{lang}.json')))


def placed(lang):
    """Return list of dicts: id, src_start, src_end, dst_start, words[(w, s, e)] in dst time, text, tag."""
    segs = load_words(lang)
    out = []
    for g in GROUPS:
        gid, ru, en, anchor, tag_ru, tag_en = g
        idx = ru if lang == 'ru' else en
        words = []
        for i in idx:
            words += segs[i]['words']
        s0 = words[0]['s']
        s1 = words[-1]['e']
        off = anchor - s0
        ws = [(w['w'], w['s'] + off, w['e'] + off) for w in words]
        fx = ONSET_FIX.get((lang, gid), 0.0)
        if fx:
            ws[0] = (ws[0][0], ws[0][1] + fx, max(ws[0][2], ws[0][1] + fx + 0.15))
        out.append(dict(id=gid, src_start=s0, src_end=s1, dst_start=anchor, dst_end=s1 + off, off=off,
                        words=ws,
                        text=TEXT[lang][gid], tag=tag_ru if lang == 'ru' else tag_en))
    return out


if __name__ == '__main__':
    for lang in ('ru', 'en'):
        P = placed(lang)
        for a, b in zip(P, P[1:] + [None]):
            nxt = b['dst_start'] if b else 120
            flag = '  <-- OVERLAP' if a['dst_end'] > nxt - 0.15 else ''
            print(lang, f"{a['id']:9s} {a['dst_start']:6.2f}-{a['dst_end']:6.2f} (src {a['src_start']:.2f}-{a['src_end']:.2f}) gap {nxt - a['dst_end']:.2f}{flag}")
