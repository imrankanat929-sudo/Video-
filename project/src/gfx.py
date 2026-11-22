"""Drawing primitives for the HUMAN MIND visual style (white on black, cairo)."""
import math
import cairo
import numpy as np

FONT = "Inter"
GY = 790  # ground line y


# ---------------------------------------------------------------- easing ----
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def e_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def e_io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x, s=1.9):
    x = clamp(x)
    c3 = s + 1
    return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2


def ramp(t, a, b, ease=e_out):
    if b <= a:
        return 1.0 if t >= a else 0.0
    return ease((t - a) / (b - a))


def window(t, a, b, fin=0.3, fout=0.3):
    """1 inside [a,b] with fades at both ends."""
    return ramp(t, a, a + fin) * (1 - ramp(t, b, b + fout, e_io))


def lerp(a, b, k):
    return a + (b - a) * k


def white(ctx, a=1.0):
    ctx.set_source_rgba(1, 1, 1, clamp(a))


def black(ctx, a=1.0):
    ctx.set_source_rgba(0, 0, 0, clamp(a))


def hash01(i, salt=0):
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


# ------------------------------------------------------------------ text ----
def _font(ctx, size, weight):
    w = cairo.FONT_WEIGHT_BOLD if weight == "bold" else cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, w)
    ctx.set_font_size(size)


def text_width(ctx, s, size, weight="bold", spacing=0.0):
    _font(ctx, size, weight)
    w = sum(ctx.text_extents(ch).x_advance for ch in s)
    return w + spacing * max(0, len(s) - 1)


def text(ctx, s, x, y, size, a=1.0, weight="bold", spacing=0.0, align="center",
         color=(1, 1, 1), reveal=1.0):
    """Draw text with letter spacing. y is the baseline-centre (cap middle).
    reveal (0..1) fades letters in left to right."""
    if a <= 0.001:
        return
    _font(ctx, size, weight)
    tw = text_width(ctx, s, size, weight, spacing)
    _font(ctx, size, weight)
    if align == "center":
        cx = x - tw / 2
    elif align == "right":
        cx = x - tw
    else:
        cx = x
    by = y + size * 0.36
    n = len(s)
    for i, ch in enumerate(s):
        la = a
        if reveal < 1.0:
            k = clamp(reveal * (n + 4) - i, 0, 4) / 4
            la = a * k
        if la > 0.001:
            ctx.set_source_rgba(color[0], color[1], color[2], clamp(la))
            ctx.move_to(cx, by)
            ctx.show_text(ch)
        cx += ctx.text_extents(ch).x_advance + spacing


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def pill(ctx, s, x, y, a=1.0, size=22, pop=1.0):
    """White rounded label with dark text (as in the style reference)."""
    if a <= 0.001:
        return
    tw = text_width(ctx, s, size, "bold", 3.0)
    w, h = tw + 2 * size * 1.25, size * 2.15
    sc = 0.85 + 0.15 * pop
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    white(ctx, a * 0.96)
    ctx.fill()
    text(ctx, s, 0, 0, size, a, "bold", 3.0, color=(0.04, 0.04, 0.04))
    ctx.restore()


def pill_seq(ctx, t, seq, x=960, y=165, size=22):
    """seq: list of (start, end, text). Crossfades between labels."""
    for (a, b, s) in seq:
        al = window(t, a, b, 0.22, 0.25)
        if al > 0:
            pill(ctx, s, x, y - 10 * (1 - ramp(t, a, a + 0.3)), al, size,
                 e_back((t - a) / 0.35))


# --------------------------------------------------------------- lines ------
def polyline(ctx, pts, frac=1.0, width=3.0, a=1.0, dash=None):
    """Draw the first `frac` of a polyline (by arc length)."""
    if frac <= 0 or a <= 0.001 or len(pts) < 2:
        return
    pts = np.asarray(pts, float)
    seg = np.hypot(*(pts[1:] - pts[:-1]).T)
    total = seg.sum()
    target = total * clamp(frac)
    ctx.move_to(*pts[0])
    acc = 0.0
    for i, L in enumerate(seg):
        if acc + L >= target:
            k = (target - acc) / L if L > 0 else 0
            p = pts[i] + (pts[i + 1] - pts[i]) * k
            ctx.line_to(*p)
            break
        ctx.line_to(*pts[i + 1])
        acc += L
    ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if dash:
        ctx.set_dash(dash)
    white(ctx, a)
    ctx.stroke()
    ctx.set_dash([])


def line(ctx, x0, y0, x1, y1, frac=1.0, width=3.0, a=1.0, dash=None):
    polyline(ctx, [(x0, y0), (x1, y1)], frac, width, a, dash)


def ground(ctx, a=1.0, y=GY, x0=-400, x1=2320, offset=0.0):
    if a <= 0.001:
        return
    ctx.move_to(x0, y)
    ctx.line_to(x1, y)
    ctx.set_line_width(2.2)
    ctx.set_dash([16, 12], offset)
    white(ctx, 0.55 * a)
    ctx.stroke()
    ctx.set_dash([])


def spotlight(ctx, x, y, r, a):
    if a <= 0.001:
        return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.10 * a)
    g.add_color_stop_rgba(0.5, 1, 1, 1, 0.035 * a)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def cone_light(ctx, x, gy, a):
    """Top-down stage light on a character."""
    if a <= 0.001:
        return
    g = cairo.LinearGradient(0, 0, 0, gy)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.0)
    g.add_color_stop_rgba(1, 1, 1, 1, 0.09 * a)
    ctx.move_to(x - 60, -50)
    ctx.line_to(x + 60, -50)
    ctx.line_to(x + 230, gy)
    ctx.line_to(x - 230, gy)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.translate(x, gy)
    ctx.scale(1, 0.16)
    g2 = cairo.RadialGradient(0, 0, 0, 0, 0, 260)
    g2.add_color_stop_rgba(0, 1, 1, 1, 0.22 * a)
    g2.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g2)
    ctx.arc(0, 0, 260, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


# -------------------------------------------------------------- shapes ------
def shape_pts(kind, r, n=60):
    """Closed outline with exactly n points, so shapes can morph."""
    ang = np.linspace(-math.pi / 2, 1.5 * math.pi, n, endpoint=False)
    if kind == "circle":
        return np.stack([np.cos(ang) * r, np.sin(ang) * r], 1)
    if kind == "triangle":
        verts = [(0, -r * 1.05), (r * 1.0, r * 0.75), (-r * 1.0, r * 0.75)]
    elif kind == "square":
        verts = [(-r * .85, -r * .85), (r * .85, -r * .85), (r * .85, r * .85),
                 (-r * .85, r * .85)]
    elif kind == "star":
        verts = []
        for i in range(10):
            rr = r * (1.05 if i % 2 == 0 else 0.45)
            aa = -math.pi / 2 + i * math.pi / 5
            verts.append((math.cos(aa) * rr, math.sin(aa) * rr))
    else:
        raise ValueError(kind)
    verts = np.array(verts + [verts[0]], float)
    seg = np.hypot(*(verts[1:] - verts[:-1]).T)
    cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], n, endpoint=False)
    x = np.interp(s, cum, verts[:, 0])
    y = np.interp(s, cum, verts[:, 1])
    return np.stack([x, y], 1)


def shape(ctx, kind, x, y, r, a=1.0, fill=True, morph_to=None, k=0.0, width=3,
          color=1.0, rot=0.0):
    if a <= 0.001:
        return
    p = shape_pts(kind, r)
    if morph_to:
        p = p * (1 - k) + shape_pts(morph_to, r) * k
    if rot:
        c, s = math.cos(rot), math.sin(rot)
        p = p @ np.array([[c, s], [-s, c]])
    ctx.move_to(x + p[0, 0], y + p[0, 1])
    for q in p[1:]:
        ctx.line_to(x + q[0], y + q[1])
    ctx.close_path()
    ctx.set_source_rgba(color, color, color, clamp(a))
    if fill:
        ctx.fill()
    else:
        ctx.set_line_width(width)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()


def heart_path(ctx, x, y, s):
    ctx.move_to(x, y + s * 0.85)
    ctx.curve_to(x - s * 1.25, y - s * 0.05, x - s * 0.6, y - s * 1.05, x, y - s * 0.35)
    ctx.curve_to(x + s * 0.6, y - s * 1.05, x + s * 1.25, y - s * 0.05, x, y + s * 0.85)
    ctx.close_path()


def glyph(ctx, kind, x, y, s, color=0.0, a=1.0):
    """Small icon glyph centred at x,y with size s (~radius)."""
    ctx.set_source_rgba(color, color, color, clamp(a))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if kind == "heart":
        heart_path(ctx, x, y + s * 0.05, s * 0.72)
        ctx.fill()
    elif kind == "check":
        ctx.move_to(x - s * 0.55, y + s * 0.02)
        ctx.line_to(x - s * 0.15, y + s * 0.42)
        ctx.line_to(x + s * 0.6, y - s * 0.4)
        ctx.set_line_width(s * 0.26)
        ctx.stroke()
    elif kind == "cross":
        for d in (1, -1):
            ctx.move_to(x - s * 0.45, y - s * 0.45 * d)
            ctx.line_to(x + s * 0.45, y + s * 0.45 * d)
        ctx.set_line_width(s * 0.26)
        ctx.stroke()
    elif kind == "dash":
        ctx.move_to(x - s * 0.45, y)
        ctx.line_to(x + s * 0.45, y)
        ctx.set_line_width(s * 0.24)
        ctx.stroke()
    elif kind in ("triangle", "circle", "square", "star"):
        shape(ctx, kind, x, y + (s * 0.08 if kind == "triangle" else 0), s * 0.55,
              a, True, color=color)
    elif kind == "link":
        ctx.set_line_width(s * 0.18)
        ctx.arc(x - s * 0.28, y, s * 0.36, 0, 2 * math.pi)
        ctx.stroke()
        ctx.arc(x + s * 0.28, y, s * 0.36, 0, 2 * math.pi)
        ctx.stroke()
    elif kind == "wave":
        ctx.set_line_width(s * 0.14)
        for i in range(31):
            u = i / 30
            px, py = x + s * (-0.62 + 1.24 * u), y + s * 0.3 * math.sin(u * math.pi * 3)
            (ctx.move_to if i == 0 else ctx.line_to)(px, py)
        ctx.stroke()
    elif kind == "excl":
        ctx.set_line_width(s * 0.24)
        ctx.move_to(x, y - s * 0.5)
        ctx.line_to(x, y + s * 0.12)
        ctx.stroke()
        ctx.arc(x, y + s * 0.48, s * 0.14, 0, 2 * math.pi)
        ctx.fill()
    else:  # text glyph like "?" or "$"
        text(ctx, kind, x, y, s * 1.15, a, "bold", color=(color,) * 3)


def badge(ctx, kind, x, y, r, a=1.0, pop=1.0, outline=False):
    """White circular coin with a dark glyph (reference '$' coins)."""
    if a <= 0.001:
        return
    sc = max(0.0, pop)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    if outline:
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        black(ctx, a)
        ctx.fill_preserve()
        white(ctx, a)
        ctx.set_line_width(3)
        ctx.stroke()
        glyph(ctx, kind, 0, 0, r * 0.95, 1.0, a)
    else:
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        white(ctx, a)
        ctx.fill()
        glyph(ctx, kind, 0, 0, r * 0.95, 0.04, a)
    ctx.restore()


def pop_badge(ctx, t, t0, kind, x, y, r, t_out=None, bob=True, outline=False):
    if t < t0:
        return
    al = ramp(t, t0, t0 + 0.12)
    if t_out is not None:
        al *= 1 - ramp(t, t_out, t_out + 0.35)
    dy = math.sin((t - t0) * 2.2 + x * 0.01) * 6 if bob else 0
    badge(ctx, kind, x, y + dy, r, al, e_back((t - t0) / 0.35, 2.4), outline)


# -------------------------------------------------------------- bubbles -----
def bubble(ctx, x, y, w, h, a=1.0, tail=(0, 1), pop=1.0, thought=False,
           dashed=False):
    """Speech/thought bubble centred at (x,y). tail=(dx,dy) direction."""
    if a <= 0.001:
        return
    sc = max(0.0, pop)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    rrect(ctx, -w / 2, -h / 2, w, h, min(h / 2, 34))
    black(ctx, a * 0.92)
    ctx.fill_preserve()
    white(ctx, a)
    ctx.set_line_width(3)
    if dashed:
        ctx.set_dash([8, 7])
    ctx.stroke()
    ctx.set_dash([])
    tx, ty = tail
    if thought:
        for i, rr in enumerate((9, 6)):
            cx = tx * (w * 0.25 + 18 + i * 22)
            cy = ty * (h / 2 + 16 + i * 20)
            ctx.arc(cx, cy, rr, 0, 2 * math.pi)
            white(ctx, a)
            ctx.set_line_width(3)
            ctx.stroke()
    else:
        bx = tx * w * 0.22
        ctx.move_to(bx - 12, h / 2 - 1)
        ctx.line_to(bx + tx * 30, h / 2 + 28)
        ctx.line_to(bx + 14, h / 2 - 1)
        black(ctx, a)
        ctx.fill_preserve()
        white(ctx, a)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.rectangle(bx - 10, h / 2 - 4, 22, 3)
        black(ctx, a)
        ctx.fill()
    ctx.restore()


# --------------------------------------------------------------- person -----
def person(ctx, x, gy, s=1.0, a=1.0, look=0.0, lean=0.0, arm_l=0.18,
           arm_r=0.18, walk=None, emblem=None, emblem_k=1.0, emblem_to=None,
           emblem_morph=0.0, hat=None, hat_a=1.0, stretch=1.0, lum=1.0,
           mirror=False):
    """Pictogram person.  (x, gy) = feet on the ground.  ~225 px tall at s=1.
    look   : -1..1 head turn (offset toward the looked-at side)
    arm_*  : radians from hanging down, rotating outward/up
    walk   : phase in radians, or None for standing
    emblem : chest cut-out shape ('triangle','circle','star',...)
    lum    : brightness of the silhouette (crowd uses < 1)"""
    if a <= 0.001:
        return
    ctx.save()
    ctx.translate(x, gy)
    ctx.scale(s * (-1 if mirror else 1), s)
    ctx.rotate(lean)
    ctx.scale(1, stretch)
    ctx.push_group()
    ctx.set_source_rgba(lum, lum, lum, 1)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    # legs
    for side in (-1, 1):
        hx, hy = side * 16, -62
        if walk is None:
            fx, fy = side * 18, -8
        else:
            ph = walk + (0 if side < 0 else math.pi)
            fx = side * 10 + math.sin(ph) * 26
            fy = -8 - max(0, math.cos(ph)) * 12
        ctx.move_to(hx, hy)
        ctx.line_to(fx, fy)
        ctx.set_line_width(19)
        ctx.stroke()
    # arms
    for side, ang in ((-1, arm_l), (1, arm_r)):
        if walk is not None and ang < 0.4:
            ang = ang + math.sin(walk + (math.pi if side > 0 else 0)) * 0.35 * side
        sx, sy = side * 33, -140
        L = 66
        ex = sx + side * math.sin(ang) * L
        ey = sy + math.cos(ang) * L
        ctx.move_to(sx, sy)
        ctx.line_to(ex, ey)
        ctx.set_line_width(17)
        ctx.stroke()
    # torso
    tw, top, bot = 80, -166, -54
    rrect(ctx, -tw / 2, top, tw, bot - top, 14)
    ctx.fill()
    ctx.save()
    ctx.move_to(-tw / 2, top + 38)
    ctx.arc(0, top + 38, tw / 2, math.pi, 2 * math.pi)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    rrect(ctx, -tw / 2, top + 30, tw, bot - top - 30, 12)
    ctx.fill()
    # head
    hx = look * 9
    ctx.arc(hx, -204, 28, 0, 2 * math.pi)
    ctx.fill()
    # hat
    if hat and hat_a > 0.01:
        ctx.save()
        ctx.translate(hx, -226)
        if hat == "cone":
            ctx.move_to(-30, 4)
            ctx.line_to(0, -58)
            ctx.line_to(30, 4)
            ctx.close_path()
            ctx.fill()
        elif hat == "beret":
            ctx.save()
            ctx.scale(1.0, 0.42)
            ctx.arc(4, -18, 38, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
            ctx.arc(6, -22, 6, 0, 2 * math.pi)
            ctx.fill()
        elif hat == "top":
            rrect(ctx, -36, -2, 72, 9, 4)
            ctx.fill()
            rrect(ctx, -22, -46, 44, 46, 4)
            ctx.fill()
        ctx.restore()
    # chest emblem cut-out
    if emblem:
        ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        shape(ctx, emblem, 0, -112, 20 * clamp(emblem_k, 0, 2), 1.0, True,
              morph_to=emblem_to, k=emblem_morph, color=0)
        ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(clamp(a))
    ctx.restore()


def head_pos(x, gy, s=1.0, look=0.0):
    return x + look * 9 * s, gy - 204 * s


def chest_pos(x, gy, s=1.0):
    return x, gy - 112 * s


# ---------------------------------------------------------------- props -----
def bulb(ctx, x, y, s, lit, a=1.0):
    """Light bulb; lit 0..1."""
    if a <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if lit > 0.01:
        for i in range(8):
            ang = i * math.pi / 4
            r0, r1 = 52, 52 + 22 * lit
            ctx.move_to(math.cos(ang) * r0, -8 + math.sin(ang) * r0)
            ctx.line_to(math.cos(ang) * r1, -8 + math.sin(ang) * r1)
        white(ctx, a * lit)
        ctx.set_line_width(5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.arc(0, -8, 34, math.pi * 0.78, math.pi * 2.22)
    ctx.line_to(14, 40)
    ctx.line_to(-14, 40)
    ctx.close_path()
    if lit > 0.01:
        white(ctx, a * lit)
        ctx.fill_preserve()
    white(ctx, a)
    ctx.set_line_width(4)
    ctx.stroke()
    for i in range(2):
        rrect(ctx, -15, 46 + i * 10, 30, 6, 3)
        white(ctx, a)
        ctx.fill()
    ctx.restore()


def flame(ctx, x, y, s, t, a=1.0):
    if a <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    # logs
    for d in (1, -1):
        ctx.move_to(-55 * d, 8)
        ctx.line_to(55 * d, -8)
    white(ctx, a * 0.8)
    ctx.set_line_width(12)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    for layer, (hh, ww, al) in enumerate(((120, 46, 0.55), (82, 30, 0.85), (46, 16, 1.0))):
        f = 1 + 0.12 * math.sin(t * 11 + layer * 2) + 0.06 * math.sin(t * 23 + layer)
        sway = 8 * math.sin(t * 7 + layer)
        h = hh * f
        ctx.move_to(-ww, -6)
        ctx.curve_to(-ww * 1.1, -h * 0.45, sway - ww * 0.3, -h * 0.7, sway, -h)
        ctx.curve_to(sway + ww * 0.3, -h * 0.7, ww * 1.1, -h * 0.45, ww, -6)
        ctx.close_path()
        white(ctx, a * al)
        ctx.fill()
    ctx.restore()
    # sparks
    for i in range(10):
        ph = (t * 0.5 + hash01(i, 3)) % 1.0
        sx = x + (hash01(i, 5) - 0.5) * 80 * s + math.sin(t * 3 + i) * 12
        sy = y - (60 + ph * 260) * s
        white(ctx, a * (1 - ph) * 0.8)
        ctx.arc(sx, sy, 2.4, 0, 2 * math.pi)
        ctx.fill()


def brain_geometry(seed=7):
    """Return (outline, gyri list) as polylines, centred at 0,0, ~440x330."""
    rng = np.random.default_rng(seed)
    th = np.linspace(0, 2 * np.pi, 400)
    rx, ry = 230, 165
    bump = 1 + 0.035 * np.sin(th * 11) + 0.02 * np.sin(th * 17 + 1.3)
    x = np.cos(th) * rx * bump
    y = -np.sin(th) * ry * bump
    # flatten the bottom slightly, frontal lobe a little fuller
    y = np.where(y > 0, y * 0.78, y)
    x = np.where(x > 0, x * 1.04, x)
    outline = np.stack([x, y], 1)
    gyri = []
    # central sulcus + lateral fissure
    gyri.append(np.array([[20, -160], [5, -100], [30, -40], [10, 20], [25, 70]], float))
    gyri.append(np.array([[-150, 40], [-60, 30], [40, 55], [140, 40]], float))
    placed = 0
    while placed < 13:
        cx = rng.uniform(-185, 185)
        cy = rng.uniform(-125, 85)
        if (cx / 195) ** 2 + (cy / 135) ** 2 > 0.62:
            continue
        r = rng.uniform(22, 40)
        a0 = rng.uniform(0, 2 * np.pi)
        span = rng.uniform(2.0, 3.4)
        th2 = np.linspace(a0, a0 + span, 24)
        gyri.append(np.stack([cx + np.cos(th2) * r * 1.3, cy + np.sin(th2) * r], 1))
        placed += 1
    # smooth the hand-placed fissures
    def smooth(p, n=40):
        p = np.asarray(p, float)
        s = np.linspace(0, len(p) - 1, n)
        i0 = np.floor(s).astype(int).clip(0, len(p) - 2)
        k = (s - i0)[:, None]
        k = k * k * (3 - 2 * k)
        return p[i0] * (1 - k) + p[i0 + 1] * k
    gyri[0] = smooth(gyri[0])
    gyri[1] = smooth(gyri[1])
    thc = np.linspace(-0.2, np.pi + 0.2, 80)
    cereb = np.stack([140 + np.cos(thc) * 62, 112 + np.sin(thc) * 34], 1)
    stem = np.array([[60, 118], [70, 170], [82, 215]], float)
    return outline, gyri, cereb, stem


_BRAIN = brain_geometry()


def brain(ctx, x, y, s, draw=1.0, a=1.0, jitter=0.0, t=0.0, inner=1.0):
    outline, gyri, cereb, stem = _BRAIN

    def tf(p):
        p = p.copy()
        if jitter > 0:
            p = p + np.stack([np.sin(p[:, 1] * 0.08 + t * 37),
                              np.cos(p[:, 0] * 0.08 + t * 41)], 1) * jitter
        return p * s + np.array([x, y])
    polyline(ctx, tf(stem), draw, 5, a * 0.8)
    polyline(ctx, tf(cereb), draw, 4, a * 0.85)
    polyline(ctx, tf(outline), draw, 5.5, a)
    for i, g in enumerate(gyri):
        polyline(ctx, tf(g), clamp(draw * 1.6 - i * 0.04), 3.2, a * 0.75 * inner)


def board(ctx, x, y, w, h, a=1.0, draw=1.0):
    """Reference-style glowing rounded frame."""
    if a <= 0.001:
        return
    rrect(ctx, x, y, w, h, 18)
    black(ctx, a * 0.85)
    ctx.fill()
    ctx.set_line_width(4)
    perim = 2 * (w + h)
    ctx.set_dash([perim * draw, perim * 2])
    rrect(ctx, x, y, w, h, 18)
    white(ctx, a)
    ctx.stroke()
    ctx.set_dash([])


def mirror(ctx, x, gy, w, h, a=1.0, bright=0.0):
    if a <= 0.001:
        return
    y = gy - h
    g = cairo.LinearGradient(x - w / 2, y, x + w / 2, gy)
    g.add_color_stop_rgba(0, 1, 1, 1, (0.04 + 0.10 * bright) * a)
    g.add_color_stop_rgba(0.5, 1, 1, 1, (0.02 + 0.05 * bright) * a)
    g.add_color_stop_rgba(1, 1, 1, 1, (0.05 + 0.12 * bright) * a)
    rrect(ctx, x - w / 2, y, w, h, w / 2)
    ctx.set_source(g)
    ctx.fill()
    rrect(ctx, x - w / 2, y, w, h, w / 2)
    white(ctx, a)
    ctx.set_line_width(5)
    ctx.stroke()
    # sheen
    ctx.move_to(x - w * 0.22, y + h * 0.22)
    ctx.line_to(x - w * 0.05, y + h * 0.12)
    ctx.move_to(x - w * 0.24, y + h * 0.32)
    ctx.line_to(x + w * 0.02, y + h * 0.17)
    white(ctx, a * (0.25 + 0.5 * bright))
    ctx.set_line_width(4)
    ctx.stroke()
    # stand
    ctx.move_to(x - w * 0.42, gy + 2)
    ctx.line_to(x + w * 0.42, gy + 2)
    white(ctx, a)
    ctx.set_line_width(6)
    ctx.stroke()
