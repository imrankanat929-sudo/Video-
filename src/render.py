"""Usage:
  python render.py LANG stills t1 t2 ...        -> PNG stills in out/stills
  python render.py LANG chunk F0 F1 OUT.mp4     -> encode frames [F0,F1) to OUT.mp4
"""
import json
import os
import subprocess
import sys

from PIL import Image

from hm_core import FPS, H, W
from hm_scenes import Cues, render_frame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cues(lang):
    with open(os.path.join(ROOT, "build", f"cues_{lang}.json"), encoding="utf-8") as f:
        return Cues(json.load(f), lang)


def main():
    lang, mode = sys.argv[1], sys.argv[2]
    C = cues(lang)
    if mode == "stills":
        os.makedirs(os.environ.get("STILLS", os.path.join(ROOT, "build", "stills")), exist_ok=True)
        for ts in sys.argv[3:]:
            img = render_frame(float(ts), C)
            Image.fromarray(img).save(os.path.join(os.environ.get("STILLS", os.path.join(ROOT, "build", "stills")), f"{lang}_{float(ts):06.2f}.png"))
    elif mode == "chunk":
        f0, f1, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                              "-crf", "15", "-tune", "film", "-pix_fmt", "yuv420p", "-r", str(FPS), out],
                             stdin=subprocess.PIPE)
        for fr in range(f0, f1):
            p.stdin.write(render_frame(fr / FPS, C).tobytes())
        p.stdin.close()
        p.wait()


if __name__ == "__main__":
    main()
