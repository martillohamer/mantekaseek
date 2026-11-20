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
