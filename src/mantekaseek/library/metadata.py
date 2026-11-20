from mantekaseek.library.duplicates import LibraryTrack
from mantekaseek.library.keys import key_to_camelot, key_to_open_key


def build_id3_tags(track: LibraryTrack) -> dict[str, str]:
    tags: dict[str, str] = {
        "TPE1": track.artist.strip(),
        "TIT2": track.title.strip(),
    }
    if track.bpm is not None:
        tags["TBPM"] = str(round(track.bpm))
    if track.genre:
        tags["TCON"] = track.genre.strip()
    if track.musical_key:
        clean_key = track.musical_key.strip()
        camelot = key_to_camelot(clean_key)
        open_key = key_to_open_key(clean_key)
        tags["TKEY"] = f"{clean_key} ({camelot} / {open_key})"
    return tags
