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

## Credentials and tokens

| Pattern | Placeholder |
|---------|-------------|
| API key / token (long alphanumeric in auth context) | `<YOUR_API_TOKEN>` |
| Bearer token (`Bearer eyJ...`) | `<YOUR_BEARER_TOKEN>` |
| GitHub PAT (`ghp_...`) | `<YOUR_GITHUB_TOKEN>` |

## Internal project identifiers

These may or may not be sensitive. Always ask the user.

| Item | Question to ask |
|------|----------------|
| Jira project key (e.g. <YOUR_JIRA_PROJECT>) | "Is this an internal-only key, or fine to publish?" |
| Internal product codes | "Should these be kept or replaced?" |
| Slack channel names with internal references | "Are these channel names fine to publish?" |

## Branding assets

| Pattern | Action |
|---------|--------|
| Org-branded SVGs (e.g. `redhat-hat.svg`) | Rename to generic (e.g. `hat-watermark.svg`) and update references |
| Org logo references in HTML/CSS | Replace with placeholder comment |

## Ambiguous strings

If you encounter an alphanumeric string of 20+ characters that does not match
a known pattern but appears in a config table or URL, flag it and ask:
> "Line X contains `<value>` — is this a private ID or safe to publish?"

## Files to always skip

- `config.md`
- `sources.md`
- `*.secrets.md`
- `eval/runs/` (run artifacts contain internal data)
- Any file the user explicitly marks as private
