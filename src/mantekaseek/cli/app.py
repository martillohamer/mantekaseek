from pathlib import Path

import typer

from mantekaseek import __version__
from mantekaseek.core.config import load_config
from mantekaseek.core.database import Database
from mantekaseek.core.logging import setup_logging
from mantekaseek.dj.mixer import TrackCandidateDJ, suggest_next_tracks
from mantekaseek.library.keys import key_to_camelot, key_to_open_key
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


@app.command("key-convert")
def key_convert(musical_key: str) -> None:
    """Convierte una tonalidad musical a notacion Camelot y OpenKey."""
    try:
        camelot = key_to_camelot(musical_key)
        open_key = key_to_open_key(musical_key)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"key={musical_key} | camelot={camelot} | open_key={open_key}")


@app.command("dj-suggest")
def dj_suggest(
    bpm: float = typer.Option(..., "--bpm", help="BPM actual del deck."),
    camelot: str = typer.Option(..., "--camelot", help="Tonalidad Camelot actual (ej. 8A)."),
    max_delta: float = typer.Option(4.0, "--max-delta", help="Margen maximo de BPM."),
) -> None:
    """Muestra sugerencias armonicas y de BPM para la siguiente mezcla."""
    sample_pool = [
        TrackCandidateDJ(track_id="1", title="Warmup Groove", bpm=126.0, camelot="8A"),
        TrackCandidateDJ(track_id="2", title="Fifth Lift", bpm=127.0, camelot="9A"),
        TrackCandidateDJ(track_id="3", title="Peak Roller", bpm=128.0, camelot="8B"),
    ]
    try:
        suggestions = suggest_next_tracks(
            current_bpm=bpm,
            current_camelot=camelot,
            candidates=sample_pool,
            max_bpm_delta=max_delta,
        )
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if not suggestions:
        typer.echo("Sin sugerencias compatibles para ese BPM y tonalidad.")
        return

    for item in suggestions:
        typer.echo(f"{item.track_id}: {item.title} ({item.bpm} BPM, {item.camelot})")
