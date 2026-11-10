"""Shared drawing / timing helpers."""
import math
import random
import cairo

W, H = 1080, 1920
FPS = 30


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    if isinstance(a, (tuple, list)):
        return tuple(lerp(x, y, t) for x, y in zip(a, b))
    return a + (b - a) * t


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t * t * t


def back_out(t, s=1.7):
    t = clamp(t)
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def prog(t, a, b):
    if b == a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def kf(t, keys, fn=ease_io):
    """Keyframes: list of (time, value). Values may be numbers or tuples."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, fn(prog(t, t0, t1)))
    return keys[-1][1]


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(c1, c2, t):
    return tuple(a + (b - a) * t for a, b in zip(c1, c2))


def shade(c, k):
    """k<1 darker, k>1 lighter"""
    if k <= 1:
        return tuple(x * k for x in c)
    return tuple(x + (1 - x) * (k - 1) for x in c)


def setc(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def ellipse(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(max(rx, 1e-3), max(ry, 1e-3))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def fill_c(ctx, c, a=1.0):
    setc(ctx, c, a)
    ctx.fill()


def glow(ctx, cx, cy, r, c, a=1.0, op=cairo.OPERATOR_ADD):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(0.4, c[0], c[1], c[2], a * 0.45)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.save()
    ctx.set_operator(op)
    ctx.set_source(g)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def vgrad(ctx, x, y, w, h, stops):
    g = cairo.LinearGradient(x, y, x, y + h)
    for off, c, a in stops:
        g.add_color_stop_rgba(off, c[0], c[1], c[2], a)
    ctx.set_source(g)
    ctx.rectangle(x, y, w, h)
    ctx.fill()


FONT = "Inter"


def font(ctx, size, weight="bold", family=FONT, italic=False):
    fam = family
    w = cairo.FONT_WEIGHT_BOLD if weight in ("bold", "black") else cairo.FONT_WEIGHT_NORMAL
    if weight == "black":
        fam = "Inter Display Black"
    sl = cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL
    ctx.select_font_face(fam, sl, w)
    ctx.set_font_size(size)


def text(ctx, s, x, y, size, c=(1, 1, 1), a=1.0, weight="bold", align="center",
         outline=0, oc=(0, 0, 0), oa=1.0, family=FONT, italic=False, spacing=0):
    font(ctx, size, weight, family, italic)
    ext = ctx.text_extents(s)
    w = ext.x_advance + spacing * max(0, len(s) - 1)
    if align == "center":
        x0 = x - w / 2
    elif align == "right":
        x0 = x - w
    else:
        x0 = x
    ctx.save()
    ctx.new_path()
    if spacing:
        xx = x0
        for ch in s:
            ctx.move_to(xx, y)
            ctx.text_path(ch)
            xx += ctx.text_extents(ch).x_advance + spacing
    else:
        ctx.move_to(x0, y)
        ctx.text_path(s)
    if outline:
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(ctx, oc, oa * a)
        ctx.set_line_width(outline)
        ctx.stroke_preserve()
    setc(ctx, c, a)
    ctx.fill()
    ctx.restore()
    return w


def text_width(ctx, s, size, weight="bold", family=FONT):
    font(ctx, size, weight, family)
    return ctx.text_extents(s).x_advance


def fit_text(ctx, s, x, y, size, maxw, **kw):
    w = text_width(ctx, s, size, kw.get('weight', 'bold'))
    if w > maxw:
        size = size * maxw / w
    return text(ctx, s, x, y, size, **kw)


def wrap(ctx, s, size, maxw, weight="bold"):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_width(ctx, trial, size, weight) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def noise1(t, seed=0):
    """Smooth 1D value noise in [-1,1]."""
    i = math.floor(t)
    f = t - i

    def h(n):
        r = random.Random(n * 7919 + seed * 104729)
        return r.uniform(-1, 1)
    return lerp(h(i), h(i + 1), ease(f))


def shake(t, amp, speed=1.0, seed=0):
    return (noise1(t * speed, seed) * amp, noise1(t * speed, seed + 31) * amp)
