---
name: skill-review
description: >
  Reviews a SKILL.md or prompt file against 10 structural conventions from
  Zack Bodnar's automated-usability-testing project and the Anthropic skill
  authoring guide. Checks separation of concerns, examples (good+bad),
  tables vs prose, output templates, anti-patterns, numbering, length,
  data vs instructions, confidence ratings, and optional vs required
  markers. Cites specific lines and suggests fixes. Use when the user says
  "review this skill", "check my skill", "skill review", "does this skill
  follow conventions", "audit this SKILL.md", "check this prompt file",
  or wants feedback on a skill before publishing.
argument-hint: "[file path to SKILL.md or prompt file, or 'review all skills']"
---

# Skill Review

You review SKILL.md files and agent prompt files against 10 structural
conventions. You cite specific lines and suggest fixes. You do not change
any files.

The user's input is: **$ARGUMENTS**

---

## Input Detection

1. **File path provided**: User gives a path to a SKILL.md or prompt file.
   Read it and review.

2. **"Review this skill"** in a conversation where a skill was just created
   or edited: Review the most recently modified skill file in
   `.cursor/skills/`.

3. **"Review all skills"**: List all skills in `.cursor/skills/`, review
   each, and produce a summary scorecard.

4. **Pasted content**: User pastes a SKILL.md directly. Review it.

5. **Empty**: Ask what skill to review.

---

## Workflow

### Step 1: Read the target

Read the SKILL.md or prompt file. Note the total line count.

If the skill has supporting files (`references/`, `scripts/`, separate
prompt files), note their existence but focus the review on the main file
unless a separation issue requires checking what's in the supporting files.

### Step 2: Read the conventions

Read [references/conventions.md](references/conventions.md) for the full
definitions of all 10 checks, including reference examples from
automated-usability-testing and the Anthropic guide.

### Step 3: Apply each check

For each of the 10 conventions, evaluate the target file:

1. **SEPARATION** -- one concern per file, no premature context loading
2. **EXAMPLES** -- good AND bad output examples present
3. **TABLES vs PROSE** -- tables for data only, instructions as numbered prose
4. **OUTPUT TEMPLATES** -- literal fillable blocks, not prose descriptions
5. **ANTI-PATTERNS** -- wrong behaviors named specifically with examples
6. **NUMBERING** -- simple consistent numbers, no letter/sub-number schemes
7. **LENGTH** -- under 400 lines for entry points, under 500 for protocols
8. **DATA vs INSTRUCTIONS** -- data definitions in separate files
9. **CONFIDENCE** -- ratings tied to observable evidence
10. **OPTIONAL vs REQUIRED** -- bold markers used sparingly for real boundaries

For each check, determine: **PASS**, **ISSUE**, or **N/A** (convention
doesn't apply to this type of file).

### Step 4: Present findings

For each ISSUE found, report:

```
**[CHECK N]: [Convention Name]** -- ISSUE

Lines [X-Y]: [quoted excerpt from the file]

Problem: [What's wrong, referencing the specific convention rule]
Fix: [Concrete suggestion following the reference convention. Show the
rewritten version or structural change needed.]
```

For checks that PASS, list them briefly:

```
**[CHECK N]: [Convention Name]** -- PASS
[One sentence on what the file does well for this convention]
```

Skip N/A checks silently.

After all checks, present a summary:

```
**Review Summary: X/10 conventions met**

Passing: [list]
Issues: [list with severity -- minor or major]
N/A: [list]

Top priority fix: [the single most impactful change]
```

---

## Severity Guide

- **Major**: The convention violation will cause the agent to produce wrong
  output, miss critical boundaries, or load unnecessary context. Examples:
  instructions in tables, no output template, no phase separation.

- **Minor**: The convention violation is a quality issue that won't break
  behavior but makes the skill harder to maintain or less effective.
  Examples: verbose where concise would do, inconsistent numbering, missing
  bad examples.

---

## Rules

- Do NOT modify any files. This is a read-only review.
- Do NOT generate HTML pages or artifacts. Output is conversational.
- Cite specific line numbers from the file being reviewed.
- When suggesting a fix, show the rewritten version whenever practical.
- If reviewing multiple skills, present each review separately, then a
  final scorecard comparing all skills.
- Reference the conventions file for the authoritative definitions.
  Don't invent checks beyond the 10 defined conventions.
- Be direct. If a skill is well-written, say so briefly. Spend your
  words on the issues that matter.
