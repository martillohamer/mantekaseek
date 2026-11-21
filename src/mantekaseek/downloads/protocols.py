from typing import Any, Protocol, runtime_checkable

from mantekaseek.downloads.ranking import DownloadCandidate


@runtime_checkable
class JsonTransportProtocol(Protocol):
    def post_json(
        self, url: str, headers: dict[str, str], body: dict[str, Any]
    ) -> dict[str, Any]: ...


@runtime_checkable
class YtdlpRunnerProtocol(Protocol):
    def run_json_lines(self, args: list[str]) -> list[dict[str, Any]]: ...


@runtime_checkable
class CommandRunnerProtocol(Protocol):
    def run(self, args: list[str]) -> int: ...


@runtime_checkable
class CandidateSearcherProtocol(Protocol):
    def search(self, artist: str, title: str) -> list[DownloadCandidate]: ...


@runtime_checkable
class FallbackSearcherProtocol(Protocol):
    def search_fallback(self, artist: str, title: str) -> DownloadCandidate | None: ...
