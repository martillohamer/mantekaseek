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
