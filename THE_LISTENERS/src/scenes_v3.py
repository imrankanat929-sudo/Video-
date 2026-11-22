"""EP01 v3: the film cut to the client's recorded voice-over (assets/voiceover_source/voice_ru.mp3).
Adds a cold-open hook, keeps the v2 visuals, places each line at the client's own timing."""
import copy
import scenes as S2
from scenes import *  # noqa
import extvo

V3 = []


def hook1(c, t, T, q):
    corridor(c, t, flicker=1.0, col='#0b0c10', wall='#14161c', floor='#0a0b0d', ceil='#0c0d10')
    k = ease(seg(t, 0.3, T))
    listener(c, 960, 900 + 140 * k, 0.55 + 0.45 * k, turn=lerp(0.7, 0.0, ease(seg(t, 0.8, 2.6))), tilt=lerp(-14, 0, seg(t, 0.8, 2.6)), t=t, glow=1.0, dark=0.2)
    if (t * 25) % 9 < 1:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#ffffff', 0.08)))


def hook2(c, t, T, q):
    V.v_r3_peep(c, t, T, q)


def hook3(c, t, T, q):
    black(c)
    a = seg(t, 0.2, 0.5) * (1 - seg(t, T - 0.6, T))
    alex(c, 960, 1500, 1.6, look=0.0, mouth=0.0, eyes='wide', t=t, sweat=2, arms='cover', tint=C('#59607a', a) if a > 0 else '#000000')


def add(s, **kw):
    s = copy.copy(s)
    s.update(kw)
    V3.append(s)


def mk(draw, vo, **kw):
    d = dict(id=0, part=1, vo=vo, draw=draw, amb='drone_room', mus='dread', sfx=[], min_dur=3.0, cam=None, fade_in=0.0,
             fade_out=0.0, lead=0.3, tail=0.5, gap=0.4, title=None, prompt='')
    d.update(kw)
    return d


# ---------------- hook (cold open)
V3.append(mk(hook1, [('HOOK', 'Алекс, не слушай следующую запись.', (312.50, 315.54))], lead=0.9, tail=0.5,
             sfx=[(0.0, 'static', 0.7), (0.0, 'tape_click', 0.8), (0.2, 'porcelain', 0.6)], cam=(1.0, 1.25, 960, 420), min_dur=4.6,
             prompt='HOOK: dark corridor, the white creature turns its head; a distorted copy of Alex\'s voice.'))
V3.append(mk(hook2, [('W', 'Если однажды ты услышишь собственный голос снаружи, никогда не отвечай.', (274.64, 279.88))], lead=0.2, tail=0.4,
             sfx=[(0.0, 'hit', 0.6), (0.1, 'knock_soft', 0.5)], cam=(1.0, 1.15, 960, 540), min_dur=5.5,
             prompt='HOOK: peephole view of the smooth eyeless face.'))
V3.append(mk(hook3, [('MIMW', 'Алекс…', (321.80, 322.55))], lead=0.8, tail=0.5, mus='silence',
             sfx=[(1.6, 'hit', 1.0), (1.6, 'boom', 0.7)], cam=(1.0, 1.1, 960, 450), min_dur=2.6,
             prompt='HOOK: black, Alex\'s face in the dark, someone whispers his name; hit.'))

# ---------------- main film from v2 scenes
src = S2.SCENES
title = [s for s in src if s['draw'] is S2.v_title2][0]
add(title, vo=[('N', 'The Listeners. Эпизод 1. 15 правил, чтобы выжить среди слушающих.', (0.0, 5.95))], min_dur=6.4, lead=0.3, tail=0.4,
    sfx=[(0.0, 'stinger', 0.5)])
KEEP_NB = {5, 10, 15}
for s in src:
    if s is title:
        continue
    pr = s['prompt']
    if pr.startswith('Insert: Alex writes rule'):
        n = int(pr.split('rule ')[1].split(' ')[0])
        if n in KEEP_NB:
            add(s, min_dur=3.0)
        continue
    kw = {}
    kw['lead'] = 0.2 if abs(s['lead'] - 0.8) < 1e-6 else s['lead']
    kw['tail'] = 0.4 if abs(s['tail'] - 1.4) < 1e-6 else s['tail']
    if s['vo']:
        kw['min_dur'] = 3.0
    elif s['draw'] is S2.v_end2:
        kw['min_dur'] = 5.0
    else:
        kw['min_dur'] = min(s['min_dur'], 5.5)
    add(s, **kw)

# ---------------- align every narration line to the recording
lines = [(i, j, txt) for i, s in enumerate(V3) for j, (spk, txt, *rest) in enumerate(s['vo']) if not rest and spk != 'FRIEND']
spans = extvo.align([x[2] for x in lines])
for (i, j, txt), sp in zip(lines, spans):
    spk = V3[i]['vo'][j][0]
    if sp is None:
        print('NOT ALIGNED:', txt)
        continue
    V3[i]['vo'] = list(V3[i]['vo'])
    V3[i]['vo'][j] = (spk, txt, sp)

SCENES = V3
for k, s in enumerate(SCENES, 1):
    s['id'] = k
