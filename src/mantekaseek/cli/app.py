from pathlib import Path
import typer

from mantekaseek import __version__
from mantekaseek.core.config import load_config
from mantekaseek.core.database import Database
from mantekaseek.core.logging import setup_logging
from mantekaseek.spotify.parser import parse_spotify_url

app = typer.Typer(help="CLI de mantekaseek / martilloseek.")


@app.command()
def info(config: Path | None = None) -> None:
    """Muestra la version y configuracion cargada."""
    cfg = load_config(config)
    typer.echo(
        f"mantekaseek v{__version__} | bitrate={cfg.bitrate_kbps}kbps | slskd={cfg.slskd_url}"
    )


@app.command("db-init")
def db_init(
    db: Path = Path("mantekaseek.sqlite3"),
    log: Path = Path("logs/mantekaseek.log"),
) -> None:
    """Inicializa la base de datos SQLite y el sistema de logs."""
    logger = setup_logging(log)
    database = Database(db)
    database.initialize()
    logger.info("Base de datos inicializada en %s", db)
    typer.echo(f"OK: SQLite lista en {db}")


@app.command("spotify-inspect")
def spotify_inspect(url: str) -> None:
    """Valida y muestra el tipo e identificador de un enlace de Spotify."""
    try:
        target = parse_spotify_url(url)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"kind={target.kind} | id={target.spotify_id}")
