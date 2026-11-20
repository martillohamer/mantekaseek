from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

TargetKind = Literal["track", "album", "playlist"]
ALLOWED_KINDS: set[str] = {"track", "album", "playlist"}


@dataclass(slots=True, frozen=True)
class SpotifyTarget:
    kind: TargetKind
    spotify_id: str


def parse_spotify_url(raw_url: str) -> SpotifyTarget:
    cleaned = raw_url.strip()
    if not cleaned:
        raise ValueError("La URL o URI de Spotify no puede estar vacia.")

    if cleaned.startswith("spotify:"):
        parts = cleaned.split(":")
        if len(parts) != 3 or parts[1] not in ALLOWED_KINDS or not parts[2].isalnum():
            raise ValueError(f"URI de Spotify no soportada o invalida: {raw_url}")
        kind: TargetKind = parts[1]  # type: ignore[assignment]
        return SpotifyTarget(kind=kind, spotify_id=parts[2])

    parsed = urlparse(cleaned)
    host = parsed.netloc.lower()
    if host not in {"open.spotify.com", "www.open.spotify.com"}:
        raise ValueError(f"Dominio no soportado para enlace de Spotify: {raw_url}")

    segments = [seg for seg in parsed.path.split("/") if seg]
    if segments and segments[0].startswith("intl-"):
        segments = segments[1:]

    if len(segments) < 2 or segments[0] not in ALLOWED_KINDS or not segments[1].isalnum():
        raise ValueError(f"Ruta de Spotify no soportada o invalida: {raw_url}")

    kind = segments[0]  # type: ignore[assignment]
    return SpotifyTarget(kind=kind, spotify_id=segments[1])
