#!/usr/bin/env bash
# Episode 2 — vertical 9:16, both languages.   ./build.sh ru|en   (SKIP_RENDER=1 to reuse rendered shots)
# 1) tighten VO pauses -> 2) shot timing -> 3) shots (each its own clip) -> 4) score/SFX -> 5) subtitles -> 6) assemble
set -euo pipefail
cd "$(dirname "$0")"; lang=$1
NAME=$([[ $lang == ru ]] && echo GTA6_VYSHLA_RU || echo GTA6_IS_HERE_EN)
python3 audio/make_vo.py $lang && python3 audio/timing.py
[[ "${SKIP_RENDER:-0}" == 1 ]] || ./render.sh $lang shots
python3 audio/music.py $lang && python3 audio/make_subs.py $lang
./render.sh $lang cover && ffmpeg -loglevel error -y -i output_$lang/cover.png -q:v 2 output_$lang/${NAME}_preview_1080x1920.jpg
TOTAL=$(python3 -c "import json;print(json.load(open('audio/timing.json'))['$lang']['total'])")
mapfile -t IDS < <(grep -oE "^  \{ id: '[a-z0-9_]+'" render/shots.js | sed -E "s/.*'(.*)'/\1/")
TYPES=(slideleft fade wipeup fadewhite slideup circleopen smoothleft fade slidedown wipeleft)
XF=0.25; inputs=(); filt=""; prev="[0:v]"
for id in "${IDS[@]}"; do inputs+=(-i "output_$lang/shots/$id.mp4"); done
for ((i=1; i<${#IDS[@]}; i++)); do
  st=$(python3 -c "import json;print(json.load(open('audio/timing.json'))['$lang']['starts']['${IDS[$i]}'])")
  filt+="${prev}[$i:v]xfade=transition=${TYPES[$((i % ${#TYPES[@]}))]}:duration=$XF:offset=$st[x$i];"; prev="[x$i]"
done
GRADE="eq=contrast=1.07:saturation=1.15:gamma=0.98,colorbalance=rs=0.03:bs=0.04:rh=0.03:bh=-0.02,noise=alls=3:allf=t,vignette=angle=PI/6"
SUB="subtitles=output_$lang/${NAME}_subtitles.srt:force_style='FontName=Rubik,Bold=1,FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.5,Shadow=0.7,MarginV=52,MarginL=10,MarginR=10'"
filt+="${prev}${GRADE},${SUB},format=yuv420p[v];"
n=${#IDS[@]}; LEADMS=250
filt+="[$n:a]aformat=channel_layouts=stereo,adelay=$LEADMS|$LEADMS,apad=whole_dur=$TOTAL,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[vo][vosc];"
filt+="[$((n+1)):a]volume=0.45[mu];[mu][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mud];"
filt+="[$((n+2)):a]volume=0.6[fx];[vo][mud][fx]amix=inputs=3:normalize=0:duration=longest,atrim=0:$TOTAL,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.75:level=false[a]"
ffmpeg -loglevel error -y "${inputs[@]}" -i audio/vo_${lang}_tight.wav -i audio/music_$lang.wav -i audio/sfx_$lang.wav \
  -filter_complex "$filt" -map "[v]" -map "[a]" -t $TOTAL -r 30 -c:v libx264 -preset slow -crf 19 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k output_$lang/${NAME}_9x16.mp4
ffprobe -v error -show_entries format=duration:stream=width,height -of compact output_$lang/${NAME}_9x16.mp4
