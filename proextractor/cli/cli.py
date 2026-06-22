import argparse
from pathlib import Path
import sys

from proextractor import __version__
from proextractor.adapters.exporters import CsvSongExporter, DirectorySongExportDestination, FileSongExportDestination, JsonSongExporter, TextSongExporter
from proextractor.adapters.propresenter import ProFileInspector, ProPresenterLegacyProImporter
from proextractor.adapters.sqlite import SQLiteSongRepository
from proextractor.application.use_cases import ExportAllSongsUseCase, ExportSongToDestinationUseCase, ExportSongUseCase, ImportSongsUseCase, InspectSourceUseCase, ListSongsUseCase, SearchSongsUseCase


DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[2] / "data" / "songs.sqlite"
DATABASE_HELP = f"SQLite database path (default: {DEFAULT_SQLITE_PATH})"
HELP_FORMATTER = argparse.RawDescriptionHelpFormatter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proextractor",
        description="Import ProPresenter .pro songs into SQLite and export their default arrangements.",
        epilog=f"""commands:
  import SOURCE       Import recognized song .pro files from a file or directory.
  list                List songs currently stored in SQLite.
  search QUERY        Search song titles, sung lyrics, and translations.
  export IDENTIFIER   Export one stored song as txt, csv, or json.
  export --all        Export every stored song to a directory.
  inspect SOURCE      Diagnose a .pro file without changing the database.

default database:
  {DEFAULT_SQLITE_PATH}

examples:
  proextractor import song.pro
  proextractor import ./library
  proextractor list
  proextractor search "worthy"
  proextractor export 1 --format txt
  proextractor export 1 --format txt --output song.txt
  proextractor export --all --format txt --output-dir ./exports
  proextractor export "No One Like The Lord" --format json > song.json
  proextractor inspect song.pro --debug

Run 'proextractor COMMAND --help' for detailed command help.
The --sqlite option can override the default database for import, list, search,
and export. A single export writes to standard output unless --output is used.""",
        formatter_class=HELP_FORMATTER,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    import_parser = subparsers.add_parser(
        "import",
        help="import .pro songs into SQLite",
        description="Import a ProPresenter song .pro file, or recursively import recognized songs from a directory. Files without recognizable song sections are skipped. Existing songs with the same source ID are replaced.",
        epilog="examples:\n  proextractor import song.pro\n  proextractor import ./library\n  proextractor import song.pro --sqlite ./other.sqlite",
        formatter_class=HELP_FORMATTER,
    )
    import_parser.add_argument("source", type=Path, metavar="SOURCE", help=".pro file or directory to import")
    import_parser.add_argument("--sqlite", type=Path, default=DEFAULT_SQLITE_PATH, metavar="PATH", help=DATABASE_HELP)
    list_parser = subparsers.add_parser(
        "list",
        help="list imported songs",
        description="List each stored song's numeric ID and title. The ID can be passed to the export command.",
        epilog="example:\n  proextractor list",
        formatter_class=HELP_FORMATTER,
    )
    list_parser.add_argument("--sqlite", type=Path, default=DEFAULT_SQLITE_PATH, metavar="PATH", help=DATABASE_HELP)
    search_parser = subparsers.add_parser(
        "search",
        help="search titles, lyrics, and translations",
        description="Search stored song titles, sung lyrics, and translations. Results show the song ID, title, and a matching lyric when available.",
        epilog='examples:\n  proextractor search "worthy"\n  proextractor search "Waardig is het Lam"',
        formatter_class=HELP_FORMATTER,
    )
    search_parser.add_argument("query", metavar="QUERY", help="case-insensitive text to find")
    search_parser.add_argument("--sqlite", type=Path, default=DEFAULT_SQLITE_PATH, metavar="PATH", help=DATABASE_HELP)
    export_parser = subparsers.add_parser(
        "export",
        help="export a song from SQLite",
        description="Export one song by numeric ID or exact title, or export every song with --all. A single export uses standard output unless --output is provided. --all requires --output-dir.",
        epilog='examples:\n  proextractor export 1 --format txt\n  proextractor export 1 --format csv --output song.csv\n  proextractor export "No One Like The Lord" --format json --output song.json\n  proextractor export --all --format txt --output-dir ./exports',
        formatter_class=HELP_FORMATTER,
    )
    export_parser.add_argument("identifier", nargs="?", metavar="IDENTIFIER", help="numeric song ID or exact song title")
    export_parser.add_argument("--all", dest="export_all", action="store_true", help="export every song in the database")
    export_parser.add_argument("--sqlite", type=Path, default=DEFAULT_SQLITE_PATH, metavar="PATH", help=DATABASE_HELP)
    export_parser.add_argument("--format", choices=("txt", "csv", "json"), default="txt", help="output format (default: txt)")
    export_parser.add_argument("-o", "--output", type=Path, metavar="FILE", help="write one song to FILE instead of standard output")
    export_parser.add_argument("--output-dir", type=Path, metavar="DIR", help="directory for --all; one file is created per song")
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="inspect binary structure and parser inference",
        description="Inspect one .pro file without importing it or changing SQLite. Reports recovered sections, slides, arrangements, text, and confidence scores.",
        epilog="examples:\n  proextractor inspect song.pro\n  proextractor inspect song.pro --debug",
        formatter_class=HELP_FORMATTER,
    )
    inspect_parser.add_argument("source", type=Path, metavar="SOURCE", help=".pro file to inspect")
    inspect_parser.add_argument("--debug", action="store_true", help="show offsets, all strings and UUIDs, mappings, unmatched blocks, and fallback decisions")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "inspect":
            print(InspectSourceUseCase(ProFileInspector()).execute(arguments.source, arguments.debug))
            return 0
        repository = SQLiteSongRepository(arguments.sqlite)
        if arguments.command == "import":
            identifiers = ImportSongsUseCase(ProPresenterLegacyProImporter(), repository).execute(arguments.source)
            print(f"Imported {len(identifiers)} song(s): {', '.join(map(str, identifiers))}")
        elif arguments.command == "list":
            for song in ListSongsUseCase(repository).execute():
                print(f"{song.id}\t{song.title}")
        elif arguments.command == "search":
            for song in SearchSongsUseCase(repository).execute(arguments.query):
                suffix = f"\t{song.snippet}" if song.snippet else ""
                print(f"{song.id}\t{song.title}{suffix}")
        elif arguments.command == "export":
            exporters = {"txt": TextSongExporter(), "csv": CsvSongExporter(), "json": JsonSongExporter()}
            exporter = exporters[arguments.format]
            if arguments.export_all:
                if arguments.identifier is not None:
                    parser.error("export: IDENTIFIER cannot be combined with --all")
                if arguments.output is not None:
                    parser.error("export: --output cannot be combined with --all; use --output-dir")
                if arguments.output_dir is None:
                    parser.error("export: --all requires --output-dir DIR")
                destination = DirectorySongExportDestination(arguments.output_dir, arguments.format)
                paths = ExportAllSongsUseCase(repository, exporter, destination).execute()
                print(f"Exported {len(paths)} song(s) to {arguments.output_dir.resolve()}")
            else:
                if arguments.identifier is None:
                    parser.error("export: provide IDENTIFIER or use --all")
                if arguments.output_dir is not None:
                    parser.error("export: --output-dir requires --all")
                if arguments.output is not None:
                    destination = FileSongExportDestination(arguments.output)
                    path = ExportSongToDestinationUseCase(repository, exporter, destination).execute(arguments.identifier)
                    print(f"Exported to {path}")
                else:
                    output = ExportSongUseCase(repository, exporter).execute(arguments.identifier)
                    sys.stdout.write(output)
        return 0
    except (FileNotFoundError, IsADirectoryError, LookupError, OSError) as error:
        print(f"proextractor: {error}", file=sys.stderr)
        return 1
