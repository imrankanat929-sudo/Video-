# DIDAO — animated series

Original 2D cartoon in a neon "Vice" city style. One recurring hero, 2-minute episodes, 6 episodes per season, every episode ends on a cliffhanger.

## Episode 1 — «За день до GTA 6» / ONE DAY BEFORE GTA 6
- `ep01/output/DIDAO_E01_ONE_DAY_BEFORE_GTA6.mp4`: the finished film (1920×1080, 16:9, 30 fps, 2:00, burned-in RU subtitles, −14 LUFS)
- `ep01/output/DIDAO_E01_cover_1280x720.jpg` and `cover.png`: the YouTube thumbnail
- `ep01/output/DIDAO_E01_subtitles_ru.srt`: subtitles as a separate file

### Pipeline (`ep01/build.sh`)
1. `render/shots.js`: 25 shots, each 3–8 s, each rendered as **its own clip** (`render/render.mjs shots` → `output/shots/*.mp4`)
2. `render/lib.js`: shared art library. The hero is drawn by one function, `hero()`, so face, hair, sweater and proportions match in every shot (see `assets/character_sheet_reference.png`)
3. `audio/music.py`: original procedural score (epic → sad piano → electronic → energetic → epic → suspense) plus SFX synced to on-screen events
4. `audio/make_subs.py`: subtitles from the voice-over word timings (voice-over starts at 0:02)
5. Assembly: cross-fades between the clips, colour grade, music ducked under the voice, loudness normalised

Requirements: ffmpeg with libass, Node and Playwright (Chromium), Python with numpy. `SKIP_RENDER=1 ./build.sh` re-assembles without re-rendering the shots.

## Episode 1, vertical English cut — `ep01_en_vertical/`
- `output/ONE_DAY_BEFORE_GTA6_EN_9x16.mp4`: 1080×1920 (9:16), 2:00, English voice-over and burned-in English subtitles. No DIDAO branding; the channel in the story is simply "My Channel".
- `output/ONE_DAY_BEFORE_GTA6_EN_preview_1080x1920.jpg`: the vertical preview (thumbnail)
- `output/ONE_DAY_BEFORE_GTA6_EN_subtitles.srt`
- `render/shots_v.js`: the 25 shots re-composed for the vertical frame. They reuse the hero and art from `ep01/render/lib.js`.
- `audio/make_vo.py`: English VO, made locally with the Kokoro TTS model (`am_puck` voice). Each line sits at the same time as in the Russian cut. The score and SFX are shared with `ep01/audio`.
- Build: `./render.sh shots` then `SKIP_RENDER=1 ./build.sh`
