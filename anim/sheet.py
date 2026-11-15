"""Character reference sheet (rendered from the same rig used in the film)."""
import sys, skia
from .core import *
from .character import Character, HERO, MOM, DAD, pose

def render(path, lang="ru"):
    Wd, Hd = 2160, 2400
    s = skia.Surface(Wd, Hd); c = s.getCanvas()
    c.clear(col("#24262c"))
    hero = Character(HERO)
    for gy in (190, 560, 930, 1300):
        c.drawLine(60, gy, 1700, gy, paint("#ffffff", 0.05, stroke=2))
    views = [dict(tr=0.0), dict(tr=0.55), dict(view="back"), dict(tr=-0.95)]
    labels = {"ru": ["СПЕРЕДИ", "3/4", "СЗАДИ", "ПРОФИЛЬ"], "en": ["FRONT", "3/4", "BACK", "SIDE"]}[lang]
    for i, v in enumerate(views):
        x = 260 + i * 410
        hero.draw(c, x, 1420, 1.25, pose(t=0.3, **v))
        text_center(c, labels[i], x, 1500, 34, "#8d93a3", "SemiBold")
    exprs = ["neutral", "surprised", "angry", "worried", "scared", "smug"]
    names = {"ru": ["Спокойный", "Удивлён", "Злится", "Тревога", "Страх", "Двойник"],
             "en": ["Neutral", "Surprised", "Angry", "Worried", "Scared", "The Double"]}[lang]
    text_center(c, "ВЫРАЖЕНИЯ" if lang == "ru" else "EXPRESSIONS", 260, 1620, 40, "#c9ccd6", "Bold")
    for i, e in enumerate(exprs):
        x = 190 + i * 285
        c.save(); c.clipRect(skia.Rect.MakeXYWH(x - 140, 1650, 280, 520))
        hero.draw(c, x, 3290, 1.7, pose(expr=e, t=1.0, tr=0.0, eye_glint=0.5 if e == "smug" else 0))
        c.restore()
        text_center(c, names[i], x, 2230, 34, "#8d93a3", "SemiBold")
    # side panel
    c.drawRect(skia.Rect.MakeLTRB(1760, 0, 2160, 2400), paint("#1e2025"))
    t1 = "ГЛАВНЫЙ ГЕРОЙ" if lang == "ru" else "MAIN CHARACTER"
    text_center(c, t1, 1960, 110, 44, "#e6e8ee", "ExtraBold")
    info = (["Возраст: 14–16", "Волосы: чёрные, лохматые", "Одежда: тёмный свитер", "Стиль: 2D"] if lang == "ru"
            else ["Age: 14–16", "Hair: black, messy", "Clothes: dark sweater", "Style: 2D"])
    for j, s_ in enumerate(info):
        text_center(c, s_, 1960, 180 + j * 52, 25, "#a9adb9", "Medium")
    for j, cc in enumerate([HERO.skin, HERO.hair, HERO.top, HERO.pants, HERO.shoe]):
        c.drawCircle(1830 + j * 65, 440, 26, paint(cc)); c.drawCircle(1830 + j * 65, 440, 26, paint("#ffffff", 0.2, stroke=2))
    mom, dad = Character(MOM), Character(DAD)
    text_center(c, "РОДИТЕЛИ" if lang == "ru" else "PARENTS", 1960, 560, 36, "#c9ccd6", "Bold")
    mom.draw(c, 1870, 1250, 0.6, pose(tr=0.2, t=0.5))
    dad.draw(c, 2060, 1250, 0.6, pose(tr=-0.2, t=0.5))
    s.makeImageSnapshot().save(path)

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "ru")
