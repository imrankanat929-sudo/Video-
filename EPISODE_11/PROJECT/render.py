"""Render video frames for one language.
usage: python3 render.py ru|en video  <chunk_index> <n_chunks> <out.mp4>
       python3 render.py ru|en stills <out_dir>     (one still per shot)"""
import sys, json, subprocess, skia
from scenes import *

FPS = 30
lang, mode = sys.argv[1], sys.argv[2]
tm = json.load(open(f'timing_{lang}_full.json'))
L = dict(LANG[lang]); L['_code'] = lang
shots, END = build_timeline(tm['S'], tm['E'])
surf = skia.Surface(W, H)
c = surf.getCanvas()

def frame(t):
    c.clear(skia.ColorBLACK)
    render_frame(c, t, shots, L)
    return surf

if mode == 'stills':
    import os; os.makedirs(sys.argv[3], exist_ok=True)
    for i, s in enumerate(shots):
        frame(s['a'] + (s['b'] - s['a']) * 0.6).makeImageSnapshot().save(f"{sys.argv[3]}/scene_{i+1:02d}_{s['f'].__name__[3:]}.png", skia.kPNG)
    print(len(shots), 'shots, end', END)
elif mode == 'at':
    for tt in sys.argv[4:]:
        frame(float(tt)).makeImageSnapshot().save(f"{sys.argv[3]}/t_{tt}.png", skia.kPNG)
else:
    k, n, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    total = int(END * FPS)
    f0, f1 = total * k // n, total * (k + 1) // n
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12',
                           '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        img = frame(fi / FPS).makeImageSnapshot()
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
