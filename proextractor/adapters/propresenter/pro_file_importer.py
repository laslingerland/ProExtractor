from pathlib import Path

from proextractor.domain.models import Arrangement, ArrangementSlideRef, Section, Slide, Song
from .pro_file_inspector import ProFileInspector


class ProPresenterLegacyProImporter:
    def __init__(self, inspector: ProFileInspector | None = None) -> None:
        self._inspector = inspector or ProFileInspector()

    def import_from_path(self, path: Path) -> list[Song]:
        paths = sorted(path.rglob("*.pro")) if path.is_dir() else [path]
        songs: list[Song] = []
        for source in paths:
            result = self._inspector.inspect(source)
            if not result.sections:
                continue
            songs.append(Song(
                id=None,
                title=result.title,
                source_id=result.source_id,
                sections=[Section(None, item.uuid, item.name) for item in result.sections],
                slides=[Slide(None, item.uuid, item.section_uuid, item.sung_text, item.translation) for item in result.slides],
                arrangements=[Arrangement(None, item.name, [ArrangementSlideRef(uuid, index) for index, uuid in enumerate(item.slide_uuids)], item.is_default) for item in result.arrangements],
            ))
        return songs
