"""Vertical 9:16 cover (1080x1920). Usage: python thumb_vertical.py LANG OUT.png"""
import sys

import cairo
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from hm_core import (STAND_Y, dashed_ground, draw_figure, draw_stairs, draw_text, light_pool, orb, stair_top,
                     stand, tonemap)

VW, VH = 1080, 1920
LINES = {"en": (["SMALL", "STEPS."], ["BIG", "CHANGE."], 168),
         "ru": (["МАЛЕНЬКИЕ", "ШАГИ."], ["БОЛЬШИЕ", "ПЕРЕМЕНЫ."], 132)}


def layer():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    c = cairo.Context(s)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    return s, c


def arrays(s):
    s.flush()
    a = np.ndarray((VH, VW, 4), np.uint8, s.get_data())
    return a[:, :, 2] / 255.0, a[:, :, 3] / 255.0


def glow(lum, s1, s2):
    def up(x):
        return np.asarray(Image.fromarray(x.astype(np.float32)).resize((VW, VH), Image.BILINEAR))
    q = lum.reshape(VH // 4, 4, VW // 4, 4).mean(axis=(1, 3))
    q2 = q.reshape(VH // 8, 2, VW // 8, 2).mean(axis=(1, 3))
    return up(gaussian_filter(q, s1)) * 0.85 + up(gaussian_filter(q2, s2)) * 1.25


def main(lang, out):
    fg, c = layer()
    ui, u = layer()
    n, w, h, x0, y0 = 6, 122, 108, 330, 1640
    light_pool(c, 700, 1250, 800, 0.07)
    dashed_ground(c, -50, VW + 50, y0, 0.5, 3)
    lit = [0.2 + 0.8 * (i / (n - 1)) ** 1.4 for i in range(n)]
    draw_stairs(c, x0, y0, n, w, h, lit=lit, lw=4)
    orb(c, x0 + n * w - 70, y0 - n * h - 95, 22, 0.0)
    for i in range(n):
        x, y = stair_top(x0, y0, w, h, i)
        c.new_sub_path(); c.arc(x - 18, y - 12, 5, 0, 6.2832)
        c.set_source_rgba(1, 1, 1, 0.35 + 0.6 * i / n); c.fill()
    sc = 1.45
    P = stand(220, lean=-0.06, head=-0.3, t=0, scale=sc)
    P["y"] = y0 + STAND_Y * sc + 2
    P["foot_n"] = (230, y0); P["foot_f"] = (210, y0)
    P["arm_n"] = (0.35, 0.3)
    light_pool(c, 220, y0 - 140, 320, 0.13)
    draw_figure(c, P)
    a, b, size = LINES[lang]
    x = 84
    draw_text(u, "HUMAN MIND", x + 4, 200, 34, "Inter SemiBold", "l", 13, (1, 1, 1, 0.7))
    y = 250 + size * 1.15
    for i, line in enumerate(a + b):
        draw_text(u, line, x, y, size, "Inter Bold", "l", 2, (1, 1, 1, 0.9 if i < 2 else 1.0))
        y += size * (1.02 if i != 1 else 1.22)
    u.move_to(x + 6, y - size * 0.55); u.line_to(x + 300, y - size * 0.55)
    u.set_source_rgba(1, 1, 1, 0.9); u.set_line_width(9); u.stroke()
    yy, xx = np.mgrid[0:VH, 0:VW].astype(np.float32)
    r = np.sqrt(((xx - VW / 2) / (VW * 0.9)) ** 2 + ((yy - VH * 0.55) / (VH * 0.6)) ** 2)
    vig = 0.075 * np.clip(1 - r, 0, 1) ** 1.6 + 0.012
    lum, alp = arrays(fg)
    ul, ua = arrays(ui)
    img = vig * (1 - alp) + lum + glow(lum, 3.0, 7.0) * 0.65
    img = img * (1 - ua) + ul + glow(ul, 2.5, 6.0) * 0.45
    img = np.clip(tonemap(img), 0, 1)
    im = Image.fromarray((img * 255 + 0.5).astype(np.uint8)).convert("RGB")
    im.save(out, optimize=True)
    im.save(out.replace(".png", ".jpg"), quality=93)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
