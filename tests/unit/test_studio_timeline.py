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
