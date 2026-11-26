# Senna Music — Roadmap

This roadmap tracks the agreed order of product definition and later delivery. It is not authorization to begin implementation.

## Phase 0 — Project foundation and concept definition

- [x] Establish repository and documentation source of truth.
- [x] Record current accepted product decisions.
- [x] Record open questions and development workflow.
- [x] Define primary GUI structure: navigation/page inventory, track lists, compact and expanded player, and Download Queue.
- [ ] Complete remaining GUI details, including exact dimensions and unresolved visual/interaction behaviour.
- [ ] Define search and provider connection.
- [ ] Define playback behaviour.
- [x] Define unified download/offline-playback model: one local downloaded file is used for both in-app offline playback and external playback.
- [x] Define download destination, folder organization, duplicate handling, format choices, and quality-selection behaviour.
- [x] Define Local Music scanning approach: user manually adds folders to scan.
- [ ] Define exact quality/bitrate levels and provider-specific download capabilities.
- [ ] Define Download Queue details.
- [ ] Complete playlist behaviour.
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
