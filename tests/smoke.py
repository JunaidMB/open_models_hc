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


def test_librarian_dedupes_collisions():
    """Two same-day screenshots with the same slug must never overwrite or crash."""
    import screenshot_librarian as sl

    original_describe = sl.describe
    sl.describe = lambda image: ("same-name", "tag-a, tag-b")
    try:
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            (folder / "shot_a.png").write_bytes(b"fake png a")
            (folder / "shot_b.png").write_bytes(b"fake png b")
            n = sl.process_folder(folder, folder / "index.md", {})
            assert n == 2, f"expected 2 processed, got {n}"
            names = sorted(p.name for p in folder.glob("*.png"))
            assert len(names) == 2 and names[0] != names[1], names
            assert any(name.endswith("-2.png") for name in names), names
    finally:
        sl.describe = original_describe
    print("ok: librarian dedupes same-slug collisions")


def test_librarian_gives_up_on_poison_images():
    import screenshot_librarian as sl

    original_describe = sl.describe

    def always_fails(image):
        raise ValueError("poison")

    sl.describe = always_fails
    try:
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            (folder / "bad.png").write_bytes(b"fake png")
            failures = {}
            for _ in range(5):
                sl.process_folder(folder, folder / "index.md", failures)
            assert failures["bad.png"] == 3, failures
            assert (folder / "bad.png").exists(), "poison image must keep its name"
    finally:
        sl.describe = original_describe
    print("ok: librarian stops retrying poison images after 3 attempts")


if __name__ == "__main__":
    test_all_tracks_compile()
    test_feed_uses_absolute_urls()
    test_lan_ip_returns_address()
    test_briefing_prompt_mentions_todos()
    test_librarian_dedupes_collisions()
    test_librarian_gives_up_on_poison_images()
    print("\nAll smoke tests passed.")
