"""Движок рендера серии: параллельные куски → склейка → звук + вшитые субтитры."""
import math
import os
import shutil
import subprocess
import time
from multiprocessing import Pool
from pathlib import Path

from core import FPS, H, W, Post


class Episode:
    """Наследник задаёт: shots() → [(класс, t0, t1, kwargs)], dur, и опционально post_params(t)."""
    dur = 0.0

    def shots(self):
        raise NotImplementedError

    def post_params(self, t):
        """Возвращает (fade, glitch) для кадра."""
        return 1.0, 0.0


def _render_chunk(args):
    ep_factory, f0, f1, out = args
    ep = ep_factory()
    shots = ep.shots()
    post = Post()
    built = {}
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        t = f / FPS
        i = next((i for i, s in enumerate(shots) if s[1] <= t < s[2]), len(shots) - 1)
        if i not in built:
            cls, t0, t1, kw = shots[i]
            built = {i: cls(t0, t1, **kw)}
        img = built[i].frame(t)
        fade, glitch = ep.post_params(t)
        proc.stdin.write(post(img, f, fade, glitch).tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def render(ep_factory, dur, out_mp4, audio_wav, ass=None, workdir=None, t_from=0.0, t_to=None, crf=21, maxrate="4M"):
    """Рендер [t_from, t_to) с аудио и субтитрами в out_mp4. Возвращает время рендера (с)."""
    t_start = time.perf_counter()
    workdir = Path(workdir or Path(out_mp4).parent / "_chunks")
    shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True)
    t_to = dur if t_to is None else t_to
    f_a, f_b = int(round(t_from * FPS)), int(math.ceil(t_to * FPS))
    n = max(1, min(os.cpu_count() or 2, 8))
    bounds = [f_a + round((f_b - f_a) * i / n) for i in range(n + 1)]
    jobs = [(ep_factory, bounds[i], bounds[i + 1], workdir / f"c{i:02d}.mp4") for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_render_chunk, jobs)
    lst = workdir / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    vf = []
    if ass:
        # субтитры идут по времени серии; для куска сдвигаем через setpts
        p = Path(ass).as_posix().replace(":", "\\:")
        fontsdir = (Path(__file__).parent / "fonts").as_posix().replace(":", "\\:")
        vf = ["-vf", f"setpts=PTS+{t_from}/TB,subtitles='{p}':fontsdir='{fontsdir}',setpts=PTS-STARTPTS"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
           "-ss", f"{t_from:.3f}", "-t", f"{t_to - t_from:.3f}", "-i", str(audio_wav), *vf,
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-maxrate", maxrate, "-bufsize", "8M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", str(out_mp4)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(workdir, ignore_errors=True)
    return time.perf_counter() - t_start
