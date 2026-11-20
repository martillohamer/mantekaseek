import pytest

from mantekaseek.spotify.parser import SpotifyTarget, parse_spotify_url


@pytest.mark.parametrize(
    ("raw_url", "expected_kind", "expected_id"),
    [
        (
            "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT",
            "track",
            "4cOdK2wGLETKBW3PvgPWqT",
        ),
        (
            "https://open.spotify.com/intl-es/album/6de0bDnzbNc9Xb6a8ingze?si=abc",
            "album",
            "6de0bDnzbNc9Xb6a8ingze",
        ),
        (
            "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "playlist",
            "37i9dQZF1DXcBWIGoYBM5M",
        ),
        ("spotify:track:4cOdK2wGLETKBW3PvgPWqT", "track", "4cOdK2wGLETKBW3PvgPWqT"),
    ],
)
def test_parse_valid_spotify_targets(raw_url: str, expected_kind: str, expected_id: str) -> None:
    target = parse_spotify_url(raw_url)
    assert isinstance(target, SpotifyTarget)
    assert target.kind == expected_kind
    assert target.spotify_id == expected_id


@pytest.mark.parametrize(
    "bad_url",
    [
        "",
        "   ",
        "https://example.com/track/123",
        "https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF",
        "spotify:user:someone",
    ],
)
def test_parse_invalid_spotify_url_raises(bad_url: str) -> None:
    with pytest.raises(ValueError):
        parse_spotify_url(bad_url)
