"""English subtitles, chunked and synced to the Russian voice-over timestamps."""
from core import *

# (start, end, "chunk / chunk / chunk")  — '/' splits on-screen chunks
SEGMENTS = [
    (0.00, 4.96, "Imagine you wake up tomorrow / and no one in the world / remembers you."),
    (5.56, 9.82, "You open your eyes, / grab your phone / and see hundreds of messages."),
    (10.30, 13.44, "But instead of the usual greetings, / there's the same question:"),
    (14.36, 15.30, "\"Who are you?\""),
    (15.36, 17.48, "At first you think / it's some kind of joke,"),
    (17.90, 20.68, "but then you leave your room / and head to the kitchen."),
    (21.22, 22.50, "Your parents are sitting there."),
    (23.12, 24.42, "You say \"Good morning\","),
    (24.42, 29.36, "but they look at you / like they're seeing / a stranger for the first time."),
    (30.02, 31.80, "One of them even asks:"),
    (31.90, 33.90, "\"Young man, / who are you here for?\""),
    (34.26, 39.48, "You try to explain / it's your home, / that you're their son, / but they call security."),
    (40.04, 44.38, "In panic, you run outside. / Maybe at least / your friends remember you."),
    (44.80, 49.88, "You call your best friend. / He answers, / but after your words / he turns serious."),
    (50.60, 53.94, "\"Listen, I don't know you. / Don't call me again.\""),
    (54.40, 57.46, "You open the family album / to find proof."),
    (57.78, 61.76, "But in every photo / where you used to be, / there's now an empty space."),
    (62.50, 65.74, "Your messages are gone. / Your photos have vanished."),
    (66.46, 69.46, "Even your name / is gone from the contacts."),
    (70.12, 72.60, "It's as if you / never existed."),
    (73.06, 76.78, "Suddenly, your phone vibrates. / A message / from an unknown number."),
    (77.42, 79.90, "\"Finally, / they forgot you.\""),
    (80.06, 80.90, "You freeze."),
    (81.36, 84.34, "A few seconds later, / another message arrives."),
    (84.86, 86.94, "\"Now all that's left / is to forget yourself.\""),
    (87.62, 90.90, "You slowly raise your phone / and open the front camera."),
    (91.50, 94.34, "But what you see / makes you step back."),
    (95.02, 97.40, "Your reflection / is smiling."),
    (97.68, 100.80, "Even though / you're not smiling / at all."),
    (101.54, 102.82, "The screen suddenly goes dark."),
    (102.82, 107.36, "And when you turn / the phone back on, / one last message appears."),
    (107.94, 110.78, "\"Tomorrow you'll forget / that you ever existed.\""),
    (111.42, 113.04, "And now the most important question."),
    (113.96, 117.02, "If the whole world forgot you, / how would you prove"),
    (117.08, 119.32, "that you were once / part of this world?"),
    (120.00, 122.80, "Write in the comments / what you would do / in my place."),
]


def build_chunks():
    out = []
    for s, e, txt in SEGMENTS:
        parts = [p.strip() for p in txt.split('/')]
        total = sum(len(p) + 6 for p in parts)
        t = s
        for p in parts:
            d = (e - s) * (len(p) + 6) / total
            out.append((t, t + d, p))
            t += d
    # extend each chunk slightly to avoid flicker gaps (but not past the next one)
    res = []
    for i, (a, b, p) in enumerate(out):
        nxt = out[i + 1][0] if i + 1 < len(out) else b + 1
        res.append((a, min(b + 0.35, nxt), p))
    return res


CHUNKS = build_chunks()


def draw_subs(ctx, t, y=1440):
    for a, b, p in CHUNKS:
        if a <= t < b:
            k = back_out(prog(t, a, a + 0.18), 2.2)
            alpha = clamp(prog(t, a, a + 0.08)) * (1 - prog(t, b - 0.08, b))
            size = 66
            lines = wrap(ctx, p, size, 900, "black")
            ctx.save()
            ctx.translate(W / 2, y)
            ctx.scale(lerp(0.8, 1.0, k), lerp(0.8, 1.0, k))
            quote = p.startswith('"') or p.endswith('"')
            col = hexc('#ffd84a') if quote else (1, 1, 1)
            for i, ln in enumerate(lines):
                yy = (i - (len(lines) - 1) / 2) * size * 1.12 + size * 0.36
                text(ctx, ln.upper(), 0, yy, size, col, alpha, weight="black", outline=14, oc=(0, 0, 0), oa=0.92)
            ctx.restore()
            break
