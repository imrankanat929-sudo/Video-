# HUMAN MIND — Episode 01
**«Твой мозг принимает решения раньше, чем ты это осознаёшь»** — a minimalist black-and-white psychology short based on Daniel Kahneman's *Thinking, Fast and Slow*.

1920×1080 · 30 fps · 1:45 · Russian voiceover

## Deliverables (`deliverables/`)
| File | What |
|---|---|
| `HUMAN_MIND_EP01_RU.mp4` | Final video (H.264 + AAC, mixed to −14 LUFS) |
| `scenes/01…06_*.mp4` | Individual scenes cut from the final video |
| `audio/mix.flac` | Final mix |
| `audio/voiceover.flac` · `music_edit.flac` · `sfx.flac` | Stems: VO, edited music, synthesized SFX |
| `thumbnail_ru.png` | 1920×1080 thumbnail (16:9) |
| `thumbnail_ru_9x16.png` | 1080×1920 thumbnail (9:16, Shorts/Reels/TikTok) |

## Timeline
| Time | Scene | On-screen text |
|---|---|---|
| 0:00–0:03.4 | **Hook**: a spark in the head comes before the "?" and the hand-raise; flash on the music drop | ТВОЙ МОЗГ ПРИНИМАЕТ РЕШЕНИЯ / РАНЬШЕ, ЧЕМ ТЫ ЭТО ОСОЗНАЁШЬ |
| 0:03–0:27 | Decisions: shirt, clock, phone, two doors, autopilot ticks, Kahneman's book, two modes | СКОЛЬКО РЕШЕНИЙ ТЫ ПРИНИМАЕШЬ КАЖДЫЙ ДЕНЬ? |
| 0:27–0:44 | System 1: fast brain network, street recognition, sudden sound → instant turn | СИСТЕМА 1 — БЫСТРОЕ МЫШЛЕНИЕ |
| 0:44–1:01 | Hasty conclusions, the confident presenter ("ЗНАЕТ ВСЁ" → "ЗНАЕТ ВСЁ?", he becomes an outline) | ПЕРВОЕ ВПЕЧАТЛЕНИЕ МОЖЕТ ОБМАНУТЬ |
| 1:00–1:22 | Freeze (tape-stop) → slowly rotating brain, magnifier, comparison, checklist, effort meter | СИСТЕМА 2 — МЕДЛЕННОЕ МЫШЛЕНИЕ |
| 1:22–1:45 | Two paths: first impression vs facts, "pause for a second", outro | ПОДУМАЙ ДВАЖДЫ. → HUMAN MIND |

Both paths stay valid in the ending: the video does not claim that fast thinking is always wrong.

## Editable project (`project/`)
- `render.html`: all animation. It is code-driven, with one function per scene; timings are given in voiceover seconds through `v()`. Open it in a browser and call `frame(t)` in the console to preview any moment. `?lang=en` switches all on-screen text to English, and `?thumb=1` renders the thumbnail layout.
- `render.mjs`: renders frames with Playwright and encodes them with ffmpeg.
- `audio_mix.py`: builds the music edit (aligns the beat drop to the hook, applies a tape-stop and low-pass for System 2, ducks under the VO), synthesizes the SFX and produces the mix.
- `assets/`: music, voiceover, word-level VO timings, style reference.

```bash
cd project
python3 audio_mix.py ../deliverables/audio            # -> voiceover/music_edit/sfx/mix .wav
node render.mjs --out video.mp4 --workers 4            # add --lang en for English text
ffmpeg -i video.mp4 -i ../deliverables/audio/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k out.mp4
node render.mjs --thumb 1 --stills 0.62 --dir thumbs   # thumbnail 16:9
node render.mjs --thumb v --stills 0.62 --dir thumbs   # thumbnail 9:16
```
Requires Node + Playwright (Chromium), Python 3 with numpy and scipy, ffmpeg, and the Inter font.

## English version
To make the English version, put an English voiceover in `assets/`, shift the `v()` timings in `render.html` to its word timings, run `audio_mix.py --vo <file>`, and render with `--lang en`.
