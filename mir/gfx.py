"""Drawing helpers on top of pycairo: colors, shapes, text, easing."""
import math
import cairo

W, H = 1080, 1920
FPS = 30

FONT_BLACK = "Inter Display Black"
FONT_BOLD = "Inter Display ExtraBold"
FONT_MONO = "JetBrains Mono ExtraBold"


# ---------- math / easing ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


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
    """0..1 progress of t inside [a, b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def pop(t, start, dur=0.35):
    """Overshoot scale for things popping in."""
    p = seg(t, start, start + dur)
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    return 1 + 2.2 * (p - 1) ** 3 + 1.2 * (p - 1) ** 2


# ---------- color ----------
def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mix(c1, c2, t):
    c1, c2 = col(c1), col(c2)
    return tuple(lerp(c1[i], c2[i], t) for i in range(4))


def col(c, a=None):
    if isinstance(c, str):
        c = hexc(c)
    if len(c) == 3:
        c = (*c, 1.0)
    if a is not None:
        c = (c[0], c[1], c[2], c[3] * a)
    return c


def setc(ctx, c, a=None):
    ctx.set_source_rgba(*col(c, a))


# ---------- shapes ----------
def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def fill_rrect(ctx, x, y, w, h, r, c, a=None):
    rrect(ctx, x, y, w, h, r)
    setc(ctx, c, a)
    ctx.fill()


def fill_rect(ctx, x, y, w, h, c, a=None):
    ctx.rectangle(x, y, w, h)
    setc(ctx, c, a)
    ctx.fill()


def circle(ctx, x, y, r, c, a=None):
    ctx.new_sub_path()
    ctx.arc(x, y, max(r, 0.01), 0, 2 * math.pi)
    setc(ctx, c, a)
    ctx.fill()


def ellipse(ctx, x, y, rx, ry, c, a=None):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    setc(ctx, c, a)
    ctx.fill()


def poly(ctx, pts, c, a=None, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    setc(ctx, c, a)
    ctx.fill()


def line(ctx, x1, y1, x2, y2, w, c, a=None, cap=cairo.LINE_CAP_ROUND):
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.set_line_width(w)
    ctx.set_line_cap(cap)
    setc(ctx, c, a)
    ctx.stroke()


def vgrad(ctx, x, y, w, h, stops):
    g = cairo.LinearGradient(0, y, 0, y + h)
    for o, c in stops:
        g.add_color_stop_rgba(o, *col(c))
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()


def glow(ctx, x, y, r, c, a=1.0):
    """Soft radial light."""
    if r <= 0 or a <= 0:
        return
    cc = col(c)
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], cc[3] * a)
    g.add_color_stop_rgba(0.35, cc[0], cc[1], cc[2], cc[3] * a * 0.45)
    g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def cone(ctx, x, y, angle, spread, length, c, a=0.4):
    """Light cone from a point."""
    cc = col(c)
    g = cairo.RadialGradient(x, y, 0, x, y, length)
    g.add_color_stop_rgba(0, cc[0], cc[1], cc[2], a)
    g.add_color_stop_rgba(1, cc[0], cc[1], cc[2], 0)
    ctx.move_to(x, y)
    ctx.arc(x, y, length, angle - spread, angle + spread)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()


# ---------- text ----------
def font(ctx, size, face=FONT_BLACK):
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text_w(ctx, s):
    return ctx.text_extents(s).x_advance


def wrap(ctx, s, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_w(ctx, test) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(ctx, s, x, y, size, c="#ffffff", face=FONT_BLACK, align="center",
         outline=0, oc="#000000", shadow=True, a=1.0, fit=None):
    """Draw one line of text; y is the baseline. Returns width."""
    font(ctx, size, face)
    if fit and text_w(ctx, s) > fit:
        size = size * fit / text_w(ctx, s)
        font(ctx, size, face)
    tw = text_w(ctx, s)
    if align == "center":
        x0 = x - tw / 2
    elif align == "right":
        x0 = x - tw
    else:
        x0 = x
    if shadow:
        ctx.move_to(x0 + size * 0.04, y + size * 0.07)
        ctx.text_path(s)
        if outline:
            ctx.set_line_width(outline * 2)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            setc(ctx, "#000000", 0.45 * a)
            ctx.stroke_preserve()
        setc(ctx, "#000000", 0.45 * a)
        ctx.fill()
    ctx.move_to(x0, y)
    ctx.text_path(s)
    if outline:
        ctx.set_line_width(outline * 2)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(ctx, oc, a)
        ctx.stroke_preserve()
    setc(ctx, c, a)
    ctx.fill()
    return tw


def sticker(ctx, s, x, y, size, angle=-4, bg="#e3262f", fg="#ffffff", s_scale=1.0, a=1.0):
    """Red tilted label like in the channel's thumbnails."""
    if s_scale <= 0 or a <= 0:
        return
    font(ctx, size)
    tw = text_w(ctx, s)
    pad_x, pad_y = size * 0.45, size * 0.32
    w, h = tw + pad_x * 2, size + pad_y * 2
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(angle))
    ctx.scale(s_scale, s_scale)
    fill_rrect(ctx, -w / 2 + 6, -h / 2 + 10, w, h, size * 0.22, "#000000", 0.45 * a)
    fill_rrect(ctx, -w / 2, -h / 2, w, h, size * 0.22, "#ffffff", a)
    fill_rrect(ctx, -w / 2 + 5, -h / 2 + 5, w - 10, h - 10, size * 0.18, bg, a)
    ctx.move_to(-tw / 2, size * 0.36)
    ctx.text_path(s)
    setc(ctx, fg, a)
    ctx.fill()
    ctx.restore()


def clock_icon(ctx, x, y, r, c="#ffffff", bg="#000000", a=1.0):
    circle(ctx, x, y, r, c, a)
    circle(ctx, x, y, r * 0.72, bg, a)
    line(ctx, x, y, x, y - r * 0.5, r * 0.22, c, a)
    line(ctx, x, y, x + r * 0.35, y + r * 0.1, r * 0.22, c, a)


def time_chip(ctx, s, x, y, size=58, bg="#c8161d", a=1.0, s_scale=1.0):
    """Pill with a clock icon and a time, like '07:00' chips on the channel."""
    if a <= 0 or s_scale <= 0:
        return
    font(ctx, size, FONT_MONO)
    tw = text_w(ctx, s)
    h = size * 1.45
    w = tw + h + size * 0.6
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s_scale, s_scale)
    fill_rrect(ctx, -w / 2 + 4, -h / 2 + 8, w, h, h / 2, "#000000", 0.5 * a)
    fill_rrect(ctx, -w / 2 - 5, -h / 2 - 5, w + 10, h + 10, h / 2 + 5, "#f2c230", a)
    fill_rrect(ctx, -w / 2, -h / 2, w, h, h / 2, bg, a)
    clock_icon(ctx, -w / 2 + h * 0.55, 0, h * 0.3, "#ffffff", bg, a)
    ctx.move_to(-w / 2 + h * 0.98, size * 0.36)
    ctx.text_path(s)
    setc(ctx, "#ffffff", a)
    ctx.fill()
    ctx.restore()
