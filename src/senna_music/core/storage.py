from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from platformdirs import user_data_path


def database_path() -> Path:
    """Return the per-user SQLite database path."""
    folder = user_data_path("Senna Music", "Admir", ensure_exists=True)
    return folder / "senna_music.sqlite3"


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    db_path = Path(path) if path is not None else database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def initialize_database(path: str | Path | None = None) -> None:
    with closing(connect(path)) as connection:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS library_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tracks (
                path TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT NOT NULL DEFAULT '',
                album TEXT NOT NULL DEFAULT '',
                track_number TEXT NOT NULL DEFAULT '',
                year TEXT NOT NULL DEFAULT '',
                genre TEXT NOT NULL DEFAULT '',
                duration REAL,
                file_format TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                modified_ns INTEGER NOT NULL,
                scan_error TEXT NOT NULL DEFAULT '',
                scanned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS playlist_tracks (
                playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
                track_path TEXT NOT NULL REFERENCES tracks(path) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                PRIMARY KEY (playlist_id, track_path)
            );
            CREATE TABLE IF NOT EXISTS favorites (
                track_path TEXT PRIMARY KEY REFERENCES tracks(path) ON DELETE CASCADE,
                position INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS favorite_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS favorite_collection_tracks (
                collection_id INTEGER NOT NULL REFERENCES favorite_collections(id) ON DELETE CASCADE,
                track_path TEXT NOT NULL REFERENCES tracks(path) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                PRIMARY KEY (collection_id, track_path)
            );
            CREATE TABLE IF NOT EXISTS download_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_url TEXT NOT NULL,
                download_url TEXT NOT NULL,
                destination_root TEXT NOT NULL,
                title TEXT NOT NULL,
                artist TEXT NOT NULL DEFAULT '',
                album TEXT NOT NULL DEFAULT '',
                requested_format TEXT NOT NULL DEFAULT 'original',
                quality TEXT NOT NULL DEFAULT '192',
                status TEXT NOT NULL DEFAULT 'queued',
                progress REAL NOT NULL DEFAULT 0,
                destination_path TEXT NOT NULL DEFAULT '',
                error TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(download_queue)")
        }
        if "destination_root" not in columns:
            connection.execute(
                "ALTER TABLE download_queue ADD COLUMN destination_root TEXT NOT NULL DEFAULT ''"
            )
        connection.execute(
            "UPDATE download_queue SET status = 'queued', progress = 0 "
            "WHERE status IN ('downloading', 'paused')"
        )
        connection.commit()


def add_download_task(task: dict[str, Any], path: str | Path | None = None) -> int:
    with closing(connect(path)) as connection, connection:
        cursor = connection.execute(
            """
            INSERT INTO download_queue (
                source, source_url, download_url, destination_root, title, artist, album,
                requested_format, quality, status, progress
            ) VALUES (
                :source, :source_url, :download_url, :destination_root, :title, :artist, :album,
                :requested_format, :quality, 'queued', 0
            )
            """,
            task,
        )
        return int(cursor.lastrowid)


def list_download_tasks(path: str | Path | None = None) -> list[dict[str, Any]]:
    with closing(connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM download_queue ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_next_download_task(path: str | Path | None = None) -> dict[str, Any] | None:
    with closing(connect(path)) as connection:
        row = connection.execute(
            "SELECT * FROM download_queue WHERE status = 'queued' ORDER BY id LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def update_download_task(
    task_id: int, path: str | Path | None = None, **updates: Any
) -> None:
    allowed = {
        "status", "progress", "destination_path", "error", "requested_format", "quality"
    }
    unknown = set(updates) - allowed
    if unknown:
        raise ValueError(f"Unsupported download fields: {', '.join(sorted(unknown))}")
    if not updates:
        return
    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = [*updates.values(), task_id]
    with closing(connect(path)) as connection, connection:
        connection.execute(
            f"UPDATE download_queue SET {assignments}, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            values,
        )


def retry_download_task(task_id: int, path: str | Path | None = None) -> None:
    update_download_task(
        task_id, path, status="queued", progress=0, error="", destination_path=""
    )


def delete_download_task(task_id: int, path: str | Path | None = None) -> None:
    with closing(connect(path)) as connection, connection:
        connection.execute("DELETE FROM download_queue WHERE id = ?", (task_id,))


def clear_finished_download_tasks(path: str | Path | None = None) -> None:
    with closing(connect(path)) as connection, connection:
        connection.execute(
            "DELETE FROM download_queue WHERE status IN ('completed', 'skipped', 'cancelled')"
        )


def get_setting(key: str, default: str = "", path: str | Path | None = None) -> str:
    with closing(connect(path)) as connection:
        row = connection.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
    return str(row["value"]) if row else default


def set_setting(key: str, value: str, path: str | Path | None = None) -> None:
    with closing(connect(path)) as connection, connection:
        connection.execute(
            """
            INSERT INTO settings(key, value) VALUES(?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )


def add_library_folder(folder: str | Path, path: str | Path | None = None) -> bool:
    normalized = str(Path(folder).expanduser().resolve())
    with closing(connect(path)) as connection, connection:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO library_folders(path) VALUES(?)", (normalized,)
        )
        return cursor.rowcount == 1


def list_library_folders(path: str | Path | None = None) -> list[str]:
    with closing(connect(path)) as connection:
        rows = connection.execute(
            "SELECT path FROM library_folders ORDER BY path COLLATE NOCASE"
        ).fetchall()
    return [str(row["path"]) for row in rows]


def _is_within(candidate: Path, root: Path) -> bool:
    resolved_candidate = candidate.resolve()
    resolved_root = root.resolve()
    return resolved_candidate == resolved_root or resolved_root in resolved_candidate.parents


def remove_library_folder(folder: str, path: str | Path | None = None) -> None:
    root = Path(folder).expanduser().resolve()
    with closing(connect(path)) as connection, connection:
        connection.execute("DELETE FROM library_folders WHERE path = ?", (str(root),))
        rows = connection.execute("SELECT path FROM tracks").fetchall()
        stale = [
            str(row["path"])
            for row in rows
            if _is_within(Path(str(row["path"])), root)
        ]
        connection.executemany("DELETE FROM tracks WHERE path = ?", [(item,) for item in stale])


def save_track(track: dict[str, Any], path: str | Path | None = None) -> None:
    with closing(connect(path)) as connection, connection:
        connection.execute(
            """
            INSERT INTO tracks (
                path, title, artist, album, track_number, year, genre,
                duration, file_format, file_size, modified_ns, scan_error, scanned_at
            ) VALUES (
                :path, :title, :artist, :album, :track_number, :year, :genre,
                :duration, :file_format, :file_size, :modified_ns, :scan_error,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(path) DO UPDATE SET
                title=excluded.title, artist=excluded.artist, album=excluded.album,
                track_number=excluded.track_number, year=excluded.year,
                genre=excluded.genre, duration=excluded.duration,
                file_format=excluded.file_format, file_size=excluded.file_size,
                modified_ns=excluded.modified_ns, scan_error=excluded.scan_error,
                scanned_at=CURRENT_TIMESTAMP
            """,
            track,
        )


def list_tracks(path: str | Path | None = None) -> list[dict[str, Any]]:
    with closing(connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM tracks ORDER BY title COLLATE NOCASE, artist COLLATE NOCASE"
        ).fetchall()
    return [dict(row) for row in rows]


def remove_missing_tracks(root: str | Path, found_paths: set[str],
                          path: str | Path | None = None) -> None:
    root_path = Path(root).resolve()
    with closing(connect(path)) as connection, connection:
        rows = connection.execute("SELECT path FROM tracks").fetchall()
        stale = []
        for row in rows:
            track_path = Path(str(row["path"])).resolve()
            if _is_within(track_path, root_path) and str(track_path) not in found_paths:
                stale.append(str(row["path"]))
        connection.executemany("DELETE FROM tracks WHERE path = ?", [(item,) for item in stale])
