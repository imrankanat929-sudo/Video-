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
 1: ("Dusk. Crane shot starts high above the pines looking down the narrow forest path and descends (first half of one continuous move).",
     "Wind, leaves, distant owl, soft footsteps. Sparse low piano over a D-minor drone.", "Title card: DIDAO / THE FOREST HAS NO EXIT / Episode 1"),
 2: ("Continuation of the crane: eye level, the three friends (Max in olive parka + beanie, HERO, Lena in maroon jacket) walk toward camera with backpacks.",
     "Footsteps on needles, wind.", ""),
 3: ("Wide on the clearing (tent left, fire pit centre). Max hammers tent pegs, Lena brings firewood, HERO strikes a match; the fire catches. Dusk turns to night.",
     "Peg knocks, match strike, fire whoosh, crackle.", ""),
 4: ("Front of the trio sitting on logs behind the fire, warm under-light, laughing and talking. Lena suddenly freezes, stares past camera and points; the others turn.",
     "Crackle, laughter (implied), rising tension.", ""),
 5: ("Reverse over the trio's backs: far between the pines, deep in fog, an impossibly tall still silhouette. Slow push toward it. Face never visible.",
     "Low hit on the cut, wind.", "Monster far away only."),
 6: ("A) Over-shoulder: HERO stands and aims his flashlight; the beam reaches the figure - it glitches and vanishes; the beam searches empty trees. "
     "B) Front medium of the three: Lena scared, HERO stunned, Max shrugs it off ('a trick of the shadows').", "Torch click, glitch/static, whoosh.", ""),
 7: ("Inside the tent at midnight, top-down close-up of HERO asleep between his friends; moonlight and branch shadows on the fabric. "
     "His eyes snap open and dart around; a faint sound outside.", "Wind drops to near silence; breathing; one distant step.", ""),
 8: ("HERO half sits up in the tent. Three slow heavy footsteps outside, silence, then three more; his eyes jump toward each step. "
     "The fabric shivers; a tall thin shadow slides across the moonlit wall.", "6 heavy steps (3 + 3) with twig snaps, heartbeat.", ""),
 9: ("POV: the tent flap is unzipped and pulled aside by HERO's hand. Outside, near the dead embers, the Tall Man stands in the clearing much closer. "
     "Slow push; its head tilts unnaturally.", "Zipper, low hit, heartbeat.", ""),
 10: ("Slow tilt up the Tall Man from his black suit and tie to the smooth, completely featureless white head. Fog drifts in front.",
      "Riser into a deep sting on 'it has no face'.", "No eyes, no mouth - ever."),
 11: ("A) Quick close-ups: HERO whispering urgently; Lena's eyes snap open; Max wakes, confused. "
      "B) Over their backs as they rush out of the tent with flashlights - beams swing to the figure, it glitches and is gone.",
      "Whispers, rustle, zipper, steps, clicks, glitch.", ""),
 12: ("Morning: cold grey fog, muted green. A) The trio with backpacks at the clearing edge - where the path was there are only trees. "
      "B) Reverse: their confused faces among identical trees, tent behind them.", "Thin bird calls, cold wind, steps.", ""),
 13: ("A) HERO walks to an old pine at the clearing edge and stops. B) Extreme close-up: carved letters 'DO NOT LOOK BACK' (exact spelling) in dark bark.",
      "Steps, sting on the close-up.", "On-screen text must be spelled exactly: DO NOT LOOK BACK"),
 14: ("Close-up of HERO's phone (no signal). It vibrates twice, wakes, and a notification from UNKNOWN slides in: 'I CAN SEE YOU ALL.' Slow push into the message.",
      "Two vibrations, notification ping.", "On-screen text must be spelled exactly: I CAN SEE YOU ALL."),
 15: ("A) HERO looking down at the phone slowly raises his head; eyes widen. B) Over the shoulders of HERO and Lena (Max is no longer with them): "
      "between the pines stand THREE identical Tall Men - the middle one much closer. Slow push toward it; all three tilt their heads at once.",
      "Low hit, heartbeat.", "Three figures share one identical design."),
 16: ("Close-up of Lena, morning fog, terrified; she glances behind, then whispers 'Wait... where is the fourth one?'", "Breathy whisper bed, silence.", ""),
 17: ("Whip-turn of HERO, then the tent in the empty clearing: door open, dark and empty inside, Max's beanie on the ground. Slow push; "
      "sharp hit + rush into the dark doorway; 0.6 s of silence; black; 'TO BE CONTINUED…'.", "Whoosh, riser, sharp hit, silence, low tail.",
      "The question to the viewer is the episode's call to action."),
}

out = os.path.join(HERE, '..', 'prompts')
os.makedirs(out, exist_ok=True)
for c in CLIPS:
    action, sound, note = SHOTS[c['id']]
    fmt = lambda v: f"- {v[0]:.1f}s: {v[2]}" if v[0] is not None else f"- (follows): {v[2]}"
    vo_ru = '\n'.join(fmt(v) for v in c['vo']['ru']) or '- (no narration)'
    vo_en = '\n'.join(fmt(v) for v in c['vo']['en']) or '- (no narration)'
    chars = HERO_T + (('; ' + SLENDER_T) if c['id'] in (5, 6, 8, 9, 10, 11, 15) else '')
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

## Narration (client recording, cut per line)
RU:
{vo_ru}

EN:
{vo_en}

## Notes
{note or '-'}

## Implementation
Rendered by `project_files/scenes_ep01.py` (renderer {c['scene'][0]}, offset {c['scene'][1]:.1f}s) with the shared DIDAO engine (`DIDAO/ASSETS/didao_engine`).
"""
    open(os.path.join(out, f"{c['name']}.md"), 'w', encoding='utf-8').write(txt)
print('prompts written')
