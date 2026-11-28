# Senna Music

Senna Music is a **local-first Windows desktop music application**: manage and play your own music library, discover tracks across supported online sources, and download audio into a folder you choose.

The application is music-only. Video playback is out of scope.

## Current build

**Version:** 0.1.0 — V1 implementation in progress.

The desktop foundation provides a runnable PySide6 shell, navigation, SQLite persistence, and Windows CI. Local Music currently includes:
- Recursive scanning of MP3, M4A, FLAC, WAV, and OGG files.
- Mutagen metadata reading and persistent SQLite track indexing.
- Startup scanning plus periodic background rescanning while the application is open.
- Safe handling of unavailable folders and incomplete scans.
- Local audio playback, previous/next, play/pause, seeking, and volume controls.
- Track details and error information from the Local Music context menu.

The application is still under active V1 development. Online search adapters, downloads, playlists, Favorites, expanded player, lyrics, and Windows packaging remain in the roadmap.

## Initial source direction

The planned integrated search sources are:
- YouTube (general YouTube, not a separate YouTube Music player)
- Spotify
- SoundCloud

Source adapters will normalize results into one list. Authenticated browser sessions/cookies will be investigated for sources that require a signed-in session. Spotify track information may be used to resolve a matching downloadable result from another supported source; Senna Music does not claim to extract Spotify's protected audio stream.

The shared download workflow is planned around yt-dlp and FFmpeg where supported. Torrent search is deferred.

## Technology baseline

- Python 3.11+
- PySide6 / Qt for the Windows desktop GUI and multimedia playback
- SQLite for local application data
- Mutagen for local audio metadata
- yt-dlp and FFmpeg for supported source download/processing workflows

## Run from source (Windows)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m senna_music
```

## Project documentation

- [Product specification](docs/PRODUCT_SPECIFICATION.md)
- [GUI specification](docs/GUI_SPECIFICATION.md)
- [Decision log](docs/DECISIONS.md)
- [Open questions](docs/OPEN_QUESTIONS.md)
- [Project status](docs/PROJECT_STATUS.md)
- [Roadmap](docs/ROADMAP.md)
- [Development workflow](docs/DEVELOPMENT_WORKFLOW.md)

GitHub is the source of truth. Implementation is delivered in small, reviewable pull requests, with tests and documentation updated alongside each milestone.
