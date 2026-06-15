---
name: second-brain-ingest
description: >-
  Ingests a source into the second-brain wiki. Accepts raw text, a file path,
  a URL, a Google Doc, or Slack context. Also processes files from the Desktop
  Notes Inbox folder. Reads the source, creates a wiki page, cross-links it
  with existing pages, and updates the index and log. Use when the user says
  "ingest this", "add this to my wiki", "save this to second brain", "wiki
  this", "process my inbox", "check my inbox", or drops content and wants it
  filed.
---

# Second Brain Ingest

Quickly adds a new source to ~/second-brain/ and turns it into a cross-linked
wiki page. This is the fast path -- one prompt, full integration.

## Step 0: Check the Desktop Inbox

If the user says "process my inbox", "check my inbox", or "ingest my inbox"
(in the context of the second brain, NOT the notetaking inbox):

1. List all files in `~/Desktop/Second Brain Inbox/`
2. Process each file through Steps 1-7 below
3. After successful ingestion, move the original file to
   `~/second-brain/sources/` (so the inbox stays clean)
4. If the inbox is empty, tell the user

This is separate from `~/Desktop/Notes Inbox/` (which feeds the notetaking
skill and produces HTML). The Second Brain Inbox feeds the wiki only.

## Step 1: Detect the input

| Input type | How to handle |
|---|---|
| Desktop Inbox file | Read from `~/Desktop/Second Brain Inbox/`, move to sources after |
| Raw pasted text | Save to `~/second-brain/sources/YYYY-MM-DD-slug.md` |
| File path (local) | Read the file directly |
| Google Doc URL | Extract via `gws docs documents get` (see source-reader skill) |
| Slack reference | Extract via Slack MCP `search_messages` |
| URL (web) | Fetch and extract text content |
| Notes Export HTML | Read the HTML, extract text content |

## Step 2: Read existing wiki pages

Scan `~/second-brain/wiki/` for all .md files (excluding index.md and log.md).
Read each file's first 10 lines to get titles and topic summaries for
cross-linking decisions.

## Step 3: Create the wiki page

Write a new file at `~/second-brain/wiki/<slug>.md` following these rules:

- Start with `# Title` matching the filename
- Summarize key points in bullet-friendly format
- Add cross-links to any related existing wiki pages using `[Title](file.md)`
- Include a "Related" section at the bottom with links
- Include a "Sources" section listing the raw source file

## Step 4: Update existing pages

For each related wiki page, add a link back to the new page in its "Related"
section (if not already present).

## Step 5: Update index.md

Add the new page under the appropriate category in `~/second-brain/wiki/index.md`.
Create a new category if none of the existing ones fit.

## Step 6: Update log.md

Append an entry to `~/second-brain/wiki/log.md`:

```
## YYYY-MM-DD — Ingested: <source name>
- Created: <new-page>.md — <one-line summary>
- Cross-linked with: <list of updated pages>
- Category: <category in index>
```

## Step 7: Relate to internship context

Before confirming, actively connect the new content to the user's internship
work. Check the new page's content against these key projects and link where
relevant:

- **prototype-creator** — prototype generation, evaluator super agent, UX rubric
- **decision-kit** — Decision Driven Development, /strategize, /decide
- **agent-eval-harness** — skill quality, eval.yaml, judges, scoring
- **ai-sdlc-pipeline** — rfe-creator → prototype-creator → strat-creator
- **my-cursor-claw** — skills, MCP connections, notetaking, notes-to-slides
- **nielsens-heuristics** — usability evaluation, AI model comparison
- **evaluator-super-agent** — the active assignment combining all of the above

Even if the source material is tangentially related (e.g., an article about
usability testing, a meeting about PatternFly, a Slack thread about local
models), find the connection and add it as a cross-link. The value of the wiki
is in the connections.

## Step 8: Confirm

Tell the user what was created, what was cross-linked to their internship work,
and suggest related pages they might want to read.
