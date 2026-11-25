"""HUMAN MIND — Episode 01 'The Power of Small Habits': scenes, titles, subtitles, compositor."""
import math
import re
import numpy as np
from hm_core import *  # noqa

TXT = {
    "ru": dict(
        week=["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"],
        book="«АТОМНЫЕ ПРИВЫЧКИ» · ДЖЕЙМС КЛИР",
        start_small="НАЧНИ С МАЛОГО",
        add1="МАЛЕНЬКИЕ ДЕЙСТВИЯ", add2="ПОВТОРЯЕМЫЕ ПОСТОЯННО",
        identity="ФОРМИРУЙ СВОЮ ЛИЧНОСТЬ",
        q1="КАКОЕ МАЛЕНЬКОЕ ДЕЙСТВИЕ", q2="ТЫ НАЧНЁШЬ СЕГОДНЯ?",
        day="ДЕНЬ", evening="1 ВЕЧЕР", hours="2 ЧАСА", minutes="5 МИНУТ", today="СЕГОДНЯ",
        keys=["маленьк* действ*", "небольш* действ*", "привычк*", "повтор*", "каждый день",
              "прогресс*", "другим человеком", "шаг"],
    ),
    "en": dict(
        week=["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"],
        book="ATOMIC HABITS · JAMES CLEAR",
        start_small="START SMALL",
        add1="SMALL ACTIONS", add2="REPEATED CONSISTENTLY",
        identity="BUILD YOUR IDENTITY",
        q1="WHAT SMALL ACTION", q2="WILL YOU START TODAY?",
        day="DAY", evening="1 EVENING", hours="2 HOURS", minutes="5 MINUTES", today="TODAY",
        keys=["small actions", "habit*", "repeat*", "repetition", "every day", "progress",
              "different person", "step"],
    ),
}

END = 116.0          # total length (s) — matches the natural end of the music
DIP = 0.32           # half-length of dip-to-dark transitions


class Cues:
    def __init__(self, d, lang):
        self.lang = lang
        self.T = TXT[lang]
        self.sent = d["sentences"]
        self.SC = d["scenes"] + [END]
        self.vo_end = d["voice_end"]
        self.S = [s["start"] for s in self.sent]
        self.E = [s["end"] for s in self.sent]
        # sub-shot cuts inside scene 3
        self.shots3 = [self.SC[2], self.S[7] - 0.2, self.S[8] - 0.25, self.S[9] - 0.2,
                       self.S[10] - 0.25, self.S[11] - 0.2, self.S[12] - 0.25, self.SC[3]]
        self.cuts = self.SC[1:6] + self.shots3[1:-1]
        self.subs = build_subs(self)


# ====================================================================== subtitles
def _norm(w):
    return re.sub(r"[^\wё']", "", w.lower())


def _kw_mask(tokens, keys):
    n = [_norm(t) for t in tokens]
    mask = [False] * len(n)
    for k in keys:
        parts = k.split()
        for i in range(len(n) - len(parts) + 1):
            ok = True
            for j, p in enumerate(parts):
                w = n[i + j]
                if p.endswith("*"):
                    ok &= w.startswith(p[:-1])
                else:
                    ok &= w == p
            if ok and not (i > 0 and n[i - 1] in ("atomic", "атомные")):
                for j in range(len(parts)):
                    mask[i + j] = True
    return mask


STOP = set("и в с по на за к о а но что не из до для от у ты как так a the to of in and for on at your you that is are be with from it an or хотя".split())


def split_chunks(ws, maxc):
    toks = [w[0] for w in ws]
    n = len(toks)
    ln = lambda i, j: len(" ".join(toks[i:j]))
    total = ln(0, n)
    if total <= maxc:
        return [ws]
    k = math.ceil(total / maxc)
    target = total / k
    best = [0.0] + [1e9] * n
    prev = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(j - 1, -1, -1):
            L = ln(i, j)
            if L > maxc + 3:
                break
            c = ((L - target) / 8) ** 2
            if j < n:
                last = toks[j - 1]
                if re.search(r"[.!?:;]$", last):
                    c -= 4
                elif re.search(r"[,—]$", last):
                    c -= 2.5
                if _norm(last) in STOP or len(_norm(last)) <= 2:
                    c += 8
                if last[:1].isupper() and toks[j][:1].isupper():
                    c += 10
            if L < 12:
                c += 6
            if best[i] + c < best[j]:
                best[j] = best[i] + c
                prev[j] = i
    cuts, j = [], n
    while j > 0:
        cuts.append((prev[j], j))
        j = prev[j]
    return [ws[a:b] for a, b in reversed(cuts)]


def build_subs(C, maxc=40):
    out = []
    for si, s in enumerate(C.sent):
        if si == len(C.sent) - 1:      # the final question is shown as a title card instead
            continue
        words = s["words"]
        mask = _kw_mask([w[0] for w in words], C.T["keys"])
        chunks = split_chunks([w + [mask[i]] for i, w in enumerate(words)], maxc)
        nxt = C.S[si + 1] if si + 1 < len(C.S) else C.vo_end + 2
        for ci, ch in enumerate(chunks):
            a = ch[0][1] - 0.08
            b = ch[-1][2] + 0.35
            if ci + 1 < len(chunks):
                b = min(b, chunks[ci + 1][0][1] - 0.1)
            else:
                b = min(b + 0.25, nxt - 0.12)
            out.append(dict(a=a, b=b, words=[(w[0], w[3]) for w in ch]))
    # make consecutive cues continuous when gaps are tiny (less flicker)
    for i in range(len(out) - 1):
        if 0 < out[i + 1]["a"] - out[i]["b"] < 0.3:
            out[i]["b"] = out[i + 1]["a"] - 0.02
    return out


def srt(C, path):
    def ts(x):
        ms = int(round(x * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    with open(path, "w", encoding="utf-8") as f:
        n = 0
        for s in C.subs:
            n += 1
            f.write(f"{n}\n{ts(s['a'])} --> {ts(s['b'])}\n{' '.join(w for w, _ in s['words'])}\n\n")
        q = C.sent[-1]
        n += 1
        f.write(f"{n}\n{ts(q['start'] - 0.08)} --> {ts(q['end'] + 1.2)}\n{q['text']}\n\n")


def draw_subs(ctx, C, t):
    for s in C.subs:
        if s["a"] <= t <= s["b"]:
            al = min(prog(t, s["a"], s["a"] + 0.14, sm), 1 - prog(t, s["b"] - 0.14, s["b"], sm))
            size = 42
            parts = []
            total = 0
            for i, (w, k) in enumerate(s["words"]):
                font(ctx, size, "Inter Bold" if k else "Inter Medium")
                ww = ctx.text_extents(w).x_advance
                sp = ctx.text_extents(" ").x_advance * 1.05 if i else 0
                parts.append((w, k, ww, sp))
                total += ww + sp
            x = W / 2 - total / 2
            y = 1000
            for w, k, ww, sp in parts:
                x += sp
                font(ctx, size, "Inter Bold" if k else "Inter Medium")
                ctx.move_to(x, y)
                ctx.set_source_rgba(1, 1, 1, al * (1.0 if k else 0.84))
                ctx.show_text(w)
                if k:  # thin luminous underline on key words
                    ctx.move_to(x + 2, y + 10)
                    ctx.line_to(x + ww - 2, y + 10)
                    ctx.set_line_width(2.5)
                    ctx.set_source_rgba(1, 1, 1, 0.75 * al)
                    ctx.stroke()
                x += ww
            return True
    return False


def title(ctx, s, y, t, a, b, size=54, weight="Inter SemiBold", tracking=10, rise=14):
    al = window(t, a, b, 0.6, 0.6)
    if al <= 0:
        return
    dy = (1 - eout((t - a) / 0.9)) * rise
    trk = tracking + (1 - eout((t - a) / 1.6)) * tracking * 0.8
    draw_text(ctx, s, W / 2, y + dy, size, weight, "c", trk, (1, 1, 1, al))


# ====================================================================== scenes
SX0, SY0, SN, SW, SH = 0.0, 0.0, 14, 95.0, 58.0
ORB = (SX0 + SN * SW + 150, SY0 - SN * SH - 170)


def scene1(ctx, ui, t, C):
    S, E = C.S, C.E
    t2 = S[2]
    cam = cam_blend([(0, (440, -440, 0.70)), (t2 - 0.2, (520, -480, 0.76)),
                     (t2 + 2.6, (-20, -190, 1.06)), (C.SC[1] + 0.4, (0, -200, 1.2))], t)
    apply_cam(ctx, *cam[:3])
    lit = [prog(t, t2 + 2.6, t2 + 3.2, sm)] + [0.0] * (SN - 1)
    # ambient light around characters + the goal
    light_pool(ctx, -120, -120, 520, 0.05)
    dashed_ground(ctx, -2600, 3200)
    draw_stairs(ctx, SX0, SY0, SN, SW, SH, lit=lit)
    orb(ctx, *ORB, 16, t)
    # dream icons — what life could look like a year from now
    kinds = ["bulb", "book", "check", "star"]
    d2 = E[1] - S[1]
    fade = 1 - prog(t, t2 - 0.1, t2 + 0.6, sm)
    for i, k in enumerate(kinds):
        ta = S[1] + d2 * (0.05 + 0.25 * i)
        p = prog(t, ta, ta + 0.6, back)
        if t < ta or fade <= 0:
            continue
        x, y = ORB[0] - 860 + i * 200, ORB[1] - 10 - 30 * math.sin(i * 1.3)
        ctx.move_to(ORB[0] - 30, ORB[1])
        ctx.line_to(lerp(ORB[0] - 30, x + 60, min(1, p)), lerp(ORB[1], y, min(1, p)))
        ctx.set_dash([4, 10])
        stroke(ctx, 2, 1, 0.25 * fade * min(1, p))
        ctx.set_dash([])
        light_pool(ctx, x, y, 100, 0.13 * fade * min(1, p))
        icon(ctx, k, x, y, 100 * p, fade * min(1, p), lw=6)
    # character A: hesitates and walks away
    xa, xb = -200.0, -60.0
    tA = t - t2
    look_up = dict(lean=-0.07, head=-0.32)
    if tA < 0:
        PA = stand(xa, t=t, **look_up)
    elif tA < 1.6:
        u = prog(tA, 0, 0.9)
        v = prog(tA, 0.9, 1.5)
        PA = stand(xa - 16 * v, t=t, lean=lerp(-0.07, 0.2, u), head=lerp(-0.32, 0.6, u),
                   arm_n=(lerp(0.1, 0.02, u), 0.05), arm_f=(-0.04, 0.05))
        PA["foot_f"] = (xa - 9 - 34 * v, 0)
    else:
        tu = prog(tA, 1.6, 1.95)
        if tu < 1:  # turning around: squash through zero width
            face = math.cos(math.pi * tu)
            face = face if abs(face) > 0.1 else math.copysign(0.1, face if face else -1)
            PA = stand(xa - 16, face=face, t=t, lean=0.2, head=0.6)
        else:
            F = flat_holds(xa - 16, 40, 62, face=-1)
            s = max(0.0, (tA - 1.95) * 1.55)
            PA = walk_pose(F, s, face=-1, lean=0.16, head=0.5, swing=0.22)
    fadeA = clamp(1 - (abs(PA["x"] - xa) - 60) / 420)
    draw_figure(ctx, PA, alpha=0.25 + 0.75 * fadeA)
    # character B: takes one small step
    tB = t - t2
    if tB < 1.2:
        PB = stand(xb, t=t + 0.7, **look_up) if tB < 0.6 else stand(
            xb, t=t + 0.7, lean=lerp(-0.07, 0.06, prog(tB, 0.6, 1.2)), head=lerp(-0.32, 0.0, prog(tB, 0.6, 1.2)))
    else:
        st0 = stair_top(SX0, SY0, SW, SH, 0)
        F = [(xb + 9, 0), (xb - 9, 0), (st0[0] - 14, st0[1]), (st0[0] + 6, st0[1])]
        s = 2 * prog(tB, 1.4, 3.1)
        PB = walk_pose(F, s, lean=0.08, head=-0.05, lift=26, swing=0.3)
        if s >= 2:
            PB["y"] += math.sin(t * 1.7) * 1.0
    draw_figure(ctx, PB)
    return cam, 1.0


def calendar(ctx, cx, cy, w, h, wd, num, circled=0.0, a=1.0, mon=False):
    x, y = cx - w / 2, cy - h / 2
    rrect(ctx, x, y, w, h, 10)
    ctx.set_source_rgba(0.04, 0.04, 0.04, a)
    ctx.fill_preserve()
    stroke(ctx, 3, 1, 0.95 * a)
    rrect(ctx, x, y, w, 48, 10)
    ctx.rectangle(x, y + 30, w, 18)
    ctx.set_source_rgba(1, 1, 1, 0.95 * a)
    ctx.fill()
    draw_text(ctx, wd, cx, y + 33, 19 if len(wd) < 10 else 16, "Inter Bold", "c", 1.5, (0.05, 0.05, 0.05, a))
    draw_text(ctx, str(num), cx, cy + 62, 104, "Inter SemiBold", "c", 0, (1, 1, 1, a))
    for sx in (-0.28, 0.28):
        ctx.new_sub_path(); ctx.arc(cx + sx * w, y - 4, 7, 0, 6.2832)
        stroke(ctx, 3, 1, a)
    if circled > 0:
        ctx.save()
        ctx.translate(cx, cy + 26)
        ctx.scale(1.0, 0.82)
        ctx.new_sub_path(); ctx.arc(0, 0, 74, -2.2, -2.2 + 6.6 * circled)
        ctx.restore()
        stroke(ctx, 4, 1, a)


def flip_times(C):
    flips = []
    tt, dt = C.S[4] + 0.15, 0.85
    while tt < C.SC[2] - 0.5:
        flips.append(tt)
        tt += dt
        dt = max(0.14, dt * 0.84)
    return flips


def scene2(ctx, ui, t, C):
    S, E = C.S, C.E
    a0, b0 = C.SC[1], C.SC[2]
    cam = cam_blend([(a0, (160, -215, 1.32, 0.0)), (b0, (150, -250, 1.55, -0.018))], t)
    apply_cam(ctx, cam[0], cam[1], cam[2], cam[3])
    # flips accelerate as weeks go by
    flips = flip_times(C)
    nflip = sum(1 for f in flips if f <= t)
    dim = 1 - 0.28 * prog(t, S[4], b0, sm)
    light_pool(ctx, 80, -160, 560, 0.06 * dim)
    ctx.move_to(-700, 0)
    ctx.line_to(1000, 0)
    stroke(ctx, 2.5, 1, 0.5)
    # desk & chair
    ctx.move_to(-5, -98); ctx.line_to(360, -98); stroke(ctx, 6, 1, 0.95)
    for lx in (14, 340):
        ctx.move_to(lx, -98); ctx.line_to(lx, 0); stroke(ctx, 4, 1, 0.8)
    ctx.move_to(-110, -56); ctx.line_to(-28, -56); stroke(ctx, 5, 0.75)
    ctx.move_to(-104, -56); ctx.line_to(-104, 0); ctx.move_to(-34, -56); ctx.line_to(-34, 0)
    ctx.move_to(-108, -56); ctx.line_to(-116, -200); stroke(ctx, 4, 0.6)
    # props: closed book, checklist, rolled mat
    hl = lambda k: window(t, S[5] + (E[5] - S[5]) * (0.12 + 0.28 * k), S[5] + (E[5] - S[5]) * (0.12 + 0.28 * k) + 1.6, 0.3, 0.8)
    light_pool(ctx, 255, -108, 120, 0.18 * hl(0))
    book_closed(ctx, 255, -102)
    book_closed(ctx, 262, -120, 86, 16, 0.8)
    clx, cly = 440, -330
    light_pool(ctx, clx, cly, 150, 0.18 * hl(2))
    rrect(ctx, clx - 60, cly - 80, 120, 160, 8); ctx.set_source_rgba(0.04, 0.04, 0.04, 1); ctx.fill_preserve()
    stroke(ctx, 2.5, 1, 0.85)
    for i in range(4):
        yy = cly - 50 + i * 34
        rrect(ctx, clx - 42, yy - 9, 18, 18, 3); stroke(ctx, 2, 1, 0.8)
        ctx.move_to(clx - 12, yy); ctx.line_to(clx + 40 - (i % 2) * 14, yy); stroke(ctx, 3, 1, 0.35)
    mx = 560
    light_pool(ctx, mx, -30, 130, 0.18 * hl(1))
    ctx.new_sub_path(); ctx.arc(mx, -28, 28, 0, 6.2832); stroke(ctx, 3, 1, 0.85)
    ctx.new_sub_path(); ctx.arc(mx, -28, 16, 0, 6.2832); stroke(ctx, 2, 1, 0.5)
    ctx.new_sub_path(); ctx.arc(mx, -28, 6, 0, 6.2832); stroke(ctx, 2, 1, 0.4)
    ctx.move_to(mx + 28, -2); ctx.line_to(mx + 140, -2); stroke(ctx, 4, 1, 0.6)
    # calendar
    ccx, ccy, cw, ch = 180, -370, 210, 230
    week = C.T["week"]
    cur = nflip
    d4 = E[3] - S[3]
    circ0 = prog(t, S[3] + d4 * 0.86, S[3] + d4 * 0.86 + 0.7)
    def circ_for(i, t_rev):
        if i == 0:
            return circ0
        return prog(t, t_rev + 0.05, t_rev + 0.4) if i % 7 == 0 else 0.0
    t_rev = flips[cur - 1] if cur else 0
    calendar(ctx, ccx, ccy, cw, ch, week[cur % 7], cur + 1, circ_for(cur, t_rev))
    if cur > 0:   # last torn page falls away
        u = (t - flips[cur - 1]) / 0.55
        if u < 1:
            ctx.save()
            ctx.translate(ccx - cw / 2, ccy - ch / 2)
            ctx.rotate(-0.9 * ein(u) - 0.2 * u)
            ctx.translate(-30 * u, 260 * ein(u))
            ctx.translate(-(ccx - cw / 2), -(ccy - ch / 2))
            pc = cur - 1
            calendar(ctx, ccx, ccy, cw, ch, week[pc % 7], pc + 1, circ_for(pc, flips[pc - 1] if pc else 0), 1 - u)
            ctx.restore()
    # thought bubble: something grandiose
    tb = window(t, S[3] + 0.4, S[3] + d4 * 0.62, 0.5, 0.6)
    if tb > 0:
        for i, (bx, by, br) in enumerate([(-38, -230, 6), (-60, -262, 10), (-92, -300, 14)]):
            ctx.new_sub_path(); ctx.arc(bx, by, br, 0, 6.2832); stroke(ctx, 2.5, 1, tb * prog(t, S[3] + 0.4 + i * 0.15, S[3] + 0.7 + i * 0.15))
        cx0, cy0 = -190, -400
        ctx.save(); ctx.translate(cx0, cy0); ctx.scale(1.5, 1.0)
        ctx.new_sub_path(); ctx.arc(0, 0, 72, 0, 6.2832); ctx.restore()
        ctx.set_source_rgba(0.03, 0.03, 0.03, tb); ctx.fill_preserve(); stroke(ctx, 2.5, 1, 0.9 * tb)
        mp = prog(t, S[3] + 1.0, S[3] + 2.6)
        pts = [(-80, 40), (-30, -20), (-5, 5), (30, -45), (80, 40)]
        ctx.move_to(cx0 + pts[0][0], cy0 + pts[0][1])
        n = int(mp * 4)
        for i in range(1, n + 1):
            ctx.line_to(cx0 + pts[i][0], cy0 + pts[i][1])
        if n < 4:
            f = mp * 4 - n
            p, q = pts[n], pts[n + 1]
            ctx.line_to(cx0 + lerp(p[0], q[0], f), cy0 + lerp(p[1], q[1], f))
        stroke(ctx, 3, 1, tb)
        if mp >= 1:
            fx, fy = cx0 + 30, cy0 - 45
            ctx.move_to(fx, fy); ctx.line_to(fx, fy - 30); ctx.line_to(fx + 18, fy - 24); ctx.line_to(fx, fy - 18)
            stroke(ctx, 2.5, 1, tb * prog(t, S[3] + 2.6, S[3] + 3.0))
    # character A at the desk — thinking, pointing at Monday, then waiting
    hx = -66
    slump = prog(t, S[4], S[5] + 2, sm)
    P = sit_pose(hx, -56, lean=lerp(0.16, 0.3, slump), head=lerp(0.15, 0.55, slump))
    J = joints(P)
    chin = (J["head"][0] + 8, J["head"][1] + 20)
    point = window(t, S[3] + d4 * 0.6, S[3] + d4 + 0.5, 0.5, 0.6)
    P["arm_f"] = (1.05, 0.9)
    if point > 0.01:
        P["hand_n"] = None
        P["arm_n"] = (lerp(0.9, 2.05, point), lerp(1.4, 0.05, point))
        P["head"] = lerp(P["head"], -0.25, point)
    else:
        P["hand_n"] = chin
        P["elbow_n"] = (0.2, 1)
    P["y"] += math.sin(t * 1.4) * 0.8
    draw_figure(ctx, P)
    # pencil writing line where he points — nothing done
    return cam, dim


# ---- re-usable "small action" poses ------------------------------------------------
def pose_read(ctx, x, t, t0=0.0, alpha=1.0, turns=(0.6, 1.5), stool=True):
    if stool:
        ctx.move_to(x - 40, -56); ctx.line_to(x + 30, -56); stroke(ctx, 5, 0.8, alpha)
        ctx.move_to(x - 32, -56); ctx.line_to(x - 32, 0); ctx.move_to(x + 22, -56); ctx.line_to(x + 22, 0)
        stroke(ctx, 4, 0.7, alpha)
    P = sit_pose(x, -56, lean=0.18, head=0.55)
    P["y"] += math.sin(t * 1.5) * 0.8
    bx, by = x + 62, -126
    P["hand_n"] = (bx + 8, by + 6)
    P["hand_f"] = (bx - 16, by + 8)
    P["elbow_n"] = (0, 1)
    P["elbow_f"] = (0, 1)
    draw_figure(ctx, P, alpha)
    turn = None
    for tt in turns:
        if t0 + tt <= t <= t0 + tt + 0.6:
            turn = (t - t0 - tt) / 0.6
    ctx.save(); ctx.translate(bx, by); ctx.rotate(-0.5); ctx.translate(-bx, -by)
    book_open(ctx, bx, by, 34, alpha, turn)
    ctx.restore()
    return P


def pose_squat(ctx, x, t, t0=0.0, alpha=1.0, period=1.5):
    u = 0.5 - 0.5 * math.cos(2 * math.pi * max(0.0, t - t0) / period)
    P = dict(x=x - 14 * u, y=lerp(STAND_Y, -60, u), face=1, lean=lerp(0.02, 0.55, u), head=lerp(0, -0.3, u),
             foot_n=(x + 10, 0), foot_f=(x - 6, 0),
             arm_n=(lerp(0.15, 1.55, u), lerp(0.1, 0.0, u)), arm_f=(lerp(-0.1, 1.45, u), 0.0))
    draw_figure(ctx, P, alpha)
    return P


def pose_write(ctx, x, t, t0=0.0, alpha=1.0, writing=True, desk=True, paper=True, check=0.0):
    if desk:
        ctx.move_to(x + 50, -98); ctx.line_to(x + 330, -98); stroke(ctx, 6, 1, 0.95 * alpha)
        for lx in (x + 66, x + 314):
            ctx.move_to(lx, -98); ctx.line_to(lx, 0); stroke(ctx, 4, 1, 0.8 * alpha)
        ctx.move_to(x - 44, -56); ctx.line_to(x + 28, -56); stroke(ctx, 5, 0.75, alpha)
        ctx.move_to(x - 38, -56); ctx.line_to(x - 38, 0); ctx.move_to(x + 22, -56); ctx.line_to(x + 22, 0)
        stroke(ctx, 4, 0.65, alpha)
    px, py = x + 112, -101
    if paper:
        ctx.move_to(px - 40, py); ctx.line_to(px + 50, py); stroke(ctx, 4, 1, alpha)
    w = (math.sin(t * 9) * 5 + math.sin(t * 23) * 2) if writing else 0
    P = sit_pose(x, -56, lean=0.26, head=0.45)
    P["hand_n"] = (px - 4 + w, py - 8 - abs(math.sin(t * 9)) * 3 * writing)
    P["hand_f"] = (px - 50, py - 4)
    P["elbow_n"] = (0, 1)
    P["elbow_f"] = (0, 1)
    draw_figure(ctx, P, alpha)
    # pencil
    hx, hy = P["hand_n"]
    ctx.move_to(hx - 2, hy + 6); ctx.line_to(hx + 14, hy - 22); stroke(ctx, 3, 1, alpha)
    return P


def blocks(ctx, t, times, pitch=40, size=33):
    k = 0
    for c in range(8):
        for r in range(c + 1):
            ta = times[k]
            k += 1
            if t < ta:
                continue
            p = back((t - ta) / 0.35)
            fl = math.exp(-(t - ta) * 3.0)
            x, y = c * pitch, -r * pitch
            s = size * p
            rrect(ctx, x + (size - s) / 2, y - size + (size - s) / 2, s, s, 6)
            ctx.set_source_rgba(1, 1, 1, 0.14 + 0.6 * fl)
            ctx.fill_preserve()
            stroke(ctx, 2.5, 1, 0.95)


def block_times(t0, t1, first):
    n = 36
    out = [first]
    for k in range(1, n):
        out.append(t0 + (t1 - t0) * (k / (n - 1)) ** 0.62)
    return out


def scene3(ctx, ui, t, C):
    S, E = C.S, C.E
    sh = C.shots3
    T = C.T
    if t < sh[1]:  # ---- 3a: one block becomes a staircase
        cam = cam_blend([(sh[0], (17, -20, 2.7)), (S[6] + 2.0, (17, -20, 2.4)), (sh[1], (150, -150, 1.12))], t)
        apply_cam(ctx, *cam[:3])
        light_pool(ctx, 150, -140, 600, 0.05)
        bt = block_times(S[6] + 2.3, E[6] - 0.2, S[6] + 0.35)
        blocks(ctx, t, bt)
        pl = window(t, S[6] + 0.3, S[6] + 4.6, 0.5, 0.6)
        if pl > 0:
            pill(ui, T["book"], W / 2, 150, 24, pl)
        return cam, 1.0
    if t < sh[2]:  # ---- 3b1: a whole book in one evening — overwhelming
        cam = cam_blend([(sh[1], (20, -150, 1.75)), (sh[2], (40, -230, 1.55))], t)
        apply_cam(ctx, *cam[:3])
        light_pool(ctx, 60, -200, 520, 0.05)
        ctx.move_to(-900, 0); ctx.line_to(900, 0); stroke(ctx, 2.5, 1, 0.5)
        heavy = prog(t, sh[2] - 1.6, sh[2] - 0.3, sm)
        y = 0
        for i in range(14):
            ww = 150 + ((i * 37) % 5) * 9
            off = ((i * 53) % 7 - 3) * 4
            bh = 24
            arr = prog(t, sh[1] + 0.05 * i, sh[1] + 0.05 * i + 0.5, eout)
            yy = y - (1 - arr) * 60
            book_closed(ctx, 160 + off, yy, ww, bh, arr * (1 - 0.45 * heavy))
            y -= bh + 2
        # moon = "one evening"
        mx, my = 330, -420
        ctx.new_sub_path(); ctx.arc(mx, my, 26, 0, 6.2832); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
        ctx.new_sub_path(); ctx.arc(mx + 12, my - 8, 24, 0, 6.2832); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill()
        draw_text(ctx, T["evening"], mx + 4, my + 60, 20, "Inter SemiBold", "c", 3, (1, 1, 1, 0.75))
        P = stand(-90, t=t, lean=lerp(-0.08, 0.14, heavy), head=lerp(-0.35, 0.5, heavy))
        draw_figure(ctx, P)
        return cam, 1.0
    if t < sh[3]:  # ---- 3b2: start with a few pages
        cam = cam_blend([(sh[2], (10, -120, 2.15)), (sh[3], (20, -125, 2.35))], t)
        apply_cam(ctx, *cam[:3])
        # reading lamp
        ctx.move_to(-150, 0); ctx.line_to(-150, -250); ctx.line_to(-110, -270); stroke(ctx, 3, 1, 0.7)
        ctx.move_to(-130, -282); ctx.line_to(-84, -282); ctx.line_to(-74, -252); ctx.line_to(-140, -252); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()
        light_pool(ctx, -20, -150, 260, 0.11)
        ctx.move_to(-500, 0); ctx.line_to(500, 0); stroke(ctx, 2.5, 1, 0.5)
        pose_read(ctx, -20, t, sh[2], turns=(0.5, 1.6))
        title(ui, T["start_small"], 175, t, S[8] - 0.1, sh[3] + 0.3, 56)
        return cam, 1.0
    if t < sh[4]:  # ---- 3c1: you don't need two hours
        cam = cam_blend([(sh[3], (-20, -250, 1.2)), (sh[4], (0, -270, 1.32))], t)
        apply_cam(ctx, *cam[:3])
        light_pool(ctx, 130, -330, 480, 0.06)
        ctx.move_to(-900, 0); ctx.line_to(900, 0); stroke(ctx, 2.5, 1, 0.5)
        cx, cy, r = 150, -330, 230
        ctx.new_sub_path(); ctx.arc(cx, cy, r, 0, 6.2832); ctx.set_source_rgba(0.03, 0.03, 0.03, 1); ctx.fill_preserve(); stroke(ctx, 4, 1, 0.95)
        for i in range(60):
            an = i * math.pi / 30
            l = 26 if i % 5 == 0 else 10
            ctx.move_to(cx + (r - 14) * math.sin(an), cy - (r - 14) * math.cos(an))
            ctx.line_to(cx + (r - 14 - l) * math.sin(an), cy - (r - 14 - l) * math.cos(an))
            stroke(ctx, 3 if i % 5 == 0 else 1.5, 1, 0.8)
        u = prog(t, sh[3] + 0.2, sh[4] - 0.2, sm)
        mang = u * 4 * math.pi
        hang = u * math.pi / 3
        ctx.move_to(cx, cy); ctx.line_to(cx + 175 * math.sin(mang), cy - 175 * math.cos(mang)); stroke(ctx, 5, 1, 1)
        ctx.move_to(cx, cy); ctx.line_to(cx + 110 * math.sin(hang), cy - 110 * math.cos(hang)); stroke(ctx, 8, 1, 1)
        ctx.new_sub_path(); ctx.new_sub_path(); ctx.arc(cx, cy, r + 18, -math.pi / 2, -math.pi / 2 + hang * 6 * 0 + mang / 2)
        stroke(ctx, 5, 1, 0.45)
        draw_text(ctx, T["hours"], cx, cy + r + 70, 26, "Inter SemiBold", "c", 4, (1, 1, 1, 0.8))
        P = stand(-260, t=t, lean=lerp(-0.08, 0.12, u), head=lerp(-0.3, 0.4, u))
        draw_figure(ctx, P)
        return cam, 1.0
    if t < sh[5]:  # ---- 3c2: a few minutes of movement
        cam = cam_blend([(sh[4], (0, -115, 2.2)), (sh[5], (0, -118, 2.4))], t)
        apply_cam(ctx, *cam[:3])
        light_pool(ctx, 0, -100, 300, 0.10)
        ctx.move_to(-500, 0); ctx.line_to(500, 0); stroke(ctx, 2.5, 1, 0.5)
        rrect(ctx, -120, -6, 240, 6, 3); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()
        pose_squat(ctx, 0, t, sh[4] + 0.3)
        rem = max(0, 300 - int((t - sh[4]) * 1))
        tp = window(t, sh[4] + 0.1, sh[5] + 0.3, 0.4, 0.3)
        pill(ui, "%02d:%02d" % (rem // 60, rem % 60), W / 2, 170, 30, tp, 4, filled=False)
        return cam, 1.0
    if t < sh[6]:  # ---- 3d1: you don't need to change everything at once
        cam = cam_blend([(sh[5], (0, -560, 1.25)), (sh[6], (0, -400, 1.25))], t)
        apply_cam(ctx, *cam[:3])
        fadeall = prog(t, sh[6] - 1.3, sh[6] - 0.4, sm)
        rrect(ctx, -280, -880, 560, 820, 16); ctx.set_source_rgba(0.03, 0.03, 0.03, 1); ctx.fill_preserve()
        stroke(ctx, 3, 1, 0.9)
        for i in range(12):
            yy = -830 + i * 64
            a = 1.0 if i == 8 else (1 - 0.85 * fadeall)
            if i == 8:
                light_pool(ctx, -60, yy, 260, 0.14 * fadeall)
            rrect(ctx, -220, yy - 18, 36, 36, 6); stroke(ctx, 3, 1, 0.9 * a)
            ctx.move_to(-160, yy); ctx.line_to(-160 + 260 + ((i * 41) % 5) * 22, yy); stroke(ctx, 8, 1, 0.35 * a)
        return cam, 1.0
    # ---- 3d2: choose one habit
    cam = cam_blend([(sh[6], (90, -165, 1.9)), (sh[7], (100, -175, 2.1))], t)
    apply_cam(ctx, *cam[:3])
    light_pool(ctx, 100, -140, 330, 0.10)
    ctx.move_to(-500, 0); ctx.line_to(700, 0); stroke(ctx, 2.5, 1, 0.5)
    d = E[12] - S[12]
    tc = S[12] + d * 0.62
    chk = prog(t, tc, tc + 0.45)
    P = pose_write(ctx, -40, t, writing=t < tc - 0.1)
    # one habit card floating above the desk
    bx, by = 150, -250
    ca = prog(t, sh[6] + 0.2, sh[6] + 0.8, eout)
    rrect(ctx, bx - 40, by - 32 + (1 - ca) * 12, 230, 64, 14)
    ctx.set_source_rgba(0.03, 0.03, 0.03, ca); ctx.fill_preserve(); stroke(ctx, 2.5, 1, 0.9 * ca)
    rrect(ctx, bx - 22, by - 18, 36, 36, 7); stroke(ctx, 3.5, 1, ca)
    ctx.move_to(bx + 34, by); ctx.line_to(bx + 160, by); stroke(ctx, 7, 1, 0.45 * ca)
    light_pool(ctx, bx, by, 140, 0.3 * chk)
    if chk > 0:
        pts = [(bx - 13, by), (bx - 5, by + 9), (bx + 11, by - 10)]
        ctx.move_to(*pts[0])
        if chk < 0.4:
            ctx.line_to(*lerp2(pts[0], pts[1], chk / 0.4))
        else:
            ctx.line_to(*pts[1]); ctx.line_to(*lerp2(pts[1], pts[2], (chk - 0.4) / 0.6))
        stroke(ctx, 5, 1, 1)
    return cam, 1.0


def scene4(ctx, ui, t, C):
    S, E = C.S, C.E
    T = C.T
    a0, b0 = C.SC[3], C.SC[4]
    N, sw, shh = 44, 46.0, 15.0
    t0, D = a0 + 0.4, (b0 - 0.7) - (a0 + 0.4)
    ncont = N * clamp((t - t0) / D) ** (1 / 0.62)
    F = [(-60, 0), (-40, 0)] + [(j * sw + 23 + (5 if j % 2 else -5), -(j + 1) * shh) for j in range(N)]
    s = clamp(ncont - 1.3, 0, len(F) - 2.01)

    def bpose(tt):
        nc = N * clamp((tt - t0) / D) ** (1 / 0.62)
        ss = clamp(nc - 1.3, 0, len(F) - 2.01)
        lk = window(tt, S[14] + 0.6, S[14] + 2.4, 0.4, 0.5)
        return walk_pose(F, ss, lean=0.08, head=lerp(0, 0.6, lk), lift=10, swing=0.35)

    P = bpose(t)
    pull = prog(t, S[15] - 0.2, b0 - 0.2)
    follow = (P["x"] + 70, P["y"] - 40, 1.75)
    wide = (N * sw / 2 + 40, -N * shh / 2 - 160, 0.68)
    cam = [lerp(follow[0], wide[0], pull), lerp(follow[1], wide[1], pull),
           math.exp(lerp(math.log(follow[2]), math.log(wide[2]), pull)), 0.0]
    apply_cam(ctx, *cam[:3])
    rate = (1 / 0.62) * N / D * clamp((t - t0) / D) ** (1 / 0.62 - 1)
    dayflick = 0.95 + 0.05 * math.cos(2 * math.pi * ncont) / (1 + rate * 0.3)
    light_pool(ctx, P["x"], P["y"], 420, 0.07)
    dashed_ground(ctx, -1400, 2600)
    # steps built one by one
    for k in range(N):
        if k >= ncont:
            break
        p = clamp((ncont - k) / 0.9)
        x, y = k * sw, -(k + 1) * shh
        hh = (k + 1) * shh + (1 - eout(p)) * 22
        pa = sm(p)
        ctx.rectangle(x, -hh, sw, hh)
        ctx.set_source_rgba(1, 1, 1, pa * (0.04 + 0.2 * math.exp(-(ncont - k) * 0.9)))
        ctx.fill()
        ctx.move_to(x, -hh); ctx.line_to(x + sw, -hh)
        stroke(ctx, 3.5, 1, 0.95 * pa)
        ctx.move_to(x, -hh); ctx.line_to(x, -k * shh); stroke(ctx, 2, 1, 0.6 * pa)
        # tiny icon of the day's small action
        age = ncont - k
        if age < 1.6:
            ia = window(age, 0, 1.6, 0.25, 0.8) * (1 / (1 + rate * 0.08))
            icon(ctx, ["book", "dumbbell", "check"][k % 3], x + sw / 2, y - 70 - age * 18, 34, ia, lw=3)
    # time-lapse ghost trail
    if rate > 2.0:
        for i, a in ((1, 0.20), (2, 0.09)):
            draw_figure(ctx, bpose(t - 0.07 * i), alpha=a * min(1, (rate - 2) / 3))
    draw_figure(ctx, P)
    day = 1 + int(round(364 * clamp(ncont / N) ** 1.6))
    pill(ui, f"{T['day']} {day}", W / 2, 120, 26, window(t, a0 + 0.2, b0 + 0.2, 0.5, 0.4), 4, filled=False)
    title(ui, T["add1"], 230, t, S[15] + 0.2, b0 + 0.25, 50, "Inter Medium", 9)
    title(ui, T["add2"], 300, t, S[15] + 0.6, b0 + 0.25, 50, "Inter Bold", 9)
    return cam, dayflick


def scene5(ctx, ui, t, C):
    S, E = C.S, C.E
    a0, b0 = C.SC[4], C.SC[5]
    cam = cam_blend([(a0, (30, -250, 1.15)), (S[18], (45, -262, 1.25)), (b0, (55, -270, 1.32))], t)
    apply_cam(ctx, *cam[:3])
    ctx.move_to(-900, 0); ctx.line_to(900, 0); stroke(ctx, 2.5, 1, 0.5)
    light_pool(ctx, -100, -150, 380, 0.07)
    conf = prog(t, S[18] + 0.2, S[18] + 2.2)
    # mirror
    mx0, mx1, my0, my1 = 60, 320, -470, -14
    mc = ((mx0 + mx1) / 2, (my0 + my1) / 2)
    rrect(ctx, mx0, my0, mx1 - mx0, my1 - my0, 120)
    g = cairo.LinearGradient(mx0, my0, mx1, my1)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.09)
    g.add_color_stop_rgba(0.5, 1, 1, 1, 0.03)
    g.add_color_stop_rgba(1, 1, 1, 1, 0.07)
    ctx.set_source(g); ctx.fill_preserve()
    stroke(ctx, 5, 1, 0.95)
    ctx.move_to(mx0 + 30, 0); ctx.line_to(mx0 + 50, my1); ctx.move_to(mx1 - 30, 0); ctx.line_to(mx1 - 50, my1)
    stroke(ctx, 3, 1, 0.7)
    # character pose: slightly unsure -> upright & confident
    bx = -140
    P = stand(bx, t=t, lean=lerp(0.12, -0.04, conf), head=lerp(0.35, -0.06, conf),
              arm_n=(lerp(0.05, -0.12, conf), lerp(0.05, 0.2, conf)), arm_f=(lerp(-0.02, -0.25, conf), 0.2))
    P["y"] -= 3 * conf
    plane = mx0 - 10
    # reflection & memories inside the mirror (clipped)
    ctx.save()
    rrect(ctx, mx0 + 4, my0 + 4, mx1 - mx0 - 8, my1 - my0 - 8, 116)
    ctx.clip()
    d18 = E[17] - S[17]
    mems = [S[17] + d18 * f for f in (0.0, 0.26, 0.52, 0.78)]
    mem_end = S[17] + d18 + 0.3
    refl_a = 1 - window(t, S[17] - 0.2, mem_end + 0.3, 0.5, 0.6)
    R = dict(P)
    R["x"] = mc[0] + 28
    R["face"] = -1
    R["foot_n"] = (R["x"] - 9, 0)
    R["foot_f"] = (R["x"] + 9, 0)
    if refl_a > 0:
        light_pool(ctx, R["x"], -150, 200, 0.10 * conf * refl_a)
        draw_figure(ctx, R, alpha=refl_a * lerp(0.42, 0.85, conf))
    for i, tm in enumerate(mems):
        a = window(t, tm, tm + d18 * 0.3 + 0.35, 0.35, 0.4) * 0.8
        if a <= 0:
            continue
        ctx.save()
        ctx.translate(mc[0] - 15, 0)
        ctx.scale(0.82, 0.82)
        if i == 0:
            pose_read(ctx, -40, t, tm, a, turns=(0.3,))
        elif i == 1:
            rrect(ctx, -90, -5, 180, 5, 2); ctx.set_source_rgba(1, 1, 1, 0.6 * a); ctx.fill()
            pose_squat(ctx, 10, t, tm, a, 1.1)
        elif i == 2:
            pose_write(ctx, -90, t, tm, a, desk=True)
        else:
            for k in range(4):
                ctx.move_to(-110 + k * 50, -k * 40 - 40); ctx.line_to(-60 + k * 50, -k * 40 - 40)
                stroke(ctx, 4, 1, a)
            icon(ctx, "check", 60, -360, 70, a, lw=4)
            draw_figure(ctx, stand(-60, t=t, lean=0.0, head=-0.1), alpha=a)
        ctx.restore()
    ctx.restore()
    # memory sparks flowing from the mirror into the character
    for i in range(10):
        ph = (t * 0.45 + i / 10) % 1
        a = window(t, S[17] + 0.5, b0, 0.6, 0.8) * math.sin(math.pi * ph) * 0.8
        if a <= 0.01:
            continue
        x = lerp(mc[0] - 60, P["x"] + 10, ph)
        y = lerp(-180 - (i % 5) * 50, -150 - (i % 3) * 20, ph) - math.sin(math.pi * ph) * 40
        ctx.new_sub_path(); ctx.arc(x, y, 3.2, 0, 6.2832); ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    light_pool(ctx, P["x"], -150, 240, 0.10 * conf)
    draw_figure(ctx, P)
    title(ui, C.T["identity"], 140, t, S[18] + 0.5, b0 + 0.2, 54, "Inter SemiBold", 10)
    return cam, 1.0


def scene6(ctx, ui, t, C):
    S, E = C.S, C.E
    a0 = C.SC[5]
    top = stair_top(SX0, SY0, SW, SH, SN - 1)
    cam = cam_blend([(a0, (top[0] + 20, top[1] - 120, 1.65)), (a0 + 1.6, (top[0] - 10, top[1] - 130, 1.5)),
                     (S[20] + 1.4, (640, -500, 0.5))], t)
    apply_cam(ctx, *cam[:3])
    dim = 1 - 0.7 * prog(t, S[20] - 0.3, S[20] + 1.6, sm)
    dashed_ground(ctx, -2600, 3600)
    light_pool(ctx, 600, -400, 1300, 0.04)
    lit = [0.35 + 0.35 * math.sin(t * 1.3 + i * 0.5) ** 2 for i in range(SN)]
    draw_stairs(ctx, SX0, SY0, SN, SW, SH, lit=lit)
    orb(ctx, *ORB, 18, t, 1.0)
    # journey dots on each step
    for i in range(SN):
        x, y = stair_top(SX0, SY0, SW, SH, i)
        ctx.new_sub_path(); ctx.arc(x - 12, y - 10, 3, 0, 6.2832); ctx.set_source_rgba(1, 1, 1, 0.55); ctx.fill()
    # last steps to the top
    F = [stair_top(SX0, SY0, SW, SH, SN - 3), (stair_top(SX0, SY0, SW, SH, SN - 3)[0] - 14, top[1] + 2 * SH),
         (stair_top(SX0, SY0, SW, SH, SN - 2)[0], top[1] + SH), (top[0] - 14, top[1]), (top[0] + 2, top[1])]
    F = [(f[0], f[1]) for f in F]
    s = 3 * prog(t, a0 + 0.2, a0 + 2.2, lambda x: x)
    if s < 3:
        P = walk_pose(F, s, lean=0.08, lift=24, swing=0.32)
    else:
        P = stand(top[0] - 6, t=t, lean=-0.03, head=-0.12)
        P["y"] += top[1]
        P["foot_n"] = (top[0] + 3, top[1])
        P["foot_f"] = (top[0] - 15, top[1])
    light_pool(ctx, P["x"], P["y"], 260, 0.12)
    draw_figure(ctx, P)
    # final question & logo
    qa, qb = S[20] - 0.05, C.vo_end + 2.4
    title(ui, C.T["q1"], 500, t, qa, qb, 66, "Inter Medium", 8)
    title(ui, C.T["q2"], 590, t, qa + 0.35, qb, 66, "Inter Bold", 8)
    la = C.vo_end + 3.3
    lg = window(t, la, END - 1.0, 1.0, 1.6)
    if lg > 0:
        trk = 26 + 14 * eout((t - la) / 4.0)
        draw_text(ui, "HUMAN MIND", W / 2, 562, 74, "Inter SemiBold", "c", trk, (1, 1, 1, lg))
        wl = 260 * eout((t - la - 0.3) / 1.6)
        ui.move_to(W / 2 - wl, 610); ui.line_to(W / 2 + wl, 610)
        ui.set_source_rgba(1, 1, 1, 0.5 * lg); ui.set_line_width(2); ui.stroke()
    dim *= 1 - 0.55 * prog(t, C.vo_end + 2.0, C.vo_end + 3.6, sm)
    return cam, dim


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6]


# ====================================================================== compositor
def render_frame(t, C, subs=True):
    n = max(i for i in range(6) if t >= C.SC[i] - 1e-9)
    fg, ctx = new_layer()
    ui, uc = new_layer()
    ctx.save()
    cam, dim = SCENES[n](ctx, uc, t, C)
    ctx.restore()
    draw_particles(ctx, t, cam, 0.8)
    lum, alp = layer_arrays(fg)
    ulum, ualp = layer_arrays(ui)
    bg = background(cam, t)
    img = bg * (1 - alp) + lum
    img = img + glow(lum) * 0.55
    img = img * dim
    img = img * (1 - ualp) + ulum + glow(ulum, 2.0, 5.0) * 0.35
    # dip-to-dark transitions
    f = 1.0
    for c in C.cuts:
        f = min(f, 0.0 + sm(abs(t - c) / DIP))
    f = min(f, prog(t, 0.0, 0.9, sm), 1 - prog(t, END - 1.6, END - 0.25, sm))
    img = img * f
    if subs:
        sl, sc = new_layer()
        if draw_subs(sc, C, t):
            sl_l, sl_a = layer_arrays(sl)
            sh_ = gaussian_filter(sl_a.reshape(H // 4, 4, W // 4, 4).mean(axis=(1, 3)), 2.5)
            shadow = np.clip(np.asarray(Image.fromarray(sh_).resize((W, H), Image.BILINEAR)) * 1.6, 0, 0.85)
            img = img * (1 - shadow) * (1 - sl_a) + sl_l + glow(sl_l, 1.5, 4) * 0.12
    img = tonemap(img) + GRAIN[int(t * FPS) % len(GRAIN)]
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
