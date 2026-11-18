#!/usr/bin/env bash
# ./render.sh ru|en shots|stills|cover [ids]
cd "$(dirname "$0")"; lang=$1; shift
PAGE="render/index.html?lang=$lang" OUT="output_$lang" SIZE=1080x1920 node ../ep01/render/render.mjs "$@"
