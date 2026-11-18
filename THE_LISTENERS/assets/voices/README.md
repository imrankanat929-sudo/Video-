Голосовые модели Piper (не хранятся в репозитории, ~63 МБ каждая). Скачать:

    for v in ruslan denis dmitri; do
      curl -L -o ru_$v.onnx      https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/$v/medium/ru_RU-$v-medium.onnx
      curl -L -o ru_$v.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/$v/medium/ru_RU-$v-medium.onnx.json
    done

ruslan — диктор, denis — Алекс, dmitri — Виктор / радио. Женские голоса (Мира, «мама») — gTTS.
