"""Квартира Армана. Расположение мебели одинаковое во всех сценах и сериях.

Спальня (мир 2600×1080): кровать слева (изголовье слева), тумбочка с часами и телефоном,
окно с задёрнутыми шторами, справа проём в гостиную — там на дальней стене телевизор.
Гостиная: телевизор на тумбе слева, окно на город справа, диван на переднем плане.
Прихожая: коридор в перспективе, входная металлическая дверь в глубине,
петли слева, ручка и задвижка замка справа, глазок по центру.
"""
import math

import cv2
import numpy as np

from core import AA, H, W, blob, gradient, poly, to_lmap, u8

WALL = (34, 30, 30)
WALL_D = (22, 20, 20)
FLOOR = (24, 24, 28)
WOOD = (30, 34, 42)

# ---------- спальня ----------
BED_W = 2600
BED = dict(bed=(200, 1150), mattress_y=690, floor_y=860, stand=(1180, 1400), stand_top=700,
           clock=(1205, 640, 1330, 700), phone=(1345, 690), window=(1500, 220, 1800, 620),
           doorway=(2050, 250, 2420, 860), tv=(2170, 520, 2330, 610))


def bedroom_base():
    img = gradient(H, BED_W, (30, 26, 26), (20, 18, 18))
    fy = BED["floor_y"]
    img[fy:] = gradient(H - fy, BED_W, (26, 26, 30), (16, 16, 18))
    for x in range(0, BED_W, 140):
        cv2.line(img, (x, fy), (x - 60, H), (20, 20, 22), 2)
    cv2.rectangle(img, (0, fy - 14), (BED_W, fy), (18, 16, 16), -1)  # плинтус
    # окно со шторами
    x0, y0, x1, y1 = BED["window"]
    cv2.rectangle(img, (x0 - 30, y0 - 30), (x1 + 30, y1 + 20), (40, 36, 34), -1)
    for cx0, cx1 in ((x0 - 60, (x0 + x1) // 2 - 4), ((x0 + x1) // 2 + 4, x1 + 60)):
        cv2.rectangle(img, (cx0, y0 - 50), (cx1, fy - 40), (36, 30, 34), -1)
        for k in range(cx0 + 20, cx1, 36):
            cv2.line(img, (k, y0 - 40), (k, fy - 50), (28, 24, 28), 3)
    cv2.line(img, ((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1), (70, 60, 56), 3)  # щель между шторами
    cv2.rectangle(img, (x0 - 80, y0 - 64), (x1 + 80, y0 - 52), (20, 18, 18), -1)  # карниз
    # кровать
    bx0, bx1 = BED["bed"]
    my = BED["mattress_y"]
    cv2.rectangle(img, (bx0 - 40, 420), (bx0 + 10, fy), (24, 22, 24), -1)  # изголовье
    cv2.rectangle(img, (bx0, my), (bx1, fy - 60), (40, 38, 44), -1)
    cv2.rectangle(img, (bx0, fy - 60), (bx1, fy - 10), (20, 18, 20), -1)
    cv2.ellipse(img, (bx0 + 110, my - 10), (90, 40), 0, 0, 360, (54, 52, 58), -1, AA)  # подушка
    # тумбочка
    s0, s1 = BED["stand"]
    st = BED["stand_top"]
    cv2.rectangle(img, (s0, st), (s1, fy), (26, 30, 38), -1)
    cv2.rectangle(img, (s0 - 8, st - 12), (s1 + 8, st), (32, 36, 44), -1)
    cv2.line(img, (s0 + 10, st + 70), (s1 - 10, st + 70), (18, 20, 26), 2)
    cv2.circle(img, ((s0 + s1) // 2, st + 40), 6, (40, 46, 56), -1, AA)
    c0, c1, c2, c3 = BED["clock"]
    cv2.rectangle(img, (c0, c1), (c2, c3), (16, 16, 18), -1)
    # проём в гостиную: темнее, видна дальняя стена с ТВ
    d0, d1, d2, d3 = BED["doorway"]
    cv2.rectangle(img, (d0 - 20, d1 - 20), (d2 + 20, d3), (26, 22, 22), -1)
    cv2.rectangle(img, (d0, d1), (d2, d3), (14, 13, 14), -1)
    cv2.rectangle(img, (d0, 760), (d2, d3), (12, 12, 14), -1)
    t0, t1, t2, t3 = BED["tv"]
    cv2.rectangle(img, (t0 - 8, t1 - 8), (t2 + 8, t3 + 8), (8, 8, 9), -1)
    cv2.rectangle(img, (t0 - 30, t3 + 8), (t2 + 30, t3 + 70), (12, 12, 14), -1)
    return img


def bedroom_lmap(screen_on=1.0):
    """Свет: телефон на тумбочке и полоска лунного света между шторами."""
    lm = np.full((H, BED_W, 3), 0.7, np.float32)
    x0, y0, x1, y1 = BED["window"]
    lm += blob(H, BED_W, (x0 + x1) / 2, 520, 60, 360, (0.5, 0.45, 0.35))
    lm += blob(H, BED_W, 520, 420, 420, 300, (1.1, 0.9, 0.7))  # холодный отсвет на стене за кроватью — силуэт читается
    px, py = BED["phone"]
    lm += blob(H, BED_W, px, py - 30, 260, 180, (1.4, 1.1, 0.8)) * screen_on
    return lm


# ---------- гостиная ----------
LIV = dict(tv=(330, 300, 1090, 730), cabinet=(290, 730, 1130, 830), window=(1330, 170, 1830, 690), floor_y=840)


def living_base(city_lit=True, seed=21):
    rng = np.random.default_rng(seed)
    img = gradient(H, W, (30, 26, 26), (20, 18, 18))
    fy = LIV["floor_y"]
    img[fy:] = gradient(H - fy, W, (26, 26, 30), (14, 14, 16))
    # окно на город
    x0, y0, x1, y1 = LIV["window"]
    sky = gradient(y1 - y0, x1 - x0, (34, 18, 10), (44, 26, 16))
    img[y0:y1, x0:x1] = sky
    for i in range(9):
        bx = x0 + int(rng.integers(-40, x1 - x0))
        bw = int(rng.integers(60, 150))
        top = y0 + int(rng.integers(140, 380))
        cv2.rectangle(img, (bx, top), (min(x1, bx + bw), y1), (20, 18, 18), -1)
        if city_lit:
            for wy in range(top + 12, y1, 22):
                for wx in range(bx + 8, min(x1, bx + bw) - 8, 18):
                    if rng.random() < 0.35:
                        cv2.rectangle(img, (wx, wy), (wx + 8, wy + 10), (70, 140, 190), -1)
    cv2.rectangle(img, (x0, y0), (x1, y1), (14, 14, 16), 14)
    cv2.line(img, ((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1), (14, 14, 16), 12)
    cv2.rectangle(img, (x0 - 30, y1), (x1 + 30, y1 + 18), (26, 24, 24), -1)
    # тумба и ТВ
    c = LIV["cabinet"]
    cv2.rectangle(img, (c[0], c[1]), (c[2], c[3]), (24, 26, 32), -1)
    cv2.line(img, ((c[0] + c[2]) // 2, c[1] + 10), ((c[0] + c[2]) // 2, c[3] - 10), (16, 18, 22), 3)
    t = LIV["tv"]
    cv2.rectangle(img, (t[0] - 16, t[1] - 16), (t[2] + 16, t[3] + 16), (10, 10, 11), -1)
    cv2.rectangle(img, (t[0], t[1]), (t[2], t[3]), (6, 6, 7), -1)
    # диван на переднем плане (силуэт)
    poly(img, [(-20, 900), (980, 900), (1010, 960), (1010, H + 5), (-20, H + 5)], (12, 12, 14))
    cv2.ellipse(img, (980, 930), (50, 70), 0, 0, 360, (12, 12, 14), -1, AA)
    return img


def living_tv_rect():
    return LIV["tv"]


# ---------- прихожая ----------
DOOR = dict(x0=790, y0=250, x1=1130, y1=840, handle=(1092, 575), lock=(1094, 505), peep=(960, 430))
VP = (960, 520)


def hallway_base():
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (20, 18, 18)
    d = DOOR
    # стены, пол, потолок к точке схода
    poly(img, [(0, 0), (d["x0"] - 60, d["y0"] - 60), (d["x0"] - 60, d["y1"] + 30), (0, H)], (28, 26, 26))
    poly(img, [(W, 0), (d["x1"] + 60, d["y0"] - 60), (d["x1"] + 60, d["y1"] + 30), (W, H)], (26, 24, 24))
    poly(img, [(0, H), (d["x0"] - 60, d["y1"] + 30), (d["x1"] + 60, d["y1"] + 30), (W, H)], FLOOR)
    poly(img, [(0, 0), (d["x0"] - 60, d["y0"] - 60), (d["x1"] + 60, d["y0"] - 60), (W, 0)], (18, 16, 16))
    for k in range(1, 9):  # доски пола
        x = k * W / 9
        cv2.line(img, (int(x), H), (int(d["x0"] - 60 + (d["x1"] - d["x0"] + 120) * k / 9), d["y1"] + 30), (18, 18, 22), 2, AA)
    # торцевая стена вокруг двери
    cv2.rectangle(img, (d["x0"] - 60, d["y0"] - 60), (d["x1"] + 60, d["y1"] + 30), (30, 28, 28), -1)
    # вешалка с курткой слева
    cv2.line(img, (180, 300), (520, 360), (14, 14, 16), 10, AA)
    poly(img, [(300, 330), (420, 350), (450, 690), (270, 660)], (16, 16, 18))
    # обувная тумба справа
    poly(img, [(1450, 760), (1760, 700), (1760, 900), (1450, 880)], (18, 18, 20))
    # дверь
    cv2.rectangle(img, (d["x0"] - 16, d["y0"] - 16), (d["x1"] + 16, d["y1"]), (16, 14, 14), -1)
    door_panel(img, 0.0)
    return img


def door_panel(img, open_k, gap_col=(3, 3, 4)):
    """Рисует дверь. open_k: 0 — закрыта, 1 — открыта на ~35°. Открывается наружу, петли слева."""
    d = DOOR
    x0, y0, x1, y1 = d["x0"], d["y0"], d["x1"], d["y1"]
    if open_k > 0:
        cv2.rectangle(img, (x0, y0), (x1, y1), gap_col, -1)
    a = math.radians(48 * open_k)
    wdt = (x1 - x0) * math.cos(a)
    shrink = 1 - 0.18 * math.sin(a)  # дальний край уходит вглубь
    ex = x0 + wdt
    ey0 = VP[1] + (y0 - VP[1]) * shrink
    ey1 = VP[1] + (y1 - VP[1]) * shrink
    pts = [(x0, y0), (ex, ey0), (ex, ey1), (x0, y1)]
    poly(img, pts, (38, 34, 34))
    inset = 26
    poly(img, [(x0 + inset, y0 + inset), (ex - inset * math.cos(a), ey0 + inset), (ex - inset * math.cos(a), ey1 - inset), (x0 + inset, y1 - inset)], (44, 40, 40))
    def at(fx, y):  # точка на полотне: доля ширины fx, высота y
        px = x0 + wdt * fx
        py = VP[1] + (y - VP[1]) * (1 - (1 - shrink) * fx)
        return int(px), int(py)
    hx, hy = at(0.88, d["handle"][1])
    cv2.rectangle(img, (hx - 10, hy - 34), (hx + 10, hy + 34), (60, 58, 58), -1)
    cv2.line(img, (hx, hy), (hx - int(60 * math.cos(a)), hy + 4), (80, 78, 78), 10, AA)
    lx, ly = at(0.88, d["lock"][1])
    cv2.circle(img, (lx, ly), 16, (60, 58, 58), -1, AA)
    cv2.line(img, (lx - int(12 * math.cos(a)), ly), (lx + int(12 * math.cos(a)), ly), (90, 88, 88), 6, AA)
    px, py = at(0.5, d["peep"][1])
    cv2.circle(img, (px, py), 8, (70, 70, 74), -1, AA)
    cv2.circle(img, (px, py), 4, (12, 12, 14), -1, AA)


def hallway_lmap(flash=None, side=0.25):
    lm = np.full((H, W, 3), 0.45, np.float32)
    lm += blob(H, W, 240, 600, 380, 500, (0.2, 0.22, 0.3)) * side / 0.25  # холодный свет из комнаты слева
    if flash is not None:
        fx, fy, r = flash
        lm += blob(H, W, fx, fy, r, r * 0.8, (2.2, 2.4, 2.6))
    return lm


class LockClose:
    """Крупно: задвижка замка (закрыта) и ручка на металлической двери."""

    def __init__(self):
        rng = np.random.default_rng(3)
        n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=40, sigmaY=1.5)
        base = np.clip(40 + n * 60, 20, 70).astype(np.uint8)
        img = cv2.merge([base, (base * 0.92).astype(np.uint8), (base * 0.9).astype(np.uint8)])
        cv2.rectangle(img, (1460, 0), (1530, H), (18, 16, 16), -1)  # стык двери и косяка
        cv2.rectangle(img, (760, 180), (1060, 900), (58, 56, 58), -1)  # накладка
        cv2.rectangle(img, (760, 180), (1060, 900), (30, 30, 32), 4)
        cv2.circle(img, (910, 380), 95, (84, 82, 84), -1, AA)           # розетка задвижки
        cv2.circle(img, (910, 380), 95, (40, 40, 42), 4, AA)
        cv2.rectangle(img, (790, 352), (1030, 408), (120, 118, 120), -1)  # барашек — горизонтально = заперто
        cv2.rectangle(img, (790, 352), (1030, 408), (50, 50, 52), 3)
        cv2.circle(img, (910, 700), 46, (84, 82, 84), -1, AA)            # ручка
        poly(img, [(890, 680), (540, 690), (530, 740), (890, 730)], (100, 98, 100))
        cv2.ellipse(img, (910, 830), (14, 30), 0, 0, 360, (12, 12, 12), -1, AA)  # скважина
        self.base = img
        self.light = to_lmap(np.full((H, W, 3), 0.35, np.float32) + blob(H, W, 920, 420, 520, 420, (1.4, 1.5, 1.6)))

    def frame(self, t):
        return cv2.multiply(self.base, self.light, scale=1 / 128)


class Peephole:
    """Вид в дверной глазок: пустой подъездный коридор, тусклая лампа в конце."""

    def __init__(self):
        img = np.zeros((H, W, 3), np.uint8)
        vp = (960, 500)
        img[:] = (40, 46, 44)
        poly(img, [(0, 0), (820, 380), (820, 640), (0, H)], (44, 54, 50))
        poly(img, [(W, 0), (1100, 380), (1100, 640), (W, H)], (40, 50, 46))
        poly(img, [(0, H), (820, 640), (1100, 640), (W, H)], (40, 44, 48))
        poly(img, [(0, 0), (820, 380), (1100, 380), (W, 0)], (60, 64, 62))
        poly(img, [(0, 560), (820, 520), (820, 640), (0, H)], (36, 60, 46))  # крашеная панель снизу
        poly(img, [(W, 560), (1100, 520), (1100, 640), (W, H)], (34, 56, 44))
        cv2.rectangle(img, (820, 380), (1100, 640), (34, 38, 38), -1)
        for x, w in ((200, 160), (1540, 170)):  # двери соседей
            poly(img, [(x, 250), (x + w, 330), (x + w, 760), (x, 860)] if x < 960 else [(x + w, 250), (x, 330), (x, 760), (x + w, 860)], (28, 26, 30))
        cv2.circle(img, (960, 400), 10, (180, 220, 240), -1, AA)
        light = np.full((H, W, 3), 0.35, np.float32) + blob(H, W, 960, 420, 300, 260, (1.2, 1.4, 1.6))
        img = cv2.multiply(img, to_lmap(light), scale=1 / 128)
        img = cv2.add(img, u8(blob(H, W, 960, 400, 60, 50, (120, 170, 200))))
        # «рыбий глаз»
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        nx, ny = (xx - W / 2) / (H / 2), (yy - H / 2) / (H / 2)
        r = np.sqrt(nx ** 2 + ny ** 2)
        k = 1 + 0.45 * r ** 2
        mapx = (W / 2 + nx / k * (H / 2) * 1.35).astype(np.float32)
        mapy = (H / 2 + ny / k * (H / 2) * 1.35).astype(np.float32)
        fish = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        fish = cv2.GaussianBlur(fish, (0, 0), 1.6)
        mask = np.clip((0.92 - r) / 0.08, 0, 1)[..., None]
        self.img = (fish * mask).astype(np.uint8)
        self.lamp = u8(blob(H, W, *self._lamp_pos(mapx, mapy), 30, 26, (80, 110, 130)))

    def _lamp_pos(self, mx, my):
        d = (mx - 960) ** 2 + (my - 400) ** 2
        y, x = np.unravel_index(np.argmin(d), d.shape)
        return x, y

    def frame(self, t):
        fl = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 23) * math.sin(t * 3.1))
        return cv2.add(self.img, cv2.convertScaleAbs(self.lamp, alpha=fl))
