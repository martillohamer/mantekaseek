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


def has_exportable_operations(project: StudioProject) -> bool:
    return bool(project.operations)


_MB_PER_SECOND: dict[str, float] = {
    "wav": 10.11,
    "flac": 6.0,
    "mp3": 2.4,
}


def estimate_export_size_mb(project: StudioProject) -> float:
    duration_sec = estimate_timeline_duration(project)
    if duration_sec <= 0.0:
        return 0.0
    rate = _MB_PER_SECOND.get(project.output_format.lower(), 2.4)
    return round(duration_sec * rate, 2)


def format_timeline_duration(project: StudioProject) -> str:
    total_seconds = max(0, int(round(estimate_timeline_duration(project))))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def format_export_overview(project: StudioProject) -> str:
    fmt = project.output_format.upper()
    duration = format_timeline_duration(project)
    size_mb = estimate_export_size_mb(project)
    return f"{project.name} [{fmt}] - {duration} (~{size_mb:.2f} MB)"


def has_valid_tempo(project: StudioProject) -> bool:
    return 20.0 <= project.tempo_bpm <= 300.0


def estimate_bars(project: StudioProject) -> int:
    duration_sec = estimate_timeline_duration(project)
    if duration_sec <= 0.0 or project.tempo_bpm <= 0.0:
        return 0
    seconds_per_bar = (60.0 / project.tempo_bpm) * 4.0
    return max(0, int(duration_sec // seconds_per_bar))


def format_bars_label(project: StudioProject) -> str:
    bars = estimate_bars(project)
    if bars == 1:
        return "1 compas"
    return f"{bars} compases"


def estimate_beats(project: StudioProject) -> int:
    duration_sec = estimate_timeline_duration(project)
    if duration_sec <= 0.0 or project.tempo_bpm <= 0.0:
        return 0
    seconds_per_beat = 60.0 / project.tempo_bpm
    return max(0, int(duration_sec // seconds_per_beat))


def format_beats_label(project: StudioProject) -> str:
    beats = estimate_beats(project)
    if beats == 1:
        return "1 pulso"
    return f"{beats} pulsos"


def has_project_targets(project: StudioProject) -> bool:
    return count_project_targets(project) > 0


def has_operations(project: StudioProject) -> bool:
    return len(project.operations) > 0


def count_operations(project: StudioProject) -> int:
    return len(project.operations)


def is_ready_to_export(project: StudioProject) -> bool:
    return has_valid_tempo(project) and has_exportable_operations(project)


def format_export_readiness(project: StudioProject) -> str:
    if is_ready_to_export(project):
        return "Lista para exportar"
    return "No lista para exportar"


def format_tempo_label(project: StudioProject) -> str:
    if has_valid_tempo(project):
        return f"{project.tempo_bpm:.1f} BPM"
    return "Tempo no valido"


def format_project_summary(project: StudioProject) -> str:
    project_label = format_project_name(project)
    tempo_label = format_tempo_label(project)
    readiness_label = format_export_readiness(project)
    output_fmt = format_output_format_label(project)
    return f"{project_label} | {tempo_label} | {output_fmt} | {readiness_label}"



def format_timeline_summary(project: StudioProject) -> str:
    op_count = len(project.operations)
    total_sec = sum(max(0.0, op.end_sec - op.start_sec) for op in project.operations)
    return f"{op_count} operaciones | {total_sec:.1f}s"


def format_studio_report(project: StudioProject) -> str:
    project_part = format_project_summary(project)
    timeline_part = format_timeline_summary(project)
    return f"{project_part} | {timeline_part}"


def format_output_format_label(project: StudioProject) -> str:
    cleaned = project.output_format.strip().upper()
    if not cleaned:
        return "FORMATO NO DEFINIDO"
    return cleaned


def has_output_format(project: StudioProject) -> bool:
    return format_output_format_label(project) != "FORMATO NO DEFINIDO"


def has_project_name(project: StudioProject) -> bool:
    return bool(project.name.strip())


def format_project_name(project: StudioProject) -> str:
    if has_project_name(project):
        return project.name.strip()
    return "PROYECTO SIN NOMBRE"


def has_complete_export_config(project: StudioProject) -> bool:
    return (
        has_project_name(project)
        and has_output_format(project)
        and is_ready_to_export(project)
    )


def format_export_config_status(project: StudioProject) -> str:
    if has_complete_export_config(project):
        return "Configuracion completa"
    return "Configuracion incompleta"


def get_missing_export_requirements(project: StudioProject) -> list[str]:
    missing: list[str] = []
    if not has_project_name(project):
        missing.append("nombre del proyecto")
    if not has_output_format(project):
        missing.append("formato de salida")
    if not has_operations(project):
        missing.append("operaciones en la linea de tiempo")
    return missing


def format_missing_export_requirements(project: StudioProject) -> str:
    missing = get_missing_export_requirements(project)
    if not missing:
        return "Ninguno"
    return ", ".join(missing)


def format_export_diagnostic(project: StudioProject) -> str:
    if has_complete_export_config(project):
        project_label = format_project_name(project)
        output_fmt = format_output_format_label(project)
        tempo_label = format_tempo_label(project)
        return f"Exportacion lista: {project_label} ({output_fmt}, {tempo_label})"
    missing_label = format_missing_export_requirements(project)
    return f"Exportacion bloqueada: falta {missing_label}"


def build_export_summary(project: StudioProject) -> dict[str, object]:
    return {
        "project": format_project_name(project),
        "ready": has_complete_export_config(project),
        "format": format_output_format_label(project),
        "tempo": format_tempo_label(project),
        "missing": get_missing_export_requirements(project),
        "diagnostic": format_export_diagnostic(project),
    }


def format_export_summary(project: StudioProject) -> str:
    summary = build_export_summary(project)
    missing_text = format_missing_export_requirements(project)
    return (
        f"Proyecto: {summary['project']}\n"
        f"Formato: {summary['format']}\n"
        f"Tempo: {summary['tempo']}\n"
        f"Faltantes: {missing_text}\n"
        f"Diagnostico: {summary['diagnostic']}"
    )


def estimate_timeline_duration_sec(project: StudioProject) -> float:
    total = 0.0
    for op in project.operations:
        start_val = getattr(op, "start_sec", None)
        end_val = getattr(op, "end_sec", None)
        if start_val is not None and end_val is not None:
            total += max(0.0, float(end_val) - float(start_val))
    return round(total, 6)


def estimate_timeline_bars(project: StudioProject) -> float:
    tempo = float(getattr(project, "tempo_bpm", 0.0) or 0.0)
    if tempo <= 0.0:
        return 0.0
    duration_sec = estimate_timeline_duration_sec(project)
    beats = duration_sec * (tempo / 60.0)
    return round(beats / 4.0, 6)


def format_timeline_bars(project: StudioProject) -> str:
    bars = estimate_timeline_bars(project)
    return f"{bars:.1f} compases"


def has_timeline_operations(project: StudioProject) -> bool:
    return bool(project.operations)
