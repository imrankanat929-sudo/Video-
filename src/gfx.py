"""Базовые 2D-примитивы: слои, камера с параллаксом, свет, грейдинг, зерно."""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from .config import W, H

# ---------------------------------------------------------------- palette
BLACK = (8, 8, 10)
CHAR = (16, 16, 18)
DGREY = (32, 32, 36)
GREY = (66, 66, 72)
LGREY = (120, 118, 116)
DRED = (80, 12, 12)
RED = (170, 28, 22)
ORANGE = (232, 118, 40)
AMBER = (255, 176, 92)
WARMW = (255, 226, 180)


def rgb(c, k=1.0):
    return np.array(c[:3], np.float32) / 255.0 * k


# ---------------------------------------------------------------- noise / easing
def hash1(x, seed=0):
    x = np.sin(np.asarray(x, np.float64) * 127.1 + seed * 311.7) * 43758.5453
    return x - np.floor(x)


def vnoise(t, seed=0):
    """1D value noise, smooth, 0..1."""
    i = math.floor(t); f = t - i
    a, b = float(hash1(i, seed)), float(hash1(i + 1, seed))
    f = f * f * (3 - 2 * f)
    return a + (b - a) * f


def fbm(t, seed=0, oct=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(oct):
        s += vnoise(t * (2 ** o), seed + o * 13) * amp
        tot += amp; amp *= 0.5
    return s / tot


def clamp01(x):
    return max(0.0, min(1.0, x))


def smooth(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = clamp01((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def ease_io(x):
    x = clamp01(x)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def lerp(a, b, t):
    return a + (b - a) * t


def flicker(t, seed=0, rate=9.0, depth=0.6, dropout=0.08):
    """Мигающая лампа: 0..1 яркость."""
    base = 1.0 - depth * (fbm(t * rate, seed) ** 2)
    # редкие провалы
    k = math.floor(t * 6.0)
    if hash1(k, seed + 5) < dropout:
        base *= 0.08 + 0.2 * float(hash1(k, seed + 9))
    return base


# ---------------------------------------------------------------- drawing
class Pen:
    """Рисование с суперсэмплингом: координаты в пикселях итогового слоя."""

    def __init__(self, w, h, ss=2, bg=(0, 0, 0, 0)):
        self.w, self.h, self.ss = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), bg)
        self.d = ImageDraw.Draw(self.img)

    def _p(self, pts):
        s = self.ss
        return [(x * s, y * s) for x, y in pts]

    def poly(self, pts, fill):
        self.d.polygon(self._p(pts), fill=_c(fill))

    def rect(self, x0, y0, x1, y1, fill):
        s = self.ss
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        self.d.rectangle([x0 * s, y0 * s, x1 * s - 1, y1 * s - 1], fill=_c(fill))

    def rrect(self, x0, y0, x1, y1, r, fill):
        s = self.ss
        self.d.rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s], r * s, fill=_c(fill))

    def ellipse(self, cx, cy, rx, ry, fill):
        s = self.ss
        self.d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=_c(fill))

    def line(self, pts, fill, width):
        self.d.line(self._p(pts), fill=_c(fill), width=max(1, int(width * self.ss)), joint="curve")
        r = width / 2
        for x, y in (pts[0], pts[-1]):
            self.ellipse(x, y, r, r, fill)

    def text(self, x, y, s, font, size, fill, anchor="la", spacing=0):
        f = font_(font, int(size * self.ss))
        self.d.text((x * self.ss, y * self.ss), s, font=f, fill=_c(fill), anchor=anchor,
                    spacing=spacing * self.ss)

    def arr(self, blur=0.0):
        im = self.img
        if self.ss != 1:
            im = im.resize((self.w, self.h), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255.0
        a = a.copy()
        a[..., :3] *= a[..., 3:4]  # premultiplied
        if blur > 0:
            a = cv2.GaussianBlur(a, (0, 0), blur)
        return a


def _c(c):
    if len(c) == 3:
        return tuple(int(v) for v in c) + (255,)
    return tuple(int(v) for v in c)


_FONTS = {}


def font_(path, size):
    k = (path, size)
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(path, size)
    return _FONTS[k]


def text_layer(lines, font, size, color=(235, 230, 222), w=W, h=H, anchor="mm", glow=0, glow_color=None,
               tracking=0):
    """lines: list of (text, x, y, size_mult). returns premult RGBA."""
    p = Pen(w, h, ss=1)
    for item in lines:
        s, x, y = item[:3]
        m = item[3] if len(item) > 3 else 1.0
        col = item[4] if len(item) > 4 else color
        fnt = item[5] if len(item) > 5 else font
        p.text(x, y, s, fnt, size * m, col, anchor=anchor)
    a = p.arr()
    if glow:
        g = cv2.GaussianBlur(a, (0, 0), glow)
        gc = rgb(glow_color or color)
        g[..., :3] = g[..., 3:4] * gc
        a = a + g * 0.9 * (1 - a[..., 3:4])
    return a


def vgrad(w, h, stops):
    """Вертикальный градиент: stops = [(pos, color), ...] -> RGB float."""
    ys = np.linspace(0, 1, h, dtype=np.float32)
    pos = [s[0] for s in stops]
    out = np.zeros((h, 3), np.float32)
    for c in range(3):
        out[:, c] = np.interp(ys, pos, [s[1][c] / 255.0 for s in stops])
    return np.repeat(out[:, None, :], w, axis=1)


def solid(w, h, rgbimg, alpha=1.0):
    a = np.ones((h, w, 1), np.float32) * alpha
    return np.concatenate([rgbimg * alpha, a], axis=2)


def radial(w, h, cx, cy, r, color, power=2.0, k=1.0, sy=1.0):
    """Аддитивное пятно света (RGB float)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) / sy) ** 2) / r
    f = np.clip(1 - d, 0, 1) ** power * k
    return f[..., None] * rgb(color)


def cone(w, h, x0, y0, ang, spread, length, color, k=1.0, soft=0.5):
    """Луч фонарика: аддитивный конус (RGB float)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - x0, yy - y0
    dist = np.sqrt(dx * dx + dy * dy) + 1e-3
    a = np.arctan2(dy, dx) - ang
    a = (a + np.pi) % (2 * np.pi) - np.pi
    edge = np.clip(1 - np.abs(a) / spread, 0, 1) ** (1 + soft * 2)
    fall = np.clip(1 - dist / length, 0, 1) ** 1.5
    f = edge * fall * k
    return f[..., None] * rgb(color)


def over(dst, src):
    """premult over: dst, src RGBA."""
    return src + dst * (1 - src[..., 3:4])


def paste(dst, src, x, y):
    """Наложить src (premult RGBA) на dst (RGBA или RGB) в позиции x,y."""
    h, w = src.shape[:2]
    H0, W0 = dst.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W0, x0 + w), min(H0, y0 + h)
    if dx1 <= dx0 or dy1 <= dy0:
        return dst
    s = src[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)]
    d = dst[dy0:dy1, dx0:dx1]
    if dst.shape[2] == 4:
        dst[dy0:dy1, dx0:dx1] = s + d * (1 - s[..., 3:4])
    else:
        dst[dy0:dy1, dx0:dx1] = s[..., :3] + d * (1 - s[..., 3:4])
    return dst


def rim(layer, dx, dy, color, k=1.0, blur=1.5):
    """Контровой свет по краю силуэта, со стороны (dx,dy) к источнику."""
    a = layer[..., 3]
    M = np.float32([[1, 0, -dx], [0, 1, -dy]])
    sh = cv2.warpAffine(a, M, (a.shape[1], a.shape[0]))
    edge = np.clip(a - sh, 0, 1)
    if blur:
        edge = cv2.GaussianBlur(edge, (0, 0), blur) * a
    out = layer.copy()
    out[..., :3] += edge[..., None] * rgb(color) * k
    return out


def tint(layer, color, k):
    out = layer.copy()
    out[..., :3] = out[..., :3] * (1 - k) + out[..., 3:4] * rgb(color) * k
    return out


# ---------------------------------------------------------------- camera & layers
class Layer:
    """img размещается в системе координат «мира» размера ref (по умолчанию — размер img) со сдвигом ox,oy."""

    def __init__(self, img, depth=1.0, add=False, name="", ox=0.0, oy=0.0, ref=None):
        self.img = img  # premult RGBA (или RGB для add)
        self.depth = depth
        self.add = add
        self.name = name
        self.h, self.w = img.shape[:2]
        self.ox, self.oy = ox, oy
        self.ref = ref or (self.w, self.h)


class Cam:
    """zoom, сдвиг (px от центра слоя), поворот (рад), тряска."""

    def __init__(self, zoom=1.0, x=0.0, y=0.0, rot=0.0):
        self.zoom, self.x, self.y, self.rot = zoom, x, y, rot

    def shake(self, t, amp, seed=1, rate=18.0):
        if amp <= 0:
            return self
        self.x += (fbm(t * rate, seed) - 0.5) * 2 * amp
        self.y += (fbm(t * rate, seed + 7) - 0.5) * 2 * amp
        self.rot += (fbm(t * rate * 0.7, seed + 3) - 0.5) * amp * 0.0012
        return self


def warp(img, cam, depth, out_w=W, out_h=H, interp=cv2.INTER_LINEAR, ref=None, ox=0.0, oy=0.0):
    h, w = img.shape[:2]
    if ref is not None:
        w, h = ref
    z = 1.0 + (cam.zoom - 1.0) * depth
    px, py = cam.x * depth, cam.y * depth
    cx, cy = w / 2 + px, h / 2 + py
    c, s = math.cos(cam.rot * depth) * z, math.sin(cam.rot * depth) * z
    M = np.float32([[c, -s, out_w / 2 - (c * cx - s * cy) + c * ox - s * oy],
                    [s, c, out_h / 2 - (s * cx + c * cy) + s * ox + c * oy]])
    return cv2.warpAffine(img, M, (out_w, out_h), flags=interp, borderMode=cv2.BORDER_CONSTANT,
                          borderValue=0)


def compose(layers, cam, base=None):
    out = np.zeros((H, W, 3), np.float32) if base is None else base
    for L in layers:
        if L is None:
            continue
        mul = None
        if isinstance(L, tuple):  # (layer, opacity[, mul])
            if len(L) == 3:
                L, gain, mul = L
            else:
                L, gain = L
        else:
            gain = 1.0
        if gain <= 0.001:
            continue
        im = warp(L.img, cam, L.depth, ref=L.ref, ox=L.ox, oy=L.oy)
        if L.add:
            c = im[..., :3] * gain
            out += c if mul is None else c * mul
        else:
            g = min(gain, 1.0)
            col = im[..., :3] * g
            if mul is not None:
                col = col * mul
            out = col + out * (1 - im[..., 3:4] * g)
    return out


# ---------------------------------------------------------------- grading
_GRAIN = None
_VIG = None
_rng = np.random.default_rng(7)


def _init_post():
    global _GRAIN, _VIG
    if _GRAIN is None:
        g = []
        for i in range(12):
            n = _rng.normal(0, 1, (H // 2 + 8, W // 2 + 8)).astype(np.float32)
            n = cv2.GaussianBlur(n, (0, 0), 0.6)
            n = cv2.resize(n, (W + 16, H + 16), interpolation=cv2.INTER_LINEAR)
            g.append(n)
        _GRAIN = g
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2 * 0.85)
        _VIG = np.clip(1 - 0.55 * np.clip(d - 0.35, 0, None) ** 1.6, 0.2, 1)[..., None].astype(np.float32)


def grade(img, t, exposure=1.0, warmth=0.0, grain=0.05, vignette=1.0, desat=0.25, weave=True,
          red_shadow=0.0):
    _init_post()
    x = img * exposure
    # тонмаппинг с мягким плечом
    x = x / (1 + np.maximum(x - 0.7, 0) * 1.2)
    lum = (x[..., 0] * 0.3 + x[..., 1] * 0.55 + x[..., 2] * 0.15)[..., None]
    x = x * (1 - desat) + lum * desat
    if warmth:
        x = x * np.array([1 + 0.10 * warmth, 1 + 0.01 * warmth, 1 - 0.14 * warmth], np.float32)
    if red_shadow:
        sh = np.clip(1 - lum * 3, 0, 1)
        x = x + sh * np.array([0.03, 0.0, 0.0], np.float32) * red_shadow
    # подъём чёрного + лёгкая кривая
    x = np.clip(x, 0, 1)
    x = 0.012 + x * (1 - 0.012)
    x = x * x * (3 - 2 * x) * 0.35 + x * 0.65
    if vignette:
        x = x * (1 - (1 - _VIG) * vignette)
    if grain:
        fi = int(t * 24)
        n = _GRAIN[fi % len(_GRAIN)]
        ox, oy = int(hash1(fi, 3) * 16), int(hash1(fi, 4) * 16)
        n = n[oy:oy + H, ox:ox + W, None]
        amp = grain * (0.55 + 0.9 * np.sqrt(np.clip(1 - lum, 0, 1)))
        x = x + n * amp * 0.5
    # пыль/царапины плёнки (редко)
    fi = int(t * 24)
    if hash1(fi, 21) < 0.05:
        px, py = int(hash1(fi, 22) * W), int(hash1(fi, 23) * H)
        r = 1 + int(hash1(fi, 24) * 3)
        cv2.circle(x, (px, py), r, (0.0, 0.0, 0.0), -1, lineType=cv2.LINE_AA) if hash1(fi, 25) < .5 else \
            cv2.circle(x, (px, py), r, (0.5, 0.48, 0.45), -1, lineType=cv2.LINE_AA)
    if hash1(fi, 31) < 0.025:
        sx = int(hash1(fi, 32) * W)
        x[:, sx:sx + 1] *= 0.75
    return np.clip(x, 0, 1)


def to_u8(x):
    return (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)


# ---------------------------------------------------------------- particles
class Particles:
    """Пепел/пыль: детерминированные частицы, рисуются аддитивно."""

    def __init__(self, n, seed=0, color=AMBER, size=(1.0, 3.0), speed=(10, 40), drift=(-15, 15), k=0.6,
                 upward=True):
        r = np.random.default_rng(seed)
        self.x = r.uniform(0, W, n); self.y = r.uniform(0, H, n)
        self.s = r.uniform(*size, n); self.v = r.uniform(*speed, n)
        self.dr = r.uniform(*drift, n); self.ph = r.uniform(0, 6.28, n)
        self.b = r.uniform(0.3, 1.0, n)
        self.color, self.k, self.up = color, k, upward

    def draw(self, img, t, gain=1.0):
        if gain <= 0:
            return img
        layer = np.zeros((H, W), np.float32)
        sgn = -1 if self.up else 1
        xs = (self.x + self.dr * t + 20 * np.sin(t * 0.5 + self.ph)) % W
        ys = (self.y + sgn * self.v * t) % H
        for x, y, s, b, ph in zip(xs, ys, self.s, self.b, self.ph):
            tw = 0.6 + 0.4 * math.sin(t * 3 + ph)
            cv2.circle(layer, (int(x), int(y)), max(1, int(s)), float(b * tw), -1, lineType=cv2.LINE_AA)
        layer = cv2.GaussianBlur(layer, (0, 0), 1.0)
        img += layer[..., None] * rgb(self.color) * self.k * gain
        return img


# ---------------------------------------------------------------- screen-space lights (half-res, cached grid)
_GRID = None


def _grid():
    global _GRID
    if _GRID is None:
        yy, xx = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)
        _GRID = (xx * 2, yy * 2)
    return _GRID


def _up(f):
    return cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR)


def sl_radial(cx, cy, r, power=2.0, k=1.0, sy=1.0):
    xx, yy = _grid()
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) / sy) ** 2) / r
    return _up(np.clip(1 - d, 0, 1) ** power * k)


def sl_cone(x0, y0, ang, spread, length, k=1.0, soft=0.5):
    xx, yy = _grid()
    dx, dy = xx - x0, yy - y0
    dist = np.sqrt(dx * dx + dy * dy) + 1e-3
    a = np.arctan2(dy, dx) - ang
    a = (a + np.pi) % (2 * np.pi) - np.pi
    edge = np.clip(1 - np.abs(a) / spread, 0, 1) ** (1 + soft * 2)
    fall = np.clip(1 - dist / length, 0, 1) ** 1.3
    hot = np.clip(1 - dist / 90, 0, 1)
    return _up(edge * fall * k + hot * 0.8 * k)


def lit(albedo, light_rgb):
    """albedo (H,W,3) * свет (H,W) или (H,W,3)."""
    if light_rgb.ndim == 2:
        light_rgb = light_rgb[..., None]
    return albedo * light_rgb
