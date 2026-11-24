"""YouTube thumbnail: two overlapping identical hallways behind the stickman.
usage: python3 thumbnail.py <lang> <out.png>
"""
import os, sys, math
import numpy as np
import skia
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from render import (W, H, fill, stroke, draw_text, text_width, draw_man, pill, HEAD_Y)

TXT = {"en": ("I’VE SEEN", "THIS BEFORE"), "ru": ("Я УЖЕ", "ЭТО ВИДЕЛ")}


def hallway(c, cx, cy, w, h, a):
    """One-point perspective corridor occupying rect centred on (cx, cy)."""
    L, R, T, B = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    vw, vh = w * 0.16, h * 0.2
    vx, vy = cx, cy + h * 0.02
    bl, br, bt, bb = vx - vw / 2, vx + vw / 2, vy - vh / 2, vy + vh / 2
    c.drawRect(skia.Rect(bl, bt, br, bb), fill(0.10 * a))
    c.drawRect(skia.Rect(bl, bt, br, bb), stroke(3, 0.9 * a))
    # glowing door at the end
    c.drawRect(skia.Rect(vx - vw * 0.18, bt + vh * 0.3, vx + vw * 0.18, bb), fill(0.75 * a))
    for (x1, y1, x2, y2) in [(bl, bt, L, T), (br, bt, R, T), (bl, bb, L, B), (br, bb, R, B)]:
        c.drawLine(x1, y1, x2, y2, stroke(3, 0.75 * a))
    # depth frames
    for k in range(1, 6):
        u = (k / 6) ** 1.8
        l, r = lerp(bl, L, u), lerp(br, R, u)
        t, b = lerp(bt, T, u), lerp(bb, B, u)
        c.drawRect(skia.Rect(l, t, r, b), stroke(1.6, 0.18 * a))
    # side doors (trapezoids) on both walls
    for side in (-1, 1):
        for k, u0 in enumerate((0.25, 0.55)):
            u1 = u0 + 0.16
            def wall_pt(u, frac):
                x = lerp(bl if side < 0 else br, L if side < 0 else R, u)
                tt = lerp(bt, T, u); bb2 = lerp(bb, B, u)
                return x, lerp(bb2, tt, frac)
            x0, y0b = wall_pt(u0, 0.0); _, y0t = wall_pt(u0, 0.62)
            x1, y1b = wall_pt(u1, 0.0); _, y1t = wall_pt(u1, 0.62)
            p = skia.Path(); p.moveTo(x0, y0b); p.lineTo(x0, y0t); p.lineTo(x1, y1t); p.lineTo(x1, y1b)
            c.drawPath(p, stroke(3, 0.85 * a))
            hx, hy = lerp(x0, x1, 0.8), lerp(y0b, y1b, 0.8) - (y1b - y1t) * 0.45
            c.drawCircle(hx, hy, 4 + 3 * u0, fill(a))
    # ceiling lights
    for k in range(1, 5):
        u = (k / 5) ** 1.6
        y = lerp(bt, T, u) + 6
        ww = lerp(vw * 0.15, w * 0.12, u)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - ww / 2, y, cx + ww / 2, y + 4 + 8 * u), 3, 3), fill(0.9 * a))
    # floor centre dashes
    c.drawLine(vx, bb, cx, B, stroke(2.5, 0.35 * a, dash=[18, 14], cap=False))


def lerp(a, b, u):
    return a + (b - a) * u


def main(lang, out):
    em = skia.Surface(W, H); c = em.getCanvas(); c.clear(skia.ColorTRANSPARENT)
    # two identical hallways, the second slipping over the first
    hallway(c, 960, 640, 1500, 900, 1.0)
    c.save(); c.translate(70, -36); hallway(c, 960, 640, 1500, 900, 0.42); c.restore()
    # glitch slices across the overlap
    for y0, hh, dx in ((470, 10, 60), (560, 6, -40), (700, 14, 80)):
        c.drawRect(skia.Rect(400 + dx, y0, 1500 + dx, y0 + hh), fill(0.10))
    # stickman centre with his echo
    draw_man(c, 1000 + 40, 1060, s=2.3, facing=1, a=0.28)
    draw_man(c, 960, 1060, s=2.3, facing=1, eyes=1.0, look=(0.0, -0.05))
    # text
    l1, l2 = TXT[lang]
    size = 150
    while max(text_width(l1, size, "Black", 0.04), text_width(l2, size, "Black", 0.04)) > 1800: size -= 4
    # dark band for readability
    band = skia.Paint(); band.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 430)],
                                                                      [skia.Color4f(0, 0, 0, 0.92).toColor(), skia.Color4f(0, 0, 0, 0).toColor()]))
    c.drawRect(skia.Rect(0, 0, W, 430), band)
    draw_text(c, l1, 960, 125, size, weight="Black", track=0.04)
    draw_text(c, l2, 960, 125 + size * 1.02, size, weight="Black", track=0.04)
    pill(c, "HUMAN MIND", 960, 1020 - 0, size=24, a=0.0)
    img = em.makeImageSnapshot()

    # composite with glow
    out_s = skia.Surface(W, H); oc = out_s.getCanvas()
    oc.clear(skia.Color(5, 5, 5))
    p = skia.Paint(); p.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H * 0.55), 900,
                                                                 [skia.Color(34, 34, 34), skia.Color(5, 5, 5)]))
    oc.drawRect(skia.Rect(0, 0, W, H), p)
    oc.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Blur(40, 40), BlendMode=skia.BlendMode.kPlus, Alpha=170))
    oc.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ImageFilter=skia.ImageFilters.Blur(10, 10), BlendMode=skia.BlendMode.kPlus, Alpha=140))
    oc.drawImage(img, 0, 0)
    vg = skia.Paint(); vg.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1150,
                                                                  [skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0).toColor(), skia.Color4f(0, 0, 0, 0.7).toColor()],
                                                                  [0, 0.6, 1]))
    oc.drawRect(skia.Rect(0, 0, W, H), vg)
    arr = out_s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    Image.fromarray(arr[..., :3]).resize((1280, 720), Image.LANCZOS).save(out, optimize=True)
    Image.fromarray(arr[..., :3]).save(out.replace(".png", "_1080p.png"), optimize=True)
    print("thumb", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
