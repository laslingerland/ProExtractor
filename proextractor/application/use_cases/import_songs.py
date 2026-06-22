from pathlib import Path

from proextractor.application.ports.song_importer import SongImporter
from proextractor.application.ports.song_repository import SongRepository


class ImportSongsUseCase:
    def __init__(self, importer: SongImporter, repository: SongRepository) -> None:
        self._importer = importer
        self._repository = repository

    def execute(self, path: Path) -> list[int]:
        return [self._repository.save_song(song) for song in self._importer.import_from_path(path)]

