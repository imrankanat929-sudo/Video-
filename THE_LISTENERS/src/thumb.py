"""YouTube cover 1920x1080 + character/creature reference sheets."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
from envs import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save(surf, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    surf.makeImageSnapshot().save(path, skia.kPNG)


def cover():
    s = skia.Surface(W, H)
    c = s.getCanvas()
    corridor(c, 0.0, col='#0b0d12', wall='#161a22', floor='#0b0c10', ceil='#0d0f13', vanish=(620, 520))
    # red emergency light
    circle(c, 620, 330, 420, paint(C('#ff2a2a', 0.18), blur=120))
    # Alex in the background, small, scared
    alex(c, 620, 760, 0.42, look=0.9, mouth=0.6, arms='cover', sweat=2, tint='#c7cbe0')
    # the Listener in foreground (big, head turned toward Alex)
    listener(c, 1480, 400 + 931 * 1.5, 1.5, turn=-0.75, tilt=-12, t=1.0, glow=1.2, ripples=1.0, arms='hang')
    vignette(c, 0.8)
    # texts
    text(c, '15 ПРАВИЛ', 70, 200, 170, '#ffd21e', stroke=22, stroke_col='#000000', shadow=12)
    text(c, 'ЧТОБЫ ВЫЖИТЬ', 74, 330, 112, '#ffffff', stroke=18, stroke_col='#000000', shadow=10)
    label(c, 'ОНИ СЛЫШАТ ТЕБЯ', 80, 380, 46, bg='#e53935', fg='#ffffff', angle=-3)
    label(c, 'СЛУШАЮЩИЕ', 84, 960, 40, bg='#ffffff', fg='#111111', angle=-2)
    # small recorder REC badge
    rrect(c, 1640, 60, 220, 70, 12, paint(C('#000000', 0.6)))
    circle(c, 1690, 95, 16, paint('#ff2a2a'))
    text(c, 'REC', 1720, 112, 44, '#ffffff', FONT_XB)
    save(s, os.path.join(ROOT, 'thumbnail', 'youtube_cover.png'))


def refs():
    # creature reference: front, turned, side poses
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14171f'))
    for x in range(0, W, 60):
        line(c, x, 0, x, H, C('#ffffff', 0.04), 1)
    for i, (turn, arms, lb) in enumerate(((0.0, 'hang', 'ФРОНТ'), (0.8, 'hang', 'СЛЫШИТ ЗВУК'), (-0.6, 'reach', 'АТАКА'), (0.3, 'up', 'ЛАЗАЕТ'))):
        listener(c, 260 + i * 470, 1000, 0.76, turn=turn, arms=arms, t=i, glow=0.6, ripples=0.8 if i == 1 else 0)
        text(c, lb, 260 + i * 470, 1060, 30, '#cfd6e6', FONT_XB, align='center')
    text(c, 'THE LISTENER / СЛУШАЮЩИЙ — REFERENCE', 40, 60, 40, '#ffffff')
    text(c, 'Белая гладкая «керамика» · нет глаз, носа, рта, волос · вытянутая голова · руки ниже колен · без крови и одежды', 40, 105, 26, '#9aa3b8', FONT_XB)
    save(s, os.path.join(ROOT, 'assets', 'creatures', 'listener_reference.png'))
    # Alex reference
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1b1e2a'))
    for i, (arms, look, lb) in enumerate((('down', 0.0, 'НЕЙТРАЛЬНО'), ('shh', 0.4, 'ТИХО'), ('cover', -0.6, 'СТРАХ'), ('phone1', 0.2, 'ТЕЛЕФОН'))):
        alex(c, 260 + i * 470, 1000, 1.05, arms=arms, look=look, sweat=1 if i == 2 else 0, eyes='normal' if i == 0 else 'wide', mouth=0.1)
        text(c, lb, 260 + i * 470, 1060, 30, '#cfd6e6', FONT_XB, align='center')
    text(c, 'АЛЕКС — REFERENCE', 40, 60, 40, '#ffffff')
    text(c, '16 лет · чёрные растрёпанные волосы · тёмный свитер · уставший напряжённый взгляд', 40, 105, 26, '#9aa3b8', FONT_XB)
    save(s, os.path.join(ROOT, 'assets', 'characters', 'alex_reference.png'))
    # supporting characters
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1b1e2a'))
    person(c, 600, 1000, 1.05, female=True, hairstyle='ponytail', coat='#d4a017', hair='#6b2f1a', look=0.2, mouth=0.1)
    text(c, 'МИРА, 16', 600, 1060, 30, '#cfd6e6', FONT_XB, align='center')
    person(c, 1300, 1000, 1.05, coat='#3f4a3a', hair='#3a2f28', beard=True, cap='#1f2a24', look=-0.2, mouth=0.0)
    text(c, 'ВИКТОР', 1300, 1060, 30, '#cfd6e6', FONT_XB, align='center')
    text(c, 'ВЫЖИВШИЕ — REFERENCE', 40, 60, 40, '#ffffff')
    save(s, os.path.join(ROOT, 'assets', 'characters', 'survivors_reference.png'))
    # location boards
    locs = [('street_night', lambda c: street(c, 0, seed=71)), ('courtyard', lambda c: courtyard_block(c, 0, music_win=(5, 2))),
            ('stairwell', lambda c: stairwell(c, 0)), ('hospital', lambda c: hospital(c, 0)), ('metro_severnaya', lambda c: subway(c, 0, crowd=0)),
            ('forest_road', lambda c: forest_road(c, 0)), ('institute', lambda c: institute_ext(c, 0)), ('lab_0', lambda c: lab(c, 0))]
    for name, fn in locs:
        s = skia.Surface(W, H)
        c = s.getCanvas()
        fn(c)
        vignette(c, 0.6)
        save(s, os.path.join(ROOT, 'assets', 'locations', f'{name}.png'))


if __name__ == '__main__':
    cover()
    refs()
    print('ok')
