# Senna Music

Senna Music is a **local-first Windows desktop music application**: manage and play your own music library, discover tracks across supported online sources, and download audio into a folder you choose.

The application is music-only. Video playback is out of scope.

## Current build

**Version:** 0.1.0 — V1 implementation in progress.

The merged desktop foundation provides:
- A runnable PySide6 desktop shell with the agreed left navigation, central workspace, and bottom player area.
- Home search entry point and dedicated Search Sources page.
- Local Music folder selection and persistent folder registration.
- A per-user SQLite database and Windows CI workflow.

The current Local Music implementation milestone adds recursive scanning of MP3, M4A, FLAC, WAV, and OGG files, Mutagen metadata reading, persistent track indexing, and a visible track list. Local playback, folder monitoring, cover art, and remaining library interactions are still in progress. Do not treat this early build as a complete player.

## Initial source direction

The planned integrated search sources are:
- YouTube (general YouTube, not a separate YouTube Music player)
- Spotify
- SoundCloud

Source adapters will normalize results into one list. Authenticated browser sessions/cookies will be investigated for sources that require a signed-in session. Spotify track information may be used to resolve a matching downloadable result from another supported source; Senna Music does not claim to extract Spotify's protected audio stream.

The shared download workflow is planned around yt-dlp and FFmpeg where supported. Torrent search is deferred.

## Technology baseline

- Python 3.11+
- PySide6 / Qt for the Windows desktop GUI
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
