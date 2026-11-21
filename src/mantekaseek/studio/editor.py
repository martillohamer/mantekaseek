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


def get_last_source_id(project: StudioProject) -> str | None:
    for op in reversed(project.operations):
        targets = getattr(op, "targets", None)
        if isinstance(targets, (tuple, list)):
            for item in reversed(targets):
                if isinstance(item, str) and item:
                    return item
        source_id = getattr(op, "source_id", None)
        if isinstance(source_id, str) and source_id:
            return source_id
    return None

def count_cut_operations(project: StudioProject) -> int:
    return sum(1 for op in project.operations if getattr(op, "kind", None) == "cut")


def list_timeline_sources(project: StudioProject) -> list[str]:
    seen: list[str] = []
    for op in project.operations:
        targets = getattr(op, "targets", None)
        if isinstance(targets, (tuple, list)):
            for item in targets:
                if isinstance(item, str) and item and item not in seen:
                    seen.append(item)
        source_id = getattr(op, "source_id", None)
        if isinstance(source_id, str) and source_id and source_id not in seen:
            seen.append(source_id)
    return seen


def count_timeline_sources(project: StudioProject) -> int:
    return len(list_timeline_sources(project))


def has_timeline_source(project: StudioProject, source_id: str) -> bool:
    return source_id in list_timeline_sources(project)


def get_timeline_end_sec(project: StudioProject) -> float:
    max_end = 0.0
    for op in project.operations:
        end_val = getattr(op, "end_sec", None)
        if end_val is not None:
            max_end = max(max_end, float(end_val))
    return round(max_end, 6)


def get_timeline_start_sec(project: StudioProject) -> float:
    starts = [
        float(start_val)
        for op in project.operations
        if (start_val := getattr(op, "start_sec", None)) is not None
    ]
    if not starts:
        return 0.0
    return round(min(starts), 6)


def get_timeline_span_sec(project: StudioProject) -> float:
    has_bounds = any(
        getattr(op, "start_sec", None) is not None or getattr(op, "end_sec", None) is not None
        for op in project.operations
    )
    if not has_bounds:
        return 0.0
    span = get_timeline_end_sec(project) - get_timeline_start_sec(project)
    return round(max(0.0, span), 6)


def format_timeline_span(project: StudioProject) -> str:
    span_sec = get_timeline_span_sec(project)
    total_seconds = max(0, int(round(span_sec)))
    mins, secs = divmod(total_seconds, 60)
    return f"{mins:02d}:{secs:02d}"


def get_timeline_span_bars(project: StudioProject, beats_per_bar: int = 4) -> float:
    if beats_per_bar <= 0:
        msg = "Compas invalido: se requiere beats_per_bar > 0"
        raise ValueError(msg)
    span_sec = get_timeline_span_sec(project)
    if span_sec <= 0.0:
        return 0.0
    beats = span_sec * (project.tempo_bpm / 60.0)
    return round(beats / beats_per_bar, 6)


def format_timeline_span_bars(project: StudioProject, beats_per_bar: int = 4) -> str:
    bars = get_timeline_span_bars(project, beats_per_bar=beats_per_bar)
    return f"{bars:.2f}"


def has_timeline_gaps(project: StudioProject) -> bool:
    intervals: list[tuple[float, float]] = []
    for op in project.operations:
        start_val = getattr(op, "start_sec", None)
        end_val = getattr(op, "end_sec", None)
        if start_val is not None and end_val is not None:
            intervals.append((float(start_val), float(end_val)))
    if len(intervals) < 2:
        return False
    intervals.sort(key=lambda pair: (pair[0], pair[1]))
    current_end = intervals[0][1]
    for start_sec, end_sec in intervals[1:]:
        if start_sec > current_end + 1e-9:
            return True
        current_end = max(current_end, end_sec)
    return False


def count_timeline_gaps(project: StudioProject) -> int:
    intervals: list[tuple[float, float]] = []
    for op in project.operations:
        start_val = getattr(op, "start_sec", None)
        end_val = getattr(op, "end_sec", None)
        if start_val is not None and end_val is not None:
            intervals.append((float(start_val), float(end_val)))
    if len(intervals) < 2:
        return 0
    intervals.sort(key=lambda pair: (pair[0], pair[1]))
    gaps = 0
    current_end = intervals[0][1]
    for start_sec, end_sec in intervals[1:]:
        if start_sec > current_end + 1e-9:
            gaps += 1
        current_end = max(current_end, end_sec)
    return gaps


def get_timeline_gap_sec(project: StudioProject) -> float:
    intervals: list[tuple[float, float]] = []
    for op in project.operations:
        start_val = getattr(op, "start_sec", None)
        end_val = getattr(op, "end_sec", None)
        if start_val is not None and end_val is not None:
            intervals.append((float(start_val), float(end_val)))
    if len(intervals) < 2:
        return 0.0
    intervals.sort(key=lambda pair: (pair[0], pair[1]))
    total_gap = 0.0
    current_end = intervals[0][1]
    for start_sec, end_sec in intervals[1:]:
        if start_sec > current_end + 1e-9:
            total_gap += start_sec - current_end
        current_end = max(current_end, end_sec)
    return round(total_gap, 6)


def format_timeline_gap(project: StudioProject) -> str:
    gap_sec = get_timeline_gap_sec(project)
    total_seconds = max(0, int(round(gap_sec)))
    mins, secs = divmod(total_seconds, 60)
    return f"{mins:02d}:{secs:02d}"


def get_timeline_active_sec(project: StudioProject) -> float:
    active_sec = get_timeline_span_sec(project) - get_timeline_gap_sec(project)
    return round(max(0.0, active_sec), 6)


def format_timeline_active(project: StudioProject) -> str:
    active_sec = get_timeline_active_sec(project)
    total_seconds = max(0, int(round(active_sec)))
    mins, secs = divmod(total_seconds, 60)
    return f"{mins:02d}:{secs:02d}"


def get_timeline_active_ratio(project: StudioProject) -> float:
    span_sec = get_timeline_span_sec(project)
    if span_sec <= 0.0:
        return 0.0
    active_sec = get_timeline_active_sec(project)
    return round(active_sec / span_sec, 6)


def format_timeline_active_pct(project: StudioProject) -> str:
    pct = max(0.0, get_timeline_active_ratio(project)) * 100.0
    return f"{pct:.1f}%"


def get_timeline_gap_ratio(project: StudioProject) -> float:
    span_sec = get_timeline_span_sec(project)
    if span_sec <= 0.0:
        return 0.0
    gap_sec = get_timeline_gap_sec(project)
    return round(gap_sec / span_sec, 6)


def format_timeline_gap_pct(project: StudioProject) -> str:
    pct = max(0.0, get_timeline_gap_ratio(project)) * 100.0
    return f"{pct:.1f}%"


def get_timeline_summary(project: StudioProject) -> dict[str, object]:
    return {
        "segments_count": len(project.operations),
        "total_duration_sec": get_timeline_span_sec(project),
        "span_sec": get_timeline_span_sec(project),
        "gap_sec": get_timeline_gap_sec(project),
        "active_sec": get_timeline_active_sec(project),
        "active_ratio": get_timeline_active_ratio(project),
        "gap_ratio": get_timeline_gap_ratio(project),
        "span_formatted": format_timeline_span(project),
        "gap_formatted": format_timeline_gap(project),
        "active_formatted": format_timeline_active(project),
        "active_pct_formatted": format_timeline_active_pct(project),
        "gap_pct_formatted": format_timeline_gap_pct(project),
    }


def can_export_project(project: StudioProject) -> bool:
    return len(get_missing_export_requirements(project)) == 0


def format_export_plan(plan: dict[str, object]) -> str:
    return (
        f"{plan['output_path']} "
        f"[{plan['format']} @ {plan['tempo_bpm']} BPM | {plan['operations_count']} ops]"
    )


def validate_export_plan(plan: dict[str, object]) -> bool:
    output_path = str(plan.get("output_path", "")).strip()
    if not output_path:
        msg = "Ruta de exportacion vacia en el plan"
        raise ValueError(msg)
    operations_count = int(plan.get("operations_count", 0))
    if operations_count <= 0:
        msg = "El plan de exportacion requiere al menos una operacion"
        raise ValueError(msg)
    return True


def execute_export_plan(plan: dict[str, object]) -> dict[str, object]:
    validate_export_plan(plan)
    return {
        "status": "ready",
        "output_path": plan["output_path"],
        "format": plan["format"],
        "operations_count": plan["operations_count"],
    }


def format_export_result(result: dict[str, object]) -> str:
    return (
        f"[{result['status']}] {result['output_path']} "
        f"({result['format']}, {result['operations_count']} ops)"
    )


def run_export_workflow(project: StudioProject, output_dir: str) -> dict[str, object]:
    plan = build_export_plan(project, output_dir=output_dir)
    result = execute_export_plan(plan)
    return {
        "result": result,
        "formatted": format_export_result(result),
    }


def build_batch_export_plan(
    projects: list[StudioProject],
    output_dir: str,
) -> list[dict[str, object]]:
    return [build_export_plan(project, output_dir=output_dir) for project in projects]


def summarize_batch_export_plan(
    plans: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "total_projects": len(plans),
        "total_operations": sum(int(plan["operations_count"]) for plan in plans),
        "output_paths": [str(plan["output_path"]) for plan in plans],
    }


def format_batch_export_summary(summary: dict[str, object]) -> str:
    total_projects = summary.get("total_projects", 0)
    total_operations = summary.get("total_operations", 0)
    raw_paths = summary.get("output_paths", [])
    paths_text = ", ".join(str(item) for item in raw_paths) if isinstance(raw_paths, list) else ""
    return (
        f"Lote: {total_projects} proyectos | "
        f"{total_operations} operaciones | {paths_text}"
    )


def execute_batch_export_plan(
    plans: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [execute_export_plan(plan) for plan in plans]


def summarize_batch_export_results(
    results: list[dict[str, object]],
) -> dict[str, object]:
    exported_paths = [
        str(item["output_path"]) for item in results if "output_path" in item
    ]
    return {
        "total_exported": len(results),
        "exported_paths": exported_paths,
    }


def format_batch_export_results_summary(summary: dict[str, object]) -> str:
    total_exported = summary.get("total_exported", 0)
    raw_paths = summary.get("exported_paths", [])
    paths_text = (
        ", ".join(str(item) for item in raw_paths) if isinstance(raw_paths, list) else ""
    )
    return f"Exportacion lote: {total_exported} archivos | {paths_text}"


def run_batch_export_workflow(
    projects: list[StudioProject],
    output_dir: str,
) -> dict[str, object]:
    plans = build_batch_export_plan(projects, output_dir=output_dir)
    results = execute_batch_export_plan(plans)
    summary = summarize_batch_export_results(results)
    return {
        "results": results,
        "summary": summary,
        "formatted": format_batch_export_results_summary(summary),
    }


def filter_export_plans_by_format(
    plans: list[dict[str, object]],
    fmt: str,
) -> list[dict[str, object]]:
    target = fmt.strip().lower()
    return [
        plan
        for plan in plans
        if str(plan.get("format", "")).strip().lower() == target
    ]


def count_export_plans_by_format(
    plans: list[dict[str, object]],
    fmt: str,
) -> int:
    return len(filter_export_plans_by_format(plans, fmt))


def group_export_plans_by_format(
    plans: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for plan in plans:
        fmt_key = str(plan.get("format", "")).strip().lower()
        grouped.setdefault(fmt_key, []).append(plan)
    return grouped


def summarize_plans_by_format(
    plans: list[dict[str, object]],
) -> dict[str, int]:
    grouped = group_export_plans_by_format(plans)
    return {fmt_key: len(items) for fmt_key, items in grouped.items()}
