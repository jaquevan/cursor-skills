---
name: notetaking
description: >
  Transforms raw notes into polished, self-contained HTML reports styled with
  PatternFly 6 and Red Hat typography. Use when the user says "take notes",
  "format my notes", "format this", "process my inbox", pastes unstructured
  text, or points to a file. Also use when the user says "reformat this note"
  or "fix this note". Also use when the user shares a GitHub repo URL or
  skill path and wants to document it. Outputs a styled HTML file to
  ~/Desktop/Notes Export/.
license: MIT
metadata:
  author: ejaquez
  version: 3.1.0
  category: productivity
  tags: [notetaking, html, patternfly, red-hat]
---

# Notetaking

Takes raw input and outputs a polished, self-contained HTML report. The output
should look like professional documentation — something you'd attach to an
email to your manager, share in Slack, or keep as an internship artifact.

---

## How to process content

### Detecting content type

Before formatting, identify what kind of input this is:

| Input type | How to handle |
|---|---|
| Meeting notes | Extract decisions, actions, discussion. Standard layout. |
| Research / analysis | Lead with findings. Use tables for comparisons. |
| **GitHub repo / skill** | Read the README and/or SKILL.md. Build a quick-start at the top. |
| Learning notes | Key concepts first, then details. |
| Raw paste | Detect type from content, then apply the right approach. |

### GitHub repos and skills

When the user shares a GitHub URL, a repo path, or a SKILL.md file:

1. **Read the README.md** (or SKILL.md) from the repo/path
2. Build a **"Getting started" section at the top** of the note with:
   - What the tool/skill does (one sentence)
   - Installation commands (exact, copy-pasteable)
   - Key commands or trigger phrases
   - Prerequisites (dependencies, MCP servers, credentials)
3. Then below, include the full structured content (use cases, architecture,
   configuration details, etc.)

The getting-started block should be immediately actionable — someone opening
this note should be able to install and use the tool within 60 seconds of
reading it.

### Reading the raw notes

Understand what the notes are *about* before formatting. Identify:
- The core topic or event
- Key people mentioned
- Decisions made (explicit or implicit)
- Action items with owners
- Numbers, metrics, or data points worth highlighting
- Relationships to known projects (OpenShift, PatternFly, ADLC, etc.)

### Condensing vs. preserving

Adapt based on length:
- **Short notes (< 500 words):** Preserve fully. Just structure and clean up.
- **Medium notes (500–1500 words):** Keep all substance. Cut filler phrases,
  repeated context, and meeting-transcript artifacts ("um", "so basically").
- **Long notes (1500+ words):** Condense to what matters — decisions, data,
  action items, and the key narrative. Summarize discussion; don't transcribe it.

### Writing the summary

The summary is the single most important element. It answers:
**"What should someone do differently after reading this?"**

Prioritize in this order:
1. **Decisions/outcomes** — what was decided or what changed
2. **The key insight** — the one thing to walk away knowing
3. **The recommendation** — what to use, what to avoid, what to do differently

Rules:
- Lead with the conclusion or recommendation in bold
- Include the most compelling number or result
- Name alternatives if they exist
- State what to avoid and why
- 2–3 sentences. No hedging.
- Never start with "This note covers..." or "We discussed..."

### Voice

Write in **neutral third-person** — like documentation.
- "The evaluation found..." not "I found..."
- "The recommendation is..." not "My recommendation is..."
- "Use Cursor for deep audits" not "I'd recommend Cursor"

This makes notes shareable without editing and gives them a professional,
authoritative tone regardless of who wrote the raw input.

### Length

Don't cut substance — cut filler and repetition. The output should be as long
as it needs to be to preserve all meaningful content. Remove:
- Meeting-transcript artifacts ("um", "so basically", "as I mentioned")
- Repeated context already covered in the summary
- Filler phrases ("it's important to note that", "at the end of the day")
- Process narration ("we then discussed", "next we moved to")

Keep: every decision, data point, action item, and substantive observation.

### Assigning tags

Assign 5–8 tags based on content. Map to categories:
- **Brand** (Red Hat ecosystem): openshift, patternfly, instructlab, rhel
- **Tools**: cursor, gemini, claude, jira, figma, mcp
- **Projects**: adlc, aisdlc, vlm, archie
- **People**: zack, priya, steven-huels, beau
- **Type**: meeting, research, standup, learning

---

## HTML output design

Generate a single self-contained HTML file. The design language is:
**PatternFly-influenced professional report — minimal, warm, readable.**

### Design principles

Follow the Red Hat brand color system strictly:
- **Core colors only**: white, black (`#151515`), gray-10 (`#f5f5f5`), dark (`#212427`)
- **Red Hat red (`#ee0000`) as pops only**: separator bars, bullet dots, summary
  border, highlight icons. Never flood. Never on backgrounds.
- **interaction-blue (`#0066cc`)** for links only. Nothing else blue.
- **No teal, no custom blues, no purples** in note bodies. Keep palette tight.
  If a color clashes with the Red Hat red pops, remove it.
- Callouts use neutral gray (`#f9f9f9`) backgrounds with gray left borders.
  Only the small icon carries semantic color (green check, orange warning).
- All sections should feel unified — same visual weight, same neutral palette.
  A reader should not notice jarring color shifts between sections.
- Tags are clickable `<a>` elements (`href="#tag-name"`) for future cross-linking
- Dark sections: ALL text must be `#e0e0e0`+ for body, `#ffffff` for headings/th
- Generous whitespace everywhere
- Full viewport width with responsive padding
- Typography: Red Hat Display (headings), Red Hat Text (body), Red Hat Mono (code)

### Header branding

Include the Red Hat fedora hat as a subtle watermark in the header:
- One large SVG, top-right of the dark header, white at 6% opacity, ~280px wide
- No red logo version — only the grey/white watermark
- The SVG path is in `assets/redhat-hat.svg`
- Header section needs `position:relative; overflow:hidden;`

### Layout structure

The page is a vertical sequence of full-width sections with alternating
backgrounds. No max-width cap — content fills the screen with padding.

Not all sections are required — use only what the content needs. Short notes
might only have: Title → Summary → Content → Footer.

For GitHub/skill notes, add a Getting Started section immediately after the
summary, before the main content.

### What NOT to do

- No cards with colored top borders (looks cluttered at scale)
- No accordions (content should be visible, not hidden)
- No banner components
- No "skip to content" buttons
- No back-to-top buttons
- No PF page wrapper classes (they constrain width)
- No red hat logo in the corner (only the grey watermark hat)
- **Never put dark/muted text on a dark background.** On dark sections, ALL
  text (body, table cells, list items, strong, th) must be light: `#e0e0e0`
  minimum for body, `#ffffff` for headings and table headers. If you can't
  read it at arm's length, the contrast is wrong.

### Footer

Every note ends with a dark footer section containing:
1. Link to original source (if processing a file)
2. Any relevant external links
3. **Always last**: credit line linking to the author's GitHub:
   `github.com/ejaquez`

### Responsive padding

```css
.s { padding: 4rem; }
@media (min-width: 1200px) { .s { padding: 4.5rem 10rem; } }
@media (min-width: 1700px) { .s { padding: 5rem 16rem; } }
@media (max-width: 768px)  { .s { padding: 2.5rem 1.25rem; } }
```

### Export

Save to: `~/Desktop/Notes Export/<YYYY-MM-DD>-<slug>.html`

If processing a file, move the original to:
`~/Desktop/Notes Export/originals/<filename>`

---

## Refinement

When the user says "fix the summary", "add detail to X", or "reformat this":
- Read the existing HTML
- Apply only the requested change
- Overwrite in place
- Confirm what changed

Full reprocessing only when the user says "reprocess" or "start over".

---

## Additional resources

- Component HTML reference → [references/component-map.md](references/component-map.md)
- Red Hat hat SVG → [assets/redhat-hat.svg](assets/redhat-hat.svg)
