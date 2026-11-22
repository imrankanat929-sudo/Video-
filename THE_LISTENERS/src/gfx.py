"""Low-level drawing helpers + characters + environments for THE LISTENERS.
Flat cinematic-cartoon style (night, moon, fog, bold titles)."""
import math, random
import numpy as np
import skia

W, H = 1920, 1080
FONT_BLACK = skia.Typeface.MakeFromFile('/usr/share/fonts/opentype/montserrat/Montserrat-Black.otf')
FONT_XB = skia.Typeface.MakeFromFile('/usr/share/fonts/opentype/montserrat/Montserrat-ExtraBold.otf')
FONT_MONO = skia.Typeface.MakeFromFile('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf')
FONT_REG = skia.Typeface.MakeFromFile('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')


def C(h, a=1.0):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, max(0, min(255, int(a * 255))))


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def seg(t, a, b):
    """0..1 progress of t inside [a,b]"""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def paint(color, style='fill', width=1, blur=0, aa=True, blend=None, shader=None, cap=None, join=None):
    p = skia.Paint(AntiAlias=aa)
    if isinstance(color, str):
        color = C(color)
    p.setColor(color)
    if style == 'stroke':
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(cap or skia.Paint.kRound_Cap)
        p.setStrokeJoin(join or skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend == 'add':
        p.setBlendMode(skia.BlendMode.kPlus)
    elif blend == 'screen':
        p.setBlendMode(skia.BlendMode.kScreen)
    elif blend == 'multiply':
        p.setBlendMode(skia.BlendMode.kMultiply)
    if shader is not None:
        p.setShader(shader)
    return p


def lin(x0, y0, x1, y1, cols, pos=None):
    cols = [C(c) if isinstance(c, str) else c for c in cols]
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], cols, pos)


def rad(x, y, r, cols, pos=None):
    cols = [C(c) if isinstance(c, str) else c for c in cols]
    return skia.GradientShader.MakeRadial(skia.Point(x, y), r, cols, pos)


def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def rrect(c, x, y, w, h, r, pt):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), pt)


def rect(c, x, y, w, h, pt):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), pt)


def oval(c, cx, cy, rx, ry, pt):
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), pt)


def circle(c, x, y, r, pt):
    c.drawCircle(x, y, r, pt)


def line(c, x0, y0, x1, y1, col, w, blur=0):
    c.drawLine(x0, y0, x1, y1, paint(col, 'stroke', w, blur))


def font(size, face=None):
    f = skia.Font(face or FONT_BLACK, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text_w(s, size, face=None):
    return font(size, face).measureText(s)


def text(c, s, x, y, size, col='#ffffff', face=None, align='left', stroke=0, stroke_col='#000000', shadow=0, alpha=1.0):
    f = font(size, face)
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    blob = skia.TextBlob.MakeFromString(s, f)
    if shadow:
        c.drawTextBlob(blob, x + shadow * 0.6, y + shadow, paint(C('#000000', 0.55 * alpha), blur=shadow * 0.5))
    if stroke:
        c.drawTextBlob(blob, x, y, paint(C(stroke_col, alpha), 'stroke', stroke))
    c.drawTextBlob(blob, x, y, paint(C(col, alpha) if isinstance(col, str) else col))
    return w


def label(c, s, x, y, size, bg='#ffffff', fg='#111111', angle=-3, alpha=1.0, pad=None, face=None, align='left'):
    """Pill label like YouTube horror thumbnails (white / red banners)."""
    pad = pad or size * 0.45
    w = text_w(s, size, face or FONT_XB)
    if align == 'center':
        x -= (w + pad * 2) / 2
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    rrect(c, 4, 6, w + pad * 2, size * 1.45, size * 0.25, paint(C('#000000', 0.45 * alpha), blur=6))
    rrect(c, 0, 0, w + pad * 2, size * 1.45, size * 0.25, paint(C(bg, alpha)))
    text(c, s, pad, size * 1.08, size, C(fg, alpha), face or FONT_XB)
    c.restore()
    return w + pad * 2


# ---------------------------------------------------------------- characters

SKIN = '#f0c4a0'
SKIN_SH = '#d9a47f'
SWEATER = '#363d4c'
SWEATER_D = '#272d39'
JEANS = '#232a38'


def limb(c, pts, col, w):
    p = skia.Path()
    p.moveTo(*pts[0])
    if len(pts) == 3:
        p.quadTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1])
    else:
        for q in pts[1:]:
            p.lineTo(*q)
    c.drawPath(p, paint(col, 'stroke', w))


def ik(sx, sy, tx, ty, l1, l2, bend=1):
    dx, dy = tx - sx, ty - sy
    d = max(1e-3, min(l1 + l2 - 1, math.hypot(dx, dy)))
    a = math.atan2(dy, dx)
    cosb = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1, min(1, cosb)))
    ea = a + b * bend
    ex, ey = sx + math.cos(ea) * l1, sy + math.sin(ea) * l1
    ux, uy = (tx - sx) / max(1e-3, math.hypot(dx, dy)), (ty - sy) / max(1e-3, math.hypot(dx, dy))
    hx, hy = sx + ux * d, sy + uy * d
    return (sx, sy), (ex, ey), (hx, hy)


IK_TARGETS = {
    'shh': (None, (14, -520)),
    'cover': ((-40, -530), (40, -530)),
    'phone': ((-30, -330), (30, -330)),
    'phone1': (None, (60, -470)),
    'ear': (None, (120, -600)),
    'knock': (None, (230, -520)),
    'handle': (None, (200, -380)),
    'flash': (None, (230, -420)),
    'recorder': (None, (40, -420)),
    'hold': ((-40, -330), (40, -330)),
    'chest': ((-20, -420), (20, -420)),
}


def tint_begin(c, tint):
    if not tint:
        return False
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(tint if isinstance(tint, int) else C(tint), skia.BlendMode.kModulate))
    c.saveLayer(None, p)
    return True


def arm_pts(sx, sy, a1, l1, a2, l2):
    """shoulder, angles in degrees (0 = down, positive = toward +x)"""
    ex = sx + math.sin(math.radians(a1)) * l1
    ey = sy + math.cos(math.radians(a1)) * l1
    hx = ex + math.sin(math.radians(a2)) * l2
    hy = ey + math.cos(math.radians(a2)) * l2
    return (sx, sy), (ex, ey), (hx, hy)


ARM_POSES = {
    # (left a1,a2, right a1,a2) angles; left arm is on -x side
    'down': (-8, -4, 8, 4),
    'tense': (-18, 20, 18, -20),
    'up': (-140, -170, 140, 170),
    'shh': (-8, -4, 25, 165),
    'phone': (-20, 140, 20, -140),
    'phone1': (-8, -4, 30, -150),
    'reach': (-8, -4, 80, 90),
    'flash': (-8, -4, 70, 95),
    'cover': (-25, 160, 25, -160),
    'hold': (-25, 120, 25, -120),
    'point': (-8, -4, 95, 100),
    'hug': (-30, 100, 30, -100),
}


def alex(c, x, y, s=1.0, look=0.0, mouth=0.3, eyes='wide', arms='down', sweat=0, t=0.0,
         hair='#14161c', sweater=SWEATER, skin=SKIN, flip=False, item=None, breathe=1.0, light=None,
         walk=0.0, brows='worried', blink=True, tint=None):
    """Alex, 16, black messy hair, dark sweater. Feet at (x,y). Height ~ 620*s"""
    tl = tint_begin(c, tint)
    _alex(c, x, y, s, look, mouth, eyes, arms, sweat, t, hair, sweater, skin, flip, item, breathe, light, walk, brows, blink)
    if tl:
        c.restore()


def _alex(c, x, y, s, look, mouth, eyes, arms, sweat, t, hair, sweater, skin, flip, item, breathe, light, walk, brows, blink):
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    bob = math.sin(t * 2.2) * 3 * breathe
    # walking legs
    lw = math.sin(walk * math.pi * 2) * 18 if walk else 0
    # shadow
    oval(c, 0, 0, 120, 16, paint(C('#000000', 0.35), blur=8))
    # legs
    for i, dx in enumerate((-34, 34)):
        off = lw if i == 0 else -lw
        rrect(c, dx - 27 + off * 0.3, -240, 54, 236, 20, paint(JEANS))
        oval(c, dx + off * 0.3 + 8, -6, 40, 15, paint('#111318'))
    # torso
    c.translate(0, bob)
    body = skia.Path()
    body.moveTo(-112, -440)
    body.cubicTo(-130, -360, -112, -260, -100, -205)
    body.lineTo(100, -205)
    body.cubicTo(112, -260, 130, -360, 112, -440)
    body.cubicTo(60, -478, -60, -478, -112, -440)
    body.close()
    c.drawPath(body, paint(sweater))
    c.drawPath(body, paint(C('#000000', 0.18), shader=lin(0, -470, 0, -205, [C('#ffffff', 0.06), C('#000000', 0.25)])))
    # ribbing
    rrect(c, -102, -232, 204, 30, 10, paint(SWEATER_D))
    for k in range(-90, 100, 14):
        line(c, k, -228, k, -206, C('#000000', 0.25), 3)
    # collar
    oval(c, 0, -452, 46, 18, paint(SWEATER_D))
    def draw_arms():
        # arms
        la1, la2, ra1, ra2 = ARM_POSES.get(arms, ARM_POSES['down'])
        tw = math.sin(t * 9) * 3 if arms in ('tense', 'up') else 0
        hands = []
        ikt = IK_TARGETS.get(arms)
        for side, a1, a2 in ((-1, la1, la2), (1, ra1, ra2)):
            tgt = ikt[0 if side < 0 else 1] if ikt else None
            if tgt:
                sh, el, hd = ik(side * 104, -420, tgt[0], tgt[1] + bob * 0, 125, 120, bend=(-1 if side > 0 else 1))
            else:
                sh, el, hd = arm_pts(side * 104, -420, a1 + tw, 125, a2 + tw, 120)
            limb(c, [sh, el, hd], sweater, 58)
            limb(c, [sh, el, hd], C('#000000', 0.12), 58)
            # cuff
            hands.append(hd)
        # item in right hand
        if item == 'phone' or arms in ('phone', 'phone1'):
            hx, hy = hands[1] if arms != 'phone' else ((hands[0][0] + hands[1][0]) / 2, (hands[0][1] + hands[1][1]) / 2)
            rrect(c, hx - 34, hy - 70, 68, 120, 12, paint('#0d0f14'))
            rrect(c, hx - 28, hy - 63, 56, 104, 8, paint(C('#9fd3ff', 0.9) if light != 'off' else '#22262f'))
        if item == 'flashlight':
            hx, hy = hands[1]
            rrect(c, hx - 12, hy - 50, 24, 70, 6, paint('#2a2a2a'))
        if item == 'recorder':
            hx, hy = hands[1]
            rrect(c, hx - 26, hy - 60, 52, 100, 10, paint('#1d1f24'))
            rrect(c, hx - 18, hy - 50, 36, 26, 4, paint('#3fe07a'))
            circle(c, hx, hy + 10, 9, paint('#c0392b'))
        for hx, hy in hands:
            circle(c, hx, hy, 30, paint(skin))
            circle(c, hx, hy, 30, paint(C('#000000', 0.08)))

        return hands

    FRONT = ('shh', 'cover', 'ear', 'phone1', 'recorder')
    hands = draw_arms() if arms not in FRONT else None
    # neck
    rect(c, -26, -500, 52, 50, paint(SKIN_SH))
    # head
    hy = -640
    c.save()
    c.translate(look * 10, 0)
    circle(c, -122, hy + 10, 30, paint(skin))
    circle(c, 122, hy + 10, 30, paint(skin))
    circle(c, -122, hy + 10, 14, paint(SKIN_SH))
    circle(c, 122, hy + 10, 14, paint(SKIN_SH))
    rrect(c, -125, hy - 150, 250, 300, 118, paint(skin))
    # shading
    rrect(c, -125, hy - 150, 250, 300, 118, paint(C('#000000', 1), shader=lin(-125, 0, 125, 0, [C('#000000', 0.0), C('#000000', 0.0), C('#000000', 0.16)], [0, 0.6, 1])))
    # hair: messy black
    hp = skia.Path()
    hp.moveTo(-132, hy - 10)
    hp.cubicTo(-150, hy - 120, -100, hy - 185, -20, hy - 178)
    hp.lineTo(-30, hy - 205)
    hp.lineTo(10, hy - 180)
    hp.lineTo(30, hy - 212)
    hp.lineTo(55, hy - 175)
    hp.lineTo(95, hy - 190)
    hp.lineTo(90, hy - 160)
    hp.cubicTo(150, hy - 130, 150, hy - 60, 132, hy - 10)
    hp.lineTo(118, hy - 60)
    hp.lineTo(95, hy - 95)
    hp.lineTo(70, hy - 70)
    hp.lineTo(50, hy - 105)
    hp.lineTo(20, hy - 70)
    hp.lineTo(-5, hy - 108)
    hp.lineTo(-35, hy - 72)
    hp.lineTo(-60, hy - 105)
    hp.lineTo(-90, hy - 70)
    hp.lineTo(-110, hy - 95)
    hp.close()
    c.drawPath(hp, paint(hair))
    c.drawPath(hp, paint(C('#ffffff', 0.06), 'stroke', 3))
    # face
    ex = look * 14
    blinkv = 1.0
    if blink:
        ph = (t * 0.37 + x * 0.001) % 1.0
        if ph < 0.03:
            blinkv = 0.1
    if eyes == 'closed':
        blinkv = 0.08
    ew, eh = (30, 36) if eyes == 'wide' else (26, 26)
    for side in (-1, 1):
        exx = side * 50 + ex
        oval(c, exx, hy + 5, ew, eh * blinkv, paint('#ffffff'))
        if blinkv > 0.3:
            pr = 13 if eyes == 'wide' else 14
            circle(c, exx + look * 9, hy + 8, pr, paint('#15161a'))
            circle(c, exx + look * 9 - 4, hy + 3, 4, paint('#ffffff'))
        # brows
        if brows == 'worried':
            line(c, exx - 24, hy - 38 + side * 0, exx + 22, hy - 50 + (0 if side > 0 else 0), '#1a1a1a', 7) if side < 0 else line(c, exx - 22, hy - 50, exx + 24, hy - 38, '#1a1a1a', 7)
        elif brows == 'angry':
            line(c, exx - 24, hy - 50, exx + 22, hy - 38, '#1a1a1a', 7) if side < 0 else line(c, exx - 22, hy - 38, exx + 24, hy - 50, '#1a1a1a', 7)
        else:
            line(c, exx - 22, hy - 44, exx + 22, hy - 46, '#1a1a1a', 7)
    # nose
    oval(c, ex * 0.6, hy + 50, 10, 7, paint(SKIN_SH))
    # mouth
    if arms in ('cover',):
        pass
    elif mouth > 0.15:
        oval(c, ex * 0.6, hy + 92, 14 + mouth * 6, 8 + mouth * 16, paint('#4a1f1f'))
    else:
        line(c, ex * 0.6 - 16, hy + 92, ex * 0.6 + 16, hy + 90, '#6b3a2c', 5)
    if sweat:
        for i in range(int(sweat)):
            sx = -112 + i * 220
            sy = hy - 40 + ((t * 30 + i * 37) % 60)
            dp = skia.Path()
            dp.moveTo(sx, sy - 18)
            dp.quadTo(sx + 12, sy, sx, sy + 10)
            dp.quadTo(sx - 12, sy, sx, sy - 18)
            c.drawPath(dp, paint('#9fdcff'))
    c.restore()
    if hands is None:
        hands = draw_arms()
    if arms == 'shh':
        hx, hy2 = hands[1]
        rrect(c, hx - 9, hy2 - 75, 18, 70, 9, paint(skin))
        circle(c, hx, hy2, 30, paint(skin))
    if arms == 'cover':
        oval(c, look * 10, hy + 100, 70, 38, paint(skin))
        oval(c, look * 10, hy + 100, 70, 38, paint(C('#000000', 0.08)))
    if light is not None and light not in ('off',):
        # rim light colour overlay e.g. phone glow from below
        c.drawCircle(0, -560, 360, paint(C(light, 0.18), blend='screen', shader=rad(0, -500, 380, [C(light, 0.35), C(light, 0)])))
    c.restore()


def person(c, x, y, s=1.0, tint=None, **kw):
    tl = tint_begin(c, tint)
    _person(c, x, y, s, **kw)
    if tl:
        c.restore()


def _person(c, x, y, s=1.0, coat='#7a2d2d', hair='#5a3b22', skin='#e9b997', look=0.0, mouth=0.2, t=0.0,
           arms='down', female=False, cap=None, beard=False, flip=False, walk=0.0, hairstyle='short', eyes='normal'):
    """Generic survivor in the same flat style."""
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    bob = math.sin(t * 2.0 + x) * 3
    lw = math.sin(walk * math.pi * 2) * 18 if walk else 0
    oval(c, 0, 0, 120, 16, paint(C('#000000', 0.35), blur=8))
    for i, dx in enumerate((-34, 34)):
        off = lw if i == 0 else -lw
        rrect(c, dx - 27 + off * 0.3, -240, 54, 236, 20, paint('#2a2d33'))
        oval(c, dx + off * 0.3 + 8, -6, 40, 15, paint('#111318'))
    c.translate(0, bob)
    body = skia.Path()
    body.moveTo(-118, -440)
    body.cubicTo(-136, -360, -120, -250, -108, -190)
    body.lineTo(108, -190)
    body.cubicTo(120, -250, 136, -360, 118, -440)
    body.cubicTo(60, -478, -60, -478, -118, -440)
    c.drawPath(body, paint(coat))
    c.drawPath(body, paint('#000000', shader=lin(0, -470, 0, -190, [C('#ffffff', 0.07), C('#000000', 0.28)])))
    line(c, 0, -450, 0, -195, C('#000000', 0.3), 4)
    la1, la2, ra1, ra2 = ARM_POSES.get(arms, ARM_POSES['down'])
    hands = []
    ikt = IK_TARGETS.get(arms)
    for side, a1, a2 in ((-1, la1, la2), (1, ra1, ra2)):
        tgt = ikt[0 if side < 0 else 1] if ikt else None
        if tgt:
            sh, el, hd = ik(side * 108, -420, tgt[0], tgt[1], 125, 120, bend=(-1 if side > 0 else 1))
        else:
            sh, el, hd = arm_pts(side * 108, -420, a1, 125, a2, 120)
        limb(c, [sh, el, hd], coat, 58)
        limb(c, [sh, el, hd], C('#000000', 0.12), 58)
        hands.append(hd)
    for hx, hy2 in hands:
        circle(c, hx, hy2, 30, paint(skin))
    rect(c, -26, -500, 52, 50, paint(skin))
    rect(c, -26, -500, 52, 50, paint(C('#000000', 0.15)))
    hy = -640
    if female and hairstyle == 'long':
        lp = skia.Path()
        lp.moveTo(-135, hy - 60)
        lp.cubicTo(-150, hy + 100, -140, hy + 170, -100, hy + 190)
        lp.lineTo(100, hy + 190)
        lp.cubicTo(140, hy + 170, 150, hy + 100, 135, hy - 60)
        lp.close()
        c.drawPath(lp, paint(hair))
    circle(c, -122, hy + 10, 28, paint(skin))
    circle(c, 122, hy + 10, 28, paint(skin))
    rrect(c, -125, hy - 150, 250, 300, 118, paint(skin))
    rrect(c, -125, hy - 150, 250, 300, 118, paint('#000000', shader=lin(-125, 0, 125, 0, [C('#000000', 0.0), C('#000000', 0.0), C('#000000', 0.16)], [0, 0.6, 1])))
    if beard:
        bp = skia.Path()
        bp.moveTo(-122, hy + 20)
        bp.cubicTo(-110, hy + 190, 110, hy + 190, 122, hy + 20)
        bp.cubicTo(60, hy + 70, -60, hy + 70, -122, hy + 20)
        c.drawPath(bp, paint(hair))
    # hair
    hp = skia.Path()
    hp.moveTo(-128, hy - 20)
    hp.cubicTo(-140, hy - 170, 140, hy - 170, 128, hy - 20)
    hp.cubicTo(80, hy - 95, -60, hy - 110, -128, hy - 20)
    c.drawPath(hp, paint(hair))
    if female:
        bp2 = skia.Path()
        bp2.moveTo(-128, hy - 30)
        bp2.cubicTo(-100, hy - 160, 100, hy - 160, 128, hy - 30)
        bp2.lineTo(60, hy - 70)
        bp2.lineTo(20, hy - 50)
        bp2.lineTo(-40, hy - 80)
        bp2.close()
        c.drawPath(bp2, paint(hair))
    if female and hairstyle == 'ponytail':
        oval(c, 140, hy - 40, 40, 90, paint(hair))
    if cap:
        cp = skia.Path()
        cp.moveTo(-132, hy - 50)
        cp.cubicTo(-130, hy - 200, 130, hy - 200, 132, hy - 50)
        cp.close()
        c.drawPath(cp, paint(cap))
        rrect(c, -40, hy - 64, 210, 26, 12, paint(cap))
    ex = look * 14
    for side in (-1, 1):
        exx = side * 50 + ex
        ew, eh = (30, 36) if eyes == 'wide' else (25, 25)
        oval(c, exx, hy + 5, ew, eh, paint('#ffffff'))
        circle(c, exx + look * 8, hy + 8, 13, paint('#15161a'))
        circle(c, exx + look * 8 - 4, hy + 3, 4, paint('#ffffff'))
        line(c, exx - 22, hy - 42 - (6 if female else 0), exx + 22, hy - 46 - (6 if female else 0), hair if not beard else '#2a2a2a', 7)
    oval(c, ex * 0.6, hy + 50, 10, 7, paint(C('#000000', 0.12)))
    if mouth > 0.15:
        oval(c, ex * 0.6, hy + 92, 14 + mouth * 6, 8 + mouth * 16, paint('#4a1f1f'))
    else:
        line(c, ex * 0.6 - 16, hy + 92, ex * 0.6 + 16, hy + 90, '#6b3a2c', 5)
    c.restore()


def _mixc(col, k, to=(34, 40, 58)):
    r, g, b = skia.ColorGetR(col), skia.ColorGetG(col), skia.ColorGetB(col)
    return skia.Color(int(r * (1 - k) + to[0] * k), int(g * (1 - k) + to[1] * k), int(b * (1 - k) + to[2] * k))


def taper(c, pts, w0, w1, pt):
    """Filled tapered limb through points (polyline), width w0 -> w1, rounded joints."""
    n = len(pts)
    lens = [0.0]
    for i in range(1, n):
        lens.append(lens[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    L = lens[-1] or 1
    left, right = [], []
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = lerp(w0, w1, lens[i] / L) / 2
        left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    c.drawPath(poly(left + right[::-1]), pt)
    for i in range(n):
        w = lerp(w0, w1, lens[i] / L) / 2
        c.drawCircle(pts[i][0], pts[i][1], w * 1.08, pt)


def listener(c, x, y, s=1.0, turn=0.0, tilt=0.0, arms='hang', t=0.0, walk=0.0, glow=0.5, dark=0.0,
             alpha=1.0, crouch=0.0, ripples=0.0, flip=False, sway=1.0, reach=0.0):
    """THE LISTENER. White ceramic, faceless, elongated egg head, long thin limbs. Feet at (x,y).
    Height ~ 900*s. turn: -1..1 head yaw toward sound; tilt: degrees; dark: 0..1 darkening."""
    if alpha <= 0.01:
        return
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    if alpha < 1:
        c.saveLayerAlpha(None, int(alpha * 255))
    hi = _mixc(C('#f7f6f2'), dark * 0.75)
    mid = _mixc(C('#dfe1e4'), dark * 0.8)
    lo = _mixc(C('#a9afba'), dark * 0.85)
    edge = _mixc(C('#7f8794'), dark * 0.6)
    wl = math.sin(walk * math.pi * 2) if walk else 0.0
    sw = math.sin(t * 0.9) * 3 * sway
    if glow > 0:
        oval(c, 0, -470, 260, 560, paint(C('#dce6ff', 0.12 * glow), blur=70))
    oval(c, 0, 0, 120, 14, paint(C('#000000', 0.4), blur=8))
    shd = lin(-70, 0, 90, 0, [hi, mid, lo], [0, 0.55, 1])
    fill = paint(hi)
    fill.setShader(shd)
    cr = crouch * 120
    # legs: long, thin, knees bent slightly backwards
    for side in (1, -1):
        ph = wl * side
        hip = (side * 24, -455 + cr)
        knee = (side * 30 - 22 + ph * 34, -240 + cr * 0.5)
        ankle = (side * 26 + ph * 56, -26)
        taper(c, [hip, knee, ankle], 40, 18, fill)
        fp = skia.Path()
        fp.moveTo(ankle[0] - 16, ankle[1] - 6)
        fp.cubicTo(ankle[0] + 20, ankle[1] - 14, ankle[0] + 66, ankle[1] + 10, ankle[0] + 70, ankle[1] + 22)
        fp.lineTo(ankle[0] - 18, ankle[1] + 22)
        fp.close()
        c.drawPath(fp, paint(lo))
    c.save()
    c.translate(0, cr)
    c.rotate(sw * 0.35 + crouch * 12)
    # pelvis + torso (organic hourglass, narrow chest)
    tp = skia.Path()
    tp.moveTo(-44, -470)
    tp.cubicTo(-58, -520, -34, -580, -40, -630)
    tp.cubicTo(-48, -680, -72, -700, -66, -728)
    tp.cubicTo(-40, -752, 40, -752, 66, -728)
    tp.cubicTo(72, -700, 48, -680, 40, -630)
    tp.cubicTo(34, -580, 58, -520, 44, -470)
    tp.cubicTo(30, -440, -30, -440, -44, -470)
    tp.close()
    c.drawPath(tp, fill)
    c.drawPath(tp, paint(edge, 'stroke', 2))
    # sternum / spine hint
    sp = skia.Path()
    sp.moveTo(4, -730)
    sp.cubicTo(-2, -650, 8, -560, 2, -480)
    c.drawPath(sp, paint(C('#8a929e', 0.35 * (1 - dark * 0.6)), 'stroke', 2.5))
    for k in range(3):
        yy = -700 + k * 26
        arc = skia.Path()
        arc.moveTo(-34 + k * 2, yy)
        arc.quadTo(0, yy + 10, 34 - k * 2, yy)
        c.drawPath(arc, paint(C('#8a929e', 0.22 * (1 - dark * 0.6)), 'stroke', 2))
    # arms: very long, wrists reaching below knee
    targets = {
        'hang': ((-78, -265), (84, -262)),
        'side': ((-170, -330), (170, -330)),
        'reach': ((-60, -560), (330, -640)),
        'reach2': ((300, -600), (340, -680)),
        'up': ((-150, -1100), (150, -1100)),
        'wall': ((260, -780), (300, -560)),
        'door': ((240, -700), (250, -520)),
    }
    tl, tr = targets.get(arms, targets['hang'])
    for side, (tx, ty) in ((-1, tl), (1, tr)):
        tx += math.sin(t * 1.1 + side) * 5 * sway + reach * 120 * (1 if side > 0 else 0.6)
        ty += math.cos(t * 0.9 + side) * 4 * sway
        sh = (side * 58, -722)
        a, el, hd = ik(sh[0], sh[1], tx, ty, 245, 240, bend=(1 if side > 0 else -1))
        taper(c, [sh, el, hd], 26, 14, fill)
        ang = math.atan2(hd[1] - el[1], hd[0] - el[0])
        for f in (-0.32, -0.12, 0.08, 0.28):
            fp = [hd, (hd[0] + math.cos(ang + f) * 45, hd[1] + math.sin(ang + f) * 45),
                  (hd[0] + math.cos(ang + f * 1.6) * 92, hd[1] + math.sin(ang + f * 1.6) * 92)]
            taper(c, fp, 9, 4, paint(mid))
        c.drawCircle(hd[0], hd[1], 13, paint(hi))
    # neck (long, leaning forward) + head
    c.save()
    c.translate(0, -738)
    c.rotate(tilt * 0.5 + 8)
    taper(c, [(0, 0), (3, -40), (8, -78)], 26, 18, fill)
    c.translate(8 + turn * 12, -78)
    c.rotate(tilt + turn * 6)
    hw = 66 - abs(turn) * 7
    hh = 230
    hp = skia.Path()
    hp.moveTo(0, 14)
    hp.cubicTo(hw * 0.9, 14, hw * 1.05, -hh * 0.45, hw * 0.78, -hh * 0.78)
    hp.cubicTo(hw * 0.55, -hh * 1.02, -hw * 0.55, -hh * 1.02, -hw * 0.78, -hh * 0.78)
    hp.cubicTo(-hw * 1.05, -hh * 0.45, -hw * 0.9, 14, 0, 14)
    hp.close()
    hs = lin(-hw, 0, hw, 0, [lo, hi, hi, mid, lo], [0, 0.25 + turn * 0.2, 0.45 + turn * 0.2, 0.75, 1])
    hpaint = paint(hi)
    hpaint.setShader(hs)
    c.drawPath(hp, hpaint)
    c.drawPath(hp, paint(edge, 'stroke', 2.2))
    # bottom occlusion
    c.save()
    c.clipPath(hp, doAntiAlias=True)
    oval(c, 0, 20, hw * 1.2, 50, paint(C('#000000', 0.18), blur=14))
    c.restore()
    # glossy ceramic highlight
    oval(c, -hw * 0.35 + turn * 28, -hh * 0.62, hw * 0.16, hh * 0.2, paint(C('#ffffff', 0.9 - dark * 0.6), blur=5))
    # facial plane: very faint smooth ridge showing where it 'faces'
    sx = turn * hw * 0.8
    if abs(turn) < 0.97:
        rp = skia.Path()
        rp.moveTo(sx, -hh * 0.82)
        rp.cubicTo(sx + turn * 10, -hh * 0.5, sx + turn * 10, -hh * 0.2, sx, -6)
        c.drawPath(rp, paint(C('#8c94a1', 0.40 * (1 - dark * 0.5)), 'stroke', 2.2))
        oval(c, sx, -hh * 0.42, hw * 0.42 * (1 - abs(turn) * 0.5), hh * 0.08, paint(C('#7f8794', 0.10), blur=8))
    c.restore()
    c.restore()
    if ripples > 0:
        dirn = 1 if turn >= 0 else -1
        hx, hyy = 40 * dirn + 10, -900 + cr
        for i in range(3):
            ph = (t * 0.8 + i / 3) % 1.0
            r = 70 + ph * 140
            a = (1 - ph) * ripples
            rc = skia.Rect.MakeLTRB(hx - r, hyy - r, hx + r, hyy + r)
            pth = skia.Path()
            pth.addArc(rc, -40 if dirn > 0 else 140, 80)
            c.drawPath(pth, paint(C('#eef3ff', 0.6 * a), 'stroke', 5))
    if alpha < 1:
        c.restore()
    c.restore()


def listener_silhouette(c, x, y, s=1.0, col='#d9dde4', a=1.0, turn=0.0, t=0.0):
    """Cheap small listener for crowds / far shots."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    sw = math.sin(t * 0.8 + x * 0.01) * 3
    pt = paint(C(col, a))
    for side in (-1, 1):
        line(c, side * 18, -420, side * 30, -10, C(col, a), 24)
    tp = poly([(-50, -690), (-30, -430), (30, -430), (50, -690)])
    c.drawPath(tp, pt)
    for side in (-1, 1):
        line(c, side * 46, -680, side * 70 + sw, -250, C(col, a), 16)
    line(c, 0, -690, 4, -760, C(col, a), 18)
    c.save()
    c.translate(6 + turn * 8, -760)
    c.rotate(turn * 10 + 6)
    oval(c, 0, -95, 52, 105, pt)
    c.restore()
    c.restore()


# ---------------------------------------------------------------- environment pieces

def sky(c, top='#0b1030', bot='#2a2f6b', w=W, h=H):
    c.drawRect(skia.Rect.MakeWH(w, h), paint('#000', shader=lin(0, 0, 0, h, [top, bot])))


def stars(c, seed=1, n=120, w=W, h=H * 0.6, t=0.0):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.random() * w, r.random() * h
        a = 0.3 + 0.5 * abs(math.sin(t * 0.7 + i))
        circle(c, x, y, r.random() * 1.6 + 0.5, paint(C('#ffffff', a * 0.6)))


def moon(c, x, y, r=110, col='#f3f0c8', glow='#fff6c0', ga=0.35):
    circle(c, x, y, r * 3.2, paint('#000', shader=rad(x, y, r * 3.2, [C(glow, ga), C(glow, 0)])))
    circle(c, x, y, r, paint(col))
    for dx, dy, rr in ((-30, -20, 18), (25, 30, 24), (40, -40, 12), (-40, 45, 10)):
        circle(c, x + dx * r / 110, y + dy * r / 110, rr * r / 110, paint(C('#000000', 0.06)))


def skyline(c, base_y, seed=3, col='#141a3a', win='#ffd76a', lit=0.08, minh=150, maxh=420, w=W, x0=-50, bw=(80, 200), win_off=False):
    r = random.Random(seed)
    x = x0
    while x < w + 50:
        bwid = r.uniform(*bw)
        bh = r.uniform(minh, maxh)
        rect(c, x, base_y - bh, bwid, bh + 2, paint(col))
        if r.random() < 0.3:
            rect(c, x + bwid * 0.4, base_y - bh - 40, 6, 40, paint(col))
        # windows
        cols_ = int(bwid // 28)
        rows = int(bh // 38)
        for i in range(cols_):
            for j in range(rows):
                if r.random() < lit and not win_off:
                    rect(c, x + 10 + i * 28, base_y - bh + 14 + j * 38, 14, 20, paint(C(win, 0.85)))
                elif r.random() < 0.25:
                    rect(c, x + 10 + i * 28, base_y - bh + 14 + j * 38, 14, 20, paint(C('#000000', 0.25)))
        x += bwid + r.uniform(4, 30)


def fog(c, t, y=700, a=0.18, col='#c9d4ff', n=7, seed=5, speed=12, h=180):
    r = random.Random(seed)
    for i in range(n):
        x = (r.random() * (W + 800) + t * speed * (0.6 + r.random())) % (W + 800) - 400
        yy = y + r.uniform(-h * 0.5, h * 0.5)
        oval(c, x, yy, r.uniform(300, 600), r.uniform(60, 130), paint(C(col, a * r.uniform(0.5, 1.0)), blur=60))


def street_lamp(c, x, y, h=520, on=1.0, flicker=0.0, t=0.0, cone=True, col='#ffd98a', side=1):
    rect(c, x - 7, y - h, 14, h, paint('#1b1e27'))
    line(c, x, y - h, x + side * 70, y - h - 10, '#1b1e27', 12)
    lx = x + side * 80
    ly = y - h
    rrect(c, lx - 30, ly - 12, 60, 22, 8, paint('#1b1e27'))
    k = on
    if flicker:
        k *= 0.4 + 0.6 * (1 if math.sin(t * 37) + math.sin(t * 23.3) > -0.6 * flicker else 0)
    if k > 0.02:
        oval(c, lx, ly + 10, 24, 8, paint(C(col, k)))
        circle(c, lx, ly + 10, 80, paint(C(col, 0.35 * k), blur=30))
        if cone:
            cp = poly([(lx - 22, ly + 12), (lx + 22, ly + 12), (lx + 190, y + 10), (lx - 190, y + 10)])
            c.drawPath(cp, paint('#000', shader=lin(0, ly, 0, y, [C(col, 0.30 * k), C(col, 0.04 * k)])))
            oval(c, lx, y + 10, 200, 32, paint(C(col, 0.18 * k), blur=12))


def car(c, x, y, s=1.0, col='#6b7380', door_open=False, lights=False, t=0.0, flip=False, dark=0.0):
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    oval(c, 0, 0, 260, 20, paint(C('#000000', 0.4), blur=10))
    body = skia.Path()
    body.moveTo(-250, -40)
    body.lineTo(-250, -110)
    body.cubicTo(-240, -130, -200, -135, -170, -138)
    body.lineTo(-110, -205)
    body.lineTo(90, -205)
    body.lineTo(160, -138)
    body.cubicTo(220, -132, 250, -120, 252, -95)
    body.lineTo(252, -40)
    body.close()
    c.drawPath(body, paint(col))
    c.drawPath(body, paint('#000', shader=lin(0, -205, 0, -40, [C('#ffffff', 0.08), C('#000000', 0.35 + dark * 0.4)])))
    win = poly([(-100, -192), (-10, -192), (-10, -142), (-150, -142)])
    c.drawPath(win, paint('#1d2433'))
    win2 = poly([(0, -192), (85, -192), (140, -142), (0, -142)])
    c.drawPath(win2, paint('#1d2433'))
    line(c, -95, -186, -40, -150, C('#ffffff', 0.12), 6)
    if door_open:
        dp = poly([(-10, -205), (-10, -45), (-95, -25), (-110, -190)])
        c.drawPath(dp, paint(col))
        c.drawPath(dp, paint(C('#000000', 0.3)))
    for wx in (-160, 160):
        circle(c, wx, -40, 44, paint('#121317'))
        circle(c, wx, -40, 20, paint('#5c606a'))
    rrect(c, 230, -112, 24, 16, 5, paint('#fff3b0' if lights else '#c9c9c9'))
    rrect(c, -254, -112, 14, 18, 4, paint('#ff3b30' if lights and int(t * 2) % 2 == 0 else '#6d1f1f'))
    if lights:
        cp = poly([(250, -110), (900, -260), (900, 60)])
        c.drawPath(cp, paint('#000', shader=lin(250, 0, 900, 0, [C('#fff6c8', 0.35), C('#fff6c8', 0)])))
    c.restore()


def tree(c, x, y, s=1.0, col='#0d1622', seed=0):
    r = random.Random(seed)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rect(c, -10, -120, 20, 120, paint(col))
    for i in range(5):
        w = 150 - i * 25
        yy = -100 - i * 80
        c.drawPath(poly([(-w + r.uniform(-10, 10), yy), (w + r.uniform(-10, 10), yy), (0, yy - 150)]), paint(col))
    c.restore()


def window_frame(c, x, y, w, h, frame='#d9d2c3', open_=0.0, curtain='#3d5a4c', curtains=True, cross=True):
    for (rx, ry, rw, rh) in ((x - 16, y - 16, w + 32, 16), (x - 16, y + h, w + 32, 16), (x - 16, y - 16, 16, h + 32), (x + w, y - 16, 16, h + 32)):
        rect(c, rx, ry, rw, rh, paint(frame))
        rect(c, rx, ry, rw, rh, paint(C('#000000', 0.15)))
    rect(c, x, y, w, h, paint(C('#bcd0ff', 0.06)))
    if cross:
        rect(c, x + w / 2 - 7, y, 14, h, paint(frame))
        rect(c, x, y + h * 0.35 - 7, w, 14, paint(frame))
    rect(c, x - 30, y + h + 10, w + 60, 26, paint(frame))
    if open_ > 0:
        # open sash swinging inward (drawn as parallelogram over left half)
        ow = w / 2 * (1 - open_ * 0.75)
        c.drawPath(poly([(x, y), (x + ow, y + 20 * open_), (x + ow, y + h - 20 * open_), (x, y + h)]), paint(C('#a9c1d9', 0.25)))
        c.drawPath(poly([(x, y), (x + ow, y + 20 * open_), (x + ow, y + h - 20 * open_), (x, y + h)]), paint(frame, 'stroke', 10))
    if curtains:
        for side in (0, 1):
            cx = x - 60 if side == 0 else x + w - 40
            cp = skia.Path()
            cp.moveTo(cx, y - 50)
            cp.lineTo(cx + 100, y - 50)
            for k in range(8):
                cp.lineTo(cx + 100 - (k % 2) * 14, y - 50 + (h + 120) * (k + 1) / 8)
            cp.lineTo(cx, y + h + 70)
            cp.close()
            c.drawPath(cp, paint(curtain))
            for k in range(3):
                line(c, cx + 20 + k * 28, y - 40, cx + 20 + k * 28, y + h + 60, C('#000000', 0.25), 6)


def room(c, wall='#3a3348', floor='#2a2230', horizon=780, light=None, pattern=True):
    rect(c, 0, 0, W, horizon, paint(wall))
    if pattern:
        for x in range(0, W, 90):
            rect(c, x, 0, 3, horizon, paint(C('#000000', 0.08)))
    rect(c, 0, horizon - 30, W, 30, paint(C('#000000', 0.25)))
    rect(c, 0, horizon, W, H - horizon, paint(floor))
    for x in range(-400, W + 400, 160):
        line(c, x, horizon, W / 2 + (x - W / 2) * 2.2, H, C('#000000', 0.18), 3)


def door(c, x, y, w=300, h=620, col='#5b3a26', open_=0.0, chain=True, peephole=True, knob='#c9a227', shake=0.0, t=0.0):
    sx = math.sin(t * 60) * 4 * shake
    rect(c, x - 22, y - 22, w + 44, h + 22, paint('#2a1d16'))
    rect(c, x, y, w, h, paint('#07080b'))
    c.save()
    c.translate(sx, 0)
    ow = w * (1 - open_)
    rect(c, x, y, ow, h, paint(col))
    rect(c, x, y, ow, h, paint('#000', shader=lin(x, 0, x + w, 0, [C('#ffffff', 0.05), C('#000000', 0.25)])))
    for i in range(2):
        rrect(c, x + 40 * (ow / w), y + 50 + i * 300, (w - 80) * (ow / w), 240, 6, paint(C('#000000', 0.18), 'stroke', 6))
    circle(c, x + ow - 40, y + h * 0.52, 16, paint(knob))
    if peephole:
        circle(c, x + ow / 2, y + 170, 9, paint('#111'))
        circle(c, x + ow / 2, y + 170, 13, paint(knob, 'stroke', 4))
    if chain:
        line(c, x + ow - 20, y + 260, x + w + 10, y + 270, '#9aa0a8', 7)
        for k in range(6):
            oval(c, x + ow - 20 + (w + 30 - ow) * k / 6, y + 262 + k * 1.6, 9, 6, paint('#bfc4cc', 'stroke', 3))
    c.restore()


def tv(c, x, y, w=520, h=320, on=True, mode='eas', t=0.0, text1='', text2=''):
    rrect(c, x - 18, y - 18, w + 36, h + 36, 14, paint('#0e0f13'))
    rect(c, x + w / 2 - 50, y + h + 18, 100, 30, paint('#0e0f13'))
    rect(c, x + w / 2 - 120, y + h + 44, 240, 12, paint('#0e0f13'))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    if not on:
        rect(c, x, y, w, h, paint('#14171d'))
        c.drawPath(poly([(x + w * 0.6, y), (x + w, y), (x + w, y + h * 0.4)]), paint(C('#ffffff', 0.04)))
    elif mode == 'eas':
        rect(c, x, y, w, h, paint('#7a0c0c'))
        blink = 1 if int(t * 2) % 2 == 0 else 0.6
        rect(c, x, y, w, h * 0.22, paint(C('#ffde38', blink)))
        text(c, 'ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ', x + w / 2, y + h * 0.15, h * 0.08, '#2a0505', align='center')
        text(c, text1 or 'ОРГАНИЗМ N-0', x + w / 2, y + h * 0.48, h * 0.13, '#ffffff', align='center')
        text(c, text2 or 'ОСТАВАЙТЕСЬ ДОМА. НЕ ШУМИТЕ.', x + w / 2, y + h * 0.68, h * 0.065, '#ffd0d0', FONT_XB, align='center')
        tx = x + w - ((t * 120) % (w + 900))
        rect(c, x, y + h * 0.82, w, h * 0.18, paint('#1a0202'))
        text(c, '  ВНИМАНИЕ • НЕ ВЫХОДИТЕ НА УЛИЦУ • ВЫКЛЮЧИТЕ ЗВУК • ЖДИТЕ ИНСТРУКЦИЙ •', tx, y + h * 0.94, h * 0.07, '#ffffff', FONT_XB)
    elif mode == 'static':
        r = np.random.RandomState(int(t * 25) % 50)
        for i in range(140):
            yy = y + r.randint(0, int(h))
            rect(c, x, yy, w, r.randint(1, 4), paint(C('#ffffff', r.uniform(0.05, 0.35))))
        rect(c, x, y, w, h, paint(C('#6c7a8a', 0.35)))
    elif mode == 'show':
        rect(c, x, y, w, h, paint('#2b6cb0'))
        circle(c, x + w * 0.3, y + h * 0.55, h * 0.22, paint('#f6d365'))
        rect(c, x + w * 0.5, y + h * 0.3, w * 0.35, h * 0.5, paint('#e8eef7'))
        text(c, 'ПРЯМОЙ ЭФИР', x + 20, y + 40, 26, '#ffffff')
    c.restore()
    if on:
        col = '#ff5a4a' if mode == 'eas' else '#9fc6ff'
        oval(c, x + w / 2, y + h / 2, w * 1.2, h * 1.6, paint(C(col, 0.10), blur=80))


def phone_screen(c, x, y, w, h, t=0.0, mode='nosignal', lines=None, battery=34, time='06:12', notif=None):
    rrect(c, x - 22, y - 22, w + 44, h + 44, 60, paint('#0a0b0e'))
    rrect(c, x - 22, y - 22, w + 44, h + 44, 60, paint('#3a3d44', 'stroke', 4))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 44, 44), True)
    rect(c, x, y, w, h, paint('#000', shader=lin(0, y, 0, y + h, ['#1c2b4a', '#0b0f1c'])))
    text(c, time, x + 40, y + 60, 34, '#ffffff', FONT_XB)
    # signal bars
    for i in range(4):
        rect(c, x + w - 190 + i * 16, y + 48 - i * 8, 10, 10 + i * 8, paint(C('#ffffff', 0.25 if mode == 'nosignal' else 0.9)))
    if mode == 'nosignal':
        line(c, x + w - 196, y + 22, x + w - 126, y + 58, '#ff4d4d', 5)
    rrect(c, x + w - 100, y + 30, 54, 26, 6, paint('#ffffff', 'stroke', 3))
    bc = '#ff4d4d' if battery < 15 else '#ffffff'
    rect(c, x + w - 96, y + 34, 46 * battery / 100, 18, paint(bc))
    if mode == 'nosignal':
        text(c, 'НЕТ СЕТИ', x + w / 2, y + h * 0.38, 64, '#ffffff', align='center')
        text(c, 'Только SOS-вызовы', x + w / 2, y + h * 0.45, 28, '#9aa8c2', FONT_XB, align='center')
        circle(c, x + w / 2, y + h * 0.62, 70, paint('#ff4d4d', 'stroke', 8))
        line(c, x + w / 2 - 50, y + h * 0.62 - 50, x + w / 2 + 50, y + h * 0.62 + 50, '#ff4d4d', 8)
    if lines:
        yy = y + 130
        for who, msg, mine in lines:
            bw = min(w - 80, text_w(msg, 30, FONT_XB) + 50)
            bx = x + w - 30 - bw if mine else x + 30
            rrect(c, bx, yy, bw, 70, 24, paint('#2f7cf6' if mine else '#2a2f3b'))
            text(c, msg, bx + 25, yy + 46, 30, '#ffffff', FONT_XB)
            if who:
                text(c, who, bx + 10, yy - 10, 22, '#8b97ad', FONT_XB)
            yy += 120
    if notif:
        k = notif[1]
        if k > 0:
            ny = y + 90 - (1 - ease_out(k)) * 140
            rrect(c, x + 20, ny, w - 40, 130, 28, paint(C('#e9edf5', 0.96)))
            text(c, notif[0], x + 50, ny + 55, 30, '#111111', FONT_XB)
            text(c, notif[2] if len(notif) > 2 else '', x + 50, ny + 100, 26, '#444b57', FONT_XB)
    c.restore()


def corridor(c, t=0.0, col='#1a1d24', lights=True, flicker=0.0, vanish=(960, 520), doors=True, floor='#121418', wall='#23272f', ceil='#15171c'):
    vx, vy = vanish
    fw, fh = 300, 360
    fx0, fy0 = vx - fw / 2, vy - fh / 2
    c.drawRect(skia.Rect.MakeWH(W, H), paint(col))
    c.drawPath(poly([(0, 0), (W, 0), (fx0 + fw, fy0), (fx0, fy0)]), paint(ceil))
    c.drawPath(poly([(0, H), (W, H), (fx0 + fw, fy0 + fh), (fx0, fy0 + fh)]), paint(floor))
    c.drawPath(poly([(0, 0), (fx0, fy0), (fx0, fy0 + fh), (0, H)]), paint(wall))
    c.drawPath(poly([(W, 0), (fx0 + fw, fy0), (fx0 + fw, fy0 + fh), (W, H)]), paint(wall))
    c.drawPath(poly([(W, 0), (fx0 + fw, fy0), (fx0 + fw, fy0 + fh), (W, H)]), paint(C('#000000', 0.15)))
    rect(c, fx0, fy0, fw, fh, paint('#050608'))
    # floor tiles lines
    for k in range(1, 9):
        z = k / 9
        zz = z ** 2.2
        yy = H + (fy0 + fh - H) * (1 - (1 - zz))
        yy = lerp(H, fy0 + fh, 1 - (1 - z) ** 0.5)
    for k in range(1, 7):
        f = 1 - (0.62 ** k)
        x0 = lerp(0, fx0, f)
        x1 = lerp(W, fx0 + fw, f)
        y0 = lerp(0, fy0, f)
        y1 = lerp(H, fy0 + fh, f)
        line(c, x0, y1, x1, y1, C('#000000', 0.35), 3)
        line(c, x0, y0, x1, y0, C('#000000', 0.3), 3)
        if doors and k < 6:
            # doors on side walls
            f2 = 1 - (0.62 ** (k + 0.55))
            dx0, dx1 = lerp(0, fx0, f), lerp(0, fx0, f2)
            dy0t, dy1t = lerp(0, fy0, f) + (lerp(H, fy0 + fh, f) - lerp(0, fy0, f)) * 0.25, lerp(0, fy0, f2) + (lerp(H, fy0 + fh, f2) - lerp(0, fy0, f2)) * 0.25
            dy0b, dy1b = lerp(H, fy0 + fh, f), lerp(H, fy0 + fh, f2)
            c.drawPath(poly([(dx0, dy0t), (dx1, dy1t), (dx1, dy1b), (dx0, dy0b)]), paint('#2d2a26'))
            ex0, ex1 = W - dx0, W - dx1
            c.drawPath(poly([(ex0, dy0t), (ex1, dy1t), (ex1, dy1b), (ex0, dy0b)]), paint('#24221f'))
        if lights:
            lx = vx
            ly = lerp(0, fy0, f) + 8
            on = 1.0
            if flicker and k == 2:
                on = 0.2 + 0.8 * (1 if math.sin(t * 31) + math.sin(t * 17.7) > -0.3 else 0)
            lw = (x1 - x0) * 0.18
            rrect(c, lx - lw / 2, ly, lw, 10 * (1 - f) + 3, 3, paint(C('#e8f1ff', 0.9 * on)))
            cp = poly([(lx - lw / 2, ly), (lx + lw / 2, ly), (lx + lw * 1.6, y1), (lx - lw * 1.6, y1)])
            c.drawPath(cp, paint('#000', shader=lin(0, ly, 0, y1, [C('#dfe9ff', 0.13 * on), C('#dfe9ff', 0.0)])))


def vignette(c, k=0.75):
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#000', shader=rad(W / 2, H / 2, 1150, [C('#000000', 0), C('#000000', 0.15 * k), C('#000000', k)], [0.45, 0.7, 1.0])))


_GRAIN = None


def grain(c, t, a=0.06):
    global _GRAIN
    if _GRAIN is None:
        _GRAIN = []
        rng = np.random.RandomState(7)
        for i in range(6):
            n = rng.randint(0, 255, (H // 2, W // 2), dtype=np.uint8)
            img = np.zeros((H // 2, W // 2, 4), np.uint8)
            img[..., 0] = n
            img[..., 1] = n
            img[..., 2] = n
            img[..., 3] = 255
            _GRAIN.append(skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType))
    im = _GRAIN[int(t * 12.5) % len(_GRAIN)]
    p = skia.Paint(Alphaf=a)
    p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(im, skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)


def letterbox_text(c, s, a=1.0, y=H - 70, size=34):
    text(c, s, W / 2, y, size, C('#ffffff', a), FONT_XB, align='center', shadow=4)


def rule_card(c, num, title, sub=None, k=1.0, t=0.0, total=15):
    """Thumbnail-style rule header: red pill 'ПРАВИЛО 01', big yellow title."""
    if k <= 0:
        return
    a = clamp(k)
    slide = (1 - ease_out(k)) * -80
    c.save()
    c.translate(slide, 0)
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 330), paint('#000', shader=lin(0, 0, 0, 330, [C('#000000', 0.75 * a), C('#000000', 0)])))
    label(c, f'ПРАВИЛО {num:02d} / {total}', 70, 58, 38, bg='#e53935', fg='#ffffff', angle=-3, alpha=a)
    lines_ = title.split('\n')
    yy = 200
    for ln in lines_:
        text(c, ln, 72, yy, 92, C('#ffd21e', a), stroke=14, stroke_col='#000000', shadow=8, alpha=a)
        yy += 100
    if sub:
        label(c, sub, 76, yy - 40, 30, bg='#ffffff', fg='#111111', angle=-2, alpha=a)
    c.restore()


def chapter_card(c, part, title, k=1.0):
    a = clamp(k)
    c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', 0.55 * a)))
    text(c, f'ЧАСТЬ {part}', W / 2, H / 2 - 60, 40, C('#e53935', a), FONT_XB, align='center')
    text(c, title, W / 2, H / 2 + 50, 100, C('#ffffff', a), align='center', stroke=0, shadow=10)


def sound_waves(c, x, y, t, k=1.0, col='#ffffff', n=3, spread=1.0, dirn=0):
    for i in range(n):
        ph = (t * 1.2 + i / n) % 1.0
        r = (40 + ph * 220) * spread
        a = (1 - ph) * k
        if dirn == 0:
            circle(c, x, y, r, paint(C(col, 0.5 * a), 'stroke', 5))
        else:
            pth = skia.Path()
            pth.addArc(skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), (-45 if dirn > 0 else 135), 90)
            c.drawPath(pth, paint(C(col, 0.6 * a), 'stroke', 6))


def music_notes(c, x, y, t, k=1.0, col='#ffd21e'):
    for i in range(6):
        ph = (t * 0.5 + i / 6) % 1.0
        nx = x + math.sin(ph * 6 + i) * 60 + (i - 3) * 30
        ny = y - ph * 300
        a = (1 - ph) * k
        circle(c, nx, ny, 14, paint(C(col, a)))
        line(c, nx + 12, ny, nx + 12, ny - 50, C(col, a), 5)
        line(c, nx + 12, ny - 50, nx + 34, ny - 40, C(col, a), 5)
