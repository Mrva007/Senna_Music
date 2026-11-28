from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from langdetect import LangDetectException, detect

API_BASE = "https://lrclib.net/api"
USER_AGENT = "Senna Music/0.1 (https://github.com/Mrva007/Senna_Music)"
TIMESTAMP_PATTERN = re.compile(r"\[(\d{2}):(\d{2})(?:\.(\d{1,3}))?\]")


class LyricsProviderError(RuntimeError):
    """Raised when the lyrics provider cannot complete a request."""


@dataclass(frozen=True)
class LyricsResult:
    status: str
    synced_lyrics: str = ""
    plain_lyrics: str = ""
    language: str = "unknown"
    message: str = ""
    provider: str = "LRCLIB"


def _request(endpoint: str, params: dict[str, str]) -> dict | list | None:
    url = f"{API_BASE}/{endpoint}?{urlencode(params)}"
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=12) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            return None
        if error.code == 429:
            retry_after = error.headers.get("Retry-After", "later")
            raise LyricsProviderError(
                f"Lyrics service rate limit reached. Retry after {retry_after}."
            ) from error
        raise LyricsProviderError(f"Lyrics service returned HTTP {error.code}.") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise LyricsProviderError(f"Lyrics service is unavailable: {error}") from error


def _language(text: str) -> str:
    sample = re.sub(r"\[[^\]]+\]", " ", text or "")
    if len(sample.strip()) < 40:
        return "unknown"
    try:
        return detect(sample)
    except LangDetectException:
        return "unknown"


def _candidate_score(
    record: dict,
    title: str,
    artist: str,
    album: str,
    duration: float | None,
    preferred_language: str,
) -> tuple[int, float, int, int]:
    record_title = str(record.get("trackName") or record.get("name") or "")
    record_artist = str(record.get("artistName") or "")
    record_album = str(record.get("albumName") or "")
    language = _language(record.get("syncedLyrics") or record.get("plainLyrics") or "")
    language_penalty = (
        0 if preferred_language == "auto" or language == preferred_language else 1
    )
    duration_difference = (
        abs(float(record.get("duration") or 0) - duration)
        if duration is not None else 0.0
    )
    title_penalty = 0 if record_title.casefold() == title.casefold() else 1
    artist_penalty = 0 if record_artist.casefold() == artist.casefold() else 1
    album_penalty = 0 if not album or record_album.casefold() == album.casefold() else 1
    return (
        language_penalty,
        duration_difference + album_penalty * 5,
        title_penalty + artist_penalty,
        0 if record.get("syncedLyrics") else 1,
    )



def _fetch_lyrics_ovh(title: str, artist: str) -> LyricsResult | None:
    url = (
        "https://api.lyrics.ovh/v1/"
        f"{quote(artist.strip(), safe='')}/{quote(title.strip(), safe='')}"
    )
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None
    plain = str(payload.get("lyrics") or "").strip() if isinstance(payload, dict) else ""
    if not plain:
        return None
    return LyricsResult(
        "found",
        plain_lyrics=plain,
        language=_language(plain),
        provider="Lyrics.ovh",
    )

def fetch_lyrics(
    title: str,
    artist: str,
    album: str = "",
    duration: float | None = None,
    preferred_language: str = "auto",
) -> LyricsResult:
    """Fetch best-match lyrics; synchronized text is preferred over plain text."""
    if not title.strip() or not artist.strip():
        return LyricsResult("not_found", message="Track title and artist are required.")

    language = preferred_language.strip().lower() or "auto"
    params = {"track_name": title.strip(), "artist_name": artist.strip()}
    if album.strip():
        params["album_name"] = album.strip()
    if duration and duration > 0:
        params["duration"] = str(round(duration))

    try:
        exact = _request("get", params)
        records = [exact] if isinstance(exact, dict) else []
        exact_language = _language(
            (exact or {}).get("syncedLyrics") or (exact or {}).get("plainLyrics") or ""
        )
        if not records or (language != "auto" and exact_language != language):
            if records:
                time.sleep(0.25)
            search_params = {
                "track_name": title.strip(),
                "artist_name": artist.strip(),
            }
            if album.strip():
                search_params["album_name"] = album.strip()
            searched = _request("search", search_params)
            if isinstance(searched, list):
                records.extend(item for item in searched if isinstance(item, dict))
    except LyricsProviderError as error:
        fallback = _fetch_lyrics_ovh(title, artist)
        if fallback:
            return fallback
        return LyricsResult("error", message=str(error))

    if not records:
        fallback = _fetch_lyrics_ovh(title, artist)
        return fallback or LyricsResult(
            "not_found", message="No lyrics were found from the available providers."
        )

    best = min(
        records,
        key=lambda record: _candidate_score(
            record, title, artist, album, duration, language
        ),
    )
    if best.get("instrumental"):
        return LyricsResult(
            "instrumental", language="unknown",
            message="This track is marked as instrumental.",
        )

    synced = str(best.get("syncedLyrics") or "").strip()
    plain = str(best.get("plainLyrics") or "").strip()
    selected_text = synced or plain
    if not selected_text:
        fallback = _fetch_lyrics_ovh(title, artist)
        return fallback or LyricsResult(
            "not_found", message="The providers returned no lyrics text."
        )

    return LyricsResult(
        "found",
        synced_lyrics=synced,
        plain_lyrics=plain,
        language=_language(selected_text),
        provider="LRCLIB",
    )


def parse_lrc(value: str) -> list[tuple[int, str]]:
    """Parse LRC timestamps into (milliseconds, lyric line) pairs."""
    lines: list[tuple[int, str]] = []
    for raw_line in value.splitlines():
        matches = list(TIMESTAMP_PATTERN.finditer(raw_line))
        if not matches:
            continue
        text = raw_line[matches[-1].end():].strip()
        for match in matches:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            fraction = int((match.group(3) or "0").ljust(3, "0"))
            lines.append((minutes * 60_000 + seconds * 1000 + fraction, text))
    return sorted(lines, key=lambda item: item[0])
