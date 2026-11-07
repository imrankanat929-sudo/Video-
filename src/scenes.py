"""Scene renderers. Each takes a context S and returns a W x H RGB image."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

from lib import *  # noqa

RED = (235, 40, 45)
YEL = (255, 214, 10)


def ev(S, key, default=None):
    """Local time (relative to scene start) of a named event."""
    t = S.ev.get(key)
    if t is None:
        return default if default is not None else S.d * 0.5
    return t - S.start


def big_text_block(img, lines, cy, size, fill=(255, 255, 255), stroke=8, spacing=1.08, pop=1.0, alpha=1.0, glow=None):
    for i, ln in enumerate(lines):
        if isinstance(ln, tuple):
            txt, col, sz = ln
        else:
            txt, col, sz = ln, fill, size
        spr = text_layer(txt, sz, col + (255,), stroke=stroke, sfill=(0, 0, 0, 255), glow=glow)
        y = cy + (i - (len(lines) - 1) / 2) * size * spacing
        paste(img, spr, W / 2, y, scale=pop, alpha=alpha)


def dark_band(img, y0, y1, a=0.6):
    m = np.zeros((H, 1), np.float32)
    ys = np.arange(H)
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    m[:, 0] = np.clip(1 - np.abs(ys - mid) / half, 0, 1) ** 0.6 * a
    arr = to_arr(img) * (1 - m[:, :, None])
    return to_img(arr)


def countdown_str(sec):
    sec = max(0, sec)
    d = int(sec // 86400)
    h = int(sec % 86400 // 3600)
    m = int(sec % 3600 // 60)
    s = int(sec % 60)
    return f"{d:02d}:{h:02d}:{m:02d}:{s:02d}" if d else f"{h:02d}:{m:02d}:{s:02d}"


# ======================================================================= 1 HOOK
def hook(S):
    p = S.lt / S.d
    bg = starfield(1300, 2310, 1)
    img = cam(bg, 1.0 + 0.1 * p).convert("RGBA")
    e = earth_static(1700, 0.6)
    paste(img, e, W / 2, H + 420 - 60 * p, scale=1.0 + 0.04 * p)
    # asteroid incoming with trail
    q = smooth(min(1, S.lt / (S.d + 0.3)))
    ax, ay = lerp(W * 0.82, W * 0.5, q), lerp(H * 0.36, H * 0.6, q)
    size = lerp(0.3, 0.62, q)
    tr = trail_sprite()
    s2 = size * 1.3
    paste(img, tr, ax + 0.53 * 600 * s2, ay - 0.85 * 600 * s2, scale=s2)
    paste(img, glow_sprite(400, (255, 140, 60), 2.0), ax, ay, scale=size * 2.2, alpha=0.9)
    paste(img, asteroid(700, 3), ax, ay, scale=size, rot=S.t * 20)
    out = img.convert("RGB")
    out = bloom(out, 0.5)
    out = dark_band(out, 120, 900, 0.65)
    L = S.L
    pops = [ease_out((S.lt - 0.1 - i * 0.45) / 0.35) for i in range(3)]
    for i, (txt, col, sz, y) in enumerate([(L["t1"], (255, 255, 255), 96, 360), (L["t2"], (255, 255, 255), 96, 470), (L["t3"], RED, 230, 650)]):
        if pops[i] > 0:
            spr = text_layer(txt, sz, col + (255,), stroke=8, glow=(160, 0, 0) if i == 2 else None)
            paste(out, spr, W / 2, y, scale=0.7 + 0.3 * pops[i] + (0.04 * math.sin(S.t * 6) if i == 2 else 0), alpha=pops[i])
    fade = clamp(S.lt / 0.35)
    if fade < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, fade)
    return out


@lru_cache(None)
def earth_static(D, lon):
    return earth(D, lon)


@lru_cache(None)
def trail_sprite(L_=1200, Wd=240, angle=-58):
    v, u = np.mgrid[0:Wd, 0:L_].astype(np.float32)
    u = u / L_
    v = (v - Wd / 2) / (Wd / 2)
    width = 0.15 + 0.85 * u ** 0.6
    a = np.exp(-(v / width) ** 2 * 3) * (1 - u) ** 1.6
    core = np.exp(-(v / width) ** 2 * 18) * (1 - u) ** 3
    col = np.stack([np.clip(a + core, 0, 1), np.clip(a * 0.55 + core, 0, 1), np.clip(a * 0.2 + core * 0.9, 0, 1)], -1)
    img = to_img(col).convert("RGBA")
    img.putalpha(to_img(np.clip(a * 1.2, 0, 1)).convert("L"))
    return img.rotate(58, Image.BILINEAR, expand=True)


# ======================================================================= 2 PHONE WAKE
@lru_cache(None)
def bedroom(warm=False):
    a = vgrad(W, H, [(0, "#0a1020"), (0.6, "#0d1428"), (1, "#05070d")])
    img = to_img(a)
    d = ImageDraw.Draw(img)
    # window with blinds
    for i in range(12):
        y = 260 + i * 46
        d.rectangle([90, y, 470, y + 30], fill=(40, 58, 92) if not warm else (90, 70, 50))
    # bed / pillow silhouettes
    d.rounded_rectangle([-100, 1250, 1200, 2100], radius=120, fill=(18, 22, 36))
    d.rounded_rectangle([600, 1150, 1100, 1350], radius=80, fill=(26, 30, 46))
    d.ellipse([-200, 1500, 700, 2200], fill=(14, 17, 28))
    # lamp
    d.rectangle([880, 600, 900, 1000], fill=(20, 22, 30))
    d.polygon([(820, 600), (960, 600), (930, 500), (850, 500)], fill=(36, 34, 40))
    return img.filter(ImageFilter.GaussianBlur(14))


def lock_screen(sw, sh, S, alert_k, red_k=0.0):
    sc = to_img(vgrad(sw, sh, [(0, "#1b2a5a"), (0.5, "#3a2a6a"), (1, "#0d1230")])).convert("RGBA")
    d = ImageDraw.Draw(sc)
    text_c(d, S.L["date"], sw / 2, 150, font(34, 600), (230, 230, 240))
    text_c(d, "07:02", sw / 2, 260, font(150, 700), (245, 245, 250))
    if alert_k > 0:
        cy = lerp(-200, 520, ease_out(alert_k))
        box = Image.new("RGBA", (sw - 50, 330), (0, 0, 0, 0))
        bd = ImageDraw.Draw(box)
        col = (int(lerp(40, 190, red_k)), int(lerp(40, 20, red_k)), int(lerp(52, 30, red_k)), 240)
        bd.rounded_rectangle([0, 0, box.width - 1, box.height - 1], radius=36, fill=col)
        warn_icon(bd, 60, 66, 30, bg=(200, 25, 35))
        bd.text((110, 66), S.L["alert"], font=font(34, 800), fill=(255, 255, 255), anchor="lm")
        bd.text((box.width - 30, 66), S.L["now"], font=font(26, 500), fill=(220, 220, 220), anchor="rm")
        lines = wrap(S.L["alert_body"], font(31, 500), box.width - 70)
        for i, ln in enumerate(lines[:5]):
            bd.text((36, 130 + i * 42), ln, font=font(31, 500), fill=(240, 240, 245))
        sc.alpha_composite(box, (25, int(cy - 165)))
    return sc


def phone_frame(S, screen, scale=1.0):
    body, (x0, y0, x1, y1), r = phone_body(screen.width, screen.height)
    body = body.copy()
    m = rounded_mask(screen.size, r)
    body.paste(screen, (x0, y0), m)
    ImageDraw.Draw(body).rounded_rectangle([body.width / 2 - 90, y0 + 22, body.width / 2 + 90, y0 + 70], radius=24, fill=(0, 0, 0, 255))
    return body


def phone_wake(S):
    see = ev(S, "see", S.d * 0.5)
    ak = clamp((S.lt - see) / 0.6)
    rk = clamp((S.lt - see - 1.2) / 0.5) * (0.75 + 0.25 * math.sin(S.lt * 12))
    bg = bedroom().copy().convert("RGBA")
    # blue screen light on scene
    gl = glow_sprite(1400, (90, 120, 255) if rk < 0.3 else (255, 60, 60), 1.8)
    paste(bg, gl, W / 2, 1000, alpha=0.35 + 0.25 * ak)
    sc = lock_screen(600, 1260, S, ak, rk)
    ph = phone_frame(S, sc)
    sway = math.sin(S.lt * 1.3) * 1.5
    paste(bg, ph, W / 2 + sway * 6, 1010 + math.sin(S.lt * 0.9) * 8, scale=0.92, rot=sway)
    z = 1.0 + 0.18 * smooth(S.lt / S.d) + 0.05 * ak
    out = cam(bg.convert("RGB"), z, W / 2, 900 + 120 * ak)
    if 0 < S.lt - see < 0.15:
        out = Image.blend(out, Image.new("RGB", (W, H), (255, 255, 255)), 0.25)
    return bloom(out, 0.35)


# ======================================================================= 3 RADAR
def radar(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#01080c"), (1, "#021418")]))
    d = ImageDraw.Draw(img, "RGBA")
    C = (60, 230, 210)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(20, 80, 80, 90), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(20, 80, 80, 90), width=1)
    sx, sy = 540, 1020
    d.ellipse([sx - 34, sy - 34, sx + 34, sy + 34], fill=(255, 200, 80))
    for rr_ in (170, 300):
        d.ellipse([sx - rr_, sy - rr_ * 0.92, sx + rr_, sy + rr_ * 0.92], outline=(60, 230, 210, 110), width=2)
    er = 420
    d.ellipse([sx - er, sy - er * 0.92, sx + er, sy + er * 0.92], outline=C + (220,), width=3)
    ang = 2.2 + 0.25 * p
    ex, ey = sx + er * math.cos(ang), sy + er * 0.92 * math.sin(ang)
    d.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], fill=(70, 150, 255))
    text_c(d, S.L["earth"], ex - 10, ey + 55, font(30, 700), (120, 180, 255))
    # trajectory
    ax0, ay0 = 1040, 120
    k = ease_out(p * 1.4)
    n = 40
    for i in range(int(n * k)):
        t0, t1 = i / n, (i + 0.6) / n
        x0 = lerp(ax0, ex, t0) + math.sin(t0 * 3) * 60
        y0 = lerp(ay0, ey, t0)
        x1 = lerp(ax0, ex, t1) + math.sin(t1 * 3) * 60
        y1 = lerp(ay0, ey, t1)
        d.line([(x0, y0), (x1, y1)], fill=(255, 80, 70, 255), width=5)
    hx = lerp(ax0, ex, k) + math.sin(k * 3) * 60
    hy = lerp(ay0, ey, k)
    d.ellipse([hx - 14, hy - 14, hx + 14, hy + 14], fill=(255, 120, 90))
    if k > 0.98:
        pr = 40 + 30 * (math.sin(S.lt * 8) * 0.5 + 0.5)
        d.ellipse([ex - pr, ey - pr, ex + pr, ey + pr], outline=(255, 60, 60, 255), width=5)
    # panel
    d.rounded_rectangle([60, 1560, 1020, 1840], radius=20, fill=(0, 30, 30, 200), outline=C + (200,), width=3)
    d.text((100, 1600), S.L["obj"], font=font(40, 800), fill=C)
    prob = min(99.8, 12 + 88 * ease_out(p * 1.2))
    d.text((100, 1670), f"{S.L['prob']}: {prob:.1f}%", font=font(40, 700), fill=(255, 90, 80) if prob > 90 else C)
    d.text((100, 1740), f"{S.L['dia']}: ~10 {S.L['km']}", font=font(40, 700), fill=C)
    d.text((70, 90), "● " + S.L["track"], font=font(36, 800), fill=(255, 70, 70) if int(S.lt * 2) % 2 else C)
    # sweep
    sa = S.lt * 2.2
    for i in range(18):
        a2 = sa - i * 0.03
        d.line([(sx, sy), (sx + 600 * math.cos(a2), sy + 600 * math.sin(a2))], fill=(60, 230, 210, int(70 * (1 - i / 18))), width=6)
    out = bloom(img, 0.9, 16, 0.3)
    out = cam(out, 1.05 + 0.12 * smooth(p), lerp(540, ex, 0.3 * p), lerp(960, ey, 0.3 * p))
    return scanlines(out)


@lru_cache(None)
def _scan():
    a = np.ones((H, 1, 3), np.float32)
    a[::4] = 0.82
    return to_img(np.repeat(a, W, 1))


def scanlines(img):
    return ImageChops.multiply(img, _scan())


# ======================================================================= 4 FAKE
def chat_screen(S, sw, sh, msgs, shown, typing=False):
    sc = Image.new("RGBA", (sw, sh), (14, 16, 22, 255))
    d = ImageDraw.Draw(sc)
    d.rectangle([0, 0, sw, 190], fill=(28, 30, 40))
    d.ellipse([40, 100, 110, 170], fill=(80, 110, 220))
    text_c(d, S.L["chat"][0], 75, 135, font(34, 800), (255, 255, 255))
    d.text((130, 112), S.L["chat"], font=font(36, 800), fill=(255, 255, 255))
    d.text((130, 156), S.L["online"], font=font(24, 500), fill=(140, 200, 140))
    y = 240
    for i, (m, mine) in enumerate(msgs):
        if i >= shown:
            break
        f = font(32, 600)
        lines = wrap(m, f, sw * 0.62)
        bh = 30 + 44 * len(lines)
        bw = max(text_size(l, f)[0] for l in lines) + 50
        x0 = sw - bw - 30 if mine else 30
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=30, fill=(50, 110, 240) if mine else (44, 46, 58))
        for j, l in enumerate(lines):
            d.text((x0 + 25, y + 16 + j * 44), l, font=f, fill=(255, 255, 255))
        y += bh + 22
    if typing:
        for j in range(3):
            a = 120 + 135 * (math.sin(S.lt * 8 - j) * 0.5 + 0.5)
            d.ellipse([60 + j * 34, y + 20, 84 + j * 34, y + 44], fill=(int(a),) * 3)
    return sc


def fake(S):
    msgs = [(m, False) for m in S.L["fake_msgs"]]
    n = len(msgs)
    shown = 1 + int(S.lt / (S.d * 0.62) * n)
    bg = bedroom().copy().convert("RGBA")
    sc = chat_screen(S, 600, 1260, msgs, shown, typing=shown <= n)
    ph = phone_frame(S, sc)
    paste(bg, ph, W / 2, 980, scale=1.0, rot=math.sin(S.lt) * 1.2)
    out = cam(bg.convert("RGB"), 1.08 + 0.1 * S.lt / S.d, W / 2, 900)
    k = (S.lt - S.d * 0.65) / 0.25
    if k > 0:
        st = text_layer(S.L["fake"], 190, RED + (255,), stroke=10, sfill=(255, 255, 255, 255))
        paste(out, st, W / 2, 880, scale=lerp(2.2, 1.0, ease_out(k)), alpha=clamp(k * 2), rot=12)
    return out


# ======================================================================= 5 CONFIRM (news)
@lru_cache(None)
def studio():
    a = vgrad(W, H, [(0, "#06142e"), (0.6, "#0d2550"), (1, "#050a18")])
    img = to_img(a)
    d = ImageDraw.Draw(img, "RGBA")
    for i, r in enumerate(range(200, 1400, 120)):
        d.ellipse([540 - r, 700 - r, 540 + r, 700 + r], outline=(90, 150, 255, 40), width=3)
    for x in range(-200, 1300, 90):
        d.line([(540, 700), (x, 0)], fill=(90, 150, 255, 18), width=2)
    # flags
    for fx, cols in ((150, ((30, 50, 110), (30, 50, 110), (30, 50, 110))), (930, ((30, 50, 110), (30, 50, 110), (30, 50, 110)))):
        d.rectangle([fx - 4, 520, fx + 4, 1300], fill=(140, 140, 150))
        for k, c in enumerate(cols):
            d.polygon([(fx, 540 + k * 80), (fx + (110 if fx < 540 else -110), 560 + k * 80), (fx + (110 if fx < 540 else -110), 640 + k * 80), (fx, 620 + k * 80)], fill=c + (200,))
    # speaker
    person(d, 540, 1450, 780, (10, 14, 26, 255), pose="back")
    # podium
    d.polygon([(330, 1050), (750, 1050), (700, 1500), (380, 1500)], fill=(22, 30, 54, 255))
    d.ellipse([470, 1130, 610, 1270], outline=(200, 180, 120, 255), width=8)
    d.ellipse([500, 1160, 580, 1240], fill=(200, 180, 120, 255))
    for mx in (500, 580):
        d.line([(mx, 1050), (mx + (-20 if mx < 540 else 20), 960)], fill=(30, 30, 30, 255), width=8)
        d.ellipse([mx - 32 + (-20 if mx < 540 else 20), 930, mx + 8 + (-20 if mx < 540 else 20) + 24, 975], fill=(30, 30, 30, 255))
    return img.filter(ImageFilter.GaussianBlur(2))


def news_overlay(img, S, head, k=1.0, live=True):
    d = ImageDraw.Draw(img, "RGBA")
    if live:
        d.rounded_rectangle([50, 90, 360, 160], radius=10, fill=(200, 20, 30, 230))
        if int(S.t * 2) % 2:
            d.ellipse([72, 112, 98, 138], fill=(255, 255, 255))
        d.text((115, 125), S.L["live"], font=font(34, 900), fill=(255, 255, 255), anchor="lm")
    x_off = lerp(-W, 0, ease_out(k))
    y0 = 1460
    d.rectangle([x_off, y0, x_off + 380, y0 + 80], fill=(210, 20, 30, 250))
    d.text((x_off + 30, y0 + 40), S.L["breaking"], font=font(44, 900), fill=(255, 255, 255), anchor="lm")
    lines = wrap(head, font(52, 900), W - 100)
    hh = 30 + 66 * len(lines)
    d.rectangle([x_off, y0 + 80, x_off + W, y0 + 80 + hh], fill=(245, 245, 248, 250))
    for i, l in enumerate(lines):
        d.text((x_off + 40, y0 + 100 + i * 66), l, font=font(52, 900), fill=(15, 20, 40))
    ty = y0 + 80 + hh
    d.rectangle([0, ty, W, ty + 64], fill=(15, 25, 60, 250))
    tick = S.L["ticker"] * 3
    tw = text_size(S.L["ticker"], font(34, 700))[0]
    off = -(S.t * 220) % tw
    d.text((off - tw, ty + 32), tick, font=font(34, 700), fill=(255, 220, 80), anchor="lm")
    return img


def confirm(S):
    base = studio().copy()
    z = 1.0 + 0.12 * smooth(S.lt / S.d)
    out = cam(base, z, 540, 900)
    out = news_overlay(out, S, S.L["confirm"], clamp(S.lt / 0.5))
    return scanlines(bloom(out, 0.3))


# ======================================================================= 6 ASTEROID CLOSE
def asteroid_close(S):
    p = S.lt / S.d
    bg = starfield(1300, 2310, 2)
    img = cam(bg, 1.0 + 0.08 * p, 650 + 50 * p, 1155).convert("RGBA")
    paste(img, glow_sprite(900, (255, 120, 60), 2.5), W * 0.62, H * 0.56, scale=1.6, alpha=0.25)
    a = asteroid(1200, 7, (0.85, -0.3, 0.45))
    paste(img, a, W / 2 + 40 - 60 * p, H * 0.56, scale=0.72 + 0.25 * smooth(p), rot=-S.t * 6)
    out = img.convert("RGB")
    tk = ev(S, "days")
    k = (S.lt - tk + 0.3) / 0.35
    if k > 0:
        out = dark_band(out, 80, 640, 0.7)
        paste(out, text_layer(S.L["days7"], 220, RED + (255,), stroke=10, glow=(150, 0, 0)), W / 2, 270, scale=lerp(1.6, 1.0, ease_out(k)), alpha=clamp(k))
        rem = 7 * 86400 - (S.lt - tk) * 3600 * 4
        paste(out, text_layer(S.L["until"], 46, (255, 255, 255, 255), stroke=4), W / 2, 430, alpha=clamp(k))
        paste(out, text_layer(countdown_str(rem), 96, (255, 255, 255, 255), stroke=5, weight=800), W / 2, 530, alpha=clamp(k))
    return bloom(out, 0.4)


# ======================================================================= DAY CARD
def daycard(S):
    n = S.arg
    p = S.lt / S.d
    bg = starfield(1300, 2310, 9 + n, n=900, tint=("#120203", "#1d0507", "#050101"))
    img = cam(bg, 1.1 - 0.05 * p)
    d = ImageDraw.Draw(img, "RGBA")
    k = ease_out(S.lt / 0.3)
    sc = lerp(1.35, 1.0, k) - 0.03 * p
    paste(img, text_layer(S.L["day"], 120, (255, 255, 255, 255), stroke=6), W / 2, 640, scale=sc)
    paste(img, text_layer(str(n), 560, RED + (255,), stroke=12, glow=(170, 0, 0)), W / 2, 960, scale=sc)
    seg = 110
    x0 = W / 2 - (7 * seg + 6 * 16) / 2
    for i in range(7):
        on = i < n
        c = RED + (255,) if on else (80, 80, 80, 200)
        if i == n - 1 and int(S.lt * 6) % 2:
            c = (255, 255, 255, 255)
        d.rounded_rectangle([x0 + i * (seg + 16), 1300, x0 + i * (seg + 16) + seg, 1330], radius=8, fill=c)
    left = 7 - n
    txt = S.L["left"](left)
    paste(img, text_layer(txt, 54, (230, 230, 230, 255), stroke=3, weight=700), W / 2, 1420, alpha=clamp((S.lt - 0.2) / 0.3))
    g = max(0, 1 - S.lt / 0.25)
    return glitch(bloom(img, 0.5), g, S.t)


# ======================================================================= MISSION CONTROL
@lru_cache(None)
def control_room():
    w = 1500
    img = to_img(vgrad(w, H, [(0, "#03060c"), (0.5, "#07101e"), (1, "#020305")]))
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(4)
    # main wall screen
    d.rectangle([120, 260, 1380, 980], fill=(6, 20, 44), outline=(60, 120, 200), width=4)
    # side screens
    for x in (20, 1390):
        d.rectangle([x, 320, x + 90, 900], fill=(8, 24, 40))
    # desks rows
    for row, (y, n, h) in enumerate(((1180, 7, 120), (1440, 6, 160), (1760, 5, 210))):
        d.polygon([(0, y + h * 0.6), (w, y + h * 0.6), (w, y + h * 1.3), (0, y + h * 1.3)], fill=(10, 12, 18, 255))
        for i in range(n):
            mx = (i + 0.5) * w / n + rng.uniform(-20, 20)
            mw = h * 1.2
            col = rng.choice([(30, 110, 200), (20, 160, 140), (180, 60, 60), (40, 90, 170)])
            d.rectangle([mx - mw / 2, y - h * 0.3, mx + mw / 2, y + h * 0.45], fill=tuple(col) + (255,))
            for k in range(5):
                yy = y - h * 0.2 + k * h * 0.12
                d.line([(mx - mw * 0.4, yy), (mx - mw * 0.4 + rng.uniform(0.2, 0.8) * mw * 0.8, yy)], fill=(255, 255, 255, 120), width=3)
            bust(d, mx + rng.uniform(-30, 30), y + h * 0.75, h * 0.9, (4, 5, 8, 255))
    person(d, 1150, 1180, 520, (4, 5, 8, 255), arm="point")
    return img


def mission(S):
    p = S.lt / S.d
    img = control_room().copy()
    d = ImageDraw.Draw(img, "RGBA")
    # animated main screen: earth & multiple trajectories
    ex, ey = 750, 640
    d.ellipse([ex - 90, ey - 90, ex + 90, ey + 90], fill=(40, 100, 220), outline=(120, 190, 255), width=4)
    for i in range(6):
        k = clamp(p * 1.6 - i * 0.12)
        pts = []
        for j in range(int(40 * k)):
            u = j / 40
            pts.append((lerp(1300, ex, u), lerp(320 + i * 40, ey, u) + math.sin(u * 3.14) * (i - 2.5) * 70))
        if len(pts) > 1:
            d.line(pts, fill=(255, 90, 70, 230) if i == 3 else (80, 200, 255, 160), width=4)
    d.text((160, 290), S.L["traj"], font=font(40, 800), fill=(120, 190, 255))
    d.text((160, 920), f"Δv = {0.4 + 2.1 * p:.2f} m/s", font=font(34, 600), fill=(255, 200, 80))
    out = cam(img, 1.05, lerp(560, 940, smooth(p)), 980 - 60 * p)
    return bloom(out, 0.5)


# ======================================================================= TV WALL
@lru_cache(None)
def tv_thumb():
    t = Image.new("RGB", (300, 200))
    bg = starfield(300, 200, 31, n=80, nebula=False)
    t.paste(bg)
    paste(t, asteroid(260, 5), 170, 95, scale=0.6)
    return t


def tv_wall(S):
    p = S.lt / S.d
    img = Image.new("RGB", (W, H), (8, 8, 12))
    d = ImageDraw.Draw(img, "RGBA")
    th = tv_thumb()
    rows, cols = 6, 3
    tw, thh = 320, 230
    gx, gy = (W - cols * tw) / (cols + 1), 60
    for r in range(rows):
        for c in range(cols):
            x = gx + c * (tw + gx)
            y = 140 + r * (thh + gy)
            d.rectangle([x - 12, y - 12, x + tw + 12, y + thh + 12], fill=(25, 25, 30))
            img.paste(th.resize((tw, thh)), (int(x), int(y)))
            fl = (math.sin(S.t * 13 + r * 3 + c * 7) * 0.5 + 0.5) * 50
            d.rectangle([x, y, x + tw, y + thh], fill=(255, 255, 255, int(fl * 0.4)))
            d.rectangle([x, y + thh - 50, x + tw, y + thh], fill=(200, 20, 30, 240))
            d.text((x + 12, y + thh - 25), S.L["breaking"], font=font(28, 900), fill=(255, 255, 255), anchor="lm")
    out = cam(img, lerp(2.4, 1.05, ease_out(p * 1.2)), lerp(W / 2, W / 2, p), lerp(H * 0.48, H / 2, p))
    return scanlines(bloom(out, 0.4))


# ======================================================================= STORE
@lru_cache(None)
def store_base():
    img = to_img(vgrad(W, H, [(0, "#2a2f33"), (0.45, "#4b5156"), (0.55, "#3a3c3c"), (1, "#1c1c1c")]))
    d = ImageDraw.Draw(img, "RGBA")
    vx, vy = 540, 900
    rng = np.random.default_rng(8)
    # ceiling lights
    for i in range(8):
        z = 1 / (1 + i * 0.6)
        y = vy - 900 * z
        w = 300 * z
        d.rectangle([vx - w, y - 12 * z, vx + w, y + 12 * z], fill=(240, 250, 255, 255))
    # shelves left/right
    for side in (-1, 1):
        xo = 0 if side < 0 else W
        poly = [(xo, 100), (vx + side * 120, vy - 260), (vx + side * 120, vy + 220), (xo, 1800)]
        d.polygon(poly, fill=(70, 74, 80, 255))
        for k in range(6):
            t = k / 5
            yo = lerp(250, 1700, t)
            yi = lerp(vy - 230, vy + 200, t)
            d.line([(xo, yo), (vx + side * 120, yi)], fill=(180, 185, 190, 255), width=10)
            # sparse products
            for j in range(12):
                u = rng.random() ** 0.8
                if rng.random() < 0.18:
                    x = lerp(xo, vx + side * 120, u)
                    y = lerp(yo, yi, u)
                    s = lerp(90, 12, u)
                    col = tuple(int(c) for c in rng.choice([(200, 60, 50), (60, 120, 200), (230, 190, 60), (90, 170, 90)]))
                    d.rectangle([x - s * 0.3, y - s, x + s * 0.3, y], fill=col + (255,))
    # floor reflection
    d.polygon([(0, 1800), (vx - 120, vy + 220), (vx + 120, vy + 220), (W, 1800), (W, H), (0, H)], fill=(40, 42, 44, 255))
    # people with carts
    for (x, h) in ((380, 360), (700, 480), (560, 240)):
        person(d, x, vy + 220 + h * 0.55, h, (10, 10, 12, 255), arm="phone" if h > 300 else None)
        d.rectangle([x + h * 0.15, vy + 220 + h * 0.2, x + h * 0.55, vy + 220 + h * 0.42], outline=(10, 10, 12, 255), width=max(2, int(h * 0.02)))
    # sign
    d.rectangle([600, 1020, 930, 1170], fill=(245, 240, 220, 255))
    return img


def store(S):
    p = S.lt / S.d
    img = store_base().copy()
    d = ImageDraw.Draw(img, "RGBA")
    lines = wrap(S.L["oos"], font(40, 900), 300)
    for i, l in enumerate(lines):
        text_c(d, l, 765, 1095 - (len(lines) - 1) * 24 + i * 48, font(40, 900), (200, 20, 30))
    fl = 1.0 if int(S.lt * 7) % 11 else 0.7
    out = cam(img, 1.0 + 0.35 * smooth(p), 540, 960 + 10 * math.sin(S.lt * 6))
    if fl < 1:
        out = Image.eval(out, lambda v: int(v * fl))
    return bloom(out, 0.35)


# ======================================================================= AIRPORT
def airport(S):
    p = S.lt / S.d
    img = Image.new("RGB", (W, 2400), (16, 18, 24))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([40, 80, W - 40, 1080], fill=(6, 6, 8), outline=(60, 60, 70), width=6)
    d.text((80, 140), S.L["dep"], font=font(60, 900), fill=(255, 200, 40), anchor="lm")
    stat = S.L["stat"]
    rng = np.random.default_rng(3)
    for i, city in enumerate(S.L["cities"]):
        y = 240 + i * 100
        d.rectangle([60, y - 40, W - 60, y + 40], fill=(16, 16, 20))
        d.text((80, y), f"{8 + i // 2:02d}:{(i * 17) % 60:02d}", font=font(40, 700), fill=(255, 210, 60), anchor="lm")
        d.text((260, y), city, font=font(40, 700), fill=(240, 240, 240), anchor="lm")
        s = stat[i % len(stat)]
        col = (255, 60, 60) if i % len(stat) in (0, 3) else (255, 190, 40)
        if i % 3 == 0 and int(S.t * 2.5 + i) % 2:
            col = (90, 20, 20)
        d.text((W - 80, y), s, font=font(36, 900), fill=col, anchor="rm")
    # window with plane
    d.rectangle([0, 1180, W, 1700], fill=(40, 60, 90))
    for x in range(0, W, 180):
        d.rectangle([x, 1180, x + 14, 1700], fill=(12, 14, 20))
    px = lerp(-300, W + 300, (S.lt / 4.5) % 1.2)
    py = lerp(1600, 1250, (S.lt / 4.5) % 1.2)
    pd = ImageDraw.Draw(img)
    pd.polygon([(px - 160, py + 20), (px + 160, py - 30), (px + 180, py - 18), (px - 150, py + 36)], fill=(12, 14, 20))
    pd.polygon([(px - 20, py), (px + 50, py - 8), (px - 60, py + 70)], fill=(12, 14, 20))
    pd.polygon([(px - 130, py + 20), (px - 160, py - 40), (px - 120, py + 14)], fill=(12, 14, 20))
    # crowd
    for i in range(70):
        x = rng.uniform(-40, W + 40)
        h = rng.uniform(380, 700)
        base = 2400 - rng.uniform(0, 260) + h * 0.15
        c = int(rng.uniform(4, 22))
        person(d, x + math.sin(S.t * 2 + i) * 6, base, h, (c, c, c + 4, 255), arm=rng.choice([None, "phone", None]))
    out = cam(img, 1.1, 540, lerp(820, 1500, smooth(p)))
    return bloom(out, 0.35)


# ======================================================================= SIZE
def size_scene(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#060a1c"), (0.6, "#1a2448"), (0.85, "#5a3a4a"), (1, "#20141c")])).convert("RGBA")
    k = smooth(p * 1.3)
    D = lerp(260, 1500, k)
    ast = asteroid(1200, 12, (0.4, 0.7, 0.55))
    paste(img, glow_sprite(800, (255, 150, 90), 2.2), W / 2, lerp(900, 820, k), scale=D / 600, alpha=0.3)
    paste(img, ast, W / 2, lerp(900, 820, k), scale=D / 1200 * 1.15)
    sk = skyline(W + 200, 520, 2, "#07080d", True, "#ffcf7a", 0.18)
    paste(img, sk, W / 2, H - 260)
    out = img.convert("RGB")
    d = ImageDraw.Draw(out)
    km = lerp(1, 10, k)
    paste(out, text_layer(f"{km:.0f} {S.L['km']}", 170, YEL + (255,), stroke=8), W / 2, 330)
    paste(out, text_layer(S.L["dia"], 50, (255, 255, 255, 255), stroke=4), W / 2, 200)
    if k > 0.4:
        old = text_layer(f"{S.L['forecast']}: 1 {S.L['km']}", 48, (200, 200, 200, 255), stroke=3)
        paste(out, old, W / 2, 470, alpha=clamp((k - 0.4) * 4))
        d.line([(W / 2 - old.width / 2 + 40, 470), (W / 2 + old.width / 2 - 40, 470)], fill=RED, width=8)
    return bloom(out, 0.35)


# ======================================================================= EARTH ZONE
def earth_zone(S):
    p = S.lt / S.d
    img = cam(starfield(1300, 2310, 4), 1.0 + 0.05 * p).convert("RGBA")
    E = earth(1000, 1.2 + S.lt * 0.04)
    paste(img, E, W / 2, 900, scale=1.0 + 0.15 * smooth(p))
    out = img.convert("RGB")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ix, iy = 640, 800
    for i in range(3):
        rr = ((S.lt * 140 + i * 120) % 360)
        a = int(255 * (1 - rr / 360))
        d.ellipse([ix - rr, iy - rr * 0.8, ix + rr, iy + rr * 0.8], outline=(255, 50, 40, a), width=6)
    zr = 60 + 260 * smooth(p)
    d.ellipse([ix - zr, iy - zr * 0.8, ix + zr, iy + zr * 0.8], fill=(255, 40, 30, 70))
    d.ellipse([ix - 16, iy - 16, ix + 16, iy + 16], fill=(255, 230, 200, 255))
    d.line([(ix, iy), (ix + 160, iy - 360), (ix + 300, iy - 360)], fill=(255, 255, 255, 230), width=4)
    out.paste(ov, (0, 0), ov)
    lab = text_layer(S.L["zone"], 46, (255, 255, 255, 255), stroke=4)
    paste(out, lab, min(W - lab.width / 2 - 10, ix + 160 + lab.width / 2 - 20), iy - 410)
    return bloom(out, 0.5)


# ======================================================================= SIRENS
def sirens(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#02030a"), (0.55, "#0b1022"), (1, "#050508")])).convert("RGBA")
    paste(img, skyline(W + 300, 900, 6, "#090b14", True, "#c9d4ff", 0.22), W / 2, 850)
    d = ImageDraw.Draw(img)
    # billboard
    d.rectangle([140, 300, 940, 620], fill=(10, 30, 120) if int(S.t * 3) % 2 else (20, 50, 160), outline=(200, 200, 220), width=6)
    lines = wrap(S.L["calm"], font(70, 900), 740)
    for i, l in enumerate(lines):
        text_c(d, l, 540, 460 - (len(lines) - 1) * 40 + i * 80, font(70, 900), (255, 255, 255))
    # street
    d.polygon([(0, 1300), (W, 1300), (W, H), (0, H)], fill=(14, 15, 20))
    d.polygon([(500, 1300), (580, 1300), (720, H), (360, H)], fill=(30, 30, 34))
    # running people
    rng = np.random.default_rng(13)
    for i in range(14):
        h = rng.uniform(300, 760)
        sp = rng.uniform(150, 420) * rng.choice([-1, 1])
        x = (rng.uniform(0, W + 400) + S.lt * sp) % (W + 400) - 200
        base = 1300 + h * 0.75
        person(d, x, base, h, (6, 6, 9, 255), lean=0.6 * np.sign(sp), arm=rng.choice(["out", None, "phone"]))
    out = img.convert("RGB")
    # police lights
    ph = (S.t * 3.0) % 1
    col = (255, 20, 30) if ph < 0.5 else (30, 60, 255)
    cx = 0 if ph < 0.5 else W
    gl = glow_sprite(1800, col, 1.6)
    out = add_glow(out, _place(gl, cx, 1300), 0.55)
    sx, sy, sr = shake(S.t, 6, 9)
    return bloom(cam(out, 1.08 + 0.06 * p, 540 + sx, 960 + sy, sr), 0.4)


def _place(spr, cx, cy):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)
    return layer


# ======================================================================= CALLS
def call_screen(S, sw, sh, name):
    sc = to_img(vgrad(sw, sh, [(0, "#1d3b2c"), (1, "#0a1410")])).convert("RGBA")
    d = ImageDraw.Draw(sc, "RGBA")
    for i in range(3):
        rr = 120 + ((S.lt * 90 + i * 60) % 180)
        a = int(200 * (1 - (rr - 120) / 180))
        d.ellipse([sw / 2 - rr, 480 - rr, sw / 2 + rr, 480 + rr], outline=(255, 255, 255, a), width=4)
    d.ellipse([sw / 2 - 120, 360, sw / 2 + 120, 600], fill=(200, 150, 110))
    text_c(d, name[0], sw / 2, 480, font(120, 800), (255, 255, 255))
    text_c(d, name, sw / 2, 720, font(64, 800), (255, 255, 255))
    text_c(d, S.L["calling"], sw / 2, 800, font(36, 500), (200, 220, 200))
    for x, c in ((sw / 2 - 150, (230, 50, 50)), (sw / 2 + 150, (60, 200, 90))):
        d.ellipse([x - 60, 1050, x + 60, 1170], fill=c)
    return sc


def calls(S):
    sw = ev(S, "friends", S.d * 0.45)
    bg = bedroom(True).copy().convert("RGBA")
    if S.lt < sw:
        sc = call_screen(S, 600, 1260, S.L["mom"])
    else:
        lt = S.lt - sw
        msgs = [(S.L["msg_out"], True), (S.L["msg_in"], False)]
        sc = chat_screen(S, 600, 1260, msgs, 1 + (lt > 2.2), typing=1.0 < lt < 2.2)
        d = ImageDraw.Draw(sc)
        d.rectangle([0, 0, 600, 190], fill=(28, 30, 40))
        d.ellipse([40, 100, 110, 170], fill=(220, 120, 60))
        text_c(d, S.L["friend"][0], 75, 135, font(34, 800), (255, 255, 255))
        d.text((130, 120), S.L["friend"], font=font(38, 800), fill=(255, 255, 255))
    paste(bg, glow_sprite(1300, (255, 170, 90), 1.8), W / 2, 1000, alpha=0.3)
    paste(bg, phone_frame(S, sc), W / 2, 980, rot=math.sin(S.lt * 0.8) * 1.5)
    z = 1.05 + 0.1 * smooth(S.lt / S.d)
    return bloom(cam(bg.convert("RGB"), z, W / 2, 940), 0.3)


# ======================================================================= ROOFTOP
@lru_cache(None)
def sunset_sky():
    a = vgrad(1400, H, [(0, "#1a1240"), (0.35, "#6a2c6a"), (0.6, "#e0603a"), (0.72, "#ffb060"), (1, "#40202a")])
    img = to_img(a).convert("RGBA")
    paste(img, glow_sprite(900, (255, 220, 150), 1.6, core=0.8), 820, 1250)
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(2)
    for i in range(14):
        y = rng.uniform(300, 1150)
        x = rng.uniform(-200, 1400)
        d.rounded_rectangle([x, y, x + rng.uniform(300, 700), y + rng.uniform(14, 36)], radius=15, fill=(255, 150, 120, 60))
    return img


def rooftop(S):
    p = S.lt / S.d
    img = sunset_sky().copy()
    paste(img, skyline(1700, 700, 9, "#3a2038", False), 700 + 40 * p, 1250)
    paste(img, skyline(1700, 650, 10, "#140a14", True, "#ffcf7a", 0.12), 700 + 90 * p, 1420)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1600, 1400, H], fill=(8, 5, 8))
    person(d, 520, 1610, 560, (8, 5, 8), pose="back")
    for i in range(5):
        bx = (200 + i * 70 + S.lt * 90) % 1400
        by = 600 + i * 25 + math.sin(S.lt * 3 + i) * 10
        wv = 14 * math.sin(S.lt * 9 + i)
        d.line([(bx - 20, by - wv), (bx, by), (bx + 20, by - wv)], fill=(20, 10, 20), width=5)
    out = cam(img.convert("RGB"), 1.05 + 0.1 * p, 650 + 100 * p, 1000)
    return bloom(out, 0.35)


# ======================================================================= LAUNCH
@lru_cache(None)
def smoke_sprite(seed):
    n = fnoise(256, 256, seed, 5, 2)
    a = radial(256, 256, 128, 128, 128, 1.4) * (0.4 + 0.6 * n)
    img = Image.new("RGBA", (256, 256), (180, 170, 165, 0))
    img.putalpha(to_img(np.clip(a, 0, 1)).convert("L"))
    return img


def launch(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, 2600, [(0, "#020308"), (0.7, "#0b1428"), (1, "#141018")])).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 2300, W, 2600], fill=(6, 6, 8))
    # tower
    d.rectangle([700, 1500, 760, 2300], fill=(10, 10, 14))
    for y in range(1520, 2300, 60):
        d.line([(700, y), (760, y + 60)], fill=(30, 30, 36), width=6)
    up = ease_in(clamp(p * 1.1)) * 1500
    rx, ry = 540, 1900 - up
    flame = glow_sprite(500, (255, 170, 60), 1.8, core=1.0)
    paste(img, flame, rx, ry + 360, scale=1.2 + 0.08 * math.sin(S.t * 40))
    paste(img, glow_sprite(1600, (255, 140, 60), 2.0), rx, ry + 400, alpha=0.6)
    d.polygon([(rx - 40, ry + 300), (rx - 40, ry - 200), (rx, ry - 330), (rx + 40, ry - 200), (rx + 40, ry + 300)], fill=(225, 225, 230))
    d.polygon([(rx - 40, ry + 300), (rx - 90, ry + 340), (rx - 40, ry + 200)], fill=(40, 40, 50))
    d.polygon([(rx + 40, ry + 300), (rx + 90, ry + 340), (rx + 40, ry + 200)], fill=(40, 40, 50))
    d.rectangle([rx - 40, ry - 120, rx + 40, ry - 90], fill=(30, 30, 40))
    rng = np.random.default_rng(1)
    for i in range(36):
        age = (S.lt * 0.8 + rng.random()) % 1
        sx = 540 + rng.uniform(-1, 1) * (100 + 600 * age)
        sy = 2280 - rng.uniform(0, 1) * 250 * age
        paste(img, smoke_sprite(i % 4), sx, sy, scale=0.8 + 2.5 * age, alpha=0.7 * (1 - age) + 0.2)
    out = img.convert("RGB")
    sx, sy, sr = shake(S.t, 5 + 4 * p, 25)
    out = cam(out, 1.0, 540 + sx, lerp(1700, 1200, smooth(p)) + sy, sr)
    return bloom(out, 0.6, 18, 0.5)


# ======================================================================= WATCH
def watch(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#03040a"), (1, "#0a0c16")])).convert("RGBA")
    paste(img, skyline(W + 300, 1100, 15, "#080a12", True, "#9fb4ff", 0.15), W / 2, 760)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([120, 260, 960, 900], fill=(8, 18, 40), outline=(90, 140, 220), width=8)
    text_c(d, S.L["mission"], 540, 360, font(64, 900), (255, 255, 255))
    text_c(d, S.L["inprog"], 540, 450, font(40, 700), (255, 200, 60))
    for i in range(12):
        a = S.lt * 4 + i * math.pi / 6
        c = int(80 + 175 * (i / 12))
        d.ellipse([540 + 90 * math.cos(a) - 14, 620 + 90 * math.sin(a) - 14, 540 + 90 * math.cos(a) + 14, 620 + 90 * math.sin(a) + 14], fill=(c, c, 255))
    el = 3600 * 3 * p + 1800 + S.lt * 13
    text_c(d, f"{S.L['elapsed']} {countdown_str(el)}", 540, 820, font(42, 700), (180, 200, 255))
    out = img.convert("RGB")
    out = add_glow(out, _place(glow_sprite(1400, (60, 100, 220), 1.6), 540, 600), 0.6)
    d = ImageDraw.Draw(out)
    rng = np.random.default_rng(6)
    for row in range(4):
        for i in range(9):
            x = i * 130 + rng.uniform(-40, 40) + (row % 2) * 60
            h = 260 + row * 120
            bust(d, x, 1250 + row * 160, h, (3 + row, 3 + row, 6 + row))
            if rng.random() < 0.2:
                d.rectangle([x + 40, 1250 + row * 160 - h * 0.9, x + 80, 1250 + row * 160 - h * 0.9 + 70], fill=(180, 200, 255))
    return bloom(cam(out, 1.0 + 0.12 * smooth(p), 540, 900), 0.4)


# ======================================================================= FAILED
def failed(S):
    img = starfield(1300, 2310, 7)
    img = cam(img, 1.05).convert("RGBA")
    tf = ev(S, "mfail", S.d * 0.4)
    hit = tf * 0.6
    k = clamp(S.lt / hit)
    ax, ay = 680, 820
    nud = 30 * ease_out(clamp((S.lt - hit) / 1.5))
    E = earth_static(500, 2.2)
    paste(img, E, 230, 1620)
    out = img.convert("RGB")
    d = ImageDraw.Draw(out, "RGBA")
    # trajectory (dashed) to Earth, even after the nudge
    if S.lt > hit:
        m = clamp((S.lt - hit) / 1.5)
        for i in range(int(30 * m)):
            u0, u1 = i / 30, (i + 0.55) / 30
            d.line([(lerp(ax + nud, 260, u0), lerp(ay, 1560, u0)), (lerp(ax + nud, 260, u1), lerp(ay, 1560, u1))], fill=(255, 70, 60, 230), width=6)
    o2 = out.convert("RGBA")
    paste(o2, asteroid(900, 3), ax + nud, ay, scale=0.75, rot=-S.t * 8)
    if S.lt < hit:
        sx, sy = lerp(-50, ax - 200, k), lerp(1100, ay + 120, k)
        paste(o2, trail_sprite(), sx - 0.53 * 150, sy + 0.85 * 150, scale=0.25, rot=180)
        paste(o2, glow_sprite(200, (200, 230, 255), 1.6, core=1), sx, sy, scale=0.6)
    out = o2.convert("RGB")
    fl = 1 - clamp((S.lt - hit) / 0.6)
    if 0 < fl < 1:
        out = add_glow(out, _place(glow_sprite(1200, (255, 240, 220), 1.4, core=1), ax - 180, ay + 120), fl)
    kk = (S.lt - tf) / 0.3
    if kk > 0:
        out = dark_band(out, 140, 560, 0.7)
        paste(out, text_layer(S.L["failed1"], 150, RED + (255,), stroke=9, glow=(140, 0, 0)), W / 2, 270, scale=lerp(1.5, 1, ease_out(kk)), alpha=clamp(kk))
        paste(out, text_layer(S.L["failed2"], 150, RED + (255,), stroke=9, glow=(140, 0, 0)), W / 2, 420, scale=lerp(1.5, 1, ease_out(kk - 0.3)), alpha=clamp(kk - 0.3))
        out = glitch(out, max(0, 0.6 - kk), S.t)
    sx, sy, sr = shake(S.t, 14 * fl, 30)
    return bloom(cam(out, 1.02 + 0.06 * S.lt / S.d, 540 + sx, 960 + sy, sr), 0.45)


# ======================================================================= QUIET STREET
@lru_cache(None)
def quiet_base():
    img = to_img(vgrad(W, H, [(0, "#3b4a63"), (0.45, "#8a96a8"), (0.52, "#a6a6a8"), (1, "#2a2c30")])).convert("RGBA")
    paste(img, skyline(W + 200, 600, 21, "#4a5466", False), W / 2, 700)
    d = ImageDraw.Draw(img)
    vx, vy = 540, 980
    d.polygon([(0, 1150), (vx - 60, vy), (vx + 60, vy), (W, 1150), (W, H), (0, H)], fill=(52, 55, 62))
    d.polygon([(vx - 30, vy), (vx + 30, vy), (W - 200, H), (200, H)], fill=(38, 40, 46))
    for i in range(10):
        u = (i / 10) ** 1.8
        y0 = lerp(vy, H + 200, u)
        y1 = lerp(vy, H + 200, u + 0.02)
        d.polygon([(lerp(vx, 540, u) - lerp(2, 30, u), y0), (lerp(vx, 540, u) + lerp(2, 30, u), y0), (lerp(vx, 540, u) + lerp(2, 30, u + 0.02), y1), (lerp(vx, 540, u) - lerp(2, 30, u + 0.02), y1)], fill=(210, 200, 150))
    for side in (-1, 1):
        for i in range(6):
            z = 1 / (1 + i * 0.7)
            x = vx + side * 520 * z
            y = vy + 700 * z
            d.rectangle([x - 5 * z, y - 900 * z, x + 5 * z, y], fill=(20, 22, 26))
            d.line([(x, y - 900 * z), (x - side * 80 * z, y - 900 * z)], fill=(20, 22, 26), width=max(2, int(8 * z)))
    return img


def quiet(S):
    p = S.lt / S.d
    img = quiet_base().copy()
    d = ImageDraw.Draw(img)
    if int(S.lt * 1.5) % 2:
        d.ellipse([820, 1020, 850, 1050], fill=(255, 190, 40))
    d.rectangle([826, 1050, 844, 1300], fill=(20, 22, 26))
    out = cam(img.convert("RGB"), 1.05 + 0.15 * p, 540, 1000)
    out = dark_band(out, 200, 700, 0.55)
    paste(out, text_layer(S.L["until"], 52, (255, 255, 255, 255), stroke=4), W / 2, 330)
    rem = 6 * 3600 - S.lt * 61
    paste(out, text_layer(countdown_str(rem), 150, RED + (255,), stroke=8, weight=800), W / 2, 470)
    return out


# ======================================================================= FAMILY
def family(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#24140c"), (1, "#0e0806")])).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([140, 300, 940, 1350], fill=(20, 30, 60))
    win = to_img(vgrad(780, 1030, [(0, "#0a1030"), (0.7, "#24305a"), (1, "#3a3050")])).convert("RGBA")
    paste(win, skyline(900, 300, 4, "#0a0c18", True, "#ffcf7a", 0.2), 390, 900)
    img.paste(win, (150, 310))
    paste(img, glow_sprite(60, (255, 255, 255), 1.2, core=1), 760, 520, alpha=0.6 + 0.3 * math.sin(S.lt * 2))
    d.rectangle([530, 300, 550, 1350], fill=(30, 18, 12))
    d.rectangle([140, 820, 940, 840], fill=(30, 18, 12))
    paste(img, glow_sprite(1200, (255, 150, 70), 1.6), 980, 1300, alpha=0.6)
    col = (12, 7, 5, 255)
    person(d, 400, 1900, 1050, col)
    person(d, 640, 1900, 980, col, lean=-0.3)
    person(d, 520, 1900, 760, col, lean=0.2)
    d.line([(470, 1210), (650, 1180)], fill=col, width=50)
    d.line([(560, 1260), (420, 1240)], fill=col, width=46)
    return bloom(cam(img.convert("RGB"), 1.02 + 0.12 * smooth(p), 540, 1000), 0.4)


# ======================================================================= BRIGHT DOT
def bright(S):
    p = S.lt / S.d
    img = starfield(1300, 2600, 17, tint=("#02030a", "#0a1430", "#121a30"))
    img = img.copy().convert("RGBA")
    k = smooth(p)
    dx, dy = 820, 500
    paste(img, glow_sprite(1200, (255, 170, 110), 1.8), dx, dy, scale=0.3 + 0.9 * k, alpha=0.5)
    paste(img, glow_sprite(160, (255, 255, 255), 1.4, core=1), dx, dy, scale=0.6 + 1.2 * k + 0.1 * math.sin(S.t * 9))
    fl = flare_sprite()
    paste(img, fl, dx, dy, scale=0.4 + 0.8 * k, alpha=0.8)
    paste(img, skyline(1500, 900, 30, "#04050a", True, "#ffcf7a", 0.14), 650, 2200)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 2420, 1300, 2600], fill=(4, 5, 10))
    for x, h, a in ((260, 460, "point"), (420, 400, None), (980, 430, "point"), (1100, 300, None)):
        person(d, x, 2430, h, (4, 5, 10), arm=a)
    out = cam(img.convert("RGB"), 1.0 + 0.2 * k, lerp(650, 720, k), lerp(1700, 1150, k))
    return bloom(out, 0.5, 20, 0.5)


@lru_cache(None)
def flare_sprite(s=900):
    y, x = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2
    a = np.exp(-np.abs(y) / 3) * np.exp(-np.abs(x) / (s * 0.18)) + np.exp(-np.abs(x) / 3) * np.exp(-np.abs(y) / (s * 0.18))
    img = Image.new("RGBA", (s, s), (255, 240, 220, 0))
    img.putalpha(to_img(np.clip(a, 0, 1)).convert("L"))
    return img


# ======================================================================= ENTRY
def entry(S):
    p = S.lt / S.d
    k = smooth(p)
    img = to_img(vgrad(W, H, [(0, "#0a0410"), (0.5, "#5a1a18"), (0.8, "#e06030"), (1, "#301010")])).convert("RGBA")
    hx, hy = lerp(W * 0.85, W * 0.45, k), lerp(H * 0.12, H * 0.5, k)
    paste(img, trail_sprite(), hx + 0.53 * 600 * 1.5, hy - 0.85 * 600 * 1.5, scale=1.5, alpha=1)
    paste(img, glow_sprite(1400, (255, 160, 80), 1.6), hx, hy, scale=0.7 + 0.8 * k)
    paste(img, glow_sprite(300, (255, 255, 240), 1.2, core=1), hx, hy, scale=0.8 + 0.6 * k)
    paste(img, skyline(W + 300, 700, 41, "#060304", True, "#ff9a5a", 0.1), W / 2, H - 340)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 60, W, H], fill=(6, 3, 4))
    for x, h in ((300, 380), (720, 420)):
        person(d, x, H - 60, h, (6, 3, 4), arm="up" if x < 500 else None)
    out = img.convert("RGB")
    out = Image.blend(out, Image.new("RGB", (W, H), (255, 230, 200)), 0.5 * ease_in(p))
    sx, sy, sr = shake(S.t, 4 + 14 * k, 22)
    return bloom(cam(out, 1.05 + 0.08 * k, 540 + sx, 960 + sy, sr), 0.7, 20, 0.45)


# ======================================================================= FLASH
def flash(S):
    lt = S.lt
    white = Image.new("RGB", (W, H), (255, 252, 245))
    if lt < 1.4:
        return white
    k = clamp((lt - 1.4) / max(0.6, S.d - 1.4))
    base = destruction_frame(S, 0.0, shake_amp=0)
    return Image.blend(white, base, ease_out(k) * 0.85)


# ======================================================================= DESTRUCTION
@lru_cache(None)
def plume_sprite():
    s = 1000
    n = fnoise(s, s, 77, 7, 4)
    n2 = fnoise(s, s, 78, 6, 8)
    y, x = np.mgrid[0:s, 0:s].astype(np.float32)
    cx = s / 2
    dx = (x - cx) / s
    # mushroom cap made of turbulent blob + stem that widens to the ground
    cap = 1 - np.sqrt((dx / 0.40) ** 2 + ((y / s - 0.30) / 0.20) ** 2)
    ring = 1 - np.sqrt((dx / 0.46) ** 2 + ((y / s - 0.40) / 0.08) ** 2)
    stem_w = 0.07 + 0.25 * np.clip((y / s - 0.45) / 0.55, 0, 1) ** 2.2
    stem = (1 - np.abs(dx) / stem_w) * (y / s > 0.38)
    shape = np.maximum(np.maximum(cap, ring * 0.8), stem)
    a = np.clip(shape * 3.0 + (n - 0.5) * 1.6 + (n2 - 0.5) * 0.6, 0, 1)
    # fire glow: strongest in lower cap & stem core, smoke darker at top/edges
    heat = np.clip(stem * 2.5 - 0.2, 0, 1) * (0.6 + 0.5 * n2) + np.clip((y / s - 0.85) / 0.15, 0, 1) * 0.6
    heat = np.clip(heat, 0, 1)
    smoke = np.stack([0.12 + 0.30 * n, 0.09 + 0.2 * n, 0.08 + 0.14 * n], -1)
    under = np.clip((y / s - 0.3) / 0.15, 0, 1) * np.clip(cap * 3, 0, 1) * (y / s < 0.5)
    smoke = smoke + under[:, :, None] * np.array([0.5, 0.18, 0.04])
    fire = np.stack([1.0 + 0 * n, 0.55 + 0.3 * n2, 0.18 + 0.1 * n2], -1)
    col = smoke * (1 - heat[:, :, None]) + fire * heat[:, :, None]
    img = to_img(np.clip(col, 0, 1)).convert("RGBA")
    img.putalpha(to_img(a).convert("L"))
    return img


def destruction_frame(S, k, shake_amp=0.0):
    img = to_img(vgrad(W, H, [(0, "#0a0304"), (0.4, "#3a0e0a"), (0.6, "#c0501e"), (0.66, "#ff9a40"), (0.72, "#4a140c"), (1, "#100406")])).convert("RGBA")
    paste(img, glow_sprite(1600, (255, 150, 60), 1.8), W / 2, 1250, scale=1.0, alpha=0.8)
    paste(img, plume_sprite(), W / 2, lerp(1250, 820, k), scale=lerp(0.45, 1.35, k))
    d = ImageDraw.Draw(img, "RGBA")
    rr = lerp(80, 1400, k)
    d.ellipse([W / 2 - rr, 1220 - rr * 0.12, W / 2 + rr, 1220 + rr * 0.12], outline=(255, 230, 180, int(255 * (1 - k))), width=int(10 + 20 * (1 - k)))
    paste(img, skyline(W + 300, 700, 50, "#080304", False), W / 2, 1460)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 1800, W, H], fill=(8, 3, 4))
    rng = np.random.default_rng(9)
    for i in range(60):
        a0 = rng.uniform(0, 1)
        sp = rng.uniform(300, 1200)
        ang = rng.uniform(-2.8, -0.3)
        t = (k * 6 + a0) % 1.5
        x = W / 2 + math.cos(ang) * sp * t
        y = 1200 + math.sin(ang) * sp * t + 400 * t * t
        s = rng.uniform(2, 7)
        d.polygon([(x - s, y), (x, y - s * 1.4), (x + s * 1.2, y + s * 0.3), (x, y + s)], fill=(25, 10, 6, 230))
    out = img.convert("RGB")
    out = Image.blend(out, Image.new("RGB", (W, H), (90, 60, 45)), 0.35 * k)
    sx, sy, sr = shake(S.t, shake_amp, 26)
    return cam(out, 1.06, 540 + sx, 960 + sy, sr)


def destruction(S):
    k = S.lt / S.d
    out = destruction_frame(S, 0.15 + 0.85 * k, shake_amp=30 * (1 - k * 0.7))
    return bloom(out, 0.6, 20, 0.45)


# ======================================================================= EARTH DUST
def earth_dust(S):
    p = S.lt / S.d
    img = cam(starfield(1300, 2310, 4), 1.02).convert("RGBA")
    E = earth(980, 1.5 + S.lt * 0.03, dust=0.25 + 0.5 * p)
    paste(img, E, W / 2, 960)
    out = img.convert("RGB")
    labels = [("sz", S.L["size"], 190), ("site", S.L["site"], 300), ("aft", S.L["aft"], 410)]
    for key, txt, y in labels:
        tk = ev(S, key, 99)
        k = (S.lt - tk) / 0.3
        if k > 0:
            spr = text_layer("•  " + txt, 64, (255, 255, 255, 255), stroke=5)
            paste(out, spr, lerp(W / 2 - 200, W / 2, ease_out(k)), y + 0 * 0, alpha=clamp(k))
    return bloom(out, 0.45)


# ======================================================================= REBUILD
def rebuild(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#3a3430"), (0.5, "#8a7a68"), (0.62, "#b09a7a"), (1, "#2a241e")])).convert("RGBA")
    paste(img, glow_sprite(700, (255, 220, 170), 1.6, core=0.6), 700, lerp(1200, 900, p), alpha=0.7)
    paste(img, skyline(W + 300, 700, 60, "#3a322c", False, broken=True), W / 2, 1100)
    paste(img, skyline(W + 300, 600, 61, "#1a1612", False, broken=True), W / 2 - 40, 1250)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1540, W, H], fill=(26, 22, 18))
    gk = smooth(p)
    sx, sy = 540, 1640
    sh = 220 * gk
    d.line([(sx, sy), (sx + 6, sy - sh)], fill=(90, 170, 70), width=10)
    if gk > 0.3:
        ls = 90 * (gk - 0.3) / 0.7
        d.ellipse([sx - ls * 1.6, sy - sh * 0.75 - ls * 0.4, sx, sy - sh * 0.75 + ls * 0.4], fill=(110, 200, 80))
        d.ellipse([sx + 6, sy - sh - ls * 0.45, sx + 6 + ls * 1.8, sy - sh + ls * 0.45], fill=(110, 200, 80))
    out = img.convert("RGB")
    out = add_glow(out, _place(glow_sprite(400, (140, 255, 120), 1.6), sx, sy - sh * 0.8), 0.25 * gk)
    out = bloom(cam(out, 1.05 + 0.15 * p, 540, lerp(1100, 1300, p)), 0.35)
    yr = int(lerp(2027, 2040, p))
    paste(out, text_layer(str(yr), 160, (255, 255, 255, 255), stroke=7), W / 2, 330)
    return out


# ======================================================================= QUESTION
def q_mark(S):
    p = S.lt / S.d
    img = starfield(1300, 2310, 33, n=1200, tint=("#020204", "#08080e", "#020204"))
    out = cam(img, 1.0 + 0.1 * p)
    paste(out, text_layer("?", 900, (255, 255, 255, 255), stroke=0, glow=(80, 120, 255)), W / 2, 860, scale=0.9 + 0.12 * smooth(p), alpha=clamp(S.lt / 0.4))
    return bloom(out, 0.5)


def unite(S):
    p = S.lt / S.d
    img = to_img(vgrad(1500, H, [(0, "#1c2a50"), (0.45, "#e08a50"), (0.6, "#ffd090"), (0.62, "#3a2a20"), (1, "#140c08")])).convert("RGBA")
    paste(img, glow_sprite(1000, (255, 230, 170), 1.6, core=0.6), 750, 1160)
    d = ImageDraw.Draw(img)
    d.ellipse([-600, 1180, 2100, 2600], fill=(20, 12, 8))
    rng = np.random.default_rng(7)
    xs = np.arange(-40, 1560, 92)
    pts = []
    for i, x in enumerate(xs):
        h = rng.uniform(300, 380)
        base = 1200 + 40 * ((x - 750) / 750) ** 2 + 10
        person(d, x, base, h, (20, 12, 8))
        pts.append((x, base - h * 0.62))
    for a, b in zip(pts[:-1], pts[1:]):
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 24)
        d.line([(a[0] + 20, a[1] - 40), mid, (b[0] - 20, b[1] - 40)], fill=(20, 12, 8), width=16)
    out = cam(img.convert("RGB"), 1.25 - 0.15 * p, lerp(600, 900, p), 1150)
    paste(out, text_layer(S.L["together"], 130, (255, 255, 255, 255), stroke=7), W / 2, 420, alpha=clamp(S.lt / 0.5))
    return bloom(out, 0.45)


def divide(S):
    p = S.lt / S.d
    k = smooth(p)
    img = to_img(vgrad(W, H, [(0, "#05080f"), (0.55, "#1a2a44"), (1, "#060a12")])).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1300, W, H], fill=(10, 14, 22))
    pts = [(540, 1300)]
    rng = np.random.default_rng(3)
    for i in range(1, 12):
        pts.append((540 + rng.uniform(-40, 40), 1300 + i * 60))
    wdt = 6 + 90 * k
    left = [(x - wdt / 2, y) for x, y in pts]
    right = [(x + wdt / 2, y) for x, y in pts][::-1]
    d.polygon(left + right, fill=(0, 0, 0))
    col = (8, 10, 16)
    for i, x in enumerate((140, 260, 380)):
        person(d, x - 160 * k, 1340 + i * 20, 520, col)
    for i, x in enumerate((700, 820, 940)):
        person(d, x + 160 * k, 1340 + i * 20, 520, col)
    out = img.convert("RGB")
    out = add_glow(out, _place(glow_sprite(500, (255, 60, 40), 1.6), 540, 1700), 0.4 * k)
    sx, sy, sr = shake(S.t, 6 * k, 20)
    out = cam(out, 1.05, 540 + sx, 1000 + sy, sr)
    paste(out, text_layer(S.L["apart"], 120, (255, 255, 255, 255), stroke=7), W / 2, 420, alpha=clamp(S.lt / 0.5))
    return bloom(out, 0.3)


# ======================================================================= TWIST
def twist(S):
    th = ev(S, "hours", S.d * 0.7)
    img = Image.new("RGB", (W, H), (6, 4, 6))
    pulse = 0.0
    if S.lt > th - 0.2:
        pulse = 0.5 + 0.5 * math.sin((S.lt - th) * 7)
        img = Image.blend(img, to_img(vgrad(W, H, [(0, "#300000"), (0.5, "#600608"), (1, "#300000")])), 0.5 + 0.4 * pulse)
    out = img
    if S.lt < th - 0.25:
        paste(out, text_layer(S.L["days7"], 220, (255, 255, 255, 255), stroke=8), W / 2, 860, scale=1.0 + 0.03 * S.lt)
        paste(out, text_layer(S.L["until"], 52, (200, 200, 200, 255), stroke=3), W / 2, 1040)
    else:
        k = ease_out((S.lt - th + 0.25) / 0.3)
        paste(out, text_layer(S.L["hours7"], 220, RED + (255,), stroke=8, sfill=(255, 255, 255, 255), glow=(200, 0, 0)), W / 2, 860, scale=lerp(1.6, 1.0, k))
        rem = 7 * 3600 - (S.lt - th) * 1
        paste(out, text_layer(countdown_str(rem), 130, (255, 255, 255, 255), stroke=6, weight=800), W / 2, 1060, alpha=clamp(k))
    g = 0.0
    if abs(S.lt - (th - 0.25)) < 0.35:
        g = 1 - abs(S.lt - (th - 0.25)) / 0.35
    out = glitch(out, g, S.t)
    sx, sy, sr = shake(S.t, 10 * g + 3 * pulse, 30)
    return bloom(cam(out, 1.03, 540 + sx, 960 + sy, sr), 0.5)


# ======================================================================= FINAL
def final(S):
    p = S.lt / S.d
    img = to_img(vgrad(W, H, [(0, "#0c0306"), (0.5, "#5a1610"), (0.75, "#c04a20"), (1, "#200808")])).convert("RGBA")
    paste(img, glow_sprite(1400, (255, 140, 60), 1.8), 600, 820, alpha=0.8)
    paste(img, asteroid(1200, 3, (0.2, 0.8, 0.55)), 600, 820 - 20 * p, scale=0.62 + 0.06 * p, rot=-S.t * 4)
    paste(img, skyline(W + 200, 600, 70, "#0a0304", True, "#ff8a4a", 0.1), W / 2, 1620)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1900, W, H], fill=(4, 1, 2))
    bust(d, 540, 1560, 640, (4, 1, 2))
    out = cam(img.convert("RGB"), 1.02 + 0.05 * p, 540, 960)
    out = dark_band(out, 120, 560, 0.6)
    k = ease_out(S.lt / 0.4)
    paste(out, text_layer(S.L["fin1"], 84, (255, 255, 255, 255), stroke=6), W / 2, 260, scale=lerp(1.3, 1, k), alpha=clamp(k))
    paste(out, text_layer(S.L["fin2"], 110, YEL + (255,), stroke=7), W / 2, 380, scale=lerp(1.3, 1, k), alpha=clamp(k))
    kc = clamp((S.lt - 1.2) / 0.4)
    if kc > 0:
        bob = 8 * math.sin(S.lt * 5)
        spr = text_layer(S.L["cta"] + "  ↓", 54, (255, 255, 255, 255), stroke=4, weight=800)
        paste(out, spr, W / 2, 1180 + bob, alpha=kc)
    fade = clamp((S.d - S.lt) / 0.8)
    if fade < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, fade)
    return bloom(out, 0.45)


SCENES = dict(hook=hook, phone_wake=phone_wake, radar=radar, fake=fake, confirm=confirm,
              asteroid_close=asteroid_close, day=daycard, mission=mission, tv_wall=tv_wall,
              store=store, airport=airport, size=size_scene, earth_zone=earth_zone, sirens=sirens,
              calls=calls, rooftop=rooftop, launch=launch, watch=watch, failed=failed, quiet=quiet,
              family=family, bright=bright, entry=entry, flash=flash, destruction=destruction,
              earth_dust=earth_dust, rebuild=rebuild, q_mark=q_mark, unite=unite, divide=divide,
              twist=twist, final=final)
