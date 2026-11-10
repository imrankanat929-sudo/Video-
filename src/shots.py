"""Shot list synced to the voice-over (times in seconds)."""
import math
import random
import cairo
from core import *
from person import draw_person, draw_head, BOY, MOM, DAD, expr, expr_blend, HEAD_Y
import phone as ph
from world import *

BLUE_NIGHT = hexc('#0f1424')


def pov_bg(ctx, t, kind='bedroom'):
    if kind == 'bedroom':
        vgrad(ctx, 0, 0, W, H, [(0, hexc('#141a2c'), 1), (1, hexc('#0a0d16'), 1)])
        bokeh(ctx, t, 2, hexc('#4a6aa8'), 10, 0.10)
    elif kind == 'street':
        vgrad(ctx, 0, 0, W, H, [(0, hexc('#5a616b'), 1), (1, hexc('#2c2f34'), 1)])
        bokeh(ctx, t, 7, hexc('#c0c8d0'), 12, 0.10)
    elif kind == 'street_dark':
        vgrad(ctx, 0, 0, W, H, [(0, hexc('#22262e'), 1), (1, hexc('#0c0e12'), 1)])
        bokeh(ctx, t, 8, hexc('#d0a060'), 10, 0.08)
    else:
        setc(ctx, (0, 0, 0)); ctx.paint()


def pov_phone(ctx, t, t0, screen, kind='bedroom', zoom0=1.0, zoom1=1.08, dur=3.0, shk=6, lit=1.0, vib=0.0,
              y=900, scale=0.9, fy=H / 2 + 60):
    pov_bg(ctx, t, kind)
    z = lerp(zoom0, zoom1, ease_io(prog(t, t0, t0 + dur)))
    dx, dy = shake(t, shk, 0.8, 3)
    vx = math.sin(t * 95) * 10 * vib
    ctx.save()
    camera(ctx, z, W / 2, fy)
    ph.phone_body(ctx, W / 2 + dx + vx, y + dy, scale, screen, lit=lit, rot=math.radians(-2 + dx * 0.1))
    ctx.restore()
    # screen light spill
    glow(ctx, W / 2, y, 900, hexc('#5a7ab8'), 0.06 * lit)


# ---------------------------------------------------------------- scene 1
def s_bed_wide(ctx, t):
    ctx.save()
    z = lerp(1.0, 1.32, ease_io(prog(t, 0, 5.5)))
    camera(ctx, z, lerp(540, 380, ease_io(prog(t, 0, 5.5))), lerp(960, 1180, ease_io(prog(t, 0, 5.5))))
    pg = 0.0
    for nt in (3.2, 4.1, 4.6, 5.0):
        pg = max(pg, 1 - prog(t, nt, nt + 0.5))
    bedroom(ctx, t, phone_glow=pg)
    ctx.restore()
    # hook title
    a = prog(t, 0.15, 0.5) * (1 - prog(t, 4.6, 5.2))
    if a > 0:
        fl = 1.0 if (int(t * 24) % 17) else 0.4
        k = back_out(prog(t, 0.15, 0.6))
        ctx.save(); ctx.translate(W / 2, 330); ctx.scale(lerp(0.85, 1, k), lerp(0.85, 1, k))
        fit_text(ctx, "А ЧТО, ЕСЛИ", 0, -110, 84, 960, c=(1, 1, 1), a=a * fl, weight="black", outline=12, oa=0.8)
        fit_text(ctx, "ВСЕ ЛЮДИ", 0, 0, 112, 960, c=(1, 1, 1), a=a * fl, weight="black", outline=14, oa=0.8)
        k2 = back_out(prog(t, 0.7, 1.1))
        if k2 > 0:
            ctx.save(); ctx.scale(lerp(1.6, 1, k2), lerp(1.6, 1, k2))
            fit_text(ctx, "ЗАБЫЛИ ТЕБЯ?", 0, 125, 120, 960, c=hexc('#ff3b3b'), a= a * clamp(k2 * 2) * fl, weight="black", outline=14,
                 oa=0.8)
            ctx.restore()
        ctx.restore()


def s_face_wake(ctx, t):
    # top-down close-up of the face on the pillow
    ctx.save()
    z = lerp(1.0, 1.12, prog(t, 5.4, 8.0))
    camera(ctx, z, 540, 900)
    vgrad(ctx, -200, -200, W + 400, H + 400, [(0, hexc('#363d52'), 1), (1, hexc('#2a3044'), 1)])
    ellipse(ctx, 540, 820, 560, 380); setc(ctx, hexc('#4a5270')); ctx.fill()  # pillow
    for i in range(3):
        ctx.move_to(100 + i * 60, 700 + i * 80); ctx.curve_to(300, 650, 700, 640, 980 - i * 40, 720 + i * 70)
        setc(ctx, hexc('#424a66')); ctx.set_line_width(6); ctx.stroke()
    # blanket
    ctx.move_to(-200, 1400); ctx.curve_to(200, 1300, 800, 1320, 1300, 1380); ctx.line_to(1300, 2200); ctx.line_to(-200, 2200)
    ctx.close_path(); setc(ctx, hexc('#2c4258')); ctx.fill()
    ctx.save(); ctx.translate(540, 900); ctx.scale(3.0, 3.0)
    ctx.rectangle(-16, 70, 32, 70); setc(ctx, shade(BOY['skin'], 0.85)); ctx.fill()
    op = prog(t, 5.9, 6.25)
    bl = 1 - op
    bl = max(bl, auto_blink(t - 6.75, 0, 100))
    look = (0, 0)
    if t > 7.0:
        look = (ease_io(prog(t, 7.0, 7.3)) * 1.4, 0)
    e = expr_blend('calm', 'confused', prog(t, 7.2, 7.6))
    draw_head(ctx, BOY, dict(blink=bl, look=look, t=t, sweat=False), e)
    ctx.restore()
    ctx.rectangle(-200, 1330, W + 400, 2000); ctx.new_path()
    ctx.move_to(-200, 1400); ctx.curve_to(200, 1300, 800, 1320, 1300, 1380); ctx.line_to(1300, 2200); ctx.line_to(-200, 2200)
    ctx.close_path(); setc(ctx, hexc('#2c4258')); ctx.fill()
    ctx.restore()
    # phone light flickering from the right
    pulses = sum(max(0, 1 - prog(t, nt, nt + 0.6)) for nt in (5.6, 6.4, 7.0, 7.5))
    glow(ctx, 1150, 900, 800, hexc('#7fa6ff'), 0.25 * clamp(pulses))
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    setc(ctx, hexc('#8890b0')); ctx.paint(); ctx.restore()


def s_sit_phone(ctx, t):
    ctx.save()
    z = lerp(1.0, 1.15, ease_io(prog(t, 8.0, 10.3)))
    camera(ctx, z, 540, 1000)
    # bedroom wall close
    vgrad(ctx, -300, -300, W + 600, H + 600, [(0, hexc('#1c2236'), 1), (1, hexc('#131726'), 1)])
    rrect(ctx, 640, 200, 420, 600, 8); setc(ctx, hexc('#2f3f62')); ctx.fill()
    ctx.rectangle(840, 200, 14, 600); setc(ctx, hexc('#262c40')); ctx.fill()
    ctx.rectangle(-300, 1200, W + 600, 900); setc(ctx, hexc('#59607a')); ctx.fill()
    ellipse(ctx, 320, 1050, 260, 90); setc(ctx, hexc('#7c84a0')); ctx.fill()
    raise_ = ease_io(prog(t, 8.0, 8.8))
    pose = dict(seated=True, t=t, blink=auto_blink(t, 2), look=(0.2, 1.1), nod=8,
                arms=dict(r=(lerp(5, 15, raise_), lerp(5, -146, raise_)), l=(lerp(5, 12, raise_), lerp(5, -120, raise_))),
                phone=raise_ > 0.5, phone_hand='r', phone_lit=1.0, turn=0.08,
                expr=expr_blend('confused', 'puzzled', prog(t, 9.0, 9.6)))
    draw_person(ctx, BOY, pose, 540, 1720, 1.35)
    # blanket over legs
    ctx.move_to(-300, 1380); ctx.curve_to(200, 1300, 700, 1340, 1400, 1300); ctx.line_to(1400, 2200); ctx.line_to(-300, 2200)
    ctx.close_path(); setc(ctx, hexc('#2c4258')); ctx.fill()
    if raise_ > 0.5:
        glow(ctx, 600, 1050, 520, hexc('#7fa6ff'), 0.35)
        glow(ctx, 560, 900, 300, hexc('#7fa6ff'), 0.12)
    ctx.restore()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); setc(ctx, hexc('#9aa2c0')); ctx.paint(); ctx.restore()


NOTIFS = [(10.35, "+7 900 000-41-61", "Ты кто?"), (10.85, "Аня К.", "Откуда у тебя мой номер?"),
          (11.35, "Неизвестный", "Мы тебя не знаем."), (11.8, "Марк", "Кто это??"),
          (12.2, "+7 900 000-11-18", "Ошиблись номером. Не пиши."), (12.55, "10 «Б»", "Кто добавил этого человека?"),
          (12.85, "Неизвестный", "Ты кто?"), (13.1, "София", "Мы знакомы?"), (13.35, "+7 900 000-87-20", "кто ты"),
          (13.55, "Лёва", "???"), (13.75, "Неизвестный", "КТО ТЫ?"), (13.95, "Бабушка", "Кто это, внучек?")]


def s_notifs(ctx, t):
    pov_phone(ctx, t, 10.3, lambda c: ph.lock_notifs(c, t, NOTIFS, 0, 70, 10.3), 'bedroom', 1.0, 1.1, 4.0)


def s_face_who(ctx, t):
    # close-up face lit by the phone, camera slowly pushes in
    vgrad(ctx, 0, 0, W, H, [(0, hexc('#161b2c'), 1), (1, hexc('#0b0e18'), 1)])
    bokeh(ctx, t, 4, hexc('#4a6aa8'), 8, 0.08)
    ctx.save()
    z = lerp(1.0, 1.45, ease_io(prog(t, 14.3, 17.6)))
    camera(ctx, z, 540, 860)
    ctx.translate(540, 900); ctx.scale(3.2, 3.2)
    rrect(ctx, -170, 110, 340, 300, 90); setc(ctx, BOY['top']); ctx.fill()
    ctx.rectangle(-16, 60, 32, 60); setc(ctx, shade(BOY['skin'], 0.85)); ctx.fill()
    e = 'puzzled'
    if t > 15.4:
        e = expr_blend('puzzled', 'smile', prog(t, 15.4, 16.0) * 0.6)
    if t > 16.8:
        e = expr_blend(expr_blend('puzzled', 'smile', 0.6), 'calm', prog(t, 16.8, 17.4))
    draw_head(ctx, BOY, dict(look=(0.1, 1.0), blink=auto_blink(t, 0.4), t=t, turn=0.05), e)
    ctx.restore()
    glow(ctx, 540, 1350, 900, hexc('#7fa6ff'), 0.22)
    # message echo
    a = prog(t, 14.36, 14.5) * (1 - prog(t, 15.2, 15.5))
    if a > 0:
        k = back_out(prog(t, 14.36, 14.6))
        ctx.save(); ctx.translate(W / 2, 330); ctx.scale(k, k)
        rrect(ctx, -300, -80, 600, 130, 50); setc(ctx, hexc('#2a2d35'), 0.92 * a); ctx.fill()
        text(ctx, "Ты кто?", 0, 8, 64, (1, 1, 1), a)
        ctx.restore()


# ---------------------------------------------------------------- scene 2
def s_hallway(ctx, t):
    u = prog(t, 17.6, 21.1)
    bx = lerp(250, 1350, u)
    ctx.save()
    camera(ctx, 1.05, bx + 120, 1060)
    hallway(ctx, t)
    pose = dict(facing='side', dir=1, phase=bx / 70, amp=1.0, t=t, blink=auto_blink(t, 2), expr='calm',
                look=(0.5, 0.3))
    draw_person(ctx, BOY, pose, bx, 1640, 1.0)
    ctx.restore()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); setc(ctx, hexc('#c8bcb0')); ctx.paint(); ctx.restore()


def kitchen_cam(ctx, t, z, cx, cy, shk=0.0):
    ctx.save()
    camera(ctx, z, cx, cy, shk=shake(t, shk, 3, 9))
    kitchen_world(ctx, t)
    ctx.restore()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); setc(ctx, hexc('#e6dccc')); ctx.paint(); ctx.restore()


def s_kitchen_wide(ctx, t):
    kitchen_cam(ctx, t, lerp(1.0, 1.06, prog(t, 21.1, 24.4)), 560, 1060)


def s_parents_close(ctx, t):
    kitchen_cam(ctx, t, lerp(1.85, 2.05, ease_io(prog(t, 24.4, 27.2))), 760, 1110)


def s_boy_mid(ctx, t):
    kitchen_cam(ctx, t, lerp(1.8, 2.0, ease_io(prog(t, 27.2, 30.0))), 260, 1180)


def s_dad_close(ctx, t):
    kitchen_cam(ctx, t, lerp(2.5, 2.75, ease_io(prog(t, 30.0, 33.7))), 860, 1060)


def s_boy_freeze(ctx, t):
    z = lerp(2.2, 3.2, ease_out(prog(t, 33.7, 34.0)))
    kitchen_cam(ctx, t, z, 262, 1180, shk=2)


def s_kitchen_chaos(ctx, t):
    z = lerp(1.25, 1.12, ease_io(prog(t, 35.0, 39.6)))
    kitchen_cam(ctx, t, z, 560, 1180, shk=lerp(2, 8, prog(t, 36, 39)))


# ---------------------------------------------------------------- street
def boy_run_x(t):
    return kf(t, [(39.6, 150), (44.6, 2600)], fn=lambda u: u)


def s_street_run(ctx, t):
    bx = boy_run_x(t)
    cx = bx + 200
    ctx.save()
    camera(ctx, 1.0, cx, 1080, shk=shake(t, 6, 3, 5))
    pose = dict(facing='side', dir=1, phase=t * 13, amp=1.0, run=1.0, t=t, expr='scared', look=(0.5, 0))
    street_world(ctx, t, cx, boy=(bx, 1680, 0.85, pose))
    ctx.restore()
    street_grade(ctx, 0.0)


def street_grade(ctx, dark):
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    setc(ctx, mix(hexc('#c4c8d0'), hexc('#7a8090'), dark)); ctx.paint(); ctx.restore()


def s_call_dial(ctx, t):
    pov_phone(ctx, t, 44.6, lambda c: ph.call_screen(c, t, "Макс", "вызов…" if t < 45.9 else "соединено", 'М'),
              'street', 1.0, 1.06, 1.6)


STREET_X = 2600


def boy_call_pose(t):
    e = 'smile'
    if t > 46.2:
        e = expr_blend('smile', 'talk', 0.5)
    if t > 48.4:
        e = expr_blend('smile', 'worried', prog(t, 48.4, 49.2))
    if t > 50.9:
        e = expr_blend('worried', 'shock', prog(t, 50.9, 51.3))
    if t > 52.6:
        e = expr_blend('shock', 'sad', prog(t, 52.6, 53.4))
    pose = dict(facing='front', t=t, blink=auto_blink(t, 1.2), turn=-0.18, look=(-0.2, 0.1),
                arms=dict(r=(125, 97), l=(4, 6)), phone=True, phone_hand='r', phone_lit=0.3, expr=e, phone_rot=0.35,
                arms_over=True)
    if 46.3 < t < 48.3:
        pose['talk'] = talk(t, True, 3)
    if t > 52.8:
        pose['tear'] = prog(t, 52.8, 54.0)
        pose['look'] = (0.2, 0.8)
    return pose


def s_call_street(ctx, t):
    ctx.save()
    z = lerp(1.6, 1.85, ease_io(prog(t, 46.2, 50.6)))
    camera(ctx, z, STREET_X, 1250)
    street_world(ctx, t, STREET_X, boy=(STREET_X, 1700, 0.9, boy_call_pose(t)), front=False)
    ctx.restore()
    street_grade(ctx, 0.1)


def s_call_close(ctx, t):
    ctx.save()
    z = lerp(3.0, 3.4, ease_io(prog(t, 50.6, 53.7)))
    camera(ctx, z, STREET_X + 10, 1180)
    street_world(ctx, t, STREET_X, boy=(STREET_X, 1700, 0.9, boy_call_pose(t)), front=False)
    ctx.restore()
    street_grade(ctx, 0.25)


def s_call_end(ctx, t):
    pov_phone(ctx, t, 53.7, lambda c: ph.call_screen(c, t, "Макс", "Вызов завершён", 'М', ended=1.0), 'street', 1.04, 1.08,
              0.6)


# ---------------------------------------------------------------- album
def s_album(ctx, t):
    van = [prog(t, 57.8 + i * 0.75, 58.6 + i * 0.75) for i in range(4)]
    ctx.save()
    z = kf(t, [(54.3, 1.0), (57.6, 1.08), (60.6, 1.18), (62.4, 1.9)])
    cx = kf(t, [(54.3, 540), (60.6, 540), (62.4, 330)])
    cy = kf(t, [(54.3, 960), (60.6, 930), (62.4, 560)])
    camera(ctx, z, cx, cy)
    album(ctx, t, 54.7, van)
    ctx.restore()
    vig = prog(t, 58, 62)
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); setc(ctx, mix(hexc('#ffffff'), hexc('#9aa0b0'), vig)); ctx.paint()
    ctx.restore()


# ---------------------------------------------------------------- phone wipe
def s_chats_vanish(ctx, t):
    pov_phone(ctx, t, 62.4, lambda c: ph.chats_list(c, t, 62.55, 0.2), 'street', 1.0, 1.05, 2.0)


def s_gallery_vanish(ctx, t):
    pov_phone(ctx, t, 64.4, lambda c: ph.gallery(c, t, 64.45, 0.085), 'street', 1.05, 1.1, 2.0)


def s_contacts(ctx, t):
    pov_phone(ctx, t, 66.4, lambda c: ph.contacts(c, t, 67.4), 'street', 1.0, 1.15, 3.6)


def s_alone(ctx, t):
    ctx.save()
    z = lerp(1.55, 0.95, ease_io(prog(t, 70.0, 73.0)))
    cx = STREET_X + 400
    camera(ctx, z, cx, 1200)
    alpha = 0.78 + 0.12 * math.sin(t * 9) * (int(t * 7) % 3 == 0)
    pose = dict(facing='front', t=t, blink=auto_blink(t), expr='sad', look=(0, 0.6), turn=0.0)
    gx = kf(t, [(70.0, cx + 900), (73.0, cx - 900)], fn=lambda u: u)
    street_world(ctx, t, cx, boy=(cx, 1700, 0.85, pose), boy_alpha=alpha, desat=0.6, dark=0.15,
                 ghost_pass=(2, gx, -1))
    ctx.restore()
    street_grade(ctx, 0.3)


# ---------------------------------------------------------------- unknown number
def s_vibrate(ctx, t):
    ctx.save()
    z = lerp(2.0, 2.3, ease_io(prog(t, 73.0, 75.0)))
    cx = STREET_X + 400
    camera(ctx, z, cx, 1300)
    vib = 1.0 if t > 73.1 else 0
    pose = dict(facing='front', t=t, blink=auto_blink(t), look=(0.1, 1.2), nod=6, turn=0.05,
                arms=dict(r=(15, -146), l=(4, 6)), phone=True, phone_hand='r', phone_lit=0.9,
                phone_rot=math.sin(t * 80) * 0.08 * vib, expr=expr_blend('sad', 'surprised', prog(t, 73.1, 73.4)))
    street_world(ctx, t, cx, boy=(cx, 1700, 0.85, pose), desat=0.6, dark=0.3, front=False)
    glow(ctx, cx + 30, 1330, 250, hexc('#7fa6ff'), 0.3)
    ctx.restore()
    street_grade(ctx, 0.4)


def s_unknown_notif(ctx, t):
    pov_phone(ctx, t, 75.0, lambda c: ph.lock_notifs(c, t, [(75.2, "Неизвестный номер", "1 новое сообщение")]),
              'street_dark', 1.0, 1.1, 2.3, vib=1.0 if t < 75.9 else 0.0)


def unknown_chat(c, t, msgs, glitch=0.0):
    ph.chat(c, t, "Неизвестный номер", msgs, sub="был(а) в сети: никогда", avatar_c=hexc('#3a3a42'), letter="?", size=40)


MSG1 = (77.0, "Наконец-то они тебя забыли.", 'in', dict(typing_until=77.42, size=50, color=hexc('#3a1f24')))
MSG2 = (81.4, "Теперь осталось забыть себя.", 'in',
        dict(typing_until=84.86, size=50, color=hexc('#3a1f24')))


def s_msg1(ctx, t):
    pov_phone(ctx, t, 77.0, lambda c: unknown_chat(c, t, [MSG1]), 'street_dark', 1.0, 1.25, 3.0, fy=640)


def s_eyes(ctx, t):
    vgrad(ctx, 0, 0, W, H, [(0, hexc('#14161c'), 1), (1, hexc('#08090c'), 1)])
    ctx.save()
    z = lerp(1.0, 1.18, prog(t, 80.0, 81.4))
    camera(ctx, z, 540, 960, shk=shake(t, 3, 4, 2))
    ctx.translate(540, 1150); ctx.scale(6.5, 6.5)
    draw_head(ctx, BOY, dict(look=(0, 0.3), t=t, blink=0, sweat=True), expr_blend('scared', 'shock', 0.75))
    ctx.restore()
    glow(ctx, 540, 1900, 1100, hexc('#7fa6ff'), 0.25)


def s_msg2(ctx, t):
    pov_phone(ctx, t, 81.3, lambda c: unknown_chat(c, t, [MSG1, MSG2]), 'street_dark', 1.05, 1.3, 6.0, fy=700)
    if 84.86 < t < 85.3:
        glitch_bars(ctx, t, 0.8)


def glitch_bars(ctx, t, a):
    rnd = random.Random(int(t * 40))
    for i in range(8):
        y = rnd.uniform(0, H); h = rnd.uniform(6, 50)
        ctx.rectangle(0, y, W, h)
        setc(ctx, rnd.choice([hexc('#ff2b4a'), hexc('#2bd4ff'), (1, 1, 1)]), a * rnd.uniform(0.1, 0.35)); ctx.fill()


# ---------------------------------------------------------------- front camera
def s_raise_phone(ctx, t):
    ctx.save()
    z = lerp(1.9, 2.1, ease_io(prog(t, 87.5, 89.6)))
    cx = STREET_X + 400
    camera(ctx, z, cx, 1250)
    u = ease_io(prog(t, 87.7, 89.4))
    pose = dict(facing='front', t=t, blink=auto_blink(t), look=lerp((0.1, 1.2), (0.1, 0.2), u), nod=lerp(6, 0, u),
                arms=dict(r=(lerp(15, 40, u), lerp(-146, -175, u)), l=(4, 6)), phone=True, phone_hand='r',
                phone_lit=0.9, expr='worried', turn=0.05)
    street_world(ctx, t, cx, boy=(cx, 1700, 0.85, pose), desat=0.7, dark=0.45, front=False)
    ctx.restore()
    street_grade(ctx, 0.5)


def s_camera_open(ctx, t):
    fl = 1 - prog(t, 89.6, 90.1)
    pov_phone(ctx, t, 89.6, lambda c: ph.face_cam(c, t, 'worried', 1.5, look=(0, 0), blink=auto_blink(t, 1)),
              'street_dark', 1.0, 1.08, 1.8)
    if fl > 0:
        ctx.rectangle(0, 0, W, H); setc(ctx, (1, 1, 1), 0.5 * fl); ctx.fill()


def s_step_back(ctx, t):
    ctx.save()
    u = ease_out(prog(t, 91.6, 92.3))
    z = lerp(2.2, 1.85, u)
    cx = STREET_X + 400
    camera(ctx, z, cx, 1250, shk=shake(t, 5 * u, 5, 4))
    e = expr_blend('worried', 'shock', prog(t, 91.5, 91.8))
    if t > 93.3:
        e = expr_blend('shock', 'scared', prog(t, 93.3, 94.0))
    pose = dict(facing='front', t=t, blink=0, look=(0, 0.1), arms=dict(r=(lerp(40, 25, u), lerp(-175, -150, u)), l=(lerp(4, 25, u), lerp(6, 35, u))),
                phone=True, phone_hand='r', phone_lit=0.9, expr=e, lean=-6 * u, dy=lerp(0, -10, u), turn=0.0)
    street_world(ctx, t, cx, boy=(cx, lerp(1700, 1640, u), lerp(0.85, 0.8, u), pose), desat=0.7, dark=0.5, front=False)
    ctx.restore()
    street_grade(ctx, 0.55)


def s_reflection1(ctx, t):
    sm = ease_io(prog(t, 95.2, 96.8))
    e = expr_blend('scared', 'creepy', sm)
    pov_phone(ctx, t, 95.0, lambda c: ph.face_cam(c, t, e, 0.0, look=(0, 0), blink=0, zoom=lerp(1.0, 1.12, prog(t, 95, 97.6))),
              'street_dark', 1.05, 1.18, 2.6, shk=3)


def s_real_face(ctx, t):
    vgrad(ctx, 0, 0, W, H, [(0, hexc('#20242c'), 1), (1, hexc('#0b0c10'), 1)])
    bokeh(ctx, t, 8, hexc('#d0a060'), 8, 0.07)
    ctx.save()
    dx, dy = shake(t, 4, 9, 1)
    z = lerp(1.0, 1.1, prog(t, 97.6, 99.3))
    camera(ctx, z, 540 + dx, 900 + dy)
    ctx.translate(540, 950); ctx.scale(3.4, 3.4)
    rrect(ctx, -170, 110, 340, 300, 90); setc(ctx, BOY['top']); ctx.fill()
    ctx.rectangle(-16, 60, 32, 60); setc(ctx, shade(BOY['skin'], 0.85)); ctx.fill()
    draw_head(ctx, BOY, dict(look=(0, 0.2), t=t, blink=0, sweat=True, tear=prog(t, 98.2, 99.3)), 'scared')
    ctx.restore()
    glow(ctx, 540, 1700, 900, hexc('#7fa6ff'), 0.28)


def s_reflection2(ctx, t):
    z = lerp(1.15, 1.5, ease_io(prog(t, 99.3, 101.5)))
    pov_phone(ctx, t, 99.3, lambda c: ph.face_cam(c, t, expr_blend('creepy', 'grin', 0.25), 0.0, look=(0, 0), blink=0,
                                                   tilt=lerp(0, 9, prog(t, 99.3, 101.5)), zoom=z),
              'street_dark', 1.18, 1.45, 2.2, shk=2)
    if int(t * 12) % 7 == 0:
        glitch_bars(ctx, t, 0.6)


# ---------------------------------------------------------------- screen off / final message
def s_screen_off(ctx, t):
    lit = 1 - prog(t, 101.54, 101.7)
    pov_phone(ctx, t, 101.5, lambda c: ph.face_cam(c, t, 'creepy', 0, blink=0, zoom=1.5), 'street_dark', 1.45, 1.45,
              1.0, lit=lit, shk=1)
    if 101.54 < t < 101.75:
        # CRT-off line
        k = prog(t, 101.54, 101.75)
        ctx.rectangle(0, H / 2 - 4, W * (1 - k), 8); setc(ctx, (1, 1, 1), 0.8 * (1 - k)); ctx.fill()


def black_screen(c, t):
    setc(c, hexc('#030304')); c.paint()


def s_power_on(ctx, t):
    on = prog(t, 104.5, 104.9)

    def scr(c):
        if t < 105.3:
            setc(c, (0, 0, 0)); c.paint()
            if t > 104.5:
                glow(c, ph.SW / 2, ph.SH / 2, 300, (1, 1, 1), 0.5 * (1 - prog(t, 104.9, 105.3)))
                c.arc(ph.SW / 2, ph.SH / 2, 40, 0, 6.3); setc(c, (1, 1, 1), 0.8 * (1 - prog(t, 104.9, 105.3))); c.fill()
        else:
            unknown_chat(c, t, [MSG1, MSG2, (105.6, "", 'in', dict(typing_until=110, size=50, color=hexc('#3a1f24')))])
    pov_phone(ctx, t, 102.8, scr, 'street_dark', 1.0, 1.1, 5.0, fy=760, lit=max(on, 0.0001) if t < 104.5 else 1.0)
    if t < 104.5:
        # dark reflection of the boy in the black screen
        ctx.save()
        ctx.translate(W / 2, 760); ctx.scale(2.2, 2.2)
        ctx.push_group()
        draw_head(ctx, BOY, dict(t=t, blink=0, look=(0, 0)), 'scared')
        ctx.pop_group_to_source(); ctx.paint_with_alpha(0.07)
        ctx.restore()


MSG3 = (107.5, "Завтра ты забудешь, что когда-то существовал.", 'in',
        dict(typing_until=107.94, size=50, color=hexc('#5a1820')))


def s_final_msg(ctx, t):
    lit = 1 - 0.85 * ease_in(prog(t, 109.0, 111.35))
    pov_phone(ctx, t, 107.9, lambda c: unknown_chat(c, t, [MSG1, MSG2, MSG3]), 'street_dark', 1.1, 1.45, 3.5, fy=800,
              lit=lit, shk=lerp(2, 6, prog(t, 108, 111)))
    k = prog(t, 107.94, 108.15)
    if 107.94 < t < 108.4:
        ctx.rectangle(0, 0, W, H); setc(ctx, hexc('#ff2030'), 0.18 * (1 - prog(t, 108.0, 108.4))); ctx.fill()
    ctx.rectangle(0, 0, W, H); setc(ctx, (0, 0, 0), 0.6 * ease_in(prog(t, 109.0, 111.35))); ctx.fill()


def s_end(ctx, t):
    setc(ctx, (0, 0, 0)); ctx.paint()
    lines = [("А ТЫ СМОГ БЫ", 111.6, (1, 1, 1)), ("ЖИТЬ, ЕСЛИ БЫ", 112.3, (1, 1, 1)),
             ("ВСЕ ТЕБЯ ЗАБЫЛИ?", 113.0, hexc('#ff3b3b'))]
    for i, (s, ta, c) in enumerate(lines):
        a = prog(t, ta, ta + 0.5)
        if a <= 0:
            continue
        fl = 1.0 if int(t * 30 + i * 7) % 23 else 0.55
        y = 640 + i * 130 + (1 - ease_out(a)) * 30
        fit_text(ctx, s, W / 2, y, 112 if i < 2 else 124, 980, c=c, a=a * fl, weight="black")
    if t > 120.0:
        a = prog(t, 120.0, 120.5)
        k = back_out(prog(t, 120.0, 120.45))
        ctx.save(); ctx.translate(W / 2, 1120); ctx.scale(k, k)
        rrect(ctx, -440, -70, 880, 130, 65); setc(ctx, (1, 1, 1), a); ctx.fill()
        # speech bubble icon
        rrect(ctx, -400, -40, 70, 54, 16); setc(ctx, (0, 0, 0), a); ctx.fill()
        ctx.move_to(-385, 10); ctx.line_to(-395, 34); ctx.line_to(-365, 12); ctx.close_path(); ctx.fill()
        fit_text(ctx, "ПИШИ В КОММЕНТАРИЯХ", 40, 17, 52, 700, c=(0, 0, 0), a=a, weight="black")
        ctx.restore()
        # bouncing arrow
        by = 1240 + abs(math.sin(t * 5)) * 30
        ctx.move_to(W / 2 - 40, by); ctx.line_to(W / 2 + 40, by); ctx.line_to(W / 2, by + 50); ctx.close_path()
        setc(ctx, (1, 1, 1), a); ctx.fill()


SHOTS = [
    (0.0, 5.4, s_bed_wide), (5.4, 8.0, s_face_wake), (8.0, 10.3, s_sit_phone), (10.3, 14.3, s_notifs),
    (14.3, 17.6, s_face_who),
    (17.6, 21.1, s_hallway), (21.1, 24.4, s_kitchen_wide), (24.4, 27.2, s_parents_close), (27.2, 30.0, s_boy_mid),
    (30.0, 33.7, s_dad_close), (33.7, 35.0, s_boy_freeze), (35.0, 39.6, s_kitchen_chaos),
    (39.6, 44.6, s_street_run), (44.6, 46.2, s_call_dial), (46.2, 50.6, s_call_street), (50.6, 53.7, s_call_close),
    (53.7, 54.3, s_call_end),
    (54.3, 62.4, s_album), (62.4, 64.4, s_chats_vanish), (64.4, 66.4, s_gallery_vanish), (66.4, 70.0, s_contacts),
    (70.0, 73.0, s_alone),
    (73.0, 75.0, s_vibrate), (75.0, 77.0, s_unknown_notif), (77.0, 80.0, s_msg1), (80.0, 81.3, s_eyes),
    (81.3, 87.5, s_msg2),
    (87.5, 89.6, s_raise_phone), (89.6, 91.4, s_camera_open), (91.4, 95.0, s_step_back),
    (95.0, 97.6, s_reflection1), (97.6, 99.3, s_real_face), (99.3, 101.5, s_reflection2),
    (101.5, 102.8, s_screen_off), (102.8, 107.9, s_power_on), (107.9, 111.4, s_final_msg), (111.4, 999, s_end),
]
# crossfade durations into the given shot (start time -> seconds)
XFADE = {5.4: 0.35, 17.6: 0.3, 21.1: 0.25, 39.6: 0.2, 54.3: 0.45, 70.0: 0.4, 87.5: 0.3}
# dip-to-black / flash markers
FLASH = {10.3: 0.2, 62.4: 0.15, 64.4: 0.15, 66.4: 0.15, 80.0: 0.12, 95.0: 0.2}
