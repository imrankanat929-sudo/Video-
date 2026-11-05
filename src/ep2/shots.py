"""«За мной кто-то идёт» — сцены и таймлайн (9:16, 30 fps), привязка к озвучке через cues."""
import math
from functools import lru_cache
import numpy as np
import cv2
from ..config import W, H, FPS, FONT_TITLE, FONT_BOLD, FONT_SEMI
from ..cues import C
from ..gfx import (Cam, Layer, compose, grade, smooth, ease_io, lerp, clamp01, flicker, fbm, hash1, rim, paste,
                   text_layer, sl_radial, sl_cone, rgb, Pen, radial, solid, vgrad)
from . import sets as S
from . import chars as CH
from .. import character as CH1

c = C()
LAMP = S.LAMP


# ---------------------------------------------------------------- атмосфера: дождь и туман (экранные слои)
class Rain:
    def __init__(self, n=420, seed=1, speed=(1700, 2600), length=(18, 46), k=0.22, angle=0.12):
        r = np.random.default_rng(seed)
        self.x = r.uniform(-200, W + 200, n); self.y = r.uniform(0, H, n)
        self.v = r.uniform(*speed, n); self.l = r.uniform(*length, n); self.b = r.uniform(0.3, 1.0, n)
        self.k, self.a = k, angle

    def draw(self, img, t, gain=1.0):
        if gain <= 0:
            return img
        buf = np.zeros((H, W), np.float32)
        ys = (self.y + self.v * t) % (H + 100) - 50
        xs = (self.x + self.v * t * self.a) % (W + 400) - 200
        for x, y, l, b in zip(xs, ys, self.l, self.b):
            cv2.line(buf, (int(x), int(y)), (int(x - l * self.a), int(y - l)), float(b), 1, cv2.LINE_AA)
        buf = cv2.GaussianBlur(buf, (0, 0), 0.7)
        img += buf[..., None] * rgb((150, 165, 195)) * self.k * gain
        return img


@lru_cache(None)
def _fog_tex(seed):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (H // 24 + 2, (W * 2) // 24 + 2)).astype(np.float32)
    n = cv2.resize(n, (W * 2, H), interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), 30)
    n = (n - n.min()) / (n.max() - n.min())
    return n


def fog(img, t, horizon=0.45, k=0.35, speed=18.0, color=(70, 80, 104), lit=None):
    a = _fog_tex(1); b = _fog_tex(2)
    ox = int(t * speed) % W; ob = int(t * speed * 0.6 + 300) % W
    f = a[:, ox:ox + W] * 0.6 + b[:, ob:ob + W] * 0.4
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    prof = np.exp(-((yy - horizon) / 0.22) ** 2) * 0.8 + 0.25
    f = (f * prof * k)[..., None]
    col = rgb(color)
    if lit is not None:
        col = col + lit * 0.5
    return img * (1 - f * 0.6) + f * col


def put(img, spr, x, y, mul=1.0, blur=0.0, alpha=1.0):
    """Спрайт (rgba, foot_x, foot_y) в экранные координаты (x, y — точка стоп)."""
    a, fx, fy = spr[0], spr[1], spr[2]
    if blur > 0.3:
        a = cv2.GaussianBlur(a, (0, 0), blur)
    if mul != 1.0 or alpha != 1.0:
        a = a.copy()
        a[..., :3] *= mul * alpha
        a[..., 3:] *= alpha
    return paste(img, a, x - fx, y - fy)


def scr(pt, cam, depth=1.0):
    z = 1 + (cam.zoom - 1) * depth
    return (W / 2 + (pt[0] - S.LW / 2 - cam.x * depth) * z, H / 2 + (pt[1] - S.LH / 2 - cam.y * depth) * z)


def breathe(cam, t, amp=4.0, seed=3):
    cam.x += (fbm(t * 0.15, seed) - 0.5) * amp * 4
    cam.y += (fbm(t * 0.13, seed + 1) - 0.5) * amp * 3
    cam.rot += (fbm(t * 0.1, seed + 2) - 0.5) * 0.004
    return cam


# ---------------------------------------------------------------- кэш спрайтов
def q(v, s):
    return int(round(v / s) * s)


@lru_cache(600)
def hero_spr(h, view="back", ph=0, light10=10, turn10=0, phone=False, stride10=10, rimk=0):
    a, fx, fy = CH.hero(h, view, phase=ph / 16, stride=stride10 / 10, light=light10 / 10, head_turn=turn10 / 10,
                        arm_phone=phone)
    if rimk:
        a = rim(a, 0, -4, LAMP, rimk / 10)
        a = rim(a, 4, 0, (150, 170, 220), rimk / 20)
    return a, fx, fy


@lru_cache(400)
def stranger_spr(h, view="front", ph=0, light10=10, arm10=0, phone=False, stride10=10, rimk=0):
    a, fx, fy = CH.stranger(h, view, phase=ph / 16, stride=stride10 / 10, light=light10 / 10, arm_up=arm10 / 10,
                            phone=phone)
    if rimk:
        a = rim(a, 0, -5, LAMP, rimk / 10)
        a = rim(a, -4, 0, LAMP, rimk / 20)
    return a, fx, fy


@lru_cache(200)
def fig_spr(h, kind, light10=10, ph=0, stride10=0, wave10=0):
    return CH.figure(h, kind, light=light10 / 10, phase=ph / 16, stride=stride10 / 10, wave=wave10 / 10)


def _side(h, ph, who):
    """Вид сбоку при ходьбе — та же фигура героя/незнакомца в профиль (на основе общего шагающего силуэта)."""
    keep = (CH1.HOODIE, CH1.HOODIE_FOLD, CH1.PANTS, CH1.PANTS_SH, CH1.HAIR, CH1.SKIN, CH1.SHOE, CH1.SOLE)
    if who == "hero":
        CH1.HOODIE, CH1.HOODIE_FOLD, CH1.PANTS, CH1.PANTS_SH = CH.JACKET, CH.JACKET_HI, CH.PANTS, CH.PANTS_SH
        CH1.HAIR, CH1.SKIN, CH1.SHOE, CH1.SOLE = CH.HAIR, CH.SKIN_SH, CH.SHOE, CH.SOLE
    else:
        CH1.HOODIE, CH1.HOODIE_FOLD, CH1.PANTS, CH1.PANTS_SH = CH.S_JACKET, CH.S_JACKET_HI, CH.S_PANTS, CH.S_PANTS
        CH1.HAIR, CH1.SKIN, CH1.SHOE, CH1.SOLE = (8, 8, 9), (14, 12, 12), (8, 8, 9), (20, 20, 22)
    try:
        a, fx, fy, _ = CH1.timur_side(h, phase=ph, light=1.0, flashlight=False)
    finally:
        (CH1.HOODIE, CH1.HOODIE_FOLD, CH1.PANTS, CH1.PANTS_SH, CH1.HAIR, CH1.SKIN, CH1.SHOE, CH1.SOLE) = keep
    if who != "hero":  # шире в плечах
        a = cv2.resize(a, (int(a.shape[1] * 1.18), a.shape[0]))
        fx *= 1.18
    return a, fx, fy


@lru_cache(200)
def side_spr(h, ph, who):
    a, fx, fy = _side(h, ph / 16, who)
    return rim(a, -4, -3, LAMP, 0.6), fx, fy


def walk_phase(t, rate=1.0):
    return q((t * rate) % 1.0 * 16, 1) % 16


# ---------------------------------------------------------------- базовые классы шотов
class Shot:
    tin, din = "cut", 0.0

    def __init__(self, t0, t1, tin=None, din=None, **kw):
        self.t0, self.t1 = t0, t1
        if tin:
            self.tin = tin
        if din is not None:
            self.din = din
        self.kw = kw
        self.rain = Rain(seed=int(t0 * 10) % 97)

    def p(self, t):
        return clamp01((t - self.t0) / max(1e-6, self.t1 - self.t0))

    def gkw(self, t):
        return dict(warmth=-0.35, desat=0.22, grain=0.06, vignette=1.25)

    def draw(self, t):
        raise NotImplementedError

    def frame(self, t):
        return grade(self.draw(t), t, **self.gkw(t))


class Black(Shot):
    def draw(self, t):
        return np.zeros((H, W, 3), np.float32)


def street_bg(t, cam, rain=None, lights_k=1.0, fogk=0.35, variant="main", flick=None):
    s = S.street_set(variant)
    lk = lights_k * (1.0 if flick is None else flick)
    img = compose([s["sky"], s["base"], (s["win"], 0.9), (s["lights"], lk)], cam)
    img = fog(img, t, horizon=0.44, k=fogk)
    return img, s


# ================================================================ 1. ОН ИДЁТ ЗА ТОБОЙ
class Title:
    @staticmethod
    @lru_cache(None)
    def layers():
        t1 = text_layer([("ЗА МНОЙ", W / 2, 300), ("КТО-ТО ИДЁТ", W / 2, 430)], FONT_TITLE, 128, color=(240, 238, 232),
                        glow=20, glow_color=(255, 190, 90))
        return t1


class WalkAway(Shot):
    """Герой спиной уходит по тротуару; камера медленно приближается."""

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        cam = Cam(1.0 + 0.10 * pr, -170, P.vy - S.LH / 2 + 120)
        breathe(cam, t, 3)
        img, s = street_bg(t, cam)
        hh = q(lerp(640, 760, ease_io(pr)), 8)
        spr = hero_spr(hh, "back", walk_phase(t), 8, 0, False, 10, 8)
        put(img, spr, W * 0.40, H * 0.86 + 0.06 * hh)
        img = self.rain.draw(img, t)
        if self.kw.get("title"):
            a = smooth(0.25, 0.9, t) * (1 - smooth(3.6, 4.4, t))
            tl = Title.layers()
            img = tl[..., :3] * a + img * (1 - tl[..., 3:4] * a)
        return img


class FollowerFar(Shot):
    """Обратный план: герой идёт к камере (в тени), позади далеко — высокий силуэт."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    def gkw(self, t):
        kw = super().gkw(t)
        dark = self.kw.get("dark_at")
        if dark:  # затемнение на «один и тот же человек»
            d = smooth(dark, dark + 0.6, t) * (1 - smooth(dark + 1.6, dark + 2.4, t))
            kw["exposure"] = 1.0 - 0.55 * d
            kw["vignette"] = 1.25 + 1.5 * d
        return kw

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        z0 = self.kw.get("zoom", (1.05, 1.22))
        cam = Cam(lerp(z0[0], z0[1], ease_io(pr)), -150, P.vy - S.LH / 2 + 60)
        breathe(cam, t, 3)
        img, s = street_bg(t, cam)
        # незнакомец далеко, под фонарём
        sz = self.kw.get("sz", (15, 13))
        zf = lerp(sz[0], sz[1], pr)
        foot = scr(P.p(-1.6, 0, zf), cam)
        hh = q(P.size(zf, 2.05) * cam.zoom, 2)
        spd = self.kw.get("speed", 1.0)
        sp = stranger_spr(max(24, hh), "front", walk_phase(t, 0.9 * spd), 5, 0, False, 10, 6)
        put(img, sp, foot[0], foot[1], blur=1.2)
        # герой ближе к камере, лицом к нам, но в тени (контровой свет фонаря)
        if self.kw.get("hero", True):
            hh2 = q(lerp(560, 600, pr), 8)
            sp2 = hero_spr(hh2, "front", walk_phase(t), 4, 0, False, 10, 10)
            put(img, sp2, W * 0.58, H * 0.97)
        img = self.rain.draw(img, t)
        return img


# ================================================================ 2. ПОВТОРЯЕТ КАЖДЫЙ ШАГ
class TurnRight(Shot):
    """Герой (или незнакомец) уходит спиной и сворачивает направо."""

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        cam = Cam(1.12, 60, P.vy - S.LH / 2 + 160, 0.0)
        breathe(cam, t, 2)
        img, s = street_bg(t, cam)
        who = self.kw["who"]
        k = ease_io(pr)
        if who == "hero":
            x = lerp(W * 0.42, W * 1.05, smooth(0.35, 1.0, pr))
            hh = q(lerp(600, 520, k), 8)
            put(img, hero_spr(hh, "back", walk_phase(t), 8, q(4 * smooth(0.25, 0.5, pr), 1), False, 10, 8), x, H * 0.84)
        else:
            x = lerp(W * 0.36, W * 1.1, smooth(0.3, 1.0, pr))
            hh = q(lerp(1250, 980, k), 8)
            sp = stranger_spr(hh, "back", walk_phase(t, 0.9), 6, 0, False, 10, 4)
            put(img, sp, x, H * 1.02 + 0.06 * hh * (1 - k))
        img = self.rain.draw(img, t)
        return img


class Crossing(Shot):
    """Переход дороги — вид сбоку."""

    def draw(self, t):
        pr = self.p(t)
        s = S.crossing_set()
        who = self.kw["who"]
        cam = Cam(1.05 + (0.08 * pr if who == "stranger" else 0), -60 + 140 * pr, 120)
        breathe(cam, t, 2)
        img = compose([s["sky"], s["base"], (s["win"], 0.9), s["posts"], s["lights"]], cam)
        img = fog(img, t, horizon=0.45, k=0.3)
        gy = s["gy"]
        x = lerp(80, S.LW - 60, pr)
        foot = scr((x, gy + 120), cam)
        if who == "hero":
            hh = q(560 * cam.zoom, 8)
            put(img, side_spr(hh, walk_phase(t, 1.0), "hero"), foot[0], foot[1])
        else:
            hh = q(700 * cam.zoom, 8)
            put(img, side_spr(hh, walk_phase(t, 0.9), "stranger"), foot[0], foot[1])
        img = self.rain.draw(img, t)
        return img


# ================================================================ 3/8. ВИТРИНА И ОТРАЖЕНИЕ
class ShopWindow(Shot):
    """kw: phone (герой с телефоном), refl_at (когда в отражении проявляется мужчина), push (зум в отражение),
    turn_at (герой медленно поворачивает голову), dark_at (затемнение)."""

    def gkw(self, t):
        kw = dict(warmth=-0.2, desat=0.2, grain=0.06, vignette=1.35)
        d = self.kw.get("dark_at")
        if d:
            k = smooth(d, d + 1.2, t)
            kw["exposure"] = 1 - 0.8 * k
            kw["vignette"] = 1.35 + 2.0 * k
        return kw

    def draw(self, t):
        s = S.shopwindow_set()
        pr = self.p(t)
        gx0, gy0, gx1, gy1 = s["glass"]
        z0, z1 = self.kw.get("zoom", (1.0, 1.12))
        foc = self.kw.get("focus", (0, 0))
        k = ease_io(pr)
        cam = Cam(lerp(z0, z1, k), foc[0] * k, -80 + foc[1] * k)
        breathe(cam, t, 2)
        ra = self.kw.get("refl_at", 1e9)
        rv = smooth(ra, ra + 1.5, t)
        # отражение: улица + высокий мужчина (зеркально)
        img = compose([s["interior"], (s["refl"], 0.5), (s["refl_light"], 0.6)], cam)
        if rv > 0:  # высокий мужчина в отражении — тёмный силуэт за плечом героя
            man = refl_man()
            img = compose([(man, 0.85 * rv)], cam, base=img)
        img = compose([s["frame"], (s["glow"], 0.9)], cam, base=img)
        # отражение героя в стекле (тёмный силуэт по центру) + сам герой спиной
        turn = 0
        ta = self.kw.get("turn_at")
        if ta:
            turn = q(8 * smooth(ta, ta + 2.2, t), 1)
        hh = q(1020 * cam.zoom, 8)
        sp = hero_spr(hh, "back", 0, 6, turn, self.kw.get("phone", False), 10, 6)
        put(img, sp, W * 0.48, H * 1.08)
        if self.kw.get("phone"):
            img += sl_radial(W * 0.52, H * 0.66, 260, power=2, k=0.35)[..., None] * rgb((150, 180, 255))
        img = self.rain.draw(img, t, 0.6)
        return img


@lru_cache(None)
def refl_man():
    s = S.shopwindow_set()
    gx0, gy0, gx1, gy1 = s["glass"]
    sp = stranger_spr(1000, "front", 0, 4, 0, False, 10, 6)
    a = np.zeros((S.LH, S.LW, 4), np.float32)
    paste(a, sp[0][:, ::-1].copy(), S.LW * 0.74 - (sp[0].shape[1] - sp[1]), gy1 - 40 - sp[2])
    return Layer(a * s["mask"][..., None], 1.0)


# ================================================================ 4. ТЕЛЕФОН У НЕЗНАКОМЦА
class TwoPhones(Shot):
    """Незнакомец вдали тоже достаёт телефон: экран подсвечивает тень на лице."""

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        zf = 12
        wp = P.p(-1.7, 0, zf)
        hz = P.size(zf, 2.05)
        cam = Cam(2.0 + 0.35 * ease_io(pr), wp[0] - S.LW / 2, wp[1] - hz * 0.55 - S.LH / 2)
        breathe(cam, t, 2)
        img, s = street_bg(t, cam)
        foot = scr(wp, cam)
        hh = q(P.size(zf, 2.05) * cam.zoom, 4)
        arm = smooth(c["his_phone"], c["his_phone"] + 1.0, t)
        sp = stranger_spr(hh, "front", 0, 5, q(arm * 10, 1), arm > 0.3, 10, 6)
        put(img, sp, foot[0], foot[1])
        if arm > 0.3:
            px, py = foot[0] + hh * 0.17, foot[1] - hh * 0.85
            img += sl_radial(px, py, hh * 0.35, power=2, k=0.7 * arm)[..., None] * rgb((160, 190, 255))
        img = self.rain.draw(img, t)
        return img


class HeroPhoneBack(Shot):
    """Герой спиной достаёт телефон (крупно по пояс)."""

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        cam = Cam(1.2, -100, P.vy - S.LH / 2 + 100)
        breathe(cam, t, 2)
        img, s = street_bg(t, cam)
        hh = q(lerp(1500, 1580, pr), 8)
        ph = smooth(self.t0 + 0.4, self.t0 + 1.0, t) > 0.5
        sp = hero_spr(hh, "back", 0, 7, 0, ph, 10, 8)
        put(img, sp, W * 0.46, H * 1.5)
        if ph:
            img += sl_radial(W * 0.52, H * 0.86, 320, power=2, k=0.4)[..., None] * rgb((150, 180, 255))
        img = self.rain.draw(img, t)
        return img


# ================================================================ 5. ДВАДЦАТЬ МИНУТ НАЗАД (воспоминание)
class Memory(Shot):
    """mode: friend | bus | alone. Синеватое размытое воспоминание."""

    def gkw(self, t):
        return dict(warmth=-0.6, desat=0.5, grain=0.075, vignette=1.8, exposure=1.05)

    def draw(self, t):
        pr = self.p(t)
        mode = self.kw["mode"]
        P = S.street_set("memory")["P"]
        if mode == "bus":
            cam = Cam(1.25, lerp(-260, -120, ease_io(pr)), P.vy - S.LH / 2 + 260)
        else:
            cam = Cam(1.05 + 0.06 * pr, lerp(-120, -40, pr), P.vy - S.LH / 2 + 140)
        breathe(cam, t, 2)
        img, s = street_bg(t, cam, variant="memory", fogk=0.45)
        if mode == "friend":
            wave = smooth(self.t0 + 0.6, self.t0 + 1.2, t) * (1 - smooth(self.t0 + 2.6, self.t0 + 3.0, t))
            leave = smooth(self.t0 + 2.6, self.t1, t)
            fx = lerp(W * 0.62, W * 0.95, leave)
            fh = q(lerp(820, 700, leave), 8)
            put(img, fig_spr(fh, "friend", 7, walk_phase(t) if leave > 0 else 0, 10 if leave > 0 else 0,
                             q(wave * 10, 1) if wave > 0 else 0), fx, H * 0.9)
            put(img, hero_spr(q(860, 8), "back", 0, 7, q(3 * (1 - leave), 1), False, 10, 6), W * 0.38, H * 0.94)
        elif mode == "bus":
            # редкая машина: фары проходят по кадру
            u = clamp01((t - self.t0 - 0.8) / 2.4)
            if 0 < u < 1:
                x = lerp(-300, W + 300, u)
                img += sl_radial(x, H * 0.56, 520, power=1.8, k=0.6)[..., None] * rgb((230, 230, 255))
                img += sl_radial(x + 80, H * 0.6, 120, power=1.2, k=1.2)[..., None] * rgb((255, 250, 240))
        else:
            hh = q(lerp(700, 560, pr), 8)
            put(img, hero_spr(hh, "back", walk_phase(t), 7, 0, False, 10, 6), W * 0.42, H * 0.86)
        img = self.rain.draw(img, t, 0.5)
        bl = cv2.GaussianBlur(img, (0, 0), 5)
        m = _vmask()
        return img * (1 - m) + bl * m


@lru_cache(None)
def _vmask():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip((d - 0.45) / 0.6, 0, 1)[..., None]


# ================================================================ 6/7. ШАГИ, УСКОРЕНИЕ
class WalkFast(Shot):
    """Герой ускоряет шаг — спиной, камера трясётся сильнее."""

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        cam = Cam(1.1 + 0.15 * pr, -160, P.vy - S.LH / 2 + 120)
        breathe(cam, t, 3)
        cam.shake(t, 6, seed=5, rate=6)
        img, s = street_bg(t, cam)
        hh = q(lerp(700, 640, pr), 8)
        put(img, hero_spr(hh, "back", walk_phase(t, 1.5), 8, 0, False, 13, 8), W * 0.42, H * 0.88)
        img = self.rain.draw(img, t)
        return img


class StrangerStop(Shot):
    """Незнакомец стоит примерно в 10 метрах под фонарём; медленный zoom-in."""

    def draw(self, t):
        pr = self.p(t)
        P = S.street_set()["P"]
        cam = Cam(1.25 + 0.45 * ease_io(pr), -260, P.vy - S.LH / 2 + 120)
        breathe(cam, t, 2)
        fl = 0.85 + 0.15 * flicker(t, 3, rate=6, depth=0.5, dropout=0.04)
        img, s = street_bg(t, cam, flick=fl)
        zf = 11
        foot = scr(P.p(-1.5, 0, zf), cam)
        hh = q(P.size(zf, 2.05) * cam.zoom, 4)
        put(img, stranger_spr(hh, "front", 0, 5, 0, False, 10, 8), foot[0], foot[1])
        img = self.rain.draw(img, t)
        return img


# ================================================================ 9. ПЕРЕУЛОК
class AlleyShot(Shot):
    """facing exit|entrance. kw: hero (back walk), stranger_z (силуэт в глубине), shake, run, second (второй у выхода),
    fg_stranger (первый мужчина на переднем плане), headlights_at."""

    def gkw(self, t):
        return dict(warmth=-0.3, desat=0.25, grain=0.07, vignette=1.5, exposure=self.kw.get("exp", 1.1))

    def draw(self, t):
        pr = self.p(t)
        facing = self.kw.get("facing", "exit")
        s = S.alley_set(facing)
        P = s["P"]
        z0, z1 = self.kw.get("zoom", (1.0, 1.12))
        cam = Cam(lerp(z0, z1, ease_io(pr)), self.kw.get("cx", 0), P.vy - S.LH / 2 + self.kw.get("cy", 160))
        breathe(cam, t, 3)
        sh = self.kw.get("shake", 2.0)
        cam.shake(t, sh, seed=7, rate=5)
        # удары/хлопок: тряска
        for key in ("door",):
            if key in self.kw.get("hits", ()):
                k0 = c[key]
                cam.shake(t, 18 * smooth(k0, k0 + 0.05, t) * (1 - smooth(k0 + 0.1, k0 + 0.6, t)), seed=11, rate=30)
        lamps = [(L, 0.9 * flicker(t, 40 + i, rate=7, depth=0.6 if i != 1 else 0.95, dropout=0.06 if i != 1 else 0.25))
                 for i, L in enumerate(s["lamps"])]
        img = compose([s["sky"], (s["base"], 1, 1.35), (s["win"], 0.8), (s["exit"], self.kw.get("exit_k", 1.0))] + lamps,
                      cam)
        # фары машины на выходе
        ha = self.kw.get("headlights_at")
        if ha:
            u = clamp01((t - ha) / 2.2)
            if 0 < u < 1:
                ex = scr(s["exit_xy"], cam)
                sweep = math.sin(u * math.pi)
                img += sl_cone(ex[0] + (u - 0.5) * 600, ex[1] - 40, math.pi / 2 + (0.5 - u) * 0.8, 0.5, 2200,
                               k=1.3 * sweep)[..., None] * rgb((230, 235, 255))
                img *= 1 + 0.6 * sweep
        img = fog(img, t, horizon=0.47, k=0.4, color=(60, 68, 90))
        ex = scr(s["exit_xy"], cam)
        # силуэт в глубине (у входа/выхода)
        sz = self.kw.get("stranger_z")
        if sz:
            vis = smooth(sz[2], sz[2] + 0.6, t) if len(sz) > 2 else 1.0
            zz = lerp(sz[0], sz[1], pr)
            foot = scr(P.p(0.2, 0, zz), cam)
            hh = q(P.size(zz, 2.05) * cam.zoom, 2)
            if vis > 0:
                put(img, stranger_spr(max(20, hh), "front", walk_phase(t, 0.9) if sz[0] != sz[1] else 0, 3, 0, False,
                                      10, 10), foot[0], foot[1], alpha=vis, blur=self.kw.get("stranger_blur", 0))
        if self.kw.get("second"):
            vis = smooth(c["movement"], c["movement"] + 1.2, t)
            zz = 24
            foot = scr(P.p(0.4, 0, zz), cam)
            hh = q(P.size(zz, 1.85) * cam.zoom, 2)
            if vis > 0:
                put(img, fig_spr(max(20, hh), "second", 2), foot[0], foot[1], alpha=vis)
        hero = self.kw.get("hero")
        if hero:
            hz = hero.get("h", (700, 640))
            hh = q(lerp(hz[0], hz[1], pr), 8)
            stride = hero.get("stride", 1.0)
            walking = hero.get("walk", True)
            ph = walk_phase(t, 1.0 * stride) if walking else 0
            turn = 0
            if hero.get("turn_at"):
                turn = q(10 * smooth(hero["turn_at"], hero["turn_at"] + 0.9, t), 1)
            sb = hero.get("step_back")
            yoff = 0
            if sb:
                yoff = 60 * ease_io(clamp01((t - sb) / 0.6))
                hh = q(hh * (1 + 0.06 * ease_io(clamp01((t - sb) / 0.6))), 8)
            put(img, hero_spr(hh, hero.get("view", "back"), ph, 6, turn, hero.get("phone", False), q(stride * 10, 1), 7),
                W * hero.get("x", 0.46), H * hero.get("y", 0.9) + yoff)
            if hero.get("phone"):
                img += sl_radial(W * 0.52, H * 0.66, 220, power=2, k=0.3)[..., None] * rgb((150, 180, 255))
        fgs = self.kw.get("fg_stranger")
        if fgs:  # первый мужчина позади героя — тёмный размытый край кадра
            grow = 1 + 0.12 * ease_io(clamp01((t - c["step_fwd"]) / 0.7))
            hh = q(2300 * grow, 8)
            sp = stranger_spr(hh, "back", 0, 3, 0, False, 10, 0)
            put(img, sp, W * 0.08, H * 1.55 * (1 + 0.1 * (grow - 1)), blur=9, mul=0.6)
        img = self.rain.draw(img, t, 0.7)
        return img


# ================================================================ ТЕЛЕФОН КРУПНО
class PhoneShot(Shot):
    """kw: bg (alley|lit|dark), script(t) -> (state, extra), vib_at (кортеж), blur_stranger."""

    def gkw(self, t):
        return dict(warmth=-0.25, desat=0.15, grain=0.06, vignette=1.3)

    def draw(self, t):
        pr = self.p(t)
        state, extra = self.kw["script"](t)
        lay = phone_layers(self.kw.get("bg", "alley"))
        cam = Cam(lerp(1.08, 1.24, ease_io(pr)), 0, 20)
        breathe(cam, t, 4)
        cam.shake(t, 2.0, seed=4, rate=1.5)
        for a in self.kw.get("vib_at", ()):
            if a <= t < a + 1.3 and (t - a) % 0.45 < 0.3:
                cam.x += math.sin(t * 190) * 5
        scr_img = screen_cached(state, extra)
        L = Layer(scr_img, 1.0, ox=lay["cx"] - S.PHW / 2, oy=lay["cy"] - S.PHH / 2, ref=(S.LW, S.LH))
        img = compose([lay["bg"]], cam)
        if self.kw.get("blur_stranger"):  # размытый силуэт позади
            k = smooth(self.kw["blur_stranger"], self.kw["blur_stranger"] + 1.0, t)
            if k > 0:
                sp = stranger_spr(1500, "front", 0, 4, 0, False, 10, 6)
                put(img, sp, W * 0.78, H * 1.05, blur=14, alpha=0.9 * k)
        img = compose([(lay["palm"], 1, 0.7), lay["body"], L, (lay["hand"], 1, 0.6)], cam, base=img)
        col = (170, 190, 255) if state != "unknown" else (200, 210, 255)
        img += sl_radial(W / 2, H / 2, 1300, power=2.4, k=0.18)[..., None] * rgb(col)
        img = self.rain.draw(img, t, 0.4)
        return img


@lru_cache(None)
def phone_layers(bg):
    w, h = S.LW, S.LH
    cx, cy = w / 2, h / 2 - 40
    if bg == "lit":
        g = vgrad(w, h, [(0, (12, 14, 22)), (0.5, (40, 40, 48)), (1, (14, 14, 18))])
        for (x, y, r_, col) in ((w * 0.2, h * 0.45, 260, (230, 225, 200)), (w * 0.85, h * 0.5, 200, (255, 210, 130)),
                                (w * 0.6, h * 0.3, 120, (255, 196, 110))):
            g += radial(w, h, x, y, r_, col, power=1.3, k=0.3)
    else:
        g = vgrad(w, h, [(0, (6, 7, 12)), (0.5, (18, 20, 28)), (1, (8, 8, 10))])
        g += radial(w, h, w * 0.75, h * 0.3, 240, LAMP, power=1.4, k=0.18)
        g += radial(w, h, w * 0.5, h * 0.12, 300, (255, 200, 130), power=1.4, k=0.1)
    bgl = Layer(solid(w, h, cv2.GaussianBlur(g, (0, 0), 8)), 0.4)
    body = S.phone_body(w, h, cx, cy)
    palm, hand = S.hand_layer(w, h, cx, cy, side=1)
    return {"bg": bgl, "body": Layer(body, 1.0), "palm": Layer(palm, 1.0), "hand": Layer(hand, 1.0), "cx": cx, "cy": cy}


@lru_cache(64)
def screen_cached(state, extra):
    if state == "photo":
        return photo_screen(extra)
    return S.phone_screen(state, extra=extra)


def script_missed(t):
    m = c["missed"]
    n = 1 + int(clamp01((t - m) / 2.4) * 2.99) if t >= m else 1
    return "missed", n


def script_unknown(t):
    d = c["dont"]
    return "unknown", round(smooth(d - 0.1, d + 0.25, t), 1)


def script_wrong(t):
    if t < c["another"]:
        return "dial", None
    return "wrong", round(smooth(c["wrong"] - 0.15, c["wrong"] + 0.25, t), 1)


# ---------------------------------------------------------------- «фотографии» на телефоне незнакомца
@lru_cache(4)
def photo_image(kind):
    """Снимок героя: shop (у витрины) | lit (на освещённой улице, рядом кто-то стоит)."""
    if kind == "shop":
        img = ShopWindow(0, 10, zoom=(1.0, 1.0)).draw(3.0)
        img = grade(img, 0.0, warmth=-0.1, desat=0.25, grain=0.03, vignette=0.8)
    else:
        s = S.lit_street_set()
        img = compose([s["sky"], s["base"], s["posts"], (s["win"], 0.9), s["lights"]], Cam(1.05, -60, 260))
        put(img, hero_spr(q(300, 8), "back", 0, 7, 0, False, 10, 6), W * 0.5, H * 0.66)
        put(img, fig_spr(330, "second", 1), W * 0.585, H * 0.665, mul=0.6)
        img = grade(img, 0.0, warmth=-0.1, desat=0.25, grain=0.03, vignette=0.8)
    return img


def photo_screen(kind):
    p = Pen(S.PHW, S.PHH, ss=2)
    p.rect(0, 0, S.PHW, S.PHH, (6, 6, 8))
    p.text(S.PHW / 2, 64, "Фото", FONT_BOLD, 30, (230, 232, 238), anchor="mm")
    p.text(S.PHW / 2, S.PHH - 110, "Сегодня, " + ("23:02" if kind == "shop" else "23:30"), FONT_SEMI, 26,
           (170, 172, 180), anchor="mm")
    a = p.arr()
    img = photo_image(kind)
    ph = int(S.PHW * 1.55)
    y0 = (S.PHH - ph) // 2
    im = cv2.resize(img[int(H * 0.18):int(H * 0.18) + int(W * 1.55)], (S.PHW, ph), interpolation=cv2.INTER_AREA)
    a[y0:y0 + ph, :, :3] = im
    a[y0:y0 + ph, :, 3] = 1
    m = Pen(S.PHW, S.PHH, ss=2)
    m.rrect(0, 0, S.PHW, S.PHH, 56, (255, 255, 255))
    return a * m.arr()[..., 3:4]


# ================================================================ 14/15. НЕЗНАКОМЕЦ РЯДОМ
class StrangerClose(Shot):
    """Незнакомец совсем близко (лицо в тени). kw: hit_at (удар + тряска), step_at, arm (None|'up'|'down')."""

    def gkw(self, t):
        return dict(warmth=-0.3, desat=0.25, grain=0.075, vignette=1.6, exposure=1.1)

    def draw(self, t):
        pr = self.p(t)
        s = S.alley_set("entrance")
        P = s["P"]
        zz = self.kw.get("zoom", (1.0, 1.12))
        cam = Cam(lerp(zz[0], zz[1], ease_io(pr)), self.kw.get("cx", 0), P.vy - S.LH / 2 + 120)
        breathe(cam, t, 2)
        hit = self.kw.get("hit_at")
        if hit:
            cam.shake(t, 22 * smooth(hit, hit + 0.04, t) * (1 - smooth(hit + 0.1, hit + 0.8, t)), seed=21, rate=28)
        lamps = [(L, 0.8 * flicker(t, 60 + i, rate=7, depth=0.7, dropout=0.1)) for i, L in enumerate(s["lamps"])]
        img = compose([s["sky"], (s["base"], 1, 1.3), (s["win"], 0.7), (s["exit"], 1.0)] + lamps, cam)
        img = fog(img, t, horizon=0.47, k=0.4, color=(60, 68, 90))
        step = 1.0
        if self.kw.get("step_at"):
            step = 1 + 0.08 * ease_io(clamp01((t - self.kw["step_at"]) / 0.8))
        arm = 0.0
        if self.kw.get("arm") == "up":
            arm = ease_io(clamp01((t - self.t0 - 0.3) / 1.6))
        elif self.kw.get("arm") == "down":
            arm = 1 - ease_io(clamp01((t - self.t0 - 0.2) / 1.6))
        hh = q(1700 * step * cam.zoom, 8)
        sp = stranger_spr(hh, "front", 0, 4, q(arm * 10, 1), arm > 0.2, 10, 9)
        sx = self.kw.get("sx", 0.5)
        put(img, sp, W * sx, H * 1.12 + (step - 1) * 600)
        if arm > 0.5:
            hx = W * sx + hh * 0.18
            hy = H * 1.12 - hh * (0.48 - 0.33 * arm + 0.03)
            img += sl_radial(hx, hy, 260, power=2, k=0.5 * arm)[..., None] * rgb((170, 190, 255))
        img = self.rain.draw(img, t, 0.7)
        return img


class HeroTurn(Shot):
    """Герой крупно спиной медленно оборачивается."""

    def gkw(self, t):
        return dict(warmth=-0.3, desat=0.25, grain=0.075, vignette=1.6, exposure=1.1)

    def draw(self, t):
        pr = self.p(t)
        s = S.alley_set("exit")
        P = s["P"]
        cam = Cam(1.25 + 0.1 * pr, 0, P.vy - S.LH / 2 + 60)
        breathe(cam, t, 2)
        img = compose([s["sky"], (s["base"], 1, 1.3), (s["win"], 0.7), (s["exit"], 1.0)] + s["lamps"], cam)
        img = fog(img, t, horizon=0.47, k=0.4, color=(60, 68, 90))
        turn = q(10 * smooth(self.t0 + 0.1, self.t1 - 0.1, t), 1)
        put(img, hero_spr(1640, "back", 0, 6, turn, False, 10, 8), W * 0.5, H * 1.55)
        img = self.rain.draw(img, t, 0.7)
        return img


# ================================================================ 17. ОСВЕЩЁННАЯ УЛИЦА
class LitStreet(Shot):
    """kw: mode arrive | around | choice."""

    def gkw(self, t):
        kw = dict(warmth=-0.2, desat=0.2, grain=0.06, vignette=1.3)
        if self.kw.get("mode") == "around":
            kw["exposure"] = 1 - 0.35 * smooth(c["understood"], c["two_opts"], t)
            kw["vignette"] = 1.3 + 1.2 * smooth(c["understood"], c["two_opts"], t)
        if self.kw.get("mode") == "choice":
            kw["exposure"] = 1 - 0.3 * smooth(c["optA"], c["which"], t)
        return kw

    def draw(self, t):
        pr = self.p(t)
        s = S.lit_street_set()
        mode = self.kw["mode"]
        gy = s["gy"]
        if mode == "arrive":
            k = ease_io(pr)
            cx = lerp(-240, 240, smooth(c["seller"], c["guard"] + 1, t)) if t > c["seller"] else -240
            cam = Cam(lerp(1.3, 1.45, k), cx, gy - S.LH / 2 - 80)
        elif mode == "around":
            cam = Cam(1.12 + 0.3 * ease_io(pr), 60, gy - S.LH / 2 - 60)
        else:
            cam = Cam(1.0 + 0.04 * pr, 0, gy - S.LH / 2 - 540)
        breathe(cam, t, 2)
        img = compose([s["sky"], s["base"], s["posts"], (s["win"], 0.9), s["lights"]], cam)
        img = fog(img, t, horizon=0.55, k=0.25)
        # продавец в витрине и охранник у будки
        sx0, sx1, sy0 = s["shop"]
        seller = scr(((sx0 + sx1) / 2 + 120, gy - 20), cam)
        put(img, fig_spr(q(190 * cam.zoom, 4), "seller", 7), seller[0], seller[1], mul=0.8)
        bx0, bx1 = s["booth"]
        guard = scr((bx1 + 60, gy + 20), cam)
        put(img, fig_spr(q(230 * cam.zoom, 4), "guard", 8), guard[0], guard[1])
        if mode == "arrive":
            hk = clamp01((t - self.t0) / 2.5)
            hero_pos = scr((S.LW * 0.48, gy + 40), cam)
            hh = q(lerp(480, 320, ease_io(hk)) * cam.zoom / 1.3, 8)
            put(img, hero_spr(hh, "back", walk_phase(t) if hk < 1 else 0, 7, 0, False, 10, 6),
                lerp(W * 0.55, hero_pos[0], ease_io(hk)), lerp(H * 1.05, hero_pos[1], ease_io(hk)))
        elif mode == "around":
            a, n = c["around"], c["nobody"]
            turn = 0
            if t > a:
                turn = q(10 * math.sin(clamp01((t - a) / (n - a + 0.8)) * 2 * math.pi) * 0.9, 1)
            hero_pos = scr((S.LW * 0.48, gy + 40), cam)
            put(img, hero_spr(q(320 * cam.zoom, 8), "back", 0, 7, turn, False, 10, 6), hero_pos[0], hero_pos[1])
        else:
            hero_pos = scr((S.LW * 0.5, gy + 40), cam)
            put(img, hero_spr(q(320 * cam.zoom, 8), "back", 0, 7, 0, False, 10, 6), hero_pos[0], hero_pos[1])
            # незнакомец на переднем плане (спиной к нам) — через дорогу от героя
            put(img, stranger_spr(1500, "back", 0, 3, 0, False, 10, 4), W * 0.16, H * 1.42, mul=0.7)
        img = self.rain.draw(img, t, 0.7)
        return img


class AcrossStranger(Shot):
    """Через дорогу стоит тот самый мужчина; улыбается(не видно) и поднимает телефон."""

    def draw(self, t):
        pr = self.p(t)
        s = S.crossing_set()
        cam = Cam(1.2 + 0.35 * ease_io(pr), 80, 40)
        breathe(cam, t, 2)
        img = compose([s["sky"], s["base"], (s["win"], 0.9), s["posts"], s["lights"]], cam)
        img = fog(img, t, horizon=0.45, k=0.3)
        gy = s["gy"]
        foot = scr((S.LW * 0.62, gy - 100), cam)
        arm = ease_io(clamp01((t - c["smiled"] - 0.5) / 1.6))
        hh = q(640 * cam.zoom, 8)
        put(img, stranger_spr(hh, "front", 0, 5, q(arm * 10, 1), arm > 0.2, 10, 8), foot[0], foot[1])
        if arm > 0.5:
            hx = foot[0] + hh * 0.18
            hy = foot[1] - hh * (0.48 - 0.33 * arm + 0.03)
            img += sl_radial(hx, hy, 160, power=2, k=0.6 * arm)[..., None] * rgb((170, 190, 255))
        img = self.rain.draw(img, t)
        return img


class PhotoShot(Shot):
    """Крупно телефон незнакомца с фотографией героя. kw: kind (shop|lit), focus_at (наезд на фигуру рядом)."""

    def gkw(self, t):
        return dict(warmth=-0.25, desat=0.2, grain=0.06, vignette=1.5)

    def draw(self, t):
        pr = self.p(t)
        kind = self.kw["kind"]
        lay = phone_layers("dark")
        fa = self.kw.get("focus_at")
        z = lerp(1.08, 1.2, ease_io(pr))
        cx, cy = 0, 60
        if fa:
            k = ease_io(clamp01((t - fa) / 2.5))
            z = lerp(z, 1.9, k)
            cx = lerp(0, 60, k); cy = lerp(60, 40, k)
        cam = Cam(z, cx, cy)
        breathe(cam, t, 3)
        scr_img = screen_cached("photo", kind)
        L = Layer(scr_img, 1.0, ox=lay["cx"] - S.PHW / 2, oy=lay["cy"] - S.PHH / 2, ref=(S.LW, S.LH))
        sp = stranger_spr(3000, "front", 0, 3, 0, False, 10, 0)
        img = compose([lay["bg"]], cam)
        put(img, sp, W * 0.5, H * 2.2, blur=12, mul=0.5)
        palm, hand = hand_dark()  # рука незнакомца держит телефон (тёмная)
        img = compose([(palm, 1, 0.5), lay["body"], L, (hand, 1, 0.5)], cam, base=img)
        img += sl_radial(W / 2, H / 2, 1300, power=2.4, k=0.15)[..., None] * rgb((170, 190, 255))
        img = self.rain.draw(img, t, 0.4)
        return img


@lru_cache(None)
def hand_dark():
    lay = phone_layers("dark")
    palm, hand = S.hand_layer(S.LW, S.LH, lay["cx"], lay["cy"], side=-1, skin=(26, 22, 20), sleeve=(8, 8, 10))
    return Layer(palm, 1.0), Layer(hand, 1.0)


# ================================================================ 18. ВЫБОР
class Choice(LitStreet):
    @staticmethod
    @lru_cache(None)
    def parts():
        def card(y, letter, lines):
            p = Pen(W, H, ss=2)
            p.rrect(70, y, W - 70, y + 300, 22, (10, 12, 18, 225))
            p.rrect(70, y, 84, y + 300, 4, (255, 190, 90))
            p.text(120, y + 70, "ВАРИАНТ " + letter, FONT_TITLE, 66, (255, 196, 110), anchor="lm")
            for i, s in enumerate(lines):
                p.text(120, y + 150 + i * 56, s, FONT_SEMI, 44, (236, 236, 240), anchor="lm")
            return p.arr()
        a = card(330, "А", ["Зайти в магазин и попросить", "вызвать полицию."])
        b = card(670, "Б", ["Обратиться к охраннику", "на парковке."])
        q_ = text_layer([("КАКОЙ ВАРИАНТ", W / 2, 150), ("ВЫБЕРЕШЬ ТЫ?", W / 2, 245)], FONT_TITLE, 84,
                        color=(244, 240, 232), glow=16, glow_color=(255, 170, 80))
        cm = text_layer([("Напиши  А  или  Б  в комментариях", W / 2, 1060)], FONT_BOLD, 48, color=(236, 230, 220))
        return q_, a, b, cm

    def frame(self, t):
        img = grade(self.draw(t), t, **self.gkw(t))
        q_, a, b, cm = self.parts()
        for L, al, mv in ((q_, smooth(self.t0 + 0.3, self.t0 + 1.3, t), 0),
                          (a, smooth(c["optA"] - 0.2, c["optA"] + 0.7, t), 1),
                          (b, smooth(c["optB"] - 0.2, c["optB"] + 0.7, t), 1),
                          (cm, smooth(c["comment"], c["comment"] + 0.8, t), 0)):
            if al <= 0:
                continue
            if mv:
                L = cv2.warpAffine(L, np.float32([[1, 0, 40 * (1 - al)], [0, 1, 0]]), (W, H))
            img = L[..., :3] * al + img * (1 - L[..., 3:4] * al)
        return img


# ================================================================ TIMELINE
def build_timeline():
    T = []
    A = T.append
    A(WalkAway(0.0, c["same_man"] - 2.24, title=True))
    A(FollowerFar(c["same_man"] - 2.24, c["turn_right"], tin="fade", din=0.5, dark_at=c["same_man"]))
    A(TurnRight(c["turn_right"], c["he_too"], who="hero"))
    A(TurnRight(c["he_too"], c["cross"], who="stranger"))
    A(Crossing(c["cross"], c["same"], who="hero"))
    A(Crossing(c["same"], c["window"], who="stranger"))
    A(ShopWindow(c["window"], c["reflection"], tin="fade", din=0.5))
    A(ShopWindow(c["reflection"], c["coinc"], zoom=(1.12, 1.7), focus=(140, -220), refl_at=c["tall"] - 1.0,
                 turn_at=c["tall"] + 1.2, dark_at=c["looks"] + 0.3))
    A(FollowerFar(c["coinc"], c["phone_out"], tin="fadein", din=0.8, sz=(15, 8), zoom=(1.1, 1.25)))
    A(HeroPhoneBack(c["phone_out"], c["his_phone"] - 0.3))
    A(TwoPhones(c["his_phone"] - 0.3, c["flashback"]))
    A(Memory(c["flashback"], c["bus"], mode="friend", tin="black", din=1.0))
    A(Memory(c["bus"], c["familiar"], mode="bus", tin="fade", din=0.8))
    A(Memory(c["familiar"], c["nightmare"], mode="alone", tin="fade", din=0.8))
    A(WalkAway(c["steps"], c["not_vanish"], tin="black", din=0.8))
    A(FollowerFar(c["not_vanish"], c["speed"], tin="fade", din=0.5, sz=(19, 17)))
    A(WalkFast(c["speed"], c["he_speed"]))
    A(FollowerFar(c["he_speed"], c["shop"], sz=(17, 9), zoom=(1.2, 1.5), speed=1.8, hero=False))
    A(ShopWindow(c["shop"], c["refl2"], phone=True, tin="fade", din=0.5))
    A(ShopWindow(c["refl2"], c["ten_m"], phone=True, zoom=(1.12, 1.6), focus=(140, -220), refl_at=c["refl2"]))
    A(StrangerStop(c["ten_m"], c["decide"]))
    A(AlleyShot(c["decide"], c["steps_back"], facing="exit", tin="black", din=0.8, zoom=(1.0, 1.1),
                hero=dict(h=(900, 720))))
    A(AlleyShot(c["steps_back"], c["dark_alley"], facing="entrance", zoom=(1.05, 1.25),
                stranger_z=(55, 50, c["followed"] - 0.6)))
    A(AlleyShot(c["dark_alley"], c["phone_a"], facing="exit", zoom=(1.0, 1.2), shake=3.5, hero=dict(h=(720, 680))))
    A(PhoneShot(c["phone_a"], c["hey"], script=script_missed, bg="alley", tin="fade", din=0.4))
    A(AlleyShot(c["hey"], c["faster"], facing="exit", zoom=(1.1, 1.2), shake=5, hero=dict(h=(760, 740)),
                exp=1.0))
    A(AlleyShot(c["faster"], c["vibr"], facing="exit", zoom=(1.1, 1.45), shake=8, hero=dict(h=(700, 660), stride=1.5),
                exit_k=1.15))
    A(PhoneShot(c["vibr"], c["stop"], script=script_unknown, bg="alley", vib_at=(c["vibr"],)))
    A(AlleyShot(c["stop"], c["turned"], facing="entrance", zoom=(1.2, 1.35), stranger_z=(3.2, 3.0),
                stranger_blur=7, hero=dict(h=(1000, 1010), walk=False, x=0.4, y=1.0, view="front"), exp=0.95))
    A(HeroTurn(c["turned"], c["close"]))
    A(StrangerClose(c["close"], c["his_phone2"], hit_at=c["close"], step_at=c["finally"] + 0.6, zoom=(1.0, 1.18)))
    A(StrangerClose(c["his_phone2"], c["photo"], arm="up", zoom=(1.1, 1.2)))
    A(PhotoShot(c["photo"], c["puts_away"], kind="shop", tin="fade", din=0.4))
    A(StrangerClose(c["puts_away"], c["movement"], arm="down", zoom=(1.15, 1.45), cx=120, tin="fade", din=0.4))
    A(AlleyShot(c["movement"], c["step_back"], facing="exit", zoom=(1.2, 2.0), cy=40, second=True,
                fg_stranger=True, hero=dict(h=(760, 760), walk=False), shake=2))
    A(AlleyShot(c["step_back"], c["seize"], facing="exit", zoom=(1.6, 1.7), cy=60, second=True, fg_stranger=True,
                hero=dict(h=(760, 760), walk=False, step_back=c["step_back"]), headlights_at=c["headlights"],
                hits=("door",), shake=2.5))
    A(AlleyShot(c["seize"], c["main_st"], facing="exit", zoom=(1.2, 1.7), second=True, shake=9, exit_k=1.2,
                hero=dict(h=(760, 620), stride=1.8)))
    A(LitStreet(c["main_st"], c["call"], mode="arrive", tin="fade", din=0.8))
    A(PhoneShot(c["call"], c["head_up"], script=script_wrong, bg="lit", vib_at=(c["another"],)))
    A(AcrossStranger(c["head_up"], c["photo2"]))
    A(PhotoShot(c["photo2"], c["around"], kind="lit", focus_at=c["someone"] + 0.2, tin="fade", din=0.4))
    A(LitStreet(c["around"], c["two_opts"], mode="around"))
    A(Choice(c["two_opts"], c["END"], mode="choice", tin="fade", din=1.0))
    # затычки между шотами, если остались зазоры (например, «кошмар» -> «шаги»)
    T.sort(key=lambda s: s.t0)
    for a_, b_ in zip(T[:-1], T[1:]):
        if b_.t0 > a_.t1:
            a_.t1 = b_.t0
    return T


TIMELINE = build_timeline()


def shot_at(t):
    for i, s in enumerate(TIMELINE):
        if s.t0 <= t < s.t1:
            return i
    return len(TIMELINE) - 1


def render_frame(t):
    i = shot_at(t)
    cur = TIMELINE[i]
    nxt = TIMELINE[i + 1] if i + 1 < len(TIMELINE) else None
    if nxt is not None and nxt.tin == "black" and t >= nxt.t0 - nxt.din / 2:
        return cur.frame(t) * clamp01((nxt.t0 - t) / (nxt.din / 2))
    img = cur.frame(t)
    if cur.tin == "black" and t < cur.t0 + cur.din / 2:
        img = img * ease_io((t - cur.t0) / (cur.din / 2))
    elif cur.tin == "fadein" and t < cur.t0 + cur.din:
        img = img * ease_io((t - cur.t0) / cur.din)
    elif cur.tin == "fade" and t < cur.t0 + cur.din and i > 0:
        k = ease_io((t - cur.t0) / cur.din)
        img = img * k + TIMELINE[i - 1].frame(t) * (1 - k)
    return img
