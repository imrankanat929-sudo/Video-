"""DIDAO engine - the ONE forest used by every scene ("Blackpine Hollow").

Layout (world metres, see CONTINUITY_BIBLE/forest_reference):
  * clearing centre CLEARING (0, 0, 20), radius 6.5
  * tent at TENT_POS, opening faces the fire / -z
  * campfire at FIRE_POS
  * the path enters the clearing from the south (-z) and winds away
  * the moon hangs to the north-west: upper-left of frame when looking +z
  * the old carved pine (CARVED_TREE) stands where the path used to meet the clearing
Every tree position is generated from a fixed seed, so the forest never changes.
"""
import math
import random

import numpy as np
import skia

from .core import (W, H, Camera, clamp, col, fog_filter, gray_to_ramp, hexc, lerp, lin_grad,
                   mix, paint, poly, rad_grad, smooth_path, vnoise, fbm, sk)

CLEARING = (0.0, 20.0)
CLEARING_R = 6.5
TENT_POS = (-2.3, 0.0, 22.2)
FIRE_POS = (0.9, 0.0, 19.2)
CARVED_TREE = (2.3, 0.0, 13.2)
MOON_DIR = (-0.50, 0.42, 1.0)  # direction to the moon (x, elevation, z)


def path_x(z):
    """Centre line of the forest path (south of the clearing)."""
    return 0.35 * math.sin(z / 7.0) + (13.5 - z) * 0.06 - 0.3


PATH_W = 1.5

# --------------------------------------------------------------------------
# palettes (time of day). Warm orange appears ONLY from the fire.
# --------------------------------------------------------------------------
PALETTES = {
    'night': dict(sky_top=hexc('#03060d'), sky_mid=hexc('#0b1322'), sky_hor=hexc('#1a2536'),
                  fog=hexc('#18222f'), fog_dist=24.0, tree_dark=hexc('#05070b'), tree_light=hexc('#5d7290'),
                  ground_near=hexc('#07090b'), ground_far=hexc('#151d27'), clearing=hexc('#1a1f22'),
                  path=hexc('#1e2224'), moon=1.0, amb=(0.40, 0.47, 0.62), rim=hexc('#9fb6dc'),
                  grass=hexc('#11171a')),
    'dusk': dict(sky_top=hexc('#0a1222'), sky_mid=hexc('#1c2a40'), sky_hor=hexc('#3c4a5c'),
                 fog=hexc('#2a3646'), fog_dist=22.0, tree_dark=hexc('#070a0f'), tree_light=hexc('#62758c'),
                 ground_near=hexc('#0b0e10'), ground_far=hexc('#222c38'), clearing=hexc('#262b2c'),
                 path=hexc('#2c2f30'), moon=0.6, amb=(0.52, 0.58, 0.70), rim=hexc('#a9bad3'),
                 grass=hexc('#161e1e')),
    'morning': dict(sky_top=hexc('#5d686e'), sky_mid=hexc('#8a9493'), sky_hor=hexc('#a9b2ae'),
                    fog=hexc('#8c9894'), fog_dist=15.0, tree_dark=hexc('#0b100f'), tree_light=hexc('#5f6f66'),
                    ground_near=hexc('#1b211d'), ground_far=hexc('#77847f'), clearing=hexc('#3a3f37'),
                    path=hexc('#454741'), moon=0.0, amb=(0.80, 0.85, 0.86), rim=hexc('#c9d3d2'),
                    grass=hexc('#26302a')),
}


# --------------------------------------------------------------------------
# tree generation
# --------------------------------------------------------------------------
def _bake_pine(seed, w=720, h=2400):
    """Draw one pine variant in grayscale (0 dark .. 1 moon-lit rim, light from LEFT)."""
    rng = random.Random(seed)
    surf = skia.Surface.MakeRaster(skia.ImageInfo.Make(w, h, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType))
    c = surf.getCanvas()
    c.clear(skia.Color4f(0, 0, 0, 0))
    cx = w / 2
    bare = rng.uniform(0.30, 0.50)          # fraction of trunk without branches
    trunk_w = rng.uniform(26, 44)
    lean = rng.uniform(-14, 14)
    g = lambda v: (v, v, v, 1)

    def trunk_x(y):
        return cx + lean * (1 - y / h)

    # foliage tiers
    fol = skia.Path()
    top = rng.uniform(0.0, 0.04) * h
    tiers = rng.randint(9, 13)
    crown_bottom = h * (1 - bare)
    maxw = rng.uniform(0.34, 0.46) * w
    for i in range(tiers):
        u = i / (tiers - 1)
        y = lerp(top + 40, crown_bottom, u ** 0.92)
        half = lerp(18, maxw, u ** 0.8) * rng.uniform(0.75, 1.1)
        if rng.random() < 0.15 and u > 0.4:
            half *= 0.55  # broken / sparse tier
        tx = trunk_x(y)
        droop = lerp(20, 90, u) * rng.uniform(0.8, 1.3)
        tier_h = lerp(70, 210, u)
        n = 9
        sides = {}
        for side in (-1, 1):
            sp = []
            for k in range(1, n + 1):
                v = k / n
                px = tx + side * half * v * rng.uniform(0.85, 1.15)
                py = y - tier_h * (1 - v) * 0.6 + droop * v * v + rng.uniform(-14, 14)
                sp.append((tx + side * half * (v - 0.5 / n), py - rng.uniform(10, 34)))
                sp.append((px, py))
            sides[side] = sp
        tier = sides[-1][::-1] + [(tx, y - tier_h)] + sides[1] + [(tx, y + 18)]
        fol.addPath(poly(tier))
    # trunk
    tr = skia.Path()
    tr.moveTo(trunk_x(top + 60) - 4, top + 60)
    tr.lineTo(trunk_x(top + 60) + 4, top + 60)
    tr.lineTo(trunk_x(h) + trunk_w / 2 + 6, h)
    tr.lineTo(trunk_x(h) - trunk_w / 2 - 6, h)
    tr.close()
    # root flare
    tr.addOval(skia.Rect(trunk_x(h) - trunk_w * 0.95, h - 22, trunk_x(h) + trunk_w * 0.95, h + 14))
    # dead branch stubs on the bare trunk
    stubs = skia.Path()
    for k in range(rng.randint(3, 8)):
        y = rng.uniform(crown_bottom, h - 120)
        side = rng.choice((-1, 1))
        L = rng.uniform(30, 130)
        tx = trunk_x(y)
        ang = rng.uniform(-0.5, 0.2)
        ex, ey = tx + side * L, y + L * ang
        stubs.moveTo(tx, y - 3)
        stubs.lineTo(ex, ey)
        stubs.lineTo(tx, y + 6)
        stubs.close()
        if rng.random() < 0.5:  # twig
            stubs.moveTo(ex - side * L * 0.4, ey - L * ang * 0.4)
            stubs.lineTo(ex - side * L * 0.1, ey - 30)
            stubs.lineTo(ex - side * L * 0.35, ey - L * ang * 0.4 + 4)
            stubs.close()
    sil = skia.Path()
    sil.addPath(fol)
    sil.addPath(tr)
    sil.addPath(stubs)
    c.drawPath(sil, paint(g(0.10)))
    c.drawPath(tr, paint(g(0.16)))
    # bark fissures
    for k in range(int(trunk_w / 5)):
        x0 = rng.uniform(-trunk_w / 2, trunk_w / 2)
        y0 = rng.uniform(crown_bottom - 200, h - 40)
        c.drawLine(trunk_x(y0) + x0, y0, trunk_x(y0 + 160) + x0 * 1.05, y0 + rng.uniform(80, 260),
                   paint(g(0.05), stroke=2.2))
    # moon rim (left edges): silhouette minus shifted silhouette
    c.saveLayer()
    c.drawPath(sil, paint(g(0.62)))
    c.save()
    c.translate(7, 3)
    c.drawPath(sil, paint(g(1.0), blend=skia.BlendMode.kDstOut))
    c.restore()
    c.restore()
    # soft inner light on lit side of foliage
    c.saveLayer(None, paint((1, 1, 1), alpha=0.35, blend=skia.BlendMode.kSrcATop))
    c.drawRect(skia.Rect(0, 0, w, h), paint(shader=lin_grad((cx - maxw, 0), (cx + maxw * 0.2, 0),
                                                              [g(0.55), g(0.0)])))
    c.restore()
    img = surf.makeImageSnapshot().withDefaultMipmaps()
    return img


_TREE_IMGS = []
N_VARIANTS = 10


def tree_images():
    if not _TREE_IMGS:
        for i in range(N_VARIANTS):
            _TREE_IMGS.append(_bake_pine(100 + i))
    return _TREE_IMGS


_TREES = []


def forest_trees():
    """Deterministic forest: list of (x, z, height, variant, flip)."""
    if _TREES:
        return _TREES
    rng = random.Random(2024)
    pts = []
    cell = 2.4
    grid = {}
    for _ in range(9000):
        x = rng.uniform(-70, 70)
        z = rng.uniform(-45, 100)
        dc = math.hypot(x - CLEARING[0], z - CLEARING[1])
        if dc < CLEARING_R + 0.6:
            continue
        if dc < CLEARING_R + 2.2 and rng.random() < 0.5:
            continue
        if z < 15 and abs(x - path_x(z)) < PATH_W * 0.5 + 0.9:
            continue
        gx, gz = int(x // cell), int(z // cell)
        ok = True
        for ix in (gx - 1, gx, gx + 1):
            for iz in (gz - 1, gz, gz + 1):
                for (px, pz) in grid.get((ix, iz), []):
                    if (px - x) ** 2 + (pz - z) ** 2 < 2.3 ** 2:
                        ok = False
        if not ok:
            continue
        grid.setdefault((gx, gz), []).append((x, z))
        pts.append((x, z, rng.uniform(17, 27), rng.randrange(N_VARIANTS), rng.random() < 0.5))
    _TREES.extend(pts)
    return _TREES


def overgrowth_trees():
    """Trees that appear ON the path in the morning (the path is gone)."""
    rng = random.Random(77)
    out = []
    z = 12.6
    while z > -40:
        x = path_x(z) + rng.uniform(-0.7, 0.7)
        if math.hypot(x - CARVED_TREE[0], z - CARVED_TREE[2]) > 2.0:
            out.append((x, z, rng.uniform(17, 26), rng.randrange(N_VARIANTS), rng.random() < 0.5))
        z -= rng.uniform(1.9, 3.0)
    return out


# --------------------------------------------------------------------------
# fog textures
# --------------------------------------------------------------------------
_FOG = []


def fog_texture():
    if not _FOG:
        rng = np.random.default_rng(3)
        w, h = 512, 128
        small = rng.random((8, 32))
        from PIL import Image, ImageFilter
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        im = im.filter(ImageFilter.GaussianBlur(10))
        a = np.asarray(im).astype(np.float32) / 255
        yy = np.linspace(0, 1, h)[:, None]
        env = np.sin(np.pi * yy) ** 1.5
        a = np.clip((a - 0.25) * 1.6, 0, 1) * env
        # make horizontally tileable
        a = 0.5 * (a + a[:, ::-1])
        rgba = np.dstack([np.full((h, w), 255, np.uint8)] * 3 + [(a * 255).astype(np.uint8)])
        img = skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)
        _FOG.append(img)
    return _FOG[0]


# --------------------------------------------------------------------------
# scene drawing
# --------------------------------------------------------------------------
class Scene:
    """Collects depth-sorted drawables and paints the whole forest view."""

    def __init__(self, cam, tod='night', t=0.0, overgrown=False, fog_mult=1.0, moon=True,
                 fire_light=0.0, extra_trees=(), hide_trees_near=None):
        self.cam = cam
        if isinstance(tod, tuple):
            a, b, u = tod
            pa, pb = PALETTES[a], PALETTES[b]
            self.pal = {k: (tuple(lerp(x, y, u) for x, y in zip(pa[k], pb[k])) if isinstance(pa[k], tuple)
                            else lerp(pa[k], pb[k], u)) for k in pa}
            tod = a if u < 0.5 else b
        else:
            self.pal = PALETTES[tod]
        self.tod = tod
        self.t = t
        self.items = []  # (depth, fn)
        self.overgrown = overgrown
        self.fog_mult = fog_mult
        self.moon = moon
        self.fire_light = fire_light
        self.extra_trees = list(extra_trees)
        self.hide_trees_near = hide_trees_near or []

    # ---- helpers -------------------------------------------------------
    def fog_amount(self, d):
        return clamp(1 - math.exp(-d * self.fog_mult / self.pal['fog_dist'])) * 0.97

    def light_side(self):
        """-1 if moonlight comes from screen-left, +1 from right."""
        rx = self.cam.dir_screen_x(MOON_DIR[0], MOON_DIR[2])
        return -1 if rx < 0 else 1

    def add(self, x, y, z, fn, bias=0.0):
        pr = self.cam.project(x, y, z)
        if pr is None:
            return
        self.items.append((pr[3] + bias, lambda c, pr=pr: fn(c, pr)))

    def add_raw(self, depth, fn):
        self.items.append((depth, fn))

    # ---- sky -------------------------------------------------------------
    def draw_sky(self, c):
        p = self.pal
        hz = H * self.cam.horizon
        sh = lin_grad((0, hz - H * 0.9), (0, hz + 10), [p['sky_top'], p['sky_mid'], p['sky_hor']], [0, 0.55, 1])
        c.drawRect(skia.Rect(0, 0, W, H), paint(shader=sh))
        if self.moon and p['moon'] > 0:
            mp = self.cam.project(MOON_DIR[0] * 1000 + self.cam.x, MOON_DIR[1] * 1000 + self.cam.y,
                                  MOON_DIR[2] * 1000 + self.cam.z)
            if mp:
                mx, my = mp[0], mp[1]
                k = p['moon']
                c.drawCircle(mx, my, 520, paint(shader=rad_grad((mx, my), 520, [(0.45, 0.55, 0.75, 0.30 * k), (0.2, 0.3, 0.45, 0.0)])))
                c.drawCircle(mx, my, 150, paint(shader=rad_grad((mx, my), 150, [(0.85, 0.9, 1, 0.55 * k), (0.6, 0.7, 0.9, 0.0)])))
                c.drawCircle(mx, my, 46, paint((0.88, 0.92, 0.98), alpha=0.97 * k))
                # maria
                for (ox, oy, r, a) in ((-12, -8, 14, 0.10), (10, 6, 10, 0.08), (-4, 16, 8, 0.07), (14, -14, 6, 0.06)):
                    c.drawCircle(mx + ox, my + oy, r, paint((0.45, 0.5, 0.6), alpha=a * k, blur=3))
                # thin cloud band over the moon
                for i in range(3):
                    yy = my + 30 + i * 34 + 10 * math.sin(self.t * 0.2 + i)
                    xx = mx - 300 + (self.t * 6 + i * 90) % 120
                    c.drawOval(skia.Rect(xx, yy - 10, xx + 620, yy + 12), paint(p['sky_mid'], alpha=0.55, blur=14))

    # ---- ground -----------------------------------------------------------
    def ground_y(self, d):
        return H * self.cam.horizon + self.cam.y * self.cam.focal / d

    def draw_ground(self, c):
        p = self.pal
        hz = H * self.cam.horizon
        stops, cols = [], []
        for d in (120, 60, 30, 18, 10, 6, 3.5, 2.0, 1.2):
            y = self.ground_y(d)
            stops.append(y)
            cols.append(mix(p['ground_near'], p['fog'], self.fog_amount(d)))
        y0 = hz
        rect = skia.Rect(0, y0, W, H)
        pos = [clamp((y - y0) / max(H - y0, 1)) for y in stops]
        sh = lin_grad((0, y0), (0, H), cols, pos)
        c.drawRect(rect, paint(shader=sh))
        # clearing (ellipse on ground)
        self._ground_poly(c, [(CLEARING[0] + CLEARING_R * math.cos(a) * (1 + 0.08 * vnoise(a * 3, 4)),
                               CLEARING[1] + CLEARING_R * math.sin(a) * (1 + 0.08 * vnoise(a * 3, 9)))
                              for a in np.linspace(0, 2 * math.pi, 64, endpoint=False)], p['clearing'], 0.85, blur=18)
        if not self.overgrown:
            left = [(path_x(z) - PATH_W / 2 * (1 + 0.15 * vnoise(z, 2)), z) for z in np.arange(14.5, -40, -0.8)]
            right = [(path_x(z) + PATH_W / 2 * (1 + 0.15 * vnoise(z, 5)), z) for z in np.arange(-40, 14.5, 0.8)]
            self._ground_poly(c, left + right, p['path'], 0.55, blur=22)

    def _ground_poly(self, c, pts, color, alpha, blur=0):
        cam = self.cam
        near = 0.35
        cp = [cam.to_cam(x, 0, z) for (x, z) in pts]
        # clip polygon against the near plane (Sutherland-Hodgman)
        out = []
        n = len(cp)
        for i in range(n):
            a, b = cp[i], cp[(i + 1) % n]
            ain, bin_ = a[2] >= near, b[2] >= near
            if ain:
                out.append(a)
            if ain != bin_:
                u = (near - a[2]) / (b[2] - a[2])
                out.append((lerp(a[0], b[0], u), a[1], near))
        if len(out) < 3:
            return
        scr = [(W / 2 + rx * cam.focal / rz, H * cam.horizon + cam.y * cam.focal / rz, rz) for rx, ry, rz in out]
        path = poly([(a, b) for a, b, _ in scr])
        dmid = sorted(d for *_, d in scr)[len(scr) // 2]
        cc = mix(color, self.pal['fog'], self.fog_amount(max(dmid, 4)))
        c.drawPath(path, paint(cc, alpha=alpha, blur=blur))

    # ---- trees ------------------------------------------------------------
    def tree_list(self):
        trees = list(forest_trees())
        if self.overgrown:
            trees += overgrowth_trees()
        trees += self.extra_trees
        return trees

    def queue_trees(self, max_d=55):
        imgs = tree_images()
        cam = self.cam
        ls = self.light_side()
        for (x, z, th, var, flip) in self.tree_list():
            if any(math.hypot(x - hx, z - hz) < hr for hx, hz, hr in self.hide_trees_near):
                continue
            rx, ry, rz = cam.to_cam(x, 0, z)
            if rz < 0.4 or rz > max_d:
                continue
            s = cam.focal / rz
            sx = W / 2 + rx * s
            wpx = th * 0.30 * s
            if sx + wpx < -50 or sx - wpx > W + 50:
                continue
            self.items.append((rz, lambda c, x=x, z=z, th=th, var=var, flip=flip, rz=rz, sx=sx, s=s:
                               self._draw_tree(c, imgs[var], th, rz, sx, s, flip, ls)))

    def _draw_tree(self, c, img, th, d, sx, s, flip, ls):
        p = self.pal
        f = self.fog_amount(d)
        dark = mix(p['tree_dark'], p['fog'], f)
        light = mix(mix(p['tree_dark'], p['tree_light'], 0.85), p['fog'], f * 0.9)
        if self.fire_light > 0:
            fx, fz = FIRE_POS[0], FIRE_POS[2]
        hpx = th * s
        wpx = hpx * img.width() / img.height()
        gy = self.ground_y(d)
        c.save()
        c.translate(sx, gy)
        if (ls > 0) != flip:  # mirror so the rim faces the moon
            c.scale(-1, 1)
        pnt = skia.Paint(AntiAlias=True)
        pnt.setColorFilter(gray_to_ramp(dark, light))
        if d < 3.5:
            pnt.setImageFilter(skia.ImageFilters.Blur((3.5 - d) * 6 + 2, (3.5 - d) * 6 + 2))
        c.drawImageRect(img, skia.Rect(-wpx / 2, -hpx, wpx / 2, 0),
                        skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kNearest), pnt)
        c.restore()

    # ---- fog sheets -------------------------------------------------------
    def queue_fog(self, depths=(7, 11, 16, 23, 32, 45), height=3.2, alpha=0.55):
        tex = fog_texture()
        cam = self.cam
        for i, d in enumerate(depths):
            def fn(c, d=d, i=i):
                s = cam.focal / d
                gy = self.ground_y(d)
                hpx = height * s * (1 + 0.15 * i)
                wpx = hpx * 4.0
                off = ((self.t * (6 + i * 2.0) + i * 330 - cam.x * s * 0.0) % wpx)
                fogc = mix(self.pal['fog'], (1, 1, 1, 1), 0.08 if self.tod != 'morning' else 0.15)
                pnt = skia.Paint(AntiAlias=True)
                pnt.setColorFilter(skia.ColorFilters.Blend(col(fogc), skia.BlendMode.kSrcIn))
                pnt.setAlphaf(alpha * (0.6 + 0.4 * (i % 2)))
                x = -wpx + off - (cam.x * s * 0.3) % wpx
                while x < W:
                    c.drawImageRect(tex, skia.Rect(x, gy - hpx * 0.75, x + wpx, gy + hpx * 0.25),
                                    skia.SamplingOptions(skia.FilterMode.kLinear), pnt)
                    x += wpx
            self.items.append((d, fn))

    # ---- ground clutter ---------------------------------------------------
    def queue_clutter(self, max_d=16, seed=5, density=1.0):
        rng = random.Random(seed)
        cam = self.cam
        p = self.pal
        n = int(260 * density)
        for i in range(n):
            x = cam.x + rng.uniform(-14, 14)
            z = rng.uniform(-40, 40)
            kind = rng.random()
            sz = rng.uniform(0.6, 1.3)
            rot = rng.uniform(-0.6, 0.6)
            seedi = rng.randrange(1 << 20)
            if not self.overgrown and z < 14.5 and abs(x - path_x(z)) < PATH_W / 2 and kind < 0.75:
                continue
            rx, ry, rz = cam.to_cam(x, 0, z)
            if rz < 0.6 or rz > max_d:
                continue

            def fn(c, x=x, z=z, kind=kind, sz=sz, rot=rot, seedi=seedi):
                pr = cam.project(x, 0, z)
                if not pr:
                    return
                sx, sy, s, d = pr
                f = self.fog_amount(d)
                base = mix(p['grass'], p['fog'], f)
                rim = mix(mix(p['grass'], p['tree_light'], 0.7), p['fog'], f)
                c.save()
                c.translate(sx, sy)
                c.scale(s, s)
                r = random.Random(seedi)
                if kind < 0.6:      # grass / fern tuft
                    for k in range(r.randint(5, 9)):
                        a = r.uniform(-1.1, 1.1)
                        L = r.uniform(0.12, 0.32) * sz
                        sway = 0.04 * math.sin(self.t * 1.3 + seedi % 7 + k)
                        path = skia.Path()
                        path.moveTo(-0.01, 0)
                        path.quadTo(math.sin(a) * L * 0.5, -L * 0.6, math.sin(a) * L + sway, -L * math.cos(a) * 0.9)
                        path.quadTo(math.sin(a) * L * 0.5 + 0.01, -L * 0.55, 0.012, 0)
                        c.drawPath(path, paint(base if k % 3 else rim))
                elif kind < 0.85:   # dry branch
                    c.rotate(math.degrees(rot) * 0.2)
                    L = r.uniform(0.4, 1.0) * sz
                    c.drawLine(-L / 2, 0, L / 2, -0.02, paint(rim, stroke=0.025))
                    for k in range(3):
                        u = r.uniform(-0.4, 0.4) * L
                        c.drawLine(u, -0.01, u + r.uniform(-0.15, 0.15), -r.uniform(0.04, 0.12), paint(base, stroke=0.012))
                else:               # stone / root
                    c.drawOval(skia.Rect(-0.12 * sz, -0.07 * sz, 0.12 * sz, 0.01), paint(base))
                    c.drawOval(skia.Rect(-0.1 * sz, -0.07 * sz, 0.02 * sz, -0.03 * sz), paint(rim, alpha=0.6))
                c.restore()
            self.items.append((rz, fn))

    # ---- moon god-rays ----------------------------------------------------
    def draw_rays(self, c, strength=0.10):
        ls = self.light_side()
        for i in range(5):
            x0 = W * (0.1 + i * 0.22) + 60 * math.sin(self.t * 0.15 + i)
            w = 90 + 50 * (i % 3)
            path = poly([(x0 + ls * 300, -50), (x0 + ls * 300 + w, -50), (x0 - ls * 500 + w * 2.2, H), (x0 - ls * 500, H)])
            a = strength * (0.5 + 0.5 * math.sin(self.t * 0.3 + i * 1.7))
            c.drawPath(path, paint(self.pal['rim'], alpha=a, blur=40, blend=skia.BlendMode.kScreen))

    # ---- render ------------------------------------------------------------
    def render(self, c, trees=True, fog=True, clutter=True, rays=0.0):
        self.draw_sky(c)
        self.draw_ground(c)
        if trees:
            self.queue_trees()
        if fog:
            self.queue_fog()
        if clutter:
            self.queue_clutter()
        self.items.sort(key=lambda it: -it[0])
        for d, fn in self.items:
            fn(c)
        if rays:
            self.draw_rays(c, rays)
