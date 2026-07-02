# Open Models User Guide

A practical guide to running, understanding, and fine-tuning open-weight language models on consumer hardware and beyond.

## What's inside

- **`docs/open_models_guide.md`** — A tutorial covering open vs. closed models, the Hugging Face ecosystem, model selection for your hardware, quantization, inference servers, and cloud scaling.
- **`docs/post_training_unsloth.md`** — An explainer on post-training: SFT, reinforcement learning with verifiable rewards (RLVR), and Group Relative Policy Optimization (GRPO) using [Unsloth](https://unsloth.ai).
- **`docs/activities_links.md`** — Curated links and references for each hands-on activity in the slide deck (Ollama setup, coding harnesses, TTS, open alternatives, and Colab notebooks).
- **`presentation.html`** — An interactive slide deck summarizing both guides.
- **`tracks/`**: Four "ship something" starter scripts for the final activity. Each is a small end-to-end product that replaces a paid service, built on the same stack as the notebooks:
  - ★ `screenshot_librarian.py`: a local VLM names, tags, and indexes your screenshots (needs Ollama only)
  - ★★ `media_indexer.py`: transcribe a folder of audio into a searchable index with Whisper
  - ★★★ `private_podcast.py`: any article → local LLM rewrite → Qwen TTS → a private podcast feed on your LAN
  - ★★★ `morning_briefing.py`: calendar, todos, and weather → a spoken daily briefing (add cron to make it ambient)
- **`skill/no-place-like-localhost.md`**: A companion skill for attendees' coding agents (Claude Code / OpenCode). It detects their OS/RAM/GPU (including the Windows-vs-WSL split), then guides them through model sizing, setup, the exercises, and the tracks Socratically: questions and decisions, not done-for-you commands.
- **`.env_example`** — Template for API keys (Hugging Face, Weights & Biases).
- **`notebooks/`** — Runnable examples:
  - `image_generation_diffusers.ipynb` — Generate images from text prompts using diffusion models via [Lightning AI](https://lightning.ai/junaid-trusting-personal/vision-model/studios/qwen-ts/code). Requires GPU credits. Or run locally on a sufficiently powerful machine by switching `cuda` to `mps`.
  - `local_transcription.ipynb` — Transcribe audio locally with Whisper
  - `ollama_openai_api.ipynb` — List local models and chat via Ollama's OpenAI-compatible API
  - `voice_design_weave.ipynb` — Design custom voices and generate speech with Qwen TTS

## Core stack

| Library | Role |
|---------|------|
| [Ollama](https://ollama.com) | Beginner-friendly local inference server — one command to pull and run models |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Portable inference on CPUs, edge devices, and unusual hardware |
| [vLLM](https://github.com/vllm-project/vllm) | Production-grade throughput with PagedAttention for serving many users |
| [Hugging Face](https://huggingface.co) | The central model hub — discover, download, and share open weights |
| [Unsloth](https://unsloth.ai) | Memory-efficient fine-tuning (SFT and GRPO) on consumer GPUs |

## Quick start

1. Copy `.env_example` to `.env` and add your API keys.
2. Read `docs/open_models_guide.md` for an introduction to the open-model ecosystem.
3. Read `docs/post_training_unsloth.md` to understand how to fine-tune and deploy models.
4. Open `presentation.html` in a browser for a slide-deck overview.

## Requirements

- Python ≥ 3.14
- A GPU with sufficient VRAM for the models you intend to run (see the hardware sizing tables in the guide)

## Setup

Create a virtual environment and install dependencies with [uv](https://docs.astral.sh/uv):

```bash
uv venv
source .venv/bin/activate
uv sync
```

On Windows:

```bash
uv venv
.venv\Scripts\activate
uv sync
```
