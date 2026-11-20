from pathlib import Path
from typing import Protocol

from mantekaseek.downloads.ranking import effective_output_bitrate


class CommandRunner(Protocol):
    def run(self, args: list[str]) -> int: ...


def build_transcode_command(
    input_path: Path,
    output_path: Path,
    source_bitrate_kbps: int,
    target_bitrate_kbps: int,
) -> list[str]:
    safe_bitrate = effective_output_bitrate(source_bitrate_kbps, target_bitrate_kbps)
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        f"{safe_bitrate}k",
        str(output_path),
    ]


def run_transcode(
    input_path: Path,
    output_path: Path,
    source_bitrate_kbps: int,
    target_bitrate_kbps: int,
    runner: CommandRunner,
) -> Path:
    cmd = build_transcode_command(
        input_path=input_path,
        output_path=output_path,
        source_bitrate_kbps=source_bitrate_kbps,
        target_bitrate_kbps=target_bitrate_kbps,
    )
    code = runner.run(cmd)
    if code != 0:
        raise RuntimeError(f"La conversion de audio fallo con codigo {code}")
    return output_path
