"""Locations for THE LISTENERS (all procedural, flat cinematic style)."""
from gfx import *

NIGHT_TINT = '#8f9ac8'
DARK_TINT = '#6c7598'
DAWN_TINT = '#c9c6d6'


# ------------------------------------------------------------------ exterior
def city_bg(c, t, top='#0a0f2c', bot='#2b2f6a', moon_xy=(1480, 190), moon_r=105, seed=2, lit=0.08, horizon=760, far=True, stars_n=120, fog_a=0.12):
    sky(c, top, bot)
    if stars_n:
        stars(c, seed + 10, stars_n, t=t)
    if moon_xy:
        moon(c, moon_xy[0], moon_xy[1], moon_r)
    if far:
        skyline(c, horizon - 30, seed=seed + 5, col='#1b2152', lit=lit * 0.6, minh=200, maxh=520, bw=(60, 140))
    skyline(c, horizon, seed=seed, col='#11163a', lit=lit, minh=150, maxh=380)
    if fog_a:
        fog(c, t, horizon - 40, fog_a, n=6)


def road(c, horizon=760, col='#1b1e29', dash=True, t=0.0, wet=False):
    rect(c, 0, horizon, W, H - horizon, paint(col))
    rect(c, 0, horizon, W, 40, paint('#2a2e3b'))
    rect(c, 0, horizon + 40, W, 6, paint('#3a3f4e'))
    if dash:
        for x in range(-100, W + 100, 240):
            rect(c, x, horizon + 170, 130, 12, paint(C('#c9b45a', 0.8)))
    if wet:
        rect(c, 0, horizon + 50, W, H, paint('#000', shader=lin(0, horizon, 0, H, [C('#5b6bb5', 0.18), C('#000000', 0)])))


def street(c, t, seed=1, lamps=((280, 1), (1500, -1)), flicker=0.0, cars=None, moon_xy=(1480, 190), top='#0a0f2c', bot='#2b2f6a', lit=0.08, fog_a=0.16, dawn=False):
    if dawn:
        city_bg(c, t, '#2a3350', '#8a8fa8', moon_xy=None, seed=seed, lit=0.0, stars_n=0, fog_a=0.25)
        road(c, col='#3a3d48')
    else:
        city_bg(c, t, top, bot, moon_xy, seed=seed, lit=lit, fog_a=fog_a * 0.6)
        road(c)
    for lx, side in lamps:
        street_lamp(c, lx, 800, 520, flicker=flicker if lx == lamps[0][0] else 0, t=t, side=side, on=0 if dawn else 1)
    for cx_, cy_, s_, col_, kw in (cars or []):
        car(c, cx_, cy_, s_, col_, t=t, **kw)


def courtyard_block(c, t, lit_windows=None, music_win=None, tv_win=None, seed=4, top='#0a0f2c', bot='#262a5c', y0=60, dark=False):
    """A big soviet apartment block facing camera. Returns window grid geometry."""
    sky(c, top, bot)
    stars(c, seed, 60, t=t)
    moon(c, 1700, 120, 70)
    bx, by, bw, bh = 120, y0, 1680, 800
    rect(c, bx, by, bw, bh, paint('#2a2f4a' if not dark else '#1d2136'))
    rect(c, bx, by, bw, bh, paint('#000', shader=lin(0, by, 0, by + bh, [C('#ffffff', 0.04), C('#000000', 0.35)])))
    cols, rows = 12, 6
    r = random.Random(seed)
    geo = {}
    for i in range(cols):
        for j in range(rows):
            wx = bx + 60 + i * 134
            wy = by + 50 + j * 125
            geo[(i, j)] = (wx, wy, 74, 80)
            col = '#0d1020'
            if lit_windows and (i, j) in lit_windows:
                col = lit_windows[(i, j)]
            rect(c, wx - 6, wy - 6, 86, 92, paint('#3a4060'))
            rect(c, wx, wy, 74, 80, paint(col))
            line(c, wx + 37, wy, wx + 37, wy + 80, '#3a4060', 5)
            # balcony slabs
            if j % 2 == 1 and i % 3 == 0:
                rect(c, wx - 20, wy + 84, 114, 14, paint('#353b5a'))
    if music_win:
        wx, wy, ww, wh = geo[music_win]
        k = 0.6 + 0.4 * abs(math.sin(t * 8))
        hue = ['#ff3d7f', '#3dd6ff', '#ffd21e', '#8a5cff'][int(t * 4) % 4]
        rect(c, wx, wy, ww, wh, paint(C(hue, k)))
        circle(c, wx + ww / 2, wy + wh / 2, 150, paint(C(hue, 0.25 * k), blur=50))
    if tv_win:
        wx, wy, ww, wh = geo[tv_win]
        f = 0.7 + 0.3 * math.sin(t * 13) * math.sin(t * 5.3)
        rect(c, wx, wy, ww, wh, paint(C('#9ec5ff', f)))
        circle(c, wx + ww / 2, wy + wh / 2, 110, paint(C('#9ec5ff', 0.22 * f), blur=40))
    # ground
    rect(c, 0, 860, W, 220, paint('#161a2b'))
    rect(c, 0, 860, W, 14, paint('#262b42'))
    # entrance door + lamp
    rect(c, 900, 760, 120, 100, paint('#0a0c14'))
    rect(c, 890, 740, 140, 20, paint('#3a4060'))
    circle(c, 960, 728, 8, paint('#ffe08a'))
    circle(c, 960, 728, 60, paint(C('#ffe08a', 0.25), blur=25))
    # playground silhouettes
    line(c, 300, 1000, 300, 880, '#0e1120', 10)
    line(c, 460, 1000, 460, 880, '#0e1120', 10)
    line(c, 300, 880, 460, 880, '#0e1120', 10)
    line(c, 360, 880, 360, 960, '#0e1120', 4)
    line(c, 400, 880, 400, 960, '#0e1120', 4)
    rect(c, 350, 958, 60, 8, paint('#0e1120'))
    return geo


def forest_road(c, t, moon_xy=(1450, 170), headlights=False):
    sky(c, '#060a1c', '#1b2346')
    stars(c, 77, 140, t=t)
    moon(c, moon_xy[0], moon_xy[1], 90, ga=0.3)
    r = random.Random(11)
    for i in range(30):
        tree(c, r.uniform(-100, W + 100), 700 + r.uniform(-10, 20), r.uniform(1.0, 1.6), '#0e1730', seed=i)
    rect(c, 0, 700, W, 380, paint('#0b1120'))
    c.drawPath(poly([(W / 2 - 40, 700), (W / 2 + 40, 700), (W + 300, H), (-300, H)]), paint('#1a1d26'))
    for k in range(6):
        f = (k + (t * 0.6) % 1) / 6
        yy = lerp(705, H, f ** 1.8)
        hh = lerp(4, 60, f ** 1.8)
        ww = lerp(3, 16, f ** 1.8)
        rect(c, W / 2 - ww / 2, yy, ww, hh, paint(C('#c9b45a', 0.7)))
    for i in range(14):
        side = -1 if i % 2 == 0 else 1
        tree(c, W / 2 + side * (300 + (i // 2) * 160 + r.uniform(0, 60)), 760 + (i // 2) * 50, 1.6 + i * 0.15, '#070b16', seed=40 + i)
    fog(c, t, 760, 0.16, col='#9fb0e0', n=8, speed=8)
    if headlights:
        c.drawPath(poly([(W / 2 - 200, H), (W / 2 + 200, H), (W / 2 + 60, 720), (W / 2 - 60, 720)]), paint('#000', shader=lin(0, H, 0, 720, [C('#fff6c8', 0.35), C('#fff6c8', 0)])))


# ------------------------------------------------------------------ interior
def bedroom(c, t, mood='dawn', phone_glow=False):
    room(c, '#2e3152' if mood != 'dawn' else '#4a4f73', '#24263e' if mood != 'dawn' else '#33364f', 800)
    # window with city
    wx, wy, ww, wh = 1100, 130, 520, 460
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    c.translate(wx, wy)
    c.scale(ww / W, wh / H)
    if mood == 'dawn':
        city_bg(c, t, '#5d6a8e', '#c7b9bf', moon_xy=None, seed=8, lit=0.0, stars_n=0, fog_a=0.3)
    else:
        city_bg(c, t, '#070b22', '#1d2250', moon_xy=(1400, 220), seed=8, lit=0.02)
    c.restore()
    window_frame(c, wx, wy, ww, wh, curtain='#5b3150')
    # light beam from window
    if mood == 'dawn':
        c.drawPath(poly([(wx, wy + wh), (wx + ww, wy + wh), (wx + ww - 300, H), (wx - 600, H)]), paint('#000', shader=lin(0, wy, 0, H, [C('#dfe3ff', 0.12), C('#dfe3ff', 0.0)])))
    # bed
    rrect(c, 120, 640, 800, 260, 30, paint('#3b2a2a'))
    rrect(c, 140, 600, 760, 160, 40, paint('#6c7aa6'))
    rrect(c, 140, 620, 760, 140, 40, paint(C('#000000', 0.12)))
    rrect(c, 160, 560, 220, 90, 40, paint('#e7e7ef'))
    rrect(c, 100, 470, 40, 430, 12, paint('#2c1f1f'))
    # nightstand
    rect(c, 960, 700, 150, 180, paint('#4a3426'))
    rect(c, 960, 700, 150, 18, paint('#5c4231'))
    rrect(c, 1000, 680, 70, 22, 6, paint('#0c0d10'))
    if phone_glow:
        oval(c, 1035, 690, 60, 18, paint(C('#9fd3ff', 0.4), blur=15))
    # poster
    rect(c, 300, 180, 240, 320, paint('#7a2d3b'))
    text(c, 'ROCK', 420, 290, 64, '#ffd21e', align='center')
    circle(c, 420, 400, 70, paint('#1b1b1b'))
    circle(c, 420, 400, 20, paint('#7a2d3b'))


def kitchen(c, t, tv_mode='eas', tv_on=True, window_open=0.0, night=False):
    room(c, '#3e4a4a' if not night else '#26303a', '#2a2f33' if not night else '#1a1e24', 780)
    # tiles
    for x in range(0, 900, 60):
        for y in range(420, 620, 60):
            rect(c, x + 2, y + 2, 56, 56, paint(C('#ffffff', 0.04)))
    # counter
    rect(c, 0, 600, 880, 300, paint('#5a4636'))
    rect(c, 0, 580, 900, 30, paint('#c8c2b6'))
    for x in range(40, 860, 210):
        rect(c, x, 640, 180, 230, paint(C('#000000', 0.15)))
        rect(c, x + 150, 720, 12, 50, paint('#c8c2b6'))
    # fridge
    rrect(c, 920, 220, 260, 660, 16, paint('#d8dde3'))
    line(c, 920, 470, 1180, 470, '#a9b0ba', 4)
    rect(c, 1150, 300, 10, 120, paint('#a9b0ba'))
    # window
    wx, wy, ww, wh = 220, 110, 420, 330
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    c.translate(wx, wy)
    c.scale(ww / W, wh / H)
    if night:
        city_bg(c, t, '#070b22', '#1d2250', moon_xy=(1400, 220), seed=12, lit=0.02)
    else:
        city_bg(c, t, '#5d6a8e', '#bdb3bd', moon_xy=None, seed=12, lit=0.0, stars_n=0, fog_a=0.3)
    c.restore()
    window_frame(c, wx, wy, ww, wh, curtains=False, open_=window_open)
    # tv on stand
    rect(c, 1290, 640, 520, 240, paint('#2b2420'))
    tv(c, 1330, 300, 460, 280, on=tv_on, mode=tv_mode, t=t)


def apartment_living(c, t, tv_on=True, tv_mode='show', night=True, lamp=False):
    room(c, '#3a3350' if night else '#4d4866', '#2a2234', 790)
    # sofa
    rrect(c, 160, 600, 640, 230, 40, paint('#5a3d55'))
    rrect(c, 160, 540, 640, 120, 40, paint('#6b4a66'))
    rrect(c, 120, 600, 90, 230, 30, paint('#4d3449'))
    rrect(c, 750, 600, 90, 230, 30, paint('#4d3449'))
    # rug
    oval(c, 960, 960, 600, 90, paint('#4a2f3f'))
    # tv
    rect(c, 1150, 650, 560, 220, paint('#2b2420'))
    tv(c, 1190, 320, 480, 300, on=tv_on, mode=tv_mode, t=t)
    if lamp:
        rect(c, 920, 380, 10, 450, paint('#222'))
        c.drawPath(poly([(870, 380), (980, 380), (950, 300), (900, 300)]), paint('#e8c47a'))
        circle(c, 925, 400, 200, paint(C('#ffd98a', 0.18), blur=60))


def stairwell(c, t, flicker=0.0, dark=0.0):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#2a3a3a'))
    rect(c, 0, 0, W, 520, paint('#3b5050'))
    rect(c, 0, 520, W, 560, paint('#2c3d3d'))
    rect(c, 0, 510, W, 14, paint('#1d2a2a'))
    # stairs going down to the right
    for k in range(9):
        x = 700 + k * 120
        y = 640 + k * 50
        rect(c, x, y, 1400, 50, paint('#4a4f50' if k % 2 == 0 else '#43484a'))
        rect(c, x, y, 1400, 8, paint('#5a6062'))
    # landing
    rect(c, 0, 640, 720, 440, paint('#3e4344'))
    # railing
    for k in range(10):
        x = 720 + k * 120
        y = 520 + k * 50
        line(c, x, y + 120, x, y - 20, '#1a1d1e', 7)
    line(c, 700, 500, 1920, 1080 - 50, '#5b3a26', 18)
    # bulb
    on = 1.0
    if flicker:
        on = 0.25 + 0.75 * (1 if math.sin(t * 29) + math.sin(t * 13.1) > -0.4 else 0)
    line(c, 420, 0, 420, 120, '#111', 4)
    circle(c, 420, 135, 18, paint(C('#ffe7a8', on)))
    circle(c, 420, 135, 300, paint(C('#ffe7a8', 0.18 * on), blur=80))
    # numbers / graffiti
    text(c, '5', 200, 300, 120, C('#ffffff', 0.25))
    text(c, 'ТИХО', 1300, 330, 80, C('#c0392b', 0.55), FONT_XB)
    if dark:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#05060a', dark)))


def store(c, t, flicker=0.0):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#2b3138'))
    rect(c, 0, 760, W, 320, paint('#1e2328'))
    for x in range(-200, W + 200, 180):
        line(c, x, 760, W / 2 + (x - W / 2) * 2.0, H, C('#000000', 0.2), 3)
    # ceiling lamps
    for i, x in enumerate(range(160, W, 360)):
        on = 1.0
        if flicker and i == 2:
            on = 0.2 + 0.8 * (1 if math.sin(t * 33) + math.sin(t * 11.7) > 0 else 0)
        rect(c, x, 40, 220, 16, paint(C('#e8f6ff', 0.95 * on)))
        c.drawPath(poly([(x, 56), (x + 220, 56), (x + 330, 760), (x - 110, 760)]), paint('#000', shader=lin(0, 56, 0, 760, [C('#e8f6ff', 0.10 * on), C('#e8f6ff', 0)])))
    # shelves
    r = random.Random(5)
    for sx in (60, 1260):
        rect(c, sx, 260, 600, 520, paint('#3d4650'))
        for k in range(5):
            yy = 300 + k * 95
            rect(c, sx, yy + 70, 600, 12, paint('#59636e'))
            x = sx + 10
            while x < sx + 580:
                w = r.uniform(30, 70)
                h = r.uniform(30, 70)
                if r.random() < 0.75:
                    rect(c, x, yy + 70 - h, w - 6, h, paint(r.choice(['#c0392b', '#e67e22', '#f1c40f', '#27ae60', '#2980b9', '#ecf0f1', '#8e44ad'])))
                x += w
    text(c, 'ПРОДУКТЫ 24', W / 2, 160, 70, C('#ff4d4d', 0.25 + 0.15 * math.sin(t * 3)), align='center')


def hospital(c, t, flicker=0.6):
    corridor(c, t, col='#1c2624', flicker=flicker, wall='#2f4440', floor='#1a2321', ceil='#1c2725')
    # signs
    rect(c, 1450, 200, 300, 70, paint('#1f6f5b'))
    text(c, 'ПАЛАТЫ 10–14', 1600, 248, 34, '#ffffff', FONT_XB, align='center')
    rect(c, 150, 230, 260, 64, paint('#8a1f1f'))
    text(c, 'ВЫХОДА НЕТ', 280, 274, 30, '#ffffff', FONT_XB, align='center')
    # gurney
    rect(c, 300, 820, 420, 30, paint('#c9ced6'))
    rect(c, 300, 790, 420, 34, paint('#e6eaf0'))
    for x in (320, 690):
        line(c, x, 850, x, 960, '#9aa0a8', 8)
        circle(c, x, 968, 12, paint('#333'))


def subway(c, t, crowd=0, crowd_alpha=1.0, speaker_on=True):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#141922'))
    # tiled wall
    for y in range(0, 640, 46):
        for x in range(((y // 46) % 2) * 40, W, 80):
            rect(c, x + 2, y + 2, 76, 42, paint('#1f2733'))
    rect(c, 0, 280, W, 90, paint('#8a1f1f'))
    text(c, 'СЕВЕРНАЯ', W / 2, 345, 70, '#ffffff', align='center')
    # platform edge
    rect(c, 0, 640, W, 440, paint('#262a31'))
    rect(c, 0, 640, W, 22, paint('#9c8430'))
    # tunnel arches
    for x in (180, 1500):
        oval(c, x + 120, 520, 140, 180, paint('#05070a'))
        rect(c, x - 20, 520, 280, 130, paint('#05070a'))
    # lamps
    for x in range(100, W, 300):
        circle(c, x, 60, 14, paint('#fff0c0'))
        circle(c, x, 60, 140, paint(C('#fff0c0', 0.15), blur=40))
    # loudspeaker
    c.drawPath(poly([(930, 150), (990, 130), (990, 230), (930, 210)]), paint('#555b66'))
    rect(c, 900, 160, 32, 40, paint('#3a3f48'))
    if speaker_on:
        sound_waves(c, 1000, 180, t, 0.8, dirn=1)
    r = random.Random(3)
    pts = []
    for i in range(crowd):
        pts.append((r.uniform(80, W - 80), 700 + r.uniform(0, 330), r.uniform(0.32, 0.5), r.uniform(-0.6, 0.6)))
    pts.sort(key=lambda p: p[1])
    for x, y, s, tr in pts:
        listener(c, x, y, s * (0.8 + (y - 700) / 900), turn=tr + 0.2 * math.sin(t * 0.4 + x), t=t + x, glow=0.3, alpha=crowd_alpha, sway=0.5, dark=0.35)


def institute_ext(c, t):
    sky(c, '#05081a', '#1e2650')
    stars(c, 99, 160, t=t)
    moon(c, 300, 160, 80)
    tree(c, 100, 820, 1.5, '#0a1020', 1)
    tree(c, 1820, 820, 1.7, '#0a1020', 2)
    rect(c, 360, 260, 1200, 560, paint('#2a2e38'))
    rect(c, 360, 260, 1200, 560, paint('#000', shader=lin(0, 260, 0, 820, [C('#ffffff', 0.05), C('#000000', 0.4)])))
    for i in range(10):
        for j in range(4):
            rect(c, 410 + i * 115, 300 + j * 115, 70, 80, paint('#0d0f16'))
    rect(c, 860, 680, 200, 140, paint('#07080b'))
    rect(c, 560, 200, 800, 70, paint('#1b1e26'))
    text(c, 'НИИ АКУСТИЧЕСКИХ ИССЛЕДОВАНИЙ', 960, 248, 38, '#c9cfd8', FONT_XB, align='center')
    rect(c, 0, 820, W, 260, paint('#141824'))
    # fence
    for x in range(0, W, 40):
        line(c, x, 840, x, 1000, '#0b0d14', 5)
    line(c, 0, 860, W, 860, '#0b0d14', 6)
    line(c, 0, 980, W, 980, '#0b0d14', 6)
    fog(c, t, 860, 0.15, n=6)


def office(c, t, night=True, lamp_on=True):
    room(c, '#2c3038', '#1e2026', 800, pattern=False)
    # metal shelves
    for sx in (80, 1500):
        rect(c, sx, 230, 340, 570, paint('#434a55'))
        for k in range(5):
            rect(c, sx, 240 + k * 110, 340, 10, paint('#5b6370'))
            for b in range(5):
                rect(c, sx + 20 + b * 62, 240 + k * 110 - 70, 48, 70, paint(['#6b5b3a', '#3a4b6b', '#5a3a3a', '#4b5b4b', '#666'][(b + k) % 5]))
    # window w/ blinds
    rect(c, 700, 160, 520, 360, paint('#0a0e22'))
    for k in range(14):
        rect(c, 700, 160 + k * 26, 520, 12, paint(C('#5a6170', 0.9)))
    # desk
    rect(c, 600, 640, 720, 40, paint('#5a4636'))
    rect(c, 640, 680, 30, 200, paint('#4a3a2c'))
    rect(c, 1250, 680, 30, 200, paint('#4a3a2c'))
    if lamp_on:
        line(c, 1180, 640, 1150, 540, '#222', 8)
        c.drawPath(poly([(1110, 540), (1200, 540), (1180, 500), (1130, 500)]), paint('#2e7d5b'))
        circle(c, 1155, 600, 260, paint(C('#ffd98a', 0.18), blur=70))
    # door on the right wall
    door(c, 1680 - 300, 200, 220, 600, col='#3d434e', chain=False, peephole=False, knob='#aaa')


def lab(c, t, lamp=1.0):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14171c'))
    rect(c, 0, 0, W, 700, paint('#1b1f26'))
    # acoustic foam wall (pyramids)
    for y in range(40, 680, 80):
        for x in range(0, W, 80):
            c.drawPath(poly([(x, y), (x + 80, y), (x + 40, y + 40)]), paint('#232833'))
            c.drawPath(poly([(x, y + 80), (x + 80, y + 80), (x + 40, y + 40)]), paint('#1a1e27'))
    rect(c, 0, 700, W, 380, paint('#0f1115'))
    # table
    rect(c, 300, 720, 1320, 40, paint('#3a3328'))
    rect(c, 340, 760, 30, 300, paint('#2c261e'))
    rect(c, 1550, 760, 30, 300, paint('#2c261e'))
    # papers
    for i, (px, py, a) in enumerate(((520, 700, -8), (640, 704, 6), (1260, 702, -4))):
        c.save()
        c.translate(px, py)
        c.rotate(a)
        rect(c, -80, -14, 160, 18, paint('#cfc8b5'))
        c.restore()
    # lamp
    if lamp > 0:
        line(c, 1400, 720, 1360, 560, '#222', 8)
        c.drawPath(poly([(1290, 560), (1420, 560), (1390, 500), (1320, 500)]), paint('#555'))
        c.drawPath(poly([(1290, 560), (1420, 560), (1500, 730), (1200, 730)]), paint('#000', shader=lin(0, 560, 0, 730, [C('#ffe7a8', 0.30 * lamp), C('#ffe7a8', 0.05 * lamp)])))
        circle(c, 1355, 640, 360, paint(C('#ffe7a8', 0.10 * lamp), blur=90))
    text(c, 'ЛАБОРАТОРИЯ 0', 960, 120, 46, C('#c0392b', 0.5), FONT_XB, align='center')


def dossier(c, t, page=0, photo_draw=None):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#2b241d'))
    for y in range(0, H, 22):
        rect(c, 0, y, W, 2, paint(C('#000000', 0.12)))
    c.save()
    c.translate(W / 2, H / 2 + 20)
    c.rotate(-2)
    rect(c, -760, -460, 1520, 900, paint('#c9a46a'))
    rect(c, -730, -430, 1460, 840, paint('#efe9da'))
    text(c, 'ДЕЛО № N-0', -680, -340, 56, '#2b2b2b')
    text(c, 'СЛУШАЮЩИЕ', -680, -270, 42, '#2b2b2b', FONT_XB)
    c.save()
    c.rotate(-12)
    rrect(c, 140, -430, 460, 110, 10, paint(C('#c0392b', 0.85), 'stroke', 8))
    text(c, 'СЕКРЕТНО', 370, -350, 64, C('#c0392b', 0.85), align='center')
    c.restore()
    # photo frame
    rect(c, -680, -220, 560, 600, paint('#1a1d24'))
    if photo_draw:
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-670, -210, 540, 580))
        photo_draw(c)
        c.restore()
    c.restore()


def notebook(c, t, rules_written, new_k=1.0, title='ПРАВИЛА'):
    """Alex's notebook of rules. rules_written: list of strings; the last one is written with progress new_k."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1e1b19'))
    # desk lamp glow
    circle(c, 1500, 200, 700, paint(C('#ffd98a', 0.12), blur=120))
    c.save()
    c.translate(W / 2 + 40, H / 2 + 30)
    c.rotate(-3)
    rect(c, -560, -480, 1120, 980, paint(C('#000000', 0.5), blur=20))
    rect(c, -550, -490, 1100, 980, paint('#efe9d6'))
    for k in range(18):
        line(c, -550, -380 + k * 50, 550, -380 + k * 50, C('#7aa7d9', 0.45), 2)
    line(c, -440, -490, -440, 490, C('#d9534f', 0.6), 3)
    text(c, title, 0, -410, 64, '#1d2a55', align='center')
    n = len(rules_written)
    start = max(0, n - 16)
    for i, r_ in enumerate(rules_written[start:]):
        idx = start + i
        s = r_
        if idx == n - 1:
            s = r_[:int(len(r_) * clamp(new_k))]
        text(c, f'{idx + 1}.', -510, -340 + i * 50, 34, '#1d2a55', FONT_XB)
        text(c, s, -430, -340 + i * 50, 34, '#1d2a55', FONT_XB)
    # pen
    if new_k < 1 and n:
        i = n - 1 - start
        px = -430 + text_w(rules_written[-1][:int(len(rules_written[-1]) * clamp(new_k))], 34, FONT_XB)
        py = -350 + i * 50
        c.save()
        c.translate(px, py)
        c.rotate(35)
        rrect(c, -8, -260, 16, 260, 6, paint('#1f2a44'))
        c.drawPath(poly([(-8, 0), (8, 0), (0, 22)]), paint('#c9a227'))
        c.restore()
    c.restore()


def peephole(c, t, inner):
    """Fisheye view through a door peephole. inner(c) draws the hallway at W,H scale."""
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#030304'))
    c.save()
    path = skia.Path()
    path.addCircle(W / 2, H / 2, 470)
    c.clipPath(path, doAntiAlias=True)
    c.translate(W / 2, H / 2)
    c.scale(1.12, 1.12)
    c.translate(-W / 2, -H / 2)
    inner(c)
    c.restore()
    circle(c, W / 2, H / 2, 470, paint('#000', shader=rad(W / 2, H / 2, 480, [C('#000000', 0), C('#000000', 0.1), C('#000000', 0.95)], [0.0, 0.7, 1.0])))
    circle(c, W / 2, H / 2, 472, paint('#1a1a1a', 'stroke', 14))


def hallway_inner(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#3b4136'))
    rect(c, 0, 760, W, 320, paint('#2c2a25'))
    rect(c, 300, 200, 300, 560, paint('#4b3a2a'))
    rect(c, 1320, 200, 300, 560, paint('#4b3a2a'))
    circle(c, 960, 60, 16, paint('#ffe7a8'))
    circle(c, 960, 60, 400, paint(C('#ffe7a8', 0.18), blur=80))


def black(c):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#000000'))
