import pytest

from senna_music.core.downloads import build_target_path, download_audio
from senna_music.core.storage import (
    add_download_task,
    clear_finished_download_tasks,
    get_next_download_task,
    initialize_database,
    list_download_tasks,
    retry_download_task,
    update_download_task,
)


def sample_task():
    return {
        "source": "YouTube",
        "source_url": "https://youtube.com/watch?v=abc",
        "download_url": "https://youtube.com/watch?v=abc",
        "destination_root": "C:/Music",
        "title": "Song",
        "artist": "Artist",
        "album": "Album",
        "requested_format": "original",
        "quality": "192",
    }


def test_download_queue_persists_status_and_retry(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    task_id = add_download_task(sample_task(), db)
    task = get_next_download_task(db)
    assert task["id"] == task_id
    update_download_task(task_id, db, status="failed", progress=42, error="network")
    retry_download_task(task_id, db)
    task = list_download_tasks(db)[0]
    assert task["status"] == "queued"
    assert task["progress"] == 0
    assert task["error"] == ""


def test_clear_finished_downloads_keeps_active_tasks(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    completed = add_download_task(sample_task(), db)
    active = add_download_task(sample_task(), db)
    update_download_task(completed, db, status="completed")
    update_download_task(active, db, status="downloading")
    clear_finished_download_tasks(db)
    assert [task["id"] for task in list_download_tasks(db)] == [active]


def test_build_target_path_organizes_and_sanitizes_names(tmp_path):
    target = build_target_path(
        {"artist": "../Artist", "album": "Album", "title": "Song/Name"},
        tmp_path,
        "mp3",
    )
    assert target.is_relative_to(tmp_path.resolve())
    assert target.parts[-3].endswith("Artist")
    assert target.suffix == ".mp3"


def test_download_audio_skips_existing_target_without_overwrite(monkeypatch, tmp_path):
    target = build_target_path(sample_task(), tmp_path, "webm")
    target.parent.mkdir(parents=True)
    target.write_bytes(b"existing")

    class FakeYDL:
        def __init__(self, options):
            self.params = options

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def extract_info(self, _url, download=False):
            assert download is False
            return {"ext": "webm"}

        def download(self, _urls):
            raise AssertionError("Existing files must not be overwritten.")

    monkeypatch.setattr("senna_music.core.downloads.YoutubeDL", FakeYDL)
    result = download_audio(sample_task(), tmp_path)
    assert result["status"] == "skipped"
    assert target.read_bytes() == b"existing"


def test_download_audio_reports_missing_url(tmp_path):
    task = sample_task()
    task["download_url"] = ""
    with pytest.raises(ValueError, match="No supported audio"):
        download_audio(task, tmp_path)

def test_interrupted_download_tasks_are_requeued_on_database_startup(tmp_path):
    db = tmp_path / "senna.sqlite3"
    initialize_database(db)
    task_id = add_download_task(sample_task(), db)
    update_download_task(task_id, db, status="downloading", progress=37)
    initialize_database(db)
    task = list_download_tasks(db)[0]
    assert task["status"] == "queued"
    assert task["progress"] == 0
    assert task["destination_root"] == "C:/Music"

def test_existing_download_queue_schema_is_migrated(tmp_path):
    import sqlite3

    db = tmp_path / "senna.sqlite3"
    connection = sqlite3.connect(db)
    connection.execute(
        """
        CREATE TABLE download_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_url TEXT NOT NULL,
            download_url TEXT NOT NULL,
            title TEXT NOT NULL,
            artist TEXT NOT NULL DEFAULT '',
            album TEXT NOT NULL DEFAULT '',
            requested_format TEXT NOT NULL DEFAULT 'original',
            quality TEXT NOT NULL DEFAULT '192',
            status TEXT NOT NULL DEFAULT 'queued',
            progress REAL NOT NULL DEFAULT 0,
            destination_path TEXT NOT NULL DEFAULT '',
            error TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()

    initialize_database(db)
    connection = sqlite3.connect(db)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(download_queue)")}
    connection.close()
    assert "destination_root" in columns
