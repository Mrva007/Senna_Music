from senna_music.core.storage import (
    add_library_folder,
    get_setting,
    initialize_database,
    list_library_folders,
    remove_library_folder,
    set_setting,
)


def test_database_initializes_and_persists_settings(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    set_setting("theme", "dark", db)
    assert get_setting("theme", path=db) == "dark"
    assert get_setting("missing", "default", db) == "default"


def test_library_folders_are_unique_and_removable(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    folder = tmp_path / "Music"
    folder.mkdir()

    assert add_library_folder(folder, db) is True
    assert add_library_folder(folder, db) is False
    assert list_library_folders(db) == [str(folder.resolve())]

    remove_library_folder(str(folder.resolve()), db)
    assert list_library_folders(db) == []
