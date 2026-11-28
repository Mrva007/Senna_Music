from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from yt_dlp import YoutubeDL


@dataclass(frozen=True)
class SearchResult:
    source: str
    title: str
    artist: str
    album: str
    duration: float | None
    url: str
    download_url: str = ""
    thumbnail: str = ""


class SearchProviderError(RuntimeError):
    """Raised when an online source cannot complete its search."""


def _normalize_entry(entry: dict[str, Any], source: str) -> SearchResult | None:
    if not entry:
        return None
    url = str(entry.get("webpage_url") or entry.get("url") or "")
    if not url:
        identifier = entry.get("id")
        if identifier and source == "YouTube":
            url = f"https://www.youtube.com/watch?v={identifier}"
    title = str(entry.get("title") or "").strip()
    if not title or not url:
        return None
    artist = str(entry.get("artist") or entry.get("uploader") or entry.get("creator") or "")
    return SearchResult(
        source=source,
        title=title,
        artist=artist,
        album=str(entry.get("album") or ""),
        duration=float(entry["duration"]) if entry.get("duration") else None,
        url=url,
        download_url=url,
        thumbnail=str(entry.get("thumbnail") or ""),
    )


def _search_ytdlp(query: str, prefix: str, source: str, limit: int) -> list[SearchResult]:
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "ignoreerrors": True,
    }
    try:
        with YoutubeDL(options) as downloader:
            data = downloader.extract_info(f"{prefix}{limit}:{query}", download=False)
    except Exception as error:
        raise SearchProviderError(f"{source} search failed: {error}") from error
    entries = data.get("entries", []) if data else []
    results = [_normalize_entry(entry, source) for entry in entries if entry]
    return [result for result in results if result is not None]


def search_youtube(query: str, limit: int = 10) -> list[SearchResult]:
    """Search general YouTube (not a separate YouTube Music player)."""
    return _search_ytdlp(query, "ytsearch", "YouTube", limit)


def search_soundcloud(query: str, limit: int = 10) -> list[SearchResult]:
    """Search SoundCloud using yt-dlp's SoundCloud search extractor."""
    return _search_ytdlp(query, "scsearch", "SoundCloud", limit)


def search_spotify(
    query: str,
    client_id: str,
    client_secret: str,
    limit: int = 10,
) -> list[SearchResult]:
    """Resolve Spotify metadata and a matching downloadable source through spotDL.

    spotDL uses Spotify for track metadata and searches other audio providers (normally
    YouTube) for the corresponding audio. It does not extract Spotify's protected stream.
    """
    if not client_id.strip() or not client_secret.strip():
        raise SearchProviderError(
            "Spotify search requires Spotify Developer app credentials. "
            "Configure the Client ID and Client Secret in Search Sources."
        )
    try:
        from spotdl import Spotdl

        client = Spotdl(
            client_id=client_id.strip(),
            client_secret=client_secret.strip(),
            headless=True,
        )
        songs = client.search([query])[:limit]
        urls = client.get_download_urls(songs)
    except Exception as error:
        raise SearchProviderError(f"Spotify lookup failed: {error}") from error

    results = []
    for song, download_url in zip(songs, urls, strict=False):
        spotify_url = str(getattr(song, "url", "") or "")
        title = str(getattr(song, "name", "") or "").strip()
        if not spotify_url or not title:
            continue
        artists = getattr(song, "artists", []) or []
        artist = ", ".join(str(item) for item in artists)
        results.append(
            SearchResult(
                source="Spotify",
                title=title,
                artist=artist,
                album=str(getattr(song, "album_name", "") or ""),
                duration=float(getattr(song, "duration", 0) or 0) or None,
                url=spotify_url,
                download_url=str(download_url or ""),
                thumbnail=str(getattr(song, "cover_url", "") or ""),
            )
        )
    return results


def search_source(
    source: str,
    query: str,
    limit: int = 10,
    spotify_client_id: str = "",
    spotify_client_secret: str = "",
) -> list[SearchResult]:
    normalized = source.casefold()
    if normalized == "youtube":
        return search_youtube(query, limit)
    if normalized == "soundcloud":
        return search_soundcloud(query, limit)
    if normalized == "spotify":
        return search_spotify(query, spotify_client_id, spotify_client_secret, limit)
    raise SearchProviderError(f"Unsupported search source: {source}")
