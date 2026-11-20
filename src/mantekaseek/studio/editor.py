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


def summarize_studio_project(project: StudioProject) -> str:
    return (
        f"proyecto={project.name} | formato={project.output_format} "
        f"| bpm={project.tempo_bpm:.1f} | ops={len(project.operations)}"
    )


SUPPORTED_EXPORT_FORMATS = ("wav", "mp3", "flac")


def build_export_plan(project: StudioProject, output_dir: str) -> dict[str, object]:
    fmt = project.output_format.lower()
    if fmt not in SUPPORTED_EXPORT_FORMATS:
        msg = f"Formato de exportacion no soportado: {project.output_format}"
        raise ValueError(msg)
    clean_dir = output_dir.rstrip("/")
    return {
        "output_path": f"{clean_dir}/{project.name}.{fmt}",
        "format": fmt,
        "tempo_bpm": project.tempo_bpm,
        "operations_count": len(project.operations),
    }


def estimate_timeline_duration(project: StudioProject, block_sec: float = 4.0) -> float:
    if block_sec <= 0:
        msg = "Duracion de bloque invalida: se requiere block_sec > 0"
        raise ValueError(msg)
    total = 0.0
    for op in project.operations:
        if op.kind == "cut":
            total += op.end_sec - op.start_sec
        elif op.kind == "paste":
            total += op.repeat * block_sec
        elif op.kind == "merge":
            total += op.crossfade_sec
    return round(total, 6)


def clear_operations(project: StudioProject) -> StudioProject:
    return StudioProject(
        name=project.name,
        output_format=project.output_format,
        tempo_bpm=project.tempo_bpm,
        operations=(),
    )


def undo_last_operation(project: StudioProject) -> StudioProject:
    return StudioProject(
        name=project.name,
        output_format=project.output_format,
        tempo_bpm=project.tempo_bpm,
        operations=project.operations[:-1],
    )


def count_operations_by_kind(project: StudioProject) -> dict[str, int]:
    counts: dict[str, int] = {}
    for op in project.operations:
        counts[op.kind] = counts.get(op.kind, 0) + 1
    return counts


def operations_for_target(project: StudioProject, target_id: str) -> list[StudioOperation]:
    return [op for op in project.operations if target_id in op.targets]


def set_project_tempo(project: StudioProject, bpm: float) -> StudioProject:
    if bpm <= 0:
        msg = "Tempo invalido: se requiere bpm > 0"
        raise ValueError(msg)
    return StudioProject(
        name=project.name,
        output_format=project.output_format,
        tempo_bpm=bpm,
        operations=project.operations,
    )


def set_output_format(project: StudioProject, output_format: str) -> StudioProject:
    fmt = output_format.lower()
    if fmt not in SUPPORTED_EXPORT_FORMATS:
        msg = f"Formato de salida no soportado: {output_format}"
        raise ValueError(msg)
    return StudioProject(
        name=project.name,
        output_format=fmt,
        tempo_bpm=project.tempo_bpm,
        operations=project.operations,
    )


def rename_project(project: StudioProject, new_name: str) -> StudioProject:
    cleaned = new_name.strip()
    if not cleaned:
        msg = "Nombre de proyecto invalido: no puede estar vacio"
        raise ValueError(msg)
    return StudioProject(
        name=cleaned,
        output_format=project.output_format,
        tempo_bpm=project.tempo_bpm,
        operations=project.operations,
    )


def list_project_targets(project: StudioProject) -> list[str]:
    seen: list[str] = []
    for op in project.operations:
        raw_targets = getattr(op, "targets", None)
        if raw_targets is not None:
            candidates = list(raw_targets)
        else:
            source = getattr(op, "source_id", None)
            candidates = [source] if source is not None else []
        for target in candidates:
            if target not in seen:
                seen.append(target)
    return seen


def count_project_targets(project: StudioProject) -> int:
    return len(list_project_targets(project))
