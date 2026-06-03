---
name: inbox-processor
description: >
  Processes files dropped into ~/Desktop/Notes Inbox/ — including raw text,
  markdown, PDFs, and images (whiteboard photos, handwritten notes, screenshots).
  Extracts content and hands off to the notetaking skill for formatting.
  Use when the user says "process my inbox", "format the files in my inbox",
  or "process this file".
license: MIT
metadata:
  author: ejaquez
  version: 2.0.0
  category: productivity
  tags: [notetaking, inbox, pdf, images]
---

# Inbox Processor

Reads files from `~/Desktop/Notes Inbox/`, extracts their content, and passes
each one through the notetaking skill for HTML formatting and export.

---

## Supported input types

| Extension | How content is extracted |
|---|---|
| `.txt`, `.md` | Read as-is |
| `.pdf` | Claude reads PDF content natively |
| `.png`, `.jpg`, `.jpeg`, `.webp` | Claude reads via vision |

---

## Workflow

### 1. List the inbox

```bash
ls ~/Desktop/Notes\ Inbox/
```

Skip `README.md`. If empty, tell the user and stop.

### 2. Process each file

For each file:
1. Extract content (read text, parse PDF, or read image with vision)
2. Pass the extracted content to the `notetaking` skill workflow:
   - Assign tags, correct grammar, improve structure
   - Generate styled HTML with PatternFly components
   - Save to `~/Desktop/Notes Export/<YYYY-MM-DD>-<slug>.html`

### 3. Archive originals

Move processed files out of the inbox:

```bash
mv ~/Desktop/Notes\ Inbox/<filename> ~/Desktop/Notes\ Inbox/processed/
```

Create the `processed/` subfolder if it doesn't exist.

### 4. Report

Tell the user:
- How many files were processed
- Where each HTML file was exported
- Any files that couldn't be processed and why
