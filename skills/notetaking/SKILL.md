---
name: notetaking
description: >
  Transforms raw, unstructured notes into clean, beautifully formatted markdown
  with rich typography, color-coded callouts, code blocks, and formatted links.
  Use when the user says "take notes", "format my notes", "meeting notes",
  "standup", "note this down", "document this skill", "summarize this", or pastes
  unstructured text to organize. Also use when the user asks to push, save, or
  commit notes to GitHub.
---

# Notetaking

Converts raw input into structured, visually rich markdown following the project
design system. Works with meeting notes, learning notes, standups, freeform
captures, and skill documentation.

## Workflow

### Step 1: Detect note type

Choose from:
- **meeting** — has attendees, agenda, or action items
- **learning** — studying a concept, tool, skill, or API
- **standup** — daily update (yesterday / today / blockers)
- **skill-doc** — documenting how a Cursor skill works
- **freeform** — anything that doesn't fit above

### Step 2: Read the style guide

Before generating output, read `references/style-guide.md` for the full
typography rules, callout syntax, and link formatting conventions.

### Step 3: Select and fill the template

Load the matching template from `templates/`:

| Type | Template |
|---|---|
| meeting | `templates/meeting.md` |
| learning | `templates/learning.md` |
| standup | `templates/standup.md` |
| skill-doc | `templates/learning.md` (with skill-specific sections) |
| freeform | No template — apply style guide directly |

Fill every section from the user's raw notes. Infer missing metadata (date,
title slug) from context or today's date. Never leave template placeholders
unfilled; remove sections that are genuinely not applicable.

### Step 4: Determine output path

Save the formatted note to the user's notes repo:

```
~/Projects/notes/<section>/<YYYY-MM-DD-slug>.md
```

Section mapping:
- meeting → `meetings/`
- learning / skill-doc → `learning/`
- standup → `standups/`
- freeform → `notes/`

Create the directory if it doesn't exist.

### Step 5: Commit and push

After writing the file:

```bash
cd ~/Projects/notes
git add <file>
git commit -m "note: <title> (<type>)"
git push
```

Confirm success and show the relative file path to the user.

---

## Cross-Skill Documentation Pattern

When the user says "document how [skill-name] works" or "note this skill":

1. Read `~/.cursor/skills/<skill-name>/SKILL.md`
2. Use the `learning.md` template with these skill-specific sections:
   - **What it does** — from the description frontmatter field
   - **Trigger phrases** — exact phrases that activate it
   - **Workflow steps** — numbered list from SKILL.md body
   - **Example input → output** — one concrete pair
   - **Composes with** — other skills it works alongside
3. Save to `~/Projects/notes/learning/skill-<skill-name>-<date>.md`

This builds a personal wiki of your skill library over time.

---

## Additional Resources

- Typography rules and callout syntax → [references/style-guide.md](references/style-guide.md)
- Meeting note structure → [templates/meeting.md](templates/meeting.md)
- Learning note structure → [templates/learning.md](templates/learning.md)
- Standup structure → [templates/standup.md](templates/standup.md)
