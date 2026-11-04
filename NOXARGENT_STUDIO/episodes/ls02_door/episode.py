"""«Последний сигнал», серия 2 — «За дверью».

Запуск:
  python episode.py --test     10-секундный тест → test_10s.mp4
  python episode.py            полная серия → Рабочий стол/СЕРИЯ_2.mp4 + СЕРИЯ_2.srt
"""
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "library"))

import apartment as AP  # noqa: E402
import phone as PH  # noqa: E402
import radio as RD  # noqa: E402
import sound as SND  # noqa: E402
import subs as SUB  # noqa: E402
from characters import arman_back, arman_front_silhouette  # noqa: E402
from city import Opposite  # noqa: E402
from core import (AA, FPS, H, W, apply_light, blob, camera, desktop, digital_glitch, draw_text, ease,  # noqa: E402
                  lerp, paste_rgba, pil_to_bgra, ramp, shake, to_lmap, u8, warp_rgba)
from engine import Episode, render  # noqa: E402
from shotkit import PhoneHands, Shot, live_sprite, place_phone, sprite  # noqa: E402

NUM = 2
VOICE = HERE / "voice.mp3"
BLACK, CARD = 2.0, 3.0          # 2 с чёрного (по ТЗ), затем титр
UNKNOWN = "Неизвестный номер"
DATE = "ЗАВТРА · 23:41"
CAPTION = "ОДИН ИЗ ВАС НЕ ДОЖИВЁТ ДО УТРА"

FIXES = {"Ми шагов": "Ни шагов", "Ми звука": "Ни звука", "0-3-17": "ноль три, семнадцать", "Амино": "Амина",
         "накысал": "написал", "похолодили": "похолодели", "Воспроизведение": "воспроизведение"}


def audio_len(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


SEG = SUB.transcribe(VOICE, HERE / "transcript.json")
AUDIO = audio_len(VOICE)
DUR = AUDIO + BLACK + CARD
wt = lambda p, after=0.0, end=False: SUB.word_time(SEG, p, after, end)  # noqa: E731

T = dict(
    turned=wt("обернулся", 3), creak=wt("двигалась", 6), chain=wt("цепочка", 13), torch=wt("включил", 20),
    empty=wt("пусто", 23), step=wt("шаг", 31), noticed=wt("заметил", 33), back=wt("задней", 38),
    lit=wt("загорелся", 44), play=wt("нажал", 48), entered=wt("вошёл", 57), scratch=wt("царапину", 59),
    looked=wt("посмотрел", 67), amina1=wt("амин", 76), froze=wt("видео", 82), rewound=wt("перемотал", 83),
    instead=wt("вместо", 85), dont=wt("не", 89), threw=wt("бросил", 90), vibr=wt("завибрировал", 93),
    msg1=wt("ты", 98), who=wt("кто", 101),
    answer=wt("ответ", 103), reply=wt("ты", 105), photo=wt("после", 107), street=wt("снимок", 110),
    zoomed=wt("увеличил", 114), was_me=wt("был", 119), corner=wt("из", 124), turned2=wt("повернул", 128),
    nobody=wt("никого", 131), ring=wt("зазвонил", 133), noise=wt("сначала", 139), name=wt("зовут", 144),
    sofa=wt("посмотрел", 156), know=wt("откуда", 160), seven=wt("семь", 167), cut=wt("оборвалась", 173),
    new_msg=wt("на", 177), two=wt("на", 181), amina2=wt("амин", 186), radio=wt("находились", 189),
    sign=wt("за", 191), date=wt("внизу", 195), tomorrow=wt("завтрашний", 196), caption=wt("а", 199),
    zoom2=wt("увеличил", 205), another=wt("ещё", 209), off=wt("погас", 214), voice=wt("из", 215),
    dont_meet=wt("встречайся", 219, end=True), late=wt("но", 222), knock=wt("постучал", 224, end=True),
    final=wt("и", 225), last=SEG[-1]["end"],
)
T["typed0"], T["sent"] = T["who"] - 0.6, T["who"] + 0.9


# ---------- общие фоны ----------
def living_dark(table_light=False):
    room = AP.living_base(city_lit=False)
    lm = np.full((H, W, 3), 0.3, np.float32) + blob(H, W, 1580, 600, 420, 500, (0.25, 0.32, 0.45))
    return apply_light(room, to_lmap(lm))


SOFA_PHONE = (600, 905)  # где лежит чужой телефон (на диване, передний план гостиной)


def foreign_on_sofa(img, scr=None, glow=0.0):
    """Чужой телефон лежит на диване экраном вверх."""
    spr = live_sprite(scr if scr is not None else PH.screen_off(), cracked=True)
    s = warp_rgba(spr, 0.2, -8)  # почти прямо: надписи на экране читаются
    x, y = SOFA_PHONE
    if glow > 0:
        cv2.add(img, u8(blob(H, W, x, y - 10, 160, 90, (60, 60, 70), glow)), dst=img)
    paste_rgba(img, s, x - s.shape[1] / 2, y - s.shape[0] / 2)


# ======================= ПЛАНЫ =======================
class HallWide(Shot):
    """0:00 Прихожая: дверь приоткрыта, Арман — маленький силуэт со спины."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        img = AP.hallway_base()
        d = AP.DOOR
        cv2.rectangle(img, (d["x0"], d["y0"]), (d["x1"], d["y1"]), (30, 28, 28), -1)
        AP.door_panel(img, 0.3)
        arman_back(img, 960, 1010, 470, arms_forward=False)
        self.img = apply_light(img, to_lmap(AP.hallway_lmap(flash=(1050, 520, 220))))

    def frame(self, t):
        return camera(self.img, 1.0 + 0.1 * ease(self.k(t)), 960, 540)


class EmptyRoom(Shot):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.img = living_dark()

    def frame(self, t):
        return camera(self.img, 1.04 + 0.03 * self.k(t), 960, 540)


class DoorMoves(Shot):
    """0:07 Дверь сама сдвигается на несколько сантиметров. mode: moving | gap (полоса света с площадки)."""

    def __init__(self, t0, t1, mode="moving"):
        super().__init__(t0, t1)
        self.mode = mode
        self.base = AP.hallway_base()
        self.lm = to_lmap(AP.hallway_lmap(flash=(960, 520, 280)))

    def frame(self, t):
        img = self.base.copy()
        d = AP.DOOR
        cv2.rectangle(img, (d["x0"], d["y0"]), (d["x1"], d["y1"]), (30, 28, 28), -1)
        if self.mode == "moving":
            k = 0.3 + 0.08 * ramp(t, T["creak"], T["creak"] + 2.6)
            AP.door_panel(img, k)
            img = apply_light(img, self.lm)
            return camera(img, 1.25 + 0.1 * ease(self.k(t)), 960, 530)
        on = (t % 1.0) < 0.6  # свет мигающей лампы на площадке
        AP.door_panel(img, 0.38, gap_col=(70, 84, 84) if on else (24, 28, 28))
        img = apply_light(img, self.lm)
        return camera(img, 1.45, 1060, 540)


class LockChain(Shot):
    """0:13 Крупно: замок закрыт, цепочка висит на месте."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.l = AP.LockClose()

    def frame(self, t):
        img = self.l.frame(t)
        k = ramp(t, T["chain"] - 0.2, T["chain"] + 0.5)
        return camera(img, lerp(1.1, 1.5, k), lerp(910, 1480, k), lerp(400, 420, k))


class LandingBeam(Shot):
    """0:20 Луч фонарика в коридор: пустая площадка, лампа мигает ровно."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.l = AP.Landing()

    def frame(self, t):
        k = ease(self.k(t))
        fx = lerp(700, 2000, k)
        on = t >= T["torch"] + 0.3
        img = self.l.frame(t, flash=(fx, 620, 260) if on else None)
        return camera(img, 1.0, lerp(900, 1700, k), 540)


class StepDown(Shot):
    """0:31 Шаг к двери; камера опускается: на полу телефон."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        img = AP.hallway_base()
        d = AP.DOOR
        cv2.rectangle(img, (d["x0"], d["y0"]), (d["x1"], d["y1"]), (30, 28, 28), -1)
        AP.door_panel(img, 0.38)
        self.base = img
        rng = np.random.default_rng(4)
        fl = np.zeros((H, W, 3), np.uint8)
        fl[:] = (26, 26, 30)
        for x in range(0, W, 160):
            cv2.line(fl, (x, 0), (x + 40, H), (18, 18, 22), 3)
        cv2.rectangle(fl, (0, 0), (W, 160), (16, 14, 14), -1)       # порог
        cv2.rectangle(fl, (0, 150), (W, 175), (40, 38, 36), -1)
        spr = PH.add_cracks(PH.phone_sprite(PH.to_bgr(PH.screen_off())))
        place_phone(fl, spr, 980, 560, 0.42, 72)
        self.floor = apply_light(fl, to_lmap(np.full((H, W, 3), 0.4, np.float32) + blob(H, W, 980, 560, 420, 300, (1.6, 1.7, 1.8))))

    def frame(self, t):
        if t < T["noticed"] + 0.3:
            k = ramp(t, self.t0, T["noticed"])
            img = apply_light(self.base, to_lmap(AP.hallway_lmap(flash=(960, lerp(560, 760, k), 260))))
            arman_back(img, 960, lerp(1240, 1120, k), lerp(900, 780, k), arms_forward=True)
            return camera(img, 1.0 + 0.08 * k, 960, lerp(540, 600, k))
        k = ramp(t, T["noticed"] + 0.3, T["noticed"] + 1.0)
        return camera(self.floor, lerp(1.0, 1.15, ease(self.k(t))), 960, lerp(380, 540, k))


class ForeignPhone(Shot):
    """0:35 Чужой телефон: треснутый экран, затем задняя крышка с наклейкой «03:17»."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        fl = np.zeros((H, W, 3), np.uint8)
        fl[:] = (26, 26, 30)
        for x in range(0, W, 160):
            cv2.line(fl, (x, 0), (x + 40, H), (18, 18, 22), 3)
        self.floor = apply_light(fl, to_lmap(np.full((H, W, 3), 0.4, np.float32) + blob(H, W, 960, 540, 520, 420, (1.6, 1.7, 1.8))))
        self.front = PH.add_cracks(PH.phone_sprite(PH.to_bgr(PH.screen_off())))
        self.back = PH.phone_back()

    def frame(self, t):
        img = self.floor.copy()
        if t < T["back"]:
            place_phone(img, self.front, 960, 540, 0.72, 4)
            return camera(img, 1.0 + 0.15 * ease((t - self.t0) / (T["back"] - self.t0)), 1020, 400)
        place_phone(img, self.back, 960, 540, 0.72, -3)
        k = ease((t - T["back"]) / (self.t1 - T["back"]))
        return camera(img, lerp(1.0, 2.0, k), lerp(960, 1045, k), lerp(540, 600, k))


class ScreenOn(Shot):
    """0:45 Экран чужого телефона загорается сам: открыто видео."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        bg = AP.hallway_base()
        self.ph = PhoneHands(t0, t1, bg, self.scr, shakes=(T["lit"],))

    def scr(self, t):
        if t < T["lit"]:
            return sprite("f_off", PH.screen_off, cracked=True)
        return sprite("f_video", PH.screen_video_ready, cracked=True)

    def frame(self, t):
        img = self.ph.frame(t)
        if T["lit"] <= t < T["lit"] + 0.25:
            img = cv2.convertScaleAbs(img, alpha=1.8)
        return img


class Video(Shot):
    """0:49–1:31 Запись на чужом телефоне: та же гостиная, статичная камера.
    Арман входит в кадр, царапина на рукаве, подходит к камере; зависание и «НЕ ПЕРЕМАТЫВАЙ»."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        room = AP.living_base(city_lit=False)
        lm = np.full((H, W, 3), 0.75, np.float32) + blob(H, W, 1210, 260, 120, 110, (3.2, 3.4, 3.6))  # пятно фонарика на стене
        self.room = apply_light(room, to_lmap(lm))
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_text(im, (0, 440), "НЕ ПЕРЕМАТЫВАЙ", 128, (235, 50, 44, 255), "bold", max_w=W, align="center")
        self.warn = pil_to_bgra(im)
        self.frozen = None

    def scene(self, t):
        img = self.room.copy()
        if t >= T["entered"] + 0.35:
            k = ramp(t, T["entered"] + 0.35, T["entered"] + 2.2)
            x = lerp(-150, 1150, k)
            h = 620
            if t >= T["looked"]:
                kk = ramp(t, T["looked"], T["froze"] - 1.0)
                h = lerp(620, 1500, kk)
                x = lerp(1150, 960, kk)
            sway = math.sin(t * 1.3) * 6
            arman_front_silhouette(img, x + sway, 920 + (h - 620) * 0.55, h, col=(8, 8, 10))
            cv2.ellipse(img, (int(x + sway), int(920 + (h - 620) * 0.55 - h * 0.92)), (int(h * 0.08), int(h * 0.094)), 0, 200, 340, (60, 62, 70), max(2, int(h * 0.006)), AA)  # контровой свет
            if T["scratch"] <= t < T["looked"]:  # царапина на правом рукаве
                sx, sy = x + sway + h * 0.16, 920 - h * 0.55
                cv2.line(img, (int(sx - 10), int(sy - 18)), (int(sx + 8), int(sy + 16)), (90, 90, 96), 3, AA)
                cv2.line(img, (int(sx - 4), int(sy - 20)), (int(sx + 12), int(sy + 10)), (70, 70, 76), 2, AA)
        return img

    def frame(self, t):
        if t < T["froze"]:
            img = self.scene(t)
            z, cx, cy = 1.0, 960, 540
            if T["scratch"] <= t < T["looked"]:  # цифровой зум к рукаву
                k = ramp(t, T["scratch"], T["scratch"] + 1.2) * (1 - ramp(t, T["looked"] - 1.5, T["looked"] - 0.3))
                z, cx, cy = lerp(1.0, 3.2, k), lerp(960, 1150 + 620 * 0.16, k), lerp(540, 920 - 620 * 0.55, k)
            img = camera(img, z, cx, cy)
            g = 0.15 + (0.8 if abs(t - (T["entered"] + 0.2)) < 0.25 else 0) + (0.5 if abs(t - T["amina1"]) < 0.3 else 0)
            img = digital_glitch(img, g, int(t * FPS))
        else:
            if self.frozen is None:
                self.frozen = digital_glitch(camera(self.scene(T["froze"] - 0.05), 1.0, 960, 540), 0.3, 5)
            img = self.frozen.copy()
            dx, dy = shake(t, T["froze"], amp=16, dur=0.4)
            img = camera(img, 1.02, 960 + dx, 540 + dy)
            if t >= T["rewound"]:  # перемотка
                k = (t - T["rewound"]) * 3
                img = np.roll(img, int(k * 140) % H, axis=0)
                cv2.putText(img, "<<", (90, 160), cv2.FONT_HERSHEY_SIMPLEX, 3, (230, 230, 230), 8, AA)
            if t >= T["instead"]:
                img = digital_glitch(img, 0.9, int(t * FPS))
            if t >= T["dont"]:
                img = cv2.convertScaleAbs(img, alpha=0.18)
                paste_rgba(img, self.warn, 0, 0)
        # интерфейс плеера
        cv2.rectangle(img, (60, H - 140), (W - 60, H - 132), (90, 90, 96), -1)
        prog = min(1.0, (t - self.t0) / 47.0)
        cv2.rectangle(img, (60, H - 140), (int(60 + (W - 120) * prog), H - 132), (230, 230, 235), -1)
        if int(t * 2) % 2 == 0 and t < T["froze"]:
            cv2.circle(img, (90, 80), 12, (40, 40, 220), -1, AA)
        return img


class LivingWide(Shot):
    """Гостиная: чужой телефон на диване, Арман стоит в стороне. mode: drop | still | sofa | corner | beam | stand | voice."""

    def __init__(self, t0, t1, mode="drop"):
        super().__init__(t0, t1)
        self.mode = mode
        self.room = living_dark()

    def frame(self, t):
        img = self.room.copy()
        m = self.mode
        if m in ("drop", "still", "stand"):
            foreign_on_sofa(img, glow=0.6 if m == "drop" else 0.3)
            arman_back(img, 1240, 1000, 620, arms_forward=(m != "stand"))
            if m == "drop":
                z = lerp(1.7, 1.0, ease((t - self.t0) / 0.6))
                dx, dy = shake(t, T["vibr"], amp=8, dur=0.3, freq=40)
                return camera(img, z, lerp(SOFA_PHONE[0], 960, ease((t - self.t0) / 0.6)) + dx, lerp(SOFA_PHONE[1], 540, ease((t - self.t0) / 0.6)) + dy)
            if m == "stand":
                return camera(img, 1.0 + 0.04 * self.k(t), 960, 540)
            return camera(img, 1.1, 1000, 600)
        if m in ("sofa", "corner"):
            foreign_on_sofa(img, glow=0.5)
            return camera(img, 2.2 + 0.15 * ease(self.k(t)), SOFA_PHONE[0] + 40, SOFA_PHONE[1] - 80)
        if m == "beam":  # резкий поворот фонарика в угол — пусто
            k = ease(min(1.0, (t - self.t0) / 0.5))
            fx = lerp(1700, SOFA_PHONE[0] - 120, k)
            img = apply_light(img, to_lmap(np.full((H, W, 3), 1.0, np.float32) + blob(H, W, fx, 700, 300, 260, (2.2, 2.4, 2.6))))
            foreign_on_sofa(img, glow=0.3)
            return camera(img, 1.25, lerp(1300, 700, k), 600)
        if m == "voice":  # чужой телефон сам включается: голосовое сообщение
            on = T["voice"] <= t < T["dont_meet"]
            if on:
                kk = (t - T["voice"]) / (T["dont_meet"] - T["voice"])
                lv = [abs(math.sin(i * 0.9 + t * 5)) * (0.3 + 0.7 * ((i * 5 + int(t * 12)) % 7) / 7) for i in range(40)]
                foreign_on_sofa(img, PH.to_bgr(PH.screen_voice(lv, kk)), glow=1.0)
            else:
                foreign_on_sofa(img, glow=0.0)
            jerk = ramp(t, T["voice"], T["voice"] + 0.25)
            return camera(img, lerp(1.6, 3.2, jerk), SOFA_PHONE[0] + 30 * jerk, SOFA_PHONE[1] - 40 * jerk)
        raise ValueError(m)


class Chat(Shot):
    """1:36 Свой телефон: переписка с неизвестным номером, затем фото окна."""

    def __init__(self, t0, t1, part=1):
        super().__init__(t0, t1)
        self.part = part
        self.ph = PhoneHands(t0, t1, living_dark(), self.scr, shakes=(T["vibr"], T["vibr"] + 0.4) if part == 1 else (),
                             zoom=lambda t: (1.0 + 0.18 * ease(self.k(t)), -40 * ease(self.k(t))))
        self.window_photo = Opposite(seed=52).frame(0.0, figure=True)

    def scr(self, t):
        m = []
        if t >= T["msg1"]:
            m.append(("in", "ТЫ УЖЕ НАРУШИЛ ПЕРВОЕ ПРАВИЛО"))
        typing = None
        if T["typed0"] <= t < T["sent"]:
            n = int(len("Кто ты?") * min(1.0, (t - T["typed0"]) / 0.9))
            typing = "Кто ты?"[:n]
        if t >= T["sent"]:
            m.append(("out", "Кто ты?"))
        if t >= T["reply"]:
            m.append(("in", "ТЫ ЗНАЕШЬ МЕНЯ ЛУЧШЕ ВСЕХ"))
        if self.part == 2:
            m = [("in", "ТЫ ЗНАЕШЬ МЕНЯ ЛУЧШЕ ВСЕХ"), ("photo", self.window_photo)]
        key = ("chat", self.part, len(m), typing)
        return sprite(key, lambda: PH.screen_chat(UNKNOWN, m, typing))

    def frame(self, t):
        img = self.ph.frame(t)
        if T["msg1"] - 2.4 <= t < T["msg1"] - 2.2 and self.part == 1:
            img = cv2.convertScaleAbs(img, alpha=1.7)
        return img


class WindowPhoto(Shot):
    """1:50 Фото окна с улицы на весь экран; зум к силуэту — это я."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.o = Opposite(seed=52)

    def frame(self, t):
        hl = ramp(t, T["was_me"], T["was_me"] + 0.6)
        img = self.o.frame(0.0, figure=True, highlight=hl)
        x0, y0, x1, y1 = Opposite.WIN
        k = ramp(t, T["zoomed"], T["zoomed"] + 2.5)
        img = camera(img, lerp(1.0, 4.2, k), lerp(960, (x0 + x1) / 2, k), lerp(540, (y0 + y1) / 2 + 10, k))
        if k > 0.6:  # цифровое увеличение: зерно крупнее
            small = cv2.resize(img, (W // 3, H // 3), interpolation=cv2.INTER_AREA)
            img = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
        return img


class Call(Shot):
    """2:13 Звонок: «Скрытый номер», затем волна голоса на тёмном фоне, имя «АМИНА»."""

    def __init__(self, t0, t1, mode="ring"):
        super().__init__(t0, t1)
        self.mode = mode
        if mode in ("ring", "ended"):
            self.ph = PhoneHands(t0, t1, living_dark(), self.scr, zoom=lambda t: (1.0 + 0.15 * ease(self.k(t)), -30 * ease(self.k(t))))
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_text(im, (0, 200), "АМИНА", 120, (240, 240, 244, 255), "bold", max_w=W, align="center")
        self.name = pil_to_bgra(im)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_text(im, (0, 110), "СКРЫТЫЙ НОМЕР", 40, (150, 150, 158, 255), "bold", max_w=W, align="center")
        self.hidden = pil_to_bgra(im)
        self.rng = np.random.default_rng(3)

    def scr(self, t):
        if self.mode == "ring":
            return sprite("ring", lambda: PH.screen_call_incoming("Скрытый номер"))
        if t < T["cut"] + 0.6:
            return sprite("incall", lambda: PH.screen_call_incoming("Скрытый номер", "на линии", in_call=True))
        if t < T["cut"] + 2.4:
            return sprite("ended", PH.screen_call_ended)
        return sprite("f_off", PH.screen_off)

    def frame(self, t):
        if self.mode in ("ring", "ended"):
            return self.ph.frame(t)
        img = np.zeros((H, W, 3), np.uint8)
        img[:] = (10, 9, 9)
        xs = np.arange(0, W, 6)
        amp = 120 * ENV[min(int(t * FPS), len(ENV) - 1)] + 8
        ys = 600 + np.sin(xs * 0.025 + t * 9) * amp * np.sin(xs * 0.004 + t) + self.rng.normal(0, 4, len(xs))
        pts = np.stack([xs, ys], 1).astype(np.int32)
        cv2.polylines(img, [pts], False, (200, 205, 210), 3, AA)
        cv2.polylines(img, [pts], False, (90, 92, 96), 9, AA)
        cv2.polylines(img, [pts], False, (200, 205, 210), 3, AA)
        paste_rgba(img, self.hidden, 0, 0)
        if t >= T["name"]:
            paste_rgba(img, self.name, 0, 0, ramp(t, T["name"], T["name"] + 0.5))
        sec = int(t - T["noise"])
        cv2.putText(img, f"00:{sec:02d}", (W // 2 - 70, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (140, 140, 146), 3, AA)
        g = 0.2
        if T["seven"] <= t < T["seven"] + 0.25:
            g = 1.0
        img = digital_glitch(img, g, int(t * FPS))
        if T["seven"] + 0.25 <= t < T["seven"] + 0.75:
            return np.zeros((H, W, 3), np.uint8)
        return img


class RadioPhoto(Shot):
    """2:57 Фото из будущего: радиостанция, двое со спины, табличка, дата, подпись, третий в окне."""

    def __init__(self, t0, t1, mode="msg"):
        super().__init__(t0, t1)
        self.mode = mode
        self.plain = RD.date_stamp(RD.radio_station(0.0, 0.0), DATE)
        self.hl = RD.date_stamp(RD.radio_station(0.0, 1.0), DATE)
        self.third = RD.date_stamp(RD.radio_station(1.0, 0.0), DATE)
        if mode == "msg":
            self.ph = PhoneHands(t0, t1, living_dark(), lambda t: sprite("radio_msg", lambda: PH.screen_chat(UNKNOWN, [("photo", self.plain)])),
                                 zoom=lambda t: (1.0 + 0.2 * ease(self.k(t)), -30))
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_text(im, (0, 905), CAPTION, 64, (235, 50, 44, 255), "bold", max_w=W, align="center")
        self.cap = pil_to_bgra(im)

    def frame(self, t):
        if self.mode == "msg":
            img = self.ph.frame(t)
            if t < self.t0 + 0.2:
                img = cv2.convertScaleAbs(img, alpha=1.6)
            return img
        if self.mode == "photo":
            src = self.hl if t >= T["amina2"] else self.plain
            k_sign = ramp(t, T["sign"], T["sign"] + 1.2)
            k_wide = ramp(t, T["radio"], T["radio"] + 1.0) * (1 - k_sign)
            z = lerp(1.25, 1.0, k_wide) if k_sign == 0 else lerp(1.0, 2.6, k_sign)
            cx = lerp(980, 960, k_wide) if k_sign == 0 else lerp(960, 950, k_sign)
            cy = lerp(700, 540, k_wide) if k_sign == 0 else lerp(540, 500, k_sign)
            return camera(src, z, cx, cy)
        if self.mode == "date":
            k = ramp(t, self.t0, T["tomorrow"] + 0.3)
            if t < T["caption"]:
                return camera(self.hl, lerp(1.0, 2.6, k), lerp(960, W - 330, k), lerp(540, H - 90, k))
            # фото карточкой сверху, под ним красная подпись
            kk = ramp(t, T["caption"], T["caption"] + 0.6)
            img = np.zeros((H, W, 3), np.uint8)
            card = cv2.resize(self.hl, (int(W * 0.74), int(H * 0.74)))
            y0 = int(lerp(-200, 60, kk))
            x0 = (W - card.shape[1]) // 2
            img[max(0, y0):y0 + card.shape[0], x0:x0 + card.shape[1]] = card[max(0, -y0):]
            paste_rgba(img, self.cap, 0, 0, kk)
            return img
        # dark window: третий силуэт проявляется
        a = ramp(t, T["another"], T["another"] + 1.6)
        src = cv2.addWeighted(self.plain, 1 - a, self.third, a, 0)
        x0, y0, x1, y1 = RD.WINDOW
        k = ease(self.k(t))
        return camera(src, lerp(1.4, 4.0, k), lerp(1100, (x0 + x1) / 2, k), lerp(560, (y0 + y1) / 2 + 10, k))


class KnockDoor(Shot):
    """3:44 Стук: закрытая дверь, ручка, тень под дверью. final — телефон на переднем плане."""

    def __init__(self, t0, t1, final=False):
        super().__init__(t0, t1)
        self.final = final
        img = AP.hallway_base()  # дверь закрыта
        d = AP.DOOR
        cv2.rectangle(img, (d["x0"] + 10, d["y1"] - 4), (d["x1"] - 10, d["y1"] + 4), (70, 84, 84), -1)  # свет из-под двери
        for sx in (900, 1010):  # тень ног снаружи
            cv2.rectangle(img, (sx, d["y1"] - 4), (sx + 50, d["y1"] + 4), (10, 10, 12), -1)
        self.img = apply_light(img, to_lmap(AP.hallway_lmap(flash=(960, 560, 240))))
        self.img = cv2.add(self.img, u8(blob(H, W, 960, d["y1"] + 10, 220, 30, (40, 50, 50))))
        if final:
            self.spr = sprite("own_off", PH.screen_off)

    def frame(self, t):
        if t >= T["last"]:
            return np.zeros((H, W, 3), np.uint8)
        if not self.final:
            dx, dy = shake(t, T["knock"], amp=14, dur=0.3, freq=24)
            return camera(self.img, 1.5, 1000 + dx, 560 + dy)
        img = camera(self.img, 1.1, 960, 520)
        img = cv2.GaussianBlur(img, (0, 0), 2.5)
        cv2.add(img, u8(blob(H, W, 1500, 930, 260, 200, (20, 20, 24))), dst=img)
        place_phone(img, self.spr, 1500, 930, 0.42, -12)
        return img


class EndCard(Shot):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        im = Image.new("RGB", (W, H))
        draw_text(im, (0, 470), "КОНЕЦ ВТОРОЙ СЕРИИ", 64, (225, 225, 228), "bold", max_w=W, align="center")
        draw_text(im, (0, 570), "ПРОДОЛЖЕНИЕ СЛЕДУЕТ", 34, (150, 150, 155), "semibold", max_w=W, align="center")
        self.card = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

    def frame(self, t):
        if t < self.t0 + BLACK:
            return np.zeros((H, W, 3), np.uint8)
        a = ramp(t, self.t0 + BLACK, self.t0 + BLACK + 0.8) * (1 - ramp(t, self.t1 - 0.6, self.t1))
        return cv2.convertScaleAbs(self.card, alpha=a)


def _env():
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(VOICE), "-f", "s16le", "-ac", "1", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 48000 // FPS
    n = len(a) // hop
    r = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1))
    return np.clip(r / (np.percentile(r, 95) + 1e-6), 0, 1)


ENV = _env()


class Ep(Episode):
    dur = DUR

    def shots(self):
        return [
            (HallWide, 0.0, T["turned"], {}),
            (EmptyRoom, T["turned"], 6.80, {}),
            (DoorMoves, 6.80, 12.62, {"mode": "moving"}),
            (LockChain, 12.62, 15.82, {}),
            (DoorMoves, 15.82, 20.26, {"mode": "gap"}),
            (LandingBeam, 20.26, 31.40, {}),
            (StepDown, 31.40, 35.42, {}),
            (ForeignPhone, 35.42, 44.64, {}),
            (ScreenOn, 44.64, T["play"] + 0.5, {}),
            (Video, T["play"] + 0.5, T["threw"] + 0.6, {}),
            (LivingWide, T["threw"] + 0.6, 96.04, {"mode": "drop"}),
            (Chat, 96.04, 103.04, {"part": 1}),
            (LivingWide, 103.04, 105.06, {"mode": "still"}),
            (Chat, 105.06, 107.20, {"part": 1}),
            (Chat, 107.20, 110.32, {"part": 2}),
            (WindowPhoto, 110.32, T["corner"], {}),
            (LivingWide, T["corner"], 128.48, {"mode": "corner"}),
            (LivingWide, 128.48, 133.48, {"mode": "beam"}),
            (Call, 133.48, 139.54, {"mode": "ring"}),
            (Call, 139.54, 156.52, {"mode": "wave"}),
            (LivingWide, 156.52, 160.22, {"mode": "sofa"}),
            (Call, 160.22, 173.24, {"mode": "wave"}),
            (Call, 173.24, 177.26, {"mode": "ended"}),
            (RadioPhoto, 177.26, 181.50, {"mode": "msg"}),
            (RadioPhoto, 181.50, 195.24, {"mode": "photo"}),
            (RadioPhoto, 195.24, 205.12, {"mode": "date"}),
            (RadioPhoto, 205.12, 213.92, {"mode": "window"}),
            (LivingWide, 213.92, T["dont_meet"] + 0.15, {"mode": "voice"}),
            (LivingWide, T["dont_meet"] + 0.15, 224.24, {"mode": "stand"}),
            (KnockDoor, 224.24, 225.76, {}),
            (KnockDoor, 225.76, AUDIO, {"final": True}),
            (EndCard, AUDIO, DUR, {}),
        ]

    def post_params(self, t):
        g = 0.0
        for tg, d, k in ((T["lit"], 0.2, 0.5), (T["msg1"] - 2.4, 0.2, 0.4), (T["voice"], 0.25, 0.6), (T["off"], 0.2, 0.5)):
            if tg <= t < tg + d:
                g = max(g, k)
        return 1.0, g


def make_ep():
    return Ep()


# ======================= ЗВУК =======================
def build_audio(out_wav):
    tr = SND.Track(DUR)
    music = SND.Track(DUR)
    music.add(0, SND.drone(DUR, base=49.0), 0)
    music.gain_curve([(0, -40), (20, -36), (48, -34), (T["amina1"], -32), (T["amina1"] + 0.05, -80), (T["amina1"] + 0.6, -30),
                      (T["froze"], -30), (T["froze"] + 0.03, -90), (T["dont"], -90), (T["dont"] + 0.3, -32), (110, -34),
                      (128, -42), (133.5, -40), (177, -40), (181.5, -32), (205, -30), (209, -40), (215.7, -50),
                      (T["last"], -50), (T["last"] + 0.01, -120), (DUR + 1, -120)])
    tr.x += music.x
    tr.add(T["creak"], SND.creak(2.8), -24)
    tr.add(0.0, SND.tv_crackle(31), -46)
    t = 20.26 + 0.0
    while t < 31.4:  # щелчки мигающей лампы: ровно раз в секунду
        tr.add(math.floor(t) + 0.0, SND.lamp_click(), -26)
        tr.add(math.floor(t) + 0.6, SND.lamp_click(), -30)
        t += 1.0
    tr.add(T["lit"], SND.vibration(0.45), -16)
    tr.add(T["lit"] + 0.5, SND.key_click(), -18)
    tr.add(T["play"], SND.key_click(), -16)
    for tg in (T["entered"] + 0.2, T["amina1"]):
        tr.add(tg, SND.static_burst(0.4), -26)
    tr.add(48.7, SND.tv_crackle(T["froze"] - 48.7, 0.6), -42)
    tr.add(T["froze"], SND.static_burst(0.5), -20)
    tr.add(T["rewound"], SND.rewind(T["instead"] - T["rewound"] + 0.3), -26)
    tr.add(T["instead"], SND.static_burst(T["dont"] - T["instead"]), -24)
    tr.add(T["dont"], SND.low_hit(), -12)
    tr.add(T["threw"] + 0.7, SND.soft_thud(), -14)
    for tv in (T["vibr"], T["vibr"] + 0.4):
        tr.add(tv, SND.vibration(), -16)
    tr.add(T["msg1"] - 0.1, SND.ping(), -24)
    for i in range(7):
        tr.add(T["typed0"] + i * 0.13, SND.key_click(), -20)
    tr.add(T["reply"] - 0.1, SND.ping(), -24)
    for tk in (99.5, 104.0, 108.5):
        tr.add(tk, SND.knock(), -30)  # редкие приглушённые удары
    tr.add(T["photo"], SND.ping(), -24)
    tr.add(110.3, SND.wind(133.5 - 110.3), -34)
    tr.add(T["ring"], SND.ringtone(139.5 - T["ring"]), -22)
    tr.add(139.54, SND.line_hiss(T["cut"] - 139.54 + 0.4), -36)
    tr.add(T["seven"], SND.static_burst(0.3), -18)
    tr.add(T["cut"] + 0.3, SND.busy_beeps(3), -24)
    tr.add(T["new_msg"], SND.ping(), -22)
    tr.add(181.5, SND.long_tone(213.9 - 181.5), -30)
    tr.add(T["off"], SND.tv_off(), -20)
    tr.add(T["voice"], SND.static_burst(0.4), -22)
    tr.add(T["voice"], SND.line_hiss(T["dont_meet"] - T["voice"]), -38)
    tr.add(T["dont_meet"] + 0.1, SND.tv_off(), -18)
    tr.add(T["knock"], SND.knock(), -6)
    tr.add(T["last"], SND.low_hit(), -10)
    cut = int((T["last"] + 1.6) * SND.SR)
    tr.x[cut:] = 0
    tr.write(out_wav.with_suffix(".fx.wav"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(VOICE), "-i", str(out_wav.with_suffix(".fx.wav")),
                    "-filter_complex", "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[v];[1:a]aresample=48000[f];"
                    "[v][f]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "[a]", "-t", f"{DUR:.3f}", "-ac", "2", str(out_wav)], check=True)


def main():
    test = "--test" in sys.argv
    work = HERE
    wav = work / "mix.wav"
    t0 = time.perf_counter()
    build_audio(wav)
    evts = SUB.events(SEG, FIXES)
    SUB.write_srt(evts, work / f"СЕРИЯ_{NUM}.srt")
    ass = work / "subs.ass"
    SUB.write_ass(evts, ass)
    if test:
        out = work / "test_10s.mp4"
        sec = render(make_ep, DUR, out, wav, ass, work / "_chunks", 44.0, 54.0)
        print(f"Тест 10 с готов за {sec:.0f} с: {out}")
        return
    out = work / f"СЕРИЯ_{NUM}.mp4"
    sec = render(make_ep, DUR, out, wav, ass, work / "_chunks")
    shutil.copy2(out, desktop() / f"СЕРИЯ_{NUM}.mp4")
    shutil.copy2(work / f"СЕРИЯ_{NUM}.srt", desktop() / f"СЕРИЯ_{NUM}.srt")
    print(f"Серия готова за {time.perf_counter() - t0:.0f} с (видео {sec:.0f} с): {desktop() / f'СЕРИЯ_{NUM}.mp4'}")


if __name__ == "__main__":
    main()
