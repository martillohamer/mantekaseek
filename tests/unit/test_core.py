from pathlib import Path

from mantekaseek.core.config import AppConfig, load_config
from mantekaseek.core.database import Database
from mantekaseek.core.logging import setup_logging


def test_load_default_config(tmp_path: Path) -> None:
    cfg_file = tmp_path / "config.toml"
    cfg = load_config(cfg_file)
    assert isinstance(cfg, AppConfig)
    assert cfg.bitrate_kbps == 320
    assert cfg.slskd_url == "http://localhost:5030"


def test_setup_logging_creates_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "logs" / "mantekaseek.log"
    logger = setup_logging(log_file)
    logger.info("Arranque de prueba")
    for handler in logger.handlers:
        handler.flush()
    assert log_file.exists()
    assert "Arranque de prueba" in log_file.read_text(encoding="utf-8")


def test_database_initializes_schema_and_tracks(tmp_path: Path) -> None:
    db_file = tmp_path / "mantekaseek.sqlite3"
    db = Database(db_file)
    db.initialize()
    assert db.is_track_downloaded("spotify:track:123") is False
    db.mark_track_downloaded(
        track_id="spotify:track:123",
        artist="Daft Punk",
        title="Around the World",
        file_path="/music/daft_punk.mp3",
    )
    assert db.is_track_downloaded("spotify:track:123") is True
