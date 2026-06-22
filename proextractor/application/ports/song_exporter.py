from typing import Protocol

from proextractor.domain.models import Song


class SongExporter(Protocol):
    def export(self, song: Song) -> str: ...

