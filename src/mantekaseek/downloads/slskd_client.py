from dataclasses import fields
from typing import Any, Protocol

from mantekaseek.downloads.ranking import DownloadCandidate


class HttpJsonTransport(Protocol):
    def post_json(
        self, url: str, headers: dict[str, str], body: dict[str, Any]
    ) -> dict[str, Any]: ...


def _build_candidate(
    *,
    source: str,
    title: str,
    bitrate_kbps: int,
    duration_ms: int,
    uri: str,
    score: float,
) -> DownloadCandidate:
    allowed = {f.name for f in fields(DownloadCandidate)}
    candidate_values: dict[str, Any] = {
        "source": source,
        "title": title,
        "artist": title.split(" - ")[0].strip() if " - " in title else "",
        "filename": title,
        "uri": uri,
        "url": uri,
        "bitrate_kbps": bitrate_kbps,
        "bitrate": bitrate_kbps,
        "duration_ms": duration_ms,
        "score": score,
        "seeders": 1,
    }
    filtered = {k: v for k, v in candidate_values.items() if k in allowed}
    return DownloadCandidate(**filtered)


class SlskdClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        transport: HttpJsonTransport,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.transport = transport

    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        query = f"{artist} {title}".strip()
        url = f"{self.base_url}/api/v0/searches"
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = self.transport.post_json(url, headers, {"searchText": query})

        results: list[DownloadCandidate] = []
        responses = payload.get("responses", [])
        if not isinstance(responses, list):
            return results

        for peer in responses:
            if not isinstance(peer, dict):
                continue
            username = str(peer.get("username", "peer"))
            upload_speed = float(peer.get("uploadSpeed", 0) or 0)
            speed_score = min(upload_speed / 1_000_000.0, 10.0)
            files = peer.get("files", [])
            if not isinstance(files, list):
                continue

            for item in files:
                if not isinstance(item, dict):
                    continue
                raw_name = str(item.get("filename", query))
                clean_name = raw_name.split("/")[-1]
                bitrate = int(item.get("bitRate", 0) or 0)
                length_sec = int(item.get("length", 0) or 0)
                duration_ms = length_sec * 1000
                uri = f"slsk://{username}/{raw_name}"
                results.append(
                    _build_candidate(
                        source="slskd",
                        title=clean_name,
                        bitrate_kbps=bitrate,
                        duration_ms=duration_ms,
                        uri=uri,
                        score=round(speed_score + (bitrate / 100.0), 2),
                    )
                )
        return results
