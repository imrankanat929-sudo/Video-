"""YouTube thumbnail (16:9). Usage: python thumb.py LANG OUT.png"""
import math
import sys

import numpy as np
from PIL import Image

from hm_core import *  # noqa

LINES = {"en": ("SMALL STEPS.", "BIG CHANGE."), "ru": ("МАЛЕНЬКИЕ ШАГИ.", "БОЛЬШИЕ ПЕРЕМЕНЫ.")}


def main(lang, out):
    fg, c = new_layer()
    ui, u = new_layer()
    n, w, h, x0, y0 = 9, 112, 92, 860, 985
    light_pool(c, 1500, 500, 900, 0.06)
    dashed_ground(c, -50, 2000, y0, 0.5, 3)
    lit = [0.15 + 0.85 * (i / (n - 1)) ** 1.4 for i in range(n)]
    draw_stairs(c, x0, y0, n, w, h, lit=lit, lw=4)
    orb(c, x0 + n * w - 20, y0 - n * h - 95, 22, 0.0)
    for i in range(n):  # small glowing footsteps on each step
        x, y = stair_top(x0, y0, w, h, i)
        c.new_sub_path(); c.arc(x - 18, y - 12, 5, 0, 6.2832)
        c.set_source_rgba(1, 1, 1, 0.35 + 0.6 * i / n); c.fill()
    P = stand(780, lean=-0.06, head=-0.3, t=0, scale=1.25)
    P["y"] = y0 + STAND_Y * 1.25 + 2
    P["foot_n"] = (790, y0); P["foot_f"] = (770, y0)
    P["arm_n"] = (0.35, 0.3)
    light_pool(c, 780, y0 - 120, 300, 0.12)
    draw_figure(c, P)
    l1, l2 = LINES[lang]
    size = 150 if lang == "en" else 100
    draw_text(u, l1, 100, 330, size, "Inter Bold", "l", 2, (1, 1, 1, 0.9))
    draw_text(u, l2, 100, 330 + size * 1.12, size, "Inter Black" if False else "Inter Bold", "l", 2, (1, 1, 1, 1))
    u.move_to(106, 330 + size * 1.12 + 50); u.line_to(106 + 260, 330 + size * 1.12 + 50)
    u.set_source_rgba(1, 1, 1, 0.9); u.set_line_width(8); u.stroke()
    draw_text(u, "HUMAN MIND", 104, 150, 30, "Inter SemiBold", "l", 12, (1, 1, 1, 0.7))
    lum, alp = layer_arrays(fg)
    ul, ua = layer_arrays(ui)
    img = VIGNETTE * 1.4 * (1 - alp) + lum + glow(lum) * 0.65
    img = img * (1 - ua) + ul + glow(ul, 2.5, 6) * 0.45
    img = np.clip(tonemap(img), 0, 1)
    im = Image.fromarray((img * 255 + 0.5).astype(np.uint8)).convert("RGB")
    im.save(out, optimize=True)
    im.resize((1280, 720), Image.LANCZOS).save(out.replace(".png", "_1280x720.jpg"), quality=92)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
