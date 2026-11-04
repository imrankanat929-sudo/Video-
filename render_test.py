"""NOXARGENT_STUDIO — тестовая сцена.

Тёмная 2D-комната: окно с лунным светом, луч фонарика, плёночное зерно,
медленный зум. 10 с, 1920x1080, 30 FPS. Результат: test.mp4 на Рабочем столе.
Запуск: python render_test.py
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

W, H, FPS, SECONDS = 1920, 1080, 30, 10
ZOOM_END = 1.12  # к концу ролика картинка приближается на 12%


def desktop() -> Path:
    if os.environ.get("NOX_DESKTOP"):  # путь от setup_windows.bat
        return Path(os.environ["NOX_DESKTOP"])
    home = Path.home()
    for p in (home / "OneDrive" / "Desktop", home / "OneDrive" / "Рабочий стол",
              home / "Desktop", home / "Рабочий стол"):
        if p.is_dir():
            return p
    (home / "Desktop").mkdir(parents=True, exist_ok=True)
    return home / "Desktop"


def build_room(w, h):
    """Базовый кадр комнаты (float32, 0..1, BGR) и маска окна."""
    img = np.zeros((h, w, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    floor_y = int(h * 0.72)
    img[:floor_y] = (0.055, 0.050, 0.060)            # стена
    img[floor_y:] = (0.030, 0.032, 0.040)            # пол
    for i in range(0, w, int(w * 0.06)):             # доски пола
        cv2.line(img, (i, floor_y), (int(w / 2 + (i - w / 2) * 2.2), h), (0.018,) * 3, 2)
    cv2.line(img, (0, floor_y), (w, floor_y), (0.02,) * 3, 4)  # плинтус

    # Окно
    wx0, wy0, wx1, wy1 = int(w * .58), int(h * .14), int(w * .80), int(h * .55)
    sky = np.zeros_like(img)
    t = np.clip((yy - wy0) / (wy1 - wy0), 0, 1)[..., None]
    sky[:] = (0.30, 0.20, 0.12) * (1 - t) + np.array((0.16, 0.10, 0.06)) * t
    cv2.circle(sky, (int(w * .74), int(h * .23)), int(h * .035), (0.85, 0.88, 0.9), -1, cv2.LINE_AA)
    win = np.zeros((h, w), np.float32)
    cv2.rectangle(win, (wx0, wy0), (wx1, wy1), 1, -1)
    img = img * (1 - win[..., None]) + sky * win[..., None]
    frame = (0.012, 0.012, 0.015)
    cv2.rectangle(img, (wx0, wy0), (wx1, wy1), frame, 14)
    cv2.line(img, ((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1), frame, 10)
    cv2.line(img, (wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2), frame, 10)
    cv2.rectangle(img, (wx0 - 30, wy1), (wx1 + 30, wy1 + 18), (0.02,) * 3, -1)  # подоконник

    # Лунный свет на полу (трапеция от окна)
    moon = np.zeros((h, w), np.float32)
    pts = np.array([[wx0, floor_y + 10], [wx1, floor_y + 10],
                    [int(wx1 - w * .05), h], [int(wx0 - w * .25), h]], np.int32)
    cv2.fillPoly(moon, [pts], 1)
    moon = cv2.GaussianBlur(moon, (0, 0), 25) * 0.10
    img += moon[..., None] * np.array((1.0, 0.85, 0.7), np.float32)

    # Мебель-силуэты: стол, стул, дверь, картина
    dark = (0.008, 0.008, 0.010)
    cv2.rectangle(img, (int(w * .12), int(h * .58)), (int(w * .38), int(h * .62)), dark, -1)
    for x in (int(w * .14), int(w * .36)):
        cv2.rectangle(img, (x - 8, int(h * .62)), (x + 8, int(h * .82)), dark, -1)
    cv2.rectangle(img, (int(w * .40), int(h * .50)), (int(w * .42), int(h * .80)), dark, -1)
    cv2.rectangle(img, (int(w * .40), int(h * .64)), (int(w * .47), int(h * .66)), dark, -1)
    cv2.rectangle(img, (int(w * .46), int(h * .66)), (int(w * .47), int(h * .80)), dark, -1)
    cv2.rectangle(img, (int(w * .02), int(h * .18)), (int(w * .10), int(h * .72)), (0.035, 0.030, 0.030), -1)
    cv2.circle(img, (int(w * .085), int(h * .46)), 6, (0.06,) * 3, -1)
    cv2.rectangle(img, (int(w * .20), int(h * .25)), (int(w * .30), int(h * .40)), (0.04, 0.035, 0.03), 6)

    # Мягкий свет из окна на стене
    glow = np.exp(-(((xx - w * .69) / (w * .25)) ** 2 + ((yy - h * .35) / (h * .35)) ** 2))
    img += glow[..., None] * np.array((0.05, 0.035, 0.025), np.float32)

    vignette = 1 - 0.75 * np.clip(((xx - w / 2) / (w * .62)) ** 2 + ((yy - h / 2) / (h * .62)) ** 2, 0, 1)
    return img, vignette.astype(np.float32)


def main():
    studio = desktop() / "NOXARGENT_STUDIO"
    for sub in ("scenes", "renders", "audio", "assets", "scripts"):
        (studio / sub).mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("FFmpeg не найден. Запустите setup_windows.bat ещё раз.")

    t0 = time.perf_counter()
    room, vignette = build_room(W, H)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rng = np.random.default_rng(7)
    dust = rng.random((140, 3)) * (W, H, 1)
    total = FPS * SECONDS
    renders = studio / "renders" / "test.mp4"

    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(renders)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for f in range(total):
        t = f / FPS
        # Луч фонарика медленно «ищет» по комнате
        cx = W * (0.30 + 0.12 * np.sin(t * 0.55) + 0.02 * np.sin(t * 3.1))
        cy = H * (0.55 + 0.07 * np.sin(t * 0.8 + 1) + 0.01 * np.sin(t * 4.3))
        r = H * 0.22
        d2 = ((xx - cx) / (r * 1.25)) ** 2 + ((yy - cy) / r) ** 2
        flick = 1 + 0.04 * np.sin(t * 37) * np.sin(t * 13)
        beam = (np.exp(-d2 * 1.6) * 1.6 + np.exp(-d2 * 0.25) * 0.25) * flick
        frame = room * (1 + beam[..., None] * np.array((5.0, 7.0, 9.0), np.float32))
        frame += beam[..., None] * np.array((0.02, 0.035, 0.05), np.float32)

        for px, py, s in dust:  # пылинки в луче
            x = int((px + t * 18 * (s - .5)) % W)
            y = int((py - t * 10 * s) % H)
            b = float(np.exp(-(((x - cx) / (r * 1.25)) ** 2 + ((y - cy) / r) ** 2) * 1.6))
            if b > 0.05:
                cv2.circle(frame, (x, y), 2, (0.5 * b, 0.6 * b, 0.7 * b), -1, cv2.LINE_AA)

        frame *= vignette[..., None]

        # Медленный зум к окну
        z = 1 + (ZOOM_END - 1) * (0.5 - 0.5 * np.cos(np.pi * f / (total - 1)))
        M = cv2.getRotationMatrix2D((W * 0.55, H * 0.45), 0, z)
        frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # Плёночное зерно + лёгкое мерцание экспозиции
        grain = rng.normal(0, 0.035, (H // 2, W // 2)).astype(np.float32)
        grain = cv2.resize(grain, (W, H), interpolation=cv2.INTER_LINEAR)
        frame = frame * (1 + 0.03 * rng.standard_normal()) + grain[..., None] * (0.4 + frame)
        out = (np.clip(frame, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)
        proc.stdin.write(out.tobytes())

    proc.stdin.close()
    proc.wait()
    elapsed = time.perf_counter() - t0
    final = desktop() / "test.mp4"
    shutil.copy2(renders, final)
    print(f"Готово: {final}")
    print(f"Время рендера: {elapsed:.1f} с")


if __name__ == "__main__":
    main()
