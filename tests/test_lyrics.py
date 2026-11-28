from senna_music.core import lyrics


def test_parse_lrc_handles_multiple_timestamps_and_milliseconds():
    parsed = lyrics.parse_lrc(
        "[00:01.2][00:02.34]First line\n[01:03.456]Second line\nmetadata"
    )
    assert parsed == [
        (1200, "First line"),
        (2340, "First line"),
        (63456, "Second line"),
    ]


def test_fetch_lyrics_prefers_synced_lyrics(monkeypatch):
    record = {
        "trackName": "Song",
        "artistName": "Artist",
        "albumName": "Album",
        "duration": 120,
        "syncedLyrics": "[00:01.00]Line",
        "plainLyrics": "Line",
        "instrumental": False,
    }
    monkeypatch.setattr(lyrics, "_request", lambda *_args, **_kwargs: record)
    monkeypatch.setattr(lyrics, "_language", lambda _text: "en")
    result = lyrics.fetch_lyrics("Song", "Artist", "Album", 120)
    assert result.status == "found"
    assert result.synced_lyrics == "[00:01.00]Line"
    assert result.plain_lyrics == "Line"


def test_fetch_lyrics_falls_back_to_search_when_exact_missing(monkeypatch):
    calls = []

    def fake_request(endpoint, _params):
        calls.append(endpoint)
        if endpoint == "get":
            return None
        return [{
            "trackName": "Song",
            "artistName": "Artist",
            "plainLyrics": "A sufficiently long lyric text for language detection.",
            "syncedLyrics": None,
            "instrumental": False,
        }]

    monkeypatch.setattr(lyrics, "_request", fake_request)
    monkeypatch.setattr(lyrics, "_language", lambda _text: "en")
    result = lyrics.fetch_lyrics("Song", "Artist")
    assert calls == ["get", "search"]
    assert result.status == "found"
    assert result.synced_lyrics == ""


def test_fetch_lyrics_reports_instrumental_track(monkeypatch):
    monkeypatch.setattr(
        lyrics, "_request",
        lambda *_args, **_kwargs: {"instrumental": True},
    )
    result = lyrics.fetch_lyrics("Song", "Artist")
    assert result.status == "instrumental"

def test_fetch_lyrics_uses_plain_provider_as_fallback(monkeypatch):
    monkeypatch.setattr(lyrics, "_request", lambda *_args, **_kwargs: None)
    fallback = lyrics.LyricsResult(
        "found", plain_lyrics="Plain text lyrics", language="en", provider="Lyrics.ovh"
    )
    monkeypatch.setattr(lyrics, "_fetch_lyrics_ovh", lambda *_args: fallback)
    result = lyrics.fetch_lyrics("Song", "Artist")
    assert result.provider == "Lyrics.ovh"
    assert result.plain_lyrics == "Plain text lyrics"


def test_fetch_lyrics_uses_fallback_when_lrclib_is_unavailable(monkeypatch):
    def fail_request(*_args, **_kwargs):
        raise lyrics.LyricsProviderError("rate limited")

    monkeypatch.setattr(lyrics, "_request", fail_request)
    fallback = lyrics.LyricsResult(
        "found", plain_lyrics="Fallback lyrics", language="en", provider="Lyrics.ovh"
    )
    monkeypatch.setattr(lyrics, "_fetch_lyrics_ovh", lambda *_args: fallback)
    result = lyrics.fetch_lyrics("Song", "Artist")
    assert result.status == "found"
    assert result.provider == "Lyrics.ovh"
