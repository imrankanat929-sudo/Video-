"""Generate voiceover lines with edge-tts, record word timings, resolve schedule."""
import asyncio, json, os, re, subprocess, sys
import edge_tts

sys.path.insert(0, os.path.dirname(__file__))
from script import VO, VOICES, SUPPLIED_OFFSET, SUPPLIED_FIX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART2_AUDIO = os.path.join(ROOT, "assets", "ru_supplied_narration_part2.mp3")
PART2_WORDS = os.path.join(ROOT, "assets", "ru_supplied_part2_words.json")
PART2_MAP = {"b1": [0], "b2": [1], "b3": [2], "b4": [3], "b5": [4], "c1": [5, 6], "c2": [7], "d1": [8], "d2": [9], "d3": [10]}


async def synth(text, cfg, mp3, boundary="WordBoundary"):
    comm = edge_tts.Communicate(text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"],
                                boundary=boundary)
    words = []
    with open(mp3, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append(dict(w=ch["text"], s=ch["offset"] / 1e7, e=(ch["offset"] + ch["duration"]) / 1e7))
    return words


def speech_span(wav):
    log = subprocess.run(["ffmpeg", "-v", "info", "-i", wav, "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    d = dur(wav)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    s0 = ends[0] if starts and starts[0] < 0.01 and ends else 0.0
    e0 = starts[-1] if starts and (len(ends) < len(starts)) else d
    return s0, e0, starts, ends


def approx_words(text, wav):
    """Word timings when the voice gives none: spread over speech, respecting pauses."""
    s0, e0, starts, ends = speech_span(wav)
    toks = text.split()
    # weight = letters + pause bonus after punctuation
    wts = []
    for t in toks:
        w = len(re.sub(r"[^\w]", "", t)) + 1.5
        wts.append(w)
    pauses = [(a, b) for a, b in zip(starts, ends) if a > s0 + 0.05 and b < e0 - 0.05]
    total_pause = sum(b - a for a, b in pauses)
    speak = (e0 - s0) - total_pause
    # assign pauses to punctuation tokens in order
    punct_idx = [i for i, t in enumerate(toks[:-1]) if re.search(r"[,.…—:;?!»]$", t) or toks[i + 1] in ("—",)]
    words, t = [], s0
    pq = list(pauses)
    for i, (tok, w) in enumerate(zip(toks, wts)):
        d = speak * w / sum(wts)
        words.append(dict(w=tok, s=t, e=t + d)); t += d
        if i in punct_idx and pq:
            a, b = pq.pop(0); t += b - a
    return words


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path]).strip())


async def main(lang):
    out = os.path.join(ROOT, "assets", f"vo_{lang}")
    os.makedirs(out, exist_ok=True)
    cfg = VOICES[lang]
    timing = []
    prev_end = 0.0
    supplied = json.load(open(os.path.join(ROOT, "assets", "ru_supplied_words.json")))
    # merge whisper segments onto RU-supplied line ids (a6 = two segments)
    seg_map = {"a1": [0], "a2": [1], "a3": [2], "a4": [3], "a5": [4], "a6": [5, 6], "a7": [7], "a8": [8], "a9": [9], "a10": [10]}
    for lid, start, latest, en, ru in VO:
        text = en if lang == "en" else ru
        if text is None:
            segs = [supplied[i] for i in seg_map[lid]]
            words = []
            for sg in segs:
                for w in sg["words"]:
                    ww = SUPPLIED_FIX.get(w["w"], w["w"])
                    if ww.startswith("-") and words:  # whisper split "что -то"
                        words[-1]["w"] += ww; words[-1]["e"] = w["e"] + SUPPLIED_OFFSET; continue
                    words.append(dict(w=ww, s=w["s"] + SUPPLIED_OFFSET, e=w["e"] + SUPPLIED_OFFSET))
            txt = " ".join(w["w"] for w in words)
            timing.append(dict(id=lid, start=None, supplied=True, text=txt, words=[dict(w=w["w"], s=w["s"], e=w["e"]) for w in words], end=words[-1]["e"]))
            prev_end = words[-1]["e"]
            print(f"{lang} {lid}: supplied {words[0]['s']:6.2f}-{prev_end:6.2f}")
            continue
        mp3 = os.path.join(out, f"{lid}.mp3"); wav = os.path.join(out, f"{lid}.wav")
        if lang == "ru" and lid in PART2_MAP and os.path.exists(PART2_AUDIO):
            # second supplied recording: cut this line out of it
            p2 = json.load(open(PART2_WORDS))
            idx = PART2_MAP[lid]
            s0 = max(0.0, p2[idx[0]]["s"] - 0.08)
            nxt = p2[idx[-1] + 1]["s"] if idx[-1] + 1 < len(p2) else p2[idx[-1]]["e"] + 0.6
            e0 = min(p2[idx[-1]]["e"] + 0.25, nxt - 0.02)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", PART2_AUDIO, "-ss", f"{s0:.3f}", "-to", f"{e0:.3f}",
                            "-ar", "48000", "-ac", "1", "-af", "afade=t=out:st=%.3f:d=0.05" % (e0 - s0 - 0.05), wav], check=True)
            words = [dict(w=w["w"], s=w["s"] - s0, e=w["e"] - s0) for i in idx for w in p2[i]["words"]]
            d = dur(wav)
            st = max(start, prev_end + 0.22) - words[0]["s"]
            speech_end = st + words[-1]["e"]
            flag = "  <-- OVER" if speech_end > latest + 0.05 else ""
            print(f"{lang} {lid}: part2 start {st:6.2f} speech_end {speech_end:6.2f} (latest {latest}){flag}")
            words = [dict(w=w["w"], s=w["s"] + st, e=w["e"] + st) for w in words]
            timing.append(dict(id=lid, start=st, dur=d, text=text, words=words, end=speech_end, supplied2=True))
            prev_end = speech_end
            continue
        try:
            words = await synth(text, cfg, mp3)
        except edge_tts.exceptions.NoAudioReceived:
            await synth(text, cfg, mp3, boundary="SentenceBoundary")
            words = None
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ar", "48000", "-ac", "1", wav], check=True)
        if not words:
            words = approx_words(text, wav)
        d = dur(wav)
        lead = words[0]["s"] if words else 0.0
        st = max(start, prev_end + 0.2) - lead  # align first word to planned start
        speech_end = st + (words[-1]["e"] if words else d)
        flag = "  <-- OVER" if speech_end > latest + 0.05 else ""
        print(f"{lang} {lid}: start {st:6.2f} speech_end {speech_end:6.2f} (latest {latest}){flag}")
        words = [dict(w=w["w"], s=w["s"] + st, e=w["e"] + st) for w in words]
        timing.append(dict(id=lid, start=st, dur=d, text=text, words=words, end=speech_end))
        prev_end = speech_end
    json.dump(timing, open(os.path.join(out, "timing.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    for lang in sys.argv[1:] or ["en", "ru"]:
        asyncio.run(main(lang))
