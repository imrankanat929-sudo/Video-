# «Ты проснулся в 90-х»

2D-анимация 1:30 (1920×1080, 30 fps) в стиле VHS-1995 по закадровому тексту.

- `video_90s.mp4` — финальное видео (1080p)
- `preview_720p.mp4` — лёгкое превью для телефона
- `preview_frames.png` — раскадровка из готового видео
- `video_90s_9x16.mp4` — вертикальная версия 9:16 (1080×1920) для Reels/Shorts/TikTok
- `preview_9x16_720p.mp4`, `preview_frames_9x16.png` — превью вертикальной версии
- `cover_9x16.png`, `cover_16x9.png` — обложки для видео
- `src/` — исходники: отрисовка сцен (canvas), синтез звука и музыки, сборка

Сборка: `src/build.sh <voice.mp3> <work_dir> <out.mp4>` (вертикаль: `VERT=1`) (нужны node + playwright, python3 + numpy/scipy, ffmpeg).

## Эпизод 2 — «Ты проснулся в 2005 году» (папка `2005/`)

- `video_2005.mp4` — видео 16:9, 1920×1080, 30 fps, 1:30 (YouTube)
- `video_2005_9x16.mp4` — вертикальная версия 1080×1920 (TikTok/Reels/Shorts)
- `cover_youtube_2005.png` — обложка YouTube 16:9; `cover_tiktok_2005_9x16.png` — обложка TikTok
- `preview_keyframe_2005.png` — кадр из готового ролика; `preview_2005_720p.mp4` — лёгкое превью
- `subtitles_2005.srt` — русские субтитры; `voice_2005.mp3` — озвучка
- `music_2005.wav`, `sfx_2005.wav` — музыка и звуковые эффекты отдельными дорожками
- исходники: `ep2005/` (сборка: `ep2005/build.sh <voice.mp3> <work_dir> <out.mp4>`, вертикаль `VERT=1`)
