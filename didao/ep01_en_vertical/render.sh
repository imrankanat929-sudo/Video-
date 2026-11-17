#!/usr/bin/env bash
# vertical renderer wrapper: ./render.sh shots|stills|cover [ids]
cd "$(dirname "$0")"
PAGE=render/index_v.html OUT=output SIZE=1080x1920 node ../ep01/render/render.mjs "$@"
