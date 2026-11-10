"""Parametric 2D character rig (flat style, matches the character sheet)."""
import math
import cairo
from core import (hexc, setc, ellipse, rrect, lerp, clamp, shade, mix)

R = 82.0  # head radius in local units (feet at y=0, up is negative)
HEAD_Y = -578.0
NECK_TOP = -500.0
SHOULDER_Y = -470.0
HIP_Y = -292.0

BOY = dict(
    skin=hexc('#c9a07a'), hair=hexc('#111114'), hair_style='messy',
    top=hexc('#26282e'), top_style='sweater', pants=hexc('#1b1d23'),
    shoes=hexc('#b9b9bb'), brow=hexc('#141416'), scale=1.0, width=1.0,
    extras=(),
)
MOM = dict(
    skin=hexc('#d2a983'), hair=hexc('#3e2a20'), hair_style='bob',
    top=hexc('#6a4a55'), top_style='cardigan', inner=hexc('#d9cfc2'),
    pants=hexc('#2e2b33'), shoes=hexc('#5a4a44'), brow=hexc('#2d1e17'),
    scale=1.04, width=0.97, extras=('earrings',),
)
DAD = dict(
    skin=hexc('#c29673'), hair=hexc('#3a3633'), hair_style='short',
    top=hexc('#3f5165'), top_style='shirt', inner=hexc('#3f5165'),
    pants=hexc('#2a2c33'), shoes=hexc('#3a3330'), brow=hexc('#2a2624'),
    scale=1.1, width=1.12, extras=('glasses', 'mustache'),
)

EXPR = {
    #            brow_dy tilt  asym eye_sy white lid  smile open  mw   teeth sweat
    'neutral':  (0.00,  0.00, 0.0, 1.00, 0.0, 0.00, 0.00, 0.00, 0.16, 0, 0),
    'calm':     (0.02,  0.00, 0.0, 1.00, 0.0, 0.10, 0.05, 0.00, 0.14, 0, 0),
    'smile':    (-0.02, 0.05, 0.0, 1.00, 0.0, 0.05, 0.45, 0.05, 0.22, 0, 0),
    'grin':     (-0.04, 0.05, 0.0, 0.95, 0.0, 0.10, 0.60, 0.35, 0.26, 1, 0),
    'surprised': (-0.10, 0.10, 0.0, 1.18, 0.0, 0.00, 0.00, 0.30, 0.09, 0, 0),
    'confused': (-0.04, 0.00, 0.12, 1.05, 0.0, 0.00, -0.10, 0.00, 0.12, 0, 0),
    'worried':  (-0.04, 0.45, 0.0, 1.05, 0.0, 0.00, -0.30, 0.02, 0.14, 0, 0),
    'sad':      (0.00,  0.55, 0.0, 0.95, 0.0, 0.25, -0.40, 0.00, 0.14, 0, 0),
    'scared':   (-0.12, 0.55, 0.0, 1.22, 0.0, 0.00, -0.25, 0.55, 0.17, 1, 1),
    'shock':    (-0.16, 0.40, 0.0, 1.30, 1.0, 0.00, -0.10, 0.70, 0.12, 0, 1),
    'stern':    (0.04, -0.35, 0.0, 0.95, 0.0, 0.20, -0.15, 0.00, 0.15, 0, 0),
    'puzzled':  (-0.06, 0.15, 0.20, 1.08, 0.0, 0.00, -0.12, 0.08, 0.10, 0, 0),
    'creepy':   (0.06, -0.45, 0.0, 0.85, 0.0, 0.48, 0.95, 0.30, 0.34, 1, 0),
    'talk':     (0.00,  0.00, 0.0, 1.00, 0.0, 0.00, 0.05, 0.25, 0.14, 0, 0),
}
EKEYS = ('brow_dy', 'tilt', 'asym', 'eye_sy', 'white', 'lid', 'smile', 'open', 'mw', 'teeth', 'sweat')


def expr(name_or_mix):
    """'scared' or [('scared',0.3),('shock',0.7)] -> param dict"""
    if isinstance(name_or_mix, dict):
        return name_or_mix
    if isinstance(name_or_mix, str):
        return dict(zip(EKEYS, EXPR[name_or_mix]))
    out = dict.fromkeys(EKEYS, 0.0)
    for name, w in name_or_mix:
        for k, v in zip(EKEYS, EXPR[name]):
            out[k] += v * w
    return out


def expr_blend(a, b, t):
    ea, eb = expr(a), expr(b)
    return {k: lerp(ea[k], eb[k], clamp(t)) for k in EKEYS}


# ------------------------------------------------------------------ hair
MESSY_CAP = [(-1.00, 0.14), (-1.20, -0.04), (-1.06, -0.24), (-1.28, -0.44), (-1.06, -0.62),
             (-1.16, -0.88), (-0.84, -0.94), (-0.86, -1.16), (-0.52, -1.10), (-0.40, -1.34),
             (-0.14, -1.16), (0.10, -1.36), (0.26, -1.14), (0.56, -1.26), (0.66, -1.04),
             (0.98, -1.06), (0.94, -0.80), (1.26, -0.72), (1.08, -0.50), (1.28, -0.30),
             (1.06, -0.12), (1.14, 0.08), (1.00, 0.16)]
MESSY_FRINGE = [(0.96, 0.06), (0.88, -0.20), (0.74, -0.10), (0.58, -0.40), (0.42, -0.26),
                (0.22, -0.48), (0.05, -0.30), (-0.15, -0.52), (-0.31, -0.33), (-0.50, -0.50),
                (-0.64, -0.27), (-0.82, -0.38), (-0.94, -0.06)]


def _arc_pts(a0, a1, r, n=24, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def hair_poly(style, turn):
    ta = abs(turn)
    sg = 1 if turn >= 0 else -1
    if style == 'messy':
        cap, fr = MESSY_CAP, MESSY_FRINGE
        back = [(-0.80, 0.30 + 0.35 * ta), (-1.08, 0.12 + 0.15 * ta)]
    elif style == 'bob':
        cap = [(-1.10, 0.62)] + _arc_pts(175, 365, 1.13) + [(1.12, 0.62)]
        fr = [(0.98, 0.62), (0.92, -0.05), (0.62, -0.42), (0.15, -0.58), (-0.35, -0.50),
              (-0.80, -0.18), (-0.95, 0.62)]
        back = [(-0.9, 0.7 + 0.1 * ta)]
    elif style == 'short':
        cap = _arc_pts(185, 355, 1.07)
        fr = [(1.0, -0.15), (0.80, -0.42), (0.45, -0.60), (0.0, -0.66), (-0.45, -0.60),
              (-0.80, -0.42), (-1.0, -0.15)]
        back = [(-0.75, 0.25 * ta), (-1.04, -0.05)]
    elif style == 'bun':
        cap = _arc_pts(180, 360, 1.08)
        fr = [(1.0, -0.05), (0.6, -0.48), (0.0, -0.62), (-0.6, -0.48), (-1.0, -0.05)]
        back = [(-0.85, 0.3 * ta)]
    elif style == 'cap':
        cap = _arc_pts(185, 355, 1.09)
        fr = [(1.0, -0.15), (0.6, -0.40), (0.0, -0.44), (-0.6, -0.40), (-1.0, -0.15)]
        back = [(-0.9, 0.25 * ta)]
    else:
        return []
    out = []
    for x, y in back:
        out.append((x * (1 - 0.2 * ta) - 0.12 * ta, y) if ta > 0.05 else None)
    out = [p for p in out if p]
    out += [(x * (1 - 0.22 * ta) - 0.12 * ta, y) for x, y in cap]
    out += [(x * (1 - 0.42 * ta) + 0.32 * ta, y) for x, y in fr]
    if ta > 0.3 and style in ('messy', 'short', 'cap', 'bun'):
        k = (ta - 0.3) / 0.7
        out.append((lerp(-0.6, -0.12, k), lerp(-0.1, 0.32, k)))
        out.append((lerp(-0.8, -0.45, k), lerp(0.1, 0.62, k)))
    if sg < 0:
        out = [(-x, y) for x, y in out]
    return out


def draw_poly(ctx, pts, s=1.0, smooth=False):
    if not smooth:
        ctx.move_to(pts[0][0] * s, pts[0][1] * s)
        for x, y in pts[1:]:
            ctx.line_to(x * s, y * s)
        ctx.close_path()
        return
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    conv = []
    for i in range(n):
        ax, ay = pts[i - 1]; bx, by = pts[i]; cx, cy = pts[(i + 1) % n]
        cr = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        conv.append(cr * area < 0)
    if not any(conv):
        conv = [True] * n
    i0 = conv.index(True)
    order = [(i0 + k) % n for k in range(n)] + [i0]
    ctx.move_to(pts[i0][0] * s, pts[i0][1] * s)
    ctrl = []
    for idx in order[1:]:
        if conv[idx]:
            px, py = pts[idx]
            if ctrl:
                qx = sum(c[0] for c in ctrl) / len(ctrl); qy = sum(c[1] for c in ctrl) / len(ctrl)
                x0, y0 = ctx.get_current_point()
                ctx.curve_to(x0 + (qx * s - x0) * 0.8, y0 + (qy * s - y0) * 0.8,
                             px * s + (qx * s - px * s) * 0.8, py * s + (qy * s - py * s) * 0.8, px * s, py * s)
            else:
                ctx.line_to(px * s, py * s)
            ctrl = []
        else:
            ctrl.append(pts[idx])
    ctx.close_path()


# ------------------------------------------------------------------ head
def draw_head(ctx, look, p, e):
    e = expr(e)
    turn = p.get('turn', 0.0)
    skin = look['skin']
    ta = abs(turn)
    sg = 1 if turn >= 0 else -1
    ctx.save()
    # bun behind head
    if look['hair_style'] == 'bun':
        ellipse(ctx, -turn * 0.6 * R, -1.15 * R, 0.42 * R, 0.38 * R)
        setc(ctx, look['hair']); ctx.fill()
    # face
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    setc(ctx, skin); ctx.fill()
    # subtle cheek shade on back side
    g = cairo.LinearGradient(-R, 0, R, 0)
    sh = shade(skin, 0.82)
    g.add_color_stop_rgba(0, sh[0], sh[1], sh[2], 0.0 + 0.6 * (sg < 0) * ta + 0.15)
    g.add_color_stop_rgba(0.5, sh[0], sh[1], sh[2], 0.0)
    g.add_color_stop_rgba(1, sh[0], sh[1], sh[2], 0.0 + 0.6 * (sg > 0) * ta + 0.15)
    # flip so that the back side is darker
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()

    fx = turn * 0.44 * R  # feature shift
    look_dx, look_dy = p.get('look', (0.0, 0.0))
    blink = p.get('blink', 0.0)

    # blush
    if p.get('blush', 0) > 0:
        for side in (-1, 1):
            ellipse(ctx, fx + side * 0.48 * R, 0.30 * R, 0.13 * R, 0.07 * R)
            setc(ctx, hexc('#d9786a'), 0.35 * p['blush']); ctx.fill()

    # eyes
    eyes = []
    for side in (-1, 1):
        ex = fx + side * 0.29 * R * (1 - 0.35 * ta)
        far = (side == -sg) and ta > 0.05
        sq = 1 - (0.55 * ta if far else 0.1 * ta)
        if far and ta > 0.88:
            continue
        eyes.append((side, ex, sq))
    ey = 0.10 * R
    for side, ex, sq in eyes:
        rx = 0.12 * R * sq
        ry = 0.175 * R * e['eye_sy']
        cx = ex + look_dx * 0.06 * R
        cy = ey + look_dy * 0.05 * R
        lid = max(e['lid'], blink)
        if blink > 0.85:
            ctx.set_line_width(0.045 * R)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(cx - rx * 1.1, cy + 0.02 * R)
            ctx.line_to(cx + rx * 1.1, cy + 0.02 * R)
            setc(ctx, hexc('#141416')); ctx.stroke()
            continue
        if e['white'] > 0.02:
            w = e['white']
            ellipse(ctx, cx, cy, rx * (1 + 0.45 * w), ry * (1 + 0.15 * w))
            setc(ctx, hexc('#f2efe9'), w); ctx.fill_preserve()
            ctx.set_line_width(0.03 * R); setc(ctx, hexc('#141416'), w); ctx.stroke()
            ellipse(ctx, cx + look_dx * 0.04 * R, cy, rx * lerp(1.0, 0.38, w), ry * lerp(1.0, 0.35, w))
            setc(ctx, hexc('#121214')); ctx.fill()
        else:
            ellipse(ctx, cx, cy, rx, ry)
            setc(ctx, hexc('#121214')); ctx.fill()
            # highlight
            ellipse(ctx, cx + rx * 0.35, cy - ry * 0.45, rx * 0.28, ry * 0.2)
            setc(ctx, (1, 1, 1), 0.55); ctx.fill()
        if lid > 0.02:
            top = cy - ry * 1.05
            ctx.rectangle(cx - rx * 1.6, top - 0.2 * R, rx * 3.2, 0.2 * R + 2 * ry * lid)
            setc(ctx, skin); ctx.fill()
            ctx.set_line_width(0.04 * R)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(cx - rx * 1.25, top + 2 * ry * lid)
            ctx.line_to(cx + rx * 1.25, top + 2 * ry * lid)
            setc(ctx, hexc('#141416')); ctx.stroke()

    # mouth
    mw = e['mw'] * R * (1 - 0.3 * ta)
    mx = fx * 1.12
    my = 0.47 * R
    smile = e['smile']
    op = e['open'] + p.get('talk', 0.0)
    if mw > 1:
        cy_c = smile * 0.16 * R  # corners up for smile
        if op < 0.06:
            ctx.move_to(mx - mw, my - cy_c)
            ctx.curve_to(mx - mw * 0.4, my + cy_c * 0.6, mx + mw * 0.4, my + cy_c * 0.6, mx + mw, my - cy_c)
            ctx.set_line_width(0.045 * R)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            setc(ctx, hexc('#3b1818')); ctx.stroke()
        else:
            h = op * 0.32 * R
            ow = mw * (1 + 0.2 * op) if smile > 0.2 else max(mw, h * 0.75)
            ctx.move_to(mx - ow, my - cy_c)
            ctx.curve_to(mx - ow * 0.4, my + cy_c * 0.3 - h * 0.15, mx + ow * 0.4, my + cy_c * 0.3 - h * 0.15,
                         mx + ow, my - cy_c)
            ctx.curve_to(mx + ow * 0.6, my + h + cy_c * 0.4, mx - ow * 0.6, my + h + cy_c * 0.4,
                         mx - ow, my - cy_c)
            ctx.close_path()
            setc(ctx, hexc('#4a1a1c')); ctx.fill_preserve()
            ctx.save(); ctx.clip()
            ellipse(ctx, mx, my + h * 0.9, ow * 0.6, h * 0.45)
            setc(ctx, hexc('#a64a4c')); ctx.fill()
            if e['teeth'] > 0.5:
                ctx.rectangle(mx - ow, my - cy_c - 0.2 * R, ow * 2, 0.2 * R + h * 0.28 + cy_c * 0.3)
                setc(ctx, hexc('#efe8dc')); ctx.fill()
            ctx.restore()

    # hair
    pts = hair_poly(look['hair_style'], turn)
    if pts:
        draw_poly(ctx, pts, R)
        setc(ctx, look['hair']); ctx.fill_preserve()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_width(0.10 * R); ctx.stroke()
        if look['hair_style'] == 'messy':
            hl = shade(look['hair'], 1.08)
            ctx.set_line_width(0.035 * R)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            for (x0, y0, x1, y1) in [(-0.6, -0.95, -0.2, -0.6), (0.1, -1.05, 0.25, -0.65), (0.6, -0.9, 0.5, -0.55)]:
                x0 = x0 * (1 - 0.3 * ta) + 0.1 * turn; x1 = x1 * (1 - 0.3 * ta) + 0.2 * turn
                ctx.move_to(x0 * R, y0 * R); ctx.line_to(x1 * R, y1 * R)
            setc(ctx, hl, 0.9); ctx.stroke()
        if look['hair_style'] == 'short':
            # grey temples
            for side in (-1, 1):
                if side == -sg and ta > 0.6:
                    continue
                ellipse(ctx, (side * 0.93 - 0.1 * turn) * R, -0.18 * R, 0.1 * R, 0.2 * R)
                setc(ctx, hexc('#77716b'), 0.8); ctx.fill()
    if look['hair_style'] == 'cap':
        cc = look.get('cap', hexc('#2f3b2e'))
        ctx.arc(-0.05 * turn * R, -0.2 * R, 1.1 * R, math.pi, 2 * math.pi)
        ctx.close_path()
        setc(ctx, cc); ctx.fill()
        # visor
        vx = (0.25 + 0.75 * ta) * sg * R if ta > 0.1 else 0
        vw = lerp(1.05, 0.75, ta) * R
        ellipse(ctx, vx * 0.9 + turn * 0.2 * R, -0.22 * R, vw, 0.13 * R)
        setc(ctx, shade(cc, 0.8)); ctx.fill()

    # brows
    bc = look['brow']
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for side, ex, sq in eyes:
        bw = 0.17 * R * sq
        by = -0.20 * R + e['brow_dy'] * R - (e['asym'] * R if side < 0 else -e['asym'] * 0.4 * R)
        inner = -side  # inner end direction
        tilt = e['tilt'] * 0.11 * R
        x_in = ex + inner * bw
        x_out = ex - inner * bw
        ctx.move_to(x_out, by + tilt * 0.4)
        ctx.line_to(x_in, by - tilt)
        ctx.set_line_width(0.075 * R)
        setc(ctx, bc); ctx.stroke()

    # extras
    if 'glasses' in look['extras']:
        ctx.set_line_width(0.035 * R)
        for side, ex, sq in eyes:
            rrect(ctx, ex - 0.2 * R * sq, ey - 0.17 * R, 0.4 * R * sq, 0.32 * R, 0.08 * R)
            setc(ctx, hexc('#1c1c1f')); ctx.stroke()
        if len(eyes) == 2:
            ctx.move_to(eyes[0][1] + 0.2 * R * eyes[0][2], ey - 0.05 * R)
            ctx.line_to(eyes[1][1] - 0.2 * R * eyes[1][2], ey - 0.05 * R)
            ctx.stroke()
    if 'mustache' in look['extras']:
        ellipse(ctx, mx, my - 0.12 * R, 0.2 * R * (1 - 0.3 * ta), 0.06 * R)
        setc(ctx, look['hair']); ctx.fill()
    if 'earrings' in look['extras']:
        pass
    if e['sweat'] > 0.3 and p.get('sweat', True):
        sx = fx + sg * 0.62 * R if ta > 0.1 else 0.62 * R
        sy = -0.05 * R + (p.get('t', 0) * 20 % 30)
        ctx.move_to(sx, sy - 0.14 * R)
        ctx.curve_to(sx + 0.08 * R, sy, sx + 0.07 * R, sy + 0.08 * R, sx, sy + 0.08 * R)
        ctx.curve_to(sx - 0.07 * R, sy + 0.08 * R, sx - 0.08 * R, sy, sx, sy - 0.14 * R)
        setc(ctx, hexc('#a9c6d8'), 0.85); ctx.fill()
    if p.get('tear', 0) > 0:
        for side, ex, sq in eyes:
            ty = ey + 0.15 * R + p['tear'] * 0.35 * R
            ellipse(ctx, ex + 0.03 * R, ty, 0.035 * R, 0.06 * R)
            setc(ctx, hexc('#b8d4e6'), 0.8); ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ limbs
def limb(ctx, x, y, a1, a2, l1, l2, sgn, width, color, end=None, end_r=0, end_color=None, cuff=None):
    """a1: angle from straight down (deg), sgn=+1 rotates toward +x. Returns end point."""
    r1 = math.radians(a1)
    ex = x + l1 * math.sin(r1) * sgn
    ey = y + l1 * math.cos(r1)
    r2 = math.radians(a1 + a2)
    hx = ex + l2 * math.sin(r2) * sgn
    hy = ey + l2 * math.cos(r2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x, y); ctx.line_to(ex, ey); ctx.line_to(hx, hy)
    ctx.set_line_width(width)
    setc(ctx, color); ctx.stroke()
    if cuff is not None:
        # darker cuff ring near the wrist
        cx = hx - (hx - ex) * 0.12; cy = hy - (hy - ey) * 0.12
        ctx.move_to(cx, cy); ctx.line_to(hx, hy)
        ctx.set_line_width(width * 1.02)
        setc(ctx, cuff); ctx.stroke()
    if end == 'hand':
        hx2 = hx + (hx - ex) / l2 * end_r * 0.7
        hy2 = hy + (hy - ey) / l2 * end_r * 0.7
        ctx.arc(hx2, hy2, end_r, 0, 2 * math.pi)
        setc(ctx, end_color); ctx.fill()
        return (hx2, hy2, r2)
    return (hx, hy, r2)


def shoe(ctx, x, y, ang, facing, dirn, color):
    ctx.save()
    ctx.translate(x, y)
    if facing == 'side':
        ctx.rotate(-ang * dirn * 0.6)
        rrect(ctx, -34 + 10 * dirn, -16, 92, 38, 17)
        setc(ctx, color); ctx.fill()
        ctx.rectangle(-34 + 10 * dirn, 14, 92, 8)
        setc(ctx, shade(color, 1.25)); ctx.fill()
    else:
        rrect(ctx, -46, -14, 92, 36, 16)
        setc(ctx, color); ctx.fill()
        ctx.rectangle(-46, 14, 92, 8)
        setc(ctx, shade(color, 1.25)); ctx.fill()
    ctx.restore()


def gait(pose):
    """Fill leg/arm angles from walk phase."""
    ph = pose.get('phase', 0.0)
    amp = pose.get('amp', 0.0)
    run = pose.get('run', 0.0)
    th = lerp(26, 42, run) * amp
    s = math.sin(ph)
    legs = []
    for k in (1, -1):  # near, far
        a = th * s * k
        knee = -lerp(8, 70, run) * amp * max(0.0, -math.sin(ph * 1 + (0 if k == 1 else math.pi) + 0.6))
        legs.append((a, knee))
    arm_a = lerp(22, 48, run) * amp
    arms = [(-arm_a * s, lerp(12, 80, run) * amp + 6), (arm_a * s, lerp(12, 80, run) * amp + 6)]
    bob = -abs(math.cos(ph)) * lerp(10, 22, run) * amp
    return legs, arms, bob


def draw_person(ctx, look, pose, x, y, scale=1.0, alpha=1.0):
    """pose keys: facing ('front'|'side'), dir, phase, amp, run, lean (deg),
    arms: dict(l=(a1,a2), r=(a1,a2)) front; side: near=(a1,a2), far=(a1,a2)
    turn, tilt, look, blink, expr, talk, seated (hide legs), breathe(t)"""
    if alpha < 0.999:
        ctx.push_group()
    sc = scale * look.get('scale', 1.0)
    wd = look.get('width', 1.0)
    facing = pose.get('facing', 'front')
    dirn = pose.get('dir', 1)
    e = expr(pose.get('expr', 'neutral'))
    legs, garms, bob = gait(pose)
    br = math.sin(pose.get('t', 0.0) * 2.2) * 2.5 * pose.get('breathe', 1.0)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.translate(0, bob + pose.get('dy', 0.0))
    skin, top, pants, shoes = look['skin'], look['top'], look['pants'], look['shoes']
    top_l = shade(top, 1.07)
    top_d = shade(top, 0.78)
    lean = pose.get('lean', 0.0) + lerp(0, 10, pose.get('run', 0.0)) * pose.get('amp', 0.0) * (1 if facing == 'side' else 0)

    if facing == 'side':
        d = dirn
        # far leg
        if not pose.get('seated'):
            (fa, fk) = legs[1]
            hx, hy, ang = limb(ctx, -4 * d, HIP_Y + 10, fa, fk, 140, 140, d, 60 * wd, shade(pants, 0.75))
            shoe(ctx, hx, hy + 2, ang, 'side', d, shade(shoes, 0.78))
        ctx.save()
        ctx.translate(0, HIP_Y)
        ctx.rotate(math.radians(lean) * d)
        ctx.translate(0, -HIP_Y)
        # far arm
        arms = pose.get('arms') or {}
        fa1, fa2 = arms.get('far', garms[1])
        limb(ctx, -8 * d, SHOULDER_Y + 6, fa1, fa2, 100, 86, d, 44 * wd, shade(top, 0.7), 'hand', 22, shade(skin, 0.8))
        ctx.restore()
        if not pose.get('seated'):
            (na, nk) = legs[0]
            hx, hy, ang = limb(ctx, 4 * d, HIP_Y + 10, na, nk, 140, 140, d, 62 * wd, pants)
            shoe(ctx, hx, hy + 2, ang, 'side', d, shoes)
        ctx.save()
        ctx.translate(0, HIP_Y)
        ctx.rotate(math.radians(lean) * d)
        ctx.translate(0, -HIP_Y)
        # torso
        hw = 58 * wd
        ctx.move_to(-hw * d * 0.95, SHOULDER_Y - 14 + br * 0.3)
        ctx.curve_to(-hw * d * 1.05, -440, -hw * d * 1.02, -340, -hw * d, HIP_Y + 8)
        ctx.line_to(hw * d * 1.02, HIP_Y + 8)
        ctx.curve_to(hw * d * 1.08, -360, hw * d * 1.0, -450, hw * d * 0.75, SHOULDER_Y - 16 + br * 0.3)
        ctx.curve_to(hw * d * 0.4, SHOULDER_Y - 30, -hw * d * 0.5, SHOULDER_Y - 30, -hw * d * 0.95, SHOULDER_Y - 14)
        ctx.close_path()
        setc(ctx, top); ctx.fill()
        ctx.rectangle(-hw * 1.02, HIP_Y - 8, hw * 2.04, 16)
        setc(ctx, top_d); ctx.fill()
        _top_details(ctx, look, 'side', d, wd)
        # neck + head
        _neck(ctx, skin)
        ctx.save()
        ctx.translate(6 * d, HEAD_Y + br * 0.4 + pose.get('nod', 0))
        ctx.rotate(math.radians(pose.get('tilt', 0.0)))
        hp = dict(pose)
        hp.setdefault('turn', 0.92 * d)
        draw_head(ctx, look, hp, e)
        ctx.restore()
        # near arm (drawn over torso)
        na1, na2 = arms.get('near', garms[0])
        hand = limb(ctx, 4 * d, SHOULDER_Y + 6, na1, na2, 100, 86, d, 46 * wd, top_l, 'hand', 23, skin,
                    cuff=top_d)
        if pose.get('phone'):
            _held_phone(ctx, hand, d, pose)
        ctx.restore()
    else:
        arms = pose.get('arms') or {}
        if not pose.get('seated'):
            for k, sgn in ((0, -1), (1, 1)):
                a = 2 + pose.get('stance', 0)
                hx, hy, ang = limb(ctx, sgn * 32 * wd, HIP_Y + 10, a, 0, 140, 140, sgn, 62 * wd, pants)
                shoe(ctx, hx + sgn * 6, hy + 2, 0, 'front', 1, shoes)
        ctx.save()
        ctx.translate(0, HIP_Y)
        ctx.rotate(math.radians(lean))
        ctx.translate(0, -HIP_Y)
        hw = 86 * wd
        ctx.move_to(-hw + 30, SHOULDER_Y - 18 + br * 0.3)
        ctx.line_to(hw - 30, SHOULDER_Y - 18 + br * 0.3)
        ctx.curve_to(hw - 4, SHOULDER_Y - 16, hw + 2, SHOULDER_Y + 4, hw + 2, SHOULDER_Y + 30)
        ctx.line_to(hw + 6, HIP_Y + 8)
        ctx.line_to(-hw - 6, HIP_Y + 8)
        ctx.line_to(-hw - 2, SHOULDER_Y + 30)
        ctx.curve_to(-hw - 2, SHOULDER_Y + 4, -hw + 4, SHOULDER_Y - 16, -hw + 30, SHOULDER_Y - 18 + br * 0.3)
        ctx.close_path()
        setc(ctx, top); ctx.fill()
        ctx.rectangle(-hw - 6, HIP_Y - 10, (hw + 6) * 2, 18)
        setc(ctx, top_d); ctx.fill()
        _top_details(ctx, look, 'front', 1, wd)
        _neck(ctx, skin)
        # arms
        hands = {}
        for key, sgn in (('l', -1), ('r', 1)):
            a1, a2 = arms.get(key, (3 + 1.5 * math.sin(pose.get('t', 0) * 1.5 + sgn), 4))
            hands[key] = limb(ctx, sgn * (hw - 16), SHOULDER_Y + 10, a1, a2, 100, 88, sgn, 48 * wd, top_l,
                              'hand', 24, skin, cuff=top_d)
        ctx.save()
        ctx.translate(0, HEAD_Y + br * 0.4 + pose.get('nod', 0))
        ctx.rotate(math.radians(pose.get('tilt', 0.0)))
        draw_head(ctx, look, pose, e)
        ctx.restore()
        # re-draw raised arms over the head when hand is near face
        for key, sgn in (('l', -1), ('r', 1)):
            if key in arms and arms[key][0] > 60 and pose.get('arms_over', True):
                a1, a2 = arms[key]
                hands[key] = limb(ctx, sgn * (hw - 16), SHOULDER_Y + 10, a1, a2, 100, 88, sgn, 48 * wd, top_l,
                                  'hand', 24, skin, cuff=top_d)
        if pose.get('phone'):
            _held_phone(ctx, hands[pose.get('phone_hand', 'r')], 1, pose)
        ctx.restore()
    ctx.restore()
    if alpha < 0.999:
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(alpha)


def _neck(ctx, skin):
    ctx.rectangle(-15, NECK_TOP - 10, 30, 34)
    setc(ctx, shade(skin, 0.85)); ctx.fill()


def _top_details(ctx, look, facing, d, wd):
    st = look['top_style']
    top = look['top']
    ctx.set_line_width(4)
    if st == 'sweater':
        # ribbed collar
        if facing == 'front':
            ellipse(ctx, 0, SHOULDER_Y - 14, 30, 10)
        else:
            ellipse(ctx, 8 * d, SHOULDER_Y - 18, 22, 9)
        setc(ctx, shade(top, 0.7)); ctx.fill()
    elif st == 'cardigan':
        if facing == 'front':
            ctx.move_to(-30, SHOULDER_Y - 18); ctx.line_to(0, -380); ctx.line_to(30, SHOULDER_Y - 18); ctx.close_path()
            setc(ctx, look['inner']); ctx.fill()
            ctx.move_to(0, -380); ctx.line_to(0, HIP_Y)
            setc(ctx, shade(top, 0.75)); ctx.stroke()
            for yy in (-360, -330):
                ctx.arc(-8, yy, 4, 0, 6.3); setc(ctx, shade(top, 1.3)); ctx.fill()
    elif st == 'shirt':
        if facing == 'front':
            ctx.move_to(-28, SHOULDER_Y - 20); ctx.line_to(0, SHOULDER_Y + 8); ctx.line_to(28, SHOULDER_Y - 20)
            ctx.line_to(14, SHOULDER_Y - 22); ctx.line_to(0, SHOULDER_Y - 6); ctx.line_to(-14, SHOULDER_Y - 22)
            ctx.close_path()
            setc(ctx, shade(top, 1.3)); ctx.fill()
            ctx.move_to(0, SHOULDER_Y); ctx.line_to(0, HIP_Y)
            setc(ctx, shade(top, 0.8)); ctx.stroke()
    elif st == 'coat':
        pass


def _held_phone(ctx, hand, d, pose):
    hx, hy, ang = hand
    ctx.save()
    ctx.translate(hx, hy)
    ctx.rotate(pose.get('phone_rot', 0.0))
    rrect(ctx, -22, -46, 44, 82, 8)
    setc(ctx, hexc('#0f0f12')); ctx.fill()
    if pose.get('phone_lit', 1.0) > 0:
        rrect(ctx, -18, -42, 36, 74, 5)
        setc(ctx, hexc('#9fc4ff'), 0.85 * pose.get('phone_lit', 1.0)); ctx.fill()
    ctx.restore()
    ctx.arc(hx, hy + 4, 20, 0, 6.3)
    setc(ctx, pose.get('skin_c', hexc('#c9a07a'))); ctx.fill()
