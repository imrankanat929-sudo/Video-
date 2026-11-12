import json, sys, subprocess, numpy as np
def load(p):
    b=subprocess.run(['ffmpeg','-v','quiet','-i',p,'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    return np.frombuffer(b,np.float32).copy()
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8")
for lang in ["ru", "en"]:
    segs, info = m.transcribe(load(f"assets/vo_{lang}.mp3"), language=lang, word_timestamps=True, beam_size=5, vad_filter=False)
    out = []
    for s in segs:
        out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "words": [{"w": w.word.strip(), "s": w.start, "e": w.end} for w in s.words]})
    json.dump(out, open(f"build/words_{lang}.json", "w"), ensure_ascii=False, indent=1)
    for s in out: print(lang, f"{s['start']:6.2f}-{s['end']:6.2f}", s["text"])
