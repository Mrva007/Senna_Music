from senna_music.core import metadata


class FakeAudio:
    def __init__(self):
        self.tags = {"title": ["Old title"], "artist": ["Artist"]}
        self.saved = False

    def save(self):
        self.saved = True


def test_update_track_metadata_writes_and_clears_supported_tags(monkeypatch, tmp_path):
    audio = FakeAudio()
    monkeypatch.setattr(metadata, "MutagenFile", lambda *_args, **_kwargs: audio)
    metadata.update_track_metadata(tmp_path / "song.mp3", {
        "title": " New title ", "artist": "", "year": "2025"
    })
    assert audio.tags == {"title": ["New title"], "date": ["2025"]}
    assert audio.saved is True


def test_update_track_metadata_rejects_unknown_fields(monkeypatch, tmp_path):
    monkeypatch.setattr(metadata, "MutagenFile", lambda *_args, **_kwargs: FakeAudio())
    try:
        metadata.update_track_metadata(tmp_path / "song.mp3", {"composer": "Someone"})
    except ValueError as error:
        assert "Unsupported metadata fields" in str(error)
    else:
        raise AssertionError("Unknown metadata field should be rejected")


def test_update_track_metadata_reports_unsupported_audio(monkeypatch, tmp_path):
    monkeypatch.setattr(metadata, "MutagenFile", lambda *_args, **_kwargs: None)
    try:
        metadata.update_track_metadata(tmp_path / "song.mp3", {"title": "Title"})
    except ValueError as error:
        assert "does not support metadata editing" in str(error)
    else:
        raise AssertionError("Unsupported audio should be rejected")
