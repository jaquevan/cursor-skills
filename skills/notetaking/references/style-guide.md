# Style Guide

Typography, callout, and formatting conventions for all generated notes.
This file is loaded by the notetaking skill at generation time.

---

## Red Hat Design Language

Notes use the Red Hat open-source design system. Apply these wherever the
rendering environment supports them.

### Fonts

| Role | Font | Use |
|------|------|-----|
| Headings | **Red Hat Display** | H1–H3, titles, pull quotes |
| Body | **Red Hat Text** | Paragraphs, lists, table cells |
| Code | **Red Hat Mono** | All code blocks, inline code, file paths |

All three are open source (SIL license) and available at:
[github.com/RedHatOfficial/RedHatFont](https://github.com/RedHatOfficial/RedHatFont)

For Quarto documents, add to `_quarto.yml`:
```yaml
format:
  html:
    mainfont: "Red Hat Text"
    monofont: "Red Hat Mono"
```

### Colors (PatternFly semantic mapping)

These color names map to PatternFly 6 design tokens and Red Hat brand palette:

| Semantic role | Color name | Hex | Use in notes |
|---|---|---|---|
| Primary / brand | Red Hat Red | `#ee0000` | Headlines, emphasis |
| Info / context | Blue 40 | `#1fa7f8` | Background/context callouts |
| Success / insight | Green 50 | `#3e8635` | Tips and key insights |
| Warning / caution | Orange 40 | `#f0ab00` | Gotchas, watch-out notes |
| Danger / decision | Red 60 | `#c9190b` | Decisions, critical info |
| Neutral | Black / Gray 80 | `#151515` | Body text |

In markdown notes these colors are expressed through GitHub Alert types (below),
not inline CSS.

---

## Title Block

Every note starts with Quarto YAML front matter:

```yaml
---
title: "Descriptive Title in Sentence Case"
date: YYYY-MM-DD
author: "ejaquez"
categories: [meeting | learning | standup | freeform]
tags: [relevant, keywords]
---
```

Follow with a one-line **TL;DR** in bold immediately after:

```markdown
**TL;DR:** One sentence that captures the entire note's value.
```

---

## Callout Alerts (GitHub Alerts — default for all notes)

Use GitHub Alerts. These render on GitHub.com, in VS Code markdown preview,
and degrade to a readable blockquote everywhere else.

**Do NOT use Quarto `:::` callout syntax in notes.** Reserve Quarto callouts
only for `.qmd` files being explicitly built with `quarto render`.

### Note — background context, definitions (blue)
```markdown
> [!NOTE]
> Useful background that isn't the main point but helps understanding.
```

### Tip — key insight, recommendation (green)
```markdown
> [!TIP]
> The main takeaway or a recommendation worth highlighting.
```

### Important — decision, must-know (red)
```markdown
> [!IMPORTANT]
> A firm decision made or a constraint that must be respected.
```

### Warning — gotcha, caveat, watch out (amber)
```markdown
> [!WARNING]
> Something that can go wrong or is easy to misunderstand.
```

### Caution — deprecated, risky, unstable (orange-red)
```markdown
> [!CAUTION]
> Use sparingly — for things being phased out or carrying real risk.
```

**Rule:** No more than 3 alert blocks per note. Use prose for everything else.

---

## Section Headings

- `##` for major sections (Context, Discussion, Decisions, Action Items)
- `###` for subsections
- Never skip heading levels
- Sentence case for all headings — not Title Case (Red Hat typography standard)
- Keep headings short — 4 words or fewer when possible

---

## Code snippets

Always use fenced code blocks with a language tag. Never use inline code for
multi-line content.

```markdown
```python
def example():
    return "always tag the language"
```
```

Supported tags: `python`, `javascript`, `typescript`, `bash`, `sql`,
`json`, `yaml`, `markdown`, `html`, `css`, `go`, `rust`, `java`

For shell commands: `bash`. For unknown file types: `text`.

Add one line of prose before each code block explaining what it does.

---

## Links

Format every link with a descriptive label and a brief context note on the same line:

```markdown
[GitHub Skills Docs](https://docs.anthropic.com/claude/docs/skills) — official reference for SKILL.md authoring
```

Never use bare URLs. Never use generic labels like "here" or "link".

For a reference section at the bottom of a note:

```markdown
## Links

- [Descriptive Label](https://example.com) — one-line context
- [Another Resource](https://example.com/page) — what it covers and why it matters
```

---

## Action items

Use a task list with owners and optional due dates:

```markdown
## Action items

- [ ] @owner — description of task (due: YYYY-MM-DD)
- [ ] @owner — description of task
```

If there is no owner, use `@me`.

---

## Tables

Use tables for structured comparisons, option lists, or mappings. Always include
a header row:

```markdown
| Column A     | Column B       | Notes              |
|--------------|----------------|--------------------|
| value one    | value two      | short context      |
```

---

## Table of contents

For notes over ~300 words, add a TOC after the TL;DR:

```markdown
## Contents

- [Context](#context)
- [Discussion](#discussion)
- [Decisions](#decisions)
- [Action items](#action-items)
- [Links](#links)
```

---

## Dividers

Use `---` to separate major sections. Do not use `***` or `___`.

---

## Tone and voice (Red Hat brand guidelines)

- Sentence case everywhere — not title case, not all caps
- Active voice, direct prose — no filler phrases
- Bold for emphasis — not italics, not underline
- Bullet lists for parallel items; prose for narrative
- Sentences under 25 words when possible
- Abbreviations introduced once: "pull request (PR)"

---

## What to avoid

- Quarto `:::` callout blocks in standard notes (use GitHub Alerts instead)
- Leaving template placeholders unfilled (remove the section instead)
- Nesting bullet lists more than 2 levels deep
- More than one H1 heading
- Title case headings
- Emoji in headings or body text
