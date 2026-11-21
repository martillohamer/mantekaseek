from pathlib import Path
from typing import Annotated

import typer

from mantekaseek import __version__
from mantekaseek.core.config import load_config
from mantekaseek.core.database import Database
from mantekaseek.core.logging import setup_logging
from mantekaseek.dj.mixer import TrackCandidateDJ, suggest_next_tracks
from mantekaseek.library.gain import AudioLevelInfo, calculate_safe_gain_db
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


@app.command("gain-plan")
def gain_plan(
    lufs: float = typer.Option(..., "--lufs", help="Sonoridad integrada medida en LUFS."),
    peak: float = typer.Option(..., "--peak", help="Pico maximo medido en dBFS."),
    target_lufs: float = typer.Option(-14.0, "--target-lufs", help="Objetivo en LUFS."),
    max_peak: float = typer.Option(-1.0, "--max-peak", help="Techo seguro de pico en dBFS."),
) -> None:
    """Calcula una ganancia segura sin superar el techo de pico."""
    info = AudioLevelInfo(track_id="cli", integrated_lufs=lufs, peak_dbfs=peak)
    gain_db = calculate_safe_gain_db(info, target_lufs=target_lufs, max_peak_dbfs=max_peak)
    projected_peak = round(peak + gain_db, 1)
    sign = "+" if gain_db > 0 else ""
    typer.echo(f"gain={sign}{gain_db:.1f}dB | projected_peak={projected_peak:.1f}dBFS")


@app.command("gain-probe")
def gain_probe(
    track_id: str = typer.Option(..., "--track-id", help="Identificador de la pista"),
    loudnorm_output: str = typer.Option(..., "--loudnorm-output", help="Salida de loudnorm"),
    target_lufs: float = typer.Option(-14.0, "--target-lufs", help="LUFS objetivo"),
    max_peak_dbfs: float = typer.Option(-1.0, "--max-peak-dbfs", help="Pico max dBFS"),
) -> None:
    """Revisa niveles de audio desde la salida de loudnorm y calcula ganancia segura."""
    from mantekaseek.library.level_probe import plan_gain_from_loudnorm

    plan = plan_gain_from_loudnorm(
        track_id=track_id,
        raw_output=loudnorm_output,
        target_lufs=target_lufs,
        max_peak_dbfs=max_peak_dbfs,
    )
    typer.echo(
        f"track_id={plan.track_id} gain_db={plan.gain_db} "
        f"projected_peak_dbfs={plan.projected_peak_dbfs}"
    )


@app.command("booth-status")
def booth_status(
    auto_mix: bool = typer.Option(False, "--auto-mix", help="Activa el piloto automatico rojo"),
    record_label: str | None = typer.Option(
        None, "--record-label", help="Inicia grabacion con etiqueta de sesion"
    ),
    pad: str | None = typer.Option(
        None, "--pad", help="Dispara un sound pad de cabina (ej. airhorn, riser, impact, scratch)"
    ),
    mic: str | None = typer.Option(
        None, "--mic", help="Canal de microfono a modular (mic_1, mic_2 o mic_3)"
    ),
    mic_style: str | None = typer.Option(
        None, "--mic-style", help="Estilo de voz para el canal indicado"
    ),
) -> None:
    """Muestra o actualiza el estado de la cabina DJ, micros, grabacion y pads."""
    from mantekaseek.dj.booth import (
        BoothState,
        configure_mic,
        summarize_booth_status,
        toggle_auto_mix,
        toggle_session_recording,
    )
    from mantekaseek.dj.sound_pads import SoundPadBank, trigger_sound_pad

    booth = BoothState()
    if mic and mic_style:
        booth = configure_mic(booth, channel=mic, voice_style=mic_style)
    if auto_mix:
        booth = toggle_auto_mix(booth)
    if record_label:
        booth = toggle_session_recording(booth, session_label=record_label)

    pads: SoundPadBank | None = None
    if pad:
        pads = trigger_sound_pad(SoundPadBank(), pad_name=pad)

    typer.echo(summarize_booth_status(booth, sound_pads=pads))


@app.command("midi-karaoke")
def midi_karaoke(
    midi_path: Annotated[Path, typer.Argument(..., help="Ruta al archivo MIDI (.mid) de karaoke")],
    karaoke: Annotated[
        bool,
        typer.Option("--karaoke/--no-karaoke", help="Activa o desactiva modo karaoke"),
    ] = True,
) -> None:
    """Inspecciona una pista MIDI de karaoke y muestra su informacion principal."""
    from mantekaseek.dj.midi_karaoke import load_midi_karaoke_track

    try:
        track = load_midi_karaoke_track(midi_path, karaoke_enabled=karaoke)
    except FileNotFoundError as exc:
        typer.secho(
            f"Error: el archivo MIDI no existe ({midi_path})",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        typer.secho(f"Error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc
    karaoke_state = "ON" if track.karaoke_enabled else "OFF"
    typer.echo(
        f"pista={track.title} | tpb={track.ticks_per_beat} "
        f"| notas={len(track.notes)} | karaoke={karaoke_state}"
    )


@app.command("sound-pad")
def sound_pad(
    pad_name: Annotated[
        str,
        typer.Argument(..., help="Nombre del sound pad (ej. airhorn, riser, impact, scratch)"),
    ],
    level_db: Annotated[
        float | None,
        typer.Option("--level-db", help="Nivel de disparo en dB para el pad"),
    ] = None,
) -> None:
    """Dispara un sound pad de cabina y muestra su nivel activo en dB."""
    from mantekaseek.dj.sound_pads import SoundPadBank, trigger_sound_pad

    bank = trigger_sound_pad(SoundPadBank(), pad_name=pad_name, level_db=level_db)
    active_level = bank.pad_levels_db.get(pad_name, 0.0)
    typer.echo(f"pad={bank.last_triggered} | nivel_db={active_level:.1f}")


@app.command("studio-plan")
def studio_plan(
    project_name: Annotated[
        str,
        typer.Argument(..., help="Nombre del proyecto en Mini Studio"),
    ],
    output_format: Annotated[
        str,
        typer.Option("--format", help="Formato de salida (wav, mp3, flac)"),
    ] = "wav",
    tempo_bpm: Annotated[
        float,
        typer.Option("--tempo-bpm", help="Tempo del proyecto en BPM"),
    ] = 120.0,
    output_dir: Annotated[
        str,
        typer.Option("--output-dir", help="Directorio de salida para la exportacion"),
    ] = "out",
) -> None:
    """Prepara y resume un plan de exportacion para un proyecto de Mini Studio."""
    from mantekaseek.studio.editor import (
        StudioProject,
        build_export_plan,
        summarize_studio_project,
    )

    project = StudioProject(
        name=project_name,
        output_format=output_format,
        tempo_bpm=tempo_bpm,
    )
    summary = summarize_studio_project(project)
    plan = build_export_plan(project, output_dir=output_dir)
    typer.echo(f"{summary} | salida={plan['output_path']}")


if __name__ == "__main__":
    app()
