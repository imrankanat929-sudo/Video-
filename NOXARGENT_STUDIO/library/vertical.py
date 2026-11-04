"""Вертикальная версия серии (9:16) для TikTok / Shorts / Reels.

Берёт чистый рендер 16:9 без субтитров и для каждого плана:
  ("crop", x)  — вырезает вертикальное окно вокруг x (главный объект плана);
  ("fit",)     — вписывает кадр целиком по ширине поверх размытого фона.
Субтитры вшиваются заново: крупнее, выше интерфейса TikTok.
"""
import subprocess
from pathlib import Path

import cv2
import numpy as np

from core import FPS, H, W

VW, VH = 1080, 1920
CW = int(H * VW / VH) // 2 * 2  # ширина вертикального окна в кадре 16:9 (606)


def compose(frame, layout):
    if layout[0] == "crop":
        x = int(min(max(layout[1] - CW / 2, 0), W - CW))
        return cv2.resize(frame[:, x:x + CW], (VW, VH), interpolation=cv2.INTER_LINEAR)
    # fit: кадр по ширине + размытый затемнённый фон из того же кадра
    small = cv2.resize(frame[:, (W - CW) // 2:(W + CW) // 2], (VW // 8, VH // 8), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 4), (VW, VH), interpolation=cv2.INTER_LINEAR)
    bg = cv2.convertScaleAbs(bg, alpha=0.45)
    fh = int(VW * H / W)
    y = (VH - fh) // 2 - 80
    bg[y:y + fh] = cv2.resize(frame, (VW, fh), interpolation=cv2.INTER_AREA)
    return bg


def make_vertical(clean_mp4, audio, layout_fn, ass, out, fontsdir):
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(clean_mp4), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           stdout=subprocess.PIPE)
    a = Path(ass).as_posix().replace(":", "\\:")
    fd = Path(fontsdir).as_posix().replace(":", "\\:")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{VW}x{VH}",
                            "-r", str(FPS), "-i", "-", "-i", str(audio), "-vf", f"subtitles='{a}':fontsdir='{fd}'",
                            "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "5M",
                            "-bufsize", "10M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                            "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    n = W * H * 3
    f = 0
    while True:
        buf = dec.stdout.read(n)
        if len(buf) < n:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        enc.stdin.write(compose(frame, layout_fn(f / FPS)).tobytes())
        f += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    return f
