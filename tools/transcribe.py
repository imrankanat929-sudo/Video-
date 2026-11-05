"""Распознавание озвучки с таймкодами слов -> sync/transcript.json (faster-whisper)."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "voiceover.mp3"
dst = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "sync" / "transcript.json"
raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(src), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
model = WhisperModel("medium", device="cpu", compute_type="int8")
segs, _ = model.transcribe(audio, language=(sys.argv[3] if len(sys.argv) > 3 else "ru"), word_timestamps=True, vad_filter=True)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("->", dst)
