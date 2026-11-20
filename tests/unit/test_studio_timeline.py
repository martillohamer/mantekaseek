from mantekaseek.studio.editor import (
    StudioProject,
    cut_segment,
    merge_tracks,
    paste_segment,
)


def test_studio_cut_paste_and_merge_operations() -> None:
    project = StudioProject(name="sesion_verano", output_format="wav", tempo_bpm=120.0)
    project = cut_segment(project, source_id="tema_a", start_sec=15.0, end_sec=45.0)
    project = paste_segment(project, source_id="tema_a", at_sec=30.0, repeat=2)
    project = merge_tracks(project, track_ids=("tema_a", "intro_midi"), crossfade_sec=1.5)

    assert len(project.operations) == 3
    assert project.operations[0].kind == "cut"
    assert project.operations[1].kind == "paste"
    assert project.operations[2].kind == "merge"


def test_summarize_studio_project() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        merge_tracks,
        paste_segment,
        summarize_studio_project,
    )

    project = StudioProject(name="sesion_verano", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=10.0, end_sec=25.0)
    project = paste_segment(project, source_id="tema_a", at_sec=25.0, repeat=1)
    project = merge_tracks(project, track_ids=("tema_a", "tema_b"), crossfade_sec=2.0)

    summary = summarize_studio_project(project)
    assert "sesion_verano" in summary
    assert "wav" in summary
    assert "128.0" in summary
    assert "ops=3" in summary


def test_build_export_plan_validates_format() -> None:
    import pytest

    from mantekaseek.studio.editor import StudioProject, build_export_plan, cut_segment

    project = StudioProject(name="master_demo", output_format="flac", tempo_bpm=125.0)
    project = cut_segment(project, source_id="loop_1", start_sec=0.0, end_sec=8.0)

    plan = build_export_plan(project, output_dir="/tmp/out")
    assert plan["output_path"] == "/tmp/out/master_demo.flac"
    assert plan["format"] == "flac"
    assert plan["operations_count"] == 1

    bad_project = StudioProject(name="malo", output_format="ogg")
    with pytest.raises(ValueError):
        build_export_plan(bad_project, output_dir="/tmp/out")


def test_estimate_timeline_duration() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        estimate_timeline_duration,
        merge_tracks,
        paste_segment,
    )

    project = StudioProject(name="sesion_test", output_format="wav", tempo_bpm=120.0)
    project = cut_segment(project, source_id="tema_a", start_sec=10.0, end_sec=30.0)
    project = paste_segment(project, source_id="tema_a", at_sec=30.0, repeat=2)
    project = merge_tracks(project, track_ids=("tema_a", "tema_b"), crossfade_sec=1.5)

    duration = estimate_timeline_duration(project, block_sec=4.0)
    assert duration == 29.5


def test_cli_studio_plan() -> None:
    from typer.testing import CliRunner

    from mantekaseek.cli.app import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "studio-plan",
            "sesion_live",
            "--format",
            "wav",
            "--tempo-bpm",
            "126.0",
            "--output-dir",
            "/tmp/studio_out",
        ],
    )
    assert result.exit_code == 0
    assert "sesion_live" in result.stdout
    assert "/tmp/studio_out/sesion_live.wav" in result.stdout


def test_clear_studio_operations() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        clear_operations,
        cut_segment,
    )

    project = StudioProject(name="toma_1", output_format="wav", tempo_bpm=124.0)
    project = cut_segment(project, source_id="loop_a", start_sec=0.0, end_sec=8.0)
    assert len(project.operations) == 1

    cleaned = clear_operations(project)
    assert cleaned.name == "toma_1"
    assert cleaned.tempo_bpm == 124.0
    assert cleaned.operations == ()


def test_undo_last_studio_operation() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        paste_segment,
        undo_last_operation,
    )

    project = StudioProject(name="sesion_undo", output_format="wav", tempo_bpm=125.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=10.0)
    project = paste_segment(project, source_id="tema_a", at_sec=10.0, repeat=1)
    assert len(project.operations) == 2

    undone = undo_last_operation(project)
    assert len(undone.operations) == 1
    assert undone.operations[0].kind == "cut"

    empty_undone = undo_last_operation(StudioProject(name="vacio"))
    assert empty_undone.operations == ()


def test_count_operations_by_kind() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        count_operations_by_kind,
        cut_segment,
        merge_tracks,
        paste_segment,
    )

    project = StudioProject(name="mezcla_final", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=16.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=20.0)
    project = paste_segment(project, source_id="tema_a", at_sec=16.0, repeat=1)
    project = merge_tracks(project, track_ids=("tema_a", "tema_b"), crossfade_sec=2.0)

    counts = count_operations_by_kind(project)
    assert counts == {"cut": 2, "paste": 1, "merge": 1}


def test_operations_for_target() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        merge_tracks,
        operations_for_target,
        paste_segment,
    )

    project = StudioProject(name="sesion_pistas", output_format="wav", tempo_bpm=126.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=12.0)
    project = paste_segment(project, source_id="tema_b", at_sec=12.0, repeat=1)
    project = merge_tracks(project, track_ids=("tema_a", "tema_b"), crossfade_sec=1.0)

    ops_a = operations_for_target(project, target_id="tema_a")
    assert [op.kind for op in ops_a] == ["cut", "merge"]


def test_set_project_tempo() -> None:
    import pytest

    from mantekaseek.studio.editor import StudioProject, cut_segment, set_project_tempo

    project = StudioProject(name="sesion_bpm", output_format="wav", tempo_bpm=120.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)

    updated = set_project_tempo(project, bpm=132.0)
    assert updated.tempo_bpm == 132.0
    assert len(updated.operations) == 1

    with pytest.raises(ValueError):
        set_project_tempo(updated, bpm=0.0)


def test_set_output_format() -> None:
    import pytest

    from mantekaseek.studio.editor import StudioProject, cut_segment, set_output_format

    project = StudioProject(name="master_final", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)

    updated = set_output_format(project, output_format="MP3")
    assert updated.output_format == "mp3"
    assert updated.tempo_bpm == 128.0
    assert len(updated.operations) == 1

    with pytest.raises(ValueError):
        set_output_format(updated, output_format="aac")


def test_rename_studio_project() -> None:
    import pytest

    from mantekaseek.studio.editor import StudioProject, cut_segment, rename_project

    project = StudioProject(name="borrador_1", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)

    renamed = rename_project(project, new_name="master_final")
    assert renamed.name == "master_final"
    assert renamed.output_format == "wav"
    assert renamed.tempo_bpm == 128.0
    assert len(renamed.operations) == 1

    with pytest.raises(ValueError):
        rename_project(renamed, new_name="   ")


def test_list_project_targets() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        list_project_targets,
        merge_tracks,
        paste_segment,
    )

    project = StudioProject(name="sesion_pistas", output_format="wav", tempo_bpm=126.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    project = paste_segment(project, source_id="tema_a", at_sec=8.0, repeat=1)
    project = merge_tracks(project, track_ids=("tema_a", "tema_b"), crossfade_sec=1.0)

    assert list_project_targets(project) == ["tema_a", "tema_b"]


def test_count_project_targets() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        count_project_targets,
        cut_segment,
        merge_tracks,
        paste_segment,
    )

    project = StudioProject(name="sesion_conteo", output_format="wav", tempo_bpm=126.0)
    assert count_project_targets(project) == 0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    project = paste_segment(project, source_id="tema_a", at_sec=8.0, repeat=1)
    project = merge_tracks(project, track_ids=("tema_a", "tema_b"), crossfade_sec=1.0)

    assert count_project_targets(project) == 2


def test_has_exportable_operations() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        has_exportable_operations,
    )

    project = StudioProject(name="sesion_vacia", output_format="wav", tempo_bpm=128.0)
    assert has_exportable_operations(project) is False

    updated = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert has_exportable_operations(updated) is True


def test_estimate_export_size_mb() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        estimate_export_size_mb,
    )

    project = StudioProject(name="master_60s", output_format="wav", tempo_bpm=128.0)
    assert estimate_export_size_mb(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=60.0)
    assert estimate_export_size_mb(project) > 0.0


def test_format_timeline_duration() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_duration,
    )

    project = StudioProject(name="sesion_reloj", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_duration(project) == "00:00"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=125.0)
    assert format_timeline_duration(project) == "02:05"


def test_format_export_overview() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_export_overview,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=60.0)

    overview = format_export_overview(project)
    assert "sesion_club" in overview
    assert "WAV" in overview
    assert "01:00" in overview
    assert "MB" in overview


def test_has_valid_tempo() -> None:
    from mantekaseek.studio.editor import StudioProject, has_valid_tempo

    valid = StudioProject(name="set_club", output_format="wav", tempo_bpm=128.0)
    assert has_valid_tempo(valid) is True

    too_slow = StudioProject(name="lento", output_format="wav", tempo_bpm=10.0)
    too_fast = StudioProject(name="rapido", output_format="wav", tempo_bpm=400.0)
    assert has_valid_tempo(too_slow) is False
    assert has_valid_tempo(too_fast) is False


def test_estimate_bars() -> None:
    from mantekaseek.studio.editor import StudioProject, cut_segment, estimate_bars

    project = StudioProject(name="sesion_120", output_format="wav", tempo_bpm=120.0)
    assert estimate_bars(project) == 0

    # A 120 BPM: 1 beat = 0.5s, 1 compas de 4/4 = 2.0s -> 16.0s son 8 compases
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=16.0)
    assert estimate_bars(project) == 8


def test_format_bars_label() -> None:
    from mantekaseek.studio.editor import StudioProject, cut_segment, format_bars_label

    project = StudioProject(name="sesion_120", output_format="wav", tempo_bpm=120.0)
    assert format_bars_label(project) == "0 compases"

    # 2.0s a 120 BPM en 4/4 = 1 compas
    one_bar = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=2.0)
    assert format_bars_label(one_bar) == "1 compas"

    # 16.0s a 120 BPM en 4/4 = 8 compases
    eight_bars = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=16.0)
    assert format_bars_label(eight_bars) == "8 compases"


def test_estimate_beats() -> None:
    from mantekaseek.studio.editor import StudioProject, cut_segment, estimate_beats

    project = StudioProject(name="sesion_120", output_format="wav", tempo_bpm=120.0)
    assert estimate_beats(project) == 0

    # A 120 BPM: 1 beat = 0.5s -> 4.0s son 8 beats
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert estimate_beats(project) == 8


def test_format_beats_label() -> None:
    from mantekaseek.studio.editor import StudioProject, cut_segment, format_beats_label

    project = StudioProject(name="sesion_120", output_format="wav", tempo_bpm=120.0)
    assert format_beats_label(project) == "0 pulsos"

    # A 120 BPM: 1 beat = 0.5s -> 1 pulso
    one_beat = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=0.5)
    assert format_beats_label(one_beat) == "1 pulso"

    # 4.0s a 120 BPM -> 8 pulsos
    eight_beats = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert format_beats_label(eight_beats) == "8 pulsos"


def test_has_project_targets() -> None:
    from mantekaseek.studio.editor import StudioProject, cut_segment, has_project_targets

    project = StudioProject(name="sesion_vacia", output_format="wav", tempo_bpm=128.0)
    assert has_project_targets(project) is False

    project = cut_segment(project, source_id="tema_base", start_sec=0.0, end_sec=8.0)
    assert has_project_targets(project) is True


def test_has_operations() -> None:
    from mantekaseek.studio.editor import StudioProject, cut_segment, has_operations

    project = StudioProject(name="sesion_vacia", output_format="wav", tempo_bpm=128.0)
    assert has_operations(project) is False

    project = cut_segment(project, source_id="tema_base", start_sec=0.0, end_sec=4.0)
    assert has_operations(project) is True


def test_count_operations() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        count_operations,
        cut_segment,
        paste_segment,
    )

    project = StudioProject(name="sesion_test", output_format="wav", tempo_bpm=128.0)
    assert count_operations(project) == 0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = paste_segment(project, source_id="tema_b", at_sec=4.0)
    assert count_operations(project) == 2


def test_is_ready_to_export() -> None:
    import pytest

    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        is_ready_to_export,
        set_project_tempo,
    )

    project = StudioProject(name="sesion_export", output_format="wav", tempo_bpm=128.0)
    assert is_ready_to_export(project) is False

    with pytest.raises(ValueError):
        set_project_tempo(project, 0.0)

    invalid_bpm_project = StudioProject(
        name="sesion_export", output_format="wav", tempo_bpm=0.0
    )
    invalid_bpm_project = cut_segment(
        invalid_bpm_project, source_id="tema_a", start_sec=0.0, end_sec=4.0
    )
    assert is_ready_to_export(invalid_bpm_project) is False

    ready = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert is_ready_to_export(ready) is True


def test_format_export_readiness() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_export_readiness,
    )

    project = StudioProject(name="sesion_export", output_format="wav", tempo_bpm=128.0)
    assert format_export_readiness(project) == "No lista para exportar"

    ready = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert format_export_readiness(ready) == "Lista para exportar"


def test_format_tempo_label() -> None:
    from mantekaseek.studio.editor import StudioProject, format_tempo_label

    valid_project = StudioProject(name="sesion_128", output_format="wav", tempo_bpm=128.0)
    assert format_tempo_label(valid_project) == "128.0 BPM"

    invalid_project = StudioProject(name="sesion_zero", output_format="wav", tempo_bpm=0.0)
    assert format_tempo_label(invalid_project) == "Tempo no valido"


def test_format_project_summary() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_project_summary,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert (
        format_project_summary(project)
        == "sesion_club | 128.0 BPM | WAV | No lista para exportar"
    )

    ready = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert (
        format_project_summary(ready)
        == "sesion_club | 128.0 BPM | WAV | Lista para exportar"
    )


def test_format_timeline_summary() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_summary,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_summary(project) == "0 operaciones | 0.0s"

    edited = cut_segment(project, source_id="tema_a", start_sec=2.0, end_sec=6.0)
    assert format_timeline_summary(edited) == "1 operaciones | 4.0s"


def test_format_studio_report() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_studio_report,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert (
        format_studio_report(project)
        == "sesion_club | 128.0 BPM | WAV | No lista para exportar | 0 operaciones | 0.0s"
    )

    edited = cut_segment(project, source_id="tema_a", start_sec=2.0, end_sec=6.0)
    assert (
        format_studio_report(edited)
        == "sesion_club | 128.0 BPM | WAV | Lista para exportar | 1 operaciones | 4.0s"
    )


def test_format_output_format_label() -> None:
    from mantekaseek.studio.editor import StudioProject, format_output_format_label

    wav_project = StudioProject(name="sesion_wav", output_format=" wav ", tempo_bpm=128.0)
    assert format_output_format_label(wav_project) == "WAV"

    empty_project = StudioProject(name="sesion_vacia", output_format="   ", tempo_bpm=128.0)
    assert format_output_format_label(empty_project) == "FORMATO NO DEFINIDO"


def test_has_output_format() -> None:
    from mantekaseek.studio.editor import StudioProject, has_output_format

    wav_project = StudioProject(name="sesion_wav", output_format="wav", tempo_bpm=128.0)
    assert has_output_format(wav_project) is True

    empty_project = StudioProject(name="sesion_vacia", output_format="   ", tempo_bpm=128.0)
    assert has_output_format(empty_project) is False


def test_has_project_name() -> None:
    from mantekaseek.studio.editor import StudioProject, has_project_name

    named_project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert has_project_name(named_project) is True

    unnamed_project = StudioProject(name="   ", output_format="wav", tempo_bpm=128.0)
    assert has_project_name(unnamed_project) is False


def test_format_project_name() -> None:
    from mantekaseek.studio.editor import StudioProject, format_project_name

    named_project = StudioProject(name="  sesion_club  ", output_format="wav", tempo_bpm=128.0)
    assert format_project_name(named_project) == "sesion_club"

    unnamed_project = StudioProject(name="   ", output_format="wav", tempo_bpm=128.0)
    assert format_project_name(unnamed_project) == "PROYECTO SIN NOMBRE"


def test_format_project_summary_normalizes_name() -> None:
    from mantekaseek.studio.editor import StudioProject, format_project_summary

    project = StudioProject(name="   ", output_format="wav", tempo_bpm=128.0)
    assert (
        format_project_summary(project)
        == "PROYECTO SIN NOMBRE | 128.0 BPM | WAV | No lista para exportar"
    )


def test_has_complete_export_config() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        has_complete_export_config,
    )

    incomplete_name = StudioProject(name="   ", output_format="wav", tempo_bpm=128.0)
    incomplete_name = cut_segment(incomplete_name, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert has_complete_export_config(incomplete_name) is False

    incomplete_fmt = StudioProject(name="sesion_club", output_format="   ", tempo_bpm=128.0)
    incomplete_fmt = cut_segment(incomplete_fmt, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert has_complete_export_config(incomplete_fmt) is False

    complete = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    complete = cut_segment(complete, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert has_complete_export_config(complete) is True


def test_format_export_config_status() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_export_config_status,
    )

    incomplete = StudioProject(name="", output_format="wav", tempo_bpm=128.0)
    assert format_export_config_status(incomplete) == "Configuracion incompleta"

    complete = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    complete = cut_segment(complete, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert format_export_config_status(complete) == "Configuracion completa"


def test_get_missing_export_requirements() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_missing_export_requirements,
    )

    empty_project = StudioProject(name="   ", output_format="   ", tempo_bpm=128.0)
    assert get_missing_export_requirements(empty_project) == [
        "nombre del proyecto",
        "formato de salida",
        "operaciones en la linea de tiempo",
    ]

    ready_project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    ready_project = cut_segment(ready_project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert get_missing_export_requirements(ready_project) == []


def test_format_missing_export_requirements() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_missing_export_requirements,
    )

    missing_both = StudioProject(name="", output_format="", tempo_bpm=128.0)
    assert (
        format_missing_export_requirements(missing_both)
        == "nombre del proyecto, formato de salida, operaciones en la linea de tiempo"
    )

    ready_project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    ready_project = cut_segment(ready_project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert format_missing_export_requirements(ready_project) == "Ninguno"


def test_format_export_diagnostic() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_export_diagnostic,
    )

    blocked = StudioProject(name="", output_format="wav", tempo_bpm=128.0)
    assert (
        format_export_diagnostic(blocked)
        == "Exportacion bloqueada: falta nombre del proyecto, operaciones en la linea de tiempo"
    )

    ready = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    ready = cut_segment(ready, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert (
        format_export_diagnostic(ready)
        == "Exportacion lista: sesion_club (WAV, 128.0 BPM)"
    )


def test_build_export_summary() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        build_export_summary,
        cut_segment,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    summary = build_export_summary(project)

    assert summary == {
        "project": "sesion_club",
        "ready": True,
        "format": "WAV",
        "tempo": "128.0 BPM",
        "missing": [],
        "diagnostic": "Exportacion lista: sesion_club (WAV, 128.0 BPM)",
    }


def test_format_export_summary() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_export_summary,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    rendered = format_export_summary(project)

    assert rendered == (
        "Proyecto: sesion_club\n"
        "Formato: WAV\n"
        "Tempo: 128.0 BPM\n"
        "Faltantes: Ninguno\n"
        "Diagnostico: Exportacion lista: sesion_club (WAV, 128.0 BPM)"
    )


def test_estimate_timeline_duration_sec() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        estimate_timeline_duration_sec,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert estimate_timeline_duration_sec(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=2.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=10.0, end_sec=15.5)
    assert estimate_timeline_duration_sec(project) == 9.5


def test_estimate_timeline_bars() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        estimate_timeline_bars,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=120.0)
    assert estimate_timeline_bars(project) == 0.0

    # A 120 BPM: 2.0 s por compas de 4/4 -> 8.0 s equivalen a 4.0 compases
    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    assert estimate_timeline_bars(project) == 4.0


def test_format_timeline_bars() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_bars,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=120.0)
    assert format_timeline_bars(project) == "0.0 compases"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    assert format_timeline_bars(project) == "4.0 compases"


def test_has_timeline_operations() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        has_timeline_operations,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert has_timeline_operations(project) is False

    project = cut_segment(project, source_id="tema_a", start_sec=1.0, end_sec=4.0)
    assert has_timeline_operations(project) is True


def test_get_last_source_id() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_last_source_id,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_last_source_id(project) is None

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=5.0, end_sec=9.0)
    assert get_last_source_id(project) == "tema_b"


def test_count_cut_operations() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        count_cut_operations,
        cut_segment,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert count_cut_operations(project) == 0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=8.0)
    assert count_cut_operations(project) == 2


def test_list_timeline_sources() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        list_timeline_sources,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert list_timeline_sources(project) == []

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=8.0)
    project = cut_segment(project, source_id="tema_a", start_sec=8.0, end_sec=12.0)
    assert list_timeline_sources(project) == ["tema_a", "tema_b"]


def test_count_timeline_sources() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        count_timeline_sources,
        cut_segment,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert count_timeline_sources(project) == 0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=8.0)
    project = cut_segment(project, source_id="tema_a", start_sec=8.0, end_sec=12.0)
    assert count_timeline_sources(project) == 2


def test_has_timeline_source() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        has_timeline_source,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert has_timeline_source(project, "tema_a") is False

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    assert has_timeline_source(project, "tema_a") is True
    assert has_timeline_source(project, "tema_b") is False


def test_get_timeline_end_sec() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_end_sec,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_end_sec(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=2.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=10.0, end_sec=14.5)
    assert get_timeline_end_sec(project) == 14.5


def test_get_timeline_start_sec() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_start_sec,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_start_sec(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=5.0, end_sec=9.0)
    project = cut_segment(project, source_id="tema_b", start_sec=2.5, end_sec=6.0)
    assert get_timeline_start_sec(project) == 2.5


def test_get_timeline_span_sec() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_span_sec,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_span_sec(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=2.5, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=10.0, end_sec=14.5)
    assert get_timeline_span_sec(project) == 12.0


def test_format_timeline_span() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_span,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_span(project) == "00:00"

    project = cut_segment(project, source_id="tema_a", start_sec=2.5, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=10.0, end_sec=74.5)
    assert format_timeline_span(project) == "01:12"


def test_get_timeline_span_bars() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_span_bars,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=120.0)
    assert get_timeline_span_bars(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=8.0)
    assert get_timeline_span_bars(project) == 4.0


def test_format_timeline_span_bars() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_span_bars,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=120.0)
    assert format_timeline_span_bars(project) == "0.00"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=8.0)
    assert format_timeline_span_bars(project) == "4.00"


def test_has_timeline_gaps() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        has_timeline_gaps,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert has_timeline_gaps(project) is False

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=4.0, end_sec=8.0)
    assert has_timeline_gaps(project) is False

    project = cut_segment(project, source_id="tema_c", start_sec=10.5, end_sec=14.0)
    assert has_timeline_gaps(project) is True


def test_count_timeline_gaps() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        count_timeline_gaps,
        cut_segment,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert count_timeline_gaps(project) == 0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=6.0, end_sec=8.0)
    project = cut_segment(project, source_id="tema_c", start_sec=11.0, end_sec=14.0)
    assert count_timeline_gaps(project) == 2


def test_get_timeline_gap_sec() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_gap_sec,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_gap_sec(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=6.0, end_sec=8.0)
    project = cut_segment(project, source_id="tema_c", start_sec=11.0, end_sec=14.0)
    assert get_timeline_gap_sec(project) == 5.0


def test_format_timeline_gap() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_gap,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_gap(project) == "00:00"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=69.0, end_sec=75.0)
    assert format_timeline_gap(project) == "01:05"


def test_get_timeline_active_sec() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_active_sec,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_active_sec(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=4.0)
    project = cut_segment(project, source_id="tema_b", start_sec=6.0, end_sec=8.0)
    project = cut_segment(project, source_id="tema_c", start_sec=11.0, end_sec=14.0)
    assert get_timeline_active_sec(project) == 9.0


def test_format_timeline_active() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_active,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_active(project) == "00:00"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=35.0)
    project = cut_segment(project, source_id="tema_b", start_sec=40.0, end_sec=75.0)
    assert format_timeline_active(project) == "01:10"


def test_get_timeline_active_ratio() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_active_ratio,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_active_ratio(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=8.0, end_sec=10.0)
    assert get_timeline_active_ratio(project) == 0.8


def test_format_timeline_active_pct() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_active_pct,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_active_pct(project) == "0.0%"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=8.0, end_sec=10.0)
    assert format_timeline_active_pct(project) == "80.0%"


def test_get_timeline_gap_ratio() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_gap_ratio,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert get_timeline_gap_ratio(project) == 0.0

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=8.0, end_sec=10.0)
    assert get_timeline_gap_ratio(project) == 0.2


def test_format_timeline_gap_pct() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        format_timeline_gap_pct,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert format_timeline_gap_pct(project) == "0.0%"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=8.0, end_sec=10.0)
    assert format_timeline_gap_pct(project) == "20.0%"


def test_get_timeline_summary() -> None:
    from mantekaseek.studio.editor import (
        StudioProject,
        cut_segment,
        get_timeline_summary,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    empty_summary = get_timeline_summary(project)
    assert empty_summary["segments_count"] == 0
    assert empty_summary["active_pct_formatted"] == "0.0%"
    assert empty_summary["gap_pct_formatted"] == "0.0%"

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=6.0)
    project = cut_segment(project, source_id="tema_b", start_sec=8.0, end_sec=10.0)
    summary = get_timeline_summary(project)
    assert summary["segments_count"] == 2
    assert summary["span_sec"] == 10.0
    assert summary["gap_sec"] == 2.0
    assert summary["active_sec"] == 8.0
    assert summary["active_ratio"] == 0.8
    assert summary["gap_ratio"] == 0.2
    assert summary["span_formatted"] == "00:10"
    assert summary["gap_formatted"] == "00:02"
    assert summary["active_formatted"] == "00:08"
    assert summary["active_pct_formatted"] == "80.0%"
    assert summary["gap_pct_formatted"] == "20.0%"


def test_can_export_project() -> None:
    from mantekaseek.studio.editor import StudioProject, can_export_project, cut_segment

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    assert can_export_project(project) is False

    project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    assert can_export_project(project) is True


def test_build_export_plan() -> None:
    from mantekaseek.studio.editor import StudioProject, build_export_plan, cut_segment

    project = StudioProject(name="sesion_club", output_format="WAV", tempo_bpm=128.0)
    plan_empty = build_export_plan(project, output_dir="/tmp/out/")
    assert plan_empty["output_path"] == "/tmp/out/sesion_club.wav"
    assert plan_empty["format"] == "wav"
    assert plan_empty["tempo_bpm"] == 128.0
    assert plan_empty["operations_count"] == 0

    ready_project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    plan_ready = build_export_plan(ready_project, output_dir="/tmp/out")
    assert plan_ready["operations_count"] == 1


def test_format_export_plan() -> None:
    from mantekaseek.studio.editor import StudioProject, build_export_plan, format_export_plan

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    plan = build_export_plan(project, output_dir="/tmp/out")
    formatted = format_export_plan(plan)
    assert "/tmp/out/sesion_club.wav" in formatted
    assert "wav" in formatted
    assert "128.0" in formatted


def test_validate_export_plan() -> None:
    import pytest

    from mantekaseek.studio.editor import (
        StudioProject,
        build_export_plan,
        cut_segment,
        validate_export_plan,
    )

    project = StudioProject(name="sesion_club", output_format="wav", tempo_bpm=128.0)
    empty_plan = build_export_plan(project, output_dir="/tmp/out")
    with pytest.raises(ValueError):
        validate_export_plan(empty_plan)

    ready_project = cut_segment(project, source_id="tema_a", start_sec=0.0, end_sec=8.0)
    ready_plan = build_export_plan(ready_project, output_dir="/tmp/out")
    assert validate_export_plan(ready_plan) is True
