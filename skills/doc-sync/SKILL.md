---
name: doc-sync
description: >
  Connects to Google Docs and keeps documentation in sync with the actual
  codebase. Scans Google Docs for references to code, APIs, skills, install
  instructions, and architecture, then cross-references against the repo to
  flag what has drifted. Use when the user says "doc sync", "check my docs",
  "are my docs up to date", "sync documentation", "what docs are stale",
  "check this Google Doc against the code", or pastes a Google Doc URL and
  asks if it's current. Also use when someone says "my README is probably
  outdated" or "does this doc still match the code".
argument-hint: "[Google Doc URL, Drive search query, or 'check all docs']"
---

# Doc Sync

You connect to Google Docs and cross-reference them against the actual codebase
to find documentation that has fallen behind. Documentation rots silently.
Install instructions stop working, architecture diagrams describe last month's
code, and API references point to functions that were renamed weeks ago. Your
job is to catch all of that.

The user's input is: **$ARGUMENTS**

---

## Input Detection

Determine what the user gave you:

1. **Google Doc URL** (contains `docs.google.com/document/d/<id>`). Extract the
   doc ID and go straight to Phase 1 with that single document.
2. **Drive search query** ("doc-sync prototype-creator docs" or "check the
   ADLC planning doc"). Use `drive_search` to find matching documents.
3. **Local path** ("doc-sync README" or "check docs/"). Scan local files only,
   skip Google Docs phases.
4. **"Check all docs"** or similar broad request. Search Drive for recently
   modified documents in the team's shared folders, plus scan local docs.
5. **Empty**. Ask:

> "What documentation should I check? You can:
> - **Paste a Google Doc URL** and I'll compare it against the codebase
> - **Name a topic** like 'prototype-creator docs' and I'll search Drive
> - **Say 'check local docs'** to scan README, SKILL.md, and docs/ files
>
> What are we syncing?"

Wait for the user's response before proceeding.

---

## Phase 1: Discover Documentation

### Google Docs (via Google Workspace MCP)

Use the Google Workspace MCP tools to find and read documents.

**Finding documents:**
```
Tool: drive_search
Arguments: { "query": "<search term>", "max_results": 10, "file_type": "document" }
```

**Reading document content:**
```
Tool: drive_get_content
Arguments: { "file_id": "<id>", "export_format": "text" }
```

Extract the document ID from URLs (the segment after `/d/` and before `/`).

For each Google Doc found, capture:
- Document title and URL
- Last modified date
- Full text content

### Local documentation

Scan the repository for documentation files:
- `README.md` and any `README` variants
- `docs/` directory contents
- `SKILL.md` files in `.cursor/skills/`
- `CHANGELOG.md`, `CONTRIBUTING.md`
- Any `.md` files in the project root

For each file, read its contents using the Read tool.

---

## Phase 2: Cross-Reference Against Codebase

Go through each document and check every verifiable claim against the actual
code. Look for these categories of drift:

### Critical drift (broken instructions)
- **Install commands** that reference packages, versions, or scripts that no
  longer exist
- **CLI commands** or **API calls** shown in docs that have changed signatures
- **File paths** referenced in docs that have moved or been deleted
- **Environment variables** or **config keys** that have been renamed
- **Code examples** that use outdated function names, parameters, or patterns

### Structural drift (stale architecture)
- **Architecture descriptions** that no longer match the directory structure
- **Skill descriptions** that reference capabilities the skill no longer has
  (or is missing capabilities it now has)
- **Workflow descriptions** that skip steps or describe a different flow than
  the code implements
- **Component or service lists** that are missing new additions or include
  removed ones

### Minor drift (wording and references)
- **Version numbers** that are behind the current release
- **Dependency references** to libraries that have been swapped
- **Team member names** or **role descriptions** that have changed
- **"Coming soon" or "TODO"** items that have since been shipped
- **Links** to external resources that may have moved

### How to verify

For each claim in a document:
1. Search the codebase for the referenced file, function, API, or path
2. If found, compare what the doc says vs what the code actually does
3. If not found, flag it as potentially removed or renamed
4. For install instructions, check `package.json`, `requirements.txt`, or
   equivalent for current versions

Be thorough but not paranoid. Focus on things a user following the docs
would actually trip over.

---

## Phase 3: Generate Drift Report

Present the findings conversationally, organized by severity.

**Format:**

> "I checked [N] documents against the codebase. Here's what I found:
>
> **Critical (will break someone's workflow):**
>
> 1. **[Doc name] > [Section]**: [What's wrong and what the code actually says]
> 2. ...
>
> **Stale (misleading but not broken):**
>
> 1. **[Doc name] > [Section]**: [What's drifted and what changed]
> 2. ...
>
> **Minor (cosmetic or low-impact):**
>
> 1. **[Doc name]**: [What's off]
> 2. ...
>
> [N] critical, [N] stale, [N] minor issues across [N] documents."

If a document is fully up to date, say so:
> "[Doc name] looks current. Nothing flagged."

### If nothing is stale

> "I checked [N] documents and everything looks current. Nice work keeping
> things in sync."

Don't invent drift to have something to report.

---

## Phase 4: Offer to Fix

After presenting the report, offer next steps:

**For local docs (README, SKILL.md, docs/):**
> "Want me to fix any of these? I can update the local files directly."

If the user says yes, make the edits. For each fix, explain what changed.

**For Google Docs:**
Since the Google Workspace MCP is read-only for document editing, provide
the specific text that needs to change:

> "I can't edit Google Docs directly, but here are the exact changes needed:
>
> **[Doc name]:**
> - Section '[X]': Change '[old text]' to '[new text]'
> - Section '[Y]': Remove the paragraph about [Z], it's no longer accurate
> - Section '[W]': Add a note about [new feature]"

This gives the user copy-pasteable corrections they can apply manually.

---

## Focus Areas

If the user specifies a focus, narrow the scan:

- "doc-sync just the API docs" > only check API-related sections
- "doc-sync SKILL.md files" > only check skill descriptions
- "doc-sync install instructions" > only verify setup/install sections
- "doc-sync prototype-creator" > only check docs related to that project

Still read all docs for context, but only report drift in the focused area.

---

## What NOT to Do

- Don't rewrite entire documents. Flag what's wrong and offer targeted fixes.
- Don't generate HTML reports or create files. This is conversational.
- Don't flag subjective writing quality issues. This is about factual accuracy,
  not prose style.
- Don't guess about drift. If you can't verify a claim against the codebase,
  say "I couldn't verify this" rather than flagging it as wrong.
- Don't skip the research. Actually check the code. "This might be outdated"
  without checking is useless.
- Don't overwhelm with minor issues. If there are 2 critical problems and
  15 minor typos, lead with the critical ones and summarize the minor ones.

---

## Related Skills

- `/notetaking` or `/notetaking-project`: If the drift report itself needs
  to be formatted as a shareable HTML document
- `/second-brain-ingest`: If the user wants to file the drift findings into
  the wiki for tracking over time
- `/source-reader`: The building-block skill this uses for Google Doc
  extraction patterns
