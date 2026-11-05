"""Декорации: всё рисуется кодом. Кэшируются на процесс (lru_cache)."""
import math
from functools import lru_cache
import numpy as np
import cv2
from .gfx import (Pen, vgrad, solid, radial, rgb, over, paste, rim, tint, BLACK, CHAR, DGREY, GREY, LGREY, DRED,
                  RED, ORANGE, AMBER, WARMW, Layer, font_)
from .config import W, H, FONT_TITLE, FONT_BOLD, FONT_SEMI, FONT_MONO
from . import character as ch

LW, LH = 2304, 1296  # стандартный размер слоя (запас 20% под камеру)


def _noise_tex(w, h, seed, scale=3.0, k=0.06):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (int(h / scale) + 2, int(w / scale) + 2)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 1.2)
    n = cv2.resize(n, (w, h))
    return (n * k)[..., None]


def _stain(w, h, seed, k=0.12):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (h // 40 + 2, w // 40 + 2)).astype(np.float32)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), 20)
    return (n / (np.abs(n).max() + 1e-6) * k)[..., None]


def textured(arr, seed, k=0.05, stain=0.1):
    """Добавить фактуру (бетон/штукатурка) в premult RGBA."""
    a = arr.copy()
    h, w = a.shape[:2]
    m = 1 + _noise_tex(w, h, seed, k=k) + _stain(w, h, seed + 1, k=stain)
    a[..., :3] *= m
    return a


# ======================================================================== CITY
def city_row(w, h, seed, base_y, hmin, hmax, color, win_col, win_prob, wmin=70, wmax=230, win=True,
             detail=True):
    """Ряд зданий: (albedo RGBA, окна RGBA)."""
    r = np.random.default_rng(seed)
    pb = Pen(w, h, ss=1)
    pw = Pen(w, h, ss=1)
    x = -40
    while x < w + 40:
        bw = r.uniform(wmin, wmax)
        bh = r.uniform(hmin, hmax)
        top = base_y - bh
        kc = r.uniform(0.85, 1.12)
        c = tuple(int(v * kc) for v in color)
        pb.rect(x, top, x + bw, h, c)
        if detail:
            kind = r.integers(0, 5)
            if kind == 0:  # антенна
                ax = x + bw * r.uniform(0.2, 0.8)
                pb.rect(ax - 1.5, top - r.uniform(30, 90), ax + 1.5, top, c)
            elif kind == 1:  # ступенчатая крыша
                pb.rect(x + bw * 0.2, top - bh * 0.08, x + bw * 0.8, top, c)
            elif kind == 2:  # бак
                tx = x + bw * r.uniform(0.2, 0.6)
                pb.rect(tx, top - 26, tx + 30, top, c)
                pb.rect(tx + 4, top - 34, tx + 26, top - 26, c)
        if win:
            cw = r.choice([8, 10, 12]); gap = cw * r.uniform(1.6, 2.4)
            rows = int((h - top) / (gap * 1.3))
            cols = int((bw - 16) / gap)
            for i in range(rows):
                for j in range(cols):
                    if r.random() < win_prob:
                        wx = x + 10 + j * gap; wy = top + 14 + i * gap * 1.3
                        if wy > h:
                            break
                        bright = r.uniform(0.35, 1.0)
                        pw.rect(wx, wy, wx + cw, wy + cw * 1.3, tuple(int(v * bright) for v in win_col))
        x += bw + r.uniform(-10, 18)
    return pb.arr(), pw.arr()


def smoke_column(w, h, seed, x, base_y, height, width, color=(46, 40, 40), alpha=0.75, lean=0.3):
    r = np.random.default_rng(seed)
    p = Pen(w, h, ss=1)
    n = 90
    for i in range(n):
        f = i / n
        cx = x + lean * height * f ** 1.5 + r.normal(0, width * 0.15 * (0.3 + f))
        cy = base_y - height * f
        rad = width * (0.25 + 1.4 * f ** 1.2) * r.uniform(0.6, 1.1)
        k = r.uniform(0.75, 1.15)
        p.ellipse(cx, cy, rad, rad * 0.75, tuple(int(v * k) for v in color) + (int(255 * alpha * 0.35),))
    return p.arr(blur=14)


@lru_cache(None)
def city_set(mood):
    """Городская панорама для окна. mood: day | after | hook."""
    w, h = LW, LH
    hz = int(h * 0.62)
    if mood == "day":
        sky = vgrad(w, h, [(0, (70, 72, 78)), (0.45, (128, 120, 112)), (0.62, (176, 150, 120)), (1, (90, 80, 70))])
        cols = [(98, 98, 104), (70, 70, 76), (44, 44, 48)]
        winc, wp = (190, 170, 130), 0.025
    elif mood == "after":
        sky = vgrad(w, h, [(0, (18, 12, 12)), (0.4, (60, 22, 14)), (0.62, (150, 62, 24)), (1, (40, 18, 12))])
        cols = [(46, 26, 22), (30, 20, 18), (16, 13, 13)]
        winc, wp = (200, 110, 50), 0.015
    else:  # hook
        sky = vgrad(w, h, [(0, (10, 8, 10)), (0.35, (40, 14, 12)), (0.6, (120, 40, 18)), (0.68, (170, 74, 28)),
                           (1, (30, 12, 10))])
        cols = [(40, 22, 20), (26, 16, 15), (12, 10, 10)]
        winc, wp = (230, 140, 60), 0.03
    out = {"sky": Layer(solid(w, h, sky), 0.1)}
    rows = [(hz, 120, 300, 0.25, 40, 110), (hz + 70, 180, 420, 0.38, 70, 200), (hz + 190, 260, 600, 0.55, 120, 300)]
    for i, (by, a, b, d, wmin, wmax) in enumerate(rows):
        alb, win = city_row(w, h, 100 + i * 17 + (0 if mood != "hook" else 50), by, a, b, cols[i], winc, wp * (1 + i),
                            wmin=wmin, wmax=wmax)
        if i == 0:
            alb = cv2.GaussianBlur(alb, (0, 0), 1.6)
        out[f"b{i}"] = Layer(alb, d)
        out[f"w{i}"] = Layer(win[..., :3].copy(), d, add=True)
        # «ослепление» окон — маска окон всех зданий (для вспышки)
        out[f"wm{i}"] = Layer(np.repeat(win[..., 3:4], 3, axis=2), d, add=True)
    if mood == "after":
        sm = smoke_column(w, h, 5, w * 0.62, hz + 10, 620, 120, color=(40, 32, 30))
        sm = over(sm, smoke_column(w, h, 6, w * 0.3, hz + 30, 380, 80, color=(34, 28, 28), lean=0.5))
        out["smoke"] = Layer(sm, 0.2)
        out["glow"] = Layer(radial(w, h, w * 0.62, hz, 700, (200, 80, 30), power=2, k=0.55, sy=0.45), 0.2, add=True)
    if mood == "hook":
        out["glow"] = Layer(radial(w, h, w * 0.5, hz - 10, 1100, (220, 90, 30), power=2.2, k=0.6, sy=0.35), 0.15,
                            add=True)
    return out


# ======================================================================== APARTMENT WINDOW VIEW
WIN_RECT = (720, 210, 1640, 900)  # окно в координатах слоя комнаты


@lru_cache(None)
def room_window_set(mood):
    w, h = LW, LH
    x0, y0, x1, y1 = WIN_RECT
    dark = mood == "after"
    wallc = (38, 36, 36) if not dark else (24, 21, 21)
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, wallc)
    # потолок и пол
    p.rect(0, 0, w, 70, tuple(int(v * 0.8) for v in wallc))
    p.rect(0, 1080, w, h, (24, 21, 20) if not dark else (14, 12, 12))
    p.rect(0, 1070, w, 1086, (30, 27, 26))
    # батарея
    for i in range(16):
        bx = 900 + i * 36
        p.rrect(bx, 960, bx + 26, 1050, 6, (52, 50, 50) if not dark else (30, 28, 28))
    # оконный проём (дыра) + откосы
    p.rect(x0 - 40, y0 - 40, x1 + 40, y1 + 50, tuple(int(v * 0.85) for v in wallc))
    p.rect(x0, y0, x1, y1, (0, 0, 0, 0))
    # рамы
    fc = (24, 24, 26)
    for (a, b, c, d) in [(x0, y0, x1, y0 + 26), (x0, y1 - 30, x1, y1), (x0, y0, x0 + 26, y1), (x1 - 26, y0, x1, y1),
                         ((x0 + x1) / 2 - 14, y0, (x0 + x1) / 2 + 14, y1), (x0, y0 + 210, x1, y0 + 232)]:
        p.rect(a, b, c, d, fc)
    # подоконник
    p.rect(x0 - 70, y1, x1 + 70, y1 + 28, (60, 58, 56) if not dark else (34, 32, 31))
    p.rect(x0 - 70, y1 + 28, x1 + 70, y1 + 40, (20, 19, 19))
    # горшок с растением на подоконнике
    p.poly([(x0 + 60, y1 - 60), (x0 + 120, y1 - 60), (x0 + 110, y1), (x0 + 70, y1)], (40, 30, 26))
    for a in range(-3, 4):
        p.line([(x0 + 90, y1 - 60), (x0 + 90 + a * 22, y1 - 130 + abs(a) * 12)], (26, 30, 24), 7)
    alb = p.arr()
    alb = textured(alb, 11, k=0.05, stain=0.12)
    # занавеска слева (ближе к камере)
    pc = Pen(w, h, ss=1)
    for i in range(9):
        cx = 560 + i * 26
        shade = 34 + (i % 3) * 7 if not dark else 20 + (i % 3) * 4
        pc.poly([(cx, 60), (cx + 34, 60), (cx + 44 + i * 2, 1078), (cx - 6 + i * 2, 1078)], (shade, shade - 4, shade - 6))
    curtain = pc.arr(blur=2.0)
    # шкаф/полка справа
    ps = Pen(w, h, ss=1)
    ps.rect(1840, 330, 2304, 1080, (22, 21, 21))
    for yy in (520, 720, 900):
        ps.rect(1840, yy, 2304, yy + 14, (34, 33, 32))
    for i in range(10):
        ps.rect(1870 + i * 34, 440 - (i % 3) * 18, 1896 + i * 34, 520, (30 + i * 3, 26, 24))
    shelf = ps.arr()
    # свет из окна на стену/пол (аддитивно)
    lightc = (150, 128, 100) if mood == "day" else (170, 70, 30)
    spill = radial(w, h, (x0 + x1) / 2, (y0 + y1) / 2 + 80, 1000, lightc, power=2.2, k=0.22, sy=0.9)
    spill += radial(w, h, (x0 + x1) / 2, 1150, 700, lightc, power=2, k=0.25, sy=0.3)
    # люстра (для мигания)
    pl = Pen(w, h, ss=2)
    pl.line([(1180, 0), (1180, 120)], (20, 20, 20), 3)
    pl.poly([(1130, 160), (1230, 160), (1205, 118), (1155, 118)], (36, 34, 32))
    lamp = pl.arr()
    lamp_glow = radial(w, h, 1180, 175, 900, (255, 190, 120), power=2.4, k=0.55, sy=0.85)
    lamp_bulb = radial(w, h, 1180, 168, 60, (255, 230, 190), power=1.5, k=1.6)
    return {
        "room": Layer(alb, 1.0), "curtain": Layer(curtain, 1.12), "shelf": Layer(shelf, 1.08),
        "spill": Layer(spill, 1.0, add=True), "lamp": Layer(lamp, 1.0),
        "lamp_glow": Layer(lamp_glow, 1.0, add=True), "lamp_bulb": Layer(lamp_bulb, 1.0, add=True),
    }


@lru_cache(None)
def table_fg():
    """Стол на переднем плане с телефоном (размыт — глубина резкости)."""
    w, h = LW, LH
    p = Pen(w, h, ss=1)
    p.poly([(0, 1000), (900, 980), (1000, 1296), (0, 1296)], (30, 24, 20))
    p.rect(0, 980, 960, 1000, (40, 32, 26))
    # телефон
    p.rrect(430, 1010, 560, 1050, 10, (12, 12, 14))
    # кружка
    p.rrect(180, 900, 270, 1000, 12, (60, 56, 54))
    p.rect(270, 930, 300, 975, (50, 46, 44))
    a = p.arr(blur=5.0)
    glow = radial(w, h, 495, 1030, 140, (160, 190, 255), power=2, k=0.0)
    return Layer(a, 1.35), glow


# ======================================================================== PHONE CLOSE-UP
PHW, PHH = 520, 1060


def _warn_tri(p, x, y, s, col):
    p.poly([(x, y - s), (x + s * 1.1, y + s * 0.85), (x - s * 1.1, y + s * 0.85)], col)
    p.rect(x - s * 0.1, y - s * 0.4, x + s * 0.1, y + s * 0.35, (20, 6, 6))
    p.ellipse(x, y + s * 0.58, s * 0.12, s * 0.12, (20, 6, 6))


def phone_screen(state, t=0.0, prog=1.0, extra=None):
    """Экран телефона (premult RGBA, PHW x PHH). state: lock|notif|alert|nosignal|calling|msg|final."""
    p = Pen(PHW, PHH, ss=2)
    sw, sh = PHW, PHH
    # обои
    p.rect(0, 0, sw, sh, (14, 14, 20))
    for i in range(12):
        p.ellipse(sw * 0.7, sh * 0.75, 380 - i * 28, 380 - i * 28, (18 + i * 2, 16 + i, 26 + i * 2))
    # статус-бар
    nosig = state in ("nosignal", "calling", "final")
    p.text(34, 30, "14:12" if state not in ("final",) else "14:59", FONT_SEMI, 26, (230, 230, 235))
    if nosig:
        p.text(sw - 36, 30, "Нет сети", FONT_SEMI, 22, (230, 90, 80), anchor="ra")
    else:
        for i in range(4):
            p.rect(sw - 120 + i * 12, 50 - i * 6, sw - 112 + i * 12, 56, (230, 230, 235))
    p.rrect(sw - 70, 36, sw - 30, 56, 4, (230, 230, 235))
    if state in ("lock", "notif"):
        p.text(sw / 2, 230, "14:12", FONT_TITLE, 120, (235, 235, 240), anchor="mm")
        p.text(sw / 2, 315, "вторник, 14 октября", FONT_SEMI, 26, (200, 200, 210), anchor="mm")
    if state == "notif":
        y = -260 + 300 * prog + 90
        p.rrect(22, y, sw - 22, y + 190, 26, (60, 16, 16, 240))
        _warn_tri(p, 70, y + 52, 22, (255, 210, 60))
        p.text(110, y + 36, "ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ", FONT_BOLD, 24, (255, 235, 230))
        p.text(44, y + 92, "Внимание! Чрезвычайная", FONT_SEMI, 24, (245, 225, 220))
        p.text(44, y + 126, "ситуация. Откройте сообщение.", FONT_SEMI, 24, (245, 225, 220))
    if state in ("alert", "msg"):
        p.rect(0, 0, sw, sh, (40, 8, 8))
        p.rect(0, 80, sw, 250, (150, 20, 18))
        _warn_tri(p, sw / 2, 150, 40, (255, 220, 70))
        p.text(sw / 2, 225, "ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ", FONT_BOLD, 28, (255, 240, 235), anchor="mm")
        if state == "alert":
            lines = ["ВНИМАНИЕ!", "ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ", "В ВАШЕМ РАЙОНЕ.", "", "Оставайтесь в помещении.",
                     "Ожидайте дальнейших", "указаний."]
            for i, s in enumerate(lines):
                p.text(sw / 2, 330 + i * 50, s, FONT_BOLD if i < 3 else FONT_SEMI, 32 if i < 3 else 28,
                       (255, 235, 230), anchor="mm")
        else:
            lines = [("Оставайтесь внутри", "капитальных зданий."), ("Следите за официальными", "сообщениями."),
                     ("Не выходите без", "необходимости.")]
            for i, (a, b) in enumerate(lines):
                vis = extra[i] if extra else 1.0
                if vis <= 0:
                    continue
                c = tuple(int(v * vis) for v in (255, 235, 230))
                y = 330 + i * 150
                p.text(48, y, "•", FONT_BOLD, 34, (255, 200, 70) if vis > .5 else c)
                p.text(84, y, a, FONT_BOLD, 32, c)
                p.text(84, y + 46, b, FONT_SEMI, 30, c)
        p.rrect(60, sh - 170, sw - 60, sh - 100, 30, (200, 40, 34))
        p.text(sw / 2, sh - 135, "ОК", FONT_BOLD, 30, (255, 240, 235), anchor="mm")
    if state in ("nosignal", "calling"):
        p.rect(0, 0, sw, sh, (12, 12, 16))
        name = extra or "Мама"
        p.ellipse(sw / 2, 300, 90, 90, (50, 50, 60))
        p.text(sw / 2, 300, name[0], FONT_BOLD, 80, (200, 200, 210), anchor="mm")
        p.text(sw / 2, 450, name, FONT_SEMI, 46, (235, 235, 240), anchor="mm")
        if state == "calling":
            dots = "." * (1 + int(t * 2) % 3)
            p.text(sw / 2, 515, "Вызов" + dots, FONT_SEMI, 28, (170, 170, 180), anchor="mm")
        else:
            p.text(sw / 2, 515, "Нет соединения с сетью", FONT_SEMI, 28, (235, 90, 80), anchor="mm")
        p.ellipse(sw / 2, sh - 170, 52, 52, (210, 40, 36))
        p.rrect(sw / 2 - 26, sh - 176, sw / 2 + 26, sh - 162, 6, (250, 240, 240))
    if state == "final":
        p.rect(0, 0, sw, sh, (10, 4, 4))
        _warn_tri(p, sw / 2, 260, 60, (230, 40, 34))
        for i, s in enumerate(["ВРЕМЯ НА", "ПРИНЯТИЕ РЕШЕНИЯ", "ОГРАНИЧЕНО"]):
            p.text(sw / 2, 420 + i * 56, s, FONT_BOLD, 38, (255, 225, 220), anchor="mm")
        rem = max(0, 59 - int(t))
        p.text(sw / 2, 720, f"00:{rem:02d}", FONT_MONO, 96, (235, 40, 36), anchor="mm")
    a = p.arr()
    # скругление экрана
    mask = Pen(PHW, PHH, ss=2)
    mask.rrect(0, 0, PHW, PHH, 54, (255, 255, 255))
    a *= mask.arr()[..., 3:4]
    return a


@lru_cache(None)
def phone_table_set():
    """Крупный план: телефон на столе (вид сверху)."""
    w, h = LW, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (34, 26, 21))
    r = np.random.default_rng(3)
    for i in range(140):  # волокна дерева
        y = r.uniform(0, h)
        c = int(r.uniform(22, 44))
        pts = [(x, y + 8 * math.sin(x / r.uniform(120, 300) + i)) for x in range(0, w + 80, 80)]
        p.line(pts, (c + 6, c, c - 5), r.uniform(1, 4))
    for x in (0, 760, 1530):  # стыки досок
        p.rect(x, 0, x + 6, h, (14, 11, 9))
    a = textured(p.arr(blur=1.0), 31, k=0.04, stain=0.18)
    # телефон-корпус
    cx, cy = w / 2, h / 2
    pb = Pen(w, h, ss=2)
    pb.rrect(cx - PHW / 2 - 22, cy - PHH / 2 - 26, cx + PHW / 2 + 22, cy + PHH / 2 + 26, 74, (8, 8, 10))
    pb.rrect(cx - PHW / 2 - 18, cy - PHH / 2 - 22, cx + PHW / 2 + 18, cy + PHH / 2 + 22, 70, (30, 30, 34))
    pb.rrect(cx - PHW / 2 - 8, cy - PHH / 2 - 10, cx + PHW / 2 + 8, cy + PHH / 2 + 10, 62, (4, 4, 6))
    body = pb.arr()
    shadow = cv2.GaussianBlur(body[..., 3], (0, 0), 30)
    a[..., :3] *= (1 - 0.7 * shadow[..., None])
    a = over(a, body)
    # блокнот и ручка рядом
    pn = Pen(w, h, ss=1)
    pn.poly([(140, 300), (560, 260), (600, 900), (190, 950)], (150, 146, 138))
    for i in range(14):
        pn.line([(190 + i * 0, 360 + i * 40), (560, 330 + i * 40)], (110, 112, 120), 2)
    pn.line([(1860, 300), (2050, 880)], (20, 20, 60), 16)
    notes = pn.arr(blur=3.5)
    a = over(a, notes * 0.6)
    return {"table": Layer(a, 1.0), "cx": cx, "cy": cy}


# ======================================================================== APARTMENT CORRIDOR (walk)
@lru_cache(None)
def corridor_apt_set():
    w, h = 4200, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (30, 27, 27))
    # обои — вертикальные полосы
    for x in range(0, w, 60):
        p.rect(x, 80, x + 3, 980, (36, 32, 31))
    p.rect(0, 0, w, 80, (22, 20, 20))
    p.rect(0, 980, w, 1000, (20, 18, 17))
    p.rect(0, 1000, w, h, (19, 16, 15))
    for x in range(0, w, 140):  # паркет
        p.line([(x, 1000), (x - 120, h)], (24, 20, 18), 3)
    # двери, картины, вешалка
    for i, dx in enumerate((500, 1700, 2900)):
        p.rect(dx, 330, dx + 330, 990, (24, 21, 20))
        p.rect(dx + 16, 346, dx + 314, 990, (34, 29, 26))
        p.rect(dx + 40, 380, dx + 290, 640, (30, 26, 23))
        p.rect(dx + 40, 680, dx + 290, 960, (30, 26, 23))
        p.ellipse(dx + 280, 680, 12, 12, (90, 84, 70))
    for fx in (1150, 2400, 3600):
        p.rect(fx, 360, fx + 240, 540, (16, 15, 15))
        p.rect(fx + 14, 374, fx + 226, 526, (44, 40, 38))
        p.poly([(fx + 14, 526), (fx + 90, 440), (fx + 150, 500), (fx + 226, 420), (fx + 226, 526)], (34, 32, 31))
    # входная дверь в конце (металл)
    ex = 3900
    p.rect(ex, 300, ex + 300, 990, (40, 40, 44))
    p.rect(ex + 20, 320, ex + 280, 990, (52, 50, 52))
    p.rect(ex + 230, 640, ex + 270, 660, (110, 104, 92))
    alb = textured(p.arr(), 41, k=0.05, stain=0.12)
    # передний план: косяки/стена, быстрее (параллакс)
    pf = Pen(w + 1200, h, ss=1)
    for x in (300, 1500, 2600, 3800, 4900):
        pf.rect(x, 0, x + 120, h, (9, 8, 8))
        pf.rect(x + 120, 0, x + 140, h, (16, 14, 14))
    fg = pf.arr(blur=6)
    return {"wall": Layer(alb, 1.0), "fg": Layer(fg, 1.5), "w": w}


# ======================================================================== STAIRWELL
@lru_cache(None)
def stairs_set():
    w, h = LW, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (28, 27, 28))
    p.rect(0, 0, w, 520, (34, 33, 34))  # верх стены светлее (побелка)
    p.rect(0, 520, w, 536, (22, 22, 24))
    # окно на площадке с оранжевым небом
    p.rect(1560, 170, 1960, 470, (0, 0, 0, 0))
    # номер этажа
    p.text(420, 300, "5", FONT_TITLE, 160, (60, 22, 20))
    # почтовые ящики
    for i in range(4):
        for j in range(2):
            p.rect(160 + i * 70, 640 + j * 80, 222 + i * 70, 710 + j * 80, (40, 44, 46))
            p.rect(170 + i * 70, 650 + j * 80, 212 + i * 70, 660 + j * 80, (16, 16, 16))
    # площадка и лестница вниз (диагональ)
    p.rect(0, 960, w, h, (26, 25, 25))
    for i in range(14):
        x = 900 + i * 70; y = 960 + i * 24
        p.rect(x, y, w, y + 24, (34 - i, 33 - i, 33 - i))
        p.rect(x, y, w, y + 4, (46, 45, 44))
    alb = textured(p.arr(), 51, k=0.06, stain=0.16)
    win = vgrad(w, h, [(0, (40, 18, 14)), (0.25, (150, 62, 26)), (0.4, (60, 26, 18)), (1, (0, 0, 0))])
    sky = solid(w, h, win)
    sky_l = Layer(sky, 0.6)
    # перила (передний план)
    pr = Pen(w, h, ss=2)
    pr.line([(820, 900), (2304, 1410)], (14, 14, 15), 22)
    for i in range(16):
        x = 860 + i * 95
        y = 914 + i * 32.5
        pr.line([(x, y), (x, y + 260)], (14, 14, 15), 9)
    rail = pr.arr(blur=1.5)
    neighbor, nx, ny = ch.person(520, kind=3, seated=False)
    return {"sky": sky_l, "wall": Layer(alb, 1.0), "rail": Layer(rail, 1.25), "neighbor": neighbor,
            "window_glow": Layer(radial(w, h, 1760, 320, 600, (190, 80, 30), k=0.3, sy=0.8), 1.0, add=True)}


# ======================================================================== STREET
@lru_cache(None)
def street_set():
    w, h = LW, LH
    vx, vy = w * 0.5, h * 0.5
    sky = vgrad(w, h, [(0, (12, 8, 9)), (0.3, (50, 18, 14)), (0.5, (150, 60, 24)), (0.6, (60, 24, 16)), (1, (8, 7, 7))])
    out = {"sky": Layer(solid(w, h, sky), 0.2)}
    sm = smoke_column(w, h, 12, w * 0.58, vy + 20, 520, 110, color=(36, 30, 30), lean=0.6)
    sm = over(sm, smoke_column(w, h, 13, w * 0.4, vy + 20, 300, 70, color=(30, 26, 26), lean=0.4))
    out["smoke"] = Layer(sm, 0.25)
    far, farw = city_row(w, h, 77, vy + 40, 80, 240, (26, 16, 15), (220, 120, 50), 0.02, wmin=40, wmax=120)
    out["far"] = Layer(far, 0.35)
    # стороны улицы в перспективе
    p = Pen(w, h, ss=1)
    p.poly([(0, 0), (vx - 260, vy - 220), (vx - 260, vy + 60), (0, h)], (20, 16, 16))
    p.poly([(w, 0), (vx + 260, vy - 260), (vx + 260, vy + 60), (w, h)], (18, 15, 15))
    p.poly([(0, h), (vx - 260, vy + 60), (vx + 260, vy + 60), (w, h)], (22, 20, 20))
    pw = Pen(w, h, ss=1)
    r = np.random.default_rng(9)
    for side in (-1, 1):  # окна по перспективе
        for i in range(10):
            f = i / 10
            x = vx + side * (260 + (1 - f) ** 2 * 900 + 40)
            for j in range(6):
                y = vy - 200 * (1 - f) - j * 90 * (1 - f) + 10
                if r.random() < 0.18:
                    s = 30 * (1 - f) + 6
                    pw.rect(x, y, x + s * side * 0.8, y + s, (200, 100, 40))
    for k in range(-1, 2):  # разметка
        pass
    for i in range(12):
        f0, f1 = i / 12, (i + 0.5) / 12
        y0 = vy + 60 + (h - vy - 60) * f0 ** 2
        y1 = vy + 60 + (h - vy - 60) * f1 ** 2
        p.poly([(vx - 2 - 14 * f0 ** 2, y0), (vx + 2 + 14 * f0 ** 2, y0), (vx + 2 + 14 * f1 ** 2, y1),
                (vx - 2 - 14 * f1 ** 2, y1)], (60, 56, 50))
    out["street"] = Layer(textured(p.arr(), 61, k=0.05, stain=0.15), 1.0)
    out["win"] = Layer(pw.arr(blur=1.0)[..., :3].copy(), 1.0, add=True)
    # машины (силуэты) и их аварийки
    cars, lights = [], []
    pc = Pen(w, h, ss=2)
    for (cx, cy, s) in [(vx - 330, vy + 170, 0.55), (vx + 180, vy + 120, 0.38), (vx - 120, vy + 95, 0.28),
                        (vx + 560, vy + 330, 0.9)]:
        cw, chh = 420 * s, 150 * s
        pc.rrect(cx - cw / 2, cy - chh * 0.55, cx + cw / 2, cy + chh * 0.45, 18 * s, (12, 11, 11))
        pc.poly([(cx - cw * 0.32, cy - chh * 0.55), (cx - cw * 0.2, cy - chh * 1.05), (cx + cw * 0.25, cy - chh * 1.05),
                 (cx + cw * 0.36, cy - chh * 0.55)], (14, 13, 13))
        pc.ellipse(cx - cw * 0.3, cy + chh * 0.45, 34 * s, 34 * s, (6, 6, 6))
        pc.ellipse(cx + cw * 0.3, cy + chh * 0.45, 34 * s, 34 * s, (6, 6, 6))
        lights.append((cx - cw * 0.46, cy - chh * 0.15, s))
        lights.append((cx + cw * 0.46, cy - chh * 0.15, s))
    out["cars"] = Layer(pc.arr(), 1.05)
    hz = np.zeros((h, w, 3), np.float32)
    for (lx, ly, s) in lights:
        hz += radial(w, h, lx, ly, 120 * s + 30, (255, 150, 40), power=2.5, k=1.2)
    out["hazard"] = Layer(hz, 1.05, add=True)
    out["vx"], out["vy"] = vx, vy
    return out


# ======================================================================== SHELTER ENTRANCE
@lru_cache(None)
def shelter_door_set():
    w, h = LW, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (30, 30, 31))
    p.rect(0, 1020, w, h, (22, 21, 21))
    # проём
    dx0, dy0, dx1, dy1 = 920, 380, 1380, 1030
    p.rect(dx0 - 50, dy0 - 50, dx1 + 50, dy1, (46, 46, 48))
    p.rect(dx0, dy0, dx1, dy1, (3, 3, 4))
    # табличка УБЕЖИЩЕ
    p.rect(900, 180, 1400, 300, (190, 184, 170))
    p.rect(910, 190, 1390, 290, (176, 30, 24))
    p.text(1150, 240, "УБЕЖИЩЕ", FONT_TITLE, 76, (240, 234, 220), anchor="mm")
    # трафаретная стрелка, трубы
    p.poly([(620, 640), (760, 640), (760, 600), (840, 680), (760, 760), (760, 720), (620, 720)], (120, 30, 24))
    for y in (60, 110):
        p.rect(0, y, w, y + 30, (40, 40, 42))
        p.rect(0, y + 26, w, y + 30, (24, 24, 26))
    alb = textured(p.arr(), 71, k=0.07, stain=0.2)
    # створка двери (рисуется отдельно, анимируется)
    pfg = Pen(w, h, ss=1)
    pfg.rect(0, 0, 160, h, (12, 12, 13))
    pfg.rect(2120, 0, w, h, (12, 12, 13))
    pfg.line([(0, 1150), (w, 1160)], (16, 16, 17), 40)
    fg = pfg.arr(blur=7)
    return {"wall": Layer(alb, 1.0), "fg": Layer(fg, 1.4), "door": (dx0, dy0, dx1, dy1)}


def door_leaf(w, h, rect, close):
    """Створка гермодвери: close 0 (открыта, повернута) .. 1 (закрыта)."""
    dx0, dy0, dx1, dy1 = rect
    p = Pen(w, h, ss=1)
    hinge = dx1
    width = (dx1 - dx0) * (0.12 + 0.88 * close)
    skew = (1 - close) * 60
    x0 = hinge - width
    col = (58, 58, 60)
    p.poly([(x0, dy0 + skew), (hinge, dy0), (hinge, dy1), (x0, dy1 - skew)], col)
    if close > 0.3:
        k = (close - 0.3) / 0.7
        for yy in (0.25, 0.5, 0.75):
            y = dy0 + (dy1 - dy0) * yy
            p.rect(x0 + 20, y - 6, hinge - 20, y + 6, (44, 44, 46))
        p.ellipse(x0 + width * 0.25, (dy0 + dy1) / 2, 46 * k, 46 * k, (30, 30, 32))
        p.ellipse(x0 + width * 0.25, (dy0 + dy1) / 2, 34 * k, 34 * k, (58, 58, 60))
    return p.arr()


# ======================================================================== SHELTER HALL
BED_POS = [(380, 900), (900, 900), (1420, 900), (1940, 900), (2460, 900), (2980, 900)]  # 6 кроватей
LAMPS = [(640, 150), (1680, 150), (2720, 150)]


@lru_cache(None)
def shelter_hall_set():
    w, h = 3400, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (34, 34, 33))
    p.rect(0, 560, w, 1000, (30, 32, 30))  # нижняя панель стены
    p.rect(0, 556, w, 566, (20, 20, 20))
    p.rect(0, 1000, w, h, (22, 22, 22))
    for x in range(0, w, 300):  # швы бетона
        p.rect(x, 0, x + 4, 1000, (26, 26, 26))
    for y in (40, 90):  # трубы
        p.rect(0, y, w, y + 34, (44, 42, 40))
        p.rect(0, y + 28, w, y + 34, (26, 25, 24))
    for x in range(120, w, 420):
        p.rect(x, 34, x + 16, 130, (30, 30, 30))
    # вентиляционная решётка
    p.rect(2000, 230, 2240, 380, (24, 24, 24))
    for i in range(8):
        p.rect(2010, 240 + i * 17, 2230, 250 + i * 17, (40, 40, 40))
    # дверь справа (выход) и полки с ящиками
    p.rect(3150, 420, 3380, 1000, (48, 46, 46))
    p.rect(3170, 440, 3360, 1000, (58, 56, 54))
    p.rect(3190, 700, 3240, 720, (90, 86, 76))
    for i in range(3):
        p.rect(60 + i * 110, 900, 150 + i * 110, 1000, (50, 44, 34))
    alb = textured(p.arr(), 81, k=0.07, stain=0.22)
    # кровати (металлические рамы)
    pb = Pen(w, h, ss=2)
    for i, (bx, by) in enumerate(BED_POS):
        bc = (52, 52, 54)
        pb.rect(bx - 210, by - 60, bx + 210, by - 30, (60, 58, 56))  # матрас
        pb.rect(bx - 210, by - 74, bx - 120, by - 56, (78, 76, 72))  # подушка
        pb.line([(bx - 220, by - 170), (bx - 220, by + 90)], bc, 10)
        pb.line([(bx + 220, by - 140), (bx + 220, by + 90)], bc, 10)
        pb.line([(bx - 220, by - 30), (bx + 220, by - 30)], bc, 9)
        pb.line([(bx - 220, by - 150), (bx - 220, by - 150)], bc, 9)
        for k in range(5):
            pb.line([(bx - 220, by - 160 + k * 26), (bx - 220, by - 160 + k * 26)], bc, 4)
    beds = pb.arr()
    return {"wall": alb, "beds": beds, "w": w, "h": h}


@lru_cache(None)
def hall_lightmaps():
    s = shelter_hall_set()
    w, h = s["w"], s["h"]
    warm = []
    for (lx, ly) in LAMPS:
        warm.append(radial(w, h, lx, ly + 40, 1000, (255, 196, 130), power=1.8, k=1.0, sy=1.1)[..., 0:1])
    red = radial(w, h, 1700, 120, 1900, (255, 255, 255), power=1.4, k=1.0, sy=0.8)[..., 0:1]
    p = Pen(w, h, ss=2)
    for (lx, ly) in LAMPS:
        p.line([(lx, 0), (lx, ly)], (18, 18, 18), 4)
        p.poly([(lx - 50, ly + 40), (lx + 50, ly + 40), (lx + 22, ly), (lx - 22, ly)], (40, 40, 38))
    lamps = p.arr()
    bulbs = [radial(w, h, lx, ly + 44, 70, (255, 230, 190), power=1.5, k=1.8) for (lx, ly) in LAMPS]
    # аварийные красные лампы на стене
    em = np.zeros((h, w, 3), np.float32)
    for x in (300, 1300, 2300, 3100):
        em += radial(w, h, x, 470, 50, (255, 60, 40), power=1.4, k=1.6)
    return warm, red, lamps, bulbs, em


# ======================================================================== SPEAKER / CLOCK
@lru_cache(None)
def speaker_set():
    w, h = LW, LH
    p = Pen(w, h, ss=2)
    p.rect(0, 0, w, h, (32, 32, 31))
    p.rect(0, 0, w, 200, (26, 26, 25))  # потолок
    p.rect(0, 196, w, 210, (18, 18, 18))
    p.rect(1300, 0, 1330, 560, (40, 40, 40))  # кабель-канал
    # коробка громкоговорителя
    bx0, by0, bx1, by1 = 860, 300, 1460, 760
    p.rect(bx0 + 16, by0 + 16, bx1 + 16, by1 + 16, (14, 14, 14))
    p.rrect(bx0, by0, bx1, by1, 16, (58, 50, 42))
    p.rrect(bx0 + 20, by0 + 20, bx1 - 20, by1 - 20, 10, (48, 42, 36))
    p.rect(bx0 + 40, by1 - 70, bx0 + 260, by1 - 34, (140, 136, 120))
    p.text(bx0 + 150, by1 - 52, "ГО-2", FONT_BOLD, 22, (30, 30, 30), anchor="mm")
    p.ellipse(bx1 - 80, by1 - 52, 20, 20, (30, 10, 10))  # индикатор (выкл)
    p.rect(bx0 + 120, 210, bx0 + 140, by0, (30, 30, 30))
    p.rect(bx1 - 140, 210, bx1 - 120, by0, (30, 30, 30))
    alb = textured(p.arr(), 91, k=0.06, stain=0.18)
    # решётка динамика — отдельный слой (вибрирует)
    gc = (1160, 500)
    pg = Pen(w, h, ss=2)
    pg.ellipse(gc[0], gc[1], 205, 205, (20, 18, 16))
    for yy in range(-190, 191, 24):
        for xx in range(-190, 191, 24):
            if xx * xx + yy * yy < 185 ** 2:
                pg.ellipse(gc[0] + xx, gc[1] + yy, 7, 7, (6, 6, 6))
    grill = pg.arr()
    led = radial(w, h, bx1 - 80, by1 - 52, 140, (255, 40, 30), power=2, k=1.0)
    led += radial(w, h, bx1 - 80, by1 - 52, 22, (255, 120, 100), power=1, k=2.0)
    return {"wall": Layer(alb, 1.0), "grill": Layer(grill, 1.0), "led": Layer(led, 1.0, add=True), "gc": gc,
            "led_xy": (bx1 - 80, by1 - 52)}


SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg"}


def seven_seg(p, x, y, s, digit, on, off):
    t = s * 0.18
    segs = {"a": [(x + t, y), (x + s - t, y), (x + s - 2 * t, y + t), (x + 2 * t, y + t)],
            "d": [(x + 2 * t, y + 2 * s - t), (x + s - 2 * t, y + 2 * s - t), (x + s - t, y + 2 * s), (x + t, y + 2 * s)],
            "g": [(x + t, y + s), (x + 2 * t, y + s - t / 2), (x + s - 2 * t, y + s - t / 2), (x + s - t, y + s),
                  (x + s - 2 * t, y + s + t / 2), (x + 2 * t, y + s + t / 2)],
            "f": [(x, y + t), (x + t, y + 2 * t), (x + t, y + s - t), (x, y + s - t / 2)],
            "b": [(x + s, y + t), (x + s, y + s - t / 2), (x + s - t, y + s - t), (x + s - t, y + 2 * t)],
            "e": [(x, y + s + t / 2), (x + t, y + s + t), (x + t, y + 2 * s - 2 * t), (x, y + 2 * s - t)],
            "c": [(x + s, y + s + t / 2), (x + s, y + 2 * s - t), (x + s - t, y + 2 * s - 2 * t), (x + s - t, y + s + t)]}
    for k, pts in segs.items():
        p.poly(pts, on if k in SEG[digit] else off)


def clock_layer(text, w=LW, h=LH, blink=True):
    p = Pen(w, h, ss=2)
    p.text(w / 2, 690, "88:88", FONT_MONO, 330, (34, 7, 7), anchor="mm")
    shown = text if blink else text.replace(":", " ")
    p.text(w / 2, 690, shown, FONT_MONO, 330, (255, 38, 28), anchor="mm")
    a = p.arr()
    g = cv2.GaussianBlur(a, (0, 0), 14)
    return a + g * 0.8 * (1 - a[..., 3:4])


@lru_cache(None)
def clock_set():
    w, h = LW, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (32, 32, 31))
    p.rect(0, 760 + 220, w, h, (24, 24, 24))
    p.rect(680, 470, 1640, 900, (10, 10, 10))
    p.rect(700, 490, 1620, 880, (20, 6, 6))
    p.rect(1080, 420, 1240, 470, (18, 18, 18))
    alb = textured(p.arr(), 95, k=0.06, stain=0.18)
    return {"wall": Layer(alb, 1.0)}


# ======================================================================== LONG CORRIDOR & DOOR
@lru_cache(None)
def long_corridor_set():
    w, h = LW, LH
    vx, vy = w / 2, h * 0.52
    p = Pen(w, h, ss=2)
    p.rect(0, 0, w, h, (6, 6, 7))
    N = 26
    for i in range(N, 0, -1):  # от дальних полос к ближним
        f0 = (i - 1) / N; f1 = i / N
        def sz(f):
            return 0.06 + 1.6 * f ** 2.2
        a, b = sz(f0), sz(f1)
        lum = 16 + 70 * f1 ** 1.2
        hw0, hh0, hw1, hh1 = 900 * a, 560 * a, 900 * b, 560 * b
        c = lambda k: (int(lum * k), int(lum * k), int(lum * k * 1.02))
        p.poly([(vx - hw1, vy - hh1), (vx - hw0, vy - hh0), (vx - hw0, vy + hh0), (vx - hw1, vy + hh1)],
               c(0.9 if i % 2 else 0.8))
        p.poly([(vx + hw1, vy - hh1), (vx + hw0, vy - hh0), (vx + hw0, vy + hh0), (vx + hw1, vy + hh1)],
               c(0.85 if i % 2 else 0.75))
        p.poly([(vx - hw1, vy - hh1), (vx + hw1, vy - hh1), (vx + hw0, vy - hh0), (vx - hw0, vy - hh0)], c(0.6))
        p.poly([(vx - hw1, vy + hh1), (vx + hw1, vy + hh1), (vx + hw0, vy + hh0), (vx - hw0, vy + hh0)], c(0.7))
        # трубы под потолком
        p.line([(vx - hw1 * 0.95, vy - hh1 * 0.8), (vx - hw0 * 0.95, vy - hh0 * 0.8)], c(1.3), max(2, 30 * b))
    # дверь в конце
    a = 0.06 + 1.6 * 0 ** 2.2
    dw, dh = 900 * 0.075, 560 * 0.1
    d0 = (vx - dw * 0.62, vy - dh * 0.85, vx + dw * 0.62, vy + 560 * 0.06)
    p.rect(d0[0] - 6, d0[1] - 6, d0[2] + 6, d0[3], (40, 40, 42))
    p.rect(*d0, (50, 48, 48))
    p.rect(d0[2] - 18, (d0[1] + d0[3]) / 2, d0[2] - 6, (d0[1] + d0[3]) / 2 + 4, (110, 104, 90))
    alb = textured(p.arr(), 101, k=0.05, stain=0.15)
    door_light = radial(w, h, vx, vy - 10, 160, (200, 120, 70), power=2, k=0.35)
    lamp_xy = (vx, vy - 560 * (0.06 + 1.6 * 0.45 ** 2.2) * 0.98)
    lamp = radial(w, h, lamp_xy[0], lamp_xy[1] + 20, 520, (255, 200, 140), power=2, k=0.55, sy=0.9)
    lamp += radial(w, h, lamp_xy[0], lamp_xy[1], 28, (255, 230, 200), power=1, k=2)
    return {"corr": Layer(alb, 1.0), "door_light": Layer(door_light, 1.0, add=True),
            "lamp": Layer(lamp, 1.0, add=True), "vp": (vx, vy), "door": d0}


@lru_cache(None)
def handle_set():
    w, h = LW, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (46, 45, 46))
    r = np.random.default_rng(12)
    for i in range(70):  # царапины
        x, y = r.uniform(0, w), r.uniform(0, h)
        L = r.uniform(30, 160); a = r.uniform(-0.4, 0.4)
        p.line([(x, y), (x + L * math.cos(a), y + L * math.sin(a))], (60, 58, 58), r.uniform(1, 2.5))
    for x in (160, w - 160):  # заклёпки
        for y in range(120, h, 180):
            p.ellipse(x, y, 16, 16, (34, 33, 33)); p.ellipse(x - 3, y - 3, 10, 10, (66, 64, 62))
    p.rect(w - 70, 0, w, h, (20, 20, 20))  # щель/косяк
    alb = textured(p.arr(blur=0.6), 111, k=0.08, stain=0.3)
    # ржавые подтёки
    rust = _stain(w, h, 113, k=1.0)[..., 0]
    rust = np.clip(rust, 0, None)
    alb[..., 0] += rust * 0.06; alb[..., 1] += rust * 0.015
    # накладка ручки
    pp = Pen(w, h, ss=2)
    px, py = 1250, 640
    pp.rrect(px - 120, py - 300, px + 120, py + 320, 24, (30, 30, 31))
    pp.rrect(px - 110, py - 290, px + 110, py + 310, 20, (70, 68, 66))
    for yy in (py - 250, py + 270):
        pp.ellipse(px, yy, 14, 14, (40, 40, 40))
    pp.ellipse(px, py + 170, 26, 40, (16, 16, 16))  # скважина
    pp.rect(px - 8, py + 180, px + 8, py + 230, (16, 16, 16))
    plate = pp.arr()
    return {"door": Layer(alb, 1.0), "plate": Layer(plate, 1.0), "pivot": (px, py)}


def handle_lever(angle, w=LW, h=LH, pivot=(1250, 640)):
    """Ручка-рычаг, angle в радианах (0 — горизонтально, + вниз)."""
    p = Pen(w, h, ss=2)
    px, py = pivot
    L, t = 560, 64
    ca, sa = math.cos(angle), math.sin(angle)
    def R(x, y):
        return (px + (x * ca - y * sa) * -1, py + (x * sa + y * ca))
    shadow = [R(-30 + 14, -t / 2 + 26), R(L + 14, -t / 2 + 30), R(L + 14, t / 2 + 30), R(-30 + 14, t / 2 + 26)]
    p.poly(shadow, (10, 10, 10, 150))
    p.ellipse(px, py, 70, 70, (40, 40, 40))
    p.ellipse(px, py, 58, 58, (96, 94, 90))
    pts = [R(-30, -t / 2), R(L, -t / 2 + 6), R(L + 20, 0), R(L, t / 2 - 2), R(-30, t / 2)]
    p.poly(pts, (88, 86, 82))
    hl = [R(-30, -t / 2), R(L, -t / 2 + 6), R(L, -t / 2 + 16), R(-30, -t / 2 + 10)]
    p.poly(hl, (150, 146, 136))
    p.ellipse(px, py, 22, 22, (60, 58, 56))
    return p.arr(blur=0.8)


# ======================================================================== VISIONS: MALL / METRO
@lru_cache(None)
def mall_set():
    w, h = LW, LH
    sky = vgrad(w, h, [(0, (14, 10, 11)), (0.4, (60, 26, 18)), (0.58, (120, 52, 24)), (1, (10, 9, 9))])
    p = Pen(w, h, ss=2)
    p.rect(0, 860, w, h, (20, 18, 18))  # парковка
    for i in range(12):
        x = 100 + i * 190
        p.poly([(x, 900), (x + 8, 900), (x - 40, 1296), (x - 52, 1296)], (44, 40, 36))
    mx0, my0, mx1, my1 = 360, 420, 1980, 860
    p.rect(mx0, my0, mx1, my1, (24, 22, 22))
    p.rect(mx0 - 20, my0 - 30, mx1 + 20, my0, (30, 28, 28))
    for i in range(15):  # стеклянный фасад
        for j in range(3):
            x = mx0 + 50 + i * 104; y = my0 + 120 + j * 100
            p.rect(x, y, x + 90, y + 86, (14, 14, 16))
    p.rect(1060, 700, 1280, 860, (8, 8, 9))  # вход
    alb = p.arr()
    pw = Pen(w, h, ss=1)
    r = np.random.default_rng(4)
    for i in range(15):
        for j in range(3):
            if r.random() < 0.12:
                x = mx0 + 50 + i * 104; y = my0 + 120 + j * 100
                pw.rect(x, y, x + 90, y + 86, (170, 110, 60))
    pw.rect(1090, 740, 1250, 860, (90, 60, 34))
    wins = pw.arr(blur=2)[..., :3].copy()
    sign = Pen(w, h, ss=2)
    sign.text(1170, my0 + 50, "ТОРГОВЫЙ ЦЕНТР", FONT_TITLE, 66, (80, 70, 60), anchor="mm")
    sign_l = sign.arr()
    sm = smoke_column(w, h, 21, 1700, 600, 500, 90, color=(30, 26, 26), lean=0.5)
    cars = Pen(w, h, ss=2)
    for (cx, cy, s) in [(520, 980, 0.8), (1560, 1050, 1.0), (900, 930, 0.6)]:
        cars.rrect(cx - 200 * s, cy - 50 * s, cx + 200 * s, cy + 40 * s, 16, (10, 10, 10))
        cars.poly([(cx - 120 * s, cy - 50 * s), (cx - 80 * s, cy - 110 * s), (cx + 90 * s, cy - 110 * s),
                   (cx + 130 * s, cy - 50 * s)], (12, 12, 12))
    return {"sky": Layer(solid(w, h, sky), 0.3), "smoke": Layer(sm, 0.35), "mall": Layer(alb, 1.0),
            "wins": Layer(wins, 1.0, add=True), "sign": Layer(sign_l, 1.0), "cars": Layer(cars.arr(), 1.2)}


@lru_cache(None)
def metro_set():
    w, h = LW, LH
    sky = vgrad(w, h, [(0, (10, 8, 9)), (0.45, (50, 22, 16)), (0.6, (90, 40, 20)), (1, (8, 8, 8))])
    p = Pen(w, h, ss=2)
    p.rect(0, 780, w, h, (20, 19, 19))
    # павильон входа
    p.rect(620, 380, 1680, 470, (34, 32, 32))
    p.rect(660, 470, 700, 900, (30, 28, 28)); p.rect(1600, 470, 1640, 900, (30, 28, 28))
    # лестница вниз в темноту
    for i in range(14):
        f = i / 14
        y = 780 + f * 420
        x0 = 760 - f * 260; x1 = 1540 + f * 260
        c = int(8 + 40 * f)
        p.rect(x0, y, x1, y + 30, (c, c, c))
    p.poly([(760, 780), (1540, 780), (1640, 900), (660, 900)], (4, 4, 5))
    for side in (-1, 1):
        x = 1150 + side * 420
        p.line([(x, 700), (x + side * 140, 1296)], (50, 48, 46), 12)
    alb = p.arr()
    m = Pen(w, h, ss=2)
    m.text(1150, 300, "М", FONT_TITLE, 200, (220, 30, 26), anchor="mm")
    sign = m.arr()
    glow = radial(w, h, 1150, 300, 420, (255, 50, 36), power=2, k=0.7)
    sm = smoke_column(w, h, 33, 500, 640, 400, 80, color=(30, 26, 26), lean=0.3)
    return {"sky": Layer(solid(w, h, sky), 0.3), "smoke": Layer(sm, 0.35), "metro": Layer(alb, 1.0),
            "sign": Layer(sign, 1.0), "glow": Layer(glow, 1.0, add=True)}


# ======================================================================== TV ROOM
TV_RECT = (1000, 560, 1440, 820)


@lru_cache(None)
def tv_room_set():
    w, h = 3000, LH
    p = Pen(w, h, ss=1)
    p.rect(0, 0, w, h, (26, 23, 23))
    p.rect(0, 0, w, 70, (18, 16, 16))
    p.rect(0, 1040, w, h, (16, 14, 14))
    # окно справа с дымным небом
    p.rect(2300, 240, 2840, 860, (0, 0, 0, 0))
    for (a, b, c, d) in [(2300, 240, 2840, 262), (2300, 838, 2840, 860), (2300, 240, 2322, 860), (2818, 240, 2840, 860),
                         (2560, 240, 2582, 860)]:
        p.rect(a, b, c, d, (16, 16, 18))
    # тумба и телевизор
    x0, y0, x1, y1 = TV_RECT
    p.rect(860, 860, 1580, 1040, (30, 25, 22))
    p.rect(880, 940, 1560, 948, (20, 17, 15))
    p.rect(x0 - 24, y0 - 24, x1 + 24, y1 + 24, (10, 10, 11))
    p.rect(1200, y1 + 24, 1240, 860, (12, 12, 12))
    # диван слева
    p.rrect(120, 760, 760, 1060, 40, (30, 26, 26))
    p.rrect(100, 640, 780, 800, 50, (34, 30, 30))
    # полка и рамки
    for fx in (300, 480):
        p.rect(fx, 380, fx + 130, 540, (14, 14, 14)); p.rect(fx + 10, 390, fx + 120, 530, (40, 36, 34))
    alb = textured(p.arr(), 121, k=0.05, stain=0.14)
    sky = vgrad(w, h, [(0, (16, 10, 10)), (0.35, (70, 26, 16)), (0.6, (140, 56, 22)), (1, (30, 14, 10))])
    city, _ = city_row(w, h, 131, 820, 100, 360, (18, 13, 12), (0, 0, 0), 0.0, win=False)
    sm = smoke_column(w, h, 133, 2600, 760, 520, 90, color=(36, 30, 30), lean=0.5)
    return {"sky": Layer(solid(w, h, sky), 0.4), "smoke": Layer(sm, 0.45), "city": Layer(city, 0.6),
            "room": Layer(alb, 1.0), "w": w}


# ======================================================================== PHONE IN HAND
@lru_cache(None)
def phone_hand_set(bg):
    w, h = LW, LH
    cx, cy = w / 2, h / 2 + 60
    if bg == "street":
        bgimg = vgrad(w, h, [(0, (20, 10, 9)), (0.5, (90, 38, 18)), (1, (12, 9, 9))])
        r = np.random.default_rng(5)
        for i in range(26):  # боке огней
            bgimg += radial(w, h, r.uniform(0, w), r.uniform(h * 0.3, h * 0.75), r.uniform(40, 120),
                            (255, 140, 50) if r.random() < .8 else (255, 60, 40), power=1.2, k=r.uniform(0.1, 0.35))
    else:
        bgimg = vgrad(w, h, [(0, (10, 9, 9)), (0.6, (22, 18, 18)), (1, (8, 8, 8))])
        bgimg += radial(w, h, w * 0.8, h * 0.25, 260, (255, 180, 120), power=1.4, k=0.12)
        bgimg += radial(w, h, w * 0.15, h * 0.6, 180, (200, 80, 40), power=1.4, k=0.08)
    bgl = Layer(solid(w, h, cv2.GaussianBlur(bgimg, (0, 0), 6)), 0.4)
    pb = Pen(w, h, ss=2)
    pb.rrect(cx - PHW / 2 - 22, cy - PHH / 2 - 26, cx + PHW / 2 + 22, cy + PHH / 2 + 26, 74, (8, 8, 10))
    pb.rrect(cx - PHW / 2 - 18, cy - PHH / 2 - 22, cx + PHW / 2 + 18, cy + PHH / 2 + 22, 70, (30, 30, 34))
    pb.rrect(cx - PHW / 2 - 8, cy - PHH / 2 - 10, cx + PHW / 2 + 8, cy + PHH / 2 + 10, 62, (4, 4, 6))
    body = pb.arr()
    ph = Pen(w, h, ss=2)
    skin = (58, 43, 36)
    sleeve = (14, 14, 16)
    # ладонь и рукав — за телефоном
    ph.poly([(cx + 120, h + 40), (cx + 60, cy + 380), (cx + 330, cy + 300), (cx + 560, h + 40)], sleeve)
    ph.ellipse(cx + 150, cy + 360, 250, 170, skin)
    palm = ph.arr(blur=1.2)
    pf = Pen(w, h, ss=2)
    for i in range(4):  # пальцы обхватывают левый край
        y = cy + 60 + i * 92
        pf.rrect(cx - PHW / 2 - 40, y, cx - PHW / 2 + 16, y + 70, 30, tuple(int(v * (1.0 - i * 0.08)) for v in skin))
    pf.rrect(cx + PHW / 2 - 30, cy + 150, cx + PHW / 2 + 40, cy + 300, 34, skin)  # большой палец справа
    fingers = pf.arr(blur=1.2)
    return {"bg": bgl, "body": Layer(body, 1.0), "palm": Layer(palm, 1.0), "hand": Layer(fingers, 1.0), "cx": cx,
            "cy": cy}
