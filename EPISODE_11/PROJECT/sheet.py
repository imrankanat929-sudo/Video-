import sys, skia
from engine import *
def sheet(look, name, out):
    s = skia.Surface(1600, 1300); c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(1600,1300), P(shader=lin(0,0,0,1300,['#2a2c33','#1c1d22'])))
    for i,(f,tu,bk) in enumerate([(0,0,False),(0,0.45,False),(1,None,False),(0,0,True)]):
        draw_person(c, 200+i*330, 760, 1.0, look, facing=f, turn=tu, back=bk, t=0.3)
    text(c, name, 40, 70, 54, '#cfd2da', align='left')
    for i,e in enumerate(['neutral','surprised','angry','worried','scared','smirk','smile']):
        c.save(); c.translate(130+i*220, 1050); draw_head(c, look, 80, 0.15 if i%2 else -0.1, e, t=1); c.restore()
    s.makeImageSnapshot().save(out, skia.kPNG)
sheet(HERO,'MAIN CHARACTER','../CHARACTERS/main_character.png')
sheet(FRIEND,'BEST FRIEND','../CHARACTERS/friend_character.png')
