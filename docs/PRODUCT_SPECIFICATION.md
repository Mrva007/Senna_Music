# Senna Music — Product Specification

**Status:** Concept in progress  
**Implementation:** Not authorized  
**Source of truth:** This document, together with the decision log and open-questions register.

## 1. Product vision

Senna Music is a standalone music platform inspired by Spotify.

It is intended to support:
- Discovering and searching for music through online music services.
- Playing music.
- Creating and managing user playlists.
- Downloading music for offline listening inside Senna Music.
- Downloading permitted audio files to the user's computer for use outside the application, for example in a car.

Senna Music is exclusively for music. Video is out of scope.

## 2. Music providers

Initial providers: Spotify, YouTube Music, and SoundCloud.

The architecture must allow additional music providers to be integrated later without changing the application's fundamental Core.

Provider capabilities are subject to the provider's APIs, licences, terms, and technical restrictions. The application must not bypass DRM or provider restrictions. Playback and download support must be assessed separately for each provider and use case.

## 3. Download capabilities

Two distinct capabilities are defined:

1. **Offline listening:** content made available for listening inside Senna Music, subject to provider capabilities and rights.
2. **Audio file download:** downloading audio files only when the source and applicable rights explicitly permit it, for use outside the application.

Expected audio formats are MP3, M4A, and FLAC, depending on the source and available rights. Format and quality selection remain open.

## 4. GUI direction

The selected direction is the simple interface option B:
- Left navigation.
- Central area for search and results.
- Music player at the bottom.
- No unnecessary recommendation or decorative sections.

Detailed navigation, page inventory, and page behaviour remain open. A separate **Local Music** page has been accepted.

## 5. Local music collection

- Music files are stored locally on the user's computer.
- The user chooses the storage folder.
- Senna Music uses that location for downloaded music files.
- Local Music is a distinct page in the GUI.

Further details of local-library scanning, supported file handling, and folder behaviour remain open.

## 6. GUI and CLI

The application has two interfaces:

### GUI
The standard graphical interface.

### CLI
A command interface for controlling the application and supporting future AI-agent integration. Intended operations include search, playback, downloads, and task monitoring, subject to permissions.

Both interfaces use the same Core and the same permission system. There must not be two independent permission systems.

CLI commands, API contracts, and permission details remain open.

## 7. User profiles

The first version starts with one user profile. A multi-user system is not required for the initial version.

## 8. Download queue

There is one shared download queue for Spotify, YouTube Music, and SoundCloud.

Required columns:

| Column | Content |
|---|---|
| Status | Waiting, Downloading, Completed, Failed, etc. |
| Track name | Track title |
| Artist | Artist name |
| Service | Source provider |
| Progress | Download percentage |

The **Service** column is mandatory so the user can always see the source of a download.

Required queue controls:
- Start
- Pause / Resume
- Cancel
- Retry
- Pause All / Resume All
- Drag & Drop reordering to change task priority

Changing task order must not automatically interrupt a download that is already active.

Queue persistence, restart recovery, concurrency, and detailed state transitions remain open.

## 9. Music player

An advanced player is located at the bottom of the GUI and includes:
- Play / Pause
- Next / Previous
- Volume
- Shuffle
- Repeat (single track / entire list)
- Playback Queue
- Reordering tracks in the playback queue

Detailed playback behaviour and provider-specific constraints remain open.

## 10. Playlists

The user manages playlists manually:
- Create
- Rename
- Delete
- Add and remove tracks
- Reorder tracks
- Play an entire playlist

Automatic collection cataloguing by artist, album, and genre is not part of the agreed concept.

## 11. Download history

The simpler option A was selected:
- There is no separate History page.
- Only current and waiting tasks appear in Download Queue.
- Completed downloads do not require a separate history view.

## 12. Explicit product constraints

- Music only; no video functionality.
- No DRM bypass or circumvention of provider restrictions.
- Provider integrations must respect APIs, licences, and terms.
- GUI and CLI share one Core and one permission system.
- Do not add unapproved features.
- Do not begin application implementation until the concept and GUI are sufficiently defined and the owner explicitly approves development.
