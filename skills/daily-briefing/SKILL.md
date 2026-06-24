---
name: daily-briefing
description: >
  Unified morning briefing that pulls calendar, tasks, email, Slack threads,
  Jira sprint status, cross-repo activity, and agent replies into one
  structured overview with meeting classification and priority ordering.
  Use when the user says "daily briefing", "prep me for my day", "morning
  brief", "what's on my plate", "what's on deck", "start my day", "daily
  prep", "what do I have today", or asks for a summary of their day ahead.
argument-hint: "[optional: 'tomorrow' or specific focus area]"
disable-model-invocation: true
---

# Daily Briefing

You produce a comprehensive morning briefing by pulling from all available
sources and presenting a prioritized view of the day. Output as a Canvas.

The user's input is: **$ARGUMENTS**

---

## Skill Composition

This skill composes existing tools and patterns:

| Source | Tool / Method | What it provides |
|--------|--------------|-----------------|
| Calendar | `user-google-workspace` MCP: `calendar_get_events` | Today's schedule |
| Tasks | `user-google-workspace` MCP: `calendar_get_events`, `drive_search` | Google Tasks |
| Email | `user-google-workspace` MCP: `gmail_list_messages` | Unread emails |
| Slack | `<YOUR_SLACK_MCP_SERVER>` MCP: `search_messages` | Active threads, saved items |
| Jira | `user-atlassian` MCP: `getMyIssues` | Sprint items, blockers |
| Repo activity | `task-dispatch` scripts: `scan_repos.py` | Git commits, agent sessions, task replies |
| Agent replies | `task-dispatch` scripts: `dispatch_task.py --check-replies` | Unread cross-agent messages |

## Read-Only Constraint

This skill MUST NEVER write, create, update, or modify data in any external
system. All MCP tool calls must be read-only operations.

## Autonomy Principle

This skill runs **fully autonomously** after invocation. No user prompts
during data gathering. If a source fails, log it silently and continue.

---

## Workflow

### Step 1: Check current time

Run `date` in the shell to get the current time and day.

If the user said "tomorrow", use `days_ahead=1` for calendar. Otherwise
use `days_ahead=0`.

### Step 2: Gather data (all in parallel)

Fire all of these simultaneously:

#### 2a. Calendar events

Server: `user-google-workspace`

```
calendar_get_events(days_ahead = 0, max_results = 25)
```

#### 2b. Unread emails

Server: `user-google-workspace`

```
gmail_list_messages(query = "is:unread", max_results = 15)
```

Also check for Gemini meeting notes from the past few days:

```
gmail_list_messages(
  query = "(from:gemini-notes OR from:meetings-noreply) after:<3 days ago>",
  max_results = 10
)
```

#### 2c. Slack activity

Server: `<YOUR_SLACK_MCP_SERVER>`

```
search_messages(query = "from:me", sort = "timestamp", limit = 20)
```

Also check saved items:

```
search_messages(query = "is:saved", limit = 10)
```

#### 2d. Jira sprint status

Server: `user-atlassian`

```
getMyIssues(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  status = "In Progress,To Do"
)
```

#### 2e. Cross-repo activity

Run in shell:

```bash
python3 .cursor/skills/task-dispatch/scripts/scan_repos.py \
  --repos-dir ~/Desktop/ --days 3
```

#### 2f. Agent replies

Run in shell:

```bash
python3 .cursor/skills/task-dispatch/scripts/dispatch_task.py \
  --check-replies --repos-dir ~/Desktop/
```

### Step 3: Classify meetings

For each calendar event, classify its type to determine prep depth:

| Type | Signals | Prep Depth |
|------|---------|------------|
| **1:1** | 2 attendees, "1:1", "Name / Name" | Deep -- DMs, shared topics, open loops |
| **Decision** | "review", "approve", "prioritize", "strategy" | Deep -- options, stakeholder positions |
| **Presentation** | "readout", "demo", "showcase", "walkthrough" | Medium -- content preview |
| **Standup** | "standup", "sync", "check-in", recurring daily | Quick -- blockers only |
| **Large** | 10+ attendees, "all hands", "town hall" | Quick -- agenda only |
| **Standard** | Everything else | Medium -- recent discussion context |

### Step 4: Build Canvas

Read the Canvas skill and follow its instructions to create:
`~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/canvases/daily-briefing.canvas.tsx`

**Canvas sections:**

1. **Header** -- "Daily Briefing -- [Day], [Date]", current time
2. **Schedule** -- Table of today's meetings with type classification,
   time, title, and prep flags. Highlight meetings needing deep prep.
3. **Agent Replies** -- Unread replies from dispatched tasks across repos.
   Show repo name, task, and agent's message. Flag as needing response.
4. **Priority Actions** -- Numbered list of suggested priorities with
   time estimates. Combine the most urgent items from all sources.
5. **Jira Sprint** -- Current sprint items grouped by status (In Progress,
   To Do). Show ticket key, summary, and priority.
6. **Slack Threads** -- Notable active threads with context. Group by
   topic, attribute to channel/person.
7. **Emails** -- Emails worth noting (not spam/newsletters). Show sender,
   subject, and whether action is needed.
8. **Repo Activity** -- Recent git commits and agent sessions across
   projects. Show what was being worked on.
9. **Coverage Footer** -- Which sources contributed data and which failed.

**Canvas rules:**
- Import only from `cursor/canvas`. No npm packages, no fetch calls.
- Use `useHostTheme()` tokens for all colors. No hardcoded hex.
- No emojis, no gradients, no box-shadows.
- Default-export the top-level component.
- Omit sections with no data.

### Step 5: Summarize in chat

Alongside the canvas, provide a brief text summary:

- Number of meetings today (with types breakdown)
- Top 3 priority items
- Any unread agent replies that need attention
- Which sources were unavailable

---

## Fallback Behavior

| Source | Fallback |
|--------|----------|
| Calendar | "Calendar unavailable -- schedule not shown" |
| Email | Skip email section |
| Slack | Skip Slack section |
| Jira | Skip Jira section; note in footer |
| Repo scan | Skip activity section; note in footer |
| Agent replies | Skip replies section; note in footer |

Always report which sources were unavailable.

---

## What NOT to Do

- Don't ask questions during data gathering. Run fully autonomously.
- Don't write to any external system. Read-only.
- Don't include meeting content from past meetings (that's `meeting-prep`).
  Just classify and flag which ones need deep prep.
- Don't generate the full prep for each meeting. Just flag type and depth.
  The user can invoke `/meeting-prep` for specific meetings.
- Don't skip the repo scan. The cross-agent awareness is what makes this
  briefing different from just checking calendar and email.
