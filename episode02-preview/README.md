# HUMAN MIND — Эпизод 02 · превью 9:16

- `HUMAN_MIND_EP02_9x16.mp4` — вертикальный ролик 1080×1920, 30 fps, 1:35 (под всю длину трека)
- `HUMAN_MIND_EP02_cover_9x16.png` — превью (обложка) 9:16

Пересборка: `npm i && ./render_all.sh` (нужны node и ffmpeg).
`timeline.js` — общий тайминг, `render.js` — анимация, `audio.js` — звуковые эффекты.
Основная версия — с треком LoVibe (`music_lovibe.mp3`), запасная `HUMAN_MIND_EP02_9x16_gravity.mp4` — с Gravity Eleven. Пересобрать только звук: `SKIP_VIDEO=1 ./render_all.sh`.

## Озвучка
- `voice/script_ru.txt` — текст озвучки с таймкодами (секунда|фраза)
- `voice/ru_voiceover.wav` — готовая русская озвучка (Piper TTS, голос ru_RU-ruslan-medium)
- `voice/build_voice.sh` — пересборка озвучки после правки текста
- Чтобы поставить свою озвучку: `VOICE=путь/к/файлу.wav SKIP_VIDEO=1 ./render_all.sh`
Музыка автоматически приглушается под голосом.
