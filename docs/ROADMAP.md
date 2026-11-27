# Senna Music — Delivery Roadmap

The roadmap tracks implementation work, not a second copy of the decision log. Accepted product and GUI behaviour remains defined in the existing specifications.

## V1 — First testable Windows application

### 1. Desktop foundation
- [x] Create the implementation branch and initial Python project structure.
- [x] Add the PySide6 application entry point and main window shell.
- [x] Add the agreed navigation destinations and bottom player area.
- [x] Add SQLite persistence for settings and registered music folders.
- [x] Add Windows CI for tests and linting.
- [x] Merge the desktop foundation PR #15.
- [ ] Verify and record the foundation CI result.

### 2. Local Music
- [x] Add and persist music folders.
- [ ] Recursively scan supported audio formats and populate the library (implemented in current PR; pending CI/review).
- [ ] Read and display track metadata and damaged-file states (implemented in current PR; pending CI/review).
- [ ] Start a library scan automatically on application launch (implemented in current PR; pending CI/review).
- [ ] Monitor folders while the application is running.
- [ ] Add cover-art thumbnails, track details, and accepted row/context actions.
- [ ] Implement local playback and the compact/expanded player.
- [ ] Implement explicit folder-selection confirmation and background folder monitoring.

### 3. Integrated search and source sessions
- [ ] Implement the shared search result model and source adapter contract.
- [ ] Implement YouTube search and URL handoff.
- [ ] Implement Spotify track lookup and matching-source resolution.
- [ ] Implement SoundCloud search and URL handoff.
- [ ] Add source enable/disable settings and authenticated session/cookie configuration where required.
- [ ] Preserve the accepted streaming-results, error, filter, sorting, history, and alternative-selection behaviour.

### 4. Downloads
- [ ] Integrate yt-dlp and FFmpeg for supported URLs.
- [ ] Implement the unified Download Queue and progress reporting.
- [ ] Implement pause/resume, retry, cancellation, and restart persistence.
- [ ] Apply destination, format, quality, duplicate, and Artist/Album/Track organization rules.
- [ ] Verify each source adapter independently.

### 5. Library experience
- [ ] Implement playlists and Favorites with the accepted ordering and safe-removal rules.
- [ ] Implement track context menus, bulk actions, and track details.
- [ ] Complete expanded player, playback queue, lyrics fallback, and saved playback state.
- [ ] Complete settings, notifications, keyboard shortcuts, and responsive layouts.

### 6. First Windows test release
- [ ] Add repeatable Windows packaging.
- [ ] Produce a test build and installation/run instructions.
- [ ] Test the complete first-version workflow on the owner's Windows computer.
- [ ] Fix issues found in the test cycle.

## Later milestones

- CLI using the same Core.
- Torrent adapter for lawful content.
- AI-agent integration.
- Backup/recovery and automatic updates.
- Additional polish and optional features.

## Definition of done

A task is complete when its acceptance criteria are met, relevant tests pass, documentation reflects the implementation, and the PR records the verification evidence.
