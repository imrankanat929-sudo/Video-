#!/usr/bin/env bash
# DIDAO Ep.1 — full pipeline:
#   1) render each shot as its own clip     (render/render.mjs shots)
#   2) score + sfx                          (audio/music.py)
#   3) subtitles from VO word timings       (audio/make_subs.py)
#   4) assemble: cross-fades, colour grade, subtitles, mix -> output/DIDAO_E01_ONE_DAY_BEFORE_GTA6.mp4
set -euo pipefail
cd "$(dirname "$0")"
[[ "${SKIP_RENDER:-0}" == 1 ]] || (cd render && node render.mjs shots)
python3 audio/music.py
python3 audio/make_subs.py
(cd render && node render.mjs cover)
ffmpeg -loglevel error -y -i output/cover.png -vf scale=1280:720 -q:v 2 output/DIDAO_E01_cover_1280x720.jpg

# shot list + transition per cut (from shots.js)
mapfile -t SHOTS < <(grep -oE "id: 's[0-9]+_[a-z0-9]+', start: [0-9.]+" render/shots.js | sed -E "s/id: '([^']+)', start: ([0-9.]+)/\1 \2/")
TRANS=(fade fadeblack fade fadeblack   fade fade fade circleopen   fade smoothleft fadewhite fade fade smoothleft   fade smoothup fade   fadewhite fade fade fade fade fadeblack fadeblack)
XF=0.4
inputs=(); filt=""; prev="[0:v]"
for i in "${!SHOTS[@]}"; do read -r id st <<<"${SHOTS[$i]}"; inputs+=(-i "output/shots/$id.mp4"); done
for ((i=1; i<${#SHOTS[@]}; i++)); do
  read -r id st <<<"${SHOTS[$i]}"
  out="[x$i]"; filt+="${prev}[$i:v]xfade=transition=${TRANS[$((i-1))]}:duration=$XF:offset=$st${out};"; prev=$out
done
GRADE="eq=contrast=1.06:saturation=1.12:gamma=0.98,colorbalance=rs=0.03:bs=0.04:rh=0.03:bh=-0.02,noise=alls=3:allf=t,vignette=angle=PI/6"
SUB="subtitles=output/DIDAO_E01_subtitles_ru.srt:force_style='FontName=Rubik,Bold=1,FontSize=17,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1.6,Shadow=0.8,MarginV=26'"
filt+="${prev}${GRADE},${SUB},format=yuv420p[v];"
n=${#SHOTS[@]}
filt+="[$n:a]adelay=2000|2000,apad=whole_dur=120,aformat=channel_layouts=stereo,volume=1.0,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,asplit=2[vo][vosc];"
filt+="[$((n+1)):a]volume=0.42[mu];[mu][vosc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mud];"
filt+="[$((n+2)):a]volume=0.55[fx];[vo][mud][fx]amix=inputs=3:normalize=0:duration=longest,atrim=0:120,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
ffmpeg -loglevel error -stats -y "${inputs[@]}" -i assets/voiceover.mp3 -i audio/music.wav -i audio/sfx.wav \
  -filter_complex "$filt" -map "[v]" -map "[a]" -t 120 -r 30 -c:v libx264 -preset slow -crf 19 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k output/DIDAO_E01_ONE_DAY_BEFORE_GTA6.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,codec_name -of compact output/DIDAO_E01_ONE_DAY_BEFORE_GTA6.mp4
