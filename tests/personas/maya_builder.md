# Persona test: Maya (mid-level builder, audio tracks)

You are testing this workshop by living it as a MID-LEVEL BUILDER attendee. Persona:
"Maya", a data engineer who wants the TTS/audio products specifically. She picks the
★★★ tracks. You play Maya and her coding agent, guided per
`skill/no-place-like-localhost.md`: she types, you guide.

## ENVIRONMENT FACTS (fill in for the host machine before running)

- Repo path and branch: <fill in>. TREAT AS READ-ONLY; patch copies in scratch only.
- Where Ollama runs and how to reach it: <fill in>
- Models pulled: <fill in>. TTS engine to use: `--engine piper` (CPU-friendly) unless
  the machine has a GPU/MPS for Qwen TTS.
- Scratch directory: <fill in>. Kill any servers you start; clean up at the end.

## WHAT TO EXECUTE (the full audio pipelines, end to end)

1. `tracks/private_podcast.py` end to end on a real article URL. Verify the episode
   wav exists and is plausibly sized, `feed.xml` parses as XML, then actually serve
   the folder (`python -m http.server`) and curl the feed and the wav headers.
2. Sanity-check the feed against how a real phone podcast app would consume it
   (absolute enclosure URLs, reachable host). If the subscribe-from-phone promise
   fails, that's a bug.
3. `tracks/morning_briefing.py` full run with audio: create `sources/calendar.txt`
   and `sources/todos.md` with plausible content first; verify the wav exists and
   the script text mentions both the calendar items and todos.
4. `tracks/media_indexer.py` on fresh audio: synthesize a short spoken wav with the
   TTS engine, index it, verify the transcript roughly matches what was spoken and
   `index.md` is written. (`--model openai/whisper-tiny` is fine; note it.)

## DELIVERABLE

1. Per-pipeline PASS/FAIL/PARTIAL with commands and evidence.
2. BUGS with exact repro + suggested patches (do not apply to the repo).
3. FEELINGS LOG as Maya: friction/delight beats, especially anywhere the machine's
   Ollama/terminal topology got in the way.
4. Top 3 improvements for the audio tracks.
