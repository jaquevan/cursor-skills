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

**What this skill adds:** daily aggregation of all agent sessions into a
single structured wiki page with tags, change tracking (created/modified/
deleted), and reasoning capture.

## Workflow

### Step 1: Determine the date

Default to today. If the user says "yesterday's sessions" or specifies a
date, use that instead. Store as `TARGET_DATE` in `YYYY-MM-DD` format.

### Step 2: Find agent transcripts for the date

Transcript locations:

**Cursor transcripts:**
`~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/`

**Claude Code transcripts (if available):**
`~/.claude/projects/` — check for any JSONL files modified on `TARGET_DATE`.

List directories modified on the target date:

```bash
find ~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/ \
  -maxdepth 1 -type d -newermt "{TARGET_DATE} 00:00" \
  ! -newermt "{TARGET_DATE} 23:59" | sort
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

### Step 4: Build the daily entry

Create a structured summary with this format:

```markdown
# Session Log — YYYY-MM-DD

**Tags:** #daily-log #<tool-tags> #<project-tags>

## Summary

<2-3 sentence overview of the day's agent work>

## Sessions

### 1. <Session topic>
- **What:** <brief description of work done>
- **Changed:** <files created/modified/deleted>
- **Why:** <reasoning or motivation>
- **Outcome:** <completed / in progress / blocked>

### 2. <Session topic>
- **What:** ...
- **Changed:** ...
- **Why:** ...
- **Outcome:** ...

## Files Touched

| File | Action | Session |
|------|--------|---------|
| .cursor/skills/work-context/SKILL.md | Created | 1 |
| canvases/work-context.canvas.tsx | Created | 1 |
| .cursor/skills/meeting-prep/SKILL.md | Created | 2 |

## Related

- [<linked wiki pages>](<file>.md)
```

**Tag generation rules:**

Always include:
- `#daily-log`
- `#YYYY-MM-DD` (the date)

Add based on content:
- `#skills` — if any skill SKILL.md files were created or modified
- `#canvas` — if any .canvas.tsx files were created
- `#eval` — if eval-related work was done
- `#mcp` — if MCP tools were called for external system interaction
- `#prototype-creator` — if prototype-creator related work appeared
- `#second-brain` — if wiki pages were created or modified
- `#jira` — if Jira tickets were referenced or modified
- `#github` — if PRs or commits were made
- `#debugging` — if the session involved troubleshooting or fixing errors
- Add any project-specific tags that match existing wiki page slugs

Limit to 5-8 tags per entry. Prefer specific tags over generic ones.

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
   to connect the entry to key projects (prototype-creator, decision-kit,
   agent-eval-harness, etc.).

### Step 6: Confirm

Tell the user:
- How many sessions were logged
- The wiki page path
- Which tags were applied
- Which existing wiki pages were cross-linked
- Any sessions that seemed incomplete or had open questions

## Fallback Behavior

| Situation | Handling |
|-----------|---------|
| No transcripts for the date | Tell the user: "No agent sessions found for {date}." |
| Transcript is too short (< 5 lines) | Skip it — likely an abandoned or trivial session |
| Transcript has no tool calls | Still log it if the user query reveals a substantive topic (research, planning, Q&A about a project) |
| Second Brain wiki doesn't exist | Create `~/second-brain/wiki/` and `index.md` / `log.md` if missing |
| Session Log category doesn't exist in index | Create it |

## Common Mistakes

| Problem | Fix |
|---------|-----|
| Reading entire transcripts | Use the bookend strategy: first 10 lines + ripgrep for tool calls + last 10 lines. Full reads are too slow for 10+ transcripts. |
| Verbose session summaries | Keep each session to 4 lines: What, Changed, Why, Outcome. The log is a reference, not a narrative. |
| Missing the "why" | The reasoning is in the assistant's text between tool calls. Don't just list file changes — capture the intent. |
| Too many tags | Cap at 5-8 tags. Prefer specific (#prototype-creator) over generic (#coding). |
| Not cross-linking | Always run `second-brain-ingest` Step 7 to connect to internship context. Session logs are most valuable when linked to project pages. |
| Skipping trivial-looking sessions | A session that only asked a question might have surfaced an important insight. Include it if the topic is project-relevant, even without file changes. |
| Logging the same day twice | Check if `session-log-YYYY-MM-DD.md` already exists. If so, append new sessions to the existing page rather than overwriting. |
