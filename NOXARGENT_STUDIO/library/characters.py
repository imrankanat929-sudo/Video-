"""Герои сериала «Последний сигнал». Внешность — только здесь, одна на все серии.

Люди рисуются силуэтами в полумраке: без лиц крупным планом.
"""
import math

import cv2
import numpy as np

from core import AA, poly

# ---------- конфиг внешности ----------
ARMAN = {
    "name": "Арман",
    "hoodie": (20, 19, 21),       # чёрная толстовка
    "hoodie_edge": (44, 40, 40),  # контровой свет по краю
    "pants": (30, 28, 30),        # тёмные брюки
    "hair": (14, 14, 15),         # короткие тёмные волосы
    "skin_shadow": (20, 21, 26),  # кожа в полумраке (руки)
    "height": 1.0,                # относительный рост
}


def _rim(img, pts, col, w):
    cv2.polylines(img, [np.int32(pts)], False, col, w, AA)


def arman_back(img, x, yf, h, arms_forward=True, hood_up=False, rim=True, cfg=ARMAN):
    """Арман со спины, стоя. yf — уровень ступней, h — рост в пикселях."""
    x, yf, h = float(x), float(yf), float(h) * cfg["height"]
    hd = cfg["hoodie"]
    sh_y = yf - h * 0.81
    hip_y = yf - h * 0.47
    # ноги
    for s in (-1, 1):
        poly(img, [(x + s * h * 0.015, hip_y), (x + s * h * 0.105, hip_y), (x + s * h * 0.085, yf), (x + s * h * 0.03, yf)], cfg["pants"])
    # корпус толстовки (свободный крой)
    body = [(x - h * 0.16, sh_y + h * 0.05), (x - h * 0.11, sh_y), (x + h * 0.11, sh_y), (x + h * 0.16, sh_y + h * 0.05),
            (x + h * 0.125, hip_y + h * 0.07), (x - h * 0.125, hip_y + h * 0.07)]
    poly(img, body, hd)
    for s in (-1, 1):
        cv2.circle(img, (int(x + s * h * 0.125), int(sh_y + h * 0.045)), int(h * 0.045), hd, -1, AA)
    # руки: при поднятом телефоне локти видны чуть в стороны
    for s in (-1, 1):
        if arms_forward:
            poly(img, [(x + s * h * 0.13, sh_y + h * 0.04), (x + s * h * 0.19, sh_y + h * 0.10), (x + s * h * 0.16, sh_y + h * 0.27), (x + s * h * 0.10, sh_y + h * 0.25)], hd)
        else:
            poly(img, [(x + s * h * 0.13, sh_y + h * 0.04), (x + s * h * 0.185, sh_y + h * 0.08), (x + s * h * 0.17, hip_y + h * 0.04), (x + s * h * 0.12, hip_y + h * 0.04)], hd)
    # голова / капюшон
    hy = yf - h * 0.92
    if hood_up:
        cv2.ellipse(img, (int(x), int(hy)), (int(h * 0.075), int(h * 0.088)), 0, 0, 360, hd, -1, AA)
    else:
        cv2.ellipse(img, (int(x), int(sh_y + h * 0.015)), (int(h * 0.085), int(h * 0.03)), 0, 0, 360, tuple(c + 4 for c in hd), -1, AA)  # капюшон на спине
        cv2.rectangle(img, (int(x - h * 0.03), int(hy + h * 0.03)), (int(x + h * 0.03), int(sh_y + h * 0.01)), cfg["hair"], -1)
        cv2.ellipse(img, (int(x), int(hy)), (int(h * 0.062), int(h * 0.074)), 0, 0, 360, cfg["hair"], -1, AA)
    if rim:
        e = cfg["hoodie_edge"]
        _rim(img, [(x - h * 0.15, sh_y + h * 0.05), (x - h * 0.135, hip_y + h * 0.05)], e, max(1, int(h * 0.006)))
        _rim(img, [(x + h * 0.15, sh_y + h * 0.05), (x + h * 0.135, hip_y + h * 0.05)], e, max(1, int(h * 0.006)))


def arman_front_silhouette(img, x, yf, h, col=None, cfg=ARMAN):
    """Неподвижная фигура анфас (силуэт в окне): капюшон на голове, руки по бокам. Без лица."""
    x, yf, h = float(x), float(yf), float(h)
    hd = col or cfg["hoodie"]
    sh_y = yf - h * 0.81
    hip_y = yf - h * 0.47
    for s in (-1, 1):
        poly(img, [(x + s * h * 0.015, hip_y), (x + s * h * 0.10, hip_y), (x + s * h * 0.085, yf), (x + s * h * 0.03, yf)], hd)
    poly(img, [(x - h * 0.15, sh_y + h * 0.03), (x + h * 0.15, sh_y + h * 0.03), (x + h * 0.135, hip_y + h * 0.06), (x - h * 0.135, hip_y + h * 0.06)], hd)
    cv2.ellipse(img, (int(x), int(sh_y + h * 0.04)), (int(h * 0.15), int(h * 0.045)), 0, 180, 360, hd, -1, AA)
    for s in (-1, 1):  # руки неподвижно по бокам
        poly(img, [(x + s * h * 0.14, sh_y + h * 0.05), (x + s * h * 0.185, sh_y + h * 0.08), (x + s * h * 0.175, hip_y + h * 0.07), (x + s * h * 0.135, hip_y + h * 0.07)], hd)
    cv2.ellipse(img, (int(x), int(yf - h * 0.92)), (int(h * 0.078), int(h * 0.092)), 0, 0, 360, hd, -1, AA)


def arman_sitting(img, hip_x, hip_y, h, k, glow=None, cfg=ARMAN):
    """Арман в кровати, вид сбоку (лицом вправо). k: 0 — лежит, 1 — сидит."""
    ang = math.radians(lerp_angle(82, 4, k))  # наклон корпуса от вертикали (к изголовью — влево)
    L = h * 0.36
    sx, sy = hip_x - math.sin(ang) * L, hip_y - math.cos(ang) * L  # плечи
    hd = cfg["hoodie"]
    nx, ny = math.cos(ang), -math.sin(ang)  # нормаль к корпусу
    wdt = h * 0.13
    poly(img, [(hip_x - nx * wdt, hip_y - ny * wdt), (hip_x + nx * wdt, hip_y + ny * wdt),
               (sx + nx * wdt * 1.05, sy + ny * wdt * 1.05), (sx - nx * wdt * 1.05, sy - ny * wdt * 1.05)], hd)
    hx, hy = sx - math.sin(ang) * h * 0.1, sy - math.cos(ang) * h * 0.1
    cv2.circle(img, (int(hx), int(hy)), int(h * 0.075), cfg["hair"], -1, AA)
    cv2.line(img, (int(sx), int(sy)), (int(hx), int(hy)), hd, int(h * 0.06), AA)  # шея/капюшон
    cv2.ellipse(img, (int(hip_x + h * 0.33), int(hip_y + h * 0.02)), (int(h * 0.36), int(h * 0.075)), 0, 180, 360, (44, 42, 48), -1, AA)  # ноги под одеялом
    # рука опирается о матрас рядом с бедром
    cv2.line(img, (int(lerp_pt(sx, hip_x, 0.35)), int(lerp_pt(sy, hip_y, 0.35))), (int(hip_x + h * 0.09), int(hip_y + h * 0.01)), hd, int(h * 0.05), AA)
    if glow is not None:  # отсвет экрана телефона по лицевой стороне
        fx0, fy0 = sx + nx * wdt * 1.0, sy + ny * wdt * 1.0  # передний край корпуса у плеча
        fx1, fy1 = lerp_pt(fx0, hip_x + nx * wdt, 0.45), lerp_pt(fy0, hip_y + ny * wdt, 0.45)
        cv2.line(img, (int(fx0), int(fy0)), (int(fx1), int(fy1)), tuple(int(c * 0.45) for c in glow), max(2, int(h * 0.02)), AA)
        cv2.ellipse(img, (int(hx + h * 0.05), int(hy)), (int(h * 0.02), int(h * 0.05)), 0, -60, 60, glow, max(2, int(h * 0.008)), AA)


def lerp_pt(a, b, k):
    return a + (b - a) * k


def lerp_angle(a, b, k):
    k = min(max(k, 0.0), 1.0)
    k = 1 - (1 - k) ** 3  # резкое начало движения
    return a + (b - a) * k


def hands_holding(img, cx, cy, pw, ph, cfg=ARMAN):
    """Руки в рукавах толстовки держат телефон (центр cx,cy; размер pw×ph)."""
    hd = cfg["hoodie"]
    sk = cfg["skin_shadow"]
    H_ = img.shape[0]
    for s in (-1, 1):
        ex = cx + s * pw * 0.48
        poly(img, [(ex - pw * 0.05, cy + ph * 0.18), (ex + s * pw * 0.32, cy + ph * 0.10), (ex + s * pw * 0.9, H_ + 40), (ex - s * pw * 0.2, H_ + 40)], hd)
        # ладонь обхватывает нижнюю часть корпуса сбоку
        cv2.ellipse(img, (int(ex + s * pw * 0.06), int(cy + ph * 0.24)), (int(pw * 0.11), int(ph * 0.10)), s * 15, 0, 360, sk, -1, AA)
        for i in range(3):  # пальцы заходят на край корпуса
            cv2.ellipse(img, (int(ex - s * pw * 0.005), int(cy + ph * 0.05 + i * ph * 0.055)), (int(pw * 0.045), int(ph * 0.02)), 0, 0, 360, sk, -1, AA)


# ---------- Амина: физически не появляется, только силуэт на фотографии ----------
AMINA = {
    "name": "Амина",
    "coat": (44, 38, 34),        # длинное тёмно-серое пальто
    "hair": (16, 18, 24),        # тёмные волосы ниже плеч
    "legs": (26, 24, 26),
    "height": 0.93,
}


def amina_back(img, x, yf, h, cfg=AMINA):
    """Амина со спины: длинное пальто, волосы ниже плеч, руки в карманах."""
    x, yf, h = float(x), float(yf), float(h) * cfg["height"]
    sh_y = yf - h * 0.81
    for s in (-1, 1):
        poly(img, [(x + s * h * 0.02, yf - h * 0.3), (x + s * h * 0.08, yf - h * 0.3), (x + s * h * 0.07, yf), (x + s * h * 0.035, yf)], cfg["legs"])
    poly(img, [(x - h * 0.13, sh_y + h * 0.05), (x - h * 0.09, sh_y), (x + h * 0.09, sh_y), (x + h * 0.13, sh_y + h * 0.05),
               (x + h * 0.15, yf - h * 0.27), (x - h * 0.15, yf - h * 0.27)], cfg["coat"])
    for s in (-1, 1):
        cv2.circle(img, (int(x + s * h * 0.1), int(sh_y + h * 0.045)), int(h * 0.04), cfg["coat"], -1, AA)
    hy = yf - h * 0.92
    poly(img, [(x - h * 0.07, hy), (x + h * 0.07, hy), (x + h * 0.085, sh_y + h * 0.12), (x - h * 0.085, sh_y + h * 0.12)], cfg["hair"])
    cv2.ellipse(img, (int(x), int(hy)), (int(h * 0.068), int(h * 0.078)), 0, 0, 360, cfg["hair"], -1, AA)
