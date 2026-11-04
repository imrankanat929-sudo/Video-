"""Телевизор и экстренный выпуск новостей (силуэт ведущего, бегущая строка, помехи)."""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

from core import AA, blob, draw_text, font, gradient, paste_rgba, pil_to_bgra, u8

TW, TH = 1280, 720
CRAWL = "ЧРЕЗВЫЧАЙНОЕ ПОЛОЖЕНИЕ  •  НЕ ВЫХОДИТЕ НА УЛИЦЫ  •  ЖДИТЕ ДАЛЬНЕЙШИХ УКАЗАНИЙ  •  "
WARNING = "НЕМЕДЛЕННО ЗАКРОЙТЕ ОКНА"


class News:
    def __init__(self, seed=5):
        rng = np.random.default_rng(seed)
        bg = gradient(TH, TW, (70, 40, 18), (30, 16, 8))
        bg = cv2.add(bg, u8(blob(TH, TW, TW * 0.62, TH * 0.35, 380, 260, (60, 38, 20))))
        for x in range(0, TW, 80):  # условная студия: светлые вертикальные панели
            cv2.rectangle(bg, (x, 0), (x + 3, TH), (80, 52, 30), -1)
        self.bg = bg
        # плашки
        top = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
        d = ImageDraw.Draw(top)
        d.rectangle((40, 36, 430, 92), fill=(200, 40, 36, 255))
        draw_text(top, (58, 46), "ЭКСТРЕННЫЙ ВЫПУСК", 30, (255, 255, 255, 255), "bold")
        d.rectangle((40, 520, 900, 590), fill=(240, 240, 240, 235))
        draw_text(top, (60, 534), "ВОЕННЫЙ КОНФЛИКТ", 36, (20, 20, 24, 255), "bold")
        self.plates = pil_to_bgra(top)
        # бегущая строка: лента из повторов текста
        f = font(38, "bold")
        self.strip_w = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(CRAWL, font=f))
        strip = Image.new("RGB", (self.strip_w * 2 + TW, 64), (170, 28, 26))
        for i in range(3):
            draw_text(strip, (i * self.strip_w, 10), CRAWL, 38, (255, 255, 255), "bold")
        self.strip = cv2.cvtColor(np.array(strip), cv2.COLOR_RGB2BGR)
        warn = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
        d = ImageDraw.Draw(warn)
        d.rectangle((0, 290, TW, 430), fill=(0, 0, 0, 230))
        draw_text(warn, (0, 322), WARNING, 64, (255, 255, 255, 255), "bold", max_w=TW, align="center")
        self.warn = pil_to_bgra(warn)
        self.noise = [u8(rng.normal(90, 55, (TH // 2, TW // 2))) for _ in range(8)]

    def anchor(self, img, cx, look=0.0):
        """Силуэт ведущего: плечи и голова, лицо в тени (без черт)."""
        col = (14, 12, 12)
        cv2.ellipse(img, (int(cx), 760), (300, 260), 0, 180, 360, col, -1, AA)
        cv2.rectangle(img, (int(cx - 48), 330), (int(cx + 48), 520), col, -1)
        cv2.ellipse(img, (int(cx + 20 * (1 - look)), 300), (88, 112), 0, 0, 360, col, -1, AA)
        cv2.ellipse(img, (int(cx + 20 * (1 - look)), 300), (90, 114), 0, 200, 340, (70, 60, 52), 3, AA)  # контровой свет

    def frame(self, t, crawl_t0=None, look=0.0, glitch=0.0, warning=False, freeze_t=None):
        tt = t if freeze_t is None else min(t, freeze_t)
        img = self.bg.copy()
        cx = 760 + 20 * math.sin(tt * 0.7) * (1 - look) + 100 * (1 - look)
        cx = 640 * look + cx * (1 - look) if look > 0 else cx
        self.anchor(img, cx, look)
        paste_rgba(img, self.plates, 0, 0)
        if crawl_t0 is not None and t >= crawl_t0:
            off = int((tt - crawl_t0) * 170) % self.strip_w
            reveal = min(1.0, (t - crawl_t0) / 0.4)
            band = self.strip[:, off:off + TW]
            yb = 640
            img[yb:yb + 64] = (img[yb:yb + 64] * (1 - reveal) + band * reveal).astype(np.uint8)
        if warning:
            n = cv2.resize(self.noise[int(t * 24) % len(self.noise)], (TW, TH))
            img = cv2.addWeighted(cv2.cvtColor(n, cv2.COLOR_GRAY2BGR), 0.85, img, 0.15, 0)
            paste_rgba(img, self.warn, 0, 0)
        elif glitch > 0:
            n = cv2.resize(self.noise[int(t * 24) % len(self.noise)], (TW, TH))
            img = cv2.addWeighted(cv2.cvtColor(n, cv2.COLOR_GRAY2BGR), glitch * 0.6, img, 1 - glitch * 0.45, 0)
            rng = np.random.default_rng(int(t * 30))
            for _ in range(int(3 + glitch * 10)):
                y = int(rng.integers(0, TH - 20))
                hh = int(rng.integers(6, 40))
                img[y:y + hh] = np.roll(img[y:y + hh], int(rng.normal(0, 60 * glitch)), axis=1)
        img[::3] = (img[::3] * 0.82).astype(np.uint8)  # строчная развёртка
        return img


def collapse(screen, k):
    """Выключение старого ТВ: картинка сжимается в линию, затем в точку. k: 0..1."""
    out = np.zeros_like(screen)
    h, w = screen.shape[:2]
    if k < 0.6:
        sh = max(2, int(h * (1 - k / 0.6) ** 2))
        small = cv2.resize(screen, (w, sh))
        small = cv2.convertScaleAbs(small, alpha=1 + k * 2)
        out[h // 2 - sh // 2:h // 2 - sh // 2 + sh] = small
    elif k < 1.0:
        kk = (k - 0.6) / 0.4
        lw = max(2, int(w * (1 - kk)))
        cv2.line(out, (w // 2 - lw // 2, h // 2), (w // 2 + lw // 2, h // 2), (230, 230, 235), 3)
        cv2.circle(out, (w // 2, h // 2), max(1, int(6 * (1 - kk))), (255, 255, 255), -1)
    return out
