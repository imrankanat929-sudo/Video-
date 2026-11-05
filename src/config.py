"""Профили эпизодов. EP=ep1 (по умолчанию, 16:9) или EP=ep2 (9:16, 30 fps), EP=ep2en (то же, английская версия)."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EP = os.environ.get("EP", "ep1")
SR = 44100
FONT_TITLE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"

LANG = "en" if EP.endswith("en") else "ru"

def L(ru, en):
    """Текст на нужном языке (EP=ep2en -> английский)."""
    return en if LANG == "en" else ru

if EP in ("ep2", "ep2en"):
    W, H = 1080, 1920
    FPS = 30
    VOICE = ROOT / EP / "assets" / "voiceover.mp3"
    TRANSCRIPT = ROOT / EP / "sync" / "transcript.json"
    CUES = ROOT / EP / "sync" / "cues.json"
    OUT = ROOT / EP / "out"
    BUILD = ROOT / "build" / EP
else:
    W, H = 1920, 1080
    FPS = 24
    VOICE = ROOT / "assets" / "voiceover.mp3"
    TRANSCRIPT = ROOT / "sync" / "transcript.json"
    CUES = ROOT / "sync" / "cues.json"
    OUT = ROOT / "out"
    BUILD = ROOT / "build"
