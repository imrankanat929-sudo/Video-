# Short muttered phrases for the "crowd of thoughts" layer (played reversed + filtered, so language-neutral).
import sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
S = sys.argv[1]
k = Kokoro(f"{S}/kokoro.onnx", f"{S}/voices.bin")
phr = ["I am late again", "did I lock the door", "what is for dinner", "she never called back", "I hate this job",
       "is he looking at me", "I need more money", "what if they find out", "just smile and nod", "I forgot my keys",
       "nobody understands", "I want to go home", "the exam is tomorrow", "why did I say that", "keep walking"]
vo = ["af_bella", "am_michael", "af_sarah", "am_adam", "bf_emma", "bm_george", "af_nicole", "am_puck"]
out = []
for i, p in enumerate(phr):
    a, sr = k.create(p, voice=vo[i % len(vo)], speed=1.0, lang="en-us")
    out.append(a)
L = max(len(a) for a in out)
arr = np.zeros((len(out), L), np.float32)
for i, a in enumerate(out): arr[i, :len(a)] = a
np.save(f"{S}/murmurs.npy", arr); print(arr.shape, sr)
