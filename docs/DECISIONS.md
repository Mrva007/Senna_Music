# Senna Music — Decision Log

This log records owner-approved product decisions. Proposals and unresolved questions belong in the relevant specification or open-questions register.

| ID | Decision | Status |
|---|---|---|
| D-001 | Senna Music is a standalone music platform inspired by Spotify. | Accepted |
| D-002 | The product is music-only; video is out of scope. | Accepted |
| D-003 | Initial providers are Spotify, YouTube Music, and SoundCloud. | Accepted |
| D-004 | Provider integrations must respect APIs, licences, terms, DRM, and technical restrictions; no circumvention. | Accepted |
| D-005 | Earlier concept: separate in-app offline listening and independent audio-file downloads. | Superseded by D-042; retained for decision history. |
| D-006 | Expected audio formats: MP3, M4A, and FLAC, subject to source and rights. | Accepted |
| D-007 | GUI direction B: left navigation, central workspace, bottom player, simple interface without unnecessary recommendations or decoration. | Accepted |
| D-008 | The user chooses the local storage folder for downloaded music files. | Accepted |
| D-009 | GUI and CLI both use the same Core and permission system. | Accepted |
| D-010 | Start with one user profile; no multi-user system required in the first version. | Accepted |
| D-011 | One shared download queue for the three initial providers, with owner-approved columns and controls. | Accepted |
| D-012 | Reordering download tasks changes priority and does not automatically interrupt an active download. | Accepted |
| D-013 | Bottom player is compact by default and can expand; Playback Queue is inside the expanded player. | Accepted |
| D-014 | Users manually create and manage playlists; no automatic artist/album/genre cataloguing. | Accepted |
| D-015 | No separate download History page; show only current and waiting tasks in Download Queue. | Accepted |
| D-016 | Local Music is a separate GUI page. | Accepted |
| D-017 | Home page places Search at the top, followed by Recently Played, Playlists, and Local Music stacked vertically; empty sections are hidden. | Accepted |
| D-018 | One shared search covers supported online sources and Local Music; results show their source, can be filtered by source, and appear in a list with track name, artist, album, and source. | Accepted |
| D-019 | The shared GUI standard for future applications is a left navigation menu and a central workspace; Senna Music's navigation can collapse to an icon-only panel. | Accepted |
| D-020 | Left navigation order: Home, Local Music, Playlists, Favorites, Download Queue, Connected Services, Settings. Search is accessed from Home, not a separate navigation item. | Accepted |
| D-021 | Local Music contains All Tracks, Artists, Albums, and Folders. Playlists is one destination containing individual playlists. | Accepted |
| D-022 | Favorites supports favourite tracks and user-created collections. | Accepted |
| D-023 | Connected Services is a separate navigation destination with Connect / Disconnect, Account status, Provider settings, and Connection diagnostics. Settings contains General, Audio & Playback, Storage & Downloads, Appearance, and Language. | Accepted |
| D-024 | Track lists show Track name, Artist, Album, Duration, and Source, with a small cover thumbnail. Column-heading clicks toggle sort direction. | Accepted |
| D-025 | A single track click starts playback. Multiple selection uses Ctrl/Shift-click. Track actions appear in both right-click context menus and per-row three-dot menus. | Accepted |
| D-026 | Individual track actions: Play, Play Next, Add to Queue, Add to Playlist, Add / Remove Favorites, View Track Details, and Download (when permitted). | Accepted |
| D-027 | Bulk track actions: Add to Queue, Add to Playlist, Add / Remove Favorites, and Download (when permitted). | Accepted |
| D-028 | Track Details shows Track name, Artist, Album, Duration, Source, File format, File location, and Track artwork. | Accepted |
| D-029 | Download Queue columns: Status, Track, Artist, Service / Source, Progress, File size, Estimated remaining time. Controls: Start, Pause / Resume, Cancel, Retry, Pause All, Resume All. | Accepted |
| D-030 | Download Queue uses Drag & Drop priority ordering; new tasks go to the end; only one download runs at a time. | Accepted |
| D-031 | Compact player shows Cover artwork, Track name, Artist, Album, and Favorite button; it expands via a dedicated button. | Accepted |
| D-032 | Expanded player contains large artwork, track information, playback controls, progress, volume, Shuffle / Repeat, Playback Queue access, and lyrics when available. | Accepted |
| D-033 | Player controls include Play / Pause, Previous / Next, Shuffle, Repeat Off / All / One, Volume, and Mute. Volume uses a slider; Repeat cycles Off → All → One → Off. | Accepted |
| D-034 | Playback Queue appears inside the expanded player and supports track reordering. | Accepted |
| D-035 | Player progress supports click-and-drag seeking. | Accepted |
| D-036 | On application close, save the last played track, playback position, and Playback Queue for restoration on next launch. | Accepted |
| D-037 | Earlier confirmation of two distinct download capabilities. | Superseded by D-042; retained for decision history. |
| D-038 | The user selects the computer folder used as the destination for independent audio-file downloads. | Accepted |
| D-039 | Organize independently downloaded files automatically using an Artist / Album / Track folder hierarchy. | Accepted |
| D-040 | If a downloaded file already exists at the destination, skip the duplicate; do not overwrite it. | Accepted |
| D-041 | Supported format choices are original format when available, MP3, M4A, and FLAC, subject to source availability and rights. | Accepted |
| D-042 | Use one unified download/storage model: download a permitted track once to the user's chosen local folder. Offline listening in Senna Music plays that same downloaded local file; there is no separate offline copy, storage location, or second download source. | Accepted; supersedes D-005 and D-037. |
| D-043 | Local Music scanning is user-directed: the user manually adds the folders Senna Music should scan. | Accepted |
| D-044 | Download quality has a default setting in Settings, with an option to override quality for an individual download, subject to source capabilities and rights. | Accepted |

| D-045 | Automatically scan all folders manually added by the user when Senna Music starts. | Accepted |
| D-046 | If a previously indexed local music file is moved or deleted, remove its library entry; never delete or modify the file on disk as part of this reconciliation. | Accepted |
| D-047 | Scan manually added Local Music folders recursively, including all subfolders. | Accepted |
| D-048 | After startup scanning, continue refreshing/monitoring manually added folders automatically in the background while Senna Music is running. | Accepted |
| D-049 | Automatically add newly discovered music files in the scanned folders to the Local Music library; no per-file confirmation is required. | Accepted |
| D-050 | Local Music supports MP3, M4A, FLAC, WAV, and OGG audio files. | Accepted |
| D-051 | Users can edit supported audio metadata in Senna Music, and changes are written into the audio file itself where the format supports the relevant metadata. | Accepted |
| D-052 | Damaged or unreadable local audio files remain visible in the library with an error indication. | Accepted |
| D-053 | Local Music metadata editing exposes the basic fields: title, artist, album, track number, year, and genre. | Accepted |
| D-054 | Metadata edits use an explicit Save / Cancel workflow; changes are not written until the user saves. | Accepted |
| D-055 | Users can bulk-edit metadata for multiple selected tracks. | Accepted |
| D-056 | Metadata edits write directly to the original audio file where supported; Senna Music does not create an automatic backup copy before editing. | Accepted |
| D-057 | Damaged or unreadable Local Music files show a red error indicator beside the track name. | Accepted |
| D-058 | A damaged or unreadable Local Music file offers a Retry action to attempt loading it again. | Accepted |
| D-059 | A damaged or unreadable Local Music file offers a Details action to display information about the error. | Accepted |
| D-060 | The error Details view shows the file name, file location, a user-friendly error message, and a technical error detail when available. | Accepted |
| D-061 | Preserve the Download Queue across application restarts. Waiting tasks remain queued; an interrupted active download resumes from its last safely saved position when the provider/source technically supports resuming. | Accepted |
| D-062 | Deleting a playlist removes only the playlist and its playlist entries; it never deletes the underlying music files or removes tracks from Local Music or Favorites. | Accepted |
| D-063 | Removing a track from a playlist removes only that playlist entry. The track remains in Local Music, Favorites, and every other playlist; its local audio file is not deleted. | Accepted |
| D-064 | Removing a track from Favorites removes only its Favorites designation. The track remains in Local Music and every playlist containing it; its local audio file is not deleted. | Accepted |
| D-065 | Playlist tracks can be manually reordered by drag and drop, and the chosen order is saved persistently. Users may also sort the displayed list by title, artist, or album without changing the saved manual order. | Accepted |
| D-066 | Deleting a Favorites collection removes only the collection and its collection entries. Tracks remain in the main Favorites list, Local Music, and any playlists containing them; local audio files are not deleted. | Accepted |
| D-067 | Tracks within each user-created Favorites collection can be manually reordered by drag and drop, and the chosen order is saved persistently. | Accepted |
| D-068 | Removing a track from a user-created Favorites collection removes it only from that collection. The track remains in the main Favorites list and in every other Favorites collection that contains it; the local audio file is not deleted. | Accepted |
| D-069 | The main Favorites list supports its own manually arranged track order, saved persistently and independently of the order in individual user-created Favorites collections. | Accepted |
| D-070 | The main Favorites list can also be temporarily sorted by track title, artist, or album. Temporary sorting does not change its saved manual order. | Accepted |
| D-071 | Each user-created Favorites collection displays its current track count alongside its name. | Accepted |
| D-072 | The main Favorites list does not display a total track count alongside its name. | Accepted |
| D-073 | Users can rename a user-created Favorites collection after it has been created. Renaming changes only the collection name; its tracks and saved order remain unchanged. | Accepted |
| D-074 | User-created Favorites collections do not support custom cover images. | Accepted |
| D-075 | A user-created Favorites collection can be deleted either from its three-dot menu or by right-clicking the collection; both actions require confirmation. Deletion removes only the collection and its entries, not tracks or local audio files elsewhere. | Accepted |
| D-076 | User-created Favorites collections are displayed alphabetically by collection name. | Accepted |
| D-077 | Favorites collections do not have a dedicated search field. | Accepted |
| D-078 | A new Favorites collection can be created either with a **New Collection** button on the Favorites page or with a **+** button beside the Favorites heading. | Accepted |

## Change control

- Do not revise an accepted decision without explicit owner approval.
- When a decision changes, preserve the history: mark the old decision as superseded and record the replacement with context.
- Update the relevant specification and project status in the same small PR.
