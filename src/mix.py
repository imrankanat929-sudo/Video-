"""Mix voice + music (ducked) + sfx, normalise for YouTube. Usage: python mix.py LANG MUSIC.mp3"""
import os
import re
import subprocess
import sys

from hm_scenes import END

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "build")


def lufs(path, extra=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", path]
    if extra:
        cmd += ["-af", extra + ",ebur128"]
    else:
        cmd += ["-af", "ebur128"]
    r = subprocess.run(cmd + ["-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def run(args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + args, check=True)


def main(lang, music):
    voice = os.path.join(B, f"voice_{lang}.wav")
    sfx = os.path.join(B, f"sfx_{lang}.wav")
    vg = -16.0 - lufs(voice)
    mg = -25.5 - lufs(music)
    fade_out = END - 5.0
    fc = (
        f"[0:a]aformat=sample_rates=48000:channel_layouts=mono,volume={vg:.2f}dB,apad,atrim=0:{END},"
        f"aformat=channel_layouts=stereo,asplit=2[v][vsc];"
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mg:.2f}dB,"
        f"afade=t=in:st=0:d=2.5,afade=t=out:st={fade_out}:d=4.6,apad,atrim=0:{END}[m];"
        f"[m][vsc]sidechaincompress=threshold=0.02:ratio=5:attack=120:release=900:makeup=1[md];"
        f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.6,apad,atrim=0:{END}[s];"
        f"[v][md][s]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.84:attack=5:release=80[out]"
    )
    pre = os.path.join(B, f"premix_{lang}.wav")
    run(["-i", voice, "-i", music, "-i", sfx, "-filter_complex", fc, "-map", "[out]", "-ar", "48000",
         "-c:a", "pcm_f32le", pre])
    g = -15.2 - lufs(pre)
    run(["-i", pre, "-af", f"volume={g:.2f}dB,alimiter=limit=0.89:attack=3:release=60", "-ar", "48000",
         "-c:a", "pcm_s24le", os.path.join(B, f"mix_{lang}.wav")])
    print(lang, "voice gain", round(vg, 2), "music gain", round(mg, 2), "final gain", round(g, 2),
          "-> LUFS", lufs(os.path.join(B, f"mix_{lang}.wav")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
