# Doc Sync — Local Documentation Drift Report

**Scan date:** 2026-06-16  
**Scope:** Local documentation only (README.md files, SKILL.md files, docs/ directory)  
**Documents checked:** 37 (11 READMEs, 21 SKILL.md files in `.cursor/skills/`, 2 docs files, 2 root-level .md, 1 `resources/skills/README.md`)

---

## Critical (will break someone's workflow)

### 1. resources/README.md > Structure diagram

The directory tree shows `jira/` containing a `GETDO-1/` subdirectory:

```
├── jira/                          # Mirror of Jira onboarding initiative (GETDO-1)
│   └── GETDO-1/                   # Initiative → Epics → Tasks as markdown
```

**Actual structure:** The `jira/` directory contains `INITIATIVE - Intern Onboarding/` (with descriptive epic subdirectories like `EPIC - Set up development tools and learn Agile-Scrum practices/`). There is no `GETDO-1/` directory. Someone following the docs to navigate the mirror would look in the wrong place.

### 2. resources/README.md > "Claude Code Plugin" section

The README describes this as a **Claude Code plugin** with installation via `~/.claude/settings.json` using `extraKnownMarketplaces` and `enabledPlugins`. However:

- The `.claude-plugin/` directory lives at `resources/.claude-plugin/`, not at the repo root
- The README's installation block references `"repo": "RH-Interns/resources"` which assumes a standalone repo structure. This workspace is `my-cursor-claw`, which bundles `resources/` as a subdirectory. Anyone cloning `my-cursor-claw` and following these instructions would get errors — the plugin config points to a GitHub repo path that doesn't match the local structure.
- The skill invocation syntax `/rh-interns:clone-onboarding` is Claude Code plugin syntax (not Cursor). These skills are in `resources/skills/` and would be invoked as Claude Code slash commands only when the plugin is installed from the separate `RH-Interns/resources` repo. In Cursor, these skills aren't auto-discovered (Cursor reads `.cursor/skills/`).

### 3. resources/skills/README.md > Image reference

The Setup section references an image:

```
![GCP Console project picker](../img/gcpproject.png)
```

**This file does not exist.** No `img/` directory or `gcpproject.png` was found anywhere in the workspace. The image link is broken.

---

## Stale (misleading but not broken)

### 4. resources/README.md > Available Skills table

The table lists 4 skills: `jira-sync`, `clone-onboarding`, `onboarding-status`, `activity-report`. But `resources/skills/` actually contains **7 skills**:

| Skill | Listed in README? |
|-------|:---:|
| jira-sync | Yes |
| clone-onboarding | Yes |
| onboarding-status | Yes |
| activity-report | Yes |
| **intern-report** | No |
| **archive-issues** | No |
| **rhai-biweekly-report** | No |

The `resources/skills/README.md` correctly lists `intern-report` and mentions `archive-issues` in examples, but the parent README table is out of date.

### 5. resources/README.md > Structure tree

The structure tree shows only 4 skill directories under `skills/`:

```
└── skills/
    ├── jira-sync/
    ├── clone-onboarding/
    ├── onboarding-status/
    └── activity-report/
```

Missing: `intern-report/`, `archive-issues/`, and `rhai-biweekly-report/`.

### 6. resources/README.md > Structure tree — scripts section

The tree only lists two scripts:

```
├── scripts/
│   ├── fetch-jira.py
│   └── clone_getdo_onboarding.py
```

**Actual scripts directory contains 4 files:**
- `fetch-jira.py` (listed)
- `clone_getdo_onboarding.py` (listed)
- `check_jira_groups.py` (missing from tree)
- `archive_getdo_issues.py` (missing from tree)

### 7. slack-login SKILL.md > Script path

The skill says:

> ```bash
> python3 scripts/slack-login.py --workspace <URL> --json --output ~/.slack_tokens.env --timeout 300
> ```
> The script path is relative to this skill's directory.

The actual script exists at `.cursor/skills/slack-login/scripts/slack-login.py`. The instruction to use a relative path `scripts/slack-login.py` is correct **if the working directory is set to the skill's directory**, but the instruction doesn't explicitly say to `cd` there first. The wording "relative to this skill's directory" is slightly ambiguous — it works for Claude (which resolves paths relative to SKILL.md) but could confuse a human running it manually.

### 8. notetaking-project SKILL.md > Source-reader reference path

The notetaking skill says:

> check if the user's prompt contains a reference to an external source. If it does, extract the content first using the instructions in the `source-reader` skill at `.cursor/skills/source-reader/SKILL.md`.

This path is valid and the file exists. **However**, the `source-reader` skill has `disable-model-invocation: true` in its frontmatter, meaning it's marked as a helper that cannot be invoked directly by the model. The notetaking skill's instructions to "use the instructions in the source-reader skill" are consistent with this design (it reads the instructions, doesn't invoke it). No drift here — just noting the pattern is correct.

---

## Minor (cosmetic or low-impact)

### 9. resources/skills/README.md > "Google Workspace" section

References `@googleworkspace/cli` (`gws`) for Google Workspace integration. The `gws` tool is a legitimate package, but the install command shown (`npm install -g @googleworkspace/cli`) may need verification — this is an uncommon package and its availability/naming could have changed since the docs were written. I couldn't verify the current npm registry status, so flagging as "couldn't verify" rather than confirmed drift.

### 10. prototype-evals-doc.md > standalone file in project root

This file references external repos (`andybraren/prototype-creator`) and Jira tickets (`<YOUR_JIRA_PROJECT>-2658`, `<YOUR_JIRA_PROJECT>-2499`, `<YOUR_JIRA_PROJECT>-2375`). It's a working document, not documentation per se, but it lives in the project root without any README or index linking to it. Not drift — just an orphaned doc that isn't referenced anywhere.

### 11. .cursor/skills/ — Multiple skills have `disable-model-invocation: true`

The following skills are marked as non-invocable helpers:
- source-reader
- slack-summary
- standup-writer
- notes-to-slides
- work-context
- session-log
- meeting-prep
- skill-to-github
- skill-creator
- rover-lookup
- tomorrow-calendar-accepted
- run-evals
- note-to-email

This is a design pattern (helper skills composed by other skills), not drift. The descriptions in each skill accurately reflect what they do. No factual errors found in their descriptions.

---

## Documents that look current (no drift found)

| Document | Status |
|----------|--------|
| `.cursor/skills/sprint-manager/SKILL.md` | Accurate — references `reference.md` which exists, MCP tools match |
| `.cursor/skills/critique/SKILL.md` | Accurate — standalone skill, no external file references |
| `.cursor/skills/humanize-text/SKILL.md` | Accurate — standalone conversational skill, no file refs |
| `.cursor/skills/superpowers/SKILL.md` | Accurate — standalone brainstorming skill |
| `.cursor/skills/second-brain-ingest/SKILL.md` | Accurate — references `~/second-brain/` paths (user directory) |
| `.cursor/skills/notetaking-project/SKILL.md` | Accurate — `assets/hat-watermark.svg` exists, `references/component-map.md` exists |
| `.cursor/skills/doc-sync/SKILL.md` | Accurate — references Google Workspace MCP patterns correctly |
| `resources/skills/jira-sync/README.md` | Accurate — script paths, env vars, and workflow all verified |
| `resources/scripts/README.md` | Accurate — describes `fetch-jira.py` and `clone_getdo_onboarding.py` correctly |
| `resources/docs/competencies.md` | Content doc, not code-referencing — N/A |
| `resources/docs/cloning-onboarding.md` | Operational guide — references correct scripts |

---

## Summary

**3 critical, 5 stale, 3 minor issues across 37 documents.**

The main problems are in `resources/README.md` which has fallen behind the actual repo structure:
- The jira mirror directory naming is wrong (`GETDO-1/` vs actual `INITIATIVE - Intern Onboarding/`)
- The skills table and directory tree are missing 3 skills and 2 scripts
- A referenced image file (`gcpproject.png`) doesn't exist
- The plugin installation instructions assume a standalone repo context that doesn't match this workspace

The `.cursor/skills/` directory is well-maintained — all 21 skill descriptions accurately reflect their actual capabilities, and internal file references (assets, references, scripts) resolve correctly.

---

Want me to fix any of these? I can update the local files directly.
