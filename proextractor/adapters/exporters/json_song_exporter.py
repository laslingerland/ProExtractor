import json

from proextractor.domain.models import Song


class JsonSongExporter:
    def export(self, song: Song) -> str:
        value = {
            "song": {"title": song.title, "id": song.id, "source_id": song.source_id},
            "sections": [{"id": item.id, "uuid": item.uuid, "name": item.name} for item in song.sections],
            "slides": [{"id": item.id, "uuid": item.uuid, "section_uuid": item.section_uuid, "sung_text": item.sung_text, "translation": item.translation} for item in song.slides],
            "arrangements": [{"id": item.id, "name": item.name, "is_default": item.is_default, "slide_refs": [{"slide_uuid": ref.slide_uuid, "sequence": ref.sequence} for ref in item.slide_refs]} for item in song.arrangements],
        }
        return json.dumps(value, ensure_ascii=False, indent=2) + "\n"
