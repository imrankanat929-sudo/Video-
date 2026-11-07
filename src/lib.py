"""Drawing primitives for the procedural 9:16 video."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 1080, 1920
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(os.path.dirname(__file__), "..", "fonts"))
_fonts = {}


def font(size, weight=900):
    key = (size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat.ttf"), size)
        f.set_variation_by_axes([weight])
        _fonts[key] = f
    return _fonts[key]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def to_img(a):
    return Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))


def to_arr(img):
    return np.asarray(img).astype(np.float32) / 255.0


# ---------------------------------------------------------------- noise
def fnoise(h, w, seed, octaves=5, base=3, persist=0.5):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        ny = base * 2 ** o
        nx = max(2, int(round(ny * w / h)))
        g = rng.random((ny + 1, nx + 1)).astype(np.float32)
        out += np.asarray(Image.fromarray(g, "F").resize((w, h), Image.BICUBIC)) * amp
        tot += amp
        amp *= persist
    out /= tot
    out -= out.min()
    out /= max(out.max(), 1e-6)
    return out


def vgrad(w, h, stops):
    """Vertical gradient. stops = [(pos0..1, '#hex'), ...]"""
    ys = np.linspace(0, 1, h)
    pos = [s[0] for s in stops]
    cols = np.array([rgb(s[1]) for s in stops], np.float32) / 255
    a = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        a[:, :, c] = np.interp(ys, pos, cols[:, c])[:, None]
    return a


def radial(w, h, cx, cy, r, power=2.0):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    return np.clip(1 - d, 0, 1) ** power


def glow_sprite(size, color, power=2.2, core=0.0):
    """RGBA soft radial glow."""
    a = radial(size, size, size / 2, size / 2, size / 2, power)
    if core:
        a = np.clip(a + core * radial(size, size, size / 2, size / 2, size / 6, 1.5), 0, 1)
    img = Image.new("RGBA", (size, size), color + (0,))
    img.putalpha(to_img(a).convert("L"))
    return img


# ---------------------------------------------------------------- compositing
def add_glow(base, layer, alpha=1.0):
    """Additive blend of an RGB/RGBA layer onto RGB base."""
    if layer.mode == "RGBA":
        l = to_arr(layer)
        add = l[:, :, :3] * l[:, :, 3:4] * alpha
    else:
        add = to_arr(layer) * alpha
    b = to_arr(base)
    return to_img(np.clip(b + add, 0, 1))


def bloom(img, strength=0.6, radius=12, thresh=0.55):
    small = img.resize((img.width // 4, img.height // 4), Image.BILINEAR)
    a = to_arr(small)
    a = np.clip((a - thresh) / (1 - thresh), 0, 1)
    b = to_img(a).filter(ImageFilter.GaussianBlur(radius / 4 + 1)).resize(img.size, Image.BILINEAR)
    return ImageChops.add(img, Image.eval(b, lambda v: int(v * strength)))


def paste(base, sprite, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    """Paste RGBA sprite centred at (cx, cy) on an RGB/RGBA image (in place)."""
    s = sprite
    if scale != 1.0:
        nw, nh = max(1, int(s.width * scale)), max(1, int(s.height * scale))
        s = s.resize((nw, nh), Image.BILINEAR)
    if rot:
        s = s.rotate(rot, Image.BILINEAR, expand=True)
    if alpha < 1.0:
        s = s.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - s.width / 2), int(cy - s.height / 2)
    base.paste(s, (x, y), s)
    return base


def cam(img, zoom=1.0, cx=None, cy=None, rot=0.0, out=(W, H)):
    """Virtual camera: crop+scale around (cx, cy) of img. zoom>1 = closer."""
    if cx is None:
        cx = img.width / 2
    if cy is None:
        cy = img.height / 2
    s = (img.height / out[1]) / zoom
    s = min(s, img.width / out[0] / zoom) if img.width / img.height < out[0] / out[1] else s
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    a, b = s * c, -s * sn
    d, e = s * sn, s * c
    c0 = cx - a * out[0] / 2 - b * out[1] / 2
    f0 = cy - d * out[0] / 2 - e * out[1] / 2
    return img.transform(out, Image.AFFINE, (a, b, c0, d, e, f0), Image.BILINEAR)


def shake(t, amp, freq=18.0, seed=0):
    if amp <= 0:
        return 0.0, 0.0, 0.0
    x = (math.sin(t * freq * 1.3 + seed) + 0.6 * math.sin(t * freq * 2.7 + seed * 2)) * amp
    y = (math.cos(t * freq * 1.1 + seed * 3) + 0.6 * math.sin(t * freq * 3.1 + seed)) * amp
    r = math.sin(t * freq * 0.9 + seed) * amp * 0.02
    return x, y, r


# ---------------------------------------------------------------- text
def text_size(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1]


def wrap(txt, f, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_size(t, f)[0] <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_c(draw, txt, cx, cy, f, fill=(255, 255, 255), stroke=0, sfill=(0, 0, 0), anchor="mm"):
    draw.text((cx, cy), txt, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


@lru_cache(512)
def text_layer(txt, size, fill, stroke=0, sfill=(0, 0, 0), weight=900, shadow=0, glow=None, maxw=980):
    """Render a single text line to an RGBA sprite (for scaling/pop animations)."""
    f = font(size, weight)
    tw, th = text_size(txt, f)
    while tw + stroke * 2 > maxw and size > 20:
        size = int(size * 0.95)
        f = font(size, weight)
        tw, th = text_size(txt, f)
    pad = stroke + shadow + 40 + (30 if glow else 0)
    img = Image.new("RGBA", (tw + pad * 2, int(size * 1.4) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = img.width / 2, img.height / 2
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).text((cx, cy), txt, font=f, fill=glow + (255,), anchor="mm", stroke_width=stroke + 6)
        g = g.filter(ImageFilter.GaussianBlur(18))
        img.alpha_composite(g)
        img.alpha_composite(g)
    if shadow:
        d.text((cx + shadow, cy + shadow), txt, font=f, fill=(0, 0, 0, 160), anchor="mm", stroke_width=stroke)
    d.text((cx, cy), txt, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)
    return img


# ---------------------------------------------------------------- space
@lru_cache(None)
def starfield(w, h, seed=1, n=2200, nebula=True, tint=("#05070f", "#0b1026", "#04050a")):
    rng = np.random.default_rng(seed)
    a = vgrad(w, h, [(0, tint[0]), (0.5, tint[1]), (1, tint[2])])
    if nebula:
        n1 = fnoise(h // 4, w // 4, seed + 5, 6, 2)
        n2 = fnoise(h // 4, w // 4, seed + 9, 6, 2)
        neb = np.zeros((h // 4, w // 4, 3), np.float32)
        neb += (np.clip(n1 - 0.45, 0, 1) ** 1.6)[:, :, None] * np.array([0.35, 0.12, 0.5])
        neb += (np.clip(n2 - 0.5, 0, 1) ** 1.6)[:, :, None] * np.array([0.05, 0.25, 0.45])
        neb = np.asarray(to_img(neb).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255
        a = a + neb * 0.9
    img = to_img(a)
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rng.random() * w, rng.random() * h
        b = rng.random() ** 4
        r = 0.6 + b * 2.4
        col = rng.choice([(255, 255, 255), (200, 220, 255), (255, 230, 200)])
        v = int(90 + 165 * min(1, b * 2 + 0.2))
        c = tuple(int(cc * v / 255) for cc in col)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    gl = img.filter(ImageFilter.GaussianBlur(3))
    return ImageChops.add(img, Image.eval(gl, lambda v: int(v * 0.8)))


@lru_cache(None)
def asteroid(D, seed=3, light=(0.75, -0.45, 0.5), base=(0.42, 0.38, 0.35)):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:D, 0:D].astype(np.float32)
    x = (x - D / 2) / (D / 2)
    y = (y - D / 2) / (D / 2)
    ang = np.arctan2(y, x)
    r = np.sqrt(x * x + y * y)
    deform = np.zeros_like(r)
    for k in range(2, 9):
        deform += np.sin(k * ang + rng.random() * 6.28) * (0.07 / k ** 0.9) * rng.random()
    R = 0.86 * (1 + deform)
    edge = np.clip((R - r) * D * 0.25, 0, 1)
    rr = np.clip(r / R, 0, 0.999)
    nz = np.sqrt(1 - rr ** 2)
    nx, ny = x / R, y / R
    h = fnoise(D, D, seed, 7, 3) * 0.9
    for _ in range(26):
        cx, cy = rng.uniform(-0.75, 0.75), rng.uniform(-0.75, 0.75)
        cr = rng.uniform(0.03, 0.2) * (rng.random() ** 1.5 + 0.3)
        dd = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / cr
        bowl = np.where(dd < 1, -(1 - dd ** 2), 0) + np.where((dd >= 1) & (dd < 1.35), 0.25 * (1 - (dd - 1) / 0.35), 0)
        h += bowl * cr * 1.6
    gy, gx = np.gradient(h)
    k = D * 0.9
    nx2, ny2, nz2 = nx - gx * k * 0.6, ny - gy * k * 0.6, nz
    nl = np.sqrt(nx2 ** 2 + ny2 ** 2 + nz2 ** 2) + 1e-6
    L = np.array(light, np.float32)
    L /= np.linalg.norm(L)
    shade = np.clip((nx2 * L[0] + ny2 * L[1] + nz2 * L[2]) / nl, 0, 1)
    tex = fnoise(D, D, seed + 7, 6, 6)
    col = np.array(base, np.float32)[None, None, :] * (0.55 + 0.7 * tex[:, :, None])
    rgb_ = col * (0.04 + 1.15 * shade[:, :, None] ** 1.2)
    # rim light (cool, from behind)
    rim = np.clip(rr - 0.75, 0, 1) / 0.25 * np.clip(-(nx * L[0] + ny * L[1]), 0, 1)
    rgb_ += rim[:, :, None] * np.array([0.25, 0.32, 0.45]) * 0.6
    img = to_img(rgb_).convert("RGBA")
    img.putalpha(to_img(edge).convert("L"))
    return img


@lru_cache(None)
def earth_texture(seed=11, TW=1024, TH=512):
    land = fnoise(TH, TW, seed, 7, 3)
    lat = np.linspace(1, -1, TH)[:, None] * np.ones((1, TW))
    land = land - 0.1 * np.abs(lat)
    is_land = np.clip((land - 0.53) * 18, 0, 1)
    veg = fnoise(TH, TW, seed + 1, 6, 4)
    ocean = np.stack([0.02 + 0.03 * land, 0.10 + 0.12 * land, 0.28 + 0.2 * land], -1)
    green = np.stack([0.12 + 0.25 * veg, 0.30 + 0.12 * veg, 0.10 + 0.04 * veg], -1)
    desert = np.array([0.55, 0.45, 0.28])
    landc = green * (1 - veg[:, :, None] ** 3) + desert * veg[:, :, None] ** 3
    tex = ocean * (1 - is_land[:, :, None]) + landc * is_land[:, :, None]
    ice = np.clip((np.abs(lat) - 0.82) * 12, 0, 1)
    tex = tex * (1 - ice[:, :, None]) + 0.92 * ice[:, :, None]
    clouds = fnoise(TH, TW, seed + 2, 7, 5)
    clouds = np.clip((clouds - 0.5) * 3.2, 0, 1) ** 1.3
    return tex.astype(np.float32), clouds.astype(np.float32)


@lru_cache(None)
def _earth_geom(D):
    y, x = np.mgrid[0:D, 0:D].astype(np.float32)
    x = (x - D / 2) / (D / 2 * 0.86)
    y = (y - D / 2) / (D / 2 * 0.86)
    r2 = x * x + y * y
    inside = r2 < 1
    z = np.sqrt(np.clip(1 - r2, 0, 1))
    lat = np.arcsin(np.clip(-y, -1, 1))
    lon = np.arctan2(x, z)
    return x, y, z, r2, inside, lat, lon


def earth(D, lon0=0.0, light=(-0.55, -0.35, 0.75), dust=0.0, dust_seed=4, glow_col=(0.35, 0.6, 1.0), night_lights=True):
    tex, clouds = earth_texture()
    TH, TW = clouds.shape
    x, y, z, r2, inside, lat, lon = _earth_geom(D)
    u = ((lon + lon0) / (2 * np.pi) % 1.0) * (TW - 1)
    v = (0.5 - lat / np.pi) * (TH - 1)
    ui, vi = u.astype(np.int32), np.clip(v.astype(np.int32), 0, TH - 1)
    col = tex[vi, ui]
    cl = clouds[vi, (ui + 37) % TW][:, :, None]
    col = col * (1 - cl * 0.85) + cl * 0.95
    L = np.array(light, np.float32)
    L /= np.linalg.norm(L)
    lam = np.clip(x * L[0] + y * L[1] + z * L[2], -1, 1)
    day = np.clip(lam * 1.4 + 0.12, 0, 1)
    out = col * (0.02 + day[:, :, None] * 1.05)
    if night_lights:
        cities = (tex[vi, ui, 1] > 0.3) * (tex[vi, ui, 2] < 0.2)
        nl = np.clip(-lam * 3, 0, 1) * cities * (fnoise_cached()[vi, ui] > 0.62)
        out += nl[:, :, None] * np.array([1.0, 0.75, 0.35]) * 0.7
    if dust > 0:
        dn = fnoise_cached(dust_seed)[vi, ui]
        dm = np.clip(dust * (0.6 + 0.8 * dn), 0, 0.95)[:, :, None]
        dcol = np.array([0.38, 0.32, 0.27]) * (0.15 + day[:, :, None])
        out = out * (1 - dm) + dcol * dm
    # atmosphere
    r = np.sqrt(r2)
    atm_in = np.clip((r - 0.7) / 0.3, 0, 1) ** 2.5 * inside
    out += atm_in[:, :, None] * np.array(glow_col) * 0.55 * (0.25 + day[:, :, None])
    outer = np.clip(1 - (r - 1) / 0.12, 0, 1) ** 2 * (~inside)
    rimlit = np.clip((x * L[0] + y * L[1]) / (r + 1e-6) * 0.8 + 0.5, 0.1, 1)
    alpha = np.where(inside, np.clip((1 - r) * D * 0.4, 0, 1), outer * 0.85 * rimlit)
    out = np.where(inside[:, :, None], out, np.array(glow_col)[None, None, :] * rimlit[:, :, None])
    img = to_img(out).convert("RGBA")
    img.putalpha(to_img(alpha).convert("L"))
    return img


@lru_cache(None)
def fnoise_cached(seed=21):
    return fnoise(512, 1024, seed, 7, 6)


# ---------------------------------------------------------------- city / people
@lru_cache(None)
def skyline(w, h, seed, color="#05060a", win=True, win_col="#ffcf7a", density=0.25, minh=0.25, maxh=1.0, broken=False):
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = rgb(color) + (255,)
    wc = rgb(win_col)
    x = -20
    while x < w:
        bw = int(rng.uniform(50, 150))
        bh = int(h * rng.uniform(minh, maxh) ** 1.3)
        top = h - bh
        if broken:
            pts = [(x, h), (x, top + rng.uniform(0, 40))]
            nseg = int(rng.integers(3, 7))
            for i in range(1, nseg):
                pts.append((x + bw * i / nseg, top + rng.uniform(0, bh * 0.35)))
            pts += [(x + bw, top + rng.uniform(0, 60)), (x + bw, h)]
            d.polygon(pts, fill=c)
        else:
            d.rectangle([x, top, x + bw, h], fill=c)
            if rng.random() < 0.3:
                d.rectangle([x + bw * 0.4, top - bh * 0.12, x + bw * 0.45, top], fill=c)
            if rng.random() < 0.25:
                d.rectangle([x + bw * 0.15, top - 18, x + bw * 0.85, top], fill=c)
        if win and not broken:
            for wy in range(top + 14, h - 8, 22):
                for wx in range(x + 8, x + bw - 10, 18):
                    if rng.random() < density:
                        k = rng.uniform(0.5, 1.0)
                        d.rectangle([wx, wy, wx + 8, wy + 11], fill=tuple(int(v * k) for v in wc) + (255,))
        x += bw + int(rng.uniform(-10, 14))
    return img


def person(d, cx, base, h, col, pose="stand", lean=0.0, arm=None):
    """Silhouette person. pose: stand, point, back (from behind, shoulders wider)."""
    hr = h * 0.068
    hy = base - h + hr
    sh_y = hy + hr * 1.55
    sw = h * (0.13 if pose != "back" else 0.15)
    hip_y = base - h * 0.47
    cx2 = cx + lean * h * 0.1
    d.ellipse([cx2 - hr, hy - hr, cx2 + hr, hy + hr], fill=col)
    d.rectangle([cx2 - hr * 0.45, hy + hr * 0.6, cx2 + hr * 0.45, sh_y + 4], fill=col)
    d.rounded_rectangle([cx2 - sw, sh_y, cx2 + sw, hip_y + h * 0.04], radius=int(sw * 0.45), fill=col)
    lw = h * 0.055
    d.polygon([(cx2 - sw * 0.85, hip_y - 5), (cx2 - 2, hip_y - 5), (cx - lw * 0.4, base), (cx - sw * 0.9 - lw * 0.3, base)], fill=col)
    d.polygon([(cx2 + 2, hip_y - 5), (cx2 + sw * 0.85, hip_y - 5), (cx + sw * 0.9 + lw * 0.3, base), (cx + lw * 0.4, base)], fill=col)
    aw = max(2, int(h * 0.05))
    if arm == "point":
        d.line([(cx2 + sw * 0.8, sh_y + aw), (cx2 + sw + h * 0.22, sh_y - h * 0.22)], fill=col, width=aw)
        d.line([(cx2 - sw * 0.85, sh_y + aw), (cx2 - sw - h * 0.03, hip_y + h * 0.02)], fill=col, width=aw)
    elif arm == "up":
        for s in (-1, 1):
            d.line([(cx2 + s * sw * 0.8, sh_y + aw), (cx2 + s * (sw + h * 0.1), sh_y - h * 0.25)], fill=col, width=aw)
    elif arm == "out":
        for s in (-1, 1):
            d.line([(cx2 + s * sw * 0.8, sh_y + aw), (cx2 + s * (sw + h * 0.2), sh_y + h * 0.17)], fill=col, width=aw)
    elif arm == "phone":
        d.line([(cx2 + sw * 0.8, sh_y + aw), (cx2 + sw + h * 0.05, sh_y + h * 0.18)], fill=col, width=aw)
        d.line([(cx2 + sw + h * 0.05, sh_y + h * 0.18), (cx2 + h * 0.06, sh_y + h * 0.05)], fill=col, width=aw)
        d.line([(cx2 - sw * 0.85, sh_y + aw), (cx2 - sw - h * 0.03, hip_y + h * 0.02)], fill=col, width=aw)
    else:
        for s in (-1, 1):
            d.line([(cx2 + s * sw * 0.85, sh_y + aw), (cx2 + s * (sw + h * 0.03), hip_y + h * 0.04)], fill=col, width=aw)


def bust(d, cx, base, h, col):
    """Head and shoulders from behind (crowd foreground)."""
    hr = h * 0.17
    hy = base - h + hr
    d.ellipse([cx - hr * 0.92, hy - hr, cx + hr * 0.92, hy + hr * 1.15], fill=col)
    d.rectangle([cx - hr * 0.55, hy + hr * 0.6, cx + hr * 0.55, hy + hr * 1.8], fill=col)
    d.ellipse([cx - h * 0.46, hy + hr * 1.45, cx + h * 0.46, hy + hr * 1.45 + h * 0.5], fill=col)
    d.rectangle([cx - h * 0.46, hy + hr * 1.45 + h * 0.25, cx + h * 0.46, base + h], fill=col)


@lru_cache(None)
def vignette(strength=0.55):
    y, x = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
    dx = (x - W / 8) / (W / 8)
    dy = (y - H / 8) / (H / 8)
    v = 1 - strength * np.clip((dx ** 2 * 0.9 + dy ** 2 * 0.7) - 0.25, 0, 1.2) / 1.2
    return to_img(np.repeat(v[:, :, None], 3, -1)).resize((W, H), Image.BILINEAR)


@lru_cache(None)
def grain_frames(n=8):
    rng = np.random.default_rng(5)
    out = []
    for _ in range(n):
        g = rng.normal(0, 1, (H // 3, W // 3)).astype(np.float32)
        out.append(Image.fromarray(np.clip(128 + g * 3.2, 0, 255).astype(np.uint8), "L").resize((W, H), Image.NEAREST).convert("RGB"))
    return out


def phone_body(sw=620, sh=1300, r=80):
    img = Image.new("RGBA", (sw + 40, sh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, sw + 39, sh + 39], radius=r + 18, fill=(30, 32, 38, 255))
    d.rounded_rectangle([4, 4, sw + 35, sh + 35], radius=r + 14, fill=(8, 8, 10, 255))
    return img, (20, 20, sw + 20, sh + 20), r


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
    return m


def warn_icon(d, cx, cy, s, col=(255, 255, 255), bg=(220, 30, 40)):
    d.polygon([(cx, cy - s), (cx + s * 1.1, cy + s * 0.85), (cx - s * 1.1, cy + s * 0.85)], fill=col)
    d.polygon([(cx, cy - s * 0.62), (cx + s * 0.78, cy + s * 0.68), (cx - s * 0.78, cy + s * 0.68)], fill=bg)
    d.rectangle([cx - s * 0.09, cy - s * 0.3, cx + s * 0.09, cy + s * 0.25], fill=col)
    d.ellipse([cx - s * 0.11, cy + s * 0.36, cx + s * 0.11, cy + s * 0.58], fill=col)


def glitch(img, amt, t):
    """RGB split + slice offsets."""
    if amt <= 0:
        return img
    r, g, b = img.split()
    o = int(amt * 30)
    r = ImageChops.offset(r, o, 0)
    b = ImageChops.offset(b, -o, int(amt * 6))
    img = Image.merge("RGB", (r, g, b))
    rng = np.random.default_rng(int(t * 60))
    for _ in range(int(amt * 10)):
        y0 = int(rng.random() * H)
        hh = int(rng.uniform(10, 80))
        sl = img.crop((0, y0, W, min(H, y0 + hh)))
        img.paste(sl, (int(rng.uniform(-80, 80) * amt), y0))
    return img
