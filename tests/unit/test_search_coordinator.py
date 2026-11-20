from typing import Any

from mantekaseek.downloads.coordinator import SearchCoordinator
from mantekaseek.downloads.slskd_client import SlskdClient
from mantekaseek.downloads.ytdlp_client import YtdlpSearcher


class FakeHttpTransport:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def post_json(self, url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
        return self.payload


class FakeYtdlpRunner:
    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = entries
        self.called = False

    def run_json_lines(self, args: list[str]) -> list[dict[str, Any]]:
        self.called = True
        return self.entries


def test_coordinator_uses_slskd_first_without_youtube_fallback() -> None:
    slskd = SlskdClient(
        base_url="http://localhost:5030",
        api_key="k",
        transport=FakeHttpTransport(
            {
                "responses": [
                    {
                        "username": "peer1",
                        "uploadSpeed": 1500000,
                        "files": [
                            {
                                "filename": "Track.mp3",
                                "size": 9000000,
                                "bitRate": 320,
                                "length": 240,
                            }
                        ],
                    }
                ]
            }
        ),
    )
    yt_runner = FakeYtdlpRunner(
        [{"id": "yt1", "title": "Track", "duration": 240, "abr": 128}]
    )
    yt = YtdlpSearcher(runner=yt_runner)

    coord = SearchCoordinator(slskd_client=slskd, ytdlp_searcher=yt)
    results = coord.search(artist="Artist", title="Track")

    assert len(results) == 1
    assert results[0].source == "slskd"
    assert yt_runner.called is False


def test_coordinator_falls_back_to_ytdlp_when_slskd_empty() -> None:
    slskd = SlskdClient(
        base_url="http://localhost:5030",
        api_key="k",
        transport=FakeHttpTransport({"responses": []}),
    )
    yt_runner = FakeYtdlpRunner(
        [{"id": "yt1", "title": "Track", "duration": 240, "abr": 128}]
    )
    yt = YtdlpSearcher(runner=yt_runner)

    coord = SearchCoordinator(slskd_client=slskd, ytdlp_searcher=yt)
    results = coord.search(artist="Artist", title="Track")

    assert len(results) == 1
    assert results[0].source == "youtube"
    assert yt_runner.called is True
