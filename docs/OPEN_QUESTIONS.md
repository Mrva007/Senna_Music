# Senna Music — Open Questions

Only implementation details that are genuinely unresolved remain here. Accepted product behaviour is recorded in DECISIONS.md and the relevant specifications. Do not reopen accepted decisions.

| # | Topic | Status | Notes |
|---:|---|---|---|
| 1 | YouTube and Spotify authenticated-session mechanism | Technical implementation | User sign-in/session support is accepted. Select the most reliable practical browser-cookie/session handoff or supported login flow. Never store account passwords in plaintext. |
| 2 | Source-specific search and download adapters | Technical validation | Implement and test YouTube, Spotify track lookup/matching, and SoundCloud independently. Verify search reliability, URL extraction, authentication needs, and which results can be processed by the shared downloader. |
| 3 | Spotify matching and alternative resolution | Technical validation | Determine the best Python-based resolver workflow for matching Spotify title/artist metadata to a corresponding result on another supported source. Preserve the actual download-source label and separate source records. |
| 4 | Exact download quality/bitrate levels | Product detail | Default quality is configured in Settings. There is no per-download quality override. Define the available quality levels and source-specific limits during download implementation. |
| 5 | Remaining GUI visual details | Deferred polish | Exact dimensions, icon assets, and precise responsive breakpoints are not blockers for the first working build. |
| 6 | In-app source-link browser behaviour | Implementation detail | The accepted behaviour allows opening a source link externally or inside the app. Choose a practical implementation that does not block the first release. |
| 7 | Lyrics provider integrations | Later implementation | Lyrics behaviour is defined; select and validate actual providers and availability during the player milestone. |
| 8 | CLI command surface | Deferred | CLI must use the same Core and permission system. Define commands after the main GUI workflows are working. |
| 9 | Windows packaging and distribution | V1 release task | Choose a repeatable packaging method and produce an installable/testable Windows build. |
| 10 | Backup and recovery | Deferred | Define backup scope and restore workflow after the core local data model is stable. |
| 11 | Automatic updates | Deferred | Choose an update mechanism after the first testable Windows release. |
| 12 | Search-history item actions | Deferred detail | Last 20 queries and immediate Clear History behaviour are accepted. Individual history-item deletion and click behaviour can be finalized during implementation if needed. |

## Resolution rule

When an item is resolved:
1. Record the decision in [DECISIONS.md](DECISIONS.md).
2. Update the relevant specification.
3. Update [PROJECT_STATUS.md](PROJECT_STATUS.md).
4. Remove or mark the item resolved here.

Do not create a new document when an existing specification can be updated.
