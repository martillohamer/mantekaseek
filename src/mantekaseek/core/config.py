import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    bitrate_kbps: int = 320
    slskd_url: str = "http://localhost:5030"
    output_dir: Path = Path("downloads")
    db_path: Path = Path("mantekaseek.sqlite3")
    log_path: Path = Path("logs/mantekaseek.log")


def load_config(config_path: Path | None = None) -> AppConfig:
    cfg = AppConfig()
    if config_path is None or not config_path.exists():
        return cfg

    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if "bitrate_kbps" in data:
        cfg.bitrate_kbps = int(data["bitrate_kbps"])
    if "slskd_url" in data:
        cfg.slskd_url = str(data["slskd_url"])
    if "output_dir" in data:
        cfg.output_dir = Path(str(data["output_dir"]))
    if "db_path" in data:
        cfg.db_path = Path(str(data["db_path"]))
    if "log_path" in data:
        cfg.log_path = Path(str(data["log_path"]))
    return cfg
