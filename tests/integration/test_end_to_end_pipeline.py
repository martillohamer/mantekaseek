from mantekaseek.downloads.pipeline import plan_track_download
from mantekaseek.downloads.ranking import DownloadCandidate
from mantekaseek.library.gain import AudioLevelInfo, is_gain_clipped, plan_batch_leveling
from mantekaseek.studio.editor import (
    StudioProject,
    build_batch_export_plan,
    cut_segment,
    execute_valid_batch_export_plan,
    format_valid_batch_results,
)


class StubSearcher:
    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        return [
            DownloadCandidate(
                source="slskd",
                artist=artist,
                title=title,
                duration_ms=429000,
                bitrate_kbps=320,
                peer_speed_kbps=2500,
            )
        ]


def test_download_gain_and_studio_export_flow() -> None:
    plan = plan_track_download(
        artist="Daft Punk",
        title="Around the World",
        duration_ms=429000,
        target_bitrate_kbps=320,
        slskd=StubSearcher(),
    )
    assert plan.candidate.source == "slskd"
    assert not plan.used_fallback

    track_id = f"{plan.candidate.artist} - {plan.candidate.title}"
    levels = [
        AudioLevelInfo(
            track_id=track_id,
            integrated_lufs=-18.0,
            peak_dbfs=-6.0,
        )
    ]
    gain_plans = plan_batch_leveling(levels, target_lufs=-14.0, max_peak_dbfs=-1.0)
    assert track_id in gain_plans
    assert not is_gain_clipped(gain_plans[track_id], max_peak_dbfs=-1.0)

    base_project = StudioProject(name="set_club", output_format="wav", tempo_bpm=128.0)
    edited = cut_segment(base_project, source_id=track_id, start_sec=0.0, end_sec=16.0)
    export_plans = build_batch_export_plan([edited], output_dir="/tmp/out")
    results = execute_valid_batch_export_plan(export_plans)
    summary_text = format_valid_batch_results(export_plans)

    assert len(results) == 1
    assert isinstance(summary_text, str) and len(summary_text) > 0
