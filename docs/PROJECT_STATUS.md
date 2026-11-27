# Senna Music — Project Status

**Current milestone:** V1 desktop foundation  
**Current version:** 0.1.0 (early development)  
**Implementation:** Authorized by the owner on 2026-11-27  
**Repository:** https://github.com/Mrva007/Senna_Music

## Current GitHub state

- Implementation branch: feature/v1-desktop-foundation
- The first implementation PR adds the PySide6 desktop shell, SQLite persistence foundation, Local Music folder registration, and Windows CI.
- No PR is merged until its diff and verification are reviewed.

## Working foundation

- Standalone, music-only, local-first desktop application.
- Left navigation, central workspace, and bottom compact-player area.
- Home search entry point; Local Music is a separate page.
- Initial online sources: YouTube, Spotify, and SoundCloud.
- Source-specific adapters feed one normalized result model.
- User-selected music storage; one local file supports both in-app and external playback.
- Shared GUI/Core architecture; CLI remains a later interface to the same Core.

## Implementation sequence

1. Desktop foundation: application entry point, navigation shell, SQLite persistence, CI.
2. Local Music: folder scanning, metadata, library views, and local playback.
3. Search: YouTube, Spotify, and SoundCloud adapters; source settings; session/cookie support where needed.
4. Downloads: yt-dlp/FFmpeg integration, unified queue, progress, pause/resume, duplicate handling, and file organization.
5. Library features: playlists, favorites, player queue, lyrics, and remaining accepted interactions.
6. Windows test build: packaging, configuration, and a repeatable test release.

## Current verification

- GitHub Actions is configured to run pytest and Ruff on Windows.
- Test results for the current PR are pending CI execution.
- The first GUI build is a foundation, not yet the complete first release.

## Deferred beyond the first testable build

Torrent search, advanced lyrics translations, CLI/agent integration, automatic updates, backup/recovery, and detailed visual micro-adjustments.
