#!/usr/bin/env bash
# "ONE DAY BEFORE GTA 6" — vertical 9:16 English cut.
#   1) English VO (Kokoro TTS, local):  KOKORO_MODEL=/path/kokoro-v1.0.onnx python3 audio/make_vo.py "$KOKORO_MODEL"
#   2) shots, each its own clip:       ./render.sh shots
#   3) subtitles + cover + assembly:   this script (SKIP_RENDER=1 to skip step 2)
# Score and SFX are shared with the 16:9 cut (../ep01/audio), same timeline.
set -euo pipefail
cd "$(dirname "$0")"
[[ "${SKIP_RENDER:-0}" == 1 ]] || ./render.sh shots
python3 audio/make_subs.py
./render.sh cover && ffmpeg -loglevel error -y -i output/cover.png -q:v 2 output/ONE_DAY_BEFORE_GTA6_EN_preview_1080x1920.jpg
mapfile -t SHOTS < <(grep -oE "id: 's[0-9]+_[a-z0-9]+', start: [0-9.]+" render/shots_v.js | sed -E "s/id: '([^']+)', start: ([0-9.]+)/\1 \2/")
TRANS=(fade fadeblack fade fadeblack   fade fade fade circleopen   fade smoothleft fadewhite fade fade smoothleft   fade smoothup fade   fadewhite fade fade fade fade fadeblack fadeblack)
XF=0.4; inputs=(); filt=""; prev="[0:v]"
for i in "${!SHOTS[@]}"; do read -r id st <<<"${SHOTS[$i]}"; inputs+=(-i "output/shots/$id.mp4"); done
for ((i=1; i<${#SHOTS[@]}; i++)); do read -r id st <<<"${SHOTS[$i]}"; filt+="${prev}[$i:v]xfade=transition=${TRANS[$((i-1))]}:duration=$XF:offset=$st[x$i];"; prev="[x$i]"; done
GRADE="eq=contrast=1.06:saturation=1.12:gamma=0.98,colorbalance=rs=0.03:bs=0.04:rh=0.03:bh=-0.02,noise=alls=3:allf=t,vignette=angle=PI/6"
SUB="subtitles=output/ONE_DAY_BEFORE_GTA6_EN_subtitles.srt:force_style='FontName=Rubik,Bold=1,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H64000000,BorderStyle=1,Outline=1.3,Shadow=0.6,MarginV=52,MarginL=10,MarginR=10'"
filt+="${prev}${GRADE},${SUB},format=yuv420p[v];"
n=${#SHOTS[@]}
filt+="[$n:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur=120,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[vo][vosc];"
filt+="[$((n+1)):a]volume=0.42[mu];[mu][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mud];"
filt+="[$((n+2)):a]volume=0.55[fx];[vo][mud][fx]amix=inputs=3:normalize=0:duration=longest,atrim=0:120,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.75:level=false[a]"
ffmpeg -loglevel error -y "${inputs[@]}" -i audio/vo_en.wav -i ../ep01/audio/music.wav -i ../ep01/audio/sfx.wav \
  -filter_complex "$filt" -map "[v]" -map "[a]" -t 120 -r 30 -c:v libx264 -preset slow -crf 19 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k output/ONE_DAY_BEFORE_GTA6_EN_9x16.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,codec_name -of compact output/ONE_DAY_BEFORE_GTA6_EN_9x16.mp4
