"""Morning Briefing: a local LLM reads your day to you before you've opened a screen.

Track difficulty: ★★★ advanced combo (LLM + TTS + a scheduler = ambient product)

Create a sources/ folder next to this script containing any plain-text files:
    sources/calendar.txt   (paste or export today's events)
    sources/todos.md       (your task list)
Weather is fetched from wttr.in if you're online; skipped gracefully if not.

    python morning_briefing.py --city London

Make it ambient by scheduling it:
    Linux/mac:  crontab -e   ->   55 7 * * *  cd <here> && python morning_briefing.py
    Windows:    Task Scheduler -> Daily 07:55 -> python morning_briefing.py

WSL terminal but Ollama on Windows? Run Windows-side (verified):
    powershell.exe -Command "cd <folder with these scripts>; uv run --no-project --with ollama --with piper-tts python morning_briefing.py --engine piper"
"""

import argparse
import urllib.request
from datetime import datetime
from pathlib import Path

from ollama import chat
from tts_helper import speak

LLM = "qwen3:4b"
SOURCES = Path(__file__).parent / "sources"

PROMPT = (
    "You are a personal morning-briefing writer. Using the context below, write a "
    "spoken script of at most 170 words: greet briefly, then weather in one sentence, "
    "then today's calendar commitments in order, then the two most important todo items. "
    "Close with one encouraging line. "
    "Plain prose only; it will be read aloud by a TTS model.\n\nToday is {date}.\n\n{context}"
)


def gather_context(city: str) -> str:
    parts = []
    try:
        weather = urllib.request.urlopen(f"https://wttr.in/{city}?format=3", timeout=5).read().decode()
        parts.append(f"WEATHER: {weather.strip()}")
    except Exception:
        parts.append("WEATHER: unavailable (offline)")
    if SOURCES.is_dir():
        for f in sorted(SOURCES.glob("*")):
            parts.append(f"--- {f.name} ---\n{f.read_text(encoding='utf-8')[:2000]}")
    else:
        parts.append("(No sources/ folder found; briefing will be generic.)")
    return "\n\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", default="London")
    parser.add_argument("--engine", default="qwen", choices=["qwen", "piper"])
    parser.add_argument("--text-only", action="store_true", help="print the script, skip TTS")
    args = parser.parse_args()

    context = gather_context(args.city)
    today = datetime.now().strftime("%A %d %B %Y")
    print(f"Writing briefing with {LLM} (first call loads the model; 30-120s is normal)...")
    script = chat(
        model=LLM,
        messages=[{"role": "user", "content": PROMPT.format(date=today, context=context)}],
    ).message.content.strip()
    print("\n" + script + "\n")

    if not args.text_only:
        out = Path(f"briefing-{datetime.now():%Y-%m-%d}.wav")
        print("Synthesising speech...")
        speak(script, out, engine=args.engine, voice="A bright, friendly radio host, medium pace.")
        print(f"Saved {out}. Play it, or wire the script to your speakers.")


if __name__ == "__main__":
    main()
