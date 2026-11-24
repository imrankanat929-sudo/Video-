# HUMAN MIND — Episode 03: Why does déjà vu happen?

Sources for the RU/EN animated episode (1920×1080, 30 fps, 1:44).

- `src/script.py` — narration, on-screen text, timing
- `src/tts.py` — voice lines (edge-tts) + timing
- `src/render.py` — skia animation renderer
- `src/audio.py` — VO + music + synthesized sound design mix
- `src/thumbnail.py`, `src/export_srt.py`
- `output/` — thumbnails and subtitles

Not in git (put them in `assets/` before running `./build.sh`):
the supplied Russian narration (`ru_supplied_narration.mp3`, transcribed into
`ru_supplied_words.json`) and the background music (`music_lovibe_a_good_man_with_a_broken_heart.mp3`).
