"""Private Podcast: turn any article into an episode in a podcast feed only you can hear.

Track difficulty: ★★★ (needs Ollama + the repo's TTS setup, GPU/MPS recommended)

ElevenLabs + a read-later service, replaced by two local models.

    python private_podcast.py https://example.com/some-article
    python private_podcast.py notes.txt --title "My notes"

Then serve the feed on your LAN and subscribe from your phone's podcast app:
    python -m http.server 8000 --directory podcast
    feed URL:  http://<your-lan-ip>:8000/feed.xml

WSL terminal but Ollama on Windows? Run the whole pipeline Windows-side (verified,
piper-tts installs fine on Windows):
    powershell.exe -Command "cd <folder with these scripts>; uv run --no-project --with ollama --with piper-tts python private_podcast.py <url> --engine piper"
"""

import argparse
import html
import re
import socket
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

from ollama import chat
from tts_helper import speak

LLM = "qwen3:4b"
PODCAST_DIR = Path("podcast")

REWRITE_PROMPT = (
    "Rewrite the following article as a short spoken-word script for a podcast episode. "
    "Plain flowing prose, no headings, no markdown, no URLs read aloud, under 400 words. "
    "Start with one sentence saying what the piece is about.\n\n"
)


def fetch_text(source: str) -> str:
    if not source.startswith("http"):
        return Path(source).read_text(encoding="utf-8")
    req = urllib.request.Request(source, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
    raw = re.sub(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", text).strip()


def lan_ip() -> str:
    """LAN address of this machine; podcast apps need absolute enclosure URLs."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 80))  # no traffic sent; just selects the LAN interface
        return s.getsockname()[0]
    except OSError:
        return "localhost"
    finally:
        s.close()


def write_feed(base: str) -> None:
    items = []
    for wav in sorted(PODCAST_DIR.glob("*.wav"), reverse=True):
        pub = datetime.fromtimestamp(wav.stat().st_mtime, tz=timezone.utc)
        items.append(
            f"<item><title>{html.escape(wav.stem)}</title>"
            f"<enclosure url='{base}/{wav.name}' type='audio/wav' length='{wav.stat().st_size}'/>"
            f"<guid>{base}/{wav.name}</guid><pubDate>{format_datetime(pub)}</pubDate></item>"
        )
    feed = (
        "<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel>"
        "<title>My Private Podcast</title><description>Generated entirely on my own machine"
        f"</description><link>{base}</link>" + "".join(items) + "</channel></rss>"
    )
    (PODCAST_DIR / "feed.xml").write_text(feed, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="article URL or path to a .txt file")
    parser.add_argument("--title", default=None)
    parser.add_argument("--engine", default="qwen", choices=["qwen", "piper"])
    parser.add_argument("--base-url", default=None,
                        help="feed base URL; defaults to http://<detected-lan-ip>:8000")
    args = parser.parse_args()

    PODCAST_DIR.mkdir(exist_ok=True)
    print("Fetching article...")
    text = fetch_text(args.source)[:15000]
    if len(text) < 200:
        sys.exit("Could not extract enough text from that source.")

    print(f"Rewriting for audio with {LLM} (first call loads the model; 30-120s is normal)...")
    script = chat(model=LLM, messages=[{"role": "user", "content": REWRITE_PROMPT + text}]).message.content

    title = args.title or re.sub(r"[^a-z0-9-]+", "-", script.split(".")[0].lower())[:50].strip("-")
    out = PODCAST_DIR / f"{datetime.now():%Y-%m-%d}-{title}.wav"
    print("Synthesising speech (first run downloads the TTS model)...")
    speak(script, out, engine=args.engine)
    base = args.base_url or f"http://{lan_ip()}:8000"
    write_feed(base)

    print(f"\nEpisode ready: {out}")
    print("Serve it:      python -m http.server 8000 --directory podcast")
    print(f"Subscribe at:  {base}/feed.xml")


if __name__ == "__main__":
    main()
