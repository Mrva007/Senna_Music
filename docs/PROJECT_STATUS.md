# Senna Music — Project Status

**Current milestone:** Local Music — recursive scan and library list  
**Current version:** 0.1.0 (early development)  
**Implementation:** Authorized by the owner on 2026-11-27  
**Repository:** https://github.com/Mrva007/Senna_Music

## Current GitHub state

- PR #15 (desktop foundation) is merged into `main`.
- Current implementation branch: `feature/local-music-library-scan`.
- The current PR work adds recursive audio scanning, metadata extraction, persistent track indexing, and the first Local Music track table.
- CI verification for the current work is pending; do not treat it as passed until GitHub reports the result.

## Working foundation

- Standalone, music-only, local-first desktop application.
- Left navigation, central workspace, and bottom compact-player area.
- Home search entry point; Local Music is a separate page.
- Initial online sources: YouTube, Spotify, and SoundCloud.
- Source-specific adapters feed one normalized result model.
- User-selected music storage; one local file supports both in-app and external playback.
- Shared GUI/Core architecture; CLI remains a later interface to the same Core.

## Implementation sequence

1. Desktop foundation: merged — application entry point, navigation shell, SQLite persistence, and CI workflow.
2. Local Music: folder registration is implemented; recursive scanning, metadata, persistent track indexing, and track-list UI are in the current PR. Folder monitoring, artwork, track details, and local playback remain.
3. Search: YouTube, Spotify, and SoundCloud adapters; source settings; session/cookie support where needed.
4. Downloads: yt-dlp/FFmpeg integration, unified queue, progress, pause/resume, duplicate handling, and file organization.
5. Library features: playlists, favorites, player queue, lyrics, and remaining accepted interactions.
6. Windows test build: packaging, configuration, and a repeatable test release.

## Current verification

- Windows GitHub Actions workflow runs pytest and Ruff for pull requests and pushes to main.
- PR #15 merged; its workflow result was not returned by the available status query.
- Current Local Music branch requires its own CI result before merge.
- The application is an early development build, not yet the complete first release.

## Deferred beyond the first testable build

Torrent search, advanced lyrics translations, CLI/agent integration, automatic updates, backup/recovery, and detailed visual micro-adjustments.
