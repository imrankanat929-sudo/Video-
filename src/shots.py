"""Сцены (шоты) по таймлайну ТЗ, привязанные к меткам озвучки (cues)."""
import math
from functools import lru_cache
import subprocess
import numpy as np
import cv2
from .config import W, H, FPS, VOICE, FONT_TITLE, FONT_BOLD, FONT_SEMI
from .cues import C
from .gfx import (Cam, Layer, compose, grade, smooth, ease_io, lerp, clamp01, flicker, fbm, hash1, rim, tint,
                  text_layer, sl_radial, sl_cone, lit, Particles, rgb, AMBER, ORANGE, RED, WARMW, solid, vgrad,
                  radial, paste, over)
from . import sets as S
from . import character as ch

c = C()


# ---------------------------------------------------------------- voice envelope (для динамика)
@lru_cache(None)
def voice_env():
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(VOICE), "-f", "s16le", "-ac", "1", "-ar", "24000", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 24000 // 100
    n = len(a) // hop
    e = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1))
    e = e / (np.percentile(e, 98) + 1e-6)
    return np.clip(e, 0, 1.5)


def env_at(t):
    e = voice_env()
    i = int(t * 100)
    return float(e[i]) if 0 <= i < len(e) else 0.0


# ---------------------------------------------------------------- sprite cache (персонажи)
@lru_cache(512)
def timur_back_spr(hgt, light10, rimdx, rimdy, rimk10, phone=False):
    a, fx, fy = ch.timur_back(hgt, light=light10 / 10, phone=phone)
    if rimk10:
        a = rim(a, rimdx, rimdy, AMBER, rimk10 / 10)
        a = rim(a, -rimdx, rimdy, AMBER, rimk10 / 20)
    return a, fx, fy


@lru_cache(64)
def timur_side_spr(hgt, ph100, light10, flashlight):
    a, fx, fy, torch = ch.timur_side(hgt, phase=ph100 / 100, light=light10 / 10, flashlight=flashlight)
    a = rim(a, -5, -2, ORANGE, 0.5)
    return a, fx, fy, torch


@lru_cache(256)
def person_spr(hgt, kind, turn10, seated=True, light10=10):
    a, fx, fy = ch.person(hgt, kind=kind, head_turn=turn10 / 10, seated=seated, light=light10 / 10)
    return a, fx, fy


def sprite(arr, foot_x, foot_y, wx, wy, depth=1.0, ref=(S.LW, S.LH)):
    """Спрайт с «точкой стоп» в мировых координатах (wx, wy)."""
    return Layer(arr, depth, ox=wx - foot_x, oy=wy - foot_y, ref=ref)


def breathe(cam, t, amp=4.0, seed=3):
    cam.x += (fbm(t * 0.15, seed) - 0.5) * amp * 4
    cam.y += (fbm(t * 0.13, seed + 1) - 0.5) * amp * 3
    cam.rot += (fbm(t * 0.1, seed + 2) - 0.5) * 0.004
    return cam


class Shot:
    tin = "cut"   # cut | fade | black | fadein
    din = 0.0
    grade_kw = {}

    def __init__(self, t0, t1, tin=None, din=None):
        self.t0, self.t1 = t0, t1
        if tin:
            self.tin = tin
        if din is not None:
            self.din = din

    def p(self, t):
        return clamp01((t - self.t0) / max(1e-6, self.t1 - self.t0))

    def draw(self, t):
        raise NotImplementedError

    def gkw(self, t):
        return self.grade_kw

    def frame(self, t):
        img = self.draw(t)
        return grade(img, t, **self.gkw(t))


class Black(Shot):
    def draw(self, t):
        return np.zeros((H, W, 3), np.float32)

    def frame(self, t):
        return grade(self.draw(t), t, grain=0.03)


# ================================================================ 0. HOOK
class Hook(Shot):
    grade_kw = dict(warmth=0.3, desat=0.15, red_shadow=1.0, grain=0.06)

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.ash = Particles(140, seed=2, color=(255, 150, 80), size=(1, 2.6), speed=(8, 30), k=0.5)

    @staticmethod
    @lru_cache(None)
    def titles():
        t1 = text_layer([("А ЧТО, ЕСЛИ…?", W / 2, H * 0.40)], FONT_TITLE, 150, color=(238, 230, 218), glow=18,
                        glow_color=(200, 40, 20))
        t2 = text_layer([("СЕРИЯ №1  ·  АТОМНАЯ БОМБА", W / 2, H * 0.53)], FONT_BOLD, 40, color=(214, 120, 70))
        return t1, t2

    def draw(self, t):
        s = S.city_set("hook")
        pr = self.p(t)
        cam = breathe(Cam(1.02 + 0.12 * ease_io(pr), 0, -40 + 40 * pr), t)
        pulse = 0.6 + 0.4 * smooth(7.6, 8.6, t) * (1 - smooth(9.0, 10.8, t))
        img = compose([s["sky"], (s["glow"], pulse), s["b0"], (s["w0"], 0.6), s["b1"], (s["w1"], 0.7), s["b2"],
                       (s["w2"], 0.8)], cam)
        img = self.ash.draw(img, t)
        t1, t2 = self.titles()
        a1 = smooth(0.4, 2.0, t) * (1 - smooth(8.2, 9.6, t)) * (0.92 + 0.08 * flicker(t, 4, depth=0.3, dropout=0.03))
        a2 = smooth(2.0, 3.2, t) * (1 - smooth(8.0, 9.4, t))
        img = t1[..., :3] * a1 + img * (1 - t1[..., 3:4] * a1)
        img = t2[..., :3] * a2 + img * (1 - t2[..., 3:4] * a2)
        return img


# ================================================================ 1-3. WINDOW (day → flash → aftermath)
WINC = ((S.WIN_RECT[0] + S.WIN_RECT[2]) / 2, (S.WIN_RECT[1] + S.WIN_RECT[3]) / 2)
FLASH_XY = (1420, 800)


class WindowShot(Shot):
    """Квартира: город в окне, силуэт Тимура. mode: day | day2 | after."""

    def __init__(self, t0, t1, mode, z0, z1, tin="cut", din=0.0):
        super().__init__(t0, t1, tin, din)
        self.mode = mode
        self.z0, self.z1 = z0, z1

    def gkw(self, t):
        if self.mode == "after":
            return dict(warmth=0.5, desat=0.3, red_shadow=1.2, grain=0.065)
        fl = c["flash"]
        e = 1.0 + 0.6 * smooth(fl, fl + 0.1, t) * (1 - smooth(fl + 1.0, fl + 5.0, t))
        return dict(warmth=0.25 + 0.5 * smooth(fl, fl + 2, t), desat=0.35, grain=0.05, exposure=e)

    def flash(self, t):
        fl = c["flash"]
        if t < fl - 0.4:
            return 0.0, 0.0
        pre = 0.15 * smooth(fl - 0.4, fl, t)  # точка разгорается
        f = pre + smooth(fl, fl + 0.08, t) * (1.0 - 0.75 * smooth(fl + 0.5, fl + 4.5, t))
        white = smooth(fl - 0.02, fl + 0.1, t) * (1 - smooth(fl + 0.45, fl + 2.2, t))
        return f, white

    def timur_pose(self, t):
        """(x, y_foot, height) в координатах комнаты."""
        fl = c["flash"]
        base = (1360, 1085, 560)
        back = (1500, 1235, 700)
        if self.mode == "after":
            return back
        k = ease_io(clamp01((t - (fl + 1.0)) / 1.8)) if self.mode == "day2" else 0.0
        return tuple(lerp(a, b, k) for a, b in zip(base, back))

    def draw(self, t):
        mood = "after" if self.mode == "after" else "day"
        city = S.city_set(mood)
        room = S.room_window_set(mood)
        pr = self.p(t)
        z = lerp(self.z0, self.z1, ease_io(pr))
        cam = Cam(z, (WINC[0] - S.LW / 2) * 0.6 * pr, (WINC[1] - S.LH / 2) * 0.5 * pr)
        breathe(cam, t, 3)
        f, white = (0.0, 0.0)
        lampk = 0.0
        roomk = 1.0
        if self.mode == "day2":
            f, white = self.flash(t)
            fl = c["flash"]
            cam.zoom += 0.10 * ease_io(clamp01((t - fl) / 0.35)) * (1 - 0.4 * smooth(fl + 1, fl + 5, t))
            cam.shake(t, 14 * smooth(fl, fl + 0.1, t) * (1 - smooth(fl + 0.3, fl + 2.5, t)), seed=5)
            roomk = 1.0 + 2.5 * f
        if self.mode == "after":
            r0 = c["rumble"]
            shake = 16 * smooth(r0, r0 + 0.6, t) * (1 - smooth(r0 + 1.4, r0 + 3.5, t))
            g0 = c["glass"]
            shake += 5 * smooth(g0, g0 + 0.2, t) * (1 - smooth(g0 + 1.5, g0 + 3.0, t))
            cam.shake(t, shake, seed=9, rate=22)
            lampk = 0.75 if t < g0 else 0.75 * flicker(t, 3, rate=12, depth=0.9, dropout=0.25)
            roomk = 0.55 + 0.6 * lampk
        sky_mul = 1.0 + 5 * white
        layers = [(city["sky"], 1, sky_mul)]
        if mood == "after":
            layers += [city["smoke"], (city["glow"], 1.0)]
        layers += [city["b0"], (city["w0"], 0.5), city["b1"], (city["w1"], 0.6), city["b2"], (city["w2"], 0.7)]
        if f > 0:
            layers += [(city["wm0"], 2.5 * f), (city["wm1"], 2.5 * f), (city["wm2"], 2.5 * f)]
        img = compose(layers, cam)
        if f > 0:  # вспышка у горизонта (экранные координаты)
            sx, sy = self._to_screen(FLASH_XY, cam, 0.25)
            img += sl_radial(sx, sy, 160 + 1400 * f, power=1.8, k=2.6 * f)[..., None] * rgb((255, 236, 210))
        tx, ty, th = self.timur_pose(t)
        light = 3 if mood == "after" else 4
        spr = timur_back_spr(int(th), light, 0, -6, 12 if mood == "day" else 9, phone=self.mode == "day2")
        tl = sprite(spr[0], spr[1], spr[2], tx, ty, 1.0)
        rk = roomk
        rl = [(room["room"], 1, rk), (room["spill"], 1.0 + 3 * f), (room["lamp"], 1, rk)]
        if lampk:
            rl += [(room["lamp_glow"], lampk), (room["lamp_bulb"], lampk)]
        rl += [(room["shelf"], 1, rk), (tl, 1, 0.7 + 1.5 * f), (room["curtain"], 1, rk)]
        img = compose(rl, cam, base=img)
        if self.mode == "day2" and t < c["flash"] + 0.5:  # свет телефона у Тимура
            sx, sy = self._to_screen((tx + 40, ty - th * 0.62), cam, 1.0)
            img += sl_radial(sx, sy, 160, power=2, k=0.25)[..., None] * rgb((150, 180, 255))
        if mood == "day" and self.mode != "day2":
            tf, tg = S.table_fg()
            img = compose([tf], cam, base=img)
        if white > 0:
            img = img * (1 - white) + white * 1.6
        return img

    @staticmethod
    def _to_screen(pt, cam, depth):
        z = 1 + (cam.zoom - 1) * depth
        return (W / 2 + (pt[0] - S.LW / 2 - cam.x * depth) * z, H / 2 + (pt[1] - S.LH / 2 - cam.y * depth) * z)


# ================================================================ phone on table
class PhoneTable(Shot):
    grade_kw = dict(warmth=0.2, desat=0.25, grain=0.05)

    def draw(self, t):
        s = S.phone_table_set()
        pr = self.p(t)
        cam = breathe(Cam(0.95 + 0.16 * ease_io(pr), 0, -30 * pr, -0.06), t, 2)
        v0, n0 = c["phone_vibrate"], c["notif"]
        vib = 0.0
        for a in (v0 + 0.1, n0 - 0.2):
            if a <= t < a + 1.3:
                vib = 1.0 if (t - a) % 0.45 < 0.3 else 0.0
        if vib:
            cam.x += math.sin(t * 190) * 3.5
            cam.y += math.cos(t * 170) * 2.5
        on = smooth(v0 + 0.15, v0 + 0.4, t)
        if t < c["opened"] + 0.4:
            state, prog = ("notif", ease_io((t - n0) / 0.5)) if t >= n0 else ("lock", 1)
        else:
            state, prog = "alert", 1
        scr = phone_screen_cached(state, int(prog * 20), 0)
        L = Layer(scr, 1.0, ox=s["cx"] - S.PHW / 2, oy=s["cy"] - S.PHH / 2, ref=(S.LW, S.LH))
        amb = 0.55
        img = compose([(s["table"], 1, amb)], cam)
        img = compose([(L, on)], cam, base=img)
        col = (255, 90, 70) if state == "alert" else (170, 190, 255)
        img += sl_radial(W / 2, H / 2, 950, power=2.4, k=0.22 * on)[..., None] * rgb(col)
        return img


@lru_cache(64)
def phone_screen_cached(state, prog20, tq, extra=None):
    return S.phone_screen(state, t=tq / 4, prog=prog20 / 20, extra=extra)


# ================================================================ phone in hand
class PhoneHand(Shot):
    def __init__(self, t0, t1, bg, script, tin="cut", din=0.0, vib_at=()):
        super().__init__(t0, t1, tin, din)
        self.bg, self.script, self.vib_at = bg, script, vib_at

    def gkw(self, t):
        return dict(warmth=0.35, desat=0.25, grain=0.06, red_shadow=0.8)

    def draw(self, t):
        s = S.phone_hand_set(self.bg)
        pr = self.p(t)
        cam = breathe(Cam(0.86 + 0.08 * ease_io(pr), 0, 70), t, 5, seed=11)
        cam.shake(t, 2.0, seed=4, rate=1.5)  # руки слегка дрожат
        for a in self.vib_at:
            if a <= t < a + 1.2 and (t - a) % 0.45 < 0.3:
                cam.x += math.sin(t * 190) * 4
        state, prog, tq, extra = self.script(t)
        scr = phone_screen_cached(state, prog, tq, extra)
        L = Layer(scr, 1.0, ox=s["cx"] - S.PHW / 2, oy=s["cy"] - S.PHH / 2, ref=(S.LW, S.LH))
        img = compose([s["bg"], (s["palm"], 1, 0.7), s["body"], L, (s["hand"], 1, 0.6)], cam)
        col = (255, 70, 60) if state in ("alert", "msg", "final") else (160, 180, 255)
        img += sl_radial(W / 2, H / 2, 1100, power=2.5, k=0.18)[..., None] * rgb(col)
        return img


def script_nosignal(t):
    s0, cl = c["signal_lost"], c["called"]
    if t < cl:
        return "nosignal", 20, 0, "Сеть недоступна"
    if t < cl + 2.4:
        return "calling", 20, int((t - cl) * 4) % 12, "Мама"
    if t < cl + 3.2:
        return "nosignal", 20, 0, "Мама"
    if t < cl + 5.6:
        return "calling", 20, int((t - cl) * 4) % 12, "Папа"
    return "nosignal", 20, 0, "Папа"


def script_msg(t):
    p2, ms = c["phone2"], c["msg_screen"]
    if t < ms:
        return "notif", int(20 * ease_io((t - p2 - 0.3) / 0.6)), 0, None
    vis = tuple(round(smooth(c[k], c[k] + 0.5, t), 1) for k in ("msg1", "msg2", "msg3"))
    return "msg", 20, 0, vis


def script_final(t):
    tl = c["time_limited"]
    return "final", 20, int(max(0, t - tl) * 4) if t > tl else 0, None


# ================================================================ TV room pan
class TVRoom(Shot):
    grade_kw = dict(warmth=0.4, desat=0.3, grain=0.07, red_shadow=1.0)

    def draw(self, t):
        s = S.tv_room_set()
        pr = self.p(t)
        cam = breathe(Cam(1.08, -420 + 700 * ease_io(pr), 0), t, 3)
        lamp = 0.5 * flicker(t, 8, rate=10, depth=0.9, dropout=0.3)
        static = 0.55 + 0.45 * float(hash1(int(t * 24), 3))
        img = compose([s["sky"], s["smoke"], s["city"], (s["room"], 1, 0.6 + 0.6 * lamp)], cam,
                      base=None)
        # «снег» на экране ТВ
        x0, y0, x1, y1 = S.TV_RECT
        r = np.random.default_rng(int(t * 24))
        n = r.random(((y1 - y0) // 3, (x1 - x0) // 3)).astype(np.float32)
        n = cv2.resize(n, (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST)
        roll = int((t * 300) % (y1 - y0))
        n[roll:roll + 20] *= 0.4
        tv = np.dstack([n * 0.8, n * 0.8, n * 0.85, np.ones_like(n)]) * static
        tv[..., 3] = 1.0
        L = Layer(tv.astype(np.float32), 1.0, ox=x0, oy=y0, ref=(s["w"], S.LH))
        img = compose([L], cam, base=img)
        sx = W / 2 + ((x0 + x1) / 2 - s["w"] / 2 - cam.x) * cam.zoom
        sy = H / 2 + ((y0 + y1) / 2 - S.LH / 2 - cam.y) * cam.zoom
        img += sl_radial(sx, sy, 900, power=2, k=0.25 * static)[..., None] * rgb((170, 180, 210))
        img += sl_radial(W * 0.5, -100, 1100, power=2, k=0.4 * lamp)[..., None] * rgb((255, 190, 120)) * 0.6
        return img


# ================================================================ 4. corridor walk
class CorridorWalk(Shot):
    grade_kw = dict(warmth=0.4, desat=0.3, grain=0.07, red_shadow=1.0)

    def draw(self, t):
        s = S.corridor_apt_set()
        pr = self.p(t)
        walk0 = self.t0 + 1.0
        speed = 330.0
        dist = max(0.0, t - walk0) * speed
        wx = 400 + dist
        cam = Cam(1.0, wx - s["w"] / 2 + 160, 0)
        breathe(cam, t, 3)
        cam.y += math.sin(dist / 380 * 2 * math.pi * 2) * 3
        torch_on = smooth(c["flashlight"] + 0.6, c["flashlight"] + 0.7, t)
        ph = (dist / 380.0) % 1.0
        hgt = 660
        spr = timur_side_spr(hgt, int(ph * 100) % 100 // 4 * 4, 6, True)
        alb = compose([s["wall"]], cam)
        # Тимур в экранных координатах
        foot_x, foot_y = W / 2 - 160, H * 0.95
        img_spr = np.zeros((H, W, 4), np.float32)
        paste(img_spr, spr[0], foot_x - spr[1], foot_y - spr[2])
        tx = foot_x - spr[1] + spr[3][0]; ty = foot_y - spr[2] + spr[3][1]
        light = 0.42 + 0.08 * fbm(t * 0.5, 2)
        light = light + sl_radial(W * 1.2, H * 0.4, 1400, power=2, k=0.25)  # отсвет из комнаты
        light = light + sl_cone(tx, ty, -0.05, 0.42, 1900, k=2.2 * torch_on)
        img = lit(alb, light)
        img = img_spr[..., :3] * 0.9 + img * (1 - img_spr[..., 3:4])
        img = compose([(s["fg"], 1, 0.6)], Cam(1.0, cam.x * 1.0, cam.y), base=img)
        img += sl_cone(tx, ty, -0.05, 0.4, 1200, k=0.05 * torch_on)[..., None] * rgb(WARMW)  # дымка в луче
        return img


# ================================================================ stairs
class Stairs(Shot):
    grade_kw = dict(warmth=0.35, desat=0.3, grain=0.07, red_shadow=1.0)

    def draw(self, t):
        s = S.stairs_set()
        pr = self.p(t)
        cam = breathe(Cam(1.0 + 0.16 * ease_io(pr), 60 * pr, 40 * pr), t, 4)
        sway = math.sin(t * 2.2) * 6
        nb = sprite(s["neighbor"], s["neighbor"].shape[1] / 2, s["neighbor"].shape[0] * 0.98, 1500 + sway, 975, 1.0)
        nb = Layer(rim(nb.img, -4, -3, ORANGE, 0.9), 1.0, ox=nb.ox, oy=nb.oy, ref=nb.ref)
        alb = compose([s["sky"], s["wall"], nb], cam)
        spr = timur_back_spr(760, 5, 0, -5, 6)
        tl = sprite(spr[0], spr[1], spr[2], 760, 1380, 1.18)
        light = 0.38 + sl_radial(W * 0.82, H * 0.2, 800, power=2, k=0.8)
        aim = -0.25 + 0.06 * math.sin(t * 0.9)
        light = light + sl_cone(W * 0.36, H * 0.68, aim, 0.32, 1700, k=2.2)
        img = compose([(s["window_glow"], 1.0)], cam, base=lit(alb, light))
        img = compose([(tl, 1, 0.55)], cam, base=img)
        img = compose([(s["rail"], 1, 0.5)], cam, base=img)
        return img


# ================================================================ street
class Street(Shot):
    grade_kw = dict(warmth=0.55, desat=0.25, grain=0.07, red_shadow=1.2)

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.ash = Particles(110, seed=8, color=(255, 140, 70), size=(1, 2.4), speed=(5, 20), k=0.45)
        r = np.random.default_rng(14)
        self.runners = [(r.uniform(0, 1), r.uniform(0.6, 1.0), r.choice([-1, 1]), int(r.integers(0, 6)),
                         r.uniform(-60, 60)) for _ in range(7)]

    def draw(self, t):
        s = S.street_set()
        pr = self.p(t)
        cam = breathe(Cam(1.02 + 0.1 * ease_io(pr), -120 + 240 * ease_io(pr), 0), t, 4)
        blink = 1.0 if (t * 1.4) % 1 < 0.5 else 0.08
        layers = [s["sky"], s["smoke"], s["far"], s["street"], (s["win"], 0.9), s["cars"], (s["hazard"], blink)]
        # бегущие люди вдали (безликие силуэты)
        vx, vy = s["vx"], s["vy"]
        for (ph, sc, d, kind, yo) in self.runners:
            u = ((ph + t * 0.035 * d) % 1.0)
            x = vx - 700 + u * 1400
            hh = int(120 * sc)
            spr = person_spr(hh, kind, 0, False, 6)
            bob = abs(math.sin(t * 9 + ph * 10)) * 4
            layers.append(sprite(spr[0], spr[1], spr[2], x, vy + 150 * sc + yo * 0.3 - bob, 1.0))
        # Тимур и сосед уходят вглубь улицы
        k = ease_io(pr)
        for (bx, hh0, who) in ((1250, 640, "t"), (1520, 680, "n")):
            hh = int(lerp(hh0, hh0 * 0.62, k)) // 4 * 4
            y = lerp(S.LH + 30, S.LH - 150, k)
            x = lerp(bx, (bx + S.LW / 2) / 2, k) + math.sin(t * 4 + hh0) * 4
            if who == "t":
                spr = timur_back_spr(hh, 4, 0, -5, 8)
            else:
                spr = person_spr(hh, 3, 0, False, 5)
                spr = (rim(spr[0], 0, -5, ORANGE, 0.8), spr[1], spr[2])
            layers.append(sprite(spr[0], spr[1], spr[2], x, y, 1.15))
        img = compose(layers, cam)
        # сирены вдали
        sir = 0.5 + 0.5 * math.sin(t * 7)
        img += sl_radial(W * 0.62, H * 0.47, 300, power=2, k=0.35 * sir)[..., None] * rgb((255, 40, 30))
        img += sl_radial(W * 0.66, H * 0.47, 260, power=2, k=0.25 * (1 - sir))[..., None] * rgb((60, 80, 255))
        img = self.ash.draw(img, t)
        return img


# ================================================================ shelter door
class ShelterDoor(Shot):
    grade_kw = dict(warmth=0.35, desat=0.3, grain=0.07, red_shadow=1.0)

    def draw(self, t):
        s = S.shelter_door_set()
        pr = self.p(t)
        cam = breathe(Cam(1.0 + 0.2 * ease_io(pr), 0, -40 * pr), t, 4)
        dc = c["door_close"]
        close = ease_io(clamp01((t - (dc - 1.6)) / 1.5))
        leaf = Layer(S.door_leaf(S.LW, S.LH, s["door"], close), 1.0)
        walk = ease_io(clamp01((t - self.t0) / (dc - 1.8 - self.t0)))
        layers = [s["wall"]]
        fig = []
        for (bx, hh0, who) in ((1080, 820, "t"), (1260, 860, "n")):
            vis = 1 - smooth(0.82, 1.0, walk)
            if vis <= 0:
                continue
            hh = int(lerp(hh0, 560, walk)) // 4 * 4
            y = lerp(S.LH + 260, 1030, walk)
            x = lerp(bx, 1150 + (bx - 1170) * 0.4, walk) + math.sin(t * 5 + hh0) * 5
            spr = timur_back_spr(hh, 4, 0, -5, 0) if who == "t" else person_spr(hh, 3, 0, False, 4)
            fig.append((sprite(spr[0], spr[1], spr[2], x, y, 1.0 + 0.2 * (1 - walk)), vis))
        alb = compose(layers + [leaf], cam)
        sweep = -1.35 + 0.35 * math.sin(t * 0.8)
        light = 0.35 + sl_cone(W * 0.45, H * 1.05, sweep, 0.3, 1600, k=2.4)
        light = light + sl_radial(W * 0.5, H * 0.18, 500, power=2, k=0.4)
        img = lit(alb, light)
        for L, vis in fig:
            img = compose([(L, vis, 0.8)], cam, base=img)
        img = compose([(s["fg"], 1, 0.5)], cam, base=img)
        img += sl_cone(W * 0.45, H * 1.05, sweep, 0.28, 1500, k=0.05)[..., None] * rgb(WARMW)
        return img


# ================================================================ 5/7/8. SHELTER HALL
PEOPLE = [(0, 4, 400), (1, 1, 440), (2, 0, 420), (3, 5, 400), (4, 2, 430)]  # (bed index, kind, height)


class Hall(Shot):
    """mode: inside | turn | door_man | other_man."""

    def __init__(self, t0, t1, mode, tin="cut", din=0.0):
        super().__init__(t0, t1, tin, din)
        self.mode = mode
        self.dust = Particles(60, seed=21, color=(200, 190, 170), size=(1, 2), speed=(3, 9), k=0.25, upward=False)

    def gkw(self, t):
        return dict(warmth=0.3, desat=0.3, grain=0.075, red_shadow=1.4, exposure=1.25)

    def lighting(self, t):
        """(warm_list[3], red, emergency) интенсивности."""
        if self.mode == "inside":
            lo, el = c["lights_out"], c["emergency_light"]
            if t < lo:
                w = [0.85 * flicker(t, 31 + i, rate=7, depth=0.4, dropout=0.06) for i in range(3)]
                return w, 0.0, 0.0
            if t < el:
                return [0.0, 0.0, 0.0], 0.0, 0.0
            k = smooth(el, el + 0.05, t) * (0.4 + 0.6 * (1 if (t - el) > 0.6 or (t - el) % 0.2 < 0.1 else 0))
            return [0.0, 0.0, 0.0], 0.9 * k, 1.0 * k
        # после аварии: красный + одна мигающая лампа над пустой кроватью
        return [0.0, 0.0, 0.55 * flicker(t, 77, rate=9, depth=0.85, dropout=0.2)], 0.85, 1.0

    def cam(self, t):
        pr = self.p(t)
        if self.mode == "inside":
            return Cam(1.0 + 0.06 * pr, lerp(-720, -50, ease_io(pr)), 0)
        if self.mode == "turn":
            k = ease_io(clamp01((t - (c["silence"] + 2.0)) / (c["look_people"] + 1.0 - c["silence"] - 2.0)))
            return Cam(1.05 + 0.08 * k, lerp(-350, 1150, k), 20 * k)
        if self.mode == "door_man":
            return Cam(1.12 + 0.05 * pr, lerp(1150, 1250, pr), -20)
        return Cam(1.1 + 0.06 * pr, lerp(-500, -420, pr), -10)

    def draw(self, t):
        s = S.shelter_hall_set()
        warm_maps, red_map, lamps, bulbs, em = S.hall_lightmaps()
        wk, rk, ek = self.lighting(t)
        hw, hh = s["w"], s["h"]
        cam = breathe(self.cam(t), t, 3, seed=17)
        ref = (hw, hh)
        lm = np.full((hh, hw, 1), 0.16, np.float32)
        for i in range(3):
            if wk[i] > 0.01:
                lm = lm + warm_maps[i] * wk[i]
        lmc = np.repeat(lm, 3, axis=2) * rgb((255, 214, 170)) * 2.2
        if rk > 0:
            lmc = lmc + red_map * rk * rgb((255, 50, 34)) * 2.4
        wall = Layer(s["wall"].copy(), 1.0)
        wall.img[..., :3] *= lmc
        beds = Layer(s["beds"].copy(), 1.0)
        beds.img[..., :3] *= lmc
        avg = rgb((255, 214, 170)) * (0.1 + 0.6 * float(np.mean(wk))) + rgb((255, 60, 40)) * rk * 0.5
        layers = [wall, Layer(lamps, 1.0), beds]
        # люди
        turn = 0.0
        if self.mode == "turn":
            turn = -ease_io(clamp01((t - (c["silence"] + 0.5)) / 0.35))
        if self.mode in ("door_man", "other_man"):
            turn = -0.6
        for bi, kind, ph in PEOPLE:
            bx, by = S.BED_POS[bi]
            if self.mode == "other_man" and bi == 1:
                continue
            spr = person_spr(ph, kind, int(round(turn * 10)), True, 10)
            layers.append((sprite(spr[0], spr[1], spr[2], bx - 40 + (bi % 2) * 60, by + 4, 1.0, ref), 1, avg * 1.2))
        if self.mode == "door_man":
            spr = person_spr(560, 3, 3, False, 10)
            sway = math.sin(t * 1.5) * 8
            layers.append((sprite(spr[0], spr[1], spr[2], 3050 + sway, 1020, 1.0, ref), 1, avg * 1.3))
        if self.mode == "other_man":
            spr = person_spr(540, 1, 6, False, 10)
            layers.append((sprite(spr[0], spr[1], spr[2], 1000 + math.sin(t) * 6, 1010, 1.0, ref), 1, avg * 1.3))
        for i in range(3):
            if wk[i] > 0.01:
                layers.append((Layer(bulbs[i], 1.0, add=True), wk[i]))
        if ek > 0:
            layers.append((Layer(em, 1.0, add=True), ek))
        img = compose(layers, cam)
        # Тимур на переднем плане (спиной) — только в первой сцене
        if self.mode == "inside":
            pr = self.p(t)
            spr = timur_back_spr(820, 4, 0, -5, 0)
            tl = sprite(spr[0], spr[1], spr[2], lerp(500, 900, pr), hh + 250, 1.25, ref)
            img = compose([(tl, 1, avg * 1.0 + 0.05)], cam, base=img)
        img = self.dust.draw(img, t, 0.6)
        return img


# ================================================================ 6. clock & speaker
class Clock(Shot):
    grade_kw = dict(warmth=0.3, desat=0.2, grain=0.07, red_shadow=1.0)

    def draw(self, t):
        s = S.clock_set()
        pr = self.p(t)
        cam = breathe(Cam(1.0 + 0.25 * ease_io(pr), 0, 0), t, 2)
        blink = (t % 1.0) < 0.5
        cl = clock_cached("1457", blink)
        img = compose([(s["wall"], 1, 0.18), Layer(cl, 1.0)], cam)
        img += sl_radial(W / 2, H * 0.55, 1000, power=2, k=0.35)[..., None] * rgb((255, 40, 30))
        return img


@lru_cache(4)
def clock_cached(txt, blink):
    return S.clock_layer(txt[:2] + ":" + txt[2:], blink=blink)


class Speaker(Shot):
    grade_kw = dict(warmth=0.3, desat=0.25, grain=0.075, red_shadow=1.2)

    def draw(self, t):
        s = S.speaker_set()
        pr = self.p(t)
        b1 = c["broadcast1"]
        if t < b1:
            z = 1.0 + 0.18 * ease_io(clamp01((t - self.t0) / (b1 - self.t0)))
            cam = Cam(z, 0, -40)
        else:
            k = ease_io(clamp01((t - b1) / (self.t1 - b1)))
            cam = Cam(1.55 + 0.2 * k, s["gc"][0] - S.LW / 2, s["gc"][1] - S.LH / 2 + 20)
        breathe(cam, t, 2)
        on = smooth(c["radio"] + 0.3, c["radio"] + 0.35, t)
        e = env_at(t) * on
        g = s["grill"]
        gz = 1 + 0.012 * e
        gl = Layer(g.img, 1.0, ox=(1 - gz) * s["gc"][0], oy=(1 - gz) * s["gc"][1])
        img = compose([(s["wall"], 1, 0.22), gl], cam)
        img = compose([(s["led"], on * (0.8 + 0.2 * e))], cam, base=img)
        img += sl_radial(W * 0.5, H * 0.1, 1200, power=2, k=0.25)[..., None] * rgb((255, 60, 40))
        img += sl_radial(W * 0.4, H * 0.9, 900, power=2, k=0.15 + 0.1 * flicker(t, 5))[..., None] * rgb((255, 200, 150))
        return img


# ================================================================ visions: mall / metro
class Vision(Shot):
    def __init__(self, t0, t1, kind, tin="fade", din=1.2):
        super().__init__(t0, t1, tin, din)
        self.kind = kind
        self.ash = Particles(80, seed=31, color=(255, 140, 70), size=(1, 2.2), speed=(4, 14), k=0.4)

    def gkw(self, t):
        return dict(warmth=0.5, desat=0.45, grain=0.08, red_shadow=1.2, vignette=1.6)

    def draw(self, t):
        pr = self.p(t)
        cam = breathe(Cam(1.0 + 0.14 * ease_io(pr), 0, -20 * pr), t, 3)
        if self.kind == "mall":
            s = S.mall_set()
            fl = 0.7 + 0.3 * flicker(t, 12, rate=4, depth=0.6)
            img = compose([s["sky"], s["smoke"], s["mall"], (s["wins"], fl), s["sign"], s["cars"]], cam)
        else:
            s = S.metro_set()
            pulse = 0.75 + 0.25 * flicker(t, 13, rate=3, depth=0.5, dropout=0.03)
            img = compose([s["sky"], s["smoke"], s["metro"], (s["sign"], 1, pulse), (s["glow"], pulse)], cam)
        img = self.ash.draw(img, t)
        # мягкое «воспоминание»: размытые края
        bl = cv2.GaussianBlur(img, (0, 0), 6)
        m = S._vision_mask()
        return img * (1 - m) + bl * m


@lru_cache(None)
def _vmask():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip((d - 0.55) / 0.6, 0, 1)[..., None]


S._vision_mask = _vmask


# ================================================================ long corridor & knocks
def knock_times():
    k0 = c["corridor_look"] + 0.4
    return [k0, k0 + 0.8, k0 + 1.6]


class LongCorridor(Shot):
    grade_kw = dict(warmth=0.3, desat=0.35, grain=0.08, red_shadow=1.3)

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.dust = Particles(90, seed=41, color=(210, 200, 180), size=(1, 2.2), speed=(20, 60), k=0.35,
                              upward=False)

    def draw(self, t):
        s = S.long_corridor_set()
        pr = self.p(t)
        cam = Cam(1.0 + 0.6 * ease_io(pr) ** 1.2, 0, (s["vp"][1] - S.LH / 2) * pr)
        breathe(cam, t, 2)
        kn = 0.0
        for kt in knock_times():
            if kt <= t < kt + 0.35:
                kn = max(kn, 1 - (t - kt) / 0.35)
        cam.shake(t, 12 * kn, seed=13, rate=30)
        lamp = 0.8 * flicker(t, 55, rate=8, depth=0.9, dropout=0.18)
        img = compose([(s["corr"], 1, 0.6 + 0.7 * lamp), (s["lamp"], lamp), (s["door_light"], 0.8 + 1.5 * kn)], cam)
        # Тимур слева на переднем плане
        k = smooth(self.t0, self.t0 + 1.5, t)
        spr = timur_back_spr(1000, 3, 0, -5, 0)
        tl = sprite(spr[0], spr[1], spr[2], 420, S.LH + 520, 1.6)
        img = compose([(tl, k, 0.3)], Cam(cam.zoom ** 0.3, cam.x * 0.2, cam.y * 0.2, cam.rot), base=img)
        dg = sum(smooth(kt, kt + 0.05, t) * (1 - smooth(kt + 0.6, kt + 2.5, t)) for kt in knock_times())
        img = self.dust.draw(img, t, min(1.0, dg))
        return img


# ================================================================ handle
class Handle(Shot):
    grade_kw = dict(warmth=0.3, desat=0.3, grain=0.08, red_shadow=1.3)

    def draw(self, t):
        s = S.handle_set()
        pr = self.p(t)
        cam = breathe(Cam(1.02 + 0.14 * ease_io(pr), 40 * pr, 30 * pr), t, 2)
        hm, he = c["handle_move"], c["handle_end"]
        a = 0.62 * ease_io(clamp01((t - (hm - 0.5)) / (he - 0.15 - (hm - 0.5))))
        a += 0.015 * math.sin(t * 40) * smooth(hm - 0.5, hm, t) * (1 - smooth(he - 0.3, he, t))
        lev = Layer(lever_cached(int(a * 200)), 1.0)
        alb = compose([s["door"], s["plate"], lev], cam)
        light = 0.08 + sl_cone(-W * 0.1, H * 0.35, 0.18 + 0.03 * math.sin(t * 0.7), 0.45, 2600, k=1.2)
        light = light + sl_radial(W * 0.55, H * 0.55, 700, power=2, k=0.3)
        img = lit(alb, light) * rgb((255, 225, 200))
        return img


@lru_cache(256)
def lever_cached(a200):
    return S.handle_lever(a200 / 200)


# ================================================================ FINAL CHOICE
class Final(Shot):
    grade_kw = dict(warmth=0.2, desat=0.1, grain=0.05, red_shadow=0.6, vignette=1.2)

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.ash = Particles(90, seed=51, color=(255, 120, 60), size=(1, 2.2), speed=(6, 18), k=0.35)

    @staticmethod
    @lru_cache(None)
    def parts():
        title = text_layer([("А ТЫ ЧТО БЫ ВЫБРАЛ?", W / 2, 150)], FONT_TITLE, 96, color=(240, 232, 220), glow=16,
                           glow_color=(190, 30, 20))
        def card(cx, letter, lines, icon):
            from .gfx import Pen
            p = Pen(W, H, ss=2)
            x0, x1 = cx - 400, cx + 400
            p.rrect(x0, 290, x1, 840, 18, (16, 12, 12, 220))
            p.rrect(x0, 290, x1, 296, 2, (170, 30, 24))
            p.text(cx, 370, "ВАРИАНТ " + letter, FONT_TITLE, 64, (232, 70, 50), anchor="mm")
            if icon == "mall":
                p.rect(cx - 140, 470, cx + 140, 580, (60, 54, 50))
                for i in range(6):
                    p.rect(cx - 125 + i * 44, 495, cx - 95 + i * 44, 525, (190, 130, 70) if i in (1, 4) else (24, 22, 22))
                p.rect(cx - 160, 455, cx + 160, 470, (80, 72, 66))
                p.rect(cx - 25, 540, cx + 25, 580, (14, 12, 12))
            else:
                p.text(cx, 520, "М", FONT_TITLE, 120, (220, 36, 30), anchor="mm")
            for i, s in enumerate(lines):
                p.text(cx, 650 + i * 50, s, FONT_SEMI, 38, (230, 224, 214), anchor="mm")
            return p.arr()
        a = card(W / 2 - 440, "А", ["Пойти в торговый центр", "и попытаться найти", "других выживших."], "mall")
        b = card(W / 2 + 440, "Б", ["Направиться к подземной", "станции метро", "и укрыться там."], "metro")
        cm = text_layer([("Напиши  А  или  Б  в комментариях", W / 2, 920)], FONT_BOLD, 44, color=(225, 215, 200))
        ct = text_layer([("Продолжение следует…", W / 2, 990)], FONT_SEMI, 32, color=(170, 70, 50))
        return title, a, b, cm, ct

    def draw(self, t):
        img = np.zeros((H, W, 3), np.float32)
        img += sl_radial(W / 2, H * 1.1, 1300, power=2, k=0.18)[..., None] * rgb((170, 40, 20))
        img = self.ash.draw(img, t, smooth(self.t0, self.t0 + 3, t))
        title, a, b, cm, ct = self.parts()
        f = c["final"]
        items = [(title, smooth(f + 0.3, f + 1.5, t), 0), (a, smooth(c["optA"] - 0.2, c["optA"] + 0.8, t), 1),
                 (b, smooth(c["optB"] - 0.2, c["optB"] + 0.8, t), 1), (cm, smooth(c["comment"], c["comment"] + 1, t), 0),
                 (ct, smooth(c["cont"] + 0.5, c["cont"] + 2, t), 0)]
        for L, al, mv in items:
            if al <= 0:
                continue
            if mv:
                M = np.float32([[1, 0, 0], [0, 1, 30 * (1 - al)]])
                L = cv2.warpAffine(L, M, (W, H))
            img = L[..., :3] * al + img * (1 - L[..., 3:4] * al)
        # медленное «дыхание» света
        img *= 0.94 + 0.06 * math.sin(t * 0.8)
        return img


# ================================================================ TIMELINE
def build_timeline():
    T = []
    T.append(Hook(0.0, c["day"]))
    T.append(WindowShot(c["day"], c["phone_vibrate"], "day", 1.0, 1.10, tin="black", din=1.4))
    T.append(PhoneTable(c["phone_vibrate"], c["window2"]))
    T.append(WindowShot(c["window2"], c["rumble"], "day2", 1.12, 1.2, tin="fade", din=0.6))
    T.append(WindowShot(c["rumble"], c["signal_lost"], "after", 1.18, 1.26, tin="fade", din=1.2))
    T.append(PhoneHand(c["signal_lost"], c["tv"], "dark", script_nosignal))
    T.append(TVRoom(c["tv"], c["leave"]))
    T.append(CorridorWalk(c["leave"], c["stairs"], tin="black", din=0.8))
    T.append(Stairs(c["stairs"], c["street"], tin="fade", din=0.6))
    T.append(Street(c["street"], c["phone2"], tin="black", din=0.8))
    T.append(PhoneHand(c["phone2"], c["building"], "street", script_msg, vib_at=(c["phone2"] + 0.2,)))
    T.append(ShelterDoor(c["building"], c["door_close"], tin="fade", din=0.6))
    T.append(Black(c["door_close"], c["inside"]))
    T.append(Hall(c["inside"], c["clock"], "inside", tin="fadein", din=1.2))
    T.append(Clock(c["clock"], c["radio"] - 1.0, tin="fade", din=0.8))
    T.append(Speaker(c["radio"] - 1.0, c["silence"], tin="fade", din=0.6))
    T.append(Hall(c["silence"], c["man_door"], "turn"))
    T.append(Hall(c["man_door"], c["mall"], "door_man", tin="fade", din=0.8))
    T.append(Vision(c["mall"], c["other_man"], "mall", tin="fade", din=1.2))
    T.append(Hall(c["other_man"], c["metro"], "other_man", tin="fade", din=1.0))
    T.append(Vision(c["metro"], c["choice_now"], "metro", tin="fade", din=1.2))
    T.append(LongCorridor(c["choice_now"], c["phone3"], tin="black", din=1.0))
    T.append(PhoneHand(c["phone3"], c["handle"], "dark", script_final, vib_at=(c["phone3"] + 0.1,)))
    T.append(Handle(c["handle"], c["handle_end"], tin="fade", din=0.6))
    T.append(Black(c["handle_end"], c["final"]))
    T.append(Final(c["final"], c["END"], tin="fadein", din=1.5))
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
    # затемнение перед «black»-переходом следующего шота
    if nxt is not None and nxt.tin == "black" and t >= nxt.t0 - nxt.din / 2:
        k = (nxt.t0 - t) / (nxt.din / 2)
        return cur.frame(t) * clamp01(k)
    img = cur.frame(t)
    if cur.tin == "black" and t < cur.t0 + cur.din / 2:
        img = img * ease_io((t - cur.t0) / (cur.din / 2))
    elif cur.tin == "fadein" and t < cur.t0 + cur.din:
        img = img * ease_io((t - cur.t0) / cur.din)
    elif cur.tin == "fade" and t < cur.t0 + cur.din and i > 0:
        k = ease_io((t - cur.t0) / cur.din)
        prev = TIMELINE[i - 1]
        img = img * k + prev.frame(t) * (1 - k)
    return img
