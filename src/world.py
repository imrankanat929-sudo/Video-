"""Backgrounds / environments + continuous 'worlds' (kitchen, street)."""
import math
import random
import cairo
from core import *
from person import draw_person, draw_head, BOY, MOM, DAD, expr, expr_blend, HEAD_Y
import phone as ph


def camera(ctx, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0, shk=(0.0, 0.0)):
    ctx.translate(W / 2 + shk[0], H / 2 + shk[1])
    ctx.rotate(rot)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


def auto_blink(t, seed=0.0, period=3.4):
    p = (t + seed * 1.37) % (period + seed * 0.3)
    if p < 0.16:
        return 1 - abs(p - 0.08) / 0.08
    return 0.0


def talk(t, on=True, seed=0):
    if not on:
        return 0.0
    return clamp(0.08 + 0.22 * abs(math.sin(t * 15 + seed)) * (0.5 + 0.5 * abs(math.sin(t * 4.3 + seed))))


def bokeh(ctx, t, seed, col, n=14, alpha=0.12, drift=8):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(-100, W + 100) + math.sin(t * 0.3 + i) * drift
        y = rnd.uniform(0, H)
        r = rnd.uniform(40, 140)
        c = mix(col, (1, 1, 1), rnd.uniform(0, 0.3))
        glow(ctx, x, y, r, c, alpha * rnd.uniform(0.4, 1.0), op=cairo.OPERATOR_SCREEN)


# ------------------------------------------------------------------ bedroom
def bedroom(ctx, t, phone_glow=0.0, sleeping=True):
    vgrad(ctx, -400, -200, W + 800, 1800, [(0, hexc('#1c2236'), 1), (1, hexc('#131726'), 1)])
    ctx.rectangle(-400, 1560, W + 800, 600); setc(ctx, hexc('#0e1019')); ctx.fill()
    ctx.rectangle(-400, 1545, W + 800, 22); setc(ctx, hexc('#1a1f2e')); ctx.fill()
    # window
    wx, wy, ww, wh = 560, 330, 400, 560
    rrect(ctx, wx - 18, wy - 18, ww + 36, wh + 36, 8); setc(ctx, hexc('#262c40')); ctx.fill()
    vgrad(ctx, wx, wy, ww, wh, [(0, hexc('#5b79ad'), 1), (0.7, hexc('#33476e'), 1), (1, hexc('#24304d'), 1)])
    # distant buildings in the window
    rnd = random.Random(3)
    x = wx
    while x < wx + ww:
        bw = rnd.uniform(50, 110); bh = rnd.uniform(120, 300)
        ctx.rectangle(x, wy + wh - bh, bw, bh); setc(ctx, hexc('#1a2238')); ctx.fill()
        x += bw + 6
    ctx.rectangle(wx + ww / 2 - 8, wy, 16, wh); setc(ctx, hexc('#262c40')); ctx.fill()
    ctx.rectangle(wx, wy + wh * 0.45 - 8, ww, 16); setc(ctx, hexc('#262c40')); ctx.fill()
    # curtains
    for cx0, sgn in ((wx - 60, 1), (wx + ww + 60, -1)):
        ctx.move_to(cx0 - 40 * sgn, wy - 60)
        ctx.line_to(cx0 + 70 * sgn, wy - 60)
        ctx.curve_to(cx0 + 40 * sgn, wy + 300, cx0 + 90 * sgn, wy + 600, cx0 + 60 * sgn, wy + wh + 120)
        ctx.line_to(cx0 - 40 * sgn, wy + wh + 120)
        ctx.close_path(); setc(ctx, hexc('#232a44')); ctx.fill()
    # light shaft
    ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.move_to(wx, wy); ctx.line_to(wx + ww, wy); ctx.line_to(wx + ww - 100, 1700); ctx.line_to(wx - 420, 1700)
    ctx.close_path()
    g = cairo.LinearGradient(0, wy, 0, 1700)
    g.add_color_stop_rgba(0, 0.35, 0.45, 0.7, 0.10); g.add_color_stop_rgba(1, 0.35, 0.45, 0.7, 0.0)
    ctx.set_source(g); ctx.fill(); ctx.restore()
    # poster + shelf
    rrect(ctx, 110, 430, 260, 360, 6); setc(ctx, hexc('#3b2230')); ctx.fill()
    ctx.arc(240, 560, 70, 0, 6.3); setc(ctx, hexc('#6b3346')); ctx.fill()
    text(ctx, "NO SIGNAL", 240, 730, 34, hexc('#a06070'), weight="black")
    ctx.rectangle(80, 930, 360, 16); setc(ctx, hexc('#2a3045')); ctx.fill()
    for i, c in enumerate(['#3a4a6a', '#5a3a3a', '#2f4f4f', '#4a4060', '#3a5a4a', '#5a5040']):
        ctx.rectangle(100 + i * 44, 930 - 90 - (i % 2) * 20, 36, 90 + (i % 2) * 20)
        setc(ctx, hexc(c)); ctx.fill()
    # nightstand (left) + phone
    ctx.rectangle(40, 1250, 190, 300); setc(ctx, hexc('#2b2a35')); ctx.fill()
    ctx.rectangle(40, 1240, 190, 20); setc(ctx, hexc('#363544')); ctx.fill()
    ctx.rectangle(60, 1330, 150, 4); setc(ctx, hexc('#1c1b24')); ctx.fill()
    # lamp
    ctx.move_to(90, 1240); ctx.line_to(110, 1120); ctx.line_to(150, 1120); ctx.line_to(170, 1240); ctx.close_path()
    setc(ctx, hexc('#3d3b4a')); ctx.fill()
    vib = math.sin(t * 90) * 3 * phone_glow
    rrect(ctx, 150 + vib, 1228, 70, 14, 4); setc(ctx, hexc('#0b0b0e')); ctx.fill()
    if phone_glow > 0:
        rrect(ctx, 154 + vib, 1226, 62, 6, 3); setc(ctx, hexc('#a8c8ff'), phone_glow); ctx.fill()
        glow(ctx, 185, 1225, 260, hexc('#6f95e6'), 0.35 * phone_glow)
        glow(ctx, 185, 1225, 600, hexc('#4a6ab0'), 0.12 * phone_glow)
    # bed
    ctx.rectangle(240, 1080, 40, 480); setc(ctx, hexc('#2c2f42')); ctx.fill()  # headboard
    rrect(ctx, 220, 1060, 80, 40, 12); setc(ctx, hexc('#353a52')); ctx.fill()
    ctx.rectangle(260, 1420, 800, 120); setc(ctx, hexc('#262a3c')); ctx.fill()  # frame
    rrect(ctx, 270, 1330, 790, 110, 30); setc(ctx, hexc('#59607a')); ctx.fill()  # mattress
    ellipse(ctx, 400, 1305, 120, 48); setc(ctx, hexc('#7c84a0')); ctx.fill()  # pillow
    for lx in (290, 1020):
        ctx.rectangle(lx, 1540, 24, 30); setc(ctx, hexc('#1c1f2c')); ctx.fill()
    if sleeping:
        ctx.save(); ctx.translate(395, 1268); ctx.rotate(-math.pi / 2 + 0.12); ctx.scale(0.55, 0.55)
        draw_head(ctx, BOY, dict(turn=0.95, blink=1.0, t=t), expr('calm'))
        ctx.restore()
    # blanket with breathing hump
    br = math.sin(t * 1.6) * 6
    ctx.move_to(450, 1440)
    ctx.curve_to(460, 1300 - br, 560, 1250 - br, 700, 1270 - br)
    ctx.curve_to(820, 1285 - br * 0.5, 900, 1300, 1060, 1300)
    ctx.line_to(1060, 1470); ctx.line_to(450, 1470); ctx.close_path()
    setc(ctx, hexc('#2c4258')); ctx.fill()
    ctx.set_line_width(5)
    for (a, b, c2, d) in [(560, 1300, 640, 1420), (760, 1300, 820, 1430), (900, 1320, 960, 1430)]:
        ctx.move_to(a, b - br); ctx.curve_to(a + 20, b + 40, c2 - 10, d - 40, c2, d)
        setc(ctx, hexc('#22354a')); ctx.stroke()


def phone_light_face(ctx, x, y, r, a=1.0, col=hexc('#7fa6ff')):
    glow(ctx, x, y, r, col, 0.22 * a)


# ------------------------------------------------------------------ hallway
def hallway(ctx, t, x0=-200, x1=2600):
    vgrad(ctx, x0, -300, x1 - x0, 1900, [(0, hexc('#2a2420'), 1), (1, hexc('#1e1a17'), 1)])
    ctx.rectangle(x0, 1140, x1 - x0, 420); setc(ctx, hexc('#241f1b')); ctx.fill()  # wainscot
    ctx.rectangle(x0, 1130, x1 - x0, 14); setc(ctx, hexc('#3a322b')); ctx.fill()
    ctx.rectangle(x0, 1560, x1 - x0, 600); setc(ctx, hexc('#171311')); ctx.fill()
    for i in range(int((x1 - x0) / 120)):
        ctx.rectangle(x0 + i * 120, 1560, 3, 600); setc(ctx, hexc('#120f0d')); ctx.fill()
    # doors
    for dx in (-60, 1500):
        ctx.rectangle(dx, 640, 300, 920); setc(ctx, hexc('#3a2f27')); ctx.fill()
        ctx.rectangle(dx + 20, 660, 260, 900); setc(ctx, hexc('#30271f')); ctx.fill()
        ctx.arc(dx + 250, 1120, 12, 0, 6.3); setc(ctx, hexc('#8a7a60')); ctx.fill()
    # kitchen doorway with warm light at the end
    ctx.rectangle(2150, 600, 360, 960); setc(ctx, hexc('#d9a86a')); ctx.fill()
    glow(ctx, 2330, 1100, 700, hexc('#d99a50'), 0.35)
    # family photo frames (foreshadowing)
    for i, fx in enumerate((420, 820, 1130)):
        fy = 760 + (i % 2) * 40
        ctx.rectangle(fx - 8, fy - 8, 236, 186); setc(ctx, hexc('#4a3b2c')); ctx.fill()
        ph.mini_family_photo(ctx, fx, fy, 220, 170, 10 + i)
        ctx.rectangle(fx, fy, 220, 170); setc(ctx, (0, 0, 0), 0.35); ctx.fill()
    # wall sconces
    for sx in (650, 1350, 1950):
        rrect(ctx, sx - 25, 560, 50, 70, 10); setc(ctx, hexc('#c9a26a')); ctx.fill()
        glow(ctx, sx, 595, 320, hexc('#c98a40'), 0.22)


# ------------------------------------------------------------------ kitchen world
def kitchen_bg(ctx, t):
    vgrad(ctx, -600, -300, W + 1200, 1900, [(0, hexc('#3a352e'), 1), (1, hexc('#2c2823'), 1)])
    # tiles band
    ctx.rectangle(-600, 1000, W + 1200, 260); setc(ctx, hexc('#3f3a33')); ctx.fill()
    for i in range(30):
        ctx.rectangle(-600 + i * 80, 1000, 2, 260); setc(ctx, hexc('#35302a')); ctx.fill()
    for j in range(4):
        ctx.rectangle(-600, 1000 + j * 65, W + 1200, 2); setc(ctx, hexc('#35302a')); ctx.fill()
    ctx.rectangle(-600, 1560, W + 1200, 600); setc(ctx, hexc('#221e1a')); ctx.fill()
    for i in range(14):
        ctx.move_to(-600 + i * 200, 1560); ctx.line_to(-900 + i * 260, 2100)
        setc(ctx, hexc('#1c1916')); ctx.set_line_width(3); ctx.stroke()
    # window with morning light
    wx, wy, ww, wh = 560, 420, 420, 480
    rrect(ctx, wx - 20, wy - 20, ww + 40, wh + 40, 8); setc(ctx, hexc('#4a4339')); ctx.fill()
    vgrad(ctx, wx, wy, ww, wh, [(0, hexc('#c9d4dc'), 1), (1, hexc('#8a9aa8'), 1)])
    for k in range(3):
        ctx.rectangle(wx + k * 140 + 20, wy + wh - 180 + k * 30, 100, 180); setc(ctx, hexc('#7a8896')); ctx.fill()
    ctx.rectangle(wx + ww / 2 - 7, wy, 14, wh); setc(ctx, hexc('#4a4339')); ctx.fill()
    ctx.rectangle(wx - 30, wy + wh, ww + 60, 22); setc(ctx, hexc('#554c40')); ctx.fill()
    # plant on sill
    rrect(ctx, wx + 40, wy + wh - 60, 60, 62, 8); setc(ctx, hexc('#7a5a40')); ctx.fill()
    for a in (-0.6, -0.2, 0.3, 0.7):
        ellipse(ctx, wx + 70 + math.sin(a) * 50, wy + wh - 90 - math.cos(a) * 30, 22, 40)
        setc(ctx, hexc('#4f6a45')); ctx.fill()
    # upper cabinets left
    ctx.rectangle(-600, 380, 900, 360); setc(ctx, hexc('#4c443a')); ctx.fill()
    for i in range(5):
        ctx.rectangle(-590 + i * 180, 395, 165, 330); setc(ctx, hexc('#544b40')); ctx.fill()
        ctx.rectangle(-590 + i * 180 + 140, 540, 8, 50); setc(ctx, hexc('#8a7f6e')); ctx.fill()
    # fridge
    rrect(ctx, -60, 640, 300, 920, 18); setc(ctx, hexc('#8d8f8e')); ctx.fill()
    ctx.rectangle(-60, 960, 300, 6); setc(ctx, hexc('#6a6c6b')); ctx.fill()
    ctx.rectangle(200, 720, 12, 160); setc(ctx, hexc('#5a5c5b')); ctx.fill()
    ctx.rectangle(200, 1010, 12, 200); setc(ctx, hexc('#5a5c5b')); ctx.fill()
    # magnets/notes
    for i, c in enumerate(('#d9c36a', '#c46a6a', '#6a9ac4')):
        ctx.rectangle(20 + i * 50, 760 + (i % 2) * 40, 40, 46); setc(ctx, hexc(c)); ctx.fill()
    # wall clock
    ctx.arc(1010, 300, 56, 0, 6.3); setc(ctx, hexc('#ddd3c2')); ctx.fill()
    ctx.set_line_width(5); setc(ctx, hexc('#2c2823'))
    ang = t * 0.05
    ctx.move_to(1010, 300); ctx.line_to(1010 + 32 * math.sin(ang), 300 - 32 * math.cos(ang)); ctx.stroke()
    ctx.move_to(1010, 300); ctx.line_to(1010 + 40 * math.sin(4.2), 300 - 40 * math.cos(4.2)); ctx.stroke()
    # pendant lamp
    ctx.move_to(760, -300); ctx.line_to(760, 520); setc(ctx, hexc('#1c1a17')); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(690, 600); ctx.line_to(830, 600); ctx.line_to(790, 520); ctx.line_to(730, 520); ctx.close_path()
    setc(ctx, hexc('#2f3a36')); ctx.fill()
    ellipse(ctx, 760, 602, 70, 10); setc(ctx, hexc('#ffe3a8')); ctx.fill()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.move_to(700, 600); ctx.line_to(820, 600); ctx.line_to(1100, 1320); ctx.line_to(420, 1320); ctx.close_path()
    g = cairo.LinearGradient(0, 600, 0, 1320)
    g.add_color_stop_rgba(0, 1, 0.85, 0.55, 0.13); g.add_color_stop_rgba(1, 1, 0.85, 0.55, 0.0)
    ctx.set_source(g); ctx.fill(); ctx.restore()


def kitchen_table(ctx, t, steam=True):
    # table top
    ctx.rectangle(440, 1300, 700, 30); setc(ctx, hexc('#6a4d36')); ctx.fill()
    ctx.rectangle(450, 1330, 680, 230); setc(ctx, hexc('#4e3826')); ctx.fill()
    ctx.rectangle(470, 1330, 30, 260); setc(ctx, hexc('#3a2a1c')); ctx.fill()
    # cloth runner
    ctx.rectangle(560, 1296, 420, 14); setc(ctx, hexc('#a89a85')); ctx.fill()
    # plates / mugs
    ellipse(ctx, 610, 1298, 70, 12); setc(ctx, hexc('#dcd6cc')); ctx.fill()
    ellipse(ctx, 610, 1296, 50, 7); setc(ctx, hexc('#c7a46a')); ctx.fill()
    rrect(ctx, 920, 1236, 52, 62, 8); setc(ctx, hexc('#c4553f')); ctx.fill()
    ctx.arc(975, 1265, 16, -1.4, 1.4); ctx.set_line_width(7); setc(ctx, hexc('#c4553f')); ctx.stroke()
    rrect(ctx, 760, 1250, 44, 50, 8); setc(ctx, hexc('#e0dccf')); ctx.fill()
    if steam:
        ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k, sx in enumerate((946, 782)):
            for j in range(2):
                ph_ = t * 1.5 + j * 0.5 + k
                yb = 1225 - (ph_ % 1) * 120
                a = 0.25 * math.sin((ph_ % 1) * math.pi)
                ctx.move_to(sx + j * 12, yb)
                ctx.curve_to(sx + 18 + j * 12, yb - 25, sx - 18 + j * 12, yb - 50, sx + j * 12, yb - 75)
                setc(ctx, (1, 1, 1), a); ctx.stroke()


BOY_K_SCALE = 0.85
BOY_K_GROUND = 1660


def boy_kitchen_state(t):
    # walk in
    x = kf(t, [(21.1, -140), (22.6, 250), (34.6, 250), (35.6, 330), (38.4, 330), (39.0, 250), (39.8, -300)],
           fn=lambda u: u)
    walking = 21.1 <= t < 22.6 or 35.0 <= t < 35.6
    running = t >= 38.95
    amp = 1.0 if (walking or running) else 0.0
    if 22.4 < t < 22.8:
        amp = 1 - prog(t, 22.4, 22.8)
    dirn = -1 if t >= 38.4 else 1
    pose = dict(facing='side', dir=dirn, phase=x / 70.0 if not running else t * 13, amp=amp, run=1.0 if running else 0,
                t=t, blink=auto_blink(t, 1))
    pose['turn'] = 0.92 * dirn
    # arms / expressions
    if 23.05 <= t < 24.9:
        up = ease_io(prog(t, 23.05, 23.4)) * (1 - ease_io(prog(t, 24.4, 24.9)))
        pose['arms'] = dict(near=(lerp(10, 155, up), lerp(10, 20 + 25 * math.sin(t * 14), up)), far=(-6, 10))
    elif 35.0 <= t < 38.4:
        u = t - 35.0
        g1 = 40 + 30 * math.sin(u * 3.2)
        g2 = 60 + 40 * math.sin(u * 4.1 + 1)
        if 36.2 < t < 37.0:   # points at himself
            pose['arms'] = dict(near=(40, 120), far=(10, 15))
        else:
            pose['arms'] = dict(near=(g1, g2), far=(15 + 15 * math.sin(u * 2.7), 30))
    e = 'calm'
    if 22.6 <= t < 24.6:
        e = 'smile'
    elif 24.6 <= t < 27.4:
        e = expr_blend('smile', 'calm', prog(t, 24.6, 27.0))
    elif 27.4 <= t < 33.6:
        e = expr_blend('calm', 'worried', prog(t, 27.4, 29.0))
    elif 33.6 <= t < 35.0:
        e = expr_blend('worried', 'shock', prog(t, 33.6, 33.9))
    elif 35.0 <= t < 37.8:
        e = 'worried'
    elif t >= 37.8:
        e = 'scared'
    pose['expr'] = e
    if 23.1 <= t < 24.4 or 35.0 <= t < 38.3:
        pose['talk'] = talk(t, True, 2)
    if 33.7 <= t < 35.0:
        pose['blink'] = 0
        pose['look'] = (0.6, 0)
    return x, pose


def parents_state(t):
    look_up = ease_io(prog(t, 24.3, 25.0))
    mom = dict(seated=True, t=t, blink=auto_blink(t, 3), turn=lerp(0.0, -0.55, look_up),
               look=lerp((0, 1.2), (-0.8, 0), look_up))
    dad = dict(seated=True, t=t, blink=auto_blink(t, 5.5), turn=lerp(0.0, -0.6, look_up),
               look=lerp((0.3, 1.2), (-0.9, 0), look_up))
    # arms on table
    mom['arms'] = dict(l=(18, -95), r=(18, -95 + 12 * math.sin(t * 2) * (1 - look_up)))
    mug = 1 - ease_io(prog(t, 24.6, 25.4))
    dad['arms'] = dict(l=(16, -92), r=(lerp(18, 45, mug), lerp(-95, -150, mug)))
    mom['expr'] = expr_blend('calm', 'puzzled', prog(t, 24.8, 25.6))
    dad['expr'] = expr_blend('calm', 'puzzled', prog(t, 25.0, 25.8))
    if t >= 29.2:
        dad['expr'] = expr_blend('puzzled', 'stern', prog(t, 29.2, 30.0))
    if 30.0 <= t < 33.7:
        dad['talk'] = talk(t, True, 1)
        dad['nod'] = math.sin(t * 3) * 3
    if t >= 34.6:
        # mom calls security, dad raises hand
        u = ease_io(prog(t, 35.6, 36.4))
        mom['arms'] = dict(l=(18, -95), r=(lerp(18, 125, u), lerp(-95, 128, u)))
        mom['phone'] = u > 0.7
        mom['phone_hand'] = 'r'
        mom['phone_lit'] = 0.6
        mom['expr'] = expr_blend('puzzled', 'scared', prog(t, 34.6, 35.4))
        mom['turn'] = lerp(-0.55, -0.2, u)
        if t >= 36.4:
            mom['talk'] = talk(t, True, 4)
        v = ease_io(prog(t, 35.0, 35.6))
        dad['arms'] = dict(l=(lerp(16, 75, v), lerp(-92, -75, v)), r=(18, -95))
        dad['expr'] = 'stern'
        if 35.6 <= t < 38.5:
            dad['talk'] = talk(t, True, 7)
    return mom, dad


def kitchen_world(ctx, t, boy_alpha=1.0):
    kitchen_bg(ctx, t)
    mom, dad = parents_state(t)
    draw_person(ctx, MOM, mom, 620, 1530, 0.8)
    draw_person(ctx, DAD, dad, 900, 1530, 0.8)
    kitchen_table(ctx, t)
    # chair backs in front? (skip) boy
    x, pose = boy_kitchen_state(t)
    if -260 < x < 1300:
        draw_person(ctx, BOY, pose, x, BOY_K_GROUND, BOY_K_SCALE, alpha=boy_alpha)


# ------------------------------------------------------------------ street world
PASSER_LOOKS = []
_r = random.Random(11)
_coats = ['#5b3a2c', '#3c4a5a', '#5a5a3c', '#4a3c5a', '#2f4a40', '#6a4a3a', '#3a3a40', '#704848']
_skins = ['#c9a07a', '#e0b896', '#8d6446', '#b88a66', '#d8ac88']
_hairs = [('short', '#2a2522'), ('bob', '#5a3a28'), ('cap', '#1d1d20'), ('bun', '#3a2a20'), ('short', '#8a8580'),
          ('bob', '#151515'), ('messy', '#4a3322')]
for i in range(16):
    hs, hc = _hairs[i % len(_hairs)]
    PASSER_LOOKS.append(dict(BOY, skin=hexc(_skins[_r.randrange(5)]), hair=hexc(hc), hair_style=hs,
                             top=hexc(_coats[i % len(_coats)]), top_style='coat', pants=hexc('#25262c'),
                             shoes=hexc('#2c2a28'), brow=hexc('#1c1c1c'), scale=_r.uniform(0.95, 1.12),
                             width=_r.uniform(0.95, 1.15), cap=hexc(_coats[(i + 3) % 8]), extras=()))
# (look idx, x at t=40, speed px/s (signed), depth)
PASSERS = []
_r = random.Random(5)
for i in range(16):
    depth = _r.choice([0.55, 0.6, 0.66, 0.72])
    sp = _r.choice([-1, 1]) * _r.uniform(110, 170) * depth / 0.66
    PASSERS.append((i, _r.uniform(-600, 3800), sp, depth))
FRONT_PASSERS = [(3, 1500, -230, 1.12), (9, -900, 210, 1.15), (12, 3200, -250, 1.1)]


def street_bg(ctx, cx, t, dark=0.0):
    """cx = camera x in world; draws parallax layers in screen-ish coords assuming camera applied."""
    sky0 = mix(hexc('#8e99a6'), hexc('#3a4250'), dark)
    sky1 = mix(hexc('#b9c0c6'), hexc('#4d5560'), dark)
    vgrad(ctx, cx - 1400, -600, 2800, 1700, [(0, sky0, 1), (1, sky1, 1)])
    # far buildings (parallax 0.35)
    for layer, (par, col, hmin, hmax, base, seed) in enumerate([
            (0.35, '#7d8692', 500, 900, 1200, 1), (0.65, '#5c6470', 400, 900, 1420, 2)]):
        off = cx * (1 - par)
        rnd = random.Random(seed)
        x = -2000
        c = mix(hexc(col), shade(hexc(col), 0.45), dark)
        while x < 6000:
            bw = rnd.uniform(180, 360); bh = rnd.uniform(hmin, hmax)
            bx = x + off
            if cx - 1500 < bx < cx + 1500:
                ctx.rectangle(bx, base - bh, bw, bh); setc(ctx, c); ctx.fill()
                # windows
                for wy in range(int(base - bh + 50), int(base - 60), 90):
                    for wx in range(int(bx + 30), int(bx + bw - 50), 70):
                        lit = rnd.random() < 0.18
                        ctx.rectangle(wx, wy, 34, 50)
                        setc(ctx, hexc('#e8d6a0') if lit and dark > 0.3 else shade(c, 0.8 if not lit else 1.25),
                             0.9); ctx.fill()
            else:
                for wy in range(int(base - bh + 50), int(base - 60), 90):
                    for wx in range(int(bx + 30), int(bx + bw - 50), 70):
                        rnd.random()
            x += bw + rnd.uniform(10, 50)
    # near facade (par 1.0): wall, doors, shop
    c_wall = mix(hexc('#6e665c'), hexc('#2e2b28'), dark)
    ctx.rectangle(cx - 1400, 700, 2800, 900); setc(ctx, c_wall); ctx.fill()
    rnd = random.Random(9)
    for i in range(-3, 14):
        bx = i * 420
        if not (cx - 1500 < bx < cx + 1500):
            continue
        ctx.rectangle(bx, 700, 6, 900); setc(ctx, shade(c_wall, 0.8)); ctx.fill()
        if i % 3 == 0:
            ctx.rectangle(bx + 110, 1100, 200, 450); setc(ctx, shade(c_wall, 0.55)); ctx.fill()
            ctx.rectangle(bx + 120, 1110, 180, 440); setc(ctx, mix(hexc('#3a2f28'), hexc('#1a1612'), dark)); ctx.fill()
        else:
            ctx.rectangle(bx + 60, 820, 300, 230); setc(ctx, mix(hexc('#9aa6b0'), hexc('#2a3038'), dark)); ctx.fill()
            ctx.rectangle(bx + 205, 820, 8, 230); setc(ctx, shade(c_wall, 0.7)); ctx.fill()
            ctx.rectangle(bx + 60, 1150, 300, 330); setc(ctx, mix(hexc('#8a96a0'), hexc('#262c34'), dark)); ctx.fill()
    # sidewalk
    ctx.rectangle(cx - 1400, 1560, 2800, 700); setc(ctx, mix(hexc('#5a5650'), hexc('#24221f'), dark)); ctx.fill()
    for i in range(-10, 40):
        x = i * 200
        if cx - 1500 < x < cx + 1500:
            ctx.move_to(x, 1560); ctx.line_to(x - 120, 2200)
            setc(ctx, mix(hexc('#4c4843'), hexc('#1c1a18'), dark)); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(cx - 1400, 1552, 2800, 14); setc(ctx, mix(hexc('#6a655e'), hexc('#2a2825'), dark)); ctx.fill()
    # lamp posts
    for i in range(-2, 12):
        lx = i * 700 + 300
        if cx - 1500 < lx < cx + 1500:
            ctx.rectangle(lx, 560, 16, 1000); setc(ctx, hexc('#2a2a2c')); ctx.fill()
            rrect(ctx, lx - 40, 540, 96, 30, 10); setc(ctx, hexc('#2a2a2c')); ctx.fill()
            if dark > 0.3:
                glow(ctx, lx + 8, 575, 300, hexc('#e8c070'), 0.3 * dark)


def passers_at(t, front=False):
    lst = FRONT_PASSERS if front else PASSERS
    out = []
    for (li, x40, sp, depth) in lst:
        x = x40 + sp * (t - 40)
        out.append((li, x, sp, depth))
    return out


def draw_passers(ctx, t, cx, front=False, ground_back=1600, ground_front=1820, desat=0.0):
    ps = passers_at(t, front)
    ps.sort(key=lambda p: p[3])
    for li, x, sp, depth in ps:
        if not (cx - 1000 < x < cx + 1000):
            continue
        look = PASSER_LOOKS[li]
        if not front:
            fog = hexc('#7d8692')
            look = dict(look, top=mix(look['top'], fog, 0.45), pants=mix(look['pants'], fog, 0.45),
                        skin=mix(look['skin'], fog, 0.35), hair=mix(look['hair'], fog, 0.4), shoes=mix(look['shoes'], fog, 0.4))
        if desat > 0:
            look = dict(look, top=mix(look['top'], hexc('#4a4a4a'), desat), skin=mix(look['skin'], hexc('#8a8a8a'), desat * 0.5))
        d = 1 if sp > 0 else -1
        y = ground_front if front else lerp(ground_back - 40, ground_back + 40, (depth - 0.55) / 0.17)
        pose = dict(facing='side', dir=d, phase=x / (70 * depth), amp=1.0, t=t, blink=auto_blink(t, li),
                    expr='calm', look=(0.3 * d, 0))
        draw_person(ctx, look, pose, x, y, depth if not front else depth)


def street_world(ctx, t, cx, boy=None, boy_alpha=1.0, dark=0.0, desat=0.0, front=True, ghost_pass=None):
    street_bg(ctx, cx, t, dark)
    draw_passers(ctx, t, cx, desat=desat)
    if boy:
        bx, by, bs, pose = boy
        draw_person(ctx, BOY, pose, bx, by, bs, alpha=boy_alpha)
    if front:
        draw_passers(ctx, t, cx, front=True, desat=desat)
    if ghost_pass is not None:
        li, x, d = ghost_pass
        pose = dict(facing='side', dir=d, phase=x / 75, amp=1.0, t=t, expr='calm')
        draw_person(ctx, PASSER_LOOKS[li], pose, x, 1760, 1.05)


# ------------------------------------------------------------------ album
def album(ctx, t, flip_t, vanish, focus=None):
    """vanish: list of 4 values 0..1 (boy disappearance per photo)"""
    # desk
    vgrad(ctx, -300, -300, W + 600, H + 600, [(0, hexc('#2a1f18'), 1), (1, hexc('#1a130e'), 1)])
    for i in range(12):
        ctx.move_to(-300, i * 200 - 100); ctx.curve_to(300, i * 200 - 60, 700, i * 200 - 140, 1400, i * 200 - 90)
        setc(ctx, hexc('#24190f'), 0.8); ctx.set_line_width(6); ctx.stroke()
    glow(ctx, 540, 700, 1100, hexc('#d0a060'), 0.18)
    cx, cy = 540, 900
    pw, phh = 470, 1180
    # album cover
    rrect(ctx, cx - pw - 30, cy - phh / 2 - 26, pw * 2 + 60, phh + 52, 18); setc(ctx, hexc('#4a2a22')); ctx.fill()
    # pages
    for side in (-1, 1):
        x = cx - pw if side < 0 else cx
        g = cairo.LinearGradient(x, 0, x + pw, 0)
        if side < 0:
            g.add_color_stop_rgb(0, *hexc('#e8e0d0')); g.add_color_stop_rgb(0.9, *hexc('#ddd4c2')); g.add_color_stop_rgb(1, *hexc('#b8ae9c'))
        else:
            g.add_color_stop_rgb(0, *hexc('#b8ae9c')); g.add_color_stop_rgb(0.1, *hexc('#ddd4c2')); g.add_color_stop_rgb(1, *hexc('#e8e0d0'))
        ctx.rectangle(x, cy - phh / 2, pw, phh); ctx.set_source(g); ctx.fill()
    flip = prog(t, flip_t, flip_t + 0.7)
    photos = [(cx - pw + 45, cy - 520, 380, 300, 21), (cx - pw + 60, cy - 60 + 40, 360, 300, 22),
              (cx + 45, cy - 500, 380, 300, 23), (cx + 50, cy + 20, 370, 330, 24)]
    for i, (x, y, w, h, seed) in enumerate(photos):
        if flip < 1 and i >= 2:
            seed += 10
        if flip < 1 and i < 2:
            seed += 10
        _album_photo(ctx, x, y, w, h, seed, (vanish[i] if flip >= 1 else 0.0), t, i)
    # turning page
    if 0 < flip < 1:
        k = math.cos(flip * math.pi)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(k, 1)
        ctx.rectangle(0, -phh / 2, pw, phh)
        setc(ctx, mix(hexc('#ddd4c2'), hexc('#a89e8c'), 1 - abs(k))); ctx.fill()
        ctx.restore()
    # hands holding the album
    sk = BOY['skin']
    for side in (-1, 1):
        hx = cx + side * (pw + 10)
        ctx.save(); ctx.translate(hx, cy + 520)
        ctx.scale(side, 1)
        ctx.move_to(-60, 60); ctx.curve_to(-70, -40, -20, -110, 30, -90)
        ctx.curve_to(70, -70, 90, 80, 60, 300); ctx.line_to(-60, 300); ctx.close_path()
        setc(ctx, sk); ctx.fill()
        rrect(ctx, -110, -70, 120, 46, 23); setc(ctx, shade(sk, 0.94)); ctx.fill()  # thumb on page
        ctx.rectangle(-20, 260, 160, 400); setc(ctx, BOY['top']); ctx.fill()
        ctx.restore()


def _album_photo(ctx, x, y, w, h, seed, vanish, t, i):
    ctx.save()
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate((seed % 5 - 2) * 0.02)
    ctx.translate(-w / 2, -h / 2)
    ctx.rectangle(-14, -14, w + 28, h + 50); setc(ctx, hexc('#f4f1ea')); ctx.fill()
    ph.mini_family_photo(ctx, 0, 0, w, h, seed, boy_alpha=1 - ease_io(vanish), ghost=ease_io(prog(vanish, 0.6, 1.0)))
    if 0 < vanish < 1:
        rnd = random.Random(seed * 3 + int(t * 20))
        for q in range(40):
            px = w * 0.5 + rnd.gauss(0, w * 0.08)
            py = h * 0.5 + rnd.gauss(0, h * 0.2) - vanish * 60 * rnd.random()
            ctx.rectangle(px, py, 4, 4); setc(ctx, (1, 1, 1), (1 - vanish) * rnd.random())
            ctx.fill()
    ctx.restore()
