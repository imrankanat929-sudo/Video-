# HUMAN MIND — Episode 01: «Почему мы хотим всем нравиться?»

Minimalist black-and-white psychology explainer, 1920×1080, 30 fps, ~1:42.
Fully procedural: every frame is drawn in code (pycairo), and the score and
sound effects are synthesized in code (numpy). Nothing is hand-keyframed, so any
timing change is a one-line edit.

## How sync works
`assets/voiceover_ru.mp3` was transcribed with word-level timestamps
(`assets/transcript.json`). `src/timeline.py` keeps those word times and is the
single source of truth:

* every animation beat in `src/scenes.py` starts on a word (`T["lovushka"]`, …);
* every whoosh / click / impact in the cue sheet (`SFX`) uses the same times;
* every music section in `src/audio.py` starts its bar grid on a scene cut, so
  downbeats, drops and impacts land on the narration;
* music is side-chain ducked under the voice and the master is normalized to -14 LUFS.

## Scenes (video time)
| # | scene | time | narration |
|---|-------|------|-----------|
| 01 | Hook: crowd snaps its gaze onto you, title word by word | 0:00–0:06 | «Почему мы так сильно хотим всем нравиться?» |
| 02 | Fear of judgment: opinion ▲→■, the idea bulb goes out, the forced «ха-ха» | 0:06–0:22 | «Ты можешь изменить своё мнение…» |
| 03 | «Почему?» impact | 0:22–0:23 | |
| 04 | Network, then campfire, then safety dome, then an approval chart (a nod to the reference frame) | 0:23–0:42 | «Дело в том, что…» |
| 05 | Brain: connection, acceptance, rejection, emotions | 0:42–0:54 | «Когда нас принимают…» |
| 06 | The trap: cage, switching ▲/● masks, real self ★ fading | 0:54–1:08 | «И постепенно появляется ловушка…» |
| 07 | Can't please everyone, then the mirror and confidence | 1:08–1:25 | «Но вот что важно…» |
| 08 | Walking forward past old masks, final message, logo | 1:25–1:42 | «А теперь подумай…» |

## Build
```bash
pip install pycairo numpy pillow scipy      # + ffmpeg, Inter font
./build.sh                                  # everything -> ../deliverables
python3 src/render.py still 55.7 frame.png  # preview any moment
```

### Using a different music track
Pass any licensed audio file you have:
```bash
MUSIC_FILE=/path/to/track.mp3 SKIP_RENDER=1 ./build.sh
```
The built-in score is written to match the scene cuts. A track you swap in keeps
the voice ducking, but its beats will not line up with the cuts.
