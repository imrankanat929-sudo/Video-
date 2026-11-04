"""Синтез звука кодом: эмбиент, гул, сирены, помехи, удары, вибрация, скрип.

Все функции возвращают моно float32 при SR=48000. Собирает Track.add(t, сигнал, громкость).
"""
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.01, r=0.2):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, cutoff):
    """Однополюсный ФНЧ (быстрый, без scipy)."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    # векторизация через блоки фильтра IIR медленна в numpy; для коротких сигналов ок,
    # для длинных используем FFT-фильтр
    if len(x) > SR * 2:
        return fft_filter(x, 0, cutoff)
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def fft_filter(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = ((f >= lo) & (f <= hi)).astype(np.float32)
    # мягкие края
    m = np.convolve(m, np.ones(9) / 9, mode="same")
    return np.fft.irfft(X * m, n=len(x)).astype(np.float32)


def noise(dur):
    return rng.standard_normal(int(dur * SR)).astype(np.float32)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return (x / m * peak).astype(np.float32)


# ---------- звуки ----------
def drone(dur, base=55.0):
    """Тёмный эмбиент: расстроенные синусы + шумовая подложка с медленной пульсацией."""
    t = t_axis(dur)
    x = np.zeros_like(t, dtype=np.float32)
    for f, a in ((base, 1.0), (base * 1.005, 0.8), (base * 1.5, 0.35), (base * 2.01, 0.25), (base * 3.0, 0.08)):
        x += a * np.sin(2 * np.pi * f * t + rng.random() * 6)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t)
    pad = fft_filter(noise(dur), 60, 400) * 0.6
    return norm((x * lfo + pad).astype(np.float32))


def notification():
    """Резкий звук уведомления: два коротких тона."""
    out = []
    for f, d in ((1318.5, 0.11), (1760.0, 0.22)):
        t = t_axis(d)
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)) * np.exp(-t * 9)
        out.append(s * env_adsr(len(t), 0.003, 0.03))
    return norm(np.concatenate(out).astype(np.float32))


def siren(dur, period=4.0):
    """Далёкая сирена: глиссандо, сильно заглушено и размыто «расстоянием»."""
    t = t_axis(dur)
    f = 620 + 330 * (0.5 - 0.5 * np.cos(2 * np.pi * t / period))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph)
    x = fft_filter(x.astype(np.float32), 300, 1400)
    tail = np.exp(-np.arange(int(0.6 * SR)) / (0.18 * SR)) * rng.standard_normal(int(0.6 * SR)) * 0.02
    x = np.convolve(x, tail, mode="same")
    return norm(x.astype(np.float32) * env_adsr(len(x), 1.5, 1.5))


def wind(dur):
    t = t_axis(dur)
    x = fft_filter(noise(dur), 80, 700)
    g = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.047 * t + 1)
    return norm((x * g).astype(np.float32) * env_adsr(len(t), 2.0, 2.0))


def tv_crackle(dur, density=1.0):
    x = fft_filter(noise(dur), 2000, 9000) * 0.25
    clicks = (rng.random(len(x)) < 0.0004 * density).astype(np.float32) * rng.standard_normal(len(x)).astype(np.float32) * 3
    return norm((x + clicks).astype(np.float32))


def static_burst(dur):
    x = fft_filter(noise(dur), 300, 12000)
    g = (rng.random(int(dur * 30)) > 0.3).astype(np.float32)
    g = np.repeat(g, SR // 30)[: len(x)]
    g = np.pad(g, (0, len(x) - len(g)))
    return norm(x * (0.4 + 0.6 * g) * env_adsr(len(x), 0.02, 0.1))


def tv_off():
    """Щелчок кинескопа и затухающий писк."""
    t = t_axis(0.8)
    click = np.zeros_like(t)
    click[: int(0.004 * SR)] = 1
    whine = np.sin(2 * np.pi * (15000 - 6000 * t) * t) * np.exp(-t * 6) * 0.15
    thump = np.sin(2 * np.pi * 60 * t) * np.exp(-t * 20)
    return norm((click + whine + thump).astype(np.float32))


def power_cut():
    """Щелчок отключения электричества + опадающий гул сети."""
    t = t_axis(1.6)
    click = np.zeros_like(t)
    click[: int(0.006 * SR)] = rng.standard_normal(int(0.006 * SR))
    hum = (np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 100 * t)) * np.exp(-t * 3) * 0.6
    return norm((click * 1.5 + hum).astype(np.float32))


def call_fail():
    """Системный сигнал «вызов невозможен» (три восходящих тона)."""
    out = []
    for f in (913.8, 1370.6, 1776.7):
        t = t_axis(0.3)
        out.append(np.sin(2 * np.pi * f * t) * env_adsr(len(t), 0.005, 0.02))
    return norm(np.concatenate(out).astype(np.float32))


def vibration(dur=0.35):
    t = t_axis(dur)
    x = np.sign(np.sin(2 * np.pi * 160 * t)) * 0.6 + np.sin(2 * np.pi * 80 * t)
    x = fft_filter(x.astype(np.float32), 40, 600)
    return norm(x * env_adsr(len(t), 0.01, 0.05))


def low_hit():
    t = t_axis(2.5)
    f = 55 * np.exp(-t * 0.6) + 30
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    x += fft_filter(noise(2.5), 20, 200) * np.exp(-t * 8) * 0.5
    return norm(x.astype(np.float32))


def knock():
    """Глухой удар в металлическую дверь."""
    t = t_axis(0.5)
    x = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 18) + np.sin(2 * np.pi * 210 * t) * np.exp(-t * 30) * 0.4
    x += fft_filter(noise(0.5), 100, 1500) * np.exp(-t * 40) * 0.6
    return norm(x.astype(np.float32))


def creak(dur):
    """Тихий медленный скрип петель."""
    t = t_axis(dur)
    f = 190 + 50 * np.sin(2 * np.pi * 0.35 * t) + 15 * rng.standard_normal(len(t)).cumsum() / SR
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * 0.5 + np.sin(ph * 2.01) * 0.3
    grains = (np.sin(2 * np.pi * 18 * t) > 0.2).astype(np.float32)
    x = fft_filter((x * (0.4 + 0.6 * grains)).astype(np.float32), 150, 2500)
    return norm(x * env_adsr(len(t), 0.4, 0.6))


def rising_tone(dur):
    t = t_axis(dur)
    f = 55 + 35 * (t / dur) ** 2
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 2.02) / SR)
    x += np.sin(2 * np.pi * np.cumsum(f * 6) / SR) * 0.08 * (t / dur)
    return norm((x * (t / dur) ** 1.5).astype(np.float32))


def tinnitus(dur):
    t = t_axis(dur)
    return norm((np.sin(2 * np.pi * 6200 * t) * env_adsr(len(t), 1.5, 1.5)).astype(np.float32))


def db(x):
    return 10 ** (x / 20)


class Track:
    def __init__(self, dur):
        self.x = np.zeros(int(dur * SR) + SR, np.float32)

    def add(self, t, sig, gain_db=0.0, fade_out=None):
        i = int(t * SR)
        if i >= len(self.x):
            return
        s = sig[: len(self.x) - i] * db(gain_db)
        self.x[i:i + len(s)] += s

    def gain_curve(self, points):
        """Огибающая громкости: [(время, дБ), ...] с линейной интерполяцией."""
        ts = np.array([p[0] for p in points]) * SR
        gs = np.array([db(p[1]) for p in points])
        g = np.interp(np.arange(len(self.x)), ts, gs)
        self.x *= g.astype(np.float32)

    def write(self, path):
        import wave
        y = np.clip(self.x, -1, 1)
        pcm = (y * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())


# ---------- серия 2 ----------
def ringtone(dur):
    """Тихий телефонный звонок: двухтональные трели с паузами."""
    t = t_axis(dur)
    tone = np.sin(2 * np.pi * 880 * t) * 0.5 + np.sin(2 * np.pi * 1320 * t) * 0.5
    trill = (np.sin(2 * np.pi * 16 * t) > 0).astype(np.float32)
    gate = ((t % 3.0) < 1.2).astype(np.float32)
    return norm((tone * trill * gate).astype(np.float32) * env_adsr(len(t), 0.02, 0.3))


def key_click():
    t = t_axis(0.04)
    x = fft_filter(noise(0.04), 2000, 8000) * np.exp(-t * 200)
    return norm(x.astype(np.float32))


def rewind(dur):
    """Цифровая перемотка: высокое «жужжание» с треском."""
    t = t_axis(dur)
    f = 300 + 900 * (t / dur)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + fft_filter(noise(dur), 1500, 7000) * 0.4
    return norm(x.astype(np.float32) * env_adsr(len(t), 0.05, 0.1))


def busy_beeps(n=3):
    out = []
    for _ in range(n):
        t = t_axis(0.35)
        out.append(np.sin(2 * np.pi * 425 * t) * env_adsr(len(t), 0.005, 0.02))
        out.append(np.zeros(int(0.35 * SR)))
    return norm(np.concatenate(out).astype(np.float32))


def soft_thud():
    t = t_axis(0.4)
    x = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 25) + fft_filter(noise(0.4), 60, 600) * np.exp(-t * 40) * 0.5
    return norm(x.astype(np.float32))


def lamp_click():
    t = t_axis(0.06)
    x = fft_filter(noise(0.06), 800, 6000) * np.exp(-t * 120) + np.sin(2 * np.pi * 100 * t) * np.exp(-t * 60) * 0.5
    return norm(x.astype(np.float32))


def line_hiss(dur):
    t = t_axis(dur)
    x = fft_filter(noise(dur), 300, 3400) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.3 * t))
    return norm(x.astype(np.float32) * env_adsr(len(t), 0.3, 0.3))


def ping():
    t = t_axis(0.5)
    x = (np.sin(2 * np.pi * 1046.5 * t) + 0.4 * np.sin(2 * np.pi * 2093 * t)) * np.exp(-t * 7)
    return norm(x.astype(np.float32))


def long_tone(dur):
    t = t_axis(dur)
    x = np.sin(2 * np.pi * 73.4 * t) + 0.5 * np.sin(2 * np.pi * 110 * t + 1) + 0.15 * np.sin(2 * np.pi * 146.8 * t)
    return norm(x.astype(np.float32) * env_adsr(len(t), 3.0, 1.5))
