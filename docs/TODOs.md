# Task Tracking & Project Board

> **Last Updated**: 2025-11-09  
> **Status**: Backlog now lives in GitHub Issues + the "Signals – Tasks" project board.

Old sprint checklists have been archived to `docs/archive/TODOs-2025-11-05.md`. From now on we open GitHub issues for every change, track them on a shared board, and keep this page as the lightweight process reference.

---

## 1. Where Work Lives

- **Issues**: https://github.com/diegovfeder/signals/issues (use the "Task" template).
- **Project Board**: `Signals – Tasks` (GitHub Projects Beta). URL: https://github.com/users/diegovfeder/projects/4/views/1
- **Docs Archive**: Anything that used to be a TODO list stays in `docs/archive/` for historical context only.

---

## 2. Board Setup (One-Time)

**Current Setup (Completed):**

1. ✅ Project created: `Signals – Tasks` under the `diegovfeder` account
2. ✅ Kanban view with columns: `Backlog → Next → In Progress → In Review → Done`
   - **Backlog**: Ideas, bugs, and future work. Not yet prioritized or scoped.
   - **Next**: Prioritized and ready to start. Should have clear scope and acceptance criteria.
   - **In Progress**: Actively being worked on. Should have an assignee.
   - **In Review**: Code review in progress + manual testing. PR must be open.
   - **Done**: Shipped to production and verified working. Auto-archives after 14 days.
3. ✅ Auto-archiving enabled for `Done` after 14 days
4. ✅ Repo labels created: `task`, `frontend`, `backend`, `pipeline`, `docs`, `ops`

**Optional Future Enhancements:**
- Custom fields: `Area`, `Priority`, `Effort` (can add via "+ New field" in board UI)
- Timeline view for sprint planning
- Filter presets for quick views

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

## 4. Viewing the Backlog

All backlog items live in GitHub Issues and are visible on the project board. Issues in the **Backlog** column represent future work that hasn't been prioritized yet. When ready to work on something, move it to **Next** to signal it's scoped and ready to tackle.

View all issues: https://github.com/diegovfeder/signals/issues
View the board: https://github.com/users/diegovfeder/projects/4/views/1

---

## 5. Workflow Expectations

1. **Open an issue before writing code or docs.** Use labels + the template so context is obvious to you and your teammate.
2. **Keep issues up to date.** Drop progress notes or blockers right in the issue rather than creating ad hoc TODO lists.
3. **Review via PRs referencing the issue number.** Example: `feat(pipeline): add MACD alert thresholds (#123)`.
4. **Close the issue only after validation steps pass.** For now we rely on manual verification: run the affected Prefect flow(s), hit key API endpoints (e.g., `/health`, `/api/signals`), and test the impacted frontend routes after `bun run lint && bun run type-check`.

This page should rarely change; update it when the process or board structure shifts.
