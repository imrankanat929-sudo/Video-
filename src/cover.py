"""Cover / thumbnail for the short."""
import sys, cairo
from core import *
from lang import tr, LANG
import shots, render
render.init()
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
setc(c, (0, 0, 0)); c.paint()
shots.s_reflection2(c, 100.6)
c.rectangle(0, 0, W, H); setc(c, (0, 0, 0), 0.25); c.fill()
g = cairo.LinearGradient(0, 0, 0, 700); g.add_color_stop_rgba(0, 0, 0, 0, 0.9); g.add_color_stop_rgba(1, 0, 0, 0, 0)
c.set_source(g); c.rectangle(0, 0, W, 700); c.fill()
g = cairo.LinearGradient(0, 1250, 0, H); g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.95)
c.set_source(g); c.rectangle(0, 1250, W, H - 1250); c.fill()
c.set_source_surface(render.VIG); c.paint()
fit_text(c, tr("А ЧТО, ЕСЛИ"), W / 2, 230, 110, 960, c=(1, 1, 1), weight="black", outline=14, oa=0.9)
fit_text(c, tr("ВСЕ ЛЮДИ"), W / 2, 360, 130, 960, c=(1, 1, 1), weight="black", outline=14, oa=0.9)
fit_text(c, tr("ЗАБЫЛИ ТЕБЯ?"), W / 2, 500, 140, 980, c=hexc('#ff3b3b'), weight="black", outline=14, oa=0.9)
fit_text(c, tr("ТВОЁ ОТРАЖЕНИЕ УЛЫБАЕТСЯ…"), W / 2, 1640, 64, 960, c=(1, 1, 1), weight="black", outline=12, oa=0.9)
s.write_to_png(sys.argv[1])
