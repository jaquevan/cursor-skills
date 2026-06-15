---
name: standup-writer
description: >-
  Auto-drafts a standup update by pulling Jira status changes, GitHub PRs,
  calendar meetings, and Slack activity since the last standup. Outputs
  paste-ready text in chat with yesterday/today/blockers format. Use when the
  user says "write my standup", "standup update", "draft my standup", "what did
  I do since last standup", "prep my standup", "standup for today", or asks for
  a standup summary.
disable-model-invocation: true
---

# Standup Writer

Reuses `work-context` Step 3 data gathering and `tomorrow-calendar-accepted`
event filtering to auto-draft a standup update. Output is paste-ready text in
chat — not a Canvas — because standups are fast and paste-and-go.

## Skill Composition

| Step | Delegates to | What it provides |
|------|-------------|-----------------|
| Data gathering | `work-context` Steps 2-3 | Parallel Jira, GitHub, Calendar, Slack queries with same server names, cloud ID, auth, graceful degradation |
| Calendar filtering | `tomorrow-calendar-accepted` | Timezone handling via `Me.md`, accepted-event-only filtering |
| MCP patterns | `work-context` | Read-only constraint, autonomy principle, fallback table |

**What this skill adds:** standup cadence detection, yesterday/today/blockers
formatting, work-channel filtering, blocker detection, and agent transcript
scanning. It skips Drive, Confluence, and Second Brain — those sources are
not standup-relevant.

## Read-Only Constraint

This skill MUST NEVER write, create, update, or modify data in any external
system. All MCP tool calls must be read-only operations. See `work-context`
for the full allowed operations list.

## Autonomy Principle

This skill runs **fully autonomously** after Step 1. No user prompts during
data gathering (Steps 2-5). If a query fails, log the error silently and
continue with remaining sources.

The only acceptable user prompts are in:
- **Step 1** — confirming the standup scope (if ambiguous)
- **Step 6** — presenting the draft

## Prerequisites

Same as `work-context`, minus Drive, Confluence, and Second Brain. The key
tools are:

| Tool | Purpose |
|------|---------|
| Atlassian MCP (`user-atlassian`) | Jira status changes |
| Slack MCP (`<YOUR_SLACK_MCP_SERVER>`) | Work channel activity |
| Google Workspace MCP (`user-google-workspace`) | Calendar events |
| GitHub CLI (`gh`) | PRs, commits |

## Workflow

### Step 1: Detect standup cadence

Determine when the last standup happened to set the lookback window.

Server: `user-google-workspace`

```
calendar_get_events(
  query = "standup",
  time_min = "<3 days ago>",
  time_max = "<now>",
  max_results = 10
)
```

Search for the recurring "standup - future sustainability & E2E" event.
Find the most recent **past** occurrence = `LAST_STANDUP`.

| Result | Lookback window |
|--------|----------------|
| Found a past standup event | `LAST_STANDUP` end time to now |
| No standup event found | Yesterday 9:00 AM in user's timezone (read from `Me.md`) |
| User specifies a range | Use that range |

Store as `SINCE_DATE` in both ISO 8601 and `YYYY-MM-DD` format.

### Step 2: Fire parallel data queries

Launch **all five** of these in a single parallel batch, reusing
`work-context` Step 3 patterns with the narrower standup window.

#### 2a. Jira — status changes since last standup

Server: `user-atlassian`

Reuse `work-context` Step 3a with modified JQL:

```
searchJiraIssuesUsingJql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  jql = "assignee = currentUser() AND status changed DURING ('{SINCE_DATE}', now()) ORDER BY updated DESC",
  fields = ["summary", "status", "issuetype", "updated", "project"],
  maxResults = 25
)
```

Second query for currently in-progress work:

```
searchJiraIssuesUsingJql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  jql = "assignee = currentUser() AND statusCategory = 'In Progress' ORDER BY priority DESC",
  fields = ["summary", "status", "issuetype", "priority", "project"],
  maxResults = 15
)
```

Third query for blocked tickets:

```
searchJiraIssuesUsingJql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  jql = "assignee = currentUser() AND (status = 'Blocked' OR status = 'Impediment') ORDER BY priority DESC",
  fields = ["summary", "status", "project"],
  maxResults = 10
)
```

#### 2b. GitHub — PRs and commits since last standup

Reuse `work-context` Step 3b with `SINCE_DATE`:

```bash
gh search prs --author="<YOUR_GITHUB_USERNAME>" --created="{SINCE_DATE}..{TODAY}" \
  --json title,url,state,createdAt,repository --limit 25

gh search prs --reviewed-by="<YOUR_GITHUB_USERNAME>" --created="{SINCE_DATE}..{TODAY}" \
  --json title,url,state,createdAt,repository --limit 10

gh api "search/commits?q=author:<YOUR_GITHUB_USERNAME>+committer-date:{SINCE_DATE}..{TODAY}&per_page=25&sort=committer-date" \
  --jq '.items[] | {message: .commit.message, date: .commit.committer.date, repo: .repository.full_name}'
```

#### 2c. Calendar — meetings attended + today's schedule

Server: `user-google-workspace`

Two queries:

**Since last standup** (for "yesterday" section):
```
calendar_get_events(
  time_min = "{SINCE_DATE}",
  time_max = "<now>",
  max_results = 25
)
```

**Today forward** (for "today" section):
```
calendar_get_events(
  time_min = "<now>",
  time_max = "<end of today>",
  max_results = 15
)
```

Apply `tomorrow-calendar-accepted` filtering to both:
- If attendee entry has `"self": true`, include only if
  `"responseStatus": "accepted"`
- If no attendees array, include if user is the organizer

#### 2d. Slack — work channel activity only

Server: `<YOUR_SLACK_MCP_SERVER>`

Reuse `work-context` Step 3d, but scoped to **work channels only**:

```
search_messages(
  query = "from:me after:{SINCE_DATE_SLACK}",
  sort = "timestamp",
  limit = 50
)
```

**Work channel allowlist** — only include messages from these channels:
- `#wg-agent-eval-harness`
- `#wg-rhai-first-uxd`
- `#team-uxd-rhai`
- `#team-openshift-ai-dashboard`

Filter out messages from DMs and social/watercooler channels.

Additionally, scan for **blocker language** in messages from any channel:
```
search_messages(
  query = "from:me blocked OR waiting on OR can't proceed after:{SINCE_DATE_SLACK}",
  limit = 10
)
```

#### 2e. Agent transcripts — undocumented work

Search recent Cursor agent conversations for work done since the last
standup that may not appear in Jira, GitHub, or Slack.

Transcript location:
`~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/`

Each chat is a directory containing a `<uuid>.jsonl` file (one JSON object
per line with `role` and `message` fields).

**Search strategy:**

1. List transcript directories modified since `SINCE_DATE`:
   ```bash
   find ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/ \
     -maxdepth 1 -type d -newermt "{SINCE_DATE}" | sort
   ```

2. For each matching directory, read the first 3 lines of the JSONL file
   to extract the user's initial query and the assistant's summary. This
   reveals the topic without reading the full conversation.

**What to extract:**
- Skills built or modified
- Files created or changed
- Investigations or debugging work
- Anything that represents progress not captured by other sources

**Cap:** Read at most 5 transcripts. Only include entries that represent
substantive work (skip short Q&A or exploratory chats).

### Step 3: Categorize results

Sort all gathered data into three buckets:

**Yesterday / Since last standup:**
- Jira tickets with status transitions (e.g., "Transitioned <YOUR_JIRA_PROJECT>-2658 to In Progress")
- GitHub PRs opened, merged, or reviewed
- Substantive Slack messages in work channels (shared artifacts, decisions, announcements)
- Meetings attended (accepted events only)
- Agent transcript work (skills built, investigations, undocumented progress)

**Today:**
- Jira tickets currently in progress (the "continue" items)
- Today's upcoming accepted meetings with times
- Any planned work mentioned in recent Slack messages

**Blockers:**
- Jira tickets with "Blocked" or "Impediment" status
- Slack messages containing blocker language
- If nothing found, output "None"

### Step 4: Filter for substance

Remove noise from each section:

- **Drop trivial Slack messages** — emoji-only, single-word replies, social
  chat. Only keep messages that mention work artifacts (ticket keys, PR links,
  tools, project names) or convey decisions/updates.
- **Drop personal calendar events** — lunch blocks, personal reminders.
  Keep meetings with other attendees only.
- **Deduplicate** — if a PR closes a Jira ticket, mention once (prefer the
  Jira framing since that's what the standup audience tracks).

### Step 5: Format output

Generate the standup update as concise paste-ready text. Each bullet should
be one line, action-oriented, and specific.

**Format:**

```
**Yesterday / Since last standup:**
- Transitioned <YOUR_JIRA_PROJECT>-2658 to In Progress
- Opened PR #123 on agent-eval-harness (download toolbar)
- Attended RH AI-first UX meeting
- Shared eval report updates in #wg-rhai-first-uxd

**Today:**
- Continue: <YOUR_JIRA_PROJECT>-2658 prototype evaluation framework
- 1:00 PM standup - future sustainability & E2E
- 1:30 PM Evan / Zack 1:1

**Blockers:**
- None
```

**Writing rules:**
- Start each bullet with a verb (Transitioned, Opened, Attended, Shared,
  Continue)
- Include ticket keys, PR numbers, and channel names for specificity
- Keep bullets to one line each — no sub-bullets, no paragraphs
- Include meeting times in the "Today" section
- "Continue: " prefix for in-progress items carrying over
- If no items exist for a section, show "- (no activity)" for
  yesterday and "- None" for blockers

### Step 6: Present in chat

Output the formatted standup text directly in chat. Do **not** create a
Canvas — standups are paste-and-go.

After the standup text, add a small note:

> Lookback window: {SINCE_DATE} to now. Sources: {included list}.
> {skipped sources, if any}.

## Fallback Behavior

| Source | Primary tool | Fallback |
|--------|-------------|----------|
| Jira | `searchJiraIssuesUsingJql` | Skip; note in footer |
| GitHub | `gh` CLI | Skip; note in footer |
| Calendar | `calendar_get_events` | Skip; note in footer |
| Slack | `search_messages` | Skip; note in footer |
| Agent transcripts | Filesystem read | Skip; note in footer |

Always report which sources were unavailable.

## Common Mistakes

| Problem | Fix |
|---------|-----|
| Creating a Canvas | Standups are paste-ready chat text. No Canvas. |
| Including social Slack messages | Only include messages from the work channel allowlist. Filter DMs and watercooler. |
| Including declined calendar events | Apply `tomorrow-calendar-accepted` filtering: only accepted events. |
| Verbose bullets | One line per bullet. No sub-bullets, no paragraphs. Start with a verb. |
| Missing ticket keys or PR numbers | Every bullet that references work should include the specific identifier. |
| Reimplementing MCP queries | Reuse `work-context` Step 3 patterns. Same servers, same cloud ID, same auth. |
| Fixed lookback window | Detect the standup cadence from calendar. Only default to yesterday 9 AM if detection fails. |
| Including Drive, Confluence, Second Brain | These are not standup-relevant. Skip them entirely. |
| Including trivial agent chats | Only include agent transcripts that represent substantive work (skills built, files changed, investigations). Skip short Q&A or exploratory chats. |
