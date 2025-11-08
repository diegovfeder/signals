# Task Tracking & Project Board

> **Last Updated**: 2025-11-06  
> **Status**: Backlog now lives in GitHub Issues + the "Signals – Tasks" project board.

Old sprint checklists have been archived to `docs/archive/TODOs-2025-11-05.md`. From now on we open GitHub issues for every change, track them on a shared board, and keep this page as the lightweight process reference.

---

## 1. Where Work Lives

- **Issues**: https://github.com/diegovfeder/signals/issues (use the "Task" template).
- **Project Board**: `Signals – Tasks` (GitHub Projects Beta). Suggested URL: https://github.com/users/diegovfeder/projects/1 — create it if it does not exist yet and update this link if GitHub assigns a different number.
- **Docs Archive**: Anything that used to be a TODO list stays in `docs/archive/` for historical context only.

---

## 2. Board Setup (One-Time)

1. Create a **Team** project named `Signals – Tasks` under the `diegovfeder` account.
2. Add views:
   - **Kanban** (default) with columns `Inbox → Ready → In Progress → In Review → Done`.
   - **Timeline** view grouped by `iteration` for sprint planning (optional but helpful once cadence returns).
3. Enable auto-archiving of cards in `Done` after 14 days to keep noise low.
4. Add fields:
   - `Area` (enum: `frontend`, `backend`, `pipeline`, `docs`, `ops`).
   - `Priority` (enum: `now`, `next`, `later`).
   - `Effort` (number of ideal hours or story points – whichever feels natural).
5. Save a filter preset `now` → `Priority = now` so we can share a short link with teammates.
6. Create/confirm repo labels: `task`, `frontend`, `backend`, `pipeline`, `docs`, `ops`, plus any experiment-specific tags you rely on.

---

## 3. Issue Template Usage

A reusable template lives in `.github/ISSUE_TEMPLATE/task.md`. It captures:

- **Context** – the user problem or observation that justifies the change.
- **Scope** – concrete bullet list (max 5) of what must change.
- **Definition of Done** – validation steps or acceptance criteria.
- **Dependencies/Risks** – blockers, migrations, or prod toggles to watch.

### Creating an Issue

```bash
# Ensure gh CLI is authenticated
brew install gh  # if needed

# From repo root
gh issue create \
  --template task.md \
  --title "pipeline: add provider failure alerts" \
  --label pipeline
```

Every issue automatically lands in the project board once the board exists. Move cards left→right as you work.

---

## 4. Backlog Themes

All pre-scoped ideas now live in `docs/TASK_SEEDS.md`. Use that file to copy the “Outcome” row into a GitHub issue, then track it on the "Signals – Tasks" board. Remove the entry from Task Seeds only after the work ships.

---

## 5. Workflow Expectations

1. **Open an issue before writing code or docs.** Use labels + the template so context is obvious to you and your teammate.
2. **Keep issues up to date.** Drop progress notes or blockers right in the issue rather than creating ad hoc TODO lists.
3. **Review via PRs referencing the issue number.** Example: `feat(pipeline): add MACD alert thresholds (#123)`.
4. **Close the issue only after validation steps pass.** For now we rely on manual verification: run the affected Prefect flow(s), hit key API endpoints (e.g., `/health`, `/api/signals`), and test the impacted frontend routes after `bun run lint && bun run type-check`.

This page should rarely change; update it when the process or board structure shifts.
