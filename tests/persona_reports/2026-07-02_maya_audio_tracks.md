# Persona run: Maya (audio tracks) — 2026-07-02, pre-session overnight

Machine: WSL2 terminal + native Windows Ollama (RTX 4080 16GB), piper TTS engine.
All bugs below were fixed on this branch the same night (commit `3a1454c`).

## Results

| Pipeline | Verdict | Notes |
|---|---|---|
| private_podcast.py (whole run Windows-side) | PASS | piper-tts installs and runs fine on native Windows (previously unknown). 130s episode from a real article, no thinking-tag leakage into audio |
| Feed serving (http.server + curl) | PASS mechanically | but see BUG 1 |
| morning_briefing.py (full audio) | PASS | all 4 calendar items in the script + live weather; todos were dropped (fixed: prompt now asks for both) |
| media_indexer.py (fresh piper-generated audio) | PASS | near-verbatim transcript with timestamps; whisper-tiny used for speed |

## Bugs found (all fixed in `3a1454c`)

1. **RSS enclosure URLs were relative.** Real podcast apps require absolute URLs; the
   advertised subscribe-from-phone step failed at the last moment. Fixed: feed now
   uses `http://<detected-lan-ip>:8000` (or `--base-url`) for enclosures, guids, and
   the channel link. Covered by `tests/smoke.py`.
2. **Piper voices downloaded into every cwd.** Fixed: anchored next to the script.
3. **tts_helper crashed opaquely on CPU-only machines** (invalid `mps` device).
   Fixed: clear "rerun with --engine piper" exit.

## Feelings highlights (verbatim from the run)

- "Dread then delight at the Windows/WSL split... one powershell.exe one-liner did
  the entire podcast pipeline in one go. But nothing told me this was the move."
  (Fixed: the one-liner is now in the track docstrings.)
- "The cold-start silence is scary... I nearly Ctrl-C'd." (Fixed: latency notes
  printed before the first model call.)
- "Genuine delight: hearing my own calendar read back in a Scottish accent 25
  seconds after typing the command. That's the demo moment; it lands."
- "Betrayal at the finish line: the podcast track's whole pitch is subscribe from
  your phone, and that exact step is the broken one." (Fixed.)
