---
name: task-dispatch
description: >
  Cross-agent task dispatch system. Send tasks to other repos, check for
  agent replies, scan repo activity (git commits, agent sessions), and
  manage bidirectional conversations between the claw and agents in other
  workspaces via BRAIN_TASKS.md files. Use when the user says "send a task
  to", "dispatch to", "add a task to", "check agent replies", "what tasks
  are pending", "scan my repos", "what have I been working on", "project
  activity", "check on my other projects", or mentions dispatching work to
  another repo or checking what agents have done.
argument-hint: "[repo name] [task description] or 'check replies' or 'scan repos'"
---

# Task Dispatch

You manage cross-agent communication between the claw and agents in other
repos. Tasks are dispatched via `BRAIN_TASKS.md` files that live in target
repo roots. Repo agents read tasks, do work, and reply -- creating a
bidirectional conversation channel.

The user's input is: **$ARGUMENTS**

---

## Input Detection

1. **Dispatch**: "send a task to prototype-creator", "next time I open
   rhoai-prototypes I need to...", "add a task to archie"
   --> Dispatch mode

2. **Check replies**: "check agent replies", "any replies from my repos",
   "what did agents do"
   --> Reply check mode

3. **Scan activity**: "what have I been working on", "scan my repos",
   "project activity", "repo status"
   --> Scan mode

4. **List tasks**: "what tasks are pending in prototype-creator", "list
   tasks for archie"
   --> List mode

5. **Empty**: Ask what they want to do.

---

## Configuration

**Projects directory:** `~/Desktop/`

This is where Evan's project repos live (prototype-creator, rhoai-prototypes,
archie, automated-usability-testing, my-cursor-claw, etc.).

---

## Dispatch Mode

1. Confirm the repo name and task description with the user before dispatching.
2. Run:

```bash
python3 .cursor/skills/task-dispatch/scripts/dispatch_task.py \
  <repo_name> "<task description>" \
  --repos-dir ~/Desktop/ \
  --context "<optional context>"
```

3. After dispatching, check if the target repo has the Brain Tasks
   instruction block in its `.cursor/rules/` or `CLAUDE.md`. If not, offer
   to add it:

> "This is the first task dispatched to [repo]. Want me to add the
> instruction block so the agent there knows how to read and reply to
> tasks?"

If yes, read `scripts/claw_tasks_instruction.md` and add it to the target
repo's `.cursor/rules/` as a new rule file or append to existing `CLAUDE.md`.

---

## Reply Check Mode

Run:

```bash
python3 .cursor/skills/task-dispatch/scripts/dispatch_task.py \
  --check-replies --repos-dir ~/Desktop/
```

Present unread agent replies grouped by repo. For each reply:
- Show the task and full conversation thread
- Ask how to respond (reply back, mark complete, or note for later)

To reply:

```bash
python3 .cursor/skills/task-dispatch/scripts/dispatch_task.py \
  <repo_name> --reply <N> --reply-message "response" --repos-dir ~/Desktop/
```

To complete:

```bash
python3 .cursor/skills/task-dispatch/scripts/dispatch_task.py \
  <repo_name> --complete <N> --repos-dir ~/Desktop/
```

---

## Scan Mode

Run:

```bash
python3 .cursor/skills/task-dispatch/scripts/scan_repos.py \
  --repos-dir ~/Desktop/ --days 7
```

This scans four sources across all repos:
1. **Git commits** -- recent commit messages and dates
2. **Claude Code sessions** -- first user prompt from each session
3. **Cursor agent transcripts** -- first user prompt from each session
4. **BRAIN_TASKS.md** -- pending tasks and unread agent replies

Present the output as a structured summary. When repo activity overlaps
with calendar/Slack context, call it out explicitly.

---

## List Mode

```bash
python3 .cursor/skills/task-dispatch/scripts/dispatch_task.py \
  <repo_name> --list --repos-dir ~/Desktop/
```

---

## The Conversation Format

`BRAIN_TASKS.md` uses checkbox tasks with blockquote conversation threads:

```markdown
- [ ] Add batch evaluation support
> **Claw:** Add batch evaluation support
> *Dispatched on 2026-06-23 14:30*
> Context: running one persona at a time is slow
>
> **Agent:** Implemented batch mode in evaluate.py. Added --batch flag.
> One question: should failed evals halt the batch or continue?
>
> **Claw:** Continue with a warning. Log the failure in the report.
>
> **Agent:** Done. Failed evaluations show a warning icon.
>
```

- **Claw:** lines are from this workspace (the dispatcher)
- **Agent:** lines are from the repo agent (the worker)
- Unread = last speaker is Agent without subsequent Claw response

---

## What NOT to Do

- Don't dispatch without confirming the repo name and task with the user
- Don't modify files in other repos beyond BRAIN_TASKS.md and the
  instruction block
- Don't assume a repo exists -- the script will error if it's not found
- Don't dispatch to this repo (my-cursor-claw) -- that's circular
