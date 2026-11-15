# DIDAO HERO — main character (permanent across all seasons)

**Source of truth:** `DIDAO/ASSETS/didao_engine/characters.py` → `HERO`. Every shot, every episode imports this rig.
Do **not** redraw him from scratch. To use him in a new episode: `from didao_engine.characters import HERO`.

| Attribute | Value (locked) |
|---|---|
| Age | 15 |
| Height / build | 1.68 m, average teen build (`k = 1.0`, shoulder 0.205 m) |
| Hair | Messy black, fixed silhouette (`HAIR_HERO_OUT/IN`), colour `#0c0d12`, blue moonlight sheen |
| Face | Teen face, brown eyes `#3a2a1f`, skin `#c9a389` |
| Clothes | Dark navy sweater `#262b36` (rib hem, crew collar), dark trousers `#1b1d23`, dark sneakers `#17181c` with grey soles `#6b6e74` |
| Props | Flashlight, phone, small dark backpack (morning scenes) |
| Personality | Curious, careful, sometimes impulsive. Not a superhero — gets scared, makes mistakes. Narrates in the first person. |

Expressions available (`EXPR`): neutral, calm, smile, worried, scared, surprised, sleep, squint, confused.
Views: front, side, back, three-quarter head turn (`yaw`), close-up portrait (`draw_portrait`).

Sheets: `HERO_REFERENCE_SHEET.png` (front / side / back / full body + neutral / scared / surprised / worried),
`HERO_EXPRESSIONS.png` (all expressions + head turn).

## Supporting cast (season 1)
* **Max** — tallest (1.80 m), olive parka `#343f31`, knitted beanie, brown boots. The skeptic.
* **Lena** — 1.62 m, auburn ponytail, maroon puffer `#4b2a2d`, grey scarf. Always notices things first.
