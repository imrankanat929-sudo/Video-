"""Episode 2 score + SFX, built per language on that language's shot timing.
python3 music.py en|ru  ->  music_<lang>.wav, sfx_<lang>.wav
Sections: energetic electronic intro -> streams (chat/notification SFX) -> lo-fi watching -> tension/choice
-> dynamic creating (dino roar, city vanish) -> rising epic on the views -> mysterious ending sting."""
import os, sys, json
lang = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
TM = json.load(open(os.path.join(here, 'timing.json')))[lang]; S = TM['starts']; X = TM['extra']; END = TM['total']
os.environ['SYNTH_DUR'] = str(END)
sys.path.insert(0, os.path.join(here, '..', '..', 'shared'))
from synth import *  # noqa
music, sfx = Track(), Track()

def beat_section(t0, t1, bpm, prog, kick_on=True, snare_on=True, hats=True, bassg=0.5, plk=0.15, padg=0.25, bright=4500, octave=0):
    bt = 60 / bpm; t = t0; b = 0
    while t < t1 - 0.02:
        ch = [n + octave for n in prog[(b // 4) % len(prog)]]
        if kick_on: music.add(kick(), t, 0.8)
        if snare_on and b % 2 == 1: music.add(snare(), t, 0.33)
        if hats: music.add(hat(), t + bt / 2, 0.3, pan=0.25); music.add(hat(), t + bt * 0.25, 0.12, pan=-0.25)
        if bassg: music.add(bass(ch[0] - 12, bt * 0.45), t, bassg); music.add(bass(ch[0] - 12, bt * 0.45), t + bt / 2, bassg * 0.8)
        if plk:
            for q in range(2): music.add(pluck(ch[(b * 2 + q) % 3] + 24, 0.28, bright), t + q * bt / 2, plk, pan=(q - 0.5) * 0.8)
        if padg and b % 4 == 0: music.add(pad([c + 12 for c in ch], min(bt * 4, t1 - t) + 0.4, 2400, a=0.05, r=0.4), t, padg)
        t += bt; b += 1

Am = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]          # Am F C G
Cmaj = [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]]        # C G Am F
Dm = [[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 49, 52]]          # Dm Bb C A
order = list(S.keys()); nxt = lambda k: S[order[order.index(k) + 1]] if order.index(k) + 1 < len(order) else END

# ---- 1. intro (hook) — energetic electronic, starts on frame 0
music.add(boom(2.0), 0.0, 0.9); sfx.add(riser(0.5, 2000, 9000)[::-1], 0.0, 0.5)
beat_section(0.0, S['b1_live'], 128, Am, bright=5500, padg=0.3)
for k in ('a2_world', 'a3_australia', 'a4_internet', 'b1_live'): sfx.add(whoosh(0.5), S[k] - 0.25, 0.35)
for i in range(4): sfx.add(beep(660 if i < 3 else 1320, 0.12), S['a2_world'] + 0.1 + i * 0.18, 0.25)      # zones
sfx.add(ping(91, 0.8), S['a3_australia'] + 0.05, 0.6)
for i in range(14): sfx.add(ping(84 + (i * 5) % 12, 0.35), S['a4_internet'] + i * 0.12, 0.22, pan=((i % 5) - 2) / 3)

# ---- 2. streams — keep energy, chat + notification SFX
beat_section(S['b1_live'], S['c1_open'], 128, Am, plk=0.1, padg=0.25, bright=3500)
for i in range(4): sfx.add(ping(88, 0.4), S['b1_live'] + i * 0.15, 0.3, pan=(i - 1.5) / 2)
t = S['b2_stream']
while t < S['c1_open']:  # chat blips
    sfx.add(bell(96 + int((t * 37) % 5) * 2, 0.08) * 0.6, t, 0.08, pan=(t * 13 % 2) - 1); t += 0.13
eng = tt(nxt('b2_stream') - S['b2_stream']); sfx.add(lp(saw(55 + 30 * eng / eng[-1], eng) + 0.5 * saw(82 + 40 * eng / eng[-1], eng), 900) * env(len(eng), 0.1, 0.3), S['b2_stream'], 0.12)
sfx.add(noise_bed(nxt('b3_millions') - S['b3_millions'], 300, 3000) * env(int((nxt('b3_millions') - S['b3_millions']) * SR), 0.3, 0.5), S['b3_millions'], 0.07)  # crowd

# ---- 3. hero watching — lo-fi
beat_section(S['c1_open'], S['c4_notice'], 88, Cmaj, snare_on=True, bassg=0.4, plk=0.0, padg=0.3)
for k in ('c1_open', 'stream2', 'stream3'):
    tt0 = S.get(k, X.get(k)); sfx.add(click(), tt0, 0.6); sfx.add(ping(84, 0.4), tt0 + 0.05, 0.3)
for i in range(int((nxt('c3_hours') - S['c3_hours']) / 0.11)): sfx.add(tick(), S['c3_hours'] + 0.2 + i * 0.11, 0.18)

# ---- 4. notice / question / choice — tension build
music.add(bell(81, 2.5), S['c4_notice'], 0.5); music.add(bell(88, 2.0), S['c4_notice'] + 0.05, 0.3)
beat_section(S['c5_thousands'], S['d1_question'], 110, Dm, snare_on=False, plk=0.16, padg=0.3, bright=3000)
for i in range(18): sfx.add(click() * 0.6, S['c5_thousands'] + i * 0.06 * 1.2, 0.25, pan=(i % 3 - 1) * 0.5)
for i in range(6): sfx.add(bell(93, 0.3) * 0.6, S['c6_millions'] + 0.15 + i * 0.3, 0.2)       # coins
d1 = S['d1_question']; d3 = S['d3_decide']
music.add(pad([50, 57, 62, 65], d3 - d1 + 0.5, 900, a=0.3), d1, 0.45)
for i in range(int((d3 - d1) / 0.9)): music.add(heartbeat(), d1 + i * 0.9, 0.3)
music.add(riser(d3 - S['d2_choice'], 300, 8000), S['d2_choice'], 0.3)
sfx.add(click(), d3 + 0.2, 0.8); music.add(boom(2.0), d3 + 0.2, 0.9); sfx.add(whoosh(0.6), d3 + 0.3, 0.4)
for i in range(3): sfx.add(whoosh(0.3), d3 + 0.4 + i * 0.12, 0.25, pan=(i - 1) * 0.6)        # streams closing

# ---- 5. creating — dynamic
e1 = S['e1_computer']; music.add(pad([57, 64, 69, 72], S['e2_program'] - e1 + 0.5, 3000, a=0.4), e1, 0.4)
for i in range(16): sfx.add(bell(91 + (i % 5) * 2, 0.6), e1 + 0.3 + i * 0.22, 0.12, pan=(i % 3 - 1) * 0.5)  # magic sparkle
beat_section(S['e2_program'], S['f1_upload'], 132, Am, bright=6000, padg=0.25, plk=0.17)
for i in range(int((S['e3_vid1'] - S['e2_program']) / 0.06)): sfx.add(key(), S['e2_program'] + 0.05 + i * 0.06, 0.3, pan=(i % 5 - 2) / 4)
sfx.add(click(), S['e3_vid1'] - 0.55, 0.7); sfx.add(riser(0.5, 800, 9000), S['e3_vid1'] - 0.5, 0.3)
for k in ('e3_vid1', 'e4_dino', 'e5_vanish'): sfx.add(whoosh(0.5), S[k] - 0.25, 0.4)
dv = S['e3_vid1']
while dv < S['e4_dino']: sfx.add(whoosh(0.7) * 0.7, dv + 0.4, 0.3); sfx.add(boom(0.8) * 0.5, dv + 1.3, 0.4); dv += 2.2   # car jumps
rt = tt(1.4); roar = lp(saw(70 + 20 * np.sin(rt * 9), rt) * (1 + noise_bed(1.4, 100, 2000) * 2), 1500) * env(len(rt), 0.1, 0.6)
sfx.add(roar, S['e4_dino'] + 0.25, 0.45); ds = S['e4_dino']
while ds < S['e5_vanish']: sfx.add(boom(0.9), ds, 0.6); ds += 0.9          # stomps
vt = S['e5_vanish']
for i in range(24): sfx.add(bell(84 + (i * 7) % 24, 0.25) * 0.5, vt + 0.4 + i * 0.12, 0.2, pan=(i % 5 - 2) / 3)   # pixels
sfx.add(riser(1.5, 300, 9000)[::-1], vt + 0.4, 0.3)

# ---- 6. publishing + views — rising epic
f1 = S['f1_upload']; music.add(pad([48, 55, 60, 64], S['f2_nobody'] - f1 + 0.4, 1800, a=0.2), f1, 0.35)
for i in range(16): sfx.add(key(), f1 + i * 0.05, 0.25)
sfx.add(bell(84, 1.0), S['f2_nobody'] - 0.3, 0.4); sfx.add(bell(91, 1.2), S['f2_nobody'] - 0.15, 0.4)
music.add(pad([45, 52, 57, 60], S['f3_gaining'] - S['f2_nobody'] + 0.3, 700, a=0.3), S['f2_nobody'], 0.35)
for i in range(int((S['f3_gaining'] - S['f2_nobody']) / 0.5)): sfx.add(tick(), S['f2_nobody'] + i * 0.5, 0.3)
music.add(riser(S['f4_counter'] - S['f3_gaining'], 200, 9000), S['f3_gaining'], 0.35); sfx.add(ping(93, 0.8), S['f3_gaining'] + 0.6, 0.5)
f4 = S['f4_counter']
music.add(boom(2.0), f4, 0.8)
for k in ('v10k', 'v100k'): music.add(boom(2.5), X[k], 0.9); sfx.add(ping(96, 0.9), X[k], 0.55)
sfx.add(ping(91, 0.7), f4 + 0.05, 0.5); sfx.add(riser(0.6, 2000, 9000)[::-1], X['v100k'] + 0.05, 0.4)
# epic: taiko + big major pads until the problem
BAR = 60 / 100 * 4; beat = BAR / 4; t = f4; b = 0; progE = [[50, 57, 62, 66], [45, 52, 57, 61], [47, 54, 59, 62], [43, 50, 55, 59]]
while t < S['h1_problem'] - 0.05:
    ch = progE[(b // 4) % 4]
    if b % 4 == 0: music.add(pad(ch, BAR + 0.6, 2600, a=0.08, r=0.5), t, 0.5)
    music.add(taiko(), t, 0.55 if b % 2 == 0 else 0.3); music.add(kick(), t, 0.5)
    if b % 4 == 2: music.add(snare(0.4), t, 0.35)
    music.add(bass(ch[0] - 12, beat * 0.9), t, 0.5); music.add(pluck(ch[(b % 3) + 1] + 12, 0.35, 4000), t + beat / 2, 0.15)
    t += beat; b += 1
for i in range(6): sfx.add(ping(86 + i % 3 * 2, 0.4), S['g1_shock'] + 0.15 + i * 0.25, 0.3, pan=0.4)
for i in range(10): sfx.add(bell(98, 0.2) * 0.5, S['g2_others'] + i * 0.3, 0.12)

# ---- 7. new problem — music cuts, mysterious ending
h1 = S['h1_problem']
g = tt(0.5); sfx.add(np.sign(np.sin(2 * np.pi * 70 * g)) * np.exp(-g * 6) * 0.4 + hp(rs.standard_normal(len(g)), 2000) * np.exp(-g * 10) * 0.5, h1, 0.5)
dr = tt(END - h1); drone = lp(saw(hz(38), dr) + saw(hz(38) * 1.006, dr) + saw(hz(44), dr) * 0.5, 400)
music.add(drone * env(len(dr), 0.3, 1.0) * 0.35, h1, 0.6)
for i in range(int((S['h4_end'] - h1) / 0.9)): music.add(heartbeat(), h1 + 0.3 + i * 0.9, 0.4)
sfx.add(ping(88, 1.2), S['h2_streamer'] + 0.05, 0.5)
sfx.add(bell(83, 1.5), S['h3_message'] + 0.2, 0.55); sfx.add(bell(90, 1.5), S['h3_message'] + 0.25, 0.35)
music.add(riser(1.4, 200, 6000), S['h4_end'] - 1.4, 0.3)
# final mysterious sting
h4 = S['h4_end']; music.add(boom(3.0), h4, 0.8)
for i, n in enumerate([62, 65, 68, 71]): music.add(bell(n + 12, 3.0), h4 + 0.05 + i * 0.09, 0.3)
music.add(riser(1.2, 500, 8000)[::-1], h4, 0.25)

write(os.path.join(here, f'music_{lang}.wav'), music, 0.22)
write(os.path.join(here, f'sfx_{lang}.wav'), sfx, 0.12)
print(lang, 'ok', END)
