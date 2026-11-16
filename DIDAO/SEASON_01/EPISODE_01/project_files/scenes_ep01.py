"""DIDAO S01E01 - shot-by-shot animation for the 12 clips.

Each clip is a function render_XX(c, t, frame, lang) that paints one 1080x1920 frame
at local clip time t (seconds). All clips share the same engine, forest layout,
character rigs and post-processing so they cut together seamlessly.
"""
import math
import os
import random
import sys

import skia

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'ASSETS'))

from didao_engine.core import (W, H, FPS, Camera, clamp, col, draw_text, ease_in, ease_in_out, ease_out, fbm,
                               fog_filter, hexc, keys, lerp, lin_grad, mix, paint, poly, post, rad_grad, seg,
                               smooth, smooth_path, tint_filter, vnoise)
from didao_engine.forest import (CARVED_TREE, FIRE_POS, MOON_DIR, PALETTES, TENT_POS, Scene, path_x)
from didao_engine.characters import (EXPR, HERO, LENA, MAX, Light, base_pose, draw_character, draw_portrait,
                                     draw_slender, expr, expr_mix, front_walk_pose, pose, pose_mix, walk_pose)
from didao_engine.props import (draw_bark, draw_beam, draw_carving, draw_fire, draw_phone, draw_tent, fire_glow,
                                TENT_COL, TENT_DARK)


# =============================================================================
# helpers
# =============================================================================
def char_light(scene, x, z, fire=0.0, rim_k=None, front=0.0, front_col=None):
    pal = scene.pal
    L = Light(amb=pal['amb'], rim=pal['rim'], rim_side=scene.light_side(),
              rim_k=rim_k if rim_k is not None else (0.85 if scene.tod != 'morning' else 0.30), shade=0.45)
    if fire > 0:
        d = math.hypot(x - FIRE_POS[0], z - FIRE_POS[2])
        w = fire * 0.6 * clamp(1.9 / (d + 0.4))
        pf = scene.cam.project(*FIRE_POS)
        pc = scene.cam.project(x, 1.0, z)
        side = 1
        if pf and pc:
            side = 1 if pf[0] > pc[0] else -1
            if pf[3] < pc[3] - 0.3:      # fire between camera and character -> frontal warm light
                L.front = clamp(w * 0.35)
                L.front_col = (1.0, 0.62, 0.38)
        L.warm = clamp(w)
        L.warm_side = side
        L.amb = tuple(a + wc * 0.22 * w for a, wc in zip(L.amb, (0.75, 0.38, 0.18)))
    if front:
        L.front = front
        L.front_col = front_col or (0.85, 0.9, 1.0)
    return L


def put_char(scene, cd, x, z, p, view='front', e=None, fire=0.0, flip=False, y=0.0, light=None, blur=None, rim_k=None):
    e = e or EXPR['neutral']

    def fn(c, pr):
        sx, sy, s, d = pr
        lt = light or char_light(scene, x, z, fire, rim_k=rim_k)
        f = scene.fog_amount(d)
        c.save()
        c.translate(sx, sy)
        c.scale(s, s)
        c.saveLayer(None, paint(cf=fog_filter(scene.pal['fog'], f)))
        bp = None
        if blur:
            bp = blur / s
        draw_character(c, cd, p, view, e, lt, t=scene.t, flip=flip, blur_px=bp)
        c.restore()
        c.restore()
    scene.add(x, y, z, fn)


def put_slender(scene, x, z, t, alpha=1.0, tilt=6.0, distort=0.0, seed=0, arm_spread=0.0, extra_fog=0.0):
    def fn(c, pr):
        sx, sy, s, d = pr
        f = clamp(scene.fog_amount(d) * 0.85 + extra_fog)
        c.save()
        c.translate(sx, sy)
        c.scale(s, s)
        c.saveLayer(None, paint(cf=fog_filter(scene.pal['fog'], f)))
        lt = Light(amb=tuple(a * 1.15 for a in scene.pal['amb']), rim=scene.pal['rim'], rim_side=scene.light_side(),
                   rim_k=0.6, shade=0.55)
        draw_slender(c, t=t, tilt=tilt, light=lt, alpha=alpha, distort=distort, seed=seed, arm_spread=arm_spread)
        c.restore()
        c.restore()
    scene.add(x, 0, z, fn)


def put_fire(scene, t, intensity, embers=1.0, smoke=0.3):
    def fn(c, pr):
        sx, sy, s, d = pr
        c.save()
        c.translate(sx, sy)
        c.scale(s, s)
        draw_fire(c, t, intensity, embers=embers, smoke=smoke)
        c.restore()
    scene.add(*FIRE_POS, fn)


def fire_light_overlay(c, scene, t, intensity):
    pr = scene.cam.project(*FIRE_POS)
    if pr and intensity > 0:
        fire_glow(c, pr[0], pr[1], pr[2], intensity, t)


def put_tent(scene, t, door=0.0, wind=0.3, skew=0.25, flip=False):
    def fn(c, pr):
        sx, sy, s, d = pr
        f = scene.fog_amount(d)
        c.save()
        c.translate(sx, sy)
        c.scale(s, s)
        if flip:
            c.scale(-1, 1)
        c.saveLayer(None, paint(cf=fog_filter(scene.pal['fog'], f)))
        lt = Light(amb=scene.pal['amb'], rim=scene.pal['rim'], rim_side=scene.light_side() * (-1 if flip else 1), rim_k=0.6)
        draw_tent(c, t=t, door=door, wind=wind, light=lt, skew=skew)
        c.restore()
        c.restore()
    scene.add(*TENT_POS, fn, bias=0.6)


def put_log(scene, x, z, length=1.6, ang=0.0):
    def fn(c, pr):
        sx, sy, s, d = pr
        c.save()
        c.translate(sx, sy)
        c.scale(s, s)
        c.drawRoundRect(skia.Rect(-length / 2, -0.26, length / 2, 0.0), 0.12, 0.12, paint((0.07, 0.055, 0.05)))
        c.drawRoundRect(skia.Rect(-length / 2, -0.26, length / 2, -0.21), 0.05, 0.05, paint((0.25, 0.20, 0.16), alpha=0.6))
        c.restore()
    scene.add(x, 0, z, fn, bias=0.05)


def black(c):
    c.clear(skia.Color4f(0, 0, 0, 1))


def cut_flash(c, t, at, dur=0.12, color=(0, 0, 0)):
    """Short dip at a hard cut to soften it."""
    a = 1 - clamp(abs(t - at) / dur)
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint(color, alpha=a * 0.6))


def tent_interior(c, t, light=0.0, ripple=0.0, shadow=None, branch=1.0, zoom=1.0, cx=0.5, cy=0.42):
    """Inside the dome tent at night: moonlit fabric, seams, moving branch shadows."""
    c.save()
    c.translate(W * cx, H * cy)
    c.scale(zoom, zoom)
    c.translate(-W * cx, -H * cy)
    base = (0.08 + light * 0.04, 0.11 + light * 0.05, 0.15 + light * 0.06, 1)
    c.drawRect(skia.Rect(-400, -400, W + 400, H + 400), paint(base))
    # moon glow through the fabric (upper left)
    c.drawCircle(W * 0.22, H * 0.12, 900, paint(shader=rad_grad((W * 0.22, H * 0.12), 900,
                 [(0.30, 0.38, 0.52, 0.85), (0.15, 0.2, 0.3, 0.3), (0, 0, 0, 0)], [0, 0.45, 1])))
    # branch shadows
    if branch:
        for i in range(6):
            x0 = W * (0.05 + 0.18 * i) + 60 * math.sin(t * 0.7 + i) + ripple * 30 * math.sin(t * 9 + i)
            pth = skia.Path()
            pth.moveTo(x0, -100)
            pth.cubicTo(x0 + 120, H * 0.15, x0 - 80, H * 0.3, x0 + 40 * math.sin(t + i), H * 0.5)
            c.drawPath(pth, paint((0.02, 0.03, 0.05), alpha=0.35 * branch, stroke=26 - i * 2, blur=18))
            for k in range(4):
                bx = x0 + k * 30
                by = H * (0.06 + 0.1 * k)
                c.drawLine(bx, by, bx + 160 * (1 if k % 2 else -1), by - 90 + 20 * math.sin(t * 1.3 + k + i),
                           paint((0.02, 0.03, 0.05), alpha=0.25 * branch, stroke=10, blur=12))
    if shadow is not None:
        sx, sa = shadow
        c.save()
        c.translate(sx, H * 0.70)
        c.scale(310, 310)
        sil = skia.Paint()
        sil.setImageFilter(skia.ImageFilters.Blur(0.06, 0.06))
        c.saveLayer(skia.Rect(-2, -4, 2, 1), sil)
        draw_slender(c, t=t, tilt=8, light=Light(amb=(0, 0, 0), rim_k=0.0, shade=0.0), alpha=sa)
        c.restore()
        c.restore()
    # dome seams (arcs) and fabric folds
    wob = lambda i: ripple * 22 * math.sin(t * 7.0 + i * 1.3)
    for i, (x0, x1) in enumerate(((-300, W * 0.40), (W * 0.15, W * 0.55), (W * 0.85, W * 0.45), (W + 300, W * 0.60))):
        pth = skia.Path()
        pth.moveTo(x0, H * 1.1)
        pth.quadTo((x0 + x1) / 2 + wob(i), H * 0.35, x1, -60)
        c.drawPath(pth, paint((0.03, 0.04, 0.06), alpha=0.8, stroke=14, blur=3))
        c.drawPath(pth, paint((0.35, 0.42, 0.55), alpha=0.18, stroke=4, blur=2))
    for i in range(9):
        x = W * (i / 8) + wob(i + 4)
        c.drawLine(x, H * 0.05, x + 120, H * 0.9, paint((0.0, 0.0, 0.0), alpha=0.18, stroke=40, blur=30))
    c.restore()


def sleeping_bag(c, cx, top_y, w, color=hexc('#18202b'), t=0.0, breath=0.0):
    rise = breath * 6 * math.sin(t * 2 * math.pi / 3.5)
    pth = smooth_path([(cx - w * 0.75, H + 50), (cx - w * 0.62, top_y + 90), (cx - w * 0.45, top_y + rise), (cx, top_y - 18 + rise),
                       (cx + w * 0.45, top_y + rise), (cx + w * 0.62, top_y + 90), (cx + w * 0.75, H + 50)], tension=0.45)
    c.drawPath(pth, paint(color))
    c.save()
    c.clipPath(pth, doAntiAlias=True)
    for i in range(1, 9):
        y = top_y + i * 130 + rise
        c.drawLine(cx - w, y, cx + w, y + 30, paint(mix(color, (0, 0, 0, 1), 0.45), stroke=8, blur=4))
        c.drawLine(cx - w, y - 30, cx + w, y, paint(mix(color, (0.5, 0.6, 0.8, 1), 0.12), stroke=20, blur=14))
    c.drawRect(skia.Rect(cx - w, top_y - 40, cx - w * 0.2, H + 60), paint((0.4, 0.5, 0.7), alpha=0.06, blur=40))
    c.restore()
    # bag hem / collar
    hem = skia.Path()
    hem.moveTo(cx - w * 0.45, top_y + rise + 6)
    hem.quadTo(cx, top_y - 30 + rise, cx + w * 0.45, top_y + rise + 6)
    c.drawPath(hem, paint(mix(color, (1, 1, 1, 1), 0.1), stroke=26))


def breath_puff(c, x, y, t, period=3.2, scale=1.0):
    ph = (t % period) / period
    if ph < 0.45:
        u = ph / 0.45
        for k in range(4):
            r = (30 + 70 * u + k * 12) * scale
            c.drawCircle(x + 60 * u * scale + k * 18, y - 20 * u * scale + k * 8, r,
                         paint((0.75, 0.82, 0.95), alpha=0.10 * math.sin(u * math.pi), blur=r * 0.5))


def portrait(c, cd, x, y, scale, yaw=0.0, e=None, light=None, t=0.0, rot=0.0, side=False, back=False):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(scale, scale)
    draw_portrait(c, cd, yaw, e, light, t, side=side, back=back)
    c.restore()


def blink_at(t, times, dur=0.16):
    for b in times:
        if b <= t <= b + dur:
            return math.sin((t - b) / dur * math.pi)
    return 0.0


def defocus_forest(c, tod='morning', t=0.0, seed=1):
    """Soft out-of-focus forest background for close-ups."""
    pal = PALETTES[tod]
    c.drawRect(skia.Rect(0, 0, W, H), paint(shader=lin_grad((0, 0), (0, H), [pal['sky_mid'], pal['fog'], pal['ground_near']], [0, 0.5, 1])))
    rng = random.Random(seed)
    for i in range(16):
        x = rng.uniform(-100, W + 100)
        w = rng.uniform(40, 160)
        d = rng.uniform(0.3, 1.0)
        cc = mix(pal['tree_dark'], pal['fog'], d * 0.8)
        c.drawRect(skia.Rect(x, -50, x + w, H + 50), paint(cc, blur=30 + 30 * (1 - d)))
    for i in range(40):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(20, 70)
        c.drawCircle(x + 10 * math.sin(t * 0.3 + i), y, r, paint(mix(pal['fog'], (1, 1, 1, 1), 0.2), alpha=0.07, blur=r * 0.4))


# =============================================================================
# CLIP 01 - JOURNEY  (dusk, crane down onto the three friends walking the path)
# =============================================================================
def render_01(c, t, frame, lang):
    u = ease_in_out(seg(t, 0.0, 6.0))
    cam = Camera(x=lerp(0.6, 0.15, u), y=lerp(9.5, 1.55, u), z=lerp(15.5, 7.8, ease_in_out(seg(t, 0, 11.5))), yaw=math.pi,
                 focal=lerp(1150, 1350, u), horizon=lerp(0.16, 0.50, u))
    sc = Scene(cam, tod='dusk', t=t)
    zh = -6.0 + 0.86 * t
    ph = t * 0.86
    for cd, dz, dx, phase_off, e in ((HERO, 0.0, 0.0, 0.0, 'calm'), (MAX, -0.7, -0.85, 0.37, 'calm'), (LENA, -0.35, 0.80, 0.71, 'neutral')):
        z = zh + dz
        x = path_x(z) + dx
        look = 0.35 * math.sin(t * 0.5 + phase_off * 5)
        ex = expr(e, lx=look, blink=blink_at(t, [2.1 + phase_off, 6.3 + phase_off, 9.8 + phase_off]))
        p = front_walk_pose(ph + phase_off, pack=1, yaw=look * 25)
        put_char(sc, cd, x, z, p, 'front', ex, rim_k=0.6)
    sc.render(c, rays=0.07)
    post(c, frame, vignette=0.8)


# =============================================================================
# CLIP 02 - CAMPSITE  (tent goes up, fire is lit, dusk turns to night)
# =============================================================================
def render_02(c, t, frame, lang):
    u = seg(t, 0, 10)
    cam = Camera(x=lerp(3.4, 3.0, u), y=1.6, z=lerp(14.3, 15.0, ease_in_out(u)), yaw=-0.62, focal=1300, horizon=0.52)
    sc = Scene(cam, tod=('dusk', 'night', smooth(seg(t, 2.0, 9.5))), t=t)
    fi = ease_out(seg(t, 3.6, 6.5))
    if 3.0 < t < 3.6:
        fi = 0.15 * abs(math.sin(t * 25))
    put_tent(sc, t, door=0.0, wind=0.25, skew=0.3)
    put_fire(sc, t, fi, embers=fi, smoke=0.25)
    put_log(sc, 0.8, 20.6, 1.5)
    # MAX - pegging the tent (side view facing the tent)
    hit = abs(math.sin(t * 2.4))
    put_char(sc, MAX, -1.0, 21.0, pose(crouch=0.55, lean=28, ls=60 + 40 * hit, le=-30, rs=45, re=-20, lh=40, rh=-10, lk=40, rk=30,
                                        lhand='fist', rhand='fist'), 'side', EXPR['calm'], fire=fi, flip=True)
    # LENA - brings firewood, then stands warming hands
    lx = keys(t, [(0, 4.4), (3.6, 2.15)], fn=lambda v: v)
    if t < 3.6:
        lp = walk_pose(t * 0.95, ls=70, le=60, rs=70, re=60, lhand='fist', rhand='fist')
    else:
        lp = pose(ls=keys(t, [(3.6, 70), (4.4, 35)]), le=keys(t, [(3.6, 60), (4.4, 70)]), rs=keys(t, [(3.6, 70), (4.4, 35)]),
                  re=keys(t, [(3.6, 60), (4.4, 70)]), lhand='open', rhand='open', lean=6)
    put_char(sc, LENA, lx, 19.7, lp, 'side', expr('calm', blink=blink_at(t, [5.5])), fire=fi, flip=True)
    # wood bundle carried
    # HERO - kneeling at the fire, striking a match
    strike = seg(t, 2.6, 3.4)
    put_char(sc, HERO, 0.05, 18.9, pose(crouch=0.85, lean=24, ls=keys(t, [(0, 50), (2.6, 75), (3.4, 60), (5, 40)]), le=-40,
                                        rs=keys(t, [(0, 40), (2.6, 70), (3.2, 85), (5, 35)]), re=-30, lh=70, rh=50, lk=110, rk=100,
                                        lhand='fist', rhand='fist'), 'side', expr('calm', blink=blink_at(t, [6.2])), fire=fi)
    sc.render(c, rays=0.05 * (1 - u))
    fire_light_overlay(c, sc, t, fi)
    # match flare
    if 2.9 < t < 3.7:
        pr = cam.project(0.62, 0.35, 19.0)
        if pr:
            a = 1 - seg(t, 3.0, 3.7)
            c.drawCircle(pr[0], pr[1], 60, paint(shader=rad_grad((pr[0], pr[1]), 60, [(1, 0.8, 0.4, 0.9 * a), (1, 0.5, 0.2, 0)]), blend=skia.BlendMode.kPlus))
    post(c, frame, vignette=0.8)


# =============================================================================
# CLIP 03 - FIRST SIGHTING
# =============================================================================
SIGHT = [(-1.7 + 0.3 * k, 7.0 + 1.6 * k, 1.1) for k in range(8)]
SEAT = {'lena': (-0.35, 20.65), 'hero': (0.9, 20.75), 'max': (2.15, 20.6)}


def render_03b(c, t, frame, lang):
    render_03(c, t + 4.6, frame, lang, standalone=True)


def render_03a(c, t, frame, lang):
    render_03(c, t, frame, lang, shift=3.0)


def render_03(c, t, frame, lang, shift=0.0, standalone=False):
    if not standalone:
        u = seg(t, 0, 4.6 + shift)
        laugh = 1 - smooth(seg(t, 3.9, 4.4)) if shift else 0.0
        t0 = t
        t = t - shift
        cam = Camera(x=0.9, y=0.95, z=lerp(16.0, 16.5, ease_in_out(u)), yaw=0.0, focal=1650, horizon=0.47)
        sc = Scene(cam, tod='night', t=t)
        put_fire(sc, t, 0.95)
        for nm in SEAT:
            put_log(sc, SEAT[nm][0], SEAT[nm][1] + 0.12, 1.1)
        scared = smooth(seg(t, 1.5, 2.1))
        le = expr_mix(expr('smile', lx=0.1), expr('scared', lx=-0.65, ly=-0.3), scared)
        le['blink'] = blink_at(t, [0.8])
        le['mouth'] += 0.30 * laugh * abs(math.sin(t0 * 8.0))
        arm = ease_out(seg(t, 2.5, 3.3))
        lp = pose(sit=1, rs=lerp(-8, -125, arm), re=lerp(-20, 10, arm), rhand='point' if arm > 0.3 else 'relaxed',
                  ls=12, le=40, yaw=lerp(5, -25, scared), head=lerp(0, -4, scared))
        put_char(sc, LENA, *SEAT['lena'][:1], SEAT['lena'][1], lp, 'front', le, fire=1.0)
        look_h = smooth(seg(t, 2.9, 3.5))
        he = expr_mix(expr('smile', lx=0.3), expr('worried', lx=-0.7), look_h)
        he['blink'] = blink_at(t, [1.2])
        he['mouth'] += 0.22 * laugh * abs(math.sin(t0 * 7.0 + 1.0))
        put_char(sc, HERO, SEAT['hero'][0], SEAT['hero'][1], pose(sit=1, ls=20, le=50, rs=-20, re=-50, lhand='fist', rhand='fist',
                                                                  yaw=lerp(10, -30, look_h)), 'front', he, fire=1.0)
        look_m = smooth(seg(t, 3.2, 3.9))
        me = expr_mix(expr('smile', lx=-0.4), expr('worried', lx=-0.8), look_m)
        me['mouth'] += 0.35 * laugh * abs(math.sin(t0 * 6.0 + 2.0))
        put_char(sc, MAX, SEAT['max'][0], SEAT['max'][1], pose(sit=1, ls=25, le=45, rs=-25, re=-45, lhand='fist', rhand='fist',
                                                               yaw=lerp(-15, -35, look_m)), 'front', me, fire=1.0)
        sc.render(c, rays=0.0)
        fire_light_overlay(c, sc, t, 0.95)
        post(c, frame, vignette=0.85)
    else:
        tt = t - 4.6
        u = ease_in_out(seg(tt, 0, 5.4))
        cam = Camera(x=-0.9, y=1.5, z=24.6, yaw=math.pi, focal=lerp(1450, 2700, u), horizon=0.5)
        sc = Scene(cam, tod='night', t=t, hide_trees_near=SIGHT)
        put_fire(sc, t, 0.9)
        for nm in SEAT:
            put_log(sc, SEAT[nm][0], SEAT[nm][1] + 0.12, 1.1)
        put_char(sc, LENA, SEAT['lena'][0], SEAT['lena'][1], pose(sit=1, ls=125, le=-8, lhand='point', rs=-10), 'back', fire=1.0)
        put_char(sc, HERO, SEAT['hero'][0], SEAT['hero'][1], pose(sit=1, ls=10, rs=-10, head=-3), 'back', fire=1.0)
        put_char(sc, MAX, SEAT['max'][0], SEAT['max'][1], pose(sit=1, ls=10, rs=-10, head=-6), 'back', fire=1.0)
        put_slender(sc, -1.7, 7.0, t, extra_fog=-0.15, tilt=keys(tt, [(0, 4), (3.5, 4), (4.5, 14)]))
        sc.render(c, rays=0.05)
        fire_light_overlay(c, sc, t, 0.9)
        post(c, frame, vignette=0.9)


# =============================================================================
# CLIP 04 - DISAPPEARANCE
# =============================================================================
def render_04(c, t, frame, lang):
    if t < 5.6:
        u = seg(t, 0, 5.6)
        cam = Camera(x=0.5, y=1.45, z=24.8, yaw=math.pi, focal=lerp(1700, 1900, u), horizon=0.5)
        sc = Scene(cam, tod='night', t=t, hide_trees_near=SIGHT)
        put_fire(sc, t, 0.9)
        stand = ease_in_out(seg(t, 0.0, 0.9))
        raise_ = ease_out(seg(t, 0.9, 1.6))
        hx, hz = SEAT['hero']
        put_char(sc, HERO, hx, hz, pose(sit=1 - stand, ls=lerp(10, 150, raise_), le=lerp(10, -10, raise_), lhand='flashlight', rs=-10), 'back', fire=1.0)
        put_char(sc, LENA, SEAT['lena'][0], SEAT['lena'][1], pose(sit=1, ls=lerp(125, 20, seg(t, 4.2, 5.0)), le=-8, lhand='point', rs=-10), 'back', fire=1.0)
        put_char(sc, MAX, SEAT['max'][0], SEAT['max'][1], pose(sit=1 - 0.6 * stand, ls=10, rs=-10), 'back', fire=1.0)
        gone = t > 4.6
        dist = seg(t, 4.0, 4.6)
        if not gone:
            put_slender(sc, -1.7, 7.0, t, extra_fog=-0.15, tilt=14, distort=dist * 1.5, alpha=1.0 - 0.5 * dist)
        sc.render(c, rays=0.04)
        fire_light_overlay(c, sc, t, 0.9)
        # beam from the torch towards the figure / then searching
        hand = cam.project(hx - 0.32, 1.62 - 0.4 * (1 - stand), hz - 0.25)
        tgt_w = (-1.7 + 0.9 * math.sin(max(0, t - 4.6) * 1.6) * seg(t, 4.6, 5.6), 1.7, 7.0)
        tgt = cam.project(*tgt_w)
        on = seg(t, 1.25, 1.4)
        if hand and tgt and on > 0:
            draw_beam(c, (hand[0], hand[1]), (tgt[0], tgt[1]), strength=on * 0.9, spread=0.10, t=t, flicker=dist)
        if 4.0 < t < 4.75:  # glitch flicker
            if int(t * 30) % 2 == 0:
                c.drawRect(skia.Rect(0, 0, W, H), paint((0.6, 0.7, 0.9), alpha=0.06, blend=skia.BlendMode.kPlus))
        post(c, frame, vignette=0.9)
    else:
        tt = t - 5.6
        u = ease_in_out(seg(tt, 0, 4.9))
        cam = Camera(x=0.9, y=1.42, z=lerp(17.4, 17.9, u), yaw=0.0, focal=1450, horizon=0.44)
        sc = Scene(cam, tod='night', t=t)
        put_fire(sc, t, 0.85)
        torch_l = Light()
        le = expr('scared', lx=0.4, ly=-0.2, blink=blink_at(tt, [1.6]))
        put_char(sc, LENA, 0.12, 20.6, pose(ls=25, le=80, rs=-25, re=-80, lhand='fist', rhand='fist', yaw=10), 'front', le, fire=0.85)
        shrug = math.sin(math.pi * seg(tt, 2.0, 3.4))
        me = expr_mix(expr('squint', lx=-0.2), expr('calm', lx=-0.5), seg(tt, 2.0, 3.0))
        me['curve'] = 0.35 * shrug
        put_char(sc, MAX, 1.68, 20.5, pose(ls=lerp(5, 45, shrug), le=lerp(5, -80, shrug), rs=lerp(-5, -45, shrug), re=lerp(-5, 80, shrug),
                                           lhand='open' if shrug > 0.3 else 'relaxed', rhand='open' if shrug > 0.3 else 'relaxed',
                                           yaw=-20, head=-4 * shrug), 'front', me, fire=0.85)
        he = expr_mix(expr('surprised', lx=0.0, ly=-0.3), expr('worried', lx=0.8), smooth(seg(tt, 2.4, 3.4)))
        he['blink'] = blink_at(tt, [3.7])
        put_char(sc, HERO, 0.9, 20.75, pose(ls=30, le=60, lhand='flashlight', rs=-5, yaw=lerp(0, 25, smooth(seg(tt, 2.4, 3.4)))), 'front', he, fire=0.85)
        sc.render(c, rays=0.0)
        fire_light_overlay(c, sc, t, 0.85)
        cut_flash(c, t, 5.6)
        post(c, frame, vignette=0.9)


# =============================================================================
# CLIP 05 - MIDNIGHT (inside the tent, hero wakes)
# =============================================================================
MOON_FACE = Light(amb=(0.40, 0.47, 0.66), rim=hexc('#9fb6dc'), rim_side=-1, rim_k=0.55, shade=0.55)


def render_05(c, t, frame, lang):
    u = ease_in_out(seg(t, 0, 9))
    zoom = lerp(1.0, 1.55, u)
    tent_interior(c, t, light=0.0, ripple=0.05, branch=0.8, zoom=zoom, cy=0.40)
    c.save()
    c.translate(W / 2, H * 0.40)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H * 0.40)
    # pillow
    c.drawOval(skia.Rect(W * 0.16, H * 0.24, W * 0.84, H * 0.48), paint((0.11, 0.13, 0.17), blur=12))
    c.drawOval(skia.Rect(W * 0.22, H * 0.27, W * 0.62, H * 0.38), paint((0.22, 0.26, 0.34), alpha=0.4, blur=40))
    # friends' sleeping bags at the edges
    sleeping_bag(c, -120, H * 0.50, 520, color=hexc('#161c1a'), t=t, breath=1)
    c.drawOval(skia.Rect(-120, H * 0.36, 160, H * 0.50), paint(mix(MAX.hat, (0.05, 0.07, 0.12, 1), 0.6)))
    sleeping_bag(c, W + 120, H * 0.52, 520, color=hexc('#22181b'), t=t + 1.3, breath=1)
    c.drawOval(skia.Rect(W - 170, H * 0.39, W + 140, H * 0.53), paint(mix(LENA.hair, (0.03, 0.04, 0.08, 1), 0.55)))
    # hero
    wake = t > 1.6
    if not wake:
        e = expr('sleep')
    else:
        dart = keys(t, [(1.6, 0.0), (3.0, 0.0), (3.3, -0.75), (4.3, -0.75), (4.6, 0.7), (5.6, 0.7), (6.0, 0.0), (9, 0.0)])
        e = expr_mix('worried', 'scared', smooth(seg(t, 5.8, 8.5)))
        e['lx'] = dart
        e['ly'] = -0.25
        e['blink'] = blink_at(t, [2.3, 2.55, 7.4])
        if t < 1.8:
            e['eye'] *= seg(t, 1.6, 1.8)
    portrait(c, HERO, W / 2, H * 0.355, 300, yaw=0.0, e=e, light=MOON_FACE, t=t)
    sleeping_bag(c, W / 2, H * 0.47, 640, t=t, breath=0 if wake else 1)
    breath_puff(c, W * 0.53, H * 0.395, t, period=3.4 if not wake else 2.0, scale=0.6)
    c.restore()
    post(c, frame, vignette=0.95, grain=0.08)


# =============================================================================
# CLIP 06 - FOOTSTEPS
# =============================================================================
STEPS = (2.0, 2.8, 3.6, 7.9, 8.6, 9.3)


def render_06(c, t, frame, lang):
    step_k = sum(math.exp(-((t - s) / 0.12) ** 2) for s in STEPS)
    u = ease_in_out(seg(t, 4.0, 10.0))
    zoom = lerp(1.0, 1.45, u) * (1 + 0.006 * step_k)
    shadow_x = keys(t, [(7.4, W * 1.25), (10.0, -W * 0.25)], fn=lambda v: v)
    sh_a = 0.0 if t < 7.4 else 0.55 * math.sin(math.pi * seg(t, 7.4, 10.4))
    tent_interior(c, t, light=0.1, ripple=0.25 + 0.6 * step_k, shadow=(shadow_x, sh_a), branch=0.7, zoom=zoom, cy=0.45)
    c.save()
    c.translate(W / 2, H * 0.45)
    c.scale(zoom, zoom)
    c.translate(-W / 2, -H * 0.45)
    look = 0.85 * smooth(seg(t, 2.0, 2.15)) * (1 - 0.7 * smooth(seg(t, 4.6, 6.0))) + 0.6 * smooth(seg(t, 7.9, 8.05))
    e = expr('scared', lx=look, ly=-0.1, blink=blink_at(t, [0.6, 5.2, 6.6]))
    e['mouth'] = 0.2 + 0.25 * smooth(seg(t, 2.0, 2.5))
    flinch = 0.03 * step_k
    sleeping_bag(c, W / 2, H * 0.78, 800, t=t)
    portrait(c, HERO, W / 2 + 10 * math.sin(t * 0.8), H * 0.53 + 20 * flinch * 30, 330 * (1 - flinch), yaw=0.18 * look, e=e,
             light=MOON_FACE, t=t, rot=2 * math.sin(t * 0.5))
    breath_puff(c, W * 0.55, H * 0.62, t, period=1.8, scale=1.0)
    c.restore()
    post(c, frame, vignette=0.95, grain=0.08)


# =============================================================================
# CLIP 07 - SECOND SIGHTING (POV through the tent door, then the hero's face)
# =============================================================================
def render_07(c, t, frame, lang):
    if t < 99:
        u = ease_in_out(seg(t, 0.8, 10.3))
        cam = Camera(x=-2.25, y=0.62, z=21.2, yaw=math.pi + 0.10, focal=lerp(1250, 1800, u), horizon=0.52)
        sc = Scene(cam, tod='night', t=t)
        put_fire(sc, t, 0.0, embers=0.55, smoke=0.4)
        put_slender(sc, -3.4, 12.6, t, tilt=keys(t, [(0, 6), (6.6, 6), (7.4, 18)]))
        sc.render(c, rays=0.07)
        fire_light_overlay(c, sc, t, 0.06)
        # tent door opening (foreground fabric)
        op = ease_out(seg(t, 0.0, 1.3))
        door = smooth_path([(W * 0.5 - 80 - 420 * op, H * 1.05), (W * 0.5 - 60 - 380 * op, H * 0.55), (W * 0.5 - 40 - 200 * op, H * 0.12),
                            (W * 0.5 + 60, H * 0.02), (W * 0.5 + 120 + 250 * op, H * 0.15), (W * 0.5 + 140 + 330 * op, H * 0.6),
                            (W * 0.5 + 160 + 360 * op, H * 1.05)], tension=0.4)
        fab = skia.Path()
        fab.addRect(skia.Rect(-10, -10, W + 10, H + 10))
        fab.addPath(door)
        fab.setFillType(skia.PathFillType.kEvenOdd)
        c.drawPath(fab, paint(mix(TENT_COL, (0, 0, 0, 1), 0.72), blur=6))
        c.drawPath(door, paint((0.30, 0.38, 0.5), alpha=0.35, stroke=14, blur=10))
        # hand pulling the flap
        hx = W * 0.5 - 40 - 380 * op
        c.save()
        c.translate(hx, H * 0.56)
        c.rotate(-8)
        sk_ = mix(HERO.skin, (0.1, 0.12, 0.2, 1), 0.55)
        c.drawPath(smooth_path([(-140, -40), (10, -60), (40, -30), (42, 20), (10, 50), (-140, 60)]), paint(sk_))
        for i in range(4):
            c.drawRoundRect(skia.Rect(20, -55 + i * 26, 70, -33 + i * 26), 11, 11, paint(sk_))
        c.drawRect(skia.Rect(-420, -70, -120, 80), paint(HERO.top, blur=2))
        c.restore()
        post(c, frame, vignette=0.95)
    else:
        tt = t - 6.4
        u = ease_in_out(seg(tt, 0, 3.6))
        c.clear(col(hexc('#05070a')))
        sc_ = lerp(330, 420, u)
        e = expr('scared', lx=0.15, ly=-0.1, blink=blink_at(tt, [2.4]))
        e['mouth'] = 0.25
        lt = Light(amb=(0.48, 0.56, 0.75), rim=hexc('#a9c0e6'), rim_side=-1, rim_k=0.8, shade=0.6)
        portrait(c, HERO, W * 0.52, H * 0.46, sc_, yaw=-0.12, e=e, light=lt, t=t)
        # fabric gap framing the face
        gap = smooth_path([(W * 0.52 - sc_ * 0.95, H * 1.1), (W * 0.52 - sc_ * 0.8, H * 0.46), (W * 0.52 - sc_ * 0.5, H * 0.2),
                           (W * 0.52 + sc_ * 0.2, H * 0.12), (W * 0.52 + sc_ * 0.75, H * 0.3), (W * 0.52 + sc_ * 0.9, H * 0.7),
                           (W * 0.52 + sc_ * 1.05, H * 1.1)], tension=0.4)
        fab = skia.Path()
        fab.addRect(skia.Rect(-10, -10, W + 10, H + 10))
        fab.addPath(gap)
        fab.setFillType(skia.PathFillType.kEvenOdd)
        c.drawPath(fab, paint(mix(TENT_COL, (0.1, 0.12, 0.2, 1), 0.55)))
        c.drawPath(gap, paint((0.08, 0.1, 0.12), stroke=18))
        c.drawPath(gap, paint((0.5, 0.6, 0.8), alpha=0.25, stroke=5, blur=3))
        # zipper teeth along the gap
        breath_puff(c, W * 0.57, H * 0.56, tt, period=1.6, scale=1.1)
        cut_flash(c, t, 6.4)
        post(c, frame, vignette=0.9)


# =============================================================================
# CLIP 08 - DISAPPEARANCE AGAIN
# =============================================================================
def render_08(c, t, frame, lang):
    if t < 3.8:
        tent_interior(c, t, light=0.0, ripple=0.1, branch=0.6, zoom=1.15)
        if t < 1.5:
            e = expr('scared', lx=-0.8, ly=0.1)
            e['mouth'] = 0.15 + 0.3 * abs(math.sin(t * 11))
            portrait(c, HERO, W * 0.5, H * 0.42, 360, yaw=-0.3, e=e, light=MOON_FACE, t=t)
            sleeping_bag(c, W / 2, H * 0.70, 760, t=t)
        elif t < 2.6:
            tt = t - 1.5
            c.drawOval(skia.Rect(W * 0.1, H * 0.25, W * 0.9, H * 0.52), paint((0.20, 0.23, 0.28)))
            e = expr_mix('sleep', 'surprised', smooth(seg(tt, 0.25, 0.4)))
            e['lx'] = 0.6
            portrait(c, LENA, W * 0.5, H * 0.40, 380, yaw=0.15, e=e, light=MOON_FACE, t=t, rot=-6)
            sleeping_bag(c, W / 2, H * 0.55, 800, color=hexc('#35262a'), t=t)
            cut_flash(c, t, 1.5, 0.08)
        else:
            tt = t - 2.6
            c.drawOval(skia.Rect(W * 0.1, H * 0.25, W * 0.9, H * 0.52), paint((0.20, 0.23, 0.28)))
            e = expr_mix('sleep', 'confused', smooth(seg(tt, 0.2, 0.45)))
            e['lx'] = -0.5
            e['blink'] = blink_at(tt, [0.7])
            portrait(c, MAX, W * 0.5, H * 0.40, 370, yaw=-0.2, e=e, light=MOON_FACE, t=t, rot=5)
            sleeping_bag(c, W / 2, H * 0.55, 800, color=hexc('#26302a'), t=t)
            cut_flash(c, t, 2.6, 0.08)
        post(c, frame, vignette=0.95, grain=0.08)
    else:
        tt = t - 3.8
        u = ease_in_out(seg(tt, 0, 6.2))
        cam = Camera(x=-0.9, y=1.6, z=lerp(25.6, 25.1, u), yaw=math.pi - 0.08, focal=1350, horizon=0.5)
        sc = Scene(cam, tod='night', t=t)
        put_fire(sc, t, 0.0, embers=0.5, smoke=0.35)
        put_tent(sc, t, door=1.0, wind=0.3, skew=0.25, flip=True)
        # trio steps out from the tent (screen right) and fans out
        walkers = ((HERO, -2.0, 20.0, 0.0), (MAX, -0.8, 20.4, 0.35), (LENA, -3.1, 20.6, 0.6))
        for cd, fx, fz, delay in walkers:
            k = ease_out(seg(tt, 0.2 + delay, 2.2 + delay))
            x = lerp(-2.3, fx, k)
            z = lerp(22.0, fz, k)
            if k <= 0.02:
                continue
            raise_ = ease_out(seg(tt, 1.6 + delay, 2.4 + delay))
            p = front_walk_pose(tt * 1.1 + delay, amount=1 - k, ls=lerp(10, 150, raise_) if cd is not LENA else 10,
                                le=-10, lhand='flashlight' if cd is not LENA else 'relaxed', rs=-10)
            put_char(sc, cd, x, z, p, 'back')
        gone = tt > 2.85
        dist = seg(tt, 2.3, 2.85)
        if not gone:
            put_slender(sc, -3.4, 12.6, t, tilt=18, distort=dist * 1.5, alpha=1 - 0.5 * dist)
        sc.render(c, rays=0.06)
        for cd, fx, fz, delay in walkers[:2]:
            k = ease_out(seg(tt, 0.2 + delay, 2.2 + delay))
            on = seg(tt, 1.9 + delay, 2.1 + delay)
            if on <= 0:
                continue
            x = lerp(-2.3, fx, k)
            z = lerp(22.0, fz, k)
            hand = cam.project(x - 0.3, 1.55, z - 0.3)
            sweep = math.sin(max(0, tt - 3.0) * (1.3 + delay)) * 2.2 * seg(tt, 3.0, 4.0)
            tgt = cam.project(-3.4 + sweep + delay * 1.5 * seg(tt, 3.0, 4.5), 1.6, 12.6)
            if hand and tgt:
                draw_beam(c, (hand[0], hand[1]), (tgt[0], tgt[1]), strength=on * 0.85, spread=0.09, t=t + delay, flicker=dist)
        cut_flash(c, t, 3.8)
        post(c, frame, vignette=0.9)


# =============================================================================
# CLIP 09 - MISSING PATH (morning)
# =============================================================================
def render_09(c, t, frame, lang):
    if t < 6.6:
        u = ease_in_out(seg(t, 0, 6.6))
        cam = Camera(x=0.25, y=lerp(1.65, 2.1, u), z=lerp(18.6, 17.9, u), yaw=math.pi, focal=1250, horizon=lerp(0.50, 0.46, u))
        sc = Scene(cam, tod='morning', t=t, overgrown=True)
        put_fire(sc, t, 0.0, embers=0.0, smoke=0.25)
        turn_m = smooth(seg(t, 2.2, 2.8))
        put_char(sc, HERO, 0.15, 14.9, pose(pack=1, ls=8, rs=-8), 'back')
        if turn_m > 0.5:
            put_char(sc, MAX, 1.15, 15.1, pose(pack=1, head=-4), 'side', expr('confused'), flip=False)
        else:
            put_char(sc, MAX, 1.15, 15.1, pose(pack=1), 'back')
        put_char(sc, LENA, -0.85, 15.2, pose(pack=1, rs=-8, re=-20), 'back')
        sc.render(c)
        post(c, frame, vignette=0.7, grain=0.06)
    else:
        tt = t - 6.6
        u = ease_in_out(seg(tt, 0, 4.2))
        cam = Camera(x=0.2, y=1.5, z=lerp(11.4, 11.9, u), yaw=0.0, focal=1500, horizon=0.47)
        sc = Scene(cam, tod='morning', t=t, overgrown=True, hide_trees_near=[(0.2, 11.6, 1.6)])
        put_tent(sc, t, door=0.0, wind=0.2, skew=0.3)
        look = 0.8 * math.sin(tt * 1.3)
        put_char(sc, LENA, -0.85, 15.2, pose(pack=1, yaw=-30 * math.sin(tt * 1.1 + 1), rs=-15, re=-70, rhand='relaxed'), 'front',
                 expr('worried', lx=-0.6 * math.sin(tt * 1.1 + 1), blink=blink_at(tt, [2.0])))
        put_char(sc, HERO, 0.15, 14.9, pose(pack=1, yaw=25 * look), 'front', expr('confused', lx=look, blink=blink_at(tt, [3.1])))
        put_char(sc, MAX, 1.15, 15.1, pose(pack=1, ls=20, le=-150, lhand='open', yaw=-20), 'front', expr('confused', lx=-0.4, blink=blink_at(tt, [1.2])))
        sc.render(c)
        cut_flash(c, t, 6.6, color=(0.6, 0.65, 0.65))
        post(c, frame, vignette=0.7, grain=0.06)


# =============================================================================
# CLIP 10 - WARNING (the carved tree)
# =============================================================================
def render_10(c, t, frame, lang):
    if t < 3.4:
        u = ease_in_out(seg(t, 0, 3.4))
        cam = Camera(x=lerp(0.2, 0.6, u), y=1.45, z=9.6, yaw=0.30, focal=1350, horizon=0.48)
        big = (CARVED_TREE[0], CARVED_TREE[2], 24.0, 3, False)
        sc = Scene(cam, tod='morning', t=t, overgrown=True, extra_trees=[big], hide_trees_near=[(1.0, 11.5, 1.6)])
        walk = seg(t, 0.0, 2.4)
        hx = lerp(-0.6, 1.25, walk)
        p = walk_pose(t * 0.9, amount=1 - smooth(seg(t, 2.0, 2.5)), pack=1)
        if t > 2.4:
            p = pose_mix(p, pose(pack=1, head=-6, ls=30, le=40, lhand='open'), smooth(seg(t, 2.4, 3.2)))
        put_char(sc, HERO, hx, 13.75, p, 'side', expr('worried', blink=blink_at(t, [2.8])))
        sc.render(c)
        # carving glimpse on the trunk
        pr = cam.project(CARVED_TREE[0] - 0.05, 1.55, CARVED_TREE[2] - 0.3)
        if pr:
            c.save()
            c.translate(pr[0], pr[1])
            c.scale(pr[2] / 2600, pr[2] / 2600)
            draw_carving(c, 0, 0, size=150, lit=0.8)
            c.restore()
        post(c, frame, vignette=0.75, grain=0.06)
    else:
        tt = t - 3.4
        u = ease_in_out(seg(tt, 0, 5.6))
        z = lerp(1.0, 1.22, u)
        c.save()
        c.translate(W / 2, H / 2 + lerp(30, -20, u))
        c.scale(z, z)
        c.translate(-W / 2, -H / 2)
        draw_bark(c, -150, -150, W + 300, H + 300, seed=11, lit=0.75)
        draw_carving(c, W / 2, H * 0.48, size=165, lit=0.95)
        c.restore()
        # trunk curvature shading + cold light
        c.drawRect(skia.Rect(0, 0, W, H), paint(shader=lin_grad((0, 0), (W, 0), [(0, 0, 0, 0.75), (0, 0, 0, 0.0), (0, 0, 0, 0.0), (0, 0, 0, 0.8)], [0, 0.3, 0.65, 1])))
        c.drawRect(skia.Rect(0, 0, W, H), paint((0.55, 0.62, 0.62), alpha=0.16, blend=skia.BlendMode.kScreen))
        for i in range(5):
            y = H * (0.2 + 0.15 * i) + 40 * math.sin(tt * 0.4 + i)
            c.drawOval(skia.Rect(-300 + (tt * 40 + i * 200) % 600, y, 900 + (tt * 40 + i * 200) % 600, y + 220),
                       paint((0.7, 0.75, 0.75), alpha=0.05, blur=60))
        cut_flash(c, t, 3.4)
        post(c, frame, vignette=0.85, grain=0.07)


# =============================================================================
# CLIP 11 - PHONE MESSAGE
# =============================================================================
def render_11(c, t, frame, lang):
    defocus_forest(c, 'morning', t)
    c.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=0.35))
    u = ease_in_out(seg(t, 3.2, 9.5))
    z = lerp(1.0, 1.32, u)
    buzz = 0.0
    for b0, b1 in ((1.5, 2.1), (2.35, 2.95)):
        if b0 <= t <= b1:
            buzz = 1.0
    screen = 0.35 if t < 1.5 else 1.0
    notif = ease_out(seg(t, 2.9, 3.3))
    c.save()
    c.translate(W / 2, H * 0.5)
    c.scale(z, z)
    c.translate(0, lerp(0, 160, u))
    draw_phone(c, 0, 0, 1280, t, screen_on=screen, notif=notif, buzz=buzz, angle=-3 + 1.5 * math.sin(t * 0.6), time_text='6:42', skin=mix(HERO.skin, (0.35, 0.42, 0.5, 1), 0.45))
    c.restore()
    post(c, frame, vignette=0.85, grain=0.06)


# =============================================================================
# CLIP 12 - FINAL REVEAL
# =============================================================================
THREE = ((-2.9, 6.0), (0.7, 10.2), (4.4, 5.6))   # south of the clearing; the middle one is much closer
FOURTH_SIGHT = [(x, z, 1.4) for x, z in THREE] + [(0.4, 12.0, 1.2), (-1.3, 9.0, 1.0), (2.6, 8.0, 1.0)]


def render_12(c, t, frame, lang):
    if t < 3.0:
        u = ease_in_out(seg(t, 0, 3.0))
        defocus_forest(c, 'morning', t, seed=4)
        c.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=0.4))
        up = smooth(seg(t, 1.0, 2.0))
        e = expr_mix(expr('worried', ly=0.9, lx=0.0), expr('scared', ly=-0.35), up)
        e['blink'] = blink_at(t, [0.5])
        lt = Light(amb=(0.62, 0.68, 0.72), rim=hexc('#c9d3d2'), rim_side=-1, rim_k=0.35, shade=0.5, front=0.25 * (1 - up), front_col=(0.6, 0.7, 1.0))
        portrait(c, HERO, W * 0.5, H * lerp(0.47, 0.43, up), lerp(380, 470, u), yaw=0.0, e=e, light=lt, t=t, rot=lerp(0, -2, up))
        post(c, frame, vignette=0.85, grain=0.06)
    else:
        tt = t - 3.0
        u = ease_in_out(seg(tt, 0, 7.6))
        close = ease_in_out(seg(tt, 3.2, 7.6))   # push toward the closest figure
        cam = Camera(x=lerp(0.9, 0.8, close), y=1.55, z=lerp(16.6, 15.6, close), yaw=math.pi, focal=lerp(1150, 1650, u), horizon=0.47)
        sc = Scene(cam, tod='morning', t=t, overgrown=True, fog_mult=1.15, hide_trees_near=FOURTH_SIGHT,
                   extra_trees=[(CARVED_TREE[0], CARVED_TREE[2], 24.0, 3, False)])
        tilt = keys(tt, [(0, 5), (5.4, 5), (6.2, 24)])
        for i, (x, z) in enumerate(THREE):
            put_slender(sc, x, z, t, tilt=tilt, seed=0, extra_fog=-0.1 if i == 1 else 0.0)
        put_char(sc, HERO, 1.35, 14.2, pose(pack=1, ls=8, le=10), 'back', blur=5)
        put_char(sc, LENA, 0.25, 14.4, pose(pack=1, rs=-8, re=-20, head=-3), 'back', blur=3)
        sc.render(c)
        cut_flash(c, t, 3.0)
        post(c, frame, vignette=0.8 + 0.1 * u, grain=0.07)


# =============================================================================
# CLIP 07B - NO FACE (slow tilt up the Tall Man to the featureless head)
# =============================================================================
def render_07b(c, t, frame, lang):
    defocus_forest(c, 'night', t, seed=9)
    c.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=0.45))
    up = ease_in_out(seg(t, 0.0, 2.6))
    sc_ = lerp(900, 1500, ease_in_out(seg(t, 0, 5.4)))
    head_y = -2.69          # head centre in slender space
    focus_y = lerp(-2.0, head_y, up)
    c.save()
    c.translate(W / 2, H * 0.46 - focus_y * sc_)
    c.scale(sc_, sc_)
    lt = Light(amb=(0.50, 0.56, 0.72), rim=hexc('#a9c0e6'), rim_side=-1, rim_k=0.9, shade=0.6)
    draw_slender(c, t=t, tilt=keys(t, [(0, 4), (3.4, 4), (3.9, 15)]), sway=0.4, light=lt)
    c.restore()
    for i in range(3):   # drifting fog in front
        y = H * (0.25 + 0.25 * i) + 30 * math.sin(t * 0.5 + i)
        c.drawOval(skia.Rect(-300 + (t * 50 + i * 300) % 700, y, 900 + (t * 50 + i * 300) % 700, y + 260),
                   paint((0.5, 0.58, 0.7), alpha=0.06, blur=70))
    post(c, frame, vignette=1.0, grain=0.09)


# =============================================================================
# CLIP 13 - THE FOURTH (Lena whispers)
# =============================================================================
def render_13(c, t, frame, lang):
    defocus_forest(c, 'morning', t, seed=6)
    c.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=0.35))
    u = ease_in_out(seg(t, 0, 5.2))
    e = expr('scared', lx=keys(t, [(0, 0.2), (1.6, 0.2), (2.0, -0.85)]), ly=-0.1, blink=blink_at(t, [1.3]))
    talk = 2.1 <= t <= 4.2
    e['mouth'] = (0.12 + 0.22 * abs(math.sin(t * 13))) if talk else 0.12
    lt = Light(amb=(0.66, 0.70, 0.74), rim=hexc('#c9d3d2'), rim_side=-1, rim_k=0.4, shade=0.5)
    portrait(c, LENA, W * 0.52, H * 0.42, lerp(400, 470, u), yaw=keys(t, [(0, 0.1), (1.6, 0.1), (2.2, -0.3)]), e=e, light=lt, t=t)
    breath_puff(c, W * 0.45, H * 0.50, t, period=1.6, scale=0.8)
    post(c, frame, vignette=0.9, grain=0.06)


# =============================================================================
# CLIP 14 - EMPTY TENT (turn around, the tent is empty, hit, silence, end card)
# =============================================================================
def put_beanie(scene, x, z):
    def fn(c, pr):
        sx, sy, s, d = pr
        c.save()
        c.translate(sx, sy)
        c.scale(s, s)
        c.saveLayer(None, paint(cf=fog_filter(scene.pal['fog'], scene.fog_amount(d))))
        hat = mix(MAX.hat, (0.2, 0.25, 0.25, 1), 0.2)
        c.drawOval(skia.Rect(-0.13, -0.10, 0.13, 0.01), paint(hat))
        c.drawRect(skia.Rect(-0.13, -0.04, 0.13, 0.01), paint(mix(hat, (0, 0, 0, 1), 0.25)))
        c.drawOval(skia.Rect(-0.16, -0.01, 0.16, 0.03), paint((0, 0, 0), alpha=0.35, blur=0.02))
        c.restore()
        c.restore()
    scene.add(x, 0, z, fn)


def render_14(c, t, frame, lang):
    HIT = 7.4
    if t < 1.0:
        # whip turn: hero spins round, motion smear
        defocus_forest(c, 'morning', t * 3, seed=4)
        c.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=0.35))
        k = ease_in_out(seg(t, 0.1, 0.8))
        lt = Light(amb=(0.64, 0.7, 0.74), rim=hexc('#c9d3d2'), rim_side=-1, rim_k=0.35, shade=0.5)
        for i in range(4):
            off = (i - 1.5) * 60 * math.sin(math.pi * k)
            p = skia.Paint()
            p.setAlphaf(0.25 if i else 1.0)
            c.saveLayer(None, p)
            portrait(c, HERO, W * 0.5 - k * 900 + off, H * 0.43, 450, yaw=lerp(0.0, -0.6, k), e=expr('scared', lx=-0.9), light=lt, t=t)
            c.restore()
        post(c, frame, vignette=0.85, grain=0.06)
        return
    if t < HIT + 0.6:
        tt = t - 1.0
        u = ease_in_out(seg(tt, 0, HIT - 1.0))
        rush = ease_in(seg(t, HIT, HIT + 0.6))
        cam = Camera(x=lerp(0.4, -1.6, u) + 0.05 * math.sin(t * 50) * rush, y=1.45, z=lerp(14.6, 18.4, u) + 2.0 * rush,
                     yaw=lerp(-0.34, -0.19, u), focal=1300 + 900 * rush, horizon=0.5)
        sc = Scene(cam, tod='morning', t=t)
        put_fire(sc, t, 0.0, embers=0.0, smoke=0.15)
        put_tent(sc, t, door=1.0, wind=0.35, skew=0.3)
        put_beanie(sc, -1.85, 21.3)
        sc.render(c)
        if rush > 0:
            c.drawRect(skia.Rect(0, 0, W, H), paint((0, 0, 0), alpha=rush * 0.7))
        cut_flash(c, t, 1.0, 0.1)
        post(c, frame, vignette=0.8 + 0.1 * u, grain=0.07)
        return
    black(c)
    a = smooth(seg(t, HIT + 1.2, HIT + 1.9))
    txt = 'TO BE CONTINUED…' if lang == 'en' else 'ПРОДОЛЖЕНИЕ СЛЕДУЕТ…'
    draw_text(c, txt, W / 2, H * 0.5, 'dejavu/DejaVuSerif-Bold.ttf', 64 if lang == 'en' else 56, (0.85, 0.87, 0.9), alpha=a, spacing=4)
    draw_text(c, 'DIDAO', W / 2, H * 0.5 + 110, 'dejavu/DejaVuSans-Bold.ttf', 30, (0.55, 0.6, 0.65), alpha=a * 0.8, spacing=14)
    post(c, frame, vignette=0.0, grain=0.05)


RENDERERS = {1: render_01, 2: render_02, 3: render_03a, 30: render_03b, 4: render_04, 5: render_05, 6: render_06,
             7: render_07, 70: render_07b, 8: render_08, 9: render_09, 10: render_10, 11: render_11, 12: render_12,
             13: render_13, 14: render_14}
