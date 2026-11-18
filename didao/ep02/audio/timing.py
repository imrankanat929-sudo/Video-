"""Shot start times for both languages: anchors are word times in the ORIGINAL VO, mapped through the
pause-tightening cuts, plus LEAD. Writes render/timing.js and audio/timing.json."""
import json, os
here = os.path.dirname(os.path.abspath(__file__)); LEAD = 0.25; TAIL = 2.3
# event: (en_time, ru_time) in original VO seconds
EV = [
 ('a1_hook', 0, 0), ('a2_world', 2.66, 2.52), ('a3_australia', 4.52, 5.48), ('a4_internet', 7.3, 8.56),
 ('b1_live', 9.84, 10.98), ('b2_stream', 11.7, 13.2), ('b3_millions', 15.54, 16.78),
 ('c1_open', 17.38, 19.56), ('c2_streams', 19.06, 21.38), ('c3_hours', 22.34, 24.04), ('c4_notice', 26.08, 28.0),
 ('c5_thousands', 28.78, 31.0), ('c6_millions', 31.26, 33.74),
 ('d1_question', 33.98, 36.82), ('d2_choice', 36.48, 39.12), ('d3_decide', 38.42, 41.44),
 ('e1_computer', 40.64, 43.98), ('e2_program', 45.1, 49.82), ('e3_vid1', 47.58, 52.18), ('e4_dino', 52.56, 57.14), ('e5_vanish', 56.37, 61.86),
 ('f1_upload', 60.24, 66.26), ('f2_nobody', 62.64, 68.86), ('f3_gaining', 65.14, 70.76), ('f4_counter', 68.44, 73.96),
 ('g1_shock', 73.18, 77.94), ('g2_others', 74.96, 80.38), ('g3_channel', 77.24, 82.44),
 ('h1_problem', 79.16, 84.84), ('h2_streamer', 80.92, 87.42), ('h3_message', 83.88, 90.92), ('h4_end', 86.04, 93.12),
]
EXTRA = {  # in-shot sync points
 'stream2': (20.18, 22.4), 'stream3': (21.32, 23.26), 'v10k': (70.2, 75.52), 'v100k': (71.56, 76.72),
}
out = {}
for li, lang in enumerate(['en', 'ru']):
    cuts = json.load(open(os.path.join(here, f'vo_{lang}_map.json')))['cuts']
    def m(t):
        r = t
        for c0, c1 in cuts:
            if t >= c1: r -= c1 - c0
            elif t > c0: r -= t - c0
        return round(r + LEAD, 3)
    import soundfile as sf
    vo_len = sf.info(os.path.join(here, f'vo_{lang}_tight.wav')).duration
    total = round(LEAD + vo_len + TAIL, 2)
    out[lang] = {'lead': LEAD, 'total': total, 'starts': {e[0]: m(e[1 + li]) for e in EV}, 'extra': {k: m(v[li]) for k, v in EXTRA.items()}}
    out[lang]['starts']['a1_hook'] = 0.0
    st = list(out[lang]['starts'].values()); print(lang, 'total', total, 'shots', len(st), 'min dur', round(min(b - a for a, b in zip(st, st[1:] + [total])), 2), 'max', round(max(b - a for a, b in zip(st, st[1:] + [total])), 2))
json.dump(out, open(os.path.join(here, 'timing.json'), 'w'), indent=1)
open(os.path.join(here, '..', 'render', 'timing.js'), 'w').write('const TIMING = ' + json.dumps(out) + ';\n')
