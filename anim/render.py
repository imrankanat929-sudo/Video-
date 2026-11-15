"""Frame renderer: python -m anim.render <lang> <out.mp4|preview.png> [t0 t1 ...]"""
import os, sys, subprocess, wave
import numpy as np
import skia
from multiprocessing import Pool
from .core import W, H, FPS
from .film import Film
from .timing import duration, VO_OFF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def vo_envelope(lang):
    """mouth-opening envelope from the voice (for lip sync)"""
    path = os.path.join(ROOT, "build", f"voice_{lang}.wav")
    if not os.path.exists(path):
        return None
    w = wave.open(path)
    sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    if w.getnchannels() > 1:
        a = a.reshape(-1, w.getnchannels()).mean(1)
    a /= 32768.0
    hop = sr // FPS
    n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
    ref = np.percentile(rms[rms > 1e-4], 95)
    env = np.clip((rms / ref - 0.12) / 0.75, 0, 1) ** 0.8
    # smooth & add jaw bounce
    env = np.convolve(env, [0.25, 0.5, 0.25], mode="same")
    pad = int(VO_OFF * FPS)
    env = np.concatenate([np.zeros(pad), env])  # voice file is placed at VO_OFF in the film
    return (FPS, env)


_film = None


def _init(lang):
    global _film
    _film = Film(lang, vo_env=vo_envelope(lang))


def _render_chunk(args):
    lang, f0, f1, path = args
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    buf = np.empty((H, W, 4), np.uint8)
    for f in range(f0, f1):
        _film.frame(c, f / FPS)
        surf.readPixels(skia.ImageInfo.Make(W, H, skia.kBGRA_8888_ColorType, skia.kPremul_AlphaType), buf)
        p.stdin.write(buf.tobytes())
    p.stdin.close()
    p.wait()
    return path


def render_video(lang, out, workers=4):
    nf = int(round(duration(lang) * FPS))
    tmp = os.path.join(ROOT, "build", f"chunks_{lang}")
    os.makedirs(tmp, exist_ok=True)
    n = workers * 3
    bounds = [round(i * nf / n) for i in range(n + 1)]
    jobs = [(lang, bounds[i], bounds[i + 1], os.path.join(tmp, f"c{i:03d}.mp4")) for i in range(n)]
    with Pool(workers, initializer=_init, initargs=(lang,)) as pool:
        for i, pth in enumerate(pool.imap(_render_chunk, jobs)):
            print(f"[{lang}] chunk {i + 1}/{n}", flush=True)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{j[3]}'\n" for j in jobs))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)


def preview(lang, out, times, cols=4, scale=0.25):
    _init(lang)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    tw, th = int(W * scale), int(H * scale)
    rows = (len(times) + cols - 1) // cols
    sheet = skia.Surface(tw * cols, th * rows)
    sc = sheet.getCanvas()
    for i, t in enumerate(times):
        _film.frame(c, t)
        img = surf.makeImageSnapshot()
        sc.drawImageRect(img, skia.Rect.MakeXYWH((i % cols) * tw, (i // cols) * th, tw, th),
                         skia.SamplingOptions(skia.FilterMode.kLinear))
        sc.drawString(f"{t:.1f}", (i % cols) * tw + 8, (i // cols) * th + 30, skia.Font(None, 26),
                      skia.Paint(Color=skia.ColorYELLOW))
    sheet.makeImageSnapshot().save(out)


if __name__ == "__main__":
    lang, out = sys.argv[1], sys.argv[2]
    if out.endswith(".png"):
        preview(lang, out, [float(x) for x in sys.argv[3:]])
    else:
        render_video(lang, out)
