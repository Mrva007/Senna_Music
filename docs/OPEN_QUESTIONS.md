# Senna Music — Open Questions

Only unresolved topics are listed here. An item becomes accepted only after the owner explicitly confirms a decision and the documentation is updated.

| # | Topic | Status | Notes |
|---:|---|---|---|
| 1 | Exact dimensions and visual design of the GUI shell | Open | Navigation order and core page structure are accepted; exact dimensions, icons, visual styling, and responsive behaviour remain open. |
| 2 | Provider connection and account-management details | Open | Must respect each provider's supported authentication and API model. The Connected Services page inventory is accepted. |
| 3 | Playback rules and capabilities for each provider | Open | Assess separately by provider and use case. |
| 4 | Offline download details | Open | Distinguish in-app offline access from external audio-file downloads. |
| 5 | Audio formats and quality of downloaded files | Open | MP3, M4A, and FLAC are expected possibilities, subject to source and rights. Format/quality selection remains open. |
| 6 | Download Queue persistence and restart recovery | Open | Queue columns, controls, ordering, and single-download concurrency are accepted; persistence/recovery of download tasks remains open. |
| 7 | Duplicate handling and files already present on disk | Open | |
| 8 | CLI commands and AI-agent API | Open | Same Core and permission system as GUI. |
| 9 | Application updates and integration/update mechanism | Open | |
| 10 | Backup and recovery of application data | Open | |
| 11 | Technology and architecture | Open | Decide after product and GUI requirements are sufficiently defined. |
| 12 | Installation and distribution | Open | |
| 13 | Detailed Local Music operations | Open | Scanning, metadata handling, file operations, and supported local formats. |
| 14 | Detailed playlist and Favorites interactions | Open | Core navigation and collection concepts are accepted; detailed editing and management interactions remain open. |
| 15 | Lyrics behaviour | Open | Show lyrics in expanded player when available; source, synchronisation, and fallback behaviour remain open. |
| 16 | Provider-specific playback and offline behaviour | Open | Capabilities must be verified per provider and must comply with their terms and restrictions. |

## Resolution rule

When an item is resolved:
1. Record the approved decision in [DECISIONS.md](DECISIONS.md).
2. Update the relevant specification.
3. Update [PROJECT_STATUS.md](PROJECT_STATUS.md).
4. Remove or mark the item resolved here, without losing useful history.
