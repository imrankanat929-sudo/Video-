"""Scene-by-scene animation. Every time used here comes from timeline.T."""
import math
import cairo
from gfx import *  # noqa
from timeline import T, W, H, HOOK_IMPACT, FINAL_TEXT, LOGO, SCENES


def cam(ctx, zoom, fx, fy):
    ctx.translate(W / 2, H / 2)
    ctx.scale(zoom, zoom)
    ctx.translate(-fx, -fy)


# ============================================================ 01 HOOK =======
HOOK_WORDS = [("ПОЧЕМУ", "pochemu"), ("МЫ", "my"), ("ТАК", "tak"),
              ("СИЛЬНО", "silno"), ("ХОТИМ", "hotim"), ("ВСЕМ", "vsem"),
              ("НРАВИТЬСЯ?", "nravitsya")]
HOOK_CROWD = [(-700, 0.82), (-480, 0.9), (-265, 0.95), (265, 0.95), (480, 0.9),
              (700, 0.82)]


def s01_hook(ctx, t):
    t_end = T["ty_mozhesh"]
    think = ramp(t, T["podumay"] - 0.1, T["podumay"] + 0.9, e_io)
    zoom = 1.0 + 0.08 * e_io(t / t_end) + 0.30 * think
    ctx.save()
    cam(ctx, zoom, 960, 600 + 40 * think)
    on = ramp(t, 0.0, 0.3)
    ground(ctx, on)
    cone_light(ctx, 960, GY, on * (1 + 0.6 * think))
    snap = e_back((t - HOOK_IMPACT) / 0.22, 2.0) if t > HOOK_IMPACT else 0
    crowd_a = ramp(t, 0.0, 0.3) * 0.42 * (1 - 0.75 * think)
    for i, (dx, sc) in enumerate(HOOK_CROWD):
        side = 1 if dx > 0 else -1
        look = lerp(side * 0.8, -side * 1.0, snap)
        lean = -side * 0.05 * snap
        person(ctx, 960 + dx, GY, sc, crowd_a, look=look, lean=lean, lum=0.6)
    # sight lines snapping onto the main character
    hx, hy = head_pos(960, GY)
    la = (1 - ramp(t, T["podumay"], T["podumay"] + 0.5)) * 0.45
    for i, (dx, sc) in enumerate(HOOK_CROWD):
        side = 1 if dx > 0 else -1
        cx, cy = head_pos(960 + dx, GY, sc, -side)
        k = ramp(t, HOOK_IMPACT + i * 0.03, HOOK_IMPACT + 0.4 + i * 0.03)
        line(ctx, cx, cy, hx + side * 40, hy + 10, k, 2.2, la, dash=[6, 9])
    # main character
    pulse = math.exp(-max(0, t - HOOK_IMPACT) * 4) if t > HOOK_IMPACT else 0
    person(ctx, 960, GY, 1.0, on, look=0, stretch=1 - 0.03 * pulse)
    # approval symbols orbiting
    sym_out = T["podumay"]
    syms = [(T["vsem"], "heart", 760, 470), (T["vsem"] + 0.18, "?", 1160, 440),
            (T["nravitsya"], "check", 1210, 600), (T["nravitsya"] + 0.2, "?", 700, 630),
            (T["nravitsya"] + 0.4, "heart", 1090, 330)]
    for (t0, k, x, y) in syms:
        pop_badge(ctx, t, t0, k, x, y, 30, t_out=sym_out)
    ctx.restore()
    # title (screen space), word-synced
    ta = 1 - ramp(t, T["podumay"] - 0.15, T["podumay"] + 0.35)
    if ta > 0:
        size = 60
        words = [w for w, _ in HOOK_WORDS]
        gap = 22
        widths = [text_width(ctx, w, size, "bold", 2) for w in words]
        widths[-1] += 50  # pill padding for the last word
        total = sum(widths) + gap * (len(words) - 1)
        x = 960 - total / 2
        for (w, key), ww in zip(HOOK_WORDS, widths):
            t0 = T[key] - 0.05
            k = ramp(t, t0, t0 + 0.25)
            if k > 0:
                yy = 175 + 18 * (1 - k)
                if key == "nravitsya":
                    pill(ctx, w, x + ww / 2, yy, ta * k, size=40,
                         pop=e_back((t - t0) / 0.35, 2.6))
                else:
                    text(ctx, w, x + ww / 2, yy, size, ta * k, "bold", 2)
            x += ww + gap


# ======================================================== 02 JUDGMENT =======
J_CROWD = [(1180, 0.9), (1350, 0.95), (1520, 0.9), (1690, 0.85)]
MX = 640


def s02_judgment(ctx, t):
    t0 = T["ty_mozhesh"]
    zoom = 1.04 + 0.05 * e_io((t - t0) / 16)
    ctx.save()
    cam(ctx, zoom, 1000 + 40 * e_io((t - t0) / 16), 560)
    ground(ctx, 1)
    cone_light(ctx, MX, GY, 0.8)

    watch = ramp(t, T["chtoby"], T["chtoby"] + 0.4)
    laugh = ramp(t, T["smeeshsya"], T["smeeshsya"] + 0.2)
    crowd_a = 0.40 + 0.18 * watch * (1 - ramp(t, T["smeeshsya"], T["smeeshsya"] + 1))
    for i, (x, sc) in enumerate(J_CROWD):
        bob = 0
        if laugh > 0 and i != 3:
            bob = abs(math.sin((t - T["smeeshsya"]) * 9 + i)) * 7 * laugh
        lk = lerp(0.3, -1.0, watch) if i else -0.3
        if i == 0:
            lk = lerp(-0.2, -1.0, watch)
        person(ctx, x, GY - bob, sc, crowd_a, look=lk, lum=0.6)

    # --- (a) opinion: triangle vs squares
    a_op = window(t, t0 + 0.2, T["otkazatsya"] - 0.3, 0.3, 0.35)
    morph = ramp(t, T["inache"], T["inache"] + 0.45, e_io)
    hx, hy = head_pos(MX, GY)
    if a_op > 0:
        bubble(ctx, MX + 120, hy - 120, 140, 110, a_op, tail=(-1, 1),
               pop=e_back((t - t0 - 0.2) / 0.4), thought=True)
        shape(ctx, "triangle", MX + 120, hy - 118, 30, a_op, True,
              morph_to="square", k=morph)
        for i, (x, sc) in enumerate(J_CROWD[:3]):
            tt = T["okruzh"] + i * 0.15
            if t > tt:
                cx, cy = head_pos(x, GY, sc)
                p = e_back((t - tt) / 0.35)
                bubble(ctx, x, cy - 105, 96, 80, a_op, tail=(0, 1), pop=p)
                shape(ctx, "square", x, cy - 105, 18, a_op)
    # --- (b) idea bulb + gazes
    lit = ramp(t, T["idei"], T["idei"] + 0.2)
    if T["stranno"] < t < T["stranno"] + 0.5:
        lit *= 0.25 + 0.75 * (math.sin((t - T["stranno"]) * 70) > 0)
    lit *= 1 - ramp(t, T["stranno"] + 0.45, T["stranno"] + 0.55)
    b_a = window(t, T["idei"] - 0.1, T["smeeshsya"] - 0.4, 0.25, 0.4)
    arm = 0.18 + 2.3 * ramp(t, T["idei"] - 0.2, T["idei"] + 0.25, e_back) \
        * (1 - ramp(t, T["stranno"] - 0.1, T["stranno"] + 0.6, e_io))
    bulb(ctx, MX + 70, hy - 130, 1.0, lit, b_a * (0.55 + 0.45 * lit))
    # sight lines while being watched
    gaze_a = 0.4 * watch * (1 - ramp(t, T["smeeshsya"] - 0.3, T["smeeshsya"]))
    gaze_a += 0.22 * ramp(t, T["kotoraya"], T["kotoraya"] + 0.4) * \
        (1 - ramp(t, T["pochemu2"] - 0.3, T["pochemu2"]))
    for i, (x, sc) in enumerate(J_CROWD):
        cx, cy = head_pos(x, GY, sc, -1)
        k = ramp(t, T["chtoby"] + i * 0.06, T["chtoby"] + 0.45 + i * 0.06)
        line(ctx, cx - 25, cy, hx + 30, hy, k, 2, gaze_a, dash=[6, 9])
    # hesitant main character
    shrink = 0.05 * ramp(t, T["inache"], T["inache"] + 0.5) * \
        (1 - ramp(t, T["otkazatsya"], T["otkazatsya"] + 0.5))
    shrink += 0.07 * ramp(t, T["stranno"], T["stranno"] + 0.5) * \
        (1 - ramp(t, T["smeeshsya"], T["smeeshsya"] + 0.6))
    lean = -0.06 * watch * (1 - ramp(t, T["smeeshsya"], T["smeeshsya"] + 0.5))
    look = 0.6 - 0.9 * ramp(t, T["inache"], T["inache"] + 0.4) * \
        (1 - ramp(t, T["otkazatsya"] - 0.2, T["otkazatsya"] + 0.2)) \
        + 0.4 * watch
    fake = ramp(t, T["kotoraya"], T["kotoraya"] + 0.15)
    mbob = abs(math.sin((t - T["kotoraya"]) * 8)) * 4 * fake
    person(ctx, MX, GY - mbob, 1.0, 1.0, look=clamp(look, -1, 1), lean=lean,
           arm_r=arm, stretch=1 - shrink)

    # --- (c) the joke
    ha_a = window(t, T["smeeshsya"], T["pochemu2"] - 0.25, 0.15, 0.25)
    if ha_a > 0:
        for i, (tt, j) in enumerate(((T["smeeshsya"], 1), (T["shutkoy"], 0),
                                     (T["shutkoy"] + 0.2, 2))):
            if t > tt:
                x, sc = J_CROWD[j]
                cx, cy = head_pos(x, GY, sc)
                p = e_back((t - tt) / 0.35)
                bubble(ctx, x + 10, cy - 100 - 20 * (j == 1), 150, 70, ha_a,
                       tail=(-1, 1), pop=p)
                text(ctx, "ХА-ХА", x + 10, cy - 100 - 20 * (j == 1), 28, ha_a,
                     "bold", 2)
        if t > T["kotoraya"]:
            p = e_back((t - T["kotoraya"]) / 0.35)
            fl = 1.0 if t < T["ne_ponr"] else 0.55 + 0.45 * (math.sin(t * 30) > -0.3)
            bubble(ctx, MX + 150, hy - 70, 120, 62, ha_a * fl, tail=(-1, 1), pop=p)
            text(ctx, "ха-ха", MX + 150, hy - 70, 24, ha_a * fl, "bold", 1)
        if t > T["ne_ponr"]:
            # the real, unspoken reaction
            p = e_out((t - T["ne_ponr"]) / 0.4)
            bubble(ctx, MX - 150, hy - 120, 110, 80, ha_a * 0.85, tail=(1, 1),
                   pop=p, thought=True, dashed=True)
            glyph(ctx, "dash", MX - 150, hy - 120, 34, 1.0, ha_a * 0.85)
    ctx.restore()
    pill_seq(ctx, t, [(T["mnenie"], T["otkazatsya"] - 0.3, "МНЕНИЕ"),
                      (T["idei"], T["smeeshsya"] - 0.4, "СОБСТВЕННАЯ ИДЕЯ"),
                      (T["shutkoy"], T["pochemu2"] - 0.25, "ЧУЖАЯ ШУТКА")])


# ============================================================ 03 WHY ========
def s03_why(ctx, t):
    t0 = T["pochemu2"]
    k = e_out((t - t0) / 0.35)
    for i in range(3):
        rk = clamp((t - t0 - i * 0.12) / 1.1)
        if 0 < rk < 1:
            ctx.arc(960, 540, 60 + e_out(rk) * 900, 0, 2 * math.pi)
            white(ctx, (1 - rk) * 0.5)
            ctx.set_line_width(3)
            ctx.stroke()
    sc = 1.35 - 0.35 * k
    ctx.save()
    ctx.translate(960, 540)
    ctx.scale(sc, sc)
    text(ctx, "?", 0, 0, 330, k, "bold")
    ctx.restore()
    person(ctx, 960, 930, 0.38, 0.6 * k)
    ground(ctx, 0.6 * k, 930, 600, 1320)


# ======================================================== 04 SOCIETY ========
NET = [(-560, -160), (-430, -330), (-200, -420), (60, -440), (300, -400),
       (500, -300), (600, -120), (-640, 30), (650, 60)]


def s04_society(ctx, t):
    t0 = T["delo"]
    t_hist = T["istorii"] - 0.5
    t_mod = T["poetomu"] - 0.25
    # ---- (a) network
    a_net = 1 - ramp(t, t_hist, t_hist + 0.45)
    if a_net > 0:
        zoom = 1.25 - 0.22 * e_io((t - t0) / 4.0)
        ctx.save()
        cam(ctx, zoom, 960, 560)
        cx, cy = chest_pos(960, GY)
        ground(ctx, a_net * 0.7)
        nodes = []
        for i, (dx, dy) in enumerate(NET):
            tt = t0 + 0.9 + i * 0.16
            ap = ramp(t, tt, tt + 0.3)
            nx, ny = 960 + dx, GY + dy
            nodes.append((nx, ny, ap))
        conn = ramp(t, T["chastyu"], T["obshestva"] + 0.4, e_io)
        for i, (nx, ny, ap) in enumerate(nodes):
            line(ctx, cx, cy, nx, ny - 65, conn, 2.2, 0.45 * a_net * ap)
            j = (i + 1) % len(nodes)
            if i < len(nodes) - 1:
                mx, my, _ = nodes[j]
                line(ctx, nx, ny - 65, mx, my - 65, conn, 1.6, 0.25 * a_net * ap)
        for (nx, ny, ap) in nodes:
            person(ctx, nx, ny, 0.55, a_net * ap * 0.6, lum=0.6,
                   look=(960 - nx) / 600)
            if conn > 0.95:
                white(ctx, a_net * 0.9)
                ctx.arc(nx, ny - 65, 5, 0, 2 * math.pi)
                ctx.fill()
        person(ctx, 960, GY, 1.0, a_net)
        ctx.restore()
    # ---- (b,c) campfire + safety dome
    a_fire = window(t, t_hist, t_mod, 0.5, 0.45)
    if a_fire > 0:
        zoom = 1.0 + 0.06 * e_io((t - t_hist) / 8)
        ctx.save()
        cam(ctx, zoom, 960, 560)
        ground(ctx, a_fire)
        spotlight(ctx, 960, 740, 460, a_fire * (0.75 + 0.12 * math.sin(t * 9)))
        link = ramp(t, T["drugih"] - 0.2, T["drugih"] + 0.4, e_back)
        tribe = [(-500, 0.8), (-330, 0.85), (-170, 0.95), (170, 0.95), (330, 0.85),
                 (500, 0.8)]
        for i, (dx, sc) in enumerate(tribe):
            tt = t_hist + 0.2 + i * 0.1
            ap = ramp(t, tt, tt + 0.35)
            side = -1 if dx > 0 else 1
            main = (dx == -170)
            person(ctx, 960 + dx, GY, sc, a_fire * ap * (1.0 if main else 0.55),
                   look=side * 0.8, arm_l=0.18 + 1.05 * link, arm_r=0.18 + 1.05 * link,
                   lum=1.0 if main else 0.6)
        flame(ctx, 960, GY - 6, 0.9, t, a_fire)
        # dome of safety
        dome = ramp(t, T["podderzhka"], T["bezopasnosti"] + 0.1, e_io)
        flash = math.exp(-max(0, t - T["bezopasnosti"]) * 3) if t > T["bezopasnosti"] else 0
        if dome > 0:
            ctx.save()
            ctx.translate(960, GY)
            ctx.scale(1, 0.72)
            ang0 = math.pi
            ctx.arc(0, 0, 650, ang0, ang0 + math.pi * dome)
            ctx.restore()
            white(ctx, a_fire * (0.5 + 0.5 * flash))
            ctx.set_line_width(3 + 3 * flash)
            ctx.set_dash([2, 12])
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            ctx.set_dash([])
        # eyes in the dark outside the circle
        eyes = ramp(t, T["podderzhka"] + 0.6, T["podderzhka"] + 1.2) * \
            (1 - 0.7 * ramp(t, T["bezopasnosti"], T["bezopasnosti"] + 0.4))
        for (ex, ey, ph) in ((170, 640, 0.0), (1760, 610, 1.7), (90, 450, 3.1),
                             (1840, 420, 4.4)):
            blink = 0.2 if math.sin(t * 1.7 + ph) > 0.93 else 1.0
            for d in (-11, 11):
                white(ctx, a_fire * eyes * 0.55 * blink)
                ctx.save()
                ctx.translate(ex + d, ey)
                ctx.scale(1, 0.55)
                ctx.arc(0, 0, 5, 0, 2 * math.pi)
                ctx.restore()
                ctx.fill()
        ctx.restore()
    # ---- (d) approval chart (homage to the reference frame)
    a_mod = ramp(t, t_mod, t_mod + 0.5)
    if a_mod > 0:
        zoom = 1.05 - 0.05 * e_io((t - t_mod) / 6)
        ctx.save()
        cam(ctx, zoom, 960, 540)
        ground(ctx, a_mod, x0=-400, x1=2320)
        bx, by, bw, bh = 700, 300, 760, 420
        board(ctx, bx, by, bw, bh, a_mod, ramp(t, t_mod, t_mod + 0.8, e_io))
        ax0, ay0 = bx + 70, by + bh - 60
        line(ctx, ax0, by + 50, ax0, ay0, ramp(t, t_mod + 0.4, t_mod + 0.8), 2.5,
             a_mod * 0.85)
        line(ctx, ax0, ay0, bx + bw - 60, ay0, ramp(t, t_mod + 0.5, t_mod + 0.9),
             2.5, a_mod * 0.85)
        pts = []
        for i in range(60):
            u = i / 59
            pts.append((ax0 + u * (bw - 160), ay0 - (u ** 2.3) * (bh - 140)))
        ck = ramp(t, T["odobrenie"] - 0.2, T["bolshoe"] + 0.2, e_io)
        polyline(ctx, pts, ck, 4, a_mod)
        for j, u in enumerate((0.32, 0.58, 0.82)):
            px = ax0 + u * (bw - 160)
            py = ay0 - (u ** 2.3) * (bh - 140)
            pop_badge(ctx, t, T["odobrenie"] + j * 0.5, "heart", px - 18, py - 40, 22)
        if t > T["bolshoe"]:
            ex, ey = pts[-1]
            fl = ramp(t, T["bolshoe"], T["bolshoe"] + 0.3)
            spotlight(ctx, ex, ey, 110, 4 * fl)
            white(ctx, a_mod * fl)
            ctx.arc(ex, ey, 8, 0, 2 * math.pi)
            ctx.fill()
        point = ramp(t, t_mod + 0.4, t_mod + 0.9, e_back)
        person(ctx, 470, GY, 1.0, a_mod, look=0.7, arm_r=0.18 + 1.75 * point)
        ctx.restore()
    pill_seq(ctx, t, [(T["chastyu"], t_hist, "ЧАСТЬ ОБЩЕСТВА"),
                      (T["istorii"], T["podderzhka"] - 0.1, "ВСЕГДА ВМЕСТЕ"),
                      (T["podderzhka"], t_mod, "БЕЗОПАСНОСТЬ"),
                      (T["odobrenie"], T["kogda"] - 0.3, "СОЦИАЛЬНОЕ ОДОБРЕНИЕ")],
             y=200 if t > t_mod else 165)


# ========================================================== 05 BRAIN ========
B_NODES = {
    "link":  (470, 330, "СВЯЗЬ", "link", "kogda"),
    "heart": (470, 700, "ПРИНЯТИЕ", "heart", "prinimayut"),
    "cross": (1450, 330, "ОТВЕРЖЕНИЕ", "cross", "otvergayut"),
    "wave":  (1450, 700, "ЭМОЦИИ", "wave", "trevogu"),
}


def s05_brain(ctx, t):
    t0 = T["kogda"]
    zoom = 1.0 + 0.07 * e_io((t - t0) / 11)
    neg = ramp(t, T["otvergayut"], T["otvergayut"] + 0.3)
    ctx.save()
    cam(ctx, zoom, 960, 520)
    bx, by = 960, 500
    glow = 0.6 + 0.4 * ramp(t, T["prinimayut"] + 0.3, T["prinimayut"] + 0.9) \
        * (1 - neg * 0.6)
    spotlight(ctx, bx, by, 460, glow * 0.8)
    jit = neg * (2.5 + 2 * math.sin(t * 13))
    flick = 1.0
    if neg > 0 and math.sin(t * 47) > 0.86:
        flick = 0.55
    brain(ctx, bx, by, 1.0, ramp(t, t0 - 0.1, t0 + 1.0, e_io), flick,
          jitter=jit, t=t, inner=glow)
    for key, (nx, ny, label, icon, wkey) in B_NODES.items():
        tt = T[wkey]
        if t < tt:
            continue
        ap = ramp(t, tt, tt + 0.2)
        bad = key in ("cross", "wave")
        # connection
        ex = bx + (-205 if nx < bx else 215)
        ey = by + (-60 if ny < by else 70)
        n = 40
        pts = []
        for i in range(n):
            u = i / (n - 1)
            px = lerp(nx, ex, u)
            py = lerp(ny, ey, u) - math.sin(u * math.pi) * 40
            if bad:
                py += math.sin(u * 40 + t * 20) * 7 * math.sin(u * math.pi)
            pts.append((px, py))
        ck = ramp(t, tt + 0.05, tt + 0.5, e_io)
        polyline(ctx, pts, ck, 2.5, 0.6 * ap, dash=None if not bad else [10, 6])
        # travelling pulses
        if ck >= 1:
            for j in range(3):
                u = ((t - tt) * (0.9 if not bad else 1.6) + j / 3) % 1.0
                k = int(u * (n - 1))
                px, py = pts[k]
                white(ctx, ap * 0.9)
                ctx.arc(px, py, 5 if not bad else 4, 0, 2 * math.pi)
                ctx.fill()
        sh = 0
        if bad and t < tt + 0.4:
            sh = math.sin((t - tt) * 60) * 10 * (1 - (t - tt) / 0.4)
        badge(ctx, icon, nx + sh, ny, 46, ap, e_back((t - tt) / 0.35, 2.2),
              outline=bad)
        text(ctx, label, nx, ny + 82, 20, ap * 0.85, "bold", 3)
    # confidence: brain radiates
    if t > T["uverennee"]:
        for i in range(2):
            rk = clamp((t - T["uverennee"] - i * 0.25) / 1.3)
            if 0 < rk < 1:
                ctx.save()
                ctx.translate(bx, by)
                ctx.scale(1, 0.75)
                ctx.arc(0, 0, 250 + rk * 220, 0, 2 * math.pi)
                ctx.restore()
                white(ctx, (1 - rk) * 0.35 * (1 - neg))
                ctx.set_line_width(2.5)
                ctx.stroke()
    # doubts: question marks drift out of the brain
    if t > T["somnevatsya"]:
        for i, (dx, ph) in enumerate(((-120, 0), (40, 0.25), (160, 0.5))):
            tt = T["somnevatsya"] + ph
            if t > tt:
                u = t - tt
                al = ramp(t, tt, tt + 0.2) * (1 - ramp(t, T["i_postepenno"] - 0.3,
                                                       T["i_postepenno"]))
                text(ctx, "?", bx + dx + math.sin(u * 3 + i) * 8, by - 120 - u * 70,
                     46, al * 0.9, "bold")
    ctx.restore()
    pill_seq(ctx, t, [(T["prinimayut"], T["uverennee"] - 0.1, "ПРИНЯТИЕ"),
                      (T["uverennee"], T["otvergayut"] - 0.2, "УВЕРЕННОСТЬ"),
                      (T["otvergayut"], T["kritikuyut"] + 0.9, "ОТВЕРЖЕНИЕ И КРИТИКА"),
                      (T["trevogu"], T["somnevatsya"] - 0.1, "ТРЕВОГА"),
                      (T["somnevatsya"], T["i_postepenno"] - 0.3, "СОМНЕНИЯ")],
             y=120)


# =========================================================== 06 TRAP ========
CAGE_X = [-200, -133, -67, 0, 67, 133, 200]
SWITCHES = [("odezhdu", -1, "ОДЕЖДА"), ("slova", 1, "СЛОВА"),
            ("interesy", -1, "ИНТЕРЕСЫ"), ("povedenie", 1, "ПОВЕДЕНИЕ")]
G_LEFT = [(240, 0.82), (400, 0.9), (560, 0.85)]
G_RIGHT = [(1360, 0.85), (1520, 0.9), (1680, 0.82)]


def cage(ctx, x, gy, t, t0, t_lock, a, glow=0.0):
    top = gy - 420
    for i, dx in enumerate(CAGE_X):
        tt = t0 + 0.15 + i * (t_lock - t0 - 0.5) / len(CAGE_X)
        k = ramp(t, tt, tt + 0.35, e_back)
        if k <= 0:
            continue
        off = min(0.0, (1 - k) * -700)
        line(ctx, x + dx, top + 40 + off, x + dx, gy + off, 1, 5, a * (0.75 + 0.25 * glow))
    lk = ramp(t, t_lock - 0.25, t_lock, e_out)
    if lk > 0:
        ctx.save()
        ctx.translate(x, top + 40)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, 200, math.pi, math.pi + math.pi * lk)
        ctx.restore()
        white(ctx, a)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.arc(x, top - 40, 14 * lk, 0, 2 * math.pi)
        white(ctx, a)
        ctx.set_line_width(4)
        ctx.stroke()


def s06_trap(ctx, t):
    t0 = T["i_postepenno"]
    lock = T["lovushka"]
    groups = ramp(t, lock + 1.0, lock + 1.6)
    zoom = 1.18 - 0.18 * ramp(t, lock + 0.6, lock + 1.8, e_io) + \
        0.04 * e_io((t - lock - 1.8) / 10)
    ctx.save()
    cam(ctx, zoom, 960, 540 + 30 * (1 - groups))
    ground(ctx, 1)
    cone_light(ctx, 960, GY, 1)
    flash = math.exp(-max(0, t - lock) * 3.5) if t > lock else 0
    reclose = ramp(t, T["odobryat"], T["odobryat"] + 0.4)
    cage_a = 1.0 - 0.8 * groups + 0.75 * reclose
    cage(ctx, 960, GY, t, t0, lock, cage_a, glow=flash + reclose)

    # which side is he pleasing
    face, sw_k, cur, prev = 0, 1.0, None, None
    for key, side, _ in SWITCHES:
        if t >= T[key] - 0.1:
            prev, cur = cur, side
            sw_k = ramp(t, T[key] - 0.1, T[key] + 0.25, e_io)
    if cur is not None:
        face = lerp(prev if prev is not None else 0, cur, sw_k)
    emblem_of = {-1: "triangle", 1: "circle"}
    for grp, side, em in ((G_LEFT, -1, "triangle"), (G_RIGHT, 1, "circle")):
        act = 0.5 + 0.5 * clamp(face * side)
        ga = groups * (0.30 + 0.25 * act)
        for i, (x, sc) in enumerate(grp):
            person(ctx, x, GY, sc, ga, look=-side * 0.8, lum=0.6,
                   emblem=em, emblem_k=0.9)
        gx = sum(x for x, _ in grp) / 3
        shape(ctx, em, gx, 420 + 6 * math.sin(t * 2 + side), 26, groups * (0.5 + 0.5 * act))
    # main costume
    em, em_to, mk, hat, hat_a = None, None, 0.0, None, 0.0
    if cur is not None:
        em_from = emblem_of[prev] if prev else emblem_of[cur]
        em, em_to, mk = em_from, emblem_of[cur], sw_k
        hat = "cone" if cur < 0 else "beret"
        hat_a = sw_k
    arms = 0.18
    if t > T["povedenie"] - 0.1:
        arms = 0.18 + 1.0 * ramp(t, T["povedenie"] - 0.1, T["povedenie"] + 0.3, e_back)
    hop = abs(math.sin((t - T["odezhdu"]) * math.pi / 0.9)) * 10 * \
        ramp(t, T["odezhdu"], T["odezhdu"] + 0.3) * (1 - ramp(t, T["ne_potomu"],
                                                              T["ne_potomu"] + 0.5))
    person(ctx, 960, GY - hop, 1.0, 1.0, look=face, lean=face * 0.05,
           arm_l=arms, arm_r=arms, emblem=em, emblem_to=em_to, emblem_morph=mk,
           hat=hat, hat_a=hat_a)
    # words he says
    if T["slova"] - 0.1 < t < T["interesy"] - 0.15:
        p = e_back((t - T["slova"] + 0.1) / 0.3)
        hx, hy = head_pos(960, GY)
        bubble(ctx, 1110, hy - 60, 110, 70, 1, tail=(-1, 1), pop=p)
        shape(ctx, "circle", 1110, hy - 60, 16, 1)
    if T["interesy"] - 0.1 < t < T["povedenie"] - 0.15:
        p = e_back((t - T["interesy"] + 0.1) / 0.3)
        hx, hy = head_pos(960, GY)
        bubble(ctx, 810, hy - 60, 110, 70, 1, tail=(1, 1), pop=p, thought=True)
        shape(ctx, "triangle", 810, hy - 58, 16, 1)
    # his real self, fading away
    star_a = ramp(t, T["ne_potomu"], T["ne_potomu"] + 0.4) * \
        (1 - 0.8 * ramp(t, T["a_potomu"] + 0.3, T["odobryat"], e_io))
    if star_a > 0:
        hx, hy = head_pos(960, GY)
        shape(ctx, "star", 960, hy - 120 + 5 * math.sin(t * 2), 34, star_a, False,
              width=3)
    # approval rewards
    for j in range(4):
        tt = T["a_potomu"] + j * 0.3
        grp = G_LEFT if j % 2 == 0 else G_RIGHT
        x, sc = grp[1 + (j // 2) * (1 if j % 2 == 0 else -1)]
        pop_badge(ctx, t, tt, "heart", x, 520 - 30 * (j // 2), 26,
                  t_out=T["vot_chto_vazhno"] - 0.3)
    ctx.restore()
    seq = [(lock, lock + 1.0, "ЛОВУШКА")]
    for i, (key, side, label) in enumerate(SWITCHES):
        end = T[SWITCHES[i + 1][0]] - 0.15 if i + 1 < len(SWITCHES) else T["ne_potomu"] - 0.1
        seq.append((T[key] - 0.1, end, label))
    seq += [(T["ne_potomu"], T["a_potomu"] - 0.1, "НЕ ПОТОМУ ЧТО ХОЧЕТСЯ"),
            (T["a_potomu"], T["vot_chto_vazhno"] - 0.3, "А РАДИ ОДОБРЕНИЯ")]
    pill_seq(ctx, t, seq)


# ===================================================== 07 REALIZATION =======
ROW = [-760, -610, -460, -310, 310, 460, 610, 760, -170, 170]
REACT = [["heart", "cross", "heart", "dash", "cross", "heart", "?", "cross", "heart", "dash"],
         ["triangle", "circle", "square", "star", "circle", "triangle", "square", "circle", "star", "square"],
         ["heart", "star", "check", "triangle", "dash", "circle", "heart", "square", "check", "star"],
         ["?", "excl", "check", "?", "star", "excl", "check", "heart", "?", "excl"]]


def s07_realization(ctx, t):
    t0 = T["vot_chto_vazhno"]
    t_crowd = T["nevozmozhno"]
    t_gone = T["zabyvaem"]
    t_mirror = T["deystvitelno"]
    zoom = 1.12 - 0.12 * ramp(t, t_crowd - 0.2, t_crowd + 0.8, e_io) + \
        0.22 * ramp(t, t_gone, t_mirror + 2.0, e_io)
    fx = 960 + 150 * ramp(t, t_gone, t_mirror + 1.5, e_io)
    ctx.save()
    cam(ctx, zoom, fx, 560)
    ground(ctx, 1)
    cone_light(ctx, 960, GY, 1 - 0.5 * ramp(t, t_gone, t_mirror))
    crowd_a = ramp(t, t_crowd, t_crowd + 0.6) * (1 - ramp(t, t_gone, t_gone + 0.9))
    please = ramp(t, T["i_inogda"], T["i_inogda"] + 0.3) * (1 - ramp(t, t_gone - 0.2,
                                                                    t_gone + 0.3))
    for i, dx in enumerate(ROW):
        tt = t_crowd + i * 0.06
        ap = ramp(t, tt, tt + 0.3) * crowd_a
        sc = 0.62 if abs(dx) > 200 else 0.7
        x = 960 + dx
        person(ctx, x, GY, sc, ap * 0.45, look=-math.copysign(0.7, dx), lum=0.6)
        # reaction badges: approval cascade, then views / tastes / expectations
        stage, ts = 0, T["absolyutno"] + i * 0.07
        for si, key in enumerate(("vzglyady", "vkusy", "ozhidaniya")):
            if t > T[key] + i * 0.03:
                stage, ts = si + 1, T[key] + i * 0.03
        if t > T["absolyutno"] + i * 0.07:
            hx, hy = head_pos(x, GY, sc)
            kind = REACT[stage][i]
            badge(ctx, kind, x, hy - 70 + 5 * math.sin(t * 2 + i), 24, crowd_a,
                  e_back((t - ts) / 0.3, 2.4), outline=kind in ("cross", "dash", "?"))
    # main: trying to please everyone, then the mirror
    walk_k = ramp(t, t_gone, t_mirror, e_io)
    mx = 960 - 160 * walk_k
    walking = t_gone < t < t_mirror
    look = math.sin((t - T["i_inogda"]) * 4.2) * please
    if t > t_gone:
        look = lerp(look, 1.0, ramp(t, t_gone, t_gone + 0.4))
    arms = 0.18 + 0.7 * please * (0.5 + 0.5 * math.sin((t - T["i_inogda"]) * 8.4))
    conf = ramp(t, T["samim"] - 0.1, T["samim"] + 0.5, e_back)
    m_a = ramp(t, t_mirror - 0.3, t_mirror + 0.4)
    bright = ramp(t, T["nravitsya2"] - 0.2, T["samim"] + 0.3, e_io)
    mirror_x = 1230
    if m_a > 0:
        spotlight(ctx, mirror_x, GY - 230, 420, m_a * (0.5 + 1.0 * bright))
        mirror(ctx, mirror_x, GY, 250, 470, m_a, bright)
        # reflection
        ctx.save()
        ctx.arc(mirror_x, GY - 470 + 125, 125, math.pi, 2 * math.pi)
        ctx.rectangle(mirror_x - 125, GY - 470 + 125, 250, 345)
        ctx.clip()
        rx = mirror_x + (mirror_x - mx) * 0.25 - 40
        person(ctx, rx, GY - 10, 0.92, m_a * (0.3 + 0.35 * bright), look=-1,
               lean=0, emblem="star", emblem_k=0.6 + 0.6 * bright, lum=1.0)
        ctx.restore()
    person(ctx, mx, GY, 1.0, 1.0, look=look, arm_l=arms + 0.3 * conf,
           arm_r=arms + 0.3 * conf, walk=(t - t_gone) * 9 if walking else None,
           emblem="star" if conf > 0 else None, emblem_k=conf,
           stretch=1 + 0.05 * conf)
    ctx.restore()
    pill_seq(ctx, t, [(T["nevozmozhno"], T["u_kazhdogo"] - 0.1, "НЕВОЗМОЖНО НРАВИТЬСЯ ВСЕМ")])
    # three ideas row
    for i, (key, lab) in enumerate((("vzglyady", "ВЗГЛЯДЫ"), ("vkusy", "ВКУСЫ"),
                                    ("ozhidaniya", "ОЖИДАНИЯ"))):
        al = window(t, T[key], t_gone - 0.2, 0.2, 0.4)
        if al > 0:
            pill(ctx, lab, 960 + (i - 1) * 250, 165, al, 22, e_back((t - T[key]) / 0.35))
    sa = window(t, T["samim"] - 0.1, T["a_teper"] - 0.2, 0.25, 0.3)
    if sa > 0:
        pill(ctx, "ЧТО НРАВИТСЯ ТЕБЕ?", 960, 165, sa, 22, e_back((t - T["samim"]) / 0.35))


# ========================================================== 08 FINAL ========
GHOSTS = [("cone", "triangle", 0.0), ("beret", "circle", 0.55), (None, None, 1.1),
          ("cone", "triangle", 1.65), ("beret", "circle", 2.2)]


def s08_final(ctx, t):
    t0 = T["a_teper"]
    end_walk = FINAL_TEXT - 0.35
    a_walk = 1 - ramp(t, end_walk - 0.6, end_walk)
    if a_walk > 0:
        zoom = 1.0 + 0.25 * e_io((t - t0) / (end_walk - t0))
        ctx.save()
        cam(ctx, zoom, 960, 580)
        speed = 150.0
        ground(ctx, a_walk, offset=(t - t0) * speed)
        cone_light(ctx, 960, GY, a_walk)
        # past "masks" fading behind him
        for i, (hat, em, dt) in enumerate(GHOSTS):
            tt = T["skolko_raz"] + dt
            if t < tt:
                continue
            u = t - tt
            gx = 760 - u * speed - i * 10
            ga = ramp(t, tt, tt + 0.3) * (1 - ramp(t, tt + 1.6, tt + 2.6)) * 0.4
            person(ctx, gx, GY, 0.92, ga * a_walk, look=-0.3, emblem=em,
                   emblem_k=0.9, hat=hat, lum=0.6)
            if hat is None:
                hx, hy = head_pos(gx, GY, 0.92)
                bubble(ctx, gx - 20, hy - 70, 130, 60, ga * a_walk, tail=(1, 1))
                text(ctx, "ХА-ХА", gx - 20, hy - 70, 22, ga * a_walk, "bold", 2)
        person(ctx, 960, GY, 1.0, a_walk, look=0.5, walk=(t - t0) * 7.2,
               emblem="star", emblem_k=1.0)
        ctx.restore()
    # final statement
    ft = FINAL_TEXT
    a_txt = ramp(t, ft, ft + 0.3) * (1 - ramp(t, LOGO - 0.5, LOGO - 0.1))
    if a_txt > 0:
        rv = ramp(t, ft, ft + 0.8, lambda x: x)
        text(ctx, "ТЫ НЕ ОБЯЗАН НРАВИТЬСЯ ВСЕМ.", 960, 505, 70, a_txt, "bold", 4,
             reveal=rv)
        ln = ramp(t, ft + 0.5, ft + 1.4, e_io)
        line(ctx, 960 - 260 * ln, 585, 960 + 260 * ln, 585, 1, 2, a_txt * 0.6)
        text(ctx, "YOU DON'T HAVE TO BE LIKED BY EVERYONE.", 960, 630, 22,
             a_txt * 0.6 * ramp(t, ft + 0.9, ft + 1.5), "bold", 5)
    # logo
    a_logo = ramp(t, LOGO, LOGO + 0.4) * (1 - ramp(t, 100.6, 101.7, e_io))
    if a_logo > 0:
        rv = ramp(t, LOGO, LOGO + 0.9, lambda x: x)
        spotlight(ctx, 960, 540, 520, a_logo * 1.3)
        brain(ctx, 960, 405, 0.28, ramp(t, LOGO, LOGO + 1.2, e_io), a_logo * 0.9)
        text(ctx, "HUMAN MIND", 960, 545, 92, a_logo, "bold", 18, reveal=rv)
        text(ctx, "ЭПИЗОД 01  ·  ПОЧЕМУ МЫ ХОТИМ ВСЕМ НРАВИТЬСЯ", 960, 625, 20,
             a_logo * 0.6 * ramp(t, LOGO + 0.8, LOGO + 1.4), "bold", 5)


SCENE_FN = {
    "01_hook": s01_hook, "02_judgment": s02_judgment, "03_why": s03_why,
    "04_society": s04_society, "05_brain": s05_brain, "06_trap": s06_trap,
    "07_realization": s07_realization, "08_final": s08_final,
}
# crossfade-in length per scene (0 = hard cut on an impact)
FADE_IN = {"01_hook": 0.0, "02_judgment": 0.45, "03_why": 0.0, "04_society": 0.4,
           "05_brain": 0.45, "06_trap": 0.4, "07_realization": 0.0,
           "08_final": 0.45}


def draw_scenes(ctx, t):
    for idx, (name, s, e) in enumerate(SCENES):
        fin = FADE_IN[name]
        nxt = SCENES[idx + 1][0] if idx + 1 < len(SCENES) else None
        fout = FADE_IN[nxt] if nxt else 0.0
        if t < s or t >= e + fout:
            continue
        a = ramp(t, s, s + fin, e_io) if fin > 0 else 1.0
        if t >= e:
            a *= 1 - ramp(t, e, e + fout, e_io) if fout > 0 else 0
        if a <= 0.001:
            continue
        ctx.push_group()
        SCENE_FN[name](ctx, t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
