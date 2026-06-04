# cursor-skills

Development mono-repo for personal Cursor Agent skills. Each skill has its own
folder under `skills/` and can be published as a standalone repo for distribution.

## Skills

| Skill | Version | Description |
|---|---|---|
| [`notetaking`](skills/notetaking/) | 3.1.0 | Transforms raw notes into polished HTML reports with PatternFly 6 styling and Red Hat typography |
| [`tag-scanner`](skills/tag-scanner/) | 2.0.0 | Scans notes for tags, assigns PF color-coded labels, builds a cross-linked index |
| [`inbox-processor`](skills/inbox-processor/) | 2.0.0 | Processes files from ~/Desktop/Notes Inbox/ (PDFs, images, text) into formatted notes |

## Getting started

See **[SETUP.md](SETUP.md)** for full setup instructions (git config, skill
installation, notes folder structure).

## Installing a skill

```bash
# Copy a skill into Cursor
cp -r skills/notetaking ~/.cursor/skills/notetaking

# Copy into Claude Code
cp -r skills/notetaking ~/.claude/skills/notetaking
```

No restart required — skills are available immediately.

## Repo structure

```
cursor-skills/
├── README.md
├── SETUP.md
├── .gitignore
└── skills/
    ├── notetaking/
    │   ├── SKILL.md              # Main skill instructions
    │   ├── eval.yaml             # Evaluation config (agent-eval-harness)
    │   ├── eval/cases/           # Test cases
    │   ├── references/
    │   │   └── component-map.md  # HTML component reference
    │   └── assets/
    │       └── redhat-hat.svg    # Red Hat fedora logo
    ├── tag-scanner/
    │   └── SKILL.md
    └── inbox-processor/
        └── SKILL.md
```

## Publishing individual skills

Each skill can be published as its own GitHub repo for distribution:

```bash
# Create standalone repo for a skill
mkdir /tmp/cursor-skill-notetaking
cp -r skills/notetaking/* /tmp/cursor-skill-notetaking/
cd /tmp/cursor-skill-notetaking
git init && git add . && git commit -m "feat: initial release"
# Then create the repo on GitHub and push
```

## Evaluating skills

This repo uses [agent-eval-harness](https://github.com/opendatahub-io/agent-eval-harness)
for automated skill evaluation. Each skill with an `eval.yaml` can be tested:

```bash
claude --plugin-dir ~/Projects/agent-eval-harness
/eval-run --skill notetaking --model claude-opus-4-6
```

Eval run artifacts (in `eval/runs/`) are gitignored — they contain
machine-specific paths and large event logs.
