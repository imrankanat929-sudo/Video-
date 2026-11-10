# What If Everyone Forgot You?

A 2-minute 9:16 animated short (YouTube Shorts / TikTok / Reels). Mystery / psychological thriller.

**Final video:** `output/what_if_everyone_forgot_you.mp4` (1080×1920, 30 fps, 2:03, English subtitles, Russian voice-over)

## How it's made
Every frame is drawn by code (Python + Cairo), there are no static images:

| File | What it does |
|---|---|
| `src/person.py` | Character rig matching the character sheet (messy black hair, dark sweater, grey sneakers), with walk/run cycles, arm joints, head turns, blinking, lip-sync and 13 blendable expressions. Also the parents and passers-by. |
| `src/world.py` | Environments: bedroom, hallway, kitchen, street (parallax + crowd), photo album. |
| `src/phone.py` | Phone UIs: lock-screen notifications, chat, call, gallery/chats/contacts vanishing, front camera. |
| `src/shots.py` | 37 shots with camera moves, synced to the voice-over timestamps. |
| `src/subs.py` | English subtitles, chunked and timed to the voice. |
| `src/audio.py` | Procedural score + SFX (notifications, vibration, ringing, glitches, low boom, hard silence at the end), ducked under the voice. |
| `src/render.py` | Multi-process frame renderer → ffmpeg. |

## Rebuild
```bash
pip install pycairo numpy scipy
cd src
python audio.py path/to/voice.mp3 ../output/mix.wav
python render.py ../output/video_noaudio.mp4
ffmpeg -i ../output/video_noaudio.mp4 -i ../output/mix.wav -c:v copy -c:a aac -b:a 192k -shortest ../output/what_if_everyone_forgot_you.mp4
```
Preview single frames: `python render.py --still 12.5,52,100 /tmp/stills`
