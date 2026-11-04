"""Общие заготовки планов: базовый класс, телефон в руках, экран-фото."""
import math

import cv2
import numpy as np

import phone as PH
from characters import hands_holding
from core import H, W, blob, camera, ease, paste_rgba, shake, u8, warp_rgba


class Shot:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def k(self, t):
        return (t - self.t0) / max(1e-6, self.t1 - self.t0)


_CACHE = {}


def sprite(key, maker, cracked=False):
    """Кэш спрайтов телефона: maker() → PIL-экран или BGR-массив."""
    k = (key, cracked)
    if k not in _CACHE:
        scr = maker()
        scr = scr if isinstance(scr, np.ndarray) else PH.to_bgr(scr)
        spr = PH.phone_sprite(scr)
        _CACHE[k] = PH.add_cracks(spr) if cracked else spr
    return _CACHE[k]


def live_sprite(scr, cracked=False):
    scr = scr if isinstance(scr, np.ndarray) else PH.to_bgr(scr)
    spr = PH.phone_sprite(scr)
    return PH.add_cracks(spr) if cracked else spr


def place_phone(img, spr, cx, cy, scale, angle=0.0, alpha=1.0):
    s = warp_rgba(spr, scale, angle)
    paste_rgba(img, s, cx - s.shape[1] / 2, cy - s.shape[0] / 2, alpha)


class PhoneHands(Shot):
    """Телефон в руках Армана. screen(t) → спрайт. shakes — моменты вибрации.
    zoom(t) → (z, dy) — наезд на экран."""

    def __init__(self, t0, t1, bg, screen, shakes=(), zoom=None, scale=0.7):
        super().__init__(t0, t1)
        self.bg = cv2.convertScaleAbs(cv2.GaussianBlur(bg, (0, 0), 9), alpha=0.55)
        self.screen, self.shakes, self.zoom, self.scale = screen, shakes, zoom, scale
        self.pw, self.ph = PH.PW * scale, PH.PH * scale

    def frame(self, t):
        img = self.bg.copy()
        dx = dy = 0.0
        for tv in self.shakes:
            a, b = shake(t, tv, amp=10, dur=0.3, freq=40)
            dx, dy = dx + a, dy + b
        cx = 960 + math.sin(t * 0.9) * 10 + math.sin(t * 2.3) * 4 + dx
        cy = 540 + math.sin(t * 0.7 + 1) * 8 + dy
        img = cv2.add(img, u8(blob(H, W, cx, cy, 500, 520, (30, 30, 34))))
        place_phone(img, self.screen(t), cx, cy, self.scale)
        hands_holding(img, cx, cy, self.pw, self.ph)
        if self.zoom:
            z, oy = self.zoom(t)
            return camera(img, z, cx, cy + oy)
        return img
