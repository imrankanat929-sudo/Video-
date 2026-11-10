#!/usr/bin/env bash
# Episode 2 build: frames -> soundtrack -> light grade -> MP4 (1920x1080, 30 fps, 1:30).
# Usage: ./build.sh <voice.mp3> <work_dir> <out.mp4>
set -euo pipefail
cd "$(dirname "$0")"
VOICE=$1; WORK=$2; OUT=$3
mkdir -p "$WORK"
export PLAYWRIGHT_PATH=${PLAYWRIGHT_PATH:-playwright}
if [ "${SKIP_RENDER:-0}" != 1 ]; then
  node render.mjs frames "$WORK/seg0.mp4" 0 900 &
  node render.mjs frames "$WORK/seg1.mp4" 900 1800 &
  node render.mjs frames "$WORK/seg2.mp4" 1800 2700 &
  wait
fi
python3 audio2005.py "$VOICE" "$WORK"
printf "file '%s'\n" "$WORK/seg0.mp4" "$WORK/seg1.mp4" "$WORK/seg2.mp4" > "$WORK/list.txt"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$WORK/list.txt" -i "$WORK/mix.wav" \
  -vf "noise=alls=4:allf=t+u,vignette=angle=PI/6,format=yuv420p" -r 30 -c:v libx264 -preset slow -crf 20 -profile:v high \
  -c:a aac -b:a 192k -t 90 -movflags +faststart "$OUT"
echo "done: $OUT"
