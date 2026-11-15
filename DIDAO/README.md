# DIDAO — animated series production

```
DIDAO/
├── ASSETS/didao_engine/        shared rendering engine (characters, forest, props, camera, post FX)
└── SEASON_01/
    ├── CONTINUITY_BIBLE/       hero, monster, forest references + season storyline
    └── EPISODE_01/
        ├── character_references/  monster_references/  environment_references/
        ├── prompts/            one shot spec + generation prompt per clip
        ├── clips/              12 separately rendered clips (+ RU variant of clip 12)
        ├── voiceover/ru, en    narration lines (Piper neural TTS) + full timeline stems
        ├── music/  sound_effects/   procedural score and SFX (stems + one-shots)
        ├── subtitles/          .srt and styled .ass, RU + EN
        ├── project_files/      all scripts: script, scenes, render, audio, assembly
        └── final/              DIDAO_EP01_RUSSIAN.mp4, DIDAO_EP01_ENGLISH.mp4, cover
```

## Rebuild the episode
```bash
pip install skia-python numpy pillow scipy piper-tts   # + ffmpeg, Piper voices ru_RU-dmitri-medium, en_US-ryan-high
cd DIDAO/SEASON_01/EPISODE_01/project_files
python make_voiceover.py      # narration (set DIDAO_VOICES to the voice model folder)
python render_clips.py        # 12 clips -> ../clips   (python render_clips.py --preview 7 3.5 for stills)
python make_audio.py          # SFX + score
python assemble.py            # validate, concat, mix, subtitles, grade -> ../final
python make_references.py     # reference sheets + cover
```
