import re
from dataclasses import dataclass

_MIX_SUFFIX_RE = re.compile(
    r"\s*\((?:original mix|extended mix|radio edit|club mix|dub mix)\)\s*$",
    re.IGNORECASE,
)


@dataclass(slots=True, frozen=True)
class LibraryTrack:
    track_id: str
    artist: str
    title: str
    bpm: float | None = None
    musical_key: str | None = None
    genre: str | None = None


def normalize_track_signature(artist: str, title: str) -> str:
    clean_artist = re.sub(r"\s+", " ", artist.strip().lower())
    clean_title = _MIX_SUFFIX_RE.sub("", title.strip().lower())
    clean_title = re.sub(r"\s+", " ", clean_title).strip()
    return f"{clean_artist} - {clean_title}"


def find_duplicates(
    tracks: list[LibraryTrack],
) -> list[tuple[LibraryTrack, LibraryTrack]]:
    seen: dict[str, LibraryTrack] = {}
    duplicates: list[tuple[LibraryTrack, LibraryTrack]] = []
    for track in tracks:
        sig = normalize_track_signature(track.artist, track.title)
        if sig in seen:
            duplicates.append((seen[sig], track))
        else:
            seen[sig] = track
    return duplicates
