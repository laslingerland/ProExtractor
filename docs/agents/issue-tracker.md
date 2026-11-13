# Issue tracker: Local Markdown

Tickets for this repository live as markdown files in `.scratch/` in this repository,
never in the parent Scripts workspace.

## Conventions

- One feature per directory: `.scratch/NNN-<slug>/`. `NNN` is the feature number.
- The feature overview is `.scratch/NNN-<slug>/README.md`.
- Each task is one file in the feature directory: `NNN-<short-description>.md`, where
  `NNN` is the task number within the feature. "Ticket 004/001" means feature 004, task 001.
  Task files link to the feature `README.md` as parent.
- Each ticket has a `Status:` line and, when triaged, a `Labels:` line near the top
  (see `triage-labels.md`).
- Dependencies go under `## Dependencies`, one per line, starting with the direction:
  `Na [NNN](...)` (this ticket waits for NNN) or `Vóór [NNN](...)` (NNN waits for this
  ticket), optionally followed by a colon and a reason.
- Discussion that must stay with a ticket goes under `## Comments` at the bottom.
- A finished task gets the `✓-` prefix. When all tasks of a feature are finished, the
  feature folder gets the `✓-` prefix and moves to `.scratch/done/`; a lapsed feature
  moves to `.scratch/wontfix/`. Update every affected link.
- Legacy planning material that is not a ticket goes in `.scratch/legacy/`.

## When a skill says "publish to the issue tracker"

Create the feature directory with its `README.md`, or add a task file to an existing
feature, using the next free number.

## When a skill says "fetch the relevant ticket"

Read the referenced file. The user normally passes a path or a number such as `004/001`.

## Wayfinding operations

- **Map**: the feature `README.md` (Notes / Decisions so far / Fog).
- **Child ticket**: a task file `NNN-<slug>.md` with a `Type:` line
  (`research`/`prototype`/`grilling`/`task`) and a `Status:` line (`claimed`/`resolved`).
- **Blocking**: `Na [NNN](...)` lines under `## Dependencies`. A ticket is unblocked
  when every ticket it waits for is resolved.
- **Frontier**: open, unblocked, unclaimed task files; the lowest number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: add the answer under `## Answer`, set `Status: resolved`, rename with
  `✓-`, and add a pointer (gist + link) to the map's Decisions so far.
