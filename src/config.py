from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
FPS = 24
SR = 44100
VOICE = ROOT / "assets" / "voiceover.mp3"
TRANSCRIPT = ROOT / "sync" / "transcript.json"
CUES = ROOT / "sync" / "cues.json"
OUT = ROOT / "out"
BUILD = ROOT / "build"
FONT_TITLE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
