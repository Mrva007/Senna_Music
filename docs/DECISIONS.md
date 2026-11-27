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
| D-079 | Selecting either Favorites collection creation entry point opens a popup dialog with a name field and **Create** / **Cancel** actions. | Accepted |
| D-080 | Favorites collection names must be unique. If a user tries to create a collection with a name that already exists, creation is blocked and the application displays a message that the name already exists. | Accepted |
| D-081 | The Create button in the Favorites collection popup remains disabled until the name field contains a non-empty name; an empty or whitespace-only value is not valid. | Accepted |
| D-082 | Favorites collection names are compared without regard to letter case; names such as `Rock` and `rock` are duplicates, and creation is blocked. | Accepted |
| D-083 | Leading and trailing whitespace is trimmed from a Favorites collection name before validation and duplicate comparison; for example, ` Rock ` is normalized to `Rock`. | Accepted |
| D-084 | Multiple consecutive spaces between words in a Favorites collection name are preserved as entered; they are not collapsed into a single space. | Accepted |
| D-085 | When a duplicate Favorites collection name is entered, the validation message is displayed directly below the name field inside the creation popup. | Accepted |
| D-086 | The duplicate-name validation message disappears immediately when the user edits the collection name so that it is no longer a duplicate. | Accepted |

| D-087 | Creating a playlist opens a popup dialog with a playlist-name field and **Create** / **Cancel** actions, following the accepted Favorites collection creation-dialog pattern. | Accepted |
| D-088 | Playlist names must be unique; duplicate comparison is case-insensitive. | Accepted |
| D-089 | When a duplicate playlist name is entered, the validation message appears below the name field and clears immediately when the user edits the name to a non-duplicate. | Accepted |
| D-090 | Renaming a playlist uses the same popup and name-validation rules as playlist creation. | Accepted |
| D-091 | Tracks can be added to a playlist from either the right-click context menu or the row's three-dot menu using **Add to Playlist**. | Accepted |
| D-092 | When multiple tracks are selected, the user can add them to an existing playlist or create a new playlist within the same flow, without leaving the add-to-playlist process. | Accepted |
| D-093 | An empty playlist remains visible and displays a message that it has no tracks yet, together with an option to add tracks. | Accepted |
| D-094 | A playlist's temporary sort selection is remembered only while that playlist remains open; temporary sorting never changes its saved manual order. | Accepted |

| D-095 | Playlists are displayed alphabetically by playlist name. | Accepted |
| D-096 | Each playlist displays its current track count alongside its name. | Accepted |
| D-097 | Playlist Rename and Delete actions are available through both the three-dot menu and the right-click context menu. | Accepted |
| D-098 | Deleting a playlist always requires confirmation before the playlist and its entries are deleted. | Accepted |
| D-099 | The playlist list itself remains alphabetically ordered by playlist name; users cannot manually reorder playlists. This does not affect the separately accepted manual ordering of tracks inside each playlist. | Accepted |
| D-100 | When adding folders to Local Music, the folder-selection flow provides an explicit **Confirm** action to complete the selection. | Accepted |

| D-101 | The expanded Music Player occupies the central workspace while the left navigation remains visible. | Accepted |
| D-102 | In the expanded Music Player, Playback Queue is displayed as a right-side column and remains visible. | Accepted |
| D-103 | In the expanded Music Player, available lyrics are displayed below the track information. | Accepted |
| D-104 | The compact Music Player includes Play / Pause, Previous, and Next controls alongside the track information and artwork. | Accepted |
| D-105 | Shuffle and Repeat controls are not displayed in the compact Music Player; they remain available in the expanded player. | Accepted |
| D-106 | Clicking the compact player's cover artwork or track name does not open the expanded player; the dedicated expand button is the entry point. | Accepted |
| D-107 | Senna Music uses a modern, minimalist visual style. | Accepted |
| D-108 | On first launch, the application theme follows the Windows theme. | Accepted |
| D-109 | Theme choices include Dark, Light, and Automatic. | Accepted |
| D-110 | Left navigation supports both manual collapse/expand and automatic adaptation to the application window size. | Accepted |
| D-111 | Settings opens as a page in the central workspace. | Accepted |
| D-112 | Notifications use both brief on-screen messages and a notification panel containing notification history. | Accepted |
| D-113 | General action confirmations use a small, centered popup dialog. | Accepted |
| D-114 | The complete GUI layout adapts to the application window size. | Accepted |
| D-115 | Connected Services presents providers in a list with their connection status and available actions. | Accepted |
| D-116 | When a provider is unavailable or its connection is interrupted, Senna Music displays the status and automatically attempts reconnection, while also offering a retry action. | Accepted |


| D-117 | The left navigation has a fixed width; users cannot resize it by dragging its edge. | Accepted |
| D-118 | Central workspace content layout is page-specific and may differ between pages. | Accepted |
| D-119 | Track lists use the standard, balanced row density. | Accepted |
| D-120 | Track-list column headers remain visible while scrolling long lists. | Accepted |
| D-121 | Artists, albums, and folders views can switch between Grid and List layouts. | Accepted |
| D-122 | Album cards show cover artwork, album name, artist, and year. | Accepted |
| D-123 | Empty pages or sections show a message and a clear action button for the next step. | Accepted |
| D-124 | Loading states may use Skeleton and Spinner indicators; show a Progress Bar when progress is known. | Accepted |
| D-125 | Senna Music retains previous searches and provides a way to clear the search history. | Accepted |
| D-126 | Keyboard shortcuts cover playback (Play/Pause, Previous, Next), focusing Search, navigation between main pages, volume/Mute, and displaying/managing Playback Queue. | Accepted |


| D-127 | When the application window becomes very narrow, the left navigation automatically collapses to icons. | Accepted |
| D-128 | In the collapsed icon-only navigation, hovering over an item displays its name in a tooltip. | Accepted |
| D-129 | The active navigation item is indicated by both a changed background and a coloured line along its left edge. | Accepted |
| D-130 | In a narrow application window, the bottom player reduces the amount of displayed information while retaining its essential playback controls. | Accepted |
| D-131 | A central-workspace page title is displayed only when needed; it is not mandatory on every page. | Accepted |
| D-132 | Grid card sizing is responsive: the number of cards per row adjusts automatically to the available workspace width. | Accepted |
| D-133 | Search history appears as a dropdown below the shared search field. | Accepted |
| D-134 | Search history can be cleared immediately without an additional confirmation prompt. | Accepted |
| D-135 | Users can customize keyboard shortcuts through Settings. | Accepted |
| D-136 | Keyboard shortcuts are discoverable both in Settings and in relevant menus/tooltips beside the associated functions. | Accepted |

| D-137 | Navigation icons use a combination: outline icons for normal items and filled icons for active items. | Accepted |
| D-138 | Icon style is consistent throughout the application. | Accepted |
| D-139 | The application uses a modern, neutral sans-serif font. | Accepted |
| D-140 | Standard text size is 14–15 px. | Accepted |
| D-141 | Typography uses a clear hierarchy of sizes and weights for headings and content. | Accepted |
| D-142 | Spacing uses a standard, balanced layout density. | Accepted |
| D-143 | UI elements use slightly rounded corners. | Accepted |
| D-144 | Surfaces and components use subtle borders without shadows. | Accepted |
| D-145 | UI animations are short and subtle. | Accepted |
| D-146 | Navigation automatically collapses according to the space required by the content. | Accepted |

| D-147 | Lyrics are selected from a combination of available sources, prioritising the best available source. | Accepted |
| D-148 | Prefer synchronised lyrics when available; otherwise use plain, non-synchronised lyrics. | Accepted |
| D-149 | If synchronised lyrics are unavailable but plain lyrics are available, display the plain lyrics automatically. | Accepted |
| D-150 | A preferred lyrics language is configurable in Settings, and the user can manually change the language. | Accepted |
| D-151 | Translated lyrics are deferred and are not a priority for the first version. | Accepted |
| D-152 | During playback, synchronised lyrics follow the current line, while the user retains the ability to scroll manually. | Accepted |
| D-153 | Lyrics synchronisation is automatic; users do not manually adjust timing. | Accepted |
| D-154 | When lyrics are unavailable, show a clear message and include the reason when it is known. | Accepted |


| D-155 | Users connect supported music services through each provider's official sign-in flow, using OAuth or another provider-supported authentication method. | Accepted |
| D-156 | Play a track inside Senna Music whenever the provider permits in-app playback under its supported capabilities and terms. | Accepted |
| D-157 | If a provider does not permit in-app playback, offer to open the track in that provider's official service. | Accepted |
| D-158 | When the same track is available from multiple connected services, show all available sources. | Accepted |
| D-159 | Users can choose their preferred/main music service in Settings. | Accepted |
| D-160 | If a service disconnects or loses connection during playback, automatically attempt to reconnect and offer a manual Retry action if reconnection fails. | Accepted |
| D-161 | Switching playback to another available service when the current service cannot play the track requires user confirmation. | Accepted |
| D-162 | Download a track only when the service or source officially permits downloading the audio file; never bypass provider restrictions. | Accepted |

## Change control

- Do not revise an accepted decision without explicit owner approval.
- When a decision changes, preserve the history: mark the old decision as superseded and record the replacement with context.
- Update the relevant specification and project status in the same small PR.
