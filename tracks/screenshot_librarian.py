"""Screenshot Librarian: a local VLM names, tags, and indexes your screenshots.

Track difficulty: ★ beginner (needs only Ollama + a vision model)

    ollama pull qwen2.5vl:3b        # 8 GB RAM machines: ollama pull moondream

Run once over a folder:
    python screenshot_librarian.py ~/Pictures/Screenshots

Make it ambient (stretch): add --watch and leave it running.
"""

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path

from ollama import chat

MODEL = os.environ.get("VLM_MODEL", "qwen2.5vl:3b")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
DONE_MARKER = re.compile(r"^\d{4}-\d{2}-\d{2}--")  # files we already renamed

PROMPT = (
    "You are naming a screenshot for a searchable library. Reply with exactly two lines:\n"
    "NAME: a 3-6 word kebab-case filename describing the content (no extension)\n"
    "TAGS: 3-5 comma-separated lowercase tags"
)


def describe(image: Path) -> tuple[str, str]:
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT, "images": [str(image)]}],
    )
    text = response.message.content
    name = re.search(r"NAME:\s*(.+)", text)
    tags = re.search(r"TAGS:\s*(.+)", text)
    slug = re.sub(r"[^a-z0-9-]+", "-", (name.group(1) if name else "unnamed").lower()).strip("-")
    return slug[:60], (tags.group(1).strip() if tags else "")


def process_folder(folder: Path, index: Path) -> int:
    processed = 0
    for image in sorted(folder.iterdir()):
        if image.suffix.lower() not in IMAGE_EXTS or DONE_MARKER.match(image.name):
            continue
        slug, tags = describe(image)
        stamp = datetime.fromtimestamp(image.stat().st_mtime).strftime("%Y-%m-%d")
        new_path = image.with_name(f"{stamp}--{slug}{image.suffix.lower()}")
        image.rename(new_path)
        with index.open("a", encoding="utf-8") as f:
            f.write(f"- `{new_path.name}`: {tags}\n")
        print(f"  {image.name}  ->  {new_path.name}   [{tags}]")
        processed += 1
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="folder containing screenshots")
    parser.add_argument("--watch", action="store_true", help="keep running, check every 10s")
    args = parser.parse_args()

    index = args.folder / "index.md"
    print(f"Librarian on duty in {args.folder} (model: {MODEL})")
    while True:
        n = process_folder(args.folder, index)
        if n:
            print(f"Filed {n} screenshot(s). Search them: grep -i <term> {index}")
        if not args.watch:
            break
        time.sleep(10)


if __name__ == "__main__":
    main()
