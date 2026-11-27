# Senna Music

Senna Music is a **local-first Windows desktop music application**: manage and play your own music library, discover tracks across supported online sources, and download audio into a folder you choose.

The application is music-only. Video playback is out of scope.

## Current build

**Version:** 0.1.0 — desktop foundation in progress.

The first development PR introduces:
- A runnable PySide6 desktop shell with the agreed left navigation, central workspace, and bottom player area.
- Home search entry point and dedicated Search Sources page.
- Local Music folder selection and persistent folder registration.
- A per-user SQLite database for application settings and library-folder configuration.
- Windows CI test workflow.

The Local Music scanner/player, source adapters, authenticated source sessions, and download workflow are being added in subsequent small milestones. The visible early-build placeholders are intentional and are not represented as completed functionality.

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
- yt-dlp and FFmpeg for supported source download/processing workflows
- Mutagen for local audio metadata

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
