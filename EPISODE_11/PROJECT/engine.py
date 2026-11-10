"""Drawing engine for Episode 11: primitives, characters, effects.
Everything is vector (skia) so close-ups stay sharp."""
import math, random
import skia

W, H = 1080, 1920
FD = '/usr/share/fonts/truetype/roboto/unhinted/'
TF_BOLD = skia.Typeface.MakeFromFile(FD + 'RobotoCondensed-Bold.ttf')
TF_MED = skia.Typeface.MakeFromFile(FD + 'RobotoCondensed-Medium.ttf')
TF_BLACK = skia.Typeface.MakeFromFile(FD + 'RobotoTTF/Roboto-Black.ttf')


# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ramp(u, a, b):
    return ease((u - a) / (b - a)) if b != a else float(u >= a)


def hx(h):
    h = h.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def tohex(r, g, b):
    return '#%02x%02x%02x' % (int(clamp(r, 0, 255)), int(clamp(g, 0, 255)), int(clamp(b, 0, 255)))


def shade(h, f):
    r, g, b = hx(h)
    return tohex(r * f, g * f, b * f)


def mix(h1, h2, t):
    a, b = hx(h1), hx(h2)
    return tohex(*[lerp(a[i], b[i], t) for i in range(3)])


def C(h, a=1.0):
    r, g, b = hx(h)
    return skia.Color(r, g, b, int(clamp(a) * 255))


def P(h='#000000', a=1.0, stroke=None, cap='round', blur=None, blend=None, shader=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(C(h, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap({'round': skia.Paint.kRound_Cap, 'butt': skia.Paint.kButt_Cap,
                        'square': skia.Paint.kSquare_Cap}[cap])
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
    return p


def lin(x0, y0, x1, y1, cols):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)],
                                          [C(*c) if isinstance(c, tuple) else C(c) for c in cols])


def rad(x, y, r, cols):
    return skia.GradientShader.MakeRadial(skia.Point(x, y), r,
                                          [C(*c) if isinstance(c, tuple) else C(c) for c in cols])


def rect(c, x0, y0, x1, y1, paint, r=0):
    rr = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    if r:
        c.drawRoundRect(rr, r, r, paint)
    else:
        c.drawRect(rr, paint)


def circle(c, x, y, r, paint):
    c.drawCircle(x, y, r, paint)


def oval(c, x, y, rx, ry, paint):
    c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), paint)


def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth(pts, close=True):
    """Catmull-Rom through points -> cubic path."""
    p = skia.Path()
    n = len(pts)
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def line(c, x0, y0, x1, y1, paint):
    c.drawLine(x0, y0, x1, y1, paint)


def text(c, s, x, y, size, h='#ffffff', a=1.0, tf=None, align='center', spacing=0.0, paint=None):
    f = skia.Font(tf or TF_BOLD, size)
    p = paint or P(h, a)
    if spacing:
        widths = [f.measureText(ch) + spacing for ch in s]
        tot = sum(widths) - spacing
        cx = x - tot / 2 if align == 'center' else (x - tot if align == 'right' else x)
        for ch, w in zip(s, widths):
            c.drawString(ch, cx, y, f, p)
            cx += w
        return tot
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    c.drawString(s, x, y, f, p)
    return w


def wrap(s, size, maxw, tf=None):
    f = skia.Font(tf or TF_BOLD, size)
    out, cur = [], ''
    for wd in s.split():
        t = (cur + ' ' + wd).strip()
        if f.measureText(t) > maxw and cur:
            out.append(cur)
            cur = wd
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def layer(c, alpha):
    p = skia.Paint()
    p.setAlphaf(clamp(alpha))
    c.saveLayer(None, p)


def cam(c, cx, cy, z, rot=0.0):
    c.translate(W / 2, H / 2)
    if rot:
        c.rotate(rot)
    c.scale(z, z)
    c.translate(-cx, -cy)


def vignette(c, s=0.65, h='#000000'):
    c.drawRect(skia.Rect.MakeWH(W, H),
               P(shader=rad(W / 2, H * 0.45, H * 0.72, [(h, 0), (h, 0), (h, s)])))


def grade(c, h, a, mode=skia.BlendMode.kMultiply):
    c.drawRect(skia.Rect.MakeWH(W, H), P(h, a, blend=mode))


def noise1(x, seed=0):
    """cheap smooth 1D noise in [-1,1]"""
    i = math.floor(x)
    f = x - i

    def h(n):
        return (math.sin((n + seed * 57.13) * 127.1) * 43758.5453) % 1.0 * 2 - 1
    return lerp(h(i), h(i + 1), f * f * (3 - 2 * f))


# ---------------------------------------------------------------- characters
class Look:
    def __init__(self, skin='#d2a57c', hair='#151517', style='messy', top='#25262c', pants='#1d1e24',
                 shoes='#b8b8b8', cap=None, shirt=None, glasses=False, tie=None, seed=1,
                 width=1.0, height=1.0, cheek=None, lips=None):
        self.skin, self.hair, self.style, self.top, self.pants = skin, hair, style, top, pants
        self.shoes, self.cap, self.shirt, self.glasses, self.tie = shoes, cap, shirt, glasses, tie
        self.seed, self.width, self.height, self.lips = seed, width, height, lips
        r = random.Random(seed)
        # hair spike pattern (fixed per character -> consistent design)
        self.spk = [r.uniform(0.0, 1.0) for _ in range(64)]


HERO = Look(skin='#d4a77e', hair='#121214', style='messy', top='#25262d', pants='#1b1c22',
            shoes='#b9b9b7', seed=11)
FRIEND = Look(skin='#e3b58e', hair='#5b3b24', style='capped', cap='#33503a', top='#6a4430',
              shirt='#d8cfbd', pants='#2f4566', shoes='#e5e0d4', seed=23)


def _vec(a, side):
    r = math.radians(a)
    return side * math.sin(r), math.cos(r)


def _limb(c, x, y, a1, a2, L1, L2, w, col, side, end=None, endr=0, cuff=None, cap='round'):
    dx, dy = _vec(a1, side)
    ex, ey = x + dx * L1, y + dy * L1
    dx2, dy2 = _vec(a2, side)
    hx_, hy_ = ex + dx2 * L2, ey + dy2 * L2
    pth = skia.Path()
    pth.moveTo(x, y)
    pth.lineTo(ex, ey)
    pth.lineTo(hx_, hy_)
    c.drawPath(pth, P(col, stroke=w, cap=cap))
    if cuff:
        cx_, cy_ = ex + dx2 * (L2 - 6), ey + dy2 * (L2 - 6)
        circle(c, cx_, cy_, w * 0.5, P(cuff))
    if end:
        circle(c, hx_ + dx2 * endr * 0.6, hy_ + dy2 * endr * 0.6, endr, P(end))
    return hx_, hy_


def ik(sx, sy, tx, ty, L1, L2, side, bend=1):
    """returns (a1,a2) limb angles (deg from down, outward positive) reaching target"""
    dx, dy = tx - sx, ty - sy
    d = clamp(math.hypot(dx, dy), 1, L1 + L2 - 0.1)
    base = math.atan2(dx * side, dy)  # angle from down
    cosA = clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1)
    A = math.acos(cosA) * bend
    a1 = math.degrees(base + A)
    ex = sx + side * math.sin(math.radians(a1)) * L1
    ey = sy + math.cos(math.radians(a1)) * L1
    a2 = math.degrees(math.atan2((tx - ex) * side, ty - ey))
    return a1, a2


def hair_shape(look, R, turn, t, back=False):
    """front hair path in head-local coords (center 0,0)"""
    s = look.spk
    style = look.style
    sw = math.sin(t * 1.7) * 0.025
    if back:
        pts = []
        for i in range(22):
            th = math.radians(-30 + i * 240 / 21)
            rr = R * (1.08 + (0.14 if i % 2 else 0) * (0.6 + 0.6 * s[i]))
            pts.append((math.cos(th) * rr, -math.sin(th) * rr))
        pts += [(-R * 0.75, R * 0.75), (0, R * 0.85), (R * 0.75, R * 0.75)]
        return poly(pts) if style == 'messy' else smooth(pts)
    sh = turn * R * 0.32
    if style == 'messy':
        pts = []
        n = 20
        for i in range(n + 1):
            th = math.radians(-28 + i * 236 / n)
            spike = (0.09 + 0.11 * s[i]) if i % 2 else 0.0
            rr = R * (1.04 + spike + sw * (i % 3))
            pts.append((math.cos(th) * rr - turn * R * 0.06, -math.sin(th) * rr - R * 0.02))
        # fringe back across the forehead (left -> right)
        m = 13
        for j in range(m + 1):
            k = j
            x = -R * 0.98 + 1.96 * R * k / m
            edge = abs(x) / R
            if k % 2 == 0:
                y = -R * (0.5 - 0.1 * s[30 + k]) + edge ** 3 * R * 0.75
            else:
                y = -R * (0.27 + 0.08 * s[40 + k]) + edge ** 3 * R * 0.8 + sw * R * 2
            x2 = x + sh * (1 - edge ** 2) + (R * 0.06 if k % 2 else 0) * (1 if turn >= 0 else -1)
            pts.append((x2, y))
        return poly(pts)
    if style in ('short', 'long', 'bob', 'bun'):
        pts = []
        for i in range(17):
            th = math.radians(-10 + i * 200 / 16)
            rr = R * 1.06
            pts.append((math.cos(th) * rr, -math.sin(th) * rr - R * 0.03))
        for j in range(7):
            x = -R * 0.98 + 1.96 * R * j / 6
            pts.append((x + sh * 0.7, -R * (0.35 + 0.06 * math.sin(j * 1.7 + look.seed)) + (abs(x) / R) ** 4 * R * 0.5))
        return smooth(pts)
    if style == 'bald':
        p = skia.Path()
        for sgn in (-1, 1):
            p.addOval(skia.Rect.MakeLTRB(sgn * R * 0.98 - R * 0.14, -R * 0.35, sgn * R * 0.98 + R * 0.14, R * 0.2))
        return p
    return skia.Path()


def draw_head(c, look, R, turn=0.0, expr='neutral', blink=0.0, eye=(0, 0), t=0.0, back=False, mouth=0.0):
    skin = look.skin
    # hair behind head
    if look.style in ('long', 'bob') and not back:
        L = 1.5 if look.style == 'long' else 0.85
        c.drawPath(smooth([(-R * 1.05, -R * 0.2), (-R * 1.12, R * L), (-R * 0.6, R * (L + 0.1)),
                           (R * 0.6, R * (L + 0.1)), (R * 1.12, R * L), (R * 1.05, -R * 0.2), (0, -R * 1.1)]),
                   P(shade(look.hair, 0.8)))
    if look.style == 'bun':
        circle(c, -turn * R * 0.3, -R * 1.12, R * 0.38, P(look.hair))
    head = skia.Path()
    head.addCircle(0, 0, R)
    c.drawPath(head, P(skin))
    # soft form shadow
    c.save()
    c.clipPath(head, doAntiAlias=True)
    circle(c, R * 0.55 - turn * R * 0.3, R * 0.55, R * 1.05, P(shade(skin, 0.82), 0.55, blur=R * 0.25))
    circle(c, -R * 0.35 + turn * R * 0.2, -R * 0.45, R * 0.45, P('#ffffff', 0.08, blur=R * 0.3))
    c.restore()
    if back:
        if look.cap:
            c.drawPath(smooth([(-R * 0.9, -R * 0.3), (R * 0.9, -R * 0.3), (R * 0.8, R * 0.35), (0, R * 0.5), (-R * 0.8, R * 0.35)]), P(look.hair))
        else:
            c.drawPath(hair_shape(look, R, turn, t, back=True), P(look.hair))
        if look.cap:
            _cap(c, look, R, 0, back=True)
        return
    fx = turn * R * 0.44
    # ear on far side when turned
    if abs(turn) > 0.35:
        circle(c, -turn * R * 0.38, R * 0.08, R * 0.15, P(shade(skin, 0.88)))
    # eyes
    ex = R * 0.27 * (1 - 0.3 * abs(turn))
    big = {'surprised': 1.22, 'shock': 1.3, 'scared': 1.2}.get(expr, 1.0)
    ew, eh = R * 0.095 * big, R * 0.14 * big
    open_ = 1 - clamp(blink)
    if expr == 'sleepy':
        open_ *= 0.35
    if expr == 'smirk' or expr == 'calm':
        open_ *= 0.7
    for sgn in (-1, 1):
        if abs(turn) > 0.8 and sgn == -math.copysign(1, turn):
            continue
        x = fx + sgn * ex + eye[0] * R * 0.06
        y = R * 0.06 + eye[1] * R * 0.05
        if open_ < 0.2:
            c.drawPath(poly([(x - ew * 1.1, y + R * 0.02), (x + ew * 1.1, y + R * 0.02)], close=False),
                       P('#141416', stroke=R * 0.035))
        else:
            oval(c, x, y, ew, eh * open_, P('#141416'))
            circle(c, x + ew * 0.35, y - eh * 0.4 * open_, ew * 0.32, P('#ffffff', 0.85))
            if expr in ('smirk', 'calm', 'sleepy'):  # heavy lids
                rect(c, x - ew * 1.4, y - eh * 1.2, x + ew * 1.4, y - eh * 0.25, P(skin))
                line(c, x - ew * 1.3, y - eh * 0.25, x + ew * 1.3, y - eh * 0.25, P('#141416', stroke=R * 0.03))
    # brows
    bcol = shade(look.hair, 0.9) if look.hair != '#151517' else '#141416'
    by = -R * 0.2
    braise = {'surprised': -0.1, 'shock': -0.14, 'scared': -0.08, 'worried': -0.04}.get(expr, 0) * R
    for sgn in (-1, 1):
        if abs(turn) > 0.8 and sgn == -math.copysign(1, turn):
            continue
        x = fx + sgn * ex
        L = R * 0.15
        d = {'angry': 0.07, 'worried': -0.06, 'scared': -0.07, 'sad': -0.06}.get(expr, 0.0) * R
        if expr == 'smirk' and sgn > 0:
            d = -0.04 * R
        yb = by + braise
        c.drawPath(poly([(x - sgn * L, yb + d), (x + sgn * L, yb - d * 0.6)], close=False),
                   P(bcol, stroke=R * 0.085))
    # blush
    if expr in ('smile', 'surprised', 'shock', 'happy'):
        for sgn in (-1, 1):
            oval(c, fx + sgn * R * 0.47, R * 0.3, R * 0.11, R * 0.06, P('#e2765e', 0.28, blur=R * 0.03))
    # mouth
    mx, my = fx + turn * R * 0.05, R * 0.47
    mc = '#3a1c1c'
    if expr in ('surprised',):
        oval(c, mx, my, R * 0.06, R * (0.07 + 0.03 * mouth), P(mc))
    elif expr in ('shock', 'scared'):
        c.drawPath(smooth([(mx - R * 0.15, my + R * 0.04), (mx, my - R * 0.08), (mx + R * 0.15, my + R * 0.04),
                           (mx + R * 0.07, my + R * 0.16), (mx - R * 0.07, my + R * 0.16)]), P(mc))
        oval(c, mx, my + R * 0.11, R * 0.07, R * 0.035, P('#a24c4c'))
    elif expr in ('smile', 'happy'):
        pth = skia.Path()
        pth.moveTo(mx - R * 0.16, my - R * 0.02)
        pth.quadTo(mx, my + R * 0.16, mx + R * 0.16, my - R * 0.02)
        c.drawPath(pth, P(mc, stroke=R * 0.045))
    elif expr in ('smirk', 'calm'):
        pth = skia.Path()
        pth.moveTo(mx - R * 0.12, my + R * 0.02)
        pth.quadTo(mx + R * 0.02, my + R * 0.07, mx + R * 0.14, my - R * 0.04)
        c.drawPath(pth, P(mc, stroke=R * 0.04))
    elif expr in ('worried', 'sad'):
        pth = skia.Path()
        pth.moveTo(mx - R * 0.12, my + R * 0.05)
        pth.quadTo(mx, my - R * 0.04, mx + R * 0.12, my + R * 0.05)
        c.drawPath(pth, P(mc, stroke=R * 0.04))
    elif expr == 'angry':
        line(c, mx - R * 0.13, my + R * 0.04, mx + R * 0.13, my + R * 0.01, P(mc, stroke=R * 0.045))
    elif expr == 'talk':
        oval(c, mx, my, R * 0.09, R * (0.02 + 0.06 * mouth), P(mc))
    if look.lips and expr not in ('shock', 'scared'):
        pass
    if expr in ('worried', 'scared'):
        sx = fx + R * 0.72
        c.drawPath(smooth([(sx, -R * 0.12), (sx + R * 0.08, R * 0.08), (sx, R * 0.14), (sx - R * 0.08, R * 0.08)]),
                   P('#9fc6e6', 0.85))
    # hair / cap in front
    if look.cap:
        _cap(c, look, R, turn)
    else:
        c.drawPath(hair_shape(look, R, turn, t), P(look.hair))
        if look.style == 'messy':
            for i in range(4):
                a = math.radians(40 + i * 28)
                x0, y0 = math.cos(a) * R * 0.75, -math.sin(a) * R * 0.75
                line(c, x0, y0, x0 * 1.2, y0 * 1.2, P(mix(look.hair, '#4a4a55', 0.6), 0.6, stroke=R * 0.03))
    if look.glasses:
        for sgn in (-1, 1):
            if abs(turn) > 0.8 and sgn == -math.copysign(1, turn):
                continue
            circle(c, fx + sgn * ex, R * 0.06, R * 0.17, P('#2a2a2e', stroke=R * 0.035))
        line(c, fx - ex + R * 0.17, R * 0.04, fx + ex - R * 0.17, R * 0.04, P('#2a2a2e', stroke=R * 0.03))


def _cap(c, look, R, turn, back=False):
    hair = look.hair
    # tufts under cap
    for sgn in (-1, 1):
        x = sgn * R * 0.92
        c.drawPath(poly([(x, -R * 0.35), (x + sgn * R * 0.16, -R * 0.12), (x + sgn * R * 0.02, -R * 0.08),
                         (x + sgn * R * 0.12, R * 0.12), (x - sgn * R * 0.06, R * 0.02)]), P(hair))
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeLTRB(-R * 1.05, -R * 1.12, R * 1.05, R * 0.6), 180, 180)
    dome.close()
    c.drawPath(dome, P(look.cap))
    rect(c, -R * 1.05, -R * 0.33, R * 1.05, -R * 0.22, P(shade(look.cap, 0.8)))
    circle(c, -turn * R * 0.1, -R * 1.08, R * 0.07, P(shade(look.cap, 0.8)))
    if back:
        return
    if abs(turn) > 0.6:
        sgn = math.copysign(1, turn)
        c.drawPath(smooth([(sgn * R * 0.4, -R * 0.33), (sgn * R * 1.55, -R * 0.36), (sgn * R * 1.6, -R * 0.24),
                           (sgn * R * 0.5, -R * 0.2)]), P(shade(look.cap, 0.75)))
    else:
        oval(c, turn * R * 0.6, -R * 0.27, R * 0.95, R * 0.17, P(shade(look.cap, 0.72)))


def draw_person(c, x, y, s, look, facing=0, turn=None, expr='neutral', blink=0.0, eye=(0, 0), t=0.0,
                walk=None, arms=None, hands=None, back=False, shadow=True, bob=0.0, tilt=0.0, mouth=0.0,
                seated=False, dim=0.0):
    """Feet at (x,y). s=scale (1 -> ~640px tall). facing: 0 front, +1 right, -1 left."""
    c.save()
    c.translate(x, y)
    c.scale(s * look.width, s * look.height)
    if shadow:
        oval(c, 0, 0, 115, 16, P('#000000', 0.35, blur=6))
    breathe = math.sin(t * 2.2) * 2.5
    if walk is not None:
        bob += abs(math.sin(walk)) * -8
    top, pants = look.top, look.pants
    if facing == 0:
        # ---- front / back view
        for sgn in (-1, 1):
            _limb(c, sgn * 33, -300 + bob, 0, 0, 150, 130, 60, pants, sgn, cap='butt')
            fx = sgn * 36
            rect(c, fx - 38 + sgn * 4, -28, fx + 38 + sgn * 4, 0, P(look.shoes), r=14)
            rect(c, fx - 38 + sgn * 4, -8, fx + 38 + sgn * 4, 0, P(shade(look.shoes, 0.75)), r=4)
        c.translate(0, bob + breathe * 0.3)
        body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-80, -478, 80, -268), 32, 32)
        c.drawRRect(body, P(top))
        if look.shirt and not back:
            c.drawPath(poly([(-28, -476), (28, -476), (22, -268), (-22, -268)]), P(look.shirt))
            line(c, -30, -470, -24, -270, P(shade(top, 0.8), stroke=6))
            line(c, 30, -470, 24, -270, P(shade(top, 0.8), stroke=6))
        if look.tie and not back:
            c.drawPath(poly([(-9, -470), (9, -470), (13, -360), (0, -340), (-13, -360)]), P(look.tie))
        rect(c, -80, -292, 80, -268, P(shade(top, 0.85)), r=10)
        # arms
        a = arms or (7, 4, 7, 4)
        for i, sgn in enumerate((-1, 1)):
            sx, sy = sgn * 72, -452
            a1, a2 = a[i * 2], a[i * 2 + 1]
            if hands and hands[i]:
                a1, a2 = ik(sx, sy, hands[i][0], hands[i][1], 118, 100, sgn)
            _limb(c, sx, sy, a1, a2, 118, 92, 46, top, sgn, end=look.skin, endr=23, cuff=shade(top, 0.82))
        # neck + head
        rect(c, -16, -500, 16, -466, P(shade(look.skin, 0.85)))
        c.translate(0, -568)
        c.rotate(tilt)
        draw_head(c, look, 84, 0 if turn is None else turn, expr, blink, eye, t, back=back, mouth=mouth)
    else:
        c.scale(facing, 1)
        ph = walk if walk is not None else 0.0
        amp = 26 if walk is not None else 0
        legs = [(amp * math.sin(ph), 0.62), (-amp * math.sin(ph), 1.0)]
        # back leg first
        for k, (ang, f) in enumerate(legs):
            col = shade(pants, 0.78) if k == 0 else pants
            sh = shade(look.shoes, 0.78) if k == 0 else look.shoes
            knee = max(0.0, -math.cos(ph + (math.pi if k else 0))) * 30 if walk is not None else 0
            hx_, hy_ = _limb(c, 0, -300 + bob, -ang, -ang + knee, 150, 130, 58, col, -1, cap='butt')
            # shoe
            c.drawPath(smooth([(hx_ - 34, hy_ - 4), (hx_ - 30, hy_ - 30), (hx_ + 20, hy_ - 26),
                               (hx_ + 52, hy_ - 6), (hx_ + 44, hy_ + 2), (hx_ - 30, hy_ + 2)]), P(sh))
        c.translate(0, bob + breathe * 0.3)
        a = arms or (7, 4, 7, 4)
        swing = 22 * math.sin(ph) if walk is not None else 0
        # back arm
        _limb(c, -4, -450, a[0] + swing, a[1] + swing + 10, 118, 92, 44, shade(top, 0.72), 1,
              end=shade(look.skin, 0.8), endr=22)
        body = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-58, -478, 58, -268), 30, 30)
        c.drawRRect(body, P(top))
        if look.shirt:
            c.drawPath(poly([(30, -470), (58, -440), (58, -280), (36, -272)]), P(look.shirt))
        rect(c, -58, -292, 58, -268, P(shade(top, 0.85)), r=10)
        rect(c, -14, -500, 14, -466, P(shade(look.skin, 0.85)))
        c.save()
        c.translate(0, -568)
        c.rotate(tilt)
        hturn = 0.95 if turn is None else turn
        draw_head(c, look, 84, hturn, expr, blink, eye, t, back=back, mouth=mouth)
        c.restore()
        if hands and hands[1]:
            a1, a2 = ik(4, -450, hands[1][0], hands[1][1], 118, 100, 1, bend=-1)
        else:
            a1, a2 = a[2] - swing, a[3] - swing + 12
        _limb(c, 4, -450, a1, a2, 118, 92, 46, top, 1, end=look.skin, endr=23, cuff=shade(top, 0.82))
    c.restore()
    if dim > 0:
        pass


def blink_at(t, seed=0, period=3.7):
    """0..1 blink amount, natural irregular blinking"""
    ph = (t + seed * 1.37) % (period + (seed % 3) * 0.6)
    return clamp(1 - abs(ph - 0.09) / 0.09) if ph < 0.18 else 0.0


# ---------------------------------------------------------------- crowd looks
PALETTE_TOP = ['#5a3d3a', '#3e4a5c', '#6b5a3a', '#3c5248', '#4a3a55', '#7a6a5a', '#2e3a4a', '#6a3a3a',
               '#556070', '#8a7650', '#3a3a3a', '#5e4b6b']
PALETTE_PANTS = ['#26304a', '#2a2a2e', '#4a4038', '#3a3f4a', '#1f2a36', '#5a5048']
SKINS = ['#e6b994', '#d2a57c', '#b98563', '#8f5e43', '#f0c8a5', '#c79775']
HAIRS = ['#1a1414', '#4a2e1c', '#7a5a3a', '#2a1c14', '#9a9a9a', '#b8864a', '#3a2418']
STYLES = ['short', 'short', 'long', 'bob', 'bun', 'bald', 'short', 'long']


def random_look(seed):
    r = random.Random(seed * 7919 + 3)
    st = r.choice(STYLES)
    hair = '#9c9c9c' if st == 'bald' else r.choice(HAIRS)
    return Look(skin=r.choice(SKINS), hair=hair, style=st, top=r.choice(PALETTE_TOP),
                pants=r.choice(PALETTE_PANTS), shoes=r.choice(['#2a2a2a', '#5a4a3a', '#cfcfcf', '#3a3a44']),
                glasses=r.random() < 0.2, seed=seed, width=r.uniform(0.92, 1.12), height=r.uniform(0.95, 1.12),
                shirt=r.choice([None, None, '#d8d0c0']))


# ---------------------------------------------------------------- thought FX
def rings(c, x, y, t, h='#8fd3ff', n=3, rmax=260, speed=0.6, a=0.6, w=5, r0=60):
    for i in range(n):
        ph = (t * speed + i / n) % 1.0
        r = r0 + ph * (rmax - r0)
        al = a * (1 - ph) * min(1, ph * 6)
        circle(c, x, y, r, P(h, al * 0.5, stroke=w * 3, blur=8))
        circle(c, x, y, r, P(h, al, stroke=w))


def wave_line(c, x, y, w, t, h='#9fd8ff', a=0.6, amp=14, freq=0.045, stroke=4):
    pts = []
    for i in range(0, int(w) + 1, 8):
        env = math.sin(math.pi * i / w)
        pts.append((x - w / 2 + i, y + math.sin(i * freq + t * 6) * amp * env))
    c.drawPath(poly(pts, close=False), P(h, a, stroke=stroke))


def cloud_path(x, y, rx, ry, seed=0):
    p = skia.Path()
    r = random.Random(seed)
    n = 7
    for i in range(n):
        a = 2 * math.pi * i / n
        px, py = x + math.cos(a) * rx * 0.72, y + math.sin(a) * ry * 0.62
        rr = (rx + ry) * 0.5 * r.uniform(0.38, 0.5)
        p.addCircle(px, py, rr)
    p.addOval(skia.Rect.MakeLTRB(x - rx * 0.8, y - ry * 0.7, x + rx * 0.8, y + ry * 0.7))
    return p


def bubble(c, x, y, size, t, appear=1.0, icon=None, from_=None, h='#eef6ff', a=0.92, seed=0, dark=False,
           glow='#8fd3ff', txt=None):
    """thought bubble; appear 0..1 scale-pop; from_=(x,y) head point for trail dots"""
    if appear <= 0:
        return
    sc = ease(appear) * (1 + 0.12 * math.sin(clamp(appear) * math.pi))
    fy = math.sin(t * 1.5 + seed) * 6
    layer(c, a * clamp(appear * 2))
    if from_:
        for k in range(3):
            f = (k + 1) / 4
            px, py = lerp(from_[0], x, f * 0.8), lerp(from_[1], y + size * 0.4, f * 0.8)
            circle(c, px, py + fy * f, size * (0.05 + 0.04 * k) * sc, P('#2a2a3a' if dark else h))
    c.save()
    c.translate(x, y + fy)
    c.scale(sc, sc)
    cp = cloud_path(0, 0, size, size * 0.72, seed)
    c.drawPath(cp, P(glow, 0.5, blur=18))
    c.drawPath(cp, P('#2a2a3a' if dark else h))
    if icon:
        draw_icon(c, icon, 0, 0, size * 0.55, t)
    if txt:
        lines_ = wrap(txt, size * 0.2, size * 1.5)
        for i, ln in enumerate(lines_):
            text(c, ln, 0, (i - (len(lines_) - 1) / 2) * size * 0.24 + size * 0.07, size * 0.2,
                 '#e8e8f0' if dark else '#2a2a35', tf=TF_MED)
    c.restore()
    c.restore()


def draw_icon(c, name, x, y, s, t=0):
    c.save()
    c.translate(x, y)
    k = s / 100.0
    c.scale(k, k)
    ink = '#2b2d3a'
    if name == 'house':
        c.drawPath(poly([(-60, -5), (0, -60), (60, -5)]), P('#c0504a'))
        rect(c, -45, -8, 45, 55, P('#e9d7b0'))
        rect(c, -12, 15, 12, 55, P('#6a4a36'))
        rect(c, 20, 5, 38, 23, P('#7ab0d6'))
    elif name == 'clock':
        circle(c, 0, 0, 58, P('#f4f1e8'))
        circle(c, 0, 0, 58, P(ink, stroke=8))
        a = t * 3
        line(c, 0, 0, math.sin(a) * 40, -math.cos(a) * 40, P(ink, stroke=7))
        line(c, 0, 0, 25, 8, P('#c0504a', stroke=7))
    elif name == 'exam':
        c.rotate(-8)
        rect(c, -45, -60, 45, 60, P('#fbfbf6'), r=6)
        for i in range(4):
            line(c, -30, -35 + i * 18, 25, -35 + i * 18, P('#9aa0b0', stroke=5))
        text(c, 'F', 22, 50, 56, '#d0443a', tf=TF_BLACK)
    elif name == 'heart':
        c.drawPath(smooth([(0, 50), (-55, 0), (-45, -40), (-12, -42), (0, -22), (12, -42), (45, -40), (55, 0)]),
                   P('#e0505a'))
    elif name == 'broken':
        c.drawPath(smooth([(0, 50), (-55, 0), (-45, -40), (-12, -42), (0, -22), (12, -42), (45, -40), (55, 0)]),
                   P('#7a2a35'))
        c.drawPath(poly([(0, -24), (-10, 0), (8, 12), (-4, 48)], close=False), P('#2a1a20', stroke=8))
    elif name == 'money':
        rect(c, -60, -35, 60, 35, P('#79a86a'), r=8)
        circle(c, 0, 0, 22, P('#5a8a4e'))
        text(c, '$', 0, 16, 44, '#e8f2df', tf=TF_BLACK)
    elif name == 'question':
        text(c, '?', 0, 40, 120, '#5a6bd6', tf=TF_BLACK)
    elif name == 'bolt':
        c.drawPath(poly([(10, -60), (-35, 8), (-2, 8), (-12, 60), (35, -10), (2, -10)]), P('#f0b43a'))
    elif name == 'eye':
        c.drawPath(smooth([(-60, 0), (0, -32), (60, 0), (0, 32)]), P('#f4f1e8'))
        circle(c, 0, 0, 22, P('#5a8ac0'))
        circle(c, 0, 0, 10, P(ink))
    elif name == 'scribble':
        pts = [(math.cos(i * 1.9) * (20 + i * 3.2) + math.sin(t * 9 + i) * 4, math.sin(i * 2.3) * (16 + i * 2.5))
               for i in range(14)]
        c.drawPath(smooth(pts, close=False), P('#d04040', stroke=8))
    elif name == 'speech':
        c.drawPath(smooth([(-55, -30), (55, -30), (60, 15), (10, 22), (-15, 50), (-12, 22), (-58, 15)]),
                   P('#f4f1e8'))
        for i in range(3):
            circle(c, -25 + i * 25, -4, 7, P(ink))
    elif name == 'cart':
        c.drawPath(poly([(-60, -40), (-42, -40), (-28, 25), (45, 25), (55, -20), (-36, -20)], close=False),
                   P(ink, stroke=8))
        circle(c, -20, 42, 10, P(ink))
        circle(c, 38, 42, 10, P(ink))
        rect(c, -25, -38, 0, -18, P('#d06a3a'))
        rect(c, 5, -45, 30, -18, P('#5a9a6a'))
    elif name == 'phone':
        rect(c, -32, -58, 32, 58, P(ink), r=10)
        rect(c, -25, -46, 25, 44, P('#7ab0d6'), r=4)
    elif name == 'food':
        oval(c, 0, -15, 55, 30, P('#d09a4a'))
        rect(c, -55, -8, 55, 6, P('#5a8a3a'), r=4)
        rect(c, -52, 4, 52, 18, P('#7a3a2a'), r=4)
        c.drawPath(smooth([(-55, 18), (55, 18), (50, 38), (-50, 38)]), P('#d09a4a'))
    elif name == 'zzz':
        text(c, 'Z', -20, 20, 60, '#5a6bd6', tf=TF_BLACK)
        text(c, 'z', 25, -5, 42, '#5a6bd6', tf=TF_BLACK)
    elif name == 'lock':
        rect(c, -40, -5, 40, 55, P('#d0a03a'), r=8)
        c.drawPath(poly([(-25, -5), (-25, -30), (25, -30), (25, -5)], close=False), P(ink, stroke=10))
    elif name == 'crack':
        c.drawPath(poly([(-50, -40), (-10, -5), (-30, 10), (20, 50)], close=False), P('#d04040', stroke=9))
    c.restore()


def particles(c, t, n=40, seed=3, area=(0, 0, W, H), h='#ffe9c0', a=0.5, size=3.0):
    r = random.Random(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        px = x0 + ((r.random() * (x1 - x0) + t * r.uniform(-12, 12)) % (x1 - x0))
        py = y0 + ((r.random() * (y1 - y0) - t * r.uniform(4, 18)) % (y1 - y0))
        al = a * (0.5 + 0.5 * math.sin(t * r.uniform(0.6, 1.6) + i))
        circle(c, px, py, size * r.uniform(0.5, 1.4), P(h, al))


def light_beam(c, pts, h='#fff1d0', a=0.18):
    c.drawPath(poly(pts), P(h, a, blur=24, blend=skia.BlendMode.kScreen))
