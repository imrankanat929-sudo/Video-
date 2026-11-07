# What if an asteroid hit Earth in 7 days? / Что, если астероид упадёт через 7 дней?

Vertical 9:16 (1080×1920, 30 fps) videos built from the two ElevenLabs voice-overs,
with burned-in word-by-word subtitles, a synthesised score and sound design,
plus 9:16 cover images.

## Output (`output/`)

| File | What |
|---|---|
| `asteroid_7_days_RU.mp4` | Russian video |
| `asteroid_7_days_EN.mp4` | English video |
| `preview_ru.jpg` | Russian cover (9:16) |
| `preview_en.jpg` | English cover (9:16) |

## Titles for upload

- RU: **Что, если астероид упадёт на Землю через 7 дней?**
- EN: **What If an Asteroid Hit Earth in 7 Days?**

## Storyboard (35 shots, cut to the voice-over)

Hook (asteroid + title) → emergency alert on the phone → tracking radar → "fake?" chat →
breaking news → asteroid close-up + countdown → DAY 1 → mission control → wall of TVs →
empty supermarket → airport departures board → DAY 3 → "bigger than thought" → impact zone on Earth →
sirens / "remain calm" billboard → calling mom, texting an old friend → rooftop at sunset → DAY 5 →
rocket launch → crowd watching the mission screen → mission failed → DAY 7 → empty street countdown →
family at the window → bright dot in the sky → atmospheric entry → white flash (music stops) →
impact & shockwave → dusty Earth → ruins + sprout, years pass → "?" → together… → …or apart? →
twist: 7 DAYS → 7 HOURS → "What would you do first?"

Sound: dark synth pads, accelerating sub pulse over days 1–5, sparse plucks on day 7,
heartbeat + riser before impact, full silence at the flash with ear-ringing tone, impact boom,
sad pad afterwards, a silence beat before the twist, then ticking clock + heartbeat.
Phone ping/vibration, alert tone, news sting, crowd murmur, sirens, phone ring, rocket rumble.

## Rebuild

```
pip install faster-whisper numpy pillow   # transcription for word timings
python src/render.py ru words_ru.json <duration> out_ru   # frames → video.mp4
python src/audio.py  ru words_ru.json voice_ru.mp3 mix_ru.wav
python src/thumb.py output
```

`src/timeline.py` holds the on-screen strings and the cue table that anchors each shot to a phrase in the voice-over.
