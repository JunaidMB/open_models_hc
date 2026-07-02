"""Shared TTS helper for the podcast and briefing tracks.

Uses the same Qwen3-TTS model as notebooks/local_tts.ipynb. Needs a GPU (CUDA)
or Apple Silicon (MPS). On a CPU-only laptop, generation will be painfully
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
        if torch.cuda.is_available():
            device = "cuda"
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = "mps"
        else:
            raise SystemExit("No CUDA or Apple Silicon GPU found. Rerun with --engine piper (CPU-friendly).")
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
    import sys

    # Anchor the voice next to this file so it downloads once, not once per cwd
    voice_home = Path(__file__).resolve().parent
    if not list(voice_home.glob("en_GB-alba-medium.onnx")):
        subprocess.run(
            [sys.executable, "-m", "piper.download_voices", "en_GB-alba-medium"],
            check=True,
            cwd=voice_home,
        )
    subprocess.run(
        ["piper", "--model", "en_GB-alba-medium", "--output_file", str(Path(out_path).resolve())],
        input=text.encode(),
        check=True,
        cwd=voice_home,
    )
    return out_path


def speak(text: str, out_path: Path, engine: str = "qwen", voice: str | None = None) -> Path:
    if engine == "piper":
        return speak_piper(text, out_path)
    kwargs = {"voice": voice} if voice else {}
    return speak_qwen(text, out_path, **kwargs)
