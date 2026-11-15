"""Core helpers: easing, colours, paints, deterministic noise, camera, text."""
import math
import functools
import numpy as np
import skia

W, H = 1080, 1920
FPS = 30

FONT_DIR = "/usr/share/fonts/opentype/inter/"


@functools.lru_cache(None)
def typeface(weight="ExtraBold"):
    return skia.Typeface.MakeFromFile(f"{FONT_DIR}Inter-{weight}.otf")


def font(size, weight="ExtraBold"):
    f = skia.Font(typeface(weight), size)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setSubpixel(True)
    return f


# ---------------------------------------------------------------- math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def inv(a, b, x):
    """normalised position of x in [a,b], clamped"""
    if b == a:
        return 1.0 if x >= b else 0.0
    return clamp((x - a) / (b - a))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def back_out(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def seg(t, a, b, f=ease_in_out):
    return f(inv(a, b, t))


def keys(t, kf, f=ease_in_out):
    """piecewise interpolation over [(time, value), ...]; values may be tuples"""
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            k = f(inv(t0, t1, t))
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, k) for a, b in zip(v0, v1))
            return lerp(v0, v1, k)
    return kf[-1][1]


def hash1(i):
    x = math.sin(i * 127.1 + 311.7) * 43758.5453
    return x - math.floor(x)


def vnoise(x, seed=0):
    """smooth 1D value noise in [-1,1]"""
    i = math.floor(x)
    f = x - i
    a = hash1(i + seed * 101.3)
    b = hash1(i + 1 + seed * 101.3)
    u = f * f * (3 - 2 * f)
    return (a + (b - a) * u) * 2 - 1


def fbm(x, seed=0, oct=3):
    s, amp, fr = 0.0, 0.5, 1.0
    for o in range(oct):
        s += amp * vnoise(x * fr, seed + o * 7)
        amp *= 0.5
        fr *= 2.0
    return s


# ---------------------------------------------------------------- colour
def hexc(h, a=255):
    if isinstance(h, tuple):
        return (h[0], h[1], h[2], a)
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def col(c, a=None):
    if isinstance(c, str):
        c = hexc(c)
    if len(c) == 3:
        c = (*c, 255)
    if a is not None:
        c = (c[0], c[1], c[2], int(clamp(a, 0, 1) * 255))
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(c[3]))


def mix(c1, c2, t):
    if isinstance(c1, str):
        c1 = hexc(c1)
    if isinstance(c2, str):
        c2 = hexc(c2)
    if len(c1) == 3:
        c1 = (*c1, 255)
    if len(c2) == 3:
        c2 = (*c2, 255)
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def shade(c, k):
    """k<0 darker, k>0 lighter"""
    if isinstance(c, str):
        c = hexc(c)
    if k < 0:
        return mix(c, (0, 0, 0, c[3] if len(c) > 3 else 255), -k)
    return mix(c, (255, 255, 255, c[3] if len(c) > 3 else 255), k)


def paint(c, a=None, stroke=None, cap=None, blur=0, blend=None, aa=True):
    p = skia.Paint(AntiAlias=aa, Color=col(c, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap in (None, "round") else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    return p


def lin_grad(x0, y0, x1, y1, colors, pos=None):
    return skia.GradientShader.MakeLinear(
        [skia.Point(x0, y0), skia.Point(x1, y1)], [col(c) for c in colors], pos)


def rad_grad(x, y, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(x, y), max(r, 0.01), [col(c) for c in colors], pos)


def gpaint(shader, blend=None, alpha=None):
    p = skia.Paint(AntiAlias=True, Shader=shader)
    if blend is not None:
        p.setBlendMode(blend)
    if alpha is not None:
        p.setAlphaf(clamp(alpha))
    return p


def glow(c, x, y, r, color, a=1.0, blend=skia.BlendMode.kPlus):
    cc = hexc(color) if isinstance(color, str) else color
    c0 = (cc[0], cc[1], cc[2], int(255 * clamp(a)))
    c1 = (cc[0], cc[1], cc[2], int(255 * clamp(a) * 0.35))
    c2 = (cc[0], cc[1], cc[2], 0)
    c.drawCircle(x, y, r, gpaint(rad_grad(x, y, r, [c0, c1, c2], [0, 0.35, 1]), blend))


# ---------------------------------------------------------------- paths
def path_poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth_path(pts, close=True, tension=0.5):
    """Catmull-Rom through points -> cubic path"""
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        k = tension / 3.0 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def rrect(x, y, w, h, r):
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


# ---------------------------------------------------------------- camera
class Cam:
    """World->screen: the world point (x, y) lands on screen centre, scaled by z."""

    def __init__(self, x=W / 2, y=H / 2, z=1.0, rot=0.0):
        self.x, self.y, self.z, self.rot = x, y, z, rot

    def apply(self, c):
        c.translate(W / 2, H / 2)
        c.scale(self.z, self.z)
        if self.rot:
            c.rotate(self.rot)
        c.translate(-self.x, -self.y)


def drift(t, amt=6.0, seed=0, speed=0.35):
    """hand-held camera float"""
    return (fbm(t * speed, seed) * amt, fbm(t * speed, seed + 50) * amt)


def shake(t, amt, seed=3, speed=18.0):
    return (vnoise(t * speed, seed) * amt, vnoise(t * speed, seed + 9) * amt)


# ---------------------------------------------------------------- text
def text_center(c, s, x, y, size, color="#ffffff", weight="ExtraBold", stroke=0,
                stroke_color="#000000", shadow=0, alpha=1.0, letter=0.0):
    f = font(size, weight)
    blob = skia.TextBlob.MakeFromString(s, f)
    w = f.measureText(s)
    if shadow:
        c.drawTextBlob(blob, x - w / 2 + shadow * 0.3, y + shadow,
                       paint((0, 0, 0), 0.55 * alpha, blur=shadow * 0.6))
    if stroke:
        c.drawTextBlob(blob, x - w / 2, y, paint(stroke_color, alpha, stroke=stroke))
    c.drawTextBlob(blob, x - w / 2, y, paint(color, alpha))
    return w


def wrap(s, f, maxw):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.measureText(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
