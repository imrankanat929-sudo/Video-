"""«Последний сигнал», серия 1 — «03:17».

Запуск:
  python episode.py --test     10-секундный тест (0:00–0:10) → test_10s.mp4
  python episode.py            полная серия → Рабочий стол/СЕРИЯ_1.mp4 + СЕРИЯ_1.srt
"""
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "library"))

import apartment as AP  # noqa: E402
import phone as PH  # noqa: E402
import sound as SND  # noqa: E402
import subs as SUB  # noqa: E402
from characters import arman_back, arman_sitting, hands_holding  # noqa: E402
from city import CityView, Opposite  # noqa: E402
from clock import ClockClose  # noqa: E402
from core import (AA, FPS, H, W, blob, camera, desktop, draw_text, ease, gradient, lerp, paste_rgba,  # noqa: E402
                  pil_to_bgra, ramp, shake, to_lmap, u8, warp_rgba, apply_light)
from engine import Episode, render  # noqa: E402
from tv import News, collapse  # noqa: E402

NUM = 1
VOICE = HERE / "voice.mp3"
TAIL = 4.0  # тишина + «КОНЕЦ ПЕРВОЙ СЕРИИ / ПРОДОЛЖЕНИЕ СЛЕДУЕТ»

MSG1 = "АРМАН, НЕ ВЫХОДИ ИЗ ДОМА. ТРЕТЬЯ МИРОВАЯ УЖЕ НАЧАЛАСЬ."
MSG2 = "АРМАН, НЕ СМОТРИ В ОКНО. ОНА УЖЕ ЗАМЕТИЛА ТЕБЯ."
MSG3 = "НЕ ОТКРЫВАЙ ДВЕРЬ. Я УЖЕ ВНУТРИ."
UNKNOWN = "Неизвестный номер"

FIXES = {"3.17": "три семнадцать", "произнес": "произнёс", "во всем": "во всём", "подошел": "подошёл",
         "погружен ": "погружён ", "освещения": "освещение", "черная": "чёрная", "Подошел": "Подошёл"}


def audio_len(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


SEG = SUB.transcribe(VOICE, HERE / "transcript.json")
AUDIO = audio_len(VOICE)
DUR = AUDIO + TAIL
wt = lambda p, after=0.0, end=False: SUB.word_time(SEG, p, after, end)  # noqa: E731

# ключевые моменты синхронизации (по пословным таймкодам)
T = dict(
    tv_on=wt("включил", 14), crawl=wt("чрезвычайное", 19), look=wt("посмотрел", 29), tv_off=wt("выключился", 38),
    power=wt("электричество", 41), dark=wt("погружен", 45), street=wt("фонари", 47), sirens=wt("сирены", 52),
    call_fail=wt("связи", 55), no_net=wt("интернет", 57), zoom=wt("приблизил", 70), cold=wt("похолодели", 73),
    hoodie=wt("толстовка", 76), lowered=wt("опустил", 80), nobody=wt("никого", 80), vibr=wt("завибрировал", 84),
    knock=wt("удара", 97), peep=wt("коридор", 103), own=wt("собственный", 111), record=wt("запись", 116),
    screen_off=wt("погас", 118), new_msg=wt("новое", 119), turn=wt("обернулся", 126), door=wt("начала", 130),
    opening=wt("открываться", 130), last=SEG[-1]["end"],
)
KNOCKS = [T["knock"] + 0.05, T["knock"] + 0.6, T["knock"] + 1.15]


# ======================= ПЛАНЫ =======================
class Shot:
    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1

    def k(self, t):
        return (t - self.t0) / max(1e-6, self.t1 - self.t0)


_SPR = {}


def phone_spr(key, maker):
    if key not in _SPR:
        _SPR[key] = PH.phone_sprite(PH.to_bgr(maker()))
    return _SPR[key]


def place_phone(img, spr, cx, cy, scale, angle=0.0, alpha=1.0):
    s = warp_rgba(spr, scale, angle)
    paste_rgba(img, s, cx - s.shape[1] / 2, cy - s.shape[0] / 2, alpha)


class PhoneNightstand(Shot):
    """0:00 Телефон на тумбочке в темноте. Экран вспыхивает: сообщение."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        rng = np.random.default_rng(2)
        n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), sigmaX=60, sigmaY=2)
        wood = np.clip(22 + n * 30, 8, 40)
        self.bg = cv2.merge([wood * 1.1, wood * 1.0, wood * 0.95]).astype(np.uint8)
        self.spr = phone_spr("msg1", lambda: PH.screen_lock_notification("Сообщение", MSG1))
        self.dark = PH.phone_sprite(PH.to_bgr(PH.screen_off()))
        self.light = blob(H, W, 960, 540, 520, 600, (1.6, 1.4, 1.2))

    def frame(self, t):
        on = t >= self.t0 + 0.07
        flash = 1.0 + (0.8 * math.exp(-(t - self.t0) * 6) if on else 0)
        lm = to_lmap(0.25 + self.light * (flash if on else 0.05))
        img = cv2.multiply(self.bg, lm, scale=1 / 128)
        place_phone(img, self.spr if on else self.dark, 960, 540, 0.66, -6)
        dx, dy = shake(t, self.t0 + 0.07, amp=18)
        k = ease(self.k(t))
        return camera(img, 1.0 + 0.32 * k, 960 + dx, lerp(540, 470, k) + dy)


class BedSit(Shot):
    """0:08 Арман резко садится на кровати."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.base = AP.bedroom_base()
        self.lm = to_lmap(AP.bedroom_lmap(1.0))
        self.glow = u8(blob(H, AP.BED_W, *AP.BED["phone"], 30, 20, (120, 110, 100)))

    def frame(self, t):
        img = self.base.copy()
        k = ramp(t, self.t0 + 0.15, self.t0 + 0.8)
        arman_sitting(img, 560, 690, 520, k, glow=(110, 100, 92))
        img = apply_light(img, self.lm, self.glow)
        dx, dy = shake(t, self.t0 + 0.2, amp=8, dur=0.4)
        return camera(img, 1.25 + 0.04 * self.k(t), 820 + dx, 560 + dy)


class Clock(Shot):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.c = ClockClose()

    def frame(self, t):
        return camera(self.c.frame(t), 1.0 + 0.06 * ease(self.k(t)), 960, 555)


NEWS = None


def news():
    global NEWS
    if NEWS is None:
        NEWS = News()
    return NEWS


class BedroomPan(Shot):
    """0:15 Панорама от кровати к телевизору в соседней комнате — он загорается."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.base = AP.bedroom_base()
        lm = AP.bedroom_lmap(1.0)
        t = AP.BED["tv"]
        self.lm_off = to_lmap(lm)
        self.lm_on = to_lmap(lm + blob(H, AP.BED_W, (t[0] + t[2]) / 2, (t[1] + t[3]) / 2 + 60, 220, 260, (1.3, 0.9, 0.6)))

    def frame(self, t):
        img = self.base.copy()
        arman_sitting(img, 560, 690, 520, 1.0, glow=(110, 100, 92))
        on = ramp(t, T["tv_on"], T["tv_on"] + 0.4)
        x0, y0, x1, y1 = AP.BED["tv"]
        if on > 0:
            scr = cv2.resize(news().frame(t), (x1 - x0, y1 - y0))
            img[y0:y1, x0:x1] = cv2.convertScaleAbs(scr, alpha=on * (0.9 + 0.1 * math.sin(t * 13)))
        img = apply_light(img, cv2.addWeighted(self.lm_off, 1 - on, self.lm_on, on, 0))
        k = ease(self.k(t))
        return camera(img, lerp(1.0, 1.35, k), lerp(900, 2150, k), lerp(540, 560, k))


class TVClose(Shot):
    """ТВ крупно в тёмной гостиной. mode: news | glitch | warning | off."""

    def __init__(self, t0, t1, mode="news"):
        super().__init__(t0, t1)
        self.mode = mode
        img = gradient(H, W, (24, 22, 22), (14, 13, 13))
        cv2.rectangle(img, (230, 110), (1690, 950), (9, 9, 10), -1)
        cv2.rectangle(img, (180, 950), (1740, H), (20, 22, 28), -1)
        self.bg = img
        self.scr = (260, 140, 1660, 928)
        self.spill = blob(H, W, 960, 540, 1100, 700, (1.0, 0.8, 0.6))

    def screen(self, t):
        n = news()
        if self.mode == "news":
            return n.frame(t, crawl_t0=T["crawl"])
        if self.mode == "glitch":
            g = 0.15 + 0.5 * ramp(t, self.t0, self.t1) * (0.5 + 0.5 * math.sin(t * 9))
            look = ramp(t, T["look"], T["look"] + 0.8)
            return n.frame(t, crawl_t0=T["crawl"], glitch=g, look=look, freeze_t=T["look"] + 0.8)
        if self.mode == "warning":
            return n.frame(t, warning=True)
        # off
        k = (t - T["tv_off"]) / 0.55
        if k < 0:
            return n.frame(t, warning=True)
        return collapse(n.frame(T["tv_off"], warning=True), min(1.0, k))

    def frame(self, t):
        img = self.bg.copy()
        x0, y0, x1, y1 = self.scr
        s = self.screen(t)
        img[y0:y1, x0:x1] = cv2.resize(s, (x1 - x0, y1 - y0))
        lvl = float(s.mean()) / 90
        img = apply_light(img, to_lmap(0.6 + self.spill * lvl * 0.5))
        z = 1.0 + 0.08 * ease(self.k(t))
        if self.mode == "news":
            z = 1.0 + 0.10 * ease(self.k(t))
        if self.mode in ("glitch", "warning"):
            z = 1.1 + 0.12 * ease(self.k(t))
        if self.mode == "off":
            z = 1.22
        return camera(img, z, 960, 534)


class Blackout(Shot):
    """0:41 Гостиная. На «электричество» — щелчок, весь кадр чёрный 1 с, затем лишь лунный свет."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.base = AP.living_base(city_lit=True)
        lm = np.full((H, W, 3), 0.35, np.float32) + blob(H, W, 1750, 500, 500, 600, (1.0, 0.8, 0.55))  # свет из прихожей
        self.lit = apply_light(self.base, to_lmap(lm))
        moon = np.full((H, W, 3), 0.28, np.float32) + blob(H, W, 1580, 600, 420, 500, (0.25, 0.32, 0.45))
        self.dark = apply_light(self.base, to_lmap(moon))

    def frame(self, t):
        z = 1.0 + 0.04 * self.k(t)
        if t < T["power"]:
            return camera(self.lit, z, 960, 540)
        if t < T["power"] + 1.0:
            return np.zeros((H, W, 3), np.uint8)
        return camera(self.dark, z, 960, 540)


class City(Shot):
    """0:44 Город без света: окна гаснут, фонари и светофоры гаснут, мигает аварийный огонь."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.c = CityView(T["dark"], T["dark"] + 2.6, T["street"])

    def frame(self, t):
        return camera(self.c.frame(t, ease(self.k(t))), 1.02, 960, 540)


def handheld_bg(img_fn):
    return img_fn


class Handheld(Shot):
    """Телефон в руках Армана. screens(t) → (ключ, фабрика экрана) или живой кадр."""

    def __init__(self, t0, t1, scene="nosignal"):
        super().__init__(t0, t1)
        self.scene = scene
        if scene in ("nosignal",):
            bg = CityView(-10, -9, -10).frame(999, 0.5)
        elif scene in ("camera", "vibrate", "message"):
            bg = Opposite().frame(0, figure=False)
        else:  # у двери
            bg = apply_light(AP.hallway_base(), to_lmap(AP.hallway_lmap(flash=(960, 500, 300))))
        bg = cv2.GaussianBlur(bg, (0, 0), 9)
        self.bg = cv2.convertScaleAbs(bg, alpha=0.55)
        self.opp = Opposite() if scene == "camera" else None
        self.pw, self.ph = PH.PW * 0.7, PH.PH * 0.7

    def screen_spr(self, t):
        s = self.scene
        if s == "nosignal":
            if t < T["call_fail"]:
                return phone_spr("dial", lambda: PH.screen_call("dial"))
            if t < T["no_net"]:
                return phone_spr("fail", lambda: PH.screen_call("fail"))
            return phone_spr("failnet", lambda: PH.screen_call("fail_net"))
        if s == "vibrate":
            if t < T["vibr"]:
                return phone_spr("off", PH.screen_off)
            return phone_spr("incoming", lambda: PH.screen_incoming(UNKNOWN, "Новое сообщение"))
        if s == "message":
            return phone_spr("msg2", lambda: PH.screen_message(UNKNOWN, MSG2))
        if s == "record":
            sec = max(0, int(t - T["record"]))
            if t >= T["screen_off"]:
                if t < T["new_msg"]:
                    return phone_spr("off", PH.screen_off)
                return phone_spr("msg3", lambda: PH.screen_message(UNKNOWN, MSG3))
            lv = [abs(math.sin(i * 0.7 + t * 3)) * (0.2 + 0.8 * ((i * 7 + int(t * 10)) % 5) / 5) for i in range(40)]
            return PH.phone_sprite(PH.to_bgr(PH.screen_recorder(sec, lv)))
        if s == "camera":
            return PH.phone_sprite(self.viewfinder(t))
        raise ValueError(s)

    def viewfinder(self, t):
        z = 1.0
        if t >= T["zoom"]:
            z = 3.0 if t < T["cold"] else 10.0
            z_prev = 1.0 if t < T["cold"] else 3.0
            t_step = T["zoom"] if t < T["cold"] else T["cold"]
            z = lerp(z_prev, z, ease((t - t_step) / 0.35))
        hl = ramp(t, T["hoodie"], T["hoodie"] + 0.5)
        world = self.opp.frame(t, figure=True, highlight=hl)
        x0, y0, x1, y1 = Opposite.WIN
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 8
        ch = min(1080 / z * 0.9, 1000)
        cw = ch * PH.SW / PH.SH
        crop = world[int(max(0, cy - ch / 2)):int(cy + ch / 2), int(max(0, cx - cw / 2)):int(cx + cw / 2)]
        if z > 4:  # цифровой зум: грубые пиксели и шум
            small = cv2.resize(crop, (max(8, int(crop.shape[1] / 3)), max(8, int(crop.shape[0] / 3))), interpolation=cv2.INTER_AREA)
            crop = cv2.resize(small, (crop.shape[1], crop.shape[0]), interpolation=cv2.INTER_LINEAR)
        vf = cv2.resize(crop, (PH.SW, PH.SH))
        vf = cv2.add(vf, u8(np.random.default_rng(int(t * 30)).normal(0, 6 + z, (PH.SH, PH.SW, 1)).repeat(3, 2)))
        label = "1x" if z < 2 else ("3x" if z < 6 else "10x")
        box = None
        if hl > 0:
            box = (PH.SW * 0.3, PH.SH * 0.3, PH.SW * 0.7, PH.SH * 0.72)
        ui = PH.camera_ui(label, box)
        paste_rgba(vf, ui, 0, 0)
        return vf

    def frame(self, t):
        img = self.bg.copy()
        sway_x = math.sin(t * 0.9) * 10 + math.sin(t * 2.3) * 4
        sway_y = math.sin(t * 0.7 + 1) * 8
        dx = dy = 0.0
        if self.scene == "vibrate":
            for tv in (T["vibr"], T["vibr"] + 0.45):
                ddx, ddy = shake(t, tv, amp=10, dur=0.3, freq=40)
                dx, dy = dx + ddx, dy + ddy
        if self.scene == "record":
            for tv in (T["new_msg"], T["new_msg"] + 0.45):
                ddx, ddy = shake(t, tv, amp=8, dur=0.3, freq=40)
                dx, dy = dx + ddx, dy + ddy
        cx, cy = 960 + sway_x + dx, 540 + sway_y + dy
        spr = self.screen_spr(t)
        scr_glow = u8(blob(H, W, cx, cy, 500, 520, (30, 30, 34)))
        img = cv2.add(img, scr_glow)
        place_phone(img, spr, cx, cy, 0.7, 0)
        hands_holding(img, cx, cy, self.pw, self.ph)
        z = 1.0
        if self.scene == "message":
            z = 1.0 + 0.35 * ease(self.k(t))
            return camera(img, z, cx, cy - 60 * ease(self.k(t)))
        if self.scene == "record" and t >= T["new_msg"]:
            z = 1.0 + 0.3 * ramp(t, T["new_msg"], self.t1)
            return camera(img, z, cx, cy - 60)
        return img


class OppositeView(Shot):
    """1:00 Дом напротив, одно освещённое окно, неподвижный силуэт. mode: wide | empty."""

    def __init__(self, t0, t1, mode="wide"):
        super().__init__(t0, t1)
        self.o = Opposite()
        self.mode = mode

    def frame(self, t):
        x0, y0, x1, y1 = Opposite.WIN
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if self.mode == "wide":
            k = ease(self.k(t))
            img = self.o.frame(t, figure=True)
            return camera(img, lerp(1.0, 2.0, k), lerp(960, cx, k), lerp(540, cy + 120, k))
        img = self.o.frame(t, figure=t < T["nobody"])
        return camera(img, 2.6 + 0.1 * self.k(t), cx, cy + 90)


class Hallway(Shot):
    """1:37 Тёмный коридор, дверь в глубине. mode: knocks | approach | inside | turn."""

    def __init__(self, t0, t1, mode="knocks"):
        super().__init__(t0, t1)
        self.mode = mode
        self.base = AP.hallway_base()
        self.lm_dark = to_lmap(AP.hallway_lmap())
        if mode == "turn":
            room = AP.living_base(city_lit=False)
            moon = np.full((H, W, 3), 0.3, np.float32) + blob(H, W, 1580, 600, 420, 500, (0.25, 0.32, 0.45))
            self.room = apply_light(room, to_lmap(moon))

    def frame(self, t):
        if self.mode == "knocks":
            img = apply_light(self.base, self.lm_dark)
            dx = dy = 0.0
            for tk in KNOCKS:
                a, b = shake(t, tk, amp=12, dur=0.25, freq=22)
                dx, dy = dx + a, dy + b
            return camera(img, 1.0 + 0.05 * self.k(t), 960 + dx, 540 + dy)
        if self.mode == "approach":
            k = ramp(t, self.t0 + 0.8, self.t1 - 0.2)  # «Я замер» — стоит, затем идёт к двери
            x, yf, h = 960, lerp(1250, 1000, k), lerp(980, 640, k)
            fx, fy, r = 960, lerp(700, 470, k), lerp(380, 220, k)
            img = apply_light(self.base, to_lmap(AP.hallway_lmap(flash=(fx, fy, r))))
            arman_back(img, x, yf, h, arms_forward=True)
            return camera(img, 1.0 + 0.1 * k, 960, 540)
        if self.mode == "inside":
            img = apply_light(self.base, to_lmap(AP.hallway_lmap(flash=(960, 520, 260))))
            return camera(img, 1.15 + 0.25 * ease(self.k(t)), 960, 520)
        if self.mode == "stepback":
            k = ease(self.k(t))
            img = apply_light(self.base, to_lmap(AP.hallway_lmap(flash=(960, 520, lerp(240, 320, k)))))
            arman_back(img, 960, lerp(1020, 1240, k), lerp(680, 960, k), arms_forward=True)
            return camera(img, 1.2 - 0.15 * k, 960, 540)
        # turn: дверь → резкий поворот → пустая комната
        if t < T["turn"]:
            img = apply_light(self.base, to_lmap(AP.hallway_lmap(flash=(960, 520, 300))))
            return camera(img, 1.35, 960, 520)
        k = (t - T["turn"]) / 0.28
        if k < 1:  # смаз при повороте
            src = self.room if k > 0.5 else apply_light(self.base, self.lm_dark)
            shift = int((1 - abs(k - 0.5) * 2) * 260)
            m = np.zeros((1, max(3, shift)), np.float32)
            m[:] = 1 / m.shape[1]
            return cv2.filter2D(src, -1, m)
        return camera(self.room, 1.05 + 0.03 * ease((t - T["turn"]) / 3), 960, 540)


class Peephole(Shot):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.p = AP.Peephole()

    def frame(self, t):
        return camera(self.p.frame(t), 1.0 + 0.03 * self.k(t), 960, 540)


class LockShot(Shot):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.l = AP.LockClose()

    def frame(self, t):
        return camera(self.l.frame(t), 1.0 + 0.12 * ease(self.k(t)), 920, 420)


class DoorOpens(Shot):
    """2:11 Дверь медленно начинает открываться сама. Затем резкий обрыв в чёрное."""

    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        self.base = AP.hallway_base()
        self.lm = to_lmap(AP.hallway_lmap(flash=(960, 520, 280)))

    def frame(self, t):
        if t >= T["last"]:
            return np.zeros((H, W, 3), np.uint8)
        img = self.base.copy()
        k = ramp(t, T["opening"], T["last"]) * 0.42
        cv2.rectangle(img, (AP.DOOR["x0"], AP.DOOR["y0"]), (AP.DOOR["x1"], AP.DOOR["y1"]), (30, 28, 28), -1)
        AP.door_panel(img, k)
        img = apply_light(img, self.lm)
        return camera(img, 1.2 + 0.22 * ease(self.k(t)), 960, 530)


class EndCard(Shot):
    def __init__(self, t0, t1):
        super().__init__(t0, t1)
        from PIL import Image
        im = Image.new("RGB", (W, H))
        draw_text(im, (0, 470), "КОНЕЦ ПЕРВОЙ СЕРИИ", 64, (225, 225, 228), "bold", max_w=W, align="center")
        draw_text(im, (0, 570), "ПРОДОЛЖЕНИЕ СЛЕДУЕТ", 34, (150, 150, 155), "semibold", max_w=W, align="center")
        self.card = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

    def frame(self, t):
        a = ramp(t, self.t0 + 1.0, self.t0 + 1.8) * (1 - ramp(t, self.t1 - 0.6, self.t1))
        return cv2.convertScaleAbs(self.card, alpha=a)


class Ep(Episode):
    dur = DUR

    def shots(self):
        s = [
            (PhoneNightstand, 0.0, 8.34, {}),
            (BedSit, 8.34, 12.92, {}),
            (Clock, 12.92, 14.96, {}),
            (BedroomPan, 14.96, 19.98, {}),
            (TVClose, 19.98, 27.04, {"mode": "news"}),
            (TVClose, 27.04, 33.76, {"mode": "glitch"}),
            (TVClose, 33.76, T["tv_off"] - 0.6, {"mode": "warning"}),
            (TVClose, T["tv_off"] - 0.6, 40.84, {"mode": "off"}),
            (Blackout, 40.84, 44.16, {}),
            (City, 44.16, 54.76, {}),
            (Handheld, 54.76, 60.08, {"scene": "nosignal"}),
            (OppositeView, 60.08, 70.14, {"mode": "wide"}),
            (Handheld, 70.14, T["lowered"], {"scene": "camera"}),
            (OppositeView, T["lowered"], 83.70, {"mode": "empty"}),
            (Handheld, 83.70, 89.28, {"scene": "vibrate"}),
            (Handheld, 89.28, 97.08, {"scene": "message"}),
            (Hallway, 97.08, 100.10, {"mode": "knocks"}),
            (Hallway, 100.10, T["peep"], {"mode": "approach"}),
            (Peephole, T["peep"], 105.42, {}),
            (Hallway, 105.42, 114.74, {"mode": "inside"}),
            (Hallway, 114.74, T["record"], {"mode": "stepback"}),
            (Handheld, T["record"], 125.98, {"scene": "record"}),
            (Hallway, 125.98, 129.88, {"mode": "turn"}),
            (LockShot, 129.88, T["door"], {}),
            (DoorOpens, T["door"], AUDIO, {}),
            (EndCard, AUDIO, DUR, {}),
        ]
        return s

    def post_params(self, t):
        g = 0.0
        for tg, d, k in ((T["vibr"], 0.25, 0.5), (T["new_msg"], 0.3, 0.6), (T["power"] - 0.08, 0.1, 0.8), (T["screen_off"], 0.2, 0.5)):
            if tg <= t < tg + d:
                g = max(g, k)
        if 27.04 <= t < 38.2 and int(t * 30) % 37 < 2:
            g = max(g, 0.3)
        return 1.0, g


def make_ep():
    return Ep()


# ======================= ЗВУК =======================
def build_audio(out_wav):
    tr = SND.Track(DUR)
    d = SND.drone(DUR)
    music = SND.Track(DUR)
    music.add(0, d, 0)
    music.gain_curve([(0, -30), (32.6, -30), (33.4, -42), (38.2, -42), (38.6, -32), (T["power"], -32), (T["power"] + 0.05, -70),
                      (44.0, -70), (45.5, -33), (T["own"], -33), (T["own"] + 0.15, -90), (114.7, -90), (116.0, -38),
                      (T["new_msg"], -38), (T["new_msg"] + 0.8, -52), (AUDIO, -52), (AUDIO + 0.01, -120), (DUR + 1, -120)])
    tr.x += music.x
    tr.add(0.0, SND.notification(), -8)
    tr.add(1.2, SND.siren(12), -36)
    tr.add(T["tv_on"], SND.tv_crackle(T["tv_off"] - T["tv_on"]), -40)
    tr.add(27.04, SND.static_burst(33.76 - 27.04), -36)
    tr.add(33.76, SND.static_burst(T["tv_off"] - 33.76), -32)
    tr.add(T["tv_off"], SND.tv_off(), -16)
    tr.add(T["power"], SND.power_cut(), -12)
    tr.add(44.3, SND.wind(83.7 - 44.3), -34)
    tr.add(T["sirens"] - 0.5, SND.siren(8, 3.2), -29)
    tr.add(T["sirens"] + 1.4, SND.siren(6.5, 4.6), -33)
    tr.add(T["call_fail"], SND.call_fail(), -20)
    tr.add(70.14, SND.tinnitus(10), -46)
    for tv in (T["vibr"], T["vibr"] + 0.45, T["new_msg"], T["new_msg"] + 0.45):
        tr.add(tv, SND.vibration(), -16)
    tr.add(89.28, SND.low_hit(), -12)
    for tk in KNOCKS:
        tr.add(tk, SND.knock(), -10)
    tr.add(T["opening"], SND.creak(T["last"] - T["opening"]), -26)
    rise = SND.rising_tone(T["last"] - 125.98)
    tr.add(125.98, rise, -27)
    cut = int(T["last"] * SND.SR)
    tr.x[cut:] = 0  # резкий обрыв: дальше тишина
    tr.write(out_wav.with_suffix(".fx.wav"))
    # голос нормализуем и смешиваем; голос всегда громче
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
    srt = desktop() / f"СЕРИЯ_{NUM}.srt"
    SUB.write_srt(evts, work / f"СЕРИЯ_{NUM}.srt")
    ass = work / "subs.ass"
    SUB.write_ass(evts, ass)
    if test:
        out = work / "test_10s.mp4"
        sec = render(make_ep, DUR, out, wav, ass, work / "_chunks", 0.0, 10.0)
        print(f"Тест 10 с готов за {sec:.0f} с: {out}")
        return
    out = work / f"СЕРИЯ_{NUM}.mp4"
    sec = render(make_ep, DUR, out, wav, ass, work / "_chunks")
    shutil.copy2(out, desktop() / f"СЕРИЯ_{NUM}.mp4")
    shutil.copy2(work / f"СЕРИЯ_{NUM}.srt", srt)
    print(f"Серия готова за {time.perf_counter() - t0:.0f} с (видео {sec:.0f} с): {desktop() / f'СЕРИЯ_{NUM}.mp4'}")


if __name__ == "__main__":
    main()
