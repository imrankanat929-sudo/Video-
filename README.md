# «Ты проснулся в 90-х»

2D-анимация 1:30 (1920×1080, 30 fps) в стиле VHS-1995 по закадровому тексту.

- `video_90s.mp4` — финальное видео (1080p)
- `preview_720p.mp4` — лёгкое превью для телефона
- `preview_frames.png` — раскадровка из готового видео
- `video_90s_9x16.mp4` — вертикальная версия 9:16 (1080×1920) для Reels/Shorts/TikTok
- `preview_9x16_720p.mp4`, `preview_frames_9x16.png` — превью вертикальной версии
- `src/` — исходники: отрисовка сцен (canvas), синтез звука и музыки, сборка

Сборка: `src/build.sh <voice.mp3> <work_dir> <out.mp4>` (вертикаль: `VERT=1`) (нужны node + playwright, python3 + numpy/scipy, ffmpeg).
