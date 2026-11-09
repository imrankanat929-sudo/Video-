"""4:3 thumbnail (1440x1080) for episode 1.  python3 thumbnail.py -> out/ep1_thumb_{ru,en}.png"""
import os
import cairo
from mir.gfx import *  # noqa
from mir import ep1, hero
from mir import world as wd

TW, TH = 1440, 1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

TXT = {
    "ru": dict(t1="МИР", t2="ОСТАНОВИЛСЯ", st="НЕ ВОЗВРАЩАЙСЯ ДОМОЙ", ep="СЕРИЯ 1"),
    "en": dict(t1="THE WORLD", t2="STOPPED", st="DO NOT GO HOME", ep="EPISODE 1"),
}


def background():
    """Frozen street from the video, rendered at 9:16 then cropped to 4:3."""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    ep1.shot_street(c, 3.0, 3.0, ep1.TEXT["ru"])
    return s


def make(lang):
    L = TXT[lang]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, TW, TH)
    ctx = cairo.Context(surf)
    bg = background()
    k = TW / W  # 1.333
    ctx.save()
    ctx.scale(k, k)
    ctx.set_source_surface(bg, 0, -560)
    ctx.paint()
    ctx.restore()
    # darken left for the title, glow behind the hero
    g = cairo.LinearGradient(0, 0, TW, 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.65)
    g.add_color_stop_rgba(0.6, 0, 0, 0, 0.15)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.0)
    ctx.rectangle(0, 0, TW, TH)
    ctx.set_source(g)
    ctx.fill()
    glow(ctx, 1110, 760, 520, "#9fd3ff", 0.35)

    # frozen keys + clock as small hints
    wd.keys(ctx, 690, 560, 46)
    ctx.arc(690, 560, 72, 0, 6.3)
    ctx.set_line_width(7)
    setc(ctx, "#e3262f")
    ctx.stroke()

    # big scared hero, bottom-right
    hero.bust(ctx, 1150, 730, 215, "scared", look=(-0.6, -0.2), rim="#9fd3ff", t=0.4)

    # title
    text(ctx, L["ep"], 60, 120, 46, "#c9d2e6", FONT_BOLD, align="left", outline=4)
    text(ctx, L["t1"], 56, 270, 150, "#ffffff", align="left", outline=11, fit=820)
    text(ctx, L["t2"], 56, 420, 132, "#ffd23f", align="left", outline=11, fit=820)
    time_chip(ctx, "09:17", 230, 560, 64)
    sticker(ctx, L["st"], 450, 880, 58, angle=-5)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"ep1_thumb_{lang}.png")
    surf.write_to_png(p)
    return p


if __name__ == "__main__":
    for lang in ("ru", "en"):
        print(make(lang))
