---
name: gdoc-writer
description: >
  Creates, edits, formats, and collaborates on Google Docs with consistent
  typography. Use when the user says "create a google doc", "write a doc",
  "make a new doc", "clean up this doc", "format this google doc", "edit my
  doc", "fix the styling", "make it look consistent", "update my internship
  progress", "update progress document", "add to my progress doc", "push
  this to a doc", "share this draft", "check for comments", "any comments
  on the doc", "reply to comments", pastes a Google Doc URL and wants
  changes, or describes content that should become a styled Google Doc.
  Also use when someone says "bold the important parts", "fix the headings",
  "apply Red Hat styling", or "which tabs does this doc have". This skill
  handles creation, editing, multi-tab navigation, typography presets, and
  collaborative commenting workflows. The internship progress document is
  at ID <YOUR_DOC_ID> and uses the
  redhat-formal preset.
argument-hint: "[description of what to create, a Google Doc URL to edit, or 'format' + a doc reference]"
---

# Google Doc Writer

You create, edit, and format Google Docs with consistent, professional
typography. You use a Python script (`scripts/gdoc_writer.py` relative to
this skill) that calls the Google Docs API directly for full control over
text insertion, formatting, tab navigation, and style application.

The user's input is: **$ARGUMENTS**

---

## Input Detection

Determine what the user wants:

1. **Create mode**: User describes content that should become a new Google Doc.
   Phrases: "create a doc about...", "write up a doc for...", "make a new doc",
   "turn this into a google doc", "doc this up".

2. **Edit mode**: User pastes a Google Doc URL or names a specific doc they
   want changed. Phrases: "edit my doc", "add this to the doc", "update the
   doc with...", or a raw URL like `https://docs.google.com/document/d/...`.

3. **Format/Clean mode**: User wants an existing doc cleaned up without
   changing content. Phrases: "format this doc", "clean up the styling",
   "make it look consistent", "fix the headings", "bold the important stuff",
   "apply Red Hat styling".

4. **Ambiguous**: Ask one clarifying question:
   > "Are you looking to create a new doc, edit an existing one, or just
   > clean up the formatting on something you already have?"

---

## Style Presets

Before creating or formatting, determine which preset to use. If the user
doesn't specify, select based on context:

| Preset | When to use | Headings | Body |
|--------|-------------|----------|------|
| `redhat-formal` | Reports, progress docs, official deliverables | Red Hat Display 18/14/12pt bold | Red Hat Text 11pt |
| `integration-proposal` | Integration plans, project proposals, tiger team docs, stakeholder deliverables | Red Hat Display 20/16/13pt bold | Red Hat Text 11pt |
| `casual-notes` | Meeting notes, working docs, quick captures | Arial 16/13pt bold | Arial 11pt |
| `meeting-doc` | Agendas, action items, decision logs | Arial 14/12pt bold, tight spacing | Arial 11pt |
| `presentation-notes` | Speaker notes, outlines for slide decks | Arial 18/14pt | Arial 12pt generous spacing |

**Auto-selection rules:**
- Mentions "report", "progress", "Red Hat", "formal" -> `redhat-formal`
- Mentions "proposal", "integration plan", "tiger team", "stakeholder", "ADLC" -> `integration-proposal`
- Mentions "meeting", "agenda", "actions", "decisions" -> `meeting-doc`
- Mentions "notes", "quick", "working doc" -> `casual-notes`
- Mentions "presentation", "slides", "outline", "talk" -> `presentation-notes`
- Default if unclear: `casual-notes`

If unsure, ask:
> "Which style? Red Hat formal, integration proposal, casual notes, meeting doc,
> or presentation notes?"

---

## Create Mode

### Step 1: Gather content

From the chat context, extract:
- The document title
- Section structure (headings, subheadings)
- Body content (paragraphs, lists, tables)
- Any items that should be bolded (names, decisions, deliverables, dates)

If the user pasted raw text or described what they want, structure it into
a logical document with appropriate headings.

### Step 2: Determine preset

Use the auto-selection rules above or ask the user.

### Step 3: Create the document

Run the script:

```bash
python3 <SKILL_DIR>/scripts/gdoc_writer.py create \
  --title "<document title>" \
  --preset <preset_name> \
  --content-file <temp_file_with_structured_content>
```

The content file is a simple markdown file you write to `/tmp/gdoc_content.md`
with the document structure. The script handles conversion to Docs API calls.

Alternatively, call the script's Python functions directly if running inline:

```python
import sys
sys.path.insert(0, "<SKILL_DIR>/scripts")
from gdoc_writer import create_doc, PRESETS

url = create_doc(
    title="My Document Title",
    content_md=content_string,
    preset="redhat-formal"
)
```

### Step 4: Report

Tell the user the doc was created and provide the URL. Mention which preset
was applied.

---

## Edit Mode

### Step 1: Identify the document

- If the user pasted a URL, extract the doc ID (segment after `/d/` and before `/`).
- If the user named a doc, use the Google Workspace MCP `drive_search` tool to
  find it:
  ```
  Tool: drive_search
  Arguments: { "query": "<doc name>", "file_type": "document", "max_results": 5 }
  ```
  Present matches and let the user confirm which one.

### Step 2: Read current content

Run the script to fetch the document structure:

```python
from gdoc_writer import read_doc, list_tabs

doc_content = read_doc(doc_id)
tabs = list_tabs(doc_id)  # Returns list of {id, title}
```

If multiple tabs exist, tell the user:
> "This doc has [N] tabs: [tab names]. Which one should I work on?"

### Step 3: Apply edits

Based on what the user asked for:
- **Add content**: Insert text at the appropriate position with formatting
- **Bold items**: Find the specified text and apply bold styling
- **Fix headings**: Normalize heading levels to the chosen preset
- **Edit specific sections**: Find the section by heading text, replace content

### Step 4: Report

Summarize what was changed. If multiple edits were made, list them briefly.

---

## Format/Clean Mode

### Step 1: Read the document

Fetch the full document structure including all tabs.

### Step 2: Analyze current formatting

The script scans for:
- Inconsistent heading sizes (H1s at different font sizes)
- Body text with mixed font families
- Missing bold on label patterns ("Deliverable:", "Decision:", "Action:", "Owner:", "Date:")
- Excessive blank lines (3+ consecutive)
- Headings that should be headings but are just bold body text

### Step 3: Determine target preset

Ask the user or auto-detect from the document's existing dominant font.

### Step 4: Apply formatting

Run the format function:

```python
from gdoc_writer import format_doc

changes = format_doc(doc_id, preset="redhat-formal", tab_id=None)
# tab_id=None means format all tabs
```

The function returns a summary of changes made.

### Step 5: Report

> "Formatted [doc title]. Applied [preset] styling:
> - Normalized [N] headings to Red Hat Display
> - Bolded [N] label patterns (Deliverable:, Decision:, etc.)
> - Fixed [N] inconsistent font sizes
> - Cleaned [N] excessive blank lines"

---

## Tab Navigation

When working with multi-tab documents:

1. **List tabs**: `list_tabs(doc_id)` returns all tab IDs and titles
2. **Read a specific tab**: `read_doc(doc_id, tab_id=TAB_ID)`
3. **Edit a specific tab**: All edit/format functions accept an optional `tab_id`
4. **Default behavior**: If no tab specified, operate on the first tab (matching
   Google Docs API default)

When a user says "go to the second tab" or "edit the Notes tab", map that to
the correct tab ID before proceeding.

---

## Auto-Bold Rules

When formatting or creating, automatically bold these patterns:

**Always bold (regardless of preset):**
- Text before a colon at the start of a line: "Owner:", "Date:", "Status:"
- Proper names when they appear after "Owner:", "Lead:", "Contact:", "Author:"
- Jira ticket keys (PROJ-1234, PROJ-567)

**Preset-specific bold patterns:**
- `redhat-formal`: "Deliverable:", "Decision:", "Action:", "Key Learning:"
- `integration-proposal`: "Goal:", "Tasks:", "Success:", "Phase", "Timeline:",
  "Stakeholders:", "Background:", "Structure:", "Struggle:", "Context:",
  "Job (JTBD):", "Deliverable:", "Next steps:"
- `meeting-doc`: "Action:", "Decision:", "Blocker:", "Next Steps:"
- `casual-notes`: minimal auto-bold (only labels before colons)
- `presentation-notes`: "Key Point:", "Transition:", "Demo:"

---

## Color Conventions

When formatting documents (especially `integration-proposal` and `redhat-formal`
presets), apply color to specific text categories using the Google Docs API
`updateTextStyle` with `foregroundColor`.

### Blue link color

RGB: r=0.07, g=0.33, b=0.80

Apply to text that is ALSO a clickable hyperlink (link.url must be set).
Blue text without a hyperlink is incorrect. If it's blue, it must link somewhere.

Linkable items:
- Jira ticket keys that link to Red Hat Jira (https://redhat.atlassian.net/browse/KEY)
- Cross-tab references (link to tab via heading ID or tab URL)
- Repository URLs and GitHub/GitLab links
- Google Doc links and external resource URLs
- PR/MR references

Do NOT color text blue without also adding a hyperlink.

### Green structure color

RGB: r=0.09, g=0.50, b=0.22

Apply ONLY to code-snippet-style structure diagrams (pipeline flows, hierarchy
visualizations). Always pair with a monospace font (Roboto Mono 10pt) to make
it clearly a structural/code block.

Do NOT use green for random emphasis or labels. Green means "this is a
structure diagram or code snippet."

### When to apply color

- `integration-proposal`: Always apply both blue and green
- `redhat-formal`: Apply blue to Jira keys and links only
- `casual-notes` and `meeting-doc`: No color application
- `presentation-notes`: Apply blue to links only

---

## Integration Proposal Conventions

When using the `integration-proposal` preset, follow these structural
conventions modeled after the Outcome Creator Integration Plan (the team's
reference document for stakeholder deliverables):

### Document title format

```
[Tool Name] Integration Plan
Red Hat AI ADLC // [JIRA-KEY]
```

### Tab structure

Multi-tab documents with clear purpose separation:

| Tab | Purpose |
|-----|---------|
| Integration Plan | Phased timeline with goals, tasks, and success criteria |
| Requirements | JTBD format: Job, Context, Struggle sections |
| Team Proposal | Problem statement, benefits, proposed workstreams |
| Output Examples | Sample outputs or demos of the tool in action |
| Documentation | Living technical documentation (architecture, metrics, history) |

Not all tabs are required. Use only what fits the project scope.

### Phase structure

Each phase in an integration plan follows this pattern:

```
Phase N: [Phase Name]
Goal: [One paragraph describing the desired end state]

Tasks:
- Task item (use ⭐ prefix for key/critical tasks)
- Task item with owner in parentheses
- Task item

Success:
- Measurable outcome with target date (target: [date])
- Another measurable outcome
```

### Requirements tab (JTBD format)

```
Job (JTBD): [Who] needs to [do what], so that [outcome].

Context: [Current state description]

Struggle:
- Pain point 1
- Pain point 2
```

### Team Proposal tab

Use numbered sections:
1. The problem: [what happens without this]
2. The payoff: [benefits of doing it]
3. Proposed workstreams (with repo links where applicable)
4. Next steps

### Cross-references

Reference other tabs inline: "Read more in the [Tab Name] tab."
Reference Jira keys by full key (PROJ-1234, PROJ-567).
Link repos and external resources as plain URLs on their own line.

### Stakeholder tables

Use a simple table with columns: Name, Role, Engagement.
Bold proper names.

---

## Known Documents

These documents are referenced frequently. When the user mentions them by
name (or a shorthand), use the doc ID directly without searching Drive.

| Shorthand | Document | ID | Default Preset |
|-----------|----------|-----|----------------|
| "progress doc", "internship progress", "progress document" | Progress Document - <YOUR_NAME> | `<YOUR_DOC_ID>` | `redhat-formal` |
| "prototype evals doc", "evals working doc" | Prototype Creator Evals - Working Document | `1NqpIyh0dPTxeG1hIcdhE9el-EopI3ITxDzlajfH1RKU` | `redhat-formal` |
| "outcome creator plan", "integration plan reference" | Outcome Creator Integration Plan | `18dLDDx97X-UNNFkcbD_rEP97K0XEKvgFJUDPPv5ku8g` | `integration-proposal` |

When the user says "update my internship progress" or "update progress document":
1. Gather context from the conversation (what was done today, meetings, deliverables)
2. Use the `gdoc_writer.py` script to add a new row to the progress table
3. Apply the `redhat-formal` preset formatting after editing

---

## Gemini Transcript Processing

The skill supports processing meeting transcripts into structured content for
Google Docs. Two modes are available:

### Mode 1: Markdown Paste (recommended, no API key needed)

Generate structured markdown from a transcript using Claude/Cursor, then paste
into Google Docs with formatting preserved.

**Setup (one time):**
1. In Google Docs: Tools > Preferences > check "Enable Markdown"

**Workflow:**
1. Read the transcript file in the chat
2. Ask Claude to extract: date, attendees, summary, decisions, action items, key points
3. Format as markdown matching the Daily Progress tab structure
4. Copy the markdown output
5. In Google Docs: Edit > "Paste from Markdown"

Alternatively, use the `gdoc_writer.py` script to write directly via the API:

```bash
python3 <SKILL_DIR>/scripts/gdoc_writer.py edit --doc-id <ID> \
  --tab-name "Daily Progress" --content-file /tmp/meeting.md \
  --preset integration-proposal
```

### Mode 2: Gemini API (requires GEMINI_API_KEY)

If you have a Gemini API key, use the automated script:

```bash
python3 <SKILL_DIR>/scripts/gemini_transcript.py <transcript_file> [--output json|markdown]
```

This sends the transcript to `gemini-2.5-flash` with a structured output schema
and extracts: date, title, attendees, summary, decisions, action items, key points.

**Requirements:** `GEMINI_API_KEY` env var or `~/.config/gemini/api_key` file.
Package: `google-genai` and `pydantic`.

### Processing a transcript in this chat

When the user says "process this transcript" or "add this meeting to my working doc":

1. Read the transcript file
2. Extract structured data (date, attendees, decisions, action items, key points)
3. Format as markdown matching the Daily Progress tab conventions:

```
## [Date] [Day of Week]

Key Meetings: [title]
Attendees: [comma-separated list]

What Was Done:
* [summary points]

Decisions Made:
* [decision 1]
* [decision 2]

Action Items:
* [owner]: [task]

Open Items:
* [unresolved questions]
```

4. Write to the working doc via gdoc_writer.py or tell the user to paste from markdown

---

## Collaboration Mode ("push this to a doc", "share this draft", "check for comments")

When a draft needs input from others, push it to Google Docs for commenting
and pull feedback back. Uses `scripts/gdoc_sync.py`.

**Safety rule:** Every action that other people can see requires explicit
user approval. Never auto-push, auto-share, or auto-reply. The script
enforces this with a `--confirm` flag that you only pass after the user
says yes.

### Pushing a Draft

1. Identify the content to push (a draft in chat, a local file, a section
   of a working doc)
2. If embedded in a larger file, extract it into a standalone markdown file,
   show it to the user, and confirm
3. Dry run first:

```bash
python3 <SKILL_DIR>/scripts/gdoc_sync.py push <file> \
  --title "Title" --share email1@example.com email2@example.com
```

4. Show the preview output (title, content length, who will get access)
5. **Wait for explicit approval** before running with `--confirm`
6. After push, note the Google Doc URL

### Checking for Comments

When the user says "any comments on the doc?" or "check the doc for feedback":

```bash
python3 <SKILL_DIR>/scripts/gdoc_sync.py pull <file>
```

Present comments grouped by commenter. For each open comment, propose a
response and wait for the user to approve, edit, or skip.

### Replying to Comments

1. Draft a reply and show it to the user
2. **Wait for explicit approval**
3. Only then run:

```bash
python3 <SKILL_DIR>/scripts/gdoc_sync.py reply <file> \
  --comment-id <id> --reply-text "approved response" --confirm
```

### Updating an Existing Doc

When the user edits the local file and wants to push updates:

```bash
python3 <SKILL_DIR>/scripts/gdoc_sync.py update <file>
```

Warn that this replaces all content (existing comments may lose anchors).
**Wait for explicit approval** before running with `--confirm`.

### Checking Status

```bash
python3 <SKILL_DIR>/scripts/gdoc_sync.py status [<file>]
```

Shows all tracked docs and their comment counts.

---

## Error Handling

| Error | Response |
|-------|----------|
| Doc URL is invalid | "That doesn't look like a Google Doc URL. Can you paste the full link?" |
| Permission denied | "I don't have edit access to that doc. Make sure it's shared with your Google account." |
| Token expired | "Auth token expired. Run `python3 gdoc_writer.py --setup` to re-authenticate." |
| Doc not found via search | "I couldn't find a doc matching '[query]'. Can you paste the URL directly?" |
| Tab doesn't exist | "That tab doesn't exist. Available tabs: [list]" |

---

## What NOT to Do

- Don't read the entire document content back to the user unless they ask.
  Just confirm what was changed.
- Don't apply formatting without knowing the target preset. Always determine
  it first (auto-select or ask).
- Don't create duplicate docs. If the user says "create" but a doc with that
  exact title exists, mention it and ask if they want to edit the existing one.
- Don't modify tabs the user didn't ask about.
- Don't change content when the user only asked for formatting fixes.
- Don't use dashes in any text you write into documents (matching the
  humanize-text voice rule for Evan's documents).
