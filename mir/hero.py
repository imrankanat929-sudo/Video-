"""The main character from the model sheet: round beige head, messy black hair,
dark sweater, dark trousers, light sneakers. Drawn from simple shapes."""
import math
import random
from .gfx import (circle, ellipse, poly, line, rrect, setc, fill_rrect, glow,
                  lerp, col, mix)

SKIN = "#d3a57c"
SKIN_SH = "#b98a63"
HAIR = "#121014"
SWEATER = "#24242b"
SWEATER_HI = "#2f2f38"
PANTS = "#17171c"
SHOE = "#c9c7c4"
EYE = "#111111"


def _hair_points(R, seed=7):
    """Messy hair outline around the head (crown + spikes)."""
    rnd = random.Random(seed)
    pts = []
    n = 18
    for i in range(n + 1):
        a = math.pi * (1.04 + 0.92 * i / n)  # from left-low over the top to right-low
        a += rnd.uniform(-0.03, 0.03)
        spike = 1.08 + (rnd.uniform(0.14, 0.3) if i % 2 else rnd.uniform(-0.02, 0.04))
        pts.append((math.cos(a) * R * spike, math.sin(a) * R * spike - R * 0.05))
    return pts


def _fringe_points(R):
    """Jagged fringe hanging over the forehead (left side longer, like the sheet)."""
    pts = [(-R * 1.06, -R * 0.05), (-R * 1.02, -R * 0.55)]
    teeth = [(-0.88, 0.02), (-0.74, -0.18), (-0.62, 0.08), (-0.48, -0.20),
             (-0.30, -0.02), (-0.16, -0.26), (0.02, -0.12), (0.18, -0.30),
             (0.36, -0.22), (0.52, -0.36), (0.70, -0.24), (0.86, -0.34), (1.00, -0.12)]
    for x, y in teeth:
        pts.append((x * R, y * R))
    pts += [(R * 1.08, -R * 0.1), (R * 1.04, -R * 0.7), (0, -R * 1.12), (-R * 0.95, -R * 0.95)]
    return pts


def head(ctx, x, y, R, expr="neutral", look=(0.0, 0.0), blink=0.0, rim=None, t=0.0):
    """Front view head. expr: neutral, surprised, scared, worried, determined, side_eye."""
    ctx.save()
    ctx.translate(x, y)
    # back hair mass
    poly(ctx, _hair_points(R), HAIR)
    circle(ctx, 0, -R * 0.12, R * 1.02, HAIR)
    # face
    circle(ctx, 0, 0, R, SKIN)
    # soft shading at the bottom of the face
    ctx.save()
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.clip()
    ellipse(ctx, R * 0.15, R * 1.05, R * 1.1, R * 0.45, SKIN_SH, 0.55)
    if rim:
        glow(ctx, -R * 1.1, -R * 0.1, R * 1.2, rim, 0.35)
    ctx.restore()
    # fringe
    poly(ctx, _fringe_points(R), HAIR)

    lx, ly = look
    ex, ey = R * 0.30, R * 0.12
    eh = R * 0.22 * (1 - 0.9 * blink)
    ew = R * 0.13
    if expr in ("surprised", "scared"):
        eh *= 1.12
        ew *= 1.1
    # brows
    bw = R * 0.26
    by = -R * 0.16
    tilt = {"neutral": 0.0, "surprised": -0.12, "scared": 0.32, "worried": 0.32,
            "determined": -0.38, "side_eye": 0.0}.get(expr, 0.0)
    lift = {"surprised": -R * 0.1, "scared": -R * 0.07, "worried": -R * 0.02}.get(expr, 0)
    for s in (-1, 1):
        cx = s * ex + lx * R * 0.05
        # tilt > 0: inner ends go up (worried), tilt < 0: inner ends go down (angry)
        inner_y = by + lift - tilt * R * 0.22
        outer_y = by + lift + tilt * R * 0.05
        x_out, x_in = cx + s * bw * 0.5, cx - s * bw * 0.5
        line(ctx, x_out, outer_y, x_in, inner_y, R * 0.085, HAIR)
    # eyes
    for s in (-1, 1):
        cx = s * ex + lx * R * 0.09
        cy = ey + ly * R * 0.06
        if expr == "side_eye":
            ellipse(ctx, cx, cy, ew * 1.05, eh * 0.9, "#f4efe6")
            ellipse(ctx, cx + R * 0.05, cy + R * 0.02, ew * 0.75, eh * 0.7, EYE)
            line(ctx, cx - ew * 1.2, cy - eh * 0.25, cx + ew * 1.2, cy - eh * 0.25, R * 0.06, HAIR)
        else:
            ellipse(ctx, cx, cy, ew, max(eh, R * 0.015), EYE)
            if blink < 0.5:
                circle(ctx, cx - ew * 0.3, cy - eh * 0.4, ew * 0.28, "#ffffff", 0.85)
    # mouth
    my = R * 0.55
    if expr == "surprised":
        ellipse(ctx, R * 0.04, my, R * 0.08, R * 0.11, "#3a1d1d")
    elif expr == "scared":
        ellipse(ctx, R * 0.03, my, R * 0.17, R * 0.15, "#3a1d1d")
        ellipse(ctx, R * 0.03, my + R * 0.07, R * 0.1, R * 0.05, "#a8494a")
        # sweat drop
        sx, sy = R * 0.78, -R * 0.02 + (t * 12 % 18)
        poly(ctx, [(sx, sy - R * 0.16), (sx - R * 0.07, sy), (sx + R * 0.07, sy)], "#9fc3d9", 0.9)
        circle(ctx, sx, sy, R * 0.07, "#9fc3d9", 0.9)
    elif expr == "worried":
        ctx.move_to(-R * 0.14, my + R * 0.02)
        ctx.curve_to(-R * 0.05, my - R * 0.06, R * 0.05, my - R * 0.06, R * 0.14, my + R * 0.03)
        ctx.set_line_width(R * 0.05)
        setc(ctx, "#3a1d1d")
        ctx.stroke()
    elif expr == "determined":
        line(ctx, -R * 0.1, my, R * 0.12, my - R * 0.02, R * 0.05, "#3a1d1d")
    ctx.restore()


def bust(ctx, x, y, R, expr="neutral", look=(0, 0), blink=0.0, rim=None, t=0.0):
    """Head + shoulders. (x, y) = head center."""
    ctx.save()
    ctx.translate(x, y)
    # sweater
    sw = R * 2.5
    top = R * 1.05
    ctx.move_to(-sw * 0.36, top)
    ctx.curve_to(-sw * 0.55, top + R * 0.1, -sw * 0.62, top + R * 0.6, -sw * 0.64, top + R * 3)
    ctx.line_to(sw * 0.64, top + R * 3)
    ctx.curve_to(sw * 0.62, top + R * 0.6, sw * 0.55, top + R * 0.1, sw * 0.36, top)
    ctx.close_path()
    setc(ctx, SWEATER)
    ctx.fill()
    # sleeve seams
    for s in (-1, 1):
        ctx.move_to(s * sw * 0.42, top + R * 0.25)
        ctx.curve_to(s * sw * 0.40, top + R * 0.9, s * sw * 0.41, top + R * 1.6, s * sw * 0.42, top + R * 3)
        ctx.set_line_width(R * 0.03)
        setc(ctx, "#1a1a20")
        ctx.stroke()
    if rim:
        glow(ctx, -sw * 0.6, top + R * 0.6, R * 1.4, rim, 0.25)
    # neck + collar
    fill_rrect(ctx, -R * 0.22, R * 0.75, R * 0.44, R * 0.45, R * 0.06, SKIN_SH)
    ctx.move_to(-R * 0.36, top)
    ctx.curve_to(-R * 0.2, top + R * 0.22, R * 0.2, top + R * 0.22, R * 0.36, top)
    ctx.set_line_width(R * 0.08)
    setc(ctx, SWEATER_HI)
    ctx.stroke()
    ctx.restore()
    head(ctx, x, y, R, expr, look, blink, rim, t)


# ---------- full body (small, used in wide shots) ----------
def body_back(ctx, x, y, h, step=0.0, arm_up=0.0, rim=None):
    """Back view, feet at (x, y), height h. step: run cycle phase (radians), 0=standing."""
    R = h * 0.12
    s = math.sin(step)
    run = 1.0 if step else 0.0
    ctx.save()
    ctx.translate(x, y)
    bounce = -abs(s) * h * 0.02 * run
    ctx.translate(0, bounce)
    leg_w = h * 0.09
    # legs
    for side, ph in ((-1, s), (1, -s)):
        lx = side * h * 0.06
        lift = max(0, ph) * h * 0.06 * run
        fill_rrect(ctx, lx - leg_w / 2, -h * 0.46, leg_w, h * 0.44 - lift, leg_w * 0.3, PANTS)
        fill_rrect(ctx, lx - leg_w * 0.62, -h * 0.045 - lift, leg_w * 1.24, h * 0.05, h * 0.02, SHOE)
    # torso (sweater)
    fill_rrect(ctx, -h * 0.15, -h * 0.75, h * 0.3, h * 0.34, h * 0.06, SWEATER)
    # arms
    for side, ph in ((-1, -s), (1, s)):
        ax = side * h * 0.155
        if side == 1 and arm_up:
            ctx.save()
            ctx.translate(ax, -h * 0.72)
            ctx.rotate(-math.pi * 0.85 * arm_up)
            fill_rrect(ctx, -h * 0.035, 0, h * 0.07, h * 0.3, h * 0.035, SWEATER)
            circle(ctx, 0, h * 0.31, h * 0.04, SKIN)
            ctx.restore()
            continue
        ctx.save()
        ctx.translate(ax, -h * 0.72)
        ctx.rotate(ph * 0.5 * run)
        fill_rrect(ctx, -h * 0.035, 0, h * 0.07, h * 0.3, h * 0.035, SWEATER)
        circle(ctx, 0, h * 0.31, h * 0.04, SKIN)
        ctx.restore()
    # neck + head (all hair from behind)
    fill_rect = fill_rrect
    fill_rect(ctx, -h * 0.03, -h * 0.79, h * 0.06, h * 0.05, 2, SKIN_SH)
    circle(ctx, 0, -h * 0.86, R, HAIR)
    poly(ctx, [(px * h / 100 * 1.2, py * h / 100 * 1.2 - h * 0.86) for px, py in
               _hair_points(10, seed=3)], HAIR)
    if rim:
        glow(ctx, 0, -h * 0.6, h * 0.5, rim, 0.25)
    ctx.restore()


def body_side(ctx, x, y, h, facing=1, arm=0.0, expr_eye=True):
    """Side view, feet at (x, y). arm: 0..1 raised waving arm angle."""
    R = h * 0.12
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing, 1)
    leg_w = h * 0.09
    fill_rrect(ctx, -leg_w / 2, -h * 0.46, leg_w, h * 0.44, leg_w * 0.3, PANTS)
    fill_rrect(ctx, -leg_w * 0.55, -h * 0.045, leg_w * 1.6, h * 0.05, h * 0.02, SHOE)
    fill_rrect(ctx, -h * 0.1, -h * 0.75, h * 0.2, h * 0.34, h * 0.06, SWEATER)
    # arm (waving forward)
    ctx.save()
    ctx.translate(h * 0.02, -h * 0.71)
    ctx.rotate(-math.pi * 0.5 * arm)
    fill_rrect(ctx, -h * 0.035, 0, h * 0.07, h * 0.3, h * 0.035, SWEATER_HI)
    circle(ctx, 0, h * 0.31, h * 0.042, SKIN)
    ctx.restore()
    fill_rrect(ctx, -h * 0.03, -h * 0.79, h * 0.06, h * 0.05, 2, SKIN_SH)
    circle(ctx, 0, -h * 0.86, R, SKIN)
    # hair covering the back and top
    pts = [(px * R / 10, py * R / 10 - h * 0.86) for px, py in _hair_points(10, seed=5)]
    poly(ctx, [(p[0] - R * 0.25, p[1]) for p in pts], HAIR)
    poly(ctx, [(-R * 1.1, -h * 0.86), (-R * 0.9, -h * 0.86 - R * 0.9),
               (R * 1.0, -h * 0.86 - R * 0.75), (R * 0.95, -h * 0.86 - R * 0.25),
               (R * 0.6, -h * 0.86 - R * 0.45), (R * 0.3, -h * 0.86 - R * 0.2),
               (-R * 0.3, -h * 0.86 + R * 0.2), (-R * 1.0, -h * 0.86 + R * 0.6)], HAIR)
    if expr_eye:
        ellipse(ctx, R * 0.55, -h * 0.86 + R * 0.05, R * 0.1, R * 0.17, EYE)
    ctx.restore()
