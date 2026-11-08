# Кадры 1–5 — промпты для генерации (9:16)

Время по 60-секундной RU-озвучке (в скобках — EN-версия).

## Шаг 0. Лист персонажей (сгенерировать один раз, дальше использовать как референс)

Имена актёров в промпт не пишем: генераторы обычно блокируют реальные лица. Внешность задана словами и одинаковая в каждом промпте.

**JOHN (блок внешности — вставляется во все кадры):**
`John, American soldier, 40 years old, fair skin, short dark-brown hair, short trimmed dark-brown beard and stubble, piercing blue eyes, strong athletic build, defined cheekbones and jawline`

**AHMED (блок внешности):**
`Ahmed, Afghan interpreter, 40 years old, olive skin, short dark hair, neat full dark beard, brown eyes, strong broad build, expressive deep-set eyes, calm serious face`

Промпт листа персонажей (сделать отдельно для каждого героя):
```
Character reference sheet, photorealistic, [БЛОК ВНЕШНОСТИ], front view, three-quarter view, profile view, neutral expression, plain light-grey background, soft even studio light, same face in all views, high detail skin texture, 35mm film look
```
John: в форме US Army, мультикам, без шлема. Ahmed: в песочной рубахе-камиз и коричневом жилете.

Дальше каждый кадр генерируем с этим листом как референсом: Midjourney `--cref <ссылка> --cw 100`, Kling/Runway — загрузить как reference/element, ChatGPT/Flux Kontext — приложить картинку и написать «same man as in reference».

**Общий стиль (добавлять в конец каждого промпта):**
`cinematic war thriller still, shot on ARRI Alexa, anamorphic 35mm lens, sandy and dark olive color grade, high contrast, realistic lighting, fine film grain, vertical 9:16 composition, no text, no watermark`

**Негатив:** `cartoon, anime, 3d render, extra people, extra fingers, distorted face, text, logo, watermark, gore, blood splatter, open wounds`

---

## КАДР 1 — 00:00.0–00:01.6 (EN 00:00.0–00:01.0)
**Озвучка:** «Американский солдат…» / "An American soldier…"
- **План:** экстремально крупный, только глаза и переносица.
- **Ракурс:** камера прямо перед лицом, на уровне глаз, чуть снизу.
- **Персонаж:** Джон, взгляд расфокусирован и устремлён мимо камеры. Лицо в пыли, тонкая полоска засохшей крови у виска, капли пота.
- **Передний план:** в фокусе голубые глаза; пылинки в воздухе, размытые.
- **Задний план:** не виден, тёплая размытая дымка.
- **Свет:** жёсткое солнце сбоку-сверху, одна половина лица в тени, блик в глазах.
```
Extreme close-up of [JOHN], only eyes and bridge of nose fill the vertical frame, face covered in fine desert dust, thin line of dried blood near the temple, beads of sweat, unfocused shocked stare just past the camera, piercing blue eyes in sharp focus, floating dust particles in the foreground, harsh side sunlight from upper left, half of the face in shadow, catchlight in the eyes, [STYLE]
```
**Движение (image-to-video):** `very slow push-in, eyes blink once, dust drifts, 2 seconds`

---

## КАДР 2 — 00:01.6–00:03.0 (EN 00:01.0–00:03.3)
**Озвучка:** «…оказался на вражеской территории.» / "…is trapped behind enemy lines,"
- **План:** общий, сверху.
- **Ракурс:** высокий ракурс с дрона, 30–40 м, камера смотрит вниз под углом ~45°.
- **Персонаж:** Джон — маленькая фигура в нижней трети кадра, лежит на спине среди камней, в форме мультикам.
- **Передний план:** скалистый склон, обломки камней, выжженная трава.
- **Задний план:** горный хребет Гиндукуш в верхней половине кадра, два столба тёмного дыма поднимаются за холмом.
- **Свет:** послеполуденное солнце, длинные тени, пыльная дымка в воздухе.
```
High-angle aerial wide shot looking down on a rocky Afghan mountain slope, a lone wounded American soldier in multicam uniform lying on his back among broken rocks, very small in the lower third of the vertical frame, scorched dry grass and rubble around him, rugged Hindu Kush ridges filling the upper half, two columns of dark smoke rising from behind a hill, hazy dusty air, late afternoon sun, long hard shadows, sense of isolation, no other people, [STYLE]
```
**Движение:** `slow descending drone move toward the soldier, smoke drifting, 1.5 seconds`

---

## КАДР 3 — 00:03.0–00:04.3 (EN 00:03.3–00:04.4)
**Озвучка:** «Его отряд уничтожен…» / "…his team is gone,"
- **План:** средний-крупный, деталь.
- **Ракурс:** камера у самой земли, низкий ракурс.
- **Персонажи:** нет (людей и тел в кадре нет).
- **Передний план:** пыльный боевой шлем US Army лежит на боку на камнях, рядом штурмовая винтовка M4 и порванная радиостанция.
- **Задний план:** не в фокусе — сгоревший бронеавтомобиль MRAP, лёгкий дым.
- **Свет:** контровое солнце через дым, лучи в пыли.
```
Low ground-level close shot of an abandoned dusty US Army combat helmet lying on its side on rocks, an M4 rifle and a torn military radio beside it, scattered spent casings, no people, no bodies, out-of-focus burned-out armored military vehicle in the background with thin smoke, backlit by low sun through the smoke, visible light rays in the dust, somber silent aftermath mood, shallow depth of field, [STYLE]
```
**Движение:** `slow lateral slide left to right, smoke drifting, 1.5 seconds`

---

## КАДР 4 — 00:04.3–00:05.75 (EN 00:04.4–00:05.8)
**Озвучка:** «…а сам он тяжело ранен.» / "…and he is badly injured."
- **План:** средний (по пояс).
- **Ракурс:** сверху вниз над героем (top shot), камера немного сбоку.
- **Персонаж:** Джон лежит на спине у валуна, тяжело дышит, глаза полузакрыты. Одна рука прижимает пропитанный бинт к бедру, вторая бессильно лежит на земле. Без открытых ран.
- **Передний план:** край валуна, гильзы.
- **Задний план:** пыльная земля, тень от скалы.
- **Свет:** жёсткое солнце, лицо частично в тени скалы, холодноватые тени.
```
Top-down medium shot of [JOHN] lying on his back against a large boulder in rocky Afghan terrain, wearing dusty multicam uniform and plate carrier, eyes half-closed, breathing heavily, one hand pressing a dirty bandage to his thigh, other hand limp on the ground, no visible open wounds, spent casings near the boulder edge in the foreground, harsh sun with the boulder's shadow falling across half his face, exhausted and fading, [STYLE]
```
**Движение:** `slow push-in toward his face, chest rises and falls, 1.5 seconds`

---

## КАДР 5 — 00:05.75–00:09.85 (EN 00:05.8–00:10.3)
**Озвучка:** «Но самое невероятное — его спасёт человек, которого он едва знает.» / "But the person who will save him is someone he barely knows."
- **План:** крупный, лицо Ахмеда.
- **Ракурс:** снизу, глазами лежащего Джона (POV), камера смотрит вверх.
- **Персонаж:** Ахмед склонился над камерой, протягивает руку вниз к зрителю. Взгляд тревожный и решительный. Песочная рубаха-камиз, коричневый жилет, на плече ремень сумки.
- **Передний план:** протянутая рука Ахмеда, слегка размыта.
- **Задний план:** яркое небо, солнце прямо за его головой — контровой ореол.
- **Свет:** контровой свет, лицо подсвечено мягким отражённым светом от земли.
```
Low-angle POV close-up looking up from the ground at [AHMED] leaning over the camera, reaching his hand down toward the viewer, worried but determined look, wearing a sand-colored shalwar kameez shirt and brown vest with a bag strap over his shoulder, his outstretched hand in the foreground slightly out of focus, bright pale sky behind him, sun directly behind his head creating a rim-light halo, face softly lit by warm light bounced from the ground, hopeful dramatic moment, [STYLE]
```
**Движение:** `start out of focus, rack focus onto his face as he reaches down, slow push-in, 4 seconds`

---

## Порядок на таймлайне
| # | RU | EN | Фраза |
|---|---|---|---|
| 1 | 0.0–1.6 | 0.0–1.0 | Американский солдат |
| 2 | 1.6–3.0 | 1.0–3.3 | оказался на вражеской территории |
| 3 | 3.0–4.3 | 3.3–4.4 | Его отряд уничтожен |
| 4 | 4.3–5.75 | 4.4–5.8 | а сам он тяжело ранен |
| 5 | 5.75–9.85 | 5.8–10.3 | его спасёт человек, которого он едва знает |

Всего в ролике будет 22 кадра (вместо прежних 31), каждый привязан к фразе.
