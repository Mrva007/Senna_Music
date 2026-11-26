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

## 3. Accepted Home page

The Home page uses a vertical layout:

1. Search at the top.
2. Recently Played section.
3. Playlists section.
4. Local Music section.

The sections below Search are stacked vertically, one after another. A section is displayed only when it has data; empty sections are hidden.

## 4. Accepted global search

- One shared search is used across the application rather than separate search fields for each provider.
- Search covers music available through connected/supported sources and the user's Local Music.
- Each result visibly identifies its source: Spotify, YouTube Music, SoundCloud, or Local Music.
- Results can be filtered by source, including an All Sources filter.
- Results are displayed as a list, not as individual cards.
- Each result row shows the track name, artist, album, and source.

Search results and available capabilities remain subject to each provider's APIs, account access, licences, and technical restrictions.

## 5. Accepted page decision

- **Local Music** is a separate page in the application. This was explicitly selected by the owner.

## 6. Not yet decided

The following must not be treated as accepted design decisions:
- Complete navigation menu and page inventory, including exact names, order, icons, and grouping.
- Exact dimensions of the shared left navigation and central workspace, and the bottom player's dimensions.
- Provider connection and account-management screens.
- Provider-specific playback presentation and states.
- Local Music page layout and supported local-library operations.
- Download Queue layout details beyond the accepted columns and controls.
- Playlist page layout and playlist editing interactions.
- Settings page structure.
- Responsive behaviour, themes, dialogs, and notifications.

## 7. Working rule

Record each GUI decision here only after the owner confirms it. Keep confirmed decisions separate from proposals and unresolved questions. Do not create production UI or implementation based on provisional suggestions.
