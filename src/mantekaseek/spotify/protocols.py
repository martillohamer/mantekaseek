from typing import Protocol, runtime_checkable

from mantekaseek.spotify.resolver import SpotifyTrack


@runtime_checkable
class SpotifyCatalogProtocol(Protocol):
    def get_track(self, track_id: str) -> list[SpotifyTrack]: ...

    def get_album_tracks(self, album_id: str) -> list[SpotifyTrack]: ...

    def get_playlist_tracks(self, playlist_id: str) -> list[SpotifyTrack]: ...
