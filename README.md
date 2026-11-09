# Мир сломался — вертикальные ролики (1080×1920)

Серия 1 «Мир остановился / The World Stopped». Все сцены нарисованы кодом (pycairo),
звук (музыка + эффекты) синтезирован numpy. Голос не встроен — текст для озвучки
с таймкодами лежит в `ep1_voiceover.md`.

```bash
pip install pycairo numpy pillow   # + ffmpeg
python3 render.py --lang both      # out/ep1_ru.mp4, out/ep1_en.mp4 (+ .srt)
python3 render.py --stills 5,30,72 # быстрые превью кадров в out/stills/
```

Тайминг реплик — `LINES` в `mir/ep1.py`. После записи голоса поправь время
начала фраз под реальное аудио и перерендери: субтитры и эмоции героя
подстроятся сами.
