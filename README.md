# Параллельная Вселенная / Parallel Universe

A 2D animated vertical short (9:16, 1080×1920, 30 fps), about 2 minutes long, with Russian and English versions.
Everything in it is code: the character rig, the sets, the camera, the lighting, the effects, the music and the sound effects.
No stock footage or stock music is used. The only outside inputs are the two voice-over recordings and the character reference image you supplied.

## Final files (`output/`)

| File | What it is |
|---|---|
| `ru/parallel_universe_ru.mp4` | Finished Russian film (H.264 + AAC, burned-in subtitles) |
| `en/parallel_universe_en.mp4` | Finished English film |
| `ru/cover_ru.png`, `en/cover_en.png` | Covers, 1080×1920 |
| `ru/subtitles_ru.srt`, `en/subtitles_en.srt` | Subtitles as separate files |
| `ru/voice_ru.wav`, `en/voice_en.wav` | Voice-over, aligned to the film timeline (starts at 0.5 s) |
| `ru/music_ru.wav`, `ru/sfx_ru.wav` (and the `en` versions) | Original music and sound-effects stems |
| `shared/character_sheet_*.png` | Character reference (front, 3/4, back, profile, expressions, parents) |

## Project (the editable source)

```
anim/core.py       maths, colours, camera, text
anim/character.py  character rig (hero, double, mom, dad): walk/run, arms, expressions, blinking, lip sync
anim/env.py        sets: hallway, bedroom (two versions), kitchen, the changed city, phone UI, the void
anim/film.py       shot list and camera moves, colour grade, distortion and glitch shaders, captions
anim/timing.py     cue sheet per language (from word-level alignment of the voice-over)
anim/audio.py      synthesised score + SFX, ducking under the voice, final mix
anim/cover.py      cover
anim/render.py     multi-process renderer (Skia → ffmpeg)
data/*.json        word timestamps of the two voice-overs
```

To rebuild (needs Python 3, `skia-python`, `numpy`, `scipy` and `ffmpeg`):

```bash
ffmpeg -i assets/voice/voice_ru_source.mp3 -ar 48000 -ac 1 build/voice_ru.wav   # same for en
python3 -m anim.audio ru
python3 -m anim.render ru build/video_ru_noaudio.mp4
ffmpeg -i build/video_ru_noaudio.mp4 -i build/mix_ru.wav -af loudnorm=I=-14:TP=-1.5 -c:v copy -c:a aac -b:a 192k -shortest output/ru/parallel_universe_ru.mp4
```

To preview single frames: `python3 -m anim.render ru preview.png 10 20 30`.
