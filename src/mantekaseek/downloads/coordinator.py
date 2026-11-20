from mantekaseek.downloads.ranking import DownloadCandidate
from mantekaseek.downloads.slskd_client import SlskdClient
from mantekaseek.downloads.ytdlp_client import YtdlpSearcher


class SearchCoordinator:
    def __init__(
        self,
        slskd_client: SlskdClient,
        ytdlp_searcher: YtdlpSearcher,
    ) -> None:
        self.slskd_client = slskd_client
        self.ytdlp_searcher = ytdlp_searcher

    def search(self, artist: str, title: str) -> list[DownloadCandidate]:
        slskd_candidates = self.slskd_client.search(artist=artist, title=title)
        if slskd_candidates:
            return slskd_candidates
        return self.ytdlp_searcher.search(artist=artist, title=title)
