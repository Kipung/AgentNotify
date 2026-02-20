# Scrum Working Agreement

Date: 2026-02-20

## Why This Exists

This document keeps execution aligned with the project charter and makes scope changes explicit before they become rework.

## Cadence

All times use your local timezone.

1. Daily standup (Mon-Fri): 15 minutes
2. Backlog refinement (Wed): 30 minutes
3. Sprint planning (every 2 weeks, Mon): 45 minutes
4. Sprint review + retro (every 2 weeks, Fri): 45 minutes

## Meeting Goals

### Daily Standup

Answer only:

1. What was completed since last standup?
2. What will be completed before next standup?
3. What is blocked and what is the unblock plan?

Output:

- Updated top-3 priorities for next 24 hours
- Explicit blocker owner

### Backlog Refinement

Focus:

1. Clarify acceptance criteria for upcoming work
2. Identify hidden cross-platform edge cases
3. Split work into mergeable increments (1 day target each)

Output:

- Ordered backlog for next sprint
- Risks with owner + mitigation

### Sprint Planning

Focus:

1. Pick sprint goal tied to charter and roadmap
2. Commit to achievable scope
3. Define verification commands for each milestone

Output:

- Sprint goal
- Committed backlog items
- Test and demo proof plan

### Sprint Review + Retro

Focus:

1. Demo shipped behavior, not plans
2. Compare expected vs actual outcomes
3. Capture one process improvement to apply immediately

Output:

- Accepted deliverables
- Deferred items list
- One working-agreement improvement

## Definition of Sprint Success

1. At least one user-visible improvement is shipped.
2. Related tests are added or updated.
3. Documentation reflects new behavior.
4. No unresolved P1/P2 defects are carried silently.

## Change Triggers

Open a direction check (outside standup) if any of these occur:

1. Two consecutive days blocked by environment/tooling.
2. Roadmap item expands by more than 30 percent effort.
3. New platform constraint invalidates current approach.
4. Test signal quality drops (flaky or un-runnable local test path).

When triggered, update:

1. `docs/project_charter.md`
2. `docs/assumptions.md`
3. `docs/commit_plan.md`

## Notes Template

Use this for each ceremony:

```markdown
# <Meeting Type> - <YYYY-MM-DD>

## Goal
- 

## Decisions
- 

## Risks / Blockers
- 

## Actions (Owner, Due Date)
- 
```
