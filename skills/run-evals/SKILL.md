---
name: run-evals
description: >-
  Runs structured evaluations for any project skill. Reads evals.json, executes
  each prompt with and without the skill, grades outputs against assertions, and
  produces a comparison summary. Use when the user says "run evals", "evaluate
  my skill", "test my skill", "run the eval suite", "benchmark my skill", or
  mentions running assertions or grading skill outputs.
disable-model-invocation: true
---

# Run Evals

Executes a structured evaluation suite for a given skill, comparing with-skill
and without-skill outputs against defined assertions.

## Step 1: Identify the skill

Ask the user which skill to evaluate if they haven't already specified one. The
skill must live at `.cursor/skills/<skill-name>/` and have an `evals/evals.json`
file. Confirm the skill name before proceeding.

## Step 2: Read the eval definitions

Read `.cursor/skills/<skill-name>/evals/evals.json`. This file contains an array
of eval entries, each with an `id`, `prompt`, `expected_output`, and optionally
an `assertions` array. If an entry has no assertions, skip grading for that entry
and note it in the summary.

## Step 3: Run each eval prompt

For each eval entry, produce two outputs. Treat each run as independent — do not
let the output of one run influence another.

### With-skill run

1. Read the skill file at `.cursor/skills/<skill-name>/SKILL.md`
2. Follow the skill's instructions to execute the eval prompt
3. Save the output to `.cursor/skills/<skill-name>/evals/results/with-skill/eval-<id>.md`

### Without-skill run

1. Do NOT read the skill file or any other eval results
2. Execute the eval prompt using only general judgment
3. Save the output to `.cursor/skills/<skill-name>/evals/results/without-skill/eval-<id>.md`

The with-skill and without-skill runs must be executed in separate subagent tasks
so that context from one does not leak into the other. If subagents are not
available, run all with-skill evals first, then all without-skill evals, and
avoid referencing previous outputs.

## Step 4: Grade each output

For each eval entry that has assertions, grade both outputs (with-skill and
without-skill) against every assertion.

For each assertion, return:
- **PASS** or **FAIL**
- A one-sentence reason quoting or referencing the output as evidence

Save grading results for each eval to:
- `.cursor/skills/<skill-name>/evals/results/with-skill/eval-<id>-grade.md`
- `.cursor/skills/<skill-name>/evals/results/without-skill/eval-<id>-grade.md`

Use this format for each grade file:

```markdown
# Eval <id> Grading — <with-skill or without-skill>

**Result:** X/Y PASS

| Assertion | Result | Evidence |
|---|---|---|
| <assertion text> | **PASS** or **FAIL** | <one-sentence reason quoting output> |
```

### Grading principles

- Require concrete evidence for a PASS — do not give the benefit of the doubt.
- Check the substance, not just the label. A section heading that exists but
  contains no meaningful content is a FAIL.
- If an assertion references something that should NOT be present, confirm its
  absence by searching the full output.

## Step 5: Produce the comparison summary

After all evals are graded, create a summary at
`.cursor/skills/<skill-name>/evals/results/summary.md` with three sections:

### 1. Passed in both configurations

Assertions that passed in both with-skill and without-skill runs. These indicate
the model handles this well on its own — the skill is not adding value here.
Consider whether these assertions are useful as regression checks or should be
replaced with more discriminating ones.

### 2. Passed only with skill

Assertions that passed with the skill but failed without it. This is where the
skill is demonstrably adding value. Note the pattern — what capability does the
skill provide that the model lacks on its own?

### 3. Failed in both configurations

Assertions that failed regardless of whether the skill was used. These indicate
either a gap in the skill's instructions, an unrealistic assertion, or a task the
model cannot reliably accomplish. Recommend whether to fix the skill or revise
the assertion.

Use this format:

```markdown
# Eval Summary — <skill-name>

**Date:** YYYY-MM-DD
**Evals run:** <count>
**Total assertions:** <count>

---

## Passed in both (skill not adding value)

| Eval | Assertion |
|---|---|
| <id> | <assertion text> |

## Passed only with skill (skill adding value)

| Eval | Assertion |
|---|---|
| <id> | <assertion text> |

## Failed in both (gap or bad assertion)

| Eval | Assertion | Recommendation |
|---|---|---|
| <id> | <assertion text> | Fix skill / Revise assertion |
```

## After the summary

Present the summary to the user and highlight:
- The skill's overall pass rate (with-skill) vs baseline (without-skill)
- The number of assertions where the skill made the difference
- Any recommendations for improving the skill or the eval suite
