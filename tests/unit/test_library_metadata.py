from mantekaseek.library.duplicates import LibraryTrack
from mantekaseek.library.metadata import build_id3_tags


def test_build_id3_tags_includes_bpm_genre_and_harmonic_key() -> None:
    track = LibraryTrack(
        track_id="42",
        artist="Disclosure",
        title="Latch",
        bpm=122.4,
        musical_key="Am",
        genre="Deep House",
    )
    tags = build_id3_tags(track)
    assert tags["TPE1"] == "Disclosure"
    assert tags["TIT2"] == "Latch"
    assert tags["TBPM"] == "122"
    assert tags["TCON"] == "Deep House"
    assert "8A" in tags["TKEY"]
    assert "1m" in tags["TKEY"]
