# Senna Music — Open Questions

Only unresolved topics are listed here. An item becomes accepted only after the owner explicitly confirms a decision and the documentation is updated.

| # | Topic | Status | Notes |
|---:|---|---|---|
| 1 | Exact dimensions and remaining visual details of the GUI shell | Partially resolved | Modern minimalist style, Windows-following initial theme, Dark/Light/Automatic choices, manual and automatic navigation collapse, and general window-responsive layout are accepted. Exact dimensions, icon set, visual tokens, and responsive breakpoints remain open. |
| 2 | Provider connection and account-management details | Partially resolved | Connected Services presentation is accepted as a provider list with status and actions. Authentication, account management, and provider-specific setup details remain open and must respect supported authentication/API models. |
| 3 | Playback rules and capabilities for each provider | Open | Assess separately by provider and use case. |
| 4 | Separate offline storage and retention | Resolved / Not applicable | There is no separate offline copy or offline storage lifecycle. Offline playback uses the same downloaded local files. Provider-specific download eligibility and rights remain governed by provider capabilities and terms. |
| 5 | Audio quality and bitrate selection | Partially resolved | Default quality is configured in Settings, with per-download override. Exact quality/bitrate levels and provider-specific availability remain open. |
| 6 | Download Queue persistence and restart recovery | Resolved | Preserve the queue across restarts. Waiting tasks remain queued; an interrupted active download resumes from its last safely saved position when the provider/source technically supports resuming. |
| 7 | Duplicate handling and files already present on disk | Resolved | Existing target files are skipped; no overwrite. |
| 8 | CLI commands and AI-agent API | Open | Same Core and permission system as GUI. |
| 9 | Application updates and integration/update mechanism | Open | |
| 10 | Backup and recovery of application data | Open | |
| 11 | Technology and architecture | Open | Decide after product and GUI requirements are sufficiently defined. |
| 12 | Installation and distribution | Open | |
| 13 | Detailed Local Music operations | Partially resolved | User manually adds folders through a selection flow with an explicit Confirm action; scanning is recursive through all subfolders, runs at startup, and continues automatically in the background while the app is open. Newly discovered music files are added automatically. Entries for moved/deleted files are removed from the library without touching disk files. Supported formats are MP3, M4A, FLAC, WAV, and OGG. Metadata editing is defined: basic fields (title, artist, album, track number, year, genre), explicit Save / Cancel, bulk editing, and direct writing to the original file without automatic backup where supported. Damaged/unreadable files remain visible with a red error indicator beside the track name. Retry and Details actions are available. |
| 14 | Detailed playlist and Favorites interactions | Resolved | Playlist creation/rename dialogs, case-insensitive unique names, duplicate-name feedback and immediate clearing, Add to Playlist via right-click and three-dot menus, multi-select add/create flow, empty-playlist state, temporary-sort selection lifetime, alphabetical playlist display with no manual reordering, per-playlist track counts, Rename/Delete access through both menus, and mandatory delete confirmation are resolved. Playlist track removal, safe deletion, persistent manual track order, and temporary sorting without changing saved order are resolved. Favorites behaviour is documented, including creation/validation, rename, deletion, ordering, counts, and track-removal rules. |
| 15 | Lyrics availability and technical behaviour | Partially resolved | Presentation is resolved: show available lyrics below track information in the expanded player. Lyrics source, synchronisation, and fallback behaviour remain open. |
| 16 | Provider-specific playback and offline behaviour | Open | Capabilities must be verified per provider and must comply with their terms and restrictions. General connection-loss handling is accepted: show status, attempt automatic reconnection, and offer Retry. |

## Resolution rule

When an item is resolved:
1. Record the approved decision in [DECISIONS.md](DECISIONS.md).
2. Update the relevant specification.
3. Update [PROJECT_STATUS.md](PROJECT_STATUS.md).
4. Remove or mark the item resolved here, without losing useful history.
