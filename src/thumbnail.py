"""Превью (обложка) 16:9: out/thumbnail.png (1920x1080) и out/thumbnail_1280.jpg."""
import numpy as np
from PIL import Image
from .config import W, H, OUT, FONT_TITLE, FONT_BOLD
from .gfx import Cam, compose, grade, sl_radial, rgb, to_u8, text_layer, Layer, Particles, Pen
from . import sets as S
from .shots import timur_back_spr, sprite, WindowShot


def build():
    OUT.mkdir(exist_ok=True)
    city = S.city_set("hook")
    room = S.room_window_set("after")
    cam = Cam(1.22, (S.WIN_RECT[0] + S.WIN_RECT[2]) / 2 - S.LW / 2 - 60, -60)
    img = compose([(city["sky"], 1, 1.0), (city["glow"], 1.2), city["b0"], (city["w0"], 1.0), city["b1"],
                   (city["w1"], 0.9), city["b2"], (city["w2"], 1.0)], cam)
    sx, sy = WindowShot._to_screen((1500, 790), cam, 0.25)
    img += sl_radial(sx, sy, 900, power=2.2, k=0.9)[..., None] * rgb((255, 200, 140))
    img += sl_radial(sx, sy, 150, power=1.3, k=2.0)[..., None] * rgb((255, 250, 240))
    spr = timur_back_spr(720, 3, 0, -7, 16)
    tl = sprite(spr[0], spr[1], spr[2], 1430, 1240, 1.0)
    img = compose([(room["room"], 1, 1.4), (room["spill"], 1.5), (room["shelf"], 1, 1.2), (tl, 1, 0.8),
                   (room["curtain"], 1, 1.2)], cam, base=img)
    img = Particles(160, seed=4, color=(255, 160, 90), size=(1, 3), k=0.6).draw(img, 3.0)
    img = grade(img, 0.37, warmth=0.6, desat=0.1, grain=0.04, red_shadow=1.0, vignette=1.3, exposure=1.0)
    # тёмная плашка слева под текст
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = np.clip(1 - xx / (W * 0.62), 0, 1)[..., None] ** 1.3 * 0.82
    img = img * (1 - shade)
    t1 = text_layer([("А ЧТО,", 90, 250), ("ЕСЛИ…", 90, 420)], FONT_TITLE, 190, color=(246, 240, 230), anchor="ls",
                    glow=20, glow_color=(160, 20, 10))
    img = t1[..., :3] + img * (1 - t1[..., 3:4])
    p = Pen(W, H, ss=2)
    p.rrect(84, 500, 990, 690, 14, (196, 30, 22))
    p.text(120, 557, "УПАДЁТ", FONT_TITLE, 74, (255, 240, 228), anchor="lm")
    p.text(120, 637, "АТОМНАЯ БОМБА?", FONT_TITLE, 74, (255, 240, 228), anchor="lm")
    p.rrect(90, 760, 330, 830, 10, (20, 16, 16, 230))
    p.text(210, 795, "СЕРИЯ №1", FONT_BOLD, 36, (232, 120, 70), anchor="mm")
    b = p.arr()
    img = b[..., :3] + img * (1 - b[..., 3:4])
    im = Image.fromarray(to_u8(img))
    im.save(OUT / "thumbnail.png")
    im.resize((1280, 720), Image.LANCZOS).save(OUT / "thumbnail_1280.jpg", quality=92)
    return OUT / "thumbnail.png"


if __name__ == "__main__":
    print(build())
