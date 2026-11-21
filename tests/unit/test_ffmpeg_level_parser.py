from pathlib import Path

from mantekaseek.library.gain import AudioLevelInfo
from mantekaseek.library.level_probe import (
    analyze_audio_file_gain,
    parse_loudnorm_output,
    plan_gain_from_loudnorm,
)


def test_parse_loudnorm_output_extracts_lufs_and_peak() -> None:
    sample_output = """
    [Parsed_loudnorm_0 @ 0x55a1]
    {
        "input_i" : "-18.50",
        "input_tp" : "-2.30",
        "input_lra" : "7.40",
        "input_thresh" : "-28.90",
        "output_i" : "-14.00",
        "output_tp" : "-1.00",
        "target_offset" : "0.00"
    }
    """
    info = parse_loudnorm_output(track_id="pista_01", raw_output=sample_output)

    assert isinstance(info, AudioLevelInfo)
    assert info.track_id == "pista_01"
    assert info.integrated_lufs == -18.5
    assert info.peak_dbfs == -2.3


def test_plan_gain_from_loudnorm_output() -> None:
    sample_output = """
    {
        "input_i" : "-19.00",
        "input_tp" : "-3.00"
    }
    """
    plan = plan_gain_from_loudnorm(
        track_id="pista_02",
        raw_output=sample_output,
        target_lufs=-14.0,
        max_peak_dbfs=-1.0,
    )
    assert plan.track_id == "pista_02"
    assert plan.gain_db == 2.0
    assert plan.projected_peak_dbfs == -1.0


class FakeFfmpegRunner:
    def __init__(self, stderr_output: str) -> None:
        self.stderr_output = stderr_output
        self.calls: list[list[str]] = []

    def run_ffmpeg(self, args: list[str]) -> str:
        self.calls.append(args)
        return self.stderr_output


def test_analyze_audio_file_gain_with_runner() -> None:
    runner = FakeFfmpegRunner(
        """
        {
            "input_i" : "-18.00",
            "input_tp" : "-2.50"
        }
        """
    )
    plan = analyze_audio_file_gain(
        track_id="pista_03",
        audio_path=Path("/tmp/demo.mp3"),
        runner=runner,
        target_lufs=-14.0,
        max_peak_dbfs=-1.0,
    )
    assert len(runner.calls) == 1
    assert "/tmp/demo.mp3" in runner.calls[0]
    assert plan.gain_db == 1.5
    assert plan.projected_peak_dbfs == -1.0


def test_cli_gain_probe_from_loudnorm_json() -> None:
    from typer.testing import CliRunner

    from mantekaseek.cli.app import app

    runner = CliRunner()
    payload = '{"input_i": "-19.00", "input_tp": "-3.00"}'
    result = runner.invoke(
        app,
        [
            "gain-probe",
            "--track-id",
            "pista_cli",
            "--loudnorm-output",
            payload,
            "--target-lufs",
            "-14.0",
            "--max-peak-dbfs",
            "-1.0",
        ],
    )
    assert result.exit_code == 0
    assert "pista_cli" in result.stdout
    assert "2.0" in result.stdout
