# WHAT IF…? — Episode 01

**«Тебе подарили 10 биткоинов. Но они краденые»**: 2D-анимация, 1920×1080, 30 fps.

Всё нарисовано кодом на HTML5 Canvas: комната, окно с туманом, герой, телефоны, интерфейсы. Стоковые картинки и видео не используются. Музыка и звуковые эффекты тоже сгенерированы кодом (`tools/audio.py`).

## Готовое видео

- `output/WhatIf_EP01_ru.mp4`: полная русская версия, 3:04 (H.264)
- `output/WhatIf_EP01_ru_short.mp4`: короткая версия, 72 секунды (первая озвучка)
- `output/thumbnail_ru.png`: превью 1280×720 (`thumbnail_ru_1080.png` — 1920×1080, `thumbnail_ru_9x16.png` — вертикальное 1080×1920)

### Вертикальная версия для Shorts (плоский стиль)

- `output/WhatIf_EP01_ru_shorts.mp4`: 1080×1920, 2:59,6 (укладывается в лимит Shorts 3:00)
- `output/thumbnail_ru_v_9x16.png`: превью для неё
- монтаж: `config/timeline.ru_v.json` (генератор `tools/make_timeline_ru_v.py`), графика: `src/flat.js`
- сборка: `python3 tools/audio.py ru_v && node tools/render.js ru_v 3 && node tools/thumbnail.js ru_v`

### Английская версия (Shorts, плоский стиль)

- `output/WhatIf_EP01_en_shorts.mp4`: 1080×1920, 2:35
- `output/thumbnail_en_v_9x16.png`: превью
- монтаж: `config/timeline.en_v.json` (генератор `tools/make_timeline_en_v.py`), озвучка `assets/audio/voice_en.mp3`
- сборка: `python3 tools/audio.py en_v && node tools/render.js en_v 3 && node tools/thumbnail.js en_v`

## Структура

```
project/
  index.html                 плеер предпросмотра (?lang=ru|en) и точка входа для рендера
  src/core.js                движок: камера с параллаксом, зерно, виньетка, пыль, easing
  src/art.js                 иллюстрации: комната, окно и туман, стол, монитор, телефон, герой
  src/ui.js                  экраны: уведомление, кошелёк, новость, чат, профиль, 112, схема транзакций, проверка
  src/scenes.js              планы короткой версии + общие композиции (комната, стол, телефон, монитор)
  src/shots.js               универсальные типы планов для полной версии (параметры — в timeline)
  src/main.js                покадровый рендер, переходы (cut / fade / black / flash), фоновые плиты
  config/timeline.ru.json    НАСТРОЙКИ МОНТАЖА полной версии: 48 планов, переходы, звуки, музыка
  config/timeline.ru_short.json  то же для короткой версии
  tools/make_timeline_ru.py  генератор timeline.ru.json (времена по словам озвучки)
  tools/thumbnail.js         превью для YouTube
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
