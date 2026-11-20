from mantekaseek.spotify.parser import parse_spotify_url
from mantekaseek.spotify.resolver import SpotifyTrack, resolve_spotify_target


class FakeSpotifyCatalog:
    def get_track(self, track_id: str) -> list[SpotifyTrack]:
        return [
            SpotifyTrack(
                spotify_id=track_id,
                artist="Daft Punk",
                title="One More Time",
                duration_ms=320000,
            )
        ]

    def get_album_tracks(self, album_id: str) -> list[SpotifyTrack]:
        return [
            SpotifyTrack(
                spotify_id=f"{album_id}_1",
                artist="Daft Punk",
                title="Discovery 1",
                duration_ms=200000,
            ),
            SpotifyTrack(
                spotify_id=f"{album_id}_2",
                artist="Daft Punk",
                title="Discovery 2",
                duration_ms=210000,
            ),
        ]

    def get_playlist_tracks(self, playlist_id: str) -> list[SpotifyTrack]:
        return [
            SpotifyTrack(
                spotify_id=f"{playlist_id}_a",
                artist="Artista A",
                title="Tema A",
                duration_ms=180000,
            ),
        ]


def test_resolve_track_album_and_playlist() -> None:
    catalog = FakeSpotifyCatalog()

    tracks_single = resolve_spotify_target(
        parse_spotify_url("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"),
        catalog,
    )
    assert len(tracks_single) == 1
    assert tracks_single[0].title == "One More Time"

    tracks_album = resolve_spotify_target(
        parse_spotify_url("https://open.spotify.com/album/6de0bDnzbNc9Xb6a8ingze"),
        catalog,
    )
    assert len(tracks_album) == 2

    tracks_playlist = resolve_spotify_target(
        parse_spotify_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"),
        catalog,
    )
    assert len(tracks_playlist) == 1
    assert tracks_playlist[0].artist == "Artista A"
