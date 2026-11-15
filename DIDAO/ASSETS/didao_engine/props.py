"""DIDAO engine - props: tent, campfire, flashlight beam, phone, carved bark."""
import math
import random

import skia

from .core import (W, H, clamp, col, fbm, hexc, lerp, lin_grad, mix, paint, poly, rad_grad,
                   smooth_path, tint_filter, vnoise, FONT_DIR, draw_text)
from .characters import Light, lit_draw, record

TENT_COL = hexc('#3b4436')
TENT_DARK = hexc('#262c23')
TENT_FLY = hexc('#4a5444')


# ---------------------------------------------------------------------------
# tent (exterior). metres, origin = centre of the front base, y down.
# ---------------------------------------------------------------------------
def draw_tent(c, t=0.0, door=0.0, wind=0.3, light=None, glow_inside=0.0, skew=0.25):
    light = light or Light(amb=(0.45, 0.5, 0.62), rim_k=0.6, shade=0.45)

    def w(x, y, i):
        return (x + wind * 0.025 * vnoise(t * 1.7 + i * 0.7, 3) * (-y), y + wind * 0.02 * vnoise(t * 1.3 + i, 8) * (-y))

    def body(cc):
        Wd, Ht = 1.15, 1.15
        side = poly([(Wd, 0.0), (Wd + skew * 1.5, -0.10), (Wd * 0.2 + skew * 1.5, -Ht + 0.02), (0.0, -Ht)])
        cc.drawPath(smooth_path([w(*p, i) for i, p in enumerate([(Wd, 0.0), (Wd + skew * 1.6, -0.08), (Wd * 0.55 + skew * 1.6, -Ht * 0.80),
                                                                    (skew * 1.2, -Ht - 0.02), (0.0, -Ht)])], tension=0.3),
                    paint(mix(TENT_COL, (0, 0, 0, 1), 0.25)))
        front = smooth_path([w(*p, i) for i, p in enumerate([(-Wd, 0.0), (-Wd * 0.92, -Ht * 0.55), (-Wd * 0.55, -Ht * 0.93), (0.0, -Ht),
                                                              (Wd * 0.55, -Ht * 0.93), (Wd * 0.92, -Ht * 0.55), (Wd, 0.0)])], tension=0.45)
        cc.drawPath(front, paint(TENT_COL))
        cc.save()
        cc.clipPath(front, doAntiAlias=True)
        # seams / poles
        for sx in (-0.62, 0.62):
            pth = skia.Path()
            pth.moveTo(sx * Wd * 1.25, 0.0)
            pth.quadTo(sx * 0.6, -Ht * 1.15, 0.0, -Ht - 0.05)
            cc.drawPath(pth, paint(TENT_DARK, stroke=0.025))
        # fabric folds
        for i in range(7):
            x = -0.9 + i * 0.3
            cc.drawLine(x, 0.0, x * 0.5, -Ht * 0.7, paint(TENT_DARK, alpha=0.35, stroke=0.04, blur=0.02))
        # door
        dh = 0.95
        dw = 0.48
        door_p = smooth_path([(-dw, 0.0), (-dw * 0.85, -dh * 0.75), (0.0, -dh), (dw * 0.85, -dh * 0.75), (dw, 0.0)], tension=0.45)
        if door > 0:
            inner = (0.02, 0.02, 0.025, 1)
            if glow_inside:
                inner = mix(inner, (0.35, 0.42, 0.55, 1), glow_inside)
            cc.save()
            cc.clipPath(door_p, doAntiAlias=True)
            cc.drawRect(skia.Rect(-1, -1.2, 1, 0.1), paint(inner))
            # rolled flap
            fl = dw * 2 * (1 - door)
            cc.drawPath(smooth_path([(-dw, 0.0), (-dw + fl, 0.0), (-dw + fl * 0.8, -dh * 0.8), (-dw * 0.4, -dh * 0.98), (-dw * 0.85, -dh * 0.75)], tension=0.4),
                        paint(mix(TENT_COL, (0, 0, 0, 1), 0.15)))
            cc.restore()
            cc.drawPath(door_p, paint(TENT_DARK, stroke=0.02))
        else:
            cc.drawPath(door_p, paint(TENT_DARK, stroke=0.02))
            cc.drawLine(0.0, -dh, 0.0, 0.0, paint((0.1, 0.1, 0.1), stroke=0.012))
            cc.drawCircle(0.02, -dh * 0.55, 0.018, paint((0.5, 0.5, 0.5)))
        if glow_inside > 0 and door <= 0:
            cc.drawRect(skia.Rect(-1.2, -1.2, 1.2, 0.1), paint((0.9, 0.8, 0.6), alpha=0.25 * glow_inside, blend=skia.BlendMode.kScreen))
        cc.restore()
        # fly sheet / rain cover edge
        cc.drawPath(smooth_path([w(*p, i + 20) for i, p in enumerate([(-Wd * 0.6, -Ht * 0.9), (0.0, -Ht - 0.06), (Wd * 0.6, -Ht * 0.9), (0.0, -Ht + 0.12)])]),
                    paint(TENT_FLY))
        # guy ropes + pegs
        for (a, b) in (((-Wd * 0.85, -Ht * 0.6), (-Wd - 0.55, 0.0)), ((Wd * 0.85, -Ht * 0.6), (Wd + 0.6 + skew, 0.02))):
            cc.drawLine(*a, *b, paint((0.55, 0.55, 0.5), alpha=0.6, stroke=0.006))
            cc.drawLine(b[0], b[1] - 0.06, b[0], b[1] + 0.01, paint((0.4, 0.4, 0.42), stroke=0.012))
        # ground shadow
    cpic = record(body, bounds=(-2.5, -2, 2.5, 0.5))
    c.drawOval(skia.Rect(-1.5, -0.08, 1.7 + skew, 0.10), paint((0, 0, 0), alpha=0.55, blur=0.08))
    lit_draw(c, cpic, light)


# ---------------------------------------------------------------------------
# campfire. metres, origin = centre of fire pit on the ground.
# ---------------------------------------------------------------------------
def draw_fire(c, t, intensity=1.0, light=None, embers=1.0, seed=0, smoke=0.3):
    light = light or Light(amb=(0.4, 0.45, 0.55), rim_k=0.3)
    rng = random.Random(seed)
    # stones ring
    stones = []
    for i in range(11):
        a = i / 11 * 2 * math.pi + rng.uniform(-0.1, 0.1)
        stones.append((math.cos(a) * 0.42, math.sin(a) * 0.14, rng.uniform(0.07, 0.11), a))
    back = [s for s in stones if s[1] < 0]
    front = [s for s in stones if s[1] >= 0]

    def stone(s):
        x, y, r, a = s
        c.drawOval(skia.Rect(x - r, y - r * 0.85, x + r, y + r * 0.4), paint((0.16, 0.17, 0.19)))
        c.drawOval(skia.Rect(x - r * 0.8, y - r * 0.85, x + r * 0.5, y - r * 0.2), paint((0.30, 0.31, 0.33), alpha=0.6, blur=0.01))
        if intensity > 0:
            c.drawOval(skia.Rect(x - r, y - r * 0.85, x + r, y + r * 0.4), paint((1.0, 0.45, 0.15), alpha=0.35 * intensity, blend=skia.BlendMode.kPlus, blur=0.02))

    for s in back:
        stone(s)
    # ash bed
    c.drawOval(skia.Rect(-0.36, -0.10, 0.36, 0.10), paint((0.06, 0.05, 0.05)))
    # logs
    for (x0, y0, x1, y1) in ((-0.32, 0.05, 0.22, -0.12), (0.30, 0.06, -0.18, -0.14), (-0.05, 0.10, 0.06, -0.20)):
        c.drawLine(x0, y0, x1, y1, paint((0.17, 0.11, 0.08), stroke=0.075))
        c.drawLine(x0, y0 - 0.02, x1, y1 - 0.02, paint((0.30, 0.20, 0.14), alpha=0.5, stroke=0.02))
    # embers in the bed
    if embers > 0:
        for i in range(14):
            ex = rng.uniform(-0.25, 0.25)
            ey = rng.uniform(-0.12, 0.06)
            fl = 0.6 + 0.4 * vnoise(t * 4 + i * 3.1, 11)
            c.drawCircle(ex, ey, 0.02 + rng.uniform(0, 0.02),
                         paint((1.0, 0.35 + 0.2 * fl, 0.08), alpha=embers * fl * 0.9, blend=skia.BlendMode.kPlus, blur=0.008))
    # flames
    if intensity > 0.01:
        layers = [((0.85, 0.18, 0.05), 1.0, 0.85), ((1.0, 0.48, 0.10), 0.75, 0.9), ((1.0, 0.82, 0.45), 0.45, 0.9)]
        for li, (fc, scale, a) in enumerate(layers):
            for i in range(7):
                bx = (i - 3) * 0.06 * (1.2 - li * 0.25)
                hh = (0.55 + 0.35 * fbm(t * 2.6 + i * 1.7, 31 + i)) * intensity * scale * (1.0 - abs(i - 3) * 0.12)
                sway = 0.10 * fbm(t * 2.0 + i, 7 + i) * hh
                bw = 0.09 * scale + 0.02
                fp = skia.Path()
                fp.moveTo(bx - bw, 0.0)
                fp.cubicTo(bx - bw * 1.2, -hh * 0.45, bx + sway * 0.5 - bw * 0.3, -hh * 0.7, bx + sway, -hh)
                fp.cubicTo(bx + sway * 0.5 + bw * 0.3, -hh * 0.7, bx + bw * 1.2, -hh * 0.45, bx + bw, 0.0)
                fp.close()
                c.drawPath(fp, paint(fc, alpha=a * min(1, intensity * 1.5), blend=skia.BlendMode.kPlus, blur=0.012 + 0.01 * li))
        # core glow
        c.drawOval(skia.Rect(-0.25, -0.30 * intensity, 0.25, 0.05), paint((1.0, 0.6, 0.25), alpha=0.35 * intensity, blend=skia.BlendMode.kPlus, blur=0.08))
        # sparks
        for i in range(16):
            ph = (t * 0.45 + i * 0.137) % 1.0
            sx = (vnoise(i * 9.1, 5) * 0.25) + 0.12 * vnoise(t * 1.5 + i, 17) * ph
            sy = -0.2 - ph * 1.6 * intensity
            a = (1 - ph) * intensity
            c.drawCircle(sx, sy, 0.008, paint((1.0, 0.6, 0.2), alpha=a, blend=skia.BlendMode.kPlus))
    if smoke > 0:
        for i in range(6):
            ph = (t * 0.12 + i / 6) % 1.0
            sx = 0.3 * vnoise(t * 0.3 + i * 4, 21) * ph
            r = 0.15 + ph * 0.6
            c.drawCircle(sx, -0.5 - ph * 2.5, r, paint((0.5, 0.55, 0.6), alpha=smoke * 0.18 * math.sin(ph * math.pi), blur=0.12))
    for s in front:
        stone(s)


def fire_glow(c, sx, sy, s, intensity, t, radius_m=4.5):
    """Screen-space warm light pool around the fire (additive)."""
    if intensity <= 0:
        return
    fl = 0.88 + 0.12 * fbm(t * 5.0, 99)
    r = min(radius_m * s, 1100) * fl
    intensity *= 0.6
    c.drawCircle(sx, sy - 0.4 * s, r, paint(shader=rad_grad((sx, sy - 0.4 * s), r,
                 [(1.0, 0.45, 0.15, 0.45 * intensity), (0.8, 0.30, 0.10, 0.16 * intensity), (0.5, 0.2, 0.1, 0.0)], [0, 0.35, 1]),
                 blend=skia.BlendMode.kPlus))
    # ground pool (flattened)
    c.save()
    c.translate(sx, sy)
    c.scale(1, 0.28)
    rr = r * 0.8
    c.drawCircle(0, 0, rr, paint(shader=rad_grad((0, 0), rr, [(1.0, 0.5, 0.2, 0.35 * intensity), (1.0, 0.4, 0.1, 0.0)]), blend=skia.BlendMode.kPlus))
    c.restore()


# ---------------------------------------------------------------------------
# flashlight beam (screen space)
# ---------------------------------------------------------------------------
def draw_beam(c, origin, target, strength=1.0, spread=0.20, t=0.0, flicker=0.0, hotspot_r=None):
    if strength <= 0:
        return
    if flicker:
        strength *= (0.2 if (int(t * 24) % 3 == 0 and flicker > 0.5) else 1.0) * (1 - 0.6 * flicker * abs(vnoise(t * 30, 4)))
    ox, oy = origin
    tx, ty = target
    dx, dy = tx - ox, ty - oy
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    w1 = L * spread
    cone = poly([(ox + nx * 6, oy + ny * 6), (tx + nx * w1, ty + ny * w1), (tx - nx * w1, ty - ny * w1), (ox - nx * 6, oy - ny * 6)])
    sh = lin_grad((ox, oy), (tx, ty), [(0.9, 0.93, 1.0, 0.42 * strength), (0.8, 0.85, 0.95, 0.10 * strength)])
    c.drawPath(cone, paint(shader=sh, blend=skia.BlendMode.kPlus, blur=10))
    hr = hotspot_r or w1 * 1.1
    c.drawCircle(tx, ty, hr, paint(shader=rad_grad((tx, ty), hr, [(0.95, 0.97, 1.0, 0.5 * strength), (0.8, 0.85, 0.95, 0.12 * strength), (0.8, 0.85, 0.95, 0.0)], [0, 0.5, 1]),
                                    blend=skia.BlendMode.kPlus))
    # dust motes in the beam
    rng = random.Random(5)
    for i in range(40):
        u = rng.random()
        v = rng.uniform(-1, 1)
        px = ox + dx * u + nx * v * w1 * u + 6 * math.sin(t * 0.7 + i)
        py = oy + dy * u + ny * v * w1 * u + 6 * math.cos(t * 0.5 + i * 2)
        c.drawCircle(px, py, 1.6, paint((1, 1, 1), alpha=0.35 * strength * (1 - u * 0.5)))
    c.drawCircle(ox, oy, 26, paint(shader=rad_grad((ox, oy), 26, [(1, 1, 1, 0.9 * strength), (1, 1, 1, 0)]), blend=skia.BlendMode.kPlus))


# ---------------------------------------------------------------------------
# phone close-up (screen space, centred at cx, cy, height ph px)
# ---------------------------------------------------------------------------
def draw_phone(c, cx, cy, ph, t, screen_on=1.0, notif=0.0, buzz=0.0, angle=-4.0, skin=hexc('#c9a389'),
               sleeve=hexc('#262b36'), time_text='3:17', lang='en'):
    pw = ph * 0.48
    shake = buzz * 6 * math.sin(t * 90)
    c.save()
    c.translate(cx + shake, cy)
    c.rotate(angle)
    # back hand (left) - palm behind phone
    skin_d = mix(skin, (0.2, 0.1, 0.08, 1), 0.45)
    c.drawPath(smooth_path([(-pw * 0.62, ph * 0.95), (-pw * 0.62, ph * 0.25), (-pw * 0.40, ph * 0.10), (pw * 0.45, ph * 0.12),
                            (pw * 0.62, ph * 0.30), (pw * 0.62, ph * 0.95)]), paint(skin_d))
    c.drawRect(skia.Rect(-pw * 0.75, ph * 0.62, pw * 0.75, ph * 1.3), paint(sleeve))
    # phone body
    body = skia.RRect.MakeRectXY(skia.Rect(-pw / 2, -ph / 2, pw / 2, ph / 2), pw * 0.13, pw * 0.13)
    c.drawRRect(body, paint((0.05, 0.05, 0.06)))
    c.drawRRect(body, paint((0.35, 0.37, 0.42), stroke=3))
    scr = skia.RRect.MakeRectXY(skia.Rect(-pw / 2 + 10, -ph / 2 + 10, pw / 2 - 10, ph / 2 - 10), pw * 0.11, pw * 0.11)
    # wallpaper: dark night gradient
    c.save()
    c.clipRRect(scr, doAntiAlias=True)
    so = screen_on
    c.drawRect(scr.rect(), paint(shader=lin_grad((0, -ph / 2), (0, ph / 2), [(0.10 * so, 0.13 * so, 0.22 * so, 1), (0.02, 0.03, 0.06, 1)])))
    if so > 0:
        # status bar: time + "no signal"
        tf = 'dejavu/DejaVuSans.ttf'
        draw_text(c, time_text, 0, -ph * 0.30, 'dejavu/DejaVuSans-Bold.ttf', ph * 0.11, (0.92, 0.94, 1.0), alpha=0.9 * so)
        # no-signal bars (empty) + cross
        bx = pw * 0.30
        by = -ph * 0.455
        for i in range(4):
            hh = 4 + i * 3
            c.drawRect(skia.Rect(bx + i * 7, by - hh, bx + i * 7 + 4, by), paint((1, 1, 1), alpha=0.25 * so))
        c.drawLine(bx - 2, by - 14, bx + 26, by + 2, paint((1, 0.4, 0.4), alpha=0.8 * so, stroke=2))
        # notification card
        if notif > 0:
            e = clamp(notif)
            ny = lerp(-ph * 0.25, -ph * 0.12, 1 - (1 - e) ** 3)
            card = skia.RRect.MakeRectXY(skia.Rect(-pw * 0.43, ny, pw * 0.43, ny + ph * 0.25), 16, 16)
            c.drawRRect(card, paint((0.18, 0.19, 0.23), alpha=0.94 * e))
            c.drawRRect(card, paint((1, 1, 1), alpha=0.08 * e, stroke=1.5))
            ix, iy = -pw * 0.43 + 34, ny + ph * 0.04
            c.drawRoundRect(skia.Rect(ix - 16, iy - 16, ix + 16, iy + 16), 8, 8, paint((0.28, 0.30, 0.36), alpha=e))
            c.drawOval(skia.Rect(ix - 10, iy - 7, ix + 10, iy + 6), paint((0.85, 0.87, 0.9), alpha=e))
            c.drawPath(poly([(ix - 5, iy + 3), (ix - 9, iy + 11), (ix + 1, iy + 5)]), paint((0.85, 0.87, 0.9), alpha=e))
            draw_text(c, 'UNKNOWN', ix + 28, iy + ph * 0.011, 'dejavu/DejaVuSans-Bold.ttf', ph * 0.028, (0.80, 0.82, 0.88), align='left', alpha=0.9 * e)
            draw_text(c, 'now', pw * 0.43 - 18, iy + ph * 0.011, 'dejavu/DejaVuSans.ttf', ph * 0.024, (0.65, 0.67, 0.72), align='right', alpha=0.8 * e)
            draw_text(c, 'I CAN SEE', -pw * 0.43 + 22, ny + ph * 0.135, 'dejavu/DejaVuSans-Bold.ttf', ph * 0.060,
                      (1.0, 1.0, 1.0), align='left', alpha=e)
            draw_text(c, 'YOU ALL.', -pw * 0.43 + 22, ny + ph * 0.21, 'dejavu/DejaVuSans-Bold.ttf', ph * 0.060,
                      (1.0, 1.0, 1.0), align='left', alpha=e)
    c.restore()
    # screen glow on the glass edge
    c.drawRRect(scr, paint((0.6, 0.7, 1.0), alpha=0.08 * screen_on, stroke=2))
    # front hand: thumb + fingers wrapping around the right edge
    c.drawPath(smooth_path([(pw * 0.50, ph * 0.60), (pw * 0.56, ph * 0.25), (pw * 0.60, ph * 0.10), (pw * 0.68, ph * 0.12),
                            (pw * 0.72, ph * 0.40), (pw * 0.68, ph * 0.75)]), paint(skin))
    for i in range(3):
        fy = ph * 0.12 + i * ph * 0.085
        c.drawPath(smooth_path([(pw * 0.505, fy), (pw * 0.54, fy - ph * 0.03), (pw * 0.64, fy - ph * 0.025), (pw * 0.66, fy + ph * 0.04), (pw * 0.52, fy + ph * 0.05)]),
                   paint(skin))
        c.drawLine(pw * 0.53, fy + ph * 0.045, pw * 0.64, fy + ph * 0.04, paint(skin_d, alpha=0.6, stroke=2))
    # left thumb over the left edge
    c.drawPath(smooth_path([(-pw * 0.68, ph * 0.48), (-pw * 0.60, ph * 0.22), (-pw * 0.50, ph * 0.16), (-pw * 0.46, ph * 0.22), (-pw * 0.53, ph * 0.44)]),
               paint(skin))
    c.drawOval(skia.Rect(-pw * 0.52, ph * 0.17, -pw * 0.46, ph * 0.22), paint((0.95, 0.85, 0.8), alpha=0.4))
    c.restore()
    # light spill from the screen
    if screen_on > 0:
        r = ph * 1.1
        c.drawCircle(cx, cy, r, paint(shader=rad_grad((cx, cy), r, [(0.55, 0.65, 0.95, 0.20 * screen_on), (0.3, 0.4, 0.7, 0.0)]),
                                      blend=skia.BlendMode.kPlus))


# ---------------------------------------------------------------------------
# bark + carving (screen space full-frame)
# ---------------------------------------------------------------------------
def draw_bark(c, x0, y0, w, h, seed=3, light=(0.55, 0.6, 0.6), moss=True, lit=1.0):
    """Old pine bark: irregular scaly plates separated by deep dark fissures."""
    rng = random.Random(seed)
    c.drawRect(skia.Rect(x0, y0, x0 + w, y0 + h), paint((0.035, 0.03, 0.028)))
    x = x0 - 60
    col_i = 0
    while x < x0 + w + 60:
        pw = rng.uniform(80, 160)
        y = y0 - rng.uniform(0, 200)
        while y < y0 + h + 100:
            ph = rng.uniform(140, 320)
            j = lambda m: rng.uniform(-m, m)
            pts = [(x + j(10), y + j(8)), (x + pw * 0.5 + j(14), y - 6 + j(10)), (x + pw + j(10), y + j(8)),
                   (x + pw + 6 + j(8), y + ph * 0.5 + j(20)), (x + pw + j(10), y + ph + j(8)),
                   (x + pw * 0.5 + j(14), y + ph + 6 + j(10)), (x + j(10), y + ph + j(8)), (x - 6 + j(8), y + ph * 0.5 + j(20))]
            v = rng.uniform(0.7, 1.15)
            pc = mix(hexc('#3a332d'), hexc('#5a5249'), rng.random() * 0.7)
            pc = (pc[0] * v * lit, pc[1] * v * lit, pc[2] * v * lit, 1)
            pp = smooth_path(pts, tension=0.18)
            c.drawPath(pp, paint(pc))
            c.save()
            c.clipPath(pp, doAntiAlias=True)
            c.drawOval(skia.Rect(x - pw * 0.2, y - ph * 0.2, x + pw * 0.55, y + ph * 0.6), paint((1, 1, 1), alpha=0.06 * lit, blur=18))
            c.drawRect(skia.Rect(x + pw * 0.6, y - 20, x + pw + 20, y + ph + 20), paint((0, 0, 0), alpha=0.35, blur=16))
            c.drawRect(skia.Rect(x - 10, y + ph * 0.75, x + pw + 10, y + ph + 20), paint((0, 0, 0), alpha=0.3, blur=12))
            for k in range(rng.randint(2, 6)):
                yy = y + rng.uniform(0.15, 0.85) * ph
                c.drawLine(x + rng.uniform(5, 25), yy, x + pw - rng.uniform(5, 25), yy + rng.uniform(-8, 8),
                           paint((0, 0, 0), alpha=0.22, stroke=rng.uniform(1, 2.5)))
            c.restore()
            if moss and rng.random() < 0.12:
                mx, my = x + rng.uniform(0, pw), y + rng.uniform(0, ph)
                for k in range(40):
                    c.drawCircle(mx + rng.gauss(0, 20), my + rng.gauss(0, 14), rng.uniform(2, 5),
                                 paint(mix(hexc('#2f3a26'), hexc('#4a5636'), rng.random()), alpha=0.7 * lit))
            y += ph * rng.uniform(0.98, 1.06)
        x += pw * rng.uniform(1.0, 1.06)
        col_i += 1


def draw_carving(c, cx, cy, lines=('DO NOT', 'LOOK', 'BACK'), size=170, reveal=1.0, seed=4, lit=1.0):
    """Knife-carved letters with raw wood inside and dark cut edges. reveal 0..1 draws strokes progressively."""
    tf = skia.Typeface.MakeFromFile(FONT_DIR + 'dejavu/DejaVuSans-Bold.ttf')
    rng = random.Random(seed)
    lh = size * 1.12
    total = sum(len(l) for l in lines)
    shown = reveal * total
    idx = 0
    for li, line in enumerate(lines):
        font = skia.Font(tf, size)
        font.setScaleX(0.86)
        wline = font.measureText(line) * 1.0
        x = cx - wline / 2
        y = cy + (li - (len(lines) - 1) / 2) * lh + size * 0.36
        for ch in line:
            adv = font.measureText(ch)
            if ch != ' ':
                a = clamp(shown - idx)
                if a > 0:
                    path = skia.TextBlob.MakeFromString(ch, font)
                    gp = skia.Path()
                    glyphs = font.textToGlyphs(ch)
                    gpath = font.getPath(glyphs[0])
                    if gpath is not None:
                        m = skia.Matrix()
                        rot = rng.uniform(-5, 5)
                        m.setRotate(rot, adv / 2, -size * 0.35)
                        m.postTranslate(x + rng.uniform(-4, 4), y + rng.uniform(-6, 6))
                        gpath.transform(m)
                        pe = skia.DiscretePathEffect.Make(6, 2.4, rng.randrange(1000))
                        # dark cut shadow (offset)
                        p1 = paint((0.04, 0.03, 0.02), alpha=a)
                        p1.setPathEffect(pe)
                        c.save()
                        c.translate(3, 4)
                        c.drawPath(gpath, p1)
                        c.restore()
                        # raw wood fill
                        p2 = paint(mix(hexc('#8c6e4c'), hexc('#b8976c'), 0.4), alpha=a)
                        p2.setColor4f(skia.Color4f(0.58 * lit, 0.48 * lit, 0.37 * lit, a))
                        p2.setPathEffect(pe)
                        c.drawPath(gpath, p2)
                        # inner shadow on top edge (cut depth)
                        c.save()
                        c.clipPath(gpath, doAntiAlias=True)
                        c.translate(-4, -6)
                        p3 = paint((0.12, 0.08, 0.05), alpha=0.55 * a, stroke=7, blur=2)
                        p3.setPathEffect(pe)
                        c.drawPath(gpath, p3)
                        c.restore()
                        # knife scratches along strokes
                        p4 = paint((0.25, 0.17, 0.10), alpha=0.5 * a, stroke=1.3)
                        p4.setPathEffect(skia.DiscretePathEffect.Make(10, 3, rng.randrange(1000)))
                        c.drawPath(gpath, p4)
            idx += 1
            x += adv * 1.0
        idx += 0
