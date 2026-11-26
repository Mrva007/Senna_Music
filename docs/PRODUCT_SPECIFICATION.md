# Senna Music — Product Specification

**Status:** Concept in progress  
**Implementation:** Not authorized  
**Source of truth:** This document, together with the GUI specification, decision log, and open-questions register.

## 1. Product vision

Senna Music is a standalone music platform inspired by Spotify.

It is intended to support:
- Discovering and searching for music through online music services.
- Playing music.
- Creating and managing user playlists and favourite collections.
- Downloading permitted audio files to the user's computer.
- Playing those same downloaded local files offline inside Senna Music or outside the application, for example in a car.

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

Senna Music uses the shared GUI structure intended for future applications: a left navigation menu and a central workspace. The structure is consistent across applications; application-specific content appears in the central workspace. Exact dimensions remain open.

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

One shared search covers music from connected/supported online providers and Local Music. Results identify their source and can be filtered by source (All Sources, Spotify, YouTube Music, SoundCloud, or Local Music). Results use a list layout with track name, artist, album, and source.

## 6. Local music collection

- Music files are stored locally on the user's computer.
- The user chooses the storage folder.
- Senna Music uses that location for downloaded music files.
- Local Music is a distinct page with All Tracks, Artists, Albums, and Folders views.

The user manually adds the folders that Senna Music should scan; the application does not automatically scan all folders or subfolders. Further details of metadata handling, supported file handling, and folder behaviour remain open.

## 7. Track lists, actions, and Favorites

The standard track list shows Track name, Artist, Album, Duration, and Source, with a small cover-art thumbnail for each track. Clicking a column heading changes sort direction.

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

Favorites supports favourite tracks and user-created collections.

## 8. GUI and CLI

The application has two interfaces:

### GUI
The standard graphical interface.

### CLI
A command interface for controlling the application and supporting future AI-agent integration. Intended operations include search, playback, downloads, and task monitoring, subject to permissions.

Both interfaces use the same Core and the same permission system. There must not be two independent permission systems.

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

No separate Download History page is planned; the Download Queue is for current and waiting tasks.

## 11. Music player and Playback Queue

The bottom player is compact by default and can be expanded using a dedicated button.

Compact player information:
- Cover artwork
- Track name
- Artist
- Album
- Favorite button

The expanded player includes large cover artwork, track information, playback controls, progress bar, volume control, Shuffle / Repeat, Playback Queue access, and lyrics when available.

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

The user manages playlists manually:
- Create
- Rename
- Delete
- Add and remove tracks
- Reorder tracks
- Play an entire playlist

All playlists are accessed through the single Playlists navigation destination. Individual playlists are not separate permanent navigation items.

Automatic collection cataloguing by artist, album, and genre is not part of the agreed concept.

## 13. Explicit product constraints

- Music only; no video functionality.
- No DRM bypass or circumvention of provider restrictions.
- Provider integrations must respect APIs, licences, and terms.
- GUI and CLI share one Core and one permission system.
- Do not add unapproved features.
- Do not begin application implementation until the concept and GUI are sufficiently defined and the owner explicitly approves development.
