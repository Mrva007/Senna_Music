from senna_music.core.storage import (
    add_library_folder,
    initialize_database,
    list_tracks,
)
from senna_music.core.scanner import scan_library


def test_scan_recursively_indexes_supported_audio_and_ignores_other_files(tmp_path, monkeypatch):
    database = tmp_path / "senna.sqlite3"
    music = tmp_path / "Music"
    nested = music / "Artist" / "Album"
    nested.mkdir(parents=True)
    audio_file = nested / "01 - Song.mp3"
    audio_file.write_bytes(b"not-a-real-mp3")
    (nested / "cover.jpg").write_bytes(b"image")

    initialize_database(database)
    add_library_folder(music, database)
    monkeypatch.setattr(
        "senna_music.core.scanner.read_track_metadata",
        lambda path: {
            "title": "Song", "artist": "Artist", "album": "Album",
            "track_number": "1", "year": "2024", "genre": "Rock",
            "duration": 123.0, "scan_error": "",
        },
    )

    assert scan_library(database) == 1
    tracks = list_tracks(database)
    assert len(tracks) == 1
    assert tracks[0]["title"] == "Song"
    assert tracks[0]["artist"] == "Artist"
    assert tracks[0]["duration"] == 123.0


def test_scan_keeps_unreadable_file_visible_and_removes_missing_index_entries(tmp_path, monkeypatch):
    database = tmp_path / "senna.sqlite3"
    music = tmp_path / "Music"
    music.mkdir()
    audio_file = music / "broken.flac"
    audio_file.write_bytes(b"broken")
    initialize_database(database)
    add_library_folder(music, database)

    monkeypatch.setattr(
        "senna_music.core.scanner.read_track_metadata",
        lambda path: {
            "title": path.stem, "artist": "", "album": "", "track_number": "",
            "year": "", "genre": "", "duration": None,
            "scan_error": "Audio metadata could not be read.",
        },
    )
    scan_library(database)
    assert list_tracks(database)[0]["scan_error"]

    audio_file.unlink()
    assert scan_library(database) == 0
    assert list_tracks(database) == []
