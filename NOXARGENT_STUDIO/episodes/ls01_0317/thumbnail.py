"""Превью серии 1 «03:17»: горизонтальное 16:9 (YouTube) и вертикальное 9:16 (TikTok/Shorts).

Запуск: python thumbnail.py → Рабочий стол/ПРЕВЬЮ_1.jpg, ПРЕВЬЮ_1_вертикальное.jpg
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
from characters import arman_back, hands_holding  # noqa: E402
from clock import seven_seg  # noqa: E402
from core import (H, W, Post, apply_light, blob, camera, desktop, digital_glitch, draw_text, paste_rgba,  # noqa: E402
                  pil_to_bgra, to_lmap, u8, warp_rgba)

MSG = "НЕ ОТКРЫВАЙ ДВЕРЬ. Я УЖЕ ВНУТРИ."


def door_scene():
    """Прихожая: дверь приоткрыта (чёрная щель), Арман со спины светит фонариком."""
    img = AP.hallway_base()
    d = AP.DOOR
    cv2.rectangle(img, (d["x0"], d["y0"]), (d["x1"], d["y1"]), (30, 28, 28), -1)
    AP.door_panel(img, 0.55)
    img = apply_light(img, to_lmap(AP.hallway_lmap(flash=(1000, 520, 300))))
    # холодный контровой свет из щели — единственный «чужой» свет в кадре
    img = cv2.add(img, u8(blob(H, W, 1120, 560, 70, 300, (60, 40, 20))))
    arman_back(img, 960, 1180, 860, arms_forward=True)
    return img


def text_layer(size, items):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    for (x, y, txt, sz, col, wt, mw, al) in items:
        draw_text(im, (x, y), txt, sz, col, wt, max_w=mw, align=al)
    return pil_to_bgra(im)


def phone_with_msg(scale):
    spr = PH.phone_sprite(PH.to_bgr(PH.screen_message("Неизвестный номер", MSG)))
    return warp_rgba(spr, scale, 8)


def red_badge(img, x, y, r):
    cv2.circle(img, (x, y), r, (52, 58, 226), -1, cv2.LINE_AA)
    cv2.putText(img, "1", (x - int(r * 0.35), y + int(r * 0.4)), cv2.FONT_HERSHEY_DUPLEX, r / 22, (255, 255, 255), 3, cv2.LINE_AA)


def finish(img, seed=3, glitch=0.25):
    img = digital_glitch(img, glitch, seed)
    return Post(seed=seed, grain=5.0)(img, 0)


def horizontal():
    scene = door_scene()
    img = camera(scene, 1.08, 820, 560)  # дверь и Арман левее, справа место под телефон
    img = digital_glitch(img, 0.25, 3)
    img = Post(seed=3, grain=5.0)(img, 0)  # зерно и виньетка — только на фоне, надписи остаются яркими
    img = cv2.convertScaleAbs(img, alpha=1.25)
    # затемнение справа под текст
    grad = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    img = (img * (1 - 0.55 * np.clip((grad - 0.45) / 0.3, 0, 1))).astype(np.uint8)
    ph = phone_with_msg(0.5)
    img = cv2.add(img, u8(blob(H, W, 1520, 600, 380, 420, (40, 40, 48))))
    paste_rgba(img, ph, 1530 - ph.shape[1] / 2, 590 - ph.shape[0] / 2)
    red_badge(img, 1700, 250, 34)
    # часы 03:17 — семисегментные, как на тумбочке
    seven_seg(img, "03:17", 70, 70, 150, col=(235, 225, 185), off_col=(0, 0, 0))
    glow = np.zeros_like(img)
    seven_seg(glow, "03:17", 70, 70, 150, col=(120, 110, 80), off_col=(0, 0, 0))
    img = cv2.add(img, cv2.GaussianBlur(glow, (0, 0), 14))
    tl = text_layer((W, H), [
        (70, 830, "ПОСЛЕДНИЙ СИГНАЛ", 104, (255, 255, 255, 255), "bold", None, "left"),
        (76, 960, "СЕРИЯ 1", 46, (230, 60, 52, 255), "bold", None, "left"),
        (310, 966, "ОН ЗНАЕТ МОЁ ИМЯ", 40, (210, 210, 215, 255), "semibold", None, "left"),
    ])
    shadow = cv2.GaussianBlur(tl, (0, 0), 8)
    shadow[..., :3] = 0
    paste_rgba(img, shadow, 4, 6, 0.9)
    paste_rgba(img, tl, 0, 0)
    return img


def vertical():
    VW, VH = 1080, 1920
    scene = door_scene()
    crop = camera(scene, 1.0, 1060, 560, out=(int(H * 9 / 16) // 2 * 2, H))
    img = cv2.resize(crop, (VW, VH), interpolation=cv2.INTER_CUBIC)
    img = digital_glitch_v(img)
    img = cv2.convertScaleAbs(img, alpha=1.25)
    ph = phone_with_msg(0.42)
    px, py = VW * 0.76, VH * 0.52
    paste_rgba(img, ph, px - ph.shape[1] / 2, py - ph.shape[0] / 2)
    red_badge(img, int(px + ph.shape[1] * 0.36), int(py - ph.shape[0] * 0.46), 30)
    top = np.linspace(1, 0, 520, dtype=np.float32)[:, None, None]
    img[:520] = (img[:520] * (1 - 0.75 * top)).astype(np.uint8)
    bot = np.linspace(0, 1, 620, dtype=np.float32)[:, None, None]
    img[VH - 620:] = (img[VH - 620:] * (1 - 0.8 * bot)).astype(np.uint8)
    seven_seg(img, "03:17", 250, 110, 170, col=(235, 225, 185), off_col=(0, 0, 0))
    glow = np.zeros_like(img)
    seven_seg(glow, "03:17", 250, 110, 170, col=(120, 110, 80), off_col=(0, 0, 0))
    img = cv2.add(img, cv2.GaussianBlur(glow, (0, 0), 14))
    tl = text_layer((VW, VH), [
        (0, 1500, "ПОСЛЕДНИЙ", 118, (255, 255, 255, 255), "bold", VW, "center"),
        (0, 1630, "СИГНАЛ", 118, (255, 255, 255, 255), "bold", VW, "center"),
        (0, 1790, "СЕРИЯ 1 · ОН ЗНАЕТ МОЁ ИМЯ", 40, (230, 60, 52, 255), "bold", VW, "center"),
    ])
    shadow = cv2.GaussianBlur(tl, (0, 0), 8)
    shadow[..., :3] = 0
    paste_rgba(img, shadow, 4, 6, 0.9)
    paste_rgba(img, tl, 0, 0)
    g = cv2.resize(np.random.default_rng(5).normal(0, 5, (960, 540)).astype(np.float32), (VW, VH))
    return np.clip(img.astype(np.float32) + g[..., None], 0, 255).astype(np.uint8)


def digital_glitch_v(img):
    rng = np.random.default_rng(11)
    out = img.copy()
    for _ in range(6):
        y = int(rng.integers(300, 1400))
        h = int(rng.integers(4, 14))
        out[y:y + h] = np.roll(out[y:y + h], int(rng.normal(0, 30)), axis=1)
    return out


def main():
    out = desktop()
    h = horizontal()
    cv2.imwrite(str(out / "ПРЕВЬЮ_1.jpg"), h, [cv2.IMWRITE_JPEG_QUALITY, 93])
    cv2.imwrite(str(out / "ПРЕВЬЮ_1_1280x720.jpg"), cv2.resize(h, (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    cv2.imwrite(str(out / "ПРЕВЬЮ_1_вертикальное.jpg"), vertical(), [cv2.IMWRITE_JPEG_QUALITY, 93])
    print("Готово:", out)


if __name__ == "__main__":
    main()
