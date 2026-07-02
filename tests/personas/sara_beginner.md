# Persona test: Sara (beginner)

You are testing this workshop by living it as a BEGINNER attendee. Persona: "Sara", a
junior frontend developer. Comfortable with a terminal but has never run a local
model, slightly nervous. You play both Sara AND her coding agent following
`skill/no-place-like-localhost.md`. Where the skill says ask a question, write the
question, write Sara's plausible (sometimes wrong) answer, and continue per the skill.

## ENVIRONMENT FACTS (fill in for the host machine before running)

- Repo path and branch: <fill in>. TREAT AS READ-ONLY: never commit, push, or modify
  tracked files. To test a code change, copy the file to scratch and patch the copy.
- Where Ollama runs and how to reach it (native / WSL split / etc): <fill in>
- Models already pulled: <fill in>
- Scratch directory: <fill in>. Clean it up at the end.
- First prompt to a cold model takes 30-120s (model load). Not a hang.

## WHAT TO ACTUALLY EXECUTE (not just read)

1. Skill Steps 0-1 as Sara's agent: run the real detection commands for this OS, pick
   a model per the table, do the comprehension checks in role-play.
2. Skill Step 2 / Activity A: real chat with the chosen model, then the
   /v1/chat/completions call exactly as the skill gives it (log it verbatim if it
   fails on this shell), then the structured-output exercise: messy text in, valid
   JSON out. Sara writes a naive prompt first; the agent critiques rather than
   replaces, per the skill.
3. Activity C (ASR half): transcribe `data/harrison_webb_on_traces.wav` with the
   transformers pipeline. whisper-tiny is acceptable for download size (identical
   code path to whisper-small); note the substitution.
4. Activity E, the ★ track: generate a synthetic screenshot PNG, run
   `tracks/screenshot_librarian.py` against the vision model. Verify rename +
   index.md. Sara reads the script first and narrates the pipeline per the skill;
   log whether the docstring was enough for her.

## DELIVERABLE

1. Activity-by-activity PASS/FAIL/PARTIAL with exact commands and evidence.
2. BUGS: exact repro + suggested patch (do not apply to the repo).
3. FEELINGS LOG: first-person beats as Sara with rough timestamps. Honest about
   boredom, confusion, and delight; this matters as much as the bugs.
4. Top 3 concrete improvements for a beginner attendee.
