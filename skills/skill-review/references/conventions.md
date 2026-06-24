# Skill Review Conventions

10 structural conventions for reviewing SKILL.md files and agent prompts.
Derived from three sources:

- **Zack Bodnar's automated-usability-testing** (`prompts/evaluate-flow.md`,
  `evaluate.md`, `score.md`) at `~/Desktop/automated-usability-testing/`
- **Anthropic's Complete Guide to Building Skills for Claude** (PDF)
- **Anthropic's Best Practices** (vendored in Superpowers plugin)

For each convention: the rule, what to look for, a reference example, and
the common violation pattern.

---

## 1. SEPARATION

**Rule:** Each file should have one role or concern. If a file loads context
the agent shouldn't see yet, that's a structural violation.

**What to look for:**
- Does the SKILL.md try to be the instructions AND the data source AND the
  output template all in one?
- Could a section be split into a separate file that gets loaded only when
  needed?
- Does reading the file front-to-back expose information the agent
  shouldn't have at a particular phase?

**Reference:** `evaluate-flow.md` is one canonical protocol, but it has a
hard `**STOP HERE**` boundary between Phase 1 (Actor) and Phase 2
(Evaluator). `evaluate.md` and `score.md` are thin wrappers (~141 and ~89
lines) that point to specific sections -- they never duplicate content.
The Phase 1 agent is explicitly forbidden from reading Phase 2's rubric.

**Common violation:** A single SKILL.md that contains persona data, scoring
rubrics, behavioral instructions, and output templates all mixed together
with no structural separation.

---

## 2. EXAMPLES

**Rule:** Show both GOOD and BAD output examples. If agents commonly
produce the wrong kind of output, the bad example must be shown with a
one-sentence explanation of why it's wrong.

**What to look for:**
- Are there literal output examples (not just descriptions of what output
  should look like)?
- Is there at least one BAD example showing what the agent should NOT
  produce?
- Does the BAD example have a one-sentence explanation of the specific
  problem?

**Reference:** `evaluate-flow.md` lines 85-113:

```
**Example of GOOD think-aloud (Deena-Junior):**
STEP 3:
- What I see: A form with fields for "Name"...
- What I'm thinking: I can fill in the name... But "Resource Name"
  auto-filled with something that has dashes... And what's a PVC?

**Example of BAD think-aloud (too analytical):**
STEP 3:
- What I'm thinking: This is a usability issue. The term PVC is not
  user-friendly... This violates the principle of speaking the user's
  language.

The bad example is evaluating. The actor does NOT evaluate.
```

**Common violation:** Skills that describe desired output in prose ("the
output should be concise and actionable") without showing a literal example
of what that looks like, or skills that show only good examples without
naming what goes wrong.

---

## 3. TABLES vs PROSE

**Rule:** Tables are for DATA only (rubrics, schemas, scoring criteria,
input/output specs, reference lookups). Instructions should be numbered
prose.

**What to look for:**
- Are behavioral instructions ("do this, then that") formatted as table
  rows?
- Are multi-step procedures stuffed into a table instead of a numbered
  list?
- Are tables being used for data where they should be (dimensions, scores,
  field mappings)?

**Reference:** `evaluate-flow.md` uses tables for:
- The 7-dimension rubric (Score | Level | Criteria)
- The report scores summary (Dimension | Score | Confidence | Rating)
- Persona reference lookup (File | Who | Key trait)

Navigation rules 1-9 are numbered prose. Agent steps in `evaluate.md`
(1-6) and `score.md` (1-11) are numbered prose.

**Common violation:** A table where each row is actually a workflow step
with conditional logic, or a Skill Composition table that embeds
multi-sentence behavioral instructions in cells.

---

## 4. OUTPUT TEMPLATES

**Rule:** Show output formats as literal inline blocks (the exact
markdown/JSON the agent should produce). Don't describe them in prose.

**What to look for:**
- Is the expected output format shown as a fenced code block the agent can
  fill in?
- Are field names, section headers, and structure visible in the template?
- Could the agent produce the output by copying the template and filling
  in the brackets?

**Reference:** `evaluate-flow.md` contains:
- Think-aloud format as a literal code block (STEP [n] with fields)
- NAVIGATION COMPLETE summary as a literal code block
- Full report template (~120 lines of exact markdown structure)
- HTML comments inside templates for agent guidance:
  `<!-- Sort rows by score ascending -->`

**Common violation:** "The report should contain an executive summary
followed by findings organized by severity" -- prose description instead
of a fillable template.

---

## 5. ANTI-PATTERNS

**Rule:** Name wrong behaviors specifically ("Do not use editorial language
like 'unfortunately'"). Don't describe them abstractly ("avoid bias").

**What to look for:**
- Are prohibited behaviors named with literal examples of the wrong words
  or patterns?
- Would the agent know exactly what NOT to do after reading the
  anti-pattern?
- Are anti-patterns grouped together in a visible section?

**Reference:** `evaluate-flow.md` Phase 2 anti-patterns:

```
- Do not use editorial language ("unfortunately," "disappointingly,"
  "critically," "surprisingly").
- Do not prescribe design solutions within issue findings.
- Do not speculate about what another persona would experience.
- Keep each finding concise -- one sentence per bullet is the target.
  Long paragraphs are a signal you are editorializing.
```

Each one names the specific wrong thing with examples in quotes.

**Common violation:** "Maintain objectivity" or "avoid bias" or "be
professional" -- abstract guidance that doesn't tell the agent what
specific words or behaviors to stop doing.

---

## 6. NUMBERING

**Rule:** Number steps simply and consistently. No letter schemes (A, B, C),
no sub-numbering (C.1, C.2), no renaming between versions.

**What to look for:**
- Are workflow steps using simple 1, 2, 3, 4 numbering?
- Are there letter-based schemes or deep sub-numbering?
- Do step numbers stay consistent if the skill has been revised?
- Can you refer to "Step 5" unambiguously?

**Reference:** `evaluate.md` uses steps 1-6. `score.md` uses steps 1-11.
`evaluate-flow.md` navigation rules are numbered 1-9. All simple integers,
no letters, no nesting.

**Common violation:** Steps labeled A, B, C with sub-steps A.1, A.2, or
phases labeled "Phase 1 Step 2a" creating ambiguity when referenced.

---

## 7. LENGTH

**Rule:** If a SKILL.md is over 400 lines, it's probably trying to do too
much. Compare against Zack's reference lengths.

**What to look for:**
- Total line count of SKILL.md
- Could sections be extracted into `references/` files?
- Is content repeated or paraphrased rather than stated once?
- Is the skill explaining things the agent already knows?

**Reference lengths:**
- `evaluate.md`: 141 lines (Phase 1 entry point)
- `score.md`: 89 lines (Phase 2 entry point)
- `evaluate-flow.md`: 607 lines (full canonical protocol with rubrics)
- Anthropic guide recommends: SKILL.md body under 500 lines

A thin entry point should be under 150 lines. A canonical protocol can
be longer but should use progressive disclosure.

**Common violation:** A 600-line SKILL.md that explains what UX research
is, defines all rubric criteria, provides the full workflow, and includes
output templates -- all in one file that could be three files.

---

## 8. DATA vs INSTRUCTIONS

**Rule:** Data definitions (persona schemas, rubric criteria, reference
tables) should be in separate files from behavioral instructions.

**What to look for:**
- Are large data blocks (YAML schemas, JSON examples, CSV-like tables)
  embedded in the instructions file?
- Could data be extracted to a `references/` file or `data/` directory?
- Would updating the data require editing the instructions file?

**Reference:** Zack's project separates:
- Persona data: `personas/*.yaml` (10 separate files)
- Rubric source: `Usability Heuristic Rubrics - Rubrics for E2E flows.csv`
- Protocol + rubric criteria: `evaluate-flow.md` (co-located because the
  criteria ARE the instructions for scoring)
- Tools: `tools/*.py`

The key question: if you need to update data without changing behavior,
can you do it without touching the instructions file?

**Common violation:** A SKILL.md that embeds a 50-row reference table of
Jira field IDs, persona definitions, or API schemas inline with the
workflow steps.

---

## 9. CONFIDENCE

**Rule:** Confidence or certainty ratings must be tied to observable
evidence, not abstract qualities.

**What to look for:**
- Are confidence levels defined with concrete observable criteria?
- Could two reviewers independently arrive at the same confidence level
  for the same finding?
- Are the definitions specific enough to be actionable?

**Reference:** `evaluate-flow.md` confidence definitions:

```
- High: Structural blocker directly observed -- the persona hit a dead
  end, abandoned, or needed CLI escape. Evidence is unambiguous.
- Medium: Friction observed and consistent with the persona's profile,
  but a user with slightly more context might score differently.
- Low: Logical inference based on persona constraints. State the
  assumption explicitly (e.g., "Assumes the persona would not recognize
  this K8s term").
```

Each level is tied to what was directly observed, not to how complex the
issue is.

**Common violation:** "High confidence = high complexity issue" or
confidence based on the reviewer's gut feeling rather than observable
evidence from the trace.

---

## 10. OPTIONAL vs REQUIRED

**Rule:** Clearly distinguish what's optional from what's required. Use
bold markers (`**CRITICAL**`, `**STOP HERE**`, `**MANDATORY**`) sparingly.
If everything is marked critical, nothing is.

**What to look for:**
- How many bold emphasis markers are used? Count them.
- Are `CRITICAL`, `MANDATORY`, `STOP HERE` used for genuinely critical
  boundaries, or scattered throughout?
- Can you tell which steps are skippable vs required?
- Are optional features clearly marked as optional?

**Reference:** `evaluate-flow.md` marker inventory:
- `**CRITICAL**`: once (line 6, phase separation mandate)
- `**STOP HERE**`: once (line 199, hard phase boundary)
- `**MANDATORY**`: used only for HTML generation step
- Everything else is regular prose with normal formatting

Three distinct markers for three genuinely non-negotiable boundaries.

**Common violation:** Every other paragraph starts with `**IMPORTANT**` or
`**NOTE**` or `**CRITICAL**`, diluting all emphasis to the point where the
truly critical boundaries are invisible.
