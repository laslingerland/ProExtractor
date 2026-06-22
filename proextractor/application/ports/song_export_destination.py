from typing import Protocol

from proextractor.domain.models import Song


class SongExportDestination(Protocol):
    """Port for writing one rendered song to an external destination."""

    def write(self, song: Song, content: str) -> str: ...

