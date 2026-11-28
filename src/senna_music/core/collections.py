from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from senna_music.core.storage import connect


def _name(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("A name is required.")
    return value


def _create(table: str, name: str, path: str | Path | None) -> bool:
    with closing(connect(path)) as db, db:
        try:
            db.execute(f"INSERT INTO {table}(name) VALUES(?)", (_name(name),))
        except sqlite3.IntegrityError:
            return False
    return True


def _rename(table: str, item_id: int, name: str, path: str | Path | None) -> bool:
    with closing(connect(path)) as db, db:
        try:
            cursor = db.execute(
                f"UPDATE {table} SET name = ? WHERE id = ?", (_name(name), item_id)
            )
        except sqlite3.IntegrityError:
            return False
        return cursor.rowcount == 1


def _delete(table: str, item_id: int, path: str | Path | None) -> None:
    with closing(connect(path)) as db, db:
        db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))


def _named_items(table: str, links: str, owner: str, path: str | Path | None):
    with closing(connect(path)) as db:
        rows = db.execute(
            f"SELECT c.id, c.name, COUNT(l.track_path) AS track_count "
            f"FROM {table} c LEFT JOIN {links} l ON l.{owner} = c.id "
            "GROUP BY c.id, c.name ORDER BY c.name COLLATE NOCASE"
        ).fetchall()
    return [dict(row) for row in rows]


def _add_links(
    table: str, owner: str, item_id: int, paths: list[str], path: str | Path | None
) -> int:
    with closing(connect(path)) as db, db:
        row = db.execute(
            f"SELECT COALESCE(MAX(position), -1) AS last FROM {table} WHERE {owner} = ?",
            (item_id,),
        ).fetchone()
        position = int(row["last"]) + 1
        added = 0
        for track_path in paths:
            cursor = db.execute(
                f"INSERT OR IGNORE INTO {table}({owner}, track_path, position) VALUES(?, ?, ?)",
                (item_id, track_path, position),
            )
            if cursor.rowcount:
                position += 1
                added += 1
        return added


def _remove_link(
    table: str, owner: str, item_id: int, track_path: str, path: str | Path | None
) -> None:
    with closing(connect(path)) as db, db:
        db.execute(
            f"DELETE FROM {table} WHERE {owner} = ? AND track_path = ?",
            (item_id, track_path),
        )


def _linked_tracks(
    table: str, owner: str, item_id: int, path: str | Path | None
) -> list[dict[str, Any]]:
    with closing(connect(path)) as db:
        rows = db.execute(
            f"SELECT tracks.*, links.position FROM {table} links "
            "JOIN tracks ON tracks.path = links.track_path "
            f"WHERE links.{owner} = ? ORDER BY links.position",
            (item_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def _reorder(
    table: str, owner: str, item_id: int, paths: list[str], path: str | Path | None
) -> None:
    with closing(connect(path)) as db, db:
        current = {
            row["track_path"] for row in db.execute(
                f"SELECT track_path FROM {table} WHERE {owner} = ?", (item_id,)
            ).fetchall()
        }
        if len(paths) != len(current) or set(paths) != current:
            raise ValueError("Reordering must include every track exactly once.")
        db.executemany(
            f"UPDATE {table} SET position = ? WHERE {owner} = ? AND track_path = ?",
            [(index, item_id, track_path) for index, track_path in enumerate(paths)],
        )


def list_playlists(path: str | Path | None = None):
    return _named_items("playlists", "playlist_tracks", "playlist_id", path)


def create_playlist(name: str, path: str | Path | None = None) -> bool:
    return _create("playlists", name, path)


def rename_playlist(item_id: int, name: str, path: str | Path | None = None) -> bool:
    return _rename("playlists", item_id, name, path)


def delete_playlist(item_id: int, path: str | Path | None = None) -> None:
    _delete("playlists", item_id, path)


def add_tracks_to_playlist(item_id: int, paths: list[str], path: str | Path | None = None):
    return _add_links("playlist_tracks", "playlist_id", item_id, paths, path)


def remove_track_from_playlist(item_id: int, track_path: str, path: str | Path | None = None):
    _remove_link("playlist_tracks", "playlist_id", item_id, track_path, path)


def list_playlist_tracks(item_id: int, path: str | Path | None = None):
    return _linked_tracks("playlist_tracks", "playlist_id", item_id, path)


def reorder_playlist_tracks(item_id: int, paths: list[str], path: str | Path | None = None):
    _reorder("playlist_tracks", "playlist_id", item_id, paths, path)


def list_favorites(path: str | Path | None = None):
    with closing(connect(path)) as db:
        rows = db.execute(
            "SELECT tracks.*, favorites.position FROM favorites "
            "JOIN tracks ON tracks.path = favorites.track_path ORDER BY favorites.position"
        ).fetchall()
    return [dict(row) for row in rows]


def add_favorites(paths: list[str], path: str | Path | None = None) -> int:
    with closing(connect(path)) as db, db:
        row = db.execute("SELECT COALESCE(MAX(position), -1) AS last FROM favorites").fetchone()
        position = int(row["last"]) + 1
        added = 0
        for track_path in paths:
            cursor = db.execute(
                "INSERT OR IGNORE INTO favorites(track_path, position) VALUES(?, ?)",
                (track_path, position),
            )
            if cursor.rowcount:
                added += 1
                position += 1
        return added


def remove_favorite(track_path: str, path: str | Path | None = None) -> None:
    with closing(connect(path)) as db, db:
        db.execute("DELETE FROM favorites WHERE track_path = ?", (track_path,))


def reorder_favorites(paths: list[str], path: str | Path | None = None) -> None:
    with closing(connect(path)) as db, db:
        current = {row["track_path"] for row in db.execute(
            "SELECT track_path FROM favorites"
        ).fetchall()}
        if len(paths) != len(current) or set(paths) != current:
            raise ValueError("Reordering must include every favorite exactly once.")
        db.executemany(
            "UPDATE favorites SET position = ? WHERE track_path = ?",
            [(index, track_path) for index, track_path in enumerate(paths)],
        )


def list_favorite_collections(path: str | Path | None = None):
    return _named_items(
        "favorite_collections", "favorite_collection_tracks", "collection_id", path
    )


def create_favorite_collection(name: str, path: str | Path | None = None) -> bool:
    return _create("favorite_collections", name, path)


def rename_favorite_collection(item_id: int, name: str, path: str | Path | None = None):
    return _rename("favorite_collections", item_id, name, path)


def delete_favorite_collection(item_id: int, path: str | Path | None = None):
    _delete("favorite_collections", item_id, path)


def add_tracks_to_favorite_collection(
    item_id: int, paths: list[str], path: str | Path | None = None
):
    return _add_links("favorite_collection_tracks", "collection_id", item_id, paths, path)


def remove_track_from_favorite_collection(
    item_id: int, track_path: str, path: str | Path | None = None
):
    _remove_link("favorite_collection_tracks", "collection_id", item_id, track_path, path)


def list_favorite_collection_tracks(item_id: int, path: str | Path | None = None):
    return _linked_tracks("favorite_collection_tracks", "collection_id", item_id, path)


def reorder_favorite_collection_tracks(
    item_id: int, paths: list[str], path: str | Path | None = None
):
    _reorder("favorite_collection_tracks", "collection_id", item_id, paths, path)
