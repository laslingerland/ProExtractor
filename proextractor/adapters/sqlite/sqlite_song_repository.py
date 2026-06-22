from importlib.resources import files
from pathlib import Path
import sqlite3

from proextractor.domain.models import Arrangement, ArrangementSlideRef, Section, Slide, Song, SongSearchResult, SongSummary


class SQLiteSongRepository:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        schema = files("proextractor.adapters.sqlite").joinpath("schema.sql").read_text(encoding="utf-8")
        with self._connect() as connection:
            connection.executescript(schema)

    def save_song(self, song: Song) -> int:
        with self._connect() as connection:
            existing = connection.execute("SELECT id FROM songs WHERE source_id = ?", (song.source_id,)).fetchone()
            existing_id = int(existing["id"]) if existing else None
            title = self._unique_title(connection, song.title, existing_id)
            if existing:
                song_id = existing_id
                assert song_id is not None
                connection.execute("UPDATE songs SET title = ? WHERE id = ?", (title, song_id))
                connection.execute("DELETE FROM sections WHERE song_id = ?", (song_id,))
                connection.execute("DELETE FROM slides WHERE song_id = ?", (song_id,))
                connection.execute("DELETE FROM arrangements WHERE song_id = ?", (song_id,))
            else:
                cursor = connection.execute("INSERT INTO songs(title, source_id) VALUES (?, ?)", (title, song.source_id))
                song_id = int(cursor.lastrowid)
            connection.executemany("INSERT INTO sections(song_id, uuid, name, sequence) VALUES (?, ?, ?, ?)", [(song_id, item.uuid, item.name, index) for index, item in enumerate(song.sections)])
            connection.executemany("INSERT INTO slides(song_id, uuid, section_uuid, sung_text, translation, physical_sequence) VALUES (?, ?, ?, ?, ?, ?)", [(song_id, item.uuid, item.section_uuid, item.sung_text, item.translation, index) for index, item in enumerate(song.slides)])
            for arrangement_index, arrangement in enumerate(song.arrangements):
                cursor = connection.execute("INSERT INTO arrangements(song_id, name, is_default, sequence) VALUES (?, ?, ?, ?)", (song_id, arrangement.name, int(arrangement.is_default), arrangement_index))
                arrangement_id = int(cursor.lastrowid)
                connection.executemany("INSERT INTO arrangement_slides(arrangement_id, slide_uuid, sequence) VALUES (?, ?, ?)", [(arrangement_id, ref.slide_uuid, ref.sequence) for ref in arrangement.slide_refs])
            return song_id

    @staticmethod
    def _unique_title(connection: sqlite3.Connection, requested: str, existing_id: int | None) -> str:
        title = requested.strip() or "Untitled"
        suffix = 0
        while True:
            candidate = title if suffix == 0 else f"{title} ({suffix})"
            if existing_id is None:
                row = connection.execute(
                    "SELECT 1 FROM songs WHERE title = ? COLLATE NOCASE",
                    (candidate,),
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT 1 FROM songs WHERE title = ? COLLATE NOCASE AND id != ?",
                    (candidate, existing_id),
                ).fetchone()
            if row is None:
                return candidate
            suffix += 1

    def list_songs(self) -> list[SongSummary]:
        with self._connect() as connection:
            rows = connection.execute("SELECT id, title, source_id FROM songs ORDER BY title COLLATE NOCASE").fetchall()
        return [SongSummary(int(row["id"]), str(row["title"]), str(row["source_id"])) for row in rows]

    def search(self, query: str) -> list[SongSearchResult]:
        pattern = f"%{query}%"
        sql = """SELECT s.id, s.title, s.source_id,
                 MAX(CASE WHEN sl.sung_text LIKE ? THEN sl.sung_text WHEN sl.translation LIKE ? THEN sl.translation ELSE '' END) snippet
                 FROM songs s LEFT JOIN slides sl ON sl.song_id=s.id
                 WHERE s.title LIKE ? OR sl.sung_text LIKE ? OR sl.translation LIKE ?
                 GROUP BY s.id, s.title, s.source_id
                 ORDER BY s.title COLLATE NOCASE"""
        with self._connect() as connection:
            rows = connection.execute(sql, (pattern, pattern, pattern, pattern, pattern)).fetchall()
        return [SongSearchResult(int(row["id"]), str(row["title"]), str(row["source_id"]), str(row["snippet"])) for row in rows]

    def get_song(self, identifier: str | int) -> Song:
        with self._connect() as connection:
            if isinstance(identifier, int) or str(identifier).isdigit():
                row = connection.execute("SELECT * FROM songs WHERE id = ?", (int(identifier),)).fetchone()
            else:
                row = connection.execute("SELECT * FROM songs WHERE title = ? COLLATE NOCASE", (str(identifier),)).fetchone()
            if row is None:
                raise LookupError(f"Song not found: {identifier}")
            song_id = int(row["id"])
            section_rows = connection.execute("SELECT * FROM sections WHERE song_id=? ORDER BY sequence", (song_id,)).fetchall()
            slide_rows = connection.execute("SELECT * FROM slides WHERE song_id=? ORDER BY physical_sequence", (song_id,)).fetchall()
            arrangement_rows = connection.execute("SELECT * FROM arrangements WHERE song_id=? ORDER BY sequence", (song_id,)).fetchall()
            arrangements: list[Arrangement] = []
            for arrangement_row in arrangement_rows:
                refs = connection.execute("SELECT * FROM arrangement_slides WHERE arrangement_id=? ORDER BY sequence", (arrangement_row["id"],)).fetchall()
                arrangements.append(Arrangement(int(arrangement_row["id"]), str(arrangement_row["name"]), [ArrangementSlideRef(str(ref["slide_uuid"]), int(ref["sequence"])) for ref in refs], bool(arrangement_row["is_default"])))
        return Song(song_id, str(row["title"]), str(row["source_id"]), [Section(int(item["id"]), str(item["uuid"]), str(item["name"])) for item in section_rows], [Slide(int(item["id"]), str(item["uuid"]), str(item["section_uuid"]) if item["section_uuid"] else None, str(item["sung_text"]), str(item["translation"])) for item in slide_rows], arrangements)
