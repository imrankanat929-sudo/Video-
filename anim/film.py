"""The film: shot list driven by the voice-over cue sheet."""
import math
import numpy as np
import skia
from .core import *
from .character import Character, HERO, MOM, DAD, pose, auto_blink
from . import env
from .env import FLOOR, hero_c, mom_c, dad_c
from .timing import cues, duration, subtitles, QUESTION, TITLE

double_c = Character(HERO)  # identical look, identical seed

WARM_LIGHT = dict(dir=1, key=("#ffcf8a", 0.22), shadow=("#2a1408", 0.30))
COLD_LIGHT = dict(dir=1, key=("#9fdcff", 0.25), shadow=("#020818", 0.42))
VOID_LIGHT = dict(dir=-1, key=("#9fe6ff", 0.35), shadow=("#000308", 0.55), top=("#bfeaff", 0.12))
PHONE_LIGHT = dict(dir=1, key=("#9fdcff", 0.15), shadow=("#020818", 0.45), under=("#9fe0ff", 0.30))

DISTORT_SKSL = """
uniform shader img;
uniform float amt;
uniform float t;
uniform float2 ctr;
half4 main(float2 p) {
    float2 d = p - ctr;
    float r = length(d);
    float w = sin(r * 0.025 - t * 9.0) * 26.0 * amt + sin(p.y * 0.018 + t * 5.0) * 14.0 * amt;
    float2 dir = r > 0.001 ? d / r : float2(0.0, 0.0);
    float2 q = p + dir * w + float2(sin(p.y * 0.05 + t * 13.0) * 6.0 * amt, 0.0);
    float ca = 9.0 * amt;
    half4 c0 = img.eval(q);
    half r1 = img.eval(q + dir * ca).r;
    half b1 = img.eval(q - dir * ca).b;
    return half4(r1, c0.g, b1, c0.a);
}
"""
_distort = skia.RuntimeEffect.MakeForShader(DISTORT_SKSL)

GLITCH_SKSL = """
uniform shader img;
uniform float amt;
uniform float t;
float h(float x) { return fract(sin(x * 127.1) * 43758.5453); }
half4 main(float2 p) {
    float band = floor(p.y / 48.0);
    float on = step(1.0 - amt * 0.6, h(band + floor(t * 24.0)));
    float2 q = p + float2((h(band * 3.1 + floor(t * 24.0)) - 0.5) * 120.0 * amt * on, 0.0);
    half4 c0 = img.eval(q);
    half r1 = img.eval(q + float2(10.0 * amt, 0.0)).r;
    half b1 = img.eval(q - float2(10.0 * amt, 0.0)).b;
    return half4(r1, c0.g, b1, c0.a);
}
"""
_glitch = skia.RuntimeEffect.MakeForShader(GLITCH_SKSL)


def grade_filter(kind, k=1.0):
    """colour-matrix grade. warm: normal world, cold: parallel universe"""
    if kind == "warm":
        m = [1.08, 0.04, 0, 0, 0.02,
             0.02, 1.00, 0, 0, 0.00,
             0, 0, 0.86, 0, -0.01,
             0, 0, 0, 1, 0]
    elif kind == "cold":
        m = [0.80, 0.10, 0.04, 0, -0.02,
             0.04, 0.92, 0.08, 0, 0.0,
             0.04, 0.10, 1.12, 0, 0.03,
             0, 0, 0, 1, 0]
    elif kind == "void":
        m = [0.70, 0.12, 0.05, 0, -0.03,
             0.04, 0.88, 0.10, 0, -0.01,
             0.05, 0.12, 1.18, 0, 0.02,
             0, 0, 0, 1, 0]
    else:
        m = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    ident = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
    m = [lerp(a, b, k) for a, b in zip(ident, m)]
    return skia.ColorFilters.Matrix(m)


class Film:
    def __init__(self, lang, vo_env=None):
        self.lang = lang
        self.C = cues(lang)
        self.D = duration(lang)
        self.subs = subtitles(lang)
        self.vo_env = vo_env  # (fps, array) mouth envelope of the voice
        C = self.C
        self.shots = [
            (0.0, C["blue_light"], self.s_hallway, "warm"),
            (C["blue_light"], C["open_door"], self.s_door_light, "warm"),
            (C["open_door"], C["same_room"], self.s_open_door, "warm"),
            (C["same_room"], C["steps"], self.s_copy_room, "mid"),
            (C["steps"], C["noise"], self.s_steps, "mid"),
            (C["noise"], C["flash_fall"] + 0.45, self.s_distort, "mid"),
            (C["flash_fall"] + 0.45, C["eyes_open"], self.s_fallen, "cold"),
            (C["eyes_open"], C["leave_room"], self.s_wake, "cold"),
            (C["leave_room"], C["parents"], self.s_alt_hall, "cold"),
            (C["parents"], C["run_out"], self.s_parents, "cold"),
            (C["run_out"], C["phone_photos"], self.s_city, "cold"),
            (C["phone_photos"], C["message"], self.s_photos, "cold"),
            (C["message"], C["voice"], self.s_message, "cold"),
            (C["voice"], C["double_stand"], self.s_voice, "void"),
            (C["double_stand"], C["says"], self.s_double_reveal, "void"),
            (C["says"], C["realize"], self.s_double_line, "void"),
            (C["realize"], C["end_vo"], self.s_finale, "void"),
            (C["end_vo"], self.D + 1, self.s_question, "void"),
        ]
        grain = (np.random.RandomState(1).rand(4, 480, 270) * 255).astype(np.uint8)
        self.grain = []
        for g in grain:
            a = np.dstack([g, g, g, np.full_like(g, 255)])
            self.grain.append(skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType))

    # ------------------------------------------------------------------ helpers
    def mouth_vo(self, t):
        if self.vo_env is None:
            return 0.0
        fps, arr = self.vo_env
        i = int((t - 0.0) * fps)
        if 0 <= i < len(arr):
            return float(arr[i])
        return 0.0

    def world(self, c, cam, fn):
        c.save()
        cam.apply(c)
        fn(c)
        c.restore()

    # ------------------------------------------------------------------ frame
    def frame(self, c, t):
        c.clear(col("#000000"))
        shot, i = None, 0
        for i, s in enumerate(self.shots):
            if s[0] <= t < s[1]:
                shot = s
                break
        if shot is None:
            shot = self.shots[-1]
        a, b, fn, grade = shot
        lt = t - a
        fx = {}
        c.saveLayer(None, skia.Paint(ColorFilter=grade_filter("cold" if grade == "mid" else grade,
                                                                0.45 if grade == "mid" else 1.0)))
        fn(c, t, lt, b - a, fx)
        c.restore()
        # transition: short fade-through-black at selected cuts
        surf = None
        if fx.get("distort", 0) > 0.001 or fx.get("glitch", 0) > 0.001:
            surf = c.getSurface()
        if fx.get("distort", 0) > 0.001:
            img = surf.makeImageSnapshot()
            u = np.array([fx["distort"], t, W / 2, fx.get("dy", H * 0.45)], np.float32).tobytes()
            sh = _distort.makeShader(skia.Data.MakeWithCopy(u), img.makeShader(skia.SamplingOptions(skia.FilterMode.kLinear)), 1)
            c.drawPaint(skia.Paint(Shader=sh))
        if fx.get("glitch", 0) > 0.001:
            img = surf.makeImageSnapshot()
            u = np.array([fx["glitch"], t], np.float32).tobytes()
            sh = _glitch.makeShader(skia.Data.MakeWithCopy(u), img.makeShader(skia.SamplingOptions(skia.FilterMode.kLinear)), 1)
            c.drawPaint(skia.Paint(Shader=sh))
        self.post(c, t, fx, grade)
        # fades between shots
        fade = fx.get("fade", 0.0)
        soft = fn in (self.s_door_light, self.s_copy_room, self.s_alt_hall, self.s_parents, self.s_city,
                      self.s_photos, self.s_voice, self.s_double_reveal, self.s_question)
        if i > 0 and soft:
            fade = max(fade, 1 - inv(a, a + 0.2, t))
        if fade > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", fade))
        if fx.get("white", 0) > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint("#eaf9ff", fx["white"]))
        self.overlay_text(c, t)
        if t < 0.6:
            c.drawRect(skia.Rect.MakeWH(W, H), paint("#000000", 1 - t / 0.6))

    def post(self, c, t, fx, grade):
        # vignette
        v = 0.55 if grade in ("void", "cold") else 0.42
        c.drawRect(skia.Rect.MakeWH(W, H), gpaint(rad_grad(W / 2, H * 0.46, H * 0.72,
                                                            [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, int(255 * v))],
                                                            [0, 0.55, 1])))
        # film grain
        g = self.grain[int(t * 24) % 4]
        p = skia.Paint(BlendMode=skia.BlendMode.kOverlay)
        p.setAlphaf(0.10)
        c.save()
        c.scale(W / 270, H / 480)
        c.drawImage(g, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
        c.restore()

    # ------------------------------------------------------------------ captions + titles
    def overlay_text(self, c, t):
        L = self.lang
        # opening title (channel-style hook)
        if t < 4.6:
            k = ease_out(inv(0.4, 1.0, t)) * (1 - inv(4.0, 4.6, t))
            if k > 0:
                y0 = 300 - 40 * (1 - k)
                l1, l2 = TITLE[L]
                c.save()
                c.translate(W / 2, y0)
                sc = 0.9 + 0.1 * back_out(inv(0.4, 1.0, t))
                c.scale(sc, sc)
                s1 = min(76, 76 * 980 / font(76, "Black").measureText(l1))
                s2 = min(88, 88 * 980 / font(88, "Black").measureText(l2))
                text_center(c, l1, 0, 0, s1, "#ffffff", "Black", stroke=14, alpha=k, shadow=10)
                text_center(c, l2, 0, s2 + 14, s2, "#5fe1ff", "Black", stroke=14, alpha=k, shadow=10)
                c.restore()
        # time chip
        C = self.C
        if 4.6 < t < C["blue_light"]:
            k = inv(4.6, 5.0, t) * (1 - inv(C["blue_light"] - 0.4, C["blue_light"], t))
            self.chip(c, "19:47", k)
        if C["eyes_open"] + 1.6 < t < C["leave_room"]:
            k = inv(C["eyes_open"] + 1.6, C["eyes_open"] + 2.0, t)
            self.chip(c, "??:??" if int(t * 6) % 2 else "19:74", k, cold=True)
        # captions
        for a, b, txt, style in self.subs:
            if a <= t < b:
                self.caption(c, txt, style, t, a, b)
                break

    def chip(self, c, s, k, cold=False):
        if k <= 0:
            return
        f = font(44, "Black")
        w = f.measureText(s) + 90
        x0 = W / 2 - w / 2
        y0 = 150
        c.drawRRect(rrect(x0, y0, w, 74, 16), paint("#000000", 0.75 * k))
        c.drawRRect(rrect(x0, y0, w, 74, 16), paint("#ff3b4e" if not cold else "#5fe1ff", k, stroke=4))
        c.drawCircle(x0 + 38, y0 + 37, 16, paint("#ffffff", k, stroke=4))
        c.drawLine(x0 + 38, y0 + 37, x0 + 38, y0 + 27, paint("#ffffff", k, stroke=4))
        c.drawString(s, x0 + 66, y0 + 53, f, paint("#ffe14d" if not cold else "#bff3ff", k))

    def caption(self, c, txt, style, t, a, b):
        size = 60
        f = font(size, "ExtraBold")
        lines = wrap(txt, f, 900)
        k = ease_out(inv(a, a + 0.12, t))
        y = 1490 - (len(lines) - 1) * 34
        colr = "#ffffff" if style == "normal" else "#7fe9ff"
        for j, ln in enumerate(lines):
            yy = y + j * 70 + (1 - k) * 14
            text_center(c, ln, W / 2, yy, size, colr, "ExtraBold", stroke=12, stroke_color="#000000",
                        alpha=k, shadow=8)

    # ================================================================== SHOTS
    def s_hallway(self, c, t, lt, dur, fx):
        C = self.C
        stop_t = C["door_notice"] + 1.4
        x_start, x_stop = 150, 2370
        # walk with ease-out into the stop
        u = inv(0.0, stop_t, t)
        xpos = lerp(x_start, x_stop, 1 - (1 - u) ** 1.6) if t < stop_t else x_stop
        speed = (x_stop - x_start) * 1.6 * (1 - u) ** 0.6 / stop_t if t < stop_t else 0
        walking = clamp(speed / 120)
        phase = xpos / 62
        notice = seg(t, C["door_notice"] + 0.6, C["door_notice"] + 2.0)
        sur = t > C["never_before"] + 0.2
        tr = lerp(0.95, 0.35, notice)
        expr = "neutral" if notice < 0.3 else ("curious" if not sur else "surprised")
        # camera: follow, then frame hero + door, then push towards the door
        cx = lerp(xpos + 150, 2480, seg(t, C["door_notice"], C["door_notice"] + 2.5))
        z = lerp(0.82, 0.92, seg(t, 0, C["door_notice"]))
        z = lerp(z, 1.30, seg(t, C["never_before"], C["blue_light"], ease_in_out))
        cy = lerp(1000, 1060, seg(t, C["never_before"], C["blue_light"]))
        dx, dy = drift(t, 8)
        cam = Cam(cx + dx, cy + dy, z)
        light = 0.25 + 0.75 * seg(t, C["door_notice"], C["blue_light"])

        def w(c):
            env.hallway(c, t, door_light=light)
            env.ground_shadow(c, xpos, FLOOR, 170)
            hero_c.draw(c, xpos, FLOOR, 0.95,
                        pose(tr=tr, t=t, walk=phase, walk_amp=walking, expr=expr,
                             blink=auto_blink(t), look=(0.6 * notice, -0.2 * notice), body_tr=lerp(0.95, 0.6, notice)),
                        light=dict(WARM_LIGHT, key=(mix("#ffcf8a", "#8fe6ff", notice), 0.22 + 0.15 * notice)))
        self.world(c, cam, w)

    def s_door_light(self, c, t, lt, dur, fx):
        # close on the gap under the door: blue light, drifting particles, shoes stepping in
        z = lerp(2.2, 2.65, lt / dur)
        dx, dy = drift(t, 4)
        cam = Cam(2560 + dx, 1330 + dy, z)
        step = seg(lt, 0.6, 1.4)

        def w(c):
            env.hallway(c, t, door_light=1.0)
            env.particles(c, t, 2600, FLOOR - 120, 26, 260, "#9fe8ff", 0.7, swirl=0.4, size=4)
            hx = lerp(2280, 2390, step)
            hero_c.draw(c, hx, FLOOR, 0.95, pose(tr=0.9, t=t, walk=hx / 40, walk_amp=0.6 * (1 - abs(step - 0.5) * 2) if 0 < step < 1 else 0),
                        light=dict(WARM_LIGHT, key=("#8fe6ff", 0.45)))
        self.world(c, cam, w)

    def s_open_door(self, c, t, lt, dur, fx):
        reach = seg(lt, 0.2, 1.0)
        op = seg(lt, 1.1, 2.8, ease_in_out)
        z = lerp(1.25, 1.55, seg(lt, 0, dur))
        dx, dy = drift(t, 5)
        cam = Cam(lerp(2470, 2560, op) + dx, 1010 + dy, z)

        def inside(cc, ix, iy, iw, ih):
            cc.save()
            cc.translate(ix + iw / 2, iy)
            s_ = ih / 1500 * 1.15
            cc.scale(s_, s_)
            cc.translate(-500, -260)
            env.bedroom(cc, t, alt=False, x_view=(-300, 1500))
            cc.restore()
            cc.drawRect(skia.Rect.MakeXYWH(ix, iy, iw, ih), paint("#5fd0ff", 0.30))
            glow(cc, ix + iw / 2, iy + ih * 0.5, iw * 1.2, "#bff3ff", 0.5)

        def w(c):
            env.hallway(c, t, door_light=1.0, door_open=op, inside=inside)
            if op > 0:
                glow(c, 2600, FLOOR - 370, 700 * op, "#8fe6ff", 0.55 * op)
                env.particles(c, t, 2600, FLOOR - 400, 30, 420 * op + 50, "#bff3ff", 0.8 * op, size=5)
            arm = (lerp(0.1, 1.25, reach) * (1 - 0.6 * op), lerp(0.15, 0.25, reach))
            hero_c.draw(c, 2390, FLOOR, 0.95,
                        pose(tr=0.85, body_tr=0.9, t=t, arms=[(0.05, 0.15), arm], expr="surprised" if op > 0.3 else "curious",
                             blink=auto_blink(t, 2), look=(0.5, 0)),
                        light=dict(WARM_LIGHT, key=("#9fe9ff", 0.30 + 0.35 * op)))
            env.fog(c, t, FLOOR - 300, FLOOR + 50, "#9fe8ff", 0.10 * op, x_view=(1800, 3400))
        self.world(c, cam, w)

    def s_copy_room(self, c, t, lt, dur, fx):
        C = self.C
        items = C["same_items"] - C["same_room"]
        # pan across the room, then push to the phone on the desk
        pan = seg(lt, 0, items + 0.6)
        push = seg(lt, items + 0.8, items + 3.0)
        cx = lerp(150, 900, pan)
        cy = lerp(1000, 1080, pan)
        z = lerp(0.72, 0.8, pan)
        cx = lerp(cx, 1065, push)
        cy = lerp(cy, 1080, push)
        z = lerp(z, 3.4, push)
        dx, dy = drift(t, 6)
        cam = Cam(cx + dx, cy + dy, z)

        def w(c):
            env.bedroom(c, t, alt=False, door_x=-150, door_state=1.0, entering_light=0.35, phone_glow=0.5 * push)
            # the boy stays in the doorway, unsure
            hero_c.draw(c, -110, FLOOR, 0.95, pose(tr=0.45, t=t, expr="curious", blink=auto_blink(t, 1),
                                                    look=(0.7, 0)),
                        light=dict(WARM_LIGHT, dir=-1, key=("#9fe6ff", 0.35)))
        self.world(c, cam, w)

    def s_steps(self, c, t, lt, dur, fx):
        walk = seg(lt, 0.2, dur - 0.2, lambda x: x)
        hx = lerp(-60, 420, walk)
        dx, dy = drift(t, 6)
        cam = Cam(lerp(300, 500, walk) + dx, 1000 + dy, lerp(0.82, 0.95, walk))

        def w(c):
            env.bedroom(c, t, alt=False, door_x=-150, door_state=1.0, entering_light=0.3)
            env.ground_shadow(c, hx, FLOOR, 170)
            hero_c.draw(c, hx, FLOOR, 0.95,
                        pose(tr=lerp(0.85, 0.5, walk), t=t, walk=hx / 55, walk_amp=0.7 if 0 < walk < 1 else 0,
                             expr="worried", blink=auto_blink(t, 3), look=(math.sin(t * 1.3) * 0.8, 0)),
                        light=dict(WARM_LIGHT, key=("#cfe9ff", 0.25)))
        self.world(c, cam, w)

    def s_distort(self, c, t, lt, dur, fx):
        C = self.C
        k = seg(t, C["noise"], C["flash_fall"], ease_in)
        sx, sy = shake(t, 4 + 26 * k)
        z = lerp(1.25, 1.6, k)
        cam = Cam(440 + sx, 860 + sy, z)
        fall = seg(t, C["flash_fall"] + 0.1, C["flash_fall"] + 0.45, ease_in)

        def w(c):
            env.bedroom(c, t, alt=k > 0.75 and int(t * 14) % 3 == 0, door_x=-150, door_state=1.0)
            env.particles(c, t * (1 + 2 * k), 440, 900, 60, 700 * (1.2 - 0.5 * k), "#9fe8ff", 0.4 + 0.6 * k,
                          swirl=1 + 4 * k, size=6)
            glow(c, 440, 820, 900 * k + 100, "#8fe6ff", 0.6 * k)
            c.save()
            c.translate(420, FLOOR)
            c.rotate(-80 * fall)
            hero_c.draw(c, 0, 0, 0.95,
                        pose(tr=math.sin(t * 3) * 0.4, t=t, expr="terrified" if k > 0.25 else "scared",
                             look=(math.sin(t * 6) * 0.9, -0.3), wind=1 + 6 * k,
                             arms=[(0.6 + 0.3 * k, 1.6), (0.6 + 0.3 * k, 1.6)] if k > 0.4 else None),
                        light=dict(COLD_LIGHT, key=("#bff3ff", 0.3 + 0.4 * k)))
            c.restore()
        self.world(c, cam, w)
        fx["distort"] = 0.15 + 0.85 * k
        fx["dy"] = 860
        fx["white"] = seg(t, C["flash_fall"] - 0.2, C["flash_fall"] + 0.2)
        fx["hard_in"] = True

    def s_fallen(self, c, t, lt, dur, fx):
        dx, dy = drift(t, 5)
        cam = Cam(650 + dx, 1250 + dy, lerp(1.05, 1.15, lt / dur))

        def w(c):
            env.bedroom(c, t, alt=True, door_x=None, wall_glow=0.6 * (1 - lt / dur), glow_x=-150)
            env.fog(c, t, FLOOR - 200, FLOOR + 100, "#9cc9ff", 0.12)
            self.lying(c, t, 1.0)
            env.particles(c, t, 650, 1300, 18, 500, "#9fe8ff", 0.4 * (1 - lt / dur), swirl=0.3, size=4)
        self.world(c, cam, w)
        fx["white"] = 1 - ease_out(inv(0, 1.4, lt))
        fx["hard_in"] = True

    def lying(self, c, t, eyes_closed, look=(0, 0), expr="dazed", sit=0.0):
        c.save()
        c.translate(320, FLOOR - 60)
        c.rotate(90 * (1 - sit))
        env.ground_shadow(c, 0, 0, 1)
        hero_c.draw(c, 0, 60 * (1 - sit), 0.95,
                    pose(tr=0.0, t=t, expr=expr, blink=eyes_closed, look=look, wind=0.3,
                         arms=[(0.25, 0.1), (0.35, 0.2)], legs=[(0.05, 0.0), (-0.08, 0.05)]),
                    light=COLD_LIGHT)
        c.restore()

    def s_wake(self, c, t, lt, dur, fx):
        if lt < 1.7:
            # close-up on his face lying on the floor; eyes slowly open
            op = seg(lt, 0.3, 1.0)
            head_x = 320 + 800 * 0.95  # rotated: head is to the right of the feet
            cam = Cam(head_x + drift(t, 3)[0], FLOOR - 60 + 30, lerp(2.8, 3.1, lt / 1.7))
            c.save()

            def w(c):
                env.bedroom(c, t, alt=True, door_x=None)
                self.lying(c, t, 1 - op, look=(math.sin(lt * 2.5) * 0.6, 0), expr="dazed" if lt < 1.1 else "worried")
            self.world(c, cam, w)
            c.restore()
        else:
            l2 = lt - 1.7
            # he gets up and looks at the wall: the door is gone
            pan = seg(l2, 0.2, 1.4)
            dx, dy = drift(t, 5)
            cam = Cam(lerp(420, 60, pan) + dx, 1000 + dy, lerp(0.95, 1.0, pan))

            def w(c):
                env.bedroom(c, t, alt=True, door_x=None, wall_glow=0.25 * (1 - pan), glow_x=-150)
                env.fog(c, t, FLOOR - 200, FLOOR + 100, "#9cc9ff", 0.1)
                hero_c.draw(c, 360, FLOOR, 0.95, pose(tr=-0.7, t=t, expr="scared", blink=auto_blink(t, 4),
                                                       look=(-0.8, 0)), light=dict(COLD_LIGHT, dir=-1))
            self.world(c, cam, w)

    def s_alt_hall(self, c, t, lt, dur, fx):
        C = self.C
        ph = C["photos"] - C["leave_room"]
        ob = C["objects"] - C["leave_room"]
        if lt < ph:
            # walks out of his (other) room into the cold hallway
            u = seg(lt, 0.0, ph, lambda x: x)
            hx = lerp(1560, 1150, u)
            dx, dy = drift(t, 6)
            cam = Cam(hx - 120 + dx, 1000 + dy, 0.9)

            def w(c):
                env.hallway(c, t, alt=True, strange=False)
                env.fog(c, t, FLOOR - 300, FLOOR, "#9cc9ff", 0.08)
                env.ground_shadow(c, hx, FLOOR, 170)
                hero_c.draw(c, hx, FLOOR, 0.95, pose(tr=-0.9, t=t, walk=hx / 55, walk_amp=0.55, expr="worried",
                                                      blink=auto_blink(t, 5), look=(-0.6, -0.3)), light=dict(COLD_LIGHT, dir=-1))
            self.world(c, cam, w)
        elif lt < ob:
            # the family photo: he is not in it
            u = seg(lt, ph, ob)
            dx, dy = drift(t, 3)
            cam = Cam(lerp(900, 860, u) + dx, 720 + dy, lerp(1.7, 2.1, u))

            def w(c):
                env.hallway(c, t, alt=True, strange=False)
                hero_c.draw(c, 1150, FLOOR, 0.95, pose(tr=-0.75, t=t, expr="worried", blink=auto_blink(t, 6),
                                                        look=(-0.8, -0.4)), light=dict(COLD_LIGHT, dir=-1))
            self.world(c, cam, w)
        else:
            # things are not where they belong: vase moved, clock running backwards
            u = seg(lt, ob, dur)
            dx, dy = drift(t, 3)
            cam = Cam(lerp(2050, 2110, u) + dx, lerp(620, 760, u) + dy, lerp(2.2, 2.0, u))

            def w(c):
                env.hallway(c, t * 6, alt=True, strange=False)
            self.world(c, cam, w)

    def s_parents(self, c, t, lt, dur, fx):
        C = self.C
        lk = C["parents_look"] - C["parents"]
        rest = dur - lk
        mom_x, dad_x = 1560, 1800

        def parents(c, react):
            mom_c.draw(c, mom_x, FLOOR, 0.9,
                       pose(tr=-0.45, t=t, expr="confused" if react > 0.5 else "calm", tilt=-6 * react,
                            blink=auto_blink(t, 7), look=(-0.7, 0),
                            arms=[(0.1, 0.1), (0.25 * react, 2.2 * react + 0.1)]),
                       light=dict(COLD_LIGHT, dir=-1))
            dad_c.draw(c, dad_x, FLOOR, 0.9,
                       pose(tr=-0.35, t=t, expr="angry" if react > 0.8 else ("confused" if react > 0.3 else "calm"),
                            tilt=5 * react, blink=auto_blink(t, 8), look=(-0.8, 0)),
                       light=dict(COLD_LIGHT, dir=-1))

        if lt < lk:
            u = seg(lt, 0, lk - 0.3)
            hx = lerp(150, 1050, u)
            dx, dy = drift(t, 6)
            cam = Cam(lerp(700, 1250, u) + dx, 1000 + dy, 0.82)

            def w(c):
                env.kitchen(c, t)
                env.ground_shadow(c, hx, FLOOR, 170)
                hero_c.draw(c, hx, FLOOR, 0.95, pose(tr=0.9, t=t, walk=hx / 55, walk_amp=0.6 if u < 1 else 0,
                                                      expr="worried", blink=auto_blink(t, 2)),
                            light=COLD_LIGHT)
                parents(c, seg(lt, lk - 1.2, lk))
            self.world(c, cam, w)
            return
        l2 = lt - lk
        if l2 < rest * 0.42:
            # parents: they don't recognise him
            u = l2 / (rest * 0.42)
            dx, dy = drift(t, 4)
            cam = Cam(1680 + dx, 820 + dy, lerp(1.55, 1.75, u))

            def w(c):
                env.kitchen(c, t)
                parents(c, 1.0)
            self.world(c, cam, w)
        elif l2 < rest * 0.78:
            # he tries to explain who he is
            u = (l2 - rest * 0.42) / (rest * 0.36)
            dx, dy = drift(t, 4)
            cam = Cam(1060 + dx, 900 + dy, lerp(1.8, 2.0, u))
            talk = max(0, math.sin(t * 17) * 0.5 + math.sin(t * 7.3) * 0.5)

            def w(c):
                env.kitchen(c, t)
                g = 0.6 + 0.35 * math.sin(t * 5)
                hero_c.draw(c, 1050, FLOOR, 0.95,
                            pose(tr=0.55, t=t, expr="scared", mouth=0.2 + 0.6 * talk, blink=auto_blink(t, 3),
                                 arms=[(0.35, 1.6 + 0.6 * g), (0.4, 1.9 - 0.5 * g)], look=(0.7, 0), brow_extra=-0.03),
                            light=COLD_LIGHT)
            self.world(c, cam, w)
        else:
            # wide: dad steps forward, the boy backs away
            u = (l2 - rest * 0.78) / (rest * 0.22)
            dx, dy = drift(t, 6)
            cam = Cam(1350 + dx, 1000 + dy, 0.95)
            hx = lerp(1050, 900, ease_out(u))

            def w(c):
                env.kitchen(c, t)
                hero_c.draw(c, hx, FLOOR, 0.95, pose(tr=0.7, t=t, expr="terrified", walk=hx / 40, walk_amp=0.4,
                                                      blink=0), light=COLD_LIGHT)
                mom_c.draw(c, mom_x, FLOOR, 0.9, pose(tr=-0.45, t=t, expr="worried", look=(-0.7, 0),
                                                       arms=[(0.1, 0.1), (0.25, 2.3)]), light=dict(COLD_LIGHT, dir=-1))
                dad_c.draw(c, lerp(dad_x, 1450, ease_out(u)), FLOOR, 0.9,
                           pose(tr=-0.6, t=t, expr="angry", walk=u * 6, walk_amp=0.5,
                                arms=[(0.3, 0.2), (1.2, 0.3)]), light=dict(COLD_LIGHT, dir=-1))
            self.world(c, cam, w)

    def s_city(self, c, t, lt, dur, fx):
        C = self.C
        L = self.lang
        ci = C["city"] - C["run_out"]
        nu = C["numbers"] - C["run_out"]
        bu = C["buildings"] - C["run_out"]
        if lt < ci + 0.3:
            # runs out of the doorway into the street
            u = seg(lt, 0, ci + 0.3, lambda x: x)
            hx = lerp(380, 1150, u)
            dx, dy = drift(t, 8)
            cam = Cam(hx + 100 + dx, 950 + dy, 0.72)

            def w(c):
                env.street(c, t, L)
                env.fog(c, t, FLOOR - 400, FLOOR + 100, "#9cc9ff", 0.14)
                env.ground_shadow(c, hx, FLOOR, 170)
                hero_c.draw(c, hx, FLOOR, 0.95, pose(tr=0.95, t=t, walk=hx / 38, run=1.0, lean=6, expr="scared",
                                                      blink=0), light=COLD_LIGHT)
            self.world(c, cam, w)
        elif lt < nu:
            # store names: wrong
            u = seg(lt, ci + 0.3, nu, lambda x: x)
            dx, dy = drift(t, 4)
            cam = Cam(lerp(150, 2000, u) + dx, 950 + dy, 1.0)
            hx = lerp(700, 1700, u)

            def w(c):
                env.street(c, t, L)
                env.fog(c, t, FLOOR - 400, FLOOR + 100, "#9cc9ff", 0.12)
                hero_c.draw(c, hx, FLOOR + 30, 0.95, pose(tr=0.6, t=t, walk=hx / 55, walk_amp=0.5, expr="worried",
                                                           look=(0.2, -1.0), blink=auto_blink(t, 4)), light=COLD_LIGHT)
            self.world(c, cam, w)
        elif lt < bu:
            # house number 14 -> 41
            u = seg(lt, nu, bu)
            dx, dy = drift(t, 3)
            cam = Cam(1320 + dx, 600 + dy, lerp(2.4, 2.8, u))
            swap = seg(lt, nu + 0.5, nu + 0.9)
            g = 1.0 - abs(swap - 0.5) * 2 if 0 < swap < 1 else 0

            def w(c):
                env.street(c, t, L, glitch=g, number_swap=swap)
            self.world(c, cam, w)
            fx["glitch"] = g * 0.8
        else:
            # wide, low angle: the city is wrong
            u = seg(lt, bu, dur)
            dx, dy = drift(t, 6)
            cam = Cam(1500 + dx, lerp(600, 250, u) + dy, lerp(0.5, 0.56, u))

            def w(c):
                env.street(c, t, L, x_view=(-1000, 4200))
                env.fog(c, t, FLOOR - 600, FLOOR + 200, "#9cc9ff", 0.16, speed=40)
                hero_c.draw(c, 1500, FLOOR + 80, 0.95, pose(tr=0.15, t=t, expr="scared", look=(0.0, -1.0), tilt=-4,
                                                             blink=auto_blink(t, 5)), light=COLD_LIGHT)
            self.world(c, cam, w)

    def bokeh_bg(self, c, t, colr="#5fd0ff"):
        c.drawRect(skia.Rect.MakeWH(W, H), gpaint(lin_grad(0, 0, 0, H, ["#050a16", "#0c1a30", "#050a16"])))
        for i in range(16):
            x = (hash1(i * 3.3) * W + t * 12 * (1 + hash1(i))) % (W + 300) - 150
            y = hash1(i * 7.1) * H
            r = 40 + 90 * hash1(i * 1.9)
            c.drawCircle(x, y, r, paint(colr, 0.06 + 0.08 * hash1(i * 4.4), blur=r * 0.15))

    def s_photos(self, c, t, lt, dur, fx):
        C = self.C
        mi = C["missing"] - C["phone_photos"]
        if lt < mi - 0.4:
            # he pulls out the phone, face lit from below
            u = seg(lt, 0, mi - 0.4)
            dx, dy = drift(t, 4)
            cam = Cam(1500 + dx, 820 + dy, lerp(1.6, 1.85, u))
            lift = seg(lt, 0.0, 0.9)

            def w(c):
                env.street(c, t, self.lang, x_view=(400, 2600))
                env.fog(c, t, FLOOR - 600, FLOOR, "#9cc9ff", 0.14)
                hero_c.draw(c, 1500, FLOOR, 0.95,
                            pose(tr=0.25, t=t, expr="worried", look=(0.2, 0.8), hold_phone=True, phone_glow=lift,
                                 arms=[(0.08, 0.12), (lerp(0.1, 0.35, lift), lerp(0.1, 2.25, lift))],
                                 blink=auto_blink(t, 6)),
                            light=dict(PHONE_LIGHT, under=("#9fe0ff", 0.35 * lift)))
            self.world(c, cam, w)
        else:
            u = seg(lt, mi - 0.4, dur)
            self.bokeh_bg(c, t)
            pw = lerp(560, 640, u)
            scr = env.gallery_screen(self.lang, t)
            dx, dy = drift(t, 5)
            env.hand_back(c, W / 2 + dx, 760 + dy, pw)
            env.phone(c, W / 2 + dx, 760 + dy, pw, t, scr, tilt=lerp(-3, 1, u))
            env.hand_front(c, W / 2 + dx, 760 + dy, pw)

    def s_message(self, c, t, lt, dur, fx):
        C = self.C
        rd = C["read"] - C["message"]
        mt = C["msg_text"] - C["message"]
        banner = seg(lt, 0.15, 0.6)
        opened = seg(lt, rd + 0.1, rd + 0.6)
        typed = seg(lt, rd + 0.6, mt + 0.15, lambda x: x)
        if lt > mt + 0.15:
            typed = 1.0
        self.bokeh_bg(c, t)
        u = lt / dur
        pw = lerp(560, 640, ease_in_out(u))
        dx, dy = drift(t, 4)
        scr = env.message_screen(self.lang, t, banner=banner, opened=opened, typed=typed)
        env.hand_back(c, W / 2 + dx, 740 + dy, pw)
        env.phone(c, W / 2 + dx, 740 + dy, pw, t, scr, tilt=lerp(1, -1, u), glow_a=0.6 + 0.4 * opened)
        env.hand_front(c, W / 2 + dx, 740 + dy, pw)
        # notification pulse
        if 0.15 < lt < 0.9:
            k = 1 - inv(0.15, 0.9, lt)
            c.drawCircle(W / 2, 300, 200 * (1 - k) + 40, paint("#7fe9ff", 0.6 * k, stroke=6))

    def s_voice(self, c, t, lt, dur, fx):
        C = self.C
        tu = C["turn"] - C["voice"]
        if lt < tu + 0.2:
            # close-up: phone light on his face, a voice behind him
            u = lt / (tu + 0.2)
            startle = seg(lt, 0.3, 0.6)
            dx, dy = drift(t, 3)
            cam = Cam(540 + dx, 760 + dy, lerp(2.3, 2.55, u))

            def w(c):
                env.void(c, t, x_view=(-600, 1600), intensity=0.3)
                env.fog(c, t, 300, 1200, "#7fb4ff", 0.08)
                hero_c.draw(c, 540, FLOOR, 0.95,
                            pose(tr=lerp(0.05, -0.25, startle), t=t, expr="scared" if startle > 0.5 else "worried",
                                 look=(lerp(0, -1, startle), 0), hold_phone=True, phone_glow=1.0, blink=0 if startle > 0 else auto_blink(t),
                                 arms=[(0.08, 0.12), (0.35, 2.25)]),
                            light=dict(PHONE_LIGHT, under=("#9fe0ff", 0.4)))
            self.world(c, cam, w)
        else:
            # he slowly turns around while the camera orbits
            u = seg(lt, tu + 0.2, dur, ease_in_out)
            tr = lerp(-0.25, -1.0, min(1, u * 1.6))
            view = "back" if u > 0.62 else "front"
            dx, dy = drift(t, 3)
            orbit = u * 700
            cam = Cam(540 + dx, lerp(760, 900, u) + dy, lerp(2.3, 1.6, u))

            def w(c):
                c.save()
                c.translate(orbit, 0)
                env.void(c, t, x_view=(-1600, 2600), intensity=0.3 + 0.7 * u)
                c.restore()
                env.fog(c, t, 300, 1200, "#7fb4ff", 0.08)
                hero_c.draw(c, 540, FLOOR, 0.95,
                            pose(view=view, tr=tr, t=t, expr="terrified", look=(-1, 0),
                                 arms=[(0.08, 0.12), (lerp(0.35, 0.1, u), lerp(2.25, 0.2, u))]),
                            light=dict(VOID_LIGHT, dir=1))
            self.world(c, cam, w)

    def s_double_reveal(self, c, t, lt, dur, fx):
        C = self.C
        sh = C["same_hair"] - C["double_stand"]
        if lt < sh:
            # over the shoulder: an exact copy of him stands in the light
            u = lt / sh
            dx, dy = drift(t, 4)
            cam = Cam(520 + dx, lerp(1000, 940, u) + dy, lerp(1.2, 1.38, u))
            appear = seg(lt, 0.0, 0.8)

            def w(c):
                env.void(c, t)
                env.fog(c, t, FLOOR - 500, FLOOR + 100, "#7fb4ff", 0.16)
                c.saveLayerAlpha(None, int(255 * appear))
                env.ground_shadow(c, 600, FLOOR, 160, 0.5)
                double_c.draw(c, 600, FLOOR, 0.95,
                              pose(tr=-0.05, t=t, expr="calm", blink=auto_blink(t, 9, 4.6), look=(-0.2, 0.1)),
                              light=dict(VOID_LIGHT, key=("#bff0ff", 0.45), shadow=("#000308", 0.35)))
                c.restore()
                # hero back, foreground, out of focus-ish & big
                hero_c.draw(c, 170, FLOOR + 1000, 1.9, pose(view="back", t=t, tilt=3, wind=0.6),
                            light=dict(VOID_LIGHT, key=("#9fe6ff", 0.2), shadow=("#000000", 0.7)))
            self.world(c, cam, w)
        else:
            # same hair, same clothes, same face: split screen
            u = seg(lt, sh, dur)
            l2 = lt - sh
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(0, 0, W / 2, H))
            cam = Cam(540 + 270 / 2.6 - 25 * u, 760, 2.6)

            def w(c):
                env.void(c, t, intensity=0.6)
                hero_c.draw(c, 540, FLOOR, 0.95, pose(tr=0.35, t=t, expr="scared", look=(1, 0), blink=auto_blink(t, 2)),
                            light=dict(VOID_LIGHT, dir=-1))
            self.world(c, cam, w)
            c.restore()
            c.save()
            c.clipRect(skia.Rect.MakeXYWH(W / 2, 0, W / 2, H))
            cam = Cam(540 - 270 / 2.6 + 25 * u, 760, 2.6)

            def w2(c):
                env.void(c, t, intensity=0.6)
                double_c.draw(c, 540, FLOOR, 0.95, pose(tr=-0.35, t=t, expr="smug", look=(-1, 0),
                                                         blink=auto_blink(t, 9, 4.6)), light=dict(VOID_LIGHT, dir=1))
            self.world(c, cam, w2)
            c.restore()
            c.drawLine(W / 2, 0, W / 2, H, paint("#9fe9ff", 0.9, stroke=4))
            glow(c, W / 2, H * 0.4, 300, "#7fe0ff", 0.25)
            # wipe in
            if l2 < 0.35:
                fx["fade"] = 1 - l2 / 0.35

    def s_double_line(self, c, t, lt, dur, fx):
        C = self.C
        dl = C["double_line"] - C["says"]
        u = lt / dur
        dx, dy = drift(t, 2.5)
        z = lerp(2.5, 3.3, ease_in_out(u))
        cam = Cam(560 + dx, 735 + dy, z)
        m = self.mouth_vo(t) if lt > dl - 0.05 else 0.0

        def w(c):
            env.void(c, t, intensity=1.0)
            env.fog(c, t, 400, 1200, "#7fb4ff", 0.10)
            double_c.draw(c, 560, FLOOR, 0.95,
                          pose(tr=-0.08, t=t, expr="smug", mouth=m, blink=auto_blink(t, 9, 4.6),
                               look=(0.0, 0.0), eye_glint=0.35 + 0.2 * math.sin(t * 2), tilt=lerp(0, -3, u)),
                          light=VOID_LIGHT)
        self.world(c, cam, w)

    def s_finale(self, c, t, lt, dur, fx):
        C = self.C
        m1 = C["maybe2"] - C["realize"]
        ro = C["real_one"] - C["realize"]
        im = C["important"] - C["realize"]
        if lt < m1:
            u = lt / m1
            dx, dy = drift(t, 2.5)
            cam = Cam(540 + dx, 740 + dy, lerp(2.4, 3.0, u))

            def w(c):
                env.void(c, t, intensity=0.7)
                env.fog(c, t, 400, 1200, "#7fb4ff", 0.08)
                hero_c.draw(c, 540, FLOOR, 0.95, pose(tr=0.05, t=t, expr="sad" if u > 0.4 else "terrified",
                                                       blink=auto_blink(t, 1), look=(0, 0.2)),
                            light=dict(VOID_LIGHT, dir=-1))
            self.world(c, cam, w)
        elif lt < ro:
            # they face each other: a portal hums between them -- someone swapped places
            u = (lt - m1) / (ro - m1)
            dx, dy = drift(t, 4)
            cam = Cam(560 + dx, 900 + dy, lerp(1.25, 1.4, u))

            def w(c):
                env.void(c, t, intensity=0.5)
                pr = 160 + 20 * math.sin(t * 3)
                glow(c, 560, 1050, 520, "#6fdcff", 0.55)
                c.drawOval(skia.Rect.MakeLTRB(560 - pr * 0.55, 1050 - pr * 1.8, 560 + pr * 0.55, 1050 + pr * 1.8),
                           paint("#bff6ff", 0.8, stroke=10, blur=4))
                c.drawOval(skia.Rect.MakeLTRB(560 - pr * 0.45, 1050 - pr * 1.6, 560 + pr * 0.45, 1050 + pr * 1.6),
                           paint("#0a2a44", 0.85))
                env.particles(c, t, 560, 1050, 40, 330, "#bff3ff", 0.8, swirl=2.5, size=5)
                hero_c.draw(c, 240, FLOOR, 0.95, pose(tr=0.95, t=t, expr="scared", blink=auto_blink(t, 1)),
                            light=dict(VOID_LIGHT, dir=1))
                double_c.draw(c, 880, FLOOR, 0.95, pose(tr=-0.95, t=t, expr="smug", blink=auto_blink(t, 9, 4.6)),
                              light=dict(VOID_LIGHT, dir=-1))
            self.world(c, cam, w)
        elif lt < im:
            # who is real? faces flicker between the two of them
            l2 = lt - ro
            which = int(l2 / 0.42) % 2
            dx, dy = drift(t, 3)
            cam = Cam(540 + dx, 740 + dy, 2.8 + 0.1 * math.sin(t))

            def w(c):
                env.void(c, t, intensity=0.8)
                ch = hero_c if which == 0 else double_c
                ch.draw(c, 540, FLOOR, 0.95, pose(tr=0.0, t=t, expr="scared" if which == 0 else "smug",
                                                  blink=0, eye_glint=0.0 if which == 0 else 0.5),
                        light=dict(VOID_LIGHT, dir=-1 if which == 0 else 1))
            self.world(c, cam, w)
            ph = (l2 % 0.42) / 0.42
            fx["glitch"] = 0.7 if ph < 0.18 else 0.0
        else:
            u = seg(lt, im, dur)
            dx, dy = drift(t, 1.5)
            cam = Cam(540 + 10 * u + dx, lerp(745, 785, u) + dy, lerp(3.0, 5.2, ease_in(u)))

            def w(c):
                env.void(c, t, intensity=0.6)
                hero_c.draw(c, 540, FLOOR, 0.95, pose(tr=0.0, t=t, expr="sad", blink=auto_blink(t, 3),
                                                       look=(0, 0)), light=dict(VOID_LIGHT, dir=-1))
            self.world(c, cam, w)
            fx["fade"] = seg(lt, dur - 1.0, dur)

    def s_question(self, c, t, lt, dur, fx):
        c.drawRect(skia.Rect.MakeWH(W, H), paint("#020409"))
        env.particles(c, t, W / 2, H * 0.45, 30, 700, "#7fe0ff", 0.35, swirl=0.3, size=4)
        k = ease_out(inv(0.4, 1.4, lt))
        q = QUESTION[self.lang]
        f = font(72, "Black")
        lines = wrap(q, f, 900)
        y = H * 0.42 - (len(lines) - 1) * 48
        for j, ln in enumerate(lines):
            text_center(c, ln, W / 2, y + j * 96 + (1 - k) * 30, 72, "#ffffff" if j < len(lines) - 1 else "#7fe9ff",
                        "Black", alpha=k, shadow=12)
        glow(c, W / 2, H * 0.62, 80 + 10 * math.sin(t * 3), "#7fe0ff", 0.5 * k)
        text_center(c, "?", W / 2, H * 0.62 + 40, 120, "#ffffff", "Black", alpha=k)
        self._no_caption = True
        fx["fade"] = seg(lt, self.D - self.C["end_vo"] - 0.8, self.D - self.C["end_vo"])
