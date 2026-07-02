"""Screenshot Librarian: a local VLM names, tags, and indexes your screenshots.

Track difficulty: ★ beginner (needs only Ollama + a vision model)

    ollama pull qwen2.5vl:3b        # 8 GB RAM machines: ollama pull moondream

Run once over a folder:
    python screenshot_librarian.py ~/Pictures/Screenshots

Make it ambient (stretch): add --watch and leave it running.

WSL terminal but Ollama on Windows? Run Windows-side (verified):
    powershell.exe -Command "cd <folder with this script>; uv run --no-project --with ollama python screenshot_librarian.py <folder>"
"""

import argparse
import json
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
    "You are naming a screenshot for a searchable library. Return JSON with "
    '"name" (a 3-6 word kebab-case filename describing the content, no extension) '
    'and "tags" (3-5 lowercase tags).'
)

# Structured outputs: the same schema trick as the Activity A exercise. Small
# VLMs often ignore "reply with exactly two lines" prompts; a schema can't be ignored.
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["name", "tags"],
}


def describe(image: Path) -> tuple[str, str]:
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT, "images": [str(image)]}],
        format=SCHEMA,
    )
    data = json.loads(response.message.content)
    slug = re.sub(r"[^a-z0-9-]+", "-", str(data.get("name", "")).lower()).strip("-")
    if not slug:
        # raise instead of filing an "unnamed" dud: the file keeps its name and
        # gets retried on the next run
        raise ValueError(f"no usable name in reply: {response.message.content[:120]}")
    tags = ", ".join(str(t).strip().lower() for t in data.get("tags", []) if str(t).strip())
    return slug[:60], tags


def process_folder(folder: Path, index: Path) -> int:
    processed = 0
    for image in sorted(folder.iterdir()):
        if image.suffix.lower() not in IMAGE_EXTS or DONE_MARKER.match(image.name):
            continue
        try:
            slug, tags = describe(image)
        except Exception as e:
            print(f"  {image.name}: model failed ({e}), skipping")
            continue
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
