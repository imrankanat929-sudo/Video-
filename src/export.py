"""Final export: base picture + burned captions + mixed audio (2-pass loudnorm to -14 LUFS) -> output/bear_video_{lang}.mp4"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'build')
O = os.path.join(ROOT, 'output')
FONTS = '/usr/share/fonts/opentype/inter'


def loudnorm_filter(wav):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', r, re.S).group(0))
    return (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


def main(langs):
    os.makedirs(O, exist_ok=True)
    for lang in langs:
        wav = os.path.join(B, f'mix_{lang}.wav')
        af = loudnorm_filter(wav) + ',aresample=48000'
        vf = f"subtitles={os.path.join(B, f'captions_{lang}.ass')}:fontsdir={FONTS}"
        out = os.path.join(O, f'bear_video_{lang}.mp4')
        cmd = ['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(B, 'base.mp4'), '-i', wav, '-map', '0:v', '-map', '1:a',
               '-vf', vf, '-af', af, '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow', '-crf', '23', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p',
               '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', '120', '-movflags', '+faststart',
               '-metadata', f'language={lang}', out]
        subprocess.run(cmd, check=True)
        print('wrote', out)


if __name__ == '__main__':
    main(sys.argv[1:] or ['ru', 'en'])
