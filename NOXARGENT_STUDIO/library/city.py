"""Город за окном Армана и дом напротив.

CityView — панорама из окна гостиной: три слоя домов (параллакс), окна гаснут
по заданному времени, фонари, светофоры, далёкий красный аварийный огонь.
Opposite — дом напротив: всё тёмное, кроме одного окна на верхнем этаже.
"""
import math

import cv2
import numpy as np

from core import AA, H, W, blob, gradient, to_lmap, u8
from characters import arman_front_silhouette

SKY = ((30, 16, 10), (46, 28, 18))
WARM = [(70, 150, 210), (90, 165, 220), (60, 125, 195), (150, 170, 180)]


class Layer:
    def __init__(self, rng, width, base_y, hmin, hmax, wmin, wmax, col, win, lit_p, t_off):
        self.w = width
        self.img = np.zeros((H, width, 3), np.uint8)
        self.alpha = np.zeros((H, width), np.uint8)
        lit = np.zeros((H, width, 3), np.uint8)
        self.off = np.full((H, width), np.inf, np.float32)
        x = -40
        t0, t1 = t_off
        while x < width:
            bw = int(rng.integers(wmin, wmax))
            top = base_y - int(rng.integers(hmin, hmax))
            cv2.rectangle(self.img, (x, top), (x + bw, H), col, -1)
            cv2.rectangle(self.alpha, (x, top), (x + bw, H), 255, -1)
            ww, wh, gx, gy = win
            for wy in range(top + gy, H - gy, wh + gy):
                for wx in range(x + gx, x + bw - ww - 4, ww + gx):
                    c = tuple(int(v * 0.55) for v in col)
                    cv2.rectangle(self.img, (wx, wy), (wx + ww, wy + wh), tuple(max(0, v - 8) for v in col), -1)
                    if rng.random() < lit_p:
                        cv2.rectangle(lit, (wx, wy), (wx + ww, wy + wh), WARM[rng.integers(len(WARM))], -1)
                        # гаснут волной слева направо с разбросом
                        self.off[wy:wy + wh + 1, wx:wx + ww + 1] = t0 + (t1 - t0) * (wx / width) * 0.8 + rng.random() * (t1 - t0) * 0.2
            x += bw + int(rng.integers(6, 40))
        self.lit = cv2.add(lit, cv2.convertScaleAbs(cv2.GaussianBlur(lit, (0, 0), 4), alpha=0.6))
        self.amask = self.alpha > 127

    def render(self, t, x0=0, w=None):
        w = w or self.w
        sl = slice(x0, x0 + w)
        on = (self.off[:, sl] > t).astype(np.uint8) * 255
        lit = cv2.bitwise_and(self.lit[:, sl], self.lit[:, sl], mask=on)
        return cv2.add(self.img[:, sl], lit)


class CityView:
    WIDTH = 2700

    def __init__(self, t_dark0, t_dark1, t_street, seed=31):
        rng = np.random.default_rng(seed)
        self.sky = gradient(H, self.WIDTH, *SKY)
        self.sky = cv2.add(self.sky, u8(blob(H, self.WIDTH, self.WIDTH / 2, H * 0.8, 1600, 300, (30, 40, 50))))
        self.layers = [
            (Layer(rng, self.WIDTH, 700, 120, 330, 80, 180, (36, 26, 22), (6, 8, 6, 9), 0.35, (t_dark0, t_dark1)), 0.25),
            (Layer(rng, self.WIDTH, 820, 200, 480, 140, 280, (28, 22, 20), (10, 12, 9, 12), 0.4, (t_dark0 + 0.3, t_dark1 + 0.3)), 0.55),
            (Layer(rng, self.WIDTH, 980, 260, 560, 220, 420, (20, 17, 16), (16, 18, 14, 16), 0.38, (t_dark0 + 0.6, t_dark1 + 0.6)), 1.0),
        ]
        self.t_street = t_street
        self.beacon = (int(self.WIDTH * 0.62), 330)
        st = np.zeros((H, self.WIDTH, 3), np.uint8)
        for x in range(80, self.WIDTH, 260):
            cv2.circle(st, (x, 900), 7, (140, 200, 240), -1, AA)
        self.street = cv2.add(st, cv2.GaussianBlur(st, (0, 0), 18) * 3)
        tl = np.zeros_like(st)
        for x in (700, 1500, 2300):
            cv2.circle(tl, (x, 930), 6, (60, 210, 90), -1, AA)
        self.traffic = cv2.add(tl, cv2.GaussianBlur(tl, (0, 0), 10) * 3)
        # мачта с аварийным огнём
        bx, by = self.beacon
        cv2.line(self.layers[0][0].img, (bx, by), (bx, 760), (34, 26, 22), 6)
        self.frame_fg = self._window_frame()
        self.beacon_spr = u8(blob(80, 80, 40, 40, 18, 18, (40, 40, 255)))

    def _window_frame(self):
        fg = np.zeros((H, W, 4), np.uint8)
        col = (12, 12, 14, 255)
        cv2.rectangle(fg, (0, 0), (W, 70), col, -1)
        cv2.rectangle(fg, (0, H - 110), (W, H), col, -1)
        cv2.rectangle(fg, (0, 0), (70, H), col, -1)
        cv2.rectangle(fg, (W - 70, 0), (W, H), col, -1)
        cv2.rectangle(fg, (W // 2 - 14, 0), (W // 2 + 14, H), col, -1)
        cv2.rectangle(fg, (0, H - 140), (W, H - 110), (24, 22, 22, 255), -1)  # подоконник
        return fg

    def frame(self, t, pan):
        """pan: 0..1 — панорама слева направо."""
        out = None
        for i, (layer, depth) in enumerate([(None, 0.08)] + self.layers):
            x = int(pan * (self.WIDTH - W) * depth)
            if layer is None:
                out = self.sky[:, x:x + W].copy()
                continue
            img = layer.render(t, x, W)
            np.copyto(out, img, where=layer.amask[:, x:x + W, None])
            if i == 1:
                bx, by = self.beacon
                px = bx - x
                if 40 <= px < W - 40 and int(t * 1.2) % 2 == 0:
                    roi = out[by - 40:by + 40, px - 40:px + 40]
                    cv2.add(roi, self.beacon_spr, dst=roi)
                    cv2.circle(out, (px, by), 5, (60, 60, 255), -1, AA)
        x = int(pan * (self.WIDTH - W))
        k = max(0.0, min(1.0, 1 - (t - self.t_street) / 0.6))
        if k > 0:
            out = cv2.add(out, cv2.convertScaleAbs(self.street[:, x:x + W], alpha=k))
            out = cv2.add(out, cv2.convertScaleAbs(self.traffic[:, x:x + W], alpha=k))
        from core import paste_rgba
        return paste_rgba(out, self.frame_fg, 0, 0)


class Opposite:
    """Дом напротив. Одно освещённое окно на верхнем этаже: (WX0, WY0)-(WX1, WY1)."""
    WIN = (900, 210, 1020, 330)

    def __init__(self, seed=41):
        rng = np.random.default_rng(seed)
        img = gradient(H, W, *SKY)
        far = Layer(rng, W, 860, 80, 260, 90, 200, (32, 24, 20), (6, 8, 6, 9), 0.0, (0, 0))
        a = far.alpha[..., None].astype(np.float32) / 255
        img = (img * (1 - a) + far.img * a).astype(np.uint8)
        # сам дом напротив
        cv2.rectangle(img, (520, 120), (1400, H), (26, 22, 21), -1)
        for fy in range(150, H, 120):
            for fx in range(560, 1380, 120):
                cv2.rectangle(img, (fx, fy + 60), (fx + 120, fy + 60), (20, 18, 18), 1)
                cv2.rectangle(img, (fx + 20, fy), (fx + 100, fy + 100), (16, 14, 14), -1)
        cv2.rectangle(img, (520, 120), (1400, 130), (18, 16, 16), -1)
        x0, y0, x1, y1 = self.WIN
        self.base = img
        room = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
        room[:] = (48, 92, 132)
        room = cv2.add(room, u8(blob(y1 - y0, x1 - x0, (x1 - x0) / 2, 10, 60, 50, (60, 80, 90))))
        self.room = room
        self.glow = u8(blob(H, W, (x0 + x1) / 2, (y0 + y1) / 2, 150, 120, (40, 70, 100)))
        self.beacon = (1700, 520)

    def frame(self, t, figure=True, highlight=0.0):
        img = self.base.copy()
        x0, y0, x1, y1 = self.WIN
        win = self.room.copy()
        if figure:
            arman_front_silhouette(win, (x1 - x0) / 2, (y1 - y0) + 22, 112, col=(10, 10, 12))
            if highlight > 0:  # контур толстовки подсвечивается
                m = cv2.inRange(win, (0, 0, 0), (14, 14, 16))
                edge = cv2.dilate(m, np.ones((3, 3), np.uint8)) - m
                win[edge > 0] = (np.array(win[edge > 0], np.float32) * (1 - highlight) + np.array((200, 220, 235)) * highlight).astype(np.uint8)
        img[y0:y1, x0:x1] = win
        cv2.rectangle(img, (x0, y0), (x1, y1), (12, 12, 12), 6)
        cv2.line(img, ((x0 + x1) // 2, y0), ((x0 + x1) // 2, y0 + 40), (12, 12, 12), 5)
        img = cv2.add(img, self.glow)
        if int(t * 1.2) % 2 == 0:
            bx, by = self.beacon
            img = cv2.add(img, u8(blob(H, W, bx, by, 16, 16, (40, 40, 255))))
            cv2.circle(img, (bx, by), 4, (60, 60, 255), -1, AA)
        return img
