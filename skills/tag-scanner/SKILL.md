---
name: tag-scanner
description: >
  Scans notes for tags, assigns PatternFly color-coded labels, and builds a
  cross-linked tag index. Use when the user says "scan my notes", "find related
  notes", "update tags", "build my index", "what notes are related to [topic]",
  or "link my notes together".
license: MIT
metadata:
  author: <YOUR_USERNAME>
  version: 2.0.0
  category: productivity
  tags: [notetaking, tags, index, patternfly]
---

# Tag Scanner

Scans notes in `~/Desktop/Notes Export/`, reads their tags, and builds a
cross-linked index. Tags use PatternFly Label color conventions.

---

## Tag color system (PatternFly 6 Labels)

| Category | PF modifier | Hex | Examples |
|---|---|---|---|
| Red Hat / brand | `pf-m-red` | `#c9190b` | `rhat`, `patternfly`, `openshift` |
| People | `pf-m-blue` | `#2b9af3` | `zack`, `priya`, `steven-huels` |
| Tools / tech | `pf-m-teal` | `#009596` | `jira`, `cursor`, `mcp`, `quarto` |
| Projects | `pf-m-purple` | `#6753ac` | `adlc`, `aisdlc`, `vlm`, `instructlab` |
| Status: positive | `pf-m-green` | `#3e8635` | `decision`, `shipped`, `resolved` |
| Status: warning | `pf-m-orange` | `#f0ab00` | `blocker`, `action-item`, `wip` |
| Neutral | `pf-m-grey` | `#8a8d90` | `meeting`, `standup`, `freeform` |

When assigning tags, always use the correct PF color class for the category.

---

## Workflow

### Step 1: Scan notes

Walk every `.html` file in `~/Desktop/Notes Export/`.
For each file, extract tags from the PF LabelGroup near the top of the document.
Record: `{ filename, title, date, tags[] }`

Build an inverted index: `tag → [list of notes that carry it]`.

### Step 2: Determine scope

| Mode | Trigger | What it does |
|---|---|---|
| **Full index** | "build my index", "scan my notes" | Regenerates the tag index |
| **Single note** | "update tags for this note" | Assigns/fixes tags on one note |
| **Query** | "what notes are about [topic]" | Returns a list — no files modified |

### Step 3: Find related notes

For each note, compute related notes by:
1. Finding all notes that share at least one tag
2. Sorting by number of shared tags (descending), then by date
3. Taking the top 5

### Step 4: Report results

For queries: return the list in chat.
For full scans: output a summary showing tag counts and related note links.

---

## Tag naming conventions

- Lowercase, hyphen-separated: `red-hat`, `cursor-skills`
- Specific over broad: `openshift` not `tools`
- People names as tags: `zack`, `jessica-forrester`
- Reuse existing tags whenever possible — overlap is what creates connections
