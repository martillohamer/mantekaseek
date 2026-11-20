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
