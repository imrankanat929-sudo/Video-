"""EP01 part 2 — "You chose the police". Vertical flat Shorts, RU + EN.
Every time is L(ru, en) in VOICE time, shifted by OFF on build.
usage: python3 tools/make_timeline_btc2.py -> config/timeline.btc2_ru_v.json, config/timeline.btc2_en_v.json"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFF = 0.3
class L(tuple):
    def __new__(cls, ru, en): return tuple.__new__(cls, (ru, en))
class T2(tuple):
    def __new__(cls, ru, en): return tuple.__new__(cls, (ru, en))
def pick(o, i):
    if isinstance(o, L): return round(o[i] + OFF, 3)
    if isinstance(o, T2): return o[i]
    if isinstance(o, dict): return {k: pick(v, i) for k, v in o.items()}
    if isinstance(o, list): return [pick(v, i) for v in o]
    return o
Y, R, B, G = 'yellow', 'red', 'blue', 'green'
def tag(ru, en, color=Y, at=None, rot=0):
    d = {'text': T2(ru, en), 'color': color, 'rot': rot}
    if at is not None: d['at'] = at
    return d
def c2(a, b): return [list(a), list(b)]
N, M = 'evening_clock', 'clock_morning2'
UNK = T2('Неизвестный', 'Unknown')
S = []
def shot(id_, type_, start, **kw): S.append(dict(id=id_, type=type_, start=start, **kw))

shot('01', 'f_phone', L(-0.3, -0.3), inT='black', inDur=0.4, clock=N, screen={'kind': 'call', 'calling': L(0.3, 0.3)}, face='determined', faceAt=L(1.0, 1.0), cam=c2((540, 760, 1.05), (540, 680, 1.25)), tag=tag('ТЫ ВЫБРАЛ ПОЛИЦИЮ', 'YOU CHOSE THE POLICE', B, L(0.98, 0.94)))
shot('02', 'f_room', L(4.7, 3.6), clock=N, red=True, phoneOn=1, monitor={'kind': 'docs'}, expr='worry', cam=c2((540, 960, 1.0), (620, 1020, 1.2)), dim=0.15, tag=tag('ЧТО БЫЛО ДАЛЬШЕ?', 'WHAT HAPPENED NEXT?', Y, L(6.2, 5.5)))
shot('03', 'f_call', L(7.9, 7.6), inT='flash', inDur=0.2, clock=N, answerAt=L(7.9, 7.6), voice=[], cam=c2((540, 960, 1.0), (520, 900, 1.12)), tag=tag('ЗВОНОК В ПОЛИЦИЮ', 'CALLING THE POLICE', B, L(10.08, 9.1)))
shot('04', 'f_monitor', L(13.9, 12.5), clock=N, monitor={'kind': 'docs', 'from': L(14.3, 13.0)}, cam=c2((540, 900, 1.05), (540, 820, 1.2)), tag=tag('ДОКАЗАТЕЛЬСТВА', 'EVIDENCE', B, L(15.36, 14.16)))
shot('05', 'f_face', L(20.4, 18.6), expr='skeptic', exprSeq=[[L(25.38, 23.24), 'determined']], question=L(21.52, 19.98), cam=c2((540, 960, 1.0), (540, 930, 1.12)), tag=tag('СНАЧАЛА НЕ ПОВЕРИЛИ', 'THEY WERE SUSPICIOUS', R, L(21.52, 19.98)))
shot('06', 'f_phone', L(26.4, 24.3), clock=N, screen={'kind': 'wallet'}, face='neutral', cam=c2((540, 700, 1.15), (540, 640, 1.3)), tag=tag('НЕ ТРОГАТЬ КРИПТОВАЛЮТУ', "DON'T TOUCH THE CRYPTO", B, L(27.56, 25.02)))
shot('07', 'f_phone', L(31.1, 28.9), clock=N, vibAt=L(31.4, 29.2), screen={'kind': 'incoming', 'title': T2('Следователь', 'Investigator')}, face='neutral', faceAt=L(31.6, 29.4), cam=c2((540, 800, 1.0), (540, 740, 1.15)), tag=tag('СЛЕДОВАТЕЛЬ', 'INVESTIGATOR', B, L(33.0, 30.2)))
shot('08', 'f_call', L(36.6, 33.9), clock=N, answerAt=L(30.0, 30.0), voice=[[L(36.8, 32.1), L(42.0, 37.0)]], cam=c2((540, 960, 1.0), (500, 880, 1.15)),
     bubbles=[{'at': L(37.82, 33.02), 'to': L(42.9, 37.9), 'text': T2('10 BTC — лишь часть украденного.', '10 BTC is only part of the theft.')}], tag=tag('НЕОЖИДАННО', 'UNEXPECTED', Y, L(37.82, 33.02)))
shot('09', 'f_graph', L(42.9, 37.9), reveal=[L(43.0, 38.0), L(46.0, 40.2)], focus=L(48.66, 42.52), crossAt=L(45.6, 39.9), cam=[[L(42.9, 37.9), 540, 1060, 1.0], [L(48.4, 42.3), 640, 900, 1.15], [L(50.9, 44.2), 840, 620, 1.6]], tag=tag('ЦЕПОЧКА КОШЕЛЬКОВ', 'A CHAIN OF WALLETS', B, L(44.38, 39.26)))
shot('10', 'f_monitor', L(50.9, 44.2), monitor={'kind': 'graph', 'focus': L(0, 0)}, redAt=L(50.9, 44.2), cam=c2((560, 860, 1.1), (600, 820, 1.25)), tag=tag('ПОЧЕМУ ИМЕННО ТЫ?', 'WHY YOU?', R, L(51.58, 44.76)))
shot('11', 'f_phone', L(54.9, 48.1), clock=M, cam=c2((540, 720, 1.1), (540, 640, 1.35)), face='neutral',
     screen=[{'kind': 'lock', 'flash': L(56.4, 49.4), 'notifs': [{'at': L(56.4, 49.4), 'kind': 'btc', 'app': T2('УВЕДОМЛЕНИЕ', 'NOTICE'), 'title': T2('Транзакция на проверке', 'Transaction under review'), 'body': T2('Доступ к средствам временно ограничен', 'Access to funds temporarily restricted'), 'big': True}]},
             {'from': L(60.4, 53.4), 'kind': 'wallet', 'dimAt': L(61.6, 54.8)}], tag=tag('ДОСТУП ОГРАНИЧЕН', 'ACCESS RESTRICTED', R, L(62.46, 55.34)))
shot('12', 'f_face', L(63.6, 56.5), expr='happy', cam=c2((540, 960, 1.0), (540, 940, 1.1)), tag=tag('ОБЛЕГЧЕНИЕ', 'RELIEF', G, L(64.66, 57.66)))
shot('13', 'f_room', L(69.6, 61.8), inT='fade', inDur=0.3, clock=N, cam=c2((540, 960, 1.0), (620, 1020, 1.25)), vibAt=L(72.6, 65.1), phoneOnAt=L(72.6, 65.1), exprAt=[L(72.9, 65.4), 'shock'], tag=tag('ЧТО-ТО СТРАННОЕ', 'SOMETHING STRANGE', R, L(71.38, 63.42)))
shot('14', 'f_phone', L(74.9, 66.9), clock=N, red=L(75.92, 67.2), face='scared', sweat=True, shotAt=L(81.08, 71.94), cam=c2((540, 720, 1.15), (540, 700, 1.3)),
     screen={'kind': 'chat', 'msgs': [{'key': 'm_know', 'at': 0, 'red': True}, {'key': T2('Ты совершил ошибку.', 'You made a mistake.'), 'at': L(75.92, 67.2), 'red': True}]},
     tag=tag('СКРИНШОТ СОХРАНЁН', 'SCREENSHOT SAVED', G, L(81.08, 71.94)))
shot('15', 'f_rewind', L(83.5, 74.4), forward=True, tag=tag('ПРОШЛО НЕСКОЛЬКО ЧАСОВ', 'HOURS LATER', Y))
shot('16', 'f_phone', L(86.5, 77.1), clock=N, vibAt=[L(86.82, 77.38), L(88.3, 78.6), L(89.8, 80.0)], screen={'kind': 'incoming'}, face='scared', faceAt=L(87.0, 77.6), cam=c2((540, 800, 1.0), (540, 740, 1.15)), tag=tag('ТОТ САМЫЙ ГОЛОС', 'THE SAME MAN', R, L(88.5, 78.78)))
shot('17', 'f_call', L(91.4, 80.7), clock=N, answerAt=L(85.0, 75.0), jolt=L(91.5, 80.8), voice=[[L(92.76, 81.86), L(95.0, 83.9)]], cam=c2((540, 960, 1.0), (520, 880, 1.18)),
     bubbles=[{'at': L(92.76, 81.86), 'to': L(96.4, 84.9), 'text': T2('Ты думаешь, полиция сможет тебя защитить?', 'Do you really think the police can protect you?'), 'red': True}], tag=tag('УГРОЗА', 'A THREAT', R, L(92.76, 81.86)))
shot('18', 'f_phone', L(96.4, 84.9), clock=N, screen={'kind': 'ended'}, face='determined', cam=c2((540, 760, 1.1), (540, 740, 1.18)), tag=tag('БОЛЬШЕ НЕ ОТВЕЧАТЬ', 'NO MORE UNKNOWN CALLS', B, L(99.0, 86.8)))
shot('19', 'f_monitor', L(102.0, 89.6), inT='black', inDur=0.3, clock=M, monitor={'kind': 'mail', 'at': L(104.88, 91.32), 'openAt': L(108.0, 95.3), 'title': T2('Новый файл', 'New file'), 'from': T2('Отправитель: неизвестен', 'Sender: unknown')},
     cam=c2((540, 860, 1.05), (700, 760, 1.3)), tag=tag('НОВЫЙ ФАЙЛ', 'A NEW FILE', Y, L(107.42, 94.48)))
TABLE = {'kind': 'table', 'head': T2(['ДАТА', 'ОТКУДА', 'КУДА', 'СУММА'], ['DATE', 'FROM', 'TO', 'AMOUNT']), 'youAt': L(113.12, 100.22), 'amountAt': L(118.62, 105.22), 'lastAt': L(129.32, 116.58),
         'last': T2('→ СЛЕДУЮЩИЙ АДРЕС: АДРЕС СЛЕДОВАТЕЛЯ', "→ NEXT ADDRESS: THE INVESTIGATOR'S ADDRESS"), 'scroll': [L(109.0, 96.2), L(112.0, 99.0)]}
shot('20', 'f_monitor', L(108.4, 95.4), clock=M, monitor=TABLE, cam=[[L(108.4, 95.4), 540, 860, 1.05], [L(112.6, 99.8), 540, 860, 1.05], [L(116.2, 102.7), 700, 820, 1.35]], tag=tag('ТВОЙ АДРЕС', 'YOUR ADDRESS', Y, L(113.12, 100.22)))
shot('21', 'f_monitor', L(116.2, 102.7), clock=M, monitor=TABLE, redAt=L(118.62, 105.22), cam=c2((760, 890, 1.6), (800, 900, 1.85)), tag=tag('+20 BTC', '+20 BTC', R, L(118.62, 105.22)))
shot('22', 'f_face', L(120.2, 107.1), expr='shock', sweat=True, question=L(123.94, 111.26), cam=c2((540, 960, 1.05), (540, 920, 1.18)), tag=tag('ОТКУДА ЭТИ ДЕНЬГИ?', 'WHERE DID IT COME FROM?', R, L(123.94, 111.26)))
shot('23', 'f_monitor', L(126.2, 113.5), clock=M, monitor=TABLE, redAt=L(129.32, 116.58), cam=[[L(126.2, 113.5), 560, 900, 1.2], [L(129.2, 116.4), 420, 1010, 1.45], [L(132.8, 119.4), 390, 1040, 1.6]], tag=tag('АДРЕС СЛЕДОВАТЕЛЯ', "THE INVESTIGATOR'S ADDRESS", R, L(129.32, 116.58), -0.04))
shot('24', 'f_window', L(132.8, 119.4), inT='fade', inDur=0.3, red=L(133.0, 119.6), cam=c2((540, 960, 1.0), (540, 900, 1.12)), tag=tag('КТО-ТО ВМЕШИВАЕТСЯ', 'SOMEONE IS INTERFERING', R, L(137.42, 123.64)))
shot('25', 'f_face', L(139.4, 125.9), expr='worry', sweat=True, cam=c2((540, 960, 1.0), (540, 940, 1.1)), tag=tag('КОМУ ДОВЕРЯТЬ?', 'WHO CAN YOU TRUST?', Y, L(140.6, 126.86)))
shot('26', 'f_face', L(143.9, 128.9), expr='determined', cam=c2((540, 960, 1.05), (540, 920, 1.15)), tag=tag('СНОВА ВЫБОР', 'A CHOICE AGAIN', Y, L(145.26, 130.64)))
shot('27', 'f_big', L(146.2, 131.8), inT='flash', inDur=0.2, sym='A', col='yellow', label=T2('ВАРИАНТ', 'OPTION'), box=T2('ПОКАЗАТЬ ФАЙЛ ПОЛИЦИИ', 'SHOW THE FILE TO THE POLICE'), ill='file', at=L(146.32, 131.9))
shot('28', 'f_big', L(150.6, 135.9), inT='flash', inDur=0.2, sym='B', col='red', label=T2('ВАРИАНТ', 'OPTION'), box=T2('РАЗОБРАТЬСЯ САМОМУ', 'INVESTIGATE ALONE'), ill='search', at=L(150.74, 136.06))
shot('29', 'f_final', L(155.9, 141.0), inT='black', inDur=0.3, subs=False, q=L(156.12, 141.18), a=L(156.8, 141.8), b=L(157.6, 142.4), c=L(158.4, 143.0), part2=L(159.2, 143.8), sub=L(160.2, 144.8),
     qText=T2('КАКОЙ ВАРИАНТ ВЫБЕРЕШЬ?', 'WHAT WOULD YOU CHOOSE?'), q2Text=T2('ПОЛИЦИЯ ИЛИ САМ?', 'POLICE OR ALONE?'), aText=T2('ПОКАЗАТЬ ФАЙЛ ПОЛИЦИИ', 'SHOW THE FILE TO THE POLICE'), bText=T2('РАЗОБРАТЬСЯ САМОМУ', 'INVESTIGATE ALONE'),
     cText=T2('ПИШИ «A» ИЛИ «B» В КОММЕНТАРИЯХ', 'WRITE “A” OR “B” IN THE COMMENTS'), p2badge=T2('ЧАСТЬ 3 — УЖЕ СКОРО', 'PART 3 — COMING SOON'), p2l1=T2('ВАРИАНТ С БОЛЬШИНСТВОМ ГОЛОСОВ', 'THE OPTION WITH THE MOST VOTES'), p2l2=T2('ПОКАЖЕМ В 3 ЧАСТИ', 'WILL HAPPEN IN PART 3'))
END = L(164.4, 149.6)

def build(i):
    lang = ('ru', 'en')[i]
    shots = []
    for s in S:
        d = pick(dict(s), i)
        if 'inT' in d: d['in'] = d.pop('inT')
        shots.append(d)
    for a, b in zip(shots, shots[1:]): a['end'] = b['start']
    end = pick(END, i); shots[0]['start'] = 0.0; shots[-1]['end'] = end
    sh = {s['id']: s for s in shots}; st = lambda k: sh[k]['start']
    ev = [{'t': 0.0, 'type': 'roomtone', 'until': end - 1.0}, {'t': sh['01']['screen']['calling'], 'type': 'ringback', 'dur': st('02') - sh['01']['screen']['calling']},
          {'t': st('03'), 'type': 'whoosh', 'gain': -6}, {'t': st('04') + 0.3, 'type': 'keyboard', 'dur': 2.5}, {'t': sh['05']['question'], 'type': 'tick'},
          {'t': sh['07']['vibAt'], 'type': 'vibrate', 'n': 3}, {'t': st('07') + 0.2, 'type': 'ringtone', 'dur': 2.6}, {'t': sh['08']['bubbles'][0]['at'], 'type': 'ui'},
          {'t': sh['09']['reveal'][0], 'type': 'ui'}, {'t': sh['09']['focus'], 'type': 'alarm'}, {'t': sh['09']['focus'], 'type': 'hit', 'gain': -6},
          {'t': sh['11']['screen'][0]['notifs'][0]['at'], 'type': 'ping'}, {'t': sh['11']['tag']['at'], 'type': 'hit', 'gain': -8}, {'t': sh['12']['tag']['at'], 'type': 'shimmer'},
          {'t': sh['13']['vibAt'], 'type': 'vibrate', 'n': 2}, {'t': sh['14']['red'], 'type': 'ping'}, {'t': sh['14']['red'], 'type': 'hit', 'gain': -3}, {'t': sh['14']['shotAt'], 'type': 'shutter'},
          {'t': st('15'), 'type': 'clock', 'dur': st('16') - st('15')}, {'t': st('16') + 0.2, 'type': 'ringtone', 'dur': st('17') - st('16') - 0.3}]
    ev += [{'t': t, 'type': 'vibrate', 'n': 2} for t in sh['16']['vibAt']]
    ev += [{'t': st('17') + 0.1, 'type': 'click'}, {'t': sh['17']['bubbles'][0]['at'], 'type': 'hit', 'gain': -4}, {'t': st('18'), 'type': 'hangup'},
           {'t': sh['19']['monitor']['at'], 'type': 'ping'}, {'t': sh['19']['monitor']['openAt'], 'type': 'click'}, {'t': st('20') + 0.2, 'type': 'keyboard', 'dur': 2.0},
           {'t': sh['20']['monitor']['youAt'], 'type': 'ui'}, {'t': sh['21']['monitor']['amountAt'], 'type': 'hit', 'gain': -2}, {'t': sh['22']['question'], 'type': 'tick'},
           {'t': sh['23']['monitor']['lastAt'], 'type': 'hit', 'gain': 0}, {'t': sh['23']['monitor']['lastAt'], 'type': 'alarm'},
           {'t': sh['27']['at'], 'type': 'hit', 'gain': -4}, {'t': sh['28']['at'], 'type': 'hit', 'gain': -4},
           {'t': sh['29']['q'], 'type': 'hit', 'gain': -2}, {'t': sh['29']['a'], 'type': 'tick'}, {'t': sh['29']['b'], 'type': 'tick'}, {'t': sh['29']['part2'], 'type': 'shimmer'}, {'t': sh['29']['sub'] + 1.25, 'type': 'click'}]
    ev.sort(key=lambda e: e['t'])
    lastAt = sh['23']['monitor']['lastAt']
    mus = [(0, 0.5), (st('03'), 0.6), (st('05'), 0.45), (st('07'), 0.55), (st('09'), 0.8), (st('11'), 0.5), (st('12'), 0.35), (st('13'), 0.6), (st('14'), 0.85),
           (st('15'), 0.5), (st('16'), 0.75), (st('17'), 0.8), (st('18'), 0.0), (st('18') + 1.2, 0.0), (st('19'), 0.5), (st('21'), 0.85), (lastAt - 0.1, 0.9), (lastAt + 0.1, 0.0),
           (lastAt + 1.4, 0.0), (st('24'), 0.7), (st('27'), 0.85), (st('29'), 0.5), (end - 4.0, 0.3), (end - 1.0, 0.0)]
    chords = [[0.0, st('05') + 0.4, [38, 45, 52, 53]], [st('05'), st('09') + 0.4, [34, 41, 50, 53]], [st('09'), st('13') + 0.4, [38, 46, 52, 57]],
              [st('13'), st('19') + 0.4, [31, 38, 46, 50]], [st('19'), st('24') + 0.4, [33, 40, 49, 52]], [st('24'), end, [38, 45, 50, 53]]]
    tl = {
      '_comment': 'Episode 01 part 2 "You chose the police" (flat 9:16). Generated by tools/make_timeline_btc2.py',
      'fps': 30, 'width': 1080, 'height': 1920, 'duration': end, 'flat': True, 'outName': f'WhatIf_EP01_part2_{lang}_shorts',
      'voice': f'assets/audio/btc2_voice_{lang}.mp3', 'voiceOffset': OFF, 'strings': f'config/strings.{lang}.json', 'transcriptFile': f'config/btc2_transcript_{lang}.json',
      'overlay': {'stages': [{'t': 0.0, 'name': T2('ПОЛИЦИЯ', 'POLICE')[i]}, {'t': st('07'), 'name': T2('СЛЕДСТВИЕ', 'INVESTIGATION')[i]}, {'t': st('13'), 'name': T2('УГРОЗЫ', 'THREATS')[i]}, {'t': st('19'), 'name': T2('ФАЙЛ', 'FILE')[i]}],
                  'hlYellow': T2(r"^(10|20|биткоин|деньг|полици|кошел|неизвестн|звон|сообщени|транзакц|файл|адрес|следовател|специалист|доказательств|криптовалют|выбор|комментар|уведомлени)",
                                 r"^(10|20|bitcoins?|money|police|wallets?|unknown|message|messages|transactions?|file|address|investigator|investigation|evidence|cryptocurrency|choice|choose|notification|crypto|theft)$")[i],
                  'hlRed': T2(r"^(не|ошибку|украденной|преступники|странное|защитить|никто|ничего|доверять)$", r"^(not|didn't|hadn't|mistake|criminals|strange|protect|stolen|trust|interfere|suspicious)$")[i]},
      'shots': shots,
      'cues': {'silence_start': st('18'), 'keep_msg': st('18') + 1.2, 'camera_freeze': end - 1.0, 'hard_black': end - 0.25},
      'audio': {'voiceGainDb': 0, 'musicGainDb': -13, 'events': ev, 'music': [{'t': round(t, 3), 'level': l} for t, l in mus], 'chords': chords,
                'heart': [[st('09'), st('11'), 72], [st('16'), st('19'), 84], [st('21'), lastAt, 90]], 'eerie': [[st('13'), st('19') - st('13')]]},
    }
    json.dump(tl, open(os.path.join(ROOT, 'config', f'timeline.btc2_{lang}_v.json'), 'w'), ensure_ascii=False, indent=1)
    print(lang, len(shots), 'shots, duration', end)
build(0); build(1)
