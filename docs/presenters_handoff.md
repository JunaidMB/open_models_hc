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
- Known repo issue: `uv sync` FAILS on native Windows because `qwen3-tts` pulls in
  `mlx` (no Windows wheels). The skill routes Windows attendees around it.

NOT yet verified anywhere (this is the macOS test list, ~30-45 min):
1. `uv venv && uv sync` on macOS (mlx has darwin wheels, so it should pass; confirm).
2. The TTS path on Apple Silicon (MPS): run `notebooks/local_tts.ipynb`, then
   `tracks/private_podcast.py` on a short article. `tts_helper.py` handles the
   generate_voice_design return shape defensively; confirm audio actually plays.
3. `tracks/screenshot_librarian.py` end to end against a live Ollama
   (`ollama pull qwen2.5vl:3b`, drop one screenshot in a test folder).
4. `tracks/morning_briefing.py --text-only`, then with TTS.
5. The skill as an attendee: install it
   (`mkdir -p ~/.claude/commands && cp skill/no-place-like-localhost.md ~/.claude/commands/`),
   open a fresh Claude Code session, invoke it, and role-play a mac attendee through
   Steps 0-2 and one track. The Windows path was tested this way; the mac path wasn't.
6. Deck on the actual projector resolution if available; otherwise trust the 1080p
   overflow checks already done.

Do all model pulls (qwen3:4b, qwen2.5vl:3b, Whisper small, Qwen3-TTS 1.7B) on home
WiFi the night before. Venue WiFi is for attendees.

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

# Python env + HF model weights (~5 GB)
uv venv && uv sync && uv pip install -U qwen-tts
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
  worthwhile, PEP 723 inline deps would fix the Windows uv sync issue properly);
  fix `pyproject.toml` so `qwen3-tts`/`mlx` is darwin-only or an optional extra.
- Companion skill distribution: QR code to wherever the skill is hosted
  (luqmaan.dev/skills/ pattern from the previous Agents Assemble session, or raw
  GitHub URL of this branch).
