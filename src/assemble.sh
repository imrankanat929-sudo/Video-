#!/bin/sh
# Concatenate rendered chunks and mux with the final mix.  Usage: sh assemble.sh LANG
set -e
L=$1; B=../build; O=../output
printf "file '%s'\n" chunks/${L}_0.mp4 chunks/${L}_1.mp4 chunks/${L}_2.mp4 chunks/${L}_3.mp4 > $B/concat_$L.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i $B/concat_$L.txt -i $B/mix_$L.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest \
  -metadata title="HUMAN MIND — Episode 01" $O/HUMAN_MIND_EP01_$L.mp4
