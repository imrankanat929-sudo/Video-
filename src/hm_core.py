"""HUMAN MIND — core 2D engine: easing, camera, glow compositing, rigged stickman, props."""
import math
import numpy as np
import cairo
from PIL import Image
from scipy.ndimage import gaussian_filter

W, H, FPS = 1920, 1080, 30


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def sm(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ein(x):
    x = clamp(x)
    return x ** 3


def back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, a, b, f=ease):
    if b <= a:
        return float(t >= a)
    return f((t - a) / (b - a))


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


def window(t, a, b, fi=0.4, fo=0.4):
    """0→1→0 envelope: fade in at a, fade out ending at b."""
    return min(prog(t, a, a + fi, sm), 1 - prog(t, b - fo, b, sm))


# ---------------------------------------------------------------- camera
def apply_cam(ctx, cx, cy, z, rot=0.0):
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    if rot:
        ctx.rotate(rot)
    ctx.translate(-cx, -cy)


def cam_blend(keys, t):
    """keys: list of (time, (cx,cy,z[,rot])) — eased interpolation between keys."""
    if t <= keys[0][0]:
        k = keys[0][1]
    elif t >= keys[-1][0]:
        k = keys[-1][1]
    else:
        for (t0, a), (t1, b) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                u = ease((t - t0) / (t1 - t0))
                # zoom interpolated geometrically for smooth dolly feel
                k = [lerp(a[i], b[i], u) for i in range(len(a))]
                k[2] = math.exp(lerp(math.log(a[2]), math.log(b[2]), u))
                break
    k = list(k) + [0.0] * (4 - len(k))
    return k


# ---------------------------------------------------------------- background / compositing
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H * 0.46) / (H * 0.70)) ** 2)
VIGNETTE = (0.055 * np.clip(1 - _r, 0, 1) ** 1.6 + 0.012).astype(np.float32)
del _yy, _xx, _r

_DOT = 46
_dots = np.zeros((H + 2 * _DOT, W + 2 * _DOT), np.float32)
for yy in range(_DOT // 2, _dots.shape[0], _DOT):
    for xx in range(_DOT // 2, _dots.shape[1], _DOT):
        _dots[yy:yy + 2, xx:xx + 2] = 1.0
DOTS = gaussian_filter(_dots, 0.6) * 0.55

_rng = np.random.default_rng(7)
GRAIN = [(_rng.standard_normal((H, W)).astype(np.float32) * (1.3 / 255)) for _ in range(6)]
PART = _rng.random((90, 5))  # x, y, size, speed, phase


def background(cam, t, dots=1.0):
    cx, cy, z, _ = cam
    ox = int((cx * z * 0.12) % _DOT)
    oy = int((cy * z * 0.12) % _DOT)
    d = DOTS[oy:oy + H, ox:ox + W]
    return VIGNETTE + d * 0.075 * dots * (0.5 + VIGNETTE * 9)


def draw_particles(ctx, t, cam, alpha=1.0):
    cx, cy, z, _ = cam
    for i, (px, py, s, sp, ph) in enumerate(PART):
        par = 0.25 + s * 0.5
        x = (px * (W + 200) - cx * z * par * 0.3 + t * (6 + sp * 10)) % (W + 200) - 100
        y = (py * (H + 200) - cy * z * par * 0.3 - t * (4 + sp * 12)) % (H + 200) - 100
        a = (0.10 + 0.22 * s) * (0.6 + 0.4 * math.sin(t * (0.6 + sp) + ph * 6.28)) * alpha
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.arc(x, y, 0.7 + s * 1.6, 0, 6.2832)
        ctx.fill()


def new_layer():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    return s, c


def layer_arrays(surf):
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    lum = a[:, :, 2].astype(np.float32) * (1 / 255)
    alp = a[:, :, 3].astype(np.float32) * (1 / 255)
    return lum, alp


def _resize(arr, w, h):
    return np.asarray(Image.fromarray(arr).resize((w, h), Image.BILINEAR))


def glow(lum, s1=3.0, s2=7.0):
    q = lum.reshape(H // 4, 4, W // 4, 4).mean(axis=(1, 3))
    g1 = gaussian_filter(q, s1)
    q2 = q.reshape(H // 8, 2, W // 8, 2).mean(axis=(1, 3))
    g2 = gaussian_filter(q2, s2)
    return _resize(g1, W, H) * 0.85 + _resize(g2, W, H) * 1.25


def tonemap(x):
    # gentle shoulder so glows bloom without clipping harshly
    return np.where(x < 0.8, x, 0.8 + 0.2 * np.tanh((x - 0.8) / 0.2))


# ---------------------------------------------------------------- text
def font(ctx, size, weight="Inter Medium"):
    ctx.select_font_face(weight, 0, 0)
    ctx.set_font_size(size)


def text_width(ctx, s, tracking=0.0):
    if not tracking:
        return ctx.text_extents(s).x_advance
    return sum(ctx.text_extents(ch).x_advance for ch in s) + tracking * (len(s) - 1)


def draw_text(ctx, s, x, y, size, weight="Inter Medium", align="c", tracking=0.0, rgba=(1, 1, 1, 1)):
    font(ctx, size, weight)
    w = text_width(ctx, s, tracking)
    x0 = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    ctx.set_source_rgba(*rgba)
    if not tracking:
        ctx.move_to(x0, y)
        ctx.show_text(s)
    else:
        for ch in s:
            ctx.move_to(x0, y)
            ctx.show_text(ch)
            x0 += ctx.text_extents(ch).x_advance + tracking
    return w


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def pill(ctx, s, x, y, size=26, alpha=1.0, tracking=3.0, filled=True):
    """Rounded label like the channel's tags: white pill, dark letters."""
    font(ctx, size, "Inter SemiBold")
    w = text_width(ctx, s, tracking)
    ph, pw = size * 1.9, w + size * 1.6
    rrect(ctx, x - pw / 2, y - ph / 2, pw, ph, ph / 2)
    if filled:
        ctx.set_source_rgba(1, 1, 1, 0.95 * alpha)
        ctx.fill()
        col = (0.06, 0.06, 0.06, alpha)
    else:
        ctx.set_source_rgba(1, 1, 1, 0.85 * alpha)
        ctx.set_line_width(2)
        ctx.stroke()
        col = (1, 1, 1, alpha)
    draw_text(ctx, s, x, y + size * 0.36, size, "Inter SemiBold", "c", tracking, col)


# ---------------------------------------------------------------- stickman
L = dict(r=21, neck=8, torso=70, ua=40, fa=38, th=50, sh=50)
LEG = L["th"] + L["sh"]
STAND_Y = -(LEG - 2)  # hip height when standing on ground y=0


def _ik(root, target, a, b, pref):
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy)
    d = min(max(d, abs(a - b) + 1e-3), a + b - 1e-3)
    base = math.atan2(dy, dx)
    al = math.acos(clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1))
    c1 = (root[0] + a * math.cos(base + al), root[1] + a * math.sin(base + al))
    c2 = (root[0] + a * math.cos(base - al), root[1] + a * math.sin(base - al))
    j = c1 if (c1[0] - c2[0]) * pref[0] + (c1[1] - c2[1]) * pref[1] > 0 else c2
    end = (root[0] + d * math.cos(base), root[1] + d * math.sin(base))
    return j, end


def _fk(p, ang, ln):
    return (p[0] + ln * math.sin(ang), p[1] + ln * math.cos(ang))


def joints(P):
    """P: x,y (hip), face (±1, may pass through 0 when turning), lean, head,
    arm_n/arm_f (shoulder, elbow) angles, hand_n/hand_f world targets,
    leg_n/leg_f angles (hip, knee) or foot_n/foot_f world targets."""
    hx, hy = P["x"], P["y"]
    f = P.get("face", 1.0)
    sg = 1.0 if f >= 0 else -1.0
    lean = P.get("lean", 0.0)
    hd = P.get("head", 0.0)
    up = (math.sin(lean), -math.cos(lean))
    sh = (up[0] * L["torso"], up[1] * L["torso"])
    nk = (sh[0] + up[0] * L["neck"], sh[1] + up[1] * L["neck"])
    hc = (nk[0] + math.sin(lean + hd) * L["r"], nk[1] - math.cos(lean + hd) * L["r"])
    J = {"hip": (0.0, 0.0), "sh": sh, "nk": nk, "head": hc}

    def loc(p):
        return ((p[0] - hx) * sg, p[1] - hy)

    for s in ("n", "f"):
        if P.get("hand_" + s) is not None:
            e, h = _ik(sh, loc(P["hand_" + s]), L["ua"], L["fa"], P.get("elbow_" + s, (-0.3, 1)))
        else:
            a1, a2 = P.get("arm_" + s, (0.12 if s == "n" else -0.12, 0.15))
            # absolute angles: 0 = hanging down, pi/2 = pointing forward, pi = up
            e = _fk(sh, a1, L["ua"])
            h = _fk(e, a1 + a2, L["fa"])
        J["el_" + s], J["ha_" + s] = e, h
        if P.get("foot_" + s) is not None:
            k, ft = _ik((0, 0), loc(P["foot_" + s]), L["th"], L["sh"], (1, 0))
        else:
            h1, k1 = P.get("leg_" + s, (0.06 if s == "n" else -0.06, 0.0))
            k = (L["th"] * math.sin(h1), L["th"] * math.cos(h1))
            ft = (k[0] + L["sh"] * math.sin(h1 - k1), k[1] + L["sh"] * math.cos(h1 - k1))
        J["kn_" + s], J["ft_" + s] = k, ft
    out = {}
    for k, (x, y) in J.items():
        out[k] = (hx + x * f, hy + y)
    return out


def draw_figure(ctx, P, alpha=1.0, bright=1.0, far=0.52):
    J = joints(P)
    sc = P.get("scale", 1.0)
    if sc != 1.0:
        ox, oy = P["x"], P["y"]
        J = {k: (ox + (x - ox) * sc, oy + (y - oy) * sc) for k, (x, y) in J.items()}
    ctx.push_group()
    lw = 12.5 * sc

    def seg(pts, w, g):
        ctx.set_source_rgb(g, g, g)
        ctx.set_line_width(w)
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.stroke()

    seg([J["sh"], J["el_f"], J["ha_f"]], lw, far * bright)
    seg([J["hip"], J["kn_f"], J["ft_f"]], lw, far * bright)
    seg([J["hip"], J["kn_n"], J["ft_n"]], lw, bright)
    seg([J["hip"], J["sh"]], 21 * sc, bright)
    seg([J["sh"], J["nk"]], 10 * sc, bright)
    ctx.set_source_rgb(bright, bright, bright)
    ctx.arc(J["head"][0], J["head"][1], L["r"] * sc, 0, 6.2832)
    ctx.fill()
    seg([J["sh"], J["el_n"], J["ha_n"]], lw, bright)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    return J


def stand(x, face=1.0, lean=0.0, head=0.0, t=0.0, breathe=1.0, **kw):
    P = dict(x=x, y=STAND_Y + math.sin(t * 1.7) * 1.2 * breathe, face=face, lean=lean, head=head,
             foot_n=(x + 9 * face, 0), foot_f=(x - 9 * face, 0),
             arm_n=(0.10 + 0.02 * math.sin(t * 1.7), 0.12), arm_f=(-0.10, 0.12))
    P.update(kw)
    return P


def gait(F, s, lift=14.0):
    """Footholds F alternate near/far (F[0] near). Returns (near_foot, far_foot, u, k)."""
    s = clamp(s, 0, len(F) - 2 - 1e-6)
    k = int(math.floor(s))
    u = s - k
    feet = {}
    for par in (0, 1):
        if k % 2 == par:
            a, b = F[k], F[k + 2]
            ux, uy = ease(u), sm(min(1.0, u * 1.5)) if b[1] < a[1] else ease(u)
            p = (lerp(a[0], b[0], ux), lerp(a[1], b[1], uy) - lift * math.sin(math.pi * u))
        else:
            p = F[k + 1]
        feet[par] = p
    return feet[0], feet[1], u, k


def walk_pose(F, s, face=1.0, lean=0.04, head=0.0, lift=14.0, swing=0.42):
    fn, ff, u, k = gait(F, s, lift)
    x = (fn[0] + ff[0]) / 2 + 6 * face
    y_des = min(fn[1], ff[1]) * 0.55 + max(fn[1], ff[1]) * 0.45 - (LEG - 6) - 3 * math.sin(math.pi * u)
    y = y_des
    for p in (fn, ff):  # keep both feet reachable
        dx = abs(p[0] - x)
        y = max(y, p[1] - math.sqrt(max(0.0, (LEG - 1.5) ** 2 - dx * dx)))
    ph = math.cos(math.pi * s)
    return dict(x=x, y=y, face=face, lean=lean, head=head, foot_n=fn, foot_f=ff,
                arm_n=(-swing * ph, 0.25 + 0.1 * abs(ph)), arm_f=(swing * ph, 0.25 + 0.1 * abs(ph)))


def flat_holds(x0, n, stride, face=1.0, y=0.0):
    F = [(x0 + 8 * face, y), (x0 - 8 * face, y)]
    for i in range(n):
        F.append((x0 + face * (stride * (i + 1) + (8 if i % 2 == 0 else -8)), y))
    return F


def sit_pose(x, seat_y, lean=0.12, head=0.1, foot_dx=48, **kw):
    """Sitting on a seat (seat top at seat_y), facing right; feet on floor y=0."""
    P = dict(x=x, y=seat_y - 6, face=1.0, lean=lean, head=head,
             foot_n=(x + foot_dx, 0), foot_f=(x + foot_dx - 12, 0),
             arm_n=(0.35, 0.6), arm_f=(0.25, 0.6))
    P.update(kw)
    return P


# ---------------------------------------------------------------- props
def stroke(ctx, w=3.0, g=1.0, a=1.0):
    ctx.set_source_rgba(g, g, g, a)
    ctx.set_line_width(w)
    ctx.stroke()


def dashed_ground(ctx, x0, x1, y=0.0, a=0.55, w=2.5, dash=(22, 16)):
    ctx.set_dash(list(dash))
    ctx.move_to(x0, y)
    ctx.line_to(x1, y)
    stroke(ctx, w, 1, a)
    ctx.set_dash([])


def light_pool(ctx, x, y, r, a=0.07):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a)
    g.add_color_stop_rgba(0.5, 1, 1, 1, a * 0.35)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 6.2832)
    ctx.fill()


def orb(ctx, x, y, r, t, a=1.0):
    light_pool(ctx, x, y, r * 7, 0.10 * a)
    light_pool(ctx, x, y, r * 3, 0.28 * a)
    pul = 1 + 0.06 * math.sin(t * 2.2)
    ctx.set_source_rgba(1, 1, 1, a)
    ctx.arc(x, y, r * pul, 0, 6.2832)
    ctx.fill()


def stairs_path(ctx, x0, y0, n, w, h, close=True):
    ctx.move_to(x0, y0)
    for i in range(n):
        ctx.line_to(x0 + i * w, y0 - (i + 1) * h)
        ctx.line_to(x0 + (i + 1) * w, y0 - (i + 1) * h)
    if close:
        ctx.line_to(x0 + n * w, y0)
        ctx.close_path()


def draw_stairs(ctx, x0, y0, n, w, h, lit=None, a=1.0, lw=3.0, glow_steps=True):
    top = y0 - n * h
    g = cairo.LinearGradient(0, top, 0, y0)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.07 * a)
    g.add_color_stop_rgba(1, 1, 1, 1, 0.015 * a)
    stairs_path(ctx, x0, y0, n, w, h)
    ctx.set_source(g)
    ctx.fill()
    stairs_path(ctx, x0, y0, n, w, h, close=False)
    stroke(ctx, lw, 1, 0.9 * a)
    ctx.move_to(x0 + n * w, top)
    ctx.line_to(x0 + n * w, y0)
    stroke(ctx, lw * 0.6, 1, 0.25 * a)
    if lit is not None:
        for i, v in enumerate(lit):
            if v <= 0.01:
                continue
            sx, sy = x0 + i * w, y0 - (i + 1) * h
            if glow_steps:
                light_pool(ctx, sx + w / 2, sy, w * 0.9, 0.10 * v * a)
            ctx.move_to(sx + 4, sy)
            ctx.line_to(sx + w - 4, sy)
            stroke(ctx, lw * 2.0, 1, v * a)


def stair_top(x0, y0, w, h, i):
    return (x0 + i * w + w / 2, y0 - (i + 1) * h)


# icons — line drawings centred at (x,y), size s
def icon(ctx, kind, x, y, s, a=1.0, lw=None):
    lw = lw or max(2.0, s * 0.07)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s / 100, s / 100)
    lw2 = lw * 100 / s
    if kind == "book":
        ctx.move_to(0, -28); ctx.curve_to(-18, -38, -38, -36, -46, -30); ctx.line_to(-46, 32)
        ctx.curve_to(-38, 26, -18, 24, 0, 34); ctx.curve_to(18, 24, 38, 26, 46, 32); ctx.line_to(46, -30)
        ctx.curve_to(38, -36, 18, -38, 0, -28); ctx.line_to(0, 34)
    elif kind == "bulb":
        ctx.arc(0, -10, 30, math.radians(135), math.radians(45))
        ctx.line_to(14, 26); ctx.line_to(-14, 26); ctx.close_path()
        ctx.move_to(-12, 36); ctx.line_to(12, 36); ctx.move_to(-7, 45); ctx.line_to(7, 45)
    elif kind == "check":
        rrect(ctx, -38, -38, 76, 76, 14)
        ctx.move_to(-18, 0); ctx.line_to(-5, 14); ctx.line_to(20, -14)
    elif kind == "star":
        for i in range(11):
            r = 44 if i % 2 == 0 else 19
            an = -math.pi / 2 + i * math.pi / 5
            (ctx.line_to if i else ctx.move_to)(r * math.cos(an), r * math.sin(an))
        ctx.close_path()
    elif kind == "dumbbell":
        ctx.move_to(-30, 0); ctx.line_to(30, 0)
        for sx in (-1, 1):
            rrect(ctx, sx * 30 - 7, -24, 14, 48, 5)
            rrect(ctx, sx * 44 - 5, -15, 10, 30, 4)
    elif kind == "pencil":
        ctx.move_to(-36, 30); ctx.line_to(-30, 14); ctx.line_to(22, -38); ctx.line_to(36, -24)
        ctx.line_to(-16, 28); ctx.close_path(); ctx.move_to(-30, 14); ctx.line_to(-16, 28)
    elif kind == "brain":
        ctx.arc(-14, -8, 22, math.pi * 0.6, math.pi * 1.9)
        ctx.arc(14, -8, 22, math.pi * 1.1, math.pi * 2.4)
        ctx.move_to(-34, 4); ctx.curve_to(-30, 30, 30, 30, 34, 4)
        ctx.move_to(0, -28); ctx.line_to(0, 22)
    ctx.restore()
    ctx.set_source_rgba(1, 1, 1, a)
    ctx.set_line_width(lw)
    ctx.stroke()


def book_closed(ctx, x, y, w=96, h=18, a=1.0):
    rrect(ctx, x - w / 2, y - h, w, h, 3)
    ctx.set_source_rgba(1, 1, 1, 0.10 * a)
    ctx.fill_preserve()
    stroke(ctx, 2.5, 1, 0.9 * a)
    ctx.move_to(x - w / 2 + 8, y - h / 2)
    ctx.line_to(x + w / 2 - 4, y - h / 2)
    stroke(ctx, 1.5, 1, 0.45 * a)


def book_open(ctx, x, y, w=70, a=1.0, turn=None):
    """Open book seen from the side-ish: two pages forming a shallow V, centred at spine (x,y)."""
    for sx in (-1, 1):
        ctx.move_to(x, y)
        ctx.curve_to(x + sx * w * 0.3, y - 10, x + sx * w * 0.7, y - 12, x + sx * w, y - 6)
        ctx.line_to(x + sx * w, y + 4)
        ctx.curve_to(x + sx * w * 0.7, y - 2, x + sx * w * 0.3, y, x, y + 8)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.92 * a)
        ctx.fill()
    if turn is not None and 0 < turn < 1:
        an = math.pi * ease(turn)
        px = x + w * math.cos(an)
        py = y - 6 - w * 0.55 * math.sin(an)
        ctx.move_to(x, y)
        ctx.curve_to(x + (px - x) * 0.4, py - 8, px, py, px, py)
        stroke(ctx, 3, 1, 0.85 * a)
