from mantekaseek.downloads.ranking import (
    DownloadCandidate,
    effective_output_bitrate,
    rank_candidates,
)


def test_effective_output_bitrate_never_upscales() -> None:
    assert effective_output_bitrate(source_bitrate_kbps=128, target_bitrate_kbps=320) == 128
    assert effective_output_bitrate(source_bitrate_kbps=320, target_bitrate_kbps=192) == 192
    assert effective_output_bitrate(source_bitrate_kbps=1411, target_bitrate_kbps=320) == 320


def test_rank_candidates_prefers_matching_title_duration_quality_and_speed() -> None:
    c_best = DownloadCandidate(
        source="slskd",
        artist="Daft Punk",
        title="One More Time",
        duration_ms=320000,
        bitrate_kbps=320,
        peer_speed_kbps=2400,
    )
    c_slow_or_mismatched = DownloadCandidate(
        source="slskd",
        artist="Daft Punk",
        title="One More Time (Live Bootleg)",
        duration_ms=490000,
        bitrate_kbps=128,
        peer_speed_kbps=150,
    )
    c_good_match_medium_speed = DownloadCandidate(
        source="slskd",
        artist="Daft Punk",
        title="One More Time",
        duration_ms=321000,
        bitrate_kbps=256,
        peer_speed_kbps=1200,
    )

    ranked = rank_candidates(
        candidates=[c_slow_or_mismatched, c_good_match_medium_speed, c_best],
        expected_artist="Daft Punk",
        expected_title="One More Time",
        expected_duration_ms=320000,
        target_bitrate_kbps=320,
    )
    assert [item.title for item in ranked] == [
        "One More Time",
        "One More Time",
        "One More Time (Live Bootleg)",
    ]
    assert ranked[0].bitrate_kbps == 320
