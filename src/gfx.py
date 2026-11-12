"""Low-level drawing helpers on top of skia."""
import math
import random
import skia

W, H = 1080, 1920
FPS = 30

FONT_BLACK = skia.Typeface.MakeFromFile('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf')
FONT_BOLD = skia.Typeface.MakeFromFile('/usr/share/fonts/opentype/inter/Inter-Bold.otf')


def hexc(h, a=255):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def col(c, a=1.0):
    return skia.Color4f(c[0], c[1], c[2], a).toColor()


def paint(c=None, a=1.0, stroke=0, aa=True, cap=None, blend=None, shader=None, blur=0):
    p = skia.Paint(AntiAlias=aa)
    if c is not None:
        if isinstance(c, str):
            c = rgb(c)
        p.setColor4f(skia.Color4f(c[0], c[1], c[2], a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap or skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blend is not None:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def _gc(c):
    if isinstance(c, int):
        return c
    if isinstance(c, str):
        c = rgb(c)
    return col(c[:3], c[3] if len(c) > 3 else 1)


def lin_grad(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)],
                                          [_gc(c) for c in cols],
                                          pos)


def rad_grad(c, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), r,
                                          [_gc(cc) for cc in cols],
                                          pos)


def path_poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def path_smooth(pts, close=True, tension=0.5):
    """Catmull-Rom through points -> cubic path."""
    p = skia.Path()
    n = len(pts)
    if n < 3:
        return path_poly(pts, close)
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else pts[(i + 1) % n]
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def ellipse(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


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


def lerp(a, b, t):
    return a + (b - a) * t


def remap(x, a, b, c=0.0, d=1.0):
    return lerp(c, d, clamp((x - a) / (b - a)))


def noise1(x, seed=0):
    """Smooth 1D value noise in [-1,1]."""
    i = math.floor(x)
    f = x - i

    def h(n):
        n = (n * 374761393 + seed * 668265263) & 0xffffffff
        n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
        return ((n ^ (n >> 16)) & 0xffff) / 32767.5 - 1.0
    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


def fbm(x, seed=0, octaves=3):
    v, a, fr = 0.0, 0.5, 1.0
    for o in range(octaves):
        v += a * noise1(x * fr, seed + o * 17)
        a *= 0.5
        fr *= 2.03
    return v


def record(bounds, fn):
    rec = skia.PictureRecorder()
    c = rec.beginRecording(skia.Rect.MakeLTRB(*bounds))
    fn(c)
    return rec.finishRecordingAsPicture()


def raster(w, h, fn):
    surf = skia.Surface(int(w), int(h))
    c = surf.getCanvas()
    c.clear(skia.ColorTRANSPARENT)
    fn(c)
    return surf.makeImageSnapshot()


def tint_filter(mul=(1, 1, 1), fog=(0, 0, 0), f=0.0, sat=1.0):
    """color matrix: out = lerp(desat(rgb)*mul, fog, f)."""
    s = sat
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    m = []
    for i, (mu, fo) in enumerate(zip(mul, fog)):
        row = [(lr * (1 - s) + (s if i == 0 else 0)),
               (lg * (1 - s) + (s if i == 1 else 0)),
               (lb * (1 - s) + (s if i == 2 else 0))]
        row = [r * mu * (1 - f) for r in row]
        m += row + [0, fo * f]
    m += [0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)


def text(canvas, s, x, y, size, color='#ffffff', font=None, align='center', a=1.0, outline=0, outline_color='#000000'):
    font = skia.Font(font or FONT_BLACK, size)
    blob = skia.TextBlob.MakeFromString(s, font)
    w = font.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if outline:
        canvas.drawTextBlob(blob, x, y, paint(outline_color, a, stroke=outline))
    canvas.drawTextBlob(blob, x, y, paint(color, a))
    return w
