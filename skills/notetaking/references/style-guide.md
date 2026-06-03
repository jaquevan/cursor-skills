# Style Guide

Typography, callout, and formatting conventions for all generated notes.
This file is loaded by the notetaking skill at generation time.

---

## Title Block

Every note starts with a Quarto YAML front matter block:

```yaml
---
title: "Descriptive Title in Title Case"
date: YYYY-MM-DD
author: "<your name>"
categories: [meeting | learning | standup | freeform]
tags: [relevant, keywords]
---
```

Follow with a one-line **TL;DR** in bold immediately under the title block:

```markdown
**TL;DR:** One sentence that captures the entire note's value.
```

---

## Section Headings

- `##` for major sections (Context, Discussion, Decisions, Action Items)
- `###` for subsections
- Never skip heading levels
- Keep headings short — 4 words or fewer when possible

---

## Callout Blocks (Quarto)

Use these for color-coded semantic emphasis. Pick the right type for the content.

### Tip — Key insight, recommendation (green)
```markdown
::: {.callout-tip title="Key Insight"}
The main takeaway or a recommendation worth highlighting.
:::
```

### Note — Background context, definitions (blue)
```markdown
::: {.callout-note title="Context"}
Useful background that isn't the main point but helps understanding.
:::
```

### Warning — Gotcha, caveat, watch out (amber)
```markdown
::: {.callout-warning title="Watch Out"}
Something that can go wrong or is easy to misunderstand.
:::
```

### Important — Decision, must-know (orange/red)
```markdown
::: {.callout-important title="Decision"}
A firm decision made or a constraint that must be respected.
:::
```

### Caution — Deprecated, risky, unstable (yellow)
```markdown
::: {.callout-caution title="Deprecated"}
Use sparingly — for things being phased out or carrying real risk.
:::
```

**Rule:** No more than 3 callout blocks per note. Use prose for everything else.

---

## Code Snippets

Always use fenced code blocks with a language tag. Never use inline code for
multi-line content.

```markdown
```python
def example():
    return "always tag the language"
```
```

Supported language tags: `python`, `javascript`, `typescript`, `bash`, `sql`,
`json`, `yaml`, `markdown`, `html`, `css`, `go`, `rust`, `java`

For shell commands, use `bash`. For file contents of unknown type, use `text`.

Add a single line of plain prose before each code block explaining what it does:

```markdown
This function fetches paginated results from the API:

```python
def fetch_all(endpoint):
    ...
```
```

---

## Links

Format every link with a descriptive label and a brief context note on the same line:

```markdown
[GitHub Skills Docs](https://docs.anthropic.com/claude/docs/skills) — official reference for SKILL.md authoring
```

Never use bare URLs. Never use generic labels like "here" or "link".

For a list of references at the bottom of a note, use a `## Links` section:

```markdown
## Links

- [Descriptive Label](https://example.com) — one-line context
- [Another Resource](https://example.com/page) — what it covers and why it matters
```

---

## Action Items

Use a task list with owners and (optionally) due dates:

```markdown
## Action Items

- [ ] @owner — description of task (due: YYYY-MM-DD)
- [ ] @owner — description of task
```

If there is no owner, use `@me`.

---

## Tables

Use tables for structured comparisons, option lists, or mappings. Always include
a header row. Align columns with spaces for readability in source:

```markdown
| Column A     | Column B       | Notes              |
|--------------|----------------|--------------------|
| value one    | value two      | short context      |
```

---

## Table of Contents

For notes over ~300 words, add a TOC after the TL;DR:

```markdown
## Contents

- [Context](#context)
- [Discussion](#discussion)
- [Decisions](#decisions)
- [Action Items](#action-items)
- [Links](#links)
```

---

## Dividers

Use `---` to separate major sections. Do not use `***` or `___`.

---

## Tone and Voice

- Write in clear, direct prose — no filler phrases ("it is important to note that")
- Use active voice
- Bullet lists for parallel items; prose for narrative
- Abbreviations are fine if introduced once: "pull request (PR)"
- Keep sentences under 25 words when possible

---

## What to Avoid

- Leaving template placeholders unfilled (remove the section instead)
- Nesting bullet lists more than 2 levels deep
- Using callouts for non-semantic decoration
- Adding more than one H1 heading (the title block is the H1)
- Emoji in headings or body text (only acceptable in action item owners if already used in the raw notes)
