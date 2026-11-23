#!/bin/bash
# Renders the preview in 4 parallel chunks, builds audio, muxes the final file.
set -e
cd "$(dirname "$0")"
OUT=${OUT:-out}; mkdir -p $OUT
N=$(node -e "console.log(require('./timeline').FRAMES)")
P=4; C=$(( (N + P - 1) / P ))
for i in $(seq 0 $((P-1))); do a=$((i*C)); b=$(( (i+1)*C < N ? (i+1)*C : N )); node render.js $a $b $OUT/part$i.mp4 & done; wait
: > $OUT/list.txt; for i in $(seq 0 $((P-1))); do echo "file 'part$i.mp4'" >> $OUT/list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i $OUT/list.txt -c copy $OUT/video.mp4
node audio.js $OUT/sfx.wav
MUSIC=${MUSIC:-music.mp3}
# Music: quiet bed (~ -28 LUFS before the final +4 dB master gain; SFX sit ~8 dB above it), extra dip at the tree reveal, fades at both ends.
ffmpeg -y -loglevel error -ss 3 -t 38 -i "$MUSIC" -i $OUT/sfx.wav -filter_complex "\
[0:a]aresample=48000,volume=-9.2dB,volume='if(between(t,11.9,13.6),0.45,1)':eval=frame,afade=t=in:d=1.2,afade=t=out:st=36.4:d=1.6[m];\
[1:a]volume=-6dB[s];[m][s]amix=inputs=2:normalize=0,volume=4dB,alimiter=limit=0.89[a]" -map "[a]" -c:a pcm_s16le $OUT/mix.wav
ffmpeg -y -loglevel error -i $OUT/video.mp4 -i $OUT/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart HUMAN_MIND_EP02_preview_9x16.mp4
node render.js --still cover HUMAN_MIND_EP02_cover_9x16.png
