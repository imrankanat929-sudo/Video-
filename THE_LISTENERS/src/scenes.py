"""THE LISTENERS — Episode 01 — 15 правил, чтобы выжить.
Screenplay + per-scene visuals. Each scene: narration lines, visuals, ambience, music, sfx.

Speakers:
  N   narrator, low calm documentary voice
  W   narrator whispering (tense moments)
  A   Alex whispering
  AN  Alex, quiet normal voice
  MOM creature imitating mother (female voice, distorted)
  MIMA creature imitating Alex (Alex voice, distorted)
  TV  emergency broadcast / radio
  MIRA Mira (whisper)
  VIK Viktor (whisper)
  MAN stranger shouting
"""
from gfx import *
from envs import *


class Q:
    """cue info passed to visuals: L[i] = (start, end) of VO line i in scene time"""
    def __init__(self, L):
        self.L = L

    def s(self, i):
        return self.L[i][0] if i < len(self.L) else 0

    def e(self, i):
        return self.L[i][1] if i < len(self.L) else 0

    def talk(self, i, t):
        """mouth movement while line i is spoken"""
        if i >= len(self.L):
            return 0.0
        a, b = self.L[i]
        if a <= t <= b:
            return 0.25 + 0.35 * abs(math.sin(t * 13))
        return 0.0


SCENES = []


def sc(id_, part, vo, draw, amb='none', mus='calm', sfx=(), min_dur=6.0, cam=None, fade_in=0.0, fade_out=0.0,
       lead=0.55, tail=0.85, gap=0.38, title=None, prompt=''):
    SCENES.append(dict(id=id_, part=part, vo=list(vo), draw=draw, amb=amb, mus=mus, sfx=list(sfx), min_dur=min_dur,
                       cam=cam, fade_in=fade_in, fade_out=fade_out, lead=lead, tail=tail, gap=gap, title=title, prompt=prompt))


RULES = [
    'Никогда не включай громкую музыку.',
    'Не разговаривай возле открытых окон.',
    'Не открывай дверь на знакомый голос.',
    'Отключи все звуки телефона.',
    'Не оставляй телевизор включённым.',
    'Не отвечай на голоса с улицы.',
    'Не верь голосу, который знает твоё имя.',
    'Тишина — не значит безопасность.',
    'Не игнорируй странные звуки.',
    'Они запоминают всё, что слышат.',
    'Не верь каждому сообщению об убежище.',
    'Держись людей, которым доверяешь.',
    'Не игнорируй экстренные предупреждения.',
    'Не возвращайся за вещами.',
    'Не отвечай своему голосу.',
]

RULE_TITLES = [
    'НЕ ВКЛЮЧАЙ\nГРОМКУЮ МУЗЫКУ',
    'НЕ ГОВОРИ\nУ ОТКРЫТЫХ ОКОН',
    'НЕ ОТКРЫВАЙ\nНА ЗНАКОМЫЙ ГОЛОС',
    'ВЫКЛЮЧИ ЗВУК\nТЕЛЕФОНА',
    'НЕ ОСТАВЛЯЙ\nТЕЛЕВИЗОР',
    'НЕ ОТВЕЧАЙ\nГОЛОСАМ С УЛИЦЫ',
    'ОН ЗНАЕТ\nТВОЁ ИМЯ',
    'ТИШИНА —\nНЕ БЕЗОПАСНОСТЬ',
    'НЕ ИГНОРИРУЙ\nСТРАННЫЕ ЗВУКИ',
    'ОНИ\nЗАПОМИНАЮТ',
    'НЕ ВЕРЬ\nКАЖДОМУ УБЕЖИЩУ',
    'ДЕРЖИСЬ\nСВОИХ',
    'НЕ ИГНОРИРУЙ\nПРЕДУПРЕЖДЕНИЯ',
    'НЕ ВОЗВРАЩАЙСЯ\nЗА ВЕЩАМИ',
    'НЕ ОТВЕЧАЙ\nСВОЕМУ ГОЛОСУ',
]

RULE_SUBS = [
    'ОНИ СЛЫШАТ ЗА КВАРТАЛ', 'ШЁПОТ ЛЕТИТ ДАЛЕКО', 'МАМА ТАК НЕ ГОВОРИТ', 'ДАЖЕ БУДИЛЬНИК',
    'ОНИ ПРИДУТ СЛУШАТЬ', 'СЛОВО В СЛОВО', 'КТО ЕГО СЛЫШАЛ?', 'ОНИ УМЕЮТ ЖДАТЬ',
    'ТИК... ТИК...', 'ГОЛОС НЕ ИСЧЕЗАЕТ', 'КТО ЕГО ПЕРЕДАЁТ?', 'ПООДИНОЧКЕ НЕ ВЫЖИТЬ',
    'ПОСЛЕДНИЙ КОНВОЙ', 'ВЕЩИ НЕ СТОЯТ ЖИЗНИ', 'ЭТО НЕ ТЫ',
]


def card(c, t, n, start=0.3, dur=4.2):
    k = seg(t, start, start + 0.5) * (1 - seg(t, start + dur, start + dur + 0.5))
    rule_card(c, n, RULE_TITLES[n - 1], RULE_SUBS[n - 1], k, t)


def nb(n, new=True):
    """notebook scene showing rules 1..n, with rule n being written"""
    def d(c, t, T, q):
        fy = H / 2 + 30 - 350 + (n - 1) * 50
        c.save()
        c.translate(W / 2 - 180, H * 0.55)
        c.scale(1.32, 1.32)
        c.translate(-W / 2, -fy)
        notebook(c, t, RULES[:n], seg(t, 0.6, min(T - 0.6, 3.6)) if new else 1.0)
        c.restore()
    return d


# ===================================================================== PART 1 — НАЧАЛО

def v_cold_open(c, t, T, q):
    corridor(c, t, flicker=1.0, col='#0d0f13', wall='#171a20', floor='#0b0c0f', ceil='#0d0f12')
    k = seg(t, 0.5, T)
    listener(c, 960, 860, 0.55 + 0.1 * k, turn=math.sin(t * 0.4) * 0.15, t=t, dark=0.35, glow=0.6)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.25)))


sc(1, 1, [('W', 'Если ты слышишь эту запись... говори тише.'),
          ('W', 'Они уже рядом. И они слушают.')],
   v_cold_open, amb='drone_room', mus='dread', sfx=[(0.2, 'tape_click', 0.8), (0.4, 'tape_hiss', 0.5)],
   min_dur=8, cam=(1.0, 1.18, 960, 520), fade_in=1.0,
   prompt='Dark corridor, flickering ceiling light, a tall white faceless ceramic figure stands far away. Slow push-in.')


def v_title(c, t, T, q):
    black(c)
    a = seg(t, 0.4, 1.6) * (1 - seg(t, T - 1.0, T - 0.2))
    listener(c, 1440, 1150, 1.25, turn=-0.25, t=t, glow=1.0, dark=0.2, alpha=a * 0.9)
    text(c, 'THE LISTENERS', 120, 360, 40, C('#e53935', a), FONT_XB)
    text(c, 'СЛУШАЮЩИЕ', 110, 500, 150, C('#ffffff', a), shadow=10)
    text(c, '15 ПРАВИЛ, ЧТОБЫ ВЫЖИТЬ', 118, 600, 64, C('#ffd21e', a), stroke=10, stroke_col='#000000')
    label(c, 'ЭПИЗОД 01', 120, 650, 34, bg='#e53935', fg='#ffffff', alpha=a)


sc(2, 1, [], v_title, amb='none', mus='title', sfx=[(0.3, 'boom', 1.0), (0.35, 'stinger', 0.7)], min_dur=6.0,
   cam=(1.0, 1.05, 700, 500), prompt='Title card: white faceless creature in darkness, title СЛУШАЮЩИЕ.')


def v_wake(c, t, T, q):
    bedroom(c, t, 'dawn', phone_glow=True)
    # Alex sitting up in bed
    k = ease(seg(t, 0.5, 2.5))
    alex(c, 520, 900 - k * 40, 0.85, look=0.6 * k, mouth=0.1, eyes='normal' if k < 0.5 else 'wide', arms='down', t=t, brows='flat' if k < 0.5 else 'worried')
    rrect(c, 140, 700, 760, 200, 40, paint('#6c7aa6'))
    rrect(c, 140, 700, 760, 60, 30, paint(C('#000000', 0.12)))


sc(3, 1, [('N', 'Меня зовут Алекс. Мне шестнадцать лет.'),
          ('N', 'В то утро меня разбудил не будильник. Меня разбудила тишина.')],
   v_wake, amb='room_dawn', mus='calm', sfx=[(0.5, 'sheets', 0.6)], min_dur=7, cam=(1.0, 1.08, 600, 600),
   prompt='Teen boy Alex (black messy hair, dark sweater) sits up in bed, grey dawn light from window, empty city outside.')


def v_phone_nosignal(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#141626'))
    circle(c, 960, 540, 700, paint(C('#4a6cff', 0.10), blur=120))
    phone_screen(c, 760, 80, 400, 860, t, 'nosignal', time='06:47')
    # thumb
    oval(c, 1240, 900 - 30 * math.sin(t * 2), 120, 170, paint(SKIN))
    oval(c, 1240, 900 - 30 * math.sin(t * 2), 120, 170, paint(C('#000000', 0.1)))


sc(4, 1, [('N', 'Телефон не ловил сеть. Ни одного нового сообщения.'),
          ('N', 'Мама ушла на ночную смену в больницу и обещала позвонить в семь утра.')],
   v_phone_nosignal, amb='room_dawn', mus='calm', sfx=[(1.0, 'tap', 0.5), (2.0, 'tap', 0.5), (2.6, 'error_beep', 0.4)],
   min_dur=7, cam=(1.0, 1.06, 960, 500), prompt='Extreme close-up of smartphone: НЕТ СЕТИ, 06:47.')


def v_voicemail(c, t, T, q):
    bedroom(c, t, 'dawn')
    alex(c, 900, 1260, 1.45, look=-0.2, mouth=q.talk(0, t) + q.talk(1, t), arms='ear', item='phone', t=t, eyes='normal')


sc(5, 1, [('N', 'Я всё равно позвонил. И оставил сообщение, которое потом пожалел.'),
          ('AN', 'Мам, где ты? Перезвони мне, пожалуйста.')],
   v_voicemail, amb='room_dawn', mus='calm', sfx=[(0.3, 'dial_beep', 0.4), (1.2, 'dial_beep', 0.4)], min_dur=7,
   cam=(1.05, 1.12, 900, 400), prompt='Medium close-up: Alex holds phone to ear, worried, dawn bedroom.')


def v_window_city(c, t, T, q):
    # view out of window at a silent city
    city_bg(c, t, '#4f5b80', '#b9aeb8', moon_xy=None, seed=21, lit=0.0, stars_n=0, fog_a=0.3)
    road(c, 860, '#3a3d48')
    for x, s_, col in ((300, 0.5, '#7b8696'), (820, 0.5, '#8c3b3b'), (1400, 0.5, '#4d5b70')):
        car(c, x, 990, s_, col, door_open=(x == 820))
    # window frame overlay (we look from inside)
    c.drawPath(poly([(0, 0), (W, 0), (W, 60), (0, 60)]), paint('#d9d2c3'))
    rect(c, 0, 0, 70, H, paint('#d9d2c3'))
    rect(c, W - 70, 0, 70, H, paint('#d9d2c3'))
    rect(c, W / 2 - 18, 0, 36, H, paint('#d9d2c3'))
    rect(c, 0, H - 80, W, 80, paint('#c9c2b3'))
    # Alex reflection
    alex(c, 600, 1500, 1.6, look=0.3, t=t, mouth=0.1, eyes='normal', tint='#ffffff')
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#cfd6e6', 0.0)))


def v_window_city_wrap(c, t, T, q):
    c.saveLayerAlpha(None, 255)
    v_window_city(c, t, T, q)
    c.restore()


def v_city_wide(c, t, T, q):
    city_bg(c, t, '#4f5b80', '#b9aeb8', moon_xy=None, seed=31, lit=0.0, stars_n=0, fog_a=0.35)
    road(c, 820, '#3a3d48')
    car(c, 500, 960, 0.7, '#7b8696', door_open=True)
    car(c, 1350, 1000, 0.75, '#8c3b3b', door_open=True, flip=True)
    street_lamp(c, 200, 860, 520, on=0)
    street_lamp(c, 1750, 860, 520, on=0, side=-1)
    # blinking traffic light
    rect(c, 1000, 520, 10, 340, paint('#1b1e27'))
    rrect(c, 980, 440, 50, 120, 10, paint('#1b1e27'))
    on = int(t * 1.5) % 2 == 0
    circle(c, 1005, 470, 15, paint('#ffb300' if on else '#3a2e10'))
    if on:
        circle(c, 1005, 470, 60, paint(C('#ffb300', 0.3), blur=20))
    # birds
    for i in range(5):
        bx = (t * 60 + i * 140) % (W + 200) - 100
        by = 200 + math.sin(t + i) * 20 + i * 15
        line(c, bx - 12, by, bx, by + 6, '#1e2230', 3)
        line(c, bx, by + 6, bx + 12, by, '#1e2230', 3)


sc(6, 1, [('N', 'За окном стоял город, в котором жили два миллиона человек.'),
          ('N', 'И я не слышал ни одной машины. Ни одного голоса. Ничего.')],
   v_city_wide, amb='city_dawn', mus='calm', sfx=[(1.0, 'birds', 0.25)], min_dur=7, cam=(1.12, 1.0, 960, 600),
   prompt='Wide shot: empty city at dawn, abandoned cars with open doors, blinking yellow traffic light, fog.')


def v_kitchen_tv(c, t, T, q):
    on = t > 1.2
    mode = 'static' if 1.2 < t < 2.0 else 'eas'
    kitchen(c, t, tv_mode=mode, tv_on=on)
    alex(c, 650, 1080, 0.9, look=1.0, mouth=0.25, t=t, arms='tense' if on else 'down', sweat=1 if t > 3 else 0)


sc(7, 1, [('N', 'Потом сам по себе включился телевизор.'),
          ('TV', 'Внимание. Экстренное оповещение. Зафиксировано распространение неизвестного организма эн-ноль.'),
          ('TV', 'Оставайтесь дома. Не выходите на улицу. Не издавайте громких звуков.')],
   v_kitchen_tv, amb='room_dawn', mus='tense', sfx=[(1.2, 'tv_on', 0.8), (1.25, 'static', 0.4), (2.0, 'eas_tone', 0.5)],
   min_dur=9, cam=(1.0, 1.1, 1300, 450), gap=0.3,
   prompt='Kitchen, TV switches on itself: red emergency broadcast ОРГАНИЗМ N-0, Alex staring.')


def v_tv_close(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0b0a0d'))
    tv(c, 160, 80, 1600, 900, True, 'eas', t, 'ОРГАНИЗМ N-0', 'НЕ ИЗДАВАЙТЕ ЗВУКОВ')


sc(8, 1, [('N', 'Сообщение повторялось снова и снова. Одними и теми же словами.'),
          ('N', 'Никто не объяснял, что такое эн-ноль. И никто не говорил, что делать дальше.')],
   v_tv_close, amb='room_dawn', mus='tense', sfx=[(0.0, 'eas_tone', 0.35)], min_dur=7, cam=(1.0, 1.12, 960, 540),
   prompt='Close-up of TV emergency alert, scrolling red text.')


def v_street_walk(c, t, T, q):
    street(c, t, seed=41, dawn=True, cars=[(1300, 960, 0.8, '#5f6b7d', dict(door_open=True)), (300, 1000, 0.85, '#8c3b3b', dict(flip=True))])
    x = lerp(-150, 900, seg(t, 0, T))
    alex(c, x, 1040, 0.7, look=0.5 * math.sin(t * 0.7), t=t, walk=t * 0.9, arms='tense', tint=DAWN_TINT)


sc(9, 1, [('N', 'Я вышел на улицу. Машины стояли прямо посреди дороги. С открытыми дверями.'),
          ('N', 'Будто люди просто вышли из них... и ушли.')],
   v_street_walk, amb='city_dawn', mus='tense', sfx=[(0.5, 'footsteps', 0.4)], min_dur=8, cam=(1.0, 1.0, 960, 540, -40, 40),
   prompt='Tracking shot: Alex walks along an empty grey street past abandoned cars with doors open.')


def v_headphones(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#33363f'))
    r = random.Random(4)
    for i in range(60):
        rect(c, r.uniform(0, W), r.uniform(0, H), r.uniform(4, 14), r.uniform(4, 14), paint(C('#ffffff', 0.05)))
    # asphalt crack
    c.drawPath(poly([(0, 700), (300, 650), (700, 720), (1100, 600), (1500, 680), (1920, 640)], close=False), paint('#1f2127', 'stroke', 8))
    # headphones
    pth = skia.Path()
    pth.moveTo(760, 600)
    pth.cubicTo(760, 280, 1160, 280, 1160, 600)
    c.drawPath(pth, paint('#16171c', 'stroke', 40))
    for x in (760, 1160):
        rrect(c, x - 70, 560, 140, 200, 60, paint('#1c1d22'))
        oval(c, x, 660, 50, 80, paint('#c0392b'))
    # cable
    cp = skia.Path()
    cp.moveTo(1160, 760)
    cp.cubicTo(1300, 900, 1500, 800, 1700, 950)
    c.drawPath(cp, paint('#16171c', 'stroke', 10))
    music_notes(c, 960, 520, t, 0.8, '#ffd21e')
    # creeping shadow at the end
    k = seg(t, T - 2.5, T)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#000', shader=lin(W, 0, 0, 0, [C('#000000', 0.7 * k), C('#000000', 0)])))


sc(10, 1, [('N', 'На асфальте лежали чьи-то наушники. Из них всё ещё играла музыка.'),
           ('W', 'Тогда я ещё не знал, что именно музыка привела их сюда.')],
   v_headphones, amb='city_dawn', mus='tense', sfx=[(0.0, 'headphones', 0.6)], min_dur=7, cam=(1.0, 1.15, 960, 600),
   prompt='Overhead close-up: headphones on wet asphalt, tiny music still playing.')


def v_first_sight(c, t, T, q):
    street(c, t, seed=51, dawn=True, lamps=((200, 1),), fog_a=0.4)
    fog(c, t, 820, 0.35, col='#d8dcea', n=9, speed=6)
    k = seg(t, 0.8, 4.5)
    listener(c, 1180, 880, 0.48, turn=lerp(0.9, -0.2, ease(seg(t, 3.0, 5.0))), t=t, alpha=k, dark=0.1, glow=0.2)
    fog(c, t + 3, 860, 0.25, col='#d8dcea', n=6, speed=4, seed=9)
    alex(c, 380, 1300, 1.3, look=0.9, mouth=0.4, t=t, arms='tense', sweat=1, tint=DAWN_TINT)


sc(11, 1, [('N', 'А потом я увидел его.'),
           ('W', 'Белая фигура стояла в тумане, в самом конце улицы. Она не двигалась.')],
   v_first_sight, amb='city_dawn', mus='dread', sfx=[(0.6, 'riser', 0.5), (4.6, 'stinger', 0.6), (3.2, 'porcelain', 0.4)],
   min_dur=8, cam=(1.0, 1.12, 1150, 500), lead=0.5,
   prompt='Over-the-shoulder: Alex in foreground, a tall white faceless figure appears in the fog at the end of the street.')


def v_hide_car(c, t, T, q):
    # under the car POV
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#08090c'))
    rect(c, 0, 0, W, 300, paint('#141519'))
    for x in range(0, W, 220):
        rect(c, x, 230, 120, 60, paint('#1d1f25'))
    # light strip under car
    rect(c, 0, 640, W, 440, paint('#8d93a3'))
    rect(c, 0, 640, W, 440, paint('#000', shader=lin(0, 640, 0, 1080, [C('#000000', 0.1), C('#000000', 0.5)])))
    # tyres
    for x in (80, 1700):
        oval(c, x, 560, 160, 220, paint('#0e0f12'))
    # creature feet walking by
    fx = lerp(1500, 600, ease(seg(t, 1.0, T - 1.0)))
    for i, off in enumerate((0, 90)):
        ph = math.sin(t * 2.2 + i * math.pi)
        lift = max(0, ph) * 30
        fxx = fx + off + ph * 20
        c.drawPath(poly([(fxx - 18, 400), (fxx + 18, 400), (fxx + 12, 860 - lift), (fxx - 12, 860 - lift)]), paint('#e8e9ec'))
        c.drawPath(poly([(fxx - 20, 860 - lift), (fxx + 90, 875 - lift), (fxx - 20, 890 - lift)]), paint('#cfd2d8'))
    # Alex face in darkness foreground
    c.save()
    c.translate(330, 1000)
    alex(c, 0, 600, 1.6, look=1.0, mouth=0.0, arms='cover', t=t, tint='#5a6178')
    c.restore()


sc(12, 1, [('N', 'Я залез под машину и закрыл рот руками.'),
           ('W', 'Оно прошло совсем рядом. Медленно. Шаг... за шагом.')],
   v_hide_car, amb='city_dawn', mus='silence', sfx=[(1.4, 'creature_step', 0.6), (2.6, 'creature_step', 0.6), (3.8, 'creature_step', 0.6), (5.0, 'creature_step', 0.6), (6.2, 'creature_step', 0.5), (0.5, 'heartbeat', 0.5)],
   min_dur=8, cam=(1.0, 1.06, 900, 600), prompt='Low angle from under a car: long white legs walk past; Alex covers his mouth in the dark foreground.')


# ===================================================================== PART 2 — КТО ОНИ

def v_chapter(n, title):
    def d(c, t, T, q):
        black(c)
        a = seg(t, 0.2, 0.9) * (1 - seg(t, T - 0.8, T - 0.1))
        text(c, f'ЧАСТЬ {n}', W / 2, H / 2 - 70, 44, C('#e53935', a), FONT_XB, align='center')
        text(c, title, W / 2, H / 2 + 50, 110, C('#ffffff', a), align='center', shadow=10)
        line(c, W / 2 - 200 * a, H / 2 + 100, W / 2 + 200 * a, H / 2 + 100, C('#e53935', a), 6)
    return d


sc(13, 2, [], v_chapter(2, 'КТО ОНИ?'), amb='none', mus='dread', sfx=[(0.2, 'boom', 0.7)], min_dur=2.9)


def photo_creature(c):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#2d2f36'))
    rect(c, -700, -220, 600, 640, paint('#3b3e47'))
    listener(c, -400, 420, 0.62, turn=0.0, t=0, glow=0.3)


def v_dossier(c, t, T, q):
    def ph(cc):
        cc.drawRect(skia.Rect.MakeXYWH(-700, -220, 600, 640), paint('#363a44'))
        listener(cc, -400, 420, 0.62, turn=0.0, t=t, glow=0.2)
    dossier(c, t, photo_draw=ph)
    c.save()
    c.translate(W / 2, H / 2 + 20)
    c.rotate(-2)
    items = ['Глаза: ОТСУТСТВУЮТ', 'Нос: ОТСУТСТВУЕТ', 'Рот: ОТСУТСТВУЕТ', 'Покров: гладкий, белый, «керамика»', 'Рост: 2,3–2,6 м', 'Слух: ЭКСТРЕМАЛЬНЫЙ']
    for i, s in enumerate(items):
        k = seg(t, 1.0 + i * 0.9, 1.4 + i * 0.9)
        if k > 0:
            text(c, s, -60, -150 + i * 80, 34, C('#1d1d1d', k), FONT_XB)
            if 'ОТСУТ' in s or 'ЭКСТР' in s:
                line(c, -60, -140 + i * 80, -60 + text_w(s, 34, FONT_XB) * k, -140 + i * 80, C('#c0392b', 0.8), 4)
    c.restore()


sc(14, 2, [('N', 'Позже выжившие назовут их Слушающими.'),
           ('N', 'У них нет глаз. Нет носа. Нет рта. Нет волос.'),
           ('N', 'Гладкое белое тело, похожее на керамику. Вытянутая голова. Слишком длинные руки и ноги.')],
   v_dossier, amb='room_night', mus='doc', sfx=[(0.2, 'paper', 0.6), (1.0, 'stamp', 0.5), (3.0, 'typewriter', 0.3)], min_dur=10,
   cam=(1.0, 1.08, 960, 520), prompt='Classified dossier ДЕЛО N-0 with a photo of the white faceless creature and anatomy notes.')


def v_anatomy(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0f1424'))
    # blueprint grid
    for x in range(0, W, 60):
        line(c, x, 0, x, H, C('#3b5bdb', 0.12), 1)
    for y in range(0, H, 60):
        line(c, 0, y, W, y, C('#3b5bdb', 0.12), 1)
    turn = math.sin(t * 0.5) * 0.8
    listener(c, 960, 1010, 0.9, turn=turn, t=t, glow=0.8, ripples=0.6)
    # callouts
    calls = [((1000, 260), (1350, 220), 'ГОЛОВА БЕЗ ЛИЦА'), ((980, 380), (1350, 380), 'ШЕЯ: ПОВОРОТ 180°'), ((870, 760), (450, 760), 'РУКИ НИЖЕ КОЛЕН'), ((1000, 900), (1350, 920), 'БЕСШУМНЫЙ ШАГ')]
    for i, ((x0, y0), (x1, y1), s) in enumerate(calls):
        k = seg(t, 0.8 + i * 1.2, 1.4 + i * 1.2)
        if k <= 0:
            continue
        line(c, x0, y0, lerp(x0, x1, k), lerp(y0, y1, k), C('#7fb2ff', 0.9), 3)
        circle(c, x0, y0, 7, paint('#7fb2ff'))
        if k >= 1:
            text(c, s, x1 + (10 if x1 > x0 else -10), y1 + 12, 34, '#cfe0ff', FONT_XB, align='left' if x1 > x0 else 'right')


sc(15, 2, [('N', 'Когда они слышат звук, голова медленно поворачивается к нему.'),
           ('N', 'Плавно. Неестественно. Как будто у шеи нет костей.')],
   v_anatomy, amb='lab_hum', mus='doc', sfx=[(0.5, 'porcelain', 0.5), (3.0, 'porcelain', 0.4)], min_dur=8,
   cam=(1.0, 1.05, 960, 500), prompt='Blueprint anatomy diagram of the Listener with callouts, head slowly turning.')


def v_blind(c, t, T, q):
    street(c, t, seed=61, lamps=((960, 1),), fog_a=0.2)
    # a person tiptoes right past a listener that doesn't see
    listener(c, 900, 900, 0.6, turn=0.0, t=t, glow=0.5)
    x = lerp(1700, 1250, seg(t, 0.5, T))
    person(c, x, 1030, 0.5, coat='#3f6e4f', hair='#4a3020', look=-0.6, mouth=0.0, walk=t * 0.5, flip=True, tint=NIGHT_TINT, eyes='wide')


sc(16, 2, [('N', 'Они не видят. Совсем. Ты можешь стоять прямо перед ним — и он тебя не заметит.'),
           ('W', 'Пока ты молчишь.')],
   v_blind, amb='city_night', mus='tense', sfx=[(0.5, 'footsteps_soft', 0.3)], min_dur=8, cam=(1.0, 1.1, 1100, 560),
   prompt='Night street under a single lamp: a survivor tiptoes past a motionless white creature that cannot see him.')


def v_shout(c, t, T, q):
    street(c, t, seed=71, lamps=((350, 1), (1550, -1)))
    s0 = q.s(1)
    turned = ease(seg(t, s0 + 1.5, s0 + 3.0))
    lunge = ease_in(seg(t, s0 + 3.3, s0 + 3.9))
    person(c, 1500, 1030, 0.55, coat='#8a5a2b', cap='#2c3e50', beard=True, hair='#3a2a1a', look=-0.5, mouth=max(q.talk(1, t) * 1.5, 0.1), t=t, arms='up' if t > s0 else 'down', tint=NIGHT_TINT)
    if t > s0:
        sound_waves(c, 1500, 690, t, 1.0)
    lx = lerp(500, 1300, lunge)
    listener(c, lx, 920, 0.62, turn=lerp(-0.2, 1.0, turned), t=t, ripples=turned, arms='reach' if lunge > 0 else 'hang', walk=t * 2 if lunge > 0 else 0)
    if lunge > 0.95:
        black(c)


sc(17, 2, [('N', 'Но стоит издать звук...'),
           ('MAN', 'Эй! Есть кто живой?! Помогите!')],
   v_shout, amb='city_night', mus='tense', sfx=[('L1+1.5', 'porcelain', 0.7), ('L1+3.3', 'creature_rush', 0.9), ('L1+3.9', 'hit', 1.0)],
   min_dur=7, tail=2.4, cam=(1.0, 1.04, 960, 540), prompt='A bearded man shouts for help; the white creature turns its head and lunges. Hard cut to black.')


def v_black_hold(c, t, T, q):
    black(c)


sc(18, 2, [('W', 'Ему хватило трёх секунд.')], v_black_hold, amb='none', mus='silence', min_dur=3.5)


def v_n0(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0b0f18'))
    # microscope-like circle with cells transforming
    cx, cy = 960, 520
    path = skia.Path()
    path.addCircle(cx, cy, 400)
    c.save()
    c.clipPath(path, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#000', shader=rad(cx, cy, 400, ['#2b3550', '#0d1220'])))
    r = random.Random(1)
    for i in range(40):
        x = cx + r.uniform(-380, 380) + math.sin(t * 0.5 + i) * 10
        y = cy + r.uniform(-380, 380) + math.cos(t * 0.4 + i) * 10
        rr = r.uniform(20, 50)
        k = clamp((t - i * 0.12) / 3)
        col = '#e05a5a' if k < 0.5 else '#f2f2f2'
        circle(c, x, y, rr, paint(C(col, 0.7)))
        circle(c, x, y, rr * 0.35, paint(C('#000000', 0.25 * (1 - k))))
    c.restore()
    circle(c, cx, cy, 402, paint('#555b66', 'stroke', 16))
    text(c, 'N-0', 1420, 260, 120, '#ffffff')
    text(c, 'ПРОИСХОЖДЕНИЕ:', 1425, 320, 28, '#e53935', FONT_XB)
    text(c, 'НЕИЗВЕСТНО', 1425, 360, 28, '#e53935', FONT_XB)


sc(19, 2, [('N', 'Организм эн-ноль меняет человека за несколько часов.'),
           ('N', 'Откуда он взялся — не знает никто. По крайней мере, так говорили по телевизору.')],
   v_n0, amb='lab_hum', mus='doc', sfx=[(0.3, 'bubble', 0.3)], min_dur=8, cam=(1.0, 1.1, 960, 520),
   prompt='Microscope view: red cells turning white. Label N-0, origin unknown.')


def v_home_notebook_start(c, t, T, q):
    apartment_living(c, t, tv_on=False, night=True, lamp=True)
    alex(c, 600, 1100, 0.95, look=0.2, mouth=0.0, t=t, arms='hold', eyes='normal')
    # notebook in hands
    rrect(c, 520, 700, 170, 120, 6, paint('#efe9d6'))


sc(20, 2, [('N', 'Я вернулся домой и заперся. В ту ночь я начал записывать правила.'),
           ('W', 'Каждое из них кто-то оплатил своей жизнью.')],
   v_home_notebook_start, amb='room_night', mus='calm', sfx=[(0.4, 'lock', 0.6)], min_dur=8, cam=(1.0, 1.1, 600, 600),
   prompt='Alex at home at night, lamp light, holding a notebook, door locked.')


# ===================================================================== PART 3 — ПРАВИЛА 1–5

sc(21, 3, [], v_chapter(3, 'ПРАВИЛА 1–5'), amb='none', mus='dread', sfx=[(0.2, 'boom', 0.7)], min_dur=2.9)


def v_r1_courtyard(c, t, T, q):
    courtyard_block(c, t, lit_windows={(2, 1): '#2a2410', (8, 4): '#2a2410'}, music_win=(5, 2) if t < T - 0.6 else None)
    if t < T - 0.6:
        music_notes(c, 5 * 134 + 160 + 37, 360, t, 1.0)
        sound_waves(c, 5 * 134 + 160 + 37, 360, t, 0.7)
    card(c, t, 1)


sc(22, 3, [('N', 'Правило номер один. Никогда не включай громкую музыку.'),
           ('N', 'На второй день кто-то в доме напротив включил колонку на полную громкость.'),
           ('N', 'Наверное, он думал, что если громко, то не так страшно.')],
   v_r1_courtyard, amb='city_night', mus='silence', sfx=[(0.0, 'music_loud', 0.55)], min_dur=10, cam=(1.0, 1.12, 900, 400),
   prompt='Night courtyard, soviet apartment block, one window flashing colored party lights, loud music.')


def v_r1_gather(c, t, T, q):
    courtyard_block(c, t, music_win=(5, 2))
    music_notes(c, 867, 360, t, 0.6)
    r = random.Random(8)
    n = int(lerp(2, 40, seg(t, 0.3, T - 1)))
    pts = [(r.uniform(80, W - 80), 900 + r.uniform(0, 160), r.uniform(0.28, 0.4)) for _ in range(40)][:n]
    pts.sort(key=lambda p: p[1])
    for i, (x, y, s) in enumerate(pts):
        listener(c, x, y, s, turn=clamp((867 - x) / 600, -1, 1) * 0.9, tilt=-15, t=t + i, glow=0.4, ripples=0.3, alpha=seg(t, i * 0.15, i * 0.15 + 0.6))
    # climbing ones
    for i in range(3):
        k = seg(t, 3 + i, T)
        if k > 0:
            listener(c, 700 + i * 160, lerp(1000, 520, k), 0.3, turn=0.6, arms='up', t=t + i * 3, tilt=-30, glow=0.4)


sc(23, 3, [('N', 'Через минуту под окнами стояли десятки белых фигур.'),
           ('N', 'Они выходили из подъездов, из машин, из темноты между домами.'),
           ('W', 'А потом некоторые из них начали подниматься по стене.')],
   v_r1_gather, amb='city_night', mus='tense', sfx=[(0.0, 'music_loud', 0.4), (1.0, 'crowd_shuffle', 0.6), (4.0, 'porcelain', 0.5), (6.0, 'climb', 0.6)],
   min_dur=11, cam=(1.0, 1.08, 960, 600), prompt='Dozens of white creatures gather below the window with music, some climb up the wall.')


def v_r1_silence(c, t, T, q):
    courtyard_block(c, t, dark=True)
    k = seg(t, 0, T)
    r = random.Random(8)
    pts = sorted([(r.uniform(80, W - 80), 900 + r.uniform(0, 160), r.uniform(0.28, 0.4)) for _ in range(40)], key=lambda p: p[1])
    for i, (x, y, s) in enumerate(pts):
        listener(c, x, y, s, turn=0.0, t=t + i, glow=0.3, dark=0.3)


sc(24, 3, [('W', 'Музыка оборвалась на середине песни.'),
           ('N', 'А они стояли под тем окном до самого утра. И слушали тишину.')],
   v_r1_silence, amb='city_night', mus='silence', sfx=[(0.0, 'glass', 0.6)], min_dur=8, cam=(1.06, 1.0, 960, 540),
   prompt='Silence: dark window, creatures stand motionless in the courtyard until dawn.')


sc(25, 3, [('N', 'Я записал первое правило.')], nb(1), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r2_window(c, t, T, q):
    kitchen(c, t, tv_on=False, window_open=1.0, night=True)
    alex(c, 520, 1080, 0.95, look=-0.6, mouth=q.talk(1, t), t=t, arms='down', eyes='normal')
    card(c, t, 2)


sc(26, 3, [('N', 'Правило номер два. Не разговаривай возле открытых окон.'),
           ('N', 'На третью ночь в квартире стало душно, и я приоткрыл окно.'),
           ('N', 'Мне хотелось просто услышать хоть что-то. Даже свой голос.')],
   v_r2_window, amb='room_night', mus='calm', sfx=[(3.0, 'window_open', 0.6)], min_dur=10, cam=(1.0, 1.08, 520, 500),
   prompt='Night kitchen, window open, Alex standing near it.')


def v_r2_talk(c, t, T, q):
    # exterior: building facade, Alex in lit window, creature crawling up from below
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#232842'))
    for i in range(5):
        for j in range(4):
            wx, wy = 160 + i * 340, 60 + j * 280
            rect(c, wx, wy, 200, 200, paint('#0d1020'))
    wx, wy = 160 + 2 * 340, 60 + 1 * 280
    rect(c, wx, wy, 200, 200, paint('#c9a65a'))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, 200, 200))
    alex(c, wx + 100, wy + 400, 0.42, look=0.1, mouth=q.talk(0, t), t=t, eyes='normal')
    c.restore()
    line(c, wx + 100, wy, wx + 100, wy + 200, '#d9d2c3', 8)
    if q.talk(0, t):
        sound_waves(c, wx + 100, wy + 110, t, 0.6)
    k = ease(seg(t, 2.0, T))
    listener(c, wx + 60, lerp(1600, 980, k), 0.5, turn=0.0, tilt=-10, arms='up', t=t, glow=0.5, ripples=0.5)


sc(27, 3, [('A', 'Здесь есть кто-нибудь? Кто-нибудь меня слышит?'),
           ('W', 'Меня услышали.'),
           ('N', 'Я заметил его только тогда, когда белая голова поднялась к подоконнику этажом ниже.')],
   v_r2_talk, amb='city_night', mus='tense', sfx=[('L1+0.0', 'climb', 0.7), ('L2+0.8', 'porcelain', 0.6)], min_dur=10,
   cam=(1.0, 1.1, 780, 500), prompt='Exterior: Alex whispers out of his lit window; a white creature crawls up the facade below.')


def v_r2_close(c, t, T, q):
    kitchen(c, t, tv_on=False, window_open=1.0 - ease(seg(t, 0.8, 1.6)), night=True)
    # creature head appears in window
    k = seg(t, 1.6, 3)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(220, 110, 420, 330))
    listener(c, 430, 1350 - 300 * ease(k), 0.9, turn=0.0, t=t, tilt=-6)
    c.restore()
    alex(c, 900, 1150, 1.05, look=-1, mouth=0.0, t=t, arms='cover', sweat=2)


sc(28, 3, [('N', 'Я захлопнул окно и замер.'),
           ('W', 'Оно прижалось к стеклу и слушало. Час. Может, два.')],
   v_r2_close, amb='room_night', mus='dread', sfx=[(0.9, 'window_slam', 0.8), (1.8, 'glass_tap', 0.6), (3.5, 'porcelain', 0.5)], min_dur=8,
   cam=(1.0, 1.12, 600, 400), prompt='Alex slams the window shut, the faceless head rises behind the glass.')


sc(29, 3, [('N', 'Второе правило.')], nb(2), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r3_knock(c, t, T, q):
    room(c, '#3b3a32', '#2a2620', 800)
    door(c, 800, 180, 320, 620, shake=1.0 if any(abs(t - x) < 0.15 for x in (0.6, 1.0, 1.4)) else 0, t=t)
    # light under door
    rect(c, 800, 795, 320, 6, paint(C('#ffe7a8', 0.7)))
    alex(c, 1450, 1080, 0.85, look=-0.9, mouth=0.1, t=t, arms='tense', sweat=1)
    card(c, t, 3, 1.8)


sc(30, 3, [('N', 'Правило номер три. Не открывай дверь, даже если слышишь знакомый голос.'),
           ('N', 'Это случилось на пятую ночь. В дверь постучали.')],
   v_r3_knock, amb='room_night', mus='tense', sfx=[(0.5, 'knock', 0.9)], min_dur=8, cam=(1.0, 1.06, 960, 500), lead=1.8,
   prompt='Dark hallway inside apartment: the front door shakes from knocking, light under the door. Alex freezes.')


def v_r3_mom(c, t, T, q):
    room(c, '#3b3a32', '#2a2620', 800)
    door(c, 600, 180, 320, 620, t=t)
    alex(c, 1080, 1250, 1.3, look=1.0, mouth=0.3, t=t, arms='handle' if t > q.s(1) else 'tense', sweat=1, flip=True)


sc(31, 3, [('MOM', 'Алекс... милый, это мама. Открой, мне холодно.'),
           ('N', 'Это был её голос. Её интонация. Я уже потянулся к замку.')],
   v_r3_mom, amb='room_night', mus='tense', sfx=[(0.0, 'knock_soft', 0.4)], min_dur=8, cam=(1.0, 1.1, 900, 450),
   prompt='Close: Alex reaches toward the door lock, a familiar female voice behind the door.')


def v_r3_peep(c, t, T, q):
    def inner(cc):
        hallway_inner(cc, t)
        listener(cc, 960, 540 + 931 * 1.7, 1.7, turn=0.0, t=t, tilt=-4 + math.sin(t) * 2)
    peephole(c, t, inner)


sc(32, 3, [('W', 'Но мама никогда не называла меня «милый».'),
           ('W', 'Я посмотрел в глазок. Там было белое, гладкое лицо. Без глаз.')],
   v_r3_peep, amb='room_night', mus='dread', sfx=[('L1+2.4', 'stinger', 0.8)], min_dur=8, cam=(1.0, 1.1, 960, 540),
   prompt='Fisheye peephole view: a smooth white eyeless face pressed against the door.')


def v_r3_mom2(c, t, T, q):
    room(c, '#2a2924', '#1d1b17', 800)
    door(c, 600, 180, 320, 620, t=t, shake=0.3 if t < 2 else 0)
    alex(c, 1280, 1080, 0.85, look=-1.0, mouth=0.0, t=t, arms='cover', sweat=2, flip=False)


sc(33, 3, [('MOM', 'Алекс... милый... открой. Открой. Открой.'),
           ('N', 'Оно повторяло эти слова до рассвета. Тем же голосом. С теми же паузами.')],
   v_r3_mom2, amb='room_night', mus='dread', sfx=[], min_dur=8, cam=(1.04, 1.0, 900, 520),
   prompt='Alex backs away from the door, covering his mouth, the voice repeats.')


sc(34, 3, [('N', 'Третье правило.')], nb(3), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r4_store(c, t, T, q):
    store(c, t, flicker=1.0)
    listener(c, lerp(1300, 1100, seg(t, 0, T)), 900, 0.6, turn=-0.2, t=t, walk=t * 0.3, glow=0.4)
    alex(c, 520, 1060, 0.75, look=0.8, mouth=0.0, t=t, arms='hold', sweat=1, tint='#c9d6e6')
    card(c, t, 4)


sc(35, 3, [('N', 'Правило номер четыре. Отключи все звуки телефона. Вообще все.'),
           ('N', 'На шестой день закончилась еда, и я пошёл в магазин у дома.'),
           ('N', 'Внутри был один из них. Он медленно ходил между полками.')],
   v_r4_store, amb='store', mus='tense', sfx=[(0.5, 'creature_step', 0.3), (2.0, 'creature_step', 0.3), (3.5, 'creature_step', 0.3)], min_dur=11,
   cam=(1.0, 1.1, 900, 600), prompt='Supermarket at night, flickering fluorescent lights, a white creature walks slowly between shelves, Alex hides.')


def v_r4_phone(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14161c'))
    k = seg(t, 0.6, 1.0)
    phone_screen(c, 760, 100, 400, 860, t, 'ok', battery=5, time='14:03', notif=('Батарея разряжена', k, 'Осталось 5%'))
    if t > 0.6:
        sound_waves(c, 960, 540, t, 1.0 * (1 - seg(t, 3, 4)))


sc(36, 3, [('W', 'И тут телефон в кармане тихо пискнул. Низкий заряд батареи.')],
   v_r4_phone, amb='store', mus='silence', sfx=[(0.6, 'low_batt', 0.9)], min_dur=5.5, cam=(1.0, 1.1, 960, 540), lead=1.8,
   prompt='Extreme close-up: phone screen, low battery notification pops up with a beep.')


def v_r4_turn(c, t, T, q):
    store(c, t, flicker=1.0)
    k = ease(seg(t, 0.3, 1.8))
    rush = ease_in(seg(t, 3.0, 4.2))
    listener(c, lerp(1100, 700, rush), 960, lerp(0.75, 1.1, rush), turn=lerp(-0.2, -1.0, k), t=t, ripples=k, arms='reach' if rush > 0 else 'hang', flip=True, walk=t * 2 if rush > 0 else 0)
    alex(c, lerp(380, -200, seg(t, 3.0, 4.5)), 1060, 0.75, look=0.8, mouth=0.5, t=t, arms='tense', sweat=2, walk=t * 3 if t > 3 else 0, tint='#c9d6e6', flip=t > 3.0)


sc(37, 3, [('W', 'Этого хватило. Голова повернулась ко мне. Я побежал.'),
           ('N', 'Я выбросил телефон в мусорный бак и больше никогда не носил его со включённым звуком.')],
   v_r4_turn, amb='store', mus='action', sfx=[(0.4, 'porcelain', 0.7), (3.0, 'creature_rush', 0.8), (3.2, 'run', 0.7), (4.5, 'shelf_crash', 0.7)],
   min_dur=9, cam=(1.0, 1.08, 800, 600), prompt='The creature snaps its head toward Alex and lunges; Alex runs away.')


sc(38, 3, [('N', 'Четвёртое правило.')], nb(4), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r5_tvwin(c, t, T, q):
    courtyard_block(c, t, tv_win=(7, 3), seed=6)
    card(c, t, 5)


sc(39, 3, [('N', 'Правило номер пять. Не оставляй телевизор включённым, если уходишь.'),
           ('N', 'В доме напротив было одно окно, которое светилось каждую ночь. Голубым, мигающим светом.')],
   v_r5_tvwin, amb='city_night', mus='calm', sfx=[(0.0, 'tv_far', 0.3)], min_dur=9, cam=(1.0, 1.25, 1100, 480),
   prompt='Apartment block at night, one window flickers with blue TV light.')


def v_r5_inside(c, t, T, q):
    apartment_living(c, t, tv_on=True, tv_mode='show', night=True)
    for i, (x, s, tr) in enumerate(((420, 0.62, 0.9), (760, 0.7, 0.7), (1830, 0.6, -0.8), (980, 0.48, 0.6), (300, 0.5, 0.95))):
        listener(c, x, 1020 - s * 60, s, turn=tr, tilt=-12, t=t + i, glow=0.4, ripples=0.25, dark=0.15)


sc(40, 3, [('N', 'Соседи уехали в первый же день. А телевизор остался работать.'),
           ('W', 'Однажды я посмотрел туда в бинокль. Комната была полна ими.'),
           ('W', 'Они стояли вокруг экрана. Неподвижно. И слушали чужие голоса из передачи.')],
   v_r5_inside, amb='room_night', mus='dread', sfx=[(0.0, 'tv_show', 0.35), (4.0, 'porcelain', 0.4)], min_dur=11,
   cam=(1.08, 1.0, 1200, 500), prompt='Inside a living room lit only by a TV show: five white creatures stand around the TV, listening.')


sc(41, 3, [('N', 'Пятое правило. Так закончилась моя первая неделя.')], nb(5), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=6, cam=(1.0, 1.05, 960, 500), fade_out=0.6)


# ===================================================================== PART 4 — ПРАВИЛА 6–10

sc(42, 4, [], v_chapter(4, 'ОНИ ЗАПОМИНАЮТ'), amb='none', mus='dread', sfx=[(0.2, 'boom', 0.7)], min_dur=2.9)


def v_r6_window_night(c, t, T, q):
    courtyard_block(c, t, dark=True, seed=9)
    # a figure? none visible; only voice
    alex_w = (5, 2)
    sound_waves(c, 960, 960, t, 0.8 if q.talk(1, t) or q.talk(2, t) else 0.0)
    card(c, t, 6)


sc(43, 4, [('N', 'Правило номер шесть. Не отвечай на голоса с улицы.'),
           ('MAN', 'Помогите! Пожалуйста, кто-нибудь! Я ранен!'),
           ('N', 'Крик раздался во дворе около полуночи. Мужской голос. Живой. Настоящий.')],
   v_r6_window_night, amb='city_night', mus='tense', sfx=[], min_dur=10, cam=(1.0, 1.12, 960, 800),
   prompt='Dark courtyard at midnight, a cry for help echoes, nobody visible.')


def v_r6_alex(c, t, T, q):
    kitchen(c, t, tv_on=False, night=True)
    alex(c, 520, 1100, 1.0, look=-0.7, mouth=0.0, t=t, arms='handle' if t < q.s(2) else 'tense', sweat=1)


sc(44, 4, [('N', 'Я схватился за ручку окна. Хотел крикнуть, что сейчас спущусь.'),
           ('MAN', 'Помогите! Пожалуйста, кто-нибудь! Я ранен!'),
           ('W', 'А потом я понял. Он кричал слово в слово. С той же интонацией. С той же паузой перед словом «ранен».')],
   v_r6_alex, amb='room_night', mus='dread', sfx=[], min_dur=11, cam=(1.0, 1.1, 520, 500),
   prompt='Alex grips the window handle, then freezes as the cry repeats identically.')


def v_r6_reveal(c, t, T, q):
    street(c, t, seed=81, lamps=((960, 1),), fog_a=0.2)
    listener(c, 960, 900, 0.7, turn=0.0, tilt=-25, t=t, glow=0.8, ripples=0.6 if t < 3 else 0)


sc(45, 4, [('N', 'Под фонарём стоял Слушающий. Один. Запрокинув голову к окнам.'),
           ('W', 'Он не звал на помощь. Он забрасывал удочку.')],
   v_r6_reveal, amb='city_night', mus='dread', sfx=[(0.3, 'porcelain', 0.4)], min_dur=8, cam=(1.0, 1.15, 960, 380),
   prompt='Under a streetlight a single white creature tilts its head up toward the windows.')


sc(46, 4, [('N', 'Шестое правило.')], nb(6), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r7_walkie(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#191b22'))
    circle(c, 960, 540, 700, paint(C('#ffb347', 0.08), blur=120))
    c.save()
    c.translate(960, 560)
    c.rotate(-8)
    rrect(c, -170, -320, 340, 640, 40, paint('#2b2f36'))
    rect(c, 110, -520, 40, 220, paint('#1d2025'))
    for k in range(7):
        rrect(c, -110, -230 + k * 34, 220, 14, 7, paint('#14161a'))
    rrect(c, -110, 40, 220, 100, 10, paint('#9be59b' if q.talk(1, t) or q.talk(2, t) else '#3a5a3a'))
    text(c, 'CH 7', 0, 108, 48, '#183018', FONT_MONO, align='center')
    circle(c, -80, 220, 30, paint('#c0392b'))
    c.restore()
    if q.talk(1, t) or q.talk(2, t):
        sound_waves(c, 960, 420, t, 0.6)
    card(c, t, 7)


sc(47, 4, [('N', 'Правило номер семь. Не доверяй голосу, который знает твоё имя.'),
           ('MOM', 'Алекс... Алекс, ты меня слышишь? Приём.'),
           ('N', 'Эту рацию я нашёл в машине скорой помощи. На восьмой день она ожила.')],
   v_r7_walkie, amb='room_night', mus='tense', sfx=[(4.0, 'radio_static', 0.6)], min_dur=10, cam=(1.0, 1.1, 960, 540),
   prompt='Close-up: a walkie-talkie on a table, channel 7, static, a voice calls Alex by name.')


def v_r7_think(c, t, T, q):
    apartment_living(c, t, tv_on=False, night=True, lamp=True)
    alex(c, 960, 1300, 1.4, look=0.0, mouth=0.0, t=t, arms='chest', eyes='wide', sweat=1, brows='worried')


sc(48, 4, [('N', 'Голос был женский. Спокойный. Знакомый.'),
           ('W', 'Но тот, кто знает твоё имя, когда-то его уже слышал. Вопрос только — где. И от кого.')],
   v_r7_think, amb='room_night', mus='dread', sfx=[(0.0, 'radio_static', 0.3)], min_dur=9, cam=(1.0, 1.12, 960, 450),
   prompt='Close-up: Alex in lamp light, thinking, scared.')


sc(49, 4, [('N', 'Седьмое правило. Рацию я не выключил. Я просто перестал отвечать.')], nb(7), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=6, cam=(1.0, 1.05, 960, 500))


def v_r8_stairs(c, t, T, q):
    stairwell(c, t, flicker=0.5)
    alex(c, 420, 1050, 0.8, look=0.7, mouth=0.0, t=t, arms='tense', walk=t * 0.5 if t < 3 else 0, tint='#b8c4c4')
    card(c, t, 8)


sc(50, 4, [('N', 'Правило номер восемь. Тишина не значит, что ты в безопасности.'),
           ('N', 'На девятое утро было тихо. Совсем. Ни шагов, ни шорохов, ни голосов.'),
           ('N', 'Я решил, что они ушли из дома, и вышел на лестницу.')],
   v_r8_stairs, amb='stairs', mus='tense', sfx=[(4.0, 'door_creak', 0.6), (6.0, 'footsteps_soft', 0.3)], min_dur=11,
   cam=(1.0, 1.06, 700, 600), prompt='Dim stairwell, flickering bulb, graffiti ТИХО, Alex steps out carefully.')


def v_r8_reveal(c, t, T, q):
    stairwell(c, t, flicker=0.8)
    # creature standing on the stairs below, motionless
    listener(c, 1450, 1080, 0.75, turn=-0.6, tilt=-8, t=t, glow=0.6, sway=0.1)
    alex(c, 420, 1050, 0.8, look=1.0, mouth=0.6, t=t, arms='cover' if t > 2 else 'tense', sweat=2, tint='#b8c4c4')


sc(51, 4, [('W', 'Он стоял на пролёт ниже. Абсолютно неподвижно.'),
           ('W', 'Он стоял там всю ночь. Просто ждал, когда кто-нибудь издаст звук.')],
   v_r8_reveal, amb='stairs', mus='dread', sfx=[(0.0, 'stinger', 0.8)], min_dur=8, cam=(1.0, 1.12, 1100, 500), lead=1.0,
   prompt='Reveal: a white creature stands motionless on the landing below, head tilted toward Alex.')


sc(52, 4, [('N', 'Восьмое правило. Они умеют ждать. Часами. Днями.')], nb(8), amb='room_night', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r9_vent(c, t, T, q):
    room(c, '#2e3152', '#24263e', 800)
    # bed + vent grille
    rrect(c, 120, 640, 800, 260, 30, paint('#3b2a2a'))
    rrect(c, 140, 600, 760, 160, 40, paint('#6c7aa6'))
    vx, vy = 1300, 200
    bulge = ease(seg(t, T - 4, T - 1)) * 18
    rect(c, vx, vy, 300, 200, paint('#1a1c25'))
    for k in range(8):
        line(c, vx + 10, vy + 15 + k * 24 + bulge * math.sin(k / 7 * math.pi), vx + 290, vy + 15 + k * 24 + bulge * math.sin(k / 7 * math.pi), '#c9ccd6', 8)
    for (sx, sy) in ((vx + 8, vy + 8), (vx + 292, vy + 8), (vx + 8, vy + 192), (vx + 292, vy + 192)):
        circle(c, sx, sy, 7, paint('#7a7d88'))
    alex(c, 700, 1060, 0.85, look=1.0, mouth=0.1, t=t, arms='tense', sweat=1 if t > 3 else 0, tint='#b6bde0')
    card(c, t, 9)


sc(53, 4, [('N', 'Правило номер девять. Не игнорируй странные звуки.'),
           ('N', 'В ту же ночь из вентиляции начали доноситься щелчки. Тихие, ровные. Тик... тик... тик...'),
           ('N', 'Я убедил себя, что это трубы. Старый дом. Ничего страшного.'),
           ('W', 'Щелчки становились ближе.')],
   v_r9_vent, amb='room_night', mus='tense', sfx=[(4.0, 'vent_tick', 0.6)], min_dur=13, cam=(1.0, 1.1, 1100, 400),
   prompt='Bedroom at night, metal vent grille on the wall slowly bulges, ticking sounds.')


def v_r9_escape(c, t, T, q):
    stairwell(c, t, flicker=1.0, dark=0.2)
    alex(c, lerp(200, 1500, seg(t, 0.2, T)), lerp(1050, 1300, seg(t, 0.2, T)), 0.8, look=-0.5, mouth=0.3, t=t, arms='hold', walk=t * 2.5, sweat=2, tint='#b8c4c4')


sc(54, 4, [('N', 'Я схватил рюкзак и ушёл из квартиры той же ночью. Не оглядываясь.'),
           ('W', 'Утром решётка вентиляции лежала на полу моей комнаты.')],
   v_r9_escape, amb='stairs', mus='action', sfx=[(0.3, 'run', 0.5), (4.0, 'vent_crash', 0.6)], min_dur=8, cam=(1.0, 1.0, 960, 540, 0, -80),
   prompt='Alex runs down the dark stairwell with a backpack.')


sc(55, 4, [('N', 'Девятое правило.')], nb(9), amb='wind', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r10_hospital(c, t, T, q):
    hospital(c, t)
    alex(c, lerp(700, 900, seg(t, 0, T)), 1080, 0.8, look=0.0, t=t, mouth=0.0, arms='flash', item='flashlight', walk=t * 0.6, tint='#a9c9bf')
    # flashlight beam
    c.drawPath(poly([(1010, 650), (1600, 450), (1600, 800)]), paint('#000', shader=lin(1010, 0, 1600, 0, [C('#fff6c8', 0.3), C('#fff6c8', 0)])))
    card(c, t, 10)


sc(56, 4, [('N', 'Правило номер десять. Они запоминают всё, что слышат.'),
           ('N', 'Я пошёл туда, куда боялся идти все эти дни. В больницу, где работала мама.')],
   v_r10_hospital, amb='hospital', mus='tense', sfx=[(0.3, 'footsteps_soft', 0.35)], min_dur=9, cam=(1.0, 1.1, 960, 520),
   prompt='Hospital corridor, flickering lights, Alex walks with a flashlight.')


def v_r10_ward(c, t, T, q):
    hospital(c, t, flicker=1.0)
    listener(c, 1120, 760, 0.42, turn=-0.3, tilt=-10, t=t, glow=0.7, ripples=0.4 if (q.talk(0, t) or q.talk(1, t)) else 0)
    alex(c, 420, 1250, 1.2, look=0.9, mouth=0.0, t=t, arms='cover', sweat=1, tint='#a9c9bf')


sc(57, 4, [('MOM', 'Пациент из двенадцатой палаты, давление восемьдесят на пятьдесят.'),
           ('MOM', 'Срочно капельницу. Срочно.'),
           ('N', 'В конце коридора стоял один из них. И говорил голосом медсестры.')],
   v_r10_ward, amb='hospital', mus='dread', sfx=[], min_dur=11, cam=(1.0, 1.08, 1000, 500),
   prompt='Hospital corridor: a white creature at the far end speaks with a nurse\'s voice; Alex hides in foreground.')


def v_r10_mom(c, t, T, q):
    hospital(c, t, flicker=1.0)
    listener(c, 960, 1080, 0.88, turn=0.0, tilt=-5, t=t, glow=0.8, ripples=0.6 if q.talk(0, t) else 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.15)))


sc(58, 4, [('MOM', 'Алекс, если ты это слышишь — уходи из города. Не ищи меня.'),
           ('W', 'Это был голос мамы. Она была здесь. Она говорила это кому-то... а оно запомнило.')],
   v_r10_mom, amb='hospital', mus='dread', sfx=[(0.0, 'riser', 0.3)], min_dur=10, cam=(1.0, 1.2, 960, 300),
   prompt='Close: the white creature stands in the corridor and speaks with the mother\'s voice. Slow push-in.')


def v_r10_cry(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#121815'))
    rect(c, 0, 0, 420, H, paint('#1d2622'))
    alex(c, 900, 1500, 1.7, look=-0.2, mouth=0.0, eyes='closed', t=t, arms='cover', tint='#9fb6ad')
    # tear
    ty = 560 + (t * 60) % 120
    oval(c, 860, ty, 8, 14, paint('#9fdcff'))


sc(59, 4, [('N', 'Они не просто слышат. Они хранят голоса. Как записи.'),
           ('N', 'Я так и не узнал, кому мама это говорила. Но я сделал так, как она просила.')],
   v_r10_cry, amb='hospital', mus='sad', sfx=[], min_dur=10, cam=(1.0, 1.05, 900, 500),
   prompt='Close-up: Alex closes his eyes, covers his mouth, a tear.')


sc(60, 4, [('N', 'Десятое правило.')], nb(10), amb='hospital', mus='sad', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500), fade_out=0.6)


# ===================================================================== PART 5 — ПРАВИЛА 11–14

sc(61, 5, [], v_chapter(5, 'ДРУГИЕ ВЫЖИВШИЕ'), amb='none', mus='dread', sfx=[(0.2, 'boom', 0.7)], min_dur=2.9)


def v_meet(c, t, T, q):
    # hospital pharmacy, Mira and Viktor
    room(c, '#2a3a35', '#1c2622', 800, pattern=False)
    for x in range(60, W, 260):
        rect(c, x, 180, 220, 560, paint('#3e504a'))
        for k in range(4):
            rect(c, x, 220 + k * 130, 220, 10, paint('#58706a'))
    person(c, 1250, 1080, 0.82, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=-0.6, mouth=q.talk(1, t), t=t, arms='shh' if t < q.s(1) else 'down', tint='#b8cfc6')
    person(c, 1600, 1080, 0.9, coat='#3f4a3a', hair='#3a2f28', beard=True, cap='#1f2a24', look=-0.8, mouth=q.talk(2, t), t=t, tint='#b8cfc6')
    alex(c, 520, 1080, 0.82, look=0.8, mouth=0.0, t=t, arms='tense', tint='#b8cfc6')


sc(62, 5, [('N', 'В аптеке больницы я встретил Миру и Виктора. Они общались жестами и шёпотом.'),
           ('MIRA', 'Тише. Ты один? Давно ты здесь?'),
           ('VIK', 'Пойдём с нами. Здесь оставаться нельзя.')],
   v_meet, amb='hospital', mus='calm', sfx=[], min_dur=11, cam=(1.0, 1.06, 1000, 560),
   prompt='Hospital pharmacy: Alex meets Mira (yellow jacket, ponytail) and Viktor (beard, cap), whispering.')


def v_radio(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1d1a17'))
    circle(c, 960, 500, 700, paint(C('#ffb347', 0.08), blur=120))
    rrect(c, 360, 300, 1200, 560, 40, paint('#5a4636'))
    rrect(c, 420, 360, 600, 440, 20, paint('#2a221a'))
    for k in range(12):
        line(c, 440, 380 + k * 34, 1000, 380 + k * 34, '#3d3226', 6)
    rrect(c, 1080, 380, 420, 120, 10, paint('#f2d07a'))
    for k in range(20):
        line(c, 1100 + k * 19, 400, 1100 + k * 19, 420 + (k % 2) * 10, '#5a4636', 3)
    nx = 1100 + (0.6 + 0.02 * math.sin(t * 3)) * 380
    line(c, nx, 385, nx, 495, '#c0392b', 4)
    circle(c, 1180, 650, 70, paint('#2a221a'))
    circle(c, 1400, 650, 70, paint('#2a221a'))
    text(c, 'FM 103.7', 1290, 560, 32, '#f2d07a', FONT_MONO, align='center')
    sound_waves(c, 720, 580, t, 0.5 if q.talk(0, t) else 0.0)
    card(c, t, 11)


sc(63, 5, [('TV', 'Говорит штаб спасения. Убежище на станции метро «Северная». Еда, вода, безопасность. Приходите.'),
           ('N', 'Правило номер одиннадцать. Не доверяй каждому сообщению об убежище.'),
           ('VIK', 'Это сообщение крутят уже две недели. Слово в слово. Ни одного нового.')],
   v_radio, amb='room_night', mus='tense', sfx=[(0.0, 'radio_static', 0.4)], min_dur=12, cam=(1.0, 1.08, 960, 520), lead=1.0,
   prompt='Close-up of an old radio, FM dial, broadcast about a shelter at metro station Северная.')


def v_metro_stairs(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e1118'))
    # escalator down view
    c.drawPath(poly([(560, 0), (1360, 0), (1200, H), (720, H)]), paint('#20252e'))
    for k in range(14):
        y = (k * 90 + t * 30) % H
        line(c, 600 + y * 0.12, y, 1320 - y * 0.12, y, '#2c323d', 6)
    for side in (-1, 1):
        line(c, 960 + side * 420, 0, 960 + side * 260, H, '#c9b45a', 10)
    circle(c, 960, H + 100, 500, paint(C('#ffe0a0', 0.15), blur=100))
    for (x, s) in ((600, 0.8), (1250, 0.85)):
        person(c, x, 1250, s, coat='#d4a017' if x < 900 else '#3f4a3a', hair='#6b2f1a' if x < 900 else '#3a2f28', female=x < 900, hairstyle='ponytail', beard=x > 900, cap=None if x < 900 else '#1f2a24', look=0.3, mouth=0.0, t=t, tint='#8f9ab8')
    alex(c, 930, 1300, 0.95, look=0.0, mouth=0.0, t=t, tint='#8f9ab8')


sc(64, 5, [('N', 'Мы всё равно пошли проверить. Медленно спустились по неподвижному эскалатору.'),
           ('W', 'Снизу доносился тот же голос. Голос из радио.')],
   v_metro_stairs, amb='subway', mus='tense', sfx=[(0.5, 'footsteps_soft', 0.35)], min_dur=9, cam=(1.0, 1.08, 960, 700),
   prompt='Three survivors descend a stopped metro escalator, a voice echoes from below.')


def v_metro_platform(c, t, T, q):
    subway(c, t, crowd=24, crowd_alpha=1.0)


sc(65, 5, [('TV', 'Убежище на станции метро «Северная». Еда, вода, безопасность. Приходите.'),
           ('W', 'Платформа была заполнена ими. Сотни. Они стояли под громкоговорителем и слушали.'),
           ('N', 'Сообщение передавал не штаб. Его передавало то, что когда-то услышало его первым.')],
   v_metro_platform, amb='subway', mus='dread', sfx=[(0.0, 'pa_echo', 0.0), (6.0, 'crowd_shuffle', 0.5)], min_dur=13,
   cam=(1.18, 1.0, 960, 500), prompt='Metro platform СЕВЕРНАЯ crowded with motionless white creatures listening to a loudspeaker.')


sc(66, 5, [('N', 'Одиннадцатое правило. Кто-то приходит на такие сообщения до сих пор.')], nb(11), amb='wind', mus='calm', sfx=[(0.8, 'pen_write', 0.5)], min_dur=6, cam=(1.0, 1.05, 960, 500))


def v_r12_forest(c, t, T, q):
    forest_road(c, t)
    for i, (x, kw) in enumerate(((760, dict(female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a')), (1160, dict(beard=True, cap='#1f2a24', coat='#3f4a3a', hair='#3a2f28')))):
        person(c, x, 1060, 0.62, look=0.2, mouth=0.0, t=t + i, walk=t * 0.5, tint=DARK_TINT, **kw)
    alex(c, 960, 1080, 0.64, look=0.0, mouth=0.0, t=t, walk=t * 0.5, tint=DARK_TINT)
    card(c, t, 12)


sc(67, 5, [('N', 'Правило номер двенадцать. Держись людей, которым доверяешь.'),
           ('N', 'Мы шли на север по лесной дороге. Втроём. Ночью, потому что ночью тише.')],
   v_r12_forest, amb='forest', mus='calm', sfx=[(0.3, 'footsteps_forest', 0.4)], min_dur=9, cam=(1.0, 1.06, 960, 700),
   prompt='Night forest road under the moon, three survivors walk in a line, fog.')


def v_r12_split(c, t, T, q):
    forest_road(c, t)
    vx = lerp(1160, 1700, seg(t, q.s(1), q.s(1) + 4))
    person(c, vx, 1060 - seg(t, q.s(1), q.s(1) + 4) * 120, 0.62 * (1 - 0.3 * seg(t, q.s(1), q.s(1) + 4)), beard=True, cap='#1f2a24', coat='#3f4a3a', hair='#3a2f28', look=0.6, mouth=q.talk(1, t), t=t, walk=t * 0.8, tint=DARK_TINT, flip=False)
    person(c, 760, 1060, 0.62, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.8, mouth=0.0, t=t, tint=DARK_TINT)
    alex(c, 960, 1080, 0.64, look=0.8, mouth=0.0, t=t, tint=DARK_TINT)
    # old car in the trees
    car(c, 1780, 900, 0.45, '#4a4f5a', dark=0.8)


sc(68, 5, [('N', 'У обочины стояла брошенная машина. Виктор решил проверить, есть ли в ней бензин.'),
           ('VIK', 'Я быстро. Ждите здесь. Ни звука.'),
           ('N', 'Он ушёл один. Всего на пару минут.')],
   v_r12_split, amb='forest', mus='tense', sfx=[(5.0, 'branch', 0.4)], min_dur=11, cam=(1.0, 1.08, 1200, 650),
   prompt='Viktor walks alone toward an abandoned car among the trees; Alex and Mira wait.')


def v_r12_voice(c, t, T, q):
    forest_road(c, t)
    # dark trees, and somewhere a white shape between trunks
    listener(c, 1650, 860, 0.35, turn=-0.5, t=t, dark=0.5, glow=0.3, alpha=seg(t, 3, 6) * 0.8)
    person(c, 760, 1100, 0.7, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.8, mouth=0.0, t=t, arms='cover', tint=DARK_TINT)
    alex(c, 980, 1110, 0.72, look=0.8, mouth=0.0, t=t, arms='tense', sweat=1, tint=DARK_TINT)


sc(69, 5, [('VIKL', 'Ребята! Идите сюда! Всё чисто! Идите ко мне!'),
           ('W', 'Виктор никогда бы не закричал. Он сам научил нас молчать.'),
           ('N', 'Мы ушли. Не попрощавшись. И больше никогда его не видели.')],
   v_r12_voice, amb='forest', mus='dread', sfx=[(0.0, 'branch', 0.3)], min_dur=11, cam=(1.0, 1.1, 1200, 600),
   prompt='Alex and Mira freeze; Viktor\'s loud voice calls from the forest; a white shape between trees.')


sc(70, 5, [('N', 'Двенадцатое правило. Мы с Мирой больше не отходили друг от друга ни на шаг.')], nb(12), amb='forest', mus='sad', sfx=[(0.8, 'pen_write', 0.5)], min_dur=6, cam=(1.0, 1.05, 960, 500))


def v_r13_car_radio(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0b0d12'))
    # car interior dashboard
    c.drawPath(poly([(0, 600), (W, 560), (W, H), (0, H)]), paint('#16181d'))
    rrect(c, 760, 680, 400, 160, 16, paint('#0e1014'))
    rrect(c, 790, 700, 340, 70, 8, paint('#ff9d3b' if int(t * 2) % 2 == 0 else '#c06a1d'))
    text(c, 'ЭКСТРЕННО', 960, 750, 44, '#2a1400', FONT_MONO, align='center')
    # windshield night forest
    c.drawPath(poly([(100, 80), (1820, 80), (1700, 560), (220, 600)]), paint('#0c1428'))
    for i in range(12):
        tree(c, 200 + i * 140, 560, 0.6, '#070b16', seed=i)
    moon(c, 1500, 180, 50)
    person(c, 520, 1350, 1.1, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.6, mouth=0.0, t=t, tint='#9aa3c0')
    alex(c, 1400, 1380, 1.12, look=-0.6, mouth=0.0, t=t, tint='#9aa3c0')
    card(c, t, 13)


sc(71, 5, [('N', 'Правило номер тринадцать. Никогда не игнорируй экстренные предупреждения.'),
           ('TV', 'Внимание. Последняя эвакуация с северного шоссе. Сегодня, в шесть ноль-ноль. Конвой не будет ждать.'),
           ('MIRA', 'Это новое сообщение. Его раньше не было. Значит, оно настоящее.')],
   v_r13_car_radio, amb='car_inside', mus='tense', sfx=[(0.2, 'radio_static', 0.4), (3.6, 'eas_tone', 0.35)], min_dur=13,
   cam=(1.0, 1.06, 960, 600), prompt='Inside an abandoned car at night: emergency message on the car radio, Alex and Mira listen.')


def v_r13_siren(c, t, T, q):
    forest_road(c, t, headlights=True)
    # distant floodlights
    for x in (880, 1040):
        circle(c, x, 715, 9, paint(C('#ffffff', 0.9)))
        circle(c, x, 715, 90, paint(C('#ffffff', 0.15), blur=40))
    person(c, 820, 1150, 0.7, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.0, mouth=0.0, t=t, walk=t, tint=DARK_TINT)
    alex(c, 1060, 1160, 0.72, look=0.0, mouth=0.0, t=t, walk=t, tint=DARK_TINT)


sc(72, 5, [('N', 'Мы шли всю ночь. К рассвету впереди показались прожекторы. Автобусы. Военные грузовики.'),
           ('W', 'Люди. Живые люди.')],
   v_r13_siren, amb='forest', mus='hope', sfx=[(2.0, 'engine_far', 0.4)], min_dur=9, cam=(1.0, 1.12, 960, 650),
   prompt='Dawn: floodlights of an evacuation convoy appear ahead on the forest road.')


sc(73, 5, [('N', 'Тринадцатое правило.')], nb(13), amb='wind', mus='hope', sfx=[(0.8, 'pen_write', 0.5)], min_dur=4.2, cam=(1.0, 1.05, 960, 500))


def v_r14_convoy(c, t, T, q):
    sky(c, '#26304f', '#7d7f99')
    rect(c, 0, 760, W, 320, paint('#2a2c33'))
    # buses / trucks
    for i, x in enumerate((100, 760, 1400)):
        rrect(c, x, 470, 560, 300, 20, paint(['#c9a227', '#4b5d3a', '#4b5d3a'][i]))
        for k in range(6):
            rect(c, x + 30 + k * 85, 510, 65, 90, paint('#1d2433'))
        circle(c, x + 110, 780, 50, paint('#111'))
        circle(c, x + 450, 780, 50, paint('#111'))
    # soldier
    person(c, 1750, 1060, 0.62, coat='#4b5d3a', cap='#3a4a2a', hair='#222', look=-0.5, mouth=0.0, t=t, arms='point', tint='#c9ccd9')
    # man running back with suitcase
    mx = lerp(1000, -100, seg(t, q.s(1), q.s(1) + 5))
    person(c, mx, 1060, 0.6, coat='#7a2d2d', hair='#2a1a10', look=-0.8, mouth=0.4, t=t, walk=t * 2, flip=True, tint='#c9ccd9')
    card(c, t, 14)


sc(74, 5, [('N', 'Правило номер четырнадцать. Никогда не возвращайся за вещами.'),
           ('N', 'Посадка уже шла, когда один мужчина вспомнил про свой чемодан. Он оставил его у шлагбаума, в двухстах метрах.')],
   v_r14_convoy, amb='convoy', mus='tense', sfx=[(0.0, 'engine_idle', 0.4)], min_dur=12, cam=(1.0, 1.05, 960, 600),
   prompt='Evacuation convoy at dawn: buses, military trucks; a man runs back for his suitcase.')


def v_r14_wheels(c, t, T, q):
    sky(c, '#26304f', '#7d7f99')
    rect(c, 0, 700, W, 380, paint('#2a2c33'))
    fog(c, t, 700, 0.3, col='#d0d4e4', n=8)
    # suitcase rolling
    mx = lerp(1500, 600, seg(t, 0, T))
    person(c, mx, 1000, 0.6, coat='#7a2d2d', hair='#2a1a10', look=0.8, mouth=0.1, t=t, walk=t * 2, tint='#c9ccd9')
    rrect(c, mx + 120, 840, 120, 160, 10, paint('#3a5a7a'))
    circle(c, mx + 140, 1005, 10, paint('#111'))
    circle(c, mx + 220, 1005, 10, paint('#111'))
    sound_waves(c, mx + 180, 1000, t, 0.8)
    for i in range(6):
        k = seg(t, 2 + i * 0.5, 4 + i * 0.5)
        listener(c, 200 + i * 300, 760, 0.3, turn=0.5 - i * 0.15, t=t + i, alpha=k, glow=0.3, dark=0.2)


sc(75, 5, [('W', 'Колёсики чемодана громко застучали по асфальту.'),
           ('N', 'Из тумана вдоль дороги начали выходить белые фигуры. Одна. Пять. Двадцать.')],
   v_r14_wheels, amb='convoy', mus='action', sfx=[(0.0, 'wheels', 0.7), (3.0, 'crowd_shuffle', 0.6), (4.0, 'porcelain', 0.5)],
   min_dur=9, cam=(1.0, 1.05, 960, 600), prompt='A man drags a rattling suitcase; white creatures emerge from the fog along the road.')


def v_r14_leave(c, t, T, q):
    sky(c, '#26304f', '#7d7f99')
    rect(c, 0, 760, W, 320, paint('#2a2c33'))
    off = ease_in(seg(t, 1.0, T)) * 2400
    for i, x in enumerate((100, 760, 1400)):
        rrect(c, x + off, 470, 560, 300, 20, paint(['#c9a227', '#4b5d3a', '#4b5d3a'][i]))
        for k in range(6):
            rect(c, x + off + 30 + k * 85, 510, 65, 90, paint('#1d2433'))
        circle(c, x + off + 110, 780, 50, paint('#111'))
        circle(c, x + off + 450, 780, 50, paint('#111'))
    fog(c, t, 760, 0.3, col='#d0d4e4', n=8)
    person(c, 700, 1080, 0.68, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.9, mouth=0.4, t=t, tint='#c9ccd9')
    alex(c, 940, 1090, 0.7, look=0.9, mouth=0.4, t=t, arms='reach', tint='#c9ccd9')
    for i in range(5):
        listener(c, 1500 + i * 90, 900 + (i % 2) * 40, 0.36, turn=-0.7, t=t + i, glow=0.3, dark=0.2, alpha=seg(t, i * 0.3, 1 + i * 0.3))


sc(76, 5, [('N', 'Конвой ушёл раньше срока. Двери закрывались на ходу.'),
           ('W', 'Мы с Мирой не успели. Мы помогали старушке подняться в автобус. Её успели посадить. Нас — нет.')],
   v_r14_leave, amb='convoy', mus='action', sfx=[(0.5, 'engine_away', 0.8), (1.5, 'door_slam_bus', 0.5)], min_dur=11,
   cam=(1.0, 1.04, 960, 600), prompt='The convoy drives away early; Alex and Mira are left behind as creatures approach.')


sc(77, 5, [('N', 'Четырнадцатое правило. Чемодан так и остался лежать на дороге.')], nb(14), amb='wind', mus='sad', sfx=[(0.8, 'pen_write', 0.5)], min_dur=6, cam=(1.0, 1.05, 960, 500), fade_out=0.6)


# ===================================================================== PART 6 — ПРАВИЛО 15

sc(78, 6, [], v_chapter(6, 'ПРАВИЛО 15'), amb='none', mus='dread', sfx=[(0.2, 'boom', 0.8)], min_dur=3.4)


def v_inst_ext(c, t, T, q):
    institute_ext(c, t)
    person(c, 900, 1040, 0.36, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', t=t, walk=t * 0.6, tint=DARK_TINT)
    alex(c, 1010, 1046, 0.37, t=t, walk=t * 0.6, tint=DARK_TINT)


sc(79, 6, [('N', 'Единственным зданием рядом с шоссе оказался старый научный институт за бетонным забором.'),
           ('N', 'На вывеске было написано: «НИИ акустических исследований».'),
           ('W', 'Тогда это название ещё ничего для меня не значило.')],
   v_inst_ext, amb='wind', mus='dread', sfx=[(1.0, 'gate_creak', 0.5)], min_dur=11, cam=(1.12, 1.0, 960, 360),
   prompt='Night exterior: a grim concrete institute behind a fence, sign НИИ АКУСТИЧЕСКИХ ИССЛЕДОВАНИЙ.')


def v_watch(c, t, T, q):
    office(c, t)
    # Mira sleeping on the floor
    rrect(c, 120, 900, 520, 90, 40, paint('#3a4a6a'))
    c.save()
    c.translate(220, 900)
    c.rotate(-90)
    c.restore()
    oval(c, 200, 900, 70, 60, paint('#e9b997'))
    oval(c, 200, 870, 80, 45, paint('#6b2f1a'))
    alex(c, 900, 1080, 0.85, look=0.9, mouth=0.0, t=t, arms='hold', eyes='normal', tint='#b4b9cc')


sc(80, 6, [('N', 'Мы забаррикадировали дверь в кабинете на втором этаже. Мира уснула первой.'),
           ('N', 'Я дежурил. Было три часа ночи, когда в коридоре кто-то остановился у двери.')],
   v_watch, amb='room_night', mus='tense', sfx=[(6.5, 'creature_step', 0.5), (7.6, 'creature_step', 0.5)], min_dur=10,
   cam=(1.0, 1.08, 960, 560), prompt='Barricaded office at night, desk lamp, Mira sleeps on the floor, Alex keeps watch.')


def v_own_voice(c, t, T, q):
    office(c, t, lamp_on=True)
    alex(c, 900, 1300, 1.35, look=1.0, mouth=0.5, eyes='wide', t=t, arms='tense', sweat=2, tint='#b4b9cc')
    if q.talk(0, t) or q.talk(1, t):
        sound_waves(c, 1500, 500, t, 0.8, dirn=-1)


sc(81, 6, [('MIMA', 'Мира... Мира, открой. Это я, Алекс.'),
           ('W', 'Это был мой голос. Мой собственный голос. За дверью.')],
   v_own_voice, amb='room_night', mus='dread', sfx=[(0.0, 'knock_soft', 0.5)], min_dur=8, cam=(1.0, 1.15, 950, 380),
   prompt='Close-up: Alex hears his own voice behind the door, terrified.')


def v_mira_wakes(c, t, T, q):
    office(c, t, lamp_on=True)
    k = ease(seg(t, 0.4, 2.0))
    person(c, lerp(300, 1100, k), 1080, 0.85, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=1.0, mouth=0.1, t=t, walk=t if k < 1 else 0, tint='#b4b9cc')
    alex(c, 600, 1080, 0.88, look=1.0, mouth=0.0, t=t, arms='reach' if t > 2 else 'tense', sweat=2, tint='#b4b9cc')


sc(82, 6, [('N', 'Мира проснулась и пошла к двери. Полусонная. Она не поняла, что я стою у неё за спиной.'),
           ('W', 'Я успел схватить её за руку в последний момент.')],
   v_mira_wakes, amb='room_night', mus='dread', sfx=[(0.6, 'footsteps_soft', 0.4)], min_dur=10, cam=(1.0, 1.06, 900, 560),
   prompt='Mira half-asleep walks toward the door; Alex grabs her hand from behind.')


def v_door_knock2(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0d0e12'))
    door(c, 760, 120, 400, 840, col='#3d434e', chain=False, peephole=False, knob='#aaa', shake=0.6 if (t % 1.3) < 0.2 else 0, t=t)
    rect(c, 760, 955, 400, 8, paint(C('#ffffff', 0.25)))
    # shadow legs under the door gap
    for x in (900, 1010):
        rect(c, x, 955, 30, 8, paint('#000000'))


sc(83, 6, [('MIMA', 'Мам, где ты? Перезвони мне, пожалуйста.'),
           ('W', 'Эти слова я сказал в первый день. В пустой комнате, в телефон, на автоответчик.'),
           ('W', 'Значит, оно было рядом с самого начала. Оно слышало меня. И запомнило.')],
   v_door_knock2, amb='room_night', mus='dread', sfx=[(0.0, 'knock_soft', 0.6), (6.0, 'scratch', 0.5)], min_dur=13, cam=(1.0, 1.15, 960, 500),
   prompt='The door from inside, a thin light strip under it broken by two thin shadows; knocking.')


def v_rule15(c, t, T, q):
    black(c)
    a = seg(t, 0.3, 1.0)
    rule_card(c, 15, RULE_TITLES[14], RULE_SUBS[14], a, t)
    alex(c, 1450, 1380, 1.3, look=0.2, mouth=0.0, t=t, arms='cover', sweat=2, tint='#8f97b8')
    person(c, 1050, 1380, 1.2, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.8, mouth=0.0, t=t, arms='cover', tint='#8f97b8')


sc(84, 6, [('N', 'Правило номер пятнадцать. Если слышишь свой голос снаружи — не отвечай. Никогда.'),
           ('W', 'Потому что если ответишь... оно узнает, что настоящий — внутри.')],
   v_rule15, amb='room_night', mus='dread', sfx=[(0.2, 'boom', 0.8)], min_dur=10, cam=(1.0, 1.05, 960, 540),
   prompt='Rule 15 card; Alex and Mira cover their mouths in darkness.')


def v_silence_hold(c, t, T, q):
    office(c, t, lamp_on=False)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.45)))
    alex(c, 820, 1080, 0.86, look=1.0, mouth=0.0, t=t, arms='cover', sweat=2, tint='#7d849e')
    person(c, 560, 1080, 0.84, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=1.0, mouth=0.0, t=t, arms='cover', tint='#7d849e')


sc(85, 6, [('W', 'Мы просидели, зажав рты, до самого рассвета.'),
           ('N', 'Голос за дверью повторял мои слова снова и снова. А потом — просто замолчал.')],
   v_silence_hold, amb='room_night', mus='silence', sfx=[(0.5, 'heartbeat', 0.6)], min_dur=9, cam=(1.0, 1.08, 700, 560),
   prompt='Darkness: Alex and Mira sit still, hands over mouths, until dawn.')


sc(86, 6, [('N', 'Пятнадцатое правило. Последнее, которое я записал в эту тетрадь.')], nb(15), amb='room_dawn', mus='sad', sfx=[(0.8, 'pen_write', 0.5)], min_dur=6.5, cam=(1.0, 1.05, 960, 500), fade_out=0.8)


# ===================================================================== PART 7 — ФИНАЛ

sc(87, 7, [], v_chapter(7, 'ЗАПИСЬ'), amb='none', mus='dread', sfx=[(0.2, 'boom', 0.8)], min_dur=3.4)


def v_basement(c, t, T, q):
    lab(c, t, lamp=0.0)
    # flashlight cone
    c.drawPath(poly([(400, H), (560, H), (1300, 640), (900, 560)]), paint('#000', shader=lin(500, H, 1100, 600, [C('#fff6c8', 0.35), C('#fff6c8', 0.05)])))
    person(c, 300, 1150, 0.75, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.7, mouth=0.0, t=t, tint='#8f97b8')
    alex(c, 520, 1160, 0.78, look=0.7, mouth=0.0, t=t, arms='flash', item='flashlight', tint='#8f97b8')
    # recorder on table
    rrect(c, 1040, 650, 90, 160, 14, paint('#1d1f24'))
    rrect(c, 1052, 670, 66, 40, 4, paint('#2a2d33'))


sc(88, 7, [('N', 'Утром мы спустились в подвал института. Там была лаборатория. Стены обиты звукоизоляцией.'),
           ('N', 'На столе, среди пыльных бумаг, лежал старый диктофон.')],
   v_basement, amb='lab_hum', mus='tense', sfx=[(0.3, 'footsteps_soft', 0.35), (3.0, 'drip', 0.3)], min_dur=11,
   cam=(1.0, 1.1, 1000, 600), prompt='Basement acoustic lab with foam walls; flashlight beam reveals an old dictaphone on a table.')


def v_recorder_close(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#121317'))
    circle(c, 960, 540, 800, paint(C('#ffe7a8', 0.10), blur=140))
    c.save()
    c.translate(960, 560)
    c.rotate(-6)
    rrect(c, -230, -420, 460, 840, 60, paint('#1d1f24'))
    rrect(c, -230, -420, 460, 840, 60, paint('#3a3d44', 'stroke', 6))
    rrect(c, -170, -340, 340, 200, 16, paint('#3fe07a' if t > 1.2 else '#24452f'))
    if t > 1.2:
        text(c, 'ФАЙЛ 001', -150, -280, 40, '#0d2a16', FONT_MONO)
        text(c, '14.03.2019', -150, -220, 46, '#0d2a16', FONT_MONO)
        text(c, '03:12', -150, -165, 40, '#0d2a16', FONT_MONO)
    for k in range(8):
        circle(c, -120 + (k % 4) * 80, 0 + (k // 4) * 80, 14, paint('#0f1013'))
    circle(c, -90, 260, 46, paint('#c0392b'))
    circle(c, 90, 260, 46, paint('#3a3d44'))
    c.drawPath(poly([(70, 235), (70, 285), (115, 260)]), paint('#ffffff'))
    c.restore()
    # finger pressing play
    k = ease(seg(t, 0.2, 1.1)) * (1 - ease(seg(t, 1.4, 2.2)))
    oval(c, 1060 + 100 * (1 - k), 820 + 200 * (1 - k), 70, 110, paint(SKIN))


sc(89, 7, [('N', 'На нём была всего одна запись. Я нажал кнопку воспроизведения.')],
   v_recorder_close, amb='lab_hum', mus='silence', sfx=[(1.1, 'tape_click', 0.9), (1.3, 'tape_hiss', 0.6)], min_dur=6.5, cam=(1.0, 1.1, 960, 450),
   prompt='Extreme close-up: dictaphone display ФАЙЛ 001, a finger presses play.')


def v_recorder_play(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#08090b'))
    # waveform
    talk = q.talk(0, t)
    for i in range(120):
        x = 160 + i * 13.5
        h = 10 + (abs(math.sin(i * 0.7 + t * 9)) * 160 * (talk > 0) + abs(math.sin(i * 1.3 + t * 3)) * 20)
        rrect(c, x, 540 - h / 2, 8, h, 4, paint(C('#3fe07a', 0.9)))
    text(c, '▶ 00:0' + str(int(t) % 10), 160, 300, 46, '#3fe07a', FONT_MONO)


sc(90, 7, [('MIMA', 'Алекс. Я знаю, что ты слушаешь.')],
   v_recorder_play, amb='lab_hum', mus='silence', sfx=[(0.0, 'tape_hiss', 0.5)], min_dur=6.0, lead=1.6, tail=2.0,
   cam=(1.0, 1.08, 960, 540), prompt='Black screen with a green audio waveform: the recording speaks.')


def v_date_reveal(c, t, T, q):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0d0e10'))
    rrect(c, 360, 240, 1200, 600, 30, paint('#24452f'))
    rrect(c, 380, 260, 1160, 560, 24, paint('#3fe07a'))
    text(c, 'ДАТА ЗАПИСИ:', 960, 420, 70, '#0d2a16', FONT_MONO, align='center')
    k = seg(t, 1.0, 1.4)
    text(c, '14.03.2019', 960, 600, 170, C('#0d2a16', k), FONT_MONO, align='center')
    if t > 4:
        rrect(c, 0, 900, W, 120, 0, paint(C('#000000', 0.0)))


sc(91, 7, [('MIRA', 'Алекс... посмотри на дату.'),
           ('W', 'Запись была сделана за семь лет до того утра, когда город замолчал.'),
           ('W', 'За семь лет до первого Слушающего. Это был мой голос. Голос, которого у меня тогда ещё не было.')],
   v_date_reveal, amb='lab_hum', mus='dread', sfx=[('L0+1.2', 'stinger', 0.8)], min_dur=13, cam=(1.0, 1.12, 960, 520),
   prompt='Dictaphone display: recording date 14.03.2019 — seven years before the outbreak.')


def v_final_corridor(c, t, T, q):
    corridor(c, t, flicker=1.0, col='#0b0c10', wall='#14161c', floor='#0a0b0d', ceil='#0c0d10')
    k = seg(t, 0, T)
    listener(c, 960, 860 + 120 * ease(k), 0.5 + 0.35 * ease(k), turn=lerp(0.6, 0.0, ease(seg(t, 2.5, 6.0))), tilt=lerp(-14, 0, seg(t, 3, 6)), t=t, glow=0.9, dark=0.25)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.2)))


sc(92, 7, [('N', 'Мы выбежали из лаборатории в коридор.'),
           ('W', 'В конце коридора, в темноте, стоял он. И медленно повернул голову к нам.'),
           ('W', 'Как будто ждал. Как будто знал, что мы придём.')],
   v_final_corridor, amb='drone_room', mus='dread', sfx=[(3.0, 'porcelain', 0.7), (0.5, 'heartbeat', 0.7), ('L2+1.5', 'riser', 0.7)], min_dur=12,
   cam=(1.0, 1.35, 960, 420), tail=1.8, prompt='Final shot: dark flickering corridor, the white creature at the end slowly turns its head toward camera; slow push-in.')


def v_end(c, t, T, q):
    black(c)
    a = seg(t, 1.0, 2.5)
    text(c, 'СЛУШАЮЩИЕ ВЕРНУТСЯ', W / 2, H / 2 + 10, 96, C('#ffffff', a), align='center')
    b = seg(t, 3.0, 4.0)
    text(c, 'THE LISTENERS WILL RETURN', W / 2, H / 2 + 90, 36, C('#e53935', b), FONT_XB, align='center')
    k = seg(t, 5.0, 6.5)
    text(c, 'Какое правило нарушил бы ты? Напиши в комментариях — шёпотом.', W / 2, H - 120, 32, C('#9aa0aa', k), FONT_XB, align='center')


sc(93, 7, [], v_end, amb='none', mus='end', sfx=[(0.0, 'hit', 1.0), (1.0, 'boom', 0.7)], min_dur=10, fade_out=1.5,
   prompt='Black screen: СЛУШАЮЩИЕ ВЕРНУТСЯ / THE LISTENERS WILL RETURN.')
