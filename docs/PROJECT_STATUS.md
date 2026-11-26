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
- [x] Local Music scanning method confirmed: user manually adds folders to scan.
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

Continue defining remaining GUI details and product questions, including exact quality/bitrate levels, provider capabilities, and detailed Local Music behaviour. The unified download/offline-playback model, manual folder scanning, and Settings default with per-download quality override are accepted. Do not revisit these or previously accepted navigation, track-list, player, and Download Queue decisions unless the owner requests a change.
