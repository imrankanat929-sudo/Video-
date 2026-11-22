"""Frame renderer: cairo foreground + glow + background, piped to ffmpeg.

usage:
  python render.py still <t> [out.png]      # one frame
  python render.py scenes                   # every scene -> out/scenes/*.mp4
"""
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cairo
import numpy as np
from PIL import Image, ImageFilter

import gfx
from scenes import draw_scenes
from timeline import FPS, W, H, SCENES, SFX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")


# ----------------------------------------------------------- background -----
def make_background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.46
    d = np.sqrt(((x - cx) / W) ** 2 + ((y - cy) / H) ** 2)
    bg = 0.018 + 0.05 * np.exp(-(d / 0.42) ** 2)
    # dot grid (as in the reference)
    grid = np.zeros((H, W), np.float32)
    step = 38
    for gy in range(step // 2, H, step):
        for gx in range(step // 2, W, step):
            grid[gy - 1:gy + 1, gx - 1:gx + 1] = 1.0
    grid = np.asarray(Image.fromarray((grid * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    bg += grid * 0.07 * np.exp(-(d / 0.55) ** 2)
    vig = 1 - 0.75 * np.clip(d / 0.75, 0, 1) ** 2
    return (bg * vig).astype(np.float32), vig.astype(np.float32)


BG, VIG = make_background()
RNG = np.random.default_rng(3)
GRAIN = [RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
BOOMS = [(t, g) for k, t, g in SFX if k == "boom"]


def shake_flash(t):
    dx = dy = fl = 0.0
    for (tb, g) in BOOMS:
        u = t - tb
        if 0 <= u < 1.0:
            env = math.exp(-u * 6) * g
            dx += math.sin(u * 63 + tb) * 9 * env
            dy += math.cos(u * 71 + tb * 2) * 7 * env
            fl += math.exp(-u * 9) * g * 0.10
    return dx, dy, fl


def particles(ctx, t):
    for i in range(70):
        px = (gfx.hash01(i, 1) * W + t * (6 + 10 * gfx.hash01(i, 2))) % W
        py = (gfx.hash01(i, 4) * H - t * (3 + 6 * gfx.hash01(i, 6))) % H
        a = 0.12 + 0.22 * gfx.hash01(i, 7)
        a *= 0.6 + 0.4 * math.sin(t * (0.6 + gfx.hash01(i, 8)) + i)
        ctx.arc(px, py, 1.0 + 1.6 * gfx.hash01(i, 9), 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, max(0, a))
        ctx.fill()


def blur(img, factor, radius):
    small = Image.fromarray(img).resize((W // factor, H // factor), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(small.resize((W, H), Image.BILINEAR), np.float32) / 255


def render_frame(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    particles(ctx, t)
    dx, dy, fl = shake_flash(t)
    ctx.save()
    ctx.translate(dx, dy)
    draw_scenes(ctx, t)
    ctx.restore()
    surf.flush()
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    lum8 = buf[:, :, 2].copy()          # premultiplied white == luminance
    A = buf[:, :, 3].astype(np.float32) / 255
    L = lum8.astype(np.float32) / 255
    g1 = blur(lum8, 4, 3)
    g2 = blur(lum8, 8, 7)
    out = BG * (1 - A) + L + 0.55 * g1 + 0.45 * g2
    out = out * (1 + fl) + fl * 0.05 * VIG
    gi = GRAIN[int(t * FPS) % len(GRAIN)]
    grain = np.repeat(np.repeat(gi, 2, 0), 2, 1)
    out = out + grain * 0.0045
    out = np.clip(out, 0, 1)
    out = out ** 0.95  # tiny lift for the glow falloff
    return (out * 255 + 0.5).astype(np.uint8)


# ---------------------------------------------------------------- output ----
def frame_range(start, end):
    return range(int(round(start * FPS)), int(round(end * FPS)))


def render_segment(args):
    name, start, end = args
    os.makedirs(os.path.join(OUT, "scenes"), exist_ok=True)
    final = os.path.join(OUT, "scenes", f"{name}.mp4")
    path = final + f".tmp{os.getpid()}.mp4"
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
           "-preset", "slow", "-crf", "16", "-tune", "animation",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in frame_range(start, end):
        p.stdin.write(render_frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {name}")
    os.replace(path, final)
    return final


def main():
    if sys.argv[1] == "still":
        t = float(sys.argv[2])
        out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUT, f"still_{t:06.2f}.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        Image.fromarray(render_frame(t)).save(out)
        print(out)
    elif sys.argv[1] == "scenes":
        only = sys.argv[2:]
        jobs = [s for s in SCENES if not only or s[0] in only]
        # longest first for better packing
        jobs.sort(key=lambda s: s[1] - s[2])
        with Pool(int(os.environ.get("JOBS", os.cpu_count()))) as pool:
            for p in pool.imap_unordered(render_segment, jobs):
                print("done", p, flush=True)


if __name__ == "__main__":
    main()
