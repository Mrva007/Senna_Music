# Senna Music — Roadmap

This roadmap tracks the agreed order of product definition and later delivery. It is not authorization to begin implementation.

## Phase 0 — Project foundation and concept definition

- [x] Establish repository and documentation source of truth.
- [x] Record current accepted product decisions.
- [x] Record open questions and development workflow.
- [x] Define primary GUI structure: navigation/page inventory, track lists, compact and expanded player, and Download Queue.
- [ ] Complete remaining GUI details, including exact dimensions and unresolved visual/interaction behaviour.
- [x] Define expanded Music Player layout: central workspace with navigation retained, always-visible Playback Queue in a right-side column, and lyrics below track information when available.
- [x] Define compact Music Player controls: Play / Pause, Previous, and Next alongside track information and artwork.
- [ ] Define search and provider connection.
- [ ] Define playback behaviour.
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
