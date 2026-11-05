"""Делит готовое видео серии 2 на две части (< 3 мин каждая).
Часть 1 кончается на сообщении «Не оборачивайся. Беги.» + заставка «Часть 2».
Часть 2 начинается с плашки «Часть 2» и кончается экраном выбора.
EP=ep2|ep2en python tools/split.py"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import cv2
from PIL import Image
from src.config import W, H, FPS, OUT, BUILD, EP, FONT_TITLE, FONT_BOLD, L
from src.cues import C
from src.gfx import Pen

SRC = OUT / L("za_mnoy_kto_to_idet_9x16.mp4", "someone_is_following_you_9x16.mp4")
STEM = L("za_mnoy_kto_to_idet", "someone_is_following_you")
CARD = 3.0  # длина заставки в конце части 1
ENC = ["-c:v", "libx264", "-preset", "slow", "-b:v", "2600k", "-maxrate", "5000k", "-bufsize", "8000k",
       "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]


def glow_text(p):
    a = p.arr()
    g = cv2.GaussianBlur(a, (0, 0), 18)
    g[..., :3] = g[..., 3:4] * np.array([0.6, 0.38, 0.1], np.float32)
    return a + g * 0.8 * (1 - a[..., 3:4])


def save_rgba(a, path):
    """premultiplied float RGBA -> PNG с прозрачностью"""
    al = np.clip(a[..., 3:4], 1e-6, 1)
    rgb = np.clip(a[..., :3] / al, 0, 1)
    out = np.concatenate([rgb, np.clip(a[..., 3:4], 0, 1)], 2)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA").save(path)


def end_card(path):
    p = Pen(W, H, ss=2)
    p.rect(0, 0, W, H, (4, 5, 8, 205))
    p.text(W / 2, H * 0.40, L("ПРОДОЛЖЕНИЕ", "TO BE"), FONT_TITLE, 120, (244, 240, 232), anchor="mm")
    p.text(W / 2, H * 0.40 + 135, L("СЛЕДУЕТ…", "CONTINUED…"), FONT_TITLE, 120, (244, 240, 232), anchor="mm")
    p.rrect(170, H * 0.40 + 250, W - 170, H * 0.40 + 360, 16, (232, 168, 60))
    p.text(W / 2, H * 0.40 + 305, L("ЧАСТЬ 2 — В СЛЕДУЮЩЕМ ВИДЕО", "PART 2 — NEXT VIDEO"), FONT_TITLE,
           L(44, 52), (16, 14, 12), anchor="mm")
    p.text(W / 2, H * 0.40 + 450, L("Подпишись, чтобы не пропустить", "Follow so you don't miss it"), FONT_BOLD, 46,
           (220, 216, 208), anchor="mm")
    save_rgba(glow_text(p), path)


def part2_badge(path):
    p = Pen(W, H, ss=2)
    p.rrect(W / 2 - 230, 120, W / 2 + 230, 250, 18, (232, 168, 60))
    p.text(W / 2, 186, L("ЧАСТЬ 2", "PART 2"), FONT_TITLE, 84, (16, 14, 12), anchor="mm")
    save_rgba(glow_text(p), path)


def run(cmd):
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + cmd, check=True)


def main():
    c = C()
    cut = c["stop"] - 0.1          # сразу после сообщения, до «Ты резко остановился» / «You froze»
    end = c["END"]
    BUILD.mkdir(parents=True, exist_ok=True)
    card, badge = BUILD / "end_card.png", BUILD / "part2_badge.png"
    end_card(card); part2_badge(badge)
    p1, p2 = OUT / f"{STEM}_part1.mp4", OUT / f"{STEM}_part2.mp4"
    # часть 1: видео до cut, затем стоп-кадр + заставка; звук затухает в тишину
    fc1 = (f"[0:v]trim=0:{cut},setpts=PTS-STARTPTS,split[v][l];"
           f"[l]trim=start={cut - 1 / FPS},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={CARD}[f];"
           f"[1:v]format=rgba,fade=in:st=0:d=0.5:alpha=1[c];"
           f"[f][c]overlay=0:0:shortest=0:eof_action=pass,trim=0:{CARD},setpts=PTS-STARTPTS[e];"
           f"[v][e]concat=n=2:v=1:a=0[vo];"
           f"[0:a]atrim=0:{cut},afade=out:st={cut - 0.4}:d=0.4,apad=pad_dur={CARD},atrim=0:{cut + CARD}[ao]")
    run(["-i", str(SRC), "-loop", "1", "-t", str(CARD), "-i", str(card), "-filter_complex", fc1,
         "-map", "[vo]", "-map", "[ao]"] + ENC + [str(p1)])
    # часть 2: от cut до конца, плашка «Часть 2» первые 3 с
    fc2 = (f"[1:v]format=rgba,fade=in:st=0:d=0.3:alpha=1,fade=out:st=2.6:d=0.4:alpha=1[b];"
           f"[0:v][b]overlay=0:0:enable='lt(t,3)'[vo];[0:a]afade=in:st=0:d=0.3[ao]")
    run(["-ss", str(cut), "-to", str(end), "-i", str(SRC), "-loop", "1", "-t", "3", "-i", str(badge),
         "-filter_complex", fc2, "-map", "[vo]", "-map", "[ao]"] + ENC + [str(p2)])
    for p in (p1, p2):
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True).stdout.strip()
        print(p, f"{float(d):.1f}s")


if __name__ == "__main__":
    main()
