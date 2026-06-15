# Sprint Manager Reference

## <YOUR_JIRA_PROJECT> Story Point Scale

From the team's Confluence guide: *Guide to Add a Sprint and Story Points to a
<YOUR_JIRA_PROJECT> Jira Ticket* (last updated Jul 23, 2025 by Adela Arreola).

| Points | Effort | Description |
|--------|--------|-------------|
| 1 | Trivial | Minimal effort. Copy changes, config tweaks, simple reviews. Done in under an hour. |
| 2 | Small | A few hours of focused work. Single-component changes, minor design updates. |
| 3 | Medium | A day or two of work. New component, moderate design exploration, or a focused consult. |
| 5 | Large | Multiple days. Multi-component feature, cross-team collaboration, or a research spike. |
| 8 | Very large | A week or more. Full workflow design, extensive prototyping, multi-stakeholder review. |
| 13 | Epic-sized | Multi-week effort. Should likely be broken into smaller stories. |

Use Fibonacci values only: 1, 2, 3, 5, 8, 13.

## Field IDs (<YOUR_JIRA_PROJECT> project)

These are the custom field IDs confirmed for the <YOUR_JIRA_PROJECT> project on
`<YOUR_ATLASSIAN_SITE>`:

| Field | Custom field ID | Write format | Read format |
|-------|----------------|--------------|-------------|
| Sprint | `customfield_10020` | Plain number (sprint ID) | Array of sprint objects |
| Story Points | `customfield_10016` | Plain number | Number or null |

**Cloud ID**: `<YOUR_ATLASSIAN_CLOUD_ID>`
**Board ID**: `11104`

## Known sprint IDs

| Sprint | ID | State | Dates |
|--------|----|-------|-------|
| <YOUR_JIRA_PROJECT> Sprint 40 | 68736 | future | Jun 13 - Jul 10, 2026 |

Update this table as new sprints are discovered during skill execution.

## Manual fallback: Adding story points in the Jira UI

If the MCP cannot edit fields (permissions issue), follow these steps:

1. Open the Jira ticket
2. Click **Edit**
3. Scroll down and locate the **Story Points** field in the **Field Tab** tab
4. Enter the estimate using the scale above
5. Click **Update** to save

## Manual fallback: Adding a sprint in the Jira UI

### Method 1: From the ticket view

1. Open the Jira ticket
2. Click the **Edit** link in the top-left of the ticket body
3. In the Edit modal, click on the **Priority** tab
4. Find the **Sprint** field and click inside it to select a sprint
5. If no dropdown appears, start typing `<YOUR_JIRA_PROJECT>` to search sprints
6. Choose the target sprint
7. Click **Update** to save

### Method 2: From the Backlog view

1. Go to the [<YOUR_JIRA_PROJECT> Backlog View](https://<YOUR_ATLASSIAN_SITE>/jira/software/c/projects/<YOUR_JIRA_PROJECT>/boards/11104/backlog)
2. Locate your issue
3. Right-click the issue and choose the appropriate sprint under **Send to**

## Permissions

If you cannot select a sprint, you may not have the necessary edit permissions
in the Jira project. Contact your team lead (Zack) or a Jira admin.

Sprint assignment only works for **active** or **upcoming** sprints. Closed
sprints cannot receive new tickets.
