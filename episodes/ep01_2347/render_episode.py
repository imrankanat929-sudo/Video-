"""Серия 1 «23:47»: рендер серии 16:9 + три нарезки 9:16 для TikTok.

Запуск:  python render_episode.py путь/к/озвучке.mp3
Длина серии берётся из аудио. Всё сохраняется в
Рабочий стол/NOXARGENT_STUDIO/episodes/ep01_2347/.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scenes as S  # noqa: E402

W, H, FPS = S.W, S.H, S.FPS
HERE = Path(__file__).resolve().parent
TAIL = 3.4  # чёрный хвост с титром после последней фразы

# Нарезки TikTok: аудио делится на N равных частей, каждый разрез
# сдвигается в самую длинную паузу между фразами в пределах ±2.5 с.
TIKTOK_PARTS = 3


def tiktok_cuts(segments, dur, parts=TIKTOK_PARTS, window=2.5, shot_starts=()):
    gaps = [(a["end"], b["start"]) for a, b in zip(segments, segments[1:])]
    cuts = [0.0]
    for i in range(1, parts):
        target = dur * i / parts
        near = [g for g in gaps if abs((g[0] + g[1]) / 2 - target) <= window] or \
            [min(gaps, key=lambda g: abs((g[0] + g[1]) / 2 - target))]
        g = max(near, key=lambda g: g[1] - g[0])
        inside = [t for t in shot_starts if g[0] <= t <= g[1]]  # склейка плана внутри паузы — режем по ней
        cuts.append(round(inside[0] if inside else (g[0] + g[1]) / 2, 2))
    cuts.append(None)
    return [(cuts[i], cuts[i + 1], f"Часть {i + 1}/{parts}") for i in range(parts)]


def desktop() -> Path:
    if os.environ.get("NOX_DESKTOP"):
        return Path(os.environ["NOX_DESKTOP"])
    home = Path.home()
    for p in (home / "OneDrive" / "Desktop", home / "OneDrive" / "Рабочий стол", home / "Desktop", home / "Рабочий стол"):
        if p.is_dir():
            return p
    (home / "Desktop").mkdir(parents=True, exist_ok=True)
    return home / "Desktop"


def font(size, bold=False):
    names = (["Inter-SemiBold.otf", "arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold
             else ["Inter-Light.otf", "InterDisplay-Light.otf", "arial.ttf", "DejaVuSans.ttf"])
    dirs = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/dejavu", "C:/Windows/Fonts"]
    for n in names:
        for d in dirs:
            p = Path(d) / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def text_card(lines):
    """Текстовая плашка BGR (на чёрном), строки: (текст, размер, яркость, y)."""
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for txt, size, b, y, bold in lines:
        f = font(size, bold)
        tw = d.textlength(txt, font=f)
        d.text(((W - tw) / 2, y), txt, font=f, fill=(b, b, b))
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)


def audio_env(audio):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(audio), "-f", "s16le", "-ac", "1", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 48000 // FPS
    n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
    rms = np.convolve(rms, np.ones(3) / 3, mode="same")
    env = np.clip(rms / (np.percentile(rms, 95) + 1e-6), 0, 1)
    return env.astype(np.float32), len(a) / 48000


def shot_list(dur, env):
    end = dur
    return [
        # (класс, t0, t1, kwargs, фокус-x для вертикальной нарезки)
        (S.Exterior, 0.0, 6.0, {}, 0.50),
        (S.YardEmpty, 6.0, 17.0, {}, 0.52),
        (S.WindowsOff, 17.0, 26.9, {}, 0.50),
        (S.Balcony, 26.9, 36.9, {}, 0.50),
        (S.Neighbor, 36.9, 48.2, {}, 0.48),
        (S.CrowdGathers, 48.2, 60.0, {}, 0.50),
        (S.Balcony, 60.0, 65.1, {"crowd": True}, 0.50),
        (S.VeraEnters, 65.1, 79.4, {"cam": "wide"}, 0.52),
        (S.Elevator, 79.4, 83.0, {}, 0.55),
        (S.Stairs, 83.0, 88.4, {}, 0.45),
        (S.VeraEnters, 88.4, 95.5, {"cam": "push"}, 0.50),
        (S.Sleeve, 95.5, 110.2, {}, 0.50),
        (S.Pulse, 110.2, 115.3, {}, 0.52),
        (S.Faces, 115.3, 125.1, {}, 0.50),
        (S.Turn, 125.1, end, {"env": env}, 0.48),
    ]


class Post:
    def __init__(self):
        rng = np.random.default_rng(99)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        v = 1 - 0.7 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1)
        self.vig = cv2.merge([np.clip(v * 255, 0, 255).astype(np.uint8)] * 3)
        self.grain = []
        for _ in range(12):
            g = cv2.resize(rng.normal(0, 5.5, (H // 2, W // 2)).astype(np.float32), (W, H))
            g3 = cv2.merge([g] * 3)
            self.grain.append((np.clip(g3, 0, 255).astype(np.uint8), np.clip(-g3, 0, 255).astype(np.uint8)))
        self.rng = rng

    def __call__(self, img, f, fade=1.0):
        img = cv2.multiply(img, self.vig, scale=1 / 255)
        flick = 1 + 0.025 * math.sin(f * 1.7) * math.sin(f * 0.37)
        if fade * flick != 1.0:
            img = cv2.convertScaleAbs(img, alpha=fade * flick)
        pos, neg = self.grain[(f * 7) % len(self.grain)]
        return cv2.subtract(cv2.add(img, pos), neg)


def render_chunk(args):
    f0, f1, dur, audio, out, title = args
    env, _ = audio_env(audio)
    shots = shot_list(dur, env)
    built = {}
    end_card = S.EndCard(dur, dur + TAIL, text_card([("23:47", 150, 210, 440, False)]))
    post = Post()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        t = f / FPS
        if t >= dur:
            img = end_card.frame(t)
            proc.stdin.write(post(img, f).tobytes())
            continue
        i = next(i for i, s in enumerate(shots) if s[1] <= t < s[2] or i == len(shots) - 1)
        if i not in built:
            cls, t0, t1, kw, _ = shots[i]
            built = {i: cls(t0, t1, **kw)}  # держим в памяти только текущий план
        img = built[i].frame(t)
        if t < 5.8:  # титр «23:47» поверх первого плана
            a = min(1.0, max(0.0, (t - 0.4) / 1.0)) * min(1.0, max(0.0, (5.6 - t) / 1.0))
            img = cv2.add(img, cv2.convertScaleAbs(title, alpha=a))
        fade = min(1.0, t / 0.8)
        proc.stdin.write(post(img, f, fade).tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def fix_text(s):
    rep = {"Биберева": "Бибирево", "Никак бывает": "Не так бывает", "вернулась суток": "вернулась с суток",
           "ждет": "ждёт", "идет": "идёт", "зеленая": "зелёная", "ее ": "её "}
    for a, b in rep.items():
        s = s.replace(a, b)
    return s


def subtitle_chunks(segments, max_len=34):
    """Короткие субтитры: длинные фразы режем по словам."""
    out = []
    for seg in segments:
        words = seg.get("words") or [(seg["start"], seg["end"], seg["text"])]
        cur, cs = "", None
        for ws, we, w in words:
            w = w.strip()
            if cs is None:
                cs = ws
            if cur and len(cur) + 1 + len(w) > max_len:
                out.append([cs, prev_end, cur])
                cur, cs = w, ws
            else:
                cur = (cur + " " + w).strip()
            prev_end = we
            if w.endswith((".", "?", "!")) and len(cur) > 12:
                out.append([cs, we, cur])
                cur, cs = "", None
        if cur:
            out.append([cs, prev_end, cur])
    # склеиваем «висящие» строки без точки с следующими
    for c in out:
        c[2] = fix_text(c[2])
        if c[1] - c[0] < 0.6:
            c[1] = c[0] + 0.6
    for a, b in zip(out, out[1:]):
        a[1] = min(a[1], b[0])
    return out


def ts(t, ass=False):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}" if ass else f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


def write_srt(chunks, path):
    with open(path, "w", encoding="utf-8") as fh:
        for i, (a, b, txt) in enumerate(chunks, 1):
            fh.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")


def write_ass(chunks, path, t0, t1, header):
    style = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
             "Style: Sub,Inter ExtraBold,76,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,2,70,70,520,1\n"
             "Style: Head,Inter ExtraBold,42,&H00C8C8C8,&H000000FF,&H00101010,&H64000000,0,0,0,0,100,100,2,0,1,3,0,8,60,60,180,1\n\n"
             "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(style)
        fh.write(f"Dialogue: 0,{ts(0, True)},{ts(3.5, True)},Head,,0,0,0,,{{\\fad(300,400)}}23:47 · {header}\n")
        for a, b, txt in chunks:
            if b <= t0 or (t1 is not None and a >= t1):
                continue
            a2, b2 = max(a, t0) - t0, (min(b, t1) if t1 else b) - t0
            fh.write(f"Dialogue: 0,{ts(a2, True)},{ts(b2, True)},Sub,,0,0,0,,{txt}\n")


def main():
    if len(sys.argv) < 2:
        sys.exit("Укажите файл озвучки: python render_episode.py voice.mp3")
    src = Path(sys.argv[1])
    out_dir = desktop() / "NOXARGENT_STUDIO" / "episodes" / "ep01_2347"
    tmp = out_dir / "_chunks"
    tt = out_dir / "tiktok"
    for d in (out_dir, tmp, tt):
        d.mkdir(parents=True, exist_ok=True)
    audio = out_dir / "voice.mp3"
    if src.resolve() != audio.resolve():
        shutil.copy2(src, audio)

    t_start = time.perf_counter()
    env, dur = audio_env(audio)
    total = int(math.ceil((dur + TAIL) * FPS))
    print(f"Озвучка: {dur:.2f} с → серия {dur + TAIL:.2f} с ({total} кадров)")

    # Субтитры (faster-whisper; расшифровка кешируется)
    seg_path = out_dir / "transcript.json"
    if not seg_path.exists():
        print("Расшифровываю озвучку…")
        from faster_whisper import WhisperModel
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(audio), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        segs, _ = WhisperModel("medium", device="cpu", compute_type="int8").transcribe(a, language="ru", vad_filter=True, word_timestamps=True)
        js = [dict(start=s.start, end=s.end, text=s.text.strip(), words=[(w.start, w.end, w.word) for w in s.words]) for s in segs]
        seg_path.write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    segments = json.loads(seg_path.read_text(encoding="utf-8"))
    chunks = subtitle_chunks(segments)
    cuts = tiktok_cuts(segments, dur, shot_starts=[sh[1] for sh in shot_list(dur, env)])
    write_srt(chunks, out_dir / "ep01_2347.srt")

    final = out_dir / "ep01_2347.mp4"
    if "--tiktok-only" in sys.argv and final.exists():
        make_tiktok(final, out_dir / "tiktok", chunks, cuts, dur, env)
        return

    title = text_card([("23:47", 170, 225, 360, False), ("БИБИРЕВО", 30, 150, 590, True)])
    n = max(1, min(os.cpu_count() or 2, 8))
    bounds = [round(total * i / n) for i in range(n + 1)]
    jobs = [(bounds[i], bounds[i + 1], dur, audio, tmp / f"c{i:02d}.mp4", title) for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(render_chunk, jobs)
    (tmp / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    video = tmp / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), "-c", "copy", str(video)], check=True)

    # Звук: голос нормализуем, под ним еле слышный низкий гул
    mix = tmp / "mix.m4a"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(audio),
                    "-f", "lavfi", "-t", f"{dur + TAIL:.2f}", "-i", "anoisesrc=color=brown:amplitude=0.5:seed=3",
                    "-filter_complex",
                    f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[v];"
                    f"[1:a]lowpass=f=110,volume=0.05,afade=t=in:d=2,afade=t=out:st={dur - 1:.2f}:d=2.5,aresample=48000[d];"
                    f"[v][d]amix=inputs=2:duration=shortest:normalize=0[a]",
                    "-map", "[a]", "-t", f"{dur + TAIL:.2f}", "-c:a", "aac", "-b:a", "192k", str(mix)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(mix), "-c", "copy", "-shortest",
                    "-movflags", "+faststart", str(final)], check=True)
    t_ep = time.perf_counter() - t_start
    print(f"Серия готова за {t_ep:.0f} с: {final}")

    make_tiktok(final, tt, chunks, cuts, dur, env)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Всё готово за {time.perf_counter() - t_start:.0f} с")


def make_tiktok(final, tt, chunks, cuts, dur, env):
    """Нарезки 9:16: кадрируем по фокусу каждого плана, жжём субтитры."""
    tt.mkdir(parents=True, exist_ok=True)
    for old in tt.glob("*"):
        old.unlink()
    shots = shot_list(dur, env)
    crop_w = int(H * 9 / 16) // 2 * 2
    expr = "+".join(f"{int(min(max(fx * W - crop_w / 2, 0), W - crop_w))}*between(t+OFF,{t0},{t1 if i < len(shots) - 1 else dur + TAIL + 1})"
                    for i, (_, t0, t1, _, fx) in enumerate(shots))
    for i, (a, b, name) in enumerate(cuts, 1):
        b = b if b is not None else dur + TAIL
        ass = tt / f"part{i}.ass"
        write_ass(chunks, ass, a, b if i < len(cuts) else None, name)
        x = expr.replace("OFF", f"{a:.3f}")
        vf = (f"crop={crop_w}:{H}:x='min({W - crop_w},{x})':y=0,scale=1080:1920:flags=lanczos,"
              f"subtitles='{ass.as_posix().replace(':', chr(92) + ':')}'")
        out = tt / f"ep01_2347_tiktok_part{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(final),
                        "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
        print(f"TikTok {i}: {a:.1f}–{b:.1f} с → {out.name}")


if __name__ == "__main__":
    main()
