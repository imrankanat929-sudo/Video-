#!/usr/bin/env bash
# Full build: scenes -> audio -> final video, per-scene clips with sound, thumbnail.
# Requires: python3 (pycairo numpy pillow scipy), ffmpeg, Inter font.
set -euo pipefail
cd "$(dirname "$0")"
OUT=out
mkdir -p "$OUT"/scenes "$OUT"/audio ../deliverables

if [[ "${SKIP_RENDER:-0}" != 1 ]]; then
  (cd src && python3 render.py scenes)
fi
(cd src && python3 audio.py)

# loudness-normalised master audio (YouTube-friendly -14 LUFS)
ffmpeg -loglevel error -y -i "$OUT"/audio/mix_raw.wav \
  -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 "$OUT"/audio/mix.wav

# join the scene segments (identical encoder settings -> stream copy)
: > "$OUT"/concat.txt
for s in 01_hook 02_judgment 03_why 04_society 05_brain 06_trap 07_realization 08_final; do
  echo "file 'scenes/$s.mp4'" >> "$OUT"/concat.txt
done
ffmpeg -loglevel error -y -f concat -safe 0 -i "$OUT"/concat.txt -c copy "$OUT"/video_silent.mp4

# final master: re-encode to keep the file < 100 MB, AAC 320k
ffmpeg -loglevel error -y -i "$OUT"/video_silent.mp4 -i "$OUT"/audio/mix.wav \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -tune animation -pix_fmt yuv420p \
  -c:a aac -b:a 320k -shortest -movflags +faststart \
  ../deliverables/HUMAN_MIND_EP01_final_1080p.mp4

# per-scene clips (cut from the master, with their slice of the soundtrack)
mkdir -p ../deliverables/scenes ../deliverables/audio
python3 - <<'PY'
import subprocess, sys
sys.path.insert(0, "src")
from timeline import SCENES
for name, s, e in SCENES:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{e - s:.3f}",
                    "-i", "out/video_silent.mp4", "-ss", f"{s:.3f}", "-t", f"{e - s:.3f}",
                    "-i", "out/audio/mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "animation",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    f"../deliverables/scenes/{name}.mp4"], check=True)
PY

# audio stems
for f in voiceover music sfx mix; do
  ffmpeg -loglevel error -y -i "$OUT"/audio/$f.wav -c:a flac ../deliverables/audio/$f.flac
done

# thumbnail
(cd src && python3 thumbnail.py ../../deliverables/HUMAN_MIND_EP01_thumbnail.png)
(cd src && python3 thumbnail_vertical.py ../../deliverables/HUMAN_MIND_EP01_thumbnail_9x16.png)
echo "built ../deliverables"
