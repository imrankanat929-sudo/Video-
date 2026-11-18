"""THE LISTENERS — Эпизод 01 — «15 правил, чтобы выжить среди Слушающих».
Version 2: narration = the client's script (Alex narrates). Visual functions are reused from scenes_v1
and extended with new shots.  Speakers: N narrator (Alex, low calm), W narrator whisper,
MIMA creature using Alex's voice, MIMW same whispered, FRIEND creature using a friend's voice."""
import scenes_v1 as V
from scenes_v1 import *  # noqa  (visuals, helpers, Q)

SCENES = []
V.REC_DATE = '14.03.2014'


def sc(id_, part, vo, draw, amb='none', mus='calm', sfx=(), min_dur=6.0, cam=None, fade_in=0.0, fade_out=0.0,
       lead=0.8, tail=1.4, gap=0.6, prompt=''):
    SCENES.append(dict(id=id_, part=part, vo=list(vo), draw=draw, amb=amb, mus=mus, sfx=list(sfx), min_dur=min_dur,
                       cam=cam, fade_in=fade_in, fade_out=fade_out, lead=lead, tail=tail, gap=gap, title=None, prompt=prompt))


V.RULES[:] = [
    'Никогда не включай громкую музыку.',
    'Не разговаривай возле открытых окон.',
    'Не открывай дверь на знакомый голос.',
    'Отключи звуковые уведомления телефона.',
    'Не оставляй телевизор включённым.',
    'Не отвечай на голоса с улицы.',
    'Не доверяй голосам, знающим твоё имя.',
    'Тишина — не признак безопасности.',
    'Не игнорируй странные звуки.',
    'Они запоминают услышанное.',
    'Не верь каждому сообщению об убежищах.',
    'Не отделяйся от тех, кому доверяешь.',
    'Не игнорируй экстренные предупреждения.',
    'Не возвращайся за вещами.',
    'Не отвечай своему голосу.',
]
V.RULE_TITLES[:] = [
    'НЕ ВКЛЮЧАЙ\nГРОМКУЮ МУЗЫКУ', 'НЕ ГОВОРИ\nУ ОТКРЫТЫХ ОКОН', 'НЕ ОТКРЫВАЙ\nНА ЗНАКОМЫЙ ГОЛОС', 'ОТКЛЮЧИ ЗВУК\nТЕЛЕФОНА',
    'НЕ ОСТАВЛЯЙ\nТЕЛЕВИЗОР', 'НЕ ОТВЕЧАЙ\nГОЛОСАМ С УЛИЦЫ', 'ОН ЗНАЕТ\nТВОЁ ИМЯ', 'ТИШИНА —\nНЕ БЕЗОПАСНОСТЬ',
    'НЕ ИГНОРИРУЙ\nСТРАННЫЕ ЗВУКИ', 'ОНИ\nЗАПОМИНАЮТ', 'НЕ ВЕРЬ\nКАЖДОМУ УБЕЖИЩУ', 'НЕ ОТДЕЛЯЙСЯ\nОТ СВОИХ',
    'НЕ ИГНОРИРУЙ\nПРЕДУПРЕЖДЕНИЯ', 'НЕ ВОЗВРАЩАЙСЯ\nЗА ВЕЩАМИ', 'НЕ ОТВЕЧАЙ\nСВОЕМУ ГОЛОСУ',
]
V.RULE_SUBS[:] = [
    'ОНИ СЛЫШАТ ЗА КВАРТАЛ', 'ДАЖЕ ОБЫЧНЫЙ РАЗГОВОР', 'ОНИ КОПИРУЮТ ГОЛОСА', 'БЕЗЗВУЧНЫЙ РЕЖИМ',
    'ЧУЖОЕ ДЫХАНИЕ', 'КТО СТОИТ СНАРУЖИ?', 'ОНИ УЧАТСЯ', 'ОНИ УМЕЮТ ЖДАТЬ',
    'ТРИ УДАРА — И ТИШИНА', 'ГОЛОС ДРУГА', 'НЕКОТОРЫЕ — ЛОВУШКИ', 'ОДИН — НЕ ВЫЖИВЕШЬ',
    'ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ', 'ВЕЩИ НЕ СТОЯТ ЖИЗНИ', 'ОНИ ДАВНО НАБЛЮДАЮТ',
]


def with_card(fn, n, start=0.3, dur=4.2):
    def d(c, t, T, q):
        fn(c, t, T, q)
        V.card(c, t, n, start, dur)
    return d


def nb_insert(n, sfx_gain=0.5):
    sc(f'nb{n}', SCENES[-1]['part'], [], V.nb(n), amb='room_night', mus='calm', sfx=[(0.6, 'pen_write', sfx_gain)], min_dur=4.3, cam=(1.0, 1.05, 960, 500),
       prompt=f'Insert: Alex writes rule {n} into his notebook.')


# ===================================================================== new visuals

def v_normal_city(c, t, T, q):
    city_bg(c, t, '#5b8bd0', '#c9dcf0', moon_xy=None, seed=33, lit=0.0, stars_n=0, fog_a=0.0)
    road(c, 800, '#4a4d58')
    k = 1 - seg(t, T - 2.0, T)  # people fade away at the end
    for i, (x, col) in enumerate(((120, '#c0392b'), (520, '#2c7be5'), (920, '#f1c40f'), (1320, '#7b8696'), (1720, '#27ae60'))):
        car(c, (x + t * 25) % (W + 400) - 200, 960, 0.55, col, lights=True, t=t)
    r = random.Random(4)
    for i in range(7):
        x = (r.uniform(0, W) + t * r.uniform(-40, 40)) % W
        c.saveLayerAlpha(None, int(255 * k))
        person(c, x, 840, 0.3, coat=r.choice(['#7a2d2d', '#2d4a7a', '#4b5d3a', '#8a5a2b', '#5a3d55']), hair=r.choice(['#3a2a1a', '#111', '#6b2f1a']),
               female=i % 2 == 0, hairstyle='long', walk=t * 0.8 + i, flip=i % 3 == 0, t=t + i, mouth=0.0)
        c.restore()
    for i in range(4):
        bx = (t * 50 + i * 300) % (W + 200) - 100
        by = 160 + math.sin(t + i) * 20 + i * 25
        line(c, bx - 12, by, bx, by + 6, '#1e2230', 3)
        line(c, bx, by + 6, bx + 12, by, '#1e2230', 3)


def v_missing_news(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a0e18'))
    # stylised world: dotted continents on a grid
    for x in range(0, W, 60):
        line(c, x, 140, x, 940, C('#3b5bdb', 0.10), 1)
    for y in range(140, 940, 60):
        line(c, 0, y, W, y, C('#3b5bdb', 0.10), 1)
    blobs = [(420, 420, 260, 170), (560, 720, 120, 190), (960, 380, 150, 110), (1010, 640, 140, 200), (1380, 420, 330, 180), (1560, 760, 110, 70)]
    r = random.Random(9)
    pts = []
    for bx, by, bw, bh in blobs:
        for i in range(int(bw * bh / 900)):
            a, d = r.uniform(0, 2 * math.pi), r.random() ** 0.5
            x, y = bx + math.cos(a) * bw * d, by + math.sin(a) * bh * d
            circle(c, x, y, 4, paint(C('#5c7cfa', 0.45)))
            pts.append((x, y, r.random()))
    k = seg(t, 0.5, T - 0.5)
    for x, y, th in pts:
        if th < k:
            circle(c, x, y, 6, paint('#ff3b30'))
            circle(c, x, y, 16, paint(C('#ff3b30', 0.2), blur=6))
    rect(c, 0, 0, W, 120, paint('#7a0c0c'))
    text(c, 'ПРОПАВШИЕ БЕЗ ВЕСТИ', 60, 82, 52, '#ffffff')
    n = int(lerp(1200, 1_480_000_000, k ** 3))
    text(c, f'{n:,}'.replace(',', ' '), W - 60, 82, 52, '#ffd21e', FONT_MONO, align='right')


def v_empty_flat(c, t, T, q):
    apartment_living(c, t, tv_on=False, night=False, lamp=False)
    # table with three plates, chair pushed back, a toy on the floor
    rect(c, 820, 760, 360, 20, paint('#5a4636'))
    for x in (870, 980, 1090):
        oval(c, x, 755, 40, 9, paint('#e8e8ec'))
    rrect(c, 1250, 900, 90, 70, 12, paint('#c0392b'))
    circle(c, 1270, 975, 12, paint('#222'))
    circle(c, 1320, 975, 12, paint('#222'))
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#1a1f33', 0.25)))


def v_empty_street(c, t, T, q):
    street(c, t, seed=41, dawn=True, cars=[(1300, 960, 0.8, '#5f6b7d', dict(door_open=True)), (420, 1000, 0.85, '#8c3b3b', dict(flip=True, door_open=True))])
    # paper flying
    for i in range(3):
        px = (t * 140 + i * 600) % (W + 200) - 100
        py = 900 + math.sin(t * 2 + i) * 40
        c.save()
        c.translate(px, py)
        c.rotate(t * 90 + i * 40)
        rect(c, -20, -14, 40, 28, paint('#d8d4c8'))
        c.restore()


def v_tv_static_close(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0b0a0d'))
    phase = seg(t, 0, T)
    if phase < 0.33:
        phone_screen(c, 760, 80, 400, 860, t, 'nosignal', time='03:14')
    elif phase < 0.66:
        tv(c, 160, 80, 1600, 900, True, 'static', t)
    else:
        rrect(c, 360, 200, 1200, 680, 20, paint('#e9edf3'))
        text(c, 'Нет подключения к интернету', 960, 520, 54, '#333a45', FONT_XB, align='center')
        circle(c, 960, 380, 60, paint('#9aa3b0', 'stroke', 10))
        line(c, 915, 335, 1005, 425, '#9aa3b0', 10)


def v_black_silence(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0b0a0d'))
    tv(c, 160, 80, 1600, 900, True, 'eas', t, 'ЧЁРНАЯ ТИШИНА', 'НЕ ИЗДАВАЙТЕ ЗВУКОВ')


def v_alex_recorder(c, t, T, q):
    apartment_living(c, t, tv_on=False, night=True, lamp=True)
    talk = max(q.talk(i, t) for i in range(3)) * 0.5
    alex(c, 900, 1330, 1.45, look=-0.15, mouth=talk, arms='recorder', item='recorder', t=t, eyes='normal')


def v_rules_title(c, t, T, q):
    black(c)
    a = seg(t, 0.3, 1.2)
    text(c, '15', W / 2, H / 2 + 60, 360, C('#ffd21e', a), align='center', stroke=24, stroke_col='#000000')
    text(c, 'ПРАВИЛ', W / 2, H / 2 + 200, 110, C('#ffffff', a), align='center')
    label(c, 'ЗАПОМНИ ИХ', W / 2, H / 2 + 240, 40, bg='#e53935', fg='#ffffff', angle=-2, alpha=seg(t, 1.0, 1.6), align='center')


def v_r1_one(c, t, T, q):
    courtyard_block(c, t, music_win=(5, 2))
    music_notes(c, 867, 360, t, 0.7)
    k = ease(seg(t, 0.5, 2.5))
    listener(c, 860, 1030, 0.42, turn=lerp(-0.8, 0.0, ease(seg(t, q.s(1), q.s(1) + 2.5))), tilt=lerp(0, -25, ease(seg(t, q.s(1), q.s(1) + 2.5))),
             t=t, glow=0.6, ripples=0.6, alpha=k)


def v_r1_after(c, t, T, q):
    courtyard_block(c, t, dark=True)
    listener(c, 860, 1030, 0.42, turn=0.0, tilt=-25, t=t, glow=0.5, dark=0.3)


def r2_facade(c, t, talk, creatures):
    courtyard_block(c, t, lit_windows={(5, 3): '#c9a65a'}, seed=12)
    wx, wy = 120 + 60 + 5 * 134, 60 + 50 + 3 * 125
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, 74, 80))
    person(c, wx + 37, wy + 150, 0.16, female=True, hairstyle='long', coat='#7a2d3b', hair='#2a1a10', arms='phone1', mouth=talk, t=t)
    c.restore()
    if talk > 0:
        sound_waves(c, wx + 37, wy + 40, t, 0.6)
    for i, (x, k) in enumerate(creatures):
        listener(c, x, 1040, 0.38, turn=clamp((wx - x) / 500, -1, 1) * 0.8, tilt=-28, t=t + i, glow=0.5, ripples=0.5, alpha=k)


def v_r2_a(c, t, T, q):
    r2_facade(c, t, 0.3 + 0.3 * abs(math.sin(t * 9)), [])
    V.card(c, t, 2)


def v_r2_b(c, t, T, q):
    stop = q.s(1) if len(q.L) > 1 else 3
    talk = 0.3 + 0.3 * abs(math.sin(t * 9)) if t < stop else 0.0
    r2_facade(c, t, talk, [(x, seg(t, q.s(2) + i * 0.6, q.s(2) + i * 0.6 + 1.0)) for i, x in enumerate((620, 900, 1200))])


def v_phone_silent(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#141626'))
    phone_screen(c, 760, 80, 400, 860, t, 'ok', time='22:40')
    k = ease(seg(t, 1.0, 1.6))
    rrect(c, 790, 420, 340, 120, 30, paint('#2a2f3b'))
    text(c, 'Без звука', 815, 495, 32, '#ffffff', FONT_XB)
    rrect(c, 1030, 455, 84, 50, 25, paint('#ff3b30' if k > 0.5 else '#5a606c'))
    circle(c, lerp(1055, 1089, k), 480, 21, paint('#ffffff'))
    # bell icon crossed
    circle(c, 960, 700, 60, paint('#ffffff', 'stroke', 8))
    line(c, 910, 650, 1010, 750, '#ff3b30', 10)
    oval(c, 1240, 900 - 30 * math.sin(t * 2), 120, 170, paint(SKIN))


def v_family_tv(c, t, T, q):
    apartment_living(c, t, tv_on=True, tv_mode='show', night=True)
    person(c, 330, 860, 0.55, coat='#5a3d55', hair='#3a2a1a', beard=True, look=0.9, mouth=0.0, t=t, tint='#b9b2d8')
    person(c, 560, 860, 0.52, female=True, hairstyle='long', coat='#7a2d3b', hair='#6b2f1a', look=0.9, mouth=0.0, t=t, tint='#b9b2d8')
    person(c, 760, 880, 0.38, female=True, hairstyle='ponytail', coat='#2c7be5', hair='#222', look=0.9, mouth=0.0, t=t, tint='#b9b2d8')


def v_tv_gather(c, t, T, q):
    courtyard_block(c, t, tv_win=(7, 3), seed=6)
    for i, x in enumerate((700, 980, 1250, 1460)):
        listener(c, x, 1040 - i % 2 * 20, 0.36, turn=clamp((1180 - x) / 500, -1, 1), tilt=-25, t=t + i, glow=0.4, ripples=0.4,
                 alpha=seg(t, 0.8 + i * 0.9, 1.8 + i * 0.9), walk=t * 0.5)


def v_tv_off_dark(c, t, T, q):
    off = t > 0.8
    apartment_living(c, t, tv_on=not off, tv_mode='show', night=True)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#05060a', 0.62 if off else 0.2)))
    person(c, 330, 860, 0.55, coat='#5a3d55', hair='#3a2a1a', beard=True, look=-0.6, mouth=0.4, t=t, tint='#6f7590', eyes='wide')
    person(c, 560, 860, 0.52, female=True, hairstyle='long', coat='#7a2d3b', hair='#6b2f1a', look=-0.8, mouth=0.0, arms='cover', t=t, tint='#6f7590', eyes='wide')
    listener(c, 120, 1100, 0.85, turn=0.6, tilt=-8, t=t, glow=0.9, dark=0.35, alpha=seg(t, 1.5, 3.5))


def v_walkie(c, t, T, q):
    q2 = Q([(0, 0), (0, T), (0, 0)])
    V.v_r7_walkie(c, t, T, q2)


def v_r8_all_turn(c, t, T, q):
    street(c, t, seed=91, lamps=((280, 1), (1500, -1)), fog_a=0.25)
    fog(c, t, 860, 0.25, n=7)
    snap = q.s(1) if len(q.L) > 1 else T * 0.6
    k = ease(seg(t, snap + 0.2, snap + 0.7))
    pts = [(260, 0.45), (520, 0.52), (800, 0.4), (1080, 0.5), (1350, 0.44), (1650, 0.5)]
    for i, (x, s) in enumerate(pts):
        listener(c, x, 900 + s * 120, s, turn=lerp((-0.3 if i % 2 else 0.3), clamp((960 - x) / 600, -1, 1), k), tilt=lerp(0, -10, k), t=t + i,
                 glow=0.4, ripples=k, dark=0.15, sway=1 - k)
    alex(c, 960, 1250, 0.95, look=0.0, mouth=0.0, t=t, arms='cover' if t > snap else 'tense', sweat=2 if t > snap else 0, tint=NIGHT_TINT)


def v_knock3(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0d0e12'))
    hits = (0.5, 1.2, 1.9)
    door(c, 760, 120, 400, 840, col='#3d434e', chain=True, peephole=True, knob='#aaa', shake=1.0 if any(abs(t - h) < 0.12 for h in hits) else 0, t=t)
    rect(c, 760, 955, 400, 8, paint(C('#ffffff', 0.25)))
    for i, h in enumerate(hits):
        if t > h:
            text(c, 'ТУК', 380, 400 + i * 120, 70, C('#ffffff', 0.2 + 0.6 * (1 - seg(t, h, h + 1.5))), align='center')


def v_alex_listen_window(c, t, T, q):
    kitchen(c, t, tv_on=False, night=True)
    alex(c, 560, 1150, 1.05, look=-0.9, mouth=0.0, t=t, arms='ear', sweat=1)
    sound_waves(c, 430, 260, t, 0.5)


def v_creature_fog(c, t, T, q):
    street(c, t, seed=51, dawn=True, lamps=((200, 1),), fog_a=0.4)
    fog(c, t, 820, 0.35, col='#d8dcea', n=9, speed=6)
    listener(c, 1000, 900, 0.55, turn=0.0, tilt=-6, t=t, alpha=seg(t, 0.3, 2.5), dark=0.1, glow=0.3, ripples=0.3)
    fog(c, t + 3, 860, 0.25, col='#d8dcea', n=6, speed=4, seed=9)


def v_shelter_msgs(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#141626'))
    circle(c, 960, 540, 700, paint(C('#4a6cff', 0.10), blur=120))
    msgs = [('Выжившие', 'Убежище в метро!', False), ('Неизвестный', 'Еда, вода, охрана', False),
            ('Неизвестный', 'Здесь безопасно', False)]
    n = 1 + int(seg(t, 0.5, 3.0) * 2.99)
    phone_screen(c, 760, 80, 400, 860, t, 'ok', lines=[(w, m[:24], mine) for w, m, mine in msgs[:n]], time='04:51')
    label(c, 'ЛОВУШКА?', 1250, 300, 44, bg='#e53935', fg='#ffffff', angle=-4, alpha=seg(t, T - 2.5, T - 2.0))


def v_walk_on(c, t, T, q):
    forest_road(c, t)
    person(c, 820, 1060, 0.62, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.0, mouth=0.0, t=t, walk=t * 0.6, tint=DARK_TINT)
    alex(c, 1060, 1080, 0.64, look=0.0, mouth=0.0, t=t, walk=t * 0.6, tint=DARK_TINT)


def v_r14_a(c, t, T, q):
    q2 = Q([(0, 0), (1.0, 6.0)])
    V.v_r14_convoy(c, t, T, q2)


def v_r15_door(c, t, T, q):
    V.v_door_knock2(c, t, T, q)
    sound_waves(c, 1300, 520, t, 0.6, dirn=-1)


def v_own_voice2(c, t, T, q):
    office(c, t, lamp_on=True)
    alex(c, 900, 1300, 1.35, look=1.0, mouth=0.1, eyes='wide', t=t, arms='cover', sweat=2, tint='#b4b9cc')
    sound_waves(c, 1500, 500, t, 0.6, dirn=-1)


def v_doc_wave(label_txt, talk_all=True):
    def d(c, t, T, q):
        c.drawRect(skia.Rect.MakeWH(W, H), paint('#08090b'))
        talking = any(q.talk(i, t) for i in range(len(q.L))) if not talk_all else True
        for i in range(120):
            x = 160 + i * 13.5
            h = 10 + abs(math.sin(i * 0.7 + t * 9)) * (150 if talking else 10) * (0.5 + 0.5 * abs(math.sin(i * 0.13 + t)))
            rrect(c, x, 540 - h / 2, 8, h, 4, paint(C('#3fe07a', 0.9)))
        text(c, label_txt, 160, 300, 46, '#3fe07a', FONT_MONO)
        text(c, f'▶ 00:{int(t):02d}', 160, 800, 40, C('#3fe07a', 0.7), FONT_MONO)
    return d


def v_date2014(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0d0e10'))
    rrect(c, 360, 240, 1200, 600, 30, paint('#24452f'))
    rrect(c, 380, 260, 1160, 560, 24, paint('#3fe07a'))
    text(c, 'ДАТА ЗАПИСИ:', 960, 420, 70, '#0d2a16', FONT_MONO, align='center')
    text(c, '14.03.2014', 960, 600, 170, C('#0d2a16', seg(t, 0.8, 1.2)), FONT_MONO, align='center')
    text(c, '12 ЛЕТ НАЗАД', 960, 740, 50, C('#0d2a16', seg(t, 2.0, 2.4)), FONT_MONO, align='center')


def v_alex_dark(c, t, T, q):
    lab(c, t, lamp=0.35)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.45)))
    turn = ease(seg(t, q.s(1) if len(q.L) > 1 else T, T)) if False else 0.0
    alex(c, 820, 1420, 1.6, look=0.0, mouth=0.0, t=t, arms='recorder', item='recorder', sweat=1, tint='#7f879f', eyes='wide')


def v_alex_turn(c, t, T, q):
    lab(c, t, lamp=0.35)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.5)))
    k = ease(seg(t, 0.5, T - 0.5))
    alex(c, 820, 1420, 1.6, look=lerp(0.0, 1.0, k), mouth=0.3 * k, t=t, sweat=2, tint='#7f879f', eyes='wide', arms='tense')


def v_hold_creature(c, t, T, q):
    corridor(c, t, flicker=1.0, col='#0b0c10', wall='#14161c', floor='#0a0b0d', ceil='#0c0d10')
    listener(c, 960, 1080, 0.88, turn=0.0, t=t, glow=0.9, dark=0.25, sway=0.2)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.25 + 0.6 * seg(t, T - 2.5, T))))


def v_question(c, t, T, q):
    black(c)
    a = seg(t, 0.5, 1.5)
    text(c, 'КТО БЫЛ ПЕРВЫМ', W / 2, H / 2 - 40, 96, C('#ffffff', a), align='center')
    text(c, 'СЛУШАЮЩИМ?', W / 2, H / 2 + 80, 96, C('#ffd21e', a), align='center')
    text(c, 'Напиши свою версию в комментариях', W / 2, H - 140, 36, C('#9aa0aa', seg(t, 3, 4)), FONT_XB, align='center')


def v_end2(c, t, T, q):
    black(c)
    a = seg(t, 0.8, 2.0)
    text(c, 'СЛУШАЮЩИЕ ВЕРНУТСЯ', W / 2, H / 2 + 10, 96, C('#ffffff', a), align='center')
    text(c, 'THE LISTENERS WILL RETURN', W / 2, H / 2 + 90, 36, C('#e53935', seg(t, 2.5, 3.5)), FONT_XB, align='center')


def v_title2(c, t, T, q):
    black(c)
    a = seg(t, 0.4, 1.6) * (1 - seg(t, T - 1.0, T - 0.2))
    listener(c, 1440, 1150, 1.25, turn=-0.25, t=t, glow=1.0, dark=0.2, alpha=a * 0.9)
    text(c, 'THE LISTENERS · ЭПИЗОД 01', 120, 330, 38, C('#e53935', a), FONT_XB)
    text(c, '15 ПРАВИЛ,', 110, 470, 130, C('#ffd21e', a), stroke=14, stroke_col='#000000')
    text(c, 'ЧТОБЫ ВЫЖИТЬ', 110, 600, 110, C('#ffffff', a))
    text(c, 'СРЕДИ СЛУШАЮЩИХ', 114, 690, 64, C('#ffffff', a * 0.8), FONT_XB)


# ===================================================================== SCRIPT (client text)

# ---- intro
sc(1, 1, [('W', 'Представь, что однажды ты просыпаешься и понимаешь: мир больше не принадлежит людям.')],
   V.v_cold_open, amb='drone_room', mus='dread', sfx=[(0.2, 'tape_click', 0.8), (0.4, 'tape_hiss', 0.4)], min_dur=8, cam=(1.0, 1.18, 960, 520), fade_in=1.0,
   prompt='Dark corridor, flickering light, a tall white faceless figure far away. Slow push-in.')
sc(2, 1, [], v_title2, mus='title', sfx=[(0.3, 'boom', 1.0), (0.35, 'stinger', 0.7)], min_dur=6.0, cam=(1.0, 1.05, 700, 500),
   prompt='Title card: 15 ПРАВИЛ, ЧТОБЫ ВЫЖИТЬ СРЕДИ СЛУШАЮЩИХ.')
sc(3, 1, [('N', 'Пять дней назад всё было как обычно. Люди ходили на работу, дети учились в школах, машины стояли в пробках.')],
   v_normal_city, amb='city_dawn', mus='calm', sfx=[(0.5, 'birds', 0.3), (0.0, 'engine_idle', 0.15)], min_dur=8, cam=(1.0, 1.06, 960, 600),
   prompt='Normal busy city day: cars, people walking, birds. People fade away at the end.')
sc(4, 1, [('N', 'Но затем по всему миру начали исчезать люди.')],
   v_missing_news, amb='lab_hum', mus='tense', sfx=[(0.5, 'riser', 0.5)], min_dur=7, cam=(1.0, 1.06, 960, 60),
   prompt='World map, red dots of missing people spreading, counter ПРОПАВШИЕ БЕЗ ВЕСТИ.')
sc(5, 1, [('N', 'Сначала пропадали целые семьи.')],
   v_empty_flat, amb='room_dawn', mus='tense', sfx=[], min_dur=5.5, cam=(1.0, 1.08, 960, 600),
   prompt='Empty family apartment: plates on the table, a toy car on the floor, nobody home.')
sc(6, 1, [('N', 'Потом опустели улицы.')],
   v_empty_street, amb='city_dawn', mus='tense', sfx=[], min_dur=5.5, cam=(1.06, 1.0, 960, 560),
   prompt='Empty grey street, abandoned cars with open doors, papers blowing.')
sc(7, 1, [('N', 'А вскоре перестали работать телефоны, телевидение и интернет.')],
   v_tv_static_close, amb='room_dawn', mus='tense', sfx=[(0.3, 'error_beep', 0.4), (2.2, 'static', 0.5)], min_dur=6.5, cam=(1.0, 1.06, 960, 520),
   prompt='Montage: phone НЕТ СЕТИ, TV static, browser no-connection page.')
sc(8, 1, [('N', 'Власти назвали это событие «Чёрной тишиной».')],
   v_black_silence, amb='room_dawn', mus='dread', sfx=[(0.0, 'eas_tone', 0.35)], min_dur=6, cam=(1.0, 1.1, 960, 540),
   prompt='Emergency broadcast: ЧЁРНАЯ ТИШИНА.')
sc(9, 1, [('N', 'Причиной стал неизвестный организм под названием N-0.')],
   V.v_n0, amb='lab_hum', mus='doc', sfx=[(0.3, 'bubble', 0.3)], min_dur=6.5, cam=(1.0, 1.1, 960, 520),
   prompt='Microscope view: red cells turning white. N-0.')
sc(10, 1, [('N', 'Он изменил людей. Но не превратил их в обычных монстров.'), ('W', 'Они стали совершенно другими.')],
   V.v_first_sight, amb='city_dawn', mus='dread', sfx=[(0.6, 'riser', 0.5), ('L1+0.3', 'stinger', 0.6), (3.2, 'porcelain', 0.4)], min_dur=8,
   cam=(1.0, 1.12, 1150, 500), prompt='Over-the-shoulder: Alex, a white faceless figure appears in the fog at the end of the street.')
sc(11, 1, [('N', 'Их тела белые, гладкие, словно сделанные из керамики.'), ('N', 'У них нет глаз, носа и рта.')],
   V.v_dossier, amb='room_night', mus='doc', sfx=[(0.2, 'paper', 0.6), (1.0, 'stamp', 0.5)], min_dur=8, cam=(1.0, 1.08, 960, 520),
   prompt='Classified dossier N-0 with photo of the creature and anatomy notes.')
sc(12, 1, [('N', 'Они не видят тебя.'), ('W', 'Но слышат даже самые тихие звуки.')],
   V.v_blind, amb='city_night', mus='tense', sfx=[(0.5, 'footsteps_soft', 0.3)], min_dur=7, cam=(1.0, 1.1, 1100, 560),
   prompt='A survivor tiptoes past a motionless white creature that cannot see him.')
sc(13, 1, [('N', 'Их называют Слушающими.')],
   V.v_anatomy, amb='lab_hum', mus='doc', sfx=[(0.5, 'porcelain', 0.5)], min_dur=7, cam=(1.0, 1.05, 960, 500),
   prompt='Blueprint diagram of the Listener, head slowly turning.')
sc(14, 1, [('N', 'Я — Алекс. Мне шестнадцать лет.'), ('W', 'И если ты слышишь эту запись, возможно, ты ещё можешь выжить.')],
   v_alex_recorder, amb='room_night', mus='calm', sfx=[(0.1, 'tape_click', 0.6)], min_dur=8, cam=(1.0, 1.08, 900, 450),
   prompt='Alex, 16, at night by lamp light, speaks into a dictaphone.')
sc(15, 1, [('N', 'Но для этого нужно запомнить пятнадцать правил.')],
   v_rules_title, mus='dread', sfx=[(0.3, 'boom', 0.8)], min_dur=5.5, cam=(1.0, 1.05, 960, 540), prompt='Card: 15 ПРАВИЛ.')

# ---- rule 1
sc(16, 2, [('N', 'Правило первое. Никогда не включай громкую музыку.'),
           ('N', 'Один парень решил, что в пустом городе ему больше нечего бояться. Он включил музыку на полную громкость.')],
   V.v_r1_courtyard, amb='city_night', mus='silence', sfx=[(0.0, 'music_loud', 0.5)], min_dur=10, cam=(1.0, 1.12, 900, 400),
   prompt='Night courtyard, one window flashes with party lights, loud music.')
sc(17, 2, [('N', 'Через несколько секунд за окном появилась белая фигура.'), ('W', 'Она медленно повернула голову в сторону квартиры.')],
   v_r1_one, amb='city_night', mus='tense', sfx=[(0.0, 'music_loud', 0.4), ('L1+0.5', 'porcelain', 0.6)], min_dur=9, cam=(1.0, 1.15, 870, 600),
   prompt='A single white figure appears under the window and slowly turns its head up toward the music.')
sc(18, 2, [('W', 'После этого музыка больше не играла.')],
   v_r1_after, amb='city_night', mus='silence', sfx=[(0.0, 'glass', 0.5)], min_dur=6, cam=(1.06, 1.0, 900, 560),
   prompt='Silence: dark window, the creature stands still below.')
nb_insert(1)

# ---- rule 2
sc(19, 2, [('N', 'Правило второе. Не разговаривай возле открытых окон.'), ('N', 'Даже обычный разговор может привлечь их внимание.')],
   v_r2_a, amb='city_night', mus='calm', sfx=[], min_dur=8, cam=(1.5, 1.9, 887, 470),
   prompt='Apartment facade at night, a woman talks on the phone in a lit open window.')
sc(20, 2, [('N', 'Однажды женщина разговаривала по телефону возле окна.'), ('W', 'Она услышала странный звук снизу и замолчала.'),
           ('W', 'Но было уже поздно. На улице стояли сразу три Слушающих.')],
   v_r2_b, amb='city_night', mus='tense', sfx=[('L1+0.0', 'porcelain', 0.6), ('L2+1.2', 'stinger', 0.5)], min_dur=12, cam=(1.3, 1.05, 887, 700),
   prompt='The woman stops talking; three white creatures stand below the window with heads tilted up.')
nb_insert(2)

# ---- rule 3
sc(21, 2, [('N', 'Правило третье. Не открывай дверь, если слышишь знакомый голос.')],
   V.v_r3_knock, amb='room_night', mus='tense', sfx=[(0.5, 'knock', 0.9)], min_dur=7, cam=(1.0, 1.06, 960, 500), lead=1.8,
   prompt='The front door shakes from knocking, Alex freezes.')
sc(22, 2, [('N', 'Они могут повторять человеческую речь.'), ('N', 'Иногда они используют голоса людей, которых ты знаешь.')],
   V.v_r3_mom2, amb='room_night', mus='dread', sfx=[(0.3, 'knock_soft', 0.4)], min_dur=8, cam=(1.04, 1.0, 900, 520),
   prompt='Alex backs away from the door covering his mouth.')
sc(23, 2, [('N', 'Неважно, насколько знакомо звучит голос за дверью.'), ('W', 'Не открывай.')],
   V.v_r3_peep, amb='room_night', mus='dread', sfx=[('L1+0.6', 'stinger', 0.8)], min_dur=7, cam=(1.0, 1.1, 960, 540),
   prompt='Fisheye peephole view: smooth white eyeless face.')
nb_insert(3)

# ---- rule 4
sc(24, 2, [('N', 'Правило четвёртое. Отключи звуковые уведомления телефона.')],
   V.v_r4_store, amb='store', mus='tense', sfx=[(0.5, 'creature_step', 0.3), (2.0, 'creature_step', 0.3)], min_dur=7, cam=(1.0, 1.1, 900, 600),
   prompt='Supermarket at night, a white creature walks between shelves, Alex hides.')
sc(25, 2, [('W', 'Сообщение, звонок или случайный сигнал могут выдать твоё местоположение.')],
   V.v_r4_phone, amb='store', mus='silence', sfx=[(0.6, 'low_batt', 0.9)], min_dur=6, cam=(1.0, 1.1, 960, 540), lead=1.6,
   prompt='Phone screen: notification beep.')
sc(26, 2, [],
   V.v_r4_turn, amb='store', mus='action', sfx=[(0.4, 'porcelain', 0.7), (3.0, 'creature_rush', 0.8), (3.2, 'run', 0.7), (4.5, 'shelf_crash', 0.7)], min_dur=6,
   cam=(1.0, 1.08, 800, 600), prompt='The creature snaps its head toward Alex and lunges; Alex runs.')
sc(27, 2, [('N', 'Переведи телефон в беззвучный режим и не забывай об этом.')],
   v_phone_silent, amb='room_night', mus='calm', sfx=[(1.1, 'tap', 0.6)], min_dur=6, cam=(1.0, 1.06, 960, 520),
   prompt='Phone: silent mode switched on.')
nb_insert(4)

# ---- rule 5
sc(28, 2, [('N', 'Правило пятое. Не оставляй телевизор включённым.')],
   V.v_r5_tvwin, amb='city_night', mus='calm', sfx=[(0.0, 'tv_far', 0.3)], min_dur=6.5, cam=(1.0, 1.2, 1100, 480),
   prompt='Apartment block at night, one window flickers with TV light.')
sc(29, 2, [('N', 'Одна семья решила использовать телевизор, чтобы заглушить страх.')],
   v_family_tv, amb='room_night', mus='calm', sfx=[(0.0, 'tv_show', 0.4)], min_dur=6.5, cam=(1.0, 1.06, 900, 600),
   prompt='A family sits on the sofa watching TV loudly at night.')
sc(30, 2, [('N', 'Но звук привлёк существ к их дому.')],
   v_tv_gather, amb='city_night', mus='tense', sfx=[(0.0, 'tv_far', 0.3), (1.0, 'crowd_shuffle', 0.5)], min_dur=7, cam=(1.0, 1.08, 1000, 600),
   prompt='White creatures gather in the courtyard under the flickering TV window.')
sc(31, 2, [('W', 'Когда экран погас, в комнате уже было слышно чужое дыхание.')],
   v_tv_off_dark, amb='room_night', mus='silence', sfx=[(0.8, 'tv_on', 0.4), (1.6, 'breath', 0.6), (2.6, 'porcelain', 0.5)], min_dur=7.5, lead=1.2,
   cam=(1.0, 1.1, 600, 560), prompt='TV goes dark; in the gloom a white figure stands behind the frightened family.')
nb_insert(5)

# ---- rule 6
sc(32, 3, [('N', 'Правило шестое. Не отвечай на голоса с улицы.')],
   V.v_r6_window_night, amb='city_night', mus='tense', sfx=[], min_dur=6, cam=(1.0, 1.12, 960, 800),
   prompt='Dark courtyard at midnight, nobody visible.')
sc(33, 3, [('N', 'Они могут звать на помощь. Могут просить открыть дверь.')],
   V.v_r6_alex, amb='room_night', mus='dread', sfx=[], min_dur=7, cam=(1.0, 1.1, 520, 500),
   prompt='Alex grips the window handle, hesitating.')
sc(34, 3, [('W', 'Но ты не знаешь, кто на самом деле стоит снаружи.')],
   V.v_r6_reveal, amb='city_night', mus='dread', sfx=[(0.3, 'porcelain', 0.4)], min_dur=7, cam=(1.0, 1.15, 960, 380),
   prompt='Under a streetlight a single white creature tilts its head up toward the windows.')
nb_insert(6)

# ---- rule 7
sc(35, 3, [('N', 'Правило седьмое. Не доверяй голосам, которые знают твоё имя.')],
   v_walkie, amb='room_night', mus='tense', sfx=[(0.5, 'radio_static', 0.5)], min_dur=7, cam=(1.0, 1.1, 960, 540),
   prompt='Close-up: a walkie-talkie, channel 7, static.')
sc(36, 3, [('N', 'Они запоминают услышанное.'), ('W', 'И чем дольше ты находишься рядом с ними, тем лучше они умеют копировать людей.')],
   V.v_r7_think, amb='room_night', mus='dread', sfx=[(0.0, 'radio_static', 0.25)], min_dur=8, cam=(1.0, 1.12, 960, 450),
   prompt='Close-up: Alex in lamp light, scared.')
nb_insert(7)

# ---- rule 8
sc(37, 3, [('N', 'Правило восьмое. Не считай тишину признаком безопасности.')],
   V.v_r8_stairs, amb='stairs', mus='tense', sfx=[(3.0, 'door_creak', 0.5)], min_dur=7, cam=(1.0, 1.06, 700, 600),
   prompt='Dim stairwell, Alex steps out carefully.')
sc(38, 3, [('N', 'Иногда Слушающие просто стоят неподвижно.'), ('W', 'Ты можешь пройти мимо и даже не заметить их.')],
   V.v_r8_reveal, amb='stairs', mus='dread', sfx=[('L1+1.0', 'stinger', 0.6)], min_dur=8, cam=(1.0, 1.12, 1100, 500), lead=1.0,
   prompt='Reveal: a white creature stands motionless on the landing below.')
sc(39, 3, [('W', 'Но стоит издать звук —'), ('W', 'и они повернутся одновременно.')],
   v_r8_all_turn, amb='city_night', mus='silence', sfx=[('L1+0.2', 'porcelain', 0.9), ('L1+0.25', 'hit', 0.7)], min_dur=7.5, gap=0.9,
   cam=(1.0, 1.1, 960, 560), prompt='A foggy street full of motionless creatures; at a sound all heads snap toward Alex at once.')
nb_insert(8)

# ---- rule 9
sc(40, 3, [('N', 'Правило девятое. Не игнорируй странные звуки.')],
   V.v_r9_vent, amb='room_night', mus='tense', sfx=[(1.0, 'vent_tick', 0.5)], min_dur=6.5, cam=(1.0, 1.1, 1100, 400),
   prompt='Bedroom at night, vent grille on the wall, ticking.')
sc(41, 3, [('N', 'Если ты услышал три одинаковых удара, а потом наступила тишина, не пытайся выяснить, что произошло.')],
   v_knock3, amb='room_night', mus='silence', sfx=[(0.45, 'knock3', 0.9)], min_dur=9, lead=2.8,
   cam=(1.0, 1.12, 960, 500), prompt='A door; three identical knocks, then silence.')
sc(42, 3, [('W', 'Возможно, кто-то уже заметил тебя.')],
   V.v_r3_mom2, amb='room_night', mus='dread', sfx=[(0.3, 'heartbeat', 0.5)], min_dur=6, cam=(1.0, 1.1, 1200, 520),
   prompt='Alex backs away from the door, covering his mouth.')
nb_insert(9)

# ---- rule 10
sc(43, 3, [('N', 'Правило десятое. Помни: они запоминают услышанное.')],
   V.v_r10_hospital, amb='hospital', mus='tense', sfx=[(0.3, 'footsteps_soft', 0.3)], min_dur=7, cam=(1.0, 1.1, 960, 520),
   prompt='Dark corridor, Alex walks with a flashlight.')
sc(44, 3, [('N', 'Однажды я услышал голос своего друга.'), ('FRIEND', 'Алекс, ты где? Алекс, ты где?'),
           ('W', 'Он повторял одну и ту же фразу, снова и снова.')],
   v_alex_listen_window, amb='room_night', mus='dread', sfx=[], min_dur=10, cam=(1.0, 1.1, 600, 480),
   prompt='Alex listens at a dark window; a friend\'s voice repeats the same phrase outside.')
sc(45, 3, [('W', 'Но мой друг исчез ещё три дня назад.')],
   v_creature_fog, amb='city_dawn', mus='dread', sfx=[(0.2, 'porcelain', 0.5), (1.5, 'stinger', 0.5)], min_dur=7, cam=(1.0, 1.15, 1000, 450),
   prompt='A white figure in the fog, standing where the friend\'s voice came from.')
nb_insert(10)

# ---- rule 11
sc(46, 4, [('N', 'Правило одиннадцатое. Не доверяй каждому сообщению об убежищах.'), ('N', 'В интернете появлялись сообщения о безопасных местах.')],
   with_card(v_shelter_msgs, 11), amb='room_night', mus='tense', sfx=[(0.8, 'tap', 0.5), (1.7, 'tap', 0.5), (2.6, 'tap', 0.5)], min_dur=9,
   cam=(1.0, 1.06, 960, 520), prompt='Phone chat with messages about a shelter at metro Северная.')
sc(47, 4, [('W', 'Но некоторые из них были ловушками.')],
   V.v_metro_stairs, amb='subway', mus='tense', sfx=[(0.5, 'footsteps_soft', 0.35)], min_dur=6.5, cam=(1.0, 1.08, 960, 700),
   prompt='Survivors descend a stopped metro escalator.')
sc(48, 4, [('N', 'Никогда не отправляйся туда, не проверив информацию.')],
   V.v_metro_platform, amb='subway', mus='dread', sfx=[(0.5, 'crowd_shuffle', 0.5)], min_dur=8, cam=(1.18, 1.0, 960, 500),
   prompt='Metro platform full of motionless white creatures under a loudspeaker.')
nb_insert(11)

# ---- rule 12
sc(49, 4, [('N', 'Правило двенадцатое. Не отделяйся от людей, которым доверяешь.')],
   V.v_r12_forest, amb='forest', mus='calm', sfx=[(0.3, 'footsteps_forest', 0.4)], min_dur=7, cam=(1.0, 1.06, 960, 700),
   prompt='Night forest road, three survivors walk together.')
sc(50, 4, [('W', 'В одиночку гораздо сложнее понять, откуда доносится звук.')],
   V.v_r12_voice, amb='forest', mus='dread', sfx=[(0.5, 'branch', 0.4), (3.0, 'porcelain', 0.4)], min_dur=7, cam=(1.0, 1.1, 1200, 600),
   prompt='Alex and Mira freeze; a white shape between the trees.')
sc(51, 4, [('N', 'Но даже в группе нельзя забывать о правилах.')],
   v_walk_on, amb='forest', mus='calm', sfx=[(0.3, 'footsteps_forest', 0.35)], min_dur=6, cam=(1.0, 1.06, 960, 700),
   prompt='Alex and Mira walk on silently.')
nb_insert(12)

# ---- rule 13
sc(52, 4, [('N', 'Правило тринадцатое. Не игнорируй экстренные предупреждения.'),
           ('N', 'Если по радио передают сообщение об эвакуации, внимательно слушай.')],
   V.v_r13_car_radio, amb='car_inside', mus='tense', sfx=[(0.2, 'radio_static', 0.35), (3.5, 'eas_tone', 0.3)], min_dur=9,
   cam=(1.0, 1.06, 960, 600), prompt='Inside an abandoned car: emergency message on the car radio.')
sc(53, 4, [('W', 'Возможно, это последнее предупреждение, которое ты получишь.')],
   V.v_r13_siren, amb='forest', mus='hope', sfx=[(1.0, 'engine_far', 0.4)], min_dur=7, cam=(1.0, 1.12, 960, 650),
   prompt='Dawn: floodlights of an evacuation convoy ahead.')
nb_insert(13)

# ---- rule 14
sc(54, 4, [('N', 'Правило четырнадцатое. Не возвращайся за вещами во время эвакуации.')],
   v_r14_a, amb='convoy', mus='tense', sfx=[(0.0, 'engine_idle', 0.4)], min_dur=7.5, cam=(1.0, 1.05, 960, 600),
   prompt='Evacuation convoy; a man runs back for his suitcase.')
sc(55, 4, [('N', 'Никакая вещь не стоит того, чтобы рисковать жизнью.')],
   V.v_r14_wheels, amb='convoy', mus='action', sfx=[(0.0, 'wheels', 0.6), (2.5, 'crowd_shuffle', 0.5)], min_dur=7.5, cam=(1.0, 1.05, 960, 600),
   prompt='The man drags a rattling suitcase; white creatures emerge from the fog.')
sc(56, 4, [('N', 'Если пришлось покинуть убежище, продолжай двигаться дальше.')],
   v_walk_on, amb='forest', mus='sad', sfx=[(0.3, 'footsteps_forest', 0.35)], min_dur=7, cam=(1.0, 1.08, 960, 650),
   prompt='Alex and Mira keep walking along the night road.')
nb_insert(14)

# ---- rule 15
sc(57, 5, [('N', 'И наконец, правило пятнадцатое.')],
   V.v_rule15, amb='room_night', mus='dread', sfx=[(0.2, 'boom', 0.8)], min_dur=6, cam=(1.0, 1.05, 960, 540),
   prompt='Rule 15 card; Alex and Mira cover their mouths in darkness.')
sc(58, 5, [('W', 'Если однажды ты услышишь собственный голос снаружи, никогда не отвечай.')],
   v_r15_door, amb='room_night', mus='dread', sfx=[(0.3, 'knock_soft', 0.5)], min_dur=8, cam=(1.0, 1.12, 960, 500),
   prompt='The door from inside; thin shadows under it; a voice outside.')
sc(59, 5, [('W', 'Потому что это означает, что они уже достаточно долго наблюдают за тобой.')],
   v_own_voice2, amb='room_night', mus='dread', sfx=[(1.0, 'scratch', 0.4)], min_dur=8, cam=(1.0, 1.15, 950, 380),
   prompt='Close-up: Alex covers his mouth, terrified, a voice behind the door.')
nb_insert(15)

# ---- final
sc(60, 6, [('N', 'Я думал, что знаю все правила. Но сегодня я нашёл кое-что странное.')],
   V.v_inst_ext, amb='wind', mus='dread', sfx=[(1.0, 'gate_creak', 0.5)], min_dur=8, cam=(1.12, 1.0, 960, 360), fade_in=0.6,
   prompt='Night: an abandoned research institute behind a fence.')
sc(61, 6, [('N', 'В заброшенном исследовательском центре лежал старый диктофон.'), ('N', 'Внутри была запись доктора Марка.')],
   V.v_basement, amb='lab_hum', mus='tense', sfx=[(0.3, 'footsteps_soft', 0.35), (3.0, 'drip', 0.3)], min_dur=9, cam=(1.0, 1.1, 1000, 600),
   prompt='Basement acoustic lab; flashlight reveals an old dictaphone.')
sc(62, 6, [('N', 'Он говорил, что Слушающие появились не пять дней назад.'), ('W', 'Они существовали задолго до катастрофы.')],
   v_doc_wave('ЗАПИСЬ: Д-Р МАРК'), amb='lab_hum', mus='dread', sfx=[(0.0, 'tape_hiss', 0.5), (0.0, 'tape_click', 0.7)], min_dur=8,
   cam=(1.0, 1.08, 960, 540), prompt='Black screen, green waveform: Dr. Mark\'s recording.')
sc(63, 6, [('W', 'Запись была сделана двенадцать лет назад.')],
   v_date2014, amb='lab_hum', mus='dread', sfx=[(0.9, 'stinger', 0.7)], min_dur=6.5, cam=(1.0, 1.12, 960, 520),
   prompt='Dictaphone display: recording date — twelve years ago.')
sc(64, 6, [('N', 'Но самое странное произошло дальше.')],
   V.v_recorder_close, amb='lab_hum', mus='silence', sfx=[(1.1, 'tape_click', 0.9), (1.3, 'tape_hiss', 0.5)], min_dur=6, cam=(1.0, 1.1, 960, 450),
   prompt='Dictaphone close-up, the play button presses itself.')
sc(65, 6, [('N', 'Диктофон неожиданно воспроизвёл мой голос.'), ('MIMA', 'Алекс, не слушай следующую запись.')],
   v_doc_wave('ФАЙЛ 002'), amb='lab_hum', mus='silence', sfx=[(0.0, 'tape_hiss', 0.5)], min_dur=8, gap=0.9, tail=1.6,
   cam=(1.0, 1.08, 960, 540), prompt='Waveform: the recorder plays Alex\'s own voice.')
sc(66, 6, [('W', 'Я никогда не произносил этих слов.')],
   v_alex_dark, amb='lab_hum', mus='dread', sfx=[(0.2, 'heartbeat', 0.5)], min_dur=6, cam=(1.0, 1.08, 820, 450),
   prompt='Close-up: Alex in the dark lab holding the dictaphone.')
sc(67, 6, [('W', 'А потом за моей спиной кто-то тихо сказал:'), ('MIMW', 'Алекс…')],
   v_alex_dark, amb='drone_room', mus='silence', sfx=[], min_dur=6.5, gap=1.0, tail=1.5, cam=(1.0, 1.12, 820, 400),
   prompt='Alex freezes as someone whispers his name behind him.')
sc(68, 6, [('W', 'Я медленно повернул голову.')],
   v_alex_turn, amb='drone_room', mus='silence', sfx=[(0.2, 'heartbeat', 0.6)], min_dur=5.5, cam=(1.0, 1.06, 820, 450),
   prompt='Alex slowly turns his head.')
sc(69, 6, [('W', 'В конце коридора стояла белая фигура.'), ('W', 'Она повернула голову прямо ко мне.')],
   V.v_final_corridor, amb='drone_room', mus='dread', sfx=[(3.0, 'porcelain', 0.7), ('L1+1.4', 'riser', 0.6)], min_dur=10,
   cam=(1.0, 1.35, 960, 420), tail=1.6, prompt='Dark flickering corridor, the white creature slowly turns its head toward camera; slow push-in.')
sc(70, 6, [('N', 'И теперь я не знаю, кто записал мой голос двенадцать лет назад.')],
   v_hold_creature, amb='drone_room', mus='dread', sfx=[], min_dur=7, cam=(1.0, 1.1, 960, 300),
   prompt='Hold on the creature in the corridor, fade to black.')
sc(71, 6, [('N', 'Как думаешь, кто был первым Слушающим — и почему они знали обо мне ещё до моего рождения?')],
   v_question, mus='end', sfx=[(0.0, 'hit', 0.9)], min_dur=8, prompt='Black: КТО БЫЛ ПЕРВЫМ СЛУШАЮЩИМ?')
sc(72, 6, [], v_end2, mus='end', sfx=[(0.5, 'boom', 0.7)], min_dur=6, fade_out=1.5,
   prompt='Black: СЛУШАЮЩИЕ ВЕРНУТСЯ / THE LISTENERS WILL RETURN.')

# number scenes sequentially (nb inserts get real ids)
for i, s in enumerate(SCENES, 1):
    s['id'] = i
