"""Профили эпизодов. EP=ep1 (по умолчанию, 16:9) или EP=ep2 (9:16, 30 fps)."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EP = os.environ.get("EP", "ep1")
SR = 44100
FONT_TITLE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"

if EP == "ep2":
    W, H = 1080, 1920
    FPS = 30
    VOICE = ROOT / "ep2" / "assets" / "voiceover.mp3"
    TRANSCRIPT = ROOT / "ep2" / "sync" / "transcript.json"
    CUES = ROOT / "ep2" / "sync" / "cues.json"
    OUT = ROOT / "ep2" / "out"
    BUILD = ROOT / "build" / "ep2"
else:
    W, H = 1920, 1080
    FPS = 24
    VOICE = ROOT / "assets" / "voiceover.mp3"
    TRANSCRIPT = ROOT / "sync" / "transcript.json"
    CUES = ROOT / "sync" / "cues.json"
    OUT = ROOT / "out"
    BUILD = ROOT / "build"
