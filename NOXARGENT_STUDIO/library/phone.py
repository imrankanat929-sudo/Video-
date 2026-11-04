"""Телефон Армана: корпус и экраны (уведомление, звонок, камера, сообщение, диктофон).

Экран рисуется в 600×1300 и кладётся в корпус. Все надписи читаемые, без случайных символов.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw

from core import AA, draw_text, font, pil_to_bgra

SW, SH = 600, 1300           # разрешение экрана
BEZEL = 26
PW, PH = SW + BEZEL * 2, SH + BEZEL * 2
RED = (226, 58, 52)          # RGB: красный — только тревога/запись
TIME = "03:17"


def _screen(bg=(6, 8, 12)):
    return Image.new("RGB", (SW, SH), bg)


def _status(im, net="Нет сети"):
    d = ImageDraw.Draw(im)
    draw_text(im, (40, 26), TIME, 30, (230, 230, 235))
    if net:
        f = font(26)
        tw = d.textlength(net, font=f)
        draw_text(im, (SW - 40 - tw - 50, 28), net, 26, (200, 200, 205))
    # батарея
    d.rounded_rectangle((SW - 82, 30, SW - 40, 52), 5, outline=(200, 200, 205), width=3)
    d.rectangle((SW - 78, 34, SW - 58, 48), fill=(200, 200, 205))


def _wallpaper(im):
    arr = np.array(im).astype(np.float32)
    yy = np.linspace(0, 1, SH)[:, None, None]
    arr += (np.array([10, 14, 26]) * (1 - yy))[...]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def _card(im, y, title, body, accent=RED, sub="сейчас"):
    d = ImageDraw.Draw(im)
    pad = 30
    lines_y = draw_text(Image.new("RGB", (SW, SH)), (0, 0), body, 40, max_w=SW - 2 * 40 - 2 * pad)
    hgt = int(110 + lines_y + 20)
    d.rounded_rectangle((40, y, SW - 40, y + hgt), 34, fill=(34, 36, 42))
    d.ellipse((40 + pad, y + 28, 40 + pad + 44, y + 72), fill=accent)
    draw_text(im, (40 + pad + 14, y + 30), "!", 32, (255, 255, 255), "bold")
    draw_text(im, (40 + pad + 62, y + 34), title, 30, (235, 235, 240), "bold")
    f = font(26)
    tw = d.textlength(sub, font=f)
    draw_text(im, (SW - 40 - pad - tw, y + 37), sub, 26, (150, 150, 158))
    draw_text(im, (40 + pad, y + 100), body, 40, (255, 255, 255), "bold", max_w=SW - 2 * 40 - 2 * pad)
    return y + hgt


def screen_lock_notification(title, body, net=None, big_time=True):
    im = _wallpaper(_screen())
    _status(im, net)
    if big_time:
        draw_text(im, (0, 150), TIME, 150, (225, 228, 235), "semibold", max_w=SW, align="center")
    _card(im, 420, title, body)
    return im


def screen_call(state):
    """state: 'dial' | 'fail' | 'fail_net'."""
    im = _screen((10, 12, 16))
    _status(im, "Нет сети")
    draw_text(im, (0, 230), "Мама", 70, (240, 240, 245), "semibold", max_w=SW, align="center")
    sub = {"dial": "Вызов…", "fail": "Вызов не удался", "fail_net": "Вызов не удался"}[state]
    col = (200, 200, 205) if state == "dial" else (240, 120, 110)
    draw_text(im, (0, 330), sub, 44, col, "bold", max_w=SW, align="center")
    d = ImageDraw.Draw(im)
    d.ellipse((SW / 2 - 70, SH - 260, SW / 2 + 70, SH - 120), fill=RED)
    d.line((SW / 2 - 34, SH - 190, SW / 2 + 34, SH - 190), fill=(255, 255, 255), width=12)
    if state == "fail_net":
        d.rounded_rectangle((40, 500, SW - 40, 740), 30, fill=(34, 36, 42))
        draw_text(im, (70, 532), "Нет подключения к интернету", 46, (255, 255, 255), "bold", max_w=SW - 140)
    return im


def screen_message(sender, text):
    """Открытый чат: одно входящее сообщение крупно."""
    im = _screen((8, 9, 12))
    _status(im, "Нет сети")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 80, SW, 200), fill=(18, 19, 24))
    draw_text(im, (0, 112), sender, 38, (240, 240, 245), "bold", max_w=SW, align="center")
    tmp = Image.new("RGB", (SW, SH))
    bottom = draw_text(tmp, (0, 0), text, 50, max_w=SW - 150)
    y0 = 300
    d.rounded_rectangle((36, y0, SW - 60, y0 + bottom + 60), 36, fill=(40, 42, 50))
    draw_text(im, (66, y0 + 30), text, 50, (255, 255, 255), "bold", max_w=SW - 150)
    draw_text(im, (40, y0 + bottom + 80), TIME, 26, (140, 140, 150))
    return im


def screen_incoming(sender, preview):
    im = _wallpaper(_screen())
    _status(im, "Нет сети")
    draw_text(im, (0, 150), TIME, 150, (225, 228, 235), "semibold", max_w=SW, align="center")
    _card(im, 420, sender, preview)
    return im


def screen_recorder(seconds, levels):
    im = _screen((10, 10, 12))
    _status(im, "Нет сети")
    draw_text(im, (0, 150), "Диктофон", 44, (235, 235, 240), "bold", max_w=SW, align="center")
    d = ImageDraw.Draw(im)
    mid = 600
    for i, lv in enumerate(levels):
        x = 40 + i * 13
        hh = 6 + lv * 180
        d.rounded_rectangle((x, mid - hh, x + 7, mid + hh), 3, fill=(230, 80, 70))
    draw_text(im, (0, 860), f"00:{seconds:02d}", 80, (245, 245, 248), "semibold", max_w=SW, align="center")
    d.ellipse((SW / 2 - 70, SH - 280, SW / 2 + 70, SH - 140), outline=(230, 230, 235), width=6)
    d.rounded_rectangle((SW / 2 - 30, SH - 240, SW / 2 + 30, SH - 180), 8, fill=RED)
    d.ellipse((50, 100, 72, 122), fill=RED)
    draw_text(im, (82, 96), "REC", 24, (245, 120, 110), "bold")
    return im


def screen_off():
    im = _screen((3, 3, 4))
    arr = np.array(im).astype(np.float32)
    yy, xx = np.mgrid[0:SH, 0:SW]
    refl = np.clip(1 - np.abs((xx * 0.6 + yy * 0.4) - 600) / 300, 0, 1) * 10
    arr += refl[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def camera_ui(zoom_label, focus_box=None):
    """Прозрачный слой интерфейса камеры поверх видоискателя."""
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, SW, 120), fill=(0, 0, 0, 150))
    d.rectangle((0, SH - 300, SW, SH), fill=(0, 0, 0, 160))
    d.ellipse((SW / 2 - 70, SH - 220, SW / 2 + 70, SH - 80), outline=(240, 240, 240, 255), width=8)
    d.ellipse((SW / 2 - 56, SH - 206, SW / 2 + 56, SH - 94), fill=(240, 240, 240, 255))
    d.rounded_rectangle((SW / 2 - 60, SH - 380, SW / 2 + 60, SH - 320), 30, fill=(0, 0, 0, 170))
    draw_text(im, (0, SH - 372), zoom_label, 34, (255, 210, 80, 255), "bold", max_w=SW, align="center")
    draw_text(im, (40, 50), "ФОТО", 28, (255, 210, 80, 255), "bold")
    if focus_box is not None:
        x0, y0, x1, y1 = focus_box
        L = 30
        c = (255, 210, 80, 255)
        for (px, py, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            d.line((px, py, px + dx * L, py), fill=c, width=5)
            d.line((px, py, px, py + dy * L), fill=c, width=5)
    return pil_to_bgra(im)


def to_bgr(im):
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def phone_sprite(screen_bgr, brightness=1.0):
    """Корпус + экран → BGRA-спрайт PW×PH."""
    spr = np.zeros((PH, PW, 4), np.uint8)
    cv2.rectangle(spr, (0, 0), (PW - 1, PH - 1), (0, 0, 0, 0), -1)
    mask = np.zeros((PH, PW), np.uint8)
    _rr(mask, 0, 0, PW - 1, PH - 1, 70, 255)
    body = np.zeros((PH, PW, 3), np.uint8)
    body[:] = (22, 22, 24)
    _rr(body, 4, 4, PW - 5, PH - 5, 66, (34, 34, 38))
    _rr(body, BEZEL - 6, BEZEL - 6, PW - BEZEL + 5, PH - BEZEL + 5, 52, (6, 6, 7))
    scr = cv2.convertScaleAbs(screen_bgr, alpha=brightness) if brightness != 1.0 else screen_bgr
    smask = np.zeros((SH, SW), np.uint8)
    _rr(smask, 0, 0, SW - 1, SH - 1, 46, 255)
    roi = body[BEZEL:BEZEL + SH, BEZEL:BEZEL + SW]
    m = (smask[..., None].astype(np.float32) / 255)
    body[BEZEL:BEZEL + SH, BEZEL:BEZEL + SW] = (roi * (1 - m) + scr * m).astype(np.uint8)
    cv2.ellipse(body, (PW // 2, BEZEL + 34), (16, 16), 0, 0, 360, (4, 4, 5), -1, AA)  # камера
    spr[..., :3] = body
    spr[..., 3] = mask
    return spr


def _rr(img, x0, y0, x1, y1, r, col):
    cv2.rectangle(img, (x0 + r, y0), (x1 - r, y1), col, -1)
    cv2.rectangle(img, (x0, y0 + r), (x1, y1 - r), col, -1)
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        cv2.circle(img, (cx, cy), r, col, -1, AA)


# ---------- серия 2: чужой телефон, чат, видео, звонок, голосовое ----------
def add_cracks(spr, seed=17):
    """Трещины на экране спрайта (паутина от точки удара)."""
    rng = np.random.default_rng(seed)
    out = spr.copy()
    cx, cy = BEZEL + SW * 0.72, BEZEL + SH * 0.18
    for i in range(11):
        a = i / 11 * 6.283 + rng.normal(0, 0.2)
        x, y = cx, cy
        for _ in range(int(rng.integers(3, 7))):
            L = rng.uniform(60, 220)
            a += rng.normal(0, 0.35)
            nx, ny = x + np.cos(a) * L, y + np.sin(a) * L
            cv2.line(out, (int(x), int(y)), (int(nx), int(ny)), (200, 205, 210, 255), 2, AA)
            x, y = nx, ny
            if not (BEZEL < x < BEZEL + SW and BEZEL < y < BEZEL + SH):
                break
    for r in (18, 34):
        cv2.circle(out, (int(cx), int(cy)), r, (190, 195, 200, 255), 2, AA)
    return out


def phone_back(sticker="03:17"):
    """Задняя крышка чужого телефона с маленькой наклейкой «03:17»."""
    spr = np.zeros((PH, PW, 4), np.uint8)
    body = np.zeros((PH, PW, 3), np.uint8)
    _rr(body, 0, 0, PW - 1, PH - 1, 70, (40, 38, 40))
    _rr(body, 6, 6, PW - 7, PH - 7, 64, (52, 50, 54))
    _rr(body, 50, 50, 270, 300, 50, (30, 30, 32))           # блок камер
    for cx, cy in ((110, 120), (210, 120), (110, 230)):
        cv2.circle(body, (cx, cy), 40, (14, 14, 16), -1, AA)
        cv2.circle(body, (cx, cy), 22, (40, 44, 52), -1, AA)
    im = Image.new("RGB", (240, 110), (232, 228, 214))       # наклейка
    draw_text(im, (0, 14), sticker, 72, (20, 20, 22), "bold", max_w=240, align="center")
    st = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    M = cv2.getRotationMatrix2D((120, 55), -7, 1.0)
    st = cv2.warpAffine(st, M, (240, 110), borderValue=(52, 50, 54))
    body[760:870, 330:570] = st
    mask = np.zeros((PH, PW), np.uint8)
    _rr(mask, 0, 0, PW - 1, PH - 1, 70, 255)
    spr[..., :3] = body
    spr[..., 3] = mask
    return spr


def screen_video_ready():
    """Чужой телефон: экран сам включился, открыто видео (значок воспроизведения)."""
    im = _screen((4, 4, 6))
    _status(im, None)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 380, SW, 380 + 340), fill=(22, 24, 30))
    d.ellipse((SW / 2 - 70, 480, SW / 2 + 70, 620), fill=(240, 240, 240))
    d.polygon([(SW / 2 - 22, 515), (SW / 2 - 22, 585), (SW / 2 + 38, 550)], fill=(20, 20, 24))
    draw_text(im, (40, 760), "ВИДЕО", 44, (235, 235, 240), "bold")
    draw_text(im, (40, 820), "00:00 / 00:47", 32, (160, 160, 168))
    return im


def screen_chat(sender, msgs, typing=None):
    """Чат. msgs: [("in"|"out", текст)] или ("photo", BGR-картинка, подпись|None)."""
    im = _screen((8, 9, 12))
    _status(im, None)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 80, SW, 190), fill=(18, 19, 24))
    draw_text(im, (0, 108), sender, 38, (240, 240, 245), "bold", max_w=SW, align="center")
    blocks = []
    for m in msgs:
        if m[0] == "photo":
            pic = cv2.cvtColor(m[1], cv2.COLOR_BGR2RGB)
            pw_ = SW - 120
            ph_ = int(pw_ * pic.shape[0] / pic.shape[1])
            blocks.append(("photo", Image.fromarray(pic).resize((pw_, ph_)), m[2] if len(m) > 2 else None, ph_ + 40 + (90 if len(m) > 2 and m[2] else 0)))
        else:
            hh = draw_text(Image.new("RGB", (SW, SH)), (0, 0), m[1], 44, max_w=SW - 190)
            blocks.append((m[0], m[1], None, int(hh + 64)))
    if typing is not None:
        blocks.append(("out", typing + "|", None, 110))
    y = SH - 160 - sum(b[3] + 24 for b in blocks)
    y = max(220, y)
    for kind, payload, cap, hgt in blocks:
        if kind == "photo":
            x0 = 40
            d.rounded_rectangle((x0 - 10, y - 10, SW - 70, y + hgt - 30), 26, fill=(40, 42, 50))
            im.paste(payload, (x0 + 10, y + 10))
            if cap:
                draw_text(im, (x0 + 10, y + payload.size[1] + 24), cap, 38, (255, 90, 80), "bold", max_w=SW - 140)
        else:
            out = kind == "out"
            x0, x1 = (110, SW - 36) if out else (36, SW - 110)
            d.rounded_rectangle((x0, y, x1, y + hgt), 34, fill=(36, 70, 140) if out else (40, 42, 50))
            draw_text(im, (x0 + 30, y + 26), payload, 44, (255, 255, 255), "bold", max_w=x1 - x0 - 60)
        y += hgt + 24
    d.rounded_rectangle((30, SH - 130, SW - 30, SH - 50), 40, fill=(26, 27, 32))
    draw_text(im, (64, SH - 112), "Сообщение", 32, (120, 120, 128))
    return im


def screen_call_incoming(name="Скрытый номер", sub="входящий вызов", in_call=False):
    im = _screen((10, 12, 16))
    _status(im, None)
    draw_text(im, (0, 260), name, 60, (240, 240, 245), "bold", max_w=SW, align="center")
    draw_text(im, (0, 350), sub, 40, (170, 170, 178), "bold", max_w=SW, align="center")
    d = ImageDraw.Draw(im)
    btns = ((SW * 0.5, RED),) if in_call else ((SW * 0.27, RED), (SW * 0.73, (52, 180, 90)))
    for cx, col in btns:
        d.ellipse((cx - 70, SH - 280, cx + 70, SH - 140), fill=col)
    return im


def screen_call_ended():
    im = _screen((10, 12, 16))
    _status(im, None)
    draw_text(im, (0, 300), "Скрытый номер", 52, (200, 200, 205), "bold", max_w=SW, align="center")
    draw_text(im, (0, 390), "Вызов завершён", 44, (240, 120, 110), "bold", max_w=SW, align="center")
    return im


def screen_voice(levels, progress):
    im = _screen((6, 6, 8))
    _status(im, None)
    draw_text(im, (0, 330), "ГОЛОСОВОЕ", 56, (245, 245, 248), "bold", max_w=SW, align="center")
    draw_text(im, (0, 400), "СООБЩЕНИЕ", 56, (245, 245, 248), "bold", max_w=SW, align="center")
    d = ImageDraw.Draw(im)
    mid = 700
    for i, lv in enumerate(levels):
        x = 40 + i * 13
        hh = 6 + lv * 150
        col = (240, 240, 245) if i / len(levels) < progress else (90, 90, 96)
        d.rounded_rectangle((x, mid - hh, x + 7, mid + hh), 3, fill=col)
    return im
