---
name: work-context
description: >-
  Aggregates recent activity across Second Brain, Jira, GitHub, Google Calendar,
  Slack, Google Drive, and Confluence into an interactive Canvas summary. Use
  when the user says "what have I been working on", "summarize my work", "my
  activity summary", "what did I do this week", "catch me up", "work summary",
  "weekly summary", "what's my context", "what have I done", "recap my week",
  or asks for a summary of recent work across tools.
disable-model-invocation: true
---

# Work Context

Gathers the user's recent activity across all connected tools and renders an
interactive Canvas organized by theme. Optimized for speed via local-first
reads and parallel MCP queries.

## Read-Only Constraint

This skill MUST NEVER write, create, update, or modify data in any external
system. All MCP tool calls must be read-only operations.

**Allowed operations:**

- **Jira:** searchJiraIssuesUsingJql, getJiraIssue, getAccessibleAtlassianResources, atlassianUserInfo, lookupJiraAccountId
- **Confluence:** searchConfluenceUsingCql, getConfluencePage
- **Slack:** search_messages, get_channel_history, get_thread, list_joined_channels, get_channel_id_by_name, whoami
- **Google:** calendar_get_events, drive_search, drive_get_content
- **Local:** filesystem reads only (Second Brain wiki)
- NEVER call tools that create, edit, transition, post, or send anything.

## Autonomy Principle

This skill runs **fully autonomously** after Step 1. No user prompts during
data gathering (Steps 2–5). If a query fails, log the error silently and
continue with remaining sources. All errors and skipped sources are reported
in the Canvas output.

The only acceptable user prompts are in:
- **Step 1** — confirming the time window
- **Step 7** — presenting the Canvas

## Prerequisites

| Tool | Purpose | How to verify |
|------|---------|---------------|
| Atlassian MCP (`user-atlassian`) | Jira + Confluence | Green dot in Settings > Tools & MCP |
| Slack MCP (`<YOUR_SLACK_MCP_SERVER>`) | Slack search | Green dot in Settings > Tools & MCP |
| Google Workspace MCP (`user-google-workspace`) | Calendar, Drive | Green dot in Settings > Tools & MCP |
| GitHub CLI (`gh`) | PRs, issues, commits | `gh auth status` returns authenticated |
| Second Brain wiki | Local knowledge base | `~/second-brain/wiki/` directory exists |

- **Atlassian cloud ID:** `<YOUR_ATLASSIAN_CLOUD_ID>`
- **GitHub username:** `jaquevan`
- **User identity:** read `Me.md` in the workspace root for name and email

## Workflow

### Step 1: Parse scope

Determine the time window from the user's prompt.

| User says | Window |
|-----------|--------|
| "this week", "weekly summary", "what did I do this week" | Last 7 days |
| "today", "what did I do today" | Today only |
| "this sprint", "current sprint" | Current sprint dates (query Jira `sprint in openSprints()` to resolve) |
| "last two weeks", "past 2 weeks" | Last 14 days |
| A specific range ("since June 1", "June 1 to June 10") | That range |
| No time mentioned | Default to last 7 days |

Store as `START_DATE` and `END_DATE` in ISO 8601 format (`YYYY-MM-DDTHH:mm:ssZ`).
Also store `START_JQL` in `YYYY-MM-DD` format for JQL queries.

### Step 2: Read Second Brain (local, instant)

Read the local wiki at `~/second-brain/` to find recently updated topics.

1. Read `~/second-brain/wiki/log.md` — scan for entries within the time window.
   Extract topic names, dates, and source descriptions.
2. Read `~/second-brain/wiki/index.md` — get the full topic catalog for
   cross-referencing later.
3. For any topics with log entries in the window, read the first 15 lines of
   each page to get the title and summary.

This is the fastest source — filesystem reads complete instantly. Start Tier 2
queries immediately after initiating these reads.

Also scan **agent transcripts** for recent work not captured elsewhere:

Transcript location:
`~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/`

Each chat is a directory containing a `<uuid>.jsonl` file (one JSON object
per line with `role` and `message` fields).

1. List transcript directories modified within the time window:
   ```bash
   find ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/ \
     -maxdepth 1 -type d -newermt "{START_DATE}" | sort
   ```

2. For each matching directory, read the first 3-5 lines of the JSONL to
   extract the user's initial query and the assistant's approach.

3. Extract: what was worked on, skills built/modified, investigations,
   decisions made. Skip short Q&A or exploratory chats.

Cap at 10 transcripts. This captures undocumented work done in Cursor
agent conversations that hasn't reached Jira, GitHub, or Slack yet.

### Step 3: Fire parallel MCP queries (all at once)

Launch **all six** of these queries in a single parallel batch. Do not wait
for one to finish before starting another.

#### 3a. Jira — assigned and updated tickets

Server: `user-atlassian`

```
searchJiraIssuesUsingJql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  jql = "assignee = currentUser() AND updated >= '{START_JQL}' ORDER BY updated DESC",
  fields = ["summary", "status", "issuetype", "updated", "priority", "project",
            "customfield_10020"],
  maxResults = 50
)
```

Also search for issues where the user is the reporter:

```
searchJiraIssuesUsingJql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  jql = "reporter = currentUser() AND created >= '{START_JQL}' ORDER BY created DESC",
  fields = ["summary", "status", "issuetype", "created", "project"],
  maxResults = 25
)
```

Categorize results:
- **Completed** — statusCategory = Done, resolved in the window
- **In Progress** — statusCategory = In Progress
- **Created** — issues the user created in the window

#### 3b. GitHub — PRs, issues, commits

Use the `gh` CLI (shell commands). Fire these in parallel:

```bash
gh search prs --author="jaquevan" --created="{START_JQL}..{END_JQL}" \
  --json title,url,state,createdAt,repository --limit 50

gh search prs --reviewed-by="jaquevan" --created="{START_JQL}..{END_JQL}" \
  --json title,url,state,createdAt,repository --limit 25

gh search issues --author="jaquevan" --created="{START_JQL}..{END_JQL}" \
  --json title,url,state,createdAt,repository --limit 25

gh api "search/commits?q=author:jaquevan+committer-date:{START_JQL}..{END_JQL}&per_page=50&sort=committer-date" \
  --jq '.items[] | {message: .commit.message, date: .commit.committer.date, repo: .repository.full_name, url: .html_url}'
```

#### 3c. Google Calendar — meetings attended

Server: `user-google-workspace`

```
calendar_get_events(
  time_min = "{START_DATE}",
  time_max = "{END_DATE}",
  max_results = 50
)
```

Extract: event titles, dates, attendee counts. Filter out declined events.

#### 3d. Slack — messages sent

Server: `<YOUR_SLACK_MCP_SERVER>`

```
search_messages(
  query = "from:me after:{START_JQL}",
  sort = "timestamp",
  limit = 100
)
```

Group results by channel. Note which channels had the most activity and
which threads generated discussion.

#### 3e. Google Drive — recently modified docs

Server: `user-google-workspace`

```
drive_search(
  query = "modifiedTime > '{START_DATE}'",
  max_results = 25
)
```

Extract: document names, types, last modified dates, and web links.

#### 3f. Confluence — pages contributed to

Server: `user-atlassian`

```
searchConfluenceUsingCql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  cql = "contributor = currentUser() AND lastmodified >= now('-7d') AND type = page",
  limit = 25
)
```

Adjust the `now('-Nd')` value to match the user's time window.

### Step 4: Optional detail follow-up (capped)

After the parallel sweep completes, fetch details for **at most 5 high-signal
items** across all sources. This prevents runaway context gathering.

Candidates for follow-up:

| Source | Condition | Follow-up tool |
|--------|-----------|----------------|
| Jira | Ticket has > 3 status changes or is an epic | `getJiraIssue` with `fields = ["comment", "description"]` |
| Slack | Thread has > 5 replies | `get_thread` for the thread |
| Drive | Doc is a Google Doc (not spreadsheet/PDF) with recent edits | `drive_get_content` for the doc |
| Confluence | Page was modified multiple times | `getConfluencePage` for full content |

Skip this step entirely if the user asked for "today" (short window, detail
is unnecessary).

### Step 5: Deduplicate and theme

Cross-reference results to avoid double-counting the same work:

1. **Jira key matching** — scan PR titles, Slack messages, and Drive doc names
   for Jira issue keys (e.g. `<YOUR_JIRA_PROJECT>-123`). Group items that reference the
   same ticket.
2. **URL matching** — detect shared links across Slack messages, Drive docs,
   and Confluence pages.
3. **Keyword clustering** — group remaining items by project or topic keywords.

Build **themes** — each theme is a cluster of related activity across sources.
A theme has:
- A short descriptive name (e.g. "MaaS onboarding flow redesign")
- The sources that contributed to it (icons/labels)
- The individual items within it

Items that don't cluster into a theme remain as standalone entries under their
source section.

### Step 6: Build Canvas

Read the Canvas skill and follow its instructions to create a `.canvas.tsx`
file. The canvas location is:
`/Users/<user>/.cursor/projects/<workspace>/canvases/work-context.canvas.tsx`

Embed all gathered data inline in the canvas file.

**Canvas sections:**

1. **Header** — "Work Context" title, date range, generated timestamp
2. **Stats row** — one stat per source with counts:
   - Jira: tickets touched
   - GitHub: PRs opened / reviewed, commits
   - Calendar: meetings attended
   - Slack: messages sent, channels active in
   - Drive: docs modified
   - Confluence: pages contributed to
   - Second Brain: topics updated
   - Agent transcripts: conversations with substantive work
   Omit any source that returned zero results or was skipped.
3. **Themes section** — cards for each cross-source theme, showing the theme
   name, contributing sources, and key items. This is the primary content.
4. **Per-source detail** — for items that didn't cluster into themes, show
   them under their source heading. Use a mix of card styles and open
   sections for visual variety.
5. **Coverage footer** — small text listing which sources were included and
   which were skipped (with reason).

**Canvas rules:**
- Import only from `cursor/canvas`. No npm packages, no fetch calls.
- Use `useHostTheme()` tokens for all colors. No hardcoded hex.
- No emojis, no gradients, no box-shadows.
- Default-export the top-level component.
- Omit sections with no data — never render empty states.

### Step 7: Summarize in chat

Alongside the canvas, provide a brief text summary:

- Top 3–5 themes with one-line descriptions
- Key stats (total tickets, PRs, meetings, etc.)
- A link to the canvas for the full breakdown
- Which sources were skipped, if any

## Fallback Behavior

| Source | Primary tool | Fallback |
|--------|-------------|----------|
| Second Brain | Filesystem read (`~/second-brain/`) | Skip; note in coverage footer |
| Agent transcripts | Filesystem read + find | Skip; note in coverage footer |
| Jira | `searchJiraIssuesUsingJql` (user-atlassian) | Try `search` (Rovo) as fallback |
| GitHub | `gh` CLI | Skip; note in coverage footer |
| Google Calendar | `calendar_get_events` (user-google-workspace) | Skip; note in coverage footer |
| Slack | `search_messages` (<YOUR_SLACK_MCP_SERVER>) | Skip; note in coverage footer |
| Google Drive | `drive_search` (user-google-workspace) | Skip; note in coverage footer |
| Confluence | `searchConfluenceUsingCql` (user-atlassian) | Skip; note in coverage footer |

Always report which sources were unavailable:

> Sources not available for this summary: {list}. The canvas reflects only the
> sources that were reachable.

## Common Mistakes

| Problem | Fix |
|---------|-----|
| Sequential data gathering | Fire ALL Tier 2 queries in a single parallel batch. Never wait for one source before starting another. |
| Asking the user during Steps 2–5 | Gather all data autonomously. Only prompt in Step 1 (scope) and Step 7 (results). |
| Dumping raw data without themes | Always run the deduplication and theming pass (Step 5). The Canvas should tell a story, not list raw API results. |
| Double-counting across sources | A PR that closes a Jira ticket is one piece of work. Use Jira key matching to group them. |
| Fetching too many details in Step 4 | Cap at 5 follow-up requests. The overview should be fast — users can drill into specifics later. |
| Omitting skipped sources | Always report which sources were unavailable in both the Canvas footer and the chat summary. |
| Hardcoded colors or emojis in Canvas | Use `useHostTheme()` tokens. No hex values, no emojis, no gradients. |
| Rendering empty Canvas sections | If a source returned nothing, omit that section entirely. |
| Forgetting to check Second Brain first | Local reads are instant. Always start with Step 2 before or concurrently with Step 3. |
| Including trivial agent chats | Only include transcripts with substantive work (skills built, files changed, investigations). Skip short Q&A. |
| Using wrong MCP server names | Jira/Confluence: `user-atlassian`. Slack: `<YOUR_SLACK_MCP_SERVER>`. Google: `user-google-workspace`. |
