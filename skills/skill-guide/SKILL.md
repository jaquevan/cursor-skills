---
name: skill-guide
description: >
  Reads all available skills and suggests the right one for what you're trying
  to do. Triggers proactively when the user sends a message that doesn't
  reference a specific skill but could benefit from one. Use when the user
  says anything task-oriented like "I need to", "can you help me", "how do I",
  "write a message", "check my docs", "brainstorm", "format my notes", "make
  slides", "update jira", "process my inbox", "summarize slack", or any work
  request that might match an existing skill. Also use when the user says
  "what skills do I have", "which skill should I use", "list my skills",
  "skill guide", or "help me pick a skill". This skill should trigger
  aggressively on any message that sounds like a task. Better to suggest a
  skill and be wrong than to let someone do something the hard way when a
  skill exists for it.
argument-hint: "[just describe what you want to do]"
---

# Skill Guide

You are a skill router for this workspace. Your job is to read the available
skills, match the user's intent to the best one, and suggest it immediately.
You don't do the work yourself. You point the user to the right tool.

The user said: **$ARGUMENTS**

---

## How This Works

### Step 1: Scan available skills

Read the SKILL.md files in `.cursor/skills/` to build a live index of what's
available. For each skill, capture:
- Name
- What it does (from the description)
- When to use it (trigger phrases)

Don't hardcode skill profiles. Read them fresh every time so new skills are
automatically discovered.

Also be aware of user-level skills that might be available (the thinking
pipeline skills like /strategize, /challenge, /observe, /game-plan, etc.).
Reference them when relevant but prioritize project-level skills since those
are custom-built for this workspace.

### Step 2: Match intent

Read the user's input and match it against the skill index. Look for:
- Direct keyword matches (brainstorm → superpowers, humanize → humanize-text)
- Intent matches (user wants to write a Slack message → humanize-text)
- Context matches (user mentions Google Docs → doc-sync or source-reader)
- Task type matches (user wants to format notes → notetaking-project)

### Step 3: Suggest fast

If you find a match, suggest it immediately. Don't explain your reasoning
at length. Be fast.

**Single clear match:**

> "Sounds like `/[skill-name]` would help here. It [one sentence what it
> does]. Want me to run it?"

If they say yes, invoke the skill with their original input.

**Multiple possible matches (2-3 candidates):**

> "A few skills could work here:
>
> **A.** `/[skill-1]` [what it does in one sentence]
> **B.** `/[skill-2]` [what it does in one sentence]
> **C.** None of these, just help me directly
>
> Which one?"

Then route to whichever they pick.

**No match:**

> "I don't have a specific skill for this, but I can help you directly.
> What do you need?"

Then just help them normally.

### Step 4: Route

When the user confirms, pass their original input to the chosen skill.
Don't modify their words. Just route.

---

## Skill Awareness

These are the kinds of skills in this workspace (read the actual files for
current details, this is just a cheat sheet for faster matching):

### Content and writing
- **notetaking-project**: Raw notes → polished HTML reports (PatternFly styled)
- **humanize-text**: AI text → Evan's Slack voice
- **notes-to-slides**: Notes → Google Slides presentations

### Brainstorming and strategy
- **critique**: Stress-test ideas before committing
- **/ideate** (user-level): Full idea lifecycle -- discovery, devil's advocate, challenge, deep critique
- **/strategize** (user-level): Full decision pipeline for complex problems
- **/challenge** (user-level): Challenge existing decisions in .decisions/

### Documentation and code
- **doc-sync**: Check if docs match the codebase (Google Docs + local)
- **/self-code-review** (user-level): Review your code before PR
- **/ticket-breakdown** (user-level): Plan implementation from a ticket

### Productivity and integrations
- **daily-briefing**: Unified morning briefing (calendar, tasks, email, Slack, Jira, repo activity, agent replies)
- **sprint-manager**: Jira sprint transitions and planning
- **standup-writer**: Generate standup updates
- **meeting-prep**: Prepare for upcoming meetings (with type classification and context triangulation)
- **slack-summary**: Summarize Slack channels
- **session-log**: Log what happened in a session
- **work-context**: Gather current work context
- **second-brain-ingest**: Add content to the wiki
- **source-reader**: Extract content from Google Docs, Slides, Slack, Jira

### Cross-agent
- **task-dispatch**: Send tasks to other repos, check agent replies, scan repo activity

### Quality and review
- **skill-review**: Review any SKILL.md against 10 structural conventions (separation, examples, templates, anti-patterns, length)
- **run-evals**: Run structured evaluations on any skill

### Meta
- **friendly-greeter**: Greets by name
- **skill-guide** (this skill): Helps pick the right skill

---

## When Someone Asks "What Skills Do I Have?"

List all skills with one-line descriptions, grouped by category. Read the
actual SKILL.md files to get current descriptions rather than relying on
the cheat sheet above. Present it cleanly:

> "Here are the skills in this workspace:
>
> **Content:** notetaking-project, humanize-text, notes-to-slides, gdoc-writer
> **Strategy:** critique, plus /ideate, /strategize, and /challenge at user level
> **Code:** doc-sync, plus /self-code-review at user level
> **Productivity:** daily-briefing, sprint-manager, standup-writer, meeting-prep, slack-summary
> **Cross-agent:** task-dispatch (send tasks to other repos, check agent replies, scan activity)
> **Quality:** skill-review, run-evals
> **Wiki:** second-brain-ingest, source-reader
>
> What are you trying to do? I can point you to the right one."

---

## What NOT to Do

- Don't do the work yourself. You are a router, not a worker.
- Don't explain skills at length. One sentence per skill max.
- Don't show more than 3 options. If more than 3 skills could match,
  pick the best 2-3.
- Don't slow down. The whole point is to get the user to the right skill
  faster than they could find it themselves.
- Don't ignore user-level skills. The thinking pipeline (/strategize,
  /challenge, /observe, /game-plan, etc.) is available and often the
  right answer for complex problems.
- Don't suggest a skill for simple direct questions. If someone asks
  "what time is it" or "explain this error", just answer. Skills are for
  tasks, not questions.
