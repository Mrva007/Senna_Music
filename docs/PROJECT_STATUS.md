# Senna Music — Project Status

**Current phase:** Concept and product definition  
**Implementation status:** Not started; explicitly not authorized  
**Current milestone:** M0 — Project foundation and concept definition

## Completed

- [x] Repository created: `Mrva007/Senna_Music`.
- [x] Initial project README established.
- [x] Accepted product concept documented.
- [x] Accepted decisions consolidated in a decision log.
- [x] Open questions registered.
- [x] GUI direction documented.
- [x] Local Music accepted as a separate GUI page.
- [x] Shared GUI shell accepted: left navigation and central workspace; navigation can collapse to an icon-only panel.
- [x] Home page structure and global search presentation accepted.
- [x] Complete primary navigation order accepted.
- [x] Local Music, Playlists, Favorites, Connected Services, and Settings page inventories accepted.
- [x] Track-list columns, track actions, multi-selection, sorting, and Track Details contents accepted.
- [x] Compact and expanded Music Player structure and controls accepted.
- [x] Playback Queue placement and playback-state restoration accepted.
- [x] Compact Music Player controls confirmed: Play / Pause, Previous, and Next alongside track information and artwork.
- [x] Shuffle and Repeat remain exclusive to the expanded Music Player; they are not shown in the compact player.
- [x] Compact-player artwork/title click behaviour confirmed: only the dedicated expand button opens the expanded player.
- [x] Modern minimalist visual direction, Windows-following initial theme, and Dark / Light / Automatic theme choices confirmed.
- [x] Left navigation manual and automatic collapse behaviour, Settings central-workspace page, and whole-layout responsiveness confirmed.
- [x] General confirmation dialogs, dual-mode notifications, Connected Services list presentation, and automatic reconnection with manual Retry confirmed.
- [x] Download Queue columns, controls, task ordering, and single-download concurrency accepted.
- [x] Unified download model confirmed: download each permitted track once to the user's chosen folder; offline listening plays that same local file, with no separate offline copy or storage location.
- [x] Independent download destination, Artist / Album / Track folder structure, duplicate-skip behaviour, and format choices confirmed.
- [x] Local Music scanning confirmed: user manually adds folders; Senna Music scans them automatically at startup.
- [x] Missing local files are reconciled by removing their library entries only; files on disk are never deleted or modified by this process.
- [x] Local Music scanning includes all subfolders recursively.
- [x] Added folders are monitored/refreshed automatically in the background while the application is running.
- [x] Newly discovered music files are added to the Local Music library automatically, without per-file confirmation.
- [x] Local Music supported formats confirmed: MP3, M4A, FLAC, WAV, and OGG.
- [x] Audio metadata fields confirmed: title, artist, album, track number, year, and genre.
- [x] Metadata editing uses explicit Save / Cancel; edits are not written until Save.
- [x] Bulk metadata editing for multiple selected tracks confirmed.
- [x] Saved metadata changes are written directly into the original audio file where supported; no automatic backup copy is created.
- [x] Damaged or unreadable local audio files remain visible with a red error indicator beside the track name.
- [x] Retry and Details actions are available for damaged or unreadable local audio files.
- [x] Error Details content confirmed: file name, file location, user-friendly error message, and technical error detail when available.
- [x] Download Queue persistence confirmed: preserve waiting tasks across restarts and resume interrupted active downloads from the last safely saved position when technically supported by the provider/source.
- [x] Playlist deletion behaviour confirmed: deleting a playlist removes only the playlist and its entries; music files and tracks in Local Music or Favorites are unaffected.
- [x] Removing a track from a playlist affects only that playlist entry; the track remains in Local Music, Favorites, and all other playlists, and its local file is not deleted.
- [x] Removing a track from Favorites removes only its Favorites designation; it remains in Local Music and all playlists containing it, and its local file is not deleted.
- [x] Deleting a user-created Favorites collection removes only that collection and its entries; tracks remain in the main Favorites list, Local Music, and any playlists containing them; local files are not deleted.
- [x] Tracks within each user-created Favorites collection can be manually reordered with Drag & Drop; the chosen order is saved persistently.
- [x] The main Favorites list has its own persistent manual order, independent of the order in individual collections.
- [x] The main Favorites list can be temporarily sorted by title, artist, or album without changing its saved manual order.
- [x] Each user-created Favorites collection displays its current track count alongside its name.
- [x] The main Favorites list does not display a total track count alongside its name.
- [x] User-created Favorites collections can be renamed after creation; renaming changes only the collection name and preserves its tracks and saved order.
- [x] User-created Favorites collections do not support custom cover images.
- [x] Favorites collections can be deleted from either the three-dot menu or right-click context menu; both require confirmation and delete only the collection and its entries.
- [x] Favorites collections are displayed alphabetically by name.
- [x] Favorites collections do not have a dedicated search field.
- [x] New Favorites collections can be created through either the **New Collection** button on the Favorites page or the **+** button beside the Favorites heading.
- [x] Both Favorites collection creation entry points open a popup dialog with a collection-name field and **Create** / **Cancel** actions.
- [x] Favorites collection names are unique; attempting to create an existing name is blocked and displays an explanatory message.
- [x] The collection dialog's **Create** button stays disabled until a non-empty name is entered; empty or whitespace-only input is invalid.
- [x] Favorites collection-name uniqueness is case-insensitive; names such as `Rock` and `rock` are duplicates.
- [x] Leading and trailing whitespace is trimmed from a Favorites collection name before validation and duplicate comparison; ` Rock ` is normalized to `Rock`.
- [x] Multiple consecutive spaces between words in a Favorites collection name are preserved as entered; they are not collapsed into one space.
- [x] A duplicate Favorites collection-name validation message appears directly below the name field inside the creation popup.
- [x] Removing a track from a user-created Favorites collection removes it only from that collection; it remains in the main Favorites list and all other Favorites collections containing it. The local audio file is not deleted.
- [x] Playlist tracks can be manually reordered with Drag & Drop; the order is saved persistently. Display sorting by title, artist, or album does not change the saved manual order.
- [x] Download quality selection confirmed: default in Settings with per-download override.

- [x] GUI details confirmed: fixed-width left navigation, page-specific central layouts, standard track-list density, sticky column headers, Grid/List switching for Artists/Albums/Folders, album-card information, empty-state actions, loading indicators, search-history clearing, and keyboard shortcut groups.
- [x] Additional GUI details confirmed: narrow-window navigation collapse and tooltips, active-item styling, adaptive compact-player information, conditional page titles, responsive Grid sizing, search-history dropdown and immediate clearing, customizable shortcuts, and shortcut discoverability.
- [x] GUI visual system confirmed: consistent outline/filled active icon treatment, neutral sans-serif typography (14–15 px), clear typographic hierarchy, balanced spacing, slightly rounded corners, subtle borders without shadows, short subtle animations, and content-driven automatic navigation collapse.

## In progress

- [ ] Continue defining remaining GUI details and unresolved product questions; exact shell dimensions, specific icon assets, detailed visual tokens, precise responsive thresholds, and remaining provider/player behaviours are still open.
- [ ] Define exact shared GUI dimensions after the GUI structure is complete.
- [ ] Define exact quality/bitrate levels and resolve provider-specific playback and download capabilities.
- [ ] Keep approved decisions, proposals, and open questions clearly separated.

## Not started / blocked by concept approval

- Application source code and runtime.
- Provider integrations.
- Playback and download implementation.
- Database and persistence implementation.
- CLI implementation.
- Packaging, installers, and release pipeline.

These are intentionally not started. Do not create application implementation until the owner explicitly approves the start of development after sufficient concept and GUI definition.

## Next action

Continue with the remaining unresolved GUI visual details (exact dimensions, specific icon assets, detailed visual tokens, and precise responsive thresholds). Then resolve provider-specific playback and download capabilities and exact audio quality / bitrate levels. Next, define provider authentication/account setup, CLI and AI-agent integration, settings/system functions, updates, backup/recovery, and installation/distribution. Do not revisit accepted decisions unless the owner requests a change.

- [x] Duplicate-name validation message clears immediately when the entered collection name is changed to a non-duplicate.
- [x] Playlist creation and rename popup, case-insensitive unique names, and duplicate-name validation behaviour confirmed.
- [x] Playlist Add to Playlist actions confirmed for right-click and three-dot menus.
- [x] Multi-select add-to-playlist flow can select an existing playlist or create one without leaving the flow.
- [x] Empty playlists remain visible with a no-tracks message and add option.
- [x] Temporary playlist sort selection is remembered only while that playlist is open; saved manual order remains unchanged.
- [x] Playlist list is displayed alphabetically by name, with a track count beside each playlist.
- [x] Playlist Rename and Delete actions are available through both the three-dot and right-click menus.
- [x] Playlist deletion always requires a confirmation prompt.
- [x] Playlist list ordering finalized: playlists remain alphabetical and cannot be manually reordered; track ordering within each playlist remains independently manual.
- [x] Local Music folder-selection flow includes an explicit **Confirm** action.

- [x] Expanded Music Player layout confirmed: it occupies the central workspace while the left navigation remains visible.
- [x] Playback Queue confirmed as an always-visible right-side column inside the expanded player, with track reordering.
- [x] Lyrics behaviour confirmed: best available source, synchronised-first with plain-text fallback, preferred language and manual selection, manual scrolling with automatic timing, no manual offset, and a clear unavailable-state message.
