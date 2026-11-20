from typing import Any

from mantekaseek.downloads.ranking import DownloadCandidate
from mantekaseek.downloads.ytdlp_client import YtdlpSearcher


class FakeCommandRunner:
    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = entries
        self.commands: list[list[str]] = []

    def run_json_lines(self, args: list[str]) -> list[dict[str, Any]]:
        self.commands.append(args)
        return self.entries


def test_ytdlp_searcher_maps_candidates() -> None:
    runner = FakeCommandRunner(
        entries=[
            {
                "id": "abc123XYZ",
                "title": "Daft Punk - One More Time",
                "duration": 320,
                "webpage_url": "https://www.youtube.com/watch?v=abc123XYZ",
            }
        ]
    )
    searcher = YtdlpSearcher(runner=runner)
    candidates = searcher.search(artist="Daft Punk", title="One More Time")

    assert len(candidates) == 1
    cand = candidates[0]
    assert isinstance(cand, DownloadCandidate)
    assert cand.source == "youtube"
    assert cand.duration_ms == 320000
    assert len(runner.commands) == 1
