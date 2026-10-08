# Snowmoon Chapter 7 - "The Final Round" (adaptation)

Adaptation of Chapter 7 of Vitalik Buterin's novel *Snowmoon* (GPL v3): https://vitalik.eth.limo/snowmoon/html/chapter-7.html
Scene: the Minpentai city final between Zei and Bai, where both players' AIs can read each other's thoughts, and Zei wins with a hidden factory.

## What is in this repo
- `render_motion_graphics.py` - Python script (numpy, OpenCV, Pillow, ffmpeg) that renders the 84-second motion-graphics video: a two-colour cellular-automaton "Minpentai" battle (Zei = teal, Bai = magenta), AI-transcript panels, score HUD, subtitles and a procedurally generated ambient soundtrack.
- `render_eth_characters.py` - renders the character version: Zei, Bai, Mu and Fin with the Ethereum diamond as their face, lip-synced dialogue (mouths follow `voice.wav` loudness if present, otherwise a talking animation), subtitles and an ambient soundtrack. Put a recorded `voice.wav` (84 s, lines at the times in `voiceover.txt`) next to the script to include real voice.
- `subtitles.srt` - subtitle timings that match `voiceover.txt`.
- `prompts.md` - character sheets, style lock and 9 shot prompts for AI video tools.
- `voiceover.txt` - English narration script.

## Pipeline
1. Read Chapter 7 and break it into 9 beats (courtyard, smoke over the city, toast, new rule, trap, the click, win, Mu's lesson, purple letter).
2. Run `python3 render_motion_graphics.py` -> `snowmoon_chapter7.mp4` (requires ffmpeg).
3. (Optional) Generate live-action shots with an AI video model using `prompts.md`, record the voiceover from `voiceover.txt`, and edit everything together in a video editor.

## Tools / models
Python, numpy, OpenCV, Pillow, scipy, ffmpeg. Script and prompts written with Claude (Anthropic). Add any video/voice tools you used here.

## License
GPL v3, same as the source novel.

## Voice
`tts.py` + `build_voice.py` generate the voices offline with Flite (CMU open-source speech synthesis, via its shared libraries): narrator, Zei, Bai and Mu each get a different voice/pitch, fitted to the timings in `render_eth_characters.py` and written to `voice.wav`. `render_eth_characters.py` then drives each speaking character's mouth from the loudness of `voice.wav` and mixes the voice over the ambient soundtrack. Flite voices are robotic; replace `voice.wav` with ElevenLabs or recorded audio (same timings, 84 s) and re-run the renderer for a more natural result.
