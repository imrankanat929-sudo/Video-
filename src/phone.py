"""Phone body + screen UIs (all drawn in screen-local coords)."""
import math
import random
import cairo
from core import *
from person import draw_head, BOY, expr, expr_blend, R as HEAD_R

SW, SH = 700, 1480
UI_BG = hexc('#0e1015')
BUBBLE_IN = hexc('#2a2d35')
BUBBLE_OUT = hexc('#2f6fe0')
TXT = hexc('#eef0f4')
SUB = hexc('#8a90a0')


def phone_body(ctx, cx, cy, scale, screen_fn, lit=1.0, rot=0.0, hand=True, skin=None):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(scale, scale)
    bw, bh = SW + 44, SH + 48
    # shadow
    rrect(ctx, -bw / 2 + 10, -bh / 2 + 24, bw, bh, 92)
    setc(ctx, (0, 0, 0), 0.45); ctx.fill()
    rrect(ctx, -bw / 2, -bh / 2, bw, bh, 92)
    setc(ctx, hexc('#1a1b20')); ctx.fill()
    rrect(ctx, -bw / 2 + 4, -bh / 2 + 4, bw - 8, bh - 8, 88)
    setc(ctx, hexc('#08080a')); ctx.fill()
    # side buttons
    ctx.rectangle(bw / 2 - 2, -380, 8, 120); setc(ctx, hexc('#1a1b20')); ctx.fill()
    ctx.save()
    ctx.translate(-SW / 2, -SH / 2)
    rrect(ctx, 0, 0, SW, SH, 70)
    ctx.clip()
    setc(ctx, (0, 0, 0)); ctx.paint()
    if lit > 0.001:
        ctx.push_group()
        screen_fn(ctx)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(clamp(lit))
    # glare
    g = cairo.LinearGradient(0, 0, SW, SH)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.06)
    g.add_color_stop_rgba(0.45, 1, 1, 1, 0.0)
    g.add_color_stop_rgba(1, 1, 1, 1, 0.03)
    ctx.set_source(g); ctx.paint()
    ctx.restore()
    # dynamic island
    rrect(ctx, -70, -SH / 2 + 22, 140, 40, 20)
    setc(ctx, (0, 0, 0)); ctx.fill()
    if hand:
        sk = skin or BOY['skin']
        # fingers on right edge
        for i, yy in enumerate((180, 300, 420)):
            rrect(ctx, bw / 2 - 30, yy, 90, 96, 46)
            setc(ctx, shade(sk, 0.92 - 0.04 * i)); ctx.fill()
        # palm + thumb on left / bottom
        ctx.move_to(-bw / 2 - 120, bh / 2 + 200)
        ctx.curve_to(-bw / 2 - 60, 420, -bw / 2 + 10, 320, -bw / 2 + 60, 360)
        ctx.curve_to(-bw / 2 + 120, 400, -bw / 2 + 60, 520, -bw / 2 + 20, 560)
        ctx.curve_to(0, 700, 200, bh / 2 + 60, 240, bh / 2 + 200)
        ctx.close_path()
        setc(ctx, sk); ctx.fill()
        ctx.move_to(bw / 2 + 60, 140)
        ctx.curve_to(bw / 2 + 130, 300, bw / 2 + 140, 700, bw / 2 + 60, bh / 2 + 200)
        ctx.line_to(bw / 2 - 10, bh / 2 + 200)
        ctx.curve_to(bw / 2 + 20, 600, bw / 2 + 40, 400, bw / 2 + 20, 140)
        ctx.close_path()
        setc(ctx, shade(sk, 0.85)); ctx.fill()
        # sleeve
        ctx.move_to(-bw / 2 - 260, bh / 2 + 400)
        ctx.line_to(-bw / 2 - 160, bh / 2 + 120)
        ctx.line_to(320, bh / 2 + 120)
        ctx.line_to(400, bh / 2 + 400)
        ctx.close_path()
        setc(ctx, hexc('#26282e')); ctx.fill()
    ctx.restore()


def status_bar(ctx, clock="7:42", c=TXT):
    text(ctx, clock, 90, 62, 30, c, weight="bold")
    # battery & signal
    rrect(ctx, SW - 110, 40, 48, 24, 6); ctx.set_line_width(2.5); setc(ctx, c, 0.9); ctx.stroke()
    ctx.rectangle(SW - 106, 44, 30, 16); setc(ctx, c, 0.9); ctx.fill()
    for i in range(4):
        ctx.rectangle(SW - 175 + i * 11, 64 - (i + 1) * 6, 7, (i + 1) * 6)
        setc(ctx, c, 0.9); ctx.fill()


def wallpaper(ctx, tint=hexc('#1b2440')):
    vgrad(ctx, 0, 0, SW, SH, [(0, shade(tint, 1.15), 1), (0.6, tint, 1), (1, hexc('#0a0c14'), 1)])
    glow(ctx, SW * 0.7, SH * 0.25, 420, hexc('#3a4f8a'), 0.35)


def notif_card(ctx, y, sender, msg, alpha=1.0, scale=1.0, icon=hexc('#38c172')):
    ctx.save()
    ctx.translate(SW / 2, y + 70)
    ctx.scale(scale, scale)
    ctx.translate(-SW / 2, -70)
    rrect(ctx, 26, 0, SW - 52, 140, 34)
    setc(ctx, hexc('#2a2e3a'), 0.88 * alpha); ctx.fill()
    rrect(ctx, 50, 26, 56, 56, 14)
    setc(ctx, icon, alpha); ctx.fill()
    # bubble icon
    ellipse(ctx, 78, 52, 16, 13); setc(ctx, (1, 1, 1), alpha); ctx.fill()
    text(ctx, sender, 128, 56, 28, TXT, alpha, align="left")
    text(ctx, "сейчас", SW - 60, 56, 24, SUB, alpha, weight="normal", align="right")
    text(ctx, msg, 128, 102, 30, hexc('#d4d8e2'), alpha, weight="normal", align="left")
    ctx.restore()


def lock_notifs(ctx, t, items, count_start=0, count_rate=40, t0=0.0):
    """items: list of (appear_time, sender, msg)"""
    wallpaper(ctx)
    status_bar(ctx)
    text(ctx, "Вторник, 14 ноября", SW / 2, 210, 30, TXT, 0.85, weight="normal")
    text(ctx, "7:42", SW / 2, 360, 150, TXT, 0.95, weight="black")
    shown = [it for it in items if t >= it[0]]
    n = len(shown)
    y0 = 470
    for i, (ta, s, m) in enumerate(reversed(shown)):
        k = back_out(prog(t, ta, ta + 0.35))
        slot = i
        y = y0 + slot * 158 - (1 - k) * 60 * (i == 0)
        if y > SH - 120:
            continue
        notif_card(ctx, y, s, m, alpha=clamp(k * 1.3) * (1 - 0.12 * i), scale=lerp(0.9, 1.0, k))
    cnt = int(count_start + max(0.0, t - t0) * count_rate)
    if cnt > 0:
        rrect(ctx, SW / 2 - 210, SH - 150, 420, 64, 32)
        setc(ctx, hexc('#2a2e3a'), 0.9); ctx.fill()
        text(ctx, f"Новых сообщений: {min(cnt, 999)}", SW / 2, SH - 107, 28, TXT)


def avatar(ctx, cx, cy, r, c, letter="?", alpha=1.0):
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    setc(ctx, c, alpha); ctx.fill()
    text(ctx, letter, cx, cy + r * 0.36, r, (1, 1, 1), alpha)


def chat_header(ctx, name, sub="", avatar_c=hexc('#555b6b'), letter="?"):
    ctx.rectangle(0, 0, SW, 210)
    setc(ctx, hexc('#161922')); ctx.fill()
    status_bar(ctx)
    text(ctx, "‹", 50, 165, 70, hexc('#4c8dff'), weight="normal", family="DejaVu Sans")
    avatar(ctx, 140, 150, 38, avatar_c, letter)
    text(ctx, name, 196, 145, 32, TXT, align="left")
    if sub:
        text(ctx, sub, 196, 182, 24, SUB, weight="normal", align="left")


def bubble(ctx, y, msg, side, alpha=1.0, k=1.0, size=34, maxw=470, color=None, typing_t=None):
    """returns height"""
    lines = wrap(ctx, msg, size, maxw, "normal") if typing_t is None else [""]
    lh = size * 1.3
    tw = max(text_width(ctx, l, size, "normal") for l in lines) if typing_t is None else 90
    bw = tw + 56
    bh = lh * len(lines) + 34
    x = 30 if side == 'in' else SW - 30 - bw
    ctx.save()
    ox = x if side == 'in' else x + bw
    ctx.translate(ox, y + bh)
    ctx.scale(k, k)
    ctx.translate(-ox, -(y + bh))
    rrect(ctx, x, y, bw, bh, 34)
    setc(ctx, color or (BUBBLE_IN if side == 'in' else BUBBLE_OUT), alpha); ctx.fill()
    if typing_t is not None:
        for i in range(3):
            a = 0.35 + 0.65 * max(0, math.sin(typing_t * 7 - i * 0.9))
            ctx.arc(x + 30 + i * 22, y + bh / 2, 8, 0, 6.3)
            setc(ctx, TXT, a * alpha); ctx.fill()
    else:
        for i, l in enumerate(lines):
            text(ctx, l, x + 28, y + 17 + size * 0.98 + i * lh, size, TXT, alpha, weight="normal", align="left")
    ctx.restore()
    return bh


def chat(ctx, t, name, msgs, sub="", avatar_c=hexc('#555b6b'), letter="?", size=34, scroll_to_bottom=True,
         glitch=0.0):
    """msgs: list of (t_appear, text, side, opts) ; opts may contain typing_until"""
    setc(ctx, UI_BG); ctx.paint()
    # layout bottom-up
    items = []
    for m in msgs:
        ta, txt, side = m[0], m[1], m[2]
        opts = m[3] if len(m) > 3 else {}
        if t < ta:
            continue
        tu = opts.get('typing_until')
        if tu is not None and t < tu:
            items.append((ta, None, side, opts, t - ta))
        else:
            items.append((tu if tu is not None else ta, txt, side, opts, None))
    y = 250
    hs = []
    for ta, txt, side, opts, tt in items:
        lines = wrap(ctx, txt, opts.get('size', size), 470, "normal") if txt else [""]
        bh = (opts.get('size', size) * 1.3) * len(lines) + 34
        hs.append((y, ta, txt, side, opts, tt))
        y += bh + 22
    for y, ta, txt, side, opts, tt in hs:
        if y < 220 - 400:
            continue
        k = back_out(prog(t, ta, ta + 0.3))
        bubble(ctx, y, txt or "", side, alpha=clamp(k * 1.5), k=lerp(0.6, 1, k), size=opts.get('size', size),
               color=opts.get('color'), typing_t=tt)
    chat_header(ctx, name, sub, avatar_c, letter)
    # input bar
    ctx.rectangle(0, SH - 130, SW, 130); setc(ctx, hexc('#161922')); ctx.fill()
    rrect(ctx, 30, SH - 112, SW - 140, 66, 33); setc(ctx, hexc('#262a35')); ctx.fill()
    text(ctx, "Сообщение", 70, SH - 68, 28, SUB, weight="normal", align="left")
    ctx.arc(SW - 62, SH - 79, 33, 0, 6.3); setc(ctx, hexc('#2f6fe0')); ctx.fill()


def call_screen(ctx, t, name, status, letter="M", ended=0.0, timer=None):
    vgrad(ctx, 0, 0, SW, SH, [(0, hexc('#25324a'), 1), (1, hexc('#0d1018'), 1)])
    status_bar(ctx)
    pulse = 1 + 0.06 * math.sin(t * 5) * (1 - ended)
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        ctx.arc(SW / 2, 470, 110 + ph * 120, 0, 6.3)
        setc(ctx, (1, 1, 1), 0.12 * (1 - ph) * (1 - ended)); ctx.set_line_width(3); ctx.stroke()
    avatar(ctx, SW / 2, 470, 110 * pulse, hexc('#d1784a'), letter)
    text(ctx, name, SW / 2, 680, 54, TXT)
    st = status if timer is None else f"{int(timer) // 60:02d}:{int(timer) % 60:02d}"
    text(ctx, st, SW / 2, 740, 32, mix(SUB, hexc('#ff5b5b'), ended), weight="normal")
    # buttons
    for i, lab in enumerate(("звук", "клавиши", "динамик")):
        cx = SW / 2 + (i - 1) * 200
        ctx.arc(cx, 1060, 62, 0, 6.3); setc(ctx, (1, 1, 1), 0.14); ctx.fill()
        text(ctx, lab, cx, 1160, 24, SUB, weight="normal")
    ctx.arc(SW / 2, 1300, 70, 0, 6.3); setc(ctx, hexc('#e5484d')); ctx.fill()
    ctx.save(); ctx.translate(SW / 2, 1300); ctx.rotate(2.35)
    rrect(ctx, -34, -12, 68, 24, 12); setc(ctx, (1, 1, 1)); ctx.fill(); ctx.restore()


def mini_family_photo(ctx, x, y, w, h, seed, boy_alpha=1.0, ghost=0.0, bg=None):
    """A tiny flat 'photo' of the family; boy can fade out leaving an empty gap."""
    rnd = random.Random(seed)
    palettes = [hexc('#6b8fb3'), hexc('#c08a5a'), hexc('#7aa37a'), hexc('#b67a8c'), hexc('#8a7ab6')]
    sky = bg or palettes[seed % len(palettes)]
    ctx.save()
    ctx.rectangle(x, y, w, h); ctx.clip()
    vgrad(ctx, x, y, w, h, [(0, shade(sky, 1.25), 1), (0.62, sky, 1), (0.63, shade(sky, 0.7), 1), (1, shade(sky, 0.6), 1)])
    # sun / props
    ctx.arc(x + w * rnd.uniform(0.15, 0.85), y + h * 0.22, h * 0.09, 0, 6.3)
    setc(ctx, (1, 0.95, 0.8), 0.6); ctx.fill()
    from person import MOM, DAD, draw_person
    s = h / 900
    base = y + h * 0.98
    draw_person(ctx, DAD, dict(arms=dict(r=(18, 0)), expr='smile', breathe=0), x + w * 0.24, base, s)
    draw_person(ctx, MOM, dict(expr='smile', breathe=0), x + w * 0.76, base, s)
    if boy_alpha > 0.01:
        draw_person(ctx, BOY, dict(expr='smile', breathe=0), x + w * 0.5, base + h * 0.02, s * 0.92, alpha=boy_alpha)
    if ghost > 0.01:
        # dashed empty outline where the boy was
        ctx.save()
        ctx.set_dash([8 * s * 6, 6 * s * 6])
        ctx.set_line_width(2.5)
        ellipse(ctx, x + w * 0.5, base - 560 * s * 0.92, 95 * s, 95 * s)
        rrect(ctx, x + w * 0.5 - 90 * s, base - 480 * s * 0.92, 180 * s, 440 * s, 30 * s)
        setc(ctx, (1, 1, 1), 0.35 * ghost); ctx.stroke()
        ctx.restore()
    ctx.restore()


def gallery(ctx, t, vanish_start, step=0.18):
    setc(ctx, UI_BG); ctx.paint()
    status_bar(ctx)
    text(ctx, "Фото", 40, 190, 58, TXT, weight="black", align="left")
    cols, gap = 3, 6
    cw = (SW - gap * (cols - 1)) / cols
    n = 0
    order = list(range(18))
    random.Random(4).shuffle(order)
    for r in range(6):
        for cidx in range(cols):
            i = r * cols + cidx
            x = cidx * (cw + gap)
            y = 240 + r * (cw + gap)
            vt = vanish_start + order.index(i) * step
            k = prog(t, vt, vt + 0.35)
            if k < 1:
                mini_family_photo(ctx, x, y, cw, cw, i, boy_alpha=1.0)
                if k > 0:
                    # dissolve: noise squares
                    rnd = random.Random(i)
                    for q in range(60):
                        qx = x + rnd.random() * cw; qy = y + rnd.random() * cw
                        if rnd.random() < k:
                            ctx.rectangle(qx, qy, cw / 7, cw / 7); setc(ctx, UI_BG); ctx.fill()
                    ctx.rectangle(x, y, cw, cw); setc(ctx, UI_BG, k); ctx.fill()
            if k > 0.5:
                ctx.rectangle(x, y, cw, cw); setc(ctx, hexc('#1b1e26'), (k - 0.5) * 2); ctx.fill()
                # broken image icon
                ctx.set_line_width(3)
                rrect(ctx, x + cw / 2 - 30, y + cw / 2 - 24, 60, 48, 6); setc(ctx, SUB, 0.5 * (k - 0.5) * 2); ctx.stroke()
    allgone = prog(t, vanish_start + 18 * step, vanish_start + 18 * step + 0.4)
    if allgone > 0:
        text(ctx, "Нет фото", SW / 2, SH - 240, 40, TXT, allgone)
        text(ctx, "Медиатека пуста", SW / 2, SH - 190, 28, SUB, allgone, weight="normal")


CHATS = [("Мама", "Не забудь ключи", '#c0587a', 'М'), ("Папа", "Горжусь тобой, сын.", '#4a7bc0', 'П'),
         ("Макс", "бро, ты сегодня придёшь?", '#d1784a', 'М'), ("10 «Б»", "Аня: домашка на стр. 42", '#5a9a6a', '10'),
         ("Бабушка", "Позвони, когда сможешь", '#9a6ac0', 'Б'), ("Лёва", "ахахах", '#c09a4a', 'Л'),
         ("Тренер", "Тренировка в 18:00", '#4ab0b0', 'Т'), ("София", "спасибо за сегодня!", '#c04a4a', 'С')]


def chats_list(ctx, t, vanish_start, step=0.22):
    setc(ctx, UI_BG); ctx.paint()
    status_bar(ctx)
    text(ctx, "Чаты", 40, 190, 58, TXT, weight="black", align="left")
    allgone = prog(t, vanish_start + len(CHATS) * step, vanish_start + len(CHATS) * step + 0.4)
    for i, (name, msg, col, l) in enumerate(CHATS):
        y = 250 + i * 140
        vt = vanish_start + i * step
        k = ease_in(prog(t, vt, vt + 0.4))
        if k >= 1:
            continue
        a = 1 - k
        dx = -k * 200
        ctx.save(); ctx.translate(dx, 0)
        avatar(ctx, 80, y + 60, 46, hexc(col), l, a)
        text(ctx, name, 150, y + 50, 32, TXT, a, align="left")
        msg_clean = msg.replace(' ❤', '').replace(' 😂', '')
        text(ctx, msg_clean, 150, y + 92, 26, SUB, a, weight="normal", align="left")
        text(ctx, "7:1" + str(i), SW - 40, y + 50, 22, SUB, a, weight="normal", align="right")
        ctx.restore()
        if k > 0:
            rnd = random.Random(i * 13)
            for q in range(25):
                if rnd.random() < k * 1.2:
                    px = 30 + rnd.random() * 400 + k * 300 * rnd.random()
                    ctx.rectangle(px, y + 20 + rnd.random() * 90, 8, 8)
                    setc(ctx, TXT, (1 - k) * 0.7); ctx.fill()
    if allgone > 0:
        text(ctx, "Нет переписок", SW / 2, SH / 2, 40, TXT, allgone)


CONTACTS = ["Алексей Б.", "Аня Ким", "Бабушка", "Данил", "Даша", "Лёва", "Макс", "Мама", "Папа", "Саша",
            "София", "Тренер", "Эмма"]


def contacts(ctx, t, delete_t, name="Саша"):
    setc(ctx, UI_BG); ctx.paint()
    status_bar(ctx)
    text(ctx, "Контакты", 40, 190, 58, TXT, weight="black", align="left")
    rrect(ctx, 30, 225, SW - 60, 62, 18); setc(ctx, hexc('#1f232c')); ctx.fill()
    text(ctx, "Поиск", 70, 266, 28, SUB, weight="normal", align="left")
    k = prog(t, delete_t, delete_t + 0.9)
    gone_idx = CONTACTS.index(name)
    y = 330
    for i, c in enumerate(CONTACTS):
        h = 96
        if i == gone_idx:
            h = 96 * (1 - ease_io(prog(t, delete_t + 0.6, delete_t + 1.2)))
            if h > 2:
                hl = 1 - prog(t, delete_t + 0.3, delete_t + 0.7)
                ctx.rectangle(0, y, SW, h); setc(ctx, hexc('#2f6fe0'), 0.35 * hl); ctx.fill()
                # glitch letters
                rnd = random.Random(int(t * 30))
                shown = "".join(ch if rnd.random() > k else rnd.choice("▓▒░#%@") for ch in c)
                if k > 0.65:
                    shown = shown[:max(0, int(len(shown) * (1 - (k - 0.65) / 0.35)))]
                gx = rnd.uniform(-8, 8) * k
                text(ctx, shown, 60 + gx, y + h * 0.62, 34, hexc('#ff6b6b') if k > 0.1 else TXT, clamp(h / 96),
                     align="left", family="DejaVu Sans" if k > 0.05 else FONT)
        else:
            text(ctx, c, 60, y + 60, 34, TXT, weight="normal", align="left")
            ctx.rectangle(60, y + h - 1, SW - 60, 1); setc(ctx, (1, 1, 1), 0.08); ctx.fill()
        y += h
        if y > SH:
            break


def face_cam(ctx, t, ex, cam_shake=0.0, bg=hexc('#1a1c22'), lit=1.0, turn=0.0, tilt=0.0, look=(0, 0), blink=0.0,
             zoom=1.0):
    """front camera viewfinder showing the boy's face filling the screen"""
    setc(ctx, (0, 0, 0)); ctx.paint()
    ctx.save()
    vh = SH - 380
    ctx.rectangle(0, 140, SW, vh); ctx.clip()
    vgrad(ctx, 0, 140, SW, vh, [(0, shade(bg, 1.2), 1), (1, shade(bg, 0.6), 1)])
    dx, dy = shake(t, cam_shake, 6)
    ctx.translate(SW / 2 + dx, 140 + vh * 0.56 + dy)
    ctx.scale(3.1 * zoom, 3.1 * zoom)
    # shoulders
    ctx.save()
    ctx.translate(0, 120)
    rrect(ctx, -150, 0, 300, 220, 70); setc(ctx, BOY['top']); ctx.fill()
    ctx.rectangle(-16, -40, 32, 50); setc(ctx, shade(BOY['skin'], 0.85)); ctx.fill()
    ctx.restore()
    ctx.rotate(math.radians(tilt))
    draw_head(ctx, BOY, dict(turn=turn, look=look, blink=blink, t=t), expr(ex) if not isinstance(ex, dict) else ex)
    ctx.restore()
    # screen-light on face
    ctx.save(); ctx.rectangle(0, 140, SW, vh); ctx.clip()
    glow(ctx, SW / 2, 140 + vh * 0.45, 600, hexc('#5a7ab8'), 0.10 * lit)
    ctx.restore()
    # UI
    status_bar(ctx)
    text(ctx, "ФОТО", SW / 2, SH - 190, 26, hexc('#f5c542'))
    text(ctx, "ВИДЕО", SW / 2 - 150, SH - 190, 26, SUB)
    text(ctx, "ПОРТРЕТ", SW / 2 + 170, SH - 190, 26, SUB)
    ctx.arc(SW / 2, SH - 95, 58, 0, 6.3); setc(ctx, (1, 1, 1)); ctx.set_line_width(6); ctx.stroke()
    ctx.arc(SW / 2, SH - 95, 48, 0, 6.3); setc(ctx, (1, 1, 1)); ctx.fill()
    rrect(ctx, 60, SH - 130, 70, 70, 14); setc(ctx, hexc('#333333'), 1); ctx.fill()
    ctx.arc(SW - 95, SH - 95, 38, 0, 6.3); setc(ctx, hexc('#333333')); ctx.fill()
