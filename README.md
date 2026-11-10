# What If Everyone Forgot You?

A 2-minute 9:16 animated short (YouTube Shorts / TikTok / Reels). Mystery / psychological thriller.

Two versions (1080×1920, 30 fps, 2:03):

| | Video | Cover |
|---|---|---|
| 🇷🇺 Russian voice, Russian subtitles & text | `output/what_if_everyone_forgot_you_RU.mp4` | `output/cover_ru.png` |
| 🇬🇧 English voice, English subtitles & text | `output/what_if_everyone_forgot_you_EN.mp4` | `output/cover_en.png` |

The English voice-over (`assets/voiceover_en.wav`) is synthesized with Kokoro TTS; every line is placed at the same moment as the Russian line, so the animation stays in sync.

## How it's made
Every frame is drawn by code (Python + Cairo), there are no static images:

| File | What it does |
|---|---|
| `src/person.py` | Character rig matching the character sheet (messy black hair, dark sweater, grey sneakers), with walk/run cycles, arm joints, head turns, blinking, lip-sync and 13 blendable expressions. Also the parents and passers-by. |
| `src/world.py` | Environments: bedroom, hallway, kitchen, street (parallax + crowd), photo album. |
| `src/phone.py` | Phone UIs: lock-screen notifications, chat, call, gallery/chats/contacts vanishing, front camera. |
| `src/shots.py` | 37 shots with camera moves, synced to the voice-over timestamps. |
| `src/subs.py` | Russian subtitles, chunk starts aligned to word timestamps from `assets/transcript.json`. |
| `src/audio.py` | Procedural score + SFX (notifications, vibration, ringing, glitches, low boom, hard silence at the end), ducked under the voice. |
| `src/lang.py` | Language switch (`VIDEO_LANG=ru` / `en`) for all on-screen text. |
| `src/tts_en.py` | Builds the English voice-over aligned to the Russian timing. |
| `src/render.py` | Multi-process frame renderer → ffmpeg. |

## Rebuild
```bash
pip install pycairo numpy scipy
cd src
python audio.py path/to/voice.mp3 ../output/mix.wav
VIDEO_LANG=ru python render.py ../output/video_noaudio.mp4   # or VIDEO_LANG=en with assets/voiceover_en.wav
ffmpeg -i ../output/video_noaudio.mp4 -i ../output/mix.wav -c:v copy -c:a aac -b:a 192k -shortest ../output/what_if_everyone_forgot_you.mp4
```
Preview single frames: `python render.py --still 12.5,52,100 /tmp/stills`
