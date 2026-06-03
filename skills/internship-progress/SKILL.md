---
name: internship-progress
description: >
  Aggregates meeting notes, skills created, standups, learning notes, and open
  action items from ~/Projects/notes/ and ~/.cursor/skills/ into a rolling
  internship progress log. Use when the user says "update my progress log",
  "what have I done this week", "internship summary", "generate my progress
  report", "what skills have I built", or "what action items are still open".
license: MIT
metadata:
  author: ejaquez
  version: 1.0.0
  category: productivity
  tags: [internship, progress, tracking, aggregation]
---

# Internship Progress

Scans your notes repo and skills directory to build a rolling, auto-updated
log of everything accomplished during your internship.

## What It Aggregates

| Source | What it captures |
|--------|-----------------|
| `~/Projects/notes/meetings/` | Meeting dates, attendees, decisions made |
| `~/Projects/notes/standups/` | Daily yesterday/today/blockers entries |
| `~/Projects/notes/learning/` | Topics studied, skills documented |
| `~/Projects/notes/notes/` | Freeform captures |
| `~/.cursor/skills/` | Skills created (folder names + descriptions) |
| All notes | Open action items (`- [ ]` tasks not yet checked off) |

---

## Workflow

### Step 1: Determine update mode

| Mode | Trigger | Output |
|------|---------|--------|
| **Full update** | "update my progress log", "generate report" | Rewrites `progress/internship-log.md` |
| **Weekly summary** | "what have I done this week" | Returns a chat summary (no file write) |
| **Open items** | "what action items are still open" | Returns only unchecked tasks |
| **Skills inventory** | "what skills have I built" | Returns skills list only |

### Step 2: Collect data

**Meetings** — For each file in `meetings/`, extract:
- `title`, `date`, `tags` from frontmatter
- Decisions (text inside `.callout-important` blocks)
- Attendees from the Context table

**Standups** — For each file in `standups/`, extract:
- Date, Today section, Blockers section

**Learning notes** — For each file in `learning/`, extract:
- `title`, `date`, `tags`
- TL;DR line

**Skills built** — For each folder in `~/.cursor/skills/`, read `SKILL.md`
frontmatter and extract `name` and the first sentence of `description`.

**Open action items** — Grep all `.md` files for `- [ ]` lines.
Record the task text, the note it came from, and that note's date.
Ignore items in `progress/internship-log.md` itself.

### Step 3: Write the progress log

Write to `~/Projects/notes/progress/internship-log.md`.
Create the `progress/` directory if it doesn't exist.

Use this structure:

```markdown
---
title: "Internship Progress Log"
date: <today>
author: "ejaquez"
categories: [progress]
tags: [internship, progress]
---

**Last updated:** <date and time>

## Contents
- [Skills Built](#skills-built)
- [Meetings](#meetings)
- [What I Learned](#what-i-learned)
- [Open Action Items](#open-action-items)
- [Activity Timeline](#activity-timeline)

---

## Skills Built

| Skill | Description | Created |
|-------|-------------|---------|
| `notetaking` | Converts raw notes... | <date of first commit or folder mtime> |
| `tag-scanner` | ... | ... |

---

## Meetings

| Date | Title | Attendees | Key Decision |
|------|-------|-----------|--------------|
| 2026-06-03 | [Intern Sync](../meetings/2026-06-03-intern-sync.md) | Zack, Priya | No MCP without approval |

---

## What I Learned

| Date | Topic | TL;DR |
|------|-------|-------|
| 2026-06-03 | [Cursor Skills](../learning/skill-notetaking-2026-06-03.md) | ... |

---

## Open Action Items

| Task | From | Due |
|------|------|-----|
| Check gh CLI availability | [Intern Sync](../meetings/...) | 2026-06-04 |

::: {.callout-tip title="Progress Check"}
<N> action items open across <M> notes. Oldest unresolved item: <date>.
:::

---

## Activity Timeline

A chronological list of all notes created, newest first.

| Date | Type | Title |
|------|------|-------|
| 2026-06-03 | meeting | Intern Sync — Cursor Skills & Presentations |
| 2026-06-03 | standup | Standup 2026-06-03 |
```

### Step 4: Commit

```bash
cd ~/Projects/notes
git add progress/internship-log.md
git commit -m "chore: update internship progress log"
git push
```

Git must be configured before this works. See `SETUP.md` in the cursor-skills
repo if `git config user.email` returns nothing.

---

## Composing with Other Skills

- Run after `notetaking` saves a new note to keep the log current
- Run after `tag-scanner` to include freshly linked notes
- The log itself can feed the `notetaking` skill's "document this skill" pattern

---

## Weekly Cadence (Suggested)

Say "update my progress log" at the end of each week before your intern sync.
The log becomes your running record for:
- End-of-internship retrospective
- Performance review conversations
- Portfolio/resume bullet points
- Handoff documentation when the internship ends
