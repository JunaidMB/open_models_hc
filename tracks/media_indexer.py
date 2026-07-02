"""Media-Library Indexer: transcribe every audio file in a folder into a searchable index.

Track difficulty: ★★ (needs the repo's Python env: transformers + librosa)

Why local wins here: transcription APIs charge per minute. Ten years of voice
memos, lecture recordings, or podcast backlogs cost £0 overnight on your own CPU.

    python media_indexer.py ./media

Outputs transcripts/<name>.md per file plus a master index.md.
Stretch: add an Ollama one-line summary per file; run nightly via cron/Task Scheduler.
"""

import argparse
from pathlib import Path

from transformers import pipeline

AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".mp4"}


def build_transcriber():
    # Same model family as notebooks/local_transcription.ipynb; the pipeline
    # handles long recordings by chunking, which the raw processor does not.
    return pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        chunk_length_s=30,
        return_timestamps=True,
    )


def summarise(text: str) -> str:
    """Stretch goal: one-line summary via your local LLM. Uncomment to enable."""
    # from ollama import chat
    # response = chat(model="qwen3:4b", messages=[{
    #     "role": "user",
    #     "content": "Summarise this transcript in one sentence:\n\n" + text[:6000],
    # }])
    # return response.message.content.strip()
    return text[:120].replace("\n", " ") + "..."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="folder of audio/video files")
    args = parser.parse_args()

    out_dir = args.folder / "transcripts"
    out_dir.mkdir(exist_ok=True)
    index = args.folder / "index.md"

    files = [f for f in sorted(args.folder.iterdir()) if f.suffix.lower() in AUDIO_EXTS]
    todo = [f for f in files if not (out_dir / f"{f.stem}.md").exists()]
    print(f"{len(files)} media file(s) found, {len(todo)} to transcribe.")
    if not todo:
        return

    transcriber = build_transcriber()
    for f in todo:
        print(f"Transcribing {f.name} ...")
        result = transcriber(str(f))
        lines = [f"# {f.name}\n"]
        for chunk in result.get("chunks", [{"timestamp": (0, None), "text": result["text"]}]):
            start = chunk["timestamp"][0] or 0
            lines.append(f"**[{int(start // 60):02d}:{int(start % 60):02d}]** {chunk['text'].strip()}\n")
        (out_dir / f"{f.stem}.md").write_text("\n".join(lines), encoding="utf-8")
        with index.open("a", encoding="utf-8") as idx:
            idx.write(f"- [{f.name}](transcripts/{f.stem}.md): {summarise(result['text'])}\n")
        print(f"  -> transcripts/{f.stem}.md")

    print(f"\nDone. Search your library: grep -ri <term> {out_dir}")


if __name__ == "__main__":
    main()
