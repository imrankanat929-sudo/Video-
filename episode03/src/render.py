"""HUMAN MIND — Episode 03 renderer (skia).

usage:
  python3 render.py video <lang> [workers]      -> output/frames_<lang>.mp4 (silent)
  python3 render.py stills <lang> t1 t2 ...      -> scratch PNGs for review
"""
import json, math, os, random, subprocess, sys
import numpy as np
import skia

sys.path.insert(0, os.path.dirname(__file__))
from script import DURATION, FPS, TEXT, KEYWORDS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080
FLOOR = 850.0
FONT_DIR = "/usr/share/fonts/opentype/inter"

# ----------------------------------------------------------------- utilities

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, u):
    return a + (b - a) * u

def seg(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def smooth(u):
    u = clamp(u); return u * u * (3 - 2 * u)

def ease_io(u):
    u = clamp(u); return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2

def ease_out(u):
    u = clamp(u); return 1 - (1 - u) ** 3

def ease_in(u):
    u = clamp(u); return u ** 3

def window(t, a, b, fi=0.4, fo=0.4):
    """0→1→0 envelope over [a,b]."""
    if t <= a or t >= b: return 0.0
    return smooth(seg(t, a, a + fi)) * (1 - smooth(seg(t, b - fo, b)))

def col(a=1.0, v=1.0):
    return skia.Color4f(v, v, v, clamp(a))

def fill(a=1.0, v=1.0):
    return skia.Paint(AntiAlias=True, Color=col(a, v))

def stroke(w, a=1.0, v=1.0, dash=None, cap=True):
    p = skia.Paint(AntiAlias=True, Color=col(a, v), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    if cap:
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    return p

def walk_x(t, t0, t1, x0, x1, acc=0.4, dec=0.6):
    """Position with constant speed, quadratic accel/decel. Returns (x, speed>0)."""
    T = t1 - t0
    v = (x1 - x0) / (T - acc / 2 - dec / 2)
    if t <= t0: return x0, False
    if t >= t1: return x1, False
    s = t - t0
    if s < acc:
        d = v * s * s / (2 * acc)
    elif s < T - dec:
        d = v * acc / 2 + v * (s - acc)
    else:
        r = T - s
        d = (x1 - x0) - v * r * r / (2 * dec)
    return x0 + d, True

# ----------------------------------------------------------------- fonts / text
_tf = {}
def typeface(weight):
    if weight not in _tf:
        _tf[weight] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, f"Inter-{weight}.otf"))
    return _tf[weight]

def text_width(s, size, weight="SemiBold", track=0.0):
    f = skia.Font(typeface(weight), size)
    return sum(f.measureText(ch) for ch in s) + track * size * max(len(s) - 1, 0)

def draw_text(c, s, x, y, size, a=1.0, weight="SemiBold", track=0.0, align="center", v=1.0, paint=None):
    """Draw tracked text; y is the baseline-centre (cap height centred on y)."""
    f = skia.Font(typeface(weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    wdt = text_width(s, size, weight, track)
    if align == "center": x -= wdt / 2
    elif align == "right": x -= wdt
    p = paint or fill(a, v)
    base = y + size * 0.36
    for ch in s:
        c.drawString(ch, x, base, f, p)
        x += f.measureText(ch) + track * size
    return wdt

def pill(c, s, cx, cy, size=26, a=1.0, track=0.16, pad=(26, 14), weight="SemiBold", dark=0.07):
    if a <= 0.003: return
    w = text_width(s, size, weight, track)
    hgt = size + pad[1] * 2
    r = skia.Rect(cx - w / 2 - pad[0], cy - hgt / 2, cx + w / 2 + pad[0], cy + hgt / 2)
    c.drawRRect(skia.RRect.MakeRectXY(r, hgt / 2, hgt / 2), fill(a))
    draw_text(c, s, cx, cy, size, a=a, weight=weight, track=track, v=dark)

# ----------------------------------------------------------------- character

def body_path():
    p = skia.Path()
    rr = skia.RRect()
    rr.setRectRadii(skia.Rect(-55, -128, 55, 0),
                    [skia.Point(50, 50), skia.Point(50, 50), skia.Point(4, 4), skia.Point(4, 4)])
    p.addRRect(rr)
    return p
BODY = body_path()
HEAD_R = 34.0
HEAD_Y = -128 - 14 - HEAD_R  # head centre relative to floor


def draw_man(c, x, y, s=1.0, facing=1, bob=0.0, lean=0.0, arm=None, look=(0.6, 0.0),
             a=1.0, outline=False, eyes=0.0, head_fill=1.0, head_tilt=0.0):
    """Stickman in the HUMAN MIND style: filled bust, round head, pill arm.
    arm: angle in degrees (0 = straight forward, -30 = up-forward) or None (rest)."""
    if a <= 0.003: return
    c.save()
    c.translate(x, y - bob)
    c.scale(s, s)
    c.rotate(lean * facing)
    pa = fill(a) if not outline else stroke(4, a)
    # arm (behind body when resting)
    if arm is not None:
        ang = math.radians(arm)
        sx, sy = facing * 26, -96
        ex, ey = sx + facing * math.cos(ang) * 74, sy + math.sin(ang) * 74
        ap = stroke(24, a) if not outline else stroke(4, a)
        if outline:
            # outline arm: draw capsule outline
            path = skia.Path(); path.moveTo(sx, sy); path.lineTo(ex, ey)
            c.drawPath(path, stroke(24, a))
            c.drawPath(path, stroke(16, 1.0, v=0.0))
        else:
            c.drawLine(sx, sy, ex, ey, ap)
    if outline:
        c.drawPath(BODY, fill(1.0, 0.03))
    c.drawPath(BODY, pa)
    # head
    c.save()
    c.translate(0, HEAD_Y)
    c.rotate(head_tilt * facing)
    if outline:
        c.drawCircle(0, 0, HEAD_R, fill(1.0, 0.03)); c.drawCircle(0, 0, HEAD_R, stroke(4, a))
    else:
        if head_fill < 1.0:
            c.drawCircle(0, 0, HEAD_R, fill(1.0, 0.02))
            c.drawCircle(0, 0, HEAD_R, stroke(2.5 / max(s, 1e-3) * 1.0 + 0.6, a))
        c.drawCircle(0, 0, HEAD_R, fill(a * head_fill))
    if eyes > 0.01 and head_fill > 0.5:
        lx, ly = look
        lx *= facing
        sep = HEAD_R * 0.30 * (1 - min(1, abs(lx)))
        ex = lx * HEAD_R * 0.52
        eyy = ly * HEAD_R * 0.35 - 2
        ep = fill(eyes * a, 0.05)
        c.drawCircle(ex - sep, eyy, 4.2, ep)
        if sep > 1.0: c.drawCircle(ex + sep, eyy, 4.2, ep)
    c.restore()
    c.restore()


def speech_bubble(c, x, y, t, a=1.0, ghost=0.0):
    if a <= 0.003: return
    for k, (dx, dy, ga) in enumerate([(0, 0, 1.0), (22, -14, ghost * 0.45), (44, -28, ghost * 0.2)]):
        aa = a * ga
        if aa <= 0.003: continue
        r = skia.Rect(x - 52 + dx, y - 28 + dy, x + 52 + dx, y + 28 + dy)
        c.drawRRect(skia.RRect.MakeRectXY(r, 28, 28), fill(aa))
        tail = skia.Path(); tail.moveTo(x - 20 + dx, y + 22 + dy); tail.lineTo(x - 30 + dx, y + 44 + dy); tail.lineTo(x - 2 + dx, y + 24 + dy); tail.close()
        c.drawPath(tail, fill(aa))
        for i in range(3):
            ph = math.sin(t * 7 - i * 0.9)
            c.drawCircle(x - 24 + i * 24 + dx, y + dy - 3 * max(0, ph), 6.5, fill(aa * (0.55 + 0.45 * max(0, ph)), 0.08))


# ----------------------------------------------------------------- street
P = 560.0          # facade module width
ROOF = 250.0

def lamp_light(c, lx, ly, a):
    # cone of light to the floor
    path = skia.Path()
    path.moveTo(lx - 16, ly + 8); path.lineTo(lx + 16, ly + 8)
    path.lineTo(lx + 150, FLOOR); path.lineTo(lx - 150, FLOOR); path.close()
    sh = skia.GradientShader.MakeLinear([skia.Point(lx, ly), skia.Point(lx, FLOOR)],
                                        [skia.Color4f(1, 1, 1, 0.16 * a).toColor(), skia.Color4f(1, 1, 1, 0.0).toColor()])
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    c.drawPath(path, p)
    # pool on the floor
    c.save(); c.scale(1, 0.12)
    sh2 = skia.GradientShader.MakeRadial(skia.Point(lx, FLOOR / 0.12), 170,
                                         [skia.Color4f(1, 1, 1, 0.18 * a).toColor(), skia.Color4f(1, 1, 1, 0).toColor()])
    p2 = skia.Paint(AntiAlias=True); p2.setShader(sh2)
    c.drawCircle(lx, FLOOR / 0.12, 170, p2)
    c.restore()
    c.drawCircle(lx, ly + 4, 9, fill(a))


def facade(c, x0, a, hero_x=None, echo=0.0):
    """One identical street module starting at x0."""
    la = 0.75 * a
    # pilasters
    c.drawLine(x0, ROOF, x0, FLOOR, stroke(2, 0.22 * a))
    # cornice
    c.drawLine(x0, ROOF, x0 + P, ROOF, stroke(3, 0.55 * a))
    c.drawLine(x0, ROOF + 16, x0 + P, ROOF + 16, stroke(1.5, 0.25 * a))
    # proximity highlight when the hero passes the door
    near = 0.0
    if hero_x is not None:
        near = math.exp(-((hero_x - (x0 + 150)) / 170) ** 2)
    # arched door
    dx0, dx1, dtop = x0 + 90, x0 + 210, 600
    door = skia.Path()
    door.moveTo(dx0, FLOOR); door.lineTo(dx0, dtop + 60)
    door.arcTo(skia.Rect(dx0, dtop, dx1, dtop + 120), 180, 180, False)
    door.lineTo(dx1, FLOOR)
    c.drawPath(door, stroke(3.2, (0.8 + 0.2 * near) * a))
    inner = skia.Path(); inner.addRRect(skia.RRect.MakeRectXY(skia.Rect(dx0 + 16, dtop + 70, dx1 - 16, FLOOR - 20), 6, 6))
    c.drawPath(inner, stroke(1.6, 0.25 * a))
    c.drawCircle(dx1 - 22, 745, 5, fill((0.8 + 0.2 * near) * a))
    c.drawLine(dx0 - 18, FLOOR - 2, dx1 + 18, FLOOR - 2, stroke(3, 0.4 * a))
    # transom glow above the door
    c.drawCircle((dx0 + dx1) / 2, dtop + 36, 10, fill(0.25 * a + 0.4 * near * a))
    # windows
    for (wx, wy, ww, wh, lit) in [(x0 + 290, 380, 120, 150, True), (x0 + 95, 330, 110, 130, False), (x0 + 290, 610, 120, 120, False)]:
        r = skia.Rect(wx, wy, wx + ww, wy + wh)
        if lit:
            c.drawRect(r, fill(0.07 * a))
        c.drawRRect(skia.RRect.MakeRectXY(r, 4, 4), stroke(2.6, la))
        c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, stroke(1.6, 0.45 * a))
        c.drawLine(wx, wy + wh * 0.45, wx + ww, wy + wh * 0.45, stroke(1.6, 0.45 * a))
        c.drawLine(wx - 8, wy + wh + 6, wx + ww + 8, wy + wh + 6, stroke(2.4, 0.5 * a))
    # street lamp at the module edge
    lx = x0 + P - 40
    c.drawLine(x0 + P - 10, FLOOR, x0 + P - 10, 360, stroke(5, 0.7 * a))
    arm = skia.Path(); arm.moveTo(x0 + P - 10, 362); arm.quadTo(x0 + P - 10, 330, lx, 336)
    c.drawPath(arm, stroke(4, 0.7 * a))
    shade = skia.Path(); shade.moveTo(lx - 20, 352); shade.lineTo(lx - 10, 334); shade.lineTo(lx + 10, 334); shade.lineTo(lx + 20, 352); shade.close()
    c.drawPath(shade, fill(0.85 * a))
    lamp_light(c, lx, 352, a)


def street(c, cam_l, cam_r, a, hero_x=None, echo=0.0, t=0.0):
    if a <= 0.003: return
    i0 = int(math.floor((cam_l - P) / P)); i1 = int(math.ceil((cam_r + P) / P))
    for i in range(i0, i1 + 1):
        facade(c, i * P, a, hero_x)
    if echo > 0.003:
        # double exposure: the street slipping against itself
        off = 26 + 10 * math.sin(t * 2.1)
        for k, ea in ((1, echo * 0.35), (2, echo * 0.15)):
            c.save(); c.translate(off * k, -6 * k)
            for i in range(i0, i1 + 1):
                facade(c, i * P, ea, None)
            c.restore()
    # sidewalk dashed line (as in the reference)
    c.drawLine(cam_l - 200, FLOOR, cam_r + 200, FLOOR, stroke(3, 0.6 * a, dash=[22, 14], cap=False))


def skyline(c, cam_x, zoom, a):
    """Far layer, parallax 0.5, very faint."""
    if a <= 0.003: return
    rnd = random.Random(7)
    blds = []
    x = -4000
    while x < 9000:
        w = rnd.uniform(120, 260); h = rnd.uniform(60, 180)
        blds.append((x, w, h)); x += w + rnd.uniform(0, 30)
    path = skia.Path()
    started = False
    for (x, w, h) in blds:
        y = ROOF - 10 - h * 0.6
        if not started:
            path.moveTo(x, ROOF); started = True
        path.lineTo(x, y); path.lineTo(x + w, y); path.lineTo(x + w, ROOF)
    c.drawPath(path, stroke(1.6, 0.13 * a))


# ----------------------------------------------------------------- icons / memory cards

def card(c, cx, cy, w, h, a, kind, t, s=1.0, dashed=False, bright=0.0):
    if a <= 0.003: return
    c.save(); c.translate(cx, cy); c.scale(s, s)
    r = skia.Rect(-w / 2, -h / 2, w / 2, h / 2)
    rr = skia.RRect.MakeRectXY(r, 18, 18)
    c.drawRRect(rr, fill(0.96 * a, 0.035))
    c.drawRRect(rr, stroke(3.2, a * (0.9 + 0.1 * bright), dash=[14, 10] if dashed else None))
    if bright > 0:
        c.drawRRect(rr, stroke(8, 0.35 * bright * a))
    c.save(); c.clipRRect(rr, True)
    icon(c, kind, w, h, a * (0.45 if dashed else 1.0), t)
    c.restore(); c.restore()


def icon(c, kind, w, h, a, t, variant=0):
    k = min(w, h) / 200.0
    if kind == "room" or kind == "room_b":
        variant = 1 if kind == "room_b" else 0
        # simple one-point perspective room
        bw, bh = w * 0.42, h * 0.42
        back = skia.Rect(-bw / 2, -bh / 2 - h * 0.04, bw / 2, bh / 2 - h * 0.04)
        c.drawRect(back, stroke(2.4, 0.75 * a))
        for (x1, y1, x2, y2) in [(back.left(), back.top(), -w / 2, -h / 2), (back.right(), back.top(), w / 2, -h / 2),
                                 (back.left(), back.bottom(), -w / 2, h / 2), (back.right(), back.bottom(), w / 2, h / 2)]:
            c.drawLine(x1, y1, x2, y2, stroke(2.0, 0.5 * a))
        # window on back wall
        wx = -bw * 0.32 if variant == 0 else -bw * 0.22
        ww = bw * 0.3
        c.drawRect(skia.Rect(wx - ww / 2, back.top() + bh * 0.18, wx + ww / 2, back.top() + bh * 0.55), stroke(2.0, 0.9 * a))
        c.drawRect(skia.Rect(wx - ww / 2, back.top() + bh * 0.18, wx + ww / 2, back.top() + bh * 0.55), fill(0.12 * a))
        # door on back wall
        dx = bw * 0.24
        c.drawRect(skia.Rect(dx - bw * 0.1, back.top() + bh * 0.3, dx + bw * 0.1, back.bottom()), stroke(2.0, 0.9 * a))
        # lamp
        lx = 0 if variant == 0 else bw * 0.05
        c.drawLine(lx, -h / 2, lx, -h / 2 + h * 0.14, stroke(1.6, 0.6 * a))
        c.drawCircle(lx, -h / 2 + h * 0.16, 5 * k + 2, fill(a))
        if variant == 1:  # a plant: the small difference
            px = -bw * 0.75; py = h * 0.33
            c.drawLine(px, py, px, py - 24 * k, stroke(2, 0.8 * a))
            c.drawCircle(px - 6 * k, py - 28 * k, 7 * k, stroke(2, 0.8 * a))
            c.drawCircle(px + 7 * k, py - 32 * k, 7 * k, stroke(2, 0.8 * a))
    elif kind == "door":
        dw, dh = 70 * k, 120 * k
        c.drawRect(skia.Rect(-dw / 2, -dh / 2 + 6, dw / 2, dh / 2 + 6), stroke(3, 0.5 * a))
        ajar = 0.35 + 0.1 * math.sin(t * 0.8)
        door = skia.Path()
        door.moveTo(-dw / 2, -dh / 2 + 6); door.lineTo(-dw / 2 + dw * (1 - ajar), -dh / 2 - 6)
        door.lineTo(-dw / 2 + dw * (1 - ajar), dh / 2 + 18); door.lineTo(-dw / 2, dh / 2 + 6); door.close()
        c.drawPath(door, fill(0.05 * a)); c.drawPath(door, stroke(3, a))
        c.drawRect(skia.Rect(-dw / 2 + dw * (1 - ajar), -dh / 2 + 6, dw / 2, dh / 2 + 6), fill(0.35 * a))
        c.drawLine(-w / 2, dh / 2 + 18, w / 2, dh / 2 + 18, stroke(2, 0.4 * a))
    elif kind == "window":
        ww = 110 * k
        r = skia.Rect(-ww / 2, -ww / 2, ww / 2, ww / 2)
        c.drawRect(r, fill(0.12 * a)); c.drawRect(r, stroke(3, a))
        c.drawLine(0, -ww / 2, 0, ww / 2, stroke(2, 0.8 * a)); c.drawLine(-ww / 2, 0, ww / 2, 0, stroke(2, 0.8 * a))
        for i in range(4):
            yy = ww / 2 + 12 + i * 10
            c.drawLine(-ww / 2 - 10 - i * 12, yy, ww / 2 + 10 + i * 12, yy, stroke(1.4, (0.25 - i * 0.05) * a))
    elif kind == "person":
        # a stranger walking past
        c.drawLine(-w / 2, h * 0.3, w / 2, h * 0.3, stroke(2, 0.4 * a, dash=[10, 7], cap=False))
        px = -w * 0.6 + ((t * 70) % (w * 1.2))
        draw_man(c, px, h * 0.3, s=0.5 * k * 1.6, facing=1, bob=3 * abs(math.sin(t * 6)), arm=None, a=a)
    elif kind == "shape":
        c.drawCircle(-30 * k, 0, 26 * k, stroke(3, a))
        tri = skia.Path(); tri.moveTo(25 * k, -26 * k); tri.lineTo(52 * k, 22 * k); tri.lineTo(-2 * k, 22 * k); tri.close()
        c.drawPath(tri, stroke(3, a))
    elif kind == "face":
        c.drawCircle(0, 0, 40 * k, stroke(3, a))
        c.drawCircle(-14 * k, -8 * k, 4 * k, fill(a)); c.drawCircle(14 * k, -8 * k, 4 * k, fill(a))
        m = skia.Path(); m.moveTo(-14 * k, 14 * k); m.quadTo(0, 24 * k, 14 * k, 14 * k)
        c.drawPath(m, stroke(3, a))
    elif kind == "place":
        hp = skia.Path(); hp.moveTo(-40 * k, 30 * k); hp.lineTo(-40 * k, -6 * k); hp.lineTo(0, -38 * k)
        hp.lineTo(40 * k, -6 * k); hp.lineTo(40 * k, 30 * k); hp.close()
        c.drawPath(hp, stroke(3, a))
        c.drawRect(skia.Rect(-10 * k, 6 * k, 10 * k, 30 * k), stroke(2.5, a))
    elif kind == "sound":
        c.drawCircle(-30 * k, 0, 7 * k, fill(a))
        for i in range(3):
            r = (18 + i * 16) * k
            arc = skia.Path(); arc.addArc(skia.Rect(-30 * k - r, -r, -30 * k + r, r), -45, 90)
            c.drawPath(arc, stroke(3, a * (1 - i * 0.22)))


def floating_icon(c, kind, x, y, s, a, t):
    if a <= 0.003: return
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, 0, 54, fill(0.95 * a, 0.04)); c.drawCircle(0, 0, 54, stroke(3, a))
    icon(c, kind, 150, 150, a, t)
    c.restore()


# ----------------------------------------------------------------- brain
def brain_paths():
    outer = None
    for (x, y, r) in [(-150, 10, 95), (-95, -70, 110), (10, -100, 115), (115, -70, 105), (175, 10, 85),
                      (95, 60, 100), (-10, 70, 100), (-120, 70, 85)]:
        p = skia.Path(); p.addCircle(x, y, r)
        outer = p if outer is None else skia.Op(outer, p, skia.PathOp.kUnion_PathOp)
    cere = skia.Path(); cere.addOval(skia.Rect(80, 95, 210, 175))
    stem = skia.Path(); stem.addRRect(skia.RRect.MakeRectXY(skia.Rect(30, 130, 80, 205), 24, 24))
    outer = skia.Op(outer, cere, skia.PathOp.kUnion_PathOp)
    outer = skia.Op(outer, stem, skia.PathOp.kUnion_PathOp)
    inner = []
    def cub(*pts):
        p = skia.Path(); p.moveTo(*pts[0])
        for i in range(1, len(pts), 3): p.cubicTo(*pts[i], *pts[i + 1], *pts[i + 2])
        inner.append(p)
    cub((-40, -200), (-10, -150), (-60, -110), (-20, -60), (20, -10), (-30, 30), (10, 90))
    cub((-200, -20), (-150, -40), (-120, 10), (-80, -10))
    cub((-150, -110), (-110, -80), (-90, -140), (-60, -110))
    cub((60, -170), (80, -120), (40, -100), (80, -60))
    cub((120, -120), (150, -90), (190, -100), (200, -50))
    cub((50, 0), (90, -20), (110, 30), (160, 20))
    cub((-120, 70), (-80, 40), (-60, 100), (-20, 80))
    cub((40, 60), (60, 100), (100, 80), (110, 120))
    cub((100, 120), (130, 130), (160, 120), (190, 140))
    return outer, inner
BRAIN_OUT, BRAIN_IN = brain_paths()


def draw_partial(c, path, u, paint):
    if u <= 0: return
    if u >= 1: c.drawPath(path, paint); return
    pm = skia.PathMeasure(path, False)
    while True:
        L = pm.getLength(); dst = skia.Path()
        if L > 0 and pm.getSegment(0, L * u, dst, True):
            c.drawPath(dst, paint)
        if not pm.nextContour():
            break


def draw_brain(c, cx, cy, s, a, draw_u, pulse, t):
    if a <= 0.003: return
    c.save(); c.translate(cx, cy); c.scale(s, s)
    if draw_u >= 1:
        c.drawPath(BRAIN_OUT, fill(0.9 * a, 0.03))
    draw_partial(c, BRAIN_OUT, draw_u, stroke(4.5 / max(s, .3) ** 0.3, a))
    for i, p in enumerate(BRAIN_IN):
        draw_partial(c, p, clamp(draw_u * 1.3 - 0.3 - i * 0.03), stroke(3, 0.55 * a))
    if pulse > 0.003:
        sc = 1 + 0.12 * (1 - pulse)
        c.save(); c.scale(sc, sc)
        c.drawPath(BRAIN_OUT, stroke(6, 0.6 * pulse * a)); c.restore()
        # synapse sparkles
        rnd = random.Random(int(t * 4))
        for i in range(10):
            x = rnd.uniform(-170, 190); y = rnd.uniform(-160, 120)
            if BRAIN_OUT.contains(x, y):
                c.drawCircle(x, y, 4, fill(pulse * a))
    c.restore()


# ----------------------------------------------------------------- timeline helpers
T = {}  # filled from timing json


def word_times(timing, lid):
    for l in timing:
        if l["id"] == lid: return l["words"]
    return []


# ======================================================================
#                              SCENES
# ======================================================================
MOVE_A = 3.6  # duration of the signature push-in


def move_a(u, base=(900.0, 540.0, 1.0)):
    """Signature camera move: push in to the hero's face (used 3 times)."""
    e = ease_io(u)
    cx = lerp(base[0], 960.0, e)
    cy = lerp(base[1], FLOOR + HEAD_Y + 6, e)
    z = lerp(base[2], 2.45, e)
    return cx, cy, z


def move_a_look(u):
    # slow head turn towards camera
    k = smooth(seg(u, 0.38, 0.86))
    return (lerp(0.75, 0.0, k), lerp(0.0, -0.05, k))


def opening_state(t):
    """Scene 1 state at time t (also used for the replay). Returns dict."""
    st = {}
    # hero walk
    hx, hw = walk_x(t, 0.0, 4.4, 560, 960, acc=0.01, dec=0.7)
    st["hx"], st["hwalk"] = hx, hw
    # friend (outline) slightly behind
    fx, fw = walk_x(t, 0.0, 4.9, 360, 790, acc=0.01, dec=0.6)
    st["fx"], st["fwalk"] = fx, fw
    # looks
    look = (0.75, 0.0)
    if 6.1 <= t < 10.6:
        k1 = smooth(seg(t, 6.1, 6.8)); k2 = smooth(seg(t, 7.6, 8.3)); k3 = smooth(seg(t, 9.6, 10.3))
        lx = lerp(lerp(lerp(0.75, 0.9, k1), -1.0, k2), 0.75, k3)
        ly = lerp(lerp(lerp(0.0, -0.7, k1), -0.1, k2), 0.0, k3)
        look = (lx, ly)
    st["facing"] = 1 if look[0] >= 0 else -1
    st["look"] = (abs(look[0]) * 1.0, look[1])
    st["head_tilt"] = -8 * smooth(seg(t, 6.1, 6.8)) * (1 - smooth(seg(t, 7.6, 8.3)))
    # camera
    if t < 5.0:
        e = ease_io(seg(t, 0, 5.0))
        cam = (lerp(720, 900, e), 540, lerp(1.12, 1.0, e))
    elif t < 11.0:
        pan = math.sin(math.pi * smooth(seg(t, 6.0, 10.7)))
        cam = (900 + 120 * pan, 540 - 20 * pan, 1.0)
    elif t < 11.0 + MOVE_A:
        u = seg(t, 11.0, 11.0 + MOVE_A)
        cam = move_a(u)
        st["look"] = move_a_look(u); st["facing"] = 1
    else:
        cx, cy, z = move_a(1.0)
        cam = (cx, cy, z + 0.03 * (t - 11.0 - MOVE_A))
        st["look"] = move_a_look(1.0); st["facing"] = 1
    st["cam"] = cam
    # friend's speech bubble
    st["bubble"] = window(t, 0.7, 3.6, 0.3, 0.4) + window(t, 7.9, 10.2, 0.25, 0.4)
    st["bubble_ghost"] = smooth(seg(t, 8.4, 9.0))
    st["ghost_echo"] = window(t, 5.9, 7.6, 0.2, 1.0)
    return st


class Frame:
    def __init__(self, lang, timing):
        self.lang = lang
        self.tx = TEXT[lang]
        self.timing = timing
        self.subs = build_subs(timing, lang)
        b1 = word_times(timing, "b1")
        self.item_times = [w["s"] for w in b1[-4:]] if len(b1) >= 4 else [53, 54, 55, 56]
        rnd = random.Random(3)
        self.dust = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.6, 2.2), rnd.uniform(0, 6.28),
                      rnd.uniform(4, 14)) for _ in range(80)]
        rnd = random.Random(11)
        kinds = ["room", "door", "window", "person", "face", "place", "shape", "sound"]
        self.s5cards = []
        tt = 73.2
        for i in range(12):
            ang = rnd.uniform(0, 2 * math.pi)
            for _ in range(20):
                x = 960 + math.cos(ang) * rnd.uniform(330, 720)
                y = 470 + math.sin(ang) * rnd.uniform(170, 300)
                if y > 250: break
                ang = rnd.uniform(0, 2 * math.pi)
            self.s5cards.append((tt, x, y, kinds[i % len(kinds)], rnd.uniform(0.6, 0.85)))
            tt += rnd.uniform(0.7, 1.0)
        self.dots = make_dot_tile()

    # ------------------------------------------------------------------
    def render(self, t, em):
        """Draw emissive content for time t. Returns dict of post params."""
        post = {"fade": 0.0, "glitch": 0.0, "dim_bg": 1.0}
        c = em
        # ---------------- scene routing
        if t < 49.0:
            self.scene_street(c, t, post)
        if 48.2 <= t < 72.8:
            self.scene_brain(c, t, post)
        if 72.0 <= t < 87.0:
            self.scene_science(c, t, post)
        if t >= 86.6:
            self.scene_final(c, t, post)
        self.draw_dust(c, t)
        # global fade in
        post["fade"] = max(post["fade"], 1 - smooth(seg(t, 0.0, 0.8)))
        # 72-ish transitions are handled inside scenes
        return post

    # ------------------------------------------------------------------
    def apply_cam(self, c, cam):
        cx, cy, z = cam
        c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-cx, -cy)

    def visible_x(self, cam):
        cx, cy, z = cam
        return cx - W / 2 / z, cx + W / 2 / z

    def draw_dust(self, c, t):
        for (x, y, r, ph, sp) in self.dust:
            yy = (y - t * sp) % H
            xx = (x + math.sin(t * 0.3 + ph) * 20) % W
            a = 0.12 + 0.18 * (0.5 + 0.5 * math.sin(t * 0.9 + ph * 3))
            c.drawCircle(xx, yy, r, fill(a))

    # ================================================================ S1–S3
    def scene_street(self, c, t, post):
        # ---- replay mapping (the repeated moment)
        GL0, GL1 = 16.05, 16.38                 # glitch window
        R0 = 16.38                              # replay start
        tt = t
        if R0 <= t < R0 + MOVE_A:
            tt = 11.0 + (t - R0)                # identical camera move
        elif t >= R0 + MOVE_A and t < 26.0:
            tt = 11.0 + MOVE_A + (t - R0 - MOVE_A)
        if GL0 <= t < GL1:
            post["glitch"] = 1.0
            tt = lerp(16.05, 11.0, ease_in(seg(t, GL0, GL1)))  # rewind blur

        st = opening_state(tt if t < 26.0 else 15.0)
        hero_x = st["hx"]; facing = st["facing"]; look = st["look"]; walking = st["hwalk"]
        arm = None; q = 0.0; trail = 0.0
        friend_x, friend_a, friend_walk = st["fx"], 1.0, st["fwalk"]
        cam = st["cam"]

        # ---- pull back after replay (20.0–24)
        if t >= 20.0 and t < 26.0:
            close = move_a(1.0)
            e = ease_io(seg(t, 20.6, 24.4))
            cam = (lerp(close[0], 930, e), lerp(close[1], 560, e), lerp(close[2] + 0.03 * (t - 20.0), 1.06, e))
            look = (lerp(0.0, 0.75, smooth(seg(t, 22.0, 23.0))), 0.0)
        # ---- scene 2: the loop (26–41)
        if t >= 26.0:
            hero_x, walking = walk_x(t, 26.0, 32.2, 960, 1860, acc=0.5, dec=0.8)
            friend_x, friend_walk = walk_x(t, 26.25, 31.4, 790, 1540, acc=0.5, dec=0.6)
            friend_a = 1 - smooth(seg(t, 29.6, 31.4))
            facing = 1; look = (0.75, 0.0)
            # confusion: look back and forth
            if t >= 32.6:
                k = t - 32.6
                facing = -1 if (0.25 < k < 1.45 or 2.7 < k < 3.3) else 1
                look = (0.8, -0.1)
            q = window(t, 33.0, 41.0, 0.3, 0.5)
            trail = window(t, 27.0, 31.8, 0.6, 0.8)
            # camera follows
            follow = hero_x + 40
            e0 = ease_io(seg(t, 26.0, 27.6))
            cx = lerp(930, follow, e0)
            z = lerp(1.06, 1.0, e0)
            cy = lerp(560, 540, e0)
            e1 = ease_io(seg(t, 32.2, 35.4))
            cam = (lerp(cx, hero_x, e1), lerp(cy, 650, e1), lerp(z, 1.18, e1))
            # S3: dive into the head (45.4 → 49)
            if t >= 45.0:
                hy = FLOOR + HEAD_Y
                e2 = ease_in(seg(t, 45.2, 49.0))
                cam = (lerp(cam[0], hero_x, e2), lerp(cam[1], hy, e2), lerp(cam[2], 26.0, e2))
        street_a = 1.0
        if t >= 35.0:
            street_a = lerp(1.0, 0.3, smooth(seg(t, 35.2, 37.0)))
        echo = st["ghost_echo"] + window(t, 26.8, 31.8, 0.8, 1.0) * 0.9

        cl, cr = self.visible_x(cam)
        c.save(); self.apply_cam(c, cam)
        # far skyline with parallax
        c.save(); c.translate(cam[0] * 0.45, 0); skyline(c, cam[0], cam[2], street_a); c.restore()
        street(c, cl, cr, street_a, hero_x=hero_x if t >= 26 else None, echo=echo, t=t)

        bob = 6 * abs(math.sin((t if t < 26 else t) * math.pi / 0.55)) if walking else 0.0
        fbob = 6 * abs(math.sin((t + 0.27) * math.pi / 0.55)) if friend_walk else 0.0
        # friend
        f_facing = 1
        if t < 26 and t > 5.2: f_facing = 1  # looks at hero (hero is to the right)
        draw_man(c, friend_x, FLOOR, s=0.94, facing=f_facing, bob=fbob, lean=3 if friend_walk else 0,
                 a=friend_a * (1 if t < 26 else 1), outline=True)
        if friend_a > 0.02 and t >= 26.0:
            # friend dissolves into echoes
            g = smooth(seg(t, 29.6, 31.4))
            for k in (1, 2):
                draw_man(c, friend_x - k * 40 * g, FLOOR, s=0.94, facing=1, bob=fbob, a=friend_a * 0.3 / k, outline=True)
        # bubble above the friend
        if t < 26:
            speech_bubble(c, friend_x + 30, FLOOR + HEAD_Y * 0.94 - 95, t, a=st["bubble"], ghost=st["bubble_ghost"])
        # hero trail (loop)
        if trail > 0.003:
            for k, ga in ((1, 0.35), (2, 0.18), (3, 0.08)):
                gx, gw = walk_x(t - 0.22 * k, 26.0, 32.2, 960, 1860, acc=0.5, dec=0.8)
                gb = 6 * abs(math.sin((t - 0.22 * k) * math.pi / 0.55)) if gw else 0
                draw_man(c, gx, FLOOR, facing=1, bob=gb, lean=3 if gw else 0, a=trail * ga)
        # ghost echo of the hero (5.9–7.6): someone was standing here a moment ago
        ge = st["ghost_echo"] if t < 26 else 0
        if ge > 0.003:
            draw_man(c, hero_x + 34, FLOOR - 4, facing=1, a=0.32 * ge)
            draw_man(c, hero_x + 68, FLOOR - 8, facing=1, a=0.14 * ge)
        zoom = cam[2]
        eyes = smooth(seg(zoom, 1.35, 1.9)) * (1 - smooth(seg(zoom, 4.0, 6.0)))
        head_fill = 1 - smooth(seg(t, 47.4, 48.6)) if t > 45 else 1.0
        draw_man(c, hero_x, FLOOR, facing=facing, bob=bob, lean=3 if walking else 0, arm=arm, look=look,
                 eyes=eyes, head_fill=head_fill, head_tilt=st["head_tilt"] if t < 26 else 0)
        # question pill above the hero
        if q > 0.003:
            hy = FLOOR + HEAD_Y - HEAD_R - 46 - 6 * math.sin(t * 2)
            c.save(); c.translate(hero_x, hy); s = 0.7 + 0.3 * ease_out(seg(t, 33.0, 33.5)); c.scale(s, s)
            c.drawCircle(0, 0, 26, fill(q)); draw_text(c, "?", 0, 0, 30, a=q, weight="Bold", v=0.07)
            c.restore()
        c.restore()

        # ---- screen space overlays
        # S1 question title
        a = window(t, 22.3, 25.9, 0.6, 0.5)
        if a > 0:
            y = 220 - 10 * ease_out(seg(t, 22.3, 23.2))
            draw_text(c, self.tx["q1"], 960, y, 64, a=a, weight="SemiBold", track=0.12)
        # S3 memory images around the hero (35.4–44.6)
        if 35.2 <= t < 45.0:
            spots = [(420, 300, "room"), (1500, 300, "door"), (360, 620, "window"), (1560, 620, "person")]
            for i, (x, y, kind) in enumerate(spots):
                t0 = 35.6 + i * 0.9
                aa = smooth(seg(t, t0, t0 + 0.6)) * (1 - 0.6 * smooth(seg(t, 40.9, 41.6))) * (1 - smooth(seg(t, 43.8, 44.8)))
                flick = 1.0 - 0.35 * max(0, math.sin(t * 9 + i * 2)) * window(t, t0 + 1.4, t0 + 2.2, 0.2, 0.2)
                fy = y + 8 * math.sin(t * 0.8 + i)
                card(c, x, fy, 300, 200, aa * flick, kind, t, s=0.92 + 0.08 * ease_out(seg(t, t0, t0 + 0.8)))
        # S3 title DÉJÀ VU + pill
        a = window(t, 41.25, 46.4, 0.5, 0.6)
        if a > 0:
            sc = 1 + 0.04 * seg(t, 41.25, 46.4)
            c.save(); c.translate(960, 230); c.scale(sc, sc)
            draw_text(c, self.tx["dv"], 0, 0, 120, a=a, weight="Bold", track=0.14)
            c.restore()
            pill(c, self.tx["fam"], 960, 340, size=26, a=window(t, 42.5, 46.4, 0.5, 0.6))
        # glitch white veil
        if post["glitch"]:
            pass
        # dive into the head: the head becomes a portal
        if t > 47.4:
            post["dim_bg"] = 1 - smooth(seg(t, 47.4, 48.6))

    # ================================================================ S4
    def scene_brain(self, c, t, post):
        tx = self.tx
        # portal ring expanding from the head
        ring = window(t, 48.2, 50.2, 0.2, 1.4)
        if ring > 0.003:
            r = lerp(HEAD_R * 26, 2400, ease_out(seg(t, 48.4, 50.2)))
            c.drawCircle(960, 540, min(r, 2600), stroke(5, ring))
        sa = smooth(seg(t, 48.6, 49.4)) * (1 - smooth(seg(t, 72.0, 72.8)))
        if sa <= 0.003: return
        # floor line
        c.drawLine(0, FLOOR, W, FLOOR, stroke(3, 0.6 * sa, dash=[22, 14], cap=False))
        # brain placement
        e = ease_io(seg(t, 56.4, 57.6))
        bx, by, bs = 1010, 430, 1.05
        bx, by, bs = lerp(bx, 960, e), lerp(by, 150, e), lerp(bs, 0.34, e)
        brain_a = sa * (1 - smooth(seg(t, 65.0, 65.8)))
        draw_u = ease_io(seg(t, 48.8, 51.2))
        pulse = 0.0
        for it in self.item_times:
            pulse = max(pulse, window(t, it + 0.75, it + 1.6, 0.1, 0.7))
        draw_brain(c, bx, by, bs, brain_a, draw_u, pulse, t)
        pill(c, tx["brain_tag"], bx, by + 290 * bs, size=24, a=brain_a * window(t, 50.6, 56.6, 0.5, 0.4))
        # items flying into the brain on "shapes, faces, places, sounds"
        kinds = ["shape", "face", "place", "sound"]
        starts = [(140, 180), (1780, 200), (180, 760), (1760, 740)]
        for i, it in enumerate(self.item_times):
            u = seg(t, it - 0.35, it + 0.85)
            a = smooth(seg(t, it - 0.35, it)) * (1 - smooth(seg(t, it + 0.55, it + 0.9)))
            if a <= 0: continue
            sx, sy = starts[i]
            e2 = ease_in(u) * 0.7 + ease_io(u) * 0.3
            x = lerp(sx, bx, e2); y = lerp(sy, by, e2) - 120 * math.sin(math.pi * u)
            floating_icon(c, kinds[i], x, y, lerp(1.05, 0.35, e2), a * sa, t)
        # hero: points at the brain (left), then stands between two rooms
        h1 = smooth(seg(t, 49.8, 50.6)) * (1 - smooth(seg(t, 56.4, 56.9)))
        arm1 = lerp(80, -38, ease_out(seg(t, 50.8, 51.5)))
        draw_man(c, 380, FLOOR, facing=1, arm=arm1, a=h1 * sa)
        # rooms (memory vs now)
        if t >= 56.8:
            h2 = smooth(seg(t, 57.0, 57.6)) * sa
            ra = smooth(seg(t, 57.0, 57.8)) * sa * (1 - smooth(seg(t, 71.4, 72.4)))
            rb = smooth(seg(t, 57.7, 58.5)) * sa * (1 - smooth(seg(t, 71.4, 72.4)))
            A = (560, 470); B = (1360, 470); cw, ch = 500, 320
            forgotten = smooth(seg(t, 63.6, 64.8))
            familiar = window(t, 62.6, 71.8, 0.4, 0.6)
            card(c, A[0], A[1], cw, ch, ra * (1 - 0.35 * forgotten), "room", t, dashed=forgotten > 0.5)
            card(c, B[0], B[1], cw, ch, rb, "room_b", t, bright=familiar)
            pill(c, tx["room_a"], A[0], A[1] + ch / 2 + 44, size=22, a=ra * (1 - 0.5 * forgotten))
            pill(c, tx["room_b"], B[0], B[1] + ch / 2 + 44, size=22, a=rb)
            # similarity links: window↔window, door↔door, lamp↔lamp
            la = window(t, 61.0, 66.0, 0.4, 0.8) * sa
            if la > 0.003:
                bw, bh = cw * 0.42, ch * 0.42
                pts = [(-bw * 0.32, -bh / 2 - ch * 0.04 + bh * 0.36, -bw * 0.22),
                       (bw * 0.24, -bh / 2 - ch * 0.04 + bh * 0.65, bw * 0.24),
                       (0, -ch / 2 + ch * 0.16, bw * 0.05)]
                for j, (ax, ay, bxo) in enumerate(pts):
                    u = ease_io(seg(t, 61.2 + j * 0.45, 62.4 + j * 0.45))
                    p0 = (A[0] + ax, A[1] + ay); p1 = (B[0] + bxo, B[1] + ay)
                    path = skia.Path(); path.moveTo(*p0)
                    mx = (p0[0] + p1[0]) / 2; my = min(p0[1], p1[1]) - 120 - 40 * j
                    path.quadTo(mx, my, *p1)
                    draw_partial(c, path, u, stroke(2.4, 0.75 * la, dash=[10, 9], cap=False))
                    # travelling glow dot
                    if 0 < u < 1:
                        q = 1 - u
                        x = q * q * p0[0] + 2 * q * u * mx + u * u * p1[0]
                        y = q * q * p0[1] + 2 * q * u * my + u * u * p1[1]
                        c.drawCircle(x, y, 7, fill(la))
                        c.drawCircle(x, y, 18, fill(0.18 * la))
            # hero looks at the first room, then the second
            facing = 1; arm = None; look = (0.75, 0)
            if 57.6 <= t < 59.9:
                facing = -1; arm = lerp(80, -30, ease_out(seg(t, 57.9, 58.5)))
            elif 59.9 <= t < 62.4:
                facing = 1; arm = lerp(80, -30, ease_out(seg(t, 60.1, 60.7)))
            elif 68.6 <= t < 71.4:
                facing = -1 if int((t - 68.6) / 0.9) % 2 == 0 else 1
            draw_man(c, 960, FLOOR, facing=facing, arm=arm, a=h2 * (1 - smooth(seg(t, 71.8, 72.6))))
        # FAMILIARITY ≠ RECOLLECTION
        a = window(t, 65.6, 71.6, 0.6, 0.6) * sa
        if a > 0.003:
            l, mid, r = tx["neq"]
            size = 56; gap = 34
            wl = text_width(l, size, "SemiBold", 0.1); wr = text_width(r, size, "SemiBold", 0.1)
            wm = text_width(mid, size * 1.2, "Bold")
            total = wl + wr + wm + 2 * gap
            x0 = 960 - total / 2
            y = 150 - 8 * ease_out(seg(t, 65.6, 66.4))
            draw_text(c, l, x0, y, size, a=a, track=0.1, align="left")
            ma = a * smooth(seg(t, 66.1, 66.6))
            draw_text(c, mid, x0 + wl + gap, y, size * 1.2, a=ma, weight="Bold", align="left")
            draw_text(c, r, x0 + wl + gap * 2 + wm, y, size, a=a * smooth(seg(t, 66.4, 67.0)), track=0.1, align="left")

    # ================================================================ S5
    def scene_science(self, c, t, post):
        sa = smooth(seg(t, 72.4, 73.2)) * (1 - smooth(seg(t, 85.0, 86.6)))
        if sa <= 0.003: return
        c.drawLine(0, FLOOR, W, FLOOR, stroke(3, 0.6 * sa, dash=[22, 14], cap=False))
        # memory fragments around the hero
        latest_x = None
        for i, (t0, x, y, kind, s) in enumerate(self.s5cards):
            life = 2.9
            a = window(t, t0, t0 + life, 0.45, 0.8)
            if a <= 0.003: continue
            flick = 1 - 0.5 * max(0, math.sin(t * 13 + i)) * window(t, t0 + 1.5, t0 + 2.1, 0.1, 0.1)
            dx = 14 * math.sin(t * 0.7 + i); dy = -12 * seg(t, t0, t0 + life)
            card(c, x + dx, y + dy, 280, 190, a * flick * sa, kind, t, s=s * (0.9 + 0.1 * ease_out(seg(t, t0, t0 + 0.6))))
            # overlap: a ghost copy slipping off
            ga = window(t, t0 + 0.9, t0 + 2.3, 0.4, 0.6)
            if ga > 0.003:
                card(c, x + dx + 26, y + dy - 16, 280, 190, 0.35 * ga * a * sa, kind, t + 0.4, s=s)
            if t0 <= t: latest_x = x
        facing = 1 if (latest_x is None or latest_x > 960) else -1
        look = (0.8, -0.35)
        arm = None
        if 81.6 <= t < 84.4:
            arm = lerp(80, -55, ease_out(seg(t, 81.6, 82.2))) if t < 83.8 else lerp(-55, 80, seg(t, 83.8, 84.4))
        draw_man(c, 960, FLOOR, facing=facing, look=look, arm=arm, a=sa)
        pill(c, self.tx["mech"], 960, 150, size=26, a=window(t, 79.7, 85.6, 0.5, 0.6) * sa)

    # ================================================================ S6
    def scene_final(self, c, t, post):
        a_in = smooth(seg(t, 86.6, 87.8))
        out = smooth(seg(t, 92.6, 94.0))
        if t < 94.2:
            # the opening composition, then the same push-in again
            M0 = 88.9
            if t < M0:
                cam = (900, 540, 1.0); look = (0.75, 0.0)
            else:
                u = seg(t, M0, M0 + MOVE_A)
                cam = move_a(u); look = move_a_look(u)
                cam = (cam[0], cam[1], cam[2] + 0.03 * max(0, t - M0 - MOVE_A))
            if M0 - 0.25 <= t < M0:
                post["glitch"] = 0.55
            a = a_in * (1 - out)
            cl, cr = self.visible_x(cam)
            c.save(); self.apply_cam(c, cam)
            c.save(); c.translate(cam[0] * 0.45, 0); skyline(c, cam[0], cam[2], a); c.restore()
            street(c, cl, cr, a)
            zoom = cam[2]
            eyes = smooth(seg(zoom, 1.35, 1.9))
            draw_man(c, 960, FLOOR, facing=1, look=look, eyes=eyes, a=a)
            c.restore()
            post["dim_bg"] = min(post.get("dim_bg", 1.0), 1 - out)
        # final question
        a = window(t, 95.5, 100.2, 0.8, 0.6)
        if a > 0.003:
            s = self.tx["final"]
            size = 62
            while text_width(s, size, "SemiBold", 0.08) > 1640: size -= 2
            draw_text(c, s, 960, 520 - 8 * ease_out(seg(t, 95.5, 96.5)), size, a=a, track=0.08)
            ln = 260 * ease_io(seg(t, 96.0, 97.2))
            c.drawLine(960 - ln, 600, 960 + ln, 600, stroke(2, 0.5 * a))
        # brand
        a = window(t, 100.6, 103.95, 0.9, 0.9)
        if a > 0.003:
            draw_text(c, self.tx["brand"], 960, 520, 84, a=a, weight="SemiBold", track=0.32)
            pill(c, self.tx["ep"], 960, 625, size=20, a=a * smooth(seg(t, 101.2, 101.9)), track=0.2)
            post["dim_bg"] = min(post.get("dim_bg", 1.0), 0.5)
        if t >= 94.0:
            post["dim_bg"] = min(post.get("dim_bg", 1.0), 0.5)


# ----------------------------------------------------------------- subtitles

def attach_punct(words, text):
    """edge-tts word boundaries drop punctuation; map them back onto the text tokens."""
    import re
    toks = text.replace("…", "… ").replace("—", " — ").replace("–", " – ").split()
    norm = lambda x: re.sub(r"[^\w]", "", x.lower())
    out = []; wi = 0
    for tok in toks:
        if norm(tok) == "":
            if out: out[-1] = dict(out[-1], w=out[-1]["w"] + (" " + tok if tok in ("—", "–") else tok))
            continue
        if wi < len(words):
            w = words[wi]
            # tokens may be split differently (e.g. "what's" vs "what" "'s")
            acc = norm(w["w"]); e = w["e"]; wj = wi + 1
            while len(acc) < len(norm(tok)) and wj < len(words):
                acc += norm(words[wj]["w"]); e = words[wj]["e"]; wj += 1
            out.append(dict(w=tok, s=w["s"], e=e)); wi = wj
        elif out:
            out[-1] = dict(out[-1], w=out[-1]["w"] + " " + tok)
    return out if out else words


def build_subs(timing, lang, maxc=44):
    kws = KEYWORDS[lang]
    chunks = []
    for line in timing:
        if line["id"] == "d3":  # shown as the final title instead
            continue
        words = attach_punct(line["words"], line["text"])
        n = len(words)
        L = lambda i, j: len(" ".join(x["w"] for x in words[i:j]))
        k = max(1, math.ceil(L(0, n) / maxc))
        target = L(0, n) / k
        # DP over break points: balanced lengths, prefer punctuation, no orphans
        best = {0: (0.0, [])}
        for j in range(1, n + 1):
            cands = []
            for i in best:
                if i >= j: continue
                ln = L(i, j)
                if ln > maxc + 4: continue
                cost = best[i][0] + (ln - target) ** 2
                if j < n and words[j - 1]["w"][-1:] in ",.…—:;?!»": cost -= 60
                if j - i == 1 and n > 1: cost += 200
                cands.append((cost, best[i][1] + [j]))
            if cands: best[j] = min(cands)
        cuts = best.get(n, (0, [n]))[1]
        i0 = 0
        for j in cuts:
            cur = words[i0:j]; i0 = j
            chunks.append(dict(s=cur[0]["s"] - 0.05, e=cur[-1]["e"] + 0.45,
                               words=[(x["w"], any(x["w"].lower().strip("«»“”\"',.…!?—:").startswith(kw) for kw in kws)) for x in cur]))
    for i in range(len(chunks) - 1):
        chunks[i]["e"] = min(chunks[i]["e"], chunks[i + 1]["s"] - 0.02)
    return chunks


def draw_subs(c, subs, t):
    for ch in subs:
        if ch["s"] <= t < ch["e"]:
            a = smooth(seg(t, ch["s"], ch["s"] + 0.12)) * (1 - smooth(seg(t, ch["e"] - 0.12, ch["e"])))
            size = 38
            sp = text_width(" ", size, "Medium")
            parts = []
            total = 0
            for wtxt, kw in ch["words"]:
                wgt = "Bold" if kw else "Medium"
                wd = text_width(wtxt, size, wgt)
                parts.append((wtxt, kw, wgt, wd)); total += wd
            total += sp * (len(parts) - 1)
            x = 960 - total / 2; y = 975
            box = skia.Rect(x - 22, y - 34, x + total + 22, y + 38)
            c.drawRRect(skia.RRect.MakeRectXY(box, 14, 14), skia.Paint(AntiAlias=True, Color=skia.Color4f(0.02, 0.02, 0.02, 0.62 * a)))
            for (wtxt, kw, wgt, wd) in parts:
                draw_text(c, wtxt, x, y, size, a=a * (1.0 if kw else 0.86), weight=wgt, align="left", v=1.0 if kw else 0.92)
                if kw:
                    c.drawLine(x, y + 26, x + wd, y + 26, stroke(2.5, 0.8 * a))
                x += wd + sp


# ----------------------------------------------------------------- compositor

def make_dot_tile():
    s = skia.Surface(W + 80, H + 80)
    c = s.getCanvas(); c.clear(skia.ColorTRANSPARENT)
    for y in range(0, H + 80, 40):
        for x in range(0, W + 80, 40):
            c.drawCircle(x + 0.5, y + 0.5, 1.25, fill(0.10))
    return s.makeImageSnapshot()


class Compositor:
    def __init__(self):
        self.em = skia.Surface(W, H)
        self.small = skia.Surface(W // 4, H // 4)
        self.small2 = skia.Surface(W // 4, H // 4)
        self.out = skia.Surface(W, H)
        self.buf = np.zeros((H, W, 4), np.uint8)
        self.info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
        # background gradient + vignette prebaked
        bg = skia.Surface(W, H); c = bg.getCanvas()
        c.clear(skia.Color(6, 6, 6))
        p = skia.Paint(); p.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H * 0.42), 900,
                                                                     [skia.Color(26, 26, 26), skia.Color(6, 6, 6)]))
        c.drawRect(skia.Rect(0, 0, W, H), p)
        self.bg = bg.makeImageSnapshot()
        vg = skia.Surface(W, H); c = vg.getCanvas(); c.clear(skia.ColorTRANSPARENT)
        p = skia.Paint(); p.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1150,
                                                                     [skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0.75).toColor()],
                                                                     [0.0, 0.55, 1.0]))
        c.drawRect(skia.Rect(0, 0, W, H), p)
        sub_bg = skia.Paint(); sub_bg.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 880), skia.Point(0, H)],
                                                                             [skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0.55).toColor()]))
        c.drawRect(skia.Rect(0, 880, W, H), sub_bg)
        self.vig = vg.makeImageSnapshot()

    def frame(self, fr: Frame, t):
        ec = self.em.getCanvas(); ec.clear(skia.ColorTRANSPARENT)
        post = fr.render(t, ec)
        draw_subs(ec, fr.subs, t)
        img = self.em.makeImageSnapshot()
        # glow at quarter resolution
        sc = self.small.getCanvas(); sc.clear(skia.ColorTRANSPARENT)
        sc.save(); sc.scale(.25, .25); sc.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear)); sc.restore()
        simg = self.small.makeImageSnapshot()
        s2 = self.small2.getCanvas(); s2.clear(skia.ColorTRANSPARENT)
        s2.drawImage(simg, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Blur(9, 9), Alpha=200))
        s2.drawImage(simg, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Blur(2.2, 2.2), BlendMode=skia.BlendMode.kPlus, Alpha=150))
        g = self.small2.makeImageSnapshot()
        oc = self.out.getCanvas()
        oc.drawImage(self.bg, 0, 0)
        dim = post.get("dim_bg", 1.0)
        oc.drawImage(fr.dots, -((t * 6) % 40), -((t * 3) % 40), skia.SamplingOptions(), skia.Paint(Alpha=int(255 * dim)))
        oc.save(); oc.scale(4, 4)
        oc.drawImage(g, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(BlendMode=skia.BlendMode.kPlus))
        oc.restore()
        oc.drawImage(img, 0, 0)
        oc.drawImage(self.vig, 0, 0)
        if post["fade"] > 0:
            oc.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color4f(0, 0, 0, clamp(post["fade"]))))
        self.out.readPixels(self.info, self.buf)
        frame = self.buf
        if post["glitch"] > 0:
            frame = glitch(frame.copy(), t, post["glitch"])
        return frame


def glitch(f, t, amt):
    rnd = random.Random(int(t * 1000))
    out = f
    for _ in range(int(7 * amt)):
        y0 = rnd.randint(0, H - 60); h = rnd.randint(8, 90)
        sh = int(rnd.uniform(-60, 60) * amt)
        out[y0:y0 + h] = np.roll(out[y0:y0 + h], sh, axis=1)
    # ghost double + lift
    ghost = np.roll(out, int(24 * amt), axis=1)
    out = np.maximum(out, (ghost.astype(np.uint16) * 0.45).astype(np.uint8))
    out[..., :3] = np.clip(out[..., :3].astype(np.int16) + int(28 * amt), 0, 255).astype(np.uint8)
    # scanlines
    out[::3, :, :3] = (out[::3, :, :3] * 0.7).astype(np.uint8)
    return out


# ----------------------------------------------------------------- drivers

def load_timing(lang):
    return json.load(open(os.path.join(ROOT, "assets", f"vo_{lang}", "timing.json")))


def render_chunk(args):
    lang, f0, f1, path = args
    fr = Frame(lang, load_timing(lang))
    comp = Compositor()
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                           "-pix_fmt", "yuv420p", "-tune", "animation", path], stdin=subprocess.PIPE)
    for i in range(f0, f1):
        ff.stdin.write(comp.frame(fr, i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    return path


def main():
    mode, lang = sys.argv[1], sys.argv[2]
    if mode == "stills":
        out = sys.argv[3]
        os.makedirs(out, exist_ok=True)
        fr = Frame(lang, load_timing(lang)); comp = Compositor()
        from PIL import Image
        for ts in sys.argv[4:]:
            t = float(ts)
            Image.fromarray(comp.frame(fr, t)[..., :3]).save(os.path.join(out, f"{lang}_{t:06.2f}.png"))
        return
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    n = int(round(DURATION * FPS))
    tmp = os.path.join(ROOT, "build"); os.makedirs(tmp, exist_ok=True)
    bounds = [round(n * k / workers) for k in range(workers + 1)]
    jobs = [(lang, bounds[k], bounds[k + 1], os.path.join(tmp, f"{lang}_part{k}.mp4")) for k in range(workers)]
    from multiprocessing import Pool
    with Pool(workers) as pool:
        parts = pool.map(render_chunk, jobs)
    lst = os.path.join(tmp, f"{lang}_parts.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(tmp, f"video_{lang}.mp4")], check=True)
    print("done", lang)


if __name__ == "__main__":
    main()
