"""Write one production prompt / shot spec per clip into ../prompts/."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from script_ep01 import CLIPS

STYLE = ("Premium cinematic 2D animation, layered parallax backgrounds, deep shadows, atmospheric fog, "
         "palette: dark blue, cold grey, black, muted green; warm orange ONLY from the campfire. "
         "Vertical 9:16, 1080x1920, 30 fps. NOT anime, NOT manga, NOT a children's cartoon, no random text.")
HERO_T = ("DIDAO HERO: 15-year-old boy, messy black hair, teen face, expressive brown eyes, dark navy sweater, "
          "dark trousers, dark sneakers with grey soles, average teen build (see CONTINUITY_BIBLE/main_character_reference)")
SLENDER_T = ("THE TALL MAN: 2.95 m, extremely thin, featureless white face, black classic suit, white shirt, dark tie, "
             "abnormally long arms, pale long-fingered hands; moves slowly or not at all")

SHOTS = {
 1: ("Dusk. Crane shot starts high above the pines looking down the narrow forest path, descends to eye level as the three friends "
     "(Max left in olive parka + beanie, HERO centre, Lena right in maroon jacket) walk toward camera with backpacks. Camera keeps dollying back.",
     "Wind, leaves, soft footsteps on needles, distant owl. Sparse low piano notes over a D-minor drone.", "Title card: DIDAO / THE FOREST HAS NO EXIT / Episode 1"),
 2: ("Wide on the clearing (tent left, fire pit centre). Max hammers tent pegs, Lena walks in carrying firewood, HERO kneels and strikes a match; "
     "the fire catches and grows. Dusk shifts to night across the clip; slow push-in.", "Peg knocks, match strike, fire whoosh, crackle begins.", ""),
 3: ("A) Front of the trio sitting on logs behind the fire, warm under-light. Lena stops smiling, freezes, points off-screen; the others turn. "
     "B) Hard cut to reverse over their backs: far between the trees, deep in fog, a tall still silhouette. Slow push toward it. Face never visible.",
     "Crackle; tension riser; low hit on the cut.", "Monster: far away only, small in frame."),
 4: ("A) Over-shoulder: HERO stands and aims his flashlight; the beam reaches the figure - it glitches and vanishes; beam searches empty trees. "
     "B) Front medium of the three: Lena scared, HERO stunned then looking back, Max shrugs ('just a tree').", "Torch click, digital glitch/static, whoosh.", ""),
 5: ("Inside the tent at night. Top-down close-up of HERO asleep in his sleeping bag between the friends; moonlight and branch shadows on the fabric. "
     "His eyes snap open, dart left and right. Slow push-in to the face. Cold breath vapour.", "Wind fades to near silence, slow breathing.", ""),
 6: ("HERO half sits up inside the tent. Three slow heavy footsteps outside (1.5 s, 3.0 s, 4.5 s); his eyes jump toward each one. "
     "Tent fabric shivers in the wind; a tall thin shadow slides across the moonlit wall. Push-in on his face.", "3 heavy steps with twig snap, heartbeat, fabric flutter.", ""),
 7: ("A) POV: the tent flap is unzipped and pulled aside by HERO's hand; outside, beside the dead embers, the Tall Man stands much closer, at the treeline. "
     "Slow push; at 4 s its head tilts unnaturally. B) Close-up of HERO's face in the narrow gap of the fabric, frozen with fear.", "Zipper, low hit, heartbeat.", ""),
 8: ("A) Quick close-ups: HERO whispering urgently; Lena's eyes snap open; Max wakes, confused. "
     "B) Over their backs as they step out of the tent with flashlights - the figure is there, beams swing to it, it glitches and is gone. Beams search the dark.",
     "Whispers, sleeping-bag rustle, zipper, steps, clicks, glitch.", ""),
 9: ("Morning: cold grey fog, muted green. A) The trio with backpacks at the clearing edge - where the path was there are only trees. Camera rises slightly. "
     "B) Reverse: their confused faces looking around, Max scratching his head.", "Thin bird calls, cold wind, steps.", "No monster."),
 10: ("A) HERO walks to an old pine at the clearing edge and stops. B) Extreme close-up of bark: carved letters 'DO NOT LOOK BACK' (exact spelling), "
      "raw pale wood in dark bark, slow push + slight tilt, fog drifting.", "Steps, low sting on the close-up.", "On-screen text must be spelled exactly: DO NOT LOOK BACK"),
 11: ("Close-up of HERO's phone in his hands (no-signal icon). It vibrates twice, the screen wakes and a notification slides in from UNKNOWN: "
      "'I CAN SEE YOU ALL.' Slow push into the message.", "Two vibrations, soft notification ping.", "On-screen text must be spelled exactly: I CAN SEE YOU ALL."),
 12: ("A) Close-up: HERO looking down at the phone slowly raises his head; eyes widen. B) Over his shoulder: between the trees beyond the empty clearing stand "
      "THREE identical Tall Men. Slow push-in; at 8 s all three tilt their heads at once; sharp musical hit + fast push, then a short silence, "
      "hard cut to black. C) 'TO BE CONTINUED…' fades in.", "Riser -> sharp hit -> 0.6 s silence -> low tail.", "Three figures share one identical design."),
}

out = os.path.join(HERE, '..', 'prompts')
os.makedirs(out, exist_ok=True)
for c in CLIPS:
    action, sound, note = SHOTS[c['id']]
    vo_ru = '\n'.join(f"- {v[0]:.1f}s: {v[1]}" for v in c['vo'])
    vo_en = '\n'.join(f"- {v[0]:.1f}s: {v[2]}" for v in c['vo'])
    chars = HERO_T + (('; ' + SLENDER_T) if c['id'] in (3, 4, 6, 7, 8, 12) else '')
    txt = f"""# {c['name']}  ({c['dur']:.1f} s)

## Shot / action
{action}

## Generation prompt (for any image/video model)
{STYLE} Location: the single Blackpine Hollow forest (tall old pines, dense fog, moonlight from upper-left/north-west,
narrow path, small clearing with tent and stone fire ring - see environment_references/). Characters: {chars}.
Action: {action}
Keep character faces, hair, clothes and proportions identical to the reference sheets. No captions or random letters in frame.

## Sound
{sound}

## Narration
RU:
{vo_ru}

EN:
{vo_en}

## Notes
{note or '-'}

## Implementation
Rendered by `project_files/scenes_ep01.py :: render_{c['id']:02d}` with the shared DIDAO engine (`DIDAO/ASSETS/didao_engine`).
"""
    open(os.path.join(out, f"{c['name']}.md"), 'w', encoding='utf-8').write(txt)
print('prompts written')
