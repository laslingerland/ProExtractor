import json

from proextractor.adapters.exporters import CsvSongExporter, JsonSongExporter, TextSongExporter
from proextractor.adapters.propresenter.binary_string_scanner import LocatedString, LocatedUUID
from proextractor.adapters.propresenter.pro_file_inspector import ProFileInspector
from proextractor.adapters.sqlite import SQLiteSongRepository
from proextractor.domain.models import Arrangement, ArrangementSlideRef, Section, Slide, Song


def make_song() -> Song:
    return Song(None, "Example", "source-1", [Section(None, "verse", "Verse")], [Slide(None, "slide", "verse", "Hello", "Hallo")], [Arrangement(None, "Default", [ArrangementSlideRef("slide", 0)], True)])


def test_repository_round_trip_and_search(tmp_path) -> None:
    database = tmp_path / "nested" / "songs.sqlite"
    repository = SQLiteSongRepository(database)
    assert database.exists()
    identifier = repository.save_song(make_song())
    song = repository.get_song(identifier)
    assert song.title == "Example"
    assert song.arranged_slides()[0].translation == "Hallo"
    assert repository.search("Hallo")[0].id == identifier


def test_saving_same_source_id_updates_song_without_duplicate(tmp_path) -> None:
    repository = SQLiteSongRepository(tmp_path / "songs.sqlite")
    original_id = repository.save_song(make_song())
    updated = Song(
        None,
        "Example updated",
        "source-1",
        [Section(None, "chorus", "Chorus")],
        [Slide(None, "updated-slide", "chorus", "Updated", "Bijgewerkt")],
        [Arrangement(None, "Default", [ArrangementSlideRef("updated-slide", 0)], True)],
    )

    updated_id = repository.save_song(updated)

    assert updated_id == original_id
    assert len(repository.list_songs()) == 1
    stored = repository.get_song(original_id)
    assert stored.title == "Example updated"
    assert [slide.sung_text for slide in stored.slides] == ["Updated"]


def test_distinct_songs_with_same_title_receive_stable_suffixes(tmp_path) -> None:
    repository = SQLiteSongRepository(tmp_path / "songs.sqlite")
    first = make_song()
    second = Song(None, "Example", "source-2", [Section(None, "verse-2", "Verse")], [], [])
    third = Song(None, "example", "source-3", [Section(None, "verse-3", "Verse")], [], [])

    first_id = repository.save_song(first)
    second_id = repository.save_song(second)
    third_id = repository.save_song(third)

    assert repository.get_song(first_id).title == "Example"
    assert repository.get_song(second_id).title == "Example (1)"
    assert repository.get_song(third_id).title == "example (2)"
    assert repository.save_song(second) == second_id
    assert repository.get_song(second_id).title == "Example (1)"


def test_repeated_section_label_for_same_uuid_is_not_a_duplicate_section() -> None:
    section_uuid = "2FBF8F3C-A24C-4C93-A35B-C89FF0235C81"
    slide_uuid = "B98978B2-FF32-4B17-8379-9155A178D791"
    sections = ProFileInspector._sections(
        [LocatedString(100, "Verse 1"), LocatedString(109, "Verse 1")],
        [LocatedUUID(64, section_uuid), LocatedUUID(120, slide_uuid)],
    )

    assert [(section.uuid, section.name) for section in sections] == [(section_uuid, "Verse 1")]
    assert sections[0].slide_uuids == [slide_uuid]


def test_exporters() -> None:
    song = make_song()
    assert TextSongExporter().export(song) == "[Verse]\n\nHello\nHallo\n"
    assert CsvSongExporter().export(song).splitlines() == ["section,slide_index,sung_text,translation", "Verse,0,Hello,Hallo"]
    assert json.loads(JsonSongExporter().export(song))["arrangements"][0]["is_default"] is True
