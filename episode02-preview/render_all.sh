#!/bin/bash
# Renders the preview in 4 parallel chunks, builds audio, muxes the final file.
set -e
cd "$(dirname "$0")"
OUT=${OUT:-out}; mkdir -p $OUT
N=$(node -e "console.log(require('./timeline').FRAMES)")
P=4; C=$(( (N + P - 1) / P ))
if [ -z "$SKIP_VIDEO" ]; then
for i in $(seq 0 $((P-1))); do a=$((i*C)); b=$(( (i+1)*C < N ? (i+1)*C : N )); node render.js $a $b $OUT/part$i.mp4 & done; wait
: > $OUT/list.txt; for i in $(seq 0 $((P-1))); do echo "file 'part$i.mp4'" >> $OUT/list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i $OUT/list.txt -c copy $OUT/video.mp4
fi
node audio.js $OUT/sfx.wav
MUSIC=${MUSIC:-music_lovibe.mp3}
MUSIC_GAIN=${MUSIC_GAIN:--14dB}   # LoVibe is loud (-9 LUFS); Gravity Eleven (-19 LUFS) uses -4dB
NAME=${NAME:-HUMAN_MIND_EP02_9x16.mp4}
# Music: full track from 0 s, clearly audible bed (~ -20 LUFS in the final mix), SFX on top.
# Short dip at the tree reveal, fade-out at the end.
D=$(node -e "console.log(require('./timeline').DURATION)")
ffmpeg -y -loglevel error -t $D -i "$MUSIC" -i $OUT/sfx.wav -filter_complex "\
[0:a]aresample=48000,volume=$MUSIC_GAIN,volume='if(between(t,11.9,12.6),0.5,1)':eval=frame,afade=t=in:d=0.3,afade=t=out:st=$(echo "$D-3" | bc):d=3[m];\
[1:a]volume=-5dB[s];[m][s]amix=inputs=2:normalize=0,volume=2dB,alimiter=limit=0.89[a]" -map "[a]" -c:a pcm_s16le $OUT/mix.wav
ffmpeg -y -loglevel error -i $OUT/video.mp4 -i $OUT/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart $NAME
node render.js --still cover HUMAN_MIND_EP02_cover_9x16.png
