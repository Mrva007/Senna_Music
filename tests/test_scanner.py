from senna_music.core.scanner import scan_library
from senna_music.core.storage import (
    add_library_folder,
    initialize_database,
    list_tracks,
    remove_library_folder,
)


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


def test_removing_folder_only_removes_library_index(tmp_path, monkeypatch):
    database = tmp_path / "senna.sqlite3"
    music = tmp_path / "Music"
    music.mkdir()
    audio_file = music / "keep-on-disk.ogg"
    audio_file.write_bytes(b"audio")
    initialize_database(database)
    add_library_folder(music, database)
    monkeypatch.setattr(
        "senna_music.core.scanner.read_track_metadata",
        lambda path: {
            "title": path.stem, "artist": "", "album": "", "track_number": "",
            "year": "", "genre": "", "duration": None, "scan_error": "",
        },
    )
    scan_library(database)

    remove_library_folder(str(music), database)

    assert list_tracks(database) == []
    assert audio_file.exists()


def test_scan_preserves_index_when_registered_folder_is_temporarily_unavailable(
    tmp_path, monkeypatch
):
    database = tmp_path / "senna.sqlite3"
    music = tmp_path / "Music"
    music.mkdir()
    audio_file = music / "keep-indexed.mp3"
    audio_file.write_bytes(b"audio")
    initialize_database(database)
    add_library_folder(music, database)
    monkeypatch.setattr(
        "senna_music.core.scanner.read_track_metadata",
        lambda path: {
            "title": path.stem, "artist": "", "album": "", "track_number": "",
            "year": "", "genre": "", "duration": None, "scan_error": "",
        },
    )
    scan_library(database)
    assert len(list_tracks(database)) == 1

    # Simulate an unplugged external drive: the registered root is unavailable.
    music.rename(tmp_path / "Music temporarily offline")
    assert scan_library(database) == 0
    assert len(list_tracks(database)) == 1


def test_scan_does_not_remove_tracks_after_partial_folder_read_error(tmp_path, monkeypatch):
    database = tmp_path / "senna.sqlite3"
    music = tmp_path / "Music"
    music.mkdir()
    audio_file = music / "still-there.wav"
    audio_file.write_bytes(b"audio")
    initialize_database(database)
    add_library_folder(music, database)
    monkeypatch.setattr(
        "senna_music.core.scanner.read_track_metadata",
        lambda path: {
            "title": path.stem, "artist": "", "album": "", "track_number": "",
            "year": "", "genre": "", "duration": None, "scan_error": "",
        },
    )
    scan_library(database)
    assert len(list_tracks(database)) == 1

    def incomplete_walk(root, followlinks=False, onerror=None):
        if onerror is not None:
            onerror(PermissionError("temporary access denied"))
        yield str(root), [], []

    monkeypatch.setattr("senna_music.core.scanner.os.walk", incomplete_walk)
    assert scan_library(database) == 0
    assert len(list_tracks(database)) == 1
