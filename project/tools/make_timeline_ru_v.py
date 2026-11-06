"""Builds config/timeline.ru_v.json: vertical 9:16 Shorts version (flat style), <= 3:00.
Times are written in VOICE time (config/transcript_ru.json) and shifted by OFF.
Audio events/music are reused from timeline.ru.json (shifted to the new offset)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFF = 0.3
TIME_KEYS = {'start', 'end', 'at', 'to', 'onAt', 'offAt', 'phoneOnAt', 'phoneOffAt', 'phoneAt', 'handAt', 'vibAt', 'from', 'since', 'count',
             'txRed', 'dimAt', 'refresh', 'stolen', 'scroll', 'calling', 'voice', 'typing', 'missed', 'reveal', 'focus', 'docs', 'warn',
             'prog', 'redRow', 'redAt', 'darkAt', 'millionAt', 'strikeAt', 'callingAt', 'q', 'a', 'b', 'c', 'sub', 'part2', 'jolt', 'flash',
             'fadeOut', 'redFlash', 'stampAt', 'faceAt', 'question', 'carAt', 'homeAt', 'freeAt', 'crossAt', 'answerAt', 'eyes', 'red', 't'}
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
shots = [
 dict(id='01', type='f_room', start=-0.3, end=3.4, inT='black', inDur=0.5, morning=True, clock=M, cam=[[540, 960, 1.0], [600, 1000, 1.18]], phoneOnAt=2.9, vibAt=2.9, exprAt=[3.0, 'shock'], tag=tag('ОДНАЖДЫ УТРОМ')),
 dict(id='02', type='f_phone', start=3.4, end=5.9, clock=M, cam=[[540, 700, 1.25], [540, 660, 1.4]], screen={'kind': 'wallet', 'count': 4.28}, face='neutral', faceAt=4.3, faceSeq=[[4.6, 'shock']], tag=tag('+10 BTC', G, 4.4)),
 dict(id='03', type='f_face', start=5.9, end=7.3, clock=M, expr='rich', coins=True, cam=[[540, 960, 1.0], [540, 920, 1.1]], tag=tag('≈ $1 000 000', G)),
 dict(id='04', type='f_dream', start=7.3, end=12.5, cam=CAM0, carAt=8.18, homeAt=8.94, freeAt=10.32, tag=tag('МЕЧТЫ', B)),
 dict(id='05', type='f_face', start=12.5, end=14.6, inT='flash', inDur=0.2, expr='worry', red=12.68, question=13.62, cam=[[540, 960, 1.0], [540, 940, 1.12]], tag=tag('ОДНА ПРОБЛЕМА', R, 13.62)),
 dict(id='06', type='f_phone', start=14.6, end=16.9, clock='clock_night', cam=[[540, 780, 1.0], [540, 700, 1.1]], snap={'at': 15.48, 'to': [540, 600, 1.5]}, stampAt=15.48, redFlash=15.48, red=15.48, screen={'kind': 'news'}, tag=tag('ЭТИ БИТКОИНЫ УКРАДЕНЫ', R, 15.48, -0.03)),
 dict(id='07', type='f_window', start=16.9, end=20.2, inT='fade', inDur=0.3, eyes=17.6, red=17.6, cam=[[540, 960, 1.0], [540, 900, 1.12]], tag=tag('КТО-ТО ЗНАЕТ', R, 17.6)),
 dict(id='08', type='f_rewind', start=20.2, end=22.4, inT='flash', inDur=0.2, tag=tag('ВСЁ НАЧАЛОСЬ РАНЬШЕ', Y), dots=True),
 dict(id='09', type='f_room', start=22.4, end=25.7, inT='black', inDur=0.4, morning=True, clock=M, cam=[[540, 960, 1.05], [520, 1000, 1.15]], handAt=24.82, phoneOn=0.8, tag=tag('ОБЫЧНОЕ УТРО', B)),
 dict(id='10', type='f_phone', start=25.7, end=31.0, clock=M, cam=[[25.7, 540, 700, 1.15], [28.3, 540, 680, 1.25], [28.5, 540, 600, 1.15], [31.0, 540, 580, 1.25]], face='neutral', faceAt=26.6, faceSeq=[[28.6, 'skeptic']],
      screen=[{'kind': 'lock', 'notifs': [{'at': 26.38, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': 'm_lucky', 'big': True}]}, {'from': 28.4, 'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 28.5}]}],
      tag=tag('НЕИЗВЕСТНЫЙ ОТПРАВИТЕЛЬ', R, 26.4)),
 dict(id='11', type='f_face', start=31.0, end=33.7, clock=M, expr='skeptic', lookX=0.6, cam=[[540, 960, 1.05], [540, 960, 1.0]], tag=tag('СПАМ?', B)),
 dict(id='12', type='f_phone', start=33.7, end=37.3, clock=M, cam=[[33.7, 540, 780, 1.0], [36.4, 540, 600, 1.45], [37.3, 540, 598, 1.46]], face='neutral', faceAt=34.2, faceSeq=[[36.38, 'shock']],
      screen=[{'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}]}, {'from': 34.5, 'kind': 'splash'}, {'from': 35.3, 'kind': 'wallet', 'count': 35.4}]),
 dict(id='13', type='f_face', start=37.3, end=40.3, clock=M, expr='shock', sweat=True, cam=[[540, 960, 1.1], [540, 900, 1.3]], tag=tag('10 BTC НА БАЛАНСЕ', Y)),
 dict(id='14', type='f_phone', start=40.3, end=44.3, clock=M, cam=[[540, 780, 1.0], [540, 640, 1.3]], face='worry', faceAt=40.5, screen={'kind': 'wallet', 'refresh': [42.68, 43.45]}, tag=tag('ПРОВЕРЯЕШЬ ЕЩЁ РАЗ', B, 42.6)),
 dict(id='15', type='f_phone', start=44.3, end=48.6, clock=M, cam=[[540, 760, 1.05], [540, 640, 1.3]], face='worry', faceSeq=[[46.4, 'shock']],
      screen=[{'kind': 'wallet'}, {'from': 44.5, 'kind': 'off'}, {'from': 44.9, 'kind': 'splash'}, {'from': 46.3, 'kind': 'wallet', 'pulse': 1}], tag=tag('ПЕРЕЗАПУСК', B, 44.5)),
 dict(id='16', type='f_face', start=48.6, end=53.9, inT='fade', inDur=0.3, clock=M, expr='happy', exprSeq=[[49.9, 'rich']], coins=True, cam=[[540, 960, 1.0], [540, 920, 1.12]], tag=tag('ТЫ РАЗБОГАТЕЛ?', G, 49.6)),
 dict(id='17', type='f_monitor', start=53.9, end=57.1, inT='fade', inDur=0.3, clock=M, cam=[[480, 820, 1.05], [600, 800, 1.2]], monitor={'kind': 'desktop', 'redRow': 56.18}, tag=tag('ОТКУДА ПЕРЕВОД?', Y)),
 dict(id='18', type='f_phone', start=57.1, end=60.7, clock=M, cam=[[540, 780, 1.05], [540, 700, 1.2]], face='neutral', faceSeq=[[59.0, 'shock']], screen={'kind': 'news', 'scroll': [58.0, 60.5], 'scrollBy': 160}, tag=tag('НОВОСТЬ', R, 59.0)),
 dict(id='19', type='f_graph', start=60.7, end=65.3, cam=[[540, 1100, 1.0], [540, 1000, 1.05]], reveal=[60.9, 64.0], tag=tag('НЕСКОЛЬКО ДНЕЙ НАЗАД', B)),
 dict(id='20', type='f_graph', start=65.3, end=71.9, cam=[[65.3, 540, 1000, 1.05], [68.8, 760, 740, 1.4], [71.9, 860, 600, 1.7]], focus=68.86, crossAt=66.4, tag=tag('АДРЕС СОВПАДАЕТ', R, 68.86)),
 dict(id='21', type='f_face', start=71.9, end=74.4, expr='scared', red=True, sweat=True, cam=[[540, 960, 1.1], [540, 900, 1.25]], darkAt=73.2, caption={'at': 73.4, 'text': 'ЭТО НЕ ПОДАРОК'}),
 dict(id='22', type='f_phone', start=74.4, end=76.6, inT='black', inDur=0.3, clock=M, cam=[[540, 1000, 1.6], [540, 990, 1.7]], face='worry', screen={'kind': 'wallet', 'txRed': 74.84}, tag=tag('КТО-ТО ИСПОЛЬЗОВАЛ КОШЕЛЁК', R, 74.6)),
 dict(id='23', type='f_room', start=76.6, end=78.5, cam=[[540, 960, 1.15], [560, 980, 1.1]], phoneOn=1, phoneOffAt=77.8, expr='determined', tag=tag('НИЧЕГО НЕ ТРОГАТЬ', B)),
 dict(id='24', type='f_room', start=78.5, end=80.7, cam=[[540, 960, 1.0], [620, 1020, 1.25]], vibAt=79.3, phoneOnAt=79.3, exprAt=[79.6, 'shock'], tag=tag('ВИБРАЦИЯ', R, 79.3)),
 dict(id='25', type='f_phone', start=80.7, end=85.3, clock=M, cam=[[540, 700, 1.1], [540, 760, 1.25]], face='worry', sweat=True,
      screen={'kind': 'chat', 'msgs': [{'key': 'm_lucky', 'at': 0}, {'key': 'm_dont', 'at': 80.9, 'red': True}, {'key': 'm_keep_short', 'at': 84.06, 'red': True}], 'typing': [82.7, 84.0]}, tag=tag('НОВОЕ СООБЩЕНИЕ', R, 80.8)),
 dict(id='26', type='f_face', start=85.3, end=90.7, inT='fade', inDur=0.3, expr='scared', sweat=True, shake=6, question=87.46, cam=[[540, 960, 1.0], [540, 920, 1.15]], tag=tag('ОТКУДА ОН ЗНАЕТ?', R, 87.4)),
 dict(id='27', type='f_phone', start=90.7, end=96.3, clock=M, vibAt=92.6, cam=[[90.7, 540, 800, 1.0], [94.3, 540, 640, 1.35], [94.5, 540, 600, 1.6], [96.3, 540, 600, 1.65]], onAt=92.6, red=94.3,
      screen={'kind': 'lock', 'flash': 92.9, 'notifs': [{'at': 92.9, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': 'm_know', 'big': True, 'red': True}]}, tag=tag('МЫ ЗНАЕМ, КТО ТЫ', R, 94.3, -0.04)),
 dict(id='28', type='f_window', start=96.3, end=100.3, inT='fade', inDur=0.4, eyes=96.5, red=96.5, cam=[[540, 960, 1.0], [540, 880, 1.15]], tag=tag('ВСЁ СЕРЬЁЗНЕЕ', R)),
 dict(id='29', type='f_phone', start=100.3, end=103.7, inT='black', inDur=0.3, clock=N, vibAt=[100.6, 102.0, 103.3], cam=[[540, 800, 1.0], [540, 740, 1.15]], face='scared', faceAt=101.0, screen={'kind': 'incoming'}, tag=tag('СКРЫТЫЙ НОМЕР', R)),
 dict(id='30', type='f_call', start=103.7, end=113.3, clock=N, jolt=103.9, answerAt=103.9, cam=[[103.7, 540, 960, 1.0], [110.0, 520, 900, 1.12], [113.3, 500, 860, 1.25]], voice=[[110.22, 116.16]],
      bubbles=[{'at': 105.2, 'to': 107.4, 'text': '…'}, {'at': 110.22, 'to': 113.3, 'text': 'У тебя есть то, что нам принадлежит.', 'red': True}],
      tag=tag('ТИШИНА', B, 105.2)),
 dict(id='31', type='f_big', start=113.3, end=115.3, inT='flash', inDur=0.2, clock='countdown_clock', sym='24', col='red', label='ЧАСА', box='У ТЕБЯ 24 ЧАСА', ill='countdown', at=113.3),
 dict(id='32', type='f_phone', start=115.3, end=117.5, clock=N, cam=[[540, 760, 1.1], [540, 760, 1.15]], face='scared', screen={'kind': 'ended'}, fadeOut=[116.8, 117.5], tag=tag('ЗВОНОК ОБРЫВАЕТСЯ', R)),
 dict(id='33', type='f_monitor', start=117.5, end=121.0, inT='fade', inDur=0.3, clock=N, cam=[[540, 900, 1.05], [540, 820, 1.2]], monitor={'kind': 'docs', 'from': 119.6}, tag=tag('СОХРАНЯЕШЬ ПЕРЕПИСКУ', B, 119.6)),
 dict(id='34', type='f_phone', start=121.0, end=124.3, clock=N, cam=[[540, 800, 1.0], [540, 720, 1.2]], face='determined', screen={'kind': 'call'}, tag=tag('ПОЛИЦИЯ', B, 123.3)),
 dict(id='35', type='f_room', start=124.3, end=127.9, inT='fade', inDur=0.3, red=True, cam=[[540, 960, 1.0], [600, 1020, 1.2]], phoneOnAt=126.6, vibAt=126.6, exprAt=[126.8, 'shock'], monitor={'kind': 'docs'}, tag=tag('ПОСЛЕДНЕЕ СООБЩЕНИЕ', R, 125.9)),
 dict(id='36', type='f_phone', start=127.9, end=131.9, clock=N, vibAt=127.9, onAt=127.9, red=128.1, cam=[[540, 820, 1.0], [540, 620, 1.5]],
      screen={'kind': 'lock', 'flash': 128.1, 'notifs': [{'at': 128.1, 'kind': 'msg', 'app': 'msg_app', 'title': 'unknown', 'body': 'm_keep2', 'big': True, 'red': True}]}),
 dict(id='37', type='f_face', start=131.9, end=133.6, inT='fade', inDur=0.3, expr='worry', phoneLight=0.8, lookY=0.8, cam=[[540, 960, 1.15], [540, 960, 1.25]]),
 dict(id='38', type='f_phone', start=133.6, end=136.1, clock=N, cam=[[540, 680, 1.3], [540, 660, 1.45]], screen={'kind': 'wallet', 'pulse': 1}, tag=tag('10 BTC', Y)),
 dict(id='39', type='f_face', start=136.1, end=140.1, inT='fade', inDur=0.3, expr='rich', coins=True, cam=[[540, 960, 1.0], [540, 920, 1.1]], tag=tag('ВСЯ ЖИЗНЬ ИЗМЕНИТСЯ', G)),
 dict(id='40', type='f_split', start=140.1, end=143.2, inT='flash', inDur=0.2, dots=True, tag=tag('ДВА ВАРИАНТА', Y)),
 dict(id='41', type='f_big', start=143.2, end=148.1, inT='flash', inDur=0.2, sym='A', col='yellow', label='ВАРИАНТ', box='ОСТАВИТЬ ДЕНЬГИ СЕБЕ', ill='wallet', at=143.36, millionAt=147.26),
 dict(id='42', type='f_monitor', start=148.1, end=153.6, inT='fade', inDur=0.3, cam=[[480, 820, 1.05], [620, 800, 1.2]], redAt=150.48, monitor={'kind': 'warning', 'docs': 148.3, 'warn': 150.48, 'prog': [150.6, 153.5]}, tag=tag('ПРИДЁТСЯ ЖИТЬ С РИСКОМ', R, 148.6)),
 dict(id='43', type='f_big', start=153.6, end=160.2, inT='flash', inDur=0.2, sym='B', col='red', label='ВАРИАНТ', box='ПОЗВОНИТЬ В ПОЛИЦИЮ', ill='call', at=153.82, callingAt=155.5, strikeAt=158.08),
 dict(id='44', type='f_face', start=160.2, end=164.0, inT='black', inDur=0.3, expr='determined', cam=[[540, 960, 1.0], [540, 900, 1.2]], tag=tag('ТЫ НА МОЁМ МЕСТЕ', Y)),
 dict(id='45', type='f_final', start=164.0, end=179.3, inT='black', inDur=0.3, subs=False, q=164.24, a=165.76, b=168.16, c=171.82, part2=173.98, sub=175.6),
]
for s in shots:
    if 'inT' in s: s['in'] = s.pop('inT')

full = json.load(open(os.path.join(ROOT, 'config', 'timeline.ru.json')))
D = OFF - full['voiceOffset']
A = full['audio']
ev = [dict(e, t=round(e['t'] + D, 3)) for e in A['events'] if e['t'] + D < 178.8]
for e in ev:
    if e['type'] == 'roomtone': e['until'] = 179.4; e['t'] = 0.0
music = [{'t': round(m['t'] + D, 3), 'level': m['level']} for m in A['music'] if m['t'] + D < 174.0] + [{'t': 174.3, 'level': 0.35}, {'t': 178.5, 'level': 0.0}]
tl = {
  '_comment': 'Вертикальная (9:16) плоская версия для Shorts, <= 3:00. Генерируется tools/make_timeline_ru_v.py.',
  'fps': 30, 'width': 1080, 'height': 1920, 'duration': 179.6, 'flat': True,
  'voice': 'assets/audio/voice_ru.mp3', 'voiceOffset': OFF, 'strings': 'config/strings.ru.json', 'transcriptFile': 'config/transcript_ru.json',
  'overlay': {'stages': [{'t': 0.0, 'name': 'ПЕРЕВОД'}, {'t': 54.2, 'name': 'КРАЖА'}, {'t': 78.8, 'name': 'УГРОЗЫ'}, {'t': 140.4, 'name': 'ВЫБОР'}]},
  'shots': shift(shots),
  'cues': {'silence_start': 95.9, 'keep_msg': 97.5, 'camera_freeze': 178.4, 'hard_black': 179.4},
  'audio': {'voiceGainDb': 0, 'musicGainDb': A['musicGainDb'], 'events': ev, 'music': music,
            'chords': [[round(a + D, 3), min(round(b + D, 3), 179.5), n] for a, b, n in A['chords'] if a + D < 179],
            'heart': [[round(a + D, 3), round(b + D, 3), bpm] for a, b, bpm in A['heart']],
            'eerie': [[round(a + D, 3), d] for a, d in A['eerie']]},
}
tl['shots'][0]['start'] = 0.0
tl['shots'][-1]['end'] = tl['duration']
for a, b in zip(tl['shots'], tl['shots'][1:]): assert abs(a['end'] - b['start']) < 1e-6, (a['id'], b['id'])
json.dump(tl, open(os.path.join(ROOT, 'config', 'timeline.ru_v.json'), 'w'), ensure_ascii=False, indent=1)
print('shots', len(shots), 'duration', tl['duration'])
