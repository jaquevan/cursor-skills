---
name: meeting-prep
description: >-
  Cross-source 1:1 meeting prep that pulls Slack DMs, calendar history, Jira
  activity, Drive docs, and Second Brain context for a specific person into a
  Canvas with prioritized talking points. Use when the user says "prep for my
  Zack 1:1", "meeting prep for Andy", "prep for my 1:1 with <name>", "prepare
  for my meeting with <name>", "what should I talk about with <name>", or asks
  to prepare for a meeting with a specific person.
disable-model-invocation: true
---

# Meeting Prep

Orchestrates existing skills (`slack-summary`, `source-reader`, `work-context`
patterns) to build a cross-source prep brief for a 1:1 meeting. Output is an
interactive Canvas with prioritized talking points.

## Skill Composition

This skill composes rather than reimplements. Each data-gathering step
delegates to an existing skill's logic:

| Step | Delegates to | What it provides |
|------|-------------|-----------------|
| Slack DMs | `slack-summary` Steps 2-5 | Thread grouping, talking point priority (high/medium/low), accuracy rules |
| Meeting note docs | `source-reader` | Google Doc extraction from URLs found in calendar events |
| MCP patterns | `work-context` | Server names, cloud ID, read-only constraint, graceful degradation |
| Agent transcripts | Local filesystem | Search past Cursor agent conversations for undocumented work context related to the person |

## Read-Only Constraint

This skill MUST NEVER write, create, update, or modify data in any external
system. All MCP tool calls must be read-only operations. See `work-context`
for the full allowed operations list.

## Autonomy Principle

This skill runs **fully autonomously** after Step 1. No user prompts during
data gathering (Steps 2-6). If a query fails, log the error silently and
continue with remaining sources.

The only acceptable user prompts are in:
- **Step 1** — identifying the person
- **Step 8** — presenting the Canvas

## Prerequisites

Same as `work-context`. Additionally:
- The person must appear as a calendar attendee, Slack contact, or Jira user

## Workflow

### Step 1: Identify the person

Extract the person's name from the user's prompt.

| User says | Person |
|-----------|--------|
| "prep for my Zack 1:1" | Zack |
| "meeting prep for Andy Braren" | Andy Braren |
| "what should I talk about with Megan" | Megan |
| "prep for my next 1:1" | Ask the user who the meeting is with |

Read `Me.md` in the workspace root for the user's own name, email, and
timezone.

### Step 2: Resolve person across systems

Given the person's name, resolve their identity in each system. Fire these
in parallel:

#### 2a. Calendar — find email and meeting history

Server: `user-google-workspace`

```
calendar_get_events(
  query = "<person name>",
  time_min = "<30 days ago>",
  time_max = "<7 days from now>",
  max_results = 25
)
```

From the results:
- Match attendee names to find their **email address** (e.g.,
  `<MANAGER_EMAIL>`)
- Find the **last completed meeting** with this person = `LAST_MEETING`
- Find the **next upcoming meeting** with this person = `NEXT_MEETING`
- The lookback window is: `LAST_MEETING` to now

If no past meeting is found, default the lookback window to 14 days.

#### 2b. Jira — find account ID

Server: `user-atlassian`

```
lookupJiraAccountId(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  searchString = "<person name or email>"
)
```

Store as `THEIR_JIRA_ID`.

#### 2c. Slack — determine display name

The person's Slack display name is usually their first name or a variation.
Use the email from Step 2a to search:

```
search_messages(
  query = "from:<first name>",
  limit = 5
)
```

Verify the sender matches by checking the results. Store as
`THEIR_SLACK_NAME`.

### Step 3: Extract doc links from calendar events

Scan the `description` field of all calendar events found in Step 2a for
Google Doc/Slides/Drive URLs. Use `source-reader`'s pattern matching:

| Pattern | Source type |
|---------|-----------|
| `docs.google.com/document/d/<id>` | Google Doc |
| `docs.google.com/presentation/d/<id>` | Google Slides |
| `drive.google.com/file/d/<id>` | Google Drive file |

Collect all unique URLs for extraction in Step 5.

### Step 4: Fire parallel data queries

Launch **all** of these in a single parallel batch. Do not wait for one to
finish before starting another.

#### 4a. Slack DMs — follow `slack-summary` logic

Server: `<YOUR_SLACK_MCP_SERVER>`

Follow `slack-summary` Steps 2-5 verbatim, scoped to this person:

1. Search both sides of the DM conversation:
   ```
   search_messages(query = "from:<their name>", sort = "timestamp", limit = 100)
   search_messages(query = "to:<their name>", sort = "timestamp", limit = 100)
   ```

2. **Group messages into threads** by topic — apply `slack-summary` Step 4
   accuracy rules:
   - Every bullet must correspond to specific messages
   - Use names, terms, and details exactly as they appear
   - If a message is ambiguous, preserve the ambiguity
   - Do not merge details from different messages unless clearly the same topic

3. **Generate talking points** — apply `slack-summary` Step 5 priority logic:
   - **High:** items they explicitly asked about or are waiting on
   - **Medium:** topics discussed but without clear resolution
   - **Low:** context items worth mentioning but not urgent

#### 4b. Jira — shared tickets

Server: `user-atlassian`

```
searchJiraIssuesUsingJql(
  cloudId = "<YOUR_ATLASSIAN_CLOUD_ID>",
  jql = "(assignee = '{THEIR_JIRA_ID}' OR reporter = '{THEIR_JIRA_ID}') AND updated >= '{LOOKBACK_START}' ORDER BY updated DESC",
  fields = ["summary", "status", "issuetype", "updated", "priority", "project"],
  maxResults = 25
)
```

If `THEIR_JIRA_ID` was not resolved, skip this step.

#### 4c. Drive — shared docs

Server: `user-google-workspace`

```
drive_search(
  query = "'<their email>' in writers OR fullText contains '<person name>'",
  max_results = 15
)
```

#### 4d. Second Brain — log scan

Read `~/second-brain/wiki/log.md` and scan for entries mentioning the
person's name within the lookback window.

#### 4e. Agent transcripts — undocumented work context

Search past Cursor agent conversations for context related to this person
that may not have made it to Jira, Slack, or Drive yet.

Transcript location:
`~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/`

Each chat is a directory containing a `<uuid>.jsonl` file with the full
conversation (one JSON object per line, with `role` and `message` fields).

**Search strategy:**

1. List transcript directories sorted by modification time to find recent
   conversations (within the lookback window):
   ```bash
   ls -lt ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/ | head -15
   ```

2. Use ripgrep to search across all recent transcripts for the person's name:
   ```bash
   rg -l "<person name>" ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/
   ```

3. For each matching transcript, read the first 3-5 lines to extract the
   user's initial query and the assistant's approach. This gives the topic
   of the conversation without reading the entire file.

**What to extract:**
- What the user was working on related to this person
- Decisions made or approaches taken that haven't been documented elsewhere
- Open questions or unfinished work that could become talking points

**Cap:** Read at most 5 matching transcripts to avoid runaway context.

### Step 5: Extract linked doc content

For each unique doc URL found in Step 3 (up to 3 docs), delegate to
`source-reader` for extraction:

- Follow `source-reader`'s source detection table to determine the type
- Use `source-reader`'s extraction instructions for that type
- Capture the extracted text as "last meeting context"

Cap at 3 docs to avoid runaway context gathering.

### Step 6: Merge talking points

Combine talking points from all sources into a unified priority list:

1. Start with Slack-derived talking points (from Step 4a)
2. Add **Jira open items** as Medium priority:
   - Tickets in progress that both people touch
   - Tickets with status changes in the window
3. Add **doc open questions** from extracted meeting notes as Low priority
4. Deduplicate: if a Slack thread references a Jira ticket, merge them into
   a single talking point
5. Sort: High first, then Medium, then Low

### Step 7: Build Canvas

Read the Canvas skill and follow its instructions to create a `.canvas.tsx`
file at:
`/Users/<user>/.cursor/projects/<workspace>/canvases/meeting-prep.canvas.tsx`

Embed all gathered data inline.

**Canvas sections:**

1. **Header** — "Prep: Evan / \<Person\>", next meeting time, lookback window
2. **Talking points** — unified priority cards (high/medium/low) with source
   attribution and detail text. This is the primary content.
3. **Slack threads** — grouped by topic (reuse `slack-summary` thread
   grouping). Each thread card shows the theme, date range, and key points.
4. **Shared Jira tickets** — table with key, summary, status, last updated
5. **Meeting note context** — extracted content from linked docs
   (via `source-reader`), summarized as key decisions and open questions
6. **Agent context** — summaries of recent Cursor agent conversations
   related to this person (undocumented work, decisions in progress)
7. **Last meeting** — date and title of previous meeting with this person
8. **Coverage footer** — which sources contributed data

**Canvas rules:**
- Import only from `cursor/canvas`. No npm packages, no fetch calls.
- Use `useHostTheme()` tokens for all colors. No hardcoded hex.
- No emojis, no gradients, no box-shadows.
- Default-export the top-level component.
- Omit sections with no data.

### Step 8: Summarize in chat

Alongside the canvas, provide a brief text summary:

- Top 3 talking points with one-line descriptions
- Next meeting time
- A link to the canvas for the full prep brief
- Which sources were skipped, if any

## Fallback Behavior

| Source | Primary tool | Fallback |
|--------|-------------|----------|
| Calendar | `calendar_get_events` | Default to 14-day lookback if no past meeting found |
| Slack | `search_messages` | Skip if person can't be found in Slack |
| Jira | `searchJiraIssuesUsingJql` | Skip if `lookupJiraAccountId` fails |
| Drive | `drive_search` | Skip; note in coverage footer |
| Second Brain | Filesystem read | Skip; note in coverage footer |
| Agent transcripts | Filesystem read + ripgrep | Skip; note in coverage footer |
| Linked docs | `source-reader` extraction | Skip individual docs that fail; note in footer |

Always report which sources were unavailable:

> Sources not available for this prep: {list}. The canvas reflects only the
> sources that were reachable.

## Common Mistakes

| Problem | Fix |
|---------|-----|
| Reimplementing Slack thread grouping | Follow `slack-summary` Steps 2-5 verbatim. Do not invent a new grouping algorithm. |
| Reimplementing doc extraction | Delegate to `source-reader`. Do not write custom Google Doc parsing. |
| Fixed lookback window | Use time since last meeting with this person. Only default to 14 days if no past meeting is found. |
| Asking the user during Steps 2-6 | Gather all data autonomously. Only prompt in Step 1 and Step 8. |
| Adding context from training data | Apply `slack-summary` accuracy rules: every claim must trace to a retrieved message or extracted doc. |
| Fetching too many linked docs | Cap at 3 doc extractions. Users can drill into specifics later. |
| Using wrong MCP server names | Jira/Confluence: `user-atlassian`. Slack: `<YOUR_SLACK_MCP_SERVER>`. Google: `user-google-workspace`. |
