---
name: notetaking
description: >
  Transforms raw notes into polished, self-contained HTML files styled with
  PatternFly 6 components and Red Hat typography. Use when the user says "take
  notes", "format my notes", "format this", or pastes unstructured text.
  Also use when the user says "process my inbox" and points to a file.
  Outputs a styled HTML file to ~/Desktop/Notes Export/.
license: MIT
metadata:
  author: ejaquez
  version: 2.0.0
  category: productivity
  tags: [notetaking, html, patternfly, red-hat]
---

# Notetaking

Takes raw input (pasted text or a file) and outputs a polished, self-contained
HTML document styled with PatternFly 6 components and Red Hat brand typography.

---

## Workflow

### 1. Accept input

Raw notes come from one of two places:
- **Chat paste** — user pastes text directly into the conversation
- **File** — user points to a file in `~/Desktop/Notes Inbox/` or attaches one

### 2. Read and process

- Assign **tags** based on content (people, tools, projects, teams)
- Correct grammar and improve structure for readability
- Apply a consistent, professional voice
- Identify relationships to other notes via shared tags

### 3. Style as HTML

Generate a **single self-contained HTML file** using:
- PatternFly 6 CSS (loaded via CDN)
- Red Hat font family (Display, Text, Mono via Google Fonts)
- PF components mapped to note elements (see `references/component-map.md`)

The HTML must be self-contained — all styles loaded via CDN links in `<head>`,
no local file dependencies. It should look polished when opened in any browser.

### 4. Export

Save the HTML file to:

```
~/Desktop/Notes Export/<YYYY-MM-DD>-<slug>.html
```

If the input was a file (PDF, image, text), move the original to:

```
~/Desktop/Notes Export/originals/<original-filename>
```

Include a "View original" link at the bottom of the HTML output pointing to
`./originals/<filename>`.

Tell the user the file path and that they can open it in any browser.

---

## Refinement

When the user says "fix the summary", "add more detail to X", "change the
tags", or any edit request about an existing note:

1. Read the existing HTML file from `~/Desktop/Notes Export/`
2. Apply the requested edit — only change what was asked
3. Overwrite the file in place
4. Confirm what was changed

**Do not regenerate the entire note for small edits.** Only regenerate fully
if the user says "reprocess this" or "start over".

### How summaries are built

The summary (info Alert at the top) should:
- Be 1–2 sentences max
- Capture the *outcome*, not the process
- Include the most important number or decision if one exists
- Use active voice, no filler

If the user says "fix the summary" — rewrite it following these rules.

### How structure is determined

The skill decides section structure based on content density:
- **Short notes (< 500 words):** No tabs, flat sections with dividers
- **Medium notes (500–1500 words):** Accordion for subsections
- **Long notes (1500+ words):** Tabs for major sections, accordion within tabs

---

## HTML structure

Every note follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{note title}</title>
  <link rel="stylesheet" href="https://unpkg.com/@patternfly/patternfly@6/patternfly.min.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;700;900&family=Red+Hat+Text:wght@400;600&family=Red+Hat+Mono:wght@400;700&display=swap">
  <style>
    /* Inline overrides — see references/component-map.md */
  </style>
</head>
<body class="pf-v6-c-page">
  <main class="pf-v6-c-page__main">
    <section class="pf-v6-c-page__main-section">
      <!-- Note content using PF components -->
    </section>
  </main>
</body>
</html>
```

---

## Tag system

Assign tags using PF Label components. Color-code by category:

| Category | PF Label color | Example tags |
|---|---|---|
| Red Hat / brand | `red` | `rhat`, `patternfly`, `openshift` |
| People | `blue` | `zack`, `priya`, `steven-huels` |
| Tools / tech | `teal` | `jira`, `quarto`, `mcp`, `cursor` |
| Projects | `purple` | `adlc`, `aisdlc`, `vlm` |
| Status | `green` / `orange` | `decision`, `blocker`, `action-item` |

Tags render as a PF LabelGroup at the top of the note, below the title.

---

## Additional resources

- Component-to-note mapping → [references/component-map.md](references/component-map.md)
