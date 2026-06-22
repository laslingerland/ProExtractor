from proextractor.application.ports.song_repository import SongRepository
from proextractor.domain.models import SongSearchResult


class SearchSongsUseCase:
    def __init__(self, repository: SongRepository) -> None:
        self._repository = repository

    def execute(self, query: str) -> list[SongSearchResult]:
        return self._repository.search(query)

