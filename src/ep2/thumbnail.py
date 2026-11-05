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


def _title(img, tag, part):
    """Общий заголовок + плашка-тег + бейдж «ЧАСТЬ N»."""
    p = Pen(W, H, ss=2)
    p.text(W / 2, 210, L("ЗА МНОЙ", "SOMEONE IS"), FONT_TITLE, L(168, 150), (246, 242, 234), anchor="mm")
    p.text(W / 2, 380, L("КТО-ТО ИДЁТ", "FOLLOWING YOU"), FONT_TITLE, L(140, 112), (246, 242, 234), anchor="mm")
    p.rrect(130, 480, W - 130, 580, 14, (232, 168, 60))
    p.text(W / 2, 530, tag, FONT_TITLE, 46, (16, 14, 12), anchor="mm")
    p.rrect(W / 2 - 150, 615, W / 2 + 150, 700, 14, (190, 30, 24))
    p.text(W / 2, 657, L("ЧАСТЬ ", "PART ") + str(part), FONT_TITLE, 54, (255, 240, 228), anchor="mm")
    t = p.arr()
    g = cv2.GaussianBlur(t, (0, 0), 22)
    g[..., :3] = g[..., 3:4] * np.array([0.55, 0.38, 0.1], np.float32)
    t = t + g * 0.7 * (1 - t[..., 3:4])
    return t[..., :3] + img * (1 - t[..., 3:4])


def _save(img, name):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGB")
    im.save(OUT / name, quality=93)
    return OUT / name


RING = (24, -40, 112, 268)  # смещение и радиусы кольца вокруг фигур (часть 2)


def build_parts():
    """Два превью для серии, разделённой на две части."""
    from .shots import render_frame
    from ..cues import C
    c = C()
    OUT.mkdir(parents=True, exist_ok=True)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    # часть 1 — витрина с отражением (как основное превью)
    sh = ShopWindow(0, 10, zoom=(1.18, 1.18), focus=(0, 0), refl_at=-5)
    img = sh.draw(5.0)
    img += sl_radial(W * 0.72, H * 0.42, 420, power=2, k=0.12)[..., None] * rgb((150, 170, 220))
    img = grade(img, 0.3, warmth=-0.3, desat=0.15, grain=0.04, vignette=1.5, exposure=1.05)
    img = img * (1 - 0.88 * np.clip(1 - yy / 0.40, 0, 1) ** 1.4)
    img = _title(img, L("ОН ПОВТОРЯЕТ КАЖДЫЙ ШАГ", "HE COPIES EVERY STEP"), 1)
    a = Pen(W, H, ss=2)
    a.line([(W * 0.9, H * 0.39), (W * 0.82, H * 0.45)], (232, 168, 60), 12)
    a.poly([(W * 0.8, H * 0.47), (W * 0.795, H * 0.43), (W * 0.84, H * 0.45)], (232, 168, 60))
    al = a.arr()
    img = al[..., :3] + img * (1 - al[..., 3:4])
    p1 = _save(img, "thumbnail_part1_9x16.jpg")
    # часть 2 — фото на телефоне: рядом с тобой кто-то стоит
    fr = render_frame(c["someone"] + 1.6)
    z = 1.6                                  # наезд на фигуры на фото
    cw, chh = int(W / z), int(H / z)
    cx, cy = W // 2, int(H * 0.43)
    x0, y0 = cx - cw // 2, max(0, cy - int(chh * 0.55))
    img = cv2.resize(fr[y0:y0 + chh, x0:x0 + cw], (W, H), interpolation=cv2.INTER_CUBIC)
    img = img * (1 - 0.9 * np.clip(1 - yy / 0.42, 0, 1) ** 1.3)
    img = _title(img, L("КТО СТОИТ РЯДОМ С ТОБОЙ?", "WHO IS STANDING NEXT TO YOU?"), 2)
    fx, fy = (cx - x0) * z, (cy - y0) * z     # центр пары на обложке
    r = Pen(W, H, ss=2)
    ex, ey, rx, ry = fx + RING[0], fy + RING[1], RING[2], RING[3]
    r.d.ellipse([(ex - rx) * r.ss, (ey - ry) * r.ss, (ex + rx) * r.ss, (ey + ry) * r.ss], outline=(225, 40, 30, 255),
                width=12 * r.ss)
    ra = r.arr()
    img = ra[..., :3] + img * (1 - ra[..., 3:4])
    p2 = _save(img, "thumbnail_part2_9x16.jpg")
    return p1, p2
