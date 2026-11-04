"""Жуткая фоновая музыка, синтезированная кодом (без чужих треков).

Инструменты: струнный «пэд» с диссонансом, музыкальная шкатулка, низкое расстроенное пианино,
сердцебиение. Всё с реверберацией. Громкость задаёт серия — музыка всегда тише голоса.
"""
import numpy as np

from sound import SR, env_adsr, fft_filter, norm, t_axis

rng = np.random.default_rng(13)


def hz(note):
    """'A4', 'C#5', 'Eb3' → частота."""
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    n = names[note[0]]
    i = 1
    if note[i] in "#b":
        n += 1 if note[i] == "#" else -1
        i += 1
    octave = int(note[i:])
    return 440.0 * 2 ** ((n + (octave - 4) * 12) / 12)


def reverb(x, sec=2.8, mix=0.45):
    """Реверберация свёрткой с затухающим шумом (через FFT)."""
    n = int(sec * SR)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / (n / 5)).astype(np.float32)
    ir = fft_filter(ir, 150, 6000)
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)].astype(np.float32)
    wet = wet / (np.max(np.abs(wet)) + 1e-9) * (np.max(np.abs(x)) + 1e-9)
    return (x * (1 - mix) + wet * mix).astype(np.float32)


def pad(dur, notes=("A2", "C3", "Eb3", "Bb3"), swell=6.0):
    """Струнный пэд: расстроенные пилы через фильтр, медленные волны громкости."""
    t = t_axis(dur)
    x = np.zeros_like(t, dtype=np.float32)
    for nt in notes:
        f = hz(nt)
        for det in (-0.004, 0.0, 0.005):
            ph = 2 * np.pi * f * (1 + det) * t + rng.random() * 6
            x += (2 * ((ph / (2 * np.pi)) % 1) - 1).astype(np.float32) * 0.3
    x = fft_filter(x, 40, 1400)
    swell_env = 0.55 + 0.45 * np.sin(2 * np.pi * t / swell - 1.5)
    return reverb(norm(x * swell_env * env_adsr(len(t), 2.5, 2.5)), 3.5, 0.5)


def music_box(melody, step=0.62, detune=0.012):
    """Музыкальная шкатулка: мелодия из нот, слегка «уплывающая» по высоте."""
    dur = len(melody) * step + 3.0
    out = np.zeros(int(dur * SR), np.float32)
    for i, nt in enumerate(melody):
        if nt is None:
            continue
        f = hz(nt) * (1 + detune * np.sin(i * 1.7))
        t = t_axis(1.8)
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
             + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12)) * np.exp(-t * 2.6)
        a = int(i * step * SR)
        out[a:a + len(s)] += s.astype(np.float32) * env_adsr(len(s), 0.002, 0.2)
    return reverb(norm(out), 3.0, 0.55)


def piano_hit(notes=("A1", "Bb1", "E2")):
    """Низкий диссонантный аккорд расстроенного пианино."""
    t = t_axis(5.0)
    x = np.zeros_like(t, dtype=np.float32)
    for nt in notes:
        f = hz(nt)
        for k, a in ((1, 1.0), (2.01, 0.5), (3.03, 0.3), (4.08, 0.15)):
            x += (a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (0.8 + k * 0.3))).astype(np.float32)
    x[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    return reverb(norm(x), 4.0, 0.5)


def heartbeat(dur, bpm0=60, bpm1=60):
    """Сердцебиение (двойной глухой удар), темп плавно меняется от bpm0 к bpm1."""
    out = np.zeros(int(dur * SR) + SR, np.float32)
    tt = 0.0
    while tt < dur:
        bpm = bpm0 + (bpm1 - bpm0) * (tt / dur)
        for off, g in ((0.0, 1.0), (0.22, 0.6)):
            t = t_axis(0.25)
            s = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 22) * g
            a = int((tt + off) * SR)
            out[a:a + len(s)] += s.astype(np.float32)
        tt += 60.0 / bpm
    return norm(fft_filter(out[: int(dur * SR)], 30, 180))


# готовые темы сериала
LULLABY = ["A5", "E5", "C5", "E5", "D#5", None, "B4", None, "A5", "E5", "C5", "B4", "A4", None, None, None]
LULLABY_SLOW = ["E5", None, "C5", None, "D#5", None, "B4", None, None, "A4", None, None]
