# Senna Music — Open Questions

Only unresolved topics are listed here. An item becomes accepted only after the owner explicitly confirms a decision and the documentation is updated.

| # | Topic | Status | Notes |
|---:|---|---|---|
| 1 | Complete left navigation and page inventory | Open | Local Music has been accepted as a separate page; the rest of the navigation remains undefined. |
| 2 | Search presentation and filters | Open | |
| 3 | How Spotify, YouTube Music, and SoundCloud accounts/services are connected | Open | Must respect each provider's supported authentication and API model. |
| 4 | Playback rules and capabilities for each provider | Open | Assess separately by provider and use case. |
| 5 | Offline download details | Open | Distinguish in-app offline access from external audio-file downloads. |
| 6 | Audio formats and quality of downloaded files | Open | MP3, M4A, and FLAC are expected possibilities, subject to source and rights. |
| 7 | Download Queue behaviour, persistence, and restart recovery | Open | |
| 8 | Maximum number of simultaneous downloads | Open | |
| 9 | Duplicate handling and files already present on disk | Open | |
| 10 | CLI commands and AI-agent API | Open | Same Core and permission system as GUI. |
| 11 | Application settings | Open | |
| 12 | Application updates and integration/update mechanism | Open | |
| 13 | Backup and recovery of application data | Open | |
| 14 | Technology and architecture | Open | Decide after product and GUI requirements are sufficiently defined. |
| 15 | Installation and distribution | Open | |

## Resolution rule

When an item is resolved:
1. Record the approved decision in [DECISIONS.md](DECISIONS.md).
2. Update the relevant specification.
3. Update [PROJECT_STATUS.md](PROJECT_STATUS.md).
4. Remove or mark the item resolved here, without losing useful history.
