"""Brown bear rig. Units: cm. Origin at ground under body centre. Facing right in side view."""
import math
import random
import skia
from gfx import paint, path_poly, path_smooth, ellipse, lin_grad, rad_grad, rgb, mix, lerp, clamp, record

FUR = rgb('#5e3b22')
FUR_D = rgb('#3a2414')
FUR_DD = rgb('#24160c')
FUR_L = rgb('#8b5a33')
FUR_LL = rgb('#a8784a')
MUZ = rgb('#9a7350')
NOSE = rgb('#16100c')
CLAW = rgb('#d8cfbf')


def fur_strokes(c, path, rng, n, length, cols, flow=(1, 0.25), width=2.2, alpha=0.55, bounds=None):
    """Short strokes clipped into path, giving a furry texture."""
    c.save()
    c.clipPath(path, doAntiAlias=True)
    b = bounds or path.getBounds()
    fx, fy = flow
    for i in range(n):
        x = rng.uniform(b.left(), b.right())
        y = rng.uniform(b.top(), b.bottom())
        L = length * rng.uniform(0.6, 1.3)
        a = math.atan2(fy, fx) + rng.uniform(-0.35, 0.35)
        cc = cols[rng.randrange(len(cols))]
        p = skia.Path()
        p.moveTo(x, y)
        p.quadTo(x + math.cos(a) * L * 0.5 + rng.uniform(-2, 2), y + math.sin(a) * L * 0.5 + rng.uniform(-2, 2),
                 x + math.cos(a) * L, y + math.sin(a) * L)
        c.drawPath(p, paint(cc, alpha * rng.uniform(0.6, 1.0), stroke=width * rng.uniform(0.7, 1.2)))
    c.restore()


def fuzzy_edge(c, path, rng, color, step=7, length=9, width=3, alpha=1.0, outward=1):
    """Tufts along an outline so silhouette isn't vector-clean."""
    meas = skia.PathMeasure(path, True)
    L = meas.getLength()
    d = 0
    while d < L:
        pos, tan = meas.getPosTan(d)
        nx, ny = tan.y() * outward, -tan.x() * outward
        l = length * rng.uniform(0.5, 1.2)
        sk = rng.uniform(-0.6, 0.6)
        p = skia.Path()
        p.moveTo(pos.x() - nx * 2, pos.y() - ny * 2)
        p.quadTo(pos.x() + nx * l * 0.6 + tan.x() * sk * l, pos.y() + ny * l * 0.6 + tan.y() * sk * l,
                 pos.x() + nx * l + tan.x() * sk * l * 1.5, pos.y() + ny * l + tan.y() * sk * l * 1.5)
        c.drawPath(p, paint(color, alpha, stroke=width))
        d += step * rng.uniform(0.6, 1.3)


# ----------------------------------------------------------------------------------------------
# SIDE VIEW (pictures for static parts, legs procedural)
# ----------------------------------------------------------------------------------------------
BODY_PTS = [(-126, -96), (-118, -124), (-92, -136), (-40, -132), (10, -140), (44, -156), (76, -148), (98, -126),
            (104, -104), (96, -80), (76, -64), (30, -60), (-30, -58), (-84, -62), (-116, -74)]


def _body_side_pic():
    def f(c):
        rng = random.Random(11)
        p = path_smooth(BODY_PTS, tension=0.5)
        neck = path_smooth([(60, -150), (104, -132), (122, -108), (112, -84), (86, -76), (70, -110)], tension=0.5)
        p.addPath(neck)
        c.drawPath(p, paint(shader=lin_grad((0, -156), (0, -56), [FUR_L, FUR, FUR_D, FUR_DD], [0, 0.35, 0.75, 1])))
        # shoulder hump highlight
        c.drawOval(ellipse(40, -140, 50, 16), paint(FUR_LL, 0.35, blur=10))
        fur_strokes(c, p, rng, 900, 10, [FUR_D, FUR_DD, FUR_L, FUR], flow=(-1, 0.35), width=2.4, alpha=0.5)
        fur_strokes(c, p, rng, 220, 12, [FUR_LL], flow=(-1, 0.2), width=1.8, alpha=0.35,
                    bounds=skia.Rect.MakeLTRB(-110, -160, 100, -120))
        fuzzy_edge(c, p, rng, FUR_D, step=3.3, length=5.5, width=2.1)
        fuzzy_edge(c, p, rng, FUR, step=5.0, length=3.9, width=1.7)
    return record((-160, -200, 160, 0), f)


def _head_side_pic():
    """Head facing right, pivot at neck (0,0)."""
    def f(c):
        rng = random.Random(5)
        skull = path_smooth([(-30, -20), (-14, -44), (16, -50), (40, -40), (62, -22), (92, -12), (104, -2), (102, 12),
                             (84, 20), (56, 24), (28, 30), (-10, 30), (-34, 14)], tension=0.5)
        c.drawPath(skull, paint(shader=lin_grad((0, -50), (0, 30), [FUR_L, FUR, FUR_D])))
        # muzzle lighter
        muz = path_smooth([(48, -24), (92, -12), (104, -2), (102, 12), (82, 20), (52, 18), (40, -4)], tension=0.5)
        c.drawPath(muz, paint(MUZ, 0.75))
        fur_strokes(c, skull, rng, 380, 8, [FUR_D, FUR_DD, FUR_L], flow=(-1, 0.15), width=2, alpha=0.45)
        fuzzy_edge(c, skull, rng, FUR_D, step=3.3, length=3.9, width=1.8)
        # ear
        ear = path_smooth([(-10, -38), (-4, -62), (14, -60), (18, -42)], tension=0.5)
        c.drawPath(ear, paint(FUR_D))
        c.drawOval(ellipse(4, -50, 7, 9), paint(FUR_DD))
        fuzzy_edge(c, ear, rng, FUR_D, step=3.0, length=3.3, width=1.5)
        # nose
        c.drawPath(path_smooth([(96, -10), (108, -6), (110, 4), (100, 6), (94, 0)], tension=0.5), paint(NOSE))
        c.drawCircle(104, -5, 2, paint('#ffffff', 0.35))
        # mouth line
        c.drawPath(path_smooth([(100, 12), (80, 16), (62, 14)], close=False), paint(FUR_DD, stroke=2.4))
        # brow ridge
        c.drawPath(path_smooth([(26, -36), (40, -38), (52, -30)], close=False), paint(FUR_DD, 0.7, stroke=4))
    return record((-60, -90, 130, 60), f)


_PICS = {}


def pics():
    if not _PICS:
        _PICS['body'] = _body_side_pic()
        _PICS['head'] = _head_side_pic()
        _PICS['front_head'] = _front_head_pic()
        _PICS['front_body'] = _front_body_pic()
        _PICS['rear'] = _rear_pic()
        _PICS['closeup'] = _closeup_head_pic()
    return _PICS


def _leg(c, top, angle, length, w_top, w_bot, color, lift=0.0, bend=0.0, front=True, claws=True):
    """Thick bear leg from 'top' point, angle from vertical (rad, + = forward)."""
    x0, y0 = top
    kx = x0 + math.sin(angle) * length * 0.5
    ky = y0 + math.cos(angle) * length * 0.5
    a2 = angle + bend
    fx = kx + math.sin(a2) * length * 0.5
    fy = ky + math.cos(a2) * length * 0.5 - lift
    pts = [(x0 - w_top / 2, y0 - 10), (x0 + w_top / 2, y0 - 10), (kx + w_bot * 0.62, ky), (fx + w_bot / 2, fy - 4),
           (fx - w_bot / 2, fy - 4), (kx - w_bot * 0.62, ky)]
    p = path_smooth(pts, tension=0.35)
    c.drawPath(p, paint(shader=lin_grad((x0, y0), (x0, fy), [mix(color, FUR, 0.55), color, mix(color, FUR_DD, 0.5)], [0, 0.5, 1])))
    rng = random.Random(int(abs(x0) * 7) + int(w_top))
    for i in range(14):
        u = rng.random()
        yy = lerp(y0, fy - 6, u)
        xx = lerp(x0, fx, u) + (w_top / 2 if rng.random() < 0.5 else -w_top / 2) * lerp(1, 0.6, u)
        c.drawLine(xx, yy, xx + rng.uniform(-3, 3), yy + rng.uniform(5, 10), paint(mix(color, FUR, 0.4), 0.8, stroke=2))
    # paw
    c.drawPath(path_smooth([(fx - w_bot * 0.62, fy - 8), (fx + w_bot * 0.75, fy - 9), (fx + w_bot * 0.95, fy), (fx - w_bot * 0.6, fy + 1)], tension=0.4),
               paint(mix(color, FUR_DD, 0.4)))
    if claws:
        for k in range(4):
            cx = fx + w_bot * 0.35 + k * 3.2
            c.drawPath(path_smooth([(cx, fy - 2), (cx + 6, fy - 1), (cx + 8, fy + 2)], close=False), paint(CLAW, 0.9, stroke=1.6))
    return (fx, fy)


def draw_side(c, phase=0.0, gait='walk', t=0.0, head_lift=0.0, sniff=0.0, speed=1.0, breath=0.0):
    """gait: 'walk' | 'run' | 'stand'"""
    P = pics()
    ph = phase * 2 * math.pi
    if gait == 'run':
        body_y = -abs(math.sin(ph)) * 16 - 8
        tilt = math.sin(ph) * 5
        stretch = 1 + math.sin(ph) * 0.05
    elif gait == 'walk':
        body_y = -abs(math.sin(ph)) * 4 * speed
        tilt = math.sin(ph) * 1.2 * speed
        stretch = 1.0
    else:
        body_y = math.sin(t * 1.6) * 1.5 * (1 + breath)
        tilt = 0
        stretch = 1 + math.sin(t * 1.6) * 0.01 * (1 + breath)

    def legs(far):
        col_ = FUR_DD if far else FUR_D
        legdefs = [(-78, 0.0, 'hind'), (52, math.pi, 'front')] if not far else [(-92, math.pi, 'hind'), (38, 0.0, 'front')]
        for x, off, kind in legdefs:
            if gait == 'stand':
                ang, lift, bend = 0.0, 0.0, 0.0
            elif gait == 'run':
                p = ph + (0 if kind == 'front' else math.pi * 0.85) + (0.35 if far else 0)
                ang = math.sin(p) * 0.62
                lift = max(0, math.cos(p)) * 18
                bend = -0.5 * max(0, math.cos(p)) if kind == 'front' else 0.4 * max(0, math.cos(p))
            else:
                p = ph + off
                ang = math.sin(p) * 0.33 * speed
                lift = max(0, math.cos(p)) * 9 * speed
                bend = (-0.35 if kind == 'front' else 0.3) * max(0, math.cos(p)) * speed
            top = (x * stretch, -100 + body_y + (4 if kind == 'hind' else 0))
            _leg(c, top, ang, 100 if kind == 'front' else 96, 52 if kind == 'hind' else 44, 28, col_, lift=lift, bend=bend)

    legs(True)
    c.save()
    c.translate(0, body_y)
    c.rotate(tilt * 0.3)
    c.scale(stretch, 1)
    c.drawPicture(P['body'])
    c.restore()
    legs(False)
    # head
    c.save()
    hx, hy = 90 * stretch, -114 + body_y
    c.translate(hx, hy)
    bob = (math.sin(ph * 2) * 3 if gait == 'walk' else math.sin(ph) * 6 if gait == 'run' else 0)
    c.rotate(-head_lift * 22 + bob + (math.sin(t * 9) * 1.5 * sniff))
    c.translate(0, 8)
    c.scale(0.95, 0.95)
    c.drawPicture(P['head'])
    # eye (animated blink-less)
    c.drawOval(ellipse(46, -26, 4.2, 3.6), paint('#0b0705'))
    c.drawCircle(47.5, -27.2, 1.3, paint('#ffffff', 0.8))
    if sniff:
        s = (math.sin(t * 22) * 0.5 + 0.5) * sniff
        c.drawOval(ellipse(104, 2, 3 + s * 2, 2 + s * 1.2), paint('#000000'))
    c.restore()


# ----------------------------------------------------------------------------------------------
# FRONT VIEW (coming toward camera)
# ----------------------------------------------------------------------------------------------
def _front_body_pic():
    def f(c):
        rng = random.Random(21)
        # shoulders / hump mass behind head
        p = path_smooth([(-120, -60), (-104, -150), (-50, -196), (0, -206), (50, -196), (104, -150), (120, -60), (60, -40), (-60, -40)], tension=0.5)
        c.drawPath(p, paint(shader=lin_grad((0, -206), (0, -40), [FUR_L, FUR, FUR_D])))
        fur_strokes(c, p, rng, 800, 11, [FUR_D, FUR_DD, FUR_L, FUR], flow=(0, 1), width=2.4, alpha=0.5)
        fuzzy_edge(c, p, rng, FUR_D, step=3.3, length=6.1, width=2.1)
        # chest darker
        ch = path_smooth([(-60, -120), (0, -136), (60, -120), (50, -50), (-50, -50)], tension=0.5)
        c.drawPath(ch, paint(FUR_D, 0.65, blur=6))
    return record((-170, -260, 170, 0), f)


def _front_head_pic():
    """Bear head facing camera. centre (0,0), approx radius 70."""
    def f(c):
        rng = random.Random(31)
        # ears
        for s in (-1, 1):
            ear = path_smooth([(s * 44, -44), (s * 62, -78), (s * 84, -70), (s * 78, -38)], tension=0.5)
            c.drawPath(ear, paint(FUR_D))
            c.drawOval(ellipse(s * 66, -60, 8, 10), paint(FUR_DD))
            fuzzy_edge(c, ear, rng, FUR_D, step=3.0, length=3.3, width=1.4)
        head = path_smooth([(-78, -10), (-70, -50), (-36, -72), (0, -76), (36, -72), (70, -50), (78, -10), (60, 30), (30, 52), (0, 58), (-30, 52), (-60, 30)], tension=0.5)
        c.drawPath(head, paint(shader=rad_grad((0, -40), 120, [FUR_L, FUR, FUR_D])))
        fur_strokes(c, head, rng, 500, 8, [FUR_D, FUR_DD, FUR_L], flow=(0, -1), width=2, alpha=0.45)
        fuzzy_edge(c, head, rng, FUR_D, step=3.0, length=4.4, width=1.8)
        # muzzle
        muz = path_smooth([(-30, 0), (-18, -14), (18, -14), (30, 0), (26, 34), (0, 46), (-26, 34)], tension=0.5)
        c.drawPath(muz, paint(shader=rad_grad((0, 10), 50, [MUZ, mix(MUZ, FUR, 0.5)])))
        fur_strokes(c, muz, rng, 140, 5, [FUR, FUR_L], flow=(0, 1), width=1.4, alpha=0.4)
        # brow ridges
        for s in (-1, 1):
            c.drawPath(path_smooth([(s * 14, -26), (s * 28, -32), (s * 42, -28)], close=False), paint(FUR_DD, 0.7, stroke=4))
        # nose
        c.drawPath(path_smooth([(-14, 4), (14, 4), (12, 16), (0, 21), (-12, 16)], tension=0.5), paint(NOSE))
        c.drawOval(ellipse(-4, 7, 4, 2), paint('#ffffff', 0.3))
        c.drawLine(0, 21, 0, 30, paint(FUR_DD, stroke=2))
        c.drawPath(path_smooth([(-14, 34), (0, 30), (14, 34)], close=False), paint(FUR_DD, stroke=2.2))
    return record((-110, -110, 110, 80), f)


def draw_front(c, phase=0.0, t=0.0, moving=True, sway=1.0, sniff=0.0, head_lift=0.0, gait='walk'):
    P = pics()
    ph = phase * 2 * math.pi
    run = gait == 'run'
    amp = (1.0 if moving else 0.0)
    bob = (abs(math.sin(ph)) * (14 if run else 5)) * amp
    # legs: alternating, the lifted leg is shorter and closer to camera (bigger)
    for s, off in ((-1, 0), (1, math.pi)):
        lift = max(0, math.sin(ph + off)) * amp
        x = s * 58
        top = -70 - bob
        bot = -2 - lift * (26 if run else 12)
        w = 44 + lift * 10
        leg = path_smooth([(x - w / 2, top), (x + w / 2, top), (x + w * 0.42, bot), (x - w * 0.42, bot)], tension=0.2)
        c.drawPath(leg, paint(FUR_D))
        c.drawOval(ellipse(x, bot, w * 0.5, 9 + lift * 3), paint(FUR_DD))
        for k in range(4):
            cx = x - 12 + k * 8
            c.drawLine(cx, bot + 4, cx, bot + 11, paint(CLAW, 0.85, stroke=2.2))
    c.save()
    c.translate(math.sin(ph) * 3 * sway * amp, -bob)
    c.drawPicture(P['front_body'])
    c.restore()
    c.save()
    hs = math.sin(ph) * 6 * sway * amp + math.sin(t * 0.7) * 3
    c.translate(hs, -150 - bob + head_lift * -18)
    c.rotate(math.sin(ph) * 3 * sway * amp)
    c.drawPicture(P['front_head'])
    # eyes
    for s in (-1, 1):
        c.drawOval(ellipse(s * 26, -18, 5.5, 5), paint('#0a0604'))
        c.drawCircle(s * 26 - 1.5, -19.5, 1.6, paint('#ffffff', 0.85))
    if sniff:
        k = (math.sin(t * 22) * 0.5 + 0.5) * sniff
        for s in (-1, 1):
            c.drawOval(ellipse(s * 6, 13, 3 + k * 1.5, 2 + k), paint('#000000'))
    c.restore()


# ----------------------------------------------------------------------------------------------
# REAR VIEW (walking away)
# ----------------------------------------------------------------------------------------------
def _rear_pic():
    def f(c):
        rng = random.Random(41)
        p = path_smooth([(-100, -60), (-96, -130), (-60, -170), (0, -182), (60, -170), (96, -130), (100, -60), (60, -46), (-60, -46)], tension=0.5)
        c.drawPath(p, paint(shader=lin_grad((0, -182), (0, -46), [FUR_L, FUR, FUR_D])))
        fur_strokes(c, p, rng, 700, 11, [FUR_D, FUR_DD, FUR_L, FUR], flow=(0, 1), width=2.4, alpha=0.5)
        fuzzy_edge(c, p, rng, FUR_D, step=3.3, length=6.1, width=2.1)
        c.drawOval(ellipse(0, -150, 9, 8), paint(FUR_D))  # tail
        # hump & ear tips beyond
        for s in (-1, 1):
            c.drawOval(ellipse(s * 30, -196, 10, 12), paint(FUR_D))
    return record((-150, -240, 150, 0), f)


def draw_rear(c, phase=0.0, t=0.0):
    P = pics()
    ph = phase * 2 * math.pi
    bob = abs(math.sin(ph)) * 4
    for s, off in ((-1, 0), (1, math.pi)):
        lift = max(0, math.sin(ph + off))
        x = s * 50
        top = -70 - bob
        bot = -2 - lift * 12
        w = 50 - lift * 8
        c.drawPath(path_smooth([(x - w / 2, top), (x + w / 2, top), (x + w * 0.4, bot), (x - w * 0.4, bot)], tension=0.2), paint(FUR_D))
        c.drawOval(ellipse(x, bot - 2, w * 0.42, 8 - lift * 4), paint(FUR_DD))
    c.save()
    c.translate(0, -bob)
    c.rotate(math.sin(ph) * 2)
    c.drawPicture(P['rear'])
    c.restore()


# ----------------------------------------------------------------------------------------------
# CLOSE-UP HEAD (3/4, facing left), centre (0,0) roughly eye level. Size ~ 600 units wide
# ----------------------------------------------------------------------------------------------
def _closeup_head_pic():
    def f(c):
        rng = random.Random(77)
        neck = path_smooth([(60, 40), (180, -60), (330, 40), (360, 400), (40, 420)], tension=0.5)
        c.drawPath(neck, paint(shader=lin_grad((150, -60), (200, 420), [FUR, FUR_D, FUR_DD])))
        fur_strokes(c, neck, rng, 1400, 22, [FUR_D, FUR_DD, FUR, FUR_L], flow=(0.3, 1), width=3.4, alpha=0.5)
        fuzzy_edge(c, neck, rng, FUR_D, step=5.0, length=9.9, width=2.8)
        head = path_smooth([(-200, 10), (-150, -70), (-60, -140), (40, -160), (140, -130), (200, -60), (210, 40), (160, 120),
                            (60, 150), (-60, 130), (-150, 90)], tension=0.5)
        c.drawPath(head, paint(shader=rad_grad((40, -80), 300, [FUR_LL, FUR_L, FUR, FUR_D], [0, 0.25, 0.6, 1])))
        fur_strokes(c, head, rng, 2200, 16, [FUR_D, FUR_DD, FUR, FUR_L], flow=(1, 0.1), width=2.8, alpha=0.5)
        fur_strokes(c, head, rng, 500, 14, [FUR_LL], flow=(1, -0.1), width=2.2, alpha=0.35,
                    bounds=skia.Rect.MakeLTRB(-60, -160, 200, -40))
        fuzzy_edge(c, head, rng, FUR_D, step=3.9, length=7.7, width=2.4)
        # ears
        for ex, ey, sc in ((150, -150, 1.0), (-20, -170, 0.85)):
            ear = path_smooth([(ex - 40 * sc, ey + 20), (ex - 30 * sc, ey - 40 * sc), (ex + 10 * sc, ey - 56 * sc), (ex + 40 * sc, ey - 20 * sc), (ex + 36 * sc, ey + 24)], tension=0.5)
            c.drawPath(ear, paint(FUR_D))
            c.drawOval(ellipse(ex, ey - 14 * sc, 16 * sc, 22 * sc), paint(FUR_DD))
            fur_strokes(c, ear, rng, 120, 10, [FUR, FUR_DD], flow=(0, -1), width=2, alpha=0.5)
            fuzzy_edge(c, ear, rng, FUR_D, step=3.3, length=5.5, width=1.8)
        # muzzle (pointing left)
        muz = path_smooth([(-60, -20), (-170, -10), (-250, 20), (-268, 56), (-240, 90), (-170, 104), (-80, 100), (-30, 60)], tension=0.5)
        c.drawPath(muz, paint(shader=lin_grad((-260, 0), (-30, 60), [MUZ, mix(MUZ, FUR_L, 0.4), FUR])))
        fur_strokes(c, muz, rng, 700, 9, [FUR, FUR_L, FUR_D], flow=(1, 0.05), width=2, alpha=0.4)
        fuzzy_edge(c, muz, rng, mix(MUZ, FUR, 0.5), step=6, length=7, width=2.2)
        # mouth line
        c.drawPath(path_smooth([(-240, 92), (-180, 100), (-110, 96), (-70, 84)], close=False), paint(FUR_DD, stroke=5))
        # brow
        c.drawPath(path_smooth([(-90, -66), (-40, -86), (10, -80)], close=False), paint(FUR_DD, 0.6, stroke=10))
    return record((-320, -260, 400, 440), f)


def draw_closeup(c, t=0.0, sniff=0.0, blink=0.0, look=0.0, nose_twitch=0.0):
    P = pics()
    c.drawPicture(P['closeup'])
    # eye
    ex, ey = -42, -46
    c.drawOval(ellipse(ex, ey, 24, 20), paint(FUR_DD))
    c.drawOval(ellipse(ex - 2 + look * 4, ey, 15, 14 * (1 - blink)), paint('#2a1408'))
    if blink < 0.8:
        c.drawOval(ellipse(ex - 2 + look * 4, ey, 9, 9 * (1 - blink)), paint('#050302'))
        c.drawCircle(ex - 7 + look * 4, ey - 5, 4, paint('#ffffff', 0.9))
        c.drawCircle(ex + 4, ey + 5, 1.8, paint('#ffffff', 0.5))
    # nose
    k = (math.sin(t * 20) * 0.5 + 0.5) * sniff
    nx, ny = -262 + nose_twitch * 3, 40 - k * 3
    nose = path_smooth([(nx - 26, ny - 18), (nx + 4, ny - 26), (nx + 26, ny - 12), (nx + 18, ny + 14), (nx - 6, ny + 22), (nx - 28, ny + 6)], tension=0.5)
    c.drawPath(nose, paint(shader=rad_grad((nx - 6, ny - 10), 34, ['#3a2c26', NOSE])))
    c.drawOval(ellipse(nx - 6, ny - 14, 9, 4), paint('#ffffff', 0.35))
    for s in (-1, 1):
        c.drawOval(ellipse(nx + s * 10 - 4, ny + 8, 6 + k * 3, 4 + k * 2), paint('#000000'))


def draw_eye_closeup(c, t=0.0, blink=0.0, look=0.0, dilate=0.0):
    """Extreme close-up on eye. centre (0,0); eye radius ~ 150."""
    rng = random.Random(91)
    bg = skia.Path()
    bg.addRect(skia.Rect.MakeLTRB(-700, -1100, 700, 1100))
    c.drawPath(bg, paint(shader=rad_grad((0, -100), 900, [FUR_L, FUR, FUR_D])))
    fur_strokes(c, bg, rng, 2600, 60, [FUR_D, FUR_DD, FUR, FUR_L, FUR_LL], flow=(1, 0.25), width=6, alpha=0.5)
    # eye socket
    c.drawOval(ellipse(0, 0, 230, 175), paint(FUR_DD, blur=18))
    c.drawOval(ellipse(0, 0, 180, 140 * (1 - blink * 0.95)), paint('#140a05'))
    if blink < 0.9:
        c.save()
        c.clipRRect(skia.RRect.MakeOval(ellipse(0, 0, 180, 140 * (1 - blink))), doAntiAlias=True)
        ix = look * 30
        c.drawCircle(ix, 0, 120, paint(shader=rad_grad((ix, 0), 120, ['#120804', '#4a2a10', '#8a5420', '#3a1e0a'], [0, 0.45, 0.8, 1])))
        for i in range(60):
            a = i / 60 * math.pi * 2
            c.drawLine(ix + math.cos(a) * 55, math.sin(a) * 55, ix + math.cos(a) * 115, math.sin(a) * 115, paint('#b07030', 0.18, stroke=3))
        c.drawCircle(ix, 0, 52 + dilate * 18, paint('#030201'))
        c.drawOval(ellipse(ix - 50, -50, 34, 22), paint('#ffffff', 0.85))
        c.drawCircle(ix + 50, 40, 10, paint('#ffffff', 0.35))
        c.restore()
    # lids fur
    c.drawPath(path_smooth([(-190, -10), (-100, -150 * (1 - blink * 0.9)), (100, -150 * (1 - blink * 0.9)), (190, -10)], close=False), paint(FUR_DD, stroke=26))
    c.drawPath(path_smooth([(-190, 10), (-100, 130 * (1 - blink * 0.9)), (100, 130 * (1 - blink * 0.9)), (190, 10)], close=False), paint(FUR_DD, stroke=18))
