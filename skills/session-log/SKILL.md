---
name: session-log
description: >-
  Scans today's Cursor and Claude agent transcripts, distills what was worked
  on, changed, deleted, and why, then creates a tagged daily entry in the
  Second Brain wiki. Use when the user says "log my sessions", "what did I do
  in cursor today", "save my session history", "daily session log", "log
  today's work", "end of day log", "journal my sessions", or asks to record
  what they worked on in agent conversations.
disable-model-invocation: true
---

# Session Log

Scans today's agent transcripts from Cursor and Claude, extracts a brief
summary of what was worked on, and writes a tagged daily entry into the
Second Brain wiki. Composes with `second-brain-ingest` for wiki integration.

## Skill Composition

| Step | Delegates to | What it provides |
|------|-------------|-----------------|
| Wiki page creation | `second-brain-ingest` Steps 2-7 | Cross-linking, index update, log update, internship context |
| Agent transcript reading | `work-context` / `standup-writer` patterns | Transcript location, JSONL format, directory listing |

**What this skill adds:** daily aggregation of all agent sessions **across
all workspaces** into a single structured wiki page with importance scoring,
people detection, carry-forward tracking, and auto-resolve.

## Workflow

### Step 1: Determine the date

Default to today. If the user says "yesterday's sessions" or specifies a
date, use that instead. Store as `TARGET_DATE` in `YYYY-MM-DD` format.

### Step 2: Find agent transcripts for the date

Transcript locations:

**Cursor transcripts (all workspaces):**
Scan all workspace transcript directories under `~/.cursor/projects/`:
```
~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID_1>/agent-transcripts/
~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID_2>/agent-transcripts/
```
Add one line per workspace you want tracked.

**Claude Code transcripts (if available):**
`~/.claude/projects/` — check for any JSONL files modified on `TARGET_DATE`.

List directories modified on the target date across all workspaces:

```bash
for dir in \
  ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID_1>/agent-transcripts \
  ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID_2>/agent-transcripts; do
  find "$dir" -maxdepth 1 -type d -newermt "{TARGET_DATE} 00:00" \
    ! -newermt "{TARGET_DATE} 23:59" 2>/dev/null
done | sort
```

Also check for Claude Code conversations if the directory exists:

```bash
find ~/.claude/projects/ -name "*.jsonl" -newermt "{TARGET_DATE} 00:00" \
  ! -newermt "{TARGET_DATE} 23:59" 2>/dev/null | sort
```

### Step 3: Read and summarize each session

For each transcript found, read the JSONL file and extract:

1. **Topic** — what was the user trying to do? Read the first user message
   (look for `<user_query>` tags or the raw message text).

2. **What was worked on** — scan assistant messages for tool calls that
   reveal actions taken:
   - `Write` / `StrReplace` tool calls = files created or modified
   - `Delete` tool calls = files deleted
   - `Shell` tool calls with `git`, `gh`, `npm` = commands run
   - `CallMcpTool` calls = external system interactions

3. **What changed** — extract file paths from tool calls to build a list
   of files created, modified, and deleted.

4. **Why** — read the assistant's reasoning around each change. Look for
   explanatory text between tool calls that describes intent.

5. **Outcome** — did the session end successfully? Check the last few
   messages for confirmation, errors, or open questions.

**Reading strategy to keep it fast:**
- Read the first 10 lines for the topic and initial context
- Scan for tool call patterns (Write, StrReplace, Delete, Shell, CallMcpTool)
  using ripgrep rather than reading every line:
  ```bash
  rg '"name":"(Write|StrReplace|Delete|Shell|CallMcpTool)"' <transcript.jsonl> | head -30
  ```
- Read the last 10 lines for the outcome
- Skip the middle unless the topic is unclear from the bookends

Cap at 15 transcripts per day.

### Step 3.5: Score importance

After summarizing each session, assign an importance score (1–5) using these
signals additively (start at 1, cap at 5):

| Signal | Boost | Detection |
|--------|-------|-----------|
| Involves manager (your manager) | +2 | Name appears in transcript content or Slack MCP calls reference him |
| Involves senior stakeholder (<COLLEAGUE_1>, <COLLEAGUE_2>, <COLLEAGUE_3>) | +1 | Name appears in transcript |
| Produces a deliverable (PR merged, skill shipped, doc published) | +2 | `git push`, `gh pr create`, file created in a shared repo |
| Carries forward from previous day | +1 per day carried | Matched against yesterday's carried-forward items |
| Session ended blocked or errored | +1 | Outcome = "blocked" or last messages contain errors |
| Touches an active sprint ticket | +1 | Jira ticket key (e.g. <YOUR_JIRA_PROJECT>-*) appears in transcript |
| Pure networking / intro meeting (no deliverables, no follow-ups) | -1 | Session topic is introductions, coffee chat, or meet-and-greet with no action items → also apply `#networking` tag |
| Exploratory / research only | 0 | No boost, no penalty |

**Scoring rules:**
- Minimum score is 1, maximum is 5.
- Sessions scoring 4–5 are marked `[IMPORTANT]` in the output.
- Carried-forward items that reach 3+ days are auto-promoted to score 5 regardless of other signals.

### Step 3.6: Detect people

Scan each session's transcript content for references to key collaborators.
Apply people tags when detected:

| Person | Detection patterns | Tag |
|--------|-------------------|-----|
| Zack (manager) | "<Manager first name>", "<Manager last name>", DM channel with manager, 1:1 calendar event | `#<manager-tag>` |
| <COLLEAGUE_1> | "<Colleague 1 first name>", "<Colleague 1 last name>", project discussions with colleague | `#<colleague-1-tag>` |
| <COLLEAGUE_2> | "<Colleague 2 first name>", "<Colleague 2 last name>" | `#<colleague-2-tag>` |
| <COLLEAGUE_3> | "<Colleague 3 first name>", "<Colleague 3 last name>" | `#<colleague-3-tag>` |
| Group context | 3+ people referenced, standup, retro, team meeting | `#team` |

People tags use the `pf-m-blue` color class (matching tag-scanner conventions).

### Step 4: Build the daily entry

Sort sessions by importance score (highest first). Create a structured
summary with this format:

```markdown
# Session Log — YYYY-MM-DD

**Signal:** <N> important items<, M stale carry-forwards if any>

**Tags:** #daily-log #YYYY-MM-DD #<people-tags> #<status-tags> #<project-tags>

## Summary

<2-3 sentence overview of the day's agent work, leading with the most important item>

## Sessions (sorted by importance)

### 1. [IMPORTANT] <High-score session topic>
- **Importance:** N/5 (<brief reason — e.g. "involves manager + deliverable">)
- **What:** <brief description of work done>
- **Changed:** <files created/modified/deleted>
- **Why:** <reasoning or motivation>
- **Outcome:** <completed / in progress / blocked>

### 2. <Medium-score session topic>
- **Importance:** N/5 (<brief reason>)
- **What:** ...
- **Changed:** ...
- **Why:** ...
- **Outcome:** ...

### 3. <Low-score session topic>
- **Importance:** N/5 (<brief reason — e.g. "networking, no deliverables">)
- **What:** ...
- **Outcome:** ...

## Carried Forward

### [DAY N] <Topic from previous day>
- **Originally:** YYYY-MM-DD
- **Importance:** N/5 (<auto-escalated if 3+ days>)
- **Last status:** <in progress / blocked — details>

## Files Touched

| File | Action | Session |
|------|--------|---------|
| .cursor/skills/work-context/SKILL.md | Created | 1 |
| canvases/work-context.canvas.tsx | Created | 1 |
| .cursor/skills/meeting-prep/SKILL.md | Created | 2 |

## Related

- [<linked wiki pages>](<file>.md)
```

**Output rules:**
- Sessions scoring 4–5 get the `[IMPORTANT]` prefix in their heading.
- Sessions scoring 1 can omit `Changed` and `Why` fields (just `What` + `Outcome`).
- The `## Carried Forward` section only appears if there are carry-forward items.
- The `**Signal:**` line always appears — it's the at-a-glance summary for skimming.

**Tag generation rules:**

Always include:
- `#daily-log`
- `#YYYY-MM-DD` (the date)

**People tags** (auto-detected from Step 3.6, `pf-m-blue` color):
- `#<manager-tag>` — any interaction, message, or reference to Zack/<YOUR_MANAGER_NAME>
- `#<colleague-1-tag>` — <COLLEAGUE_1> references
- `#<colleague-2-tag>` — <COLLEAGUE_2> references
- `#<colleague-3-tag>` — <COLLEAGUE_3> references
- `#team` — group meetings, standups, retros (3+ people)

**Status tags** (derived from importance scoring and outcomes):
- `#blocked` (`pf-m-orange`) — session ended with unresolved blocker
- `#shipped` (`pf-m-green`) — deliverable completed and pushed/shared
- `#carried-forward` (`pf-m-orange`) — item appeared yesterday and is still open
- `#stale` (`pf-m-orange`) — carried forward 3+ days, auto-escalated
- `#decision-made` (`pf-m-green`) — a decision was recorded or committed to
- `#manager-sync` (`pf-m-grey`) — 1:1 or direct feedback loop with manager

**Context tags** (derived from content):
- `#sprint-work` (`pf-m-purple`) — touches an active Jira sprint ticket
- `#networking` (`pf-m-grey`) — intro meetings, coffee chats, no deliverables
- `#skills` — if any skill SKILL.md files were created or modified
- `#canvas` — if any .canvas.tsx files were created
- `#eval` — if eval-related work was done
- `#mcp` — if MCP tools were called for external system interaction
- `#<your-project-tag>` — if <your-project> related work appeared
- `#second-brain` — if wiki pages were created or modified
- `#jira` — if Jira tickets were referenced or modified
- `#github` — if PRs or commits were made
- `#debugging` — if the session involved troubleshooting or fixing errors
- Add any project-specific tags that match existing wiki page slugs

**Tag limits:** 5–10 tags per entry. People and status tags do not count
toward the limit — they are always included when detected. Prefer specific
tags over generic ones.

### Step 4.5: Carry forward unresolved items

Before writing, check for items that should carry forward from previous days.

1. **Read yesterday's log:** Open `~/second-brain/wiki/session-log-{YESTERDAY}.md`
   (calculate YESTERDAY from TARGET_DATE). If it doesn't exist, check the most
   recent session-log file instead.

2. **Extract unresolved items:** Find sessions with `Outcome: in progress` or
   `Outcome: blocked`. Also look for an existing `## Carried Forward` section
   in yesterday's log (items may already be carrying).

3. **Increment carry counter:** For each unresolved item, track how many
   consecutive days it has appeared:
   - If the item's `[DAY N]` marker exists, increment N.
   - If it's new from yesterday (no marker), start at `[DAY 2]`.

4. **Auto-escalate stale items:** If an item reaches DAY 3+:
   - Set its importance to 5 (regardless of other signals).
   - Add `#stale` tag to the daily entry.
   - Move it to the top of the Carried Forward section.

5. **Auto-close dropped items:** If a carried-forward item does NOT appear in
   today's transcripts AND is NOT tagged `#blocked` AND has been absent for
   2 consecutive days, mark it `Resolved (auto-closed — no activity for 2 days)`
   and stop carrying it forward.

6. **Build the Carried Forward section** using this format:
   ```markdown
   ## Carried Forward

   ### [DAY N] <Original session topic>
   - **Originally:** YYYY-MM-DD
   - **Importance:** N/5 (<reason — auto-escalated if 3+ days>)
   - **Last status:** <in progress / blocked — details from last log>
   ```

7. **Skip if empty:** If no items carry forward, omit the section entirely.

### Step 5: Write to Second Brain wiki

Delegate to `second-brain-ingest` Steps 2-7:

1. **Check existing pages** — scan `~/second-brain/wiki/` first 10 lines
   of each .md file for cross-linking decisions (Step 2).

2. **Create the wiki page** at:
   `~/second-brain/wiki/session-log-YYYY-MM-DD.md`

   Follow `second-brain-ingest` Step 3 rules:
   - Start with `# Session Log — YYYY-MM-DD`
   - Add a "Related" section with links to connected wiki pages
   - Add a "Sources" section noting the transcript UUIDs

3. **Update existing pages** — add a link back from any related pages
   in their "Related" section (Step 4).

4. **Update index.md** — add under a "Session Logs" category. Create the
   category if it doesn't exist yet (Step 5).

5. **Update log.md** — append a log entry (Step 6):
   ```
   ## YYYY-MM-DD — Session Log

   **Sessions:** N agent conversations
   **Created:** session-log-YYYY-MM-DD.md — <one-line summary>
   **Tags:** #daily-log #skills #canvas ...
   **Cross-linked with:** <list of updated pages>
   **Category:** Session Logs
   ```

6. **Relate to internship context** — apply `second-brain-ingest` Step 7
   to connect the entry to key projects (<your-project>, <your-project>,
   agent-eval-harness, etc.).

### Step 6: Confirm

Tell the user:
- How many sessions were logged
- The wiki page path
- Which tags were applied
- Which existing wiki pages were cross-linked
- Any sessions that seemed incomplete or had open questions

## Auto-Resolve Rules

This skill operates **without user interaction** by default. No "did you
complete this?" prompts. The importance engine and carry-forward mechanism
replace manual check-ins entirely.

| Rule | Behavior |
|------|----------|
| **No prompt needed** | The session log runs, scores, sorts, and writes. Zero questions asked. |
| **Auto-close carried items** | If a carried-forward item doesn't appear in transcripts for 2 consecutive days AND isn't tagged `#blocked`, mark it as `Resolved (auto-closed)` and stop carrying. |
| **Auto-escalate** | Items carried 3+ days get `#stale`, importance = 5, and appear at the top of Carried Forward. |
| **Daily signal line** | The `**Signal:**` line always appears at the top — count of important items + any stale carry-forwards by name. |
| **Importance replaces manual triage** | You don't need to ask "was this important?" — the scoring table determines it from transcript evidence. |

**What "auto" means in practice:**
- Intro meetings with peers (no action items, no follow-ups) automatically score 1/5 and sink to the bottom. No tagging needed.
- A 1:1 with manager that produces a new task automatically scores 4/5 and gets `[IMPORTANT]` + `#<manager-tag>` + `#manager-sync`.
- A blocked PR that carries for 3 days auto-escalates to 5/5 + `#stale` without any user action.

## Fallback Behavior

| Situation | Handling |
|-----------|---------|
| No transcripts for the date | Tell the user: "No agent sessions found for {date}." |
| Transcript is too short (< 5 lines) | Skip it — likely an abandoned or trivial session |
| Transcript has no tool calls | Still log it if the user query reveals a substantive topic (research, planning, Q&A about a project) |
| Second Brain wiki doesn't exist | Create `~/second-brain/wiki/` and `index.md` / `log.md` if missing |
| Session Log category doesn't exist in index | Create it |
| No previous session log exists (first run) | Skip carry-forward — no items to carry |
| Carried-forward item resolved in today's sessions | Move it from Carried Forward to the regular Sessions list with outcome = "completed" |

## Common Mistakes

| Problem | Fix |
|---------|-----|
| Reading entire transcripts | Use the bookend strategy: first 10 lines + ripgrep for tool calls + last 10 lines. Full reads are too slow for 10+ transcripts. |
| Verbose session summaries | Keep each session to 5 lines: Importance, What, Changed, Why, Outcome. The log is a reference, not a narrative. |
| Missing the "why" | The reasoning is in the assistant's text between tool calls. Don't just list file changes — capture the intent. |
| Too many tags | People + status tags are always included. Context tags cap at 5–8. Prefer specific (#<your-project-tag>) over generic (#coding). |
| Not cross-linking | Always run `second-brain-ingest` Step 7 to connect to internship context. Session logs are most valuable when linked to project pages. |
| Skipping trivial-looking sessions | A session that only asked a question might have surfaced an important insight. Include it if the topic is project-relevant, even without file changes. Score it appropriately (low importance is fine — but still log it). |
| Logging the same day twice | Check if `session-log-YYYY-MM-DD.md` already exists. If so, append new sessions to the existing page rather than overwriting. |
| Asking the user to triage | Never ask "was this important?" or "should I carry this forward?" — the scoring engine decides automatically. |
| Forgetting carry-forward on first run | If no previous session log exists, skip Step 4.5 cleanly. Don't error. |
