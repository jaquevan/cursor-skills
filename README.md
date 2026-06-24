# Cursor Skills

A collection of reusable [Agent Skills](https://agentskills.io) for Cursor and Claude Code. These skills automate personal productivity workflows -- from note-taking and meeting prep to sprint management and daily journaling.

## Skills

### Daily Workflow

| Skill | What it does |
|-------|-------------|
| **[daily-briefing](skills/daily-briefing/)** | Unified morning briefing -- pulls calendar, tasks, email, Slack, Jira, cross-repo activity, and agent replies into a single Canvas |
| **[work-context](skills/work-context/)** | Aggregates recent activity across Jira, GitHub, Calendar, Slack, Drive, and a local wiki into an interactive Canvas summary |
| **[meeting-prep](skills/meeting-prep/)** | Cross-source meeting prep with type classification -- pulls Slack DMs, calendar history, Jira tickets, Gemini notes, and Drive docs into a Canvas |
| **[standup-writer](skills/standup-writer/)** | Auto-drafts a standup update (yesterday/today/blockers) from Jira status changes, PRs, calendar, and Slack |
| **[session-log](skills/session-log/)** | Scans today's agent transcripts and writes a tagged daily entry into a Second Brain wiki with importance scoring and carry-forward tracking |
| **[sprint-manager](skills/sprint-manager/)** | Manages Jira sprint transitions -- finds tickets, presents a dashboard, batch-updates sprint assignments, story points, and status |
| **[doc-sync](skills/doc-sync/)** | Detects documentation drift between Google Docs and a codebase |

### Cross-Agent

| Skill | What it does |
|-------|-------------|
| **[task-dispatch](skills/task-dispatch/)** | Sends tasks to other repos, checks agent replies, and scans repo activity (git commits, agent sessions) via `BRAIN_TASKS.md` files |

### Content Pipeline

| Skill | What it does |
|-------|-------------|
| **[notetaking-project](skills/notetaking-project/)** | Transforms raw notes into polished, self-contained HTML reports with PatternFly 6 styling |
| **[notes-to-slides](skills/notes-to-slides/)** | Converts notes into branded Google Slides presentations |
| **[gdoc-writer](skills/gdoc-writer/)** | Creates, edits, formats, and collaborates on Google Docs -- includes push/pull/reply workflow for document commenting |
| **[humanize-text](skills/humanize-text/)** | Rewrites AI-generated text to sound natural and human |
| **[source-reader](skills/source-reader/)** | Extracts content from Google Docs, Slides, Slack, Jira, and Drive for downstream processing |

### Knowledge Management

| Skill | What it does |
|-------|-------------|
| **[second-brain-ingest](skills/second-brain-ingest/)** | Ingests sources into a local wiki with cross-linking and indexing |
| **[slack-summary](skills/slack-summary/)** | Summarizes Slack conversations into a Canvas with talking points |

### Writing and Review

| Skill | What it does |
|-------|-------------|
| **[critique](skills/critique/)** | Stress-tests raw ideas and proposals with real research before you commit to them |
| **[skill-review](skills/skill-review/)** | Reviews a SKILL.md against 10 structural conventions -- separation, examples, templates, anti-patterns, length |

### Finance

| Skill | What it does |
|-------|-------------|
| **[budget-tracker](skills/budget-tracker/)** | Manages a personal budget via a Google Sheets tracker -- log spending, record income, view dashboard, process bank statements |

### Infrastructure and Meta

| Skill | What it does |
|-------|-------------|
| **[skill-creator](skills/skill-creator/)** | Interactive guide for creating new skills following workspace conventions |
| **[skill-guide](skills/skill-guide/)** | Routes user intent to the right skill -- reads available skills and suggests the best match |
| **[skill-to-github](skills/skill-to-github/)** | Publishes skills to a shared GitHub repo after scrubbing sensitive data and enforcing git identity |
| **[loop-architect](skills/loop-architect/)** | Designs and builds agent loops, goals, skills, and automations in Cursor |
| **[run-evals](skills/run-evals/)** | Runs structured skill evaluations with and without the skill enabled |
| **[slack-login](skills/slack-login/)** | Extracts Slack tokens and configures the Slack MCP server |
| **[rover-lookup](skills/rover-lookup/)** | Looks up employee info using the Dataverse MCP |

### Jira Integrations

| Skill | What it does |
|-------|-------------|
| **[sprint-manager](skills/sprint-manager/)** | Manages sprint transitions via the Atlassian MCP |

## Setup

See [SETUP.md](SETUP.md) for installation and MCP configuration instructions.

## Structure

```
skills/
├── skill-name/
│   ├── SKILL.md          # Main instructions (required)
│   ├── references/        # Optional reference docs
│   ├── scripts/           # Optional utility scripts
│   └── eval/             # Optional eval cases
```

Sensitive values in skill files use placeholder format: `<YOUR_ATLASSIAN_CLOUD_ID>`, `<YOUR_SLACK_MCP_SERVER>`, etc. See each skill's SKILL.md for setup notes.
