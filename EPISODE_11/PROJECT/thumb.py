"""9:16 preview (thumbnail) for each language."""
import skia
from scenes import *

TT = {'ru': (['ЧТО, ЕСЛИ ЛЮДИ', 'СМОГУТ'], 'ЧИТАТЬ МЫСЛИ?'), 'en': (['WHAT IF PEOPLE', 'COULD'], 'READ MINDS?')}

def thumb(lang, out):
    L = dict(LANG[lang]); L['_code'] = lang
    s = skia.Surface(W, H); c = s.getCanvas()
    c.save(); cam(c, 540, 1050, 1.0)
    bg_city(c, 3.0, 0, 'night')
    draw_crowd(c, CROWD1, 4.0, 4.0)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P('#0a0a18', 0.55))
    circle(c, 540, 1080, 620, P(VIOLET, 0.35, blur=140))
    for i in range(4):
        circle(c, 540, 1060, 330 + i * 120, P(CYAN, 0.35 - i * 0.07, stroke=6, blur=3))
    c.save(); cam(c, 0, -10, 4.4)
    c.translate(0, 0)
    closeup(c, HERO, 0.0, 'shock', 0.0, (0.3, -0.2), 0.4)
    for sgn in (-1, 1):
        x = sgn * 84 * 0.27
        for r in (5, 9):
            circle(c, x + 0.3 * 84 * 0.06, 5 - 0.2 * 84 * 0.05, r, P(CYAN, 0.8, stroke=1.3))
    c.restore()
    c.restore() if False else None
    for (x, y, sz, ic, sd) in [(170, 820, 120, 'heart', 1), (910, 790, 120, 'lock', 2), (150, 1390, 105, 'money', 3),
                                (930, 1360, 110, 'broken', 4)]:
        bubble(c, x, y, sz, 1.0, appear=1.0, icon=ic, seed=sd, glow=CYAN)
    # friend in the corner - the twist
    c.save(); c.translate(905, 1720); c.scale(0.9, 0.9)
    circle(c, 0, 0, 220, P(VIOLET, 0.5, blur=60))
    closeup(c, FRIEND, -0.4, 'smirk', 0, (-0.8, 0), 0.0)
    for sgn in (-1, 1):
        circle(c, -0.4 * 84 * 0.44 + sgn * 84 * 0.27 * 0.88 - 0.8 * 84 * 0.06, 5, 10, P(VIOLET, 0.8, blur=5))
    c.restore()
    vignette(c, 0.55)
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 640), P(shader=lin(0, 0, 0, 640, [('#05050c', 0.92), ('#05050c', 0)])))
    top, hl = TT[lang]
    for i, ln in enumerate(top):
        text(c, ln, W / 2, 190 + i * 128, 128, '#ffffff', tf=TF_BOLD)
    fs = 170
    while skia.Font(TF_BOLD, fs).measureText(hl) > 1000:
        fs -= 4
    y = 190 + len(top) * 128 + 40
    text(c, hl, W / 2, y, fs, CYAN, tf=TF_BOLD, paint=P(CYAN, 0.8, blur=22))
    text(c, hl, W / 2, y, fs, '#e9f7ff', tf=TF_BOLD)
    # episode pill
    lab = L['episode']
    w = skia.Font(TF_BOLD, 46).measureText(lab) + 60
    rect(c, 60, 1760, 60 + w, 1840, P('#ff4a6a'), r=40)
    text(c, lab, 60 + w / 2, 1817, 46, '#ffffff', tf=TF_BOLD)
    s.makeImageSnapshot().save(out, skia.kPNG)

thumb('ru', '../RU_VERSION/preview_9x16_ru.png')
thumb('en', '../EN_VERSION/preview_9x16_en.png')
