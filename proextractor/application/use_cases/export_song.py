from proextractor.application.ports.song_exporter import SongExporter
from proextractor.application.ports.song_repository import SongRepository


class ExportSongUseCase:
    def __init__(self, repository: SongRepository, exporter: SongExporter) -> None:
        self._repository = repository
        self._exporter = exporter

    def execute(self, identifier: str | int) -> str:
        return self._exporter.export(self._repository.get_song(identifier))

