import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    artist TEXT NOT NULL,
                    title TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def is_track_downloaded(self, track_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM tracks WHERE track_id = ? LIMIT 1",
                (track_id,),
            ).fetchone()
        return row is not None

    def mark_track_downloaded(
        self,
        track_id: str,
        artist: str,
        title: str,
        file_path: str,
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tracks (track_id, artist, title, file_path)
                VALUES (?, ?, ?, ?)
                """,
                (track_id, artist, title, file_path),
            )
            conn.commit()
