"""English voice-over (Kokoro TTS, local). Each line is synthesised separately and placed at the
same timeline position as in the Russian cut, so picture sync is preserved. Output: vo_en.wav (120 s)."""
import sys, os, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
here = os.path.dirname(os.path.abspath(__file__)); MODEL = sys.argv[1]
VOICE = os.environ.get('VOICE', 'am_puck')
# (start_s, end_limit_s, text)
LINES = [
 (2.0, 5.3, "There's only one day left until GTA 6."),
 (5.4, 9.9, "Almost ten years of waiting... and finally, the moment is here."),
 (10.05, 11.8, "The whole world is going crazy."),
 (11.9, 17.1, "People are buying new PCs, consoles, monitors. Game stores are packed."),
 (17.2, 22.0, "The internet is nothing but GTA 6. Everyone is getting ready to play."),
 (22.1, 23.6, "But there's one problem."),
 (23.7, 28.6, "I don't have a powerful PC. I don't have the game. And I don't have the money."),
 (28.7, 35.5, "I look at the screen and realize: tomorrow the whole world will be playing GTA 6... and I'll be left out."),
 (35.7, 37.7, "But suddenly... I get an idea."),
 (37.8, 42.4, "If I can't play GTA 6... why not make money from it?"),
 (42.9, 48.8, "I open an AI video app and start making my own videos in the style of GTA 6."),
 (49.1, 53.0, "Video one: a walk through the huge city of Vice City."),
 (53.3, 56.4, "Video two: a crazy ride in a sports car."),
 (56.6, 62.4, "Video three: what would happen if I ended up inside GTA 6?"),
 (62.9, 66.8, "I edit the clips, add music, and upload them to my channel."),
 (67.3, 72.4, "At first, almost nobody watches. But a few hours later... something incredible happens."),
 (72.8, 75.6, "My first video hits ten thousand views."),
 (75.7, 77.3, "Then fifty thousand."),
 (77.4, 79.9, "And then my channel starts blowing up."),
 (80.2, 84.4, "I realize this might be my only chance to earn enough for the game."),
 (84.55, 86.5, "And then... midnight."),
 (86.6, 89.0, "GTA 6 is officially out."),
 (89.3, 91.1, "The whole world launches the game."),
 (91.2, 94.7, "And I'm staring at my screen, watching new notifications roll in."),
 (94.95, 101.3, "My channel keeps growing. But will the money I've made be enough to finally buy GTA 6?"),
 (101.6, 107.4, "Or will I stay the guy who makes money from a game... he has never even played?"),
]
k = Kokoro(MODEL, os.path.join(os.path.dirname(MODEL), 'voices-v1.0.bin'))
SR = 24000; out = np.zeros(int(120 * SR), dtype=np.float32); report = []
for st, lim, txt in LINES:
    speed = 1.0
    while True:
        a, sr = k.create(txt, voice=VOICE, speed=speed, lang='en-us'); assert sr == SR
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0] - 200): nz[-1] + 1200]
        if len(a) / SR <= lim - st or speed >= 1.25: break
        speed = round(speed + 0.05, 2)
    i = int(st * SR); out[i:i + len(a)] += a[: len(out) - i]
    report.append((st, round(st + len(a) / SR, 2), lim, speed, txt))
sf.write(os.path.join(here, 'vo_en.wav'), out / max(1e-6, np.abs(out).max()) * 0.9, SR)
for r in report: print(('OVER ' if r[1] > r[2] + 0.05 else '     '), r[:4], r[4][:50])
