"""DIDAO S01E01 - automatic assembly of the final episode (RU + EN).

Steps (per language):
 1. validate every clip (exists, non-empty, 1080x1920, 30 fps, expected frame count)
 2. concatenate the 12 clips in script order (no gaps, no extra black frames)
 3. place narration lines on the timeline (synced to clip offsets)
 4. mix narration + SFX + score (score ducked under the voice), loudness-normalise to -14 LUFS
 5. build subtitles (.ass burned in, .srt delivered separately) + episode title card
 6. final grade (gentle contrast / cool split-tone), H.264 + AAC MP4 export
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, resample_poly, sosfilt, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script_ep01 import CLIPS, END_CARD_CLIP, GAP, SEASON_TITLE_EN, SEASON_TITLE_RU, EP_TITLE_EN, EP_TITLE_RU  # noqa

EP = os.path.join(HERE, '..')
CLIPDIR = os.path.join(EP, 'clips')
SR = 48000
TMP = os.path.join(EP, 'project_files', '_build')
os.makedirs(TMP, exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                          'stream=width,height,r_frame_rate,nb_read_frames,codec_name', '-of', 'json', path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)['streams'][0]


def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if ch == 2:
        x = x.reshape(-1, 2)
    return x, sr


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def offsets():
    o, acc = {}, 0.0
    for c in CLIPS:
        o[c['id']] = acc
        acc += c['dur']
    return o, acc


def validate(lang):
    report = []
    files = []
    for c in CLIPS:
        name = c['name'] + ('_RU' if (lang == 'ru' and c['id'] == END_CARD_CLIP) else '') + '.mp4'
        p = os.path.join(CLIPDIR, name)
        ok = os.path.exists(p) and os.path.getsize(p) > 10000
        if not ok:
            raise SystemExit(f'missing/empty clip: {name}')
        s = probe(p)
        exp = int(round(c['dur'] * 30))
        fr = s['r_frame_rate']
        good = s['width'] == 1080 and s['height'] == 1920 and fr == '30/1' and int(s['nb_read_frames']) == exp
        report.append(f"{name:36s} {s['width']}x{s['height']} {fr} frames={s['nb_read_frames']}/{exp} {s['codec_name']} {'OK' if good else 'CHECK'}")
        if not good:
            raise SystemExit('clip check failed: ' + report[-1])
        files.append(p)
    return files, report


def vo_timeline(lang):
    """Returns list of (abs_start, abs_end, text, wav) with no overlaps."""
    off, total = offsets()
    out = []
    prev_end = 0.0
    for c in CLIPS:
        for i, (planned, src, text) in enumerate(c['vo'][lang]):
            wavp = os.path.join(EP, 'voiceover', lang, f"VO_{lang.upper()}_{c['id']:02d}_{i + 1}.wav")
            x, sr = read_wav(wavp)
            d = len(x) / sr
            st = max(off[c['id']] + (planned if planned is not None else 0.0), prev_end + GAP)
            out.append((st, st + d, text, wavp))
            prev_end = st + d
    return out


def build_audio(lang, total):
    n = int((total + 0.5) * SR)
    vo = np.zeros(n)
    # the client recording is already mastered: keep its relative levels, only normalise the whole track
    tl = vo_timeline(lang)
    sos_hp = butter(2, 90, 'high', fs=SR, output='sos')
    for st, en, text, wavp in tl:
        x, sr = read_wav(wavp)
        x = resample_poly(x, SR, sr)
        x = sosfilt(sos_hp, x)
        i = int(st * SR)
        vo[i:i + len(x)] += x[: n - i]
    vo = vo / (np.max(np.abs(vo)) + 1e-9) * 0.9
    # small dark room reverb on the narration
    ir_n = int(0.9 * SR)
    rng = np.random.default_rng(1)
    ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.18 * SR))
    ir = sosfilt(butter(2, 3500, 'low', fs=SR, output='sos'), ir)
    ir /= np.sqrt(np.sum(ir ** 2))
    wet = fftconvolve(vo, ir)[:n] * 0.05
    vo_st = np.stack([vo + wet, vo + np.roll(wet, 400)], 1)
    sfx, _ = read_wav(os.path.join(EP, 'sound_effects', 'SFX_EP01_FULL.wav'))
    mus, _ = read_wav(os.path.join(EP, 'music', 'MUSIC_EP01_FULL.wav'))
    sfx = np.pad(sfx, ((0, max(0, n - len(sfx))), (0, 0)))[:n]
    mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n]
    # ducking envelope from the voice
    env = np.abs(vo)
    env = sosfilt(butter(1, 4, 'low', fs=SR, output='sos'), env)
    env = np.clip(env / 0.05, 0, 1)
    duck = 1.0 - 0.55 * env
    mix = vo_st * 1.0 + sfx * 0.75 + mus * 0.30 * duck[:, None]
    sfx_duck = 1.0 - 0.3 * env
    mix = vo_st * 1.0 + sfx * 0.75 * sfx_duck[:, None] + mus * 0.30 * duck[:, None]
    mix /= max(1.0, np.max(np.abs(mix)) / 0.95)
    raw = os.path.join(TMP, f'mix_{lang}.wav')
    write_wav(raw, mix)
    # VO-only stem for the archive
    write_wav(os.path.join(EP, 'voiceover', f'VO_{lang.upper()}_FULL_TIMELINE.wav'), vo_st / (np.max(np.abs(vo_st)) + 1e-9) * 0.9)
    norm = os.path.join(TMP, f'mix_{lang}_norm.wav')
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                          capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', af, '-ar', str(SR), norm])
    return norm, tl


def fmt_ass(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'


def fmt_srt(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def build_subs(lang, tl):
    off, total = offsets()
    events = [(st, en + 0.25, txt) for st, en, txt, _ in tl]
    events.sort()
    # avoid overlapping subtitle events
    fixed = []
    for i, (a, b, txt) in enumerate(events):
        if i + 1 < len(events):
            b = min(b, events[i + 1][0] - 0.02)
        fixed.append((a, b, txt))
    srt = os.path.join(EP, 'subtitles', f'DIDAO_EP01_{lang.upper()}.srt')
    with open(srt, 'w', encoding='utf-8') as f:
        for i, (a, b, txt) in enumerate(fixed, 1):
            f.write(f'{i}\n{fmt_srt(a)} --> {fmt_srt(b)}\n{txt}\n\n')
    st_title = SEASON_TITLE_RU if lang == 'ru' else SEASON_TITLE_EN
    ep_title = EP_TITLE_RU if lang == 'ru' else EP_TITLE_EN
    ass = os.path.join(EP, 'subtitles', f'DIDAO_EP01_{lang.upper()}.ass')
    with open(ass, 'w', encoding='utf-8') as f:
        f.write('[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n')
        f.write('[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, '
                'Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n')
        f.write('Style: Sub,DejaVu Sans,50,&H00F2F2F2,&H000000FF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,3.2,1.5,2,110,110,520,1\n')
        f.write('Style: Brand,DejaVu Sans,34,&H00D8D8D8,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,22,0,1,1.5,0,8,60,60,250,1\n')
        f.write('Style: Title,DejaVu Serif,70,&H00F4F4F4,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,4,0,1,2.5,2,8,60,60,310,1\n')
        f.write('Style: Ep,DejaVu Serif,44,&H00C8D0D8,&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,2,0,1,2,1.5,8,60,60,410,1\n\n')
        f.write('[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
        f.write(f'Dialogue: 1,{fmt_ass(0.6)},{fmt_ass(5.6)},Brand,,0,0,0,,{{\\fad(600,700)}}D I D A O\n')
        f.write(f'Dialogue: 1,{fmt_ass(0.9)},{fmt_ass(5.6)},Title,,0,0,0,,{{\\fad(800,700)}}{st_title}\n')
        f.write(f'Dialogue: 1,{fmt_ass(1.4)},{fmt_ass(5.6)},Ep,,0,0,0,,{{\\fad(800,700)}}{ep_title}\n')
        for a, b, txt in fixed:
            f.write(f'Dialogue: 0,{fmt_ass(a)},{fmt_ass(b)},Sub,,0,0,0,,{{\\fad(120,120)}}{txt}\n')
    return ass, srt


def assemble(lang):
    files, report = validate(lang)
    off, total = offsets()
    lst = os.path.join(TMP, f'concat_{lang}.txt')
    with open(lst, 'w') as f:
        for p in files:
            f.write(f"file '{os.path.abspath(p)}'\n")
    pic = os.path.join(TMP, f'picture_{lang}.mp4')
    run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', pic])
    audio, tl = build_audio(lang, total)
    ass, srt = build_subs(lang, tl)
    out = os.path.join(EP, 'final', f'DIDAO_EP01_{"RUSSIAN" if lang == "ru" else "ENGLISH"}.mp4')
    grade = ("eq=contrast=1.05:saturation=0.94:gamma=0.98,"
             "colorbalance=rs=-0.02:bs=0.03:rh=0.01:bh=-0.01,"
             f"ass='{ass}'")
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pic, '-i', audio, '-vf', grade, '-map', '0:v', '-map', '1:a',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', '30',
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{total:.3f}', '-movflags', '+faststart', out])
    with open(os.path.join(EP, 'project_files', f'assembly_report_{lang}.txt'), 'w') as f:
        f.write('\n'.join(report) + f'\nTOTAL {total:.2f}s\nVO lines:\n')
        for st, en, txt, _ in tl:
            f.write(f'  {st:7.2f}-{en:7.2f}  {txt}\n')
    print(out)


if __name__ == '__main__':
    for lang in (sys.argv[1:] or ['ru', 'en']):
        assemble(lang)
