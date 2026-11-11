#!/usr/bin/env bash
# Rebuild everything: ./build.sh  (needs node 18+, python3 with numpy/scipy/faster-whisper, ffmpeg)
set -e
cd "$(dirname "$0")"; W=work; mkdir -p $W
(cd render && npm install --silent)
for n in en ru; do ffmpeg -v error -y -i voice/voice_${n}_original.mp3 -ac 1 -ar 16000 $W/vo_$n.wav; done
cp $W/vo_en.wav $W/vo_a.wav; cp $W/vo_ru.wav $W/vo_b.wav
# timeline.json already contains phrase placement + corrected subtitles; prep.py regenerates it from whisper JSON.
for L in en ru; do
  node render/render.js $L 0 1350 $W/${L}_a.mp4 & node render/render.js $L 1350 2700 $W/${L}_b.mp4 & wait
  printf "file '%s'\nfile '%s'\n" ${L}_a.mp4 ${L}_b.mp4 > $W/list_$L.txt
  ffmpeg -v error -y -f concat -safe 0 -i $W/list_$L.txt -c copy $W/video_$L.mp4
  python3 audio.py $W $L
  ffmpeg -v error -y -i $W/video_$L.mp4 -i $W/mix_$L.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-14:TP=-1.0:LRA=11 -ar 48000 -c:a aac -b:a 192k -movflags +faststart ../output/black_death_$L.mp4
done
node render/thumb.js ../output
