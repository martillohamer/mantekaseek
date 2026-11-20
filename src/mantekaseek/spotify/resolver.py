from dataclasses import dataclass
from typing import Protocol

from mantekaseek.spotify.parser import SpotifyTarget


@dataclass(slots=True, frozen=True)
class SpotifyTrack:
    spotify_id: str
    artist: str
    title: str
    duration_ms: int
    album: str | None = None


class SpotifyCatalog(Protocol):
    def get_track(self, track_id: str) -> list[SpotifyTrack]: ...

    def get_album_tracks(self, album_id: str) -> list[SpotifyTrack]: ...

    def get_playlist_tracks(self, playlist_id: str) -> list[SpotifyTrack]: ...


def resolve_spotify_target(target: SpotifyTarget, catalog: SpotifyCatalog) -> list[SpotifyTrack]:
    if target.kind == "track":
        return catalog.get_track(target.spotify_id)
    if target.kind == "album":
        return catalog.get_album_tracks(target.spotify_id)
    if target.kind == "playlist":
        return catalog.get_playlist_tracks(target.spotify_id)
    raise ValueError(f"Tipo de objetivo de Spotify no soportado: {target.kind}")
