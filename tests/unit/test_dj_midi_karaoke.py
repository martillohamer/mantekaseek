from pathlib import Path

from mantekaseek.dj.midi_karaoke import load_midi_karaoke_track


def test_load_midi_karaoke_track_reads_metadata_and_notes(tmp_path: Path) -> None:
    midi_file = tmp_path / "fiesta_trio.mid"
    header = (
        b"MThd"
        + (6).to_bytes(4, "big")
        + (0).to_bytes(2, "big")
        + (1).to_bytes(2, "big")
        + (480).to_bytes(2, "big")
    )
    track_events = b"\x00\x90\x3c\x64\x00\xff\x2f\x00"
    track_chunk = b"MTrk" + len(track_events).to_bytes(4, "big") + track_events
    midi_file.write_bytes(header + track_chunk)

    track = load_midi_karaoke_track(midi_file, karaoke_enabled=True)
    assert track.title == "fiesta_trio"
    assert track.ticks_per_beat == 480
    assert track.karaoke_enabled is True
    assert len(track.notes) == 1
    assert track.notes[0].note == 60
    assert track.notes[0].velocity == 100


def test_cli_midi_karaoke_command(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    from mantekaseek.cli.app import app

    midi_file = tmp_path / "coro_trio.mid"
    header = (
        b"MThd"
        + (6).to_bytes(4, "big")
        + (0).to_bytes(2, "big")
        + (1).to_bytes(2, "big")
        + (480).to_bytes(2, "big")
    )
    track_events = b"\x00\x90\x3c\x64\x00\xff\x2f\x00"
    track_chunk = b"MTrk" + len(track_events).to_bytes(4, "big") + track_events
    midi_file.write_bytes(header + track_chunk)

    runner = CliRunner()
    result = runner.invoke(app, ["midi-karaoke", str(midi_file)])
    assert result.exit_code == 0
    assert "coro_trio" in result.stdout
    assert "notas=1" in result.stdout
    assert "karaoke=ON" in result.stdout
