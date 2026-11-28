from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from mutagen import File as MutagenFile
from mutagen import MutagenError
from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename


class DownloadCancelled(RuntimeError):
    """Raised when a user cancels an active download."""


def _safe_component(value: str, fallback: str) -> str:
    cleaned = sanitize_filename(value.strip(), restricted=True).strip(" .")
    return cleaned or fallback


def build_target_path(task: dict[str, Any], destination: str | Path, extension: str) -> Path:
    root = Path(destination).expanduser().resolve()
    artist = _safe_component(str(task.get("artist") or ""), "Unknown Artist")
    album = _safe_component(str(task.get("album") or ""), "Singles")
    title = _safe_component(str(task.get("title") or ""), "Unknown Track")
    target = (root / artist / album / f"{title}.{extension}").resolve()
    if not target.is_relative_to(root):
        raise ValueError("The generated download path is outside the selected destination.")
    return target


def _write_download_tags(path: Path, task: dict[str, Any]) -> None:
    audio = MutagenFile(path, easy=True)
    if audio is None:
        return
    if audio.tags is None:
        try:
            audio.add_tags()
        except (MutagenError, OSError, ValueError):
            return
    for field in ("title", "artist", "album"):
        value = str(task.get(field) or "").strip()
        if value:
            audio.tags[field] = [value]
    try:
        audio.save()
    except (MutagenError, OSError, ValueError):
        return


def download_audio(
    task: dict[str, Any],
    destination: str | Path,
    progress_callback: Callable[[float], None] | None = None,
    cancel_event: threading.Event | None = None,
    pause_event: threading.Event | None = None,
) -> dict[str, Any]:
    """Download one supported audio URL without overwriting an existing file."""
    url = str(task.get("download_url") or "").strip()
    if not url:
        raise ValueError("No supported audio download URL is available for this result.")

    requested_format = str(task.get("requested_format") or "original").lower()
    if requested_format not in {"original", "mp3", "m4a", "flac"}:
        raise ValueError(f"Unsupported audio format: {requested_format}")

    def progress_hook(data: dict[str, Any]) -> None:
        if cancel_event is not None and cancel_event.is_set():
            raise DownloadCancelled("Download cancelled by user.")
        if pause_event is not None:
            while not pause_event.is_set():
                if cancel_event is not None and cancel_event.is_set():
                    raise DownloadCancelled("Download cancelled by user.")
                pause_event.wait(0.25)
        if data.get("status") == "downloading" and progress_callback is not None:
            downloaded = data.get("downloaded_bytes") or 0
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            if total:
                progress_callback(min(100.0, downloaded * 100.0 / total))

    root = Path(destination).expanduser().resolve()
    options: dict[str, Any] = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "continuedl": True,
        "overwrites": False,
        "progress_hooks": [progress_hook],
    }

    with YoutubeDL(options) as probe:
        info = probe.extract_info(url, download=False)
    if not info:
        raise RuntimeError("The source did not return downloadable audio.")
    extension = str(info.get("ext") or "mp3").lower()
    target_extension = requested_format if requested_format != "original" else extension
    target = build_target_path(task, root, target_extension)
    if target.exists():
        return {
            "status": "skipped",
            "path": str(target),
            "message": "A file with this name already exists; it was not overwritten.",
        }

    options["outtmpl"] = str(target.with_suffix("")) + ".%(ext)s"
    if requested_format != "original":
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": requested_format,
                "preferredquality": str(task.get("quality") or "192"),
            }
        ]
    with YoutubeDL(options) as downloader:
        result = downloader.download([url])
        if result:
            raise RuntimeError(f"yt-dlp returned download error code {result}.")

    if not target.is_file():
        candidates = sorted(target.parent.glob(target.stem + ".*"))
        target = next(
            (candidate for candidate in candidates if candidate.suffix.lower() != ".part"),
            target,
        )
    if not target.is_file():
        raise RuntimeError("Download finished, but the output audio file was not found.")

    _write_download_tags(target, task)
    if progress_callback is not None:
        progress_callback(100.0)
    return {"status": "completed", "path": str(target), "message": ""}
