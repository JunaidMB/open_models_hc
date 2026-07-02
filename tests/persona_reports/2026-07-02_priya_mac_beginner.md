# Persona run: Priya (mac beginner) — 2026-07-02, pre-session afternoon

Machine: the actual presenter MacBook (Apple M4, 32 GB unified, macOS). Ollama local
with qwen3:4b, qwen2.5vl:3b, qwen3:1.7b; repo venv ready. The mac counterpart of the
Sara/Maya/Deen Windows runs. All fixes below were applied on this branch the same
afternoon. TTS/podcast tracks not re-run here (verified separately the same day).

## Results

| Stage | Verdict | Notes |
|---|---|---|
| Step 0 detection | PASS | all mac commands work verbatim; `sysctl hw.memsize` prints raw bytes (skill now prefers `system_profiler`) |
| Step 1 model choice | PASS | M-series gate failed on first guess, landed on second, as designed. `llmfit` TUI vs `llmfit fit` gotcha (fixed); top recommendations were obscure 35B community fine-tunes (caveat extended) |
| Step 2 curl gate | PASS verbatim | 15.7s; prediction mismatch ("expected an API-key error") was the best teaching moment. curl progress table looked like an error (skill now uses `-s`) |
| Activity A structured output | PASS only via native API | THE critical finding, see below |
| Activity E (★ librarian) | PASS | 15.3s for two images incl. model load; idempotent re-run confirmed; the "3b VLM = ~11 GB" claim verified exactly in `ollama ps` |

## The critical finding (fixed in skill + notebook)

With qwen3, `response_format` on the OpenAI-style `/v1` endpoint spends the entire
token budget in the reasoning channel: unbounded it hung 6+ minutes and had to be
killed; capped (300 and 2,500 tokens) it returned `finish_reason: length` with EMPTY
content. `/no_think` does not work over the API. The working pattern, which
`screenshot_librarian.py` already models: native `ollama` client with `think=False`
and `format=<schema>` (3.0s, 77 tokens, valid JSON). The skill now steers attendees
there up front, and `notebooks/ollama_openai_api.ipynb` (which hardcoded
`lfm2.5:latest` and had five empty cells) now scaffolds the whole exercise with that
pattern; executed end-to-end clean on this machine.

Also fed back into the skill: thinking latency is per-request, not just first-load
(one naive extraction burned 3m20s thinking); reasoning arrives in a separate
`reasoning` JSON field over the API rather than the REPL's visible stream.

## Pacing

Steps 0-2 plus one track measured at ~55-80 min. Comfortably inside a 2-hour session
with slides, now that the Activity A landmine is patched (the unpatched hole cost
40+ min in testing).

## Feelings highlights (verbatim from the run)

- "Wait, that's it for setup? I was braced for an hour of Docker."
- "I predicted a login error and it just... answered. From my laptop. Offline??"
- "Did I break it? Is it thinking about me?" (3-minute silent thinking wait)
- "It literally used all 2,500 tokens saying nothing. I hate it here."
- "Sixty times faster. Write that down." (native API + think=False)
- "The schema made it well-formed, not right. I caught the AI being wrong."
- "It *named my screenshots*. I'm running this on my real Screenshots folder
  tonight, no cloud, nobody sees them but me."
