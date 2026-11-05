"""Рендер: параллельно по кускам -> склейка -> звук -> вшитые субтитры.
python -m src.render [--fast] [--start S --end E]"""
import argparse, os, subprocess, time
from multiprocessing import Process
from .config import W, H, FPS, OUT, BUILD, EP
from .cues import C


def worker(idx, f0, f1, path, scale):
    if EP.startswith("ep2"):
        from .ep2.shots import render_frame
    else:
        from .shots import render_frame
    from .gfx import to_u8
    import cv2
    w, h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    t0 = time.time()
    for k, fi in enumerate(range(f0, f1)):
        img = to_u8(render_frame(fi / FPS))
        if scale != 1:
            img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        p.stdin.write(img.tobytes())
        if k % 240 == 0:
            el = time.time() - t0
            print(f"[w{idx}] {k}/{f1 - f0} frames  {el:.0f}s", flush=True)
    p.stdin.close(); p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="черновик 960x540")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--bitrate", default="2600k")
    ap.add_argument("--reuse", action="store_true", help="не перерендеривать готовые куски build/part_*.mp4")
    a = ap.parse_args()
    c = C()
    OUT.mkdir(parents=True, exist_ok=True); BUILD.mkdir(parents=True, exist_ok=True)
    end = a.end or c["END"]
    F0, F1 = int(a.start * FPS), int(end * FPS)
    n = a.jobs
    # кадры чередуются по сложности — делим на мелкие куски и раздаём по кругу
    chunks = 4 * n
    bounds = [F0 + (F1 - F0) * i // chunks for i in range(chunks + 1)]
    parts = [str(BUILD / f"part_{i:03d}.mp4") for i in range(chunks)]
    scale = 0.5 if a.fast else 1.0
    if EP.startswith("ep2"):
        from .ep2.audio import build as build_audio
        from .ep2.subs import build as build_subs
        names = (("someone_is_following_you_9x16.mp4", "someone_is_following_you_9x16_nosubs.mp4") if EP == "ep2en"
                 else ("za_mnoy_kto_to_idet_9x16.mp4", "za_mnoy_kto_to_idet_9x16_nosubs.mp4"))
    else:
        from .audio import build as build_audio
        from .subtitles import build as build_subs
        names = ("what_if_ep1_atomic.mp4", "what_if_ep1_atomic_nosubs.mp4")
    build_subs()
    build_audio()
    t0 = time.time()
    queue = [i for i in range(chunks) if not (a.reuse and os.path.exists(parts[i]))]
    running = []
    while queue or running:
        while queue and len(running) < n:
            i = queue.pop(0)
            pr = Process(target=worker, args=(i, bounds[i], bounds[i + 1], parts[i], scale)); pr.start()
            running.append(pr)
        for pr in running[:]:
            if not pr.is_alive():
                pr.join(); running.remove(pr)
        time.sleep(0.5)
    print(f"frames done in {time.time() - t0:.0f}s", flush=True)
    lst = BUILD / "parts.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    clean = BUILD / "video_clean.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(clean)], check=True)
    tag = "_draft" if a.fast else ""
    ss = ["-ss", str(a.start), "-t", str(end - a.start)]
    ass = str(BUILD / "subtitles.ass").replace(":", r"\:")
    enc = ["-c:v", "libx264", "-preset", "slow", "-b:v", a.bitrate, "-maxrate", "5000k", "-bufsize", "8000k",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
    # 1) с субтитрами, 2) без субтитров (субтитры — отдельным файлом .srt)
    for name, vf in ((names[0].replace(".mp4", tag + ".mp4"), f"ass={ass}"), (names[1].replace(".mp4", tag + ".mp4"), None)):
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(clean)] + ss + ["-i", str(BUILD / "mix.wav")]
        if vf:
            cmd += ["-vf", vf if not a.fast else vf + ":original_size=1920x1080"]
        cmd += ["-map", "0:v", "-map", "1:a", "-shortest"] + enc + [str(OUT / name)]
        subprocess.run(cmd, check=True)
        print("wrote", OUT / name, flush=True)


if __name__ == "__main__":
    main()
