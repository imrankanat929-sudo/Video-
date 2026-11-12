"""Shot list: every shot animates characters, camera and environment."""
import math
import random
import skia
import world
import hero
import bear
from world import Cam, render_world, trail_x, pal_mix, actor_tint_layer
from gfx import (W, H, paint, path_poly, path_smooth, ellipse, lin_grad, rad_grad, rgb, mix, lerp, clamp, smooth, ease_in_out,
                 ease_out, ease_in, remap, fbm, noise1, tint_filter)

# ------------------------------------------------------------------------------------------------
# global mood
# ------------------------------------------------------------------------------------------------
MOOD = [(0, 'day'), (15.5, 'day'), (24, 'tense'), (48, 'tense'), (66, 'dark'), (95, 'dark'), (101.5, 'tense'), (103.0, 'relief'), (120, 'relief')]


def pal_at(T):
    for (t0, a), (t1, b) in zip(MOOD, MOOD[1:]):
        if t0 <= T <= t1:
            return pal_mix(a, b, smooth((T - t0) / max(t1 - t0, 1e-6)))
    return world.PAL[MOOD[-1][1]]


def handheld(T, amp=6.0, rot=0.25, speed=0.6, seed=1):
    return (fbm(T * speed, seed) * amp, fbm(T * speed, seed + 5) * amp, fbm(T * speed * 0.8, seed + 9) * rot)


# ------------------------------------------------------------------------------------------------
# actors in world
# ------------------------------------------------------------------------------------------------
def actor(x, z, fn, extra_fog=0.0, darken=0.0, w=3.2, h=3.4):
    def draw(c, cam, pal):
        X, Y, s = cam.proj(x, 0, z)
        if Y < -200:
            return
        b = skia.Rect.MakeLTRB(X - w * s, Y - h * s, X + w * s, Y + 0.6 * s)

        def inner(cc):
            cc.save()
            cc.translate(X, Y)
            cc.scale(s / 100, s / 100)
            # contact shadow
            cc.drawOval(ellipse(0, 0, 70 * w / 1.6, 12), paint('#000000', 0.35, blur=8))
            fn(cc)
            cc.restore()
        actor_tint_layer(c, cam, pal, z, b, inner, extra_fog=extra_fog, darken=darken)
    return (z, draw)


def world_blurred(c, cam, pal, t, blur=6.0, actors=(), scale=3, **kw):
    """Render the world at 1/scale resolution and draw it blurred (depth of field background)."""
    surf = skia.Surface(W // scale, H // scale)
    cc = surf.getCanvas()
    cc.scale(1 / scale, 1 / scale)
    render_world(cc, cam, pal, t, actors=actors, **kw)
    img = surf.makeImageSnapshot()
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
    c.save()
    c.scale(scale, scale)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()


def light_wrap(c, pal, a=0.25):
    """Soft directional light from the sun side to tie characters into the scene."""
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=lin_grad((0, 0), (W, H * 0.6), [(*pal['sun'], a), (*pal['sun'], 0.0)]),
                                                    blend=skia.BlendMode.kSoftLight))


def char_tint(c, pal, fn, amount=0.6):
    """Draw character fn with the scene light colour (no fog)."""
    p = skia.Paint()
    light = tuple(lerp(1.0, l, amount) for l in pal['light'])
    p.setColorFilter(tint_filter(light, pal['fog'], 0.0, lerp(1.0, pal['sat'], amount)))
    c.saveLayer(None, p)
    fn(c)
    c.restore()


# ------------------------------------------------------------------------------------------------
# pictograms (example style)
# ------------------------------------------------------------------------------------------------
def icon_run(c, s=1.0):
    p = paint('#1b1b1f', stroke=9 * s)
    c.drawCircle(10 * s, -38 * s, 9 * s, paint('#1b1b1f'))
    c.drawLine(4 * s, -26 * s, -6 * s, 4 * s, p)
    c.drawLine(-6 * s, 4 * s, 14 * s, 16 * s, p)
    c.drawLine(14 * s, 16 * s, 10 * s, 36 * s, p)
    c.drawLine(-6 * s, 4 * s, -24 * s, 26 * s, p)
    c.drawLine(2 * s, -18 * s, 24 * s, -8 * s, p)
    c.drawLine(2 * s, -18 * s, -20 * s, -12 * s, p)


def icon_shout(c, s=1.0):
    c.drawOval(ellipse(-8 * s, 0, 22 * s, 26 * s), paint('#1b1b1f'))
    c.drawOval(ellipse(-8 * s, 4 * s, 12 * s, 14 * s), paint('#c0392b'))
    for k in range(3):
        r = (30 + k * 12) * s
        pth = skia.Path()
        pth.addArc(skia.Rect.MakeLTRB(-8 * s - r, -r, -8 * s + r, r), -35, 70)
        c.drawPath(pth, paint('#1b1b1f', stroke=5 * s))


def icon_hide(c, s=1.0):
    for (x, y, r) in ((-22, 8, 20), (0, -6, 24), (22, 8, 20), (0, 16, 22)):
        c.drawCircle(x * s, y * s, r * s, paint('#2f6b33'))
    c.drawCircle(10 * s, -2 * s, 4 * s, paint('#1b1b1f'))
    c.drawCircle(-4 * s, -2 * s, 4 * s, paint('#1b1b1f'))


def icon_step(c, s=1.0):
    for (x, y) in ((-14, 20), (12, -12)):
        c.drawOval(ellipse(x * s, y * s, 9 * s, 15 * s), paint('#1b1b1f'))
        for k in range(4):
            c.drawCircle((x - 7 + k * 4.5) * s, (y - 19) * s, 2.6 * s, paint('#1b1b1f'))
    c.drawLine(-30 * s, -30 * s, -4 * s, -30 * s, paint('#1b1b1f', stroke=5 * s))
    c.drawPath(path_poly([(0, -30 * s), (-10 * s, -38 * s), (-10 * s, -22 * s)]), paint('#1b1b1f'))


def icon_food(c, s=1.0):
    c.drawCircle(0, 6 * s, 26 * s, paint('#d23b2f'))
    c.drawOval(ellipse(-9 * s, -2 * s, 7 * s, 10 * s), paint('#ffffff', 0.45))
    c.drawLine(0, -18 * s, 4 * s, -34 * s, paint('#4a3020', stroke=5 * s))
    c.drawOval(ellipse(14 * s, -28 * s, 12 * s, 6 * s), paint('#3d8a3a'))


def icon_voice(c, s=1.0):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-34 * s, -24 * s, 34 * s, 20 * s), 14 * s, 14 * s)
    c.drawRRect(r, paint('#1b1b1f'))
    c.drawPath(path_poly([(-14 * s, 18 * s), (-24 * s, 36 * s), (0, 18 * s)]), paint('#1b1b1f'))
    for k, hh in enumerate((8, 16, 10, 18, 8)):
        x = (-20 + k * 10) * s
        c.drawLine(x, -hh / 2 * s - 2 * s, x, hh / 2 * s - 2 * s, paint('#ffffff', stroke=4 * s))


def icon_bubble(c, x, y, r, icon, appear=1.0, cross=0.0, t=0.0, tail=(0, 0)):
    if appear <= 0:
        return
    k = ease_out(appear)
    sc = 0.5 + 0.5 * k + 0.08 * math.sin(clamp(appear) * math.pi)
    c.save()
    c.translate(x, y + math.sin(t * 2.2) * 4)
    c.scale(sc, sc)
    # cloud
    pth = skia.Path()
    for i in range(9):
        a = i / 9 * math.pi * 2
        pth.addCircle(math.cos(a) * r * 0.78, math.sin(a) * r * 0.62, r * 0.42)
    pth.addOval(ellipse(0, 0, r * 0.9, r * 0.72))
    c.drawPath(pth, paint('#000000', 0.25 * k, blur=10))
    c.drawPath(pth, paint('#ffffff', k))
    if tail != (0, 0):
        tx, ty = tail
        c.drawCircle(tx * 0.55, ty * 0.55, r * 0.14, paint('#ffffff', k))
        c.drawCircle(tx * 0.85, ty * 0.85, r * 0.08, paint('#ffffff', k))
    c.save()
    c.scale(r / 60, r / 60)
    icon(c, 1.0)
    c.restore()
    if cross > 0:
        cl = ease_out(cross)
        p = paint('#e53935', stroke=r * 0.16)
        c.drawLine(-r * 0.55, -r * 0.55, lerp(-r * 0.55, r * 0.55, cl), lerp(-r * 0.55, r * 0.55, cl), p)
        if cross > 0.5:
            c2 = ease_out((cross - 0.5) * 2)
            c.drawLine(r * 0.55, -r * 0.55, lerp(r * 0.55, -r * 0.55, c2), lerp(-r * 0.55, r * 0.55, c2), p)
    c.restore()


def birds(c, t, x0=0, y0=300, n=5, scale=1.0):
    for i in range(n):
        x = (x0 + t * (60 + i * 6) + i * 70) % (W + 300) - 150
        y = y0 + i * 26 + math.sin(t * 0.7 + i) * 12
        fl = math.sin(t * 9 + i * 1.3)
        s = scale * (0.8 + 0.1 * i)
        pth = skia.Path()
        pth.moveTo(x - 14 * s, y - 6 * s * fl)
        pth.quadTo(x - 6 * s, y - 2 * s, x, y + 2 * s)
        pth.quadTo(x + 6 * s, y - 2 * s, x + 14 * s, y - 6 * s * fl)
        c.drawPath(pth, paint('#2a2a2a', 0.75, stroke=3 * s))


def vapor(c, x, y, t, s=1.0, a=0.35):
    ph = (t * 0.55) % 1.0
    c.drawOval(ellipse(x - ph * 40 * s, y - ph * 20 * s, (20 + ph * 50) * s, (12 + ph * 25) * s), paint('#e8ecec', a * (1 - ph), blur=14 * s))


def dust(c, x, y, t, s=1.0, a=0.5, seed=1):
    rng = random.Random(seed)
    for i in range(14):
        ph = clamp(t)
        dx = rng.uniform(-1, 1) * 160 * s * ph
        dy = -rng.uniform(0.2, 1) * 70 * s * ph
        r = (18 + rng.uniform(0, 30) * ph) * s
        c.drawCircle(x + dx, y + dy, r, paint('#b19a76', a * (1 - ph) * 0.6, blur=10 * s))


def ground_closeup(c, pal, t, horizon=0.55, seed=4):
    """A low, near ground plane for macro shots: leaf litter, needles, twigs."""
    rng = random.Random(seed)
    c.drawRect(skia.Rect.MakeLTRB(0, H * horizon - 60, W, H), paint(shader=lin_grad((0, H * horizon - 60), (0, H), [(*mix(pal['ground_far'], pal['fog'], 0.5), 0.0), (*mix(pal['ground_far'], pal['fog'], 0.3), 1.0), pal['ground']], [0, 0.1, 1])))
    for i in range(260):
        u = rng.random() ** 0.7
        y = lerp(H * horizon, H + 40, u)
        x = rng.uniform(-40, W + 40)
        s = lerp(0.3, 3.2, u)
        colr = ['#8a5a2a', '#a8742e', '#6b4a24', '#5a5a2a', '#7a6a3a'][i % 5]
        c.save()
        c.translate(x, y)
        c.rotate(rng.uniform(0, 180))
        cc = mix(rgb(colr), pal['fog'], (1 - u) * 0.6)
        cc = tuple(cc[k] * pal['light'][k] for k in range(3))
        c.drawOval(ellipse(0, 0, 12 * s, 5 * s), paint(cc, 0.95))
        c.drawLine(-10 * s, 0, 10 * s, 0, paint(mix(cc, (0, 0, 0), 0.3), 0.6, stroke=0.8 * s))
        c.restore()


# ------------------------------------------------------------------------------------------------
# helper: hero/bear quick constructors
# ------------------------------------------------------------------------------------------------
def hero_back(phase=0.0, standing=False, head_turn=0.0, t=0.0, speed=1.0):
    return lambda c: hero.draw_back(c, phase=phase, standing=standing, head_turn=head_turn, t=t, speed=speed)


def hero_front(ex='calm', t=0.0, step=0.0, talk=0.0, arms_out=0.0, blink=0.0, look=(0, 0)):
    exd = hero.EXPR[ex] if isinstance(ex, str) else ex
    return lambda c: hero.draw_front(c, ex=exd, t=t, step=step, talk=talk, arms_out=arms_out, blink=blink, look=look, breathe=1.0)


def blink_at(t, period=3.7, seed=0):
    ph = (t + seed * 1.3) % period
    return clamp(1 - abs(ph - 0.08) / 0.08) if ph < 0.16 else 0.0


HERO_SPEED = 1.25  # m/s
STRIDE = 1.35      # metres per walk cycle


# ------------------------------------------------------------------------------------------------
# SHOTS
# each: fn(c, lt, T, d)
# ------------------------------------------------------------------------------------------------
def s_aerial(c, lt, T, d):
    pal = pal_at(T)
    u = ease_in_out(lt / d)
    z_hero = 30 + T * HERO_SPEED
    cz = lerp(-20, z_hero - 7.5, u ** 0.9)
    cam = Cam(x=trail_x(cz), y=lerp(36, 2.2, u ** 1.15), z=cz, hy=lerp(H * 0.27, H * 0.44, u), f=1150)
    sx, sy, r = handheld(T, 2, 0.05)
    cam.sx, cam.sy = sx, sy
    hz = z_hero
    act = [actor(trail_x(hz), hz, hero_back(phase=hz / STRIDE, t=T))]
    render_world(c, cam, pal, T, actors=act, mountains=True, zfar=lerp(120, 62, u), rays=1.2, leaves=3)
    birds(c, T, x0=-200, y0=lerp(260, -200, u), n=6, scale=1.2)


def s_follow(c, lt, T, d):
    pal = pal_at(T)
    hz = 30 + T * HERO_SPEED
    cz = hz - 4.0 + 0.3 * math.sin(T * 0.4)
    cam = Cam(x=trail_x(cz) * 0.4 + trail_x(hz) * 0.6 + 0.35, y=1.85 + 0.04 * math.sin(T * 4.6), z=cz, hy=H * 0.43)
    sx, sy, r = handheld(T, 5, 0.2)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    act = [actor(trail_x(hz), hz, hero_back(phase=hz / STRIDE, t=T))]
    render_world(c, cam, pal, T, actors=act, rays=1.2)


def s_front_walk(c, lt, T, d):
    """Hero walks toward camera, camera dollies back - calm, earbuds (listening to music)."""
    pal = pal_at(T)
    # walking along -z? we keep camera looking +z: hero faces camera, so walk toward camera means z decreasing.
    hz = 140 - lt * 1.15
    cz = hz - 3.6 - lt * 0.05
    cam = Cam(x=trail_x(hz) + 0.15, y=1.55, z=cz, hy=H * 0.42, f=1250)
    sx, sy, r = handheld(T, 4, 0.15)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    ph = lt * 1.15 / STRIDE
    ex = hero.expr_mix('calm', 'relief', 0.0)
    nod = 0.5 + 0.5 * math.sin(T * 6.3)

    def fn(cc):
        hero.draw_front(cc, ex=ex, t=T, step=ph, blink=blink_at(T), look=(0.2 * math.sin(T * 0.8), 0), breathe=1.0)
    act = [actor(trail_x(hz), hz, fn)]
    render_world(c, cam, pal, T, actors=act, rays=1.1)
    # floating music notes (listening to music)
    X, Y, s = cam.proj(trail_x(hz), 1.75, hz)
    for k in range(3):
        ph2 = (lt * 0.45 + k / 3) % 1.0
        x = X + s * 0.32 + ph2 * 90 + 18 * math.sin(T * 2 + k)
        y = Y - ph2 * 160
        a = math.sin(ph2 * math.pi) * 0.9
        c.drawCircle(x, y, 9, paint('#ffffff', a))
        c.drawLine(x + 8, y, x + 8, y - 34, paint('#ffffff', a, stroke=4))
        c.drawLine(x + 8, y - 34, x + 20, y - 26, paint('#ffffff', a, stroke=4))


def foreground_leaves(c, t, a=1.0, side='both', seed=7, dark=0.0):
    rng = random.Random(seed)
    p_col = mix(rgb('#0e1a10'), (0, 0, 0), dark)
    for i in range(16):
        left = i % 2 == 0
        if side == 'left' and not left or side == 'right' and left:
            continue
        x = (rng.uniform(-150, 260) if left else rng.uniform(W - 260, W + 150))
        y = rng.uniform(-100, H + 100)
        ang = rng.uniform(0, 360) + 6 * math.sin(t * 0.9 + i)
        L = rng.uniform(260, 520)
        c.save()
        c.translate(x + 10 * math.sin(t * 0.6 + i), y)
        c.rotate(ang)
        pth = path_smooth([(0, 0), (L * 0.5, -L * 0.18), (L, 0), (L * 0.5, L * 0.18)], tension=0.5)
        c.drawPath(pth, paint(p_col, a, blur=14))
        c.restore()


def s_watcher(c, lt, T, d):
    """POV from bushes: someone is watching."""
    pal = pal_at(T)
    hz0 = 30 + T * HERO_SPEED
    cz = hz0 - 16
    cam = Cam(x=trail_x(hz0) - 3.2, y=0.9, z=cz, hy=H * 0.47, f=1500)
    sx, sy, r = handheld(T, 7, 0.3, speed=0.35, seed=4)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    act = [actor(trail_x(hz0), hz0, lambda cc: hero.draw_side(cc, phase=hz0 / STRIDE, t=T, dirn=1, look=0))]
    world_blurred(c, cam, pal, T, blur=1.2, actors=act, scale=2)
    # breathing foreground branches (blurred, dark)
    foreground_leaves(c, T, a=0.96, seed=11)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=rad_grad((W / 2, H * 0.48), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.55)])))


def s_branch(c, lt, T, d):
    """Close-up: a dry branch snaps on the forest floor."""
    pal = pal_at(T)
    snap = 0.22
    k = clamp((lt - snap) / 0.25)
    shake = (1 - clamp((lt - snap) / 0.5)) * (lt > snap) * 18
    c.save()
    c.translate(math.sin(lt * 80) * shake, math.cos(lt * 70) * shake * 0.6)
    c.translate(W / 2, H * 0.6)
    c.scale(1 + lt * 0.05, 1 + lt * 0.05)
    c.translate(-W / 2, -H * 0.6)
    cam = Cam(x=trail_x(240), y=0.5, z=240, hy=H * 0.5, f=900)
    world_blurred(c, cam, pal, T, blur=9, scale=4, particles=False)
    ground_closeup(c, pal, T, horizon=0.44)
    # shadow passing
    c.drawOval(ellipse(W * 0.5 + 200 - lt * 300, H * 0.66, 520, 160), paint('#000000', 0.35 * clamp(lt / 0.3), blur=60))
    # branch: two halves pivoting at middle
    cx, cy = W * 0.52, H * 0.66
    bend = ease_out(k) * 26
    for side in (-1, 1):
        c.save()
        c.translate(cx, cy)
        c.rotate(-side * bend)
        L = 520
        pth = path_smooth([(0, -16), (side * L * 0.5, -19), (side * L, -10), (side * L, 10), (side * L * 0.5, 16), (0, 16)], tension=0.3)
        c.drawPath(pth, paint(shader=lin_grad((0, -12), (0, 12), ['#a07a4e', '#6e4e30', '#4a3420'])))
        c.drawLine(side * L * 0.35, -8, side * L * 0.55, -60, paint('#6e4e30', stroke=8))
        if k > 0:
            for j in range(5):
                c.drawLine(0, -6 + j * 3, side * (10 + j * 5) * k, -14 + j * 6, paint('#e0c49a', 0.9, stroke=3))
        c.restore()
    # splinters & dust
    if lt > snap:
        rng = random.Random(3)
        for j in range(16):
            vx, vy = rng.uniform(-500, 500), rng.uniform(-700, -200)
            tt = lt - snap
            x = cx + vx * tt
            y = cy + vy * tt + 1400 * tt * tt
            c.drawLine(x, y, x + 10, y - 4, paint('#d9b98a', clamp(1 - tt * 1.5), stroke=4))
        dust(c, cx, cy, (lt - snap) * 1.4, s=1.4, a=0.6)
    c.restore()


def s_turn_head(c, lt, T, d):
    """Hero stops, turns his head toward the sound."""
    pal = pal_at(T)
    k = ease_out(remap(lt, 0.1, 0.6))
    cam = Cam(x=0.0, y=1.6, z=T * HERO_SPEED + 20, hy=H * 0.40, f=1200)
    world_blurred(c, cam, pal, T, blur=7, scale=3)
    ex = hero.expr_mix('calm', 'surprised', k)

    def fn(cc):
        cc.translate(W * 0.48 - k * 40, H * 0.36)
        cc.scale(1.9, 1.9)
        hero.draw_bust(cc, ex, turn=lerp(-0.1, 0.55, k), look=(lerp(0, 1, k), 0), t=T, blink=0, breathe=0.4)
    char_tint(c, pal, fn)
    light_wrap(c, pal)


def s_bear_reveal(c, lt, T, d):
    """Whip-pan to the bushes: a big bear silhouette deep in the forest."""
    pal = pal_at(T)
    whip = 1 - ease_out(clamp(lt / 0.35))
    zb = 90 + 24
    cam = Cam(x=trail_x(90) + 0.4 + whip * 6, y=1.6, z=90, hy=H * 0.44, f=lerp(1300, 1700, ease_in_out(lt / d)))
    sx, sy, r = handheld(T, 4, 0.12, seed=8)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    emerge = smooth(remap(lt, 0.6, 3.0))
    bx = trail_x(zb) + 4.6 - emerge * 1.0
    act = [actor(bx, zb, lambda cc: bear.draw_side(cc, phase=0, gait='stand', t=T, head_lift=0.1 * emerge), extra_fog=0.25 * (1 - emerge), darken=0.35)]
    if whip > 0.02:
        surf = skia.Surface(W, H)
        render_world(surf.getCanvas(), cam, pal, T, actors=act, rays=0.6, fog=1.4)
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(90 * whip, 2))
        c.drawImage(surf.makeImageSnapshot(), 0, 0, skia.SamplingOptions(), p)
    else:
        render_world(c, cam, pal, T, actors=act, rays=0.6, fog=1.4)
    # eye glint
    X, Y, s = cam.proj(bx + 1.05, 1.18, zb)
    gl = smooth(remap(lt, 1.6, 2.2)) * (0.6 + 0.4 * math.sin(T * 3))
    c.drawCircle(X, Y, 3 + s * 0.02, paint('#f6e7b0', gl, blur=2))


def s_ots_bear(c, lt, T, d):
    """Over-the-shoulder: hero back in foreground, bear stands on the trail a few dozen metres ahead."""
    pal = pal_at(T)
    hz = 200.0
    bz = hz + 16
    u = ease_in_out(lt / d)
    cam = Cam(x=trail_x(hz) - 0.75, y=1.75, z=hz - 2.6 + u * 0.5, hy=H * 0.42, f=1250 + u * 120)
    sx, sy, r = handheld(T, 4, 0.15, seed=2)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    act = [actor(trail_x(hz) - 0.1, hz, hero_back(standing=True, t=T, head_turn=0.0)),
           actor(trail_x(bz), bz, lambda cc: bear.draw_front(cc, phase=0, t=T, moving=False, sniff=0.3), darken=0.1)]
    render_world(c, cam, pal, T, actors=act, rays=0.8)


def s_hero_freeze(c, lt, T, d):
    pal = pal_at(T)
    cam = Cam(x=trail_x(200) + 1, y=1.6, z=170, hy=H * 0.40, f=1200)
    world_blurred(c, cam, pal, T, blur=8, scale=3)
    k = ease_out(remap(lt, 0.0, 0.5))
    ex = hero.expr_mix('surprised', 'fear', k)
    tremble = 1.0

    def fn(cc):
        cc.translate(W * 0.5 + math.sin(T * 40) * 1.5 * tremble, H * 0.37)
        sc = 2.15 + lt * 0.06
        cc.scale(sc, sc)
        hero.draw_bust(cc, ex, turn=0.12, look=(0.6, -0.1), t=T, breathe=0.15)
    char_tint(c, pal, fn)
    light_wrap(c, pal, 0.18)


def s_bear_eye(c, lt, T, d):
    pal = pal_at(T)
    c.save()
    sc = 1.0 + lt * 0.05
    c.translate(W / 2, H * 0.42)
    c.scale(sc, sc)
    c.scale(1.25, 1.25)
    b = clamp(1 - abs(lt - 0.6) / 0.12)
    bear.draw_eye_closeup(c, t=T, blink=b, look=lerp(0.4, -0.5, smooth(remap(lt, 0.9, 1.5))), dilate=smooth(remap(lt, 1.2, 2.0)))
    c.restore()
    p = skia.Paint()
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=rad_grad((W / 2, H * 0.42), H * 0.6, [(0, 0, 0, 0), (0, 0, 0, 0.7)])))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(tuple(pal['light']), 0.08, blend=skia.BlendMode.kMultiply))


def s_bear_sniff(c, lt, T, d):
    pal = pal_at(T)
    cam = Cam(x=trail_x(200) - 2, y=1.2, z=180, hy=H * 0.5, f=1000)
    world_blurred(c, cam, pal, T, blur=9, scale=3)
    lift = ease_in_out(remap(lt, 0.2, 1.4))

    def fn(cc):
        cc.translate(W * 0.58, H * 0.47)
        sc = 1.25 + lt * 0.03
        cc.scale(sc, sc)
        cc.rotate(-lift * 10 + math.sin(T * 1.3) * 1.2)
        bear.draw_closeup(cc, t=T, sniff=0.3 + 0.7 * lift, blink=blink_at(T, 4.1, 2), nose_twitch=math.sin(T * 13) * lift)
        vapor(cc, -280, 60, T, s=2.0, a=0.18)
    char_tint(c, pal, fn, amount=0.8)
    light_wrap(c, pal, 0.15)


def paws(c, pal, t, phase, gait='walk', scale=5.5, x0=W * 0.5, ground=H * 0.86, seed=2, near_only=False):
    """Low macro view: the bear's front legs, chest and paws on the forest floor (same rig as wide shots)."""
    c.save()
    c.translate(x0, ground)
    c.scale(scale, scale)
    c.translate(-45, 0)
    bear.draw_side(c, phase=phase, gait=gait, t=t, head_lift=0.0)
    c.restore()


def s_paws(c, lt, T, d, gait='stand', speed=1.0, seed=2):
    pal = pal_at(T)
    c.save()
    cam = Cam(x=trail_x(260), y=0.5, z=260, hy=H * 0.5, f=900)
    world_blurred(c, cam, pal, T, blur=9, scale=4, particles=False)
    ground_closeup(c, pal, T, horizon=0.5, seed=seed)

    def fn(cc):
        ph = lt * (0.6 if gait == 'walk' else 1.8) * speed
        paws(cc, pal, T, ph, gait=gait, scale=9.0, x0=W * 0.42 - (lt * 160 if gait != 'stand' else 0), ground=H * 0.9)
    char_tint(c, pal, fn, amount=0.8)
    # kicked leaves when paw lands
    if gait != 'stand':
        ph = (lt * (0.6 if gait == 'walk' else 1.8) * speed) % 1.0
        dust(c, W * 0.55, H * 0.86, ph * 2, s=1.0, a=0.5)
    c.restore()


def s_fear_ecu(c, lt, T, d, groups=None):
    """Extreme close-up of the face, heartbeat push-in; thought bubbles with options."""
    pal = pal_at(T)
    cam = Cam(x=trail_x(200) + 0.5, y=1.6, z=175, hy=H * 0.45, f=1200)
    world_blurred(c, cam, pal, T, blur=10, scale=3)
    beat = math.exp(-((T * 1.25) % 1.0) * 7)
    sc = 2.9 + lt * 0.05 + beat * 0.02
    eye_dart = 0.4 * math.sin(T * 1.7) + 0.3 * noise1(T * 2, 3)

    def fn(cc):
        cc.translate(W * 0.5, H * 0.40)
        cc.scale(sc, sc)
        hero.draw_bust(cc, hero.EXPR['fear'], turn=0.05, look=(eye_dart, 0), t=T, blink=blink_at(T, 3.1), breathe=0.4)
    char_tint(c, pal, fn)
    light_wrap(c, pal, 0.12)
    # thought bubbles: run? scream? hide?  (times from VO 'what' group)
    if groups:
        g = groups.get('what')
        m = groups.get('main')
        if g:
            ws = g['words']
            times = [ws[min(i, len(ws) - 1)][1] for i in _option_word_idx(ws)]
            spots = [(170, H * 0.24), (W - 170, H * 0.24), (170, H * 0.45)]
            icons = [icon_run, icon_shout, icon_hide]
            for (x, y), ic, t0 in zip(spots, icons, times):
                ap = clamp((T - t0 + 0.05) / 0.3)
                cross = 0.0
                if m:
                    cross = clamp((T - m['dst_start'] - 0.4) / 0.5)
                fade = 1 - clamp((T - (m['dst_end'] if m else 99) - 0.6) / 0.4)
                if ap > 0 and fade > 0:
                    c.save()
                    c.saveLayerAlpha(None, int(255 * fade))
                    icon_bubble(c, x, y, 88, ic, appear=ap, cross=cross, t=T)
                    c.restore()
                    c.restore()


def _option_word_idx(ws):
    """indices of the 3 option words (run/scream/hide) - the last three question starts."""
    starts = [0]
    for i, (w, s, e) in enumerate(ws):
        if w.endswith('?') and i + 1 < len(ws):
            starts.append(i + 1)
    return starts[-3:] if len(starts) >= 4 else starts[1:4]


def s_two_shot(c, lt, T, d):
    """Profile: hero left foreground (side, facing right), bear far right; heavy stillness."""
    pal = pal_at(T)
    u = ease_in_out(lt / d)
    hz = 300.0
    cam = Cam(x=trail_x(hz + 6) - 1.0 - u * 0.6, y=1.4, z=hz - 3.2 + u * 0.3, hy=H * 0.44, f=1150)
    sx, sy, r = handheld(T, 3, 0.1, seed=12)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    bz = hz + 15
    act = [actor(trail_x(hz) - 0.9, hz, lambda cc: hero.draw_side(cc, standing=True, ex=hero.EXPR['cautious'], t=T, dirn=1, look=0.5)),
           actor(trail_x(bz) + 0.6, bz, lambda cc: bear.draw_side(cc, gait='stand', t=T, head_lift=0.4 + 0.2 * math.sin(T * 0.7), sniff=0.6, breath=1), darken=0.05, w=3.0)]
    render_world(c, cam, pal, T, actors=act, rays=0.5, fog=1.2)


def s_bear_approach(c, lt, T, d, speed=0.55, gait='walk', start=13.0, low=True, shake=0.0):
    pal = pal_at(T)
    bz0 = 400 + start
    bz = bz0 - lt * speed * (3.5 if gait == 'run' else 1.4)
    cz = 400 - (lt * 0.3 if not shake else 0)
    cam = Cam(x=trail_x(bz) + 0.2, y=0.55 if low else 1.6, z=cz, hy=H * (0.52 if low else 0.44), f=1150)
    sx, sy, r = handheld(T, 4 + shake * 14, 0.15 + shake * 0.6, speed=0.6 + shake, seed=6)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    ph = lt * (0.55 if gait == 'walk' else 1.6) * (speed / 0.55 if gait == 'walk' else 1)
    act = [actor(trail_x(bz), bz, lambda cc: bear.draw_front(cc, phase=ph, t=T, moving=True, gait=gait, sniff=0.2))]
    render_world(c, cam, pal, T, actors=act, rays=0.4, fog=1.1, wind=1.4 if shake else 1.0)
    if gait == 'run':
        X, Y, s = cam.proj(trail_x(bz), 0, bz)
        dust(c, X, Y, (ph % 1.0) * 1.5, s=s / 200, a=0.6, seed=int(ph))


def s_rules(c, lt, T, d, groups=None):
    """Hero stands still, hands low, does not approach; pictograms: no stepping closer, no feeding."""
    pal = pal_at(T)
    hz = 500.0
    u = ease_in_out(lt / d)
    cam = Cam(x=trail_x(hz) + 0.1, y=1.25, z=hz - 3.0 + u * 0.4, hy=H * 0.44, f=1200)
    sx, sy, r = handheld(T, 3, 0.1, seed=14)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    act = [actor(trail_x(hz), hz, hero_front('cautious', t=T, blink=blink_at(T), look=(0, 0)))]
    render_world(c, cam, pal, T, actors=act, rays=0.5)
    if groups and 'advice1' in groups:
        ws = groups['advice1']['words']
        n = len(ws)
        t_step = ws[0][1]
        t_food = ws[min(n - 1, int(n * 0.55))][1]
        for (x, y, ic, t0) in ((W * 0.25, H * 0.2, icon_step, t_step), (W * 0.75, H * 0.2, icon_food, t_food)):
            ap = clamp((T - t0) / 0.3)
            if ap > 0:
                icon_bubble(c, x, y, 105, ic, appear=ap, cross=clamp((T - t0 - 0.45) / 0.5), t=T)


def s_speak(c, lt, T, d, groups=None):
    pal = pal_at(T)
    cam = Cam(x=trail_x(500) + 1, y=1.6, z=480, hy=H * 0.42, f=1200)
    world_blurred(c, cam, pal, T, blur=8, scale=3)
    # mouth moves like talking calmly
    talk = max(0.0, math.sin(T * 9.0)) * 0.35 * (0.6 + 0.4 * math.sin(T * 2.3)) if lt > 0.3 else 0.0

    def fn(cc):
        cc.translate(W * 0.46, H * 0.38)
        cc.scale(2.0, 2.0)
        hero.draw_bust(cc, hero.EXPR['speak'], turn=0.3, look=(0.7, 0), talk=talk, t=T, blink=blink_at(T, 3.3), breathe=0.6)
    char_tint(c, pal, fn)
    light_wrap(c, pal, 0.15)
    ap = clamp((lt - 0.4) / 0.3)
    icon_bubble(c, W * 0.8, H * 0.2, 95, icon_voice, appear=ap, t=T)


def s_gap_wide(c, lt, T, d):
    """High wide: the forest between them, fog drifting."""
    pal = pal_at(T)
    u = ease_in_out(lt / d)
    hz = 600.0
    bz = hz + 14
    cam = Cam(x=trail_x(hz + 5), y=lerp(3.0, 5.5, u), z=hz - 5.5 - u * 1.0, hy=H * lerp(0.36, 0.30, u), f=1150)
    act = [actor(trail_x(hz), hz, lambda cc: hero.draw_back(cc, standing=True, t=T)),
           actor(trail_x(bz), bz, lambda cc: bear.draw_front(cc, phase=lt * 0.3, t=T, moving=True), darken=0.05)]
    render_world(c, cam, pal, T, actors=act, rays=0.4, fog=1.5)
    # distance line between them
    X1, Y1, s1 = cam.proj(trail_x(hz), 0, hz)
    X2, Y2, s2 = cam.proj(trail_x(bz), 0, bz)
    a = clamp((lt - 0.5) / 0.5) * 0.9
    p = paint('#ffd400', a, stroke=5)
    p.setPathEffect(skia.DashPathEffect.Make([18, 14], -T * 40))
    c.drawLine(X1, Y1 - 10, X2, Y2 + 10, p)


def s_back_away(c, lt, T, d):
    """Hero slowly increases distance, steps off the trail so the bear's path stays free."""
    pal = pal_at(T)
    hz0 = 700.0
    u = ease_in_out(lt / d)
    hz = hz0 - u * 2.2
    hx = trail_x(hz0) + u * 2.0
    bz = hz0 + 13
    cam = Cam(x=trail_x(hz0) + 0.9, y=1.7, z=hz0 - 5.8, hy=H * 0.42, f=1150)
    sx, sy, r = handheld(T, 3, 0.1, seed=15)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    step = lt * 0.45

    def hfn(cc):
        hero.draw_front(cc, ex=hero.EXPR['cautious'], t=T, step=step, arms_out=0.2, blink=blink_at(T), look=(0, 0), breathe=1)
    act = [actor(hx, hz, hfn), actor(trail_x(bz), bz, lambda cc: bear.draw_front(cc, phase=0, t=T, moving=False, sniff=0.4), darken=0.1)]
    render_world(c, cam, pal, T, actors=act, rays=0.35)
    # free path arrow for the bear along the trail + distance meter
    a = clamp((lt - 0.8) / 0.5) * 0.95
    if a > 0:
        pts = []
        for k in range(12):
            z = bz - 1 - k * 1.0
            X, Y, s = cam.proj(trail_x(z), 0.05, z)
            pts.append((X, Y))
        p = paint('#ffd400', a, stroke=7)
        p.setPathEffect(skia.DashPathEffect.Make([22, 16], -T * 60))
        c.drawPath(path_smooth(pts, close=False), p)
        X1, Y1, s1 = cam.proj(hx, 0, hz)
        X2, Y2, s2 = cam.proj(trail_x(bz), 0, bz)
        # double arrow
        q = paint('#ffffff', a, stroke=5)
        c.drawLine(X1, Y1 - 30, X2, Y2 - 30, q)


def s_bear_head_low(c, lt, T, d):
    pal = pal_at(T)
    hz = 720.0
    cam = Cam(x=trail_x(hz), y=1.0, z=hz - 4.5 - lt * 0.2, hy=H * 0.47, f=1600)
    sx, sy, r = handheld(T, 3, 0.1, seed=16)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    k = ease_in_out(lt / d)
    act = [actor(trail_x(hz), hz, lambda cc: bear.draw_front(cc, phase=0, t=T, moving=False, sniff=1.0, head_lift=-k * 1.0))]
    render_world(c, cam, pal, T, actors=act, rays=0.3, fog=1.1)
    X, Y, s = cam.proj(trail_x(hz), 1.1, hz)
    vapor(c, X - 10, Y + 40, T, s=s / 400, a=0.25)


def s_hero_serious(c, lt, T, d):
    pal = pal_at(T)
    cam = Cam(x=trail_x(760), y=1.6, z=740, hy=H * 0.45, f=1200)
    world_blurred(c, cam, pal, T, blur=10, scale=3)
    beat = math.exp(-((T * 1.9) % 1.0) * 7)
    sx, sy, r = handheld(T, 6, 0.3, seed=17, speed=1.2)

    def fn(cc):
        cc.translate(W * 0.5 + sx, H * 0.40 + sy)
        sc = 2.5 + lt * 0.12 + beat * 0.03
        cc.scale(sc, sc)
        hero.draw_bust(cc, hero.expr_mix('fear', 'cautious', 0.35), turn=-0.1, look=(-0.3, 0), t=T, breathe=1.6, blink=blink_at(T, 2.4))
    char_tint(c, pal, fn)
    light_wrap(c, pal, 0.1)


def s_bear_run_side(c, lt, T, d):
    pal = pal_at(T)
    bz = 820.0
    bx = trail_x(bz) - 7 + lt * 9.0
    cam = Cam(x=bx - 0.6, y=0.8, z=bz - 5.5, hy=H * 0.5, f=1150)
    sx, sy, r = handheld(T, 10, 0.5, seed=18, speed=1.6)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    ph = lt * 2.0
    act = [actor(bx, bz, lambda cc: bear.draw_side(cc, phase=ph, gait='run', t=T))]
    render_world(c, cam, pal, T, actors=act, rays=0.25, wind=2.0, leaves=14)
    X, Y, s = cam.proj(bx - 1.0, 0, bz)
    dust(c, X, Y, (ph % 1.0) * 1.5, s=s / 150, a=0.7, seed=int(ph * 2))


def s_hero_hold(c, lt, T, d, fear=0.7):
    pal = pal_at(T)
    cam = Cam(x=trail_x(850), y=1.6, z=830, hy=H * 0.45, f=1200)
    world_blurred(c, cam, pal, T, blur=11, scale=3)
    sx, sy, r = handheld(T, 9, 0.4, seed=19, speed=1.8)

    def fn(cc):
        cc.translate(W * 0.5 + sx, H * 0.39 + sy)
        sc = 2.7 + lt * 0.1
        cc.scale(sc, sc)
        hero.draw_bust(cc, hero.expr_mix('cautious', 'fear', fear), turn=0.0, look=(0, 0), t=T, breathe=2.0, shake=1.0)
    char_tint(c, pal, fn)


def s_bluff_stop(c, lt, T, d):
    """OTS from behind hero: bear charges and skids to a stop a few metres away (bluff charge)."""
    pal = pal_at(T)
    hz = 900.0
    stop_t = 1.1
    k = ease_out(clamp(lt / stop_t))
    bz = hz + lerp(18, 6.5, k)
    cam = Cam(x=trail_x(hz) - 0.1, y=1.7, z=hz - 2.4, hy=H * 0.42, f=1150)
    impact = math.exp(-max(0, lt - stop_t) * 5) * (lt > stop_t)
    sx, sy, r = handheld(T, 5 + 30 * impact, 0.2 + impact, seed=20, speed=2.5)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    running = lt < stop_t
    ph = lt * 1.8 if running else 0
    act = [actor(trail_x(hz) - 0.75, hz, hero_back(standing=True, t=T)),
           actor(trail_x(bz) + 0.3, bz, lambda cc: bear.draw_front(cc, phase=ph, t=T, moving=running, gait='run' if running else 'walk',
                                                               head_lift=0.4 * impact, sniff=0.6))]
    render_world(c, cam, pal, T, actors=act, rays=0.2, wind=1.5)
    X, Y, s = cam.proj(trail_x(bz) + 0.3, 0, bz)
    if lt > stop_t * 0.6:
        dust(c, X, Y, clamp((lt - stop_t * 0.6) / 1.4), s=s / 120, a=0.85, seed=4)


def s_hero_firm(c, lt, T, d):
    pal = pal_at(T)
    hz = 950.0
    cam = Cam(x=trail_x(hz) - 0.3, y=0.9, z=hz - 3.4 - lt * 0.15, hy=H * 0.5, f=1150)
    sx, sy, r = handheld(T, 3, 0.1, seed=21)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    act = [actor(trail_x(hz), hz, hero_front(hero.expr_mix('cautious', 'fear', 0.3), t=T, arms_out=0.25, blink=blink_at(T)))]
    render_world(c, cam, pal, T, actors=act, rays=0.2)


def s_bear_pace(c, lt, T, d):
    pal = pal_at(T)
    bz = 1000.0
    bx = trail_x(bz) - 2.5 + lt * 0.9
    cam = Cam(x=trail_x(bz) - 0.3 + lt * 0.2, y=1.2, z=bz - 8.5, hy=H * 0.46, f=1200)
    sx, sy, r = handheld(T, 5, 0.2, seed=22)
    cam.sx, cam.sy, cam.roll = sx, sy, r
    ph = lt * 0.7
    act = [actor(bx, bz, lambda cc: bear.draw_side(cc, phase=ph, gait='walk', t=T, head_lift=0.1 * math.sin(T * 2), sniff=0.4))]
    render_world(c, cam, pal, T, actors=act, rays=0.2, fog=1.2)
    X, Y, s = cam.proj(bx + 1.2, 0.95, bz)
    vapor(c, X, Y, T, s=s / 300, a=0.25)


def s_standoff(c, lt, T, d):
    """Near silence: slow push into the bear's face, breath vapour."""
    pal = pal_at(T)
    hz = 1100.0
    u = lt / d
    cam = Cam(x=trail_x(hz), y=1.2, z=hz - 6.0 + u * 2.2, hy=H * 0.46, f=1300 + u * 300)
    act = [actor(trail_x(hz), hz, lambda cc: bear.draw_front(cc, phase=0, t=T, moving=False, sniff=0.5 + 0.5 * math.sin(T * 1.2), head_lift=0.2))]
    render_world(c, cam, pal, T, actors=act, rays=0.15, fog=1.3, particles=True, leaves=2)
    X, Y, s = cam.proj(trail_x(hz), 1.15, hz)
    vapor(c, X, Y + 20, T, s=s / 300, a=0.3)


def s_bear_looks(c, lt, T, d):
    pal = pal_at(T)
    hz = 1212.0
    cam = Cam(x=trail_x(hz) + 0.3, y=1.3, z=hz - 5.0, hy=H * 0.45, f=1350)
    k = ease_in_out(remap(lt, 0.3, 1.4))
    act = [actor(trail_x(hz), hz, lambda cc: (cc.rotate(0), bear.draw_front(cc, phase=0, t=T, moving=False, sniff=0.2, head_lift=0.3 - 0.3 * k)))]
    render_world(c, cam, pal, T, actors=act, rays=0.3)


def s_bear_turn(c, lt, T, d):
    """Bear turns away: side walk heading off the trail into the trees."""
    pal = pal_at(T)
    bz = 1300.0
    bx = trail_x(bz) + lt * 1.3
    cam = Cam(x=trail_x(bz) + 0.4, y=1.3, z=bz - 9.0 - lt * 0.6, hy=H * 0.45, f=1150)
    ph = lt * 0.6
    act = [actor(bx, bz, lambda cc: bear.draw_side(cc, phase=ph, gait='walk', t=T, head_lift=-0.15))]
    render_world(c, cam, pal, T, actors=act, rays=0.45, fog=1.2)


def s_bear_leaves(c, lt, T, d):
    """Rear view - the bear walks away between the trees, camera pulls back & cranes up."""
    pal = pal_at(T)
    u = ease_in_out(lt / d)
    bz0 = 1400.0
    bz = bz0 + lt * 1.2
    bx = trail_x(bz) + lt * 0.6
    cam = Cam(x=trail_x(bz0), y=lerp(1.5, 4.5, u), z=bz0 - 6 - u * 6, hy=H * lerp(0.44, 0.36, u), f=1150)
    act = [actor(bx, bz, lambda cc: bear.draw_rear(cc, phase=lt * 0.6, t=T), extra_fog=u * 0.25)]
    render_world(c, cam, pal, T, actors=act, rays=0.6, fog=1.4)


def s_safe(c, lt, T, d):
    """Hero from behind at the forest edge in warm light; relief."""
    pal = pal_at(T)
    u = ease_in_out(lt / d)
    hz = 1600.0
    cam = Cam(x=trail_x(hz) - 0.2, y=lerp(1.5, 2.3, u), z=hz - lerp(3.0, 6.0, u), hy=H * lerp(0.45, 0.42, u), f=1150)
    breath = math.sin(T * 1.2)
    act = [actor(trail_x(hz), hz, lambda cc: hero.draw_back(cc, standing=True, t=T, head_turn=0.0))]
    render_world(c, cam, pal, T, actors=act, rays=1.5, fog=0.9, mountains=False, leaves=4)
    birds(c, T, x0=0, y0=260, n=4, scale=1.0)


def s_endcard(c, lt, T, d):
    pal = world.PAL['dark']
    cam = Cam(x=trail_x(1700), y=1.8, z=1700 + lt * 0.4, hy=H * 0.62, f=1150)
    world_blurred(c, cam, pal, T, blur=6, scale=3, rays=0.3)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint('#05080a', 0.72))
    # two faint eyes in the dark forest
    a = 0.55 * smooth(remap(lt, 3.0, 5.0)) * (1 - blink_at(T, 3.0) * 1.0)
    for s in (-1, 1):
        c.drawCircle(W / 2 + s * 26, H * 0.73, 6, paint('#f2d27a', a, blur=3))


# ------------------------------------------------------------------------------------------------
SHOTS = [
    # S1 0:00-0:12
    (0.0, 9.4, s_aerial),
    (9.4, 12.0, s_follow),
    # S2 0:12-0:24
    (12.0, 14.7, s_front_walk),
    (14.7, 17.25, s_watcher),
    (17.25, 18.45, s_branch),
    (18.45, 19.9, s_turn_head),
    (19.9, 24.6, s_bear_reveal),
    # S3 0:24-0:36
    (24.6, 27.5, s_ots_bear),
    (27.5, 29.4, s_hero_freeze),
    (29.4, 31.8, s_bear_eye),
    (31.8, 34.8, s_bear_sniff),
    (34.8, 36.6, lambda c, lt, T, d: s_paws(c, lt, T, d, gait='stand')),
    # S4 0:36-0:49
    (36.6, 47.2, None),  # fear ECU - needs groups
    (47.2, 49.6, s_two_shot),
    # S5 0:49-1:02
    (49.6, 51.0, lambda c, lt, T, d: s_bear_approach(c, lt, T, d, speed=0.55)),
    (51.0, 55.4, None),  # rules - needs groups
    (55.4, 56.6, lambda c, lt, T, d: s_paws(c, lt, T, d, gait='walk', seed=5)),
    (56.6, 59.6, None),  # speak
    (59.6, 62.4, s_gap_wide),
    # S6 1:02-1:16
    (62.4, 68.4, s_back_away),
    (68.4, 69.7, s_bear_head_low),
    (69.7, 72.9, lambda c, lt, T, d: s_bear_approach(c, lt, T, d, speed=1.2, gait='walk', start=12.0, shake=0.2)),
    (72.9, 76.0, s_hero_serious),
    # S7 1:16-1:32
    (76.0, 77.6, s_bear_run_side),
    (77.6, 78.6, lambda c, lt, T, d: s_hero_hold(c, lt, T, d, 0.9)),
    (78.6, 80.4, lambda c, lt, T, d: s_bear_approach(c, lt, T, d, speed=1.0, gait='run', start=10.5, shake=1.0)),
    (80.4, 81.3, lambda c, lt, T, d: s_paws(c, lt, T, d, gait='run', seed=7)),
    (81.3, 84.4, s_bluff_stop),
    (84.4, 86.7, s_hero_firm),
    (86.7, 89.9, s_bear_pace),
    (89.9, 91.1, lambda c, lt, T, d: s_bear_approach(c, lt, T, d, speed=0.9, gait='run', start=8.5, shake=0.8)),
    (91.1, 92.2, lambda c, lt, T, d: s_hero_hold(c, lt, T, d, 0.6)),
    (92.2, 95.6, s_standoff),
    # S8 1:32-1:46
    (95.6, 97.6, s_bear_looks),
    (97.6, 99.4, s_bear_turn),
    (99.4, 102.4, s_bear_leaves),
    # S9 1:46-2:00
    (102.4, 107.4, s_safe),
    (107.4, 120.0, s_endcard),
]

CHAPTERS = [(0.0, 1), (24.6, 2), (49.6, 3), (76.0, 4)]


def bind_groups(groups):
    out = []
    for t0, t1, fn in SHOTS:
        if fn is None:
            if t0 == 36.6:
                fn = (lambda g: (lambda c, lt, T, d: s_fear_ecu(c, lt, T, d, g)))(groups)
            elif t0 == 51.0:
                fn = (lambda g: (lambda c, lt, T, d: s_rules(c, lt, T, d, g)))(groups)
            elif t0 == 56.6:
                fn = (lambda g: (lambda c, lt, T, d: s_speak(c, lt, T, d, g)))(groups)
        out.append((t0, t1, fn))
    return out
