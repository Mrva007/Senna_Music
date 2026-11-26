# Senna Music — Open Questions

Only unresolved topics are listed here. An item becomes accepted only after the owner explicitly confirms a decision and the documentation is updated.

| # | Topic | Status | Notes |
|---:|---|---|---|
| 1 | Complete left navigation and page inventory | Open | Local Music and the Home/search structure are accepted; remaining pages, exact names, order, icons, and grouping are still undefined. |
| 2 | How Spotify, YouTube Music, and SoundCloud accounts/services are connected | Open | Must respect each provider's supported authentication and API model. |
| 3 | Playback rules and capabilities for each provider | Open | Assess separately by provider and use case. |
| 4 | Offline download details | Open | Distinguish in-app offline access from external audio-file downloads. |
| 5 | Audio formats and quality of downloaded files | Open | MP3, M4A, and FLAC are expected possibilities, subject to source and rights. |
| 6 | Download Queue behaviour, persistence, and restart recovery | Open | |
| 7 | Maximum number of simultaneous downloads | Open | |
| 8 | Duplicate handling and files already present on disk | Open | |
| 9 | CLI commands and AI-agent API | Open | Same Core and permission system as GUI. |
| 10 | Application settings | Open | |
| 11 | Application updates and integration/update mechanism | Open | |
| 12 | Backup and recovery of application data | Open | |
| 13 | Technology and architecture | Open | Decide after product and GUI requirements are sufficiently defined. |
| 14 | Installation and distribution | Open | |
| 15 | Exact dimensions of the shared GUI shell | Open | Define the left navigation, central workspace, and bottom player dimensions after the GUI structure is complete. |

## Resolution rule

When an item is resolved:
1. Record the approved decision in [DECISIONS.md](DECISIONS.md).
2. Update the relevant specification.
3. Update [PROJECT_STATUS.md](PROJECT_STATUS.md).
4. Remove or mark the item resolved here, without losing useful history.
