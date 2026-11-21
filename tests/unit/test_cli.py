from pathlib import Path

from typer.testing import CliRunner

from mantekaseek.cli.app import app

runner = CliRunner()


def test_cli_info_command() -> None:
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "mantekaseek" in result.stdout


def test_cli_db_init_command(tmp_path: Path) -> None:
    db_file = tmp_path / "cli_test.sqlite3"
    log_file = tmp_path / "cli_test.log"
    result = runner.invoke(app, ["db-init", "--db", str(db_file), "--log", str(log_file)])
    assert result.exit_code == 0
    assert db_file.exists()


def test_cli_spotify_inspect_command() -> None:
    result = runner.invoke(
        app,
        ["spotify-inspect", "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"],
    )
    assert result.exit_code == 0
    assert "track" in result.stdout
    assert "4cOdK2wGLETKBW3PvgPWqT" in result.stdout


def test_cli_key_convert_command() -> None:
    result = runner.invoke(app, ["key-convert", "Am"])
    assert result.exit_code == 0
    assert "8A" in result.stdout
    assert "1m" in result.stdout


def test_cli_dj_suggest_command() -> None:
    result = runner.invoke(
        app,
        ["dj-suggest", "--bpm", "126.0", "--camelot", "8A"],
    )
    assert result.exit_code == 0


def test_cli_gain_plan_command() -> None:
    result = runner.invoke(
        app,
        ["gain-plan", "--lufs", "-20.0", "--peak", "-6.0", "--target-lufs", "-14.0"],
    )
    assert result.exit_code == 0
    assert "+5.0dB" in result.stdout or "5.0" in result.stdout


def test_cli_help_lists_descriptions_for_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in (
        "info",
        "db-init",
        "spotify-inspect",
        "key-convert",
        "dj-suggest",
        "gain-plan",
        "gain-probe",
        "booth-status",
        "midi-karaoke",
        "sound-pad",
        "studio-plan",
    ):
        assert cmd in result.stdout
    assert "Revisa niveles de audio" in result.stdout
    assert "Muestra o actualiza el estado de la cabina" in result.stdout
    assert "Inspecciona una pista MIDI" in result.stdout
    assert "Dispara un sound pad" in result.stdout
    assert "Prepara y resume un plan de exportacion" in result.stdout


def test_cli_midi_karaoke_missing_file_clean_error(tmp_path: Path) -> None:
    missing = tmp_path / "no_existe.mid"
    result = runner.invoke(app, ["midi-karaoke", str(missing)])
    assert result.exit_code == 1
    assert "Traceback" not in result.output
    assert "no existe" in result.output.lower()


def test_cli_gain_probe_accepts_max_peak_option() -> None:
    result = runner.invoke(
        app,
        [
            "gain-probe",
            "--track-id",
            "t-1",
            "--loudnorm-output",
            '{"input_i":"-18.0","input_tp":"-6.0"}',
            "--target-lufs",
            "-14.0",
            "--max-peak",
            "-1.0",
        ],
    )
    assert result.exit_code == 0
    assert "t-1" in result.stdout
