# WHAT IF A BEAR ATTACKED YOU? — вертикальный short (9:16, 2:00)

## Результат (`output/`)
| Файл | Описание |
|---|---|
| `bear_video_ru.mp4` | Русская версия: 1080×1920, 30 fps, H.264 High, AAC 192k, 120 с, −14 LUFS, вшитые субтитры |
| `bear_video_en.mp4` | Английская версия, те же параметры |
| `bear_subtitles_ru.srt` / `bear_subtitles_en.srt` | Отдельные субтитры (≤2 строк, синхронизированы по словам) |
| `bear_thumbnail.png` | Обложка RU 1080×1920 «ТЫ ВСТРЕТИЛ МЕДВЕДЯ!» |
| `bear_thumbnail_en.png` | Обложка EN 1080×1920 «YOU MET A BEAR!» |

## Как собрано
Всё процедурное (свой код, без сторонних ассетов): графика — skia, музыка и звуки — синтез в numpy/scipy, озвучка — предоставленные mp3.

```
python3 src/transcribe.py medium   # тайминги слов озвучки (faster-whisper)
python3 src/render.py              # видеоряд -> build/base.mp4 (4 процесса)
python3 src/audio.py               # музыка + SFX + озвучка с дакингом
python3 src/subs.py                # SRT + ASS-титры
python3 src/thumbnail.py           # обложка
python3 src/export.py              # финальные mp4
```
- `src/timeline.py` — раскладка фраз озвучки по сценам ТЗ.
- `src/shots.py` — раскадровка (~40 планов, 9 сцен).
- `src/hero.py`, `src/bear.py`, `src/world.py` — персонаж, медведь, лес (псевдо-3D камера, туман, лучи, частицы).
