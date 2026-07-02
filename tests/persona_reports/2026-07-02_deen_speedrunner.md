# Persona run: Deen (advanced speedrunner) — 2026-07-02, pre-session overnight

Machine: WSL2 terminal + native Windows Ollama (RTX 4080 16GB), heavy GPU contention
from parallel persona tests (realistic for a workshop room). All bugs below were
fixed on this branch the same night.

## Results

| Item | Verdict | Notes |
|---|---|---|
| Activity B: OpenCode + Ollama | PASS plumbing, PARTIAL exercise | `npm i -g opencode-ai` → working in under 5 min. But models are NOT auto-discovered: a provider block in `opencode.json` is required (now shipped as `docs/opencode.example.json`). qwen3:4b at ~31 tok/s never produced a grounded answer in 3 runs: one fluent hallucination, one degenerate refusal after a real tool call, one raw function-call emitted as text |
| ★★★★★ go build something cool | PASS in ~20 min | built downloads_triage.py (folder → qwen3:4b → triage_plan.md). Iteration arc: format="json" gave a different JSON shape every run; an explicit schema gave 15/15 files sorted correctly. The tier is achievable and organically teaches schema-constrained decoding |
| Ambient --watch stretch | PARTIAL | loop mechanics work (image 1 renamed in 4s on a quiet GPU) but a filename collision crashed the watcher; see bugs |
| Skill stress-read | findings below | non-negotiables read as gatekeeping for fast attendees |

## Bugs found (all fixed on this branch)

1. **Filename collision crash / silent data loss.** Two same-day screenshots with
   the same slug: FileExistsError kills the watcher on Windows; on POSIX rename
   silently overwrites the earlier screenshot. Fixed: unique_path() dedupe (-2, -3
   suffixes) and the rename moved inside the try. Regression-tested in smoke.py.
2. **Poison-image infinite retry.** An always-failing image was retried every 10s
   forever (22 observed model calls). Fixed: 3 attempts per session, then skip.
3. **No generation cap.** moondream free-ran to a 54K-char response on an ambiguous
   image. Fixed: num_predict=120 on the librarian call.
4. **index.md entries could collide.** Fixed by (1); names are now unique.
5. **Activity B oversold on the slide** ("models plug straight into its CLI").
   Fixed: slide and skill now ship the provider config and reframe the exercise as
   observing HOW a 4B model fails in a harness, which is the honest and more
   interesting version.

Also fed into the skill: moondream cannot complete the librarian track (annotated in
the sizing table); a sharing-the-GPU troubleshooting entry (ollama ps, ollama stop,
GGML 500 = retry); an advanced lane (gatekeeper → reviewer at the stretch tiers,
gates on design decisions rather than command ceremony).

## Feelings highlights (verbatim from the run)

- "npm install to working local coding agent in under 5 minutes felt great."
- "The ★★★★★ tier is the best-designed part of the night... the JSON-shape-roulette
  to structured-outputs arc was a real aha I earned myself."
- "Activity B's experiment step assumes the model can do the task; qwen3:4b never
  once produced a grounded answer, and the slide gives me no vocabulary for that
  outcome." (Fixed: the failure modes ARE now the exercise.)
- "The 'pace to the room' rule only licenses harder questions for fast attendees,
  not less ceremony; those are different things." (Fixed.)
