# Deck spec — content lock before template copy

The agent must build this structure from the user's note BEFORE copying the
template. Every slide in the final deck maps to one entry here with final
text. The template supplies visuals only — all wording comes from this spec.

## Rules

1. One entry per slide in presentation order (title through closing).
2. Each entry has `role`, `layout_hint` (layout display name from the
   template catalog), and `text_fields` with every user-visible string.
3. Optional areas the user doesn't need: set value to `[CLEAR]`.
4. Character limits are enforced HERE, not after insertion. If a field
   exceeds its layout limit, shorten it or split the slide before proceeding.
5. If the user provides unstructured notes, infer the spec and output it
   for review before executing.

## Schema

```yaml
meta:
  presentation_title: ""
  subtitle: ""                    # or [CLEAR]
  presenter_name: ""
  presenter_title: ""             # or [CLEAR]
  deck_filename: ""               # for the copied template file name

slides:
  - order: 1
    role: title
    layout_hint: "Title slide with image"
    text_fields:
      title: ""                   # max 40 chars, 2 lines
      subheading: ""              # max 40 chars, 1 line — or [CLEAR]
      presenter: ""               # max 40 chars, 2 lines (name\ntitle)

  - order: 2
    role: section_opener
    layout_hint: "Interior title left"
    text_fields:
      title: ""                   # max 60 chars, 3 lines
      subheading: ""              # or [CLEAR]
      col1: ""                    # max 80 chars, 3 lines
      col2: ""                    # max 80 chars, 3 lines
      col3: ""                    # max 80 chars, 3 lines
      section_marker: "[CLEAR]"
      source: "[CLEAR]"

  - order: 3
    role: agenda
    layout_hint: "Interior overview"
    text_fields:
      title: ""                   # max 40 chars
      section_label: "Agenda"     # or user's label
      body: ""                    # max 250 chars, 8 lines

  - order: 4
    role: content
    layout_hint: "Interior title and body"
    text_fields:
      title: ""                   # max 50 chars, 1 line
      body: ""                    # max 350 chars, 8 lines
      section_marker: "[CLEAR]"
      source: "[CLEAR]"

  - order: 5
    role: three_column
    layout_hint: "Interior three column"
    text_fields:
      title: ""                   # max 50 chars
      col1: ""                    # max 120 chars, 4 lines
      col2: ""                    # max 120 chars, 4 lines
      col3: ""                    # max 120 chars, 4 lines
      subheading: "[CLEAR]"
      section_marker: "[CLEAR]"
      source: "[CLEAR]"

  - order: N
    role: closing
    layout_hint: "Closing"
    text_fields:
      title: "Thank you"
      subtitle: ""                # presenter info or custom closing

# Roles: title, section_opener, agenda, content, two_column,
#         three_column, data_callouts, timeline, quote,
#         large_text, image, closing
#
# layout_hint must match a layout display name from the template.
# See references/slide-categories.md for the full catalog.
```

## Minimum bar

- At least 3 slides: title + 1 content + closing.
- No `text_fields` value may be empty string "" in the final spec
  (use `[CLEAR]` for intentionally blank fields).
- Every field must fit within its layout's character limit.
- No field may contain text from `references/placeholders-to-replace.md`.
