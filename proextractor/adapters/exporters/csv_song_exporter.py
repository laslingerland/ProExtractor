import csv
import io

from proextractor.domain.models import Song


class CsvSongExporter:
    def export(self, song: Song) -> str:
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow([f"Song title: {song.title}"])
        writer.writerow([])
        writer.writerow(["section", "slide_index", "sung_text", "translation"])
        names = {section.uuid: section.name for section in song.sections}
        for index, slide in enumerate(song.arranged_slides()):
            writer.writerow([names.get(slide.section_uuid or "", ""), index, slide.sung_text, slide.translation])
        return stream.getvalue()
