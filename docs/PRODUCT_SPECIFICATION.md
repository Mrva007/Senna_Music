# Senna Music — Product Specification

**Status:** Concept in progress  
**Implementation:** Not authorized  
**Source of truth:** This document, together with the GUI specification, decision log, and open-questions register.

## 1. Product vision

Senna Music is a local-first music downloader and player. Its primary purpose is to help the user find music from supported online sources, download audio files where the source and applicable rights permit it, organize those files in the user's local music collection, and play the local files in Senna Music.

The application retains its full local Music Player, playlists, Favorites, Download Queue, and Local Music library. Online search is a way to discover source items and obtain their source URLs for the local download workflow; online streaming is not the defining purpose of the product.

Senna Music is exclusively for music. Video is out of scope.

## 2. Music providers

Initial providers: Spotify, YouTube Music, and SoundCloud.

The architecture must allow additional music providers to be integrated later without changing the application's fundamental Core.

Provider capabilities are subject to the provider's APIs, licences, terms, and technical restrictions. The application must not bypass DRM or provider restrictions. Playback and download support must be assessed separately for each provider and use case.

## 3. Downloads and offline playback

Senna Music has one unified local-download model; there are no separate download destinations or separate ways of storing music for offline listening.

- Music is downloaded once to the computer folder selected by the user.
- Offline listening means playing those same already-downloaded local files inside Senna Music, without requiring an internet connection.
- There is no separate app-managed offline copy, second storage location, or additional offline download source.
- The same downloaded file can also be played outside Senna Music, where permitted.

The owner confirmed these download and file-organization rules:

- The user selects the destination folder on the computer.
- Files are organized automatically into an Artist / Album / Track folder hierarchy.
- If a target file already exists, the duplicate is skipped; it is not overwritten.
- Format choices: original format when available, MP3, M4A, and FLAC, subject to source availability and applicable rights.
- Download quality uses a default configured in Settings, with an option to override it for an individual download.

Provider capabilities and applicable rights still determine whether a track can be downloaded at all and which formats/qualities are available.

## 4. GUI direction and navigation

The selected GUI direction is the simple option B:
- Left navigation, normally expanded with icons and labels and collapsible to an icon-only panel.
- Central workspace for page content, search, and results.
- Music player at the bottom.
- No unnecessary recommendation or decorative sections.

Senna Music uses the shared GUI structure intended for future applications: a left navigation menu and a central workspace. The structure is consistent across applications; application-specific content appears in the central workspace. Exact dimensions remain open. The left navigation has a fixed width and cannot be resized by dragging its edge; when the application window becomes very narrow it automatically collapses to icons, with item names shown on hover. The active navigation item uses both a changed background and a coloured left-edge line. Central workspace layout is page-specific, and page titles appear only when needed. Artists, Albums, and Folders views support switching between Grid and List. Album cards show artwork, album name, artist, and year. Grid card counts adapt automatically to available workspace width. In narrow windows, the bottom player reduces displayed information but retains essential playback controls.

Accepted left-navigation order:
1. Home
2. Local Music
3. Playlists
4. Favorites
5. Download Queue
6. Connected Services
7. Settings

There is no separate Search navigation item; search is available from Home.

## 5. Home and global search

Home places the shared search at the top, followed by Recently Played, Playlists, and Local Music sections stacked vertically. Sections with no data are hidden.

One integrated search covers Local Music and the three initial online sources: YouTube, Spotify, and SoundCloud. Online sources are searched simultaneously by default, and their results are combined into one list. The user can filter by All Sources or an individual source. Results use a compact list/table rather than large preview cards and show track/title, artist, album when available, and a clearly visible Source column. Search history is retained in a dropdown below the search field and can be cleared immediately without confirmation.

Each online source has its own search adapter because source search, result structure, and URL extraction differ. Adapters normalize results into a common format. A Download action passes the selected result's source URL to the local download workflow, which uses the already-planned yt-dlp and FFmpeg tools where supported. The shared downloader does not imply that every source or every item is downloadable. Source-specific technical restrictions, rights, and legal requirements still apply.

The integrated search is a dedicated music-search interface, not a general-purpose browser. The concept does not assume official provider APIs or OAuth as a prerequisite. The exact non-API search and URL-acquisition method for each source must be technically validated before implementation. This clarification does not authorize DRM circumvention or bypassing access controls.

## 6. Local music collection

- Music files are stored locally on the user's computer.
- The user chooses the storage folder.
- Senna Music uses that location for downloaded music files.
- Local Music is a distinct page with All Tracks, Artists, Albums, and Folders views.

The user manually adds the folders that Senna Music should scan through a folder-selection flow with an explicit **Confirm** action to complete the selection. Scanning is recursive and includes all subfolders. Senna Music automatically scans those folders at startup and continues monitoring them in the background while the application is running. Newly discovered music files are added to the library automatically, without a separate confirmation step. If a previously indexed file has been moved or deleted, the application removes its entry from the library; it does not delete or modify files on disk.

Local Music supports MP3, M4A, FLAC, WAV, and OGG files. Senna Music reads supported audio metadata and allows the user to edit these basic fields: title, artist, album, track number, year, and genre. The editing workflow uses explicit Save / Cancel controls; changes are not written until the user selects Save. Users can bulk-edit metadata for multiple selected tracks. When saved, changes are written directly into the original audio file where the format supports the relevant metadata. Senna Music does not create an automatic backup copy before editing. If a file is damaged or cannot be read, it remains visible in the library with a red error indicator beside its track name rather than being silently omitted. The available actions are Retry (attempt to load the file again) and Details. The Details view shows the file name, file location, a user-friendly error message, and a technical error detail when available.

## 7. Track lists, actions, and Favorites

The standard track list shows Track name, Artist, Album, Duration, and Source, with a small cover-art thumbnail for each track. Clicking a column heading changes sort direction. Track lists use standard, balanced row density, and column headers remain visible while scrolling long lists.

A single click on a track starts playback. Multiple tracks can be selected using Ctrl/Shift-click.

Track actions are available through a right-click context menu and a three-dot menu on each row:
- Play
- Play Next
- Add to Queue
- Add to Playlist
- Add / Remove Favorites
- View Track Details
- Download (when permitted)

Bulk actions for selected tracks:
- Add to Queue
- Add to Playlist
- Add / Remove Favorites
- Download (when permitted)

Track Details shows track name, artist, album, duration, source, file format, file location, and track artwork.

Favorites supports favourite tracks and user-created collections. A new collection can be created either with a **New Collection** button on the Favorites page or with a **+** button beside the Favorites heading. Selecting either entry point opens a popup dialog containing a collection-name field and **Create** / **Cancel** actions. Collection names must be unique: if the entered name already exists, creation is blocked and the user sees a message that the name already exists directly below the name field inside the creation popup. The message disappears immediately when the user edits the name so that it is no longer a duplicate. The **Create** button remains disabled until the name field contains a non-empty name; empty or whitespace-only input is invalid. Name comparison is case-insensitive, so names such as `Rock` and `rock` are treated as duplicates and creation is blocked. Leading and trailing whitespace is automatically trimmed before validation and duplicate comparison, so ` Rock ` is normalized to `Rock`. Multiple consecutive spaces between words are preserved as entered and are not collapsed; for example, `Rock   Classics` remains `Rock   Classics`. Each user-created Favorites collection displays its current track count alongside its name (for example, `Rock Classics (24)`). The main Favorites list does not display a total track count alongside its name. The main Favorites list supports its own manually arranged track order, saved persistently and independently of the order in individual user-created Favorites collections. The main Favorites list can also be temporarily sorted by track title, artist, or album. Temporary sorting does not change its saved manual order.  Tracks within each user-created Favorites collection can be manually reordered by drag and drop, and the chosen order is saved persistently. Removing a track from a user-created Favorites collection removes it only from that collection. The track remains in the main Favorites list and in every other Favorites collection that contains it; the local audio file is not deleted. Removing a track from the main Favorites list removes only its Favorites designation; the track remains in Local Music and every playlist containing it, and its local audio file is not deleted. Deleting a user-created Favorites collection removes only that collection and its entries; tracks remain in the main Favorites list, Local Music, and any playlists containing them, and local audio files are not deleted. Users can rename a user-created Favorites collection after creation; renaming changes only its name and does not affect its tracks or their saved order. User-created Favorites collections do not support custom cover images. User-created Favorites collections are displayed alphabetically by name. The Favorites collections view does not include a dedicated collection-search field. A collection can be deleted either through its three-dot menu or by right-clicking it; both paths show a confirmation prompt. Deletion removes only the collection and its entries; tracks remain in the main Favorites list, Local Music, and any playlists containing them, and local audio files are not deleted.

## 8. GUI and CLI

The application has two interfaces:

### GUI
The standard graphical interface.

### CLI
A command interface for controlling the application and supporting future AI-agent integration. Intended operations include search, playback, downloads, and task monitoring, subject to permissions.

Both interfaces use the same Core and the same permission system. There must not be two independent permission systems. Keyboard shortcuts cover playback (Play/Pause, Previous, Next), focusing Search, navigation between main pages, volume/Mute, and displaying/managing Playback Queue. Users can customize shortcuts through Settings; shortcuts are discoverable both in Settings and in relevant menus/tooltips beside the associated functions. Empty pages or sections show a message with a clear next-action button. Loading states use Skeleton and Spinner indicators, with a Progress Bar when progress is known.

Shared visual system: use consistent outline icons for normal navigation items and filled icons for active items; a modern neutral sans-serif font with standard 14–15 px text and clear typographic hierarchy; balanced spacing; slightly rounded corners; subtle borders without shadows; and short, subtle animations. Navigation automatically collapses according to the space required by content. Exact dimensions, icon asset selection, detailed visual tokens, and precise responsive thresholds remain open.

CLI commands, API contracts, and permission details remain open.

## 9. User profiles

The first version starts with one user profile. A multi-user system is not required for the initial version.

## 10. Download queue

There is one shared download queue for Spotify, YouTube Music, and SoundCloud.

Accepted columns:
- Status
- Track
- Artist
- Service / Source
- Progress
- File size
- Estimated remaining time

Accepted controls:
- Start
- Pause / Resume
- Cancel
- Retry
- Pause All
- Resume All

Queue behaviour:
- Drag & Drop reordering changes task priority without interrupting the active download.
- Newly added tasks go to the end of the queue.
- Only one download runs at a time.
- The queue is preserved when the application closes. Waiting tasks remain queued after restart.
- If an active download was interrupted, Senna Music resumes it from the last safely saved position when the provider/source technically supports resuming. If resuming is not supported, the task remains available for a safe retry; the application must not claim that partial progress can be resumed.

No separate Download History page is planned; the Download Queue is for current and waiting tasks.

## 11. Music player and Playback Queue

The bottom player is compact by default and can be expanded using a dedicated button.

Compact player information:
- Cover artwork
- Track name
- Artist
- Album
- Favorite button

The expanded player occupies the central workspace while the left navigation remains visible. Its main area includes large cover artwork, track information, playback controls, progress bar, volume control, Shuffle / Repeat, and available lyrics below the track information. Playback Queue is displayed in a dedicated, always-visible right-side column within the expanded player and supports track reordering.

Lyrics use the best available source, preferring synchronised lyrics and automatically falling back to plain lyrics. Users set a preferred lyrics language in Settings and may change it manually. Translated lyrics are deferred beyond the first-version priority. During playback, synchronised lyrics follow the current line while still allowing manual scrolling; timing is automatic and users cannot manually offset it. When lyrics are unavailable, show a clear message and the reason when known. Provider-specific availability remains subject to each provider's capabilities and terms.

Controls:
- Play / Pause
- Previous / Next
- Shuffle
- Repeat: Off / All / One
- Volume
- Mute

Volume uses a slider. Repeat cycles Off → All → One → Off. The progress bar supports click and drag seeking.

Playback Queue is displayed inside the expanded player and supports track reordering.

When the application closes, it saves the last played track, playback position, and Playback Queue for restoration at the next launch.

## 12. Playlists

The user manages playlists:
- Create, rename, and delete playlists. Playlist entries are displayed alphabetically by playlist name, and each playlist displays its current track count alongside its name. The playlist list itself cannot be manually reordered; manual Drag & Drop ordering applies to tracks within an individual playlist.
- Rename and Delete are available through both the playlist's three-dot menu and right-click context menu. Deleting a playlist always requires a confirmation prompt.
- Add and remove tracks.
- Reorder tracks manually using Drag & Drop; the chosen order is saved persistently.
- Temporarily sort a playlist by title, artist, or album without changing its saved manual order. The selected sort is remembered only while that playlist remains open.
- Play an entire playlist.

Creating a playlist opens a popup with a playlist-name field and **Create** / **Cancel** actions, following the accepted Favorites collection dialog pattern. Playlist names must be unique, with case-insensitive comparison. If the entered name is a duplicate, a validation message appears below the name field and disappears immediately when the user edits the name to a non-duplicate. Renaming a playlist uses the same popup and validation rules as creation.

Tracks can be added to a playlist from the right-click context menu or the row's three-dot menu through **Add to Playlist**. When multiple tracks are selected, the user can choose an existing playlist or create a new one within the same flow, without leaving the add-to-playlist process. An empty playlist remains visible and displays a message that it has no tracks yet, with an option to add tracks.

Removing a track from Favorites removes only its Favorites designation; the track remains in Local Music and every playlist containing it, and its local audio file is not deleted. Removing a track from a playlist removes only that entry from the current playlist. The track remains in Local Music, Favorites, and every other playlist; its local audio file is not deleted. Deleting a playlist removes only that playlist and its playlist entries. It never deletes the underlying music files and never removes the tracks from Local Music or Favorites. All playlists are accessed through the single Playlists navigation destination. Individual playlists are not separate permanent navigation items.

Automatic collection cataloguing by artist, album, and genre is not part of the agreed concept.

## 13. Explicit product constraints

- Music only; no video functionality.
- No DRM bypass or circumvention of provider restrictions.
- Provider integrations must respect APIs, licences, and terms.
- GUI and CLI share one Core and one permission system.
- Do not add unapproved features.
- Do not begin application implementation until the concept and GUI are sufficiently defined and the owner explicitly approves development.


## 14. Provider connection, source selection, and playback rules

- Users connect each supported service through its official sign-in flow, using OAuth or another authentication method supported by that provider.
- Senna Music plays a track inside the application when the provider permits in-app playback under its APIs, capabilities, licences, and terms.
- If in-app playback is not permitted, Senna Music offers to open the track in the provider's official service.
- If the same track is available from multiple connected services, show all available sources.
- Users can choose a preferred/main music service in Settings.
- If a service disconnects or loses connection during playback, Senna Music attempts to reconnect automatically and offers Retry if that attempt fails.
- If the current service cannot play a track and another source is available, switching to that source requires user confirmation.
- Download an audio file only when the service or source officially permits downloading that file. No restriction, DRM, or provider limitation may be bypassed.
- These are general product rules. Exact playback, authentication, offline, and download capabilities must be checked separately for Spotify, YouTube Music, SoundCloud, and any future provider; no capability is assumed merely because a provider is listed.


## 15. Provider capability and policy research — 27 November 2026

**Research status only.** These findings are not new owner-approved product decisions and do not silently revise D-155–D-162. They identify compatibility blockers that must be resolved before provider integration work.

### Spotify

- The Web Playback SDK can stream Spotify content inside a web application, but it requires a Spotify Premium account. Spotify's developer policy says streaming through the Spotify Platform is only available to Premium subscribers.
- Spotify's policy explicitly prohibits creating a product or service integrated with streams or content from another service. This appears to conflict with Senna Music's planned combined multi-provider playback/source experience.
- Spotify also prohibits voice-enabled third-party apps that let users control Spotify by voice. This matters if voice control is ever added to Senna Music.
- Spotify's developer policy also restricts commercial streaming applications. The exact eligibility of Senna Music's intended distribution/use must be clarified with Spotify.
- No Spotify audio-file download/offline-copy capability is approved by the reviewed developer API documentation.
- **Status:** Do not implement Spotify as an in-app stream in the combined multi-provider player without written clarification/permission from Spotify. Premium is required for the Web Playback SDK.

Official sources:
- https://developer.spotify.com/policy
- https://developer.spotify.com/documentation/web-playback-sdk
- https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback

### YouTube Music / YouTube

- The reviewed official Google documentation provides the YouTube Data API and YouTube IFrame Player API; it does not document an official YouTube Music audio-only playback API.
- The IFrame Player API embeds and controls a YouTube video player, not a replaceable audio-only player. The player and its required controls/branding must remain compliant with YouTube's rules.
- YouTube API policies prohibit extracting/separating audio tracks, downloading content for offline playback outside the YouTube Premium experience, and allowing background playback of the embedded YouTube player (including when the API service is minimized or closed).
- Google's policy guide gives a search engine listing YouTube videos alongside other platforms, with clear source distinction, as an example of independent value. That does not grant permission to extract audio or provide background/offline playback.
- **Status:** YouTube results may be investigated as clearly attributed discovery links, but an in-app audio-only/background player and app-managed audio downloads are not supported by the reviewed official API rules. External playback through the official YouTube Music service is the safe provisional route.

Official sources:
- https://developers.google.com/youtube/iframe_api_reference
- https://developers.google.com/youtube/terms/developer-policies-guide
- https://developers.google.com/youtube/terms/developer-policies

### SoundCloud

- SoundCloud API authentication uses OAuth 2.1 with PKCE. API access requires a registered application and current registration/credential requirements must be met.
- The API can provide a stream URL for tracks that are available for off-platform streaming. Track access must be checked: playable, preview, or blocked. Creator restrictions, paywalls, and geographic restrictions can prevent streaming.
- SoundCloud's API Terms of Use prohibit using its API to create an alternative on-demand service aggregating user content from multiple uploaders, or a playback experience aggregating SoundCloud content with other services (the terms give SoundCloud with YouTube as an example), unless the relevant content is explicitly licensed for that use.
- The API Terms prohibit file-save functionality, persistent caching/downloads, and offline access to API user content, even where an uploader enables downloads on SoundCloud's own platform. Session-only caching is narrowly permitted for operation during that session.
- SoundCloud's public API guidance says public API use is generally not available for commercial use cases; the API Terms list only specific acceptable commercial cases and reserve approval discretion to SoundCloud.
- **Status:** Technically streamable tracks exist, but the Senna Music multi-provider/on-demand aggregation model requires explicit licensing/approval from SoundCloud before implementation. Do not use the API to download or store SoundCloud content.

Official sources:
- https://developers.soundcloud.com/docs
- https://developers.soundcloud.com/docs/api/terms-of-use
- https://help.soundcloud.com/hc/en-us/articles/115003446727-SoundCloud-Public-APIs

### Overall compatibility conclusion

Historical conclusion for the earlier API-based multi-provider streaming concept: Spotify and SoundCloud API terms contain cross-service aggregation restrictions, and YouTube's reviewed APIs do not provide the desired audio-only/background/offline playback model. This conclusion applies to those API/streaming approaches, not automatically to the now-approved local-first search/downloader concept. The latter requires separate source-by-source technical and rights validation, as described below.


## Local-first search and future sources — owner clarification

The product direction was clarified after the initial provider playback research: Senna Music is primarily a local downloader and player, not a multi-service streaming platform. The existing Music Player remains in scope for playing the user's local music.

The initial integrated search scope is YouTube, Spotify, and SoundCloud, searched in parallel and presented in one source-labelled list. Search adapters are source-specific; download processing remains shared through yt-dlp and FFmpeg where supported. The earlier API/streaming compatibility findings describe the official API and playback routes that were researched; they do not, by themselves, establish that every page-based search or download method is technically possible or legally permitted. Those methods require separate source-by-source validation. No API, login, streaming, or download permission should be assumed.

Torrent search is a future extension only. It is not part of the initial version and must be designed as an additional source adapter, limited to lawful content and use.
