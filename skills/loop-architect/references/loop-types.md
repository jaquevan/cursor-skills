# Loop Types Reference

Four ways to automate an agent prompt, from simplest to most autonomous.

---

## 1. Schedule Loop (Heartbeat / Cron)

Runs on a fixed cadence. The simplest loop type.

**Heartbeat**: every N minutes/hours. Good for monitoring and polling.
- Every 5 minutes, check CI status
- Every hour, scan for new issues

**Cron**: at specific times. Good for reports and reviews.
- Daily at 9am, generate standup summary
- Fridays at 10am, review merged PRs for skill gaps
- Sundays at 8pm, prepare weekly brief

**How to build in Cursor:**

| Cadence | Tool | Notes |
|---------|------|-------|
| In-session interval | `/loop 5m [prompt]` | Runs while session is open. Agent stays active. |
| Scheduled time | Cursor Automation (cron trigger) | Runs independently. Can use cloud compute. |
| External schedule | GitHub Action + Cursor CLI | Runs in CI. Good for repo-scoped work. |

**When to use:** The task is the same every time. No conditional logic.
You want a report, a check, or a summary delivered on a predictable
schedule.

**When NOT to use:** The task depends on whether something changed. Use
an event loop or goal loop instead.

**Prompt template:**

```
Every [cadence], do the following:
1. [Gather context: what to read, query, or check]
2. [Analyze: what to look for or evaluate]
3. [Act: what to produce, send, or update]
4. [Escalate: what to do if something is wrong]
```

**Example:**

```
Daily at 9am, review all open PRs on [repo]:
1. List PRs open more than 24 hours with their CI status
2. For each, check: approvals, conflicts, failing checks
3. Post a summary to #engineering in Slack with a table:
   PR | Author | Age | Status | Blocker
4. If any PR has been open more than 72 hours, DM the author
```

---

## 2. Event Loop (Hook / Trigger)

Runs when something specific happens. Reactive, not scheduled.

**Internal events** (agent lifecycle):
- Session started -> set up context
- File edited -> run formatter
- Shell command about to execute -> safety check
- Subagent stopped -> chain to next task

**External events** (integrations):
- PR opened -> triage and review
- Slack message received -> respond or route
- CI completed -> check results
- Jira issue created -> start implementation

**How to build in Cursor:**

| Event source | Tool | Notes |
|-------------|------|-------|
| Agent lifecycle | Hook (hooks.json) | Runs before/after tool use, shell, file edits |
| GitHub/GitLab | Cursor Automation (git trigger) | PR opened, pushed, merged, CI completed |
| Slack | Cursor Automation (Slack trigger) | Message in channel, reaction added |
| HTTP webhook | Cursor Automation (webhook trigger) | Any external service that sends webhooks |
| File/output change | `/loop` with watcher | Dynamic schedule, wakes on event |

**When to use:** Work should only happen in response to a specific
trigger. No point running if nothing changed.

**When NOT to use:** You need continuous monitoring without a clear
trigger event. Use a heartbeat instead.

**Prompt template:**

```
When [event] happens:
1. [Read the event context: PR diff, Slack message, issue details]
2. [Classify: is this something that needs action?]
3. [If yes, act: what specific steps to take]
4. [If no, skip silently or log why]
5. [If blocked, escalate: notify human or create ticket]
```

---

## 3. Goal Loop

Runs until a measurable condition is true. The most autonomous loop
type. A separate model checks whether the goal is met after each turn,
so the agent that did the work isn't grading its own homework.

**How to build in Cursor:**

| Scope | Tool | Notes |
|-------|------|-------|
| In-session | `/goal [condition]` | Keeps working until condition validated |
| In automation | Goal-based prompt in automation instructions | Define exit criteria in the prompt |
| As subagent | Spawn subagent with goal-based prompt | Isolate goal work from parent thread |

**When to use:** The work has a clear, verifiable end state. You can
write a condition that a separate model can check.

**When NOT to use:**
- Success criteria are subjective ("make it better")
- The condition can't be automatically verified
- The task is open-ended with no natural stopping point

**Good goal conditions** (measurable, verifiable):

```
All tests in test/auth pass and lint is clean
The PR has zero failing CI checks and at least one approval
Every function in src/api/ has JSDoc comments
The migration runs without errors on the test database
```

**Bad goal conditions** (vague, subjective):

```
The code is clean and well-organized          # "clean" is undefined
Make sure everything works                     # "everything" and "works" are both vague
Improve the performance                        # improve by how much? measured how?
Fix all the bugs                               # how do you know there are no more bugs?
```

**Prompt template:**

```
Goal: [measurable condition]

Steps to achieve the goal:
1. [First action toward the goal]
2. [Validation step: how to check progress]
3. [Iteration: what to try if validation fails]

When blocked:
- [Specific escalation: stop, alert, skip]

Do NOT:
- [Anti-pattern: specific wrong approaches to avoid]
```

**Cost warning:** Goal loops are the most expensive loop type. Every
turn is a model call, plus a separate validation call. If your goal
condition is too loose, the agent will iterate indefinitely. Always
set a maximum iteration count or time limit when possible.

---

## 4. Compound Loop (Loop of Loops)

A parent loop that spawns child loops or subagents, each with their
own type. This is where the real leverage lives.

**Pattern:** Schedule -> Discover -> Spawn goal-based subagents

```
Parent (daily at 9am):
  1. Scan for open issues tagged "bug"
  2. For each issue:
     - Spawn a subagent with a goal: "fix this bug and all tests pass"
     - The subagent works in its own worktree
     - A separate checker subagent reviews the fix
  3. Collect results
  4. Post summary to Slack
```

**Pattern:** Event -> Triage -> Route to specialized loops

```
Parent (on PR opened):
  1. Read the PR diff
  2. Classify: security change? API change? UI change?
  3. Route to the right checker:
     - Security: spawn security review subagent
     - API: spawn contract validation subagent
     - UI: spawn visual regression subagent
  4. Aggregate results as PR comments
```

**The maker/checker split:** Never let the same agent write code and
validate it. The model that wrote the code is too generous grading its
own work. Always use a separate subagent (potentially a different model
or different instructions) for verification.

**How to structure subagents in Cursor:**

- Use the Task tool to spawn subagents from within a session
- Give each subagent a specific, narrow goal
- Use `isolation: worktree` when subagents touch files
- Collect results back in the parent thread

---

## Decision Matrix

| Question | Schedule | Event | Goal | Compound |
|----------|----------|-------|------|----------|
| Happens at fixed times? | Yes | No | No | Maybe |
| Triggered by external event? | No | Yes | No | Maybe |
| Has a measurable end state? | No | No | Yes | Yes |
| Needs multiple specialized agents? | No | No | No | Yes |
| Cost predictable? | Yes | Depends on volume | No | No |
| Complexity | Low | Medium | Medium | High |
| Risk of token waste | Low | Low | High | High |
