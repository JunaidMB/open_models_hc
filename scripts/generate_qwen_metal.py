"""Generate images using Qwen-Image-2512 via stable-diffusion-cpp-python.

Automatically merges sharded safetensors into single-file checkpoints
if needed, then runs inference on macOS Metal (or other ggml backends).
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def find_index_file(shard_dir: Path) -> Optional[Path]:
    """Return the first .json file with 'index' in its name, or None."""
    candidates = [f for f in shard_dir.iterdir() if f.suffix == ".json" and "index" in f.name]
    if candidates:
        logger.debug("Found index file: %s", candidates[0])
        return candidates[0]
    return None


def merge_shards(shard_dir: Path, output_path: Path) -> None:
    """Merge sharded safetensors into a single file using the index.

    Skips gracefully if the directory does not exist or contains no shards.
    """
    if not shard_dir.exists():
        logger.warning("Shard directory does not exist: %s", shard_dir)
        return

    # If a single unsharded safetensors file already exists, nothing to do.
    single_files = list(shard_dir.glob("*.safetensors"))
    sharded = [f for f in single_files if "-of-" in f.name]
    unsharded = [f for f in single_files if "-of-" not in f.name]

    if not sharded and unsharded:
        logger.info(
            "Directory %s already contains a single unsharded file (%s); no merge needed.",
            shard_dir,
            unsharded[0].name,
        )
        return

    if not sharded:
        logger.warning("No safetensors files found in %s; nothing to merge.", shard_dir)
        return

    index_file = find_index_file(shard_dir)
    if index_file is None:
        logger.error("Found shards but no .index.json in %s; cannot merge.", shard_dir)
        return

    logger.info("Merging %d shard(s) from %s → %s", len(sharded), shard_dir, output_path)

    from safetensors import safe_open
    from safetensors.torch import save_file

    with open(index_file) as fh:
        index = json.load(fh)

    weight_map = index["weight_map"]
    files_seen = {shard_dir / fn for fn in weight_map.values()}
    tensors = {}

    for full_path in files_seen:
        logger.debug("Reading shard: %s", full_path.name)
        with safe_open(str(full_path), framework="pt", device="cpu") as f:
            for key in f.keys():
                tensors[key] = f.get_tensor(key)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_file(tensors, str(output_path))
    logger.info(
        "Merged %d tensors (%d shards) → %s",
        len(tensors),
        len(files_seen),
        output_path,
    )


def resolve_checkpoint_path(
    shard_dir: Path, merged_name: str, model_root: Path
) -> Optional[Path]:
    """Return the final single-file checkpoint path for a component.

    Priority:
      1. Already-merged file in model_root.
      2. Single unsharded file inside shard_dir.
      3. Merge shards in shard_dir → merged file in model_root.

    Returns None if nothing usable is found.
    """
    merged = model_root / merged_name
    if merged.exists():
        logger.info("Using pre-merged checkpoint: %s", merged)
        return merged

    if not shard_dir.exists():
        logger.error("Neither merged file nor shard directory found: %s", shard_dir)
        return None

    # Look for a single unsharded safetensors file directly in the component dir.
    single_candidates = [
        f for f in shard_dir.glob("*.safetensors") if "-of-" not in f.name
    ]
    if single_candidates:
        candidate = single_candidates[0]
        logger.info("Using single unsharded checkpoint: %s", candidate)
        return candidate

    # Need to merge shards.
    merge_shards(shard_dir, merged)
    if merged.exists():
        return merged

    logger.error("Failed to produce a merged checkpoint for %s", shard_dir)
    return None


def generate(sd, output_path: Path, **kwargs) -> None:
    """Generate an image and save it to disk.

    All keyword arguments are forwarded to ``sd.generate_image()``.
    Commonly-used keys: prompt, negative_prompt, width, height,
    sample_steps, seed, cfg_scale.
    """
    logger.info("Generating image with parameters: %s", kwargs)
    output = sd.generate_image(**kwargs)
    output[0].save(output_path)
    logger.info("Saved output to %s", output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images with Qwen-Image-2512 via stable-diffusion-cpp-python."
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        default=Path("./models/Qwen-Image-2512"),
        help="Root directory containing text_encoder/, transformer/, vae/ subdirectories. "
             "You can also point this at a Hugging Face cache snapshot folder.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./data/qwen_metal_output.png"),
        help="Path to write the generated image.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="a 20-year-old Egyptian hijabi girl at an anime convention",
        help="Text prompt describing the desired image.",
    )
    parser.add_argument(
        "--negative-prompt",
        type=str,
        default="grey, ugly, sad.",
        help="Text prompt describing what to avoid.",
    )
    parser.add_argument(
        "--width", type=int, default=1664, help="Image width in pixels."
    )
    parser.add_argument(
        "--height", type=int, default=928, help="Image height in pixels."
    )
    parser.add_argument(
        "--sample-steps", type=int, default=50, help="Number of denoising steps."
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="RNG seed for reproducibility."
    )
    parser.add_argument(
        "--cfg-scale", type=float, default=4.0, help="Classifier-free guidance scale."
    )
    parser.add_argument(
        "--wtype",
        type=str,
        default="f16",
        choices=["default", "f32", "f16", "q4_0", "q5_1", "q8_0"],
        help="Weight type / quantization for the model.",
    )
    parser.add_argument(
        "--diffusion-flash-attn",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable flash attention in the diffusion transformer.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose backend output.",
    )
    return parser.parse_args()


def main() -> None:
      
    """
    # Custom prompt with different dimensions
    uv run generate_qwen_metal.py \
    --prompt "a futuristic city at sunset" \
    --negative-prompt "sad, sunken colours" \
    --width 1328 \
    --height 1328 \
    --sample_steps 50 \
    --seed 123 \
    --output "data/generated_image.png"
    """
      
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    model_root = args.model_root
    llm_dir = model_root / "text_encoder"
    transformer_dir = model_root / "transformer"
    vae_file = model_root / "vae" / "diffusion_pytorch_model.safetensors"

    logger.info("Model root: %s", model_root.resolve())

    # Resolve single-file paths (merge shards on-the-fly if necessary).
    merged_llm = resolve_checkpoint_path(llm_dir, "text_encoder_merged.safetensors", model_root)
    merged_transformer = resolve_checkpoint_path(
        transformer_dir, "transformer_merged.safetensors", model_root
    )

    if merged_llm is None or merged_transformer is None:
        logger.error(
            "Could not resolve required checkpoints. "
            "Ensure the model is downloaded to %s or specify --model-root.",
            model_root,
        )
        sys.exit(1)

    if not vae_file.exists():
        logger.error("VAE file not found: %s", vae_file)
        sys.exit(1)

    logger.info("Loading model via stable-diffusion-cpp…")
    logger.info("  LLM (text encoder): %s", merged_llm)
    logger.info("  Transformer:        %s", merged_transformer)
    logger.info("  VAE:                %s", vae_file)
    logger.info("  Weight type:        %s", args.wtype)

    from stable_diffusion_cpp import StableDiffusion

    sd = StableDiffusion(
        diffusion_model_path=str(merged_transformer),
        llm_path=str(merged_llm),
        vae_path=str(vae_file),
        wtype=args.wtype,
        diffusion_flash_attn=args.diffusion_flash_attn,
    )
    logger.info("Model loaded successfully.")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    gen_kwargs = {
        "prompt": args.prompt,
        "negative_prompt": args.negative_prompt,
        "width": args.width,
        "height": args.height,
        "sample_steps": args.sample_steps,
        "seed": args.seed,
        "cfg_scale": args.cfg_scale,
    }

    generate(sd, args.output, **gen_kwargs)


if __name__ == "__main__":
    main()
