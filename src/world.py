"""Pseudo-3D forest: sprites placed in world (x, z) metres, perspective camera, fog, light rays, particles."""
import math
import random
import skia
from gfx import (W, H, paint, path_poly, path_smooth, ellipse, lin_grad, rad_grad, rgb, mix, lerp, clamp, raster,
                 tint_filter, noise1, fbm, smooth)

# ------------------------------------------------------------------------------------------------
# Palettes (mood keyframes)
# ------------------------------------------------------------------------------------------------
PAL = {
    'day':   dict(sky_top=rgb('#9cc4d6'), sky_bot=rgb('#f2e2b8'), fog=rgb('#bfcdb6'), light=(1.0, 0.98, 0.9), ground=rgb('#4b4a2c'),
                  ground_far=rgb('#7d8562'), trail=rgb('#9a8058'), rays=0.55, fogd=55.0, sat=1.0, sun=rgb('#fff1c4')),
    'tense': dict(sky_top=rgb('#7d97a0'), sky_bot=rgb('#c9c6ad'), fog=rgb('#8e9c92'), light=(0.82, 0.86, 0.86), ground=rgb('#37382a'),
                  ground_far=rgb('#5f6a5a'), trail=rgb('#7a6a50'), rays=0.3, fogd=42.0, sat=0.85, sun=rgb('#f4e6c0')),
    'dark':  dict(sky_top=rgb('#3e4d57'), sky_bot=rgb('#6f7470'), fog=rgb('#4d5a5a'), light=(0.56, 0.62, 0.68), ground=rgb('#202119'),
                  ground_far=rgb('#3b4442'), trail=rgb('#4f463a'), rays=0.12, fogd=30.0, sat=0.7, sun=rgb('#c9c3b0')),
    'relief': dict(sky_top=rgb('#e7a46c'), sky_bot=rgb('#fbe0a8'), fog=rgb('#d9b98f'), light=(1.06, 0.93, 0.8), ground=rgb('#4a3c26'),
                   ground_far=rgb('#9a8058'), trail=rgb('#a07c52'), rays=0.7, fogd=50.0, sat=1.0, sun=rgb('#ffe2a0')),
}


def pal_mix(a, b, t):
    A, B = PAL[a] if isinstance(a, str) else a, PAL[b] if isinstance(b, str) else b
    out = {}
    for k in A:
        if isinstance(A[k], tuple):
            out[k] = mix(A[k], B[k], t)
        else:
            out[k] = lerp(A[k], B[k], t)
    return out


# ------------------------------------------------------------------------------------------------
# Sprites
# ------------------------------------------------------------------------------------------------
SPR = {}
PX_PER_M = 60.0  # sprite raster resolution


def _spruce(seed, h=20.0):
    rng = random.Random(seed)
    w = h * 0.34
    Wpx, Hpx = int(w * PX_PER_M) + 40, int(h * PX_PER_M) + 20
    cx = Wpx / 2
    dark = rgb('#1d3324')
    mid = rgb('#2d4a31')
    lite = rgb('#4f7343')

    def f(c):
        # trunk
        c.drawRect(skia.Rect.MakeLTRB(cx - 0.18 * PX_PER_M, Hpx - h * 0.7 * PX_PER_M, cx + 0.18 * PX_PER_M, Hpx), paint('#3a2a1e'))
        tiers = 16
        base_y = Hpx - 2.4 * PX_PER_M
        top_y = 6
        for i in range(tiers):
            u = i / (tiers - 1)
            y = lerp(base_y, top_y + 30, u ** 0.92)
            half = (w / 2) * (1 - u) ** 0.9 * PX_PER_M * rng.uniform(0.82, 1.08) + 10
            th = (base_y - top_y) / tiers * 1.7
            for side in (-1, 1):
                hs = half * rng.uniform(0.85, 1.1)
                droop = th * 0.35 + hs * 0.12
                tipx, tipy = cx + side * hs, y + droop
                pts = [(cx, y - th)]
                # upper edge: gentle convex curve to tip
                for k in range(1, 6):
                    v = k / 6
                    pts.append((cx + side * hs * v, y - th + (th + droop) * (v ** 1.6)))
                pts.append((tipx, tipy))
                # lower jagged edge back to trunk
                nj = max(3, int(hs / 13))
                for k in range(nj):
                    v = 1 - (k + 0.5) / nj
                    bx = cx + side * hs * v
                    by = y + droop * v + th * 0.08
                    pts.append((bx + side * 4, by + rng.uniform(5, 14)))
                    pts.append((bx - side * 4, by - rng.uniform(0, 5)))
                pts.append((cx, y + 4))
                colr = mix(dark, mid, rng.uniform(0.0, 1.0)) if side > 0 else mix(mid, lite, rng.uniform(0.15, 0.5))
                c.drawPath(path_poly(pts), paint(colr))
                # needle texture
                for k in range(int(hs / 7)):
                    v = rng.random()
                    xx = cx + side * hs * v
                    yy = y - th * (1 - v) * 0.6 + droop * v + rng.uniform(-th * 0.3, th * 0.1)
                    c.drawLine(xx, yy, xx + side * rng.uniform(2, 7), yy + rng.uniform(3, 9),
                               paint(lite if side < 0 else dark, 0.45, stroke=1.8))
    return raster(Wpx, Hpx, f), h


def _pine(seed, h=24.0):
    rng = random.Random(seed)
    w = h * 0.36
    Wpx, Hpx = int(w * PX_PER_M) + 40, int(h * PX_PER_M) + 20
    cx = Wpx / 2

    def f(c):
        # tall orange-brown trunk
        tw = 0.24 * PX_PER_M
        trunk = path_poly([(cx - tw, Hpx), (cx - tw * 0.55, 40), (cx + tw * 0.55, 40), (cx + tw, Hpx)])
        c.drawPath(trunk, paint(shader=lin_grad((cx - tw, 0), (cx + tw, 0), ['#9a5a34', '#c27a48', '#5a3420'], [0, 0.35, 1])))
        for k in range(30):
            y = rng.uniform(Hpx * 0.4, Hpx)
            c.drawLine(cx - tw * 0.6, y, cx + tw * 0.4, y + rng.uniform(-3, 3), paint('#4a2a18', 0.35, stroke=2))
        # crown clumps at top
        for k in range(18):
            u = rng.random()
            yy = lerp(20, Hpx * 0.42, u)
            xx = cx + rng.uniform(-1, 1) * (w / 2) * PX_PER_M * (0.3 + 0.7 * math.sin(u * math.pi))
            r = rng.uniform(0.9, 1.6) * PX_PER_M
            c.drawOval(ellipse(xx, yy, r, r * 0.6), paint('#24402b'))
            c.drawOval(ellipse(xx - r * 0.25, yy - r * 0.2, r * 0.7, r * 0.35), paint('#4a6e40', 0.7))
        # branches
        for k in range(6):
            y = rng.uniform(Hpx * 0.2, Hpx * 0.45)
            s = rng.choice((-1, 1))
            c.drawLine(cx, y, cx + s * rng.uniform(0.8, 1.6) * PX_PER_M, y - 20, paint('#5a3420', stroke=5))
    return raster(Wpx, Hpx, f), h


def _bush(seed, h=1.4):
    rng = random.Random(seed)
    w = h * 2.0
    Wpx, Hpx = int(w * PX_PER_M) + 30, int(h * PX_PER_M) + 20
    cx = Wpx / 2

    def f(c):
        for k in range(26):
            u = rng.random()
            xx = cx + rng.uniform(-1, 1) * (w / 2 - 0.3) * PX_PER_M
            yy = Hpx - rng.uniform(0.25, h * 0.75) * PX_PER_M * (1 - abs(xx - cx) / (w * PX_PER_M) * 0.8)
            r = rng.uniform(0.25, 0.45) * PX_PER_M
            c.drawCircle(xx, yy, r, paint(['#22391f', '#2e4a28', '#3b5a30'][k % 3]))
        for k in range(60):
            xx = cx + rng.uniform(-1, 1) * (w / 2 - 0.2) * PX_PER_M
            yy = Hpx - rng.uniform(0.3, h * 0.8) * PX_PER_M
            c.drawOval(ellipse(xx, yy, 6, 3.5), paint('#5c7f44', 0.6))
    return raster(Wpx, Hpx, f), h


def _fern(seed, h=0.8):
    rng = random.Random(seed)
    w = h * 2.2
    Wpx, Hpx = int(w * PX_PER_M) + 20, int(h * PX_PER_M) + 10
    cx = Wpx / 2

    def f(c):
        for k in range(9):
            a = math.radians(rng.uniform(-75, 75))
            L = rng.uniform(0.6, 1.0) * h * PX_PER_M
            x0, y0 = cx, Hpx
            x1 = x0 + math.sin(a) * L
            y1 = y0 - math.cos(a) * L * 0.9
            colr = ['#3d6a33', '#4d7c3c', '#2f5528'][k % 3]
            c.drawPath(path_smooth([(x0, y0), ((x0 + x1) / 2 + math.sin(a) * 10, (y0 + y1) / 2 - 8), (x1, y1)], close=False), paint(colr, stroke=2.4))
            for j in range(10):
                u = j / 10
                px, py = lerp(x0, x1, u), lerp(y0, y1, u) - math.sin(u * math.pi) * 8
                ll = (1 - u) * 12 + 3
                c.drawLine(px, py, px - math.cos(a) * ll, py - math.sin(a) * ll - 4, paint(colr, stroke=3))
                c.drawLine(px, py, px + math.cos(a) * ll, py + math.sin(a) * ll - 4, paint(colr, stroke=3))
    return raster(Wpx, Hpx, f), h


def _rock(seed, h=0.5):
    rng = random.Random(seed)
    w = h * 2.2
    Wpx, Hpx = int(w * PX_PER_M) + 10, int(h * PX_PER_M) + 6
    cx = Wpx / 2

    def f(c):
        pts = [(cx - w / 2 * PX_PER_M, Hpx), (cx - w * 0.4 * PX_PER_M, Hpx * 0.4), (cx - 0.05 * PX_PER_M, 4), (cx + w * 0.35 * PX_PER_M, Hpx * 0.3), (cx + w / 2 * PX_PER_M, Hpx)]
        p = path_smooth(pts, tension=0.4)
        c.drawPath(p, paint(shader=lin_grad((0, 0), (0, Hpx), ['#8c8a80', '#55544c'])))
        c.drawPath(path_smooth([(cx - w * 0.3 * PX_PER_M, Hpx * 0.3), (cx, 8), (cx + w * 0.3 * PX_PER_M, Hpx * 0.35)], close=False), paint('#4b6a3a', 0.6, stroke=6))
    return raster(Wpx, Hpx, f), h


def _grass(seed, h=0.35):
    rng = random.Random(seed)
    Wpx, Hpx = int(0.7 * PX_PER_M), int(h * PX_PER_M) + 4
    cx = Wpx / 2

    def f(c):
        for k in range(12):
            x0 = cx + rng.uniform(-8, 8)
            x1 = x0 + rng.uniform(-14, 14)
            c.drawPath(path_smooth([(x0, Hpx), ((x0 + x1) / 2, Hpx * 0.5), (x1, rng.uniform(2, Hpx * 0.4))], close=False),
                       paint(['#5d7a3a', '#7c8f45', '#47622e'][k % 3], stroke=2))
    return raster(Wpx, Hpx, f), h


def _leaves(seed):
    rng = random.Random(seed)
    Wpx, Hpx = 120, 30

    def f(c):
        for k in range(14):
            x = rng.uniform(8, Wpx - 8)
            y = rng.uniform(8, Hpx - 4)
            c.drawOval(ellipse(x, y, rng.uniform(4, 7), rng.uniform(1.6, 3)), paint(['#8a5a2a', '#a8742e', '#6b4a24', '#5a5a2a'][k % 4], 0.9))
        for k in range(4):
            x = rng.uniform(5, Wpx - 30)
            y = rng.uniform(8, Hpx - 4)
            c.drawLine(x, y, x + rng.uniform(15, 30), y + rng.uniform(-4, 4), paint('#5a4028', stroke=2))
    return raster(Wpx, Hpx, f), 0.25


def _treeline(seed, kind='spruce'):
    """Horizontal strip of distant tree silhouettes; 400 m wide, base at bottom. 10 px per m."""
    rng = random.Random(seed)
    Wpx, Hpx = 4000, 330

    def f(c):
        x = 0
        while x < Wpx:
            hh = rng.uniform(17, 31) * 10
            ww = hh * rng.uniform(0.32, 0.42)
            pts = [(x - ww / 2, Hpx)]
            tiers = 6
            for i in range(tiers):
                u = i / tiers
                yy = Hpx - hh * (0.15 + 0.85 * u)
                hw = ww / 2 * (1 - u)
                pts.insert(0, (x - hw, yy))
                pts.append((x + hw * 0.6, yy - 6))
            pts = [(x - ww / 2, Hpx)] + [(x - ww / 2 * (1 - i / tiers) - 3, Hpx - hh * (0.12 + 0.88 * i / tiers)) for i in range(tiers)] + \
                  [(x, Hpx - hh)] + [(x + ww / 2 * (1 - i / tiers) + 3, Hpx - hh * (0.12 + 0.88 * i / tiers)) for i in reversed(range(tiers))] + [(x + ww / 2, Hpx)]
            c.drawPath(path_poly(pts), paint('#1f3326'))
            x += ww * rng.uniform(0.35, 0.6)
        c.drawRect(skia.Rect.MakeLTRB(0, Hpx - 30, Wpx, Hpx), paint('#1f3326'))
    return raster(Wpx, Hpx, f)


def _mountains(seed):
    rng = random.Random(seed)
    Wpx, Hpx = 3000, 600

    def f(c):
        for layer, (colr, amp, base) in enumerate([('#8aa1ae', 380, 600), ('#6f8796', 260, 600)]):
            pts = [(0, Hpx)]
            for i in range(61):
                x = i / 60 * Wpx
                y = base - amp * (0.5 + 0.5 * fbm(i / 7 + layer * 10, seed + layer, 4)) - 40
                pts.append((x, y))
            pts.append((Wpx, Hpx))
            c.drawPath(path_poly(pts), paint(colr))
            # snow-ish highlights on far layer
    return raster(Wpx, Hpx, f)


def _fogblob(seed):
    def f(c):
        rng = random.Random(seed)
        for k in range(10):
            c.drawOval(ellipse(rng.uniform(200, 600), rng.uniform(80, 120), rng.uniform(100, 220), rng.uniform(30, 55)), paint('#ffffff', 0.18, blur=30))
    return raster(800, 200, f)


def init_sprites():
    if SPR:
        return
    SPR['spruce'] = [_spruce(s, h) for s, h in ((1, 20), (2, 23), (3, 17), (4, 26))]
    SPR['pine'] = [_pine(s, h) for s, h in ((5, 24), (6, 27))]
    SPR['bush'] = [_bush(s, h) for s, h in ((7, 1.3), (8, 1.7), (9, 1.0))]
    SPR['fern'] = [_fern(s, h) for s, h in ((10, 0.8), (11, 0.65), (12, 0.9))]
    SPR['rock'] = [_rock(s, h) for s, h in ((13, 0.5), (14, 0.8))]
    SPR['grass'] = [_grass(s) for s in (15, 16, 17)]
    SPR['leaves'] = [_leaves(s) for s in (18, 19, 20)]
    SPR['treeline'] = [_treeline(s) for s in (21, 22, 23)]
    SPR['mount'] = _mountains(24)
    SPR['fog'] = [_fogblob(s) for s in (25, 26)]


# ------------------------------------------------------------------------------------------------
# Trail & tree field
# ------------------------------------------------------------------------------------------------
def trail_x(z):
    return 2.2 * math.sin(z / 21.0) + 1.0 * math.sin(z / 8.3 + 1.3)


TRAIL_W = 1.5


def _h(ix, iz, k=0):
    n = (ix * 73856093) ^ (iz * 19349663) ^ (k * 83492791)
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffffff) / 0xffffff


CELL = 3.4


def objects_in_view(cam, zfar=62.0):
    out = []
    z0 = cam.z + 0.6
    iz0, iz1 = int(math.floor(z0 / CELL)), int(math.floor((cam.z + zfar) / CELL))
    tanh = (W / 2) / cam.f + 0.05
    for iz in range(iz0, iz1 + 1):
        zc = iz * CELL
        dz = max(zc - cam.z, 1.0)
        half = dz * tanh + 7
        ix0, ix1 = int(math.floor((cam.x - half) / CELL)), int(math.floor((cam.x + half) / CELL))
        for ix in range(ix0, ix1 + 1):
            r = _h(ix, iz)
            x = (ix + _h(ix, iz, 1)) * CELL
            z = (iz + _h(ix, iz, 2)) * CELL
            if z <= cam.z + 0.5:
                continue
            d = abs(x - trail_x(z))
            if d < TRAIL_W / 2 + 0.2:
                continue
            if d > 4.4:
                if r < 0.62:
                    k = _h(ix, iz, 3)
                    kind = 'pine' if k < 0.3 else 'spruce'
                    v = SPR[kind][int(_h(ix, iz, 4) * len(SPR[kind]))]
                    out.append((z, x, kind, v, 1.0 + 0.2 * _h(ix, iz, 5), _h(ix, iz, 6) < 0.5))
                elif r < 0.8:
                    v = SPR['bush'][int(_h(ix, iz, 4) * 3)]
                    out.append((z, x, 'bush', v, 1.0, _h(ix, iz, 6) < 0.5))
            # undergrowth near trail and ground detail
            for k in range(3 if dz < 25 else 1):
                rr = _h(ix, iz, 10 + k)
                gx = (ix + _h(ix, iz, 20 + k)) * CELL
                gz = (iz + _h(ix, iz, 30 + k)) * CELL
                if gz <= cam.z + 0.4:
                    continue
                gd = abs(gx - trail_x(gz))
                if gd < TRAIL_W / 2:
                    if dz < 20 and rr < 0.5:
                        out.append((gz, gx, 'leaves', SPR['leaves'][k % 3], 1.0, rr < 0.25))
                    continue
                if rr < 0.35:
                    out.append((gz, gx, 'fern', SPR['fern'][int(_h(ix, iz, 40 + k) * 3)], 1.0, rr < 0.17))
                elif rr < 0.55:
                    out.append((gz, gx, 'grass', SPR['grass'][k % 3], 1.0, False))
                elif rr < 0.62:
                    out.append((gz, gx, 'rock', SPR['rock'][k % 2], 1.0, rr < 0.6))
                elif rr < 0.85 and dz < 22:
                    out.append((gz, gx, 'leaves', SPR['leaves'][k % 3], 1.0, False))
    return out


# ------------------------------------------------------------------------------------------------
# Camera & renderer
# ------------------------------------------------------------------------------------------------
class Cam:
    def __init__(self, x=0.0, y=1.7, z=0.0, f=1150.0, hy=None, roll=0.0, sx=0.0, sy=0.0):
        self.x, self.y, self.z, self.f = x, y, z, f
        self.hy = H * 0.45 if hy is None else hy
        self.roll = roll
        self.sx, self.sy = sx, sy  # screen shake offsets

    def proj(self, x, y, z):
        dz = z - self.z
        if dz < 0.05:
            dz = 0.05
        s = self.f / dz
        return (W / 2 + (x - self.x) * s, self.hy + (self.y - y) * s, s)


def fog_amount(dz, pal):
    return clamp(1 - math.exp(-dz / pal['fogd'] * 1.25)) * 0.95


def draw_sky(c, cam, pal, t):
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=lin_grad((0, cam.hy - 1400), (0, cam.hy + 40), [pal['sky_top'], pal['sky_bot']])))
    # sun glow upper left
    sx, sy = W * 0.18, cam.hy - 700
    c.drawCircle(sx, sy, 520, paint(shader=rad_grad((sx, sy), 520, [(*pal['sun'], 0.8), (*pal['sun'], 0.0)])))


def draw_backdrop(c, cam, pal, t, mountains=False):
    if mountains:
        img = SPR['mount']
        D = 2500.0
        s = cam.f / D * 2.2
        off = (cam.x * s) % img.width()
        y = cam.hy + (cam.y - 0) * cam.f / D - img.height() * 1.0 + 30
        p = skia.Paint(AntiAlias=True)
        p.setColorFilter(tint_filter(pal['light'], pal['fog'], 0.35, pal['sat']))
        for k in range(-1, 2):
            c.drawImageRect(img, skia.Rect.MakeXYWH(-off + k * img.width() - 300, y, img.width(), img.height()), skia.SamplingOptions(skia.FilterMode.kLinear), p)
    for i, D in enumerate((140.0, 95.0, 68.0)):
        img = SPR['treeline'][i]
        s = cam.f / D / 10.0  # px per sprite px
        wpx = img.width() * s
        hpx = img.height() * s
        base_y = cam.hy + cam.y * cam.f / D
        off = ((cam.x + 37 * i) * cam.f / D) % wpx
        p = skia.Paint(AntiAlias=True)
        p.setColorFilter(tint_filter(pal['light'], pal['fog'], fog_amount(D, pal) * (0.95 - i * 0.08), pal['sat']))
        k0 = -1
        x = -off + k0 * wpx + W / 2
        while x < W + wpx:
            c.drawImageRect(img, skia.Rect.MakeXYWH(x, base_y - hpx, wpx, hpx), skia.SamplingOptions(skia.FilterMode.kLinear), p)
            x += wpx
        # fill below treeline with ground-far colour to horizon
    # haze band
    c.drawRect(skia.Rect.MakeLTRB(0, cam.hy - 260, W, cam.hy + 160),
               paint(shader=lin_grad((0, cam.hy - 260), (0, cam.hy + 160), [(*pal['fog'], 0.0), (*pal['fog'], 0.55), (*pal['fog'], 0.0)])))


def draw_ground(c, cam, pal, t):
    top = cam.hy + cam.y * cam.f / 140.0
    c.drawRect(skia.Rect.MakeLTRB(0, top, W, H + 400),
               paint(shader=lin_grad((0, top), (0, H), [mix(pal['ground_far'], pal['fog'], 0.5), pal['ground_far'], pal['ground']], [0, 0.12, 0.6])))
    # dappled light patches
    for k in range(10):
        gz = cam.z + 3 + ((k * 7.3 + 1) % 30)
        gx = trail_x(gz) + math.sin(k * 3.1) * 4
        X, Y, s = cam.proj(gx, 0, gz)
        if Y > H + 50:
            continue
        r = 1.6 * s
        c.drawOval(ellipse(X, Y, r * 1.6, r * 0.32), paint((*pal['sun'],), 0.10 * pal['rays'] * 2, blur=max(1, r * 0.2)))
    # trail polygon
    left, right = [], []
    zs = []
    z = cam.z + 0.3
    while z < cam.z + 120:
        zs.append(z)
        z += 0.25 if z < cam.z + 4 else (0.8 if z < cam.z + 20 else 3.0)
    for z in zs:
        tx = trail_x(z)
        w = TRAIL_W / 2 * (1 + 0.15 * math.sin(z * 0.7))
        l = cam.proj(tx - w, 0, z)
        r = cam.proj(tx + w, 0, z)
        left.append((l[0], l[1]))
        right.append((r[0], r[1]))
    pts = left + right[::-1]
    p = path_poly(pts)
    c.drawPath(p, paint(shader=lin_grad((0, cam.hy), (0, H), [mix(pal['trail'], pal['fog'], 0.6), pal['trail'], mix(pal['trail'], pal['ground'], 0.25)], [0, 0.15, 1])))
    # trail edges darker (soft)
    c.drawPath(path_poly(left, close=False), paint(pal['ground'], 0.5, stroke=6, blur=3))
    c.drawPath(path_poly(right, close=False), paint(pal['ground'], 0.5, stroke=6, blur=3))


def draw_sprite(c, cam, pal, z, x, img_h, scale=1.0, flip=False, extra_fog=0.0, sway=0.0):
    img, h = img_h
    X, Y, s = cam.proj(x, 0, z)
    hpx = h * scale * s
    wpx = img.width() / img.height() * hpx
    if X + wpx / 2 < -50 or X - wpx / 2 > W + 50 or Y - hpx > H + 50 or Y < -100 - 0:
        if Y < -100:
            return
        if X + wpx / 2 < -50 or X - wpx / 2 > W + 50:
            return
    dz = z - cam.z
    p = skia.Paint(AntiAlias=True)
    p.setColorFilter(tint_filter(pal['light'], pal['fog'], clamp(fog_amount(dz, pal) + extra_fog), pal['sat']))
    c.save()
    c.translate(X, Y)
    if sway:
        c.skew(sway, 0)
    if flip:
        c.scale(-1, 1)
    c.drawImageRect(img, skia.Rect.MakeXYWH(-wpx / 2, -hpx, wpx, hpx), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear) if False else skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()


def draw_rays(c, cam, pal, t, strength=1.0):
    a = pal['rays'] * strength
    if a <= 0.01:
        return
    sx, sy = W * 0.05, cam.hy - 1500
    for k in range(7):
        ang = math.radians(62 + k * 7.5 + 2 * math.sin(t * 0.13 + k))
        L = 3600
        wdt = 0.035 + 0.02 * math.sin(k * 2.1)
        x1 = sx + math.cos(ang - wdt) * L
        y1 = sy + math.sin(ang - wdt) * L
        x2 = sx + math.cos(ang + wdt) * L
        y2 = sy + math.sin(ang + wdt) * L
        al = a * (0.10 + 0.08 * (0.5 + 0.5 * math.sin(t * 0.4 + k * 1.7)))
        p = path_poly([(sx, sy), (x1, y1), (x2, y2)])
        c.drawPath(p, paint(shader=lin_grad((sx, sy), (sx + math.cos(ang) * L * 0.75, sy + math.sin(ang) * L * 0.75),
                                            [(*pal['sun'], al), (*pal['sun'], al * 0.6), (*pal['sun'], 0.0)]),
                            blend=skia.BlendMode.kScreen, blur=18))


def draw_fog_layer(c, cam, pal, t, amount=1.0, y_off=0.0):
    if amount <= 0:
        return
    for k, D in enumerate((40.0, 22.0, 12.0)):
        img = SPR['fog'][k % 2]
        s = cam.f / D
        wpx = 26 * s
        hpx = wpx / 4
        Y = cam.hy + (cam.y - 0.6) * s - hpx * 0.55 + y_off
        drift = (t * (0.6 + k * 0.3) + cam.x) * s * 0.4
        off = drift % wpx
        p = skia.Paint(AntiAlias=True)
        p.setColorFilter(tint_filter((1, 1, 1), pal['fog'], 1.0))
        p.setAlphaf(clamp(amount * (0.85 - k * 0.2)))
        x = -off - wpx
        while x < W + wpx:
            c.drawImageRect(img, skia.Rect.MakeXYWH(x, Y, wpx, hpx), skia.SamplingOptions(skia.FilterMode.kLinear), p)
            x += wpx


def draw_particles(c, cam, pal, t, n=40, leaves=8, seed=3, wind=1.0):
    rng = random.Random(seed)
    for i in range(n):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        sp = rng.uniform(4, 14)
        x = (x0 + t * sp * wind + 20 * math.sin(t * 0.5 + i)) % W
        y = (y0 + t * sp * 0.5 + 15 * math.sin(t * 0.3 + i * 1.7)) % H
        r = rng.uniform(1.2, 3.2)
        a = (0.25 + 0.25 * math.sin(t * 1.3 + i)) * (0.4 + pal['rays'])
        c.drawCircle(x, y, r, paint(pal['sun'], a, blur=1.2))
    for i in range(leaves):
        x0, y0 = rng.uniform(0, W), rng.uniform(-H, 0)
        fall = rng.uniform(60, 120)
        y = (y0 + t * fall) % (H + 200) - 100
        x = x0 + 60 * math.sin(t * 1.1 + i * 2) + t * 25 * wind
        x = x % (W + 100) - 50
        ang = math.sin(t * 2.3 + i) * 70
        c.save()
        c.translate(x, y)
        c.rotate(ang)
        sc = rng.uniform(0.8, 1.6)
        c.drawOval(ellipse(0, 0, 9 * sc, 4 * sc), paint(['#a8742e', '#8a5a2a', '#c09040'][i % 3], 0.9))
        c.restore()


def render_world(c, cam, pal, t, actors=(), rays=1.0, fog=1.0, particles=True, mountains=False, zfar=62.0, wind=1.0, leaves=6):
    """actors: list of (z, draw_fn(c, cam, pal)) inserted in depth order."""
    init_sprites()
    c.save()
    c.translate(cam.sx, cam.sy)
    if cam.roll:
        c.rotate(cam.roll, W / 2, H / 2)
    draw_sky(c, cam, pal, t)
    draw_backdrop(c, cam, pal, t, mountains=mountains)
    draw_ground(c, cam, pal, t)
    draw_fog_layer(c, cam, pal, t, amount=fog * 0.6)
    objs = objects_in_view(cam, zfar)
    items = [(o[0], 0, o) for o in objs] + [(a[0], 1, a) for a in actors]
    items.sort(key=lambda it: -it[0])
    for z, kind, o in items:
        if kind == 0:
            _, x, typ, spr, sc, flip = o
            sway = 0.0
            if typ in ('spruce', 'pine'):
                sway = 0.006 * math.sin(t * 0.8 + x) * wind
            elif typ in ('fern', 'grass', 'bush'):
                sway = 0.05 * math.sin(t * 1.7 + x * 3) * wind
            draw_sprite(c, cam, pal, z, x, spr, sc, flip, sway=sway)
        else:
            o[1](c, cam, pal)
    draw_rays(c, cam, pal, t, rays)
    if particles:
        draw_particles(c, cam, pal, t, leaves=leaves, wind=wind)
    c.restore()


def actor_tint_layer(c, cam, pal, z, bounds, fn, extra_fog=0.0, darken=0.0):
    """Draw an actor with fog/light tint applied via a layer limited to bounds."""
    dz = z - cam.z
    p = skia.Paint()
    f = clamp(fog_amount(dz, pal) * 0.85 + extra_fog)
    light = tuple(l * (1 - darken) for l in pal['light'])
    p.setColorFilter(tint_filter(light, pal['fog'], f, pal['sat']))
    c.saveLayer(bounds, p)
    fn(c)
    c.restore()
