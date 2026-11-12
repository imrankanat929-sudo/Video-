"""Main character: teen, messy black hair, dark sweater, dark pants, grey sneakers, rust backpack.
All drawing in centimetre units, origin at feet centre (y up = negative)."""
import math
import skia
from gfx import paint, path_poly, path_smooth, ellipse, lin_grad, rad_grad, rgb, mix, lerp, clamp, noise1

SKIN = rgb('#d6a67a')
SKIN_SH = rgb('#b38058')
SKIN_HI = rgb('#e7bd94')
HAIR = rgb('#111114')
HAIR_HI = rgb('#2c2c33')
SWEAT = rgb('#2a2a31')
SWEAT_HI = rgb('#3a3a44')
SWEAT_SH = rgb('#1a1a1f')
PANTS = rgb('#1d1e24')
PANTS_SH = rgb('#141418')
SHOE = rgb('#b4b4b4')
SHOE_SOLE = rgb('#e8e8e8')
PACK = rgb('#8a4a2a')
PACK_SH = rgb('#5e3119')
PACK_HI = rgb('#a8613a')
STRAP = rgb('#3b2b22')
BUD = rgb('#f2f2f2')

EXPR = {
    'calm':      dict(brow_y=0, brow_tilt=0.0, eye_h=1.0, eye_close=0, mouth_open=0.0, mouth_curve=0.15, mouth_w=1.0, sweat=0, pupil=1.0),
    'surprised': dict(brow_y=-16, brow_tilt=0.05, eye_h=1.28, eye_close=0, mouth_open=0.65, mouth_curve=0.0, mouth_w=0.55, sweat=0, pupil=0.8),
    'fear':      dict(brow_y=-9, brow_tilt=0.42, eye_h=1.18, eye_close=0, mouth_open=0.3, mouth_curve=-0.5, mouth_w=0.9, sweat=1, pupil=0.75),
    'cautious':  dict(brow_y=5, brow_tilt=-0.18, eye_h=0.86, eye_close=0, mouth_open=0.0, mouth_curve=-0.12, mouth_w=0.8, sweat=0.4, pupil=1.0),
    'relief':    dict(brow_y=-5, brow_tilt=0.2, eye_h=1.0, eye_close=1, mouth_open=0.08, mouth_curve=0.55, mouth_w=1.0, sweat=0, pupil=1.0),
    'speak':     dict(brow_y=-2, brow_tilt=0.12, eye_h=0.95, eye_close=0, mouth_open=0.0, mouth_curve=0.0, mouth_w=0.85, sweat=0.3, pupil=1.0),
}


def expr_mix(a, b, t):
    A, B = EXPR[a] if isinstance(a, str) else a, EXPR[b] if isinstance(b, str) else b
    return {k: lerp(A[k], B[k], t) for k in A}


# ----------------------------------------------------------------------------------------------
# HEAD (radius 100 units, centre origin). turn: -1 (profile left) .. 0 front .. 1 (profile right)
# ----------------------------------------------------------------------------------------------
def _hair_path(turn, back=False, t=0.0):
    """Fluffy messy hair mass. Outline = lobed cloud over the top + jagged fringe over forehead."""
    pts = []
    if back:
        n = 22
        for i in range(n):
            a = math.pi * 2 * i / n - math.pi / 2
            r = (122 if i % 2 == 0 else 113) + 4 * math.sin(i * 1.3)
            x, y = math.cos(a) * r * 1.02, math.sin(a) * r * 0.98 - 6
            if y > 30:
                y = 30 + (y - 30) * 0.5 + (16 if i % 2 == 0 else 0)
            pts.append((x, y))
        return path_smooth(pts, tension=0.8)
    n = 15
    for i in range(n + 1):
        a = math.pi * 0.93 + math.pi * 1.14 * i / n
        r = (128 if i % 2 == 0 else 112) + 4 * math.sin(i * 2.1 + t * 1.5)
        pts.append((math.cos(a) * r * 1.03 + turn * 8, math.sin(a) * r - 6))
    # fringe right->left, tips hanging down over forehead, swept to one side
    k = 11
    for i in range(k + 1):
        u = i / k
        x = lerp(104, -104, u) + turn * 22
        if i % 2 == 0:
            y = -14 + 8 * math.sin(i * 1.9) + 10 * (1 - abs(u - 0.45) * 1.6)
            x -= 10
        else:
            y = -40 + 6 * math.sin(i)
        pts.append((x, y))
    return path_smooth(pts, tension=0.38)


def draw_head(c, ex, turn=0.0, look=(0, 0), talk=0.0, blink=0.0, t=0.0, earbuds=True, sweat_t=0.0, back=False):
    """ex = expression dict."""
    if back:
        c.drawOval(ellipse(0, 0, 100, 104), paint(SKIN_SH))
        hp = _hair_path(0, back=True)
        c.drawPath(hp, paint(HAIR))
        c.drawOval(ellipse(-30, -60, 50, 30), paint(HAIR_HI, 0.5, blur=12))
        # ears
        c.drawOval(ellipse(-104, 8, 14, 20), paint(SKIN_SH))
        c.drawOval(ellipse(104, 8, 14, 20), paint(SKIN_SH))
        if earbuds:
            c.drawCircle(-104, 12, 6, paint(BUD))
            c.drawCircle(104, 12, 6, paint(BUD))
        return
    # ears
    ex_off = turn * 60
    if turn < 0.85:
        c.drawOval(ellipse(-100 + ex_off * 0.3, 10, 16, 22), paint(SKIN_SH))
    if turn > -0.85:
        c.drawOval(ellipse(100 + ex_off * 0.3, 10, 16, 22), paint(SKIN_SH))
    # face
    face = skia.Path()
    face.addOval(ellipse(0, 0, 100, 102))
    sh = rad_grad((-30 + turn * 30, -30), 150, [SKIN_HI, SKIN, SKIN_SH], [0, 0.55, 1])
    c.drawPath(face, paint(shader=sh))
    # cheek blush
    c.drawOval(ellipse(-52 + ex_off, 42, 18, 10), paint('#d98a6a', 0.25, blur=6))
    c.drawOval(ellipse(52 + ex_off, 42, 18, 10), paint('#d98a6a', 0.25, blur=6))
    # eyes
    ex_h = ex['eye_h']
    close = clamp(max(ex['eye_close'], blink))
    for side in (-1, 1):
        sx = side * 34 * (1 - abs(turn) * 0.35) + ex_off + look[0] * 6
        sy = 12 + look[1] * 5
        if (turn > 0.7 and side < 0) or (turn < -0.7 and side > 0):
            continue
        ew, eh = 12.5, 19 * ex_h
        if close > 0.6:
            pth = skia.Path()
            if ex['eye_close'] > 0.5:  # happy/relief closed arc
                pth.moveTo(sx - 13, sy + 2)
                pth.quadTo(sx, sy - 10, sx + 13, sy + 2)
            else:
                pth.moveTo(sx - 13, sy + 2)
                pth.quadTo(sx, sy + 7, sx + 13, sy + 2)
            c.drawPath(pth, paint(HAIR, stroke=5.5))
        else:
            hh = eh * (1 - close)
            c.drawOval(ellipse(sx, sy, ew, hh), paint('#0d0d10'))
            pr = 4.2 * ex['pupil']
            c.drawCircle(sx - 3.5 + look[0] * 2, sy - hh * 0.45, pr, paint('#ffffff', 0.95))
            c.drawCircle(sx + 4, sy + hh * 0.35, pr * 0.45, paint('#ffffff', 0.6))
    # nose
    nx = ex_off * 1.05
    c.drawPath(path_smooth([(nx - 4, 30), (nx + 2, 38), (nx + 7, 33)], close=False), paint(SKIN_SH, stroke=3.5))
    # mouth
    mx, my = ex_off * 0.95, 62
    mo = clamp(ex['mouth_open'] + talk)
    mw = 20 * ex['mouth_w']
    curve = ex['mouth_curve']
    if mo > 0.06:
        p = skia.Path()
        if curve < -0.05:  # fearful open mouth: arched top, flat-ish bottom
            top = my - 8 + 14 * curve
            bot = my + 6 + 18 * mo
            p.moveTo(mx - mw, my + 4)
            p.cubicTo(mx - mw * 0.5, top, mx + mw * 0.5, top, mx + mw, my + 4)
            p.cubicTo(mx + mw * 0.7, bot, mx - mw * 0.7, bot, mx - mw, my + 4)
        else:
            top = my - 4 - 3 * curve
            bot = my + 26 * mo
            p.moveTo(mx - mw, my)
            p.cubicTo(mx - mw * 0.6, top - 6 * curve, mx + mw * 0.6, top - 6 * curve, mx + mw, my)
            p.cubicTo(mx + mw * 0.9, bot, mx - mw * 0.9, bot, mx - mw, my)
        p.close()
        c.drawPath(p, paint('#3b1a16'))
        b = p.getBounds()
        c.save()
        c.clipPath(p, doAntiAlias=True)
        c.drawOval(ellipse(mx, b.bottom() + 2, mw * 0.7, 10 * mo + 2), paint('#b4545a'))
        c.drawRect(skia.Rect.MakeLTRB(mx - mw, b.top() - 2, mx + mw, b.top() + 5), paint('#f3eee6'))
        c.restore()
    else:
        p = skia.Path()
        p.moveTo(mx - mw, my - 2 * curve)
        p.quadTo(mx, my + 10 * curve, mx + mw, my - 2 * curve)
        c.drawPath(p, paint('#5a2e22', stroke=4.5))
    # hair
    hp = _hair_path(turn, t=t)
    c.drawPath(hp, paint(HAIR))
    # hair strands highlights
    for i in range(7):
        x = -80 + i * 27 + turn * 15
        c.drawPath(path_smooth([(x, -100), (x + 8, -70), (x + 2, -40)], close=False), paint(HAIR_HI, 0.55, stroke=4))
    # side locks
    for side in (-1, 1):
        lp = path_poly([(side * 96, -40), (side * 112, 6), (side * 100, 2), (side * 106, 26), (side * 88, -10)])
        c.drawPath(lp, paint(HAIR))
    # brows
    for side in (-1, 1):
        if (turn > 0.7 and side < 0) or (turn < -0.7 and side > 0):
            continue
        bx = side * 36 * (1 - abs(turn) * 0.35) + ex_off
        by = -8 + ex['brow_y']
        tilt = ex['brow_tilt'] * side  # positive = inner end raised
        inner = (bx - side * 17, by - 12 * ex['brow_tilt'] * 1.4)
        outer = (bx + side * 17, by + 6 * ex['brow_tilt'])
        p = skia.Path()
        p.moveTo(*inner)
        p.quadTo(bx, by - 5, *outer)
        c.drawPath(p, paint(HAIR, stroke=9.5))
    if earbuds:
        if turn < 0.85:
            c.drawCircle(-100 + ex_off * 0.3, 16, 7, paint(BUD))
        if turn > -0.85:
            c.drawCircle(100 + ex_off * 0.3, 16, 7, paint(BUD))
    # sweat drop
    sw = ex['sweat']
    if sw > 0.05:
        sx = 92 + ex_off * 0.2
        sy = -22 + 30 * (sweat_t % 1.0)
        dp = skia.Path()
        dp.moveTo(sx, sy - 18)
        dp.cubicTo(sx + 12, sy - 2, sx + 10, sy + 10, sx, sy + 10)
        dp.cubicTo(sx - 10, sy + 10, sx - 12, sy - 2, sx, sy - 18)
        c.drawPath(dp, paint('#9fd3f2', sw * 0.95))
        c.drawCircle(sx - 3, sy + 2, 3, paint('#ffffff', sw * 0.8))


def draw_head_side(c, ex, look=0.0, t=0.0, earbuds=True, talk=0.0):
    """Profile facing right. radius 100."""
    c.drawOval(ellipse(0, 0, 98, 102), paint(SKIN))
    # nose bump + chin
    p = path_smooth([(82, -10), (104, 18), (92, 30), (90, 56), (70, 86), (30, 100), (0, 96)], close=False)
    c.drawPath(p, paint(SKIN, stroke=1))
    c.drawPath(path_poly([(70, -20), (104, 20), (90, 32), (92, 60), (60, 92), (20, 100), (0, 60)]), paint(SKIN))
    c.drawOval(ellipse(-6, 14, 16, 22), paint(SKIN_SH))  # ear
    if earbuds:
        c.drawCircle(-4, 18, 7, paint(BUD))
        c.drawLine(-4, 24, -14, 110, paint(BUD, 0.9, stroke=2.5))
    # eye
    ex_h = ex['eye_h']
    c.drawOval(ellipse(62 + look * 3, 6, 9, 18 * ex_h), paint('#0d0d10'))
    c.drawCircle(60, -2, 3.2, paint('#ffffff'))
    by = -22 + ex['brow_y']
    bp = skia.Path()
    bp.moveTo(46, by + 4 - ex['brow_tilt'] * 10)
    bp.quadTo(64, by - 6, 80, by + 2 + ex['brow_tilt'] * 6)
    c.drawPath(bp, paint(HAIR, stroke=8))
    mo = clamp(ex['mouth_open'] + talk)
    if mo > 0.06:
        c.drawOval(ellipse(82, 66, 8, 4 + 12 * mo), paint('#3b1a16'))
    else:
        c.drawLine(74, 66, 90, 64 - 6 * ex['mouth_curve'], paint('#5a2e22', stroke=4))
    # hair: mass covering back/top + fringe to the front
    pts = []
    for i in range(22):
        a = math.pi * 0.62 + math.pi * 1.25 * i / 21
        r = 110 + 10 * math.sin(i * 2.9 + 0.5)
        pts.append((math.cos(a) * r - 4, math.sin(a) * r - 6))
    pts += [(98, -36), (80, -28), (88, -10), (58, -26), (48, -6), (30, -30), (14, -8), (-10, -30), (-30, 30), (-60, 70), (-78, 60)]
    c.drawPath(path_poly(pts), paint(HAIR))
    for i in range(6):
        x = -60 + i * 26
        c.drawPath(path_smooth([(x - 10, -96), (x + 8, -70), (x + 18, -44)], close=False), paint(HAIR_HI, 0.5, stroke=4))


# ----------------------------------------------------------------------------------------------
# BODY
# ----------------------------------------------------------------------------------------------
def _limb(c, p0, p1, p2, w0, w1, w2, color):
    """Two-segment tapered limb hip->knee->ankle."""
    def perp(a, b, w):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        return (-dy / L * w, dx / L * w)
    n0 = perp(p0, p1, w0 / 2)
    n1a = perp(p0, p1, w1 / 2)
    n1b = perp(p1, p2, w1 / 2)
    n1 = ((n1a[0] + n1b[0]) / 2, (n1a[1] + n1b[1]) / 2)
    n2 = perp(p1, p2, w2 / 2)
    pts = [(p0[0] + n0[0], p0[1] + n0[1]), (p1[0] + n1[0], p1[1] + n1[1]), (p2[0] + n2[0], p2[1] + n2[1]),
           (p2[0] - n2[0], p2[1] - n2[1]), (p1[0] - n1[0], p1[1] - n1[1]), (p0[0] - n0[0], p0[1] - n0[1])]
    c.drawPath(path_smooth(pts, tension=0.25), paint(color))
    c.drawCircle(p1[0], p1[1], w1 / 2, paint(color))


def _leg_ik(hip, foot, L1=44, L2=44, bend=1):
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    d = min(math.hypot(dx, dy), L1 + L2 - 0.01)
    a = math.atan2(dy, dx)
    cosb = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d)
    b = math.acos(clamp(cosb, -1, 1))
    ka = a - b * bend
    knee = (hip[0] + math.cos(ka) * L1, hip[1] + math.sin(ka) * L1)
    return knee


def _shoe_side(c, x, y, ang=0.0, dirn=1):
    c.save()
    c.translate(x, y)
    c.rotate(math.degrees(ang))
    c.scale(dirn, 1)
    p = path_smooth([(-9, -9), (6, -11), (18, -5), (22, 1), (-10, 2)], tension=0.4)
    c.drawPath(p, paint(SHOE))
    c.drawRoundRect(skia.Rect.MakeLTRB(-11, -1, 23, 4), 2, 2, paint(SHOE_SOLE))
    c.drawLine(0, -9, 10, -6, paint('#8a8a8a', stroke=1.4))
    c.restore()


def walk_pose(phase, speed=1.0):
    """Return foot offsets etc for a side walk cycle. phase in cycles."""
    ph = phase * 2 * math.pi
    stride = 26 * speed
    out = {}
    for name, off in (('near', 0.0), ('far', math.pi)):
        p = ph + off
        x = math.cos(p) * stride
        lift = max(0.0, math.sin(p)) * 10 * speed
        out[name] = (x, -lift, -math.sin(p) * 0.25 * speed if lift > 0 else 0.0)
    out['bob'] = abs(math.sin(ph)) * 3.2 * speed
    out['arm'] = math.cos(ph) * 0.55 * speed
    return out


def draw_side(c, phase=0.0, speed=1.0, ex=None, t=0.0, look=0.0, standing=False, talk=0.0, lean=0.0, dirn=1):
    """Full body, side view facing right (dirn=-1 faces left). Origin at feet."""
    ex = ex or EXPR['calm']
    c.save()
    c.scale(dirn, 1)
    wp = walk_pose(phase, 0 if standing else speed)
    bob = wp['bob']
    hip = (0, -84 + bob)
    c.save()
    c.translate(0, 0)
    # far leg
    fx, fy, fa = wp['far']
    foot = (fx, -6 + fy)
    knee = _leg_ik(hip, foot)
    _limb(c, (hip[0] - 2, hip[1]), knee, foot, 18, 14, 12, PANTS_SH)
    _shoe_side(c, foot[0], foot[1] + 4, fa)
    # far arm
    sh = (6 + lean * 10, -138 + bob)
    aa = -wp['arm']
    el = (sh[0] + math.sin(aa) * 26, sh[1] + math.cos(aa) * 26)
    hd = (el[0] + math.sin(aa + 0.35) * 24, el[1] + math.cos(aa + 0.35) * 24)
    _limb(c, sh, el, hd, 13, 11, 10, SWEAT_SH)
    c.drawCircle(hd[0], hd[1] + 2, 6.5, paint(SKIN_SH))
    # backpack
    c.save()
    c.translate(-18 + lean * 8, -128 + bob)
    c.rotate(lean * 8)
    bp = path_smooth([(-24, -30), (4, -34), (8, 0), (6, 32), (-22, 34), (-28, 0)], tension=0.4)
    c.drawPath(bp, paint(PACK))
    c.drawPath(path_smooth([(-28, -4), (-22, -10), (-20, 20), (-30, 18)], tension=0.3), paint(PACK_SH))
    c.drawRoundRect(skia.Rect.MakeLTRB(-26, -36, 4, -22), 8, 8, paint(PACK_HI))
    c.drawLine(-18, -14, -18, 26, paint(PACK_SH, stroke=2.5))
    c.restore()
    # torso (sweater)
    torso = path_smooth([(-12 + lean * 10, -150 + bob), (14 + lean * 12, -152 + bob), (18 + lean * 6, -120 + bob),
                         (14, -86 + bob), (-14, -84 + bob), (-16 + lean * 4, -120 + bob)], tension=0.35)
    c.drawPath(torso, paint(SWEAT))
    c.drawPath(path_smooth([(10 + lean * 10, -146 + bob), (16 + lean * 6, -118 + bob), (12, -90 + bob)], close=False), paint(SWEAT_HI, 0.6, stroke=3))
    # strap
    c.drawLine(-4 + lean * 10, -150 + bob, 8 + lean * 6, -112 + bob, paint(STRAP, stroke=4))
    # near leg
    nx, ny, na = wp['near']
    foot = (nx, -6 + ny)
    knee = _leg_ik(hip, foot)
    _limb(c, hip, knee, foot, 20, 15, 12.5, PANTS)
    _shoe_side(c, foot[0], foot[1] + 4, na)
    # head
    c.save()
    c.translate(10 + lean * 16, -182 + bob)
    c.scale(0.3, 0.3)
    draw_head_side(c, ex, look=look, t=t, talk=talk)
    c.restore()
    # near arm
    aa = wp['arm']
    sh = (2 + lean * 10, -138 + bob)
    el = (sh[0] + math.sin(aa) * 26, sh[1] + math.cos(aa) * 26)
    hd = (el[0] + math.sin(aa + 0.35) * 24, el[1] + math.cos(aa + 0.35) * 24)
    _limb(c, sh, el, hd, 14, 12, 10, SWEAT)
    c.drawCircle(hd[0], hd[1] + 2, 6.8, paint(SKIN))
    c.restore()
    c.restore()


def draw_back(c, phase=0.0, speed=1.0, t=0.0, standing=False, head_turn=0.0, shoulder=0.0):
    """Full body seen from behind, walking away from camera. Origin feet centre."""
    ph = phase * 2 * math.pi
    sp = 0 if standing else speed
    bob = abs(math.sin(ph)) * 3 * sp
    sway = math.sin(ph) * 2.2 * sp
    c.save()
    c.translate(sway, 0)
    # legs (alternate lifting)
    for side, off in ((-1, 0), (1, math.pi)):
        lift = max(0.0, math.sin(ph + off)) * sp
        x = side * 10
        top = -84 + bob
        bottom = -6 - lift * 9
        knee_y = lerp(top, bottom, 0.5) - lift * 3
        _limb(c, (x, top), (x + side * 1, knee_y), (x, bottom), 19, 15, 13, PANTS if side < 0 else PANTS_SH)
        c.save()
        c.translate(x, bottom + 4)
        sc = 1 - lift * 0.25
        c.drawRoundRect(skia.Rect.MakeLTRB(-9, -8 * sc, 9, 4), 5, 5, paint(SHOE))
        c.drawRoundRect(skia.Rect.MakeLTRB(-9.5, 1, 9.5, 5), 2, 2, paint(SHOE_SOLE))
        c.restore()
    # arms
    for side, off in ((-1, math.pi), (1, 0)):
        sw = math.sin(ph + off) * 3 * sp
        x = side * 24
        _limb(c, (x, -144 + bob), (x + side * 3, -118 + bob - sw), (x + side * 2, -94 + bob - sw * 1.6), 13, 11, 10, SWEAT_SH)
        c.drawCircle(x + side * 2, -91 + bob - sw * 1.6, 6.5, paint(SKIN_SH))
    # torso
    torso = path_smooth([(-26, -150 + bob), (26, -150 + bob), (24, -110 + bob), (18, -84 + bob), (-18, -84 + bob), (-24, -110 + bob)], tension=0.35)
    c.drawPath(torso, paint(SWEAT))
    # head
    c.save()
    c.translate(head_turn * 6, -180 + bob)
    c.scale(0.3, 0.3)
    if abs(head_turn) > 0.35:
        c.scale(-1 if head_turn < 0 else 1, 1)
        draw_head_side(c, EXPR['calm'], t=t)
    else:
        draw_head(c, EXPR['calm'], back=True, t=t)
    c.restore()
    # backpack
    c.save()
    c.translate(0, -124 + bob)
    c.rotate(sway * 0.6)
    c.drawLine(-14, -26, -16, 12, paint(STRAP, stroke=5))
    c.drawLine(14, -26, 16, 12, paint(STRAP, stroke=5))
    body = path_smooth([(-22, -28), (22, -28), (25, 0), (23, 28), (-23, 28), (-25, 0)], tension=0.3)
    c.drawPath(body, paint(shader=lin_grad((0, -30), (0, 30), [PACK_HI, PACK, PACK_SH])))
    c.drawRoundRect(skia.Rect.MakeLTRB(-20, -34, 20, -14), 8, 8, paint(PACK_HI))
    c.drawRoundRect(skia.Rect.MakeLTRB(-15, 4, 15, 24), 5, 5, paint(PACK_SH))
    c.drawLine(-12, 6, 12, 6, paint('#c9a27a', stroke=1.6))
    c.drawRect(skia.Rect.MakeLTRB(-3, -16, 3, -6), paint('#2a1a12'))
    for s in (-1, 1):
        c.drawRoundRect(skia.Rect.MakeLTRB(s * 25 - 5, -6, s * 25 + 5, 20), 4, 4, paint(PACK_SH))
    c.restore()
    c.restore()


def draw_front(c, ex=None, t=0.0, step=0.0, talk=0.0, blink=0.0, look=(0, 0), arms_out=0.0, breathe=0.0, head_turn=0.0):
    """Full body front view. step: backward step cycle amount (phase)."""
    ex = ex or EXPR['calm']
    ph = step * 2 * math.pi
    sp = 1.0 if step else 0.0
    bob = abs(math.sin(ph)) * 2.5 * sp + math.sin(t * 2.2) * 0.8 * breathe
    for side, off in ((-1, 0), (1, math.pi)):
        lift = max(0.0, math.sin(ph + off)) * sp
        x = side * 11
        top = -84 + bob
        bottom = -6 - lift * 7
        _limb(c, (x, top), (x + side * 1.5, lerp(top, bottom, 0.5)), (x + side * 1, bottom), 19, 15, 13, PANTS)
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 10, bottom - 6, x + 10, bottom + 4), 5, 5, paint(SHOE))
        c.drawRoundRect(skia.Rect.MakeLTRB(x - 10.5, bottom + 1, x + 10.5, bottom + 5), 2, 2, paint(SHOE_SOLE))
    # backpack peeks around
    c.drawRoundRect(skia.Rect.MakeLTRB(-29, -152 + bob, 29, -100 + bob), 10, 10, paint(PACK_SH))
    torso = path_smooth([(-27, -152 + bob), (27, -152 + bob), (25, -110 + bob), (19, -84 + bob), (-19, -84 + bob), (-25, -110 + bob)], tension=0.35)
    c.drawPath(torso, paint(shader=lin_grad((0, -150), (0, -84), [SWEAT_HI, SWEAT, SWEAT_SH])))
    c.drawLine(-14, -150 + bob, -12, -112 + bob, paint(STRAP, stroke=5))
    c.drawLine(14, -150 + bob, 12, -112 + bob, paint(STRAP, stroke=5))
    c.drawPath(path_smooth([(-8, -152 + bob), (0, -146 + bob), (8, -152 + bob)], close=False), paint(SWEAT_SH, stroke=3))
    # arms
    for side in (-1, 1):
        x = side * 26
        ao = arms_out
        el = (x + side * (4 + ao * 10), -118 + bob)
        hd = (x + side * (3 + ao * 18), -92 + bob - ao * 8)
        _limb(c, (x, -146 + bob), el, hd, 13, 11, 10, SWEAT)
        c.drawCircle(hd[0], hd[1] + 2, 6.8, paint(SKIN))
    c.save()
    c.translate(head_turn * 4, -181 + bob)
    c.scale(0.3, 0.3)
    draw_head(c, ex, turn=head_turn, talk=talk, blink=blink, look=look, t=t, sweat_t=t * 0.7)
    c.restore()


def draw_bust(c, ex, turn=0.0, look=(0, 0), talk=0.0, blink=0.0, t=0.0, breathe=1.0, shake=0.0):
    """Close-up: head + shoulders. Head radius 100 at origin; shoulders below."""
    br = math.sin(t * 2.4) * 3 * breathe
    # shoulders / sweater
    sh = path_poly([(-215, 1200), (-205, 300), (-185, 200 + br), (-110, 146 + br), (-40, 120), (40, 120), (110, 146 + br), (185, 200 + br), (205, 300), (215, 1200)])
    c.drawPath(sh, paint(shader=lin_grad((0, 120), (0, 600), [SWEAT_HI, SWEAT, SWEAT_SH])))
    # straps
    for s in (-1, 1):
        c.drawPath(path_smooth([(s * 70, 128 + br), (s * 92, 220 + br), (s * 100, 420), (s * 104, 1200)], close=False), paint(STRAP, stroke=24))
        c.drawPath(path_smooth([(s * 70, 128 + br), (s * 92, 220 + br), (s * 100, 420), (s * 104, 1200)], close=False), paint('#4d3a2e', stroke=4))
    # neck
    c.drawRect(skia.Rect.MakeLTRB(-26 + turn * 10, 70, 26 + turn * 10, 128), paint(SKIN_SH))
    c.drawPath(path_smooth([(-44, 122), (0, 140), (44, 122)], close=False), paint(SWEAT_SH, stroke=10))
    # earbud cable
    c.drawPath(path_smooth([(-98 + turn * 18, 26), (-80, 110), (-54, 180), (-40, 260)], close=False), paint(BUD, 0.85, stroke=2.4))
    c.save()
    c.translate(shake * math.sin(t * 60) * 1.2, 0)
    draw_head(c, ex, turn=turn, look=look, talk=talk, blink=blink, t=t, sweat_t=t * 0.6)
    c.restore()
