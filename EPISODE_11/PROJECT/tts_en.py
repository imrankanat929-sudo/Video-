# Generates the English voiceover with Kokoro (local neural TTS) and a timing file.
import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
S = sys.argv[1]  # dir with kokoro.onnx / voices.bin
voice = sys.argv[2] if len(sys.argv) > 2 else "am_michael"
k = Kokoro(f"{S}/kokoro.onnx", f"{S}/voices.bin")
lines = [l.strip() for l in open("script_en.txt") if l.strip()]
sr = 24000; out = [np.zeros(int(0.35*sr))]; t = 0.35; timing = []
for i, l in enumerate(lines):
    a, sr = k.create(l, voice=voice, speed=1.0, lang="en-us")
    timing.append({"start": round(t, 3), "end": round(t+len(a)/sr, 3), "text": l})
    out.append(a); t += len(a)/sr
    nxt = lines[i+1] if i+1 < len(lines) else ""
    gap = 1.0 if nxt.startswith("Day") or i == 0 else (0.75 if nxt.startswith('"') or l.endswith('"') else 0.45)
    out.append(np.zeros(int(gap*sr))); t += gap
    print(i, round(t,1), l[:50], flush=True)
sf.write("../EN_VERSION/voiceover_en.wav", np.concatenate(out), sr)
json.dump(timing, open("timing_en.json", "w"), indent=1)
