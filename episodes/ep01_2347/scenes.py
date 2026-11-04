"""Серия 1 «23:47» — визуальные планы.

Каждый план — класс с методом frame(t), где t — время от начала серии (с).
Всё рисуется в 2D: тёмная ночная палитра, силуэты, лунный и натриевый свет.
"""
import math

import cv2
import numpy as np

W, H, FPS = 1920, 1080, 30
AA = cv2.LINE_AA

# ---------- палитра (BGR) ----------
SKY_TOP, SKY_BOT = (22, 10, 6), (46, 24, 14)
FACADE = (38, 34, 36)
FACADE_DARK = (26, 23, 25)
WIN_OFF = (30, 24, 22)
GROUND = (24, 24, 28)
SIL = (16, 15, 18)
SKIN = (150, 160, 178)
HAIR = (40, 90, 215)       # рыжий
UNIFORM = (40, 82, 34)     # зелёная форма
PARKA = (34, 40, 40)
ROBE = (96, 92, 116)
WARM = [(70, 150, 210), (90, 165, 220), (60, 125, 195), (130, 160, 175)]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def lerp(a, b, x):
    return a + (b - a) * x


def gradient(h, w, top, bot):
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    g = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    return np.repeat(g, w, axis=1).astype(np.uint8)


def blob(h, w, cx, cy, rx, ry, color, power=1.0):
    """Мягкое световое пятно как float-слой (для glow/lightmap)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    return np.exp(-d)[..., None] * np.array(color, np.float32) * power


def camera(img, z, cx, cy, rot=0.0):
    """Камера: (cx, cy) — точка мира в центре кадра, z — зум (>=1)."""
    hw, hh = W / (2 * z), H / (2 * z)
    cx = min(max(cx, hw), img.shape[1] - hw)
    cy = min(max(cy, hh), img.shape[0] - hh)
    M = cv2.getRotationMatrix2D((cx, cy), rot, z)
    M[0, 2] += W / 2 - cx
    M[1, 2] += H / 2 - cy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def apply_light(img, lmap_u8, glow_u8=None):
    out = cv2.multiply(img, lmap_u8, scale=1 / 128)
    if glow_u8 is not None:
        out = cv2.add(out, glow_u8)
    return out


def to_lmap(f):
    return np.clip(f * 128, 0, 255).astype(np.uint8)


# ---------- персонажи ----------
# Приглушённые ночные цвета одежды (BGR)
TOPS = [(70, 44, 30), (40, 52, 78), (58, 58, 62), (36, 92, 112), (42, 70, 50), (96, 112, 128),
        (82, 64, 50), (30, 30, 34), (64, 40, 70), (50, 78, 96), (88, 88, 92), (80, 70, 40)]
PANTS = [(60, 40, 28), (26, 26, 30), (46, 46, 50), (40, 50, 64), (72, 54, 40), (34, 40, 36)]
HAIRS = [(18, 18, 20), (24, 38, 58), (40, 52, 70), (90, 92, 96), (30, 30, 34)]
HATS = [None, None, None, (90, 60, 40), (70, 60, 50), (30, 30, 32), (60, 90, 100)]
# ночью цвета приглушены; рыжего и красного нет — это цвет Веры
DIM = 0.42
TOPS, PANTS, HAIRS = ([tuple(int(c * DIM) for c in col) for col in pal] for pal in (TOPS, PANTS, HAIRS))
HATS = [None if h is None else tuple(int(c * DIM) for c in h) for h in HATS]


def outfit(rng):
    """Случайный комплект одежды: верх, низ, волосы, шапка (или None), длинное пальто."""
    return (TOPS[rng.integers(len(TOPS))], PANTS[rng.integers(len(PANTS))],
            HAIRS[rng.integers(len(HAIRS))], HATS[rng.integers(len(HATS))], rng.random() < 0.3)


def person(img, x, yf, h, facing=-1, phase=None, kind="generic", col=SIL, wear=None):
    """Силуэт человека в профиль. yf — уровень ступней, h — рост в пикселях.
    wear — комплект одежды из outfit(); без него рисуется тёмный силуэт."""
    if kind == "generic" and wear is not None:
        return dressed(img, x, yf, h, facing, phase, wear)
    x, yf, h = float(x), float(yf), float(h)
    r = h * 0.075
    hy = yf - h + r
    sh_y, hip_y = yf - h * 0.80, yf - h * 0.47
    step = 0.0 if phase is None else math.sin(phase)
    lw = max(1, int(h * 0.055))
    body = col
    if kind == "robe":
        body = ROBE
    elif kind == "vera":
        body = UNIFORM
    # ноги
    for s in (-1, 1):
        fx = x + facing * s * step * h * 0.09
        cv2.line(img, (int(x + s * h * 0.025), int(hip_y)), (int(fx), int(yf)), col, lw, AA)
    if kind == "robe":
        pts = [(x - h * 0.09, sh_y), (x + h * 0.09, sh_y), (x + h * 0.12, yf - h * 0.2), (x - h * 0.12, yf - h * 0.2)]
        cv2.fillPoly(img, [np.int32(pts)], body, AA)
        for s in (-1, 1):  # тапочки
            fx = x + facing * s * step * h * 0.09
            cv2.ellipse(img, (int(fx + facing * h * 0.02), int(yf)), (max(1, int(h * 0.035)), max(1, int(h * 0.012))), 0, 0, 360, (120, 120, 150), -1, AA)
    else:
        pts = [(x - h * 0.10, sh_y), (x + h * 0.10, sh_y), (x + h * 0.075, hip_y + h * 0.02), (x - h * 0.075, hip_y + h * 0.02)]
        cv2.fillPoly(img, [np.int32(pts)], body, AA)
    if kind == "vera":  # парка на плечах
        pts = [(x - h * 0.12, sh_y - h * 0.01), (x + h * 0.12, sh_y - h * 0.01), (x + h * 0.11, sh_y + h * 0.2), (x - h * 0.11, sh_y + h * 0.2)]
        cv2.fillPoly(img, [np.int32(pts)], PARKA, AA)
    # руки висят вдоль тела
    cv2.line(img, (int(x), int(sh_y + h * 0.02)), (int(x + facing * h * 0.015), int(hip_y + h * 0.05)), col if kind != "vera" else PARKA, lw, AA)
    # шея и голова
    cv2.line(img, (int(x), int(sh_y)), (int(x + facing * h * 0.01), int(hy + r)), col, lw, AA)
    if kind == "vera":
        cv2.ellipse(img, (int(x - facing * r * 1.4), int(hy + r * 0.6)), (max(1, int(r * 0.45)), max(1, int(r * 1.3))), -facing * 20, 0, 360, HAIR, -1, AA)
        cv2.circle(img, (int(x), int(hy)), max(1, int(r)), HAIR, -1, AA)
        cv2.circle(img, (int(x + facing * r * 0.35), int(hy + r * 0.1)), max(1, int(r * 0.7)), (70, 80, 100), -1, AA)
    else:
        cv2.circle(img, (int(x), int(hy)), max(1, int(r)), col, -1, AA)
        if kind == "robe":  # бледное лицо
            cv2.circle(img, (int(x + facing * r * 0.35), int(hy + r * 0.1)), max(1, int(r * 0.7)), (80, 86, 100), -1, AA)


def dressed(img, x, yf, h, facing, phase, wear):
    top, pants, hair, hat, coat = wear
    x, yf, h = float(x), float(yf), float(h)
    r = h * 0.075
    hy = yf - h + r
    sh_y, hip_y = yf - h * 0.80, yf - h * 0.47
    step = 0.0 if phase is None else math.sin(phase)
    lw = max(1, int(h * 0.06))
    for s in (-1, 1):
        fx = x + facing * s * step * h * 0.09
        cv2.line(img, (int(x + s * h * 0.025), int(hip_y)), (int(fx), int(yf)), pants, lw, AA)
        cv2.line(img, (int(fx), int(yf)), (int(fx + facing * h * 0.04), int(yf)), (14, 14, 16), max(1, lw), AA)
    bottom = yf - h * 0.22 if coat else hip_y + h * 0.04
    pts = [(x - h * 0.10, sh_y), (x + h * 0.10, sh_y), (x + h * (0.10 if coat else 0.08), bottom), (x - h * (0.10 if coat else 0.08), bottom)]
    cv2.fillPoly(img, [np.int32(pts)], top, AA)
    sleeve = tuple(int(c * 0.8) for c in top)
    cv2.line(img, (int(x), int(sh_y + h * 0.02)), (int(x + facing * h * 0.015), int(hip_y + h * 0.05)), sleeve, lw, AA)
    cv2.line(img, (int(x), int(sh_y)), (int(x + facing * h * 0.01), int(hy + r)), (30, 33, 40), lw, AA)
    cv2.circle(img, (int(x), int(hy)), max(1, int(r)), hair, -1, AA)
    cv2.circle(img, (int(x + facing * r * 0.4), int(hy + r * 0.15)), max(1, int(r * 0.65)), (36, 40, 50), -1, AA)
    if hat is not None:
        cv2.ellipse(img, (int(x), int(hy - r * 0.2)), (max(1, int(r * 1.05)), max(1, int(r * 0.8))), 0, 180, 360, hat, -1, AA)


def draw_head(img, cx, cy, s, u, mouth=0.0, glow=0.0):
    """Крупная голова Веры. u: 0 — профиль влево, 1 — анфас. s — высота головы."""
    ax, ay = 0.34 * s, 0.48 * s
    I = lambda v: int(round(v))
    hair_d = tuple(int(c * 0.7) for c in HAIR)
    # хвост (за головой; при повороте уходит за лицо)
    tail_x = cx + (0.40 * s) * (1 - u) + 0.05 * s * u
    cv2.ellipse(img, (I(tail_x), I(cy + 0.18 * s)), (I(0.11 * s), I(0.36 * s)), -18 * (1 - u), 0, 360, hair_d, -1, AA)
    # шея
    cv2.rectangle(img, (I(cx - 0.12 * s), I(cy + 0.25 * s)), (I(cx + 0.13 * s), I(cy + 0.8 * s)), tuple(int(c * 0.6) for c in SKIN), -1)
    # затылок
    cv2.ellipse(img, (I(cx + 0.07 * s * (1 - u)), I(cy - 0.03 * s)), (I(ax * 1.07), I(ay * 1.03)), 0, 0, 360, HAIR, -1, AA)
    # лицо + свет: светлая сторона слева (окна/фонари)
    x0, y0 = I(cx - ax * 1.4), I(cy - ay * 1.1)
    x1, y1 = I(cx + ax * 1.4), I(cy + ay * 1.1)
    x0c, y0c, x1c, y1c = max(0, x0), max(0, y0), min(img.shape[1], x1), min(img.shape[0], y1)
    mask = np.zeros((img.shape[0], img.shape[1]), np.uint8)
    cv2.ellipse(mask, (I(cx), I(cy)), (I(ax), I(ay)), 0, 0, 360, 255, -1, AA)
    if u < 0.6:  # нос в профиль
        k = 1 - u / 0.6
        p = [(cx - ax + 0.02 * s, cy - 0.02 * s), (cx - ax - 0.07 * s * k, cy + 0.10 * s), (cx - ax + 0.03 * s, cy + 0.15 * s)]
        cv2.fillPoly(mask, [np.int32(p)], 255, AA)
    roi = (slice(y0c, y1c), slice(x0c, x1c))
    xs = np.linspace(x0c, x1c, x1c - x0c, dtype=np.float32)
    shade = np.clip(1.15 - (xs - (cx - ax)) / (2 * ax) * (0.75 - 0.35 * u), 0.35, 1.2)[None, :, None]
    face = np.array(SKIN, np.float32)[None, None] * shade * (1 + glow * 0.25)
    m = mask[roi].astype(np.float32)[..., None] / 255
    img[roi] = (img[roi] * (1 - m) + face * m).astype(np.uint8)
    # чёлка/линия волос
    cv2.ellipse(img, (I(cx + 0.05 * s * (1 - u)), I(cy - 0.27 * s)), (I(ax * 1.04), I(0.2 * s)), 0, 180, 360, HAIR, -1, AA)
    fx = cx - (1 - u) * 0.2 * s
    ey = cy - 0.02 * s
    eye_c = (200, 205, 210) if glow <= 0 else (220, 225, 230)
    eyes = [(fx - (0.04 + 0.10 * u) * s, 0.6 + 0.4 * u)]
    if u > 0.3:
        eyes.append((fx + 0.14 * s * u, min(1.0, (u - 0.3) / 0.5)))
    for ex, k in eyes:
        cv2.ellipse(img, (I(ex), I(ey)), (I(0.05 * s * k), I(0.018 * s)), 0, 0, 360, eye_c, -1, AA)
        cv2.circle(img, (I(ex - 0.008 * s * (1 - u)), I(ey)), I(0.015 * s), (40, 50, 50), -1, AA)
        cv2.line(img, (I(ex - 0.055 * s * k), I(ey - 0.06 * s)), (I(ex + 0.05 * s * k), I(ey - 0.065 * s)), hair_d, max(2, I(0.012 * s)), AA)
    if glow > 0:  # едва заметный отсвет в глазах
        for ex, k in eyes:
            cv2.circle(img, (I(ex + 0.01 * s), I(ey - 0.006 * s)), max(1, I(0.005 * s)), (255, 255, 255), -1, AA)
    mx = fx - (1 - u) * 0.02 * s
    mw = 0.1 * s * (0.45 + 0.55 * u)
    mh = 0.004 * s + mouth * 0.045 * s
    cv2.ellipse(img, (I(mx), I(cy + 0.25 * s)), (I(mw / 2), max(1, I(mh / 2))), 0, 0, 360, (55, 55, 95), -1, AA)
    cv2.line(img, (I(fx + 0.01 * s * u), I(cy + 0.04 * s)), (I(fx - 0.01 * s), I(cy + 0.14 * s)), tuple(int(c * 0.65) for c in SKIN), max(1, I(0.006 * s)), AA)


def torso(img, cx, top, s, u):
    """Плечи: парка поверх зелёной формы."""
    wd = s * (0.95 + 0.55 * u)
    pts = [(cx - wd * 0.5, top + 0.18 * s), (cx + wd * 0.5, top + 0.18 * s), (cx + wd * 0.75, H + 10), (cx - wd * 0.75, H + 10)]
    cv2.fillPoly(img, [np.int32(pts)], PARKA, AA)
    cv2.ellipse(img, (int(cx), int(top + 0.18 * s)), (int(wd * 0.5), int(0.12 * s)), 0, 180, 360, PARKA, -1, AA)
    v = [(cx - 0.16 * s, top + 0.05 * s), (cx + 0.16 * s, top + 0.05 * s), (cx, top + 0.42 * s)]
    cv2.fillPoly(img, [np.int32(v)], UNIFORM, AA)
    cv2.line(img, (int(cx - 0.16 * s), int(top + 0.05 * s)), (int(cx), int(top + 0.42 * s)), (24, 50, 20), 3, AA)


# ---------- окружение ----------
class Building:
    def __init__(self, rng, x0, y0, x1, y1, floors, cols, lit_p, col=FACADE):
        self.box = (x0, y0, x1, y1)
        self.col = col
        fh, cw = (y1 - y0) / floors, (x1 - x0) / cols
        self.fh = fh
        self.wins = []
        for f in range(floors):
            for c in range(cols):
                wx, wy = x0 + c * cw + cw * 0.22, y0 + f * fh + fh * 0.25
                r = (int(wx), int(wy), int(wx + cw * 0.56), int(wy + fh * 0.5))
                lit = rng.random() < lit_p
                self.wins.append([r, lit, WARM[rng.integers(len(WARM))], f, c, 1.0])

    def draw_facade(self, img):
        x0, y0, x1, y1 = map(int, self.box)
        cv2.rectangle(img, (x0, y0), (x1, y1), self.col, -1)
        y = y0
        while y < y1:
            cv2.line(img, (x0, int(y)), (x1, int(y)), tuple(c - 6 for c in self.col), 1)
            y += self.fh
        for w in self.wins:
            cv2.rectangle(img, w[0][:2], w[0][2:], WIN_OFF, -1)

    def draw_lit(self, img, glow=None):
        for r, lit, col, *_rest in self.wins:
            k = _rest[2]
            if lit and k > 0:
                c = tuple(int(v * k) for v in col)
                cv2.rectangle(img, r[:2], r[2:], c, -1)
                if glow is not None:
                    cv2.rectangle(glow, (r[0] - 3, r[1] - 3), (r[2] + 3, r[3] + 3), tuple(int(v * 0.25 * k) for v in col), -1)


def sky(h, w, rng, stars=60):
    img = gradient(h, w, SKY_TOP, SKY_BOT)
    for _ in range(stars):
        x, y = int(rng.random() * w), int(rng.random() * h * 0.5)
        b = int(60 + rng.random() * 80)
        img[y, x] = (b, b, b)
    return img


def lamp_post(img, x, ytop, yb):
    cv2.line(img, (x, ytop), (x, yb), (12, 12, 14), 6, AA)
    cv2.line(img, (x, ytop), (x + 40, ytop - 10), (12, 12, 14), 5, AA)
    cv2.ellipse(img, (x + 46, ytop - 6), (16, 6), 0, 0, 360, (120, 190, 240), -1, AA)


def car(img, x, y, w, col=(20, 20, 24)):
    h = w * 0.32
    cv2.rectangle(img, (int(x), int(y - h * 0.55)), (int(x + w), int(y)), col, -1)
    pts = [(x + w * 0.2, y - h * 0.55), (x + w * 0.32, y - h), (x + w * 0.7, y - h), (x + w * 0.82, y - h * 0.55)]
    cv2.fillPoly(img, [np.int32(pts)], col, AA)
    for wx in (x + w * 0.2, x + w * 0.8):
        cv2.circle(img, (int(wx), int(y)), int(h * 0.22), (8, 8, 10), -1, AA)


DOORS = [380, 960, 1540]
GROUND_Y = 560


class Yard:
    """Двор у дома: фасад с тремя подъездами, фонари, машины, площадка."""

    def __init__(self, seed, lit_p):
        rng = np.random.default_rng(seed)
        self.bld = Building(rng, -40, -200, W + 40, GROUND_Y, 9, 18, lit_p)
        # над входом в подъезд (дверь, козырёк, лампа) окон нет
        self.bld.wins = [w for w in self.bld.wins
                         if not any(w[0][2] > dx - 100 and w[0][0] < dx + 100 and w[0][3] > GROUND_Y - 215 for dx in DOORS)]
        img = np.zeros((H, W, 3), np.uint8)
        img[:] = FACADE
        self.bld.draw_facade(img)
        img[GROUND_Y:] = gradient(H - GROUND_Y, W, (28, 28, 32), (18, 18, 22))
        cv2.rectangle(img, (0, GROUND_Y), (W, GROUND_Y + 14), (34, 32, 34), -1)  # отмостка
        for dx in DOORS:
            cv2.rectangle(img, (dx - 45, GROUND_Y - 150), (dx + 45, GROUND_Y), (14, 14, 16), -1)
            cv2.rectangle(img, (dx - 75, GROUND_Y - 175), (dx + 75, GROUND_Y - 160), (22, 22, 24), -1)
            cv2.circle(img, (dx, GROUND_Y - 190), 7, (140, 200, 240), -1, AA)
        for x in (60, 230):
            car(img, x, GROUND_Y + 95, 150)
        car(img, 1700, GROUND_Y + 95, 160, (22, 20, 26))
        # горка/турник справа на дальнем плане
        cv2.line(img, (1180, 610), (1215, 540), SIL, 4, AA)
        cv2.line(img, (1250, 610), (1215, 540), SIL, 4, AA)
        cv2.line(img, (1215, 540), (1335, 540), SIL, 4, AA)
        cv2.line(img, (1335, 540), (1300, 610), SIL, 4, AA)
        cv2.line(img, (1335, 540), (1370, 610), SIL, 4, AA)
        for x in (110, 1820):
            lamp_post(img, x, 300, 700)
        self.base = img
        lm = np.full((H, W, 3), 0.55, np.float32)
        glow = np.zeros((H, W, 3), np.float32)
        for x in (156, 1866):
            lm += blob(H, W, x, 760, 420, 170, (0.6, 1.0, 1.5))
            glow += blob(H, W, x, 294, 60, 40, (60, 120, 170))
        for dx in DOORS:
            lm += blob(H, W, dx, GROUND_Y - 120, 150, 140, (0.45, 0.7, 0.95))
            lm += blob(H, W, dx, GROUND_Y + 60, 170, 60, (0.3, 0.5, 0.7))
            glow += blob(H, W, dx, GROUND_Y - 190, 30, 30, (60, 110, 150))
        lm += blob(H, W, W * 0.5, H * 0.85, W * 0.6, 300, (0.25, 0.2, 0.15))  # луна на асфальте
        self.lmap = to_lmap(lm)
        self.glow = np.clip(glow, 0, 255).astype(np.uint8)


def figure_h(y):
    return 60 + (y - 600) * 0.48


def crowd_grid(rows=10, cols=19, y0=640, y1=990, skip=None):
    pts = []
    for r in range(rows):
        y = lerp(y0, y1, r / (rows - 1))
        h = figure_h(y)
        sp = h * 0.47
        for c in range(cols):
            if skip and (r, c) in skip:
                continue
            x = W / 2 + (c - (cols - 1) / 2) * sp + (r % 2) * sp * 0.4
            pts.append((x, y, h, r, c))
    return pts


# ======================= ПЛАНЫ =======================
class Shot:
    t0 = t1 = 0.0

    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def k(self, t):
        return (t - self.t0) / (self.t1 - self.t0)


class Exterior(Shot):
    """0:00 Общий план: панельки Бибирева, 23:47."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        rng = np.random.default_rng(1)
        img = sky(H, W, rng)
        far = [Building(rng, x, 380 + rng.integers(-60, 40), x + 260, 820, 16, 6, 0.25, (30, 26, 28)) for x in range(-100, W, 300)]
        for b in far:
            b.draw_facade(img)
        self.near = [Building(rng, 120, 250, 860, 900, 17, 14, 0.45), Building(rng, 1080, 300, 1820, 900, 17, 14, 0.4)]
        for b in self.near:
            b.draw_facade(img)
        glow = np.zeros_like(img)
        for b in far:
            b.draw_lit(img, glow)
        for b in self.near:
            b.draw_lit(img, glow)
        img[900:] = gradient(H - 900, W, (26, 26, 30), (14, 14, 18))
        for x in (40, 960, 1880):
            lamp_post(img, x, 760, 980)
        lm = np.full((H, W, 3), 1.0, np.float32)
        for x in (86, 1006, 1926):
            lm += blob(H, W, x, 960, 200, 70, (0.8, 1.4, 2.0))
        img = apply_light(img, to_lmap(lm))
        glow = cv2.GaussianBlur(glow, (0, 0), 6)
        self.img = cv2.add(img, glow)

    def frame(self, t):
        k = ease(self.k(t))
        return camera(self.img, 1.0 + 0.07 * k, W / 2, H * 0.52)


class YardEmpty(Shot):
    """0:06 Пустой двор стоит и ждёт."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.y = Yard(2, 0.4)
        img = self.y.base.copy()
        glow = self.y.glow.copy()
        self.y.bld.draw_lit(img, glow)
        self.img = apply_light(img, self.y.lmap, cv2.GaussianBlur(glow, (0, 0), 5))

    def frame(self, t):
        k = ease(self.k(t))
        return camera(self.img, 1.12, lerp(W * 0.45, W * 0.56, k), H * 0.5)


class WindowsOff(Shot):
    """0:17 Окна гаснут по одному — будто кто-то идёт по дому."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        rng = np.random.default_rng(3)
        self.b = Building(rng, -20, -40, W + 20, H + 40, 8, 12, 0.55)
        self.bg = np.zeros((H, W, 3), np.uint8)
        self.b.draw_facade(self.bg)
        lit = [w for w in self.b.wins if w[1]]
        # «обход» дома змейкой сверху вниз
        lit.sort(key=lambda w: (w[3], w[4] if w[3] % 2 == 0 else -w[4]))
        start, end = t0 + 0.9, t1 - 0.6
        for i, w in enumerate(lit):
            w.append(start + (end - start) * i / max(1, len(lit) - 1))
        self.lit = lit
        lm = np.full((H, W, 3), 0.9, np.float32) + blob(H, W, W * 0.2, H * 0.1, 900, 600, (0.4, 0.3, 0.2))
        self.lmap = to_lmap(lm)

    def frame(self, t):
        img = self.bg.copy()
        glow = np.zeros_like(img)
        for w in self.lit:
            w[5] = 1.0 - min(1.0, max(0.0, (t - w[6]) / 0.12))
        self.b.draw_lit(img, glow)
        img = apply_light(img, self.lmap, cv2.GaussianBlur(glow, (0, 0), 8))
        return camera(img, 1.03 + 0.04 * ease(self.k(t)), W / 2, H / 2)


class Balcony(Shot):
    """Вид с балкона девятого этажа. crowd=True — толпа внизу."""

    def __init__(self, t0, t1, crowd=False):
        super().__init__(t0, t1)
        rng = np.random.default_rng(4)
        img = sky(H, W, rng, 30)
        b = Building(rng, 200, -60, 1720, 330, 6, 16, 0.0)
        b.draw_facade(img)
        img[330:] = gradient(H - 330, W, (26, 26, 30), (20, 20, 24))
        for x, y in ((300, 520), (520, 540), (1500, 500)):
            cv2.rectangle(img, (x, y), (x + 110, y + 50), (14, 14, 18), -1)
        cv2.rectangle(img, (760, 420), (1100, 470), (30, 30, 34), 3)  # песочница/площадка
        lm = np.full((H, W, 3), 0.6, np.float32)
        for x in (180, 1750):
            lm += blob(H, W, x, 600, 330, 230, (0.6, 1.0, 1.5))
        lm += blob(H, W, 960, 380, 900, 120, (0.15, 0.25, 0.4))
        self.lmap = to_lmap(lm)
        self.crowd = []
        if crowd:
            for r in range(9):
                for c in range(24):
                    x = 470 + c * 42 + (r % 2) * 18 + rng.normal(0, 2)
                    y = 480 + r * 30
                    self.crowd.append((x, y, 30 + r * 1.5, outfit(rng)))
        self.bg = img
        rail = np.zeros((H, W), np.uint8)
        cv2.rectangle(rail, (0, 760), (W, 790), 255, -1)
        cv2.rectangle(rail, (0, 1010), (W, H), 255, -1)
        for x in range(30, W, 70):
            cv2.rectangle(rail, (x, 760), (x + 12, 1010), 255, -1)
        self.rail = cv2.merge([rail] * 3)

    def frame(self, t):
        img = self.bg.copy()
        for x, y, h, wear in self.crowd:
            person(img, x, y, h, facing=-1, wear=wear)
            cv2.circle(img, (int(x), int(y - h * 0.93)), max(2, int(h * 0.08)), (52, 54, 62), -1, AA)
        img = apply_light(img, self.lmap)
        img = cv2.subtract(img, self.rail)
        sway = math.sin(t * 0.7) * 6 + math.sin(t * 1.9) * 2
        return camera(img, 1.05, W / 2 + sway, H / 2 + math.sin(t * 0.5) * 4, rot=math.sin(t * 0.4) * 0.3)


class Neighbor(Shot):
    """0:37 Соседка выходит из подъезда и идёт «по линейке»."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.y = Yard(5, 0.0)

    def pos(self, t):
        start = self.t0 + 1.2
        if t < start:
            return DOORS[2], GROUND_Y + 30, 0.0, True
        n = (t - start) / 1.3  # шагов: ровно 1 шаг в 1.3 с
        step_i, frac = int(n), n - int(n)
        dist = (step_i + ease(frac)) * 48
        x = DOORS[2] - dist * 0.85
        y = GROUND_Y + 30 + dist * 0.45
        return x, y, (step_i + frac) * math.pi, False

    def frame(self, t):
        img = self.y.base.copy()
        x, y, ph, inside = self.pos(t)
        d0 = DOORS[2]
        if t > self.t0 + 0.4:  # дверь открыта — тёплый проём
            cv2.rectangle(img, (d0 - 40, GROUND_Y - 145), (d0 + 40, GROUND_Y), (60, 110, 150), -1)
        if not inside:
            person(img, x, y, figure_h(y + 60), facing=-1, phase=ph, kind="robe")
        img = apply_light(img, self.y.lmap, self.y.glow)
        k = ease(self.k(t))
        return camera(img, 1.5, lerp(d0 - 120, x - 40, k), lerp(GROUND_Y - 40, y - 60, k))


class CrowdGathers(Shot):
    """0:48 Подъезды выпускают людей: сто, двести. Все лицом на запад."""

    def __init__(self, t0, t1, rng_seed=6):
        super().__init__(t0, t1)
        self.y = Yard(rng_seed, 0.0)
        rng = np.random.default_rng(rng_seed)
        pts = crowd_grid()
        self.people = []
        for (x, y, h, r, c) in pts:
            door = DOORS[min(2, int(x / (W / 3)))]
            t_out = t0 + 0.3 + rng.random() * 7.6
            dur = math.hypot(x - door, y - GROUND_Y) / 160
            self.people.append(dict(x=x, y=y, door=door, t_out=t_out, dur=dur, kind="generic", wear=outfit(rng)))
        # соседка уже стоит впереди
        self.people.append(dict(x=W * 0.33, y=760, door=DOORS[2], t_out=-99, dur=1, kind="robe", wear=None))

    def placed(self, p, t):
        k = (t - p["t_out"]) / p["dur"]
        if k < 0:
            return None
        k = min(k, 1.0)
        x = lerp(p["door"], p["x"], k)
        y = lerp(GROUND_Y + 10, p["y"], k)
        ph = None if k >= 1 else (t - p["t_out"]) * 5.0
        return x, y, ph

    def frame(self, t):
        img = self.y.base.copy()
        live = []
        for p in self.people:
            s = self.placed(p, t)
            if s:
                live.append((s[1], s[0], s[2], p["kind"], p["wear"]))
        for y, x, ph, kind, wear in sorted(live, key=lambda a: a[0]):
            person(img, x, y, figure_h(y), facing=-1, phase=ph, kind=kind, wear=wear)
        img = apply_light(img, self.y.lmap, self.y.glow)
        k = ease(self.k(t))
        return camera(img, lerp(1.0, 1.08, k), W / 2, H / 2 + 20)


class VeraEnters(Shot):
    """1:05 Вера входит в толпу: рыжий хвост, зелёная форма."""
    target = (W * 0.52, 815)

    def __init__(self, t0, t1, cam="wide"):
        super().__init__(t0, t1)
        self.y = Yard(7, 0.0)
        self.cam = cam
        pts = crowd_grid()
        tx, ty = self.target
        rng = np.random.default_rng(17)
        self.crowd = [(x, y, h, outfit(rng)) for (x, y, h, r, c) in pts if math.hypot(x - tx, (y - ty) * 2.5) > 45]
        self.fg = [outfit(rng), outfit(rng)]
        self.static = self.y.base.copy()
        lm = self.y.lmap.astype(np.float32) / 128
        lm += blob(H, W, tx, ty - 60, 120, 160, (0.6, 0.8, 1.1))
        self.lmap = to_lmap(lm)

    def vera(self, t):
        start, stop = self.t0 + 0.6, self.t0 + 6.5
        if self.cam != "wide":
            return self.target[0], self.target[1], None
        k = min(1.0, max(0.0, (t - start) / (stop - start)))
        x = lerp(W + 60, self.target[0], k)
        y = lerp(700, self.target[1], k)
        return x, y, (None if k >= 1 else (t - start) * 4.0)

    def frame(self, t):
        img = self.static.copy()
        vx, vy, ph = self.vera(t)
        items = [(y, x, None, "generic", w) for (x, y, h, w) in self.crowd] + [(vy, vx, ph, "vera", None)]
        for y, x, p, kind, w in sorted(items, key=lambda a: a[0]):
            person(img, x, y, figure_h(y), facing=-1, phase=p, kind=kind, wear=w)
        if self.cam == "push":  # крупные фигуры на переднем плане
            for x, w in zip((vx - 330, vx + 300), self.fg):
                person(img, x, 1150, 520, facing=-1, wear=w)
        img = apply_light(img, self.lmap, self.y.glow)
        k = ease(self.k(t))
        if self.cam == "wide":
            return camera(img, lerp(1.15, 1.45, k), lerp(W * 0.62, vx, 0.6), lerp(H * 0.55, vy - 90, k))
        return camera(img, lerp(1.6, 2.9, k), vx + 10, lerp(vy - 70, vy - 110, k))


class Elevator(Shot):
    """1:19 Лифт стоит, горит красным."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        img = gradient(H, W, (40, 40, 44), (26, 26, 30))
        cv2.rectangle(img, (620, 180), (1300, 1080), (24, 24, 26), -1)
        cv2.rectangle(img, (650, 210), (1270, 1080), (70, 66, 66), -1)
        cv2.line(img, (960, 210), (960, 1080), (30, 30, 32), 4)
        for x in range(680, 1260, 30):
            cv2.line(img, (x, 220), (x, 1080), (62, 58, 58), 1)
        cv2.rectangle(img, (1380, 520), (1450, 660), (50, 50, 54), -1)
        img[900:] = gradient(H - 900, W, (30, 30, 34), (18, 18, 22))
        self.bg = img
        red = blob(H, W, 960, 120, 520, 260, (10, 18, 120)) + blob(H, W, 1415, 560, 140, 140, (8, 14, 110))
        self.red = np.clip(red, 0, 255).astype(np.uint8)

    def frame(self, t):
        pulse = 0.75 + 0.25 * math.sin(t * 3.2)
        img = cv2.add(self.bg, cv2.convertScaleAbs(self.red, alpha=pulse))
        cv2.rectangle(img, (880, 90), (1040, 150), (10, 10, 20), -1)
        cv2.putText(img, "--", (920, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (40, 40, int(200 * pulse + 40)), 5, AA)
        cv2.circle(img, (1415, 560), 18, (40, 40, int(170 * pulse + 60)), -1, AA)
        return camera(img, 1.05 + 0.08 * ease(self.k(t)), W / 2, H / 2)


class Stairs(Shot):
    """1:23 Девять этажей вниз, на каждом — открытая дверь и пустая квартира."""
    FLOORS = 4

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        Ht = H * self.FLOORS
        img = gradient(Ht, W, (34, 34, 38), (30, 30, 34))
        for f in range(self.FLOORS):
            y0 = f * H
            land = y0 + 760
            cv2.rectangle(img, (0, land), (W, land + 40), (20, 20, 24), -1)
            # дверь квартиры, приоткрытая, тёплый свет
            cv2.rectangle(img, (300, land - 470), (560, land), (16, 16, 18), -1)
            cv2.rectangle(img, (310, land - 460), (550, land), (50, 90, 120), -1)
            pts = [(550, land - 460), (690, land - 500), (690, land + 30), (550, land)]
            cv2.fillPoly(img, [np.int32(pts)], (24, 22, 24), AA)
            light = [(310, land), (550, land), (760, land + 40), (170, land + 40)]
            cv2.fillPoly(img, [np.int32(light)], (46, 70, 90), AA)
            cv2.putText(img, str(9 - f * 2), (1650, y0 + 300), cv2.FONT_HERSHEY_SIMPLEX, 4, (60, 60, 66), 10, AA)
            # пролёт лестницы вниз
            for i in range(12):
                sx = 900 + i * 70
                sy = land + 40 + i * 24
                cv2.rectangle(img, (sx, sy), (sx + 70, y0 + H + 760 if f < self.FLOORS - 1 else Ht), (22, 22, 26), -1)
            cv2.line(img, (900, land - 120), (1740, land + 170), (14, 14, 16), 8, AA)
            for i in range(0, 12, 2):
                cv2.line(img, (900 + i * 70, land - 120 + i * 24 + 6), (900 + i * 70, land + 40 + i * 24), (14, 14, 16), 4, AA)
        self.img = img

    def frame(self, t):
        k = self.k(t)
        cy = lerp(H * 0.45, H * (self.FLOORS - 0.55), k)
        shake = math.sin(t * 15) * 8
        z = 1.1
        cy = min(max(cy, H / 2), self.img.shape[0] - H / 2)
        crop = self.img[int(cy - H / 2): int(cy - H / 2) + H]
        return camera(crop, z, W / 2 + shake, H / 2 + abs(math.sin(t * 7.5)) * 10)


class Sleeve(Shot):
    """1:35 Крупно: Вера в профиль, я беру её за рукав."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        rng = np.random.default_rng(9)
        bg = gradient(H, W, (30, 28, 30), (16, 16, 20))
        for _ in range(40):
            x, y = rng.random() * W * 1.2 - 100, 760 + rng.random() * 200
            person(bg, x, y + 500, 900 + rng.random() * 300, facing=-1, col=(12, 12, 14))
        lm = np.full((H, W, 3), 0.8, np.float32) + blob(H, W, 300, 200, 500, 400, (0.4, 0.8, 1.2))
        bg = apply_light(bg, to_lmap(lm))
        for x, y, r in ((200, 180, 70), (1700, 260, 90), (1400, 120, 50)):
            bg = cv2.add(bg, np.clip(blob(H, W, x, y, r, r, (40, 90, 130)), 0, 255).astype(np.uint8))
        self.bg = cv2.GaussianBlur(bg, (0, 0), 10)

    def frame(self, t):
        img = self.bg.copy()
        cx, cy, s = 900, 360, 360
        torso(img, cx + 40, cy + 0.38 * s, s * 1.15, 0.0)
        draw_head(img, cx, cy, s, 0.0)
        # рука героя появляется справа и сжимает рукав
        k = ease((t - (self.t0 + 1.0)) / 0.9)
        if k > 0:
            gx, gy = lerp(W + 200, 1020, k), 880
            cv2.line(img, (int(gx + 60), int(gy + 10)), (W + 50, int(gy + 80)), (30, 30, 34), 120, AA)
            cv2.ellipse(img, (int(gx), int(gy)), (70, 55), 0, 0, 360, (120, 130, 150), -1, AA)
            for i in range(4):
                cv2.ellipse(img, (int(gx - 55), int(gy - 35 + i * 24)), (28, 12), 0, 0, 360, (130, 140, 160), -1, AA)
        breath = math.sin(t * 0.9) * 3
        return camera(img, 1.06 + 0.05 * ease(self.k(t)), W / 2, H / 2 + breath)


class Pulse(Shot):
    """1:50 Пальцы холодные. Пульс ровный, как метроном."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        bg = gradient(H, W, (24, 34, 22), (14, 20, 14))
        cv2.rectangle(bg, (0, 380), (W, 700), (132, 128, 128), -1)  # запястье
        cv2.ellipse(bg, (W // 2, 380), (W, 40), 0, 0, 180, (112, 108, 110), -1, AA)
        cv2.rectangle(bg, (0, 330), (520, 760), (40, 82, 34), -1)   # манжета формы
        cv2.rectangle(bg, (500, 330), (530, 760), (28, 60, 24), -1)
        for i in range(2):  # мои пальцы сверху
            x = 980 + i * 110
            cv2.ellipse(bg, (x, 300), (60, 260), 0, 0, 360, (128, 136, 158), -1, AA)
            cv2.ellipse(bg, (x, 520), (52, 40), 0, 0, 360, (140, 148, 170), -1, AA)
        cv2.line(bg, (1700, -50), (1180, 300), (30, 30, 34), 260, AA)
        lm = np.full((H, W, 3), 0.7, np.float32) + blob(H, W, 600, 300, 900, 500, (0.4, 0.4, 0.5))
        self.bg = apply_light(bg, to_lmap(lm))
        self.flash = np.clip(blob(H, W, 1040, 560, 260, 120, (30, 30, 40)), 0, 255).astype(np.uint8)

    def frame(self, t):
        beat = (t - (self.t0 + 1.6)) % 1.0
        on = t > self.t0 + 1.6
        p = math.exp(-beat * 9) if on else 0
        img = self.bg.copy()
        if p > 0.01:
            img = cv2.add(img, cv2.convertScaleAbs(self.flash, alpha=p))
        return camera(img, 1.15 + 0.03 * p + 0.06 * ease(self.k(t)), W / 2, H / 2)


class Faces(Shot):
    """1:55 Сотни лиц, у всех одинаковое выражение. Они слушают."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        Wp = int(W * 1.6)
        img = gradient(H, Wp, (22, 20, 22), (12, 12, 16))
        rows = [(360, 210, 0.55), (640, 280, 0.75), (980, 380, 1.0)]
        for ry, s, light in rows:
            sp = s * 0.95
            n = int(Wp / sp) + 2
            for i in range(n):
                cx = i * sp + (0 if ry != 640 else sp / 2)
                tmp = img
                cv2.rectangle(tmp, (int(cx - s * 0.5), int(ry + s * 0.35)), (int(cx + s * 0.5), H), (18, 18, 22), -1)
                cv2.ellipse(tmp, (int(cx), int(ry - s * 0.05)), (int(s * 0.36), int(s * 0.5)), 0, 0, 360, (20, 20, 24), -1, AA)
                face_s = s
                ax, ay = int(face_s * 0.33), int(face_s * 0.46)
                c = tuple(int(v * light * 0.7) for v in SKIN)
                cv2.ellipse(tmp, (int(cx), int(ry)), (ax, ay), 4, 0, 360, c, -1, AA)
                cv2.ellipse(tmp, (int(cx), int(ry - s * 0.28)), (int(ax * 1.05), int(s * 0.2)), 4, 180, 360, (20, 20, 24), -1, AA)
                for sx in (-1, 1):
                    ex, ey = int(cx + sx * s * 0.13), int(ry - s * 0.02 + sx * s * 0.01)
                    cv2.ellipse(tmp, (ex, ey), (int(s * 0.045), int(s * 0.015)), 4, 0, 360, (150, 155, 160), -1, AA)
                    cv2.circle(tmp, (ex, ey), max(2, int(s * 0.013)), (30, 30, 34), -1, AA)
                cv2.line(tmp, (int(cx - s * 0.05), int(ry + s * 0.25)), (int(cx + s * 0.05), int(ry + s * 0.26)), (50, 50, 70), max(2, int(s * 0.01)), AA)
        lm = np.full((H, Wp, 3), 0.6, np.float32) + blob(H, Wp, Wp * 0.3, 0, Wp, 700, (0.5, 0.6, 0.8))
        img = apply_light(img, to_lmap(lm))
        self.img = img

    def frame(self, t):
        k = ease(self.k(t))
        return camera(self.img, 1.0, lerp(W * 0.5, self.img.shape[1] - W * 0.5, k), H / 2)


class Turn(Shot):
    """2:05 Вера поворачивает голову и говорит моим голосом."""

    def __init__(self, t0, t1, env):
        super().__init__(t0, t1)
        self.env = env
        bg = gradient(H, W, (24, 22, 26), (12, 12, 16))
        rng = np.random.default_rng(13)
        for _ in range(30):
            x = rng.random() * W
            person(bg, x, 1500, 1100 + rng.random() * 200, facing=-1, col=(10, 10, 12))
        self.bg = cv2.GaussianBlur(bg, (0, 0), 14)

    def frame(self, t):
        img = self.bg.copy()
        u = ease((t - self.t0) / 2.6)
        mouth = 0.0
        if t > 131.5:
            i = int(t * FPS)
            mouth = float(self.env[min(i, len(self.env) - 1)]) if i < len(self.env) else 0.0
        glow = max(0.0, min(1.0, (t - 143.0) / 1.0))
        cx, cy, s = 960, 430, 470
        torso(img, cx + 30 * (1 - u), cy + 0.38 * s, s * 1.15, u)
        draw_head(img, cx, cy, s, u, mouth=mouth, glow=glow)
        k = ease((t - self.t0) / (self.t1 - self.t0))
        z = lerp(1.0, 1.55, k)
        return camera(img, z, cx - 40 * (1 - u), lerp(H / 2, cy + 10, k))


class EndCard(Shot):
    def __init__(self, t0, t1, card):
        super().__init__(t0, t1)
        self.card = card  # BGR + alpha

    def frame(self, t):
        img = np.zeros((H, W, 3), np.uint8)
        a = min(1.0, max(0.0, (t - self.t0 - 0.4) / 0.8)) * min(1.0, max(0.0, (self.t1 - t) / 0.6))
        return cv2.addWeighted(img, 1, self.card, a, 0)
