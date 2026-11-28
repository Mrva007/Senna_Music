from types import SimpleNamespace

import pytest

from senna_music.core import search


class FakeYoutubeDL:
    def __init__(self, options):
        self.options = options
        self.query = ""

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def extract_info(self, query, download=False):
        self.query = query
        assert download is False
        return {
            "entries": [
                {
                    "id": "abc123",
                    "title": "Song",
                    "uploader": "Artist",
                    "duration": 120,
                    "thumbnail": "https://example.test/cover.jpg",
                },
                {"title": "Invalid result"},
            ]
        }


def test_youtube_search_normalizes_flat_results(monkeypatch):
    monkeypatch.setattr(search, "YoutubeDL", FakeYoutubeDL)
    results = search.search_youtube("artist song", limit=5)
    assert len(results) == 1
    assert results[0].source == "YouTube"
    assert results[0].title == "Song"
    assert results[0].artist == "Artist"
    assert results[0].url == "https://www.youtube.com/watch?v=abc123"


def test_soundcloud_uses_soundcloud_search_prefix(monkeypatch):
    captured = {}

    class CapturingYDL(FakeYoutubeDL):
        def extract_info(self, query, download=False):
            captured["query"] = query
            return {"entries": [{"url": "https://soundcloud.com/artist/song", "title": "Song"}]}

    monkeypatch.setattr(search, "YoutubeDL", CapturingYDL)
    results = search.search_soundcloud("artist song", limit=7)
    assert captured["query"] == "scsearch7:artist song"
    assert results[0].source == "SoundCloud"


def test_spotify_requires_credentials():
    with pytest.raises(search.SearchProviderError, match="requires Spotify Developer"):
        search.search_spotify("artist song", "", "")


def test_spotify_uses_metadata_and_matching_audio_url(monkeypatch):
    class FakeSpotdl:
        def __init__(self, **_kwargs):
            pass

        def search(self, queries):
            assert queries == ["artist song"]
            return [
                SimpleNamespace(
                    url="https://open.spotify.com/track/id",
                    name="Song",
                    artists=["Artist"],
                    album_name="Album",
                    duration=125,
                    cover_url="",
                )
            ]

        def get_download_urls(self, songs):
            assert len(songs) == 1
            return ["https://www.youtube.com/watch?v=matched"]

    monkeypatch.setitem(__import__("sys").modules, "spotdl", SimpleNamespace(Spotdl=FakeSpotdl))
    results = search.search_spotify("artist song", "client", "secret")
    assert results[0].source == "Spotify"
    assert results[0].url == "https://open.spotify.com/track/id"
    assert results[0].download_url == "https://www.youtube.com/watch?v=matched"
