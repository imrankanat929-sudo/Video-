"""Render the 12 clips (video only) into ../clips/. Usage:
   python render_clips.py                 # all clips, 4 workers
   python render_clips.py 3 7             # selected clips
   python render_clips.py --preview 3 1.0 6.0   # PNG stills of clip 3 at given times
"""
import os, sys, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script_ep01 import CLIPS
import scenes_ep01 as S
from didao_engine.core import FPS, new_surface, VideoWriter, save_png

OUT = os.path.join(HERE, '..', 'clips')


def render_clip(args):
    cid, lang = args
    clip = next(c for c in CLIPS if c['id'] == cid)
    n = int(round(clip['dur'] * FPS))
    suffix = '' if lang == 'en' else '_RU'
    path = os.path.join(OUT, clip['name'] + suffix + '.mp4')
    surf = new_surface()
    vw = VideoWriter(path)
    t0 = time.time()
    for f in range(n):
        cv = surf.getCanvas()
        cv.clear(0xFF000000)
        S.RENDERERS[cid](cv, f / FPS, f, lang)
        vw.write(surf)
    vw.close()
    return f"{os.path.basename(path)}: {n} frames in {time.time() - t0:.0f}s"


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--preview':
        cid = int(a[1])
        for ts in a[2:]:
            surf = new_surface(); cv = surf.getCanvas(); cv.clear(0xFF000000)
            S.RENDERERS[cid](cv, float(ts), int(float(ts) * FPS), 'en')
            save_png(surf, f'/tmp/claude-0/t/p{cid:02d}_{ts}.png')
        sys.exit()
    ids = [int(x) for x in a] or [c['id'] for c in CLIPS]
    jobs = [(i, 'en') for i in ids] + ([(12, 'ru')] if 12 in ids else [])
    jobs.sort(key=lambda j: -next(c['dur'] for c in CLIPS if c['id'] == j[0]))
    with Pool(4) as p:
        for r in p.imap_unordered(render_clip, jobs):
            print(r, flush=True)
