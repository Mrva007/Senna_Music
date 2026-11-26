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

## In progress

- [ ] Continue defining remaining GUI details and unresolved product questions.
- [ ] Define exact shared GUI dimensions after the GUI structure is complete.
- [ ] Resolve provider-specific playback, offline, and download capabilities.
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

Continue with download and offline-listening behaviour, including destination, folder organization, duplicate handling, and permitted formats. Do not revisit already accepted navigation, track-list, player, or Download Queue decisions unless the owner requests a change.
