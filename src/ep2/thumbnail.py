"""Превью 9:16 (1080x1920): герой у витрины, в стекле — отражение высокого мужчины."""
import numpy as np
import cv2
from PIL import Image
from ..config import W, H, OUT, FONT_TITLE, FONT_BOLD, L
from ..gfx import grade, Pen, sl_radial, rgb
from .shots import ShopWindow


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    sh = ShopWindow(0, 10, zoom=(1.18, 1.18), focus=(0, 0), refl_at=-5)
    img = sh.draw(5.0)
    img += sl_radial(W * 0.72, H * 0.42, 420, power=2, k=0.12)[..., None] * rgb((150, 170, 220))
    img = grade(img, 0.3, warmth=-0.3, desat=0.15, grain=0.04, vignette=1.5, exposure=1.05)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = img * (1 - 0.85 * np.clip(1 - yy / 0.36, 0, 1) ** 1.4)
    p = Pen(W, H, ss=2)
    p.text(W / 2, 210, L("ЗА МНОЙ", "SOMEONE IS"), FONT_TITLE, L(168, 150), (246, 242, 234), anchor="mm")
    p.text(W / 2, 380, L("КТО-ТО ИДЁТ", "FOLLOWING YOU"), FONT_TITLE, L(140, 112), (246, 242, 234), anchor="mm")
    p.rrect(150, 480, W - 150, 580, 14, (232, 168, 60))
    p.text(W / 2, 530, L("ОН ПОВТОРЯЕТ КАЖДЫЙ ШАГ", "HE COPIES EVERY STEP"), FONT_TITLE, 46, (16, 14, 12), anchor="mm")
    t = p.arr()
    g = cv2.GaussianBlur(t, (0, 0), 22)
    g[..., :3] = g[..., 3:4] * np.array([0.55, 0.38, 0.1], np.float32)
    t = t + g * 0.7 * (1 - t[..., 3:4])
    img = t[..., :3] + img * (1 - t[..., 3:4])
    # стрелка на отражение
    a = Pen(W, H, ss=2)
    a.line([(W * 0.9, H * 0.36), (W * 0.82, H * 0.44)], (232, 168, 60), 12)
    a.poly([(W * 0.8, H * 0.465), (W * 0.795, H * 0.425), (W * 0.84, H * 0.445)], (232, 168, 60))
    al = a.arr()
    img = al[..., :3] + img * (1 - al[..., 3:4])
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    im.save(OUT / "thumbnail_9x16.png")
    im.convert("RGB").save(OUT / "thumbnail_9x16.jpg", quality=93)
    return OUT / "thumbnail_9x16.jpg"


if __name__ == "__main__":
    print(build())
