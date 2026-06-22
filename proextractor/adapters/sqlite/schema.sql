PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    source_id TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    uuid TEXT NOT NULL,
    name TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    UNIQUE(song_id, uuid)
);
CREATE TABLE IF NOT EXISTS slides (
    id INTEGER PRIMARY KEY,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    uuid TEXT NOT NULL,
    section_uuid TEXT,
    sung_text TEXT NOT NULL,
    translation TEXT NOT NULL,
    physical_sequence INTEGER NOT NULL,
    UNIQUE(song_id, uuid)
);
CREATE TABLE IF NOT EXISTS arrangements (
    id INTEGER PRIMARY KEY,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    is_default INTEGER NOT NULL DEFAULT 0,
    sequence INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS arrangement_slides (
    arrangement_id INTEGER NOT NULL REFERENCES arrangements(id) ON DELETE CASCADE,
    slide_uuid TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    PRIMARY KEY(arrangement_id, sequence)
);
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
CREATE INDEX IF NOT EXISTS idx_slides_text ON slides(sung_text, translation);

