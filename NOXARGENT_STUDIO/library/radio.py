"""Старая радиостанция (локация с фотографии из будущего, серия 2+).

Бетонное здание с мачтой, дверь с табличкой (частично закрыта), тёмное окно второго этажа.
"""
import cv2
import numpy as np

from characters import amina_back, arman_back, arman_front_silhouette
from core import AA, H, W, blob, gradient, poly, to_lmap, u8

DOOR = (840, 560, 1060, 900)
SIGN = (870, 470, 1030, 530)
WINDOW = (1260, 300, 1420, 450)   # тёмное окно, где стоит третий


def radio_station(third=0.0, highlight_amina=0.0):
    """Кадр-фотография у радиостанции. third: 0..1 — насколько заметен силуэт в окне."""
    rng = np.random.default_rng(23)
    img = gradient(H, W, (30, 18, 12), (52, 34, 24))
    # мачта с растяжками
    cv2.line(img, (1640, 40), (1640, 520), (22, 18, 16), 8)
    for y in range(80, 520, 60):
        cv2.line(img, (1610, y), (1670, y + 40), (22, 18, 16), 3)
        cv2.line(img, (1670, y), (1610, y + 40), (22, 18, 16), 3)
    cv2.line(img, (1640, 60), (1360, 520), (18, 16, 14), 2, AA)
    cv2.line(img, (1640, 60), (1900, 520), (18, 16, 14), 2, AA)
    cv2.circle(img, (1640, 40), 6, (40, 40, 200), -1, AA)
    # здание
    cv2.rectangle(img, (300, 260), (1560, 900), (40, 38, 38), -1)
    cv2.rectangle(img, (280, 240), (1580, 270), (28, 26, 26), -1)
    for _ in range(40):  # пятна и трещины бетона
        x, y = int(rng.integers(320, 1540)), int(rng.integers(280, 880))
        cv2.circle(img, (x, y), int(rng.integers(6, 30)), (34, 32, 32), -1, AA)
    for wx in (420, 620, 1260):
        cv2.rectangle(img, (wx, 300), (wx + 160, 450), (14, 14, 16), -1)
        cv2.line(img, (wx + 80, 300), (wx + 80, 450), (30, 28, 28), 4)
    x0, y0, x1, y1 = DOOR
    cv2.rectangle(img, (x0 - 14, y0 - 14), (x1 + 14, y1), (24, 22, 22), -1)
    cv2.rectangle(img, (x0, y0), (x1, y1), (36, 44, 46), -1)
    cv2.line(img, ((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1), (26, 30, 32), 3)
    # табличка: текст не читается — закрыта ржавчиной и полосой скотча
    sx0, sy0, sx1, sy1 = SIGN
    cv2.rectangle(img, (sx0, sy0), (sx1, sy1), (150, 150, 140), -1)
    for i in range(6):
        cv2.rectangle(img, (sx0 + 12 + i * 24, sy0 + 18), (sx0 + 26 + i * 24, sy0 + 40), (70, 70, 66), -1)
    poly(img, [(sx0 - 10, sy0 + 34), (sx1 + 10, sy0 + 4), (sx1 + 14, sy0 + 30), (sx0 - 6, sy1 + 6)], (60, 92, 110))
    img[900:] = gradient(H - 900, W, (30, 30, 34), (18, 18, 20))
    # окно с третьим силуэтом
    wx0, wy0, wx1, wy1 = WINDOW
    if third > 0:
        win = img[wy0:wy1, wx0:wx1].copy()
        fig = win.copy()
        arman_front_silhouette(fig, (wx1 - wx0) / 2, (wy1 - wy0) + 30, 150, col=(4, 4, 5))
        img[wy0:wy1, wx0:wx1] = cv2.addWeighted(win, 1 - third, fig, third, 0)
    # фонарь над дверью — единственный свет
    lm = np.full((H, W, 3), 0.55, np.float32) + blob(H, W, 950, 520, 520, 420, (0.9, 1.0, 1.1))
    img = cv2.multiply(img, to_lmap(lm), scale=1 / 128)
    img = cv2.add(img, u8(blob(H, W, 950, 520, 40, 30, (110, 160, 190))))
    # двое со спины
    arman_back(img, 870, 1060, 560, arms_forward=False)
    amina_back(img, 1080, 1060, 560)
    if highlight_amina > 0:
        m = np.zeros((H, W), np.uint8)
        amina_back(cv2.merge([m, m, m]), 1080, 1060, 560)
        mm = np.zeros((H, W, 3), np.uint8)
        amina_back(mm, 1080, 1060, 560, cfg=dict(coat=(255, 255, 255), hair=(255, 255, 255), legs=(255, 255, 255), height=0.93))
        edge = cv2.morphologyEx(mm[..., 0], cv2.MORPH_GRADIENT, np.ones((5, 5), np.uint8))
        img[edge > 0] = (img[edge > 0] * (1 - highlight_amina) + np.array((210, 225, 235)) * highlight_amina).astype(np.uint8)
    return img


def date_stamp(img, text="ЗАВТРА · 23:41"):
    """Штамп даты камеры в правом нижнем углу (как на плёночном фото)."""
    from PIL import Image
    from core import draw_text
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw_text(im, (W - 540, H - 230), text, 62, (255, 150, 60), "bold")  # отступ от краёв: не режется зумом
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
