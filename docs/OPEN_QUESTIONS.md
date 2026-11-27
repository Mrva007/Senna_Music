# Senna Music — Open Questions

Only unresolved topics are listed here. An item becomes accepted only after the owner explicitly confirms a decision and the documentation is updated.

| # | Topic | Status | Notes |
|---:|---|---|---|
| 1 | Exact dimensions and visual design of the GUI shell | Open | Navigation order and core page structure are accepted; exact dimensions, icons, visual styling, and responsive behaviour remain open. |
| 2 | Provider connection and account-management details | Open | Must respect each provider's supported authentication and API model. The Connected Services page inventory is accepted. |
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
| 13 | Detailed Local Music operations | Partially resolved | User manually adds folders; scanning is recursive through all subfolders, runs at startup, and continues automatically in the background while the app is open. Newly discovered music files are added automatically. Entries for moved/deleted files are removed from the library without touching disk files. Supported formats are MP3, M4A, FLAC, WAV, and OGG. Metadata editing is defined: basic fields (title, artist, album, track number, year, genre), explicit Save / Cancel, bulk editing, and direct writing to the original file without automatic backup where supported. Damaged/unreadable files remain visible with a red error indicator beside the track name. Retry and Details actions are available. |
| 14 | Detailed playlist and Favorites interactions | Partially resolved | Playlist deletion, track removal, and deletion of Favorites collections are resolved. Deleting a Favorites collection removes only that collection and its entries; tracks remain in the main Favorites list, Local Music, and any playlists containing them. Removing a track from Favorites removes only its Favorites designation; removing a track from a playlist removes only that playlist entry. Playlist tracks support persistent manual ordering and temporary display sorting by title, artist, or album. Tracks within Favorites collections support persistent manual ordering. The main Favorites list has its own persistent manual order, independent of individual collections, and supports temporary sorting by title, artist, or album without changing that saved order. Removing a track from a user-created Favorites collection removes it only from that collection; it remains in the main Favorites list and any other Favorites collections containing it. Each user-created Favorites collection displays its current track count alongside its name; the main Favorites list does not display a total count. Renaming a user-created Favorites collection after creation is resolved: only the collection name changes; its tracks and saved order remain unchanged. Custom cover images are not supported. Deletion is available through both the three-dot menu and right-click context menu, with confirmation; it removes only the collection and its entries. Collections are displayed alphabetically by name and there is no dedicated collection-search field. New collections can be created through either the **New Collection** button on the Favorites page or the **+** button beside the Favorites heading. Either entry point opens a popup dialog with a collection-name field and **Create** / **Cancel** actions. Collection names must be unique; an existing name blocks creation and produces a message that the name already exists. The **Create** button remains disabled until the name field contains a non-empty value; empty or whitespace-only input is invalid. Name comparison is case-insensitive: `Rock` and `rock` are treated as the same name. Leading and trailing whitespace is trimmed before validation and duplicate comparison, so ` Rock ` is normalized to `Rock`. Multiple consecutive spaces between words are preserved as entered and are not collapsed; for example, `Rock   Classics` remains `Rock   Classics`. Other editing and collection-management interactions remain open. |
| 15 | Lyrics behaviour | Open | Show lyrics in expanded player when available; source, synchronisation, and fallback behaviour remain open. |
| 16 | Provider-specific playback and offline behaviour | Open | Capabilities must be verified per provider and must comply with their terms and restrictions. |

## Resolution rule

When an item is resolved:
1. Record the approved decision in [DECISIONS.md](DECISIONS.md).
2. Update the relevant specification.
3. Update [PROJECT_STATUS.md](PROJECT_STATUS.md).
4. Remove or mark the item resolved here, without losing useful history.
