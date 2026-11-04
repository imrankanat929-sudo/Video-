"""Цифровые часы на тумбочке Армана (семисегментный дисплей)."""
import cv2
import numpy as np

from core import AA, H, W, blob, gradient, poly, u8

SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
       "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}
DIGIT_COL = (225, 215, 170)  # холодный бело-голубой (BGR); красный оставлен для тревоги


def seven_seg(img, text, x, y, h, col=DIGIT_COL, colon_on=True, off_col=(7, 7, 8)):
    w = h * 0.55
    t = h * 0.12
    for ch in text:
        if ch == ":":
            if colon_on:
                for yy in (y + h * 0.3, y + h * 0.7):
                    cv2.circle(img, (int(x + w * 0.2), int(yy)), int(t * 0.55), col, -1, AA)
            x += w * 0.45
            continue
        on = SEG.get(ch, "")
        segs = {
            "a": [(x + t, y), (x + w - t, y), (x + w - t * 1.6, y + t), (x + t * 1.6, y + t)],
            "d": [(x + t * 1.6, y + h - t), (x + w - t * 1.6, y + h - t), (x + w - t, y + h), (x + t, y + h)],
            "g": [(x + t, y + h / 2), (x + t * 1.6, y + h / 2 - t / 2), (x + w - t * 1.6, y + h / 2 - t / 2), (x + w - t, y + h / 2), (x + w - t * 1.6, y + h / 2 + t / 2), (x + t * 1.6, y + h / 2 + t / 2)],
            "f": [(x, y + t), (x + t, y + t * 1.6), (x + t, y + h / 2 - t * 0.6), (x, y + h / 2 - t * 0.1)],
            "e": [(x, y + h / 2 + t * 0.1), (x + t, y + h / 2 + t * 0.6), (x + t, y + h - t * 1.6), (x, y + h - t)],
            "b": [(x + w, y + t), (x + w - t, y + t * 1.6), (x + w - t, y + h / 2 - t * 0.6), (x + w, y + h / 2 - t * 0.1)],
            "c": [(x + w, y + h / 2 + t * 0.1), (x + w - t, y + h / 2 + t * 0.6), (x + w - t, y + h - t * 1.6), (x + w, y + h - t)],
        }
        for k, pts in segs.items():
            poly(img, pts, col if k in on else off_col)
        x += w * 1.25


class ClockClose:
    """Крупный план часов на тумбочке."""

    def __init__(self):
        img = gradient(H, W, (10, 10, 12), (4, 4, 5))
        img[760:] = gradient(H - 760, W, (22, 26, 34), (12, 14, 18))  # столешница тумбочки
        cv2.rectangle(img, (420, 330), (1500, 780), (16, 16, 18), -1)    # корпус часов
        cv2.rectangle(img, (470, 380), (1450, 730), (5, 5, 6), -1)       # стекло
        cv2.line(img, (420, 780), (1500, 780), (30, 30, 34), 3)
        self.base = img
        self.glow = u8(blob(H, W, 960, 555, 520, 220, DIGIT_COL, 0.14))
        refl = u8(blob(H, W, 960, 830, 520, 50, DIGIT_COL, 0.10))       # отражение на столешнице
        self.refl = refl

    def frame(self, t, text="03:17"):
        img = self.base.copy()
        seven_seg(img, text, 560, 430, 250, colon_on=(int(t * 2) % 2 == 0))
        img = cv2.add(img, self.glow)
        return cv2.add(img, self.refl)
