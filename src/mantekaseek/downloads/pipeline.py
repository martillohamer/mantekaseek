from dataclasses import dataclass
from typing import Protocol

from mantekaseek.downloads.ranking import (
    DownloadCandidate,
    effective_output_bitrate,
    rank_candidates,
)


class SlskdSearcher(Protocol):
    def search(self, artist: str, title: str) -> list[DownloadCandidate]: ...


class YoutubeFallback(Protocol):
    def search_fallback(self, artist: str, title: str) -> DownloadCandidate | None: ...


@dataclass(slots=True, frozen=True)
class DownloadPlan:
    candidate: DownloadCandidate
    output_bitrate_kbps: int
    used_fallback: bool


def plan_track_download(
    artist: str,
    title: str,
    duration_ms: int,
    target_bitrate_kbps: int,
    slskd: SlskdSearcher,
    youtube_fallback: YoutubeFallback | None = None,
) -> DownloadPlan:
    slskd_candidates = slskd.search(artist, title)
    if slskd_candidates:
        ranked = rank_candidates(
            candidates=slskd_candidates,
            expected_artist=artist,
            expected_title=title,
            expected_duration_ms=duration_ms,
            target_bitrate_kbps=target_bitrate_kbps,
        )
        chosen = ranked[0]
        return DownloadPlan(
            candidate=chosen,
            output_bitrate_kbps=effective_output_bitrate(chosen.bitrate_kbps, target_bitrate_kbps),
            used_fallback=False,
        )

    if youtube_fallback is not None:
        fallback_candidate = youtube_fallback.search_fallback(artist, title)
        if fallback_candidate is not None:
            return DownloadPlan(
                candidate=fallback_candidate,
                output_bitrate_kbps=effective_output_bitrate(
                    fallback_candidate.bitrate_kbps, target_bitrate_kbps
                ),
                used_fallback=True,
            )

    raise LookupError(f"No se encontraron candidatos para {artist} - {title}")
