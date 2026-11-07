"""Render the 9:16 video frames for one language.

usage: python render.py LANG WORDS.json DURATION OUTDIR [--stills t1,t2,...] [--workers N]
"""
import argparse
import math
import os
import subprocess
import sys
from multiprocessing import Process

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from lib import W, H, font, text_size, vignette, grain_frames, ease_out, clamp  # noqa
import scenes as SC  # noqa
import timeline as TL  # noqa

FPS = 30
XF = 0.22  # crossfade length
HARD_IN = {"day", "flash", "destruction", "twist", "hook", "failed"}
NO_SUBS = {"hook", "day", "final"}


class Ctx:
    pass


def scene_frame(lang, sc, t, evs):
    S = Ctx()
    S.lang, S.L, S.t = lang, TL.STR[lang], t
    S.start, S.d, S.arg = sc["start"], sc["end"] - sc["start"], sc["arg"]
    S.lt = t - sc["start"]
    S.ev = evs
    return SC.SCENES[sc["name"]](S)


def draw_subs(img, subs, t):
    cur = None
    for c in subs:
        if c["start"] - 0.05 <= t < c["end"]:
            cur = c
            break
    if not cur:
        return img
    f = font(80, 900)
    words = [w for w, _, _ in cur["words"]]
    space = text_size("A A", f)[0] - 2 * text_size("A", f)[0]
    lines, line = [], []
    for i, w in enumerate(words):
        test = " ".join(words[j] for j in line + [i])
        if line and text_size(test, f)[0] > 940:
            lines.append(line)
            line = []
        line.append(i)
    lines.append(line)
    pop = 1.0 + 0.14 * (1 - ease_out((t - cur["start"]) / 0.14))
    sw, sh = 1060, 130 * len(lines) + 40
    spr = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(spr)
    for li, ln in enumerate(lines):
        widths = [text_size(words[i], f)[0] for i in ln]
        total = sum(widths) + space * (len(ln) - 1)
        x = sw / 2 - total / 2
        y = 20 + li * 120 + 55
        for i, wdt in zip(ln, widths):
            _, s, e = cur["words"][i]
            active = s - 0.03 <= t
            col = (255, 214, 10) if (s - 0.03 <= t < e + 0.08) else (255, 255, 255) if active else (235, 235, 235)
            d.text((x + 4, y + 6), words[i], font=f, fill=(0, 0, 0, 150), anchor="lm", stroke_width=8, stroke_fill=(0, 0, 0, 150))
            d.text((x, y), words[i], font=f, fill=col, anchor="lm", stroke_width=8, stroke_fill=(0, 0, 0))
            x += wdt + space
    if pop != 1.0:
        spr = spr.resize((int(sw * pop), int(sh * pop)), Image.BILINEAR)
    img.paste(spr, (int(W / 2 - spr.width / 2), int(1400 - spr.height / 2)), spr)
    return img


def frame(lang, scenes, evs, subs, t, fi):
    idx = max(i for i, s in enumerate(scenes) if s["start"] <= t or i == 0)
    sc = scenes[idx]
    img = scene_frame(lang, sc, t, evs)
    lt = t - sc["start"]
    if idx > 0 and lt < XF and sc["name"] not in HARD_IN:
        prev = scene_frame(lang, scenes[idx - 1], t, evs)
        img = Image.blend(prev, img, clamp(lt / XF))
    img = ImageChops.multiply(img, vignette())
    img = ImageChops.add(img, grain_frames()[0], 1.0, -128)  # static, light texture (moving grain bloats the file)
    if sc["name"] not in NO_SUBS:
        img = draw_subs(img, subs, t)
    return img


def worker(lang, words, dur, outdir, k, n, total):
    scenes, evs, wl, end = TL.build(lang, words, dur)
    subs = TL.chunks(wl, lang)
    a, b = total * k // n, total * (k + 1) // n
    out = os.path.join(outdir, f"seg{k:02d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-tune", "film", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(a, b):
        img = frame(lang, scenes, evs, subs, fi / FPS, fi)
        p.stdin.write(img.tobytes())
        if (fi - a) % 150 == 0:
            print(f"[{lang} w{k}] {fi - a}/{b - a}", flush=True)
    p.stdin.close()
    p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lang")
    ap.add_argument("words")
    ap.add_argument("duration", type=float)
    ap.add_argument("outdir")
    ap.add_argument("--stills")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    scenes, evs, wl, end = TL.build(a.lang, a.words, a.duration)
    if a.stills:
        subs = TL.chunks(wl, a.lang)
        ts = [float(x) for x in a.stills.split(",")] if a.stills != "mid" else [(s["start"] + s["end"]) / 2 for s in scenes]
        for t in ts:
            frame(a.lang, scenes, evs, subs, t, 0).save(os.path.join(a.outdir, f"still_{t:07.2f}.jpg"), quality=85)
        return
    total = int(math.ceil(end * FPS))
    procs = [Process(target=worker, args=(a.lang, a.words, a.duration, a.outdir, k, a.workers, total)) for k in range(a.workers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    with open(os.path.join(a.outdir, "list.txt"), "w") as f:
        for k in range(a.workers):
            f.write(f"file 'seg{k:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(a.outdir, "list.txt"), "-c", "copy",
                    os.path.join(a.outdir, "video.mp4")], check=True)
    print("done", total, "frames")


if __name__ == "__main__":
    main()
