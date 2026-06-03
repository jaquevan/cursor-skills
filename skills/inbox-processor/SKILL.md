---
name: inbox-processor
description: >
  Processes files dropped into ~/Desktop/Notes Inbox/ — including raw text,
  markdown, PDFs, and images (whiteboard photos, handwritten notes, screenshots).
  Converts each file into a clean, formatted note and saves it to
  ~/Projects/notes/. Use when the user says "process my inbox",
  "format the files in my inbox", "process this file", or points to a file
  in the Notes Inbox folder.
license: MIT
metadata:
  author: ejaquez
  version: 1.0.0
  category: productivity
  tags: [notetaking, inbox, pdf, images, ocr]
---

# Inbox Processor

Reads files from `~/Desktop/Notes Inbox/`, extracts content from any format,
and hands each one to the notetaking skill for formatting and saving.

---

## Supported Input Types

| Extension | How content is extracted |
|---|---|
| `.txt`, `.md` | Read as-is |
| `.pdf` | Read using Claude's built-in PDF understanding |
| `.png`, `.jpg`, `.jpeg`, `.webp` | Read using Claude's vision capability |

---

## Workflow

### Step 1: List the inbox

```bash
ls ~/Desktop/Notes\ Inbox/
```

Skip `README.md`. If the inbox is empty, tell the user and stop.

### Step 2: Process each file

For each file:

1. **Extract content**
   - Text/markdown: read directly
   - PDF: read the file — Claude can parse PDF content natively
   - Image: read the image — Claude can extract text and structure from
     whiteboard photos, handwritten notes, and screenshots

2. **Identify note type**
   Use the same detection rules as the `notetaking` skill:
   - Attendees / action items → meeting
   - Yesterday / today / blockers → standup
   - Concept / tool / API → learning
   - Code only → snippet
   - Anything else → freeform

3. **Format the note**
   Apply the notetaking skill's full workflow:
   - Read `~/.cursor/skills/notetaking/references/style-guide.md`
   - Select the matching template from `~/.cursor/skills/notetaking/templates/`
   - Fill it with the extracted content
   - Use the source filename's date prefix if present (e.g. `2026-06-03-meeting.pdf`)
     otherwise use today's date

4. **Save the formatted note**
   Write to `~/Projects/notes/<section>/<YYYY-MM-DD-slug>.md`

5. **Archive the original**
   Move the original file to `~/Projects/notes/attachments/`:
   ```bash
   mv ~/Desktop/Notes\ Inbox/<filename> ~/Projects/notes/attachments/<filename>
   ```

### Step 3: Commit everything

After all files are processed:

```bash
cd ~/Projects/notes
git add .
git -c user.email="ejaquez@users.noreply.github.com" \
    -c user.name="ejaquez" \
    -c commit.gpgsign=false \
    commit --no-gpg-sign -m "note: process inbox (<N> files)"
git push
```

### Step 4: Report

Tell the user:
- How many files were processed
- Where each note was saved (relative path)
- Any files that couldn't be processed and why

---

## Single-File Mode

If the user points to a specific file ("process this PDF" or drags a file into
the chat), process just that one file using the same workflow above. No need
to scan the full inbox.

---

## Tips for Best Results

**Whiteboard photos:** Make sure the image is in focus and well-lit. Claude
reads the text and structure directly — no OCR library needed.

**Handwritten notes:** Works best when writing is clear. Claude will do its
best to interpret ambiguous words from context.

**PDFs:** Multi-page PDFs are read in full. If the PDF is very long (50+
pages), Claude will summarize rather than transcribe verbatim.

**Raw text dumps:** No special formatting needed. The messier the better —
that's what this skill is for.

---

## Composing with Other Skills

After processing the inbox, chain into:
- `tag-scanner` — to link new notes to related existing notes
- `internship-progress` — to update the progress log with anything new
