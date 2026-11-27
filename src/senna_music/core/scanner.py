from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mutagen import File as MutagenFile

from senna_music.core.storage import (
    list_library_folders,
    remove_missing_tracks,
    save_track,
)

SUPPORTED_FORMATS = {".mp3", ".m4a", ".flac", ".wav", ".ogg"}


def _tag_value(tags: Any, key: str) -> str:
    if not tags:
        return ""
    value = tags.get(key)
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    return str(value)


def read_track_metadata(file_path: Path) -> dict[str, Any]:
    """Read common audio tags. Keep unreadable supported files visible with an error."""
    result: dict[str, Any] = {
        "title": file_path.stem,
        "artist": "",
        "album": "",
        "track_number": "",
        "year": "",
        "genre": "",
        "duration": None,
        "scan_error": "",
    }
    try:
        audio = MutagenFile(file_path, easy=True)
        if audio is None:
            result["scan_error"] = "Audio metadata could not be read."
            return result
        tags = audio.tags
        result.update(
            title=_tag_value(tags, "title") or file_path.stem,
            artist=_tag_value(tags, "artist"),
            album=_tag_value(tags, "album"),
            track_number=_tag_value(tags, "tracknumber"),
            year=_tag_value(tags, "date") or _tag_value(tags, "year"),
            genre=_tag_value(tags, "genre"),
            duration=float(audio.info.length) if audio.info and audio.info.length else None,
        )
    except Exception as error:  # damaged files must remain visible in the library
        result["scan_error"] = f"{type(error).__name__}: {error}"
    return result


def scan_library(database: str | Path | None = None) -> int:
    """Recursively scan registered folders and reconcile the local track index."""
    total = 0
    for folder in list_library_folders(database):
        root = Path(folder)
        found: set[str] = set()
        if root.is_dir():
            for current, directories, filenames in os.walk(root, followlinks=False):
                directories[:] = [
                    name for name in directories if not (Path(current) / name).is_symlink()
                ]
                for filename in filenames:
                    file_path = Path(current) / filename
                    if file_path.is_symlink() or file_path.suffix.casefold() not in SUPPORTED_FORMATS:
                        continue
                    try:
                        stat = file_path.stat()
                        metadata = read_track_metadata(file_path)
                        record = {
                            "path": str(file_path.resolve()),
                            **metadata,
                            "file_format": file_path.suffix.lstrip(".").upper(),
                            "file_size": stat.st_size,
                            "modified_ns": stat.st_mtime_ns,
                        }
                        save_track(record, database)
                        found.add(record["path"])
                        total += 1
                    except OSError:
                        continue
        remove_missing_tracks(root, found, database)
    return total
