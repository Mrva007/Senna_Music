from senna_music.core.collections import (
    add_favorites, add_tracks_to_favorite_collection, add_tracks_to_playlist,
    create_favorite_collection, create_playlist, delete_favorite_collection,
    delete_playlist, list_favorite_collection_tracks, list_favorite_collections,
    list_favorites, list_playlist_tracks, list_playlists, remove_favorite,
    remove_track_from_favorite_collection, remove_track_from_playlist,
    rename_favorite_collection, rename_playlist, reorder_favorites,
    reorder_playlist_tracks,
)
from senna_music.core.storage import initialize_database, save_track, remove_missing_tracks


def add_track(db, path, title):
    save_track({
        "path": str(path), "title": title, "artist": "Artist", "album": "Album",
        "track_number": "", "year": "", "genre": "", "duration": 120.0,
        "file_format": "MP3", "file_size": 10, "modified_ns": 1, "scan_error": "",
    }, db)


def test_playlists_support_unique_names_tracks_and_saved_order(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    paths = [tmp_path / "a.mp3", tmp_path / "b.mp3"]
    for index, path in enumerate(paths):
        add_track(db, path, f"Track {index}")
    assert create_playlist(" Rock ", db)
    assert not create_playlist("rock", db)
    playlist = list_playlists(db)[0]
    assert playlist["name"] == "Rock"
    assert add_tracks_to_playlist(playlist["id"], [str(p) for p in paths], db) == 2
    assert [t["path"] for t in list_playlist_tracks(playlist["id"], db)] == [str(p) for p in paths]
    reorder_playlist_tracks(playlist["id"], [str(paths[1]), str(paths[0])], db)
    assert [t["path"] for t in list_playlist_tracks(playlist["id"], db)] == [str(paths[1]), str(paths[0])]
    assert rename_playlist(playlist["id"], " Road ", db)
    assert not rename_playlist(playlist["id"], "road", db)
    remove_track_from_playlist(playlist["id"], str(paths[0]), db)
    assert len(list_playlist_tracks(playlist["id"], db)) == 1
    delete_playlist(playlist["id"], db)
    assert list_playlists(db) == []


def test_favorites_and_collections_are_independent_and_persistent(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    paths = [tmp_path / "one.mp3", tmp_path / "two.mp3"]
    for index, path in enumerate(paths):
        path.write_bytes(b"audio")
        add_track(db, path, f"Track {index}")
    assert add_favorites([str(p) for p in paths], db) == 2
    assert create_favorite_collection("  Road  ", db)
    assert not create_favorite_collection("road", db)
    collection = list_favorite_collections(db)[0]
    assert collection["track_count"] == 0
    add_tracks_to_favorite_collection(collection["id"], [str(paths[0])], db)
    remove_track_from_favorite_collection(collection["id"], str(paths[0]), db)
    assert len(list_favorites(db)) == 2
    assert list_favorite_collection_tracks(collection["id"], db) == []
    assert rename_favorite_collection(collection["id"], "Road Trips", db)
    reorder_favorites([str(paths[1]), str(paths[0])], db)
    assert [t["path"] for t in list_favorites(db)] == [str(paths[1]), str(paths[0])]
    remove_favorite(str(paths[0]), db)
    assert len(list_favorites(db)) == 1
    delete_favorite_collection(collection["id"], db)
    assert paths[0].exists() and paths[1].exists()


def test_deleting_indexed_track_cascades_playlist_links_but_not_audio(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")
    add_track(db, audio, "Song")
    assert create_playlist("Playlist", db)
    playlist = list_playlists(db)[0]
    add_tracks_to_playlist(playlist["id"], [str(audio)], db)
    remove_missing_tracks(tmp_path, set(), db)
    assert list_playlist_tracks(playlist["id"], db) == []
    assert audio.exists()
