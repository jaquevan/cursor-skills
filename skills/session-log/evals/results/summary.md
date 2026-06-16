# Eval Summary — session-log

**Date:** 2026-06-16
**Evals run:** 6
**Total assertions:** 36

**With-skill pass rate:** 35/36 (97%)
**Without-skill pass rate:** 31/36 (86%)
**Skill delta:** +4 assertions where skill made the difference

---

## Passed in both (skill not adding value)

These assertions pass regardless of whether the skill is used — the model handles them well on its own. These serve as regression checks.

| Eval | Assertion |
|---|---|
| importance-scoring | Session A must be scored 4 or 5 out of 5 |
| importance-scoring | Session B must be scored 1 out of 5 |
| importance-scoring | Session C must be scored 1 or 2 out of 5 |
| importance-scoring | Session A must appear first in the sorted output |
| importance-scoring | Session B must appear last in the sorted output |
| importance-scoring | Session A must have the [IMPORTANT] prefix |
| importance-scoring | Session B must NOT have the [IMPORTANT] prefix |
| importance-scoring | The output must include a #zack tag |
| importance-scoring | The output must include a #sprint-work tag |
| importance-scoring | Session B must NOT include Changed or Why fields |
| carry-forward | The output must contain a '## Carried Forward' section |
| carry-forward | The carried item must show [DAY 2] marker |
| carry-forward | The carried item must reference the original date |
| carry-forward | The carried item must show 'Last status: in progress' |
| carry-forward | The output must include a #carried-forward tag |
| carry-forward | The carried item must NOT be tagged #stale |
| auto-escalate-stale | The item must show [DAY 3] marker |
| auto-escalate-stale | The importance must be 5/5 |
| auto-escalate-stale | The output must include a #stale tag |
| auto-escalate-stale | The item must appear at the top |
| auto-escalate-stale | The Signal line must mention the stale carry-forward |
| people-detection | The tags must include #andy |
| people-detection | The tags must include #steven |
| people-detection | The tags must NOT include #zack |
| people-detection | The tags must include #team |
| signal-line | The output must start with '# Session Log —' |
| signal-line | The second line must be a '**Signal:**' line |
| signal-line | The Signal line must mention '2 important items' |
| signal-line | The Signal line must mention the stale carry-forward |
| auto-close | The item must be marked as auto-closed or resolved |
| auto-close | The resolution reason must mention '2 days' |
| auto-close | The item must NOT appear in Carried Forward section |
| auto-close | The output must NOT carry this item forward |

## Passed only with skill (skill adding value)

These assertions demonstrate where the skill's explicit rules produce better, more consistent output than general judgment alone.

| Eval | Assertion |
|---|---|
| importance-scoring | The output must include a #networking tag for Session B |
| people-detection | The tags must include #debugging for Session B |
| signal-line | A **Tags:** line must appear after the Signal line (with correct mandatory tags #daily-log #YYYY-MM-DD) |

**Pattern:** The skill adds value primarily in **tag consistency** — ensuring specific tag names are used exactly as defined (`#networking` vs. generic descriptions, `#debugging` vs. `#ci`, mandatory `#daily-log` + date format). Without the skill, the model uses reasonable but inconsistent tag names.

## Failed in both (gap or bad assertion)

| Eval | Assertion | Recommendation |
|---|---|---|
| (none) | — | — |

## Failed only with skill (skill regression)

| Eval | Assertion | Analysis |
|---|---|---|
| importance-scoring | The output must include a #networking tag | The with-skill run omitted `#networking` from the Tags line despite the session being clearly a networking session. The tag rules define it but the agent didn't apply it. **Fix skill** — add emphasis that `#networking` must appear whenever a session scores -1 for the networking signal. |

---

## Recommendations

1. **Skill is working well.** 97% pass rate with strong performance on all core mechanics (importance scoring, carry-forward, auto-escalate, auto-close, signal line, people detection).

2. **Tag application is the weak spot.** The one failure (missing `#networking`) shows that while the tag is defined in the rules, it wasn't reliably applied. Consider making the connection more explicit: "If a session triggers the -1 networking penalty in Step 3.5, always add `#networking` in Step 4."

3. **Baseline is surprisingly strong (86%).** The model intuits most of the behavior on its own. The skill's main value is **consistency and precision** — ensuring exact tag names, mandatory fields, and format adherence rather than inventing the concepts from scratch.

4. **Keep all assertions as regression checks.** Even the "passed in both" assertions protect against future model regressions where the base model might lose these intuitions.
