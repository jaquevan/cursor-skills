---
name: sprint-manager
description: >-
  Manage <YOUR_JIRA_PROJECT> sprint transitions using the Atlassian MCP. Finds your
  assigned tickets, shows sprint and story point status, and updates tickets
  for the next sprint. Use when the user says "sprint planning", "move tickets
  to sprint", "storypoint my tickets", "sprint review", "what's in my sprint",
  "sprint kickoff prep", "end of sprint", or "sprint transition".
---

# Sprint Manager

Manages sprint transitions for the <YOUR_JIRA_PROJECT> Jira project via the Atlassian MCP.
Finds the user's tickets, presents a sprint dashboard, and batch-updates sprint
assignments and story points.

## Prerequisites

- Atlassian MCP server (`plugin-atlassian-atlassian`) must be connected
- User must have edit permissions on <YOUR_JIRA_PROJECT> tickets

## Workflow

### Step 1: Resolve identity and cloud context

Call both in parallel:

```
atlassianUserInfo()
getAccessibleAtlassianResources()
```

- `atlassianUserInfo` returns the authenticated user's `account_id`
- `getAccessibleAtlassianResources` returns the `cloudId` (use the one for
  `<YOUR_ATLASSIAN_SITE>` — known ID: `<YOUR_ATLASSIAN_CLOUD_ID>`)

### Step 2: Find the user's open tickets

```
searchJiraIssuesUsingJql(
  cloudId = "<cloudId>",
  jql = "project = <YOUR_JIRA_PROJECT> AND assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC",
  fields = ["summary", "status", "priority", "issuetype",
            "customfield_10020", "customfield_10016"],
  maxResults = 50
)
```

**Field mapping:**

| Jira field | Custom field ID | Type |
|---|---|---|
| Sprint | `customfield_10020` | number (sprint ID) for writes, object array for reads |
| Story Points | `customfield_10016` | number |

### Step 3: Discover the target sprint

If the user doesn't specify a sprint, find the next upcoming one:

```
searchJiraIssuesUsingJql(
  cloudId = "<cloudId>",
  jql = "project = <YOUR_JIRA_PROJECT> AND sprint in futureSprints() ORDER BY created DESC",
  fields = ["customfield_10020"],
  maxResults = 1
)
```

Extract the sprint ID and name from `customfield_10020[0]`:

```json
{
  "id": 68736,
  "name": "<YOUR_JIRA_PROJECT> Sprint 40",
  "state": "future",
  "boardId": 11104
}
```

Sprint naming convention: `<YOUR_JIRA_PROJECT> Sprint <number>`

### Step 4: Present the sprint dashboard

Group the user's tickets into three buckets:

1. **Current/active sprint** — tickets in `openSprints()` (need review: carry
   over or close)
2. **Backlog** — tickets with no sprint (candidates for next sprint)
3. **Already in target sprint** — no action needed

Present a table for each group:

```
| Key | Summary | Status | Sprint | Points |
```

For each ticket needing action, note what's missing (sprint, story points, or
both).

### Step 5: Collect user decisions

For each ticket that needs updating, ask the user:

1. **Move to next sprint?** Yes / No / Leave in backlog
2. **Story points?** Suggest a value based on the <YOUR_JIRA_PROJECT> Story Point Scale
   (see [reference.md](reference.md))
3. **Status transition?** If the ticket is in "New" or "Backlog" and being
   moved to a sprint, ask if it should be transitioned (e.g., to "In Progress",
   "Refinement", or "To Do")

Use the AskQuestion tool to collect structured answers when available.

**Story point guidance** — suggest based on ticket scope:

| Points | Effort level | Example |
|---|---|---|
| 1 | Trivial | Copy change, minor config update |
| 2 | Small | Single-component fix, small review |
| 3 | Medium | New component or moderate design work |
| 5 | Large | Multi-component feature, cross-team collab |
| 8 | Very large | Full workflow design, multi-week effort |
| 13 | Epic-sized | Should probably be broken into smaller stories |

### Step 6: Execute updates

For each approved ticket, do two things:

**6a. Update fields** — call `editJiraIssue` for sprint and story points:

```
editJiraIssue(
  cloudId = "<cloudId>",
  issueIdOrKey = "<YOUR_JIRA_PROJECT>-XXXX",
  fields = {
    "customfield_10020": <sprint_id>,
    "customfield_10016": <story_points>
  }
)
```

**Important**: The sprint field expects a plain number (the sprint ID), not an
object. For example: `"customfield_10020": 68736`

Only include fields that are changing. If the user only wants to set story
points, omit the sprint field and vice versa.

**6b. Transition status** — if the user requested a status change, call
`transitionJiraIssue` (on `plugin-atlassian-atlassian`, not `user-atlassian`):

First, get available transitions:

```
getTransitionsForJiraIssue(
  cloudId = "<cloudId>",
  issueIdOrKey = "<YOUR_JIRA_PROJECT>-XXXX"
)
```

Then transition using the matching transition ID:

```
transitionJiraIssue(
  cloudId = "<cloudId>",
  issueIdOrKey = "<YOUR_JIRA_PROJECT>-XXXX",
  transition = { "id": "<transition_id>" }
)
```

**Available <YOUR_JIRA_PROJECT> transitions** (transition IDs are global):

| Transition ID | Target Status | Status Category |
|---------------|--------------|-----------------|
| 11 | New | To Do |
| 21 | Backlog | To Do |
| 31 | Refinement | To Do |
| 41 | To Do | To Do |
| 51 | In Progress | In Progress |
| 61 | Review | In Progress |
| 71 | Closed | Done |

**Important**: Status transitions require `transitionJiraIssue`, not
`editJiraIssue`. You cannot change status via a field edit — Jira enforces
workflow transitions. The `transitionJiraIssue` tool is only available on the
`plugin-atlassian-atlassian` server, not `user-atlassian`.

### Step 7: Confirm results

After all updates, present a before/after summary:

```
| Key | Summary | Before | After |
```

Include a link to each updated ticket:
`https://<YOUR_ATLASSIAN_SITE>/browse/<YOUR_JIRA_PROJECT>-XXXX`

## Common JQL patterns

```
# All my open tickets
project = <YOUR_JIRA_PROJECT> AND assignee = currentUser() AND statusCategory != Done

# My tickets in the current sprint
project = <YOUR_JIRA_PROJECT> AND assignee = currentUser() AND sprint in openSprints()

# My tickets with no sprint
project = <YOUR_JIRA_PROJECT> AND assignee = currentUser() AND sprint is EMPTY AND statusCategory != Done

# My tickets missing story points
project = <YOUR_JIRA_PROJECT> AND assignee = currentUser() AND cf[10016] is EMPTY AND statusCategory != Done

# All tickets in a specific sprint
project = <YOUR_JIRA_PROJECT> AND sprint = "<YOUR_JIRA_PROJECT> Sprint 40"

# Future sprints
project = <YOUR_JIRA_PROJECT> AND sprint in futureSprints()
```

## Edge cases

- **No tickets found**: Confirm the user's account is correct via
  `atlassianUserInfo`, then suggest broader JQL (e.g. remove `assignee` filter)
- **Sprint not open yet**: Use `futureSprints()` JQL function to find upcoming
  sprints
- **Permission denied on edit**: Fall back to manual instructions — see
  [reference.md](reference.md) for the step-by-step Jira UI method
- **Field ID mismatch**: If `customfield_10016` or `customfield_10020` fail,
  use `getJiraIssueTypeMetaWithFields` to discover the correct field IDs for
  the <YOUR_JIRA_PROJECT> project
- **Status not changing**: Status requires `transitionJiraIssue` (workflow
  transition), not `editJiraIssue` (field edit). Use the transition IDs from
  the table in Step 6b. The tool is only on `plugin-atlassian-atlassian`.
- **Ticket moved to sprint but still shows "New"**: Always ask about status
  transition when moving tickets to a sprint. A ticket in Sprint 40 with
  status "New" is confusing — it should be at least "To Do" or "In Progress".

## Additional resources

- <YOUR_JIRA_PROJECT> Story Point Scale and manual fallback instructions:
  [reference.md](reference.md)
