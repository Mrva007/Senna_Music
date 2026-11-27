# Senna Music — GUI Specification

**Status:** Partially defined; detailed GUI definition remains in progress.  
**Implementation:** Not authorized.

## 1. Accepted overall layout

The selected GUI direction is the simple option B:

- Left-side navigation.
- Central workspace for page content, search, and results.
- Music player anchored at the bottom.
- Avoid unnecessary recommendations and decorative sections.

The left navigation is normally expanded with icons and labels. The user can collapse it to a narrow icon-only panel and expand it again.

## 2. Shared application workspace standard

Senna Music follows the shared GUI structure intended to be reused across future applications:

- A left-side navigation menu.
- A central workspace where the selected page and its content are displayed.

The structure and dimensions should remain consistent across applications; application-specific content and functions occupy the central workspace. Exact dimensions are not yet defined.

## 3. Accepted navigation

The accepted left-navigation order is:

1. Home
2. Local Music
3. Playlists
4. Favorites
5. Download Queue
6. Connected Services
7. Settings

There is no separate Search navigation item. Search is available from the Home page.

## 4. Accepted Home page and global search

The Home page uses a vertical layout:

1. Shared search at the top.
2. Recently Played section.
3. Playlists section.
4. Local Music section.

The sections below Search are stacked vertically, one after another. A section is displayed only when it has data; empty sections are hidden.

One shared search covers music available through connected/supported online providers and Local Music. Each result visibly identifies its source: Spotify, YouTube Music, SoundCloud, or Local Music. Results can be filtered by source, including All Sources. Results use a list layout, not cards, and each row shows track name, artist, album, and source.

## 5. Accepted page contents and behaviour

### Local Music

Local Music is a separate page with these views:

- All Tracks
- Artists
- Albums
- Folders

### Playlists

Playlists is one navigation destination containing the user's playlists. Individual playlists are not separate permanent navigation items. The playlist list is displayed alphabetically by playlist name, and each playlist shows its current track count beside its name. Users cannot manually reorder the playlist list; this is separate from the persistent manual Drag & Drop ordering of tracks within an individual playlist. Both the three-dot menu and right-click context menu provide Rename and Delete actions. Delete always opens a confirmation prompt before removing the playlist and its entries. Creating a playlist opens a popup with a playlist-name field and **Create** / **Cancel** actions, following the accepted Favorites collection dialog pattern. Playlist names must be unique using case-insensitive comparison. A duplicate-name message appears below the name field and clears immediately when the entered name is edited to a non-duplicate. Renaming uses the same popup and validation rules as creation. Tracks can be added from either the right-click context menu or the row's three-dot menu through **Add to Playlist**. For multiple selected tracks, the user can choose an existing playlist or create a new one without leaving the add-to-playlist flow. An empty playlist remains visible and shows a no-tracks-yet message with an option to add tracks. Tracks can be manually reordered with Drag & Drop; the selected order is saved persistently. Users can temporarily sort by title, artist, or album without changing the saved manual order; the selected sort is remembered only while that playlist remains open. Removing a track from a playlist removes only that entry from the current playlist; the track remains in Local Music, Favorites, and every other playlist, and its local audio file is not deleted. Deleting a playlist removes only the playlist and its entries; it never deletes the underlying music files or removes tracks from Local Music or Favorites.

### Favorites

Favorites supports favourite tracks and user-created collections. A new collection can be created either with a **New Collection** button on the Favorites page or with a **+** button beside the Favorites heading. Selecting either entry point opens a popup dialog containing a collection-name field and **Create** / **Cancel** actions. Collection names must be unique. If the entered name already exists, the collection is not created and the dialog displays a message that the name already exists directly below the name field and disappears immediately when the user edits the name so that it is no longer a duplicate. The **Create** button remains disabled until the field contains a non-empty name; an empty or whitespace-only value is invalid. Name comparison is case-insensitive, so names such as `Rock` and `rock` are treated as duplicates and creation is blocked. Leading and trailing whitespace is automatically trimmed before validation and duplicate comparison, so ` Rock ` is normalized to `Rock`. Multiple consecutive spaces between words are preserved as entered and are not collapsed; for example, `Rock   Classics` remains `Rock   Classics`. Each user-created Favorites collection displays its current track count alongside its name (for example, `Rock Classics (24)`). The main Favorites list does not display a total track count alongside its name. The main Favorites list supports its own manually arranged track order, saved persistently and independently of the order in individual user-created Favorites collections. The main Favorites list can also be temporarily sorted by track title, artist, or album. Temporary sorting does not change its saved manual order.  Tracks within each user-created Favorites collection can be manually reordered by drag and drop, and the chosen order is saved persistently. Removing a track from a user-created Favorites collection removes it only from that collection. The track remains in the main Favorites list and in every other Favorites collection that contains it; the local audio file is not deleted. Removing a track from the main Favorites list removes only its Favorites designation; the track remains in Local Music and every playlist containing it, and its local audio file is not deleted. Deleting a user-created Favorites collection removes only that collection and its entries; tracks remain in the main Favorites list, Local Music, and any playlists containing them, and local audio files are not deleted. Users can rename a user-created Favorites collection after creation; renaming changes only its name and does not affect its tracks or their saved order. User-created Favorites collections have no custom cover-image option. Collections are displayed alphabetically by name. There is no dedicated search field for Favorites collections. The collection's three-dot menu and its right-click context menu both provide Delete; either path opens the same confirmation prompt. Deletion removes only the collection and its entries, never the underlying audio files or tracks in the main Favorites list, Local Music, or playlists.

### Download Queue

Download Queue is a separate page in the left navigation. Its accepted columns are:

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

Tasks can be reordered with Drag & Drop. Reordering must not interrupt the active download. New tasks are added to the end of the queue. Only one download runs at a time.

No separate download-history page is planned.

### Connected Services

Connected Services is a separate navigation destination and includes:

- Connect / Disconnect
- Account status
- Provider settings
- Connection diagnostics

### Settings

Accepted Settings categories:

- General
- Audio & Playback
- Storage & Downloads
- Appearance
- Language

## 6. Accepted track-list behaviour

The standard track list is used across Local Music, search results, playlists, and Favorites unless a page-specific requirement says otherwise.

- A single click on a track starts playback immediately.
- Multiple tracks can be selected using Ctrl/Shift-click.
- Track actions are available through both a right-click context menu and a three-dot menu on each row.
- Accepted individual actions: Play, Play Next, Add to Queue, Add to Playlist, Add / Remove Favorites, View Track Details, and Download (when permitted).
- Accepted bulk actions: Add to Queue, Add to Playlist, Add / Remove Favorites, and Download (when permitted).

Track-list columns:

- Track name
- Artist
- Album
- Duration
- Source

A small cover-art thumbnail appears with each track. Clicking a column heading changes sorting direction (ascending/descending).

Track Details displays:

- Track name
- Artist
- Album
- Duration
- Source
- File format
- File location
- Track artwork

## 7. Accepted Music Player

### Compact player

The bottom player is compact by default and can be expanded using a dedicated expand button. It displays:

- Cover artwork
- Track name
- Artist
- Album
- Favorite button
- Play / Pause
- Previous
- Next

Shuffle and Repeat controls are not shown in the compact player; they are available in the expanded player.

The progress bar supports click and drag seeking.

### Expanded player

The expanded player occupies the central workspace; the left navigation remains visible.

The main player area contains:
- Large cover artwork
- Track information
- Playback controls
- Progress bar
- Volume control
- Shuffle / Repeat
- Lyrics below the track information, when available

Playback Queue is displayed in a dedicated right-side column within the expanded player and remains visible. The queue supports reordering tracks.

The expanded player does not include a separately accepted Track Details section.

Controls:

- Play / Pause
- Previous / Next
- Shuffle
- Repeat: Off / All / One
- Volume
- Mute

Volume uses a slider. Repeat cycles Off → All → One → Off.

Playback Queue is displayed inside the expanded player. The queue supports reordering tracks.

When the application closes, it saves the last played track, playback position, and Playback Queue for restoration at the next launch.

## 8. Accepted visual style and shared GUI behaviour

- Visual direction: modern and minimalist.
- On first launch, the application follows the Windows theme.
- Available theme choices are Dark, Light, and Automatic.
- The left navigation supports manual collapse/expand and automatic adaptation to the application window size.
- Settings opens as a page in the central workspace.
- The complete GUI layout adapts to the application window size.
- General action confirmations use a small, centered popup dialog.
- Notifications appear as brief on-screen messages and are also retained in a notification-history panel.
- Connected Services uses a provider list showing each service's connection status and available actions.
- If a provider is unavailable or a connection is interrupted, the application displays the status, automatically attempts reconnection, and offers a manual Retry action.

### Compact player navigation

Clicking the compact player's cover artwork or track name does not open the expanded player. The dedicated expand button is used to open it.

## 9. Additional accepted layout and interaction details

- Left navigation width is fixed; users cannot resize it by dragging its edge.
- The central workspace layout is page-specific and may differ between pages.
- Track lists use a standard, balanced row density.
- Track-list column headers remain visible while scrolling long lists.
- Artists, Albums, and Folders views can switch between Grid and List layouts.
- Album cards show cover artwork, album name, artist, and year.
- Empty pages or sections show a message and a clear action button for the next step.
- Loading states use Skeleton and Spinner indicators; a Progress Bar is shown when progress is known.
- Previous searches are retained, with an option to clear search history.
- Keyboard shortcuts cover playback (Play/Pause, Previous, Next), focusing Search, navigation between main pages, volume/Mute, and displaying/managing Playback Queue.

## 10. Not yet decided

The following must not be treated as accepted design decisions:

- Exact dimensions of the shared left navigation, central workspace, and bottom player remain open.
- Exact icon set, visual tokens, and detailed responsive breakpoints remain open; the modern minimalist direction, theme options/default, and general responsive behaviour are accepted.
- Provider-specific playback presentation and states.
- Remaining Local Music file-management behaviour beyond the accepted scanning, metadata-editing, and damaged-file handling rules. Folder selection includes an explicit **Confirm** action. The user adds folders manually; they are scanned recursively at startup and monitored in the background. Entries for moved/deleted files are removed from the library without touching disk files. Metadata editing is defined: title, artist, album, track number, year, and genre; explicit Save / Cancel; bulk editing; direct writing to the original file without automatic backup where supported. Damaged/unreadable files remain visible with a red error indicator beside the track name and offer Retry and Details. Details shows file name, file location, a user-friendly error message, and technical error detail when available.
- Remaining playlist presentation and management details not yet specified.
- Exact download quality/bitrate levels and provider-specific download restrictions. The unified local download and offline-playback model is accepted.
- Additional dialog and notification details beyond the accepted general confirmation popup and brief-message / notification-history pattern.
- Lyrics availability, source, synchronisation, and fallback behaviour; presentation is accepted as below the track information in the expanded player.

## 10. Working rule

Record each GUI decision here only after the owner confirms it. Keep confirmed decisions separate from proposals and unresolved questions. Do not create production UI or implementation based on provisional suggestions.
