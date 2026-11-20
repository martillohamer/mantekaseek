from pathlib import Path

from mantekaseek.downloads.transcode import build_transcode_command, run_transcode


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, args: list[str]) -> int:
        self.commands.append(args)
        return 0


def test_build_transcode_command_caps_bitrate() -> None:
    cmd = build_transcode_command(
        input_path=Path("tmp/source.wav"),
        output_path=Path("out/track.mp3"),
        source_bitrate_kbps=1411,
        target_bitrate_kbps=320,
    )
    assert cmd[:3] == ["ffmpeg", "-y", "-i"]
    assert "-b:a" in cmd
    bitrate_arg = cmd[cmd.index("-b:a") + 1]
    assert bitrate_arg == "320k"


def test_run_transcode_invokes_runner_with_safe_bitrate() -> None:
    runner = FakeRunner()
    out_file = run_transcode(
        input_path=Path("tmp/low.mp3"),
        output_path=Path("out/low_out.mp3"),
        source_bitrate_kbps=128,
        target_bitrate_kbps=320,
        runner=runner,
    )
    assert out_file == Path("out/low_out.mp3")
    assert len(runner.commands) == 1
    assert runner.commands[0][runner.commands[0].index("-b:a") + 1] == "128k"
