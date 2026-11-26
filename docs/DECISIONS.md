# Senna Music — Decision Log

This log records owner-approved product decisions. Proposals and unresolved questions belong in the relevant specification or open-questions register.

| ID | Decision | Status |
|---|---|---|
| D-001 | Senna Music is a standalone music platform inspired by Spotify. | Accepted |
| D-002 | The product is music-only; video is out of scope. | Accepted |
| D-003 | Initial providers are Spotify, YouTube Music, and SoundCloud. | Accepted |
| D-004 | Provider integrations must respect APIs, licences, terms, DRM, and technical restrictions; no circumvention. | Accepted |
| D-005 | Two separate download capabilities: in-app offline listening and permitted audio-file downloads for external use. | Accepted |
| D-006 | Expected audio formats: MP3, M4A, and FLAC, subject to source and rights. | Accepted |
| D-007 | GUI direction B: left navigation, central search/results area, bottom player, simple interface without unnecessary recommendations or decoration. | Accepted |
| D-008 | The user chooses the local storage folder for downloaded music files. | Accepted |
| D-009 | GUI and CLI both use the same Core and permission system. | Accepted |
| D-010 | Start with one user profile; no multi-user system required in the first version. | Accepted |
| D-011 | One shared download queue for the three initial providers, with the specified columns and controls. | Accepted |
| D-012 | Reordering download tasks changes priority and does not automatically interrupt an active download. | Accepted |
| D-013 | Bottom player includes the specified playback controls and a reorderable playback queue. | Accepted |
| D-014 | Users manually create and manage playlists; no automatic artist/album/genre cataloguing. | Accepted |
| D-015 | No separate download History page; show only current and waiting tasks in Download Queue. | Accepted |
| D-016 | Local Music is a separate GUI page. | Accepted |

## Change control

- Do not revise an accepted decision without explicit owner approval.
- When a decision changes, preserve the history: mark the old decision as superseded and record the replacement with context.
- Update the relevant specification and project status in the same small PR.
