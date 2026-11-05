"""Декорации «За мной кто-то идёт» (вертикаль 9:16). Единая перспектива и палитра:
чёрный / тёмно-синий / серый + жёлтые фонари, туман, мокрый асфальт."""
import math
from functools import lru_cache
import numpy as np
import cv2
from ..gfx import Pen, vgrad, solid, radial, rgb, over, Layer, font_
from ..config import W, H, FONT_TITLE, FONT_BOLD, FONT_SEMI, FONT_MONO
from ..sets import textured, _noise_tex

LW, LH = int(W * 1.2), int(H * 1.2)      # 1296 x 2304
F = 640.0                                 # фокус (px слоя)
CAMH = 1.6                                # высота камеры, м
FOG = (34, 40, 56)
LAMP = (255, 196, 110)


class Persp:
    def __init__(self, vx=LW / 2, vy=LH * 0.44, camx=0.0, fogd=38.0):
        self.vx, self.vy, self.camx, self.fogd = vx, vy, camx, fogd

    def p(self, x, y, z):
        z = max(z, 0.3)
        return (self.vx + (x - self.camx) * F / z, self.vy + (CAMH - y) * F / z)

    def fog(self, c, z, k=1.0):
        m = (1 - math.exp(-z / self.fogd)) * k
        return tuple(int(a * (1 - m) + b * m) for a, b in zip(c[:3], FOG)) + tuple(c[3:])

    def size(self, z, meters):
        return meters * F / max(z, 0.3)


def quad(pen, P, pts, col):
    pen.poly([P.p(*q) for q in pts], col)


def facade(pen, wl, P, x, z0, z1, top, col, seed, win_p=0.12, side=-1, step=3.0, shop=None, lit_col=(255, 190, 110)):
    """Фасад в плоскости x (side -1 слева, +1 справа) от z0 до z1, окна в слой wl."""
    r = np.random.default_rng(seed)
    z = z1
    while z > z0:
        za = max(z0, z - step)
        zm = (z + za) / 2
        quad(pen, P, [(x, 0, za), (x, top, za), (x, top, z), (x, 0, z)], P.fog(_jit(col, r), zm))
        # окна по этажам
        for fl in range(1, int(top / 3)):
            y0, y1 = fl * 3 + 0.9, fl * 3 + 2.3
            if y1 > top - 0.4:
                break
            a, b = za + 0.6, z - 0.6
            lit = r.random() < win_p
            c = P.fog((14, 16, 22), zm) if not lit else P.fog(tuple(int(v * r.uniform(0.5, 1.0)) for v in lit_col), zm, 0.7)
            quad(pen, P, [(x, y0, a), (x, y1, a), (x, y1, b), (x, y0, b)], c)
            if lit:
                quad(wl, P, [(x, y0, a), (x, y1, a), (x, y1, b), (x, y0, b)], tuple(int(v * 0.5) for v in c))
        z = za
    # цоколь
    quad(pen, P, [(x, 0, z0), (x, 0.5, z0), (x, 0.5, z1), (x, 0, z1)], P.fog((16, 17, 20), z0 + 5))


def _jit(c, r):
    k = r.uniform(0.88, 1.1)
    return tuple(int(v * k) for v in c)


def car(pen, P, x0, x1, z0, col=(16, 18, 24), lights=None):
    L = 4.3
    zm = z0 + L / 2
    c = P.fog(col, zm)
    quad(pen, P, [(x0, 0.25, z0), (x0, 1.0, z0), (x0, 1.0, z0 + L), (x0, 0.25, z0 + L)], c)  # бок
    quad(pen, P, [(x0, 1.0, z0 + 0.9), (x0, 1.45, z0 + 1.4), (x0, 1.45, z0 + 3.0), (x0, 1.0, z0 + 3.5)], c)
    cb = P.fog(tuple(int(v * 0.8) for v in col), z0)
    quad(pen, P, [(x0, 0.25, z0), (x1, 0.25, z0), (x1, 1.0, z0), (x0, 1.0, z0)], cb)  # зад
    quad(pen, P, [(x0 + 0.15, 1.0, z0 + 0.9), (x1 - 0.15, 1.0, z0 + 0.9), (x1 - 0.2, 1.42, z0 + 1.4),
                  (x0 + 0.2, 1.42, z0 + 1.4)], P.fog((10, 12, 16), z0))
    for wx in (x0 + 0.2, x1 - 0.2):
        a = P.p(wx, 0.32, z0)
        pen.ellipse(a[0], a[1], P.size(z0, 0.32), P.size(z0, 0.3), (6, 6, 7))
    if lights is not None:
        for wx in (x0 + 0.25, x1 - 0.25):
            lights.append(P.p(wx, 0.8, z0) + (P.size(z0, 0.25),))


def lamp(pen, P, x, z, lamps, height=4.6, arm=0.9, side=-1):
    b = P.p(x, 0, z)
    t = P.p(x, height, z)
    hx = P.p(x - side * arm, height, z)
    wpx = max(1.5, P.size(z, 0.12))
    c = P.fog((14, 15, 18), z)
    pen.line([b, t], c, wpx)
    pen.line([t, hx], c, wpx * 0.8)
    pen.ellipse(hx[0], hx[1] + P.size(z, 0.08), P.size(z, 0.22), P.size(z, 0.1), c)
    g = P.p(x - side * arm, 0, z)
    lamps.append(dict(head=(hx[0], hx[1] + P.size(z, 0.12)), ground=g, r=P.size(z, 3.2), z=z))


def lamp_lights(w, h, lamps, k=1.0):
    """Свет фонарей (RGB аддитивно): ореол, конус в тумане, пятно на асфальте, мокрый блик."""
    out = np.zeros((h, w, 3), np.float32)
    for L in lamps:
        att = math.exp(-L["z"] / 60)
        hx, hy = L["head"]
        gx, gy = L["ground"]
        r = L["r"]
        out += radial(w, h, hx, hy, r * 0.25 + 6, (255, 236, 200), power=1.4, k=1.6 * att)
        out += radial(w, h, hx, hy, r * 0.9, LAMP, power=2.0, k=0.35 * att)
        cy = (hy + gy) / 2
        out += radial(w, h, (hx + gx) / 2, cy, r * 0.55, LAMP, power=1.8, k=0.25 * att, sy=(gy - hy) / (r * 0.9) + 0.5)
        out += radial(w, h, gx, gy, r * 1.1, LAMP, power=1.6, k=0.35 * att, sy=0.3)
        out += radial(w, h, gx, gy + r * 0.25, r * 0.12, LAMP, power=1.2, k=0.25 * att, sy=4.0)  # блик на мокром
    return out * k


def ground(pen, P, x_left, x_right, xs=(), cols=None):
    """Полосы земли от горизонта до камеры. xs — границы полос (тротуар/бордюр/дорога)."""
    bounds = [x_left] + list(xs) + [x_right]
    cols = cols or [(30, 32, 38)] * (len(bounds) - 1)
    zs = [80, 40, 20, 10, 5, 2.5, 1.2, 0.6]
    for a, b, c in zip(bounds[:-1], bounds[1:], cols):
        for z1, z0 in zip(zs[:-1], zs[1:]):
            quad(pen, P, [(a, 0, z0), (b, 0, z0), (b, 0, z1), (a, 0, z1)], P.fog(c, (z0 + z1) / 2))


def wet(arr, seed, k=0.08):
    a = arr.copy()
    h, w = a.shape[:2]
    a[..., :3] *= 1 + _noise_tex(w, h, seed, scale=5, k=k)
    return a


# ======================================================================== MAIN STREET
@lru_cache(None)
def street_set(variant="main"):
    """variant: main (тротуар слева, фасад с витриной) | memory (знакомая улица с остановкой)."""
    w, h = LW, LH
    P = Persp()
    sky = vgrad(w, h, [(0, (5, 7, 14)), (0.3, (12, 16, 28)), (0.44, (40, 46, 64)), (0.6, (16, 18, 24)), (1, (10, 11, 14))])
    pen = Pen(w, h, ss=2)
    wl = Pen(w, h, ss=1)
    # дальний город
    r = np.random.default_rng(3)
    x = -400
    while x < w + 400:
        bw = r.uniform(30, 90); bh = r.uniform(30, 160)
        pen.rect(x, P.vy - bh, x + bw, P.vy + 4, (20, 24, 34))
        x += bw
    ground(pen, P, -20, 30, xs=(-3.2, -0.55, -0.4, 7.6, 7.75),
           cols=[(26, 28, 34), (44, 46, 54), (58, 60, 66), (22, 24, 30), (58, 60, 66), (40, 42, 50)])
    # разметка
    for z in range(4, 80, 6):
        quad(pen, P, [(3.4, 0.0, z), (3.6, 0.0, z), (3.6, 0.0, z + 2.5), (3.4, 0.0, z + 2.5)], P.fog((70, 70, 72), z))
    lamps, carl = [], []
    facade(pen, wl, P, 11.0, 4, 90, 22, (30, 32, 42), 11, win_p=0.12, side=1)
    facade(pen, wl, P, -3.2, 1.0, 90, 16, (34, 36, 46), 12, win_p=0.10, side=-1)
    if variant == "main":
        # витрина магазина на левом фасаде (z 9..15) — «тот самый магазин»
        quad(pen, P, [(-3.19, 0.4, 9), (-3.19, 2.6, 9), (-3.19, 2.6, 15), (-3.19, 0.4, 15)], (120, 96, 60))
        quad(wl, P, [(-3.19, 0.4, 9), (-3.19, 2.6, 9), (-3.19, 2.6, 15), (-3.19, 0.4, 15)], (130, 100, 60))
        quad(pen, P, [(-3.15, 2.7, 9.5), (-3.15, 3.2, 9.5), (-3.15, 3.2, 14.5), (-3.15, 2.7, 14.5)], (40, 46, 60))
        for (x0, x1, z0) in ((0.0, 1.8, 7), (0.0, 1.8, 19), (0.1, 1.9, 34), (8.2, 9.9, 13), (8.2, 9.9, 28)):
            car(pen, P, x0, x1, z0, lights=None)
    else:  # память: остановка, без машин у бордюра
        z0, z1 = 10, 15
        c = P.fog((40, 44, 52), 12)
        quad(pen, P, [(-1.0, 2.5, z0), (-3.0, 2.5, z0), (-3.0, 2.5, z1), (-1.0, 2.5, z1)], c)
        for zz in (z0, z1):
            pen.line([P.p(-1.0, 0, zz), P.p(-1.0, 2.5, zz)], c, P.size(zz, 0.08))
        quad(pen, P, [(-2.95, 0, z0), (-2.95, 2.4, z0), (-2.95, 2.4, z1), (-2.95, 0, z1)], (30, 34, 44, 160))
        sp = P.p(-0.9, 2.2, 9.2)
        pen.rrect(sp[0] - 20, sp[1] - 50, sp[0] + 20, sp[1] - 10, 6, (40, 70, 60))
        pen.line([sp, P.p(-0.9, 0, 9.2)], (20, 22, 26), 3)
    for z in (5, 15, 25, 35, 45, 60):
        lamp(pen, P, -0.8, z, lamps, side=-1)
    for z in (10, 30, 50):
        lamp(pen, P, 7.9, z, lamps, side=1)
    base = wet(pen.arr(), 5)
    wlights = wl.arr(blur=1.2)[..., :3].copy()
    lights = lamp_lights(w, h, lamps)
    return {"sky": Layer(solid(w, h, sky), 0.4), "base": Layer(base, 1.0), "win": Layer(wlights, 1.0, add=True),
            "lights": Layer(lights, 1.0, add=True), "P": P, "lamp_info": lamps}


# ======================================================================== CROSSING (вид сбоку)
@lru_cache(None)
def crossing_set():
    """Пешеходный переход, вид сбоку. Герой и незнакомец идут слева направо."""
    w, h = LW, LH
    p = Pen(w, h, ss=2)
    sky = vgrad(w, h, [(0, (5, 7, 14)), (0.4, (14, 18, 30)), (1, (10, 11, 14))])
    gy = h * 0.66
    r = np.random.default_rng(7)
    wl = Pen(w, h, ss=1)
    x = -50
    while x < w + 50:  # дома на той стороне
        bw = r.uniform(180, 340); bh = r.uniform(700, 1200)
        col = tuple(int(v * r.uniform(0.85, 1.1)) for v in (26, 28, 38))
        p.rect(x, gy - bh, x + bw, gy - 120, col)
        for yy in range(int(gy - bh + 40), int(gy - 200), 90):
            for xx in range(int(x + 25), int(x + bw - 40), 70):
                lit = r.random() < 0.1
                c = (14, 16, 22) if not lit else (200, 150, 90)
                p.rect(xx, yy, xx + 34, yy + 50, c)
                if lit:
                    wl.rect(xx, yy, xx + 34, yy + 50, (120, 90, 50))
        x += bw + 6
    p.rect(0, gy - 120, w, gy - 100, (48, 50, 56))  # тротуар дальний
    p.rect(0, gy - 100, w, gy + 260, (20, 22, 28))  # дорога
    for i in range(9):  # зебра (в перспективе сбоку — полосы)
        x0 = 300 + i * 80
        p.poly([(x0, gy - 96), (x0 + 40, gy - 96), (x0 + 90, gy + 256), (x0 + 30, gy + 256)], (88, 90, 94))
    p.rect(0, gy + 260, w, gy + 290, (64, 66, 72))  # бордюр
    p.rect(0, gy + 290, w, h, (34, 36, 42))
    base = wet(p.arr(), 9)
    lamps = []
    lights = np.zeros((h, w, 3), np.float32)
    for lx in (150, 1150):
        pp = Pen(w, h, ss=2)
        lights += radial(w, h, lx + 60, gy - 690, 40, (255, 236, 200), power=1.4, k=1.4)
        lights += radial(w, h, lx + 60, gy - 690, 500, LAMP, power=2.0, k=0.3)
        lights += radial(w, h, lx + 60, gy + 300, 520, LAMP, power=1.6, k=0.35, sy=0.35)
    pp = Pen(w, h, ss=2)
    for lx in (150, 1150):
        pp.line([(lx, gy + 320), (lx, gy - 700)], (12, 13, 16), 12)
        pp.line([(lx, gy - 700), (lx + 70, gy - 700)], (12, 13, 16), 10)
        pp.ellipse(lx + 65, gy - 694, 26, 10, (14, 14, 16))
    # светофор
    pp.line([(980, gy + 330), (980, gy - 300)], (12, 13, 16), 10)
    pp.rrect(950, gy - 420, 1010, gy - 290, 8, (10, 10, 12))
    lights += radial(w, h, 980, gy - 330, 22, (80, 255, 140), power=1.2, k=0.9)
    lights += radial(w, h, 980, gy - 330, 140, (60, 200, 120), power=2, k=0.15)
    return {"sky": Layer(solid(w, h, sky), 0.5), "base": Layer(base, 1.0), "posts": Layer(pp.arr(), 1.0),
            "win": Layer(wl.arr(blur=1)[..., :3].copy(), 1.0, add=True), "lights": Layer(lights, 1.0, add=True),
            "gy": gy}


# ======================================================================== SHOP WINDOW (витрина + отражение)
@lru_cache(None)
def shopwindow_set():
    """Герой у витрины. В стекле — интерьер магазина и отражение улицы (с незнакомцем)."""
    w, h = LW, LH
    p = Pen(w, h, ss=2)
    p.rect(0, 0, w, h, (24, 26, 32))
    gx0, gy0, gx1, gy1 = 120, 360, w - 120, 1640  # стекло витрины
    # интерьер: полки с товарами, тёплый свет
    p.rect(gx0, gy0, gx1, gy1, (70, 56, 40))
    r = np.random.default_rng(2)
    for i, yy in enumerate(range(gy0 + 160, gy1 - 100, 230)):
        p.rect(gx0 + 40, yy, gx1 - 40, yy + 16, (40, 32, 26))
        x = gx0 + 60
        while x < gx1 - 100:
            bw = r.uniform(30, 80); bh = r.uniform(60, 170)
            kc = r.uniform(0.6, 1.2)
            c = tuple(int(v * kc) for v in (110, 92, 72))
            p.rect(x, yy - bh, x + bw, yy, c)
            x += bw + r.uniform(6, 20)
    p.rect(gx0, gy0, gx1, gy0 + 90, (40, 34, 30))
    p.text(w / 2, gy0 + 46, "П Р О Д У К Т Ы", FONT_BOLD, 52, (150, 130, 100), anchor="mm")
    interior = p.arr()
    # рама витрины и стена
    fr = Pen(w, h, ss=2)
    fr.rect(0, 0, w, h, (22, 24, 30))
    fr.rect(gx0, gy0, gx1, gy1, (0, 0, 0, 0))
    fr.rect(gx0 - 20, gy0 - 20, gx1 + 20, gy0, (12, 12, 14)); fr.rect(gx0 - 20, gy1, gx1 + 20, gy1 + 30, (12, 12, 14))
    fr.rect(gx0 - 20, gy0, gx0, gy1, (12, 12, 14)); fr.rect(gx1, gy0, gx1 + 20, gy1, (12, 12, 14))
    fr.rect(w / 2 - 10, gy0, w / 2 + 10, gy1, (12, 12, 14))
    fr.rect(0, gy1 + 30, w, h, (30, 32, 38))  # тротуар
    frame = textured(fr.arr(), 23, k=0.05, stain=0.12)
    # отражение улицы (зеркально, тёмное, синеватое): дома напротив, фонарь
    rf = Pen(w, h, ss=1)
    rf.rect(gx0, gy0, gx1, gy1, (14, 18, 30))
    x = gx0
    while x < gx1:
        bw = r.uniform(120, 260); bh = r.uniform(300, 800)
        rf.rect(x, gy0 + 200 + r.uniform(0, 200), x + bw, gy1, (22, 26, 38))
        x += bw + 10
    rf.rect(gx0, gy1 - 220, gx1, gy1, (18, 20, 28))
    refl = rf.arr(blur=3)
    refl_l = radial(w, h, w * 0.78, gy0 + 380, 200, LAMP, power=2, k=0.55)
    glow = radial(w, h, w / 2, (gy0 + gy1) / 2, 900, (255, 200, 130), power=1.6, k=0.5, sy=1.2)
    glow += radial(w, h, w / 2, gy1 + 300, 700, (255, 200, 130), power=1.6, k=0.35, sy=0.35)
    mask = np.zeros((h, w), np.float32); mask[gy0:gy1, gx0:gx1] = 1
    return {"interior": Layer(interior, 1.0), "refl": Layer(refl, 1.0), "refl_light": Layer(refl_l, 1.0, add=True),
            "frame": Layer(frame, 1.0), "glow": Layer(glow, 1.0, add=True), "glass": (gx0, gy0, gx1, gy1),
            "mask": mask}


# ======================================================================== ALLEY
@lru_cache(None)
def alley_set(facing="exit"):
    """Узкий переулок: слева старые гаражи, справа высокая стена дома. facing: exit | entrance."""
    w, h = LW, LH
    P = Persp(vy=LH * 0.47, fogd=26.0)
    sky = vgrad(w, h, [(0, (4, 5, 10)), (0.4, (12, 15, 26)), (1, (8, 9, 12))])
    pen = Pen(w, h, ss=2)
    wl = Pen(w, h, ss=1)
    xl, xr = -2.6, 2.4
    if facing == "entrance":
        xl, xr = -2.4, 2.6
    end = 60
    # дальний выход: свет главной улицы
    a, b = P.p(xl, 0, end), P.p(xr, 8, end)
    exit_col = (120, 104, 76) if facing == "exit" else (60, 62, 72)
    pen.rect(a[0], b[1], b[0], a[1], exit_col)
    ground(pen, P, xl, xr, cols=[(22, 24, 28)])
    gar_side, wall_side = (xl, xr) if facing == "exit" else (xr, xl)
    # стена дома (высокая)
    facade(pen, wl, P, wall_side, 0.8, end, 20, (30, 30, 36), 31, win_p=0.04, step=4.0)
    # гаражи: ряд металлических ворот
    z = 1.0
    n = 1
    r = np.random.default_rng(5)
    while z < end:
        z1 = z + 3.2
        col = tuple(int(v * r.uniform(0.8, 1.15)) for v in (46, 48, 52))
        quad(pen, P, [(gar_side, 0, z), (gar_side, 2.6, z), (gar_side, 2.6, z1), (gar_side, 0, z1)], P.fog(col, z))
        quad(pen, P, [(gar_side, 0.05, z + 0.25), (gar_side, 2.25, z + 0.25), (gar_side, 2.25, z1 - 0.25),
                      (gar_side, 0.05, z1 - 0.25)], P.fog(tuple(int(v * 0.75) for v in col), z))
        for k in range(1, 6):  # рёбра ворот
            yy = 0.05 + k * 0.37
            pen.line([P.p(gar_side, yy, z + 0.25), P.p(gar_side, yy, z1 - 0.25)], P.fog((30, 30, 34), z),
                     max(1, P.size(z, 0.03)))
        if z < 25:
            c = P.p(gar_side, 1.9, z + 1.6)
            pen.text(c[0], c[1], str(n), FONT_BOLD, max(8, P.size(z, 0.4)), P.fog((110, 106, 96), z), anchor="mm")
        # крыша гаражей и стена сверху
        quad(pen, P, [(gar_side, 2.6, z), (gar_side, 3.2, z), (gar_side, 3.2, z1), (gar_side, 2.6, z1)],
             P.fog((20, 20, 22), z))
        z = z1; n += 1
    # высокая стена за гаражами
    facade(pen, wl, P, gar_side + (0.6 if gar_side > 0 else -0.6), 4, end, 16, (24, 24, 30), 33, win_p=0.03,
           step=5.0)
    # водосточные трубы
    for zz in (6, 15, 27, 41):
        pen.line([P.p(wall_side - 0.05 * np.sign(wall_side), 0, zz), P.p(wall_side - 0.05 * np.sign(wall_side), 14, zz)],
                 P.fog((40, 40, 44), zz), max(2, P.size(zz, 0.1)))
    # лужи
    pd = Pen(w, h, ss=1)
    for (px, pz, s) in ((0.2, 4, 1.2), (-0.8, 9, 1.0), (0.6, 17, 1.4), (-0.3, 30, 1.6)):
        c = P.p(px, 0, pz)
        pd.ellipse(c[0], c[1], P.size(pz, s), P.size(pz, s) * 0.18, (255, 255, 255, 255))
    puddles = cv2.GaussianBlur(pd.arr()[..., 3], (0, 0), 2)
    # тусклые фонари на стене
    lamps = []
    for zz in (8, 22, 40):
        hx = P.p(wall_side - 0.3 * np.sign(wall_side), 4.2, zz)
        pen.rect(hx[0] - P.size(zz, 0.25), hx[1] - P.size(zz, 0.1), hx[0] + P.size(zz, 0.25), hx[1] + P.size(zz, 0.1),
                 (16, 16, 18))
        lamps.append(dict(head=(hx[0], hx[1] + P.size(zz, 0.15)), ground=P.p(wall_side * 0.4, 0, zz),
                          r=P.size(zz, 2.6), z=zz))
    base = wet(textured(pen.arr(), 41, k=0.05, stain=0.15), 43)
    lights = [lamp_lights(w, h, [L], k=0.75) for L in lamps]
    exit_glow = radial(w, h, (a[0] + b[0]) / 2, a[1] - 60, 520, (255, 200, 130) if facing == "exit" else (120, 130, 160),
                       power=1.6, k=0.7 if facing == "exit" else 0.35, sy=1.4)
    return {"sky": Layer(solid(w, h, sky), 0.5), "base": Layer(base, 1.0), "win": Layer(wl.arr(blur=1)[..., :3].copy(), 1.0, add=True),
            "lamps": [Layer(L, 1.0, add=True) for L in lights], "exit": Layer(exit_glow, 1.0, add=True),
            "puddles": puddles, "P": P, "exit_xy": ((a[0] + b[0]) / 2, a[1]), "end": end}


# ======================================================================== MAIN LIT STREET (24 часа + парковка)
@lru_cache(None)
def lit_street_set(view="arrive"):
    """Освещённая главная улица: круглосуточный магазин и охраняемая парковка.
    view: arrive (герой выходит из переулка) | across (вид с той стороны дороги, из-за спины незнакомца)."""
    w, h = LW, LH
    sky = vgrad(w, h, [(0, (5, 7, 14)), (0.35, (14, 18, 30)), (0.5, (40, 44, 60)), (1, (12, 13, 16))])
    p = Pen(w, h, ss=2)
    wl = Pen(w, h, ss=1)
    gy = h * 0.6
    # дома на фоне
    r = np.random.default_rng(17)
    x = -40
    while x < w + 40:
        bw = r.uniform(200, 360); bh = r.uniform(500, 1000)
        p.rect(x, gy - bh, x + bw, gy, tuple(int(v * r.uniform(0.85, 1.1)) for v in (22, 24, 32)))
        for yy in range(int(gy - bh + 40), int(gy - 380), 90):
            for xx in range(int(x + 25), int(x + bw - 40), 70):
                if r.random() < 0.08:
                    p.rect(xx, yy, xx + 30, yy + 46, (190, 140, 80)); wl.rect(xx, yy, xx + 30, yy + 46, (110, 80, 44))
        x += bw + 4
    # магазин «24 ЧАСА» слева
    sx0, sx1, sy0 = 60, 640, gy - 360
    p.rect(sx0, sy0, sx1, gy, (36, 36, 40))
    p.rect(sx0 + 30, sy0 + 110, sx1 - 30, gy - 10, (190, 186, 170))       # яркая витрина (холодно-белая)
    for yy in (sy0 + 190, sy0 + 260):
        p.rect(sx0 + 50, yy, sx1 - 50, yy + 10, (120, 116, 106))
    p.rect(sx0 + 250, sy0 + 130, sx0 + 330, gy - 10, (150, 148, 136))       # дверь
    p.rect(sx0 + 10, sy0 + 10, sx1 - 10, sy0 + 90, (150, 30, 26))
    p.text((sx0 + sx1) / 2, sy0 + 52, "24 ЧАСА", FONT_TITLE, 58, (255, 236, 220), anchor="mm")
    # парковка справа: будка охраны, шлагбаум, сетка
    bx0, bx1 = 820, 1060
    p.rect(bx0, gy - 260, bx1, gy, (40, 42, 46))
    p.rect(bx0 + 30, gy - 220, bx1 - 30, gy - 120, (170, 160, 120))
    p.rect(bx0 - 10, gy - 280, bx1 + 10, gy - 260, (24, 24, 28))
    p.text((bx0 + bx1) / 2, gy - 300, "ОХРАНЯЕМАЯ ПАРКОВКА", FONT_BOLD, 26, (150, 150, 150), anchor="mm")
    p.rect(1060, gy - 100, 1296, gy - 86, (150, 120, 40))  # шлагбаум
    for xx in range(1080, 1296, 40):
        p.line([(xx, gy - 180), (xx, gy)], (30, 32, 36), 3)
    p.line([(1060, gy - 180), (1296, gy - 180)], (30, 32, 36), 3)
    # тротуар и дорога
    p.rect(0, gy, w, gy + 60, (60, 62, 68))
    p.rect(0, gy + 60, w, h, (22, 24, 30))
    for i in range(8):
        p.rect(i * 190, gy + 330, i * 190 + 110, gy + 350, (80, 80, 84))
    p.rect(0, h - 260, w, h - 230, (60, 62, 68))
    p.rect(0, h - 230, w, h, (36, 38, 44))
    base = wet(p.arr(), 19)
    lights = radial(w, h, (sx0 + sx1) / 2, gy - 150, 600, (230, 225, 200), power=1.6, k=0.6, sy=0.9)
    lights += radial(w, h, (sx0 + sx1) / 2, gy + 220, 520, (230, 225, 200), power=1.6, k=0.4, sy=0.35)
    lights += radial(w, h, (bx0 + bx1) / 2, gy - 170, 300, (255, 220, 150), power=1.8, k=0.45)
    lights += radial(w, h, (bx0 + bx1) / 2, gy + 200, 380, (255, 210, 130), power=1.6, k=0.3, sy=0.35)
    for lx in (720, 1220):  # фонари
        lights += radial(w, h, lx, gy - 560, 34, (255, 236, 200), power=1.3, k=1.5)
        lights += radial(w, h, lx, gy - 560, 420, LAMP, power=2, k=0.3)
        lights += radial(w, h, lx, gy + 120, 420, LAMP, power=1.6, k=0.3, sy=0.35)
    posts = Pen(w, h, ss=2)
    for lx in (720, 1220):
        posts.line([(lx - 40, gy + 40), (lx - 40, gy - 570)], (12, 13, 16), 10)
        posts.line([(lx - 40, gy - 570), (lx, gy - 570)], (12, 13, 16), 8)
    return {"sky": Layer(solid(w, h, sky), 0.5), "base": Layer(base, 1.0), "posts": Layer(posts.arr(), 1.0),
            "win": Layer(wl.arr(blur=1)[..., :3].copy(), 1.0, add=True), "lights": Layer(lights, 1.0, add=True),
            "gy": gy, "shop": (sx0, sx1, sy0), "booth": (bx0, bx1)}


# ======================================================================== PHONE
PHW, PHH = 560, 1140


def phone_screen(state, t=0.0, extra=None):
    """Экран телефона. state: missed | unknown | shown_photo | wrong | dial."""
    p = Pen(PHW, PHH, ss=2)
    sw, sh = PHW, PHH
    p.rect(0, 0, sw, sh, (10, 12, 18))
    p.text(36, 34, "23:18" if state != "wrong" else "23:31", FONT_SEMI, 26, (225, 228, 235))
    for i in range(4):
        p.rect(sw - 128 + i * 12, 52 - i * 6, sw - 120 + i * 12, 58, (225, 228, 235))
    p.rrect(sw - 74, 38, sw - 34, 58, 4, (225, 228, 235))
    if state == "missed":
        n = extra or 3
        p.text(sw / 2, 200, "23:18", FONT_TITLE, 120, (232, 234, 240), anchor="mm")
        msgs = [("Макс", "Ты дошёл?"), ("Макс", "Ответь, пожалуйста"), ("Макс", "Перезвони мне СРОЧНО")]
        for i, (a, b) in enumerate(msgs[:n]):
            y = 330 + i * 150
            p.rrect(24, y, sw - 24, y + 130, 26, (34, 38, 50, 235))
            p.ellipse(78, y + 64, 34, 34, (60, 110, 200))
            p.text(78, y + 64, "М", FONT_BOLD, 34, (240, 244, 250), anchor="mm")
            p.text(130, y + 42, a, FONT_BOLD, 28, (240, 242, 246), anchor="lm")
            p.text(130, y + 88, b, FONT_SEMI, 26, (200, 204, 214), anchor="lm")
            p.text(sw - 44, y + 42, "сейчас", FONT_SEMI, 20, (150, 154, 164), anchor="rm")
    if state in ("unknown", "wrong"):
        p.rect(0, 80, sw, 200, (20, 22, 30))
        p.ellipse(70, 140, 38, 38, (60, 62, 70))
        p.text(70, 140, "?", FONT_BOLD, 40, (220, 220, 225), anchor="mm")
        p.text(124, 120, "Неизвестный номер", FONT_BOLD, 28, (235, 236, 240), anchor="lm")
        p.text(124, 160, "+7 ••• ••• •• ••", FONT_SEMI, 24, (150, 152, 160), anchor="lm")
        vis = 1.0 if extra is None else extra
        if vis > 0:
            if state == "unknown":
                lines = ["НЕ", "ОБОРАЧИВАЙСЯ.", "БЕГИ."]
            else:
                lines = ["ТЫ ВЫБРАЛ", "НЕ ТО", "МЕСТО."]
            by = 300
            p.rrect(30, by, sw - 30, by + 60 + 76 * len(lines), 34, (52, 54, 64, int(255 * vis)))
            for i, s in enumerate(lines):
                p.text(58, by + 68 + i * 76, s, FONT_TITLE, 52, tuple(int(v * vis) for v in (250, 250, 252)),
                       anchor="lm")
            p.text(sw - 50, by + 92 + 76 * len(lines), "23:" + ("24" if state == "unknown" else "31"), FONT_SEMI, 20,
                   (150, 152, 160), anchor="rm")
    if state == "dial":
        p.text(sw / 2, 260, "1 1 2", FONT_TITLE, 96, (235, 236, 240), anchor="mm")
        for i in range(9):
            cx_, cy_ = 120 + (i % 3) * 160, 440 + (i // 3) * 160
            p.ellipse(cx_, cy_, 62, 62, (40, 42, 50))
            p.text(cx_, cy_, str(i + 1), FONT_SEMI, 44, (230, 230, 236), anchor="mm")
    a = p.arr()
    m = Pen(PHW, PHH, ss=2)
    m.rrect(0, 0, PHW, PHH, 56, (255, 255, 255))
    return a * m.arr()[..., 3:4]


def phone_body(w, h, cx, cy, scale=1.0):
    pb = Pen(w, h, ss=2)
    hw, hh = (PHW / 2 + 22) * scale, (PHH / 2 + 26) * scale
    pb.rrect(cx - hw, cy - hh, cx + hw, cy + hh, 76 * scale, (8, 8, 10))
    pb.rrect(cx - hw + 4, cy - hh + 4, cx + hw - 4, cy + hh - 4, 72 * scale, (30, 32, 38))
    pb.rrect(cx - hw + 12, cy - hh + 14, cx + hw - 12, cy + hh - 14, 64 * scale, (4, 4, 6))
    return pb.arr()


def hand_layer(w, h, cx, cy, side=1, skin=(52, 42, 38), sleeve=(22, 25, 32)):
    """Рука, держащая телефон (side=1 правая). sleeve — рукав (у героя — его куртка)."""
    ph = Pen(w, h, ss=2)
    s = side
    ph.poly([(cx + s * 60, h + 60), (cx + s * 10, cy + 420), (cx + s * 320, cy + 330), (cx + s * 600, h + 60)], sleeve)
    ph.ellipse(cx + s * 150, cy + 390, 250, 170, skin)
    palm = ph.arr(blur=1.2)
    pf = Pen(w, h, ss=2)
    for i in range(4):
        y = cy + 70 + i * 94
        x0 = cx - s * (PHW / 2 + 40)
        pf.rrect(min(x0, x0 + s * 56), y, max(x0, x0 + s * 56), y + 70, 30, tuple(int(v * (1 - i * 0.08)) for v in skin))
    xt = cx + s * (PHW / 2 - 30)
    pf.rrect(min(xt, xt + s * 70), cy + 170, max(xt, xt + s * 70), cy + 320, 34, skin)
    return palm, pf.arr(blur=1.2)
