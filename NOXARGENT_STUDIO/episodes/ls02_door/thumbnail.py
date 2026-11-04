"""Превью серии 2 «За дверью»: 16:9 (YouTube) и 9:16 (TikTok/Shorts).

Треснутый чужой телефон с фото у радиостанции (третий силуэт в окне) и красной подписью.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "library"))

import apartment as AP  # noqa: E402
import phone as PH  # noqa: E402
import radio as RD  # noqa: E402
from characters import hands_holding  # noqa: E402
from core import H, W, Post, apply_light, blob, camera, desktop, digital_glitch, draw_text, paste_rgba, pil_to_bgra, to_lmap, u8, warp_rgba  # noqa: E402

CAPTION = "ОДИН ИЗ ВАС НЕ ДОЖИВЁТ ДО УТРА"


def photo():
    return RD.date_stamp(RD.radio_station(1.0, 0.0), "ЗАВТРА · 23:41")


def phone_spr():
    scr = PH.screen_chat("Неизвестный номер", [("photo", photo(), CAPTION)])
    return PH.add_cracks(PH.phone_sprite(PH.to_bgr(scr)))


def background():
    img = AP.hallway_base()
    d = AP.DOOR
    cv2.rectangle(img, (d["x0"], d["y0"]), (d["x1"], d["y1"]), (30, 28, 28), -1)
    AP.door_panel(img, 0.38, gap_col=(70, 84, 84))
    img = apply_light(img, to_lmap(AP.hallway_lmap(flash=(960, 520, 260))))
    return img


def texts(size, items):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    for (x, y, txt, sz, col, wt, mw, al) in items:
        draw_text(im, (x, y), txt, sz, col, wt, max_w=mw, align=al)
    t = pil_to_bgra(im)
    sh = cv2.GaussianBlur(t, (0, 0), 8)
    sh[..., :3] = 0
    return t, sh


def horizontal():
    img = camera(background(), 1.05, 700, 540)
    img = digital_glitch(img, 0.25, 4)
    img = Post(seed=4, grain=5.0)(img, 0)
    # крупно: фото из будущего на весь правый край
    ph = photo()
    card = cv2.resize(ph, (1000, 562))
    x0, y0 = 860, 70
    img[y0:y0 + 562, x0:x0 + 1000] = card
    cv2.rectangle(img, (x0, y0), (x0 + 1000, y0 + 562), (230, 230, 230), 6)
    # круг-выделение третьего силуэта в окне
    wx0, wy0, wx1, wy1 = RD.WINDOW
    cx = x0 + (wx0 + wx1) / 2 * 1000 / W
    cy = y0 + (wy0 + wy1) / 2 * 562 / H
    cv2.circle(img, (int(cx), int(cy)), 70, (52, 58, 226), 6, cv2.LINE_AA)
    # телефон с трещинами слева внизу
    spr = warp_rgba(phone_spr(), 0.36, 10)
    paste_rgba(img, spr, 150, 70)
    bot = np.linspace(0, 1, 380, dtype=np.float32)[:, None, None]
    img[H - 380:] = (img[H - 380:] * (1 - 0.75 * bot)).astype(np.uint8)
    t, sh = texts((W, H), [
        (860, 655, CAPTION, 46, (235, 52, 46, 255), "bold", 1000, "center"),
        (70, 800, "ФОТО ИЗ ЗАВТРА", 132, (255, 255, 255, 255), "bold", None, "left"),
        (76, 960, "ПОСЛЕДНИЙ СИГНАЛ · СЕРИЯ 2", 46, (215, 215, 220, 255), "bold", None, "left"),
    ])
    paste_rgba(img, sh, 4, 6, 0.9)
    paste_rgba(img, t, 0, 0)
    return img


def vertical():
    VW, VH = 1080, 1920
    crop = camera(background(), 1.0, 1000, 560, out=(606, H))
    img = cv2.resize(crop, (VW, VH), interpolation=cv2.INTER_CUBIC)
    img = digital_glitch(cv2.resize(img, (W, H)), 0.2, 6)
    img = cv2.resize(img, (VW, VH))
    img = cv2.convertScaleAbs(img, alpha=0.8)
    card = cv2.resize(photo(), (1000, 562))
    img[230:230 + 562, 40:1040] = card
    cv2.rectangle(img, (40, 230), (1040, 792), (230, 230, 230), 6)
    wx0, wy0, wx1, wy1 = RD.WINDOW
    cv2.circle(img, (int(40 + (wx0 + wx1) / 2 * 1000 / W), int(230 + (wy0 + wy1) / 2 * 562 / H)), 64, (52, 58, 226), 6, cv2.LINE_AA)
    spr = warp_rgba(phone_spr(), 0.42, -8)
    paste_rgba(img, spr, VW - spr.shape[1] - 30, 840)
    g = cv2.resize(np.random.default_rng(5).normal(0, 5, (960, 540)).astype(np.float32), (VW, VH))
    img = np.clip(img.astype(np.float32) + g[..., None], 0, 255).astype(np.uint8)
    t, sh = texts((VW, VH), [
        (40, 110, CAPTION, 46, (235, 52, 46, 255), "bold", 1000, "center"),
        (0, 1490, "ФОТО", 128, (255, 255, 255, 255), "bold", VW, "center"),
        (0, 1625, "ИЗ ЗАВТРА", 128, (255, 255, 255, 255), "bold", VW, "center"),
        (0, 1795, "ПОСЛЕДНИЙ СИГНАЛ · СЕРИЯ 2", 42, (215, 215, 220, 255), "bold", VW, "center"),
    ])
    bot = np.linspace(0, 1, 560, dtype=np.float32)[:, None, None]
    img[VH - 560:] = (img[VH - 560:] * (1 - 0.8 * bot)).astype(np.uint8)
    paste_rgba(img, sh, 4, 6, 0.9)
    paste_rgba(img, t, 0, 0)
    return img


def main():
    out = desktop()
    h = horizontal()
    cv2.imwrite(str(out / "ПРЕВЬЮ_2.jpg"), h, [cv2.IMWRITE_JPEG_QUALITY, 93])
    cv2.imwrite(str(out / "ПРЕВЬЮ_2_1280x720.jpg"), cv2.resize(h, (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    cv2.imwrite(str(out / "ПРЕВЬЮ_2_вертикальное.jpg"), vertical(), [cv2.IMWRITE_JPEG_QUALITY, 93])
    print("Готово")


if __name__ == "__main__":
    main()
