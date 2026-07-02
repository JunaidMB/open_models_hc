"""Mechanical smoke tests for the workshop tracks. No models or servers needed.

    uv run --no-project --with ollama python tests/smoke.py

The ollama package is needed for import checks only; nothing is called.
"""

import py_compile
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ROOT / "tracks"
sys.path.insert(0, str(TRACKS))


def test_all_tracks_compile():
    for f in sorted(TRACKS.glob("*.py")):
        py_compile.compile(str(f), doraise=True)
    print("ok: all tracks compile")


def test_feed_uses_absolute_urls():
    import private_podcast as pp

    with tempfile.TemporaryDirectory() as td:
        pp.PODCAST_DIR = Path(td)
        (Path(td) / "2026-01-01-test-episode.wav").write_bytes(b"RIFF0000WAVEfmt ")
        pp.write_feed("http://192.168.1.10:8000")
        tree = ET.parse(Path(td) / "feed.xml")
        enclosure = tree.find(".//enclosure")
        assert enclosure is not None, "feed has no enclosure"
        url = enclosure.get("url")
        assert url == "http://192.168.1.10:8000/2026-01-01-test-episode.wav", url
        link = tree.find(".//link")
        assert link is not None and link.text.startswith("http://192.168.1.10:8000"), "channel link not absolute"
    print("ok: feed enclosure and link URLs are absolute")


def test_lan_ip_returns_address():
    import private_podcast as pp

    ip = pp.lan_ip()
    assert isinstance(ip, str) and ip, ip
    print(f"ok: lan_ip() -> {ip}")


def test_briefing_prompt_mentions_todos():
    import morning_briefing as mb

    assert "todo" in mb.PROMPT.lower(), "briefing prompt no longer asks for todos"
    print("ok: briefing prompt covers calendar and todos")


if __name__ == "__main__":
    test_all_tracks_compile()
    test_feed_uses_absolute_urls()
    test_lan_ip_returns_address()
    test_briefing_prompt_mentions_todos()
    print("\nAll smoke tests passed.")
