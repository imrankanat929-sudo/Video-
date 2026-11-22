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

### Music
The current master uses **LoVibe. – "A Good Man With A Broken Heart"**. The file is
not stored in the repo (copyright), so put it at `assets/music_good_man.mp3` before you build.
It is cut to the edit in `src/audio.py`:
* the track starts 4.12 s in, so its intro plays under the hook and **the drop lands
  on the scene-2 cut (0:06.3)**;
* full silence on «Почему?» (0:22), back in with the next scene;
* -14 dB breath on «Но вот что важно» (1:08), swelling back;
* fades out under the logo; ducked under the narrator everywhere.

Other options:
```bash
MUSIC=synth SKIP_RENDER=1 ./build.sh                      # original built-in score
MUSIC_FILE=/path/track.mp3 MUSIC_SKIP=0 SKIP_RENDER=1 ./build.sh
```
