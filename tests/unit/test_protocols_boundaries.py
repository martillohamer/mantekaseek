from typing import Any

from mantekaseek.downloads.protocols import (
    CandidateSearcherProtocol,
    CommandRunnerProtocol,
    FallbackSearcherProtocol,
    JsonTransportProtocol,
    YtdlpRunnerProtocol,
)
from mantekaseek.downloads.ranking import DownloadCandidate
from mantekaseek.downloads.slskd_client import SlskdClient
from mantekaseek.downloads.ytdlp_client import YtdlpSearcher
from mantekaseek.spotify.protocols import SpotifyCatalogProtocol
from mantekaseek.spotify.resolver import SpotifyTrack


class FakeTransport:
    def post_json(self, url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
        return {"url": url, "headers": headers, "body": body}


class FakeYtdlpRunner:
    def run_json_lines(self, args: list[str]) -> list[dict[str, Any]]:
        return [{"args": args}]


class FakeCommandRunner:
    def run(self, args: list[str]) -> int:
        return 0 if args else 1


class FakeSearcher:
    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        return []


class FakeFallback:
    def search_fallback(self, artist: str, title: str) -> DownloadCandidate | None:
        return None


class FakeCatalog:
    def get_track(self, track_id: str) -> list[SpotifyTrack]:
        return []

    def get_album_tracks(self, album_id: str) -> list[SpotifyTrack]:
        return []

    def get_playlist_tracks(self, playlist_id: str) -> list[SpotifyTrack]:
        return []


def test_protocols() -> None:
    t, y, c, s = FakeTransport(), FakeYtdlpRunner(), FakeCommandRunner(), FakeSearcher()
    assert isinstance(t, JsonTransportProtocol)
    assert isinstance(y, YtdlpRunnerProtocol)
    assert isinstance(c, CommandRunnerProtocol)
    assert isinstance(SlskdClient("http://localhost:5030", "k", t), CandidateSearcherProtocol)
    assert isinstance(YtdlpSearcher(y), CandidateSearcherProtocol)
    assert isinstance(s, CandidateSearcherProtocol)
    assert isinstance(FakeFallback(), FallbackSearcherProtocol)
    assert isinstance(FakeCatalog(), SpotifyCatalogProtocol)
