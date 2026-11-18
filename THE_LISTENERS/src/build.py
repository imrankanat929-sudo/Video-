"""Build THE LISTENERS EP01 (Russian): VO -> timeline -> scene renders -> mix -> final film, SRT, scripts, thumbnail.
usage: python3 build.py [timeline|render|audio|final|all|thumb] [scene ids...]"""
import os, sys, json, math, subprocess, re
from multiprocessing import Pool
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skia
from gfx import W, H, vignette, grain, paint, C, ease, lerp, seg
import scenes as S
import tts
import audio as A

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
FPS = 25
SR = A.SR
SPEAKER_NAMES = {'A': 'Алекс', 'AN': 'Алекс', 'MOM': 'Голос', 'MIMA': 'Голос', 'TV': 'Радио', 'MIRA': 'Мира', 'VIK': 'Виктор', 'VIKL': 'Голос', 'MAN': 'Голос', 'FRIEND': 'Голос друга', 'MIMW': 'Голос'}
os.makedirs(BUILD, exist_ok=True)


def parse_time(v, L):
    if isinstance(v, (int, float)):
        return float(v)
    m = re.match(r'L(\d+)\+([\d.]+)', v)
    i, off = int(m.group(1)), float(m.group(2))
    return L[i][0] + off


def timeline():
    tl = []
    t = 0.0
    for s in S.SCENES:
        L, clips = [], []
        cur = s['lead']
        for spk, text in s['vo']:
            y = tts.synth(spk, text)
            d = len(y) / SR
            L.append((cur, cur + d))
            clips.append((spk, text, cur, d))
            cur += d + s['gap']
        end = (L[-1][1] if L else 0) + s['tail']
        dur = max(s['min_dur'], end)
        dur = math.ceil(dur * FPS) / FPS
        tl.append(dict(id=s['id'], part=s['part'], start=round(t, 3), dur=dur, L=L, clips=clips))
        t += dur
    json.dump(tl, open(os.path.join(BUILD, 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'total {t:.1f}s = {t / 60:.2f} min, scenes {len(tl)}')
    return tl


def load_tl():
    return json.load(open(os.path.join(BUILD, 'timeline.json')))


def scene_by_id(i):
    for s in S.SCENES:
        if s['id'] == i:
            return s


def render_scene(args):
    item, out = args
    s = scene_by_id(item['id'])
    T = item['dur']
    q = S.Q([tuple(x) for x in item['L']])
    nfr = int(round(T * FPS))
    arr = np.zeros((H, W, 4), np.uint8)
    surf = skia.Surface(arr)
    c = surf.getCanvas()
    cam = s['cam'] or (1.0, 1.0, W / 2, H / 2)
    z0, z1, fx, fy = cam[:4]
    px0, px1 = (cam[4], cam[5]) if len(cam) > 4 else (0, 0)
    tmp = out + '.tmp.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-tune', 'animation', '-pix_fmt', 'yuv420p', '-threads', '2',
                           '-g', '50', tmp], stdin=subprocess.PIPE)
    for f in range(nfr):
        t = f / FPS
        k = ease(t / T) if T > 0 else 0
        z = lerp(z0, z1, k)
        px = lerp(px0, px1, k)
        zmin = 1 + abs(px) * 2 / W + 0.004
        z = max(z, zmin) if px0 or px1 else z
        # slow handheld drift
        dx = math.sin(t * 0.7 + item['id']) * 3 + math.sin(t * 1.9) * 1.2
        dy = math.cos(t * 0.6 + item['id']) * 2.5
        c.clear(skia.ColorBLACK)
        c.save()
        c.translate(fx + px + dx, fy + dy)
        c.scale(z * 1.006, z * 1.006)
        c.translate(-fx, -fy)
        s['draw'](c, t, T, q)
        c.restore()
        vignette(c, 0.7)
        grain(c, t, 0.05)
        a = 0.0
        if s['fade_in'] and t < s['fade_in']:
            a = max(a, 1 - t / s['fade_in'])
        if s['fade_out'] and t > T - s['fade_out']:
            a = max(a, (t - (T - s['fade_out'])) / s['fade_out'])
        if a > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint(C('#000000', min(1, a))))
        ff.stdin.write(arr.tobytes())
    ff.stdin.close()
    ff.wait()
    os.replace(tmp, out)
    return item['id']


def render(ids=None, procs=4):
    tl = load_tl()
    os.makedirs(os.path.join(ROOT, 'scenes'), exist_ok=True)
    jobs = []
    for it in tl:
        if ids and it['id'] not in ids:
            continue
        out = os.path.join(ROOT, 'scenes', f'scene_{it["id"]:03d}.mp4')
        jobs.append((it, out))
    jobs.sort(key=lambda j: -j[0]['dur'])
    with Pool(procs) as p:
        for i in p.imap_unordered(render_scene, jobs):
            print('rendered', i, flush=True)


# ------------------------------------------------------------------ audio

def mix():
    tl = load_tl()
    total = tl[-1]['start'] + tl[-1]['dur']
    N = int(total * SR) + SR
    vo = np.zeros(N, np.float32)
    mus = np.zeros(N, np.float32)
    amb = np.zeros(N, np.float32)
    fx = np.zeros(N, np.float32)
    XF = 1.0  # crossfade seconds for beds
    for it in tl:
        s = scene_by_id(it['id'])
        st, d = it['start'], it['dur']
        # voice
        for spk, text, at, dd in it['clips']:
            y = tts.synth(spk, text)
            A.place(vo, y, st + at)
        # music & ambience with crossfades
        a0 = max(0, st - XF / 2)
        dd = d + XF
        n = int(dd * SR)
        e = np.ones(n, np.float32)
        nf = int(XF * SR)
        e[:nf] = np.linspace(0, 1, nf)
        e[-nf:] = np.linspace(1, 0, nf)
        A.place(mus, A.music(s['mus'], a0, dd)[:n] * e, a0)
        A.place(amb, A.amb(s['amb'], a0, dd, it['id'])[:n] * e, a0)
        # sfx
        for at, name, g in s['sfx']:
            tt = parse_time(at, it['L'])
            if name in A.BEDS:
                bd = max(0.5, d - tt)
                x = A.BEDS[name](bd)
                x = x * A.adsr(len(x), 0.05, 0.4)
            elif name in A.SFX:
                x = A.SFX[name]()
            else:
                print('missing sfx', name)
                continue
            A.place(fx, x * g, st + tt)
    # ---- ducking: background goes down while the voice speaks
    envv = np.abs(vo)
    win = int(0.03 * SR)
    envv = np.convolve(envv, np.ones(win) / win, mode='same')
    act = (envv > 0.004).astype(np.float32)
    # attack 60ms / release 450ms smoothing (one-pole up/down)
    g = np.zeros_like(act)
    up, dn = 1 - math.exp(-1 / (0.06 * SR)), 1 - math.exp(-1 / (0.45 * SR))
    # vectorised approximation: smooth with asymmetric filters via scipy lfilter on max-hold
    from scipy import signal as sg
    hold = sg.lfilter([dn], [1, -(1 - dn)], act)
    hold = np.maximum(hold, sg.lfilter([up], [1, -(1 - up)], act))
    g = np.clip(hold * 2.0, 0, 1)
    duck_bg = 1 - g * (1 - 10 ** (-16 / 20))   # -16 dB under voice
    duck_fx = 1 - g * (1 - 10 ** (-11 / 20))   # -11 dB for effects
    music_lvl, amb_lvl, fx_lvl = 0.5, 0.42, 0.62
    bg = mus * music_lvl * duck_bg + amb * amb_lvl * duck_bg + fx * fx_lvl * duck_fx
    # stereo: widen background with slight decorrelation
    L = bg + np.roll(amb * amb_lvl * duck_bg, 240) * 0.15
    R = bg - np.roll(amb * amb_lvl * duck_bg, 240) * 0.15
    vo_g = 1.15
    L = L + vo * vo_g
    R = R + vo * vo_g
    st = np.stack([L, R], 1)[:int(total * SR)]
    pk = np.max(np.abs(st))
    st = st / max(pk, 1e-6) * 0.95
    os.makedirs(os.path.join(ROOT, 'voiceover'), exist_ok=True)
    raw = os.path.join(BUILD, 'mix.f32')
    st.astype(np.float32).tofile(raw)
    vo[:int(total * SR)].astype(np.float32).tofile(os.path.join(BUILD, 'vo.f32'))
    # loudness normalise to YouTube-ish -14 LUFS
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw,
                    '-af', 'loudnorm=I=-15:TP=-1.5:LRA=14', '-ar', str(SR), '-c:a', 'pcm_s16le', os.path.join(BUILD, 'mix.wav')], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', os.path.join(BUILD, 'vo.f32'),
                    '-af', 'loudnorm=I=-16:TP=-1.5', '-ar', '44100', '-c:a', 'libmp3lame', '-b:a', '160k', os.path.join(ROOT, 'voiceover', 'russian.mp3')], check=True)
    # stems for convenience
    os.makedirs(os.path.join(ROOT, 'assets', 'music'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'assets', 'sound_effects'), exist_ok=True)
    for name, x, folder in (('music_score.mp3', mus * music_lvl, 'music'), ('sfx_and_ambience.mp3', fx * fx_lvl + amb * amb_lvl, 'sound_effects')):
        x = x[:int(total * SR)]
        x = x / max(1e-6, np.max(np.abs(x))) * 0.9
        p = os.path.join(BUILD, name + '.f32')
        x.astype(np.float32).tofile(p)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', p, '-ar', '44100', '-c:a', 'libmp3lame', '-b:a', '128k',
                        os.path.join(ROOT, 'assets', folder, name)], check=True)
    print('mix done', total)


# ------------------------------------------------------------------ subtitles / scripts

def fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def wrap(s, n=44):
    words, lines, cur = s.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines


def split_sentences(text):
    parts = re.split(r'(?<=[.!?…])\s+', text)
    out = []
    for p in parts:
        if out and len(out[-1]) + len(p) < 60:
            out[-1] += ' ' + p
        else:
            out.append(p)
    return out


def subtitles():
    tl = load_tl()
    cues = []
    for it in tl:
        for spk, text, at, d in it['clips']:
            t0 = it['start'] + at
            name = SPEAKER_NAMES.get(spk)
            parts = split_sentences(text)
            tot = sum(len(p) for p in parts)
            tt = t0
            for p in parts:
                pd = d * len(p) / tot
                lab = (f'{name}: ' if name and p is parts[0] else '')
                lines = wrap(lab + p)
                # chunk into max 2 lines
                for k in range(0, len(lines), 2):
                    chunk = lines[k:k + 2]
                    cd = pd * len(' '.join(chunk)) / max(1, len(' '.join(lines)))
                    cues.append((tt, tt + cd, '\n'.join(chunk)))
                    tt += cd
    os.makedirs(os.path.join(ROOT, 'subtitles'), exist_ok=True)
    with open(os.path.join(ROOT, 'subtitles', 'russian.srt'), 'w', encoding='utf-8') as f:
        for i, (a, b, s) in enumerate(cues, 1):
            f.write(f'{i}\n{fmt(a)} --> {fmt(max(a + 0.6, b - 0.02))}\n{s}\n\n')
    print('srt cues', len(cues))


def scripts():
    tl = load_tl()
    d = os.path.join(ROOT, 'scripts')
    os.makedirs(d, exist_ok=True)
    parts = {1: 'ЧЁРНАЯ ТИШИНА', 2: 'ПРАВИЛА 1–5', 3: 'ПРАВИЛА 6–10', 4: 'ПРАВИЛА 11–14', 5: 'ПРАВИЛО 15', 6: 'ДИКТОФОН'}
    with open(os.path.join(d, 'russian_script.txt'), 'w', encoding='utf-8') as f:
        f.write('THE LISTENERS — ЭПИЗОД 01 — 15 ПРАВИЛ, ЧТОБЫ ВЫЖИТЬ СРЕДИ СЛУШАЮЩИХ\nРусский сценарий озвучки\n')
        f.write('Обозначения: [ДИКТОР] — низкий спокойный голос; [ДИКТОР, шёпот]; [АЛЕКС, шёпот]; [ГОЛОС] — имитация существа.\n')
        cur = None
        names = {'N': 'ДИКТОР', 'W': 'ДИКТОР, шёпот', 'A': 'АЛЕКС, шёпот', 'AN': 'АЛЕКС', 'MOM': 'ГОЛОС «МАМЫ» (существо)', 'MIMA': 'ГОЛОС АЛЕКСА (существо)',
                 'TV': 'ЭКСТРЕННОЕ ВЕЩАНИЕ', 'MIRA': 'МИРА, шёпот', 'VIK': 'ВИКТОР, шёпот', 'VIKL': 'ГОЛОС «ВИКТОРА» (существо)', 'MAN': 'МУЖЧИНА / ГОЛОС', 'FRIEND': 'ГОЛОС ДРУГА (существо)', 'MIMW': 'ГОЛОС АЛЕКСА, шёпот (существо)'}
        for it in tl:
            if it['part'] != cur:
                cur = it['part']
                f.write(f'\n\n===== ЧАСТЬ {cur} — {parts[cur]} =====\n')
            if it['clips']:
                f.write(f'\n[Сцена {it["id"]:03d} · {fmt(it["start"])[:8]}]\n')
            for spk, text, at, dd in it['clips']:
                f.write(f'{names[spk]}: {text}\n')
    with open(os.path.join(d, 'timeline.txt'), 'w', encoding='utf-8') as f:
        f.write('scene\tstart\tend\tdur\tpart\tmusic\tambience\tfile\n')
        for it in tl:
            s = scene_by_id(it['id'])
            f.write(f'{it["id"]:03d}\t{fmt(it["start"])}\t{fmt(it["start"] + it["dur"])}\t{it["dur"]:.2f}s\t{it["part"]}\t{s["mus"]}\t{s["amb"]}\tscenes/scene_{it["id"]:03d}.mp4\n')
    with open(os.path.join(d, 'scene_prompts.txt'), 'w', encoding='utf-8') as f:
        f.write('THE LISTENERS EP01 — scene prompts (visual design per scene)\n')
        f.write('Global style: flat cinematic horror illustration, night palette (cold white, dark grey, black, deep blue, dull red warnings), volumetric fog, deep shadows, slow camera, film grain, 16:9 1920x1080.\n')
        f.write('CREATURE (constant): THE LISTENER — 2.3-2.6 m, smooth matte white ceramic body, NO eyes / nose / mouth / hair, elongated egg-shaped head, long thin arms reaching below the knees, thin backward-bent legs, slow unnatural movement, head turns toward sound. No blood, no clothes, no zombie features.\n')
        f.write('ALEX (constant): 16 y.o., black messy hair, dark grey-blue sweater, dark jeans, tired tense eyes.\n\n')
        for it in tl:
            s = scene_by_id(it['id'])
            cam = s['cam'] or (1, 1, 960, 540)
            move = 'static' if abs(cam[0] - cam[1]) < 0.01 else ('slow push-in' if cam[1] > cam[0] else 'slow pull-out')
            f.write(f'scene_{it["id"]:03d}  [{it["dur"]:.1f}s, part {it["part"]}, camera: {move}, music: {s["mus"]}, ambience: {s["amb"]}]\n  {s["prompt"] or "Title / chapter card or notebook insert (Alex writes the rule down)."}\n\n')
    print('scripts written')


def final():
    tl = load_tl()
    lst = os.path.join(BUILD, 'concat.txt')
    with open(lst, 'w') as f:
        for it in tl:
            f.write(f"file '{os.path.join(ROOT, 'scenes', f'scene_{it['id']:03d}.mp4')}'\n")
    video = os.path.join(BUILD, 'video.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    os.makedirs(os.path.join(ROOT, 'final'), exist_ok=True)
    out = os.path.join(ROOT, 'final', 'THE_LISTENERS_EP01_RU.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', video, '-i', os.path.join(BUILD, 'mix.wav'), '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                    '-metadata', 'title=THE LISTENERS — 15 правил, чтобы выжить среди Слушающих (Эпизод 01)', out], check=True)
    print('final ->', out)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    ids = [int(x) for x in sys.argv[2:]] or None
    if cmd in ('timeline', 'all'):
        timeline()
    if cmd in ('render', 'all'):
        render(ids)
    if cmd in ('audio', 'all'):
        mix()
    if cmd in ('subs', 'all'):
        subtitles()
        scripts()
    if cmd in ('final', 'all'):
        final()
