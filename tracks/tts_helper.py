"""Shared TTS helper for the podcast and briefing tracks.

Uses the same Qwen3-TTS model as notebooks/local_tts.ipynb. Needs a GPU (CUDA)
or Apple Silicon (MPS) — on a CPU-only laptop, generation will be painfully
slow. CPU fallback: `uv pip install piper-tts` and pass --engine piper.
"""

from pathlib import Path

_qwen_model = None


def speak_qwen(text: str, out_path: Path, voice: str = "A warm, clear narrator with a calm pace.") -> Path:
    global _qwen_model
    import torch
    import soundfile as sf
    from huggingface_hub import snapshot_download
    from qwen_tts import Qwen3TTSModel

    if _qwen_model is None:
        device = "cuda" if torch.cuda.is_available() else "mps"
        _qwen_model = Qwen3TTSModel.from_pretrained(
            snapshot_download("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"),
            device_map=torch.device(device),
            dtype=torch.bfloat16,
        )
    wavs, sr = _qwen_model.generate_voice_design(
        text=text.strip(),
        language="Auto",
        instruct=voice,
        non_streaming_mode=True,
        max_new_tokens=4096,
    )
    audio = wavs[0] if isinstance(wavs, (list, tuple)) else wavs
    sf.write(out_path, audio, sr, subtype="PCM_16")
    return out_path


def speak_piper(text: str, out_path: Path) -> Path:
    """CPU-friendly fallback (~50 MB model, real-time on any laptop)."""
    import subprocess

    subprocess.run(
        ["piper", "--model", "en_GB-alba-medium", "--output_file", str(out_path)],
        input=text.encode(),
        check=True,
    )
    return out_path


def speak(text: str, out_path: Path, engine: str = "qwen", voice: str | None = None) -> Path:
    if engine == "piper":
        return speak_piper(text, out_path)
    kwargs = {"voice": voice} if voice else {}
    return speak_qwen(text, out_path, **kwargs)
