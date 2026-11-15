"""Cover / thumbnail 1080x1920."""
import sys, math
import skia
from .core import *
from . import env
from .env import FLOOR, hero_c
from .character import Character, HERO, pose
from .film import VOID_LIGHT, grade_filter

double_c = Character(HERO)


def render(lang, path):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    t = 3.0
    c.saveLayer(None, skia.Paint(ColorFilter=grade_filter("cold")))
    c.save()
    Cam(1450, 520, 0.62).apply(c)
    env.street(c, t, lang, x_view=(-1000, 4200))
    env.fog(c, t, FLOOR - 700, FLOOR + 200, "#9cc9ff", 0.2)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint("#020611", 0.45))
    # portal
    px, py = 600, 1180
    glow(c, px, py, 700, "#6fdcff", 0.7)
    for i in range(3):
        r = 1 - i * 0.12
        c.drawOval(skia.Rect.MakeLTRB(px - 170 * r, py - 430 * r, px + 170 * r, py + 430 * r),
                   paint("#bff6ff", 0.9 - i * 0.25, stroke=14 - i * 4, blur=3 + i * 3))
    c.drawOval(skia.Rect.MakeLTRB(px - 145, py - 400, px + 145, py + 400),
               gpaint(rad_grad(px, py, 420, ["#dffbff", "#5fd0ff", "#0a2a44"], [0, 0.35, 1])))
    from .env import particles
    particles(c, 2.0, px, py, 70, 520, "#bff3ff", 0.9, swirl=2, size=6)
    # the double, standing at the portal, facing us
    double_c.draw(c, 760, 1640, 0.92, pose(tr=-0.2, t=1, expr="smug", eye_glint=0.8, look=(-0.6, 0.1)),
                  light=dict(VOID_LIGHT, dir=-1, key=("#bff3ff", 0.5), shadow=("#000308", 0.35)))
    # the hero, foreground left, turning back towards us in fear
    hero_c.draw(c, 250, 2380, 1.75, pose(tr=0.55, t=1, expr="terrified", look=(-0.9, 0)),
                light=dict(VOID_LIGHT, dir=1, key=("#bff3ff", 0.45), shadow=("#000308", 0.4)))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), gpaint(rad_grad(W / 2, H * 0.5, H * 0.75,
                                                          [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 170)], [0, 0.55, 1])))
    # title
    if lang == "ru":
        lines = [("ТЫ ПОПАЛ", "#ffffff"), ("В ДРУГУЮ", "#ffffff"), ("ВСЕЛЕННУЮ?", "#5fe9ff")]
    else:
        lines = [("ANOTHER", "#ffffff"), ("UNIVERSE?", "#5fe9ff")]
    y = 250
    for txt, cc in lines:
        size = min(170, 170 * 1000 / font(170, "Black").measureText(txt))
        c.save()
        c.translate(W / 2, y)
        c.rotate(-3)
        text_center(c, txt, 0, 0, size, cc, "Black", stroke=26, stroke_color="#03060d", shadow=18)
        c.restore()
        y += size * 1.02
    s.makeImageSnapshot().save(path)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
