"""Vertical 9:16 cover: big brown bear in the foreground, the hero far away on the trail, dark forest."""
import os
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bear  # noqa: E402
import hero  # noqa: E402
import shots  # noqa: E402
import world  # noqa: E402
from gfx import W, H, paint, lin_grad, rad_grad, text, FONT_BLACK, FONT_BOLD  # noqa: E402
from world import Cam, render_world, trail_x  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    world.init_sprites()
    T = 50.0
    pal = world.pal_mix('tense', 'dark', 0.55)
    pal['rays'] = 0.55
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    hz = 330.0
    cam = Cam(x=trail_x(hz - 14) + 0.1, y=1.5, z=hz - 15.0, hy=H * 0.47, f=1250)
    act = [shots.actor(trail_x(hz), hz, lambda cc: hero.draw_back(cc, standing=True, t=T))]
    render_world(c, cam, pal, T, actors=act, rays=1.6, fog=1.3, leaves=5)
    # rim light behind the bear
    c.drawCircle(W * 0.7, H * 0.62, 650, paint(shader=rad_grad((W * 0.7, H * 0.62), 650, [(1.0, 0.85, 0.55, 0.35), (1, 0.8, 0.5, 0.0)])))

    def fn(cc):
        cc.translate(W * 0.70, H * 0.72)
        cc.scale(1.55, 1.55)
        cc.rotate(-6)
        bear.draw_closeup(cc, t=0.3, sniff=0.6)
    shots.char_tint(c, pal, fn, amount=0.55)
    # cinematic grade
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=rad_grad((W * 0.45, H * 0.55), H * 0.75, [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0.7)], [0, 0.45, 1])))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 760), paint(shader=lin_grad((0, 0), (0, 760), [(0, 0, 0, 0.8), (0, 0, 0, 0)])))
    # title
    text(c, 'ТЫ ВСТРЕТИЛ', W / 2, 300, 132, '#ffffff', FONT_BLACK, outline=18, outline_color='#0b0b0b')
    text(c, 'МЕДВЕДЯ!', W / 2, 460, 176, '#ffd400', FONT_BLACK, outline=20, outline_color='#0b0b0b')
    # red pill
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - 230, 520, 460, 72), 36, 36)
    c.drawRRect(r, paint('#e53935'))
    text(c, 'ЧТО ДЕЛАТЬ?', W / 2, 572, 46, '#ffffff', FONT_BLACK)
    os.makedirs(os.path.join(ROOT, 'output'), exist_ok=True)
    surf.makeImageSnapshot().save(os.path.join(ROOT, 'output', 'bear_thumbnail.png'))


if __name__ == '__main__':
    main()
