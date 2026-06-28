# Open Models Quick-Reference Cheatsheet

## Ollama Commands

| Command | Description |
|---------|-------------|
| `ollama pull <model>` | Download a model from the Ollama Hub |
| `ollama run <model>` | Start an interactive chat session |
| `ollama list` | Show all locally cached models |
| `ollama rm <model>` | Remove a model from local cache |
| `ollama ps` | Show currently running models |
| `ollama stop <model>` | Stop a running model |
| `ollama serve` | Start the Ollama API server (background daemon) |
| `ollama create <name> -f Modelfile` | Import a custom GGUF model |
| `ollama show <model>` | Display model info, parameters, and system prompt |
| `ollama cp <src> <dst>` | Copy a model to a new name |

---

## vLLM & llama.cpp Commands

| Command | Description |
|---------|-------------|
| `vllm serve <model>` | Start an OpenAI-compatible API server |
| `vllm serve <model> --tensor-parallel-size 2` | Serve with multi-GPU tensor parallelism |
| `vllm serve <model> --max-model-len 16384` | Override default context window |
| `python -m llama_cpp.server --model <gguf>` | Start a llama.cpp HTTP server |
| `make -C llama.cpp` | Build llama.cpp from source |
| `cmake -B build && cmake --build build --config Release` | Build llama.cpp with CMake |
| `python llama.cpp/convert_hf_to_gguf.py <hf_model> --outfile <out.gguf> --outtype q4_k_m` | Convert HF checkpoint to GGUF |

---

## Hugging Face CLI

| Command | Description |
|---------|-------------|
| `huggingface-cli login` | Authenticate with your Hugging Face token |
| `huggingface-cli download <repo>` | Download a model repo to the local cache |
| `huggingface-cli download <repo> --local-dir ./models` | Download to a specific directory |
| `huggingface-cli scan-cache` | List cached models and their disk usage |
| `huggingface-cli delete-cache` | Interactive cache cleanup |
| `huggingface-cli repo create <name> --type model` | Create a new model repo |
| `huggingface-cli upload <repo> <file>` | Upload a file to a model repo |
| `git clone https://huggingface.co/<repo>` | Clone a model repo with Git LFS |

---

## Quantization Memory Footprints

Model memory ≈ parameters × bytes-per-param. Values below include ~20% headroom for KV cache.

| Size | Q4_K_M (~0.5B/param) | Q8_0 (~1B/param) | FP16 (~2B/param) |
|------|------------------------|-------------------|------------------|
| **1B** | ~0.7 GB | ~1.3 GB | ~2.5 GB |
| **3B** | ~2.0 GB | ~3.8 GB | ~7.5 GB |
| **7B** | ~4.5 GB | ~8.5 GB | ~17 GB |
| **8B** | ~5.0 GB | ~9.5 GB | ~19 GB |
| **13B** | ~8.5 GB | ~16 GB | ~32 GB |
| **30B** | ~19 GB | ~37 GB | ~75 GB |
| **70B** | ~45 GB | ~85 GB | ~170 GB |

---

## Ollama Model Tags

| Tag | Meaning |
|-----|---------|
| `:latest` | Default tag, usually points to the largest + best-quantized variant |
| `:7b`, `:13b`, `:70b` | Parameter count variant |
| `:q4`, `:q5`, `:q8` | Quantization bit width shorthand |
| `:fp16` | Full 16-bit precision, no quantization |
| `:text` | Base (pre-trained) model, not aligned for chat |
| `:instruct` | Fine-tuned for instruction following |
| `:chat` | Fine-tuned for conversational dialogue |
| `:code` | Fine-tuned on code corpora |
| `:vision` | Multimodal, accepts image inputs |

---

## PyTorch / CUDA Version Pairings

| PyTorch | CUDA | Install command |
|---------|------|-----------------|
| 2.6 | 12.6 / 12.4 | `pip install torch` (default) |
| 2.5 | 12.1 / 11.8 | legacy stable |
| 2.4 | 12.1 / 11.8 | legacy stable |
| 2.3 | 12.1 / 11.8 | legacy stable |
| 2.2 | 12.1 / 11.8 | legacy stable |

Verify your active CUDA:
```bash
python -c "import torch; print(torch.version.cuda)"
python -c "import torch; print(torch.cuda.is_available())"
```

---

## Ollama Environment Variables

| Variable | Default | Effect |
|----------|---------|--------|
| `OLLAMA_HOST` | `127.0.0.1:11434` | Bind address for the API server |
| `OLLAMA_MODELS` | `~/.ollama/models` | Local model storage directory |
| `OLLAMA_KEEP_ALIVE` | `5m` | How long to keep a model loaded after last request |
| `OLLAMA_NUM_PARALLEL` | `1` | Max concurrent requests per model |
| `OLLAMA_FLASH_ATTENTION` | `0` | Enable flash attention (`1`) for lower VRAM usage |
| `OLLAMA_MAX_LOADED_MODELS` | `1` | Max models to keep in VRAM simultaneously |
| `OLLAMA_NOHISTORY` | `0` | Disable readline history in the REPL |
| `OLLAMA_DEBUG` | `0` | Enable verbose debug logging |

Set in your shell or `~/.zshrc` / `~/.bashrc`:
```bash
export OLLAMA_KEEP_ALIVE=30m
export OLLAMA_FLASH_ATTENTION=1
```

---

## Hugging Face → GGUF Conversion

Requires a cloned llama.cpp repo.

```bash
# 1. Install dependencies
pip install gguf protobuf sentencepiece

# 2. Run the converter
python /path/to/llama.cpp/convert_hf_to_gguf.py \
    ./my-hf-model \
    --outfile my-model-q4.gguf \
    --outtype q4_k_m
```

| `--outtype` | Description |
|-------------|-------------|
| `q4_0` | Legacy 4-bit, block-wise |
| `q4_k_m` | K-quant medium (recommended default) |
| `q4_k_s` | K-quant small (smaller, lower quality) |
| `q4_k_l` | K-quant large (larger, higher quality) |
| `q5_k_m` | 5-bit K-quant medium |
| `q8_0` | 8-bit, near-FP16 quality |
| `f16` | Full 16-bit FP16 |
| `bf16` | BFloat16 |
| `auto` | Pick quantization based on config |

---

## Git LFS Commands for Model Repos

| Command | Description |
|---------|-------------|
| `git lfs install` | Initialize Git LFS for your user account |
| `git lfs track "*.bin"` | Track large binary files by pattern |
| `git lfs ls-files` | List LFS-tracked files in the repo |
| `git lfs pull` | Download LFS objects for the current checkout |
| `git lfs fetch --all` | Download all LFS objects for all branches |
| `git lfs uninstall` | Remove LFS hooks from the repo |
| `GIT_LFS_SKIP_SMUDGE=1 git clone <repo>` | Clone without downloading LFS files (fast, metadata only) |
| `git lfs migrate import --include="*.bin"` | Convert existing large files to LFS retroactively |
| `git lfs dedup` | Deduplicate LFS objects locally (Windows ReFS only) |
