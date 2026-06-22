from proextractor.adapters.sqlite import SQLiteSongRepository
from proextractor.cli.cli import DEFAULT_SQLITE_PATH, build_parser, main
from proextractor.domain.models import Arrangement, ArrangementSlideRef, Section, Slide, Song


def test_database_commands_default_to_project_data_directory() -> None:
    arguments = build_parser().parse_args(["list"])
    assert arguments.sqlite == DEFAULT_SQLITE_PATH
    assert arguments.sqlite.name == "songs.sqlite"
    assert arguments.sqlite.parent.name == "data"


def test_top_level_help_explains_commands_database_and_export(capsys) -> None:
    parser = build_parser()
    try:
        parser.parse_args(["--help"])
    except SystemExit as error:
        assert error.code == 0
    help_text = capsys.readouterr().out
    assert "default database:" in help_text
    assert "export IDENTIFIER" in help_text
    assert "--output song.txt" in help_text
    assert "--all --format txt --output-dir" in help_text


def test_native_single_and_bulk_file_export(tmp_path) -> None:
    database = tmp_path / "songs.sqlite"
    repository = SQLiteSongRepository(database)
    identifier = repository.save_song(Song(
        None,
        "Example/Song",
        "source",
        [Section(None, "verse", "Verse")],
        [Slide(None, "slide", "verse", "Hello", "Hallo")],
        [Arrangement(None, "Default", [ArrangementSlideRef("slide", 0)], True)],
    ))

    output_file = tmp_path / "one" / "song.txt"
    assert main(["export", str(identifier), "--sqlite", str(database), "--output", str(output_file)]) == 0
    assert output_file.read_text(encoding="utf-8") == "[Verse]\n\nHello\nHallo\n"

    output_directory = tmp_path / "all"
    assert main(["export", "--all", "--sqlite", str(database), "--format", "json", "--output-dir", str(output_directory)]) == 0
    exported_files = list(output_directory.glob("*.json"))
    assert len(exported_files) == 1
    assert exported_files[0].name == f"{identifier} - Example_Song.json"
