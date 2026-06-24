# Design Patterns for Loops

The five pieces every loop needs, how to implement each in Cursor,
and real examples from the field.

Source: Addy Osmani's "Loop Engineering" and the How I AI podcast
episode "Prompts are out and loops are in" (June 2026).

---

## The Five Pieces

### 1. Automation / Trigger

The thing that starts the loop without you typing anything.

**In Cursor:**

- **Automations tab**: Define trigger, prompt, cadence, environment.
  Results land in a triage view. Use for scheduled and event-driven loops.
- **/loop**: In-session interval. `loop 5m check deploy status` runs
  every 5 minutes while the session is open.
- **/goal**: In-session goal. Keeps working until a verifiable condition
  is met. A separate small model checks the condition after each turn.
- **Hooks (hooks.json)**: Fire on agent lifecycle events (session start,
  tool use, file edit, shell command). Not for scheduling, but for
  reactive behavior within a session.

**Key insight from Osmani:** An automation can call a skill. Keep the
recurring prompt maintainable by firing `$skill-name` instead of
pasting a wall of instructions into a schedule nobody will ever update.

### 2. Isolation (Worktrees)

Two agents writing the same file is the same headache as two engineers
committing to the same lines without talking.

**In Cursor:**

- Git worktrees: `git worktree add ../feature-branch feature-branch`
- Subagent isolation: use `isolation: worktree` on Task subagents
- Each agent gets its own branch and checkout

**When to isolate:**
- Multiple subagents working on different files in parallel
- Long-running loops that shouldn't block the main workspace
- Goal loops that might produce throwaway work

**When isolation is overkill:**
- Read-only loops (reports, summaries, monitoring)
- Single-agent sequential work

### 3. Skills

Project knowledge so the agent doesn't re-derive your whole codebase
from zero every cycle. A skill is intent written down once where the
agent reads it every run.

**Without skills:** The loop re-discovers your conventions, build steps,
and "we don't do it like that because of the incident" every single
cycle. That's wasted tokens and inconsistent output.

**With skills:** The loop compounds. Each run builds on established
knowledge instead of starting fresh.

**In Cursor:**

- Project skills: `.cursor/skills/skill-name/SKILL.md`
- Personal skills: `~/.cursor/skills/skill-name/SKILL.md`
- Invoke explicitly in prompts: reference the skill by name
- Auto-invocation: set `disable-model-invocation: false` for skills
  the agent should pick up from context

**Skill design for loops specifically:**
- Keep skills under 500 lines (they eat context every cycle)
- Put the loop prompt in the automation, not in the skill
- The skill holds the HOW (conventions, standards, tools)
- The automation holds the WHEN and WHAT

### 4. Connectors (MCP Servers + Plugins)

A loop that can only see the filesystem is a tiny loop. Connectors let
the agent read your issue tracker, query a database, hit a staging API,
drop a message in Slack.

**Available in Cursor via MCP:**
- GitHub / GitLab (PRs, issues, CI)
- Slack (read channels, post messages)
- Jira / Linear (issues, sprints, boards)
- Google Workspace (Docs, Sheets, Calendar)
- Figma, PagerDuty, Sentry, Dataverse
- Custom MCP servers

**The difference connectors make:**
- Without: Agent says "here is the fix"
- With: Agent opens the PR, links the Jira ticket, and pings the
  channel once CI is green

**Before building a loop, verify:**
1. Which MCP servers does the loop need?
2. Are they connected and authenticated?
3. Does the automation environment have access to them?

### 5. Subagents (Maker / Checker Split)

The most useful structural pattern in a loop is splitting the agent
that writes from the agent that checks.

**Why:** The model that wrote the code is way too generous grading its
own homework. A second agent with different instructions catches what
the first one talked itself into.

**In Cursor:**
- Task tool spawns subagents from within a session
- Each subagent gets its own context and instructions
- Can use different models and reasoning effort levels
- Subagents can have their own goals

**Common splits:**

| Role | Job | Notes |
|------|-----|-------|
| Explorer | Read codebase, gather context | Read-only, fast model |
| Implementer | Write code, make changes | Full access, strong model |
| Verifier | Run tests, check standards | Different instructions, separate context |
| Reporter | Summarize results, post to Slack | Read-only, connectors enabled |

**Cost note:** Each subagent is its own model call with its own tool
use. Spend them where a second opinion is worth paying for: security
reviews, test validation, standards compliance. Don't spawn a subagent
to rename a variable.

### +1. Memory (State Tracking)

The agent forgets everything between runs. The repo doesn't. State
has to live on disk, not in the context.

**Options in Cursor:**

| Method | Good for | Example |
|--------|----------|---------|
| Markdown file in repo | Simple state, human-readable | `LOOP_STATE.md` with a checklist |
| Git branch state | Code changes across runs | Each run commits to the same branch |
| External tracker (Linear, Jira) | Team-visible progress | Update ticket status via MCP |
| Cursor Automation triage | Automated results | Findings land in the triage inbox |

**What to track:**
- What was done this run
- What's still pending
- What failed and why
- What was escalated

---

## Putting It Together: Example Loops

### Example 1: Daily PR Babysitter

**Type:** Schedule loop (daily cron) with goal-based subagents

**Trigger:** Automation, daily at 10:15am
**Skills needed:** Code review standards, PR merge criteria
**Connectors:** GitHub MCP, Slack MCP
**Subagents:** One per stale PR that needs fixing
**Memory:** PR status tracked via GitHub labels

**Prompt:**
```
Look at open PRs on [repo]. For any PR open more than 12 hours:
1. Check merge readiness: CI status, approvals, conflicts
2. If all checks pass but no approval, post to #team asking for review
3. If checks are failing:
   - Spin up a subagent in its own worktree to fix the failing checks
   - Give the subagent this goal: "All CI checks pass on this PR"
   - The subagent should push fixes and comment on the PR
4. If blocked on conflicts, comment on the PR with resolution guidance
5. Post a daily summary to #engineering:
   PRs ready to merge | PRs needing review | PRs being fixed
```

### Example 2: Weekly Skills Gap Finder

**Type:** Schedule loop (weekly cron) with compound subagents

**Trigger:** Automation, Fridays at 10am
**Skills needed:** Skill authoring conventions
**Connectors:** GitHub MCP
**Subagents:** One per identified skill gap, each with a validation goal
**Memory:** Skills inventory in AGENTS.md or similar

**Prompt:**
```
From recent PRs and commits merged this week on [repo]:
1. Identify tools, CLIs, or workflows that agents use repeatedly
   but have no skill for
2. For each gap:
   - Create the skill using /create-skill conventions
   - Spin up a subagent with this goal: "Validate the skill by
     running it against the base branch. The skill instructions
     produce correct output."
3. Report results: which skills were created, which passed validation,
   which need human review
```

### Example 3: CI Failure Auto-Triage

**Type:** Event loop (git trigger: CI completed)

**Trigger:** Automation on CI completion (failure only)
**Skills needed:** Project test patterns, common failure modes
**Connectors:** GitHub MCP
**Subagents:** Explorer (read logs) + Implementer (fix) + Verifier (re-test)
**Memory:** Triage results in automation inbox

**Prompt:**
```
When CI fails on a PR:
1. Read the failure logs and identify the root cause
2. Classify: flaky test, real bug, environment issue, dependency problem
3. If flaky test: re-run CI and comment on PR
4. If real bug:
   - Spawn implementer subagent to draft a fix in a worktree
   - Spawn verifier subagent to run the fix against the test suite
   - If fix passes, push to the PR and request review
5. If environment/dependency: comment on PR with diagnosis and
   suggested manual steps
```

---

## Design Anti-Patterns

**The "fix everything" loop:** A loop with no scope boundary that tries
to fix every issue it finds. It will iterate forever and burn tokens.
Always scope: which files, which tests, which issues.

**The self-grading loop:** The same agent writes code and decides if
it's good. It will always think it's good. Use the maker/checker split.

**The context-stuffing loop:** A loop that loads every skill, every
file, and every piece of context on every run. Keep loops lean. Load
only what's needed for THIS cycle.

**The fire-and-forget loop:** A loop with no state tracking that does
the same work over and over because it can't remember what it already
did. Add a memory layer.

**The infinite goal loop:** A goal condition that's too vague to ever
be satisfied. "Make the code better" will run forever. "All tests pass
and lint is clean" will stop.
