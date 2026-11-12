"""Render the picture track (no text) to build/base.mp4 using 4 parallel workers.
usage: python3 render.py [--preview] [--frames a:b] [--still T ...]"""
import math
import os
import random
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import W, H, FPS, paint, lin_grad, rad_grad, clamp, smooth, remap, text, FONT_BLACK, FONT_BOLD  # noqa: E402
import shots  # noqa: E402
import timeline  # noqa: E402
import world  # noqa: E402

ROOT = timeline.ROOT
BUILD = os.path.join(ROOT, 'build')
DUR = 120.0
NFRAMES = int(DUR * FPS)

GROUPS = {g['id']: g for g in timeline.placed('ru')}
SHOTS = shots.bind_groups(GROUPS)
XFADE = {102.4: 0.8}               # crossfade into shot starting at t
FLASH = [(76.0, 0.18, '#ffffff', 0.55), (81.3 + 1.1, 0.12, '#000000', 0.6), (17.25 + 0.22, 0.10, '#ffffff', 0.35)]
FADES = [(106.6, 107.4, 'out'), (107.4, 108.3, 'in')]

_GRAIN = []


def grain_images():
    if not _GRAIN:
        rng = np.random.default_rng(5)
        for i in range(6):
            n = rng.normal(128, 40, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)
            a = np.dstack([n, n, n, np.full_like(n, 255)])
            _GRAIN.append(skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType))
    return _GRAIN


def shot_at(T):
    for i, (t0, t1, fn) in enumerate(SHOTS):
        if t0 <= T < t1:
            return i
    return len(SHOTS) - 1


def draw_shot(c, i, T):
    t0, t1, fn = SHOTS[i]
    fn(c, T - t0, T, t1 - t0)


def hud(c, T):
    """Top progress dots + story clock badge (example style). Text labels come from ASS (per language)."""
    if T >= 107.4:
        ch = 4
        a_all = 1.0
    else:
        ch = 1
        for t0, k in shots.CHAPTERS:
            if T >= t0:
                ch = k
        a_all = 1.0
    a = a_all * clamp(T / 0.4)
    cx, cy = W / 2, 112
    for k in range(1, 5):
        x = cx + (k - 2.5) * 52
        done = k <= ch
        if done:
            pulse = 1 + 0.12 * math.exp(-max(0, T - [0, 0, 24.6, 49.6, 76.0][k]) * 4) if k == ch and k > 1 else 1
            c.drawCircle(x, cy, 19 * pulse, paint('#e53935', a))
        else:
            c.drawCircle(x, cy, 19, paint('#000000', 0.35 * a))
            c.drawCircle(x, cy, 19, paint('#ffffff', 0.5 * a, stroke=2.5))
        text(c, str(k), x, cy + 9, 25, '#ffffff', FONT_BLACK, a=a)
    # story clock badge
    if T < 107.4:
        minutes = 16 * 60 + 40 + int(T / 7.5)
        s = f'{minutes // 60:02d}:{minutes % 60:02d}'
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(40, 88, 150, 50), 25, 25)
        c.drawRRect(r, paint('#e53935', 0.95 * a))
        blink = 0.5 + 0.5 * math.sin(T * 6)
        c.drawCircle(68, 113, 8, paint('#ffffff', a * (0.4 + 0.6 * blink)))
        text(c, s, 130, 125, 32, '#ffffff', FONT_BLACK, a=a)


def post(c, T, f):
    # vignette
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(shader=rad_grad((W / 2, H * 0.47), H * 0.72, [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0.55)], [0, 0.55, 1])))
    # grain
    g = grain_images()[f % 6]
    p = skia.Paint()
    p.setBlendMode(skia.BlendMode.kOverlay)
    p.setAlphaf(0.10)
    c.drawImageRect(g, skia.Rect.MakeLTRB(0, 0, W, H), skia.SamplingOptions(), p)
    # flashes
    for t0, dur, colr, amt in FLASH:
        if t0 <= T < t0 + dur:
            c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint(colr, amt * (1 - (T - t0) / dur)))
    for t0, t1, kind in FADES:
        if t0 <= T < t1:
            u = smooth((T - t0) / (t1 - t0))
            c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H), paint('#000000', u if kind == 'out' else 1 - u))
    # bottom gradient so captions read well
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.62, W, H), paint(shader=lin_grad((0, H * 0.62), (0, H), [(0, 0, 0, 0), (0, 0, 0, 0.42)])))
    # top gradient for HUD
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 260), paint(shader=lin_grad((0, 0), (0, 260), [(0, 0, 0, 0.45), (0, 0, 0, 0)])))


def render_frame(f, surf=None):
    T = f / FPS
    surf = surf or skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    i = shot_at(T)
    t0 = SHOTS[i][0]
    if t0 in XFADE and T - t0 < XFADE[t0] and i > 0:
        u = smooth((T - t0) / XFADE[t0])
        draw_shot(c, i - 1, T)
        c.saveLayerAlpha(None, int(255 * u))
        draw_shot(c, i, T)
        c.restore()
    else:
        draw_shot(c, i, T)
    post(c, T, f)
    hud(c, T)
    return surf


def worker(args):
    a, b, out = args
    world.init_sprites()
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    t0 = time.time()
    for f in range(a, b):
        render_frame(f, surf)
        pr.stdin.write(surf.toarray().tobytes())
        if (f - a) % 150 == 0:
            print(f'[{a}-{b}] frame {f} {(time.time() - t0) / max(1, f - a + 1):.2f}s/f', flush=True)
    pr.stdin.close()
    pr.wait()
    return out


def main():
    args = sys.argv[1:]
    os.makedirs(BUILD, exist_ok=True)
    if args and args[0] == '--still':
        world.init_sprites()
        for s in args[1:]:
            T = float(s)
            surf = render_frame(int(round(T * FPS)))
            surf.makeImageSnapshot().save(os.path.join(BUILD, 'stills', f'still_{T:06.2f}.png'))
        return
    a, b = 0, NFRAMES
    if args and args[0] == '--frames':
        a, b = map(int, args[1].split(':'))
    nproc = int(os.environ.get('NPROC', '4'))
    # interleaved chunks (balance heavy and light shots)
    chunk = 180
    jobs = []
    for k, s in enumerate(range(a, b, chunk)):
        jobs.append((s, min(b, s + chunk), os.path.join(BUILD, 'seg', f'seg_{k:03d}.mp4')))
    os.makedirs(os.path.join(BUILD, 'seg'), exist_ok=True)
    t0 = time.time()
    with Pool(nproc) as pool:
        outs = pool.map(worker, jobs, chunksize=1)
    with open(os.path.join(BUILD, 'seg', 'list.txt'), 'w') as fh:
        for o in outs:
            fh.write(f"file '{o}'\n")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(BUILD, 'seg', 'list.txt'),
                    '-c', 'copy', os.path.join(BUILD, 'base.mp4')], check=True)
    print('done', time.time() - t0)


if __name__ == '__main__':
    main()
