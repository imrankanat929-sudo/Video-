#!/usr/bin/env bash
# Full rebuild of HUMAN MIND — Episode 03 (EN + RU).
# Requires: ffmpeg, python3 with skia-python, numpy, pillow, edge-tts.
set -euo pipefail
cd "$(dirname "$0")"
python3 src/tts.py en ru                 # voice lines + timing (RU first half = supplied recording)
python3 src/audio.py en ru               # build/mix_<lang>.wav
python3 src/export_srt.py en ru          # output/subtitles_<lang>.srt
python3 src/thumbnail.py en output/thumbnail_en.png
python3 src/thumbnail.py ru output/thumbnail_ru.png
for L in en ru; do
  python3 src/render.py video $L 4       # build/video_<lang>.mp4 (silent)
  ffmpeg -y -v error -i build/video_$L.mp4 -i build/mix_$L.wav -map 0:v -map 1:a \
    -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest \
    output/HUMAN_MIND_EP03_deja_vu_$L.mp4
done
