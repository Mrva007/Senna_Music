from __future__ import annotations

from pathlib import Path
from typing import Any

from mutagen import File as MutagenFile

TAG_KEYS = {"title": "title", "artist": "artist", "album": "album", "track_number": "tracknumber", "year": "date", "genre": "genre"}


def update_track_metadata(file_path: str | Path, updates: dict[str, str]) -> None:
    """Write supported basic tags directly to the original audio file."""
    unknown = set(updates) - set(TAG_KEYS)
    if unknown:
        raise ValueError(f"Unsupported metadata fields: {', '.join(sorted(unknown))}")
    audio = MutagenFile(Path(file_path), easy=True)
    if audio is None:
        raise ValueError("This audio file format does not support metadata editing.")
    if audio.tags is None:
        try:
            audio.add_tags()
        except Exception as error:  # noqa: BLE001
            raise ValueError(f"Metadata cannot be added to this file: {error}") from error
    for field, value in updates.items():
        key = TAG_KEYS[field]
        normalized = value.strip()
        if normalized:
            audio.tags[key] = [normalized]
        elif key in audio.tags:
            del audio.tags[key]
    try:
        audio.save()
    except Exception as error:  # noqa: BLE001
        raise ValueError(f"Metadata could not be saved: {error}") from error


def read_cover_art(file_path: str | Path) -> bytes | None:
    """Return the first embedded image when the container exposes one."""
    audio = MutagenFile(Path(file_path), easy=False)
    if audio is None or audio.tags is None:
        return None
    tags: Any = audio.tags
    if hasattr(tags, "getall"):
        pictures = tags.getall("APIC")
        if pictures:
            return bytes(pictures[0].data)
    cover = tags.get("covr") if hasattr(tags, "get") else None
    if cover:
        return bytes(cover[0])
    pictures = getattr(audio, "pictures", None)
    if pictures:
        return bytes(pictures[0].data)
    return None
