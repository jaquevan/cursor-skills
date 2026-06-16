# Cursor Skills

A collection of reusable [Agent Skills](https://agentskills.io) for Cursor and Claude Code. These skills automate personal productivity workflows -- from note-taking and meeting prep to sprint management and daily journaling.

## Skills

### Productivity

| Skill | What it does |
|-------|-------------|
| **[work-context](skills/work-context/)** | Aggregates recent activity across Jira, GitHub, Calendar, Slack, Drive, and a local wiki into an interactive Canvas summary |
| **[meeting-prep](skills/meeting-prep/)** | Cross-source 1:1 prep -- pulls Slack DMs, calendar history, Jira tickets, and Drive docs for a specific person into a Canvas with prioritized talking points |
| **[standup-writer](skills/standup-writer/)** | Auto-drafts a standup update (yesterday/today/blockers) from Jira status changes, PRs, calendar, and Slack |
| **[session-log](skills/session-log/)** | Scans today's agent transcripts and writes a tagged daily entry into a Second Brain wiki |
| **[sprint-manager](skills/sprint-manager/)** | Manages Jira sprint transitions -- finds tickets, presents a dashboard, batch-updates sprint assignments, story points, and status |
| **[tomorrow-calendar-accepted](skills/tomorrow-calendar-accepted/)** | Shows tomorrow's accepted calendar events in a clean schedule |
| **[doc-sync](skills/doc-sync/)** | Detects documentation drift between code and docs in a project |

### Content Pipeline

| Skill | What it does |
|-------|-------------|
| **[notetaking-project](skills/notetaking-project/)** | Transforms raw notes into polished, self-contained HTML reports with PatternFly 6 styling |
| **[notes-to-slides](skills/notes-to-slides/)** | Converts notes into branded Google Slides presentations |
| **[note-to-email](skills/note-to-email/)** | Converts notes into formatted email drafts |
| **[source-reader](skills/source-reader/)** | Extracts content from Google Docs, Slides, Slack, Jira, and Drive for downstream processing |
| **[humanize-text](skills/humanize-text/)** | Rewrites AI-generated text to sound more natural and human |

### Knowledge Management

| Skill | What it does |
|-------|-------------|
| **[second-brain-ingest](skills/second-brain-ingest/)** | Ingests sources into a local wiki with cross-linking and indexing |
| **[slack-summary](skills/slack-summary/)** | Summarizes Slack conversations into a Canvas with talking points |
| **[inbox-processor](skills/inbox-processor/)** | Processes files from a desktop inbox folder |
| **[tag-scanner](skills/tag-scanner/)** | Scans notes for tags and builds a cross-linked index |

### Writing and Review

| Skill | What it does |
|-------|-------------|
| **[critique](skills/critique/)** | Provides structured feedback on writing, presentations, or documents |
| **[superpowers](skills/superpowers/)** | Enhances agent capabilities with advanced reasoning and problem-solving patterns |

### Skill Development

| Skill | What it does |
|-------|-------------|
| **[skill-creator](skills/skill-creator/)** | Scaffolds new Cursor Agent Skills following established project conventions |
| **[skill-to-github](skills/skill-to-github/)** | Publishes skills to GitHub after scrubbing sensitive data, enforcing git identity, and stripping AI attribution |
| **[skill-guide](skills/skill-guide/)** | Reference guide for skill authoring best practices |

### Utilities

| Skill | What it does |
|-------|-------------|
| **[rover-lookup](skills/rover-lookup/)** | Looks up colleagues in an internal directory |
| **[slack-login](skills/slack-login/)** | Extracts Slack tokens via browser login and configures Slack MCP |
| **[run-evals](skills/run-evals/)** | Runs skill evaluations using the agent-eval-harness |

## How Skills Compose

These skills are designed to compose with each other rather than work in isolation:

- **meeting-prep** delegates Slack thread grouping to **slack-summary** and doc extraction to **source-reader**
- **standup-writer** reuses **work-context** data gathering patterns with a narrower time window
- **session-log** delegates wiki integration to **second-brain-ingest**
- **notetaking-project** uses **source-reader** as its extraction layer for external sources
- **notes-to-slides** reads finished HTML notes from **notetaking-project**
- **skill-to-github** enforces identity rules from the **github** skill and references **sensitive-patterns.md**

## Setup

### Prerequisites

- [Cursor](https://cursor.com) or [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- MCP servers configured for the services you use (see below)

### Configuration

These skills use placeholder values that you need to replace with your own. Search for these placeholders across all SKILL.md files and replace them:

| Placeholder | What to put | Where it's used |
|-------------|------------|-----------------|
| `<YOUR_ATLASSIAN_CLOUD_ID>` | Your Atlassian cloud ID (UUID) | sprint-manager, work-context, meeting-prep, standup-writer |
| `<YOUR_EMAIL>` | Your work email | sprint-manager, work-context |
| `<YOUR_GITHUB_USERNAME>` | Your GitHub username | work-context, standup-writer |
| `<YOUR_JIRA_PROJECT>` | Your Jira project key (e.g., MYPROJ) | sprint-manager, work-context, standup-writer |
| `<YOUR_SLACK_MCP_SERVER>` | Your Slack MCP server name from Cursor settings | work-context, standup-writer, meeting-prep |
| `<YOUR_ATLASSIAN_SITE>` | Your Atlassian site URL (e.g., myorg.atlassian.net) | sprint-manager |
| `<YOUR_WORKSPACE_PROJECT_ID>` | Your Cursor workspace project ID (found in ~/.cursor/projects/) | session-log, work-context, standup-writer, meeting-prep |
| `<YOUR_WORKSPACE_PATH>` | Absolute path to your workspace | Various |

### MCP Servers

Skills that interact with external services expect these MCP servers:

| MCP Server | Used by | Purpose |
|-----------|---------|---------|
| Atlassian (`user-atlassian` or `plugin-atlassian-atlassian`) | sprint-manager, work-context, meeting-prep, standup-writer | Jira + Confluence |
| Slack | work-context, meeting-prep, standup-writer, slack-summary | Slack search and history |
| Google Workspace (`user-google-workspace`) | work-context, meeting-prep, standup-writer, tomorrow-calendar-accepted | Calendar, Drive, Gmail |

### Installing Skills

Copy individual skill directories into your workspace's `.cursor/skills/` folder:

```bash
cp -r skills/work-context /path/to/your/workspace/.cursor/skills/
```

Or symlink them:

```bash
ln -s /path/to/cursor-skills/skills/work-context /path/to/your/workspace/.cursor/skills/work-context
```

## Skill Format

Every skill follows the [Agent Skills standard](https://agentskills.io):

```
skills/<skill-name>/
├── SKILL.md          # Required -- skill definition with YAML frontmatter
├── reference.md      # Optional -- deep reference material
├── scripts/          # Optional -- automation scripts
├── references/       # Optional -- supporting docs
├── templates/        # Optional -- output templates
├── assets/           # Optional -- static files (SVGs, images)
├── eval.yaml         # Optional -- eval harness config
└── eval/             # Optional -- test cases
```

## License

MIT
