"""Быстрый просмотр кадров: python -m src.preview 12.5 38 ... -> build/preview_*.jpg"""
import sys, time
from PIL import Image
from .config import BUILD
from .config import EP
if EP.startswith("ep2"):
    from .ep2.shots import render_frame
else:
    from .shots import render_frame
from .gfx import to_u8

if __name__ == "__main__":
    BUILD.mkdir(exist_ok=True)
    for a in sys.argv[1:]:
        t = float(a); t0 = time.time()
        img = render_frame(t)
        Image.fromarray(to_u8(img)).resize((img.shape[1] // 2, img.shape[0] // 2)).save(BUILD / f"preview_{t:07.2f}.jpg", quality=88)
        print(f"{t:7.2f}  {time.time()-t0:.2f}s", flush=True)
