"""2D character rig drawn with Skia.

Character space: feet centre at (0, 0), y grows downward, the hero is ~1000 units tall.
The same Look + seed is used for the hero and his double so they are pixel-identical;
only the Pose (expression, behaviour) differs.
"""
import math
import random
import skia
from .core import (paint, col, mix, shade, lin_grad, rad_grad, gpaint, smooth_path,
                   path_poly, clamp, lerp, vnoise, hexc)


class Look:
    def __init__(self, **kw):
        self.skin = "#d4a47c"
        self.skin_shadow = "#b98863"
        self.hair = "#111114"
        self.hair_hi = "#2a2a33"
        self.top = "#25262d"
        self.top_dark = "#1a1b21"
        self.top_trim = "#1d1e24"
        self.pants = "#16171c"
        self.pants_dark = "#0f1014"
        self.shoe = "#c3c3c6"
        self.sole = "#ececee"
        self.eye = "#0d0d10"
        self.brow = "#121214"
        self.height = 1.0
        self.head_r = 118
        self.hair_style = "messy"
        self.seed = 7
        self.glasses = False
        self.stubble = False
        self.top_style = "sweater"
        self.width = 1.0
        self.lip = None
        self.__dict__.update(kw)


HERO = Look()
MOM = Look(skin="#d9ad88", skin_shadow="#bf8f6b", hair="#4a2d1e", hair_hi="#6b4430",
           top="#6d3b45", top_dark="#552c35", top_trim="#5e313a", pants="#2c2f3a",
           pants_dark="#22242d", shoe="#3a3330", sole="#5a514c", height=1.06,
           head_r=112, hair_style="bob", seed=21, top_style="cardigan", lip="#a3555a")
DAD = Look(skin="#cf9c74", skin_shadow="#b0805c", hair="#3b2a20", hair_hi="#594033",
           top="#4c5a6b", top_dark="#3c4858", top_trim="#43505f", pants="#2a2b30",
           pants_dark="#1f2024", shoe="#2b2622", sole="#4a423c", height=1.14,
           head_r=116, hair_style="short", seed=33, glasses=True, stubble=True,
           top_style="shirt", width=1.12)

EXPR = {
    #            brow_ang brow_y  eyes      mouth     sweat
    "neutral":   (0.00, 0.00, "dot", "none", 0),
    "calm":      (0.02, 0.02, "dot", "none", 0),
    "curious":   (-0.10, -0.06, "dot", "flat", 0),
    "surprised": (-0.16, -0.16, "dot", "o", 0),
    "worried":   (-0.30, -0.08, "dot", "frown", 0),
    "scared":    (-0.34, -0.14, "white", "open", 1),
    "terrified": (-0.40, -0.20, "white", "wide", 1),
    "angry":     (0.34, 0.06, "dot", "frown", 0),
    "smug":      (0.10, 0.08, "lid", "smirk", 0),
    "sad":       (-0.38, -0.04, "dot", "frown", 0),
    "confused":  ("asym", -0.04, "dot", "squiggle", 0),
    "determined": (0.20, 0.04, "dot", "flat", 0),
    "dazed":     (-0.12, -0.02, "lid2", "o", 0),
}


def pose(**kw):
    p = dict(view="front", tr=0.0, body_tr=None, t=0.0,
             walk=0.0, walk_amp=0.0, run=0.0,
             arms=None, legs=None,
             expr="neutral", blink=0.0, mouth=0.0, look=(0.0, 0.0),
             tilt=0.0, sweat=None, wind=1.0, lean=0.0, breathe=1.0,
             hold_phone=False, phone_glow=0.0, brow_extra=0.0, eye_glint=0.0)
    p.update(kw)
    return p


def auto_blink(t, seed=0, period=3.7):
    """returns 0..1 eye closure for natural blinking"""
    ph = (t + seed * 1.37) % period
    # occasional double blink
    d = abs(ph - 0.08)
    if d < 0.09:
        return 1 - d / 0.09
    return 0.0


class Character:
    def __init__(self, look):
        self.L = look
        rnd = random.Random(look.seed)
        self.tufts = [(rnd.uniform(-1, 1), rnd.uniform(0.8, 1.2), rnd.uniform(0, 6.28)) for _ in range(40)]

    # ------------------------------------------------------------------
    def draw(self, c, x, y, s, P, light=None):
        """draw at screen/world (x, y) feet position with scale s (units->px)"""
        L = self.L
        c.save()
        c.translate(x, y)
        c.scale(s * L.height, s * L.height)
        if light:
            c.saveLayer(None, None)
        tr = clamp(P["tr"], -1, 1)
        btr = P["body_tr"] if P["body_tr"] is not None else tr * 0.75
        back = P["view"] == "back"
        t = P["t"]
        ph = P["walk"]
        amp = P["walk_amp"]
        bob = -abs(math.sin(ph)) * 14 * amp - P["run"] * abs(math.sin(ph)) * 18
        c.translate(0, bob)
        if P["lean"]:
            c.rotate(P["lean"])
        face = 1 if (tr >= 0) else -1
        prof = abs(btr)

        arms = P["arms"] or self._default_arms(P, prof)
        legs = P["legs"] or self._default_legs(P)

        # far arm (profile)
        if prof > 0.55 and not back:
            far = 0 if face > 0 else 1
            self._arm(c, far, arms[far], btr, face, P, far_side=True)
        self._legs(c, legs, btr, face, back)
        self._torso(c, btr, face, back, P)
        if back:
            for i in (0, 1):
                self._arm(c, i, arms[i], btr, face, P)
            self._neck(c, btr)
            self._head_back(c, P)
        else:
            self._neck(c, btr)
            self._head(c, P)
            for i in (0, 1):
                if prof > 0.55 and i == (0 if face > 0 else 1):
                    continue
                self._arm(c, i, arms[i], btr, face, P)
        if light:
            self._light(c, light)
            c.restore()
        c.restore()

    # ------------------------------------------------------------------
    def _light(self, c, light):
        """light = dict(key=(colour, alpha), shadow=(colour, alpha), dir=+1 (from right) / -1)"""
        d = light.get("dir", 1)
        kc, ka = light.get("key", ("#ffd9a0", 0.18))
        sc, sa = light.get("shadow", ("#0a0c20", 0.35))
        k = hexc(kc)
        sh = hexc(sc)
        g = lin_grad(-260 * d, -500, 260 * d, -500,
                     [(sh[0], sh[1], sh[2], int(255 * sa)), (sh[0], sh[1], sh[2], 0),
                      (k[0], k[1], k[2], 0), (k[0], k[1], k[2], int(255 * ka))],
                     [0.0, 0.42, 0.55, 1.0])
        c.drawPaint(gpaint(g, skia.BlendMode.kSrcATop))
        if "top" in light:
            tc, ta = light["top"]
            q = hexc(tc)
            g2 = lin_grad(0, -1050, 0, 0, [(q[0], q[1], q[2], int(255 * ta)), (q[0], q[1], q[2], 0)],
                          [0, 0.7])
            c.drawPaint(gpaint(g2, skia.BlendMode.kSrcATop))
        if "under" in light:
            tc, ta = light["under"]
            q = hexc(tc)
            g3 = lin_grad(0, -950, 0, -560, [(q[0], q[1], q[2], 0), (q[0], q[1], q[2], int(255 * ta))])
            c.drawPaint(gpaint(g3, skia.BlendMode.kSrcATop))

    # ------------------------------------------------------------------
    def _default_arms(self, P, prof):
        ph, amp = P["walk"], max(P["walk_amp"], P["run"])
        sw = math.sin(ph) * amp * (0.55 if P["run"] < 0.5 else 0.9)
        e = 0.15 + 0.9 * P["run"]
        if prof > 0.55:
            return [(sw, e), (-sw, e)]
        return [(0.08 + 0.02 * math.sin(P["t"] * 1.3), 0.12 + sw * 0.3),
                (0.08 + 0.02 * math.sin(P["t"] * 1.3 + 1), 0.12 - sw * 0.3)]

    def _default_legs(self, P):
        ph, amp = P["walk"], max(P["walk_amp"], P["run"] * 1.3)
        a = math.sin(ph) * 0.42 * amp
        k0 = max(0.0, math.sin(ph + 1.4)) * 0.7 * amp
        k1 = max(0.0, math.sin(ph + 1.4 + math.pi)) * 0.7 * amp
        return [(a, k0), (-a, k1)]

    # ------------------------------------------------------------------
    def _legs(self, c, legs, btr, face, back):
        L = self.L
        prof = abs(btr)
        hw = 50 * (1 - 0.75 * prof) * L.width
        order = [0, 1]
        for i in order:
            sgn = -1 if i == 0 else 1
            a, k = legs[i]
            hip = (sgn * hw + btr * 10, -445)
            fx = face if prof > 0.4 else 0.25 * sgn
            # thigh direction
            kx = hip[0] + math.sin(a) * 205 * (fx if prof > 0.4 else 0.6)
            ky = hip[1] + math.cos(a) * 205
            a2 = a - k
            ax = kx + math.sin(a2) * 200 * (fx if prof > 0.4 else 0.6)
            ay = ky + math.cos(a2) * 200
            if prof <= 0.4:
                # front view: walking shows as lifting the foot
                lift = max(0, -math.sin(a) * 1.2) * 40 + k * 40
                ay = min(ay, -40 - 0 + 0) if False else ay
                ay -= lift
                ky -= lift * 0.4
            far = (prof > 0.55 and ((face > 0 and i == 0) or (face < 0 and i == 1)))
            pc = L.pants_dark if far else L.pants
            pth = skia.Path()
            pth.moveTo(*hip)
            pth.lineTo(kx, ky)
            pth.lineTo(ax, ay - 30)
            p = paint(pc, stroke=92 * L.width)
            p.setStrokeCap(skia.Paint.kButt_Cap)
            c.drawPath(pth, p)
            # hem flare
            c.drawPath(path_poly([(ax - 49 * L.width, ay - 34), (ax + 49 * L.width, ay - 34),
                                  (ax + 52 * L.width, ay - 22), (ax - 52 * L.width, ay - 22)]),
                       paint(pc))
            # crease line
            c.drawLine(kx + 18 * (sgn if prof < 0.4 else 0), ky + 30, ax + 14 * (sgn if prof < 0.4 else 0), ay - 40,
                       paint(L.pants_dark if not far else shade(L.pants_dark, -0.3), 0.8, stroke=4))
            # shoe
            self._shoe(c, ax, ay, prof, face, sgn, far, back)

    def _shoe(self, c, x, y, prof, face, sgn, far, back):
        L = self.L
        w = lerp(118, 150, prof) * L.width
        fwd = (face * 22 * prof) if not back else (-face * 22 * prof)
        if prof < 0.4:
            fwd = sgn * 8
        x0 = x - w / 2 + fwd
        body = skia.Path()
        body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y - 42, w, 42), 20, 20))
        sc = shade(L.shoe, -0.25) if far else L.shoe
        c.drawPath(body, paint(sc))
        # toe cap
        if prof < 0.4 and not back:
            c.drawOval(skia.Rect.MakeXYWH(x0 + w * 0.18, y - 30, w * 0.64, 20), paint(shade(sc, 0.12)))
        elif not back:
            tx = x0 + (w * 0.62 if face > 0 else 0)
            c.drawOval(skia.Rect.MakeXYWH(tx, y - 30, w * 0.38, 22), paint(shade(sc, 0.12)))
        # laces
        if not back:
            for j in range(2):
                cx = x0 + w * (0.5 if prof < 0.4 else (0.6 if face > 0 else 0.4))
                c.drawLine(cx - 10, y - 36 + j * 7, cx + 10, y - 36 + j * 7, paint(shade(sc, -0.2), stroke=3))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0 - 2, y - 12, w + 4, 12), 6, 6),
                    paint(shade(L.sole, -0.2) if far else L.sole))

    # ------------------------------------------------------------------
    def _torso(self, c, btr, face, back, P):
        L = self.L
        prof = abs(btr)
        sh = lerp(100, 68, prof) * L.width
        hem = lerp(98, 74, prof) * L.width
        br = 1 + 0.006 * math.sin(P["t"] * 2.2) * P["breathe"]
        top = -660 * br
        off = btr * 6
        pts = [(-sh + off, top + 22), (-sh * 0.55 + off, top - 2), (sh * 0.55 + off, top - 2), (sh + off, top + 22),
               (sh * 1.03 + off, top + 120), (hem + off, -432), (hem * 0.98 + off, -412),
               (-hem * 0.98 + off, -412), (-hem + off, -432), (-sh * 1.03 + off, top + 120)]
        body = smooth_path(pts, True, 0.35)
        c.drawPath(body, paint(L.top))
        # shading on far side
        c.save()
        c.clipPath(body, doAntiAlias=True)
        d = 1 if btr >= 0 else -1
        sx = -d * sh
        g = lin_grad(sx, 0, sx + d * sh * 0.9, 0, [(0, 0, 0, 70), (0, 0, 0, 0)])
        c.drawRect(skia.Rect.MakeLTRB(-300, -800, 300, -380), gpaint(g))
        # hem band
        c.drawRect(skia.Rect.MakeLTRB(-300, -446, 300, -405), paint(L.top_trim))
        c.drawLine(-hem + off, -446, hem + off, -446, paint(shade(L.top_dark, -0.2), 0.6, stroke=3))
        # folds
        fc = paint(L.top_dark, 0.9, stroke=5)
        if not back:
            c.drawLine(-sh * 0.45 + off, -520, -sh * 0.2 + off, -470, fc)
            c.drawLine(sh * 0.5 + off, -560, sh * 0.25 + off, -500, fc)
        if L.top_style == "cardigan" and not back:
            cx = off + btr * 30
            c.drawLine(cx, top + 10, cx, -412, paint(L.top_dark, stroke=7))
            for j in range(4):
                c.drawCircle(cx + 12, -600 + j * 45, 6, paint("#e8dcc8"))
            # inner shirt V
            c.drawPath(path_poly([(cx - 40, top), (cx + 40, top), (cx, top + 90)]), paint("#e9e1d4"))
        if L.top_style == "shirt" and not back:
            cx = off + btr * 30
            c.drawPath(path_poly([(cx - 46, top - 2), (cx, top + 40), (cx + 46, top - 2), (cx + 30, top + 26),
                                  (cx, top + 46), (cx - 30, top + 26)]), paint(shade(L.top, 0.25)))
            c.drawLine(cx, top + 40, cx, -412, paint(L.top_dark, stroke=4))
            for j in range(4):
                c.drawCircle(cx, -590 + j * 45, 5, paint(shade(L.top, 0.35)))
        c.restore()
        # neckline rib
        if not back and L.top_style == "sweater":
            c.drawOval(skia.Rect.MakeLTRB(-48 + off + btr * 25, top - 10, 48 + off + btr * 25, top + 16),
                       paint(L.top_trim))
        self._top = top

    def _neck(self, c, btr):
        L = self.L
        top = getattr(self, "_top", -660)
        x = btr * 22
        c.drawRect(skia.Rect.MakeLTRB(x - 20, top - 45, x + 20, top + 4), paint(L.skin_shadow))

    # ------------------------------------------------------------------
    def _arm(self, c, i, ang, btr, face, P, far_side=False):
        L = self.L
        prof = abs(btr)
        sgn = -1 if i == 0 else 1
        a, e = ang
        top = getattr(self, "_top", -660)
        shx = lerp(88, 20, prof) * sgn * L.width + btr * 6
        if prof > 0.55:
            shx = (8 if far_side else -6) * face
        sh = (shx, top + 34)
        if prof > 0.55:
            fx = face
        else:
            fx = sgn
        ex = sh[0] + math.sin(a) * 160 * fx
        ey = sh[1] + math.cos(a) * 160
        if prof > 0.55:
            a2 = a + e
        else:
            a2 = a - e
        wx = ex + math.sin(a2) * 145 * fx
        wy = ey + math.cos(a2) * 145
        colr = L.top_dark if far_side else L.top
        pth = skia.Path()
        pth.moveTo(*sh)
        pth.lineTo(ex, ey)
        pth.lineTo(wx, wy)
        p = paint(colr, stroke=56 * L.width)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawPath(pth, p)
        # sleeve fold at elbow
        c.drawLine(ex - 14, ey - 4, ex + 12, ey + 6, paint(L.top_dark if not far_side else shade(L.top_dark, -0.3),
                                                          stroke=4))
        # cuff
        dx, dy = math.sin(a2) * fx, math.cos(a2)
        cx0, cy0 = wx - dx * 22, wy - dy * 22
        cp = paint(L.top_trim if not far_side else shade(L.top_trim, -0.25), stroke=60 * L.width)
        cp.setStrokeCap(skia.Paint.kButt_Cap)
        c.drawLine(cx0, cy0, wx + dx * 4, wy + dy * 4, cp)
        # hand
        hx, hy = wx + dx * 30, wy + dy * 30
        sk = L.skin_shadow if far_side else L.skin
        if P.get("hold_phone") and i == 1 and not far_side:
            self._phone_in_hand(c, hx, hy, P)
        c.drawCircle(hx, hy, 29, paint(sk))
        c.drawCircle(hx - 6, hy - 8, 11, paint(shade(sk, 0.08), 0.6))

    def _phone_in_hand(self, c, hx, hy, P):
        c.save()
        c.translate(hx, hy - 40)
        c.rotate(-8)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-42, -78, 84, 150), 12, 12), paint("#0b0b0e"))
        g = P.get("phone_glow", 0.0)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-36, -72, 72, 138), 8, 8),
                    paint(mix("#1b2133", "#bfe6ff", g)))
        c.restore()

    # ------------------------------------------------------------------
    def _hair_points(self, cx, cy, r, tr, t, wind, back=False):
        L = self.L
        pts = []
        style = L.hair_style
        if style == "messy":
            n = 11
            a0 = math.radians(188 - 24 * max(0, tr) + 8 * max(0, -tr))
            a1 = math.radians(352 + 24 * max(0, -tr) - 8 * max(0, tr))
            if back:
                a0, a1 = math.radians(150), math.radians(390)
            lean = 0.16 - 0.10 * tr
            for j in range(n):
                u = j / (n - 1)
                ang = lerp(a0, a1, u)
                jj = self.tufts[j]
                # valley then a leaning tip -> windswept, uneven tufts
                pts.append((cx + math.cos(ang) * r * (1.03 + 0.03 * jj[0]),
                            cy + math.sin(ang) * r * (1.03 + 0.03 * jj[0])))
                if j < n - 1:
                    sway = (math.sin(t * 2.1 + jj[2]) * 0.035 + vnoise(t * 0.8 + j, 3) * 0.03) * wind
                    ta = ang + (a1 - a0) / (n - 1) * 0.5 + lean + sway + 0.08 * jj[0]
                    rr = r * (1.12 + 0.11 * jj[1] * (1.15 if 2 < j < 8 else 0.75))
                    pts.append((cx + math.cos(ta) * rr, cy + math.sin(ta) * rr))
            if back:
                for j in range(7):
                    u = j / 6
                    x = lerp(cx + r * 0.97, cx - r * 0.97, u)
                    y = cy + r * (0.70 if j % 2 == 0 else 0.52) - abs(u - 0.5) * r * 0.55
                    pts.append((x, y))
                return pts
            # side lock (right), fringe, side lock (left)
            pts.append((cx + r * 1.03, cy + r * 0.02))
            pts.append((cx + r * 0.90, cy - r * 0.12))
            nf = 7
            xr = cx + r * (0.86 - 0.12 * max(0, -tr)) + tr * r * 0.10
            xl = cx - r * (0.86 - 0.12 * max(0, tr)) + tr * r * 0.10
            for j in range(nf + 1):
                u = j / nf
                x = lerp(xr, xl, u)
                tipj = j % 2 == 1
                sway = math.sin(t * 1.9 + j) * r * 0.012 * wind
                if tipj:
                    y = cy - r * (0.27 + 0.05 * self.tufts[20 + j][1]) + r * 0.03 * math.sin(u * 3.1)
                    x += -r * 0.07 + sway
                else:
                    y = cy - r * (0.46 + 0.04 * self.tufts[20 + j][0])
                pts.append((x, y))
            pts.append((cx - r * 0.92, cy - r * 0.14))
            pts.append((cx - r * 1.03, cy + r * 0.0))
            return pts
        if style == "short":
            n = 12
            for j in range(n + 1):
                ang = lerp(math.radians(192), math.radians(348), j / n)
                rr = r * (1.07 if j % 2 else 1.11)
                pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
            pts.append((cx + r * 0.95, cy - r * 0.32))
            for j in range(6):
                u = j / 5
                pts.append((lerp(cx + r * 0.85, cx - r * 0.85, u) + tr * r * 0.15,
                            cy - r * (0.52 + 0.06 * (j % 2)) - math.sin(u * math.pi) * r * 0.08))
            pts.append((cx - r * 0.95, cy - r * 0.32))
            return pts
        if style == "bob":
            n = 16
            for j in range(n + 1):
                ang = lerp(math.radians(140), math.radians(400), j / n)
                rr = r * (1.16 + 0.02 * math.sin(j * 1.7))
                if math.sin(ang) > 0.3:
                    rr *= 1.05
                pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr + (r * 0.25 if math.sin(ang) > 0.5 else 0)))
            pts.append((cx + r * 0.80, cy + r * 0.45))
            pts.append((cx + r * 0.88, cy - r * 0.10))
            for j in range(7):
                u = j / 6
                pts.append((lerp(cx + r * 0.75, cx - r * 0.75, u) + tr * r * 0.15,
                            cy - r * (0.30 + 0.05 * (j % 2)) - math.sin(u * math.pi) * r * 0.12 + u * r * 0.08))
            pts.append((cx - r * 0.88, cy - r * 0.05))
            pts.append((cx - r * 0.80, cy + r * 0.45))
            return pts
        return pts

    def _head(self, c, P):
        L = self.L
        r = L.head_r
        tr = clamp(P["tr"], -1, 1)
        t = P["t"]
        cx, cy = tr * 8, -800
        c.save()
        c.translate(cx, cy + r * 0.9)
        c.rotate(P["tilt"])
        c.translate(-cx, -(cy + r * 0.9))
        # back hair (bob)
        if L.hair_style == "bob":
            c.drawOval(skia.Rect.MakeLTRB(cx - r * 1.22, cy - r * 1.1, cx + r * 1.22, cy + r * 1.15), paint(L.hair))
        # face
        c.drawCircle(cx, cy, r, paint(L.skin))
        # face shading (form)
        g = rad_grad(cx - r * 0.35 + tr * r * 0.3, cy - r * 0.4, r * 1.5,
                     [(255, 235, 210, 40), (0, 0, 0, 0), (60, 30, 20, 60)], [0, 0.55, 1])
        c.drawCircle(cx, cy, r, gpaint(g))
        if L.stubble:
            c.save()
            c.clipPath(self._circle_path(cx, cy, r))
            c.drawOval(skia.Rect.MakeLTRB(cx - r * 0.75 + tr * r * 0.3, cy + r * 0.25, cx + r * 0.75 + tr * r * 0.3, cy + r * 1.2),
                       paint("#6b4a3a", 0.22))
            c.restore()
        self._face(c, cx, cy, r, tr, P)
        # hair
        hp = self._hair_points(cx, cy, r, tr, t, P["wind"])
        hpath = smooth_path(hp, True, 0.42)
        c.drawPath(hpath, paint(L.hair))
        # hair sheen / strands
        c.save()
        c.clipPath(hpath, doAntiAlias=True)
        g2 = rad_grad(cx - r * 0.3, cy - r * 0.9, r * 0.9, [hexc(L.hair_hi, 200), hexc(L.hair_hi, 0)])
        c.drawCircle(cx - r * 0.3, cy - r * 0.9, r * 0.9, gpaint(g2))
        sp = paint(shade(L.hair_hi, 0.08), 0.55, stroke=4)
        for j in range(4):
            q = skia.Path()
            x0 = cx - r * 0.55 + j * r * 0.32 + tr * r * 0.1
            q.moveTo(x0, cy - r * 1.0)
            q.quadTo(x0 + r * 0.18, cy - r * 0.78, x0 + r * 0.06, cy - r * 0.52)
            c.drawPath(q, sp)
        c.restore()
        if L.glasses:
            self._glasses(c, cx, cy, r, tr)
        c.restore()

    def _circle_path(self, x, y, r):
        p = skia.Path()
        p.addCircle(x, y, r)
        return p

    def _head_back(self, c, P):
        L = self.L
        r = L.head_r
        t = P["t"]
        cx, cy = 0, -800
        c.save()
        c.translate(cx, cy + r * 0.9)
        c.rotate(P["tilt"])
        c.translate(-cx, -(cy + r * 0.9))
        c.drawCircle(cx, cy, r, paint(L.skin_shadow))
        hp = self._hair_points(cx, cy, r, 0, t, P["wind"], back=True)
        hpath = smooth_path(hp, True, 0.42)
        c.drawPath(hpath, paint(L.hair))
        c.save()
        c.clipPath(hpath, doAntiAlias=True)
        g2 = rad_grad(cx, cy - r * 0.7, r, [hexc(L.hair_hi, 170), hexc(L.hair_hi, 0)])
        c.drawCircle(cx, cy - r * 0.7, r, gpaint(g2))
        for j in range(7):
            a = math.radians(200 + j * 20)
            c.drawLine(cx + math.cos(a) * r * 0.2, cy - r * 0.1 + math.sin(a) * r * 0.2,
                       cx + math.cos(a) * r * 1.0, cy + math.sin(a) * r * 1.0, paint(L.hair_hi, 0.55, stroke=4))
        c.restore()
        c.restore()

    def _glasses(self, c, cx, cy, r, tr):
        sep = r * 0.33 * (1 - 0.35 * abs(tr))
        fx = cx + tr * r * 0.42
        ey = cy + r * 0.05
        p = paint("#2a2420", stroke=7)
        for s in (-1, 1):
            if abs(tr) > 0.7 and s == (-1 if tr > 0 else 1):
                continue
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(fx + s * sep - r * 0.21, ey - r * 0.17, r * 0.42, r * 0.32), 12, 12), p)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(fx + s * sep - r * 0.21, ey - r * 0.17, r * 0.42, r * 0.32), 12, 12),
                        paint("#cfe8ff", 0.10))
        c.drawLine(fx - sep + r * 0.21, ey - r * 0.05, fx + sep - r * 0.21, ey - r * 0.05, p)

    def _face(self, c, cx, cy, r, tr, P):
        L = self.L
        e = EXPR.get(P["expr"], EXPR["neutral"])
        bang, by, etype, mouth, sweat = e
        if P["sweat"] is not None:
            sweat = P["sweat"]
        sq = 1 - 0.38 * abs(tr)
        fx = cx + tr * r * 0.46
        sep = r * 0.31 * sq
        ey = cy + r * 0.06
        lx, ly = P["look"]
        blink = clamp(P["blink"])
        for s in (-1, 1):
            # far eye hidden in profile
            far = (tr > 0 and s < 0) or (tr < 0 and s > 0)
            if abs(tr) > 0.82 and far:
                continue
            k = 1.0 - (0.25 * abs(tr) if far else 0)
            ex = fx + s * sep * (0.82 if far else 1.0)
            self._eye(c, ex, ey, r, k, etype, blink, lx, ly, s, P)
            # brows
            if bang == "asym":
                ang, yo = (0.18 if s < 0 else -0.25), (0.02 if s < 0 else -0.10)
            else:
                ang, yo = bang, by
            yo += P["brow_extra"]
            bw = r * 0.19 * k
            byy = ey - r * (0.30 - yo)
            inner = -s  # inner end towards face centre
            dy = ang * r * 0.35
            x1, x2 = ex - bw, ex + bw
            y1 = byy + (dy if inner < 0 else -dy) * 0.5
            y2 = byy + (dy if inner > 0 else -dy) * 0.5
            bp = paint(L.brow, stroke=r * 0.075)
            bpath = skia.Path()
            bpath.moveTo(x1, y1)
            bpath.quadTo(ex, byy - r * 0.035, x2, y2)
            c.drawPath(bpath, bp)
        # mouth
        mx = fx + tr * r * 0.05
        my = cy + r * 0.52
        op = clamp(P["mouth"])
        if op > 0.04:
            self._mouth_open(c, mx, my, r, op, sq)
        elif mouth == "o":
            c.drawOval(skia.Rect.MakeLTRB(mx - r * 0.07, my - r * 0.06, mx + r * 0.07, my + r * 0.10), paint("#3a1418"))
        elif mouth == "open":
            self._mouth_open(c, mx, my, r, 0.55, sq)
        elif mouth == "wide":
            self._mouth_open(c, mx, my, r, 0.95, sq)
        elif mouth == "frown":
            p = skia.Path()
            p.moveTo(mx - r * 0.13 * sq, my + r * 0.06)
            p.quadTo(mx, my - r * 0.05, mx + r * 0.13 * sq, my + r * 0.06)
            c.drawPath(p, paint("#3a1a14", stroke=r * 0.045))
        elif mouth == "flat":
            c.drawLine(mx - r * 0.1 * sq, my, mx + r * 0.1 * sq, my, paint("#3a1a14", stroke=r * 0.04))
        elif mouth == "smirk":
            p = skia.Path()
            p.moveTo(mx - r * 0.12 * sq, my + r * 0.01)
            p.quadTo(mx + r * 0.02, my + r * 0.05, mx + r * 0.15 * sq, my - r * 0.05)
            c.drawPath(p, paint("#3a1a14", stroke=r * 0.04))
        elif mouth == "squiggle":
            p = skia.Path()
            p.moveTo(mx - r * 0.13 * sq, my)
            p.cubicTo(mx - r * 0.05, my - r * 0.06, mx + r * 0.03, my + r * 0.06, mx + r * 0.13 * sq, my - r * 0.01)
            c.drawPath(p, paint("#3a1a14", stroke=r * 0.04))
        if L.lip and op <= 0.04 and mouth in ("none", "flat"):
            c.drawLine(mx - r * 0.09, my, mx + r * 0.09, my, paint(L.lip, stroke=r * 0.05))
        if sweat:
            sx = fx + (r * 0.62 if tr <= 0.3 else -r * 0.62) * 1
            sy = cy - r * 0.12 + (P["t"] * 40 % 30) * 0.3
            dp = skia.Path()
            dp.moveTo(sx, sy - r * 0.16)
            dp.cubicTo(sx + r * 0.10, sy, sx + r * 0.08, sy + r * 0.1, sx, sy + r * 0.1)
            dp.cubicTo(sx - r * 0.08, sy + r * 0.1, sx - r * 0.10, sy, sx, sy - r * 0.16)
            c.drawPath(dp, paint("#9fd3f2", 0.85 * clamp(sweat)))
            c.drawCircle(sx - r * 0.02, sy + r * 0.02, r * 0.025, paint("#ffffff", 0.8 * clamp(sweat)))

    def _eye(self, c, ex, ey, r, k, etype, blink, lx, ly, s, P):
        L = self.L
        ew, eh = r * 0.088 * k, r * 0.135
        if etype == "white":
            R = r * 0.17 * k
            if blink > 0.5:
                c.drawLine(ex - R, ey, ex + R, ey, paint(L.eye, stroke=r * 0.04))
                return
            hh = R * (1 - blink)
            c.drawOval(skia.Rect.MakeLTRB(ex - R, ey - hh, ex + R, ey + hh), paint("#fbfbf6"))
            c.drawOval(skia.Rect.MakeLTRB(ex - R, ey - hh, ex + R, ey + hh), paint("#1a1a1a", stroke=r * 0.025))
            pr = R * 0.42
            px, py = ex + lx * R * 0.4, ey + ly * R * 0.35
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(ex - R, ey - hh, ex + R, ey + hh))
            c.drawCircle(px, py, pr, paint(L.eye))
            c.drawCircle(px - pr * 0.3, py - pr * 0.35, pr * 0.28, paint("#ffffff"))
            c.restore()
            return
        cx = ex + lx * r * 0.05
        cy = ey + ly * r * 0.05
        hh = eh * (1 - blink)
        if hh < eh * 0.15:
            c.drawLine(cx - ew * 1.1, cy + eh * 0.2, cx + ew * 1.1, cy + eh * 0.2, paint(L.eye, stroke=r * 0.04))
            return
        rect = skia.Rect.MakeLTRB(cx - ew, cy - hh, cx + ew, cy + hh)
        c.drawOval(rect, paint(L.eye))
        # highlight
        c.drawCircle(cx - ew * 0.25, cy - hh * 0.45, ew * 0.32, paint("#ffffff", 0.85))
        if P["eye_glint"] > 0:
            c.drawCircle(cx + ew * 0.3, cy + hh * 0.3, ew * 0.22, paint("#9fe9ff", P["eye_glint"]))
        if etype in ("lid", "lid2"):
            # heavy upper lid -> calm, knowing look
            lid = 0.45 if etype == "lid" else 0.55
            ytop = cy - hh + 2 * hh * lid
            c.drawRect(skia.Rect.MakeLTRB(cx - ew * 1.6, cy - hh * 1.6, cx + ew * 1.6, ytop), paint(L.skin))
            c.drawLine(cx - ew * 1.45, ytop, cx + ew * 1.45, ytop, paint(L.eye, stroke=r * 0.045))

    def _mouth_open(self, c, mx, my, r, op, sq):
        w = r * (0.10 + 0.05 * op) * sq
        h = r * (0.03 + 0.20 * op)
        rect = skia.Rect.MakeLTRB(mx - w, my - h * 0.35, mx + w, my + h * 0.65)
        c.drawOval(rect, paint("#3b1216"))
        c.save()
        pth = skia.Path()
        pth.addOval(rect)
        c.clipPath(pth, doAntiAlias=True)
        c.drawOval(skia.Rect.MakeLTRB(mx - w * 0.7, my + h * 0.25, mx + w * 0.7, my + h * 0.95), paint("#c45d63"))
        if op > 0.3:
            c.drawRect(skia.Rect.MakeLTRB(mx - w, my - h * 0.35, mx + w, my - h * 0.18), paint("#f2efe6"))
        c.restore()
