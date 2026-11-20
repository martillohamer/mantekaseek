from typing import Any

from mantekaseek.downloads.ranking import DownloadCandidate
from mantekaseek.downloads.slskd_client import SlskdClient


class FakeHttpTransport:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.calls: list[tuple[str, str]] = []

    def post_json(self, url: str, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((url, headers.get("X-API-KEY", "")))
        return self.payload


def test_slskd_client_search_maps_candidates() -> None:
    transport = FakeHttpTransport(
        payload={
            "responses": [
                {
                    "username": "dj_asturias",
                    "uploadSpeed": 2457600,
                    "files": [
                        {
                            "filename": "@@dj_asturias/House/Daft Punk - One More Time.mp3",
                            "size": 12800000,
                            "bitRate": 320,
                            "length": 320,
                        }
                    ],
                }
            ]
        }
    )
    client = SlskdClient(
        base_url="http://localhost:5030",
        api_key="secreto-prueba",
        transport=transport,
    )
    candidates = client.search(artist="Daft Punk", title="One More Time")

    assert len(candidates) == 1
    cand = candidates[0]
    assert isinstance(cand, DownloadCandidate)
    assert cand.source == "slskd"
    assert cand.bitrate_kbps == 320
    assert cand.duration_ms == 320000
    assert len(transport.calls) == 1
