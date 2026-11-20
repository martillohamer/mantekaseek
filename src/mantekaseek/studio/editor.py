from dataclasses import dataclass


@dataclass(frozen=True)
class StudioOperation:
    kind: str
    targets: tuple[str, ...]
    start_sec: float = 0.0
    end_sec: float = 0.0
    at_sec: float = 0.0
    repeat: int = 1
    crossfade_sec: float = 0.0


@dataclass(frozen=True)
class StudioProject:
    name: str
    output_format: str = "wav"
    tempo_bpm: float = 120.0
    operations: tuple[StudioOperation, ...] = ()


def cut_segment(
    project: StudioProject,
    source_id: str,
    start_sec: float,
    end_sec: float,
) -> StudioProject:
    if start_sec < 0 or end_sec <= start_sec:
        msg = "Rango de corte invalido: se requiere 0 <= start_sec < end_sec"
        raise ValueError(msg)
    op = StudioOperation(
        kind="cut",
        targets=(source_id,),
        start_sec=start_sec,
        end_sec=end_sec,
    )
    return StudioProject(
        name=project.name,
        output_format=project.output_format,
        tempo_bpm=project.tempo_bpm,
        operations=(*project.operations, op),
    )


def paste_segment(
    project: StudioProject,
    source_id: str,
    at_sec: float,
    repeat: int = 1,
) -> StudioProject:
    if at_sec < 0 or repeat < 1:
        msg = "Parametros de pegado invalidos: se requiere at_sec >= 0 y repeat >= 1"
        raise ValueError(msg)
    op = StudioOperation(
        kind="paste",
        targets=(source_id,),
        at_sec=at_sec,
        repeat=repeat,
    )
    return StudioProject(
        name=project.name,
        output_format=project.output_format,
        tempo_bpm=project.tempo_bpm,
        operations=(*project.operations, op),
    )


def merge_tracks(
    project: StudioProject,
    track_ids: tuple[str, ...],
    crossfade_sec: float = 0.0,
) -> StudioProject:
    if len(track_ids) < 2 or crossfade_sec < 0:
        msg = "Fusion invalida: se requieren al menos 2 pistas y crossfade_sec >= 0"
        raise ValueError(msg)
    op = StudioOperation(
        kind="merge",
        targets=track_ids,
        crossfade_sec=crossfade_sec,
    )
    return StudioProject(
        name=project.name,
        output_format=project.output_format,
        tempo_bpm=project.tempo_bpm,
        operations=(*project.operations, op),
    )
