"""Generate RU + EN narration with Piper neural TTS (offline). One WAV per line."""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.dirname(__file__))
from script_ep01 import CLIPS
VOICES = os.environ.get('DIDAO_VOICES', '/tmp/claude-0/voices')
CFG = {'ru': ('ru_RU-dmitri-medium', 1.12), 'en': ('en_US-ryan-high', 1.08)}
OUT = os.path.join(os.path.dirname(__file__), '..', 'voiceover')
report = {}
for lang, (voice, ls) in CFG.items():
    for clip in CLIPS:
        for i, line in enumerate(clip['vo']):
            text = line[1] if lang == 'ru' else line[2]
            fn = os.path.join(OUT, lang, f"VO_{lang.upper()}_{clip['id']:02d}_{i+1}.wav")
            subprocess.run([sys.executable, '-m', 'piper', '-m', f'{VOICES}/{voice}.onnx', '-f', fn,
                            '--length-scale', str(ls), '--sentence-silence', '0.35'], input=text.encode(), check=True,
                           stderr=subprocess.DEVNULL)
            with wave.open(fn) as w:
                d = w.getnframes() / w.getframerate()
            report[os.path.basename(fn)] = dict(text=text, start=line[0], dur=round(d, 2), end=round(line[0] + d, 2), clip_dur=clip['dur'])
json.dump(report, open(os.path.join(OUT, 'vo_timing.json'), 'w'), ensure_ascii=False, indent=1)
for k, v in report.items():
    flag = '  <-- OVER' if v['end'] > v['clip_dur'] - 0.3 else ''
    print(f"{k:22s} {v['start']:5.1f} +{v['dur']:5.2f} = {v['end']:5.2f} / {v['clip_dur']}{flag}")
