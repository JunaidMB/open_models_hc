# Presenters' Handoff: state of play before the session

Written so a coding agent (or a human) on any machine can pick up exactly where prep
left off. On a new machine: clone the repo, check out `productising-local-models`,
open a coding agent in the repo root, and say "read docs/presenters_handoff.md and
skill/no-place-like-localhost.md".

## Where everything lives

- Branch `productising-local-models`, PR #2 on JunaidMB/open_models_hc. Contains the
  full deck, the four `tracks/` starter products, the companion skill, and doc updates.
- `presentation.html` is fully self-contained (no build step, works offline, from
  file:// or any static server). 30 slides. `#N` in the URL deep-links to slide N;
  arrow keys, click zones, and touch swipe navigate.
- Session: Hulm Club Tech Guild, 2 July 2026, 18:00-20:00. Luqmaan presents with
  Junaid; one presents while the other circulates.

## Decisions already made (don't relitigate)

- Activities are labelled A-F on slides, in the skill, and in docs/activities_links.md.
  A: Ollama. B: coding harness (OpenCode, not Continue.dev). C: speech and TTS.
  D: image gen (optional, presenter-led). E: ship something (the four tracks).
  F: fine-tune, take-home.
- The framing thesis: the OpenAI-compatible API is how local models become products;
  the recipe is trigger, then a small model, then an artifact.
- The companion skill is deliberately Socratic: agents guide, attendees type and
  decide. Don't "fix" it into a task-runner.
- No em dashes in any new written material (presenter preference).
- The right-sizing tool is `llmfit` (github.com/AlexsJones/llmfit). Unified memory
  claim, verified: capacity is the win, speed is not (M4 Max 546 GB/s vs ~1 TB/s on
  an RTX 4090; decode 2-3x slower like-for-like, prefill worse).
- Post-training slides (25-27) stay intentionally technical. Open question for Junaid
  on the PR: what LFM stands for on the Open Alternatives slide.

## Test status: what has and hasn't been verified

Overnight persona testing (see tests/: three attendee personas run live on WSL2 +
Windows Ollama + RTX 4080; reports in tests/persona_reports/, all found bugs fixed
and regression-tested in tests/smoke.py):
- Beginner (Sara): Activities A, C, E(*) pass; PowerShell curl trap and librarian
  silent-failure fixed
- Builder (Maya): all three audio pipelines pass end to end Windows-side with piper;
  RSS absolute-URL bug fixed; piper-tts confirmed installing on native Windows
- Speedrunner (Deen): OpenCode installs in minutes (config now shipped at
  docs/opencode.example.json); five-star tier achievable in ~20 min; --watch
  collision crash, poison-image retry loop, and missing num_predict cap fixed

Earlier verification on the same machine (simulated attendee run):
- Skill flow end to end, Windows/WSL split guidance, powershell.exe interop.
- Python-to-Ollama round trip Windows-side via `uv run --no-project --with ollama`.
- `screenshot_librarian.py` fails cleanly and correctly when Ollama is unreachable.

macOS verification, 2 July afternoon (M-series MacBook, the demo machine):
1. `uv venv && uv sync` PASSES on macOS, and now on native Windows too. The old
   failure (`qwen3-tts` pulling `mlx`, no Windows wheels) is fixed at the root:
   `pyproject.toml` now depends on `qwen-tts` (the PyTorch package the code
   actually imports) with `transformers==4.57.3`, and drops `qwen3-tts`, which
   nothing imported. transformers 5.x breaks qwen-tts's model load; do not
   re-raise the pin without testing TTS.
2. TTS on Apple Silicon (MPS) PASSES: Qwen3-TTS VoiceDesign generated real,
   audible audio in ~39s cold (model load included), ~12s of speech. Note: torch
   from PyPI on native Windows is CPU-only, so Windows TTS stays on piper.
3. `screenshot_librarian.py` PASSES against live Ollama + qwen2.5vl:3b (renamed,
   tagged, indexed a real screenshot).
4. `morning_briefing.py --text-only` PASSES (live weather + calendar + todos all
   in the script). Full-TTS run and `private_podcast.py` in progress.
5. `tests/smoke.py`: all six mechanical tests pass on macOS.

6. The skill as a mac attendee PASSES (persona run, see
   tests/persona_reports/2026-07-02_priya_mac_beginner.md). Critical catch, fixed:
   qwen3 + response_format on /v1 returns empty content; skill and the Activity A
   notebook now use the native client with think=False + format=schema. The
   notebook (which hardcoded lfm2.5 and had empty exercise cells) now scaffolds
   the full structured-output exercise; executed clean end to end.
7. Full podcast pipeline PASSES on Apple Silicon (two real episodes over MPS,
   LAN feed fetches HTTP 200); spaced --title feed-URL bug found and fixed.

Still open:
- Deck on the actual projector resolution if available; otherwise trust the 1080p
  overflow checks already done.

Do all model pulls (qwen3:4b, qwen2.5vl:3b, Whisper small, Qwen3-TTS 1.7B) on home
WiFi the night before. Venue WiFi is for attendees. (Done on the MacBook, 2 July.)

## One-shot prefetch (run on home WiFi, walk away)

Roughly 12-15 GB total. From the repo root on the MacBook:

```bash
# Tools (skip any already installed)
brew install ollama llmfit
curl -fsSL https://opencode.ai/install | bash   # or: npm i -g opencode-ai

# Ollama models (fetches in sequence; ~9 GB)
ollama pull qwen3:4b
ollama pull qwen2.5vl:3b
ollama pull qwen3:1.7b        # fallback for demoing the weak-machine path

# Python env + HF model weights (~5 GB); qwen-tts is a declared dependency now
uv venv && uv sync
uv run python -c "from transformers import pipeline; pipeline('automatic-speech-recognition', model='openai/whisper-small')"
uv run python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign')"
```

Notes: the TTS snapshot may need a Hugging Face token (`cp .env_example .env`, add
`HUGGINGFACEHUB_API_TOKEN`, or `huggingface-cli login`) if the repo is gated. Also
download Handy (handy.computer) for the Wispr Flow replacement demo, and have Claude
Code installed for the skill test.

## Remaining open items

- Junaid to answer the LFM question on PR #2 and review/merge.
- Optional post-workshop: convert the three local notebooks to marimo (assessed as
  worthwhile; PEP 723 inline deps would isolate each notebook's environment).
  The `qwen3-tts`/`mlx` pyproject issue is already fixed (2 July).
- Companion skill distribution: DONE. Served at https://luqmaan.dev/skills/localhost
  (text/markdown, Cloudflare Pages); QR on the MacBook Desktop
  (localhost-workshop-skill-qr.png) decodes to that URL. Note the site copy is a
  snapshot: if the skill changes again, re-copy it to public/skills/localhost.md
  in the luqmaan.dev repo and push (deploy is automatic).
