import json

from senna_music.cli import main


def test_cli_version_outputs_json(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("SENNA_MUSIC_DATABASE", str(tmp_path / "senna.sqlite3"))
    assert main(["version"]) == 0
    assert json.loads(capsys.readouterr().out)["version"] == "0.1.0"


def test_cli_library_folder_management_uses_shared_database(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("SENNA_MUSIC_DATABASE", str(tmp_path / "senna.sqlite3"))
    folder = tmp_path / "music"
    folder.mkdir()
    assert main(["library", "add-folder", str(folder)]) == 0
    added = json.loads(capsys.readouterr().out.splitlines()[0])
    assert added["added"] is True

    assert main(["library", "folders"]) == 0
    folders = json.loads(capsys.readouterr().out)
    assert folders == [str(folder.resolve())]


def test_cli_playlist_crud_and_favorites(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("SENNA_MUSIC_DATABASE", str(tmp_path / "senna.sqlite3"))
    assert main(["playlists", "create", "Road"]) == 0
    created = json.loads(capsys.readouterr().out)
    assert created["created"] is True
    assert main(["playlists", "list"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["name"] == "Road"
