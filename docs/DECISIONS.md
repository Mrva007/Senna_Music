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

## Change control

- Do not revise an accepted decision without explicit owner approval.
- When a decision changes, preserve the history: mark the old decision as superseded and record the replacement with context.
- Update the relevant specification and project status in the same small PR.
