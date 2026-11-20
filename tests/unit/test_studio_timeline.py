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
