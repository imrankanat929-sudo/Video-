#!/bin/bash
# Generates the Russian voiceover with Piper TTS and places each line at its timestamp.
# Needs: piper (pip install piper-tts) and the voice model ru_RU-ruslan-medium.onnx
#   PIPER=/path/to/piper MODEL=/path/to/ru_RU-ruslan-medium.onnx ./build_voice.sh
set -e
cd "$(dirname "$0")"
PIPER=${PIPER:-piper}; MODEL=${MODEL:-ru_RU-ruslan-medium.onnx}
TMP=$(mktemp -d); inputs=(); filt=""; i=0; prev_end=0
while IFS='|' read -r t txt; do
  [ -z "$t" ] && continue
  echo "$txt" | "$PIPER" -m "$MODEL" --length_scale 1.08 --sentence_silence 0.25 -f $TMP/$i.wav 2>/dev/null
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $TMP/$i.wav)
  awk -v t=$t -v p=$prev_end -v x="$txt" 'BEGIN{ if (t < p) printf "WARNING: line overlaps previous (%.2f < %.2f): %s\n", t, p, x }'
  prev_end=$(awk -v t=$t -v d=$d 'BEGIN{print t+d}')
  inputs+=(-i $TMP/$i.wav)
  ms=$(awk -v t=$t 'BEGIN{printf "%d", t*1000}')
  filt+="[$i:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay=${ms}|${ms}[v$i];"
  i=$((i+1))
done < script_ru.txt
mix=""; for j in $(seq 0 $((i-1))); do mix+="[v$j]"; done
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "${filt}${mix}amix=inputs=$i:normalize=0,apad=whole_dur=95,atrim=0:95,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-2:LRA=7[out]" -map "[out]" -c:a pcm_s16le ru_voiceover.wav
rm -rf $TMP
echo "ru_voiceover.wav written ($i lines)"
