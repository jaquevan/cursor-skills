---
name: notes-to-slides
description: >-
  Converts notes into a Red Hat-branded Google Slides presentation by building
  a deck spec first, then copying the official template and populating it.
  Use when the user says "turn this into slides", "make a presentation from
  my notes", "create slides", "convert to slides", or references a note and
  asks for a slide deck.
disable-model-invocation: true
---

# Notes to Slides

Converts notes into Google Slides using the Red Hat Standard template.
The workflow is **content-first**: build a complete deck spec before touching
the template. The template supplies visuals only — all wording comes from
the spec.

## Template

**Red Hat Standard Presentation Template**
- **Template ID:** `1zg_T6Hyxbv_QNF5pauLiHl2QZ41eXyIwAOA1rdspvgM`
- **Location:** Cursor/Claude folder in Drive

Use only one theme per deck (light or dark). The default is the light theme.

## Workflow

### Step 1: Read the note

Read the note file (HTML from `~/Desktop/Notes Export/` or markdown from
`notes/`). Extract: title, date, summary, key points, decisions, open
questions, next actions, and tags.

### Step 1.5: Choose a story arc

Read [references/story-arcs.md](references/story-arcs.md) and select the
arc that fits the note's content:

- **Journey** — for updates, retrospectives, sprint reviews
- **Problem-Tension-Resolution** — for proposals, tool introductions
- **Myth-Busting** — for research findings, challenging assumptions

The arc determines slide order, headline tone, and layout variety.

### Step 1.75: Write headlines first

Draft one headline per slide as an **assertion**, not a label. Read them
in sequence — they should tell the complete story on their own.

| Label (avoid) | Assertion (use) |
|---|---|
| What I Built | I built 10 skills in 2 weeks |
| Key Highlights | 100% eval pass rate across 11 assertions |
| How I Evaluated | Structured evals proved the skill adds value |

Show the headlines to the user for approval before building the full spec.
If the headlines don't tell a story, rewrite them before proceeding.

### Step 2: Build the deck spec (content lock)

**Do not copy or touch the template until this step is complete.**

From the headlines and note content, produce a complete YAML deck spec
following the schema in [templates/deck-spec.md](templates/deck-spec.md):

- One entry per slide matching the approved headline sequence
- `story_arc` field in meta (journey, problem-resolution, myth-busting)
- Every `text_fields` value filled with final text or `[CLEAR]`
- Character limits enforced NOW (see content fitting limits below)
- `layout_hint` matches a display name from [references/slide-categories.md](references/slide-categories.md)
- Vary layouts by arc beat (see story-arcs.md layout variety table)
- No field contains text from [references/placeholders-to-replace.md](references/placeholders-to-replace.md)

Output the spec. If creating interactively, show it to the user for review.

### Step 3: Copy the template

Only proceed after the spec is complete.

```bash
gws drive files copy --params '{"fileId":"1zg_T6Hyxbv_QNF5pauLiHl2QZ41eXyIwAOA1rdspvgM"}' \
  --json '{"name":"<deck_filename from spec>"}' --format json 2>/dev/null
```

### Step 4: Find donor slides by layout display name

Use `presentations get` to map every slide by its layout display name.
**Never use slide indices** — they change between copies.

```python
layout_names = {l["objectId"]: l["layoutProperties"]["displayName"]
                for l in data["layouts"]}

donors = {}
for slide in data["slides"]:
    name = layout_names.get(slide["slideProperties"]["layoutObjectId"], "?")
    imgs = sum(1 for pe in slide["pageElements"] if pe.get("image"))
    if name not in donors or imgs > donors[name]["imgs"]:
        donors[name] = {"oid": slide["objectId"], "imgs": imgs}
```

Pick the donor with the **most images** for each layout — this gets the
richest visual version (with icons, photos, decorative elements).

### Step 5: Delete non-donor slides

Keep one donor per needed layout category. Delete everything else from
the end backward in batches of ~34.

### Step 6: Duplicate donors and replace ALL text

For each slide in the deck spec:

1. **Duplicate** the matching donor via `duplicateObject`. NEVER use
   `createSlide` — it produces bare slides without images or icons.
2. **Read** the duplicate's placeholder IDs via `presentations get`.
3. **Replace** every placeholder with the spec's `text_fields`:
   - Delete existing text, then insert new text
   - `[CLEAR]` fields: delete text, leave empty
   - Run in small batches (3-5 requests, 0.3s delays)
4. After all slides are built, **delete unused donors**.

### Step 7: Clean up

- Clear master slide text (`g3ad37377157_0_2` and `g3ad37377157_0_3`)
- Delete Quick Tip shapes: scan for non-placeholder elements with "Quick
  tip" text. Quick Tips can hide in three places:
  1. **Direct shapes** on the slide (shapeType with text containing "Quick tip")
  2. **Element groups** (`elementGroup.children[]`) — check each child's
     text. If any child has "Quick tip", delete the parent group.
  3. **Layout-level** elements — these can't be deleted from the slide.
     If the PDF export shows Quick Tips that aren't on the slide instance,
     the layout has them baked in. Switch to a different layout.
- PRESERVE all images — they are branding elements

### Step 8: Reorder slides

Move slides one at a time with `updateSlidesPosition` to match the
deck spec's `order` field.

### Step 9: Purge verification

Run the validation script:

```bash
python3 .cursor/skills/notes-to-slides/scripts/validate-slides.py <presentationId>
```

This checks:
- Forbidden placeholder strings from [references/placeholders-to-replace.md](references/placeholders-to-replace.md)
- Image counts per layout type (catches bare `createSlide` slides)
- Empty TITLE/BODY placeholders
- Quick Tip shapes

**Zero issues required before handoff.** Fix and re-run until clean.

### Step 10: PDF export check

```bash
gws drive files export --params '{"fileId":"<id>","mimeType":"application/pdf"}' \
  --output slides-export.pdf 2>/dev/null
```

Read the PDF to catch layout-level issues the API can't see (Quick Tips
baked into layouts, text from presenter fields). Delete the PDF after.

### Step 11: Open and report

```bash
open "https://docs.google.com/presentation/d/<presentationId>/edit"
```

Report: title, URL, slide count, template used. Recommend human review
before presenting — per Red Hat AI brand guidelines.

## Content fitting limits

| Layout display name | Area | Max chars | Max lines |
|---|---|---|---|
| Title slide with image | Title | 40 | 2 |
| Title slide with image | Subheading | 40 | 1 |
| Title slide with image | Presenter | 40 | 2 |
| Interior title left | Title | 60 | 3 |
| Interior title left | Each column | 80 | 3 |
| Interior overview | Body | 250 | 8 |
| Interior title and body | Body | 350 | 8 |
| Interior three column | Each column | 120 | 4 |
| Interior title and two column body | Each body | 200 | 6 |
| Interior four column | Each column | 80 | 3 |
| Interior data three callouts | Each callout | 100 | 3 |
| Interior large text | Title | 80 | 3 |
| Closing | Subtitle | 80 | 3 |

If content exceeds limits, split across slides in the deck spec BEFORE
copying the template. Never try to fix overflow after insertion.

## Editing existing decks

When the user wants to modify an existing deck (not create from scratch),
use slide-level editing. Never regenerate the entire deck.

### Read before write

Always `presentations get` the current state first. Compare to the last
known deck spec. If text differs, the user edited it — preserve their
changes on untouched slides.

### Supported edit commands

| User says | Action |
|---|---|
| "Edit slide 3" | Read slide 3, replace its text only |
| "Change the headline on slide 4" | Modify only the TITLE placeholder |
| "Add a slide after slide 3" | Duplicate the nearest donor, insert at position 4, populate |
| "Remove slide 5" | Delete it with `deleteObject` |
| "Swap slides 3 and 4" | Use `updateSlidesPosition` |
| "Make the headlines more assertive" | Read all headlines, rewrite as assertions, update each |

### Two-pass approach

Inspired by [red-hat-quick-deck](https://github.com/toddward/red-hat-quick-deck):

1. **First pass:** Generate the deck from the spec. Show it to the user.
2. **Second pass:** User reviews and requests specific changes. Apply
   slide-level edits only — never regenerate unless the user says "start over."

This keeps user edits safe and makes iteration fast.

## References

- [references/story-arcs.md](references/story-arcs.md) — Narrative structures: Journey, Problem-Resolution, Myth-Busting
- [references/slide-categories.md](references/slide-categories.md) — Layout catalog with 12 categories
- [references/placeholders-to-replace.md](references/placeholders-to-replace.md) — Forbidden template strings
- [templates/deck-spec.md](templates/deck-spec.md) — Required YAML schema for content lock
- [scripts/validate-slides.py](scripts/validate-slides.py) — Automated validation

## What NOT to do

- **NEVER use `createSlide`** — always `duplicateObject` on donor slides
- **NEVER use `createShape`** — use existing placeholders only
- **NEVER copy the template before the deck spec is complete**
- Do not hardcode slide indices — find slides by layout display name
- Do not delete images from template slides — they are branding
- Do not send more than 5 requests per batchUpdate call
- Do not leave any forbidden placeholder text (see purge list)
- Do not overflow text — enforce limits in the deck spec
- Do not mix light and dark theme content slides
