# Sensitive Pattern Reference

Scan skill files for these patterns before publishing. For each match, propose
the corresponding placeholder.

## Identifiers and IDs

| Pattern | Regex hint | Placeholder |
|---------|------------|-------------|
| Email address | `[\w.+\-]+@[\w\-]+\.\w+` | `<YOUR_EMAIL>` |
| UUID / cloud tenant ID | `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` | `<YOUR_ATLASSIAN_CLOUD_ID>` |
| Google Drive folder ID | alphanumeric 28-44 chars after `/folders/` | `<YOUR_DRIVE_FOLDER_ID>` |
| Google Doc/Sheet/Slides ID | alphanumeric 44 chars after `/d/` | `<YOUR_DRIVE_FILE_ID>` |
| Slack workspace ID | `T[A-Z0-9]{8,11}` | `<YOUR_SLACK_WORKSPACE_ID>` |
| Slack channel ID | `C[A-Z0-9]{8,11}` | `<YOUR_SLACK_CHANNEL_ID>` |
| GitHub username (in queries) | hardcoded username in `--author=` or `author:` | `<YOUR_GITHUB_USERNAME>` |

## Hostnames and URLs

| Pattern | Placeholder |
|---------|-------------|
| `*.atlassian.net` | `<YOUR_ATLASSIAN_SITE>` |
| `*.enterprise.slack.com` | `<YOUR_SLACK_WORKSPACE_URL>` |
| `gitlab.cee.*` or internal GitLab | `<YOUR_INTERNAL_GITLAB>` |
| Any non-public hostname | `<YOUR_INTERNAL_HOST>` |

## Workspace-specific patterns

| Pattern | Placeholder |
|---------|-------------|
| Absolute home paths (`/Users/<name>/`) | `~/` |
| Workspace project ID (`Users-<name>-Desktop-<workspace>`) | `<YOUR_WORKSPACE_PROJECT_ID>` |
| MCP server with workspace prefix (`project-0-<workspace>-slack`) | `<YOUR_SLACK_MCP_SERVER>` |
| Agent transcript base path | `~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/` |

## People and org names

| Pattern | When to flag | Placeholder |
|---------|-------------|-------------|
| Colleague names in contact references | "contact X if..." | `[Your team contact]` |
| Personal name in metadata (`author:`) | YAML frontmatter | `<YOUR_USERNAME>` |
| Manager/stakeholder email | in config or examples | `<MANAGER_EMAIL>`, `<STAKEHOLDER_EMAIL>` |
| Colleague full names in scoring/detection tables | importance scoring, people detection logic | `<COLLEAGUE_NAME_1>`, `<COLLEAGUE_NAME_2>`, etc. |
| Hardcoded person-to-tag mappings | `#zack`, `#andy` style people tags | `#<colleague-tag>` |
| Manager name in auto-boost logic | "involves manager (Name)" | `involves manager (<YOUR_MANAGER_NAME>)` |

## Credentials and tokens

| Pattern | Placeholder |
|---------|-------------|
| API key / token (long alphanumeric in auth context) | `<YOUR_API_TOKEN>` |
| Bearer token (`Bearer eyJ...`) | `<YOUR_BEARER_TOKEN>` |
| GitHub PAT (`ghp_...`) | `<YOUR_GITHUB_TOKEN>` |
| Slack XOXC token (`xoxc-...`) | `<YOUR_SLACK_XOXC_TOKEN>` |
| Slack XOXD token (`xoxd-...`) | `<YOUR_SLACK_XOXD_TOKEN>` |

## Internal project identifiers

These may or may not be sensitive. Always ask the user.

| Item | Question to ask |
|------|----------------|
| Jira project key (e.g. <YOUR_JIRA_PROJECT>) | "Is this an internal-only key, or fine to publish?" |
| Internal product codes | "Should these be kept or replaced?" |
| Slack channel names with internal references | "Are these channel names fine to publish?" |

## Google Workspace IDs

| Pattern | Regex hint | Placeholder |
|---------|------------|-------------|
| Google Slides presentation ID | alphanumeric 44 chars in `presentation/d/` URLs | `<YOUR_SLIDES_ID>` |
| Google Slides edit URL | `https://docs.google.com/presentation/d/<ID>/edit` | `https://docs.google.com/presentation/d/<YOUR_SLIDES_ID>/edit` |
| Google Forms ID | alphanumeric 44 chars in `forms/d/` URLs | `<YOUR_FORMS_ID>` |

## Multi-workspace paths

| Pattern | Regex hint | Placeholder |
|---------|------------|-------------|
| Multiple workspace transcript dirs listed together | `Users-<name>-Desktop-<project>` repeated | Replace each with `<YOUR_WORKSPACE_PROJECT_ID_N>` or consolidate to single placeholder |
| Hardcoded workspace names in prose | "my-cursor-claw, prototype-creator, ..." | `<YOUR_WORKSPACE_1>, <YOUR_WORKSPACE_2>, ...` |
| `find` commands scanning multiple dirs | `for dir in ~/.cursor/projects/Users-...` loops | Generic single-dir example with `<YOUR_WORKSPACE_PROJECT_ID>` |

## Branding assets

| Pattern | Action |
|---------|--------|
| Org-branded SVGs (e.g. `hat-watermark.svg`) | Rename to generic (e.g. `hat-watermark.svg`) and update references |
| Org logo references in HTML/CSS | Replace with placeholder comment |

## Ambiguous strings

If you encounter an alphanumeric string of 20+ characters that does not match
a known pattern but appears in a config table or URL, flag it and ask:
> "Line X contains `<value>` — is this a private ID or safe to publish?"

## Eval artifacts

| Pattern | Action |
|---------|--------|
| `eval/runs/` directories | Always skip — contain user paths, internal data, transcript excerpts |
| `eval.yaml` with absolute paths | Sanitize `/Users/<name>/` paths to `~/` or `<YOUR_WORKSPACE_PATH>` |
| `events.json` in eval runs | Contains full agent transcripts with real paths, emails, internal URLs — never publish |
| `stdout.log` / `stderr.log` in eval runs | May contain absolute paths and internal hostnames |

## Pre-push checklist

Run these scans against the staging directory AFTER sanitization, BEFORE committing.
If any match, abort and re-sanitize.

```bash
# Emails (excluding placeholder patterns)
rg '[\w.+-]+@[\w-]+\.\w+' --glob '*.md' --glob '*.yaml' | grep -v '<YOUR_'

# UUIDs
rg '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

# Absolute home paths
rg '/Users/\w+/' --glob '*.md' --glob '*.yaml'

# Workspace project IDs
rg 'Users-\w+-Desktop-' --glob '*.md'

# Slack tokens
rg 'xox[bpcd]-' --glob '*.md' --glob '*.py' | grep -v '<YOUR_\|<xox'

# Internal hostnames
rg '\.atlassian\.net|\.redhat\.com|gitlab\.cee' --glob '*.md' | grep -v '<YOUR_'

# Google Doc/Slides IDs (44-char alphanumeric after /d/)
rg '/d/[A-Za-z0-9_-]{20,}' --glob '*.md'

# Colleague names (customize this list)
rg -i 'your-manager-username|your-colleague-names' --glob '*.md'
```

## Files to always skip

- `config.md`
- `sources.md`
- `*.secrets.md`
- `eval/runs/` (run artifacts contain internal data)
- `*.log` files inside eval directories
- `events.json` files inside eval directories
- Any file the user explicitly marks as private
