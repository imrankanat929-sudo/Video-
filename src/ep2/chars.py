"""Персонажи «За мной кто-то идёт». Все — силуэты без лиц.
Герой: тёмная куртка, тёмные брюки, кроссовки, короткие тёмные волосы — один вид во всех кадрах.
Незнакомец: очень высокий, широкие плечи, чёрная куртка, тёмные брюки, лицо в тени."""
import math
from ..gfx import Pen

JACKET = (22, 25, 32)
JACKET_HI = (40, 44, 54)
PANTS = (34, 36, 44)
PANTS_SH = (26, 28, 34)
SHOE = (20, 20, 24)
SOLE = (120, 120, 124)
HAIR = (18, 16, 15)
SKIN_SH = (46, 38, 34)

S_JACKET = (10, 10, 12)
S_JACKET_HI = (24, 24, 28)
S_PANTS = (18, 18, 22)


def _k(c, k):
    return tuple(int(v * k) for v in c[:3])


def _walk(phase, stride):
    ph = phase * 2 * math.pi
    return ph, abs(math.sin(ph)) * 0.012 * stride


def hero(hgt, view="back", phase=0.0, stride=1.0, light=1.0, head_turn=0.0, arm_phone=False):
    """view: back (спиной, уходит) | front (лицом, но в тени) .
    head_turn -1..1 — поворот головы (видно ухо/профиль). Возвращает (rgba, foot_x, foot_y)."""
    w, h = int(hgt * 0.62), int(hgt * 1.04)
    p = Pen(w, h, ss=2)
    Hh = hgt
    cx = w / 2
    L = lambda c: _k(c, light)
    ph, bob = _walk(phase, stride)
    top = bob * Hh
    # ноги: в походке одна стопа приподнята и короче
    for side in (-1, 1):
        lift = max(0.0, side * math.sin(ph)) * 0.05 * stride
        xh = cx + side * 0.048 * Hh
        xa = cx + side * 0.055 * Hh + side * math.sin(ph) * 0.006 * Hh
        ya = (0.94 - lift) * Hh
        p.poly([(xh - 0.052 * Hh, 0.5 * Hh + top), (xh + 0.052 * Hh, 0.5 * Hh + top), (xa + 0.036 * Hh, ya),
                (xa - 0.038 * Hh, ya)], L(PANTS if side < 0 else PANTS_SH))
        p.rrect(xa - 0.046 * Hh, ya - 0.012 * Hh, xa + 0.044 * Hh, ya + 0.052 * Hh, 0.02 * Hh, L(SHOE))
        p.rect(xa - 0.046 * Hh, ya + 0.04 * Hh, xa + 0.044 * Hh, ya + 0.054 * Hh, L(SOLE))
    # руки
    for side in (-1, 1):
        if arm_phone and side > 0:
            p.line([(cx + 0.13 * Hh, 0.2 * Hh + top), (cx + 0.14 * Hh, 0.33 * Hh + top),
                    (cx + 0.06 * Hh, 0.36 * Hh + top)], L(JACKET), 0.06 * Hh)
            continue
        sw = -side * math.sin(ph) * 0.03 * stride
        p.line([(cx + side * 0.13 * Hh, 0.2 * Hh + top), (cx + side * 0.15 * Hh, 0.34 * Hh + top + sw * Hh),
                (cx + side * 0.145 * Hh, 0.46 * Hh + top + sw * Hh)], L(JACKET), 0.06 * Hh)
        p.ellipse(cx + side * 0.145 * Hh, 0.49 * Hh + top + sw * Hh, 0.02 * Hh, 0.028 * Hh, L(SKIN_SH))
    # куртка (короткая, до бёдер) с воротником
    p.poly([(cx - 0.14 * Hh, 0.19 * Hh + top), (cx - 0.07 * Hh, 0.155 * Hh + top), (cx + 0.07 * Hh, 0.155 * Hh + top),
            (cx + 0.14 * Hh, 0.19 * Hh + top), (cx + 0.13 * Hh, 0.36 * Hh + top), (cx + 0.125 * Hh, 0.53 * Hh + top),
            (cx - 0.125 * Hh, 0.53 * Hh + top), (cx - 0.13 * Hh, 0.36 * Hh + top)], L(JACKET))
    p.rect(cx - 0.125 * Hh, 0.51 * Hh + top, cx + 0.125 * Hh, 0.535 * Hh + top, L(JACKET_HI))
    if view == "front":
        p.line([(cx, 0.17 * Hh + top), (cx, 0.52 * Hh + top)], L(JACKET_HI), 0.005 * Hh)  # молния
    else:
        p.line([(cx - 0.09 * Hh, 0.3 * Hh + top), (cx + 0.09 * Hh, 0.3 * Hh + top)], L(JACKET_HI), 0.004 * Hh)
    p.poly([(cx - 0.07 * Hh, 0.15 * Hh + top), (cx + 0.07 * Hh, 0.15 * Hh + top), (cx + 0.06 * Hh, 0.19 * Hh + top),
            (cx - 0.06 * Hh, 0.19 * Hh + top)], L(JACKET_HI))  # воротник
    # голова
    hx = cx + head_turn * 0.012 * Hh
    p.rect(cx - 0.026 * Hh, 0.11 * Hh + top, cx + 0.026 * Hh, 0.16 * Hh + top, L(_k(SKIN_SH, 0.8)))
    if abs(head_turn) > 0.15:
        s = 1 if head_turn > 0 else -1
        p.ellipse(hx + s * 0.05 * Hh, 0.08 * Hh + top, 0.022 * Hh, 0.03 * Hh, L(SKIN_SH))  # профиль щеки (в тени)
    p.ellipse(hx, 0.066 * Hh + top, 0.056 * Hh, 0.068 * Hh, L(HAIR if view == "back" else _k(SKIN_SH, 0.55)))
    if view == "front":
        p.ellipse(hx, 0.035 * Hh + top, 0.058 * Hh, 0.04 * Hh, L(HAIR))
    for k in range(6):
        a = math.pi * (0.15 + 0.7 * k / 5)
        p.ellipse(hx - math.cos(a) * 0.048 * Hh, 0.066 * Hh + top - math.sin(a) * 0.062 * Hh, 0.014 * Hh,
                  0.012 * Hh, L(HAIR))
    return p.arr(), cx, 0.995 * Hh


def stranger(hgt, view="front", phase=0.0, stride=1.0, light=1.0, arm_up=0.0, phone=False):
    """Очень высокий широкоплечий мужчина; лицо скрыто тенью.
    arm_up 0..1 — правая рука поднимается (показывает телефон)."""
    w, h = int(hgt * 0.75), int(hgt * 1.04)
    p = Pen(w, h, ss=2)
    Hh = hgt
    cx = w / 2
    L = lambda c: _k(c, light)
    ph, bob = _walk(phase, stride)
    top = bob * Hh * 0.7
    for side in (-1, 1):
        lift = max(0.0, side * math.sin(ph)) * 0.04 * stride
        xh = cx + side * 0.055 * Hh
        xa = cx + side * 0.06 * Hh
        ya = (0.95 - lift) * Hh
        p.poly([(xh - 0.058 * Hh, 0.5 * Hh + top), (xh + 0.058 * Hh, 0.5 * Hh + top), (xa + 0.04 * Hh, ya),
                (xa - 0.042 * Hh, ya)], L(S_PANTS))
        p.rrect(xa - 0.05 * Hh, ya - 0.01 * Hh, xa + 0.05 * Hh, ya + 0.045 * Hh, 0.02 * Hh, L((8, 8, 9)))
    for side in (-1, 1):
        if side > 0 and arm_up > 0:
            a = arm_up
            ex, ey = cx + 0.2 * Hh, (0.36 - 0.12 * a) * Hh + top
            hx, hy = cx + (0.2 - 0.02 * a) * Hh, (0.48 - 0.33 * a) * Hh + top
            p.line([(cx + 0.17 * Hh, 0.2 * Hh + top), (ex, ey), (hx, hy)], L(S_JACKET), 0.072 * Hh)
            if phone:
                p.rrect(hx - 0.035 * Hh, hy - 0.07 * Hh, hx + 0.035 * Hh, hy + 0.01 * Hh, 0.008 * Hh, (6, 6, 8))
            continue
        sw = -side * math.sin(ph) * 0.02 * stride
        p.line([(cx + side * 0.17 * Hh, 0.2 * Hh + top), (cx + side * 0.19 * Hh, 0.35 * Hh + top + sw * Hh),
                (cx + side * 0.18 * Hh, 0.49 * Hh + top + sw * Hh)], L(S_JACKET), 0.072 * Hh)
        p.ellipse(cx + side * 0.18 * Hh, 0.52 * Hh + top + sw * Hh, 0.024 * Hh, 0.032 * Hh, L((24, 20, 18)))
    # широкий торс, чёрная куртка
    p.poly([(cx - 0.19 * Hh, 0.19 * Hh + top), (cx - 0.08 * Hh, 0.145 * Hh + top), (cx + 0.08 * Hh, 0.145 * Hh + top),
            (cx + 0.19 * Hh, 0.19 * Hh + top), (cx + 0.17 * Hh, 0.38 * Hh + top), (cx + 0.15 * Hh, 0.54 * Hh + top),
            (cx - 0.15 * Hh, 0.54 * Hh + top), (cx - 0.17 * Hh, 0.38 * Hh + top)], L(S_JACKET))
    p.rect(cx - 0.15 * Hh, 0.515 * Hh + top, cx + 0.15 * Hh, 0.545 * Hh + top, L(S_JACKET_HI))
    p.poly([(cx - 0.085 * Hh, 0.14 * Hh + top), (cx + 0.085 * Hh, 0.14 * Hh + top), (cx + 0.07 * Hh, 0.2 * Hh + top),
            (cx - 0.07 * Hh, 0.2 * Hh + top)], L(S_JACKET_HI))  # высокий воротник
    if view == "front":
        p.line([(cx, 0.18 * Hh + top), (cx, 0.53 * Hh + top)], L(S_JACKET_HI), 0.005 * Hh)
    # голова — полностью в тени
    p.rect(cx - 0.03 * Hh, 0.1 * Hh + top, cx + 0.03 * Hh, 0.15 * Hh + top, (8, 8, 9))
    p.ellipse(cx, 0.06 * Hh + top, 0.055 * Hh, 0.066 * Hh, (7, 7, 8))
    p.ellipse(cx, 0.025 * Hh + top, 0.058 * Hh, 0.035 * Hh, (12, 12, 14))
    return p.arr(), cx, 0.995 * Hh


def figure(hgt, kind="man", light=1.0, phase=0.0, stride=0.0, wave=0.0):
    """Прочие силуэты: друг (kind=friend), второй незнакомец (kind=second), продавец, охранник."""
    w, h = int(hgt * 0.7), int(hgt * 1.04)
    p = Pen(w, h, ss=2)
    Hh = hgt
    cx = w / 2
    L = lambda c: _k(c, light)
    col = {"friend": (40, 42, 52), "second": (12, 12, 14), "seller": (44, 44, 50), "guard": (26, 30, 34)}[kind]
    ph = phase * 2 * math.pi
    for side in (-1, 1):
        lift = max(0.0, side * math.sin(ph)) * 0.05 * stride
        p.line([(cx + side * 0.05 * Hh, 0.5 * Hh), (cx + side * 0.055 * Hh, (0.95 - lift) * Hh)], L(_k(col, 0.7)),
               0.085 * Hh)
    for side in (-1, 1):
        if kind == "friend" and side > 0 and wave > 0:
            a = math.sin(wave * 9) * 0.03
            p.line([(cx + 0.13 * Hh, 0.2 * Hh), (cx + 0.2 * Hh, 0.12 * Hh), (cx + (0.22 + a) * Hh, 0.02 * Hh)],
                   L(col), 0.055 * Hh)
            continue
        p.line([(cx + side * 0.13 * Hh, 0.2 * Hh), (cx + side * 0.15 * Hh, 0.48 * Hh)], L(col), 0.055 * Hh)
    p.poly([(cx - 0.14 * Hh, 0.19 * Hh), (cx + 0.14 * Hh, 0.19 * Hh), (cx + 0.13 * Hh, 0.54 * Hh),
            (cx - 0.13 * Hh, 0.54 * Hh)], L(col))
    p.ellipse(cx, 0.08 * Hh, 0.055 * Hh, 0.066 * Hh, L(_k(col, 0.8)))
    if kind == "second":  # капюшон
        p.poly([(cx - 0.075 * Hh, 0.15 * Hh), (cx - 0.07 * Hh, 0.04 * Hh), (cx, 0.0), (cx + 0.07 * Hh, 0.04 * Hh),
                (cx + 0.075 * Hh, 0.15 * Hh)], L(col))
    if kind == "guard":  # фуражка
        p.rect(cx - 0.07 * Hh, 0.02 * Hh, cx + 0.07 * Hh, 0.045 * Hh, L((16, 18, 22)))
        p.rect(cx - 0.08 * Hh, 0.04 * Hh, cx + 0.08 * Hh, 0.052 * Hh, L((16, 18, 22)))
    return p.arr(), cx, 0.995 * Hh
