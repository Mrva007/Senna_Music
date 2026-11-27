# Senna Music — Project Status

**Current milestone:** Local Music — recursive scan and library list  
**Current version:** 0.1.0 (early development)  
**Implementation:** Authorized by the owner on 2026-11-27  
**Repository:** https://github.com/Mrva007/Senna_Music

## Current GitHub state

- PR #15 (desktop foundation) is merged into `main`.
- PR #15 tests passed (2/2), but its Ruff step failed on three SIM117 transaction-context findings and one I001 import-order finding.
- PR #16 fixes those inherited lint findings and adds the first Local Music scanning milestone.
- Current implementation branch: `feature/local-music-library-scan`.
- PR #16 CI must be green before merge.

## Working foundation

- Standalone, music-only, local-first desktop application.
- Left navigation, central workspace, and bottom compact-player area.
- Home search entry point; Local Music is a separate page.
- Initial online sources: YouTube, Spotify, and SoundCloud.
- Source-specific adapters feed one normalized result model.
- User-selected music storage; one local file supports both in-app and external playback.
- Shared GUI/Core architecture; CLI remains a later interface to the same Core.

## Implementation sequence

1. Desktop foundation: merged — application entry point, navigation shell, SQLite persistence, and CI workflow. Its first CI run passed tests but failed Ruff; the lint findings are corrected in PR #16.
2. Local Music: folder registration is implemented; recursive scanning, metadata, persistent track indexing, automatic startup scan, and track-list UI are in PR #16. Folder monitoring, artwork, track details, and local playback remain.
3. Search: YouTube, Spotify, and SoundCloud adapters; source settings; session/cookie support where needed.
4. Downloads: yt-dlp/FFmpeg integration, unified queue, progress, pause/resume, duplicate handling, and file organization.
5. Library features: playlists, favorites, player queue, lyrics, and remaining accepted interactions.
6. Windows test build: packaging, configuration, and a repeatable test release.

## Current verification

- Windows GitHub Actions workflow runs pytest and Ruff for pull requests and pushes to main.
- PR #15: pytest passed (2 tests); Ruff failed with 4 findings.
- PR #16: CI is the required verification gate; do not merge until both pytest and Ruff pass.
- The application is an early development build, not yet the complete first release.

## Deferred beyond the first testable build

Torrent search, advanced lyrics translations, CLI/agent integration, automatic updates, backup/recovery, and detailed visual micro-adjustments.
