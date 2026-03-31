import logging
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get(
    "FASHION_AI_DB",
    os.path.join(os.path.dirname(__file__), "fashion_ai.db"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    original_filename TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    garment_type TEXT,
    style TEXT,
    material TEXT,
    color_palette TEXT,
    pattern TEXT,
    season TEXT,
    occasion TEXT,
    consumer_profile TEXT,
    trend_notes TEXT,
    location_continent TEXT,
    location_country TEXT,
    location_city TEXT,
    designer TEXT,
    image_year INTEGER,
    image_month INTEGER,
    status TEXT DEFAULT 'pending',
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    tag TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS images_fts USING fts5(
    image_id,
    description,
    garment_type,
    style,
    material,
    trend_notes,
    annotation_text
);
"""


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")


def _migrate(conn: sqlite3.Connection) -> None:
    """Handle schema changes for existing databases."""
    cursor = conn.execute("PRAGMA table_info(images)")
    columns = {row[1] for row in cursor.fetchall()}
    if "error_message" not in columns:
        conn.execute("ALTER TABLE images ADD COLUMN error_message TEXT")
        conn.commit()
        logger.info("Migrated: added error_message column")


def init_db(db_path: str | None = None) -> None:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    try:
        _apply_pragmas(conn)
        conn.executescript(SCHEMA)
        conn.commit()
        _migrate(conn)
    finally:
        conn.close()


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


@contextmanager
def get_db(db_path: str | None = None) -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
