from proextractor.application.ports.song_repository import SongRepository
from proextractor.domain.models import SongSummary


class ListSongsUseCase:
    def __init__(self, repository: SongRepository) -> None:
        self._repository = repository

    def execute(self) -> list[SongSummary]:
        return self._repository.list_songs()

