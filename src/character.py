"""Тимур, 17 лет: тёмные волосы, чёрная толстовка, серые брюки, тёмные кроссовки.
Один набор цветов и пропорций для всех сцен — внешность не меняется."""
import math
from .gfx import Pen

HOODIE = (15, 15, 17)
HOODIE_FOLD = (27, 27, 31)
PANTS = (78, 78, 84)
PANTS_SH = (58, 58, 64)
HAIR = (21, 16, 13)
SKIN = (104, 78, 64)
SHOE = (24, 24, 28)
SOLE = (92, 92, 96)


def _scale(c, k):
    return tuple(int(v * k) for v in c[:3])


def timur_back(hgt, light=1.0, sway=0.0, phone=False):
    """Вид со спины, стоит. Возвращает (rgba, foot_x, foot_y)."""
    w, h = int(hgt * 0.6), int(hgt * 1.03)
    p = Pen(w, h, ss=2)
    cx = w / 2 + sway * hgt * 0.01
    Hh = hgt
    L = lambda c: _scale(c, light)
    # ноги
    for side in (-1, 1):
        x_hip = cx + side * 0.05 * Hh
        x_ank = cx + side * 0.058 * Hh
        p.poly([(x_hip - 0.055 * Hh, 0.49 * Hh), (x_hip + 0.055 * Hh, 0.49 * Hh),
                (x_ank + 0.036 * Hh, 0.935 * Hh), (x_ank - 0.04 * Hh, 0.935 * Hh)],
               L(PANTS if side < 0 else PANTS_SH))
        # складки
        p.line([(x_hip + side * 0.01 * Hh, 0.62 * Hh), (x_ank, 0.72 * Hh)], L(PANTS_SH), 0.006 * Hh)
        # кроссовки
        p.rrect(x_ank - 0.047 * Hh, 0.925 * Hh, x_ank + 0.043 * Hh, 0.995 * Hh, 0.02 * Hh, L(SHOE))
        p.rect(x_ank - 0.046 * Hh, 0.982 * Hh, x_ank + 0.042 * Hh, 0.997 * Hh, L(SOLE))
    # руки (рукава)
    for side in (-1, 1):
        if phone and side > 0:
            p.line([(cx + 0.125 * Hh, 0.19 * Hh), (cx + 0.15 * Hh, 0.33 * Hh), (cx + 0.07 * Hh, 0.37 * Hh)],
                   L(HOODIE), 0.062 * Hh)
            continue
        p.line([(cx + side * 0.125 * Hh, 0.19 * Hh), (cx + side * 0.15 * Hh, 0.33 * Hh),
                (cx + side * 0.142 * Hh, 0.46 * Hh)], L(HOODIE), 0.062 * Hh)
        p.ellipse(cx + side * 0.142 * Hh, 0.495 * Hh, 0.022 * Hh, 0.03 * Hh, L(SKIN))
        p.rect(cx + side * 0.142 * Hh - 0.03 * Hh, 0.455 * Hh, cx + side * 0.142 * Hh + 0.03 * Hh, 0.475 * Hh,
               L(HOODIE_FOLD))
    # торс-толстовка
    p.poly([(cx - 0.135 * Hh, 0.185 * Hh), (cx - 0.07 * Hh, 0.15 * Hh), (cx + 0.07 * Hh, 0.15 * Hh),
            (cx + 0.135 * Hh, 0.185 * Hh), (cx + 0.128 * Hh, 0.35 * Hh), (cx + 0.12 * Hh, 0.5 * Hh),
            (cx - 0.12 * Hh, 0.5 * Hh), (cx - 0.128 * Hh, 0.35 * Hh)], L(HOODIE))
    p.rect(cx - 0.12 * Hh, 0.475 * Hh, cx + 0.12 * Hh, 0.505 * Hh, L(HOODIE_FOLD))  # резинка
    p.line([(cx - 0.05 * Hh, 0.3 * Hh), (cx - 0.07 * Hh, 0.45 * Hh)], L(HOODIE_FOLD), 0.004 * Hh)
    p.line([(cx + 0.06 * Hh, 0.28 * Hh), (cx + 0.075 * Hh, 0.44 * Hh)], L(HOODIE_FOLD), 0.004 * Hh)
    # капюшон (лежит на спине)
    p.ellipse(cx, 0.185 * Hh, 0.082 * Hh, 0.05 * Hh, L(HOODIE_FOLD))
    p.ellipse(cx, 0.19 * Hh, 0.07 * Hh, 0.04 * Hh, L(HOODIE))
    # шея, уши, голова (затылок, тёмные волосы)
    p.rect(cx - 0.028 * Hh, 0.11 * Hh, cx + 0.028 * Hh, 0.16 * Hh, L(_scale(SKIN, 0.8)))
    p.ellipse(cx - 0.057 * Hh, 0.078 * Hh, 0.01 * Hh, 0.017 * Hh, L(_scale(SKIN, 0.75)))
    p.ellipse(cx + 0.057 * Hh, 0.078 * Hh, 0.01 * Hh, 0.017 * Hh, L(_scale(SKIN, 0.75)))
    p.ellipse(cx, 0.066 * Hh, 0.059 * Hh, 0.071 * Hh, L(HAIR))
    # пряди по контуру макушки (неровный, «живой» силуэт)
    for k in range(7):
        a = math.pi * (0.15 + 0.7 * k / 6)
        p.ellipse(cx - math.cos(a) * 0.05 * Hh, 0.066 * Hh - math.sin(a) * 0.064 * Hh, 0.016 * Hh,
                  0.013 * Hh, L(HAIR))
    p.poly([(cx - 0.052 * Hh, 0.09 * Hh), (cx + 0.052 * Hh, 0.09 * Hh), (cx + 0.036 * Hh, 0.122 * Hh),
            (cx - 0.036 * Hh, 0.122 * Hh)], L(HAIR))
    return p.arr(), cx, 0.997 * Hh


def timur_side(hgt, phase=0.0, light=1.0, flashlight=True, facing=1, stride=1.0):
    """Вид сбоку (силуэт) при ходьбе. phase 0..1. Возвращает (rgba, foot_x, foot_y, torch_xy)."""
    w, h = int(hgt * 0.8), int(hgt * 1.03)
    p = Pen(w, h, ss=2)
    Hh = hgt
    cx = w / 2
    L = lambda c: _scale(c, light)
    ph = phase * 2 * math.pi
    bob = abs(math.sin(ph)) * 0.008 * Hh
    hip = (cx, 0.5 * Hh - bob)
    th, sh = 0.235 * Hh, 0.235 * Hh
    f = lambda v: v * facing

    def leg(sign, col):
        a = sign * 0.42 * stride * math.sin(ph)  # бедро
        knee_bend = max(0.0, sign * math.sin(ph + 1.3)) * 0.38 * stride + 0.06
        kx = hip[0] + f(math.sin(a) * th); ky = hip[1] + math.cos(a) * th
        b = a - knee_bend
        ax = kx + f(math.sin(b) * sh); ay = ky + math.cos(b) * sh
        p.line([hip, (kx, ky), (ax, ay)], L(col), 0.075 * Hh)
        # кроссовок
        p.rrect(ax - f(0.03 * Hh) if facing > 0 else ax - 0.075 * Hh, ay - 0.012 * Hh,
                ax + 0.075 * Hh if facing > 0 else ax + 0.03 * Hh, ay + 0.035 * Hh, 0.015 * Hh, L(SHOE))
        p.rect(min(ax - f(0.03 * Hh), ax + f(0.075 * Hh)), ay + 0.025 * Hh,
               max(ax - f(0.03 * Hh), ax + f(0.075 * Hh)), ay + 0.037 * Hh, L(SOLE))

    def arm(sign, col, torch=False):
        sx, sy = cx + f(0.005 * Hh), 0.19 * Hh - bob
        if torch:
            ex, ey = sx + f(0.1 * Hh), 0.3 * Hh - bob
            hx, hy = ex + f(0.13 * Hh), 0.29 * Hh - bob
            p.line([(sx, sy), (ex, ey), (hx, hy)], L(col), 0.058 * Hh)
            p.ellipse(hx + f(0.01 * Hh), hy, 0.02 * Hh, 0.022 * Hh, L(SKIN))
            p.line([(hx, hy - 0.002 * Hh), (hx + f(0.07 * Hh), hy - 0.01 * Hh)], (40, 40, 44), 0.022 * Hh)
            return (hx + f(0.075 * Hh), hy - 0.01 * Hh)
        a = -sign * 0.35 * stride * math.sin(ph)
        ex, ey = sx + f(math.sin(a) * 0.15 * Hh), sy + math.cos(a) * 0.15 * Hh
        a2 = a + 0.25
        hx, hy = ex + f(math.sin(a2) * 0.14 * Hh), ey + math.cos(a2) * 0.14 * Hh
        p.line([(sx, sy), (ex, ey), (hx, hy)], L(col), 0.058 * Hh)
        p.ellipse(hx, hy + 0.01 * Hh, 0.02 * Hh, 0.026 * Hh, L(SKIN))
        return None

    leg(-1, PANTS_SH)
    arm(-1, (10, 10, 12))
    # торс
    lean = f(0.012 * Hh)
    p.poly([(cx - f(0.065 * Hh) + lean, 0.16 * Hh - bob), (cx + f(0.055 * Hh) + lean, 0.16 * Hh - bob),
            (cx + f(0.075 * Hh), 0.33 * Hh - bob), (cx + f(0.07 * Hh), 0.51 * Hh - bob),
            (cx - f(0.075 * Hh), 0.51 * Hh - bob), (cx - f(0.08 * Hh), 0.3 * Hh - bob)], L(HOODIE))
    p.rect(cx - 0.075 * Hh, 0.485 * Hh - bob, cx + 0.072 * Hh, 0.512 * Hh - bob, L(HOODIE_FOLD))
    # капюшон сзади шеи
    p.ellipse(cx - f(0.05 * Hh) + lean, 0.175 * Hh - bob, 0.045 * Hh, 0.04 * Hh, L(HOODIE_FOLD))
    leg(1, PANTS)
    # шея + голова
    p.rect(cx - 0.02 * Hh + lean, 0.11 * Hh - bob, cx + 0.022 * Hh + lean, 0.165 * Hh - bob, L(_scale(SKIN, 0.7)))
    hx, hy = cx + f(0.012 * Hh) + lean, 0.066 * Hh - bob
    p.ellipse(hx, hy, 0.056 * Hh, 0.068 * Hh, L(_scale(SKIN, 0.55)))
    p.ellipse(hx - f(0.012 * Hh), hy - 0.012 * Hh, 0.055 * Hh, 0.058 * Hh, L(HAIR))
    p.ellipse(hx + f(0.02 * Hh), hy - 0.045 * Hh, 0.04 * Hh, 0.022 * Hh, L(HAIR))
    torch = arm(1, HOODIE, torch=flashlight)
    return p.arr(), cx, hip[1] + th + sh + 0.035 * Hh, torch


def person(hgt, kind=0, light=1.0, head_turn=0.0, seated=True, seed=0):
    """Другие люди в убежище — безликие силуэты. head_turn -1..1."""
    w, h = int(hgt * 0.9), int(hgt * 1.05)
    p = Pen(w, h, ss=2)
    Hh = hgt
    cx = w / 2
    cols = [(34, 32, 30), (40, 34, 30), (30, 32, 36), (44, 40, 36), (28, 26, 26), (38, 36, 40)]
    coat = _scale(cols[kind % len(cols)], light)
    dark = _scale((20, 19, 19), light)
    hair = _scale([(30, 26, 22), (55, 52, 50), (20, 18, 16), (70, 66, 60), (24, 20, 18), (40, 30, 24)][kind % 6], light)
    if seated:
        # колени/ноги
        p.poly([(cx - 0.17 * Hh, 0.62 * Hh), (cx + 0.2 * Hh, 0.62 * Hh), (cx + 0.24 * Hh, 0.72 * Hh),
                (cx - 0.15 * Hh, 0.74 * Hh)], dark)
        p.line([(cx + 0.2 * Hh, 0.7 * Hh), (cx + 0.22 * Hh, 0.98 * Hh)], dark, 0.08 * Hh)
        p.line([(cx + 0.1 * Hh, 0.7 * Hh), (cx + 0.12 * Hh, 0.98 * Hh)], dark, 0.08 * Hh)
        top = 0.28 * Hh
        hunch = 0.04 * Hh * (kind % 3)
        p.poly([(cx - 0.15 * Hh, top + 0.07 * Hh), (cx + 0.13 * Hh, top + 0.07 * Hh + hunch * .3),
                (cx + 0.17 * Hh, 0.66 * Hh), (cx - 0.18 * Hh, 0.68 * Hh)], coat)
        hy = top + hunch * 0.5
    else:
        for s in (-1, 1):
            p.line([(cx + s * 0.05 * Hh, 0.5 * Hh), (cx + s * 0.06 * Hh, 0.98 * Hh)], dark, 0.08 * Hh)
        p.poly([(cx - 0.14 * Hh, 0.18 * Hh), (cx + 0.14 * Hh, 0.18 * Hh), (cx + 0.15 * Hh, 0.62 * Hh),
                (cx - 0.15 * Hh, 0.62 * Hh)], coat)
        for s in (-1, 1):
            p.line([(cx + s * 0.13 * Hh, 0.2 * Hh), (cx + s * 0.16 * Hh, 0.5 * Hh)], coat, 0.06 * Hh)
        hy = 0.1 * Hh
    hx = cx + head_turn * 0.03 * Hh
    p.rect(cx - 0.025 * Hh, hy + 0.02 * Hh, cx + 0.025 * Hh, hy + 0.1 * Hh, _scale((60, 48, 40), light))
    p.ellipse(hx, hy, 0.06 * Hh, 0.07 * Hh, _scale((62, 50, 44), light))
    p.ellipse(hx - head_turn * 0.012 * Hh, hy - 0.015 * Hh, 0.062 * Hh, 0.06 * Hh, hair)
    return p.arr(), cx, 0.98 * Hh
