# cursor-skills

Personal Cursor Agent skills for internship workflows, notetaking, and knowledge management.

## Skills

Each skill is designed to be installed as a standalone folder. When pushing to GitHub,
**each skill gets its own repository** — this matches the Anthropic-recommended distribution
model where users can clone or download only what they need.

| Skill | Repo (when published) | Description |
|---|---|---|
| [`notetaking`](skills/notetaking/) | `cursor-skill-notetaking` | Converts raw notes into structured Quarto markdown with GitHub Alerts, Red Hat typography, and git push |
| [`tag-scanner`](skills/tag-scanner/) | `cursor-skill-tag-scanner` | Scans frontmatter tags across all notes, builds tag index, injects Related Notes |
| [`internship-progress`](skills/internship-progress/) | `cursor-skill-internship-progress` | Aggregates meetings, skills, standups, and open action items into a rolling log |
| [`inbox-processor`](skills/inbox-processor/) | `cursor-skill-inbox-processor` | Processes PDFs, images, and raw text from ~/Desktop/Notes Inbox/ into formatted notes |

This repo serves as the **mono-repo development workspace** for all skills.
Individual skill repos on GitHub are mirrors of each skill subfolder.

---

## Installing a skill

```bash
# Option 1: Clone and copy
git clone https://github.com/ejaquez/cursor-skill-notetaking
cp -r cursor-skill-notetaking/notetaking ~/.cursor/skills/notetaking

# Option 2: Clone this mono-repo and copy the skill you want
git clone https://github.com/ejaquez/cursor-skills
cp -r cursor-skills/skills/notetaking ~/.cursor/skills/notetaking
```

No restart required — the skill is available immediately in any Cursor chat.

---

## Using the notetaking skill

Paste raw notes into any Cursor chat and say one of:

- `"take notes on this"`
- `"format my meeting notes"`
- `"standup"`
- `"process my inbox"` (for files in `~/Desktop/Notes Inbox/`)
- `"document how [skill-name] works"`

### Note types and output locations

| What you paste | Template | Saved to |
|---|---|---|
| Meeting notes (attendees, agenda) | `meeting.md` | `~/Projects/notes/meetings/` |
| Learning / studying a concept | `learning.md` | `~/Projects/notes/learning/` |
| Yesterday / today / blockers | `standup.md` | `~/Projects/notes/standups/` |
| Skill documentation | `learning.md` (skill variant) | `~/Projects/notes/learning/` |
| Anything else | style guide only | `~/Projects/notes/notes/` |

---

## Design system

Notes are styled using the **Red Hat open-source design language**:

- **Fonts**: Red Hat Display (headings), Red Hat Text (body), Red Hat Mono (code)
  — [github.com/RedHatOfficial/RedHatFont](https://github.com/RedHatOfficial/RedHatFont)
- **Callouts**: GitHub Alerts (`> [!NOTE]`, `> [!TIP]`, etc.) — render on GitHub
  and VS Code without needing `quarto render`
- **Colors**: PatternFly 6 semantic palette (info blue, success green, warning amber,
  danger red)

---

## Skill structure

```
skills/
└── notetaking/
    ├── SKILL.md              # Main skill — loaded by Cursor
    ├── templates/
    │   ├── meeting.md
    │   ├── learning.md
    │   └── standup.md
    └── references/
        └── style-guide.md    # Typography, callout, and formatting rules
```

## Publishing individual skill repos

When ready to publish a skill as its own GitHub repo:

```bash
# Create a new repo for the skill
cd /tmp && mkdir cursor-skill-notetaking
cp -r ~/Projects/cursor-skills/skills/notetaking/* cursor-skill-notetaking/
cd cursor-skill-notetaking
git init && git add . && git commit -m "feat: initial release v1.0.0"
# Create the repo on GitHub, then:
git remote add origin https://github.com/ejaquez/cursor-skill-notetaking
git push -u origin main
```
