"""Render reference sheets (character / monster / environment), the layout map and the Shorts cover.
All images are drawn with the SAME rig code used in the clips - they are the continuity source of truth."""
import math
import os
import sys

import skia

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scenes_ep01 as S  # noqa: E402  (sets up engine path)
from didao_engine.core import (W, H, Camera, col, draw_text, hexc, lin_grad, mix, new_surface, paint, post, rad_grad, save_png)
from didao_engine.characters import (EXPR, HERO, LENA, MAX, SLENDER_H, Light, draw_character, draw_portrait, draw_slender,
                                     expr, pose, walk_pose)
from didao_engine.forest import (CARVED_TREE, CLEARING, CLEARING_R, FIRE_POS, TENT_POS, Scene, forest_trees, path_x)
from didao_engine.props import draw_beam

EP = os.path.join(HERE, '..')
SEASON = os.path.join(EP, '..')
BOLD = 'dejavu/DejaVuSans-Bold.ttf'
REG = 'dejavu/DejaVuSans.ttf'
STUDIO = Light(amb=(0.95, 0.95, 0.97), rim=hexc('#bcd0f0'), rim_side=-1, rim_k=0.5, shade=0.35)
BG = hexc('#1c222d')
FG = (0.86, 0.88, 0.92)


def label(c, txt, x, y, size=30, color=FG, align='center', font=BOLD):
    draw_text(c, txt, x, y, font, size, color, align=align)


def sheet_header(c, w, title, sub):
    c.drawRect(skia.Rect(0, 0, w, 120), paint(hexc('#11151c')))
    label(c, title, 50, 75, 46, align='left')
    label(c, sub, w - 50, 75, 26, (0.6, 0.65, 0.72), align='right', font=REG)


def character_sheet(cd, fname, title, notes):
    w, h = 2700, 1700
    s = new_surface(w, h)
    c = s.getCanvas()
    c.clear(col(BG))
    sheet_header(c, w, title, 'DIDAO - CHARACTER REFERENCE - DO NOT REDESIGN')
    # floor + height grid
    base = 1300
    scale = 560
    for m in range(0, 3):
        y = base - m * 0.5 * scale * 2
    for i in range(0, 20):
        y = base - i * 0.1 * scale
        if y < 170:
            break
        c.drawLine(40, y, 1700, y, paint((1, 1, 1), alpha=0.04 if i % 5 else 0.10, stroke=1))
    views = [('FRONT', 'front', pose(), False), ('SIDE', 'side', pose(), False), ('BACK', 'back', pose(), False),
             ('FULL BODY / ACTION', 'front', pose(ls=150, le=-10, lhand='flashlight', yaw=12), False)]
    for i, (name, v, p, fl) in enumerate(views):
        x = 230 + i * 420
        c.save()
        c.translate(x, base)
        c.scale(scale, scale)
        draw_character(c, cd, p, v, EXPR['neutral'] if i < 3 else EXPR['worried'], STUDIO, flip=fl)
        c.restore()
        label(c, name, x, base + 70, 28)
    label(c, f'height {cd.height:.2f} m', 1000, base + 125, 24, (0.6, 0.65, 0.72), font=REG)
    # expressions (each in its own clipped cell)
    cells = [('NEUTRAL', 'neutral', 1780, 150), ('SCARED', 'scared', 2230, 150), ('SURPRISED', 'surprised', 1780, 710), ('WORRIED', 'worried', 2230, 710)]
    for name, e, x0, y0 in cells:
        c.save()
        c.clipRect(skia.Rect(x0, y0, x0 + 430, y0 + 540))
        c.drawRect(skia.Rect(x0, y0, x0 + 430, y0 + 540), paint((1, 1, 1), alpha=0.03))
        c.translate(x0 + 215, y0 + 230)
        c.scale(210, 210)
        draw_portrait(c, cd, 0.0, EXPR[e], STUDIO)
        c.restore()
        c.drawRect(skia.Rect(x0, y0 + 480, x0 + 430, y0 + 540), paint(hexc('#11151c'), alpha=0.85))
        label(c, name, x0 + 215, y0 + 522, 26)
    # palette + notes
    y = 1460
    for i, (nm, cc) in enumerate((('skin', cd.skin), ('hair', cd.hair), ('top', cd.top), ('pants', cd.pants), ('shoes', cd.shoes), ('eyes', cd.eyes))):
        x = 60 + i * 170
        c.drawRoundRect(skia.Rect(x, y, x + 130, y + 80), 10, 10, paint(cc))
        c.drawRoundRect(skia.Rect(x, y, x + 130, y + 80), 10, 10, paint((1, 1, 1), alpha=0.3, stroke=2))
        hx = '#%02x%02x%02x' % tuple(int(v * 255) for v in cc[:3])
        label(c, f'{nm} {hx}', x + 65, y + 120, 20, (0.7, 0.74, 0.8), font=REG)
    for i, n in enumerate(notes):
        label(c, n, 1100, 1450 + i * 40, 24, (0.78, 0.8, 0.86), align='left', font=REG)
    save_png(s, os.path.join(EP, 'character_references', fname))


def expressions_strip():
    w, h = 2400, 760
    s = new_surface(w, h)
    c = s.getCanvas()
    c.clear(col(BG))
    sheet_header(c, w, 'DIDAO HERO - EXPRESSIONS & TURNAROUND HEAD', 'yaw -0.45 .. +0.45')
    items = [('neutral', 0.0), ('calm', 0.0), ('worried', 0.0), ('scared', 0.0), ('surprised', 0.0), ('sleep', 0.0),
             ('neutral', -0.45), ('neutral', 0.45)]
    for i, (e, yaw) in enumerate(items):
        x = 160 + i * 295
        c.save()
        c.translate(x, 380)
        c.scale(200, 200)
        draw_portrait(c, HERO, yaw, EXPR[e], STUDIO)
        c.restore()
        label(c, f'{e.upper()}' + (f' yaw {yaw:+.2f}' if yaw else ''), x, 700, 22)
    save_png(s, os.path.join(EP, 'character_references', 'HERO_EXPRESSIONS.png'))


def monster_sheet():
    w, h = 2400, 1800
    s = new_surface(w, h)
    c = s.getCanvas()
    c.clear(col(hexc('#141920')))
    sheet_header(c, w, 'THE TALL MAN (SLENDERMAN) - MONSTER REFERENCE', 'height 2.95 m - featureless face - black suit, white shirt, dark tie')
    base = 1660
    sc = 400
    c.save()
    c.translate(450, base)
    c.scale(sc, sc)
    draw_slender(c, t=0, tilt=0, sway=0, light=STUDIO)
    c.restore()
    label(c, 'FRONT (neutral)', 450, base + 60, 26)
    c.save()
    c.translate(1050, base)
    c.scale(sc, sc)
    draw_slender(c, t=0, tilt=18, sway=0, light=STUDIO, arm_spread=0.4)
    c.restore()
    label(c, 'HEAD TILT / ARMS (menace)', 1050, base + 60, 26)
    # scale comparison
    c.save()
    c.translate(1700, base)
    c.scale(sc, sc)
    draw_slender(c, t=0, tilt=6, sway=0, light=STUDIO)
    c.restore()
    c.save()
    c.translate(2050, base)
    c.scale(sc, sc)
    draw_character(c, HERO, pose(), 'front', EXPR['scared'], STUDIO)
    c.restore()
    label(c, 'SCALE vs HERO (1.68 m)', 1880, base + 60, 26)
    for i, n in enumerate(['Rules: moves slowly or not at all; never runs.', 'Early shots: far away, small, half-lost in fog.',
                           'Presence grows each scene: far -> treeline -> three copies.', 'Vanishes with a short glitch (slice displacement + static).',
                           'Never show a face. Never change proportions or suit.']):
        label(c, n, 60, 200 + i * 42, 26, (0.78, 0.8, 0.86), align='left', font=REG)
    save_png(s, os.path.join(EP, 'monster_references', 'SLENDERMAN_REFERENCE_SHEET.png'))


def environment_refs():
    shots = [('FOREST_NIGHT_PATH', Camera(x=0.2, y=1.6, z=8, yaw=math.pi, focal=1300, horizon=0.5), 'night'),
             ('FOREST_DUSK_CLEARING', Camera(x=3.2, y=1.7, z=14.0, yaw=-0.6, focal=1250, horizon=0.52), 'dusk'),
             ('FOREST_MORNING_OVERGROWN', Camera(x=0.25, y=1.7, z=18.0, yaw=math.pi, focal=1250, horizon=0.48), 'morning')]
    for name, cam, tod in shots:
        s = new_surface()
        c = s.getCanvas()
        sc = Scene(cam, tod=tod, t=2.0, overgrown=(tod == 'morning'))
        if tod == 'dusk':
            S.put_tent(sc, 2.0)
            S.put_fire(sc, 2.0, 0.8)
        sc.render(c, rays=0.06)
        if tod == 'dusk':
            S.fire_light_overlay(c, sc, 2.0, 0.8)
        post(c, 0)
        save_png(s, os.path.join(EP, 'environment_references', name + '.png'))
    # top-down layout map
    w = h = 1600
    s = new_surface(w, h)
    c = s.getCanvas()
    c.clear(col(hexc('#0d1218')))
    sheet_header(c, w, 'BLACKPINE HOLLOW - LAYOUT MAP', '1 grid cell = 5 m, north = up (+z)')
    cx, cz, k = 800, 20.0, 22.0

    def P(x, z):
        return (cx + x * k, 900 - (z - cz) * k)
    for g in range(-40, 41, 5):
        a = P(g, -10)
        b = P(g, 50)
        c.drawLine(a[0], 130, b[0], h, paint((1, 1, 1), alpha=0.05, stroke=1))
        a = P(-40, g + 20)
        c.drawLine(0, a[1], w, a[1], paint((1, 1, 1), alpha=0.05, stroke=1))
    for (x, z, th, var, fl) in forest_trees():
        px, py = P(x, z)
        if 0 < px < w and 130 < py < h:
            c.drawCircle(px, py, 6, paint((0.25, 0.35, 0.3)))
    pts = [P(path_x(z), z) for z in [14 - i * 0.5 for i in range(80)]]
    for a, b in zip(pts, pts[1:]):
        c.drawLine(*a, *b, paint((0.6, 0.55, 0.45), stroke=PATH_PX))
    c.drawCircle(*P(*CLEARING), CLEARING_R * k, paint((0.5, 0.55, 0.5), alpha=0.25))
    marks = [('TENT', TENT_POS[0], TENT_POS[2], (0.4, 0.6, 0.4)), ('FIRE', FIRE_POS[0], FIRE_POS[2], (1, 0.5, 0.2)),
             ('CARVED PINE', CARVED_TREE[0], CARVED_TREE[2], (0.8, 0.7, 0.5)), ('TALL MAN #1 (clip 3)', -1.7, 7.0, (0.9, 0.9, 0.95)),
             ('TALL MAN #2 (clips 7-8)', -3.4, 12.6, (0.9, 0.9, 0.95))] + [(f'THREE (clip 12)', x, z, (0.9, 0.3, 0.3)) for x, z in S.THREE]
    for nm, x, z, cc in marks:
        px, py = P(x, z)
        c.drawCircle(px, py, 12, paint(cc))
        label(c, nm, px + 18, py + 8, 22, cc, align='left')
    label(c, 'PATH (gone in the morning)', P(path_x(0), 0)[0] + 30, P(0, 0)[1], 22, (0.6, 0.55, 0.45), align='left')
    mx, my = P(-14, 44)
    c.drawLine(mx, my, mx + 0, my, paint((1, 1, 1)))
    label(c, 'MOON  (north-west)', 120, 200, 24, (0.75, 0.82, 0.95), align='left')
    c.drawLine(110, 210, 60, 160, paint((0.75, 0.82, 0.95), stroke=3))
    save_png(s, os.path.join(EP, 'environment_references', 'LAYOUT_MAP_TOPDOWN.png'))


PATH_PX = 30


def cover(lang='en'):
    s = new_surface()
    c = s.getCanvas()
    cam = Camera(x=0.6, y=1.5, z=15.6, yaw=0.0, focal=1500, horizon=0.47)
    sc = Scene(cam, tod='night', t=3.0, fog_mult=1.1, hide_trees_near=[(2.1, 27.5, 1.5), (1.8, 22, 1.5)])
    S.put_slender(sc, 2.1, 27.5, 3.0, tilt=12, extra_fog=-0.1)
    sc.render(c, rays=0.10)
    pr = cam.project(2.1, 1.7, 27.5)
    hs = 1050
    hx, hy = W * 0.33, H * 0.64 + 1.62 * hs
    # torch at the end of the raised arm
    ox, oy = hx + 0.58 * hs, hy - 1.86 * hs
    draw_beam(c, (ox, oy), (pr[0], pr[1]), strength=0.95, spread=0.10, t=1.0)
    c.save()
    c.translate(hx, hy)
    c.scale(hs, hs)
    lt = Light(amb=(0.45, 0.52, 0.68), rim=hexc('#a9c0e6'), rim_side=1, rim_k=1.0, shade=0.55, front=0.2, front_col=(0.8, 0.85, 1.0))
    draw_character(c, HERO, pose(ls=135, le=-5, lhand='flashlight', yaw=18), 'front', expr('scared', lx=0.7), lt, shadow=False)
    c.restore()
    post(c, 0, vignette=0.9, grain=0.05)
    c.drawRect(skia.Rect(0, 0, W, 560), paint(shader=lin_grad((0, 0), (0, 560), [(0, 0, 0, 0.8), (0, 0, 0, 0)])))
    draw_text(c, 'D I D A O', W / 2, 120, BOLD, 36, (0.65, 0.7, 0.78))
    if lang == 'ru':
        draw_text(c, 'ОН СЛЕДИТ', W / 2, 270, 'dejavu/DejaVuSerif-Bold.ttf', 112, (0.95, 0.95, 0.97), spacing=3)
        draw_text(c, 'ЗА ТОБОЙ', W / 2, 410, 'dejavu/DejaVuSerif-Bold.ttf', 112, (0.95, 0.95, 0.97), spacing=3)
        save_png(s, os.path.join(EP, 'final', 'DIDAO_EP01_COVER_RU.png'))
    else:
        draw_text(c, 'HE IS', W / 2, 270, 'dejavu/DejaVuSerif-Bold.ttf', 140, (0.95, 0.95, 0.97), spacing=6)
        draw_text(c, 'WATCHING YOU', W / 2, 410, 'dejavu/DejaVuSerif-Bold.ttf', 96, (0.95, 0.95, 0.97), spacing=2)
        save_png(s, os.path.join(EP, 'final', 'DIDAO_EP01_COVER.png'))


if __name__ == '__main__':
    character_sheet(HERO, 'HERO_REFERENCE_SHEET.png', 'DIDAO HERO (15) - MAIN CHARACTER',
                    ['Messy black hair (fixed silhouette), dark navy sweater,', 'dark trousers, dark sneakers with grey soles.',
                     'Curious, careful, sometimes impulsive. Not a superhero.', 'Same rig in every episode: characters.py -> HERO'])
    character_sheet(MAX, 'MAX_REFERENCE_SHEET.png', 'MAX - FRIEND', ['Tallest of the three. Olive parka, knitted beanie.', 'Skeptic: "it was just a tree".'])
    character_sheet(LENA, 'LENA_REFERENCE_SHEET.png', 'LENA - FRIEND', ['Auburn ponytail, maroon puffer, grey scarf.', 'Observant: always sees it first.'])
    expressions_strip()
    monster_sheet()
    environment_refs()
    cover()
    cover('ru')
    print('refs done')
