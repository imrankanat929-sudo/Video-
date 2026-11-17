#!/usr/bin/env bash
# Russian vertical renderer: ./render_ru.sh shots|stills|cover [ids]
cd "$(dirname "$0")"
python3 render/make_ru.py >/dev/null
PAGE=render/index_v_ru.html OUT=output_ru SIZE=1080x1920 node ../ep01/render/render.mjs "$@"
