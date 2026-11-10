"""Render the animation frames and pipe them to ffmpeg.

usage: python render.py out.mp4 [start] [end] [workers]
       python render.py --still t1,t2,... outdir
"""
import os
import sys
import subprocess
import multiprocessing as mp
import numpy as np
import cairo

sys.path.insert(0, os.path.dirname(__file__))
from core import *
import shots
from subs import draw_subs

DURATION = 123.17


def _vignette():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.28, W / 2, H / 2, H * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.75)
    c.set_source(g); c.paint()
    return s


def _grain(seed):
    rng = np.random.default_rng(seed)
    w, h = W // 2, H // 2
    n = rng.integers(0, 255, (h, w), dtype=np.uint8)
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0] = n; arr[..., 1] = n; arr[..., 2] = n; arr[..., 3] = 255
    s = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, w, h)
    return s, arr


VIG = None
GRAINS = None


def init():
    global VIG, GRAINS
    VIG = _vignette()
    GRAINS = [_grain(i) for i in range(8)]


def shot_at(t):
    for i, (a, b, fn) in enumerate(shots.SHOTS):
        if a <= t < b:
            return i
    return len(shots.SHOTS) - 1


def render_shot(i, t):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    setc(c, (0, 0, 0)); c.paint()
    a, b, fn = shots.SHOTS[i]
    fn(c, t)
    return s


def render_frame(t):
    i = shot_at(t)
    a, b, fn = shots.SHOTS[i]
    surf = render_shot(i, t)
    c = cairo.Context(surf)
    xf = shots.XFADE.get(a)
    if xf and t < a + xf and i > 0:
        prev = render_shot(i - 1, t)
        c2 = cairo.Context(prev)
        c2.set_source_surface(surf); c2.paint_with_alpha(ease_io((t - a) / xf))
        surf, c = prev, c2
    fl = shots.FLASH.get(a)
    if fl and t < a + fl:
        c.rectangle(0, 0, W, H); setc(c, (1, 1, 1), 0.55 * (1 - (t - a) / fl)); c.fill()
    # post: vignette + grain
    if t < 111.4:
        c.set_source_surface(VIG); c.paint()
        gs, _ = GRAINS[int(t * FPS) % len(GRAINS)]
        c.save(); c.scale(2, 2)
        c.set_source_surface(gs); c.get_source().set_filter(cairo.FILTER_NEAREST)
        c.set_operator(cairo.OPERATOR_OVERLAY); c.paint_with_alpha(0.07)
        c.restore()
    # fade in / out
    if t < 0.35:
        c.rectangle(0, 0, W, H); setc(c, (0, 0, 0), 1 - t / 0.35); c.fill()
    if t > DURATION - 0.4:
        c.rectangle(0, 0, W, H); setc(c, (0, 0, 0), clamp((t - (DURATION - 0.4)) / 0.4)); c.fill()
    draw_subs(c, t)
    surf.flush()
    return surf


def frame_bytes(t):
    s = render_frame(t)
    arr = np.ndarray((H, W, 4), dtype=np.uint8, buffer=s.get_data())
    return arr[..., :3].tobytes()  # BGR (cairo ARGB32 little-endian = B,G,R,A)


def worker(args):
    idx, f0, f1, path = args
    init()
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                          '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                          '-crf', '19', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame_bytes(f / FPS))
        if (f - f0) % 150 == 0:
            print(f"[w{idx}] {f - f0}/{f1 - f0}", flush=True)
    p.stdin.close(); p.wait()
    return path


def main():
    if sys.argv[1] == '--still':
        init()
        ts = [float(x) for x in sys.argv[2].split(',')]
        os.makedirs(sys.argv[3], exist_ok=True)
        for t in ts:
            render_frame(t).write_to_png(os.path.join(sys.argv[3], f"f_{t:07.2f}.png"))
        return
    out = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else DURATION
    nw = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    f0, f1 = int(t0 * FPS), int(t1 * FPS)
    tmp = out + '.parts'
    os.makedirs(tmp, exist_ok=True)
    n = (f1 - f0)
    step = (n + nw * 4 - 1) // (nw * 4)
    jobs = []
    for k, a in enumerate(range(f0, f1, step)):
        jobs.append((k, a, min(f1, a + step), os.path.join(tmp, f'p{k:03d}.mp4')))
    with mp.Pool(nw) as pool:
        parts = pool.map(worker, jobs, chunksize=1)
    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w') as fh:
        for p in parts:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out],
                   check=True)
    print("done", out)


if __name__ == '__main__':
    main()
