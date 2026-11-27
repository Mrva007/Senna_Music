# Senna Music — Roadmap

This roadmap tracks the agreed order of product definition and later delivery. It is not authorization to begin implementation.

## Phase 0 — Project foundation and concept definition

- [x] Establish repository and documentation source of truth.
- [x] Record current accepted product decisions.
- [x] Record open questions and development workflow.
- [x] Define primary GUI structure: navigation/page inventory, track lists, compact and expanded player, and Download Queue.
- [ ] Complete remaining GUI details: exact dimensions, specific icon assets, detailed visual tokens, precise responsive thresholds, and unresolved interaction behaviour.
- [x] Confirm modern minimalist visual direction, Windows-following initial theme, and Dark / Light / Automatic theme choices.
- [x] Confirm manual and automatic left-navigation collapse, Settings in the central workspace, and whole-layout responsiveness.
- [x] Confirm fixed left-navigation width and page-specific central workspace layouts.
- [x] Confirm standard track-list density and sticky column headers.
- [x] Confirm Grid/List switching for Artists, Albums, and Folders, plus album-card information.
- [x] Confirm empty-state message/action pattern and Skeleton/Spinner/known-progress loading indicators.
- [x] Confirm retained search history with a clear-history option.
- [x] Confirm keyboard shortcut groups for playback, Search focus, main-page navigation, volume/Mute, and Playback Queue.
- [x] Confirm narrow-window navigation collapse, hover tooltips, and active navigation styling.
- [x] Confirm adaptive compact-player information and conditional central page titles.
- [x] Confirm responsive Grid card sizing and search-history dropdown/immediate clearing.
- [x] Confirm customizable keyboard shortcuts and their discoverability in Settings and relevant menus/tooltips.
- [x] Confirm visual-system rules: consistent outline/filled active icon treatment, neutral sans-serif typography (14–15 px), clear hierarchy, balanced spacing, slightly rounded corners, subtle borders without shadows, short subtle animations, and content-driven automatic navigation collapse.
- [x] Confirm general confirmation dialogs, brief notifications plus history panel, Connected Services list presentation, and automatic reconnection with manual Retry.
- [x] Confirm compact-player artwork/title clicks do not expand the player; only the dedicated expand button does.
- [x] Define expanded Music Player layout: central workspace with navigation retained, always-visible Playback Queue in a right-side column, and lyrics below track information when available.
- [x] Define compact Music Player controls: Play / Pause, Previous, and Next alongside track information and artwork.
- [x] Confirm Shuffle and Repeat controls are available only in the expanded Music Player, not the compact player.
- [x] Define integrated local-first music search: search YouTube, Spotify, and SoundCloud simultaneously, combine results in one source-labelled list, and provide source filters.
- [x] Define separate source search adapters with a shared normalized result model and common yt-dlp / FFmpeg download workflow where supported.
- [ ] Validate non-API search and URL extraction, download eligibility, and rights separately for each initial source.
- [ ] Define exact integrated-search placement and detailed row interactions.
- [x] Define lyrics source priority, synchronisation, language preference, fallback, and unavailable-state behaviour.
- [ ] Define provider-specific playback behaviour.
- [x] Define unified download/offline-playback model: one local downloaded file is used for both in-app offline playback and external playback.
- [x] Define download destination, folder organization, duplicate handling, format choices, and quality-selection behaviour.
- [x] Define Local Music scanning approach: user manually adds folders; scan automatically at application startup.
- [x] Define missing-file reconciliation: remove missing/moved entries from the library without changing files on disk.
- [x] Define recursive scanning of manually added folders, including all subfolders.
- [x] Define automatic background monitoring while the application is running.
- [x] Define automatic addition of newly discovered music files to the Local Music library.
- [x] Define supported Local Music audio formats: MP3, M4A, FLAC, WAV, and OGG.
- [x] Define audio metadata editing: title, artist, album, track number, year, and genre; explicit Save / Cancel; bulk editing; direct writes to the original file where supported, without automatic backup.
- [x] Define handling of damaged/unreadable files: keep them visible with a red error indicator beside the track name, with Retry and Details actions.
- [ ] Define exact quality/bitrate levels and provider-specific download capabilities.
- [x] Define Download Queue persistence and restart recovery: preserve waiting tasks across restarts and resume interrupted active downloads from the last safely saved position when technically supported.
- [x] Define playlist track removal, safe playlist deletion, Favorites track removal and collection-track removal, safe Favorites collection deletion, persistent manual playlist ordering, and persistent manual ordering in both the main Favorites list and individual Favorites collections, plus temporary display sorting by title, artist, or album in playlists and the main Favorites list, and visible track counts for user-created Favorites collections (the main Favorites list has no total count beside its name).
- [x] Define renaming of user-created Favorites collections; renaming changes only the collection name and preserves its tracks and saved order.
- [x] Define Favorites collection deletion access through both the three-dot menu and right-click context menu, with confirmation; custom collection cover images are not supported.
- [x] Define Favorites collection display order (alphabetical by name) and confirm that no dedicated collection-search field is provided.
- [x] Define both Favorites collection creation entry points: **New Collection** on the Favorites page and **+** beside the Favorites heading.
- [x] Define the collection creation dialog: name field with **Create** and **Cancel** actions.
- [x] Define duplicate Favorites collection-name handling: reject an existing name and display a message.
- [x] Define empty-name validation: keep **Create** disabled until a non-empty collection name is entered; reject whitespace-only input.
- [x] Define case-insensitive Favorites collection-name uniqueness; `Rock` and `rock` are duplicates.
- [x] Define trimming leading and trailing whitespace from Favorites collection names before validation and duplicate comparison.
- [x] Define preservation of multiple consecutive spaces between words in Favorites collection names; do not collapse them.
- [x] Define placement of duplicate-name validation message directly below the name field inside the creation popup.
- [x] Define playlist creation and rename dialogs, case-insensitive unique names, duplicate-name feedback and immediate clearing.
- [x] Define playlist Add to Playlist entry points in right-click and three-dot menus.
- [x] Define multi-select add-to-playlist flow, including creating a playlist without leaving the flow.
- [x] Define the visible empty-playlist state and its add-tracks option.
- [x] Define temporary playlist sort-selection lifetime without changing saved manual order.
- [x] Define playlist-list alphabetical ordering and per-playlist track counts.
- [x] Define playlist Rename/Delete access through three-dot and right-click menus, with mandatory delete confirmation.
- [x] Confirm playlist list remains alphabetical with no manual reordering (D-099).
- [ ] Define CLI and future AI-agent integration.
- [ ] Define settings and system functions.
- [ ] Review concept completeness and obtain explicit owner approval to begin implementation.

## Phase 1 — Architecture and technical planning

**Blocked until Phase 0 is sufficiently complete and approved.**

- Define technology choices and architecture.
- Define Core boundaries and shared permission model.
- Define provider adapter/integration contracts.
- Define data storage and persistence.
- Define packaging, installation, updates, backup, and recovery.

No technology choice is pre-approved by this roadmap.

## Phase 2 — Implementation

**Not authorized.** Scope and sequence will be planned only after the concept and architecture are approved.

Implementation should be split into small, reviewable tasks and pull requests. Each completed task must update project status and its acceptance evidence.

## Definition of done

A task is complete only when:
- Its agreed acceptance criteria are met.
- Relevant checks or tests have been performed where applicable.
- Documentation reflects the actual result.
- The corresponding GitHub issue/PR is updated.
- The owner can identify the change and its status without repeating prior investigation.

- [x] Define immediate clearing of duplicate-name validation when the user edits the name to a non-duplicate.
- [x] Define playlist creation/rename validation, Add to Playlist flows, empty-playlist state, and temporary sort-selection lifetime (D-087–D-094).
- [x] Define alphabetical playlist display, per-playlist track counts, Rename/Delete menu access, and delete confirmation (D-095–D-098).
- [x] Confirm that the playlist list itself cannot be manually reordered (D-099).
- [x] Define an explicit **Confirm** action in the Local Music folder-selection flow (D-100).


- [x] Define general provider connection and playback rules: official sign-in, in-app playback when permitted, official-service fallback, all available sources, preferred provider setting, reconnection/Retry, and user-confirmed source switching (D-155–D-161).
- [x] Confirm that audio-file downloads are permitted only when officially allowed by the service/source (D-162).
- [ ] Verify actual authentication, playback, offline, and download capabilities separately for each initial provider.


- [x] Research official Spotify, YouTube, and SoundCloud developer capabilities and restrictions.
- [ ] Resolve provider policy compatibility and owner decisions before online-provider implementation.
- [ ] Obtain written provider permission where required or revise initial provider scope/playback behaviour.


- [ ] Later phase: evaluate and define a torrent-search adapter for lawful content; not part of the initial version.
