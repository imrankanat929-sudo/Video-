"""DIDAO engine - core: canvas, camera, colour, easing, noise, video output.

All Didao episodes are rendered with this engine so characters, forest and
lighting stay identical between scenes and between episodes.
World units are metres. +x right, +y up, +z away from the default camera.
"""
import math
import random
import subprocess

import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/usr/share/fonts/truetype/"


# --------------------------------------------------------------------------
# maths helpers
# --------------------------------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def seg(t, a, b):
    """0..1 progress of t inside [a, b]."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def keys(t, pts, fn=ease_in_out):
    """Piecewise interpolation through (time, value) keyframes.
    value may be a number or a tuple."""
    if t <= pts[0][0]:
        return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t <= t1:
            u = fn(seg(t, t0, t1))
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
            return lerp(v0, v1, u)
    return pts[-1][1]


_NOISE = [random.Random(1234).random() for _ in range(4096)]


def vnoise(x, seed=0):
    """Smooth 1-D value noise in [-1, 1]."""
    x = x + seed * 57.31
    i = math.floor(x)
    f = x - i
    a = _NOISE[i % 4096]
    b = _NOISE[(i + 1) % 4096]
    u = f * f * (3 - 2 * f)
    return (a + (b - a) * u) * 2 - 1


def fbm(x, seed=0, octaves=3):
    v, amp, fr, tot = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        v += vnoise(x * fr, seed + o * 13) * amp
        tot += amp
        amp *= 0.5
        fr *= 2.03
    return v / tot


# --------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------
def hexc(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def mul(c, k):
    return (c[0] * k[0], c[1] * k[1], c[2] * k[2], c[3] if len(c) > 3 else 1.0)


def sk(c, alpha=None):
    a = c[3] if len(c) > 3 else 1.0
    if alpha is not None:
        a = alpha
    return skia.Color4f(clamp(c[0]), clamp(c[1]), clamp(c[2]), clamp(a))


def col(c, alpha=None):
    f = sk(c, alpha)
    return f.toColor()


def paint(c=None, alpha=None, stroke=None, aa=True, blend=None, shader=None,
          blur=None, cap=None, join=None, cf=None):
    p = skia.Paint(AntiAlias=aa)
    if c is not None:
        p.setColor4f(sk(c, alpha))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap or skia.Paint.kRound_Cap)
        p.setStrokeJoin(join or skia.Paint.kRound_Join)
    if blend is not None:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if cf is not None:
        p.setColorFilter(cf)
    return p


def lin_grad(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear(
        [skia.Point(*p0), skia.Point(*p1)], [col(c) for c in colors], pos)


def rad_grad(c, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), max(r, 1e-4), [col(c2) for c2 in colors], pos)


def tint_filter(mult, add=(0, 0, 0)):
    """Colour matrix: out = in*mult + add (rgb)."""
    m = [mult[0], 0, 0, 0, add[0],
         0, mult[1], 0, 0, add[1],
         0, 0, mult[2], 0, add[2],
         0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)


def fog_filter(fog_col, f, mult=(1, 1, 1)):
    """out = in*mult*(1-f) + fog*f"""
    return tint_filter(tuple(m * (1 - f) for m in mult), tuple(c * f for c in fog_col[:3]))


def gray_to_ramp(dark, light):
    """Map a grayscale image (R channel) to a dark->light colour ramp."""
    m = [light[0] - dark[0], 0, 0, 0, dark[0],
         light[1] - dark[1], 0, 0, 0, dark[1],
         light[2] - dark[2], 0, 0, 0, dark[2],
         0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)


# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------
def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth_path(pts, close=True, tension=0.5):
    """Catmull-Rom spline through points -> cubic bezier path."""
    n = len(pts)
    p = skia.Path()
    if n < 3:
        return poly(pts, close)
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else pts[(i + 1) % n]
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def capsule(a, b, wa, wb):
    """Tapered limb from a (width wa) to b (width wb) with round ends."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L, dx / L
    p = skia.Path()
    p.moveTo(ax + nx * wa / 2, ay + ny * wa / 2)
    p.lineTo(bx + nx * wb / 2, by + ny * wb / 2)
    p.lineTo(bx - nx * wb / 2, by - ny * wb / 2)
    p.lineTo(ax - nx * wa / 2, ay - ny * wa / 2)
    p.close()
    p.addCircle(ax, ay, wa / 2)
    p.addCircle(bx, by, wb / 2)
    return p


def text_path(text, font_file, size, x=0, y=0):
    tf = skia.Typeface.MakeFromFile(FONT_DIR + font_file)
    font = skia.Font(tf, size)
    blob = skia.TextBlob.MakeFromString(text, font)
    return font, blob


def text_width(text, font_file, size):
    tf = skia.Typeface.MakeFromFile(FONT_DIR + font_file)
    font = skia.Font(tf, size)
    return font.measureText(text)


def draw_text(canvas, text, x, y, font_file, size, c, align='center', alpha=1.0, blur=None, spacing=0):
    tf = skia.Typeface.MakeFromFile(FONT_DIR + font_file)
    font = skia.Font(tf, size)
    w = font.measureText(text) + spacing * (len(text) - 1)
    if align == 'center':
        x0 = x - w / 2
    elif align == 'right':
        x0 = x - w
    else:
        x0 = x
    p = paint(c, alpha=alpha, blur=blur)
    if spacing:
        cx = x0
        for ch in text:
            canvas.drawString(ch, cx, y, font, p)
            cx += font.measureText(ch) + spacing
    else:
        canvas.drawString(text, x0, y, font, p)
    return w


# --------------------------------------------------------------------------
# camera / projection
# --------------------------------------------------------------------------
class Camera:
    """Simple perspective camera with yaw. focal = px per metre at 1 m."""

    def __init__(self, x=0.0, y=1.5, z=0.0, yaw=0.0, focal=1500.0, horizon=0.5, roll=0.0):
        self.x, self.y, self.z = x, y, z
        self.yaw = yaw          # radians, + turns right
        self.focal = focal
        self.horizon = horizon  # screen fraction of horizon line (tilt)
        self.roll = roll

    def to_cam(self, x, y, z):
        dx, dz = x - self.x, z - self.z
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        rx = dx * c - dz * s
        rz = dx * s + dz * c
        return rx, y - self.y, rz

    def project(self, x, y, z):
        rx, ry, rz = self.to_cam(x, y, z)
        if rz <= 0.05:
            return None
        s = self.focal / rz
        return (W / 2 + rx * s, H * self.horizon - ry * s, s, rz)

    def dir_screen_x(self, wx, wz):
        """Screen-space sign (-1 left, +1 right) of a world direction."""
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        rx = wx * c - wz * s
        return rx


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------
def new_surface(w=W, h=H):
    info = skia.ImageInfo.Make(w, h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
    return skia.Surface.MakeRaster(info)


class VideoWriter:
    def __init__(self, path, fps=FPS, w=W, h=H, crf=17):
        self.proc = subprocess.Popen([
            'ffmpeg', '-y', '-loglevel', 'error',
            '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p',
            '-profile:v', 'high', '-r', str(fps), '-movflags', '+faststart', path],
            stdin=subprocess.PIPE)

    def write(self, surface):
        self.proc.stdin.write(surface.makeImageSnapshot().tobytes())

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def save_png(surface, path):
    surface.makeImageSnapshot().save(path, skia.kPNG)


# --------------------------------------------------------------------------
# post effects shared by every shot (keeps the film look consistent)
# --------------------------------------------------------------------------
_GRAIN = []


def _grain_images():
    if not _GRAIN:
        rng = np.random.default_rng(7)
        for i in range(6):
            g = rng.normal(128, 40, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)
            rgba = np.dstack([g, g, g, np.full_like(g, 255)])
            _GRAIN.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))
    return _GRAIN


def post(canvas, frame, vignette=0.75, grain=0.07, flicker=0.0, lift=(0.0, 0.0, 0.0)):
    # vignette
    if vignette:
        sh = rad_grad((W / 2, H * 0.47), H * 0.72,
                      [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, vignette)], [0, 0.45, 1.0])
        canvas.drawRect(skia.Rect(0, 0, W, H), paint(shader=sh))
    if flicker:
        canvas.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=flicker))
    if any(lift):
        canvas.drawRect(skia.Rect(0, 0, W, H), paint((*lift, 1), blend=skia.BlendMode.kPlus))
    # film grain (overlay blend)
    if grain:
        img = _grain_images()[frame % 6]
        p = skia.Paint()
        p.setBlendMode(skia.BlendMode.kOverlay)
        p.setAlphaf(grain)
        canvas.drawImageRect(img, skia.Rect(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear), p)
