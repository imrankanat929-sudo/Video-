"""Build the 60s vertical recap from trailer footage.
usage: python3 build.py ru|en
"""
import json, os, subprocess, sys

LANG = sys.argv[1]
SCR = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/user/Video-/covenant-recap"
SRC = f"{SCR}/trailer/trailer.mp4"
WORK = f"{SCR}/build_{LANG}"
os.makedirs(WORK, exist_ok=True)
FPS = 30
FG_W, FG_H, FG_Y = 1080, 960, 330

# (ru_start, ru_end, src_start, src_end, cx0, cx1)   cx = horizontal centre of the crop (0..1)
SHOTS = [
    (0.0, 1.6, 15.0, 17.4, .44, .44),   # John wounded in trench
    (1.6, 3.0, 4.30, 5.85, .5, .5),     # aerial desert
    (3.0, 4.3, 12.0, 12.85, .4, .4),    # explosion
    (4.3, 5.75, 55.1, 57.0, .42, .46),  # John bleeding, a hand reaches him
    (5.75, 7.4, 22.0, 23.5, .66, .66),  # Ahmed in helmet
    (7.4, 8.9, 67.15, 68.85, .6, .66),  # Ahmed, beanie
    (8.9, 10.5, 42.0, 43.45, .5, .5),   # humvees on the road
    (10.5, 12.3, 46.46, 47.72, .6, .6), # John in vehicle
    (12.3, 14.8, 7.21, 9.75, .3, .76),  # Ahmed -> John in one car (pan)
    (14.8, 16.4, 43.46, 44.82, .5, .5), # unit on foot, aerial
    (16.4, 17.9, 9.79, 10.95, .55, .55),# ambush explosion
    (17.9, 19.8, 57.04, 58.68, .62, .62),# Ahmed fighting
    (19.8, 21.5, 73.25, 74.48, .42, .42),# Ahmed tends wounded John
    (21.5, 23.6, 64.0, 65.45, .66, .66),# lone figure across the slope
    (23.6, 25.0, 65.6, 67.1, .6, .6), # John on the cart
    (25.0, 26.4, 74.5, 75.77, .45, .45),# Ahmed hauling the cart into the sun
    (26.4, 27.6, 75.8, 77.1, .46, .46), # cart on mountain road
    (27.6, 29.2, 26.79, 27.98, .5, .5), # American base
    (29.2, 30.8, 18.54, 20.15, .3, .3), # John at home
    (30.8, 32.4, 123.17, 124.37, .72, .72),# photo of Ahmed on phone
    (32.4, 33.6, 117.75, 118.73, .3, .3),# Taliban
    (33.6, 34.9, 106.42, 107.4, .5, .5),# armed man in car
    (34.9, 36.6, 97.79, 99.3, .35, .35),# officer (bureaucracy)
    (36.6, 38.3, 99.33, 101.35, .33, .33),# John thinking
    (38.3, 39.4, 91.46, 92.65, .5, .5), # John decides
    (39.4, 41.1, 101.38, 102.7, .26, .3),# John geared up
    (41.1, 42.9, 109.46, 111.06, .5, .5),# convoy road aerial
    (42.9, 44.1, 140.71, 141.27, .3, .3),# Ahmed's wife
    (44.1, 46.9, 132.67, 135.5, .5, .5),# running through the tunnel
    (46.9, 47.8, 111.92, 112.55, .6, .6),# Taliban pickups
    (47.8, 48.7, 141.29, 141.9, .42, .42),# gunners pickup
    (48.7, 49.5, 58.71, 59.5, .28, .28),# masked fighter
    (49.5, 50.4, 127.5, 128.22, .45, .45),# fire on the dam
    (50.4, 52.4, 85.58, 86.94, .41, .41),# fire, despair
    (52.4, 53.3, 141.92, 142.65, .5, .5),# gunship arrives
    (53.3, 53.8, 144.04, 144.6, .39, .39),# strike
    (53.8, 55.6, 105.33, 106.42, .72, .72),# John with pistol
    (55.6, 57.0, 147.6, 149.0, .52, .52),# John close-up
    (57.0, 58.3, 47.75, 49.05, .35, .35),# Ahmed close-up
    (58.3, 60.0, 149.6, 151.4, .68, .68),# silhouette at sunset
]
SC_RU = [0.0, 5.75, 14.8, 21.5, 29.2, 38.3, 46.9, 53.7, 60.0]
SC_EN = [0.0, 5.8, 15.1, 22.9, 28.6, 37.6, 47.6, 54.9, 60.0]

def to_lang(t):
    if LANG == "ru": return t
    for i in range(8):
        a, b = SC_RU[i], SC_RU[i + 1]
        if a <= t <= b + 1e-6:
            return SC_EN[i] + (t - a) * (SC_EN[i + 1] - SC_EN[i]) / (b - a)
    return t

# frame-exact slots
slots = []
for s in SHOTS:
    f0, f1 = round(to_lang(s[0]) * FPS), round(to_lang(s[1]) * FPS)
    slots.append((f0, f1) + s[2:])

GRADE = ("eq=contrast=1.12:saturation=0.86:gamma=0.97,"
         "colorbalance=rs=0.05:gs=0.02:bs=-0.07:rm=0.04:gm=0.02:bm=-0.05:rh=0.03:bh=-0.05,"
         "vignette=angle=PI/5")

def render(i, f0, f1, ss, se, cx0, cx1):
    out = f"{WORK}/c{i:02d}.mp4"
    n = f1 - f0; slot = n / FPS; avail = se - ss
    speed = min(1.0, avail / slot)
    take = slot * speed + 0.15
    zin = i % 2 == 0
    z0, z1 = (1.0, 1.07) if zin else (1.07, 1.0)
    xexpr = f"max(0,min(454,({cx0}+({cx1}-{cx0})*t/{slot})*854-200))"
    interp = f",minterpolate=fps={FPS}:mi_mode=blend" if speed < 0.85 else f",fps={FPS}"
    fc = (f"[0:v]delogo=x=26:y=80:w=52:h=28,crop=854:356:0:62,setpts=(PTS-STARTPTS)/{speed:.4f}{interp},split[a][b];"
          f"[a]scale=-2:1920,crop=1080:1920,boxblur=28:2,eq=brightness=-0.22:saturation=0.6[bg];"
          f"[b]crop=400:356:'{xexpr}':0,scale=2160:1920:flags=lanczos,"
          f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={FG_W}x{FG_H}:fps={FPS},"
          f"unsharp=5:5:0.6,{GRADE}[fg];"
          f"[bg][fg]overlay=0:{FG_Y},format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-t", f"{take:.3f}", "-i", SRC,
                    "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n), "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "16", out], check=True)
    return out

if "--ass-only" not in sys.argv:
    clips = [render(i, *s) for i, s in enumerate(slots)]
    with open(f"{WORK}/list.txt", "w") as f:
        for c in clips: f.write(f"file '{c}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{WORK}/list.txt",
                    "-c", "copy", f"{WORK}/video.mp4"], check=True)

# ---------- overlay text (ASS) ----------
def at(t):
    cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def srt_read(p):
    blocks = open(p).read().strip().split("\n\n"); out = []
    for b in blocks:
        l = b.split("\n"); a, c = l[1].split(" --> ")
        tt = lambda x: int(x[:2]) * 3600 + int(x[3:5]) * 60 + int(x[6:8]) + int(x[9:]) / 1000
        out.append((tt(a), tt(c), " ".join(l[2:])))
    return out

import re
KW = {"ru": ["вражеской", "территории.", "уничтожен,", "тяжело", "ранен.", "спасёт", "Джон", "Кинли", "Ахмедом.", "Ахмед",
             "Ахмеда", "засаду.", "единственным", "выжившим", "не", "бросает", "горы,", "базы.", "опасности.", "документы",
             "вернуться", "друга.", "эвакуации.", "окружают", "безвыходной.", "помощь.", "обещание", "спас"],
      "en": ["enemy", "lines,", "gone,", "badly", "injured.", "save", "John", "Kinley", "Ahmed,", "Ahmed", "ambushed.",
             "only", "survivors.", "refuses", "abandon", "mountains", "base.", "danger.", "documents", "decision.",
             "Afghanistan", "Ahmed's", "evacuation", "enemies", "impossible.", "help", "arrives.", "promise", "saved"]}[LANG]
TITLE = {"ru": ("ОН НЁС ЕГО", "ЧЕРЕЗ ГОРЫ"), "en": ("HE CARRIED HIM", "ACROSS MOUNTAINS")}[LANG]
TAGS = {"ru": ["ВРАЖЕСКИЙ ТЫЛ", "ПЕРЕВОДЧИК", "ЗАСАДА", "НЕ БРОСИЛ", "ВИЗЫ НЕТ", "ОН ВЕРНУЛСЯ", "ОКРУЖЕНЫ", "ДОЛГ ВОЗВРАЩЁН"],
        "en": ["BEHIND ENEMY LINES", "THE INTERPRETER", "AMBUSH", "HE WON'T LEAVE HIM", "NO VISA", "GOING BACK", "SURROUNDED", "DEBT REPAID"]}[LANG]
SC = SC_RU if LANG == "ru" else SC_EN

def hl(text):
    return " ".join("{\\c&H00D7FF&}" + w + "{\\c&HFFFFFF&}" if w in KW else w for w in text.split())

ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T1,Inter Black,{t1},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,8,0,8,40,40,70,1
Style: T2,Inter Black,{t2},&H0000D7FF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,8,0,8,40,40,180,1
Style: Sub,Inter Black,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,0,5,70,70,0,1
Style: Tag,Inter Black,50,&H00FFFFFF,&H00FFFFFF,&H002A2AE0,&H002A2AE0,0,0,0,0,100,100,1,-4,3,14,0,5,0,0,0,1
Style: Fin,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,7,0,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".format(t1=96 if LANG == "ru" else 86, t2=128 if LANG == "ru" else 100)
ev = [f"Dialogue: 5,{at(0)},{at(59.0)},T1,,0,0,0,,{TITLE[0]}",
      f"Dialogue: 5,{at(0)},{at(59.0)},T2,,0,0,0,,{TITLE[1]}"]
for i, tag in enumerate(TAGS):
    a, b = SC[i], min(SC[i + 1], 59.0)
    ev.append(f"Dialogue: 6,{at(a + 0.1)},{at(b)},Tag,,0,0,0,,{{\\pos(330,{FG_Y + FG_H - 10})"
              f"\\fscx40\\fscy40\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}}{tag}")
for a, b, t in srt_read(f"{OUT}/subtitles/covenant_{LANG}.srt"):
    if t.startswith("A PROMISE"): continue
    ev.append(f"Dialogue: 7,{at(a)},{at(b)},Sub,,0,0,0,,{{\\pos(540,1480)\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)}}{hl(t)}")
ev.append(f"Dialogue: 8,{at(59.0)},{at(60.0)},Fin,,0,0,0,,{{\\pos(540,{FG_Y + FG_H // 2})\\fad(250,0)}}A PROMISE\\N{{\\c&H00D7FF&}}IS A PROMISE.")
open(f"{WORK}/overlay.ass", "w").write(ass + "\n".join(ev) + "\n")

# ---------- music bed (placeholder: synthesized drone + hits) ----------
hits = [SC[i] for i in range(1, 8)] + [0.0]
hit_expr = "+".join(f"0.55*sin(2*PI*48*(t-{h:.2f}))*exp(-3.5*(t-{h:.2f}))*gte(t,{h:.2f})" for h in hits)
env = f"(0.55+0.45*clip((t-{SC[6]})/{SC[7]-SC[6]},0,1))*clip((59.6-t)/1.6,0,1)"
drone = ("(0.16*sin(2*PI*55*t)+0.10*sin(2*PI*82.41*t+sin(2*PI*0.13*t))+0.06*sin(2*PI*110*t)*(0.6+0.4*sin(2*PI*0.25*t))"
         "+0.05*sin(2*PI*164.8*t)*(0.5+0.5*sin(2*PI*0.17*t)))")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                f"aevalsrc='{env}*{drone}+{hit_expr}':s=44100:d=60",
                "-f", "lavfi", "-i", "anoisesrc=d=60:c=brown:a=0.08:r=44100",
                "-filter_complex", "[1]lowpass=f=500,volume=0.5[w];[0][w]amix=inputs=2:normalize=0,lowpass=f=2500,"
                "afade=t=out:st=58.5:d=1.5[a]", "-map", "[a]", "-ac", "2", f"{WORK}/bed.wav"], check=True)

vo = f"{OUT}/audio/vo_{LANG}_60s.mp3"
final = f"{OUT}/final/covenant_recap_{LANG}.mp4"
os.makedirs(f"{OUT}/final", exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{WORK}/video.mp4", "-i", vo, "-i", f"{WORK}/bed.wav",
                "-filter_complex",
                f"[0:v]ass={WORK}/overlay.ass,fade=t=in:st=0:d=0.15,format=yuv420p[v];"
                "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,loudnorm=I=-14:TP=-1.5:LRA=11,asplit[vo1][vo2];"
                "[2:a]aresample=48000,volume=0.22[m];[m][vo2]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md];"
                "[md][vo1]amix=inputs=2:normalize=0[mix0];[mix0]alimiter=limit=0.89[a]",
                "-map", "[v]", "-map", "[a]", "-t", "60", "-r", str(FPS),
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", final], check=True)
print(final)
