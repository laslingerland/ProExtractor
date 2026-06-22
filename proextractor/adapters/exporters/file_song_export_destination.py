from pathlib import Path
import re

from proextractor.domain.models import Song


class FileSongExportDestination:
    """Write a single export to an exact file path."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def write(self, song: Song, content: str) -> str:
        del song
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(content, encoding="utf-8", newline="")
        return str(self._path.resolve())


class DirectorySongExportDestination:
    """Write each song to a deterministic, filesystem-safe filename."""

    def __init__(self, directory: Path, extension: str) -> None:
        self._directory = directory
        self._extension = extension.lstrip(".")

    def write(self, song: Song, content: str) -> str:
        self._directory.mkdir(parents=True, exist_ok=True)
        safe_title = re.sub(r"[^\w .()-]+", "_", song.title, flags=re.UNICODE).strip(" .") or "song"
        prefix = f"{song.id} - " if song.id is not None else ""
        path = self._directory / f"{prefix}{safe_title}.{self._extension}"
        path.write_text(content, encoding="utf-8", newline="")
        return str(path.resolve())

