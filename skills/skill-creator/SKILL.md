---
name: skill-creator
description: >-
  Scaffolds new Cursor Agent Skills following the project's SKILL.md conventions.
  Use when the user says "create a skill", "new skill", "scaffold a skill",
  "make a skill for", or asks to build a reusable workflow as a skill.
disable-model-invocation: true
---

# Skill Creator

Guides the creation of new skills in this workspace following the established
patterns from existing skills (work-context, meeting-prep, notetaking-project,
sprint-manager, etc.).

## Phase 1: Discovery

Gather from the user (skip what's already provided):

1. **What does the skill do?** One-sentence purpose.
2. **Trigger phrases** — what the user would say to invoke it.
3. **Data sources** — which MCP servers, local files, or CLI tools does it need?
4. **Output format** — Canvas, chat text, HTML file, wiki page, or file creation?
5. **Does it compose with existing skills?** Check if any of these can be reused:
   - `source-reader` for external content extraction
   - `slack-summary` for Slack thread grouping and talking points
   - `work-context` for multi-source data gathering patterns
   - `second-brain-ingest` for wiki page creation
   - `tomorrow-calendar-accepted` for calendar event filtering

Use the AskQuestion tool for structured gathering when available.

## Phase 2: Write the SKILL.md

### Location

All project skills go in `.cursor/skills/<skill-name>/SKILL.md`.

### Frontmatter

```yaml
---
name: skill-name
description: >-
  What it does + trigger phrases. Include explicit user phrases like
  "summarize slack", "sprint planning", etc. for routing accuracy.
disable-model-invocation: true
---
```

- `name`: kebab-case, matches directory name, max 64 chars
- `description`: max 1024 chars, third-person, includes WHAT and WHEN
- `disable-model-invocation: true`: default on — skill only loads when named

### Body structure

Follow the pattern used across this workspace:

1. **H1 title** matching the skill's purpose
2. **One-paragraph purpose** — what it does and outputs
3. **Skill Composition table** (if it reuses other skills):
   ```
   | Step | Delegates to | What it provides |
   ```
4. **Read-Only Constraint** (if it calls MCP tools) — list allowed operations
5. **Autonomy Principle** (if multi-step) — specify which steps prompt the user
6. **Prerequisites** — MCP servers, CLI tools, local files needed
7. **Workflow** — numbered steps (`### Step N: Title`)
8. **Fallback Behavior** — table of source / primary tool / fallback
9. **Common Mistakes** — table of problem / fix

### MCP server names (this workspace)

| Server | Purpose |
|--------|---------|
| `user-atlassian` | Jira + Confluence (read + Teamwork Graph) |
| `plugin-atlassian-atlassian` | Jira + Confluence (read + write + transitions) |
| `<YOUR_SLACK_MCP_SERVER>` | Slack search and history |
| `user-google-workspace` | Calendar, Drive, Gmail, Sheets |

Atlassian cloud ID: `<YOUR_ATLASSIAN_CLOUD_ID>`

### Writing rules

- Keep SKILL.md under 500 lines
- Use tables for mappings, options, and reference data
- Use code blocks for MCP tool calls and CLI commands
- Link to `reference.md` or `references/` for deep detail
- Every claim about tool behavior should reference the actual MCP tool name
- If composing with another skill, say "follow X skill Steps N-M" rather
  than copy-pasting the steps

## Phase 3: Supporting files (if needed)

| File | When to add |
|------|------------|
| `reference.md` | Deep reference material (field IDs, scales, manual fallbacks) |
| `references/` | Multiple supporting docs |
| `scripts/` | Automation scripts (Python, bash) |
| `templates/` | Output templates |
| `assets/` | Static files (SVGs, images) |
| `eval.yaml` | Eval harness config for quality testing |

Most skills are Tier 1 (SKILL.md only). Only add supporting files when the
skill genuinely needs them.

## Phase 4: Verify

- [ ] SKILL.md under 500 lines
- [ ] Description includes trigger phrases and is third-person
- [ ] Consistent terminology throughout
- [ ] MCP server names match the workspace table above
- [ ] Composing skills are referenced, not reimplemented
- [ ] Read-only constraint present if skill calls external APIs
- [ ] Common Mistakes table covers likely failure modes
