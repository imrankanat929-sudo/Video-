"""1920x1080 thumbnail in the same style."""
import math
import sys
from PIL import Image

import render
from gfx import *  # noqa
from scenes import HOOK_CROWD


def draw(ctx, t):
    ground(ctx, 1)
    cone_light(ctx, 1380, GY, 1.6)
    for dx, sc in HOOK_CROWD:
        x = 1380 + dx * 0.75
        if x > 1950:
            continue
        side = 1 if dx > 0 else -1
        person(ctx, x, GY, sc * 0.9, 0.45, look=-side, lean=-side * 0.05, lum=0.6)
        cx, cy = head_pos(x, GY, sc * 0.9, -side)
        hx, hy = head_pos(1380, GY, 1.15)
        line(ctx, cx, cy, hx + side * 40, hy + 10, 1, 2.4, 0.5, dash=[6, 9])
    person(ctx, 1380, GY, 1.15, 1.0, stretch=0.97, lean=-0.03)
    for k, x, y in (("heart", 1180, 380), ("?", 1600, 350), ("check", 1650, 520),
                    ("cross", 1120, 560)):
        badge(ctx, k, x, y, 36, 1.0, 1.0, outline=(k == "cross"))
    text(ctx, "ПОЧЕМУ МЫ", 110, 330, 108, 1, "bold", 3, align="left")
    text(ctx, "ХОТИМ ВСЕМ", 110, 465, 108, 1, "bold", 3, align="left")
    w = text_width(ctx, "НРАВИТЬСЯ?", 92, "bold", 3)
    rrect(ctx, 100, 540, w + 60, 135, 67)
    white(ctx, 1)
    ctx.fill()
    text(ctx, "НРАВИТЬСЯ?", 130, 607, 92, 1, "bold", 3, align="left",
         color=(0.03, 0.03, 0.03))
    text(ctx, "HUMAN MIND  ·  ЭПИЗОД 01", 112, 760, 26, 0.75, "bold", 6, align="left")


render.draw_scenes = draw
render.particles = lambda ctx, t: None
out = sys.argv[1] if len(sys.argv) > 1 else "thumbnail.png"
Image.fromarray(render.render_frame(200.0)).convert("RGB").save(out)
print(out)
