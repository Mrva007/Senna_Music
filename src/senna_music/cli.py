from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import keyring

from senna_music.core.collections import (
    add_favorites,
    add_tracks_to_playlist,
    create_playlist,
    delete_playlist,
    list_favorites,
    list_playlists,
    list_playlist_tracks,
    remove_favorite,
    remove_track_from_playlist,
    rename_playlist,
)
from senna_music.core.downloads import DownloadCancelled, download_audio
from senna_music.core.lyrics import fetch_lyrics
from senna_music.core.scanner import scan_library
from senna_music.core.search import search_source
from senna_music.core.storage import (
    add_download_task,
    add_library_folder,
    clear_finished_download_tasks,
    delete_download_task,
    get_next_download_task,
    initialize_database,
    list_download_tasks,
    list_library_folders,
    list_tracks,
    remove_library_folder,
    retry_download_task,
    update_download_task,
    get_setting,
)

KEYRING_SERVICE = "Senna Music"


def _emit(payload: Any, stream=None) -> None:
    print(json.dumps(payload, ensure_ascii=False, default=str), file=stream or sys.stdout)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="senna-music-cli",
        description="Senna Music command-line interface for agents and automation.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("version", help="Show the installed application version.")

    library = commands.add_parser("library", help="Manage the local music library.")
    library_commands = library.add_subparsers(dest="action", required=True)
    library_commands.add_parser("list", help="List indexed local tracks.")
    library_commands.add_parser("folders", help="List registered music folders.")
    library_commands.add_parser("scan", help="Scan registered folders.")
    add_folder = library_commands.add_parser("add-folder", help="Register and scan a folder.")
    add_folder.add_argument("path")
    remove_folder = library_commands.add_parser("remove-folder", help="Unregister a folder.")
    remove_folder.add_argument("path")

    search = commands.add_parser("search", help="Search an enabled online provider.")
    search.add_argument("query")
    search.add_argument(
        "--source", choices=["all", "YouTube", "Spotify", "SoundCloud"], default="all"
    )
    search.add_argument("--limit", type=int, default=10)

    download = commands.add_parser("download", help="Add an audio download to the queue.")
    download.add_argument("--url", required=True, help="Original source URL.")
    download.add_argument("--download-url", help="Matched audio URL; defaults to --url.")
    download.add_argument("--source", default="YouTube")
    download.add_argument("--title", required=True)
    download.add_argument("--artist", default="")
    download.add_argument("--album", default="")
    download.add_argument("--destination", required=True)
    download.add_argument("--format", choices=["original", "mp3", "m4a", "flac"])
    download.add_argument("--quality", choices=["128", "192", "256", "320"])

    queue = commands.add_parser("queue", help="Manage the persistent download queue.")
    queue_commands = queue.add_subparsers(dest="action", required=True)
    queue_commands.add_parser("list", help="List queued and completed downloads.")
    queue_commands.add_parser("run", help="Process all queued downloads.")
    retry = queue_commands.add_parser("retry", help="Retry a failed or cancelled task.")
    retry.add_argument("task_id", type=int)
    remove = queue_commands.add_parser("remove", help="Remove a queue entry.")
    remove.add_argument("task_id", type=int)
    queue_commands.add_parser("clear-finished", help="Remove completed, skipped, and cancelled tasks.")

    playlists = commands.add_parser("playlists", help="Manage playlists.")
    playlist_commands = playlists.add_subparsers(dest="action", required=True)
    playlist_commands.add_parser("list")
    create = playlist_commands.add_parser("create")
    create.add_argument("name")
    rename = playlist_commands.add_parser("rename")
    rename.add_argument("playlist_id", type=int)
    rename.add_argument("name")
    delete = playlist_commands.add_parser("delete")
    delete.add_argument("playlist_id", type=int)
    add = playlist_commands.add_parser("add")
    add.add_argument("playlist_id", type=int)
    add.add_argument("track_paths", nargs="+")
    tracks = playlist_commands.add_parser("tracks")
    tracks.add_argument("playlist_id", type=int)
    remove_track = playlist_commands.add_parser("remove")
    remove_track.add_argument("playlist_id", type=int)
    remove_track.add_argument("track_path")

    favorites = commands.add_parser("favorites", help="Manage Favorites.")
    favorite_commands = favorites.add_subparsers(dest="action", required=True)
    favorite_commands.add_parser("list")
    favorite_add = favorite_commands.add_parser("add")
    favorite_add.add_argument("track_paths", nargs="+")
    favorite_remove = favorite_commands.add_parser("remove")
    favorite_remove.add_argument("track_path")

    lyrics = commands.add_parser("lyrics", help="Find lyrics for a track.")
    lyrics.add_argument("title")
    lyrics.add_argument("--artist", required=True)
    lyrics.add_argument("--album", default="")
    lyrics.add_argument("--duration", type=float)
    lyrics.add_argument("--language", default="auto")

    return parser


def _run_queue() -> int:
    completed = 0
    failed = 0
    while True:
        task = get_next_download_task()
        if task is None:
            break
        task_id = int(task["id"])
        update_download_task(task_id, status="downloading", error="")
        try:
            result = download_audio(
                task, task["destination_root"],
                ffmpeg_location=get_setting("ffmpeg_location", ""),
            )
            update_download_task(
                task_id,
                status=result["status"],
                progress=100 if result["status"] in {"completed", "skipped"} else 0,
                destination_path=result.get("path", ""),
                error=result.get("message", ""),
            )
            if result["status"] in {"completed", "skipped"}:
                completed += 1
        except DownloadCancelled as error:
            update_download_task(task_id, status="cancelled", error=str(error))
        except Exception as error:  # noqa: BLE001 - CLI reports each task failure
            update_download_task(task_id, status="failed", error=str(error))
            failed += 1
    _emit({"completed_or_skipped": completed, "failed": failed})
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    initialize_database()

    try:
        if args.command == "version":
            _emit({"name": "Senna Music", "version": "0.1.0"})
            return 0

        if args.command == "library":
            if args.action == "list":
                _emit(list_tracks())
            elif args.action == "folders":
                _emit(list_library_folders())
            elif args.action == "scan":
                _emit({"scanned_tracks": scan_library()})
            elif args.action == "add-folder":
                folder = Path(args.path).expanduser()
                if not folder.is_dir():
                    raise ValueError(f"Folder does not exist: {folder}")
                added = add_library_folder(folder)
                payload = {"added": added, "folder": str(folder.resolve())}
                if added:
                    payload["scanned_tracks"] = scan_library()
                _emit(payload)
            elif args.action == "remove-folder":
                removed = remove_library_folder(args.path)
                _emit({"removed": removed, "folder": args.path, "files_deleted": False})
            return 0

        if args.command == "search":
            sources = (
                [
                    source for source in ("YouTube", "Spotify", "SoundCloud")
                    if get_setting(f"source_enabled:{source.casefold()}", "false") == "true"
                ]
                if args.source == "all" else [args.source]
            )
            client_id = keyring.get_password(KEYRING_SERVICE, "spotify_client_id") or ""
            client_secret = keyring.get_password(KEYRING_SERVICE, "spotify_client_secret") or ""
            results = []
            errors = {}
            query = args.query.casefold().strip()
            for track in list_tracks():
                searchable = " ".join(
                    [track["title"], track["artist"], track["album"]]
                ).casefold()
                if query in searchable:
                    results.append({
                        "source": "Local Music",
                        "title": track["title"],
                        "artist": track["artist"],
                        "album": track["album"],
                        "duration": track["duration"],
                        "url": track["path"],
                        "download_url": "",
                        "thumbnail": "",
                    })
            for source in sources:
                try:
                    found = search_source(
                        source, args.query, args.limit, client_id, client_secret
                    )
                    results.extend(asdict(result) for result in found)
                except RuntimeError as error:
                    errors[source] = str(error)
            _emit({"results": results, "errors": errors})
            return 0

        if args.command == "download":
            destination = Path(args.destination).expanduser()
            if not destination.is_dir():
                raise ValueError(f"Download destination does not exist: {destination}")
            task_id = add_download_task({
                "source": args.source,
                "source_url": args.url,
                "download_url": args.download_url or args.url,
                "destination_root": str(destination.resolve()),
                "title": args.title,
                "artist": args.artist,
                "album": args.album,
                "requested_format": args.format or get_setting("download_format", "original"),
                "quality": args.quality or get_setting("download_quality", "192"),
            })
            _emit({"queued": True, "task_id": task_id})
            return 0

        if args.command == "queue":
            if args.action == "list":
                _emit(list_download_tasks())
                return 0
            if args.action == "run":
                return _run_queue()
            if args.action == "retry":
                retry_download_task(args.task_id)
                _emit({"queued_for_retry": args.task_id})
                return 0
            if args.action == "remove":
                delete_download_task(args.task_id)
                _emit({"removed": args.task_id})
                return 0
            if args.action == "clear-finished":
                clear_finished_download_tasks()
                _emit({"cleared": True})
                return 0

        if args.command == "playlists":
            if args.action == "list":
                _emit(list_playlists())
            elif args.action == "create":
                created = create_playlist(args.name)
                _emit({"created": created, "name": args.name})
                return 0 if created else 2
            elif args.action == "rename":
                renamed = rename_playlist(args.playlist_id, args.name)
                _emit({"renamed": renamed, "playlist_id": args.playlist_id})
                return 0 if renamed else 2
            elif args.action == "delete":
                delete_playlist(args.playlist_id)
                _emit({"deleted": args.playlist_id})
            elif args.action == "add":
                added = add_tracks_to_playlist(args.playlist_id, args.track_paths)
                _emit({"added": added, "playlist_id": args.playlist_id})
            elif args.action == "tracks":
                _emit(list_playlist_tracks(args.playlist_id))
                return 0
            elif args.action == "remove":
                remove_track_from_playlist(args.playlist_id, args.track_path)
                _emit({"removed": args.track_path, "playlist_id": args.playlist_id})
            return 0

        if args.command == "favorites":
            if args.action == "list":
                _emit(list_favorites())
            elif args.action == "add":
                _emit({"added": add_favorites(args.track_paths)})
            elif args.action == "remove":
                remove_favorite(args.track_path)
                _emit({"removed": args.track_path})
            return 0

        if args.command == "lyrics":
            result = fetch_lyrics(
                args.title, args.artist, args.album, args.duration, args.language
            )
            _emit(asdict(result))
            return 0 if result.status == "found" else 2

    except (OSError, ValueError, RuntimeError) as error:
        _emit({"error": str(error)}, stream=sys.stderr)
        return 1

    return 2
