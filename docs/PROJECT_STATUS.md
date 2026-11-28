# Senna Music — Project Status

**Current milestone:** Local Music — playback and background monitoring  
**Current version:** 0.1.0 (early development)  
**Implementation:** Authorized by the owner on 2026-11-27  
**Repository:** https://github.com/Mrva007/Senna_Music

## Current GitHub state

- PR #15 (desktop foundation) is merged into `main`.
- PR #16 (recursive Local Music scanning, metadata, persistent indexing, and track list) is merged into `main`.
- PR #16 Windows CI passed on its final head: 7 tests passed and Ruff reported no issues.
- The current implementation adds periodic background library rescanning, local audio playback controls, seeking, volume, track details, and explicit folder confirmation. Its verification is tracked by the current pull request and Windows CI.
- GitHub `main` is the source of truth. No unmerged implementation is considered complete.

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
2. Local Music scanning: merged — folder registration, recursive scan, metadata, persistent track indexing, startup scan, and safe reconciliation.
3. Local Music playback/monitoring: current PR — periodic background rescan, local playback controls, seeking, volume, track details, and explicit folder confirmation.
4. Search: YouTube, Spotify, and SoundCloud adapters; source settings; session/cookie support where needed.
5. Downloads: yt-dlp/FFmpeg integration, unified queue, progress, pause/resume, duplicate handling, and file organization.
6. Library features: playlists, Favorites, player queue, lyrics, and remaining accepted interactions.
7. Windows test build: packaging, configuration, and a repeatable test release.

## Current verification

- Windows GitHub Actions workflow runs pytest and Ruff for pull requests and pushes to main.
- PR #16: pytest passed (7/7) and Ruff passed.
- The current PR's Windows CI is the verification gate for its changes.
- The application is an early development build, not yet the complete first release.

## Deferred beyond the first testable build

Torrent search, advanced lyrics translations, CLI/agent integration, automatic updates, backup/recovery, and detailed visual micro-adjustments.
