# Senna Music — Development Workflow

## 1. Source of truth

GitHub repository `Mrva007/Senna_Music` is the single source of truth for project decisions, status, plans, and (after approval) source code.

Local working copies are for development and testing; they do not override GitHub documentation.

## 2. Current phase rule

The project is in concept definition. Do not implement application code, select a technology stack, or create a production GUI until the owner has sufficiently defined and approved the concept and GUI and explicitly authorizes implementation.

Documentation and project-management scaffolding are allowed during this phase.

## 3. Before every change

1. Inspect the current GitHub repository state and relevant documents.
2. Confirm the target branch and latest commit.
3. Read the current README and project status.
4. Identify the exact scope and files to change.
5. Preserve accepted decisions unless the owner explicitly approves a change.

Never assume a local copy is current.

## 4. Change process

- Use a dedicated branch for a coherent, small change.
- Prefer one focused issue/task and one small PR at a time.
- Keep PRs reviewable and avoid unrelated changes.
- Do not overwrite or replace README content without checking its current state.
- Do not merge a PR without the owner's approval unless an explicit standing instruction authorizes it.

## 5. After every change

1. Verify the changed files and diff.
2. Check that README and status documents remain accurate.
3. Update the relevant decision/specification/roadmap documents in the same PR.
4. Record completed work and remaining work.
5. Report the branch, PR, changed files, and verification result clearly.

## 6. Decision discipline

Use three distinct categories:
- **Accepted:** explicitly approved by the owner.
- **Proposal:** suggested, not yet approved.
- **Open:** unresolved; must not be implemented as if accepted.

Ask one focused question at a time during concept decisions. Do not repeat questions already answered.

## 7. Safety and scope

- No resets, force pushes, destructive cleanup, or deletion of user work without an explicit plan and approval.
- Do not bypass provider DRM, access controls, licences, or terms.
- Do not add features beyond the agreed scope without discussing them first.
