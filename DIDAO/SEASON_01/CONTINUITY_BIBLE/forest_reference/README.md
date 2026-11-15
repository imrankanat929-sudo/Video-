# BLACKPINE HOLLOW — the one forest of Season 1

**Source of truth:** `didao_engine/forest.py`. All tree positions come from a fixed seed (2024), so every camera angle
sees the same forest. See `LAYOUT_MAP_TOPDOWN.png`.

| Element | World position (m) |
|---|---|
| Clearing | centre (0, 20), radius 6.5 |
| Tent (door faces south / the fire) | (-2.3, 22.2) |
| Campfire (stone ring) | (0.9, 19.2) |
| Old carved pine "DO NOT LOOK BACK" | (2.3, 13.2) |
| Path | enters the clearing from the south (z < 13.5), winding; **overgrown by trees from the morning of day 2** |
| Moon | north-west → upper-left of frame when looking north; rim light always from the moon side |

Palettes (`PALETTES`): `dusk`, `night`, `morning`. Dark blue / cold grey / black / muted green.
Warm orange appears **only** from the campfire. Fog density per palette (`fog_dist`).
