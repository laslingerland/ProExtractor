from proextractor.application.ports.song_export_destination import SongExportDestination
from proextractor.application.ports.song_exporter import SongExporter
from proextractor.application.ports.song_repository import SongRepository


class ExportSongToDestinationUseCase:
    def __init__(self, repository: SongRepository, exporter: SongExporter, destination: SongExportDestination) -> None:
        self._repository = repository
        self._exporter = exporter
        self._destination = destination

    def execute(self, identifier: str | int) -> str:
        song = self._repository.get_song(identifier)
        return self._destination.write(song, self._exporter.export(song))


class ExportAllSongsUseCase:
    def __init__(self, repository: SongRepository, exporter: SongExporter, destination: SongExportDestination) -> None:
        self._repository = repository
        self._exporter = exporter
        self._destination = destination

    def execute(self) -> list[str]:
        paths: list[str] = []
        for summary in self._repository.list_songs():
            song = self._repository.get_song(summary.id)
            paths.append(self._destination.write(song, self._exporter.export(song)))
        return paths

