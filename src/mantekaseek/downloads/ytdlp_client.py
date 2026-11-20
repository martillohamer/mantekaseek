from dataclasses import fields
from typing import Any, Protocol

from mantekaseek.downloads.ranking import DownloadCandidate


class YtdlpCommandRunner(Protocol):
    def run_json_lines(self, args: list[str]) -> list[dict[str, Any]]: ...


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
        "seeders": 0,
    }
    filtered = {k: v for k, v in candidate_values.items() if k in allowed}
    return DownloadCandidate(**filtered)


class YtdlpSearcher:
    def __init__(self, runner: YtdlpCommandRunner, limit: int = 5) -> None:
        self.runner = runner
        self.limit = max(1, limit)

    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        query = f"{artist} {title}".strip()
        args = [
            "yt-dlp",
            "--dump-json",
            "--no-playlist",
            "--flat-playlist",
            f"ytsearch{self.limit}:{query}",
        ]
        entries = self.runner.run_json_lines(args)
        candidates: list[DownloadCandidate] = []

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            item_title = str(entry.get("title") or query)
            video_id = str(entry.get("id") or "")
            uri = str(
                entry.get("webpage_url")
                or (f"https://www.youtube.com/watch?v={video_id}" if video_id else query)
            )
            duration_sec = int(entry.get("duration") or 0)
            duration_ms = max(0, duration_sec) * 1000
            abr = int(entry.get("abr") or 0)
            candidates.append(
                _build_candidate(
                    source="youtube",
                    title=item_title,
                    bitrate_kbps=abr,
                    duration_ms=duration_ms,
                    uri=uri,
                    score=1.0,
                )
            )
        return candidates
