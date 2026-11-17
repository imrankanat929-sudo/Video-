"""Generate the Russian vertical shot list (shots_v_ru.js) from the English one (shots_v.js).
Every replacement must match, so a change to shots_v.js that breaks the translation fails loudly.
Spec-mandated English captions (ONE DAY LEFT., GTA VI IS NOW AVAILABLE., YOUR NEXT VIDEO..., the video title) stay English."""
import os
here = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(here, 'shots_v.js'), encoding='utf-8').read()
R = [
 ("CH = 'My Channel'", "CH = 'Мой канал'"),
 ("neonText(ctx, 'ONE DAY', W / 2, 850, 150, C.pink); neonText(ctx, 'BEFORE', W / 2, 1000, 150, C.pink)", "neonText(ctx, 'ЗА ДЕНЬ', W / 2, 850, 150, C.pink); neonText(ctx, 'ДО', W / 2, 1000, 150, C.pink)"),
 ("'EPISODE 1'", "'ЭПИЗОД 1'"),
 ("'OUT TOMORROW'", "'ВЫХОДИТ ЗАВТРА'"),
 ("'GTA 6 RELEASES IN'", "'ДО ВЫХОДА GTA 6 ОСТАЛОСЬ'"),
 ("'LINE: 3 BLOCKS LONG'", "'ОЧЕРЕДЬ: 3 КВАРТАЛА'"),
 ("'PRE-ORDER'", "'ПРЕДЗАКАЗ'"), ("'CONSOLE'", "'КОНСОЛЬ'"), ("'GAMING PC'", "'ИГРОВОЙ ПК'"), ("'4K MONITOR'", "'МОНИТОР 4K'"),
 ("text(ctx, 'SOLD OUT', 0, 2, { size: 50", "text(ctx, 'РАСПРОДАНО', 0, 2, { size: 42"), ("boxLabel: 'PC'", "boxLabel: 'ПК'"),
 ("'GTA 6 COMES OUT TOMORROW!!!'", "'GTA 6 ВЫХОДИТ ЗАВТРА!!!'"), ("'I TOOK A WEEK OFF FOR GTA 6'", "'ВЗЯЛ ОТПУСК РАДИ GTA 6'"),
 ("'BOUGHT A NEW PC OVERNIGHT'", "'КУПИЛ НОВЫЙ ПК ЗА НОЧЬ'"), ("'ALL GTA 6 SECRETS'", "'ВСЕ СЕКРЕТЫ GTA 6'"),
 ("'GTA 6 COUNTDOWN STREAM'", "'СТРИМ: ОБРАТНЫЙ ОТСЧЁТ'"), ("'GTA 6 WILL BREAK THE INTERNET'", "'GTA 6 СЛОМАЕТ ИНТЕРНЕТ'"),
 ("M views · ${i + 1}h ago`", " млн просмотров · ${i + 1} ч назад`"),
 ("'New post about GTA 6', 'You were tagged in #GTA6', '1,892 new videos', 'News: servers are ready', 'Friend: \"playing all night\"', 'Store: only 1 PC left'",
  "'Новый пост о GTA 6', 'Тебя отметили в #GTA6', '1 892 новых видео', 'Новость: серверы готовы', 'Друг: «играем всю ночь»', 'Магазин: остался 1 ПК'"),
 ("'just now'", "'только что'"), ("' posts'", "' публикаций'"),
 ("'TRAILER'", "'ТРЕЙЛЕР'"),
 ("'GTA 6 — Standard Edition', 50, 650, { size: 50", "'GTA 6 — Стандартное издание', 50, 650, { size: 44"),
 ("'Release: TOMORROW, 12:00 AM'", "'Выход: ЗАВТРА, 00:00'"), ("'BUY NOW'", "'КУПИТЬ'"), ("'Your balance:  $0.00'", "'Твой баланс:  $0.00'"),
 ("'PAYMENT'", "'ОПЛАТА'"), ("'DECLINED'", "'ОТКЛОНЕНА'"), ("'Insufficient funds'", "'Недостаточно средств'"),
 ("'need $69.99'", "'нужно $69.99'"),
 ("'videos / search: GTA 6'", "'видео / поиск: GTA 6'"),
 ("'I LIVED A DAY IN GTA 6'", "'Я ПРОЖИЛ ДЕНЬ В GTA 6'"), ("'EVERYTHING ABOUT GTA 6'", "'ВСЁ О GTA 6'"), ("'TOP 10 GTA 6 CARS'", "'ТОП-10 МАШИН GTA 6'"),
 ("'GTA 6 IN 60 SECONDS'", "'GTA 6 ЗА 60 СЕКУНД'"), ("'WHAT IF GTA 6 WAS REAL?'", "'ЧТО ЕСЛИ GTA 6 — РЕАЛЬНОСТЬ?'"), ("'GTA 6 CITY TOUR'", "'ГОРОД GTA 6: ОБЗОР'"),
 ("M views`", " млн просмотров`"),
 ("text(ctx, 'WHAT IF…', 540, 200, { size: 120", "text(ctx, 'А ЧТО, ЕСЛИ…', 540, 200, { size: 104"),
 ("'10 sec', 'Cinematic'", "'10 сек', 'Кино'"), ("'Describe your video:'", "'Опиши видео:'"),
 ("'A huge Vice City-style city at night, neon lights, palm trees, sports cars, cinematic shot'", "'Огромный город в стиле Vice City ночью, неон, пальмы, спортивные машины, кинематографичный кадр'"),
 ("'GENERATE ✦'", "'СОЗДАТЬ ✦'"), ("`Generating… ", "`Генерация… "),
 ("'AI VIDEO #1', 'A walk through Vice City'", "'AI ВИДЕО #1', 'Прогулка по Вайс-Сити'"),
 ("'AI VIDEO #2', 'A crazy ride in a sports car'", "'AI ВИДЕО #2', 'Безумная поездка на спорткаре'"),
 ("'AI VIDEO #3', 'What if I ended up inside GTA 6?'", "'AI ВИДЕО #3', 'Что если бы я оказался в GTA 6?'"),
 ("`${Math.floor(112 + t * 12)} MPH`", "`${Math.floor(180 + t * 20)} км/ч`"),
 ("text(ctx, 'NEW LIFE', 540, 570, { size: 130", "text(ctx, 'НОВАЯ ЖИЗНЬ', 520, 570, { size: 88"),
 ("'Mission: earn GTA 6'", "'Миссия: заработать на GTA 6'"),
 ("['VIDEO', 'TEXT', 'MUSIC']", "['ВИДЕО', 'ТЕКСТ', 'МУЗЫКА']"),
 ("`Uploading to ${CH}…`", "`Загрузка: ${CH}…`"), ("'Published!'", "'Опубликовано!'"),
 ("'Views:'", "'Просмотры:'"), ("} HRS`", "} Ч`"),
 ("'1,000 views!', 'Your video is taking off'", "'1 000 просмотров!', 'Видео набирает обороты'"),
 ("'VIEWS'", "'ПРОСМОТРЫ'"), ("'SUBSCRIBERS'", "'ПОДПИСЧИКИ'"),
 ("['Best GTA 6 video ever', 'max_v'], ['Make part two!!!', 'liza.play'], ['How did you make this?', 'kirill_07'], ['Better than the trailer', 'neon_rider'], ['Waiting for the next one', 'arthur']",
  "['Лучшее видео про GTA 6', 'max_v'], ['Сделай вторую часть!!!', 'liza.play'], ['Как ты это сделал?', 'kirill_07'], ['Это лучше трейлера', 'neon_rider'], ['Жду новое видео', 'arthur']"),
 ("'+1 subscriber'", "'+1 подписчик'"),
 ("['THE WHOLE WORLD', 'IS PLAYING']", "['ВЕСЬ МИР', 'ИГРАЕТ']"),
 ("'Notifications'", "'Уведомления'"),
 ("['+128 subscribers', `${CH} is growing`", "['+128 подписчиков', `${CH} растёт`"),
 ("['New comment', '\"waiting for part 2!\"'", "['Новый комментарий', '«жду вторую серию!»'"),
 ("['Trending #12',", "['В тренде #12',"), ("['+1,000 views', 'in the last 5 minutes'", "['+1 000 просмотров', 'за последние 5 минут'"),
 ("} subscribers`", "} подписчиков`"), ("} views`", "} просмотров`"),
 ("'EARNED'", "'ЗАРАБОТАНО'"), ("'GOAL: GTA 6 — $69.99'", "'ЦЕЛЬ: GTA 6 — $69.99'"),
 ("'NEW MESSAGE · unknown sender'", "'НОВОЕ СООБЩЕНИЕ · неизвестный'"),
 ("[['Will', 'he', 'earn'], ['enough', 'money'], ['to', 'finally', 'buy'], ['GTA 6?']]", "[['Сможет', 'ли', 'он'], ['заработать'], ['достаточно', 'денег,'], ['чтобы', 'наконец'], ['купить', 'GTA 6?']]"),
 ("ctx.font = `900 104px ${FONT}`; let wi", "ctx.font = `900 88px ${FONT}`; let wi"),
 ("640 + li * 140 - (1 - a) * 20, { size: 104", "600 + li * 120 - (1 - a) * 20, { size: 88"),
 ("ctx.font = `900 104px ${FONT}`; x +=", "ctx.font = `900 88px ${FONT}`; x +="),
 ("'Tell me in the comments'", "'Пиши ответ в комментариях'"),
 ("neonText(ctx, 'ONE DAY BEFORE', 0, 0, 104, C.pink)", "neonText(ctx, 'ЗА ДЕНЬ ДО', 0, 0, 110, C.pink)"),
 ("text(ctx, 'TO BE CONTINUED…', 540, 1660, { size: 84", "text(ctx, 'ПРОДОЛЖЕНИЕ СЛЕДУЕТ…', 540, 1660, { size: 66"),
 ("'EPISODE 2 — COMING SOON'", "'ЭПИЗОД 2 — СКОРО'"),
 ("text(ctx, '1 DAY', 0, 0, { size: 190", "text(ctx, 'ЗА ДЕНЬ', 0, 0, { size: 170"),
 ("text(ctx, 'BEFORE', 0, 190, { size: 170", "text(ctx, 'ДО', 0, 190, { size: 190"),
 ("fillRR(ctx, -230, -60, 460, 120, 18, C.red); text(ctx, 'NO MONEY', 0, 4, { size: 76", "fillRR(ctx, -260, -60, 520, 120, 18, C.red); text(ctx, 'НЕТ ДЕНЕГ', 0, 4, { size: 72"),
]
for a, b in R:
    if a not in s: raise SystemExit('missing: ' + a)
    s = s.replace(a, b)
s = s.replace('fmtEn(', 'fmt(')
s = s.replace('// "ONE DAY BEFORE GTA 6" — vertical 9:16 English cut', '// «ЗА ДЕНЬ ДО GTA 6» — vertical 9:16 Russian cut (generated by make_ru.py — edit shots_v.js instead)')
open(os.path.join(here, 'shots_v_ru.js'), 'w', encoding='utf-8').write(s)
print('ok', len(R), 'replacements')
