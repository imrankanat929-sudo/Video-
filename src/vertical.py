"""Вертикальная версия 9:16 (1080x1920) для TikTok / Reels / Shorts + вертикальная обложка.
Берёт чистый рендер build/video_clean.mp4 и звук build/mix.wav (их делает src.render).
python -m src.vertical"""
import subprocess
import numpy as np
import cv2
from PIL import Image
from .config import W, H, FPS, OUT, BUILD, FONT_TITLE, FONT_BOLD, FONT_SEMI
from .cues import C
from .gfx import Pen
from . import subtitles as SUB

VW, VH = 1080, 1920
MID_Y = 500          # верх кадра с видео
MID_H = 810          # 4:3-кроп центра кадра -> 1080x810
SUB_Y = MID_Y + MID_H + 70


def header():
    p = Pen(VW, VH, ss=2)
    p.text(VW / 2, 215, "А ЧТО, ЕСЛИ…?", FONT_TITLE, 104, (246, 238, 226), anchor="mm")
    p.rrect(150, 300, VW - 150, 396, 14, (190, 28, 20))
    p.text(VW / 2, 348, "УПАДЁТ АТОМНАЯ БОМБА", FONT_TITLE, 52, (255, 240, 228), anchor="mm")
    p.text(VW / 2, 440, "СЕРИЯ №1", FONT_BOLD, 34, (230, 120, 72), anchor="mm")
    a = p.arr()
    g = cv2.GaussianBlur(a, (0, 0), 16)
    g[..., :3] = g[..., 3:4] * np.array([0.6, 0.05, 0.02], np.float32)
    return a + g * 0.8 * (1 - a[..., 3:4])


def background(frame):
    small = cv2.resize(frame, (192, 108), interpolation=cv2.INTER_AREA)
    crop = small[:, 66:126]  # центр 60x108 ≈ 9:16
    bg = cv2.resize(crop, (VW, VH), interpolation=cv2.INTER_LINEAR)
    bg = cv2.GaussianBlur(bg, (0, 0), 18).astype(np.float32) / 255 * 0.42
    return bg


def compose_v(frame, t, c, hdr):
    out = background(frame)
    f = frame.astype(np.float32) / 255
    if t < c["final"] - 0.05:
        mid = cv2.resize(f[:, 240:1680], (VW, MID_H), interpolation=cv2.INTER_AREA)
        y0, hh = MID_Y, MID_H
    else:  # экран выбора — целиком, чтобы оба варианта были видны
        x0, x1 = 90, W - 90  # обе карточки целиком, но крупнее
        hh = int(VW * H / (x1 - x0)) // 2 * 2
        mid = cv2.resize(f[:, x0:x1], (VW, hh), interpolation=cv2.INTER_AREA)
        y0 = MID_Y + 80
    out[y0:y0 + hh] = mid
    # мягкие края кадра
    fade = 40
    for i in range(fade):
        k = i / fade
        out[y0 + i] = out[y0 + i] * k + out[y0 - 1] * (1 - k) if y0 > 0 else out[y0 + i]
        j = y0 + hh - 1 - i
        out[j] = out[j] * k + out[y0 + hh] * (1 - k)
    out = hdr[..., :3] + out * (1 - hdr[..., 3:4])
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


def ass_vertical(c):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {VW}
PlayResY: {VH}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Inter ExtraBold,64,&H00F2F6FA,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,4,1.5,8,70,70,{SUB_Y},204
Style: Radio,Inter ExtraBold,64,&H0090D8FF,&H000000FF,&H00000000,&H96000000,0,1,0,0,100,100,0,0,1,4,1.5,8,70,70,{SUB_Y},204

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    radio = [(c["broadcast1"] - 0.1, c["silence"] - 0.1), (c["broadcast2"] - 0.1, c["broadcast2_end"] + 0.2)]
    path = BUILD / "subtitles_vertical.ass"
    with open(path, "w", encoding="utf-8") as f:
        f.write(head)
        for a, b, t in SUB.lines():
            if a >= c["final"] - 0.1:
                continue
            st = "Radio" if any(x <= a + 0.2 < y for x, y in radio) else "Main"
            f.write(f"Dialogue: 0,{SUB.ts_ass(a)},{SUB.ts_ass(b)},{st},,0,0,0,,{{\\fad(100,100)}}" +
                    "\\N".join(SUB.wrap(t, 26)) + "\n")
    return path


def build_video(bitrate="2700k"):
    c = C()
    hdr = header()
    ass = str(ass_vertical(c)).replace(":", r"\:")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(BUILD / "video_clean.mp4"), "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    out = OUT / "what_if_ep1_atomic_tiktok_9x16.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                            "-r", str(FPS), "-i", "-", "-i", str(BUILD / "mix.wav"), "-vf", f"ass={ass}",
                            "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "libx264", "-preset", "slow",
                            "-b:v", bitrate, "-maxrate", "5000k", "-bufsize", "8000k", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)],
                           stdin=subprocess.PIPE)
    n = W * H * 3
    i = 0
    while True:
        buf = dec.stdout.read(n)
        if len(buf) < n:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        enc.stdin.write(compose_v(fr, i / FPS, c, hdr).tobytes())
        i += 1
        if i % 1200 == 0:
            print(f"{i} frames", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()
    return out


def build_cover():
    """Обложка 9:16 из той же картинки, что и горизонтальное превью."""
    from .thumbnail import base_image
    base = base_image()  # float RGB 1920x1080, без текста
    cx = 1180
    crop = base[:, cx - 304:cx + 304]
    img = cv2.resize(crop, (VW, VH), interpolation=cv2.INTER_LANCZOS4)
    rng = np.random.default_rng(3)
    img = np.clip(img + rng.normal(0, 0.025, img.shape).astype(np.float32), 0, 1)
    yy = np.linspace(0, 1, VH, dtype=np.float32)[:, None, None]
    img = img * (1 - 0.75 * np.clip(1 - yy / 0.45, 0, 1) ** 1.5)  # затемнение сверху под текст
    p = Pen(VW, VH, ss=2)
    p.text(VW / 2, 300, "А ЧТО,", FONT_TITLE, 170, (246, 240, 230), anchor="mm")
    p.text(VW / 2, 470, "ЕСЛИ…", FONT_TITLE, 170, (246, 240, 230), anchor="mm")
    p.rrect(110, 580, VW - 110, 790, 16, (196, 30, 22))
    p.text(VW / 2, 640, "УПАДЁТ", FONT_TITLE, 82, (255, 240, 228), anchor="mm")
    p.text(VW / 2, 730, "АТОМНАЯ БОМБА?", FONT_TITLE, 82, (255, 240, 228), anchor="mm")
    p.rrect(VW / 2 - 130, 830, VW / 2 + 130, 900, 10, (20, 16, 16, 230))
    p.text(VW / 2, 865, "СЕРИЯ №1", FONT_BOLD, 38, (232, 120, 70), anchor="mm")
    t = p.arr()
    g = cv2.GaussianBlur(t, (0, 0), 20)
    g[..., :3] = g[..., 3:4] * np.array([0.6, 0.06, 0.03], np.float32)
    t = t + g * 0.8 * (1 - t[..., 3:4])
    img = t[..., :3] + img * (1 - t[..., 3:4])
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(OUT / "thumbnail_tiktok_9x16.jpg", quality=93)
    return OUT / "thumbnail_tiktok_9x16.jpg"


if __name__ == "__main__":
    print(build_cover())
    print(build_video())
