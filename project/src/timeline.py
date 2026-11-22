"""Single source of truth for timing.

Every visual beat and every music/SFX hit is derived from the voiceover word
timestamps below (seconds inside voiceover_ru.mp3).  The voiceover is placed at
VO_OFFSET in the final video, so V(x) converts a voiceover time to video time.
"""

FPS = 30
W, H = 1920, 1080
VO_OFFSET = 1.0          # voiceover starts 1 s in: hook impact happens first
DURATION = 102.0         # ~1:42 total


def V(t):
    return t + VO_OFFSET


# --- key word times (voiceover clock) -------------------------------------
W_ = {
    # hook
    "pochemu": 0.00, "my": 0.40, "tak": 0.72, "silno": 0.88, "hotim": 1.22,
    "vsem": 1.82, "nravitsya": 2.32, "podumay": 3.70,
    # judgment
    "ty_mozhesh": 5.30, "mnenie": 6.64, "okruzh": 8.42, "inache": 9.74,
    "otkazatsya": 11.32, "idei": 12.26, "chtoby": 13.56, "stranno": 14.60,
    "smeeshsya": 16.66, "shutkoy": 17.74, "kotoraya": 18.48, "ne_ponr": 19.48,
    "pochemu2": 21.04,
    # society
    "delo": 22.40, "chastyu": 25.28, "obshestva": 25.90,
    "istorii": 28.18, "lyudi": 28.68, "zaviseli": 29.38, "drugih": 30.20,
    "podderzhka": 31.22, "bezopasnosti": 34.04,
    "poetomu": 35.46, "odobrenie": 37.02, "bolshoe": 39.56,
    # brain
    "kogda": 41.38, "prinimayut": 41.96, "uverennee": 43.92,
    "otvergayut": 46.22, "kritikuyut": 47.22, "trevogu": 49.24,
    "somnevatsya": 50.96,
    # trap
    "i_postepenno": 52.74, "lovushka": 54.72,
    "odezhdu": 57.14, "slova": 58.06, "interesy": 58.90, "povedenie": 60.14,
    "ne_potomu": 61.20, "a_potomu": 63.62, "odobryat": 65.90,
    # realization
    "vot_chto_vazhno": 67.32, "nevozmozhno": 69.14, "absolyutno": 70.24,
    "vsem2": 70.92, "u_kazhdogo": 72.26, "vzglyady": 73.68, "vkusy": 74.66,
    "ozhidaniya": 75.38, "i_inogda": 76.70, "zabyvaem": 79.70,
    "deystvitelno": 80.94, "nravitsya2": 81.60, "samim": 82.56,
    # outro
    "a_teper": 83.64, "skolko_raz": 85.06, "radi": 86.98, "chuzhoe": 88.46,
    "odobrenie_end": 89.36, "vo_end": 90.10,
}
T = {k: V(v) for k, v in W_.items()}

# --- scene boundaries (video clock) ---------------------------------------
HOOK_IMPACT = 0.35
FINAL_TEXT = 92.0
LOGO = 96.6
SCENES = [
    # name,            start,               end
    ("01_hook",        0.0,                 T["ty_mozhesh"]),
    ("02_judgment",    T["ty_mozhesh"],     T["pochemu2"]),
    ("03_why",         T["pochemu2"],       T["delo"]),
    ("04_society",     T["delo"],           T["kogda"]),
    ("05_brain",       T["kogda"],          T["i_postepenno"]),
    ("06_trap",        T["i_postepenno"],   T["vot_chto_vazhno"]),
    ("07_realization", T["vot_chto_vazhno"], T["a_teper"]),
    ("08_final",       T["a_teper"],        DURATION),
]

# --- sound design cue sheet (video clock) ---------------------------------
# kind: boom | click | whoosh | tick | riser(end time) | swell(end) | ding
SFX = [
    ("boom", HOOK_IMPACT, 1.0),
    ("whoosh", T["pochemu"] - 0.05, 0.5),
    # hook symbols pop
    ("click", T["vsem"], 0.6), ("click", T["vsem"] + 0.18, 0.5),
    ("click", T["nravitsya"], 0.7), ("click", T["nravitsya"] + 0.2, 0.5),
    ("click", T["nravitsya"] + 0.4, 0.5),
    ("whoosh", T["podumay"] - 0.1, 0.45),
    # judgment
    ("whoosh", T["ty_mozhesh"] - 0.25, 0.7),
    ("click", T["mnenie"], 0.6),
    ("click", T["okruzh"], 0.5), ("click", T["okruzh"] + 0.15, 0.5),
    ("click", T["okruzh"] + 0.3, 0.5),
    ("ding", T["inache"], 0.4),
    ("click", T["idei"], 0.8),
    ("whoosh", T["chtoby"], 0.35),
    ("boom", T["stranno"], 0.35),
    ("click", T["smeeshsya"], 0.5), ("click", T["shutkoy"], 0.5),
    ("click", T["shutkoy"] + 0.2, 0.5), ("click", T["kotoraya"], 0.4),
    ("riser", T["pochemu2"] - 1.6, 1.6),
    ("boom", T["pochemu2"], 1.2),
    # society
    ("whoosh", T["delo"] - 0.2, 0.6),
    ("click", T["chastyu"], 0.5), ("click", T["obshestva"], 0.6),
    ("whoosh", T["istorii"] - 0.4, 0.6),
    ("boom", T["bezopasnosti"], 0.45),
    ("whoosh", T["poetomu"] - 0.2, 0.6),
    ("click", T["odobrenie"], 0.5), ("click", T["odobrenie"] + 0.5, 0.5),
    ("click", T["odobrenie"] + 1.0, 0.5),
    ("ding", T["bolshoe"], 0.5),
    # brain
    ("whoosh", T["kogda"] - 0.25, 0.7),
    ("ding", T["prinimayut"], 0.5),
    ("click", T["uverennee"], 0.5),
    ("boom", T["otvergayut"], 0.4),
    ("click", T["kritikuyut"], 0.6),
    ("click", T["trevogu"], 0.5), ("click", T["somnevatsya"], 0.5),
    ("riser", T["i_postepenno"] - 1.0, 1.0),
    # trap
    ("tick", T["i_postepenno"] + 0.0, 0.5),
    ("boom", T["lovushka"], 1.1),
    ("whoosh", T["odezhdu"] - 0.1, 0.5), ("whoosh", T["slova"] - 0.1, 0.5),
    ("whoosh", T["interesy"] - 0.1, 0.5), ("whoosh", T["povedenie"] - 0.1, 0.5),
    ("click", T["a_potomu"], 0.5), ("click", T["a_potomu"] + 0.3, 0.5),
    ("click", T["a_potomu"] + 0.6, 0.5), ("click", T["a_potomu"] + 0.9, 0.5),
    ("riser", T["vot_chto_vazhno"] - 2.0, 2.0),
    # realization
    ("boom", T["vot_chto_vazhno"], 0.9),
    ("whoosh", T["nevozmozhno"] - 0.1, 0.5),
    ("click", T["vzglyady"], 0.5), ("click", T["vkusy"], 0.5),
    ("click", T["ozhidaniya"], 0.5),
    ("whoosh", T["zabyvaem"], 0.4),
    ("swell", T["deystvitelno"] - 0.3, 1.8),
    ("ding", T["samim"], 0.6),
    # outro
    ("whoosh", T["a_teper"] - 0.2, 0.5),
    ("riser", FINAL_TEXT - 1.5, 1.5),
    ("boom", FINAL_TEXT, 1.1),
    ("whoosh", LOGO - 0.2, 0.5),
    ("ding", LOGO + 0.1, 0.7),
]
