"""9:16 thumbnails (cover images) for RU and EN. usage: python thumb.py OUTDIR"""
import os
import sys

from PIL import Image, ImageDraw, ImageChops

sys.path.insert(0, os.path.dirname(__file__))
from lib import *  # noqa
from scenes import trail_sprite, plume_sprite, RED, YEL  # noqa

TXT = {
    "ru": dict(top="ДО УДАРА", big="7 ДНЕЙ", q1="ЧТО БЫ ТЫ", q2="СДЕЛАЛ?", timer="06:23:59:59"),
    "en": dict(top="IMPACT IN", big="7 DAYS", q1="WHAT WOULD", q2="YOU DO?", timer="06:23:59:59"),
}


def base():
    img = to_img(vgrad(W, H, [(0, "#05030a"), (0.35, "#2a0a12"), (0.62, "#a03418"), (0.7, "#ff8a3a"), (0.76, "#3a0e0a"), (1, "#080203")])).convert("RGBA")
    st = starfield(W, H, 44, n=900, nebula=False)
    img = Image.blend(img.convert("RGB"), ImageChops.screen(img.convert("RGB"), st), 0.6).convert("RGBA")
    ax, ay = 590, 900
    paste(img, glow_sprite(1500, (255, 120, 40), 1.6), ax, ay, alpha=0.9)
    paste(img, trail_sprite(), ax + 0.53 * 600 * 2.2, ay - 0.85 * 600 * 2.2, scale=2.2)
    paste(img, trail_sprite(), ax + 0.53 * 600 * 1.6, ay - 0.85 * 600 * 1.6, scale=1.6)
    paste(img, glow_sprite(900, (255, 200, 120), 1.5), ax, ay, alpha=0.8)
    paste(img, asteroid(1200, 3, (-0.6, 0.6, 0.5)), ax, ay, scale=0.6, rot=20)
    # fiery leading edge (additive)
    hot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste(hot, glow_sprite(1100, (255, 100, 25), 1.2), ax - 140, ay + 150)
    paste(hot, glow_sprite(600, (255, 200, 120), 1.5), ax - 190, ay + 210)
    img = add_glow(img.convert("RGB"), hot, 0.9).convert("RGBA")
    paste(img, skyline(W + 300, 700, 70, "#0a0304", True, "#ff9a5a", 0.12), W / 2, 1560)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1900, W, H], fill=(5, 2, 2))
    for x, h, a in ((180, 260, "point"), (300, 230, None), (860, 250, "up")):
        person(d, x, 1905, h, (5, 2, 2), arm=a)
    out = img.convert("RGB")
    out = bloom(out, 0.6, 20, 0.5)
    out = ImageChops.multiply(out, vignette(0.6))
    return out


def make(lang, path):
    T = TXT[lang]
    out = base()
    out = to_img(to_arr(out) * (1 - 0.55 * np.clip(1 - np.abs(np.arange(H) - 330)[:, None, None] / 330, 0, 1)))
    paste(out, text_layer(T["top"], 110, (255, 255, 255, 255), stroke=9), W / 2, 150)
    paste(out, text_layer(T["big"], 300, YEL + (255,), stroke=16, sfill=(0, 0, 0, 255), glow=(255, 60, 0)), W / 2, 380, rot=-3)
    # timer badge
    tb = text_layer(T["timer"], 80, (255, 255, 255, 255), stroke=0, weight=800)
    bw, bh = tb.width - 20, 120
    badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(badge).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=24, fill=RED + (240,))
    paste(out, badge, W / 2, 600)
    paste(out, tb, W / 2, 600)
    out = to_img(to_arr(out) * (1 - 0.5 * np.clip(1 - np.abs(np.arange(H) - 1430)[:, None, None] / 260, 0, 1)))
    paste(out, text_layer(T["q1"], 130, (255, 255, 255, 255), stroke=10), W / 2, 1360)
    paste(out, text_layer(T["q2"], 150, (255, 255, 255, 255), stroke=10), W / 2, 1510)
    out.save(path, quality=95)


if __name__ == "__main__":
    od = sys.argv[1]
    os.makedirs(od, exist_ok=True)
    for lang in ("ru", "en"):
        make(lang, os.path.join(od, f"preview_{lang}.jpg"))
