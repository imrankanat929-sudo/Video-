# WHAT IF…? — Episode 01

**«Тебе подарили 10 биткоинов. Но они краденые»**: 2D-анимация, 1920×1080, 30 fps.

Всё нарисовано кодом на HTML5 Canvas: комната, окно с туманом, герой, телефоны, интерфейсы. Стоковые картинки и видео не используются. Музыка и звуковые эффекты тоже сгенерированы кодом (`tools/audio.py`).

## Готовое видео

- `output/WhatIf_EP01_ru.mp4`: русская версия

## Структура

```
project/
  index.html                 плеер предпросмотра (?lang=ru|en) и точка входа для рендера
  src/core.js                движок: камера с параллаксом, зерно, виньетка, пыль, easing
  src/art.js                 иллюстрации: комната, окно и туман, стол, монитор, телефон, герой
  src/ui.js                  экраны: уведомление, кошелёк, новость, чат, профиль, 112, схема транзакций, проверка
  src/scenes.js              18 планов (сцены), привязанные к озвучке
  src/main.js                покадровый рендер, переходы (cut / fade / black / flash), фоновые плиты
  config/timeline.ru.json    НАСТРОЙКИ МОНТАЖА: планы, переходы, ключевые точки, звуковые события, автоматизация музыки
  config/strings.ru.json     весь текст на экране (RU)
  config/strings.en.json     весь текст на экране (EN), заготовка
  config/transcript_ru.json  расшифровка озвучки с таймингом слов (Whisper)
  assets/audio/              voice_ru.mp3 (исходник), music_ru.wav, sfx_ru.wav, mix_ru.wav
  assets/backgrounds/        отдельные фоновые иллюстрации (PNG 1920×1080)
  assets/fonts/              Inter, JetBrains Mono
  tools/render.js            рендер MP4 (Playwright + ffmpeg)
  tools/audio.py             генерация музыки и SFX, сведение с голосом
  tools/export_backgrounds.js  экспорт фонов
  tools/stills.js            контрольные кадры
```

## Как собрать

```bash
cd project
pip install numpy scipy
python3 tools/audio.py ru            # музыка + эффекты + сведение → assets/audio/mix_ru.wav
node tools/render.js ru 3            # 3 параллельных потока → output/WhatIf_EP01_ru.mp4
node tools/export_backgrounds.js     # фоны → assets/backgrounds/
node tools/server.js 8080            # предпросмотр: http://127.0.0.1:8080/index.html
```

## Английская версия

1. Положить озвучку в `assets/audio/voice_en.mp3`.
2. Скопировать `config/timeline.ru.json` в `timeline.en.json`, заменить `voice` и `strings`, переставить `shots` и `cues` по таймингу английских слов.
3. `python3 tools/audio.py en && node tools/render.js en 3`
