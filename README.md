# cursor-skills

Personal Cursor Agent skills for internship workflows, notetaking, and knowledge management.

## What's Here

| Skill | Description |
|---|---|
| [`notetaking`](skills/notetaking/) | Converts raw notes into structured, beautifully formatted markdown with Quarto callouts, code blocks, and git push |
| [`tag-scanner`](skills/tag-scanner/) | Scans frontmatter tags across all notes, builds a tag index, and injects Related Notes sections |
| [`internship-progress`](skills/internship-progress/) | Aggregates meetings, skills, standups, and open action items into a rolling internship progress log |
| [`inbox-processor`](skills/inbox-processor/) | Processes files from ~/Desktop/Notes Inbox/ — raw text, PDFs, and images — into formatted notes |

## Installing a Skill

1. Clone this repo or download a skill folder as a ZIP
2. Copy the skill folder into `~/.cursor/skills/`:

```bash
cp -r skills/notetaking ~/.cursor/skills/notetaking
```

3. The skill is available immediately in any Cursor chat — no restart needed.

## Using the Notetaking Skill

Paste raw notes into any Cursor chat and say one of:

- "take notes on this"
- "format my meeting notes"
- "standup"
- "document how [skill-name] works"

The skill detects the note type, applies the matching template and style guide, saves the formatted file to `~/Projects/notes/`, and commits + pushes to GitHub.

### Note Types

| What you say | Template used | Saved to |
|---|---|---|
| meeting / attendees / agenda | `meeting.md` | `notes/meetings/` |
| learning / studying / concept | `learning.md` | `notes/learning/` |
| standup / yesterday / today | `standup.md` | `notes/standups/` |
| document this skill | `learning.md` (skill variant) | `notes/learning/` |
| anything else | style guide only | `notes/notes/` |

## Skill Structure

```
skills/
└── notetaking/
    ├── SKILL.md              # Main skill — loaded by Cursor
    ├── templates/
    │   ├── meeting.md        # Meeting notes template
    │   ├── learning.md       # Learning / skill-doc template
    │   └── standup.md        # Daily standup template
    └── references/
        └── style-guide.md    # Typography and callout conventions
```

## Adding More Skills

Each skill lives in its own folder under `skills/`. Follow the structure above — every skill needs a `SKILL.md` with valid YAML frontmatter (`name` and `description` fields).

See [`claude-skills/overview.md`](https://github.com/anthropics/skills) for authoring guidance.
