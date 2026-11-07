"""Episode 02 "What if water disappeared": vertical flat Shorts, RU + EN.
Every time is written as L(ru, en) in VOICE time; the build shifts it by OFF.
usage: python3 tools/make_timeline_ep02.py  -> config/timeline.ep02_ru_v.json, config/timeline.ep02_en_v.json"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFF = 0.3

class L(tuple):
    def __new__(cls, ru, en): return tuple.__new__(cls, (ru, en))
def pick(o, i):
    if isinstance(o, L): return round(o[i] + OFF, 3)
    if isinstance(o, dict): return {k: pick(v, i) for k, v in o.items()}
    if isinstance(o, list): return [pick(v, i) for v in o]
    if isinstance(o, T2): return o[i]
    return o
class T2(tuple):            # text per language
    def __new__(cls, ru, en): return tuple.__new__(cls, (ru, en))

Y, R, B, G = 'yellow', 'red', 'blue', 'green'
def tag(ru, en, color=Y, at=None, rot=0):
    d = {'text': T2(ru, en), 'color': color, 'rot': rot}
    if at is not None: d['at'] = at
    return d
def cam2(a, b): return [list(a), list(b)]
M2, LT = 'clock_morning2', 'clock_later'

S = []
def shot(id_, type_, start, **kw): S.append(dict(id=id_, type=type_, start=start, **kw))
shot('01', 'f_room', L(-0.3, -0.3), inT='black', inDur=0.5, morning=True, clock=M2, cam=cam2((540, 960, 1.0), (600, 1000, 1.15)), phoneOn=0.3, tag=tag('УТРО', 'MORNING', Y, L(0.9, 0.4)))
shot('02', 'f_face', L(2.4, 1.8), expr='happy', thought='glass', thoughtAt=L(4.66, 3.64), clock=M2, cam=cam2((540, 980, 1.0), (540, 940, 1.08)), tag=tag('СТАКАН ХОЛОДНОЙ ВОДЫ', 'A GLASS OF COLD WATER', B, L(4.66, 3.64)))
shot('03', 'f_kitchen', L(6.2, 4.8), clock=M2, openAt=L(8.46, 7.40), nothingAt=L(10.2, 9.04), cam=cam2((540, 960, 1.0), (580, 900, 1.12)), tag=tag('НИЧЕГО', 'NOTHING', R, L(10.2, 9.04)))
shot('04', 'f_tap', L(11.6, 10.3), clock=M2, hardAt=L(13.74, 12.6), xAt=L(15.26, 13.98), cam=cam2((540, 900, 1.0), (560, 860, 1.1)), tag=tag('ВОДЫ НЕТ', 'STILL NOTHING', R, L(15.26, 13.98)))
shot('05', 'f_face', L(16.3, 15.4), expr='skeptic', thought='?', thoughtAt=L(17.52, 16.92), lookX=0.6, clock=M2, cam=cam2((540, 960, 1.05), (540, 960, 1.0)), tag=tag('ОТКЛЮЧИЛИ?', 'WATER SHUT OFF?', B, L(17.52, 16.92)))
shot('06', 'f_bath', L(19.9, 19.6), clock=M2, tapAt=L(23.14, 23.5), showerAt=L(24.72, 25.4), xAt=L(27.2, 27.62), caption={'at': L(27.92, 28.64), 'text': T2('НИ ОДНОЙ КАПЛИ', 'NOT A SINGLE DROP')}, cam=cam2((540, 960, 1.0), (540, 940, 1.08)), tag=tag('ВАННАЯ', 'BATHROOM', B))
shot('07', 'f_phone', L(28.7, 30.3), clock=M2, face='worry', faceAt=L(29.0, 30.6), cam=cam2((540, 720, 1.1), (540, 640, 1.3)),
     screen={'kind': 'lock', 'notifs': [{'at': L(30.86, 32.02), 'kind': 'msg', 'app': T2('УВЕДОМЛЕНИЯ', 'NOTIFICATIONS'), 'title': T2('Нет новых сообщений', 'No new messages'), 'body': T2('Предупреждений об аварии нет', 'No outage warnings')}]},
     tag=tag('НИКАКИХ ПРЕДУПРЕЖДЕНИЙ', 'NO WARNINGS', R, L(34.32, 35.3)))
shot('08', 'f_window', L(36.0, 36.6), morning=True, phone=0.2, cam=cam2((540, 960, 1.0), (540, 900, 1.12)), tag=tag('САМОЕ СТРАШНОЕ', 'THINGS GET TERRIFYING', R, L(39.24, 40.46)))
shot('09', 'f_river', L(40.8, 41.6), boatsAt=L(44.58, 44.92), peopleAt=L(47.62, 47.58), cam=cam2((540, 1000, 1.0), (560, 980, 1.06)), tag=tag('РЕКА', 'THE RIVER', B, L(42.3, 42.8)))
shot('10', 'f_river', L(50.0, 49.5), boatsAt=L(48.0, 48.0), dryAt=L(50.94, 50.96), cam=cam2((560, 980, 1.06), (540, 1040, 1.2)), tag=tag('РЕКИ НЕТ', 'THE RIVER IS GONE', R, L(51.34, 51.36)))
shot('11', 'f_face', L(55.6, 56.5), expr='worry', thought='dam', thoughtAt=L(59.16, 59.94), cam=cam2((540, 960, 1.0), (540, 940, 1.1)), tag=tag('АВАРИЯ НА ПЛОТИНЕ?', 'A DAM ACCIDENT?', Y, L(59.16, 59.94)))
shot('12', 'f_city', L(60.4, 61.4), fountainAt=L(62.7, 63.5), lakeAt=L(64.18, 65.26), holesAt=L(66.9, 70.08), cam=[[L(60.4, 61.4), 380, 900, 1.25], [L(63.9, 64.9), 600, 1000, 1.2], [L(66.6, 69.6), 540, 1060, 1.05], [L(70.3, 72.2), 540, 1040, 1.0]], tag=tag('ВСЁ ВЫСОХЛО', 'EVERYTHING IS DRY', R, L(66.9, 70.08)))
shot('13', 'f_tv', L(70.3, 72.2), worldAt=L(76.4, 79.5), faceAt=L(71.4, 73.3), faceExpr='shock', banner=T2('ЭКСТРЕННЫЕ НОВОСТИ', 'BREAKING NEWS'), ticker=T2('ВОДА ИСЧЕЗАЕТ ПО ВСЕМУ МИРУ  •  ', 'WATER IS DISAPPEARING WORLDWIDE  •  '), cam=cam2((540, 760, 1.0), (560, 720, 1.15)), tag=tag('НЕЧТО НЕВОЗМОЖНОЕ', 'SOMETHING IMPOSSIBLE', R, L(83.16, 86.82)))
shot('14', 'f_globe', L(84.3, 88.6), items=[{'at': L(88.76, 92.36), 'text': T2('РЕКИ', 'RIVERS')}, {'at': L(89.42, 93.14), 'text': T2('ОЗЁРА', 'LAKES')}, {'at': L(90.16, 93.84), 'text': T2('МОРЯ', 'SEAS')}, {'at': L(90.96, 94.72), 'text': T2('ОКЕАНЫ', 'OCEANS')}], cam=cam2((540, 900, 1.0), (540, 880, 1.06)), tag=tag('НЕ ТОЛЬКО ИЗ КРАНОВ', 'NOT JUST THE TAPS', R, L(85.56, 89.18)))
shot('15', 'f_seabed', L(91.9, 95.9), fishAt=L(95.86, 101.96), cam=cam2((420, 900, 1.15), (640, 980, 1.05)), tag=tag('СУХОЕ ДНО', 'DRY OCEAN FLOOR', Y, L(94.64, 99.82)))
shot('16', 'f_store', L(99.3, 104.9), grabFrom=L(101.74, 107.9), emptyAt=L(106.76, 113.48), sign=T2('ВОДА', 'WATER'), emptyText=T2('ПУСТО', 'SOLD OUT'), cam=cam2((540, 900, 1.0), (540, 940, 1.08)), shake=2, tag=tag('ПАНИКА', 'PANIC', R, L(100.14, 106.32)))
shot('17', 'f_glass', L(108.2, 115.1), priceAt=L(113.24, 119.34), price=T2('БЕСЦЕННО', 'PRICELESS'), face='worry', cam=cam2((540, 900, 1.0), (540, 860, 1.12)), tag=tag('НАСТОЯЩАЯ ЦЕННОСТЬ', 'INCREDIBLY VALUABLE', G, L(113.24, 119.34)))
shot('18', 'f_rewind', L(115.0, 121.3), forward=True, clock=LT, tag=tag('ПРОХОДИТ НЕСКОЛЬКО ЧАСОВ', 'A FEW HOURS LATER', Y))
shot('19', 'f_river', L(117.1, 123.0), dry=True, crowd=True, flash=L(121.78, 127.88), clock=LT, cam=cam2((540, 1060, 1.15), (540, 1020, 1.05)), tag=tag('ЛЮДИ НЕ ВЕРЯТ', 'IN DISBELIEF', B, L(123.92, 130.12)))
shot('20', 'f_door', L(126.5, 131.9), doorAt=L(130.8, 136.7), openAt=L(134.1, 140.04), clock=LT, cam=[[L(126.5, 131.9), 540, 1000, 1.0], [L(132.4, 138.0), 540, 1000, 1.0], [L(133.6, 139.2), 540, 900, 1.3], [L(135.6, 141.3), 540, 880, 1.35]], tag=tag('МЕТАЛЛИЧЕСКАЯ ДВЕРЬ', 'A METAL DOOR', R, L(131.66, 136.9)))
shot('21', 'f_door', L(135.6, 141.3), open=0.28, knocks=[L(136.94, 142.66), L(137.4, 142.98), L(138.0, 143.42)], knockText=T2('ТУК', 'KNOCK'), clock=LT, cam=cam2((540, 880, 1.35), (540, 860, 1.45)), tag=tag('ТРИ УДАРА', 'THREE KNOCKS', R, L(136.94, 142.66)))
shot('22', 'f_door', L(139.1, 145.3), open=0.28, dark=L(139.1, 145.3), hand=True, flashAt=L(140.84, 147.36), eyesAt=L(142.6, 148.6), clock=LT, cam=cam2((540, 900, 1.2), (560, 860, 1.35)), tag=tag('ФОНАРИК', 'FLASHLIGHT', Y, L(140.84, 147.36)))
shot('23', 'f_phone', L(143.8, 149.8), clock=LT, vibAt=L(145.1, 152.6), onAt=L(144.0, 150.0), red=L(147.72, 155.76), cam=[[L(143.8, 149.8), 540, 800, 1.0], [L(147.6, 155.6), 540, 640, 1.35], [L(147.8, 155.8), 540, 600, 1.6], [L(149.8, 158.3), 540, 600, 1.65]],
     screen={'kind': 'lock', 'flash': L(145.22, 152.76), 'notifs': [{'at': L(145.22, 152.76), 'kind': 'alert', 'app': T2('ЭКСТРЕННОЕ ОПОВЕЩЕНИЕ', 'EMERGENCY ALERT'), 'title': T2('ВНИМАНИЕ', 'WARNING'), 'body': T2('Не пытайтесь вернуть воду.', 'Do not try to bring the water back.'), 'big': True, 'red': True}]},
     tag=tag('НЕ ПЫТАЙТЕСЬ ВЕРНУТЬ ВОДУ', 'DO NOT BRING THE WATER BACK', R, L(147.72, 155.76), -0.04))
shot('24', 'f_face', L(149.8, 158.3), expr='scared', sweat=True, shake=4, cam=cam2((540, 960, 1.1), (540, 930, 1.2)), tag=tag('ТЫ ЗАМИРАЕШЬ', 'YOU FREEZE', B, L(150.1, 158.7)))
shot('25', 'f_door', L(151.0, 159.8), open=0.28, dark=True, eyesAt=L(151.0, 159.8), questions=L(151.12, 159.98), clock=LT, cam=cam2((540, 880, 1.3), (540, 860, 1.45)), tag=tag('КТО ПОД ЗЕМЛЁЙ?', "WHO'S UNDERGROUND?", R, L(153.16, 162.28)))
shot('26', 'f_end', L(155.2, 164.0), subs=False, dots=True, q=L(155.3, 164.12), line1=T2('ЧТО, ЕСЛИ ЭТО', 'WHAT IF THIS WAS'), line2=T2('ТОЛЬКО НАЧАЛО?', 'ONLY THE BEGINNING?'),
     ask=L(160.0, 168.6), askText=T2('А ТЫ БЫ ОТКРЫЛ ДВЕРЬ?', 'WOULD YOU OPEN THE DOOR?'), askText2=T2('ПИШИ В КОММЕНТАРИЯХ', 'TELL ME IN THE COMMENTS'), part2=L(160.6, 169.2), sub=L(161.6, 170.2), p2l1=T2('ЧТО ЗА ДВЕРЬЮ —', "WHAT'S BEHIND THE DOOR —"), p2l2=T2('УЗНАЕШЬ ВО 2 ЧАСТИ', 'FIND OUT IN PART 2'))
END = L(165.3, 174.0)

def events(i):
    e = []
    g = lambda t: pick(t, i) if isinstance(t, L) else t
    find = lambda id_: next(s for s in S if s['id'] == id_)
    e.append({'t': 0.0, 'type': 'roomtone', 'until': g(END) - 1.2})
    e += [{'t': g(find('03')['openAt']), 'type': 'squeak'}, {'t': g(find('03')['nothingAt']), 'type': 'hit', 'gain': -10},
          {'t': g(find('04')['hardAt']), 'type': 'squeak'}, {'t': g(find('04')['hardAt']) + 0.6, 'type': 'squeak'}, {'t': g(find('04')['xAt']), 'type': 'hit', 'gain': -6},
          {'t': g(find('05')['thoughtAt']), 'type': 'tick'},
          {'t': g(find('06')['tapAt']), 'type': 'squeak'}, {'t': g(find('06')['showerAt']), 'type': 'squeak'}, {'t': g(find('06')['caption']['at']), 'type': 'hit', 'gain': -4},
          {'t': g(find('07')['screen']['notifs'][0]['at']), 'type': 'ui'},
          {'t': g(find('08')['tag']['at']), 'type': 'whoosh', 'gain': -6},
          {'t': g(find('09')['start']), 'type': 'flow', 'dur': g(find('10')['dryAt']) - g(find('09')['start']) + 0.8},
          {'t': g(find('10')['dryAt']), 'type': 'drain'}, {'t': g(find('10')['dryAt']) + 0.4, 'type': 'hit', 'gain': -4},
          {'t': g(find('11')['thoughtAt']), 'type': 'tick'}]
    for k in ('fountainAt', 'lakeAt', 'holesAt'): e.append({'t': g(find('12')[k]), 'type': 'tick'})
    e += [{'t': g(find('13')['start']) + 0.2, 'type': 'jingle'}, {'t': g(find('13')['worldAt']), 'type': 'alarm'}, {'t': g(find('13')['tag']['at']), 'type': 'hit', 'gain': -6}]
    for it in find('14')['items']: e.append({'t': g(it['at']), 'type': 'tick'})
    e += [{'t': g(find('14')['items'][-1]['at']), 'type': 'hit', 'gain': -2},
          {'t': g(find('15')['start']), 'type': 'whoosh', 'gain': -8},
          {'t': g(find('16')['start']), 'type': 'crowd', 'dur': g(find('17')['start']) - g(find('16')['start'])}, {'t': g(find('16')['emptyAt']), 'type': 'hit', 'gain': -4},
          {'t': g(find('17')['priceAt']), 'type': 'shimmer'}, {'t': g(find('18')['start']), 'type': 'clock', 'dur': 2.0},
          {'t': g(find('19')['start']), 'type': 'crowd', 'dur': g(find('20')['start']) - g(find('19')['start'])}]
    f0 = g(find('19')['flash'])
    for k in range(5): e.append({'t': f0 + k * 0.77, 'type': 'shutter'})
    e += [{'t': g(find('20')['doorAt']), 'type': 'hit', 'gain': -4}, {'t': g(find('20')['openAt']), 'type': 'squeak'}]
    for k in find('21')['knocks']: e.append({'t': g(k), 'type': 'knock'})
    e += [{'t': g(find('22')['flashAt']), 'type': 'click'}, {'t': g(find('22')['eyesAt']), 'type': 'hit', 'gain': -8},
          {'t': g(find('23')['vibAt']), 'type': 'vibrate', 'n': 2}, {'t': g(find('23')['screen']['notifs'][0]['at']), 'type': 'alert'},
          {'t': g(find('23')['red']), 'type': 'hit', 'gain': -2},
          {'t': g(find('25')['questions']), 'type': 'whoosh', 'gain': -8},
          {'t': g(find('26')['q']), 'type': 'hit', 'gain': -3}, {'t': g(find('26')['part2']), 'type': 'shimmer'}, {'t': g(find('26')['sub']) + 1.25, 'type': 'click'}]
    return sorted(e, key=lambda x: x['t'])

def music(i):
    find = lambda id_: pick(next(s for s in S if s['id'] == id_)['start'], i)
    pts = [(0, 0.3), (find('03'), 0.4), (find('06'), 0.55), (find('08'), 0.6), (find('10'), 0.85), (find('12'), 0.6), (find('13'), 0.55),
           (find('14'), 0.85), (find('16'), 0.9), (find('17'), 0.5), (find('19'), 0.55), (find('20'), 0.7),
           (find('21') - 0.2, 0.0), (find('22') + 0.4, 0.0), (find('22') + 0.9, 0.6), (find('23'), 0.8), (find('24'), 0.4),
           (find('26'), 0.6), (pick(END, i) - 4.5, 0.4), (pick(END, i) - 1.0, 0.0)]
    return [{'t': round(t, 3), 'level': l} for t, l in pts]

def build(i, lang):
    shots = []
    for s in S:
        d = pick(dict(s), i)
        if 'inT' in d: d['in'] = d.pop('inT')
        shots.append(d)
    for a, b in zip(shots, shots[1:]): a['end'] = b['start']
    end = pick(END, i)
    shots[0]['start'] = 0.0; shots[-1]['end'] = end
    st = lambda id_: next(s for s in shots if s['id'] == id_)['start']
    chords = [[0.0, st('08') + 0.4, [41, 48, 53, 57]], [st('08'), st('13') + 0.4, [38, 45, 52, 53]], [st('13'), st('17') + 0.4, [38, 46, 52, 57]],
              [st('17'), st('20') + 0.4, [34, 41, 50, 53]], [st('20'), st('26') + 0.4, [31, 38, 46, 50]], [st('26'), end, [33, 40, 45, 52]]]
    hb = [[st('10'), st('11'), 70], [st('20'), st('24') + 1.0, 84]]
    langname = 'ru' if i == 0 else 'en'
    tl = {
      '_comment': 'EP02 What if water disappeared. Generated by tools/make_timeline_ep02.py',
      'fps': 30, 'width': 1080, 'height': 1920, 'duration': end, 'flat': True, 'outName': f'WhatIf_EP02_{langname}_shorts',
      'voice': f'assets/audio/ep02_voice_{langname}.mp3', 'voiceOffset': OFF, 'strings': f'config/strings.{langname}.json', 'transcriptFile': f'config/ep02_transcript_{langname}.json',
      'overlay': {'stages': [{'t': 0.0, 'name': T2('КРАН', 'TAP')[i]}, {'t': st('08'), 'name': T2('РЕКА', 'RIVER')[i]}, {'t': st('13'), 'name': T2('МИР', 'WORLD')[i]}, {'t': st('18'), 'name': T2('ДВЕРЬ', 'DOOR')[i]}],
                  'hlYellow': T2(r"^(вод|кран|капл|рек|озер|озёр|мор|океан|корабл|двер|удар|фонарик|телефон|новост|стакан|земл|плотин|фонтан|магазин|бутыл|ценност|душ|утр|окн|лодк|город|телевизор|сообщени)",
                                 r"^(water|tap|taps|drop|river|rivers|lakes?|seas?|oceans?|ships?|door|knocks|flashlight|phone|news|glass|land|dam|fountains|stores?|bottles|valuable|shower|morning|window|boats|cities|television|message|notification|riverbed|underground)$")[i],
                  'hlRed': T2(r"^(не|нет|ничего|страшное|исчезла|исчезло|невозможное|паниковать|замираешь|экстренное|экстренные)$",
                              r"^(nothing|not|no|terrifying|gone|disappeared|impossible|panic|freeze|emergency|strange|dry)$")[i]},
      'shots': shots,
      'cues': {'silence_start': -10, 'keep_msg': -9, 'camera_freeze': end - 1.2, 'hard_black': end - 0.2},
      'audio': {'voiceGainDb': 0, 'musicGainDb': -13, 'events': events(i), 'music': music(i), 'chords': chords, 'heart': hb, 'eerie': [[st('20'), st('26') - st('20')]]},
    }
    json.dump(tl, open(os.path.join(ROOT, 'config', f'timeline.ep02_{langname}_v.json'), 'w'), ensure_ascii=False, indent=1)
    print(lang, 'shots', len(shots), 'duration', end)

build(0, 'ru'); build(1, 'en')
