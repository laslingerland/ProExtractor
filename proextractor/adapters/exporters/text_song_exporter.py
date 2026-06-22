from proextractor.domain.models import Song


class TextSongExporter:
    def export(self, song: Song) -> str:
        section_names = {section.uuid: section.name for section in song.sections}
        output: list[str] = []
        previous_section: str | None = None
        for slide in song.arranged_slides():
            if slide.section_uuid != previous_section:
                output.append(f"[{section_names.get(slide.section_uuid or '', 'Unsectioned')}]")
                previous_section = slide.section_uuid
            texts = [value for value in (slide.sung_text, slide.translation) if value]
            if texts:
                output.append("\n".join(texts))
        return "\n\n".join(output) + "\n"

