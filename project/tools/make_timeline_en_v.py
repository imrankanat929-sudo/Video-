"""Builds config/timeline.en_v.json: English vertical (9:16) Shorts version, flat style.
Times are written in VOICE time (config/transcript_en.json) and shifted by OFF."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFF = 0.3
TIME_KEYS = {'start', 'end', 'at', 'to', 'onAt', 'offAt', 'phoneOnAt', 'phoneOffAt', 'phoneAt', 'handAt', 'vibAt', 'from', 'since', 'count',
             'txRed', 'refresh', 'stolen', 'scroll', 'calling', 'voice', 'typing', 'reveal', 'focus', 'docs', 'warn', 'prog', 'redRow',
             'redAt', 'darkAt', 'millionAt', 'strikeAt', 'callingAt', 'q', 'a', 'b', 'c', 'sub', 'part2', 'jolt', 'flash', 'fadeOut',
             'redFlash', 'stampAt', 'faceAt', 'question', 'carAt', 'homeAt', 'freeAt', 'crossAt', 'answerAt', 'eyes', 'red', 't', 'until'}
def shift(o, key=None):
    if isinstance(o, dict): return {k: shift(v, k) for k, v in o.items()}
    if isinstance(o, list):
        if key == 'cam' and o and isinstance(o[0], list) and len(o[0]) == 4: return [[round(k[0] + OFF, 3)] + k[1:] for k in o]
        if key in ('faceSeq', 'exprSeq', 'exprAt'):
            return [[round(x[0] + OFF, 3), x[1]] for x in o] if isinstance(o[0], list) else [round(o[0] + OFF, 3), o[1]]
        if key == 'to': return o
        return [shift(v, key) for v in o]
    if key in TIME_KEYS and isinstance(o, (int, float)) and not isinstance(o, bool): return round(o + OFF, 3)
    return o

M, N = 'morning_clock', 'evening_clock'
Y, R, B, G = 'yellow', 'red', 'blue', 'green'
def tag(text, color=Y, at=None, rot=0):
    d = {'text': text, 'color': color, 'rot': rot}
    if at is not None: d['at'] = at
    return d
CAM0 = [[540, 960, 1.0], [540, 960, 1.06]]
lock = lambda at, body, red=False: {'kind': 'lock', 'flash': at, 'notifs': [{'at': at, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': body, 'big': True, 'red': red}]}
shots = [
 dict(id='01', type='f_room', start=-0.3, end=3.4, inT='black', inDur=0.5, morning=True, clock=M, cam=[[540, 960, 1.0], [600, 1000, 1.18]], phoneOnAt=1.86, vibAt=1.86, exprAt=[2.6, 'shock'], tag=tag('ONE MORNING')),
 dict(id='02', type='f_phone', start=3.4, end=6.4, clock=M, cam=[[540, 700, 1.25], [540, 660, 1.4]], screen={'kind': 'wallet', 'count': 3.96}, face='neutral', faceAt=4.0, faceSeq=[[4.5, 'shock']], tag=tag('+10 BTC', G, 4.0)),
 dict(id='03', type='f_face', start=6.4, end=10.4, clock=M, expr='happy', exprSeq=[[6.98, 'rich']], coins=True, cam=[[540, 960, 1.0], [540, 920, 1.12]], tag=tag('A FORTUNE', G, 6.9)),
 dict(id='04', type='f_face', start=10.4, end=12.1, inT='flash', inDur=0.2, expr='worry', red=10.5, question=11.16, cam=[[540, 960, 1.0], [540, 940, 1.12]], tag=tag('ONE PROBLEM', R, 11.16)),
 dict(id='05', type='f_phone', start=12.1, end=14.5, clock='clock_night', cam=[[540, 780, 1.0], [540, 700, 1.1]], snap={'at': 13.42, 'to': [540, 600, 1.5]}, stampAt=13.42, redFlash=13.42, red=13.42, screen={'kind': 'news'}, tag=tag('THESE BITCOINS ARE STOLEN', R, 13.42, -0.03)),
 dict(id='06', type='f_window', start=14.5, end=16.5, inT='fade', inDur=0.3, eyes=14.62, red=14.62, cam=[[540, 960, 1.0], [540, 900, 1.12]], tag=tag('SOMEONE KNOWS', R, 14.62)),
 dict(id='07', type='f_rewind', start=16.5, end=18.3, inT='flash', inDur=0.2, tag=tag('IT STARTED EARLIER', Y)),
 dict(id='08', type='f_room', start=18.3, end=21.0, inT='black', inDur=0.4, morning=True, clock=M, cam=[[540, 960, 1.05], [520, 1000, 1.15]], handAt=20.14, phoneOn=0.8, tag=tag('AN ORDINARY MORNING', B)),
 dict(id='09', type='f_phone', start=21.0, end=25.8, clock=M, cam=[[21.0, 540, 700, 1.15], [23.6, 540, 680, 1.25], [23.8, 540, 600, 1.15], [25.8, 540, 580, 1.25]], face='neutral', faceAt=21.8, faceSeq=[[24.0, 'skeptic']],
      screen=[lock(21.7, 'm_lucky'), {'from': 23.7, 'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 23.84}]}], tag=tag('UNKNOWN SENDER', R, 22.3)),
 dict(id='10', type='f_face', start=25.8, end=27.7, clock=M, expr='skeptic', lookX=0.6, cam=[[540, 960, 1.05], [540, 960, 1.0]], tag=tag('SPAM?', B, 27.0)),
 dict(id='11', type='f_phone', start=27.7, end=29.8, clock=M, cam=[[540, 780, 1.0], [540, 640, 1.35]], face='neutral', faceAt=28.0,
      screen=[{'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}]}, {'from': 28.3, 'kind': 'splash'}, {'from': 28.9, 'kind': 'wallet', 'count': 29.0}]),
 dict(id='12', type='f_phone', start=29.8, end=32.3, clock=M, cam=[[540, 640, 1.4], [540, 600, 1.55]], face='shock', screen={'kind': 'wallet', 'pulse': 1}, tag=tag('10 BTC ON THE BALANCE', Y, 30.82)),
 dict(id='13', type='f_face', start=32.3, end=34.4, clock=M, expr='shock', sweat=True, cam=[[540, 960, 1.1], [540, 900, 1.3]], tag=tag('NO WAY', Y, 32.9)),
 dict(id='14', type='f_phone', start=34.4, end=38.2, clock=M, cam=[[540, 780, 1.0], [540, 640, 1.3]], face='worry', faceAt=34.6, faceSeq=[[36.8, 'shock']], screen={'kind': 'wallet', 'refresh': [34.66, 35.44, 36.1]}, tag=tag('REFRESH', B, 34.66)),
 dict(id='15', type='f_face', start=38.2, end=41.3, inT='fade', inDur=0.3, clock=M, expr='happy', exprSeq=[[39.4, 'rich']], coins=True, cam=[[540, 960, 1.0], [540, 920, 1.12]], tag=tag('YOU COULD BUY ANYTHING', G, 39.4)),
 dict(id='16', type='f_dream', start=41.3, end=46.1, cam=CAM0, carAt=41.70, homeAt=42.96, freeAt=44.66, homeKey='dream_house', freeKey='dream_life', tag=tag('DREAMS', B)),
 dict(id='17', type='f_monitor', start=46.1, end=49.2, inT='fade', inDur=0.3, clock=M, cam=[[480, 820, 1.05], [600, 800, 1.2]], monitor={'kind': 'desktop', 'redRow': 48.32}, tag=tag('WHERE DID IT COME FROM?', Y, 47.3)),
 dict(id='18', type='f_phone', start=49.2, end=52.5, clock=M, cam=[[540, 780, 1.05], [540, 700, 1.2]], face='neutral', faceSeq=[[50.92, 'shock']], screen={'kind': 'news', 'scroll': [50.0, 52.3], 'scrollBy': 160}, tag=tag('SHOCKING NEWS', R, 50.92)),
 dict(id='19', type='f_graph', start=52.5, end=57.1, cam=[[540, 1100, 1.0], [540, 1000, 1.05]], reveal=[52.7, 56.0], tag=tag('SEVERAL DAYS EARLIER', B)),
 dict(id='20', type='f_graph', start=57.1, end=62.3, cam=[[57.1, 540, 1000, 1.05], [59.7, 760, 740, 1.4], [62.3, 860, 600, 1.7]], focus=59.72, crossAt=58.4, tag=tag('SAME ADDRESS', R, 59.72)),
 dict(id='21', type='f_face', start=62.3, end=64.9, expr='worry', exprSeq=[[63.7, 'shock']], sweat=True, cam=[[540, 960, 1.0], [540, 930, 1.15]], tag=tag('IT ALL MAKES SENSE', Y, 63.3)),
 dict(id='22', type='f_face', start=64.9, end=66.6, expr='scared', red=True, sweat=True, cam=[[540, 960, 1.1], [540, 900, 1.25]], darkAt=65.5, caption={'at': 65.74, 'text': "THIS WASN'T A GIFT"}),
 dict(id='23', type='f_phone', start=66.6, end=68.9, inT='black', inDur=0.3, clock=M, cam=[[540, 1000, 1.6], [540, 990, 1.7]], face='worry', screen={'kind': 'wallet', 'txRed': 67.2}, tag=tag('SOMEONE USED YOUR WALLET', R, 66.8)),
 dict(id='24', type='f_room', start=68.9, end=71.0, cam=[[540, 960, 1.15], [560, 980, 1.1]], phoneOn=1, phoneOffAt=70.06, expr='determined', tag=tag("DON'T TOUCH IT", B)),
 dict(id='25', type='f_room', start=71.0, end=73.2, cam=[[540, 960, 1.0], [620, 1020, 1.25]], vibAt=71.92, phoneOnAt=71.92, exprAt=[72.2, 'shock'], tag=tag('BZZZ', R, 71.92)),
 dict(id='26', type='f_phone', start=73.2, end=78.3, clock=M, cam=[[540, 700, 1.1], [540, 760, 1.25]], face='worry', sweat=True,
      screen={'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}, {'key': 'm_dont', 'at': 73.6, 'red': True}, {'key': 'm_keep_short', 'at': 77.02, 'red': True}], 'typing': [75.9, 77.0]}, tag=tag('ANOTHER MESSAGE', R, 73.3)),
 dict(id='27', type='f_face', start=78.3, end=82.9, inT='fade', inDur=0.3, expr='scared', sweat=True, shake=6, question=80.3, cam=[[540, 960, 1.0], [540, 920, 1.15]], tag=tag('HOW DO THEY KNOW?', R, 80.3)),
 dict(id='28', type='f_phone', start=82.9, end=87.4, clock=M, vibAt=83.6, onAt=83.6, red=85.56, cam=[[82.9, 540, 800, 1.0], [85.5, 540, 640, 1.35], [85.7, 540, 600, 1.6], [87.4, 540, 600, 1.65]],
      screen=lock(83.9, 'm_know', True), tag=tag('WE KNOW WHO YOU ARE', R, 85.56, -0.04)),
 dict(id='29', type='f_phone', start=87.4, end=91.3, inT='black', inDur=0.3, clock=N, vibAt=[88.9, 90.2], cam=[[540, 800, 1.0], [540, 740, 1.15]], face='scared', faceAt=89.3, screen={'kind': 'incoming'}, tag=tag('UNKNOWN NUMBER', R, 90.16)),
 dict(id='30', type='f_call', start=91.3, end=100.8, clock=N, jolt=91.62, answerAt=91.62, cam=[[91.3, 540, 960, 1.0], [97.5, 520, 900, 1.12], [100.8, 500, 860, 1.25]], voice=[[98.16, 102.4]],
      bubbles=[{'at': 92.7, 'to': 95.4, 'text': '…'}, {'at': 98.16, 'to': 100.8, 'text': 'You have something that belongs to us.', 'red': True}],
      tag=tag('SILENCE', B, 92.7)),
 dict(id='31', type='f_big', start=100.8, end=103.2, inT='flash', inDur=0.2, clock='countdown_clock', sym='24', col='red', label='HOURS', box='YOU HAVE 24 HOURS', ill='countdown', at=100.88),
 dict(id='32', type='f_phone', start=103.2, end=104.7, clock=N, cam=[[540, 760, 1.1], [540, 760, 1.15]], face='scared', screen={'kind': 'ended'}, fadeOut=[104.1, 104.7], tag=tag('CALL ENDED', R)),
 dict(id='33', type='f_window', start=104.7, end=109.6, inT='fade', inDur=0.3, eyes=104.9, red=104.9, cam=[[540, 960, 1.0], [540, 880, 1.15]], tag=tag('THIS IS SERIOUS', R, 107.86)),
 dict(id='34', type='f_monitor', start=109.6, end=112.6, inT='fade', inDur=0.3, clock=N, cam=[[540, 900, 1.05], [540, 820, 1.2]], monitor={'kind': 'docs', 'from': 109.9}, tag=tag('SAVING THE MESSAGES', B, 109.98)),
 dict(id='35', type='f_phone', start=112.6, end=115.5, clock=N, cam=[[540, 800, 1.0], [540, 720, 1.2]], face='determined', screen={'kind': 'call'}, tag=tag('POLICE', B, 112.74)),
 dict(id='36', type='f_room', start=115.5, end=118.1, inT='fade', inDur=0.3, red=True, cam=[[540, 960, 1.0], [600, 1020, 1.2]], phoneOnAt=116.56, vibAt=116.56, exprAt=[116.8, 'shock'], monitor={'kind': 'docs'}, tag=tag('ONE FINAL MESSAGE', R, 116.18)),
 dict(id='37', type='f_phone', start=118.1, end=121.0, clock=N, vibAt=118.1, onAt=118.1, red=118.22, cam=[[540, 820, 1.0], [540, 620, 1.5]], screen=lock(118.22, 'm_keep2', True)),
 dict(id='38', type='f_face', start=121.0, end=122.6, inT='fade', inDur=0.3, expr='worry', phoneLight=0.8, lookY=0.8, cam=[[540, 960, 1.15], [540, 960, 1.25]]),
 dict(id='39', type='f_phone', start=122.6, end=124.0, clock=N, cam=[[540, 680, 1.3], [540, 660, 1.45]], screen={'kind': 'wallet', 'pulse': 1}, tag=tag('10 BTC', Y)),
 dict(id='40', type='f_face', start=124.0, end=126.0, inT='fade', inDur=0.3, expr='rich', coins=True, cam=[[540, 960, 1.0], [540, 920, 1.1]], tag=tag('A CHANCE TO GET RICH', G)),
 dict(id='41', type='f_split', start=126.0, end=128.5, inT='flash', inDur=0.2, tag=tag('TWO CHOICES', Y, 127.0)),
 dict(id='42', type='f_big', start=128.5, end=133.3, inT='flash', inDur=0.2, sym='A', col='yellow', label='OPTION', box='KEEP THE MONEY', ill='wallet', at=128.58, tag=tag('CRIMINAL INVESTIGATION', R, 131.76)),
 dict(id='43', type='f_big', start=133.3, end=138.2, inT='flash', inDur=0.2, sym='B', col='red', label='OPTION', box='CALL THE POLICE', ill='call', at=133.46, callingAt=134.76, strikeAt=137.04),
 dict(id='44', type='f_face', start=138.2, end=140.9, inT='black', inDur=0.3, expr='determined', cam=[[540, 960, 1.0], [540, 900, 1.2]], tag=tag('RIGHT NOW', Y, 139.88)),
 dict(id='45', type='f_final', start=140.9, end=154.9, inT='black', inDur=0.3, subs=False, q=141.06, a=142.7, b=145.04, c=147.62, part2=149.3, sub=150.8),
]
for s in shots:
    if 'inT' in s: s['in'] = s.pop('inT')

events = [
 {'t': -0.3, 'type': 'roomtone', 'until': 154.6},
 {'t': 1.86, 'type': 'vibrate', 'n': 2}, {'t': 3.96, 'type': 'hit', 'gain': -4}, {'t': 4.0, 'type': 'ping'}, {'t': 6.98, 'type': 'shimmer'},
 {'t': 10.3, 'type': 'whoosh', 'gain': -8}, {'t': 13.2, 'type': 'whoosh', 'gain': -4}, {'t': 13.42, 'type': 'hit', 'gain': -2},
 {'t': 16.2, 'type': 'whoosh', 'gain': -6}, {'t': 16.55, 'type': 'rewind'},
 {'t': 21.7, 'type': 'vibrate', 'n': 1}, {'t': 21.75, 'type': 'ping'}, {'t': 23.7, 'type': 'click'},
 {'t': 28.3, 'type': 'click'}, {'t': 30.82, 'type': 'hit', 'gain': -8},
 {'t': 34.66, 'type': 'refresh'}, {'t': 35.44, 'type': 'refresh'}, {'t': 36.1, 'type': 'refresh'}, {'t': 39.4, 'type': 'shimmer'},
 {'t': 41.70, 'type': 'tick'}, {'t': 42.96, 'type': 'tick'}, {'t': 44.66, 'type': 'tick'},
 {'t': 46.6, 'type': 'keyboard', 'dur': 1.8}, {'t': 48.32, 'type': 'ui'}, {'t': 50.0, 'type': 'refresh'}, {'t': 50.92, 'type': 'hit', 'gain': -8},
 {'t': 52.7, 'type': 'ui'}, {'t': 59.72, 'type': 'alarm'}, {'t': 59.72, 'type': 'hit', 'gain': -6},
 {'t': 65.5, 'type': 'hit', 'gain': -2}, {'t': 67.2, 'type': 'ui'}, {'t': 70.06, 'type': 'click'},
 {'t': 71.92, 'type': 'vibrate', 'n': 3}, {'t': 73.6, 'type': 'ping'}, {'t': 77.02, 'type': 'ping'},
 {'t': 83.6, 'type': 'vibrate', 'n': 2}, {'t': 83.9, 'type': 'ping'}, {'t': 85.56, 'type': 'hit', 'gain': -2},
 {'t': 87.6, 'type': 'ringtone', 'dur': 3.6}, {'t': 88.9, 'type': 'vibrate', 'n': 4}, {'t': 91.62, 'type': 'click'},
 {'t': 100.88, 'type': 'hit', 'gain': 0}, {'t': 100.88, 'type': 'clock', 'dur': 2.2}, {'t': 103.68, 'type': 'hangup'},
 {'t': 110.0, 'type': 'keyboard', 'dur': 2.4}, {'t': 112.74, 'type': 'ui'},
 {'t': 116.56, 'type': 'vibrate', 'n': 2}, {'t': 118.22, 'type': 'hit', 'gain': -3}, {'t': 118.25, 'type': 'ping'},
 {'t': 122.72, 'type': 'shimmer'}, {'t': 126.0, 'type': 'whoosh', 'gain': -8},
 {'t': 128.58, 'type': 'hit', 'gain': -4}, {'t': 131.76, 'type': 'alarm'},
 {'t': 133.46, 'type': 'hit', 'gain': -4}, {'t': 134.76, 'type': 'ringback', 'dur': 3.4}, {'t': 137.04, 'type': 'ui'},
 {'t': 141.06, 'type': 'hit', 'gain': -2}, {'t': 142.7, 'type': 'tick'}, {'t': 145.04, 'type': 'tick'}, {'t': 147.62, 'type': 'tick'},
 {'t': 149.3, 'type': 'shimmer'}, {'t': 151.9, 'type': 'click'},
]
music = [(0, 0.3), (4.0, 0.55), (6.4, 0.7), (10.3, 0.3), (12.1, 0.8), (16.5, 0.3), (18.3, 0.25), (29.8, 0.45), (38.2, 0.6),
         (46.1, 0.55), (57.1, 0.8), (65.0, 0.9), (66.6, 0.4), (71.0, 0.6), (82.9, 0.75), (86.8, 0.0), (87.4, 0.0), (87.6, 0.6),
         (91.6, 0.0), (98.0, 0.0), (98.2, 0.6), (100.8, 0.9), (103.7, 0.4), (115.5, 0.6), (118.0, 0.1), (118.2, 0.8),
         (126.0, 0.6), (128.5, 0.8), (138.2, 0.5), (140.9, 0.4), (148.8, 0.2), (149.3, 0.35), (153.9, 0.0)]
chords = [(-0.3, 10.6, [38, 45, 53]), (10.2, 16.8, [38, 46, 52, 57]), (16.4, 29.9, [38, 45, 52, 53]), (29.5, 46.4, [34, 41, 50, 53]),
          (46.0, 69.2, [38, 46, 52, 57]), (68.8, 87.7, [31, 38, 46, 50]), (87.2, 113.9, [33, 40, 49, 52]), (113.5, 128.7, [38, 46, 52, 57]),
          (128.3, 133.6, [34, 41, 50, 53]), (133.2, 141.2, [31, 38, 46, 50]), (140.8, 149.6, [38, 45, 50, 53]), (149.2, 154.6, [33, 40, 45, 52])]
heart = [(12.1, 16.5, 70), (57.1, 68.9, 72), (82.9, 86.8, 80), (87.4, 104.7, 84), (113.7, 126.0, 70), (138.2, 147.0, 60)]

tl = {
  '_comment': 'English vertical (9:16) flat Shorts version. Generated by tools/make_timeline_en_v.py.',
  'fps': 30, 'width': 1080, 'height': 1920, 'duration': 155.2, 'flat': True,
  'voice': 'assets/audio/voice_en.mp3', 'voiceOffset': OFF, 'strings': 'config/strings.en.json', 'transcriptFile': 'config/transcript_en.json',
  'overlay': {'stages': [{'t': 0.0, 'name': 'TRANSFER'}, {'t': 46.4, 'name': 'THEFT'}, {'t': 69.2, 'name': 'THREATS'}, {'t': 126.3, 'name': 'CHOICE'}],
              'hlYellow': r"^(10|24|bitcoins?|money|fortune|rich|wallet|unknown|message|car|house|life|news|crypto|cryptocurrency|hours|comments|choose|police|spam|balance|lucky|evening|ringing|address)$",
              'hlRed': r"^(don't|not|nobody|wasn't|stolen|criminals|someone|shocking|criminal|investigation|we|know|serious)$"},
  'shots': shift(shots),
  'cues': {'silence_start': 87.1, 'keep_msg': 87.7, 'camera_freeze': 153.9, 'hard_black': 154.9},
  'audio': {'voiceGainDb': 0, 'musicGainDb': -13, 'events': shift(events), 'music': [{'t': round(t + OFF, 3), 'level': l} for t, l in music],
            'chords': [[round(max(a + OFF, 0), 3), round(b + OFF, 3), n] for a, b, n in chords],
            'heart': [[round(a + OFF, 3), round(b + OFF, 3), bpm] for a, b, bpm in heart], 'eerie': [[69.2, 18.0], [113.9, 12.0]]},
}
tl['shots'][0]['start'] = 0.0
tl['shots'][-1]['end'] = tl['duration']
tl['audio']['events'][0]['t'] = 0.0
for a, b in zip(tl['shots'], tl['shots'][1:]): assert abs(a['end'] - b['start']) < 1e-6, (a['id'], b['id'])
json.dump(tl, open(os.path.join(ROOT, 'config', 'timeline.en_v.json'), 'w'), ensure_ascii=False, indent=1)
print('shots', len(shots), 'duration', tl['duration'])
