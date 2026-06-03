---
name: notetaking
description: >
  Transforms raw, unstructured notes into clean, beautifully formatted markdown
  with rich typography, color-coded callouts, code blocks, and formatted links.
  Use when the user says "take notes", "format my notes", "meeting notes",
  "standup", "note this down", "document this skill", "summarize this", or pastes
  unstructured text to organize. Also use when the user asks to push, save, or
  commit notes to GitHub.
license: MIT
metadata:
  author: ejaquez
  version: 1.1.0
  category: productivity
  tags: [notetaking, markdown, quarto, red-hat]
---

# Notetaking

Two ways to capture a note — **chat paste** (fastest) or **file/inbox** (for
documents). Both produce the same clean output.

---

## Mode 1: Quick Chat Paste (default)

The user pastes raw text directly into the chat. No file needed.

1. Read the pasted content
2. Detect note type (see Step 1 below)
3. Read `references/style-guide.md`
4. Format the note and **render it in the chat first** so the user can see it
5. Ask: *"Save this to your notes repo and push?"*
6. On confirmation — or if the user said "save it" in the original message — write the file and commit

**This mode is intentionally frictionless.** The user should be able to paste
raw text mid-conversation and get a formatted note in seconds.

---

## Mode 2: File or Inbox

The user provides a file path, or asks to process a file that was dropped into
`~/Desktop/Notes Inbox/`. Hand off to the `inbox-processor` skill.

---

## Step 1: Detect note type

| Signals | Type |
|---|---|
| Attendees, agenda, decisions, action items | **meeting** |
| "yesterday / today / blockers" | **standup** |
| Studying a concept, tool, API, or skill | **learning** |
| Documenting a Cursor skill | **skill-doc** |
| Code snippet with no other context | **snippet** |
| Anything else | **freeform** |

For **snippet** type: extract the code, add a one-line description and language
tag, and append to `~/Projects/notes/snippets/README.md`. No full template needed.

---

## Step 2: Read the style guide

Before generating output, read `references/style-guide.md`.

---

## Step 3: Select and fill the template

| Type | Template |
|---|---|
| meeting | `templates/meeting.md` |
| learning / skill-doc | `templates/learning.md` |
| standup | `templates/standup.md` |
| freeform / snippet | Style guide only, no template |

Fill every section. Infer missing metadata (date, title slug) from context
or today's date. Remove sections that are genuinely not applicable — never
leave placeholders.

---

## Step 4: Output path

```
~/Projects/notes/<section>/<YYYY-MM-DD-slug>.md
```

| Type | Folder |
|---|---|
| meeting | `meetings/` |
| learning / skill-doc | `learning/` |
| standup | `standups/` |
| freeform | `notes/` |
| project-specific | `projects/<project-name>/` |

If the note is clearly scoped to a specific project (e.g. "notes from the
cursor-skills work today"), save it under `projects/<project-name>/` instead.

---

## Step 5: Commit and push

**Prerequisite check:** Before committing, verify git is configured:

```bash
git config user.email
git config user.name
```

If either returns nothing, stop and tell the user:
> Git is not configured. Run the setup steps in `SETUP.md` before notes can be pushed.

Once confirmed, commit and push:

```bash
cd ~/Projects/notes
git add <file>
git commit -m "note: <title> (<type>)"
git push
```

Conventional commit types for notes: `note:` for new notes, `chore:` for
index/tag updates, `fix:` for corrections to existing notes.

Confirm success and show the relative file path.

---

## Cross-Skill Documentation Pattern

When the user says "document how [skill-name] works" or "note this skill":

1. Read `~/.cursor/skills/<skill-name>/SKILL.md`
2. Use `templates/learning.md` with these sections:
   - **What it does** — from the description frontmatter
   - **Trigger phrases** — exact phrases that activate it
   - **Workflow steps** — numbered list from the SKILL.md body
   - **Example input → output** — one concrete pair
   - **Composes with** — other skills it works alongside
3. Save to `~/Projects/notes/learning/skill-<skill-name>-<date>.md`

---

## Additional Resources

- Typography and callout syntax → [references/style-guide.md](references/style-guide.md)
- Meeting template → [templates/meeting.md](templates/meeting.md)
- Learning template → [templates/learning.md](templates/learning.md)
- Standup template → [templates/standup.md](templates/standup.md)
