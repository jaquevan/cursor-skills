# Slide Categories & Layout Reference

The Red Hat Standard Template has 53 layouts organized into 12 categories.
Each layout exists in both light theme (IDs starting with `g3b0`, `g3925`,
`g3b6`) and dark theme (IDs starting with `g3d43`). Always use layouts from
one theme only.

This reference helps the skill match note content to the right layout.

---

## Category 1: Title & Closing

**When to use:** First and last slides. Always required.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Title (2 presenters) | g3b0f681f8ea_0_321 | TITLE(1), SUBTITLE(), SUBTITLE(1), SUBTITLE(2) | Multi-presenter decks |
| Title with image | g3b0f681f8ea_0_439 | TITLE(), SUBTITLE(), SUBTITLE(1), SUBTITLE(2) | Single presenter + branding photo |
| Closing | g3b0f681f8ea_0_330 | TITLE(), SUBTITLE(1) | Clean end slide with social links |
| Closing with image | g3b0f681f8ea_0_543 | TITLE(), SUBTITLE(), SUBTITLE(1) | End slide with photo (has Quick Tip - AVOID) |

**Recommendation:** Use "Title with image" for opening, "Closing" (simple) for end.

---

## Category 2: Section Openers & Dividers

**When to use:** Section breaks, chapter transitions, "here's what's next" slides.

**Key principle:** A section opener should preview the content that follows,
not just state a title. Choose the layout based on how much preview context
the section needs.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| **Interior title left** | g3925d247048_4_862 | TITLE(), SUBTITLE(2-4,8) | Big title + 3 callout previews with icons. Best for "Here's what I worked on" or "What we'll cover" with project-level detail. |
| **Interior title** (6-up grid) | g3b0f681f8ea_0_915 | TITLE(), SUBTITLE(1,2) + 6 TEXT shapes | Title + 6 body areas in 2x3 grid with icons. For sections with 4-6 sub-topics to preview. |
| **Interior large text** | g3925d247048_4_1004 | TITLE(), SUBTITLE(), SUBTITLE(5) | One powerful statement. For impactful transitions like "What I learned" or a key insight. |
| Divider (simple) | g3b0f681f8ea_0_880 | TITLE(), SUBTITLE() | Clean minimal break with just title + marker. |
| Divider with title | g3b0f681f8ea_0_605 | TITLE(), SUBTITLE(), SUBTITLE(1) | Split layout — title left, text right. AVOID for short text on the right side; it renders tiny in a gray panel. |

**Decision guide for section openers:**
- 0 preview items → Large text or Simple divider
- 1-2 preview items → Large text with details in subtitle
- 3 preview items → Interior title left (3 callout columns)
- 4-6 preview items → Interior title (6-up grid)
- Just a clean break → Simple divider

---

## Category 3: Agenda & Overview

**When to use:** Showing what will be covered, table of contents.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Interior overview | g3925d247048_4_16 | TITLE(), SUBTITLE(1), BODY(1), SUBTITLE() | 3-5 topics with descriptions |
| Interior agenda (2-col) | g3b0f681f8ea_0_970 | TITLE(), SUBTITLE(1), BODY(2), BODY(3), SUBTITLE() | 6-10 topics in two columns |

**Limits:** Overview body holds ~10 lines. Agenda body holds ~20 items split across 2 columns.

---

## Category 4: Content Body

**When to use:** Main content slides with paragraphs and bullet points.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Title and body | g3925d247048_4_235 | TITLE(), BODY(), SUBTITLE(5) | Standard bullet content |
| Title, subhead, body | g3925d247048_4_202 | TITLE(), SUBTITLE(1), BODY(), SUBTITLE(5) | Content with a subheading |
| Body only | g3925d247048_4_254 | BODY(), SUBTITLE(5) | When the content speaks for itself |
| Title left | g3925d247048_4_862 | TITLE(), SUBTITLE(2-4,8) | Large title with supporting callouts |
| Interior title | g3b0f681f8ea_0_915 | TITLE(), SUBTITLE(1), SUBTITLE(2) | Big statement slide |

**Limits:** Body holds ~8 lines of bullets (350 chars max). If content exceeds this, duplicate the slide and split.

**Recommendation:** "Title and body" is the workhorse layout.

---

## Category 5: Two Column

**When to use:** Comparing two things, showing pros/cons, before/after.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Title + two column body | g3925d247048_4_273 | TITLE(), BODY(), BODY(1), SUBTITLE(1) | Two text columns with headers |
| Title + column body | g3925d247048_4_299 | TITLE(), BODY(1), SUBTITLE(1) | One column text + one column visual |
| Two chevrons | g3925d247048_4_85 | TITLE(), SUBTITLE(1-3,5) | Two process steps with arrows |

**Limits:** Each column body holds ~6 lines (200 chars).

---

## Category 6: Three Column

**When to use:** Three parallel items, key highlights, feature comparison.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Three column | g3925d247048_4_922 | TITLE(), SUBTITLE(1,3,4,8) | 3 items with icons above |
| Three chevrons | g3925d247048_4_47 | TITLE(), SUBTITLE(1-5) | 3 process steps with arrows |

**Limits:** Each column holds ~4 lines (120 chars). Has 3 icon images.

---

## Category 7: Four+ Column & Grid

**When to use:** 4+ parallel items, feature matrices.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Four column | g3925d247048_4_800 | TITLE(), SUBTITLE(1,3,4,6,8) | 4 short items |
| Two by two | g3925d247048_4_747 | TITLE(), SUBTITLE(1-4,8) | 2x2 grid of items |

**Limits:** Very short text per cell — 2-3 lines max (80 chars).

---

## Category 8: Data & Callouts

**When to use:** Statistics, metrics, percentages, KPIs.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Three callouts | g3925d247048_4_394 | TITLE(), many SUBTITLE() | 3 big numbers with labels |
| Two callouts | g3925d247048_4_449 | TITLE(), many SUBTITLE() | 2 big numbers with context |
| Two pies | g3925d247048_4_498 | TITLE(), SUBTITLE(1-4,8) | 2 pie charts with labels |
| Large pie | g3925d247048_4_545 | TITLE(), many SUBTITLE() | Single large chart |
| Interior callout | g3b0f681f8ea_0_740 | SUBTITLE(), SUBTITLE(1) | Full-slide callout statement |

**Recommendation:** Use "Three callouts" for stats dashboards, "Interior callout" for a single impactful number.

---

## Category 9: Quotes

**When to use:** Customer quotes, testimonials, key statements.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Large quote | g3925d247048_4_708 | TITLE(), SUBTITLE(8) | One big quote + attribution |
| Two column quote | g3925d247048_4_658 | TITLE(), SUBTITLE(1-4,8) | Two quotes side by side |
| Three column quote | g3925d247048_4_600 | TITLE(), many SUBTITLE() | Three testimonials |

---

## Category 10: Image Focused

**When to use:** When visuals are the primary content.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Full-width image | g3b0f681f8ea_0_902 | (none) | Full-bleed photo slide |
| Image left | g3925d247048_4_975 | TITLE(), SUBTITLE(4,8) | Image on left, text on right |

---

## Category 11: Timeline

**When to use:** Chronological events, roadmaps, milestones.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Vertical timeline | g3925d247048_4_321 | SUBTITLE(1,3,5) | 3-5 milestones stacked |
| Horizontal timeline | g3925d247048_4_351 | TITLE(), many SUBTITLE() | 3-5 milestones in a row |

---

## Category 12: Large Text

**When to use:** Key message slides, section statements.

| Layout | ID (light) | Placeholders | Best for |
|---|---|---|---|
| Interior large text | g3925d247048_4_1004 | TITLE(), SUBTITLE(), SUBTITLE(5) | One big statement |

---

## Expected Image Counts

When a slide is properly created via `duplicateObject` from a donor template
slide, it should have the following number of images. If images are missing,
the slide was likely created bare with `createSlide` — which is wrong.

| Layout display name | Expected images | What the images are |
|---|---|---|
| Title slide with image | 2 | Product logo + photo |
| Closing slide with image | 1 | Photo/branding |
| Closing | 0 | Social links only |
| Interior title left | 3 | Icons above callout columns |
| Interior three column | 3 | Icons above each column |
| Interior four column | 4 | Icons above each column |
| Interior large text | 1 | Decorative element |
| Interior image left | 1 | Photo placeholder |
| All other layouts | 0 | Text-only layouts |

The validation script (`scripts/validate-slides.py`) checks these counts
automatically. A mismatch flags the slide as potentially bare.

---

## Content-to-Layout Matching

When choosing a layout for note content, use this decision tree:

1. **Is it a key metric or number?** → Data callouts (Cat 8)
2. **Is it a comparison of 2 things?** → Two column (Cat 5)
3. **Is it 3 parallel items?** → Three column (Cat 6)
4. **Is it 4+ items in a grid?** → Four+ column (Cat 7)
5. **Is it a timeline or roadmap?** → Timeline (Cat 11)
6. **Is it a quote or testimonial?** → Quotes (Cat 9)
7. **Is it a single key message?** → Large text (Cat 12) or Callout
8. **Is it a list of bullet points?** → Content body (Cat 4)
9. **Is it a section break?** → Divider (Cat 2)
10. **Is it an agenda/overview?** → Agenda (Cat 3)
