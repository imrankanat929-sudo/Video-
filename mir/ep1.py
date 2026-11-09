"""Episode 1 - THE WORLD STOPPED / МИР ОСТАНОВИЛСЯ.

All timings are in seconds. Voice-over lines have a planned start time; the
voice should be placed at these marks (or re-time LINES to the real audio
and re-render)."""
import math
import random
import cairo
from .gfx import *  # noqa
from . import world as wd
from . import hero

DURATION = 114.0

# (start, english, russian)
LINES = [
    (0.6, "I was the only person moving in a city full of frozen people.",
     "Я был единственным, кто мог двигаться в городе, полном застывших людей."),
    (6.2, "Cars stood in the middle of the road.",
     "Машины замерли посреди дороги."),
    (9.7, "A bird hung motionless above a rooftop.",
     "Птица неподвижно висела над крышей."),
    (12.8, "Even the water in the fountain had stopped in midair.",
     "Даже вода в фонтане остановилась в воздухе."),
    (17.4, "But the strangest thing was waiting inside my apartment.",
     "Но самое странное ждало меня в квартире."),
    (22.5, "I woke up on an ordinary Tuesday and checked my phone.",
     "Я проснулся обычным вторником и посмотрел на телефон."),
    (27.3, "It said 9:17.",
     "Девять семнадцать."),
    (29.6, "The clock on the wall showed the same time, but its second hand was not moving.",
     "Настенные часы показывали то же время, но секундная стрелка не двигалась."),
    (36.8, "I looked through the window.",
     "Я выглянул в окно."),
    (39.2, "A bus was frozen halfway through a turn.",
     "Автобус застыл посреди поворота."),
    (42.8, "People stood on the pavement like statues.",
     "Люди стояли на тротуаре, как статуи."),
    (46.0, "One man's keys were hanging above the ground.",
     "У одного мужчины ключи зависли над землёй."),
    (50.5, "I ran downstairs and shouted for help.",
     "Я сбежал вниз и позвал на помощь."),
    (53.8, "Nobody answered.",
     "Никто не ответил."),
    (55.8, "I waved my hand in front of a woman's face.",
     "Я помахал рукой перед лицом женщины."),
    (60.3, "Nothing.",
     "Ничего."),
    (62.8, "Then every phone on the street lit up at once.",
     "И вдруг все телефоны на улице одновременно загорелись."),
    (67.3, "Mine buzzed too.",
     "Мой тоже завибрировал."),
    (69.3, "A message appeared from an unknown sender:",
     "Пришло сообщение от неизвестного отправителя:"),
    (72.5, "“YOU HAVE TEN MINUTES.”",
     "«У ТЕБЯ ЕСТЬ ДЕСЯТЬ МИНУТ»."),
    (75.3, "Ten minutes until what?",
     "Десять минут до чего?"),
    (78.0, "I looked up at the city clock.",
     "Я посмотрел на часы на городской башне."),
    (81.0, "Its hands began to move, even though every other clock was still.",
     "Их стрелки начали двигаться, хотя все остальные часы стояли."),
    (86.6, "A second message arrived.",
     "Пришло второе сообщение."),
    (88.8, "“DO NOT GO HOME.”",
     "«НЕ ВОЗВРАЩАЙСЯ ДОМОЙ»."),
    (92.0, "Behind me, the apartment building door slowly opened by itself.",
     "Позади меня дверь подъезда медленно открылась сама."),
    (100.5, "Would you go inside to find out who sent the message, or run toward the clock tower?",
     "Ты бы зашёл внутрь, чтобы узнать, кто отправил сообщение, или побежал к башне?"),
]

TEXT = {
    "ru": dict(ep="СЕРИЯ 1", t1="МИР", t2="ОСТАНОВИЛСЯ", hook="ВСЕ ЗАМЕРЛИ",
               weekday="Вторник, 9 ноября", unknown="Неизвестный", now="сейчас",
               msg1="У ТЕБЯ ЕСТЬ ДЕСЯТЬ МИНУТ", msg2="НЕ ВОЗВРАЩАЙСЯ ДОМОЙ",
               typing="печатает…", q="А ТЫ БЫ КУДА?", opt1="ЗАЙТИ ВНУТРЬ",
               opt2="БЕЖАТЬ К БАШНЕ", comment="ПИШИ 1 ИЛИ 2 В КОММЕНТАХ"),
    "en": dict(ep="EPISODE 1", t1="THE WORLD", t2="STOPPED", hook="EVERYONE FROZE",
               weekday="Tuesday, November 9", unknown="Unknown sender", now="now",
               msg1="YOU HAVE TEN MINUTES.", msg2="DO NOT GO HOME.",
               typing="typing…", q="WHAT WOULD YOU DO?", opt1="GO INSIDE",
               opt2="RUN TO THE TOWER", comment="COMMENT 1 OR 2"),
}

MSG1_T = 71.6   # first message bubble pops
MSG2_T = 88.6   # second message bubble pops
TIMER_T = 72.5  # countdown starts
TOWER_T = 81.0  # tower hands start moving
LIGHT_T = 63.8  # all phones light up
BUZZ_T = 67.3
DOOR_T0, DOOR_T1 = 92.8, 98.8
Q_T = 100.3
BLACK_T = 110.5


# ---------------- camera ----------------
class Cam:
    def __init__(self, z=1.0, cx=W / 2, cy=H / 2, sx=0.0, sy=0.0):
        self.z, self.cx, self.cy, self.sx, self.sy = z, cx, cy, sx, sy

    def apply(self, ctx, d=1.0):
        zl = 1 + (self.z - 1) * d
        ctx.translate(W / 2 + self.sx * d, H / 2 + self.sy * d)
        ctx.scale(zl, zl)
        ctx.translate(-(W / 2 + (self.cx - W / 2) * d), -(H / 2 + (self.cy - H / 2) * d))


def shake(t, t0, dur=0.6, amp=18):
    p = seg(t, t0, t0 + dur)
    if p <= 0 or p >= 1:
        return 0.0, 0.0
    k = (1 - p) ** 2 * amp
    return math.sin(t * 91) * k, math.cos(t * 77) * k


def layer(ctx, cam, d, fn):
    ctx.save()
    cam.apply(ctx, d)
    fn()
    ctx.restore()


def haze(ctx, y, h, c="#8b8590", a=0.35):
    vgrad(ctx, -600, y, W + 1200, h, [(0, col(c, 0)), (0.6, col(c, a)), (1, col(c, a * 0.4))])


# ---------------- shots ----------------
def shot_street(ctx, t, lt, L):
    z = 1.0 + 0.06 * ease(lt / 9.5) + 0.14 * ease(seg(t, 6.0, 8.8))
    cam = Cam(z, lerp(540, 600, ease(seg(t, 6.0, 8.8))), lerp(960, 1200, ease(seg(t, 6.0, 8.8))))
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -300, H + 600, sun=(820, 1050, 700)))
    layer(ctx, cam, 0.25, lambda: wd.skyline(ctx, 1, 1120, "#3d4862", n=9, hmin=250, hmax=650, lit=0.06))
    layer(ctx, cam, 0.35, lambda: haze(ctx, 800, 360, a=0.3))

    def mid():
        wd.skyline(ctx, 2, 1210, "#2d364b", hmin=200, hmax=520, lit=0.12)
        haze(ctx, 1050, 170, a=0.25)
    layer(ctx, cam, 0.5, mid)

    def near():
        wd.ground(ctx, 1200)
        wd.lane_marks(ctx, 1560)
        wd.streetlamp(ctx, 70, 1262, 420, on=0.6)
        wd.streetlamp(ctx, 960, 1262, 420, on=0.6)
        wd.person(ctx, 200, 1262, 230, "#5a4a6a", pose=1)
        wd.person(ctx, 360, 1262, 220, "#4a6070", facing=-1)
        wd.person(ctx, 720, 1262, 235, "#6a5547", pose=1, bag=True)
        wd.person(ctx, 860, 1262, 215, "#3f5a4a", facing=-1, skirt=True)
        wd.car(ctx, 330, 1470, 400, "#7a4d4a", lights=0.6)
        wd.car(ctx, 820, 1700, 460, "#4d5e7a", facing=-1, lights=0.6)
        wd.car(ctx, -120, 1700, 420, "#6b6b48", lights=0.5)
    layer(ctx, cam, 1.0, near)
    layer(ctx, cam, 1.35, lambda: wd.dust(ctx, 3, 70, 0.5))


def shot_bird(ctx, t, lt, L):
    p = ease(lt / 3.2)
    cam = Cam(1.0 + 0.18 * p, 540, lerp(1150, 880, p))
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -300, H + 600, stops=[(0, "#1a2236"), (0.6, "#3d4a66"), (1, "#7d7b88")]))

    def clouds():
        for x, y, s in ((200, 500, 1.0), (760, 330, 1.3), (900, 820, 0.8), (90, 900, 0.7)):
            for k in range(4):
                ellipse(ctx, x + k * 70 * s, y - (k % 2) * 30 * s, 110 * s, 55 * s, "#8d93a8", 0.35)
    layer(ctx, cam, 0.3, clouds)

    def roof():
        poly(ctx, [(-300, 1350), (1400, 1250), (1400, 2400), (-300, 2400)], "#262b38")
        fill_rect(ctx, 700, 1120, 90, 160, "#2f3442")
        fill_rect(ctx, 690, 1110, 110, 20, "#3a4050")
        line(ctx, 250, 1330, 250, 1050, 6, "#1b1f29")
        line(ctx, 200, 1110, 300, 1110, 5, "#1b1f29")
        line(ctx, 215, 1160, 285, 1160, 5, "#1b1f29")
        wd.bird(ctx, 540, 820, 170)
        # frozen feathers
        for fx, fy, a in ((640, 900, 0.4), (470, 930, -0.7), (600, 980, 1.2)):
            ctx.save()
            ctx.translate(fx, fy)
            ctx.rotate(a)
            ellipse(ctx, 0, 0, 16, 5, "#c9ccd6", 0.85)
            ctx.restore()
        r = 210 + 10 * math.sin(lt * 4)
        ctx.arc(540, 830, r, 0, 2 * math.pi)
        ctx.set_line_width(5)
        setc(ctx, "#ffffff", 0.35 * seg(lt, 0.6, 1.2))
        ctx.stroke()
    layer(ctx, cam, 1.0, roof)
    layer(ctx, cam, 1.3, lambda: wd.dust(ctx, 4, 50, 0.45))


def shot_fountain(ctx, t, lt, L):
    p = ease(lt / 4.5)
    cam = Cam(1.05 + 0.15 * p, 540, lerp(1120, 1180, p))
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -300, H + 600, sun=(300, 1000, 600)))
    layer(ctx, cam, 0.3, lambda: wd.skyline(ctx, 7, 1100, "#36405a", hmin=200, hmax=600, lit=0.08))

    def trees():
        haze(ctx, 900, 260, a=0.3)
        for i, x in enumerate((-40, 160, 380, 700, 920, 1120)):
            wd.tree(ctx, x, 1170, 330 + (i % 2) * 60)
    layer(ctx, cam, 0.6, trees)

    def plaza():
        fill_rect(ctx, -600, 1160, W + 1200, 1200, "#4a4d57")
        for i in range(-6, 20):
            line(ctx, i * 120 - 300, 1160, i * 220 - 1300, 2600, 2, "#000000", 0.15)
        for j in range(8):
            yy = 1160 + j * j * 22
            line(ctx, -600, yy, W + 600, yy, 2, "#000000", 0.12)
        wd.fountain(ctx, 540, 1330, 380, t)
        wd.person(ctx, 900, 1560, 360, "#57606e", facing=-1, pose=1)
        # coin frozen in the air
        circle(ctx, 790, 1220, 13, "#e3c35b")
        circle(ctx, 786, 1216, 4, "#fff4c0")
        glow(ctx, 790, 1220, 40, "#ffe08a", 0.4)
        wd.bird(ctx, 220, 1600, 60, "#3a3d48")
    layer(ctx, cam, 1.0, plaza)
    layer(ctx, cam, 1.3, lambda: wd.dust(ctx, 5, 60, 0.4))


def shot_apartment(ctx, t, lt, L):
    p = ease(lt / 5.1)
    cam = Cam(1.0 + 0.75 * p, lerp(540, 720, p), lerp(1000, 560, p))
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -600, H + 1200))
    layer(ctx, cam, 0.3, lambda: wd.skyline(ctx, 9, 1500, "#333c52", hmin=500, hmax=1100, lit=0.05))

    def build():
        g = 0.65 + 0.35 * math.sin(lt * 3.0)
        wd.apartment(ctx, 540, 1750, 900, 1600, seed=5, hero_window=(2, 3, g))
        wd.ground(ctx, 1782)
    layer(ctx, cam, 1.0, build)
    layer(ctx, cam, 1.2, lambda: wd.dust(ctx, 6, 40, 0.4))


def bedroom_bg(ctx, cam):
    def wall():
        vgrad(ctx, -400, -400, W + 800, H + 800, [(0, "#1b1b22"), (1, "#2c2a33")])
        # cold window light on the wall
        poly(ctx, [(-100, 200), (380, 120), (520, 1300), (-100, 1500)], "#8fb4d9", 0.08)
        fill_rect(ctx, 760, 300, 260, 360, "#000000", 0.18)
    layer(ctx, cam, 0.3, wall)

    def bed():
        ellipse(ctx, 540, 1900, 900, 420, "#33415a")
        ellipse(ctx, 300, 1700, 330, 120, "#d9d7dd", 0.15)
    layer(ctx, cam, 0.7, bed)


def lockscreen(ctx, sx, sy, sw, sh, L, t, pulse=0.0):
    ctx.save()
    rrect(ctx, sx, sy, sw, sh, sw * 0.1)
    ctx.clip()
    vgrad(ctx, sx, sy, sw, sh, [(0, "#16233d"), (0.6, "#3a2c54"), (1, "#5a3a52")])
    glow(ctx, sx + sw * 0.7, sy + sh * 0.75, sw * 0.9, "#ff8fa0", 0.25)
    text(ctx, L["weekday"], sx + sw / 2, sy + sh * 0.17, sw * 0.065, "#e8ecf5", FONT_BOLD, shadow=False)
    sc = 1 + 0.12 * pulse
    ctx.save()
    ctx.translate(sx + sw / 2, sy + sh * 0.33)
    ctx.scale(sc, sc)
    text(ctx, "9:17", 0, 0, sw * 0.3, "#ffffff", FONT_BLACK, shadow=False)
    ctx.restore()
    if pulse:
        glow(ctx, sx + sw / 2, sy + sh * 0.28, sw * 0.6, "#ffffff", 0.25 * pulse)
    # status bar
    fill_rrect(ctx, sx + sw * 0.78, sy + sh * 0.035, sw * 0.1, sh * 0.018, 4, "#ffffff", 0.8)
    fill_rrect(ctx, sx + sw * 0.36, sy + sh * 0.025, sw * 0.28, sh * 0.03, sh * 0.015, "#000000")
    ctx.restore()


def msg_screen(ctx, sx, sy, sw, sh, L, t, n_msgs, typing=False, red2=False, glitch=0.0):
    ctx.save()
    rrect(ctx, sx, sy, sw, sh, sw * 0.1)
    ctx.clip()
    fill_rect(ctx, sx, sy, sw, sh, "#0f1218")
    # header
    fill_rect(ctx, sx, sy, sw, sh * 0.15, "#1a1f29")
    circle(ctx, sx + sw * 0.15, sy + sh * 0.095, sw * 0.075, "#3b4252")
    text(ctx, "?", sx + sw * 0.15, sy + sh * 0.113, sw * 0.09, "#ffffff", FONT_BLACK, shadow=False)
    text(ctx, L["unknown"], sx + sw * 0.28, sy + sh * 0.09, sw * 0.062, "#ffffff", FONT_BOLD, align="left",
         shadow=False, fit=sw * 0.66)
    text(ctx, L["typing"] if typing else L["now"], sx + sw * 0.28, sy + sh * 0.122, sw * 0.045,
         "#7fb3ff" if typing else "#8a93a6", FONT_BOLD, align="left", shadow=False)
    fill_rrect(ctx, sx + sw * 0.36, sy + sh * 0.025, sw * 0.28, sh * 0.03, sh * 0.015, "#000000")
    y = sy + sh * 0.2

    def bubble(msg, y, bg, fg, a=1.0, sc=1.0):
        fs = sw * 0.1
        font(ctx, fs, FONT_BLACK)
        lines = wrap(ctx, msg, sw * 0.78)
        bh = len(lines) * fs * 1.2 + fs * 0.9
        bw = max(text_w(ctx, ln) for ln in lines) + fs * 1.1
        ctx.save()
        ctx.translate(sx + sw * 0.06, y)
        ctx.scale(max(sc, 0.01), max(sc, 0.01))
        fill_rrect(ctx, 0, 0, bw, bh, fs * 0.6, bg, a)
        for i, ln in enumerate(lines):
            text(ctx, ln, fs * 0.55, fs * 1.25 + i * fs * 1.2, fs, fg, FONT_BLACK, align="left", shadow=False, a=a)
        ctx.restore()
        return bh

    for i in range(n_msgs):
        msg = L["msg1"] if i == 0 else L["msg2"]
        if i == 1:
            sc = pop(t, MSG2_T)
            bg = "#d21f2a" if red2 else "#2a3242"
            y += bubble(msg, y, bg, "#ffffff", sc=sc) + sh * 0.03
        else:
            sc = pop(t, MSG1_T)
            dim = n_msgs > 1
            y += bubble(msg, y, "#2a3242" if dim else "#e8ecf5", "#9aa3b5" if dim else "#0f1218",
                        sc=sc) + sh * 0.03
    if typing:
        fill_rrect(ctx, sx + sw * 0.06, y, sw * 0.26, sw * 0.13, sw * 0.065, "#2a3242")
        for k in range(3):
            a = 0.35 + 0.65 * max(0, math.sin(t * 7 - k * 0.8))
            circle(ctx, sx + sw * (0.12 + k * 0.07), y + sw * 0.065, sw * 0.018, "#cfd6e4", a)
    if glitch:
        rnd = random.Random(int(t * 30))
        for _ in range(6):
            gy = sy + rnd.random() * sh
            fill_rect(ctx, sx, gy, sw, rnd.uniform(4, 22), rnd.choice(["#ff2a3a", "#2affff", "#ffffff"]), 0.35 * glitch)
    ctx.restore()


def shot_phone(ctx, t, lt, L):
    cam = Cam(1.0 + 0.08 * ease(lt / 7), 540, 900)
    bedroom_bg(ctx, cam)
    pulse = math.exp(-((t - 27.6) / 0.35) ** 2)

    def ph():
        wd.hand_holding(ctx, 540, 900, 420, part="back")
        s = wd.phone_body(ctx, 540, 900, 420, glow_a=0.5 + 0.3 * pulse)
        lockscreen(ctx, *s, L, t, pulse)
        wd.hand_holding(ctx, 540, 900, 420, part="front")
    layer(ctx, cam, 1.0, ph)


def shot_wallclock(ctx, t, lt, L):
    cam = Cam(1.0 + 0.3 * ease(lt / 7.2), 540, lerp(900, 860, ease(lt / 7.2)))

    def wall():
        vgrad(ctx, -400, -400, W + 800, H + 800, [(0, "#24232c"), (1, "#312e38")])
        for i in range(-6, 20):
            fill_rect(ctx, i * 90, -400, 3, H + 800, "#ffffff", 0.025)
        poly(ctx, [(-100, 300), (300, 200), (520, 1500), (-100, 1700)], "#8fb4d9", 0.07)
        fill_rect(ctx, 120, 1420, 840, 26, "#3d3530")
        fill_rect(ctx, 200, 1300, 70, 120, "#5a6a7a")
        fill_rect(ctx, 300, 1340, 180, 80, "#6a4d4a")
        fill_rect(ctx, 760, 1250, 40, 170, "#4a5a4a")
        circle(ctx, 780, 1240, 50, "#3a4a3a")
    layer(ctx, cam, 0.6, wall)
    # second hand twitches every second but never moves on
    twitch = max(0.0, math.sin((t % 1.0) * math.pi)) ** 10 * 0.45
    layer(ctx, cam, 1.0, lambda: wd.clock_face(ctx, 540, 860, 300, 9, 17, 23 + twitch, light=0.15))


def shot_window(ctx, t, lt, L):
    # camera path: room -> bus -> pavement -> keys
    keys_xy = (790, 1330)
    p1 = ease(seg(t, 38.4, 40.2))
    p2 = ease(seg(t, 42.6, 44.0))
    p3 = ease(seg(t, 45.8, 47.2))
    z = 1.0 + 0.4 * p1 + 0.1 * p2 + 0.6 * p3
    cx = lerp(lerp(lerp(540, 470, p1), 500, p2), keys_xy[0], p3)
    cy = lerp(lerp(lerp(960, 1080, p1), 1330, p2), keys_xy[1] - 60, p3)
    cam = Cam(z, cx, cy)

    def outside():
        fill_rect(ctx, -600, -600, W + 1200, 1300, "#3a4156")
        wd.skyline(ctx, 21, 700, "#424a61", n=8, hmin=900, hmax=1300, lit=0.12)
        fill_rect(ctx, -600, 700, W + 1200, 120, "#3d414c")
        fill_rect(ctx, -600, 820, W + 1200, 480, "#24272f")
        for i in range(-4, 14):
            fill_rect(ctx, i * 150, 1040, 80, 10, "#d8d2c0", 0.6)
        for i in range(8):
            fill_rect(ctx, 820 + i * 46, 840, 28, 440, "#d8d2c0", 0.35)
        # curved skid of the turn
        ctx.arc(1000, 1500, 640, math.pi * 1.05, math.pi * 1.35)
        ctx.set_line_width(10)
        setc(ctx, "#000000", 0.25)
        ctx.stroke()
        fill_rect(ctx, -600, 1300, W + 1200, 200, "#3d414c")
        fill_rect(ctx, -600, 1300, W + 1200, 8, "#5a5e68")
        fill_rect(ctx, -600, 1500, W + 1200, 900, "#2b2e36")
        for x, h in ((-20, 150), (120, 160), (300, 140)):
            wd.person(ctx, x, 815, h, PEOPLE[x % 5])
        wd.bus(ctx, 430, 1150, 660, angle=-0.16)
        wd.person(ctx, 120, 1440, 300, "#5a4a6a", pose=1)
        wd.person(ctx, 300, 1450, 290, "#4a6070", facing=-1, bag=True)
        wd.person(ctx, 500, 1445, 310, "#6b4650", pose=1, skirt=True)
        wd.person(ctx, 900, 1450, 330, "#57606e", facing=-1, keys=True)
        # keys frozen in midair + their fall trail
        for k in range(4):
            circle(ctx, keys_xy[0] + 6, keys_xy[1] - 60 - k * 22, 4, "#ffffff", 0.25 - k * 0.05)
        wd.keys(ctx, *keys_xy, 40)
        if t > 46.0:
            r = 75 + 6 * math.sin(t * 6)
            ctx.arc(keys_xy[0], keys_xy[1], r, 0, 2 * math.pi)
            ctx.set_line_width(7)
            setc(ctx, "#e3262f", seg(t, 46.0, 46.4))
            ctx.stroke()
    layer(ctx, cam, 1.0, outside)

    def frame():
        a = 1 - seg(t, 39.2, 40.0)
        if a <= 0:
            return
        ctx.rectangle(-800, -800, W + 1600, H + 1600)
        ctx.rectangle(150, 380, 780, 1100)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        setc(ctx, "#17171d", a)
        ctx.fill()
        ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        fill_rect(ctx, 530, 380, 20, 1100, "#2a2a33", a)
        fill_rect(ctx, 150, 860, 780, 20, "#2a2a33", a)
        fill_rect(ctx, 110, 1470, 860, 50, "#34333c", a)
        poly(ctx, [(60, 330), (260, 330), (200, 1480), (40, 1480)], "#3a3046", a)
        poly(ctx, [(1020, 330), (820, 330), (880, 1480), (1040, 1480)], "#3a3046", a)
    layer(ctx, cam, 1.7, frame)


PEOPLE = wd.PEOPLE_COLORS


def shot_runout(ctx, t, lt, L):
    cam = Cam(1.05 - 0.05 * ease(seg(t, 53.6, 55.6)), 540, 1150)
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -400, H + 800))
    layer(ctx, cam, 0.3, lambda: wd.skyline(ctx, 31, 1250, "#36405a", hmin=300, hmax=800, lit=0.06))

    def near():
        haze(ctx, 1000, 300, a=0.25)
        wd.apartment(ctx, -80, 1400, 900, 1700, seed=8)
        wd.ground(ctx, 1400, walk="#3b3f4a")
        wd.streetlamp(ctx, 980, 1450, 430, on=0.5)
        wd.person(ctx, 690, 1462, 290, "#6a5547", pose=1)
        wd.person(ctx, 900, 1470, 300, "#3f5a4a", facing=-1)
        wd.car(ctx, 820, 1700, 420, "#4d5e7a", facing=-1)
        # hero runs out of the doorway towards the street
        p = ease_out(seg(t, 50.2, 52.2))
        hx, hy = lerp(-60, 470, p), lerp(1460, 1640, p)
        h = lerp(300, 420, p)
        step = (t * 14) if p < 0.98 else 0.0
        hero.body_back(ctx, hx, hy, h, step=step)
        # shout rings
        for k in range(3):
            q = seg(t, 52.0 + k * 0.35, 53.6 + k * 0.35)
            if 0 < q < 1:
                ctx.arc(hx, hy - h * 0.9, 60 + q * 520, -math.pi * 0.95, -math.pi * 0.05)
                ctx.set_line_width(8)
                setc(ctx, "#ffffff", 0.45 * (1 - q))
                ctx.stroke()
    layer(ctx, cam, 1.0, near)
    layer(ctx, cam, 1.3, lambda: wd.dust(ctx, 32, 50, 0.4))


def shot_wave(ctx, t, lt, L):
    cam = Cam(1.0 + 0.12 * ease(lt / 6.9), 540, 1150)
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -400, H + 800))
    layer(ctx, cam, 0.3, lambda: (wd.skyline(ctx, 41, 1300, "#36405a", hmin=300, hmax=900, lit=0.06),
                                  haze(ctx, 1000, 320, a=0.3)))
    layer(ctx, cam, 0.6, lambda: (wd.ground(ctx, 1450), wd.car(ctx, 200, 1640, 380, "#6b6b48")))

    def fg():
        ellipse(ctx, 540, 1800, 600, 50, "#000000", 0.25)
        wd.person(ctx, 720, 1800, 940, "#6b4650", hair="#3a2a20", facing=-1, skirt=True)
        waving = seg(t, 56.4, 56.8) * (1 - seg(t, 60.0, 60.6))
        arm = 0.25 + waving * (0.62 + 0.12 * math.sin(t * 13))
        hero.body_side(ctx, 320, 1800, 860, facing=1, arm=arm)
    layer(ctx, cam, 1.0, fg)
    layer(ctx, cam, 1.3, lambda: wd.dust(ctx, 42, 50, 0.4))


def shot_phones(ctx, t, lt, L):
    sx, sy = shake(t, LIGHT_T, 0.8, 22)
    bx, by = shake(t, BUZZ_T, 0.5, 10)
    cam = Cam(1.0 + 0.06 * ease(lt / 6.6) + 0.12 * ease(seg(t, BUZZ_T, BUZZ_T + 1.2)), 540,
              lerp(1100, 1350, ease(seg(t, BUZZ_T, BUZZ_T + 1.2))), sx + bx, sy + by)
    lit = lambda x: ease(seg(t, LIGHT_T + x / 4000, LIGHT_T + x / 4000 + 0.25))
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -400, H + 800, stops=[(0, "#0f1422"), (0.6, "#26304a"), (1, "#545a6e")]))

    def city():
        wd.skyline(ctx, 51, 1180, "#2a3246", hmin=300, hmax=800, lit=0.08)
        haze(ctx, 950, 260, a=0.25)
        # windows of the city light up too
        rnd = random.Random(52)
        for _ in range(60):
            x, y = rnd.uniform(-300, W + 300), rnd.uniform(500, 1150)
            l = lit(x + 300)
            if l:
                fill_rect(ctx, x, y, 16, 20, "#bfe6ff", 0.7 * l)
    layer(ctx, cam, 0.35, city)

    def street():
        wd.ground(ctx, 1200)
        for x, y, h, c, f in ((60, 1262, 220, "#5a4a6a", 1), (230, 1262, 230, "#4a6070", -1),
                              (420, 1262, 215, "#6a5547", 1), (640, 1262, 225, "#3f5a4a", -1),
                              (820, 1262, 235, "#6b4650", 1), (1010, 1262, 220, "#57606e", -1),
                              (150, 1560, 330, "#7a6a4a", 1), (900, 1580, 340, "#4a6070", -1)):
            wd.person(ctx, x, y, h, c, phone=max(0.05, lit(x)), facing=f)
        # hero in the foreground, his phone buzzes
        hx, hy, h = 540, 1840, 560
        buzz = seg(t, BUZZ_T, BUZZ_T + 0.3)
        hero.body_back(ctx, hx, hy, h, arm_up=0.38 * ease(seg(t, BUZZ_T, BUZZ_T + 0.5)))
        if buzz:
            px, py = hx + h * 0.42, hy - h * 0.86
            glow(ctx, px, py, 160, "#bfe6ff", 0.7)
            fill_rrect(ctx, px - 16, py - 30, 32, 60, 6, "#d9f1ff")
            for k in range(3):
                q = ((t - BUZZ_T) * 2.5 + k / 3) % 1
                if t < BUZZ_T + 1.8:
                    ctx.arc(px, py, 40 + q * 70, -0.6, 0.6)
                    ctx.set_line_width(5)
                    setc(ctx, "#ffffff", 0.6 * (1 - q))
                    ctx.stroke()
                    ctx.arc(px, py, 40 + q * 70, math.pi - 0.6, math.pi + 0.6)
                    ctx.stroke()
    layer(ctx, cam, 1.0, street)
    # flash when every phone lights up
    f = math.exp(-((t - LIGHT_T - 0.1) / 0.18) ** 2)
    if f > 0.01:
        fill_rect(ctx, 0, 0, W, H, "#dff3ff", 0.35 * f)


def phone_closeup(ctx, t, lt, L, n_msgs, typing, red2=False, glitch=0.0, zoom=0.1, dur=8.0,
                  sh=(0.0, 0.0)):
    cam = Cam(1.0 + zoom * ease(lt / dur), 540, 860, *sh)

    def bg():
        vgrad(ctx, -400, -400, W + 800, H + 800, [(0, "#11141c"), (1, "#252a36")])
        wd.skyline(ctx, 61, 1700, "#1c2130", hmin=400, hmax=900, lit=0.1)
        for i in range(5):
            glow(ctx, 100 + i * 230, 1500 + (i % 2) * 120, 180, "#bfe6ff", 0.25)
    layer(ctx, cam, 0.3, bg)

    def ph():
        wd.hand_holding(ctx, 540, 860, 520, part="back")
        s = wd.phone_body(ctx, 540, 860, 520, glow_a=0.7, glow_c="#ff4b55" if red2 and t > MSG2_T else "#9fd3ff")
        msg_screen(ctx, *s, L, t, n_msgs, typing, red2, glitch)
        wd.hand_holding(ctx, 540, 860, 520, part="front")
    layer(ctx, cam, 1.0, ph)


def shot_msg1(ctx, t, lt, L):
    typing = 69.8 < t < MSG1_T
    n = 1 if t >= MSG1_T else 0
    phone_closeup(ctx, t, lt, L, n, typing, zoom=0.14, dur=8.6, sh=shake(t, MSG1_T, 0.4, 10))


def shot_tower(ctx, t, lt, L):
    run = max(0.0, t - TOWER_T)
    ss = 23 + run * 6.0          # hands visibly sweep
    mm = 17 + ss / 60
    light = ease(seg(t, TOWER_T, TOWER_T + 1.5))
    p = ease(lt / 8.7)
    sx, sy = shake(t, TOWER_T, 0.7, 16)
    cam = Cam(1.0 + 0.3 * p, 540, lerp(1000, 760, p), sx, sy)
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -400, H + 800, stops=[(0, "#0e1322"), (0.55, "#2a3550"), (1, "#6d6c7c")]))

    def clouds():
        for x, y, s in ((150, 300, 1.2), (820, 520, 1.0), (300, 1100, 0.9), (900, 1000, 1.1)):
            for k in range(4):
                ellipse(ctx, x + k * 70 * s, y - (k % 2) * 30 * s, 120 * s, 50 * s, "#7d8398", 0.3)
    layer(ctx, cam, 0.25, clouds)
    layer(ctx, cam, 0.5, lambda: (wd.skyline(ctx, 71, 1750, "#262d40", hmin=300, hmax=600, lit=0.08),
                                  haze(ctx, 1350, 400, a=0.25)))

    def tw():
        if light:
            for k in range(3):
                q = ((t - TOWER_T) * 0.8 + k / 3) % 1
                ctx.arc(540, 715, 120 + q * 500, 0, 2 * math.pi)
                ctx.set_line_width(4)
                setc(ctx, "#ffe2a8", 0.35 * (1 - q) * light)
                ctx.stroke()
        wd.tower(ctx, 540, 1900, 300, 1350, (9, mm, ss), light=light)
    layer(ctx, cam, 0.8, tw)

    def fg():
        # a street clock in the foreground stays frozen at 9:17
        line(ctx, 120, 2000, 120, 1350, 16, "#14171f")
        wd.clock_face(ctx, 120, 1300, 90, 9, 17, 23, face="#cfcabc")
    layer(ctx, cam, 1.3, fg)


def shot_msg2(ctx, t, lt, L):
    typing = 87.2 < t < MSG2_T
    n = 2 if t >= MSG2_T else 1
    g = math.exp(-((t - MSG2_T - 0.15) / 0.2) ** 2)
    phone_closeup(ctx, t, lt, L, n, typing, red2=True, glitch=g, zoom=0.12, dur=5.4,
                  sh=shake(t, MSG2_T, 0.6, 20))


def door_scene(ctx, t, z, sh=(0, 0), frozen_t=None):
    tt = t if frozen_t is None else frozen_t
    op = ease(seg(tt, DOOR_T0, DOOR_T1)) * 0.92
    cam = Cam(z, 540, 1250, *sh)
    layer(ctx, cam, 0.1, lambda: wd.sky(ctx, -600, H + 1200, stops=[(0, "#0e1220"), (0.7, "#262f45"), (1, "#4a4c5c")]))

    def b():
        wd.apartment(ctx, 540, 1500, 1150, 1800, seed=12, door_open=op, door_light=op, lit=0.1)
        wd.ground(ctx, 1532)
        wd.streetlamp(ctx, 1000, 1590, 650, on=0.7)
        # cold light spilling out of the doorway
        if op:
            poly(ctx, [(455, 1500), (625, 1500), (760, 1900), (320, 1900)], "#7fa8d6", 0.12 * op)
    layer(ctx, cam, 1.0, b)
    layer(ctx, cam, 1.2, lambda: wd.dust(ctx, 81, 80, 0.45, area=(300, 900, 480, 900), color="#bcd8ff"))


def shot_door(ctx, t, lt, L):
    p = ease(lt / 8.5)
    door_scene(ctx, t, 1.45 + 0.3 * p, shake(t, DOOR_T0, 0.5, 8))
    sc = pop(t, 96.6)
    if sc:
        sticker(ctx, L["msg2"], 540, 300, 62, angle=-4, s_scale=sc)


def shot_question(ctx, t, lt, L):
    # motion stops on the main object (the open door)
    door_scene(ctx, t, 1.75, frozen_t=Q_T)
    fill_rect(ctx, 0, 0, W, H, "#000000", 0.45 * seg(lt, 0, 0.6))
    s = pop(t, Q_T + 0.3)
    if s:
        ctx.save()
        ctx.translate(540, 290)
        ctx.scale(s, s)
        text(ctx, L["q"], 0, 0, 96, "#ffd23f", outline=9, fit=980)
        ctx.restore()

    def option(i, label, y, t0, icon):
        s = pop(t, t0)
        if not s:
            return
        ctx.save()
        ctx.translate(540, y)
        ctx.scale(s, s)
        fill_rrect(ctx, -470 + 8, -80 + 12, 940, 160, 40, "#000000", 0.5)
        fill_rrect(ctx, -470, -80, 940, 160, 40, "#ffffff")
        fill_rrect(ctx, -464, -74, 928, 148, 36, "#1c2030")
        circle(ctx, -380, 0, 52, "#e3262f")
        text(ctx, str(i), -380, 26, 72, "#ffffff", shadow=False)
        icon(-270, 0)
        text(ctx, label, -200, 26, 70, "#ffffff", align="left", fit=640)
        ctx.restore()

    def door_icon(x, y):
        fill_rrect(ctx, x - 30, y - 50, 60, 100, 6, "#7fa8d6")
        fill_rect(ctx, x - 22, y - 42, 30, 92, "#050608")
        circle(ctx, x + 18, y + 4, 5, "#1c2030")

    def tower_icon(x, y):
        fill_rect(ctx, x - 22, y - 30, 44, 80, "#ffe2a8")
        poly(ctx, [(x - 30, y - 30), (x, y - 62), (x + 30, y - 30)], "#ffe2a8")
        circle(ctx, x, y - 6, 15, "#1c2030")
        line(ctx, x, y - 6, x, y - 16, 3, "#ffe2a8")
        line(ctx, x, y - 6, x + 7, y - 6, 3, "#ffe2a8")

    option(1, L["opt1"], 520, 101.4, door_icon)
    option(2, L["opt2"], 720, 104.6, tower_icon)
    c = seg(t, 107.4, 107.8)
    if c:
        text(ctx, L["comment"], 540, 900, 48, "#ffffff", outline=5, a=c, fit=940)


SHOTS = [
    (0.0, 9.5, shot_street),
    (9.5, 12.7, shot_bird),
    (12.7, 17.2, shot_fountain),
    (17.2, 22.3, shot_apartment),
    (22.3, 29.4, shot_phone),
    (29.4, 36.6, shot_wallclock),
    (36.6, 50.2, shot_window),
    (50.2, 55.6, shot_runout),
    (55.6, 62.5, shot_wave),
    (62.5, 69.1, shot_phones),
    (69.1, 77.7, shot_msg1),
    (77.7, 86.4, shot_tower),
    (86.4, 91.8, shot_msg2),
    (91.8, Q_T, shot_door),
    (Q_T, BLACK_T, shot_question),
]

# reaction bust: (time, expression, look, visible)
BUST = [
    (0.0, "scared", (0.6, -0.3), True),
    (6.2, "surprised", (0.5, 0.2), True),
    (9.5, "surprised", (0.3, -1.0), True),
    (12.7, "neutral", (0.6, 0.0), True),
    (17.2, "worried", (0.6, -0.8), True),
    (22.3, "neutral", (0.5, -0.4), True),
    (27.3, "surprised", (0.5, -0.4), True),
    (29.4, "surprised", (0.4, -0.7), True),
    (33.5, "worried", (0.4, -0.7), True),
    (36.6, "neutral", (0.6, -0.2), True),
    (39.2, "surprised", (0.6, -0.2), True),
    (46.0, "scared", (0.7, -0.1), True),
    (50.2, "scared", (0.0, 0.0), False),
    (69.1, "worried", (0.6, -0.4), True),
    (MSG1_T, "scared", (0.6, -0.4), True),
    (75.3, "worried", (0.6, -0.4), True),
    (77.7, "surprised", (0.3, -1.0), True),
    (TOWER_T, "scared", (0.3, -1.0), True),
    (86.4, "worried", (0.6, -0.4), True),
    (MSG2_T, "scared", (0.6, -0.4), True),
    (91.8, "scared", (0.8, -0.2), True),
    (Q_T, "worried", (0.6, -0.3), True),
    (105.5, "determined", (0.7, -0.3), True),
    (BLACK_T, "determined", (0.0, 0.0), False),
]


def bust_state(t):
    cur = BUST[0]
    for b in BUST:
        if b[0] <= t:
            cur = b
    # visibility slide
    vis = 1.0
    for i, b in enumerate(BUST):
        if b[0] <= t:
            prev_vis = BUST[i - 1][3] if i else b[3]
            p = ease(seg(t, b[0], b[0] + 0.35))
            vis = lerp(1.0 if prev_vis else 0.0, 1.0 if b[3] else 0.0, p)
    return cur, vis


def draw_bust(ctx, t):
    (t0, expr, look, _), vis = bust_state(t)
    if vis <= 0.01:
        return
    R = 128
    x = 215
    y = 1660 + (1 - vis) * 520 + math.sin(t * 2.2) * 5
    # small bounce when the expression changes
    since = t - t0
    sc = 1 + 0.08 * math.exp(-since * 9) * math.sin(since * 30) if since < 0.6 else 1.0
    blink_phase = (t + 0.7) % 3.4
    blink = 1.0 if blink_phase < 0.12 else 0.0
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    glow(ctx, 0, 60, 330, "#000000", 0.6)
    hero.bust(ctx, 0, 0, R, expr, look, blink, rim="#9fd3ff", t=t)
    ctx.restore()


def subtitle_chunks(lang):
    """Split each voice line into short chunks with estimated timing."""
    out = []
    for i, (st, en, ru) in enumerate(LINES):
        s = en if lang == "en" else ru
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else BLACK_T
        dur = min(est_dur(s, lang), nxt - st - 0.15)
        words = s.split()
        chunks, cur = [], []
        for w in words:
            if cur and len(" ".join(cur + [w])) > 24:
                chunks.append(" ".join(cur))
                cur = []
            cur.append(w)
            if w[-1] in ".,:?!»”" and len(" ".join(cur)) > 6:
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        # merge tiny tails
        merged = []
        for c in chunks:
            if merged and len(c) < 8 and len(merged[-1]) + len(c) < 28:
                merged[-1] += " " + c
            else:
                merged.append(c)
        total = sum(len(c) for c in merged)
        tt = st
        for c in merged:
            d = dur * len(c) / total
            out.append((tt, tt + d, c))
            tt += d
    return out


def est_dur(s, lang):
    words = len(s.split())
    letters = sum(ch.isalpha() for ch in s)
    if lang == "en":
        return max(1.0, words / 2.6 + 0.3)
    return max(1.0, letters / 14.5 + 0.3)


def draw_subtitle(ctx, t, chunks):
    for a, b, s in chunks:
        if a <= t < b:
            k = pop(t, a, 0.18)
            ctx.save()
            ctx.translate(540, 1430)
            ctx.scale(0.9 + 0.1 * k, 0.9 + 0.1 * k)
            text(ctx, s.upper(), 0, 0, 64, "#ffffff", outline=8, fit=960)
            ctx.restore()
            return


def draw_overlays(ctx, t, L, chunks):
    # hook title
    if t < 6.6:
        a = 1 - seg(t, 6.0, 6.6)
        s1, s2 = pop(t, 0.15), pop(t, 0.45)
        text(ctx, L["ep"], 540, 250, 44, "#c9d2e6", FONT_BOLD, outline=4, a=a * seg(t, 0.1, 0.4))
        if s1:
            ctx.save(); ctx.translate(540, 400); ctx.scale(s1, s1)
            text(ctx, L["t1"], 0, 0, 150, "#ffffff", outline=10, a=a, fit=1000)
            ctx.restore()
        if s2:
            ctx.save(); ctx.translate(540, 540); ctx.scale(s2, s2)
            text(ctx, L["t2"], 0, 0, 132, "#ffd23f", outline=10, a=a, fit=1000)
            ctx.restore()
        sticker(ctx, L["hook"], 560, 680, 58, angle=-5, s_scale=pop(t, 1.0), a=a)
    # time chip: frozen 09:17, then the countdown
    if 0.8 < t < Q_T:
        if t < TIMER_T:
            s = "09:17"
            bg = "#1d2a44" if t < 62.5 else "#c8161d"
        else:
            rem = max(0, 600 - (t - TIMER_T))
            s = "%02d:%02d" % (rem // 60, rem % 60)
            bg = "#c8161d"
        sc = pop(t, 0.8) if t < 2 else (pop(t, TIMER_T) if TIMER_T <= t < TIMER_T + 1 else 1.0)
        y = 120 if t > 6.6 else 120
        time_chip(ctx, s, 540, y, 54, bg=bg, s_scale=sc)
    draw_bust(ctx, t)
    draw_subtitle(ctx, t, chunks)


def shot_at(t):
    for i, (a, b, fn) in enumerate(SHOTS):
        if a <= t < b:
            return i
    return None


def render_frame(ctx, t, lang, chunks):
    L = TEXT[lang]
    fill_rect(ctx, 0, 0, W, H, "#000000")
    if t >= BLACK_T:
        return
    i = shot_at(t)
    a, b, fn = SHOTS[i]
    fn(ctx, t, t - a, L)
    # short crossfade from the previous shot (skip on hard cuts into surprises)
    xf = 0.22
    if i > 0 and t - a < xf and fn not in (shot_question,):
        pa, pb, pfn = SHOTS[i - 1]
        ctx.push_group()
        pfn(ctx, t, t - pa, L)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - (t - a) / xf)
    draw_overlays(ctx, t, L, chunks)
