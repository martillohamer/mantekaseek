from mantekaseek.library.duplicates import LibraryTrack, find_duplicates
from mantekaseek.library.keys import key_to_camelot, key_to_open_key


def test_key_conversions_camelot_and_open_key() -> None:
    assert key_to_camelot("C") == "8B"
    assert key_to_camelot("Am") == "8A"
    assert key_to_camelot("F#m") == "11A"

    assert key_to_open_key("C") == "1d"
    assert key_to_open_key("Am") == "1m"
    assert key_to_open_key("F#m") == "4m"


def test_find_duplicates_by_normalized_artist_and_title() -> None:
    t1 = LibraryTrack(track_id="1", artist="Peggy Gou", title="It Goes Like (Nanana)", bpm=129.0)
    t2 = LibraryTrack(
        track_id="2",
        artist="peggy gou",
        title="It Goes Like (Nanana) (Original Mix)",
        bpm=129.0,
    )
    t3 = LibraryTrack(track_id="3", artist="Bicep", title="Glue", bpm=128.0)

    dupes = find_duplicates([t1, t2, t3])
    assert len(dupes) == 1
    assert {dupes[0][0].track_id, dupes[0][1].track_id} == {"1", "2"}
