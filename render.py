"""Render episode 1 to a vertical 1080x1920 video.

    python3 render.py --lang ru            # full video -> out/ep1_ru.mp4
    python3 render.py --lang en
    python3 render.py --stills 3,30,72     # preview frames -> out/stills/
"""
import argparse
import os
import subprocess
import sys
from multiprocessing import Pool

import cairo
import numpy as np

from mir.gfx import W, H, FPS
from mir import ep1, audio

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def _post_tables():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    vig = np.clip(1.0 - 0.55 * np.clip(d - 0.45, 0, 1) ** 1.6, 0, 1)
    rng = np.random.default_rng(7)
    grains = [rng.normal(0, 4, (H // 2, W // 2)).astype(np.int16) for _ in range(6)]
    grains = [g.repeat(2, 0).repeat(2, 1) for g in grains]
    return (vig[..., None] * 256).astype(np.uint16), grains


_VIG = _GRAINS = None


def frame_bytes(t, lang, chunks, idx, ts=None):
    global _VIG, _GRAINS
    if _VIG is None:
        _VIG, _GRAINS = _post_tables()
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ep1.render_frame(ctx, t, lang, chunks, ts)
    surf.flush()
    arr = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    rgb = (arr[..., :3].astype(np.uint16) * _VIG >> 8).astype(np.int16)
    rgb += _GRAINS[(idx // 3) % len(_GRAINS)][..., None]
    np.clip(rgb, 0, 255, out=rgb)
    out = np.empty((H, W, 4), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = 255
    return out


def load_voice(path):
    import json
    v = json.load(open(path, encoding="utf-8"))
    ep1.set_voice(v["lang"], v["spans"], v.get("words"))
    ep1.use_lang(v["lang"])
    return v


def get_chunks(lang):
    return ep1.voice_chunks(lang) if lang in ep1.VOICE else ep1.subtitle_chunks(lang)


def render_chunk(args):
    lang, f0, f1, path, voice = args
    if voice:
        load_voice(voice)
    chunks = get_chunks(lang)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
           "-crf", "21", "-tune", "grain", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(f0, f1):
        T = i / FPS
        p.stdin.write(frame_bytes(ep1.unwarp(T), lang, chunks, i, T).tobytes())
    p.stdin.close()
    p.wait()
    return path


def render_video(lang, jobs=4, voice=None):
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "tmp")
    os.makedirs(tmp, exist_ok=True)
    total = int(ep1.duration() * FPS)
    step = (total + jobs - 1) // jobs
    parts = [(lang, i, min(i + step, total), os.path.join(tmp, f"{lang}_{i:06d}.mp4"), voice)
             for i in range(0, total, step)]
    with Pool(jobs) as pool:
        paths = pool.map(render_chunk, parts)
    lst = os.path.join(tmp, f"{lang}.txt")
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    sfx = "_voice" if voice else ""
    wav = os.path.join(OUT, f"ep1_music_sfx{sfx}_{lang}.wav")
    audio.render(wav, ep1)
    final = os.path.join(OUT, f"ep1_{lang}{sfx}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav]
    if voice:
        import json
        vj = json.load(open(voice))
        ms = int(vj.get("offset", 0) * 1000)
        cmd += ["-i", os.path.join(os.path.dirname(OUT), vj["audio"]), "-filter_complex",
                f"[2:a]adelay={ms}|{ms},aresample=44100,aformat=channel_layouts=stereo,volume=1.6,apad,asplit[v1][v2];"
                "[1:a][v1]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500[bed];"
                "[bed][v2]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]",
                "-map", "0:v", "-map", "[a]"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "23", "-maxrate", "4M", "-bufsize", "8M",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", final]
    subprocess.run(cmd, check=True)
    for p in paths:
        os.remove(p)
    os.remove(lst)
    return final


def write_srt(lang):
    def ts(x):
        ms = int(round(x * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    path = os.path.join(OUT, f"ep1_{lang}.srt")
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, s) in enumerate(get_chunks(lang), 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="ru", choices=["ru", "en", "both"])
    ap.add_argument("--stills", default="")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--voice", default="", help="voice json: {lang, audio, spans, words}")
    a = ap.parse_args()
    if a.voice:
        a.lang = load_voice(a.voice)["lang"]
    langs = ["ru", "en"] if a.lang == "both" else [a.lang]
    voice = os.path.abspath(a.voice) if a.voice else None
    if a.stills:
        from PIL import Image
        d = os.path.join(OUT, "stills")
        os.makedirs(d, exist_ok=True)
        for lang in langs:
            chunks = get_chunks(lang)
            for s in a.stills.split(","):
                T = float(s)
                img = frame_bytes(ep1.unwarp(T), lang, chunks, 0, T)
                t = T
                Image.fromarray(img[..., [2, 1, 0]]).save(os.path.join(d, f"{lang}_{t:06.2f}.png"))
        return
    os.makedirs(OUT, exist_ok=True)
    for lang in langs:
        print("rendering", lang, flush=True)
        print(render_video(lang, a.jobs, voice))
        print(write_srt(lang))


if __name__ == "__main__":
    sys.exit(main())
