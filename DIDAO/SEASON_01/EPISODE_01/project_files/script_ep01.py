"""DIDAO S01E01 "THE LAST NIGHT" - master script / timing sheet (v2: client voiceover).

The narration is the client's recorded voiceover (second person, RU + EN), cut into lines
(see make_voiceover.py). Picture is shared by both languages; clip durations fit the longer language.

Clip fields:
  id, name, dur (s)
  scene: (renderer id, time offset inside that renderer)
  vo: {'ru': [...], 'en': [...]}, each line = (planned start inside the clip or None, source segment(s), subtitle text)
      source = segment index from the transcription, a list of indices, or an explicit (t0, t1) range in the recording.
"""

SERIES = "DIDAO"
SEASON_TITLE_EN = "THE FOREST HAS NO EXIT"
SEASON_TITLE_RU = "ЛЕС БЕЗ ВЫХОДА"
EP_TITLE_EN = "Episode 1: The Last Night"
EP_TITLE_RU = "Серия 1: Последняя ночь"

VO_SOURCE = {'ru': 'voiceover/source/DIDAO_EP01_VO_RU_ORIGINAL.mp3', 'en': 'voiceover/source/DIDAO_EP01_VO_EN_ORIGINAL.mp3'}
GAP = 0.30   # minimum pause between two narration lines

CLIPS = [
    dict(id=1, name="CLIP_01A_JOURNEY", dur=7.1, scene=(1, 0.0), vo={
        'ru': [(0.4, 0, "Представь, что ты отправился с друзьями в лес на выходные."),
               (None, 1, "Вы хотели просто отдохнуть, разбить палатку и провести ночь под звёздами."),
               (None, 2, "Но вы даже не представляли, что этот лес станет вашей ловушкой.")],
        'en': [(0.4, 0, "Imagine going camping in the forest with your friends for the weekend."),
               (None, 1, "You just want to relax, set up a tent, and spend a night under the stars."),
               (None, 2, "But you have no idea that this forest is about to become your trap.")]}),
    dict(id=2, name="CLIP_01B_JOURNEY", dur=7.4, scene=(1, 7.1), vo={'ru': [], 'en': []}),
    dict(id=3, name="CLIP_02_CAMPSITE", dur=6.0, scene=(2, 0.0), vo={
        'ru': [(0.6, 3, "В первый вечер всё было спокойно.")],
        'en': [(0.6, 3, "On the first evening, everything seems normal.")]}),
    dict(id=4, name="CLIP_03A_CAMPFIRE", dur=8.2, scene=(3, 0.0), vo={
        'ru': [(0.4, 4, "Вы сидели у костра, разговаривали и шутили."),
               (3.3, 5, "Но вдруг твой друг заметил между деревьями высокую фигуру.")],
        'en': [(0.4, 4, "You're sitting around the campfire, talking and laughing."),
               (3.3, 5, "Suddenly, your friend notices a tall figure standing between the trees.")]}),
    dict(id=5, name="CLIP_03B_FIRST_SIGHTING", dur=5.2, scene=(30, 0.0), vo={
        'ru': [(0.3, 6, "Она была настолько высокой, что почти доставала до верхушек деревьев.")],
        'en': [(0.3, 6, "It's so tall that it almost reaches the treetops.")]}),
    dict(id=6, name="CLIP_04_DISAPPEARANCE", dur=9.9, scene=(4, 0.0), vo={
        'ru': [(0.3, 7, "Ты направил на неё фонарик."),
               (2.4, 8, "Но в следующую секунду фигура исчезла."),
               (5.6, 9, "Вы решили, что это просто игра теней, и легли спать.")],
        'en': [(0.3, 7, "You point your flashlight toward it."),
               (2.4, 8, "But the next second, the figure disappears."),
               (5.6, 9, "You decide it was just a trick of the shadows and go to sleep.")]}),
    dict(id=7, name="CLIP_05_MIDNIGHT", dur=6.0, scene=(5, 0.0), vo={
        'ru': [(0.8, 10, "Около полуночи ты проснулся от странного звука.")],
        'en': [(0.8, 10, "Around midnight, you wake up because of a strange sound.")]}),
    dict(id=8, name="CLIP_06_FOOTSTEPS", dur=10.0, scene=(6, 0.0), vo={
        'ru': [(0.3, (41.80, 43.50), "Три медленных шага…"),
               (4.4, (43.50, 44.70), "…потом тишина."),
               (6.3, 12, "И ещё три шага.")],
        'en': [(0.3, 11, "Three slow footsteps."),
               (4.4, 12, "Then silence."),
               (6.3, 13, "And three more footsteps.")]}),
    dict(id=9, name="CLIP_07A_SECOND_SIGHTING", dur=9.3, scene=(7, 0.0), vo={
        'ru': [(0.5, 13, "Ты осторожно открыл палатку и выглянул наружу."),
               (3.6, 14, "На поляне стоял тот самый силуэт."),
               (6.3, 15, "Высокий, худой, в чёрном костюме.")],
        'en': [(0.5, 14, "You carefully open the tent and look outside."),
               (3.6, 15, "The same figure is standing in the clearing."),
               (6.3, 16, "Tall, thin, wearing a black suit.")]}),
    dict(id=10, name="CLIP_07B_NO_FACE", dur=5.4, scene=(70, 0.0), vo={
        'ru': [(0.4, 16, "Но самое странное было в другом."),
               (2.6, 17, "У него не было лица.")],
        'en': [(0.4, 17, "But there's something even stranger."),
               (2.6, 18, "It has no face.")]}),
    dict(id=11, name="CLIP_08_DISAPPEARANCE_AGAIN", dur=8.0, scene=(8, 0.0), vo={
        'ru': [(0.3, 18, "Ты резко разбудил друзей."),
               (3.9, 19, "Но когда они выбежали из палатки, фигура уже исчезла.")],
        'en': [(0.3, 19, "You quickly wake your friends."),
               (3.9, 20, "But when they rush outside, the figure is already gone.")]}),
    dict(id=12, name="CLIP_09_MISSING_PATH", dur=10.4, scene=(9, 0.0), vo={
        'ru': [(0.5, 20, "Утром вы решили немедленно покинуть лес."),
               (3.4, 21, "Однако дорога, по которой вы пришли, исчезла."),
               (6.6, 22, "Вместо неё повсюду были одинаковые деревья.")],
        'en': [(0.5, 21, "In the morning, you decide to leave the forest immediately."),
               (3.4, 22, "But the road you used to get here has disappeared."),
               (6.6, 23, "Everywhere you look, there are identical trees.")]}),
    dict(id=13, name="CLIP_10_WARNING", dur=7.8, scene=(10, 0.0), vo={
        'ru': [(0.3, 23, "Вы начали искать выход, пока не заметили странную надпись на одном из стволов."),
               (5.2, 24, "«Не смотрите назад».")],
        'en': [(0.3, 24, "You start searching for an exit until you notice a strange message carved into a tree."),
               (5.2, 25, "“Do not look back.”")]}),
    dict(id=14, name="CLIP_11_PHONE_MESSAGE", dur=9.2, scene=(11, 0.0), vo={
        'ru': [(0.3, 25, "В этот момент твой телефон завибрировал."),
               (2.9, 26, "Пришло сообщение от неизвестного отправителя."),
               (6.1, 27, "«Я вижу вас всех».")],
        'en': [(0.3, 26, "At that moment, your phone vibrates."),
               (2.9, 27, "A message appears from an unknown sender."),
               (6.1, 28, "“I can see you all.”")]}),
    dict(id=15, name="CLIP_12_FINAL_REVEAL", dur=9.6, scene=(12, 0.0), vo={
        'ru': [(0.4, 28, "Ты поднял голову и посмотрел между деревьями."),
               (3.6, 29, "Там стояли три одинаковые фигуры."),
               (6.0, 30, "Но одна из них была гораздо ближе остальных.")],
        'en': [(0.4, 29, "You raise your head and look between the trees."),
               (3.6, 30, "Three identical figures are standing there."),
               (6.0, 31, "But one of them is much closer than the others.")]}),
    dict(id=16, name="CLIP_13_THE_FOURTH", dur=4.9, scene=(13, 0.0), vo={
        'ru': [(0.3, 31, "И вдруг твой друг прошептал:"),
               (2.1, 32, "«Подожди… а где четвёртый?»")],
        'en': [(0.3, 32, "Suddenly, your friend whispers:"),
               (2.1, 33, "“Wait… where is the fourth one?”")]}),
    dict(id=17, name="CLIP_14_EMPTY_TENT", dur=9.8, scene=(14, 0.0), vo={
        'ru': [(0.3, 33, "Ты обернулся, но палатка уже была пуста."),
               (4.0, 34, "Как думаешь, куда исчез твой друг?")],
        'en': [(0.3, 34, "You turn around."),
               (None, 35, "But the tent is already empty."),
               (4.0, 36, "Where do you think your friend disappeared?")]}),
]

# the clip whose picture contains the language-specific end card
END_CARD_CLIP = 17

# durations fitted to the recorded narration by make_voiceover.py
import json as _json, os as _os
_fit = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'clip_durations.json')
if _os.path.exists(_fit):
    _d = _json.load(open(_fit))
    for _c in CLIPS:
        _c['dur'] = _d.get(str(_c['id']), _c['dur'])
    _acc = 0.0
    for _c in CLIPS:
        if _c['scene'][0] == 1:
            _c['scene'] = (1, _acc)
            _acc += _c['dur']
