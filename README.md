# Senna Music

A standalone, music-only desktop platform inspired by Spotify. The product concept is being defined before implementation begins.

> **Project phase: Concept and product definition. No application implementation is authorized yet.**

## Product direction

Senna Music is intended to bring together music discovery through supported online services, playback, user-managed playlists, offline listening inside the application, and downloads of audio files where the source and rights explicitly permit them.

The application is music-only. Video is out of scope.

Initial service integrations under consideration:
- Spotify
- YouTube Music
- SoundCloud

All service capabilities must respect each provider's APIs, licences, terms, and technical restrictions. Senna Music will not bypass DRM or platform restrictions.

## Current status

The accepted concept and unresolved decisions are maintained in the documentation:

- [Product concept and specification](docs/PRODUCT_SPECIFICATION.md)
- [GUI concept](docs/GUI_SPECIFICATION.md)
- [Decision log](docs/DECISIONS.md)
- [Open questions](docs/OPEN_QUESTIONS.md)
- [Project status](docs/PROJECT_STATUS.md)
- [Concept and delivery roadmap](docs/ROADMAP.md)
- [Development workflow](docs/DEVELOPMENT_WORKFLOW.md)

The documentation is the source of truth. If a discussion produces a new decision, update the relevant document and decision log through a small pull request.

## Development principles

1. Do not change accepted product decisions without the owner's approval.
2. Do not implement features while the project is in the concept phase.
3. Resolve open product and GUI questions before choosing implementation details that depend on them.
4. Keep GUI and CLI as interfaces to the same Core and permission system.
5. Prefer small, reviewable pull requests with explicit scope and acceptance criteria.
6. Keep project status and roadmap current as decisions and work are completed.
7. Respect provider APIs, licences, terms, DRM, and download restrictions.

## Planned interfaces

- **GUI:** primary graphical interface.
- **CLI:** command interface using the same Core and permission model; intended to support future AI-agent integration.

## Current milestone

**M0 — Project foundation and concept definition**

Establish the documentation and contribution workflow, then complete product and GUI definition. Implementation begins only after explicit approval.
