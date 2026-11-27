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

## In progress

- [ ] Continue defining remaining GUI details and unresolved product questions.
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

Continue defining remaining GUI details and product questions, including exact quality/bitrate levels, provider capabilities, and remaining playlist/Favorites interactions. Playlist deletion is defined: it removes only the playlist and its entries, never music files or tracks in Local Music or Favorites. Deleting a Favorites collection removes only that collection and its entries; tracks remain in the main Favorites list, Local Music, and any playlists containing them. Removing a track from Favorites removes only its Favorites designation. Playlist tracks support persistent manual ordering and temporary display sorting by title, artist, or album. Tracks within Favorites collections support persistent manual ordering. User-created Favorites collections can be renamed without changing their tracks or saved order. The main Favorites list has its own persistent manual order, independent of individual collections, and temporary sorting by title, artist, or album does not change that order. Removing a track from one Favorites collection affects only that collection; it remains in the main Favorites list and other collections containing it. Local Music folder selection, recursive scanning, startup scanning, background monitoring, automatic addition of newly discovered files, missing-file reconciliation, supported audio formats, writing metadata changes into files where supported, basic editable fields, explicit Save / Cancel, bulk editing, no automatic backup, and visibility of damaged files with a red error indicator plus Retry and Details actions are accepted. The unified download/offline-playback model and Settings default with per-download quality override are also accepted. Do not revisit previously accepted decisions unless the owner requests a change.

- [x] Duplicate-name validation message clears immediately when the entered collection name is changed to a non-duplicate.
