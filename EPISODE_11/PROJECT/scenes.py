"""Episode 11 - 'What if people could read each other's minds?'  Shots + timeline."""
import math, random
import skia
from engine import *

# ------------------------------------------------------------------ strings
LANG = {
    'ru': dict(
        title=['ЧТО, ЕСЛИ ЛЮДИ', 'СМОГУТ ЧИТАТЬ', 'МЫСЛИ', 'ДРУГ ДРУГА?'], day='ДЕНЬ',
        live='ПРЯМОЙ ЭФИР', banner='СРОЧНО: ЛЮДИ СЛЫШАТ МЫСЛИ ДРУГ ДРУГА',
        ticker='УЧЁНЫЕ НЕ МОГУТ ОБЪЯСНИТЬ ФЕНОМЕН  •  ГОРОДА ПО ВСЕМУ МИРУ СООБЩАЮТ О СТРАННЫХ СЛУЧАЯХ  •  ',
        feed=['Я СЛЫШУ МЫСЛИ!', 'ДЕНЬ 3: КАК ЖИТЬ?', 'ЧТО ДУМАЕТ УЧИТЕЛЬ', 'ЭТО НЕ ФЕЙК', 'ПРОВЕРКА СПОСОБНОСТИ',
              'МОЙ СОСЕД ДУМАЕТ...', 'ПОЧЕМУ ЭТО ПРОИЗОШЛО?', 'ТИШИНА БОЛЬШЕ НЕ ТИХАЯ'],
        shop='ПРОДУКТЫ', episode='ВЫПУСК 11',
        final='А теперь представь, что завтра ты сможешь услышать мысли только одного человека.',
        final2='Кого бы ты выбрал?', views='тыс. просмотров'),
    'en': dict(
        title=['WHAT IF PEOPLE', 'COULD READ', 'EACH OTHER\'S', 'MINDS?'], day='DAY',
        live='LIVE', banner='BREAKING: PEOPLE CAN HEAR EACH OTHER\'S THOUGHTS',
        ticker='SCIENTISTS CANNOT EXPLAIN THE PHENOMENON  •  CITIES AROUND THE WORLD REPORT STRANGE CASES  •  ',
        feed=['I CAN HEAR THOUGHTS!', 'DAY 3: HOW TO LIVE?', 'WHAT MY TEACHER THINKS', 'THIS IS NOT FAKE',
              'TESTING THE ABILITY', 'MY NEIGHBOR THINKS...', 'WHY DID THIS HAPPEN?', 'SILENCE IS NOT QUIET'],
        shop='GROCERY', episode='EPISODE 11',
        final='Now imagine that tomorrow you could hear only one person\'s thoughts.',
        final2='Who would you choose?', views='K views'),
}
TITLE_HL = {'ru': 2, 'en': 3}  # index of the highlighted title line

CYAN = '#8fd3ff'
VIOLET = '#b48cff'
MOM = Look(skin='#e2b48f', hair='#6a3f26', style='long', top='#8a5a52', pants='#3a3440', shoes='#4a3a3a', seed=5)
DAD = Look(skin='#d6a47c', hair='#2e2420', style='short', top='#4f6a7a', pants='#2a2e36', shoes='#2a2a2a',
           glasses=True, seed=6, width=1.08, height=1.06)
TEACHER = Look(skin='#dcae88', hair='#8e8e8e', style='bald', top='#7a6a52', shirt='#e0dccf', tie='#6a2e2e',
               pants='#3a3530', shoes='#2a2220', glasses=True, seed=7, width=1.1, height=1.08)
GIRL = Look(skin='#efc8a6', hair='#a8532a', style='long', top='#5a6e8a', pants='#2a2e3a', shoes='#d0d0d0', seed=9)
ANCHOR = Look(skin='#d9a985', hair='#2a1e18', style='short', top='#2a3248', shirt='#e8e4dc', tie='#8a2e32',
              pants='#22252e', seed=12)
SELLER = Look(skin='#c99670', hair='#3a2a20', style='short', top='#3f6a52', shirt='#e8e4dc', pants='#2a2e36', seed=31)


def head_of(x, y, s, look):
    return x, y - 568 * s * look.height


def closeup(c, look, turn=0.0, expr='neutral', blink=0.0, eye=(0, 0), t=0.0, tilt=0.0):
    """draw a person so the head centre is at (0,0): use with cam(c, 0, y, zoom)"""
    draw_person(c, 0, 568 * look.height, 1.0, look, turn=turn, expr=expr, blink=blink, eye=eye, t=t, shadow=False,
                tilt=tilt)


# ------------------------------------------------------------------ city
class City:
    def __init__(self, seed, x0=-1600, x1=4200):
        r = random.Random(seed)
        self.far, self.near = [], []
        x = x0
        while x < x1:
            w = r.uniform(160, 320)
            self.far.append((x, w, r.uniform(380, 900), [r.random() for _ in range(80)]))
            x += w + r.uniform(-30, 10)
        x = x0
        while x < x1:
            w = r.uniform(280, 520)
            self.near.append((x, w, r.uniform(420, 700), r.choice(['#5a4a44', '#4a4f5a', '#6a5a4a', '#3e4a4e',
                                                                   '#584848', '#4c5248']),
                              [r.random() for _ in range(80)], r.random()))
            x += w + r.uniform(0, 30)


CITY = City(4)


def bg_city(c, t, camx=0.0, mood='day', ground=1330, lamps=True):
    sky = {'day': ('#5d7590', '#d8b898'), 'dusk': ('#2b2f4a', '#c9876a'), 'night': ('#0b0f1c', '#2a3048'),
           'morning': ('#6f8aa6', '#f0d2a8'), 'grey': ('#55606e', '#a8acb0')}[mood]
    c.drawRect(skia.Rect.MakeLTRB(-3000, -3000, 6000, ground + 10), P(shader=lin(0, -200, 0, ground, sky)))
    if mood == 'night':
        particles(c, 0, n=60, seed=8, area=(-400, -200, 1500, 600), h='#ffffff', a=0.5, size=1.6)
    night = mood in ('night', 'dusk')
    # far layer
    farc = mix(sky[0], '#1a1c26', 0.45)
    c.save()
    c.translate(-camx * 0.35, 0)
    for (x, w, h, rnd) in CITY.far:
        top = ground - 260 - h
        rect(c, x, top, x + w, ground, P(farc))
        if night or mood == 'dusk':
            k = 0
            for yy in range(int(top) + 30, ground - 300, 46):
                for xx in range(int(x) + 18, int(x + w) - 20, 34):
                    k += 1
                    if rnd[k % 80] > 0.62:
                        rect(c, xx, yy, xx + 14, yy + 20, P('#ffd68a', 0.55 * rnd[(k * 7) % 80]))
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(-3000, ground - 700, 6000, ground), P(shader=lin(0, ground - 700, 0, ground,
                                                                                    [(sky[1], 0), (sky[1], 0.35)])))
    # near layer (storefronts)
    c.save()
    c.translate(-camx * 0.7, 0)
    for (x, w, h, col, rnd, rr) in CITY.near:
        cc = shade(col, 0.45) if mood == 'night' else (shade(col, 0.75) if mood == 'dusk' else col)
        top = ground - 120 - h
        rect(c, x, top, x + w, ground, P(cc))
        rect(c, x, top, x + w, top + 18, P(shade(cc, 0.8)))
        for i, yy in enumerate(range(int(top) + 50, ground - 330, 92)):
            for j, xx in enumerate(range(int(x) + 30, int(x + w) - 60, 78)):
                lit = rnd[(i * 5 + j) % 80]
                wc = '#ffd98e' if (night and lit > 0.45) else ('#9fb4c4' if not night else '#2a3040')
                rect(c, xx, yy, xx + 46, yy + 58, P(wc, 0.9 if night else 0.75), r=3)
                if not night:
                    rect(c, xx, yy, xx + 46, yy + 20, P('#ffffff', 0.18), r=3)
        # shop window + awning
        sx0, sx1 = x + 26, x + w - 26
        rect(c, sx0, ground - 270, sx1, ground - 40, P('#ffdca0' if night else '#38434e', 0.85 if night else 1))
        if not night:
            rect(c, sx0, ground - 270, sx1, ground - 200, P('#ffffff', 0.08))
        aw = ['#8a3a34', '#3a5a6a', '#6a6a3a', '#5a3a5a'][int(rr * 4)]
        c.drawPath(poly([(sx0 - 14, ground - 300), (sx1 + 14, ground - 300), (sx1 + 30, ground - 250),
                         (sx0 - 30, ground - 250)]), P(shade(aw, 0.6 if night else 1)))
        for k in range(int((sx1 - sx0) / 40)):
            if k % 2:
                c.drawPath(poly([(sx0 - 14 + k * 40, ground - 300), (sx0 + 26 + k * 40, ground - 300),
                                 (sx0 + 26 + k * 40 + 4, ground - 250), (sx0 - 14 + k * 40 - 4, ground - 250)]),
                           P('#ffffff', 0.12))
    c.restore()
    # sidewalk
    c.drawRect(skia.Rect.MakeLTRB(-3000, ground, 6000, 4000),
               P(shader=lin(0, ground, 0, ground + 700, ['#4a4c54' if not night else '#20222a',
                                                         '#2c2e34' if not night else '#121318'])))
    c.save()
    c.translate(-camx, 0)
    for k in range(-30, 60):
        x = k * 220
        line(c, x, ground + 6, x - 260, ground + 700, P('#000000', 0.12, stroke=3))
    if lamps:
        for k in range(-8, 16):
            x = k * 760 + 300
            rect(c, x - 7, ground - 620, x + 7, ground + 20, P('#2a2c32'))
            rect(c, x - 7, ground - 620, x + 60, ground - 606, P('#2a2c32'))
            if night or mood == 'dusk':
                circle(c, x + 52, ground - 596, 18, P('#ffe2a8'))
                circle(c, x + 52, ground - 596, 160, P('#ffd58a', 0.18, blur=60))
                oval(c, x + 52, ground + 60, 220, 40, P('#ffd58a', 0.12, blur=30))
    c.restore()
    if not night:
        c.drawRect(skia.Rect.MakeLTRB(-3000, -3000, 6000, ground),
                   P(shader=lin(0, 0, 0, ground, [('#ffffff', 0.0), ('#fff2dc', 0.07)])))


class Walker:
    def __init__(self, seed, x0, v, depth):
        self.look = random_look(seed)
        self.x0, self.v, self.depth, self.seed = x0, v, depth, seed


def make_crowd(seed, n, x0=-300, x1=1400, vmin=90, vmax=150, dmin=0.0, dmax=1.0, bothdir=True):
    r = random.Random(seed)
    out = []
    for i in range(n):
        v = r.uniform(vmin, vmax) * (r.choice([-1, 1]) if bothdir else 1)
        out.append(Walker(seed * 100 + i, r.uniform(x0, x1), v, r.uniform(dmin, dmax)))
    out.sort(key=lambda w: w.depth)
    return out


def crowd_pos(w, tau, x0=-500, x1=1600, ground=1330, near=1620, smin=0.5, smax=0.95):
    span = x1 - x0
    x = x0 + ((w.x0 + w.v * tau - x0) % span)
    s = lerp(smin, smax, w.depth)
    y = lerp(ground + 40, near, w.depth)
    return x, y, s


def draw_crowd(c, walkers, tau, t, fog=None, exclude=lambda w: False, **kw):
    heads = []
    for w in walkers:
        if exclude(w):
            continue
        x, y, s = crowd_pos(w, tau, **kw)
        ph = (w.x0 + w.v * tau) / (95.0 * s) * (1 if w.v > 0 else -1)
        draw_person(c, x, y, s, w.look, facing=1 if w.v > 0 else -1, walk=ph, t=t + w.seed,
                    blink=blink_at(t, w.seed))
        heads.append((head_of(x, y, s, w.look), s, w))
        if fog and w.depth < 0.35:
            pass
    return heads


# ------------------------------------------------------------------ overlays
def day_card(c, n, u, L, dur=1.9):
    if u > dur:
        return
    a = ramp(u, 0, 0.25) * (1 - ramp(u, dur - 0.45, dur))
    c.drawRect(skia.Rect.MakeWH(W, H), P('#05060a', 0.55 * a))
    y = 760
    sc = 1 + 0.04 * u
    c.save()
    c.translate(W / 2, y)
    c.scale(sc, sc)
    s = f"{L['day']} {n}"
    jit = 5 * (1 - ramp(u, 0.0, 0.4))
    text(c, s, -jit, 0, 190, '#ff4a6a', 0.55 * a, tf=TF_BOLD, spacing=14)
    text(c, s, jit, 0, 190, CYAN, 0.55 * a, tf=TF_BOLD, spacing=14)
    text(c, s, 0, 0, 190, '#f2f2f2', a, tf=TF_BOLD, spacing=14)
    w = 360 * ramp(u, 0.15, 0.7)
    rect(c, -w, 50, w, 56, P('#f2f2f2', 0.8 * a))
    c.restore()


def mind_noise(c, t, n, seed=1, a=0.5, area=(0, 300, W, 1300), h=CYAN):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(area[0], area[2])
        y = r.uniform(area[1], area[3])
        wave_line(c, x, y + math.sin(t + i) * 20, r.uniform(120, 260), t + i, h=h, a=a * r.uniform(0.4, 1),
                  amp=r.uniform(6, 16), stroke=3)


def shake(c, t, amt, seed=0):
    if amt > 0:
        c.translate(noise1(t * 9, seed) * amt, noise1(t * 9 + 50, seed) * amt)


# ================================================================== SHOTS
# every shot: f(c, u, d, L, k) where u=local time, d=duration, k=dict of extra cue times (local)

CROWD1 = make_crowd(1, 16)


def sh_title(c, u, d, L, k):
    c.save()
    z = 1.0 + 0.04 * u
    cam(c, 540, 1100, z)
    bg_city(c, u, 0, 'dusk')
    draw_crowd(c, CROWD1, u, u, smax=0.8)
    draw_person(c, 540, 1560, 0.95, HERO, t=u, blink=blink_at(u, 1), expr='neutral')
    c.restore()
    vignette(c, 0.75)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 900), P(shader=lin(0, 0, 0, 900, [('#05060a', 0.85), ('#05060a', 0)])))
    hl = TITLE_HL[L['_code']]
    for i, s in enumerate(L['title']):
        a = ramp(u, 0.15 + i * 0.18, 0.6 + i * 0.18)
        y = 260 + i * 118 + (1 - a) * 30
        col = CYAN if i == hl else '#f4f4f4'
        if i == hl:
            text(c, s, W / 2, y, 118, CYAN, 0.45 * a, tf=TF_BOLD, paint=P(CYAN, 0.5 * a, blur=14))
        text(c, s, W / 2, y, 112, col, a, tf=TF_BOLD)
    text(c, L['episode'], W / 2, 150, 40, '#c9cbd4', 0.8 * ramp(u, 0.0, 0.4), tf=TF_MED, spacing=6)


def sh_street_intro(c, u, d, L, k):
    slow = k.get('slow', d * 0.5)
    tau = u if u < slow else slow + (u - slow) * 0.18
    pz = ease(u / d)
    c.save()
    cam(c, 540, lerp(1100, 1020, pz), lerp(1.0, 1.9, pz))
    bg_city(c, tau, 0, 'morning')
    heads = draw_crowd(c, CROWD1, tau + 20, u, smax=0.8)
    expr = 'surprised' if u > slow + 0.3 else 'neutral'
    eye = (math.sin(u * 2) * 0.6, 0) if u > slow + 0.3 else (0, 0)
    draw_person(c, 540, 1560, 0.95, HERO, t=u, blink=blink_at(u, 2), expr=expr, eye=eye)
    if u > slow:
        a = ramp(u, slow, slow + 0.8)
        for (hx_, hy_), s, w in heads:
            rings(c, hx_, hy_, u + w.seed * 0.3, CYAN, rmax=200 * s, r0=70 * s, a=0.55 * a, w=3)
        rings(c, 540, 1560 - 568 * 0.95, u * 1.3, VIOLET, rmax=330, r0=90, a=0.5 * a, w=4)
    c.restore()
    if u > slow:
        grade(c, '#6a7ab0', 0.25 * ramp(u, slow, slow + 0.8))
    vignette(c, 0.7)


def sh_eyes(c, u, d, L, k):
    c.drawRect(skia.Rect.MakeWH(W, H), P('#16161c'))
    c.save()
    z = lerp(5.2, 5.6, u / d)
    shake(c, u, 2.0)
    cam(c, 0, 10, z)
    draw_head(c, HERO, 84, 0, 'surprised', blink_at(u + 1.3, 0), eye=(0, 0), t=u)
    # ring reflections inside eyes
    for sgn in (-1, 1):
        x = sgn * 84 * 0.27
        for i in range(2):
            ph = (u * 0.9 + i * 0.5) % 1
            circle(c, x, 5, 4 + ph * 9, P(CYAN, 0.7 * (1 - ph), stroke=1.2))
    c.restore()
    rings(c, W / 2, 900, u, VIOLET, rmax=900, r0=200, a=0.3, w=6)
    vignette(c, 0.8)


def _kitchen_bg(c, u):
    c.drawRect(skia.Rect.MakeLTRB(-400, -400, 1500, 1400), P(shader=lin(0, 0, 0, 1400, ['#5a4a40', '#3e342e'])))
    # window
    rect(c, 70, 420, 430, 880, P('#f7e6c0'))
    rect(c, 70, 420, 430, 880, P('#4a3a30', stroke=18))
    line(c, 250, 420, 250, 880, P('#4a3a30', stroke=12))
    line(c, 70, 650, 430, 650, P('#4a3a30', stroke=12))
    circle(c, 330, 520, 60, P('#fff8e0', 0.9, blur=30))
    # cabinets
    for i in range(3):
        rect(c, 520 + i * 180, 300, 680 + i * 180, 620, P('#6e5a48'), r=6)
        rect(c, 600 + i * 180 - 30, 560, 600 + i * 180 + 30, 572, P('#c8b48a'), r=4)
    # counter
    rect(c, 470, 960, 1200, 1010, P('#8a7a68'))
    rect(c, 470, 1010, 1200, 1400, P('#5e4c3e'))
    # fridge
    rect(c, 900, 520, 1120, 1400, P('#c8ccd0'), r=14)
    line(c, 900, 820, 1120, 820, P('#9aa0a6', stroke=6))
    rect(c, 920, 700, 934, 790, P('#8a9096'), r=4)
    # floor
    c.drawRect(skia.Rect.MakeLTRB(-400, 1400, 1500, 2600), P(shader=lin(0, 1400, 0, 2200, ['#6a5444', '#3a2e26'])))
    for i in range(-6, 14):
        line(c, i * 140, 1400, i * 220 - 300, 2400, P('#000000', 0.12, stroke=3))
    light_beam(c, [(70, 420), (430, 420), (1100, 1750), (380, 1900)], a=0.22)
    particles(c, u, n=30, seed=4, area=(150, 500, 900, 1600), h='#fff1d0', a=0.6, size=2.4)


def sh_kitchen(c, u, d, L, k):
    c.save()
    cam(c, lerp(560, 520, u / d), 1150, lerp(1.0, 1.08, u / d))
    _kitchen_bg(c, u)
    # parents seated behind table
    talk = max(0, math.sin(u * 9)) if u < 0.9 else 0
    draw_person(c, 300, 1720, 0.82, MOM, turn=0.35, t=u, blink=blink_at(u, 3), expr='smile', eye=(0.6, 0))
    draw_person(c, 640, 1720, 0.86, DAD, turn=-0.2, t=u + 1, blink=blink_at(u, 4), expr='neutral',
                hands=[None, None], eye=(-0.3, 0.4))
    # table
    rect(c, 80, 1330, 900, 1365, P('#a0805e'), r=8)
    rect(c, 110, 1365, 870, 1700, P('#6a4e38'))
    oval(c, 300, 1322, 70, 14, P('#f0ece4'))
    rect(c, 600, 1260, 660, 1328, P('#d0d6dc'), r=8)
    for i in range(3):  # steam
        ph = (u * 0.5 + i / 3) % 1
        x = 630 + math.sin(u * 2 + i * 2) * 14
        circle(c, x, 1240 - ph * 160, 10 + ph * 16, P('#ffffff', 0.25 * (1 - ph), blur=6))
    # hero enters from right
    walk_in = ramp(u, 0, 1.0)
    hx = lerp(1250, 900, walk_in)
    draw_person(c, hx, 1760, 0.95, HERO, facing=-1, walk=u * 5 if u < 1.0 else None, t=u,
                blink=blink_at(u, 5), expr='surprised' if u > 1.4 else 'neutral', turn=-0.85)
    # thoughts
    a1 = ramp(u, 1.1, 1.5)
    if a1 > 0:
        rings(c, 300, 1720 - 568 * 0.82 * MOM.height, u, CYAN, rmax=190, r0=60, a=0.6 * a1, w=3)
        bubble(c, 230, 860, 120, u, appear=(u - 1.1) / 0.5, icon='money', from_=(290, 1180), seed=1)
        bubble(c, 520, 760, 100, u, appear=(u - 1.6) / 0.5, icon='clock', from_=(560, 1170), seed=2)
    c.restore()
    vignette(c, 0.6)


CROWD2 = make_crowd(2, 22, vmin=80, vmax=140)
ICONS = ['house', 'clock', 'money', 'heart', 'food', 'phone', 'question', 'bolt', 'exam', 'speech', 'zzz', 'cart']


def sh_street_walk(c, u, d, L, k):
    hx = 300 + u * 150
    c.save()
    cam(c, hx + 140, 1080, 1.05)
    bg_city(c, u, hx - 300, 'day')
    heads = draw_crowd(c, [w for w in CROWD2 if w.depth < 0.55], u, u, x0=hx - 1000, x1=hx + 1300)
    draw_person(c, hx, 1520, 0.92, HERO, facing=1, walk=u * 5.2, t=u, blink=blink_at(u, 6),
                expr='surprised' if u < d * 0.4 else 'worried', turn=0.9, eye=(0.4, -0.2))
    heads += draw_crowd(c, [w for w in CROWD2 if w.depth >= 0.55], u, u, x0=hx - 1000, x1=hx + 1300)
    # thoughts increase over time
    frac = ease(u / d)
    for i, ((x, y), s, w) in enumerate(heads):
        start = (w.seed % 17) / 17 * d * 0.85
        if u > start and (i / max(1, len(heads))) < 0.25 + frac:
            ap = (u - start) / 0.4
            bubble(c, x + 40 * s, y - 210 * s, 95 * s + 20, u, appear=ap, icon=ICONS[w.seed % len(ICONS)],
                   from_=(x, y - 90 * s), seed=w.seed, a=0.85)
            rings(c, x, y, u + w.seed, CYAN, rmax=170 * s, r0=60 * s, a=0.35, w=2.5)
    c.restore()
    mind_noise(c, u, int(2 + 10 * frac), seed=3, a=0.35 * frac)
    vignette(c, 0.55)


def sh_ears(c, u, d, L, k):
    lift = ramp(u, 0.1, 0.55)
    c.save()
    shake(c, u, 4 * ramp(u, 0.4, 1.2))
    cam(c, 540, 1000 + 0 * u, lerp(1.6, 1.85, u / d))
    bg_city(c, u + 5, 600, 'day')
    draw_crowd(c, CROWD2, u * 0.3 + 9, u, x0=-400, x1=1600)
    c.drawRect(skia.Rect.MakeLTRB(-1000, -1000, 3000, 3000), P('#1a1a2a', 0.45))
    hy = 1560 - 568 * 0.95
    hands = [(lerp(-50, -88, lift), lerp(-210, -568, lift)), (lerp(50, 88, lift), lerp(-210, -568, lift))]
    draw_person(c, 540, 1560, 0.95, HERO, t=u, expr='scared' if u > 0.4 else 'worried',
                blink=0.9 if 0.6 < u < 1.4 else 0, hands=hands if lift > 0.01 else None, tilt=-3 * lift)
    for i in range(5):
        rings(c, 540, hy, u * 1.4 + i * 0.2, [CYAN, VIOLET, '#ff7a9a'][i % 3], rmax=520, r0=100, a=0.45, w=4)
    c.restore()
    mind_noise(c, u, 14, seed=5, a=0.5, h='#c6a8ff')
    grade(c, '#8a4a7a', 0.25 + 0.1 * math.sin(u * 8))
    vignette(c, 0.8)


def sh_school_ext(c, u, d, L, k):
    c.save()
    cam(c, 540, 1060, lerp(1.0, 1.06, u / d))
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 1400), P(shader=lin(0, 0, 0, 1300, ['#7790aa', '#e3c9a6'])))
    # school building
    rect(c, -100, 520, 1180, 1330, P('#9a6a52'))
    rect(c, -100, 500, 1180, 540, P('#6e4c3c'))
    for row in range(3):
        for col in range(6):
            x = -40 + col * 210
            y = 580 + row * 230
            if row == 2 and col in (2, 3):
                continue
            rect(c, x, y, x + 120, y + 150, P('#b8d0dc'))
            rect(c, x, y, x + 120, y + 150, P('#e9e2d6', stroke=10))
            line(c, x + 60, y, x + 60, y + 150, P('#e9e2d6', stroke=6))
    rect(c, 400, 1050, 680, 1330, P('#3a2e28'))
    rect(c, 420, 1070, 535, 1330, P('#6a8494'))
    rect(c, 545, 1070, 660, 1330, P('#6a8494'))
    rect(c, 380, 990, 700, 1050, P('#e9e2d6'), r=6)
    circle(c, 540, 420, 70, P('#e9e2d6'))
    circle(c, 540, 420, 70, P('#6e4c3c', stroke=10))
    line(c, 540, 420, 540, 375, P('#3a2e28', stroke=7))
    line(c, 540, 420, 572, 430, P('#3a2e28', stroke=7))
    c.drawRect(skia.Rect.MakeLTRB(-500, 1330, 1600, 2600), P(shader=lin(0, 1330, 0, 2000, ['#8a8478', '#4a463e'])))
    for i, (x0, v, s) in enumerate([(-100, 120, 0.55), (1150, -110, 0.6), (200, 90, 0.5), (900, -130, 0.65)]):
        x = x0 + v * u
        draw_person(c, x, 1400 + i * 18, s, random_look(70 + i), facing=1 if v > 0 else -1, walk=x / (95 * s), t=u)
    hx = lerp(150, 430, u / d)
    draw_person(c, hx, 1640, 0.85, HERO, facing=1, walk=hx / 80, t=u, turn=0.9, expr='worried',
                blink=blink_at(u, 7))
    c.restore()
    vignette(c, 0.55)
    day_card(c, 1, u, L, dur=min(1.9, d))


def _board(c, u, talking=True):
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 1500), P(shader=lin(0, 0, 0, 1400, ['#5d6e6a', '#3e4a48'])))
    rect(c, 110, 300, 970, 760, P('#2c4a3c'))
    rect(c, 110, 300, 970, 760, P('#7a5a3a', stroke=20))
    rect(c, 110, 760, 970, 778, P('#7a5a3a'))
    for i, s in enumerate(['x² − 5x + 6 = 0', '(x − 2)(x − 3) = 0', 'x = 2;  x = 3']):
        text(c, s, 170, 400 + i * 110, 62, '#e8eee6', 0.85, tf=TF_MED, align='left')
    c.drawPath(smooth([(620, 640), (700, 600), (820, 660), (900, 610)], close=False), P('#e8eee6', 0.6, stroke=4))
    # clock
    circle(c, 1040, 260, 46, P('#ecebe4'))
    line(c, 1040, 260, 1040 + 30 * math.sin(u), 260 - 30 * math.cos(u), P('#333333', stroke=5))


def sh_class_board(c, u, d, L, k):
    pz = ease(u / d)
    c.save()
    cam(c, lerp(540, 470, pz), lerp(1000, 1180, pz), lerp(1.0, 1.25, pz))
    _board(c, u)
    c.drawRect(skia.Rect.MakeLTRB(-500, 1050, 1600, 2600), P(shader=lin(0, 1050, 0, 2000, ['#6a5a48', '#3a3028'])))
    talk = abs(math.sin(u * 8)) if (u % 2.2) < 1.6 else 0
    draw_person(c, 760, 1150, 0.62, TEACHER, turn=-0.3, t=u, expr='talk', mouth=talk, blink=blink_at(u, 8),
                arms=(8, 4, 40 + 25 * math.sin(u * 2), 70 + 20 * math.sin(u * 2.3)))
    # teacher speech: clean, plain bubble
    a = ramp(u, 0.3, 0.7)
    layer(c, a * 0.95)
    rect(c, 520, 560, 960, 700, P('#ffffff'), r=26)
    c.drawPath(poly([(760, 700), (800, 700), (760, 760)]), P('#ffffff'))
    for i in range(3):
        rect(c, 560, 590 + i * 34, 560 + [360, 300, 200][i] * min(1, max(0, u - 0.4 - i * 0.3) * 1.5), 606 + i * 34,
             P('#9aa0aa'), r=6)
    c.restore()
    # students from behind (2 rows)
    for row, (yy, s, xs) in enumerate([(1520, 0.72, [160, 420, 680, 940]), (1880, 0.95, [120, 470, 820])]):
        for j, x in enumerate(xs):
            lk = HERO if (row == 1 and j == 1) else random_look(200 + row * 10 + j)
            draw_person(c, x, yy, s, lk, back=True, t=u + j, shadow=False)
            rect(c, x - 200, yy - 300 * s, x + 200, yy - 270 * s, P('#9a7a58'))
            rect(c, x - 190, yy - 270 * s, x + 190, yy + 200, P('#5e4632'))
            # thoughts begin
            if not (row == 1 and j == 1):
                hx_, hy_ = head_of(x, yy, s, lk)
                bubble(c, hx_ + 30, hy_ - 150 * s, 70 * s + 20, u, appear=(u - 1.6 - j * 0.4 - row * 0.3) / 0.4,
                       icon=ICONS[(row * 4 + j * 3) % 12], from_=(hx_, hy_ - 60 * s), seed=row * 9 + j, a=0.8)
    c.restore()
    vignette(c, 0.6)


def _class_front(c, u, k, girl_glow=0.0, desat=0.0, freeze=False):
    tt = 0 if freeze else u
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 1500), P(shader=lin(0, 0, 0, 1300, ['#5a6a70', '#3e4a50'])))
    for i in range(3):
        x = 60 + i * 340
        rect(c, x, 240, x + 260, 760, P('#dfe8ea'))
        rect(c, x, 240, x + 260, 760, P('#e8e2d6', stroke=14))
        line(c, x + 130, 240, x + 130, 760, P('#e8e2d6', stroke=8))
    light_beam(c, [(60, 240), (1000, 240), (1300, 1500), (-200, 1500)], a=0.10)
    c.drawRect(skia.Rect.MakeLTRB(-500, 1100, 1600, 2600), P(shader=lin(0, 1100, 0, 2000, ['#6a5a48', '#3a3028'])))
    heads = []
    rows = [(1240, 0.5, [170, 400, 650, 890]), (1530, 0.68, [150, 540, 930]), (1880, 0.9, [210, 860])]
    for row, (yy, s, xs) in enumerate(rows):
        for j, x in enumerate(xs):
            if row == 1 and j == 1:
                lk = HERO
            elif row == 2 and j == 0:
                lk = GIRL
            else:
                lk = random_look(300 + row * 10 + j)
            expr, eye = 'neutral', (0, 0)
            if lk is HERO:
                expr = 'worried' if u > k.get('t10', 99) else ('surprised' if u > 0.4 else 'neutral')
                if freeze:
                    expr = 'shock'
                eye = (math.sin(u * 3) * 0.8, 0) if not freeze else (-1, 0.5)
            elif lk is GIRL:
                expr = 'sad' if freeze else 'neutral'
            draw_person(c, x, yy, s, lk, t=tt + j + row, blink=0 if freeze else blink_at(u, row * 5 + j),
                        expr=expr, eye=eye, turn=(0.15 if lk is GIRL else (x - 540) / 1600), shadow=False)
            rect(c, x - 175 * s / 0.7, yy - 300 * s, x + 175 * s / 0.7, yy - 268 * s, P('#a58560'))
            rect(c, x - 165 * s / 0.7, yy - 268 * s, x + 165 * s / 0.7, yy + 400, P('#664c36'))
            heads.append((head_of(x, yy, s, lk), s, lk, row, j))
    return heads


def sh_class_front(c, u, d, L, k):
    t10 = k.get('t10', d * 0.6)
    c.save()
    pz = ease(u / d)
    shake(c, u, 3 * ramp(u, t10, d))
    cam(c, 540, lerp(1050, 1180, pz), lerp(1.0, 1.2, pz))
    heads = _class_front(c, u, k)
    # thoughts: one by one, then hundreds
    order = [(0, 1, 'exam', 0.2), (1, 0, 'house', k.get('t8b', 2.0)), (0, 3, 'speech', k.get('t9', 4.6)),
             (2, 1, 'clock', t10 - 0.2), (0, 0, 'food', t10), (0, 2, 'phone', t10 + 0.2), (1, 2, 'heart', t10 + 0.4)]
    for (row, j, icon, st) in order:
        for (hp, s, lk, rr, jj) in heads:
            if rr == row and jj == j:
                bubble(c, hp[0] + 20, hp[1] - 190 * s, 150 * s + 10, u, appear=(u - st) / 0.4, icon=icon,
                       from_=(hp[0], hp[1] - 90 * s), seed=row * 5 + j)
                if u > st:
                    rings(c, hp[0], hp[1], u + j, CYAN, rmax=200 * s, r0=80 * s, a=0.4, w=3)
    c.restore()
    if u > t10:
        f = ramp(u, t10, d)
        r = random.Random(4)
        for i in range(int(40 * f)):
            x, y = r.uniform(60, 1020), r.uniform(250, 1300)
            bubble(c, x, y + math.sin(u * 2 + i) * 10, r.uniform(26, 50), u, appear=(u - t10 - i * 0.05) / 0.3,
                   icon=None, h='#dff0ff', a=0.35, seed=i)
        mind_noise(c, u, int(16 * f), seed=6, a=0.45 * f)
        grade(c, '#7a5a9a', 0.2 * f)
    vignette(c, 0.6)


def sh_freeze(c, u, d, L, k):
    t12 = k.get('t12', d * 0.5)
    if u < t12:
        c.save()
        cam(c, lerp(540, 380, ease(u / t12)), lerp(1150, 1300, ease(u / t12)), lerp(1.15, 1.5, ease(u / t12)))
        heads = _class_front(c, 0.0, k, freeze=True)
        c.restore()
        grade(c, '#808080', 0.9 * ramp(u, 0, 0.4), skia.BlendMode.kSaturation)
        c.drawRect(skia.Rect.MakeWH(W, H), P('#0a0a12', 0.35 * ramp(u, 0, 0.4)))
        # girl highlight (redrawn in colour)
        c.save()
        cam(c, lerp(540, 380, ease(u / t12)), lerp(1150, 1300, ease(u / t12)), lerp(1.15, 1.5, ease(u / t12)))
        hp = head_of(210, 1880, 0.9, GIRL)
        circle(c, hp[0], hp[1], 260, P(VIOLET, 0.25 * ramp(u, 0.3, 1.0), blur=60))
        draw_person(c, 210, 1880, 0.9, GIRL, t=0, expr='sad', turn=0.15, shadow=False, eye=(0.8, -0.4))
        rect(c, 210 - 225, 1880 - 270, 210 + 225, 1880 - 241, P('#a58560'))
        rect(c, 210 - 212, 1880 - 241, 210 + 212, 2400, P('#664c36'))
        rings(c, hp[0], hp[1], u, VIOLET, rmax=380, r0=100, a=0.6 * ramp(u, 0.4, 1.0), w=4)
        c.restore()
        vignette(c, 0.8)
    else:
        v = u - t12
        dd = d - t12
        hero_cut = dd * 0.72
        c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#262634', '#14141c'])))
        if v < hero_cut:
            c.save()
            cam(c, 0, -120, lerp(3.2, 3.5, v / dd))
            circle(c, 0, -60, 260, P(VIOLET, 0.25, blur=60))
            closeup(c, GIRL, 0.2, 'sad', blink_at(v, 2), (-0.6, 0.3), v)
            c.restore()
            bubble(c, 700, 470, 230, v, appear=v / 0.5, icon='broken', dark=True, glow=VIOLET, seed=4,
                   from_=(560, 760))
            rings(c, 540, 870, v, VIOLET, rmax=700, r0=220, a=0.35, w=5)
        else:
            w_ = v - hero_cut
            c.save()
            shake(c, w_, 3)
            cam(c, 0, -60, lerp(3.4, 3.0, w_ / max(0.1, dd - hero_cut)))
            closeup(c, HERO, -0.2, 'shock', 0, (-0.8, 0), w_)
            c.restore()
            grade(c, '#6a4a8a', 0.25)
        vignette(c, 0.8)


def draw_news(c, x0, y0, x1, y1, t, L, zoom=1.0):
    w, h = x1 - x0, y1 - y0
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), P(shader=lin(x0, y0, x1, y1, ['#1c3a6a', '#0e1a34'])))
    for i in range(6):
        circle(c, x0 + w * (0.15 + i * 0.15), y0 + h * 0.3, h * 0.25, P('#3a6ab0', 0.15, blur=20))
    # globe logo-ish
    cx, cy = x0 + w * 0.82, y0 + h * 0.36
    circle(c, cx, cy, h * 0.17, P('#5aa0e0', 0.35))
    rings(c, cx, cy, t, CYAN, rmax=h * 0.3, r0=h * 0.1, a=0.6, w=h * 0.01)
    s = h / 900.0
    draw_person(c, x0 + w * 0.38, y1 + h * 0.35, 1.25 * s * 1.6, ANCHOR, t=t, expr='talk',
                mouth=abs(math.sin(t * 9)) * (1 if (t % 2.5) < 2 else 0), blink=blink_at(t, 9), shadow=False)
    # lower third
    by = y1 - h * 0.27
    rect(c, x0, by, x1, by + h * 0.13, P('#c8283a'))
    rect(c, x0, by, x0 + w * 0.24, by + h * 0.13, P('#f2f2f2'))
    fl = h * 0.06
    while skia.Font(TF_BOLD, fl).measureText(L['live']) > w * 0.21:
        fl *= 0.95
    text(c, L['live'], x0 + w * 0.12, by + h * 0.065 + fl * 0.36, fl, '#c8283a', tf=TF_BOLD)
    bl = L['banner']
    fs = h * 0.058
    f = skia.Font(TF_BOLD, fs)
    while f.measureText(bl) > w * 0.72 and fs > 8:
        fs *= 0.95
        f = skia.Font(TF_BOLD, fs)
    text(c, bl, x0 + w * 0.26, by + h * 0.09, fs, '#ffffff', tf=TF_BOLD, align='left')
    # ticker
    ty = by + h * 0.13
    rect(c, x0, ty, x1, y1, P('#0a0f1e'))
    tk = L['ticker'] * 3
    fsz = h * 0.05
    off = (t * w * 0.18) % skia.Font(TF_MED, fsz).measureText(L['ticker'])
    text(c, tk, x0 + w * 0.02 - off, ty + h * 0.075, fsz, '#e0e6f0', tf=TF_MED, align='left')
    c.restore()


def sh_tv(c, u, d, L, k):
    cut = d * 0.52
    if u < cut:
        c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#141a26', '#0a0c12'])))
        c.save()
        cam(c, 540, 900, lerp(1.0, 1.25, u / cut))
        rect(c, 80, 560, 1000, 1110, P('#050608'), r=18)
        draw_news(c, 100, 580, 980, 1090, u, L)
        rect(c, 300, 1110, 780, 1150, P('#1a1c22'))
        c.drawRect(skia.Rect.MakeLTRB(-400, -400, 1500, 2400), P(shader=rad(540, 840, 1100, [('#5a8ad0', 0.18), ('#5a8ad0', 0)])))
        # family silhouettes on couch (backs)
        rect(c, -50, 1500, 1130, 1900, P('#1a1c24'), r=60)
        for x, lk in [(260, MOM), (540, HERO), (820, DAD)]:
            draw_person(c, x, 1900, 0.95, lk, back=True, t=u, shadow=False)
        rect(c, -80, 1660, 1160, 2200, P('#22242e'), r=50)
        c.restore()
        c.drawRect(skia.Rect.MakeWH(W, H), P('#0a1a3a', 0.15 + 0.05 * math.sin(u * 13), blend=skia.BlendMode.kScreen))
    else:
        v = u - cut
        c.save()
        cam(c, 540, lerp(980, 900, v / (d - cut)), lerp(1.0, 1.08, v / (d - cut)))
        bg_city(c, 0, 200, 'night', lamps=True)
        rect(c, 160, 220, 920, 1000, P('#1a1c24'))
        draw_news(c, 190, 260, 890, 700, u, L)
        c.drawRect(skia.Rect.MakeLTRB(-400, -400, 1500, 2400), P(shader=rad(540, 480, 900, [('#5a8ad0', 0.22), ('#5a8ad0', 0)])))
        r = random.Random(5)
        for i in range(14):
            x = r.uniform(-60, 1140)
            s = r.uniform(0.55, 0.85)
            y = 1350 + s * 500
            lk = random_look(400 + i)
            draw_person(c, x, y, s, lk, back=True, t=u + i, tilt=r.uniform(-6, 6))
            if r.random() < 0.4:
                hp = head_of(x, y, s, lk)
                rings(c, hp[0], hp[1], u + i, CYAN, rmax=120, r0=40, a=0.35, w=2)
        c.restore()
        vignette(c, 0.6)
    day_card(c, 3, u, L, dur=min(1.9, d * 0.45))


def sh_avoid(c, u, d, L, k):
    c.save()
    cam(c, lerp(500, 580, u / d), 1060, 1.05)
    bg_city(c, u, 900, 'grey', lamps=False)
    # bus stop shelter
    rect(c, 140, 900, 940, 1340, P('#c8dce6', 0.18))
    rect(c, 140, 900, 940, 1340, P('#3a3e46', stroke=12))
    rect(c, 120, 860, 960, 910, P('#3a3e46'))
    rect(c, 250, 1210, 830, 1240, P('#5a5248'))
    ppl = [(230, 0.86, -1, 41), (450, 0.9, 1, 42), (680, 0.84, -1, 43), (880, 0.88, 1, 44)]
    for i, (x, s, f, sd) in enumerate(ppl):
        lk = random_look(sd)
        turn_away = ramp(u, 0.3 + i * 0.25, 0.8 + i * 0.25)
        draw_person(c, x, 1480 + i % 2 * 30, s, lk, facing=f, turn=f * 0.9, t=u + i, blink=blink_at(u, sd),
                    expr='sad', eye=(0, 1), tilt=8 * turn_away, arms=(7, 4, 20, 4 + 130 * turn_away))
        hp = head_of(x, 1480 + i % 2 * 30, s, lk)
        bubble(c, hp[0] + f * 60, hp[1] - 160, 60, u, appear=(u - 0.4 - i * 0.3) / 0.4, icon='lock', dark=True,
               glow='#555577', seed=sd, from_=(hp[0], hp[1] - 80))
    c.restore()
    grade(c, '#5a6a80', 0.25)
    vignette(c, 0.65)


def _hallway(c):
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 1400), P(shader=lin(0, 0, 0, 1300, ['#6a7a7e', '#4a5458'])))
    for i in range(-3, 10):
        x = i * 130
        rect(c, x, 560, x + 122, 1320, P('#4e6a86'))
        rect(c, x + 20, 600, x + 102, 640, P('#3e5670'))
        rect(c, x + 98, 900, x + 108, 980, P('#c8ccd0'))
    c.drawRect(skia.Rect.MakeLTRB(-500, 1320, 1600, 2600), P(shader=lin(0, 1320, 0, 2000, ['#8a8478', '#55504a'])))


def sh_quarrel(c, u, d, L, k):
    A = random_look(51)
    B = random_look(57)
    c.save()
    shake(c, u, 2.5 * ramp(u, 1.0, 2.0))
    cam(c, 540, 1080, lerp(1.15, 1.35, u / d))
    _hallway(c)
    g = ramp(u, 0.6, 1.4)
    draw_person(c, 300, 1600, 0.95, A, facing=1, t=u, expr='angry' if u > 0.8 else 'neutral', blink=blink_at(u, 51),
                arms=(7, 4, 20 + 40 * g + 12 * math.sin(u * 7) * g, 4 + 150 * g))
    draw_person(c, 790, 1600, 0.95, B, facing=-1, t=u, expr='angry' if u > 1.1 else 'surprised',
                blink=blink_at(u, 57), arms=(7, 4, 15 + 35 * g, 4 + 120 * g + 20 * math.sin(u * 6) * g))
    bubble(c, 300, 720, 120, u, appear=(u - 0.3) / 0.4, icon='scribble', dark=True, glow='#ff5a5a', seed=8,
           from_=(300, 980))
    bubble(c, 790, 700, 110, u, appear=(u - 0.9) / 0.4, icon='bolt', dark=True, glow='#ff5a5a', seed=9,
           from_=(790, 980))
    c.restore()
    grade(c, '#a04a4a', 0.15 * g)
    vignette(c, 0.65)


def sh_fake_smile(c, u, d, L, k):
    woman = Look(skin='#e6bc98', hair='#3a2418', style='bob', top='#a07a5a', pants='#3a3440', seed=61)
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#b89a7a', '#5a4838'])))
    for i in range(7):  # bokeh cafe lights
        circle(c, 100 + i * 150, 300 + (i % 3) * 120, 50 + (i % 2) * 30, P('#ffe2a8', 0.25, blur=20))
    c.save()
    cam(c, 540, 820, lerp(1.0, 1.12, u / d))
    draw_person(c, 560, 1820, 1.75, woman, turn=-0.1, t=u, expr='smile', blink=blink_at(u, 61), eye=(-0.3, 0.2))
    c.restore()
    reveal = ramp(u, 0.9, 1.6)
    if reveal > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#10101a', 0.3 * reveal))
        bubble(c, 820, 330, 170, u, appear=(u - 0.9) / 0.5, icon='scribble', dark=True, glow='#ff6a6a', seed=10,
               from_=(680, 560))
        rings(c, 560, 820, u, '#ff7a8a', rmax=500, r0=200, a=0.4 * reveal, w=4)
    # hero foreground (over shoulder)
    c.save()
    c.translate(120, 1900)
    draw_person(c, 0, 1160, 2.4, HERO, back=True, t=u, shadow=False)
    c.restore()
    vignette(c, 0.65)


def sh_feed(c, u, d, L, k):
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#14161e', '#08090c'])))
    c.save()
    cam(c, 540, 960, lerp(1.0, 1.06, u / d))
    px0, py0, px1, py1 = 190, 280, 890, 1700
    c.drawRect(skia.Rect.MakeLTRB(-400, -400, 1500, 2400), P(shader=rad(540, 1000, 900, [('#6a8ad0', 0.18), ('#6a8ad0', 0)])))
    rect(c, px0 - 22, py0 - 22, px1 + 22, py1 + 22, P('#0c0d10'), r=70)
    c.save()
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(px0, py0, px1, py1), 50, 50)
    c.clipRRect(rr, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(px0, py0, px1, py1), P('#15171e'))
    scroll = u * 170
    cw, ch = (px1 - px0 - 48) / 2, 420
    cols = ['#3a4a6a', '#5a3a4a', '#3a5a4a', '#5a4a3a', '#4a3a6a', '#3a5a6a']
    for i in range(16):
        col, row = i % 2, i // 2
        x = px0 + 16 + col * (cw + 16)
        y = py0 + 120 + row * (ch + 20) - scroll
        if y > py1 or y + ch < py0:
            continue
        rect(c, x, y, x + cw, y + ch * 0.74, P(cols[i % 6]), r=16)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x, y, x + cw, y + ch * 0.74))
        lk = random_look(500 + i)
        draw_person(c, x + cw / 2, y + ch * 0.74 + 330, 0.62, lk, t=u + i, expr=['surprised', 'talk', 'shock',
                    'smile'][i % 4], mouth=abs(math.sin(u * 8 + i)), blink=blink_at(u, i), shadow=False)
        hp = head_of(x + cw / 2, y + ch * 0.74 + 330, 0.62, lk)
        rings(c, hp[0], hp[1], u + i * 0.3, CYAN, rmax=150, r0=50, a=0.5, w=2.5)
        c.restore()
        circle(c, x + cw / 2, y + ch * 0.37, 26, P('#000000', 0.35))
        c.drawPath(poly([(x + cw / 2 - 8, y + ch * 0.37 - 13), (x + cw / 2 + 14, y + ch * 0.37),
                         (x + cw / 2 - 8, y + ch * 0.37 + 13)]), P('#ffffff', 0.9))
        cap = L['feed'][i % len(L['feed'])]
        fs = 26
        while skia.Font(TF_BOLD, fs).measureText(cap) > cw - 10:
            fs -= 1
        text(c, cap, x + 4, y + ch * 0.74 + 38, fs, '#eef0f4', tf=TF_BOLD, align='left')
        text(c, f"{(i * 37) % 900 + 100} {L['views']}", x + 4, y + ch * 0.74 + 72, 22, '#8a8e98', tf=TF_MED,
             align='left')
    rect(c, px0, py0, px1, py0 + 100, P('#15171e'))
    rect(c, px0 + 40, py0 + 44, px0 + 150, py0 + 62, P('#d03a4a'), r=8)
    for i in range(3):
        circle(c, px1 - 60 - i * 50, py0 + 54, 14, P('#5a5e68'))
    c.restore()
    # hands
    for sgn in (-1, 1):
        x = 540 + sgn * 380
        oval(c, x, 1450, 70, 140, P(HERO.skin))
        oval(c, x - sgn * 40, 1350, 34, 22, P(shade(HERO.skin, 0.92)))
        rect(c, x - 80, 1560, x + 80, 2200, P(HERO.top), r=40)
    c.restore()
    vignette(c, 0.6)


def sh_watch(c, u, d, L, k):
    c.save()
    cam(c, 540, lerp(1000, 900, u / d), lerp(1.0, 1.15, u / d))
    bg_city(c, u, 100, 'night', ground=1180, lamps=False)
    for (x, y, w_, h_) in [(80, 700, 260, 150), (700, 620, 300, 170)]:
        draw_news(c, x, y, x + w_, y + h_, u, L)
        circle(c, x + w_ / 2, y + h_ / 2, w_, P('#4a8ad0', 0.18, blur=50))
    r = random.Random(11)
    for i in range(10):
        x, y = r.uniform(-100, 1180), r.uniform(800, 1150)
        rings(c, x, y, u * 0.6 + i * 0.37, CYAN, rmax=180, r0=10, a=0.4, w=2)
    # question in the sky
    a = ramp(u, d * 0.35, d * 0.7)
    text(c, '?', 540, 520, 300, '#c8d8ff', 0.18 * a, tf=TF_BLACK, paint=P('#a8c0ff', 0.25 * a, blur=20))
    # rooftop + railing
    rect(c, -400, 1500, 1500, 2600, P('#141620'))
    rect(c, -400, 1330, 1500, 1342, P('#2a2e3a'))
    for i in range(-3, 14):
        rect(c, i * 110, 1330, i * 110 + 10, 1500, P('#2a2e3a'))
    draw_person(c, 540, 1640, 1.05, HERO, back=True, t=u, shadow=False, tilt=2 * math.sin(u * 0.8))
    c.restore()
    vignette(c, 0.7)


CROWD3 = make_crowd(3, 34, vmin=60, vmax=120)


def sh_world(c, u, d, L, k):
    c.save()
    cam(c, 540, lerp(980, 1060, u / d), lerp(1.0, 1.12, u / d))
    bg_city(c, u, 300 + u * 20, 'dusk', ground=1050)
    heads = draw_crowd(c, CROWD3, u, u, x0=-500, x1=1600, ground=1050, near=1750, smin=0.32, smax=0.75)
    for (x, y), s, w in heads:
        rings(c, x, y, u + w.seed * 0.17, [CYAN, VIOLET][w.seed % 2], rmax=160 * s + 40, r0=40 * s, a=0.4, w=2.5)
        bubble(c, x + 20 * s, y - 230 * s, 110 * s, u, appear=(u - (w.seed % 13) * 0.12) / 0.4,
               icon=ICONS[w.seed % 12], h='#e6f2ff', a=0.55, seed=w.seed, from_=(x, y - 100 * s))
    c.restore()
    mind_noise(c, u, 10, seed=7, a=0.3)
    grade(c, '#6a5aa0', 0.18)
    vignette(c, 0.65)
    day_card(c, 5, u, L, dur=min(2.0, d * 0.4))


def sh_meeting(c, u, d, L, k):
    suits = [Look(skin=sk, hair=hr, style=st, top=tp, shirt='#e8e4dc', tie=tie, pants='#22252e', seed=80 + i,
                  glasses=(i == 2), width=1.08)
             for i, (sk, hr, st, tp, tie) in enumerate([('#d6a47c', '#8e8e8e', 'bald', '#2a2e3a', '#6a2e2e'),
                                                        ('#b98563', '#1a1414', 'short', '#3a3a44', '#2e4a6a'),
                                                        ('#e6b994', '#7a5a3a', 'short', '#2e3440', '#5a5a2e'),
                                                        ('#8f5e43', '#1a1414', 'short', '#3a3030', '#6a2e4a')])]
    c.save()
    cam(c, lerp(500, 580, u / d), 1050, lerp(1.08, 1.16, u / d))
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 2600), P('#2a2c34'))
    rect(c, -100, 280, 1180, 1050, P(shader=lin(0, 280, 0, 1050, ['#2a3a5a', '#7a6a7a'])))
    for i in range(12):
        x = -100 + i * 110
        rect(c, x, 700 - (i * 53 % 230), x + 90, 1050, P('#1e2434'))
    for i in range(-1, 6):
        rect(c, -100 + i * 260, 280, -88 + i * 260, 1050, P('#1a1c22'))
    rect(c, -500, 1050, 1600, 2600, P('#3a3634'))
    pos = [(160, 1, 0), (380, 1, 1), (700, -1, 2), (920, -1, 3)]
    for x, f, i in pos:
        draw_person(c, x, 1600, 0.85, suits[i], facing=f, turn=f * 0.85, t=u + i, blink=blink_at(u, 80 + i),
                    expr=['angry', 'smirk', 'worried', 'angry'][i], shadow=False)
    c.drawPath(poly([(-60, 1240), (1140, 1240), (1260, 1420), (-180, 1420)]), P('#5a3e2c'))
    rect(c, -180, 1420, 1260, 2600, P('#3e2a1e'))
    rect(c, -180, 1420, 1260, 1450, P('#2e1e14'))
    for x in (300, 800):
        rect(c, x - 60, 1260, x + 60, 1290, P('#e8e4dc'))
    for j, (x, f, i) in enumerate(pos):
        hp = head_of(x, 1600, 0.85, suits[i])
        bubble(c, hp[0], hp[1] - 200, 90, u, appear=(u - 0.2 - j * 0.25) / 0.4, icon=['money', 'lock', 'eye', 'bolt'][j],
               seed=j, from_=(hp[0], hp[1] - 100), a=0.85)
        rings(c, hp[0], hp[1], u + j, CYAN, rmax=170, r0=70, a=0.3, w=2)
    c.restore()
    vignette(c, 0.65)


def _shelves(c):
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 2600), P('#22252c'))
    r = random.Random(21)
    cols = ['#6a3a5a', '#a08a3a', '#3a6a4a', '#b05a3a', '#9a3a3a', '#d0c8b8', '#3a5a8a']
    for sh in range(5):
        y = 380 + sh * 230
        rect(c, -300, y + 150, 1400, y + 168, P('#9aa0a6'))
        x = -280
        while x < 1380:
            w_ = r.uniform(60, 100)
            col = r.choice(cols)
            if sh % 2:
                rect(c, x, y + 20, x + w_ * 0.6, y + 150, P(col), r=10)
                rect(c, x + w_ * 0.2, y - 10, x + w_ * 0.4, y + 30, P(col))
            else:
                rect(c, x, y + 10, x + w_, y + 150, P(col))
                rect(c, x, y + 50, x + w_, y + 70, P('#ffffff', 0.2))
            x += w_ + 10
    for x in (-60, 520, 1100):
        rect(c, x, 300, x + 26, 1500, P('#3a3e46'))


def sh_shop(c, u, d, L, k):
    cust = random_look(91)
    c.save()
    cam(c, lerp(520, 560, u / d), 1050, lerp(1.08, 1.15, u / d))
    _shelves(c)
    rect(c, 80, 170, 620, 290, P('#8a2a2a'))
    text(c, L['shop'], 350, 258, 92, '#e8d8c8', tf=TF_BOLD, spacing=6)
    c.drawRect(skia.Rect.MakeLTRB(-500, 0, 1600, 2600), P('#000000', 0.35))
    light_beam(c, [(600, 900), (1200, 600), (1300, 1500), (700, 1100)], a=0.10)
    # seller already holding the item
    draw_person(c, 780, 1500, 0.92, SELLER, turn=-0.5, t=u, expr='smirk', blink=blink_at(u, 31),
                hands=[None, None])
    hx = lerp(-100, 330, ramp(u, 0, 1.2))
    draw_person(c, hx, 1640, 0.95, cust, facing=1, walk=hx / 90 if u < 1.2 else None, t=u, blink=blink_at(u, 91),
                expr='surprised' if u > 1.3 else 'neutral')
    rect(c, 560, 1180, 1300, 1230, P('#8a7a68'))
    rect(c, 580, 1230, 1300, 1800, P('#4e4238'))
    # item in seller's hand already
    lift = ramp(u, 0.4, 1.0)
    iy = lerp(1240, 1100, lift)
    rect(c, 640, iy - 80, 720, iy, P('#b05a3a'), r=6)
    rect(c, 640, iy - 56, 720, iy - 40, P('#ffffff', 0.3))
    circle(c, 690, iy - 10, 22, P(SELLER.skin))
    hp = head_of(hx, 1640, 0.95, cust)
    bubble(c, hp[0] + 80, hp[1] - 190, 95, u, appear=(u - 0.2) / 0.4, icon='food', seed=3, from_=(hp[0], hp[1] - 90))
    hp2 = head_of(780, 1500, 0.92, SELLER)
    rings(c, hp2[0], hp2[1], u, CYAN, rmax=200, r0=70, a=0.4 * lift, w=3)
    c.restore()
    vignette(c, 0.65)


def sh_friends_secret(c, u, d, L, k):
    A = random_look(111)
    B = random_look(118)
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#6a5040', '#2e241e'])))
    for i in range(8):
        circle(c, 80 + i * 140, 360 + (i % 3) * 140, 40 + (i % 2) * 30, P('#ffd8a0', 0.25, blur=22))
    c.save()
    cam(c, 540, 1100, lerp(1.15, 1.3, u / d))
    draw_person(c, 300, 1720, 0.95, A, facing=1, t=u, expr='smile' if u < 0.9 else 'worried', blink=blink_at(u, 111),
                arms=(7, 4, 40, 70))
    draw_person(c, 790, 1720, 0.95, B, facing=-1, t=u, expr='talk' if u < 0.9 else 'shock',
                mouth=abs(math.sin(u * 8)) if u < 0.9 else 0, blink=blink_at(u, 118))
    rect(c, 120, 1330, 980, 1370, P('#8a6a4a'), r=10)
    rect(c, 500, 1370, 600, 1800, P('#4a3a2e'))
    rect(c, 330, 1270, 390, 1330, P('#e8e4dc'), r=8)
    rect(c, 690, 1270, 750, 1330, P('#e8e4dc'), r=8)
    hp = head_of(300, 1720, 0.95, A)
    reveal = ramp(u, 0.6, 1.1)
    bubble(c, hp[0] + 40, hp[1] - 210, 110, u, appear=(u - 0.5) / 0.4, icon='heart', seed=5, from_=(hp[0], hp[1] - 100),
           glow='#ff8aa8')
    if reveal > 0:
        rings(c, hp[0], hp[1], u, '#ff8aa8', rmax=260, r0=80, a=0.5 * reveal, w=3)
    c.restore()
    vignette(c, 0.65)


CROWD4 = make_crowd(4, 24, vmin=160, vmax=260)


def sh_crowd_lonely(c, u, d, L, k):
    pz = ease(u / d)
    c.save()
    cam(c, 540, lerp(1150, 860, pz), lerp(1.0, 2.3, pz))
    bg_city(c, u, 0, 'grey')
    heads = draw_crowd(c, [w for w in CROWD4 if w.depth < 0.5], u, u, x0=-600, x1=1700)
    c.drawRect(skia.Rect.MakeLTRB(-1000, -1000, 3000, 3000), P('#1a1c26', 0.4))
    circle(c, 540, 1100, 520, P('#ffe8c8', 0.12, blur=120))
    draw_person(c, 540, 1520, 0.92, HERO, t=u, expr='sad', blink=blink_at(u, 12), eye=(0, 0.6))
    heads2 = draw_crowd(c, [w for w in CROWD4 if w.depth >= 0.5], u, u, x0=-600, x1=1700)
    for (x, y), s, w in heads + heads2:
        bubble(c, x, y - 200 * s, 70 * s, u, appear=1, icon=ICONS[w.seed % 12], a=0.45, seed=w.seed, h='#d8e4f0')
    c.restore()
    grade(c, '#5a6a90', 0.3)
    vignette(c, 0.75)


def sh_hero_close(c, u, d, L, k):
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#2a2e3e', '#12141c'])))
    r = random.Random(3)
    for i in range(10):  # watching eyes in the dark
        x, y = r.uniform(60, 1020), r.uniform(200, 1500)
        if abs(x - 540) < 330 and 500 < y < 1300:
            continue
        a = ramp(u, 0.6 + i * 0.12, 1.0 + i * 0.12)
        c.save()
        c.translate(x, y)
        draw_icon(c, 'eye', 0, 0, 60, u)
        c.restore()
        c.drawRect(skia.Rect.MakeLTRB(x - 40, y - 30, x + 40, y + 30), P('#12141c', 1 - a))
    c.save()
    cam(c, 0, -40, lerp(3.4, 3.8, u / d))
    closeup(c, HERO, math.sin(u * 1.2) * 0.25, 'worried', blink_at(u, 13), (math.sin(u * 1.5), 0), u)
    c.restore()
    bubble(c, 820, 420, 150, u, appear=(u - 0.3) / 0.5, icon='lock' if u < d * 0.55 else 'crack', seed=7,
           from_=(700, 640))
    vignette(c, 0.75)


def _bedroom(c, u):
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 2600), P(shader=lin(0, 0, 0, 1700, ['#4a5468', '#2a2e3a'])))
    rect(c, 640, 360, 1000, 860, P('#fff2d6'))
    for i in range(9):
        rect(c, 640, 380 + i * 52, 1000, 404 + i * 52, P('#d8c8a8'))
    rect(c, 640, 360, 1000, 860, P('#3a3a44', stroke=16))
    light_beam(c, [(640, 360), (1000, 360), (500, 1500), (-100, 1400)], a=0.18)
    rect(c, 60, 420, 300, 720, P('#6a4a5a'))
    circle(c, 180, 540, 70, P('#c8a85a'))
    rect(c, 330, 470, 520, 640, P('#3a5a6a'))
    particles(c, u, n=25, seed=9, area=(200, 400, 1000, 1400), a=0.5, size=2)


def sh_wake(c, u, d, L, k):
    sit = ramp(u, d * 0.45, d * 0.6)
    c.save()
    cam(c, 540, lerp(1150, 1080, u / d), lerp(1.15, 1.25, u / d))
    _bedroom(c, u)
    rect(c, -60, 1180, 1140, 1240, P('#5a4a3a'), r=10)
    rect(c, -60, 1240, 1140, 1900, P('#e0dad0'))
    if sit < 0.5:
        oval(c, 300, 1220, 200, 70, P('#f2eee6'))
        c.save()
        c.translate(330, 1170)
        c.rotate(-80)
        opn = ramp(u, 1.0, 1.3)
        draw_head(c, HERO, 84, 0, 'neutral', 1 - opn, eye=(math.sin(u * 1.5) * 0.8, 0), t=u)
        c.restore()
        c.drawPath(smooth([(400, 1180), (1140, 1150), (1160, 1400), (380, 1420)]), P('#5a6a8a'))
    else:
        draw_person(c, 520, 1720, 1.0, HERO, t=u, expr='surprised', blink=blink_at(u, 14), eye=(math.sin(u * 1.2), 0))
        c.drawPath(smooth([(-80, 1450), (1160, 1420), (1160, 1900), (-80, 1900)]), P('#5a6a8a'))
    c.restore()
    vignette(c, 0.55)
    day_card(c, 7, u, L, dur=min(2.0, d * 0.35))


CROWD5 = make_crowd(5, 14, vmin=60, vmax=95)


def sh_quiet_street(c, u, d, L, k):
    hx = 300 + u * 110
    c.save()
    cam(c, hx + 120, 1060, 1.05)
    bg_city(c, u, hx - 300, 'morning')
    for i in range(4):  # birds
        bx = (i * 300 + u * 80) % 1600 - 200 + hx - 300
        by = 400 + i * 40 + math.sin(u * 2 + i) * 10
        fl = math.sin(u * 10 + i) * 10
        c.drawPath(poly([(bx - 16, by - fl), (bx, by), (bx + 16, by - fl)], close=False), P('#2a2a30', stroke=4))
    draw_crowd(c, [w for w in CROWD5 if w.depth < 0.55], u, u, x0=hx - 1000, x1=hx + 1300)
    draw_person(c, hx, 1520, 0.92, HERO, facing=1, walk=u * 4.2, t=u, blink=blink_at(u, 15), expr='neutral',
                turn=0.9, eye=(0.3, -0.3))
    draw_crowd(c, [w for w in CROWD5 if w.depth >= 0.55], u, u, x0=hx - 1000, x1=hx + 1300)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P('#ffe8c0', 0.08, blend=skia.BlendMode.kScreen))
    vignette(c, 0.45)


def _park(c, u, mood=0.0):
    c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 1350), P(shader=lin(0, 0, 0, 1350,
                                                                          [mix('#6a7aa0', '#2a2c48', mood),
                                                                           mix('#f0c090', '#c0705a', mood)])))
    circle(c, 820, 880, 110, P('#fff0c8', 0.7, blur=30))
    for i, (x, y, r) in enumerate([(-40, 900, 230), (240, 950, 180), (900, 920, 250), (1150, 980, 190), (560, 1000, 150)]):
        rect(c, x - 18, y, x + 18, 1350, P(mix('#3a2e2a', '#1a1418', mood)))
        circle(c, x, y - r * 0.4, r, P(mix('#4a6a48', '#22302a', mood)))
        circle(c, x - r * 0.4, y - r * 0.1, r * 0.7, P(mix('#3e5a3e', '#1c2822', mood)))
    c.drawRect(skia.Rect.MakeLTRB(-500, 1330, 1600, 2600), P(shader=lin(0, 1330, 0, 2100,
                                                                          [mix('#6a7a4a', '#2a3226', mood),
                                                                           mix('#3a4a2e', '#141a14', mood)])))
    c.drawPath(poly([(380, 1330), (700, 1330), (1300, 2600), (-200, 2600)]), P(mix('#b0a080', '#4a4238', mood)))
    particles(c, u, n=20, seed=13, area=(0, 600, 1080, 1500), h='#fff0c0', a=0.5, size=2.5)


def sh_meet(c, u, d, L, k):
    c.save()
    cam(c, 540, 1100, lerp(1.05, 1.18, u / d))
    _park(c, u, 0.15)
    fx = lerp(1200, 720, ramp(u, 0, d * 0.6))
    walking = u < d * 0.6
    draw_person(c, 360, 1600, 0.95, HERO, facing=1, t=u, blink=blink_at(u, 16), expr='neutral' if u < d * 0.5 else 'smile',
                turn=0.85, arms=(7, 4, 7 + 60 * ramp(u, d * 0.55, d * 0.7) * (1 - ramp(u, d * 0.85, d)), 4 + 120 * ramp(u, d * 0.55, d * 0.7) * (1 - ramp(u, d * 0.85, d))))
    draw_person(c, fx, 1610, 0.95, FRIEND, facing=-1, walk=fx / 80 if walking else None, t=u, blink=blink_at(u, 23),
                expr='calm', turn=-0.85)
    c.restore()
    vignette(c, 0.6)


def sh_friend_close(c, u, d, L, k):
    smile = k.get('smile', False)
    c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#7a6a8a', '#3a2e3e'])))
    for i in range(9):
        circle(c, 60 + i * 130, 400 + (i % 3) * 200, 50 + (i % 2) * 40, P('#ffd8a0', 0.2, blur=26))
    glow = 1.0 if not smile else 0.6
    circle(c, 540, 860, 520, P(VIOLET, 0.25 * glow, blur=100))
    c.save()
    cam(c, 0, -30, lerp(3.6, 3.9, u / d))
    ex = 'smirk' if (smile and u > 0.4) else 'calm'
    closeup(c, FRIEND, -0.3, ex, blink_at(u, 23), (-0.6, 0), u)
    if not smile:
        for sgn in (-1, 1):  # faint glow in the eyes while the voice speaks
            x = -0.3 * 84 * 0.44 + sgn * 84 * 0.27 * 0.9 - 0.6 * 84 * 0.06
            circle(c, x, 5, 9, P(VIOLET, 0.5 + 0.3 * math.sin(u * 5), blur=6))
    c.restore()
    if not smile:
        rings(c, 540, 900, u * 0.8, VIOLET, rmax=900, r0=320, a=0.45, w=6)
    vignette(c, 0.7)


def sh_look_smile(c, u, d, L, k):
    half = d * 0.45
    if u < half:
        c.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, 0, H, ['#6a6a8a', '#2e2a3a'])))
        circle(c, 300, 900, 600, P(VIOLET, 0.18, blur=100))
        c.save()
        cam(c, 0, -30, lerp(3.6, 3.8, u / half))
        closeup(c, HERO, 0.3, 'surprised', blink_at(u + 0.5, 17), (0.7, 0), u)
        c.restore()
        vignette(c, 0.7)
    else:
        sh_friend_close(c, u - half, d - half, L, {'smile': True})


def sh_final_close(c, u, d, L, k):
    pz = ease(u / d)
    c.save()
    z = lerp(3.5, 1.0, pz)
    cam(c, lerp(360, 540, pz), lerp(1600 - 568 * 0.95 - 20, 1150, pz), z)
    _park(c, u, 0.6 + 0.3 * pz)
    draw_person(c, 360, 1600, 0.95, HERO, facing=1, turn=0.6 - 0.4 * pz, t=u, blink=blink_at(u, 18),
                expr='surprised' if u < d * 0.4 else 'neutral', eye=(0.3, 0))
    draw_person(c, 720, 1610, 0.95, FRIEND, facing=-1, turn=-0.85, t=u, blink=blink_at(u, 23), expr='smirk')
    rings(c, 540, 1050, u * 0.5, VIOLET, rmax=600, r0=100, a=0.25 * pz, w=3)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', 0.85 * ramp(u, d * 0.55, d)))
    vignette(c, 0.8)


def sh_end(c, u, d, L, k):
    c.drawRect(skia.Rect.MakeWH(W, H), P('#050508'))
    particles(c, u, n=50, seed=17, area=(0, 0, W, H), h='#a8b8ff', a=0.25, size=1.6)
    vo_end = k.get('vo_end', d - 5)
    # row of silhouettes, one lights up
    a = ramp(u, 0.3, 1.5) * (1 - ramp(u, vo_end + 0.2, vo_end + 1.0))
    if a > 0:
        layer(c, a)
        for i in range(7):
            x = 90 + i * 150
            lk = random_look(700 + i) if i != 3 else FRIEND
            draw_person(c, x, 1300, 0.42, lk, back=False, t=u + i, shadow=False, blink=blink_at(u, i))
        c.drawRect(skia.Rect.MakeLTRB(0, 700, W, 1320), P('#050508', 0.75))
        sel = ramp(u, 2.0, 3.0)
        hp = head_of(540, 1300, 0.42, FRIEND)
        circle(c, hp[0], hp[1], 120, P(VIOLET, 0.35 * sel, blur=40))
        draw_person(c, 540, 1300, 0.42, FRIEND, t=u, shadow=False, expr='calm', blink=blink_at(u, 23))
        c.drawRect(skia.Rect.MakeLTRB(0, 700, W, 1320), P('#050508', 0.75 * (1 - sel)))
        rings(c, hp[0], hp[1], u, VIOLET, rmax=260, r0=60, a=0.5 * sel, w=3)
        c.restore()
    # final question card (after the voice ends)
    fa = ramp(u, vo_end + 0.6, vo_end + 1.6)
    if fa > 0:
        lines_ = wrap(L['final'], 66, 900)
        y0 = 760 - len(lines_) * 40
        for i, ln in enumerate(lines_):
            text(c, ln, W / 2, y0 + i * 86, 66, '#e8e8f0', fa, tf=TF_MED)
        q = ramp(u, vo_end + 1.6, vo_end + 2.4)
        yq = y0 + len(lines_) * 86 + 90
        text(c, L['final2'], W / 2, yq, 104, VIOLET, 0.6 * q, tf=TF_BOLD, paint=P(VIOLET, 0.6 * q, blur=16))
        text(c, L['final2'], W / 2, yq, 100, '#ffffff', q, tf=TF_BOLD)
        rings(c, W / 2, yq + 280, u, VIOLET, rmax=200, r0=20, a=0.4 * q, w=3)
    c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', ramp(u, d - 0.8, d)))


# ================================================================== timeline
def build_timeline(S, E, tail=5.5):
    end = E[-1] + tail
    sh = []

    def add(f, a, b, xf=0.35, **k):
        sh.append(dict(f=f, a=a, b=b, xf=xf, k=k))
    add(sh_title, 0, S[1] - 0.2, xf=0)
    add(sh_street_intro, S[1] - 0.2, E[1] - 0.7, slow=(S[1] + 0.55 * (E[1] - S[1])) - (S[1] - 0.2))
    add(sh_eyes, E[1] - 0.7, S[2] - 0.15, xf=0.12)
    add(sh_kitchen, S[2] - 0.15, S[3] - 0.15)
    add(sh_street_walk, S[3] - 0.15, S[5] - 0.1)
    add(sh_ears, S[5] - 0.1, S[6] - 0.2, xf=0.12)
    add(sh_school_ext, S[6] - 0.2, S[7] - 0.1)
    add(sh_class_board, S[7] - 0.1, S[8] - 0.1)
    a = S[8] - 0.1
    add(sh_class_front, a, S[11] - 0.1, t8b=(S[8] + E[8]) / 2 - a, t9=S[9] - a, t10=S[10] - a)
    a = S[11] - 0.1
    add(sh_freeze, a, S[13] - 0.3, xf=0.15, t12=S[12] - 0.2 - a)
    add(sh_tv, S[13] - 0.3, S[14] - 0.1)
    add(sh_avoid, S[14] - 0.1, S[15] - 0.1)
    add(sh_quarrel, S[15] - 0.1, S[16] - 0.1)
    add(sh_fake_smile, S[16] - 0.1, S[17] - 0.1)
    add(sh_feed, S[17] - 0.1, S[18] - 0.1)
    add(sh_watch, S[18] - 0.1, S[19] - 0.3)
    add(sh_world, S[19] - 0.3, S[21] - 0.1)
    add(sh_meeting, S[21] - 0.1, S[22] - 0.1)
    split = S[22] + 0.38 * (E[22] - S[22])
    add(sh_shop, S[22] - 0.1, split)
    add(sh_friends_secret, split, S[23] - 0.1)
    add(sh_crowd_lonely, S[23] - 0.1, S[24] - 0.1)
    add(sh_hero_close, S[24] - 0.1, S[25] - 0.3)
    add(sh_wake, S[25] - 0.3, S[26] - 0.1, xf=0.6)
    add(sh_quiet_street, S[26] - 0.1, S[28] - 0.1)
    add(sh_meet, S[28] - 0.1, S[29] - 0.2)
    add(sh_friend_close, S[29] - 0.2, S[30] - 0.1)
    add(sh_look_smile, S[30] - 0.1, S[31] - 0.1)
    add(sh_final_close, S[31] - 0.1, S[32] - 0.1)
    add(sh_end, S[32] - 0.1, end, xf=0.4, vo_end=E[-1] - (S[32] - 0.1))
    return sh, end


def render_frame(c, t, shots, L):
    idx = 0
    for i, s in enumerate(shots):
        if s['a'] <= t:
            idx = i
    s = shots[idx]
    if idx > 0 and t - s['a'] < s['xf']:
        p = shots[idx - 1]
        c.save()
        p['f'](c, t - p['a'], p['b'] - p['a'], L, p['k'])
        c.restore()
        layer(c, ease((t - s['a']) / s['xf']))
        s['f'](c, t - s['a'], s['b'] - s['a'], L, s['k'])
        c.restore()
    else:
        c.save()
        s['f'](c, t - s['a'], s['b'] - s['a'], L, s['k'])
        c.restore()
