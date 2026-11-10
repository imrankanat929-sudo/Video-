#!/usr/bin/env bash
# Full build: render frames -> soundtrack -> VHS grade -> final MP4.
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
python3 audio.py "$VOICE" "$WORK/mix.wav"

printf "file '%s'\n" "$WORK/seg0.mp4" "$WORK/seg1.mp4" "$WORK/seg2.mp4" > "$WORK/list.txt"
VHS="scale=1280:1080:flags=bilinear,scale=1920:1080:flags=bicubic,\
rgbashift=rh=-4:bh=4:gv=1,\
eq=saturation=0.8:contrast=0.94:brightness=0.015:gamma=1.04,\
colorbalance=rs=0.05:gs=0.01:bs=-0.05:rm=0.03:bm=-0.03,\
noise=alls=9:allf=t+u,\
unsharp=5:5:0.5,\
vignette=angle=PI/5,format=yuv420p"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$WORK/list.txt" -i "$WORK/mix.wav" \
  -vf "$VHS" -r 30 -c:v libx264 -preset slow -crf 20 -profile:v high \
  -c:a aac -b:a 192k -t 90 -movflags +faststart "$OUT"
echo "done: $OUT"
