from dataclasses import dataclass
from difflib import SequenceMatcher


def effective_output_bitrate(source_bitrate_kbps: int, target_bitrate_kbps: int) -> int:
    if source_bitrate_kbps <= 0 or target_bitrate_kbps <= 0:
        raise ValueError("Los bitrates deben ser mayores que cero.")
    return min(source_bitrate_kbps, target_bitrate_kbps)


@dataclass(slots=True, frozen=True)
class DownloadCandidate:
    source: str
    artist: str
    title: str
    duration_ms: int
    bitrate_kbps: int
    peer_speed_kbps: int = 0


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def score_candidate(
    candidate: DownloadCandidate,
    expected_artist: str,
    expected_title: str,
    expected_duration_ms: int,
    target_bitrate_kbps: int,
) -> float:
    artist_sim = _similarity(candidate.artist, expected_artist)
    title_sim = _similarity(candidate.title, expected_title)
    text_score = (artist_sim * 0.4 + title_sim * 0.6) * 100.0

    duration_diff_s = abs(candidate.duration_ms - expected_duration_ms) / 1000.0
    duration_score = max(0.0, 25.0 - duration_diff_s * 1.5)

    eff_bitrate = effective_output_bitrate(candidate.bitrate_kbps, target_bitrate_kbps)
    quality_score = (eff_bitrate / max(target_bitrate_kbps, 1)) * 20.0

    speed_score = min(candidate.peer_speed_kbps / 200.0, 15.0)

    penalty = 0.0
    lower_title = candidate.title.lower()
    if ("live" in lower_title and "live" not in expected_title.lower()) or (
        "bootleg" in lower_title and "bootleg" not in expected_title.lower()
    ):
        penalty += 20.0

    return text_score + duration_score + quality_score + speed_score - penalty


def rank_candidates(
    candidates: list[DownloadCandidate],
    expected_artist: str,
    expected_title: str,
    expected_duration_ms: int,
    target_bitrate_kbps: int = 320,
) -> list[DownloadCandidate]:
    return sorted(
        candidates,
        key=lambda c: score_candidate(
            c,
            expected_artist=expected_artist,
            expected_title=expected_title,
            expected_duration_ms=expected_duration_ms,
            target_bitrate_kbps=target_bitrate_kbps,
        ),
        reverse=True,
    )
