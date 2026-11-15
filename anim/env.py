"""Environments (hallway, bedroom, kitchen, street, phone UI, void)."""
import math
import random
import skia
from .core import *
from .character import Character, HERO, MOM, DAD, pose

FLOOR = 1500  # world y of the floor line for side-view sets

hero_c = Character(HERO)
mom_c = Character(MOM)
dad_c = Character(DAD)


def ground_shadow(c, x, y, w, a=0.35):
    c.drawOval(skia.Rect.MakeLTRB(x - w, y - w * 0.12, x + w, y + w * 0.12), paint("#000000", a, blur=w * 0.12))


# ====================================================================== frames / pictures
def picture(c, x, y, w, h, kind, alt=False, t=0.0, frame="#5b3d2a"):
    """framed picture with small scene; alt=True -> the parallel-world version"""
    c.save()
    c.drawRect(skia.Rect.MakeXYWH(x - 8, y - 8, w + 16, h + 16), paint("#000000", 0.25, blur=8))
    c.drawRect(skia.Rect.MakeXYWH(x - 10, y - 10, w + 20, h + 20), paint(frame))
    c.drawRect(skia.Rect.MakeXYWH(x - 10, y - 10, w + 20, h + 20), paint(shade(frame, 0.2), stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint("#e9e2d2"))
    c.clipRect(skia.Rect.MakeXYWH(x + 6, y + 6, w - 12, h - 12))
    ix, iy, iw, ih = x + 6, y + 6, w - 12, h - 12
    if kind == "family":
        c.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), gpaint(lin_grad(0, iy, 0, iy + ih, ["#8fc3e6", "#d9eef7"])))
        c.drawRect(skia.Rect.MakeXYWH(ix, iy + ih * 0.72, iw, ih), paint("#7bb36a"))
        sc = ih / 1150
        base = iy + ih * 0.98
        if not alt:
            dad_c.draw(c, ix + iw * 0.22, base, sc, pose(tr=0.1, expr="calm", t=1))
            hero_c.draw(c, ix + iw * 0.5, base, sc * 0.92, pose(tr=0.0, expr="neutral", mouth=0.0, t=1))
            mom_c.draw(c, ix + iw * 0.78, base, sc, pose(tr=-0.1, t=1))
        else:
            # same photo, but the boy is gone and the parents stand apart, smiling at nobody
            dad_c.draw(c, ix + iw * 0.25, base, sc, pose(tr=0.25, expr="calm", t=1))
            mom_c.draw(c, ix + iw * 0.75, base, sc, pose(tr=-0.25, t=1))
            c.drawOval(skia.Rect.MakeXYWH(ix + iw * 0.43, base - ih * 0.12, iw * 0.14, ih * 0.04), paint("#000000", 0.15))
    elif kind == "sea":
        c.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), gpaint(lin_grad(0, iy, 0, iy + ih, ["#f6c28b", "#f39a7a"])))
        c.drawCircle(ix + iw * 0.5, iy + ih * 0.55, ih * 0.18, paint("#fff1c7"))
        c.drawRect(skia.Rect.MakeXYWH(ix, iy + ih * 0.6, iw, ih), paint("#3f7fa8"))
    elif kind == "sea_alt":
        c.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), gpaint(lin_grad(0, iy, 0, iy + ih, ["#25304c", "#5d6c8f"])))
        c.drawCircle(ix + iw * 0.3, iy + ih * 0.35, ih * 0.13, paint("#dfe9ff"))
        c.drawCircle(ix + iw * 0.7, iy + ih * 0.3, ih * 0.09, paint("#dfe9ff"))
        c.drawRect(skia.Rect.MakeXYWH(ix, iy + ih * 0.6, iw, ih), paint("#1d2a3f"))
    elif kind == "dog":
        c.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), paint("#f1d8a8"))
        c.drawOval(skia.Rect.MakeXYWH(ix + iw * 0.25, iy + ih * 0.35, iw * 0.5, ih * 0.45), paint("#b07a46"))
        c.drawCircle(ix + iw * 0.5, iy + ih * 0.35, iw * 0.18, paint("#b07a46"))
        c.drawCircle(ix + iw * 0.44, iy + ih * 0.33, iw * 0.03, paint("#111"))
        c.drawCircle(ix + iw * 0.56, iy + ih * 0.33, iw * 0.03, paint("#111"))
    elif kind == "cat":
        c.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), paint("#b8c4d6"))
        c.drawOval(skia.Rect.MakeXYWH(ix + iw * 0.28, iy + ih * 0.4, iw * 0.44, ih * 0.45), paint("#2b2b33"))
        c.drawCircle(ix + iw * 0.5, iy + ih * 0.38, iw * 0.16, paint("#2b2b33"))
        c.drawPath(path_poly([(ix + iw * 0.37, iy + ih * 0.3), (ix + iw * 0.4, iy + ih * 0.12), (ix + iw * 0.47, iy + ih * 0.26)]), paint("#2b2b33"))
        c.drawPath(path_poly([(ix + iw * 0.63, iy + ih * 0.3), (ix + iw * 0.6, iy + ih * 0.12), (ix + iw * 0.53, iy + ih * 0.26)]), paint("#2b2b33"))
        c.drawCircle(ix + iw * 0.45, iy + ih * 0.37, iw * 0.03, paint("#9ff0ff"))
        c.drawCircle(ix + iw * 0.55, iy + ih * 0.37, iw * 0.03, paint("#9ff0ff"))
    elif kind == "double":
        # a portrait of the boy... smiling the way he never smiles
        c.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), gpaint(lin_grad(0, iy, 0, iy + ih, ["#3a4e70", "#1b2338"])))
        hero_c.draw(c, ix + iw * 0.5, iy + ih * 2.25, ih / 520, pose(expr="smug", t=1, eye_glint=0.6))
    c.restore()


# ====================================================================== hallway
def wall_paper(c, x0, x1, y0, y1, base, stripe, t=0):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(base))
    p = paint(stripe, 0.35)
    x = x0 - (x0 % 60)
    while x < x1:
        c.drawRect(skia.Rect.MakeLTRB(x, y0, x + 22, y1), p)
        x += 60


def floor_planks(c, x0, x1, y0, y1, base, line):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(base))
    rows = 6
    for r in range(rows):
        yy = y0 + (y1 - y0) * (r / rows) ** 1.3
        c.drawLine(x0, yy, x1, yy, paint(line, 0.6, stroke=2 + r))
        off = (r * 137) % 240
        x = x0 - (x0 % 240) + off
        yb = y0 + (y1 - y0) * ((r + 1) / rows) ** 1.3
        while x < x1:
            c.drawLine(x, yy, x + (x - 540) * 0.04, yb, paint(line, 0.5, stroke=3))
            x += 240
    g = lin_grad(0, y0, 0, y0 + 80, [(0, 0, 0, 90), (0, 0, 0, 0)])
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 80), gpaint(g))


def door(c, x, y_floor, w=300, h=720, colr="#7a5236", open_k=0.0, strange=False, t=0.0,
         light=0.0, inside=None):
    """door centred at x; open_k 0..1 swings it (hinge on the left)."""
    x0 = x - w / 2
    y0 = y_floor - h
    # frame
    c.drawRect(skia.Rect.MakeLTRB(x0 - 26, y0 - 26, x0 + w + 26, y_floor), paint(shade(colr, -0.35)))
    c.drawRect(skia.Rect.MakeLTRB(x0 - 18, y0 - 18, x0 + w + 18, y_floor), paint(shade(colr, 0.12)))
    # opening
    if open_k > 0 or inside:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y_floor))
        if inside:
            inside(c, x0, y0, w, h)
        else:
            c.drawRect(skia.Rect.MakeLTRB(x0, y0, x0 + w, y_floor), paint("#0b1430"))
        c.restore()
    # leaf
    k = clamp(open_k)
    lw = w * (1 - k * 0.86)
    leaf = skia.Rect.MakeLTRB(x0, y0, x0 + lw, y_floor)
    base = colr if not strange else "#3b3f52"
    c.drawRect(leaf, paint(shade(base, -0.25 * k)))
    # panels
    pc = paint(shade(base, -0.18 - 0.2 * k))
    for (py, ph) in ((0.08, 0.38), (0.53, 0.40)):
        c.drawRRect(rrect(x0 + lw * 0.14, y0 + h * py, lw * 0.72, h * ph, 6), pc)
        c.drawRRect(rrect(x0 + lw * 0.14, y0 + h * py, lw * 0.72, h * ph, 6), paint(shade(base, 0.15), 0.5, stroke=3))
    if strange:
        # engraved rings, faint glowing seams
        cx, cy = x0 + lw / 2, y0 + h * 0.3
        for i in range(3):
            c.drawCircle(cx, cy, lw * (0.12 + i * 0.07), paint("#7fe3ff", 0.10 + 0.25 * light * (0.5 + 0.5 * math.sin(t * 3 + i)), stroke=3))
    # handle
    hx = x0 + lw - 34 * (1 - k)
    if k < 0.9:
        c.drawRRect(rrect(hx - 10, y_floor - h * 0.48 - 8, 30, 14, 7), paint("#d8c8a0" if not strange else "#9aa6c0"))
        c.drawCircle(hx, y_floor - h * 0.48, 12, paint("#c2a86f" if not strange else "#7f8aa5"))
        if strange:
            c.drawRect(skia.Rect.MakeXYWH(hx - 4, y_floor - h * 0.48 + 22, 8, 18), paint("#000000"))
            glow(c, hx, y_floor - h * 0.48 + 30, 26, "#6fe0ff", 0.6 * light)
    # shade the leaf edge
    c.drawRect(skia.Rect.MakeLTRB(x0 + lw - 8, y0, x0 + lw, y_floor), paint("#000000", 0.25))
    # light from under the door
    if light > 0 and k < 0.05:
        flick = 0.85 + 0.15 * math.sin(t * 11) * math.sin(t * 3.3)
        c.drawRect(skia.Rect.MakeLTRB(x0 + 4, y_floor - 7, x0 + w - 4, y_floor), paint("#bff3ff", light * flick))
        c.save()
        c.drawOval(skia.Rect.MakeLTRB(x0 - 120, y_floor - 30, x0 + w + 120, y_floor + 140),
                   gpaint(rad_grad(x, y_floor, w * 0.9, [(80, 200, 255, int(190 * light * flick)), (40, 120, 255, 0)])))
        c.restore()
        for i in range(12):
            ph = (t * 0.35 + hash1(i * 3.1)) % 1.0
            px = x0 + w * hash1(i * 7.7) + math.sin(t + i) * 10
            py = y_floor - 6 - ph * 220
            glow(c, px, py, 9 * (1 - ph) + 3, "#9fe8ff", light * (1 - ph) * 0.9)


def ceiling_lamp(c, x, y, colr="#ffd59a", a=1.0, r=500):
    c.drawLine(x, y - 200, x, y - 40, paint("#2a2420", stroke=4))
    c.drawPath(path_poly([(x - 60, y), (x + 60, y), (x + 36, y - 46), (x - 36, y - 46)]), paint("#e8dcc0"))
    glow(c, x, y + 20, r, colr, 0.55 * a)
    glow(c, x, y, 70, "#fff6e0", 0.9 * a)


def hallway(c, t, alt=False, strange=True, door_open=0.0, door_light=0.0, inside=None, x_view=(-400, 3600)):
    x0, x1 = x_view
    if not alt:
        wall_paper(c, x0, x1, -400, FLOOR, "#b88a5e", "#a67a50")
        wains = "#6e4b33"
        floor_c, floor_l = "#5a3c28", "#3c2719"
    else:
        wall_paper(c, x0, x1, -400, FLOOR, "#5f6f86", "#53637a")
        wains = "#3c4659"
        floor_c, floor_l = "#33384a", "#232735"
    # wainscot
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR - 380, x1, FLOOR), paint(wains))
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR - 392, x1, FLOOR - 374), paint(shade(wains, 0.2)))
    xx = x0 - (x0 % 260)
    while xx < x1:
        c.drawRRect(rrect(xx + 30, FLOOR - 340, 200, 290, 6), paint(shade(wains, -0.15), stroke=4))
        xx += 260
    # baseboard + floor
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR - 40, x1, FLOOR), paint(shade(wains, -0.3)))
    floor_planks(c, x0, x1, FLOOR, FLOOR + 900, floor_c, floor_l)
    # ceiling cornice
    c.drawRect(skia.Rect.MakeLTRB(x0, -400, x1, 190), paint(shade("#b88a5e" if not alt else "#5f6f86", -0.08)))
    c.drawRect(skia.Rect.MakeLTRB(x0, 180, x1, 205), paint(shade(wains, 0.3)))
    # front door of the flat (left)
    door(c, 0, FLOOR, 320, 760, "#4d3527" if not alt else "#2f3548")
    # coat rack
    c.drawRect(skia.Rect.MakeXYWH(330, 660, 220, 18), paint("#3a281c"))
    for i, cc in enumerate(["#3d5a80", "#8a3b3b"] if not alt else ["#5b2b2b", "#2f3e57"]):
        hx = 370 + i * 110 + (40 if alt else 0)
        c.drawPath(smooth_path([(hx, 680), (hx + 45, 700), (hx + 50, 960), (hx - 45, 970), (hx - 40, 700)]), paint(cc))
    # pictures
    picture(c, 700, 560, 300, 230, "family", alt=alt, t=t)
    picture(c, 1100, 600, 170, 200, "dog" if not alt else "cat", t=t)
    # normal bedroom door (his real room)
    door(c, 1600, FLOOR, 300, 740, "#7a5236" if not alt else "#465068")
    # shelf with vase
    c.drawRect(skia.Rect.MakeXYWH(1900, 900, 260, 16), paint("#3b291e" if not alt else "#2a3040"))
    vx = 1960 if not alt else 2110
    c.drawPath(smooth_path([(vx - 30, 900), (vx + 30, 900), (vx + 38, 850), (vx + 18, 800), (vx - 18, 800), (vx - 38, 850)]),
               paint("#3f7d8c" if not alt else "#8c3f6a"))
    # wall clock
    clock(c, 2050, 560, 70, t, alt)
    # the strange door
    if strange:
        door(c, 2600, FLOOR, 300, 740, "#7a5236", open_k=door_open, strange=True, t=t, light=door_light,
             inside=inside)
    # lamps
    lamp_c = "#ffcf8a" if not alt else "#9cc7ff"
    for lx in (500, 1500, 2600):
        ceiling_lamp(c, lx, 260, lamp_c, 0.85 if not alt else 0.6)


def clock(c, x, y, r, t, alt=False, rate=1.0):
    c.drawCircle(x, y, r + 10, paint("#2c241e" if not alt else "#22283a"))
    c.drawCircle(x, y, r, paint("#f3ecdc" if not alt else "#cdd6e6"))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.drawLine(x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82,
                   x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92, paint("#333", stroke=4))
    sgn = -1 if alt else 1  # clock runs backwards in the other world
    sa = sgn * (math.floor(t * rate) / 60) * 2 * math.pi
    ma = (47 / 60) * 2 * math.pi * sgn
    ha = (7 / 12 + 47 / 720) * 2 * math.pi * sgn
    c.drawLine(x, y, x + math.sin(ha) * r * 0.5, y - math.cos(ha) * r * 0.5, paint("#222", stroke=7))
    c.drawLine(x, y, x + math.sin(ma) * r * 0.75, y - math.cos(ma) * r * 0.75, paint("#222", stroke=5))
    c.drawLine(x, y, x + math.sin(sa) * r * 0.85, y - math.cos(sa) * r * 0.85, paint("#c0392b", stroke=2))
    c.drawCircle(x, y, 6, paint("#222"))


# ====================================================================== bedroom
def bedroom(c, t, alt=False, door_x=None, door_state=1.0, wall_glow=0.0, phone_glow=0.0, x_view=(-300, 1500),
            entering_light=0.0, glow_x=-150):
    """side-on bedroom, x in [0, 1300]; door at door_x (None -> no door)"""
    x0, x1 = x_view
    wall = "#7f90b0" if alt else "#b7a78c"
    wall2 = "#72839f" if alt else "#aa9a80"
    wall_paper(c, x0, x1, -500, FLOOR, wall, wall2)
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR - 40, x1, FLOOR), paint("#2b2f3d"))
    floor_planks(c, x0, x1, FLOOR, FLOOR + 900, "#4b3a33" if not alt else "#3b3a44", "#2d221d")
    # rug
    c.drawOval(skia.Rect.MakeLTRB(200, FLOOR + 40, 1000, FLOOR + 200), paint("#8c4b4b" if not alt else "#4b5f8c", 0.9))
    c.drawOval(skia.Rect.MakeLTRB(240, FLOOR + 60, 960, FLOOR + 180), paint("#ffffff", 0.12, stroke=6))
    # window with night city
    wx, wy, ww, wh = 760 if not alt else 300, 420, 360, 440
    c.drawRect(skia.Rect.MakeXYWH(wx - 20, wy - 20, ww + 40, wh + 40), paint("#ddd6c8"))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), gpaint(lin_grad(0, wy, 0, wy + wh, ["#0d1430", "#253a6b"] if not alt else ["#0a1a2a", "#1d5a6e"])))
    if alt:
        c.drawCircle(wx + ww * 0.3, wy + 100, 40, paint("#e9f6ff"))
        c.drawCircle(wx + ww * 0.62, wy + 80, 24, paint("#e9f6ff"))
        glow(c, wx + ww * 0.3, wy + 100, 140, "#9fe0ff", 0.4)
    else:
        c.drawCircle(wx + ww * 0.7, wy + 90, 34, paint("#fff4d6"))
        glow(c, wx + ww * 0.7, wy + 90, 120, "#ffe9b0", 0.35)
    rnd = random.Random(5 if not alt else 9)
    for i in range(9):
        bx = wx + i * 44 + rnd.uniform(-10, 10)
        bh = rnd.uniform(90, 260) * (1.4 if alt and i % 3 == 0 else 1)
        c.drawRect(skia.Rect.MakeXYWH(bx, wy + wh - bh, 40, bh), paint("#0a0f20"))
        for j in range(int(bh // 30)):
            if rnd.random() < 0.45:
                c.drawRect(skia.Rect.MakeXYWH(bx + 8 + (j % 2) * 16, wy + wh - bh + 10 + j * 28, 9, 12),
                           paint("#ffd27a" if not alt else "#7fe8ff", 0.8))
    c.restore()
    c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, paint("#ddd6c8", stroke=14))
    c.drawLine(wx, wy + wh * 0.45, wx + ww, wy + wh * 0.45, paint("#ddd6c8", stroke=14))
    c.drawRect(skia.Rect.MakeXYWH(wx - 40, wy + wh + 20, ww + 80, 24), paint("#cfc6b6"))
    # poster
    px = 1180 if not alt else 1180
    c.drawRect(skia.Rect.MakeXYWH(px - 120, 480, 240, 330), paint("#1c1c24"))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(px - 110, 490, 220, 310))
    if not alt:
        c.drawRect(skia.Rect.MakeXYWH(px - 110, 490, 220, 310), gpaint(lin_grad(0, 490, 0, 800, ["#ff7b54", "#5b2a86"])))
        c.drawCircle(px, 610, 60, paint("#ffd36b"))
        text_center(c, "SPACE", px, 760, 40, "#ffffff", "Black")
    else:
        c.drawRect(skia.Rect.MakeXYWH(px - 110, 490, 220, 310), gpaint(lin_grad(0, 490, 0, 800, ["#3fd0c9", "#16325c"])))
        c.drawCircle(px - 30, 600, 40, paint("#e9f6ff"))
        c.drawCircle(px + 40, 650, 26, paint("#e9f6ff"))
        c.save(); c.scale(-1, 1); text_center(c, "SPACE", -px, 760, 40, "#ffffff", "Black"); c.restore()
    c.restore()
    # bed
    bx = 120 if not alt else 760
    c.drawRRect(rrect(bx - 20, FLOOR - 330, 40, 330, 8), paint("#4a3528"))
    c.drawRRect(rrect(bx, FLOOR - 230, 480, 170, 20), paint("#e6e1d6"))
    c.drawRRect(rrect(bx + 120, FLOOR - 250, 380, 150, 30), paint("#3e6b8a" if not alt else "#7a3e5a"))
    c.drawRRect(rrect(bx + 20, FLOOR - 270, 120, 70, 30), paint("#f5f2ea"))
    c.drawRect(skia.Rect.MakeXYWH(bx, FLOOR - 60, 480, 60), paint("#4a3528"))
    # desk + lamp + phone
    dx = 880 if not alt else 220
    c.drawRect(skia.Rect.MakeXYWH(dx, FLOOR - 400, 360, 26), paint("#5d4331"))
    c.drawRect(skia.Rect.MakeXYWH(dx + 20, FLOOR - 374, 22, 374), paint("#4a3528"))
    c.drawRect(skia.Rect.MakeXYWH(dx + 318, FLOOR - 374, 22, 374), paint("#4a3528"))
    lx = dx + 300 if not alt else dx + 50
    c.drawLine(lx, FLOOR - 400, lx - 40, FLOOR - 560, paint("#22252e", stroke=10))
    c.drawPath(path_poly([(lx - 90, FLOOR - 560), (lx + 10, FLOOR - 600), (lx + 20, FLOOR - 540)]), paint("#22252e"))
    glow(c, lx - 30, FLOOR - 520, 260, "#ffd49a" if not alt else "#a9d8ff", 0.35)
    # phone on desk (same place in both worlds)
    c.drawRRect(rrect(dx + 140, FLOOR - 414, 90, 16, 5), paint("#0e0e12"))
    if phone_glow > 0:
        glow(c, dx + 185, FLOOR - 420, 80, "#a6e3ff", phone_glow)
    # books
    for i, cc in enumerate(["#c0392b", "#2c7a7b", "#e1a33b", "#6a4c93"]):
        c.drawRect(skia.Rect.MakeXYWH(dx + 20 + i * 28, FLOOR - 470, 24, 70), paint(cc))
    # clock & frames
    clock(c, 560 if not alt else 1000, 420, 56, t, alt)
    picture(c, 380 if not alt else 560, 560, 130, 160, "sea" if not alt else "sea_alt", t=t)
    if alt:
        picture(c, 60, 360, 120, 150, "double", t=t)
    # plant
    pxp = 40 if not alt else 1240
    c.drawRect(skia.Rect.MakeXYWH(pxp - 40, FLOOR - 120, 80, 120), paint("#a8643c"))
    for i in range(6):
        a = -1.2 + i * 0.5
        lc = "#3f8f4f" if not alt else "#556070"
        c.drawPath(smooth_path([(pxp, FLOOR - 120), (pxp + math.sin(a) * 60, FLOOR - 200 - abs(math.cos(a)) * 60),
                                (pxp + math.sin(a) * 120, FLOOR - 260 + (80 if alt else 0))], False), paint(lc, stroke=18))
    # door (on the left wall section)
    if door_x is not None:
        def inside(cc, ix, iy, iw, ih):
            cc.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), paint("#b88a5e"))
            glow(cc, ix + iw / 2, iy + ih * 0.3, iw, "#ffcf8a", 0.6)
        door(c, door_x, FLOOR, 300, 740, "#7a5236", open_k=door_state, inside=inside)
        if entering_light > 0:
            glow(c, door_x, FLOOR - 370, 500, "#8fe6ff", entering_light)
    if wall_glow > 0:
        # shimmering outline where the door used to be
        gx = glow_x if door_x is None else door_x
        a = wall_glow * (0.6 + 0.4 * math.sin(t * 9))
        c.drawRect(skia.Rect.MakeXYWH(gx - 160, FLOOR - 760, 320, 760), paint("#9feaff", a, stroke=6, blur=6))
        glow(c, gx, FLOOR - 380, 420, "#7fdcff", a * 0.6)


# ====================================================================== kitchen
def kitchen(c, t, x_view=(-300, 2100)):
    x0, x1 = x_view
    wall_paper(c, x0, x1, -400, FLOOR, "#7d8aa0", "#728098")
    # tiles
    for i in range(int((x1 - x0) // 80) + 2):
        for j in range(5):
            xx = x0 - (x0 % 80) + i * 80
            c.drawRect(skia.Rect.MakeXYWH(xx, 860 + j * 80, 78, 78), paint("#b9c4d4" if (i + j) % 2 else "#aab6c8"))
    floor_planks(c, x0, x1, FLOOR, FLOOR + 900, "#3e4252", "#2a2d39")
    # counter
    c.drawRect(skia.Rect.MakeXYWH(-200, FLOOR - 420, 1100, 420), paint("#e6e2da"))
    c.drawRect(skia.Rect.MakeXYWH(-220, FLOOR - 440, 1140, 30), paint("#4c4f5c"))
    for i in range(4):
        c.drawRect(skia.Rect.MakeXYWH(-180 + i * 270, FLOOR - 390, 250, 360), paint("#d3cec4", stroke=4))
        c.drawRect(skia.Rect.MakeXYWH(-80 + i * 270, FLOOR - 260, 50, 10), paint("#8a8e99"))
    # upper cabinets
    for i in range(4):
        c.drawRect(skia.Rect.MakeXYWH(-180 + i * 270, 380, 250, 300), paint("#e6e2da"))
        c.drawRect(skia.Rect.MakeXYWH(-180 + i * 270, 380, 250, 300), paint("#c6c1b7", stroke=4))
    # kettle & mugs
    c.drawPath(smooth_path([(120, FLOOR - 440), (230, FLOOR - 440), (220, FLOOR - 560), (130, FLOOR - 560)]), paint("#c0392b"))
    c.drawCircle(400, FLOOR - 470, 30, paint("#f0eee8"))
    # fridge
    c.drawRRect(rrect(1000, FLOOR - 1020, 330, 1020, 24), paint("#dfe4ea"))
    c.drawLine(1000, FLOOR - 640, 1330, FLOOR - 640, paint("#b4bcc6", stroke=5))
    c.drawRect(skia.Rect.MakeXYWH(1030, FLOOR - 860, 14, 140), paint("#9aa3ad"))
    c.drawRect(skia.Rect.MakeXYWH(1030, FLOOR - 600, 14, 140), paint("#9aa3ad"))
    # magnets / drawing on fridge: a child's drawing of 3 people... with one scratched out
    c.drawRect(skia.Rect.MakeXYWH(1120, FLOOR - 960, 150, 120), paint("#fbfaf4"))
    for k, xx in enumerate((1150, 1195, 1240)):
        c.drawCircle(xx, FLOOR - 920, 12, paint("#333", stroke=3))
        c.drawLine(xx, FLOOR - 908, xx, FLOOR - 870, paint("#333", stroke=3))
    c.drawLine(1180, FLOOR - 940, 1212, FLOOR - 860, paint("#d33", stroke=5))
    c.drawLine(1212, FLOOR - 940, 1180, FLOOR - 860, paint("#d33", stroke=5))
    # window
    c.drawRect(skia.Rect.MakeXYWH(1450, 420, 380, 460), paint("#d7d2c6"))
    c.drawRect(skia.Rect.MakeXYWH(1470, 440, 340, 420), gpaint(lin_grad(0, 440, 0, 860, ["#0b1630", "#1f4e66"])))
    c.drawLine(1640, 440, 1640, 860, paint("#d7d2c6", stroke=12))
    # table
    c.drawRect(skia.Rect.MakeXYWH(1380, FLOOR - 330, 560, 26), paint("#6b4c38"))
    c.drawRect(skia.Rect.MakeXYWH(1420, FLOOR - 304, 22, 304), paint("#5a3f2e"))
    c.drawRect(skia.Rect.MakeXYWH(1880, FLOOR - 304, 22, 304), paint("#5a3f2e"))
    ceiling_lamp(c, 1100, 260, "#cfe3ff", 0.75, 650)


# ====================================================================== street
SIGNS = {
    "ru": [("ПРОДУКТЫ 24", "ПРОДУКТЫ 25"), ("АПТЕКА", "АПТЕКА БЕЗ ВЫХОДА"), ("ХЛЕБ", "ХЛЁБ"), ("КАФЕ «ЛУНА»", "КАФЕ «ДВЕ ЛУНЫ»")],
    "en": [("GROCERY 24", "GROCERY 25"), ("PHARMACY", "PHARMACY NO EXIT"), ("BAKERY", "BAKREY"), ("CAFE MOON", "CAFE TWO MOONS")],
}


def street(c, t, lang, glitch=0.0, x_view=(-600, 3600), number_swap=1.0):
    x0, x1 = x_view
    # sky
    c.drawRect(skia.Rect.MakeLTRB(x0, -3200, x1, FLOOR + 1900), gpaint(lin_grad(0, -2400, 0, 1300, ["#040812", "#0e2140", "#2a4f6e"])))
    # two moons
    glow(c, 700, -380, 420, "#8fd8ff", 0.35)
    c.drawCircle(700, -380, 90, paint("#e9f7ff"))
    c.drawCircle(1040, -520, 46, paint("#d8f0ff"))
    glow(c, 1040, -520, 200, "#8fd8ff", 0.25)
    rnd = random.Random(11)
    for i in range(80):
        c.drawCircle(x0 + rnd.random() * (x1 - x0), -1200 + rnd.random() * 900, rnd.uniform(1, 3),
                     paint("#ffffff", 0.3 + 0.5 * (0.5 + 0.5 * math.sin(t * 2 + i))))
    # far skyline: tall strange towers (some leaning, one floating)
    for i in range(22):
        bx = x0 + i * 200 + rnd.uniform(-30, 30)
        bh = rnd.uniform(1500, 2600)
        bw = rnd.uniform(110, 190)
        c.save()
        c.translate(bx + bw / 2, FLOOR - 300)
        c.rotate(rnd.uniform(-4, 4) if i % 4 == 0 else 0)
        c.drawRect(skia.Rect.MakeXYWH(-bw / 2, -bh, bw, bh), paint("#132640"))
        for j in range(int(bh // 70)):
            for k in range(int(bw // 40)):
                if rnd.random() < 0.3:
                    c.drawRect(skia.Rect.MakeXYWH(-bw / 2 + 12 + k * 40, -bh + 20 + j * 70, 18, 26),
                               paint("#6fdcff", 0.25 + 0.3 * rnd.random()))
        c.restore()
    # floating block
    fy = -700 + math.sin(t * 0.7) * 30
    c.save()
    c.translate(1950, fy)
    c.rotate(8 + math.sin(t * 0.5) * 3)
    c.drawRect(skia.Rect.MakeXYWH(-230, -160, 460, 320), paint("#18304d"))
    for k in range(5):
        for j in range(2):
            c.drawRect(skia.Rect.MakeXYWH(-200 + k * 85, -110 + j * 120, 45, 60), paint("#8ff0ff", 0.65))
    c.restore()
    glow(c, 1950, fy + 260, 380, "#7fdcff", 0.3)
    # an upside-down tower hanging from the sky
    c.drawRect(skia.Rect.MakeXYWH(820, -2600, 240, 1500), paint("#10223a"))
    for j in range(14):
        c.drawRect(skia.Rect.MakeXYWH(850 + (j % 3) * 70, -2560 + j * 100, 30, 44), paint("#ff9fd8", 0.45))
    c.drawPath(path_poly([(820, -1100), (1060, -1100), (940, -980)]), paint("#10223a"))
    # near buildings (shop fronts)
    signs = SIGNS[lang]
    for i in range(4):
        sx = i * 900 - 300
        c.drawRect(skia.Rect.MakeXYWH(sx, FLOOR - 1500, 860, 1500), paint(["#2d3f5c", "#33435f", "#2a3a52", "#384a66"][i]))
        # upper windows
        for j in range(3):
            for k in range(4):
                lit = hash1(i * 31 + j * 7 + k) > 0.5
                c.drawRect(skia.Rect.MakeXYWH(sx + 70 + k * 190, FLOOR - 1400 + j * 230, 110, 150),
                           paint("#7fd0ff" if lit else "#16233a", 0.55 if lit else 1))
        # shop window
        c.drawRect(skia.Rect.MakeXYWH(sx + 60, FLOOR - 560, 520, 420), paint("#0c1626"))
        glow(c, sx + 320, FLOOR - 360, 380, "#62c9ff", 0.25)
        # entrance door
        c.drawRect(skia.Rect.MakeXYWH(sx + 630, FLOOR - 460, 180, 460), paint("#151d2c"))
        # sign
        name = signs[i][1]
        flick = 1.0 if hash1(math.floor(t * 8) + i * 13) > 0.08 else 0.35
        c.drawRect(skia.Rect.MakeXYWH(sx + 40, FLOOR - 700, 780, 110), paint("#0b1220"))
        c.drawRect(skia.Rect.MakeXYWH(sx + 40, FLOOR - 700, 780, 110), paint("#62d6ff", 0.8 * flick, stroke=5))
        size = 64 if len(name) < 14 else 50
        glow(c, sx + 430, FLOOR - 645, 330, "#62d6ff", 0.25 * flick)
        text_center(c, name, sx + 430, FLOOR - 622, size, mix("#bff3ff", "#ffffff", 0.3), "Black", alpha=flick)
        # house number plate
        num = ["7", "14", "41", "3"][i]
        if i == 1:
            num = "14" if number_swap < 0.5 else "41"
        house_plate(c, sx + 720, FLOOR - 900, num, t, glitch if i == 1 else 0)
    # street lamps
    for i in range(5):
        lx = i * 800
        c.drawRect(skia.Rect.MakeXYWH(lx - 8, FLOOR - 900, 16, 900), paint("#0d1626"))
        c.drawRect(skia.Rect.MakeXYWH(lx - 8, FLOOR - 900, 110, 14), paint("#0d1626"))
        glow(c, lx + 100, FLOOR - 880, 360, "#a8e6ff", 0.45)
        c.drawOval(skia.Rect.MakeLTRB(lx - 250, FLOOR - 30, lx + 450, FLOOR + 140),
                   gpaint(rad_grad(lx + 100, FLOOR + 50, 350, [(140, 220, 255, 70), (140, 220, 255, 0)])))
    # pavement
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR, x1, FLOOR + 1900), paint("#1a2232"))
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR, x1, FLOOR + 16), paint("#2c3a52"))
    for i in range(int((x1 - x0) / 220) + 2):
        xx = x0 - (x0 % 220) + i * 220
        c.drawLine(xx, FLOOR + 16, xx - 60, FLOOR + 400, paint("#111827", stroke=3))
    # puddle reflections
    c.drawOval(skia.Rect.MakeXYWH(900, FLOOR + 120, 500, 60), paint("#5ac8ff", 0.12))


def house_plate(c, x, y, num, t, glitch=0.0):
    c.drawRRect(rrect(x - 70, y - 50, 140, 100, 10), paint("#1b4f8c"))
    c.drawRRect(rrect(x - 62, y - 42, 124, 84, 8), paint("#ffffff", stroke=4))
    if glitch > 0:
        for k in range(3):
            dx = (hash1(math.floor(t * 20) + k) - 0.5) * 30 * glitch
            text_center(c, num, x + dx, y + 24, 66, ["#ff3b5c", "#3bffd0", "#ffffff"][k], "Black", alpha=0.7)
    else:
        text_center(c, num, x, y + 24, 66, "#ffffff", "Black")


# ====================================================================== phone UI
def phone(c, cx, cy, w, t, screen_fn, tilt=0.0, glow_a=0.6):
    h = w * 2.05
    c.save()
    c.translate(cx, cy)
    c.rotate(tilt)
    glow(c, 0, 0, w * 1.1, "#7fd6ff", glow_a * 0.35)
    c.drawRRect(rrect(-w / 2 - 6, -h / 2 - 6, w + 12, h + 12, w * 0.13), paint("#000000", 0.5, blur=18))
    c.drawRRect(rrect(-w / 2, -h / 2, w, h, w * 0.12), paint("#0b0c10"))
    c.drawRRect(rrect(-w / 2, -h / 2, w, h, w * 0.12), paint("#3a3d48", stroke=4))
    sx, sy, sw, sh = -w / 2 + w * 0.045, -h / 2 + w * 0.045, w * 0.91, h - w * 0.09
    c.save()
    c.clipRRect(rrect(sx, sy, sw, sh, w * 0.09), doAntiAlias=True)
    screen_fn(c, sx, sy, sw, sh)
    c.restore()
    # notch
    c.drawRRect(rrect(-w * 0.14, sy + w * 0.03, w * 0.28, w * 0.07, w * 0.035), paint("#000000"))
    c.restore()


def hand_back(c, cx, cy, w, skin="#d4a47c", sleeve="#25262d"):
    """palm + sleeve behind the phone"""
    h = w * 2.05
    c.drawPath(smooth_path([(cx - w * 0.95, cy + h * 1.2), (cx - w * 0.75, cy + h * 0.62), (cx - w * 0.2, cy + h * 0.5),
                            (cx + w * 0.45, cy + h * 0.55), (cx + w * 0.7, cy + h * 0.75), (cx + w * 0.6, cy + h * 1.2)]),
               paint(sleeve))
    c.drawOval(skia.Rect.MakeLTRB(cx - w * 0.62, cy + h * 0.28, cx + w * 0.55, cy + h * 0.62), paint(skin))
    c.drawOval(skia.Rect.MakeLTRB(cx - w * 0.62, cy + h * 0.28, cx + w * 0.55, cy + h * 0.62),
               gpaint(lin_grad(0, cy + h * 0.28, 0, cy + h * 0.62, [(0, 0, 0, 0), (0, 0, 0, 90)])))


def hand_front(c, cx, cy, w, skin="#d4a47c"):
    """fingers wrapping the left edge, thumb on the right edge"""
    h = w * 2.05
    for k in range(4):
        y = cy + h * (0.02 + k * 0.095)
        c.drawRRect(rrect(cx - w * 0.58, y, w * 0.15, h * 0.08, w * 0.07), paint(shade(skin, -0.04 * k)))
        c.drawRRect(rrect(cx - w * 0.58, y, w * 0.15, h * 0.08, w * 0.07), paint("#000000", 0.18, stroke=2))
    c.drawPath(smooth_path([(cx + w * 0.38, cy + h * 0.46), (cx + w * 0.40, cy + h * 0.22), (cx + w * 0.47, cy + h * 0.16),
                            (cx + w * 0.56, cy + h * 0.22), (cx + w * 0.58, cy + h * 0.46)]), paint(skin))
    c.drawPath(smooth_path([(cx + w * 0.38, cy + h * 0.46), (cx + w * 0.40, cy + h * 0.22), (cx + w * 0.47, cy + h * 0.16),
                            (cx + w * 0.56, cy + h * 0.22), (cx + w * 0.58, cy + h * 0.46)]), paint("#000000", 0.15, stroke=2))


def hand_holding(c, cx, cy, w, skin="#d4a47c", sleeve="#25262d"):
    hand_front(c, cx, cy, w, skin)


def status_bar(c, sx, sy, sw, time_s="21:14"):
    text_center(c, time_s, sx + sw * 0.16, sy + 52, 30, "#ffffff", "SemiBold")
    c.drawRRect(rrect(sx + sw - 90, sy + 30, 52, 24, 6), paint("#ffffff", stroke=3))
    c.drawRect(skia.Rect.MakeXYWH(sx + sw - 85, sy + 35, 30, 14), paint("#ffffff"))


def gallery_screen(lang, t, reveal=1.0):
    def fn(c, sx, sy, sw, sh):
        c.drawRect(skia.Rect.MakeXYWH(sx, sy, sw, sh), paint("#0d0f14"))
        status_bar(c, sx, sy, sw)
        text_center(c, "Фото" if lang == "ru" else "Photos", sx + sw * 0.2, sy + 140, 46, "#ffffff", "Bold")
        cols = 2
        tw = (sw - 30) / cols
        th = tw * 1.15
        scenes = ["birthday", "sea", "school", "friends", "family", "selfie"]
        for i, sc in enumerate(scenes):
            gx = sx + 10 + (i % cols) * (tw + 10)
            gy = sy + 180 + (i // cols) * (th + 10)
            thumb(c, gx, gy, tw, th, sc, t)
    return fn


def thumb(c, x, y, w, h, sc, t):
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    pal = {"birthday": ("#f7c6a3", "#e98a6b"), "sea": ("#8ed1f2", "#2f84b8"), "school": ("#e9e3c9", "#a8b48a"),
           "friends": ("#f2d488", "#86b36e"), "family": ("#cfe3f5", "#7bb36a"), "selfie": ("#b6c2d6", "#5d6c8f")}[sc]
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), gpaint(lin_grad(0, y, 0, y + h, [pal[0], pal[1]])))
    base = y + h * 0.98
    s = h / 1150
    if sc == "birthday":
        c.drawRect(skia.Rect.MakeXYWH(x + w * 0.3, y + h * 0.62, w * 0.4, h * 0.2), paint("#fff3e6"))
        for k in range(3):
            c.drawRect(skia.Rect.MakeXYWH(x + w * (0.38 + k * 0.1), y + h * 0.52, 5, h * 0.1), paint("#e74c3c"))
            glow(c, x + w * (0.38 + k * 0.1) + 2, y + h * 0.5, 14, "#ffd27a", 0.9)
    if sc == "friends":
        mom_c.draw(c, x + w * 0.2, base, s * 0.8, pose(tr=0.2, t=1))
        dad_c.draw(c, x + w * 0.8, base, s * 0.8, pose(tr=-0.2, t=1))
    if sc == "family":
        dad_c.draw(c, x + w * 0.25, base, s * 0.9, pose(tr=0.2, t=1))
        mom_c.draw(c, x + w * 0.75, base, s * 0.9, pose(tr=-0.2, t=1))
    if sc == "school":
        c.drawRect(skia.Rect.MakeXYWH(x, y + h * 0.15, w, h * 0.35), paint("#2f4f3f"))
    if sc == "sea":
        c.drawRect(skia.Rect.MakeXYWH(x, y + h * 0.6, w, h), paint("#e9d29a"))
    # the empty spot where the hero used to be: dashed silhouette outline
    cx = x + w * 0.5
    sil = skia.Path()
    sil.addCircle(cx, y + h * 0.38, h * 0.11)
    sil.addRRect(rrect(cx - h * 0.12, y + h * 0.5, h * 0.24, h * 0.5, h * 0.08))
    p = paint("#ffffff", 0.55, stroke=3)
    p.setPathEffect(skia.DashPathEffect.Make([10, 8], (t * 30) % 18))
    c.drawPath(sil, p)
    c.restore()


def message_screen(lang, t, banner=0.0, opened=0.0, typed=1.0):
    sender = "Я" if lang == "ru" else "Me"
    number = "+7 999 014-14-14" if lang == "ru" else "+1 (555) 014-1414"
    msg = "Не пытайся вернуться. Здесь уже есть ты." if lang == "ru" else "Don't try to come back. There's already a you here."

    def fn(c, sx, sy, sw, sh):
        if opened < 1:
            gallery_screen(lang, t)(c, sx, sy, sw, sh)
            c.drawRect(skia.Rect.MakeXYWH(sx, sy, sw, sh), paint("#000000", 0.35 * banner))
        if opened > 0:
            c.saveLayerAlpha(None, int(255 * opened))
            c.drawRect(skia.Rect.MakeXYWH(sx, sy, sw, sh), paint("#0b0d12"))
            status_bar(c, sx, sy, sw)
            c.drawRect(skia.Rect.MakeXYWH(sx, sy + 80, sw, 150), paint("#161922"))
            c.drawCircle(sx + sw / 2, sy + 130, 34, paint("#3b4256"))
            text_center(c, sender[0], sx + sw / 2, sy + 144, 36, "#ffffff", "Bold")
            text_center(c, number, sx + sw / 2, sy + 205, 28, "#9aa3b5", "Medium")
            # bubble
            f = font(40, "SemiBold")
            n = int(len(msg) * clamp(typed))
            shown = msg[:n]
            lines = wrap(msg, f, sw * 0.62)
            # map typed chars over the wrapped lines
            out, k = [], 0
            for ln in lines:
                take = max(0, min(len(ln), n - k))
                out.append(ln[:take])
                k += len(ln) + 1
            bh = 30 + len(lines) * 52
            bx, by = sx + 24, sy + 290
            c.drawRRect(rrect(bx, by, sw * 0.72, bh, 30), paint("#2a2f3c"))
            for i, ln in enumerate(out):
                c.drawString(ln, bx + 28, by + 58 + i * 52, f, paint("#ffffff"))
            text_center(c, "21:14", bx + sw * 0.62, by + bh + 36, 24, "#6b7385", "Medium")
            c.restore()
        if banner > 0 and opened < 1:
            by = sy - 200 + 230 * ease_out(banner)
            c.drawRRect(rrect(sx + 16, by, sw - 32, 170, 34), paint("#e9edf5", 0.96))
            c.drawRRect(rrect(sx + 40, by + 28, 64, 64, 16), paint("#34c759"))
            c.drawRRect(rrect(sx + 56, by + 46, 32, 24, 8), paint("#ffffff"))
            c.drawString(sender + "  " + number, sx + 124, by + 58, font(30, "Bold"), paint("#111"))
            prev = msg if len(msg) < 26 else msg[:24] + "…"
            c.drawString(prev, sx + 124, by + 108, font(30, "Medium"), paint("#333"))
            c.drawString("сейчас" if lang == "ru" else "now", sx + sw - 140, by + 58, font(24, "Medium"), paint("#777"))
    return fn


# ====================================================================== void (confrontation)
def void(c, t, x_view=(-1000, 2200), intensity=1.0):
    x0, x1 = x_view
    c.drawRect(skia.Rect.MakeLTRB(x0, -1500, x1, 3500), gpaint(lin_grad(0, -500, 0, 2500, ["#03050b", "#0a1424", "#03050b"])))
    # distant city silhouettes, very dark
    rnd = random.Random(4)
    for i in range(18):
        bx = x0 + i * 200
        bh = rnd.uniform(300, 900)
        c.drawRect(skia.Rect.MakeXYWH(bx, FLOOR - bh, 180, bh), paint("#0a1626"))
        for j in range(int(bh // 90)):
            if rnd.random() < 0.3:
                c.drawRect(skia.Rect.MakeXYWH(bx + 30 + (j % 3) * 45, FLOOR - bh + 30 + j * 90, 16, 22), paint("#4fc3ff", 0.25))
    c.drawRect(skia.Rect.MakeLTRB(x0, FLOOR, x1, 3500), paint("#060a12"))
    # spotlight cone from above
    cone = path_poly([(520, -600), (580, -600), (980, FLOOR + 40), (120, FLOOR + 40)])
    c.drawPath(cone, gpaint(lin_grad(0, -600, 0, FLOOR, [(150, 220, 255, int(70 * intensity)), (150, 220, 255, int(18 * intensity))])))
    c.drawOval(skia.Rect.MakeLTRB(150, FLOOR - 60, 950, FLOOR + 90), gpaint(rad_grad(550, FLOOR, 420, [(160, 225, 255, int(110 * intensity)), (160, 225, 255, 0)])))


def fog(c, t, y0, y1, colr="#9cc9ff", a=0.18, x_view=(-1000, 4000), speed=20):
    x0, x1 = x_view
    for i in range(7):
        fx = x0 + ((i * 640 + t * speed * (1 + i % 3 * 0.4)) % (x1 - x0 + 800)) - 400
        fy = lerp(y0, y1, hash1(i * 5.3))
        r = 380 + 160 * hash1(i * 2.2)
        c.drawOval(skia.Rect.MakeXYWH(fx - r * 1.6, fy - r * 0.5, r * 3.2, r), paint(colr, a, blur=r * 0.35))


def particles(c, t, cx, cy, n=40, radius=600, colr="#9fe8ff", a=1.0, swirl=1.0, seed=0, size=6):
    for i in range(n):
        h1, h2, h3 = hash1(i * 3.7 + seed), hash1(i * 9.1 + seed), hash1(i * 1.3 + seed)
        ang = h1 * 6.283 + t * (0.4 + h2) * swirl
        rr = radius * (0.2 + 0.8 * ((h3 + t * 0.15) % 1.0))
        x = cx + math.cos(ang) * rr
        y = cy + math.sin(ang) * rr * 0.9 - t * 30 * h2
        tw = 0.5 + 0.5 * math.sin(t * 5 + i)
        glow(c, x, y, size * (1.5 + h2 * 2.5), colr, a * tw)
