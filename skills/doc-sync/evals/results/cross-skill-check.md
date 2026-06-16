# Cross-Skill Consistency Check

**Date:** 2025-06-16  
**Skills under review:** critique, doc-sync, humanize-text, superpowers  
**Compared against:** notetaking-project, sprint-manager, second-brain-ingest, slack-login, standup-writer, slack-summary, rover-lookup, meeting-prep, work-context

---

## Summary

| Skill | Frontmatter | Description | Input Detection | Output | Tone | Cross-refs | Skill-creator | Overall |
|-------|:-----------:|:-----------:|:---------------:|:------:|:----:|:----------:|:-------------:|:-------:|
| critique | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **ALL PASS** |
| doc-sync | PASS | PASS | PASS | PASS | PASS | FAIL | PASS | **6/7** |
| humanize-text | PASS | PASS | PASS | PASS | PASS | FAIL | PASS | **6/7** |
| superpowers | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **ALL PASS** |

---

## 1. YAML Frontmatter Format

### Convention observed in existing skills

Existing skills use these frontmatter fields:
- `name` (required) — kebab-case identifier
- `description` (required) — multi-line via `>` or `>-`; acts as trigger description
- `disable-model-invocation: true` (optional) — present on data-gathering skills
- `argument-hint` (optional) — placeholder showing expected input
- `license`, `metadata` (rare) — only on notetaking-project

Most existing skills use ONLY `name` + `description`. Some action-oriented skills add `disable-model-invocation: true`. The notetaking skill is an outlier with `license` and `metadata`.

### Results

| Skill | Result | Notes |
|-------|--------|-------|
| critique | **PASS** | Uses `name`, `description` (multi-line `>`), `argument-hint`. Matches pattern. |
| doc-sync | **PASS** | Uses `name`, `description` (multi-line `>`), `argument-hint`. Matches pattern. |
| humanize-text | **PASS** | Uses `name`, `description` (multi-line `>`), `argument-hint`. Matches pattern. |
| superpowers | **PASS** | Uses `name`, `description` (multi-line `>`), `argument-hint`. Matches pattern. |

**Notes:**
- All four new skills use the `>` (folded block scalar) syntax for descriptions while some existing skills use `>-` (folded, strip final newline). This is inconsequential — both are valid YAML and behave identically for description triggering.
- The `argument-hint` field is a nice addition not present on most existing skills. It doesn't conflict with conventions.
- None of the conversational skills should have `disable-model-invocation: true`, and none do. Correct.

---

## 2. Description Quality

### Convention observed in existing skills

Existing descriptions follow a consistent pattern:
1. **What it does** (1-2 sentences)
2. **Trigger phrases** ("Use when the user says..." with 6-12 quoted phrases)
3. **Edge case triggers** ("Also use when...")

The skill-creator guidelines explicitly say descriptions should be "a little bit pushy" — include enough trigger phrases that Claude doesn't under-trigger.

### Results

| Skill | Result | Trigger phrases | Notes |
|-------|--------|:--------------:|-------|
| critique | **PASS** | 10+ | "critique this", "stress test this idea", "poke holes in this", "what could go wrong", "is this a good idea", "devil's advocate", "tear this apart", "what am I missing", "before I commit to this", "sanity check this". Also includes NOT-trigger clarification vs /challenge. Excellent coverage. |
| doc-sync | **PASS** | 9+ | "doc sync", "check my docs", "are my docs up to date", "sync documentation", "what docs are stale", "check this Google Doc against the code", URL paste trigger, "my README is probably outdated", "does this doc still match the code". Good coverage including the URL-paste scenario. |
| humanize-text | **PASS** | 9+ | "humanize this", "make this sound like me", "rewrite this for Slack", "fix this message", "how would I say this", "respond to this", "anti AI voice", paste trigger, "drafts a Slack message and wants it cleaned up", reply-to-message trigger. Thorough. |
| superpowers | **PASS** | 10+ | "brainstorm", "give me ideas", "ideate", "superpowers", "what could I build", "help me think of", "creative directions", "remix this idea", "wildcard ideas", "rapid fire ideas". Also mentions non-coding tasks and domain breadth. Matches the pushy standard. |

All four new skills match or exceed the trigger phrase coverage of existing skills like `rover-lookup` (7 phrases) and `slack-summary` (7 phrases).

---

## 3. Input Detection

### Convention observed in existing skills

Existing skills handle input detection in a consistent pattern:
- **notetaking-project**: Detects content type (meeting notes, research, GitHub, Slack, etc.)
- **second-brain-ingest**: Has a table mapping input types to handling
- **sprint-manager**: Resolves identity first, then proceeds
- **slack-login**: Detects workspace URL or name from prompt

Common pattern: enumerate 3-5 input types → handle each → handle empty input with a prompt.

### Results

| Skill | Result | Input types handled | Empty handling |
|-------|--------|:------------------:|:--------------:|
| critique | **PASS** | Pasted text, short description, empty | Yes — asks "What should I tear apart?" |
| doc-sync | **PASS** | Google Doc URL, Drive search query, local path, "check all docs", empty | Yes — offers 3 bullet options |
| humanize-text | **PASS** | Pasted text to rewrite, message to respond to, both, empty | Yes — asks to paste text |
| superpowers | **PASS** | Topic with mode, topic without mode, existing idea, empty | Yes — explains 4 modes |

All four skills follow the exact same structure as existing skills: numbered list of input types, clear handling for each, and a quoted prompt for empty input. The empty-input prompts are helpful without being verbose.

---

## 4. Output Conventions

### Convention observed in existing skills

Existing skills split into two camps:
1. **File-producing** (notetaking → HTML, standup-writer → paste-ready text, slack-summary → Canvas)
2. **Conversational** (rover-lookup → inline chat, slack-login → instructions + confirmation)

Key rule: Skills that produce files say so explicitly. Conversational skills explicitly say "don't create files."

### Results

| Skill | Result | Output type | Explicit boundary |
|-------|--------|-------------|:------------------:|
| critique | **PASS** | Conversational | "Don't generate HTML pages or files. This is a fast, conversational skill." ✓ |
| doc-sync | **PASS** | Conversational with optional local edits | "Don't generate HTML reports or create files. This is conversational." Offers to edit local docs if asked. ✓ |
| humanize-text | **PASS** | Conversational (paste-ready text) | "Don't create files. Output goes inline in the chat." ✓ |
| superpowers | **PASS** | Conversational | "Don't generate HTML or files. Output is conversational." ✓ |

All four correctly identify as conversational and explicitly prohibit file creation. No accidental promises of HTML reports or artifacts.

---

## 5. Tone Consistency

### Convention observed in existing skills

The skill-creator guidelines say: "Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs." The existing skills use:
- Plain English instructions
- Curious, not hostile tone
- Explain reasoning ("because standups are fast and paste-and-go")
- Occasional casual asides
- MUSTs only when truly critical (e.g., "This skill MUST NEVER write, create, update, or modify data")

### Results

| Skill | Result | Notes |
|-------|--------|-------|
| critique | **PASS** | "Curious, not hostile. You're stress-testing, not attacking." Directly addresses tone. Uses natural language throughout. "Don't be mean. Curious and direct, never dismissive." Excellent. |
| doc-sync | **PASS** | "Be thorough but not paranoid." "Don't guess about drift." Practical and direct without being aggressive. Explains why research matters. |
| humanize-text | **PASS** | Matches the voice it describes — casual, direct, informative. "Seriously. Not one." is emphatic but not hostile. Real examples ground the instructions naturally. |
| superpowers | **PASS** | "Your job is to generate ideas, not evaluate them." Clear framing. "Some ideas will be obvious, some will be weird, and that's the point." Natural and encouraging. |

All four skills match the existing tone: plain English, practical, explains reasoning, avoids bureaucratic MUSTs except where genuinely critical.

---

## 6. Cross-References

### Convention observed in existing skills

Existing skills frequently reference related skills:
- **standup-writer** → references `work-context`, `tomorrow-calendar-accepted`
- **meeting-prep** → references `slack-summary`, `source-reader`, `work-context`
- **notetaking-project** → references `source-reader`
- **second-brain-ingest** → references `source-reader`

Good cross-references serve two purposes:
1. Skill composition (reusing logic from other skills)
2. User routing (suggesting the user try a different skill for adjacent needs)

### Results

| Skill | Result | Cross-references present | Missing |
|-------|--------|------------------------|---------|
| critique | **PASS** | References `/challenge` (differentiates), `/strategize` (for formalizing), `/journal` (for recording). All appropriate and helpful. | None missing. |
| doc-sync | **FAIL** | References `source-reader` implicitly (via Google Workspace MCP patterns). | Missing: Should mention `/notetaking` for users who want to turn drift reports into formatted docs. Should mention `/second-brain-ingest` for users who want to file sync results into the wiki. |
| humanize-text | **FAIL** | No cross-references to other skills. | Missing: Should mention that for longer-form writing (not Slack), users might want a different approach. Could reference that if the user wants to draft a full email rather than a Slack message, `/note-to-email` exists. |
| superpowers | **PASS** | References `/critique` (for stress-testing chosen ideas) and `/strategize` (for turning ideas into plans). Both appear in the "Going Deeper" section. | None missing. |

### Recommended fixes

**doc-sync:** Add to the "Phase 4: Offer to Fix" section:
```markdown
If the user wants to document their findings:
> "Want me to turn this drift report into a formatted note? (`/notetaking`)
> Or file it into your wiki? (`/second-brain-ingest`)"
```

**humanize-text:** Add after the "What NOT to Do" section:
```markdown
## Related Skills

If the user needs something beyond Slack rewrites:
- Full email drafting → `/note-to-email`
- Message content (not voice) needs work → suggest they draft the content first, then run `/humanize-text` on the result
```

---

## 7. Skill-Creator Compliance

### Key guidelines from skill-creator/SKILL.md

1. **Progressive disclosure**: Keep SKILL.md under 500 lines; bundle resources for long content
2. **Description is the trigger**: All "when to use" info goes in the description, not the body
3. **Explain the why**: Theory of mind > rigid MUSTs
4. **Lean prompts**: Remove things not pulling their weight
5. **Examples pattern**: Include examples where useful
6. **Name + description required in frontmatter**

### Results

| Skill | Lines | Under 500? | Why explained? | Examples? | Lean? | Result |
|-------|:-----:|:----------:|:--------------:|:---------:|:-----:|--------|
| critique | 162 | ✓ | ✓ ("The web search is what makes this skill different") | ✓ (output format template) | ✓ | **PASS** |
| doc-sync | 219 | ✓ | ✓ ("Documentation rots silently") | ✓ (output format template, MCP call examples) | ✓ | **PASS** |
| humanize-text | 253 | ✓ | ✓ ("This is speed, not sloppiness") | ✓ (extensive real examples from Evan's messages) | ✓ | **PASS** |
| superpowers | 221 | ✓ | ✓ ("Quantity enables quality") | ✓ (format templates for each mode) | ✓ | **PASS** |

All four skills are well within the 500-line limit, explain their reasoning naturally, include useful examples/templates, and don't contain unnecessary bloat.

**Additional compliance notes:**
- All four use the `$ARGUMENTS` variable pattern for input, which is consistent
- All four have clear "What NOT to Do" sections, preventing common failure modes
- None use excessive ALWAYS/NEVER caps (humanize-text uses them for the hard rules about dashes and buzzwords, which is appropriate — those are genuinely non-negotiable)
- All four explain reasoning behind their constraints rather than just barking orders

---

## Overall Assessment

### Skills that pass all checks: critique, superpowers

These two skills are exemplary. They match all existing conventions, have thorough trigger phrases, proper cross-references, appropriate tone, and follow skill-creator guidelines closely.

### Skills with minor issues: doc-sync, humanize-text

Both fail only on cross-references — a minor omission that doesn't affect functionality but reduces the discoverability of related skills for users.

### Priority fixes

1. **doc-sync** — Add user-routing cross-references to notetaking and second-brain-ingest (low effort, high value for user flow)
2. **humanize-text** — Add a brief "Related Skills" section pointing to note-to-email for non-Slack use cases (low effort, helps avoid misuse)

### Things done exceptionally well across all four new skills

- **Input detection structure** is consistent and thorough
- **"What NOT to Do" sections** prevent the most common failure modes clearly
- **Tone** is perfect — curious, direct, helpful, never hostile
- **Output boundaries** are explicit and correct (no accidental file creation promises)
- **Description trigger coverage** is thorough and "pushy" per skill-creator guidance
- **Length** is appropriate — substantive without bloat
- **The `$ARGUMENTS` pattern** for input detection is consistent across all four

---

## Appendix: Field Comparison Table

| Field | notetaking | sprint-manager | second-brain | slack-login | critique | doc-sync | humanize-text | superpowers |
|-------|:----------:|:--------------:|:------------:|:-----------:|:--------:|:--------:|:-------------:|:-----------:|
| name | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| description | ✓ (>) | ✓ (>-) | ✓ (>-) | ✓ (inline) | ✓ (>) | ✓ (>) | ✓ (>) | ✓ (>) |
| argument-hint | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| disable-model-invocation | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| license | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| metadata | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

The `argument-hint` field is a new convention introduced by these four skills. It's a good pattern — provides UX guidance for users who trigger the skill manually. Consider backporting to existing skills.
