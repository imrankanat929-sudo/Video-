"""Props and environments built from flat shapes."""
import math
import random
import cairo
from .gfx import (W, H, circle, ellipse, poly, line, rrect, setc, fill_rrect, fill_rect,
                  vgrad, glow, cone, text, font, text_w, col, mix, lerp, FONT_BLACK,
                  FONT_BOLD, FONT_MONO)

# palette: muted dawn with frozen blue tint
SKY = [(0, "#141b2b"), (0.45, "#2a3650"), (0.8, "#56607a"), (1, "#8b8590")]
WARM = "#ffcf8a"
COLD = "#9fd3ff"
ROAD = "#23262e"
WALK = "#3b3f4a"


def sky(ctx, y0=0, h=H, stops=SKY, sun=None):
    vgrad(ctx, -400, y0, W + 800, h, stops)
    if sun:
        glow(ctx, sun[0], sun[1], sun[2], "#f2b38a", 0.35)


def stars(ctx, seed, n, y_max, a=0.6):
    rnd = random.Random(seed)
    for _ in range(n):
        circle(ctx, rnd.uniform(-200, W + 200), rnd.uniform(-200, y_max), rnd.uniform(1, 2.6), "#dfe6ff", a * rnd.uniform(0.3, 1))


def skyline(ctx, seed, base_y, color, win="#ffcf8a", n=9, hmin=300, hmax=800,
            x0=-300, x1=W + 300, lit=0.12, win_a=0.85, roof=True):
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        bw = rnd.uniform(140, 260)
        bh = rnd.uniform(hmin, hmax)
        top = base_y - bh
        fill_rect(ctx, x, top, bw - 8, bh + 4, color)
        if roof and rnd.random() < 0.35:
            fill_rect(ctx, x + bw * 0.6, top - 40, 10, 40, color)
            fill_rect(ctx, x + bw * 0.2, top - 22, bw * 0.25, 22, color)
        # windows
        cols = max(2, int(bw / 46))
        rows = int(bh / 62)
        ww = (bw - 8) / cols
        for r in range(rows):
            for c in range(cols):
                wx = x + c * ww + ww * 0.28
                wy = top + 28 + r * 62
                if rnd.random() < lit:
                    fill_rect(ctx, wx, wy, ww * 0.44, 30, win, win_a * rnd.uniform(0.5, 1))
                else:
                    fill_rect(ctx, wx, wy, ww * 0.44, 30, "#000000", 0.18)
        x += bw


def ground(ctx, y, h=H, road=ROAD, walk=WALK):
    fill_rect(ctx, -400, y, W + 800, 60, walk)
    fill_rect(ctx, -400, y + 60, W + 800, 10, "#55596377")
    fill_rect(ctx, -400, y + 70, W + 800, h, road)


def lane_marks(ctx, y, a=0.8):
    for i in range(-3, 14):
        fill_rect(ctx, i * 160, y, 90, 12, "#d8d2c0", a)


def car(ctx, x, y, w, color="#7a4d4a", facing=1, lights=0.0):
    """Side view car. (x, y) = bottom center on the road."""
    h = w * 0.36
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing, 1)
    ellipse(ctx, 0, 0, w * 0.55, h * 0.12, "#000000", 0.35)
    fill_rrect(ctx, -w / 2, -h * 0.85, w, h * 0.6, h * 0.2, color)
    poly(ctx, [(-w * 0.28, -h * 0.82), (-w * 0.18, -h * 1.25), (w * 0.15, -h * 1.25),
               (w * 0.3, -h * 0.82)], color)
    poly(ctx, [(-w * 0.24, -h * 0.84), (-w * 0.16, -h * 1.17), (-w * 0.02, -h * 1.17),
               (-w * 0.02, -h * 0.84)], "#9fb2c8", 0.75)
    poly(ctx, [(w * 0.02, -h * 0.84), (w * 0.02, -h * 1.17), (w * 0.13, -h * 1.17),
               (w * 0.25, -h * 0.84)], "#9fb2c8", 0.75)
    fill_rect(ctx, -w / 2, -h * 0.5, w, h * 0.06, "#000000", 0.18)
    for wx in (-w * 0.3, w * 0.3):
        circle(ctx, wx, -h * 0.22, h * 0.24, "#141418")
        circle(ctx, wx, -h * 0.22, h * 0.11, "#6c6e75")
    fill_rrect(ctx, w * 0.45, -h * 0.72, w * 0.06, h * 0.12, 3, "#ffe6a8")
    fill_rrect(ctx, -w * 0.51, -h * 0.72, w * 0.04, h * 0.12, 3, "#d33a3a")
    if lights:
        cone(ctx, w * 0.5, -h * 0.66, 0, 0.25, w * 0.9, "#ffe6a8", 0.35 * lights)
    ctx.restore()


def bus(ctx, x, y, w, angle=0.0, color="#3e7a80"):
    h = w * 0.36
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ellipse(ctx, 0, 0, w * 0.55, h * 0.1, "#000000", 0.35)
    fill_rrect(ctx, -w / 2, -h * 1.05, w, h * 0.9, h * 0.12, color)
    fill_rect(ctx, -w / 2, -h * 0.4, w, h * 0.08, "#000000", 0.18)
    n = 7
    for i in range(n):
        wx = -w / 2 + w * 0.06 + i * w * 0.128
        fill_rrect(ctx, wx, -h * 0.94, w * 0.1, h * 0.36, 6, "#a8c0d0", 0.8)
        # frozen passenger silhouettes
        if i % 2 == 0:
            circle(ctx, wx + w * 0.05, -h * 0.72, h * 0.08, "#2b3340", 0.8)
    fill_rrect(ctx, w * 0.43, -h * 0.94, w * 0.05, h * 0.65, 6, "#a8c0d0", 0.6)
    for wx in (-w * 0.32, w * 0.3):
        circle(ctx, wx, -h * 0.15, h * 0.17, "#141418")
        circle(ctx, wx, -h * 0.15, h * 0.08, "#6c6e75")
    fill_rrect(ctx, -w * 0.3, -h * 1.15, w * 0.3, h * 0.1, 6, "#1b1d22")
    font(ctx, h * 0.09, FONT_MONO)
    ctx.move_to(-w * 0.28, -h * 1.075)
    setc(ctx, "#ffb347")
    ctx.show_text("14")
    ctx.restore()


PEOPLE_COLORS = ["#5a4a6a", "#4a6070", "#6a5547", "#3f5a4a", "#6b4650", "#57606e", "#7a6a4a"]


def person(ctx, x, y, h, coat="#57606e", hair="#2a211c", phone=0.0, facing=1,
           pose=0, keys=False, t=0.0, bag=False, skirt=False):
    """Faceless frozen pedestrian, feet at (x, y). phone: screen glow 0..1."""
    R = h * 0.105
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing, 1)
    ellipse(ctx, 0, 0, h * 0.16, h * 0.025, "#000000", 0.3)
    # legs (mid-step pose: frozen while walking)
    stride = (0.18 if pose == 1 else 0.05)
    for s in (-1, 1):
        ctx.save()
        ctx.translate(0, -h * 0.45)
        ctx.rotate(s * stride)
        fill_rrect(ctx, -h * 0.04, 0, h * 0.08, h * 0.45, h * 0.03, "#22252c")
        fill_rrect(ctx, -h * 0.045, h * 0.42, h * 0.1, h * 0.04, h * 0.015, "#15161a")
        ctx.restore()
    # coat
    if skirt:
        poly(ctx, [(-h * 0.13, -h * 0.78), (h * 0.13, -h * 0.78), (h * 0.19, -h * 0.36), (-h * 0.19, -h * 0.36)], coat)
    else:
        fill_rrect(ctx, -h * 0.14, -h * 0.79, h * 0.28, h * 0.42, h * 0.07, coat)
    fill_rect(ctx, -h * 0.005, -h * 0.75, h * 0.01, h * 0.36, "#000000", 0.15)
    # back arm
    ctx.save()
    ctx.translate(-h * 0.1, -h * 0.74)
    ctx.rotate(0.15)
    fill_rrect(ctx, -h * 0.035, 0, h * 0.07, h * 0.33, h * 0.035, mix(coat, "#000000", 0.25))
    ctx.restore()
    # front arm: holds phone up or hangs
    ctx.save()
    ctx.translate(h * 0.1, -h * 0.74)
    if phone or keys:
        ctx.rotate(-1.0)
    else:
        ctx.rotate(-0.12)
    fill_rrect(ctx, -h * 0.035, 0, h * 0.07, h * 0.3, h * 0.035, coat)
    circle(ctx, 0, h * 0.31, h * 0.035, "#c49a76")
    ctx.restore()
    hx, hy = h * 0.1 + math.sin(1.0) * h * 0.31, -h * 0.74 + math.cos(1.0) * h * 0.31
    if phone:
        fill_rrect(ctx, hx - h * 0.02, hy - h * 0.09, h * 0.05, h * 0.09, 3, "#0d0f14")
        fill_rrect(ctx, hx - h * 0.012, hy - h * 0.083, h * 0.034, h * 0.076, 2, mix("#1b2433", "#d9f1ff", phone))
        glow(ctx, hx, hy - h * 0.05, h * 0.35 * (0.4 + phone), "#bfe6ff", 0.55 * phone)
    if bag:
        fill_rrect(ctx, -h * 0.2, -h * 0.5, h * 0.12, h * 0.14, 4, "#2a2622")
    # neck + head (faceless, hair cap)
    fill_rect(ctx, -h * 0.025, -h * 0.83, h * 0.05, h * 0.05, "#b48a68")
    circle(ctx, 0, -h * 0.9, R, "#c49a76")
    ctx.save()
    ctx.arc(0, -h * 0.9, R * 1.02, 0, 2 * math.pi)
    ctx.clip()
    fill_rect(ctx, -R * 1.2, -h * 0.9 - R * 1.2, R * 1.5, R * 1.25, hair)
    ellipse(ctx, -R * 0.4, -h * 0.9 + R * 0.2, R * 0.6, R * 0.9, hair)
    ctx.restore()
    if phone:
        glow(ctx, R * 0.6, -h * 0.9, R * 1.6, "#bfe6ff", 0.35 * phone)
    ctx.restore()


def keys(ctx, x, y, s, t=0.0):
    """Key ring frozen in midair."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(0.5)
    ctx.arc(0, 0, s * 0.35, 0, 2 * math.pi)
    ctx.set_line_width(s * 0.08)
    setc(ctx, "#d9c27a")
    ctx.stroke()
    for ang, c in ((0.6, "#d9c27a"), (1.5, "#b8c0c8")):
        ctx.save()
        ctx.rotate(ang)
        fill_rrect(ctx, s * 0.3, -s * 0.08, s * 0.7, s * 0.16, s * 0.05, c)
        circle(ctx, s * 0.32, 0, s * 0.18, c)
        fill_rect(ctx, s * 0.8, 0, s * 0.08, s * 0.14, c)
        ctx.restore()
    ctx.restore()


def bird(ctx, x, y, s, color="#14161c"):
    ctx.save()
    ctx.translate(x, y)
    ellipse(ctx, 0, 0, s * 0.5, s * 0.17, color)
    circle(ctx, s * 0.45, -s * 0.06, s * 0.13, color)
    poly(ctx, [(s * 0.55, -s * 0.06), (s * 0.72, -s * 0.02), (s * 0.55, 0.0)], "#c79a3a")
    poly(ctx, [(-s * 0.1, -s * 0.05), (-s * 0.55, -s * 0.75), (-s * 0.1, -s * 0.55), (s * 0.18, -s * 0.05)], color)
    poly(ctx, [(-s * 0.05, 0.02), (s * 0.25, s * 0.55), (s * 0.2, 0.02)], mix(color, "#000000", 0.3))
    poly(ctx, [(-s * 0.45, 0), (-s * 0.85, -s * 0.12), (-s * 0.8, s * 0.12)], color)
    ctx.restore()


def fountain(ctx, x, y, s, t=0.0):
    """Fountain with water frozen in midair. (x, y) = basin center."""
    rnd = random.Random(11)
    ctx.save()
    ctx.translate(x, y)
    ellipse(ctx, 0, s * 0.18, s * 1.05, s * 0.2, "#000000", 0.3)
    fill_rect(ctx, -s, -s * 0.05, s * 2, s * 0.2, "#6d717c")
    ellipse(ctx, 0, s * 0.15, s, s * 0.17, "#5d616b")
    ellipse(ctx, 0, -s * 0.05, s, s * 0.17, "#8a8e98")
    ellipse(ctx, 0, -s * 0.05, s * 0.9, s * 0.13, "#3f6f86")
    ellipse(ctx, 0, -s * 0.05, s * 0.9, s * 0.13, "#9fd3ff", 0.15)
    fill_rrect(ctx, -s * 0.08, -s * 0.6, s * 0.16, s * 0.6, 6, "#7b7f89")
    ellipse(ctx, 0, -s * 0.6, s * 0.35, s * 0.07, "#8a8e98")
    # frozen arcs of droplets
    for arc_i in range(9):
        ang = -math.pi / 2 + (arc_i - 4) * 0.28
        v = s * 1.3
        for k in range(16):
            u = k / 15
            px = math.cos(ang) * v * u * 1.2
            py = -s * 0.65 + math.sin(ang) * v * u + s * 1.2 * u * u
            if py > -s * 0.08:
                break
            r = s * rnd.uniform(0.012, 0.03)
            circle(ctx, px, py, r, "#cfeaff", 0.85)
            circle(ctx, px - r * 0.3, py - r * 0.3, r * 0.35, "#ffffff", 0.9)
    # frozen splash crowns
    for k in range(30):
        px = rnd.uniform(-s * 0.8, s * 0.8)
        py = -s * 0.07 - rnd.uniform(0, s * 0.12)
        circle(ctx, px, py, s * rnd.uniform(0.01, 0.022), "#e6f6ff", 0.8)
    glow(ctx, 0, -s * 0.5, s * 1.1, "#9fd3ff", 0.18 + 0.04 * math.sin(t * 2))
    ctx.restore()


def clock_face(ctx, x, y, r, hh, mm, ss=None, face="#efe9dc", rim="#2b2d33", light=0.0,
               numbers=False):
    ctx.save()
    ctx.translate(x, y)
    if light:
        glow(ctx, 0, 0, r * 2.4, "#ffe2a8", 0.45 * light)
    circle(ctx, 3, 6, r * 1.08, "#000000", 0.35)
    circle(ctx, 0, 0, r * 1.08, rim)
    circle(ctx, 0, 0, r, mix(face, "#fff4d8", light))
    for i in range(60):
        a = i / 60 * 2 * math.pi
        big = i % 5 == 0
        r1 = r * (0.8 if big else 0.88)
        line(ctx, math.sin(a) * r1, -math.cos(a) * r1, math.sin(a) * r * 0.94, -math.cos(a) * r * 0.94,
             r * (0.045 if big else 0.015), "#26272c")
    ha = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    ma = (mm + (ss or 0) / 60) / 60 * 2 * math.pi
    line(ctx, 0, 0, math.sin(ha) * r * 0.5, -math.cos(ha) * r * 0.5, r * 0.08, "#1b1c20")
    line(ctx, 0, 0, math.sin(ma) * r * 0.75, -math.cos(ma) * r * 0.75, r * 0.055, "#1b1c20")
    if ss is not None:
        sa = ss / 60 * 2 * math.pi
        line(ctx, -math.sin(sa) * r * 0.15, math.cos(sa) * r * 0.15,
             math.sin(sa) * r * 0.85, -math.cos(sa) * r * 0.85, r * 0.022, "#c8161d")
    circle(ctx, 0, 0, r * 0.06, "#c8161d")
    ctx.restore()


def tower(ctx, x, base_y, w, hgt, clock_t, light=0.0, color="#2c3346"):
    """Clock tower. clock_t = (h, m, s)."""
    ctx.save()
    top = base_y - hgt
    fill_rect(ctx, x - w / 2, top, w, hgt, color)
    fill_rect(ctx, x - w / 2, top, w * 0.12, hgt, "#ffffff", 0.04)
    fill_rect(ctx, x + w * 0.38, top, w * 0.12, hgt, "#000000", 0.18)
    poly(ctx, [(x - w * 0.62, top), (x, top - w * 0.95), (x + w * 0.62, top)], mix(color, "#000000", 0.25))
    fill_rect(ctx, x - w * 0.6, top, w * 1.2, w * 0.1, mix(color, "#ffffff", 0.08))
    line(ctx, x, top - w * 0.95, x, top - w * 1.25, 6, "#1d2230")
    # narrow windows
    for i in range(5):
        fill_rrect(ctx, x - w * 0.08, top + w * 1.35 + i * w * 0.55, w * 0.16, w * 0.3, w * 0.08, "#000000", 0.35)
    clock_face(ctx, x, top + w * 0.55, w * 0.36, *clock_t, light=light)
    ctx.restore()


def apartment(ctx, x, base_y, w, hgt, seed=5, hero_window=None, door_open=0.0,
              door_light=0.0, lit=0.15, color="#4a4f5e"):
    """Apartment block with entrance. hero_window=(row, col, glow)"""
    rnd = random.Random(seed)
    left = x - w / 2
    top = base_y - hgt
    fill_rect(ctx, left, top, w, hgt, color)
    fill_rect(ctx, left, top, w, 18, mix(color, "#000000", 0.3))
    for i in range(1, 8):
        fill_rect(ctx, left, top + i * hgt / 8, w, 4, "#000000", 0.1)
    cols, rows = 5, int((hgt - 330) / 150)
    cw = w / cols
    for r in range(rows):
        for c in range(cols):
            wx = left + c * cw + cw * 0.2
            wy = top + 60 + r * 150
            on = rnd.random() < lit
            hw = hero_window and hero_window[0] == r and hero_window[1] == c
            fill_rect(ctx, wx - 6, wy - 6, cw * 0.6 + 12, 100, "#2a2d36")
            if hw:
                g = hero_window[2]
                fill_rect(ctx, wx, wy, cw * 0.6, 88, mix("#4a5468", WARM, g))
                glow(ctx, wx + cw * 0.3, wy + 44, cw * 1.2, WARM, 0.5 * g)
            else:
                fill_rect(ctx, wx, wy, cw * 0.6, 88, WARM if on else "#59657a", 0.85 if on else 0.9)
                if not on:
                    poly(ctx, [(wx, wy), (wx + cw * 0.25, wy), (wx, wy + 40)], "#ffffff", 0.08)
            fill_rect(ctx, wx + cw * 0.3 - 2, wy, 4, 88, "#2a2d36")
    # entrance
    dw, dh = 170, 270
    dx, dy = x - dw / 2, base_y - dh
    fill_rect(ctx, dx - 40, dy - 70, dw + 80, 26, "#2c2f38")
    poly(ctx, [(dx - 50, dy - 44), (dx + dw + 50, dy - 44), (dx + dw + 30, dy - 70), (dx - 30, dy - 70)], "#353945")
    fill_rect(ctx, dx - 14, dy - 14, dw + 28, dh + 14, "#2a2c33")
    # dark inside
    fill_rect(ctx, dx, dy, dw, dh, "#050608")
    if door_light:
        glow(ctx, x, dy + dh * 0.45, dw * 0.9, "#7fa8d6", 0.3 * door_light)
        fill_rect(ctx, x - 3, dy + 40, 6, 30, "#bcd8ff", 0.5 * door_light)  # faint lamp deep inside
    # door panel swinging inward (hinge on the left)
    if door_open < 1:
        pw = dw * (1 - door_open * 0.86)
        skew = door_open * 18
        poly(ctx, [(dx, dy), (dx + pw, dy + skew), (dx + pw, dy + dh - skew), (dx, dy + dh)], "#5a3f35")
        poly(ctx, [(dx + pw * 0.12, dy + 20 + skew * 0.3), (dx + pw * 0.88, dy + 20 + skew * 0.9),
                   (dx + pw * 0.88, dy + dh * 0.45), (dx + pw * 0.12, dy + dh * 0.45)], "#000000", 0.18)
        circle(ctx, dx + pw * 0.85, dy + dh * 0.55, 7, "#c9b27a")
    # lamp above the door
    circle(ctx, x, dy - 90, 10, "#ffe2a8")
    glow(ctx, x, dy - 90, 160, WARM, 0.35)
    # number plate
    fill_rrect(ctx, dx + dw + 30, dy + 10, 60, 44, 6, "#2f5d8a")
    text(ctx, "14", dx + dw + 60, dy + 44, 30, "#ffffff", FONT_BOLD, shadow=False)
    # steps
    fill_rect(ctx, dx - 40, base_y, dw + 80, 16, "#5d616b")
    fill_rect(ctx, dx - 60, base_y + 16, dw + 120, 16, "#4d515b")


def streetlamp(ctx, x, base_y, h, on=0.0):
    line(ctx, x, base_y, x, base_y - h, 10, "#1c1f26")
    line(ctx, x, base_y - h, x + 60, base_y - h - 10, 8, "#1c1f26")
    fill_rrect(ctx, x + 40, base_y - h - 14, 50, 14, 5, "#2a2e38")
    if on:
        cone(ctx, x + 65, base_y - h, math.pi / 2, 0.45, h * 0.9, WARM, 0.25 * on)
        glow(ctx, x + 65, base_y - h - 4, 60, WARM, 0.6 * on)


def tree(ctx, x, base_y, s, color="#2b3a3a"):
    fill_rect(ctx, x - s * 0.06, base_y - s * 0.6, s * 0.12, s * 0.6, "#2a221e")
    circle(ctx, x, base_y - s * 0.85, s * 0.42, color)
    circle(ctx, x - s * 0.28, base_y - s * 0.68, s * 0.3, color)
    circle(ctx, x + s * 0.3, base_y - s * 0.7, s * 0.3, mix(color, "#000000", 0.15))


def dust(ctx, seed, n, a=0.5, area=(-100, -100, W + 200, H + 200), color="#dfe9ff"):
    """Frozen floating specks - they never move (time stopped)."""
    rnd = random.Random(seed)
    x0, y0, w, h = area
    for _ in range(n):
        circle(ctx, x0 + rnd.random() * w, y0 + rnd.random() * h, rnd.uniform(1.2, 3.5), color, a * rnd.uniform(0.2, 1))


# ---------- phone ----------
def phone_body(ctx, x, y, w, glow_a=0.6, glow_c="#9fd3ff"):
    """Returns screen rect (sx, sy, sw, sh). (x, y) is the phone center."""
    h = w * 2.05
    if glow_a:
        glow(ctx, x, y, w * 1.6, glow_c, glow_a * 0.5)
    fill_rrect(ctx, x - w / 2 + 10, y - h / 2 + 18, w, h, w * 0.14, "#000000", 0.4)
    fill_rrect(ctx, x - w / 2, y - h / 2, w, h, w * 0.14, "#0b0c10")
    fill_rrect(ctx, x - w / 2 + 3, y - h / 2 + 3, w - 6, h - 6, w * 0.13, "#2a2c33")
    b = w * 0.045
    sx, sy, sw, sh = x - w / 2 + b, y - h / 2 + b, w - 2 * b, h - 2 * b
    return sx, sy, sw, sh


def hand_holding(ctx, x, y, w, side=1, part="back"):
    """Hand + sweater cuff holding a phone of width w centered at (x, y).
    Draw part="back" before the phone and part="front" after it."""
    h = w * 2.05
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(side, 1)
    if part == "back":
        poly(ctx, [(-w * 0.1, h * 0.42), (w * 0.62, h * 0.36), (w * 1.0, h * 1.5), (-w * 0.5, h * 1.5)], "#24242b")
        fill_rrect(ctx, -w * 0.14, h * 0.36, w * 0.8, h * 0.13, w * 0.06, "#2f2f38")
        ellipse(ctx, w * 0.22, h * 0.36, w * 0.5, h * 0.17, "#c99d75")
    else:
        # thumb on the left edge
        ctx.save()
        ctx.translate(-w * 0.52, h * 0.36)
        ctx.rotate(0.75)
        fill_rrect(ctx, -w * 0.08, -w * 0.42, w * 0.17, w * 0.5, w * 0.085, "#d3a57c")
        fill_rrect(ctx, -w * 0.06, -w * 0.4, w * 0.12, w * 0.12, w * 0.05, "#e2b994")
        ctx.restore()
        # fingers wrapping the right edge
        for i in range(4):
            fill_rrect(ctx, w * 0.42, h * 0.02 + i * w * 0.17, w * 0.17, w * 0.14, w * 0.07, "#d3a57c")
            fill_rect(ctx, w * 0.42, h * 0.02 + i * w * 0.17 + w * 0.12, w * 0.12, w * 0.02, "#b98a63")
    ctx.restore()
