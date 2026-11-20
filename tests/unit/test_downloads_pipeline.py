import pytest

from mantekaseek.downloads.pipeline import (
    DownloadPlan,
    plan_track_download,
)
from mantekaseek.downloads.ranking import DownloadCandidate


class FakeSlskdWithResults:
    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        return [
            DownloadCandidate(
                source="slskd",
                artist=artist,
                title=title,
                duration_ms=210000,
                bitrate_kbps=192,
                peer_speed_kbps=900,
            ),
            DownloadCandidate(
                source="slskd",
                artist=artist,
                title=title,
                duration_ms=210000,
                bitrate_kbps=320,
                peer_speed_kbps=2500,
            ),
        ]


class FakeSlskdEmpty:
    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        return []


class FakeYoutubeFallback:
    def search_fallback(self, artist: str, title: str) -> DownloadCandidate | None:
        return DownloadCandidate(
            source="youtube",
            artist=artist,
            title=f"{title} (Official Audio)",
            duration_ms=211000,
            bitrate_kbps=128,
            peer_speed_kbps=0,
        )


class FakeYoutubeEmpty:
    def search_fallback(self, artist: str, title: str) -> DownloadCandidate | None:
        return None


def test_plan_prefers_best_slskd_candidate_and_caps_bitrate() -> None:
    plan = plan_track_download(
        artist="Disclosure",
        title="Latch",
        duration_ms=210000,
        target_bitrate_kbps=320,
        slskd=FakeSlskdWithResults(),
        youtube_fallback=FakeYoutubeFallback(),
    )
    assert isinstance(plan, DownloadPlan)
    assert plan.candidate.source == "slskd"
    assert plan.candidate.bitrate_kbps == 320
    assert plan.output_bitrate_kbps == 320
    assert plan.used_fallback is False


def test_plan_uses_youtube_fallback_when_slskd_empty_without_upscaling() -> None:
    plan = plan_track_download(
        artist="Disclosure",
        title="Latch",
        duration_ms=210000,
        target_bitrate_kbps=320,
        slskd=FakeSlskdEmpty(),
        youtube_fallback=FakeYoutubeFallback(),
    )
    assert plan.candidate.source == "youtube"
    assert plan.used_fallback is True
    assert plan.output_bitrate_kbps == 128


def test_plan_raises_when_neither_slskd_nor_youtube_finds_track() -> None:
    with pytest.raises(LookupError):
        plan_track_download(
            artist="Desconocido",
            title="Inexistente",
            duration_ms=180000,
            target_bitrate_kbps=320,
            slskd=FakeSlskdEmpty(),
            youtube_fallback=FakeYoutubeEmpty(),
        )
