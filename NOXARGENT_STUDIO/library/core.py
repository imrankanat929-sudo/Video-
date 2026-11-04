"""Общие инструменты студии: кадр, камера, свет, текст, пост-обработка."""
import math
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
AA = cv2.LINE_AA
LIB = Path(__file__).resolve().parent
FONTS = LIB / "fonts"


def desktop() -> Path:
    if os.environ.get("NOX_DESKTOP"):
        return Path(os.environ["NOX_DESKTOP"])
    home = Path.home()
    for p in (home / "OneDrive" / "Desktop", home / "OneDrive" / "Рабочий стол", home / "Desktop", home / "Рабочий стол"):
        if p.is_dir():
            return p
    (home / "Desktop").mkdir(parents=True, exist_ok=True)
    return home / "Desktop"


STUDIO = desktop() / "NOXARGENT_STUDIO"


# ---------- математика ----------
def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def lerp(a, b, x):
    return a + (b - a) * x


def clamp01(x):
    return min(max(x, 0.0), 1.0)


def ramp(t, t0, t1):
    """0 до t0, 1 после t1, плавно между."""
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return ease((t - t0) / (t1 - t0))


# ---------- рисование ----------
def gradient(h, w, top, bot, horizontal=False):
    n = w if horizontal else h
    t = np.linspace(0, 1, n, dtype=np.float32)
    g = np.array(top, np.float32)[None] * (1 - t[:, None]) + np.array(bot, np.float32)[None] * t[:, None]
    if horizontal:
        return np.repeat(g[None], h, axis=0).astype(np.uint8)
    return np.repeat(g[:, None], w, axis=1).astype(np.uint8)


def blob(h, w, cx, cy, rx, ry, color, power=1.0):
    """Мягкое световое пятно (float32 HxWx3). Для больших пятен считается на сетке 1/4."""
    s = 4 if min(rx, ry) >= 40 else 1
    hs, ws = (h + s - 1) // s, (w + s - 1) // s
    yy, xx = np.mgrid[0:hs, 0:ws].astype(np.float32)
    d = ((xx * s - cx) / rx) ** 2 + ((yy * s - cy) / ry) ** 2
    g = np.exp(-d)
    if s > 1:
        g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
    return g[..., None] * np.array(color, np.float32) * power


def u8(f):
    return np.clip(f, 0, 255).astype(np.uint8)


def to_lmap(f):
    """float-множитель освещения → uint8 (128 = 1.0)."""
    return np.clip(f * 128, 0, 255).astype(np.uint8)


def apply_light(img, lmap_u8, glow_u8=None):
    out = cv2.multiply(img, lmap_u8, scale=1 / 128)
    if glow_u8 is not None:
        out = cv2.add(out, glow_u8)
    return out


def poly(img, pts, col):
    cv2.fillPoly(img, [np.int32(pts)], col, AA)


def camera(img, z, cx, cy, rot=0.0, out=(W, H)):
    """Камера: (cx, cy) — точка мира в центре кадра, z — зум."""
    ow, oh = out
    hw, hh = ow / (2 * z), oh / (2 * z)
    cx = min(max(cx, hw), img.shape[1] - hw) if img.shape[1] >= 2 * hw else img.shape[1] / 2
    cy = min(max(cy, hh), img.shape[0] - hh) if img.shape[0] >= 2 * hh else img.shape[0] / 2
    M = cv2.getRotationMatrix2D((cx, cy), rot, z)
    M[0, 2] += ow / 2 - cx
    M[1, 2] += oh / 2 - cy
    return cv2.warpAffine(img, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def shake(t, t_hit, amp=14, dur=0.35, freq=31):
    """Смещение камеры при испуге/ударе."""
    d = t - t_hit
    if d < 0 or d > dur:
        return 0.0, 0.0
    k = (1 - d / dur) ** 2 * amp
    return k * math.sin(d * freq * 6.28), k * math.cos(d * freq * 5.1)


# ---------- текст ----------
_font_cache = {}


def font(size, weight="semibold"):
    key = (size, weight)
    if key not in _font_cache:
        names = {"semibold": ["Montserrat-SemiBold.ttf"], "bold": ["Montserrat-Bold.ttf", "Montserrat-SemiBold.ttf"]}[weight]
        f = None
        for n in names:
            for d in (FONTS, Path("C:/Windows/Fonts"), Path.home() / ".fonts"):
                if (d / n).exists():
                    f = ImageFont.truetype(str(d / n), size)
                    break
            if f:
                break
        _font_cache[key] = f or ImageFont.load_default()
    return _font_cache[key]


def wrap(text, f, max_w):
    words, lines, cur = text.split(), [], ""
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text(im, xy, text, size, color=(255, 255, 255), weight="semibold", max_w=None, align="left", spacing=1.25):
    """Пишет текст на PIL-изображении (RGB/RGBA). Возвращает нижнюю границу."""
    f = font(size, weight)
    d = ImageDraw.Draw(im)
    lines = wrap(text, f, max_w) if max_w else [text]
    x, y = xy
    for ln in lines:
        tw = d.textlength(ln, font=f)
        lx = x + (max_w - tw) / 2 if (align == "center" and max_w) else x
        d.text((lx, y), ln, font=f, fill=color)
        y += size * spacing
    return y


def paste_rgba(dst, rgba, x, y, alpha=1.0):
    """Наложение RGBA (numpy, BGRA) на BGR-кадр по координатам левого верхнего угла."""
    h, w = rgba.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    x1, y1 = x0 + w, y0 + h
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(dst.shape[1], x1), min(dst.shape[0], y1)
    if cx1 <= cx0 or cy1 <= cy0 or alpha <= 0:
        return dst
    src = rgba[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    a = src[..., 3:4].astype(np.float32) * (alpha / 255)
    roi = dst[cy0:cy1, cx0:cx1]
    dst[cy0:cy1, cx0:cx1] = (roi * (1 - a) + src[..., :3] * a).astype(np.uint8)
    return dst


def pil_to_bgra(im):
    arr = np.array(im.convert("RGBA"))
    return arr[..., [2, 1, 0, 3]].copy()


def warp_rgba(rgba, scale, angle):
    """Поворот/масштаб спрайта RGBA вокруг центра; возвращает новый спрайт."""
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * sin + w * cos) + 2, int(h * cos + w * sin) + 2
    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(rgba, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))


# ---------- пост-обработка: зерно VHS, виньетка, мерцание, помехи ----------
class Post:
    def __init__(self, seed=99, grain=6.0):
        rng = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = 1 - 0.72 * np.clip(((xx - W / 2) / (W * 0.64)) ** 2 + ((yy - H / 2) / (H * 0.64)) ** 2, 0, 1)
        self.vig = cv2.merge([u8(v * 255)] * 3)
        self.grain = []
        for _ in range(12):
            g = cv2.resize(rng.normal(0, grain, (H // 2, W // 2)).astype(np.float32), (W, H))
            g3 = cv2.merge([g * 0.9, g, g * 1.1])
            self.grain.append((u8(g3), u8(-g3)))
        self.rng = np.random.default_rng(seed + 1)

    def __call__(self, img, f, fade=1.0, glitch=0.0):
        img = cv2.multiply(img, self.vig, scale=1 / 255)
        flick = 1 + 0.02 * math.sin(f * 1.7) * math.sin(f * 0.37)
        a = fade * flick
        if abs(a - 1.0) > 1e-3:
            img = cv2.convertScaleAbs(img, alpha=a)
        if glitch > 0:
            img = digital_glitch(img, glitch, f)
        pos, neg = self.grain[(f * 7) % len(self.grain)]
        return cv2.subtract(cv2.add(img, pos), neg)


def digital_glitch(img, k, f):
    """Редкие цифровые помехи: сдвиг полос и расслоение каналов."""
    rng = np.random.default_rng(f * 7919)
    out = img.copy()
    for _ in range(int(2 + k * 8)):
        y = int(rng.integers(0, H - 8))
        hh = int(rng.integers(4, 10 + int(k * 50)))
        dx = int(rng.normal(0, 25 * k + 4))
        out[y:y + hh] = np.roll(out[y:y + hh], dx, axis=1)
    if k > 0.3:
        b, g, r = cv2.split(out)
        s = int(4 + 10 * k)
        out = cv2.merge([np.roll(b, -s, axis=1), g, np.roll(r, s, axis=1)])
    return out
