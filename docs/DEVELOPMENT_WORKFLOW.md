# Senna Music — Development Workflow

## 1. Source of truth

GitHub repository `Mrva007/Senna_Music` is the single source of truth for project decisions, status, plans, and (after approval) source code.

Local working copies are for development and testing; they do not override GitHub documentation.

## 2. Current phase rule

The owner explicitly authorized implementation on 2026-11-27. The project is now in V1 implementation. Do not return to concept-definition questioning unless an actual implementation blocker requires a decision. Preserve accepted decisions and build in small, testable PRs.

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

Avoid reopening settled decisions. Ask only when a genuine blocker cannot be resolved from the accepted specifications or a safe technical default. Prefer making reversible technical choices and documenting them over delaying implementation.

## 7. Safety and scope

- No resets, force pushes, destructive cleanup, or deletion of user work without an explicit plan and approval.
- Do not bypass provider DRM, access controls, licences, or terms.
- Do not add features beyond the agreed scope without discussing them first.
