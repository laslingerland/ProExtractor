from pathlib import Path

from proextractor.application.ports.song_importer import SourceInspector


class InspectSourceUseCase:
    def __init__(self, inspector: SourceInspector) -> None:
        self._inspector = inspector

    def execute(self, path: Path, debug: bool = False) -> str:
        return self._inspector.inspect(path).render(debug)

