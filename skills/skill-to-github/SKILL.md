---
name: skill-to-github
description: >-
  Publishes Cursor skills to a GitHub repository after scrubbing sensitive data.
  Detects org-specific values, confirms replacements, enforces git identity, and
  strips AI attribution. Use when the user says "publish my skills", "push
  skills to github", "share a skill", "update cursor-skills repo", or wants to
  publish skills for colleagues.
disable-model-invocation: true
---

# Skill to GitHub

Safely publishes skills from `.cursor/skills/` to a shared GitHub repository
by scrubbing sensitive data, enforcing git identity per the `github` skill,
and stripping AI attribution.

Inspired by Adi Pizanti's `publish-skill-to-github` skill, extended with
deeper sensitive pattern detection, eval run exclusion, branding asset
handling, and git identity enforcement.

## Two-folder model

```
.cursor/skills/               <- private originals, real values, never touched
<target-repo>/                <- sanitized copies, git repo, what others see
```

The originals are never modified. All sanitization happens on copies in a
staging directory before committing to the target repo.

## Prerequisites

```bash
gh auth status   # must be authenticated
git --version    # must be installed
```

Read the `github` skill for git identity rules. For GitHub repos:
- Author: `<YOUR_GITHUB_USERNAME> <<YOUR_GITHUB_EMAIL>>`
- Committer: `<YOUR_GITHUB_USERNAME> <<YOUR_GITHUB_EMAIL>>`

## Workflow

### Step 1: Gather parameters

List available skills:

```bash
ls .cursor/skills/
```

Ask in a single message (skip what's already provided):

1. **Which skill(s)?** One, several, or "all"
2. **Target GitHub repo?** Default: `jaquevan/cursor-skills`
3. **Any extra values to scrub?** (optional)

### Step 2: Read skill files

For each skill, read every file in its directory.

**Hard skip — never read or publish:**
- `config.md`, `sources.md`, `*.secrets.md`
- `eval/runs/` directories (run artifacts contain internal data, user paths, transcripts)
- `events.json`, `stdout.log`, `stderr.log` inside eval directories
- Any file the user flags as private

Keep `eval.yaml` and `eval/cases/` (test definitions are shareable, but sanitize
absolute paths in `eval.yaml` — e.g. `/Users/<name>/` → `~/`).

### Step 3: Detect sensitive data

Scan every file against the patterns in
[sensitive-patterns.md](sensitive-patterns.md).

For each match, record: **file path**, **line number**, **original value**,
**suggested placeholder**.

Additionally scan for these workspace-specific patterns not in the general
reference:

| Pattern | Example | Placeholder |
|---------|---------|-------------|
| Workspace project ID | `Users-<name>-Desktop-<workspace>` | `<YOUR_WORKSPACE_PROJECT_ID>` |
| MCP server with workspace prefix | `project-0-<workspace>-slack` | `<YOUR_SLACK_MCP_SERVER>` |
| Agent transcript paths | `~/.cursor/projects/.../agent-transcripts/` | `~/.cursor/projects/<YOUR_WORKSPACE_PROJECT_ID>/agent-transcripts/` |
| Absolute home directory paths | `/Users/<name>/` | `~/` |
| Branding assets | `hat-watermark.svg` | `hat-watermark.svg` (rename file too) |
| Colleague names in scoring/detection tables | Names in importance logic or people tags | `<COLLEAGUE_NAME>` or generic description |
| Google Slides/Doc IDs in eval summaries | 44-char alphanumeric in URLs | `<YOUR_SLIDES_ID>` |
| Multi-workspace path lists | `for dir in ~/.cursor/projects/Users-...` | Single-dir example with placeholder |

Also flag:
- Inline config tables with hardcoded values (candidate for `config.example.md`)
- Ambiguous alphanumeric strings 20+ chars (ask the user)

### Step 4: Confirm sanitization plan

Present the full replacement table **before writing anything**:

```
File                  | Line | Original                        | Replacement
SKILL.md              |  27  | <YOUR_EMAIL>              | <YOUR_EMAIL>
SKILL.md              |  54  | 2b9e35e3-...-ee02432            | <YOUR_ATLASSIAN_CLOUD_ID>
SKILL.md              |  98  | <YOUR_SLACK_MCP_SERVER>  | <YOUR_SLACK_MCP_SERVER>
```

Also list:
- Files that will be **skipped** (config.md, eval/runs/, etc.)
- Branding assets that will be **renamed**
- Config tables that will be **extracted** to `config.example.md`

Ask: "Should internal project keys (e.g. <YOUR_JIRA_PROJECT>) be replaced or kept?"

**Do not write any files until the user confirms.**

### Step 5: Prepare sanitized files

Work in `/tmp/skill-publish/<skill-name>/`.

1. **Copy files** — rsync the skill directory, excluding `eval/runs/`:
   ```bash
   rsync -av --exclude='eval/runs/' <skill-dir>/ /tmp/skill-publish/<skill-name>/
   ```

2. **Apply replacements** — substitute every confirmed value.

3. **Rename branding assets** — if files like `hat-watermark.svg` exist, rename
   them and update all references.

4. **Extract config** — if inline config tables exist:
   - Create `config.example.md` with placeholder values
   - Add setup note to SKILL.md: `> **Setup:** Copy config.example.md to
     config.md and fill in your values.`
   - Remove inline hardcoded values

5. **Verify sanitization** — run the pre-push checklist from
   [sensitive-patterns.md](sensitive-patterns.md) against the staging directory.
   If ANY pattern matches, fix the leak before proceeding. This is a hard gate.

### Step 6: Set up / verify target repo

```bash
gh repo view <owner>/<repo>
```

If the repo doesn't exist, create it:
```bash
gh repo create <owner>/<repo> --public --description "Cursor Agent Skills"
```

Clone or pull:
```bash
# If local clone exists
git -C <local-path> pull --ff-only

# If not, clone fresh
gh repo clone <owner>/<repo> <local-path>
```

If `pull --ff-only` fails, **stop and ask** — never force-push without
explicit instruction.

Ensure `.gitignore` includes:
```
**/config.md
**/sources.md
**/*.secrets.md
**/eval/runs/
```

### Step 7: Copy files and commit

```bash
rsync -a --delete /tmp/skill-publish/<skill-name>/ <local-path>/skills/<skill-name>/
```

Update `README.md` at repo root — add a row for each new/updated skill.

**Git identity** — follow the `github` skill:

```bash
git -C <local-path> add -A
git -C <local-path> status --porcelain
```

If nothing to commit, tell the user and stop.

Otherwise commit with correct identity:

```bash
GIT_COMMITTER_NAME="<YOUR_GITHUB_USERNAME>" GIT_COMMITTER_EMAIL="<YOUR_GITHUB_EMAIL>" \
  git -C <local-path> commit \
  --author="<YOUR_GITHUB_USERNAME> <<YOUR_GITHUB_EMAIL>>" \
  -m "Add <skill-name> skill"
```

**Strip Co-authored-by** (Cursor auto-injects this):

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 \
GIT_COMMITTER_NAME="<YOUR_GITHUB_USERNAME>" GIT_COMMITTER_EMAIL="<YOUR_GITHUB_EMAIL>" \
git -C <local-path> filter-branch -f \
  --msg-filter 'sed "/^Co-authored-by:.*/d" | sed "/^$/N;/^\n$/d"' \
  --env-filter 'export GIT_COMMITTER_NAME="<YOUR_GITHUB_USERNAME>"; export GIT_COMMITTER_EMAIL="<YOUR_GITHUB_EMAIL>"' \
  HEAD~1..HEAD
```

Verify:
```bash
git -C <local-path> log -1 --format='Author: %an <%ae> | Committer: %cn <%ce>'
git -C <local-path> log -1 --format='%B'
```

### Step 8: Push (only when told)

**Do NOT push automatically.** Only push when the user explicitly says "push".

```bash
git -C <local-path> push origin main
```

If push fails, report the error — never retry with `--force`.

Report back:
- Published URL: `https://github.com/<owner>/<repo>/tree/main/skills/<skill-name>`
- Values that were scrubbed
- Files that were skipped
- Git author/committer identity used

## Guardrails

- **Never publish** `config.md`, `sources.md`, `*.secrets.md`, or `eval/runs/`
- **Never guess** on ambiguous long strings — ask the user
- **Always confirm** the sanitization table before writing
- **Never modify** the originals in `.cursor/skills/`
- **Idempotent** — if the skill exists in the repo, update rather than duplicate
- **One skill at a time** when multiple requested — confirm each individually
- **Never push** without explicit user instruction
- **Always enforce** git identity per the `github` skill
- **Always strip** `Co-authored-by: Cursor` trailers after committing
