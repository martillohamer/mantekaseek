from mantekaseek.dj.mixer import TrackCandidateDJ, suggest_next_tracks


def test_suggest_next_tracks_prioritizes_harmonic_and_bpm_fit() -> None:
    c1 = TrackCandidateDJ(track_id="1", title="Tema 1", bpm=126.5, camelot="9A")
    c2 = TrackCandidateDJ(track_id="2", title="Tema 2", bpm=126.0, camelot="8A")
    c3 = TrackCandidateDJ(track_id="3", title="Tema 3", bpm=142.0, camelot="8A")
    c4 = TrackCandidateDJ(track_id="4", title="Tema 4", bpm=126.0, camelot="2B")

    suggestions = suggest_next_tracks(
        current_bpm=126.0,
        current_camelot="8A",
        candidates=[c4, c3, c1, c2],
        max_bpm_delta=4.0,
    )
    assert [s.track_id for s in suggestions] == ["2", "1"]


def test_rank_mix_suggestions_prioritizes_harmonic_and_bpm() -> None:
    from mantekaseek.dj.mixer import MixSuggestion, rank_mix_suggestions

    sug_bpm_lejos = MixSuggestion(
        track_id="t_bpm_lejos",
        bpm_diff=8.0,
        harmonic_score=1.0,
    )
    sug_ideal = MixSuggestion(
        track_id="t_ideal",
        bpm_diff=0.5,
        harmonic_score=1.0,
    )
    sug_armonia_baja = MixSuggestion(
        track_id="t_armonia_baja",
        bpm_diff=0.5,
        harmonic_score=0.2,
    )

    ranked = rank_mix_suggestions([sug_bpm_lejos, sug_armonia_baja, sug_ideal])
    assert [item.track_id for item in ranked] == ["t_ideal", "t_bpm_lejos", "t_armonia_baja"]


def test_filter_mix_suggestions_by_harmony_and_bpm() -> None:
    from mantekaseek.dj.mixer import MixSuggestion, filter_mix_suggestions

    candidatos = [
        MixSuggestion(track_id="valida", bpm_diff=1.5, harmonic_score=0.9),
        MixSuggestion(track_id="bpm_alto", bpm_diff=6.0, harmonic_score=1.0),
        MixSuggestion(track_id="armonia_baja", bpm_diff=1.0, harmonic_score=0.3),
    ]

    filtradas = filter_mix_suggestions(
        candidatos,
        min_harmonic_score=0.7,
        max_bpm_diff=3.0,
    )
    assert [item.track_id for item in filtradas] == ["valida"]
