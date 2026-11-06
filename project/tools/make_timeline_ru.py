"""Builds config/timeline.ru.json (full episode, 3 min voice-over).

Times below are written in VOICE time (as in config/transcript_ru.json) and shifted by
VOICE_OFFSET to video time. Edit here and re-run, or edit the generated JSON directly.
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFF = 0.5
TIME_KEYS = {'start', 'end', 'at', 'onAt', 'offAt', 'phoneOnAt', 'phoneOffAt', 'phoneAt', 'vibAt', 'from', 'since', 'count',
             'txRed', 'dimAt', 'refresh', 'stolen', 'scroll', 'calling', 'voice', 'typing', 'missed', 'reveal', 'focus', 'docs',
             'warn', 'prog', 'redRow', 'redAt', 'tiltAt', 'darkAt', 'millionAt', 'strikeAt', 'callingAt', 'walletAt',
             'emergencyAt', 'q', 'a', 'b', 'c', 'd', 'd2', 'freeze', 'jolt', 'flash', 'fadeOut', 'redFlash', 't', 'until', 'red'}

def shift(o, key=None):
    if isinstance(o, dict): return {k: shift(v, k) for k, v in o.items()}
    if isinstance(o, list):
        if key == 'cam' and o and isinstance(o[0], list) and len(o[0]) == 4: return [[round(k[0] + OFF, 3)] + k[1:] for k in o]
        return [shift(v, key) for v in o]
    if key in TIME_KEYS and isinstance(o, (int, float)) and not isinstance(o, bool): return round(o + OFF, 3)
    return o

M, N = 'morning_clock', 'evening_clock'
wallet = {'kind': 'wallet'}
shots = [
 # --- hook ---
 dict(id='01_room', type='room', start=-0.5, end=3.4, inT='black', inDur=0.8, title=True, morning=True, cam=[[990, 540, 1], [900, 600, 1.25]], phoneOnAt=2.9, vibAt=2.9, clock=M),
 dict(id='02_balance', type='desk', start=3.4, end=5.9, cam=[[960, 390, 1.7], [960, 370, 1.85]], screen={'kind': 'wallet', 'count': 4.28}, clock=M),
 dict(id='03_huge', type='held', start=5.9, end=7.3, inT='fade', inDur=0.3, cam=[[960, 420, 1.6], [960, 400, 1.8]], screen={'kind': 'wallet', 'pulse': 1}, clock=M),
 dict(id='04_dream', type='dream', start=7.3, end=12.5, inT='fade', inDur=0.4, cam=[[860, 540, 1], [1060, 540, 1.05]], carAt=8.18, homeAt=8.94, freeAt=10.32),
 dict(id='05_problem', type='room', start=12.5, end=14.6, inT='black', inDur=0.35, cam=[[960, 560, 1.15], [1000, 560, 1.25]], tiltAt=12.7, dim=0.25, phoneOn=0.6),
 dict(id='06_stolen', type='held', start=14.6, end=16.9, cam=[[960, 560, 1.15], [960, 470, 1.35]], snap={'at': 15.48, 'to': [960, 380, 2.0]}, redFlash=15.48, fadeOut=[16.5, 16.9], screen={'kind': 'news', 'stolen': 15.48}),
 dict(id='07_someone', type='window', start=16.9, end=20.2, inT='fade', inDur=0.4, cam=[[980, 520, 1.05], [1020, 520, 1.17]], red=17.6),
 dict(id='08_earlier', type='title', style='rewind', start=20.2, end=22.4, inT='flash', inDur=0.25, text='earlier', at=20.38),
 # --- morning ---
 dict(id='09_morning', type='window', start=22.4, end=25.7, inT='black', inDur=0.5, morning=True, cam=[[940, 520, 1.0], [1000, 520, 1.12]], phoneAt=24.82),
 dict(id='10_lucky', type='held', start=25.7, end=31.0, clock=M, cam=[[25.7, 960, 500, 1.4], [28.3, 960, 470, 1.6], [28.5, 960, 450, 1.35], [31.0, 960, 430, 1.5]],
      screen=[{'kind': 'lock', 'notifs': [{'at': 26.38, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': 'm_lucky', 'big': True}]},
              {'from': 28.4, 'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 28.5}]}]),
 dict(id='11_spam', type='desk', start=31.0, end=33.7, inT='fade', inDur=0.3, clock=M, cam=[[960, 520, 1.25], [960, 560, 1.05]], screen={'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}]}),
 dict(id='12_freeze', type='desk', start=33.7, end=37.3, clock=M, cam=[[33.7, 960, 540, 1.1], [36.4, 960, 390, 1.75], [37.3, 960, 388, 1.77]],
      screen=[{'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}]}, {'from': 34.5, 'kind': 'splash'}, {'from': 35.3, 'kind': 'wallet', 'count': 35.4}]),
 dict(id='13_really', type='held', start=37.3, end=40.3, clock=M, hand=2, cam=[[960, 400, 1.9], [960, 410, 2.05]], screen={'kind': 'wallet', 'pulse': 1}),
 dict(id='14_check', type='desk', start=40.3, end=44.3, inT='fade', inDur=0.3, clock=M, cam=[[960, 560, 1.2], [960, 420, 1.55]], screen={'kind': 'wallet', 'refresh': [42.68, 43.45]}),
 dict(id='15_restart', type='held', start=44.3, end=48.6, clock=M, cam=[[960, 520, 1.25], [960, 420, 1.6]],
      screen=[{'kind': 'wallet'}, {'from': 44.5, 'kind': 'off'}, {'from': 44.9, 'kind': 'splash'}, {'from': 46.3, 'kind': 'wallet', 'pulse': 1}]),
 dict(id='16_rich', type='window', start=48.6, end=53.9, inT='fade', inDur=0.5, bright=True, phone=0.7, cam=[[1000, 520, 1.0], [960, 520, 1.15]]),
 # --- investigation ---
 dict(id='17_source', type='monitor', start=53.9, end=57.1, inT='fade', inDur=0.4, cam=[[700, 540, 1.2], [1150, 560, 1.45]], monitor={'kind': 'desktop', 'redRow': 56.18}),
 dict(id='18_news', type='held', start=57.1, end=60.7, clock=M, cam=[[960, 560, 1.2], [960, 520, 1.3]], screen={'kind': 'news', 'scroll': [58.0, 60.5], 'scrollBy': 160}),
 dict(id='19_graph', type='monitor', start=60.7, end=65.3, fg=False, cam=[[600, 520, 1.3], [900, 540, 1.35]], monitor={'kind': 'graph', 'reveal': [60.9, 63.5]}),
 dict(id='20_match', type='monitor', start=65.3, end=71.9, fg=False, cam=[[65.3, 900, 540, 1.35], [68.6, 1300, 600, 1.5], [71.9, 1350, 620, 1.85]], redAt=68.86, monitor={'kind': 'graph', 'focus': 68.86}),
 dict(id='21_not_gift', type='room', start=71.9, end=74.4, cam=[[960, 560, 1.1], [1000, 580, 1.25]], red=True, monitor={'kind': 'graph', 'focus': -1}, darkAt=73.3, caption={'at': 73.5, 'key': 'not_gift'}),
 dict(id='22_used', type='desk', start=74.4, end=76.6, inT='black', inDur=0.3, clock=M, cam=[[960, 710, 1.8], [960, 700, 1.95]], screen={'kind': 'wallet', 'txRed': 74.84}),
 dict(id='23_dont_touch', type='desk', start=76.6, end=78.5, clock=M, cam=[[960, 540, 1.05], [960, 540, 0.95]], dark=0.75, screen=wallet, offAt=77.8),
 # --- threats ---
 dict(id='24_vibrate', type='side', start=78.5, end=80.7, cam=[[900, 540, 1.0], [960, 520, 1.12]], vibAt=79.3),
 dict(id='25_dont_return', type='held', start=80.7, end=85.3, clock=M, cam=[[960, 560, 1.35], [960, 620, 1.55]],
      screen={'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}, {'key': 'm_dont', 'at': 80.9, 'red': True}, {'key': 'm_keep_short', 'at': 84.06, 'red': True}], 'typing': [82.7, 84.0]}),
 dict(id='26_nervous', type='room', start=85.3, end=90.7, inT='fade', inDur=0.4, shake=5, tiltAt=85.5, tilt=-0.12, cam=[[1100, 560, 1.3], [1150, 540, 1.5]], phoneOn=0.7),
 dict(id='27_we_know', type='desk', start=90.7, end=96.3, clock=M, vibAt=92.6, dark=0.72, cam=[[90.7, 960, 540, 1.0], [94.3, 960, 470, 1.6], [94.5, 960, 450, 1.9], [96.3, 960, 450, 1.95]],
      screen={'kind': 'lock', 'flash': 92.9, 'notifs': [{'at': 92.9, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': 'm_know', 'big': True, 'red': True}]}, onAt=92.6),
 dict(id='28_serious', type='window', start=96.3, end=100.3, inT='fade', inDur=0.5, red=96.5, cam=[[1000, 520, 1.0], [1040, 500, 1.2]]),
 # --- the call ---
 dict(id='29_ring', type='desk', start=100.3, end=103.7, inT='black', inDur=0.4, clock=N, vibAt=[100.6, 102.0, 103.3], cam=[[960, 560, 1.0], [960, 520, 1.25]], screen={'kind': 'incoming'}),
 dict(id='30_answer', type='held', start=103.7, end=107.5, clock=N, jolt=103.9, cam=[[960, 500, 1.3], [960, 470, 1.5]], screen=[{'kind': 'incoming'}, {'from': 103.9, 'kind': 'active', 'since': 103.9}]),
 dict(id='31_voice', type='held', start=107.5, end=110.1, clock=N, hand=2, cam=[[960, 560, 1.6], [960, 630, 1.95]], screen={'kind': 'active', 'since': 103.9, 'voice': [[110.22, 116.16]]}),
 dict(id='32_belongs', type='window', start=110.1, end=113.3, red=110.3, phone=1, cam=[[1000, 520, 1.1], [1040, 480, 1.3]]),
 dict(id='33_24h', type='title', style='countdown', start=113.3, end=115.3, at=113.3),
 dict(id='34_hangup', type='held', start=115.3, end=117.5, clock=N, cam=[[960, 520, 1.3], [960, 520, 1.4]], fadeOut=[116.6, 117.5], screen={'kind': 'ended'}),
 # --- going to the police ---
 dict(id='35_evidence', type='monitor', start=117.5, end=121.0, inT='fade', inDur=0.4, cam=[[800, 540, 1.15], [960, 540, 1.3]], monitor={'kind': 'docs', 'from': 119.6}),
 dict(id='36_police', type='desk', start=121.0, end=124.3, clock=N, cam=[[960, 560, 1.1], [960, 480, 1.4]], screen={'kind': 'call'}),
 dict(id='37_last', type='room', start=124.3, end=127.9, inT='fade', inDur=0.4, cam=[[960, 540, 1.0], [880, 620, 1.3]], monitor={'kind': 'docs'}, phoneOnAt=126.6, vibAt=126.6),
 dict(id='38_keep', type='desk', start=127.9, end=131.9, clock=N, vibAt=127.9, dark=0.75, cam=[[960, 560, 1.0], [960, 450, 1.7]], onAt=127.9,
      screen={'kind': 'lock', 'flash': 128.1, 'notifs': [{'at': 128.1, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': 'm_keep2', 'big': True, 'red': True}]}),
 dict(id='39_look', type='window', start=131.9, end=133.6, inT='fade', inDur=0.4, cam=[[980, 520, 1.05], [1020, 520, 1.15]]),
 dict(id='40_ten', type='desk', start=133.6, end=136.1, inT='fade', inDur=0.3, clock=N, cam=[[960, 420, 1.5], [960, 400, 1.7]], screen={'kind': 'wallet', 'pulse': 1}),
 dict(id='41_life', type='room', start=136.1, end=140.1, inT='fade', inDur=0.4, red=True, monitor={'kind': 'docs'}, phoneOn=0.9, dim=0.2, cam=[[1100, 560, 1.25], [1160, 540, 1.5]]),
 # --- the choice ---
 dict(id='42_two', type='split', start=140.1, end=143.2, inT='fade', inDur=0.4, clock=N),
 dict(id='43_optA', type='option', side='A', start=143.2, end=148.1, inT='flash', inDur=0.25, clock=N, at=143.36, millionAt=147.26, cam=[[980, 540, 1.0], [1010, 540, 1.08]]),
 dict(id='44_risk', type='monitor', start=148.1, end=153.6, inT='fade', inDur=0.4, cam=[[560, 560, 1.25], [1260, 470, 1.45]], redAt=150.48, monitor={'kind': 'warning', 'docs': 148.3, 'warn': 150.48, 'prog': [150.6, 153.5]}),
 dict(id='45_optB', type='option', side='B', start=153.6, end=160.2, inT='flash', inDur=0.25, clock=N, at=153.82, callingAt=155.5, strikeAt=158.08, cam=[[940, 540, 1.0], [910, 540, 1.08]]),
 dict(id='46_your_place', type='room', start=160.2, end=164.0, inT='black', inDur=0.5, monitor={'kind': 'warning'}, red=True, monLight=0.6, phoneOn=0.9, tilt=-0.1, dim=0.25, cam=[[1100, 560, 1.25], [1160, 540, 1.6]]),
 dict(id='47_final', type='final', start=164.0, end=178.7, inT='black', inDur=0.3, clock=N, q=164.24, a=165.76, b=168.16, c=171.82, d=175.4, d2=176.6, freeze=174.8),
 dict(id='48_part2', type='part2', start=178.7, end=184.1, inT='black', inDur=0.6),
]
for s in shots:
    if 'inT' in s: s['in'] = s.pop('inT')

events = [
 {'t': -0.5, 'type': 'roomtone', 'until': 183.7},
 {'t': 2.9, 'type': 'vibrate', 'n': 2}, {'t': 4.28, 'type': 'hit', 'gain': -4}, {'t': 4.3, 'type': 'ping'},
 {'t': 6.66, 'type': 'shimmer'}, {'t': 8.18, 'type': 'tick'}, {'t': 8.94, 'type': 'tick'}, {'t': 10.32, 'type': 'tick'},
 {'t': 12.4, 'type': 'whoosh', 'gain': -8}, {'t': 15.3, 'type': 'whoosh', 'gain': -4}, {'t': 15.48, 'type': 'hit', 'gain': -2},
 {'t': 19.9, 'type': 'whoosh', 'gain': -6}, {'t': 20.25, 'type': 'rewind'},
 {'t': 26.38, 'type': 'vibrate', 'n': 1}, {'t': 26.45, 'type': 'ping'}, {'t': 28.4, 'type': 'click'},
 {'t': 34.5, 'type': 'click'}, {'t': 36.38, 'type': 'hit', 'gain': -8},
 {'t': 42.68, 'type': 'refresh'}, {'t': 43.45, 'type': 'refresh'}, {'t': 44.5, 'type': 'click'}, {'t': 46.3, 'type': 'ui'},
 {'t': 54.5, 'type': 'keyboard', 'dur': 2.2}, {'t': 56.18, 'type': 'ui'}, {'t': 58.0, 'type': 'refresh'},
 {'t': 60.9, 'type': 'ui'}, {'t': 68.86, 'type': 'alarm'}, {'t': 68.86, 'type': 'hit', 'gain': -6},
 {'t': 73.3, 'type': 'hit', 'gain': -2}, {'t': 74.84, 'type': 'ui'}, {'t': 77.8, 'type': 'click'},
 {'t': 79.3, 'type': 'vibrate', 'n': 3}, {'t': 80.9, 'type': 'ping'}, {'t': 84.06, 'type': 'ping'},
 {'t': 92.6, 'type': 'vibrate', 'n': 2}, {'t': 92.9, 'type': 'ping'}, {'t': 94.3, 'type': 'hit', 'gain': -2},
 {'t': 100.5, 'type': 'ringtone', 'dur': 3.4}, {'t': 100.6, 'type': 'vibrate', 'n': 5}, {'t': 103.9, 'type': 'click'},
 {'t': 113.3, 'type': 'hit', 'gain': 0}, {'t': 113.3, 'type': 'clock', 'dur': 2.0}, {'t': 116.16, 'type': 'hangup'},
 {'t': 118.2, 'type': 'keyboard', 'dur': 2.6}, {'t': 119.84, 'type': 'click'}, {'t': 122.0, 'type': 'ui'},
 {'t': 126.6, 'type': 'vibrate', 'n': 2}, {'t': 128.1, 'type': 'hit', 'gain': -3}, {'t': 128.15, 'type': 'ping'},
 {'t': 134.3, 'type': 'shimmer'}, {'t': 140.1, 'type': 'whoosh', 'gain': -8},
 {'t': 143.36, 'type': 'hit', 'gain': -4}, {'t': 147.26, 'type': 'shimmer'}, {'t': 150.48, 'type': 'alarm'},
 {'t': 153.82, 'type': 'hit', 'gain': -4}, {'t': 155.5, 'type': 'ringback', 'dur': 4.6}, {'t': 158.08, 'type': 'ui'},
 {'t': 164.24, 'type': 'hit', 'gain': -2}, {'t': 165.76, 'type': 'tick'}, {'t': 168.16, 'type': 'tick'}, {'t': 171.82, 'type': 'tick'},
 {'t': 178.7, 'type': 'hit', 'gain': -3},
]
music = [(0, 0.3), (4.3, 0.55), (7.3, 0.7), (12.4, 0.3), (14.6, 0.8), (20.2, 0.3), (22.4, 0.25), (36.0, 0.45), (48.6, 0.6),
         (53.9, 0.55), (65.3, 0.8), (73.0, 0.9), (76.6, 0.4), (78.5, 0.6), (90.7, 0.75), (95.6, 0.0), (96.6, 0.0), (97.2, 0.65),
         (100.3, 0.6), (103.8, 0.0), (110.0, 0.0), (110.3, 0.6), (113.3, 0.9), (116.2, 0.4), (124.3, 0.6), (127.8, 0.1),
         (128.1, 0.8), (140.1, 0.6), (143.2, 0.8), (160.2, 0.5), (164.0, 0.4), (172.0, 0.2), (175.4, 0.0), (178.7, 0.0), (178.8, 0.35), (183.0, 0.0)]
chords = [(-0.5, 12.9, [38, 45, 53]), (12.3, 20.6, [38, 46, 52, 57]), (20.2, 36.6, [38, 45, 52, 53]), (36.0, 53.9, [34, 41, 50, 53]),
          (53.5, 78.9, [38, 46, 52, 57]), (78.3, 100.7, [31, 38, 46, 50]), (100.0, 124.7, [33, 40, 49, 52]), (124.0, 143.6, [38, 46, 52, 57]),
          (143.0, 153.9, [34, 41, 50, 53]), (153.4, 164.4, [31, 38, 46, 50]), (163.8, 179.0, [38, 45, 50, 53]), (178.6, 184.0, [33, 40, 45, 52])]
heart = [(14.6, 20.2, 70), (65.3, 78.3, 72), (90.7, 95.6, 80), (100.3, 117.3, 84), (124.3, 140.0, 70), (160.2, 175.0, 60)]

tl = {
  '_comment': 'Монтажные настройки полной RU-версии. Генерируется tools/make_timeline_ru.py (времена там — по озвучке, здесь — по видео: +voiceOffset).',
  'fps': 30, 'width': 1920, 'height': 1080, 'duration': 184.6,
  'voice': 'assets/audio/voice_ru.mp3', 'voiceOffset': OFF, 'strings': 'config/strings.ru.json',
  'shots': shift(shots),
  'cues': shift({'silence_start': 95.6, 'keep_msg': 97.2, 'camera_freeze': 182.7, 'hard_black': 183.7}),
  'audio': {'voiceGainDb': 0, 'musicGainDb': -13,
            'events': shift(events), 'music': [{'t': round(t + OFF, 3), 'level': l} for t, l in music],
            'chords': [[round(a + OFF, 3), round(b + OFF, 3), n] for a, b, n in chords],
            'heart': [[round(a + OFF, 3), round(b + OFF, 3), bpm] for a, b, bpm in heart],
            'eerie': [[78.5 + OFF, 22.0], [124.3 + OFF, 16.0]]},
}
tl['shots'][0]['start'] = 0.0
json.dump(tl, open(os.path.join(ROOT, 'config', 'timeline.ru.json'), 'w'), ensure_ascii=False, indent=1)
# sanity: shots are contiguous
for a, b in zip(tl['shots'], tl['shots'][1:]):
    assert abs(a['end'] - b['start']) < 1e-6, (a['id'], b['id'])
print('shots', len(shots), 'duration', tl['duration'])
