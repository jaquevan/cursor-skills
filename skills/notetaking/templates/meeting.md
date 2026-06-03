---
title: "{{TITLE}}"
date: {{YYYY-MM-DD}}
author: "{{AUTHOR}}"
categories: [meeting]
tags: [{{TAGS}}]
---

**TL;DR:** {{ONE_SENTENCE_SUMMARY}}

## Contents

- [Context](#context)
- [Discussion](#discussion)
- [Decisions](#decisions)
- [Action Items](#action-items)
- [Links](#links)

---

## Context

| Field       | Value                    |
|-------------|--------------------------|
| Date        | {{YYYY-MM-DD HH:MM}}     |
| Attendees   | {{NAME, NAME, NAME}}     |
| Meeting type | {{sync \| planning \| review \| 1:1 \| kickoff}} |
| Related to  | {{project or topic}}     |

::: {.callout-note title="Background"}
{{Why this meeting was called and what it was trying to resolve or decide.}}
:::

---

## Discussion

{{Narrative summary of what was discussed. Use ### subheadings for distinct topics.
Keep to prose — bullet lists only for parallel enumerable items.}}

### {{Topic 1}}

{{Discussion summary}}

### {{Topic 2}}

{{Discussion summary}}

---

## Decisions

::: {.callout-important title="Decision"}
{{State the decision clearly. One decision per callout. Remove this block if no formal decisions were made.}}
:::

---

## Action Items

- [ ] @{{owner}} — {{task description}} (due: {{YYYY-MM-DD}})
- [ ] @{{owner}} — {{task description}}

---

## Links

- [{{Descriptive Label}}]({{URL}}) — {{one-line context}}
