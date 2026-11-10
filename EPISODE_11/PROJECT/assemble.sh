#!/bin/bash
# usage: assemble.sh ru|en <chunk_dir>
set -e
L=$1; D=$2; U=$(echo $L | tr a-z A-Z)
rm -f $D/list_$L.txt; for k in 0 1 2 3; do echo "file '$D/${L}_$k.mp4'" >> $D/list_$L.txt; done
ffmpeg -v error -y -f concat -safe 0 -i $D/list_$L.txt -i mix_$L.wav \
  -vf "ass=subtitles_$L.ass" -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -shortest -movflags +faststart \
  ../${U}_VERSION/final_video_$L.mp4
