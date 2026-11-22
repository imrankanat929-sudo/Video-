"""1080x1920 (9:16) thumbnail in the same style."""
import math
import sys

import cairo
import numpy as np
from PIL import Image, ImageFilter

from gfx import *  # noqa

VW, VH = 1080, 1920
CROWD = [(-560, 0.78), (-310, 0.84), (310, 0.84), (560, 0.78)]


def background():
    y, x = np.mgrid[0:VH, 0:VW].astype(np.float32)
    d = np.sqrt(((x - VW / 2) / VW) ** 2 + ((y - VH * 0.62) / VH) ** 2 * 0.6)
    bg = 0.018 + 0.05 * np.exp(-(d / 0.45) ** 2)
    grid = np.zeros((VH, VW), np.float32)
    for gy in range(19, VH, 38):
        for gx in range(19, VW, 38):
            grid[gy - 1:gy + 1, gx - 1:gx + 1] = 1.0
    bg += grid * 0.07 * np.exp(-(d / 0.6) ** 2)
    return bg * (1 - 0.7 * np.clip(d / 0.8, 0, 1) ** 2)


def blur(img, f, r):
    s = Image.fromarray(img).resize((VW // f, VH // f), Image.BILINEAR)
    s = s.filter(ImageFilter.GaussianBlur(r))
    return np.asarray(s.resize((VW, VH), Image.BILINEAR), np.float32) / 255


def draw(ctx):
    # stage: same character scene as the video, scaled up for portrait
    ctx.save()
    ctx.translate(540, 1500)
    ctx.scale(1.25, 1.25)
    ctx.translate(-960, -GY)
    ground(ctx, 1)
    cone_light(ctx, 960, GY, 1.7)
    hx, hy = head_pos(960, GY, 1.0)
    for dx, sc in CROWD:
        side = 1 if dx > 0 else -1
        x = 960 + dx
        person(ctx, x, GY, sc, 0.5, look=-side, lean=-side * 0.05, lum=0.6)
        cx, cy = head_pos(x, GY, sc, -side)
        line(ctx, cx, cy, hx + side * 36, hy + 10, 1, 2.4, 0.55, dash=[6, 9])
    person(ctx, 960, GY, 1.0, 1.0, stretch=0.97, lean=-0.03)
    for k, x, y in (("heart", 760, 330), ("?", 1170, 290), ("check", 1250, 440),
                    ("cross", 670, 460)):
        badge(ctx, k, x, y, 32, 1.0, 1.0, outline=(k == "cross"))
    ctx.restore()
    # title
    text(ctx, "ПОЧЕМУ МЫ", 540, 300, 112, 1, "bold", 3)
    text(ctx, "ХОТИМ ВСЕМ", 540, 435, 112, 1, "bold", 3)
    w = text_width(ctx, "НРАВИТЬСЯ?", 100, "bold", 3)
    rrect(ctx, 540 - w / 2 - 34, 505, w + 68, 145, 72)
    white(ctx, 1)
    ctx.fill()
    text(ctx, "НРАВИТЬСЯ?", 540, 577, 100, 1, "bold", 3, color=(0.03, 0.03, 0.03))
    text(ctx, "HUMAN MIND  ·  ЭПИЗОД 01", 540, 1730, 30, 0.75, "bold", 7)


def main(out):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, VW, VH)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    draw(ctx)
    surf.flush()
    buf = np.ndarray((VH, VW, 4), np.uint8, surf.get_data())
    lum8 = buf[:, :, 2].copy()
    A = buf[:, :, 3].astype(np.float32) / 255
    L = lum8.astype(np.float32) / 255
    # glow only around the light, not over the dark text inside the pill
    out_img = background() * (1 - A) + L + 0.5 * blur(lum8, 4, 3) * (1 - A * (L < 0.5)) \
        + 0.4 * blur(lum8, 8, 7)
    out_img = np.clip(out_img, 0, 1) ** 0.95
    Image.fromarray((out_img * 255 + 0.5).astype(np.uint8)).convert("RGB").save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "thumbnail_9x16.png")
