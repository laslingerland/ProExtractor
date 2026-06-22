from pathlib import Path
from typing import Protocol

from proextractor.domain.models import Song


class SourceInspection(Protocol):
    def render(self, debug: bool = False) -> str: ...


class SongImporter(Protocol):
    def import_from_path(self, path: Path) -> list[Song]: ...


class SourceInspector(Protocol):
    def inspect(self, path: Path) -> SourceInspection: ...

