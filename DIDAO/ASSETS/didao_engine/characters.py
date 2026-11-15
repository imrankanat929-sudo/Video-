"""DIDAO engine - character rigs.

THE DIDAO HERO is defined here once (HERO) and must never be redrawn from
scratch: every episode imports this rig. Proportions, hair silhouette,
clothes and colours are fixed constants.

Local character space: metres, origin between the feet, y DOWN (up is -y),
+x is the direction the character faces in side view.
"""
import math
import random

import skia

from .core import (capsule, clamp, col, hexc, lerp, lin_grad, mix, paint, poly, rad_grad,
                   smooth_path, tint_filter, sk)

# ---------------------------------------------------------------------------
# expressions
# ---------------------------------------------------------------------------
EXPR = {
    #            eye   pupil brow  inner  mouth  mouthw curve  look_x look_y
    'neutral':   dict(eye=1.0, pupil=1.0, brow=0.0, inner=0.0, mouth=0.0, mw=1.0, curve=0.0, lx=0.0, ly=0.0),
    'calm':      dict(eye=0.9, pupil=1.0, brow=0.0, inner=0.0, mouth=0.0, mw=1.0, curve=0.25, lx=0.0, ly=0.0),
    'smile':     dict(eye=0.85, pupil=1.0, brow=0.1, inner=0.0, mouth=0.1, mw=1.1, curve=0.8, lx=0.0, ly=0.0),
    'worried':   dict(eye=1.05, pupil=0.9, brow=0.2, inner=0.6, mouth=0.05, mw=0.9, curve=-0.3, lx=0.0, ly=0.0),
    'scared':    dict(eye=1.32, pupil=0.62, brow=0.55, inner=0.85, mouth=0.38, mw=0.85, curve=-0.4, lx=0.0, ly=0.0),
    'surprised': dict(eye=1.38, pupil=0.75, brow=0.95, inner=0.3, mouth=0.55, mw=0.7, curve=0.0, lx=0.0, ly=0.0),
    'sleep':     dict(eye=0.0, pupil=1.0, brow=-0.05, inner=0.0, mouth=0.0, mw=0.95, curve=0.0, lx=0.0, ly=0.0),
    'squint':    dict(eye=0.55, pupil=1.0, brow=-0.25, inner=-0.3, mouth=0.0, mw=1.0, curve=-0.1, lx=0.0, ly=0.0),
    'confused':  dict(eye=1.05, pupil=0.95, brow=0.35, inner=0.35, mouth=0.08, mw=0.9, curve=-0.2, lx=0.0, ly=0.0),
}


def expr_mix(a, b, t):
    ea = EXPR[a] if isinstance(a, str) else a
    eb = EXPR[b] if isinstance(b, str) else b
    return {k: lerp(ea[k], eb[k], t) for k in ea}


def expr(name, **over):
    e = dict(EXPR[name])
    e.update(over)
    return e


# ---------------------------------------------------------------------------
# character definitions (CONTINUITY: do not change)
# ---------------------------------------------------------------------------
class CharDef:
    def __init__(self, name, height, skin, hair, top, top_dark, pants, shoes, sole, eyes,
                 shoulder=0.205, hip=0.15, head_h=0.255, hair_style='hero', hat=None, extra=None,
                 build=1.0):
        self.name = name
        self.height = height
        self.skin = skin
        self.hair = hair
        self.top = top
        self.top_dark = top_dark
        self.pants = pants
        self.shoes = shoes
        self.sole = sole
        self.eyes = eyes
        self.shoulder = shoulder
        self.hip = hip
        self.head_h = head_h
        self.hair_style = hair_style
        self.hat = hat
        self.extra = extra or {}
        self.build = build
        k = height / 1.68
        self.k = k
        # skeleton (y up as negative)
        self.ankle_y = -0.075 * k
        self.knee_y = -0.47 * k
        self.hip_y = -0.88 * k
        self.shoulder_y = -1.39 * k
        self.neck_y = -1.45 * k
        self.thigh = (self.knee_y - self.hip_y) * -1 * -1
        self.thigh = abs(self.hip_y - self.knee_y)
        self.shin = abs(self.knee_y - self.ankle_y)
        self.uarm = 0.285 * k
        self.farm = 0.25 * k


# The DIDAO HERO - 15 years old, messy black hair, dark sweater, dark trousers, dark sneakers.
HERO = CharDef('hero', 1.68,
               skin=hexc('#c9a389'), hair=hexc('#0c0d12'), top=hexc('#262b36'), top_dark=hexc('#191c24'),
               pants=hexc('#1b1d23'), shoes=hexc('#17181c'), sole=hexc('#6b6e74'), eyes=hexc('#3a2a1f'),
               hair_style='hero')

# Friend 1 - MAX: taller, olive parka, knitted beanie.
MAX = CharDef('max', 1.80,
              skin=hexc('#b48a6c'), hair=hexc('#2a1d16'), top=hexc('#343f31'), top_dark=hexc('#252e23'),
              pants=hexc('#252b35'), shoes=hexc('#3a2d22'), sole=hexc('#2a2420'), eyes=hexc('#2b1e16'),
              shoulder=0.225, hip=0.16, hair_style='short', hat=hexc('#4a4f3f'), build=1.1)

# Friend 2 - LENA: auburn ponytail, muted maroon jacket, grey scarf.
LENA = CharDef('lena', 1.62,
               skin=hexc('#d3b09a'), hair=hexc('#4a2a1e'), top=hexc('#4b2a2d'), top_dark=hexc('#371d20'),
               pants=hexc('#1c1e25'), shoes=hexc('#26262b'), sole=hexc('#77787c'), eyes=hexc('#3d4a3a'),
               shoulder=0.185, hip=0.155, hair_style='ponytail', extra={'scarf': hexc('#5d636b')}, build=0.92)


# ---------------------------------------------------------------------------
# poses
# ---------------------------------------------------------------------------
def base_pose():
    return dict(x=0.0, y=0.0, lean=0.0, head=0.0, yaw=0.0,
                ls=4.0, le=6.0, rs=-4.0, re=-6.0,      # shoulders / elbows (deg, 0 = down, + = toward +x)
                lh=2.0, lk=0.0, rh=-2.0, rk=0.0,       # hips / knees (knee + bends backward)
                lf=0.0, rf=0.0, lhand='relaxed', rhand='relaxed', crouch=0.0, breathe=0.0,
                sit=0.0, lfs=0.0, rfs=0.0, pack=0)


def pose(**kw):
    p = base_pose()
    p.update(kw)
    return p


def pose_mix(a, b, t):
    out = {}
    for k in a:
        if isinstance(a[k], (int, float)) and isinstance(b.get(k), (int, float)):
            out[k] = lerp(a[k], b[k], t)
        else:
            out[k] = b[k] if t > 0.5 else a[k]
    return out


def front_walk_pose(phase, amount=1.0, **kw):
    """Walking toward / away from camera (front or back view)."""
    a = phase * 2 * math.pi
    s = math.sin(a)
    p = base_pose()
    p['lfs'] = max(0.0, s) * amount
    p['rfs'] = max(0.0, -s) * amount
    p['lh'] = 2 + 1.5 * s
    p['rh'] = -2 + 1.5 * s
    p['ls'] = 5 + 3 * s
    p['rs'] = -5 + 3 * s
    p['le'] = 10 + 14 * max(0, -s) * amount
    p['re'] = -10 - 14 * max(0, s) * amount
    p['y'] = -abs(math.cos(a)) * 0.022 * amount + 0.01
    p['x'] = 0.012 * s
    p['head'] = 1.2 * s
    p.update(kw)
    return p


def walk_pose(phase, amount=1.0, **kw):
    """Side-view walk cycle. phase in cycles."""
    a = phase * 2 * math.pi
    s = math.sin(a)
    p = base_pose()
    p['lh'] = 24 * s * amount
    p['rh'] = -24 * s * amount
    p['lk'] = max(0, 38 * math.sin(a + 1.9)) * amount + 4
    p['rk'] = max(0, 38 * math.sin(a + 1.9 + math.pi)) * amount + 4
    p['lf'] = -8 * math.cos(a) * amount
    p['rf'] = 8 * math.cos(a) * amount
    p['ls'] = -20 * s * amount
    p['rs'] = 20 * s * amount
    p['le'] = 22 + 6 * s
    p['re'] = 22 - 6 * s
    p['y'] = -abs(math.cos(a)) * 0.025 * amount + 0.012
    p['lean'] = 4 * amount
    p.update(kw)
    return p


# ---------------------------------------------------------------------------
# lighting
# ---------------------------------------------------------------------------
class Light:
    def __init__(self, amb=(0.42, 0.48, 0.62), rim=hexc('#9fb6dc'), rim_side=-1, rim_w=0.022,
                 rim_k=0.9, shade=0.45, warm=0.0, warm_side=1, warm_col=hexc('#ff8a3a'), warm_w=0.03,
                 fill=None, front=0.0, front_col=hexc('#dfe6ff')):
        self.amb = amb
        self.rim = rim
        self.rim_side = rim_side
        self.rim_w = rim_w
        self.rim_k = rim_k
        self.shade = shade
        self.warm = warm
        self.warm_side = warm_side
        self.warm_col = warm_col
        self.warm_w = warm_w
        self.front = front          # flashlight / frontal key strength
        self.front_col = front_col


def lit_draw(c, pic, light, scale_px=1.0, blur_px=None):
    """Composite a recorded character picture with ambient, shading and rim lights.
    Must be called with the canvas already in character space."""
    b = pic.cullRect()
    b = skia.Rect(b.left() - 0.2, b.top() - 0.2, b.right() + 0.2, b.bottom() + 0.2)
    outer = skia.Paint()
    if blur_px:
        outer.setImageFilter(skia.ImageFilters.Blur(blur_px, blur_px))
    c.saveLayer(b, outer)
    # base with ambient tint
    amb = light.amb
    if light.front:
        amb = tuple(lerp(a, f, light.front) for a, f in zip(amb, light.front_col[:3]))
    c.saveLayer(b, paint(cf=tint_filter(amb)))
    c.drawPicture(pic)
    # form shading: darker away from the key light
    side = light.rim_side if not light.warm or light.warm < 0.4 else light.warm_side
    x0, x1 = (b.left(), b.right()) if side < 0 else (b.right(), b.left())
    sh = lin_grad((x0, 0), (x1, 0), [(0, 0, 0, 0.0), (0, 0, 0, light.shade * 0.5), (0, 0, 0, light.shade)], [0.0, 0.55, 1.0])
    c.drawRect(b, paint(shader=sh, blend=skia.BlendMode.kSrcATop))
    c.restore()

    def rim(colr, side, w, k, up=0.7):
        if k <= 0.001:
            return
        c.saveLayer(b, paint(blend=skia.BlendMode.kPlus))
        bp = skia.Paint()
        bl = max(w * 0.30, 0.002)
        bp.setImageFilter(skia.ImageFilters.Blur(bl, bl))
        c.saveLayer(b, bp)
        c.drawPicture(pic, None, paint(cf=skia.ColorFilters.Blend(col(colr, k), skia.BlendMode.kSrcIn)))
        c.save()
        c.translate(-side * w, w * up)
        c.drawPicture(pic, None, paint(blend=skia.BlendMode.kDstOut))
        c.restore()
        c.restore()
        c.drawPicture(pic, None, paint(blend=skia.BlendMode.kDstIn))
        c.restore()

    rim(light.rim, light.rim_side, light.rim_w, light.rim_k)
    if light.warm > 0:
        rim(light.warm_col, light.warm_side, light.warm_w, light.warm, up=0.1)
        # warm bounce on the fire-facing half
        x0, x1 = (b.left(), b.right()) if light.warm_side < 0 else (b.right(), b.left())
        sh = lin_grad((x0, 0), (x1, 0), [(*light.warm_col[:3], 0.35 * light.warm), (*light.warm_col[:3], 0.0)], [0.0, 0.6])
        c.drawRect(b, paint(shader=sh, blend=skia.BlendMode.kSrcATop))
    c.restore()


# ---------------------------------------------------------------------------
# head drawing (unit space: crown ~ -0.56, chin 0.45, eyes on y = 0)
# ---------------------------------------------------------------------------
R_FACE = 0.40


def _warp(x, y, yaw):
    """Rotate a face point around the vertical axis (cylindrical approx)."""
    u = clamp(x / R_FACE, -0.999, 0.999)
    th = math.asin(u)
    return (R_FACE * math.sin(th + yaw), y), math.cos(th + yaw)


def _wpts(pts, yaw, dx=0.0):
    return [(_warp(x, y, yaw)[0][0] + dx, y) for x, y in pts]


HAIR_HERO_OUT = [(-0.400, 0.05), (-0.445, -0.07), (-0.475, -0.19), (-0.455, -0.28), (-0.495, -0.38), (-0.43, -0.49),
                 (-0.42, -0.59), (-0.31, -0.635), (-0.25, -0.705), (-0.14, -0.675), (-0.06, -0.735), (0.04, -0.69),
                 (0.13, -0.735), (0.21, -0.67), (0.31, -0.66), (0.37, -0.58), (0.455, -0.51), (0.445, -0.41),
                 (0.495, -0.32), (0.45, -0.22), (0.465, -0.11), (0.400, 0.05)]
HAIR_HERO_IN = [(0.375, 0.00), (0.37, -0.13), (0.335, -0.20), (0.285, -0.135), (0.245, -0.235), (0.18, -0.15),
                (0.125, -0.255), (0.06, -0.165), (-0.005, -0.265), (-0.075, -0.16), (-0.13, -0.255), (-0.195, -0.165),
                (-0.255, -0.245), (-0.305, -0.15), (-0.35, -0.195), (-0.375, 0.00)]
HAIR_HERO_STRANDS = [((-0.30, -0.55), (-0.20, -0.30), (-0.17, -0.10)), ((-0.05, -0.65), (0.0, -0.40), (0.02, -0.24)),
                     ((0.12, -0.62), (0.16, -0.40), (0.15, -0.23)), ((0.30, -0.55), (0.32, -0.35), (0.27, -0.22)),
                     ((-0.40, -0.45), (-0.36, -0.30), (-0.29, -0.10)), ((0.40, -0.45), (0.40, -0.25), (0.36, -0.14))]


def draw_head_front(c, cd, yaw=0.0, e=None, t=0.0, back=False):
    e = e or EXPR['neutral']
    skin = cd.skin
    skin_d = mix(skin, (0.25, 0.12, 0.10, 1), 0.35)
    hair = cd.hair
    hair_hi = mix(hair, (0.55, 0.62, 0.75, 1), 0.28)
    sy = math.sin(yaw)
    jaw_dx = sy * 0.11

    # --- back hair mass (behind head) ---
    if cd.hair_style == 'ponytail':
        tail_side = 1 if yaw >= 0 else -1
        path = smooth_path([(-0.42, -0.30), (-0.45, 0.10), (-0.44, 0.42), (-0.36, 0.52), (0.36, 0.52),
                            (0.44, 0.42), (0.45, 0.10), (0.42, -0.30), (0.0, -0.60)])
        c.drawPath(path, paint(mix(hair, (0, 0, 0, 1), 0.3)))
        if back:
            tp = smooth_path([(-0.10, -0.25), (0.10, -0.25), (0.13, 0.30), (0.05, 0.75), (-0.03, 0.80), (-0.12, 0.35)])
            c.drawPath(tp, paint(hair))
    if cd.hair_style == 'short' and not cd.hat:
        pass

    # --- ears ---
    for side in (-1, 1):
        (ex, ey), vis = _warp(side * 0.375, 0.07, yaw)
        if back:
            vis = 1
            ex = side * 0.385
        if vis > -0.15:
            ear = smooth_path([(ex, -0.04), (ex + side * 0.075, -0.05), (ex + side * 0.09, 0.08),
                               (ex + side * 0.05, 0.20), (ex, 0.18)])
            c.drawPath(ear, paint(skin_d if back else skin))
            if not back:
                c.drawPath(smooth_path([(ex + side * 0.02, 0.0), (ex + side * 0.06, 0.02), (ex + side * 0.055, 0.12),
                                        (ex + side * 0.025, 0.14)], close=False), paint(skin_d, stroke=0.018))

    # --- head shape ---
    outline = [(0.0, -0.57), (0.27, -0.50), (0.375, -0.28), (0.385, 0.0), (0.355, 0.18),
               (0.29 + jaw_dx * 0.4, 0.31), (0.13 + jaw_dx, 0.43), (0.0 + jaw_dx, 0.455),
               (-0.13 + jaw_dx, 0.43), (-0.29 + jaw_dx * 0.4, 0.31), (-0.355, 0.18), (-0.385, 0.0),
               (-0.375, -0.28), (-0.27, -0.50)]
    head = smooth_path(outline)
    c.drawPath(head, paint(skin))
    if back:
        _draw_hair_back(c, cd, hair, hair_hi)
        return
    # soft form shading on the head (cheek/jaw)
    c.save()
    c.clipPath(head, doAntiAlias=True)
    c.drawRect(skia.Rect(-0.5, 0.18, 0.5, 0.5), paint(skin_d, alpha=0.25, blur=0.05))
    sd = 1 if yaw >= 0 else -1
    c.drawOval(skia.Rect(-0.42 * sd - 0.12, -0.35, -0.42 * sd + 0.12, 0.45), paint(skin_d, alpha=0.35, blur=0.07))
    # cheek warmth
    for side in (-1, 1):
        (cx, _), vis = _warp(side * 0.22, 0.13, yaw)
        if vis > 0.2:
            c.drawOval(skia.Rect(cx - 0.07, 0.08, cx + 0.07, 0.18), paint((0.75, 0.35, 0.32), alpha=0.10, blur=0.03))
    c.restore()

    # --- eyes ---
    blink = e.get('blink', 0.0)
    eo = e['eye'] * (1 - blink)
    for side in (-1, 1):
        (ex, ey), vis = _warp(side * 0.165, 0.0, yaw)
        if vis < 0.05:
            continue
        sx = max(vis, 0.25)
        ew = 0.084 * sx
        eh = 0.045 * eo
        c.save()
        c.translate(ex, ey)
        if eo > 0.05:
            up_y = -eh - 0.004
            lo_y = eh * 0.75
            inner = -side
            eye = skia.Path()
            eye.moveTo(-ew, 0.004)
            eye.cubicTo(-ew * 0.6, up_y * 1.15, ew * 0.45, up_y * 1.2, ew, -0.004)
            eye.cubicTo(ew * 0.6, lo_y, -ew * 0.5, lo_y * 1.05, -ew, 0.004)
            eye.close()
            c.drawPath(eye, paint((0.86, 0.84, 0.80)))
            c.save()
            c.clipPath(eye, doAntiAlias=True)
            ir = 0.037
            ix = clamp(e['lx'], -1, 1) * ew * 0.45 + sy * 0.012
            iy = clamp(e['ly'], -1, 1) * eh * 0.5 + 0.002
            c.drawCircle(ix, iy, ir, paint(cd.eyes))
            c.drawCircle(ix, iy, ir, paint((0, 0, 0), alpha=0.45, stroke=0.006))
            c.drawCircle(ix, iy, 0.016 * e['pupil'], paint((0.02, 0.02, 0.03)))
            c.drawCircle(ix - 0.011, iy - 0.012, 0.0085, paint((1, 1, 1), alpha=0.9))
            c.drawCircle(ix + 0.012, iy + 0.010, 0.0045, paint((1, 1, 1), alpha=0.45))
            # lid shadow
            c.drawRect(skia.Rect(-ew, up_y * 1.3, ew, up_y * 0.35), paint((0.2, 0.1, 0.08), alpha=0.35, blur=0.01))
            c.restore()
            # upper lid / lashes line
            lid = skia.Path()
            lid.moveTo(-ew * 1.05, 0.006)
            lid.cubicTo(-ew * 0.6, up_y * 1.18, ew * 0.45, up_y * 1.22, ew * 1.08, -0.006)
            c.drawPath(lid, paint((0.08, 0.05, 0.05), stroke=0.013))
            lo = skia.Path()
            lo.moveTo(-ew * 0.8, lo_y * 0.6)
            lo.cubicTo(-ew * 0.3, lo_y * 1.1, ew * 0.4, lo_y * 1.0, ew * 0.85, lo_y * 0.3)
            c.drawPath(lo, paint(skin_d, alpha=0.8, stroke=0.006))
            # crease
            cr = skia.Path()
            cr.moveTo(-ew * 0.8, up_y * 1.6 - 0.006)
            cr.cubicTo(-ew * 0.3, up_y * 2.1 - 0.012, ew * 0.4, up_y * 2.0 - 0.012, ew * 0.9, up_y * 1.4 - 0.006)
            c.drawPath(cr, paint(skin_d, alpha=0.7, stroke=0.006))
        else:
            cl = skia.Path()
            cl.moveTo(-ew, 0.0)
            cl.cubicTo(-ew * 0.4, 0.022, ew * 0.4, 0.022, ew, 0.0)
            c.drawPath(cl, paint((0.10, 0.06, 0.05), stroke=0.012))
            c.drawPath(cl, paint(skin_d, alpha=0.4, stroke=0.03, blur=0.01))
        c.restore()

    # --- brows ---
    for side in (-1, 1):
        inner_pt, v1 = _warp(side * 0.07, -0.095 - e['brow'] * 0.045 - e['inner'] * 0.035, yaw)
        mid_pt, v2 = _warp(side * 0.17, -0.13 - e['brow'] * 0.05, yaw)
        outer_pt, v3 = _warp(side * 0.27, -0.10 - e['brow'] * 0.035 + e['inner'] * 0.012, yaw)
        if v2 < 0.05:
            continue
        b = skia.Path()
        b.moveTo(*inner_pt)
        b.quadTo(*mid_pt, *outer_pt)
        c.drawPath(b, paint(mix(cd.hair, (0, 0, 0, 1), 0.2), stroke=0.026 * max(v2, 0.4)))

    # --- nose ---
    (nx, _), _ = _warp(0.0, 0.18, yaw)
    sd = -1 if yaw >= 0 else 1
    bridge = skia.Path()
    bridge.moveTo(nx + sd * 0.035 - sy * 0.03, 0.02)
    bridge.quadTo(nx + sd * 0.045, 0.12, nx + sd * 0.030, 0.19)
    c.drawPath(bridge, paint(skin_d, alpha=0.55, stroke=0.012, blur=0.004))
    c.drawOval(skia.Rect(nx - 0.055, 0.19, nx + 0.055, 0.225), paint(skin_d, alpha=0.45, blur=0.008))
    for side in (-1, 1):
        c.drawOval(skia.Rect(nx + side * 0.03 - 0.013, 0.195, nx + side * 0.03 + 0.013, 0.212), paint((0.3, 0.15, 0.13), alpha=0.6))
    c.drawCircle(nx - 0.01, 0.165, 0.014, paint((1, 0.95, 0.9), alpha=0.15, blur=0.006))

    # --- mouth ---
    (mx, _), _ = _warp(0.0, 0.31, yaw)
    mw = 0.085 * e['mw'] * (1 - abs(sy) * 0.25)
    mo = e['mouth']
    cv = e['curve']
    my = 0.305
    lip = (0.55, 0.30, 0.28, 1)
    if mo > 0.04:
        oh = 0.075 * mo
        m = skia.Path()
        m.moveTo(mx - mw, my - cv * 0.01)
        m.cubicTo(mx - mw * 0.5, my - oh * 0.55, mx + mw * 0.5, my - oh * 0.55, mx + mw, my - cv * 0.01)
        m.cubicTo(mx + mw * 0.6, my + oh * 1.1, mx - mw * 0.6, my + oh * 1.1, mx - mw, my - cv * 0.01)
        m.close()
        c.drawPath(m, paint((0.16, 0.05, 0.05)))
        c.save()
        c.clipPath(m, doAntiAlias=True)
        c.drawRect(skia.Rect(mx - mw, my - oh, mx + mw, my - oh * 0.35), paint((0.85, 0.82, 0.78), alpha=0.85))
        c.drawOval(skia.Rect(mx - mw * 0.6, my + oh * 0.3, mx + mw * 0.6, my + oh * 1.2), paint((0.45, 0.16, 0.16)))
        c.restore()
        c.drawPath(m, paint(lip, alpha=0.6, stroke=0.008))
    else:
        m = skia.Path()
        m.moveTo(mx - mw, my - cv * 0.012)
        m.cubicTo(mx - mw * 0.4, my + cv * 0.02 + 0.004, mx + mw * 0.4, my + cv * 0.02 + 0.004, mx + mw, my - cv * 0.012)
        c.drawPath(m, paint((0.28, 0.12, 0.11), stroke=0.011))
    # lower lip shade
    c.drawOval(skia.Rect(mx - mw * 0.7, my + 0.018 + mo * 0.07, mx + mw * 0.7, my + 0.045 + mo * 0.07),
               paint(lip, alpha=0.30, blur=0.006))
    c.drawOval(skia.Rect(mx - 0.05, my + 0.07 + mo * 0.06, mx + 0.05, my + 0.085 + mo * 0.06), paint(skin_d, alpha=0.3, blur=0.01))

    # --- hair / hat ---
    _draw_hair_front(c, cd, yaw, hair, hair_hi, t)


def _draw_hair_front(c, cd, yaw, hair, hair_hi, t):
    sy = math.sin(yaw)
    if cd.hair_style == 'hero':
        out = [(x + sy * 0.05 * (1 - abs(x) / 0.6), y) for x, y in HAIR_HERO_OUT]
        inn = _wpts(HAIR_HERO_IN, yaw)
        shape = smooth_path(out + inn, tension=0.5)
        c.drawPath(shape, paint(hair))
        c.save()
        c.clipPath(shape, doAntiAlias=True)
        # sheen from moonlight - blue grey strands
        for (a, b, d) in HAIR_HERO_STRANDS:
            pa = (a[0] + sy * 0.04, a[1])
            pb = _warp(*b, yaw)[0]
            pd = _warp(*d, yaw)[0]
            s = skia.Path()
            s.moveTo(*pa)
            s.quadTo(*pb, *pd)
            c.drawPath(s, paint(hair_hi, alpha=0.55, stroke=0.022, blur=0.006))
        c.drawOval(skia.Rect(-0.35, -0.62, 0.15, -0.42), paint(hair_hi, alpha=0.25, blur=0.05))
        c.restore()
        # fringe shadow onto forehead
        c.save()
        c.clipPath(smooth_path([(0.0, -0.57), (0.27, -0.50), (0.375, -0.28), (0.385, 0.0), (-0.385, 0.0), (-0.375, -0.28), (-0.27, -0.50)]), doAntiAlias=True)
        sh = smooth_path([(x, y + 0.035) for x, y in inn], close=False)
        c.drawPath(sh, paint((0.2, 0.1, 0.08), alpha=0.35, stroke=0.04, blur=0.015))
        c.restore()
    elif cd.hair_style == 'short':
        # short hair visible at the sides under the beanie
        for side in (-1, 1):
            c.drawPath(smooth_path([(side * 0.36, -0.30), (side * 0.40, -0.10), (side * 0.37, 0.05), (side * 0.33, -0.15)]), paint(hair))
        # sideburn tufts
    elif cd.hair_style == 'ponytail':
        out = [(-0.40, 0.12), (-0.43, -0.12), (-0.41, -0.40), (-0.25, -0.58), (0.0, -0.62), (0.25, -0.58), (0.41, -0.40), (0.43, -0.12), (0.40, 0.12)]
        out = [(x + sy * 0.04 * (1 - abs(x) / 0.6), y) for x, y in out]
        inn = _wpts([(0.375, 0.02), (0.37, -0.16), (0.28, -0.29), (0.10, -0.33), (-0.06, -0.24), (-0.20, -0.28), (-0.33, -0.24), (-0.375, -0.10), (-0.38, 0.02)], yaw)
        shape = smooth_path(out + inn, tension=0.4)
        c.drawPath(shape, paint(hair))
        c.save()
        c.clipPath(shape, doAntiAlias=True)
        for k in range(5):
            x = -0.3 + k * 0.15
            s = skia.Path()
            s.moveTo(x * 0.3, -0.58)
            s.quadTo(x, -0.45, x * 1.2, -0.10)
            c.drawPath(s, paint(hair_hi, alpha=0.35, stroke=0.02, blur=0.006))
        c.restore()
    if cd.hat:
        hat = cd.hat
        hp = smooth_path([(-0.43, -0.20), (-0.44, -0.40), (-0.33, -0.62), (0.0, -0.72), (0.33, -0.62), (0.44, -0.40), (0.43, -0.20), (0.0, -0.17)], tension=0.4)
        hp = smooth_path([(x + sy * 0.03, y) for x, y in [(-0.43, -0.18), (-0.45, -0.40), (-0.33, -0.63), (0.0, -0.72), (0.33, -0.63), (0.45, -0.40), (0.43, -0.18)]] + [(0.0, -0.15)], tension=0.4)
        c.drawPath(hp, paint(hat))
        c.save()
        c.clipPath(hp, doAntiAlias=True)
        # folded cuff
        c.drawRect(skia.Rect(-0.5, -0.32, 0.5, -0.14), paint(mix(hat, (0, 0, 0, 1), 0.2)))
        for k in range(-8, 9):
            x = k * 0.05 + sy * 0.03
            c.drawLine(x, -0.32, x, -0.14, paint(mix(hat, (0, 0, 0, 1), 0.4), stroke=0.008))
            c.drawLine(x, -0.70, x * 1.05, -0.33, paint(mix(hat, (0, 0, 0, 1), 0.3), stroke=0.006))
        c.restore()


def _draw_hair_back(c, cd, hair, hair_hi):
    if cd.hair_style == 'hero':
        out = [(-x, y) for x, y in HAIR_HERO_OUT]
        back = smooth_path(out[::-1] + [(0.39, 0.12), (0.30, 0.22), (0.15, 0.18), (0.05, 0.27), (-0.08, 0.19),
                                         (-0.20, 0.25), (-0.30, 0.16), (-0.39, 0.12)], tension=0.35)
        c.drawPath(back, paint(hair))
        c.save()
        c.clipPath(back, doAntiAlias=True)
        for k in range(7):
            x = -0.32 + k * 0.105
            s = skia.Path()
            s.moveTo(x * 0.4, -0.62)
            s.quadTo(x * 1.1, -0.25, x * 0.9, 0.15)
            c.drawPath(s, paint(hair_hi, alpha=0.35, stroke=0.02, blur=0.008))
        c.drawCircle(0.0, -0.40, 0.04, paint(hair_hi, alpha=0.4, blur=0.02))  # crown swirl
        c.restore()
    elif cd.hair_style == 'ponytail':
        back = smooth_path([(-0.43, 0.25), (-0.45, -0.20), (-0.30, -0.56), (0.0, -0.62), (0.30, -0.56), (0.45, -0.20), (0.43, 0.25), (0.0, 0.32)])
        c.drawPath(back, paint(hair))
        c.drawPath(smooth_path([(-0.09, -0.05), (0.09, -0.05), (0.12, 0.40), (0.04, 0.85), (-0.04, 0.88), (-0.12, 0.45)]), paint(mix(hair, hair_hi, 0.2)))
        c.drawRect(skia.Rect(-0.08, -0.08, 0.08, -0.02), paint((0.1, 0.1, 0.12)))
    elif cd.hair_style == 'short':
        c.drawPath(smooth_path([(-0.40, 0.15), (-0.42, -0.20), (-0.30, -0.50), (0.30, -0.50), (0.42, -0.20), (0.40, 0.15), (0.0, 0.22)]), paint(hair))
    if cd.hat:
        hp = smooth_path([(-0.43, -0.18), (-0.45, -0.40), (-0.33, -0.63), (0.0, -0.72), (0.33, -0.63), (0.45, -0.40), (0.43, -0.18), (0.0, -0.15)], tension=0.4)
        c.drawPath(hp, paint(cd.hat))
        c.drawRect(skia.Rect(-0.45, -0.32, 0.45, -0.16), paint(mix(cd.hat, (0, 0, 0, 1), 0.2)))


def draw_head_side(c, cd, e=None, t=0.0):
    """Profile facing +x."""
    e = e or EXPR['neutral']
    skin = cd.skin
    skin_d = mix(skin, (0.25, 0.12, 0.10, 1), 0.35)
    hair = cd.hair
    hair_hi = mix(hair, (0.55, 0.62, 0.75, 1), 0.28)
    if cd.hair_style == 'ponytail':
        c.drawPath(smooth_path([(-0.40, -0.25), (-0.62, -0.10), (-0.70, 0.30), (-0.60, 0.65), (-0.52, 0.30), (-0.42, 0.0)]), paint(hair))
    prof = [(-0.40, -0.10), (-0.33, -0.42), (-0.08, -0.57), (0.22, -0.48), (0.36, -0.25), (0.385, -0.08),
            (0.37, -0.02), (0.395, 0.06), (0.465, 0.165), (0.44, 0.19), (0.395, 0.205), (0.41, 0.27),
            (0.395, 0.31), (0.405, 0.35), (0.375, 0.42), (0.30, 0.455), (0.12, 0.44), (-0.02, 0.33),
            (-0.10, 0.38), (-0.30, 0.25)]
    hp = smooth_path(prof, tension=0.4)
    c.drawPath(hp, paint(skin))
    c.save()
    c.clipPath(hp, doAntiAlias=True)
    c.drawOval(skia.Rect(-0.45, -0.3, 0.05, 0.5), paint(skin_d, alpha=0.4, blur=0.06))
    c.restore()
    # ear
    c.drawPath(smooth_path([(-0.06, -0.04), (0.02, -0.06), (0.04, 0.08), (0.0, 0.19), (-0.07, 0.16)]), paint(skin_d))
    # eye
    eo = e['eye'] * (1 - e.get('blink', 0.0))
    if eo > 0.05:
        eye = poly([(0.27, -0.005 - 0.03 * eo), (0.345, -0.01), (0.33, 0.02 * eo), (0.27, 0.02 * eo)])
        c.drawPath(eye, paint((0.86, 0.84, 0.80)))
        c.save()
        c.clipPath(eye, doAntiAlias=True)
        c.drawCircle(0.325, 0.002, 0.028, paint(cd.eyes))
        c.drawCircle(0.33, 0.002, 0.013, paint((0.02, 0.02, 0.02)))
        c.restore()
        c.drawLine(0.26, -0.01 - 0.035 * eo, 0.35, -0.012, paint((0.08, 0.05, 0.05), stroke=0.012))
    else:
        c.drawLine(0.27, 0.005, 0.345, 0.008, paint((0.08, 0.05, 0.05), stroke=0.012))
    c.drawLine(0.24, -0.13 - e['brow'] * 0.04, 0.36, -0.12 - e['brow'] * 0.03 - e['inner'] * 0.02,
               paint(mix(hair, (0, 0, 0, 1), 0.2), stroke=0.025))
    # mouth
    mo = e['mouth']
    if mo > 0.05:
        c.drawPath(poly([(0.40, 0.29), (0.34, 0.30), (0.33, 0.30 + mo * 0.05), (0.40, 0.31 + mo * 0.06)]), paint((0.16, 0.05, 0.05)))
    else:
        c.drawLine(0.405, 0.305, 0.34, 0.31, paint((0.30, 0.12, 0.11), stroke=0.01))
    c.drawCircle(0.42, 0.185, 0.012, paint((0.3, 0.15, 0.13), alpha=0.5))
    # hair
    if cd.hair_style == 'hero':
        hs = [(-0.43, 0.20), (-0.49, 0.03), (-0.48, -0.10), (-0.54, -0.24), (-0.47, -0.36), (-0.49, -0.48),
              (-0.36, -0.57), (-0.29, -0.67), (-0.15, -0.62), (-0.04, -0.71), (0.08, -0.63), (0.22, -0.66),
              (0.28, -0.55), (0.41, -0.48), (0.38, -0.39), (0.44, -0.28), (0.385, -0.22), (0.40, -0.13),
              (0.32, -0.16), (0.29, -0.22), (0.22, -0.14), (0.15, -0.26), (0.05, -0.22), (0.04, -0.08),
              (-0.06, -0.02), (-0.10, 0.06), (-0.18, 0.20), (-0.30, 0.26)]
        sp = smooth_path(hs, tension=0.5)
        c.drawPath(sp, paint(hair))
        c.save()
        c.clipPath(sp, doAntiAlias=True)
        for k in range(5):
            s = skia.Path()
            s.moveTo(-0.3 + k * 0.12, -0.60)
            s.quadTo(-0.1 + k * 0.12, -0.40, 0.0 + k * 0.1, -0.20)
            c.drawPath(s, paint(hair_hi, alpha=0.45, stroke=0.02, blur=0.006))
        c.restore()
    elif cd.hair_style == 'ponytail':
        sp = smooth_path([(-0.42, 0.10), (-0.44, -0.30), (-0.30, -0.55), (0.0, -0.62), (0.25, -0.55), (0.38, -0.32),
                          (0.30, -0.28), (0.12, -0.33), (-0.05, -0.18), (-0.10, 0.05), (-0.25, 0.15)], tension=0.4)
        c.drawPath(sp, paint(hair))
    elif cd.hair_style == 'short':
        c.drawPath(smooth_path([(-0.42, 0.15), (-0.45, -0.25), (-0.1, -0.2), (-0.05, 0.05), (-0.2, 0.20)]), paint(hair))
    if cd.hat:
        hp = smooth_path([(-0.47, -0.10), (-0.45, -0.45), (-0.20, -0.68), (0.15, -0.68), (0.38, -0.45), (0.40, -0.22), (0.0, -0.18)], tension=0.4)
        c.drawPath(hp, paint(cd.hat))
        c.save()
        c.clipPath(hp, doAntiAlias=True)
        c.drawRect(skia.Rect(-0.6, -0.36, 0.6, -0.1), paint(mix(cd.hat, (0, 0, 0, 1), 0.2)))
        c.restore()


# ---------------------------------------------------------------------------
# body drawing
# ---------------------------------------------------------------------------
def _limb_end(a, ang_deg, L):
    r = math.radians(ang_deg)
    return (a[0] + math.sin(r) * L, a[1] + math.cos(r) * L)


def _hand(c, cd, at, ang, kind, view, side, scale=1.0, dark=0.0):
    skin = mix(cd.skin, (0, 0, 0, 1), dark)
    skin_d = mix(skin, (0.25, 0.12, 0.10, 1), 0.35)
    c.save()
    c.translate(*at)
    c.rotate(-ang)
    k = cd.k * scale * 0.78
    if kind in ('flashlight',):
        # fist around a torch (torch points along the arm)
        c.drawRoundRect(skia.Rect(-0.022 * k, 0.02 * k, 0.022 * k, 0.21 * k), 0.012, 0.012, paint((0.12, 0.12, 0.13)))
        c.drawRoundRect(skia.Rect(-0.03 * k, 0.17 * k, 0.03 * k, 0.24 * k), 0.01, 0.01, paint((0.20, 0.20, 0.22)))
        c.drawOval(skia.Rect(-0.026 * k, 0.225 * k, 0.026 * k, 0.245 * k), paint((0.95, 0.95, 0.85)))
        c.drawRoundRect(skia.Rect(-0.045 * k, 0.0, 0.045 * k, 0.11 * k), 0.035, 0.035, paint(skin))
        for i in range(3):
            c.drawLine(-0.04 * k, (0.03 + i * 0.026) * k, 0.03 * k, (0.03 + i * 0.026) * k, paint(skin_d, stroke=0.006))
    elif kind == 'point':
        c.drawRoundRect(skia.Rect(-0.042 * k, 0.0, 0.042 * k, 0.10 * k), 0.035, 0.035, paint(skin))
        c.drawRoundRect(skia.Rect(-0.011 * k, 0.06 * k, 0.011 * k, 0.19 * k), 0.011, 0.011, paint(skin))
        c.drawLine(-0.03 * k, 0.04 * k, -0.045 * k, 0.09 * k, paint(skin, stroke=0.02))
    elif kind == 'fist':
        c.drawRoundRect(skia.Rect(-0.045 * k, 0.0, 0.045 * k, 0.11 * k), 0.04, 0.04, paint(skin))
        c.drawLine(-0.03 * k, 0.07 * k, 0.03 * k, 0.07 * k, paint(skin_d, stroke=0.006))
    elif kind == 'open':
        c.drawRoundRect(skia.Rect(-0.048 * k, 0.0, 0.048 * k, 0.10 * k), 0.03, 0.03, paint(skin))
        for i in range(4):
            x = (-0.035 + i * 0.023) * k
            c.drawRoundRect(skia.Rect(x - 0.01 * k, 0.07 * k, x + 0.01 * k, (0.17 - abs(i - 1.5) * 0.015) * k), 0.01, 0.01, paint(skin))
        c.drawLine(side * 0.045 * k, 0.03 * k, side * 0.075 * k, 0.09 * k, paint(skin, stroke=0.02 * k))
    else:  # relaxed
        hp = smooth_path([(-0.04 * k, 0.0), (0.04 * k, 0.0), (0.05 * k, 0.09 * k), (0.03 * k, 0.16 * k), (-0.02 * k, 0.17 * k), (-0.045 * k, 0.10 * k)])
        c.drawPath(hp, paint(skin))
        c.drawLine(-0.01 * k, 0.10 * k, -0.012 * k, 0.15 * k, paint(skin_d, alpha=0.6, stroke=0.005))
    c.restore()


def _shoe(c, cd, at, ang, view, dark=0.0):
    k = cd.k
    sh = mix(cd.shoes, (0, 0, 0, 1), dark)
    so = mix(cd.sole, (0, 0, 0, 1), dark)
    c.save()
    c.translate(*at)
    c.rotate(ang)
    if view == 'side':
        up = smooth_path([(-0.07 * k, -0.06 * k), (0.04 * k, -0.07 * k), (0.15 * k, -0.035 * k), (0.185 * k, 0.0), (-0.08 * k, 0.0)], tension=0.4)
        c.drawPath(up, paint(sh))
        c.drawRect(skia.Rect(-0.085 * k, -0.012 * k, 0.19 * k, 0.012 * k), paint(so))
        c.drawLine(0.0, -0.06 * k, 0.07 * k, -0.045 * k, paint(mix(sh, (1, 1, 1, 1), 0.15), stroke=0.008))
    elif view == 'front':
        up = smooth_path([(-0.06 * k, -0.07 * k), (0.06 * k, -0.07 * k), (0.07 * k, 0.0), (-0.07 * k, 0.0)], tension=0.4)
        c.drawPath(up, paint(sh))
        c.drawRect(skia.Rect(-0.072 * k, -0.012 * k, 0.072 * k, 0.012 * k), paint(so))
        c.drawLine(-0.025 * k, -0.06 * k, 0.025 * k, -0.06 * k, paint(mix(sh, (1, 1, 1, 1), 0.15), stroke=0.008))
    else:  # back
        up = smooth_path([(-0.06 * k, -0.08 * k), (0.06 * k, -0.08 * k), (0.065 * k, 0.0), (-0.065 * k, 0.0)], tension=0.4)
        c.drawPath(up, paint(sh))
        c.drawRect(skia.Rect(-0.068 * k, -0.014 * k, 0.068 * k, 0.012 * k), paint(so))
    c.restore()


def draw_body(c, cd, p, view='front', e=None, t=0.0, head_scale=1.0):
    """Draw the full character into c (character space). view: front | back | side | tq"""
    k = cd.k
    b = cd.build
    side_view = view == 'side'
    back = view == 'back'
    ox, oy = p['x'], p['y'] + p['crouch'] * 0.35 * k
    sit = p.get('sit', 0.0)
    hip = (ox, lerp(cd.hip_y + oy, -0.46 * k, sit))
    lean = p['lean']
    lr = math.radians(lean)

    def rot_up(L):  # point L metres up the spine from hip
        return (hip[0] + math.sin(lr) * L, hip[1] - math.cos(lr) * L)

    spine_len = abs(cd.shoulder_y - cd.hip_y)
    sh_c = rot_up(spine_len)
    neck_c = rot_up(spine_len + 0.06 * k)
    breathe = p.get('breathe', 0.0)

    if side_view:
        hips = {'l': (hip[0] + 0.0, hip[1]), 'r': (hip[0] - 0.0, hip[1])}
        shs = {'l': (sh_c[0] + 0.01, sh_c[1] + 0.02), 'r': (sh_c[0] - 0.01, sh_c[1] + 0.02)}
    else:
        sw = cd.shoulder * b
        hw = cd.hip * 0.62
        hips = {'l': (hip[0] + hw, hip[1]), 'r': (hip[0] - hw, hip[1])}
        shs = {'l': (sh_c[0] + sw * 0.86, sh_c[1] + 0.03 * k), 'r': (sh_c[0] - sw * 0.86, sh_c[1] + 0.03 * k)}
    crouch = p['crouch']

    def leg(sidek, dark=0.0):
        hp = hips[sidek]
        ha = p[sidek + 'h'] if side_view else p[sidek + 'h']
        kn = p[sidek + 'k'] + crouch * 70
        ha = ha + crouch * 55 if side_view else ha
        thigh_l = cd.thigh
        shin_l = cd.shin
        if not side_view and crouch:
            thigh_l *= (1 - crouch * 0.55)
            shin_l *= (1 - crouch * 0.15)
        fs = p.get(sidek + 'fs', 0.0)
        if not side_view and fs:
            thigh_l *= (1 - 0.22 * fs)
        knee = _limb_end(hp, ha, thigh_l)
        ank = _limb_end(knee, ha - kn, shin_l)
        if not side_view and sit > 0:
            sgn = 1 if sidek == 'l' else -1
            kx = hp[0] + sgn * 0.04 * k
            knee = (lerp(knee[0], kx, sit), lerp(knee[1], hp[1] + 0.06 * k, sit))
            ank = (lerp(ank[0], kx, sit), lerp(ank[1], cd.ankle_y, sit))
            if sit > 0.5:
                c.drawPath(capsule(hp, knee, 0.20 * k, 0.17 * k), paint(mix(cd.pants, (0, 0, 0, 1), dark)))
        pc = mix(cd.pants, (0, 0, 0, 1), dark)
        c.drawPath(capsule(hp, knee, 0.165 * k * b, 0.12 * k), paint(pc))
        c.drawPath(capsule(knee, ank, 0.12 * k, 0.095 * k), paint(pc))
        # fold at knee
        c.drawLine(knee[0] - 0.03 * k, knee[1] - 0.01, knee[0] + 0.03 * k, knee[1] + 0.01, paint(mix(pc, (0, 0, 0, 1), 0.3), stroke=0.006))
        if side_view:
            _shoe(c, cd, (ank[0], ank[1] + 0.075 * k), p[sidek + 'f'] + crouch * 10, 'side', dark)
        else:
            _shoe(c, cd, (ank[0], ank[1] + 0.075 * k), 0, 'back' if back else 'front', dark)

    def arm(sidek, dark=0.0):
        sp = shs[sidek]
        sa = p[sidek + 's'] + lean
        ea = p[sidek + 'e']
        elbow = _limb_end(sp, sa, cd.uarm)
        wrist = _limb_end(elbow, sa + ea, cd.farm)
        tc = mix(cd.top, (0, 0, 0, 1), dark)
        c.drawPath(capsule(sp, elbow, 0.125 * k * b, 0.105 * k * b), paint(tc))
        c.drawPath(capsule(elbow, wrist, 0.105 * k * b, 0.088 * k), paint(tc))
        # sleeve folds + cuff
        c.drawLine(*_limb_end(elbow, sa + ea, 0.04), *_limb_end(elbow, sa + ea, 0.08),
                   paint(mix(tc, (0, 0, 0, 1), 0.35), stroke=0.007))
        cuff_a = _limb_end(elbow, sa + ea, cd.farm - 0.035 * k)
        c.drawPath(capsule(cuff_a, wrist, 0.09 * k, 0.088 * k), paint(mix(tc, (0, 0, 0, 1), 0.25)))
        kind = p[sidek + 'hand']
        _hand(c, cd, wrist, sa + ea, kind, view, 1 if sidek == 'l' else -1, dark=dark)

    def torso(dark=0.0):
        tc = mix(cd.top, (0, 0, 0, 1), dark)
        tdk = mix(cd.top_dark, (0, 0, 0, 1), dark)
        c.save()
        c.translate(*hip)
        c.rotate(lean)
        L = spine_len
        if side_view:
            pts = [(-0.11 * k * b, 0.05), (-0.12 * k * b, -L * 0.5), (-0.10 * k * b, -L * 0.95), (-0.03, -L - 0.05 * k),
                   (0.06 * k, -L - 0.03 * k), (0.12 * k * b, -L * 0.85), (0.135 * k * b + breathe * 0.01, -L * 0.6), (0.12 * k * b, -L * 0.25),
                   (0.12 * k * b, 0.05)]
        else:
            sw = cd.shoulder * b
            pts = [(-cd.hip * 1.12, 0.06), (-sw * 0.80, -L * 0.40), (-sw * 0.95, -L * 0.86), (-sw * 0.78, -L - 0.01 * k),
                   (-0.08 * k, -L - 0.07 * k), (0.08 * k, -L - 0.07 * k), (sw * 0.78, -L - 0.01 * k), (sw * 0.95, -L * 0.86),
                   (sw * 0.80, -L * 0.40), (cd.hip * 1.12, 0.06)]
        body = smooth_path(pts, tension=0.35)
        c.drawPath(body, paint(tc))
        c.save()
        c.clipPath(body, doAntiAlias=True)
        # hem rib band
        c.drawRect(skia.Rect(-0.4, -0.02, 0.4, 0.07), paint(tdk))
        for i in range(-12, 13):
            c.drawLine(i * 0.025, -0.015, i * 0.025, 0.065, paint(mix(tdk, (0, 0, 0, 1), 0.3), stroke=0.004))
        # sweater folds
        for (x0, y0, x1, y1) in ((-0.10, -0.10, -0.03, -0.30), (0.09, -0.12, 0.04, -0.28), (-0.05, -0.38, 0.06, -0.36)):
            c.drawLine(x0 * k, y0 * k, x1 * k, y1 * k, paint(tdk, stroke=0.012, blur=0.004))
        if cd.name == 'max':  # parka zip and pockets
            c.drawLine(0.0, 0.06, 0.0, -L - 0.05, paint(mix(tdk, (0, 0, 0, 1), 0.4), stroke=0.01))
            if not side_view:
                c.drawRect(skia.Rect(-0.17 * k, -0.20 * k, -0.06 * k, -0.08 * k), paint(tdk, stroke=0.006))
                c.drawRect(skia.Rect(0.06 * k, -0.20 * k, 0.17 * k, -0.08 * k), paint(tdk, stroke=0.006))
        if cd.name == 'lena':  # puffer quilting
            for i in range(1, 6):
                c.drawLine(-0.4, -L * i / 6, 0.4, -L * i / 6 + 0.01, paint(tdk, stroke=0.008))
        c.restore()
        # collar
        if not side_view:
            if back:
                c.drawRoundRect(skia.Rect(-0.085 * k, -L - 0.085 * k, 0.085 * k, -L - 0.035 * k), 0.03, 0.03, paint(tdk))
            elif cd.name == 'max':
                c.drawPath(smooth_path([(-0.13 * k, -L - 0.02), (-0.10 * k, -L - 0.11 * k), (0.10 * k, -L - 0.11 * k), (0.13 * k, -L - 0.02), (0.0, -L + 0.03)]), paint(tdk))
            else:
                col_p = skia.Path()
                col_p.moveTo(-0.075 * k, -L - 0.072 * k)
                col_p.quadTo(0.0, -L + 0.0 * k, 0.075 * k, -L - 0.072 * k)
                c.drawPath(col_p, paint(tdk, stroke=0.028 * k))
        if 'scarf' in cd.extra:
            sc = mix(cd.extra['scarf'], (0, 0, 0, 1), dark)
            c.drawPath(smooth_path([(-0.12 * k, -L - 0.02), (-0.10 * k, -L - 0.11 * k), (0.10 * k, -L - 0.11 * k), (0.12 * k, -L - 0.02), (0.0, -L + 0.02)]), paint(sc))
            if not back:
                c.drawRoundRect(skia.Rect(0.02 * k, -L + 0.0, 0.08 * k, -L + 0.22 * k), 0.02, 0.02, paint(mix(sc, (0, 0, 0, 1), 0.15)))
        c.restore()

    def backpack():
        if not p.get('pack'):
            return
        c.save()
        c.translate(*hip)
        c.rotate(lean)
        L = spine_len
        pc = (0.16, 0.17, 0.15, 1) if cd.name != 'lena' else (0.20, 0.17, 0.17, 1)
        if back:
            c.drawRoundRect(skia.Rect(-0.17 * k, -L + 0.02, 0.17 * k, -L * 0.18), 0.05, 0.05, paint(pc))
            c.drawRoundRect(skia.Rect(-0.13 * k, -L * 0.55, 0.13 * k, -L * 0.25), 0.03, 0.03, paint(mix(pc, (0, 0, 0, 1), 0.3)))
            c.drawLine(-0.12 * k, -L * 0.62, 0.12 * k, -L * 0.62, paint((0.05, 0.05, 0.05), stroke=0.01))
        elif side_view:
            c.drawRoundRect(skia.Rect(-0.30 * k, -L + 0.04, -0.09 * k, -L * 0.2), 0.05, 0.05, paint(pc))
        else:
            for sx in (-1, 1):
                c.drawLine(sx * 0.12 * k, -L - 0.02, sx * 0.13 * k, -L * 0.45, paint(mix(pc, (0, 0, 0, 1), 0.2), stroke=0.035 * k))
        c.restore()

    def neck():
        ncol = mix(cd.skin, (0.25, 0.12, 0.10, 1), 0.3)
        c.drawPath(capsule((sh_c[0], sh_c[1] + 0.02), (neck_c[0], neck_c[1] - 0.03 * k), 0.095 * k, 0.088 * k), paint(ncol))

    def head():
        hs = cd.head_h * k * head_scale
        hc = (neck_c[0] + math.sin(lr) * hs * 0.45, neck_c[1] - hs * 0.42)
        c.save()
        c.translate(hc[0], hc[1] - hs * 0.10)
        c.rotate(p['head'] + lean * 0.3)
        c.scale(hs, hs)
        if side_view:
            draw_head_side(c, cd, e, t)
        else:
            draw_head_front(c, cd, math.radians(p['yaw']) if not back else 0.0, e, t, back=back)
        c.restore()

    if side_view:
        arm('r', dark=0.35)
        leg('r', dark=0.30)
        neck()
        backpack()
        torso()
        leg('l')
        head()
        arm('l')
    elif back:
        leg('l')
        leg('r')
        arm('l')
        arm('r')
        neck()
        torso()
        head()
        backpack()
    else:
        leg('l')
        leg('r')
        neck()
        torso()
        backpack()
        head()
        arm('l')
        arm('r')


def record(fn, bounds=(-2, -4, 2, 1)):
    rec = skia.PictureRecorder()
    cc = rec.beginRecording(skia.Rect(*bounds))
    fn(cc)
    return rec.finishRecordingAsPicture()


def draw_character(c, cd, p, view='front', e=None, light=None, t=0.0, flip=False, shadow=True,
                   blur_px=None, head_scale=1.0):
    """Draw a lit character at the current canvas origin (feet), already scaled to metres."""
    light = light or Light()
    if shadow:
        c.drawOval(skia.Rect(-0.42 * cd.k, -0.05, 0.42 * cd.k, 0.05), paint((0, 0, 0), alpha=0.55, blur=0.05))
    pic = record(lambda cc: draw_body(cc, cd, p, view, e, t, head_scale))
    c.save()
    if flip:
        c.scale(-1, 1)
        lt = Light(**{**light.__dict__})
        lt.rim_side = -light.rim_side
        lt.warm_side = -light.warm_side
        light = lt
    lit_draw(c, pic, light, blur_px=blur_px)
    c.restore()


def draw_portrait(c, cd, yaw=0.0, e=None, light=None, t=0.0, neck=True, back=False, side=False):
    """Close-up head + shoulders, unit = head height. Origin = head centre (eye line)."""
    light = light or Light()

    def body(cc):
        k = 1.0
        if neck:
            ncol = mix(cd.skin, (0.25, 0.12, 0.10, 1), 0.3)
            cc.drawPath(capsule((0.0 + math.sin(yaw) * 0.05, 0.3), (0.0, 0.72), 0.40, 0.46), paint(ncol))
            # shoulders / sweater
            tc = cd.top
            sw = cd.shoulder / cd.head_h * 1.05
            sh = smooth_path([(-sw * 1.25, 2.4), (-sw * 1.15, 1.10), (-sw * 0.85, 0.74), (-0.30, 0.62), (0.30, 0.62),
                              (sw * 0.85, 0.74), (sw * 1.15, 1.10), (sw * 1.25, 2.4)], tension=0.35)
            cc.drawPath(sh, paint(tc))
            if cd.name == 'hero' or cd.name == 'lena':
                cp = skia.Path()
                cp.moveTo(-0.30, 0.62)
                cp.quadTo(0.0, 0.92, 0.30, 0.62)
                cc.drawPath(cp, paint(cd.top_dark, stroke=0.10))
            if 'scarf' in cd.extra:
                cc.drawPath(smooth_path([(-0.55, 0.85), (-0.45, 0.55), (0.45, 0.55), (0.55, 0.85), (0.0, 1.0)]), paint(cd.extra['scarf']))
            if cd.name == 'max':
                cc.drawPath(smooth_path([(-0.55, 0.95), (-0.42, 0.50), (0.42, 0.50), (0.55, 0.95), (0.0, 0.85)]), paint(cd.top_dark))
                cc.drawLine(0.0, 0.88, 0.0, 2.4, paint((0.05, 0.06, 0.05), stroke=0.03))
            for (x0, y0, x1, y1) in ((-0.9, 1.3, -0.6, 1.8), (0.85, 1.25, 0.6, 1.9)):
                cc.drawLine(x0, y0, x1, y1, paint(cd.top_dark, stroke=0.05, blur=0.02))
        if side:
            draw_head_side(cc, cd, e, t)
        else:
            draw_head_front(cc, cd, yaw, e, t, back=back)

    pic = record(body, bounds=(-2.5, -1.5, 2.5, 3))
    lit_draw(c, pic, light)


# ---------------------------------------------------------------------------
# THE TALL MAN (Slenderman) - one fixed design
# ---------------------------------------------------------------------------
SLENDER_H = 2.95


def draw_slender(c, t=0.0, tilt=6.0, sway=1.0, arm_spread=0.0, light=None, alpha=1.0, blur_px=None,
                 distort=0.0, seed=0):
    """Feet at origin, metres, y down. Featureless white face, black suit, white shirt, dark tie."""
    light = light or Light(amb=(0.55, 0.6, 0.72), rim_k=0.7, shade=0.5)
    sw = math.sin(t * 0.6 + seed) * 0.8 * sway

    def body(cc):
        suit = (0.035, 0.035, 0.045, 1)
        suit_hi = (0.10, 0.10, 0.12, 1)
        shirt = (0.80, 0.81, 0.84, 1)
        skin = (0.90, 0.90, 0.92, 1)
        Hh = SLENDER_H
        hip_y = -1.45
        sh_y = -2.42
        cc.save()
        cc.rotate(sw * 0.3)
        # legs - very long and thin
        for s in (-1, 1):
            leg = poly([(s * 0.045, hip_y), (s * 0.13, hip_y), (s * 0.10, -0.05), (s * 0.04, -0.05)])
            cc.drawPath(leg, paint(suit))
            cc.drawPath(smooth_path([(s * 0.035, -0.06), (s * 0.12, -0.06), (s * 0.15 + s * 0.06, 0.0), (s * 0.03, 0.0)]), paint((0.02, 0.02, 0.02)))
        # arms (behind torso edges), extremely long
        for s in (-1, 1):
            ang = s * (3 + arm_spread * 18)
            a = (s * 0.21, sh_y + 0.05)
            el = _limb_end(a, ang, 0.62)
            wr = _limb_end(el, ang + s * arm_spread * 8, 0.62)
            cc.drawPath(capsule(a, el, 0.10, 0.085), paint(suit))
            cc.drawPath(capsule(el, wr, 0.085, 0.075), paint(suit))
            cc.drawPath(capsule(_limb_end(el, ang, 0.56), wr, 0.08, 0.08), paint((0.6, 0.6, 0.62)))
            # pale hand with long fingers
            cc.save()
            cc.translate(*wr)
            cc.rotate(-ang)
            cc.drawPath(smooth_path([(-0.04, 0.0), (0.04, 0.0), (0.045, 0.08), (-0.045, 0.08)]), paint(skin))
            for i in range(4):
                x = -0.03 + i * 0.02
                L = 0.20 - abs(i - 1.5) * 0.02
                cc.drawPath(capsule((x, 0.06), (x + (i - 1.5) * 0.008, 0.06 + L), 0.016, 0.010), paint(skin))
            cc.drawPath(capsule((-s * 0.04, 0.03), (-s * 0.06, 0.12), 0.017, 0.011), paint(skin))
            cc.restore()
        # torso / jacket
        jacket = smooth_path([(-0.15, hip_y + 0.18), (-0.17, hip_y - 0.3), (-0.235, sh_y + 0.08), (-0.20, sh_y - 0.02),
                              (-0.06, sh_y - 0.06), (0.06, sh_y - 0.06), (0.20, sh_y - 0.02), (0.235, sh_y + 0.08),
                              (0.17, hip_y - 0.3), (0.15, hip_y + 0.18)], tension=0.3)
        cc.drawPath(jacket, paint(suit))
        # shirt V and tie
        v = poly([(-0.075, sh_y - 0.04), (0.075, sh_y - 0.04), (0.0, sh_y + 0.42)])
        cc.drawPath(v, paint(shirt))
        tie = poly([(-0.022, sh_y - 0.02), (0.022, sh_y - 0.02), (0.03, sh_y + 0.34), (0.0, sh_y + 0.40), (-0.03, sh_y + 0.34)])
        cc.drawPath(tie, paint((0.07, 0.07, 0.09)))
        cc.drawPath(poly([(-0.03, sh_y - 0.03), (0.03, sh_y - 0.03), (0.018, sh_y + 0.02), (-0.018, sh_y + 0.02)]), paint((0.09, 0.09, 0.11)))
        # lapels
        for s in (-1, 1):
            lap = poly([(s * 0.075, sh_y - 0.05), (s * 0.13, sh_y + 0.10), (s * 0.08, sh_y + 0.12), (s * 0.002, sh_y + 0.44)])
            cc.drawPath(lap, paint(suit_hi))
        # buttons + pocket square line
        cc.drawCircle(0.0, sh_y + 0.55, 0.012, paint((0.12, 0.12, 0.14)))
        cc.drawLine(0.0, sh_y + 0.45, 0.0, hip_y + 0.18, paint((0.0, 0.0, 0.0), stroke=0.008))
        cc.drawLine(-0.15, hip_y + 0.0, -0.05, hip_y + 0.02, paint(suit_hi, stroke=0.01))
        cc.drawLine(0.05, hip_y + 0.02, 0.15, hip_y + 0.0, paint(suit_hi, stroke=0.01))
        # neck + head (featureless)
        cc.drawPath(capsule((0.0, sh_y - 0.03), (0.0, sh_y - 0.12), 0.075, 0.07), paint((0.75, 0.75, 0.78)))
        cc.save()
        cc.translate(0.0, sh_y - 0.27)
        cc.rotate(tilt + sw * 2)
        head = smooth_path([(0.0, -0.20), (0.12, -0.15), (0.14, 0.0), (0.11, 0.14), (0.0, 0.19), (-0.11, 0.14), (-0.14, 0.0), (-0.12, -0.15)], tension=0.45)
        cc.drawPath(head, paint(skin))
        cc.save()
        cc.clipPath(head, doAntiAlias=True)
        cc.drawOval(skia.Rect(0.02, -0.25, 0.25, 0.25), paint((0.55, 0.56, 0.62), alpha=0.6, blur=0.05))
        cc.drawOval(skia.Rect(-0.08, -0.06, -0.02, 0.0), paint((0.6, 0.6, 0.66), alpha=0.25, blur=0.02))   # faint sockets
        cc.drawOval(skia.Rect(0.02, -0.06, 0.08, 0.0), paint((0.6, 0.6, 0.66), alpha=0.25, blur=0.02))
        cc.restore()
        cc.restore()
        cc.restore()

    pic = record(body, bounds=(-1.5, -3.5, 1.5, 0.5))
    p = skia.Paint()
    p.setAlphaf(alpha)
    if blur_px:
        p.setImageFilter(skia.ImageFilters.Blur(blur_px, blur_px))
    c.saveLayer(skia.Rect(-1.6, -3.6, 1.6, 0.6), p)
    if distort > 0:
        # glitch: horizontal slices displaced
        rng = random.Random(int(t * 30) + seed)
        y = -3.4
        while y < 0.2:
            hgt = rng.uniform(0.05, 0.3)
            dx = rng.uniform(-1, 1) * distort * 0.25
            c.save()
            c.clipRect(skia.Rect(-1.6, y, 1.6, y + hgt))
            c.translate(dx, 0)
            lit_draw(c, pic, light)
            c.restore()
            y += hgt
    else:
        lit_draw(c, pic, light)
    c.restore()
